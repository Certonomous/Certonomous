# VR1 — FROZEN ACCEPTANCE TEST FOR THE NON-UNIQUE SELECTOR CLASS (`L-398`)

**Repair-registration.** Frozen before any work under it. Sanaa's 2026-08-28 amendment makes a
finding-repair a queue item: *"frozen, capped, schedulable work items like any case."*

## 1. The finding this repairs
`L-398` / `DEAD_LEVER_AUDIT` §9.2. `verification/runs/F3_runs/successor_triple_2026-08-26/grade_f3s.py:239`
selects a pressure file with `sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)[0]`.
The selector admits more than one member where the code assumes exactly one; under a surface rename
(`rampSurface`, `upperSurface`) three files match and ASCII puts `T_` first, so **a temperature field
is graded against a pressure band**. Driver twins at `run_f3s.py:255,:287`.

## 2. WHAT IS MINE AND WHAT IS NOT — stated first, because it decides the deliverable
`grade_f3s.py` is a **frozen comparator** (rule 2 bars the edit post-compute) and its tree is
**cfd's territory**. **The repair itself is not mine and this item does not attempt it.**
**This item's deliverable is the FROZEN ACCEPTANCE TEST** any successor must pass — written *before*
a successor exists, so it cannot be shaped to the repair that arrives.

## 3. Gate (frozen)
A committed control script under `verification/credibility/` that, given any candidate selector:
- **G1** REFUSES a directory holding `T_rampSurface.raw`, `p_rampSurface.raw`, `rho_rampSurface.raw`
  (three matches where one is meant) — a **cardinality** refusal, not a "pick better" heuristic.
- **G2** ACCEPTS a directory holding exactly `p_coneSurface.raw` among `T_`/`rho_` siblings.
- **G3** REFUSES silently-wrong behaviour: it must **fail** a selector that returns `T_rampSurface.raw`
  rather than merely warn.
- **G4** is driven on **bytes written by the real producer** where available (§2j): real `.raw`
  basenames enumerated from disk, not invented.

## 4. Threshold / label
**PASS** = all four limbs behave, G1/G3 firing and G2 silent. **GATE FAIL** = any limb misbehaves.
**NOT A RESULT** if the control cannot be driven at all.

## 5. Cap
**8.0 core-minutes.** Zero solver compute. An overrun stops the item (rule 12).

## 6. Not claimed
No verdict on F3S moves. The frozen comparator is not edited. This item does not oblige cfd to
adopt the test; it obliges **me** to have written it before judging their repair.
