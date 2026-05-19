// Point the logo and site-name links to the root homepage
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(
        "a.md-header__button.md-logo, a.md-header__title"
    ).forEach(function (el) {
        el.setAttribute("href", "/");
    });
});
