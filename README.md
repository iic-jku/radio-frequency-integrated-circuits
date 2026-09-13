# Radio-Frequency Integrated Circuits

[![Quarto Publish](https://github.com/iic-jku/radio-frequency-integrated-circuits/actions/workflows/quarto-publish.yml/badge.svg?branch=main)](https://github.com/iic-jku/radio-frequency-integrated-circuits/actions/workflows/quarto-publish.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17563943.svg)](https://doi.org/10.5281/zenodo.17563943)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-online-brightgreen)](https://iic-jku.github.io/radio-frequency-integrated-circuits/rfic.html)

**(c) 2025-2026 Harald Pretl and co-authors, Department for Integrated Circuits (ICD), Johannes Kepler University, Linz (JKU)**

This is the material for a graduate-level radio-frequency integrated circuit course, held at JKU under course number 336.023 ("VO Integrierte Hochfrequenz-Schaltungstechnik"). Follow this [link to access the material](https://iic-jku.github.io/radio-frequency-integrated-circuits/rfic.html).

All course material is made publicly available and shared under the Apache-2.0 license.

**We happily accept [pull requests](https://github.com/iic-jku/radio-frequency-integrated-circuits/pulls) to fix typos or add content! If you want to discuss something that is not clear, please [open an issue](https://github.com/iic-jku/radio-frequency-integrated-circuits/issues/new)!**

## Lecture Slides

One reveal.js deck per chapter is generated from the lecture notes (`slides_<topic>.qmd`, listed on `slides.qmd`). Figures, display equations, callouts, lists and tables go on slides; prose becomes speaker notes (press `S`). Figure, equation, table and section numbers match the notes.

After adding, removing or renaming a chapter, or adding/removing labels (`#fig-`, `#eq-`, `#tbl-`, `#nte-`, `#sec-`), regenerate and check:

```bash
python3 _slides/gen_decks.py
python3 -m unittest _slides/test_gen_decks.py
```

Optional markup in the chapter files to improve slides (ignored by the HTML and PDF notes):

- `::: {.content-visible when-format="revealjs"}` — slide-only content (e.g. key bullet points); a leading `###` heading becomes the slide title.
- `::: {.content-hidden when-format="revealjs"}` — keep content in the notes only.
- `{.no-slide}` on a div (callout, figure cell) or in an equation label (`{#eq-foo .no-slide}`) — skip it on slides.

The render log lists `SLIDES: crowded slide …` warnings for slides that are good candidates for slide-only bullets.
