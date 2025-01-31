from django.shortcuts import render,redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
import os
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import account_activation_token

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
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        context = {'fieldValues': request.POST}

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'authentication/register.html', context)

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'authentication/register.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return render(request, 'authentication/register.html', context)

        if len(password) < 5:
            messages.error(request, 'Password is too short.')
            return render(request, 'authentication/register.html', context)

        # Create a new user
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()
        #path_to_view
        #- getting domain we are on 
        #- relative url to varification 
        # - encode UID
        #-token 
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        
        domain=get_current_site(request).domain
        link = reverse('activate',kwargs={'uidb64':uidb64,'token':account_activation_token.make_token(user)})
        activate_url='http://' +domain+link
        # Send Email Verification
        email_subject = "Activate your  account"
        email_body = "Hi!" +user.username+  "please use this link to verify your account\n" +activate_url

        try:
            email_message = EmailMessage(
                email_subject,
                email_body,
                os.environ.get("EMAIL_HOST_USER"),  # ✅ FIXED FROM_EMAIL
                [email],  
            )
            email_message.send(fail_silently=False)
            messages.success(request, 'Account successfully created. Check your email for activation.')
        except Exception as e:
            messages.error(request, f'Email sending failed: {e}')

        return render(request, 'authentication/register.html', context)
    
class VarificationView(View):
    def get(self,request,uidb64,token):
        try:
            id=force_bytes(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=id)

            if not account_activation_token.check_token(user,token):
                return redirect('login'+'?message'+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()

            messages.success(request,"Account activated successfully" )
            return redirect('login')
        except Exception as ex:
            pass
            
        return redirect('login')
    
class LoginView(View):
    def get(self,request):
        return render(request,"authentication/login.html")
