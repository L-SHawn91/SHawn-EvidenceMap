from __future__ import annotations

import argparse

from .cartridges import cartridge_ids
from .export import to_json, to_markdown
from .pipeline import build_evidence_map


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a public-demo research evidence map.")
    parser.add_argument("query", help="Research question or topic")
    parser.add_argument("--cartridge", choices=cartridge_ids(), default="bio", help="Domain cartridge to use")
    parser.add_argument("--limit", type=int, default=20, help="Maximum ranked evidence rows to return")
    parser.add_argument(
        "--ranking-mode",
        choices=["balanced", "recent", "foundational"],
        default="recent",
        help="Ranking profile for public evidence maps",
    )
    parser.add_argument("--no-cache", action="store_true", help="Bypass the local public-demo query cache")
    parser.add_argument("--cache-ttl-hours", type=float, default=24, help="Local query cache TTL in hours")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown instead of JSON")
    args = parser.parse_args()

    evidence_map = build_evidence_map(
        args.query,
        limit=args.limit,
        ranking_mode=args.ranking_mode,
        cartridge_id=args.cartridge,
        use_cache=not args.no_cache,
        cache_ttl_hours=args.cache_ttl_hours,
    )
    if args.markdown:
        print(to_markdown(evidence_map))
    else:
        print(to_json(evidence_map))


if __name__ == "__main__":
    main()
