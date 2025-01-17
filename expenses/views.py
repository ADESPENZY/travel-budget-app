from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from travel.models import Trip, CategoryBudget
from userProfile.models import User_Profile
from django.contrib.auth.decorators import login_required
import openpyxl
from django.http import HttpResponse
from django.core.paginator import Paginator

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

    # Paginate the expenses
    paginator = Paginator(expenses, 5)  # 5 expenses per page
    page_number = request.GET.get('page')
    expenses_page = paginator.get_page(page_number)    

    # Get all categories for the dropdown
    categories = CategoryBudget.objects.filter(trip=trip).values_list('category', flat=True)
    # Get all category to display not the strings 
    category = CategoryBudget.objects.filter(trip=trip)

    return render(request, 'expenses/expense_list.html', {
        'trip': trip,
        'expenses': expenses,
        'expenses': expenses_page,  # Use the paginated object
        'categories': categories,  # Pass categories for the dropdown
        'category': category,  # Pass categories for the dropdown
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

@login_required
def edit_expense(request, trip_id, expense_id):
    # Fetch the expense, ensuring it belongs to the given trip_id
    expense = get_object_or_404(Expense, id=expense_id, trip_id=trip_id)

    category_budgets = CategoryBudget.objects.filter(trip_id=trip_id).select_related('trip')

    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency = None
        preferred_currency_symbol = None

    # Ensure only the owner can edit the expense
    if request.user != expense.user:
        return redirect('trip_detail', trip_id=trip_id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, trip=expense.trip)
        if form.is_valid():
            form.save()
            return redirect('expense-list', trip_id=trip_id)
    else:
        form = ExpenseForm(instance=expense, trip=expense.trip)

    category_budgets_with_remaining = [
        {
            'category': category.category,
            'category_budget': category.budget,
            'remaining_budget': category.remaining_budget(),
        }
        for category in category_budgets
    ]

    return render(request, 'expenses/edit_expense.html', {
        'form': form,
        'trip': expense.trip,
        'expense': expense,
        'category_budgets': category_budgets_with_remaining,
        'preferred_currency_symbol': preferred_currency_symbol,
        'preferred_currency': preferred_currency,
    })

@login_required
def expense_detail(request, trip_id, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, trip_id=trip_id)
    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
        preferred_currency_symbol = CURRENCY_SYMBOLS.get(preferred_currency, preferred_currency)
    except User_Profile.DoesNotExist:
        preferred_currency_symbol = ''

    return render(request, 'expenses/expense_detail.html', {
        'expense': expense,
        'preferred_currency_symbol': preferred_currency_symbol,
    })

@login_required
def delete_expense(request, trip_id, expense_id):
    # Fetch the expense ensuring it belongs to the user and the given trip_id
    expense = get_object_or_404(Expense, id=expense_id, trip_id=trip_id, user=request.user)
    
    if request.method == 'POST':
        expense.delete()
        return redirect('expense-list', trip_id=trip_id)

    return render(request, 'expenses/delete_expense.html', {'expense': expense})

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from travel.models import Trip
from userProfile.models import User_Profile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


@login_required
def download_expenses_pdf(request, trip_id):
    from django.template.defaultfilters import truncatewords

    # Get the trip and related expenses
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    expenses = trip.expenses.all()

    # Fetch the user's preferred currency
    try:
        user_profile = User_Profile.objects.get(user=request.user)
        preferred_currency = user_profile.preferred_currency
    except User_Profile.DoesNotExist:
        preferred_currency = 'N/A'

    # Create the HttpResponse object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=expenses_{trip.trip_name}.pdf'

    # Create the PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Title
    styles = getSampleStyleSheet()
    title = Paragraph(f"Expenses for {trip.trip_name}", styles['Title'])
    elements.append(title)

    # Table data
    data = [['Date', 'Category', 'Description', 'Amount', 'Preferred Currency']]
    total_expenses = 0
    for expense in expenses:
        total_expenses += expense.amount
        # Truncate the description to 6 words
        truncated_description = truncatewords(expense.description, 6)
        data.append([
            expense.date.strftime('%Y-%m-%d'),  # Date
            expense.category.category,  # Category
            truncated_description,  # Truncated Description
            expense.amount,  # Amount
            preferred_currency  # Preferred Currency
        ])

    # Add totals row
    data.append(['', '', 'Total', total_expenses, preferred_currency])

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
