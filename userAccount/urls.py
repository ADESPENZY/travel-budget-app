from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_user, name='register-page'),
    path('login_user/', views.login_user, name='login-page'),
    path('logout_user/', views.logout_user, name='logout-page'),
    
]