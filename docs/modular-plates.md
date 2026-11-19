# Modular Plasma-Cut Plate Structure

Status: PROPOSED (2026-11-05). Direction set by user; hand drawings in progress.

## Why
Two goals, one mechanism:
1. **OSE compliance** — the design is reproducible with the minimum toolset a
   participant has (a plasma cutter + a drill press), not a metal shop.
2. **Self-replication** — the machine cuts its own structure. If every
   structural member is a flat plate cut by the machine's own plasma head,
   the machine can produce a copy of itself.

## Core idea
Replace the welded square-tube frame with **flat steel plates that interlock
by bolting**. Each plate is a single plasma-cut profile (2.5D — cut + drilled
+ possibly light bending). Plates mate at designed joints (bolted tabs,
dovetail-ish interlocks, or clevis lugs) so the assembled structure is rigid
without welding.

## Consequences for the rest of the design
- **No welded joints** — everything is bolted, which already matches the
  "keep interfaces bolted, not welded-precise" rule in scope.yaml.
- **Rigidity comes from the plate geometry + bolt preload**, not from weld
  continuity. This is the hard engineering problem: a bolted-plate frame must
  resist the same bending/torsion loads the tube frame did.
- **The plasma head is now also the fabrication tool** — plate profiles must
  be cuttable at the machine's own kerf/amperage (Powermax 65 limits on
  thickness and detail).
- **Self-replication loop:** machine cuts plates -> plates bolt into frame ->
  frame holds rails/motors -> machine reproduces frame.

## Open questions (need answers before CAD)
1. **Plate stock thickness** available from the site? (Powermax 65 sweet spot
   ~ up to ~6 mm carbon steel for clean cut; thicker = slower/dirty.)
2. **Interlock joint style** — bolted tabs, clevis lugs, or true dovetail
   interlock? (Dovetails give the best stiffness-per-bolt; bolted tabs the
   easiest to cut and align.)
3. **Bending allowance** — pure flat (no bending) or light air-bent edges
   allowed? Pure-flat is most self-replicable (no press brake).
4. **Trough/water bed** — does it stay as the existing committed design, or
   also move to cut plates? (It's already a separate module.)
5. **Self-replication target** — does the machine cut ALL its plates, or just
   the frame (leaving rails/lead-screws/bearings as purchased parts)?

## Sourcing status (2026-11-05, user ordering)
- Basic **pinion + rack** — order placed (drives X/Y).
- **Steppers + controllers** — order placed.
- Rationale: order the drive chain now so firmware/control work can proceed
  while hand drawings for the structural modules are finished.

## Hand drawings (in progress)
User is hand-drawing the other (non-drive) elements — structural modules,
joints, lifting frame. These feed the CAD once the modular-plate concept is
pinned down.
