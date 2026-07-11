# Roadmap

SHawn EvidenceMap is an early-stage public-safe evidence mapping toolkit. The roadmap focuses on maintainer hygiene and reusable public workflows rather than private project imports.

## Completed in v0.2.3

- Added a reproducible, correctness-first public benchmark runner and raw JSON report.
- Added optional OpenAlex API-key support with credential-safe error messages.
- Added a dated cross-project scope snapshot without a speed leaderboard.
- Added an ethical pilot outreach strategy focused on independent runs and public failure reports rather than stars.

## Completed in v0.2.2

- Added missing-database rejection for all read-only SQLite commands.
- Added safe clickable HTTP(S) provenance links.
- Added a domain-neutral `generic` cartridge as the default for unscoped scholarly queries.
- Split onboarding into a real topic-search path and a clearly labeled fixed database fixture.

## Completed in v0.2.1

- Added a deterministic public PMID/DOI/GEO linkage demo using identifiers, titles, and source URLs only.
- Added a five-minute pilot path and structured feedback form for genuine external runs.
- Added CI and Pages verification for the public-metadata snapshot.

## Completed in v0.2.0

- Added an active GitHub Actions Public CI gate.
- Added a generated-metadata SQLite reference pipeline with schema versioning, identifier normalization, provenance, relations, integrity checks, and deterministic export.
- Added a responsive static database demo and downloadable canonical JSON.

## Near-term

- Maintain the active GitHub Actions Public CI gate and expand adapter coverage without requiring secrets.
- Prepare optional package distribution metadata without claiming external adoption.
- Add more public metadata adapter tests for PubMed, Europe PMC, OpenAlex, and Crossref.
- Expand toy examples for the `bio`, `ai_cs`, `policy`, `education`, `legal`, and `patent_tech` cartridges.
- Improve evidence-table schema examples and JSON validation.
- Add contributor-friendly docs for building a new cartridge.
- Harden public-safety scanning and false-positive documentation.

## Later

- Publish small release bundles with sample public reports.
- Add optional static report gallery generation.
- Add richer adapter health checks without storing private caches or source-locked corpora.
