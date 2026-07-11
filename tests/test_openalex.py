from __future__ import annotations

import urllib.error
import urllib.parse
from email.message import Message

import pytest

from evidencemap import openalex


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
