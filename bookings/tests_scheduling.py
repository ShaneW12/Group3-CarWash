
from datetime import date, timedelta, time

from django.test import TestCase

from .models import Appointment
from .scheduling import (
    appointments_overlap,
    calculate_end_time,
    is_slot_available,
    get_available_slots,
)


class SchedulingTests(TestCase):

    def setUp(self):
        self.test_date = date.today() + timedelta(days=7)

        # Existing 90-minute appointment: 9:00-10:30
        self.appointment = Appointment.objects.create(
            customer_name="Test Customer",
            email="test@example.com",
            phone="5551234567",
            vehicle_year=2022,
            vehicle_make="Honda",
            vehicle_model="Civic",
            vehicle_type="sedan",
            service="interior-detailing",
            total_price_cents=2000,
            total_duration_minutes=90,
            appointment_date=self.test_date,
            appointment_time=time(9, 0),
            status="Scheduled",
        )

    def test_appointment_overlap(self):
        start = calculate_end_time(
            __import__("datetime").datetime.combine(
                self.test_date, time(9, 0)
            ),
            60
        )

        self.assertTrue(
            appointments_overlap(
                start,
                start + timedelta(minutes=60),
                start,
                start + timedelta(minutes=90)
            )
        )

    def test_overlapping_slot_is_unavailable(self):
        self.assertFalse(
            is_slot_available(
                self.test_date,
                time(9, 30),
                60
            )
        )

    def test_slot_after_appointment_is_available(self):
        self.assertTrue(
            is_slot_available(
                self.test_date,
                time(10, 30),
                60
            )
        )

    def test_appointment_cannot_exceed_closing(self):
        self.assertFalse(
            is_slot_available(
                self.test_date,
                time(16, 30),
                60
            )
        )

    def test_appointment_can_end_at_closing(self):
        self.assertTrue(
            is_slot_available(
                self.test_date,
                time(16, 0),
                60
            )
        )

    def test_cancelled_appointment_does_not_block(self):
        self.appointment.status = "Cancelled"
        self.appointment.save(update_fields=["status"])

        self.assertTrue(
            is_slot_available(
                self.test_date,
                time(9, 0),
                60
            )
        )

    def test_available_slots_exclude_booked_times(self):
        slots = get_available_slots(
            self.test_date,
            60
        )

        self.assertNotIn("09:00", slots)
        self.assertNotIn("09:30", slots)
        self.assertNotIn("10:00", slots)
        self.assertIn("10:30", slots)

    def test_invalid_duration_is_rejected(self):
        self.assertFalse(
            is_slot_available(
                self.test_date,
                time(11, 0),
                0
            )
        )

    def test_non_interval_start_is_rejected(self):
        self.assertFalse(
            is_slot_available(
                self.test_date,
                time(11, 15),
                30
            )
        )
