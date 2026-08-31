# VMFL003-M2 arms C and D — THE BUDGET/KILL REPAIR IS REFUSED, AND THE MEASUREMENT THAT REFUSES IT

**Author:** `ansys-lane-opus`, 2026-08-31, under the `ansys-verification-supervisor`'s
BUDGET/KILL brief and Sanaa's ordering directive of 2026-08-31
(`etc/sessions/2026-08-31T2130Z_sanaa_ansys_fix_order.md`, commit `733d9403`).

**ZERO COMPUTE. No solver was started.** Every number below is read from artifacts already
on disk under `verification/runs/ansys_verification/VMFL003_M2/`. **No pre-registration was
drafted, nothing was frozen, and no queue entry was filed** — this document records why.

**NOT FILED ANYWHERE** (`CLAUDE.md` rules 7, 8).

---

## THE CONCLUSION, FIRST

**Rows 11 and 12 of `COVERAGE_ROWS.md` are correctly `NOT A RESULT`, and `BUDGET/KILL` is
the correct PROXIMATE cause. It is not the BINDING cause.** A successor registration whose
only registered change is a correctly-sized cap is **provably incapable of converting either
row**, and the proof needs no assumption about what the unfinished iterations would have
done.

**The binding cause is the frozen iterative-convergence residual clause** — the same clause
that already accounts for rows 6, 9 and 10, all three of which are classed `GATE-DESIGN`.
Arms C and D fail it on levels that **ran to their own `endTime` and are complete on disk**.

Under Sanaa's ordering this work therefore belongs at position **5 (gate design)**, not
position 1. **It is handed back rather than executed.**

---

## 1. THE RUNS WERE NOT DIVERGING — and they were not converging either

**MEASURED**, from each level's own `log.simpleFoam`, anchored `Time = ` and
`Initial residual = ` patterns.

Both killed levels had been **flat at a fixed residual floor for thousands of iterations**
when the cap fired:

| killed level | field | flat at | from iteration | to kill at |
|---|---|---|---|---|
| `D_kOmegaSST/L3_1000x5` | `Ux` | 2.95–2.97e−10 | 228 | 5949 |
| `D_kOmegaSST/L3_1000x5` | `omega` | 1.75–1.91e−08 | 595 | 5948 |
| `C_RNGkEpsilon/D_500x3` | `Ux` | 1.4798–1.4800e−08 | 409 | 4085 |

**Nothing in this rung diverged.** Across all 19 executed levels of all four arms, every
level either settled or plateaued at bounded amplitude. The single level with a genuine
convergence defect is `D_kOmegaSST/L1_250x5`, which **completed** at `endTime 15000` with
`Ux` stuck at 2.340e−05 and Δp oscillating with a peak-to-peak of 7.776e−02 Pa (3.821 ppm)
over its last 7 500 iterations — plateaued, not descending, not diverging.

## 2. THE KILL REMOVED NOTHING FROM THE GRADED QUANTITY

The gate quantity is `dp_pa = RHO * (<p>_inlet − <p>_outlet)`
(`grade_vmfl003_m2.py:301-315`, `RHO = 1.225`), read from
`postProcessing/{pInletMonitor,pOutletMonitor}/0/surfaceFieldValue.dat`.

**MEASURED — iteration at which Δp first comes within a relative tolerance of its own final
value and stays:**

| level | within 1e−6 rel | within 1e−9 rel | ran to |
|---|---|---|---|
| `D_kOmegaSST/L3_1000x5` (KILLED) | **171** | **268** | 5948 |
| `A_kEpsilon/L3_1000x5` | 200 | 291 | 22000 |
| `C_RNGkEpsilon/L3_1000x5` | 193 | 298 | 22000 |
| `C_RNGkEpsilon/L2_500x5` | 133 | 207 | 18000 |

**Arm D's killed level had its graded quantity final to one part in 10⁹ by iteration 268
and was killed at 5949.** 97.1 % of that level's 1662.74 s was spent after the answer had
stopped moving to 1 ppm.

**Rung-wide, MEASURED across all four arms and all 19 executed levels: of 141.025 core-min
consumed, 132.952 core-min — 94.3 % — was spent after the graded quantity had already
reached within 1 ppm of its own final value.** Reported under `CLAUDE.md` rule 12, which
requires waste to be named rather than absorbed.

**The cap was not too small for the physics. The registered `endTime` was ~80× larger than
the physics needed.**

## 3. AND A FINISHED RUN WOULD STILL BE `NOT A RESULT` — measured, not inferred

The frozen clause is `RESID_TOL = 1.0e-8` on each of a gated field list
(`grade_vmfl003_m2.py:134,420` — `p, Ux, k, epsilon`;
`grade_vmfl003_m2_omega.py:136,422` — `p, Ux, k, omega`).

**Final initial residuals at the end of the iterations actually executed:**

| arm / level | state | p | Ux | k | ε or ω | frozen leg |
|---|---|---|---|---|---|---|
| C / `L1_250x5` | **complete, `rc=0`, at `endTime`** | 9.955e−08 | 2.338e−06 | 3.657e−06 | 2.776e−06 | **FAILS ×4** |
| C / `L2_500x5` | **complete, `rc=0`, at `endTime`** | 2.311e−10 | 6.889e−09 | 2.127e−08 | 1.389e−08 | **FAILS on k, ε** |
| C / `L3_1000x5` | **complete, `rc=0`, at `endTime`** | 4.611e−10 | 9.478e−09 | 1.861e−08 | 7.967e−08 | **FAILS on k, ε** |
| D / `L1_250x5` | **complete, `rc=0`, at `endTime`** | 9.423e−07 | 2.340e−05 | 1.594e−05 | 6.223e−05 | **FAILS ×4** |
| D / `L2_500x5` | **complete, `rc=0`, at `endTime`** | 2.967e−09 | 5.127e−08 | 1.221e−07 | 1.116e−06 | **FAILS on Ux, k, ω** |
| D / `L3_1000x5` | killed at 5949/22000 | 1.780e−09 | 2.960e−10 | 3.822e−09 | 1.847e−08 | **FAILS on ω** |

**ARM C: all three Roache gate levels are COMPLETE on disk and all three fail the frozen
residual leg.** `CLAUDE.md` rule 5 step (1) — any level not iteratively converged →
`NOT A RESULT`. Arm C needs **not one further core-minute** to be shown ungradeable under
its frozen gate. The only level it lost is `D_500x3`, a **wall-treatment ladder diagnostic,
not a gate level**, and the supervisor's own `SUPERVISOR_TRIAGE_rc124.md` §Finding 2 already
established that level was **starved by the cap allocator** (36 s against its siblings'
1117 s for the identical mesh), not defeated by the solver.

**ARM D: L1 and L2 both ran to `endTime` and both fail the frozen residual leg.** The
disqualifier sits at the two COMPLETE levels. **Whatever `L3` does, arm D is already
`NOT A RESULT` under its frozen gate** — and finishing `L3` costs ~105 core-min.

**Only the last row of that table rests on extrapolation** (ω flat at 1.75–1.91e−08 across
iterations 595–5948 → `EXTRAPOLATED` to hold at 22000), and **the conclusion does not
depend on it.**

## 4. THE CLAUSE IS NOT MERELY UNMET — IT IS UNMEETABLE HERE

ε and ω park on a floor of 1.39e−08 to 7.97e−08 at **every level of every arm** and stay
there for thousands of iterations. Arms A and B ran the **full** registered `endTime` on the
full budget and hit the same floor (row #9: L3 ε = 2.494e−08; row #10: L3 k = 1.377e−07,
ε = 7.490e−08). The 1e−8 threshold sits **below the attainable fixed-point floor of the
ε/ω equation** in this configuration.

This is the defect the supervisor's brief names as standing requirement 11 — *a convergence
clause satisfiable across the whole range*. **It is not satisfiable at any budget**, so it
is not a budget defect.

**The measurement that makes the correct replacement clause easy to defend, when the team
reaches gate design:** Δp reaches within 1 ppm of its final value by iteration ≤ 300 at
every fine level and then does not move for 18 000–21 700 further iterations. A plateau leg
on the graded quantity is a far stronger convergence demonstration here than any residual
threshold, and it is **satisfiable**.

## 5. WHAT A CORRECTLY-SIZED CAP WOULD HAVE COST — recorded so the figure is not re-derived

`EXTRAPOLATED` from each level's own measured `ExecutionTime / lastTime` rate; siblings on
the identical mesh give the bracket. Serial, `ranks = 1`, so core-min = wall s / 60.

| | point | bracket |
|---|---|---|
| Arm C, complete all six levels | **48.6 core-min** | 46.9 – 50.0 |
| Arm D, `L3_1000x5` alone to `endTime 22000` | **105.6 core-min** | 102.5 – 106.8 |
| Arm D, complete all six levels | **131.9 core-min** | 126 – 146 |
| **Both arms** | **~180 core-min** | 173 – 196 |

Against the frozen `PER_ARM_CAP = 40`: arm C needs **1.45×**, arm D **3.3×**.
Derived cost at $0.0513/core-h (owner-stated; the box cannot read its own billing):
**$0.154 DERIVED**, not measured.

**The money is trivial and is not the objection.** The objection is that the 180 core-min
buys two rows already determined to be `NOT A RESULT` by §3 above.

**The arm-D upper bracket is not guaranteed.** Its `L3` ran at 0.2795 s/iteration against
the 0.0307 s/iteration arm A took on the *identical* mesh — **9.1×** — and the rate is not
stationary across that arm's own levels (L2 0.0196 → L3 0.2795). The supervisor's
`TRIAGE_ARM_D_BUDGET_STOP.md` hypothesis of a badly-converging inner linear solve is
untouched by anything here, and it means no honest upper bound on arm D exists without
first running the `VMFL007_R2` preconditioner sweep.

## 6. THE §12.2 ANSWER, WHICH CAPS THE CASE INDEPENDENTLY

Asked and answered before any freeze, per charter §12.2:

1. **The continuum model the solver discretises:** incompressible steady RANS — Reynolds-averaged
   Navier–Stokes with a two-equation eddy-viscosity closure (k-ε / RNG k-ε / realizable k-ε /
   k-ω SST) and an algebraic log-law wall function (`nutkWallFunction`).
2. **The model the reference is the exact solution of:** none. **21 744 Pa is the Moody-chart
   smooth-pipe branch** (VM2026R1 p. 19, Tables .03.1/.03.2) — an **empirical correlation**.
3. **SAME or DIFFERENT: `DIFFERENT`.**
   `VERIFICATION_CHARTER §2h.6.1 (v1.27, 2026-08-31, the exact-PDE rule)` names correlations
   explicitly among different-model references that *"CAP AT `GATE REACHED`, HOWEVER EXACT
   ITS OWN ALGEBRA."*
4. **Ceiling: `GATE REACHED`. `PASS` is unavailable for this case in any successor**, and
   none was sought. Charter §12.4 first bullet: no retrospective promotion.

## 7. THE CONTAMINATION THAT CLOSES THE DOOR ON A SUCCESSOR WRITTEN TODAY

Establishing §§1–5 required reading arms C's and D's graded values off disk. They are:

- `C_RNGkEpsilon/L3_1000x5` Δp = **20 451.523134950 Pa** — **−5.943 %** vs the 21 744 Pa reference
- `D_kOmegaSST/L3_1000x5` Δp = **20 349.105682540 Pa** — **−6.414 %** vs the same reference

Both sit outside the frozen ±2.5 % band, so both are `GATE FAIL` before rule 5 and
`NOT A RESULT` after it.

**Any new gate, band, threshold, cap, level, ceiling, label or convergence clause written
for these arms from now on is written by someone who has seen the answer.** `CLAUDE.md`
rule 2 and charter §11.2 are explicit that the freeze's entire evidentiary content is that
the gate could not have been fitted. **A successor registration for VMFL003-M2 arms C and D
cannot carry a changed convergence clause without forfeiting exactly that**, and the only
clause it could carry unchanged is the one §3 proves cannot be met.

**This is a one-way door and this lane is not walking through it.** Whether a successor is
possible at all — and on what terms — is the supervisor's ruling, and a clause change is a
threshold change, which `ESCALATION_CHARTER` §4.1 and D539 reserve to Sanaa.

## 8. A CORRECTION THIS INVESTIGATION OWES THE REGISTER

Register rows **#11 (L37)** and **#12 (L38)** both assert:

> *"NO `RC.txt` or `record.json` exists anywhere under `VMFL003_M2`" … "Rule 4's `rc = 0`
> conjunct is therefore UNEVALUABLE FROM DISK for this entire rung."*

**MEASURED: that is false.** `RUN_RC.txt` exists at **all 19 executed levels**, written
2026-08-25 16:47–19:05Z **during the runs**, and each records `rc=` explicitly —
`C/D_500x3 rc=124 … timeout_s=36`, `D/L3_1000x5 rc=124 … timeout_s=1663`, `rc=0` at the
other seventeen. The same supervisor's `SUPERVISOR_TRIAGE_rc124.md` (21:56Z the same
evening) **reads those very files** and tabulates rc for every level, so the register and
the triage document contradict each other.

The likely mechanism is a **filename mismatch** — the rows searched for `RC.txt` and
`record.json`; the launcher writes `RUN_RC.txt`. That is the shape charter §11.5 names: an
instrument reporting its own blind spot as a fact about the world.

**Rule 4's `rc = 0` conjunct IS evaluable from disk for this rung, and it fires**: `rc=124`
at exactly the two killed levels, which is `timeout`'s budget signature and independently
confirms the `BUDGET/KILL` proximate class. **The rows are not edited by this lane** — a
register row is the supervisor's, and rows 11 and 12 are frozen record. The correction is
reported for the supervisor to land.

## 9. WHAT IS CORROBORATED RATHER THAN FOUND

The M2 pre-registration **already declared** the anisotropy defect, before compute:
`PREREGISTRATION.md:57` — *"ladder (N_r = 3/4/5/6) moves it 1.7356 % — the model/wall
channel is ~2200× the axial"*; `:246-251` — the radial channel is *"unrefinable on this
case"* under `N-AV10` (R⁺ = 408 forbids a ratio-2 radial triple below Re ≈ 21 252);
`:330` — the GCI is emitted as *"an axial-channel diagnostic, not a certification"*.

**Independently re-measured here on the gate quantity**, and it confirms the frozen document:

| refinement direction | Δp movement |
|---|---|
| axial, `L2_500x5` → `L3_1000x5` (N_x 500→1000, N_r fixed 5) | **7.76 ppm** (arm A), 3.66–16.7 ppm across arms |
| radial ladder, N_r 3→6 at fixed N_x = 500 | **1.7233 %** (arm A) |

**Ratio 2 222× — against the frozen document's pre-registered ~2 200×.** The registration
was candid about its own limit and the limit is real. **This is not a new defect and the M2
registration is not faulted for it.** It is the reason the case's honest ceiling is
`GATE REACHED` on the referent ground of §6 *and* on the no-usable-triple ground, which
agree.

**One genuinely new observation, offered as a diagnostic and not as a gate finding.** The
`f_dev` friction-factor diagnostic is built from `pSlabA − pSlabB`
(`grade_vmfl003_m2.py:325`, `dpdx = RHO*(pa-pb)/SLAB_DX`). **MEASURED: that slab difference
is BIT-IDENTICAL between `L2_500x5` and `L3_1000x5` in all four arms** — A 6786.827268 /
6786.827268, B 6615.667596 / 6615.667596, C 6671.943356 / 6671.943356, D 6649.115728 /
6649.115728, i.e. d21 = 0 exactly — and the L1→L2 step is 0.052083 % in **all four arms to
six figures**. Fully developed pipe pressure is exactly linear in x, a linear field is
integrated exactly by the scheme on a uniform mesh, and the 500-mesh slab faces are a subset
of the 1000-mesh faces. **`f_dev` carries zero axial-mesh information by construction** and
is ungradeable as a triple — the class the supervisor's brief names as standing requirement
10, and the same class as VMFL038's τ_w and VMFL029's net wall heat flux. **The gate
quantity `dp_pa` is NOT so pinned** and does refine (d21 = 0.0745–0.338 Pa, ~7 700× the
iterative plateau noise of ≈2e−5 Pa), so the registered gate is sound on this point and only
the secondary diagnostic is affected.

---

## WHAT THIS LANE DID NOT DO, STATED PLAINLY

- **No pre-registration drafted, no comparator written, nothing frozen, no queue entry
  filed.** The twelve standing requirements were therefore **not** exercised to refusal —
  requirements 1–9 and 11–12 have **no** artifact behind them here and must not be reported
  as discharged. Requirement 10's conservation-identity test **was** run, on real bytes, and
  its result is §9's last paragraph.
- **No run was launched and no verdict was issued.** Rows 11 and 12 stand exactly as they
  are, un-re-graded, per `CLAUDE.md` rule 12.
- **No register row, charter clause or frozen file was edited.**
