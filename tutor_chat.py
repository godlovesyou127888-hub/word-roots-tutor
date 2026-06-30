#!/usr/bin/env python3
"""Simple interactive wrapper for word-roots-tutor."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from main import (
    load_roots,
    load_progress,
    save_progress,
    ask_random,
    quiz,
    review,
    list_roots,
    progress_status,
    lookup,
    export_csv,
    reset_progress,
    print_root,
)

roots = load_roots()
progress = load_progress()

while True:
    try:
        raw = input(">>> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if not raw:
        continue

    cmd, *args = raw.split()
    c = cmd.lower()

    if c in {"exit", "quit", "q"}:
        save_progress(progress)
        print("已儲存進度，再見！")
        break
    if c in {"help", "?"}:
        print("ask | quiz | review | list [n] | progress | export | reset | <root/word> | help | exit")
        continue
    if c == "progress":
        progress_status(roots, progress)
        continue
    if c == "review":
        review(roots, progress)
        continue
    if c == "quiz":
        quiz(roots, progress)
        continue
    if c == "list":
        n = int(args[0]) if args and args[0].isdigit() else None
        list_roots(roots, n)
        continue
    if c == "ask":
        ask_random(roots, progress)
        continue
    if c == "export":
        export_csv(roots, progress)
        continue
    if c == "reset":
        if input("確定要重置進度嗎？ (y/N): ").strip().lower() == "y":
            reset_progress(progress)
        continue
    lookup(roots, raw)
