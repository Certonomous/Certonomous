# A3GC-AR1C — PRE-REGISTRATION

**Frozen 2026-09-12. Written BEFORE any AR1C compute. SUBMISSIONS PARKED.**

AR1C is a **continuation** of A3GC-AR1 carrying **one changed equation**. It exists to
decide a single question that AR1's own row could not: **is AR1's `nuTilda` plateau at
1.0089e-06 set by leftover linear-solver error, or is it where this configuration lands?**

**A3GC-AR1's `NOT A RESULT` verdict (`cd1609cfb`) STANDS and is NOT rewritten.**
AR1C produces a **new row**. AR1's run root is read-only evidence and was not written into.

---

## 1. WHAT AR1 MEASURED

AR1 completed to Time 6000, rc=0, fields at 0/2000/4000/6000, and graded
**NOT A RESULT** on exactly one gate:

| quantity | AR1 value | registered gate | status |
|---|---|---|---|
| `nuTilda` initRes | **1.008859568e-06** | <= 1e-06 | **FAIL by +0.886 %** |
| `U0` `U1` `U2` `he` `p` initRes | all <= 1e-06 | <= 1e-06 | OK |
| CD | 0.02300300328 (+0.032 % vs anchor 0.0229956) | +-2 % | OK |
| CL | 0.3131159742 (+0.000 % vs anchor 0.3131159) | +-2 % | OK |

## 2. THE PLATEAU IS REAL, AND IT IS NOT DRIFTING TOWARD THE GATE

Measured on the **graded series** — the `nuTilda initRes:` lines the frozen comparator
reads (`a3gc_grade.py:613`), **61 samples at `printInterval` 100** over 6000 steps.
Source: `/home/ubuntu/certonomous-runs/A3GC-AR1/primal.log`.

| window (graded samples) | min | max | peak-to-peak | samples below 1e-06 |
|---|---|---|---|---|
| last 10 | 1.008786925e-06 | 1.013653679e-06 | 0.48 % | **0 / 10** |
| last 20 | 1.007423301e-06 | 1.013957262e-06 | 0.65 % | **0 / 20** |
| last 50 | 1.005122996e-06 | 1.014616585e-06 | 0.94 % | **0 / 50** |

**The minimum RISES as the window narrows** (1.0051e-06 over 5000 steps -> 1.0088e-06 over
the last 1000). The plateau is flat to under 1 % and is drifting **very slightly AWAY from
the gate**. **Running longer alone cannot clear it, and AR1C does not propose that.**

## 3. THE MECHANISM UNDER TEST, AND THE HEADROOM THAT MAKES THE TEST DISCRIMINATING

AR1 solves `nuTilda` with `smoothSolver / GaussSeidel / relTol 0.1 / tolerance 0 / nSweeps 1`
(`A3GC-AR1/system/fvSolution:39-46`) — `nuTilda` shares one regex entry with U, T, e, h, k,
omega, epsilon.

At AR1's final step the linear solve reports
`initRes 1.008859568e-06  finalRes 4.019679e-08  No Iterations 3`.

- Leftover linear error carried into the next outer step: **4.019679e-08 = 3.98 % of initRes.**
- Reduction needed to clear the gate: **0.886 %.**
- **Headroom ratio 4.5x.**

So a perfect linear solve has *enough* room to clear the gate **if** the plateau is set by
linear-error carryover — and *nowhere near* enough to matter if it is set by the nonlinear /
discretisation balance. **That is what makes this test discriminating rather than decorative.**

**Correction to the working hypothesis, recorded before compute:** `nuTilda` is **NOT**
relTol-limited. It terminates at ratio 0.041 against a relTol target of 0.1 — **0 of the last
400 solves stop at the threshold.** The looseness is therefore *real but not saturating*, which
is why the honest prediction below has a genuine losing branch.

## 4. THE CHANGE — NAMED AS THE PACKAGE IT IS

**The D6RF10-R3 `nuTilda` repair, smoothSolver limb**, ported from A2
(`cases/dafoam/ladder-a/A2/curriculum_D6RF10`), where it took `nuTilda` from 4.07e-04 to
7.87e-05 at 13 sub-iterations per outer step:

    nuTilda { solver smoothSolver; smoother GaussSeidel;
              relTol 0.001; tolerance 1e-09; nSweeps 3; }

`nuTilda` is **removed from the shared regex group** so U, T, e, h, k, omega and epsilon keep
`relTol 0.1 / nSweeps 1` **unchanged**. **This is a one-equation change.**

**`nNonOrthogonalCorrectors` stays 0** — see §8, this is load-bearing for the grading path.

**The complete AR1 -> AR1C difference is two files and nothing else:**
`system/fvSolution` (the block above) and `system/controlDict` (comment only; `endTime` stays
6000). `runScript_a3gc.py`, `constant/`, `system/fvSchemes`, `system/decomposeParDict` and the
mesh are **byte-identical to AR1**.

## 5. WHAT "CONTINUATION" MEANS HERE — MEASURED, NOT ASSUMED

**Measured on a throwaway probe before this document was written** (root
`_probe_AR1C_restart`, 20 graded steps, **1.90 core-min**, discarded):

`startFrom latestTime` loads the 6000 field (`Create mesh for time = 6000`) but **DAFoam
resets the clock to 0 and then runs until the clock reaches `endTime`** — so it runs `endTime`
steps, writes time dirs from the reset clock, and **collides with the existing 2000/4000/6000
dirs.** That would have put stale and fresh fields under the same names.

**AR1C therefore does NOT use `startFrom latestTime`.** AR1's `processor*/6000` state — including
`phi`, `rho` and `betaFINuTilda` — is **staged as AR1C's `processor*/0`**, the old clock
(`uniform/`) is dropped, and the run is an ordinary `startTime 0 -> endTime 6000`.
**Last written time == `endTime` == 6000, with no name collision.**

**The probe also measured a restart transient**: `nuTilda` initRes reads 7.00e-06 at the first
step and decays through 2.85e-06, 1.28e-06, 1.35e-06 to 1.48e-06 by step 20. **It does not
return to the plateau instantly.** §6 registers a burn-in for exactly this reason.

## 6. THE REGISTERED PREDICTION — BOTH BRANCHES ARE REAL RESULTS

**Graded quantity:** `nuTilda initRes` as read by the frozen comparator, over the
**last 10 graded samples** (`REG_PLAT_WINDOW` = 10, `a3gc_grade.py:242`) — i.e. steps
5100-6000, which is **5100 steps past the restart transient**.

**Burn-in:** the first 5 graded samples (steps 100-500) are **excluded from every plateau
statement** as restart transient. They are reported, never gated.

**PREDICTION P-AR1C-1 (the fix transfers).**
**PASS** if `nuTilda initRes <= 1e-06` at the last printed step **and** all 10 samples of the
final window are `<= 1e-06`. Mechanism confirmed: the plateau was leftover linear-solver error,
and the D6RF10-R3 package transfers from A2 to A3.

**FALSIFICATION P-AR1C-1 (the plateau is the configuration).**
**GATE FAIL** if the final-window **minimum stays above 1e-06** while the final-window
peak-to-peak is **<= 2.0 %**. That conjunction is the real result: with the linear solve
tightened by two decades and the residual still flat and still above the gate, **1.0089e-06 is
where this configuration lands**, and the plateau is proven flat over a registered window
rather than asserted.

**Between the two -> `NOT A RESULT`** (final-window minimum above 1e-06 **and** peak-to-peak
above 2.0 %): the window is not a plateau, so it licenses neither statement.
*Registered because a registration that supplies two thresholds has by construction declared
the space between them evidence for neither (grader AMENDMENT 3(a)).*

**Plateau flatness is a MEASUREMENT, not an impression:** peak-to-peak over the last 10 graded
samples, threshold **2.0 %**. AR1's own last-10 peak-to-peak was **0.48 %**, so 2.0 % is a
loose, generous band that AR1 clears by 4x — it is not tuned to the answer.

**Reported, never gated:** CD and CL against anchor 0.0229956 / 0.3131159; the number of
`nuTilda` sub-iterations per outer step (AR1: 3); the final/initial ratio (AR1: 0.0398).

**DISCLOSED BRANCH (registered now so it cannot be chosen later):** DAFoam exits the primal
early if **max initRes < `primalMinResTol` = 1e-8** (`DASolver.C`, the `loop()` limb), which is
**two decades below this plateau** and is not expected. If it nevertheless fires, the run ends
before `endTime`, `last time == endTime` fails, and **AR1C is `NOT A RESULT` on completion** —
the residual banner is reported but **does not rescue the row**, and the disposition of such a
row is the supervisor's, not this lane's.

## 7. GATES — UNCHANGED, AND THE 1e-06 GATE DOES NOT MOVE

**`REG_INITRES_MAX` = 1e-06 is NOT touched.** The grading path is
`cases/dafoam/ladder-a/A3/curriculum_A3GC/a3gc_grade.py`, **reused UNCHANGED** at
**md5 `73dbe368934956700da87e5a1f44ea0c`**, committed in the same commit as this document.
All A3GC gates (G-SYS, G-TOL, G-RES, G-PLAT, G-COMPLETE) apply as written.

## 8. WHY `nNonOrthogonalCorrectors` IS NOT TOUCHED HERE — A GRADING-PATH DEFECT, MEASURED

`DAUtility::primalResidualControl` prints one `<eq> initRes:` line **per non-orthogonal
corrector** (called inside `while (simple.correctNonOrthogonal())`, `pEqnSimple.H:41,52`),
while the comparator's `read_log` keeps the **last** match in the final `Time =` block
(`a3gc_grade.py:695-702`). With correctors on, the graded `p` would be the **last corrector's**
residual — taken from an almost-solved field — not the outer residual.

**Demonstrated with a planted control, not asserted:** fed a synthetic final block carrying
the true outer `p initRes 1.000000e-03` followed by correctors at 5.5e-05 and a planted
**1.234e-09**, the comparator's own regex returns **1.234e-09** — the plant was read back — and
the 1e-06 gate reads *PASS-looking* on a residual that is truly 1.0e-03. The **same reader**
returns the honest 1.000000e-03 on a single-corrector block, so the reader is shown able to
return both answers.

**AR1C keeps `nNonOrthogonalCorrectors` at 0, so this defect cannot touch its row.**
It is raised as a defect against the A3GC grading path and is **the supervisor's to rule on**,
because it blocks the L2 repair, not this one.

## 9. COST — PRE-REGISTERED, PER CLAUDE.md RULE 12

**Basis:** AR1, same mesh (399,360 cells), same `np`=4, same 6000 steps:
`ExecutionTime 3590.84 s`, `ClockTime 7467 s` (`A3GC-AR1/primal.log`).

- **Estimate: 500 core-minutes gross** (7467 wall s x 4 ranks / 60 = 497.8), on a box measured
  at load ~48-53 on 16 cores. Solver-time basis would be 239 core-min; **the gross figure is
  registered** because the box is oversubscribed and §6 of the budget charter forbids hiding
  contention in the estimate.
- Ranks: **4**, forced by AR1's existing 4-way decomposition and chosen to stay modest while
  four protected runs are live.
- The `nuTilda` package adds sub-iterations on **one** equation; `nuTilda` is a small fraction
  of step cost, so the estimate is **not** inflated for it. Any overshoot is a misprediction to
  be reported at calibration, not absorbed.
- **NO CAP of any kind** (Sanaa, directive #17, 2026-09-12): no `timeout`, no deadline, no
  core-minute guard, no watchdog able to signal. **Memory containment is retained and is not a
  cap:** `--memory=6g --memory-swap=6g --oom-score-adj=500`.
- Actual-versus-predicted lands in `docs/COST_CALIBRATION.md` at completion (rule 12).

## 10. COMPLETION

Graded only if rc=0, an `End` line, **last time == `endTime` = 6000**, fields present, and the
`endTime` fields newer than the staged `0`. A run failing any clause is **NOT A RESULT**.

---

# ADDENDUM 1 — 2026-09-12 — A PROVENANCE CITATION I COULD NOT CORROBORATE

**Dated addendum, appended at the foot. Alters NO gate, NO threshold, NO cap and NO label.
The 1e-06 gate, the prediction, the falsification condition, the 2.0 % flatness band, the
5-sample burn-in and the grading path are ALL unchanged. Lines whose number changed above this
section: 0.**

## What is wrong

§4 states that the applied `nuTilda` package is "the D6RF10-R3 `nuTilda` repair", and the commit
message that froze this document says it "took `nuTilda` from 4.07e-04 to 7.87e-05 at 13
sub-iterations per outer step". **I took that figure from my brief and did not verify it before
freezing. It does not survive checking.**

Searched: `cases/dafoam/ladder-a/A2/curriculum_D6RF10/PREREGISTRATION.md`, the same directory's
`D6RF10_GRADE_RECORD.md`, and a repository-wide grep for the literal figure. **The value
`7.87e-05` occurs nowhere on disk except in this document's own §4.** No record of a D6RF10 rung
named as a `nuTilda` linear-solver repair was found.

**What D6RF10 actually records** (`D6RF10_GRADE_RECORD.md:62-65`):

| rung | configuration | outcome |
|---|---|---|
| R1 | `nNonOrth 3`, `DARhoSimpleFoam` | **GATE FAIL** (`p_first_uncorrected` 1.681236312e-05) |
| R2 | `nNonOrth 12`, `DARhoSimpleFoam` | **NOT A RESULT** — SIGKILLed ~4 % short of its deadline |
| R3 | `DARhoSimpleCFoam` + `nNonOrth 12`, `relax_p` 0.70 | **PASS** (`p_first_uncorrected` 6.3233727e-06) |

Those rungs turn on **solver coupling and corrector depth**, not on a `nuTilda` linear-solver
package. **So the name "the D6RF10-R3 nuTilda repair" in §4 is not supported by the record, and
the 4.07e-04 -> 7.87e-05 figure is uncorroborated.**

## What is NOT wrong, and how I know

**The settings themselves are sound and are measured active in this very run.** The change is
what §4 prints — `relTol 0.001 / tolerance 1e-09 / nSweeps 3` on `nuTilda` alone — and AR1C's own
first step is the control:

| | initRes | finalRes | nIters |
|---|---|---|---|
| probe, AR1's settings | 7.004707703e-06 | 2.755606367e-07 | 3 |
| **AR1C, this package** | **7.004707703e-06** | **3.743733924e-09** | **9** |

Identical `initRes` to ten digits proves the staged state is genuinely AR1's; `finalRes` **74x
tighter** proves the package is installed and acting. **The experiment §6 registers is unaffected**
— it tests a mechanism, and the mechanism is driven by the settings, not by their name.

## The correction

**§4's package is hereby cited as what it verifiably is: a tightened `nuTilda` linear solve,
adopted by this lane, `relTol 0.001 / tolerance 1e-09 / nSweeps 3`, with `nuTilda` removed from
the shared regex group. Its provenance is THIS document and the arithmetic in §3 — the 3.98 %
leftover against the 0.886 % needed — and NOT a prior D6RF10 result.** Any reader who followed
the D6RF10-R3 citation to look for a precedent should stop: there isn't one, and the case for the
change stands on §3's headroom measurement alone, which is where it always actually rested.

**Recorded rather than quietly fixed**, because a frozen document is never edited (rule 6) and
because a provenance I cannot corroborate is exactly the kind of borrowed confidence the lab's
own rules say to surface instead of carry.
