# Audiophore brand asset Makefile
#
# Usage:
#   make            # build everything (SVG + PNG + favicon + BRANDING.md)
#   make svgs       # only SVGs
#   make pngs       # only PNGs (requires SVGs to exist)
#   make favicons   # only favicons
#   make docs       # only BRANDING.md
#   make clean      # remove all generated assets
#   make check      # CI check: exit 1 if BRANDING.md is out of sync
#   make install    # install Python dependencies
#
# The brand.toml file is the source of truth. Edit it, then run `make`.

PYTHON := python3
SCRIPTS := scripts
ASSETS := logos

.PHONY: all build svgs pngs favicons docs clean check install help

all: build docs

help:
	@echo "Targets:"
	@echo "  all      - build everything (default)"
	@echo "  build    - generate SVGs, PNGs, and favicons"
	@echo "  svgs     - generate only SVGs"
	@echo "  pngs     - generate only PNGs (requires SVGs)"
	@echo "  favicons - generate only favicons"
	@echo "  docs     - regenerate BRANDING.md from brand.toml"
	@echo "  clean    - remove all generated assets"
	@echo "  check    - verify BRANDING.md is in sync with brand.toml"
	@echo "  install  - install Python dependencies"

build:
	$(PYTHON) $(SCRIPTS)/build.py all

svgs:
	$(PYTHON) $(SCRIPTS)/build.py symbol wordmark lockup

pngs:
	$(PYTHON) $(SCRIPTS)/build.py png

favicons:
	$(PYTHON) $(SCRIPTS)/build.py favicon

docs:
	$(PYTHON) $(SCRIPTS)/render_branding_md.py

clean:
	$(PYTHON) $(SCRIPTS)/build.py --clean all

check:
	$(PYTHON) $(SCRIPTS)/render_branding_md.py --check

install:
	$(PYTHON) -m pip install -r requirements.txt
