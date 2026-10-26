# AI_CAD workflow

This folder contains a draft, project-local workbook-to-JSON workflow for
AI-assisted FreeCAD work. The workbook is seeded with current plasma-table
notes so it can be reviewed and corrected; candidate components are not final
design decisions.

## Files

- `workflow.xlsx` — work instructions plus human-edited project brief,
  constraints, part/feature registry, assembly instances/connections,
  references, and change log.
- `WORKFLOW.md` — human and agent process, status meanings, and design
  boundaries.
- `requirements.txt` — Python dependency for reading/writing Excel workbooks.
- `tools/create_workbook.py` — rebuilds the initial workbook template. This
  overwrites `workflow.xlsx`; do not run it after users have entered data.
- `tools/export_workbook.py` — validates workbook references and exports JSON.
- `schemas/part.schema.json` — starter JSON Schema for exported per-part
  documents.
- `generated/` — generated JSON snapshots; regenerate after workbook edits.

The agent skill is in
[`.github/skills/ai-cad-workflow/SKILL.md`](../.github/skills/ai-cad-workflow/SKILL.md).

## Quick start

From the repository root, install the exporter dependency once:

```powershell
python -m pip install -r AI_CAD\requirements.txt
```

Export the workbook:

```powershell
python AI_CAD\tools\export_workbook.py
```

Or provide paths:

```powershell
python AI_CAD\tools\export_workbook.py --workbook AI_CAD\workflow.xlsx --output AI_CAD\generated
```

The exporter stops with a clear error for missing required sheets/columns,
duplicate IDs, broken part/feature/assembly references, or missing/escaping
reference paths. It does not generate FreeCAD geometry.

## Source of truth

`workflow.xlsx` is the user-maintained source of project intent. JSON in
`generated/` is derived output and must not be edited by hand. Per-part JSON
files preserve feature descriptions and constraints for the agent and future
FreeCAD scripts. Assembly JSON records instances and connections; blank
placements and empty connections are intentionally unresolved, not zero-valued.

Use repository-relative paths in `References.path`. The exporter verifies that
each referenced path exists inside the repository.
