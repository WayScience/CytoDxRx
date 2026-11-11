# CLAUDE.md

Guidance for Claude Code (and other coding agents) working in this repository.

## What this is

CytoDxRx diagnoses and corrects technical artifacts (position effects, cell-density or
confluence effects) in plate-based image-based profiles. It takes per-plate well-level
profiles and platemaps, decides which artifacts are present and separable from biology,
fits corrections, writes a plan for a person to approve, and applies the approved
corrections. It is intended for the cytomining community and follows pycytominer
conventions. It is pre-alpha; see `docs/index.md` for the intended workflow.

## Commands

```bash
uv sync                                              # environment (dev group)
uv run pytest                                        # tests
uv run pre-commit run --all-files                    # lint, format, spelling, markdown, yaml
uv run --group docs sphinx-build -W -b html docs docs/_build/html   # docs, warnings are errors
```

## Layout

- `cytodxrx/`: the package (flat layout). One module per concept, with numpy-style docstrings.
- `tests/`: `tests/test_<module>.py` covers `cytodxrx/<module>.py`.
- `docs/`: Sphinx with MyST markdown. The API reference is generated from docstrings,
  one page per module, so a new module needs no docs edit.

## Conventions

- Tables follow pycytominer: metadata columns start with `Metadata_` (`Metadata_Plate`,
  `Metadata_Well`), features keep their CellProfiler names, files are parquet.
- Functions take and return DataFrames or arrays. Fitted corrections are objects with
  `fit` and `transform`, and they serialize to tables keyed on plate and well.
- A correction must be expressible as a constant per well and feature (plus a scale
  per plate), so it applies identically to a well's median and to every cell in it.
- Estimability depends on the plate design. Report when an artifact cannot be separated
  from biology and which assumption an estimate relies on, instead of guessing.
- Numerical decisions are rule-based, calibrated and recorded. Do not put a language
  model in the decision path.
- Type hints on public functions. No new dependency without discussion.
- No data in the repository beyond small test fixtures. Never commit large files.

## Working rules

- Keep changes small and focused; one pull request does one thing.
- Every change has tests, and documentation if it changes behavior.
- Ask before changing the scope, the input contract or a public interface.

## Glossary

- **artifact**: a technical effect on well profiles that is not biology.
- **position effect**: an artifact that is a function of well position. **Tilt** is one
  type (a smooth additive row-plus-column map with a per-layout amplitude); others
  include control-column offsets, parity patterns and edge effects.
- **covariate effect**: an artifact driven by a measured covariate, such as cell count
  or confluence.
- **platemap**: the file that says what is in each well; a barcode-to-platemap table
  links plates to platemaps. A **layout** is a set of plates sharing the same arrangement.
- **identifiability grade**: whether an artifact can be separated from biology in a
  design: by design, under an assumption, or not at all.
- **plan file**: the proposed corrections with their evidence; a person approves entries
  before anything is applied.
