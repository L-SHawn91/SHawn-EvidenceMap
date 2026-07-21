from __future__ import annotations

from typing import Any

from .cartridges import get_cartridge
from .cache import get_cached_map, set_cached_map
from .core.pipeline import build_with_cartridge
from .models import EvidenceMap, StatementResult
from .review import ReviewFileError, apply_review_payload, build_statement


def build_evidence_map(
    query: str,
    limit: int = 20,
    ranking_mode: str = "recent",
    cartridge_id: str = "generic",
    use_cache: bool = True,
    cache_ttl_hours: float = 24,
    claim: str = "",
    review_payload: dict[str, Any] | None = None,
    draft_statement: bool = False,
) -> EvidenceMap:
    normalized_claim = claim.strip()
    if review_payload is not None and not normalized_claim:
        raise ReviewFileError("a claim is required when applying review relations")

    evidence_map = None
    if use_cache:
        evidence_map = get_cached_map(query, limit, ranking_mode, ttl_hours=cache_ttl_hours, cartridge_id=cartridge_id)

    if evidence_map is None:
        cartridge = get_cartridge(cartridge_id)
        evidence_map = build_with_cartridge(query, cartridge, limit=limit, ranking_mode=ranking_mode)
        if use_cache:
            # Cache public search candidates only; local review decisions are applied below.
            set_cached_map(evidence_map, limit=limit, ranking_mode=ranking_mode, cartridge_id=cartridge_id)

    evidence_map.claim = normalized_claim
    evidence_map.statement = StatementResult()
    for row in evidence_map.rows:
        row.claim = evidence_map.claim
        row.evidence_relation = "candidate"
    if review_payload is not None:
        apply_review_payload(evidence_map, review_payload)
    if draft_statement:
        evidence_map.statement = build_statement(evidence_map)
    return evidence_map
