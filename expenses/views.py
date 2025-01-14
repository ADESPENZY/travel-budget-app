from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from travel.models import Trip, CategoryBudget
from userProfile.models import User_Profile

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


def expense_list(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    sort_by = request.GET.get('sort', '') 
    
    # Get all expenses for the trip
    expenses = trip.expenses.all()

    if sort_by == 'date':
        expenses = expenses.order_by('date')  # Sort by date
    elif sort_by == 'amount':
        expenses = expenses.order_by('amount')  # Sort by amount

    # Filter by category if a filter is applied
    category_filter = request.GET.get('category')
    if category_filter:
        expenses = expenses.filter(category__category=category_filter)

    # Get all categories for the dropdown
    categories = CategoryBudget.objects.filter(trip=trip).values_list('category', flat=True)

    return render(request, 'expenses/expense_list.html', {
        'trip': trip,
        'expenses': expenses,
        'categories': categories,  # Pass categories for the dropdown
        'selected_category': category_filter,  # Pass the selected category to retain the filter
    })


def add_expense(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    category_budgets = CategoryBudget.objects.filter(trip=trip).select_related('trip')

    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency = None
        preferred_currency_symbol = None

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, trip=trip)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.trip = trip
            expense.save()
            return redirect('expense-list', trip_id=trip.id)
    else:
        form = ExpenseForm(initial={'trip': trip}, trip=trip)

    category_budgets_with_remaining = [
    {
        'category': category.category,
        'category_budget': category.budget,  # Pass only the category name (string)
        'remaining_budget': category.remaining_budget(),
    }
    for category in category_budgets
]

    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'trip': trip,
        'category_budgets': category_budgets_with_remaining,
        'preferred_currency_symbol': preferred_currency_symbol,
        'preferred_currency':preferred_currency,
    })
