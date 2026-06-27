from __future__ import annotations

from evidencemap.core.cartridge import EvidenceCartridge
from evidencemap.core.dedupe import dedupe_papers
from evidencemap.models import EvidenceMap, Paper


def build_with_cartridge(
    query: str,
    cartridge: EvidenceCartridge,
    limit: int = 20,
    ranking_mode: str = "recent",
) -> EvidenceMap:
    pool_size = max(30, limit * 3)
    fetched: list[Paper] = []
    try:
        fetched.extend(cartridge.search(query, pool_size))
    except Exception:
        # Public demo should degrade gracefully when sources rate-limit or time out.
        fetched = []

    deduped = dedupe_papers(fetched)
    try:
        cartridge.enrich(deduped)
    except Exception:
        pass

    papers = cartridge.rank(query, deduped, limit, ranking_mode)
    rows = [cartridge.paper_to_row(query, paper) for paper in papers]
    return EvidenceMap(query=query, papers=papers, rows=rows, cartridge=cartridge.id)
