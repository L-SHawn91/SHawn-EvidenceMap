# Public Boundary

SHawn EvidenceMap is a public-safe projection of an evidence workflow. It is not a publication of private SHawn research state.

## Allowed

- Public scholarly metadata
- Synthetic or toy examples
- Public report templates
- Public metadata adapter code
- Schemas and validation examples
- Generated SQLite reference databases built only from deterministic synthetic metadata or public identifier/title snapshots
- Public paper–dataset registry linkages with source URLs, when no abstract, full text, sample-level data, or scientific conclusion is copied
- Public schema migrations, identifier normalization, provenance, relation, and integrity-check code
- Mock or dry-run workflow examples

## Not allowed

- Non-public operational databases or full-text collections
- Full-text PDFs or unpublished manuscripts
- Credentials, cookies, OAuth files, tokens, or `.env` files
- Local machine paths or cloud-drive private paths
- Discord identifiers, workflow logs, memory exports, or internal project state
- Patient/sample data or non-public lab data
- Claims that require private evidence not present in this repository

## Maintainer check

Run before public commits:

```bash
python3 scripts/public_safety_scan.py .
PYTHONPATH=src python3 -m pytest -q
```
