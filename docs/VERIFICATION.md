# Verification

This repository is verified with both local reproducible commands and active GitHub Actions Public CI.

## Maintainer gate

Run from the repository root:

```bash
PYTHONPATH=src python3 -m pytest -q
python3 scripts/public_safety_scan.py .
python3 -m compileall -q src
PYTHONPATH=src python3 -m evidencemap.refdb demo --db build/reference-demo.sqlite3
PYTHONPATH=src python3 -m evidencemap.refdb verify --db build/reference-demo.sqlite3
git diff --check
git status -sb
```

Current expected result for v0.2.0:

```text
pytest: 21 passed
public_safety_scan: PUBLIC_SAFETY_OK
compileall: OK
reference_db: REFERENCE_DB_OK
deterministic JSON export: OK
static database page parity: OK
git diff --check: OK
wheel build: OK
clean-wheel install, CLI help, and reference DB commands: OK
```

## What the safety scan checks

The public-safety scan fails on concrete secret-like assignments, private corpus/manuscript markers, and private local/cloud path patterns. It intentionally skips generated folders such as `.git`, `__pycache__`, `dist`, and `build`.

## CI status

GitHub Actions [Public CI](https://github.com/L-SHawn91/SHawn-EvidenceMap/actions/workflows/ci.yml) runs on pushes and pull requests. It verifies tests, the public-safety scan, source compilation, wheel build, existing CLI execution, SQLite integrity, canonical export determinism, generated-page parity, and both wheel and synthetic-reference artifacts.
