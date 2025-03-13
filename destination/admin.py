from django.contrib import admin
from .models import Destination, Country

admin.site.register(Country)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'country', 'is_popular', 'price')  # Show in list
    list_filter = ('is_popular', 'country')  # Add filtering
    search_fields = ('location_name', 'country__country')  # Search destinations