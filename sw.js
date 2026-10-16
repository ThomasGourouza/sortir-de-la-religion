/* Service worker : lecture hors connexion. Fichier généré par build/build.py. */
var VERSION = "1792186198";
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
  "frise.html",
  "reponses.html",
  "lexique.html",
  "annexes.html",
  "bibliotheque.html",
  "js/pages.js?v=" + VERSION
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
  var page = (new URL(req.url).pathname.match(/([a-z]+\.html)$/) || [null, "index.html"])[1];
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
