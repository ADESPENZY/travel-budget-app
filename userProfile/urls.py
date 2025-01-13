from django.urls import path
from . import views

urlpatterns = [
    path('', views.step_one, name='step_one'),
    path('step_two/', views.step_two, name='step_two'),
    path('review/', views.review, name='review'),
    path('profile_detail/', views.profile_detail, name='profile_detail'),
    path('update_profile/', views.update_profile, name='update_profile')
]