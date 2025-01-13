from django.forms import ModelForm
from . models import User_Profile

class StepOneForm(ModelForm):
    class Meta:
        model = User_Profile
        fields = ['firstname', 'lastname', 'dob', 'bio', 'country', 'city', 'phone_number']

class StepTwoForm(ModelForm):
    class Meta:
        model = User_Profile
        fields = [
            'preferred_currency','travel_preferences', 'travel_frequency', 'image',
            'favorite_destinations', 
            'emergency_contact_name', 'emergency_contact_phone'
        ]
