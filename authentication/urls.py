# from .views import RegistrationView,UsernameValidationView,EmailValidationView
# from django.urls import path
# from django.views.decorators.csrf import csrf_exempt

from django.urls import path
from .views import RegistrationView, UsernameValidationView, EmailValidationView,VarificationView,LoginView,LogoutView


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('validate-username/', UsernameValidationView.as_view(), name="validate-username"),
    path('validate-email/', EmailValidationView.as_view(), name='validate-email'),
    path('activate/<uidb64>/<token>',VarificationView.as_view(),name="activate"),

]
