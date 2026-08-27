# F26D — RINGLEB DISCRIMINATING ARM: PRE-REGISTRATION, 2026-08-27

**THIS IS A DIAGNOSTIC, NOT A LADDER, AND IT DOES NOT RESCOPE F26.**
F26_RINGLEB remains **BLOCKED** (`SOLVER_ADMISSION_ARM_2026-08-27.md`). Nothing in this
document unblocks it, rescopes it, or establishes a rescope cost. **The rescope cost is NOT
established and stays not established until this arm answers** — and answering it is not the
same as paying it. No result here may be promoted into F26's registration. Nothing is sent,
filed, uploaded or submitted (rule 7).

**Frozen before compute (rule 2).** Gate, thresholds, caps, labels and predictions below are
fixed at this document's commit. The run root is ABSENT (§8). Amendments before first compute
must state the condition and how it was checked; after first compute, dated addenda only.

---

## 1. The question, and why it is worth 7 core-minutes

`SOLVER_ADMISSION_ARM_2026-08-27.md` §4 ends: *"Which of the three constituents — zero
viscosity, strong wall curvature, or high subsonic Mach — carries the failure is not resolved
here and is the obvious next question."* This arm asks exactly that question and nothing else.

The three candidate causes, named before compute:

- **C_mu — zero viscosity.** `mu = 0`, so the cell Reynolds number is infinite at every level
  and the discretisation carries no physical dissipation to damp a growing mode.
- **C_kappa — strong wall curvature.** The Ringleb walls are strongly curved streamlines;
  max |kappa| = 0.4544 on the inner wall (measured, §3).
- **C_M — high subsonic Mach.** Max M = 0.8567 on the inner wall (measured, §3), against
  M = 1 at V = 0.9129.

**An arm whose every outcome is consistent with all three is not worth 5 core-minutes.** §4
states what each candidate predicts and which observation separates it. §5 states, plainly,
which pair this arm **cannot** separate and why that is a property of Ringleb flow rather than
a shortcut taken here.

## 2. Ladder classification (Sanaa §3, L0–L7), stated explicitly

**This arm is an L0 DIAGNOSTIC — "L0 diagnose first", which the standing directive makes
MANDATORY AND FIRST.** L0 is defined as *a reading, not a run*; this arm obtains that reading
by running controlled variants of the problem, because no reading of the existing logs
separates the three candidates. It is registered as an **L0 diagnostic extension**, and its
outputs are L0 readings.

**It is explicitly NOT an L1–L7 repair step and may not be promoted to one.**

- Arm **AV** adds viscosity, changing the governing equations from Euler to Navier–Stokes.
  That is an **L7 formulation** change. It is run here as a *diagnostic probe only*. **The
  exact Ringleb solution is an exact solution of the EULER equations and is NOT an exact
  solution of Navier–Stokes**, so AV's error norms against it are meaningless and are not
  graded; only AV's **completion** is read.
- Arm **AM** changes the streamline band, i.e. the **problem** — a different Mach and a
  different geometry. It is not on the L0–L7 ladder at all, because that ladder repairs a
  registered problem and this substitutes an easier one on purpose.

**ANTI-GAMING (Sanaa §3, absolute), acknowledged and applied:** neither AV nor AM may become
F26's configuration. Model, scheme class and formulation are never selected by agreement with
the reference. **Every arm run is reported, including any that fails to build or is abandoned**
— a single reported arm out of several run is the signature the clause exists to catch. If a
repair follows from this reading it is a **separate registration**, frozen on its own.

**One change per run (Sanaa §3), with each arm's reference named:**

| arm | reference | THE ONE CHANGE |
|---|---|---|
| **A0** | — (reference arm) | none; baseline |
| **AV** | A0 | `mu` 0 -> 1e-3 in `constant/thermophysicalProperties` |
| **AM** | A0 | streamline band `k` [0.5, 0.8] -> [0.277154, 0.35] |

Wall boundary conditions, schemes, relaxation, solver, initial field (the exact field) and
iteration count are **identical across all three arms**. In particular AV keeps **slip walls**:
switching to no-slip would be a second change and would add a boundary layer the exact field
does not contain.

## 3. The measured design, computed at registration time from `exact_f26.py`

Wall metrics on the bounding streamlines, over |phi| <= 2.4, 4001 samples, curvature by
finite difference in phi:

| arm | band `k` | d(psi) | inner wall max M | inner wall max abs kappa | inner arclen |
|---|---|---|---|---|---|
| **A0 / AV** | [0.500000, 0.800000] | 0.7500 | **0.8567** | **0.4544** | 8.1423 |
| **AM** | [0.277154, 0.350000] | 0.7500 | **0.3544** | **0.1151** | 15.0694 |

`d(psi)` is **matched to four decimal places by construction** so the duct's stream-function
width is unchanged and width is not a third varying quantity.

**Cell Reynolds number for AV** (`mu = 1e-3`, `rho ~ 0.85`, `q ~ 0.7`, `h` = inner arclen /
n_along): L1 202, L2 101, L3 50, L4 25. Finite at every level and falling under refinement,
which is the property C_mu says is missing.

## 4. THE DISCRIMINATION — registered before compute

**The observable is `N*`, the stability threshold**: the coarsest registered level at which the
arm FAILS. It is a completion property and needs no exact solution, no Richardson
extrapolation and no error norm.

**A level COMPLETES iff all of:** `rc = 0`; an `End` line in the solver log; last time ==
`endTime` (4000); `ExecutionTime` count == 4000. Anything else — SIGFPE (`rc=136`), FOAM abort
(`rc=134`), negative temperature, or a short log — is a FAILURE. `N* = NONE` iff all four
levels complete.

**The grid ladder, `r = 2` in each direction** (cells x4 per step):

| level | n_along x n_across | cells |
|---|---|---|
| L1 | 24 x 4 | 96 |
| L2 | 48 x 8 | 384 |
| L3 | 96 x 16 | 1,536 |
| L4 | 192 x 32 | 6,144 |

**On `r`, and why 2 is sufficient here.** `r = 2.000` exactly, per direction, between every
adjacent pair. The prior arm's model check used `r21 = 1.125`, and cfd's predecessor
downgraded a "9 % error floor" claim on the ground that a triple at that ratio cannot
extrapolate — a downgrade since vindicated, because `scripts/roache_triple.py` accepts
`r21 = 1.125` as CONVERGING with no minimum-`r` guard. **That instrument gap is verification's
to close and is not touched here.** This arm is immune to it by construction: **`r = 2` is at
or above every minimum-`r` threshold in general use (Roache's own recommendation is
`r >= 1.3`), and, decisively, NO RICHARDSON EXTRAPOLATION IS PERFORMED BY THIS ARM AT ALL.**
`grade_f26d.py` does not call `roache_triple.py`, computes no observed order, and reports no
GCI. The threshold `N*` is an ordinal reading on a bracketing ladder; `r` sets only how tightly
the bracket is drawn. **No claim here depends on any `r`.**

### 4.1 What each candidate predicts

| candidate | prediction for **AV** (`mu` raised) | prediction for **AM** (band lowered) |
|---|---|---|
| **C_mu** | `N*` moves UP — AV completes all four levels | no effect: `N*(AM) = N*(A0)` |
| **C_kappa** | no effect: `N*(AV) = N*(A0)` | `N*` moves UP — AM completes all four |
| **C_M** | no effect: `N*(AV) = N*(A0)` | `N*` moves UP — AM completes all four |

### 4.2 The registered reading, fixed before compute

| AV | AM | READING |
|---|---|---|
| completes all 4 | fails at `N*(A0)` | **C_mu carries it.** Curvature and Mach are neither necessary nor sufficient. |
| fails at `N*(A0)` | completes all 4 | **{C_kappa OR C_M} carries it; C_mu does not.** Not separated further by any knob in this arm — see §5. |
| completes all 4 | completes all 4 | **AMBIGUOUS, and reported as such.** Both are sufficient repairs; neither is shown necessary. No candidate is eliminated. |
| fails | fails | **NONE of the three carries it.** The cause lies in the solver / boundary treatment / scheme, a **fourth candidate this arm did not register**. A decisive negative and the most informative outcome available. |

### 4.3 A0's own registered prediction, which is also the arm's validity check

**A0 completes L1 (96) and L2 (384) and FAILS at L3 (1,536).** Basis: the prior arm measured
the threshold between 600 and 864 cells; L2 = 384 lies below it, L3 = 1,536 above it.

**If A0 completes L3, this arm is `NOT A RESULT`** — the reference the two probe arms are read
against would have moved, and AV/AM would be compared to nothing. This is registered as a
refusal condition, not as a finding to be explained after the fact.

## 5. WHAT THIS ARM CANNOT SEPARATE, stated plainly

**It cannot separate C_kappa from C_M by any knob, and that is a property of Ringleb flow, not
a corner cut here.** Measured at registration time over `k` in [0.3, 0.9]: max Mach and max
wall curvature are **both strictly monotone increasing in `k`**, and **both attain their
maximum at `phi = 0`** — so no choice of `K_MIN`, `K_MAX` or `PHI_END` lowers one while holding
the other. Cutting `PHI_END` to 0.8, 1.2, 1.6 or 2.0 changes **neither** maximum. Arm AM
therefore moves them **together**, by construction, and is registered as a **joint** probe.

**So, honestly labelled: this is a PARTIAL discriminator.**

- It **separates C_mu from {C_kappa, C_M}** — cleanly, by a single knob.
- It **separates {C_kappa OR C_M} jointly from "none of the three"** — cleanly.
- It **does NOT separate C_kappa from C_M** by any knob.

### 5.1 A weaker, secondary separation — registered as secondary, not as a gate

For `mu = 0` Euler flow there is **no intrinsic length scale**: the equations are invariant
under `x -> s x`, so wall curvature cannot enter the discrete problem on its own — it enters
**only** through the dimensionless product `kappa * h`. Refining the mesh **reduces** it.

**Therefore, if C_kappa carried the failure, the failure would have to EASE under refinement.**
The prior measurement says the opposite: the configuration converges below 600 cells and fails
above 864. If A0's §4.3 prediction holds, that is **evidence against C_kappa**, and combined
with AM completing it points to **C_M**.

**This is registered as a SECONDARY reading and is weaker than AV's knob**, because it rests on
a physical argument (scale invariance) rather than on a controlled change. It may support a
conclusion; **it may not carry one alone**, and it is never reported as if it were a knob.

## 6. Cost, cap and ranks

- **Ranks: 1** (serial) for every run. `decomposePar` is never invoked.
- **Estimate: 6.8 core-minutes.**
- **Cap: 10.2 core-minutes = 1.5 x the estimate.** Checked after every run in
  `ClockTime x ranks / 60`; a crossing HALTS the launcher at exit 3 with unrun levels left
  PENDING. **The cap is never raised** (rule 12: an overrun stops the run).
- **`cost_basis`: derived, NOT MEASURED.** 3 arms x (96 + 384 + 1,536 + 6,144) cells x 4,000
  iterations = 97.92 M cell-iterations, at 3.55 us/cell-iteration — a rate read from ONE lab
  record of a DIFFERENT case (`verification/runs/FPE_DIAG_runs/BL1/log.simpleFoam`: 3,520
  cells, 2,000 iterations, serial, ClockTime 25 s) — = 347.6 s = 5.79 core-min serial, plus 12
  mesh builds (blockMesh + checkMesh + postProcess) at ~5 s = 1.0 core-min. Total 6.8
  core-min. **This is an upper estimate for the completing case: an arm that aborts costs
  less.** At the owner-stated $0.0513/core-h this is **$0.0058 estimated and $0.0087 at cap,
  reported-by-owner and NOT MEASURED — the box cannot read its own billing**
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Estimate-versus-actual calibration is owed at completion** (rule 12) and lands in
  `docs/COST_CALIBRATION.md`.

## 7. Gate

**There is no PASS/GATE FAIL gate on a physical quantity, because this arm measures no physical
quantity.** Its product is the §4.2 reading. The registered verdict vocabulary for the arm:

- **GATE REACHED** — A0 satisfies §4.3 and both probe arms ran to a definite `N*`, so §4.2
  returns one of its four readings.
- **NOT A RESULT** — A0 completes L3 (§4.3), or any arm fails to build, or any run is
  incomplete in a way the completion rule cannot classify.
- **BLOCKED** — the box cannot run the arm at all.

**F26_RINGLEB's own status is untouched by every one of these outcomes. It stays BLOCKED.**

## 8. Absence condition (rule 2)

Checked **2026-08-27T19:34:38Z** (`date -u`, stamp repeated in the freeze commit message):

- `test -e /home/ubuntu/Certonomous/verification/runs/F26_RINGLEB_runs` -> **ABSENT**
- `test -e /home/ubuntu/Certonomous/verification/runs/F26D_runs` -> **ABSENT**
- No `RC.txt`, no `log.*` and no numeric time directory anywhere under `cases/F26_RINGLEB/`.

`run_f26d.sh` creates the run root and **REFUSES** any pre-existing `0/`, numeric time
directory or `processor*` under a destination it is about to build.

## 9. Instrument rules observed

`grade_f26d.py`: zero `ast.Assert` nodes in the shipped path (L-332), `--selftest` rc 0,
`python3 -O` rc 2 **at module entry before any work**, and a **planted control driven in BOTH
directions through the real reader** (standing rule 3) — a completing log is mutated to carry
an abort signature and must be read as FAILED, and a failing log is mutated to carry a
completion signature and must be read as COMPLETED. A reader never shown able to return the
other answer is not evidence. Every refusal is a `raise` or `sys.exit`, never an `assert`.
