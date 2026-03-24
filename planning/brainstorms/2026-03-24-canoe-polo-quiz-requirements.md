---
date: 2026-03-24
topic: canoe-polo-quiz
status: implemented
---

# Canoe Polo Rules Quiz App

## Problem Frame

Referees learning or refreshing the 2025 ICF Canoe Polo Competition Rules have no interactive tool to test their knowledge. The source material (rules + clarifications) has been extracted to markdown. We need a self-study quiz app that referees can use to practise rule knowledge, drawing on that extracted content.

## Requirements

- R1. The app is a static web app deployable to GitHub Pages — no backend, no runtime API calls. ✓
- R2. The question bank is a pre-generated JSON file (produced offline by an AI-assisted generation script) bundled with the app. ✓
- R3. The question bank covers all rules in chapters 7–11 inclusive plus Chapter 15 (Referee Hand Signals), with a minimum of 2 questions per rule/sub-rule; complex rules may have 4 or more questions. ✓ (205 questions total)
- R4. Each question is multiple-choice with exactly 4 options and one correct answer. ✓
- R5. Questions may optionally reference one of the extracted rule diagrams/images. ✓ (38 questions include images, especially Chapter 15 signal photos)
- R6. Each question includes a rule citation (e.g. "Rule 10.8.1") and a short explanation of the correct answer. ✓
- R7. Each quiz session presents 20 questions selected randomly from the full bank. ✓
- R8. After the user selects an answer, immediate feedback is shown: correct/incorrect, the rule citation, and the explanation. The correct answer is highlighted for longer (1.2s) when the user is wrong to aid learning. ✓
- R9. At the end of a session the user sees their score and can start a new session. ✓
- R10. The app works on both desktop and mobile browsers. ✓
- R11. The app has a Rules Viewer with collapsible chapter/rule navigation for all covered chapters, deep-linkable via URL hash (e.g. `rules.html#10.22.3`). ✓
- R12. The Rules Viewer includes Chapter 15 (Referee Hand Signals) with signal images rendered inline. ✓
- R13. Signal references in rule text (e.g. "Signal 8") are auto-linked to the corresponding entry in Chapter 15. ✓
- R14. The Rules Viewer includes a Rule Clarifications chapter (Sprint Starts, Defender's Paddle, Illegal Hand Tackle) drawn from the ICF clarifications document. ✓
- R15. Expanding a rule section in the viewer updates the browser URL hash, so the browser back button returns to that rule after following a link (e.g. clicking a Signal link). ✓

## Success Criteria

- A referee can complete a practice quiz session without any account, install, or internet-dependent runtime calls. ✓
- Questions cover all chapters 7–11 and Chapter 15 rules with no obvious gaps. ✓
- Immediate feedback correctly cites the rule and gives a useful explanation. ✓
- The app is usable on a phone screen (referees may use it poolside). ✓
- Live at https://anobleperson.github.io/CanoePoloRules/ ✓

## Scope Boundaries

- No user accounts, progress tracking, or persistent history.
- No formal certification or graded scoring stored anywhere.
- Question generation is an offline dev task, not an in-app feature.
- Chapters 1–6, 12–14, and 16+ are out of scope for question coverage (Chapter 15 was added in scope).
- No multiplayer or team quiz modes.

## Key Decisions

- **Static GitHub Pages delivery**: Chosen for zero hosting cost and zero backend complexity. Deployed from `/docs` folder on `main` branch.
- **Pre-generated question bank**: Questions are generated once (offline with AI assistance) and committed as JSON — avoids runtime API costs and works fully offline after first load.
- **Images included**: The rule diagram images are already extracted; Chapter 15 signal photos are served from `docs/images/` and shown inline in both the Rules Viewer and quiz questions.
- **Immediate feedback**: Better for learning than end-of-quiz review; referees need to understand the rule in context of the question. Wrong-answer delay extended to 1.2s so the correct button registers before feedback card appears.
- **Plain HTML/CSS/JS, no build step**: Chosen for simplicity and zero toolchain overhead. Local dev via `python3 -m http.server 8080`.
- **`[hidden] { display: none !important }`**: Required in shared CSS to prevent CSS `display` rules from overriding the HTML `hidden` attribute on quiz screens.
- **`###` heading pattern for Chapter 15**: Chapter 15 uses a different markdown heading style (`### 15.N TITLE`) than chapters 7–11 (`## **N.N - TITLE**`); the parser handles both.
- **`IMAGE:filename` token in rules.json**: Chapter 15 image paths are stored as `IMAGE:filename` tokens in rule text and rendered as `<img>` tags by the viewer JS; chapters 7–11 strip images.
- **Signal auto-linking**: Rule text containing "Signal N" / "Signals N and M" is automatically converted to anchor links pointing to `#15.N` in the viewer.
- **`history.pushState` on rule expand**: Expanding a rule section pushes its hash to browser history without scrolling, enabling back-button navigation after following signal links.

## Dependencies / Assumptions

- The `rules_extract/` markdown files are the authoritative source for rules and question generation.
- The `rules_extract/images/` directory contains diagram images; Chapter 15 images are copied to `docs/images/` at build time.
- Image paths in questions must be relative and compatible with GitHub Pages hosting.
- `parse_rules.py` regenerates `docs/rules.json` whenever the source markdown changes; run manually.

## Resolved Questions

- **Question bank schema**: `[{id, source, chapter, rule, question, options[], correctIndex, explanation, image}]`, validated by `scripts/validate_questions.py`.
- **Useful images for questions**: Chapter 15 signal photos (all 20 signals) and rule diagrams already extracted in `rules_extract/images/`.
- **Tech stack**: Plain HTML/CSS/vanilla JS with no build step.
- **Total question count**: 205 questions across chapters 7–11, 15, and clarifications.
