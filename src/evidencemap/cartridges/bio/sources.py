from __future__ import annotations

from evidencemap.europepmc import enrich_papers_from_europepmc, search_europepmc
from evidencemap.models import Paper
from evidencemap.pubmed import search_pubmed


def search_bio_sources(query: str, limit: int) -> list[Paper]:
    papers: list[Paper] = []
    for source_fn in (search_pubmed, search_europepmc):
        try:
            papers.extend(source_fn(query, limit=limit))
        except Exception:
            continue
    return papers


def enrich_bio_papers(papers: list[Paper]) -> None:
    enrich_papers_from_europepmc(papers)
