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

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        category = self.cleaned_data.get('category')
        
        if category:
            remaining_budget = category.remaining_budget()
            if amount > remaining_budget:
                raise forms.ValidationError(
                    f"The amount exceeds the remaining budget for the category '{category.category}'. "
                    f"Remaining budget: {remaining_budget}."
                )
        return amount

        