from __future__ import annotations

import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evidencemap.pipeline import build_evidence_map  # noqa: E402


HOST = "127.0.0.1"
PORT = 8765


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_file(ROOT / "web" / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path != "/demo":
            self.send_error(404)
            return
        params = parse_qs(parsed.query)
        query = (params.get("q") or [""])[0].strip()
        ranking_mode = (params.get("mode") or ["recent"])[0]
        if ranking_mode not in {"recent", "foundational", "balanced"}:
            ranking_mode = "recent"
        body = render_page(query=query, ranking_mode=ranking_mode)
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(404)
            return
        encoded = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("[EvidenceMap] " + fmt % args + "\n")


def render_page(query: str, ranking_mode: str) -> str:
    rows = ""
    status = "Enter a biomedical research question."
    if query:
        evidence_map = build_evidence_map(query, limit=10, ranking_mode=ranking_mode)
        status = f"{len(evidence_map.rows)} evidence rows · mode={ranking_mode}"
        rows = "\n".join(
            f"""
            <tr>
              <td>{escape(row.evidence_type)}</td>
              <td>{escape(str(row.year or ""))}</td>
              <td>{escape(row.title)}</td>
              <td>{escape(row.rationale)}</td>
              <td>{escape(row.support_sentence)}</td>
              <td><a href="{escape(row.source_url)}" target="_blank" rel="noreferrer">source</a></td>
            </tr>
            """
            for row in evidence_map.rows
        )
    if not rows:
        rows = """
        <tr>
          <td colspan="6">No results yet.</td>
        </tr>
        """
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SHawn EvidenceMap Demo</title>
  <style>
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f8fafc;
      color: #17202a;
    }}
    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 56px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(2rem, 6vw, 4rem);
      letter-spacing: 0;
      line-height: 1;
    }}
    p {{
      color: #5d6978;
      max-width: 760px;
    }}
    form {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 180px 120px;
      gap: 10px;
      margin: 28px 0;
    }}
    input, select, button {{
      min-height: 44px;
      border: 1px solid #d9e0e8;
      border-radius: 8px;
      padding: 0 12px;
      font: inherit;
      background: white;
    }}
    button {{
      border-color: #0f766e;
      background: #0f766e;
      color: white;
      font-weight: 700;
      cursor: pointer;
    }}
    .status {{
      margin-bottom: 12px;
      color: #0f766e;
      font-weight: 700;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid #d9e0e8;
      border-radius: 8px;
      background: white;
    }}
    table {{
      width: 100%;
      min-width: 980px;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid #d9e0e8;
      vertical-align: top;
      text-align: left;
      font-size: 0.92rem;
    }}
    th {{
      color: #5d6978;
      font-size: 0.78rem;
      text-transform: uppercase;
    }}
    @media (max-width: 760px) {{
      form {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
<main>
  <h1>SHawn EvidenceMap</h1>
  <p>Public-demo evidence mapping from public biomedical metadata. Outputs require manual verification before citation or manuscript use.</p>
  <form action="/demo" method="get">
    <input name="q" value="{escape(query)}" placeholder="endometrial organoid implantation" />
    <select name="mode">
      {option("recent", ranking_mode, "Recent")}
      {option("foundational", ranking_mode, "Foundational")}
      {option("balanced", ranking_mode, "Balanced")}
    </select>
    <button type="submit">Map</button>
  </form>
  <div class="status">{escape(status)}</div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Evidence</th>
          <th>Year</th>
          <th>Paper</th>
          <th>Rationale</th>
          <th>Support sentence</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>
</main>
</body>
</html>"""


def option(value: str, selected: str, label: str) -> str:
    attr = " selected" if value == selected else ""
    return f'<option value="{value}"{attr}>{label}</option>'


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), DemoHandler)
    print(f"SHawn EvidenceMap demo: http://{HOST}:{PORT}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
