# user_preference/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.preferences_main, name='preferences'),
    path('currency/', views.currency_preference, name='currency_preference'),
    path('tools/', views.tools_main, name='tools'),
    path('tools/currency-exchange/', views.currency_exchange, name='currency_exchange'),
    path('tools/salary-calculator/', views.salary_calculator, name='salary_calculator'),
]