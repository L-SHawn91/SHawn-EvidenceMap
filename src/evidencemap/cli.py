from __future__ import annotations

import argparse

from .cartridges import cartridge_ids
from .export import to_json, to_markdown
from .pipeline import build_evidence_map
from .report import to_customer_report
from .review import ReviewFileError, load_review_file
from .visual_report import to_visual_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a public-demo research evidence map.")
    parser.add_argument("query", help="Research question or topic")
    parser.add_argument(
        "--cartridge",
        choices=cartridge_ids(),
        default="generic",
        help="Domain cartridge to use (default: generic)",
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum ranked evidence rows to return")
    parser.add_argument(
        "--ranking-mode",
        choices=["balanced", "recent", "foundational"],
        default="recent",
        help="Ranking profile for public evidence maps",
    )
    parser.add_argument("--no-cache", action="store_true", help="Bypass the local public-demo query cache")
    parser.add_argument("--cache-ttl-hours", type=float, default=24, help="Local query cache TTL in hours")
    parser.add_argument("--claim", default="", help="Scientific proposition to review (separate from the search topic)")
    parser.add_argument("--reviews", help="Local JSON file containing explicit evidence-relation reviews")
    parser.add_argument("--draft-statement", action="store_true", help="Request a gated, deterministic statement draft")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="Print JSON (default output)")
    output_group.add_argument("--markdown", action="store_true", help="Print Markdown instead of JSON")
    output_group.add_argument("--report", action="store_true", help="Print fixed research report Markdown")
    output_group.add_argument("--html-report", action="store_true", help="Print fixed visual research report HTML")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        review_payload = load_review_file(args.reviews) if args.reviews else None
    except ReviewFileError as exc:
        parser.error(str(exc))

    try:
        evidence_map = build_evidence_map(
            args.query,
            limit=args.limit,
            ranking_mode=args.ranking_mode,
            cartridge_id=args.cartridge,
            use_cache=not args.no_cache,
            cache_ttl_hours=args.cache_ttl_hours,
            claim=args.claim,
            review_payload=review_payload,
            draft_statement=args.draft_statement,
        )
    except ReviewFileError as exc:
        parser.error(str(exc))
    if args.html_report:
        print(to_visual_html(evidence_map))
    elif args.report:
        print(to_customer_report(evidence_map))
    elif args.markdown:
        print(to_markdown(evidence_map))
    else:
        print(to_json(evidence_map))


if __name__ == "__main__":
    main()
