from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from evidencemap.models import EvidenceRow, Paper


SearchFn = Callable[[str, int], list[Paper]]
EnrichFn = Callable[[list[Paper]], None]
RankFn = Callable[[str, list[Paper], int, str], list[Paper]]
RowFn = Callable[[str, Paper], EvidenceRow]


@dataclass(frozen=True, slots=True)
class EvidenceCartridge:
    id: str
    name: str
    description: str
    status: str
    sources: tuple[str, ...]
    evidence_labels: tuple[str, ...]
    search: SearchFn
    enrich: EnrichFn
    rank: RankFn
    paper_to_row: RowFn
