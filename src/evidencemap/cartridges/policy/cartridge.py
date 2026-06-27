from __future__ import annotations

from evidencemap.cartridges.common.scholarly import ScholarlyCartridgeConfig, make_scholarly_cartridge


POLICY_CARTRIDGE = make_scholarly_cartridge(
    ScholarlyCartridgeConfig(
        id="policy",
        name="Policy EvidenceMap",
        description="Public policy evidence mapping from OpenAlex scholarly metadata.",
        aliases={
            "policy": {"policy", "policies", "governance", "regulation", "public sector"},
            "evaluation": {"evaluation", "impact", "outcome", "effectiveness", "assessment"},
            "intervention": {"intervention", "program", "initiative", "reform", "implementation"},
            "guideline": {"guideline", "recommendation", "framework", "standard"},
        },
        theme_rules=(
            ("policy evaluation evidence", r"\bevaluation|impact|outcome|effectiveness|assessment\b"),
            ("intervention evidence", r"\bintervention|program|initiative|reform|implementation\b"),
            ("guideline or framework evidence", r"\bguideline|recommendation|framework|standard\b"),
            ("governance or regulation evidence", r"\bgovernance|regulation|regulatory|law|compliance\b"),
            ("review evidence", r"\breview|systematic review|meta-analysis|scoping review\b"),
        ),
    )
)
