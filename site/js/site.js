(function () {
  var en = localStorage.getItem("clave-lang") === "en";

  function apply() {
    document.documentElement.lang = en ? "en" : "ru";
    document.querySelectorAll("[data-ru]").forEach(function (el) {
      el.textContent = en ? el.dataset.en : el.dataset.ru;
    });
    document.querySelectorAll("[data-ru-placeholder]").forEach(function (el) {
      el.placeholder = en ? el.dataset.enPlaceholder : el.dataset.ruPlaceholder;
    });
    var lang = document.getElementById("lang");
    if (lang) lang.textContent = en ? "EN / RU" : "RU / EN";
  }

  var langButton = document.getElementById("lang");
  if (langButton) {
    langButton.addEventListener("click", function () {
      en = !en;
      localStorage.setItem("clave-lang", en ? "en" : "ru");
      apply();
    });
  }
  apply();

  var player = document.getElementById("player");
  document.querySelectorAll("[data-play]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (player && player.showModal) player.showModal();
    });
  });
  if (player) {
    player.querySelector("[data-close]").addEventListener("click", function () {
      player.close();
    });
    player.addEventListener("click", function (event) {
      if (event.target === player) player.close();
    });
  }

  var form = document.getElementById("brief");
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var name = form.name.value.trim();
      var task = form.task.value.trim();
      var contact = form.contact.value.trim();
      var error = document.getElementById("form-error");
      if (!name || !task || !contact) {
        error.hidden = false;
        return;
      }
      error.hidden = true;
      form.hidden = true;
      document.getElementById("sent").hidden = false;
    });
  }

  var telegram = document.getElementById("telegram");
  if (telegram) {
    telegram.addEventListener("click", function (event) {
      if (telegram.getAttribute("href") === "#") {
        event.preventDefault();
        document.getElementById("telegram-note").hidden = false;
      }
    });
  }

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var narrow = window.matchMedia("(max-width: 860px)").matches;
  var journey = document.getElementById("journey");
  function placeJourney() {
    if (!journey) return;
    var forced = new URLSearchParams(location.search).get("frame");
    var progress = 0;
    if (!reduceMotion && !narrow) {
      var total = journey.offsetHeight - window.innerHeight;
      var passed = Math.min(Math.max(-journey.getBoundingClientRect().top, 0), Math.max(total, 0));
      progress = total > 0 ? passed / total : 0;
    }
    if (forced !== null && forced !== "") progress = Math.min(Math.max(Number(forced), 0), 1);
    journey.style.setProperty("--p", progress.toFixed(4));
    var swing = Math.sin(progress * Math.PI);
    journey.style.setProperty("--yaw", (swing * 4).toFixed(2) + "deg");
    journey.style.setProperty("--overlap", (swing * 12).toFixed(2) + "%");
    journey.classList.toggle("is-left", progress > 0.4);
    journey.classList.toggle("is-open", progress > 0.92);
  }
  if (journey && !reduceMotion && !narrow) {
    window.addEventListener("scroll", placeJourney, { passive: true });
    window.addEventListener("resize", placeJourney);
  }
  placeJourney();
})();
