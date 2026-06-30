#!/usr/bin/env python3
"""Word Roots Tutor — TUI edition (100 roots)."""

from __future__ import annotations

import json
import os
import platform
import random
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import msvcrt  # type: ignore
else:
    import select
    import termios
    import tty

THIS_DIR = Path(__file__).resolve().parent
ROOTS_FILE = THIS_DIR.parent / "data" / "roots.json"
PROGRESS_FILE = THIS_DIR.parent / "data" / "progress.json"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_roots() -> list[dict[str, Any]]:
    with open(ROOTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_progress() -> dict[str, Any]:
    if not PROGRESS_FILE.exists():
        return {"asked": [], "updated_at": None}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress: dict[str, Any]) -> None:
    progress["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def mark_asked(progress: dict[str, Any], root: str) -> None:
    asked = set(progress.get("asked", []))
    asked.add(root)
    progress["asked"] = sorted(asked)
    save_progress(progress)


# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    REVERSE = "\033[7m"
    CLEAR = "\033[2J"
    HOME = "\033[H"
    HIDE = "\033[?25l"
    SHOW = "\033[?25h"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"

    @staticmethod
    def fg(r: int, g: int, b: int) -> str:
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg(r: int, g: int, b: int) -> str:
        return f"\033[48;2;{r};{g};{b}m"


def move(row: int, col: int) -> str:
    return f"\033[{row};{col}H"


def colorize(text: str, *codes: str) -> str:
    return "".join(codes) + text + C.RESET


def box(text: str, width: int, title: str = "", border_color: str = C.CYAN) -> str:
    inner = width - 2
    lines = text.split("\n")
    wrapped = []
    for line in lines:
        while len(line) > inner:
            wrapped.append(line[:inner])
            line = line[inner:]
        wrapped.append(line)
    top = border_color + "┌" + "─" * width + "┐" + C.RESET
    if title:
        mid = (width - len(title)) // 2
        title_line = (
            border_color
            + "│"
            + " " * mid
            + C.BOLD
            + C.WHITE
            + title
            + C.RESET
            + border_color
            + " " * (width - mid - len(title))
            + "│"
            + C.RESET
        )
        rows = [top, title_line]
    else:
        rows = [top]
    for line in wrapped:
        pad = inner - len(line)
        rows.append(
            border_color
            + "│"
            + C.RESET
            + line
            + " " * pad
            + border_color
            + "│"
            + C.RESET
        )
    bottom = border_color + "└" + "─" * width + "┘" + C.RESET
    rows.append(bottom)
    return "\n".join(rows)


def progress_bar(current: int, total: int, width: int = 30) -> str:
    ratio = current / total if total else 0
    filled = int(width * ratio)
    empty = width - filled
    return (
        C.GREEN
        + "█" * filled
        + C.DIM
        + "░" * empty
        + C.RESET
        + f" {current}/{total}"
    )


# ---------------------------------------------------------------------------
# Input (non-blocking-ish)
# ---------------------------------------------------------------------------

def read_char() -> str:
    ch = ""
    if IS_WINDOWS:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch == "\x00":
                ch = msvcrt.getwch()
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            ch = sys.stdin.read(1)
    return ch


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

class TutorTUI:
    def __init__(self) -> None:
        self.roots = load_roots()
        self.progress = load_progress()
        self.term_size = shutil.get_terminal_size()
        self.last_action = ""
        self.current_index = 0
        self.choice_index = 0
        self.message = ""
        self.running = True

        self.menus = {
            "main": [
                ("ask", "Random ask"),
                ("quiz", "Quiz mode"),
                ("review", "Review asked"),
                ("list", "List roots"),
                ("progress", "Progress"),
                ("export", "Export CSV"),
                ("reset", "Reset progress"),
                ("quit", "Quit"),
            ],
            "mode": [
                ("ask", "Ask unrevealed"),
                ("quiz", "Sentence quiz"),
                ("list", "Browse list"),
            ],
        }
        self.view = "main"

    # ----- navigation helpers -----

    def menu_bounds(self) -> int:
        return len(self.menus[self.view])

    def current_label(self) -> str:
        return self.menus[self.view][self.choice_index][0]

    def render_menu(self) -> str:
        items = []
        for idx, (key, label) in enumerate(self.menus[self.view]):
            if idx == self.choice_index:
                items.append(
                    C.REVERSE
                    + C.BOLD
                    + f" > {key}"
                    + " " * (12 - len(key))
                    + label
                    + C.RESET
                )
            else:
                items.append(
                    C.DIM + f"   {key}" + C.RESET + " " * (12 - len(key)) + label
                )
        header = colorize("WORD ROOTS TUTOR — TUI", C.BOLD + C.CYAN)
        body = "\n".join(items)
        footer = colorize(
            "↑↓ move  |  Enter select  |  Esc back", C.DIM + C.WHITE
        )
        if self.message:
            footer = (
                colorize(self.message, C.YELLOW)
                + "\n"
                + footer
            )
        return "\n\n".join([header, body, footer])

    def render_root_detail(self, root: dict[str, Any]) -> str:
        title = colorize(root["root"], C.BOLD + C.WHITE) + colorize(
            f" {root['pronunciation']}", C.CYAN
        )
        lines = [
            colorize("MEANING", C.BOLD + C.YELLOW) + f" {root['meaning']}",
            colorize("ORIGIN", C.BOLD + C.YELLOW) + f" {root['origin']}",
            colorize("DERIVED", C.BOLD + C.YELLOW)
            + " "
            + ", ".join(root["derived"]),
            colorize("EXAMPLE", C.BOLD + C.YELLOW)
            + " "
            + root["example_sentence"],
            colorize("TIP", C.BOLD + C.YELLOW) + " " + root["mnemonic"],
        ]
        hint = colorize(
            "Press any key to continue...", C.DIM + C.WHITE
        )
        return "\n\n".join([title] + lines + [hint])

    # ----- commands -----

    def cmd_ask(self) -> None:
        asked = set(self.progress.get("asked", []))
        candidates = [r for r in self.roots if r["root"] not in asked]
        if not candidates:
            self.message = "All roots reviewed — great job!"
            return
        target = random.choice(candidates)
        self.detail_mode = "ask"
        self.active_root = target
        self.message = "Press any key after reading..."
        mark_asked(self.progress, target["root"])

    def cmd_quiz(self) -> None:
        target = random.choice(self.roots)
        self.detail_mode = "quiz"
        self.active_root = target
        self.message = "Read the question, then press any key..."

    def cmd_review(self) -> None:
        asked = set(self.progress.get("asked", []))
        pool = [r for r in self.roots if r["root"] in asked]
        if not pool:
            self.message = "No roots reviewed yet — try ask first."
            return
        target = random.choice(pool)
        self.detail_mode = "review"
        self.active_root = target
        self.message = "Press any key after reading..."

    def cmd_list(self) -> None:
        self.detail_mode = "list"
        self.list_page = 0

    def cmd_progress(self) -> None:
        asked = set(self.progress.get("asked", []))
        pct = len(asked) / len(self.roots) * 100 if self.roots else 0
        self.message = (
            colorize("Progress:", C.BOLD + C.CYAN)
            + " "
            + progress_bar(len(asked), len(self.roots))
            + f"  ({pct:.1f}%)"
        )
        if self.progress.get("updated_at"):
            self.message += "\n" + colorize(
                f"Last save: {self.progress['updated_at']}", C.DIM
            )

    def cmd_export(self) -> None:
        asked = set(self.progress.get("asked", []))
        path = THIS_DIR.parent / "data" / "progress.csv"
        import csv

        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["root", "meaning", "origin", "reviewed"])
            for r in self.roots:
                writer.writerow(
                    [r["root"], r["meaning"], r["origin"], "yes" if r["root"] in asked else "no"]
                )
        self.message = f"Exported to {path}"

    def cmd_reset(self) -> None:
        self.progress = {"asked": [], "updated_at": None}
        save_progress(self.progress)
        self.message = colorize("Progress reset.", C.YELLOW)

    def cmd_quit(self) -> None:
        self.running = False

    # ----- input handling -----

    def handle_main_menu(self, key: str) -> None:
        if key == "\x1b":
            self.cmd_quit()
            return
        if key in ("\x1b[A", "w", "W"):
            self.choice_index = (self.choice_index - 1) % self.menu_bounds()
            return
        if key in ("\x1b[B", "s", "S"):
            self.choice_index = (self.choice_index + 1) % self.menu_bounds()
            return
        if key in ("\r", "\n", " "):
            action = self.current_label()
            if action == "ask":
                self.cmd_ask()
            elif action == "quiz":
                self.cmd_quiz()
            elif action == "review":
                self.cmd_review()
            elif action == "list":
                self.cmd_list()
            elif action == "progress":
                self.cmd_progress()
            elif action == "export":
                self.cmd_export()
            elif action == "reset":
                self.cmd_reset()
            elif action == "quit":
                self.cmd_quit()
            return

    def handle_detail(self, key: str) -> None:
        if self.detail_mode == "list":
            page_size = max(1, self.term_size.lines - 8)
            if key in ("\x1b[B", "s", "S", " "):
                self.list_page = min(
                    self.list_page + 1,
                    max(0, (len(self.roots) - 1) // page_size),
                )
                return
            if key in ("\x1b[A", "w", "W"):
                self.list_page = max(0, self.list_page - 1)
                return
        if key in ("\x1b", "q", "Q"):
            self.detail_mode = None
            self.view = "main"
            return
        self.detail_mode = None
        self.view = "main"

    def tick(self) -> None:
        key = read_char()
        if key:
            if self.detail_mode:
                self.handle_detail(key)
            else:
                if self.view == "main":
                    self.handle_main_menu(key)

    def render(self) -> str:
        w = min(self.term_size.columns, 80)
        if self.detail_mode == "list":
            page_size = max(1, self.term_size.lines - 8)
            start = self.list_page * page_size
            end = min(len(self.roots), start + page_size)
            items = []
            for idx, r in enumerate(self.roots[start:end], start=start + 1):
                reviewed = "✔" if r["root"] in self.progress.get("asked", []) else " "
                items.append(
                    colorize(f"{idx:03d} ", C.DIM)
                    + f"[{reviewed}] "
                    + colorize(f"{r['root']:10s}", C.CYAN)
                    + r["meaning"]
                )
            header = colorize(
                f"ROOTS LIST ({start+1}-{end} of {len(self.roots)})",
                C.BOLD + C.WHITE,
            )
            hint = colorize(
                "↑↓/ws navigate  |  Esc back",
                C.DIM + C.WHITE,
            )
            return "\n".join([header] + items + [hint])
        if self.detail_mode in ("ask", "quiz", "review") and hasattr(self, "active_root"):
            r = self.active_root
            if self.detail_mode == "quiz":
                title = colorize("QUIZ", C.BOLD + C.MAGENTA)
                q = colorize("Q", C.BOLD + C.YELLOW) + "  " + r["quiz"]
                body = "\n\n".join([title, q, colorize("(press any key)", C.DIM)])
            else:
                title = colorize(self.detail_mode.upper(), C.BOLD + C.GREEN)
                prefix = ""
                if self.detail_mode == "ask":
                    prefix = colorize("Was it: ", C.BOLD + C.WHITE) + colorize(
                        r["root"], C.BOLD + C.CYAN
                    ) + colorize(f" ({r['pronunciation']})", C.DIM) + " — " + colorize(
                        r["meaning"], C.YELLOW
                    )
                else:
                    prefix = colorize(r["root"], C.BOLD + C.CYAN) + colorize(
                        f" ({r['pronunciation']})", C.DIM
                    )
                body = "\n\n".join(
                    [
                        title,
                        prefix,
                        colorize("MEANING", C.BOLD) + "  " + r["meaning"],
                        colorize("ORIGIN", C.BOLD) + "  " + r["origin"],
                        colorize("DERIVED", C.BOLD)
                        + "  "
                        + ", ".join(r["derived"]),
                        colorize("EXAMPLE", C.BOLD) + "  " + r["example_sentence"],
                        colorize("TIP", C.BOLD) + "  " + r["mnemonic"],
                        colorize("(press any key)", C.DIM),
                    ]
                )
            return body
        return self.render_menu()

    def run(self) -> int:
        os.system("")  # enable ANSI on Windows 10+
        if IS_WINDOWS:
            # best-effort: disable QuickEdit to avoid accidental selection pauses
            try:
                import ctypes  # type: ignore
                kernel32 = ctypes.windll.kernel32  # type: ignore
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)
            except Exception:
                pass
        else:
            old_tty = termios.tcgetattr(sys.stdin)  # type: ignore
            tty.setcbreak(sys.stdin.fileno())  # type: ignore

        try:
            sys.stdout.write(C.HIDE + C.CLEAR + C.HOME)
            while self.running:
                term = self.term_size
                sys.stdout.write(C.HOME)
                content = self.render()
                sys.stdout.write(content + "\n")
                footer_line = max(3, term.lines - 1)
                progress = len(self.progress.get("asked", []))
                sys.stdout.write(
                    move(footer_line, 1)
                    + colorize(
                        f" {progress}/%d " % len(self.roots),
                        C.BOLD + C.BLACK + C.BG_CYAN,
                    )
                    + "   "
                    + colorize("WORD ROOTS TUTOR", C.BOLD + C.WHITE + C.BG_BLUE)
                    + "   "
                    + colorize(
                        " q=quit  ↑↓=move  Enter=select ",
                        C.DIM + C.WHITE,
                    )
                    + " " * max(0, term.columns - 70)
                    + C.RESET
                )
                sys.stdout.flush()
                time.sleep(0.01)
                self.tick()
        finally:
            sys.stdout.write(C.SHOW + C.RESET + C.HOME + "\n")
            if not IS_WINDOWS:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)  # type: ignore
        return 0


def main() -> int:
    return TutorTUI().run()


if __name__ == "__main__":
    raise SystemExit(main())
