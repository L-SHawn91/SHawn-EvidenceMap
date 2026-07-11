from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from .models import Paper


OPENALEX_WORKS = "https://api.openalex.org/works"


class OpenAlexRequestError(RuntimeError):
    """OpenAlex request failure that never includes credential-bearing URLs."""


def search_openalex(query: str, limit: int = 20) -> list[Paper]:
    """Search OpenAlex public metadata with an optional environment API key."""
    request_params = {
        "search": query,
        "per-page": str(max(1, min(limit, 100))),
        "sort": "relevance_score:desc",
    }
    api_key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if api_key:
        request_params["api_key"] = api_key
    params = urllib.parse.urlencode(request_params)
    try:
        with urllib.request.urlopen(
            f"{OPENALEX_WORKS}?{params}", timeout=25
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise OpenAlexRequestError(
            f"OpenAlex request failed with HTTP {exc.code}"
        ) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise OpenAlexRequestError("OpenAlex request failed with a network error") from None
    except json.JSONDecodeError:
        raise OpenAlexRequestError("OpenAlex returned an invalid JSON response") from None

    papers: list[Paper] = []
    for item in payload.get("results", []):
        title = clean(item.get("display_name") or "")
        if not title:
            continue
        doi = normalize_doi(item.get("doi") or "")
        openalex_id = item.get("id") or ""
        source_id = doi or openalex_id.rsplit("/", 1)[-1] or title[:80]
        papers.append(
            Paper(
                id=source_id,
                title=title,
                abstract=inverted_index_to_text(item.get("abstract_inverted_index") or {}),
                year=parse_int(item.get("publication_year")),
                journal=host_venue_name(item),
                authors=parse_authors(item.get("authorships") or []),
                doi=doi,
                citations=parse_int(item.get("cited_by_count")),
                url=doi_url(doi) or openalex_id,
                source="openalex",
                source_hits=["openalex"],
            )
        )
    return papers


def inverted_index_to_text(index: dict[str, list[int]]) -> str:
    if not index:
        return ""
    positioned: list[tuple[int, str]] = []
    for token, positions in index.items():
        for pos in positions:
            positioned.append((int(pos), token))
    return clean(" ".join(token for _, token in sorted(positioned)))


def parse_authors(authorships: list[dict]) -> list[str]:
    authors: list[str] = []
    for item in authorships[:12]:
        author = item.get("author") or {}
        name = author.get("display_name") or ""
        if name:
            authors.append(name)
    return authors


def host_venue_name(item: dict) -> str:
    source = item.get("primary_location", {}).get("source") or {}
    return source.get("display_name") or ""


def normalize_doi(value: str) -> str:
    return value.replace("https://doi.org/", "").strip()


def doi_url(doi: str) -> str:
    return f"https://doi.org/{doi}" if doi else ""


def parse_int(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def clean(value: str) -> str:
    return " ".join(value.replace("<i>", "").replace("</i>", "").split())
