from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get("username", "")
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry! Username is already taken, please choose another one.'}, status=409)
        return JsonResponse({'username_valid': True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get("email", "")
        if not email:
            return JsonResponse({'email_error': 'Email is required.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'This email is already registered. Please use another one.'}, status=409)
        return JsonResponse({'email_valid': True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
