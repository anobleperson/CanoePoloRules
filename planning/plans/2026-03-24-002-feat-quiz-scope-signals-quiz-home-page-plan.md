---
title: "feat: Quiz Scope Update, Signals Quiz & Home Page"
type: feat
status: active
date: 2026-03-24
origin: planning/brainstorms/2026-03-24-quiz-scope-and-signals-quiz-requirements.md
---

# feat: Quiz Scope Update, Signals Quiz & Home Page

## Overview

Update the Rules Quiz chapter scope (remove ch7, add ch17.4/17.5), add Chapter 17 to the Rules Viewer, build a new image-based Signals Quiz, and replace the single-entry start screen with a three-panel home page giving equal prominence to all three modes.

## Origin Document

Source: `planning/brainstorms/2026-03-24-quiz-scope-and-signals-quiz-requirements.md`

Key decisions carried forward:
- Runtime filter for ch7 (not deletion) — preserves questions.json for future use
- Signals Quiz is a separate, lightweight implementation (not reuse of quiz engine)
- Three-panel home page replaces the current single-button start card

## Deferred Questions Resolved

- **R1 (ch7 removal)**: Delete all 27 chapter 7 questions from `questions.json` directly. Simpler and cleaner.
- **R4 (Signals engine)**: New `signals.html` + `signals.js` files. Reuse `shared.css` and `quiz.css` for visual consistency; no new stylesheet needed.
- **R5 (distractors)**: Pick 3 randomly from the other 19 signals. Simple and sufficient for now.
- **R2 (ch17 parsing)**: Chapter 17 uses `## **17.N - TITLE**` headings — already matched by the existing `SECTION_HEADING_RE`. Only `CHAPTERS_IN_SCOPE` and `CHAPTER_TITLES` need updating in `parse_rules.py`.

## Implementation Units

### Unit 1 — Remove Chapter 7 Questions from questions.json

**Goal:** Chapter 7 questions are deleted from `questions.json` so they no longer appear in the Rules Quiz.

**Files:**
- `docs/questions.json`
- `docs/index.html` (subtitle text update)

**Approach:**
Delete all question objects with `"chapter": 7` from `questions.json` (there are 27 of them). The pool shrinks from 205 to 178 questions.

Also update the start screen subtitle text in `index.html` to remove "Chapters 7 to 11" and replace with "Chapters 8–11 and 17".

**Patterns to follow:** existing question objects in `docs/questions.json`

**Verification:** Run `python3 scripts/validate_questions.py`. Grep confirms no `"chapter": 7` entries remain. Total question count is 178.

---

### Unit 2 — Add Chapter 17 to Rules Viewer

**Goal:** All of Chapter 17 (Shot Clock, sections 17.1–17.5) appears in the Rules Viewer sidebar and content.

**Files:**
- `scripts/parse_rules.py`
- `docs/rules.json` (regenerated)

**Approach:**
1. In `parse_rules.py`, add `17` to `CHAPTERS_IN_SCOPE` and add to `CHAPTER_TITLES`:
   ```python
   CHAPTERS_IN_SCOPE = {7, 8, 9, 10, 11, 15, 17}
   CHAPTER_TITLES = {
       ...
       17: "Shot Clock",
   }
   ```
2. Run `python3 scripts/parse_rules.py` to regenerate `docs/rules.json`.
3. Verify `rules.json` contains a chapter 17 entry with 5 sections (17.1–17.5).

**Note:** `max(CHAPTERS_IN_SCOPE)` will now be 17, so any chapter number > 17 correctly halts parsing. Chapter 17 uses `## **17.N - TITLE**` format — matched by existing `SECTION_HEADING_RE`.

**Patterns to follow:** `scripts/parse_rules.py:21-30` (CHAPTERS_IN_SCOPE / CHAPTER_TITLES)

**Verification:** Open `rules.html` locally; Chapter 17 — Shot Clock appears in the sidebar with 5 sections. Each section expands to show rule text.

---

### Unit 3 — Add Chapter 17 Questions and Fill Coverage Gaps

**Goal:** At least 1 question per numbered sub-item in 17.4 and 17.5 (17.4 has 3 sub-items → 3+ questions; 17.5 has 7 sub-items → 7+ questions, totalling 10+ new ch17 questions). Also audit all other in-scope chapters (8–11) and fill any numbered rule/sub-rule that currently has zero questions.

**Files:**
- `docs/questions.json`
- `docs/rules.json` (read-only, source material)

**Approach:**

**Part A — Chapter 17 questions:**
Read ch17 sections from `rules.json` for source text. Write at least 1 question per numbered sub-item:
- 17.4.1, 17.4.2, 17.4.3 (Shot Clock Expiry sub-rules) → 3+ questions, each with `"rule": "17.4.1"` etc.
- 17.5.1 through 17.5.7 (Shot Clock Reset sub-rules) → 7+ questions

Schema for each:
```json
{
  "chapter": 17,
  "rule": "17.4.1",
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correctIndex": 0,
  "explanation": "..."
}
```

**Part B — Coverage audit (ch8–11):**
For each section in `rules.json` chapters 8–11, cross-reference against `questions.json`. Identify any numbered rule or sub-rule (e.g. `10.12.1`) with zero questions. Write at least 1 question for each gap found.

Read `rules.json` section IDs and text → build a set of covered rule IDs from `questions.json` → write questions for uncovered IDs.

**Patterns to follow:** Any ch10 question block in `docs/questions.json` for JSON schema

**Verification:** Run `python3 scripts/validate_questions.py`. Every section ID in ch8–11 and ch17.4/17.5 has at least one matching `"rule"` entry in `questions.json`.

---

### Unit 4 — New Signals Quiz Page

**Goal:** `signals.html` presents all 20 referee hand signals in random order, shows the signal photo, and asks the user to name the signal from 4 options (signal names).

**Files:**
- `docs/signals.html` (new)
- `docs/signals.js` (new)

**Approach:**

`signals.html` structure mirrors `index.html` / `rules.html`:
- Same `<head>` with shared.css + quiz.css, favicon tags, site-header with nav
- Nav links: Quiz (index.html), Signals Quiz (signals.html, active), Rules (rules.html)
- Three screens inside `<main class="quiz-main">`:
  - `#sigStart` — title card with "Signal Recognition Quiz", brief description, Start button
  - `#sigQuestion` — progress bar, signal image (`<img>`), 4 option buttons (signal names only, no letter prefix needed — or keep A/B/C/D for consistency)
  - `#sigEnd` — score display + Try Again + Back to Home buttons

`signals.js` logic:
1. Load `rules.json` via `fetch('rules.json')`
2. Extract ch15 sections — these are the 20 signals. Each section has `id` (e.g. `"15.3"`), `heading` (signal name), and `text` (contains `IMAGE:filename` token + description text).
3. Parse each section to extract: `imageFile` (from `IMAGE:filename` token), `name` (from `heading`), `description` (remaining text lines).
4. Shuffle the 20 signals for the session.
5. For each signal, build 4 options: correct signal name + 3 random other signal names.
6. Show signal image; player picks a name. Immediate visual feedback (correct/incorrect button highlight) then show feedback panel with signal name + description.
7. After all 20, show end screen with score.

Key functions:
- `parseSignals(rulesData)` — extracts signal objects from ch15 chapter
- `buildOptions(signals, correctIndex)` — returns 4 shuffled name options
- `showSignal(index)` — renders image + options
- `showFeedback(isCorrect, signal)` — shows result + description
- `showEnd()` — score display

**Patterns to follow:**
- `docs/quiz.js` — overall screen flow, shuffle, buildSession patterns
- `docs/rules.js:141-148` — IMAGE: token parsing pattern
- `docs/index.html` — HTML structure, card layout, screen divs

**Verification:**
- Open `signals.html`; Start button loads signals from rules.json.
- All 20 signals appear (one per question), each with its photo.
- Options are signal names; correct answer is always one of the 4.
- After all 20, end screen shows score (e.g. "17 / 20").
- Feedback shows signal description after answering.

---

### Unit 5 — Three-Panel Home Page

**Goal:** `index.html` start screen shows three mode cards: View Rules, Rules Quiz, Signals Quiz. Each is immediately clickable and self-explanatory.

**Files:**
- `docs/index.html`
- `docs/quiz.css` (minor additions for home panel layout if needed)

**Approach:**

Replace the `#screenStart` card content with a three-panel layout:

```html
<div id="screenStart" class="screen screen-home">
  <h1 class="home-title">ICF 2025 Canoe Polo Rules</h1>
  <p class="home-subtitle">Prepare for your referee exam</p>
  <div class="home-panels">
    <a href="rules.html" class="home-panel">
      <div class="panel-icon">&#128218;</div>
      <h2>View Rules</h2>
      <p>Browse all chapters with collapsible sections and deep links.</p>
    </a>
    <div class="home-panel home-panel-primary" id="panelQuiz">
      <div class="panel-icon">&#10003;</div>
      <h2>Rules Quiz</h2>
      <p>20 random questions from Chapters 8–11 and 17. Immediate feedback.</p>
      <button class="btn btn-primary btn-lg" id="btnStart">Start Quiz</button>
    </div>
    <a href="signals.html" class="home-panel">
      <div class="panel-icon">&#128075;</div>
      <h2>Signals Quiz</h2>
      <p>Recognise all 20 referee hand signals from photos.</p>
    </a>
  </div>
</div>
```

The Rules Quiz panel stays in-page (same quiz screens flow). The other two panels are `<a>` links.

CSS additions to `quiz.css`:
- `.screen-home` — centred layout, max-width wider than current card
- `.home-panels` — `display: flex; gap: 1.5rem; flex-wrap: wrap; justify-content: center`
- `.home-panel` — card styling, flex column, min-width ~260px
- `.home-panel-primary` — slight border highlight (use `var(--color-primary)`)
- Mobile: panels stack vertically

Keep the existing `#screenQuestion`, `#screenFeedback`, `#screenEnd` screens and all quiz.js logic intact — only the start screen changes.

Update nav `<a href="index.html" class="active">Quiz</a>` to read "Home" (or keep "Quiz" — implementation judgement call, keep it simple).

**Patterns to follow:**
- `docs/quiz.css` — existing card, btn, screen styles
- `docs/shared.css` — CSS custom properties

**Verification:**
- `index.html` loads; three panels visible side-by-side on desktop, stacked on mobile.
- "View Rules" links to `rules.html`.
- "Signals Quiz" links to `signals.html`.
- "Start Quiz" button in Rules Quiz panel launches the quiz flow as before.
- Ch7 questions absent from quiz (Unit 1 already applied).

---

## Acceptance Criteria

- [ ] Rules Quiz sessions never contain chapter 7 questions (R1)
- [ ] Rules Viewer sidebar shows Chapter 17 — Shot Clock with sections 17.1–17.5 (R2)
- [ ] Rules Quiz has at least 1 question per numbered sub-item in 17.4 (3 sub-items) and 17.5 (7 sub-items) (R3)
- [ ] Every numbered rule/sub-rule in chapters 8–11 has at least 1 question in `questions.json`
- [ ] `signals.html` presents all 20 signals in random order with photos (R4)
- [ ] Signal options are signal names; 3 distractors are randomly drawn from the other 19 signals (R5)
- [ ] Home page shows three panels: View Rules, Rules Quiz, Signals Quiz (R6)
- [ ] Text-based ch15 questions still appear in the Rules Quiz (R7)
- [ ] Signals Quiz feedback shows the signal description text (R8)
- [ ] Signals Quiz end screen shows score out of 20 (R9)

## Dependencies

- Unit 2 must complete before Unit 3 can be verified (need ch17 text to write questions)
- Unit 4 depends on `rules.json` ch15 data (already present; no blocker)
- Unit 5 can be developed in parallel with Units 1–4

## Risks

- Chapter 17 markdown may have formatting quirks — verify `rules.json` ch17 output after regeneration before writing questions
- Signal images must be present in `docs/images/` — they were copied in the previous session; confirm 20 images exist matching the `IMAGE:filename` tokens in ch15 sections

## Sources & References

- **Origin document:** [planning/brainstorms/2026-03-24-quiz-scope-and-signals-quiz-requirements.md](planning/brainstorms/2026-03-24-quiz-scope-and-signals-quiz-requirements.md)
- `scripts/parse_rules.py:21-30` — CHAPTERS_IN_SCOPE / CHAPTER_TITLES
- `docs/quiz.js:38-55` — startQuiz / buildSession patterns
- `docs/rules.js:141-148` — IMAGE: token rendering
- `docs/index.html` — HTML structure to mirror in signals.html
- `docs/quiz.css` — styles to extend for home panels
