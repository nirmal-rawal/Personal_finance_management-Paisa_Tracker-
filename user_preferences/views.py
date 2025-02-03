from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages

def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    user_preference = UserPreference.objects.filter(user=request.user).first()  # Use `.first()` to avoid errors

    if request.method == 'POST':
        currency = request.POST.get("currency")
        if user_preference:
            user_preference.currency = currency
            user_preference.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)

        messages.success(request, 'Change saved')

    return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preference': user_preference})
