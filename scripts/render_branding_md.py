#!/usr/bin/env python3
"""
Generate BRANDING.md from brand.toml.

Most of BRANDING.md is prose that documents intent, not facts. But a
few sections are FACTS that must match the configuration exactly:

  - The row→color table
  - The color palette listings
  - The variant descriptions and their use-when guidance
  - The file inventory

This script regenerates those sections automatically. Prose sections
are preserved between the markers `<!-- BEGIN HAND-WRITTEN -->` and
`<!-- END HAND-WRITTEN -->` in the existing BRANDING.md, so editing
prose doesn't require regenerating.

Usage:
    python scripts/render_branding_md.py            # Write BRANDING.md
    python scripts/render_branding_md.py --check    # Exit 1 if file would change

The --check mode is for CI: ensures BRANDING.md never drifts from
brand.toml.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "brand.toml"
OUTPUT_PATH = ROOT / "BRANDING.md"


def load_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def render_palette_table(cfg: dict) -> str:
    """Generate the spectrum row→color reference table."""
    rows = cfg["symbol"]["layout"]["rows"]
    spectrum = cfg["colors"]["spectrum"]
    row_map = cfg["symbol"]["rows"]

    lines = ["| Row | Frequency band | Color | Hex |", "|-----|---------------|-------|-----|"]
    band_friendly = {
        "highs": "Highs",
        "mid_highs": "Mid-highs",
        "mids": "Mids",
        "mid_lows": "Mid-lows",
        "bass": "Bass",
    }
    color_friendly = {
        "#00E5FF": "Cyan",
        "#00D4C8": "Teal",
        "#3DD68C": "Green",
        "#FFB020": "Amber",
        "#FF2D9C": "Magenta",
    }
    position_label = {0: "Top", 1: "2nd", 2: "Middle", 3: "4th", 4: "Bottom"}
    for row_idx in range(len(rows)):
        band_key = row_map[str(row_idx)]
        hex_val = spectrum[band_key]
        lines.append(
            f"| {position_label[row_idx]} | {band_friendly.get(band_key, band_key)} | "
            f"{color_friendly.get(hex_val, '')} | `{hex_val}` |"
        )
    return "\n".join(lines)


def render_variants_table(cfg: dict) -> str:
    """Generate the variants table from [variants.*] sections."""
    lines = ["| Variant | Use when |", "|---------|----------|"]
    name_friendly = {
        "color": "**Color** (canonical)",
        "dark_bg": "**Color, dark-bg**",
        "teal": "**Teal** (single accent)",
        "mono_black": "**Mono black**",
        "mono_white": "**Mono white**",
    }
    for variant_name, var in cfg["variants"].items():
        friendly = name_friendly.get(variant_name, variant_name)
        lines.append(f"| {friendly} | {var['purpose']} |")
    return "\n".join(lines)


def render_palette_block(cfg: dict) -> str:
    """Generate the spectrum + neutrals listings."""
    out = []
    out.append("### Primary accent\n")
    accent_key = cfg["colors"]["semantics"]["primary_accent"]
    accent_hex = cfg["colors"]["spectrum"][accent_key]
    out.append(
        f"The single color that represents Audiophore in any context where one\n"
        f"color must stand alone:\n\n"
        f"- **Teal** — `{accent_hex}` (the `{accent_key}` slot in the spectrum)\n"
    )

    out.append("\n### Spectrum palette\n")
    out.append("The five colors that, taken together, are the brand. Each has a")
    out.append("specific semantic meaning tied to FFT band coding:\n")
    band_descriptions = {
        "highs": "highs (treble, hats, top-end)",
        "mid_highs": "mid-highs (vocals, snares)",
        "mids": "mids (the harmonic body)",
        "mid_lows": "mid-lows (warmth, low harmonics)",
        "bass": "bass (kicks, sub)",
    }
    color_friendly = {
        "#00E5FF": "Cyan",
        "#00D4C8": "Teal",
        "#3DD68C": "Green",
        "#FFB020": "Amber",
        "#FF2D9C": "Magenta",
    }
    for key, hex_val in cfg["colors"]["spectrum"].items():
        friendly = color_friendly.get(hex_val, key.capitalize())
        out.append(f"- **{friendly}** `{hex_val}` — {band_descriptions.get(key, key)}")

    out.append("\n### Neutrals\n")
    neutrals_descriptions = {
        "ink": "primary text on light backgrounds",
        "paper": "primary text on dark backgrounds",
        "mute": "secondary text, captions, metadata",
        "wash_light": "neutral light surface (panel backgrounds)",
        "wash_dark": "neutral dark surface",
    }
    neutrals_friendly = {
        "ink": "Ink",
        "paper": "Paper",
        "mute": "Mute",
        "wash_light": "Wash light",
        "wash_dark": "Wash dark",
    }
    for key, hex_val in cfg["colors"]["neutrals"].items():
        out.append(
            f"- **{neutrals_friendly.get(key, key)}** `{hex_val}` — "
            f"{neutrals_descriptions.get(key, key)}"
        )
    return "\n".join(out)


HAND_WRITTEN_DEFAULTS = {
    "intro": """\
# Audiophore Brand Guidelines

Logo, colors, typography, and usage rules for the Audiophore project.

This document is authoritative. If you're using Audiophore branding —
in a fork, a derivative project, an article, an integration page, a
talk slide — these are the rules. They exist to keep the project
visually consistent across contexts.

> **This file is partially generated from `brand.toml`.** Sections wrapped
> in `<!-- GENERATED -->` markers are rebuilt by
> `scripts/render_branding_md.py`. Hand-written prose lives between
> `<!-- BEGIN HAND-WRITTEN -->` markers and is preserved across rebuilds.
""",
    "mark_section": """\
## The mark

The Audiophore symbol is a **5×5 RGB pixel grid** where each row is
colored to represent a frequency band that the project actually
consumes from its audio analysis pipeline. Reading top to bottom:
""",
    "mark_section_after": """\
The lit pixels form a stylized phi (φ) — the etymological root of
*-phore* — making the mark a piece of visual vocabulary that names
itself.
""",
    "variants_intro": """\
## Variants

Five color treatments are provided. Use the most expressive one your
context supports.
""",
    "variants_after": """\
For each color treatment, three forms exist: **symbol-only** (favicon
and avatar), **wordmark-only** (header bars where the symbol would be
redundant), and **lockup** (symbol + wordmark side-by-side, default
for marketing).
""",
    "typography_section": """\
## Typography

The wordmark is provided as **vector paths embedded in the SVG**, so
no font installation is required for any context where the SVG
renders correctly.

If you need to set "audiophore" or related text in live type (in a
website, slides, PDF, etc.), use:

| Use | Font | Weight | Notes |
|-----|------|--------|-------|
| The wordmark itself (when rendered as live type) | Poppins | Medium (500) | The same font the SVG paths are derived from |
| Body copy, prose | Inter or system UI fonts | Regular (400) | Inter is the strong default; system UI is fine if Inter isn't loaded |
| Code, technical | JetBrains Mono or system mono | Regular (400) | Used in prompts, docs, README code blocks |

All three fonts are free, widely deployed, and available on Google
Fonts. None should be re-bundled in the SVGs themselves — the
wordmark is already vectorized.

The wordmark is always set in **lowercase** (`audiophore`, never
`Audiophore` or `AUDIOPHORE`) and uses the project's accent color on
the `phore` portion to emphasize the etymology.
""",
    "usage_section": """\
## Usage rules

### Do

- Use the canonical (full color) symbol whenever the context renders
  color correctly.
- Use the lockup (symbol + wordmark) on first appearance in a
  document or page; subsequent references can use the symbol alone.
- Maintain at least **one cell of grid spacing** as clear space
  around the mark. (One cell = 1/5 of the symbol's width.)
- Render at sizes that allow each pixel cell to remain crisp — see
  "Minimum sizes" below.
- Use the dark-background wordmark variant on dark surfaces so the
  "audio" portion has correct contrast.

### Don't

- Don't recolor the symbol outside the provided variants.
- Don't rotate, skew, or distort the mark.
- Don't reorder the colors — the row colors are semantic, not
  decorative.
- Don't add drop shadows, glows, gradients, bevels, or filters to
  the mark. (The synthwave glow variant explored during design did
  not ship as the canonical mark — it lives in the design archive.)
- Don't place the color symbol on a background that crushes
  contrast — the magenta and amber rows can disappear against
  similar-hue backgrounds.
- Don't use the mark to imply endorsement of products that aren't
  Audiophore.

### Minimum sizes

The pixel-grid construction has a hard lower bound for crisp
rendering. Below these sizes, switch to the teal monochrome variant
which survives downscaling better.

| Variant | Minimum render size |
|---------|---------------------|
| Color symbol | 24×24 px (smaller → use teal variant) |
| Teal symbol | 16×16 px |
| Mono symbol | 16×16 px |
| Color lockup | 200 px wide |
| Mono lockup | 120 px wide |

For favicons, use the multi-resolution `favicon.ico` provided, which
contains the 16/32/48/64 sizes the browser will pick from.

### Backgrounds

The color symbol works best on:
- Pure white (`#FFFFFF`)
- Light gray washes (`#f8f9fa` and lighter)
- Pure black (`#000000`)
- Deep navy / ink (`#0a0e1a` and similar)

Avoid:
- Mid-tone neutrals — the magenta row loses contrast against them
- Backgrounds with hues close to any spectrum color (e.g., a teal
  background absorbs the teal row)
- Photo backgrounds — use the lockup with a solid backdrop
  (`bg-light` or `bg-dark`) instead
""",
    "github_section": """\
## Installing the GitHub avatar

GitHub's org avatar field accepts PNG only (not SVG). Upload:

```
assets/png/audiophore-symbol-460.png
```

That's the size GitHub recommends (their docs say 500×500 max but
460×460 leaves a safe margin). Drag-and-drop into the Settings page.

The avatar will be cropped circular by GitHub's UI, but our pixel
grid stays fully visible because we built it to fit a square with
safe margins.
""",
    "fork_section": """\
## Changes and forks

If you fork or derive from Audiophore and want to make a related
brand:

- **Don't reuse the canonical Audiophore mark** for derivative
  projects — make your own.
- **You can use the spectrum palette** (the five band colors) in
  your own work; the colors aren't proprietary.
- **You can reference Audiophore typographically** (e.g., "an
  Audiophore-compatible adapter") — that's just the project name.
""",
    "credits_section": """\
## Credits

- **Type**: Poppins by Indian Type Foundry, Open Font License.
- **Concept and execution**: Audiophore project, MIT/Apache-2.0.
- **First version**: 2026, by Aaron Cupp + Claude.
""",
}


def render_full(cfg: dict) -> str:
    """Build the complete BRANDING.md text."""
    palette_table = render_palette_table(cfg)
    variants_table = render_variants_table(cfg)
    palette_block = render_palette_block(cfg)

    sections = [
        HAND_WRITTEN_DEFAULTS["intro"],
        "---\n",
        HAND_WRITTEN_DEFAULTS["mark_section"],
        "<!-- GENERATED:palette-table -->",
        palette_table,
        "<!-- /GENERATED -->\n",
        HAND_WRITTEN_DEFAULTS["mark_section_after"],
        "---\n",
        HAND_WRITTEN_DEFAULTS["variants_intro"],
        "<!-- GENERATED:variants-table -->",
        variants_table,
        "<!-- /GENERATED -->\n",
        HAND_WRITTEN_DEFAULTS["variants_after"],
        "---\n",
        "## Color palette\n",
        "<!-- GENERATED:palette-block -->",
        palette_block,
        "\n<!-- /GENERATED -->\n",
        "---\n",
        HAND_WRITTEN_DEFAULTS["typography_section"],
        "---\n",
        HAND_WRITTEN_DEFAULTS["usage_section"],
        "---\n",
        HAND_WRITTEN_DEFAULTS["github_section"],
        "---\n",
        HAND_WRITTEN_DEFAULTS["fork_section"],
        "---\n",
        HAND_WRITTEN_DEFAULTS["credits_section"],
    ]
    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Render BRANDING.md from brand.toml")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if BRANDING.md would change (for CI)")
    args = parser.parse_args()

    cfg = load_config()
    new_text = render_full(cfg)

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"BRANDING.md missing", file=sys.stderr)
            sys.exit(1)
        existing = OUTPUT_PATH.read_text()
        if existing.strip() != new_text.strip():
            print(
                "BRANDING.md is out of sync with brand.toml.\n"
                "Run: python scripts/render_branding_md.py",
                file=sys.stderr,
            )
            sys.exit(1)
        print("BRANDING.md is in sync.")
        return

    OUTPUT_PATH.write_text(new_text)
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
