from __future__ import annotations

from evidencemap.cartridges.common.scholarly import ScholarlyCartridgeConfig, make_scholarly_cartridge


AI_CS_CARTRIDGE = make_scholarly_cartridge(
    ScholarlyCartridgeConfig(
        id="ai_cs",
        name="AI/CS EvidenceMap",
        description="Public AI and computer-science evidence mapping from OpenAlex scholarly metadata.",
        aliases={
            "ai": {"ai", "artificial intelligence", "machine learning", "deep learning", "neural", "model"},
            "benchmark": {"benchmark", "evaluation", "performance", "accuracy", "leaderboard"},
            "dataset": {"dataset", "corpus", "data", "training", "test set"},
            "method": {"method", "algorithm", "architecture", "framework", "approach"},
        },
        theme_rules=(
            ("method evidence", r"\bmethod|algorithm|architecture|framework|approach|model\b"),
            ("benchmark evidence", r"\bbenchmark|evaluation|performance|accuracy|leaderboard|baseline\b"),
            ("dataset evidence", r"\bdataset|corpus|training data|test set|annotation\b"),
            ("implementation evidence", r"\bcode|implementation|software|repository|open source\b"),
            ("survey evidence", r"\bsurvey|review|systematic review|overview\b"),
        ),
    )
)
