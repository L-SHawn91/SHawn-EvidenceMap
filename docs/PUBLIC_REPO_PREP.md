# Public Repo Preparation

PUBLIC_STATUS: public-demo

## Current state

- Public GitHub repository and static GitHub Pages demo exist.
- Apache-2.0 licensing is active.
- Public boundary, security, citation, and contribution documents are present.
- Public-safe supporting layers exist: search-lite, paper-map-lite, sync-lite, newbrain-router, and document QA utilities.

## Maintainer checklist

Before public release or application references:

1. Run the public safety scan.
2. Run smoke tests or compile checks.
3. Confirm no private paths, credentials, caches, databases, manuscripts, PDFs, or workflow state are present.
4. Confirm examples use only public metadata or synthetic outputs.
5. Confirm release notes and roadmap issues are current.

## Do not include

- Local cache files
- Logs
- Private SHawn workflow docs
- Private cloud project strategy docs
- Private comparison reports unless rewritten for public audience
