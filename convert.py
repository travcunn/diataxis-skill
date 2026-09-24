#!/usr/bin/env python3
"""
Convert the Diataxis documentation framework's reStructuredText sources
(https://github.com/evildmp/diataxis-documentation-framework) into clean
GitHub-flavored Markdown reference pages.

Invoked by update.sh. Uses only the Python standard library; pandoc is
invoked as a subprocess for the rst -> gfm conversion itself.

Approach
--------
Sphinx/docutils has directives and roles that pandoc's rst reader either
does not understand (toctree, meta, sidebar, grid, grid-item, rst-class,
cssclass) or renders in a way that loses information once flattened to
plain gfm text (:doc:/:ref:/:term: roles, which pandoc renders as bare
code-spans with the role stripped). Rather than patch pandoc's output
after the fact for every case, most of the real work happens in a
PRE-PROCESSING pass over the raw .rst text:

  * :doc:/:ref:/:term: roles and toctree entries are resolved to their
    final Markdown link (or plain text, for anchors with no page of
    their own) *before* pandoc ever sees them, using an opaque sentinel
    token so pandoc cannot mangle bracket/paren characters. The
    sentinel is swapped back for real Markdown after pandoc runs.
  * .. image:: / .. figure:: directives are replaced with a plain
    italic "Figure: <file>" note (plus any caption text, preserved
    verbatim) before pandoc sees them.
  * .. rubric:: text is flattened to an ordinary paragraph, because
    pandoc's rst reader wraps rubric content in its own bold span,
    which collides with **bold** markup already inside the text.
  * .. meta:: blocks are dropped outright.

Everything pandoc DOES understand natively (list-table, epigraph,
external hyperlinks, emphasis, literals) is left alone and only
lightly cleaned up afterwards.

Directives pandoc does not recognise at all (sidebar, admonition/note,
grid, grid-item, rst-class, cssclass) still get parsed correctly by
pandoc's generic "unknown directive" fallback -- it turns each into a
<div class="NAME"> wrapping fully-converted Markdown content. The
POST-PROCESSING pass turns those divs into GitHub blockquotes (sidebar
and any real admonitions) or simply unwraps them (grid/grid-item/
rst-class/cssclass), discarding only the wrapper, never the content.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Cross-reference resolution table.
#
# Diataxis's :doc:/:ref: targets and toctree entries all resolve to one of:
#   - another converted page (-> a Markdown link to its sibling .md file)
#   - an anchor inside a page, with no page of its own (-> plain text)
#   - a page this corpus deliberately excludes (news, translation) (-> plain text)
#
# PAGES holds every converted page's docname -> H1 title (used as link text
# when a role/toctree entry gives no explicit text of its own, mirroring how
# Sphinx falls back to the target's title).
# ---------------------------------------------------------------------------

PAGES: dict[str, str] = {
    "index": "Diátaxis",
    "start-here": "Start here - Diátaxis in five minutes",
    "application": "Applying Diátaxis",
    "tutorials": "Tutorials",
    "how-to-guides": "How-to guides",
    "reference": "Reference",
    "explanation": "Explanation",
    "compass": "The compass",
    "how-to-use-diataxis": "Diátaxis as a guide to work",
    "theory": "Understanding Diátaxis",
    "foundations": "Foundations",
    "map": "The map",
    "quality": "Towards a theory of quality in documentation",
    "tutorials-how-to": "The difference between a tutorial and how-to guide",
    "reference-explanation": "The difference between reference and explanation",
    "colophon": "Colophon",
}

# :ref: labels that don't share their name with the docname they point to.
LABEL_ALIASES: dict[str, str] = {
    "how-to": "how-to-guides",
    "diataxis": "index",
}

# Labels that mark an anchor partway down a page, not the page itself --
# there is no sensible Markdown file to link to, so these become plain text.
ANCHOR_ONLY: set[str] = {"respect-structure", "deep-quality", "contact"}

# Docnames that exist upstream but are deliberately excluded from this corpus.
EXCLUDED_PAGES: set[str] = {"translation", "news", "self"}

LIVE_URL_BASE = "https://diataxis.fr"

SKIP_DOCNAMES = {"news", "translation"}


def live_url(docname: str) -> str:
    if docname == "index":
        return f"{LIVE_URL_BASE}/"
    return f"{LIVE_URL_BASE}/{docname}/"


# ---------------------------------------------------------------------------
# Pre-processing: operate on the raw .rst text, before pandoc ever sees it.
# ---------------------------------------------------------------------------


class RoleResolver:
    """Resolves :doc:/:ref:/:term: role bodies and toctree entries to a
    final Markdown snippet, handing back an opaque sentinel token that
    survives the pandoc round-trip unmodified. Scoped to one source file."""

    def __init__(self) -> None:
        self._sentinels: dict[str, str] = {}
        self._counter = 0

    def resolve(self, entry: str) -> str:
        normalized = re.sub(r"\s+", " ", entry).strip()
        m = re.match(r"^(.*)\s<([^<>]+)>$", normalized)
        if m:
            custom_text: str | None = m.group(1).strip()
            target = m.group(2).strip()
        else:
            custom_text = None
            target = normalized

        key = LABEL_ALIASES.get(target, target)

        if key in PAGES:
            text = custom_text or PAGES[key]
            result = f"[{text}]({key}.md)"
        elif key in ANCHOR_ONLY or key in EXCLUDED_PAGES:
            result = custom_text or key
        else:
            raise ValueError(
                f"Unresolved cross-reference target {target!r} (from {entry!r}). "
                "Add it to PAGES, LABEL_ALIASES, ANCHOR_ONLY or EXCLUDED_PAGES."
            )

        self._counter += 1
        token = f"XDLROLETOKEN{self._counter:04d}X"
        self._sentinels[token] = result
        return token

    def apply(self, text: str) -> str:
        """Replace every sentinel token with its resolved Markdown text."""
        for token, result in self._sentinels.items():
            text = text.replace(token, result)
        return text


def substitute_inline_roles(text: str, resolver: RoleResolver) -> str:
    def repl(m: re.Match) -> str:
        return resolver.resolve(m.group(1))

    return re.sub(r":(?:doc|ref|term):`([^`]+)`", repl, text)


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _block_extent(lines: list[str], start: int, base_indent: int) -> int:
    """Index of the first line after the indented block (options + body)
    that follows a directive line at `start` with indentation `base_indent`."""
    i = start + 1
    n = len(lines)
    while i < n:
        if lines[i].strip() == "":
            j = i
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n and _indent_of(lines[j]) > base_indent:
                i = j
                continue
            return i
        if _indent_of(lines[i]) > base_indent:
            i += 1
            continue
        return i
    return i


def _dedent_block(block_lines: list[str]) -> list[str]:
    indents = [_indent_of(l) for l in block_lines if l.strip() != ""]
    if not indents:
        return []
    m = min(indents)
    return [l[m:] if l.strip() != "" else "" for l in block_lines]


def _strip_meta(lines: list[str], i: int, base_indent: int) -> tuple[list[str], int]:
    end = _block_extent(lines, i, base_indent)
    return [], end


def _process_toctree(
    lines: list[str], i: int, base_indent: int, resolver: RoleResolver
) -> tuple[list[str], int]:
    end = _block_extent(lines, i, base_indent)
    block = lines[i + 1 : end]

    hidden = any(re.match(r"^\s*:hidden:\s*$", l) for l in block)

    idx = 0
    while idx < len(block) and block[idx].strip().startswith(":"):
        idx += 1
    while idx < len(block) and block[idx].strip() == "":
        idx += 1
    entries = [l.strip() for l in block[idx:] if l.strip() != ""]

    if hidden or not entries:
        return [], end

    indent_str = " " * base_indent
    out = [f"{indent_str}- {resolver.resolve(entry)}" for entry in entries]
    out.append("")
    return out, end


def _process_rubric(lines: list[str], i: int, base_indent: int) -> tuple[list[str], int]:
    header = lines[i]
    m = re.match(r"^ *\.\.\s+rubric::\s*(.*)$", header)
    assert m is not None
    parts = [m.group(1).rstrip()]
    j = i + 1
    while j < len(lines):
        line = lines[j]
        if line.strip() == "" or _indent_of(line) <= base_indent:
            break
        parts.append(line.strip())
        j += 1
    text = " ".join(p for p in parts if p)
    return [f"{' ' * base_indent}{text}"], j


def _process_image_or_figure(
    lines: list[str], i: int, base_indent: int
) -> tuple[list[str], int]:
    end = _block_extent(lines, i, base_indent)
    header = lines[i]
    m = re.match(r"^ *\.\.\s+(?:image|figure)::\s*(\S+)\s*$", header)
    assert m is not None
    basename = m.group(1).rsplit("/", 1)[-1]

    block = lines[i + 1 : end]
    idx = 0
    while idx < len(block) and block[idx].strip().startswith(":"):
        idx += 1
    while idx < len(block) and block[idx].strip() == "":
        idx += 1
    caption = _dedent_block(block[idx:])

    indent_str = " " * base_indent
    out = [f"{indent_str}*Figure: {basename}*", ""]
    if any(l.strip() for l in caption):
        out.extend(f"{indent_str}{l}" if l.strip() else "" for l in caption)
        out.append("")
    return out, end


def _strip_grid_argument(lines: list[str], i: int, base_indent: int) -> tuple[list[str], int]:
    """`.. grid:: 1 2 2 2` (sphinx-design column-count spec) carries a
    directive argument that is pure layout config, never real content.
    Pandoc has no idea what "grid" means, so it falls back to treating that
    argument as the div's first paragraph -- drop it, keep the directive
    line (with its options and body) exactly as pandoc would otherwise see
    it, so grid-item content still comes through untouched."""
    return [f"{' ' * base_indent}..  grid::"], i + 1


DIRECTIVE_RE = re.compile(r"^( *)\.\.\s+([a-zA-Z_-]+)::")


def preprocess_rst(text: str, resolver: RoleResolver) -> str:
    text = substitute_inline_roles(text, resolver)

    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        m = DIRECTIVE_RE.match(lines[i])
        if m:
            base_indent = len(m.group(1))
            name = m.group(2)
            if name == "meta":
                repl, end = _strip_meta(lines, i, base_indent)
                out.extend(repl)
                i = end
                continue
            if name == "toctree":
                repl, end = _process_toctree(lines, i, base_indent, resolver)
                out.extend(repl)
                i = end
                continue
            if name == "rubric":
                repl, end = _process_rubric(lines, i, base_indent)
                out.extend(repl)
                i = end
                continue
            if name in ("image", "figure"):
                repl, end = _process_image_or_figure(lines, i, base_indent)
                out.extend(repl)
                i = end
                continue
            if name == "grid":
                repl, end = _strip_grid_argument(lines, i, base_indent)
                out.extend(repl)
                i = end
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Post-processing: clean up pandoc's gfm output.
# ---------------------------------------------------------------------------

DROP_DIV_CLASSES = {"meta", "toctree", "rst-class", "cssclass"}
BLOCKQUOTE_DIV_CLASSES = {
    "sidebar",
    "note",
    "admonition",
    "warning",
    "tip",
    "attention",
    "caution",
    "danger",
    "error",
    "hint",
    "important",
}
ALERT_MAP = {
    "note": "NOTE",
    "warning": "WARNING",
    "tip": "TIP",
    "important": "IMPORTANT",
    "caution": "CAUTION",
}

DIV_OPEN_RE = re.compile(r'^<div class="([^"]*)"[^>]*>$')


def _render_div(cls: str, content: list[str]) -> list[str]:
    lines = content[:]
    if lines and lines[0].strip() == "":
        lines = lines[1:]
    if lines and lines[-1].strip() == "":
        lines = lines[:-1]

    if cls in DROP_DIV_CLASSES:
        return []

    if cls in BLOCKQUOTE_DIV_CLASSES:
        out = []
        alert = ALERT_MAP.get(cls)
        if alert:
            out.append(f"> [!{alert}]")
        for l in lines:
            out.append(f"> {l}" if l.strip() else ">")
        out.append("")
        return out

    # Unknown or purely structural (grid, grid-item, ...): unwrap, keep content.
    return lines + [""]


def transform_divs(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    stack: list[dict] = []
    for line in lines:
        m_open = DIV_OPEN_RE.match(line.strip())
        is_close = line.strip() == "</div>"
        if m_open:
            stack.append({"class": m_open.group(1), "content": []})
            continue
        if is_close and stack:
            frame = stack.pop()
            rendered = _render_div(frame["class"], frame["content"])
            target = stack[-1]["content"] if stack else out
            target.extend(rendered)
            continue
        (stack[-1]["content"] if stack else out).append(line)
    return "\n".join(out)


def cleanup_artifacts(text: str) -> str:
    # Header id attributes docutils attaches from `.. _label:` targets, e.g.
    # "## Some heading {#some-label}".
    text = re.sub(r"[ \t]*\{#[^}\n]+\}", "", text)
    # Any interpreted-text / title-ref span attributes pandoc might emit.
    text = re.sub(r"\{\.interpreted-text[^}]*\}", "", text)
    text = re.sub(r"\{\.title-ref\}", "", text)
    # Leftover substitution references, e.g. |something|.
    text = re.sub(r"\|([A-Za-z][\w-]*)\|", r"\1", text)
    # Collapse runs of 3+ blank lines left behind by dropped blocks.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


H1_RE = re.compile(r"^#\s", re.MULTILINE)


def add_provenance_header(text: str, docname: str, commit: str, date: str) -> str:
    stripped = text.lstrip("\n")
    m = H1_RE.match(stripped)
    if not m:
        print(f"WARNING: {docname}.md has no H1 as its first line", file=sys.stderr)
    header = (
        f"<!--\n"
        f"Source: {live_url(docname)}\n"
        f"Upstream commit: {commit}\n"
        f"Converted: {date}\n"
        f"-->\n\n"
    )
    return header + stripped.rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def convert_page(rst_path: Path, pandoc: str, commit: str, date: str) -> tuple[str, str]:
    docname = rst_path.stem
    resolver = RoleResolver()
    raw = rst_path.read_text(encoding="utf-8")
    pre = preprocess_rst(raw, resolver)

    proc = subprocess.run(
        [pandoc, "-f", "rst", "-t", "gfm", "--wrap=none"],
        input=pre,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"pandoc failed on {rst_path.name}:\n{proc.stderr}")

    md = proc.stdout
    md = resolver.apply(md)
    md = transform_divs(md)
    md = cleanup_artifacts(md)
    md = add_provenance_header(md, docname, commit, date)

    title_match = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else docname
    return md, title


def write_sources_md(out_dir: Path, pages: list[tuple[str, str]]) -> None:
    lines = [
        "# Sources",
        "",
        "Converted from the Diataxis documentation framework "
        "(https://github.com/evildmp/diataxis-documentation-framework).",
        "",
        "| File | Page title | Live URL |",
        "| --- | --- | --- |",
    ]
    for docname, title in pages:
        filename = f"{docname}.md"
        lines.append(f"| {filename} | {title} | {live_url(docname)} |")
    lines += [
        "",
        "Content by Daniele Procida, licensed under CC BY-SA 4.0.",
        "Source repository: https://github.com/evildmp/diataxis-documentation-framework",
        "",
    ]
    (out_dir / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pandoc", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--date", required=True)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    rst_files = sorted(
        p
        for p in args.source.glob("*.rst")
        if p.stem not in SKIP_DOCNAMES
    )

    written: list[tuple[str, str]] = []
    for rst_path in rst_files:
        docname = rst_path.stem
        if docname not in PAGES:
            raise RuntimeError(
                f"{rst_path.name} is not registered in PAGES; add it before converting."
            )
        md, title = convert_page(rst_path, args.pandoc, args.commit, args.date)
        out_path = args.out / f"{docname}.md"
        out_path.write_text(md, encoding="utf-8")
        written.append((docname, title))
        print(f"  {out_path.name:32s} <- {rst_path.name}")

    write_sources_md(args.out, sorted(written))
    print(f"  {'SOURCES.md':32s} <- (generated)")


if __name__ == "__main__":
    main()
