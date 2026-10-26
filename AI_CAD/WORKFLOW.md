# AI_CAD workflow and data contract

## Purpose

Use a user-edited workbook to organize project intent, then export validated
JSON for an agent to inspect and use when creating standalone FreeCAD macros.
The workflow is deliberately staged: a valid export does not mean a part is
fully specified, and a rendered model is not an engineering approval.

## Work sequence

1. Read `Device_Brief`, `Constraints`, `Parts`, `Features`, `Assemblies`,
   `Instances`, `Connections`, `References`, and `Change_Log`.
2. Run `python AI_CAD\tools\export_workbook.py` after workbook edits. Resolve
   validation errors before modeling.
3. Review the relevant `generated/parts/<part_id>.json`, project constraints,
   source documents, and any existing FreeCAD models.
4. Identify missing dimensions, conflicting requirements, uncertain references,
   and decisions that materially affect geometry. Ask the user focused
   clarification questions rather than silently guessing.
5. If the user agrees that an item belongs in the design, add it to the
   workbook with a stable ID and a draft/proposed status. Record the reason in
   `Change_Log`, then export again. Keep unapproved ideas visibly proposed.
6. Generate a standalone FreeCAD macro for the requested part. The macro must
   cite the part ID, JSON path, workbook, assumptions, and any reference files
   in its header or document metadata.
7. Build geometry in the part-local coordinate system, name meaningful
   features, recompute, check for invalid/empty shapes, report the bounding
   envelope, and save a render and native FreeCAD document. Do not modify an
   existing model unless the user requests that.
8. The user runs the macro in FreeCAD, reviews the model/render, and provides
   feedback. Update the workbook only for accepted design changes and preserve
   a change-log entry.

## Workbook rules

- One record per row in the Excel tables; do not rename required worksheets or
  headers without updating the exporter.
- IDs are stable references (`PART-*`, `FEAT-*`, `CON-*`, `ASMB-*`, `INST-*`,
  `CONN-*`, `REF-*`, `CHG-*`). Names and descriptions may be edited.
- `target_envelope_x/y/z` are optional part-local design targets in the
  project `length_units`; they are not a substitute for the measured envelope
  the generated FreeCAD macro must report.
- Use semicolons between multiple IDs in a cell.
- Blank means unknown/not supplied, never numeric zero.
- `hard` means a requirement; `preferred` allows a documented trade-off;
  `informational` records context without a pass/fail claim.
- `draft`, `proposed`, `open`, and `future` statuses are not released design
  decisions. Keep source and authority information with any important claim.
- Use repository-relative reference paths. A reference is a pointer; the agent
  must actually inspect the file before relying on its contents.
- `Assemblies` identify groupings; `Instances` identify each occurrence of a
  part; `Connections` describe joints between named interfaces. Do not infer
  placements or joints from membership alone.

## FreeCAD macro contract

For every generated part macro:

- Use millimetres unless the part specification explicitly says otherwise.
- Keep the part geometry in its local coordinates. Set a clear datum/origin;
  represent assembly placement separately.
- Report local X/Y/Z bounding-box min/max and length/width/height.
- Report the chosen placement datum and, when useful, center of mass separately.
- Use stable labels tied to feature IDs where possible.
- Make required features explicit. If a required feature cannot be built,
  stop with a useful error; do not silently omit it.
- Include optional features only when specified or requested.
- Check that recomputed shapes are non-null and valid before saving.
- Save to a new file by default. Do not overwrite the source workbook, JSON,
  or an existing FreeCAD document.
- Distinguish measured geometry checks from engineering validation. A bounding
  box check is not a strength, fit, electrical, safety, or manufacturability
  certification.

## Plasma-table seed data notes

Initial workbook entries are projected from `README.md`, `calc/`, and
`drawings/`. Some notes disagree or describe evolving concepts: for example,
the current tank is documented as 1712 x 1712 x 140 mm, while the machine
envelope is 1600 x 2500 mm; the earlier lift calculation uses a shallower
water table; and the slat note suggests moving from 2 mm to 3 mm. These are
deliberately visible as draft/proposed and need reconciliation before a final
assembly.

The exporter checks data shape and references, not engineering correctness.
The workbook and generated geometry are planning/design aids only.
