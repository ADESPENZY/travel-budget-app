from django import forms
from .models import Trip, Itinerary, CategoryBudget

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['trip_name', 'destination_name', 'start_date', 'end_date', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'trip_name': 'Trip Name',
            'destination_name': 'Destination Name',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'budget': 'Budget',
        }

class ItineraryForm(forms.ModelForm):
    category_budget = forms.ModelChoiceField(
        queryset=CategoryBudget.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Itinerary
        fields = ['title', 'category_budget', 'details', 'start_time', 'end_time', 'budget']

    def __init__(self, *args, **kwargs):
        trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)
        if trip:
            self.fields['category_budget'].queryset = trip.category_budgets.all()

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


class CategoryBudgetForm(forms.ModelForm):
    class Meta:
        model = CategoryBudget
        fields = [ 'category', 'budget']
