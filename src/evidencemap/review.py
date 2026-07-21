from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from .models import EvidenceMap, StatementResult


RELATION_STATES = frozenset(
    {"candidate", "reviewed-support", "reviewed-contradict", "uncertain"}
)


class ReviewFileError(ValueError):
    """Raised when a local review payload does not match the public schema."""


def load_review_file(path: str | Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewFileError(f"review file must contain valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReviewFileError("review file must contain a JSON object")
    return payload


def apply_review_payload(evidence_map: EvidenceMap, payload: Mapping[str, Any]) -> None:
    unknown_fields = set(payload) - {"schema_version", "reviews"}
    if unknown_fields:
        names = ", ".join(sorted((str(field) for field in unknown_fields)))
        raise ReviewFileError(f"unknown top-level field(s): {names}")
    schema_version = payload.get("schema_version", 1)
    if isinstance(schema_version, bool) or not isinstance(schema_version, int) or schema_version != 1:
        raise ReviewFileError("unsupported schema_version; expected 1")
    reviews = payload.get("reviews")
    if not isinstance(reviews, list):
        raise ReviewFileError("review payload must contain a reviews list")

    rows_by_id = {row.paper_id: row for row in evidence_map.rows}
    seen: set[str] = set()
    decisions: list[tuple[str, str]] = []
    for item in reviews:
        if not isinstance(item, Mapping):
            raise ReviewFileError("each reviews item must be an object")
        unknown_item_fields = set(item) - {"paper_id", "relation"}
        if unknown_item_fields:
            names = ", ".join(sorted((str(field) for field in unknown_item_fields)))
            raise ReviewFileError(f"unknown review item field(s): {names}")
        paper_id = item.get("paper_id")
        relation = item.get("relation")
        if not isinstance(paper_id, str) or not paper_id.strip():
            raise ReviewFileError("each review requires a non-empty paper_id")
        if paper_id in seen:
            raise ReviewFileError(f"duplicate review for paper_id: {paper_id}")
        if paper_id not in rows_by_id:
            raise ReviewFileError(f"unknown paper_id: {paper_id}")
        if relation not in RELATION_STATES - {"candidate"}:
            raise ReviewFileError(f"invalid relation: {relation}")
        seen.add(paper_id)
        decisions.append((paper_id, relation))

    for paper_id, relation in decisions:
        rows_by_id[paper_id].evidence_relation = relation


def build_statement(evidence_map: EvidenceMap) -> StatementResult:
    supports = [row for row in evidence_map.rows if row.evidence_relation == "reviewed-support"]
    contradictions = [row for row in evidence_map.rows if row.evidence_relation == "reviewed-contradict"]
    counts = {
        "reviewed_support_count": len({row.paper_id for row in supports}),
        "reviewed_contradict_count": len({row.paper_id for row in contradictions}),
    }
    claim = evidence_map.claim.strip()
    if not claim:
        return StatementResult(status="needs_check", reason="A non-empty claim is required.", **counts)
    if contradictions:
        return StatementResult(
            status="needs_check",
            reason="Reviewed contradicting evidence must be resolved before drafting.",
            **counts,
        )
    if counts["reviewed_support_count"] < 2:
        return StatementResult(
            status="needs_check",
            reason="At least two distinct reviewed-support sources are required.",
            **counts,
        )

    normalized_claim = claim.rstrip(". ")
    draft = (
        f"Across {counts['reviewed_support_count']} reviewed public sources, the available evidence "
        f"supports the claim that {normalized_claim}. This statement remains limited to the study "
        "contexts represented in those sources."
    )
    return StatementResult(status="ready", draft=draft, **counts)
