# Verification

This repository is verified with local, reproducible commands until GitHub Actions CI is enabled.
CI enablement is tracked publicly in issue #7.

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
```

## What the safety scan checks

The public-safety scan fails on concrete secret-like assignments, private corpus/manuscript markers, and private local/cloud path patterns. It intentionally skips generated folders such as `.git`, `__pycache__`, `dist`, and `build`.

## CI status

GitHub Actions CI is not claimed as active until a workflow-scope credential is used to add the workflow file. Until then, all public claims should say "local verification passes", not "CI passing".
