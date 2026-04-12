---
title: Quiz Question Coverage Gaps and Subsection ID Remapping
category: content
date: 2026-04-12
tags: [quiz, data-quality, json, rules-coverage, deep-linking, questions]
problem_type: logic-error
components: [docs/questions.json, docs/rules.json, quiz.js]
symptoms:
  - "View Rule" deep-links pointed to parent section (e.g. 10.1) instead of the tested subsection (e.g. 10.1.3)
  - Clarification questions used display names (e.g. "Sprint Starts") not section IDs, breaking all clarification deep-links
  - Large coverage gaps — chapters 10, 17, and clarifications had many untested rules
---

# Quiz Question Coverage Gaps and Subsection ID Remapping

## Problem

The quiz's "View Rule" button uses `rules.html#{question.rule}` to deep-link to the specific rule being tested. Many questions had their `rule` field set to a parent section ID (e.g. `10.1`) when the question actually tested a specific subsection (e.g. `10.1.3`). This caused the link to land at the top of a section group rather than the exact rule being tested.

Clarification questions were worse: `rule` was set to human-readable display names like `"Sprint Starts"` which don't match any ID in `rules.json`, so the link went nowhere.

Additionally, coverage analysis revealed chapters 10, 17, and all three clarification rules were substantially under-tested.

## Root Cause

Questions were originally authored with the parent section ID for convenience (e.g. `10.19` rather than `10.19.3`). The quiz schema doesn't enforce that `rule` must be a leaf subsection ID, so mismatches silently passed validation.

Clarification sections have non-obvious IDs (`clarif-sprint-starts`, `clarif-defenders-paddle`, `clarif-illegal-hand-tackle`) that weren't documented prominently, so questions used prose labels instead.

## Investigation

### Coverage gap analysis

Built a Python script to cross-reference all subsection IDs from `rules.json` against `rule` values in `questions.json`, filtered to quiz scope (`{8, 9, 10, 11, 17, 'clarifications'}`):

```python
QUIZ_SCOPE = {8, 9, 10, 11, 17, 'clarifications'}

with open('docs/rules.json') as f:
    rules = json.load(f)
with open('docs/questions.json') as f:
    questions = json.load(f)

covered = {q['rule'] for q in questions}
gaps = []

for chapter in rules:
    ch = chapter['chapter']
    if ch not in QUIZ_SCOPE:
        continue
    for section in chapter['sections']:
        for sub in section.get('subsections', []):
            if sub['id'] not in covered:
                gaps.append(sub['id'])
```

Output: 100+ uncovered subsections in scope. Results saved to `quiz_coverage_gaps.md`.

### Remapping existing questions

Each question's `explanation` consistently cites the specific sub-rule being tested (e.g. "Rule 10.19.3 states..."), making it unambiguous which subsection ID was intended. Built a `REMAPS` dictionary of 102 entries mapping question ID → correct subsection ID.

## Solution

### Step 1: Build REMAPS dict from explanation text

```python
REMAPS = {
    'ch10-r101-001': '10.1.1',
    'ch10-r101-002': '10.1.2',
    # ... 102 total entries
    'clarif-sprint1-001': 'clarif-sprint-starts',
    'clarif-defender-001': 'clarif-defenders-paddle',
}

for q in questions:
    if q['id'] in REMAPS:
        q['rule'] = REMAPS[q['id']]
```

### Step 2: q() helper for consistent new question authoring

```python
def q(id, chapter, rule, question, options, correct, explanation, source='rules'):
    return {
        'id': id, 'source': source, 'chapter': chapter, 'rule': rule,
        'question': question, 'options': options,
        'correctIndex': correct, 'explanation': explanation, 'image': None
    }
```

The `rule` parameter here is always the leaf subsection ID (e.g. `'10.19.3'`), not a parent.

### Step 3: Duplicate-safe insertion

```python
existing_ids = {q['id'] for q in questions}
for nq in NEW_QUESTIONS:
    if nq['id'] not in existing_ids:
        questions.append(nq)
        existing_ids.add(nq['id'])
```

### Step 4: Signal-only rules — use section title, not signal numbers

Rules in chapter 15 that are signals-only should not appear in the main quiz. For rules *tested* in the main quiz that reference signals, questions should use the section title in the question stem (e.g. "Which signals apply for an **illegal kayak tackle**?") rather than asking players to name signal numbers by rote.

### Results

| Pass | Questions added | Rules remapped |
|------|----------------|----------------|
| fill_question_gaps.py | 164 | 102 |
| fill_question_gaps_2.py | 50 | — |
| **Total** | **214 new** | **102 remapped** |

Final question count: 154 → 368

## Prevention

### Add ruleId validation to validate_questions.py

```python
# Build valid leaf IDs from rules.json
valid_rule_ids = set()
for chapter in rules:
    for section in chapter['sections']:
        valid_rule_ids.add(section['id'])
        for sub in section.get('subsections', []):
            valid_rule_ids.add(sub['id'])

# Check each question
for q in questions:
    if q['rule'] not in valid_rule_ids:
        errors.append(f"{q['id']}: rule '{q['rule']}' not found in rules.json")
```

### Warn on parent-section IDs (sections that have subsections)

```python
parent_ids = {
    section['id']
    for chapter in rules
    for section in chapter['sections']
    if section.get('subsections')
}

for q in questions:
    if q['rule'] in parent_ids:
        warnings.append(f"{q['id']}: rule '{q['rule']}' is a parent section — prefer a subsection ID")
```

### Document clarification IDs explicitly

The non-obvious clarification section IDs should be listed wherever questions are authored:

| Display name | Section ID |
|---|---|
| Sprint Starts | `clarif-sprint-starts` |
| Defenders Paddle | `clarif-defenders-paddle` |
| Illegal Hand Tackle | `clarif-illegal-hand-tackle` |

## Related

- [signal-questions-in-rules-quiz-20260324.md](../logic-errors/signal-questions-in-rules-quiz-20260324.md) — related issue: signal-number questions were added to the main rules quiz; fixed by routing them to a dedicated Signals Quiz. The same principle applies here: question content must match the `rule` ID precisely.
- `quiz_coverage_gaps.md` — gap tracker in repo root; chapters 8, 9, and 11 still have partial coverage as of 2026-04-12.
- `scripts/fill_question_gaps.py` — first-pass script (164 new questions, 102 remaps)
- `scripts/fill_question_gaps_2.py` — second-pass script (50 additional questions for rules with enough substance for two)
