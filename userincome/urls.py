from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="incomes"),
    path('add-income/', views.add_income, name='add-income'),
    path('edit-income/<int:id>/', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>/', views.delete_income, name="income-delete"),
    path('search-incomes/', views.search_incomes, name="search_incomes"),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('income-summary/', views.income_summary, name='income-summary'),
    path('income-category-summary/', views.income_category_summary, name="income-category-summary"),
    path('scan-income-receipt/', views.scan_income_receipt_api, name='scan-income-receipt'),
]