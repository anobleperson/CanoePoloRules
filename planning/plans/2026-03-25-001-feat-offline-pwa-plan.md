---
title: "feat: Add offline PWA support (service worker + manifest)"
type: feat
status: completed
date: 2026-03-25
origin: planning/brainstorms/2026-03-25-offline-pwa-requirements.md
---

# feat: Add Offline PWA Support

## Overview

Make the app fully functional without internet after one connected visit. Referees use this at venues with poor or no mobile reception. Three sections — Rules Quiz, Rules Viewer, Signals Quiz — must all load and work offline.

Strategy: cache-first service worker that precaches all 35 assets on install, with a "new version available" banner when a new service worker is waiting.

(see origin: planning/brainstorms/2026-03-25-offline-pwa-requirements.md)

---

## Requirements Trace

| ID | Requirement | Implementation Unit |
|----|-------------|---------------------|
| R1 | All three sections work fully offline after first visit | Unit 2 (SW precache) |
| R2 | All 35 assets pre-cached on first connected visit | Unit 2 (precache list) |
| R3 | Non-intrusive "new version" banner on next online visit after deploy | Unit 3 (SW registration + banner) |
| R4 | App installable to home screen | Unit 1 (manifest.json) |
| R5 | With cached version and no banner shown, behaves exactly as if online | Unit 2 (cache-first strategy) |

---

## Implementation Units

### Unit 1 — Web App Manifest

**Goal:** Make the app installable to iPhone/Android home screen.

**Files:**
- `docs/manifest.json` ← create

**Approach:**
Create a minimal Web App Manifest. The icons (`apple-touch-icon.png`, `favicon-32.png`) already exist — reference them. Set `start_url` to `/CanoePoloRules/` and `scope` to `/CanoePoloRules/`. Use `"display": "standalone"` so it opens without browser chrome.

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

Add `<link rel="manifest" href="manifest.json">` to all three HTML pages (`index.html`, `rules.html`, `signals.html`). The `<meta name="theme-color">` and `<meta name="apple-mobile-web-app-capable">` tags can also be added to `shared.css`-included pages at this time.

**Verification:** Chrome DevTools → Application → Manifest shows name, icons, and installable status. "Add to Home Screen" prompt appears on Android Chrome after second visit.

---

### Unit 2 — Service Worker

**Goal:** Cache-first service worker that precaches all 35 assets on install; serves from cache when offline.

**Files:**
- `docs/sw.js` ← create

**Approach:**

```js
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
  '/CanoePoloRules/favicon.svg',
  '/CanoePoloRules/favicon-32.png',
  '/CanoePoloRules/apple-touch-icon.png',
  '/CanoePoloRules/manifest.json',
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
```

**Lifecycle events:**

- `install`: `cache.addAll(ASSETS)` — fetches and caches all assets. Call `self.skipWaiting()` is NOT used here — we want the new SW to wait so the "new version" banner can appear.
- `activate`: Delete all caches whose name doesn't match `CACHE_NAME`. Call `clients.claim()` so the new SW controls existing tabs.
- `fetch`: Cache-first. Return cached response if found; otherwise fetch from network (and optionally cache the response for navigations).
- `message`: Listen for `{ type: 'SKIP_WAITING' }` message from the page. When received, call `self.skipWaiting()` to activate the new SW.

**Update detection (postMessage to page):**
In the `install` event, after caching, notify clients that a new version is ready:
```js
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});
```

The page-side update detection uses `ServiceWorkerRegistration.onupdatefound` / `installing.onstatechange` (see Unit 3).

**Verification:** With DevTools → Application → Service Workers, confirm SW installs and activates. Network throttled to "Offline" — all three pages load fully with no network requests.

---

### Unit 3 — SW Registration + Update Banner

**Goal:** Register the service worker in all three HTML pages. Show a non-intrusive "New version available — tap to reload" banner when a new SW is waiting.

**Files:**
- `docs/index.html` ← add manifest link + SW registration script
- `docs/rules.html` ← add manifest link + SW registration script
- `docs/signals.html` ← add manifest link + SW registration script
- `docs/shared.css` ← add update banner styles

**Approach — HTML changes (same in all three pages):**

In `<head>`:
```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#005b8e">
<meta name="apple-mobile-web-app-capable" content="yes">
```

Before `</body>`:
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
      if (reg && reg.waiting) {
        reg.waiting.postMessage({ type: 'SKIP_WAITING' });
      }
    });
    window.location.reload();
  });
}
</script>
```

**Approach — CSS (add to `shared.css`):**

```css
/* ── SW Update Banner ── */
#swUpdateBanner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  z-index: 9999;
}

#swUpdateBanner[hidden] { display: none; }

#swUpdateReload {
  background: #fff;
  color: var(--color-primary);
  border: none;
  border-radius: 4px;
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}
```

**Verification:** Deploy a change, then visit the app while online. The "New version available" banner appears at the bottom. Clicking "Reload" activates the new SW and the banner disappears. Visiting in Airplane Mode after one connected visit loads all three sections normally with no errors.

---

## Scope Boundaries

- No push notifications or background sync (see origin)
- No offline indicator in the UI — the app simply works
- No IndexedDB or user data persistence
- `CACHE_VERSION` must be bumped on every deploy — this is the only required maintenance step

## Key Maintenance Note

**Every deploy:** bump `CACHE_VERSION` in `docs/sw.js` (e.g., `'v1'` → `'v2'`). Without this, phones cache the old SW indefinitely and never see the "new version" banner.

## Dependencies / Assumptions

- GitHub Pages serves at `https://anobleperson.github.io/CanoePoloRules/` — all cached paths use `/CanoePoloRules/` prefix (see origin)
- GitHub Pages is already HTTPS — required for Service Worker registration
- `manifest.json` is added as part of Unit 1 and must appear in Unit 2's ASSETS list

## Sources

- **Origin document:** [planning/brainstorms/2026-03-25-offline-pwa-requirements.md](../brainstorms/2026-03-25-offline-pwa-requirements.md)
  - Key decisions carried forward: precache-all strategy (~1.5 MB), banner update flow, CACHE_VERSION maintenance
- MDN Service Worker API: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- MDN Web App Manifest: https://developer.mozilla.org/en-US/docs/Web/Manifest
