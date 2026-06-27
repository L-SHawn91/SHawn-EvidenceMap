# Public Release Checklist

Run before any public push or deployment.

## Visibility

- [ ] README contains `PUBLIC_STATUS: public-demo`
- [ ] No private repo history was copied
- [ ] No non-public SHawn project material is present

## Secret and Path Scan

- [ ] No `.env` or `.env.local`
- [ ] No API keys or auth JSON
- [ ] No private local paths
- [ ] No private storage, note-vault, PDF-library, or corpus references

Suggested scan:

```bash
bash scripts/public_safety_scan.sh
```

## Product Safety

- [ ] Output says manual verification is required
- [ ] No clinical advice claims
- [ ] All data sources are public
- [ ] Demo examples use public or synthetic data
