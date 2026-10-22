# Plasma table — project

Plasma cutting table for Uitvindersgilde (Hof van Cartesius, Utrecht).
Design phase, started 2026-10-20. Customer spec sheet: `Plasma Table Constraints.ods` (2026-10-21).

## Layout
- `drawings/`    — FreeCAD models, drawings, vendor STEP files
- `calc/`        — sizing calcs & comparisons (axis-sizing.md, z-axis-spindle.md)
- `docs/`        — specs, decisions log, math-derivation.md
- `reference/`   — vendor datasheets, torque curves
- `spreadsheet/` — `constraints.xlsx` (customer + project constraints, live formulas)

## Customer spec (from the ODS, 2026-10-21)
| Item | Value |
|---|---|
| **Torch (customer buys)** | Hypertherm **Powermax 65** with CPC port |
| **Software** | LinuxCNC **Qtplasmac** + **SheetCAM** (nesting/material settings), local at the machine |
| **Motion controller** | Mesa **7i76e** (Ethernet FPGA motion, LinuxCNC) |
| **THC** | Mesa **THCAD-5** (ohmic sensing, initial touch-off) + **THCAD-10** (voltage sensing, real-time THC) |
| **Min sheet to cut** | **1000 × 2000 mm** ("bigger is better") |
| **Outer max dimensions** | **X 1600 × Y 2500** (customer envelope) |
| **Material on hand** | 1700 mm |
| **Z drilling** | small holes + spot drilling, 6 mm max into steel (2000 N feed) |
| **EMI** | high — plasma generates lots of electrical noise (design must tolerate) |

**Desired features (customer):** plasma + THC + water table · break-away (part collision) ·
scribing tool (pneumatic/electric) · drilling + spot drilling · high/adjustable Z (curved
surfaces) · 1000×2000 min sheets · light milling ("ballscrew vs belts" — customer's own
suggestion) · **4th axis for tube plasma** · more (e.g. gear tooth cutter).

## Core spec (draft)
- X + Y: HG20 linear rails, 2 rails × 2 blocks per axis
- Drive: **rack & pinion (long axis, 15 m/min) vs ballscrew (precision)** — `calc/axis-sizing.md`
- Motors: StepperOnline closed-loop NEMA 24 (4 Nm) under evaluation
- Z: linear bearings + self-locking lead screw + thrust bearing + brushless spindle (Flipsky) — `calc/z-axis-spindle.md`
- Adjustable table height

## Math (manual-checkable)
Full step-by-step derivations: `docs/math-derivation.md`. Core numbers here.

**X/Y feed force** (Kc = 2500 N/mm² mild steel, brass 1500; feed ≈ 0.4 × tangential;
chip area A = fz·ap·e):
```
Ff = 0.4 × Kc × fz × ap × e
engraving:  0.4 × 2500 × 0.03 × 1.0 × 0.7  ≈ 21 N
light mill: 0.4 × 2500 × 0.05 × 3.0 × 0.7  ≈ 105 N
slotting:   0.4 × 2500 × 0.05 × 3.0 × 0.9  ≈ 135 N   ← X/Y envelope ≈ 20–150 N
```
Force is tiny vs a 4 Nm motor — **force is never the decider.**

**The real constraint is the LONG-AXIS ballscrew critical speed** (customer outer max
X1600×Y2500 → ~2500 mm travel → ~2800 mm screw span):
```
Nc = K × D / L² × 1e7   rpm        (K end-support: fixed-supp 15.1, fixed-fixed 21.9)
L = 2800 mm, D = 25 mm, K = 15.1  →  Nc ≈ 482 rpm
20 mm lead @ 15 m/min needs 750 rpm  →  750 / 482 = 1.56×  CRITICAL  →  FAILS the 50% rule
```
So at the customer's real span a ballscrew **cannot** safely do 15 m/min plasma unless you
go large-diameter, add a mid-span bearing, or accept slower rapids. **A rack & pinion has no
critical-speed limit** — for the long X axis at plasma speed the rack is the safer choice.
Ballscrew wins where precision/low-backlash matters (short axis, engraving/brass).

> **Live version:** `spreadsheet/constraints.xlsx` — every force/speed/margin is a live formula.
> Edit the YELLOW inputs (K, D, lead, span, Kc…) and all verdicts recompute. It now reflects
> the customer ODS (Powermax 65, 1000×2000 min / 1600×2500 outer / 1700 on hand) and flags
> the long-axis critical-speed FAIL on every ballscrew lead.

## Water table + table height (2026-10-21)
Water table for kerf cooling (prevents warping) and arc damping, with **fill pump + drain**,
and a **raise/lower table** for access:
- **Guides:** telescoping square tube — smaller tube inside the main column, bearings guide it
- **Lift:** pulley + steel cable + **counterweight** (assist, not full lift); raise/lower is
  designed to work with the table **full of water**
- **Pins** fix the table at set positions (cable can slack off — no power/brake needed at rest)
- **Safety stop:** counterweight < 0.9 × EMPTY table weight → a drained table can **never**
  self-lift into the workpiece/torch (passive protection, no electronics)
- **Axes:** X/Y are fixed to the table — the whole table moves; the plasma head keeps its
  own **large Z travel**

**Live calcs** in `spreadsheet/constraints.xlsx` → **Water-Table** sheet (all yellow inputs
on the Inputs sheet). With defaults (1700×1700×100 mm water ≈ 289 kg, 250 kg structure):
| Check | Value | Verdict |
|---|---|---|
| Full lifting load | ≈ 530 kg | — |
| Max counterweight (safety) | 225 kg (< empty 250 kg) | **PASS** no self-lift |
| Manual force, full table (4:1 MA) | ≈ 78 kg equiv | **PASS** ≤ 100 kg |
| Cable SF (6 mm, 24 kN) | ≈ 18× | **PASS** ≥ 10 |
| Pin SF (2 × M12) | ≈ 9.5× | **PASS** ≥ 5 |
| Fill time (50 L/min pump) | ≈ 6 min | — |
| Drain | gravity + sump | — |

## Reference files acquired — in `drawings/`
- `24HS40-5004D-E1000.STEP` (8 MB motor model), `_Full_Datasheet.pdf`, `_Torque_Curve.pdf` (OMC)
- `hiwin_Linear_Guideway_E1_catalog.pdf` (17.6 MB, HG series), `hiwin_HG_series_catalog.pdf`
- HGR20/HGH20 STEP models: not downloaded (all CAD portals need login) — model from catalog dims

## Decisions log
- 2026-10-20: v1 sizing. 24HS40 NEMA 24, encoder caps 900 rpm.
- 2026-10-20: **v2 correction.** Cut force is ~38 N (not 2000 N) → X/Y torque trivial. Real
  constraint = speed vs lead. 2000 N reclassified as **Z drilling feed** (downward), not X/Y.
- 2026-10-20: **Z axis** = drilling/feed axis. 2× HG20 + **2.5 mm self-locking lead screw** +
  **thrust bearing 51217** (96 kN, 2% utilisation) + Flipsky brushless spindle, ~1300 rpm,
  ~1–2.5 Nm, 6 mm max hole. Tool changer (plasma+drill) shares one Z. `calc/z-axis-spindle.md`.
- 2026-10-21: **v3 two-regime.** 15 m/min needed **only for plasma** (~35 N, no push);
  cutting/embossing runs **very slow** and needs force (20–150 N). Both drives pass force/torque
  ≥1.5× → capability is not the decider; it's precision (ballscrew) vs simplicity (rack).
  Full math in `docs/math-derivation.md`.
- 2026-10-21: **Customer ODS ingested** (`Plasma Table Constraints.ods`). Torch is **Powermax 65**
  (customer supplies), control = **LinuxCNC Qtplasmac + SheetCAM + Mesa 7i76e + THCAD-5/10**.
  Envelope is **1000×2000 min / X1600×Y2500 outer** (the chat's "1700×1700" was material on hand,
  not the envelope). **Key correction:** at the real ~2500 mm long axis, the ballscrew
  **critical speed is the binding constraint** for 15 m/min plasma (750 rpm needed vs ~482 rpm
  critical, D25/fixed-supported) → **rack preferred for the long axis**, ballscrew for the
  precision/short axis. Constraints spreadsheet now reflects all ODS numbers + this finding.
- 2026-10-21: **Water table + height lift.** Water table (cooling/anti-warp, fill pump + drain);
  table raise/lower via telescoping square-tube guides + pulley/cable/counterweight, pin-fixed
  at set heights; passive safety (CW < 0.9 × empty weight) so a drained bed can't slam into the
  torch. X/Y fixed to table; plasma head keeps its own large Z. `constraints.xlsx` → Water-Table
  sheet (all checks PASS with defaults: ~78 kg manual lift, cable SF 18×, pin SF 9.5×).
  **Accepted tradeoff:** table is DRAINED before raising (safer — light table, easy lift;
  full table only lowers, CW-assisted).
- 2026-10-21: **Context: one-off job shop, NOT a production machine.** Table height/position
  adjustments are done manually for fixturing per process — no need for powered/automatic
  positioning. **Tool changing is MANUAL for now** (plasma ↔ drill ↔ scribe ↔ mill),
  may be automated later — design the Z head/tool interface so a manual change is quick
  and repeatable, but don't build an ATC yet.
