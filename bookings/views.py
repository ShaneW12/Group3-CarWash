
from datetime import date as today_date
from datetime import date
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
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from customers.models import Vehicle

from .nhtsa import get_vehicle_makes, get_vehicle_models

from .models import Appointment
from services.models import Service

vehicle_years = range(date.today().year, 1995, -1)

@require_GET
def vehicle_makes(request):
    try:
        makes = get_vehicle_makes()

        return JsonResponse({
            "makes": [
                {
                    "id": item["MakeId"],
                    "name": item["MakeName"]
                }
                for item in makes
            ]
        })

    except Exception:
        return JsonResponse(
            {"error": "Unable to retrieve vehicle makes."},
            status=503
        )


@require_GET
def vehicle_models(request):
    make = request.GET.get("make", "").strip()
    year = request.GET.get("year", "").strip()

    if not make or not year:
        return JsonResponse(
            {"error": "Make and year are required."},
            status=400
        )

    if not year.isdigit() or not 1996 <= int(year) <= date.today().year:
        return JsonResponse(
            {"error": "Invalid vehicle year."},
            status=400
        )

    try:
        models = get_vehicle_models(make, year)

        return JsonResponse({
            "models": [
                item["Model_Name"]
                for item in models
            ]
        })

    except Exception:
        return JsonResponse(
            {"error": "Unable to retrieve vehicle models."},
            status=503
        )


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
     available_services = list(Service.objects.all())

    # Only retrieve vehicles belonging to this customer
     customer_vehicles = (
        list(Vehicle.objects.filter(customer=request.user))
        if request.user.is_authenticated
        else []
    )

     context = {
        "vehicle_years": vehicle_years,
        "available_services": available_services,
        "customer_vehicles": customer_vehicles,
    }
     
     if request.method == "POST":

        
        # CUSTOMER INFORMATION
        if request.user.is_authenticated:
            first_name = request.user.first_name.strip()
            last_name = request.user.last_name.strip()
            email = request.user.email.strip().lower()
            phone = request.user.phone.strip()
        else:
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            email = request.POST.get("email", "").strip().lower()
            phone = request.POST.get("phone", "").strip()

        # VEHICLE INFORMATION
        if request.user.is_authenticated:

            saved_vehicle_id = request.POST.get(
                "saved_vehicle", ""
            ).strip()

            # Only allow vehicles owned by this customer
            selected_vehicle = next(
                (
                    vehicle for vehicle in customer_vehicles
                    if str(vehicle.pk) == saved_vehicle_id
                ),
                None
            )

            if selected_vehicle is None:
                messages.error(
                    request,
                    "Please select one of your saved vehicles."
                )
                return render(request, "booking.html", context)

            vehicle_year = str(selected_vehicle.year)
            vehicle_make = selected_vehicle.make
            vehicle_model = selected_vehicle.model
            vehicle_type = selected_vehicle.vehicle_type

        else:
            vehicle_year = request.POST.get(
                "vehicle_year", ""
            ).strip()

            vehicle_make = request.POST.get(
                "vehicle_make", ""
            ).strip()

            vehicle_model = request.POST.get(
                "vehicle_model", ""
            ).strip()

            vehicle_type = request.POST.get(
                "vehicle_type", ""
            ).strip()




        allowed_services = {
            service.code for service in available_services
        }
        allowed_vehicle_types = {
            "sedan",
            "suv",
            "truck",
            "coupe",
            "hatchback",
            "van",
            "wagon",
            "other",
        }

        if (
            not first_name
        or not last_name
        or not email
        or not phone
        or not vehicle_year.isdigit()
        or not 1996 <= int(vehicle_year) <= date.today().year
        or not vehicle_make
        or not vehicle_model
        or vehicle_type not in allowed_vehicle_types
        or not selected_services
        or any(s not in allowed_services for s in selected_services)
        or not appointment_date
        or not appointment_time
        ):
            messages.error(
                request,
                "Please complete all booking fields correctly."
            )
            return render(request, "booking.html",context)

        if appointment_date < today_date.today():
            messages.error(
                request,
                "Please choose today or a future appointment date."
            )
            return render(request, "booking.html",context)
        
        
        # Retrieve selected services from MongoDB
        selected_service_objects = [
            service
            for service in available_services
            if service.code in selected_services
        ]

        # Calculate total price
        total_price_cents = sum(
            service.price_cents
            for service in selected_service_objects
        )

        # Calculate total duration
        total_duration_minutes = sum(
            service.duration_minutes
            for service in selected_service_objects
        )

        # Create appointment
        
        appointment = Appointment(
            customer_name=f"{first_name} {last_name}",
            email=email,
            phone=phone,
            vehicle_year=int(vehicle_year),
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            vehicle_type=vehicle_type,
            service=", ".join(selected_services),
            total_price_cents=total_price_cents,
            total_duration_minutes=total_duration_minutes,
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
            return render(request, "booking.html", context)

        messages.success(
            request,
            "Your appointment was created successfully!"
        )
        return redirect("booking")

     return render(request, "booking.html", context)


def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if (
            not first_name
            or not last_name
            or not email
            or not phone
            or not password
            or password != confirm
        ):
            messages.error(
                request,
                "Please complete all fields and make sure passwords match."
            )
            return render(request, "signup.html")

        User = get_user_model()

        if User.objects.filter(email__iexact=email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return render(request, "signup.html")

        try:
            validate_password(password)

            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                )

        except ValidationError as exc:
            messages.error(
                request,
                " ".join(exc.messages)
            )
            return render(request, "signup.html")

        except IntegrityError:
            messages.error(
                request,
                "That account already exists."
            )
            return render(request, "signup.html")

        auth_login(request, user)

        messages.success(
            request,
            "Account created successfully."
        )
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
