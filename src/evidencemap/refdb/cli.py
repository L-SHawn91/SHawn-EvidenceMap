from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Sequence

from .demo import build_public_metadata_demo, build_synthetic_demo, render_demo_page
from .interchange import (
    InterchangeError,
    export_bibtex,
    export_csv,
    export_ris,
    parse_bibtex,
    parse_csv,
    parse_identifiers,
    parse_ris,
)
from .store import ReferenceStore


_INPUT_PARSERS = {
    "identifiers": parse_identifiers,
    "csv": parse_csv,
    "ris": parse_ris,
    "bibtex": parse_bibtex,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build, ingest, verify, and export verifiable metadata bridge databases."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    for command in ("demo", "public-demo", "verify"):
        child = commands.add_parser(command)
        child.add_argument("--db", required=True, type=Path, help="SQLite database path")

    export = commands.add_parser("export")
    export.add_argument("--db", required=True, type=Path, help="SQLite database path")
    export.add_argument("--out", required=True, type=Path, help="Output file path")
    export.add_argument(
        "--format",
        choices=("json", "csv", "ris", "bibtex"),
        default="json",
        help="Entity handoff format; JSON includes audit state",
    )

    page = commands.add_parser("page")
    page.add_argument("--db", required=True, type=Path, help="SQLite database path")
    page.add_argument("--out", required=True, type=Path, help="HTML output path")

    ingest = commands.add_parser("ingest")
    ingest.add_argument("--db", required=True, type=Path, help="SQLite database path")
    ingest.add_argument("--input", required=True, type=Path, help="UTF-8 input file")
    ingest.add_argument(
        "--format",
        required=True,
        choices=tuple(_INPUT_PARSERS),
        help="Conservative input parser",
    )
    ingest.add_argument(
        "--recorded-at",
        help="Audit timestamp; defaults to current UTC ISO-8601 time",
    )
    return parser


def _parse_ingest_input(args: argparse.Namespace):
    try:
        content = args.input.read_bytes()
        text = content.decode("utf-8-sig")
        records = _INPUT_PARSERS[args.format](text)
    except (OSError, UnicodeError, InterchangeError) as exc:
        print(f"REFERENCE_DB_INPUT_ERROR: {exc}", file=sys.stderr)
        return None
    digest = hashlib.sha256(content).hexdigest()
    run_id = f"{args.format}-sha256-{digest[:16]}"
    recorded_at = args.recorded_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return records, run_id, recorded_at


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    parsed_ingest = None
    if args.command == "ingest":
        parsed_ingest = _parse_ingest_input(args)
        if parsed_ingest is None:
            return 2

    if args.command in {"verify", "export", "page"} and not args.db.is_file():
        print(f"REFERENCE_DB_ERROR: database does not exist: {args.db}", file=sys.stderr)
        return 2

    with ReferenceStore(args.db) as store:
        if args.command == "demo":
            build_synthetic_demo(store)
            print("REFERENCE_DB_DEMO_OK")
            return 0

        if args.command == "public-demo":
            build_public_metadata_demo(store)
            print("PUBLIC_METADATA_DB_DEMO_OK")
            return 0

        if args.command == "ingest":
            assert parsed_ingest is not None
            records, run_id, recorded_at = parsed_ingest
            summary = store.ingest_records(
                records,
                run_id=run_id,
                source=f"user_{args.format}",
                started_at=recorded_at,
                finished_at=recorded_at,
            )
            marker = "REFERENCE_DB_INGEST_PARTIAL" if summary["rejected"] else "REFERENCE_DB_INGEST_OK"
            print(
                f"{marker} inserted={summary['inserted']} merged={summary['merged']} "
                f"rejected={summary['rejected']} run_id={run_id}"
            )
            return 3 if summary["rejected"] else 0

        if args.command == "verify":
            issues = store.verify()
            if issues:
                print("REFERENCE_DB_FAIL")
                for issue in issues:
                    print(issue)
                return 2
            print("REFERENCE_DB_OK")
            return 0

        if args.command == "export":
            payload = json.loads(store.export_json())
            entities = payload["entities"]
            try:
                rendered = {
                    "json": store.export_json,
                    "csv": lambda: export_csv(entities),
                    "ris": lambda: export_ris(entities),
                    "bibtex": lambda: export_bibtex(entities),
                }[args.format]()
            except InterchangeError as exc:
                print(f"REFERENCE_DB_EXPORT_ERROR: {exc}", file=sys.stderr)
                return 2
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(rendered, encoding="utf-8")
            print(f"REFERENCE_DB_EXPORT_WRITTEN:{args.out}")
            return 0

        if args.command == "page":
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(render_demo_page(store.export_json()), encoding="utf-8")
            print(f"REFERENCE_DB_PAGE_WRITTEN:{args.out}")
            return 0

    return 0
