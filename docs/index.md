# CytoDxRx

CytoDxRx diagnoses and corrects technical artifacts in plate-based image-based profiles.

**Pre-alpha.** CytoDxRx is under construction. The package does not do anything yet
beyond reporting its version. These pages describe where it is going.

## The problem

Wells on a plate are shifted by where they sit and by how many cells grew in them,
independent of what is in the well. Row and column gradients, differences between
control columns, alternating-row patterns and cell-density effects are examples.
Which of these are present, and which can be told apart from biology at all,
depends on the experiment and its plate design.

## The workflow

CytoDxRx is built around a human-in-the-loop workflow:

1. **inspect**: read the platemaps and report which artifacts the design can
   separate from biology, and under which assumptions.
1. **discover**: test for each artifact on the well-level profiles, fit corrections
   for the ones found, and write a plan file and a report.
1. **review**: a person reads the report and approves the plan.
1. **apply**: apply the approved corrections to well-level or single-cell profiles.

Detection and fitting use well-level profiles only. Corrections are constants per
well and feature, so the same numbers apply to every cell in a well.

## What it expects

Per-plate well-level profiles (un-normalized, after cell quality control), the
platemaps, and optionally a cell count per well and labels for validation.
Image analysis, cell quality control, aggregation and feature selection happen
elsewhere, for example with [pycytominer](https://github.com/cytomining/pycytominer).

```{toctree}
:hidden:
:maxdepth: 2

development
reference
```
