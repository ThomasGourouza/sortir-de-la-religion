/* Sortir de la religion sans en fonder une autre ? : interactions de lecture */
(function () {
  "use strict";

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var drawer = $("#drawer"), backdrop = $("#backdrop"), menuBtn = $("#menu-btn");
  var wide = window.matchMedia("(min-width: 1100px)");
  var parties = $$("details.partie");

  /* Sommaire */
  function openDrawer() {
    if (wide.matches) return;
    drawer.classList.add("open");
    backdrop.hidden = false;
    menuBtn.setAttribute("aria-expanded", "true");
    var active = $(".toc a.active");
    if (active) active.scrollIntoView({ block: "center" });
  }
  function closeDrawer() {
    drawer.classList.remove("open");
    backdrop.hidden = true;
    menuBtn.setAttribute("aria-expanded", "false");
  }
  menuBtn.addEventListener("click", function () {
    drawer.classList.contains("open") ? closeDrawer() : openDrawer();
  });
  $("#close-drawer").addEventListener("click", closeDrawer);
  backdrop.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  /* Ouvrir une cible : déplie les details parents puis fait défiler */
  function reveal(id, smooth) {
    var el = document.getElementById(id);
    if (!el) return;
    var p = el;
    while (p) {
      if (p.tagName === "DETAILS") p.open = true;
      p = p.parentElement;
    }
    var go = function () {
      var y = el.getBoundingClientRect().top + window.pageYOffset - 60;
      window.scrollTo(0, Math.max(0, y));
    };
    setTimeout(go, 0);
    setTimeout(go, 150);
    setTimeout(go, 450);
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-target]");
    if (!a) return;
    var id = a.getAttribute("data-target");
    if (id === "top") { closeDrawer(); return; }
    e.preventDefault();
    closeDrawer();
    history.replaceState(null, "", "#" + id);
    reveal(id);
  });

  /* Filtre du sommaire */
  $("#toc-filter").addEventListener("input", function () {
    var q = this.value.trim().toLowerCase()
      .normalize("NFD").replace(/[̀-ͯ]/g, "");
    $$(".toc > li").forEach(function (li) {
      var subs = $$("ul li", li), anyHit = false;
      subs.forEach(function (s) {
        var hit = !q || s.textContent.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").indexOf(q) >= 0;
        s.classList.toggle("hidden", !hit);
        if (hit) anyHit = true;
      });
      var self = li.firstElementChild.textContent.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
      li.classList.toggle("hidden", !!q && !anyHit && self.indexOf(q) < 0);
    });
  });

  /* Tout déplier, tout replier */
  $("#expand-all").addEventListener("click", function () { $$("details.partie, details.section").forEach(function (d) { d.open = true; }); saveOpen(); });
  $("#collapse-all").addEventListener("click", function () { parties.forEach(function (d) { d.open = false; }); saveOpen(); });

  /* Mémoire des parties ouvertes */
  function saveOpen() {
    store.set("sdr-open", JSON.stringify(parties.filter(function (d) { return d.open; }).map(function (d) { return d.id; })));
  }
  parties.forEach(function (d) { d.addEventListener("toggle", saveOpen); });
  try {
    var saved = JSON.parse(store.get("sdr-open") || "[]");
    saved.forEach(function (id) { var d = document.getElementById(id); if (d) d.open = true; });
  } catch (e) {}

  /* Thème et taille du texte */
  var themes = ["auto", "light", "sepia", "dark"];
  $("#theme-btn").addEventListener("click", function () {
    var cur = document.documentElement.dataset.theme || "auto";
    var next = themes[(themes.indexOf(cur) + 1) % themes.length];
    if (next === "auto") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = next;
    store.set("sdr-theme", next === "auto" ? "" : next);
    this.setAttribute("aria-label", "Thème : " + ({ auto: "automatique", light: "clair", sepia: "sépia", dark: "sombre" })[next]);
  });
  function fontStep(d) {
    var cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--fs")) || 18;
    var next = Math.max(14, Math.min(26, cur + d));
    document.documentElement.style.setProperty("--fs", next + "px");
    store.set("sdr-font", String(next));
  }
  $("#font-up").addEventListener("click", function () { fontStep(1); });
  $("#font-down").addEventListener("click", function () { fontStep(-1); });

  /* Progression, section courante, retour en haut, reprise de lecture */
  var bar = $("#progress-bar"), toTop = $("#to-top"), title = $("#current-title");
  var defaultTitle = title.textContent;
  var tocLinks = {};
  $$(".toc a[data-target]").forEach(function (a) { tocLinks[a.getAttribute("data-target")] = a; });
  var current = null;

  function setCurrent(id, label) {
    if (id === current) return;
    current = id;
    $$(".toc a.active").forEach(function (a) { a.classList.remove("active"); });
    if (tocLinks[id]) tocLinks[id].classList.add("active");
    title.textContent = label || defaultTitle;
  }

  var heads = $$("details.section, details.partie");
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    setTimeout(function () {
      ticking = false;
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
      toTop.hidden = h.scrollTop < 900;
      var best = null, bestTop = -Infinity, lim = 90;
      for (var i = 0; i < heads.length; i++) {
        var d = heads[i];
        if (!d.offsetParent) continue;
        var top = d.getBoundingClientRect().top;
        if (top <= lim && top > bestTop) { best = d; bestTop = top; }
      }
      if (best) {
        var s = best.querySelector("summary .sec-nom, summary .part-sub, summary .part-label");
        setCurrent(best.id, s ? s.textContent : "");
        store.set("sdr-pos", best.id);
      } else {
        setCurrent(null, "");
      }
    }, 60);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });

  var resume = $("#resume-btn"), pos = store.get("sdr-pos");
  if (resume && pos && document.getElementById(pos)) {
    resume.hidden = false;
    resume.addEventListener("click", function () { reveal(pos); });
  }

  /* Lien profond à l'ouverture */
  if (location.hash.length > 1) {
    var id = decodeURIComponent(location.hash.slice(1));
    if (document.getElementById(id)) setTimeout(function () { reveal(id, false); }, 50);
  }
  window.addEventListener("hashchange", function () {
    var id = decodeURIComponent(location.hash.slice(1));
    if (id && document.getElementById(id)) reveal(id);
  });

  /* Impression : tout déplier */
  window.addEventListener("beforeprint", function () { $$("details").forEach(function (d) { d.open = true; }); });

  onScroll();
})();
