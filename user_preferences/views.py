from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
import json
import requests
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from expenses.models import Expenses
from userincome.models import Income
from datetime import datetime
import calendar
from django.utils import timezone

@login_required
def tools_main(request):
    return render(request, 'preferences/tools_main.html')

@login_required
def salary_calculator(request):
    if request.method == 'POST':
        basic_salary = float(request.POST.get('basic_salary', 0))
        allowances = float(request.POST.get('allowances', 0))
        bonus = float(request.POST.get('bonus', 0))
        
        # Nepal tax calculation rules (2023)
        gross_salary = basic_salary + allowances + bonus
        
        # Social Security Fund (SSF) calculation (if applicable)
        ssf_percentage = 0.11  # 11% of basic salary
        ssf_contribution = min(basic_salary * ssf_percentage, 3500)  # Max 3500 NPR
        
        # Taxable income
        taxable_income = gross_salary - ssf_contribution
        
        # Nepal tax slabs (2023)
        if taxable_income <= 500000:
            tax = taxable_income * 0.01
        elif taxable_income <= 700000:
            tax = 5000 + (taxable_income - 500000) * 0.10
        elif taxable_income <= 1000000:
            tax = 25000 + (taxable_income - 700000) * 0.20
        elif taxable_income <= 2000000:
            tax = 85000 + (taxable_income - 1000000) * 0.30
        else:
            tax = 385000 + (taxable_income - 2000000) * 0.36
        
        # Provident Fund (PF) - assuming 10% of basic salary
        pf_percentage = 0.10
        pf_contribution = basic_salary * pf_percentage
        
        # Net salary calculation
        total_deductions = tax + ssf_contribution + pf_contribution
        net_salary = gross_salary - total_deductions
        
        context = {
            'basic_salary': basic_salary,
            'allowances': allowances,
            'bonus': bonus,
            'gross_salary': gross_salary,
            'taxable_income': taxable_income,
            'tax': tax,
            'ssf_contribution': ssf_contribution,
            'pf_contribution': pf_contribution,
            'total_deductions': total_deductions,
            'net_salary': net_salary,
            'calculated': True,
        }
        return render(request, 'preferences/salary_calculator.html', context)
    
    return render(request, 'preferences/salary_calculator.html')

@login_required
def preferences_main(request):
    return render(request, 'preferences/main.html')

@login_required
def currency_preference(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for code, details in data.items():
            currency_data.append({
                'code': code,
                'name': details['name'],
                'symbol': details['symbol']
            })

    user_preference = UserPreference.objects.filter(user=request.user).first()

    if request.method == 'POST':
        currency = request.POST.get("currency")
        if user_preference:
            user_preference.currency = currency
            user_preference.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Currency preference saved')
        return redirect('currency_preference')

    return render(request, 'preferences/currency_preference.html', {
        'currencies': currency_data,
        'user_preference': user_preference,
    })

@login_required
def currency_exchange(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for code, details in data.items():
            currency_data.append({
                'code': code,
                'name': details['name'],
                'symbol': details['symbol']
            })

    # Fetch real-time exchange rates
    api_key = 'ab2319f80b0dff2da6530457'  
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
    response = requests.get(url)
    exchange_rates = response.json().get('conversion_rates', {}) if response.status_code == 200 else {}

    return render(request, 'preferences/currency_exchange.html', {
        'currencies': currency_data,
        'exchange_rates': exchange_rates,
    })
@login_required
def generate_report(request):
    if request.method == 'POST':
        # Get the date from the form (format: YYYY-MM)
        report_date = request.POST.get('reportDate')
        try:
            year, month = map(int, report_date.split('-'))
            if month < 1 or month > 12:
                raise ValueError
        except (ValueError, AttributeError):
            messages.error(request, "Invalid date format. Please select a valid month and year.")
            return redirect('generate_report')
        
        send_email = 'send_email' in request.POST
        
        # Rest of your report generation code...
        month_name = calendar.month_name[month]
        
        # Get expenses and incomes for the selected month
        expenses = Expenses.objects.filter(
            owner=request.user,
            date__year=year,
            date__month=month
        )
        
        incomes = Income.objects.filter(
            owner=request.user,
            date__year=year,
            date__month=month
        )
        
        # Calculate stats
        total_expenses = sum(expense.amount for expense in expenses)
        total_income = sum(income.amount for income in incomes)
        net_income = total_income - total_expenses
        
        # Group expenses by category
        by_category = {}
        for expense in expenses:
            if expense.category in by_category:
                by_category[expense.category] += expense.amount
            else:
                by_category[expense.category] = expense.amount
        
        # Get user's currency preference
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
        
        # Generate some AI insights
        insights = []
        if net_income < 0:
            insights.append(f"In {month_name} {year}, your expenses exceeded your income by {currency}{abs(net_income):.2f}. Consider reviewing discretionary spending.")
        else:
            insights.append(f"Great job in {month_name} {year}! You saved {currency}{net_income:.2f}.")
            
        if len(by_category) > 0:
            largest_category = max(by_category.items(), key=lambda x: x[1])
            insights.append(f"Your largest expense category was {largest_category[0]} at {currency}{largest_category[1]:.2f}.")
        
        # Prepare context for template
        stats = {
            'totalExpenses': total_expenses,
            'totalIncome': total_income,
            'byCategory': by_category,
            'currency': currency
        }
        
        context = {
            'user': request.user,
            'month': month_name,
            'year': year,
            'stats': stats,
            'net_income': net_income,
            'insights': insights,
            'site_url': settings.SITE_URL
        }
        
        # Render the report
        report_html = render_to_string('expenses/email/monthly_report.html', context)
        
        if send_email:
            # Send email
            send_mail(
                subject=f"Your {month_name} {year} Financial Report",
                message="Please view your financial report in HTML format.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=report_html
            )
            messages.success(request, f"Report for {month_name} {year} has been generated and sent to your email!")
        else:
            # Just show the report in browser
            return render(request, 'expenses/email/monthly_report.html', context)
        
        return redirect('tools')
    
    # For GET request, just render the form
    return render(request, 'preferences/generate_report.html')