#!/usr/bin/env python3
"""
generate_questions.py — Generates docs/questions.json using an LLM.

Requires: pip install anthropic
Set ANTHROPIC_API_KEY environment variable before running.

Usage:
    python3 scripts/generate_questions.py [--chapter 10] [--dry-run]

This script is provided as a template for re-generating the question bank.
The current docs/questions.json was generated directly by Claude Code.
"""

import json
import os
import re
import sys
import argparse

try:
    import anthropic
except ImportError:
    print("anthropic package not found. Install with: pip install anthropic")
    sys.exit(1)

RULES_MD = os.path.join(os.path.dirname(__file__), '..', 'rules_extract', '2025_icf_canoe_polo_rules.md')
CLARIF_MD = os.path.join(os.path.dirname(__file__), '..', 'rules_extract', '2025_icf_canoe_polo_rule_clarifications.md')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'questions.json')

SYSTEM_PROMPT = """You are generating multiple-choice quiz questions for canoe polo referees studying the ICF 2025 rules.

For each rule or sub-rule provided, generate 2-4 questions. Each question must:
- Be unambiguous and answerable from the rule text alone
- Have exactly 4 options, one definitively correct
- Include a concise explanation citing the specific rule number
- Target under 200 characters for the question text

Prefer questions about: specific numbers/thresholds, definitions, what a referee must do (not may do), penalty outcomes, and exception conditions.

Respond ONLY with a JSON array of question objects:
[{
  "rule": "<rule number or clarification topic>",
  "question": "<question text>",
  "options": ["<opt1>", "<opt2>", "<opt3>", "<opt4>"],
  "correctIndex": <0-3>,
  "explanation": "<explanation citing rule>"
}]"""

SECTION_HEADING_RE = re.compile(r'^##\s+\*?\*?(\d+)\.(\d+(?:\.\d+)*)\s*[-–]\s*(.+?)\*?\*?\s*$')


def extract_chapter_sections(filepath, target_chapters=(7, 8, 9, 10, 11)):
    """Extract text for each numbered section in the target chapters."""
    sections = []
    current_section = None
    current_lines = []
    in_scope = False

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            m = SECTION_HEADING_RE.match(line)
            if m:
                ch = int(m.group(1))
                if ch in target_chapters:
                    if current_section:
                        current_section['text'] = '\n'.join(current_lines)
                        sections.append(current_section)
                    current_section = {
                        'chapter': ch,
                        'rule': f"{ch}.{m.group(2)}",
                        'heading': re.sub(r'\*+', '', m.group(3)).strip(),
                        'source': 'rules',
                    }
                    current_lines = []
                    in_scope = True
                elif ch > max(target_chapters):
                    if current_section:
                        current_section['text'] = '\n'.join(current_lines)
                        sections.append(current_section)
                        current_section = None
                    in_scope = False
                continue
            if in_scope and current_section and line.strip():
                if not line.startswith('![') and 'ICF Canoe Polo Competition Rules' not in line:
                    current_lines.append(line.strip())

    if current_section:
        current_section['text'] = '\n'.join(current_lines)
        sections.append(current_section)

    return sections


def generate_for_section(client, section, dry_run=False):
    """Call LLM to generate questions for one rule section."""
    prompt = f"""Rule {section['rule']}: {section['heading']}

{section['text'][:2000]}"""

    if dry_run:
        print(f"  [DRY RUN] Would generate questions for {section['rule']}")
        return []

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text.strip()
    # Extract JSON array
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        print(f"  WARNING: No JSON array found for {section['rule']}")
        return []

    try:
        raw_questions = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse error for {section['rule']}: {e}")
        return []

    questions = []
    for j, q in enumerate(raw_questions):
        questions.append({
            'id': f"ch{section['chapter']}-r{section['rule'].replace('.', '')}-{j+1:03d}",
            'source': section.get('source', 'rules'),
            'chapter': section['chapter'],
            'rule': section['rule'],
            'question': q.get('question', ''),
            'options': q.get('options', []),
            'correctIndex': q.get('correctIndex', 0),
            'explanation': q.get('explanation', ''),
            'image': None,
        })

    return questions


def main():
    parser = argparse.ArgumentParser(description='Generate questions.json from rules markdown')
    parser.add_argument('--chapter', type=int, help='Only generate for one chapter (7-11)')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be done, no API calls')
    args = parser.parse_args()

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key and not args.dry_run:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key) if not args.dry_run else None

    chapters = [args.chapter] if args.chapter else [7, 8, 9, 10, 11]
    sections = extract_chapter_sections(RULES_MD, target_chapters=chapters)
    print(f"Found {len(sections)} sections across chapters {chapters}")

    all_questions = []
    for i, section in enumerate(sections):
        print(f"[{i+1}/{len(sections)}] Generating for {section['rule']}: {section['heading']}")
        qs = generate_for_section(client, section, dry_run=args.dry_run)
        all_questions.extend(qs)
        print(f"  → {len(qs)} questions")

    if not args.dry_run:
        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        with open(OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(all_questions, f, indent=2, ensure_ascii=False)
        print(f"\nWritten {len(all_questions)} questions to {OUTPUT}")
        print("Run python3 scripts/validate_questions.py to validate.")


if __name__ == '__main__':
    main()
