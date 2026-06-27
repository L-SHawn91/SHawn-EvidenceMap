from __future__ import annotations

import json
import urllib.parse
import urllib.request

from .models import Paper


EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def search_europepmc(query: str, limit: int = 20) -> list[Paper]:
    """Search Europe PMC public metadata without private credentials."""
    params = urllib.parse.urlencode(
        {
            "query": query,
            "format": "json",
            "pageSize": str(max(1, min(limit, 100))),
            "sort": "relevance",
        }
    )
    with urllib.request.urlopen(f"{EUROPE_PMC}?{params}", timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))

    papers: list[Paper] = []
    for item in payload.get("resultList", {}).get("result", []):
        pmid = item.get("pmid") or ""
        doi = item.get("doi") or ""
        title = clean(item.get("title") or "")
        if not title:
            continue
        source_id = pmid or doi or item.get("id") or title[:80]
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else item.get("doiUrl") or ""
        if not url and item.get("id"):
            url = f"https://europepmc.org/article/{item.get('source', 'MED')}/{item['id']}"
        papers.append(
            Paper(
                id=source_id,
                title=title,
                abstract=clean(item.get("abstractText") or ""),
                year=parse_year(item.get("pubYear")),
                journal=item.get("journalTitle") or "",
                authors=parse_authors(item.get("authorString") or ""),
                doi=doi,
                pmcid=item.get("pmcid") or "",
                citations=parse_int(item.get("citedByCount")),
                url=url,
                source="europe_pmc",
                source_hits=["europe_pmc"],
            )
        )
    return papers


def enrich_papers_from_europepmc(papers: list[Paper]) -> None:
    """Add public citation/PMCID/DOI metadata for PMID-backed papers."""
    pmids = sorted({paper.id for paper in papers if paper.id and str(paper.id).isdigit()})
    if not pmids:
        return
    for chunk in chunks(pmids, 20):
        query = " OR ".join(f"EXT_ID:{pmid}" for pmid in chunk)
        params = urllib.parse.urlencode(
            {
                "query": f"({query}) AND SRC:MED",
                "format": "json",
                "pageSize": str(len(chunk)),
            }
        )
        with urllib.request.urlopen(f"{EUROPE_PMC}?{params}", timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
        by_pmid = {
            item.get("pmid"): item
            for item in payload.get("resultList", {}).get("result", [])
            if item.get("pmid")
        }
        for paper in papers:
            item = by_pmid.get(paper.id)
            if not item:
                continue
            if paper.citations is None:
                paper.citations = parse_int(item.get("citedByCount"))
            if not paper.pmcid:
                paper.pmcid = item.get("pmcid") or ""
            if not paper.doi:
                paper.doi = item.get("doi") or ""
            if "europe_pmc" not in paper.source_hits:
                paper.source_hits.append("europe_pmc")


def parse_authors(value: str) -> list[str]:
    return [part.strip().rstrip(".") for part in value.split(",") if part.strip()]


def parse_year(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def parse_int(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def clean(value: str) -> str:
    return " ".join(value.replace("<i>", "").replace("</i>", "").split())


def chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]
