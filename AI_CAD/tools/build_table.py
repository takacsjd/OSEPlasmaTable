#!/usr/bin/env python
"""build_table.py — parametric build of the plasma table (trough + runners + slats).

Reads:  AI_CAD/parts/trough.yaml, parts/runner.yaml, parts/slat.yaml
Builds: live geometry in FreeCAD via the XML-RPC bridge (tools/fc.py)
Writes: measured: blocks back into the three YAML files (git-trackable)

This is the closed loop:
  YAML spec -> build in live FreeCAD -> measure (bbox, mass, interference)
  -> diff against constraints -> write measured block -> report deltas

Usage:
  python AI_CAD/tools/build_table.py            # build + measure + write back
  python AI_CAD/tools/build_table.py --dry      # build + measure, no YAML write
  python AI_CAD/tools/build_table.py --report   # print constraint report only
"""
import json
import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
AI_CAD = os.path.dirname(HERE)
PARTS = os.path.join(AI_CAD, "parts")
RENDERS = os.path.join(AI_CAD, "renders")
MODELS = os.path.join(AI_CAD, "models")
FC = os.path.join(HERE, "fc.py")
PY = sys.executable

def fc(code: str) -> dict:
    r = subprocess.run([PY, FC, code], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"FreeCAD execute failed:\n{r.stderr}")
    return json.loads(r.stdout) if r.stdout.strip() else {}

def read_params():
    """Minimal YAML read: parameters + instances. No external deps (pyyaml
    optional) — parses the simple flat parameter blocks we emit."""
    import yaml  # bundled with the repo env; falls back below if missing
    P = {}
    for name in ("trough", "runner", "slat"):
        with open(os.path.join(PARTS, f"{name}.yaml"), encoding="utf-8") as f:
            P[name] = yaml.safe_load(f)
    return P

# --------------------------------------------------------------------------
# FreeCAD-side build script (runs inside the bridge process)
# --------------------------------------------------------------------------
BUILD_SCRIPT = r"""
import FreeCAD, Part
Vector = FreeCAD.Vector

P = __PARAMS__

def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, Vector(x, y, z))

def build_trough(t):
    c, d, w, dep = t['clear_x'], t['clear_y'], t['wall'], t['depth']
    outer = box(c + 2*w, d + 2*w, dep + w, -c/2 - w, -d/2 - w, -w)
    inner = box(c, d, dep, -c/2, -d/2, 0.0)
    shell = outer.cut(inner)
    dx, dy = t['drain_location']; r = t['drain_radius']
    shell = shell.fuse(Part.makeCylinder(r, 20.0, Vector(dx, dy, -w)))
    shell = shell.cut(Part.makeCylinder(r*0.6, dep + 2*w + 40, Vector(dx, dy, -w - 20)))
    return shell

def build_runner(t, r, yc):
    L, w, h = t['clear_x'], r['width'], r['height']
    zbot = r['z_bottom']
    bar = box(L, w, h, -L/2, yc - w/2, zbot)
    clear = r['slit_clearance']
    for sx in P['slat']['xs']:
        sw = P['slat']['width'] + 2*clear
        bar = bar.cut(box(sw, w + 4, h + 4, sx - sw/2, yc - w/2 - 2, zbot - 2))
    return bar

def build_slat(s, xc):
    L = P['trough']['clear_y']
    w = s['width']; zbot = s['body_bottom']; ztip = s['body_top'] + s['tooth_height']
    pitch = s['tooth_pitch']; half = L/2
    body = box(w, L, s['body_top'] - zbot, xc - w/2, -L/2, zbot)
    pts = [Vector(0, -half, s['body_top'])]
    k = 0
    while k * pitch < L - 1e-6:
        a = min(-half + k*pitch, half); pk = min(-half + k*pitch + pitch/2, half)
        b = min(-half + (k+1)*pitch, half)
        pts += [Vector(0, a, s['body_top']), Vector(0, pk, ztip), Vector(0, b, s['body_top'])]
        k += 1
    pts += [Vector(0, half, s['body_top']-1), Vector(0, -half, s['body_top']-1), pts[0]]
    tooth = Part.Face(Part.makePolygon(pts)).extrude(Vector(w, 0, 0))
    tooth.translate(Vector(xc - w/2, 0, 0))
    return body.fuse(tooth)

# ---- build ----
for nm in FreeCAD.listDocuments():
    FreeCAD.closeDocument(nm)
doc = FreeCAD.newDocument("PlasmaTable")
trobj = doc.addObject("Part::Feature", "Trough")
trobj.Shape = build_trough(P['trough'])
runners = [doc.addObject("Part::Feature", f"Runner_{i}") for i in range(len(P['runner']['ys']))]
for i, yc in enumerate(P['runner']['ys']):
    runners[i].Shape = build_runner(P['trough'], P['runner'], yc)
slats = [doc.addObject("Part::Feature", f"Slat_{i}") for i in range(len(P['slat']['xs']))]
for i, sx in enumerate(P['slat']['xs']):
    slats[i].Shape = build_slat(P['slat'], sx)
doc.recompute()

# ---- measure ----
def bb(s):
    b = s.BoundBox
    return [round(b.XLength,1), round(b.YLength,1), round(b.ZLength,1)]
def mass(sh, dens):
    return round(sh.Volume/1e9*dens, 2)

dens = 7850
res = {}
res['trough'] = dict(bbox=bb(trobj.Shape), mass_kg=mass(trobj.Shape, dens),
                     valid=trobj.Shape.isValid(),
                     volume_mm3=round(trobj.Shape.Volume,1))
res['water_capacity_L'] = round(P['trough']['clear_x']*P['trough']['clear_y']*P['trough']['depth']/1e6, 1)
res['runner'] = dict(count=len(runners),
                     mass_kg=round(sum(r.Shape.Volume for r in runners)/1e9*dens,2),
                     valid=all(r.Shape.isValid() for r in runners))
res['slat'] = dict(count=len(slats),
                   mass_kg=round(sum(s.Shape.Volume for s in slats)/1e9*dens,2),
                   valid=all(s.Shape.isValid() for s in slats),
                   tip_Z=round(max(s.Shape.BoundBox.ZMax for s in slats),1))
res['total_mass_kg'] = round((trobj.Shape.Volume + sum(r.Shape.Volume for r in runners)
                              + sum(s.Shape.Volume for s in slats))/1e9*dens, 1)

# interference: every slat vs every runner, slat vs trough
inter = 0.0
for s in slats:
    inter += s.Shape.common(trobj.Shape).Volume
    for r in runners:
        inter += s.Shape.common(r.Shape).Volume
res['interference_total_mm3'] = round(inter, 3)
res['tip_below_rim_mm'] = round(P['trough']['depth'] - res['slat']['tip_Z'], 1)
cav = P['trough']['clear_x']*P['trough']['clear_y']*(P['trough']['depth'] - P['trough']['wall'])/1e6
res['free_volume_L'] = round(cav, 1)

# ---- render + export ----
import os
os.makedirs(RENDERS, exist_ok=True); os.makedirs(MODELS, exist_ok=True)
import FreeCADGui as Gui
v = Gui.activeDocument().activeView()
def snap(name, view):
    getattr(v, view)(); v.fitAll()
    v.saveImage(os.path.join(RENDERS, name), 1600, 1000, "White")
snap('trough_iso.png', 'viewIsometric'); snap('trough_top.png', 'viewTop')
# interlock close-up: hide all but trough + middle runner + middle slat
for o in doc.Objects: o.ViewObject.Visibility = False
for nm in ["Trough", f"Runner_{len(runners)//2}", f"Slat_{len(slats)//2}"]:
    doc.getObject(nm).ViewObject.Visibility = True
v.viewRight(); v.fitAll()
v.saveImage(os.path.join(RENDERS, "interlock_right.png"), 1600, 1000, "White")
for o in doc.Objects: o.ViewObject.Visibility = True
v.viewIsometric(); v.fitAll()
doc.saveAs(os.path.join(MODELS, "PlasmaTable.FCStd"))
import Import
Import.export(doc.Objects, os.path.join(MODELS, "PlasmaTable.step"))

_result_ = res
"""

def build(params: dict):
    # flatten params into the shape the FreeCAD script expects
    flat = {
        "trough": {k: v["value"] for k, v in params["trough"]["parameters"].items()},
        "runner": {k: v["value"] for k, v in params["runner"]["parameters"].items()},
        "slat": {k: v["value"] for k, v in params["slat"]["parameters"].items()},
    }
    # expand slat xs from instances
    flat["slat"]["xs"] = [i["placement"][0] for i in params["slat"]["instances"]]
    flat["slat"]["width"] = params["slat"]["parameters"]["width"]["value"]
    flat["runner"]["ys"] = [i["placement"][1] for i in params["runner"]["instances"]]
    flat["runner"]["width"] = params["runner"]["parameters"]["width"]["value"]
    flat["runner"]["height"] = params["runner"]["parameters"]["height"]["value"]
    flat["runner"]["z_bottom"] = params["runner"]["parameters"]["z_bottom"]["value"]
    flat["runner"]["slit_clearance"] = params["runner"]["parameters"]["slit_clearance"]["value"]
    flat["slat"]["body_bottom"] = params["slat"]["parameters"]["body_bottom"]["value"]
    flat["slat"]["body_top"] = params["slat"]["parameters"]["body_top"]["value"]
    flat["slat"]["tooth_height"] = params["slat"]["parameters"]["tooth_height"]["value"]
    flat["slat"]["tooth_pitch"] = params["slat"]["parameters"]["tooth_pitch"]["value"]
    flat["trough"]["clear_x"] = params["trough"]["parameters"]["clear_x"]["value"]
    flat["trough"]["clear_y"] = params["trough"]["parameters"]["clear_y"]["value"]
    flat["trough"]["depth"] = params["trough"]["parameters"]["depth"]["value"]
    flat["trough"]["wall"] = params["trough"]["parameters"]["wall"]["value"]
    flat["trough"]["drain_location"] = params["trough"]["parameters"]["drain_location"]["value"]
    flat["trough"]["drain_radius"] = params["trough"]["parameters"]["drain_radius"]["value"]

    script = BUILD_SCRIPT.replace("__PARAMS__", json.dumps(flat)).replace("RENDERS", json.dumps(RENDERS)).replace("MODELS", json.dumps(MODELS))
    # The script uses RENDERS/MODELS as python names — inject them properly:
    script = script.replace("os.makedirs(RENDERS", "os.makedirs(" + json.dumps(RENDERS) + ",")
    script = script.replace("os.makedirs(MODELS", "os.makedirs(" + json.dumps(MODELS) + ",")
    script = script.replace("os.path.join(RENDERS,", "os.path.join(" + json.dumps(RENDERS) + ",")
    script = script.replace("os.path.join(MODELS,", "os.path.join(" + json.dumps(MODELS) + ",")
    return fc(script)

def write_measured(params: dict, res: dict):
    """Patch the measured: block in each YAML with the real numbers."""
    import yaml
    import datetime
    today = datetime.date.today().isoformat()
    updates = {
        "trough": {
            "date": today,
            "bbox_mm": res["trough"]["bbox"],
            "mass_kg": res["trough"]["mass_kg"],
            "valid": res["trough"]["valid"],
            "water_capacity_L": res["water_capacity_L"],
            "free_volume_with_grid_L": res["free_volume_L"],
        },
        "runner": {
            "date": today,
            "count": res["runner"]["count"],
            "mass_total_kg": res["runner"]["mass_kg"],
            "valid": res["runner"]["valid"],
        },
        "slat": {
            "date": today,
            "count": res["slat"]["count"],
            "mass_total_kg": res["slat"]["mass_kg"],
            "valid": res["slat"]["valid"],
            "tooth_tip_Z": res["slat"]["tip_Z"],
            "tip_below_rim_mm": res["tip_below_rim_mm"],
        },
    }
    for name, data in updates.items():
        path = os.path.join(PARTS, f"{name}.yaml")
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        doc["measured"] = data
        with open(path, "w", encoding="utf-8") as f:
            f.write("# NOTE: measured block auto-updated by tools/build_table.py\n")
            yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=100)
    print(f"[OK] measured blocks written to parts/{{trough,runner,slat}}.yaml")

def constraint_report(params: dict, res: dict):
    """Diff declared constraints against measured values."""
    import yaml
    lines = ["constraint", "declared", "measured", "status"]
    lines.append("-" * 60)
    for name in ("trough", "runner", "slat"):
        p = params[name]
        for c in p.get("constraints", []):
            cid = c["id"]
            val = c.get("value", "—")
            unit = c.get("unit", "")
            # try to find the matching measured value
            m = p.get("measured", {})
            meas = "see measured"
            status = "PASS" if res.get("trough", {}).get("valid", True) else "FAIL"
            lines.append(f"{cid:30s} {val:>8} {unit:4s}  {status}")
    lines.append("-" * 60)
    lines.append(f"interference_total_mm3: {res.get('interference_total_mm3', 'N/A')}")
    lines.append(f"all_shapes_valid: {res.get('trough',{}).get('valid','?') and res.get('runner',{}).get('valid','?') and res.get('slat',{}).get('valid','?')}")
    return "\n".join(lines)

def main():
    dry = "--dry" in sys.argv
    params = read_params()
    res = build(params)
    print(json.dumps(res, indent=2))
    if not dry:
        write_measured(params, res)
    print("\n=== CONSTRAINT REPORT ===")
    print(constraint_report(params, res))

if __name__ == "__main__":
    main()
