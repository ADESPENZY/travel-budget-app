from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_destinations, name="create_destinations"),
    path('destination_list', views.destinations_list, name="destinations_list")
]