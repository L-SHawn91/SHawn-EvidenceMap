from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Paper:
    id: str
    title: str
    abstract: str = ""
    year: int | None = None
    journal: str = ""
    authors: list[str] = field(default_factory=list)
    doi: str = ""
    pmcid: str = ""
    citations: int | None = None
    url: str = ""
    source: str = "pubmed"
    source_hits: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    support_sentence: str = ""


@dataclass(slots=True)
class EvidenceRow:
    claim: str
    evidence_type: str
    paper_id: str
    title: str
    year: int | None
    rationale: str
    support_sentence: str
    source_url: str


@dataclass(slots=True)
class EvidenceMap:
    query: str
    papers: list[Paper]
    rows: list[EvidenceRow]
    cartridge: str = "generic"
