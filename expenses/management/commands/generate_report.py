from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Expenses, Notification
from user_preferences.models import UserPreference
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum
import json
from datetime import datetime
import os
from google.generativeai import configure
from google.generativeai.generative_models import GenerativeModel
from smtplib import SMTPAuthenticationError

class Command(BaseCommand):
    help = 'Generate financial reports for a specific month and year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='Year for the report')
        parser.add_argument('month', type=int, help='Month for the report')
        parser.add_argument('--email', action='store_true', help='Send email notifications')
        parser.add_argument('--username', type=str, help='Generate for specific user only')

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        send_email = options['email']
        username = options['username']

        users = User.objects.all()
        if username:
            users = users.filter(username=username)

        for user in users:
            try:
                # Get user's currency preference
                user_preference = UserPreference.objects.filter(user=user).first()
                currency = user_preference.currency if user_preference else "USD"
                
                # Get expenses and incomes for the specified month
                expenses = Expenses.objects.filter(
                    owner=user,
                    date__year=year,
                    date__month=month,
                    transaction_type='Expense'
                )
                
                incomes = Expenses.objects.filter(
                    owner=user,
                    date__year=year,
                    date__month=month,
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
                
                # Generate AI insights
                insights = self.generate_financial_insights(stats, f"{month:02d}/{year}")
                
                # Print report to console
                self.stdout.write(f"\nFinancial Report for {user.username} - {month:02d}/{year}")
                self.stdout.write("=" * 50)
                self.stdout.write(f"Income: {currency}{total_income:.2f}")
                self.stdout.write(f"Expenses: {currency}{total_expenses:.2f}")
                self.stdout.write(f"Net Income: {currency}{net_income:.2f}\n")
                
                self.stdout.write("Expense Categories:")
                for category, amount in by_category.items():
                    self.stdout.write(f"- {category}: {currency}{amount:.2f}")
                
                self.stdout.write("\nAI Insights:")
                for insight in insights:
                    self.stdout.write(f"- {insight}")
                
                # Send email if requested
                if send_email:
                    month_name = datetime(year, month, 1).strftime("%B %Y")
                    subject = f"Your Financial Report - {month_name}"
                    
                    html_message = render_to_string('expenses/email/monthly_report.html', {
                        'user': user,
                        'stats': stats,
                        'month': month_name,
                        'insights': insights,
                        'net_income': net_income,
                        'site_url': settings.SITE_URL
                    })
                    
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
                            message=f"Your financial report for {month_name} is ready",
                            notification_type='monthly_report',
                            related_url='/stats/'
                        )
                        
                        self.stdout.write(self.style.SUCCESS(f"\nEmail sent to {user.email}"))
                    except SMTPAuthenticationError as e:
                        self.stdout.write(self.style.ERROR(f"Email authentication failed: {str(e)}"))
                        self.stdout.write(self.style.WARNING("Please check your email credentials in .env"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error sending email: {str(e)}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error generating report for {user.username}: {str(e)}"))

    def generate_financial_insights(self, stats, month):
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Gemini API key not configured")
                
            configure(api_key=api_key)
            model = GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Analyze this financial data and provide 3 concise, actionable insights.
            Focus on spending patterns and practical advice.
            Keep it friendly and conversational.

            Financial Data for {month}:
            - Total Income: {stats['currency']}{stats['totalIncome']:.2f}
            - Total Expenses: {stats['currency']}{stats['totalExpenses']:.2f}
            - Net Income: {stats['currency']}{(stats['totalIncome'] - stats['totalExpenses']):.2f}
            - Expense Categories: {', '.join([f"{category}: {stats['currency']}{amount:.2f}" for category, amount in stats['byCategory'].items()])}

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