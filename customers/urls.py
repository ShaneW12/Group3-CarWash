from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("my-vehicles/", views.my_vehicles, name="my_vehicles"),
]