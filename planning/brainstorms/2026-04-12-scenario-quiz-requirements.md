---
date: 2026-04-12
topic: scenario-quiz
---

# Scenario Quiz

## Problem Frame

The existing Rules Quiz tests factual recall ("What are the dimensions of the playing area?"), but referee exams also test *applied judgement* — recognising what calls to make in real game situations. A scenario quiz bridges this gap, presenting game incidents and asking users to identify the correct referee action(s).

## Requirements

- R1. A new page (`scenario.html`) hosts the scenario quiz as a standalone section, with its own nav link and home panel on `index.html`.
- R2. Each question presents a game situation as a paragraph stem (e.g. "Player A grabs Player B's arm during a shot attempt inside the 6m area — what should the referee do?"), followed by 4 options.
- R3. Options use a select-all-that-apply checkbox interaction. The user ticks one or more options and then taps a "Check Answer" button to submit.
- R4. Scoring is all-or-nothing: only selecting exactly the correct set of options earns a point.
- R5. After checking, the feedback screen shows which options were correct/incorrect (per-option colouring), the explanation text, and a link to the relevant rule in the rules viewer.
- R6. A session is 10 randomly selected questions.
- R7. Scenario questions are stored in a new static JSON file (e.g. `scenarios.json`) with a schema that supports multiple correct answer indices (`correctIndices: []`).
- R8. The initial question pool contains 30–50 scenarios, prioritising game rules (chapter 9/10/11) and clarifications. Sanction-related scenarios (cautions, exclusions, penalty calls) must make up at least 30% of the pool.
- R9. Scenario content is generated from the rules text in `rules_extract/`, with human review before committing to `scenarios.json`.

## Success Criteria

- A referee exam candidate can complete a 10-question scenario session and correctly identify what calls to make (and not make) in game incidents.
- The all-or-nothing feedback clearly communicates which options were right/wrong, supporting learning rather than just scoring.
- The scenario quiz is accessible offline via the existing service worker.

## Scope Boundaries

- No multi-step or branching scenarios — each question is a single self-contained incident.
- No partial credit scoring.
- Session size is fixed at 10; no user-configurable session length in this version.
- No progress persistence (no resume, no history) — same as existing quizzes.

## Key Decisions

- **Select-all-that-apply over combo options**: Chosen over "A and B" combined answer options because it better reflects how referees must identify each required action independently, and provides richer feedback per option.
- **All-or-nothing scoring**: Partial credit rejected to keep scoring simple and align with exam-style pass/fail expectations.
- **Separate page**: Chosen over a mode on the existing quiz page to keep the scenario quiz independently discoverable and allow it to diverge in layout if needed.
- **10-question session**: Shorter than the 20-question Rules Quiz because scenario questions require more cognitive effort per question.

## Dependencies / Assumptions

- Content generation from `rules_extract/` will produce a sufficient bank of distinct, unambiguous scenarios before the page ships.
- The existing service worker cache strategy covers `scenarios.json` and `scenario.html` for offline use.

## Outstanding Questions

### Resolve Before Planning
*(none)*

### Deferred to Planning

- [Affects R7, R8][Technical] What is the exact `scenarios.json` schema? (fields: `id`, `chapter`, `rule`, `situation`, `options[]`, `correctIndices[]`, `explanation`)
- [Affects R8][Needs research] What is the best approach for generating scenario content from rules text — scripted extraction, AI-assisted authoring, or a mix? What quality-control step is needed before adding to the bank?
- [Affects R1][Technical] Home panel icon, label copy, and nav ordering for `scenario.html`.
- [Affects R3, R5][Technical] Checkbox/option component design — whether it reuses option-btn styles or introduces a new component.

## Next Steps

→ `/ce:plan` for structured implementation planning
