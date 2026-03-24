---
title: Null reference TypeError silently aborts a fetch promise chain
category: runtime-errors
date: 2026-03-24
tags: [javascript, promise, fetch, null-reference, async]
---

## Problem

After a successful `fetch()` + `JSON.parse`, the second `.then()` callback (which built the page content) never ran. The page showed a permanent loading state with no error visible to the user.

**Symptom:** First `.then()` completed (nav was built), but second `.then()` (content build) never executed. No console error was surfaced because the catch handler itself referenced a null element.

## Root Cause

Inside `buildNav()`, the code called `document.getElementById('navLoading').remove()` **after** it had already cleared the nav container with `nav.innerHTML = ''`. Clearing innerHTML removed `#navLoading` from the DOM, so the subsequent `.remove()` call returned `null` and threw:

```
TypeError: Cannot read properties of null (reading 'remove')
```

This TypeError propagated up through the `.then()` chain and was caught by `.catch()`. But the catch handler also referenced `#navLoading` (now removed), causing a second null reference that swallowed the error silently.

```js
// BEFORE — double-remove caused TypeError aborting the chain
function buildNav(chapters) {
  nav.innerHTML = '';         // removes #navLoading from DOM
  // ...build nav...
  document.getElementById('navLoading').remove(); // ← null, throws TypeError
}
```

## Solution

Remove the redundant `.remove()` call — `innerHTML = ''` already cleared the element. Add null guards in the catch handler:

```js
// AFTER
function buildNav(chapters) {
  nav.innerHTML = '';  // #navLoading already gone, no further action needed
  // ...build nav...
}

// catch handler with null guards
.catch(err => {
  const navMsg = document.getElementById('navLoading');
  const contentMsg = document.getElementById('contentLoading');
  if (navMsg) navMsg.textContent = 'Error loading rules.';
  if (contentMsg) contentMsg.textContent = 'Could not load rules: ' + err.message;
});
```

## Prevention

- **Guard all DOM lookups in catch handlers** — if the error occurred during page setup, the elements you want to update may no longer exist.
- After clearing a container with `innerHTML = ''`, do not call `.remove()` on child elements that were inside it — they are already gone.
- Add a global `window.onerror` or unhandled-rejection listener during development to surface swallowed errors.
- When a `.then()` callback silently fails to run, add a `console.log` at the top of the callback to confirm whether it is entered — this immediately distinguishes "callback threw" from "callback never called".
