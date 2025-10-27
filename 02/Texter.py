from __future__ import annotations

import argparse
import re
from typing import List


class Texter:
    """Perform text analysis for assignment A02, operation 4."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def run(self) -> None:
        text = self._read_text(self.file_path)
        paragraphs = self._count_paragraphs(text)
        spaces_after_dots = self._count_spaces_after_dots(text)
        print(f"Paragraphs: {paragraphs}")
        print(f"Spaces after dots: {spaces_after_dots}")

    @staticmethod
    def _read_text(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", newline="") as handle:
            return handle.read()

    @staticmethod
    def _normalize_newlines(text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _count_paragraphs(self, text: str) -> int:
        """Count paragraphs separated by a blank (whitespace-only) line."""
        norm = self._normalize_newlines(text)
        # Split where there's at least one empty/whitespace-only line.
        blocks = [b for b in re.split(r"\n\s*\n+", norm) if b.strip()]
        return len(blocks)

    @staticmethod
    def _count_spaces_after_dots(text: str) -> int:
        """
        Count spaces immediately after '.'.
        Accept both ASCII space ' ' and non-breaking space '\u00A0'.
        """
        total = 0
        n = len(text)
        space_chars = {" ", "\u00A0"}
        for i, ch in enumerate(text):
            if ch == ".":
                j = i + 1
                while j < n and text[j] in space_chars:
                    total += 1
                    j += 1
        return total


def parse_args(argv: List[str]) -> argparse.Namespace:
    """
    Parse CLI args while ignoring unknown flags injected by Jupyter/VS Code
    (e.g., -f <kernel.json> or --f=...).
    """
    parser = argparse.ArgumentParser(
        description="Count paragraphs and spaces after dots."
    )
    # Primary positional arg
    parser.add_argument("path", nargs="?", help="Path to the text file.")
    # Optional named alias if you prefer: python texter.py --input test.txt
    parser.add_argument(
        "-i", "--input", dest="path_opt", help="Path to the text file."
    )
    # Do NOT declare '-f' to avoid colliding with Jupyter; just ignore it.
    args, _unknown = parser.parse_known_args(argv[1:])
    return args


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    file_path = args.path_opt or args.path
    if not file_path:
        print("Usage: python texter.py <path_to_text_file>")
        print("Example: python texter.py test.txt")
        return
    try:
        Texter(file_path).run()
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}")
    except OSError as exc:
        print(f"Error reading file '{file_path}': {exc}")


if __name__ == "__main__":
    import sys
    main(sys.argv)
