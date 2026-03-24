---
module: Rules Viewer (Mobile)
date: 2026-03-25
problem_type: ui_bug
component: frontend_stimulus
symptoms:
  - "Selecting a rule section on mobile showed the rule text with no heading, making it unclear what was selected"
  - "Back button in the rule view showed only 'Ch 10' instead of 'Ch 10 — Game Play'"
root_cause: logic_error
resolution_type: code_fix
severity: low
tags: [mobile, rules-viewer, drill-down, navigation, heading]
---

# Troubleshooting: Mobile Rule View Missing Section Title and Abbreviated Back Button

## Problem

In the mobile drill-down rules viewer, when a user tapped a section (e.g. rule 10.23), the rule text appeared with no visible title. The `.rule-header` is hidden on mobile via CSS (to avoid the toggle affordance), so users had no way to see which section they had navigated to. Additionally, the back button showed an abbreviated chapter reference ("Ch 10") rather than the full chapter name ("Ch 10 — Game Play").

## Environment

- Module: Rules Viewer (`docs/rules.html`, `docs/rules.js`)
- Affected Component: `#mobileRuleView`, `showMobileRule()`, `#mobileBackChapterName`
- Date: 2026-03-25

## Symptoms

- Rule content visible but no heading above it (`.rule-header` hidden by CSS: `display: none`)
- Back button text: "← Ch 10" — chapter title truncated
- Users couldn't identify which section they were reading without scrolling into the text

## What Didn't Work

**Direct solution:** Root cause identified immediately.

## Root Cause

Two separate omissions:

1. **Missing heading**: `#mobileRuleView`'s nav bar had only a back button — no heading element. The `.rule-header` inside `buildRuleSection()` is hidden on mobile via `.mobile-rule-content .rule-header { display: none }` (correct — avoids toggle confusion), but nothing else was showing the section title.

2. **Abbreviated back button**: `showMobileRule()` only used `'Ch ' + chapter.chapter` without `chapter.title`, producing "Ch 10" instead of "Ch 10 — Game Play".

## Solution

**`docs/rules.html`** — add a heading element to the rule view nav bar:

```html
<div id="mobileRuleView" hidden>
  <div class="mobile-nav-bar">
    <button class="mobile-back-btn" id="mobileBackToSections">&#8592; <span id="mobileBackChapterName"></span></button>
    <h2 class="mobile-chapter-heading" id="mobileRuleHeading"></h2>
  </div>
  <div id="mobileRuleContent" class="mobile-rule-content"></div>
</div>
```

**`docs/rules.js`** — populate both elements in `showMobileRule()`:

```js
// Back button: full chapter name
document.getElementById('mobileBackChapterName').textContent = typeof chapter.chapter === 'number'
  ? 'Ch ' + chapter.chapter + ' \u2014 ' + chapter.title
  : chapter.title;

// Section heading
document.getElementById('mobileRuleHeading').textContent = section.id + ' \u2014 ' + section.heading;
```

The existing `.mobile-chapter-heading` CSS class handles truncation with `text-overflow: ellipsis`, so long headings degrade gracefully.

## Why This Works

The `#mobileRuleHeading` element reuses the existing `.mobile-chapter-heading` style (already used in the section list nav bar), giving it the same truncation and font treatment for free. The full chapter title in the back button gives users a clear path back without ambiguity.

## Prevention

- When hiding a component's built-in header (e.g. `.rule-header { display: none }`), always ensure an equivalent heading is surfaced elsewhere in the layout — don't rely on content text to self-identify.
- Mobile nav bars should consistently show: back target (what you'll return to) + current context (where you are now).

## Related Issues

- See also: [home-panels-overflow-mobile-20260324.md](home-panels-overflow-mobile-20260324.md) — prior mobile layout fix in the same project
