from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from evidencemap.refdb import ReferenceStore, build_public_metadata_demo, render_demo_page


EXPECTED_PAPER_TITLE = "Imbalanced Host Response to SARS-CoV-2 Drives Development of COVID-19."
EXPECTED_DATASET_TITLE = "Transcriptional response to SARS-CoV-2 infection"
EXPECTED_LINKAGE = "NCBI GEO links GSE147507 to PMID 32416070."


def _build_export(path: Path) -> str:
    with ReferenceStore(path) as store:
        build_public_metadata_demo(store)
        assert store.verify() == []
        return store.export_json()


def test_public_metadata_demo_is_deterministic_and_metadata_only(tmp_path: Path) -> None:
    first = _build_export(tmp_path / "first.sqlite3")
    second = _build_export(tmp_path / "second.sqlite3")

    assert first == second
    payload = json.loads(first)
    assert payload["counts"] == {
        "entities": 3,
        "identifiers": 4,
        "relations": 3,
        "provenance": 3,
        "ingest_runs": 1,
    }

    entities = {entity["kind"]: entity for entity in payload["entities"]}
    assert entities["paper"]["title"] == EXPECTED_PAPER_TITLE
    assert entities["paper"]["identifiers"] == {
        "doi": "10.1016/j.cell.2020.04.026",
        "pmid": "32416070",
    }
    assert entities["dataset"]["title"] == EXPECTED_DATASET_TITLE
    assert entities["dataset"]["identifiers"] == {"accession": "GSE147507"}
    assert entities["claim"]["title"] == EXPECTED_LINKAGE
    assert all(entity["metadata"]["data_class"] == "public_metadata" for entity in entities.values())

    serialized = json.dumps(payload).lower()
    assert "abstract" not in serialized
    assert "full_text" not in serialized
    assert "private" not in serialized
    assert "patient" not in serialized
    assert all(row["source_ref"].startswith("https://") for row in payload["provenance"])


def test_public_metadata_page_states_registry_linkage_boundary(tmp_path: Path) -> None:
    page = render_demo_page(_build_export(tmp_path / "public.sqlite3"))

    assert "Public metadata linkage demo" in page
    assert "Registry linkage only" in page
    assert "does not independently validate a scientific conclusion" in page
    assert EXPECTED_PAPER_TITLE in page
    assert EXPECTED_DATASET_TITLE in page
    assert EXPECTED_LINKAGE in page
    assert "5-minute pilot" in page
    assert 'href="https://pubmed.ncbi.nlm.nih.gov/32416070/"' in page
    assert 'href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE147507"' in page
    assert 'rel="noopener noreferrer"' in page


def test_public_demo_cli_builds_and_exports_without_network(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "public.sqlite3"
    json_path = tmp_path / "nested" / "reference.json"
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}

    built = subprocess.run(
        [sys.executable, "-m", "evidencemap.refdb", "public-demo", "--db", str(db_path)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert built.returncode == 0, built.stderr
    assert "PUBLIC_METADATA_DB_DEMO_OK" in built.stdout

    exported = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencemap.refdb",
            "export",
            "--db",
            str(db_path),
            "--out",
            str(json_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert exported.returncode == 0, exported.stderr
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["counts"]["entities"] == 3
