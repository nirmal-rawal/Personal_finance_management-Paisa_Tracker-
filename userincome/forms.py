from django import forms
from django.contrib.auth.models import User
from .models import Income

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class IncomeForm(forms.ModelForm):
    receipt = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'd-none'
        })
    )
    
    class Meta:
        model = Income
        fields = ['amount', 'date', 'description', 'source', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'source': forms.Select(attrs={
                'class': 'form-control'
            })
        }        