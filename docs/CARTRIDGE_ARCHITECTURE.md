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

future cartridges/
  ai_cs
  policy
  education
  patent
```

## Current Cartridge

`bio` is the only active public cartridge.

It uses:
- PubMed
- Europe PMC
- biomedical evidence labels
- recent/foundational/balanced ranking modes

## Expansion Rule

Keep new cartridges shallow until demand appears.

Add a cartridge to the public CLI only after:
- it has public-safe sources
- it has a minimal ranking rule
- it has evidence labels
- it passes safety scan
- it has at least one public sample output

## Private Boundary

The public cartridge layer must not directly import private SHawn ecosystem repos, private caches, private corpus DBs, or personal workflow state.

Private SHawn ecosystem capabilities can inform later premium workflows, but only through audited public-safe adapters and outputs.
