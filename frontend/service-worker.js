/**
 * DataFix PWA Service Worker
 * Enables offline caching and desktop/mobile PWA installation.
 */

const CACHE_NAME = "datafix-cache-v1";
const ASSETS_TO_CACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./css/style.css",
  "./css/speedometer.css",
  "./js/app.js",
  "./js/api.js",
  "./js/speedometer.js",
  "./js/threeScene.js",
  "./js/collegeData.js"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn("ServiceWorker asset caching warning:", err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((cachedResponse) => {
      return cachedResponse || fetch(e.request).catch(() => {
        return caches.match("./index.html");
      });
    })
  );
});
