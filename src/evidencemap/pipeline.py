from __future__ import annotations

import re

from .cache import get_cached_map, set_cached_map
from .europepmc import enrich_papers_from_europepmc, search_europepmc
from .models import EvidenceMap, EvidenceRow, Paper
from .pubmed import search_pubmed
from .quality_gate import rank_public_papers


THEME_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("model system evidence", re.compile(r"\borganoid|assembloid|3d culture|model\b", re.I)),
    ("mechanistic evidence", re.compile(r"\bmechanism|pathway|signaling|gene|protein|transcript", re.I)),
    ("clinical or patient evidence", re.compile(r"\bpatient|clinical|cohort|trial|diagnosis", re.I)),
    ("omics evidence", re.compile(r"\bsingle-cell|scrna|rna-seq|transcriptom|proteom|metabolom", re.I)),
]


def build_evidence_map(
    query: str,
    limit: int = 20,
    ranking_mode: str = "recent",
    use_cache: bool = True,
    cache_ttl_hours: float = 24,
) -> EvidenceMap:
    if use_cache:
        cached = get_cached_map(query, limit, ranking_mode, ttl_hours=cache_ttl_hours)
        if cached is not None:
            return cached

    pool_size = max(30, limit * 3)
    fetched: list[Paper] = []
    for source_fn in (search_pubmed, search_europepmc):
        try:
            fetched.extend(source_fn(query, limit=pool_size))
        except Exception:
            # Public demo should degrade gracefully when a source rate-limits or times out.
            continue
    deduped = dedupe_papers(fetched)
    try:
        enrich_papers_from_europepmc(deduped)
    except Exception:
        pass
    papers = rank_public_papers(query, deduped, limit=limit, ranking_mode=ranking_mode)
    rows = [_paper_to_row(query, paper) for paper in papers]
    evidence_map = EvidenceMap(query=query, papers=papers, rows=rows)
    if use_cache:
        set_cached_map(evidence_map, limit=limit, ranking_mode=ranking_mode)
    return evidence_map


def _paper_to_row(query: str, paper: Paper) -> EvidenceRow:
    text = f"{paper.title}\n{paper.abstract}"
    evidence_type = _classify(text)
    rationale = _rationale(query, text, paper)
    claim = f"Evidence related to: {query}"
    return EvidenceRow(
        claim=claim,
        evidence_type=evidence_type,
        paper_id=paper.id,
        title=paper.title,
        year=paper.year,
        rationale=rationale,
        support_sentence=paper.support_sentence,
        source_url=paper.url,
    )


def _classify(text: str) -> str:
    for label, pattern in THEME_RULES:
        if pattern.search(text):
            return label
    return "background evidence"


def _rationale(query: str, text: str, paper: Paper) -> str:
    query_terms = [t.lower() for t in re.findall(r"[A-Za-z0-9-]{4,}", query)]
    lowered = text.lower()
    hits = [term for term in query_terms if term in lowered]
    parts: list[str] = []
    if hits:
        parts.append("Query term overlap: " + ", ".join(hits[:8]))
    if paper.quality_score:
        parts.append(f"quality={paper.quality_score:.2f}")
    if paper.citations is not None:
        parts.append(f"cited_by={paper.citations}")
    if paper.pmcid:
        parts.append(f"pmcid={paper.pmcid}")
    return "; ".join(parts) if parts else "Relevant by public-source ranking; manual review required."


def dedupe_papers(papers: list[Paper]) -> list[Paper]:
    merged: dict[str, Paper] = {}
    for paper in papers:
        key = dedupe_key(paper)
        existing = merged.get(key)
        if existing is None:
            merged[key] = paper
            continue
        merge_into(existing, paper)
    return list(merged.values())


def dedupe_key(paper: Paper) -> str:
    if paper.doi:
        return "doi:" + paper.doi.lower()
    if paper.id and str(paper.id).isdigit():
        return "pmid:" + str(paper.id)
    title = re.sub(r"[^a-z0-9]+", " ", paper.title.lower()).strip()
    return "title:" + title[:120]


def merge_into(existing: Paper, incoming: Paper) -> None:
    existing.source_hits = sorted(set(existing.source_hits + incoming.source_hits + [incoming.source]))
    if not existing.abstract and incoming.abstract:
        existing.abstract = incoming.abstract
    if not existing.doi and incoming.doi:
        existing.doi = incoming.doi
    if not existing.pmcid and incoming.pmcid:
        existing.pmcid = incoming.pmcid
    if existing.citations is None and incoming.citations is not None:
        existing.citations = incoming.citations
    if not existing.journal and incoming.journal:
        existing.journal = incoming.journal
    if not existing.authors and incoming.authors:
        existing.authors = incoming.authors
    if existing.source != "pubmed" and incoming.source == "pubmed":
        existing.source = "pubmed"
        existing.id = incoming.id or existing.id
        existing.url = incoming.url or existing.url
