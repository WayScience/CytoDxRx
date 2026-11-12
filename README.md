# CytoDxRx

Diagnose and correct technical artifacts in image-based profiles.

## Why

In plate-based image-based profiling, a well's profile reflects where the well sits on the plate and how many cells grew in it, as well as what is in it.
Row and column gradients, differences between control columns, alternating-row patterns and cell-density effects are examples.
Left uncorrected, these effects can be mistaken for biology.
They can also inflate replicate agreement when replicates share a well position.
Which artifacts are present in an experiment, and which can be separated from biology at all, depends on the plate design.

## What correction gives you

Profiles whose differences reflect what was applied to the wells rather than where the wells were.
A report that says what was found, what was corrected and what could not be separated from biology.

## What it will do

CytoDxRx follows a human-in-the-loop workflow:

1. **inspect**: read the platemaps and report which artifacts the design can separate from biology, and under which assumptions.
1. **discover**: test for each artifact on the well-level profiles, fit corrections for the ones found, and write a plan file and a report.
1. **review**: a person reads the report and approves the plan.
1. **apply**: apply the approved corrections to well-level or single-cell profiles.

Detection and fitting use well-level profiles.
Corrections are constants per well and feature, so the same numbers apply to every cell in a well.
The package currently reports only its version.

## What it expects

Per-plate well-level profiles (un-normalized, after cell quality control), the platemaps, and optionally a cell count per well and labels for validation.

## What it is not

CytoDxRx starts after image analysis, cell quality control and aggregation.
It does not segment cells, extract features, aggregate cells to wells or select features.
Use tools such as [CytoTable](https://github.com/cytomining/CytoTable), [coSMicQC](https://github.com/cytomining/coSMicQC) and [pycytominer](https://github.com/cytomining/pycytominer) for those.

## Install

CytoDxRx is not yet released.
To work on it from a source checkout:

```bash
git clone https://github.com/WayScience/CytoDxRx
cd CytoDxRx
uv sync
```

## Contributing

Please see [CONTRIBUTING.md](https://github.com/WayScience/CytoDxRx/blob/main/CONTRIBUTING.md).

## License

BSD 3-Clause.
See [LICENSE](https://github.com/WayScience/CytoDxRx/blob/main/LICENSE).
