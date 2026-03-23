---
date: 2026-03-24
topic: canoe-polo-quiz
---

# Canoe Polo Rules Quiz App

## Problem Frame

Referees learning or refreshing the 2025 ICF Canoe Polo Competition Rules have no interactive tool to test their knowledge. The source material (rules + clarifications) has been extracted to markdown. We need a self-study quiz app that referees can use to practise rule knowledge, drawing on that extracted content.

## Requirements

- R1. The app is a static web app deployable to GitHub Pages — no backend, no runtime API calls.
- R2. The question bank is a pre-generated JSON file (produced offline by an AI-assisted generation script) bundled with the app.
- R3. The question bank covers all rules in chapters 7–11 inclusive, with a minimum of 2 questions per rule/sub-rule; complex rules (e.g. 10.8.1) may have 4 or more questions.
- R4. Each question is multiple-choice with exactly 4 options and one correct answer.
- R5. Questions may optionally reference one of the extracted rule diagrams/images.
- R6. Each question includes a rule citation (e.g. "Rule 10.8.1") and a short explanation of the correct answer.
- R7. Each quiz session presents 20 questions selected randomly from the full bank.
- R8. After the user selects an answer, immediate feedback is shown: correct/incorrect, the rule citation, and the explanation.
- R9. At the end of a session the user sees their score and can start a new session.
- R10. The app works on both desktop and mobile browsers.

## Success Criteria

- A referee can complete a practice quiz session without any account, install, or internet-dependent runtime calls.
- Questions cover all chapters 7–11 rules with no obvious gaps.
- Immediate feedback correctly cites the rule and gives a useful explanation.
- The app is usable on a phone screen (referees may use it poolside).

## Scope Boundaries

- No user accounts, progress tracking, or persistent history.
- No formal certification or graded scoring stored anywhere.
- Question generation is an offline dev task, not an in-app feature.
- Chapters 1–6 and 12+ are out of scope for question coverage.
- No multiplayer or team quiz modes.

## Key Decisions

- **Static GitHub Pages delivery**: Chosen for zero hosting cost and zero backend complexity.
- **Pre-generated question bank**: Questions are generated once (offline with AI assistance) and committed as JSON — avoids runtime API costs and works fully offline after first load.
- **Images included**: The rule diagram images are already extracted; questions can reference them where helpful (e.g. field layout, tackle illustrations).
- **Immediate feedback**: Better for learning than end-of-quiz review; referees need to understand the rule in context of the question.

## Dependencies / Assumptions

- The `rules_extract/` markdown files are the authoritative source for question generation.
- The `rules_extract/images/` directory contains diagram images referenced in questions.
- Image paths in questions must be relative and compatible with GitHub Pages hosting.

## Outstanding Questions

### Deferred to Planning

- [Affects R2][Technical] What format/schema should the question bank JSON use?
- [Affects R5][Needs research] Which rule images are most useful to include in questions, and how should image-bearing questions be authored?
- [Affects R1][Technical] What tech stack for the web app — plain HTML/CSS/JS, or a lightweight framework?
- [Affects R3][Needs research] How many total questions will chapters 7–11 produce at 2+ per rule? (Estimate: 150–200+)

## Next Steps

→ `/ce:plan` for structured implementation planning
