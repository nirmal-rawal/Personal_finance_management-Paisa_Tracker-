from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('update-budget/', views.update_budget, name="update_budget"),
]