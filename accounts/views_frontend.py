from django.shortcuts import render

def login_page(request):
    return render(request, 'auth/login.html')

def register_page(request):
    return render(request, 'auth/register.html')

def home_page(request):
    return render(request, 'home/home.html')

def profile_page(request):
    return render(request, 'profile.html')