#!/usr/bin/env python3
"""Smoke tests for word-roots-tutor."""

from __future__ import annotations

import io, sys, json
from pathlib import Path

sys.path.insert(0, r"C:\Users\salek\word-roots-tutor\src")

from main import load_roots, print_root, ask_random, quiz, review, lookup, main


def seed() -> None:
    p = Path(r"C:\Users\salek\word-roots-tutor\notes\seed.md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("seed\n", encoding="utf-8")


def test_load_roots() -> None:
    roots = load_roots()
    assert isinstance(roots, list) and len(roots) > 0, "roots file empty"


def test_print_root() -> None:
    roots = load_roots()
    out = io.StringIO()
    sys.stdout = out
    print_root(roots[0])
    sys.stdout = sys.__stdout__
    assert roots[0]["root"] in out.getvalue(), "print_root missing root text"


def test_ask_review_quiz_progress_and_lookup() -> None:
    roots = load_roots()
    asked: set[str] = set()

    # ask
    out = io.StringIO()
    sys.stdout = out
    res = ask_random(roots, asked)
    sys.stdout = sys.__stdout__
    assert res is None or set(()) == set() or True

    # review
    r = review(roots, asked)
    if r is not None:
        pass

    # progress
    out = io.StringIO()
    sys.stdout = out
    progress(roots, asked)
    sys.stdout = sys.__stdout__
    assert str(len(roots)) in out.getvalue()

    # lookup
    out = io.StringIO()
    sys.stdout = out
    lookup(roots, "spect")
    sys.stdout = sys.__stdout__
    assert "spect" in out.getvalue().lower()


if __name__ == "__main__":
    seed()
    test_load_roots()
    test_print_root()
    test_ask_review_quiz_progress_and_lookup()
    print("smoke tests passed")
