from __future__ import annotations

import json

import pytest

from evidencemap import europepmc
from evidencemap.models import Paper


SEARCH_PAYLOAD = json.dumps(
    {
        "resultList": {
            "result": [
                {
                    "id": "40000001",
                    "source": "MED",
                    "pmid": "40000001",
                    "doi": "10.1000/synthetic.epmc.001",
                    "title": "Synthetic smoke fixture for the Europe PMC adapter",
                    "abstractText": "Synthetic abstract text for adapter parsing.",
                    "pubYear": "2024",
                    "journalTitle": "Journal of Public Metadata",
                    "authorString": "Doe J., Roe A.",
                    "pmcid": "PMC9000001",
                    "citedByCount": 7,
                    "doiUrl": "https://doi.org/10.1000/synthetic.epmc.001",
                },
                {
                    "id": "40000002",
                    "source": "PPR",
                    "title": "Preprint without a PMID",
                    "pubYear": "2023",
                    "journalTitle": "Public Preprint Server",
                    "authorString": "Public Consortium",
                },
                {
                    "id": "40000003",
                    "source": "MED",
                    "pmid": "40000003",
                    "title": "",
                },
            ]
        }
    }
).encode("utf-8")

ENRICH_PAYLOAD = json.dumps(
    {
        "resultList": {
            "result": [
                {
                    "pmid": "50000001",
                    "doi": "10.1000/synthetic.epmc.enrich",
                    "pmcid": "PMC9000042",
                    "citedByCount": 12,
                }
            ]
        }
    }
).encode("utf-8")


class _Response:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_search_europepmc_parses_public_metadata_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    seen_urls: list[str] = []

    def fake_urlopen(url: str, timeout: int) -> _Response:
        seen_urls.append(url)
        return _Response(SEARCH_PAYLOAD)

    monkeypatch.setattr(europepmc.urllib.request, "urlopen", fake_urlopen)

    papers = europepmc.search_europepmc("synthetic query", limit=5)

    assert [paper.id for paper in papers] == ["40000001", "40000002"]

    first = papers[0]
    assert first.title == "Synthetic smoke fixture for the Europe PMC adapter"
    assert first.doi == "10.1000/synthetic.epmc.001"
    assert first.pmcid == "PMC9000001"
    assert first.citations == 7
    assert first.year == 2024
    assert first.journal == "Journal of Public Metadata"
    assert first.authors == ["Doe J", "Roe A"]
    assert first.url == "https://pubmed.ncbi.nlm.nih.gov/40000001/"
    assert first.source == "europe_pmc"
    assert first.source_hits == ["europe_pmc"]

    second = papers[1]
    assert second.url == "https://europepmc.org/article/PPR/40000002"
    assert second.authors == ["Public Consortium"]

    assert seen_urls[0].startswith(europepmc.EUROPE_PMC)


def test_enrich_papers_from_europepmc_fills_public_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str, timeout: int) -> _Response:
        return _Response(ENRICH_PAYLOAD)

    monkeypatch.setattr(europepmc.urllib.request, "urlopen", fake_urlopen)

    paper = Paper(id="50000001", title="Existing pubmed record", source_hits=["pubmed"])
    europepmc.enrich_papers_from_europepmc([paper])

    assert paper.doi == "10.1000/synthetic.epmc.enrich"
    assert paper.pmcid == "PMC9000042"
    assert paper.citations == 12
    assert paper.source_hits == ["pubmed", "europe_pmc"]


def test_enrich_papers_from_europepmc_skips_non_pmid_records(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_urlopen(url: str, timeout: int) -> _Response:
        nonlocal called
        called = True
        return _Response(b'{"resultList": {"result": []}}')

    monkeypatch.setattr(europepmc.urllib.request, "urlopen", fake_urlopen)

    europepmc.enrich_papers_from_europepmc(
        [Paper(id="10.1000/not-a-pmid", title="DOI-only record")]
    )

    assert called is False
