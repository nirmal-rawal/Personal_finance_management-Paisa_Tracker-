from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Expenses, Budget, Notification
from user_preferences.models import UserPreference
from django.contrib.auth.models import User
import json
from google.generativeai import configure
from google.generativeai.generative_models import GenerativeModel
import os
from django.db.models import Sum
from smtplib import SMTPAuthenticationError

@shared_task
def generate_monthly_reports():
    today = timezone.now().date()
    first_day_current_month = today.replace(day=1)
    last_month = first_day_current_month - timedelta(days=1)
    
    users = User.objects.all()
    
    for user in users:
        try:
            # Get user's currency preference
            user_preference = UserPreference.objects.filter(user=user).first()
            currency = user_preference.currency if user_preference else "USD"
            
            # Get expenses and incomes for the month
            expenses = Expenses.objects.filter(
                owner=user,
                date__year=last_month.year,
                date__month=last_month.month,
                transaction_type='Expense'
            )
            
            incomes = Expenses.objects.filter(
                owner=user,
                date__year=last_month.year,
                date__month=last_month.month,
                transaction_type='Income'
            )
            
            # Calculate totals
            total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
            total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
            net_income = total_income - total_expenses
            
            # Categorize expenses
            by_category = {}
            for expense in expenses:
                if expense.category in by_category:
                    by_category[expense.category] += expense.amount
                else:
                    by_category[expense.category] = expense.amount
            
            # Prepare stats for AI analysis
            stats = {
                'totalIncome': total_income,
                'totalExpenses': total_expenses,
                'byCategory': by_category,
                'currency': currency
            }
            
            # Generate AI insights with your exact prompt format
            insights = generate_financial_insights(stats, last_month.strftime("%B %Y"))
            
            # Prepare email content
            month_name = last_month.strftime("%B %Y")
            subject = f"Your Monthly Financial Report - {month_name}"
            
            html_message = render_to_string('expenses/email/monthly_report.html', {
                'user': user,
                'stats': stats,
                'month': month_name,
                'insights': insights,
                'net_income': net_income,
                'site_url': settings.SITE_URL
            })
            
            # Send email
            try:
                send_mail(
                    subject=subject,
                    message='',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )
                
                # Create notification
                Notification.objects.create(
                    user=user,
                    message=f"Your monthly financial report for {month_name} is ready",
                    notification_type='monthly_report',
                    related_url='/stats/'
                )
                
                print(f"Report generated and sent to {user.email}")
            except SMTPAuthenticationError as e:
                print(f"Email authentication failed for {user.email}: {str(e)}")
            except Exception as e:
                print(f"Error sending email to {user.email}: {str(e)}")
            
        except Exception as e:
            print(f"Error generating report for {user.username}: {str(e)}")

def generate_financial_insights(stats, month):
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key not configured")
            
        configure(api_key=api_key)
        model = GenerativeModel('gemini-1.5-flash')
        
        # Your exact prompt format
        prompt = f"""
        Analyze this financial data and provide 3 concise, actionable insights.
        Focus on spending patterns and practical advice.
        Keep it friendly and conversational.

        Financial Data for {month}:
        - Total Income: {stats['currency']}{stats['totalIncome']}
        - Total Expenses: {stats['currency']}{stats['totalExpenses']}
        - Net Income: {stats['currency']}{stats['totalIncome'] - stats['totalExpenses']}
        - Expense Categories: {', '.join([f"{category}: {stats['currency']}{amount}" for category, amount in stats['byCategory'].items()])}

        Spending Pattern Recognition: Identify recurring expenses and highlight any unnecessary spending.

        Trend Forecasting: Predict future expenses and income trends based on historical data.

        Personalized Financial Insights: Provide tailored advice and budgeting strategies, considering the user's unique spending behavior.

        Actionable Insights: Offer specific, practical advice that the user can act on to improve their financial health.

        Format the response as a JSON array of strings, like this:
        ["insight 1", "insight 2", "insight 3"]
        """
        
        response = model.generate_content(prompt)
        text = response.text
        cleaned_text = text.replace('```json', '').replace('```', '').strip()
        
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        return [
            "Your highest expense category this month might need attention.",
            "Consider setting up a budget for better financial management.",
            "Track your recurring expenses to identify potential savings.",
        ]

@shared_task
def check_budget_alerts():
    budgets = Budget.objects.select_related('user').all()
    
    for budget in budgets:
        try:
            today = timezone.now().date()
            first_day_month = today.replace(day=1)
            
            total_expenses = Expenses.objects.filter(
                owner=budget.user,
                date__gte=first_day_month,
                transaction_type='Expense'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            percentage_used = (total_expenses / budget.amount) * 100 if budget.amount > 0 else 0
            remaining_budget = budget.amount - total_expenses
            
            if percentage_used >= 80 and (
                not budget.last_alert_sent or 
                budget.last_alert_sent.month != today.month or
                budget.last_alert_sent.year != today.year
            ):
                user_preference = UserPreference.objects.filter(user=budget.user).first()
                currency = user_preference.currency if user_preference else "USD"
                
                subject = f"Budget Alert: You've used {percentage_used:.0f}% of your budget"
                
                html_message = render_to_string('expenses/email/budget_alert.html', {
                    'user': budget.user,
                    'percentage_used': percentage_used,
                    'budget_amount': budget.amount,
                    'total_expenses': total_expenses,
                    'remaining_budget': remaining_budget,
                    'threshold': 80,
                    'currency': currency,
                    'site_url': settings.SITE_URL
                })
                
                send_mail(
                    subject=subject,
                    message='',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[budget.user.email],
                    fail_silently=False
                )
                
                Notification.objects.create(
                    user=budget.user,
                    message=f"Budget Alert: You've used {percentage_used:.0f}% of your monthly budget",
                    notification_type='budget_alert',
                    related_url='/stats/'
                )
                
                budget.last_alert_sent = timezone.now()
                budget.save()
                
        except Exception as e:
            print(f"Error checking budget for {budget.user.username}: {str(e)}")