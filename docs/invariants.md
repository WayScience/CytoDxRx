# Invariants

These are statements the package is meant to keep true.
Each one is written down before its code, so it can be reviewed and then checked.
They are checked in one of three ways, and the docs say which:

- **formally proved**: a proof covers every input.
  Nothing is proved yet.
- **bounded symbolic check**: a tool searched for a counterexample and found none within a time limit.
  This is not a proof.
- **property test**: a test runs many generated inputs, with a tolerance for floating-point numbers.

| Area            | Invariant                                                                                                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| plate geometry  | a well name and its row and column are the same information: converting one way and back returns the original, for every well of every plate format                            |
| design table    | every well of every plate has exactly one role, and a well that has a compound is never a control                                                                              |
| identifiability | a grade is always one of the three; adding controls never lowers a grade                                                                                                       |
| correction      | a correction is a constant per well and feature, so the median of the corrected cells of a well equals the corrected well profile                                              |
| correction      | the weight used to shrink a layout's amplitude toward the shared value is between 0 and 1, so the shrunk amplitude lies between the layout's own estimate and the shared value |
| ordering        | the order in which artifacts are fitted is fixed and respects their dependencies                                                                                               |
| plan            | `apply` uses only approved entries, never a proposed or rejected one                                                                                                           |
| plan            | reading a plan file and writing it again returns the same plan                                                                                                                 |
| tables          | a correction table is keyed on plate and well, and applying it to a table it does not cover is an error                                                                        |
