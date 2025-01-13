from django.shortcuts import render, redirect
from .forms import RegisterUser
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def register_user(request):
    if request.method == 'POST':
        form = RegisterUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully. You can now log in.")
            return redirect('login-page')  # Replace 'login-page' with your actual login view name
        else:
            messages.error(request, "There were errors in your form. Please fix them and try again.")
            return render(request, 'account/register-page.html', {'form': form})  # Re-render with errors
    else:
        form = RegisterUser()

    return render(request, 'account/register-page.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "You have been logged in successfully")
                return redirect("dashboard")  # Adjust redirection as needed
            else:
                messages.error(request, "Your account is inactive. Please contact support.")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'account/login-page.html')


def logout_user(request):
    logout(request)
    messages.info(request, 'You have successfully logged out of your account')


