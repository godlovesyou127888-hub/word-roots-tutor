#!/usr/bin/env python3
"""Word Roots Tutor — 100 essential roots with progress persistence."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
ROOTS_FILE = THIS_DIR.parent / "data" / "roots.json"
PROGRESS_FILE = THIS_DIR.parent / "data" / "progress.json"


def load_roots() -> list[dict]:
    with open(ROOTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {"asked": [], "updated_at": None}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress: dict) -> None:
    progress["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def mark_asked(progress: dict, root: str) -> None:
    asked = set(progress.get("asked", []))
    asked.add(root)
    progress["asked"] = sorted(asked)
    save_progress(progress)


def print_root(r: dict) -> None:
    print(
        f"\n{r['root']} ({r['pronunciation']})\n"
        f" meaning : {r['meaning']}\n"
        f" origin  : {r['origin']}\n"
        f" derived : {', '.join(r['derived'])}\n"
        f" example : {r['example_sentence']}\n"
        f" tip     : {r['mnemonic']}"
    )


def ask_random(roots: list[dict], progress: dict) -> dict | None:
    asked = set(progress.get("asked", []))
    candidates = [r for r in roots if r["root"] not in asked]
    if not candidates:
        print("review complete!")
        return None
    target = random.choice(candidates)
    print(f"Was it: {target['root']} ({target['pronunciation']}) — {target['meaning']}")
    input("Press Enter to reveal")
    print_root(target)
    mark_asked(progress, target["root"])
    return target


def quiz(roots: list[dict], progress: dict) -> dict | None:
    target = random.choice(roots)
    asked = set(progress.get("asked", []))
    print(f"\nQ: {target['quiz']}")
    input("Press Enter to reveal answer")
    print(
        f"A: {target['root']} ({target['pronunciation']}) → {target['meaning']}\n"
        f"sentence: {target['example_sentence']}"
    )
    mark_asked(progress, target["root"])
    return target


def review(roots: list[dict], progress: dict) -> dict | None:
    asked = set(progress.get("asked", []))
    pool = [r for r in roots if r["root"] in asked]
    if not pool:
        print("No roots reviewed yet — ask a few first.")
        return None
    r = random.choice(pool)
    print(f"Was it: {r['root']} ({r['pronunciation']}) — {r['meaning']}")
    input("Press Enter to reveal")
    print_root(r)
    return r


def lookup(roots: list[dict], text: str) -> None:
    find = text.strip().lower()
    hits = [
        r
        for r in roots
        if find in r["root"].lower() or find in r["meaning"].lower()
    ]
    if not hits:
        print("no match")
        return
    for r in hits:
        print_root(r)


def list_roots(roots: list[dict], limit: int | None = None) -> None:
    items = roots[:limit] if limit else roots
    print(f"\n=== roots ({len(items)}) ===")
    for r in items:
        print(f"{r['root']:10s} | {r['meaning']}")


def progress_status(roots: list[dict], progress: dict) -> None:
    asked = set(progress.get("asked", []))
    print(f"reviewed: {len(asked)} / {len(roots)}")
    if progress.get("updated_at"):
        print(f"last save: {progress['updated_at']}")


def export_csv(roots: list[dict], progress: dict) -> None:
    asked = set(progress.get("asked", []))
    path = THIS_DIR.parent / "data" / "progress.csv"
    import csv

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["root", "meaning", "reviewed"])
        for r in roots:
            writer.writerow([r["root"], r["meaning"], "yes" if r["root"] in asked else "no"])
    print(f"exported to {path}")


def reset_progress(progress: dict) -> None:
    progress["asked"] = []
    progress["updated_at"] = None
    save_progress(progress)
    print("progress reset")


def main() -> int:
    roots = load_roots()
    progress_data = load_progress()
    print(
        "WORD ROOTS TUTOR",
        "commands:",
        "  ask | quiz | review | list [n] | progress",
        "  <root/word> | help | exit",
        "",
        sep="\n",
    )
    while True:
        raw = input(">>> ").strip()
        if not raw:
            continue
        cmd, *args = raw.split()
        c = cmd.lower()
        if c in {"exit", "quit", "q"}:
            break
        if c in {"help", "?"}:
            print("ask | quiz | review | list [n] | progress | <root/word> | help | exit")
            continue
        if c == "progress":
            progress_status(roots, progress_data)
            continue
        if c == "review":
            review(roots, progress_data)
            continue
        if c == "quiz":
            quiz(roots, progress_data)
            continue
        if c == "list":
            n = int(args[0]) if args and args[0].isdigit() else None
            list_roots(roots, n)
            continue
        if c == "ask":
            ask_random(roots, progress_data)
            continue
        if c == "export":
            export_csv(roots, progress_data)
            continue
        if c == "reset":
            reset_progress(progress_data)
            continue
        lookup(roots, raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
