# Canoe Polo Rules Quiz

An interactive web app for canoe polo referees to self-study the 2025 ICF Competition Rules.

**Live app:** [GitHub Pages URL — set after first deploy]

## Features

- **Quiz**: 20 random multiple-choice questions per session drawn from a 150+ question bank covering ICF rules chapters 7–11 and rule clarifications. Immediate feedback with rule citation after each answer.
- **Rules Viewer**: Collapsible chapter/rule navigation for all chapters 7–11. Deep-linkable via URL hash (e.g. `rules.html#10.22.3`).

## Local Development

The app is plain HTML/CSS/JS with no build step. Because `fetch()` fails on `file://` URLs, use a local server:

```bash
cd docs
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080).

## Project Structure

```
rules_extract/          Source rules PDFs extracted to markdown + images
scripts/                Offline developer tools
  parse_rules.py        Parses rules markdown → docs/rules.json
  generate_questions.py Template for AI-assisted question generation
  validate_questions.py Validates docs/questions.json schema
docs/                   GitHub Pages source root
  index.html            Quiz app
  quiz.js
  rules.html            Rules viewer
  rules.js
  shared.css
  quiz.css
  rules.css
  questions.json        Pre-generated question bank (committed)
  rules.json            Pre-parsed rules tree (committed)
  images/               Rule diagram images used by questions
```

## Regenerating Content

### rules.json

```bash
python3 scripts/parse_rules.py
```

### questions.json

Edit `scripts/generate_questions.py` with your preferred LLM API, then run:

```bash
python3 scripts/generate_questions.py
python3 scripts/validate_questions.py
```

## GitHub Pages Setup

1. Push this repo to GitHub
2. Go to Settings → Pages
3. Set Source to "Deploy from a branch", branch `main`, folder `/docs`
4. Save — the app will be live at `https://<username>.github.io/<repo>/`

## Rules Source

Based on the [2025 ICF Canoe Polo Competition Rules](https://www.canoeicf.com/rules).
