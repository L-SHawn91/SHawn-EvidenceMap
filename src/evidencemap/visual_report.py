from __future__ import annotations

import html
from collections import Counter
from datetime import date

from .models import EvidenceMap


def to_visual_html(evidence_map: EvidenceMap) -> str:
    counts = Counter(row.evidence_type for row in evidence_map.rows)
    years = sorted([row.year for row in evidence_map.rows if row.year])
    source_counts = Counter(source_label(row.source_url) for row in evidence_map.rows)
    max_count = max(counts.values(), default=1)
    year_counts = Counter(years)
    max_year_count = max(year_counts.values(), default=1)
    top_rows = evidence_map.rows[:5]
    coverage_score = report_score(evidence_map)
    confidence_label = confidence_band(coverage_score)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SHawn EvidenceMap Report</title>
  <style>
    :root {{
      --ink: #17202a;
      --muted: #5d6978;
      --line: #d9e0e8;
      --bg: #f8fafc;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-soft: #ccfbf1;
      --accent-mid: #14b8a6;
      --blue: #2563eb;
      --blue-soft: #dbeafe;
      --green: #16a34a;
      --green-soft: #dcfce7;
      --rose: #be123c;
      --rose-soft: #ffe4e6;
      --warn: #b45309;
      --warn-soft: #fffbeb;
      --shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        linear-gradient(180deg, #ecfeff 0, rgba(248, 250, 252, 0) 310px),
        var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 40px 0 64px; }}
    .cover {{ display: grid; gap: 16px; padding: 40px 0 28px; border-bottom: 1px solid var(--line); }}
    .eyebrow {{ color: var(--accent); font-size: 0.82rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0; }}
    h1 {{ margin: 0; max-width: 940px; font-size: clamp(2.2rem, 6vw, 4.8rem); line-height: 1; letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 1.45rem; letter-spacing: 0; }}
    h3 {{ margin: 0 0 8px; font-size: 1rem; }}
    p {{ margin: 0; color: var(--muted); }}
    ul {{ margin: 0; padding-left: 1.25rem; color: var(--muted); }}
    li {{ margin: 8px 0; }}
    section {{ padding: 30px 0; border-bottom: 1px solid var(--line); }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .pill {{ border: 1px solid var(--line); border-radius: 999px; background: white; padding: 6px 10px; font-size: 0.86rem; color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .grid.two {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .grid.four {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .card {{ border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 16px; box-shadow: var(--shadow); }}
    .metric {{ font-size: 2rem; font-weight: 800; color: var(--accent); line-height: 1; }}
    .metric.blue {{ color: var(--blue); }}
    .metric.green {{ color: var(--green); }}
    .metric.warn {{ color: var(--warn); }}
    .hero-panel {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      align-items: stretch;
    }}
    .verdict {{
      display: grid;
      gap: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 22px;
      box-shadow: var(--shadow);
    }}
    .verdict h2 {{ font-size: 1.8rem; margin: 0; }}
    .score-ring {{
      width: 170px;
      height: 170px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      margin: auto;
      background: conic-gradient(var(--accent) {coverage_score * 3.6}deg, #e5e7eb 0deg);
    }}
    .score-inner {{
      width: 126px;
      height: 126px;
      border-radius: 50%;
      background: white;
      display: grid;
      place-items: center;
      text-align: center;
      padding: 12px;
    }}
    .score-inner strong {{ display: block; font-size: 2rem; line-height: 1; }}
    .score-inner span {{ color: var(--muted); font-size: 0.78rem; }}
    .matrix {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .signal {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #ffffff;
    }}
    .signal strong {{ display: block; margin-bottom: 4px; }}
    .signal.good {{ background: var(--green-soft); border-color: #bbf7d0; }}
    .signal.mid {{ background: var(--blue-soft); border-color: #bfdbfe; }}
    .signal.watch {{ background: var(--warn-soft); border-color: #fde68a; }}
    .signal.risk {{ background: var(--rose-soft); border-color: #fecdd3; }}
    .bar-row {{ display: grid; grid-template-columns: 220px minmax(0, 1fr) 40px; gap: 10px; align-items: center; margin: 10px 0; }}
    .bar-bg {{ height: 12px; border-radius: 999px; background: #e5e7eb; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: var(--accent); }}
    .bar-fill.blue {{ background: var(--blue); }}
    .bar-fill.green {{ background: var(--green); }}
    .bar-fill.warn {{ background: var(--warn); }}
    .mini-bars {{ display: grid; gap: 8px; }}
    .mini-bar-row {{ display: grid; grid-template-columns: 120px minmax(0, 1fr) 32px; gap: 8px; align-items: center; color: var(--muted); font-size: 0.86rem; }}
    .mini-bar-bg {{ height: 8px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }}
    .mini-bar-fill {{ height: 100%; background: var(--blue); }}
    .timeline {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(38px, 1fr));
      align-items: end;
      gap: 8px;
      min-height: 180px;
      padding-top: 14px;
    }}
    .timeline-col {{ display: grid; gap: 6px; align-items: end; text-align: center; color: var(--muted); font-size: 0.75rem; }}
    .timeline-bar {{ min-height: 8px; border-radius: 6px 6px 0 0; background: linear-gradient(180deg, var(--accent-mid), var(--accent)); }}
    .flow {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
    .flow-step {{ position: relative; border: 1px solid var(--line); border-radius: 8px; background: white; padding: 14px; }}
    .flow-step::after {{ content: "→"; position: absolute; right: -12px; top: 50%; transform: translateY(-50%); color: var(--muted); }}
    .flow-step:last-child::after {{ content: ""; }}
    .rank {{ color: var(--accent); font-weight: 800; font-size: 0.82rem; text-transform: uppercase; }}
    .top-card {{ display: grid; gap: 8px; }}
    .tag {{ display: inline-flex; width: fit-content; border-radius: 999px; background: var(--accent-soft); color: #115e59; padding: 4px 8px; font-weight: 700; font-size: 0.78rem; }}
    .tag.blue {{ background: var(--blue-soft); color: #1d4ed8; }}
    .tag.warn {{ background: var(--warn-soft); color: #92400e; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; background: white; }}
    table {{ width: 100%; min-width: 980px; border-collapse: collapse; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 0.9rem; }}
    th {{ color: var(--muted); font-size: 0.76rem; text-transform: uppercase; }}
    .note {{ border-left: 4px solid var(--warn); padding: 12px 14px; background: #fffbeb; color: #713f12; }}
    .callout {{ border-left: 4px solid var(--accent); padding: 14px 16px; background: #f0fdfa; color: #134e4a; }}
    .footer {{ color: var(--muted); font-size: 0.9rem; }}
    .print-button {{
      position: fixed;
      right: 18px;
      bottom: 18px;
      border: 0;
      border-radius: 999px;
      background: var(--ink);
      color: white;
      padding: 10px 14px;
      font-weight: 800;
      box-shadow: var(--shadow);
      cursor: pointer;
    }}
    @media print {{
      body {{ background: white; }}
      main {{ width: auto; padding: 24px; }}
      section {{ break-inside: avoid; }}
      .card, .table-wrap {{ break-inside: avoid; }}
      .print-button {{ display: none; }}
    }}
    @media (max-width: 840px) {{
      .grid, .grid.two, .grid.four, .hero-panel, .flow, .matrix {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 1fr; }}
      .flow-step::after {{ content: ""; }}
    }}
  </style>
</head>
<body>
<main>
  <header class="cover">
    <div class="eyebrow">SHawn EvidenceMap · Client-Ready Evidence Brief</div>
    <h1>{esc(evidence_map.query)}</h1>
    <div class="meta">
      <span class="pill">Date: {date.today().isoformat()}</span>
      <span class="pill">Cartridge: {esc(evidence_map.cartridge)}</span>
      <span class="pill">Rows: {len(evidence_map.rows)}</span>
      <span class="pill">Evidence score: {coverage_score}/100</span>
      <span class="pill">Confidence: {confidence_label}</span>
      <span class="pill">Pilot deliverable</span>
    </div>
  </header>

  <section>
    <div class="hero-panel">
      <div class="verdict">
        <div class="eyebrow">Executive Verdict</div>
        <h2>{esc(executive_verdict(evidence_map))}</h2>
        <p>{esc(interpretation(evidence_map))}</p>
        <div class="callout">{esc(commercial_readout(evidence_map))}</div>
      </div>
      <div class="card">
        <div class="score-ring">
          <div class="score-inner">
            <div>
              <strong>{coverage_score}</strong>
              <span>evidence brief score</span>
            </div>
          </div>
        </div>
        <p style="text-align:center; margin-top:14px;">{confidence_label} confidence for a first-pass evidence brief</p>
      </div>
    </div>
  </section>

  <section>
    <h2>Executive Snapshot</h2>
    <div class="grid four">
      <div class="card"><div class="metric">{len(evidence_map.rows)}</div><p>ranked evidence rows</p></div>
      <div class="card"><div class="metric blue">{len(counts)}</div><p>evidence categories</p></div>
      <div class="card"><div class="metric green">{year_span(years)}</div><p>year coverage</p></div>
      <div class="card"><div class="metric warn">{len(source_counts)}</div><p>source families</p></div>
    </div>
  </section>

  <section>
    <h2>Key Findings</h2>
    {key_findings_html(evidence_map)}
  </section>

  <section>
    <h2>Evidence Dashboard</h2>
    <div class="grid two">
      <div class="card">
        <h3>Evidence Mix</h3>
        {evidence_mix_html(counts, max_count)}
      </div>
      <div class="card">
        <h3>Source Coverage</h3>
        {source_mix_html(source_counts)}
      </div>
    </div>
  </section>

  <section>
    <h2>Year Timeline</h2>
    {year_timeline_html(year_counts, max_year_count)}
  </section>

  <section>
    <h2>Quality Signals</h2>
    {quality_signals_html(evidence_map)}
  </section>

  <section>
    <h2>Top Evidence</h2>
    <div class="grid">
      {top_cards_html(top_rows)}
    </div>
  </section>

  <section>
    <h2>Ranked Evidence Table</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th><th>Evidence</th><th>Year</th><th>Paper</th><th>Rationale</th><th>Support sentence</th><th>Source</th>
          </tr>
        </thead>
        <tbody>
          {table_rows_html(evidence_map)}
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Initial Interpretation</h2>
    <p>{esc(interpretation(evidence_map))}</p>
  </section>

  <section>
    <h2>Evidence Gap Check</h2>
    {gap_check_html(evidence_map)}
  </section>

  <section>
    <h2>Action Plan</h2>
    {action_plan_html(evidence_map)}
  </section>

  <section>
    <h2>Delivery Package</h2>
    <div class="grid">
      <div class="card"><h3>Visual Brief</h3><p>User-facing HTML/PDF-ready report with evidence dashboard and top sources.</p></div>
      <div class="card"><h3>Evidence Table</h3><p>Ranked table with evidence label, support sentence, source link, and quality rationale.</p></div>
      <div class="card"><h3>Follow-up Plan</h3><p>Clear next steps for deeper manual review, report expansion, or workflow refinement.</p></div>
    </div>
  </section>

  <section>
    <h2>QA and Limitations</h2>
    <div class="note">
      Public metadata may be incomplete or duplicated. Ranking is a triage signal, not a quality appraisal.
      This report does not verify full text, methods quality, statistical validity, legal status, clinical recommendations, or patent claims.
    </div>
  </section>

  <p class="footer">Prepared as a SHawn EvidenceMap preliminary report. Pilot requests: https://github.com/L-SHawn91/SHawn-EvidenceMap/discussions/9</p>
</main>
<button class="print-button" onclick="window.print()">Export PDF</button>
</body>
</html>"""


def evidence_mix_html(counts: Counter[str], max_count: int) -> str:
    if not counts:
        return "<p>No evidence rows returned.</p>"
    rows = []
    for label, count in counts.most_common():
        width = round((count / max_count) * 100)
        rows.append(
            f'<div class="bar-row"><div>{esc(label)}</div><div class="bar-bg"><div class="bar-fill" style="width:{width}%"></div></div><div>{count}</div></div>'
        )
    return "\n".join(rows)


def year_timeline_html(counts: Counter[int], max_count: int) -> str:
    if not counts:
        return "<p>Year metadata not available.</p>"
    rows = []
    for year in sorted(counts):
        count = counts[year]
        height = max(8, round((count / max_count) * 150))
        rows.append(
            f'<div class="timeline-col"><div class="timeline-bar" style="height:{height}px"></div><div>{year}</div><strong>{count}</strong></div>'
        )
    return '<div class="timeline">' + "\n".join(rows) + "</div>"


def source_mix_html(counts: Counter[str]) -> str:
    if not counts:
        return "<p>No source metadata available.</p>"
    max_count = max(counts.values(), default=1)
    rows = []
    for label, count in counts.most_common():
        width = round((count / max_count) * 100)
        rows.append(
            f'<div class="mini-bar-row"><div>{esc(label)}</div><div class="mini-bar-bg"><div class="mini-bar-fill" style="width:{width}%"></div></div><div>{count}</div></div>'
        )
    return '<div class="mini-bars">' + "\n".join(rows) + "</div>"


def top_cards_html(rows) -> str:
    if not rows:
        return '<div class="card"><p>No top evidence available.</p></div>'
    cards = []
    for idx, row in enumerate(rows, start=1):
        cards.append(
            f"""<div class="card top-card">
  <div class="rank">Rank {idx}</div>
  <span class="tag">{esc(row.evidence_type)}</span>
  <h3>{esc(row.title)}</h3>
  <p>{esc(str(row.year or "Year unavailable"))}</p>
  <p>{esc(row.support_sentence)}</p>
</div>"""
        )
    return "\n".join(cards)


def key_findings_html(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return "<p>No findings available because no evidence rows were returned.</p>"
    items = []
    for idx, row in enumerate(evidence_map.rows[:3], start=1):
        items.append(
            f"<li><strong>Finding {idx}:</strong> {esc(row.evidence_type)} is represented by <em>{esc(row.title)}</em>{f' ({row.year})' if row.year else ''}. {esc(row.support_sentence)}</li>"
        )
    return "<ul>" + "\n".join(items) + "</ul>"


def quality_signals_html(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return '<div class="note">No evidence rows were returned. Re-run with broader terms before delivery.</div>'
    rows = evidence_map.rows
    support_ratio = round(100 * sum(bool(row.support_sentence) for row in rows) / len(rows))
    year_ratio = round(100 * sum(bool(row.year) for row in rows) / len(rows))
    source_ratio = min(100, len({source_label(row.source_url) for row in rows}) * 25)
    diversity_ratio = min(100, len({row.evidence_type for row in rows}) * 25)
    return f"""<div class="matrix">
  <div class="signal {signal_class(support_ratio)}"><strong>Support Sentence Coverage</strong><div class="metric">{support_ratio}%</div><p>Rows with an extracted sentence that can be checked by a reviewer.</p></div>
  <div class="signal {signal_class(year_ratio)}"><strong>Year Metadata Coverage</strong><div class="metric blue">{year_ratio}%</div><p>Rows with usable publication year metadata for timeline interpretation.</p></div>
  <div class="signal {signal_class(source_ratio)}"><strong>Source Breadth</strong><div class="metric green">{source_ratio}%</div><p>Public source diversity proxy based on link families in the ranked table.</p></div>
  <div class="signal {signal_class(diversity_ratio)}"><strong>Evidence Label Diversity</strong><div class="metric warn">{diversity_ratio}%</div><p>Whether the map has multiple evidence types rather than one narrow cluster.</p></div>
</div>"""


def gap_check_html(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return '<div class="note">No evidence rows were returned. Broaden the query before delivery.</div>'
    counts = Counter(row.evidence_type for row in evidence_map.rows)
    dominant, dominant_count = counts.most_common(1)[0]
    gaps = []
    if len(counts) == 1 and len(evidence_map.rows) >= 3:
        gaps.append(f"Evidence is concentrated in one category: {dominant}. Add query variants to test for missing evidence types.")
    if any(not row.support_sentence for row in evidence_map.rows):
        gaps.append("Some rows lack support sentences. Manual abstract/full-text review is recommended.")
    if all((row.year or 0) < 2020 for row in evidence_map.rows):
        gaps.append("Most evidence appears older. Add a recent-mode run before delivery.")
    if not gaps:
        gaps.append(f"Evidence is sufficiently clustered for a first-pass brief. Dominant signal: {dominant} ({dominant_count} rows).")
    return "<ul>" + "\n".join(f"<li>{esc(gap)}</li>" for gap in gaps) + "</ul>"


def action_plan_html(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return '<div class="note">No action plan can be generated until the query returns evidence rows.</div>'
    return """<div class="flow">
  <div class="flow-step"><div class="rank">Step 1</div><h3>Verify</h3><p>Open top sources and confirm title, abstract, date, and fit to the client question.</p></div>
  <div class="flow-step"><div class="rank">Step 2</div><h3>Refine</h3><p>Add synonyms, comparator terms, and exclusion terms to reduce noise.</p></div>
  <div class="flow-step"><div class="rank">Step 3</div><h3>Deepen</h3><p>Separate recent, foundational, and application-oriented evidence runs.</p></div>
  <div class="flow-step"><div class="rank">Step 4</div><h3>Deliver</h3><p>Package a verified PDF, evidence table, and short recommendation memo.</p></div>
</div>"""


def table_rows_html(evidence_map: EvidenceMap) -> str:
    rows = []
    for idx, row in enumerate(evidence_map.rows, start=1):
        rows.append(
            f"<tr><td>{idx}</td><td>{esc(row.evidence_type)}</td><td>{esc(str(row.year or ''))}</td><td>{esc(row.title)}</td><td>{esc(row.rationale)}</td><td>{esc(row.support_sentence)}</td><td><a href=\"{esc(row.source_url)}\">source</a></td></tr>"
        )
    return "\n".join(rows)


def executive_verdict(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return "No deliverable signal yet"
    score = report_score(evidence_map)
    if score >= 80:
        return "Strong first-pass evidence signal"
    if score >= 60:
        return "Usable pilot evidence signal"
    if score >= 40:
        return "Partial signal, needs refinement"
    return "Weak signal, broaden the search"


def commercial_readout(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return "Review readiness: not ready. Broaden or rewrite the research question first."
    score = report_score(evidence_map)
    if score >= 70:
        return "Review readiness: suitable as a first-pass evidence brief after manual verification of top sources."
    return "Review readiness: suitable as an internal scoping run; strengthen it before external use."


def interpretation(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return "No ranked evidence rows were returned. The query should be broadened or rewritten."
    counts = Counter(row.evidence_type for row in evidence_map.rows)
    dominant = counts.most_common(1)[0][0]
    top = evidence_map.rows[0]
    return (
        f"The strongest current signal is {dominant}. The top-ranked source is {top.title}"
        f"{f' ({top.year})' if top.year else ''}. Manual verification is required before using this as an external conclusion."
    )


def report_score(evidence_map: EvidenceMap) -> int:
    rows = evidence_map.rows
    if not rows:
        return 0
    row_score = min(30, len(rows) * 4)
    support_score = round(25 * sum(bool(row.support_sentence) for row in rows) / len(rows))
    year_score = round(15 * sum(bool(row.year) for row in rows) / len(rows))
    diversity_score = min(15, len({row.evidence_type for row in rows}) * 5)
    source_score = min(15, len({source_label(row.source_url) for row in rows}) * 5)
    return min(100, row_score + support_score + year_score + diversity_score + source_score)


def confidence_band(score: int) -> str:
    if score >= 80:
        return "High"
    if score >= 60:
        return "Medium"
    if score >= 40:
        return "Low-medium"
    return "Low"


def signal_class(score: int) -> str:
    if score >= 80:
        return "good"
    if score >= 60:
        return "mid"
    if score >= 40:
        return "watch"
    return "risk"


def source_label(url: str) -> str:
    value = (url or "").lower()
    if "pubmed" in value or "ncbi.nlm.nih.gov" in value:
        return "PubMed"
    if "europepmc" in value:
        return "Europe PMC"
    if "doi.org" in value:
        return "DOI"
    if "openalex" in value:
        return "OpenAlex"
    if not value:
        return "Unknown"
    return "Other"


def year_span(years: list[int]) -> str:
    if not years:
        return "N/A"
    if min(years) == max(years):
        return str(min(years))
    return f"{min(years)}-{max(years)}"


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)
