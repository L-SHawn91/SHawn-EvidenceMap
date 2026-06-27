# SHawn EvidenceMap

PUBLIC_STATUS: public-demo

Research evidence mapping from public literature metadata.

Public landing page:

```text
https://l-shawn91.github.io/SHawn-EvidenceMap/
```

## What It Does

SHawn EvidenceMap turns a research question into a small, transparent evidence map:

1. Plan a public literature query
2. Search public metadata sources
3. Group papers by simple evidence themes
4. Build a claim/evidence table
5. Export Markdown or JSON

## Current Scope

This repository starts as a clean public-demo skeleton. It does not copy private SHawn ecosystem history.

Included:
- Public metadata search
- PubMed E-utilities adapter
- Europe PMC adapter
- OpenAlex adapter for general scholarly cartridges
- Cartridge architecture with `bio` as the first active cartridge
- Abstract-level triage
- Claim/evidence table schema
- Markdown and JSON export

Excluded:
- Private full-text corpus
- Private PDF ingestion
- Manuscript drafting
- Clinical advice
- Private lab or non-public project data
- SHawn internal agent operations

## Quick Start

```bash
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --cartridge bio --limit 10 --markdown
```

Ranking modes:

```bash
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --ranking-mode recent --markdown
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --ranking-mode foundational --markdown
```

## Cartridge Architecture

The public product is one repo with domain cartridges:

```text
src/evidencemap/core/
src/evidencemap/cartridges/bio/
```

Active public-demo cartridges:

- `bio`: biomedical literature
- `ai_cs`: AI and computer science
- `policy`: policy and governance research
- `education`: education research
- `patent_tech`: patent/technology landscape research

Each cartridge keeps its own source choices, evidence labels, and ranking behavior without splitting the public product into separate repos.

See:

```text
docs/CARTRIDGE_ARCHITECTURE.md
```

Local web demo:

```bash
python3 web/server.py
```

Then open:

```text
http://127.0.0.1:8765/
```

For local development:

```bash
python3 -m pip install -e .
evidencemap "endometrial organoid implantation" --limit 10 --markdown
```

## Safety Note

This tool is for research planning and literature triage. Outputs should be manually verified before citation, clinical interpretation, grant submission, or manuscript use.

## Public / Private Boundary

This repo is public-demo only. It must not contain private paths, credentials, private databases, non-public project state, or personal workflow logs.
