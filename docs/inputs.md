# Inputs and outputs

This page is the input contract.
CytoDxRx requires these inputs rather than processing raw data itself.

## Inputs

### Well-level profiles

One row per well per plate, un-normalized, after cell quality control.
Parquet or CSV, one file per plate or one pooled file.

| Column             | Meaning                                               |
| ------------------ | ----------------------------------------------------- |
| `Metadata_Plate`   | the plate barcode                                     |
| `Metadata_Well`    | the well name, such as `A01` or `P24`                 |
| other `Metadata_*` | kept as they are                                      |
| everything else    | numeric features, which keep their CellProfiler names |

### Platemaps

A platemap says what is in each well.
A barcode-to-platemap table links each plate to its platemap.
A **layout** is a set of plates that share the same arrangement.

A platemap needs a well column, a compound identifier column and a solvent column.
The column names are parameters.
A platemap may also have a role column that sets each well's role explicitly.

### Plate format

The number of rows and columns of the plate, for example 8 by 12 (96 wells) or 16 by 24 (384 wells).
Well names have a row letter and a column number, as in `A01`.

### Optional inputs

- A cell count per well, which enables the cell-density correction.
- Labels for validation, for example a mechanism of action for each compound.

## The design table

CytoDxRx builds one table from the platemaps, with one row per well of every plate.
Every well has exactly one role:

| Role       | Meaning                                    |
| ---------- | ------------------------------------------ |
| `compound` | the well has a compound                    |
| `control`  | the well has no compound but has a solvent |
| `empty`    | the well has neither                       |

If the platemap has a role column, it decides.
Otherwise the role follows from the compound and solvent columns.
A well that a platemap does not list is `empty`.
Platemaps that contradict themselves, for example a control well with a compound, are an error that names the wells.

## Outputs

- **Correction tables**, keyed on plate and well: a shift per well and feature, and a scale per plate.
- **Corrected profiles**, in the original units.
- **The plan file**, which records what was found and what a person approved.
- **A report** for the person who reviews the plan.
