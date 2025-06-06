from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userincome.models import Income
from expenses.models import Expenses, Budget, Notification
from user_preferences.models import UserPreference
from datetime import date, timedelta, datetime
from collections import defaultdict
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from expenses.forms import BudgetForm
from django.db import models
from itertools import chain
from django.http import JsonResponse
from .models import ChatMessage
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

@login_required(login_url='/authentication/login/')
def dashboard(request):
    # Fetch income data
    incomes = Income.objects.filter(owner=request.user)
    total_income = sum(income.amount for income in incomes)

    # Fetch expense data
    expenses = Expenses.objects.filter(owner=request.user)
    total_expenses = sum(expense.amount for expense in expenses)

    # Calculate net income
    net_income = total_income - total_expenses

    # Calculate savings rate
    savings_rate = (net_income / total_income * 100) if total_income > 0 else 0

    # Fetch user's currency preference
    user_preference = UserPreference.objects.filter(user=request.user).first()
    currency = user_preference.currency if user_preference else "USD"

    # Handle budget - get or create single budget per user
    budget, created = Budget.objects.get_or_create(user=request.user, defaults={'amount': 0})

    # Calculate current month expenses
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    current_month_expenses = Expenses.objects.filter(
        owner=request.user,
        date__gte=first_day_of_month,
        date__lte=today,
        transaction_type='Expense'
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    # Calculate budget usage percentage
    budget_percentage = 0
    if budget.amount > 0:
        budget_percentage = (current_month_expenses / budget.amount) * 100
        # Send email alert if expenses exceed 80% of budget
        if budget_percentage >= 80 and settings.EMAIL_HOST_USER:
            send_budget_alert_email(request.user, budget.amount, current_month_expenses, currency)

    # Budget form
    budget_form = BudgetForm(instance=budget)

    # Recent transactions (last 5)
    recent_incomes = incomes.order_by('-date')[:5]
    recent_expenses = expenses.order_by('-date')[:5]

    # Prepare recent transactions with proper type and category/source
    recent_transactions = []
    for income in recent_incomes:
        recent_transactions.append({
            'date': income.date,
            'description': income.description,
            'category': income.source,
            'transaction_type': 'Income',
            'amount': income.amount
        })
    
    for expense in recent_expenses:
        recent_transactions.append({
            'date': expense.date,
            'description': expense.description,
            'category': expense.category,
            'transaction_type': 'Expense',
            'amount': expense.amount
        })

    # Sort all transactions by date (newest first)
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:5]

    # Top categories for expenses (now top 5 instead of top 3)
    expense_categories = {}
    for expense in expenses:
        if expense.category in expense_categories:
            expense_categories[expense.category] += expense.amount
        else:
            expense_categories[expense.category] = expense.amount
    top_expense_categories = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:5]

    # Top sources for income
    income_sources = {}
    for income in incomes:
        if income.source in income_sources:
            income_sources[income.source] += income.amount
        else:
            income_sources[income.source] = income.amount
    top_income_sources = sorted(income_sources.items(), key=lambda x: x[1], reverse=True)[:3]

    # Monthly income and expense data for the chart
    monthly_income = defaultdict(float)
    monthly_expenses = defaultdict(float)

    for income in incomes:
        month = income.date.strftime("%Y-%m")
        monthly_income[month] += income.amount

    for expense in expenses:
        month = expense.date.strftime("%Y-%m")
        monthly_expenses[month] += expense.amount

    # Sort months in ascending order
    sorted_months = sorted(monthly_income.keys())

    # Prepare data for the chart
    chart_labels = sorted_months
    chart_income_data = [monthly_income[month] for month in sorted_months]
    chart_expense_data = [monthly_expenses[month] for month in sorted_months]

    # Expense breakdown by category (top 5 + others grouped as "Other")
    top_categories = dict(sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:5])
    other_amount = sum(amount for category, amount in expense_categories.items() if category not in top_categories)
    
    expense_breakdown = {category: (amount / total_expenses) * 100 if total_expenses > 0 else 0 
                        for category, amount in top_categories.items()}
    
    if other_amount > 0:
        expense_breakdown['Other'] = (other_amount / total_expenses) * 100 if total_expenses > 0 else 0
    
    expense_breakdown_labels = list(expense_breakdown.keys())
    expense_breakdown_values = list(expense_breakdown.values())

    # Best and worst spending days
    daily_spending = defaultdict(float)
    for expense in expenses:
        day = expense.date.strftime("%A")
        daily_spending[day] += expense.amount
    best_spending_day = min(daily_spending.items(), key=lambda x: x[1]) if daily_spending else (None, 0)
    worst_spending_day = max(daily_spending.items(), key=lambda x: x[1]) if daily_spending else (None, 0)

    # Cash flow summary (net savings trend)
    net_savings_trend = [monthly_income[month] - monthly_expenses[month] for month in sorted_months]

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'currency': currency,
        'budget': budget,
        'current_month_expenses': current_month_expenses,
        'budget_percentage': budget_percentage,
        'budget_form': budget_form,
        'recent_transactions': recent_transactions,
        'top_expense_categories': top_expense_categories,
        'top_income_sources': top_income_sources,
        'chart_labels': chart_labels,
        'chart_income_data': chart_income_data,
        'chart_expense_data': chart_expense_data,
        'expense_breakdown_labels': expense_breakdown_labels,
        'expense_breakdown_values': expense_breakdown_values,
        'best_spending_day': best_spending_day,
        'worst_spending_day': worst_spending_day,
        'net_savings_trend': net_savings_trend,
        'savings_rate': savings_rate,
    }
    return render(request, 'dashboard/index.html', context)

def send_budget_alert_email(user, budget_amount, spent_amount, currency):
    remaining = budget_amount - spent_amount
    percentage_used = (spent_amount / budget_amount) * 100
    subject = f"Budget Alert: You've used {percentage_used:.0f}% of your monthly budget"
    message = (
        f"Hi {user.username},\n\n"
        f"You have used {percentage_used:.0f}% of your monthly budget.\n\n"
        f"Budget amount: {currency}{budget_amount:.2f}\n"
        f"Spent so far: {currency}{spent_amount:.2f}\n"
        f"Remaining: {currency}{max(remaining, 0):.2f}\n\n"
        "Please review your expenses to stay within your budget."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )
    
    # Create session notification
    Notification.objects.create(
        user=user,
        message=f"Budget Alert: You've used {percentage_used:.0f}% of your monthly budget",
        notification_type='budget_alert',
        related_url='/stats/'
    )

@login_required
def update_budget(request):
    if request.method == 'POST':
        budget, created = Budget.objects.get_or_create(user=request.user)
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
        else:
            messages.error(request, 'Error updating budget. Please enter a valid amount.')
    return redirect('dashboard')

@csrf_exempt
@login_required
def chat_bot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Handle clear chat request
        if data.get('clear_chat'):
            ChatMessage.objects.filter(user=request.user).delete()
            return JsonResponse({'status': 'success', 'message': 'Chat history cleared'})
        
        # Handle normal chat message
        user_message = data.get('message', '').lower()
        
        # Get user's financial data
        expenses = Expenses.objects.filter(owner=request.user)
        incomes = Income.objects.filter(owner=request.user)
        
        # Generate response based on user's message
        response = generate_chat_response(user_message, request.user, expenses, incomes)
        
        # Save the chat interaction
        ChatMessage.objects.create(
            user=request.user,
            message=user_message,
            response=response
        )
        
        return JsonResponse({'response': response})
    
    # Get chat history
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return JsonResponse({'history': list(chat_history.values())})

def generate_chat_response(message, user, expenses, incomes):
    message = message.lower().strip()
    
    # Help command
    if 'help' in message:
        return (
            '1. Financial Information\n'
            '- "Show my total expenses"\n'
            '- "What are my monthly expenses?"\n'
            '- "Show my total income"\n'
            '- "What are my savings?"\n\n'
            '2. Financial Analysis\n'
            '- "How can I improve my finances?"\n'
            '- "Analyze my spending"\n'
            '- "Show my biggest expenses"\n\n'
            '3. Budget Information\n'
            '- "Show my budget"\n'
            '- "Am I over budget?"'
        )
    
    # Basic expense analysis
    if any(phrase in message for phrase in ['total expenses', 'all expenses', 'how much did i spend']):
        total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        return f"Your total expenses are ${total:.2f}"
    
    elif any(phrase in message for phrase in ['monthly expenses', 'this month', 'spending this month']):
        current_month = datetime.now().month
        monthly_expenses = expenses.filter(date__month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
        return f"Your expenses this month are ${monthly_expenses:.2f}"
    
    elif any(phrase in message for phrase in ['income', 'how much do i earn', 'my earnings']):
        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        return f"Your total income is ${total_income:.2f}"
    
    elif any(phrase in message for phrase in ['savings', 'how much did i save', 'money saved']):
        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        savings = total_income - total_expenses
        return f"Your total savings are ${savings:.2f}"
    
    # Budget-related queries
    elif any(phrase in message for phrase in ['show my budget', 'what is my budget', 'budget amount']):
        budget = Budget.objects.filter(user=user).first()
        if budget:
            return f"Your monthly budget is ${budget.amount:.2f}"
        else:
            return "You haven't set up a budget yet. You can set one from your dashboard."
    
    elif any(phrase in message for phrase in ['am i over budget', 'budget status', 'budget progress']):
        budget = Budget.objects.filter(user=user).first()
        if not budget:
            return "You haven't set up a budget yet. You can set one from your dashboard."
        
        current_month = datetime.now().month
        monthly_expenses = expenses.filter(date__month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
        budget_percentage = (monthly_expenses / budget.amount * 100) if budget.amount > 0 else 0
        
        if budget_percentage > 100:
            return f"You are over budget! You've spent ${monthly_expenses:.2f}, which is {budget_percentage:.1f}% of your ${budget.amount:.2f} budget."
        elif budget_percentage > 80:
            return f"You're close to your budget limit. You've spent ${monthly_expenses:.2f}, which is {budget_percentage:.1f}% of your ${budget.amount:.2f} budget."
        else:
            return f"You're within your budget. You've spent ${monthly_expenses:.2f}, which is {budget_percentage:.1f}% of your ${budget.amount:.2f} budget."
    
    # Financial improvement advice
    elif any(phrase in message for phrase in ['improve', 'better finances', 'financial advice', 'how to save']):
        # Get some basic financial metrics
        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        savings = total_income - total_expenses
        
        # Get top expense categories
        expense_categories = {}
        for expense in expenses:
            if expense.category in expense_categories:
                expense_categories[expense.category] += expense.amount
            else:
                expense_categories[expense.category] = expense.amount
        
        top_expenses = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:3]
        
        advice = [
            "Here are some personalized financial tips:",
            f"1. Your top 3 expense categories are: {', '.join([f'{cat} (${amt:.2f})' for cat, amt in top_expenses])}",
            "2. Consider setting a budget for these categories to control spending.",
            f"3. Your current savings rate is {(savings/total_income * 100):.1f}% of your income.",
            "4. Aim to save at least 20% of your income if possible.",
            "5. Track your expenses regularly and look for areas to cut back.",
            "\nWould you like more specific advice about any of these areas?"
        ]
        return "\n".join(advice)
    
    # Analyze spending patterns
    elif any(phrase in message for phrase in ['analyze', 'spending pattern', 'where do i spend']):
        expense_categories = {}
        for expense in expenses:
            if expense.category in expense_categories:
                expense_categories[expense.category] += expense.amount
            else:
                expense_categories[expense.category] = expense.amount
        
        analysis = ["Here's an analysis of your spending:"]
        for category, amount in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (amount / sum(expense_categories.values())) * 100
            analysis.append(f"- {category}: ${amount:.2f} ({percentage:.1f}% of total spending)")
        
        return "\n".join(analysis)
    
    else:
        return "I'm not sure about that. Type 'help' to see what I can help you with!"