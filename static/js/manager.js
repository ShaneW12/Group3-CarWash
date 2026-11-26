document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById(
        "manager-edit-form"
    );

    if (!form) return;

    const dateInput = document.getElementById(
        "id_appointment_date"
    );

    const originalTimeInput = document.getElementById(
        "id_appointment_time"
    );

    const serviceInputs = form.querySelectorAll(
        'input[name="selected_services"]'
    );

    const priceDisplay = document.getElementById(
        "manager-total-price"
    );

    const durationDisplay = document.getElementById(
        "manager-total-duration"
    );

    const availabilityMessage = document.getElementById(
        "manager-availability-message"
    );

    const saveButton = document.getElementById(
        "manager-save-btn"
    );

    const slotsUrl = form.dataset.slotsUrl;

    // Preserve the appointment's original time.
    let preferredTime = originalTimeInput.value.slice(0, 5);

    let requestController = null;

    // Convert the existing Django time input
    // into a dynamic select dropdown.
    const timeSelect = document.createElement("select");

    timeSelect.id = originalTimeInput.id;
    timeSelect.name = originalTimeInput.name;
    timeSelect.className = originalTimeInput.className;
    timeSelect.required = true;

    originalTimeInput.replaceWith(timeSelect);

    function resetTimeOptions(message) {

        timeSelect.replaceChildren(
            new Option(message, "")
        );

        timeSelect.disabled = true;
        saveButton.disabled = true;
    }

    function getSelectedServices() {

        return Array.from(serviceInputs)
            .filter(input => input.checked)
            .map(input => input.value);
    }

    function formatTime(time) {

        const [hours, minutes] = time
            .split(":")
            .map(Number);

        const period = hours >= 12 ? "PM" : "AM";

        const displayHours = hours % 12 || 12;

        return `${displayHours}:${String(minutes)
            .padStart(2, "0")} ${period}`;
    }

    function clearSummary() {

        priceDisplay.textContent = "—";
        durationDisplay.textContent = "—";
    }

    async function updateAppointmentSummary() {

        // Cancel any previous unfinished API request.
        if (requestController) {
            requestController.abort();
        }

        const controller = new AbortController();
        requestController = controller;

        const selectedDate = dateInput.value;
        const selectedServices = getSelectedServices();

        clearSummary();

        if (!selectedServices.length) {

            resetTimeOptions("Select services first");

            priceDisplay.textContent = "$0.00";
            durationDisplay.textContent = "0 minutes";

            availabilityMessage.textContent =
                "Please select at least one service.";

            return;
        }

        if (!selectedDate) {

            resetTimeOptions("Select a date first");

            availabilityMessage.textContent =
                "Please select an appointment date.";

            return;
        }

        resetTimeOptions("Loading available times...");

        availabilityMessage.textContent =
            "Checking appointment availability...";

        const params = new URLSearchParams();

        params.append("date", selectedDate);

        selectedServices.forEach(service => {

            params.append("service", service);

        });

        try {

            const response = await fetch(
                `${slotsUrl}?${params.toString()}`,
                {
                    signal: controller.signal,
                    cache: "no-store"
                }
            );

            const data = await response.json();

            if (controller.signal.aborted) return;

            if (!response.ok) {

                throw new Error(
                    data.error || "Unable to load available times."
                );
            }

            // Update pricing.
            priceDisplay.textContent =
                `$${(data.total_price_cents / 100).toFixed(2)}`;

            // Update appointment duration.
            durationDisplay.textContent =
                `${data.total_duration_minutes} minutes`;

            const availableSlots = data.available_slots;

            if (!availableSlots.length) {

                resetTimeOptions("No available times");

                availabilityMessage.textContent =
                    "No available appointment times for this date.";

                return;
            }

            timeSelect.replaceChildren(
                new Option("Select an appointment time", "")
            );

            availableSlots.forEach(slot => {

                const option = new Option(
                    formatTime(slot),
                    slot
                );

                timeSelect.appendChild(option);

            });

            timeSelect.disabled = false;

            // Keep the previous time selected
            // if it is still available.
            if (availableSlots.includes(preferredTime)) {

                timeSelect.value = preferredTime;

            }

            saveButton.disabled = !timeSelect.value;

            availabilityMessage.textContent =
                `${availableSlots.length} appointment times available.`;

        } catch (error) {

            if (error.name === "AbortError") return;

            resetTimeOptions("Unable to load times");

            availabilityMessage.textContent =
                error.message;

            console.error(error);
        }
    }

    // Refresh when the manager changes the date.
    dateInput.addEventListener(
        "change",
        updateAppointmentSummary
    );

    // Refresh when services are selected or removed.
    serviceInputs.forEach(input => {

        input.addEventListener(
            "change",
            updateAppointmentSummary
        );

    });

    // Remember the manager's selected appointment time.
    timeSelect.addEventListener("change", () => {

        preferredTime = timeSelect.value;

        saveButton.disabled = !timeSelect.value;

    });

    // Load availability immediately when editing begins.
    updateAppointmentSummary();

});