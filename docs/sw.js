// sw.js — Service Worker for offline support
// IMPORTANT: Bump CACHE_VERSION on every deploy to invalidate old caches.

const CACHE_VERSION = 'v2';
const CACHE_NAME = 'cp-rules-' + CACHE_VERSION;

const ASSETS = [
  '/CanoePoloRules/',
  '/CanoePoloRules/rules.html',
  '/CanoePoloRules/signals.html',
  '/CanoePoloRules/shared.css',
  '/CanoePoloRules/quiz.css',
  '/CanoePoloRules/rules.css',
  '/CanoePoloRules/quiz.js',
  '/CanoePoloRules/rules.js',
  '/CanoePoloRules/signals.js',
  '/CanoePoloRules/questions.json',
  '/CanoePoloRules/rules.json',
  '/CanoePoloRules/manifest.json',
  '/CanoePoloRules/favicon.svg',
  '/CanoePoloRules/favicon-32.png',
  '/CanoePoloRules/apple-touch-icon.png',
  // Field of play diagram
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0053-03.png',
  // Signal images (page105)
  '/CanoePoloRules/images/page105_img1.png',
  '/CanoePoloRules/images/page105_img2.png',
  '/CanoePoloRules/images/page105_img3.png',
  '/CanoePoloRules/images/page105_img4.png',
  '/CanoePoloRules/images/page105_img5.png',
  // Signal images (page108)
  '/CanoePoloRules/images/page108_img1.png',
  '/CanoePoloRules/images/page108_img2.png',
  '/CanoePoloRules/images/page108_img3.png',
  '/CanoePoloRules/images/page108_img4.png',
  '/CanoePoloRules/images/page108_img5.png',
  // Signal images (pdf-0106)
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0106-00.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0106-01.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0106-02.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0106-03.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0106-04.png',
  // Signal images (pdf-0107)
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0107-00.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0107-01.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0107-02.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0107-03.png',
  '/CanoePoloRules/images/2025_icf_canoe_polo_rules.pdf-0107-04.png',
];

// Install: precache all assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  // Do NOT call skipWaiting() here — let the new SW wait so the
  // "New version available" banner can appear on the page.
});

// Activate: delete stale caches, claim all clients
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch: cache-first strategy
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request);
    })
  );
});

// Message: allow the page to trigger skipWaiting for the update banner
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
