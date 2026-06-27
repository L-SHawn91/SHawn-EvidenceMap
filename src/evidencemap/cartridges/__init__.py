from __future__ import annotations

from evidencemap.core.cartridge import EvidenceCartridge
from evidencemap.cartridges.bio import BIO_CARTRIDGE


CARTRIDGES: dict[str, EvidenceCartridge] = {
    BIO_CARTRIDGE.id: BIO_CARTRIDGE,
}


def get_cartridge(cartridge_id: str) -> EvidenceCartridge:
    try:
        return CARTRIDGES[cartridge_id]
    except KeyError as exc:
        available = ", ".join(sorted(CARTRIDGES))
        raise ValueError(f"Unknown cartridge '{cartridge_id}'. Available: {available}") from exc


def cartridge_ids() -> list[str]:
    return sorted(CARTRIDGES)
