from __future__ import annotations

from evidencemap.core.cartridge import EvidenceCartridge

from .labels import EVIDENCE_LABELS, paper_to_row
from .ranking import rank_public_papers
from .sources import enrich_bio_papers, search_bio_sources


BIO_CARTRIDGE = EvidenceCartridge(
    id="bio",
    name="Biomedical EvidenceMap",
    description="Public biomedical literature evidence mapping from PubMed and Europe PMC metadata.",
    status="public_demo",
    sources=("pubmed", "europe_pmc"),
    evidence_labels=EVIDENCE_LABELS,
    search=search_bio_sources,
    enrich=enrich_bio_papers,
    rank=rank_public_papers,
    paper_to_row=paper_to_row,
)
