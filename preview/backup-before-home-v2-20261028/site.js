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
  var plate = document.getElementById("journey-frame");
  var frameCount = 52;
  if (plate && !reduceMotion && !narrow) {
    for (var i = 1; i <= frameCount; i++) {
      var preload = new Image();
      preload.src = "media/journey/frame-" + String(i).padStart(2, "0") + ".jpg";
    }
  }
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
    if (plate && !narrow) {
      var index = Math.round(progress * (frameCount - 1)) + 1;
      if (plate.dataset.frame !== String(index)) {
        plate.dataset.frame = String(index);
        plate.src = "media/journey/frame-" + String(index).padStart(2, "0") + ".jpg";
      }
    }
    journey.classList.toggle("is-left", progress > 0.2);
    journey.classList.toggle("is-open", progress > 0.4 && progress < 0.56);
  }
  var works = [
    { href: "veil.html", img: "media/art-left.jpg", ru: "Veil", en: "Veil" },
    { href: "night-road.html", img: "media/art-mid.jpg", ru: "Night Road", en: "Night Road" },
    { href: "above-the-clouds.html", img: "media/art-right.jpg", ru: "Above the Clouds", en: "Above the Clouds" },
    { href: "black-gold.html", img: "media/black-gold.jpg", ru: "Black Gold", en: "Black Gold" }
  ];
  var hall = document.getElementById("gallery");
  var hits = document.querySelectorAll(".fit .hall-hit");
  var hallStart = 0;
  function paintHall() {
    if (!hall) return;
    for (var i = 0; i < hits.length; i++) {
      var work = works[(hallStart + i) % works.length];
      var hit = hits[i];
      hit.href = work.href;
      var img = document.querySelectorAll(".fit .plate")[i];
      if (img) img.src = work.img;
      var label = hit.querySelector("span");
      label.dataset.ru = work.ru;
      label.dataset.en = work.en;
      label.textContent = en ? work.en : work.ru;
    }
    journey.classList.toggle("is-paged", hallStart !== 0);
  }
  var nextHall = document.querySelector("[data-hall-next]");
  if (nextHall) {
    nextHall.addEventListener("click", function () {
      hallStart = (hallStart + 1) % works.length;
      paintHall();
    });
  }
  var forcedHall = new URLSearchParams(location.search).get("hall");
  if (forcedHall) {
    hallStart = Math.min(Math.max(Number(forcedHall) || 0, 0), works.length - 1);
    paintHall();
  }
  if (journey && !reduceMotion && !narrow) {
    window.addEventListener("scroll", placeJourney, { passive: true });
    window.addEventListener("resize", placeJourney);
  }
  placeJourney();
})();
