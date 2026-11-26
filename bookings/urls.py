
from django.urls import path
from . import views
from . import manager_views

urlpatterns = [
    path("", views.home, name="index"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("booking/", views.booking, name="booking"),

    # Appointment Management
    path(
        "my-appointments/",
        views.my_appointments,
        name="my_appointments"
    ),
    path(
    'cancel-appointment/<str:appointment_id>/',
    views.cancel_appointment,
    name='cancel_appointment'
    ),

    path("signup/", views.signup, name="signup"),
    path(
        "forgot_password/",
        views.forgot_password,
        name="forgot_password"
    ),
    path(
    "api/vehicle/makes/",
    views.vehicle_makes,
    name="vehicle_makes"
),

path(
    "api/vehicle/models/",
    views.vehicle_models,
    name="vehicle_models"
),
path(
    "api/booking/available-slots/",
    views.available_booking_slots,
    name="available_booking_slots"
),
path(
    "api/ai-recommendation/",
    views.ai_booking_recommendation,
    name="ai_booking_recommendation"
),
path(
    "manager/",
    manager_views.manager_dashboard,
    name="manager_dashboard"
),
# Manager Appointment Management

path(
    "manager/appointments/<str:appointment_id>/cancel/",
    manager_views.manager_cancel_appointment,
    name="manager_cancel_appointment"
),

path(
    "manager/appointments/<str:appointment_id>/complete/",
    manager_views.manager_complete_appointment,
    name="manager_complete_appointment"
),

path(
    "manager/appointments/<str:appointment_id>/delete/",
    manager_views.manager_delete_appointment,
    name="manager_delete_appointment"
),
path(
    "manager/appointments/<str:appointment_id>/edit/",
    manager_views.manager_edit_appointment,
    name="manager_edit_appointment"
),
]
