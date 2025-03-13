# forms.py
from django import forms
from .models import Destination

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['location_name', 'country', 'description', 'price', 'image', 'is_popular']
