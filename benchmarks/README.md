# Public benchmark

This directory contains the correctness-first public benchmark for SHawn EvidenceMap.

## What it measures

The runner records three distinct kinds of evidence:

1. SHawn EvidenceMap public-query correctness and informational timing.
2. Deterministic local SQLite creation, verification, and negative-path behavior.
3. An optional PyAlex overlap smoke test that confirms both tools can retrieve three public scholarly metadata records.

The PyAlex lane is **not a speed leaderboard**. PyAlex is a thin OpenAlex API client. SHawn EvidenceMap queries public sources, deduplicates records, ranks them, and renders evidence-map rows. Their scopes and outputs differ.

## Reproduce

Create two isolated environments from public packages:

```bash
python3 -m venv .venv-shawn
.venv-shawn/bin/python -m pip install \
  https://github.com/L-SHawn91/SHawn-EvidenceMap/releases/download/v0.2.3/shawn_evidencemap-0.2.3-py3-none-any.whl

python3 -m venv .venv-pyalex
# 0.21 is pinned to reproduce the version measured on 2026-07-11.
.venv-pyalex/bin/python -m pip install pyalex==0.21
```

From a checkout of this repository, run:

```bash
.venv-shawn/bin/python scripts/public_benchmark.py \
  --source-release v0.2.3 \
  --pyalex-python .venv-pyalex/bin/python \
  --output benchmark.json
```

Defaults:

- network lanes: one discarded warm-up and five measured runs;
- local lanes: three discarded warm-ups and ten measured runs;
- three requested records;
- median, minimum, maximum, raw timings, exit code, peak RSS, and output hashes;
- correctness is evaluated before timing.

OpenAlex currently provides only a limited no-key testing allowance. For repeated runs, use a free key through `OPENALEX_API_KEY`. The runner records only whether a key was present; it never records the value.

## Published result

- [`results/2026-07-11-v0.2.3.json`](results/2026-07-11-v0.2.3.json)
- [Interpretation and cross-project scope snapshot](../docs/PUBLIC_BENCHMARK_2026-07-11.md)

## Claims this benchmark does not support

- that SHawn EvidenceMap is faster than PyAlex;
- that different-scope research tools can be ranked by one runtime number;
- that this early project is production-ready or battle-tested;
- that maintainer-generated runs, CI traffic, or downloads are external adoption;
- that three returned records establish scientific completeness or validity.
