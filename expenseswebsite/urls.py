"""
URL configuration for expenseswebsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',include('expenses.urls')),
    path('incomes/', include('userincome.urls')),
    path('admin/', admin.site.urls),
    path('authentication/',include('authentication.urls')),
    path('preferences/',include('user_preferences.urls')),

    # path('authentication/login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    # path('authentication/register/', auth_views.LoginView.as_view(template_name='authentication/register.html'), name='register'),

]
