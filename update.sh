#!/usr/bin/env bash
# Re-runnable conversion of the Diataxis documentation framework
# (https://github.com/evildmp/diataxis-documentation-framework, CC BY-SA 4.0)
# from reStructuredText to GitHub-flavored Markdown, into reference/.
#
# Safe to re-run any time upstream changes: it shallow-clones a fresh copy,
# converts every page, and overwrites reference/*.md in place.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pandoc_bin="$(command -v pandoc || true)"
repo_url="https://github.com/evildmp/diataxis-documentation-framework"
out_dir="$here/reference"

if [[ -z "$pandoc_bin" ]]; then
  echo "error: pandoc not found on PATH" >&2
  exit 1
fi

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

clone_dir="$work_dir/repo"

echo "Cloning $repo_url (shallow, read-only) ..."
git clone --quiet --depth 1 "$repo_url" "$clone_dir"
commit_sha="$(git -C "$clone_dir" rev-parse HEAD)"
convert_date="$(date +%Y-%m-%d)"

echo "Cloned at commit $commit_sha"
echo

mkdir -p "$out_dir"

echo "Converting pages with pandoc + convert.py ..."
python3 "$here/convert.py" \
  --source "$clone_dir/source" \
  --out "$out_dir" \
  --pandoc "$pandoc_bin" \
  --commit "$commit_sha" \
  --date "$convert_date"

echo
page_count="$(find "$out_dir" -maxdepth 1 -name '*.md' ! -name 'SOURCES.md' | wc -l | tr -d ' ')"
echo "Wrote $page_count reference pages + SOURCES.md to $out_dir"
ls -la "$out_dir"
