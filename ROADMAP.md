# Roadmap

SHawn EvidenceMap is an early-stage public-safe evidence mapping toolkit. The roadmap focuses on maintainer hygiene and reusable public workflows rather than private project imports.

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
