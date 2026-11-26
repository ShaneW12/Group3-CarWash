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

    appointments = Appointment.objects.all().order_by(
        "appointment_date",
        "appointment_time"
    )

    context = {
        "appointments": appointments,

        "total_appointments": appointments.count(),

        "scheduled_appointments": appointments.filter(
            status="Scheduled"
        ).count(),

        "completed_appointments": appointments.filter(
            status="Completed"
        ).count(),

        "cancelled_appointments": appointments.filter(
            status="Cancelled"
        ).count(),
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