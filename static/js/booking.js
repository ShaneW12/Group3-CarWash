
/*
 * CleanRide Booking JavaScript
 *
 * Features:
 * 1. NHTSA Vehicle Selection
 * 2. Dynamic Service Pricing and Duration
 * 3. Smart Appointment Availability
 * 4. Gemini AI Appointment Recommendations
 */


/* ==========================================
   1. NHTSA VEHICLE SELECTION
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    const yearSelect = document.getElementById("vehicle-year");
    const makeSelect = document.getElementById("vehicle-make");
    const modelSelect = document.getElementById("vehicle-model");

    // Logged-in users select saved vehicles instead.
    if (!yearSelect || !makeSelect || !modelSelect) {
        return;
    }

    const makesUrl = makeSelect.dataset.url;
    const modelsUrl = modelSelect.dataset.url;

    let makesRequest = 0;
    let modelsRequest = 0;

    function resetDropdown(dropdown, placeholder) {
        dropdown.replaceChildren(
            new Option(placeholder, "")
        );
        dropdown.disabled = true;
    }

    // Load manufacturers when year changes
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

    // Load models when manufacturer changes
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

    // Validate guest vehicle selection
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


/* ==========================================
   2. DYNAMIC SERVICE PRICING AND DURATION
========================================== */

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

    if (
        !summaryServices ||
        !summaryDuration ||
        !summaryPrice
    ) {
        return;
    }

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

        summaryServices.textContent =
            selectedServiceNames.length > 0
                ? selectedServiceNames.join(", ")
                : "No services selected";

        summaryDuration.textContent =
            totalDurationMinutes + " minutes";

        summaryPrice.textContent =
            "$" + (totalPriceCents / 100).toFixed(2);
    }

    serviceCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener(
            "change",
            updateAppointmentSummary
        );
    });

    updateAppointmentSummary();

});


/* ==========================================
   3. APPOINTMENT AVAILABILITY
   4. GEMINI AI RECOMMENDATIONS
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    const dateInput = document.getElementById("date");
    const timeSelect = document.getElementById("time");

    const serviceCheckboxes = document.querySelectorAll(
        ".service-checkbox"
    );

    const availabilityMessage = document.getElementById(
        "availability-message"
    );

    // AI elements
    const aiSection = document.getElementById(
        "ai-recommendation-section"
    );

    const aiButton = document.getElementById(
        "ai-recommend-button"
    );

    const aiResult = document.getElementById(
        "ai-recommendation-result"
    );

    const aiError = document.getElementById(
        "ai-recommendation-error"
    );

    const recommendedTime = document.getElementById(
        "ai-recommended-time"
    );

    const recommendationReason = document.getElementById(
        "ai-recommendation-reason"
    );

    const useTimeButton = document.getElementById(
        "ai-use-time-button"
    );

    if (!dateInput || !timeSelect) {
        return;
    }

    let availabilityRequestVersion = 0;
    let aiRequestVersion = 0;

    let aiController = null;
    let currentRecommendation = null;

    // Keep AI optional if its HTML is not present.
    const aiEnabled = Boolean(
        aiSection &&
        aiButton &&
        aiResult &&
        aiError &&
        recommendedTime &&
        recommendationReason &&
        useTimeButton &&
        aiSection.dataset.url
    );


    /* --------------------------------------
       Helper functions
    -------------------------------------- */

    function getSelectedServices() {
        return Array.from(serviceCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
    }

    function setAvailabilityMessage(message) {
        if (availabilityMessage) {
            availabilityMessage.textContent = message;
        }
    }

    function resetTimes(message) {
        timeSelect.replaceChildren(
            new Option(message, "")
        );

        timeSelect.disabled = true;
    }

    function formatTime(time) {

        const [hour, minute] = time.split(":")
            .map(Number);

        return new Date(
            2000, 0, 1, hour, minute
        ).toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit"
        });
    }

    function isTimeInDropdown(time) {
        return !timeSelect.disabled &&
            Array.from(timeSelect.options).some(
                option => option.value === time
            );
    }

    function setAIButtonReady() {
        if (!aiEnabled) {
            return;
        }

        aiButton.disabled =
            timeSelect.disabled ||
            !dateInput.value ||
            getSelectedServices().length === 0;
    }

    function resetAIRecommendation() {

        // Invalidate any outstanding AI response.
        aiRequestVersion++;

        if (aiController) {
            aiController.abort();
            aiController = null;
        }

        currentRecommendation = null;

        if (!aiEnabled) {
            return;
        }

        aiResult.hidden = true;
        aiError.hidden = true;

        recommendedTime.textContent = "";
        recommendationReason.textContent = "";

        aiButton.textContent = "✨ Get AI Recommendation";

        setAIButtonReady();
    }

    function showAIError(message) {
        if (!aiEnabled) {
            return;
        }

        aiResult.hidden = true;
        aiError.textContent = message;
        aiError.hidden = false;
    }


    /* --------------------------------------
       Retrieve available appointment times
    -------------------------------------- */

    async function updateAvailableTimes() {

        const version = ++availabilityRequestVersion;

        // Clear recommendations whenever inputs change.
        resetAIRecommendation();

        const selectedServices = getSelectedServices();
        const selectedDate = dateInput.value;

        if (!selectedDate || selectedServices.length === 0) {

            resetTimes("Select services and a date first");

            setAvailabilityMessage(
                "Choose your services and date to see available times."
            );

            setAIButtonReady();
            return;
        }

        resetTimes("Checking availability...");

        setAvailabilityMessage(
            "Finding available appointments..."
        );

        setAIButtonReady();

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

            // Ignore outdated responses.
            if (version !== availabilityRequestVersion) {
                return;
            }

            if (!response.ok) {
                throw new Error(
                    data.error || "Unable to check availability."
                );
            }

            resetTimes("Select an available time");

            if (
                !Array.isArray(data.available_slots) ||
                data.available_slots.length === 0
            ) {
                resetTimes("No available appointments");

                setAvailabilityMessage(
                    "No appointments are available for this date. " +
                    "Please choose another date."
                );

                setAIButtonReady();
                return;
            }

            data.available_slots.forEach(slot => {

                timeSelect.add(
                    new Option(formatTime(slot), slot)
                );
            });

            timeSelect.disabled = false;

            setAvailabilityMessage(
                `${data.available_slots.length} available ` +
                "starting times found."
            );

            setAIButtonReady();

        } catch (error) {

            if (version !== availabilityRequestVersion) {
                return;
            }

            console.error(error);

            resetTimes("Unable to load appointments");

            setAvailabilityMessage(
                "Unable to check availability. Please try again."
            );

            setAIButtonReady();
        }
    }


    /* --------------------------------------
       Request a Gemini AI recommendation
    -------------------------------------- */

    async function getAIRecommendation() {

        if (!aiEnabled) {
            return;
        }

        const selectedDate = dateInput.value;
        const selectedServices = getSelectedServices();

        resetAIRecommendation();

        if (
            !selectedDate ||
            selectedServices.length === 0
        ) {
            showAIError(
                "Please select a date and at least one service."
            );
            return;
        }

        if (timeSelect.disabled) {
            showAIError(
                "Please wait for available appointment times to load."
            );
            return;
        }

        const params = new URLSearchParams();

        params.append("date", selectedDate);

        selectedServices.forEach(code => {
            params.append("service", code);
        });

        const version = ++aiRequestVersion;
        const controller = new AbortController();

        aiController = controller;

        aiButton.disabled = true;
        aiButton.textContent = "Getting recommendation...";

        try {
            const response = await fetch(
                `${aiSection.dataset.url}?${params.toString()}`,
                {
                    method: "GET",
                    signal: controller.signal
                }
            );

            const data = await response.json();

            // Ignore requests for outdated selections.
            if (version !== aiRequestVersion) {
                return;
            }

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    "Unable to get an AI recommendation."
                );
            }

            if (!data.recommended_time) {
                showAIError(
                    data.reason ||
                    "No appointment times are available."
                );
                return;
            }

            // Never accept a time missing from the
            // current Python-generated dropdown.
            if (!isTimeInDropdown(data.recommended_time)) {
                throw new Error(
                    "The recommended time is no longer " +
                    "available. Please refresh your times."
                );
            }

            currentRecommendation = data.recommended_time;

            recommendedTime.textContent = formatTime(
                data.recommended_time
            );

            recommendationReason.textContent =
                data.reason || "Recommended available time.";

            aiError.hidden = true;
            aiResult.hidden = false;

        } catch (error) {

            if (version !== aiRequestVersion) {
                return;
            }

            if (error.name !== "AbortError") {
                console.error("Gemini AI error:", error);

                showAIError(
                    error.message ||
                    "AI recommendations are temporarily unavailable."
                );
            }

        } finally {

            if (version === aiRequestVersion) {

                aiController = null;

                aiButton.textContent =
                    "✨ Get AI Recommendation";

                setAIButtonReady();
            }
        }
    }


    /* --------------------------------------
       Use the recommended appointment time
    -------------------------------------- */

    function useRecommendedTime() {

        if (!currentRecommendation) {
            return;
        }

        if (!isTimeInDropdown(currentRecommendation)) {

            resetAIRecommendation();

            showAIError(
                "This appointment time is no longer available."
            );

            return;
        }

        // Select the actual option in the booking form.
        timeSelect.value = currentRecommendation;

        // Notify other JavaScript listeners.
        timeSelect.dispatchEvent(
            new Event("change", {
                bubbles: true
            })
        );

        // Highlight selection briefly through focus.
        timeSelect.focus();

        // The customer must still submit the booking form.
    }


    /* --------------------------------------
       Event listeners
    -------------------------------------- */

    // Date changes trigger Python availability checks.
    dateInput.addEventListener(
        "change",
        updateAvailableTimes
    );

    // Service changes update availability.
    serviceCheckboxes.forEach(checkbox => {
        checkbox.addEventListener(
            "change",
            updateAvailableTimes
        );
    });

    // AI recommendation button
    if (aiEnabled) {

        aiButton.addEventListener(
            "click",
            getAIRecommendation
        );

        useTimeButton.addEventListener(
            "click",
            useRecommendedTime
        );

        aiResult.hidden = true;
        aiError.hidden = true;

        aiButton.disabled = true;
    }

    // Initialize availability on page load.
    updateAvailableTimes();

});
