# Ecosystem comparison and product-gap review — 2026-07-11

## Executive verdict

SHawn EvidenceMap does **not** have a demonstrated runtime-performance problem at its current pilot scale. Its larger problem is category fit.

The current product is strongest as a **lightweight, verifiable scholarly-metadata snapshot and handoff layer**. The name and tagline can instead lead a visitor to expect one or more of the following:

- a systematic-review workspace;
- AI-assisted screening;
- a citation or knowledge graph;
- an interactive evidence map;
- full-text extraction or scientific question answering.

Those expectations are already served by mature open-source projects and established web products. SHawn should not attempt to duplicate all of them. Its defensible route is to make public scholarly metadata **portable, deterministic, inspectable, updateable, and easy to hand off** to those tools.

The highest-value product work is therefore:

1. accept user-supplied identifiers and standard bibliographic files;
2. export RIS, BibTeX, and CSV in addition to the current artifacts;
3. add a project manifest plus snapshot/update/diff workflow;
4. retain source-query and deduplication decisions as an audit trail;
5. build citation relations and a small static interactive map only after the data handoff path works;
6. obtain independent run evidence instead of adding unrelated features.

## Scope and method

This review separates projects by role. Different roles are not placed in one runtime leaderboard.

### Discovery breadth

- The community-maintained [Evidence Synthesis Tools directory](https://evidencesynthesis-tools.github.io/) described **290** open-source tools in early 2026.
- A disclosed keyword filter over each tool name and first description block retained **116** search, screening, metadata, reference-management, mapping, or workflow-adjacent names. The terms and all retained names are preserved in the raw JSON.
- From those results and exact-name searches, this review verified a purposeful strategic core of **39 public GitHub repositories** with a same-turn GitHub GraphQL snapshot. This is not a ranked or exhaustive 39-of-116 sample: it retains direct workflow/screening alternatives, metadata/citation components, mapping/bibliometric alternatives, handoff targets, and recent AI/full-text entrants that materially affect positioning.
- It separately reviewed **13 service or freeware alternatives** from their official product pages.
- Five installable projects were tested in clean Python 3.11 virtual environments for installability and top-level CLI discoverability only.

The raw repository and onboarding snapshot is stored in [`benchmarks/results/2026-07-11-ecosystem-snapshot.json`](../benchmarks/results/2026-07-11-ecosystem-snapshot.json).

### Evidence rules

- Official repositories, documentation, product pages, and package registries were preferred.
- GitHub stars, forks, releases, and dates are public activity or attention signals, not user counts or scientific-quality measures.
- Vendor-reported user counts remain vendor claims and are not merged with repository metrics.
- A missing SPDX value in GitHub metadata is reported as unresolved, not interpreted as closed source.
- The 290-tool directory is a discovery source, not final authority for license or maintenance status.
- Install time and environment size are informational. The packages perform different work and are not speed-ranked.
- SHawn's functional claims were executed in this repository. Unless a row explicitly says otherwise, other-project capability cells are conservative readings of official documentation and were not functionally exercised.

## Market map

### 1. Direct review-workflow and screening alternatives

| Project | Main role | What it already does that SHawn does not | Relationship to SHawn |
|---|---|---|---|
| [ASReview](https://github.com/asreview/asreview) | Active-learning screening | Interactive screening, simulation, server/crowd workflows, a substantial user community | Strong direct substitute if the user's goal is screening; future export target |
| [CoLRev](https://github.com/CoLRev-Environment/colrev) | Git-based collaborative review environment | Whole-review workflow, data-quality model, validate/undo, extensibility, collaboration | Closest open workflow platform; integration target rather than a speed comparator |
| [MetaScreener](https://github.com/ChaokunHong/MetaScreener) | Multi-LLM title/abstract and full-text screening | PICO-style criteria, uncertainty routing, extraction, risk-of-bias commands, UI/server | Important new threat in AI screening; outside SHawn's current public-safe metadata niche |
| [Colandr](https://github.com/datakind/permanent-colandr-back) | ML-assisted review web application | Deduplication, screening, extraction, multi-user web workflow | Broader hosted workflow; potential interchange target |
| [Abstrackr](https://github.com/bwallace/abstrackr-web) | ML-assisted citation screening | Collaborative decisions and prioritization | Screening substitute, not metadata-artifact competitor |
| [revtools](https://github.com/mjwestgate/revtools) | R research-synthesis tools | Visual/topic-assisted screening | R-side handoff target |
| [metagear](https://cran.r-project.org/package=metagear) | R review and meta-analysis utilities | Deduplication, PDF handling, interactive screening | R-side complement; GitHub source reviewed through a CRAN mirror |
| [ReviewAid](https://github.com/aurumz-rgb/ReviewAid) | AI full-text screening and extraction | Full-text screening and structured extraction | Emerging AI substitute for downstream work |
| [HAWC](https://github.com/shapiromatron/hawc) | Systematic-review content management | Structured assessment workspace and collaboration | Domain workflow complement |
| [Systematic Review Accelerator 2](https://github.com/IEBH/SRA2) | Review automation suite | Multiple task-specific accelerators | Collection of complements, especially search translation |

**Implication:** SHawn should not build a second ASReview, CoLRev, or MetaScreener. It should produce clean, auditable inputs for them.

### 2. Search, metadata, deduplication, and citation components

| Project | Main role | Lesson for SHawn |
|---|---|---|
| [PyAlex](https://github.com/J535D165/pyalex) | Python interface to OpenAlex | Keep SHawn's value above the API-wrapper layer: normalization, provenance, deterministic artifacts, and workflow handoff |
| [habanero](https://github.com/sckott/habanero) | Python client for Crossref | Do not compete as another generic API wrapper |
| [paperscraper](https://github.com/jannisborn/paperscraper) | Multi-source publication metadata retrieval | Multi-source breadth and usable data frames are expected features |
| [pybliometrics](https://github.com/pybliometrics-dev/pybliometrics) | Scopus API wrapper | Proprietary-source connectors may remain optional and user-credentialed |
| [Citation.js](https://github.com/citation-js/citation-js) | Citation-format conversion | Standard bibliographic interchange is a solved problem and should be supported |
| [synthesisr](https://github.com/mjwestgate/synthesisr) | Bibliographic import and deduplication | RIS/BibTeX import and transparent duplicate handling are table stakes for evidence synthesis |
| [ASySD](https://github.com/camaradesuk/ASySD) | Search-result deduplication | Deduplication quality requires evaluation, not only deterministic execution |
| [OpenRefine](https://github.com/OpenRefine/OpenRefine) | Inspectable data cleaning and reconciliation | A useful general baseline for reviewable normalization; SHawn must explain its domain-specific provenance and deterministic handoff value |
| [CitationChaser](https://github.com/nealhaddaway/citationchaser) | Forward/backward citation chasing | Seed-to-neighborhood expansion is a natural next relation feature |
| [Paperfetcher](https://github.com/paperfetcher/paperfetcher) | Citation searching and RIS export | A one-click citation chase plus RIS handoff is a useful minimal workflow |
| [SRA Polyglot](https://github.com/IEBH/sra-polyglot) | Search-strategy translation | Search-string translation is specialist work; integrate or link rather than recreate |
| [OpenCitations Meta](https://github.com/opencitations/oc_meta) | Open citation metadata infrastructure | OpenCitations can complement OpenAlex relations and provenance |

### 3. Mapping and bibliometric-analysis alternatives

| Project | Main role | Gap exposed in SHawn |
|---|---|---|
| [Open Knowledge Maps / Headstart](https://github.com/OpenKnowledgeMaps/Headstart) | Web-based knowledge maps from scholarly search | It produces the visual map that the term “EvidenceMap” may lead users to expect |
| [bibliometrix / Biblioshiny](https://github.com/massimoaria/bibliometrix) | Comprehensive bibliometric and science mapping | SHawn has no co-citation, co-authorship, co-word, thematic, or historiographic analysis |
| [EviAtlas](https://github.com/ESHackathon/eviatlas) | Systematic-map visualization | Evidence-map users expect filtering and visual distribution of evidence |
| [LitStudy](https://github.com/NLeSC/litstudy) | Notebook-based literature analysis | Python users may expect analysis-ready tables and notebooks |
| [ScientoPy](https://github.com/jpruiz84/ScientoPy) | Python scientometric analysis | Trend and topic analysis are established adjacent capabilities |
| [citracer](https://github.com/marcpinet/citracer) | Citation-chain tracing and interactive graph | A small recent project can still present a clearer visual-graph proposition than SHawn |
| [PRISMA2020](https://github.com/prisma-flowdiagram/PRISMA2020) | Reproducible review flow diagrams | Standard reporting outputs matter more than another proprietary-looking report format |

### 4. Reference management and local research libraries

| Project | Main role | Relationship |
|---|---|---|
| [Zotero](https://github.com/zotero/zotero) | Collect, organize, annotate, cite, and share sources | Essential export/import target; not a realistic direct competitor |
| [JabRef](https://github.com/JabRef/jabref) | BibTeX/BibLaTeX library management | Confirms BibTeX as required interchange for a research CLI |
| [Open Paper](https://github.com/khoj-ai/openpaper) | Paper library, reading, notes, annotations, AI assistant | Shows the value of a user-owned corpus and integrated reading surface |
| [Better BibTeX for Zotero](https://github.com/retorquere/zotero-better-bibtex) | Stable citation keys and automated BibTeX/BibLaTeX export | A more precise interoperability surface than treating the Zotero desktop application as one monolith |
| [Zotero translation-server](https://github.com/zotero/translation-server) | Server-side metadata translation | Potential standards-based service boundary for future handoffs |

### 5. Full-text and agentic research alternatives

| Project | Main role | Product lesson |
|---|---|---|
| [PaperQA2](https://github.com/Future-House/paper-qa) | Citation-grounded RAG over user documents | Full-text QA is a mature, dependency-heavy separate product category |
| [LatteReview](https://github.com/PouriaRouzrokh/LatteReview) | Agentic review automation | Agentic orchestration is moving quickly but does not replace metadata provenance |
| [LitLLMs](https://github.com/LitLLM/litllms-for-literature-review-tmlr) | Evaluation of LLMs for literature review | Evaluation evidence should precede broad AI claims |
| [DenseReviewer](https://github.com/ielab/densereviewer) | Dense-retrieval screening prioritization | Relevance ranking needs recall-oriented evaluation if SHawn claims review utility |
| [ProfOlaf](https://github.com/sr-lab/ProfOlaf) | Citation snowballing | Citation expansion is a focused feature with clearer user value than generic AI prose |

**Implication:** full-text RAG, AI screening, and autonomous synthesis should remain integrations or later optional layers. Adding an LLM now would increase cost and risk without fixing the handoff gap.

## Service and freeware substitutes

These products are kept separate because repository metrics are not comparable. “Source not established” means this review did not find an official full-product public repository plus an OSI license; it is not a legal conclusion.

| Product | Officially described role | Source/product boundary observed |
|---|---|---|
| [Rayyan](https://www.rayyan.ai/) | Search, deduplication, screening, collaboration, extraction, PICO, risk of bias, and API access | Freemium web product; full-product OSS source not established |
| [Elicit](https://elicit.com/) | Semantic search, research reports, screening, and data extraction | Hosted AI product; full-product OSS source not established |
| [Covidence](https://www.covidence.org/) | End-to-end systematic-review management and collaboration | Commercial hosted product |
| [DistillerSR](https://www.distillersr.com/) | Configurable, auditable literature-evidence management | Commercial enterprise platform |
| [Nested Knowledge](https://about.nested-knowledge.com/) | Living SLR, screening, extraction, meta-analysis, and interactive synthesis | Hosted commercial platform |
| [EPPI-Reviewer](https://eppi.ioe.ac.uk/cms/er4/) | Review management, searching, screening, extraction, mapping, and synthesis | Hosted product with current 2026 release history; full-product OSS source not established |
| [CADIMA](https://www.cadima.info/) | Free team-based systematic review and map workflow | Free web tool; full-product OSI source not established |
| [ResearchRabbit](https://www.researchrabbit.ai/) | Paper discovery, collections, citation exploration, and visual context | Hosted discovery product; full-product OSS source not established |
| [Connected Papers](https://www.connectedpapers.com/) | Seed-paper similarity graph and prior/derivative works | Hosted visual-discovery product |
| [Litmaps](https://www.litmaps.com/) | Discover, visualize, share, and monitor literature | Hosted product with free/paid plans |
| [Scite](https://scite.ai/) | Full-text search, citation context, supporting/contrasting classifications, API/MCP | Commercial hosted data and AI product |
| [VOSviewer](https://www.vosviewer.com/) | Free desktop and web bibliometric-network visualization | Freeware; official full-product OSS source not established in this review |
| [Semantic Scholar](https://www.semanticscholar.org/) | Scholarly discovery and metadata/API infrastructure | Free service and API, not a complete review-workflow OSS substitute |

## Dated public repository snapshot

Selected strategic rows from the 39-repository raw snapshot:

| Project | Stars | Forks | Latest release | Last push | License field | Interpretation |
|---|---:|---:|---|---|---|---|
| SHawn EvidenceMap | 0 | 0 | v0.2.3 (2026-07-11) | 2026-07-11 | Apache-2.0 | Active engineering; no independent adoption signal |
| ASReview | 943 | 174 | v3.0.8 (2026-06-18) | 2026-06-29 | Apache-2.0 | Mature direct screening benchmark |
| MetaScreener | 1,319 | 47 | fp-audit-protocol-v1.0 (2026-05-08) | 2026-06-11 | Apache-2.0 | Rapidly visible new AI-screening entrant |
| PaperQA2 | 8,849 | 888 | v2026.03.18 | 2026-06-29 | Apache-2.0 | Large adjacent full-text/QA project |
| bibliometrix | 643 | 171 | v5.4.1 (2026-06-16) | 2026-06-27 | unresolved | Established science-mapping alternative |
| PyAlex | 396 | 50 | v0.21 (2026-02-23) | 2026-07-06 | MIT | Established OpenAlex client layer |
| Open Knowledge Maps / Headstart | 215 | 45 | v7 (2021-11-25) | 2026-07-10 | MIT | Active code despite old formal release |
| CoLRev | 43 | 54 | 0.16.2 (2026-02-24) | 2026-07-10 | MIT | Small but collaborative and workflow-complete |
| CitationChaser | 151 | 14 | 0.0.4 (2022-01-24) | 2025-03-21 | unresolved | Focused citation-chasing utility |
| Colandr backend | 20 | 1 | v1.1.0 (2026-04-09) | 2026-06-15 | MIT | Small repository footprint, broader hosted workflow |
| synthesisr | 35 | 15 | v0.4.0 (2026-03-26) | 2026-03-26 | unresolved | Direct bibliographic import/dedup reference |
| ReviewAid | 9 | 6 | v2.3.0 (2026-04-18) | 2026-07-08 | Apache-2.0 | New, active full-text screening/extraction project |
| HAWC | 28 | 17 | v2026.1 (2026-04-21) | 2026-07-04 | unresolved | Active structured review workspace |
| citracer | 23 | 0 | v1.7.0 (2026-04-13) | 2026-04-13 | MIT | New focused citation-graph project |
| Open Paper | 376 | 58 | none in GitHub | 2026-07-10 | AGPL-3.0 | Active user-owned paper-library surface |

No row establishes scientific validity or actual active-user count. SHawn's zero stars/forks and absence of documented downstream use remain a real external-evidence gap.

## Fresh-environment onboarding smoke

All five exact versions installed and exposed a working top-level help command in separate Python 3.11 virtual environments.

| Package | Exact source/version | CLI | Install | Top-level help | Declared requirement entries | Venv size |
|---|---|---|---|---|---:|---:|
| SHawn EvidenceMap | public release wheel 0.2.3 | `evidencemap` | PASS | PASS | 1 | 86,274 KB |
| ASReview | PyPI 3.0.8 | `asreview` | PASS | PASS | 40 | 507,472 KB |
| CoLRev | PyPI 0.16.2 | `colrev` | PASS | PASS | 48 | 641,326 KB |
| MetaScreener | PyPI 2.0.0a4 | `metascreener` | PASS | PASS | 33 | 1,028,415 KB |
| PaperQA2 | PyPI 2026.3.18 | `pqa` | PASS | PASS | 60 | 364,877 KB |

This supports one narrow finding: SHawn has a small, easy-to-discover distributable. It does **not** show that SHawn is faster or better; dependency and environment-size differences primarily reflect different and often much broader functionality. Network-dependent installation timing is retained only in the raw JSON. This onboarding lane used Python 3.11; the separate public benchmark used Python 3.10.12, so the lanes are not cross-timed.

## Capability comparison

Legend: **Yes** = documented core capability; **Partial** = available only for a narrower path; **No** = not a current product capability.

Except for SHawn's executed repository tests and the five top-level install/help smokes, other-project cells below are official-documentation assessments, not functional verification.

| Capability | SHawn | ASReview | CoLRev | MetaScreener | Open Knowledge Maps | bibliometrix | PaperQA2 |
|---|---|---|---|---|---|---|---|
| Search a public topic directly | Yes | No; import-first | Partial; source operations | No; upload/import-first | Yes | Partial; import/API | No; user corpus-first |
| User-supplied corpus/identifiers | **Partial: query only; DB is fixture-only** | Yes | Yes | Yes | Seed/query driven | Yes | Yes |
| Standard RIS/BibTeX/CSV interchange | **No complete handoff path** | Yes | Yes | Export supported | Not its primary role | Yes | Corpus/files |
| Deterministic SQLite/JSON artifact | **Yes** | Project-specific | Git/data workflow | Audit records | No equivalent claim | Analysis objects/exports | Index/caches |
| Integrity verification and negative-path guard | **Yes, narrow reference DB** | Workflow validation differs | Validate/undo | Audit/calibration differs | No equivalent claim | No equivalent claim | No equivalent claim |
| Interactive screening | No | **Yes** | Yes | **Yes** | No | No | No |
| Collaboration | No | Server/crowd options | **Git-based** | UI/server path | Shared web map | Shiny/app workflows | No review-team workflow |
| Full-text extraction/QA | No | No | Integrations vary | **Yes** | No | No | **Yes** |
| Citation/bibliometric graph | No | No | Not primary | No | **Yes** | **Yes** | No |
| Interactive visual evidence map | Static report only | Screening UI | Workflow UI | Screening UI | **Yes** | **Yes** | No |
| Domain-specific public-source cartridges | **Yes** | Model/extensions | Endpoints/plugins | Criteria/models | Data-source configs | Analysis methods | Settings/tools |
| Independent public adoption evidence | **None documented** | Strong public signals | Multiple contributors/signals | Early but substantial attention | Institutional platform evidence | Established use/signals | Strong repository attention |

## SHawn scorecard

| Dimension | Assessment | Evidence |
|---|---|---|
| Distributable and first CLI discovery | Strong for an early project | Public wheel, clean install, working help, small environment |
| Deterministic public artifact generation | Strong and unusual | SQLite schema/migrations, normalization, provenance, relations, integrity check, deterministic JSON/HTML |
| Metadata-source coverage | Moderate | PubMed, Europe PMC, OpenAlex, Crossref; no completeness evaluation |
| Public safety | Strong for the demonstrated scope | Metadata/toy-data boundary, credential-safe OpenAlex path, negative-path tests |
| User-controlled ingestion | Weak | Topic query works, but the reference DB remains fixture-only |
| Interoperability | Weak | No complete RIS/BibTeX/CSV import-export handoff |
| Actual “map” capability | Weak | Theme rows and static HTML are not a citation/knowledge/evidence map in the established sense |
| Search and deduplication quality evidence | Weak | Correctness smoke exists; recall, precision, coverage, and duplicate-resolution accuracy are untested |
| Screening, extraction, collaboration | Absent by design | Mature alternatives already cover these jobs |
| Independent adoption | Absent | No verified external run, downstream use, external correction, or contribution at snapshot date |

## Product decision: build, integrate, or avoid

| Decision | Capability | Reason |
|---|---|---|
| **Build now** | Identifier and RIS/BibTeX/CSV ingestion | Converts the fixture into a real user workflow |
| **Build now** | RIS, BibTeX, CSV, JSON, and SQLite export from one canonical model | Makes SHawn a neutral handoff layer |
| **Build now** | `project manifest → snapshot → update → diff` | Differentiates SHawn through reproducible change tracking |
| **Build now** | Source-query, result-count, deduplication, and exclusion audit | Turns “public metadata” into reviewable provenance |
| **Build next** | OpenAlex/OpenCitations citation relations and static interactive HTML | Makes the “map” claim more literal after core ingestion works |
| **Integrate** | ASReview / MetaScreener screening | Do not duplicate mature screening systems |
| **Integrate** | CoLRev workflow | Export a compatible project or documented handoff |
| **Integrate** | Zotero / JabRef / bibliometrix | Use standard formats and examples |
| **Integrate or link** | SRA Polyglot / litsearchr | Search-strategy design is specialist functionality |
| **Avoid for now** | Hosted collaborative review UI | High maintenance, already crowded, and not required for the public-safe artifact niche |
| **Avoid for now** | General full-text RAG or chat | PaperQA2, Elicit, Scite, and Open Paper already occupy this space |
| **Avoid for now** | Autonomous synthesis or manuscript generation | Expands claim and safety risk before retrieval quality is established |
| **Avoid** | Generic meta-analysis engine | Mature R/Python ecosystems already solve it |

## Recommended positioning

Current broad wording:

> Research evidence mapping from public literature metadata.

More defensible wording:

> A lightweight CLI that turns public scholarly metadata into verifiable, deterministic reference snapshots for evidence-synthesis handoffs.

The repository name can remain, but the README should explain that “map” currently means a structured metadata/evidence table and reference graph schema, not a complete systematic review, bibliometric network, or scientific conclusion.

## Improvement roadmap

### P0 — make v0.2.4 useful with a user's own records

1. **Canonical input contract**
   - Accept DOI, PMID, OpenAlex ID, and public registry accessions.
   - Accept newline lists plus RIS, BibTeX, and CSV.
   - Preserve the original input string, normalized identifier, source, and resolution status.

2. **Interoperable export contract**
   - RIS for ASReview, Rayyan-like tools, and citation-chasing tools.
   - BibTeX for JabRef and LaTeX workflows.
   - CSV for screening and audit.
   - Existing JSON/SQLite/HTML retained as canonical verifiable artifacts.

3. **Deduplication audit**
   - Record exact-match and heuristic-match reasons.
   - Never silently merge ambiguous records.
   - Provide a machine-readable unresolved queue.

4. **Positioning correction**
   - Change the top-level tagline.
   - Add an explicit “not screening / not full text / not meta-analysis” comparison box.
   - Add one handoff quickstart rather than another internal demo.

### P1 — make the map literal and measurable

1. Add a project manifest recording query text, cartridge, source set, retrieval timestamp, package version, and non-secret authentication-presence flags.
2. Support deterministic snapshot/update/diff with added, removed, and changed records plus stable content hashes.
3. Expand cited and citing relations from seed records through OpenAlex and, where appropriate, OpenCitations.
4. Generate a self-contained interactive HTML relation view with filtering by year, source, theme, and relation type.
5. Add public benchmark fixtures at 100 and 1,000 records.
6. Evaluate identifier resolution, duplicate precision/recall, source overlap, and deterministic reruns.
7. Publish handoff examples for ASReview, CoLRev, Zotero/JabRef, and bibliometrix.

### External adoption observations — not release gates

Track, but do not claim to control, the following external outcomes:

1. Independent installations and public failure/correction reports.
2. A downstream handoff into another tool.
3. Corrections to the compatibility guide from maintainers of adjacent projects; ask for correction, not endorsement or stars.
4. Repeated external bottlenecks that justify new features.

## Why not just export OpenAlex CSV?

For a one-off OpenAlex search, the official export may be sufficient and SHawn adds little. SHawn becomes useful only when a workflow needs normalized identifiers across sources, explicit provenance and duplicate decisions, deterministic SQLite/JSON artifacts, integrity checks, and the same standards-based handoff on rerun. The next release must demonstrate that distinction with user-supplied inputs; it should not claim it in the abstract.

## Acceptance gates for the next release

These are future targets, not current results:

- a fresh public wheel imports a mixed public test set of DOI/PMID/OpenAlex IDs;
- repeated imports produce the same canonical JSON and SQLite hash;
- RIS and BibTeX round-trip tests preserve identifiers and titles;
- ambiguous duplicates are reported instead of silently merged;
- a missing or malformed input fails without creating a false-success artifact;
- a 100-record public fixture completes with documented correctness and provenance checks;
- at least one external person completes or publicly fails the handoff quickstart.

## Final assessment

The project should continue, but not by racing ASReview, Elicit, bibliometrix, PaperQA2, or Open Knowledge Maps feature-for-feature.

Its best opportunity is the space between metadata APIs and review applications:

```text
public scholarly APIs / user identifiers
                ↓
normalized, provenance-rich, deterministic snapshot
                ↓
RIS / BibTeX / CSV / JSON / SQLite handoff
                ↓
ASReview · CoLRev · Zotero · bibliometrix · custom agents
```

That position is narrower than “complete evidence mapping,” but it is clearer, technically credible, compatible with the current public-safety boundary, and more likely to earn real downstream use.

## Primary sources

- [Raw 39-repository and onboarding snapshot](../benchmarks/results/2026-07-11-ecosystem-snapshot.json)
- [Evidence Synthesis Tools directory](https://evidencesynthesis-tools.github.io/)
- [ASReview official site](https://asreview.nl/)
- [CoLRev documentation](https://colrev-environment.github.io/colrev/)
- [MetaScreener repository](https://github.com/ChaokunHong/MetaScreener)
- [Open Knowledge Maps](https://openknowledgemaps.org/) and [Headstart](https://github.com/OpenKnowledgeMaps/Headstart)
- [bibliometrix official site](https://www.bibliometrix.org/)
- [PaperQA2 repository](https://github.com/Future-House/paper-qa)
- [Rayyan](https://www.rayyan.ai/), [Elicit](https://elicit.com/), [Covidence](https://www.covidence.org/), [DistillerSR](https://www.distillersr.com/), and [Nested Knowledge](https://about.nested-knowledge.com/)
- [ResearchRabbit](https://www.researchrabbit.ai/), [Connected Papers](https://www.connectedpapers.com/), [Litmaps](https://www.litmaps.com/), [Scite](https://scite.ai/), and [VOSviewer](https://www.vosviewer.com/)
- [CADIMA](https://www.cadima.info/) and [EPPI-Reviewer](https://eppi.ioe.ac.uk/cms/er4/)
