from bson import ObjectId

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.views.decorators.http import require_POST
from django.http import Http404

from .models import Appointment
from .forms import ManagerAppointmentForm
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET

from services.models import Service
from .scheduling import get_available_slots
from django.db.models import Q
from django.core.paginator import Paginator

def get_manager_appointment(appointment_id):

    if not ObjectId.is_valid(appointment_id):
        raise Http404("Invalid appointment ID")

    return get_object_or_404(
        Appointment,
        pk=ObjectId(appointment_id)
    )


@login_required(login_url="login")
@permission_required(
    "bookings.view_appointment",
    raise_exception=True
)
def manager_dashboard(request):

    all_appointments = Appointment.objects.all()

    appointments = all_appointments

    # Retrieve search and filter values.
    search_query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()
    selected_date = request.GET.get("date", "").strip()

    # Search customer and vehicle information.
    if search_query:

        appointments = appointments.filter(

            Q(customer_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(phone__icontains=search_query)
            | Q(vehicle_make__icontains=search_query)
            | Q(vehicle_model__icontains=search_query)
            | Q(service__icontains=search_query)

        )

    # Filter by appointment status.
    if selected_status in [
        "Scheduled",
        "Completed",
        "Cancelled",
    ]:

        appointments = appointments.filter(
            status=selected_status
        )

    # Filter by appointment date.
    if selected_date:

        try:
            parsed_date = parse_date(selected_date)
        except ValueError:
            parsed_date = None

        if parsed_date:

            appointments = appointments.filter(
                appointment_date=parsed_date
            )

        else:

            messages.error(
                request,
                "Please enter a valid appointment date."
            )

    appointments = appointments.order_by(
        "appointment_date",
        "appointment_time",
        "pk"
    )
    filtered_count = appointments.count()

# Display 10 appointments per page
    paginator = Paginator(appointments, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
    "appointments": page_obj,

    "page_obj": page_obj,

    "total_appointments":
        all_appointments.count(),

    "scheduled_appointments":
        all_appointments.filter(
            status="Scheduled"
        ).count(),

    "completed_appointments":
        all_appointments.filter(
            status="Completed"
        ).count(),

    "cancelled_appointments":
        all_appointments.filter(
            status="Cancelled"
        ).count(),

    "filtered_count": filtered_count,

    "search_query": search_query,

    "selected_status": selected_status,

    "selected_date": selected_date,
}

    return render(
        request,
        "manager_dashboard.html",
        context
    )
@login_required(login_url="login")
@permission_required(
    "bookings.change_appointment",
    raise_exception=True
)
@require_POST
def manager_cancel_appointment(request, appointment_id):

    appointment = get_manager_appointment(appointment_id)

    if appointment.status != "Scheduled":
        messages.error(
            request,
            "Only scheduled appointments can be cancelled."
        )
        return redirect("manager_dashboard")

    appointment.status = "Cancelled"
    appointment.save(update_fields=["status"])

    messages.success(
        request,
        "Appointment cancelled successfully."
    )

    return redirect("manager_dashboard")
@login_required(login_url="login")
@permission_required(
    "bookings.change_appointment",
    raise_exception=True
)
@require_POST
def manager_complete_appointment(request, appointment_id):

    appointment = get_manager_appointment(appointment_id)

    if appointment.status != "Scheduled":
        messages.error(
            request,
            "Only scheduled appointments can be completed."
        )
        return redirect("manager_dashboard")

    appointment.status = "Completed"
    appointment.save(update_fields=["status"])

    messages.success(
        request,
        "Appointment marked as completed."
    )

    return redirect("manager_dashboard")
@login_required(login_url="login")
@permission_required(
    "bookings.delete_appointment",
    raise_exception=True
)
@require_POST
def manager_delete_appointment(request, appointment_id):

    appointment = get_manager_appointment(appointment_id)

    appointment.delete()

    messages.success(
        request,
        "Appointment permanently deleted."
    )

    return redirect("manager_dashboard")
@login_required(login_url="login")
@permission_required(
    "bookings.change_appointment",
    raise_exception=True
)
@require_http_methods(["GET", "POST"])
def manager_edit_appointment(request, appointment_id):

    appointment = get_manager_appointment(
        appointment_id
    )

    if appointment.status != "Scheduled":

        messages.error(
            request,
            "Only scheduled appointments can be edited."
        )

        return redirect("manager_dashboard")

    if request.method == "POST":

        form = ManagerAppointmentForm(
            request.POST,
            instance=appointment
        )

        if form.is_valid():

            updated_appointment = form.save(
                commit=False
            )

            updated_appointment.save(
                update_fields=[
                    "customer_name",
                    "email",
                    "phone",
                    "vehicle_year",
                    "vehicle_make",
                    "vehicle_model",
                    "vehicle_type",
                    "service",
                    "total_price_cents",
                    "total_duration_minutes",
                    "appointment_date",
                    "appointment_time",
                ]
            )

            messages.success(
                request,
                "Appointment updated successfully."
            )

            return redirect("manager_dashboard")

    else:

        form = ManagerAppointmentForm(
            instance=appointment
        )

    return render(
        request,
        "manager_edit_appointment.html",
        {
            "form": form,
            "appointment": appointment,
        }
    )
@login_required(login_url="login")
@permission_required(
    "bookings.change_appointment",
    raise_exception=True
)
@require_GET
def manager_available_slots(request, appointment_id):

    appointment = get_manager_appointment(
        appointment_id
    )

    if appointment.status != "Scheduled":
        return JsonResponse(
            {"error": "This appointment cannot be edited."},
            status=400
        )

    try:
        selected_date = parse_date(
            request.GET.get("date", "")
        )
    except ValueError:
        selected_date = None

    service_codes = request.GET.getlist("service")

    if not selected_date:
        return JsonResponse(
            {"error": "Please select a valid date."},
            status=400
        )

    if not service_codes:
        return JsonResponse(
            {"error": "Please select at least one service."},
            status=400
        )

    if len(service_codes) != len(set(service_codes)):
        return JsonResponse(
            {"error": "Duplicate services are not allowed."},
            status=400
        )

    selected_services = list(
        Service.objects.filter(code__in=service_codes)
    )

    if len(selected_services) != len(service_codes):
        return JsonResponse(
            {"error": "Invalid service selection."},
            status=400
        )

    if len(", ".join(service_codes)) > 100:
        return JsonResponse(
            {"error": "Too many services selected."},
            status=400
        )

    original_codes = [
        code.strip()
        for code in appointment.service.split(",")
        if code.strip()
    ]

    services_changed = (
        set(service_codes) != set(original_codes)
    )

    # Preserve the original quoted price and duration
    # if the selected services have not changed.
    if (
        services_changed
        or appointment.total_duration_minutes <= 0
    ):

        total_price_cents = sum(
            service.price_cents
            for service in selected_services
        )

        total_duration_minutes = sum(
            service.duration_minutes
            for service in selected_services
        )

    else:

        total_price_cents = (
            appointment.total_price_cents
        )

        total_duration_minutes = (
            appointment.total_duration_minutes
        )

    available_slots = get_available_slots(
        selected_date,
        total_duration_minutes,
        exclude_appointment_id=appointment.pk
    )

    return JsonResponse({
        "date": selected_date.isoformat(),
        "total_price_cents": total_price_cents,
        "total_duration_minutes": total_duration_minutes,
        "available_slots": available_slots,
    })