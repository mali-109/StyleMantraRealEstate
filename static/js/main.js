const mobileMenu =
    document.getElementById("mobileMenu");

const navMenu =
    document.querySelector(".nav-menu");


if (mobileMenu) {

    mobileMenu.addEventListener(
        "click",
        function () {

            navMenu.classList.toggle(
                "mobile-open"
                
            );

        }
    );

}