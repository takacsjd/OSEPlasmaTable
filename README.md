# Plasma table — project

Plasma cutting table for Uitvindersgilde (Hof van Cartesius, Utrecht).
Design phase, started 2026-10-20.

## Layout
- `drawings/`    — FreeCAD models, drawings, vendor STEP files
- `calc/`        — sizing calcs & comparisons (axis-sizing.md, etc.)
- `docs/`        — specs, decisions log, math-derivation.md
- `reference/`   — vendor datasheets, torque curves
- `spreadsheet/` — project tracking spreadsheet

## Core spec (draft)
- X + Y: HG20 linear rails, 2 rails × 2 blocks per axis
- Drive: ballscrew vs rack & pinion (decision in progress → calc/axis-sizing.md)
- Motors: StepperOnline closed-loop NEMA 24 (4 Nm) under evaluation
- Speed: 15 m/min travel (plasma cut speed)
- Bonus: light machining/drilling of soft metals (brass, alu) on X
- Adjustable table height

## Math (manual-checkable)
Full step-by-step derivations: `docs/math-derivation.md`. Core numbers here:

**X/Y feed force** (Kc = 2500 N/mm² mild steel, brass 1500; feed ≈ 0.4 × tangential;
chip area A = fz·ap·e):
```
Ff = 0.4 × Kc × fz × ap × e
engraving:  0.4 × 2500 × 0.03 × 1.0 × 0.7  ≈ 21 N
light mill: 0.4 × 2500 × 0.05 × 3.0 × 0.7  ≈ 105 N
slotting:   0.4 × 2500 × 0.05 × 3.0 × 0.9  ≈ 135 N   ← X/Y envelope ≈ 20–150 N
```

**Drive capability** (4 Nm NEMA 24):
```
ballscrew:  F = 2πηT/L   →  150 N @ 20 mm lead needs T = 0.53 Nm (13 % of 4)
rack:       F = T/(m·z/2) →  m1 z12: 150 N needs 0.90 Nm (22 %); 15 m/min @ 398 rpm
speed cap:  encoder 60 kHz / 4000 CPR = 900 rpm hard ceiling
```
Both drives clear every corner with ≥1.5× margin → **decision is precision
(ballscrew) vs simplicity/cost (rack), not capability.** 2000 N is Z-only.

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
- 2026-10-21: Sizing v3 (two-regime). User confirmed: 15 m/min needed **only for
  plasma** (≈35 N, no push); cutting/embossing runs **very slow** and needs force
  (20–150 N, derived from Kc=2500 N/mm² × chip area). Both regimes validated:
  ballscrew 20 mm lead AND rack m1 z12 clear every corner ≥1.5× (typical ≥4×).
  **Capability is not the decider** — decision is precision/backlash (ballscrew)
  vs simplicity/cost/full-length X (rack). 2000 N remains Z-only. Full manual
  math in docs/math-derivation.md + README math section.
