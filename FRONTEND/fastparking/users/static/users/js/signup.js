// RUN only when DOM is loaded
console.log("signup.js loaded");

document.addEventListener("DOMContentLoaded", function() {
    console.log("signup.js started");
    const modal = document.getElementById("termsModal");
    const closeBtn = document.querySelector("#termsModal .btn-close");
    const termsLink = document.getElementById("terms_link");
    const acceptBtn = document.getElementById("acceptBtn");
    const declineBtn = document.getElementById("declineBtn");

    // Відкриття модального вікна при кліку на посилання
    termsLink?.addEventListener("click", function()
    {
        modal.classList.add("show");
        modal.style.display = "block";
    });


  // Обробник події для кнопок погодження та відмови
    acceptBtn?.addEventListener("click", function() {
        document.getElementById("accept_oferta").checked = true;
        modal.style.display = "none";
    });

    declineBtn?.addEventListener("click", function() {
        document.getElementById("accept_oferta").checked = false;
        modal.style.display = "none";
    });

    // Закриття модального вікна при кліку на хрестик
    closeBtn?.addEventListener("click", function() {
        modal.classList.remove("show");
        modal.style.display = "none";
    });
});