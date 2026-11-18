
    document.addEventListener("DOMContentLoaded", function () {

        const yearSelect = document.getElementById("vehicle-year");
        const makeSelect = document.getElementById("vehicle-make");
        const modelSelect = document.getElementById("vehicle-model");

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

                resetDropdown(makeSelect, "Unable to load manufacturers");
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

                resetDropdown(modelSelect, "Unable to load models");
                console.error(error);
            }
        });

        // Prevent booking before vehicle selection is complete
        yearSelect.closest("form").addEventListener("submit", function (event) {
            if (!yearSelect.value || !makeSelect.value || !modelSelect.value) {
                event.preventDefault();
                alert("Please select your vehicle year, make, and model.");
            }
        });

    });
