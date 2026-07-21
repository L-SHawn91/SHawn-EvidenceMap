import json
import tomllib

import pytest

import evidencemap

from evidencemap.cache import map_from_dict
from evidencemap.cartridges import get_cartridge
from evidencemap.cartridges.common.scholarly import best_candidate_source_sentence
from evidencemap.cartridges.bio.ranking import rank_public_papers
from evidencemap.cli import build_parser
import evidencemap.cli as cli_module
from evidencemap.export import to_json, to_markdown
from evidencemap.models import EvidenceMap, EvidenceRow, Paper
from evidencemap.report import to_customer_report
from evidencemap.visual_report import to_visual_html
import evidencemap.pipeline as pipeline_module
from evidencemap.review import ReviewFileError, apply_review_payload, build_statement, load_review_file


def make_row(paper_id: str, relation: str = "candidate") -> EvidenceRow:
    return EvidenceRow(
        claim="Endometrial organoids model implantation biology.",
        evidence_type="model system evidence",
        paper_id=paper_id,
        title=f"Paper {paper_id}",
        year=2025,
        rationale="query overlap",
        candidate_source_sentence=f"Candidate sentence {paper_id}.",
        source_url=f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/",
        evidence_relation=relation,
        source="pubmed",
        doi=f"10.1000/{paper_id}",
        pmid=paper_id,
        source_section="abstract",
        source_sentence_index=2,
    )


def make_map(*rows: EvidenceRow, claim: str = "Endometrial organoids model implantation biology.") -> EvidenceMap:
    papers = [Paper(id=row.paper_id, title=row.title, url=row.source_url) for row in rows]
    return EvidenceMap(query="endometrial organoid implantation", claim=claim, papers=papers, rows=list(rows), cartridge="bio")


def test_cli_accepts_claim_review_file_and_statement_gate_flags() -> None:
    args = build_parser().parse_args(
        ["endometrial organoid implantation", "--claim", "Organoids model implantation.", "--reviews", "reviews.json", "--draft-statement", "--json"]
    )
    assert args.claim == "Organoids model implantation."
    assert args.reviews == "reviews.json"
    assert args.draft_statement is True
    assert args.json is True

    with pytest.raises(SystemExit):
        build_parser().parse_args(["topic", "--json", "--markdown"])


def test_cli_reports_review_application_errors_without_traceback(monkeypatch, capsys) -> None:
    def fail_build(*args, **kwargs):
        raise ReviewFileError("unknown paper_id: missing")

    monkeypatch.setattr(cli_module, "build_evidence_map", fail_build)
    monkeypatch.setattr("sys.argv", ["evidencemap", "topic", "--json"])

    with pytest.raises(SystemExit) as exc_info:
        cli_module.main()

    stderr = capsys.readouterr().err
    assert exc_info.value.code == 2
    assert "unknown paper_id: missing" in stderr
    assert "Traceback" not in stderr


def test_new_exports_use_candidate_terminology_and_traceability() -> None:
    evidence_map = make_map(make_row("123"))
    markdown = to_markdown(evidence_map)
    payload = json.loads(to_json(evidence_map))

    assert "Candidate source sentence" in markdown
    assert "Support sentence" not in markdown
    assert "reviewed-support" not in markdown
    assert "candidate_source_sentence" in payload["rows"][0]
    assert "support_sentence" not in payload["rows"][0]
    assert payload["rows"][0]["source_sentence_index"] == 2
    assert payload["rows"][0]["doi"] == "10.1000/123"
    assert payload["rows"][0]["pmid"] == "123"


def test_public_exports_show_source_name_and_source_url_separately() -> None:
    evidence_map = make_map(make_row("123"))
    markdown = to_markdown(evidence_map)
    report = to_customer_report(evidence_map)
    html = to_visual_html(evidence_map)

    assert "| Source name | Source URL |" in markdown
    assert "| pubmed | https://pubmed.ncbi.nlm.nih.gov/123/ |" in markdown
    assert "| Source name | Source URL |" in report
    assert "| pubmed | https://pubmed.ncbi.nlm.nih.gov/123/ |" in report
    assert "<th>Source name</th><th>Source URL</th>" in html
    assert ">pubmed</td><td><a href=\"https://pubmed.ncbi.nlm.nih.gov/123/\"" in html


def test_reviews_reject_malformed_duplicate_unknown_and_invalid_relations() -> None:
    evidence_map = make_map(make_row("1"), make_row("2"))

    with pytest.raises(ReviewFileError, match="reviews"):
        apply_review_payload(evidence_map, {})
    with pytest.raises(ReviewFileError, match="duplicate"):
        apply_review_payload(
            evidence_map,
            {"reviews": [{"paper_id": "1", "relation": "reviewed-support"}, {"paper_id": "1", "relation": "uncertain"}]},
        )
    with pytest.raises(ReviewFileError, match="unknown paper_id"):
        apply_review_payload(evidence_map, {"reviews": [{"paper_id": "9", "relation": "reviewed-support"}]})
    with pytest.raises(ReviewFileError, match="invalid relation"):
        apply_review_payload(evidence_map, {"reviews": [{"paper_id": "1", "relation": "support"}]})
    with pytest.raises(ReviewFileError, match="schema_version"):
        apply_review_payload(evidence_map, {"schema_version": 2, "reviews": []})


@pytest.mark.parametrize("relation", [None, True, 1, [], {}])
def test_reviews_reject_non_string_relations_as_review_file_errors(relation: object) -> None:
    evidence_map = make_map(make_row("1"))

    with pytest.raises(ReviewFileError, match="invalid relation"):
        apply_review_payload(evidence_map, {"reviews": [{"paper_id": "1", "relation": relation}]})


def test_reviews_reject_unknown_top_level_fields() -> None:
    evidence_map = make_map(make_row("1"))

    with pytest.raises(ReviewFileError, match="unknown top-level field"):
        apply_review_payload(evidence_map, {"reviews": [], "review_status": "approved"})


def test_reviews_reject_unknown_item_fields() -> None:
    evidence_map = make_map(make_row("1"))

    with pytest.raises(ReviewFileError, match="unknown review item field"):
        apply_review_payload(
            evidence_map,
            {"reviews": [{"paper_id": "1", "relation": "reviewed-support", "rationale": "looks supportive"}]},
        )


def test_review_application_is_atomic_when_a_later_item_fails() -> None:
    evidence_map = make_map(make_row("1"), make_row("2"))

    with pytest.raises(ReviewFileError, match="unknown review item field"):
        apply_review_payload(
            evidence_map,
            {
                "reviews": [
                    {"paper_id": "1", "relation": "reviewed-support"},
                    {"paper_id": "2", "relation": "uncertain", "note": "typo field"},
                ]
            },
        )

    assert [row.evidence_relation for row in evidence_map.rows] == ["candidate", "candidate"]


def test_reviews_only_promote_rows_explicitly_named_by_user() -> None:
    evidence_map = make_map(make_row("1"), make_row("2"))
    apply_review_payload(evidence_map, {"reviews": [{"paper_id": "1", "relation": "reviewed-support"}]})

    assert evidence_map.rows[0].evidence_relation == "reviewed-support"
    assert evidence_map.rows[1].evidence_relation == "candidate"


@pytest.mark.parametrize(
    ("claim", "relations", "reason_fragment"),
    [
        ("", ["reviewed-support", "reviewed-support"], "claim"),
        ("A claim.", ["reviewed-support"], "two"),
        ("A claim.", ["reviewed-support", "reviewed-support", "reviewed-contradict"], "contradict"),
    ],
)
def test_statement_gate_blocks_unsafe_drafts(claim: str, relations: list[str], reason_fragment: str) -> None:
    rows = [make_row(str(index + 1), relation) for index, relation in enumerate(relations)]
    result = build_statement(make_map(*rows, claim=claim))

    assert result.status == "needs_check"
    assert result.draft == ""
    assert reason_fragment in result.reason.lower()


def test_statement_gate_emits_only_a_conservative_wrapper_after_two_reviewed_supports() -> None:
    evidence_map = make_map(make_row("1", "reviewed-support"), make_row("2", "reviewed-support"))
    result = build_statement(evidence_map)

    assert result.status == "ready"
    assert result.reviewed_support_count == 2
    assert "available evidence supports the claim that" in result.draft
    assert evidence_map.claim.rstrip(".") in result.draft
    assert "limited to the study contexts" in result.draft


def test_paper_and_row_default_to_unreviewed_candidate_state() -> None:
    row = make_row("1")
    assert row.evidence_relation == "candidate"
    assert row.source_section == "abstract"
    assert row.source_sentence_index == 2


def test_candidate_sentence_reports_its_one_based_abstract_location() -> None:
    text = "Background without overlap. Organoid implantation models reproduce epithelial responses. Final note."
    sentence, section, index = best_candidate_source_sentence(text, [{"organoid"}, {"implantation"}])

    assert sentence == "Organoid implantation models reproduce epithelial responses."
    assert section == "abstract"
    assert index == 2


def test_bio_ranking_tracks_candidate_sentence_location() -> None:
    paper = Paper(
        id="123",
        title="Background title",
        abstract="Background only. Organoid implantation models reproduce epithelial responses.",
        source="pubmed",
    )

    ranked = rank_public_papers("organoid implantation", [paper], limit=1, ranking_mode="recent")

    assert ranked[0].candidate_source_sentence.startswith("Organoid implantation")
    assert ranked[0].source_section == "abstract"
    assert ranked[0].source_sentence_index == 2


def test_cartridge_rows_preserve_source_identifiers_and_never_auto_review() -> None:
    paper = Paper(
        id="12345",
        title="Organoid implantation model",
        abstract="Organoid implantation models reproduce epithelial responses.",
        doi="10.1000/test",
        url="https://pubmed.ncbi.nlm.nih.gov/12345/",
        source="pubmed",
        candidate_source_sentence="Organoid implantation models reproduce epithelial responses.",
        source_section="abstract",
        source_sentence_index=1,
    )

    row = get_cartridge("generic").paper_to_row("organoid implantation", paper)

    assert row.evidence_relation == "candidate"
    assert row.claim == ""
    assert row.candidate_source_sentence.startswith("Organoid")
    assert row.source == "pubmed"
    assert row.doi == "10.1000/test"
    assert row.pmid == "12345"
    assert row.source_sentence_index == 1


def test_legacy_cache_support_sentence_migrates_without_public_legacy_field() -> None:
    restored = map_from_dict(
        {
            "query": "legacy",
            "papers": [{"id": "1", "title": "Legacy", "support_sentence": "Legacy candidate."}],
            "rows": [
                {
                    "claim": "Evidence related to: legacy",
                    "evidence_type": "background evidence",
                    "paper_id": "1",
                    "title": "Legacy",
                    "year": 2020,
                    "rationale": "legacy",
                    "support_sentence": "Legacy candidate.",
                    "source_url": "https://example.org/1",
                }
            ],
        }
    )

    assert restored.rows[0].candidate_source_sentence == "Legacy candidate."
    assert restored.rows[0].evidence_relation == "candidate"
    assert "support_sentence" not in json.loads(to_json(restored))["rows"][0]


def test_review_file_loader_rejects_invalid_json_and_returns_object(tmp_path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("not-json", encoding="utf-8")
    with pytest.raises(ReviewFileError, match="valid JSON"):
        load_review_file(invalid)

    valid = tmp_path / "reviews.json"
    valid.write_text('{"reviews": []}', encoding="utf-8")
    assert load_review_file(valid) == {"reviews": []}


def test_pipeline_applies_reviews_after_caching_unreviewed_search_results(monkeypatch) -> None:
    base = make_map(make_row("1"), make_row("2"), claim="")
    cached_snapshots = []

    monkeypatch.setattr(pipeline_module, "get_cached_map", lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline_module, "get_cartridge", lambda cartridge_id: object())
    monkeypatch.setattr(pipeline_module, "build_with_cartridge", lambda *args, **kwargs: base)
    monkeypatch.setattr(
        pipeline_module,
        "set_cached_map",
        lambda evidence_map, **kwargs: cached_snapshots.append(json.loads(to_json(evidence_map))),
    )

    result = pipeline_module.build_evidence_map(
        "topic",
        claim="A claim.",
        review_payload={
            "reviews": [
                {"paper_id": "1", "relation": "reviewed-support"},
                {"paper_id": "2", "relation": "reviewed-support"},
            ]
        },
        draft_statement=True,
    )

    assert [row["evidence_relation"] for row in cached_snapshots[0]["rows"]] == ["candidate", "candidate"]
    assert [row.evidence_relation for row in result.rows] == ["reviewed-support", "reviewed-support"]
    assert result.claim == "A claim."
    assert {row.claim for row in result.rows} == {"A claim."}
    assert result.statement.status == "ready"


def test_pipeline_without_claim_does_not_promote_topic_into_row_claim(monkeypatch) -> None:
    base = make_map(make_row("1"), claim="")
    monkeypatch.setattr(pipeline_module, "get_cached_map", lambda *args, **kwargs: base)

    result = pipeline_module.build_evidence_map("topic", claim="")

    assert result.claim == ""
    assert result.rows[0].claim == ""


def test_pipeline_rejects_review_relations_without_a_claim(monkeypatch) -> None:
    base = make_map(make_row("1"), claim="")
    monkeypatch.setattr(pipeline_module, "get_cached_map", lambda *args, **kwargs: base)

    with pytest.raises(ReviewFileError, match="claim is required"):
        pipeline_module.build_evidence_map(
            "topic",
            review_payload={"reviews": [{"paper_id": "1", "relation": "reviewed-support"}]},
        )


def test_markdown_exposes_statement_gate_status_without_scientific_validation_claim() -> None:
    evidence_map = make_map(make_row("1"), claim="A claim.")
    evidence_map.statement = build_statement(evidence_map)

    markdown = to_markdown(evidence_map)
    assert "Statement status: needs_check" in markdown
    assert "At least two distinct reviewed-support" in markdown
    assert "scientifically validated" not in markdown.lower()


def test_runtime_and_package_versions_match_0_3_0() -> None:
    from pathlib import Path

    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == "0.3.0"
    assert evidencemap.__version__ == "0.3.0"


def test_fixed_reports_use_candidate_language_and_show_review_relation() -> None:
    evidence_map = make_map(make_row("1"), claim="A claim.")
    evidence_map.statement = build_statement(evidence_map)

    report = to_customer_report(evidence_map)
    html = to_visual_html(evidence_map)

    for rendered in (report, html):
        assert "Candidate source sentence" in rendered
        assert "Support sentence" not in rendered
        assert "candidate" in rendered
        assert "needs_check" in rendered
