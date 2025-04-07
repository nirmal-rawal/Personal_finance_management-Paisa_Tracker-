# expenses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="expenses"),
    path('add-expense/', views.add_expense, name='add-expense'),
    path('edit-expense/<int:id>/', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>/', views.delete_expense, name="expense-delete"),
    path('search-expenses/', views.search_expenses, name="search_expenses"),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('expense_category_summary/', views.expense_category_summary, name="expense_category_summary"),
    path('stats/', views.stats_view, name="stats"),
    path('scan-receipt/', views.scan_receipt_api, name='scan-receipt'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:id>/', views.mark_notification_as_read, name='mark_notification_read'),
    path('notifications/unread/', views.get_unread_notifications, name='unread_notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]