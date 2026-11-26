document.addEventListener("DOMContentLoaded", () => {

    const homepage = document.querySelector(
        ".cleanride-home"
    );

    if (!homepage) return;

    const hero = document.getElementById(
        "home-hero"
    );

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    const hasMouse = window.matchMedia(
        "(hover: hover) and (pointer: fine)"
    ).matches;

    if (reducedMotion) return;


    /* =====================================
       1. Cursor Spotlight
    ===================================== */

    if (hero && hasMouse) {

        hero.addEventListener("pointermove", event => {

            const bounds = hero.getBoundingClientRect();

            const x = event.clientX - bounds.left;
            const y = event.clientY - bounds.top;

            hero.style.setProperty(
                "--cursor-x",
                `${x}px`
            );

            hero.style.setProperty(
                "--cursor-y",
                `${y}px`
            );

        });

    }


    /* =====================================
       2. Water Ripple Click Effect
    ===================================== */

    if (hasMouse) {

        homepage.addEventListener("pointerdown", event => {

            if (event.button !== 0) return;

            const ripple = document.createElement("span");

            ripple.className = "cursor-ripple";

            ripple.setAttribute("aria-hidden", "true");

            ripple.style.left = `${event.clientX}px`;
            ripple.style.top = `${event.clientY}px`;

            document.body.appendChild(ripple);

            ripple.addEventListener(
                "animationend",
                () => ripple.remove(),
                { once: true }
            );

            // Cleanup fallback.
            setTimeout(() => ripple.remove(), 1000);

        });

    }


    /* =====================================
       3. Scroll Reveal Animation
    ===================================== */

    if ("IntersectionObserver" in window) {

        const revealElements = homepage.querySelectorAll(
            ".reveal"
        );

        const observer = new IntersectionObserver(

            entries => {

                entries.forEach(entry => {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "visible"
                        );

                        observer.unobserve(entry.target);

                    }

                });

            },

            {
                threshold: 0.08
            }

        );

        homepage.classList.add("animations-enabled");

        revealElements.forEach(element => {
            observer.observe(element);
        });

    }

});