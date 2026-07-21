from __future__ import annotations

import json
from dataclasses import asdict

from .models import EvidenceMap


def to_json(evidence_map: EvidenceMap) -> str:
    return json.dumps(asdict(evidence_map), ensure_ascii=False, indent=2)


def to_markdown(evidence_map: EvidenceMap) -> str:
    lines = [
        f"# Evidence Map: {evidence_map.query}",
        "",
        "PUBLIC_STATUS: public-demo-output",
        f"CARTRIDGE: {evidence_map.cartridge}",
        "",
        "This output is for research triage and requires manual verification before citation.",
        "",
        f"Research topic: {evidence_map.query}",
        f"Claim under review: {evidence_map.claim or 'Not supplied'}",
        "",
        f"Statement status: {evidence_map.statement.status}",
        *([f"Statement reason: {evidence_map.statement.reason}"] if evidence_map.statement.reason else []),
        *([f"Statement draft: {evidence_map.statement.draft}"] if evidence_map.statement.draft else []),
        "",
        "| Relation | Evidence type | Year | Paper | Rationale | Candidate source sentence | Location | DOI | PMID | Source name | Source URL |",
        "|---|---|---:|---|---|---|---|---|---|---|---|",
    ]
    for row in evidence_map.rows:
        title = _cell(row.title)
        rationale = _cell(row.rationale)
        year = "" if row.year is None else str(row.year)
        lines.append(
            f"| {_cell(row.evidence_relation)} | {_cell(row.evidence_type)} | {year} | {title} | {rationale} | {_cell(row.candidate_source_sentence)} | {_cell(_location(row.source_section, row.source_sentence_index))} | {_cell(row.doi)} | {_cell(row.pmid)} | {_cell(row.source)} | {_cell(row.source_url)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _location(section: str, index: int | None) -> str:
    if not section:
        return ""
    return f"{section} sentence {index}" if index is not None else section
