from django.shortcuts import render, redirect, get_object_or_404
from .forms import TripForm, ItineraryForm, CategoryBudgetForm
from django.contrib import messages
from .models import Trip, Itinerary, CategoryBudget
from userProfile.models import User_Profile
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from travel.models import Trip
from userProfile.models import User_Profile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.utils.text import Truncator  # Import Truncator

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
            category_budget.trip = trip  # Associate the budget with the trip

            # Set the trip before calling `clean()`
            try:
                category_budget.clean()  # Call clean explicitly to validate
                existing_budgets_total = trip.category_budgets.aggregate(total=Sum('budget'))['total'] or 0
                total_after_adding = existing_budgets_total + category_budget.budget

                if total_after_adding > trip.budget:
                    messages.error(
                        request,
                        f"Adding this category budget exceeds the trip's overall budget of {trip.budget} {preferred_currency_symbol}. "
                        f"Please adjust the budget."
                    )
                else:
                    category_budget.save()
                    messages.success(request, f"Category budget for {category_budget.category} added successfully!")
                    return redirect('trip_detail', trip_id=trip.id)
            except ValidationError as e:
                messages.error(request, f"Validation error: {e}")
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
    # Get the trip and category budget
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    category_budget = get_object_or_404(CategoryBudget, id=category_budget_id, trip=trip)

    # Retrieve the user's preferred currency and symbol
    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency = None
        preferred_currency_symbol = None

    if request.method == 'POST':
        form = CategoryBudgetForm(request.POST, instance=category_budget)
        if form.is_valid():
            category_budget = form.save(commit=False)
            category_budget.trip = trip  # Associate the budget with the trip

            # Validate total budget
            category_budget.clean()  # Call clean explicitly to validate
            existing_budgets_total = (
                trip.category_budgets.exclude(id=category_budget.id)
                .aggregate(total=Sum('budget'))['total']
                or 0
            )
            total_after_edit = existing_budgets_total + category_budget.budget

            if total_after_edit > trip.budget:
                messages.error(
                    request,
                    f"Updating this category budget exceeds the trip's overall budget of "
                    f"{trip.budget} {preferred_currency_symbol}. Please adjust the budget."
                )
            else:
                category_budget.save()
                messages.success(request, f"Category budget for '{category_budget.category}' updated successfully!")
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
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    user_profile = get_object_or_404(User_Profile, user=request.user)
    preferred_currency = user_profile.preferred_currency
    category_budgets = CategoryBudget.objects.filter(trip=trip)

    if request.method == 'POST':
        form = ItineraryForm(request.POST, trip=trip)
        if form.is_valid():
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            category_budget = form.cleaned_data['category_budget']
            budget = form.cleaned_data['budget']

            if end_time and start_time and start_time >= end_time:
                form.add_error('end_time', 'End time must be after the start time.')
            elif budget > category_budget.budget:
                form.add_error('budget', 'Itinerary budget exceeds the category budget.')
            else:
                itinerary_item = form.save(commit=False)
                itinerary_item.trip = trip
                itinerary_item.save()
                return redirect('trip_detail', trip_id=trip.id)
    else:
        form = ItineraryForm(trip=trip)

    category_budgets_with_remaining = [
        {
            'category': category.category,
            'category_budget': category.budget,
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

@login_required
def edit_itinerary(request, trip_id, itinerary_id):
    itinerary = get_object_or_404(Itinerary, id=itinerary_id, trip_id=trip_id)
    category_budgets = CategoryBudget.objects.filter(trip_id=trip_id).select_related('trip')

    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency = None
        preferred_currency_symbol = None

    if request.user != itinerary.trip.user:
        return redirect('trip_detail', trip_id=trip_id)

    if request.method == 'POST':
        form = ItineraryForm(request.POST, request.FILES, instance=itinerary, trip=itinerary.trip)
        if form.is_valid():
            form.save()
            return redirect('list_itinerary', trip_id=trip_id)
    else:
        form = ItineraryForm(instance=itinerary, trip=itinerary.trip)

    category_budgets_with_remaining = [
        {
            'category': category.category,
            'category_budget': category.budget,
            'remaining_budget': category.remaining_iti_budget(),
        }
        for category in category_budgets
    ]

    return render(request, 'travel/edit_itinerary.html', {
        'form': form,
        'trip': itinerary.trip,
        'itinerary': itinerary,
        'category_budgets': category_budgets_with_remaining,
        'preferred_currency_symbol': preferred_currency_symbol,
        'preferred_currency': preferred_currency,
    })

@login_required
def delete_itinerary(request, trip_id, itinerary_id):
    # Fetch the itinerary ensuring it belongs to the user and the given trip_id
    itinerary = get_object_or_404(Itinerary, id=itinerary_id, trip_id=trip_id, user=request.user)
    
    if request.method == 'POST':
        itinerary.delete()
        return redirect('itinerary-list', trip_id=trip_id)

    return render(request, 'travel/delete_itinerary.html', {'itinerary': itinerary})

def list_itinerary(request, trip_id):
    # Get the trip object or return a 404 if not found
    trip = get_object_or_404(Trip, id=trip_id)

    # Retrieve all itineraries associated with the trip
    items = trip.items.all()  # `related_name='items'` in the Itinerary model

    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'start_time':
        items = items.order_by('start_time')  # Sort by start time
    elif sort_by == 'budget':
        items = items.order_by('budget')  # Sort by budget

    # Filtering by category
    category_filter = request.GET.get('category')
    if category_filter:
        items = items.filter(category_budget__category=category_filter)

    # Pagination
    paginator = Paginator(items, 5)  # Show 5 itineraries per page
    page_number = request.GET.get('page')
    items_page = paginator.get_page(page_number)

    # Get all categories for the dropdown
    categories = CategoryBudget.objects.filter(trip=trip).values_list('category', flat=True)
    category_objects = CategoryBudget.objects.filter(trip=trip)

    return render(request, 'travel/itinerary_list.html', {
        'trip': trip,
        'itineraries': items,  # Pass unpaginated list if needed elsewhere
        'itineraries_page': items_page,  # Pass the paginated object
        'categories': categories,  # Pass category names for the dropdown
        'category_objects': category_objects,  # Pass full category objects
        'selected_category': category_filter,  # Pass selected category for retaining filter
    })

@login_required
def itinerary_detail(request, trip_id, itinerary_id):
    # Get the itinerary associated with the trip and user
    itinerary = get_object_or_404(Itinerary, id=itinerary_id, trip_id=trip_id, trip__user=request.user)

    # Fetch the user's preferred currency
    user_profile = get_object_or_404(User_Profile, user=request.user)
    preferred_currency = user_profile.preferred_currency
    preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)

    return render(request, 'travel/itinerary_detail.html', {
        'itinerary': itinerary,
        'preferred_currency': preferred_currency,
        'preferred_currency_symbol': preferred_currency_symbol,
    })

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

@login_required
def download_itinerary_pdf(request, trip_id):
    # Get the trip and related itineraries
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    itineraries = trip.items.all()

    # Create the HttpResponse object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=itinerary_{trip.trip_name}.pdf'

    # Create the PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Title
    styles = getSampleStyleSheet()
    title = Paragraph(f"Itinerary for {trip.trip_name}", styles['Title'])
    elements.append(title)

    # Table data
    data = [['Title', 'Category', 'Details', 'Start Time', 'End Time', 'Budget']]
    total_budget = 0
    for itinerary in itineraries:
        # Truncate the details to 6 words
        truncated_description = Truncator(itinerary.details).words(3) if itinerary.details else 'N/A'
        total_budget += itinerary.budget
        data.append([
            itinerary.title,
            itinerary.category_budget.category,  # Category name
            truncated_description,  # Truncated details
            itinerary.start_time.strftime('%Y-%m-%d %H:%M:%S'),  # Start time
            itinerary.end_time.strftime('%Y-%m-%d %H:%M:%S') if itinerary.end_time else 'N/A',  # End time
            itinerary.budget,  # Budget
        ])

    # Add totals row
    data.append(['', '', '', '', 'Total Budget', total_budget])

    # Create the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Rows background
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Table grid
    ]))
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    return response








