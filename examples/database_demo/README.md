# Synthetic database demo

This example is generated locally by the SQLite reference pipeline. It uses deterministic synthetic metadata to demonstrate:

- paper, dataset, and claim entities
- stable identifier normalization
- typed evidence relations
- source provenance
- idempotent ingest-run recording
- integrity verification
- canonical JSON and static HTML export

Run:

```bash
python3 -m evidencemap.refdb demo --db demo.sqlite3
python3 -m evidencemap.refdb verify --db demo.sqlite3
python3 -m evidencemap.refdb export --db demo.sqlite3 --out demo.json
python3 -m evidencemap.refdb page --db demo.sqlite3 --out web/db-demo/index.html
```

The generated `.sqlite3` file is disposable and ignored by Git. No article full text, non-public research record, or operational database is included.
