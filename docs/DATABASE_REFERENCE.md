# SQLite Reference Pipeline

SHawn EvidenceMap includes a reproducible SQLite reference pipeline that demonstrates how an evidence workflow can persist entities, stable identifiers, provenance, and relations without publishing non-public research records.

## Public boundary

The bundled demo is deterministic and entirely synthetic. It contains no copied article text, PDFs, unpublished findings, credentials, local paths, or operational database state. The generated SQLite file is a disposable build artifact and is not tracked by Git.

## Data model

The reference schema represents three entity kinds:

- `paper` — a scholarly record identified by normalized DOI, PMID, or demo identifier
- `dataset` — a public-data-style record identified by normalized accession or demo identifier
- `claim` — a bounded evidence statement identified by a demo identifier

Supporting tables preserve:

- multiple stable identifiers per entity
- typed relations between papers, datasets, and claims
- source and retrieval provenance
- deterministic ingest-run metadata
- schema migration history

## Safety and integrity behavior

The implementation uses Python's standard-library `sqlite3` module and enables foreign-key enforcement. Identifier normalization is deterministic:

- DOI values are lowercased and stripped of common resolver prefixes
- PMID values are stripped of an optional `PMID:` prefix
- accession values are uppercased

If identifiers in one upsert resolve to different existing entities, the operation raises an identifier-collision error instead of silently merging records. Repeated ingest, relation, provenance, and run operations are idempotent.

## Run the demo

From a source checkout:

```bash
python3 -m pip install -e '.[dev]'
python3 -m evidencemap.refdb demo --db demo.sqlite3
python3 -m evidencemap.refdb verify --db demo.sqlite3
python3 -m evidencemap.refdb export --db demo.sqlite3 --out demo.json
python3 -m evidencemap.refdb page --db demo.sqlite3 --out web/db-demo/index.html
```

Expected verification output:

```text
REFERENCE_DB_OK
```

The existing `evidencemap` literature-search CLI remains unchanged. Database commands are exposed separately through `python -m evidencemap.refdb`.

## Reproducibility contract

Two fresh demo databases must produce byte-identical canonical JSON exports. CI verifies:

1. schema migration and integrity
2. identifier normalization and collision rejection
3. idempotent upsert and relation behavior
4. provenance and ingest-run retention
5. deterministic JSON export
6. deterministic static page generation
7. wheel installation and existing CLI behavior

## What this proves—and what it does not

The reference pipeline proves the public implementation of database-backed evidence mechanics: stable identifiers, provenance, relations, integrity checks, incremental upsert, and reproducible export.

It does not claim that the generated records are research evidence, citation-ready findings, external adoption, or a copy of any non-public operational system.
