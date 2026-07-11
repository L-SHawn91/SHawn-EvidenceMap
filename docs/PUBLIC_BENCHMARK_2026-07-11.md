# Public benchmark report — 2026-07-11

## Result

SHawn EvidenceMap v0.2.3 passed every correctness gate in a fresh virtual environment built from the candidate release wheel.

| Case | Repetitions | Correctness | Median wall time | Range | Peak RSS |
|---|---:|---|---:|---:|---:|
| SHawn generic public query | 5 | PASS; 3 rows, generic cartridge, no bio-only labels | 3.364 s | 2.742–3.493 s | 29,956 KB |
| SHawn fixed public DB creation | 10 | PASS; DB created every run | 0.097 s | 0.093–0.102 s | 22,744 KB |
| SHawn existing-DB verification | 10 | PASS; integrity checks accepted | 0.075 s | 0.072–0.077 s | 22,748 KB |
| SHawn missing-DB rejection | 10 | PASS; exit 2 and no file creation | 0.075 s | 0.071–0.076 s | 22,244 KB |

### PyAlex overlap smoke — separate scope

| Case | Repetitions | Correctness | Median wall time | Range | Peak RSS |
|---|---:|---|---:|---:|---:|
| PyAlex OpenAlex overlap smoke | 5 | PASS; 3 records with IDs | 1.293 s | 0.823–1.863 s | 28,928 KB |

The separate table is deliberate: PyAlex and SHawn perform different work and must not be treated as one speed leaderboard.

Raw observations, output hashes, environment details, and exact pass conditions are in [`benchmarks/results/2026-07-11-v0.2.3.json`](../benchmarks/results/2026-07-11-v0.2.3.json).

## Interpretation

The result supports a narrow claim:

> In the documented Linux environment, the v0.2.3 candidate wheel repeatedly completed its public-query, fixed-database, integrity-verification, and missing-path safety checks.

It does **not** establish a cross-project speed winner. The PyAlex lane exists only because both tools can retrieve OpenAlex work metadata. PyAlex is a lightweight OpenAlex interface; SHawn EvidenceMap queries public scholarly sources, deduplicates records, ranks them, and renders evidence-map rows. Network latency, OpenAlex service state, source count, and output work differ.

The observed `1.293 s` PyAlex median and `3.364 s` SHawn median must therefore not be presented as “PyAlex is faster” or “SHawn is slower.” They are smoke-test observations from different workflows.

## Method

- **SHawn version:** 0.2.3 candidate wheel installed into a new virtual environment.
- **PyAlex version:** 0.21 installed into a separate virtual environment.
- **Query:** `open science metadata reproducibility`.
- **Requested records:** 3.
- **Network lane:** one discarded warm-up plus five measured runs.
- **Local lane:** three discarded warm-ups plus ten measured runs.
- **Timing statistic:** median, with raw/minimum/maximum retained.
- **Memory:** peak resident set size sampled from Linux `/proc/<pid>/status`.
- **Correctness first:** a fast run fails if its exit code, row count, output marker, cartridge, or file side effect is wrong.
- **Privacy:** hostname, username, working directory, executable paths, credentials, and raw result text are omitted. Output is represented by SHA-256 hashes.
- **OpenAlex authentication:** no API key was present for this short smoke run. OpenAlex's official documentation describes limited no-key testing access; repeated use should set a free `OPENALEX_API_KEY` without exposing its value.

Environment:

```text
Linux 6.8.0-94-generic, x86_64
AMD Ryzen 7 5800X3D, 16 logical CPUs
Python 3.10.12
```

## Three comparison lanes

### Lane A — repeatable SHawn checks

These are comparable across SHawn releases because the commands and expected outcomes are stable:

- generic query returns three rows without biomedical-only default labels;
- fixed public metadata fixture creates a database;
- existing database passes integrity verification;
- missing database is rejected without creating a file.

### Lane B — narrow PyAlex overlap smoke

The only shared assertion is that both tools can retrieve three public scholarly metadata records. Timing is retained for transparency but is not ranked.

### Lane C — public scope snapshot, not runtime ranking

The projects below address related but different tasks. GitHub counts were read from the public GitHub API on 2026-07-11 and will change.

| Project | Publicly described role | Stars | Forks | Created | Runtime rank? |
|---|---|---:|---:|---:|---|
| [SHawn EvidenceMap](https://github.com/L-SHawn91/SHawn-EvidenceMap) | Public-safe scholarly metadata evidence mapping and reference DB artifacts | 0 | 0 | 2026 | No |
| [CoLRev](https://github.com/CoLRev-Environment/colrev) | Open-source environment for collaborative reviews | 43 | 54 | 2021 | No; broader workflow |
| [revtools](https://github.com/mjwestgate/revtools) | R tools supporting research synthesis | 58 | 25 | 2016 | No; different language and workflow |
| [EviAtlas](https://github.com/ESHackathon/eviatlas) | Geographic visualization for systematic maps | 31 | 9 | 2018 | No; visualization scope |
| [PyAlex](https://github.com/J535D165/pyalex) | Python interface to OpenAlex | 396 | 50 | 2022 | Overlap smoke only |
| [Citation.js](https://github.com/citation-js/citation-js) | Citation-format conversion | 206 | 48 | 2024 | No; conversion scope |

This snapshot demonstrates the adoption gap rather than technical superiority: SHawn EvidenceMap has reproducible release evidence but no external stars, forks, contributors, or documented downstream use at the measurement date.

## Operational finding and v0.2.3 change

The comparison exposed an important deployment boundary. OpenAlex now treats API keys as the normal access path and limits no-key use to testing/demo access. v0.2.3 therefore adds optional `OPENALEX_API_KEY` support.

Security boundary:

- the key is read only from the environment;
- blank values are omitted;
- credential-bearing request URLs are not included in raised error messages;
- tests verify HTTP errors do not expose the key;
- benchmark JSON records only a Boolean `openalex_api_key_present` value.

## Claims we do not make

- SHawn EvidenceMap is faster, lighter, more complete, or better than PyAlex or another project.
- Different-scope research tools form a valid speed leaderboard.
- Five network requests establish stable service-level performance.
- Three records establish search completeness or scientific validity.
- The project is production-ready, battle-tested, widely adopted, or independently validated.
- Maintainer-generated CI, clones, release downloads, or benchmark runs are external adoption.
- A repository metric measures scientific quality.

## Limitations

- One Linux workstation and one network route were measured.
- Network results depend on OpenAlex, Crossref, DNS, and transient service conditions.
- The benchmark uses one query and three requested records.
- It does not test thousands of records, concurrency, long-running services, or custom DOI/PMID/GEO database ingestion.
- The project author designed and executed the benchmark. Public code, raw data, output hashes, and explicit prohibited claims reduce but do not remove self-benchmark bias.
- Cross-project GitHub metrics measure activity and adoption signals, not correctness or scientific value.

## Reproduce or challenge the result

Run the documented command in [`benchmarks/README.md`](../benchmarks/README.md). A useful external response is not a star; it is one of:

- a raw JSON result from another environment;
- a public issue describing an install or correctness failure;
- a correction to the comparison scope;
- a small pull request improving the runner or methodology.
