# Research Report Template

PUBLIC_STATUS: public-demo

SHawn EvidenceMap reports use a fixed Markdown structure so public review artifacts are consistent across cartridges.

## Fixed Sections

1. Executive Summary
2. Scope
3. Method Snapshot
4. Evidence Mix
5. Year Coverage
6. Ranked Evidence Table
7. Preliminary Triage Note
8. Recommended Next Steps
9. Limitations
10. Delivery Note

## Generate

```bash
PYTHONPATH=src python3 -m evidencemap.cli "research question" --cartridge bio --limit 10 --report
```

Generate a review-ready visual brief:

```bash
PYTHONPATH=src python3 -m evidencemap.cli "research question" --cartridge bio --limit 10 --html-report > report.html
```

## Visual Brief Sections

1. Cover
2. Executive Triage Status
3. Metadata Triage Score
4. Executive Snapshot
5. Top Candidate Records
6. Evidence Dashboard
7. Source Coverage
8. Year Timeline
9. Quality Signals
10. Top Candidate Evidence
11. Ranked Evidence Table
12. Preliminary Triage Note
13. Evidence Gap Check
14. Action Plan
15. Delivery Package
16. QA and Limitations

## Visual Brief Standard

The HTML brief is the preferred user-facing review artifact. It should help a reviewer answer five questions quickly:

- Is there enough public evidence signal to continue?
- Which evidence category dominates the first pass?
- Which top sources should be manually verified first?
- Where are the gaps or risks?
- What is the next manual review step?

The report includes an `Export PDF` button so the same HTML can be printed or saved as a PDF for review.

## Boundary

Reports are preliminary research-planning outputs. They require manual verification before citation, manuscript use, clinical interpretation, policy recommendations, investment decisions, or public claims.
