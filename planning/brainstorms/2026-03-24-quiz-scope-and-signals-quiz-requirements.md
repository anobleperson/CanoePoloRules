---
date: 2026-03-24
topic: quiz-scope-and-signals-quiz
---

# Quiz Scope Update & Signals Quiz

## Problem Frame

The quiz's chapter scope needs to align with actual referee exam requirements: chapter 7 (Officials) is no longer required, and chapter 17 (Shot Clock — specifically sections 17.4 and 17.5) is now in scope. Additionally, signal recognition is a distinct skill from rule recall, and a dedicated signals quiz (show image → name the signal) serves that learning need better than text-based questions.

## Requirements

- R1. Chapter 7 questions are excluded from the Rules Quiz. Chapter 7 content remains in the Rules Viewer.
- R2. Chapter 17 (Shot Clock) is added to the Rules Viewer in full (sections 17.1–17.5).
- R3. The Rules Quiz includes questions for chapter 17 sections 17.4 (Shot Clock Expiry) and 17.5 (Shot Clock Reset) only; sections 17.1–17.3 are in the viewer but not quizzed.
- R4. A new Signals Quiz mode exists separately from the Rules Quiz. It presents all 20 referee hand signals (chapter 15), one at a time in random order, showing the signal photo and asking the user to name the signal from 4 options.
- R5. The Signals Quiz multiple-choice options are signal names (e.g. "Obstruction", "Free Shot", "Referee's Ball"). Three distractors are plausible adjacent signals.
- R6. The home/start page presents three clear entry points: **View Rules**, **Rules Quiz**, and **Signals Quiz**.
- R7. The existing text-based chapter 15 questions (how signals are performed) remain in the Rules Quiz bank; the Signals Quiz is purely image-based recognition.
- R8. After each signal answer, feedback shows correct/incorrect and the signal's description (e.g. "Signal 9 — Obstruction: Hold one arm up in the air fist clenched for 2 seconds…").
- R9. The Signals Quiz tracks score across all 20 signals in a single session and shows a result at the end.

## Success Criteria

- A referee can practise signal recognition entirely by image, without needing to read text descriptions first.
- The Rules Quiz no longer contains chapter 7 questions.
- The Rules Quiz covers shot clock rules (17.4 and 17.5) with at least 2 questions per section.
- The home page makes all three modes immediately obvious without explanation.

## Scope Boundaries

- Chapter 7 questions are removed from the Rules Quiz bank (or filtered out at runtime — implementation decision). Chapter 7 rules stay in the viewer.
- Chapters 17.1–17.3 are in the viewer but not in any quiz.
- The Signals Quiz does not include text-based questions about how signals are performed — that stays in the Rules Quiz.
- No progressive difficulty, spaced repetition, or score history across sessions.

## Key Decisions

- **Signal name as options (not scenario descriptions)**: Chosen for clarity and testability — referees need to recognise signals by name quickly.
- **Signals Quiz is fully separate**: A shared quiz engine with a different data source is cleaner than mixing image-recognition and text questions in one mode.
- **Three-panel home page**: Replacing the current single-entry start screen; all three modes need equal prominence.

## Outstanding Questions

### Deferred to Planning

- [Affects R1][Technical] Should chapter 7 questions be removed from questions.json, or filtered at runtime by the quiz engine? Removing is simpler; filtering preserves them for potential future use.
- [Affects R4][Technical] Does the Signals Quiz reuse the existing quiz engine/JS with a different data source, or is it a lightweight separate implementation?
- [Affects R5][Technical] How are the three distractor signals chosen per question — random from the 20, or curated by similarity group (e.g. signals that look alike)?
- [Affects R2][Technical] Does chapter 17 parse cleanly with the existing `parse_rules.py` patterns, or does it need a new heading/format handler?

## Next Steps

→ `/ce:plan` for structured implementation planning
