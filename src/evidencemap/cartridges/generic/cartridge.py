from __future__ import annotations

from evidencemap.cartridges.common.scholarly import ScholarlyCartridgeConfig, make_scholarly_cartridge


GENERIC_CARTRIDGE = make_scholarly_cartridge(
    ScholarlyCartridgeConfig(
        id="generic",
        name="Generic Scholarly EvidenceMap",
        description="Domain-neutral public scholarly metadata mapping from OpenAlex and Crossref.",
        aliases={},
        theme_rules=(
            ("review evidence", r"\breview|systematic review|meta-analysis|scoping review|survey\b"),
            ("software or tool evidence", r"\bsoftware|tool|code|repository|open[ -]source|api\b"),
            ("data resource evidence", r"\bdataset|corpus|database|data resource|benchmark data\b"),
            ("methodology evidence", r"\bmethod|methodology|framework|standard|protocol|model\b"),
            ("empirical evidence", r"\bexperiment|empirical|evaluation|analysis|results|study\b"),
        ),
    )
)
