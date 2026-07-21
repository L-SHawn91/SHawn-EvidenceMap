# Changelog

All notable public changes to this project are documented here.

## [Unreleased]

### Added
- Search-topic/claim separation with `--claim`, manual `--reviews` relation files, and a fail-closed `--draft-statement` gate.
- Candidate sentence traceability through source section, 1-based sentence index, DOI, PMID, source name, and source URL.
- Runtime `evidencemap.__version__` synchronized with package version `0.3.0`.
- A public claim-review guide and review-file example.
- A reproducible 60-second metadata bridge demo generated from tracked public/synthetic input and the real ingest, verify, and export path.
- A mobile-first Metadata Audit Pilot page with downloadable audit JSON, CSV, RIS, and BibTeX artifacts.
- Regression tests for the advertised `3 inserted / 2 merged / 1 rejected` decision summary and public intake boundary.

### Changed
- Automatically selected text is now presented as a candidate source sentence rather than a support sentence; no automatic evidence relation is implied.
- Fixed Markdown and visual reports use triage/coverage language instead of verdict/confidence wording.
- Legacy cached `support_sentence` payloads are migrated on read, while new JSON exports use only `candidate_source_sentence`.
- Public pilot intake now routes through GitHub Discussion #9 and the structured feedback issue instead of a personal email address.
- The landing page now leads with the Verifiable Metadata Bridge role and removes unsupported private-workspace promises.
- The launch path now uses a free, bounded early-validation cohort; premature public pricing and service-oriented language were removed until independent use and repeat demand exist.

### Security
- Public-safety scanning now rejects personal Gmail contact addresses from tracked public surfaces.
- Future repository commits use the account's GitHub noreply address; published history is not rewritten.

## [0.2.4] - 2026-07-12

### Added
- User-supplied DOI, PMID, OpenAlex work ID, and explicit public-accession ingestion.
- CSV, conservative RIS, and conservative BibTeX input plus deterministic entity-only handoff exports, including stable roundtrips for nested braces and literal `#` values.
- Schema v2 `ingest_events` records for inserted, merged, and rejected inputs with source provenance, atomic whole-run rollback on unexpected failures, and run/event consistency verification.
- A tested step migration that preserves existing schema-v1 entities and identifiers.
- A dated ecosystem comparison covering a 290-tool discovery census, 116 adjacent names, a same-turn 43-repository public snapshot, 13 service/freeware alternatives, and five clean-environment CLI onboarding smokes.
- Regression tests for snapshot scope, canonical repository identities, public-safe fields, onboarding-smoke boundaries, and report consistency.

### Changed
- The public product descriptor is **SHawn EvidenceMap — Verifiable Metadata Bridge**. `Verifiable` refers to local integrity and auditability, not external identifier resolution.
- The project is positioned as a verifiable, deterministic scholarly-metadata snapshot and standards-based handoff layer rather than a complete screening, full-text synthesis, meta-analysis, or knowledge-map application.
- The near-term roadmap now prioritizes user-supplied identifiers, RIS/BibTeX/CSV interchange, and auditable resolution/deduplication before project diff and interactive-map features.
- The public benchmark now uses the canonical Citation.js repository snapshot.
- The ecosystem snapshot now includes AgentSLR, OpenScholar, Robin, and EPPI-Reviewer's source-available repository; the report distinguishes public code, OSI-licensed OSS, source-available software, and paid-API dependencies.

## [0.2.3] - 2026-07-11

### Added
- A correctness-first public benchmark runner with raw JSON, output hashes, repeated timing, sampled peak RSS, and explicit no-leaderboard boundaries.
- A dated public benchmark report and ethical 14/30/60-day pilot outreach strategy.
- Optional `OPENALEX_API_KEY` environment support for repeated OpenAlex-backed searches.

### Security
- OpenAlex HTTP and network errors no longer include credential-bearing request URLs.
- Tests verify that environment credentials are omitted from raised error messages and benchmark output records only key presence, never the value.

### Verification
- The v0.2.3 candidate wheel passed five network smoke repetitions and ten local repetitions for DB creation, verification, and missing-path rejection.
- The PyAlex overlap lane is correctness-only; cross-tool timing is explicitly informational and not a speed ranking.

## [0.2.2] - 2026-07-11

### Fixed
- Read-only database commands now reject missing paths without creating or approving empty SQLite files.
- Public provenance URLs render as safe, clickable HTTP(S) links; non-HTTP schemes remain escaped text.
- Unscoped scholarly queries now use a domain-neutral `generic` cartridge instead of biomedical labels.
- The build requirement now matches the setuptools version needed for SPDX license expressions in clean wheel builds.

### Improved
- The onboarding guide separates real topic search from the fixed offline database fixture.
- Documentation states that custom DOI/PMID/GEO replacement is not supported by the v0.2.2 database pilot.
- Negative-path expectations are documented for pilot verification.

### Verification
- Clean-wheel blind testing covers valid setup, offline rerun, missing-database rejection, public links, and generic query labels.

## [0.2.1] - 2026-07-10

### Added
- Deterministic offline public-metadata demo linking PMID `32416070`, DOI `10.1016/j.cell.2020.04.026`, and GEO accession `GSE147507` through official registry metadata.
- `public-demo` SQLite CLI command, canonical JSON, and responsive static Pages view.
- Five-minute pilot quickstart and structured issue form for genuine external run feedback.
- CI verification for public-metadata DB integrity, deterministic export, and tracked JSON/HTML parity.

### Verification
- Public identifiers, titles, linkage, and source URLs were read back from NCBI PubMed and GEO metadata.
- The example contains no abstract, full text, PDF, sample-level values, patient information, or private research record.

### Boundaries
- The registry linkage is a metadata assertion only and does not independently validate a scientific conclusion.
- Self-runs, CI runs, and requested stars are not claimed as external adoption.
- PyPI publication is not claimed; the verified GitHub release wheel remains the installation path.

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
