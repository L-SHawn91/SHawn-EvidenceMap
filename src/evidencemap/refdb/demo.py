from __future__ import annotations

import html
import json
from typing import Any, Mapping

from .schema import SCHEMA_VERSION
from .store import ReferenceStore


def build_synthetic_demo(store: ReferenceStore) -> None:
    """Populate a deterministic six-entity reference graph."""
    paper_a = store.upsert_entity(
        kind="paper",
        title="Synthetic Repair Biology paper A",
        identifiers={"doi": "10.0000/SYNTHETIC.REPAIR.001"},
        metadata={"data_class": "synthetic"},
    )
    paper_b = store.upsert_entity(
        kind="paper",
        title="Synthetic Repair Biology paper B",
        identifiers={"pmid": "PMID:00000010"},
        metadata={"data_class": "synthetic"},
    )
    dataset_a = store.upsert_entity(
        kind="dataset",
        title="Synthetic gene expression matrix",
        identifiers={"accession": "demo-ds-001"},
        metadata={"data_class": "synthetic"},
    )
    dataset_b = store.upsert_entity(
        kind="dataset",
        title="Synthetic single-cell matrix",
        identifiers={"accession": "demo-ds-002"},
        metadata={"data_class": "synthetic"},
    )
    claim_a = store.upsert_entity(
        kind="claim",
        title="Synthetic claim: treatment improves repair",
        identifiers={"demo_id": "claim-001"},
        metadata={"data_class": "synthetic"},
    )
    claim_b = store.upsert_entity(
        kind="claim",
        title="Synthetic claim: gene signature persists",
        identifiers={"demo_id": "claim-002"},
        metadata={"data_class": "synthetic"},
    )

    for source_id, target_id, relation in (
        (paper_a, dataset_a, "produces"),
        (paper_a, dataset_b, "produces"),
        (paper_b, dataset_a, "supports"),
        (claim_a, paper_a, "supported_by"),
        (claim_b, paper_b, "supported_by"),
    ):
        store.add_relation(source_id, target_id, relation)

    provenance = (
        (paper_a, "example://paper/repair-a", "2026-01-01T00:00:00Z"),
        (paper_b, "example://paper/repair-b", "2026-01-01T00:00:00Z"),
        (dataset_a, "example://dataset/demo-ds-001", "2026-01-01T00:00:01Z"),
        (dataset_b, "example://dataset/demo-ds-002", "2026-01-01T00:00:01Z"),
        (claim_a, "example://claim/claim-001", "2026-01-01T00:00:02Z"),
        (claim_b, "example://claim/claim-002", "2026-01-01T00:00:02Z"),
    )
    for entity_id, source_ref, retrieved_at in provenance:
        store.add_provenance(
            entity_id,
            source="synthetic_fixture",
            source_ref=source_ref,
            retrieved_at=retrieved_at,
        )

    store.record_ingest_run(
        run_id="demo-run-001",
        source="synthetic_fixture",
        started_at="2026-01-01T00:00:00Z",
        finished_at="2026-01-01T00:00:02Z",
        record_count=6,
    )


def render_demo_page(export_data: str | Mapping[str, Any]) -> str:
    """Render canonical export data as a deterministic, escaped static page."""
    payload = json.loads(export_data) if isinstance(export_data, str) else dict(export_data)
    counts = payload.get("counts", {})
    entities = payload.get("entities", [])
    relations = payload.get("relations", [])
    provenance = payload.get("provenance", [])
    ingest_runs = payload.get("ingest_runs", [])

    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    entity_rows = "".join(
        "<tr>"
        f"<td data-label=\"Kind\"><span class=\"kind {esc(entity.get('kind', ''))}\">{esc(entity.get('kind', ''))}</span></td>"
        f"<td data-label=\"Title\"><strong>{esc(entity.get('title', ''))}</strong></td>"
        f"<td data-label=\"Identifier\"><code>{esc(_identifier_text(entity.get('identifiers', {})))}</code></td>"
        "</tr>"
        for entity in entities
    )
    relation_rows = "".join(
        "<tr>"
        f"<td data-label=\"Source\"><code>{esc(row.get('source', ''))}</code></td>"
        f"<td data-label=\"Relation\"><span class=\"relation\">{esc(row.get('relation', ''))}</span></td>"
        f"<td data-label=\"Target\"><code>{esc(row.get('target', ''))}</code></td>"
        "</tr>"
        for row in relations
    )
    provenance_rows = "".join(
        "<tr>"
        f"<td data-label=\"Entity\"><code>{esc(row.get('entity', ''))}</code></td>"
        f"<td data-label=\"Source\">{esc(row.get('source', ''))}</td>"
        f"<td data-label=\"Reference\"><code>{esc(row.get('source_ref', ''))}</code></td>"
        f"<td data-label=\"Retrieved\">{esc(row.get('retrieved_at', ''))}</td>"
        "</tr>"
        for row in provenance
    )
    run_rows = "".join(
        "<tr>"
        f"<td data-label=\"Run\"><code>{esc(row.get('run_id', ''))}</code></td>"
        f"<td data-label=\"Source\">{esc(row.get('source', ''))}</td>"
        f"<td data-label=\"Started\">{esc(row.get('started_at', ''))}</td>"
        f"<td data-label=\"Finished\">{esc(row.get('finished_at', ''))}</td>"
        f"<td data-label=\"Records\">{esc(row.get('record_count', ''))}</td>"
        "</tr>"
        for row in ingest_runs
    )

    cards = "".join(
        f'<div class="metric"><span>{esc(label)}</span><strong>{esc(counts.get(key, 0))}</strong></div>'
        for key, label in (
            ("entities", "Entities"),
            ("identifiers", "Identifiers"),
            ("relations", "Relations"),
            ("provenance", "Provenance"),
            ("ingest_runs", "Ingest runs"),
        )
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Synthetic database reference demo</title>
  <style>
    :root {{ --ink:#19231f; --muted:#66736d; --paper:#f6f3e9; --panel:#fffdf7; --sage:#2f6f61; --sage-soft:#dfece6; --gold:#b88732; --line:#d9ded8; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--paper); color:var(--ink); font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    main {{ width:min(1180px,calc(100% - 32px)); margin:0 auto; padding:54px 0 72px; }}
    .hero {{ padding:34px; border:1px solid var(--line); border-radius:20px; background:linear-gradient(135deg,#fffdf7 0%,#edf3ed 100%); box-shadow:0 18px 55px rgba(45,70,61,.08); }}
    .eyebrow {{ color:var(--sage); font-size:12px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }}
    h1 {{ max-width:800px; margin:10px 0 12px; font-size:clamp(34px,6vw,64px); line-height:1; letter-spacing:-.045em; }}
    .lead {{ max-width:760px; margin:0; color:var(--muted); font-size:18px; }}
    .badges {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; }}
    .badge {{ padding:7px 11px; border-radius:999px; background:var(--sage-soft); color:var(--sage); font-size:12px; font-weight:750; }}
    .actions {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:18px; }}
    .actions a {{ padding:9px 13px; border:1px solid var(--sage); border-radius:9px; color:var(--sage); font-size:13px; font-weight:750; text-decoration:none; }}
    .actions a:first-child {{ background:var(--sage); color:white; }}
    .boundary {{ margin-top:18px; padding:13px 15px; border-left:4px solid var(--gold); background:#fff8e7; border-radius:0 10px 10px 0; color:#5f4a24; }}
    .metrics {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; margin:24px 0; }}
    .metric {{ min-height:104px; padding:18px; border:1px solid var(--line); border-radius:15px; background:var(--panel); }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; font-weight:750; text-transform:uppercase; letter-spacing:.06em; }}
    .metric strong {{ display:block; margin-top:8px; color:var(--sage); font-size:34px; line-height:1; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
    section {{ margin-top:18px; padding:22px; border:1px solid var(--line); border-radius:16px; background:var(--panel); overflow:hidden; }}
    section.wide {{ grid-column:1/-1; }}
    h2 {{ margin:0 0 4px; font-size:21px; letter-spacing:-.02em; }}
    .section-note {{ margin:0 0 16px; color:var(--muted); font-size:13px; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ width:100%; border-collapse:collapse; min-width:560px; }}
    th,td {{ padding:11px 10px; border-bottom:1px solid #e5e8e3; text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:11px; letter-spacing:.07em; text-transform:uppercase; }}
    tbody tr:last-child td {{ border-bottom:0; }}
    code {{ color:#365149; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; overflow-wrap:anywhere; }}
    .kind,.relation {{ display:inline-flex; padding:4px 8px; border-radius:999px; font-size:11px; font-weight:800; white-space:nowrap; }}
    .kind {{ background:var(--sage-soft); color:var(--sage); }}
    .kind.dataset {{ background:#f6ead2; color:#875f1e; }}
    .kind.claim {{ background:#e9e5f5; color:#5d4b87; }}
    .relation {{ background:#eef1ed; color:#53615b; }}
    footer {{ margin-top:22px; color:var(--muted); font-size:13px; text-align:center; }}
    @media (max-width:820px) {{
      .metrics {{ grid-template-columns:repeat(2,1fr); }}
      .grid {{ grid-template-columns:1fr; }}
      section.wide {{ grid-column:auto; }}
      .hero {{ padding:24px; }}
      table,tbody,tr,td {{ display:block; width:100%; min-width:0; }}
      thead {{ position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }}
      tbody tr {{ padding:10px 0; border-bottom:1px solid #e5e8e3; }}
      tbody tr:last-child {{ border-bottom:0; }}
      td,tbody tr:last-child td {{ display:grid; grid-template-columns:82px minmax(0,1fr); gap:10px; padding:4px 0; border:0; overflow-wrap:anywhere; }}
      td::before {{ content:attr(data-label); color:var(--muted); font-size:10px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; }}
    }}
  </style>
</head>
<body>
<main>
  <header class="hero">
    <div class="eyebrow">SHawn EvidenceMap · SQLite reference</div>
    <h1>Synthetic database reference demo</h1>
    <p class="lead">Papers, datasets, claims, provenance, and relations are persisted in a deterministic SQLite reference store and exported as a static, inspectable report.</p>
    <div class="badges"><span class="badge">Synthetic metadata only</span><span class="badge">Schema v{esc(payload.get('schema_version', SCHEMA_VERSION))}</span><span class="badge">Foreign keys enabled</span><span class="badge">Canonical export</span></div>
    <div class="actions"><a href="reference.json">Inspect canonical JSON</a><a href="https://github.com/L-SHawn91/SHawn-EvidenceMap/blob/main/docs/DATABASE_REFERENCE.md">Read schema and boundary docs</a></div>
    <div class="boundary"><strong>Public boundary:</strong> No private corpus, manuscript, or operational database is included.</div>
  </header>
  <div class="metrics">{cards}</div>
  <div class="grid">
    <section><h2>Entities</h2><p class="section-note">Typed records with normalized stable identifiers.</p><div class="table-wrap"><table><thead><tr><th>Kind</th><th>Title</th><th>Identifier</th></tr></thead><tbody>{entity_rows}</tbody></table></div></section>
    <section><h2>Relations</h2><p class="section-note">Explicit links connecting claims, papers, and datasets.</p><div class="table-wrap"><table><thead><tr><th>Source</th><th>Relation</th><th>Target</th></tr></thead><tbody>{relation_rows}</tbody></table></div></section>
    <section class="wide"><h2>Provenance</h2><p class="section-note">Source references and fixed retrieval timestamps for deterministic verification.</p><div class="table-wrap"><table><thead><tr><th>Entity</th><th>Source</th><th>Reference</th><th>Retrieved</th></tr></thead><tbody>{provenance_rows}</tbody></table></div></section>
    <section class="wide"><h2>Ingest runs</h2><p class="section-note">Idempotent build metadata for the generated example.</p><div class="table-wrap"><table><thead><tr><th>Run</th><th>Source</th><th>Started</th><th>Finished</th><th>Records</th></tr></thead><tbody>{run_rows}</tbody></table></div></section>
  </div>
  <footer>Generated deterministically by SHawn EvidenceMap · Apache-2.0 · manual verification required for real research use</footer>
</main>
</body>
</html>"""


def _identifier_text(identifiers: Any) -> str:
    if not isinstance(identifiers, Mapping):
        return ""
    return ", ".join(f"{key}:{value}" for key, value in sorted(identifiers.items()))
