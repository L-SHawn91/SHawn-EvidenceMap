from __future__ import annotations

import re
from dataclasses import dataclass

from evidencemap.core.cartridge import EvidenceCartridge
from evidencemap.crossref import search_crossref
from evidencemap.models import EvidenceRow, Paper
from evidencemap.openalex import search_openalex


@dataclass(frozen=True, slots=True)
class ScholarlyCartridgeConfig:
    id: str
    name: str
    description: str
    aliases: dict[str, set[str]]
    theme_rules: tuple[tuple[str, str], ...]
    sources: tuple[str, ...] = ("openalex", "crossref")
    status: str = "public_demo"


def make_scholarly_cartridge(config: ScholarlyCartridgeConfig) -> EvidenceCartridge:
    compiled_rules = tuple((label, re.compile(pattern, re.I)) for label, pattern in config.theme_rules)
    evidence_labels = tuple(label for label, _ in config.theme_rules) + ("background evidence",)

    def search(query: str, limit: int) -> list[Paper]:
        papers: list[Paper] = []
        for source_fn in (search_openalex, search_crossref):
            try:
                papers.extend(source_fn(query, limit=limit))
            except Exception:
                continue
        return papers

    def enrich(papers: list[Paper]) -> None:
        return None

    def rank(query: str, papers: list[Paper], limit: int, ranking_mode: str) -> list[Paper]:
        return rank_scholarly_papers(query, papers, limit, config.aliases, ranking_mode)

    def paper_to_row(query: str, paper: Paper) -> EvidenceRow:
        text = f"{paper.title}\n{paper.abstract}"
        evidence_type = classify(text, compiled_rules)
        return EvidenceRow(
            claim="",
            evidence_type=evidence_type,
            paper_id=paper.id,
            title=paper.title,
            year=paper.year,
            rationale=rationale_for(query, text, paper),
            candidate_source_sentence=paper.candidate_source_sentence,
            source_url=paper.url,
            evidence_relation="candidate",
            source=paper.source,
            doi=paper.doi,
            pmid=paper.id if paper.source == "pubmed" and paper.id.isdigit() else "",
            source_section=paper.source_section,
            source_sentence_index=paper.source_sentence_index,
        )

    return EvidenceCartridge(
        id=config.id,
        name=config.name,
        description=config.description,
        status=config.status,
        sources=config.sources,
        evidence_labels=evidence_labels,
        search=search,
        enrich=enrich,
        rank=rank,
        paper_to_row=paper_to_row,
    )


def rank_scholarly_papers(
    query: str,
    papers: list[Paper],
    limit: int,
    aliases: dict[str, set[str]],
    ranking_mode: str,
) -> list[Paper]:
    groups = concept_groups(query, aliases)
    scored: list[Paper] = []
    for paper in papers:
        score, support = score_scholarly_paper(paper, groups, ranking_mode)
        if score <= 0:
            continue
        paper.quality_score = score
        paper.candidate_source_sentence = support
        paper.source_section = "abstract" if paper.abstract else "title"
        _, _, paper.source_sentence_index = best_candidate_source_sentence(
            paper.abstract or paper.title, groups, section=paper.source_section
        )
        scored.append(paper)
    scored.sort(
        key=lambda p: (
            p.quality_score,
            p.citations or 0,
            p.year or 0,
        ),
        reverse=True,
    )
    return scored[:limit]


def score_scholarly_paper(
    paper: Paper,
    groups: list[set[str]],
    ranking_mode: str,
) -> tuple[float, str]:
    title = normalize(paper.title)
    abstract = normalize(paper.abstract)
    text = f"{title} {abstract}".strip()
    if not text:
        return 0.0, ""
    if weak_placeholder_text(text):
        return 0.0, ""

    title_hits = concept_hit_count(title, groups)
    text_hits = concept_hit_count(text, groups)
    required = min(2, len(groups)) if len(groups) >= 2 else 1
    if text_hits < required:
        return 0.0, ""

    support = best_support_sentence(paper.abstract or paper.title, groups)
    abstract_bonus = 0.15 if paper.abstract else 0.0
    doi_bonus = 0.06 if paper.doi else 0.0
    citation_bonus = citation_weight(paper.citations, ranking_mode)
    uncited_penalty = 0.12 if paper.citations == 0 else 0.0
    recency_bonus = recency_weight(paper.year, ranking_mode)
    score = title_hits * 0.35 + text_hits * 0.16 + abstract_bonus + doi_bonus + citation_bonus + recency_bonus - uncited_penalty
    return round(score, 4), support


def concept_groups(query: str, aliases: dict[str, set[str]]) -> list[set[str]]:
    lowered = normalize(query)
    groups: list[set[str]] = []
    for key, values in aliases.items():
        if key in lowered or any(value in lowered for value in values):
            groups.append(values)
    if groups:
        return groups
    terms = re.findall(r"[a-z0-9-]{5,}", lowered)
    return [{term} for term in terms[:5]]


def classify(text: str, rules: tuple[tuple[str, re.Pattern[str]], ...]) -> str:
    for label, pattern in rules:
        if pattern.search(text):
            return label
    return "background evidence"


def rationale_for(query: str, text: str, paper: Paper) -> str:
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
    if paper.doi:
        parts.append(f"doi={paper.doi}")
    return "; ".join(parts) if parts else "Relevant by public-source ranking; manual review required."


def citation_weight(citations: int | None, ranking_mode: str) -> float:
    if citations is None:
        return 0.0
    if ranking_mode == "foundational":
        return min(0.50, citations / 1200)
    if ranking_mode == "recent":
        return min(0.05, citations / 1800)
    return min(0.45, citations / 900)


def recency_weight(year: int | None, ranking_mode: str) -> float:
    if not year:
        return 0.0
    if ranking_mode == "foundational":
        if year <= 2019:
            return 0.14
        if year <= 2022:
            return 0.06
        return 0.0
    if ranking_mode == "recent":
        return max(0.0, min(0.22, (year - 2018) * 0.028))
    return max(0.0, min(0.08, (year - 2018) * 0.01))


def concept_hit_count(text: str, groups: list[set[str]]) -> int:
    count = 0
    for aliases in groups:
        if any(alias in text for alias in aliases):
            count += 1
    return count


def best_support_sentence(text: str, groups: list[set[str]]) -> str:
    """Deprecated compatibility wrapper for the pre-0.3 helper name."""
    return best_candidate_source_sentence(text, groups)[0]


def best_candidate_source_sentence(
    text: str,
    groups: list[set[str]],
    section: str = "abstract",
) -> tuple[str, str, int | None]:
    sentences = split_sentences(text)
    if not sentences:
        return "", section, None
    best_index, best = max(
        enumerate(sentences, start=1),
        key=lambda item: (concept_hit_count(normalize(item[1]), groups), len(item[1])),
    )
    best = best.strip()
    clipped = best[:360] + ("..." if len(best) > 360 else "")
    return clipped, section, best_index


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def normalize(text: str) -> str:
    return text.lower().replace("-", " ")


def weak_placeholder_text(text: str) -> bool:
    lowered = normalize(text)
    return any(
        phrase in lowered
        for phrase in (
            "description to come",
            "abstract not available",
            "no abstract available",
        )
    )
