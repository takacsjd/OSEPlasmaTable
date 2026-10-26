---
name: ai-cad-workflow
description: "Use when working from AI_CAD/workflow.xlsx to clarify device requirements, update parts/features/constraints, export JSON, or create and iteratively revise FreeCAD part macros."
---

# AI_CAD workbook-to-FreeCAD workflow

Follow the project workflow in [AI_CAD/WORKFLOW.md](../../../AI_CAD/WORKFLOW.md).

## Procedure

1. Inspect the workbook, generated JSON, project notes, and relevant references
   before proposing geometry.
2. Distinguish confirmed requirements from draft, proposed, inferred, and
   unknown information. Do not promote a suggestion to a hard constraint.
3. Ask the user about missing or conflicting values that materially change the
   part shape, interfaces, envelope, or safety. State assumptions explicitly
   for low-impact details.
4. When the user requests a new part, add or update workbook rows only for
   clearly relevant requirements, parts, features, or references. Use stable
   IDs, retain existing IDs, assign draft/proposed status to unapproved
   additions, and add a `Change_Log` entry explaining the change.
5. Run the exporter and resolve its validation errors:

   ```powershell
   python AI_CAD\tools\export_workbook.py
   ```

6. Generate a standalone FreeCAD macro driven by the relevant exported JSON.
   Include source part/feature IDs and paths in the script, preserve part-local
   coordinates, and report its envelope and datum.
7. Save to a new output file. Provide concise run instructions and ask the user
   to return the render, FreeCAD console errors, and requested revisions.
8. After feedback, revise the macro and, when the user accepts a design change,
   update the workbook and re-export. Do not claim a model has been rendered or
   validated unless it was actually run in FreeCAD.

The workbook is the editable source of intent; files under
`AI_CAD/generated/` are derived and must not be manually edited.
