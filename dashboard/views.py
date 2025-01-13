from django.shortcuts import redirect, render
from userProfile.models import User_Profile
from travel.models import Trip

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    try:
        # Check if the user's profile is complete
        user_profile = User_Profile.objects.get(user=request.user)
        if not user_profile.complete_profile:
            return redirect('step_one')  # Redirect to profile completion page
    except User_Profile.DoesNotExist:
        return redirect('step_one')  # Redirect to profile creation

    # Fetch the user's trips
    user_trips = Trip.objects.filter(user=request.user)
    return render(request, 'dashboard/dashboard.html', {
        'user_profile': user_profile,
        'user_trips': user_trips,
    })

