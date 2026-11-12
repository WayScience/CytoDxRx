# Artifacts

An **artifact** is a technical effect on well profiles that is not biology.
This page names the artifacts CytoDxRx is built around.
The names are decided; each artifact is added only when it has a detector, a fit and a validation.
Nothing is implemented yet.

## Position effects

A position effect is a function of where a well sits on the plate.

| Artifact              | What it is                                                                                                                          |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| tilt                  | a smooth additive map, a row part plus a column part, shared by the plates of an experiment, with its own amplitude for each layout |
| control-column offset | the control columns differ from each other, or from the interior of the plate                                                       |
| parity                | an alternating pattern across rows or columns                                                                                       |
| edge                  | the outer ring of wells differs, for example from evaporation                                                                       |
| row or column effect  | one row or column is shifted on its own                                                                                             |
| quadrant              | the four quadrants of the plate differ                                                                                              |
| local spatial         | a smooth patch that is not a row-plus-column map                                                                                    |

## Covariate effects

A covariate effect is driven by a measured quantity.
The first one is the cell count of the well, a proxy for confluence.

## Identifiability

Whether an artifact can be separated from biology depends on how treatments are placed.
Each artifact gets one of three grades for a given design:

- **by design**: the design separates it, for example control wells in two columns that should be identical.
- **under an assumption**: it can be separated if an assumption holds, for example that compounds are placed independently of position.
  The assumption is stated, and tested where it can be.
- **not identifiable**: the design cannot separate it.
  CytoDxRx says so instead of guessing.

For example, if every compound sits at one position and its replicates share that position, the compound and the position are confounded within a layout.
Replicate agreement is then partly agreement in position.

## Fitting several artifacts

Some artifacts share a basis, for example a row effect inside a tilt.
Overlapping artifacts are fitted in a fixed order or jointly, and a nested model comparison decides whether the extra artifact is needed.
The order and the units are fixed by the package, not chosen per run.
