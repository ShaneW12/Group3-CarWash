

document.addEventListener("DOMContentLoaded", function () {

    const yearSelect = document.getElementById("vehicle-year");
    const makeSelect = document.getElementById("vehicle-make");
    const modelSelect = document.getElementById("vehicle-model");

    // Only initialize NHTSA dropdowns if they exist.
    // Logged-in users use saved vehicles instead.
    if (!yearSelect || !makeSelect || !modelSelect) {
        return;
    }

    const makesUrl = makeSelect.dataset.url;
    const modelsUrl = modelSelect.dataset.url;

    let makesRequest = 0;
    let modelsRequest = 0;

    // Reset a dropdown
    function resetDropdown(dropdown, placeholder) {
        dropdown.innerHTML = "";
        dropdown.add(new Option(placeholder, ""));
        dropdown.disabled = true;
    }

    // Load manufacturers when a year is selected
    yearSelect.addEventListener("change", async function () {

        const requestId = ++makesRequest;
        modelsRequest++;

        resetDropdown(makeSelect, "Select manufacturer");
        resetDropdown(modelSelect, "Select model");

        if (!yearSelect.value) {
            return;
        }

        resetDropdown(makeSelect, "Loading manufacturers...");

        try {
            const response = await fetch(makesUrl);

            if (!response.ok) {
                throw new Error("Unable to load manufacturers");
            }

            const data = await response.json();

            if (requestId !== makesRequest) {
                return;
            }

            resetDropdown(makeSelect, "Select manufacturer");

            data.makes.sort((a, b) =>
                a.name.localeCompare(b.name)
            );

            data.makes.forEach(make => {
                makeSelect.add(
                    new Option(make.name, make.name)
                );
            });

            makeSelect.disabled = false;

        } catch (error) {

            if (requestId !== makesRequest) {
                return;
            }

            resetDropdown(
                makeSelect,
                "Unable to load manufacturers"
            );

            console.error(error);
        }
    });

    // Load models when a manufacturer is selected
    makeSelect.addEventListener("change", async function () {

        const requestId = ++modelsRequest;

        resetDropdown(modelSelect, "Select model");

        const year = yearSelect.value;
        const make = makeSelect.value;

        if (!year || !make) {
            return;
        }

        resetDropdown(modelSelect, "Loading models...");

        try {
            const params = new URLSearchParams({
                make: make,
                year: year
            });

            const response = await fetch(
                `${modelsUrl}?${params.toString()}`
            );

            if (!response.ok) {
                throw new Error("Unable to load models");
            }

            const data = await response.json();

            if (requestId !== modelsRequest) {
                return;
            }

            resetDropdown(modelSelect, "Select model");

            const models = [...new Set(data.models)].sort();

            if (models.length === 0) {
                resetDropdown(modelSelect, "No models found");
                return;
            }

            models.forEach(model => {
                modelSelect.add(
                    new Option(model, model)
                );
            });

            modelSelect.disabled = false;

        } catch (error) {

            if (requestId !== modelsRequest) {
                return;
            }

            resetDropdown(
                modelSelect,
                "Unable to load models"
            );

            console.error(error);
        }
    });

    // Validate guest vehicle selection before submission
    yearSelect.closest("form").addEventListener(
        "submit",
        function (event) {

            if (
                !yearSelect.value ||
                !makeSelect.value ||
                !modelSelect.value
            ) {
                event.preventDefault();

                alert(
                    "Please select your vehicle year, make, and model."
                );
            }
        }
    );

});


/*
 *  Dynamic Service Pricing
 * Updates the booking summary when services change.
 */

document.addEventListener("DOMContentLoaded", function () {

    const serviceCheckboxes = document.querySelectorAll(
        ".service-checkbox"
    );

    const summaryServices = document.getElementById(
        "summary-services"
    );

    const summaryDuration = document.getElementById(
        "summary-duration"
    );

    const summaryPrice = document.getElementById(
        "summary-price"
    );

    function updateAppointmentSummary() {

        let totalPriceCents = 0;
        let totalDurationMinutes = 0;
        let selectedServiceNames = [];

        serviceCheckboxes.forEach(function (checkbox) {

            if (checkbox.checked) {

                const price = Number(
                    checkbox.dataset.price
                );

                const duration = Number(
                    checkbox.dataset.duration
                );

                const serviceName = checkbox
                    .closest(".service-option")
                    .querySelector("strong")
                    .textContent.trim();

                totalPriceCents += price;
                totalDurationMinutes += duration;

                selectedServiceNames.push(serviceName);
            }
        });

        // Update selected service names
        summaryServices.textContent =
            selectedServiceNames.length > 0
                ? selectedServiceNames.join(", ")
                : "No services selected";

        // Update total duration
        summaryDuration.textContent =
            totalDurationMinutes + " minutes";

        // Convert cents into dollars
        summaryPrice.textContent =
            "$" + (totalPriceCents / 100).toFixed(2);
    }

    // Listen for service checkbox changes
    serviceCheckboxes.forEach(function (checkbox) {

        checkbox.addEventListener(
            "change",
            updateAppointmentSummary
        );
    });

    // Initialize the summary when the page loads
    updateAppointmentSummary();

});


/*
 * CleanRide Smart Appointment Availability
 */

document.addEventListener("DOMContentLoaded", function () {

    const dateInput = document.getElementById("date");
    const timeSelect = document.getElementById("time");

    const serviceCheckboxes = document.querySelectorAll(
        ".service-checkbox"
    );

    const availabilityMessage = document.getElementById(
        "availability-message"
    );

    if (!dateInput || !timeSelect) {
        return;
    }

    let requestVersion = 0;

    function resetTimes(message) {
        timeSelect.replaceChildren(
            new Option(message, "")
        );

        timeSelect.disabled = true;
    }

    async function updateAvailableTimes() {

        // Invalidate older responses
        const version = ++requestVersion;

        const selectedServices = Array.from(
            serviceCheckboxes
        )
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

        const selectedDate = dateInput.value;

        if (!selectedDate || selectedServices.length === 0) {
            resetTimes("Select services and a date first");

            availabilityMessage.textContent =
                "Choose your services and date to see available times.";

            return;
        }

        resetTimes("Checking availability...");

        availabilityMessage.textContent =
            "Finding available appointments...";

        const params = new URLSearchParams();

        params.append("date", selectedDate);

        selectedServices.forEach(code => {
            params.append("service", code);
        });

        try {
            const response = await fetch(
                `${timeSelect.dataset.url}?${params.toString()}`
            );

            const data = await response.json();

            // Ignore responses for outdated selections
            if (version !== requestVersion) {
                return;
            }

            if (!response.ok) {
                throw new Error(
                    data.error || "Unable to check availability."
                );
            }

            resetTimes("Select an available time");

            if (data.available_slots.length === 0) {

                resetTimes("No available appointments");

                availabilityMessage.textContent =
                    "No appointments are available for this date. " +
                    "Please choose another date.";

                return;
            }

            data.available_slots.forEach(slot => {

                const [hour, minute] = slot.split(":")
                    .map(Number);

                const formattedTime = new Date(
                    2000, 0, 1, hour, minute
                ).toLocaleTimeString("en-US", {
                    hour: "numeric",
                    minute: "2-digit"
                });

                timeSelect.add(
                    new Option(formattedTime, slot)
                );
            });

            timeSelect.disabled = false;

            availabilityMessage.textContent =
                `${data.available_slots.length} available ` +
                `starting times found.`;

        } catch (error) {

            if (version !== requestVersion) {
                return;
            }

            console.error(error);

            resetTimes("Unable to load appointments");

            availabilityMessage.textContent =
                "Unable to check availability. Please try again.";
        }
    }

    // Refresh availability when the date changes
    dateInput.addEventListener(
        "change",
        updateAvailableTimes
    );

    // Refresh availability when services change
    serviceCheckboxes.forEach(checkbox => {
        checkbox.addEventListener(
            "change",
            updateAvailableTimes
        );
    });

    // Check availability on page load
    updateAvailableTimes();

});


