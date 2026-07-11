from __future__ import annotations

import inspect

from evidencemap.cartridges import cartridge_ids, get_cartridge
from evidencemap.cli import build_parser
from evidencemap.models import Paper
from evidencemap.pipeline import build_evidence_map


def test_generic_cartridge_is_the_default_for_unscoped_queries() -> None:
    args = build_parser().parse_args(["open science metadata reproducibility"])

    assert "generic" in cartridge_ids()
    assert args.cartridge == "generic"
    assert inspect.signature(build_evidence_map).parameters["cartridge_id"].default == "generic"


def test_generic_cartridge_uses_neutral_evidence_labels() -> None:
    cartridge = get_cartridge("generic")
    paper = Paper(
        id="example",
        title="Open-source models for development of data and metadata standards",
        abstract="This article describes an open software framework and metadata standard.",
        url="https://example.org/public-record",
        source="openalex",
    )

    row = cartridge.paper_to_row("open science metadata reproducibility", paper)

    assert row.evidence_type in {
        "methodology evidence",
        "software or tool evidence",
        "data resource evidence",
        "empirical evidence",
        "review evidence",
        "background evidence",
    }
    assert row.evidence_type not in {
        "mechanistic evidence",
        "drug screening evidence",
        "model system evidence",
    }
