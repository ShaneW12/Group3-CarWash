from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("my-vehicles/", views.my_vehicles, name="my_vehicles"),
    path("my-vehicles/<str:vehicle_id>/edit/", views.edit_vehicle, name="edit_vehicle"),
    path("my-vehicles/<str:vehicle_id>/delete/", views.delete_vehicle, name="delete_vehicle"),

]