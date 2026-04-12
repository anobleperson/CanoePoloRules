#!/usr/bin/env python3
"""
fix_heading_levels.py — Fix heading levels in the rules markdown.

The PDF extraction produced a flat heading structure where everything uses ##.
This script corrects the hierarchy:

  # CHAPTER X           (was ## **CHAPTER X**)
  ## X.Y - SECTION      (unchanged — main sections stay at h2)
  ### X.Y.Z - sub-rule  (was ## X.Y.Z, or plain text — all three-level numeric items)
  plain text            (X.Y.Z.a letter-suffix items are body text, not headings)
  plain text            (governance tags [SR]/[PR]/[CR] are not headings)

Usage:
    python3 scripts/fix_heading_levels.py [--dry-run]
"""

import re
import sys
import os

RULES_MD = os.path.join(os.path.dirname(__file__), '..', 'rules_extract', '2025_icf_canoe_polo_rules.md')

# --- Patterns for items that ARE currently ## headings ---

# Chapter headings: ## **CHAPTER X - ...**
CHAPTER_RE = re.compile(r'^(## )(\*?\*?CHAPTER\s+\d+.*)$', re.IGNORECASE)

# Governance tags: ## **[SR]** or ## [SR] etc.
GOVERNANCE_RE = re.compile(r'^## (\*?\*?\[(?:SR|PR|CR)\]\*?\*?)\s*$')

# Four-level with letter suffix: ## 1.6.1.c - ...  or ## 16.11.9.b - ...
# These are incorrectly marked as headings and should be plain text.
HEADING_4LEVEL_RE = re.compile(r'^## (\*?\*?\d+\.\d+\.\d+\.?[a-z]\s*[-–].+)$')

# Three-level numeric: ## 10.19.2 - ...  or ## **10.5.1 - title**
# These should be ### (h3)
HEADING_3LEVEL_RE = re.compile(r'^## (\*?\*?\d+\.\d+\.\d+\s*[-–].+)$')

# Specific body-text lines that were mistakenly given ## markers.
# Only two confirmed cases; listed explicitly to avoid false positives.
BODYTEXT_HEADING_LINES = {
    '## The Chief Scrutineer will: ',
    '## The Chief Scrutineer will:',
    '## The official events recognised by the ICF are the following: ',
    '## The official events recognised by the ICF are the following:',
}

# --- Pattern for plain-text three-level items that should become ### ---
# Matches lines like:
#   7.3.1 - International competitions...
#   - 1.9.3 - Individual entries...
#   * 10.30.1 - Signal 15 applies.
# But NOT four-level letter items like 1.6.1.a, 10.5.1.a, 16.11.9.b
PLAIN_3LEVEL_RE = re.compile(
    r'^'
    r'(?P<prefix>[-*\s]*)'                 # optional leading - * or spaces (list marker)
    r'(?P<num>\d+\.\d+\.\d+)'             # exactly three numeric levels: X.Y.Z
    r'(?P<after>\s*[-–]\s+.+)$'           # followed immediately by a dash separator
)
# A line is four-level if the three-level match is immediately followed by a letter or dot+letter
FOUR_LEVEL_SUFFIX_RE = re.compile(r'^\d+\.\d+\.\d+\.?[a-z]\s*[-–]')


def is_already_heading(line):
    """Return True if the line already starts with # (any level)."""
    return line.startswith('#')


def fix_line(line):
    """Apply heading-level corrections to a single line. Returns the fixed line."""

    # 1. Chapter headings: ## **CHAPTER X** → # **CHAPTER X**
    m = CHAPTER_RE.match(line)
    if m:
        return '# ' + m.group(2)

    # 2. Governance tags: ## **[SR]** → **[SR]**
    m = GOVERNANCE_RE.match(line)
    if m:
        return m.group(1)

    # 3. Four-level letter items wrongly given ##: demote to plain text
    m = HEADING_4LEVEL_RE.match(line)
    if m:
        return m.group(1)

    # 4. Three-level numeric items at wrong level: ## X.Y.Z → ### X.Y.Z
    m = HEADING_3LEVEL_RE.match(line)
    if m:
        return '### ' + m.group(1)

    # 5. Specific body-text lines mistakenly given ##: remove the ##
    stripped_line = line.rstrip()
    if stripped_line in BODYTEXT_HEADING_LINES:
        return line[3:]  # strip leading '## '

    # 6. Plain-text three-level items that should be ### headings
    if not is_already_heading(line):
        m = PLAIN_3LEVEL_RE.match(line)
        if m:
            # Ensure it's not actually four-level (letter suffix right after the digits)
            rest_of_line = line[len(m.group('prefix')):]  # line without the list prefix
            if not FOUR_LEVEL_SUFFIX_RE.match(rest_of_line):
                return '### ' + m.group('num') + m.group('after')

    return line


def main():
    dry_run = '--dry-run' in sys.argv

    with open(RULES_MD, 'r', encoding='utf-8') as f:
        original = f.read()

    lines = original.splitlines(keepends=True)
    fixed_lines = []
    changes = []

    for i, line in enumerate(lines, start=1):
        stripped = line.rstrip('\n')
        fixed = fix_line(stripped)
        if fixed != stripped:
            changes.append((i, stripped, fixed))
        fixed_lines.append(fixed + ('\n' if line.endswith('\n') else ''))

    print(f"Total changes: {len(changes)}")
    for lineno, old, new in changes:
        print(f"  line {lineno:4d}: {repr(old[:80])} → {repr(new[:80])}")

    if not dry_run:
        with open(RULES_MD, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        print(f"\nWritten to {RULES_MD}")
    else:
        print("\n(dry run — no file written)")


if __name__ == '__main__':
    main()
