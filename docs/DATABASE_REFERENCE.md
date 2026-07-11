# Verifiable Metadata Bridge Reference

SHawn EvidenceMap includes a local-first **Verifiable Metadata Bridge**. It imports public scholarly identifiers or conservative bibliographic interchange records, records each ingest decision, and exports SQLite/JSON plus deterministic CSV/RIS/BibTeX handoffs without publishing non-public research records.

`Verifiable` means local integrity and auditability. Importing a DOI, PMID, OpenAlex work ID, or accession does not prove that the identifier exists and does not perform external registry resolution.

## Public boundary

Two bundled demonstrations are available:

- the synthetic demo contains generated records only;
- the public-metadata demo contains public identifiers, titles, one official NCBI paper–dataset registry linkage, and source URLs only.

Neither demo contains abstracts, copied article text, PDFs, sample-level values, unpublished findings, credentials, local paths, or operational database state. Generated SQLite files are disposable build/release artifacts and are not tracked by Git.

## Data model

The reference schema represents three entity kinds:

- `paper` — a scholarly record identified by normalized DOI, PMID, or demo identifier
- `dataset` — a public-data-style record identified by normalized accession or demo identifier
- `claim` — a bounded evidence statement identified by a demo identifier

Supporting tables preserve:

- multiple stable identifiers per entity
- typed relations between papers, datasets, and claims
- source and retrieval provenance
- ingest-run summaries and per-record `inserted`, `merged`, or `rejected` events
- schema migration history

## Safety and integrity behavior

The implementation uses Python's standard-library `sqlite3` module and enables foreign-key enforcement. Identifier normalization is deterministic:

- DOI values are lowercased, stripped of common resolver prefixes, and minimally syntax-validated
- PMID values are stripped of an optional `PMID:` prefix and must contain digits only
- OpenAlex work IDs are normalized to uppercase `W` plus digits
- accession values are uppercased

If identifiers in one upsert resolve to different existing entities, the operation raises an identifier-collision error instead of silently merging records. Repeated ingest, relation, provenance, and run operations are idempotent.

## Import and handoff formats

| Format | Import boundary | Export behavior |
|---|---|---|
| `identifiers` | one DOI, PMID, OpenAlex work ID, or explicitly prefixed `accession:` per line | not applicable |
| `csv` | fixed header fields: `title,doi,pmid,openalex_id,accession,year,journal,authors,url` | UTF-8, fixed columns, `\n` line endings |
| `ris` | `TY`…`ER` records; common title, author, year, journal, DOI, accession/ID, and URL tags; continuation lines unsupported | deterministic common-tag subset |
| `bibtex` | `@article`, `@misc`, and `@dataset`; no macros, concatenation, `crossref`, or unsupported entry types | deterministic citation keys from primary identifiers |
| `json` | not an interchange input in v0.2.4 | audit-inclusive canonical database snapshot |

Unknown or malformed syntax is rejected instead of guessed. CSV/RIS/BibTeX exports contain entity metadata only, so audit timestamps do not change their bytes. JSON intentionally includes provenance, ingest runs, and ingest events.

```bash
python3 -m evidencemap.refdb ingest --db bridge.sqlite3 --input identifiers.txt --format identifiers
python3 -m evidencemap.refdb ingest --db bridge.sqlite3 --input records.csv --format csv
python3 -m evidencemap.refdb verify --db bridge.sqlite3
python3 -m evidencemap.refdb export --db bridge.sqlite3 --out records.json --format json
python3 -m evidencemap.refdb export --db bridge.sqlite3 --out records.csv --format csv
python3 -m evidencemap.refdb export --db bridge.sqlite3 --out records.ris --format ris
python3 -m evidencemap.refdb export --db bridge.sqlite3 --out records.bib --format bibtex
```

A syntactically broken input file fails before the database is opened. A parsed record that collides across existing entities is recorded as `rejected`; accepted records remain available, and the CLI exits nonzero when any record was rejected.

## Run the demo

From a source checkout:

```bash
python3 -m pip install -e '.[dev]'
python3 -m evidencemap.refdb demo --db demo.sqlite3
python3 -m evidencemap.refdb public-demo --db public-metadata.sqlite3
python3 -m evidencemap.refdb verify --db public-metadata.sqlite3
python3 -m evidencemap.refdb export --db public-metadata.sqlite3 --out reference.json
python3 -m evidencemap.refdb page --db public-metadata.sqlite3 --out index.html
```

The complete external-user path is documented in [`PILOT_QUICKSTART.md`](PILOT_QUICKSTART.md).

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
4. provenance, ingest-run, and per-record decision retention
5. deterministic demo JSON plus deterministic entity-only CSV/RIS/BibTeX export
6. deterministic static page generation
7. wheel installation and existing CLI behavior

## What this proves—and what it does not

The bridge proves the public implementation of database-backed evidence mechanics: stable identifiers, provenance, per-record ingest decisions, relations, integrity checks, incremental upsert, and reproducible handoff export.

It does not claim that the synthetic records are research evidence, that a registry linkage independently validates a scientific conclusion, that the outputs are citation-ready findings, that external adoption exists, or that the examples copy a non-public operational system.
