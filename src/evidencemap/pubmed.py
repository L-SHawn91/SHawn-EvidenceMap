from __future__ import annotations

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from .models import Paper


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(query: str, limit: int = 20) -> list[Paper]:
    """Search PubMed public metadata without private credentials."""
    ids = _esearch(query, limit)
    if not ids:
        return []
    return _efetch(ids)


def _esearch(query: str, limit: int) -> list[str]:
    params = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": str(max(1, min(limit, 100))),
            "sort": "relevance",
        }
    )
    with urllib.request.urlopen(f"{EUTILS}/esearch.fcgi?{params}", timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("esearchresult", {}).get("idlist", [])


def _efetch(ids: list[str]) -> list[Paper]:
    params = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
        }
    )
    with urllib.request.urlopen(f"{EUTILS}/efetch.fcgi?{params}", timeout=30) as response:
        root = ET.fromstring(response.read())

    papers: list[Paper] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = _text(article, ".//PMID")
        title = _text(article, ".//ArticleTitle")
        abstract = " ".join(
            " ".join(part.strip() for part in abstract_node.itertext() if part.strip())
            for abstract_node in article.findall(".//AbstractText")
        )
        journal = _text(article, ".//Journal/Title")
        year = _year(article)
        authors = _authors(article)
        if not pmid or not title:
            continue
        papers.append(
            Paper(
                id=pmid,
                title=title,
                abstract=abstract,
                year=year,
                journal=journal,
                authors=authors,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                source_hits=["pubmed"],
            )
        )
    return papers


def _text(node: ET.Element, path: str) -> str:
    found = node.find(path)
    if found is None or found.text is None:
        return ""
    return "".join(found.itertext()).strip()


def _year(article: ET.Element) -> int | None:
    raw = _text(article, ".//PubDate/Year") or _text(article, ".//ArticleDate/Year")
    try:
        return int(raw)
    except ValueError:
        return None


def _authors(article: ET.Element) -> list[str]:
    out: list[str] = []
    for author in article.findall(".//Author"):
        last = _text(author, "LastName")
        fore = _text(author, "ForeName")
        collective = _text(author, "CollectiveName")
        name = " ".join(part for part in [fore, last] if part).strip() or collective
        if name:
            out.append(name)
    return out
