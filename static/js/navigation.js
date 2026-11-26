document.addEventListener("DOMContentLoaded", () => {

    const header = document.getElementById(
        "site-header"
    );

    const mobileToggle = document.getElementById(
        "mobile-menu-toggle"
    );

    const navigationMenu = document.getElementById(
        "navigation-menu"
    );

    const accountDropdown = document.getElementById(
        "account-dropdown"
    );

    const accountToggle = document.getElementById(
        "account-toggle"
    );

    const accountMenu = document.getElementById(
        "account-menu"
    );

    if (!header) return;


    /* ======================================
       1. STICKY NAVIGATION SCROLL EFFECT
    ====================================== */

    function updateHeader() {

        header.classList.toggle(
            "scrolled",
            window.scrollY > 50
        );

    }

    window.addEventListener(
        "scroll",
        updateHeader,
        { passive: true }
    );

    updateHeader();


    /* ======================================
       2. ACCOUNT DROPDOWN
    ====================================== */

    function closeAccountMenu() {

        if (!accountDropdown || !accountToggle ||
            !accountMenu) return;

        accountDropdown.classList.remove("open");

        accountToggle.setAttribute(
            "aria-expanded",
            "false"
        );

        accountMenu.inert = true;

    }


    function toggleAccountMenu() {

        if (!accountDropdown || !accountToggle ||
            !accountMenu) return;

        const isOpen = accountDropdown.classList.toggle(
            "open"
        );

        accountToggle.setAttribute(
            "aria-expanded",
            String(isOpen)
        );

        accountMenu.inert = !isOpen;

    }


    if (accountToggle) {

        accountToggle.addEventListener(
            "click",
            toggleAccountMenu
        );

    }


    /* ======================================
       3. MOBILE NAVIGATION
    ====================================== */

    function closeMobileMenu() {

        if (!mobileToggle || !navigationMenu) return;

        mobileToggle.classList.remove("open");

        navigationMenu.classList.remove("open");

        mobileToggle.setAttribute(
            "aria-expanded",
            "false"
        );

        closeAccountMenu();

    }


    if (mobileToggle && navigationMenu) {

        mobileToggle.addEventListener("click", () => {

            const isOpen = navigationMenu.classList.toggle(
                "open"
            );

            mobileToggle.classList.toggle(
                "open",
                isOpen
            );

            mobileToggle.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

            if (!isOpen) {
                closeAccountMenu();
            }

        });

    }


    /* ======================================
       4. CLOSE MENUS WHEN CLICKING OUTSIDE
    ====================================== */

    document.addEventListener("click", event => {

        if (
            accountDropdown &&
            !accountDropdown.contains(event.target)
        ) {
            closeAccountMenu();
        }

        if (!header.contains(event.target)) {
            closeMobileMenu();
        }

    });


    /* ======================================
       5. KEYBOARD ACCESSIBILITY
    ====================================== */

    document.addEventListener("keydown", event => {

        if (event.key !== "Escape") return;

        if (
            accountDropdown &&
            accountDropdown.classList.contains("open")
        ) {

            closeAccountMenu();
            accountToggle.focus();

            return;
        }

        if (
            navigationMenu &&
            navigationMenu.classList.contains("open")
        ) {

            closeMobileMenu();
            mobileToggle.focus();

        }

    });


    /* ======================================
       6. RESET MOBILE MENU ON DESKTOP
    ====================================== */

    const desktopMedia = window.matchMedia(
        "(min-width: 851px)"
    );

    desktopMedia.addEventListener("change", event => {

        if (event.matches) {
            closeMobileMenu();
        }

    });

});