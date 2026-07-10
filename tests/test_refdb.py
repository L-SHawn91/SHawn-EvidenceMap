from __future__ import annotations

import json
from pathlib import Path

import pytest

from evidencemap.refdb import ReferenceStore, SCHEMA_VERSION, build_synthetic_demo


def test_migrate_fresh_database_and_rerun_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "reference.sqlite3"

    with ReferenceStore(db_path) as store:
        assert store.migrate() == SCHEMA_VERSION
        assert store.migrate() == SCHEMA_VERSION
        assert store.schema_version == SCHEMA_VERSION
        assert store.verify() == []


def test_upsert_entity_deduplicates_normalized_identifiers(tmp_path: Path) -> None:
    with ReferenceStore(tmp_path / "reference.sqlite3") as store:
        first = store.upsert_entity(
            kind="paper",
            title="Synthetic repair study",
            year=2025,
            identifiers={"doi": "https://doi.org/10.0000/SYNTHETIC.001", "pmid": "PMID:00000001"},
            metadata={"license": "synthetic"},
        )
        second = store.upsert_entity(
            kind="paper",
            title="",
            identifiers={"doi": "10.0000/synthetic.001"},
        )
        third = store.upsert_entity(
            kind="paper",
            title="Synthetic repair study",
            identifiers={"pmid": "00000001"},
        )

        assert first == second == third
        assert store.counts()["entities"] == 1
        exported = json.loads(store.export_json())
        assert exported["entities"][0]["title"] == "Synthetic repair study"
        assert exported["entities"][0]["identifiers"] == {
            "doi": "10.0000/synthetic.001",
            "pmid": "00000001",
        }


def test_upsert_rejects_identifier_collision_instead_of_merging(tmp_path: Path) -> None:
    with ReferenceStore(tmp_path / "reference.sqlite3") as store:
        store.upsert_entity(
            kind="paper",
            title="Synthetic paper A",
            identifiers={"doi": "10.0000/synthetic.a"},
        )
        store.upsert_entity(
            kind="paper",
            title="Synthetic paper B",
            identifiers={"pmid": "00000002"},
        )

        with pytest.raises(ValueError, match="identifier collision"):
            store.upsert_entity(
                kind="paper",
                title="Conflicting synthetic record",
                identifiers={
                    "doi": "10.0000/synthetic.a",
                    "pmid": "00000002",
                },
            )


def test_relations_cover_paper_dataset_claim_and_are_idempotent(tmp_path: Path) -> None:
    with ReferenceStore(tmp_path / "reference.sqlite3") as store:
        paper_id = store.upsert_entity(
            kind="paper",
            title="Synthetic organoid study",
            identifiers={"demo_id": "paper-001"},
        )
        dataset_id = store.upsert_entity(
            kind="dataset",
            title="Synthetic expression matrix",
            identifiers={"accession": "demo-ds-001"},
        )
        claim_id = store.upsert_entity(
            kind="claim",
            title="Synthetic treatment increases repair score",
            identifiers={"demo_id": "claim-001"},
        )

        store.add_relation(paper_id, dataset_id, "produces")
        store.add_relation(paper_id, dataset_id, "produces")
        store.add_relation(claim_id, paper_id, "supported_by")

        assert store.counts() == {
            "entities": 3,
            "identifiers": 3,
            "relations": 2,
            "provenance": 0,
            "ingest_runs": 0,
        }
        exported = json.loads(store.export_json())
        assert {(row["source"], row["relation"], row["target"]) for row in exported["relations"]} == {
            ("demo_id:claim-001", "supported_by", "demo_id:paper-001"),
            ("demo_id:paper-001", "produces", "accession:DEMO-DS-001"),
        }


def test_provenance_and_ingest_runs_are_deduplicated(tmp_path: Path) -> None:
    with ReferenceStore(tmp_path / "reference.sqlite3") as store:
        entity_id = store.upsert_entity(
            kind="dataset",
            title="Synthetic public registry entry",
            identifiers={"accession": "demo-ds-002"},
        )
        store.add_provenance(
            entity_id,
            source="synthetic_fixture",
            source_ref="example://dataset/demo-ds-002",
            retrieved_at="2026-01-01T00:00:00Z",
        )
        store.add_provenance(
            entity_id,
            source="synthetic_fixture",
            source_ref="example://dataset/demo-ds-002",
            retrieved_at="2026-01-01T00:00:00Z",
        )
        store.record_ingest_run(
            run_id="demo-run-001",
            source="synthetic_fixture",
            started_at="2026-01-01T00:00:00Z",
            finished_at="2026-01-01T00:00:01Z",
            record_count=1,
        )
        store.record_ingest_run(
            run_id="demo-run-001",
            source="synthetic_fixture",
            started_at="2026-01-01T00:00:00Z",
            finished_at="2026-01-01T00:00:01Z",
            record_count=1,
        )

        assert store.counts()["provenance"] == 1
        assert store.counts()["ingest_runs"] == 1
        assert store.verify() == []


def test_synthetic_demo_export_is_byte_deterministic(tmp_path: Path) -> None:
    first_path = tmp_path / "first.sqlite3"
    second_path = tmp_path / "second.sqlite3"

    with ReferenceStore(first_path) as first:
        build_synthetic_demo(first)
        first_export = first.export_json()
        assert first.verify() == []

    with ReferenceStore(second_path) as second:
        build_synthetic_demo(second)
        second_export = second.export_json()
        assert second.verify() == []

    assert first_export == second_export
    payload = json.loads(first_export)
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["counts"] == {
        "entities": 6,
        "identifiers": 6,
        "relations": 5,
        "provenance": 6,
        "ingest_runs": 1,
    }
    assert all(entity["metadata"].get("data_class") == "synthetic" for entity in payload["entities"])


def test_export_is_deterministic_across_insertion_order(tmp_path: Path) -> None:
    records = [
        ("paper", "Synthetic paper B", {"demo_id": "paper-b"}),
        ("dataset", "Synthetic dataset A", {"accession": "demo-ds-a"}),
        ("claim", "Synthetic claim C", {"demo_id": "claim-c"}),
    ]

    exports: list[str] = []
    for index, ordered in enumerate((records, list(reversed(records)))):
        with ReferenceStore(tmp_path / f"order-{index}.sqlite3") as store:
            for kind, title, identifiers in ordered:
                store.upsert_entity(
                    kind=kind,
                    title=title,
                    identifiers=identifiers,
                    metadata={"data_class": "synthetic"},
                )
            exports.append(store.export_json())

    assert exports[0] == exports[1]


def test_invalid_entity_kind_is_rejected(tmp_path: Path) -> None:
    with ReferenceStore(tmp_path / "reference.sqlite3") as store:
        with pytest.raises(ValueError, match="entity kind"):
            store.upsert_entity(
                kind="unsupported",
                title="Synthetic invalid entity",
                identifiers={"demo_id": "invalid-001"},
            )


def test_memory_database_is_supported() -> None:
    with ReferenceStore(":memory:") as store:
        build_synthetic_demo(store)
        assert store.counts()["entities"] == 6
        assert store.verify() == []


def test_verify_reports_foreign_key_corruption(tmp_path: Path) -> None:
    db_path = tmp_path / "corrupt.sqlite3"
    with ReferenceStore(db_path) as store:
        store.upsert_entity(
            kind="paper",
            title="Synthetic paper",
            identifiers={"demo_id": "paper-001"},
        )

    import sqlite3

    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute(
        "INSERT INTO relations (source_id, target_id, relation) VALUES (?, ?, ?)",
        (1, 999, "supported_by"),
    )
    connection.commit()
    connection.close()

    with ReferenceStore(db_path) as store:
        issues = store.verify()

    assert any("foreign key" in issue.lower() for issue in issues)
