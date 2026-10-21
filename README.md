# Plasma table — project

Plasma cutting table for Uitvindersgilde (Hof van Cartesius, Utrecht).
Design phase, started 2026-10-20.

## Layout
- `drawings/`    — FreeCAD models, drawings, vendor STEP files
- `calc/`        — sizing calcs & comparisons (axis-sizing.md, etc.)
- `docs/`        — specs, decisions log, references notes
/`reference/`   — vendor datasheets, torque curves
- `spreadsheet/` — project tracking spreadsheet

## Core spec (draft)
- X + Y: HG20 linear rails, 2 rails × 2 blocks per axis
- Drive: ballscrew vs rack & pinion (decision in progress → calc/axis-sizing.md)
- Motors: StepperOnline closed-loop NEMA 24 (4 Nm) under evaluation
- Speed: 15 m/min travel (plasma cut speed)
- Bonus: light machining/drilling of soft metals (brass, alu) on X
- Adjustable table height

## Reference files acquired (2026-10-21) — in `drawings/`
- `drawings/24HS40-5004D-E1000.STEP` — **motor STEP model, 8.0 MB** (OMC/StepperOnline, login-free)
- `drawings/24HS40-5004D-E1000_Full_Datasheet.pdf` — full datasheet (OMC)
- `drawings/24HS40-5004D-E1000_Torque_Curve.pdf` — torque curve (OMC, SVG already here)
- `drawings/hiwin_Linear_Guideway_E1_catalog.pdf` — full HG-series catalog, 17.6 MB (Hiwin official; scanned-image PDF, dims by visual lookup)
- `drawings/hiwin_HG_series_catalog.pdf` — HG-Info intro catalog (Hiwin official)
- HGR20/HGH20 **STEP models: not downloaded** — GrabCAD, Hiwin CAD portal, 3Dfindit all require login. Decision: model from catalog dims in FreeCAD.

## Decisions log
- 2026-10-20: Project folder created. Drive sizing started (24HS40 NEMA 24).
- 2026-10-20: Corrected sizing (v2). Cut force is ~38 N (not 2000 N) → torque is
  trivial. The real constraint is **speed vs lead**: 15 m/min needs ≥20 mm ballscrew
  lead (24HS40 encoder caps at 900 rpm). 5 mm lead tops out ~6 m/min (matches
  colleague's Hypertherm 45 table). Corner decel is fine (stops <2 mm). Recommend
  20 mm lead ballscrew X for cutting + drilling; 5 mm lead only if precision-first.
  See calc/axis-sizing.md.
- 2026-10-20: Z axis = drilling/feed axis. 2000 N is the **Z downward feed force**
  (not X). Z: 2x HG20 + **2.5 mm lead screw** (self-locking, NEMA24 OK) +
  **thrust ball bearing 51217** (the "cone + cylinder" lathe-type bearing, 96 kN C,
  2.1% utilisation). Spindle: **Flipsky brushless off-axis, belt-reduced**,
  ~1300 rpm, ~1–2.5 Nm, ~150–300 W for 6 mm HSS in steel. 6 mm max hole.
  Tool changer (plasma+drill) shares one Z axis. See calc/z-axis-spindle.md.
