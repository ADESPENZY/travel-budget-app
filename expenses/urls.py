from django.urls import path
from . import views

urlpatterns = [
    path('<int:trip_id>/expenses/', views.expense_list, name='expense-list'),
    path('<int:trip_id>/add-expense/', views.add_expense, name='add-expense'),
    path('<int:trip_id>/expenses/edit/<int:expense_id>/', views.edit_expense, name='edit-expense'),
    path('<int:trip_id>/expenses/delete/<int:expense_id>/', views.delete_expense, name='delete-expense'),
]