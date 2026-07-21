from __future__ import annotations

import re

from evidencemap.models import EvidenceRow, Paper


THEME_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("drug screening evidence", re.compile(r"\bdrug|compound|therapeutic|screening|high-throughput|high throughput|assay\b", re.I)),
    ("model system evidence", re.compile(r"\borganoid|assembloid|3d culture|model\b", re.I)),
    ("mechanistic evidence", re.compile(r"\bmechanism|pathway|signaling|gene|protein|transcript", re.I)),
    ("clinical or patient evidence", re.compile(r"\bpatient|clinical|cohort|trial|diagnosis", re.I)),
    ("omics evidence", re.compile(r"\bsingle-cell|scrna|rna-seq|transcriptom|proteom|metabolom", re.I)),
]

EVIDENCE_LABELS = tuple(label for label, _ in THEME_RULES) + ("background evidence",)


def paper_to_row(query: str, paper: Paper) -> EvidenceRow:
    text = f"{paper.title}\n{paper.abstract}"
    evidence_type = classify(text)
    rationale = rationale_for(query, text, paper)
    return EvidenceRow(
        claim="",
        evidence_type=evidence_type,
        paper_id=paper.id,
        title=paper.title,
        year=paper.year,
        rationale=rationale,
        candidate_source_sentence=paper.candidate_source_sentence,
        source_url=paper.url,
        evidence_relation="candidate",
        source=paper.source,
        doi=paper.doi,
        pmid=paper.id if paper.source == "pubmed" and paper.id.isdigit() else "",
        source_section=paper.source_section,
        source_sentence_index=paper.source_sentence_index,
    )


def classify(text: str) -> str:
    for label, pattern in THEME_RULES:
        if pattern.search(text):
            return label
    return "background evidence"


def rationale_for(query: str, text: str, paper: Paper) -> str:
    query_terms = [t.lower() for t in re.findall(r"[A-Za-z0-9-]{4,}", query)]
    lowered = text.lower()
    hits = [term for term in query_terms if term in lowered]
    parts: list[str] = []
    if hits:
        parts.append("Query term overlap: " + ", ".join(hits[:8]))
    if paper.quality_score:
        parts.append(f"quality={paper.quality_score:.2f}")
    if paper.citations is not None:
        parts.append(f"cited_by={paper.citations}")
    if paper.pmcid:
        parts.append(f"pmcid={paper.pmcid}")
    return "; ".join(parts) if parts else "Relevant by public-source ranking; manual review required."
