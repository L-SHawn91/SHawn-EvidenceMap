# Metadata Bridge pilot outreach strategy

PUBLIC_STATUS: public launch playbook · no private contact data

## Objective

Obtain independent evidence that a researcher, librarian, or research-software user can run SHawn EvidenceMap on a real public metadata workflow and identify whether the metadata bridge saves meaningful cleanup or handoff time.

The objective is not to maximize stars, impressions, clones, or maintainer-generated downloads. A documented failure is useful evidence.

## Current baseline — 2026-07-12

```text
Independent documented runs: 0
External actionable issues: 0
Documented downstream uses: 0
Free validation cohort participants: 0
Repeat users: 0
```

Maintainer executions, CI, release read-backs, and automated traffic do not change this baseline.

## Positioning

Use:

> SHawn EvidenceMap is an Apache-2.0, local-first CLI that turns public DOI, PMID, OpenAlex, accession, CSV, RIS, and BibTeX records into auditable SQLite/JSON snapshots and deterministic CSV/RIS/BibTeX handoffs. It records provenance and inserted/merged/rejected decisions instead of silently merging identifier collisions.

Short form:

> Turn messy DOI and PMID lists into auditable, deterministic research handoffs—locally, without lock-in.

Do not say:

- verified DOI or registry-validated identifier;
- scientifically validated evidence;
- systematic-review replacement;
- clinical-grade or submission-ready;
- private workspace, private upload, or enterprise SLA;
- faster or better than another tool without a scoped executable benchmark.

`Verifiable` refers to local integrity, provenance, normalized identifiers, and recorded processing decisions.

## Public conversion surfaces

- Landing page: https://l-shawn91.github.io/SHawn-EvidenceMap/pilot.html
- 60-second executable demo: https://l-shawn91.github.io/SHawn-EvidenceMap/assets/pilot-demo-60s.mp4
- Pilot intake and discussion: https://github.com/L-SHawn91/SHawn-EvidenceMap/discussions/9
- Structured run feedback: https://github.com/L-SHawn91/SHawn-EvidenceMap/issues/new?template=pilot-feedback.yml
- Free release: https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/tag/v0.2.4

Do not publish a personal email address. Do not collect private data through GitHub.

## Initial user profile

Prioritize:

1. systematic or scoping review researchers managing DOI/PMID lists in spreadsheets;
2. medical or health-science librarians supporting evidence synthesis;
3. graduate students, postdocs, and research faculty handing records to Zotero or Rayyan;
4. small labs that need a reproducible metadata manifest for a public research workflow;
5. research-software engineers evaluating local-first metadata interoperability.

Do not target pharmaceutical/CRO enterprise, clinical decision support, regulated submissions, private full-text workflows, or teams requiring an SLA during this validation stage.

## Current free-validation boundary

The Apache-2.0 CLI, import/export formats, audit events, database verification, documentation, and bug fixes remain free. The first three bounded validation slots are also free and include:

- metadata cleanup and collision review;
- reproducible audit snapshot and export package;
- workflow setup for Zotero, Rayyan, R, or Python;
- one 30-minute feedback conversation.

Keep each validation run to approximately 20–250 public metadata records and one handoff workflow. This stage includes no SLA, custom feature development, private-data handling, or ongoing support commitment.

Do not publish pricing or solicit payment at this stage. Reconsider a support model only after all of these are true:

1. at least five independently documented executions;
2. at least three repeat users;
3. at least two users independently ask for setup or ongoing support;
4. no unresolved P0/P1 onboarding blocker;
5. applicable institutional and administrative requirements have been checked.

## Fourteen-day sprint

### Days 1–2 — public conversion path

- [x] remove personal Gmail addresses from tracked launch surfaces;
- [x] configure future repository commits with a GitHub noreply address;
- [x] make Discussion #9 the primary public intake;
- [x] publish an explicit no-private-data boundary.

### Days 3–4 — executable demonstration

- [x] build a tracked public/synthetic CSV fixture;
- [x] execute the real v0.2.4 ingest, verify, and export path;
- [x] publish the actual `3 inserted / 2 merged / 1 rejected` result;
- [x] publish a reproducible 60-second MP4 and downloadable outputs.

### Days 5–7 — five personalized outreach slots

Send no more than five direct messages before reviewing response quality:

| Slot | Role | Personalization evidence | Ask | Status |
|---|---|---|---|---|
| 1 | evidence-synthesis librarian | public methods/support page | 20-minute workflow observation | pending |
| 2 | systematic-review author | recent public review/method paper | test public DOI/PMID handoff | pending |
| 3 | graduate student or postdoc | public review workflow context | identify first confusing step | pending |
| 4 | research-software engineer | public metadata/reproducibility work | inspect audit/interchange boundary | pending |
| 5 | open-science community member | public interoperability activity | reproduce one documented path | pending |

Do not store names, email addresses, private replies, or unpublished topics in this repository. Record only aggregate counts and public links a participant chooses to publish.

### Days 8–10 — interviews

Target three 20-minute workflow interviews. Observe the current process before presenting the tool. Ask:

1. Where does the DOI/PMID list originate?
2. Which duplicate or conflict cases require manual work?
3. Which tool receives the cleaned list?
4. What provenance must be retained?
5. Would you run this workflow again, and why or why not?

### Days 11–14 — evidence snapshot

Record only:

- outreach attempts;
- responses;
- interviews completed;
- independent executions;
- actionable issues;
- unsolicited setup or support requests;
- completed free validation runs;
- repeat users.

## Direct outreach template

> Hi — I maintain SHawn EvidenceMap, a new Apache-2.0 metadata bridge for public DOI/PMID and bibliographic records. I am not asking for a star or endorsement. I am trying to learn how researchers currently clean duplicates and preserve provenance before moving records into Zotero, Rayyan, R, or Python. Would you be willing to show me that workflow for 20 minutes or try one public example? A negative result is useful. The 60-second executable demo and data boundary are here: https://l-shawn91.github.io/SHawn-EvidenceMap/pilot.html

Personalize the first two sentences from the recipient's public work. Never imply affiliation or prior approval.

## Community post template

> Maintainer disclosure: I built SHawn EvidenceMap, an early Apache-2.0 CLI for local-first scholarly metadata handoffs. It normalizes public DOI/PMID/OpenAlex/accession records, records inserted/merged/rejected decisions, and exports auditable SQLite/JSON plus deterministic CSV/RIS/BibTeX. It is not a screening platform and does not validate identifiers against external registries. I am looking for one or two failure-oriented pilot runs, not stars or endorsements. Demo, fixture, outputs, and limitations: https://l-shawn91.github.io/SHawn-EvidenceMap/pilot.html

Check each community's posting rules before posting. Do not paste identical promotional text into multiple communities on the same day.

## Channel order

1. High-fit direct contacts: five personalized requests.
2. GitHub Discussion #9 and structured feedback issue.
3. OpenAlex Community or evidence-synthesis software communities after one independent run.
4. Research-software communities after one concrete correction or use case.
5. Broad social or OSS channels only after a documented downstream run.

Never advertise inside competitor issue trackers.

## KPI gates

### Day 14

- three completed interviews;
- one independent execution attempt;
- one actionable correction or explicit workflow-fit statement.

### Day 30

- three independent users;
- one actionable external issue;
- one real public metadata workflow completed.

### Day 60

- five independently documented executions;
- at least two repeat users;
- evidence of which output or onboarding step creates repeat value.

### Day 90

- three repeat users and two unsolicited support requests;
- only then decide whether to test a support model privately;
- otherwise retain the project as free OSS/research infrastructure.

## Stop and reassess

Pause broader promotion if:

- the first two independent users cannot complete installation;
- two users fail at the same onboarding step;
- users consistently expect registry validation or scientific appraisal;
- no one can name a real handoff pain after five interviews;
- external support would conflict with applicable institutional or administrative requirements.

Fix the product boundary or onboarding before widening reach.

## Prohibited tactics

- asking for stars, forks, downloads, or reciprocal promotion;
- treating maintainer traffic as adoption;
- scraped email lists, mass DMs, or repeated unsolicited follow-ups;
- publishing private correspondence or participant identities;
- accepting private PDFs, manuscripts, patient/sample data, credentials, or confidential review queries;
- claiming demand, adoption, superiority, or scientific validation without evidence.
