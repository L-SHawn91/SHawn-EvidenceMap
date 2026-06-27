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

Generate a client-ready visual brief:

```bash
PYTHONPATH=src python3 -m evidencemap.cli "research question" --cartridge bio --limit 10 --html-report > report.html
```

## Visual Brief Sections

1. Cover
2. Executive Snapshot
3. Key Findings
4. Evidence Mix
5. Year Timeline
6. Top Evidence
7. Ranked Evidence Table
8. Initial Interpretation
9. Evidence Gap Check
10. Action Plan
11. Delivery Package
12. QA and Limitations

## Boundary

Reports are preliminary research-planning outputs. They require manual verification before citation, manuscript use, clinical interpretation, policy recommendations, investment decisions, or public claims.
