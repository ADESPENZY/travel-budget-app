from django.shortcuts import render, redirect, get_object_or_404
from .forms import TripForm, ItineraryForm, CategoryBudgetForm
from django.contrib import messages
from .models import Trip, Itinerary, CategoryBudget
from userProfile.models import User_Profile
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

# Create your views here.
def add_trip(request):
    user_profile = User_Profile.objects.get(user=request.user)
    preferred_currency = user_profile.preferred_currency
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()
            messages.info(request, 'your account have been created successfully')
            return redirect('trip_list')
        else:
            messages.error(request, 'something went wrong')
            return redirect('add_trip') 
    else:
        form = TripForm()
        return render(request, 'travel/add_trip.html',  {'form': form, 'preferred_currency':preferred_currency})

CURRENCY_SYMBOLS = {
    'USD': '$',  # US Dollar
    'EUR': '€',  # Euro
    'GBP': '£',  # British Pound
    'JPY': '¥',  # Japanese Yen
    'AUD': 'A$',  # Australian Dollar
    'CAD': 'C$',  # Canadian Dollar
    'CHF': 'CHF',  # Swiss Franc
    'CNY': '¥',  # Chinese Yuan
    'SEK': 'kr',  # Swedish Krona
    'NZD': 'NZ$',  # New Zealand Dollar
    'MXN': 'Mex$',  # Mexican Peso
    'SGD': 'S$',  # Singapore Dollar
    'HKD': 'HK$',  # Hong Kong Dollar
    'NOK': 'kr',  # Norwegian Krone
    'KRW': '₩',  # South Korean Won
    'TRY': '₺',  # Turkish Lira
    'INR': '₹',  # Indian Rupee
    'RUB': '₽',  # Russian Ruble
    'ZAR': 'R',  # South African Rand
    'BRL': 'R$',  # Brazilian Real
    'THB': '฿',  # Thai Baht
    'MYR': 'RM',  # Malaysian Ringgit
    'IDR': 'Rp',  # Indonesian Rupiah
    'PHP': '₱',  # Philippine Peso
    'VND': '₫',  # Vietnamese Dong
    'ILS': '₪',  # Israeli Shekel
    'PLN': 'zł',  # Polish Zloty
    'AED': 'د.إ',  # United Arab Emirates Dirham
    'SAR': '﷼',  # Saudi Riyal
    'EGP': '£',  # Egyptian Pound
    'PKR': '₨',  # Pakistani Rupee
    'BDT': '৳',  # Bangladeshi Taka
    'NGN': '₦',  # Nigerian Naira
    'KWD': 'د.ك',  # Kuwaiti Dinar
}


def trip_list(request):
    # Fetch trips that belong to the current user and include related category_budgets
    trips = Trip.objects.filter(user=request.user).prefetch_related('category_budgets')

    # Retrieve the user's preferred currency
    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency = None
        preferred_currency_symbol = None  # Fallback if no profile exists

    return render(request, 'travel/trip_list.html', {
        'trips': trips,
        'preferred_currency': preferred_currency,
        'preferred_currency_symbol': preferred_currency_symbol
    })


def edit_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    user_profile = User_Profile.objects.get(user=request.user)
    preferred_currency = user_profile.preferred_currency  # Retrieve preferred currency

    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trip updated successfully!')
            return redirect('trip_list')
        else:
            messages.error(request, 'Failed to update trip. Please check the form for errors.')
    else:
        form = TripForm(instance=trip)

    return render(request, 'travel/edit_trip.html', {
        'form': form,
        'preferred_currency': preferred_currency
    })


# View to delete a trip
def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        trip.delete()
        return redirect('trip_list')
    return render(request, 'travel/trip_delete.html', {'trip': trip})


@login_required
def create_category_budget(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    # Retrieve the user's preferred currency
    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency = None
        preferred_currency_symbol = None  # Fallback if no profile exists

    if request.method == 'POST':
        form = CategoryBudgetForm(request.POST)
        if form.is_valid():
            category_budget = form.save(commit=False)
            category_budget.trip = trip  # Associate the budget with the selected trip
            category_budget.save()
            messages.success(request, f"Category budget for {category_budget.category} added successfully!")
            return redirect('trip_detail', trip_id=trip.id)
        else:
            messages.error(request, "Failed to add category budget. Please check the form.")
    else:
        form = CategoryBudgetForm()

    return render(request, 'travel/category_budget.html', {
        'form': form,
        'trip': trip,
        'preferred_currency': preferred_currency,
        'preferred_currency_symbol': preferred_currency_symbol
    })

@login_required
def edit_category_budget(request, trip_id, category_budget_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    category_budget = get_object_or_404(CategoryBudget, id=category_budget_id, trip=trip)
    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency = None
        preferred_currency_symbol = None  # Fallback if no profile exists

    if request.method == 'POST':
        form = CategoryBudgetForm(request.POST, instance=category_budget)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category budget for {category_budget.category} updated successfully!")
            return redirect('trip_detail', trip_id=trip.id)
        else:
            messages.error(request, "Failed to update category budget. Please check the form.")
    else:
        form = CategoryBudgetForm(instance=category_budget)

    return render(request, 'travel/edit_category_budget.html', {
        'form': form,
        'trip': trip,
        'category_budget': category_budget,
        'preferred_currency': preferred_currency,
        'preferred_currency_symbol': preferred_currency_symbol
    })

@login_required
def delete_category_budget(request, trip_id, category_budget_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    category_budget = get_object_or_404(CategoryBudget, id=category_budget_id, trip=trip)

    if request.method == 'POST':
        category_budget.delete()
        messages.success(request, f"Category budget for {category_budget.category} deleted successfully!")
        return redirect('trip_detail', trip_id=trip.id)

    return render(request, 'travel/confirm_delete_category_budget.html', {
        'trip': trip,
        'category_budget': category_budget,
    })

@login_required
def add_itinerary(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)  # Ensure the trip belongs to the user
    user_profile = get_object_or_404(User_Profile, user=request.user)  # Retrieve the user profile
    preferred_currency = user_profile.preferred_currency  # For the preferred currency
    category_budgets = CategoryBudget.objects.filter(trip=trip)

    if request.method == 'POST':
        form = ItineraryForm(request.POST, trip=trip)
        if form.is_valid():
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            category_budget = form.cleaned_data['category_budget']
            budget = form.cleaned_data['budget']

            # Check for valid times
            if end_time and start_time >= end_time:
                form.add_error('end_time', 'End time must be after the start time.')
            elif budget > category_budget.budget:
                form.add_error('budget', 'Itinerary budget exceeds the category budget.')
            else:
                itinerary_item = form.save(commit=False)
                itinerary_item.trip = trip  # Link the itinerary to the trip
                itinerary_item.save()
                return redirect('trip_detail', trip_id=trip.id)
    else:
        form = ItineraryForm(trip=trip)

    category_budgets_with_remaining = [
    {
        'category': category.category,
        'category_budget': category.budget,  # Pass only the category name (string)
        'remaining_budget': category.remaining_iti_budget(),
    }
    for category in category_budgets
]

    return render(request, 'travel/add_itinerary.html', {
        'form': form,
        'trip': trip,
        'preferred_currency': preferred_currency,
        'category_budgets': category_budgets_with_remaining,
    })

from django.http import HttpResponseServerError

@login_required
def trip_detail(request, trip_id):
    try:
        trip = get_object_or_404(Trip, id=trip_id)

        # Trip-level calculations
        total_trip_expenses = trip.total_expenses()
        total_trip_budget = trip.budget
        remaining_budget = total_trip_budget - total_trip_expenses

        # Itinerary-level calculations
        total_itineraries_budget = sum(category.total_itineraries() for category in trip.category_budgets.all())
        remaining_iti_budget = total_trip_budget - total_itineraries_budget

        # Data for the trip-level pie chart
        pie_chart_data = {
            'labels': ['Expenses', 'Remaining Budget'],
            'data': [float(total_trip_expenses), float(remaining_budget)],
        }

        # Data for the itinerary-level pie chart
        itinerary_pie_chart_data = {
            'labels': ['Total Itineraries', 'Remaining Itinerary Budget'],
            'data': [float(total_itineraries_budget), float(remaining_iti_budget)],
        }

        # Bar chart data (daily expenses)
        daily_expenses = trip.expenses.values('date').annotate(total=Sum('amount'))
        daily_labels = [entry['date'].strftime('%Y-%m-%d') for entry in daily_expenses]
        daily_totals = [entry['total'] for entry in daily_expenses]

        daily_bar_chart_data = {
            'labels': daily_labels,
            'data': daily_totals
        }

        context = {
            'trip': trip,
            'total_trip_budget': total_trip_budget,
            'total_trip_expenses': total_trip_expenses,
            'remaining_budget': remaining_budget,
            'pie_chart_data': pie_chart_data,
            'itinerary_pie_chart_data': itinerary_pie_chart_data,
            'daily_bar_chart_data': daily_bar_chart_data,
        }
        return render(request, 'travel/trip_detail.html', context)
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return HttpResponseServerError("An unexpected error occurred.")





