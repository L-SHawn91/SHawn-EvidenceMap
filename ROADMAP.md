# Roadmap

SHawn EvidenceMap is an early-stage public-safe evidence mapping toolkit. The roadmap focuses on maintainer hygiene and reusable public workflows rather than private project imports.

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
