---
title: "PWA Not Updating on iPhone Home Screen After Deploy"
category: runtime-errors
date: 2026-04-12
tags:
  - pwa
  - service-worker
  - cache
  - ios
  - safari
  - github-pages
  - offline
problem_type: stale-cache
---

## Problem

A Progressive Web App installed to an iPhone home screen continued serving stale cached content after new versions were deployed to GitHub Pages. The service worker's cache-first strategy prevented updated assets from being fetched, and the update banner (triggered via a `SKIP_WAITING` message) never appeared.

**Symptoms:**
- App launched from iPhone home screen shows outdated content after a deploy
- Update/reload banner does not appear in the app UI
- Force-closing and reopening the app does not fetch new content
- Deleting website data via Settings → Safari → Advanced → Website Data does not resolve the issue
- Problem persists across multiple open/close cycles

## Root Cause

`CACHE_VERSION` in `docs/sw.js` was never bumped between deploys. The cached `sw.js` on the device was byte-for-byte identical to what was on the server, so the browser had nothing new to install — no update check triggered, no banner appeared.

Critically, clearing Safari's Website Data does **not** unregister service workers on iOS. The service worker and its Cache Storage live in a separate partition from Safari's browsable site data. The existing service worker survived the wipe and continued serving everything from the stale `cp-rules-v1` cache.

## Solution

Bump `CACHE_VERSION` in `docs/sw.js`:

```js
// Before
const CACHE_VERSION = 'v1';

// After
const CACHE_VERSION = 'v2';
```

This single change ripples through the service worker lifecycle:

1. GitHub Pages serves the updated `sw.js`
2. The browser detects the byte difference and installs a new service worker alongside the old one
3. The new SW's `install` handler populates a fresh cache named `cp-rules-v2` with all current assets
4. The `activate` handler deletes every cache not matching `cp-rules-v2` (including stale `cp-rules-v1`)
5. The update banner fires, prompting the user to reload

The comment directly above the constant already warned about this:

```js
// IMPORTANT: Bump CACHE_VERSION on every deploy to invalidate old caches.
```

## iOS-Specific Gotchas

**Website Data deletion doesn't evict SW caches on iOS.** Unlike desktop Chrome/Firefox, clearing site data in iOS Settings leaves service worker registrations and their caches intact. The only reliable developer-side fix is bumping `CACHE_VERSION`.

**iOS updates service workers lazily.** A new SW may sit in "waiting" state until all tabs showing the app are closed and reopened. For a single-page quiz app with no cross-tab shared state, calling `self.skipWaiting()` in the `install` event is safe and avoids this delay.

**Home screen PWAs lag further.** Standalone mode (added to home screen) is even less aggressive about checking for SW updates than regular Safari browsing. This makes `CACHE_VERSION` bumps even more important than in a standard web context.

**SW file must not be cached aggressively.** GitHub Pages serves `sw.js` with a short TTL by default. If you ever migrate to a CDN, ensure `sw.js` is not given a long `Cache-Control` max-age, or the browser will never fetch the updated file.

## Prevention

**Bump `CACHE_VERSION` on every deploy where any cached asset changed.** This includes any HTML, JS, CSS, JSON, or image file listed in the `ASSETS` array in `sw.js`.

Deploy checklist:
- [ ] Did any file in `ASSETS` change? If yes, bump `CACHE_VERSION` before pushing
- [ ] Is `sw.js` itself listed in `ASSETS`? (It must not be — it should never cache itself)

When in doubt, bump it. The cost of an unnecessary bump is a one-time re-download for users. The cost of a missed bump is users permanently stranded on stale content.

**Automation option:** Replace the `CACHE_VERSION` constant with the current git commit hash in a deploy script:

```sh
GIT_HASH=$(git rev-parse --short HEAD)
sed -i '' "s/const CACHE_VERSION = '.*'/const CACHE_VERSION = '$GIT_HASH'/" docs/sw.js
```

This guarantees a unique version on every deploy with no manual step.

## Related

- [`docs/solutions/integration-issues/offline-pwa-service-worker-github-pages-20260325.md`](../integration-issues/offline-pwa-service-worker-github-pages-20260325.md) — Initial PWA setup with service worker, manifest, and update banner implementation
