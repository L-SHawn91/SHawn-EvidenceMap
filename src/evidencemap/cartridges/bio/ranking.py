from __future__ import annotations

import re

from evidencemap.models import Paper


CORE_ALIASES: dict[str, set[str]] = {
    "endometrial": {"endometrial", "endometrium", "uterine", "uterus"},
    "organoid": {"organoid", "organoids", "assembloid", "assembloids", "3d"},
    "implantation": {"implantation", "implant", "receptivity", "receptive", "embryo"},
    "drug": {"drug", "compound", "therapeutic", "pharmacological", "small molecule"},
    "screening": {"screening", "screen", "high throughput", "hts", "assay"},
    "target": {"target", "targeting", "pathway", "mechanism", "biomarker"},
    "cancer": {"cancer", "tumor", "tumour", "oncology", "carcinoma"},
}


def rank_public_papers(
    query: str,
    papers: list[Paper],
    limit: int,
    ranking_mode: str = "balanced",
) -> list[Paper]:
    groups = concept_groups(query)
    scored: list[Paper] = []
    for paper in papers:
        score, support = score_public_paper(query, paper, groups, ranking_mode=ranking_mode)
        if score <= 0:
            continue
        paper.quality_score = score
        paper.candidate_source_sentence = support
        _, _, paper.source_sentence_index = best_candidate_source_sentence(
            paper.abstract or paper.title,
            groups,
        )
        paper.source_section = "abstract" if paper.abstract else "title"
        scored.append(paper)

    scored.sort(
        key=lambda p: (
            p.quality_score,
            1 if p.source == "pubmed" else 0,
            p.citations or 0,
            p.year or 0,
        ),
        reverse=True,
    )
    return scored[:limit]


def concept_groups(query: str) -> list[set[str]]:
    lowered = query.lower()
    groups: list[set[str]] = []
    for key, aliases in CORE_ALIASES.items():
        if key in lowered or any(alias in lowered for alias in aliases):
            groups.append(aliases)
    if groups:
        return groups

    terms = re.findall(r"[a-z0-9-]{5,}", lowered)
    return [{term} for term in terms[:5]]


def score_public_paper(
    query: str,
    paper: Paper,
    groups: list[set[str]],
    ranking_mode: str = "balanced",
) -> tuple[float, str]:
    title = normalize(paper.title)
    abstract = normalize(paper.abstract)
    text = f"{title} {abstract}".strip()
    if not text:
        return 0.0, ""

    title_hits = concept_hit_count(title, groups)
    text_hits = concept_hit_count(text, groups)
    required = min(2, len(groups)) if groups else 1
    if text_hits < required:
        return 0.0, ""

    support = best_support_sentence(query, paper.abstract or paper.title, groups)
    abstract_bonus = 0.15 if paper.abstract else 0.0
    pmid_bonus = 0.08 if paper.id and paper.id.isdigit() else 0.0
    pmcid_bonus = 0.05 if paper.pmcid else 0.0
    citation_bonus = citation_weight(paper.citations, ranking_mode)
    recency_bonus = recency_weight(paper.year, ranking_mode)

    score = (
        title_hits * 0.35
        + text_hits * 0.16
        + abstract_bonus
        + pmid_bonus
        + pmcid_bonus
        + citation_bonus
        + recency_bonus
    )
    return round(score, 4), support


def citation_weight(citations: int | None, ranking_mode: str) -> float:
    if citations is None:
        return 0.0
    if ranking_mode == "foundational":
        return min(0.55, citations / 900)
    if ranking_mode == "recent":
        return min(0.04, citations / 1600)
    return min(0.18, citations / 1000)


def recency_weight(year: int | None, ranking_mode: str) -> float:
    if not year:
        return 0.0
    if ranking_mode == "foundational":
        if year <= 2019:
            return 0.16
        if year <= 2022:
            return 0.08
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


def best_support_sentence(query: str, text: str, groups: list[set[str]]) -> str:
    """Deprecated compatibility wrapper for the pre-0.3 helper name."""
    return best_candidate_source_sentence(text, groups)[0]


def best_candidate_source_sentence(text: str, groups: list[set[str]]) -> tuple[str, str, int | None]:
    sentences = split_sentences(text)
    if not sentences:
        return "", "", None
    ranked = sorted(
        enumerate(sentences, start=1),
        key=lambda item: (concept_hit_count(normalize(item[1]), groups), len(item[1])),
        reverse=True,
    )
    index, sentence = ranked[0]
    sentence = sentence.strip()
    candidate = sentence[:360] + ("..." if len(sentence) > 360 else "")
    return candidate, "abstract", index


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def normalize(text: str) -> str:
    return text.lower().replace("-", " ")
