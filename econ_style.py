"""
Shared chart style for Southbound 35 figures.

A close approximation of The Economist's chart style: cream
background, bold left-aligned title with a red accent bar, hidden
y-axis spine, horizontal-only gridlines, and a small palette tuned
for legibility on a white blog page.

Usage from inside a post's build script:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from econ_style import apply, COLORS, redbar, source_line

    apply()
    ...
    fig, ax = plt.subplots(...)
    redbar(fig)
    ...
    source_line(ax, "Sources: TWDB; ARWA.")
"""

from __future__ import annotations
import matplotlib as mpl
import matplotlib.pyplot as plt

# --- Palette (Economist-style) ---------------------------------------
# Primary categorical palette. Use COLORS["red"] sparingly as the
# accent. Use blue / cyan / green / yellow for ordered series.
COLORS = {
    "red":      "#E3120B",   # signature red, used for accents
    "blue":     "#006BA2",   # primary categorical
    "cyan":     "#3EBCD2",
    "green":    "#379A8B",
    "yellow":   "#EBB434",
    "olive":    "#B4BA39",
    "purple":   "#9A607F",
    "tan":      "#D1B07C",
    "darkgray": "#758D99",
    "gray":     "#A3A3A3",
}

CATEGORICAL = [
    COLORS["blue"], COLORS["red"], COLORS["green"],
    COLORS["yellow"], COLORS["cyan"], COLORS["purple"],
    COLORS["tan"], COLORS["darkgray"],
]

BG    = "#F2F2F0"   # cream background
GRID  = "#B4B4B4"   # gridline color
INK   = "#1A1A1A"   # near-black text


def apply():
    """Set matplotlib rcParams to the Economist-style defaults."""
    mpl.rcParams.update({
        # Backgrounds
        "figure.facecolor":  BG,
        "axes.facecolor":    BG,
        "savefig.facecolor": BG,
        "savefig.edgecolor": BG,

        # Spines: keep bottom only
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.spines.left":   False,
        "axes.spines.bottom": True,
        "axes.edgecolor":     INK,
        "axes.linewidth":     1.0,

        # Title: bold, left-aligned, with extra top padding to leave
        # room for the red accent bar.
        "axes.titlesize":     14,
        "axes.titleweight":   "bold",
        "axes.titlelocation": "left",
        "axes.titlepad":      14,
        "axes.titlecolor":    INK,

        # Axis labels
        "axes.labelsize":   10,
        "axes.labelcolor":  INK,
        "axes.labelpad":    8,

        # Grid: horizontal only, light
        "axes.grid":      True,
        "axes.grid.axis": "y",
        "grid.color":     GRID,
        "grid.linewidth": 0.5,
        "grid.alpha":     0.7,

        # Ticks: x-axis only; hide y-tick marks (keep labels).
        "xtick.color":       INK,
        "xtick.labelsize":   9,
        "xtick.direction":   "out",
        "xtick.major.size":  4,
        "xtick.major.width": 1.0,

        "ytick.color":       INK,
        "ytick.labelsize":   9,
        "ytick.left":        False,
        "ytick.major.size":  0,

        # Fonts
        "font.family":      "sans-serif",
        "font.sans-serif":  ["Helvetica", "Arial", "Liberation Sans",
                             "DejaVu Sans"],
        "font.size":        11,
        "text.color":       INK,

        # Legend
        "legend.fontsize":  9,
        "legend.frameon":   False,

        # Default categorical color cycle
        "axes.prop_cycle":  mpl.cycler(color=CATEGORICAL),

        # Output
        "figure.dpi":       150,
        "savefig.dpi":      150,
        "figure.constrained_layout.use": True,
    })


def redbar(fig, width_frac: float = 0.04, height_frac: float = 0.012,
           x: float = 0.0, y: float = 0.985):
    """Draw the small red accent bar at the top-left of a figure.

    Coordinates are in figure fraction. The default places a thin
    horizontal red bar in the upper-left, just above the chart title,
    in the style of The Economist's print and web charts.
    """
    rect = plt.Rectangle(
        (x, y), width_frac, height_frac,
        transform=fig.transFigure,
        facecolor=COLORS["red"], edgecolor="none",
        clip_on=False, zorder=20,
    )
    fig.add_artist(rect)


def source_line(ax, text: str, y: float = -0.14, fontsize: float = 7.5):
    """Add a small, gray source/footnote line below the chart axes."""
    ax.text(0.0, y, text,
            transform=ax.transAxes,
            fontsize=fontsize, color=COLORS["darkgray"],
            ha="left", va="top")
