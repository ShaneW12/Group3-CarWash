
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get(
            "confirm_password", ""
        )

        # Validate required fields
        if not all([
            first_name,
            last_name,
            email,
            phone,
            password
        ]):
            messages.error(
                request,
                "Please complete all required fields."
            )
            return render(request, "signup.html")

        # Confirm passwords match
        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return render(request, "signup.html")

        # Check for duplicate email
        if User.objects.filter(
            email__iexact=email
        ).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return render(request, "signup.html")

        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as error:
            messages.error(
                request,
                " ".join(error.messages)
            )
            return render(request, "signup.html")

        # Create customer and save phone number
        User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        messages.success(
            request,
            "Account created successfully. Please log in."
        )

        return redirect("login")

    return render(request, "signup.html")
