
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


class CustomerFlowTests(TestCase):
    def setUp(self):
        self.email = "visitor@example.com"
        self.password = "SafePassword923!"
        self.user = get_user_model().objects.create_user(
            username=self.email, email=self.email, password=self.password,
        )
        self.own = Appointment.objects.create(
            customer_name="Visitor", email=self.email, phone="5551231234",
            vehicle_make="Honda", vehicle_model="Civic", service="detail",
            appointment_date=date.today() + timedelta(days=2),
            appointment_time=time(11, 0),
        )
        self.other = Appointment.objects.create(
            customer_name="Other", email="other@example.com", phone="5551231234",
            vehicle_make="Honda", vehicle_model="Civic", service="detail",
            appointment_date=date.today() + timedelta(days=2),
            appointment_time=time(11, 0),
        )

    def test_login_with_email_and_view_own_appointments(self):
        response = self.client.post(reverse("login"), {
            "email": self.email, "password": self.password,
            "next": reverse("my_appointments"),
        })
        self.assertRedirects(response, reverse("my_appointments"))
        page = self.client.get(reverse("my_appointments"))
        self.assertContains(page, "Visitor")
        self.assertNotContains(page, "Other</")

    def test_cannot_cancel_other_customer_appointment(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("cancel_appointment", args=[self.other.id]))
        self.assertEqual(response.status_code, 404)
        self.other.refresh_from_db()
        self.assertEqual(self.other.status, "Scheduled")

    def test_signup_creates_account_and_logs_in(self):
        response = self.client.post(reverse("signup"), {
            "first_name": "New", "last_name": "Customer",
            "email": "newcustomer@example.com", "phone": "5551231234",
            "password": "SecurePass124!", "confirm_password": "SecurePass124!",
        })
        self.assertRedirects(response, reverse("my_appointments"))
        self.assertTrue(get_user_model().objects.filter(email="newcustomer@example.com").exists())

    def test_logged_in_booking_is_bound_to_account_email(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("booking"), {
            "first_name": "Visitor", "last_name": "Customer",
            "email": "other@example.com", "phone": "5551231234",
            "vehicle": "civic", "service": ["basic-wash"],
            "date": (date.today() + timedelta(days=3)).isoformat(),
            "time": "10:00",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.filter(email=self.email, service="basic-wash").exists())

    def test_chat_tracking_removed_from_link(self):
        response = self.client.get(reverse("booking") + "?utm_source=chatgpt.com")
        self.assertRedirects(response, reverse("booking"))
