#!/usr/bin/env python3
"""Run a correctness-first public benchmark for SHawn EvidenceMap.

Network timing is recorded for reproducibility, not as a cross-tool speed rank.
The JSON output intentionally omits hostnames, usernames, working directories,
and full command paths.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable, Sequence


def summarize_numbers(values: Sequence[float]) -> dict[str, Any]:
    """Return raw observations and robust summary statistics."""
    if not values:
        raise ValueError("at least one observation is required")
    raw = list(values)
    return {
        "median": statistics.median(raw),
        "min": min(raw),
        "max": max(raw),
        "raw": raw,
    }


def _linux_rss_kb(pid: int) -> int:
    status = Path(f"/proc/{pid}/status")
    try:
        for line in status.read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
        return 0
    return 0


def run_command(
    command: Sequence[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute one command and capture timing, output, and sampled peak RSS."""
    started = time.perf_counter()
    process = subprocess.Popen(
        list(command),
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    peak_rss_kb = 0
    stop = threading.Event()

    def monitor() -> None:
        nonlocal peak_rss_kb
        while not stop.is_set():
            peak_rss_kb = max(peak_rss_kb, _linux_rss_kb(process.pid))
            stop.wait(0.002)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    stdout, stderr = process.communicate()
    stop.set()
    thread.join(timeout=0.1)
    peak_rss_kb = max(peak_rss_kb, _linux_rss_kb(process.pid))
    return {
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "wall_seconds": time.perf_counter() - started,
        "peak_rss_kb": peak_rss_kb,
    }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def evaluate_runs(
    name: str,
    runs: Sequence[dict[str, Any]],
    *,
    expected_exit_code: int,
    required_stdout: Sequence[str] = (),
    required_stderr: Sequence[str] = (),
    forbidden_stdout: Sequence[str] = (),
) -> dict[str, Any]:
    """Evaluate correctness first, then summarize informational timing."""
    if not runs:
        raise ValueError("at least one run is required")
    failed_runs: list[int] = []
    failure_reasons: dict[str, list[str]] = {}
    samples: list[dict[str, Any]] = []

    for index, run in enumerate(runs, start=1):
        reasons: list[str] = []
        if run["exit_code"] != expected_exit_code:
            reasons.append(
                f"exit {run['exit_code']} != expected {expected_exit_code}"
            )
        reasons.extend(
            f"stdout missing {value!r}"
            for value in required_stdout
            if value not in run["stdout"]
        )
        reasons.extend(
            f"stderr missing {value!r}"
            for value in required_stderr
            if value not in run["stderr"]
        )
        reasons.extend(
            f"stdout contains forbidden {value!r}"
            for value in forbidden_stdout
            if value in run["stdout"]
        )
        if reasons:
            failed_runs.append(index)
            failure_reasons[str(index)] = reasons
        samples.append(
            {
                "exit_code": run["exit_code"],
                "wall_seconds": run["wall_seconds"],
                "peak_rss_kb": run["peak_rss_kb"],
                "stdout_sha256": _sha256_text(run["stdout"]),
                "stderr_sha256": _sha256_text(run["stderr"]),
            }
        )

    return {
        "name": name,
        "correctness": {
            "pass": not failed_runs,
            "failed_runs": failed_runs,
            "failure_reasons": failure_reasons,
            "expected_exit_code": expected_exit_code,
        },
        "timing_is_informational": True,
        "wall_seconds": summarize_numbers(
            [float(run["wall_seconds"]) for run in runs]
        ),
        "peak_rss_kb": {
            "max": max(int(run["peak_rss_kb"]) for run in runs),
            "raw": [int(run["peak_rss_kb"]) for run in runs],
        },
        "samples": samples,
    }


def _cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except (FileNotFoundError, PermissionError, IndexError):
        pass
    return platform.processor() or "unknown"


def _environment() -> dict[str, Any]:
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "cpu_model": _cpu_model(),
        "logical_cpu_count": os.cpu_count(),
        "python": platform.python_version(),
        "rss_method": "linux_proc_status_sampling",
        "openalex_api_key_present": bool(
            os.environ.get("OPENALEX_API_KEY", "").strip()
        ),
        "hostname_omitted": True,
        "paths_omitted": True,
    }


def _measure(
    command_factory: Callable[[int, bool], tuple[list[str], Callable[[dict[str, Any]], None] | None]],
    *,
    cwd: Path,
    warmups: int,
    repetitions: int,
) -> list[dict[str, Any]]:
    for index in range(warmups):
        command, after = command_factory(index, True)
        result = run_command(command, cwd=cwd)
        if after:
            after(result)
    measured: list[dict[str, Any]] = []
    for index in range(repetitions):
        command, after = command_factory(index, False)
        result = run_command(command, cwd=cwd)
        if after:
            after(result)
        measured.append(result)
    return measured


def _shawn_cli_command(query: str) -> list[str]:
    return [
        sys.executable,
        "-c",
        "from evidencemap.cli import main; main()",
        query,
        "--limit",
        "3",
        "--markdown",
        "--no-cache",
    ]


def _pyalex_command(python: str, query: str) -> list[str]:
    code = (
        "from importlib.metadata import version; "
        "from pyalex import Works; "
        f"rows=Works().search({query!r}).get(per_page=3); "
        "print('PYALEX_VERSION='+version('pyalex')); "
        "print('ROWS='+str(len(rows))); "
        "print('IDS_PRESENT='+str(all(bool(row.get(\"id\")) for row in rows)))"
    )
    return [python, "-c", code]


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    query = args.query
    with tempfile.TemporaryDirectory(prefix="evidencemap-public-benchmark-") as raw:
        work = Path(raw)

        def query_factory(index: int, warmup: bool) -> tuple[list[str], Callable[[dict[str, Any]], None]]:
            def annotate(result: dict[str, Any]) -> None:
                rows = result["stdout"].count("\n| candidate |")
                result["stdout"] += f"\nBENCH_ROWS={rows}\n"

            return _shawn_cli_command(query), annotate

        query_runs = _measure(
            query_factory,
            cwd=work,
            warmups=args.network_warmups,
            repetitions=args.network_repetitions,
        )
        query_case = evaluate_runs(
            "shawn_generic_query",
            query_runs,
            expected_exit_code=0,
            required_stdout=("CARTRIDGE: generic", "BENCH_ROWS=3"),
            forbidden_stdout=(
                "mechanistic evidence",
                "drug screening evidence",
                "model system evidence",
            ),
        )

        def demo_factory(index: int, warmup: bool) -> tuple[list[str], Callable[[dict[str, Any]], None]]:
            lane = "warmup" if warmup else "measure"
            db = work / f"demo-{lane}-{index}.sqlite3"
            db.unlink(missing_ok=True)

            def annotate(result: dict[str, Any]) -> None:
                result["stdout"] += f"\nBENCH_DB_CREATED={int(db.is_file())}\n"

            return [
                sys.executable,
                "-m",
                "evidencemap.refdb",
                "public-demo",
                "--db",
                str(db),
            ], annotate

        demo_runs = _measure(
            demo_factory,
            cwd=work,
            warmups=args.local_warmups,
            repetitions=args.local_repetitions,
        )
        demo_case = evaluate_runs(
            "shawn_public_demo",
            demo_runs,
            expected_exit_code=0,
            required_stdout=("PUBLIC_METADATA_DB_DEMO_OK", "BENCH_DB_CREATED=1"),
        )

        verify_db = work / "verify.sqlite3"
        seed = run_command(
            [
                sys.executable,
                "-m",
                "evidencemap.refdb",
                "public-demo",
                "--db",
                str(verify_db),
            ],
            cwd=work,
        )
        if seed["exit_code"] != 0 or not verify_db.is_file():
            raise RuntimeError("failed to seed the verification database")

        def verify_factory(index: int, warmup: bool) -> tuple[list[str], None]:
            return [
                sys.executable,
                "-m",
                "evidencemap.refdb",
                "verify",
                "--db",
                str(verify_db),
            ], None

        verify_runs = _measure(
            verify_factory,
            cwd=work,
            warmups=args.local_warmups,
            repetitions=args.local_repetitions,
        )
        verify_case = evaluate_runs(
            "shawn_verify_existing_database",
            verify_runs,
            expected_exit_code=0,
            required_stdout=("REFERENCE_DB_OK",),
        )

        def missing_factory(index: int, warmup: bool) -> tuple[list[str], Callable[[dict[str, Any]], None]]:
            lane = "warmup" if warmup else "measure"
            db = work / f"missing-{lane}-{index}.sqlite3"
            db.unlink(missing_ok=True)

            def annotate(result: dict[str, Any]) -> None:
                result["stderr"] += f"\nBENCH_DB_NOT_CREATED={int(not db.exists())}\n"

            return [
                sys.executable,
                "-m",
                "evidencemap.refdb",
                "verify",
                "--db",
                str(db),
            ], annotate

        missing_runs = _measure(
            missing_factory,
            cwd=work,
            warmups=0,
            repetitions=args.local_repetitions,
        )
        missing_case = evaluate_runs(
            "shawn_reject_missing_database",
            missing_runs,
            expected_exit_code=2,
            required_stderr=("database does not exist", "BENCH_DB_NOT_CREATED=1"),
        )

        cases = [query_case, demo_case, verify_case, missing_case]
        tool_versions: dict[str, str] = {
            "shawn_evidencemap": importlib.metadata.version("shawn-evidencemap")
        }

        if args.pyalex_python:
            pyalex_version_result = run_command(
                [
                    args.pyalex_python,
                    "-c",
                    "from importlib.metadata import version; print(version('pyalex'))",
                ],
                cwd=work,
            )
            if pyalex_version_result["exit_code"] != 0:
                raise RuntimeError("could not read the PyAlex version")
            tool_versions["pyalex"] = pyalex_version_result["stdout"].strip()

            def pyalex_factory(index: int, warmup: bool) -> tuple[list[str], None]:
                return _pyalex_command(args.pyalex_python, query), None

            pyalex_runs = _measure(
                pyalex_factory,
                cwd=work,
                warmups=args.network_warmups,
                repetitions=args.network_repetitions,
            )
            cases.append(
                evaluate_runs(
                    "pyalex_openalex_overlap_smoke",
                    pyalex_runs,
                    expected_exit_code=0,
                    required_stdout=("ROWS=3", "IDS_PRESENT=True"),
                )
            )

    return {
        "schema_version": "1",
        "measured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_release": args.source_release,
        "environment": _environment(),
        "tool_versions": tool_versions,
        "input": {
            "query": query,
            "query_sha256": _sha256_text(query),
            "requested_rows": 3,
        },
        "methodology": {
            "correctness_first": True,
            "network_timing_is_informational_only": True,
            "network_warmups": args.network_warmups,
            "network_repetitions": args.network_repetitions,
            "local_warmups": args.local_warmups,
            "local_repetitions": args.local_repetitions,
            "cross_tool_speed_ranking": False,
        },
        "cases": cases,
        "overall_pass": all(case["correctness"]["pass"] for case in cases),
        "claims_not_made": [
            "SHawn EvidenceMap is faster than PyAlex or any other project",
            "different-scope research tools form a speed leaderboard",
            "the project is production-ready or battle-tested",
            "maintainer-generated traffic is external adoption",
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the correctness-first SHawn EvidenceMap public benchmark."
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--query", default="open science metadata reproducibility"
    )
    parser.add_argument("--source-release", default="v0.2.3")
    parser.add_argument("--pyalex-python")
    parser.add_argument("--network-warmups", type=int, default=1)
    parser.add_argument("--network-repetitions", type=int, default=5)
    parser.add_argument("--local-warmups", type=int, default=3)
    parser.add_argument("--local-repetitions", type=int, default=10)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"PUBLIC_BENCHMARK_WRITTEN:{args.output}")
    print(f"PUBLIC_BENCHMARK_PASS={int(report['overall_pass'])}")
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
