from __future__ import annotations

import json
import urllib.error
import urllib.parse
from email.message import Message

import pytest

from evidencemap import openalex


OPENALEX_PAYLOAD = json.dumps(
    {
        "results": [
            {
                "id": "https://openalex.org/W9000001",
                "display_name": "Synthetic smoke fixture for the <i>OpenAlex</i> adapter",
                "doi": "https://doi.org/10.1000/synthetic.openalex.001",
                "publication_year": 2024,
                "cited_by_count": 9,
                "abstract_inverted_index": {
                    "Synthetic": [0],
                    "abstract": [1],
                    "text.": [2],
                },
                "authorships": [
                    {"author": {"display_name": "Jane Doe"}},
                    {"author": {"display_name": "Alex Roe"}},
                ],
                "primary_location": {
                    "source": {"display_name": "Journal of Public Metadata"}
                },
            },
            {
                "id": "https://openalex.org/W9000002",
                "display_name": "Record without a DOI",
                "publication_year": 2023,
                "authorships": [{"author": {"display_name": "Public Consortium"}}],
                "primary_location": {},
            },
            {"display_name": ""},
        ]
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


def test_search_openalex_parses_public_metadata_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str, timeout: int) -> _Response:
        return _Response(OPENALEX_PAYLOAD)

    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    monkeypatch.setattr(openalex.urllib.request, "urlopen", fake_urlopen)

    papers = openalex.search_openalex("synthetic query", limit=5)

    assert [paper.id for paper in papers] == [
        "10.1000/synthetic.openalex.001",
        "W9000002",
    ]

    first = papers[0]
    assert first.title == "Synthetic smoke fixture for the OpenAlex adapter"
    assert first.doi == "10.1000/synthetic.openalex.001"
    assert first.year == 2024
    assert first.citations == 9
    assert first.journal == "Journal of Public Metadata"
    assert first.authors == ["Jane Doe", "Alex Roe"]
    assert first.abstract == "Synthetic abstract text."
    assert first.url == "https://doi.org/10.1000/synthetic.openalex.001"
    assert first.source == "openalex"
    assert first.source_hits == ["openalex"]

    second = papers[1]
    assert second.doi == ""
    assert second.url == "https://openalex.org/W9000002"
    assert second.journal == ""


def test_openalex_request_uses_optional_environment_key(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"results": []}'

    def fake_urlopen(url: str, timeout: int) -> Response:
        captured["url"] = url
        assert timeout == 25
        return Response()

    monkeypatch.setenv("OPENALEX_API_KEY", "public-test-key with spaces")
    monkeypatch.setattr(openalex.urllib.request, "urlopen", fake_urlopen)

    assert openalex.search_openalex("open metadata", limit=3) == []
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(captured["url"]).query)
    assert params["api_key"] == ["public-test-key with spaces"]
    assert params["per-page"] == ["3"]


def test_openalex_request_omits_blank_environment_key(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"results": []}'

    def fake_urlopen(url: str, timeout: int) -> Response:
        captured["url"] = url
        return Response()

    monkeypatch.setenv("OPENALEX_API_KEY", "   ")
    monkeypatch.setattr(openalex.urllib.request, "urlopen", fake_urlopen)

    openalex.search_openalex("open metadata", limit=3)
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(captured["url"]).query)
    assert "api_key" not in params


def test_openalex_http_errors_do_not_expose_environment_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sensitive_value = "never-print-" + "this-openalex-key"

    def fake_urlopen(url: str, timeout: int) -> object:
        raise urllib.error.HTTPError(url, 401, "Unauthorized", Message(), None)

    monkeypatch.setenv("OPENALEX_API_KEY", sensitive_value)
    monkeypatch.setattr(openalex.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(openalex.OpenAlexRequestError) as captured:
        openalex.search_openalex("open metadata", limit=3)

    assert sensitive_value not in str(captured.value)
    assert "401" in str(captured.value)


def test_openalex_network_errors_do_not_expose_environment_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sensitive_value = "network-" + "credential-value"

    def fake_urlopen(url: str, timeout: int) -> object:
        raise urllib.error.URLError(f"failed request for {url}")

    monkeypatch.setenv("OPENALEX_API_KEY", sensitive_value)
    monkeypatch.setattr(openalex.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(openalex.OpenAlexRequestError) as captured:
        openalex.search_openalex("open metadata", limit=3)

    assert sensitive_value not in str(captured.value)
    assert "network error" in str(captured.value)


def test_openalex_invalid_json_does_not_expose_environment_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sensitive_value = "invalid-json-" + "credential-value"

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b"not-json"

    monkeypatch.setenv("OPENALEX_API_KEY", sensitive_value)
    monkeypatch.setattr(
        openalex.urllib.request,
        "urlopen",
        lambda url, timeout: Response(),
    )

    with pytest.raises(openalex.OpenAlexRequestError) as captured:
        openalex.search_openalex("open metadata", limit=3)

    assert sensitive_value not in str(captured.value)
    assert "invalid JSON" in str(captured.value)
