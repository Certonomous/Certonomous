# M6C2 ROUTE (d) L1 — **SOLVE** RUNG, PRE-REGISTERED BEFORE COMPUTE

**Status: FROZEN BEFORE FIRST COMPUTE.** `verification/runs/M6C2_runs/ROUTE_D_SOLVE/L1/`
does not exist at this commit; the launcher tests for it and refuses if it does.

Its own rung. It does not amend `dc7f4cfd` (L1 mesh admission) or `cfbb4e4d` (L2), and it
changes no gate, threshold, cap or label in either.

---

## 1. THE LESSON THIS DOCUMENT IS BUILT AROUND

Route (d) L2 registered four predictions and two falsifiers, **all aimed at route (c)'s
failure mode recurring. Every one was correct. Route (c) did not recur — and the mesh
failed anyway, on skewness, through a channel the registration never mentioned.**

**A pre-registration written to catch the last failure is blind to the next one.**

So this document registers **falsifiers for how the RESULT COULD BE UNUSABLE**, not only
for the hypothesis under test. And the first of those was computed **before** asking for
any compute — with the consequence below.

## 2. THE DISQUALIFYING LIMITATION, COMPUTED BEFORE THE RUN, NOT DISCOVERED AFTER

The AGARD AR-138 B1 condition is **M = 0.8395, α = 3.06°, Re = 11.72e6** on the mean
aerodynamic chord (0.64607 m). From those three numbers alone: a = 340.3 m/s,
**U = 285.7 m/s**, ν = 1.575e-05 m²/s.

Route (d) L1's surface cells sit at refinement level 4 on a 0.5 m background = **0.03125 m**,
first cell centre **0.01562 m**. With Cf = 0.0576·Re^(−1/5):

| | first-cell y⁺ |
|---|---:|
| **L1, level-4 surface** | **≈ 9,447** |
| L1, level-5 (nose / crown / cap_nose) | ≈ 4,723 |
| wall functions valid | **30 – 300** |
| low-Re wall resolution | ≈ 1 |

**y⁺ ≈ 9,447 is about 31× the top of the wall-function validity range**, and
**`addLayers` was `false`, so there is no prism layer at all** — the near-wall cell is a
cut hexahedron. The wing carries **26 cells per chord** at level 4.

**THEREFORE, DECLARED HERE RATHER THAN FOUND LATER: this solve CANNOT produce a
validatable aerodynamic result.** Specifically it may **not** be used to claim

- agreement or disagreement with AR-138 Cp at any spanwise station,
- a lift, drag or moment coefficient comparable to any reference,
- shock position or the λ-shock structure (M6's defining feature),
- **any** skin-friction or boundary-layer quantity.

**No such claim may be made from this rung even if the numbers happen to look
reasonable.** A plausible-looking Cp from a y⁺ = 9,447 mesh with no layers is a
coincidence, not a validation, and this clause exists so that coincidence cannot be
promoted afterwards.

## 3. WHAT IS ACTUALLY UNDER TEST — MESH USABILITY, NOT AERODYNAMICS

**Registered question: does the route (d) L1 mesh run a compressible RANS solver to a
converged, bounded, physically-shaped steady state?**

That is the natural successor to mesh *admissibility* and it is the whole claim.
Admissibility says `checkMesh` accepts the mesh; usability says a solver does.

**Solver:** `rhoSimpleFoam`, k-ω SST, wall functions, `endTime` 2000.
**Patches:** `farfield` freestream, `symm` symmetryPlane, wing patches `wall`.

## 4. LABELS, FIXED NOW

- **`PASS`** — rc = 0, `End`, last time == `endTime`, fields present; **and** all four
  usability limbs in §5 clear.
- **`GATE FAIL`** — the run completes but a §5 usability limb fails.
- **`NOT A RESULT`** — the run does not complete, or a reader fails its plant.
- **`BLOCKED`** — the solver cannot be run at all.

**`PASS` here means "the mesh is usable by a solver". It does NOT mean the answer is
right, and §2 forbids reading it that way.**

## 5. USABILITY FALSIFIERS — THE POINT OF THIS DOCUMENT

Registered **before** the run. Each is a way the result could be **unusable** that is not
a statement about the hypothesis:

1. **Divergence / non-completion** — any NaN, any floating-point exception, any bounding
   cascade that does not decay, or a run that stops short of `endTime`.
2. **Unboundedness** — negative or zero `k` or `omega` at `endTime`, or static temperature
   outside 100–600 K anywhere in the field. A solver can "converge" to nonsense.
3. **Residual stagnation without convergence** — initial residuals for `Ux`, `p`, `h`
   failing to fall **at least two orders** from their first-iteration values by
   `endTime`. Two orders is deliberately weak: this is a usability check, not a
   convergence claim.
4. **Non-physical global force** — |CL| > 2.0 or CL < 0 at α = +3.06°, or |CD| > 1.0.
   These are **absurdity bounds**, not accuracy bounds, and clearing them is **not**
   evidence of accuracy (§2).

**Any limb failing → `GATE FAIL`, reported at the core-minutes spent.**

## 6. NO ORDER, NO GCI, NO TRIPLE

**One level. No observed order of convergence, no GCI, and no Richardson extrapolation may
be computed or quoted from this rung** — and L2 is not available to pair with it, because
**L2 is `GATE FAIL`** (`e4fd30e1`) and a failed level is not a member of a grid family.

## 7. COMPLETION RULE AND PLANT

`rc` captured **inside** the wrapper; `End` line; **last time == `endTime` 2000**; fields
`U p T k omega nut alphat` present at `endTime`; **every field newer than the case's own
`0/T`** (age guard). The force reader plants a known value into a copy of the force file
and is **refused** if it cannot read it back.

## 8. COMPUTE (rule 12) — ANCHORED ON TONIGHT'S OWN MEASUREMENTS

Anchor, measured on this box tonight: **MRF R2 coarse, 154,715 cells, 0.5000 s/iteration
at 2 ranks** = 1.667e-02 core-min per iteration, i.e. **1.078e-07 core-min per
cell-iteration**. Route (d) L1 is 152,399 cells.

`rhoSimpleFoam` solves more equations than `simpleFoam` (adds energy); allowing a factor
of **1.6**: 152,399 × 2000 × 1.078e-07 × 1.6 ≈ **52.6 core-min**.

| | |
|---|---:|
| **estimate** | **~53 core-min** |
| **CAP** | **150 core-min** |
| derived | ≈ \$0.045 at \$0.0513/core-h — **derived, not measured** |

**The cap is ~2.8× the estimate because the anchor swaps solver** (incompressible →
compressible) — an anchor from a different equation set is weaker than one from the same
case, and that is stated as the reason for the margin rather than hidden inside the
estimate.

**Calibration carried forward from tonight:** L1 mesh estimate missed by **16× over**
(misprediction of delivered cell count); re-anchoring on L1's own measured cost brought L2
to **ratio 0.95**. Mesh cost per cell measured: L1 4.79e-06, **L2 6.31e-06 core-min/cell**.

**Disk:** free re-read immediately before launch; does not start below 20 GiB.

---

*Frozen 2026-09-11. §A1.3 stays FALSIFIED, route (c) stays TERMINATED, `M6C1` stays
BLOCKED, route (d) L2 stays `GATE FAIL`. Submissions parked.*
