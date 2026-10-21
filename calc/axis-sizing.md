# Plasma table — X/Y drive sizing (v3, two-regime)

Working dir: `C:\Users\Core\Documents\plasma-table`
Updated: 2026-10-21

## Given (confirmed)
- Torch: Hypertherm 45 (45 A) — plasma travel **15 m/min** (rapid + thin-steel cut)
- Machining use: **light engraving / embossing / brass gears / tooth-cutting,
  ≤3 mm depth of cut, can run very slow** (one-off guild projects)
- **2000 N is the Z drilling feed force — it never loads X/Y** (see
  `calc/z-axis-spindle.md`)
- Guides: HG20 rails, 2 rails × 2 blocks per axis
  - HGH20CA: C = 27.1 kN, Co = 36.68 kN/block, 0.20 kg/block, 2.21 kg/m rail
- Motor: **24HS40-5004D** NEMA 24, 4.0 Nm holding, 1000 PPR encoder (4000 CPR),
  encoder max 60 kHz → hard ceiling **900 rpm**
- Carriage (guess): ~10–12 kg per axis

## Key reframe: two regimes, never simultaneous
- **Plasma:** needs **speed** (15 m/min), needs **~35 N** (torch doesn't push;
  only carriage friction) — the drive runs fast, nearly unloaded.
- **Cutting/embossing:** needs **force** (20–150 N, derived below), at
  **very low speed** — exactly where a stepper is at *peak* torque.
- So validate each drive at *its* worst corner (fast+light, slow+heavy).
  If both corners pass, the decision is precision vs simplicity — not capability.

## X/Y feed force — derivation (manual-checkable)
Basis: Sumitomo specific cutting pressure (N/mm²): **mild steel Kc ≈ 2500–3000**,
**brass ≈ 1500**, aluminium ≈ 800. Feed force ≈ 0.3–0.5 of tangential
(rake-angle ratio; 0.4 used). Uncut chip area `A = fz·ap·e`, e = engagement
factor (profile milling ≈ 0.5–0.7, slotting ≈ 0.9).

```
A  = fz · ap · e          (mm²)   uncut chip area
Ft = Kc · A               (N)     tangential (spindle) force
Ff = 0.4 · Ft             (N)     feed force  = X/Y drive demand
```

| Case | d | ap | fz | e | A = fz·ap·e | Ft = 2500·A | **Ff = 0.4·Ft** |
|------|---|----|----|---|-------------|-------------|-----------------|
| Engraving (3 mm tool) | 3 | 1.0 | 0.03 | 0.7 | 0.021 mm² | 53 N | **≈ 21 N** |
| Light mill (6 mm 2-fl) | 6 | 3.0 | 0.05 | 0.7 | 0.105 mm² | 263 N | **≈ 105 N** |
| Slotting (10 mm 2-fl) | 10 | 3.0 | 0.05 | 0.9 | 0.135 mm² | 338 N | **≈ 135 N** |
| Brass gear (6 mm 2-fl) | 6 | 3.0 | 0.05 | 0.7 | 0.105 mm² | 158 N (Kc 1500) | **≈ 63 N** |

**X/Y force envelope: ~20 N (engrave) → ~150 N (worst slotting).**

## Drive capability vs that envelope (4 Nm NEMA 24)
**Ballscrew:** `F = 2π·η·T / L`  (η = 0.9)
**Rack & pinion:** pitch radius `r = m·z/2` → `F = T / r = 2T / (m·z)`
**Speeds:** ballscrew `v = L·rpm`; rack `v = π·m·z·rpm` (mm/min)

| Drive | Plasma corner: 15 m/min, ~35 N needed | Cutting corner: 150 N, ≤500 mm/min |
|-------|----------------------------------------|-------------------------------------|
| BS 20 mm lead | 750 rpm; T≈1.0 Nm → **283 N** (8×) | **0.53 Nm** needed (13 % of 4 Nm) |
| Rack m1 z12 (38 mm/rev) | 398 rpm; ~2 Nm → **333 N** (9×) | **0.90 Nm** (22 % of 4 Nm) |
| Rack m1.5 z16 (75 mm/rev) | 200 rpm; ~3 Nm → **233 N** (7×) | **1.80 Nm** (45 %) |
| Rack m2 z14 (88 mm/rev) | 171 rpm; ~3.5 Nm → **200 N** (6×) | **2.10 Nm** (52 %) |

All corners pass with **≥1.5× margin** (typical ≥4×). **Capability is NOT the
decider.** HG20 rails: 2 blocks ≈ 73 kN static vs ≤150 N demand — ~1 % use.

## What actually decides rack vs ballscrew (for this guild)
- **Precision / backlash:** ballscrew wins by a lot (near-zero backlash vs
  ~0.05–0.1 mm rack). This is the value in *engraving, embossing, brass gears*.
- **Simplicity / cost / full-length X:** rack wins — motor+pinion ride the
  carriage, no long screw, no mid-support bearing past ~800 mm, and an enclosed
  pinion stays clean against dross/spatter.
- **15 m/min plasma:** both achieve it (table above).
- If ballscrew: **≥20 mm lead** to reach 15 m/min within the 900 rpm ceiling
  (a 5 mm lead tops out at 4.5 m/min — fine for the guild, but no 15 m/min).
- If rack: **module 1, 12–16 teeth** (38–75 mm/rev) → 15 m/min at 200–400 rpm,
  inside the motor's flat-torque band.

## Verdict (v3)
1. X/Y force demand is **20–150 N** (derived above); **both drives pass both
   regimes with margin** — the 2000 N drilling load is carried by Z only.
2. The real trade is **precision (ballscrew) vs simplicity/cost/full-length
   (rack)** for a light-use guild table.
3. Recommendation: **rack & pinion (m1, 12–16 T) is adequate and simpler**;
   **ballscrew 20 mm lead if engraving precision is the priority**.
   Either way: 4 Nm NEMA 24, HG20 rails, light carriage.
4. Z drilling axis: `calc/z-axis-spindle.md` (2000 N feed, self-locking
   2.5 mm lead screw, 51217 thrust bearing, off-axis Flipsky + belt).

## Open
- **X/Y stroke lengths (mm)** → screw length / rack length / mid-support needs.
- Decision: rack vs ballscrew (see trade table).
- Torch height control (Z) — see z-axis-spindle.md.

## Reference
- Motor: `drawings/24HS40-5004D-E1000_Torque_Curve.svg`
- Kc values: Sumitomo N-P technical info (steel 2500–3000 N/mm², brass ~1500)
- HGH20 data: Hiwin HG series catalog (drawings/)
