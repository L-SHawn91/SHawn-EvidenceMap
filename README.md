# SHawn EvidenceMap

PUBLIC_STATUS: public-demo · early-stage OSS

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Public boundary](https://img.shields.io/badge/public--boundary-metadata%20%2B%20toy%20data-green.svg)](docs/PUBLIC_BOUNDARY.md)
[![Release: v0.1.1](https://img.shields.io/badge/release-v0.1.1-informational.svg)](CHANGELOG.md)

Research evidence mapping from public literature metadata.

## Public review quick facts

- **Representative repo:** `SHawn-EvidenceMap`
- **License:** Apache-2.0
- **Release:** `v0.1.1` hardening release after `v0.1.0` public-safe launch
- **Demo:** https://l-shawn91.github.io/SHawn-EvidenceMap/
- **Verification:** `pytest`, `public_safety_scan`, and `compileall` pass locally
- **Maintainer evidence:** [`docs/MAINTAINER_EVIDENCE.md`](docs/MAINTAINER_EVIDENCE.md)
- **Verification details:** [`docs/VERIFICATION.md`](docs/VERIFICATION.md)
- **Boundary:** public scholarly metadata, synthetic examples, templates, and public reports only


**License:** Apache-2.0

Public landing page:

```text
https://l-shawn91.github.io/SHawn-EvidenceMap/
```

Maintainer evidence:

```text
docs/MAINTAINER_EVIDENCE.md
```

## SHawn public OSS stack

SHawn EvidenceMap is the report/flagship layer of a public-safe research-agent evidence workflow stack:

| Layer | Public repo | Role |
|---|---|---|
| Search | [`shawn-bio-search-lite`](https://github.com/L-SHawn91/shawn-bio-search-lite) | Public scholarly metadata adapters |
| Map | [`paper-map-lite`](https://github.com/L-SHawn91/paper-map-lite) | Toy claim/evidence graph schemas |
| Report | [`SHawn-EvidenceMap`](https://github.com/L-SHawn91/SHawn-EvidenceMap) | Evidence maps and public reports |
| Coordinate | [`shawn-sync-lite`](https://github.com/L-SHawn91/shawn-sync-lite) | Public-safe manifests and boundary templates |
| Execute safely | [`newbrain-router`](https://github.com/L-SHawn91/newbrain-router) | Dry-run routing and approval-gate examples |
| QA documents | [`shawn-docx-qa`](https://github.com/L-SHawn91/shawn-docx-qa) / [`SHawn-hwp`](https://github.com/L-SHawn91/SHawn-hwp) | Public document QA utilities |
| Present | [`SHawn-WEB`](https://github.com/L-SHawn91/SHawn-WEB) | Public hub/demo surface |

This is not a dump of private SHawn repos. The public stack contains schemas, templates, toy data, public metadata adapters, mock executors, and public reports only.

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
- Crossref adapter for general scholarly cartridges
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
- `legal`: legal/regulatory research
- `patent_tech`: patent/technology landscape research

Each cartridge keeps its own source choices, evidence labels, and ranking behavior without splitting the public product into separate repos.

See:

```text
docs/CARTRIDGE_ARCHITECTURE.md
```

## Customer Reports

Generate a fixed customer-facing preliminary report:

```bash
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --cartridge bio --limit 5 --report
```

Generate a visual HTML report:

```bash
PYTHONPATH=src python3 -m evidencemap.cli "drug screening organoid cancer therapeutic" --cartridge bio --limit 5 --html-report > report.html
```

The Markdown report format is fixed across cartridges:

1. Executive Summary
2. Scope
3. Method Snapshot
4. Evidence Mix
5. Year Coverage
6. Ranked Evidence Table
7. Initial Interpretation
8. Recommended Next Steps
9. Limitations
10. Delivery Note

Sample reports:

```text
examples/reports/bio_drug_screening_organoid_cancer.md
examples/reports/ai_cs_llm_benchmark_dataset.md
examples/reports/policy_climate_intervention_evaluation.md
examples/reports/education_intervention_learning_outcomes.md
examples/reports/legal_ai_regulation_liability.md
examples/reports/patent_tech_crispr_landscape.md
```

Visual sample reports:

```text
examples/reports/html/
```

The visual brief is the preferred client-facing pilot deliverable. It includes:

1. Executive Verdict
2. Evidence Score Ring
3. Executive Snapshot
4. Key Findings
5. Evidence Dashboard
6. Source Coverage
7. Year Timeline
8. Quality Signals
9. Top Evidence
10. Ranked Evidence Table
11. Evidence Gap Check
12. Action Plan
13. Delivery Package
14. QA and Limitations

The visual brief includes an `Export PDF` button for browser print/PDF delivery.

See:

```text
docs/REPORT_TEMPLATE.md
```

## Source Boundary

Public cartridges use no-auth public metadata sources only. API-key, login, paid, institutional, customer-uploaded, or private SHawn ecosystem sources are private-only.

See:

```text
docs/SOURCE_BOUNDARY.md
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

Before release or tag, run:

```bash
bash scripts/public_safety_scan.sh
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --cartridge bio --limit 3 --markdown
```

See `SECURITY.md`, `LICENSE`, and `CITATION.cff` for public-use boundaries.

## Public / Private Boundary

This repo is public-demo only. It must not contain private paths, credentials, private databases, non-public project state, or personal workflow logs.

## Maintainer checks

```bash
PYTHONPATH=src python3 -m pytest -q
python3 scripts/public_safety_scan.py .
python3 -m compileall -q src
```

## Project documents

- [Public boundary](docs/PUBLIC_BOUNDARY.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
