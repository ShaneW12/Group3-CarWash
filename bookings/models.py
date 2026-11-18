
from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    vehicle_year = models.PositiveIntegerField(null=True, blank=True)
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=30, default="", blank=True)

    service = models.CharField(max_length=100)

    # NEW: Dynamic pricing and duration
    total_price_cents = models.PositiveIntegerField(default=0)
    total_duration_minutes = models.PositiveIntegerField(default=0)

    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.TimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Scheduled'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.service}"

    @property
    def total_price_dollars(self):
        return self.total_price_cents / 100
