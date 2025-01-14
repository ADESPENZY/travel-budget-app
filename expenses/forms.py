from django import forms
from .models import Expense, CategoryBudget

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'receipt']

    def __init__(self, *args, **kwargs):
        trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)

        if trip:
            # Filter category dropdown by trip
            self.fields['category'].queryset = CategoryBudget.objects.filter(trip=trip)