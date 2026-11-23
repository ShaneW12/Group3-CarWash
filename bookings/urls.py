
from django.urls import path
from . import views

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
]
