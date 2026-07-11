# Five-minute public onboarding

Choose the path that matches what you want to test.

| Goal | Command | Network |
|---|---|---|
| Search public scholarly metadata for your own topic | `evidencemap "your topic"` | Required |
| Verify the bundled SQLite/JSON/HTML reference pipeline | `python -m evidencemap.refdb public-demo ...` | Not required after installation |

The SQLite pilot is a **fixed fixture**. Version 0.2.3 does not accept a replacement DOI, PMID, or GEO accession. Do not interpret the bundled registry linkage as independent validation of a scientific conclusion.

## 1. Install the verified release

Use an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/download/v0.2.3/shawn_evidencemap-0.2.3-py3-none-any.whl
```

The package is not currently published on PyPI. The command above installs the GitHub release wheel.

OpenAlex currently provides only a limited no-key testing allowance. One short pilot normally fits that allowance. For repeated searches, set a free key in the environment without posting it publicly:

```bash
export OPENALEX_API_KEY="your-key"
```

## Path A — search your own topic

The default `generic` cartridge uses domain-neutral labels and public OpenAlex/Crossref metadata:

```bash
evidencemap "open science metadata reproducibility" --limit 3 --markdown --no-cache
```

Choose a domain cartridge when domain-specific sources and evidence labels are appropriate:

```bash
evidencemap "endometrial organoid implantation" --cartridge bio --limit 5 --markdown --no-cache
```

Available cartridges are shown by:

```bash
evidencemap --help
```

This path requires network access. Results are research-triage output and require manual source verification before citation or public claims.

## Path B — verify the fixed database reference

- **Time:** about 5 minutes
- **Input:** bundled public identifiers and titles only
- **Network during these commands:** none

```bash
mkdir -p pilot-output
python -m evidencemap.refdb public-demo --db pilot-output/public-metadata.sqlite3
python -m evidencemap.refdb verify --db pilot-output/public-metadata.sqlite3
python -m evidencemap.refdb export --db pilot-output/public-metadata.sqlite3 --out pilot-output/reference.json
python -m evidencemap.refdb page --db pilot-output/public-metadata.sqlite3 --out pilot-output/index.html
```

Expected status markers:

```text
PUBLIC_METADATA_DB_DEMO_OK
REFERENCE_DB_OK
```

The export should contain:

```text
entities: 3
identifiers: 4
relations: 3
provenance: 3
ingest_runs: 1
```

Open `pilot-output/index.html` and inspect:

- DOI `10.1016/j.cell.2020.04.026`
- PMID `32416070`
- GEO accession `GSE147507`
- explicit paper–dataset linkage relations
- clickable NCBI PubMed and GEO provenance links
- canonical JSON and SQLite structure

The bundled snapshot was verified against:

- PubMed: https://pubmed.ncbi.nlm.nih.gov/32416070/
- NCBI GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE147507

### Negative-path check

A read command must not create or approve a database that does not exist:

```bash
python -m evidencemap.refdb verify --db pilot-output/does-not-exist.sqlite3
```

Expected result:

```text
REFERENCE_DB_ERROR: database does not exist: pilot-output/does-not-exist.sqlite3
```

The command exits nonzero and does not create the file.

## Send genuine pilot feedback

Open the [pilot feedback form](https://github.com/L-SHawn91/SHawn-EvidenceMap/issues/new?template=pilot-feedback.yml) and report:

- which path you ran
- whether the commands completed
- the first confusing step
- a reproducible installation or output problem
- one public-metadata use case the current interface does or does not support

GitHub authentication is required to submit the issue. A positive report is not required; specific friction and reproducible failures are more useful than stars.

## Public boundary

The bundled snapshot contains public identifiers, titles, registry linkage, and source URLs only. It contains no abstract, article full text, PDF, sample-level expression values, patient information, private manuscript, or unpublished research record.

Do not paste private manuscripts, PDFs, credentials, patient/sample data, or confidential project details into a pilot issue.

## What counts as adoption evidence

The maintainer does not treat self-runs, automated CI, or requested stars as external adoption. A pilot becomes public adoption evidence only when an external user independently confirms a real run, use case, problem, or contribution.
