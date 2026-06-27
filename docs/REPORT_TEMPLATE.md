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
2. Executive Verdict
3. Evidence Score Ring
4. Executive Snapshot
5. Key Findings
6. Evidence Dashboard
7. Source Coverage
8. Year Timeline
9. Quality Signals
10. Top Evidence
11. Ranked Evidence Table
12. Initial Interpretation
13. Evidence Gap Check
14. Action Plan
15. Delivery Package
16. QA and Limitations

## Visual Brief Standard

The HTML brief is the preferred client-facing pilot deliverable. It should help a buyer answer five questions quickly:

- Is there enough public evidence signal to continue?
- Which evidence category dominates the first pass?
- Which top sources should be manually verified first?
- Where are the gaps or risks?
- What is the next paid step?

The report includes an `Export PDF` button so the same HTML can be printed or saved as a PDF for delivery.

## Boundary

Reports are preliminary research-planning outputs. They require manual verification before citation, manuscript use, clinical interpretation, policy recommendations, investment decisions, or public claims.
