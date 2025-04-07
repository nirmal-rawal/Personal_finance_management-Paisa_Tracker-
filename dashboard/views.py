from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userincome.models import Income
from expenses.models import Expenses, Budget
from user_preferences.models import UserPreference
from datetime import date, timedelta, datetime
from collections import defaultdict
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from expenses.forms import BudgetForm
from django.db import models
from itertools import chain

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

    # Top categories for expenses
    expense_categories = {}
    for expense in expenses:
        if expense.category in expense_categories:
            expense_categories[expense.category] += expense.amount
        else:
            expense_categories[expense.category] = expense.amount
    top_expense_categories = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:3]

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

    # Expense breakdown by category
    expense_breakdown = {category: (amount / total_expenses) * 100 if total_expenses > 0 else 0 
                        for category, amount in expense_categories.items()}
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