from __future__ import annotations

import importlib.util
from pathlib import Path

from evidencemap.models import EvidenceMap, EvidenceRow, Paper


ROOT = Path(__file__).parents[1]


def load_web_server_module():
    spec = importlib.util.spec_from_file_location("evidencemap_web_server", ROOT / "web" / "server.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_web_demo_shows_source_name_and_source_url_separately(monkeypatch) -> None:
    module = load_web_server_module()
    row = EvidenceRow(
        claim="A claim.",
        evidence_type="model system evidence",
        paper_id="123",
        title="Paper 123",
        year=2025,
        rationale="query overlap",
        candidate_source_sentence="Candidate sentence.",
        source_url="https://pubmed.ncbi.nlm.nih.gov/123/",
        source="pubmed",
        pmid="123",
    )
    evidence_map = EvidenceMap(
        query="topic",
        claim="A claim.",
        papers=[Paper(id="123", title="Paper 123")],
        rows=[row],
        cartridge="bio",
    )
    monkeypatch.setattr(module, "build_evidence_map", lambda *args, **kwargs: evidence_map)

    html = module.render_page(query="topic", claim="A claim.", ranking_mode="recent")

    assert "<th>Source name</th>" in html
    assert "<th>Source URL</th>" in html
    assert "<td>pubmed</td>" in html
    assert '<a href="https://pubmed.ncbi.nlm.nih.gov/123/"' in html


def test_web_demo_does_not_link_non_http_source_url(monkeypatch) -> None:
    module = load_web_server_module()
    unsafe_url = "javascript:alert('unsafe')"
    row = EvidenceRow(
        claim="A claim.",
        evidence_type="model system evidence",
        paper_id="123",
        title="Paper 123",
        year=2025,
        rationale="query overlap",
        candidate_source_sentence="Candidate sentence.",
        source_url=unsafe_url,
        source="untrusted-provider",
    )
    evidence_map = EvidenceMap(
        query="topic",
        claim="A claim.",
        papers=[Paper(id="123", title="Paper 123")],
        rows=[row],
        cartridge="bio",
    )
    monkeypatch.setattr(module, "build_evidence_map", lambda *args, **kwargs: evidence_map)

    html = module.render_page(query="topic", claim="A claim.", ranking_mode="recent")

    assert 'href="javascript:' not in html
    assert "javascript:alert(&#x27;unsafe&#x27;)" in html
