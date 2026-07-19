from __future__ import annotations

import json
import urllib.request

import pytest

from evidencemap import crossref


CROSSREF_PAYLOAD = json.dumps(
    {
        "message": {
            "items": [
                {
                    "DOI": "10.1000/synthetic.crossref.001",
                    "URL": "https://doi.org/10.1000/synthetic.crossref.001",
                    "title": ["Synthetic smoke fixture for the <i>Crossref</i> adapter"],
                    "abstract": "<jats:p>Synthetic abstract text for adapter parsing.</jats:p>",
                    "container-title": ["Journal of Public Metadata"],
                    "author": [
                        {"given": "Jane", "family": "Doe"},
                        {"given": "Alex", "family": "Roe"},
                    ],
                    "is-referenced-by-count": 4,
                    "published-print": {"date-parts": [[2024, 5, 1]]},
                },
                {
                    "URL": "https://example.org/no-doi",
                    "title": ["Record without a DOI"],
                    "container-title": ["Public Preprint Server"],
                    "author": [{"family": "Public Consortium"}],
                    "published-online": {"date-parts": [[2023]]},
                },
                {"title": []},
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


def test_search_crossref_parses_public_metadata_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> _Response:
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        return _Response(CROSSREF_PAYLOAD)

    monkeypatch.setattr(crossref.urllib.request, "urlopen", fake_urlopen)

    papers = crossref.search_crossref("synthetic query", limit=3)

    assert [paper.id for paper in papers] == [
        "10.1000/synthetic.crossref.001",
        "https://example.org/no-doi",
    ]

    first = papers[0]
    assert first.title == "Synthetic smoke fixture for the Crossref adapter"
    assert first.abstract == "Synthetic abstract text for adapter parsing."
    assert first.journal == "Journal of Public Metadata"
    assert first.authors == ["Jane Doe", "Alex Roe"]
    assert first.doi == "10.1000/synthetic.crossref.001"
    assert first.citations == 4
    assert first.year == 2024
    assert first.url == "https://doi.org/10.1000/synthetic.crossref.001"
    assert first.source == "crossref"
    assert first.source_hits == ["crossref"]

    second = papers[1]
    assert second.doi == ""
    assert second.url == "https://example.org/no-doi"
    assert second.year == 2023
    assert second.authors == ["Public Consortium"]

    assert str(captured["url"]).startswith(crossref.CROSSREF_WORKS)
    user_agent = str(captured["headers"].get("User-agent", ""))
    assert "SHawn-EvidenceMap" in user_agent
