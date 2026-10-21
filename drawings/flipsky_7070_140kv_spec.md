# Flipsky 7070 (140KV) — Z-axis spindle motor
Project: `C:\Users\Core\Documents\plasma-table`
Captured: 2026-10-21

## Why this motor (Z / drill spindle)
Off-axis outrunner, belt-driven → keeps the Z spindle light and rigid.
Requirement (from `calc/z-axis-spindle.md`): ~1300 rpm, ~1–2.5 Nm, 150–300 W.
A 7070 is **massively oversized** for this — that's good (speed headroom,
torque margin, cheap, proven, sensored option available).

## KV variants (same 7070 platform)
| KV  | no-load @ 48 V | no-load @ 72 V | note |
|-----|----------------|----------------|------|
| 110 | ~7200 rpm      | ~10800 rpm     | most torque/amp, common |
| 140 | ~6700 rpm      | ~10000 rpm     | **chosen** — user asked for 140KV |
| 170 | ~8100 rpm      | ~12200 rpm     | fastest, least torque/amp |

KV only changes back-EMF (Kv) and torque constant (Kt ≈ 60/Kv Nm/A).
Higher KV = more rpm per volt, less torque per amp. For a low-speed drill
spindle **110KV would give slightly more torque headroom than 140KV** — 140KV
is fine (still ~5× the rpm we need), 110KV is a reasonable alternative if you
want max low-speed torque.

## Electrical specs (7070 platform, all KV variants)
| parameter            | value         |
|----------------------|---------------|
| Max power            | 4200 W (peak) |
| Max current          | 100 A         |
| Voltage range        | 6–18 S (≈ 75 V peak) |
| Max torque (quoted)  | 9.5 Nm        |
| Weight               | 1.08 kg       |
| Winding resistance   | 0.055 Ω       |
| Magnets/poles        | 12 N / 14 P   |
| Sensor               | sensored option available (good for low-speed drilling) |
| Shaft                | 10 mm, D or round |
| Keyway               | 3 × 3 mm      |

## Dimensions (from vendor drawing — `flipsky_7070_drawing.webp`)
| feature            | value         |
|--------------------|---------------|
| Body OD            | ⌀70 ±0.1 mm   |
| Body length        | 70 ±0.8 mm    |
| Rear (mounting) face OD | ⌀55 ±0.1 mm |
| Mounting holes     | 4 × M4        |
| Bolt circle        | ⌀44 ±0.05 mm  |
| Shaft collar width | 10 mm         |
| Exposed shaft      | 20 mm         |
| Rear face → shaft tip | 30 mm      |

> Note: "7070" = ⌀70 × 70 mm — matches body OD and length above.
> Drawing read via vision; bolt-circle/Ø44 and 4×M4 confirmed from vendor +
> forum. If you model the motor in FreeCAD, ⌀70 / 70 L / ⌀44 BCD / 4×M4 /
> ⌀10 shaft / 3×3 key are the numbers that matter for a mount + belt pulley.

## Driver
- 48 V (or 12–18 S) sensored BLDC ESC, 40–60 A class is plenty for this load
  (100 A class if you want headroom / regen).
- For CNC speed control: use an RPM/tach signal (sensored) or close the loop
  on encoder feedback.

## Sources
- Drawing: technobotix.in product 1781252000001602386 (7070 D-shaft drawing)
- Specs: Technobotix, AliExpress 1005009363152184, foil.zone, esk8.news
- 140/170KV availability: Technobotix (KV selector 110/140/170), foil.zone, Facebook/Flipsky

## Files in this folder
- `flipsky_7070_drawing.webp` — vendor dimensioned drawing (front + side views)
- `flipsky_7070_spec.md` — this file
