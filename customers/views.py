from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()


def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "signup.html")

        User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "signup.html")

# Create your views here.
