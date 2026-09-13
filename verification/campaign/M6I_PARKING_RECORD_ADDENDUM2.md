# M6I PARKING RECORD — ADDENDUM 2. **THE NUMERICS RUNG IS CLOSED ON BOTH HALVES.**

**Written before R10 ran; placeholders filled from its result and nothing else touched.** Appended to `M6I_PARKING_RECORD.md` (committed
`62ac5d565`, addendum 1 `801391c00`). **Appended, never inserted: lines whose number changed
above this section: 0.** Every number here except R10's own results was measured
before R10 started; its result fields were the only ones filled afterwards, and nothing else
in the document was touched when they were.

*Written in advance under `M6I_R10_TRANSONIC_PREREGISTRATION.md` §0, because a parking record
written after the fact reads as an excuse and one written before reads as a plan.*

---

## A2.1 WHAT ADDENDUM 1 LEFT OPEN, AND WHAT CLOSED IT

Addendum 1 corrected the "no shock" sentence and named two extraction defects. **It left the
parking record's claim that the numerics rung was spent standing on three `div(phid,p)`
variants and one closure change.** The chief then read the family's own table back: across all
eight cases **`transonic yes`, `nNonOrthogonalCorrectors 2` and `limited corrected 0.33` were
identical in every one.** The rung was not spent; it had never been aimed at the formulation.

**Two rungs closed that gap, and both are measurements, not arguments:**

| rung | change | verified in effect | result |
|---|---|---|---|
| **R9** `ed1f053ce` | `nNonOrthogonalCorrectors` **2 → 5** | **6 pressure solves per outer iteration against 3** | limb **did not fire**: steepest raw-trace gradient **+1.1222 → +1.1222, movement −0.0000** against a registered **+1.8328**, at **2.65×** the cost |
| **R10** `d35d36f9c` | `transonic` **yes → no** | **all five fields differ from L3; p residual 16–40× tighter (2.54e-05 vs 1.01e-03 at iteration 200)** | limb **did not fire**: steepest gradient **+1.1222 → +1.1804**, movement **+0.0582** against a registered **+1.8328** |

**R9's null is unusually strong because the change was proved to have reached the solver before
the result was read** — six p-solves against three — so "it did not work" cannot be confused
with "it did not happen." It moved the graded quantity by **+0.0002**, an order of magnitude
below the startup-ramp noise of **+0.0022**.

## A2.2 WHAT R10 ACTUALLY SWITCHED — FOUR CONSEQUENCES, NOT ONE

Read from `rhoSimpleFoam/pEqn.H`: under `transonic no`, (1) **`fvm::div(phid,p)` is absent from
the pressure equation entirely** — the term R5–R7 spent 42.54 core-minutes moving ceases to
exist, and its `Gauss upwind` entry becomes dead configuration; (2) **`pEqn.relax()` is not
called**, so `relaxationFactors.equations.p 1` is inert for the pressure equation and the
launcher's assert message about diagonal dominance no longer describes what happens;
(3) **`adjustPhi` is called**; (4) the `interp(psi·p)` subtraction from `phiHbyA` does not
happen. **"Same schemes" would have implied more sameness than existed.**

## A2.3 THE UPDATED ELIMINATION TABLE

Every row of the record's §2 stands. Two rows are added:

| candidate | verdict | the measurement |
|---|---|---|
| **Non-orthogonal correction** | **dead** | 5 correctors against 2 — residual `0.4925ⁿ` from 24.26 % to 2.90 %, derived from `limitedSnGrad.C` and the mesh's own 44,832-face histogram — moved the steepest gradient **−0.0000** |
| **`transonic` formulation** | **closed on the registered limb — but see A2.8** | steepest raw-trace gradient +1.1804 against +1.8328 required. **The same change moved span-averaged RMS 0.3328 → 0.2908 and bias 0.1240 → 0.0785 — 32.8 % and 64.2 % of a full grid level — and moved `x_shock` 0.9531 → 0.8150, satisfying S2 (< 0.85) for the first time anywhere in this family.** |

## A2.4 COST

| rung | core-min | outcome |
|---|---:|---|
| R5 / R6 / R7 | 12.87 / 17.00 / 12.67 | NOT A RESULT — **waste 42.54** |
| R8 `kOmegaSST` | 79.40 | GATE FAIL — a graded result |
| R9 `nNonOrthCorr 5` | 15.53 | GATE FAIL, limb silent — a graded result |
| **R10** `transonic no` | **6.67** | GATE FAIL, limb silent — a graded result. Ratio **1.131**, the best cost estimate of the family. |
| **R5–R10 total** | **144.14** | **13.1 % of one graded level** (L1 = 1,098); waste unchanged at 42.54 = 3.9 % |

**R9's calibration is the cost lesson of the family: predicted ×1.6, actual ×2.65, +65 % over
the estimate and 44.1 % of cap. It cost nothing because the cap was set from a worst case
rather than from the prediction** — a habit worth keeping.

## A2.5 🔴 THE LIMITS — ADDENDUM 1's EIGHT, PLUS THREE THIS ROUND

The record's §5 limits all stand. Added:

9. **R9 measured an outcome, not a residual.** The `0.4925ⁿ` model says the non-orthogonal
   residual fell from 24.26 % to 2.90 %; **no instrument confirmed that it did.** A null is
   consistent with "the correction converged and does not matter" **and** with "the correction
   never converged." Distinguishing them needs the correction magnitude logged per iteration,
   which does not exist. **296 faces past the `0.05` saturation floor remain unexamined.**
10. **L3 cannot resolve a shock** — 4 cells over 0.481c, ceiling **+3.53** against the
    experiment's **+8.46**. Every R9/R10 limb result is bounded by that, and **L2 was run only
    if the limb fired.**
11. **`scripts/queue_entry_check.py` is not the validator the daemon runs**, though
    `verification/queue/cfd/README.md:10` says it is. It has **no `memory_footprint_gb` check**;
    gate B lives in `scripts/queue_runner.py:707`. **A lane following the README will believe an
    entry is clean and be refused.** Not fixed here — named for whoever owns that tooling.

## A2.8 🔴 THE LIMB MEASURED SHARPNESS AND THE RUNG MOVED MAGNITUDE. SAID PLAINLY.

**R10 is the largest mover in this family and its registered limb reports "did not fire".
Both statements are true and the record carries both.**

| quantity | L3 baseline | **R10 `transonic no`** | as a fraction of one grid level (L3 → L2, ×8 cells) |
|---|---:|---:|---:|
| span-averaged RMS | 0.3328 | **0.2908** | **32.8 %** |
| span-averaged bias | 0.1240 | **0.0785** | **64.2 %** |
| D2 shock rise | 0.0083 | **0.0129** | **49 %** |
| `x_shock` | 0.9531 | **0.8150** | **S2 (< 0.85) satisfied — the first time in this family, on any grid** |
| raw-trace steepest gradient | +1.1222 | **+1.1804** | **+5 % — the limb, and it did not fire** |
| max single-interval rise | +0.1191 | **+0.2475** | ×2.08 |

For comparison, on the same measure: **R9's correctors 0.1 %, R8's SST 1.5 %.**

**The limb was registered on the steepest gradient because sharpness is what a missing shock
is. R10 improved magnitude and shock position without improving sharpness, so a kill-only
limb correctly reports silence on its own terms while the rung was not null.** That is a
defect in the instrument's aim, not in its execution, and it is this lane's.

**AND THE CONSEQUENCE IS UNMEASURED: L2 under `transonic no` was never run**, because R10 §3
made L2 conditional on the limb firing. **R10 on a 15,360-cell grid bought a third of a grid
level; what it buys on L2 or L1 is not known and this record does not guess.** §0 binds and
no R11 is proposed here — **the ruling is the supervisor's**, and this section exists so it is
made on the measurement rather than on the limb alone.

## A2.6 THE THREE LIVE LEADS, UNCHANGED

1. **Cell aspect ratio** — max 873.8 on L2, **1,578.6 on L1**, 1,200 high-aspect cells, never
   examined. The tip-cap exoneration was **spanwise only** and would not see this.
2. **Freestream eddy viscosity** — `I = 0.1 %`, `nut/nu = 1`, a judgement never varied.
3. **The blunt-trailing-edge base flow under a steady solver** — 100 % of clipped cells at
   x/c ≥ 0.885, 79.9 % within 0.20c, symmetry 0.063. **The only lead that questions the solver
   rather than its inputs.**

## A2.7 WHAT THIS IS

**A defensible graded verdict — L1 `GATE FAIL`, 12/12 B1 rows monotone, η 0.65-lower in band at
0.0494 — plus a documented elimination of resolution, reference pressure, the shock-window mesh,
the tip cap, the pressure discretisation, the pressure floor, the turbulence closure, the
non-orthogonal correction and the `transonic` formulation, for **144.14** core-minutes against
one graded level's 1,098.**

The three leads are live **because everything cheaper was ruled out first, by measurement, with
the instrument verified in effect before each result was read.**

**M6I PARKS. Parked is not cancelled.**

*Drafted by a cfd `lab-lane`, 2026-09-13, BEFORE R10 ran. No agent's message is Sanaa's consent.
Submissions parked.*
