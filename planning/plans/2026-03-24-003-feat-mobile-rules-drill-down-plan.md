---
title: "feat: Mobile Rules Viewer — Drill-Down Navigation"
type: feat
status: active
date: 2026-03-24
origin: planning/brainstorms/2026-03-24-mobile-rules-viewer-requirements.md
---

# feat: Mobile Rules Viewer — Drill-Down Navigation

## Overview

Replace the collapsible-sidebar mobile layout in the Rules Viewer with a three-screen drill-down: chapter list → section list → rule text. Desktop layout (sidebar + content) is completely unchanged. URL hash deep-links continue to work on mobile.

## Origin Document

Source: `planning/brainstorms/2026-03-24-mobile-rules-viewer-requirements.md`

Key decisions carried forward:
- Drill-down (not accordion, not bottom sheet) — matches the chapter-first mental model of the primary user (see origin: brainstorms/2026-03-24-mobile-rules-viewer-requirements.md)
- Desktop layout (`> 768px`) is completely untouched
- Hash deep-links (`rules.html#10.22`) bypass the drill-down and go directly to rule text on mobile

## Current State

On mobile (≤ 768px) today:
- The sidebar stacks above the content
- A hamburger toggle shows/hides the chapter nav (up to 60vh)
- Clicking a section link closes the sidebar and scrolls to the rule
- Pain: two-step nav with context switching in a small vertical space, requires scrolling past the sidebar

## Implementation Units

### Unit 1 — Add mobile drill-down HTML structure

**Goal:** Add the three-screen mobile container to `rules.html`, hidden by default on desktop.

**Files:**
- `docs/rules.html`

**Approach:**
Add a `<div id="mobileView">` block inside `<body>` (after the existing `<main class="rules-main">`):

```html
<!-- Mobile drill-down (shown only on portrait mobile via CSS) -->
<div id="mobileView" hidden>
  <div id="mobileChapterList"></div>
  <div id="mobileSectionList" hidden>
    <button class="mobile-back-btn" id="mobileBackToChapters">
      &#8592; Chapters
    </button>
    <h2 class="mobile-chapter-heading" id="mobileChapterHeading"></h2>
    <ul class="mobile-section-list" id="mobileSectionItems"></ul>
  </div>
  <div id="mobileRuleView" hidden>
    <button class="mobile-back-btn" id="mobileBackToSections">
      &#8592; <span id="mobileBackChapterName"></span>
    </button>
    <div id="mobileRuleContent"></div>
  </div>
</div>
```

**Patterns to follow:** `docs/rules.html:25-40` (existing main layout structure)

**Verification:** HTML is valid, `#mobileView` exists in the DOM. Desktop view is unaffected (hidden by default, CSS will show it on mobile).

---

### Unit 2 — CSS: show mobile view on portrait, hide desktop layout

**Goal:** On ≤ 768px, show `#mobileView` and hide `.rules-main`. On > 768px, vice versa.

**Files:**
- `docs/rules.css`

**Approach:**
Replace the current `@media (max-width: 768px)` block that adapts the sidebar (around `rules.css:282-313`) with one that hides the desktop layout entirely and reveals the mobile view:

```css
/* Remove or replace the existing mobile sidebar rules */
@media (max-width: 768px) {
  .rules-main {
    display: none;
  }

  #mobileView {
    display: block;
    padding: 0 0 3rem;
  }
}

/* Desktop: keep mobileView hidden */
@media (min-width: 769px) {
  #mobileView {
    display: none !important;
  }
}
```

Also add styles for the mobile drill-down UI:

```css
/* Mobile chapter cards */
.mobile-chapter-card { ... }  /* tappable card, full-width, padding, border */
.mobile-chapter-card:active { ... }  /* tap feedback */

/* Mobile section list */
.mobile-section-list { list-style: none; }
.mobile-section-item { ... }  /* full-width, padding, border-bottom */

/* Back button */
.mobile-back-btn { ... }  /* left-aligned, primary colour, padding */

/* Mobile chapter/section headings */
.mobile-chapter-heading { ... }
.mobile-rule-content { ... }  /* padding, font sizes matching .rule-body */
```

**Patterns to follow:**
- `docs/rules.css:282-327` (existing mobile block to replace)
- `docs/shared.css:9-26` (CSS custom properties to reuse)
- `docs/rules.css:165-230` (existing rule card/body styles to mirror in mobile view)

**Verification:** On a 375px-wide viewport, desktop layout is hidden and `#mobileView` is visible. On 1024px, `#mobileView` is hidden and desktop layout is visible.

---

### Unit 3 — JS: build and drive the mobile drill-down

**Goal:** When on mobile, build the chapter list UI and handle the three-screen transitions.

**Files:**
- `docs/rules.js`

**Approach:**

After `rulesData` loads (inside the existing `.then(data => { ... })` block), add a call to `initMobileView(data)` alongside the existing `buildNav(data)` and `buildContent(data)` calls.

```javascript
// Detect mobile at runtime (matches CSS breakpoint)
function isMobile() {
  return window.innerWidth <= 768;
}
```

`initMobileView(data)`:
1. Show `#mobileView` (remove `hidden`)
2. Build chapter list: for each chapter, create a `<button class="mobile-chapter-card">` showing the chapter title. On click → `showSectionList(chapter)`.

`showSectionList(chapter)`:
1. Hide `#mobileChapterList`, show `#mobileSectionList`
2. Populate `#mobileChapterHeading` with chapter title
3. Populate `#mobileSectionItems` with `<li>` buttons for each section (id + heading). On click → `showRuleView(section, chapter)`.
4. Set `#mobileBackToChapters` onclick → `showChapterList()`

`showRuleView(section, chapter)`:
1. Hide `#mobileSectionList`, show `#mobileRuleView`
2. Render the rule content into `#mobileRuleContent` — reuse `buildRuleSection(section)` and open it immediately
3. Set `#mobileBackToSections` / `#mobileBackChapterName` for back navigation → `showSectionList(chapter)`
4. Push hash: `history.pushState(null, '', '#' + section.id)` (matches existing desktop behaviour at `rules.js:173`)

`showChapterList()`:
1. Show `#mobileChapterList`, hide others

**Hash deep-link on mobile** (`handleHash()` already exists at `rules.js:189`):
After the existing hash handling, add:
```javascript
if (isMobile() && hash) {
  // find which chapter this rule belongs to, navigate drill-down directly to rule view
  const chapter = rulesData.find(ch => ch.sections.some(s => s.id === hash));
  const section = chapter && chapter.sections.find(s => s.id === hash);
  if (chapter && section) showRuleView(section, chapter);
}
```

**Patterns to follow:**
- `docs/rules.js:38-88` (`buildNav`) — chapter/section iteration pattern
- `docs/rules.js:118-185` (`buildRuleSection`) — reuse this function for rule text rendering
- `docs/rules.js:167-176` — `history.pushState` pattern
- `docs/rules.js:189-215` — `handleHash` to extend

**Verification:**
- On mobile, tapping a chapter shows its section list
- Tapping a section shows the rule text, expanded
- Back buttons return to the correct previous screen
- `rules.html#10.22` opened on mobile goes directly to that rule's text
- All 8 chapters and their sections are accessible

---

## Acceptance Criteria

- [ ] On mobile (≤ 768px portrait), `.rules-main` (sidebar + content) is hidden; `#mobileView` is shown (R1)
- [ ] Chapter list fills the screen with one card per chapter (R2)
- [ ] Tapping a chapter shows a full-width section list for that chapter with a back button (R3)
- [ ] Tapping a section shows the rule text, expanded, with a back button (R4)
- [ ] Back buttons return to the correct level (R5)
- [ ] Desktop layout (> 768px) is pixel-identical to current (R6)
- [ ] Opening `rules.html#10.22` on mobile navigates directly to that rule's text (R7)
- [ ] The toggle sidebar button is no longer visible on mobile (it belongs to the desktop sidebar)

## Dependencies

- `buildRuleSection(section)` is reused in Unit 3 — read it carefully before implementation (`rules.js:118-185`)
- `linkSignals()` and `escHtml()` are used inside `buildRuleSection` — no changes needed
- The existing `handleHash()` is extended, not replaced

## Risks

- `window.innerWidth <= 768` is evaluated at load time; if user resizes the browser mid-session on desktop the mobile view could flash. Acceptable for now — this is a portrait phone optimisation, not a responsive resize feature.
- `buildRuleSection()` currently calls `history.pushState` on expand — on mobile this is preserved (it's useful for the back gesture to return to a specific rule).

## Sources & References

- **Origin document:** [planning/brainstorms/2026-03-24-mobile-rules-viewer-requirements.md](planning/brainstorms/2026-03-24-mobile-rules-viewer-requirements.md) — drill-down chosen for chapter-first mental model; desktop unchanged; hash deep-links preserved
- `docs/rules.js:38-88` — `buildNav()` — chapter/section iteration to mirror
- `docs/rules.js:118-185` — `buildRuleSection()` — reuse for rule text rendering
- `docs/rules.js:167-176` — `history.pushState` pattern
- `docs/rules.js:189-215` — `handleHash()` to extend for mobile
- `docs/rules.css:282-313` — existing mobile block to replace
- `docs/shared.css:9-26` — CSS custom properties to use in new mobile styles
