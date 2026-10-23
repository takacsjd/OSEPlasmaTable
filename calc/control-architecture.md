# Control architecture — firmware & arc-voltage sensing
Project: `C:\Users\Core\Documents\plasma-table`
Captured: 2026-10-22

## Decision (recommended)
**Use the customer's spec: LinuxCNC + Mesa 7i76e + THCAD-10/THCAD-5 (Stack A).**
Do NOT put an ESP32 in the motion loop. LinuxCNC and an ESP32/GRBL
firmware are **alternative controllers, not a master/slave pair** —
"LinuxCNC streams G-code to an ESP32 for real-time control" is not a
buildable architecture (two motion controllers would fight over the same
steppers). Pick one as the motion controller.

### Why Stack A wins for a plasma table
1. **Native integrated THC.** LinuxCNC PlasmaC/QtPlasmac does the
   torch-height PID *inside* the motion controller (reads arc voltage →
   drives Z). In the ESP32/FluidNC world THC is **not native** — the
   FluidNC wiki states the ESP32 ADC is poor for this and the answer is
   an **external** THC board (more parts, more failure points).
2. **Hard real-time.** LinuxCNC runs RT-PREEMPT. The ESP32 path has
   USB/WiFi jitter — fine for hobby, not for production plasma THC.
3. **The isolated voltage sensing you want is the THCAD itself** —
   purpose-built, 2500 V isolated, 0–10 V out. No DIY instrumentation.
4. **Keeps the 4 Nm NEMA24 + ~100× torque margin** already sized.

### M5Stack display
Poor fit in Stack A (LinuxCNC HMIs are Linux). **Use a local 7–10" touch
panel on the control PC** (or a second HMI client). Keep the M5Stack as a
spare/HMI for other projects. The M5Stack only fits naturally in the
FluidNC/ESP32 world (Stack B), which is the weaker choice for plasma THC.

## What Mesa is
**Mesa Electronics** (Oklahoma City, US) — industrial I/O + motion boards
for LinuxCNC. Pieces in the spec:
- **7i76e** — stepper/I/O card (PCIe in control PC): step/dir for the
  NEMA24s + analog in/out + digital I/O. The "stepper driver interface."
- **THCAD-10** — torch-height front-end daughterboard (sockets into the
  Mesa 7i92 backplane). Job: take the HV arc sense, divide, isolate,
  output clean 0–10 V analog + ArcOK digital.
- **7i92** — backplane the daughterboards socket into.

## Arc-voltage chain (the "proper instrumentation")
```
Powermax65 CPC arc-sense
   -> external ~1.3 MΩ divider  (for the 0–10 V THCAD-10 model)
   -> Mesa THCAD-10  (2500 V common-mode isolated; pins 2&5 removed for creepage)
   -> 0–10 V analog + ArcOK
   -> 7i92 backplane
   -> LinuxCNC PlasmaC THC  (PID -> Z axis)
   -> 7i76e step/dir -> stepper driver -> Z motor
```
THCAD-5 = the ohmic **touch-off** board (initial height / part detection).

### 4–20 mA clarification
4–20 mA is an industrial **transmission** standard (current loop to a
PLC/DCS over long cable) — for **carrying** a signal, not **sensing** one.
For local arc-voltage sensing the correct instrument is an **isolated
voltage divider into an isolated analog input** = the THCAD-10 + external
divider. The THCAD already provides the galvanic/optical isolation you
were reaching for. **No 4–20 mA transmitter needed on a CNC plasma table.**

## Firmware landscape (reference; if ESP32/Stack B were chosen)
| Firmware      | Platform           | Plasma THC        | Notes |
|---------------|--------------------|-------------------|-------|
| FluidNC       | ESP32 (best fit)   | **Not native**    | Best ESP32 fw, WiFi/web UI, SD-card autonomous; bolt-on external THC. |
| grblHAL       | STM32/Teensy (ESP32 less common) | Plugin, external up/down | More features; plasma still external. |
| GRBL_ESP32    | ESP32              | None real         | Too basic. |
| KRANC         | ESP32              | Not plasma-specific | General-purpose. |
| LinuxCNC PlasmaC | Linux PC + Mesa  | **Native, integrated** | **← recommended for plasma** |

## Sourcing / open items
- [ ] Confirm which Mesa boards the customer already has (7i76e? 7i92? THCAD-10 vs THCAD-5?)
- [ ] External divider for THCAD-10: (139−10)/100 µA ≈ **1.3 MΩ** 1 W metal-film (+100 nF)
- [ ] Control PC: LinuxCNC (2.9+) + PlasmaC/QtPlasmac, RT-PREEMPT kernel
- [ ] Local touch HMI (7–10") on the control PC
- [ ] Confirm Powermax65 is the SYNC/CPC version (arc-sense line present)
