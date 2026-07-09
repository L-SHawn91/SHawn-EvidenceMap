# Maintainer Evidence

This document summarizes public, verifiable maintenance evidence for SHawn EvidenceMap.
It is vendor-neutral and describes the repository's public release and maintenance posture.

## Representative repository

- Repository: https://github.com/L-SHawn91/SHawn-EvidenceMap
- License: Apache-2.0 (`LICENSE` + `NOTICE`)
- Homepage/demo: https://l-shawn91.github.io/SHawn-EvidenceMap/
- Release: `v0.1.1` — maintainer evidence and verification hardening, after the `v0.1.0` public-safe evidence map release
- Scope: public-safe evidence mapping for scholarly metadata and research-agent workflows

## Maintenance signals

Public maintenance infrastructure is present in the repository:

- `README.md` with the public stack table and demo link
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `docs/VERIFICATION.md`
- Issue templates and pull-request template
- Public roadmap issues for adapters, schema, public-boundary policy, report gallery, and CI
- A merged pull request demonstrating the branch → PR → merge workflow

## Reproducible local verification

Run from the repository root:

```bash
PYTHONPATH=src python3 -m pytest -q
python3 scripts/public_safety_scan.py .
python3 -m compileall -q src
git status -sb
```

Current verified state:

- `pytest`: 9 passed
- `public_safety_scan`: `PUBLIC_SAFETY_OK`
- `compileall`: OK
- working tree: clean at verification

GitHub Actions CI is planned publicly in issue #7. Until it is enabled, do not describe the project as having passing CI; describe the local verification commands above instead.

## Public-safe boundary

The public boundary is documented in `docs/PUBLIC_BOUNDARY.md` and checked with `scripts/public_safety_scan.py`.

Allowed:

- Public scholarly metadata
- Synthetic or toy examples
- Public report templates
- Public metadata adapter code
- Schemas and validation examples
- Mock or dry-run workflow examples

Not allowed:

- Private databases or private corpora
- Full-text PDFs or unpublished manuscripts
- Credentials, cookies, OAuth files, tokens, or `.env` files
- Local machine paths or cloud-drive private paths
- Discord identifiers, workflow logs, memory exports, or internal project state
- Patient/sample data or non-public lab data
- Claims that require private evidence not present in this repository

## Supporting public stack

Related public-safe Apache-2.0 repositories maintained as supporting layers:

| Layer | Repository | Role |
|---|---|---|
| Search | `shawn-bio-search-lite` | Public scholarly metadata adapters |
| Map | `paper-map-lite` | Toy claim/evidence graph schemas |
| Coordinate | `shawn-sync-lite` | Public-safe manifests and boundary templates |
| Execute safely | `newbrain-router` | Dry-run routing and approval-gate examples |
| QA documents | `shawn-docx-qa` / `SHawn-hwp` | Public document QA utilities |

`SHawn-WEB` is a mixed-license public hub and demo surface in a supporting role.

## Maintainer workflow

The intended maintenance loop is:

```text
roadmap issue → branch → pull request → local tests + public-safety scan → merge → changelog/release note → tagged release
```

Current stage: early public release. No external adoption is claimed; this document records maintenance discipline, public-boundary hygiene, and verifiable release practice.
