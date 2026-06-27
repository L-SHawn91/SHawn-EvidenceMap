from __future__ import annotations

import re

from evidencemap.models import Paper


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
