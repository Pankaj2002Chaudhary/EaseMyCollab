from django.shortcuts import render

def login_page(request):
    return render(request, 'auth/login.html')

def register_page(request):
    return render(request, 'auth/register.html')

def home_page(request):
    return render(request, 'home/home.html')

def profile_page(request):
    return render(request, 'profile.html')
from django.shortcuts import render

def forgot_password_page(request):
    """Browser par Forgot Password ka HTML page render karne ke liye"""
    return render(request, 'auth/forget_password.html')