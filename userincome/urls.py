from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="incomes"),
    path('add-income/', views.add_income, name='add-income'),
    path('edit-income/<int:id>/', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>/', views.delete_income, name="income-delete"),  # Correct URL pattern
    path('search-incomes/', views.search_incomes, name="search_incomes"),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
]