from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import EvidenceMap, EvidenceRow, Paper, StatementResult


CACHE_VERSION = "v2"
DEFAULT_CACHE_PATH = Path.home() / ".cache" / "shawn-evidencemap" / "query_cache.json"


def get_cached_map(
    query: str,
    limit: int,
    ranking_mode: str,
    ttl_hours: float,
    cartridge_id: str = "generic",
    cache_path: Path = DEFAULT_CACHE_PATH,
) -> EvidenceMap | None:
    payload = load_cache(cache_path)
    item = payload.get(cache_key(query, limit, ranking_mode, cartridge_id))
    if not item:
        return None
    age_hours = (time.time() - float(item.get("ts", 0))) / 3600
    if age_hours > ttl_hours:
        return None
    return map_from_dict(item.get("data") or {})


def set_cached_map(
    evidence_map: EvidenceMap,
    limit: int,
    ranking_mode: str,
    cartridge_id: str = "generic",
    cache_path: Path = DEFAULT_CACHE_PATH,
) -> None:
    payload = load_cache(cache_path)
    payload[cache_key(evidence_map.query, limit, ranking_mode, cartridge_id)] = {
        "ts": time.time(),
        "data": asdict(evidence_map),
    }
    save_cache(payload, cache_path)


def cache_key(query: str, limit: int, ranking_mode: str, cartridge_id: str = "generic") -> str:
    raw = f"{CACHE_VERSION}|{cartridge_id}|{query.strip().lower()}|{limit}|{ranking_mode}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_cache(cache_path: Path) -> dict[str, Any]:
    try:
        if not cache_path.exists():
            return {}
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(payload: dict[str, Any], cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def map_from_dict(data: dict[str, Any]) -> EvidenceMap:
    paper_fields = set(Paper.__dataclass_fields__)
    row_fields = set(EvidenceRow.__dataclass_fields__)
    papers: list[Paper] = []
    for raw in data.get("papers", []):
        paper = dict(raw)
        if "candidate_source_sentence" not in paper and "support_sentence" in paper:
            paper["candidate_source_sentence"] = paper.pop("support_sentence")
        papers.append(Paper(**{key: value for key, value in paper.items() if key in paper_fields}))
    rows: list[EvidenceRow] = []
    for raw in data.get("rows", []):
        row = dict(raw)
        if "candidate_source_sentence" not in row and "support_sentence" in row:
            row["candidate_source_sentence"] = row.pop("support_sentence")
        rows.append(EvidenceRow(**{key: value for key, value in row.items() if key in row_fields}))
    statement_raw = data.get("statement") or {}
    statement = StatementResult(**statement_raw) if isinstance(statement_raw, dict) else StatementResult()
    return EvidenceMap(
        query=data.get("query", ""),
        papers=papers,
        rows=rows,
        cartridge=data.get("cartridge", "generic"),
        claim=data.get("claim", ""),
        statement=statement,
    )
