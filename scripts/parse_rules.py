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
CLARIF_MD = os.path.join(os.path.dirname(__file__), '..', 'rules_extract', '2025_icf_canoe_polo_rule_clarifications.md')
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
# Some sections lack ## and are just bold: **10.11 - REFEREE'S BALL [SR]**
SECTION_HEADING_BOLD_RE = re.compile(r'^\*\*(\d+)\.(\d+(?:\.\d+)*)\s*[-–]\s*(.+?)\*\*\s*$')
CHAPTER_START_RE = re.compile(r'^##\s+\*?\*?CHAPTER\s+(\d+)', re.IGNORECASE)

# Sub-rule inline pattern: "10.22.3.a - text..."
SUBRULE_INLINE_RE = re.compile(r'^(\d+(?:\.\d+)+)\s*[-–]\s+(.+)$')

# Governance tag lines like ## **[SR]** or standalone **[SR]**
GOVERNANCE_RE = re.compile(r'^(?:##\s+)?\*?\*?\[(?:SR|PR|CR)\]\*?\*?\s*$')

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
            lines_out = [
                line.strip() for line in current_text_lines
                if line.strip()
                and not PAGE_BREAK_RE.match(line.strip())
                and not IMAGE_RE.match(line.strip())
                and not GOVERNANCE_RE.match(line.strip())
            ]
            current_section['text'] = '\n'.join(lines_out)

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

        m_section = SECTION_HEADING_RE.match(line_stripped) or SECTION_HEADING_BOLD_RE.match(line_stripped)
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


def parse_clarifications():
    """Parse the rule clarifications markdown into a chapter-like structure."""
    # Topic names map (part numbers stripped) → canonical id/heading
    TOPICS = {
        'SPRINT STARTS': ('clarif-sprint-starts', 'Sprint Starts'),
        "DEFENDER'S PADDLE": ('clarif-defenders-paddle', "Defender's Paddle"),
        'ILLEGAL HAND TACKLE': ('clarif-illegal-hand-tackle', 'Illegal Hand Tackle'),
    }
    # Pattern: ALL CAPS heading optionally followed by (N); allow smart apostrophe
    HEADING_RE = re.compile(r"^([A-Z][A-Z\s'\u2019]+[A-Z])(?:\s*\(\d+\))?\s*$")

    def normalise(s):
        return s.replace('\u2019', "'").replace('\u2018', "'")
    PAGE_RE = re.compile(r'^<!--\s*Page')
    CLARIF_PAGE_BREAK_RE = re.compile(r'^ICF Canoe Polo\s*$|^\d+\s*$')

    sections = {}  # topic_key -> {'id', 'heading', 'lines'}
    current_key = None

    with open(CLARIF_MD, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        ls = line.rstrip('\n').strip()
        if not ls or PAGE_RE.match(ls) or IMAGE_RE.match(ls) or CLARIF_PAGE_BREAK_RE.match(ls):
            continue
        # Detect topic heading
        m = HEADING_RE.match(ls)
        if m:
            topic = normalise(m.group(1).strip())
            if topic in TOPICS:
                current_key = topic
                if topic not in sections:
                    tid, theading = TOPICS[topic]
                    sections[topic] = {'id': tid, 'heading': theading, 'lines': []}
                continue
            # Sub-headings (e.g. "Not at the Same Time:") — keep as text
        if current_key:
            sections[current_key]['lines'].append(ls)

    result_sections = []
    for topic_key in ['SPRINT STARTS', "DEFENDER'S PADDLE", 'ILLEGAL HAND TACKLE']:
        if topic_key in sections:
            s = sections[topic_key]
            result_sections.append({
                'id': s['id'],
                'heading': s['heading'],
                'text': '\n'.join(l for l in s['lines'] if l),
                'subsections': [],
            })

    return {
        'chapter': 'clarifications',
        'title': 'Rule Clarifications',
        'sections': result_sections,
    }


def main():
    print("Parsing rules markdown...")
    chapters = parse_rules()

    print("Parsing clarifications...")
    clarif_chapter = parse_clarifications()
    chapters.append(clarif_chapter)

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
