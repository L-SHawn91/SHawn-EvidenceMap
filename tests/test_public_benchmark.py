from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "public_benchmark.py"
SPEC = importlib.util.spec_from_file_location("public_benchmark", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
benchmark = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(benchmark)


def test_summarize_numbers_reports_raw_median_and_range() -> None:
    assert benchmark.summarize_numbers([0.4, 0.1, 0.3, 0.2]) == {
        "median": 0.25,
        "min": 0.1,
        "max": 0.4,
        "raw": [0.4, 0.1, 0.3, 0.2],
    }


def test_summarize_numbers_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one"):
        benchmark.summarize_numbers([])


def test_run_command_captures_process_evidence(tmp_path: Path) -> None:
    result = benchmark.run_command(
        [
            sys.executable,
            "-c",
            "import sys; print('ROWS=3'); print('warning', file=sys.stderr)",
        ],
        cwd=tmp_path,
    )

    assert result["exit_code"] == 0
    assert result["stdout"] == "ROWS=3\n"
    assert result["stderr"] == "warning\n"
    assert result["wall_seconds"] >= 0
    assert result["peak_rss_kb"] > 0


def test_evaluate_runs_prioritizes_correctness_over_speed() -> None:
    runs = [
        {
            "exit_code": 0,
            "stdout": "CARTRIDGE: generic\nROWS=3\n",
            "stderr": "",
            "wall_seconds": 0.01,
            "peak_rss_kb": 1000,
        },
        {
            "exit_code": 0,
            "stdout": "CARTRIDGE: bio\nROWS=3\n",
            "stderr": "",
            "wall_seconds": 0.001,
            "peak_rss_kb": 900,
        },
    ]

    report = benchmark.evaluate_runs(
        "generic_query",
        runs,
        expected_exit_code=0,
        required_stdout=("CARTRIDGE: generic", "ROWS=3"),
        forbidden_stdout=("CARTRIDGE: bio",),
    )

    assert report["correctness"]["pass"] is False
    assert report["correctness"]["failed_runs"] == [2]
    assert report["timing_is_informational"] is True
    assert report["wall_seconds"]["median"] == pytest.approx(0.0055)
    assert "stdout" not in report["samples"][0]
    assert len(report["samples"][0]["stdout_sha256"]) == 64


def test_evaluate_runs_accepts_expected_negative_exit() -> None:
    report = benchmark.evaluate_runs(
        "missing_database",
        [
            {
                "exit_code": 2,
                "stdout": "",
                "stderr": "REFERENCE_DB_ERROR: database does not exist: missing.sqlite3\n",
                "wall_seconds": 0.02,
                "peak_rss_kb": 800,
            }
        ],
        expected_exit_code=2,
        required_stderr=("database does not exist",),
    )

    assert report["correctness"]["pass"] is True
    assert report["correctness"]["failed_runs"] == []


def test_published_benchmark_result_is_passing_and_public_safe() -> None:
    result_path = (
        Path(__file__).parents[1]
        / "benchmarks"
        / "results"
        / "2026-07-11-v0.2.3.json"
    )
    raw = result_path.read_text()
    result = json.loads(raw)

    assert result["schema_version"] == "1"
    assert result["source_release"] == "v0.2.3"
    assert result["tool_versions"]["shawn_evidencemap"] == "0.2.3"
    assert result["overall_pass"] is True
    assert result["methodology"]["cross_tool_speed_ranking"] is False
    assert result["environment"]["openalex_api_key_present"] is False
    assert all(case["correctness"]["pass"] for case in result["cases"])
    assert "/home/" not in raw
    assert "/tmp/" not in raw
    assert "hostname\"" not in raw
