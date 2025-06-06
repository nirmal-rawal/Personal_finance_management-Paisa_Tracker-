# user_preference/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="preferences"),
    path('currency_preference/', views.currency_preference, name="currency_preference"),
    path('tools/', views.tools_main, name="tools"),
    path('tools/currency-exchange/', views.currency_exchange, name='currency_exchange'),
    path('tools/salary-calculator/', views.salary_calculator, name='salary_calculator'),
    path('generate_report/', views.generate_report, name="generate_report"),
]