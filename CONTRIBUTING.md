# Contributing to SHawn EvidenceMap

Thanks for helping improve SHawn EvidenceMap. This repository is an early-stage public-safe evidence mapping toolkit built from public scholarly metadata, toy examples, and reusable schemas.

## What contributions fit

Good contributions include:

- Public metadata source adapters and adapter tests
- Evidence schema improvements
- Cartridge examples that use public metadata or synthetic data only
- Documentation, examples, and report templates
- Public-safety scanner improvements
- Bug fixes with small reproducible examples

## Public boundary

Do not submit:

- Credentials, tokens, cookies, or `.env` files
- Private databases, private corpora, unpublished manuscripts, or PDFs
- Local machine paths, workflow logs, memory exports, or private project state
- Patient/sample data or non-public lab data
- Clinical, legal, or investment advice claims

Use synthetic examples or public metadata links instead.

## Local checks

```bash
PYTHONPATH=src python3 -m pytest -q
python3 scripts/public_safety_scan.py .
python3 -m compileall -q src
```

## Pull requests

Keep pull requests focused and explain:

1. What changed
2. Which public-safe boundary was preserved
3. Which tests or scans were run

By contributing, you agree that your contribution is licensed under Apache-2.0.
