#!/usr/bin/env python3
"""
Keep the generated tables in BRANDING.md in sync with brand.toml.

BRANDING.md is the source of truth for its own prose. A few regions are
*facts* that must match brand.toml exactly — the row→color table, the
variants table, and the spectrum/neutrals colour listings. Those regions
are wrapped in markers:

    <!-- GENERATED:palette-table -->
    ...table body, rewritten from brand.toml...
    <!-- /GENERATED -->

Everything outside a GENERATED block is hand-written prose and is
preserved verbatim. Prose may optionally be bracketed with
`<!-- BEGIN HAND-WRITTEN -->` / `<!-- END HAND-WRITTEN -->` for the
reader's benefit, but those markers carry no special meaning — anything
not inside a GENERATED block is left untouched.

Usage:
    python scripts/render_branding_md.py            # Rewrite GENERATED blocks in place
    python scripts/render_branding_md.py --check    # Exit 1 if any block is stale (CI)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "brand.toml"
OUTPUT_PATH = ROOT / "BRANDING.md"

BAND_FRIENDLY = {
    "highs": "Highs",
    "mid_highs": "Mid-highs",
    "mids": "Mids",
    "mid_lows": "Mid-lows",
    "bass": "Bass",
}
BAND_DESCRIPTION = {
    "highs": "highs (treble, hats, top-end)",
    "mid_highs": "mid-highs (vocals, snares)",
    "mids": "mids (the harmonic body)",
    "mid_lows": "mid-lows (warmth, low harmonics)",
    "bass": "bass (kicks, sub)",
}
COLOR_FRIENDLY = {
    "#00E5FF": "Cyan",
    "#00D4C8": "Teal",
    "#3DD68C": "Green",
    "#FFB020": "Amber",
    "#FF2D9C": "Magenta",
}
POSITION_LABEL = {0: "Top", 1: "2nd", 2: "Middle", 3: "4th", 4: "Bottom"}
VARIANT_FRIENDLY = {
    "color": "**Color** (canonical)",
    "dark_bg": "**Color, dark-bg**",
    "teal": "**Teal** (single accent)",
    "mono_black": "**Mono black**",
    "mono_white": "**Mono white**",
}
NEUTRAL_FRIENDLY = {
    "ink": "Ink",
    "paper": "Paper",
    "mute": "Mute",
    "wash_light": "Wash light",
    "wash_dark": "Wash dark",
}
NEUTRAL_DESCRIPTION = {
    "ink": "primary text on light backgrounds",
    "paper": "primary text on dark backgrounds",
    "mute": "secondary text, captions, metadata",
    "wash_light": "neutral light surface (panel backgrounds)",
    "wash_dark": "neutral dark surface",
}


def load_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


# ─── Generated-block renderers ──────────────────────────────────────

def render_palette_table(cfg: dict) -> str:
    rows = cfg["symbol"]["layout"]["rows"]
    spectrum = cfg["colors"]["spectrum"]
    row_map = cfg["symbol"]["rows"]
    lines = [
        "| Row | Frequency band | Color | Hex |",
        "|-----|---------------|-------|-----|",
    ]
    for row_idx in range(len(rows)):
        band_key = row_map[str(row_idx)]
        hex_val = spectrum[band_key]
        lines.append(
            f"| {POSITION_LABEL[row_idx]} | {BAND_FRIENDLY.get(band_key, band_key)} | "
            f"{COLOR_FRIENDLY.get(hex_val, '')} | `{hex_val}` |"
        )
    return "\n".join(lines)


def render_variants_table(cfg: dict) -> str:
    lines = ["| Variant | Use when |", "|---------|----------|"]
    for variant_name, var in cfg["variants"].items():
        if not var.get("show_in_table", True):
            continue
        friendly = VARIANT_FRIENDLY.get(variant_name, variant_name)
        lines.append(f"| {friendly} | {var['purpose']} |")
    return "\n".join(lines)


def render_spectrum_list(cfg: dict) -> str:
    lines = []
    for key, hex_val in cfg["colors"]["spectrum"].items():
        friendly = COLOR_FRIENDLY.get(hex_val, key.capitalize())
        lines.append(f"- **{friendly}** `{hex_val}` — {BAND_DESCRIPTION.get(key, key)}")
    return "\n".join(lines)


def render_neutrals_list(cfg: dict) -> str:
    lines = []
    for key, hex_val in cfg["colors"]["neutrals"].items():
        lines.append(
            f"- **{NEUTRAL_FRIENDLY.get(key, key)}** `{hex_val}` — "
            f"{NEUTRAL_DESCRIPTION.get(key, key)}"
        )
    return "\n".join(lines)


GENERATORS = {
    "palette-table": render_palette_table,
    "variants-table": render_variants_table,
    "spectrum-list": render_spectrum_list,
    "neutrals-list": render_neutrals_list,
}

BLOCK_RE = re.compile(
    r"(?P<open><!-- GENERATED:(?P<name>[\w-]+) -->\n)"
    r"(?P<body>.*?)"
    r"(?P<close>\n<!-- /GENERATED -->)",
    re.DOTALL,
)


def rewrite_blocks(cfg: dict, text: str) -> str:
    """Replace the body of every GENERATED block with freshly-rendered content."""
    seen: set[str] = set()

    def repl(m: re.Match) -> str:
        name = m.group("name")
        seen.add(name)
        gen = GENERATORS.get(name)
        if gen is None:
            raise ValueError(
                f"Unknown GENERATED block {name!r} in BRANDING.md. "
                f"Known blocks: {', '.join(sorted(GENERATORS))}."
            )
        return f"{m.group('open')}{gen(cfg)}{m.group('close')}"

    result = BLOCK_RE.sub(repl, text)
    missing = set(GENERATORS) - seen
    if missing:
        raise ValueError(
            f"BRANDING.md is missing GENERATED blocks: {', '.join(sorted(missing))}."
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync BRANDING.md generated blocks with brand.toml")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if any generated block is out of sync (for CI)")
    args = parser.parse_args()

    cfg = load_config()
    if not OUTPUT_PATH.exists():
        print("BRANDING.md missing", file=sys.stderr)
        sys.exit(1)
    current = OUTPUT_PATH.read_text()
    updated = rewrite_blocks(cfg, current)

    if args.check:
        if current != updated:
            print(
                "BRANDING.md generated blocks are out of sync with brand.toml.\n"
                "Run: python scripts/render_branding_md.py",
                file=sys.stderr,
            )
            sys.exit(1)
        print("BRANDING.md is in sync.")
        return

    OUTPUT_PATH.write_text(updated)
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
