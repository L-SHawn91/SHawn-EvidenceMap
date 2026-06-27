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
        "| Claim | Evidence type | Year | Paper | Rationale | Support sentence | Source |",
        "|---|---|---:|---|---|---|---|",
    ]
    for row in evidence_map.rows:
        title = _cell(row.title)
        rationale = _cell(row.rationale)
        year = "" if row.year is None else str(row.year)
        lines.append(
            f"| {_cell(row.claim)} | {_cell(row.evidence_type)} | {year} | {title} | {rationale} | {_cell(row.support_sentence)} | {row.source_url} |"
        )
    lines.append("")
    return "\n".join(lines)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()
