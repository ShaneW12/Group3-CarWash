
from datetime import date, timedelta, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from bookings.models import Appointment
from customers.models import Vehicle
from services.models import Service


class AppointmentTests(TestCase):

    def setUp(self):
        # Create a test customer
        self.user = get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Customer",
            phone="5551234567",
        )

        # Create services in the test database
        self.standard_wash = Service.objects.create(
            code="standard-wash",
            name="Standard Car Wash",
            price_cents=2500,
            duration_minutes=30,
        )

        self.vacuum = Service.objects.create(
            code="vacuum",
            name="Vacuum Service",
            price_cents=1000,
            duration_minutes=15,
        )

        # Create a saved vehicle for the customer
        self.vehicle = Vehicle.objects.create(
            customer=self.user,
            year=2022,
            make="Honda",
            model="Civic",
            vehicle_type="sedan",
            license_plate="ABC1234",
        )

        # Create an existing appointment
        self.appointment = Appointment.objects.create(
            customer_name="Test Customer",
            email="test@example.com",
            phone="5551234567",
            vehicle_year=2022,
            vehicle_make="Honda",
            vehicle_model="Civic",
            vehicle_type="sedan",
            service="standard-wash",
            total_price_cents=2500,
            total_duration_minutes=30,
            appointment_date=date.today() + timedelta(days=3),
            appointment_time=time(10, 0),
            status="Scheduled",
        )

    def test_guest_can_create_appointment(self):
        response = self.client.post(
            reverse("booking"),
            {
                "first_name": "New",
                "last_name": "Customer",
                "email": "new@example.com",
                "phone": "5551234567",
                "vehicle_year": "2022",
                "vehicle_make": "Honda",
                "vehicle_model": "Civic",
                "vehicle_type": "sedan",
                "service": ["standard-wash"],
                "date": (
                    date.today() + timedelta(days=4)
                ).isoformat(),
                "time": "10:00",
            }
        )

        self.assertRedirects(
            response,
            reverse("booking")
        )

        self.assertTrue(
            Appointment.objects.filter(
                email="new@example.com"
            ).exists()
        )

    def test_logged_in_user_can_book_saved_vehicle(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("booking"),
            {
                "saved_vehicle": str(self.vehicle.pk),
                "service": ["standard-wash"],
                "date": (
                    date.today() + timedelta(days=5)
                ).isoformat(),
                "time": "10:00",
            }
        )

        self.assertRedirects(
            response,
            reverse("booking")
        )

        appointment = Appointment.objects.filter(
            email=self.user.email,
            appointment_date=date.today() + timedelta(days=5),
        ).first()

        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.vehicle_make, "Honda")
        self.assertEqual(appointment.vehicle_model, "Civic")
        self.assertEqual(appointment.vehicle_year, 2022)
        self.assertEqual(appointment.phone, self.user.phone)

    def test_multiple_services_calculate_correct_totals(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("booking"),
            {
                "saved_vehicle": str(self.vehicle.pk),
                "service": ["standard-wash", "vacuum"],
                "date": (
                    date.today() + timedelta(days=6)
                ).isoformat(),
                "time": "11:00",
            }
        )

        self.assertRedirects(
            response,
            reverse("booking")
        )

        appointment = Appointment.objects.get(
            email=self.user.email,
            appointment_date=date.today() + timedelta(days=6),
        )

        self.assertEqual(
            appointment.total_price_cents,
            3500
        )

        self.assertEqual(
            appointment.total_duration_minutes,
            45
        )

    def test_booking_page_loads_database_services(self):
        response = self.client.get(reverse("booking"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Standard Car Wash")
        self.assertContains(response, "Vacuum Service")
        self.assertContains(response, 'value="standard-wash"')

    def test_invalid_service_is_rejected(self):
        response = self.client.post(
            reverse("booking"),
            {
                "first_name": "New",
                "last_name": "Customer",
                "email": "invalid@example.com",
                "phone": "5551234567",
                "vehicle_year": "2022",
                "vehicle_make": "Honda",
                "vehicle_model": "Civic",
                "vehicle_type": "sedan",
                "service": ["fake-service"],
                "date": (
                    date.today() + timedelta(days=4)
                ).isoformat(),
                "time": "10:00",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Appointment.objects.filter(
                email="invalid@example.com"
            ).exists()
        )

    def test_customer_can_view_own_appointments(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("my_appointments")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Customer")

    def test_customer_can_cancel_appointment(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "cancel_appointment",
                args=[str(self.appointment.pk)]
            )
        )

        self.assertRedirects(
            response,
            reverse("my_appointments")
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            "Cancelled"
        )


class CustomerFlowTests(TestCase):

    def setUp(self):
        self.email = "visitor@example.com"
        self.password = "SafePassword923!"

        self.user = get_user_model().objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
            first_name="Visitor",
            last_name="Customer",
            phone="5551231234",
        )

        self.own = Appointment.objects.create(
            customer_name="Visitor Customer",
            email=self.email,
            phone="5551231234",
            vehicle_year=2022,
            vehicle_make="Honda",
            vehicle_model="Civic",
            vehicle_type="sedan",
            service="standard-wash",
            appointment_date=date.today() + timedelta(days=2),
            appointment_time=time(11, 0),
        )

        self.other = Appointment.objects.create(
            customer_name="Other Customer",
            email="other@example.com",
            phone="5551231234",
            vehicle_year=2022,
            vehicle_make="Toyota",
            vehicle_model="Camry",
            vehicle_type="sedan",
            service="standard-wash",
            appointment_date=date.today() + timedelta(days=2),
            appointment_time=time(11, 0),
        )

    def test_login_with_email(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": self.email,
                "password": self.password,
                "next": reverse("my_appointments"),
            }
        )

        self.assertRedirects(
            response,
            reverse("my_appointments")
        )

        self.assertTrue(
            "_auth_user_id" in self.client.session
        )

    def test_customer_sees_only_own_appointments(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("my_appointments")
        )

        self.assertContains(
            response,
            "Visitor Customer"
        )

        self.assertNotContains(
            response,
            "Other Customer"
        )

    def test_cannot_cancel_other_customer_appointment(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "cancel_appointment",
                args=[str(self.other.pk)]
            )
        )

        self.assertEqual(response.status_code, 404)

        self.other.refresh_from_db()

        self.assertEqual(
            self.other.status,
            "Scheduled"
        )

    def test_signup_creates_account_and_saves_phone(self):
        response = self.client.post(
            reverse("signup"),
            {
                "first_name": "New",
                "last_name": "Customer",
                "email": "newcustomer@example.com",
                "phone": "5551231234",
                "password": "SecurePass124!",
                "confirm_password": "SecurePass124!",
            }
        )

        self.assertRedirects(
            response,
            reverse("my_appointments")
        )

        user = get_user_model().objects.get(
            email="newcustomer@example.com"
        )

        self.assertEqual(user.phone, "5551231234")

    def test_booking_requires_saved_vehicle_for_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("booking"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "You haven't saved any vehicles yet"
        )

class VehicleManagementTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="TestPassword123!",
            first_name="Vehicle",
            last_name="Owner",
            phone="5551234567",
        )

        self.other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="TestPassword123!",
        )

        self.vehicle = Vehicle.objects.create(
            customer=self.user,
            year=2022,
            make="Honda",
            model="Civic",
            vehicle_type="sedan",
            license_plate="ABC1234",
        )

    def test_customer_can_view_saved_vehicles(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_vehicles"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Honda")
        self.assertContains(response, "Civic")

    def test_customer_can_add_vehicle(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("my_vehicles"),
            {
                "vehicle_year": "2023",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_type": "sedan",
                "license_plate": "XYZ1234",
            }
        )

        self.assertRedirects(
            response,
            reverse("my_vehicles")
        )

        self.assertTrue(
            Vehicle.objects.filter(
                customer=self.user,
                make="Toyota",
                model="Camry",
            ).exists()
        )

    def test_customer_can_edit_vehicle(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "edit_vehicle",
                args=[str(self.vehicle.pk)]
            ),
            {
                "vehicle_year": "2023",
                "vehicle_make": "Honda",
                "vehicle_model": "Accord",
                "vehicle_type": "sedan",
                "license_plate": "UPDATED123",
            }
        )

        self.assertRedirects(
            response,
            reverse("my_vehicles")
        )

        self.vehicle.refresh_from_db()

        self.assertEqual(self.vehicle.model, "Accord")
        self.assertEqual(self.vehicle.year, 2023)

    def test_customer_can_delete_vehicle(self):
        self.client.force_login(self.user)

        vehicle_id = self.vehicle.pk

        response = self.client.post(
            reverse(
                "delete_vehicle",
                args=[str(vehicle_id)]
            )
        )

        self.assertRedirects(
            response,
            reverse("my_vehicles")
        )

        self.assertFalse(
            Vehicle.objects.filter(pk=vehicle_id).exists()
        )

    def test_cannot_edit_another_users_vehicle(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                "edit_vehicle",
                args=[str(self.vehicle.pk)]
            ),
            {
                "vehicle_year": "2024",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_type": "sedan",
            }
        )

        self.assertEqual(response.status_code, 404)

        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.make, "Honda")

    def test_cannot_delete_another_users_vehicle(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                "delete_vehicle",
                args=[str(self.vehicle.pk)]
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Vehicle.objects.filter(
                pk=self.vehicle.pk
            ).exists()
        )

