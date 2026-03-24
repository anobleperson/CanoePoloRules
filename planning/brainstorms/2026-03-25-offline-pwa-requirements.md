---
date: 2026-03-25
topic: offline-pwa
---

# Offline Support (PWA)

## Problem Frame

Referees use this app at venues that may have no or poor mobile reception. Currently every page load and JSON fetch requires a network connection. Adding offline support means the full app — quiz, rules viewer, signals quiz — works after a single initial connected visit.

## Requirements

- R1. After one connected visit, all three sections (Rules Quiz, Rules Viewer, Signals Quiz) load and function fully without internet.
- R2. All 35 assets are pre-cached on first visit: HTML, JS, CSS, JSON data files, all 21 signal images, and the field-of-play diagram.
- R3. When a new version of the app is deployed and the user is online, a non-intrusive banner appears offering a reload to get the latest content.
- R4. The app is installable to the phone home screen (web app manifest + icons already present).
- R5. When offline with a cached version and no banner is shown, the app behaves exactly as if online — no error states.

## Success Criteria

- Opening the app in Airplane Mode (after one prior connected visit) loads all three sections without any network requests.
- Updating `questions.json` and deploying causes a "New version available" banner to appear on next visit with internet, and the updated questions are active after reload.
- The app can be added to iPhone/Android home screen and opens without browser chrome.

## Scope Boundaries

- No push notifications or background sync — purely a caching layer.
- No offline indication badge/icon in the UI — the app simply works.
- No user data to persist — all content is read-only, so no IndexedDB or sync needed.

## Key Decisions

- **Update strategy: "New version available" banner** — Referees need accurate rules; silently staying on a stale version risks quiz questions being out of date. A banner on next connected visit lets users choose when to reload.
- **Precache all assets on install** — The full asset set is only ~1.5 MB (dominated by 21 signal photos). Precaching everything is simpler than runtime caching and guarantees complete offline availability.
- **Cache versioning via a constant in the service worker** — Bumping a `CACHE_VERSION` string in `sw.js` on every deploy is the required maintenance step; without it, phones stay on stale cached versions indefinitely.

## Dependencies / Assumptions

- GitHub Pages serves the site at `https://anobleperson.github.io/CanoePoloRules/` — the service worker registration and all cached paths must use this prefix.
- GitHub Pages already serves over HTTPS, which is required for Service Worker registration.
- The `apple-touch-icon.png` and `favicon-32.png` already exist; a `manifest.json` is all that's needed for installability.

## Outstanding Questions

### Deferred to Planning

- [Affects R3][Technical] How should the "new version available" banner be styled and positioned? (small bottom banner, dismissible?)
- [Affects R2][Needs research] Confirm the exact GitHub Pages URL path prefix for `sw.js` registration (`./sw.js` from `index.html` should resolve correctly — verify during implementation).
- [Affects R1][Technical] Confirm `signals.css` is served via `shared.css`/`quiz.css` or identify if a separate file exists that needs caching.

## Next Steps

→ `/ce:plan` for structured implementation planning
