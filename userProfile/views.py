from django.shortcuts import render, redirect
from .forms import StepOneForm, StepTwoForm
from .models import User_Profile
from datetime import datetime
import re 
# Create your views here.

def step_one(request):
    errors = {}  # Dictionary to store validation errors
    form_data = request.session.get('step_one_data', {})

    if request.method == 'POST':
        # Retrieve form data from POST request
        form_data['firstname'] = request.POST.get('firstname', '').strip()
        form_data['lastname'] = request.POST.get('lastname', '').strip()
        form_data['dob'] = request.POST.get('dob', '').strip()
        form_data['bio'] = request.POST.get('bio', '').strip()
        form_data['country'] = request.POST.get('country', '').strip()
        form_data['city'] = request.POST.get('city', '').strip()
        form_data['phone_number'] = request.POST.get('phone_number', '').strip()

        # Validation logic
        if not form_data['firstname']:
            errors['firstname'] = "First name is required."
        elif len(form_data['firstname']) < 2:
            errors['firstname'] = "First name must be at least 2 characters long."

        if not form_data['lastname']:
            errors['lastname'] = "Last name is required."
        elif len(form_data['lastname']) < 2:
            errors['lastname'] = "Last name must be at least 2 characters long."

        if not form_data['dob']:
            errors['dob'] = "Date of birth is required."
        else:
            try:
                from datetime import datetime
                dob = datetime.strptime(form_data['dob'], '%Y-%m-%d')  # Assuming YYYY-MM-DD format
                if dob.year < 1900 or dob > datetime.now():
                    errors['dob'] = "Please enter a valid date of birth."
            except ValueError:
                errors['dob'] = "Invalid date format. Please use YYYY-MM-DD."

        if not form_data['bio']:
            errors['bio'] = "Bio is required."
        elif len(form_data['bio']) > 500:
            errors['bio'] = "Bio must not exceed 500 characters."

        if not form_data['country']:
            errors['country'] = "Country is required."

        if not form_data['city']:
            errors['city'] = "City is required."

        if not form_data['phone_number']:
            errors['phone_number'] = "Phone number is required."
        else:
            # Clean up the phone number (remove spaces, parentheses, hyphens, etc.)
            phone_number = re.sub(r"[^\d+]", "", form_data['phone_number'])
            international_pattern = r"^\+\d{10,15}$"  # Matches + followed by 10 to 15 digits
            local_pattern = r"^\d{10}$"  # Matches exactly 10 digits (US format without country code)

            if not (re.match(international_pattern, phone_number) or re.match(local_pattern, phone_number)):
                errors['phone_number'] = (
                    "Phone number must be in international format (e.g., +1234567890) or "
                    "a 10-digit US format (e.g., 8329873124)."
                )
            else:
                form_data['phone_number'] = phone_number  # Save cleaned phone number


        # If there are no errors, save data to the session and proceed
        if not errors:
            request.session['step_one_data'] = form_data
            return redirect('step_two')  # Replace 'next_step' with your next step URL

    # If validation fails or it's a GET request, render the form with errors
    return render(request, 'userProfile/add_profile.html', {
        'form_data': form_data,
        'error': errors,
    })


def step_two(request):
    errors = {}  # Dictionary to store validation errors
    form_data = request.session.get('step_two_data', {})  # Retrieve saved session data

    # Dropdown options for user_profile
    preferred_currency_options = dict(User_Profile.CURRENCY_CHOICES)
    travel_preferences_options = dict(User_Profile.TRAVEL_PREFERENCES)
    travel_frequency_options = dict(User_Profile.TRAVEL_FREQUENCY_CHOICES)

    if request.method == 'POST':
        # Retrieve form data from POST request
        form_data['preferred_currency'] = request.POST.get('preferred_currency')
        form_data['travel_preferences'] = request.POST.getlist('travel_preferences')  # Handles multiple preferences
        form_data['travel_frequency'] = request.POST.get('travel_frequency')
        form_data['favorite_destinations'] = request.POST.get('favorite_destinations', '').strip()
        form_data['emergency_contact_name'] = request.POST.get('emergency_contact_name', '').strip()
        form_data['emergency_contact_phone'] = request.POST.get('emergency_contact_phone', '').strip()

        # Validate form fields
        if not form_data['preferred_currency']:
            errors['preferred_currency'] = "At least one preferred currency must be selected."

        if not form_data['travel_preferences']:
            errors['travel_preferences'] = "At least one travel preference must be selected."

        if not form_data['travel_frequency']:
            errors['travel_frequency'] = "At least one travel frequency must be selected."

        if not form_data['favorite_destinations']:
            errors['favorite_destinations'] = "Enter Your Favorite Destinations."
        elif len(form_data['favorite_destinations']) < 2:
            errors['favorite_destinations'] = "Favorite Destination must be at least 2 characters long."

        if not form_data['emergency_contact_name']:
            errors['emergency_contact_name'] = "Emergency contact name is required."
        elif len(form_data['emergency_contact_name']) < 2:
            errors['emergency_contact_name'] = "Emergency contact name must be at least 2 characters long."

        if not form_data.get('emergency_contact_phone'):
            errors['emergency_contact_phone'] = "Emergency contact phone is required."
        else:
            # Clean up the phone number (remove spaces, parentheses, hyphens, etc.)
            emergency_contact_phone = re.sub(r"[^\d+]", "", form_data['emergency_contact_phone'].strip())

            # International format: + followed by 10-15 digits
            international_pattern = r"^\+\d{10,15}$"
            # Local format: Exactly 10 digits
            local_pattern = r"^\d{10}$"

            if not (re.match(international_pattern, emergency_contact_phone) or re.match(local_pattern, emergency_contact_phone)):
                errors['emergency_contact_phone'] = (
                    "Phone number must be in international format (e.g., +1234567890) or "
                    "a 10-digit local format (e.g., 8329873124)."
                )
            else:
                form_data['emergency_contact_phone'] = emergency_contact_phone  # Save cleaned phone number

        # Handle file upload separately
        image = request.FILES.get('image')
        if not image:
            errors['image'] = "Profile image is required."
        elif not image.content_type.startswith('image/'):
            errors['image'] = "Uploaded file must be an image."

        # If there are no validation errors, save to the model
        if not errors:
            # Retrieve the current user's profile
            user_profile, created = User_Profile.objects.get_or_create(user=request.user)

            # Save data from both steps
            step_one_data = request.session.get('step_one_data', {})
            user_profile.firstname = step_one_data.get('firstname')
            user_profile.lastname = step_one_data.get('lastname')
            user_profile.dob = step_one_data.get('dob')
            user_profile.bio = step_one_data.get('bio')
            user_profile.country = step_one_data.get('country')
            user_profile.city = step_one_data.get('city')
            user_profile.phone_number = step_one_data.get('phone_number')

            user_profile.preferred_currency = form_data.get('preferred_currency')
            user_profile.travel_preferences = form_data.get('travel_preferences')
            user_profile.travel_frequency = form_data.get('travel_frequency')
            user_profile.favorite_destinations = form_data.get('favorite_destinations')
            user_profile.emergency_contact_name = form_data.get('emergency_contact_name')
            user_profile.emergency_contact_phone = form_data.get('emergency_contact_phone')

            # Assign the uploaded image
            if image:
                user_profile.image = image

            # Mark the profile as complete
            user_profile.complete_profile = True
            user_profile.save()

            # Save non-file form data to the session
            request.session['step_two_data'] = form_data
            return redirect('review')  # Redirect to the next step

    # Render the form with errors (if any) or prefill existing session data
    return render(request, 'userProfile/add_profile2.html', {
        'form_data': form_data,
        'error': errors,
        'currency_options': preferred_currency_options,
        'preference_options': travel_preferences_options,
        'frequency_options': travel_frequency_options
    })

from django.core.exceptions import ObjectDoesNotExist

def review(request):
    # Collect all data from session
    step_one_data = request.session.get('step_one_data', {})
    step_two_data = request.session.get('step_two_data', {})

    # Handle image separately (since it cannot be stored in sessions)
    image = request.FILES.get('image')
    if image:
        step_two_data['image'] = image

    review_data = {
        **step_one_data,
        **step_two_data,
    }

    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Redirect unauthenticated users to the login page
            return redirect('login')  # Replace with your login page URL

        try:
            # Check if a User_Profile for this user already exists
            user_profile = User_Profile.objects.get(user=request.user)
            # Update the existing profile
            user_profile.firstname = review_data.get('firstname')
            user_profile.lastname = review_data.get('lastname')
            user_profile.dob = review_data.get('dob')
            user_profile.bio = review_data.get('bio')
            user_profile.country = review_data.get('country')
            user_profile.city = review_data.get('city')
            user_profile.phone_number = review_data.get('phone_number')
            user_profile.preferred_currency = review_data.get('preferred_currency')
            user_profile.travel_preferences = review_data.get('travel_preferences')
            user_profile.travel_frequency = review_data.get('travel_frequency')
            user_profile.favorite_destinations = review_data.get('favorite_destinations')
            user_profile.emergency_contact_name = review_data.get('emergency_contact_name')
            user_profile.emergency_contact_phone = review_data.get('emergency_contact_phone')

            if image:
                user_profile.image = image
            user_profile.save()

        except ObjectDoesNotExist:
            # Create a new User_Profile if one doesn't exist
            user_profile = User_Profile(
                user=request.user,  # Associate with the logged-in user
                firstname=review_data.get('firstname'),
                lastname=review_data.get('lastname'),
                dob=review_data.get('dob'),
                bio=review_data.get('bio'),
                country=review_data.get('country'),
                city=review_data.get('city'),
                phone_number=review_data.get('phone_number'),
                preferred_currency=review_data.get('preferred_currency'),
                travel_preferences=review_data.get('travel_preferences'),
                travel_frequency=review_data.get('travel_frequency'),
                favorite_destinations=review_data.get('favorite_destinations'),
                emergency_contact_name=review_data.get('emergency_contact_name'),
                emergency_contact_phone=review_data.get('emergency_contact_phone'),
            )

            if image:
                user_profile.image = image
            user_profile.save()

        # Clear session data after saving
        request.session.pop('step_one_data', None)
        request.session.pop('step_two_data', None)

        # Redirect to a success page or dashboard
        return redirect('dashboard')  # Replace with your success page URL

    # Render the review page with collected data
    return render(request, 'userProfile/review.html', {
        'review_data': review_data,
    })

def profile_detail(request):
    profile = User_Profile.objects.get(user=request.user)
    return render(request, 'userProfile/profile_detail.html', {'profile':profile})

from django.shortcuts import render, redirect, get_object_or_404
from .models import User_Profile
from .forms import StepOneForm, StepTwoForm
from django.contrib.auth.decorators import login_required

@login_required
def update_profile(request):
    # Get the user's profile, or return a 404 if not found
    user_profile = get_object_or_404(User_Profile, user=request.user)

    if request.method == 'POST':
        # Update the first part of the profile
        step_one_form = StepOneForm(request.POST, instance=user_profile)
        step_two_form = StepTwoForm(request.POST, request.FILES, instance=user_profile)

        if step_one_form.is_valid() and step_two_form.is_valid():
            # Save the updated data
            step_one_form.save()
            step_two_form.save()

            # Redirect to a success page or user dashboard
            return redirect('profile_detail')  # Replace with your success page URL
    else:
        # Pre-fill the forms with the user's existing data
        step_one_form = StepOneForm(instance=user_profile)
        step_two_form = StepTwoForm(instance=user_profile)

    return render(request, 'userProfile/edit_profile.html', {
        'step_one_form': step_one_form,
        'step_two_form': step_two_form,
    })
