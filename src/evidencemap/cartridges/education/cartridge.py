from __future__ import annotations

from evidencemap.cartridges.common.scholarly import ScholarlyCartridgeConfig, make_scholarly_cartridge


EDUCATION_CARTRIDGE = make_scholarly_cartridge(
    ScholarlyCartridgeConfig(
        id="education",
        name="Education EvidenceMap",
        description="Public education research evidence mapping from OpenAlex scholarly metadata.",
        aliases={
            "education": {"education", "learning", "teaching", "student", "classroom", "school"},
            "intervention": {"intervention", "program", "curriculum", "pedagogy", "instruction"},
            "outcome": {"outcome", "achievement", "performance", "attainment", "learning gain"},
            "study": {"trial", "experiment", "cohort", "meta-analysis", "systematic review"},
        },
        theme_rules=(
            ("intervention evidence", r"\bintervention|program|curriculum|pedagogy|instruction\b"),
            ("learning outcome evidence", r"\boutcome|achievement|performance|attainment|learning gain\b"),
            ("experimental or cohort evidence", r"\btrial|experiment|cohort|longitudinal|quasi-experimental\b"),
            ("review evidence", r"\bmeta-analysis|systematic review|scoping review|review\b"),
            ("technology-enhanced learning evidence", r"\bonline learning|e-learning|digital learning|learning analytics\b"),
        ),
    )
)
