#!/usr/bin/env python3
"""Git commit time-lapse visualizer. Animates repo growth as a heatmap."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta

HEAT = [" ", "·", "▪", "▫", "◆", "█"]
COLORS = ["\033[90m", "\033[34m", "\033[36m", "\033[32m", "\033[33m", "\033[31m"]
RESET = "\033[0m"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL)


def commits_by_day() -> dict[str, int]:
    out = git("log", "--pretty=format:%ad", "--date=short")
    counts: dict[str, int] = defaultdict(int)
    for line in out.splitlines():
        counts[line.strip()] += 1
    return counts


def date_range(counts: dict[str, int]) -> list[str]:
    if not counts:
        return []
    dates = sorted(counts)
    start = datetime.strptime(dates[0], "%Y-%m-%d").date()
    end = datetime.strptime(dates[-1], "%Y-%m-%d").date()
    out = []
    d = start
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def heat_char(count: int, peak: int) -> str:
    if count == 0:
        return f"{COLORS[0]}{HEAT[0]}{RESET}"
    bucket = min(len(HEAT) - 1, 1 + (count * (len(HEAT) - 2)) // max(1, peak))
    return f"{COLORS[bucket]}{HEAT[bucket]}{RESET}"


def render_grid(counts: dict[str, int], days: list[str], peak: int, cols: int) -> list[str]:
    cells = [heat_char(counts.get(d, 0), peak) for d in days]
    rows = []
    for r in range(0, len(cells), cols):
        rows.append("".join(cells[r:r + cols]))
    return rows


def animate(counts: dict[str, int], days: list[str], peak: int, cols: int, delay: float) -> None:
    running: dict[str, int] = {}
    total = 0
    for i, d in enumerate(days, start=1):
        running[d] = counts.get(d, 0)
        total += running[d]
        rows = render_grid(running, days, peak, cols)
        sys.stdout.write("\033[H\033[J")
        print(f"git time-lapse · {days[0]} → {d} · {total} commits")
        print()
        for row in rows:
            print(row)
        sys.stdout.flush()
        time.sleep(delay)


def main() -> None:
    p = argparse.ArgumentParser(description="Git commit time-lapse")
    p.add_argument("--cols", type=int, default=shutil.get_terminal_size().columns - 2)
    p.add_argument("--delay", type=float, default=0.04, help="seconds per day frame")
    p.add_argument("--no-animate", action="store_true", help="render full grid once")
    args = p.parse_args()

    try:
        counts = commits_by_day()
    except subprocess.CalledProcessError:
        sys.exit("error: not a git repository (or git not installed)")
    if not counts:
        sys.exit("no commits found")

    days = date_range(counts)
    peak = max(counts.values())

    if args.no_animate:
        for row in render_grid(counts, days, peak, args.cols):
            print(row)
        print(f"\n{sum(counts.values())} commits across {len(days)} days · peak {peak}/day")
    else:
        animate(counts, days, peak, args.cols, args.delay)


if __name__ == "__main__":
    main()
