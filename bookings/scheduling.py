
from datetime import date, datetime, time, timedelta

from django.utils import timezone

from .models import Appointment


# CleanRide business settings
OPENING_TIME = time(9, 0)
CLOSING_TIME = time(17, 0)

SLOT_INTERVAL_MINUTES = 30
SERVICE_BAY_CAPACITY = 1


def appointments_overlap(
    new_start,
    new_end,
    existing_start,
    existing_end
):
    """
    Return True if two appointments overlap.
    """
    return (
        new_start < existing_end
        and new_end > existing_start
    )


def get_existing_appointments(appointment_date):
    """
    Retrieve scheduled appointments for a date.
    Cancelled and completed appointments do not
    block availability in this initial version.
    """
    return Appointment.objects.filter(
        appointment_date=appointment_date,
        status="Scheduled"
    )


def calculate_end_time(start_time, duration_minutes):
    """
    Calculate an appointment's ending datetime.
    """
    return start_time + timedelta(
        minutes=duration_minutes
    )


def is_slot_available(
    appointment_date,
    start_time,
    duration_minutes,
    exclude_appointment_id=None
):
    """
    Check whether an appointment can be scheduled.

    Arguments:
        appointment_date: Python date
        start_time: Python time
        duration_minutes: Positive integer
        exclude_appointment_id: Optional appointment ID

    Returns:
        True when the slot is available.
    """

    if not isinstance(appointment_date, date) or isinstance(
        appointment_date, datetime
    ):
        return False

    if not isinstance(start_time, time):
        return False

    if (
        isinstance(duration_minutes, bool)
        or not isinstance(duration_minutes, int)
        or duration_minutes <= 0
    ):
        return False

    if start_time.tzinfo is not None:
        return False

    if appointment_date < timezone.localdate():
        return False

    # Enforce 30-minute start intervals
    if (
        start_time.second != 0
        or start_time.microsecond != 0
        or (
            start_time.hour * 60 + start_time.minute
        ) % SLOT_INTERVAL_MINUTES != 0
    ):
        return False

    new_start = datetime.combine(
        appointment_date,
        start_time
    )

    new_end = calculate_end_time(
        new_start,
        duration_minutes
    )

    opening = datetime.combine(
        appointment_date,
        OPENING_TIME
    )

    closing = datetime.combine(
        appointment_date,
        CLOSING_TIME
    )

    # Appointment must fit within business hours
    if new_start < opening or new_end > closing:
        return False

    # Reject starting times that have already passed
    if appointment_date == timezone.localdate():
        current_time = timezone.localtime().replace(
            tzinfo=None
        )

        if new_start <= current_time:
            return False

    existing_appointments = get_existing_appointments(
        appointment_date
    )

    overlapping_count = 0

    for appointment in existing_appointments:

        if (
            exclude_appointment_id is not None
            and str(appointment.pk)
            == str(exclude_appointment_id)
        ):
            continue

        if (
            appointment.appointment_time is None
            or not appointment.total_duration_minutes
            or appointment.total_duration_minutes <= 0
        ):
            # Fail closed when a scheduled appointment
            # has missing scheduling information.
            return False

        existing_start = datetime.combine(
            appointment_date,
            appointment.appointment_time
        )

        existing_end = calculate_end_time(
            existing_start,
            appointment.total_duration_minutes
        )

        if appointments_overlap(
            new_start,
            new_end,
            existing_start,
            existing_end
        ):
            overlapping_count += 1

            if overlapping_count >= SERVICE_BAY_CAPACITY:
                return False

    return True


def get_available_slots(
    appointment_date,
    duration_minutes,
    exclude_appointment_id=None
):
    """
    Return available start times for a given
    date and appointment duration.

    Example:
        ["09:00", "09:30", "10:00"]
    """

    if not isinstance(appointment_date, date) or isinstance(
        appointment_date, datetime
    ):
        return []

    if (
        isinstance(duration_minutes, bool)
        or not isinstance(duration_minutes, int)
        or duration_minutes <= 0
    ):
        return []

    available_slots = []

    current_slot = datetime.combine(
        appointment_date,
        OPENING_TIME
    )

    closing = datetime.combine(
        appointment_date,
        CLOSING_TIME
    )

    while current_slot + timedelta(
        minutes=duration_minutes
    ) <= closing:

        if is_slot_available(
    appointment_date,
    current_slot.time(),
    duration_minutes,
    exclude_appointment_id=exclude_appointment_id
):
            available_slots.append(
                current_slot.strftime("%H:%M")
            )

        current_slot += timedelta(
            minutes=SLOT_INTERVAL_MINUTES
        )

    return available_slots
