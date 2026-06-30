---
name: word-roots-tutor
description: Use when practicing or teaching the 100 essential English word roots. Covers quiz, review, lookup, and progress tracking for root-based vocabulary learning.
version: 1.0.0
author: Gary
license: MIT
metadata:
  hermes:
    tags: [education, vocabulary, english, tutoring, word-roots]
    related_skills: []
---

# Word Roots Tutor

## Overview

Teach and practice the 100 essential English word roots through interactive
drills. The tutor keeps local progress so you can resume study sessions and
focus on weak roots.

## When to Use

- User asks to quiz or review word roots.
- User wants progress on root memorization.
- User asks for a root's meaning, origin, or example words.

## Project Layout

- `data/roots.json` — root bank (100 items).
- `data/progress.json` — asked history + last-save timestamp.
- `src/main.py` — CLI entrypoint.

## Usage

Run from the project directory:

```bash
python src/main.py
```

Commands:

- `ask` — ask one unrevealed root (stopping when all are asked).
- `quiz` — sentence-style quiz.
- `review` — re-ask a previously revealed root.
- `list [n]` — show roots, optionally limited.
- `progress` — show progress and last save time.
- `export` — write `data/progress.csv` with reviewed status.
- `reset` — clear `data/progress.json` to start fresh.
- `<root/word>` — lookup by root or meaning.

## Common Pitfalls

- Don't manually edit `progress.json` while the tutor is running.
- `roots.json` must keep the required fields per entry:
  `root`, `pronunciation`, `meaning`, `origin`,
  `derived`, `example_sentence`, `mnemonic`, `quiz`.

## Verification Checklist

- [ ] `python src/main.py` reaches the `>>>` prompt.
- [ ] `ask` advances `reviewed` count and updates `data/progress.json`.
- [ ] `progress` reports the updated count.
- [ ] `export` produces a readable `data/progress.csv`.
