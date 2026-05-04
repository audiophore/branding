# Audiophore Brand Guidelines

Logo, colors, typography, and usage rules for the Audiophore project.

This document is authoritative. If you're using Audiophore branding —
in a fork, a derivative project, an article, an integration page, a
talk slide — these are the rules. They exist to keep the project
visually consistent across contexts.

---

## The mark

The Audiophore symbol is a **5×5 RGB pixel grid** where each row is
colored to represent a frequency band that the project actually
consumes from its audio analysis pipeline. Reading top to bottom:

| Row | Frequency band | Color | Hex |
|-----|---------------|-------|-----|
| Top | Highs | Cyan | `#00E5FF` |
| 2nd | Mid-highs | Teal | `#00D4C8` |
| Middle | Mids | Green | `#3DD68C` |
| 4th | Mid-lows | Amber | `#FFB020` |
| Bottom | Bass | Magenta | `#FF2D9C` |

The lit pixels form a stylized phi (φ) — the etymological root of
*-phore* — making the mark a piece of visual vocabulary that names
itself.

---

## Variants

Five color treatments are provided. Use the most expressive one your
context supports.

| Variant | Use when |
|---------|----------|
| **Color** (canonical) | Web, app UIs, social, GitHub avatar, slides — wherever full color is available and renders correctly |
| **Teal** (single accent) | Single-color contexts that *can* render color but only one — embroidery on a dark cap, single-color Pantone print, accent overlays |
| **Mono black** | Black-on-white print, light backgrounds where color isn't appropriate (academic papers, formal docs) |
| **Mono white** | White-on-dark print, dark backgrounds where color isn't appropriate, terminal banners |

For each color treatment, three forms exist: **symbol-only** (favicon
and avatar), **wordmark-only** (header bars where the symbol would be
redundant), and **lockup** (symbol + wordmark side-by-side, default
for marketing).

---

## Color palette

### Primary accent

The single color that represents Audiophore in any context where one
color must stand alone:

- **Teal** — `#00D4C8` (RGB 0, 212, 200) (HSL 176°, 100%, 42%)

This is the color in the project's "monochrome" CI badges, terminal
output, plot accents, etc.

### Spectrum palette

The five colors that, taken together, are the brand. Each has a
specific semantic meaning tied to FFT band coding:

- **Cyan** `#00E5FF` — highs (treble, hats, top-end)
- **Teal** `#00D4C8` — mid-highs (vocals, snares)
- **Green** `#3DD68C` — mids (the harmonic body)
- **Amber** `#FFB020` — mid-lows (warmth, low harmonics)
- **Magenta** `#FF2D9C` — bass (kicks, sub)

Use them in this order whenever you visualize multiple bands. The
ordering matters — it matches the literal high-to-low frequency
arrangement of the pixel grid in the symbol.

### Neutrals

- **Ink** `#1a1f2e` — primary text on light backgrounds
- **Paper** `#FFFFFF` — primary text on dark backgrounds
- **Mute** `#8b95a8` — secondary text, captions, metadata
- **Wash light** `#f8f9fa` — neutral light surface (panel backgrounds)
- **Wash dark** `#0a0e1a` — neutral dark surface

---

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

---

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

---

## Files in this kit

```
logos/
├── svg/
│   ├── audiophore-symbol.svg              ← canonical full-color mark
│   ├── audiophore-symbol-teal.svg         ← single-accent fallback
│   ├── audiophore-symbol-mono-black.svg   ← print, light bg
│   ├── audiophore-symbol-mono-white.svg   ← print, dark bg
│   ├── audiophore-wordmark.svg            ← wordmark for light bg
│   ├── audiophore-wordmark-dark-bg.svg    ← wordmark for dark bg
│   ├── audiophore-wordmark-teal.svg       ← all-accent variant
│   ├── audiophore-wordmark-mono-black.svg
│   ├── audiophore-wordmark-mono-white.svg
│   ├── audiophore-lockup.svg              ← canonical, light bg
│   ├── audiophore-lockup-dark-bg.svg      ← canonical, dark bg
│   ├── audiophore-lockup-teal.svg         ← all-accent variant
│   ├── audiophore-lockup-mono-black.svg
│   └── audiophore-lockup-mono-white.svg
├── png/
│   ├── audiophore-symbol-{28,64,128,256,460,512,1024}.png
│   ├── audiophore-symbol-teal-{...}.png
│   ├── audiophore-symbol-mono-black-{...}.png
│   ├── audiophore-symbol-mono-white-{...}.png
│   ├── audiophore-wordmark-{200,400,800}.png
│   ├── audiophore-wordmark-dark-bg-{200,400,800}.png
│   ├── audiophore-lockup-{400,800,1200,2400}.png
│   ├── audiophore-lockup-dark-bg-{...}.png
│   ├── audiophore-lockup-teal-{...}.png
│   ├── audiophore-lockup-mono-black-{...}.png
│   └── audiophore-lockup-mono-white-{...}.png
└── favicon/
    ├── favicon.ico             ← multi-resolution legacy favicon
    ├── favicon-{16,32,48,64,180,192,512}.png
    └── (favicon-180 doubles as Apple touch icon)
```

---

## Installing the GitHub avatar

GitHub's org avatar field accepts PNG only (not SVG). Upload:

```
logos/png/audiophore-symbol-460.png
```

That's the size GitHub recommends (their docs say 500×500 max but
460×460 leaves a safe margin). Drag-and-drop into the Settings page.

The avatar will be cropped circular by GitHub's UI, but our pixel
grid stays fully visible because we built it to fit a square with
safe margins.

---

## Changes and forks

If you fork or derive from Audiophore and want to make a related
brand:

- **Don't reuse the canonical Audiophore mark** for derivative
  projects — make your own.
- **You can use the spectrum palette** (the five band colors) in
  your own work; the colors aren't proprietary.
- **You can reference Audiophore typographically** (e.g., "an
  Audiophore-compatible adapter") — that's just the project name.

---

## Credits

- **Type**: Poppins by Indian Type Foundry, Open Font License.
- **Concept and execution**: Audiophore project, MIT/Apache-2.0.
- **First version**: 2026, by Aaron Cupp + Claude.
