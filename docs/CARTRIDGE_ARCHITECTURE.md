# Cartridge Architecture

PUBLIC_STATUS: public-demo

SHawn EvidenceMap uses a cartridge architecture so the public product can stay unified while each domain keeps its own sources, labels, ranking, and output logic.

## Layers

```text
core/
  cartridge contract
  generic pipeline
  dedupe
  shared models
  cache/export/safety

cartridges/
  bio/
    sources
    ranking
    evidence labels
    row template
  ai_cs
  policy
  education
  legal
  patent_tech
```

## Current Cartridge

Active public-demo cartridges:

### `bio`

Uses:
- PubMed
- Europe PMC
- biomedical evidence labels
- recent/foundational/balanced ranking modes

### `ai_cs`

Uses:
- OpenAlex
- Crossref
- method, benchmark, dataset, implementation, and survey labels

### `policy`

Uses:
- OpenAlex
- Crossref
- policy evaluation, intervention, guideline/framework, governance/regulation, and review labels

### `education`

Uses:
- OpenAlex
- Crossref
- intervention, learning outcome, experimental/cohort, review, and technology-enhanced learning labels

### `legal`

Uses:
- OpenAlex
- Crossref
- case law/precedent, statutory/regulatory, legal scholarship, governance/policy, and review labels

### `patent_tech`

Uses:
- OpenAlex
- Crossref
- technology landscape, patent/IP, application, prototype/validation, and review labels

## Expansion Rule

Keep new cartridges shallow until demand appears.

Add or deepen a cartridge in the public CLI only after:
- it has public-safe sources
- it has a minimal ranking rule
- it has evidence labels
- it passes safety scan
- it has at least one public sample output

## Private Boundary

The public cartridge layer must not directly import private SHawn ecosystem repos, private caches, private corpus DBs, or personal workflow state.

Private SHawn ecosystem capabilities can inform later premium workflows, but only through audited public-safe adapters and outputs.
