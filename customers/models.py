from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django_mongodb_backend.fields import ObjectIdAutoField


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

class Vehicle(models.Model):
    id = ObjectIdAutoField(primary_key=True)

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
    )

    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=30)
    license_plate = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        db_table = "vehicles"

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


