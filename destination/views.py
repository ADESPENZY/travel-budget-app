# views.py
from django.shortcuts import get_object_or_404, render, redirect
from .forms import DestinationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Country, Destination
from django.core.paginator import Paginator
from travel.forms import TripForm

@login_required
def create_destinations(request):
    if request.method == "POST":
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Destination created successfully!")
            return redirect('home-page')  # Redirect to the destination list page
    else:
        form = DestinationForm()
    
    return render(request, 'destination/create_destinations.html', {'form': form})

def destinations_list(request):
    countries = Country.objects.all()
    destinations = Destination.objects.all()

    selected_country_id = request.GET.get('country')
    if selected_country_id:
        destinations = destinations.filter(country_id=selected_country_id)  # Filter by country ID

    # Pagination: Show 3 destinations per page
    paginator = Paginator(destinations, 3)  # 3 destinations per page
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)

    return render(request, 'destination/destination_list.html', {
        'countries': countries,
        'selected_country_id': selected_country_id,
        'destinations': destinations,
        'page_obj': page_obj 
    })

def destinations_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)

    # Assuming you're using a separate view for creating trips
    trip_form = TripForm(initial={'destination': destination.location_name})

    context = {
        'destination': destination,
        'trip_form': trip_form,  # Pass the form to the context
    }

    return render(request, 'destination/destination_detail.html', context)
