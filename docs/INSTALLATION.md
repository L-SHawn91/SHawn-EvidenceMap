# Installation

SHawn EvidenceMap v0.2.2 is distributed as a verified wheel attached to the GitHub release. PyPI publication is not currently claimed.

## Install the release wheel

Use an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/download/v0.2.2/shawn_evidencemap-0.2.2-py3-none-any.whl
```

Verify the command-line interface:

```bash
evidencemap --help
evidencemap "open science metadata reproducibility" --limit 3 --markdown --no-cache
python -m evidencemap.refdb public-demo --db public-metadata.sqlite3
python -m evidencemap.refdb verify --db public-metadata.sqlite3
```

The first workflow searches public scholarly metadata using the domain-neutral `generic` cartridge. The database workflow verifies a bundled fixed fixture; it does not accept replacement DOI, PMID, or GEO identifiers in v0.2.2.

For the complete offline pilot, follow [`PILOT_QUICKSTART.md`](PILOT_QUICKSTART.md).

## Verify the wheel checksum

Download both release assets:

```bash
curl -LO https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/download/v0.2.2/shawn_evidencemap-0.2.2-py3-none-any.whl
curl -LO https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/download/v0.2.2/SHA256SUMS
sha256sum -c SHA256SUMS
```

## Install from a source checkout

```bash
git clone https://github.com/L-SHawn91/SHawn-EvidenceMap.git
cd SHawn-EvidenceMap
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
PYTHONPATH=src python -m pytest -q
```

## Distribution boundary

The release contains source code and public examples only. It does not include private corpora, manuscripts, PDFs, credentials, private workflow state, or unpublished research data.
