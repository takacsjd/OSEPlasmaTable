# Gantry Motor & Gear Sourcing + Selection  (v1, 2026-11-02)

Scope: X single-driven, Y dual-driven (both sides), rack & pinion, HG50 guides,
motor + pinion + carriage captive against a **static, replaceable rack** on a
steel feature; preload/mounting stiffness question open. Bed lift =
square-tube-in-square-tube columns (bed tubes larger than frame tubes),
corners + midpoints. Frame solid, independent of gantry. Modular parts list.

---
## 1. Motor

### Confirmed baseline (on file)
`drawings/24HS40-5004D-E1000_Full_Datasheet.pdf`
- **24HS40-5004D-E1000** — NEMA 23-class closed-loop stepper
- **Holding torque: 4.0 Nm** (user-confirmed acceptable 2026-11-02: "4nm is fine")
- **Rated / peak current: 5.0 A**
- Encoder: **1000 PPR** (4000 CPR quadrature)
- Shaft: GX16 (16 mm bore class)
- Status: datasheet on file; no supplier price captured yet.

### Sourcing options (checked 2026-11-02)
| Source | Item | Notes |
|---|---|---|
| **StepperOnline** (stepperonline.com) | 24HS40-5004D-E1000 — **$32.95, in stock** | Direct match to the datasheet part. US ship. |
| **Vallder.com** (EU, DHL) | Servo Stepper **5.0 / 8.5 / 12.5 Nm** — €103.40 / €108.90 / €127.60 (SKU 1149001/1038000/1149000) + ZDM-2HA865 closed-loop driver €50.49 | Closed-loop "servo stepper" sets, EU stock, 5.0 Nm variant is the 4 Nm class. Driver sold separately (or as set). |
| **Vallder.com** | **MKS SERVO42C** (SKU 1225000), Integrated Closed Loop Motors (1238000) | Alternative closed-loop options on the same EU shop. |

**Recommendation:** source the **24HS40-5004D-E1000** from **StepperOnline** (exact
part match to the datasheet already in `drawings/`, $32.95, in stock) as primary;
keep **Vallder 5.0 Nm servo-stepper set** as the EU-shipping fallback if the
driver/closed-loop integration is preferred over open-loop + encoder.

> Quantity: X = 1 motor, Y = 2 motors (dual drive). Total **3 motors**.
> Plus 3 matched drivers (24HS40 → 5 A driver, e.g. DM860H / ZDM-2HA865).

---
## 2. Gear (rack & pinion) selection

### Design inputs (from `calc/axis-sizing.md` v4)
- Forces: **20 N** engraving → **150 N** worst-case slotting (X/Y only; Z carries the 2000 N drilling load)
- Speed target: **15 m/min**
- Motor: **4.0 Nm** continuous
- Rack is **static & replaceable**, mounted on a steel feature → the pinion
  (on the motor) is the only rotating gear per axis.

### Sizing (verified by calculation)
Pinion torque at pitch radius `r = m·z` (module m, teeth z):  `T = F·r`
With `m = 2 mm`, `z = 12`:  `r = 24 mm`, pitch dia `48 mm`.

| Case | T required | Motor 4.0 Nm |
|---|---|---|
| Engraving (20 N) | **0.48 Nm** | 8.3× margin |
| Slotting (150 N) | **3.60 Nm** | 1.11× margin (at usable limit) |
| Speed @ 15 m/min | **99 rpm** | ~30× below continuous ceiling |

**Selected: Module 2, 20° PA, 12 teeth, 48 mm pitch diameter.**
This lands the worst-case slotting torque exactly at the 4 Nm motor with the
0.9 usable-margin, and leaves ~30× speed headroom. Engraving is 8× under.

### Candidate racks / pinions to source
| Item | Source | Notes |
|---|---|---|
| **KHK KRF-2-1000 / KRF-2-1500 / KRF-2-2000** (module 2, hardened steel, 1000/1500/2000 mm) | khkgears (EU distributor; KRF stock racks 0.5–10 module, 100–2000 mm) | The standard CNC hardened rack. Length = X/Y stroke + overtravel. |
| KHK spur pinion **SPM-2-12** (module 2, 12T, 20° PA) matched to KRF-2 | KHK | Matches the pinion selection; hardened, bore for motor coupling. |
| Generic carbon-steel rack+pinion m1.5/m2 | AliExpress / McMaster / Amazon (1.5–2.0 module, 14–20T) | Cheaper, lower accuracy (Level 7); fine for engraving, marginal for slotting repeat. |
| **Vallder "Rack and Pinion Gearbox" (1145000) / Helical Gear HG (1220000)** | vallder.com | These are gearboxes/reducers, not raw rack+pinion — useful if we add a gearbox to lower rpm, not the linear drive itself. |

> **Z axis:** uses the **Hypertherm Duramax MRT 32-pitch** rack (torch-integrated
> sleeve, P/N 228738) — **no separate Z gear** is sourced. The torch's own pinion
> drives the Z.

---
## 3. Guides (confirmed: HG50)
- User spec: **HG50 linear bearings**, carriage carries motor + pinion.
- Vallder has **SHAC GHR linear guideways** (1257000) + GHR blocks (1256000)
  as an EU option; Hiwin **HGH50 / HGW50** equivalents via usual channels.
- 2 rails per axis × 2 blocks per rail (matches the calc's "2 rails × 2 blocks").

---
## 4. Modular parts tree (as user specified)
```
Bed                      (done — trough, 183 kg)
└─ Bed frame            (new)  square-tube-in-square-tube lift columns,
│                            corners + midpoints, bed tubes > frame tubes
└─ Carriage frame        (new)  solid, independent of gantry; mounts on bed frame
│   top, ~3.5 ft (~1.07 m) above ground
└─ Y carriage LEFT       (new)  HG50 + motor + pinion + rack (static, replaceable)
└─ Y carriage RIGHT      (new)  same, dual-driven
└─ X carriage            (new)  HG50 + motor + pinion + rack (static, replaceable)
└─ Tool attachment IF    (new)  Hypertherm Duramax 180° machine torch mount
└─ Z axis module         (new)  torch-integrated: Duramax MRT 32-pitch pinion
                                on the torch, no separate Z gear
```
Attachment order (each part attaches to the previous):
Bed → Bed frame → Carriage frame → (Y-L, Y-R) → X → Tool IF → Z module.

---
## 5. Open items / next
- [ ] Confirm rack length: need X & Y **stroke lengths** (not yet set) → picks KRF length.
- [ ] Preload vs mounting-stiffness decision for the captive pinion (user: "maybe mounting is enough").
- [ ] **Center-of-travel stability** — user concern; likely addressed by rack support
      brackets every ≤300 mm + the steel feature. To be modeled in CAD.
- [ ] CAD render of the full modular tree via FreeCAD bridge (in progress).
- [ ] Capture driver part number (24HS40 needs a 5 A driver) — Vallder DM860H (1151000) candidate.
