
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="index"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("login/", views.login, name="login"),
    path("booking/", views.booking, name="booking"),

    # Appointment Management
    path(
        "my-appointments/",
        views.my_appointments,
        name="my_appointments"
    ),
    path(
        "cancel-appointment/<int:appointment_id>/",
        views.cancel_appointment,
        name="cancel_appointment"
    ),

    path("signup/", views.signup, name="signup"),
    path(
        "forgot_password/",
        views.forgot_password,
        name="forgot_password"
    ),
]
