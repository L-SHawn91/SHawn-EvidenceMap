from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from .demo import build_public_metadata_demo, build_synthetic_demo, render_demo_page
from .store import ReferenceStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build, verify, and export SQLite reference demos."
    )
    parser.add_argument(
        "command",
        choices=("demo", "public-demo", "verify", "export", "page"),
    )
    parser.add_argument("--db", required=True, type=Path, help="SQLite database path")
    parser.add_argument("--out", type=Path, help="Output path for export or page")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in {"export", "page"} and args.out is None:
        parser.error("--out is required for export and page")
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
            assert args.out is not None
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(store.export_json(), encoding="utf-8")
            print(f"REFERENCE_DB_EXPORT_WRITTEN:{args.out}")
            return 0

        if args.command == "page":
            assert args.out is not None
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(render_demo_page(store.export_json()), encoding="utf-8")
            print(f"REFERENCE_DB_PAGE_WRITTEN:{args.out}")
            return 0

    return 0
