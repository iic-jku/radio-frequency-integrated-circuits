#!/usr/bin/env python3
# -------------------------------------------------
# Unit tests for slides/_tools/gen_decks.py
# -------------------------------------------------
# SPDX-FileCopyrightText: 2026 Harald Pretl
# Johannes Kepler University, Institute for Integrated Circuits
# SPDX-License-Identifier: Apache-2.0
#
# Run: python3 -m unittest slides/_tools/test_gen_decks.py

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_decks  # noqa: E402

BOOK = """\
---
title: Test
---

{{< include /content/_abbrv.qmd >}}
{{< include /content/intro/_sec_intro.qmd >}}
{{< include /content/lna/_sec_lna.qmd >}}
{{< include /content/exam/_sec_exam_questions.qmd >}}
"""

INTRO = """\
::: {.content-hidden}
# Not a heading {#sec-licence}
:::

# Introduction {#sec-intro}

Text with inline math $x$ only.

## Basics {#sec-intro-basics}

$$
a = b
$$ {#eq-first}

{{< include /content/intro/_fig_one.qmd >}}

::: {#nte-example .callout-note}
## Example Title
$$
c = d
$$ {#eq-in-callout}
:::

| a | b |
|---|---|
| 1 | 2 |
: Caption {#tbl-one}

::: {.content-visible when-format="revealjs"}
## Slide Only {#sec-slide-only}
$$
e
$$ {#eq-slide-only}
:::

## Unnumbered {.unnumbered}

### Deeper {#sec-intro-deeper}
"""

FIG_ONE = """\
```{python}
#| label: fig-one
# a python comment, not a heading
print(1)
```
"""

LNA = """\
# Low Noise Amplifiers {#sec-lna}

See @sec-intro-basics.

{{< embed ./content/lna/nb.ipynb#fig-from-notebook >}}

$$
f
$$ {#eq-lna}
"""

EXAM = """\
# Appendix: Examination Questions {#sec-exam}
"""


def make_tree(root):
    files = {
        "rfic.qmd": BOOK,
        "content/_abbrv.qmd": "::: {.hidden}\n\\newcommand{\\x}{x}\n:::\n",
        "content/intro/_sec_intro.qmd": INTRO,
        "content/intro/_fig_one.qmd": FIG_ONE,
        "content/lna/_sec_lna.qmd": LNA,
        "content/exam/_sec_exam_questions.qmd": EXAM,
    }
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")


class NumberLabelsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)
        paths = gen_decks.book_includes(self.root)
        self.labels = gen_decks.number_labels(paths, self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def num(self, label):
        return self.labels[label]["number"]

    def test_sections_are_hierarchical(self):
        self.assertEqual(self.num("sec-intro"), "1")
        self.assertEqual(self.num("sec-intro-basics"), "1.1")
        self.assertEqual(self.num("sec-lna"), "2")

    def test_unnumbered_heading_does_not_count(self):
        # "## Unnumbered" is skipped, so ### Deeper is below 1.1
        self.assertEqual(self.num("sec-intro-deeper"), "1.1.1")

    def test_hidden_and_slide_only_content_is_ignored(self):
        self.assertNotIn("sec-licence", self.labels)
        self.assertNotIn("sec-slide-only", self.labels)
        self.assertNotIn("eq-slide-only", self.labels)

    def test_callout_heading_is_not_a_section(self):
        self.assertNotIn("sec-example-title", self.labels)

    def test_flat_counters_across_chapters(self):
        self.assertEqual(self.num("eq-first"), "1")
        self.assertEqual(self.num("eq-in-callout"), "2")
        self.assertEqual(self.num("eq-lna"), "3")
        self.assertEqual(self.num("fig-one"), "1")
        self.assertEqual(self.num("fig-from-notebook"), "2")
        self.assertEqual(self.num("tbl-one"), "1")
        self.assertEqual(self.num("nte-example"), "1")

    def test_chapter_of_label(self):
        self.assertEqual(self.labels["fig-one"]["chapter"], 1)
        self.assertEqual(self.labels["eq-lna"]["chapter"], 2)

    def test_code_comment_is_not_a_heading(self):
        self.assertEqual(self.num("sec-lna"), "2")


class RenderFilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)
        self.files = gen_decks.render_files(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_deck_per_chapter_without_exam(self):
        decks = sorted(f for f in self.files
                       if f.startswith("slides/") and f.count("/") == 1
                       and f != "slides/index.qmd")
        self.assertEqual(decks, ["slides/intro.qmd", "slides/lna.qmd"])

    def test_deck_front_matter(self):
        deck = self.files["slides/lna.qmd"]
        self.assertIn('title: "Low Noise Amplifiers"', deck)
        self.assertIn("rfic-chapter: 2", deck)
        self.assertIn("number-offset: [1]", deck)
        self.assertIn("{{< include /content/lna/_sec_lna.qmd >}}", deck)
        self.assertIn("(../rfic.html#sec-lna)", deck)
        self.assertIn("path: _tools/structure.lua", deck)
        self.assertIn("bibliography: ../references.bib", deck)

    def test_overview_lists_decks(self):
        index = self.files["slides/index.qmd"]
        self.assertIn("2. [Low Noise Amplifiers](lna.html)", index)
        self.assertIn("(../rfic.html)", index)

    def test_numbers_map_links_from_slides_dir(self):
        self.assertIn('"book": "../rfic.html"',
                      self.files["slides/_tools/numbers.json"])

    def test_check_mode_detects_stale_files(self):
        gen_decks.ROOT = self.root
        try:
            self.assertEqual(gen_decks.main([]), 0)
            self.assertEqual(gen_decks.main(["--check"]), 0)
            (self.root / "slides" / "lna.qmd").write_text("edited")
            self.assertEqual(gen_decks.main(["--check"]), 1)
        finally:
            gen_decks.ROOT = Path(gen_decks.__file__).resolve().parents[2]


if __name__ == "__main__":
    unittest.main()
