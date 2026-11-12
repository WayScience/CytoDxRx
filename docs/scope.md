# Scope

CytoDxRx diagnoses and corrects technical artifacts in plate-based image-based profiles.
This page says what is in and out of scope.
Decisions are marked **decided**; open ones are marked **proposed** and are meant to be argued with.

## What it does

1. **inspect** reads the platemaps and reports which artifacts the plate design can separate from biology, and under which assumptions.
1. **discover** tests for each artifact on the well-level profiles, fits corrections for the ones found, and writes a [plan file](plan-file.md) and a report.
1. **review** is a person: they read the report and approve entries of the plan.
1. **apply** applies the approved corrections to well-level or single-cell profiles.

## Boundaries

**decided**

- CytoDxRx starts after image analysis, cell quality control and aggregation.
  It does not segment cells, extract features, aggregate cells to wells or select features.
- It corrects profile-level artifacts only, not image-level ones such as illumination.
- A correction is a constant per well and feature, plus a scale per plate, in the original units of the profiles.
  The same constants apply to the median of a well's cells and to every cell in the well.
- The plate format is a parameter.
  96-well and 384-well designs are supported from the start.
- Decisions are rule-based, calibrated and recorded.
  No language model is in the decision path.
- It is a library first, with a thin command line on top.
- Estimability comes first: the plate design decides which artifacts can be separated from biology, so `inspect` runs before any fitting.

**proposed**

- Normalization, rank transforms and feature selection stay in the user's pipeline, for example [pycytominer](https://github.com/cytomining/pycytominer).
  CytoDxRx takes un-normalized profiles and returns corrected, un-normalized profiles.
  It scales each plate on its controls internally, only to put plates on common units while it estimates effects.
- pycytominer is not a dependency.
  CytoDxRx follows its conventions (`Metadata_` columns, tables in and out, parquet files).
- `apply` accepts a single-cell table keyed on plate and well.
  CytoDxRx does not aggregate cells.
- The repository lives under WayScience for now and may move to cytomining.

## Out of scope for now

- Batch correction across plates or experiments.
- Corrections that depend on the biology of a well, such as a treatment effect.
- Choosing the downstream analysis.
