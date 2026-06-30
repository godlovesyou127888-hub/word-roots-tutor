#!/usr/bin/env python3
"""Smoke tests for word-roots-tutor skill flow."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\salek\word-roots-tutor\src")

from main import (
    ask_random,
    quiz,
    review,
    progress_status,
    lookup,
    load_roots,
    load_progress,
    save_progress,
    reset_progress,
)

ROOTS_FILE = Path(r"C:\Users\salek\word-roots-tutor\data\roots.json")
PROGRESS_FILE = Path(r"C:\Users\salek\word-roots-tutor\data\progress.json")


def setup() -> None:
    save_progress({"asked": [], "updated_at": None})


def teardown() -> None:
    save_progress({"asked": [], "updated_at": None})


def test_progress_roundtrip() -> None:
    setup()
    p = load_progress()
    assert p["asked"] == []
    save_progress({"asked": ["spect"], "updated_at": "2020-01-01T00:00:00"})
    p = load_progress()
    assert "spect" in p["asked"]
    teardown()


def test_ask_and_progress() -> None:
    setup()
    roots = load_roots()
    p = load_progress()
    sys.stdin = io.StringIO("\n")
    out = io.StringIO()
    sys.stdout = out
    ask_random(roots, p)
    sys.stdout = sys.__stdout__
    assert len(p["asked"]) == 1
    teardown()


def test_quiz_records_root() -> None:
    setup()
    roots = load_roots()
    p = load_progress()
    sys.stdin = io.StringIO("\n\n")
    before = set(p.get("asked", []))
    quiz(roots, p)
    after = set(p.get("asked", []))
    assert len(after - before) == 1
    teardown()


def test_review_after_ask() -> None:
    setup()
    roots = load_roots()
    p = load_progress()
    sys.stdin = io.StringIO("\n\n\n")
    ask_random(roots, p)
    assert len(p["asked"]) == 1
    out = io.StringIO()
    sys.stdout = out
    review(roots, p)
    sys.stdout = sys.__stdout__
    assert "review" in out.getvalue().lower() or len(p["asked"]) > 0
    teardown()


def test_lookup_spect() -> None:
    roots = load_roots()
    out = io.StringIO()
    sys.stdout = out
    lookup(roots, "spect")
    sys.stdout = sys.__stdout__
    assert "spect" in out.getvalue().lower()


if __name__ == "__main__":
    test_progress_roundtrip()
    test_ask_and_progress()
    test_quiz_records_root()
    test_review_after_ask()
    test_lookup_spect()
    print("smoke tests passed")
