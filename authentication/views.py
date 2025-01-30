from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages

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
    
    def post(self, request):
        # GET USER DATA
        username = request.POST.get('username')  # Use .get() to avoid KeyError
        email = request.POST.get('email')        # Use .get() to avoid KeyError
        password = request.POST.get('password')  # Use .get() to avoid KeyError

        context={
            'fieldValues':request.POST

        }

        # Validate the data
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'authentication/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'authentication/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return render(request, 'authentication/register.html')

        if len(password) < 5:
            messages.error(request, 'Password is too short.')
            return render(request, 'authentication/register.html',context)

        # Create a new user
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()
        messages.success(request, 'Account successfully created.')
        return render(request, 'authentication/register.html')


        
        return render(request, 'authentication/register.html')

