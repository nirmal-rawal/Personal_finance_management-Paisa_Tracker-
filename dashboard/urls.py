from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('update-budget/', views.update_budget, name="update_budget"),
    path('chat/', views.chat_bot, name='chat_bot'),
]