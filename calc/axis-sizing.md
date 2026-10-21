# Plasma table — axis drive sizing (v2, corrected)

Working dir: `C:\Users\Core\Documents\plasma-table`
Updated: 2026-10-20

## Given (confirmed)
- Torch: Hypertherm 45 (45 A)
- Cut force: **~38 N** at 3 mm steel, 5 m/min, ~10° kerf angle
  (brass/alu: similar or lower — aluminium cuts faster)
- Speed targets: **cut** 5 m/min (3 mm steel); **rapid / thin steel** up to 15 m/min
- Guides: HG20 rails, 2 rails × 2 blocks per axis
  - HGH20CA: C = 27.1 kN, Co = 36.68 kN/block, 0.20 kg/block, 2.21 kg/m rail
- Motor under evaluation: **24HS40-5004D** NEMA 24, 4.0 Nm holding, 5 A,
  1000 PPR encoder = **4000 CPR**, encoder max **60 kHz**
  → hard speed ceiling: 60 000 / 4000 = **15 rev/s = 900 rpm**
- Carriage (guess): ~10–12 kg per axis

## What "lead" / "leadway" / "spindel" means
- **Ballscrew lead** = linear travel of the nut per full revolution of the screw.
  5 mm lead → 1 rev = 5 mm. 20 mm lead → 1 rev = 20 mm.
- **Spindel** (Dutch) = the ballscrew itself. "Spindel met 5 mm lead" = a 5 mm lead screw.
- Lead is the **only** knob that sets max speed for a given motor rpm:
  `v_max = lead × rpm`. This is the whole trade.
  - Short lead (5 mm): stiff, precise, low backlash, great for drilling — but slow.
  - Long lead (20–25 mm): fast — but the screw is more flexible, less precise.

## Constraint 1 — speed vs lead (THE binding one, NOT torque)
`v = lead × rpm`; the 24HS40 is practical to ~1200 rpm, hard-capped at 900 rpm (encoder).

| lead | max speed @1200 rpm | max speed @900 rpm | reaches 15 m/min? |
|------|---------------------|--------------------|-------------------|
| 5 mm | 6.0 m/min | 4.5 m/min | ✗ (colleague's 6 m/min) |
| 10 mm| 12.0 m/min| 9.0 m/min | ✗ |
| 16 mm| 19.2 m/min| 14.4 m/min| ~marginal |
| 20 mm| 24.0 m/min| 18.0 m/min| ✓ |
| 25 mm| 30.0 m/min| 22.5 m/min| ✓ |

**Minimum lead to hit 15 m/min within the 900 rpm ceiling: 12.5 mm → use 20 mm.**
Your colleague's 5 mm lead is exactly 6 m/min at 1200 rpm — consistent. It
**cannot** reach 15 m/min no matter how much torque you have. Speed limit, not strength.

## Constraint 2 — torque (trivial at 38 N)
`T = F·lead / (2π·η)`, η = 0.9. At 38 N the required torque is a rounding error:

| lead | T @38 N | T @350 N (if it were that much) |
|------|---------|-------------------------------|
| 5 mm | 0.03 Nm | 0.31 Nm |
| 20 mm| 0.13 Nm | 1.24 Nm |
| 25 mm| 0.17 Nm | 1.55 Nm |

Even at 10× the force a 4 Nm NEMA 24 is still fine for cutting. **Torque is not the driver.**

## Constraint 3 — corner deceleration (fine)
`F_carriage = T·2π·η / lead`; `a = F / m`

| lead | F @4 Nm | a (m/s²) on 12 kg | stop dist from 250 mm/s (15 m/min) |
|------|---------|-------------------|------------------------------------|
| 5 mm | 254 N | 21.2 m/s² | 1.5 mm |
| 20 mm| 636 N | 53.0 m/s² | 0.6 mm |
| 25 mm| 795 N | 66.3 m/s² | 0.5 mm |

Stops from 15 m/min in well under 2 mm. **Corner decel is a non-issue** with this
motor/carriage mass. The real cornering risk is the **CNC controller's** planner
limit (accel/decel in G-code), not the hardware.

## Verdict
1. **Speed sets the lead: use ≥20 mm lead** (20 or 25 mm). A 5 mm screw, whatever
   the motor, physically cannot do 15 m/min. If the table is primarily a 5 m/min
   cutting rig (Hypertherm 45 typical), 5 mm is acceptable and keeps
   stiffness/precision for the drilling role.
2. **Torque and cornering are NOT constraints** at 38 N with a 4 Nm NEMA 24.
3. **For both fast cutting AND precise drilling on one X axis**, 20 mm lead is
   the compromise: 0.020 mm/rev is still very good resolution, and a closed-loop
   encoder removes the step-loss worry.
4. **Rack & pinion is not needed and is worse here**: at 38 N the pinion torque is
   trivial, but you lose the rigidity/repeatability a ballscrew gives for drilling,
   and a rack is harder to keep clean against plasma dross/spatter.

## Recommendation
- **X axis (cutting + drilling): ballscrew, 20 mm lead**, 4 Nm closed-loop NEMA 24
  (or NEMA 34 if the spindle/carriage gets heavier later). Single motor at one end,
  screw supported at the other — this already keeps the moving carriage light
  (nut only), which is the "meander chain / off-axis motor" benefit you wanted.
- **Y axis: same 20 mm lead ballscrew**, or rack if Y is pure rapid (no drilling).
- **Z axis (torch): short-lead (5 mm) ballscrew** or lead screw — precision and
  stiffness matter, speed doesn't.
- **Keep a 5 mm lead screw available** if the table becomes precision/drilling-first
  rather than a fast cutter — it's the right tool for that.

## Open
- Confirm carriage mass (barely affects accel).
- Stroke lengths (X, Y) → screw length; a 20–25 mm lead screw > ~800 mm
  unsupported needs a mid-support bearing.
- Torch height control (Z) method — separate from the X/Y drive decision.

## Reference
- Motor: `reference/24HS40-5004D-E1000_Torque_Curve.svg`
- HGH20 data: Hiwin HG series catalog (hiwin.com HG-Info.pdf)
