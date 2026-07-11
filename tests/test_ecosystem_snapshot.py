from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "benchmarks" / "results" / "2026-07-11-ecosystem-snapshot.json"
REPORT = ROOT / "docs" / "ECOSYSTEM_COMPARISON_2026-07-11.md"
PUBLIC_BENCHMARK = ROOT / "docs" / "PUBLIC_BENCHMARK_2026-07-11.md"


def load_snapshot() -> dict:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_ecosystem_snapshot_has_declared_scope_and_no_speed_ranking() -> None:
    data = load_snapshot()

    assert data["schema_version"] == 1
    assert data["snapshot_date"] == "2026-07-11"
    assert data["methodology"]["cross_project_performance_ranking"] is False
    assert data["directory_census"]["parsed_tools"] == 290
    assert data["directory_census"]["keyword_filtered_adjacent_count"] == len(
        data["directory_census"]["keyword_filtered_names"]
    )
    assert data["directory_census"]["keyword_filter_terms"]
    assert "Purposeful strategic sample" in data["directory_census"][
        "core_repository_selection"
    ]


def test_repository_snapshot_is_unique_public_and_includes_target() -> None:
    data = load_snapshot()
    repositories = data["repositories"]
    canonical = [row["canonical_repo"] for row in repositories]

    assert len(repositories) == 39
    assert len(canonical) == len(set(canonical))
    assert all(row["url"].startswith("https://github.com/") for row in repositories)
    assert all("/home/" not in json.dumps(row) for row in repositories)
    assert all("/tmp/" not in json.dumps(row) for row in repositories)

    target = next(
        row for row in repositories if row["canonical_repo"] == "L-SHawn91/SHawn-EvidenceMap"
    )
    assert target["lane"] == "target"
    assert target["latest_release"] == "v0.2.3"


def test_onboarding_smoke_is_discovery_only() -> None:
    data = load_snapshot()
    smoke = data["onboarding_smoke"]

    assert {row["package"] for row in smoke} == {
        "shawn-evidencemap",
        "asreview",
        "colrev",
        "metascreener",
        "paper-qa",
    }
    assert all(row["install_exit"] == 0 for row in smoke)
    assert all(row["help_exit"] == 0 for row in smoke)
    assert "informational" in data["methodology"]["timing_warning"].lower()


def test_report_matches_snapshot_and_uses_canonical_citation_js_repository() -> None:
    report = REPORT.read_text(encoding="utf-8")
    public_benchmark = PUBLIC_BENCHMARK.read_text(encoding="utf-8")

    assert "**290**" in report
    assert "**116**" in report
    assert "**39 public GitHub repositories**" in report
    assert "official-documentation assessments, not functional verification" in report
    assert "https://github.com/citation-js/citation-js" in report
    assert "https://github.com/citation-js/citation-js" in public_benchmark
    assert "https://github.com/larsgw/citation.js" not in report
    assert "https://github.com/larsgw/citation.js" not in public_benchmark
