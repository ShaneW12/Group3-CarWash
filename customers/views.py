from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Vehicle
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import Http404
from django.core.exceptions import ValidationError
from datetime import date
from bson import ObjectId

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

def get_customer_vehicle(request, vehicle_id):
    # Reject invalid MongoDB ObjectIds
    if not ObjectId.is_valid(vehicle_id):
        raise Http404("Vehicle not found.")

    return get_object_or_404(
        Vehicle,
        pk=ObjectId(vehicle_id),
        customer=request.user
    )

@login_required(login_url="/login/")
@require_POST
def delete_vehicle(request, vehicle_id):

    vehicle = get_customer_vehicle(request, vehicle_id)

    vehicle.delete()

    messages.success(
        request,
        "Vehicle deleted successfully!"
    )

    return redirect("my_vehicles")


@login_required(login_url="/login/")
def edit_vehicle(request, vehicle_id):

    vehicle = get_customer_vehicle(request, vehicle_id)

    vehicle_years = range(
        date.today().year, 1995, -1
    )

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

    if request.method == "POST":

        year = request.POST.get(
            "vehicle_year", ""
        ).strip()

        make = request.POST.get(
            "vehicle_make", ""
        ).strip()

        model = request.POST.get(
            "vehicle_model", ""
        ).strip()

        vehicle_type = request.POST.get(
            "vehicle_type", ""
        ).strip()

        license_plate = request.POST.get(
            "license_plate", ""
        ).strip().upper()

        # Validate the updated vehicle details
        if (
            not year.isdigit()
            or not 1996 <= int(year) <= date.today().year
            or not make
            or not model
            or len(make) > 50
            or len(model) > 50
            or vehicle_type not in allowed_vehicle_types
            or len(license_plate) > 20
        ):
            messages.error(
                request,
                "Please enter valid vehicle information."
            )

            return redirect(
                "edit_vehicle",
                vehicle_id=vehicle_id
            )

        # Update the existing MongoDB document
        vehicle.year = int(year)
        vehicle.make = make
        vehicle.model = model
        vehicle.vehicle_type = vehicle_type
        vehicle.license_plate = license_plate

        try:
            vehicle.full_clean()
            vehicle.save(update_fields=[
                "year",
                "make",
                "model",
                "vehicle_type",
                "license_plate",
            ])
        except ValidationError:
            messages.error(
                request,
                "Please check your vehicle information."
            )
            return redirect(
                "edit_vehicle",
                vehicle_id=vehicle_id
            )

        messages.success(
            request,
            "Vehicle updated successfully!"
        )

        return redirect("my_vehicles")

    return render(
        request,
        "edit_vehicle.html",
        {
            "vehicle": vehicle,
            "vehicle_years": vehicle_years,
        }
    )



@login_required(login_url="/login/")
def my_vehicles(request):

    # Retrieve only this customer's vehicles
    vehicles = Vehicle.objects.filter(
        customer=request.user
    ).order_by("-year", "make", "model")

    vehicle_years = range(
        date.today().year, 1995, -1
    )

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

    if request.method == "POST":

        year = request.POST.get(
            "vehicle_year", ""
        ).strip()

        make = request.POST.get(
            "vehicle_make", ""
        ).strip()

        model = request.POST.get(
            "vehicle_model", ""
        ).strip()

        vehicle_type = request.POST.get(
            "vehicle_type", ""
        ).strip()

        license_plate = request.POST.get(
            "license_plate", ""
        ).strip().upper()

        # Validate submitted information
        if (
            not year.isdigit()
            or not 1996 <= int(year) <= date.today().year
            or not make
            or not model
            or len(make) > 50
            or len(model) > 50
            or vehicle_type not in allowed_vehicle_types
            or len(license_plate) > 20
        ):
            messages.error(
                request,
                "Please enter valid vehicle information."
            )

            return redirect("my_vehicles")

        # Save the vehicle to MongoDB
        Vehicle.objects.create(
            customer=request.user,
            year=int(year),
            make=make,
            model=model,
            vehicle_type=vehicle_type,
            license_plate=license_plate,
        )

        messages.success(
            request,
            "Your vehicle has been saved successfully!"
        )

        return redirect("my_vehicles")

    return render(
        request,
        "my_vehicles.html",
        {
            "vehicles": vehicles,
            "vehicle_years": vehicle_years,
        }
    )

