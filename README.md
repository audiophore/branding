# Audiophore Brand Assets

This directory contains the official Audiophore logo files and brand
guidelines. See `BRANDING.md` for usage rules, color values, and
typography.

> **Regenerating the assets?** The kit builds from `brand.toml` —
> run `make install && make help` to get started. (Full developer
> docs land in a later pass.)

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
