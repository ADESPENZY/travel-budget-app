from django.urls import path
from . import views

urlpatterns = [
    path('', views.add_trip, name='add_trip'),
    path('trip_list/', views.trip_list, name='trip_list'),
    path('trips/edit/<int:trip_id>/', views.edit_trip, name='edit_trip'),  # Edit a specific trip
    path('trips/delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),  # Delete a specific trip
    path('trip/<int:trip_id>/category-budget/', views.create_category_budget, name='category_budget'),
    path('trip/<int:trip_id>/category_budget/<int:category_budget_id>/edit/', views.edit_category_budget, name='edit_category_budget'),
    path('trip/<int:trip_id>/category_budget/<int:category_budget_id>/delete/', views.delete_category_budget, name='delete_category_budget'),
    path('<int:trip_id>/items/add/', views.add_itinerary, name='add_itinerary'),
    path('<int:trip_id>/items/edit/<int:itinerary_id>/', views.edit_itinerary, name='edit_itinerary'),
    path('<int:trip_id>/items/delete/<int:itinerary_id>/', views.delete_itinerary, name='delete_itinerary'),
    path('<int:trip_id>/items/list/', views.list_itinerary, name='list_itinerary'),
    path('travel/<int:trip_id>/details/', views.trip_detail, name='trip_detail'),
]