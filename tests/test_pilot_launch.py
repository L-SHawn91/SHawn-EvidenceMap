from __future__ import annotations

import json
from pathlib import Path

from evidencemap.refdb import ReferenceStore
from evidencemap.refdb.interchange import parse_csv


ROOT = Path(__file__).resolve().parents[1]


def test_pilot_demo_input_produces_advertised_audit_decisions(tmp_path: Path) -> None:
    records = parse_csv((ROOT / "examples/pilot/dirty_records.csv").read_text(encoding="utf-8"))
    with ReferenceStore(tmp_path / "pilot.sqlite3") as store:
        summary = store.ingest_records(
            records,
            run_id="pilot-demo-test",
            source="public_pilot_demo",
            started_at="2026-07-12T00:00:00Z",
            finished_at="2026-07-12T00:00:01Z",
        )
        issues = store.verify()
        payload = json.loads(store.export_json())

    assert summary == {"inserted": 3, "merged": 2, "rejected": 1}
    assert payload["counts"]["entities"] == 3
    assert issues == []


def test_pilot_page_links_executable_artifacts_and_safe_intake() -> None:
    page = (ROOT / "web/pilot.html").read_text(encoding="utf-8")
    homepage = (ROOT / "web/index.html").read_text(encoding="utf-8")
    summary = json.loads((ROOT / "web/assets/pilot-demo-summary.json").read_text(encoding="utf-8"))

    assert "assets/pilot-demo-60s.mp4" in page
    assert "assets/pilot-demo-summary.json" in page
    assert "discussions/9" in page
    assert "hosted private-data upload" in page.lower()
    assert "not proof that an identifier exists in an external registry" in page
    assert "pilot.html" in homepage
    assert summary["summary"] == {"inserted": 3, "merged": 2, "rejected": 1}
    assert summary["verification"] == "pass"


def test_public_launch_surfaces_do_not_publish_personal_email() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "docs/LAUNCH_PLAN.md",
        ROOT / "src/evidencemap/crossref.py",
        ROOT / "src/evidencemap/visual_report.py",
        ROOT / "web/index.html",
        ROOT / "web/pilot.html",
        ROOT / "web/sample.html",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    assert "@gmail.com" not in combined
    assert "mailto:" not in combined
