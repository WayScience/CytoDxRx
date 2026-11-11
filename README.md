# CytoDxRx

Diagnose and correct technical artifacts in image-based profiles.

> **Pre-alpha.** CytoDxRx is under construction and does not do anything yet beyond
> reporting its version. This page describes where it is going.

## Why

In plate-based image-based profiling, a well's profile depends on where it sits on
the plate and on how many cells grew in it, as well as on what is in it. Row and
column gradients, differences between control columns, alternating-row patterns and
cell-density effects are examples. Which of these are present in an experiment, and
which can be separated from biology at all, depends on the plate design.

## What it will do

CytoDxRx follows a human-in-the-loop workflow:

1. **inspect**: read the platemaps and report which artifacts the design can
   separate from biology, and under which assumptions.
1. **discover**: test for each artifact on the well-level profiles, fit corrections
   for the ones found, and write a plan file and a report.
1. **review**: a person reads the report and approves the plan.
1. **apply**: apply the approved corrections to well-level or single-cell profiles.

Detection and fitting use well-level profiles. Corrections are constants per well and
feature, so the same numbers apply to every cell in a well.

## What it is not

CytoDxRx starts after image analysis, cell quality control and aggregation. It does
not segment cells, extract features, aggregate cells to wells or select features; use
tools such as [CytoTable](https://github.com/cytomining/CytoTable),
[coSMicQC](https://github.com/cytomining/coSMicQC) and
[pycytominer](https://github.com/cytomining/pycytominer) for those.

## Install

CytoDxRx is not yet released. To work on it from a source checkout:

```bash
git clone https://github.com/WayScience/CytoDxRx
cd CytoDxRx
uv sync
```

## Documentation

See the [docs](docs/index.md) and the [development guide](docs/development.md).

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

BSD 3-Clause. See [LICENSE](LICENSE).
