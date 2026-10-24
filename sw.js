/* Service worker : lecture hors connexion. Fichier généré par build/build.py. */
var VERSION = "1792795764";
var SHELL_CACHE = "sdr-shell-" + VERSION;
var IMG_CACHE = "sdr-images";
var FONT_CACHE = "sdr-fonts";
var SHELL = [
  "./",
  "index.html",
  "css/style.css?v=" + VERSION,
  "js/app.js?v=" + VERSION,
  "js/sauts.js?v=" + VERSION,
  "favicon.svg",
  "auteurs.html",
  "lexique.html",
  "annexes.html",
  "bibliotheque.html",
  "galerie.html",
  "sources.html",
  "js/pages.js?v=" + VERSION,
  "facile/index.html",
  "facile/auteurs.html",
  "facile/lexique.html",
  "facile/annexes.html",
  "facile/bibliotheque.html",
  "facile/galerie.html",
  "facile/sources.html",
  "en/index.html",
  "en/auteurs.html",
  "en/lexique.html",
  "en/annexes.html",
  "en/bibliotheque.html",
  "en/galerie.html",
  "en/sources.html",
  "ru/index.html",
  "ru/auteurs.html",
  "ru/lexique.html",
  "ru/annexes.html",
  "ru/bibliotheque.html",
  "ru/galerie.html",
  "ru/sources.html",
  "de/index.html",
  "de/auteurs.html",
  "de/lexique.html",
  "de/annexes.html",
  "de/bibliotheque.html",
  "de/galerie.html",
  "de/sources.html",
  "es/index.html",
  "es/auteurs.html",
  "es/lexique.html",
  "es/annexes.html",
  "es/bibliotheque.html",
  "es/galerie.html",
  "es/sources.html",
  "js/portrait.js?v=" + VERSION
];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(SHELL_CACHE).then(function (c) { return c.addAll(SHELL); }));
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) {
      return k !== SHELL_CACHE && k !== IMG_CACHE && k !== FONT_CACHE;
    }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

function cacheFirst(req, name) {
  return caches.open(name).then(function (c) {
    return c.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) {
        if (res && (res.ok || res.type === "opaque")) c.put(req, res.clone());
        return res;
      });
    });
  });
}

function networkFirst(req) {
  /* clé de cache relative à la portée du service worker : en/index.html et index.html sont deux pages */
  var rel = new URL(req.url).pathname.slice(new URL(self.registration.scope).pathname.length);
  var page = /(^|\/)$/.test(rel) ? rel + "index.html" : rel;
  return fetch(req).then(function (res) {
    if (res && res.ok) {
      var copy = res.clone();
      caches.open(SHELL_CACHE).then(function (c) { c.put(page, copy); });
    }
    return res;
  }).catch(function () {
    return caches.match(page, { ignoreSearch: true });
  });
}

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(cacheFirst(req, FONT_CACHE));
    return;
  }
  if (url.origin !== self.location.origin) return;
  if (req.mode === "navigate" || /\/([a-z]+\.html)?$/.test(url.pathname)) {
    e.respondWith(networkFirst(req));
    return;
  }
  if (url.pathname.indexOf("/images/") >= 0) {
    e.respondWith(cacheFirst(req, IMG_CACHE));
    return;
  }
  e.respondWith(cacheFirst(req, SHELL_CACHE));
});
