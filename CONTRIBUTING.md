# Contributing

Thank you for your interest in CytoDxRx.

## Set up

CytoDxRx uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pre-commit install
```

## Check your work

```bash
# tests
uv run pytest

# linting, formatting and the other checks CI runs
uv run pre-commit run --all-files

# the documentation, with warnings as errors
uv run --group docs sphinx-build -W -b html docs docs/_build/html
```

## Conventions

- Keep pull requests small and focused; one pull request does one thing.
- Every change has tests, and documentation if it changes behavior.
- Tests prefer real over mocked data.
- Make all technical documentation brief, simple, and true.
- Production code has accurate type hints and numpy-style docstrings that describe every parameter and return value.
  The API reference is generated from the docstrings, one page per module, so a new module needs no docs edit.
- Tables follow [pycytominer](https://github.com/cytomining/pycytominer) conventions: metadata columns start with `Metadata_`, and features keep their CellProfiler names.
- The numerical decisions are rule-based and recorded.
  Nothing in the package depends on a language model.

## Pull requests

The pull request template has a checklist that includes tests and docs.
Run `uv run pre-commit run --all-files` before opening a pull request.

## Code of conduct

Be kind: see our [code of conduct](https://github.com/WayScience/CytoDxRx/blob/main/CODE_OF_CONDUCT.md).
