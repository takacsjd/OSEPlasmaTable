# Hypertherm Powermax 65 — CNC plasma torch (customer-supplied)
Project: `C:\Users\Core\Documents\plasma-table`
Captured: 2026-10-22

## Is this torch intended for plasma CNC?
**Yes — unambiguously.** The customer spec calls for a Powermax 65 with **CPC port**.
That's a *mechanized/CNC* plasma system:
- Torch: **Duramax 180° full-length machine torch** (the CNC-style torch, not the hand torch)
- **Gear rack (32 pitch)** on the positioning sleeve — this is the torch's *own* Z-axis drive
- **Cap-sensor switch** — for breakaway / part collision detection (already in customer wishlist)
- **CPC port** (Common Plasma Connector) — carries pilot, preheat, cut, arc-voltage sense
- Designed to bolt onto a wide variety of X-Y tables (Hypertherm manual, §3-7)
- Powermax 65 = 65 A, 139 V arc, ~9 kW. Cut: up to ~20 mm (3/4") mild steel.

Part numbers (180° full-length machine torch):
- 059476 — 15 ft lead
- 059477 — 25 ft lead (common for CNC)
- 059478 — 35 ft lead
- 228737 — MRT positioning sleeve kit (includes gear rack)
- 228738 — **MRT removable gear rack replacement** (32 pitch)
- 228735 — MRT front mounting sleeve
- 228736 — MRT adapter ring (coupler)

Torch weights (from operator manual §Specs):
- Machine torch 25 ft: 7.6 lb (3.4 kg)
- Machine torch 50 ft: 13.2 lb (6.0 kg)
- Machine torch 75 ft: 18.8 lb (8.5 kg)
- Power supply 65 A: 54.1 lb (24.5 kg) CSA / 47.0 lb (21.3 kg) CE

## The gear rack (32 pitch)
The full-length machine torch ships with a **32-pitch rack** on the positioning sleeve.
- This is a **standard 32-pitch involute rack** (DIN 3960 / ISO 53 standard, module m = 25.4/32 ≈ **0.8 mm**).
- The customer's "rack gear already attached" observation is **correct** — the torch has its own Z rack.
- **Z drive options for this machine:**
  1. **Torch-rack Z drive (standard CNC plasma):** pinion meshes with the torch's 32-pitch rack, motor on the gantry, rack on the torch sleeve. Z motion = motor drives pinion → rack → torch moves. This is the classic PlasmaC / Hypertherm PHC setup.
  2. **Ballscrew / lead-screw Z drive:** ignore the torch rack (it stays as a passive positioning sleeve), use a separate screw. More precision, more parts, more cost.
- **Recommendation for this build:** **option 1** — the torch already has the rack, it's 32 pitch (standard), and the customer wants "high/adjustable Z (curved surfaces)" which a rack/pinion does fine. Use a standard 32-pitch pinion (module 0.8 mm), 12–16 teeth, with a bearing-supported carrier on the gantry.
- **Pinion spec to order:** 32 pitch, 14 teeth, module 0.8 mm, bore 10–12 mm (for 24HS40 motor shaft or a 5 mm pinion shaft with a coupling).
- **Rack length:** the torch's own rack is ~100–150 mm — enough for a 50–100 mm Z stroke, which is all a plasma table needs (standoff 6–12 mm + plunge 5 mm + THC band ±5 mm).

## Arc voltage / THC — the safe way (Mesa THCAD)
Your customer spec already picks this: **Mesa THCAD-5** (ohmic touch-off) + **THCAD-10** (voltage-sense THC). Both are the right choice and they solve the "how do I tap high voltage safely" problem.

### How it works
The **CPC port** on the Powermax 65 has a dedicated **arc-voltage sense line** (one of the 4–5 CPC pins). Hypertherm's own PHC (Plasma Height Control) system uses this same sense line. The Mesa THCAD boards are built to accept this line through an **external voltage divider** (two resistors) that steps the ~139 V arc voltage down to the board's input range.

### Mesa THCAD options (from the manual)
| Board | Input range | Divider | Use |
|---|---|---|---|
| **THCAD-5** | 0–5 V | **external** high-voltage resistor | touch-off / ohmic sensing |
| **THCAD-10** | 0–10 V | **external** high-voltage resistor | **arc-voltage THC** (real-time height) |
| THCAD-300 | 0–300 V | **on-board** divider | arc-voltage THC (no external divider) |

**You need a THCAD-10 (or -300) for the arc voltage THC, and a THCAD-5 for the ohmic touch-off.**

### Voltage divider math (THCAD-10, 0–10 V input)
Formula: **R_series = (V_arc_max − 10 V) / 100 µA**

For a Powermax 65 arc at ~139 V:
- R_series = (139 − 10) / 100 µA = **1.29 MΩ**
- Use a **1.3 MΩ, 1 W, metal-film** resistor (or two in series, e.g. 680 kΩ + 680 kΩ, with a 100 nF cap across the low side for filtering).
- The THCAD-10's input impedance is 100 kΩ, so the divider loads the sense line minimally.

### Why this is safe
1. **No direct contact with the arc voltage.** The sense line is a *low-current, high-impedance* tap — you're not shunting any real current from the arc.
2. **The THCAD is isolated** — 2500 V common-mode isolation on the 300 V model, 500 V continuous on the 10 V model.
3. **The resistor does the voltage division** — the THCAD only sees ≤10 V at its input.
4. **EMI:** use shielded cable for the sense line, route it *away* from the torch lead and motor cables, and ground the shield at the THCAD end only.

### Qtplasmac setup (LinuxCNC)
- THCAD-10 → analog input 0 of the Mesa 7i76e (or 7i90) → `plasma-thc` component in Qtplasmac.
- THCAD-5 → analog input 1 → `plasma-torch-touchoff` (ohmic sensing for initial height).
- Qtplasmac handles the PID loop, arc-OK detection, and THC enable/disable.
- SheetCAM outputs the G-code; Qtplasmac interprets M67 (arc start) / M75 (arc stop) / M74 (THC on) / M76 (THC off).

### What to order
| Item | Part / spec |
|---|---|
| Mesa THCAD-10 | 0–10 V input, external divider (for arc voltage THC) |
| Mesa THCAD-5 | 0–5 V input, external divider (for ohmic touch-off) |
| Voltage divider | 1.3 MΩ 1 W metal-film (or 2× 680 kΩ) + 100 nF cap |
| Shielded cable | 2-conductor, 100 ft, for the sense line |
| Pinion (32 pitch) | 14 teeth, module 0.8 mm, bore 10–12 mm |

## Reference files (in `drawings/`)
- `hypertherm_duramax_torches_dimensions.pdf` (1.4 MB, HYP112931) — **official Hypertherm torch dimension brochure** (full-length: 35 mm barrel, 39.6 cm, 32-pitch rack)
- `duramax_torch_figures_p1–p4.png` — rendered figure pages from that PDF (p2 = machine torch dimensions)
- `powermax65_operator_manual_806650.pdf` (6 MB, rev 4) — full operator manual with torch setup, gear rack, parts, cut charts
- `mesa_thcad_manual.pdf` (105 KB) — THCAD-5/10/300 manual with divider math, pinout, isolation specs

## Open items
- [ ] Confirm the customer's Powermax 65 is the **SYNC** version (CPC port) — not the older 2-wire pilot version
- [ ] Order the Mesa THCAD boards + divider resistors
- [ ] Order the 32-pitch pinion (module 0.8 mm, 14 teeth)
- [ ] Decide: torch-rack Z drive (recommended) vs ballscrew Z drive
- [ ] Confirm the torch's rack length is sufficient for the Z stroke needed (likely ~100–150 mm on the torch sleeve)
- [ ] EMI: shielded sense line, route away from motor cables, ground at THCAD end only
