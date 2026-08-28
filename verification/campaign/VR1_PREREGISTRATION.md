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

---

## Amendment 1 — 2026-08-28T19:35Z — **G1 AS FROZEN TESTED THE WRONG PROPOSITION.** Corrected before first compute; the original is struck, not rewritten

**Rule 2 condition, stated and checked:** amendments before first compute are legal and must name
the condition and how it was verified. **No run directory exists for VR1 and no artifact has been
written.** The instrument was driven once, from the working tree, producing the line
`VERDICT: NOT A RESULT` on stdout and **no result-bearing artefact** (charter §2i.1: a launch
producing no artefact does not close the gates — *"there was no answer to fit to"*). Verified by
`ls verification/runs/ | grep -i vr1` → **absent**. The gate below is corrected **because it was
wrong**, not because a result was inconvenient — and the correction makes the gate **stricter**,
not looser.

**~~G1 REFUSES a directory holding `T_rampSurface.raw`, `p_rampSurface.raw`,
`rho_rampSurface.raw` (three matches where one is meant)~~** — **STRUCK.**

**Why it was wrong, and it is the more interesting half of this item.** *Three matches* is a
property of **the defective reader's filter**, not of the directory. That directory contains
**exactly one pressure file**. A correct selector must **return `p_rampSurface.raw`**, not refuse
it. **I had encoded the DEFECT'S SYMPTOM as a property of the INPUT** — so the gate demanded that a
repaired reader fail on well-formed data, and it duly failed the known-good selector while the
known-bad one also failed. **A gate that both candidates fail is not discriminating; it is broken**,
and it would have rejected every correct repair cfd could have sent.

**G1 (corrected) — THE SELECTOR MUST NEVER RETURN A NON-PRESSURE FILE.** On a directory holding
`T_rampSurface.raw`, `p_rampSurface.raw`, `rho_rampSurface.raw`, the selector must return
**`p_rampSurface.raw`**. Returning `T_…` is the L-398 failure and is a **GATE FAIL**.

**G1b (new) — AND IT MUST REFUSE ON A GENUINELY AMBIGUOUS SET.** On a directory holding
`p_coneSurface.raw` **and** `p_rgh_coneSurface.raw` — two real pressure fields, one meant — the
selector must **raise**, not choose. This is the cardinality limb G1 was reaching for and missed.

**G2, G3, G4 unchanged.** **Cap unchanged at 8.0 core-minutes.** **No label changes.**

**Recorded because the failure is the lesson:** the gate was driven **before** it was believed, and
driving it is what exposed it. A frozen gate that had never been executed would have been discovered
by the first team whose correct repair it rejected.
