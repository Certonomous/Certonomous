# T25RF — numerics feasibility probe for the resolved-channel conjugate case

**THIS IS AN UNGATED FEASIBILITY RUNG. IT HAS NO GATE, NO THRESHOLD, NO BAND AND
NO PRE-REGISTERED LABEL. IT PRODUCES NO VERDICT.**

`VERIFICATION_CHARTER.md` **§2m** applies in its exact terms and its price is
accepted in full:

> A feasibility rung's output is not a verdict and may not be reported as one. It
> may emit **no** word from the fixed vocabulary — not `PASS`, not `GATE REACHED`,
> not `GATE FAIL`. Its numbers are reportable as **observations** and **nothing may
> be cited from it as a result.**

Four consequences, stated flatly because each one is the kind of thing that gets
misread later:

1. **T25RF is NOT run under the T25R registration, and NOT under any future T25R2
   registration.** It is its own rung. It **closes no gate** belonging to any other
   registration, and it does not start any other registration's freeze clock or
   consume its first-compute event. A future T25R2 that wants a verdict freezes its
   own pre-registration and **runs again** — the fields this probe leaves on disk
   are evidence about the numerics and may *inform* that registration; they are not
   that registration's answer (§2d, §2m.2).
2. **Nothing from T25RF may reach a demo screen or be quoted as a result** —
   no Act C surface, no table cell, no figure, no headline number.
3. **T25RF touches no existing evidence.** `T25R_L1`, `T25R_L2` and
   `T25R_L2_DT025` are the record of the 04:09Z divergence and are read-only to
   this rung. All probe work lives in
   `verification/runs/T-family/T25RF_runs/`.
4. **T25RF edits no frozen file.** Not `T25R_PREREGISTRATION.md`, not
   `analyse_t25R.py`, not `mark_done_t25R.py`, not `run_one_t25R.sh`, and not
   `build_t25R.py` (which is under a live rule-6 referral and is neither committed,
   reverted nor further edited here — the probe case is built by copying the
   already-built L1 mesh).

---

## 1. What is being probed, and why

The 04:09Z `T25R_L1` run aborted at `Time = 1.5` with
`FOAM FATAL ERROR: Negative initial temperature T0: -14.46`, rc=134, after three
timesteps. The build itself measured correct on every geometric and flux count.
The question this probe answers is **narrow and purely numerical**: *what solver
settings, if any, let this case advance stably at the registered `deltaT` 0.5 and
Co ~ 1600?*

### 1.1 The mechanism, read out of the v2606 source BEFORE the probe was written

This is recorded here, pre-compute, because it determines the arms and because it
**refutes the hypothesis the probe was commissioned to test.** The commissioning
hypothesis was that `system/fvSolution` registers **no** `relaxationFactors` and
that the PIMPLE outer loop therefore degenerates into an unrelaxed SIMPLE. That
premise is false as stated, and the true mechanism is narrower:

- `T25R_L1/system/coolant/fvSolution` **does** register relaxation:
  `fields { "p_rgh" 0.7; }` and `equations { "(U|h|k|omega)" 0.9; }`.
- `T25R_L1/system/fvSolution` **does** register `PIMPLE { nOuterCorrectors 5; }`,
  and the log shows exactly five outer sweeps per step.
- `chtMultiRegionFoam.C:111` sets `const bool finalIter = (oCorr == nOuterCorr-1)`;
  `fluid/solveFluid.H:3` then calls `mesh.data().setFinalIteration(true)` for that
  sweep and clears it at `:37`.
- `fvMatrix::relax()` (`src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.C:1249`)
  resolves its relaxation key as `psi_.select(mesh.data().isFinalIteration())`, and
  `GeometricField::select(bool)`
  (`src/OpenFOAM/fields/GeometricFields/GeometricField/GeometricField.C:1179`)
  returns `name() + "Final"` when that flag is set.
- OpenFOAM keyword regexes match in full, so **`"(U|h|k|omega)"` does not match
  `UFinal` or `hFinal`.** `UEqn.relax()` and `EEqn.relax()` therefore find **no
  entry** on the fifth sweep and apply **no relaxation at all**.
- `p_rgh.relax()` and `turbulence.correct()` run in `chtMultiRegionFoam.C`'s
  coupled branch **after** `solveFluid.H` has already cleared the flag, so `p_rgh`,
  `k` and `omega` stay relaxed on every sweep including the last.

**So the failure is not "no relaxation registered". It is that momentum and energy
are relaxed on sweeps 1-4 and UNRELAXED on sweep 5, and at Co ~ 1600 the `1/dt`
term contributes almost nothing to the momentum diagonal, so the single unrelaxed
sweep has no diagonal dominance left to stabilise it.** The `T25R_L1` log carries
this signature directly: continuity `sum local` sits at O(1e-2 - 1e-1) on sweeps
1-4 of `Time = 0.5` and jumps to 1.135 on sweep 5; at `Time = 1.0` it is 3.609 on
sweep 4 and 125.93 on sweep 5, with `Min T` falling from 288.21 to -73.54 across
that same sweep.

The frozen `T25R` `fvSolution` comment names this behaviour deliberately — "the
FINAL outer sweep is unrelaxed by omission, which is what makes the last-sweep
initial residual of section 3.5 a meaningful convergence measure rather than a
relaxation artefact". **That choice is the thing under test here.** A consequence
to be reported honestly if an arm holds: relaxing the final sweep weakens the
`T25R` §3.5 convergence measure, and any registration that adopts it owes a
replacement measure.

---

## 2. The probe case

- Built by copying the already-verified `T25R_L1` two-region mesh
  (16608 cells, 24 cells across the gap, dx 2.5 mm, non-orthogonality 0,
  inlet area 0.021 m2, mdot 0.2016 kg/s). **The mesh is not rebuilt and
  `build_t25R.py` is not run.**
- **`endTime` 30 s at `deltaT` 0.5 — 60 steps.** The reference case died at
  t = 1.5, so 60 steps is twenty times the distance to the known failure and is
  ample to separate "stable" from "diverging".
- **Loads: Sanaa's 2026-09-01 04:20Z volumetric loads, NOT the loads frozen into
  `T25R_L1`.** Applied to the `module` region as a `scalarSemiImplicitSource` on
  `h`, `volumeMode specific`:
  - `q''' = 1.0e5 W/m3` for `0 <= t < 60 s`
  - `q''' = 2.5e4 W/m3` for `t >= 60 s`
  The frozen `T25R_L1` values (70000 / 2800 W/m3) are **not** used: probing the
  old loads would prove the wrong thing. Since `endTime` is 30 s the probe sits
  entirely inside the takeoff branch at 1.0e5 W/m3, which is the more demanding
  of the two.
- Everything else — mesh, thermophysical properties, boundary conditions,
  `fvSchemes`, `nOuterCorrectors` where unvaried, function objects — is copied
  unchanged from `T25R_L1`.

## 3. What is varied — the arms, run SEQUENTIALLY, cheapest first, STOPPING at the first arm that holds

| arm | change relative to `T25R_L1` numerics |
|---|---|
| **A0** | none (registered numerics: relaxation on sweeps 1-4 only, `nOuterCorrectors 5`), new loads. Confirms the crash reproduces and is not an artefact of the old loads. |
| **A1** | final-sweep relaxation added to `system/coolant/fvSolution`: `fields { p_rgh 0.3; p_rghFinal 0.3; }`, `equations { U 0.7; UFinal 0.7; h 0.7; hFinal 0.7; "(k\|omega)" 0.7; "(k\|omega)Final" 0.7; }`. `nOuterCorrectors` stays 5. |
| **A2** | A1 plus `nOuterCorrectors 10` in `system/fvSolution`. |
| **A3** | *only if A1 and A2 both fail:* `frozenFlow true` in the coolant `PIMPLE` dict. |

**A3 is a DEPARTURE and is flagged as one if it is reached.** The `T25R`
pre-registration §3.3 declined `frozenFlow` by name and on the record, as a
stronger approximation than its quasi-steady framing. If `frozenFlow` turns out to
be the only thing that runs, that is a significant physical finding about the case
and is reported as a departure requiring disclosure in any future registration —
never adopted quietly.

## 4. How the probe is READ — these are READING CRITERIA, NOT GATES

**No verdict attaches to any of them.** They exist so that "held" and "did not
hold" mean the same thing to a later reader. An arm is called *held* when all three
observations are true over the full 60 steps:

- **(a) `Min T` in the coolant region stays above 273 K for the whole probe** and
  the run reaches `Time = 30` without a fatal error.
- **(b) the last-sweep initial residuals for coolant `p_rgh`, `Ux` and `h` fall
  below 1e-6.**
- **(c) continuity `sum local` does not grow monotonically** across the probe.

Criterion (b) is the strictest of the three and may well not be met inside 5-10
outer sweeps during a strong thermal transient even by an arm that is perfectly
stable. **Missing (b) while meeting (a) and (c) is reported as exactly that — a
stable arm with an incompletely converged outer loop — and is not called a
failure.** Whatever is measured is reported; none of these three lines is allowed
to become a verdict.

## 5. COST — cap, basis, and the stop rule

The unit is **core-minutes** (wall s x ranks / 60), per `CLAUDE.md` rule 12 and
`COMPUTE_BUDGET_CHARTER.md`.

**Basis.** The `T25R` registration priced its L1 POINT case at **14.14 core-min for
1800 steps** at `nOuterCorrectors 5`, i.e. **0.00786 core-min/step**. That is a
pre-registered estimate, not a measurement: the 04:09Z run died at 6 s and measured
only 0.100 core-min, which prices nothing.

**Predicted, at 1 rank:**

| arm | steps | outer sweeps | predicted core-min |
|---|---|---|---|
| A0 | 60 (expected to abort far sooner) | 5 | <= 0.5 |
| A1 | 60 | 5 | ~0.5 |
| A2 | 60 | 10 | ~0.9 |
| A3 | 60 | 5 | ~0.3 |
| **predicted total** | | | **~2.2** |

**CAP: THE WHOLE PROBE — ALL ARMS TOGETHER — IS CAPPED AT 30 CORE-MINUTES.** The
cap is set an order of magnitude above the prediction because a stiff arm can pay
many more GAMG iterations per sweep than the basis assumed; it is not an
expectation. Per-arm `timeout` is 480 s (8 core-min at 1 rank) and the running
total is checked against the 30 cap before each arm is launched.

**The cap STOPS the probe. It does not get a new budget** (rule 12). If the running
total reaches 30 core-min the remaining arms are not launched, and that stop is
reported as its own finding rather than folded into any cost ratio. Waste is
reported separately and never absorbed.

**Dollars, if anyone derives them:** at the recorded c7a.4xlarge rate of
$0.0513/core-h, 30 core-min is $0.026. That figure is **derived, not measured** —
this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Estimate-versus-actual.** Per rule 12's calibration clause, the actual
core-minutes per arm and in total are compared against the table above at probe
completion and the ratio reported with its attribution.

## 6. Mechanics

- Each arm runs under a detached wrapper that captures the solver's own `$?`
  **inside** the wrapper, on the line after the solver runs — never around the
  `setsid` line, which exits 0 for every outcome.
- `0` is staged from `0.orig` per arm and `0/module/T` is touched last, immediately
  before launch, so nothing is written into the case between that touch and the
  solver start.
- Each arm writes `STATUS.<ARM>` beside its `log.solve`, inside its own case
  directory.
- Arms are strictly sequential. The probe stops at the first arm that holds.

---

*Written and committed before any T25RF compute. Ungated: no gate, no threshold,
no band, no label, no verdict.*

---

## Addendum A1 — 2026-09-01, added AFTER arms A0/A1/A2 and BEFORE arm A2T

**Lines whose number changed above this section: 0.**

This addendum adds one arm. **It alters no gate, no threshold, no band, no label
and no cost cap** — there are none to alter, and the 30 core-min probe cap is
unchanged and still binding. It is recorded before the arm it authorises runs.

**The condition, and how it was checked.** Arms A1 and A2 both ran to
`Time = 30` with `rc = 0`, and the reader
`verification/runs/T-family/T25RF_runs/read_arm_t25RF.py` measured, over each of
them, that **44 % (A1: 266 of 600) and 51 % (A2: 608 of 1200) of all `p_rgh`
solves terminated at GAMG's default `maxIter` of 1000**, having stalled at a
final residual of roughly 4.4e-9 against the registered absolute `tolerance` of
1e-9. The solver is therefore paying a thousand iterations per solve to close a
gap it cannot close, on roughly half of all pressure solves, and that is the
dominant term in both arms' cost. `CLAUDE.md` rule 12 requires waste to be
reported rather than absorbed; this arm measures whether it is **removable**,
so that a future T25R2 can be priced against its 600 core-min cap on a number
that is not half stall.

**Arm A2T:** arm A2's numerics exactly, with the coolant `p_rgh` and
`p_rghFinal` absolute `tolerance` relaxed **1e-9 -> 1e-8**. Nothing else changes:
same mesh, same loads, same relaxation, same `nOuterCorrectors 10`, same
`endTime`.

**How A2T is read.** The same three criteria of section 4, plus one comparison
that is the point of the arm: **the last-sweep `Min/max T` at `Time = 30` must
agree with A2's to within 1e-4 K.** If it does, the stalled iterations were
buying nothing and the tolerance is the cost bug; if it does not, the tolerance
is load-bearing and must stay at 1e-9 and be paid for. Either way this remains an
**ungated observation and produces no verdict.**

**Cost.** A2T is drawn from the SAME 30 core-min probe cap, which is not raised.
Spend before this arm: **11.700 core-min** (A0 0.083 + A1 3.650 + A2 7.967).
Headroom: **18.300 core-min**. A2T is predicted at ~4 core-min and is launched
under an 600 s timeout that the runner clamps to the remaining headroom.

**Arm A3 (`frozenFlow`) is NOT reached and is NOT run.** Its registered trigger
was "A1 and A2 both fail". Both held criteria (a) and (c) and ran to `endTime`
without a fatal error. The `T25R` section 3.3 refusal of `frozenFlow` therefore
stands untouched, and this probe records **no departure**.
