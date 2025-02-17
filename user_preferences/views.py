from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
import json
import requests
from django.conf import settings
from .models import UserPreference
from django.contrib import messages

@login_required  # Add this decorator to enforce authentication
def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    # Open the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for code, details in data.items():
            currency_data.append({
                'code': code,
                'name': details['name'],
                'symbol': details['symbol']
            })

    # Get the user's preferences (only for authenticated users)
    user_preference = UserPreference.objects.filter(user=request.user).first()

    if request.method == 'POST':
        currency = request.POST.get("currency")
        if user_preference:
            user_preference.currency = currency
            user_preference.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)

        messages.success(request, 'Change saved')

    # Fetch real-time exchange rates
    api_key = 'ab2319f80b0dff2da6530457'  
    base_currency = 'USD'  # Base currency for conversion
    url = f'https://v6.exchangerate-api.com/v6/ab2319f80b0dff2da6530457/latest/USD'
    response = requests.get(url)
    exchange_rates = response.json().get('conversion_rates', {}) if response.status_code == 200 else {}

    return render(request, 'preferences/index.html', {
        'currencies': currency_data,
        'user_preference': user_preference,
        'exchange_rates': exchange_rates,
    })