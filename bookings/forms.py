from django import forms
from django.utils import timezone

from .models import Appointment
from .scheduling import is_slot_available, get_available_slots
from services.models import Service


class ManagerAppointmentForm(forms.ModelForm):

    selected_services = forms.MultipleChoiceField(
        label="Services",
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Appointment

        fields = [
            "customer_name",
            "email",
            "phone",
            "vehicle_year",
            "vehicle_make",
            "vehicle_model",
            "vehicle_type",
            "appointment_date",
            "appointment_time",
        ]

        widgets = {
            "appointment_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"}
            ),

            "appointment_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": "1800",
                    "min": "09:00",
                    "max": "16:30",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Retrieve the service catalog from MongoDB
        self.available_services = {
            service.code: service
            for service in Service.objects.all()
        }

        self.fields["selected_services"].choices = [
            (
                service.code,
                f"{service.name} - "
                f"${service.price_cents / 100:.2f} "
                f"({service.duration_minutes} min)"
            )
            for service in self.available_services.values()
        ]

        # Require scheduling information
        self.fields["appointment_date"].required = True
        self.fields["appointment_time"].required = True
        self.fields["vehicle_year"].required = True

        self.fields["appointment_date"].widget.attrs["min"] = (
            timezone.localdate().isoformat()
        )

        # Match the vehicle types used by the booking page
        self.fields["vehicle_type"] = forms.ChoiceField(
            choices=[
                ("sedan", "Sedan"),
                ("suv", "SUV"),
                ("truck", "Truck"),
                ("coupe", "Coupe"),
                ("hatchback", "Hatchback"),
                ("van", "Van"),
                ("wagon", "Wagon"),
                ("other", "Other"),
            ]
        )

        # Retrieve original appointment services
        self.original_service_codes = [
            code.strip()
            for code in self.instance.service.split(",")
            if code.strip()
        ]

        if not self.is_bound:
            self.initial["selected_services"] = (
                self.original_service_codes
            )

    def clean_vehicle_year(self):

        year = self.cleaned_data["vehicle_year"]

        if not 1996 <= year <= timezone.localdate().year:
            raise forms.ValidationError(
                "Please enter a valid vehicle year."
            )

        return year

    def clean(self):

        cleaned_data = super().clean()

        selected_codes = cleaned_data.get(
            "selected_services"
        )

        appointment_date = cleaned_data.get(
            "appointment_date"
        )

        appointment_time = cleaned_data.get(
            "appointment_time"
        )

        if (
            not selected_codes
            or not appointment_date
            or not appointment_time
        ):
            return cleaned_data

        # Prevent duplicate services
        if len(selected_codes) != len(set(selected_codes)):
            self.add_error(
                "selected_services",
                "Duplicate services are not allowed."
            )
            return cleaned_data

        selected_services = [
            self.available_services[code]
            for code in selected_codes
        ]

        service_string = ", ".join(selected_codes)

        if len(service_string) > 100:
            self.add_error(
                "selected_services",
                "Too many services selected."
            )
            return cleaned_data

        # Preserve the original quoted price and duration
        # unless the selected services have changed.
        services_changed = (
            set(selected_codes)
            != set(self.original_service_codes)
        )

        if (
            services_changed
            or self.instance.total_duration_minutes <= 0
        ):

            total_price_cents = sum(
                service.price_cents
                for service in selected_services
            )

            total_duration_minutes = sum(
                service.duration_minutes
                for service in selected_services
            )

        else:

            total_price_cents = (
                self.instance.total_price_cents
            )

            total_duration_minutes = (
                self.instance.total_duration_minutes
            )

        # Check availability without blocking the
        # appointment we are currently editing.
        if not is_slot_available(
            appointment_date,
            appointment_time,
            total_duration_minutes,
            exclude_appointment_id=self.instance.pk
        ):

            available_slots = get_available_slots(
                appointment_date,
                total_duration_minutes,
                exclude_appointment_id=self.instance.pk
            )

            if available_slots:
                error_message = (
                    "This appointment time is unavailable. "
                    "Available times: "
                    + ", ".join(available_slots)
                )
            else:
                error_message = (
                    "No appointment times are available "
                    "for this date and service duration."
                )

            self.add_error(
                "appointment_time",
                error_message
            )

            return cleaned_data

        cleaned_data["service_string"] = service_string

        cleaned_data["total_price_cents"] = (
            total_price_cents
        )

        cleaned_data["total_duration_minutes"] = (
            total_duration_minutes
        )

        return cleaned_data

    def save(self, commit=True):

        appointment = super().save(commit=False)

        appointment.service = self.cleaned_data[
            "service_string"
        ]

        appointment.total_price_cents = self.cleaned_data[
            "total_price_cents"
        ]

        appointment.total_duration_minutes = self.cleaned_data[
            "total_duration_minutes"
        ]

        if commit:
            appointment.save()

        return appointment