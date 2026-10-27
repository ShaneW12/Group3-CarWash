from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.
def home(request):
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def about(request):
    return render(request, 'about.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "You have logged in successfully.")
            return redirect("index")

        messages.error(request, "Invalid email or password.")

    return render(request, "login.html")

def booking(request):
    return render(request, 'booking.html')

def signup(request):
    return render(request, 'signup.html')

def forgot_password(request):
    return render(request, 'forgot_password.html')