from __future__ import annotations

import json
from pathlib import Path
import sqlite3

import pytest

from evidencemap.refdb.interchange import (
    InterchangeError,
    InterchangeRecord,
    export_bibtex,
    export_csv,
    export_ris,
    parse_bibtex,
    parse_csv,
    parse_identifiers,
    parse_ris,
)
from evidencemap.refdb.schema import SCHEMA_V1_SQL
from evidencemap.refdb.store import ReferenceStore


def test_identifier_input_normalizes_supported_types_without_guessing_accessions() -> None:
    records = parse_identifiers(
        """
        doi:https://doi.org/10.1000/ABC.1
        PMID:12345
        https://openalex.org/W98765
        accession:GSE1234
        """
    )

    assert [record.kind for record in records] == ["paper", "paper", "paper", "dataset"]
    assert [record.identifiers for record in records] == [
        {"doi": "10.1000/abc.1"},
        {"pmid": "12345"},
        {"openalex": "W98765"},
        {"accession": "GSE1234"},
    ]

    try:
        parse_identifiers("GSE9999\n")
    except InterchangeError as exc:
        assert "explicit accession:" in str(exc)
    else:
        raise AssertionError("bare accession must not be guessed")


def test_csv_input_maps_metadata_and_requires_an_identifier() -> None:
    records = parse_csv(
        "title,doi,pmid,openalex_id,accession,year,journal,authors,url\n"
        'A public paper,10.1000/ABC.2,,, ,2025,Journal A,"Kim; Lee",https://example.org/a\n'
        "A public dataset,,,,GSE2000,2024,,,https://example.org/d\n"
    )

    assert records[0].kind == "paper"
    assert records[0].title == "A public paper"
    assert records[0].identifiers == {"doi": "10.1000/abc.2"}
    assert records[0].metadata == {
        "authors": ["Kim", "Lee"],
        "journal": "Journal A",
        "url": "https://example.org/a",
        "year": 2025,
    }
    assert records[1].kind == "dataset"
    assert records[1].identifiers == {"accession": "GSE2000"}

    try:
        parse_csv("title,year\nNo identifier,2025\n")
    except InterchangeError as exc:
        assert "identifier" in str(exc)
    else:
        raise AssertionError("CSV row without an identifier must fail")


def test_real_v1_database_migrates_to_v2_without_losing_entities(tmp_path: Path) -> None:
    db_path = tmp_path / "v1.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.executescript(SCHEMA_V1_SQL)
    connection.execute(
        "INSERT INTO entities (kind, title, metadata) VALUES ('paper', 'Existing', '{}')"
    )
    connection.execute(
        "INSERT INTO identifiers (entity_id, id_type, id_value) VALUES (1, 'pmid', '123')"
    )
    connection.execute("PRAGMA user_version = 1")
    connection.commit()
    connection.close()

    with ReferenceStore(db_path) as store:
        assert store.schema_version == 2
        assert store.verify() == []
        payload = json.loads(store.export_json())

    assert payload["entities"][0]["title"] == "Existing"
    assert payload["counts"]["ingest_events"] == 0


def test_ingest_records_records_insert_merge_and_collision_rejection(tmp_path: Path) -> None:
    records = parse_csv(
        "title,doi,pmid,openalex_id,accession,year,journal,authors,url\n"
        "Inserted,10.1000/new,,,,2025,,,,\n"
        "Collision,10.1000/a,200,,,,,,,\n"
    )
    with ReferenceStore(tmp_path / "ingest.sqlite3") as store:
        store.upsert_entity(kind="paper", title="A", identifiers={"doi": "10.1000/a"})
        store.upsert_entity(kind="paper", title="B", identifiers={"pmid": "200"})

        summary = store.ingest_records(
            records,
            run_id="csv-sha256-test",
            source="user_csv",
            started_at="2026-07-11T00:00:00Z",
            finished_at="2026-07-11T00:00:01Z",
        )
        second = store.ingest_records(
            parse_csv(
                "title,doi,pmid,openalex_id,accession,year,journal,authors,url\n"
                "Richer title,10.1000/new,,,,2026,Journal B,,,\n"
            ),
            run_id="csv-sha256-test-2",
            source="user_csv",
            started_at="2026-07-11T00:00:02Z",
            finished_at="2026-07-11T00:00:03Z",
        )
        repeated = store.ingest_records(
            records,
            run_id="csv-sha256-test",
            source="user_csv",
            started_at="2026-07-11T00:00:04Z",
            finished_at="2026-07-11T00:00:05Z",
        )
        payload = json.loads(store.export_json())

    assert summary == {"inserted": 1, "merged": 0, "rejected": 1}
    assert repeated == summary
    assert second == {"inserted": 0, "merged": 1, "rejected": 0}
    assert payload["counts"]["ingest_events"] == 3
    assert payload["counts"]["provenance"] == 2
    assert {(row["source"], row["source_ref"]) for row in payload["provenance"]} == {
        ("user_csv", "csv-row:2"),
    }
    assert [event["action"] for event in payload["ingest_events"]] == [
        "inserted",
        "rejected",
        "merged",
    ]
    rejected = payload["ingest_events"][1]
    assert rejected["entity_ref"] is None
    assert "identifier collision" in rejected["detail"]["reason"]


def test_unexpected_ingest_error_rolls_back_the_entire_run(tmp_path: Path) -> None:
    with ReferenceStore(tmp_path / "atomic.sqlite3") as store:
        with pytest.raises(TypeError):
            store.ingest_records(
                [
                    InterchangeRecord(
                        kind="paper",
                        title="Cannot serialize",
                        identifiers={"doi": "10.1000/atomic"},
                        metadata={"unsupported": {1, 2}},
                        input_ref="test:1",
                    )
                ],
                run_id="atomic-test",
                source="test",
                started_at="2026-07-11T00:00:00Z",
                finished_at="2026-07-11T00:00:01Z",
            )

        assert store.counts() == {
            "entities": 0,
            "identifiers": 0,
            "relations": 0,
            "provenance": 0,
            "ingest_runs": 0,
            "ingest_events": 0,
        }


def test_ris_subset_parses_repeated_authors_and_rejects_unterminated_records() -> None:
    records = parse_ris(
        "TY  - JOUR\n"
        "TI  - Public study\n"
        "AU  - Kim, A\n"
        "AU  - Lee, B\n"
        "PY  - 2025\n"
        "JO  - Journal A\n"
        "DO  - 10.1000/RIS.1\n"
        "UR  - https://example.org/ris\n"
        "ER  -\n"
    )
    assert records[0].title == "Public study"
    assert records[0].identifiers == {"doi": "10.1000/ris.1"}
    assert records[0].metadata["authors"] == ["Kim, A", "Lee, B"]
    assert records[0].metadata["year"] == 2025

    try:
        parse_ris("TY  - JOUR\nTI  - Broken\nDO  - 10.1000/broken\n")
    except InterchangeError as exc:
        assert "ER" in str(exc)
    else:
        raise AssertionError("unterminated RIS must fail")


def test_bibtex_subset_parses_article_and_rejects_string_macros() -> None:
    records = parse_bibtex(
        '@article{public2025,\n'
        '  title = {Public study},\n'
        '  author = {Kim, A and Lee, B},\n'
        '  year = {2025},\n'
        '  journal = {Journal A},\n'
        '  doi = {10.1000/BIB.1},\n'
        '  openalex = {W12345},\n'
        '  url = {https://example.org/bib}\n'
        '}\n'
    )
    assert records[0].identifiers == {"doi": "10.1000/bib.1", "openalex": "W12345"}
    assert records[0].metadata["authors"] == ["Kim, A", "Lee, B"]
    assert records[0].metadata["journal"] == "Journal A"

    try:
        parse_bibtex('@string{j = "Journal"}\n')
    except InterchangeError as exc:
        assert "@string" in str(exc).lower()
    else:
        raise AssertionError("BibTeX string macros must fail")


def test_standard_exports_are_deterministic_and_roundtrip() -> None:
    records = parse_csv(
        "title,doi,pmid,openalex_id,accession,year,journal,authors,url\n"
        '"{C}++ Method #1",10.1000/B,,,,2024,Journal B,"Lee; Kim",https://example.org/b\n'
        "Paper A,,100,W100,,2025,Journal A,Park,https://example.org/a\n"
    )
    entities = [
        {
            "kind": record.kind,
            "title": record.title,
            "identifiers": record.identifiers,
            "metadata": record.metadata,
        }
        for record in reversed(records)
    ]

    csv_text = export_csv(entities)
    ris_text = export_ris(entities)
    bibtex_text = export_bibtex(entities)

    assert csv_text == export_csv(list(reversed(entities)))
    assert ris_text == export_ris(list(reversed(entities)))
    assert bibtex_text == export_bibtex(list(reversed(entities)))
    assert "\r\n" not in csv_text
    assert "AN  - pmid:100" in ris_text
    assert "AN  - openalex:W100" in ris_text
    assert "@article{doi_10_1000_b" in bibtex_text

    assert export_csv(
        [
            {
                "kind": record.kind,
                "title": record.title,
                "identifiers": record.identifiers,
                "metadata": record.metadata,
            }
            for record in parse_csv(csv_text)
        ]
    ) == csv_text
    assert export_ris(
        [
            {
                "kind": record.kind,
                "title": record.title,
                "identifiers": record.identifiers,
                "metadata": record.metadata,
            }
            for record in parse_ris(ris_text)
        ]
    ) == ris_text
    assert export_bibtex(
        [
            {
                "kind": record.kind,
                "title": record.title,
                "identifiers": record.identifiers,
                "metadata": record.metadata,
            }
            for record in parse_bibtex(bibtex_text)
        ]
    ) == bibtex_text
