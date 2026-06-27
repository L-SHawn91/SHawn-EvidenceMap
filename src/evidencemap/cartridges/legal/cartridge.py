from __future__ import annotations

from evidencemap.cartridges.common.scholarly import ScholarlyCartridgeConfig, make_scholarly_cartridge


LEGAL_CARTRIDGE = make_scholarly_cartridge(
    ScholarlyCartridgeConfig(
        id="legal",
        name="Legal EvidenceMap",
        description="Public legal/regulatory evidence mapping from OpenAlex and Crossref metadata.",
        aliases={
            "ai": {"ai", "artificial intelligence", "algorithmic", "automated decision", "machine learning"},
            "legal": {"legal", "law", "judicial", "jurisprudence", "court"},
            "regulation": {"regulation", "regulatory", "compliance", "statute", "legislation"},
            "liability": {"liability", "responsibility", "accountability", "negligence", "tort"},
            "case": {"case law", "precedent", "litigation", "ruling", "judgment"},
            "policy": {"policy", "governance", "public law", "administrative"},
        },
        theme_rules=(
            ("case law or precedent evidence", r"\bcase law|precedent|litigation|ruling|judgment|court\b"),
            ("statutory or regulatory evidence", r"\bstatute|legislation|regulation|regulatory|compliance\b"),
            ("legal scholarship evidence", r"\blegal theory|jurisprudence|law review|doctrine|scholarship\b"),
            ("governance or policy evidence", r"\bgovernance|policy|administrative|public law\b"),
            ("review evidence", r"\breview|survey|systematic review|overview\b"),
        ),
    )
)
