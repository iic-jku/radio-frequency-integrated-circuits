#!/usr/bin/env python3
# -------------------------------------------------
# Generate one reveal.js deck per chapter of rfic.qmd
# -------------------------------------------------
# SPDX-FileCopyrightText: 2026 Harald Pretl
# Johannes Kepler University, Institute for Integrated Circuits
# SPDX-License-Identifier: Apache-2.0
#
# Writes (relative to the project root):
#   slides_<topic>.qmd       one deck per chapter
#   slides.qmd               overview page linking all decks
#   _slides/numbers.json     book numbering of every sec/fig/eq/tbl/nte label
#
# Usage:
#   python _slides/gen_decks.py           # (re)generate files
#   python _slides/gen_decks.py --check   # exit 1 if generated files are stale

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = "rfic.qmd"
EXCLUDE_TOPICS = {"exam"}  # chapters without a deck

RE_INCLUDE = re.compile(r"^\{\{<\s*include\s+/?(\S+?)\s*>\}\}\s*$")
RE_EMBED = re.compile(r"\{\{<\s*embed\s+\S+?#((?:fig|tbl)-[\w-]+)\s*>\}\}")
RE_SEC_FILE = re.compile(r"^content/(\w+)/_sec_\w+\.qmd$")
RE_FENCE = re.compile(r"^(`{3,}|~{3,})")
RE_DIV_OPEN = re.compile(r"^(:{3,})\s*\S")
RE_DIV_CLOSE = re.compile(r"^(:{3,})\s*$")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
RE_ATTR = re.compile(r"\{([^{}]*)\}\s*$")
RE_CELL_LABEL = re.compile(r"^#\|\s*label:\s*((?:fig|tbl)-[\w-]+)")
RE_LABEL_ATTR = re.compile(r"\{#((?:fig|eq|tbl|nte)-[\w-]+)")

PREFIX = {"sec": "Section", "fig": "Figure", "eq": "Equation",
          "tbl": "Table", "nte": "Note"}


def book_includes(root=ROOT):
    """Top-level include paths of rfic.qmd, in order (project-relative)."""
    paths = []
    for line in (root / BOOK).read_text(encoding="utf-8").splitlines():
        m = RE_INCLUDE.match(line.strip())
        if m:
            paths.append(m.group(1))
    return paths


def expand(path, root=ROOT):
    """Lines of a qmd file with nested includes expanded, in document order."""
    for line in (root / path).read_text(encoding="utf-8").splitlines():
        m = RE_INCLUDE.match(line.strip())
        if m:
            yield from expand(m.group(1), root)
        else:
            yield line


def _div_hidden_in_book(opener):
    """True if a div opener hides its content from the HTML book."""
    fmt = re.search(r'when-format="([^"]+)"', opener)
    if "content-hidden" in opener:
        return fmt is None or fmt.group(1) in ("html", "html5")
    if "content-visible" in opener:
        return fmt is not None and fmt.group(1) == "revealjs"
    return False


def number_labels(paths, root=ROOT):
    """Replicate Quarto's HTML numbering for the whole book.

    Returns {label: {"type", "number", "chapter"}} where chapter is the
    1-based index of the level-1 heading the label belongs to.
    """
    labels = {}
    counters = {"fig": 0, "eq": 0, "tbl": 0, "nte": 0}
    sec = [0] * 6
    chapter = 0
    fence = None      # opening fence string while inside a code block
    divs = []         # stack of (colons, is_callout, hidden)

    def add(label, kind):
        if kind == "sec":
            return
        counters[kind] += 1
        labels[label] = {"type": kind, "number": str(counters[kind]),
                         "chapter": chapter}

    for path in paths:
        for line in expand(path, root):
            hidden = any(d[2] for d in divs)
            if fence:
                if line.strip().startswith(fence):
                    fence = None
                elif not hidden:
                    m = RE_CELL_LABEL.match(line.strip())
                    if m:
                        add(m.group(1), m.group(1).split("-")[0])
                continue
            m = RE_FENCE.match(line.strip())
            if m:
                fence = m.group(1)
                continue
            m = RE_DIV_CLOSE.match(line)
            if m and divs:
                divs.pop()
                continue
            m = RE_DIV_OPEN.match(line)
            if m:
                divs.append((m.group(1), "callout" in line,
                             _div_hidden_in_book(line)))
                if not hidden and not _div_hidden_in_book(line):
                    lab = RE_LABEL_ATTR.search(line)
                    if lab:
                        add(lab.group(1), lab.group(1).split("-")[0])
                continue
            if hidden:
                continue
            h = RE_HEADING.match(line)
            if h and not any(d[1] for d in divs):
                attr = RE_ATTR.search(h.group(2))
                attrs = attr.group(1) if attr else ""
                if "unnumbered" in attrs or re.search(r"(^|\s)-(\s|$)", attrs):
                    continue
                level = len(h.group(1))
                sec[level - 1] += 1
                sec[level:] = [0] * (6 - level)
                if level == 1:
                    chapter = sec[0]
                ident = re.search(r"#(sec-[\w-]+)", attrs)
                if ident:
                    labels[ident.group(1)] = {
                        "type": "sec",
                        "number": ".".join(str(n) for n in sec[:level]),
                        "chapter": chapter}
                continue
            for lab in RE_LABEL_ATTR.findall(line):
                add(lab, lab.split("-")[0])
            for lab in RE_EMBED.findall(line):
                add(lab, lab.split("-")[0])
    return labels


def chapters(paths, root=ROOT):
    """Chapter records for all top-level includes that are _sec_ files."""
    out = []
    number = 0
    for path in paths:
        m = RE_SEC_FILE.match(path)
        if not m:
            continue
        number += 1
        title = None
        for line in expand(path, root):
            h = RE_HEADING.match(line)
            if h and len(h.group(1)) == 1:
                title = RE_ATTR.sub("", h.group(2)).strip()
                break
        out.append({"topic": m.group(1), "file": path, "number": number,
                    "title": title, "deck": f"slides_{m.group(1)}.qmd"})
    return out


DECK_TEMPLATE = """\
---
# Generated by _slides/gen_decks.py from {book} -- do not edit.
title: "{title}"
subtitle: "Radio-Frequency Integrated Circuits"
rfic-chapter: {number}
number-offset: [{offset}]
execute:
  freeze: false
format:
  revealjs:
    slide-level: 3
    number-sections: true
    slide-number: c/t
    scrollable: true
    chalkboard: true
    theme: [default, _slides/slides.scss]
    footer: "[RFIC lecture notes](rfic.html#{sec_id})"
    menu:
      numbers: true
filters:
  - at: pre-ast
    path: _slides/structure.lua
  - at: post-render
    path: _slides/numbers.lua
bibliography: references.bib
---

{{{{< include /content/_abbrv.qmd >}}}}
{{{{< include /{file} >}}}}

### References {{.unnumbered .smaller .scrollable}}

::: {{#refs}}
:::
"""

OVERVIEW_TEMPLATE = """\
---
# Generated by _slides/gen_decks.py from {book} -- do not edit.
title: "Lecture Slides"
---

Slide decks generated from the [lecture notes](rfic.html), one per chapter.
Press `S` for speaker notes, `C` for the chalkboard, and `?` for all shortcuts.

{items}
"""


def chapter_sec_id(ch, root=ROOT):
    for line in expand(ch["file"], root):
        h = RE_HEADING.match(line)
        if h and len(h.group(1)) == 1:
            m = re.search(r"#(sec-[\w-]+)", h.group(2))
            return m.group(1) if m else ""
    return ""


def render_files(root=ROOT):
    """Return {relative path: content} of every generated file."""
    paths = book_includes(root)
    chs = chapters(paths, root)
    files = {}
    for ch in chs:
        if ch["topic"] in EXCLUDE_TOPICS:
            continue
        files[ch["deck"]] = DECK_TEMPLATE.format(
            book=BOOK, title=ch["title"], number=ch["number"],
            offset=ch["number"] - 1, file=ch["file"],
            sec_id=chapter_sec_id(ch, root))
    items = "\n".join(
        f"{ch['number']}. [{ch['title']}]({ch['deck'].replace('.qmd', '.html')})"
        for ch in chs if ch["topic"] not in EXCLUDE_TOPICS)
    files["slides.qmd"] = OVERVIEW_TEMPLATE.format(book=BOOK, items=items)
    numbers = {"book": BOOK.replace(".qmd", ".html"), "prefix": PREFIX,
               "labels": number_labels(paths, root)}
    files["_slides/numbers.json"] = json.dumps(numbers, indent=1,
                                               sort_keys=True) + "\n"
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if generated files differ from disk")
    args = ap.parse_args(argv)
    stale = []
    for rel, content in render_files(ROOT).items():
        target = ROOT / rel
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == content:
            continue
        if args.check:
            stale.append(rel)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            print(f"wrote {rel}")
    if stale:
        print("stale generated files (run python _slides/gen_decks.py):",
              *stale, sep="\n  ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
