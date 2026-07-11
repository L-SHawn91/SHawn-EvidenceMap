from __future__ import annotations

from evidencemap.cartridges.ai_cs import AI_CS_CARTRIDGE
from evidencemap.cartridges.bio import BIO_CARTRIDGE
from evidencemap.cartridges.education import EDUCATION_CARTRIDGE
from evidencemap.cartridges.generic import GENERIC_CARTRIDGE
from evidencemap.cartridges.legal import LEGAL_CARTRIDGE
from evidencemap.cartridges.patent_tech import PATENT_TECH_CARTRIDGE
from evidencemap.cartridges.policy import POLICY_CARTRIDGE
from evidencemap.core.cartridge import EvidenceCartridge


CARTRIDGES: dict[str, EvidenceCartridge] = {
    AI_CS_CARTRIDGE.id: AI_CS_CARTRIDGE,
    BIO_CARTRIDGE.id: BIO_CARTRIDGE,
    EDUCATION_CARTRIDGE.id: EDUCATION_CARTRIDGE,
    GENERIC_CARTRIDGE.id: GENERIC_CARTRIDGE,
    LEGAL_CARTRIDGE.id: LEGAL_CARTRIDGE,
    PATENT_TECH_CARTRIDGE.id: PATENT_TECH_CARTRIDGE,
    POLICY_CARTRIDGE.id: POLICY_CARTRIDGE,
}


def get_cartridge(cartridge_id: str) -> EvidenceCartridge:
    try:
        return CARTRIDGES[cartridge_id]
    except KeyError as exc:
        available = ", ".join(sorted(CARTRIDGES))
        raise ValueError(f"Unknown cartridge '{cartridge_id}'. Available: {available}") from exc


def cartridge_ids() -> list[str]:
    return sorted(CARTRIDGES)
