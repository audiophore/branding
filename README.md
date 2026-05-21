# Audiophore Brand Assets

This directory contains the official Audiophore logo files and brand
guidelines. See `BRANDING.md` for usage rules, color values, and
typography.

## Quick start

- **GitHub org avatar:** upload `logos/png/audiophore-symbol-460.png`
- **Website favicon:** use `logos/favicon/favicon.ico` (multi-resolution)
- **Apple touch icon:** use `logos/favicon/favicon-180.png`
- **README hero / docs:** use `logos/svg/audiophore-lockup.svg` (light bg)
  or `audiophore-lockup-dark-bg.svg` (dark bg)
- **Embed in your own page:** copy a SVG file or link an absolute URL

## Browse the assets

Open `preview.html` in a browser to see every variant rendered at
working sizes against light and dark backgrounds.

## Files

```
.
├── BRANDING.md         ← usage rules, colors, fonts, do's and don'ts
├── README.md           ← this file
├── preview.html        ← visual inventory of every asset
└── logos/
    ├── svg/            ← source files, scale to any size
    ├── png/            ← rasterized at standard sizes
    └── favicon/        ← favicon.ico and PWA icon sizes
```

## Consuming the kit

For ad-hoc use, just grab a file (see *Quick start*). To consume the kit at a
**pinned version** — so a brand update can't silently restyle your project —
use a tagged release. Releases are versioned `vX.Y.Z` and listed on the
[Releases page](https://github.com/audiophore/branding/releases); each one
ships a `.zip` / `.tar.gz` bundle of `logos/`, `BRANDING.md`, and `preview.html`.

**As a git submodule** (how `audiophore/website` consumes it):

```sh
git submodule add https://github.com/audiophore/branding.git branding
git -C branding checkout v1.0.0      # pin to a release tag
git add branding && git commit       # the recorded submodule commit is your version pin
```

To move to a newer release later, check out the new tag inside the submodule
and commit the bump — a reviewable one-line diff.

**As a downloaded bundle:**

```sh
gh release download v1.0.0 --repo audiophore/branding   # grabs the .zip + .tar.gz
```

Either way, the `logos/` directory layout and filenames are a stable contract
(see *Files* above), so a pin bump never moves assets out from under you.

## Developing the kit

Every asset in `logos/` — and the tables in `BRANDING.md` — is generated
from `brand.toml`. Don't hand-edit the outputs; edit `brand.toml` (or the
prose in `BRANDING.md`) and rebuild.

```sh
make install     # one-time: install the Python build deps
make             # rebuild all SVGs, PNGs, favicons, and BRANDING.md tables
make help        # list every target
```

### Editing the brand

`brand.toml` is the single source of truth — colors, grid layout, output
sizes, and variants all live there. After editing it, run `make` and commit
the regenerated `logos/` alongside your `brand.toml` change.

Common tasks:

- **Add a raster size** — add the pixel value under the relevant
  `[sizes.*]` list, then `make`.
- **Change a color** — edit the hex in `[colors.spectrum]` /
  `[colors.neutrals]`; `make` updates the assets and the `BRANDING.md`
  tables together.
- **Add a variant** — add a `[variants.<name>]` block (give it a flavored
  `purpose`), then `make`.

### Requirements

- Python 3.11+ (CI uses 3.12)
- [ImageMagick](https://imagemagick.org) — packs the multi-resolution `favicon.ico`
- **Poppins Medium** — the wordmark glyph paths are derived from it. On
  Linux/CI it's read from the path in `brand.toml`; on other systems point
  `$POPPINS_TTF` at your `Poppins-Medium` file before running `make`.

### CI

CI re-runs `make` on every PR and fails if the committed `logos/` or
`BRANDING.md` drift from what `brand.toml` produces — so the only way to
change an asset is via `brand.toml` + `make`.

### Releases

Releases are automated with [release-please](https://github.com/googleapis/release-please).
Merging changes to `main` opens (or updates) a `chore(main): release X.Y.Z` PR
carrying the version bump and changelog; **merge that PR to cut the release** —
it tags `vX.Y.Z`, publishes the GitHub Release, and attaches the asset bundle.
There's no manual `git tag` or `gh release create`. Version bumps follow
Conventional Commits: `feat:` → minor, `fix:` → patch.
