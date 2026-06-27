from __future__ import annotations

from collections import Counter
from datetime import date

from .models import EvidenceMap


def to_customer_report(evidence_map: EvidenceMap) -> str:
    evidence_counts = Counter(row.evidence_type for row in evidence_map.rows)
    top_years = sorted({row.year for row in evidence_map.rows if row.year}, reverse=True)
    lines = [
        f"# SHawn EvidenceMap Report: {evidence_map.query}",
        "",
        "PUBLIC_STATUS: public-demo-report",
        f"REPORT_DATE: {date.today().isoformat()}",
        f"CARTRIDGE: {evidence_map.cartridge}",
        "",
        "## 1. Executive Summary",
        "",
        f"This preliminary evidence report maps the research question `{evidence_map.query}` using public literature metadata.",
        f"The current run returned {len(evidence_map.rows)} ranked evidence rows.",
        "",
        "This report is designed for research planning, review scoping, grant background preparation, and manuscript evidence triage. It is not a substitute for manual source review.",
        "",
        "## 2. Scope",
        "",
        f"- Research question: `{evidence_map.query}`",
        f"- Cartridge: `{evidence_map.cartridge}`",
        "- Data type: public literature metadata and abstracts when available",
        "- Output type: claim-centered evidence map",
        "- Verification level: preliminary, manual verification required",
        "",
        "## 3. Method Snapshot",
        "",
        "- Search public metadata sources configured for the selected cartridge.",
        "- Normalize records into a shared paper schema.",
        "- Deduplicate by DOI, PMID, or normalized title.",
        "- Rank records by query concept coverage, citation signal, year profile, and metadata quality.",
        "- Extract a support sentence from title/abstract text when available.",
        "- Classify each row into a cartridge-specific evidence label.",
        "",
        "## 4. Evidence Mix",
        "",
    ]
    if evidence_counts:
        for label, count in evidence_counts.most_common():
            lines.append(f"- {label}: {count}")
    else:
        lines.append("- No evidence rows returned.")
    lines.extend(
        [
            "",
            "## 5. Year Coverage",
            "",
            "- Years represented: " + (", ".join(str(year) for year in top_years[:10]) if top_years else "not available"),
            "",
            "## 6. Ranked Evidence Table",
            "",
            "| # | Evidence type | Year | Paper | Rationale | Support sentence | Source |",
            "|---:|---|---:|---|---|---|---|",
        ]
    )
    for idx, row in enumerate(evidence_map.rows, start=1):
        year = "" if row.year is None else str(row.year)
        lines.append(
            f"| {idx} | {_cell(row.evidence_type)} | {year} | {_cell(row.title)} | {_cell(row.rationale)} | {_cell(row.support_sentence)} | {row.source_url} |"
        )
    lines.extend(
        [
            "",
            "## 7. Initial Interpretation",
            "",
            interpretation(evidence_map),
            "",
            "## 8. Recommended Next Steps",
            "",
            "- Manually open and verify the top-ranked sources.",
            "- Confirm whether the evidence labels match the intended research use case.",
            "- Expand the query with synonyms, population/context terms, or comparator terms.",
            "- Separate foundational and recent evidence if the report will support a review, grant, or manuscript.",
            "- For citation use, verify bibliographic metadata directly from the publisher or indexed source.",
            "",
            "## 9. Limitations",
            "",
            "- Public metadata may be incomplete, stale, duplicated, or missing abstracts.",
            "- Ranking is a triage signal, not a quality appraisal.",
            "- Support sentences are extracted automatically and may not represent the full paper.",
            "- This report does not verify full text, methods quality, statistical validity, or clinical/policy recommendations.",
            "- Manual expert review is required before citation, manuscript use, clinical interpretation, business decisions, or public claims.",
            "",
            "## 10. Delivery Note",
            "",
            "Prepared as a SHawn EvidenceMap preliminary report. For deeper paid work, the next deliverable can include expanded search strategy, inclusion/exclusion criteria, manual source verification, and a polished evidence brief.",
            "",
        ]
    )
    return "\n".join(lines)


def interpretation(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return "No ranked evidence rows were returned. The query should be broadened or rewritten before further analysis."
    top = evidence_map.rows[0]
    labels = Counter(row.evidence_type for row in evidence_map.rows)
    dominant = labels.most_common(1)[0][0]
    return (
        f"The strongest current signal is `{dominant}`. The top-ranked source is `{top.title}`"
        f"{f' ({top.year})' if top.year else ''}. This suggests the query has enough public metadata signal for an initial evidence map, but the top sources should be manually reviewed before any client-facing conclusion."
    )


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()
