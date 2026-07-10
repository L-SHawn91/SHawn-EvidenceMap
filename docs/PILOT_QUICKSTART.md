# Five-minute public metadata pilot

This pilot verifies that SHawn EvidenceMap can persist and export an official paper–dataset registry linkage without downloading article text or research data.

- **Time:** about 5 minutes
- **Input:** bundled public identifiers and titles only
- **Network during the demo:** none

## 1. Install the verified release

Use an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/download/v0.2.1/shawn_evidencemap-0.2.1-py3-none-any.whl
```

The package is not currently published on PyPI. The command above installs the GitHub release wheel.

## 2. Build the public metadata snapshot

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

## 3. Inspect the result

Open `pilot-output/index.html` in a browser and check that it shows:

- paper DOI `10.1016/j.cell.2020.04.026`
- paper PMID `32416070`
- GEO accession `GSE147507`
- explicit `paper → dataset` and linkage relations
- provenance URLs for NCBI PubMed and NCBI GEO

The bundled snapshot was verified against:

- PubMed: https://pubmed.ncbi.nlm.nih.gov/32416070/
- NCBI GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE147507

## 4. Send genuine pilot feedback

Please open the [pilot feedback form](https://github.com/L-SHawn91/SHawn-EvidenceMap/issues/new?template=pilot-feedback.yml) and report one of the following:

- whether the commands completed
- the first confusing step
- a reproducible installation or output problem
- one public-metadata use case the schema does or does not support

A positive report is not required. Specific friction and reproducible failures are more useful than stars.

## Public boundary

This snapshot contains public identifiers, titles, registry linkage, and source URLs only. It contains no abstract, article full text, PDF, sample-level expression values, patient information, private manuscript, or unpublished research record. The registry linkage does not independently validate a scientific conclusion.

Do not paste private manuscripts, PDFs, credentials, patient/sample data, or confidential project details into a pilot issue.

## What counts as adoption evidence

The maintainer does not treat self-runs, automated CI, or requested stars as external adoption. A pilot becomes public adoption evidence only when an external user independently confirms a real run, use case, problem, or contribution.
