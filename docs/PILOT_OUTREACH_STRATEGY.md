# Pilot outreach strategy

## Objective

The objective is to obtain independent, public evidence that another person can install SHawn EvidenceMap, run one documented path, and report what worked or failed.

The objective is **not** to maximize stars, impressions, clones, or maintainer-generated activity.

## Current baseline — 2026-07-11

```text
External users with a documented run: 0
External feedback comments: 0
External issues or pull requests: 0
Documented downstream uses: 0
```

Maintainer runs, CI jobs, release read-backs, benchmark executions, and automated clones do not change this baseline.

## Conversion event

A successful pilot conversion requires all three:

1. a distinct external person;
2. a stated install or execution attempt using their own environment or topic;
3. a verifiable public link, such as a GitHub Discussion comment, issue, pull request, or public downstream repository.

A failure report counts as a successful pilot conversion if it satisfies those conditions. A star without an execution report does not count.

## Positioning

Use this description:

> SHawn EvidenceMap is an early, public-safe command-line tool that searches public scholarly metadata, deduplicates and ranks records, and can produce a deterministic SQLite/JSON/HTML reference fixture. It is seeking installation and workflow feedback, not endorsement.

Do not position it as a replacement for CoLRev, revtools, EviAtlas, PyAlex, Citation.js, or a full systematic-review platform.

## Channel order

### Tier 0 — direct design review, days 1–7

Ask 3–5 existing professional contacts who perform literature review, bibliometrics, research software, or open-science work.

Request:

- 15 minutes;
- one documented path;
- their own topic if using the search path;
- one public sentence about success or failure;
- no star and no endorsement.

Why first: response quality and relevance are higher than broad public posting, and the first corrections can be made before wider exposure.

Privacy: do not publish contact names, private replies, email addresses, or unpublished research topics. Only link feedback the participant has made public.

### Tier 1 — domain communities, after one direct review

#### Evidence Synthesis Hackathon

Official site: https://eshackathon.org/

The ESHackathon explicitly supports development, testing, and promotion of open evidence-synthesis software and workflows. Approach it as a testing or interoperability request, not a product launch.

Potential fit:

- ESHToolsBlog or a tool-testing discussion after one independent run;
- a reproducibility or interoperability demo;
- feedback on where a metadata triage layer fits in evidence-synthesis workflows.

Do not claim ESHackathon affiliation or list the tool in a community project without acceptance.

#### ESMARConf

Official mission: https://esmarconf.org/mission/

ESMARConf focuses on evidence synthesis and meta-analysis in R. SHawn EvidenceMap is Python-based, so it should not be pitched as a direct conference fit until there is an R-facing export or a concrete cross-language workflow. Treat it as a later collaboration route, not the first promotional channel.

#### OpenAlex Community Group

Official community route: https://groups.google.com/g/openalex-community

Use the community discussion group rather than the announcement-focused OpenAlex User Group. Position SHawn EvidenceMap as a downstream OpenAlex/Crossref integration and triage layer, not a PyAlex competitor.

A courtesy note to PyAlex maintainers may share the benchmark scope before wider distribution. It must not request endorsement, stars, reciprocal links, or issue-tracker promotion.

### Tier 2 — research software communities, after one real case

- US-RSE: https://us-rse.org/
- Society of Research Software Engineering: https://society-rse.org/

Join the relevant community route and check its posting norms first. Share a reproducibility case or ask for benchmark-method feedback. Do not drop a generic repository link into unrelated channels.

Entry gate:

```text
At least one external documented run
and one concrete correction or use case
```

### Tier 3 — broad OSS channels, after a documented downstream case

Examples include general open-source forums, Reddit, Hacker News, or social media. Broad promotion before a real case is likely to produce low-quality traffic and no evidence.

Entry gate:

```text
One public downstream use
or one external benchmark reproduction
or one merged external contribution
```

## Cadence

- Contact no more than two high-fit people or communities per week initially.
- Do not post identical text to several communities on the same day.
- Wait at least seven days before one polite follow-up.
- Stop after one unanswered follow-up.
- Record public outcomes, not private identities.
- If two people fail at the same step, pause promotion and fix onboarding before widening reach.

## Message templates

### Direct pilot request

> Hi — I maintain SHawn EvidenceMap, a two-week-old open-source CLI for public scholarly metadata triage and reproducible SQLite/JSON/HTML outputs. I am not asking for a star or endorsement. Would you be willing to spend 15 minutes trying either your own search topic or the fixed offline fixture, then leave one public sentence about where it worked or failed? The install path and scope limits are here: https://github.com/L-SHawn91/SHawn-EvidenceMap/discussions/9

### OpenAlex community request

> Maintainer disclosure: I built SHawn EvidenceMap, an early open-source downstream tool using public OpenAlex and Crossref metadata. It is not a replacement for PyAlex or a full review platform. I published a correctness-first benchmark with raw JSON and explicitly avoided a speed ranking because the workflows differ. I am looking for one or two people to reproduce the three-record metadata path or point out an unfair comparison assumption. No star or endorsement requested. Benchmark: https://github.com/L-SHawn91/SHawn-EvidenceMap/blob/main/docs/PUBLIC_BENCHMARK_2026-07-11.md

### Evidence-synthesis tool-testing request

> I maintain a new Python CLI that turns public scholarly metadata into a small evidence-triage map and deterministic reference artifacts. The project currently has no documented external users, so I am seeking failure-oriented testing rather than promotion. Would one reviewer be willing to try a 15-minute public pilot and identify where this does or does not fit an evidence-synthesis workflow? Scope, unsupported use cases, raw benchmark data, and the feedback form are public.

## Public response destinations

Preferred:

1. Discussion #9 for a short run report;
2. the pilot feedback issue form for a reproducible failure or unsupported use case;
3. a pull request for a documentation or benchmark correction;
4. a public downstream repository for an actual use case.

Never ask participants to share private PDFs, manuscripts, credentials, API keys, patient data, unpublished datasets, or confidential review queries.

## KPI gates

### By 2026-07-25 — 14 days

- benchmark runner, raw JSON, and interpretation publicly merged;
- 2 direct design-review requests sent;
- at least 1 external public response or installation attempt;
- at least 1 correction incorporated, if a correction is received;
- courtesy benchmark-scope notice prepared for PyAlex maintainers, but not posted to an issue tracker as advertising.

### By 2026-08-10 — 30 days

- at least 3 independently documented install attempts;
- at least 2 distinct external people;
- at least 1 actionable external issue, including a failure report;
- at least 1 external benchmark reproduction or raw-result comparison;
- OpenAlex Community or ESHackathon outreach attempted only if the first direct review has occurred.

### By 2026-09-09 — 60 days

- at least 1 documented use with an external person's own topic or workflow;
- at least 1 external contribution, including documentation;
- at least 1 community demo, tool-testing conversation, or public downstream link;
- decision recorded: continue, reposition, integrate with another project, or archive.

## Stop and reassess rules

Pause broader promotion when any condition occurs:

- the first two independent users cannot finish installation;
- benchmark correctness fails on another supported environment;
- OpenAlex authentication or rate limits block the advertised pilot;
- the project cannot explain how it differs from a thin API client or full review platform;
- feedback indicates the primary use case is unsupported.

In those cases, fix the product boundary before increasing reach.

## Prohibited tactics

- asking for stars, forks, downloads, or reciprocal promotion;
- using alternate accounts or coordinated self-engagement;
- treating maintainer downloads or CI clones as adoption;
- posting advertisements in competitor issue trackers;
- claiming superiority from the PyAlex smoke timing;
- claiming affiliation with OpenAlex, ESHackathon, ESMARConf, or RSE organizations;
- mass direct messages, scraped email lists, or repeated unsolicited follow-ups;
- publishing private correspondence as evidence.
