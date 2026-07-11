from __future__ import annotations

from .cartridges import get_cartridge
from .cache import get_cached_map, set_cached_map
from .core.pipeline import build_with_cartridge
from .models import EvidenceMap


def build_evidence_map(
    query: str,
    limit: int = 20,
    ranking_mode: str = "recent",
    cartridge_id: str = "generic",
    use_cache: bool = True,
    cache_ttl_hours: float = 24,
) -> EvidenceMap:
    if use_cache:
        cached = get_cached_map(query, limit, ranking_mode, ttl_hours=cache_ttl_hours, cartridge_id=cartridge_id)
        if cached is not None:
            return cached

    cartridge = get_cartridge(cartridge_id)
    evidence_map = build_with_cartridge(query, cartridge, limit=limit, ranking_mode=ranking_mode)
    if use_cache:
        set_cached_map(evidence_map, limit=limit, ranking_mode=ranking_mode, cartridge_id=cartridge_id)
    return evidence_map
