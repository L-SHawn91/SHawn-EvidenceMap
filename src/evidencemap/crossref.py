from __future__ import annotations

import json
import urllib.parse
import urllib.request

from .models import Paper


CROSSREF_WORKS = "https://api.crossref.org/works"


def search_crossref(query: str, limit: int = 20) -> list[Paper]:
    """Search Crossref public metadata without private credentials."""
    params = urllib.parse.urlencode(
        {
            "query": query,
            "rows": str(max(1, min(limit, 100))),
            "sort": "relevance",
        }
    )
    request = urllib.request.Request(
        f"{CROSSREF_WORKS}?{params}",
        headers={"User-Agent": "SHawn-EvidenceMap/0.1 (mailto:dr.shawn91@gmail.com)"},
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))

    papers: list[Paper] = []
    for item in payload.get("message", {}).get("items", []):
        title = clean(first(item.get("title")))
        if not title:
            continue
        doi = (item.get("DOI") or "").strip()
        abstract = clean(item.get("abstract") or "")
        papers.append(
            Paper(
                id=doi or item.get("URL") or title[:80],
                title=title,
                abstract=abstract,
                year=parse_year(item),
                journal=clean(first(item.get("container-title"))),
                authors=parse_authors(item.get("author") or []),
                doi=doi,
                citations=parse_int(item.get("is-referenced-by-count")),
                url=f"https://doi.org/{doi}" if doi else item.get("URL", ""),
                source="crossref",
                source_hits=["crossref"],
            )
        )
    return papers


def parse_authors(authors: list[dict]) -> list[str]:
    out: list[str] = []
    for author in authors[:12]:
        name = " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part).strip()
        if name:
            out.append(name)
    return out


def parse_year(item: dict) -> int | None:
    for key in ("published-print", "published-online", "published", "created"):
        parts = item.get(key, {}).get("date-parts") or []
        if parts and parts[0]:
            return parse_int(parts[0][0])
    return None


def first(value: object) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    return str(value or "")


def parse_int(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def clean(value: str) -> str:
    return " ".join(value.replace("<i>", "").replace("</i>", "").replace("<jats:p>", "").replace("</jats:p>", "").split())
