---
module: PWA / Offline Support
date: 2026-03-25
problem_type: integration_issue
component: service_worker
symptoms:
  - "App unusable at venues with no or poor mobile reception — every page load and JSON fetch required a live network connection"
  - "Rules Quiz, Rules Viewer, and Signals Quiz all failed to load or function without internet"
root_cause: missing_offline_strategy
resolution_type: feature_implementation
severity: high
tags: [pwa, service-worker, offline, github-pages, cache-first, web-app-manifest]
---

# PWA Offline Support on a GitHub Pages Static Site

## Problem

Referees use the app at sports venues that may have no mobile reception. The app had no caching layer — every visit fetched HTML, CSS, JS, and JSON fresh from GitHub Pages. In the field, the app was completely non-functional without a network connection.

## Environment

- Module: All (Rules Quiz `index.html`, Rules Viewer `rules.html`, Signals Quiz `signals.html`)
- Hosting: GitHub Pages at `https://anobleperson.github.io/CanoePoloRules/`
- Stack: Vanilla HTML/CSS/JS, no build step, no npm
- Date: 2026-03-25

## Symptoms

- Opening any page in Airplane Mode showed a browser "No internet connection" error
- All three sections (quiz, rules viewer, signals) non-functional offline
- No "Add to Home Screen" prompt on mobile (no web app manifest)

## Root Cause

The app had no service worker and no `manifest.json`. Without a service worker, browsers never cache anything beyond standard HTTP caching, which does not cover cross-origin navigations or JSON fetches reliably on mobile. Without a manifest, the app was not installable.

## Solution

Three-part implementation:

### 1. `docs/manifest.json` — Web App Manifest

```json
{
  "name": "Canoe Polo Rules",
  "short_name": "CP Rules",
  "start_url": "/CanoePoloRules/",
  "scope": "/CanoePoloRules/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#005b8e",
  "icons": [
    { "src": "favicon-32.png", "sizes": "32x32", "type": "image/png" },
    { "src": "apple-touch-icon.png", "sizes": "180x180", "type": "image/png" }
  ]
}
```

### 2. `docs/sw.js` — Cache-First Service Worker

```js
// IMPORTANT: Bump CACHE_VERSION on every deploy.
const CACHE_VERSION = 'v1';
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
  // + all 20 signal images and 1 field-of-play diagram (21 total)
];

// Install: precache all assets (no skipWaiting — let the update banner appear)
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

// Activate: delete stale caches, claim all clients
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// Fetch: cache-first
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});

// Message: page can trigger skipWaiting to activate a waiting SW
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});
```

### 3. SW Registration + "New Version Available" Banner (all 3 HTML pages)

In `<head>` of each page:
```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#005b8e">
<meta name="apple-mobile-web-app-capable" content="yes">
```

Before `</body>` of each page:
```html
<div id="swUpdateBanner" hidden>
  <span>New version available.</span>
  <button id="swUpdateReload">Reload</button>
</div>
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/CanoePoloRules/sw.js').then(reg => {
      reg.addEventListener('updatefound', () => {
        const newWorker = reg.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            document.getElementById('swUpdateBanner').hidden = false;
          }
        });
      });
    });
    document.getElementById('swUpdateReload').addEventListener('click', () => {
      navigator.serviceWorker.getRegistration().then(reg => {
        if (reg && reg.waiting) reg.waiting.postMessage({ type: 'SKIP_WAITING' });
      });
      window.location.reload();
    });
  }
</script>
```

## Why This Works

- **Precache-all strategy**: The full asset set is ~1.5 MB (dominated by 21 images). With no build step, precaching everything on install is simpler than runtime caching and guarantees complete offline availability after a single connected visit.
- **No `skipWaiting()` in install**: Calling `skipWaiting()` immediately would activate the new SW before the page can display the banner. Instead, the page detects `installing.state === 'installed'` and shows the banner; only when the user clicks "Reload" does the page send `SKIP_WAITING`.
- **`clients.claim()` in activate**: Ensures the newly activated SW controls existing open tabs immediately (without needing a reload).
- **Cache-first fetch**: Returns cached response instantly if found — zero network cost when offline.

## GitHub Pages–Specific Gotchas

- **URL prefix is required in all paths**: GitHub Pages serves the site at `/CanoePoloRules/`, not `/`. All cached asset paths must use `/CanoePoloRules/` as a prefix, including the `start_url` in `manifest.json`.
- **`sw.js` scope**: Register from HTML as `/CanoePoloRules/sw.js` (absolute path), not `./sw.js`. `./sw.js` resolves correctly from `index.html` but will resolve incorrectly if the page is ever served from a subdirectory.
- **`[hidden]` CSS override**: `shared.css` has `[hidden] { display: none !important; }`. The update banner uses the `hidden` attribute, so it must be removed via JS (`element.hidden = false`) rather than relying on a `display:` rule in the banner's CSS. Do not add `display: flex` to `#swUpdateBanner` — the `[hidden]` override will always win unless the attribute is removed first.

## Maintenance

**Every deploy: bump `CACHE_VERSION`** in `docs/sw.js` (e.g. `'v1'` → `'v2'`).

Without this, browsers that have already cached the old SW will never detect an update, because the browser only re-fetches `sw.js` and checks for byte changes. If `CACHE_VERSION` is not bumped, the ASSETS list change is invisible to the browser.

## Prevention

- Add `CACHE_VERSION` bump to your deploy checklist or deploy script for any static-site PWA.
- When adding new assets to the app (new images, JS files, CSS), add them to `ASSETS` in `sw.js` and bump `CACHE_VERSION` in the same commit.
- Test offline behaviour in Chrome DevTools → Application → Service Workers → check "Offline" before declaring offline support working.

## Related Issues

- See also: [focus-ring-carried-between-questions-20260325.md](../ui-bugs/focus-ring-carried-between-questions-20260325.md) — another case where browser behaviour at screen transition required explicit intervention
