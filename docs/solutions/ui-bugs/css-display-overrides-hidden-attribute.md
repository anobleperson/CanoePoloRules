---
title: CSS display property overrides HTML hidden attribute
category: ui-bugs
date: 2026-03-24
tags: [css, html, hidden, display, specificity]
---

## Problem

Multiple screens/sections were visible simultaneously on page load, even though they had the HTML `hidden` attribute set. Only the first screen should be visible.

**Symptom:** All `<section hidden>` elements rendered as if `hidden` had no effect.

## Root Cause

CSS rules applied `display: flex` (or `display: block`) to elements via class selectors. The HTML `hidden` attribute sets `display: none` via the browser's default stylesheet, which has the **lowest possible specificity**. Any author-level CSS `display` rule overrides it — including rules like:

```css
/* This silently defeats the hidden attribute */
.screen-start {
  display: flex;
}
```

So `<section class="screen-start" hidden>` ended up displayed because the class rule won.

## Solution

Add a single rule to the global stylesheet that re-enforces `hidden` with `!important`:

```css
/* Ensure the hidden attribute always wins over display rules */
[hidden] {
  display: none !important;
}
```

Place this in the shared/global CSS file so it applies everywhere.

## Prevention

- Add `[hidden] { display: none !important }` to every project's base/reset stylesheet from day one.
- When toggling visibility in JS, prefer the `hidden` attribute (`el.hidden = true/false`) over manually setting `display` — but only after this rule is in place.
- If you see an element that "should be hidden" but isn't, check whether any CSS rule sets `display` on that element or its classes.
