from evidencemap.export import to_json, to_markdown
from evidencemap.models import EvidenceMap, EvidenceRow, Paper
from evidencemap.report import to_customer_report
from evidencemap.visual_report import to_visual_html


def sample_map(query="organoid | implantation"):
    row = EvidenceRow(
        claim="Claim with | separator",
        evidence_type="Public metadata",
        paper_id="p1",
        title="Title with | pipe",
        year=2024,
        rationale="Line one\nline two",
        candidate_source_sentence="Manual verification required.",
        source_url="https://example.org/paper",
    )
    paper = Paper(id="p1", title=row.title, abstract="Public abstract", year=2024, url=row.source_url)
    return EvidenceMap(query=query, papers=[paper], rows=[row], cartridge="bio")


def test_json_export_contains_query_and_rows():
    payload = to_json(sample_map())
    assert '"query": "organoid | implantation"' in payload
    assert '"rows"' in payload
    assert '"source_url": "https://example.org/paper"' in payload


def test_markdown_export_escapes_table_cells():
    md = to_markdown(sample_map())
    assert "Research topic: organoid | implantation" in md
    assert "Title with \\| pipe" in md
    assert "Line one line two" in md
    assert "PUBLIC_STATUS: public-demo-output" in md


def test_customer_report_includes_limitations_and_manual_review_boundary():
    report = to_customer_report(sample_map())
    assert "Manual expert review is required" in report
    assert "Public metadata may be incomplete" in report
    assert "SHawn EvidenceMap Report" in report


def test_visual_html_escapes_query_text():
    html = to_visual_html(sample_map('<script>alert(1)</script>'))
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>alert(1)</script>" not in html


def test_visual_html_does_not_link_non_http_source_url():
    evidence_map = sample_map()
    evidence_map.rows[0].source_url = "javascript:alert('unsafe')"

    html = to_visual_html(evidence_map)

    assert 'href="javascript:' not in html
    assert "javascript:alert(&#x27;unsafe&#x27;)" in html
