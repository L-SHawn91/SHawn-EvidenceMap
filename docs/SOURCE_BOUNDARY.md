# Source Boundary

PUBLIC_STATUS: public-demo

SHawn EvidenceMap separates public-demo sources from private/commercial sources.

## Public Sources

Public cartridges may use sources that are:
- accessible without API keys
- accessible without account login
- safe to call from public-demo code
- based on public metadata

Current public sources:
- PubMed E-utilities
- Europe PMC
- OpenAlex
- Crossref

## Private-Only Sources

Sources requiring API keys, paid accounts, user login, institutional access, or private uploaded files are private-only.

Examples:
- paid legal databases
- authenticated patent APIs
- private customer uploads
- full-text PDF libraries
- private reference-manager libraries or corpus DBs
- institutional journal access
- customer confidential material
- SHawn private ecosystem caches and registries

Private-only sources must not be imported directly into this public repo.

## Product Rule

Public report output can mention that deeper paid work may use additional verified sources, but the public code must not include credentials, private endpoints, private paths, or private workflow assumptions.
