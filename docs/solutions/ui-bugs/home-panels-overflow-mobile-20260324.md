---
module: Home Page
date: 2026-03-24
problem_type: ui_bug
component: frontend_stimulus
symptoms:
  - "Three home page mode cards overflow the mobile viewport in portrait orientation"
  - "User must scroll to see all three options (View Rules, Rules Quiz, Signals Quiz)"
root_cause: config_error
resolution_type: code_fix
severity: low
tags: [mobile, css, home-page, flexbox, overflow]
---

# Troubleshooting: Home Page Panels Overflow Mobile Viewport

## Problem

On portrait mobile (≤600px), the three mode-selection cards on the home page stack vertically and collectively exceed the viewport height, requiring the user to scroll to see all three options. The layout used desktop-sized padding, icon sizes, and gap values with no mobile override.

## Environment

- Module: Home Page (`docs/index.html`, `docs/quiz.css`)
- Affected Component: `.home-panel`, `.home-panels`, `.screen-home`
- Date: 2026-03-24

## Symptoms

- On a 375px-wide phone, the three stacked cards plus title/subtitle exceeded ~800px total height
- Viewport usable height after header is ~615px on a typical phone
- All three panels were visible only after scrolling

## What Didn't Work

**Direct solution:** The problem was identified and fixed on the first attempt.

## Solution

Added a `@media (max-width: 600px)` block to `docs/quiz.css` targeting the home panel elements specifically:

```css
@media (max-width: 600px) {
  .screen-home {
    padding-top: 1rem;         /* was 2.5rem */
  }

  .home-title {
    font-size: 1.3rem;         /* was 1.6rem */
  }

  .home-subtitle {
    font-size: 0.9rem;
    margin-bottom: 1rem;       /* was 2rem */
  }

  .home-panels {
    gap: 0.5rem;               /* was 1.25rem */
  }

  .home-panel {
    padding: 0.875rem 1.25rem; /* was 1.75rem 1.5rem */
    max-width: 100%;
    flex: 1 1 100%;
    gap: 0.35rem;
  }

  .panel-icon {
    font-size: 1.5rem;         /* was 2rem */
    margin-bottom: 0;
  }

  .home-panel h2 {
    font-size: 1rem;           /* was 1.1rem */
  }

  .home-panel p {
    display: none;             /* descriptions hidden — titles are self-explanatory */
  }

  .home-panel .btn-lg {
    margin-top: 0.5rem;
    padding: 0.625rem 1.25rem;
    font-size: 0.9rem;
  }
}
```

## Why This Works

The combined vertical height of three cards at desktop sizing (padding 1.75rem top+bottom, 2rem icon, 2-line description, 2rem gaps) exceeded 800px — too tall for any phone viewport. Reducing padding, icon size, and gaps, and hiding the descriptions (which add ~40px per card but convey no essential information since the titles are self-explanatory) brought total height to ~400px, comfortably within any phone viewport.

The breakpoint of 600px catches all portrait phones without affecting landscape or tablet layouts.

## Prevention

- When designing home/landing pages with vertically stacked cards, always estimate total mobile height: `(padding × 2 + icon + heading + description + gaps) × card_count + page_chrome`.
- A description paragraph (~40px per card × 3 cards) is often the biggest win to hide on mobile — titles should be self-sufficient.
- Desktop panel layouts (flex-wrap, max-width constraints) should always have an explicit `≤600px` override block.

## Related Issues

No related issues documented yet.
