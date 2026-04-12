---
title: "feat: Add Scenario Quiz page"
type: feat
status: active
date: 2026-04-12
origin: planning/brainstorms/2026-04-12-scenario-quiz-requirements.md
---

# feat: Add Scenario Quiz page

## Enhancement Summary

**Deepened on:** 2026-04-12
**Research agents used:** race-condition review, code simplicity review, checkbox UX research, AI MCQ generation research, referee scenario quality research

### Key improvements added
1. **Race condition fixes** — three timing landmines identified in `handleCheck`: double-tap, stale setTimeout firing after navigation, and DOM detachment. All have specific fixes.
2. **Checkbox accessibility** — full accessible checkbox pattern using `appearance: none`, `:focus-within`, `:has()`, non-colour feedback icons (✓ ✗ !), and correct `disabled` vs `aria-disabled` usage.
3. **AI prompt template** — a complete, ready-to-use Opus prompt structure with chain-of-thought, 2 few-shot examples, 5 distractor type taxonomy, and a Bloom's Application enforcement constraint.
4. **Human reviewer checklist** — 20-point validation checklist with BLOCK items before adding any scenario to `scenarios.json`.
5. **Coverage distribution** — specific target split for the 30–50 question pool; priority scenario types for sanction combinations.
6. **Chapter clarification** — primary game rules and fouls are in **Chapter 10** (10.10–10.38), not Chapter 9 (which is Competition Schedule). Scenarios draw from Ch10, Ch17, clarifications.

### New considerations
- Inline `arraysEqual` (no extraction); rename to `displayCorrectIndices` for codebase consistency
- Add `min-height: 44px` to `.option-btn` for WCAG touch target compliance
- Generate one scenario per API call; batch generation produces repetitive distractors

---

## Overview

Add a new `scenario.html` page that presents game-situation scenarios and asks the user to select all correct referee actions using checkboxes. This tests applied judgement rather than factual recall — bridging the gap between the existing Rules Quiz (fact recall) and what referee exams actually test.

Key differences from the existing Rules Quiz:
- **Select-all-that-apply** checkboxes + "Check Answer" button (vs single-tap immediate answer)
- **Per-option feedback** — each option coloured correct/incorrect/missed after submission
- **All-or-nothing scoring** — only exact match to `correctIndices[]` scores a point
- **10-question sessions** (vs 20) — scenarios require more cognitive effort
- **New `scenarios.json`** data file with a multi-correct-answer schema

## Problem Statement / Motivation

Referee exam candidates using the existing Rules Quiz develop factual recall but get no practice with applied judgement scenarios. Exams test both. Scenarios involving sanctions (cautions, exclusions, penalty calls) are especially important — these are high-stakes decisions in real games and require recognising that multiple actions must be taken simultaneously (e.g. award a penalty shot AND sanction the offending player).

(see origin: planning/brainstorms/2026-04-12-scenario-quiz-requirements.md)

## Proposed Solution

### New files

| File | Purpose |
|---|---|
| `docs/scenario.html` | New quiz page — 4-screen layout (start, question, feedback, end) |
| `docs/scenario.js` | Quiz engine for scenario quiz — IIFE, checkbox multi-select logic |
| `docs/scenario.css` | Page-specific styles — checkbox appearance, `.missed` feedback state |
| `docs/scenarios.json` | 30–50 scenario questions with `correctIndices[]` array |

### Modified files

| File | Change |
|---|---|
| `docs/sw.js` | Bump `CACHE_VERSION` to `'v4'`; add 4 new assets to `ASSETS` array |
| `docs/index.html` | Add 4th home panel (Scenarios) + nav link |
| `docs/signals.html` | Add Scenarios nav link |
| `docs/rules.html` | Add Scenarios nav link |

---

## Technical Considerations

### `scenarios.json` schema

```json
[
  {
    "id": "scn-ch10-001",
    "chapter": 10,
    "rule": "10.29.2",
    "situation": "With the blue team attacking inside the white team's 6-metre area, Player A (blue) is in a clear shooting position and begins to raise the ball. Player B (white), unable to reach the ball, deliberately pushes Player A's kayak side-on, unbalancing them and preventing the shot. The referee clearly sees the deliberate contact.",
    "options": [
      "Award a goal penalty shot to the blue team",
      "Award a free shot to the blue team",
      "Issue a sanction card to Player B",
      "Issue a sanction card to Player A"
    ],
    "correctIndices": [0, 2],
    "explanation": "Rule 10.29.2 requires a goal penalty shot for any deliberate foul on a shooter inside the 6-metre area — not a free shot. Rule 10.35.4 additionally requires a sanction card for the offending player (Player B, white) whenever a deliberate or dangerous foul results in a goal penalty shot. Both actions must be taken simultaneously. Option B is wrong because a free shot applies outside the zone; here the deliberate foul inside 6m on a shooter triggers the GPS. Option D is wrong — it is Player B who committed the foul, not Player A."
  }
]
```

**Field notes:**
- `id`: pattern `scn-ch{n}-{seq}`, e.g. `scn-ch10-001`
- `rule`: leaf subsection ID only (never parent); drives the `rules.html#rule` deep-link — use the primary/sanction rule when the scenario spans multiple rules
- `situation`: paragraph stem (3–5 sentences) describing the game incident
- `options`: always exactly 4 strings; parallel grammatical form, approximately equal length
- `correctIndices`: array of 0–3 integers; minimum 1, maximum 3 (never all 4 correct)
- `explanation`: cites specific sub-clauses; explains both why each correct option applies and why each distractor is wrong

---

### `scenario.js` architecture

Follow the same IIFE + 4-screen pattern as `quiz.js` and `signals.js`.

**Key constants:**
```js
const SESSION_SIZE = 10;
const LETTERS = ['A', 'B', 'C', 'D'];
```

**State:**
```js
let allScenarios = [];
let session = [];         // [{scenario, shuffledOrder, displayCorrectIndices}]
let current = 0;
let score = 0;
let pendingFeedback = null;  // cancel token for setTimeout — see race condition section
```

**Session building:**
- Shuffle full pool; slice to `Math.min(SESSION_SIZE, pool.length)`
- For each scenario, generate a `shuffledOrder` array (same pattern as `quiz.js`'s `displayOrder`)
- Remap `correctIndices` through the shuffle: `displayCorrectIndices = correctIndices.map(i => shuffledOrder.indexOf(i))`
- Name: `displayCorrectIndices` (plural, consistent with `quiz.js`'s `displayCorrectIndex` naming pattern)

**`showQuestion(index)`:**
- Render `<label class="option-btn" for="scn-opt-{i}">` + `<input type="checkbox" id="scn-opt-{i}">` + `<span class="option-indicator">` + letter + text spans for each option
- Set `btnScnCheck.disabled = true` initially
- Wire `change` listener on each checkbox to enable `btnScnCheck` when any is checked
- Wire `btnScnCheck.onclick` to `handleCheck(index)`
- After `showScreen('scnQuestion')`: `if (document.activeElement) document.activeElement.blur()`

**`handleCheck(index)` — with race condition fixes:**
```js
function handleCheck(index) {
  // 1. Disable immediately — prevents double-tap before setTimeout fires
  btnScnCheck.disabled = true;

  // 2. Cancel any pending feedback from a previous question
  cancelPendingFeedback();

  const checked = getCheckedIndices();   // sorted numerically
  const correct = session[index].displayCorrectIndices;
  const isCorrect =
    checked.length === correct.length &&
    checked.every((v, i) => v === correct[i]);  // both pre-sorted; inline, no helper fn needed
  if (isCorrect) score++;

  revealOptionStates(correct, checked);

  // 3. Cancel token prevents stale callback firing after navigation
  const token = { canceled: false };
  token.id = setTimeout(() => {
    if (token.canceled) return;
    showFeedback(index, isCorrect);
  }, isCorrect ? 300 : 1200);
  pendingFeedback = token;
}

function cancelPendingFeedback() {
  if (pendingFeedback) {
    clearTimeout(pendingFeedback.id);
    pendingFeedback.canceled = true;
    pendingFeedback = null;
  }
}
```
Call `cancelPendingFeedback()` at the start of `startQuiz()` and `showEnd()`.

**`getCheckedIndices()`:**
```js
function getCheckedIndices() {
  return [...document.querySelectorAll('.option-checkbox')]
    .map((cb, i) => cb.checked ? i : -1)
    .filter(i => i !== -1)
    .sort((a, b) => a - b);  // numeric sort — default lexicographic would be wrong
}
```

**`revealOptionStates(correct, checked)`:**
```js
function revealOptionStates(correct, checked) {
  document.querySelectorAll('.option-btn').forEach((label, i) => {
    if (!document.contains(label)) return;  // node detached — skip
    const isCorrect = correct.includes(i);
    const isChecked = checked.includes(i);
    label.classList.toggle('correct',   isCorrect);
    label.classList.toggle('incorrect', isChecked && !isCorrect);
    label.classList.toggle('missed',    !isChecked && isCorrect);
    label.classList.add('revealed');
    // Append icon for non-colour accessibility
    const icon = document.createElement('span');
    icon.className = 'option-icon';
    icon.setAttribute('aria-hidden', 'true');
    label.appendChild(icon);
    // Lock input
    const cb = label.querySelector('.option-checkbox');
    if (cb) { cb.disabled = true; cb.tabIndex = -1; }
  });
}
```

**Per-option states after reveal:**
- `.correct` — in `displayCorrectIndices`, whether or not checked
- `.incorrect` — checked but NOT in `displayCorrectIndices`
- `.missed` — in `displayCorrectIndices` but NOT checked
- `.revealed` — all labels get this class to kill hover/pointer effects

**Fetch with pool guard:**
```js
fetch('scenarios.json')
  .then(r => {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  })
  .then(data => {
    allScenarios = data;
    btnScnStart.disabled = false;   // only enable after data is ready
    initStart();
  })
  .catch(err => {
    document.getElementById('scnStart').querySelector('.card').innerHTML =
      '<p style="color:var(--color-incorrect)">Could not load scenarios: ' + err.message + '</p>';
  });
```
Render `btnScnStart` with `disabled` attribute in HTML; remove it only after successful fetch.

**`showScreen` uses its own ID list:**
```js
function showScreen(id) {
  ['scnStart', 'scnQuestion', 'scnFeedback', 'scnEnd'].forEach(s => {
    document.getElementById(s).hidden = s !== id;
  });
}
```

**`showEnd` score thresholds** (same as existing quiz): 90% = excellent, 70% = good, 50% = keep studying, below = keep at it.

---

### `scenario.css`

Extend existing `quiz.css` patterns. All CSS tokens from `shared.css` `:root` apply.

**Add to `shared.css` `:root`:**
```css
--color-missed:    #b45309;   /* amber-700 — meets 4.5:1 on white */
--color-missed-bg: #fef3c7;   /* amber-100 */
```

**`scenario.css` rules:**

```css
/* ── Hidden-but-accessible checkbox ─────────────────────────────────── */
.option-checkbox {
  -webkit-appearance: none;
  appearance: none;
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;   /* clicks go to the label wrapper */
}

/* ── Custom checkbox indicator ──────────────────────────────────────── */
.option-indicator {
  flex-shrink: 0;
  width: 1.15em;
  height: 1.15em;
  border: 2px solid var(--color-border);
  border-radius: 3px;
  background: var(--color-bg);
  display: grid;
  place-content: center;
  transition: border-color 0.1s, background 0.1s;
}

.option-indicator::before {
  content: "";
  width: 0.55em;
  height: 0.55em;
  transform: scale(0);
  transition: transform 100ms ease-in-out;
  clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%);
  background: currentColor;
}

/* Checked state — drives indicator AND label highlight (no JS needed) */
.option-checkbox:checked ~ .option-indicator {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: #fff;
}
.option-checkbox:checked ~ .option-indicator::before { transform: scale(1); }

.option-btn:has(.option-checkbox:checked) {
  border-color: var(--color-primary);
  background: #e8f4fb;
}

/* Focus ring via :focus-within on the label (replaces :focus-visible on button) */
.option-btn:focus-within {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
}

/* ── Touch target minimum ────────────────────────────────────────────── */
.option-btn {
  min-height: 44px;   /* WCAG 2.5.5 — was ~40px with 0.75rem padding */
}

/* ── Post-reveal locked state ────────────────────────────────────────── */
.option-btn.revealed {
  cursor: default;
  pointer-events: none;
}
.option-btn.revealed:hover {
  border-color: inherit;
  background: inherit;
}

/* ── Feedback states (extend existing .correct / .incorrect) ─────────── */
.option-btn.missed {
  border-color: var(--color-missed);
  background: var(--color-missed-bg);
  color: var(--color-missed);
}
.option-btn.missed .option-letter { background: var(--color-missed); color: #fff; }

/* ── Non-colour icons (WCAG 1.4.1) ──────────────────────────────────── */
.option-icon {
  flex-shrink: 0;
  font-size: 0.9rem;
  margin-left: auto;
  font-weight: 700;
}
.option-btn.correct   .option-icon::before { content: "✓"; }
.option-btn.incorrect .option-icon::before { content: "✗"; }
.option-btn.missed    .option-icon::before { content: "!"; }

/* ── "Check Answer" button disabled state ────────────────────────────── */
#btnScnCheck:disabled { opacity: 0.4; cursor: not-allowed; }
```

**Why `:has()` is safe here:** Supported in all modern browsers (95%+ global, all evergreens since late 2023). iOS Safari 16+, Chrome 105+, Firefox 121+.

---

### `scenario.html` structure

Mirrors `signals.html` — same 4-screen scaffold, same header/nav, same SW registration block. Use `scn`-prefixed IDs throughout.

**Option markup (per item):**
```html
<li>
  <label class="option-btn" for="scn-opt-0">
    <input type="checkbox" id="scn-opt-0" name="options" value="0"
           class="option-checkbox">
    <span class="option-indicator" aria-hidden="true"></span>
    <span class="option-letter" aria-hidden="true">A</span>
    <span class="option-text">Award a goal penalty shot</span>
  </label>
</li>
```
The `aria-hidden` on indicator and letter keeps screen reader output clean — the label text is sufficient.

**New home panel in `index.html`:**
```html
<a href="scenario.html" class="home-panel home-panel-link">
  <div class="panel-icon">&#127381;</div>
  <h2>Scenario Quiz</h2>
  <p>Game situations: identify every correct referee action.</p>
</a>
```
Add as 4th panel (after Signals Quiz panel).

**Nav link** (add to all 4 HTML files):
```html
<a href="scenario.html">Scenarios</a>
```

**SW registration** — copy verbatim from `signals.html` (including `#swUpdateBanner` block). Use `/CanoePoloRules/sw.js` absolute path.

---

### `sw.js` changes

```js
const CACHE_VERSION = 'v4';   // was 'v3'

const ASSETS = [
  // … existing entries …
  '/CanoePoloRules/scenario.html',
  '/CanoePoloRules/scenario.js',
  '/CanoePoloRules/scenario.css',
  '/CanoePoloRules/scenarios.json',
];
```

---

### Content generation approach

> **Sequencing note:** Content generation is a separate step done *after* the code is complete and working. Use Claude Opus (or equivalent capable model) for the generation step to maximise scenario quality.

> **Chapter note:** Game rules and fouls are in **Chapter 10** (10.10–10.38). Chapter 9 is Competition Schedule. Primary sources: `rules_extract/2025_icf_canoe_polo_rules.md` (Ch10, Ch17) and `rules_extract/2025_icf_canoe_polo_rule_clarifications.md`.

#### Recommended coverage distribution (40-question pool)

| Category | Target | Key sections |
|---|---|---|
| Foul recognition + restart type | 12–14 q | 10.19–10.26, GPS boundary (10.29.2–10.29.6) |
| Combined foul + sanction (restart AND card) | 10–12 q | 10.28, 10.32–10.36, 10.29 + 10.35.4 |
| Advantage rule | 4–5 q | 10.12 (including deferred card after advantage) |
| Clarification-specific scenarios | 4–6 q | Sprint starts, defender's paddle, hand tackle timing |
| Restart procedure + location | 4–5 q | 10.29–10.38 (taking throws, GPS procedure) |
| Edge cases (simultaneous decisions) | 3–4 q | Red card + reduced team, illegal sub preventing goal |

Sanction-combination questions (combined foul + sanction row) naturally satisfy the ≥30% sanctions requirement.

#### Priority scenario types for sanction combinations

| Situation | Restart | Card | Key novice error |
|---|---|---|---|
| Deliberate foul on shooter inside 6m | Goal penalty shot | Yellow (min.) | GPS only, forgetting the card |
| Deliberate dangerous foul anywhere | Free shot | Red or Yellow | Under-calling the card severity |
| Advantage played, card still due | Original restart abandoned | Card at next stoppage | Forgetting the card after advantage |
| Illegal entry/sub preventing goal | Goal penalty shot | Red (ejection) | Under-calling to yellow |
| Foul outside 6m, goal undefended | Goal penalty shot | Yellow | Missing "undefended goal" escalation trigger |

#### Prompt template for Opus

Use this structure for each scenario generated. **Generate one per API call** — batch generation produces repetitive distractors and more F4 failures (too many correct options).

```
You are an expert canoe polo referee examiner writing a scenario-based quiz question
for ICF referee certification candidates. You will produce ONE scenario question.

SOURCE RULES (use only these; do not invent rules not present here):
[PASTE LEAF SUBSECTION(S) — include clarifications text when relevant]

BLOOM'S LEVEL: Write a NOVEL GAME INCIDENT. The correct answer must require
knowing the rule, not just reading the situation. Include one factual detail
that a novice might think changes the call but which the rule says is irrelevant
(the "trap detail" technique).

CONSTRAINTS:
- Situation: 3–5 sentences, one incident, one foul, specific location
  (inside/outside 6m, exact zone if relevant). No rule numbers in the text.
- Action in terms of effect, not prejudged intent. Let the candidate assess intent.
- Options: exactly 4, between 1 and 3 correct (never all 4).
- Each distractor must be TYPE 1, 2, 3, 4, or 5 (label type in <thinking>).
- Explanation: cite specific sub-clause for each correct option AND explain
  why each distractor is wrong.
- `rule`: leaf subsection ID only (e.g., "10.29.2", never "10.29").

DISTRACTOR TYPES:
- TYPE 1 (Wrong tier): free throw vs free shot vs GPS
- TYPE 2 (Wrong player): correct action, wrong team or player
- TYPE 3 (Incomplete): missing required companion action (card + restart)
- TYPE 4 (Overcorrection): harsher sanction than warranted
- TYPE 5 (Under-action): "allow play" or "play advantage" when mandatory

For sanction scenarios: use TYPE 3 as at least one distractor.

OUTPUT FORMAT (JSON only, after <thinking> block):
{
  "id": "scn-ch{N}-{seq}",
  "chapter": <int>,
  "rule": "<leaf-subsection-id>",
  "situation": "...",
  "options": ["A", "B", "C", "D"],
  "correctIndices": [<0-based ints, 1–3 entries>],
  "explanation": "..."
}

Think through your reasoning in a <thinking> block before producing JSON.
Output ONLY the thinking block followed by the JSON object.

[PASTE TWO FEW-SHOT EXAMPLES — one single-correct, one multi-correct sanction]
```

#### Common LLM failure modes to watch for

| Code | Problem | Fix |
|---|---|---|
| F1 | Stem-answer cluing — option text echoes unique words from situation | Constraint: forbid options echoing situation's unique terms |
| F2 | Implausible distractors — no real referee would choose them | Require each distractor to represent a documented novice mistake |
| F3 | Grammatical cues — correct option is notably longer/different | Audit all 4 options for parallel form and similar length |
| F4 | Answer inflation — 3 or 4 options correct | Constrain: max 3 correct; make some questions single-correct |
| F5 | Compound scenario — two simultaneous fouls, ambiguous chain | Require: one incident, one foul, one clear victim |
| F6 | Reverse-engineered question from explanation | Chain-of-thought block forces pre-flight reasoning |
| F7 | Invented rules — wrong distances, wrong card colours | Inline source text is the only reliable fix |
| F8 | Overly long stems — irrelevant details inflate cognitive load | Constrain situation to 3–5 sentences, every sentence relevant |

#### Human reviewer checklist

Run every generated scenario through this before adding to `scenarios.json`. **(BLOCK)** items are disqualifying.

**Content accuracy**
- [ ] **(BLOCK)** Every correct action in `correctIndices` is directly supported by a specific sub-clause cited in the explanation
- [ ] **(BLOCK)** `rule` field is a leaf subsection ID, not a parent section
- [ ] **(BLOCK)** Explanation states why each distractor is wrong — not only why correct options are right
- [ ] Explanation cites the specific sub-clause (e.g., "Rule 10.35.4"), not just the chapter

**Scenario quality**
- [ ] **(BLOCK)** Situation describes exactly one incident (no compound fouls, no "meanwhile" clauses)
- [ ] **(BLOCK)** Situation is unambiguous — a knowledgeable referee can determine the correct call from the facts given
- [ ] No rule numbers or rule text appear in the situation paragraph
- [ ] Location relative to the 6m zone is explicitly stated when the call depends on it
- [ ] Situation is 3–5 sentences

**Option quality**
- [ ] **(BLOCK)** Between 1 and 3 options are correct (not 0, not 4)
- [ ] Each distractor represents a genuine novice mistake (wrong tier, forgotten card, wrong team, wrong threshold)
- [ ] Options are parallel in grammatical form and approximately equal in length
- [ ] No option text echoes a unique phrase from the situation

**Schema** (also caught by `validate_scenarios.py`)
- [ ] `correctIndices` values are all valid option indices (0–3)
- [ ] `options` array has exactly 4 entries
- [ ] `id` follows the `scn-ch{N}-{seq}` pattern

#### After generating 10 questions — review for distribution

Re-read the pool after every 10 questions. Check:
- Are at least 30% sanction combinations (TYPE 3 distractor present)?
- Is the GPS boundary (inside vs. outside 6m) being tested from multiple angles?
- Are the clarifications (sprint starts, defender's paddle, hand tackle timing) represented?
- Is `correctIndices` length varied (not always 2 correct answers)?

---

## System-Wide Impact

- **Interaction graph**: `scenario.html` loads `scenario.js` → fetches `scenarios.json` → renders checkboxes → Check Answer button triggers evaluation → feedback shown → Next/See Results → end screen
- **Offline**: `scenarios.json` must be in `ASSETS` or the page silently fails for PWA users; `CACHE_VERSION` bump forces cache refresh for existing installs (see learnings: `pwa-cache-version-stale-update.md`)
- **Home panel layout**: Adding a 4th panel — verify 2×2 wrap looks correct at 480–600px and single-column looks acceptable on narrowest screens. The existing `home-panels-overflow-mobile` fix was calculated for 3 panels; re-measure.
- **Nav on all pages**: All 4 HTML files need the Scenarios nav link added consistently

---

## Acceptance Criteria

- [ ] `scenario.html` renders correctly on mobile and desktop with the same header/nav as other pages
- [ ] Home panel (index.html) shows 4 panels; layout is not broken on mobile at 375px
- [ ] Nav link to Scenarios appears on all pages (index, signals, rules, scenario)
- [ ] Selecting checkboxes highlights the selected options via indicator fill + label border; Check Answer button is disabled until at least one is ticked
- [ ] Check Answer button disabled immediately on first click (prevents double-tap)
- [ ] Submitting the correct exact combination marks the question as correct (score increments)
- [ ] Submitting a partial or wrong combination scores 0; per-option colouring shows correct (green ✓) / incorrect (red ✗) / missed (amber !)
- [ ] Icons (✓ ✗ !) appear alongside colour for colour-vision accessibility
- [ ] "View Rule" deep-link navigates to the correct leaf subsection in rules.html
- [ ] "Try Again" reshuffles the full pool and draws a new 10-question session; no stale setTimeout fires from previous session
- [ ] `scenario.html` works offline (service worker caches the page and `scenarios.json`)
- [ ] SW update banner appears on `scenario.html` when a new service worker is waiting
- [ ] `scenarios.json` contains 30–50 entries; ≥30% involve sanctions
- [ ] `scenarios.json` passes schema validation (leaf subsection IDs, valid `correctIndices`)
- [ ] No focus rings appear on option labels when transitioning between questions
- [ ] Keyboard navigation: Tab moves through checkboxes, Space toggles; Tab skips locked options after reveal

## Success Metrics

- A user can complete a 10-question scenario session without errors or layout issues on iOS Safari and Chrome Android
- Per-option feedback (especially the `.missed` state) makes clear which options were right/wrong without reading the explanation

## Dependencies & Risks

| Risk | Mitigation |
|---|---|
| Scenario content quality — ambiguous scenarios or wrong `correctIndices` undermine trust | Human reviewer checklist (20-point); `validate_scenarios.py`; generate one per call |
| 4th home panel breaks mobile layout | Measure total stacked height at 375px after adding panel; adjust padding/gap in `quiz.css` if needed |
| Service worker not updated → offline users miss new page | Always bump `CACHE_VERSION` in the same commit as any new cached asset |
| `displayCorrectIndices` remapping bug in session builder | Verify with a known scenario: check that `shuffledOrder.indexOf(originalCorrectIndex)` produces the correct display-slot index |
| Double-tap on Check Answer corrupts score | `btnScnCheck.disabled = true` as first line of `handleCheck` |
| Stale setTimeout firing after user navigates | `pendingFeedback` cancel token; `cancelPendingFeedback()` called in `startQuiz()` and `showEnd()` |
| Pool under 10 entries during authoring | `Math.min(SESSION_SIZE, pool.length)` guard; show visible warning if `session.length < SESSION_SIZE` |
| AI generates questions with invented rules | Always paste inline source text; no generation without the rule text present in the prompt |

## Sources & References

**Origin document:** [planning/brainstorms/2026-04-12-scenario-quiz-requirements.md](../brainstorms/2026-04-12-scenario-quiz-requirements.md)

Key decisions carried forward:
- Select-all-that-apply (not combo options) for richer per-option feedback
- All-or-nothing scoring aligned with exam-style pass/fail
- Separate page (not a mode on the existing quiz) for independent discoverability

**Internal references:**
- `docs/quiz.js` — `buildSession`, `showQuestion`, `handleAnswer`, `showFeedback`, `showEnd` patterns to follow
- `docs/signals.js` — second quiz page example; confirms `scn`-prefix ID convention
- `docs/sw.js:4` — `CACHE_VERSION` to bump; lines ~8–20 for `ASSETS` array
- `docs/index.html:34–55` — home panel grid markup
- `docs/quiz.css:122–187` — `.option-btn` styles to extend for checkbox/label variant
- `docs/quiz.css:340–428` — `.home-panel` styles

**Learnings applied:**
- `docs/solutions/runtime-errors/pwa-cache-version-stale-update.md` — always bump CACHE_VERSION when adding cached assets
- `docs/solutions/ui-bugs/focus-ring-carried-between-questions-20260325.md` — blur active element after showScreen
- `docs/solutions/ui-bugs/css-display-overrides-hidden-attribute.md` — do not set `display:` on screen classes
- `docs/solutions/ui-bugs/home-panels-overflow-mobile-20260324.md` — 4th panel may need mobile layout re-check
- `docs/solutions/content/quiz-question-coverage-gap-subsection-remapping.md` — leaf subsection IDs only in `rule` field

**External references (research agents):**
- [Checkbox Pattern | APG | WAI | W3C](https://www.w3.org/WAI/ARIA/apg/patterns/checkbox/)
- [Pure CSS Custom Checkbox Style | Modern CSS Solutions](https://moderncss.dev/pure-css-custom-checkbox-style/)
- [WCAG 2.5.5: Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [WCAG 1.4.1: Use of Color](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)
- [Designing Multiple-Choice Questions — University of Waterloo](https://uwaterloo.ca/centre-for-teaching-excellence/catalogs/tip-sheets/designing-multiple-choice-questions)
- [Decision-making training in sporting officials — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1469029221001217)
