from __future__ import annotations

SCHEMA_VERSION = 2

SCHEMA_V1_SQL = """
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('paper', 'dataset', 'claim')),
    title TEXT NOT NULL DEFAULT '',
    metadata TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS identifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    id_type TEXT NOT NULL,
    id_value TEXT NOT NULL,
    UNIQUE(id_type, id_value)
);

CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    target_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relation TEXT NOT NULL,
    UNIQUE(source_id, target_id, relation)
);

CREATE TABLE IF NOT EXISTS provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    UNIQUE(entity_id, source, source_ref, retrieved_at)
);

CREATE TABLE IF NOT EXISTS ingest_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    record_count INTEGER NOT NULL CHECK (record_count >= 0)
);
"""

SCHEMA_V2_SQL = """
ALTER TABLE ingest_runs
    ADD COLUMN expects_events INTEGER NOT NULL DEFAULT 0
    CHECK (expects_events IN (0, 1));

CREATE TABLE IF NOT EXISTS ingest_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES ingest_runs(run_id) ON DELETE CASCADE,
    record_index INTEGER NOT NULL CHECK (record_index >= 0),
    input_ref TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('inserted', 'merged', 'rejected')),
    entity_ref TEXT,
    detail TEXT NOT NULL DEFAULT '{}',
    UNIQUE(run_id, record_index)
);
CREATE INDEX IF NOT EXISTS idx_ingest_events_run_id ON ingest_events(run_id);
"""

MIGRATIONS = {
    0: SCHEMA_V1_SQL,
    1: SCHEMA_V2_SQL,
}

# Compatibility export for callers that need the complete fresh-database schema.
SCHEMA_SQL = SCHEMA_V1_SQL + "\n" + SCHEMA_V2_SQL
