---
date: 2026-03-24
topic: mobile-rules-viewer
---

# Mobile Rules Viewer — Drill-Down Navigation

## Problem Frame

On a phone in portrait mode the Rules Viewer is difficult to use. The current design puts a collapsible sidebar above the content; users must toggle it open, select a chapter, expand sections, click a link, close the sidebar, and then scroll to the content. For referees who typically start from a known chapter and browse its sections, this is too many steps in a narrow vertical space.

## Requirements

- R1. On mobile portrait (viewport ≤ 768px), the Rules Viewer shows a chapter-first drill-down instead of the sidebar + content layout.
- R2. The first screen shows all chapters as a full-width tappable list.
- R3. Tapping a chapter transitions to a full-width list of that chapter's sections (headings only).
- R4. Tapping a section shows the rule text for that section, full-width, expanded.
- R5. At each level a back control (button or browser back) returns to the previous screen.
- R6. The desktop layout (viewport > 768px) is completely unchanged.
- R7. Deep links via URL hash (`rules.html#10.22`) still work: opening a hash URL on mobile jumps directly to the rule text view for that section, bypassing the drill-down screens.

## Success Criteria

- A referee on a phone can reach any rule's text in at most 3 taps from the home screen.
- No toggle button or floating panel is needed on mobile.
- The desktop experience is unaffected.

## Scope Boundaries

- No search or filter functionality (separate feature if needed later).
- Landscape phone orientation is not specifically catered for — it may revert to the desktop layout at ≥ 769px width, which is acceptable.
- No swipe gestures required — tap-based navigation only.
- The signals quiz and rules quiz pages are out of scope.

## Key Decisions

- **Drill-down over accordion**: chosen because users start from a chapter, not from a desire to read linearly; a drill-down matches their chapter-first mental model.
- **Desktop layout unchanged**: avoids regression risk and maintains the side-by-side layout that works well on larger screens.
- **Hash deep-link preserved**: rule links from the quiz feedback screen must still work on mobile.

## Next Steps

→ `/ce:plan` for structured implementation planning
