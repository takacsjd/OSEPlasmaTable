#!/usr/bin/env python
"""AI_CAD object catalog: list objects and keep notes on each piece.

The "writing space" for describing each object lives in the part YAMLs
(parts/*.yaml, assemblies/*.yaml) under two fields:

  description: <free text>     <- what the piece IS (role, intent)
  notes:                       <- dated scratchpad, appended over time
    - date: 2026-10-27
      author: jon
      text: "..."

Commands:
  python objects.py list                table of every object in the project
  python objects.py show <ID>           full entry for one object (PART-*, ASMB-*)
  python objects.py note <ID> "text"    append a dated note (author from --who)
  python objects.py desc <ID> "text"    set/replace the description
  python objects.py new <ID> "name"     scaffold a new part file from a template

No FreeCAD required — pure file reads/writes against the YAML specs.
"""
import datetime as _dt
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent          # AI_CAD/
PARTS = ROOT / "parts"
ASMB = ROOT / "assemblies"


def _today():
    return _dt.date.today().isoformat()


def _load(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def discover():
    """Find every object file (parts + assemblies)."""
    files = []
    for d in (PARTS, ASMB):
        if d.is_dir():
            files.extend(sorted(d.glob("*.yaml")))
    return files


def collect():
    """One record per object, with summary fields pulled out of the YAML."""
    recs = []
    for f in discover():
        d = _load(f)
        measured = d.get("measured") or {}
        notes = d.get("notes") or []
        recs.append({
            "id": d.get("part_id") or d.get("assembly_id") or f.stem.upper(),
            "name": d.get("name", ""),
            "kind": "part" if f.parent == PARTS else "assembly",
            "file": str(f.relative_to(ROOT.parent)),
            "status": d.get("status", ""),
            "material": d.get("material", ""),
            "count": measured.get("count", ""),
            "mass_kg": measured.get("mass_total_kg") or measured.get("mass_kg") or "",
            "description": (d.get("description") or "").strip().split("\n")[0],
            "notes": len(notes),
            "last_measured": measured.get("date", ""),
        })
    return recs


def cmd_list():
    recs = collect()
    w_id, w_name, w_mass, w_desc = 16, 26, 10, 58
    line = "+" + "-" * (w_id + 1) + "+" + "-" * (w_name + 1) + "+" + "-" * (w_mass + 1) + "+" + "-" * (w_desc + 1) + "+"
    print(line)
    print(f"| {'ID':<{w_id}} | {'NAME':<{w_name}} | {'KG':>{w_mass}} | {'DESCRIPTION / NOTES':<{w_desc}} |")
    print(line)
    for r in recs:
        desc = (r["description"] or "-")[:w_desc]
        note_tag = f"  ({r['notes']} note{'s' if r['notes'] != 1 else ''})" if r["notes"] else ""
        mass = f"{r['mass_kg']:.2f}" if isinstance(r["mass_kg"], (int, float)) else (r["mass_kg"] or "-")
        print(f"| {r['id']:<{w_id}} | {r['name'][:w_name]:<{w_name}} | {mass:>{w_mass}} | {desc}{note_tag[:w_desc-len(desc)-1]:<{w_desc-len(desc)}} |")
    print(line)
    tot = sum(r["mass_kg"] for r in recs if isinstance(r["mass_kg"], (int, float)))
    print(f"objects: {len(recs)}   total measured mass: {tot:.1f} kg")
    print("detail:  python objects.py show <ID>")


def find_obj(obj_id):
    for f in discover():
        d = _load(f)
        if (d.get("part_id") or d.get("assembly_id") or f.stem.upper()) == obj_id.upper():
            return f, d
    print(f"ERROR: no object '{obj_id}' in {ROOT}")
    sys.exit(1)


def cmd_show(obj_id):
    f, d = find_obj(obj_id)
    d["description"] = d.get("description") or ""
    d["notes"] = d.get("notes") or []
    print(yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100))
    print(f"# file: {f.relative_to(ROOT.parent)}")


def _rewrite(f: Path, d):
    txt = yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100)
    txt = "# NOTE: description/notes/measured blocks maintained by tools/objects.py + build_table.py\n" + txt
    f.write_text(txt, encoding="utf-8")
    print(f"updated: {f.relative_to(ROOT.parent)}")


def cmd_note(obj_id, text, author):
    f, d = find_obj(obj_id)
    notes = d.get("notes") or []
    notes.append({"date": _today(), "author": author, "text": text})
    d["notes"] = notes
    _rewrite(f, d)


def cmd_desc(obj_id, text):
    f, d = find_obj(obj_id)
    d["description"] = text
    _rewrite(f, d)


TEMPLATE = """part_id: {id}
name: {name}
status: proposed
role:
description: >-
  <what this piece is, why it exists, how it fits the system>

material:
parameters:
instances:
- inst_id: {id}-INST-0
  placement: [0, 0, 0]
constraints:
measured:
notes:
- date: {today}
  author: jon
  text: scaffolded
references:
- path: ../global.yaml
provenance:
  source: scaffolded {today}
  built_by: pending
"""


def cmd_new(obj_id, name):
    if not re.fullmatch(r"[A-Z][A-Z0-9-]*", obj_id):
        print("ERROR: id must be UPPER-KEBAB like PART-GANTRY")
        sys.exit(1)
    f = PARTS / f"{obj_id.lower()}.yaml"
    if f.exists():
        print(f"ERROR: {f} already exists")
        sys.exit(1)
    f.write_text(TEMPLATE.format(id=obj_id, name=name, today=_today()), encoding="utf-8")
    print(f"created: {f.relative_to(ROOT.parent)}")


def main():
    a = sys.argv[1:]
    if not a or a[0] == "list":
        cmd_list()
    elif a[0] == "show":
        cmd_show(a[1])
    elif a[0] == "note":
        who = "jon"
        rest = a[1:]
        if "--who" in rest:
            i = rest.index("--who")
            who = rest[i + 1]
            rest = rest[:i] + rest[i + 2:]
        cmd_note(rest[0], " ".join(rest[1:]), who)
    elif a[0] == "desc":
        cmd_desc(a[1], " ".join(a[2:]))
    elif a[0] == "new":
        cmd_new(a[1], " ".join(a[2:]) or a[1].title())
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
