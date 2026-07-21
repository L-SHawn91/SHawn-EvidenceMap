"""SHawn EvidenceMap public package."""

from ._version import __version__
from .models import EvidenceMap, EvidenceRow, Paper, StatementResult
from .pipeline import build_evidence_map

__all__ = [
    "EvidenceMap",
    "EvidenceRow",
    "Paper",
    "StatementResult",
    "__version__",
    "build_evidence_map",
]
