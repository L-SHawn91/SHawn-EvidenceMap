from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import EvidenceMap, EvidenceRow, Paper


CACHE_VERSION = "v1"
DEFAULT_CACHE_PATH = Path.home() / ".cache" / "shawn-evidencemap" / "query_cache.json"


def get_cached_map(
    query: str,
    limit: int,
    ranking_mode: str,
    ttl_hours: float,
    cartridge_id: str = "bio",
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
    cartridge_id: str = "bio",
    cache_path: Path = DEFAULT_CACHE_PATH,
) -> None:
    payload = load_cache(cache_path)
    payload[cache_key(evidence_map.query, limit, ranking_mode, cartridge_id)] = {
        "ts": time.time(),
        "data": asdict(evidence_map),
    }
    save_cache(payload, cache_path)


def cache_key(query: str, limit: int, ranking_mode: str, cartridge_id: str = "bio") -> str:
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
    papers = [Paper(**paper) for paper in data.get("papers", [])]
    rows = [EvidenceRow(**row) for row in data.get("rows", [])]
    return EvidenceMap(query=data.get("query", ""), papers=papers, rows=rows, cartridge=data.get("cartridge", "bio"))
