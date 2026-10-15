/* Sortir de la religion sans en fonder une autre ? : historique des sauts, commun à toutes les pages du site */
window.sauts = (function () {
  var K = "sdr-jumps";
  var pageOf = function (path) { return path.replace(/.*\//, "") || "index.html"; };
  var PAGE = pageOf(location.pathname);
  var jumps = [], jc = 0, leaving = false; /* jumps[jc] est la case de la position courante, remplie quand on la quitte */
  var nav = document.getElementById("jump-nav"), prev = document.getElementById("jump-prev"), next = document.getElementById("jump-next");

  function reveal(id, dy) { /* ouvre les sections repliées, puis place l'élément à dy px du haut (60 par défaut) */
    var el = document.getElementById(id);
    if (!el) return;
    for (var p = el; p; p = p.parentElement) if (p.tagName === "DETAILS") p.open = true;
    var go = function () { window.scrollTo(0, Math.max(0, el.getBoundingClientRect().top + window.pageYOffset - (dy == null ? 60 : dy))); };
    /* Les images ont leurs dimensions : un défilement suffit ; le rattrapage couvre le chargement des polices. */
    setTimeout(go, 0);
    setTimeout(go, 300);
  }
  function posNow() { /* dernier élément à id passé sous la barre, et son décalage */
    var best = null, bestTop = -Infinity, els = document.querySelectorAll("main [id]");
    for (var i = 0; i < els.length; i++) {
      if (!els[i].offsetParent) continue;
      var top = els[i].getBoundingClientRect().top;
      if (top <= 90 && top > bestTop) { best = els[i]; bestTop = top; }
    }
    return best ? { page: PAGE, id: best.id, dy: bestTop } : { page: PAGE, y: window.pageYOffset };
  }
  function restore(p) { if (p.id && document.getElementById(p.id)) reveal(p.id, p.dy); else window.scrollTo(0, p.y || 0); }
  function save() { try { sessionStorage.setItem(K, JSON.stringify({ jumps: jumps, jc: jc })); } catch (e) {} }
  function paint() { nav.hidden = jumps.length === 0; prev.disabled = jc === 0; next.disabled = jc >= jumps.length - 1; }
  function newJump() { jumps[jc] = posNow(); jumps.length = jc + 1; jc++; save(); paint(); }
  function go(d) {
    jumps[jc] = posNow(); jc += d; var p = jumps[jc]; save(); paint();
    if (p.page === PAGE) restore(p);
    else { leaving = true; location.href = p.page + (p.id ? "#" + p.id : ""); }
  }
  prev.addEventListener("click", function () { if (jc > 0) go(-1); });
  next.addEventListener("click", function () { if (jc < jumps.length - 1) go(1); });
  /* Tout lien interne suivi d'un clic ordinaire est un saut : on note d'où l'on part */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || a.target || a.origin !== location.origin) return;
    newJump();
    if (pageOf(a.pathname) !== PAGE) leaving = true;
  }, true);
  window.addEventListener("pagehide", function () { if (!leaving) { jumps[jc] = posNow(); save(); } });

  var restored = false;
  function sync(scroll) { /* à l'ouverture de la page, ou à son retour depuis le cache du navigateur */
    leaving = false;
    try { var s = JSON.parse(sessionStorage.getItem(K)); if (s && s.jumps) { jumps = s.jumps; jc = s.jc; } } catch (e) {}
    var p = jumps[jc], hash = decodeURIComponent(location.hash.slice(1));
    if (p && p.page === PAGE && (!hash || hash === p.id)) { restored = scroll; if (scroll) restore(p); } /* retour par les boutons : position exacte */
    else if (p) { jumps.length = jc + 1; jc++; } /* arrivée par un lien, le navigateur ou l'adresse : nouvelle case */
    paint();
  }
  sync(true);
  window.addEventListener("pageshow", function (e) { if (e.persisted) sync(false); });
  return { reveal: reveal, newJump: newJump, restored: restored };
})();
