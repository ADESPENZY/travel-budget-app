from django.contrib import admin
from .models import Trip, Itinerary, CategoryBudget

class TripAdmin(admin.ModelAdmin):
    list_display = ('trip_name', 'start_date', 'end_date', 'destination_name', 'budget')  # Corrected
    list_filter = ('start_date', 'end_date', 'destination_name')  # Optional, for filtering
    search_fields = ('trip_name', 'destination_name')  # Optional, for search functionality

class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_budget', 'trip', 'start_time', 'end_time', 'budget')
    list_filter = ('category_budget', 'trip')
    search_fields = ('title', 'category_budget')

class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'budget')
    list_filter = ('category', 'budget')
    search_fields = ('category',)

admin.site.register(Trip, TripAdmin)
admin.site.register(Itinerary, ItineraryAdmin)
admin.site.register(CategoryBudget, CategoryBudgetAdmin)
