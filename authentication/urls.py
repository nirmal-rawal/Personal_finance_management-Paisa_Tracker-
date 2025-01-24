# from .views import RegistrationView,UsernameValidationView,EmailValidationView
# from django.urls import path
# from django.views.decorators.csrf import csrf_exempt

from django.urls import path
from .views import RegistrationView, UsernameValidationView, EmailValidationView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('validate-username/', UsernameValidationView.as_view(), name="validate-username"),
    path('validate-email/', EmailValidationView.as_view(), name='validate-email'),
]
