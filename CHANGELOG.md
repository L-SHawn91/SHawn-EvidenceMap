# Changelog

All notable public changes to this project are documented here.

## [0.2.0] - 2026-07-10

### Added
- Public GitHub Actions CI for tests, public-safety scanning, source compilation, wheel build, CLI verification, and artifact upload.
- SQLite reference schema for paper, dataset, and claim entities with normalized identifiers, typed relations, provenance, and ingest-run records.
- Idempotent DOI/PMID/accession upsert with explicit cross-entity collision rejection.
- Integrity and foreign-key checks plus canonical insertion-order-independent JSON export.
- Deterministic synthetic database build, JSON artifact, and responsive static Pages demo.
- Database CLI commands: `demo`, `verify`, `export`, and `page`.
- Public CI status badge, database verification gate, and reviewer-facing evidence links.

### Verification
- 21 tests cover the existing evidence pipeline and the SQLite migration, deduplication, relation, provenance, integrity, determinism, CLI, and HTML paths.
- CI builds two independent synthetic databases and requires byte-identical canonical exports.

### Boundaries
- The database demo contains generated synthetic metadata only.
- No article full text, unpublished research record, credential, local path, or operational database state is included.

## [0.1.1] - 2026-07-09

### Added
- Maintainer evidence and verification docs for public reviewer/readme traceability.
- Export, report, visual HTML escaping, and public-safety scanner regression tests.
- Package metadata for repository, homepage, issues, and documentation links.
- Verified release wheel and `SHA256SUMS` attached to the v0.1.1 GitHub release.
- Installation guide with clean virtual-environment verification.

### Boundaries
- CI is still tracked as a public roadmap issue until workflow-scope credentials are available.
- No external adoption or CI-passing claim is made for this release.

## [0.1.0] - 2026-07-09

### Added
- Public Apache-2.0 release posture.
- Public metadata evidence-map pipeline and GitHub Pages demo.
- Cartridge architecture for biomedical, AI/CS, policy, education, legal, and patent/technology examples.
- Public boundary, security, citation, and contribution documentation.
- Local public-safety scanner and smoke tests for maintainer hygiene.

### Boundaries
- Public metadata and synthetic/example outputs only.
- No private corpora, private PDFs, unpublished manuscripts, credentials, internal workflow state, or private project data.
