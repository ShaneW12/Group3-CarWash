
from datetime import date, timedelta, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Appointment


class AppointmentTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testcustomer",
            email="test@example.com",
            password="TestPassword123!"
        )

        self.appointment = Appointment.objects.create(
            customer_name="Test Customer",
            email="test@example.com",
            phone="5551234567",
            vehicle_make="Honda",
            vehicle_model="Civic",
            service="basic-wash",
            appointment_date=date.today() + timedelta(days=3),
            appointment_time=time(10, 0),
            status="Scheduled"
        )

    def test_create_appointment(self):
        response = self.client.post(
            reverse("booking"),
            {
                "first_name": "New",
                "last_name": "Customer",
                "email": "new@example.com",
                "phone": "5551234567",
                "vehicle": "civic",
                "service": ["basic-wash"],
                "date": (date.today() + timedelta(days=4)).isoformat(),
                "time": "10:00",
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Appointment.objects.filter(
                email="new@example.com"
            ).exists()
        )

    def test_customer_can_view_own_appointments(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_appointments"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Customer")

    def test_customer_can_cancel_appointment(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "cancel_appointment",
                args=[self.appointment.id]
            )
        )

        self.assertEqual(response.status_code, 302)

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "Cancelled")
