#!/usr/bin/env python3
"""
parse_rules.py — Parses the ICF Canoe Polo rules markdown (chapters 7-11)
into a structured rules.json for the rules viewer.

Usage:
    python3 scripts/parse_rules.py

Output:
    docs/rules.json
"""

import json
import re
import os

RULES_MD = os.path.join(os.path.dirname(__file__), '..', 'rules_extract', '2025_icf_canoe_polo_rules.md')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'rules.json')

CHAPTER_TITLES = {
    7: "Officials",
    8: "Equipment and Playing Area",
    9: "Competition Schedule",
    10: "Game Play",
    11: "Protests and Disciplinary",
}

# Chapter heading pattern: ## **7.1 - COMPETITION COMMITTEE**
SECTION_HEADING_RE = re.compile(r'^##\s+\*?\*?(\d+)\.(\d+(?:\.\d+)*)\s*[-–]\s*(.+?)\*?\*?\s*$')
CHAPTER_START_RE = re.compile(r'^##\s+\*?\*?CHAPTER\s+(\d+)', re.IGNORECASE)

# Sub-rule inline pattern: "10.22.3.a - text..."
SUBRULE_INLINE_RE = re.compile(r'^(\d+(?:\.\d+)+)\s*[-–]\s+(.+)$')

# Governance tag lines like ## **[SR]**
GOVERNANCE_RE = re.compile(r'^##\s+\*?\*?\[(?:SR|PR|CR)\]\*?\*?\s*$')

# Page break artifacts
PAGE_BREAK_RE = re.compile(r'^ICF Canoe Polo Competition Rules 2025 \d+ of 134')

# Image lines
IMAGE_RE = re.compile(r'^\!\[')


def clean_heading(text):
    return re.sub(r'\*+', '', text).strip()


def parse_rules():
    with open(RULES_MD, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    chapters = []
    current_chapter = None
    current_section = None
    current_text_lines = []

    def flush_section():
        if current_section is not None:
            text = ' '.join(
                line.strip() for line in current_text_lines
                if line.strip()
                and not PAGE_BREAK_RE.match(line.strip())
                and not IMAGE_RE.match(line.strip())
                and not GOVERNANCE_RE.match(line.strip())
            )
            current_section['text'] = text

    in_scope = False

    for line in lines:
        line_stripped = line.rstrip('\n')

        # Detect chapter 7 start
        m_chapter = CHAPTER_START_RE.match(line_stripped)
        if m_chapter:
            ch_num = int(m_chapter.group(1))
            if 7 <= ch_num <= 11:
                flush_section()
                current_chapter = {
                    'chapter': ch_num,
                    'title': CHAPTER_TITLES.get(ch_num, f'Chapter {ch_num}'),
                    'sections': []
                }
                chapters.append(current_chapter)
                current_section = None
                current_text_lines = []
                in_scope = True
            elif ch_num > 11:
                flush_section()
                in_scope = False
            continue

        m_section = SECTION_HEADING_RE.match(line_stripped)
        if m_section:
            ch_num = int(m_section.group(1))
            if 7 <= ch_num <= 11:
                flush_section()
                in_scope = True

                # Ensure we have the right chapter
                if current_chapter is None or current_chapter['chapter'] != ch_num:
                    # Find or create chapter
                    existing = next((c for c in chapters if c['chapter'] == ch_num), None)
                    if existing:
                        current_chapter = existing
                    else:
                        current_chapter = {
                            'chapter': ch_num,
                            'title': CHAPTER_TITLES.get(ch_num, f'Chapter {ch_num}'),
                            'sections': []
                        }
                        chapters.append(current_chapter)

                rule_num = f"{ch_num}.{m_section.group(2)}"
                heading = clean_heading(m_section.group(3))
                current_section = {
                    'id': rule_num,
                    'heading': heading,
                    'text': '',
                    'subsections': []
                }
                current_chapter['sections'].append(current_section)
                current_text_lines = []
            elif ch_num > 11:
                flush_section()
                in_scope = False
            continue

        if not in_scope:
            continue

        # Skip governance tags, page breaks, images
        if GOVERNANCE_RE.match(line_stripped):
            continue
        if PAGE_BREAK_RE.match(line_stripped.strip()):
            continue
        if IMAGE_RE.match(line_stripped.strip()):
            continue

        # Accumulate text for current section
        if current_section is not None and line_stripped.strip():
            current_text_lines.append(line_stripped)

    flush_section()

    # Sort chapters
    chapters.sort(key=lambda c: c['chapter'])

    return chapters


def main():
    print("Parsing rules markdown...")
    chapters = parse_rules()

    total_sections = sum(len(c['sections']) for c in chapters)
    print(f"Found {len(chapters)} chapters, {total_sections} sections")
    for c in chapters:
        print(f"  Chapter {c['chapter']} ({c['title']}): {len(c['sections'])} sections")

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)

    print(f"Written to {OUTPUT}")


if __name__ == '__main__':
    main()
