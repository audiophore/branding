#!/usr/bin/env python3
"""
Audiophore brand asset generator.

Reads brand.toml, produces:
  - logos/svg/*.svg     (all logo variants in vector form)
  - logos/png/*.png     (all rasters at all configured sizes)
  - logos/favicon/*.png (favicon sizes)
  - logos/favicon/favicon.ico (multi-resolution legacy favicon)

Usage:
    python scripts/build.py            # Build everything
    python scripts/build.py symbol     # Build only symbol assets
    python scripts/build.py wordmark   # etc.
    python scripts/build.py --clean    # Remove generated files first

The configuration in brand.toml is the single source of truth for
colors, layout, sizes, and variants. Edit there, not here.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import cairosvg
import tomllib  # Python 3.11+
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen


# ─── Paths ──────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "brand.toml"
# Canonical artifacts live in logos/ — the directory downstream consumers fetch.
ASSETS_DIR = ROOT / "logos"
SVG_DIR = ASSETS_DIR / "svg"
PNG_DIR = ASSETS_DIR / "png"
FAVICON_DIR = ASSETS_DIR / "favicon"


# ─── Config helpers ─────────────────────────────────────────────────

def load_config() -> dict:
    """Load brand.toml as a dict."""
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def color(cfg: dict, key: str) -> str:
    """Resolve a palette key (e.g. 'highs', 'ink') to its hex value."""
    if key in cfg["colors"]["spectrum"]:
        return cfg["colors"]["spectrum"][key]
    if key in cfg["colors"]["neutrals"]:
        return cfg["colors"]["neutrals"][key]
    raise KeyError(f"Unknown color key: {key!r}")


def opacity_for_distance(cfg: dict, dist: int) -> float:
    """Look up opacity by distance-from-center; clamps to last defined."""
    table = cfg["symbol"]["opacity"]
    keys = sorted(k for k in table if k.startswith("distance_"))
    max_dist = int(keys[-1].split("_")[1])
    dist = min(dist, max_dist)
    return table[f"distance_{dist}"]


# ─── Symbol generation ─────────────────────────────────────────────

def symbol_svg(cfg: dict, variant: str) -> str:
    """Generate the symbol SVG for a given variant."""
    sym = cfg["symbol"]
    vb = sym["viewbox"]
    px = sym["pixel_size"]
    gap = sym["pixel_gap"]
    radius = sym["pixel_radius"]

    # Center grid in viewBox: 5*px + 4*gap = 312, leaving 8px of slack
    grid_total = 5 * px + 4 * gap
    margin = (vb - grid_total) / 2

    var = cfg["variants"][variant]
    is_spectrum = var["mode"] == "spectrum"

    rects = []
    for row_idx, row in enumerate(sym["layout"]["rows"]):
        # Pick this row's fill color
        if is_spectrum:
            row_palette_key = sym["rows"][str(row_idx)]
            fill = color(cfg, row_palette_key)
        else:
            fill = color(cfg, var["single_color"])

        for col_idx, lit in enumerate(row):
            if not lit:
                continue
            x = margin + col_idx * (px + gap)
            y = margin + row_idx * (px + gap)

            # Center column always full opacity; outer columns fade
            distance = abs(col_idx - 2)  # 2 is center of 0..4
            op = opacity_for_distance(cfg, distance)
            op_attr = f' opacity="{op}"' if op < 1.0 else ""

            rects.append(
                f'  <rect x="{x:g}" y="{y:g}" width="{px}" height="{px}" '
                f'rx="{radius}" fill="{fill}"{op_attr}/>'
            )

    rects_str = "\n".join(rects)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb} {vb}" width="{vb}" height="{vb}" role="img" aria-label="{cfg["meta"]["name"]}">
  <title>{cfg["meta"]["name"]}</title>
{rects_str}
</svg>
'''


def write_symbols(cfg: dict) -> list[Path]:
    """Generate all symbol SVG variants. Returns list of paths written."""
    written = []
    for variant in cfg["variants"]:
        svg = symbol_svg(cfg, variant)
        suffix = "" if variant == "color" else f"-{variant.replace('_', '-')}"
        path = SVG_DIR / f"audiophore-symbol{suffix}.svg"
        # Skip dark_bg for symbols (the color symbol works on both backgrounds)
        if variant == "dark_bg":
            continue
        path.write_text(svg)
        written.append(path)
    return written


# ─── Wordmark generation ────────────────────────────────────────────

def extract_text_paths(cfg: dict) -> tuple[list[tuple[str, str, int, int]], int, int, int]:
    """
    Extract glyph-path data for the wordmark text.

    Returns (glyph_data, total_width, cap_height, descent) where
    glyph_data is a list of (char, svg_d, x_offset, advance_width).
    """
    wm = cfg["wordmark"]
    # $POPPINS_TTF overrides the brand.toml path for local dev (e.g. macOS),
    # where Poppins lives somewhere other than the Linux/CI default.
    font_path = os.environ.get("POPPINS_TTF") or wm["font_path"]
    if not Path(font_path).exists():
        raise FileNotFoundError(
            f"Font not found: {font_path}\n"
            f"Install Poppins via your system font manager, then either set "
            f"$POPPINS_TTF to the .ttf path or update wordmark.font_path in "
            f"brand.toml."
        )

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    cap_height = font["OS/2"].sCapHeight
    descent = abs(font["hhea"].descent)

    glyphs = []
    x = 0
    for ch in wm["text"]:
        glyph_name = cmap.get(ord(ch))
        if not glyph_name:
            raise ValueError(f"No glyph for character {ch!r} in font")
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        glyphs.append((ch, pen.getCommands(), x, hmtx[glyph_name][0]))
        x += hmtx[glyph_name][0]

    return glyphs, x, cap_height, descent


def wordmark_svg(cfg: dict, variant: str) -> str:
    """Generate the wordmark SVG for a given variant."""
    wm = cfg["wordmark"]
    var = cfg["variants"][variant]

    glyphs, total_width, cap_height, descent = extract_text_paths(cfg)
    margin = 50
    vb_width = total_width + 2 * margin
    vb_height = cap_height + 100  # extra room for descenders

    ink_color = color(cfg, var["ink"])
    accent_color = color(cfg, var["accent"])

    split = wm["split"]
    ink_glyphs = glyphs[:split]
    accent_glyphs = glyphs[split:]

    def build_paths(group):
        return "\n      ".join(
            f'<path d="{path}" transform="translate({x + margin}, 0)"/>'
            for ch, path, x, adv in group
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_width} {vb_height}" width="{vb_width}" height="{vb_height}" role="img" aria-label="{wm["text"]}">
  <title>{wm["text"]}</title>
  <g transform="translate(0, {cap_height + 50}) scale(1, -1)">
    <g fill="{ink_color}">
      {build_paths(ink_glyphs)}
    </g>
    <g fill="{accent_color}">
      {build_paths(accent_glyphs)}
    </g>
  </g>
</svg>
'''


def write_wordmarks(cfg: dict) -> list[Path]:
    """Generate all wordmark SVG variants."""
    written = []
    for variant in cfg["variants"]:
        svg = wordmark_svg(cfg, variant)
        suffix = "" if variant == "color" else f"-{variant.replace('_', '-')}"
        path = SVG_DIR / f"audiophore-wordmark{suffix}.svg"
        path.write_text(svg)
        written.append(path)
    return written


# ─── Lockup generation ──────────────────────────────────────────────

def extract_inner(svg_text: str) -> str:
    """Strip the outer <svg> wrapper from an SVG string, keeping content."""
    start = svg_text.find(">", svg_text.find("<svg")) + 1
    end = svg_text.rfind("</svg>")
    inner = svg_text[start:end].strip()
    # Remove <title> and <desc> tags
    import re
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.DOTALL)
    inner = re.sub(r"<desc>.*?</desc>", "", inner, flags=re.DOTALL)
    return inner.strip()


def lockup_svg(cfg: dict, variant: str) -> str:
    """Build a lockup combining symbol and wordmark for a variant."""
    lk = cfg["lockup"]
    sym_size = cfg["symbol"]["viewbox"]
    glyphs, total_width, cap_height, descent = extract_text_paths(cfg)

    wm_scale = lk["wordmark_cap_target"] / cap_height
    wm_vb_width = total_width + 100  # matches wordmark margin = 50 each side
    wm_vb_height = cap_height + 100

    wm_w_scaled = int(wm_vb_width * wm_scale)
    wm_h_scaled = int(wm_vb_height * wm_scale)

    total_w = sym_size + lk["gap"] + wm_w_scaled
    total_h = sym_size
    wm_y = (total_h - wm_h_scaled) // 2

    sym_inner = extract_inner(symbol_svg(cfg, variant))
    wm_inner = extract_inner(wordmark_svg(cfg, variant))

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}" role="img" aria-label="{cfg["meta"]["name"]}">
  <title>{cfg["meta"]["name"]}</title>
  <g transform="translate(0, 0)">
    {sym_inner}
  </g>
  <g transform="translate({sym_size + lk["gap"]}, {wm_y}) scale({wm_scale})">
    {wm_inner}
  </g>
</svg>
'''


def write_lockups(cfg: dict) -> list[Path]:
    """Generate all lockup SVG variants."""
    written = []
    for variant in cfg["variants"]:
        svg = lockup_svg(cfg, variant)
        suffix = "" if variant == "color" else f"-{variant.replace('_', '-')}"
        path = SVG_DIR / f"audiophore-lockup{suffix}.svg"
        path.write_text(svg)
        written.append(path)
    return written


# ─── PNG rasterization ──────────────────────────────────────────────

def rasterize_pngs(cfg: dict) -> list[Path]:
    """Convert all SVGs to PNGs at the configured sizes."""
    written = []

    # Symbols (square, all variants except dark_bg which doesn't have a symbol)
    for variant in cfg["variants"]:
        if variant == "dark_bg":
            continue
        suffix = "" if variant == "color" else f"-{variant.replace('_', '-')}"
        src = SVG_DIR / f"audiophore-symbol{suffix}.svg"
        if not src.exists():
            continue
        for size in cfg["sizes"]["symbol"]["px"]:
            dst = PNG_DIR / f"audiophore-symbol{suffix}-{size}.png"
            cairosvg.svg2png(
                url=str(src), write_to=str(dst),
                output_width=size, output_height=size,
            )
            written.append(dst)

    # Lockups (rectangular)
    for variant in cfg["variants"]:
        suffix = "" if variant == "color" else f"-{variant.replace('_', '-')}"
        src = SVG_DIR / f"audiophore-lockup{suffix}.svg"
        if not src.exists():
            continue
        for size in cfg["sizes"]["lockup"]["px"]:
            dst = PNG_DIR / f"audiophore-lockup{suffix}-{size}.png"
            cairosvg.svg2png(url=str(src), write_to=str(dst), output_width=size)
            written.append(dst)

    # Wordmarks
    for variant in cfg["variants"]:
        suffix = "" if variant == "color" else f"-{variant.replace('_', '-')}"
        src = SVG_DIR / f"audiophore-wordmark{suffix}.svg"
        if not src.exists():
            continue
        # Skip mono variants of wordmark for PNG (just keep light/dark color and teal)
        if variant in ("mono_black", "mono_white", "teal"):
            continue
        for size in cfg["sizes"]["wordmark"]["px"]:
            dst = PNG_DIR / f"audiophore-wordmark{suffix}-{size}.png"
            cairosvg.svg2png(url=str(src), write_to=str(dst), output_width=size)
            written.append(dst)

    return written


# ─── Favicons ───────────────────────────────────────────────────────

def build_favicons(cfg: dict) -> list[Path]:
    """Generate the favicon set from the canonical color symbol."""
    written = []
    src = SVG_DIR / "audiophore-symbol.svg"
    for size in cfg["sizes"]["favicon"]["px"]:
        dst = FAVICON_DIR / f"favicon-{size}.png"
        cairosvg.svg2png(
            url=str(src), write_to=str(dst),
            output_width=size, output_height=size,
        )
        written.append(dst)

    # Multi-resolution favicon.ico via ImageMagick
    ico_path = FAVICON_DIR / "favicon.ico"
    inputs = [str(FAVICON_DIR / f"favicon-{s}.png") for s in cfg["sizes"]["favicon"]["ico_sizes"]]
    if not all(Path(p).exists() for p in inputs):
        print("  warning: skipping favicon.ico — required PNG sizes missing")
        return written

    convert_bin = shutil.which("convert") or shutil.which("magick")
    if not convert_bin:
        print("  warning: skipping favicon.ico — ImageMagick not found")
        return written

    cmd = [convert_bin, *inputs, str(ico_path)]
    subprocess.run(cmd, check=True)
    written.append(ico_path)
    return written


# ─── Cleanup and CLI ────────────────────────────────────────────────

def clean():
    """Remove all generated assets."""
    for d in (SVG_DIR, PNG_DIR, FAVICON_DIR):
        if d.exists():
            shutil.rmtree(d)
            print(f"  removed {d.relative_to(ROOT)}")
    for d in (SVG_DIR, PNG_DIR, FAVICON_DIR):
        d.mkdir(parents=True, exist_ok=True)


def ensure_dirs():
    for d in (SVG_DIR, PNG_DIR, FAVICON_DIR):
        d.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument(
        "targets", nargs="*",
        choices=["all", "symbol", "wordmark", "lockup", "png", "favicon", []],
        default=[],
        help="Which assets to build (default: all)",
    )
    parser.add_argument("--clean", action="store_true", help="Remove generated files first")
    args = parser.parse_args()

    cfg = load_config()
    ensure_dirs()

    if args.clean:
        print("Cleaning…")
        clean()

    targets = set(args.targets) if args.targets else {"all"}
    if "all" in targets:
        targets = {"symbol", "wordmark", "lockup", "png", "favicon"}

    if "symbol" in targets:
        print("Building symbol SVGs…")
        for p in write_symbols(cfg):
            print(f"  {p.relative_to(ROOT)}")
    if "wordmark" in targets:
        print("Building wordmark SVGs…")
        for p in write_wordmarks(cfg):
            print(f"  {p.relative_to(ROOT)}")
    if "lockup" in targets:
        print("Building lockup SVGs…")
        for p in write_lockups(cfg):
            print(f"  {p.relative_to(ROOT)}")
    if "png" in targets:
        print("Rasterizing PNGs…")
        pngs = rasterize_pngs(cfg)
        print(f"  {len(pngs)} PNG files written to {PNG_DIR.relative_to(ROOT)}/")
    if "favicon" in targets:
        print("Building favicons…")
        for p in build_favicons(cfg):
            print(f"  {p.relative_to(ROOT)}")

    print("\nDone.")


if __name__ == "__main__":
    main()
