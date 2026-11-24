
from datetime import date as today_date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date, parse_time
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Appointment


# Existing website pages
def home(request):
    return render(request, 'index.html')


def services(request):
    return render(request, 'services.html')


def about(request):
    return render(request, 'about.html')


def login(request):
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = ""

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = None
        # The original branch uses Django's default username-based user model.
        # Looking up the username by email allows customers to sign in using email.
        if email and password:
            match = get_user_model().objects.filter(email__iexact=email).first()
            if match:
                user = authenticate(request, username=match.get_username(), password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect(next_url or "my_appointments")
        messages.error(request, "Incorrect email or password.")
    return render(request, "login.html", {"next": next_url})


def logout(request):
    if request.method == "POST":
        auth_logout(request)
        messages.success(request, "You have logged out.")
    return redirect("index")


# Appointment Management - Create
def booking(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        # Signed-in customers can only create bookings for their own account.
        if request.user.is_authenticated:
            email = request.user.email.lower()
        phone = request.POST.get("phone", "").strip()

        vehicle = request.POST.get("vehicle", "")
        selected_services = request.POST.getlist("service")

        appointment_date = parse_date(request.POST.get("date", ""))
        appointment_time = parse_time(request.POST.get("time", ""))

        vehicles = {
            "civic": ("Honda", "Civic"),
            "rav4": ("Toyota", "RAV4"),
        }

        allowed_services = {
            "basic-wash",
            "triple-foam",
            "undercarriage",
            "vacuum",
            "detail",
            "tire-shine",
        }

        if (
            not first_name
            or not last_name
            or not email
            or not phone
            or vehicle not in vehicles
            or not selected_services
            or any(s not in allowed_services for s in selected_services)
            or not appointment_date
            or not appointment_time
        ):
            messages.error(
                request,
                "Please complete all booking fields correctly."
            )
            return render(request, "booking.html")

        if appointment_date < today_date.today():
            messages.error(
                request,
                "Please choose today or a future appointment date."
            )
            return render(request, "booking.html")

        make, model = vehicles[vehicle]

        appointment = Appointment(
            customer_name=f"{first_name} {last_name}",
            email=email,
            phone=phone,
            vehicle_make=make,
            vehicle_model=model,
            service=", ".join(selected_services),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status="Scheduled",
        )

        try:
            appointment.full_clean()
            appointment.save()
        except ValidationError:
            messages.error(
                request,
                "Please check your appointment information."
            )
            return render(request, "booking.html")

        messages.success(
            request,
            "Your appointment was created successfully!"
        )
        return redirect("booking")

    return render(request, "booking.html")


def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if not all([first_name, last_name, email, password]) or password != confirm:
            messages.error(request, "Complete all fields and make sure passwords match.")
            return render(request, "signup.html")
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "signup.html")
        try:
            validate_password(password)
            with transaction.atomic():
                # In this original SQLite branch the default User model uses username.
                # Store email as username so the account has a stable unique login.
                user = User.objects.create_user(
                    username=email, email=email, password=password,
                    first_name=first_name, last_name=last_name,
                )
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
            return render(request, "signup.html")
        except IntegrityError:
            messages.error(request, "That account already exists.")
            return render(request, "signup.html")
        auth_login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("my_appointments")
    return render(request, "signup.html")


def forgot_password(request):
    return render(request, 'forgot_password.html')


# Appointment Management - View
@login_required(login_url="/login/")
def my_appointments(request):
    appointments = Appointment.objects.filter(
        email__iexact=request.user.email
    ).order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "my_appointments.html",
        {"appointments": appointments}
    )


# Appointment Management - Cancel
@login_required(login_url="/login/")
@require_POST
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        email__iexact=request.user.email
    )

    if appointment.status != "Scheduled":
        messages.error(
            request,
            "Only scheduled appointments can be cancelled."
        )
    else:
        appointment.status = "Cancelled"
        appointment.save(update_fields=["status"])

        messages.success(
            request,
            "Your appointment was cancelled successfully."
        )

    return redirect("my_appointments")
