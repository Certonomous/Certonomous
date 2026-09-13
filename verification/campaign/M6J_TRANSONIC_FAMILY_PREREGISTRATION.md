# M6J — THE `transonic no` FAMILY: L3, L2, L1. PRE-REGISTRATION.

**Item:** `M6J_TRANSONIC_FAMILY`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.
**Origin:** the top lead named in `M6I_PARKING_RECORD.md` ADDENDUM 2 §A2.8 — R10 moved the Cp
more than any rung in M6I (32.8 % of a grid level on RMS, 64.2 % on bias) and **L2 and L1 under
`transonic no` were never run.**

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**
Pre-compute: **`verification/runs/M6J_runs/` does not exist.** Launch through the runner;
entries drafted fail-closed into `verification/queue/cfd/held/`.

## §0 — M6I STAYS PARKED. THIS IS A NEW ACT, NOT AN R11.

M6I's §0 is untouched: its ladder is exhausted and nothing here reopens it. M6J carries one
**lead** forward under a fresh registration, which is what `M6I_PARKING_RECORD.md` §6 means by
*"parked is not cancelled"*. **No M6I gate, threshold, band, cap or label is altered.**

---

## 1. 🔴 THE ROACHE TRIPLE IS **NOT** IN PLAY, AND THE DISPATCH'S PREMISE DOES NOT SURVIVE THE FROZEN DEFINITION

M6J is the first M6 act since R5 that is a **family**, so it is the first that *could* produce
a triple. **But the admissibility bar is far higher than one satisfied limb, and this document
states that before the run rather than discovering it after.**

`M6I_R1_SOLVE_PREREGISTRATION.md` ADDENDUM 3, frozen, reads: *"A level is **shock-bearing only
if S1 AND S2 hold at BOTH η = 0.65 and η = 0.90**."* That is **four conditions per level,
twelve across a family.** Measured:

| level (`transonic`) | S1 @0.65 ≥0.212 | S1 @0.90 ≥0.320 | S2 @0.65 <0.85 | S2 @0.90 <0.85 | shock-bearing |
|---|---|---|---|---|---|
| L3_TVD (yes) | 0.0690 ✗ | 0.0434 ✗ | 0.9531 ✗ | 0.9233 ✗ | **no** |
| L2 (yes) | 0.1031 ✗ | 0.0582 ✗ | 0.8851 ✗ | 0.9233 ✗ | **no** |
| L1 (yes) | 0.1098 ✗ | 0.0827 ✗ | 0.8851 ✗ | 0.9233 ✗ | **no** |
| **L3 R10 (no)** | 0.0822 ✗ | 0.0515 ✗ | **0.8150 ✓** | 0.9233 ✗ | **no** |

**R10's L3 passes 1 of 4. S1 fails by 2.6× at η 0.65 and 6.2× at η 0.90. NO LEVEL IN THIS
ACT'S ENTIRE HISTORY HAS EVER BEEN SHOCK-BEARING.**

**So: the triple is registered here as a CONDITIONAL OUTCOME THIS DOCUMENT DOES NOT EXPECT.**
If all three M6J levels clear all twelve conditions, ADDENDUM 3 clause 1 applies and the triple
is computed under rule 5. **Otherwise ADDENDUM 3 clause 2 governs — no three-level order, no
GCI, computed, quoted or implied, and the comparison is labelled *"TWO LEVELS, NO ASYMPTOTIC
RANGE DEMONSTRATED"*.** ADDENDUM 3 is frozen and is **not** being reinterpreted.

**What M6J is actually for, stated plainly:** a **clean one-change measurement of `transonic no`
across three grids**, each with an already-graded `transonic yes` counterpart at identical
schemes. That is worth 1,083 core-minutes on its own. The triple is a bonus, not the plan.

---

## 2. 🔴 THE SCHEME SET — THE GRADED FAMILY IS MIXED AND A TRIPLE CANNOT BE

Measured across the graded family:

| level | `div(phi,U)` | `div(phi,nuTilda)` |
|---|---|---|
| **L3** | `linearUpwind limitedGrad` | `upwind` |
| **L2, L1** | `limitedLinearV 1` | `limitedLinear 1` |

**The family that produced M6I's verdict does not share a scheme set.** A Roache triple
requires three levels differing **only in h**; a mixed triple conflates discretisation order
with a scheme change.

**REGISTERED: the TVD set on all three levels** — `L3_TVD`, `L2` and `L1` carry a
**byte-identical `divSchemes` block, sha256 `223a8d2227d598e1`**, verified by this lane.

**`linearUpwind` is not available and that is measured, not preferred: `L2/ATTEMPT1_DIVERGED`
and `L1/ATTEMPT1_DIVERGED` both exist** — it diverged on both fine levels, which is why
ADDENDUM 8 moved them to TVD in the first place.

🔴 **AND THE COST OF THAT CHOICE IS AGAINST US: R10's evidence was obtained on L3 with
`linearUpwind`, NOT on the TVD set.** M6J-L3 therefore **re-establishes the effect on the
scheme set the family will actually use** before L2 and L1 are believed. Its counterpart is
`L3_TVD` (graded, `transonic yes`, identical schemes) — a clean one-change comparison. **If
M6J-L3 does not reproduce R10's direction against `L3_TVD`, the lead is weaker than the
parking record recorded and §5's branch (c) applies.**

---

## 3. 🔴 RANKS: 4 ON ALL THREE LEVELS — NOT 8 ON L1, AND HERE IS WHY

The dispatch offered L1 at 8 ranks. **This lane registers 4, and the reason is not throughput.**
All three levels carry `numberOfSubdomains 4; method hierarchical`. **Running L1 at 8 means
editing `decomposeParDict` — a second change** — and the R6/R7 comparison that settled the
pressure-floor question rested on **sha256-identical partitions and starting fields.** At 4
ranks every M6J level's decomposition is byte-identical to its graded counterpart's, so **the
only difference from the graded family is `transonic no`.** L1 at 4 ranks is 245,760 cells per
rank, a load L1 has already run to completion. The cost in core-minutes is unchanged; only wall
time doubles, and **nothing is killed on clock** (Sanaa directive #17).

---

## 4. THE ONE CHANGE, AND THE THREE BASELINES

**`system/fvSolution` and `system/fvSolution.startup`: `transonic yes;` → `transonic no;`**

| M6J level | staged from | cells | endTime | graded counterpart (`transonic yes`, identical schemes) |
|---|---|---|---|---|
| `M6J_L3` | `L3_TVD` | 15,360 | 3000 | `L3_TVD`, `m6i_grade_L3_TVD.json` |
| `M6J_L2` | `L2` | 122,880 | 5000 | `L2`, `m6i_grade_L2.json` |
| `M6J_L1` | `L1` | 983,040 | 8000 | `L1`, `m6i_grade_L1.json` |

**NOT carried forward:** R9's `nNonOrthogonalCorrectors 5` (stays **2**) and R8's `kOmegaSST`
(stays **`SpalartAllmaras`**) — both closed rungs that moved nothing, and either would confound
the formulation against its baseline. **Also unchanged:** `limited corrected 0.33`,
`pMinFactor 0.2`, `pMaxFactor 2.0`, every `div` scheme, every relaxation factor, `fvOptions`,
`writeInterval 200`, `purgeWrite 2`, `decomposeParDict`. **Added:** the verdict-inert
`clipCount` instrument.

**Pre-launch assertions, per level:** `constant/` byte-identical to the source; **exactly 3**
differing files in `system/` (`fvSolution`, `fvSolution.startup`, `controlDict`); **exactly 3**
changed/added lines; **exactly 1** new file (`system/clipCount.fo`); `nNonOrthogonalCorrectors`
still 2; `RASModel SpalartAllmaras`; the three pre-existing functionObjects byte-identical.
**And every launcher assert simulated against the staged case before arming** — that class of
defect refused this ladder twice (R8's model assert, R10's `transonic` assert).

---

## 5. THE PREDICTION — ALL THREE BRANCHES REGISTERED BEFORE THE RUN

**What is known: one measurement, on the coarsest grid, on a different scheme set.** R10-L3
(`linearUpwind`): RMS −32.8 % of a grid level, bias −64.2 %, S2 satisfied at η 0.65, S1 failed
by 2.6×/6.2×. **What is not known: anything about L2 or L1 under `transonic no`.**

- **(a) S2 HOLDS ACROSS THE FAMILY.** All three levels clear S2 at both stations and the S1
  limbs improve monotonically → the lead is real and resolution-robust. **If all twelve
  conditions clear, ADDENDUM 3 clause 1 opens the triple.** *This document does not expect
  twelve; it expects at most improvement.*
- **(b) S2 HOLDS ON L3 AND IS LOST ON L1.** **Registered now as a FINDING, not a
  disappointment:** a formulation benefit that disappears under refinement is a
  **resolution-dependent artefact**, and it would mean R10's result was a coarse-grid effect
  that the parking record's A2.8 over-weighted. That is a real result about the lead and it is
  written down **before** the run so it cannot be read as a let-down afterwards.
- **(c) M6J-L3 DOES NOT REPRODUCE R10's DIRECTION against `L3_TVD`.** Then the effect is
  scheme-dependent as well, the lead is weaker than recorded, and **L2 and L1 are not run** —
  §7's cost is not spent chasing an effect the coarse level already failed to confirm.

**Branch (c) is checked first and gates the other two.**

---

## 6. THE CURE GATE — TRANSCRIBED UNCHANGED

**D1** ≥ **0.1401**; **D2** ≥ **0.0880**; **D3** `x_shock_cfd` must leave **0.8851** forward.
**S1** ≥ 0.212 / ≥ 0.320; **S2** < 0.85; **B1** ≤ 0.050 on 12 rows; **B2** ≤ Δ_local.
Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, hash-verified in
the same shell invocation as each run; planted control must print `reader_saw_the_plant: true`.

🔴 **D2/D3 MISLOCATE AND THE DISCLOSURE TRAVELS:** the comparator resamples onto experimental
orifices whose intervals widen aft (**0.0501c at 0.4752 against 0.0701c at 0.8851**), so its
argmax picks the widest aft interval, not the steepest feature. **No reader may take `x_shock`
from it as a physical shock position** (parking addendum `801391c00`, Defect B). **S2 is a
`x_shock` limb and inherits this — which is precisely why §1 does not treat R10's single
satisfied S2 as evidence of a shock.**

---

## 7. COST (rule 12)

**Measured law, derived from the family's own three runs at 4 ranks:**
L3 `5.47/(15,360×2,800) = 1.272e-07`; L2 `69.87/(122,880×4,800) = 1.185e-07`;
L1 `949.53/(983,040×7,200) = 1.342e-07` core-min per cell-iteration. **Mean 1.27e-07**, and
R10 measured `transonic no` at the same stage-2 cost as `transonic yes` (5.47 vs 5.47).

| level | cells × iterations | **predicted core-min** | wall at 4 ranks | **cap** |
|---|---|---:|---:|---:|
| M6J_L3 | 15,360 × 3,000 | **5.9** | 0.02 h | **17.7** |
| M6J_L2 | 122,880 × 5,000 | **78.0** | 0.33 h | **234** |
| M6J_L1 | 983,040 × 8,000 | **998.8** | 4.16 h | **2,996** |
| **total** | | **1,082.6** | | **3,248** |

**Caps are 3× the prediction, which covers the worst ratio this family has ever measured —
R9's ×2.65 against an estimate of ×1.6.** A crossing grades the row `NOT A RESULT`; the cap is
never raised; **nothing is killed on spend or clock.** `cost_basis`: **MEASURED** in
core-minutes from each run's logs; dollars **DERIVED, NOT MEASURED** at $0.0513/core-h
→ ≈ $0.93 for the family. **Checkpoints every 200 iterations** (`writeInterval 200`,
`purgeWrite 2`) — on L1 that is ≈ 6 minutes of wall, well inside the 30-minute requirement.
**`memory_footprint_gb` per level, transcribed from the frozen R1 table: L3 0.5, L2 1.0,
L1 4.0** — declared, not measured, as that table says of itself. **R9's gate-B omission is not
repeated.**

---

## 8. WHAT THIS DOES NOT DO

1. **Does not reopen M6I** (§0) or alter any frozen gate, band, cap or label.
2. **Does not reinterpret ADDENDUM 3** — §1 quotes its four-condition bar and accepts clause 2
   as the expected outcome.
3. **Does not carry R9's correctors or R8's SST forward** (§4).
4. **Does not claim R10's result generalises** — §5 registers all three branches including the
   two that say it does not.
5. **Does not run L2 or L1 if branch (c) fires** (§5).
6. 🔴 **Does not fix the known-false `LAUNCH.log` line.** The launcher hard-codes
   `SA transonic=yes equations.p=1` in an echo and **will print `transonic=yes` on every M6J
   run**, directly under the widened assert's truthful `registered transonic formulation: no`.
   It is a measurement script and not this lane's to edit. **No successor may read that log
   line as evidence of this act's formulation.**

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
No agent's message is Sanaa's consent. Submissions parked.*
