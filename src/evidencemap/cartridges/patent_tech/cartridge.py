from __future__ import annotations

from evidencemap.cartridges.common.scholarly import ScholarlyCartridgeConfig, make_scholarly_cartridge


PATENT_TECH_CARTRIDGE = make_scholarly_cartridge(
    ScholarlyCartridgeConfig(
        id="patent_tech",
        name="Patent/Tech EvidenceMap",
        description="Public technology-landscape evidence mapping from OpenAlex scholarly metadata.",
        aliases={
            "technology": {"technology", "technical", "innovation", "commercialization", "prototype"},
            "patent": {"patent", "intellectual property", "ip", "claim", "invention"},
            "application": {"application", "use case", "translation", "deployment", "industry"},
            "landscape": {"landscape", "trend", "roadmap", "emerging", "market"},
        },
        theme_rules=(
            ("technology landscape evidence", r"\blandscape|trend|roadmap|emerging|market\b"),
            ("patent or IP evidence", r"\bpatent|intellectual property| IP |claim|invention\b"),
            ("application evidence", r"\bapplication|use case|translation|deployment|industry\b"),
            ("prototype or validation evidence", r"\bprototype|validation|proof of concept|pilot|demonstration\b"),
            ("review evidence", r"\breview|survey|overview|bibliometric\b"),
        ),
    )
)
