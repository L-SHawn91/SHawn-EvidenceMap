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
    candidate_source_sentence: str = ""
    source_section: str = ""
    source_sentence_index: int | None = None

    @property
    def support_sentence(self) -> str:
        """Deprecated read alias for pre-0.3 integrations."""
        return self.candidate_source_sentence

    @support_sentence.setter
    def support_sentence(self, value: str) -> None:
        self.candidate_source_sentence = value


@dataclass(slots=True)
class EvidenceRow:
    claim: str
    evidence_type: str
    paper_id: str
    title: str
    year: int | None
    rationale: str
    candidate_source_sentence: str
    source_url: str
    evidence_relation: str = "candidate"
    source: str = ""
    doi: str = ""
    pmid: str = ""
    source_section: str = ""
    source_sentence_index: int | None = None

    @property
    def support_sentence(self) -> str:
        """Deprecated read alias; public serializers use candidate terminology."""
        return self.candidate_source_sentence


@dataclass(slots=True)
class StatementResult:
    status: str = "not_requested"
    reason: str = ""
    draft: str = ""
    reviewed_support_count: int = 0
    reviewed_contradict_count: int = 0


@dataclass(slots=True)
class EvidenceMap:
    query: str
    papers: list[Paper]
    rows: list[EvidenceRow]
    cartridge: str = "generic"
    claim: str = ""
    statement: StatementResult = field(default_factory=StatementResult)
