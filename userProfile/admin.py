from django.contrib import admin
from .models import User_Profile

# Register your models here.
@admin.register(User_Profile)
class User_ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'firstname', 
        'lastname', 
        'dob', 
        'preferred_currency', 
        'travel_preferences', 
        'travel_frequency', 
        'country', 
        'city', 
        'phone_number', 
        'complete_profile'
    )
    list_filter = (
        'preferred_currency', 
        'travel_preferences', 
        'travel_frequency', 
        'country', 
        'complete_profile'
    )
    search_fields = (
        'user__username', 
        'firstname', 
        'lastname', 
        'country', 
        'city', 
        'phone_number'
    )
    readonly_fields = ('user',)
    