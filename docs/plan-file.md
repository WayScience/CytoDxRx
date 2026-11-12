# The plan file

`discover` writes a plan file.
A person reads the report, edits the plan, and `apply` reads only what was approved.
This page is a draft of the format; it will change when the first implementation is reviewed.

```yaml
cytodxrx_plan: 1
software_version: 0.1.0
experiment:
  plate_format: [16, 24]
  plates: [BR00148919, BR00148920]
entries:
  - artifact: control_column_offset
    status: proposed           # proposed, approved or rejected
    identifiability: by_design # by_design, under_assumption or not_identifiable
    assumptions: []
    evidence:
      statistic: 0.97
      baseline: 0.55
    parameters: {}
```

## Rules

- `discover` writes every entry as `proposed`.
- A person changes an entry to `approved` or `rejected`.
  Nothing else in the file is meant to be edited by hand.
- `apply` applies only `approved` entries, in the package's fixed order.
- An entry that is `not_identifiable` cannot be approved.
- Unknown keys are an error, so a typo cannot silently change what is applied.
- The plan records the version of CytoDxRx that wrote it.
