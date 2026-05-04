/* Gurbani Path service worker
 *
 * Strategy:
 *   - For app shell + corpus (the big /app/ page): cache-first with
 *     background revalidation
 *   - For other HTML pages (landing, about, credits, etc.): network-first
 *     so users see the latest copy when online
 *   - For static assets (CSS, fonts, icons): cache-first, never expire
 *     until version bump
 *
 * To force all clients to re-fetch (e.g. after a corpus update),
 * bump CACHE_VERSION below.
 */

const CACHE_VERSION = 'v1';
const CACHE_NAME = `gurbanipath-${CACHE_VERSION}`;

// Pages and assets to pre-cache on install
const PRECACHE = [
  '/',
  '/app/',
  '/about.html',
  '/credits.html',
  '/privacy.html',
  '/feedback.html',
  '/site.css',
  '/manifest.webmanifest',
  '/favicon.ico',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/apple-touch-icon.png',
  '/fonts/NotoSerifGurmukhi.ttf',
];

// ---- INSTALL ----
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // addAll fails the whole install if any URL fails — use Promise.allSettled
      // so missing optional assets don't break installation
      return Promise.allSettled(
        PRECACHE.map((url) =>
          cache.add(new Request(url, { cache: 'reload' })).catch((err) => {
            console.warn('[SW] Pre-cache miss:', url, err.message);
          })
        )
      );
    })
  );
  self.skipWaiting();
});

// ---- ACTIVATE ----
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k.startsWith('gurbanipath-') && k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ---- FETCH ----
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Skip cross-origin requests entirely (Google Fonts CSS, etc.)
  if (url.origin !== self.location.origin) return;

  // App shell: cache-first, revalidate in background
  if (url.pathname.startsWith('/app/')) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const fetchPromise = fetch(req)
          .then((response) => {
            if (response && response.status === 200) {
              const clone = response.clone();
              caches.open(CACHE_NAME).then((c) => c.put(req, clone));
            }
            return response;
          })
          .catch(() => cached);
        return cached || fetchPromise;
      })
    );
    return;
  }

  // Static assets: cache-first
  if (
    url.pathname.startsWith('/fonts/') ||
    url.pathname.startsWith('/icons/') ||
    url.pathname === '/site.css' ||
    url.pathname === '/favicon.ico' ||
    url.pathname === '/manifest.webmanifest'
  ) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTML pages: network-first
  if (req.headers.get('Accept')?.includes('text/html')) {
    event.respondWith(
      fetch(req)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, clone));
          }
          return response;
        })
        .catch(() => caches.match(req).then((c) => c || caches.match('/')))
    );
    return;
  }

  // Default: network, fallback to cache
  event.respondWith(
    fetch(req).catch(() => caches.match(req))
  );
});
