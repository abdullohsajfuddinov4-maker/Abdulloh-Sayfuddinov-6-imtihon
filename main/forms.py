from .models import Expenses ,Income
from django import forms

class ExpensesForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['amount', 'category', 'date', 'description']