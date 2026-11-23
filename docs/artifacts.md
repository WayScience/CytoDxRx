# Technical artifacts

A **technical artifact** is a technical effect on well profiles that is not biology.
This page names the technical artifacts CytoDxRx is built around.
Each technical artifact is added only when it has a detector, a fit and a validation.
Nothing is implemented yet.
The literature behind the names is listed under [References](#references).

## Position effects

A position effect is a function of where a well sits on the plate.

| Technical artifact    | What it is                                                                                                                          |
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

Whether a technical artifact can be separated from biology depends on how treatments are placed.
Each technical artifact gets one of three grades for a given design:

- **by design**: the design separates it, for example control wells in two columns that should be identical.
- **under an assumption**: it can be separated if an assumption holds, for example that compounds are placed independently of position.
  The assumption is stated, and tested where it can be.
- **not identifiable**: the design cannot separate it.
  CytoDxRx says so instead of guessing.

For example, if every compound sits at one position and its replicates share that position, the compound and the position are confounded within a layout.
Replicate agreement is then partly agreement in position.

## Fitting several technical artifacts

Some technical artifacts share a basis, for example a row effect inside a tilt.
Overlapping technical artifacts are fitted in a fixed order or jointly, and a nested model comparison decides whether the extra technical artifact is needed.
The order and the units are fixed by the package, not chosen per run.

## References

Plate position effects are long known in screening, mostly from plate-based assays that read out one value per well.
These papers back the following names:

- **edge**: Lundholt et al., "A simple technique for reducing edge effect in cell-based assays", *J Biomol Screen* 8(5):566-570 (2003), [doi:10.1177/1087057103256465](https://doi.org/10.1177/1087057103256465).

- **row or column effect**: Brideau et al., "Improved statistical methods for hit selection in high-throughput screening", *J Biomol Screen* 8(6):634-647 (2003), [doi:10.1177/1087057103258285](https://doi.org/10.1177/1087057103258285), which introduced the B-score, a median-polish correction of row and column effects.
  Malo et al., "Statistical practice in high-throughput screening data analysis", *Nat Biotechnol* 24(2):167-175 (2006), [doi:10.1038/nbt1186](https://doi.org/10.1038/nbt1186), which models a row and a column offset for each plate.

- **position effects in general**: Makarenkov et al., "An efficient method for the detection and elimination of systematic error in high-throughput screening", *Bioinformatics* 23(13):1648-1657 (2007), [doi:10.1093/bioinformatics/btm145](https://doi.org/10.1093/bioinformatics/btm145).

- **cell-count covariate effect**: Seal et al., "Counting cells can accurately predict small-molecule bioactivity benchmarks", *Nature Communications* 17:2436 (2026), [doi:10.1038/s41467-026-68725-5](https://doi.org/10.1038/s41467-026-68725-5), which shows that cell count confounds Cell Painting benchmarks and recommends excluding features that are strongly correlated with it.
  Rezvani et al., "Image-based cell profiling enhancement via data cleaning methods", *PLOS ONE* 17(5):e0267280 (2022), [doi:10.1371/journal.pone.0267280](https://doi.org/10.1371/journal.pone.0267280), which regresses cell area out of the other features on each plate; it adjusts for cell area, not cell count.
  Snijder et al., "Population context determines cell-to-cell variability in endocytosis and virus infection", *Nature* 461:520-523 (2009), [doi:10.1038/nature08282](https://doi.org/10.1038/nature08282), on how a cell's population context, including local cell density, shapes its phenotype.

No reference is given for the other names: tilt, control-column offset, parity, quadrant and local spatial.
They name patterns seen in image-based profiles and are CytoDxRx's own.
Each one is added only after a detector shows it in data.
