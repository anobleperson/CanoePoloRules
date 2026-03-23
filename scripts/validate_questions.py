#!/usr/bin/env python3
"""
validate_questions.py — Validates docs/questions.json against the required schema.

Usage:
    python3 scripts/validate_questions.py

Checks:
  - All required fields present
  - correctIndex is 0-3
  - options has exactly 4 strings
  - ids are unique
  - image paths (when non-null) exist in docs/images/
  - source is "rules" or "clarification"
  - chapter is an integer
  - question text is <= 300 chars (warning only)
"""

import json
import os
import sys

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'docs', 'questions.json')
DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

REQUIRED_FIELDS = ['id', 'source', 'chapter', 'rule', 'question', 'options', 'correctIndex', 'explanation', 'image']
VALID_SOURCES = {'rules', 'clarification'}


def validate():
    if not os.path.exists(QUESTIONS_FILE):
        print(f"ERROR: {QUESTIONS_FILE} not found")
        return False

    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        try:
            questions = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON — {e}")
            return False

    if not isinstance(questions, list):
        print("ERROR: questions.json must be a JSON array")
        return False

    errors = []
    warnings = []
    seen_ids = set()

    for i, q in enumerate(questions):
        prefix = f"Question {i+1} (id={q.get('id', '?')})"

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in q:
                errors.append(f"{prefix}: missing field '{field}'")

        if not all(f in q for f in REQUIRED_FIELDS):
            continue  # Skip further checks if fields are missing

        # id uniqueness
        if q['id'] in seen_ids:
            errors.append(f"{prefix}: duplicate id '{q['id']}'")
        seen_ids.add(q['id'])

        # source
        if q['source'] not in VALID_SOURCES:
            errors.append(f"{prefix}: source must be 'rules' or 'clarification', got '{q['source']}'")

        # chapter
        if not isinstance(q['chapter'], int):
            errors.append(f"{prefix}: chapter must be an integer")

        # options
        if not isinstance(q['options'], list) or len(q['options']) != 4:
            errors.append(f"{prefix}: options must be an array of exactly 4 strings")
        elif not all(isinstance(o, str) for o in q['options']):
            errors.append(f"{prefix}: all options must be strings")

        # correctIndex
        if not isinstance(q['correctIndex'], int) or q['correctIndex'] not in range(4):
            errors.append(f"{prefix}: correctIndex must be 0, 1, 2, or 3")

        # explanation
        if not isinstance(q['explanation'], str) or not q['explanation'].strip():
            errors.append(f"{prefix}: explanation must be a non-empty string")

        # image
        if q['image'] is not None:
            if not isinstance(q['image'], str):
                errors.append(f"{prefix}: image must be a string path or null")
            else:
                img_path = os.path.join(DOCS_DIR, q['image'])
                if not os.path.exists(img_path):
                    errors.append(f"{prefix}: image file not found: {q['image']}")

        # question length warning
        if isinstance(q['question'], str) and len(q['question']) > 300:
            warnings.append(f"{prefix}: question text is {len(q['question'])} chars (target: ≤200)")

    print(f"Validated {len(questions)} questions")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  ⚠  {w}")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  ✗  {e}")
        return False

    print(f"\n✓ All checks passed — {len(questions)} valid questions")
    print(f"  Sources: {sum(1 for q in questions if q['source']=='rules')} from rules, "
          f"{sum(1 for q in questions if q['source']=='clarification')} from clarifications")
    print(f"  Chapters: { {c: sum(1 for q in questions if q['chapter']==c) for c in sorted(set(q['chapter'] for q in questions))} }")
    print(f"  With images: {sum(1 for q in questions if q['image'])}")
    return True


if __name__ == '__main__':
    ok = validate()
    sys.exit(0 if ok else 1)
