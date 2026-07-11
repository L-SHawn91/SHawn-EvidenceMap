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


def test_refdb_read_commands_reject_missing_database_without_creating_file(tmp_path: Path) -> None:
    commands = (
        ("verify",),
        ("export", "--out", str(tmp_path / "missing.json")),
        ("page", "--out", str(tmp_path / "missing.html")),
    )

    for index, command in enumerate(commands):
        db_path = tmp_path / f"missing-{index}.sqlite3"
        result = _run_module(*command, "--db", str(db_path), cwd=tmp_path)

        assert result.returncode != 0
        assert "database does not exist" in result.stderr
        assert not db_path.exists()


def test_render_demo_page_is_deterministic_and_escapes_content(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.sqlite3"
    with ReferenceStore(db_path) as store:
        build_synthetic_demo(store)
        entity_id = store.upsert_entity(
            kind="claim",
            title="<script>alert('synthetic')</script>",
            identifiers={"demo_id": "escape-check"},
            metadata={"data_class": "synthetic"},
        )
        store.add_provenance(
            entity_id,
            source="synthetic_fixture",
            source_ref="javascript:alert('unsafe')",
            retrieved_at="2026-01-01T00:00:00Z",
        )
        export_json = store.export_json()

    first = render_demo_page(export_json)
    second = render_demo_page(export_json)

    assert first == second
    assert "<script>" not in first
    assert "&lt;script&gt;alert(&#x27;synthetic&#x27;)&lt;/script&gt;" in first
    assert 'href="javascript:' not in first
    assert "javascript:alert(&#x27;unsafe&#x27;)" in first
    assert "Synthetic database reference demo" in first
    assert "DEMO-DS-001" in first


def test_refdb_cli_ingest_and_standard_exports(tmp_path: Path) -> None:
    input_path = tmp_path / "records.csv"
    db_path = tmp_path / "bridge.sqlite3"
    input_path.write_text(
        "title,doi,pmid,openalex_id,accession,year,journal,authors,url\n"
        'Paper,10.1000/CLI,,,,2025,Journal,"Kim; Lee",https://example.org/p\n'
        "Dataset,,,,GSE3000,2024,,,https://example.org/d\n",
        encoding="utf-8",
    )

    ingest = _run_module(
        "ingest",
        "--db",
        str(db_path),
        "--input",
        str(input_path),
        "--format",
        "csv",
        "--recorded-at",
        "2026-07-11T00:00:00Z",
        cwd=tmp_path,
    )
    assert ingest.returncode == 0, ingest.stderr
    assert "REFERENCE_DB_INGEST_OK inserted=2 merged=0 rejected=0" in ingest.stdout

    for output_format, suffix, marker in (
        ("json", "json", '"ingest_events"'),
        ("csv", "csv", "title,doi,pmid,openalex_id"),
        ("ris", "ris", "TY  - JOUR"),
        ("bibtex", "bib", "@article{doi_10_1000_cli"),
    ):
        output_path = tmp_path / f"records.{suffix}"
        result = _run_module(
            "export",
            "--db",
            str(db_path),
            "--out",
            str(output_path),
            "--format",
            output_format,
            cwd=tmp_path,
        )
        assert result.returncode == 0, result.stderr
        assert marker in output_path.read_text(encoding="utf-8")


def test_refdb_cli_rejects_malformed_input_before_creating_database(tmp_path: Path) -> None:
    input_path = tmp_path / "broken.ris"
    db_path = tmp_path / "must-not-exist.sqlite3"
    input_path.write_text("TY  - JOUR\nTI  - Missing terminator\n", encoding="utf-8")

    result = _run_module(
        "ingest",
        "--db",
        str(db_path),
        "--input",
        str(input_path),
        "--format",
        "ris",
        cwd=tmp_path,
    )

    assert result.returncode != 0
    assert "REFERENCE_DB_INPUT_ERROR" in result.stderr
    assert not db_path.exists()
