from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from .schema import SCHEMA_SQL, SCHEMA_VERSION

_ALLOWED_KINDS = frozenset({"paper", "dataset", "claim"})
_IDENTIFIER_PRIORITY = {"doi": 0, "pmid": 1, "accession": 2, "demo_id": 3}


class ReferenceStore:
    """Small SQLite store for reproducible evidence-reference examples."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        raw_path = str(db_path)
        self.db_path: str | Path = ":memory:" if raw_path == ":memory:" else Path(db_path)
        if isinstance(self.db_path, Path):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._migrated = False

    def __enter__(self) -> "ReferenceStore":
        self.migrate()
        return self

    def __exit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None:
        try:
            if exc is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        finally:
            self._conn.close()

    @property
    def schema_version(self) -> int:
        row = self._conn.execute("PRAGMA user_version").fetchone()
        return int(row[0]) if row else 0

    def migrate(self) -> int:
        """Apply the current reference schema to a fresh database."""
        current = self.schema_version
        if current > SCHEMA_VERSION:
            raise RuntimeError(
                f"database schema {current} is newer than supported schema {SCHEMA_VERSION}"
            )
        if current < SCHEMA_VERSION:
            self._conn.executescript(SCHEMA_SQL)
            self._conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self._conn.commit()
        self._migrated = True
        return self.schema_version

    def counts(self) -> dict[str, int]:
        self._ensure_schema()
        tables = ("entities", "identifiers", "relations", "provenance", "ingest_runs")
        return {
            table: int(self._conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in tables
        }

    def upsert_entity(
        self,
        *,
        kind: str,
        title: str,
        identifiers: Mapping[str, str],
        metadata: Mapping[str, Any] | None = None,
        **extra_metadata: Any,
    ) -> int:
        """Insert or enrich one entity, deduplicating by normalized identifiers."""
        self._ensure_schema()
        if kind not in _ALLOWED_KINDS:
            raise ValueError(f"unsupported entity kind: {kind}")

        normalized = self.normalize_identifiers(identifiers)
        if not normalized:
            raise ValueError("at least one identifier is required")

        matched_ids = self._find_entity_ids(normalized)
        if len(matched_ids) > 1:
            joined = ", ".join(str(entity_id) for entity_id in sorted(matched_ids))
            raise ValueError(f"identifier collision detected across entities: {joined}")

        incoming_metadata = dict(extra_metadata)
        if metadata:
            incoming_metadata.update(dict(metadata))

        if not matched_ids:
            metadata_text = self._dump_json(incoming_metadata)
            with self._conn:
                cursor = self._conn.execute(
                    "INSERT INTO entities (kind, title, metadata) VALUES (?, ?, ?)",
                    (kind, title or "", metadata_text),
                )
                if cursor.lastrowid is None:
                    raise RuntimeError("SQLite did not return an entity id")
                entity_id = int(cursor.lastrowid)
                self._insert_identifiers(entity_id, normalized)
            return entity_id

        entity_id = next(iter(matched_ids))
        existing = self._conn.execute(
            "SELECT kind, title, metadata FROM entities WHERE id = ?", (entity_id,)
        ).fetchone()
        if existing is None:
            raise RuntimeError(f"identifier points to missing entity {entity_id}")
        if existing["kind"] != kind:
            raise ValueError(
                f"entity kind mismatch for identifiers: {existing['kind']} != {kind}"
            )

        merged_metadata = self._load_json(existing["metadata"])
        merged_metadata.update(incoming_metadata)
        merged_title = existing["title"] or title or ""

        with self._conn:
            self._conn.execute(
                "UPDATE entities SET title = ?, metadata = ? WHERE id = ?",
                (merged_title, self._dump_json(merged_metadata), entity_id),
            )
            self._insert_identifiers(entity_id, normalized)
        return entity_id

    def add_relation(self, source_id: int, target_id: int, relation: str) -> None:
        self._ensure_schema()
        relation = relation.strip()
        if not relation:
            raise ValueError("relation must not be empty")
        with self._conn:
            self._conn.execute(
                "INSERT OR IGNORE INTO relations (source_id, target_id, relation) VALUES (?, ?, ?)",
                (source_id, target_id, relation),
            )

    def add_provenance(
        self,
        entity_id: int,
        source: str,
        source_ref: str,
        retrieved_at: str,
    ) -> None:
        self._ensure_schema()
        if not all(value.strip() for value in (source, source_ref, retrieved_at)):
            raise ValueError("source, source_ref, and retrieved_at are required")
        with self._conn:
            self._conn.execute(
                """
                INSERT OR IGNORE INTO provenance
                    (entity_id, source, source_ref, retrieved_at)
                VALUES (?, ?, ?, ?)
                """,
                (entity_id, source.strip(), source_ref.strip(), retrieved_at.strip()),
            )

    def record_ingest_run(
        self,
        *,
        run_id: str,
        source: str,
        started_at: str,
        finished_at: str,
        record_count: int,
    ) -> None:
        self._ensure_schema()
        if record_count < 0:
            raise ValueError("record_count must be non-negative")
        if not all(value.strip() for value in (run_id, source, started_at, finished_at)):
            raise ValueError("ingest-run fields must not be empty")
        with self._conn:
            self._conn.execute(
                """
                INSERT OR IGNORE INTO ingest_runs
                    (run_id, source, started_at, finished_at, record_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, source, started_at, finished_at, record_count),
            )

    def verify(self) -> list[str]:
        """Return integrity findings; an empty list means the store is clean."""
        self._ensure_schema()
        issues: list[str] = []

        integrity_rows = self._conn.execute("PRAGMA integrity_check").fetchall()
        failures = [str(row[0]) for row in integrity_rows if str(row[0]).lower() != "ok"]
        if failures:
            issues.append("integrity check failed: " + "; ".join(failures))

        foreign_key_rows = self._conn.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_rows:
            issues.append(f"foreign key violations: {len(foreign_key_rows)}")

        if self.schema_version != SCHEMA_VERSION:
            issues.append(
                f"schema version mismatch: {self.schema_version} != {SCHEMA_VERSION}"
            )

        collisions = self._conn.execute(
            """
            SELECT id_type, id_value, COUNT(*)
            FROM identifiers
            GROUP BY id_type, id_value
            HAVING COUNT(*) > 1
            """
        ).fetchall()
        if collisions:
            issues.append(f"duplicate identifiers: {len(collisions)}")
        return issues

    def export_json(self) -> str:
        """Return a canonical JSON representation independent of insertion order."""
        self._ensure_schema()
        entity_rows = self._load_entities()
        payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "counts": self.counts(),
            "entities": entity_rows,
            "relations": self._load_relations(),
            "provenance": self._load_provenance(),
            "ingest_runs": self._load_ingest_runs(),
        }
        return self._dump_json(payload)

    @classmethod
    def normalize_identifiers(cls, identifiers: Mapping[str, str]) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for raw_key, raw_value in identifiers.items():
            if raw_value is None:
                continue
            key = str(raw_key).strip().lower()
            value = str(raw_value).strip()
            if not key or not value:
                continue

            if key == "doi":
                value = value.lower()
                value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
                value = re.sub(r"^doi:\s*", "", value)
                value = value.lstrip("/")
            elif key == "pmid":
                value = re.sub(r"^pmid:\s*", "", value, flags=re.IGNORECASE)
            elif key == "accession":
                value = value.upper()

            if value:
                normalized[key] = value
        return normalized

    def _ensure_schema(self) -> None:
        if not self._migrated:
            self.migrate()

    def _find_entity_ids(self, identifiers: Mapping[str, str]) -> set[int]:
        entity_ids: set[int] = set()
        for id_type, id_value in identifiers.items():
            row = self._conn.execute(
                "SELECT entity_id FROM identifiers WHERE id_type = ? AND id_value = ?",
                (id_type, id_value),
            ).fetchone()
            if row is not None:
                entity_ids.add(int(row["entity_id"]))
        return entity_ids

    def _insert_identifiers(self, entity_id: int, identifiers: Mapping[str, str]) -> None:
        for id_type, id_value in identifiers.items():
            self._conn.execute(
                """
                INSERT OR IGNORE INTO identifiers (entity_id, id_type, id_value)
                VALUES (?, ?, ?)
                """,
                (entity_id, id_type, id_value),
            )

    def _load_entities(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id, kind, title, metadata FROM entities"
        ).fetchall()
        entities: list[dict[str, Any]] = []
        for row in rows:
            identifiers = {
                item["id_type"]: item["id_value"]
                for item in self._conn.execute(
                    """
                    SELECT id_type, id_value
                    FROM identifiers
                    WHERE entity_id = ?
                    ORDER BY id_type, id_value
                    """,
                    (row["id"],),
                ).fetchall()
            }
            entities.append(
                {
                    "kind": row["kind"],
                    "title": row["title"],
                    "identifiers": identifiers,
                    "metadata": self._load_json(row["metadata"]),
                }
            )
        return sorted(entities, key=self._entity_sort_key)

    def _load_relations(self) -> list[dict[str, str]]:
        references = self._entity_references()
        rows = self._conn.execute(
            "SELECT source_id, target_id, relation FROM relations"
        ).fetchall()
        relations = [
            {
                "source": references[int(row["source_id"])],
                "relation": row["relation"],
                "target": references[int(row["target_id"])],
            }
            for row in rows
        ]
        return sorted(
            relations,
            key=lambda row: (row["source"], row["relation"], row["target"]),
        )

    def _load_provenance(self) -> list[dict[str, str]]:
        references = self._entity_references()
        rows = self._conn.execute(
            "SELECT entity_id, source, source_ref, retrieved_at FROM provenance"
        ).fetchall()
        provenance = [
            {
                "entity": references[int(row["entity_id"])],
                "source": row["source"],
                "source_ref": row["source_ref"],
                "retrieved_at": row["retrieved_at"],
            }
            for row in rows
        ]
        return sorted(
            provenance,
            key=lambda row: (
                row["entity"],
                row["source"],
                row["source_ref"],
                row["retrieved_at"],
            ),
        )

    def _load_ingest_runs(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT run_id, source, started_at, finished_at, record_count
            FROM ingest_runs
            ORDER BY run_id
            """
        ).fetchall()
        return [
            {
                "run_id": row["run_id"],
                "source": row["source"],
                "started_at": row["started_at"],
                "finished_at": row["finished_at"],
                "record_count": int(row["record_count"]),
            }
            for row in rows
        ]

    def _entity_references(self) -> dict[int, str]:
        rows = self._conn.execute(
            "SELECT entity_id, id_type, id_value FROM identifiers"
        ).fetchall()
        grouped: dict[int, list[tuple[str, str]]] = {}
        for row in rows:
            grouped.setdefault(int(row["entity_id"]), []).append(
                (row["id_type"], row["id_value"])
            )

        references: dict[int, str] = {}
        for entity_id, identifiers in grouped.items():
            id_type, id_value = min(
                identifiers,
                key=lambda item: (
                    _IDENTIFIER_PRIORITY.get(item[0], 100),
                    item[0],
                    item[1],
                ),
            )
            references[entity_id] = f"{id_type}:{id_value}"
        return references

    @staticmethod
    def _entity_sort_key(entity: Mapping[str, Any]) -> tuple[Any, ...]:
        identifiers = entity.get("identifiers", {})
        return (
            tuple(sorted(identifiers.items())),
            entity.get("kind", ""),
            entity.get("title", ""),
            ReferenceStore._dump_json(entity.get("metadata", {})),
        )

    @staticmethod
    def _load_json(value: str) -> dict[str, Any]:
        try:
            parsed = json.loads(value or "{}")
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def _dump_json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
