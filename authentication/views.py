from django.shortcuts import render, redirect
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
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

# Thread class for sending emails in the background
class EmailThread(threading.Thread):
    def __init__(self, email_body):
        self.email_body = email_body
        threading.Thread.__init__(self)

    def run(self):
        self.email_body.send(fail_silently=False)

# View for validating username
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get("username", "")

        # Return early if the username is empty
        if not username:
            return JsonResponse({'username_valid': True})

        # Check if the username contains only alphanumeric characters
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters.'}, status=400)

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry! Username is already taken, please choose another one.'}, status=409)

        return JsonResponse({'username_valid': True})

# View for validating email
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get("email", "")

        # Return early if the email is empty
        if not email:
            return JsonResponse({'email_valid': True})

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'This email is already registered. Please use another one.'}, status=409)

        return JsonResponse({'email_valid': True})
    
# View for user registration
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

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={'uidb64': uidb64, 'token': account_activation_token.make_token(user)})
        activate_url = 'http://' + domain + link

        email_subject = "Activate your account"
        email_body = "Hi " + user.username + ", please use this link to verify your account\n" + activate_url

        email_message = EmailMessage(
            email_subject,
            email_body,
            os.environ.get("EMAIL_HOST_USER"),
            [email],
        )

        # Use threading to send the email in the background
        EmailThread(email_message).start()
        messages.success(request, 'Account successfully created. Check your email for activation.')

        return render(request, 'authentication/register.html', context)

# View for account verification
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message' + 'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, "Account activated successfully")
            return redirect('login')
        except Exception as ex:
            pass

        return redirect('login')

# View for user login
class LoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, "Welcome, " + user.username + " You are now logged in")
                    return redirect('expenses')

                messages.error(request, "Account is not active, please check your email")
                return render(request, "authentication/login.html")
            messages.error(request, "Invalid username or password, Try again")
            return render(request, "authentication/login.html")
        messages.error(request, "Please fill all fields")
        return render(request, "authentication/login.html")

# View for user logout
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out")
        return redirect('login')

# View for requesting password reset email
class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')

    def post(self, request):
        username_or_email = request.POST.get('username_or_email')
        context = {'values': request.POST}

        if not username_or_email:
            messages.error(request, 'Please supply a username or email')
            return render(request, 'authentication/reset_password.html', context)

        # Check if the input is an email or username
        if '@' in username_or_email:
            user = User.objects.filter(email=username_or_email)
        else:
            user = User.objects.filter(username=username_or_email)

        if user.exists():
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain
            link = reverse('reset-user-password', kwargs={'uidb64': uidb64, 'token': PasswordResetTokenGenerator().make_token(user[0])})
            reset_url = 'http://' + domain + link

            email_subject = "Password reset instructions"
            email_body = "Hi " + user[0].username + ", please use this link to reset your password\n" + reset_url

            email_message = EmailMessage(
                email_subject,
                email_body,
                os.environ.get("EMAIL_HOST_USER"),
                [user[0].email],
            )

            # Use threading to send the email in the background
            EmailThread(email_message).start()
            messages.success(request, 'We have sent you an email to reset your password')

            return render(request, 'authentication/reset_password.html', context)

        messages.error(request, 'No user found with this username or email')
        return render(request, 'authentication/reset_password.html', context)

# View for completing password reset
class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token}

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'Link is invalid, please request a new one')
                return render(request, 'authentication/reset_password.html', context)

        except Exception as e:
            pass

        return render(request, 'authentication/set_newpassword.html', context)

    def post(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token}

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set_newpassword.html', context)

        if len(password) < 5:
            messages.error(request, 'Password is too short')
            return render(request, 'authentication/set_newpassword.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successfully, you can now login with your new password')
            return redirect('login')

        except Exception as e:
            messages.error(request, 'Something went wrong, please try again')
            return render(request, 'authentication/set_newpassword.html', context)
        

def account_view(request):
    # Your view logic here
    return render(request, 'profile.html')  # or whatever your template name is