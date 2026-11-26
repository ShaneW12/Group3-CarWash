document.addEventListener("DOMContentLoaded", () => {

    const builder = document.getElementById(
        "service-builder"
    );

    if (!builder) return;

    const checkboxes = builder.querySelectorAll(
        ".catalog-checkbox"
    );

    const priceDisplay = document.getElementById(
        "builder-price"
    );

    const durationDisplay = document.getElementById(
        "builder-duration"
    );

    const selectedDisplay = document.getElementById(
        "builder-selected-services"
    );

    const clearButton = document.getElementById(
        "builder-clear"
    );

    const submitButton = document.getElementById(
        "builder-submit"
    );


    function updateBuilder() {

        let totalPriceCents = 0;
        let totalDuration = 0;

        const selectedNames = [];

        checkboxes.forEach(checkbox => {

            const card = checkbox.closest(
                ".catalog-card"
            );

            const action = card.querySelector(
                ".catalog-action"
            );

            if (checkbox.checked) {

                totalPriceCents += Number(
                    checkbox.dataset.price
                );

                totalDuration += Number(
                    checkbox.dataset.duration
                );

                selectedNames.push(
                    checkbox.dataset.name
                );

                action.textContent =
                    "✓ Service Selected";

            } else {

                action.textContent =
                    "Select Service";

            }

        });


        // Display selected services

        selectedDisplay.textContent =
            selectedNames.length
                ? selectedNames.join(", ")
                : "No services selected yet.";


        // Update price

        priceDisplay.textContent =
            "$" + (totalPriceCents / 100).toFixed(2);


        // Update duration

        durationDisplay.textContent =
            `${totalDuration} minutes`;


        // Prevent empty selections

        submitButton.disabled =
            selectedNames.length === 0;

    }


    checkboxes.forEach(checkbox => {

        checkbox.addEventListener(
            "change",
            updateBuilder
        );

    });


    clearButton.addEventListener("click", () => {

        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        updateBuilder();

    });


    builder.addEventListener("submit", event => {

        const hasSelection = Array.from(
            checkboxes
        ).some(checkbox => checkbox.checked);

        if (!hasSelection) {
            event.preventDefault();
        }

    });


    // Initialize summary

    updateBuilder();

});