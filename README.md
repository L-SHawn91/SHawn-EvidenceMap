# SHawn EvidenceMap

**Bring public identifiers or a research claim → get an auditable candidate-evidence table with explicit human review gates.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Public boundary](https://img.shields.io/badge/public--boundary-metadata%20%2B%20toy%20data-green.svg)](docs/PUBLIC_BOUNDARY.md)
[![Release: v0.2.4](https://img.shields.io/badge/release-v0.2.4-informational.svg)](CHANGELOG.md)
[![Public CI](https://github.com/L-SHawn91/SHawn-EvidenceMap/actions/workflows/ci.yml/badge.svg)](https://github.com/L-SHawn91/SHawn-EvidenceMap/actions/workflows/ci.yml)

A local-first Python CLI with two bounded workflows: normalize DOI/PMID/OpenAlex/accession and bibliographic records into an integrity-checked audit trail, or search public metadata for candidate source sentences around a user-supplied claim. Human review states are explicit; the tool never auto-labels a source as supporting or contradicting a claim. No account, upload, or cloud workspace is required.

**[▶ Watch the 60-second demo](https://l-shawn91.github.io/SHawn-EvidenceMap/assets/pilot-demo-60s.mp4)** · **[Try the free pilot](https://l-shawn91.github.io/SHawn-EvidenceMap/pilot.html)** · **[Request a validation slot](https://github.com/L-SHawn91/SHawn-EvidenceMap/discussions/9)**

## Public review quick facts

- **Representative repo:** `SHawn-EvidenceMap`
- **License:** Apache-2.0
- **Release:** `v0.2.4` verifiable metadata bridge and interoperability release
- **Next release candidate:** `v0.3.0` claim-review workflow (unreleased on this branch until tagged)
- **Demo:** https://l-shawn91.github.io/SHawn-EvidenceMap/
- **Synthetic database demo:** https://l-shawn91.github.io/SHawn-EvidenceMap/db-demo/
- **Public metadata linkage demo:** https://l-shawn91.github.io/SHawn-EvidenceMap/public-metadata-demo/
- **Executable 60-second bridge demo:** https://l-shawn91.github.io/SHawn-EvidenceMap/assets/pilot-demo-60s.mp4
- **Free early validation:** https://l-shawn91.github.io/SHawn-EvidenceMap/pilot.html
- **Five-minute pilot:** [`docs/PILOT_QUICKSTART.md`](docs/PILOT_QUICKSTART.md)
- **Verification:** public CI passes `pytest`, database integrity and determinism checks, `public_safety_scan`, `compileall`, wheel build, CLI verification, and artifact upload
- **Installable release:** [`v0.2.4` wheel + SHA256SUMS](https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/tag/v0.2.4)
- **Installation:** [`docs/INSTALLATION.md`](docs/INSTALLATION.md)
- **Community/validation requests:** [GitHub Discussion #9](https://github.com/L-SHawn91/SHawn-EvidenceMap/discussions/9)
- **Public benchmark:** [`docs/PUBLIC_BENCHMARK_2026-07-11.md`](docs/PUBLIC_BENCHMARK_2026-07-11.md) · [runner and raw JSON](benchmarks/README.md)
- **Ecosystem comparison:** [`docs/ECOSYSTEM_COMPARISON_2026-07-11.md`](docs/ECOSYSTEM_COMPARISON_2026-07-11.md) · [43-repository raw snapshot](benchmarks/results/2026-07-11-ecosystem-snapshot.json)
- **Pilot outreach strategy:** [`docs/PILOT_OUTREACH_STRATEGY.md`](docs/PILOT_OUTREACH_STRATEGY.md)
- **Maintainer evidence:** [`docs/MAINTAINER_EVIDENCE.md`](docs/MAINTAINER_EVIDENCE.md)
- **Verification details:** [`docs/VERIFICATION.md`](docs/VERIFICATION.md)
- **Database reference:** [`docs/DATABASE_REFERENCE.md`](docs/DATABASE_REFERENCE.md)
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

SHawn EvidenceMap supports two public workflows:

1. Search public scholarly metadata and build a transparent candidate-evidence table.
2. Keep the search topic separate from an optional proposition supplied with `--claim`.
3. Preserve candidate sentence location, DOI/PMID, source name, and source URL.
4. Apply only user-supplied `candidate`, `reviewed-support`, `reviewed-contradict`, or `uncertain` relation states.
5. Gate a deterministic statement wrapper behind at least two reviewed-support rows and zero reviewed-contradict rows.
6. Ingest DOI, PMID, OpenAlex work ID, public accession, CSV, RIS, or conservative BibTeX records.
7. Normalize identifiers, reject cross-entity collisions, preserve ingest audit events, and export deterministic handoffs.

## Database-backed reference pipeline

The public reference layer demonstrates database mechanics without publishing non-public research records. It uses Python's standard-library `sqlite3` module to persist paper, dataset, and claim entities with normalized identifiers, provenance, typed relations, schema migrations, integrity checks, and deterministic export.

```bash
python3 -m evidencemap.refdb demo --db demo.sqlite3
python3 -m evidencemap.refdb public-demo --db public-metadata.sqlite3
python3 -m evidencemap.refdb ingest --db bridge.sqlite3 --input records.csv --format csv
python3 -m evidencemap.refdb verify --db public-metadata.sqlite3
python3 -m evidencemap.refdb export --db bridge.sqlite3 --out records.ris --format ris
python3 -m evidencemap.refdb page --db public-metadata.sqlite3 --out index.html
```

The synthetic demo contains generated records. The public-metadata demo contains only identifiers, titles, an official NCBI registry linkage, and source URLs; it does not include abstracts, full text, sample-level values, or a validated scientific conclusion. See the [`five-minute pilot`](docs/PILOT_QUICKSTART.md) and [`database reference`](docs/DATABASE_REFERENCE.md).

## Current Scope

This repository starts as a clean public-demo skeleton. It does not copy private SHawn ecosystem history.

Included:
- Public metadata search
- PubMed E-utilities adapter
- Europe PMC adapter
- OpenAlex adapter for general scholarly cartridges
- Crossref adapter for general scholarly cartridges
- Cartridge architecture with `generic` as the domain-neutral default and explicit domain cartridges
- Abstract-level triage
- Search-topic/claim separation and candidate-evidence table schema
- Human-authored relation review files with fail-closed validation
- Evidence-bounded statement gate; no automatic support/contradiction judgment
- Markdown and JSON export
- SQLite reference schema with migrations and foreign-key integrity checks
- DOI/PMID/OpenAlex/accession normalization and collision-safe entity upsert
- Identifier-list, CSV, conservative RIS, and conservative BibTeX ingestion
- Per-record inserted/merged/rejected audit events and input provenance
- Deterministic entity-only CSV/RIS/BibTeX handoff exports
- Paper–dataset–claim relations and source provenance
- Deterministic database JSON and static HTML export
- Offline public paper–dataset registry-linkage example using identifiers, titles, and source URLs only
- Five-minute pilot and structured feedback path for genuine external runs

Excluded:
- Private full-text corpus
- Private PDF ingestion
- Unrestricted manuscript drafting or automatic claim validation
- Clinical advice
- Private lab or non-public project data
- SHawn internal agent operations

## Quick Start

Install the verified v0.2.4 release wheel:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/download/v0.2.4/shawn_evidencemap-0.2.4-py3-none-any.whl
```

### Search public metadata for your own topic

```bash
evidencemap "open science metadata reproducibility" --limit 3 --markdown --no-cache
```

The domain-neutral `generic` cartridge is the default. Select `--cartridge bio`, `ai_cs`, `policy`, `education`, `legal`, or `patent_tech` when domain-specific sources and labels are appropriate.

### Verify the fixed SQLite reference fixture

```bash
python -m evidencemap.refdb public-demo --db public-metadata.sqlite3
python -m evidencemap.refdb verify --db public-metadata.sqlite3
```

Repeated OpenAlex-backed searches can use an optional `OPENALEX_API_KEY` environment variable. Never commit or post the key. One short no-key pilot uses OpenAlex's limited demo allowance; see [`docs/INSTALLATION.md`](docs/INSTALLATION.md).

### Bridge your own public identifiers or bibliographic records

```bash
printf 'doi:10.1000/example\nPMID:12345\nhttps://openalex.org/W98765\naccession:GSE1234\n' > identifiers.txt
python -m evidencemap.refdb ingest --db bridge.sqlite3 --input identifiers.txt --format identifiers
python -m evidencemap.refdb verify --db bridge.sqlite3
python -m evidencemap.refdb export --db bridge.sqlite3 --out bridge.csv --format csv
python -m evidencemap.refdb export --db bridge.sqlite3 --out bridge.ris --format ris
python -m evidencemap.refdb export --db bridge.sqlite3 --out bridge.bib --format bibtex
```

Identifier-only input is **not registry-resolved metadata**. RIS and BibTeX support a documented conservative subset and reject unsupported syntax instead of guessing. See the [`five-minute onboarding`](docs/PILOT_QUICKSTART.md), [`database reference`](docs/DATABASE_REFERENCE.md), and [`installation guide`](docs/INSTALLATION.md).

From a source checkout:

```bash
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --cartridge bio --limit 10 --markdown
```

Ranking modes:

```bash
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --ranking-mode recent --markdown
PYTHONPATH=src python3 -m evidencemap.cli "endometrial organoid implantation" --ranking-mode foundational --markdown
```

### Review a claim without automatic evidence labeling

```bash
PYTHONPATH=src python3 -m evidencemap.cli \
  "endometrial organoid implantation" \
  --claim "Endometrial organoid co-culture models reproduce selected implantation-related responses." \
  --json --no-cache > candidate-map.json

# Review the returned source text and paper IDs, then create reviews.json.
PYTHONPATH=src python3 -m evidencemap.cli \
  "endometrial organoid implantation" \
  --claim "Endometrial organoid co-culture models reproduce selected implantation-related responses." \
  --reviews reviews.json --draft-statement --markdown --no-cache
```

Every row starts as `candidate`. The statement gate remains `needs_check` unless at least two distinct rows are manually marked `reviewed-support` and none is marked `reviewed-contradict`. See [`docs/CLAIM_REVIEW_WORKFLOW.md`](docs/CLAIM_REVIEW_WORKFLOW.md).

## Cartridge Architecture

The public product is one repo with domain cartridges:

```text
src/evidencemap/core/
src/evidencemap/cartridges/bio/
```

Active public-demo cartridges:

- `generic`: domain-neutral scholarly metadata (default)
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

## Research Reports

Generate a fixed preliminary research report:

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
7. Preliminary Triage Note
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

The visual brief is the preferred user-facing review artifact. It includes:

1. Executive Triage Status
2. Metadata Triage Score
3. Executive Snapshot
4. Claim and Statement Gate
5. Top Candidate Records
6. Evidence Dashboard
7. Source Coverage
8. Year Timeline
9. Quality Signals
10. Top Candidate Evidence
11. Ranked Evidence Table
12. Preliminary Triage Note
13. Evidence Gap Check
14. Action Plan
15. Delivery Package
16. QA and Limitations

The visual brief includes an `Export PDF` button for browser print/PDF delivery.

See:

```text
docs/REPORT_TEMPLATE.md
```

## Source Boundary

Public cartridges use no-auth public metadata sources only. API-key, login, paid, institutional, user-uploaded, or private SHawn ecosystem sources are private-only.

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

This tool is for research planning and literature triage. Candidate sentences are not evidence judgments. Even `reviewed-*` states record a user's review decision, not full-text quality appraisal or scientific validation. Verify wording, context, methods, and citations before clinical interpretation, grant submission, manuscript use, or public claims.

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
- [Claim review workflow](docs/CLAIM_REVIEW_WORKFLOW.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
