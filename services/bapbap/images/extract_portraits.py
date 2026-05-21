"""
extract_portraits.py
--------------------
Extracts individual portrait cards from a horizontal strip screenshot.
Automatically detects card boundaries and strips level numbers / progress bars.

Usage:
    python3 extract_portraits.py <input_image> [output_dir]

Defaults:
    input_image : screenshot.png  (in the same directory)
    output_dir  : portraits/      (created if it doesn't exist)
"""

import sys
import os
from pathlib import Path
from itertools import groupby
from operator import itemgetter

import numpy as np
from PIL import Image


# ── Tuneable crop margins ────────────────────────────────────────────────────
# Rows to skip at the top (dark background + level badge overlap)
TOP_MARGIN = 17
# Rows to skip at the bottom (progress bar + level number badge)
BOTTOM_CUTOFF = 199   # rows 212-223 are the progress bar / badge area
# Minimum width (in columns) a dark region must be to count as a card separator
MIN_GAP_WIDTH = 15
# ─────────────────────────────────────────────────────────────────────────────


def find_card_boundaries(img_array: np.ndarray) -> list[tuple[int, int]]:
    """Return list of (x_start, x_end) for each card by detecting dark vertical gaps.

    Uses RGB channels only (ignores alpha) so transparent separators are detected
    correctly. Only gaps at least MIN_GAP_WIDTH columns wide are treated as real
    separators; this prevents dark portrait areas from being misread as boundaries.
    """
    # Use RGB only — alpha=0 (transparent) pixels would skew averages low
    rgb = img_array[:, :, :3]
    brightness = rgb.mean(axis=(0, 2))   # shape: (width,)

    threshold = brightness.mean() * 0.5
    dark_cols = np.where(brightness < threshold)[0]

    # Group consecutive dark columns into gap regions
    all_gaps: list[tuple[int, int]] = []
    for _, g in groupby(enumerate(dark_cols), lambda x: x[0] - x[1]):
        group = list(map(itemgetter(1), g))
        all_gaps.append((group[0], group[-1]))

    # Keep only wide-enough gaps (real card separators)
    gap_groups = [(x0, x1) for x0, x1 in all_gaps if (x1 - x0 + 1) >= MIN_GAP_WIDTH]

    # Card regions sit between consecutive gaps
    cards: list[tuple[int, int]] = []
    for i in range(len(gap_groups) - 1):
        x_start = gap_groups[i][1] + 1
        x_end = gap_groups[i + 1][0] - 1
        if x_end > x_start:
            cards.append((x_start, x_end))

    return cards


def extract_portraits(
    input_path: str,
    output_dir: str = "portraits",
) -> None:
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    height = img.size[1]

    # Determine vertical crop bounds
    y_top = TOP_MARGIN
    y_bot = min(BOTTOM_CUTOFF, height)

    cards = find_card_boundaries(arr)
    print(f"Detected {len(cards)} cards in '{input_path}'")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i, (x1, x2) in enumerate(cards, start=1):
        crop = img.crop((x1, y_top, x2, y_bot))
        filename = out / f"portrait_{i:02d}.png"
        crop.save(filename)
        print(f"  Saved {filename}  ({crop.size[0]}x{crop.size[1]} px)")

    print(f"\nDone — {len(cards)} portraits written to '{output_dir}/'")


if __name__ == "__main__":
    input_image = sys.argv[1] if len(sys.argv) > 1 else "screenshot.png"
    output_directory = sys.argv[2] if len(sys.argv) > 2 else "portraits"
    extract_portraits(input_image, output_directory)
