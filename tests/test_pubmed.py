from __future__ import annotations

import pytest

from evidencemap import pubmed


ESEARCH_JSON = b'{"esearchresult": {"idlist": ["30000001", "30000002"]}}'

EFETCH_XML = b"""<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>30000001</PMID>
      <Article>
        <Journal><Title>Journal of Public Metadata</Title></Journal>
        <ArticleTitle>Synthetic smoke fixture for the PubMed adapter</ArticleTitle>
        <Abstract><AbstractText>Synthetic abstract text used only for adapter parsing.</AbstractText></Abstract>
        <AuthorList>
          <Author><LastName>Doe</LastName><ForeName>Jane</ForeName></Author>
          <Author><LastName>Roe</LastName><ForeName>Alex</ForeName></Author>
        </AuthorList>
      </Article>
    </MedlineCitation>
    <PubmedData>
      <History>
        <PubMedPubDate PubStatus="pubmed"><Year>2024</Year></PubMedPubDate>
      </History>
      <ArticleIdList>
        <ArticleId IdType="pubmed">30000001</ArticleId>
      </ArticleIdList>
    </PubmedData>
    <MedlineCitation>
      <Article>
        <ArticleDate><Year>2024</Year></ArticleDate>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>30000002</PMID>
      <Article>
        <Journal><Title>Journal of Public Metadata</Title></Journal>
        <ArticleTitle>Second synthetic entry with a collective author</ArticleTitle>
        <Abstract>
          <AbstractText Label="BACKGROUND">Background sentence.</AbstractText>
          <AbstractText Label="RESULTS">Results sentence.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author><CollectiveName>Public Consortium</CollectiveName></Author>
        </AuthorList>
      </Article>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList>
        <ArticleId IdType="pubmed">30000002</ArticleId>
      </ArticleIdList>
    </PubmedData>
    <MedlineCitation>
      <Article>
        <ArticleDate><Year>2023</Year></ArticleDate>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


class _Response:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_search_pubmed_parses_public_metadata_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    payloads = [ESEARCH_JSON, EFETCH_XML]
    seen_urls: list[str] = []

    def fake_urlopen(url: str, timeout: int) -> _Response:
        seen_urls.append(url)
        return _Response(payloads.pop(0))

    monkeypatch.setattr(pubmed.urllib.request, "urlopen", fake_urlopen)

    papers = pubmed.search_pubmed("synthetic query", limit=2)

    assert [paper.id for paper in papers] == ["30000001", "30000002"]
    assert papers[0].title == "Synthetic smoke fixture for the PubMed adapter"
    assert papers[0].journal == "Journal of Public Metadata"
    assert papers[0].authors == ["Jane Doe", "Alex Roe"]
    assert papers[0].url == "https://pubmed.ncbi.nlm.nih.gov/30000001/"
    assert papers[0].source_hits == ["pubmed"]
    assert "Synthetic abstract text" in papers[0].abstract

    assert papers[1].authors == ["Public Consortium"]
    assert "Background sentence." in papers[1].abstract
    assert "Results sentence." in papers[1].abstract

    assert seen_urls[0].startswith("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?")
    assert seen_urls[1].startswith("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?")


def test_search_pubmed_returns_empty_when_esearch_has_no_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(url: str, timeout: int) -> _Response:
        return _Response(b'{"esearchresult": {"idlist": []}}')

    monkeypatch.setattr(pubmed.urllib.request, "urlopen", fake_urlopen)

    assert pubmed.search_pubmed("synthetic query", limit=5) == []
