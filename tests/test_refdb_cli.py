from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from evidencemap.refdb import ReferenceStore, build_synthetic_demo, render_demo_page


def _run_module(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_root = Path(__file__).resolve().parents[1] / "src"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(part for part in (str(src_root), existing) if part)
    return subprocess.run(
        [sys.executable, "-m", "evidencemap.refdb", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_refdb_cli_demo_verify_export_and_page(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.sqlite3"
    json_path = tmp_path / "nested" / "demo.json"
    html_path = tmp_path / "nested" / "site" / "index.html"

    demo = _run_module("demo", "--db", str(db_path), cwd=tmp_path)
    assert demo.returncode == 0, demo.stderr
    assert "REFERENCE_DB_DEMO_OK" in demo.stdout

    verify = _run_module("verify", "--db", str(db_path), cwd=tmp_path)
    assert verify.returncode == 0, verify.stderr
    assert verify.stdout.strip() == "REFERENCE_DB_OK"

    export = _run_module("export", "--db", str(db_path), "--out", str(json_path), cwd=tmp_path)
    assert export.returncode == 0, export.stderr
    assert json.loads(json_path.read_text())["counts"]["entities"] == 6

    page = _run_module("page", "--db", str(db_path), "--out", str(html_path), cwd=tmp_path)
    assert page.returncode == 0, page.stderr
    html = html_path.read_text()
    assert "Synthetic database reference demo" in html
    assert "Papers, datasets, claims, provenance, and relations" in html
    assert "No private corpus, manuscript, or operational database is included" in html


def test_render_demo_page_is_deterministic_and_escapes_content(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.sqlite3"
    with ReferenceStore(db_path) as store:
        build_synthetic_demo(store)
        store.upsert_entity(
            kind="claim",
            title="<script>alert('synthetic')</script>",
            identifiers={"demo_id": "escape-check"},
            metadata={"data_class": "synthetic"},
        )
        export_json = store.export_json()

    first = render_demo_page(export_json)
    second = render_demo_page(export_json)

    assert first == second
    assert "<script>" not in first
    assert "&lt;script&gt;alert(&#x27;synthetic&#x27;)&lt;/script&gt;" in first
    assert "Synthetic database reference demo" in first
    assert "DEMO-DS-001" in first
