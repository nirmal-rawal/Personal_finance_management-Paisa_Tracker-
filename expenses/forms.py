from django import forms
from django.contrib.auth.models import User
from .models import Budget

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter monthly budget'
            }),
        }