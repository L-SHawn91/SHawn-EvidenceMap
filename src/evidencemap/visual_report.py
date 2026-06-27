from __future__ import annotations

import html
from collections import Counter
from datetime import date

from .models import EvidenceMap


def to_visual_html(evidence_map: EvidenceMap) -> str:
    counts = Counter(row.evidence_type for row in evidence_map.rows)
    years = sorted([row.year for row in evidence_map.rows if row.year])
    max_count = max(counts.values(), default=1)
    year_counts = Counter(years)
    max_year_count = max(year_counts.values(), default=1)
    top_rows = evidence_map.rows[:3]
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
      --warn: #b45309;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
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
    section {{ padding: 30px 0; border-bottom: 1px solid var(--line); }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .pill {{ border: 1px solid var(--line); border-radius: 999px; background: white; padding: 6px 10px; font-size: 0.86rem; color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .card {{ border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 16px; }}
    .metric {{ font-size: 2rem; font-weight: 800; color: var(--accent); line-height: 1; }}
    .bar-row {{ display: grid; grid-template-columns: 220px minmax(0, 1fr) 40px; gap: 10px; align-items: center; margin: 10px 0; }}
    .bar-bg {{ height: 12px; border-radius: 999px; background: #e5e7eb; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: var(--accent); }}
    .top-card {{ display: grid; gap: 8px; }}
    .tag {{ display: inline-flex; width: fit-content; border-radius: 999px; background: var(--accent-soft); color: #115e59; padding: 4px 8px; font-weight: 700; font-size: 0.78rem; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; background: white; }}
    table {{ width: 100%; min-width: 980px; border-collapse: collapse; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 0.9rem; }}
    th {{ color: var(--muted); font-size: 0.76rem; text-transform: uppercase; }}
    .note {{ border-left: 4px solid var(--warn); padding: 12px 14px; background: #fffbeb; color: #713f12; }}
    .footer {{ color: var(--muted); font-size: 0.9rem; }}
    @media print {{
      body {{ background: white; }}
      main {{ width: auto; padding: 24px; }}
      section {{ break-inside: avoid; }}
      .card, .table-wrap {{ break-inside: avoid; }}
    }}
    @media (max-width: 840px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 1fr; }}
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
      <span class="pill">Pilot deliverable</span>
    </div>
  </header>

  <section>
    <h2>Executive Snapshot</h2>
    <div class="grid">
      <div class="card"><div class="metric">{len(evidence_map.rows)}</div><p>ranked evidence rows</p></div>
      <div class="card"><div class="metric">{len(counts)}</div><p>evidence categories</p></div>
      <div class="card"><div class="metric">{year_span(years)}</div><p>year coverage</p></div>
    </div>
  </section>

  <section>
    <h2>Key Findings</h2>
    {key_findings_html(evidence_map)}
  </section>

  <section>
    <h2>Evidence Mix</h2>
    {evidence_mix_html(counts, max_count)}
  </section>

  <section>
    <h2>Year Timeline</h2>
    {year_timeline_html(year_counts, max_year_count)}
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
    <div class="grid">
      <div class="card">
        <h3>Immediate</h3>
        <p>Review the top 5 sources and confirm whether the support sentences match the client question.</p>
      </div>
      <div class="card">
        <h3>Next Pass</h3>
        <p>Expand synonyms, add comparator terms, and split foundational versus recent evidence.</p>
      </div>
      <div class="card">
        <h3>Paid Upgrade</h3>
        <p>Add manual source verification, inclusion/exclusion notes, and a polished decision brief.</p>
      </div>
    </div>
  </section>

  <section>
    <h2>Delivery Package</h2>
    <div class="grid">
      <div class="card"><h3>Visual Brief</h3><p>Client-facing HTML/PDF-ready report with evidence dashboard and top sources.</p></div>
      <div class="card"><h3>Evidence Table</h3><p>Ranked table with evidence label, support sentence, source link, and quality rationale.</p></div>
      <div class="card"><h3>Follow-up Plan</h3><p>Clear next steps for deeper manual review, report expansion, or premium workflow.</p></div>
    </div>
  </section>

  <section>
    <h2>QA and Limitations</h2>
    <div class="note">
      Public metadata may be incomplete or duplicated. Ranking is a triage signal, not a quality appraisal.
      This report does not verify full text, methods quality, statistical validity, legal status, clinical recommendations, or patent claims.
    </div>
  </section>

  <p class="footer">Prepared as a SHawn EvidenceMap preliminary report. Contact: dr.shawn91@gmail.com</p>
</main>
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
        width = round((count / max_count) * 100)
        rows.append(
            f'<div class="bar-row"><div>{year}</div><div class="bar-bg"><div class="bar-fill" style="width:{width}%"></div></div><div>{count}</div></div>'
        )
    return "\n".join(rows)


def top_cards_html(rows) -> str:
    if not rows:
        return '<div class="card"><p>No top evidence available.</p></div>'
    cards = []
    for row in rows:
        cards.append(
            f"""<div class="card top-card">
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


def table_rows_html(evidence_map: EvidenceMap) -> str:
    rows = []
    for idx, row in enumerate(evidence_map.rows, start=1):
        rows.append(
            f"<tr><td>{idx}</td><td>{esc(row.evidence_type)}</td><td>{esc(str(row.year or ''))}</td><td>{esc(row.title)}</td><td>{esc(row.rationale)}</td><td>{esc(row.support_sentence)}</td><td><a href=\"{esc(row.source_url)}\">source</a></td></tr>"
        )
    return "\n".join(rows)


def interpretation(evidence_map: EvidenceMap) -> str:
    if not evidence_map.rows:
        return "No ranked evidence rows were returned. The query should be broadened or rewritten."
    counts = Counter(row.evidence_type for row in evidence_map.rows)
    dominant = counts.most_common(1)[0][0]
    top = evidence_map.rows[0]
    return (
        f"The strongest current signal is {dominant}. The top-ranked source is {top.title}"
        f"{f' ({top.year})' if top.year else ''}. Manual verification is required before using this as a client-facing conclusion."
    )


def year_span(years: list[int]) -> str:
    if not years:
        return "N/A"
    if min(years) == max(years):
        return str(min(years))
    return f"{min(years)}-{max(years)}"


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)
