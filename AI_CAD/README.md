# AI CAD — Engineering Management of the Design Cycle

A closed-loop system for iterating on mechanical design using a live FreeCAD
process as the geometry/verification channel. The data is YAML in git; the
geometry is built, measured, and verified in real time through an XML-RPC
bridge into a running FreeCAD instance.

## Architecture

```
AI_CAD/
  README.md                  ← this file
  WORKFLOW.md                ← step-by-step closed loop
  global.yaml                ← shared units, materials, design rules
  parts/                     ← one YAML per part
    trough.yaml              ← PART-TROUGH (anchor)
    runner.yaml              ← PART-RUNNER
    slat.yaml                ← PART-SLAT
  assemblies/
    table.yaml               ← ASMB-TABLE (trough + runner grid + slat grid)
  models/                    ← FreeCAD native + STEP exports (git)
    PlasmaTable.FCStd
    PlasmaTable.step
  renders/                   ← PNG screenshots (git, for review)
    trough_iso.png
    trough_top.png
    interlock_right.png
  tools/
    fc.py                    ← XML-RPC client for the FreeCAD bridge
    build_table.py           ← parametric build + measure + write-back
```

## The Closed Loop

```
        ┌─────────────────────────────────────────────┐
        │  1. DECLARE  —  YAML spec (in git)          │
        │  parts/trough.yaml, runner.yaml, slat.yaml  │
        │  constraints, candidates, parameters        │
        └──────────────────┬──────────────────────────┘
                           ▼
        ┌─────────────────────────────────────────────┐
        │  2. BUILD    —  FreeCAD live (XML-RPC)      │
        │  tools/build_table.py                       │
        │  reads YAML → parametric geometry           │
        └──────────────────┬──────────────────────────┘
                           ▼
        ┌─────────────────────────────────────────────┐
        │  3. MEASURE  —  read-back from FreeCAD      │
        │  bbox, volume, mass, validity, interference │
        │  tip clearance, free water volume           │
        └──────────────────┬──────────────────────────┘
                           ▼
        ┌─────────────────────────────────────────────┐
        │  4. DIFF     —  declared vs measured        │
        │  constraint_report() prints PASS/FAIL       │
        │  per constraint                             │
        └──────────────────┬──────────────────────────┘
                           ▼
        ┌─────────────────────────────────────────────┐
        │  5. WRITE  —  measured: blocks into YAML    │
        │  (git-trackable, human-readable)            │
        └──────────────────┬──────────────────────────┘
                           ▼
        ┌─────────────────────────────────────────────┐
        │  6. DECIDE —  user reviews renders + data   │
        │  promote/reject candidates, lock constraints│
        │  → next iteration                           │
        └─────────────────────────────────────────────┘
```

## Prerequisites

- **FreeCAD 1.1+** running with the RobustMCPBridge workbench loaded.
- Bridge listening on port **9875** (XML-RPC).
- Verify: `python AI_CAD/tools/fc.py "import FreeCAD; _result_=FreeCAD.Version()"`

Relaunch FreeCAD if dead:
```
"C:/Program Files/FreeCAD 1.1/bin/freecad.exe" \
  "C:/Users/Core/AppData/Roaming/FreeCAD/Mod/RobustMCPBridge/freecad_mcp_bridge/blocking_bridge.py"
```

## Usage

```bash
# Build + measure + write measured blocks back to YAMLs + print report
python AI_CAD/tools/build_table.py

# Build + measure + print report (no YAML write)
python AI_CAD/tools/build_table.py --dry
```

Output:
- `models/PlasmaTable.FCStd` — native FreeCAD document
- `models/PlasmaTable.step`  — STEP export (CAD exchange)
- `renders/*.png`            — screenshots for review
- `parts/*.yaml`             — `measured:` blocks updated in-place
- Stdout: JSON results + constraint report (PASS/FAIL per constraint)

## YAML Schema (per part)

```yaml
part_id: PART-TROUGH        # stable ID
name: Plasma table trough
status: active              # draft | active | frozen
role: anchor                # anchor | structural | functional
material: steel

parameters:                 # parametric fields
  clear_x: { value: 1700, unit: mm, constraint_id: CON-TROUGH-CLEAR }
  depth:   { value: 140,  unit: mm, constraint_id: CON-TROUGH-DEPTH }
  wall:    { value: 6,    unit: mm }

instances:                  # one entry per placed copy
  - inst_id: INST-0
    placement: [0, 0, 0]

constraints:                # the engineering contract
  - id: CON-TROUGH-CLEAR
    description: Internal clear width
    value: 1700
    unit: mm
    priority: hard          # hard | preferred | informational
    status: confirmed       # open | proposed | confirmed | locked
    provenance: "User spec 2026-10-26"

candidates:                 # design alternatives under test
  - id: CAND-TROUGH-01
    description: "Welded box, 6mm steel"
    status: confirmed       # proposed | testing | confirmed | rejected
    note: "Measured 2026-10-26"

measured:                   # auto-written by build_table.py
  date: "2026-10-26"
  bbox_mm: [1712.0, 1712.0, 146.0]
  mass_kg: 183.15
  valid: true

provenance:
  source: "User conversation 2026-10-20 through 2026-10-26"
  built_by: "Hermes Agent + FreeCAD 1.1.3 MCP bridge"
  last_measured: "2026-10-26"
```

## What Changed from the Old AI_CAD

| Old (xlsx/JSON/macro) | New (YAML/live bridge) |
|---|---|
| 9-sheet xlsx workbook (~120 cols) | One YAML per part |
| Standalone FreeCAD macro (manual exec) | XML-RPC bridge (live, in-process) |
| Manual error reporting (read macro output) | `build_table.py` prints PASS/FAIL per constraint |
| 3 synced copies (xlsx + JSON + macro) | 1 source (YAML) + 1 derived (FCStd/STEP) |
| No fit check | Boolean intersection + min distance (measured) |
| No candidate tracking | `candidates[]` with lifecycle |
| Blank = unknown (spreadsheet) | `measured:` block, git-diffable |

## Constraint IDs

Stable IDs follow the pattern:
- `CON-<PART>-<FEATURE>` for constraints
- `FEAT-<PART>-<FEATURE>` for features
- `INST-<PART>-<N>` for placed instances
- `CAND-<PART>-<NN>` for candidates

Priority tiers:
- **hard** — must be satisfied; geometry cannot ship otherwise
- **preferred** — strongly desired; deviation requires justification
- **informational** — for reference; no enforcement

Status lifecycle:
`open → proposed → confirmed → locked` (for constraints)
`proposed → testing → confirmed | rejected` (for candidates)

## Legacy

`AI_CAD/legacy/` holds the old xlsx/JSON/macro system (openpyxl workbook,
`generated/*.json`, `project.json` catalog, `part.schema.json`, and the
`export_workbook` test). It is preserved, not deleted — `project.json` still
holds the full part catalog (gantry, torch, rotary, etc.) that will be
converted to per-part YAML as each part is worked. Nothing in the live loop
reads from it; the openpyxl dependency is gone from the active tooling.

## Measured Results (2026-10-26)

| Part | Count | Mass (kg) | Valid | Notes |
|---|---|---|---|---|
| Trough | 1 | 183.15 | ✓ | 1712×1712×146 mm outer, ~387 L water |
| Runner | 3 | 49.96 | ✓ | 40×40 mm, full-height through-slits |
| Slat | 11 | 213.59 | ✓ | Shark-tooth, tips at Z=112 (28 mm below rim) |
| **Total** | **15** | **446.7** | **✓** | **Zero interference, 16/16 constraints PASS** |
