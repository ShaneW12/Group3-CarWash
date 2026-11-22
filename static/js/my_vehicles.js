
document.addEventListener("DOMContentLoaded", () => {

    const yearSelect = document.getElementById(
        "vehicle-year"
    );

    const makeSelect = document.getElementById(
        "vehicle-make"
    );

    const modelSelect = document.getElementById(
        "vehicle-model"
    );

    if (!yearSelect || !makeSelect || !modelSelect) {
        return;
    }

    function resetSelect(select, placeholder) {
        select.replaceChildren(
            new Option(placeholder, "")
        );
        select.disabled = true;
    }

    function addOptions(select, values) {
        values.forEach(value => {
            select.add(new Option(value, value));
        });

        select.disabled = values.length === 0;
    }

    // Load manufacturers when the year changes
    yearSelect.addEventListener("change", async () => {

        resetSelect(
            makeSelect,
            "Loading manufacturers..."
        );

        resetSelect(
            modelSelect,
            "Select model"
        );

        if (!yearSelect.value) {
            resetSelect(makeSelect, "Select manufacturer");
            return;
        }

        const requestedYear = yearSelect.value;

        try {
            const response = await fetch(
                makeSelect.dataset.url
            );

            if (!response.ok) {
                throw new Error("Unable to load makes");
            }

            const data = await response.json();

            if (yearSelect.value !== requestedYear) {
                return;
            }

            resetSelect(makeSelect, "Select manufacturer");

            const makes = [...new Set(
                data.makes.map(make => make.name)
            )].sort();

            addOptions(makeSelect, makes);

        } catch (error) {
            console.error(error);
            resetSelect(
                makeSelect,
                "Unable to load manufacturers"
            );
        }
    });

    // Load models when the manufacturer changes
    makeSelect.addEventListener("change", async () => {

        resetSelect(modelSelect, "Loading models...");

        if (!makeSelect.value || !yearSelect.value) {
            resetSelect(modelSelect, "Select model");
            return;
        }

        const selectedMake = makeSelect.value;
        const selectedYear = yearSelect.value;

        const params = new URLSearchParams({
            make: selectedMake,
            year: selectedYear
        });

        try {
            const response = await fetch(
                `${modelSelect.dataset.url}?${params}`
            );

            if (!response.ok) {
                throw new Error("Unable to load models");
            }

            const data = await response.json();

            if (
                makeSelect.value !== selectedMake ||
                yearSelect.value !== selectedYear
            ) {
                return;
            }

            resetSelect(modelSelect, "Select model");

            const models = [...new Set(data.models)]
                .sort();

            addOptions(modelSelect, models);

        } catch (error) {
            console.error(error);
            resetSelect(
                modelSelect,
                "Unable to load models"
            );
        }
    });

});
