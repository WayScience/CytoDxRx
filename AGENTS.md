# AGENTS.md

Guidance for coding agents working in this repository.

## What this is

CytoDxRx diagnoses and corrects technical artifacts (position effects, cell-density or
confluence effects) in plate-based image-based profiles. It takes per-plate well-level
profiles and platemaps, decides which artifacts are present and separable from biology,
fits corrections, writes a plan for a person to approve, and applies the approved
corrections. It is intended for the cytomining community and follows pycytominer
conventions.

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
- No new dependency without discussion.
- No data in the repository beyond small test fixtures. Never commit large files.

## Working rules

- Keep changes small and focused; one pull request does one thing.
- Make all technical documentation brief, simple, and true.
- Every change has tests, and documentation if it changes behavior.
- Tests prefer real over mocked data.
- Ask before changing the scope, the input contract or a public interface.
- All production code must include accurate type hints and docstrings with complete descriptions of parameters and return values.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and checks, and the glossary in `docs/glossary.md` for the terms used here.
