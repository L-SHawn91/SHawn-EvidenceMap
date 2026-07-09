## Summary


## Public boundary check

- [ ] No credentials, tokens, cookies, or `.env` files
- [ ] No private corpora, PDFs, manuscripts, local paths, workflow logs, or project state
- [ ] Examples use public metadata or synthetic/toy data only

## Verification

- [ ] `PYTHONPATH=src python3 -m pytest -q`
- [ ] `python3 scripts/public_safety_scan.py .`
- [ ] `python3 -m compileall -q src`
