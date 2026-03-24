---
module: Rules Quiz
date: 2026-03-25
problem_type: ui_bug
component: frontend_stimulus
symptoms:
  - "A blue focus outline appears on one of the answer option buttons as soon as a new question loads"
  - "The highlighted button is always in the same position as the previously clicked answer"
root_cause: async_timing
resolution_type: code_fix
severity: low
tags: [focus-ring, quiz, mobile, browser-focus, transition]
---

# Troubleshooting: Focus Ring Carried Onto New Option Buttons Between Questions

## Problem

After answering a question and clicking "Next Question", one of the new option buttons on the next question appeared pre-highlighted with a blue focus outline. It looked as though the previous answer was still selected.

## Environment

- Module: Rules Quiz (`docs/quiz.js`, `docs/quiz.css`)
- Affected Component: `.option-btn` focus state, `showQuestion()` / `showFeedback()` transition
- Date: 2026-03-25

## Symptoms

- Blue outline visible on an answer button immediately when the next question appeared
- Always on the button in the same vertical position as the previously clicked answer
- Not caused by any `correct`/`incorrect` CSS class — those are stripped when options are recreated

## What Didn't Work

**Direct solution:** Root cause identified immediately.

## Root Cause

1. User clicks an option button → that button receives browser focus
2. After the delay, `showFeedback()` hides `screenQuestion` and shows `screenFeedback`
3. User clicks "Next Question" (`btnNext`) → `btnNext` receives focus
4. `showQuestion()` rebuilds `optionsList` with new buttons, then `showScreen('screenQuestion')` hides `screenFeedback` (and thus `btnNext`)
5. When the focused element (`btnNext`) becomes hidden, the browser relocates focus to the next focusable element in the DOM — the first new `.option-btn`
6. This programmatically-relocated focus triggers `:focus-visible`, showing the outline even though no keyboard navigation occurred

## Solution

Blur the active element at the end of `showQuestion()`, after `showScreen` hides the previous screen:

```js
// docs/quiz.js — inside showQuestion(), after showScreen()
showScreen('screenQuestion');
// Blur any focused element so the browser doesn't carry a focus ring
// onto the new option buttons when the previous screen is hidden.
if (document.activeElement) document.activeElement.blur();
```

## Why This Works

`document.activeElement.blur()` releases focus from whichever element held it (typically `btnNext`). With no element focused, the browser has nothing to relocate when the previous screen is hidden, so no `:focus-visible` outline appears on the new buttons.

## Prevention

- Any time a screen transition hides a focused element, the browser will try to relocate focus. Blur the active element before or immediately after the transition to prevent carry-over.
- `:focus-visible` is intentionally shown for programmatic focus relocation (it's considered non-mouse), so relying on `:focus-visible` alone does not prevent this.

## Related Issues

- See also: [css-display-overrides-hidden-attribute.md](css-display-overrides-hidden-attribute.md) — another case where display/hidden state interacts unexpectedly with browser behaviour
