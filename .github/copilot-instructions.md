# Copilot Instructions for RFIC Course Material

## Project Overview
This is a Quarto-based educational website and PDF document for a graduate-level Radio-Frequency Integrated Circuits (RFIC) course at Johannes Kepler University. The content covers RF circuit fundamentals, transceiver architectures, and specific circuit blocks (LNA, mixer, oscillator, PLL, power amplifiers).

## Architecture & Structure

### Content Organization
- **Main document**: `rfic.qmd` orchestrates all content via `{{< include >}}` directives
- **Content modules**: Each topic lives in `content/{topic}/` with:
  - `_sec_{topic}.qmd` - main section text with theory and equations
  - `_fig_{name}.qmd` - standalone figure files with embedded Python code
  - Naming convention: All content files start with `_` to prevent standalone rendering
- **Shared macros**: `content/_macros.qmd` defines LaTeX commands (e.g., `\VDD`, `\gm`, `\ID`) used throughout for consistent notation

### Multi-Format Output
- **HTML**: Primary web format with dark/light themes (cosmo/solar)
- **PDF**: Generated via typst format with A4 layout
- **Typst**: Alternative to LaTeX, configured in `_quarto.yml` format section
- All formats share same source; use format-specific YAML frontmatter when needed

## Development Workflows

### Local Preview
```bash
quarto preview           # Live preview with auto-reload
quarto render           # Build all formats (HTML + PDF)
quarto render rfic.qmd --to html   # Single format
```

### Python Dependencies
Install from `requirements.txt` before rendering:
- **schemdraw**: Circuit diagram generation (most figures in lna/, mixer/, etc.)
- **matplotlib/numpy**: Data visualization and signal processing plots
- **pygmid**: gm/ID methodology for transistor sizing
- **pysmithchart**: Smith chart generation for impedance matching

### Build System
- **GitHub Actions**: `.github/workflows/quarto-publish.yml` auto-publishes to gh-pages on push to main
- **APT dependency**: `librsvg2-bin` required for SVG processing in CI
- **Freeze mechanism**: Quarto caches Python execution in `_freeze/` to speed up rebuilds

## Code Patterns & Conventions

### Figure Generation Pattern
All `_fig_*.qmd` files follow this structure:
```python
#| label: fig-descriptive-name      # Must start with 'fig-'
#| echo: false                       # Hide code, show only figure
#| fig-cap: "Descriptive caption"   # Required for cross-references

import schemdraw as sd
import schemdraw.elements as elm

# Configure schemdraw for consistent output
sd.svgconfig.svg2 = False
with sd.Drawing(canvas='svg') as d:
    d.config(unit=2, fontsize=14)
    # Circuit drawing code...
```

### LaTeX Macro Usage
Always use custom macros from `_macros.qmd` for consistency:
- Voltages: `\VDD`, `\VSS`, `\VGS{}`, `\VDS{}` (uppercase for DC)
- Small-signal: `\vgs{}`, `\vds{}` (lowercase v)
- Parameters: `\gm{}`, `\gds{}`, `\gmid` (gm/ID), `\ID{}`
- Capacitances: `\CGS{}`, `\Cgs{}`, `\Cox{}` (uppercase C for totals, lowercase for per-unit)

### Copyright Headers
Every `.qmd` file includes Apache 2.0 license in hidden block:
```markdown
::: {.content-hidden}
Copyright (C) 2024-2025 Harald Pretl and co-authors
Licensed under the Apache License, Version 2.0
:::
```

## Key Technical Details

### Cross-References
- Sections: `{#sec-identifier}` → `@sec-identifier`
- Figures: `{#fig-identifier}` → `@fig-identifier`
- Equations: `{#eq-identifier}` → `@eq-identifier`
- Use kebab-case for all identifiers

### Bibliography
- BibTeX entries in `references.bib`
- Cite as `[@citation-key]` for parenthetical, `@citation-key` for textual

### Mathematical Notation
- Use `$$` for display math, `$` for inline
- RF conventions: frequency `f`, angular frequency `\omega`, impedance `Z`
- Power in dBm: `P_\mathrm{dBm}`, linear power: `P`

## Common Tasks

### Adding New Content Section
1. Create `content/{topic}/` directory
2. Add `_sec_{topic}.qmd` with `{#sec-topic}` ID
3. Add individual `_fig_*.qmd` files for complex figures
4. Include in `rfic.qmd`: `{{< include /content/{topic}/_sec_{topic}.qmd >}}`
5. Update table of contents in `_quarto.yml` if adding to navbar

### Creating Circuit Diagrams
- Use schemdraw's element library: `elm.AnalogNFet`, `elm.Resistor`, `elm.Capacitor`
- Position elements: `.up()`, `.down()`, `.right()`, `.left()`
- Anchoring: `.at(element.drain)`, `.anchor('gate')`
- Labels: `.label(r'$R_\mathrm{s}$')` with LaTeX math
- Reference existing figures in `content/lna/` for complex examples

### Testing Changes
1. Check syntax: `quarto check`
2. Preview locally before committing
3. Verify PDF generation: `quarto render rfic.qmd --to typst`
4. Check Python figures render correctly (look in `_freeze/` for cached outputs)

## Pitfalls to Avoid
- Don't name content files without leading `_` (will create unwanted standalone pages)
- Always set `echo: false` in figure chunks (showing code breaks layout)
- Use raw strings `r'...'` for LaTeX in Python to avoid escaping issues
- Include macros file first: `{{< include /content/_macros.qmd >}}` in any new document
- Remember schemdraw coordinates are relative; use `.at()` for absolute positioning
