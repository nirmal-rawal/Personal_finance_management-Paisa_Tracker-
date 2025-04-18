# user_preference/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
import json
import requests
from django.conf import settings
from .models import UserPreference
from django.contrib import messages

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