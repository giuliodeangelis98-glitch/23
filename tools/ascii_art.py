#!/usr/bin/env python3
"""ASCII art generator. Turns text into banners or images into ASCII."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BANNER_FONT = {
    " ": ["     ", "     ", "     ", "     ", "     "],
    "!": ["  #  ", "  #  ", "  #  ", "     ", "  #  "],
    "?": [" ### ", "#   #", "   # ", "  #  ", "  #  "],
    ".": ["     ", "     ", "     ", "     ", "  #  "],
    ",": ["     ", "     ", "     ", "  #  ", " #   "],
    "'": ["  #  ", "  #  ", "     ", "     ", "     "],
    ":": ["     ", "  #  ", "     ", "  #  ", "     "],
    "-": ["     ", "     ", " ### ", "     ", "     "],
    "0": [" ### ", "#  ##", "# # #", "##  #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "  ## ", " #   ", "#####"],
    "3": [" ### ", "#   #", "  ## ", "#   #", " ### "],
    "4": ["#  # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "#### "],
    "6": [" ### ", "#    ", "#### ", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   "],
    "8": [" ### ", "#   #", " ### ", "#   #", " ### "],
    "9": [" ### ", "#   #", " ####", "    #", " ### "],
    "A": [" ### ", "#   #", "#####", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#### ", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "###  ", "#    ", "#####"],
    "F": ["#####", "#    ", "###  ", "#    ", "#    "],
    "G": [" ####", "#    ", "#  ##", "#   #", " ####"],
    "H": ["#   #", "#   #", "#####", "#   #", "#   #"],
    "I": [" ### ", "  #  ", "  #  ", "  #  ", " ### "],
    "J": ["  ###", "    #", "    #", "#   #", " ### "],
    "K": ["#   #", "#  # ", "###  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#### ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#### ", "#  # ", "#   #"],
    "S": [" ####", "#    ", " ### ", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "# # #", "## ##", "#   #"],
    "X": ["#   #", " # # ", "  #  ", " # # ", "#   #"],
    "Y": ["#   #", " # # ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "   # ", "  #  ", " #   ", "#####"],
}

ANSI_COLORS = {
    "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
    "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m",
    "white": "\033[37m", "bright_red": "\033[91m", "bright_green": "\033[92m",
    "bright_yellow": "\033[93m", "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m", "bright_cyan": "\033[96m",
}
RESET = "\033[0m"


def render_banner(text: str, fill: str = "█") -> list[str]:
    rows = ["", "", "", "", ""]
    for ch in text.upper():
        glyph = BANNER_FONT.get(ch, BANNER_FONT["?"])
        for i in range(5):
            rows[i] += glyph[i].replace("#", fill) + " "
    return rows


def image_to_ascii(path: Path, width: int) -> list[str]:
    try:
        from PIL import Image
    except ImportError:
        sys.exit("error: image mode requires Pillow (pip install Pillow)")
    ramp = "@%#*+=-:. "
    img = Image.open(path).convert("L")
    aspect = img.height / img.width
    height = max(1, int(width * aspect * 0.55))
    img = img.resize((width, height))
    pixels = img.getdata()
    chars = [ramp[min(len(ramp) - 1, p * len(ramp) // 256)] for p in pixels]
    return ["".join(chars[i:i + width]) for i in range(0, len(chars), width)]


def main() -> None:
    p = argparse.ArgumentParser(description="ASCII art generator")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("text", help="render text as a banner")
    t.add_argument("text")
    t.add_argument("--fill", default="█", help="fill character")
    t.add_argument("--color", choices=ANSI_COLORS.keys())

    i = sub.add_parser("image", help="render an image as ASCII")
    i.add_argument("path", type=Path)
    i.add_argument("--width", type=int, default=80)
    i.add_argument("--color", choices=ANSI_COLORS.keys())

    args = p.parse_args()
    lines = render_banner(args.text, args.fill) if args.cmd == "text" else image_to_ascii(args.path, args.width)
    prefix = ANSI_COLORS[args.color] if args.color else ""
    suffix = RESET if args.color else ""
    for line in lines:
        print(f"{prefix}{line}{suffix}")


if __name__ == "__main__":
    main()
