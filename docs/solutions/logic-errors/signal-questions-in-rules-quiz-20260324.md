---
module: Rules Quiz
date: 2026-03-24
problem_type: logic_error
component: frontend_stimulus
symptoms:
  - "Rules quiz asked questions requiring signal number recall (e.g. 'Which signal is used for both the sprint start and start infringements?')"
  - "Answer options listed 'Signal 1', 'Signal 2', etc. — knowledge users cannot apply without seeing signal images"
  - "Chapter 15 signal description questions appeared in the rules quiz session pool"
root_cause: scope_issue
resolution_type: code_fix
severity: medium
tags: [quiz-questions, signals, scope, question-bank]
---

# Troubleshooting: Signal-Number Questions Appearing in Rules Quiz

## Problem

The rules quiz question pool included 41 questions from Chapter 15 (hand signal form and identification) plus one Chapter 10 question asking which signal number applies to a free shot. These questions require users to recall specific signal numbers and physical signal descriptions — knowledge they cannot apply without being shown signal images. The rules quiz shows no images, making these questions unanswerable in context.

## Environment

- Module: Rules Quiz
- Affected Component: `docs/questions.json` — shared question bank
- Date: 2026-03-24

## Symptoms

- Quiz presented questions like "Which signal is used for both the sprint start and start infringements?" with options "Signal 1", "Signal 2", "Signal 8", "Signal 14"
- Questions asked how specific signals are physically performed (arm positions, durations)
- Users expected to identify signals by number without any visual reference

## What Didn't Work

**Direct solution:** The problem was identified and fixed on the first attempt.

## Solution

Removed all Chapter 15 questions and the one non-Chapter-15 question whose answer options were signal numbers from `questions.json`.

**Commands run:**

```js
// Filter applied to questions.json
const keep = q.filter(x => {
  if (x.chapter === 15) return false;
  // 10.30 "Which signal applies when a free shot is awarded?" — answers are Signal N
  if (x.rule === '10.30' && x.options && x.options.some(o => /Signal \d/i.test(o))) return false;
  return true;
});
// 195 → 154 questions (41 removed)
```

**Result:** 154 questions remain across chapters 8–11 and 17. Chapter 15 is completely absent from the rules quiz pool.

## Why This Works

The rules quiz and signals quiz are deliberately separate:
- **Signals Quiz** — shows a photo of a referee performing a signal, user picks the signal name. Visual context makes signal identification reasonable.
- **Rules Quiz** — text questions about rules, procedures, and decisions. No images.

Signal number knowledge (e.g., "Signal 9 is obstruction") is arbitrary memorisation without the visual. It belongs exclusively in the Signals Quiz. Chapter 15 of the rules text is essentially a signal reference catalogue — every question derived from it tests signal recognition, not rule understanding.

The non-Chapter-15 exception (`10.30`): the question "Which signal applies when a free shot is awarded?" has signal number answer options, so the same reasoning applies even though it comes from Chapter 10.

## Prevention

- When adding new questions to `questions.json`, do not include any from Chapter 15.
- Avoid answer options of the form "Signal N" in the rules quiz — if the answer is a signal number, the question belongs in the Signals Quiz or needs to be reframed without requiring signal number recall.
- Other Chapter 10/17 questions that mention "signal" in passing (e.g., "the timekeeper's signal sounds") are fine — the word "signal" alone is not the criterion. The criterion is: does answering require knowing a hand signal number or physical form?

## Related Issues

No related issues documented yet.
