/* Pages outils (frise, réponses, lexique, annexes, bibliothèque) : thème, taille du texte, filtres */
(function () {
  "use strict";

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var norm = function (s) { return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };

  var themes = ["auto", "light", "sepia", "dark"];
  $("#theme-btn").addEventListener("click", function () {
    var cur = document.documentElement.dataset.theme || "auto";
    var next = themes[(themes.indexOf(cur) + 1) % themes.length];
    if (next === "auto") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = next;
    store.set("sdr-theme", next === "auto" ? "" : next);
  });
  function fontStep(d) {
    var cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--fs")) || 18;
    var next = Math.max(14, Math.min(26, cur + d));
    document.documentElement.style.setProperty("--fs", next + "px");
    store.set("sdr-font", String(next));
  }
  $("#font-up").addEventListener("click", function () { fontStep(1); });
  $("#font-down").addEventListener("click", function () { fontStep(-1); });

  /* Filtres : texte libre, type de réponse, partie */
  var input = $("[data-filtre-texte]");
  var typeBtns = $$("[data-filtre-type]");
  var partSel = $("[data-filtre-partie]");
  var type = "tous";

  function apply() {
    var q = input ? norm(input.value.trim()) : "";
    var part = partSel ? partSel.value : "";
    $$("[data-item]").forEach(function (el) {
      var carte = el.closest(".rep-carte");
      var texte = el.textContent + (carte ? " " + carte.querySelector("h2").textContent : "");
      var ok = !q || norm(texte).indexOf(q) >= 0;
      if (ok && type !== "tous" && el.hasAttribute("data-type")) ok = el.getAttribute("data-type") === type;
      if (ok && part && el.hasAttribute("data-partie")) ok = el.getAttribute("data-partie") === part;
      el.hidden = !ok;
    });
    $$(".rep-carte > ul").forEach(function (ul) {
      var h = ul.previousElementSibling;
      var vide = !$$("[data-item]", ul).some(function (el) { return !el.hidden; });
      ul.hidden = vide;
      if (h && h.tagName === "H3") h.hidden = vide;
    });
    $$("[data-groupe]").forEach(function (g) {
      g.hidden = !$$("[data-item]", g).some(function (el) { return !el.hidden; });
    });
    var vide = $("#aucun");
    if (vide) vide.hidden = $$("[data-item]").some(function (el) { return !el.hidden; });
  }
  if (input) input.addEventListener("input", apply);
  if (partSel) partSel.addEventListener("change", apply);
  typeBtns.forEach(function (b) {
    b.addEventListener("click", function () {
      type = b.getAttribute("data-filtre-type");
      typeBtns.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      apply();
    });
  });

  /* Lien profond vers un terme du lexique ou un article des annexes : le mettre en évidence, et l'ouvrir s'il est replié.
     Vaut à l'arrivée sur la page et à chaque changement d'ancre (lien d'un article vers un autre de la même page). */
  function cible(defiler) {
    if (location.hash.length < 2) return;
    var el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (!el) return;
    $$(".cible").forEach(function (x) { if (x !== el) x.classList.remove("cible"); });
    el.classList.add("cible");
    if (el.tagName === "DETAILS") el.open = true;
    if (el.hidden) { /* masqué par un filtre : on le rétablit */
      if (input) input.value = "";
      type = "tous";
      typeBtns.forEach(function (x) { x.setAttribute("aria-pressed", String(x.getAttribute("data-filtre-type") === "tous")); });
      apply();
    }
    if (defiler) el.scrollIntoView();
  }
  cible(false);
  window.addEventListener("hashchange", function () { cible(true); });

  if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  }
})();
