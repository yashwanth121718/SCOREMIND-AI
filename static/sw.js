// ============================================================
// Service Worker for EvalAI PWA Caching
// ============================================================

const CACHE_NAME = 'evalai-cache-v1';
const ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/css/dashboard.css',
  '/static/js/script.js',
  '/static/js/validation.js',
  '/static/js/dashboard.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    })
  );
});
