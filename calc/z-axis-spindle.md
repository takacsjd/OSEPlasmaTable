# Z axis (drilling) + spindle — design (v1)

Project: `C:\Users\Core\Documents\plasma-table`
Date: 2026-10-20

## Role
Z is the **drilling/feed axis**. It must carry **2000 N downward** (design margin;
real 6 mm HSS feed force is ~300–600 N) for one-off holes up to **6 mm in steel**,
plus embossing/marking and brass gear cutting. Speed is not important — precision,
stiffness and holding torque are.

## Architecture (as decided)
```
[stationary]  Z lead screw (motor + bearing at frame, not on the moving part)
                |
                v
[moving]      Z carriage: 2x HG20 rail blocks (per rail)
                |
                v
              Drill spindle assembly:
                 - drill chuck / 6mm tool
                 - drill shaft (close to X axis line = minimum overhang)
                 - THUST bearing (51215/51217) on the shaft
                 - Flipsky brushless motor OFF the axis, belt-driven
```

**The "off-axis motor + belt" idea is exactly right** — it's the standard
solution and it gives you the light, rigid spindle the drilling wants.
The motor (Flipsky outrunner, ~1 kg) stays on the frame; only the nut +
bearing + shaft move with Z. This is the "meander chain / off-axis" benefit.

## Bearing — the "cone + cylinder" one
That's a **single-row thrust ball bearing** (lathe-spindle type):
- one **ring with balls** (the "cone" look) + one **flat washer** (the "cylinder")
- carries **axial load only**, one direction.

| code | bore×OD×h | C (dyn) | C0 (static) |
|------|-----------|---------|-------------|
| 51215 | 75 × 120 × 29 | 63.7 kN | 112 kN |
| 51217 | 85 × 130 × 33 | 96.0 kN | 264 kN |

2000 N on a 51217 = **2.1% utilisation**. Even the 51215 has 30× static margin.
Pick **51217** (or 51215) on the drill shaft. This is what a lathe spindle
uses for exactly this job — axial feed force.

> Note: a single-row thrust bearing takes the **feed force**. It does NOT take
> radial/overhang loads. That's why the drill shaft must stay **close to the
> Z axis line** (minimal overhang) — the radial load then is small and taken
> by a second small radial bearing or by the HGH20 carriage.

## Z lead screw sizing
Lead screw (self-locking, low efficiency η≈0.2–0.3). Torque for 2000 N:

| lead | T @η=0.3 | 4 Nm NEMA24 pushes | verdict |
|------|----------|--------------------|---------|
| 2.5 mm | 2.7 Nm | 3000 N | ✓ works with 4 Nm NEMA24 |
| 5 mm | 5.3 Nm | 1500 N | ✗ needs NEMA34 |
| 8 mm | 8.5 Nm | 940 N | ✗ |
| 10 mm | 10.6 Nm | 754 N | ✗ |

**Z: use a 2.5 mm lead screw** (or 5 mm + NEMA 34 motor). Self-locking means
the drill **holds position when the motor is off** — critical so the tool
doesn't drop onto the workpiece. This is the opposite of X/Y (where you want
high lead for speed); Z wants **low lead + self-locking** for holding force.

## Drill spindle
- **Speed**: 6 mm HSS in mild steel wants ~1300 rpm (Vc≈25 m/min).
  `n = Vc·1000/(π·D) = 25·1000/(π·6) ≈ 1326 rpm`.
- **Torque at tool**: ~1–2.5 Nm. **Power**: ~150–300 W. Modest.
- **Flipsky outrunner** (e.g. 7070 110–150 KV, ~9.5 Nm max, ~4000 W, ~1 kg):
  - 150 KV @ 48 V ≈ 7200 rpm no-load → **5× headroom** over 1300 rpm needed.
  - With a **2:1 belt reduction** → ~3600 rpm spindle, ~15–19 Nm. Massive margin.
  - Even 1:1 is overkill. The belt also lets you **mount the motor off-axis**
    (the whole point) and keep the spindle light.
- **Driver**: a 48 V brushless ESC (e.g. 100 A class, or 40–60 A for this load)
  + an RPM/tach signal for the CNC if you want closed-loop speed.

## Drilling torque/power summary (6 mm HSS, mild steel)
| | value |
|---|---|
| spindle speed | ~1300 rpm |
| tool torque | ~1–2.5 Nm |
| tool power | ~150–300 W |
| feed force (real) | ~300–600 N |
| feed force (design) | **2000 N** (margin) |
| Z screw | 2.5 mm lead, self-locking, NEMA24 4 Nm (or 5 mm + NEMA34) |
| thrust bearing | 51217 (96 kN C) — 2.1% utilisation |

## Tool changer (open option)
If you add a tool changer (plasma on one side, drill on the other):
- The **Z axis + thrust bearing + spindle** become the common moving head.
- Tool changer = a rotary index (2 positions) or a swap on the Z carriage.
- Keep the **drill shaft on the Z axis line** so the thrust bearing and
  lead screw stay aligned regardless of which tool is active.
- This is the cleanest way to share one Z axis between plasma and drill.

## Open
- Confirm Z stroke (drill travel).
- Drill chuck type (6 mm max → a 6–10 mm keyed or ER11 collet).
- Is the Flipsky sensored or sensorless? (Sensored = better low-speed torque
  for drilling; 150 KV sensorless is fine at 1300 rpm.)
- Z motor: 2.5 mm lead + NEMA24, or 5 mm + NEMA34? (2.5 mm keeps it NEMA24.)

## Reference
- 51215/51217: SKF / NSK catalogs (C, C0 above)
- Flipsky 7070: ~9.5 Nm max, ~4200 W (foil.zone / Flipsky datasheet)
- HGH20: hiwin.com HG-Info.pdf
