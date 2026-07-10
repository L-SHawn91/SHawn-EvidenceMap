# Verification

This repository is verified with both local reproducible commands and active GitHub Actions Public CI.

## Maintainer gate

Run from the repository root:

```bash
PYTHONPATH=src python3 -m pytest -q
python3 scripts/public_safety_scan.py .
python3 -m compileall -q src
git diff --check
git status -sb
```

Current expected result after the v0.1.1 hardening pass:

```text
pytest: 9 passed
public_safety_scan: PUBLIC_SAFETY_OK
compileall: OK
git diff --check: OK
wheel build: OK
clean-wheel install and CLI help: OK
```

## What the safety scan checks

The public-safety scan fails on concrete secret-like assignments, private corpus/manuscript markers, and private local/cloud path patterns. It intentionally skips generated folders such as `.git`, `__pycache__`, `dist`, and `build`.

## CI status

GitHub Actions [Public CI](https://github.com/L-SHawn91/SHawn-EvidenceMap/actions/workflows/ci.yml) runs on pushes and pull requests. It verifies tests, the public-safety scan, source compilation, wheel build, CLI execution, and wheel artifact upload. Verified run: https://github.com/L-SHawn91/SHawn-EvidenceMap/actions/runs/29061091630.
