# Customer Report Template

PUBLIC_STATUS: public-demo

SHawn EvidenceMap customer reports use a fixed Markdown structure so pilot deliverables are consistent across cartridges.

## Fixed Sections

1. Executive Summary
2. Scope
3. Method Snapshot
4. Evidence Mix
5. Year Coverage
6. Ranked Evidence Table
7. Initial Interpretation
8. Recommended Next Steps
9. Limitations
10. Delivery Note

## Generate

```bash
PYTHONPATH=src python3 -m evidencemap.cli "research question" --cartridge bio --limit 10 --report
```

## Boundary

Reports are preliminary research-planning outputs. They require manual verification before citation, manuscript use, clinical interpretation, policy recommendations, investment decisions, or public claims.
