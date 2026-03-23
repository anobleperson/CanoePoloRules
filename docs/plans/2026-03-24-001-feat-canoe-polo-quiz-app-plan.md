---
title: "feat: Canoe Polo Rules Quiz App"
type: feat
status: active
date: 2026-03-24
origin: docs/brainstorms/2026-03-24-canoe-polo-quiz-requirements.md
---

# feat: Canoe Polo Rules Quiz App

## Overview

Build a static GitHub Pages web app for canoe polo referees with two tools: (1) a multiple-choice **quiz** to test rule knowledge, and (2) a **rules viewer** with collapsible chapter/rule navigation and deep-linkable rule anchors. The project has three workstreams: an offline question bank generator, the quiz interface, and the rules viewer.

## Problem Statement

Referees learning or refreshing the 2025 ICF Canoe Polo rules have no interactive tool to test their knowledge. The source material has already been extracted to markdown and images in `rules_extract/`. What is missing is a quiz interface and a structured question bank drawn from that content.

See origin document for full problem framing: [docs/brainstorms/2026-03-24-canoe-polo-quiz-requirements.md](../brainstorms/2026-03-24-canoe-polo-quiz-requirements.md)

## Proposed Solution

Three deliverables built in sequence:

1. **Question bank generator** — a script (Python, run offline by the developer) that reads the extracted rules markdown, calls an LLM to generate questions, and writes a validated `docs/questions.json`.

2. **Rules viewer** — a static `docs/rules.html` page with a collapsible chapter/rule tree parsed from `rules_extract/` markdown, deep-linkable via URL hash (e.g. `rules.html#10.22.3`).

3. **Quiz web app** — `docs/index.html` + `docs/quiz.js` + `docs/style.css` (plain HTML/CSS/JS, no framework, no build step) served by GitHub Pages from `docs/`. Quiz feedback includes an optional "View Rule X" link that opens `rules.html` at the cited rule anchor.

## Technical Approach

### Architecture

```
RulesQuiz/
  rules_extract/
    images/                         ← source images (read-only)
    2025_icf_canoe_polo_rules.md    ← generation source
    2025_icf_canoe_polo_rule_clarifications.md  ← generation source
  scripts/
    generate_questions.py           ← offline LLM generation script
    validate_questions.py           ← validates schema of questions.json
    parse_rules.py                  ← parses markdown into rules.json for the viewer
  docs/                             ← GitHub Pages source root
    index.html                      ← quiz app
    quiz.js
    rules.html                      ← rules viewer
    rules.js
    shared.css                      ← shared base styles
    quiz.css
    rules.css
    questions.json                  ← pre-generated, committed to repo
    rules.json                      ← pre-parsed rules tree, committed to repo
    images/                         ← copy of relevant rule images for questions
  docs/brainstorms/
  docs/plans/
```

**GitHub Pages config:** Set Pages source to `docs/` directory on the `main` branch.

**Image strategy:** Only images actually referenced by questions are copied into `docs/images/` as part of the generation step. This avoids copying all 85+ images into the served directory unnecessarily.

### Question Bank JSON Schema

Every question in `questions.json` must conform to this schema:

```json
{
  "id": "ch10-r10.22.3.d-001",
  "source": "rules",
  "chapter": 10,
  "rule": "10.22.3.d",
  "question": "At what paddle angle relative to the water surface is a kayak tackle considered illegal?",
  "options": [
    "Between 30 and 60 degrees",
    "Between 60 and 80 degrees",
    "Between 80 and 100 degrees",
    "More than 100 degrees"
  ],
  "correctIndex": 2,
  "explanation": "Rule 10.22.3.d defines an illegal kayak tackle as one where the attacking paddle is between 80 and 100 degrees relative to the water surface.",
  "image": null
}
```

**Field definitions:**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier. Format: `ch{N}-r{rule}-{seq}` (e.g. `ch10-r10.22.3d-001`) or `clarif-{topic}-{seq}` for clarifications |
| `source` | `"rules"` \| `"clarification"` | yes | Which source document the question comes from |
| `chapter` | integer | yes | Chapter number (7–11). Use `0` for clarification-only questions with no chapter mapping |
| `rule` | string | yes | Rule number citation (e.g. `"10.22.3.d"`) or clarification topic (e.g. `"Illegal Hand Tackle"`) |
| `question` | string | yes | The question text. Target: under 200 characters |
| `options` | string[4] | yes | Exactly 4 answer strings, stored in a fixed order |
| `correctIndex` | 0–3 | yes | Index into `options` of the correct answer |
| `explanation` | string | yes | Short explanation of why the correct answer is correct, citing the rule |
| `image` | string \| null | yes | Relative path from `docs/` to an image file (e.g. `"images/page106_img1.png"`), or `null` |

**Display note:** The app will shuffle `options` on each question display for randomization. `correctIndex` always refers to the stored order, not the displayed order. The app tracks the mapping internally.

### Rules Viewer (`docs/rules.html`)

The rules viewer parses a pre-generated `docs/rules.json` (produced by `scripts/parse_rules.py`) and renders a collapsible tree of chapters and rules.

**`rules.json` structure:**

```json
[
  {
    "chapter": 7,
    "title": "Officials",
    "sections": [
      {
        "id": "7.1",
        "heading": "Competition Committee",
        "text": "The Competition Committee shall consist of...",
        "subsections": [
          { "id": "7.1.1", "text": "..." }
        ]
      }
    ]
  }
]
```

**Deep linking:** Each rule section gets an `id` attribute matching its rule number (e.g. `id="10.22.3"`). Navigating to `rules.html#10.22.3` auto-expands the parent chapter and scrolls to that section on page load.

**Navigation:** Left sidebar (or top accordion on mobile) lists chapter titles. Clicking a chapter expands/collapses its rules. Individual rule sections are collapsible.

**Quiz → rules linking:** In quiz feedback, after answering a question, an optional link appears: `"View Rule 10.22.3 →"` which opens `rules.html#10.22.3` in a new tab. The link is always present — whether the answer was right or wrong — but never auto-navigates.

**Search (deferred to v2):** Not in scope for initial build. The tree navigation is the MVP.

### App State Machine

The app has three views:

```
START ──[Begin Quiz]──► QUESTION (1 of 20)
                           │
                      [Select Answer]
                           │
                      QUESTION + FEEDBACK
                           │
                      [Next Question]
                           │
                     (repeat × 20)
                           │
                       END SCREEN
                           │
                    [New Session]──► QUESTION (1 of 20)
```

**START view:** Title, brief description, "Start Quiz" button. One-line note: "Your progress is not saved."

**QUESTION view:**
- Header: "Question N of 20 · Score: X"
- Optional image (if `image` field is non-null), max-width 100%
- Question text
- 4 answer buttons (options displayed in shuffled order)

**QUESTION + FEEDBACK view (after answer selected):**
- All 4 options remain visible but disabled
- Selected option highlighted: green if correct, red if incorrect
- If incorrect: the correct option is highlighted in green
- Below options: rule citation + explanation text
- "Next Question" button (or "See Results" on question 20)

**END SCREEN view:**
- "Quiz Complete!"
- Score: "14 / 20 — 70%"
- "Start New Session" button (draws a fresh random 20)

### Session Logic

```js
// On session start:
const session = shuffle(allQuestions).slice(0, 20)
let current = 0
let score = 0

// On answer:
const shuffledOptions = session[current]._shuffledOptions  // computed once per question on display
const selectedOriginalIndex = shuffledOptions[selectedDisplayIndex].originalIndex
const isCorrect = selectedOriginalIndex === session[current].correctIndex
if (isCorrect) score++
showFeedback(isCorrect, session[current])

// On next:
current++
if (current === 20) showEndScreen()
else showQuestion()
```

Options are shuffled once when a question is first displayed (not re-shuffled on feedback view).

### Image Path Canonicalization

The `rules_extract/images/` directory contains two naming conventions for the same images. The canonical convention for `questions.json` and for files in `docs/images/` is:

- Rules images: `page{N}_imgN.png` (e.g. `page106_img1.png`)
- Clarification images: `clarif_page{N}_imgN.png` (e.g. `clarif_page3_img1.png`)

The `2025_icf_canoe_polo_rules.pdf-{page}-{idx}.png` files are duplicates and should not be referenced in questions.

**Image usability:** Before referencing any clarification image in a question, confirm it is non-blank (some extracted PDFs have blank white rectangles). The generation script should include a pre-flight check or a curated allowlist of usable images.

### Tech Stack

- **App:** Plain HTML5, CSS3, vanilla JavaScript (ES2020). No framework, no bundler, no build step.
- **Generator script:** Python 3 + Anthropic SDK (or equivalent LLM API). Run once offline; output is committed.
- **Validator script:** Python 3 (jsonschema). Run to verify `questions.json` before deploying.
- **Hosting:** GitHub Pages, source = `docs/` directory.
- **Local dev:** `python3 -m http.server 8080` from `docs/` (required because `fetch()` of JSON fails on `file://`).

### Error Handling

- If `questions.json` fails to load (first visit, offline): show a user-legible error on the start screen: "Could not load question bank. Please check your connection and refresh."
- If bank has fewer than 20 questions (malformed JSON): show start screen error and do not allow quiz to begin.
- If an image fails to load: hide the image element silently (CSS `onerror` handler); do not break the question.

## Implementation Phases

### Phase 1: Project Scaffolding

- [ ] Create `docs/` directory with `index.html`, `quiz.js`, `style.css` stubs
- [ ] Create `scripts/` directory
- [ ] Add `docs/images/` directory (gitkeep or first images)
- [ ] Configure GitHub Pages source to `docs/` in repo settings (manual step, documented in README)
- [ ] Add `README.md` with local dev instructions (`python3 -m http.server`)

**Deliverable:** Repo is ready for development; GitHub Pages is configured.

### Phase 2: Question Bank Generation

- [ ] Write `scripts/generate_questions.py`:
  - Reads `rules_extract/2025_icf_canoe_polo_rules.md` (chapters 7–11 only)
  - Reads `rules_extract/2025_icf_canoe_polo_rule_clarifications.md`
  - Extracts each rule section as a chunk
  - Calls LLM (Anthropic API) to generate 2–4 questions per chunk, conforming to JSON schema
  - Writes raw output to `docs/questions.json`
- [ ] Write `scripts/validate_questions.py`:
  - Validates `questions.json` against the schema (all required fields, `correctIndex` in range, exactly 4 options, unique `id`s)
  - Reports any referenced `image` paths that do not exist in `docs/images/`
- [ ] Run generation, review and spot-check 10% of questions for accuracy
- [ ] Copy referenced images from `rules_extract/images/` to `docs/images/`
- [ ] Commit `docs/questions.json` and `docs/images/`

**Deliverable:** Validated `docs/questions.json` with full chapter 7–11 + clarifications coverage.

**Generation prompt guidance (for `generate_questions.py`):**

```python
SYSTEM_PROMPT = """
You are generating multiple-choice quiz questions for canoe polo referees studying the ICF 2025 rules.

For each rule or sub-rule provided, generate 2-4 questions. Each question must:
- Be unambiguous and answerable from the rule text alone
- Have exactly 4 options (A/B/C/D), one definitively correct
- Include a concise explanation citing the specific rule number
- Be under 200 characters for the question text

Prefer questions about: specific numbers/thresholds, definitions, what a referee must do (not may do), penalty outcomes, and exception conditions.

Respond ONLY with a JSON array of question objects conforming to this schema:
[{
  "rule": "<rule number>",
  "question": "<question text>",
  "options": ["<opt1>", "<opt2>", "<opt3>", "<opt4>"],
  "correctIndex": <0-3>,
  "explanation": "<explanation citing rule>"
}]
"""
```

### Phase 3: Rules Viewer

- [ ] Write `scripts/parse_rules.py`:
  - Parses `rules_extract/2025_icf_canoe_polo_rules.md` (chapters 7–11 only)
  - Builds a structured tree of chapters → sections → sub-sections
  - Writes `docs/rules.json`
- [ ] Write `docs/rules.html` + `docs/rules.js` + `docs/rules.css`:
  - Loads `rules.json` and renders a collapsible chapter/rule tree
  - Each rule section has an `id` matching its rule number (e.g. `id="10.22.3"`)
  - On page load, reads `window.location.hash` — if a rule id is found, expand its chapter and scroll to it
  - Chapter collapse/expand state is toggled on click
  - Mobile: sidebar collapses to a top accordion; rule sections remain readable at 375px width
- [ ] Add nav link from `index.html` to `rules.html` ("View Rules") and vice versa ("Take Quiz")

**Deliverable:** Working rules viewer at `docs/rules.html` with deep-link support.

### Phase 4: Quiz App Implementation

- [ ] **`docs/index.html`**: Single-page shell. Loads `quiz.js` and `style.css`. Contains placeholder `<div>` containers for each view (start, question, end). No inline JS.

- [ ] **`docs/quiz.js`**: Implements the full app:
  - `loadQuestions()` — fetch `questions.json`, parse, handle errors
  - `startSession()` — Fisher-Yates shuffle + slice 20, init state
  - `showQuestion(index)` — render question view with shuffled options
  - `selectAnswer(displayIndex)` — check answer, track score, show feedback + "View Rule X →" link (opens `rules.html#{ruleId}` in new tab)
  - `nextQuestion()` — advance index or show end screen
  - `showEndScreen()` — render score as "X / 20 — Y%"
  - `resetSession()` — clear state, start new session

- [ ] **`docs/style.css`**: Mobile-first responsive layout.
  - Max content width ~600px, centered
  - Question counter / score header (sticky or fixed)
  - Answer buttons: full-width, large touch targets (min 44px height)
  - Feedback colours: green (#2d7a2d or similar) for correct, red (#b22222) with text label — WCAG AA contrast
  - Correct/incorrect conveyed via text label AND colour (accessibility)
  - Images: `max-width: 100%; height: auto`
  - Error state: clearly styled, distinguishable from normal UI

### Phase 5: Testing & Polish

- [ ] Manual test quiz on desktop Chrome and mobile Safari (poolside use case)
- [ ] Test rules viewer: navigate to `rules.html#10.22.3`, confirm chapter expands and scrolls to rule
- [ ] Test "View Rule X" link in quiz feedback opens `rules.html` at the correct anchor
- [ ] Verify all image paths in `questions.json` resolve in `docs/`
- [ ] Test error states: rename `questions.json` temporarily, verify error message appears
- [ ] Test session restart: confirm fresh 20 questions are drawn
- [ ] Spot-check 5 questions with images display correctly on mobile
- [ ] Review answer option shuffling: correct answer appears in each position across multiple sessions
- [ ] Run `scripts/validate_questions.py` one final time
- [ ] Deploy to GitHub Pages and smoke test quiz and rules viewer at the live URL

## Acceptance Criteria

- [ ] Quiz app and rules viewer both load on GitHub Pages with no console errors
- [ ] Each quiz session presents exactly 20 questions drawn randomly from the bank
- [ ] Selecting an answer immediately shows: correct/incorrect state, rule citation, explanation
- [ ] The correct answer is highlighted even when the user answers incorrectly
- [ ] "Next Question" button only appears after an answer is selected
- [ ] End screen shows score as "X / 20 — Y%"
- [ ] "Start New Session" draws a fresh random 20 (not the same sequence)
- [ ] Answer option order is shuffled per question display
- [ ] App is functional and readable on an iPhone-sized screen (375px wide)
- [ ] `questions.json` covers all chapters 7–11 rules + rule clarifications
- [ ] Every question in `questions.json` passes `validate_questions.py` with no errors
- [ ] Failed `questions.json` load shows a user-readable error (not a blank/broken UI)
- [ ] Rules viewer: navigating to `rules.html#10.22` expands the chapter and scrolls to rule 10.22
- [ ] Quiz feedback shows optional "View Rule X →" link that opens the rules viewer at the correct anchor
- [ ] Rules viewer is navigable and readable on 375px-wide mobile screen

## Dependencies & Prerequisites

- Anthropic API key (or equivalent LLM) available locally for question generation — not needed at runtime
- GitHub repository with Pages enabled (source: `docs/`)
- Python 3.x with `anthropic` and `jsonschema` packages for the generation scripts

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM generates factually incorrect questions | Medium | High | Spot-check 10%+ of generated questions against source rules; run validator |
| Some clarification images are blank (PDF extraction artefact) | Known | Medium | Curate allowlist of usable images before authoring image questions |
| GitHub Pages base path breaks relative URLs | Low | Medium | Use relative paths only; test at live URL before marking done |
| `fetch()` of JSON fails in local dev on file:// | Certain (local only) | Low | Document `python3 -m http.server` as required for local dev |
| Generated bank has <150 questions | Low | Low | 70+ rules × 2 min = 140+ expected; validate count in validator script |

## System-Wide Impact

This is a greenfield project with no existing codebase to affect. No callbacks, middleware, or shared state to audit. The only external dependency is the GitHub Pages hosting infrastructure, which is stateless.

## Outstanding Questions

**Rules viewer v2 (deferred):** Full-text search across all rules. Not in scope for initial build; the collapsible tree is the MVP.

These were deferred from the brainstorm as planning-level decisions and are now resolved or addressed above:

- **JSON schema** → defined in "Question Bank JSON Schema" section above
- **Image path convention** → `page{N}_imgN.png` and `clarif_page{N}_imgN.png` canonical; duplicates excluded
- **Tech stack** → plain HTML/CSS/JS, no framework
- **Clarifications in scope** → yes, with citation format `"Illegal Hand Tackle"` etc. and `source: "clarification"`
- **Session advance mechanism** → explicit "Next Question" button only
- **Option order** → shuffled per question display; `correctIndex` refers to stored order
- **Score display** → "X / 20 — Y%" on end screen only; no per-chapter breakdown
- **Progress persistence** → not saved; one-line note on start screen

## Sources & References

### Origin

- **Origin document:** [docs/brainstorms/2026-03-24-canoe-polo-quiz-requirements.md](../brainstorms/2026-03-24-canoe-polo-quiz-requirements.md)
  - Key decisions carried forward: static GitHub Pages delivery, pre-generated question bank, chapters 7–11 + clarifications coverage, 20 questions per session, immediate per-question feedback

### Internal References

- Source rules: `rules_extract/2025_icf_canoe_polo_rules.md`
- Source clarifications: `rules_extract/2025_icf_canoe_polo_rule_clarifications.md`
- Source images: `rules_extract/images/`
