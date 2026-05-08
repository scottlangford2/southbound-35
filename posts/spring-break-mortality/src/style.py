"""
style.py
Shared matplotlib style and color palette for spring-break-mortality figures.

This module re-exports the canonical Southbound 35 (Economist-inspired)
chart style from `econ_style.py` at the repo root, and preserves the
color-name aliases that the existing figure code uses.
"""

import sys
from pathlib import Path

# southbound-35/posts/spring-break-mortality/src/style.py -> repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import matplotlib.pyplot as plt
from econ_style import apply as _apply, COLORS as _COLORS, redbar as _redbar

# ── Color aliases (kept stable for existing figure code) ───────────────────
RED    = _COLORS["red"]
BLUE   = _COLORS["blue"]
ORANGE = _COLORS["yellow"]
GRAY   = _COLORS["darkgray"]
GREEN  = _COLORS["green"]

ALPHA_BAR  = 0.85
ALPHA_FILL = 0.20

# ── Figure default sizes (kept the same) ───────────────────────────────────
FIG_W  = 7.0
FIG_H  = 4.5
FIG_DW = 12.0
FIG_DH = 4.5
DPI    = 150


def apply_style() -> None:
    """Apply the shared Economist-style rcParams. Call once at start."""
    _apply()


def save(fig: plt.Figure, path: str) -> None:
    """Add the red accent bar, save the figure, and close it."""
    _redbar(fig)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {path}")
