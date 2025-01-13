from django.urls import path
from . import views

urlpatterns = [
    path('<int:trip_id>/expenses/', views.expense_list, name='expense-list'),
    path('<int:trip_id>/add-expense/', views.add_expense, name='add-expense'),
]