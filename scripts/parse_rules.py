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
    15: "Referee Hand Signals",
    17: "Shot Clock",
}

CHAPTERS_IN_SCOPE = {7, 8, 9, 10, 11, 15, 17}

# Chapter heading pattern: ## **7.1 - COMPETITION COMMITTEE**
SECTION_HEADING_RE = re.compile(r'^##\s+\*?\*?(\d+)\.(\d+(?:\.\d+)*)\s*[-–]\s*(.+?)\*?\*?\s*$')
# Some sections lack ## and are just bold: **10.11 - REFEREE'S BALL [SR]**
SECTION_HEADING_BOLD_RE = re.compile(r'^\*\*(\d+)\.(\d+(?:\.\d+)*)\s*[-–]\s*(.+?)\*\*\s*$')
# Chapter 15 uses ### headings with no dash: ### 15.1 START / INFRINGEMENT
SECTION_HEADING_H3_RE = re.compile(r'^###\s+(\d+)\.(\d+(?:\.\d+)*)[.\s]+(.+)$')
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
        if current_section is not None and '_chapter' in current_section:
            ch_num = current_section.pop('_chapter')
            include_images = (ch_num == 15)
            lines_out = []
            for line in current_text_lines:
                ls = line.strip()
                if not ls:
                    continue
                if PAGE_BREAK_RE.match(ls):
                    continue
                if GOVERNANCE_RE.match(ls):
                    continue
                if IMAGE_RE.match(ls):
                    if include_images:
                        # Extract filename from ![](images/filename.png)
                        m = re.match(r'^\!\[\]\(images/(.+?)\)', ls)
                        if m:
                            lines_out.append('IMAGE:' + m.group(1))
                    continue
                lines_out.append(ls)
            current_section['text'] = '\n'.join(lines_out)

    def find_or_create_chapter(ch_num):
        existing = next((c for c in chapters if c['chapter'] == ch_num), None)
        if existing:
            return existing
        ch = {
            'chapter': ch_num,
            'title': CHAPTER_TITLES.get(ch_num, f'Chapter {ch_num}'),
            'sections': []
        }
        chapters.append(ch)
        return ch

    def start_section(ch_num, sub, heading_raw):
        nonlocal current_chapter, current_section, current_text_lines
        flush_section()
        in_scope_flag = True
        current_chapter = find_or_create_chapter(ch_num)
        rule_num = f"{ch_num}.{sub}"
        current_section = {
            'id': rule_num,
            'heading': clean_heading(heading_raw),
            'text': '',
            'subsections': [],
            '_chapter': ch_num,
        }
        current_chapter['sections'].append(current_section)
        current_text_lines = []
        return in_scope_flag

    in_scope = False

    for line in lines:
        line_stripped = line.rstrip('\n')

        # Detect chapter start
        m_chapter = CHAPTER_START_RE.match(line_stripped)
        if m_chapter:
            ch_num = int(m_chapter.group(1))
            if ch_num in CHAPTERS_IN_SCOPE:
                flush_section()
                current_chapter = find_or_create_chapter(ch_num)
                current_section = None
                current_text_lines = []
                in_scope = True
            else:
                flush_section()
                in_scope = False
            continue

        # Try all section heading patterns
        m_section = (SECTION_HEADING_RE.match(line_stripped)
                     or SECTION_HEADING_BOLD_RE.match(line_stripped)
                     or SECTION_HEADING_H3_RE.match(line_stripped))
        if m_section:
            ch_num = int(m_section.group(1))
            if ch_num in CHAPTERS_IN_SCOPE:
                in_scope = start_section(ch_num, m_section.group(2), m_section.group(3))
            else:
                flush_section()
                in_scope = False
            continue

        if not in_scope:
            continue

        # Accumulate text for current section (filtering happens in flush_section)
        if current_section is not None and line_stripped.strip():
            current_text_lines.append(line_stripped)

    flush_section()

    # Sort chapters
    chapters.sort(key=lambda c: c['chapter'])

    return chapters


def parse_clarifications():
    """Parse the rule clarifications markdown into a chapter-like structure."""
    def normalise(s):
        return s.replace('\u2019', "'").replace('\u2018', "'")

    TOPICS = {
        'SPRINT STARTS': ('clarif-sprint-starts', 'Sprint Starts'),
        "DEFENDER'S PADDLE": ('clarif-defenders-paddle', "Defender's Paddle"),
        'ILLEGAL HAND TACKLE': ('clarif-illegal-hand-tackle', 'Illegal Hand Tackle'),
    }
    SKIP_HEADINGS = {'WWW.CANOEICF.COM/RULES', 'CONTENTS', 'Contents'}
    H2_RE = re.compile(r'^##\s+(.+)$')
    PART_RE = re.compile(r'\s*\(\d+\)\s*$')

    sections = {}
    order = []
    current_key = None

    with open(CLARIF_MD, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        ls = line.rstrip('\n').strip()
        if not ls or IMAGE_RE.match(ls):
            continue

        m = H2_RE.match(ls)
        if m:
            raw = normalise(m.group(1).strip())
            topic = PART_RE.sub('', raw).strip()
            if topic in SKIP_HEADINGS or topic not in TOPICS:
                current_key = None
                continue
            current_key = topic
            if topic not in sections:
                tid, theading = TOPICS[topic]
                sections[topic] = {'id': tid, 'heading': theading, 'lines': []}
                order.append(topic)
            continue

        if ls.startswith('# '):
            current_key = None
            continue

        if current_key:
            text_line = re.sub(r'^[*\-]\s+', '\u2022 ', ls)
            text_line = re.sub(r'_(.+?)_', r'\1', text_line)
            sections[current_key]['lines'].append(text_line)

    result_sections = []
    for topic_key in order:
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
