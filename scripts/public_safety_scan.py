#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

HARD_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|cookie)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"/(home|Users)/[^\s]+/(SHawn|SHide|OneDrive|Clouds)/"),
    re.compile(r"(?i)(corpus\.db|private[_-]?corpus|raw[_-]?manuscript)"),
]
SKIP_PARTS = {'.git', '.venv', 'node_modules', '__pycache__', 'dist', 'build'}

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    findings: list[tuple[str, str]] = []
    for path in root.rglob('*'):
        if not path.is_file() or SKIP_PARTS.intersection(path.parts):
            continue
        if path.stat().st_size > 750_000:
            continue
        text = path.read_text(errors='ignore')
        for pat in HARD_PATTERNS:
            if pat.search(text):
                findings.append((str(path.relative_to(root)), pat.pattern))
    if findings:
        for file, pattern in findings:
            print(f"PUBLIC_SAFETY_FAIL\t{file}\t{pattern}")
        return 1
    print('PUBLIC_SAFETY_OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
