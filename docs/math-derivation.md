# Math used — manual cross-check page

Companion to `calc/axis-sizing.md` (v3) and `README.md`. Every number on the
main / constraints pages, derived step by step so you can re-run it on a
calculator. All SI (N, mm, m, min), each step shown.

---

## 1. X/Y feed force for cutting / engraving / slotting

### 1.1 Source data (assumptions, listed)
| Symbol | Value | Source |
|--------|-------|--------|
| Kc (steel, mild) | 2500 N/mm² | Sumitomo N-P info: "general steel 2500–3000 N/mm²" (lower bound used) |
| Kc (brass) | 1500 N/mm² | Same table (cast iron 1500; brass in 1000–1500 band) |
| Kc (aluminium) | 800 N/mm² | Same table |
| Feed/tangential ratio | 0.4 | Rake-angle dependent, 0.3–0.5 for steel; 0.4 used |
| ap | 3.0 mm | Your 3 mm depth-of-cut |
| fz (steel, 2-flute) | 0.03–0.05 mm/tooth | Haas engraving-mill data: 0.0004–0.0006 in ≈ 0.01–0.015 mm for engraving; 0.03–0.05 for light milling |
| e (engagement) | 0.7 profile / 0.9 slot | Profile milling ~50–70 % of tool in contact; slotting full width |

### 1.2 Formulas
```
A  = fz · ap · e        (mm²)  uncut chip area
Ft = Kc · A             (N)    tangential force at tool
Ff = 0.4 · Ft           (N)    feed force = X/Y axis demand
```

### 1.3 Worked rows (re-run these)
**Engraving, 3 mm tool, fz = 0.03, ap = 1.0 mm (engraving is ~1 mm deep), e = 0.7:**
```
A  = 0.03 × 1.0 × 0.7 = 0.021 mm²
Ft = 2500 × 0.021     = 52.5 N
Ff = 0.4 × 52.5       = 21 N
```
**Light mill, 6 mm 2-flute, fz = 0.05, ap = 3.0, e = 0.7:**
```
A  = 0.05 × 3.0 × 0.7 = 0.105 mm²
Ft = 2500 × 0.105     = 262.5 N
Ff = 0.4 × 262.5      = 105 N
```
**Slotting, 10 mm 2-flute, fz = 0.05, ap = 3.0, e = 0.9:**
```
A  = 0.05 × 3.0 × 0.9 = 0.135 mm²
Ft = 2500 × 0.135     = 337.5 N
Ff = 0.4 × 337.5      = 135 N
```
**Brass gear, 6 mm 2-flute, fz = 0.05, ap = 3.0, e = 0.7, Kc = 1500:**
```
A  = 0.05 × 3.0 × 0.7 = 0.105 mm²
Ft = 1500 × 0.105     = 157.5 N
Ff = 0.4 × 157.5      = 63 N
```
**Envelope: ~20 N (engrave) … ~150 N (worst slotting).**

> Note: these are *average* forces. Instantaneous peaks are ~2–3× higher but
> last milliseconds; the drive is validated with 2×+ margin so peaks are covered.

---

## 2. Drive force & speed formulas

### 2.1 Ballscrew
```
F = 2π · η · T / L          (N)   η = 0.9 efficiency, T in N·m, L in m
T = F · L / (2π · η)        (N·m)
v = L · rpm                 (mm/min)
```
**Cutting corner check (150 N, 20 mm lead):**
```
T = 150 × 0.020 / (2 × 3.1416 × 0.9) = 3.0 / 5.655 = 0.53 N·m   (13 % of 4 N·m)
```
**Plasma corner check (15 m/min = 15000 mm/min, 20 mm lead):**
```
rpm = 15000 / 20 = 750 rpm
F available ≈ 2π × 0.9 × 1.0 / 0.020 = 283 N   (torque at 750 rpm ≈ 1 N·m from curve)
```

### 2.2 Rack & pinion
```
pitch radius   r = (m · z) / 2            (m = module mm, z = teeth)
F = T / r        (N)
v = π · m · z · rpm    (mm/min)           (pitch circumference = π·d = π·m·z)
```
**Rack m1 z12 (r = 6 mm = 0.006 m):**
```
15 m/min: rpm = 15000 / (π × 1 × 12) = 15000 / 37.7 = 398 rpm
150 N:    T   = 150 × 0.006 = 0.90 N·m      (22 % of 4 N·m)
```
**Rack m1.5 z16 (r = 12 mm):**
```
rpm = 15000 / (π × 1.5 × 16) = 199 rpm
T   = 150 × 0.012 = 1.80 N·m      (45 %)
```
**Rack m2 z14 (r = 14 mm):**
```
rpm = 15000 / (π × 2 × 14) = 171 rpm
T   = 150 × 0.014 = 2.10 N·m      (52 %)
```

---

## 3. Motor speed ceiling (encoder)
```
f_max = 60000 Hz (encoder/driver)
CPR   = 1000 PPR × 4 quadrants = 4000 counts/rev
rpm_max = 60000 / 4000 × 60 = 15 × 60 = 900 rpm   ← hard limit for any screw/rack
```

---

## 4. Rail load check (HG20)
```
HGH20CA static rating per block: Co = 36.68 kN
X/Y demand ≤ 150 N
2 blocks per axis:  2 × 36680 N static vs 150 N  →  utilisation = 150/73360 ≈ 0.2 %
```
Rails are ~500× the force they will ever see. Not a design driver.

---

## 5. Z axis / drilling (separate doc, math summary)
Full: `calc/z-axis-spindle.md`.
```
Feed force design: 2000 N (your value)
Self-locking lead screw 2.5 mm, d=16 mm, η≈0.45 (trapezoid):
   F = 2π·η·T/L = 2π × 0.45 × 4.0 / 0.0025 = 4523 N  → 2.3× margin on 2000 N
   (self-locking: holds position with power off — critical for drilling)
Thrust bearing: 51217, C = 96.4 kN axial → 2000/96400 ≈ 2 % utilisation
Drill torque 6 mm HSS in mild steel @ 1300 rpm: ≈ 1–2.5 N·m → Flipsky 140KV
   at 48 V: 2400 rpm, ~3–5 N·m continuous → OK with 1:1 or 1.5:1 belt
```

---

## 6. Cross-check list (what to re-run yourself)
1. Rows in §1.3 — each is 3 multiplications.
2. §2.1 ballscrew T for 150 N — one division.
3. §2.2 rack T and rpm for m1 z12 — one division each.
4. §3 encoder rpm ceiling.
5. If any number disagrees with your shop experience, **adjust the listed
   assumption** (Kc, fz, e, or the 0.4 feed ratio) rather than the formulas —
   the formulas are exact geometry; the assumptions carry the uncertainty.
