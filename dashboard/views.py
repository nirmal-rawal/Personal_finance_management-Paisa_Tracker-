from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from userincome.models import Income
from expenses.models import Expenses
from user_preferences.models import UserPreference
from datetime import date, timedelta
from collections import defaultdict

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

    # Fetch user's currency preference
    user_preference = UserPreference.objects.filter(user=request.user).first()
    currency = user_preference.currency if user_preference else "USD"

    # Fetch recent transactions (last 5)
    recent_incomes = incomes.order_by('-date')[:5]
    recent_expenses = expenses.order_by('-date')[:5]

    # Fetch top categories for expenses
    expense_categories = {}
    for expense in expenses:
        if expense.category in expense_categories:
            expense_categories[expense.category] += expense.amount
        else:
            expense_categories[expense.category] = expense.amount
    top_expense_categories = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:3]

    # Fetch top sources for income
    income_sources = {}
    for income in incomes:
        if income.source in income_sources:
            income_sources[income.source] += income.amount
        else:
            income_sources[income.source] = income.amount
    top_income_sources = sorted(income_sources.items(), key=lambda x: x[1], reverse=True)[:3]

    # Fetch monthly income and expense data for the chart
    monthly_income = defaultdict(float)
    monthly_expenses = defaultdict(float)

    for income in incomes:
        month = income.date.strftime("%Y-%m")  # Group by year and month
        monthly_income[month] += income.amount

    for expense in expenses:
        month = expense.date.strftime("%Y-%m")  # Group by year and month
        monthly_expenses[month] += expense.amount

    # Sort months in ascending order
    sorted_months = sorted(monthly_income.keys())

    # Prepare data for the chart
    chart_labels = sorted_months
    chart_income_data = [monthly_income[month] for month in sorted_months]
    chart_expense_data = [monthly_expenses[month] for month in sorted_months]

    # Expense breakdown by category
    expense_breakdown = {category: (amount / total_expenses) * 100 for category, amount in expense_categories.items()}
    expense_breakdown_labels = list(expense_breakdown.keys())
    expense_breakdown_values = list(expense_breakdown.values())

    # Monthly spending limit and alerts
    monthly_spending_limit = 5000  # Example limit (can be dynamic)
    spending_progress = (total_expenses / monthly_spending_limit) * 100

    # Best and worst spending days
    daily_spending = defaultdict(float)
    for expense in expenses:
        day = expense.date.strftime("%A")  # Group by day of the week
        daily_spending[day] += expense.amount
    best_spending_day = min(daily_spending.items(), key=lambda x: x[1])
    worst_spending_day = max(daily_spending.items(), key=lambda x: x[1])

    # Cash flow summary (net savings trend)
    net_savings_trend = [monthly_income[month] - monthly_expenses[month] for month in sorted_months]

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'currency': currency,
        'recent_incomes': recent_incomes,
        'recent_expenses': recent_expenses,
        'top_expense_categories': top_expense_categories,
        'top_income_sources': top_income_sources,
        'chart_labels': chart_labels,
        'chart_income_data': chart_income_data,
        'chart_expense_data': chart_expense_data,
        'expense_breakdown_labels': expense_breakdown_labels,
        'expense_breakdown_values': expense_breakdown_values,
        'monthly_spending_limit': monthly_spending_limit,
        'spending_progress': spending_progress,
        'best_spending_day': best_spending_day,
        'worst_spending_day': worst_spending_day,
        'net_savings_trend': net_savings_trend,
    }
    return render(request, 'dashboard/index.html', context)