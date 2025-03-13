# views.py
from django.shortcuts import render, redirect
from .forms import DestinationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    return render(request, "destination/destination_list.html")