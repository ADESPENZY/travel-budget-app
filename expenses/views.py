from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from travel.models import Trip

def expense_list(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    expenses = trip.expenses.all()
    return render(request, 'expenses/expense_list.html', {'trip': trip, 'expenses': expenses})

def add_expense(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.trip = trip
            expense.save()
            return redirect('expense-list', trip_id=trip.id)
    else:
        form = ExpenseForm(initial={'trip': trip})
    return render(request, 'expenses/add_expense.html', {'form': form, 'trip': trip})
