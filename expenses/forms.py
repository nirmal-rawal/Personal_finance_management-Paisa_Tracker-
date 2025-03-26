from django import forms
from django.contrib.auth.models import User
from .models import Budget, Expenses
from django.core.validators import FileExtensionValidator

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

class ExpenseForm(forms.ModelForm):
    receipt = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'd-none'
        })
    )
    
    class Meta:
        model = Expenses
        fields = ['amount', 'date', 'description', 'category', 'transaction_type', 'receipt']
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
            'category': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].widget = forms.RadioSelect(
            choices=[('Expense', 'Expense'), ('Income', 'Income')],
            attrs={'class': 'form-check-input'}
        )