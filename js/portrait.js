/* Fenêtre du portrait en grand au survol d'un avatar (img.avatar). Chargé par toutes les pages du site. */
(function () {
  "use strict";
  /* Portrait en grand au survol de l'avatar (au toucher : une pression ouvre, une autre ferme) */
  var popup = document.createElement("figure");
  popup.className = "portrait-popup";
  popup.hidden = true;
  popup.innerHTML = '<img alt=""><figcaption></figcaption>';
  document.body.appendChild(popup);
  var popupImg = popup.querySelector("img"), popupCap = popup.querySelector("figcaption"), popupPour = null;
  function placerPopup(av) {
    var r = av.getBoundingClientRect(), top = r.top - 8, left = r.right + 12;
    var haut = (parseInt(getComputedStyle(document.documentElement).getPropertyValue("--topbar"), 10) || 52) + 8;
    if (left + popup.offsetWidth > window.innerWidth - 16) left = Math.max(16, r.left - popup.offsetWidth - 12);
    if (top + popup.offsetHeight > window.innerHeight - 16) top = window.innerHeight - 16 - popup.offsetHeight;
    popup.style.left = left + "px";
    popup.style.top = Math.max(haut, top) + "px";
  }
  function montrerPopup(av) {
    popupPour = av;
    popupImg.src = av.currentSrc || av.src;
    popupImg.alt = av.alt;
    popupCap.textContent = av.getAttribute("data-legende") || av.alt;
    popup.hidden = false;
    placerPopup(av);
    requestAnimationFrame(function () { placerPopup(av); popup.classList.add("visible"); });
  }
  function cacherPopup() {
    popupPour = null;
    popup.classList.remove("visible");
    popup.hidden = true;
  }
  var tactile = window.matchMedia("(hover: none)").matches;
  document.addEventListener("mouseover", function (e) {
    var av = e.target.closest && e.target.closest("img.avatar");
    if (av && !tactile) montrerPopup(av);
  });
  document.addEventListener("mouseout", function (e) {
    var av = e.target.closest && e.target.closest("img.avatar");
    if (av && !tactile) cacherPopup();
  });
  if (tactile) {
    document.addEventListener("click", function (e) {
      var av = e.target.closest && e.target.closest("img.avatar");
      if (av) {
        e.preventDefault();
        if (popupPour === av) cacherPopup(); else montrerPopup(av);
      } else if (popupPour) cacherPopup();
    }, true);
  }
  window.addEventListener("scroll", function () { if (popupPour) cacherPopup(); }, { passive: true });
  popupImg.addEventListener("load", function () { if (popupPour) placerPopup(popupPour); });
})();
