from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import RegistrationView, UsernameValidationView, EmailValidationView, VerificationView, LoginView, LogoutView, RequestPasswordResetEmail, CompletePasswordReset,account_view

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('validate-username/', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email/', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
    path('request-reset-link/', RequestPasswordResetEmail.as_view(), name='request-password'),
    path('reset-password/<uidb64>/<token>', CompletePasswordReset.as_view(), name='reset-user-password'),
    path('account/', account_view, name='account'),
    
]