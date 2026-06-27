#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

hard_fail='(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|OPENAI_API_KEY=|ANTHROPIC_API_KEY=|BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY|/Users/shawn|/home/mdge|CloudStorage|corpus\.db|GlocalLab|ec_aso|disease_atlas|cycle_analysis)'
review_terms='(OneDrive|Obsidian|Zotero|NRF|unpublished)'

if rg -n --hidden -S "$hard_fail" "$repo_root" \
  -g '!*.egg-info/**' \
  -g '!__pycache__/**' \
  -g '!scripts/public_safety_scan.sh' \
  -g '!.git/**'; then
  echo "Public safety scan found hard-fail matches." >&2
  exit 1
fi

if rg -n --hidden -S "$review_terms" "$repo_root" \
  -g '!*.egg-info/**' \
  -g '!__pycache__/**' \
  -g '!scripts/public_safety_scan.sh' \
  -g '!.git/**'; then
  echo "Public safety scan found review terms above; review manually before public release." >&2
fi

echo "Public safety scan passed."
