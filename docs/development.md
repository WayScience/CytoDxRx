# Development

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

- Tables follow [pycytominer](https://github.com/cytomining/pycytominer) conventions:
  metadata columns start with `Metadata_`, and features keep their CellProfiler names.
- Docstrings use the numpy style. The API reference is generated from them, one page
  per module, so a new module needs no docs edit.
- Every change comes with tests and, if it changes behavior, documentation.
- The numerical decisions are rule-based and recorded. Nothing in the package
  depends on a language model.

## Pull requests

Keep pull requests small and focused. The pull request template has a checklist
that includes tests and docs.
