# W5 — every published shape-gradient claim, re-run under the corrected derivative

**Session 2026-08-01.** Docket item `w5-regrade-every-published-gradient-claim`,
`est_core_min` 300.0, gate: *"Every published shape-gradient or
shape-optimisation claim is listed with its corrected value and a verdict of
holds, moves, or withdrawn."*

**Nothing here has been filed upstream.** The corrected derivative is the
four-line local patch of `dafoam/PATCH_getRotationMatrix3d.md`, applied to a
scratch clone (`/home/ubuntu/certonomous-runs/W5-patch/idwarp`), never to an
installed package.

---

## 0. What was actually run, and the control that makes it readable

Each case below was re-run **twice**: once on the container's shipped IDWarp
2.6.2 and once with `PYTHONPATH` pointed at the patched clone. Same case, same
rank count, same FD step, same task, back to back. Every log prints
`IDWARP_IMPORTED_FROM:` so which stack produced which table is on the record and
not inferred.

**The control that validates every comparison below: the finite difference must
not move.** The patch touches only `src/adjoint/output{Reverse,Forward}/
vectorUtils_{b,d}.f90` — derivative code. If a patched run's FD column differed
from its stock run's, the comparison would be between two different functions
and nothing could be concluded. It does not differ, in any row, in any case:
**every `Fd Magnitude` is bit-identical between the stock and patched runs.**
That is stated per case below and it is the reason the "corrected" column can be
read as a correction rather than as a different experiment.

Second control: the **stock re-runs reproduce the published tables to every
printed digit.** Nothing below rests on remembering what a number used to be.

**A caveat on the wall clocks, not on the numbers.** Several of these ran
concurrently with each other and with the R4 ladder, and the box went briefly
above its 14 usable cores. Every wall time quoted here is therefore a
*contended* measurement and is not comparable with the uncontended figures in
the published records. The derivative values are unaffected — each run had its
`--cpus` cap and its own decomposition, and the stock/patched pairs were
identically placed.

| case | rank count | stock run | patched run | measured cost |
| --- | --- | --- | --- | --- |
| A1 NACA0012 (4 032 cells, 10 DVs) | **2** — the count the published number was measured at | `W5-regrade/a1_unpatched_stock.log` | `W5-regrade/a1_patched_patched.log` | 65 s + 53 s wall at 2 ranks = **3.9 core-min** |
| A4 Ahmed coarse (2 777 cells, 1 scalar shape DV) | **4** | `W5-regrade/a4_stock_checktotals.log` | `W5-regrade/a4_patched_checktotals.log` | 47 s + 58 s wall at 4 ranks = **7.0 core-min** |
| A5 U-bend, pressure-loss (4 800 cells, 27 shape DVs) | **4** | `W5-regrade/a5pl_stock_checktotals.log` | `W5-regrade/a5pl_patched_checktotals.log` | 235 s + 250 s wall at 4 ranks (contended) = **32.3 core-min** |
| A2 MACH wing (38 304 cells, 105 DVs) | **4** | published `check_totals` attempt 2 (`A2_mach_tutorial_wing.md:40`) | `W5-regrade/a2_patched_checktotals.log` | patched run only, see §3a |

**One case that is NOT in that table, and why.** The U-bend case sitting in the
patch tree (`W5-patch/a5_case`) is **not** the case the published A5 number came
from, and it was run before that was noticed. Its `runScript.py` carries the
**stock tutorial objective** `0.5*CPL − 0.5*HFX`, where the published A5 rung
replaced it with a **pure pressure-loss** objective `TP1 − TP2`
(`A5_work/UBend_Channel_pressureloss/runScript.py:160`), and it computes all six
FFD DV groups where the published run restricted `check_totals` to
`of=["OBJ.val"], wrt=["shapexUpper"]` (`:321-331`). The objectives are not even
the same magnitude — baseline TP1 reads 88.1 in one and 2869.5 in the other. So
that pair is reported in §4a as what it is, a stock-objective measurement, and
the published 46.6% is regraded in §4 from the pressure-loss case itself.

---

## 1. A1 NACA0012 — the whole shape chain collapses, and the FD never moves

`runScript.py -task check_totals`, `step=1e-3`, `form=central`, `step_calc=abs`,
np=2, 2026-08-01. Published source of the "before" column:
`dafoam/ladder-a/A1_naca0012_incompressible.md:110-121`.

| derivative | published | **stock re-run** | **patched** | FD moved? |
| --- | --- | --- | --- | --- |
| CD wrt `patchV` | 0.232% | **0.2317%** | **0.2317%** | no |
| **CD wrt shape (8 FFD DVs)** | **11.43%** | **11.43%** | **0.03745%** | no |
| CL wrt `patchV` | 0.232% | **0.2316%** | **0.2316%** | no |
| **CL wrt shape** | **1.671%** | **1.671%** | **0.01494%** | no |
| `volcon` wrt shape | 4.4e-14 | **4.367e-12 %** | **4.367e-12 %** | no |
| `thickcon` wrt shape | 1.3e-13 | **1.265e-11 %** | **1.265e-11 %** | no |
| `rcon` wrt shape | 1.4e-10 | **1.363e-08 %** | **1.363e-08 %** | no |

Analytic magnitudes: CD/shape `6.460294e-02` → `6.490498e-02` against an
FD of `6.489575e-02` that is identical in both runs. The primal is untouched:
both runs converge at `Time = 435` with
`Minimal residual 9.646409714038222e-09`, the same 16 digits the published
record reports.

The two rows that are **not** in the shape chain (`patchV`) and the three that
bypass the volume warp (the geometric constraints) do not move by a digit. That
is the patch behaving exactly as its own §6 predicted, measured on a case it was
not tuned on.

**Verdicts.**

* **A1 `CD wrt shape` = 11.43%, graded FAIL — HOLDS as published, and is now
  attributed.** The shipped toolchain still produces 11.43%; that was reproduced
  today, not recalled. Under the corrected derivative the same case reads
  **0.03745%**, a 305-fold reduction in the absolute error (7.415918e-03 →
  2.430027e-05). The number that moves is not the claim — it is the *cause*: the
  disagreement was upstream IDWarp, not this lab's adjoint chain.
* **A1 `CL wrt shape` = 1.671%, graded PASS — MOVES (within PASS).** To
  **0.01494%**, a 112-fold reduction. See §3: this row is the load-bearing one
  for A2.

---

## 2. A4 Ahmed body — the correction does **not** rescue it, and that resolves a published contradiction

`runScript.py -task check_totals`, np=4, 2 777 cells, one scalar FFD design
variable (the rear-slant break-line height). Published source:
`dafoam/ladder-a/A4_ahmed_body.md:196-211`.

| | analytic | FD | rel. error |
| --- | --- | --- | --- |
| published | 0.21821 | 0.24258 | **10.04%** |
| **stock re-run** | **0.21821** | **0.24258** | **10.04%** |
| **patched** | **0.22086** | **0.24258** | **8.953%** |

The FD is identical across all three. The stock re-run reproduces the published
figure exactly.

**The corrected derivative moves A4's error by 1.09 percentage points — from
10.04% to 8.95% — and no further.** Roughly **11% of A4's gradient disagreement
is the rotation defect; the other 89% has no identified cause.** This is the
opposite of A1 and A5, where the same four lines collapsed the error to
FD-truncation level, and it was not predictable from them.

**Verdicts.**

* **A4 `CD wrt shape` = 10.04%, CONDITIONAL — HOLDS, at 8.953%.** Still inside
  the 5–15% CONDITIONAL band of the lab's own standard
  (`ladder-a/A_stepsize_study.md:89-94`). The grade does not move.
* **The published PASS/CONDITIONAL contradiction is resolved in favour of
  CONDITIONAL.** `A4_ahmed_body.md:207` and `A4_ahmed_body.json:216` say PASS;
  `:160-164`, `ACTIVE_RESEARCH.md:88`, `DAFOAM_CASE_STATUS.md:61` and
  `NOT_PASSING_REGISTER.md:338` say CONDITIONAL, and `:163` records that the
  PASS wording "has not been reconciled by its owner." It is reconciled now, and
  by measurement rather than by preference: the one explanation that could have
  lifted A4 to PASS — "it was all the upstream bug" — has been tested and
  rejected. **A4 keeps a second, independent open question that A1 no longer
  has.**

*This is the result this item was most at risk of getting wrong.* The
expectation after A1 and A5 was that the patch would clear A4 too. It does not,
and the run that says so is the same protocol that cleared the others.

---

## 3. A2 MACH wing — why "1.71%, VERIFIED" was never safe

A2's four gradient rows (`CD/shape 1.71%`, `CL/shape 1.17%`, `CD/twist 0.389%`,
`CL/twist 1.12%`) are published as **VERIFIED** on
`dafoam/ladder-a/A2_mach_tutorial_wing.md:49-53`, on `benchmarks.html:134-136`
and on `shoot.html:546`, and the **28.3% drag reduction** headline
(`A2_mach_tutorial_wing.md:82`, `benchmarks.html:123`, `shoot.html:658`) rests
on that gate passing. All 96 shape DVs and 7 twist DVs go through
`mesh.warpDeriv`. Grepping `benchmarks.html` and `shoot.html` for
`warp|idwarp|sign.flip|11.43|46.6|10.04` returns nothing: the reader-facing
surface carries no trace of the defect.

The published reasoning for trusting A2 is explicit
(`A2_mach_tutorial_wing.md:63`): the shape rows "land inside the 1–12% normal
band and are noticeably tighter than A1's shape-derivative agreement." And the
band itself is defined, on `A2_mach_tutorial_wing.md:44`, by naming A1's rows:

> Calibration reference (measured tonight on the official unmodified NACA0012
> tutorial, ladder A1): … **CL wrt shape ~1.67%** … A shape-derivative FD gap of
> 1–12% is normal for this problem class, not evidence of a broken adjoint.

**A1's 1.67% is the calibration A2 was graded against, and it has now been
measured to be almost entirely the defect.**

**A1's own paired run refutes that reasoning, with numbers from a single
`check_totals` call.** In the stock run of §1, `CL wrt shape` read **1.671%** —
inside the same band, tighter than A1's own CD row, on exactly the same
`warpDeriv` call that was simultaneously producing 11.43% on CD. Under the
corrected derivative that same row reads 0.01494%. **So 1.671% was not a clean
gradient with a little numerical noise in it; it was ~99% rotation defect.**

An aggregate in the 1–2% band is therefore not evidence that the chain is
sound. It is compatible with the defect being fully present. A2's 1.71% and
1.17% sit in precisely that range, and A2 has never been tested under the
real-seed `warpDeriv` protocol that overturned A5's clearance
(`A5_ubend_internal.md:976-1044`).

---

### 3a. A2 could not be regraded, because its published verification is no longer reproducible on this box

This was attempted properly and it failed, and the failure is the most important
thing this document has to say about A2.

**Attempt 1 — the case as preserved.** `check_totals` was launched against a copy
of `/home/ubuntu/certonomous-runs/A2-mach-wing` with the patched IDWarp, np=4,
at 12:45:22Z. It ran for **59.6 minutes (238 core-minutes at 4 ranks)** and died
at **perturbation 132 of 211** with
`openmdao.core.analysis_error.AnalysisError: 'scenario1.coupling.aero.solver'
<class DAFoamSolver>: Error calling solve_nonlinear(), Mesh quality error!`
(`W5-regrade/a2_patched_checktotals.log`, `rc=1` at 13:44:58Z). No table.

The reason is visible in that log's own first lines. Its baseline primal
converges to **CD 0.03142017502, CL 0.4967099218**. The published A2 primal is
**CD 0.02772949388, CL 0.4775877833** (`A2_mach_tutorial_wing.md:23-24`).
**The preserved case is not at its published baseline** — the 47-iteration
IPOPT optimisation ran in that directory (`OptView.hst`, `opt_IPOPT.txt`,
`opt_run_driver.log` are all in it) and left the mesh deformed. Perturbing an
already-deformed mesh by another FD step is what eventually produced the
mesh-quality failure.

**Attempt 2 — rebuild the mesh, with a gate fixed before the run.** The gate:
*the rebuilt baseline must return the published CD 0.02772949388, or the case is
not restored and no gradient number from it means anything.* `preProcessing.sh`
was re-run in the container (the surface CGNS was already on disk, no download)
and the primal solved at np=4.

**Gate FAILED.** The rebuilt case returns **CD 0.02964132667, CL 0.4999507339**
(`W5-regrade/a2_rebuilt_runmodel.log`) — **6.9% from the published `run_model`
figure.** It lands instead within **0.07%** of the *optimisation's* iter-0
baseline, 0.029619634 (`A2_mach_tutorial_wing.md:77`), at the trimmed CL ≈ 0.5.
So `runScript.py` as preserved carries the CL-trimmed angle of attack, not the
tutorial default the published `run_model` used, and rebuilding the mesh does
not undo that.

**And it is worse than a one-off offset: A2's primal does not reproduce.** Four
solves of nominally the same case, from states preserved in this tree, converge
to four different answers:

| source | CD | CL |
| --- | --- | --- |
| published `run_model` (`A2_mach_tutorial_wing.md:23`) | 0.02772949388 | 0.4775877833 |
| the preserved case (`a2_patched_checktotals.log`) | 0.03142017502 | 0.4967099218 |
| after `preProcessing.sh` rebuild (`a2_rebuilt_runmodel.log`) | 0.02964132667 | 0.4999507339 |
| the two twist copies, both identical (§3b) | 0.03162405532 | 0.5216398962 |

**A 14% spread in CD.** Compare A1, where the same exercise reproduced
`Minimal residual 9.646409714038222e-09` and the whole derivative table to every
printed digit. The CL climbing monotonically down that column — 0.4776, 0.4967,
0.4999, 0.5216 — points at the angle-of-attack state in `0/U` being carried
forward and re-written by each run rather than reset, so every copy inherits the
last one's trim. That is the likely mechanism and it is not proven here.

**Verdict on S7–S11 — A2's four VERIFIED gradient rows and the 28.3% drag
reduction: NOT REGRADED, and the reason is a provenance failure, not a gradient
result.** Two things follow and neither is comfortable:

1. **The most prominently published gradient claim this lab has cannot currently
   be re-verified.** `benchmarks.html:115` states *"Every gradient below was
   verified against finite differences before any optimisation result was
   allowed to stand"* and `:141` that this *"is why the 28.3% drag reduction that
   followed is trustworthy rather than merely large."* That verification ran
   once, on 2026-07-2x, at a state this box no longer holds. **Nobody can
   re-do it from what is preserved** — not this session, and not a reader.
2. **§3's argument therefore stands unrebutted rather than confirmed.** A1's
   1.67% CL/shape — the exact figure `A2_mach_tutorial_wing.md:44` names as the
   calibration for calling A2's 1.71% normal — is now measured to have been
   ~99% rotation defect. That does not prove A2's rows are defective. It removes
   the only evidence that was offered for them being sound.

**What was measured instead** is in §3b: a stock-versus-patched pair on the
rebuilt A2 geometry, restricted to the twist design variables, which answers the
transferable question — *how much of this case's gradient error is the rotation
defect?* — at a fourteenth of the cost of the full sweep, while being explicit
that it is not at the published state.

### 3b. On A2's own geometry, the correction is a **no-op** for twist — and that narrows the exposure

The full 105-DV sweep is 210 primal solves. The twist subset is 7 DVs, 14
solves, and it goes through the same `DVGeo → IDWarp warpDeriv` chain. Both runs
used the rebuilt A2 geometry of §3a, np=4, `step=1e-3 central abs` (the
published step), with `check_totals` restricted to
`of=[CD, CL], wrt=[twist]` — the only edit made to `runScript.py`, and it is
recorded in the file as a comment. Stock and patched ran concurrently, same
state, same step.

| derivative | stock analytic | patched analytic | FD (both) | stock rel | patched rel |
| --- | --- | --- | --- | --- | --- |
| CD wrt twist (7) | 2.020405e-03 | **2.020405e-03** | 2.017324e-03 | 0.1840% | **0.1840%** |
| CL wrt twist (7) | 2.266683e-02 | **2.266683e-02** | 2.264033e-02 | 0.1659% | **0.1659%** |

**The analytic magnitudes are bit-identical between stock and patched.** The
corrected derivative changes nothing at all for twist on this case. That is
consistent with `PROOF.md` §23's five-mesh finding that the rotation term
contributes exactly zero to `Sum of dxs` while changing `‖dXs‖` by factors of
5–34: the twist mode appears to sit in that null space. No mechanism is claimed
here beyond the measurement.

**Verdicts.**

* **S9 (A2 `CD wrt twist` 0.389%) and S10 (`CL wrt twist` 1.12%): HOLD.** The
  defect does not reach them. The rows read 0.184% and 0.166% at the rebuilt
  state rather than 0.389% and 1.12% at the published one — the state differs,
  the conclusion does not.
* **S7, S8 (A2 CD/CL wrt *shape*, 96 FFD DVs) and S11 (28.3% drag reduction):
  still NOT REGRADED.** Twist is a global rotation about a reference axis; the
  shape DVs are local FFD point displacements, and A1 shows *those* are affected
  — comprehensively. **The twist result must not be read across to them.** What
  it does do is halve the exposure: two of A2's four VERIFIED rows are now
  measured clear, and the remaining two are the ones the optimisation actually
  drove on.

## 4. A5 U-bend — the published 46.6% closes to 2.24%, and that is a claim moving *up*

`runScript.py -task check_totals`, `of=["OBJ.val"]`, `wrt=["shapexUpper"]`
(27 components), `step=1e-4`, `form=central`, np=4, on the **pressure-loss**
configuration — the case the published number came from
(`A5_work/UBend_Channel_pressureloss/`). Published source:
`dafoam/ladder-a/A5_ubend_internal.md:159`, log
`A5_work/.../check_totals_run1.log`.

| | analytic | FD | rel. error |
| --- | --- | --- | --- |
| published | 1.938364e+01 | 3.340851e+01 | **46.6377%** |
| **stock re-run** | **1.938364e+01** | **3.340851e+01** | **46.6377%** |
| **patched** | **3.350432e+01** | **3.340851e+01** | **2.2372%** |

The stock re-run reproduces the published table to **every digit of all three
columns**, and the baseline objective matches too — `TP1: 2869.524210823638`,
the same 16 digits in the published log, the stock re-run and the patched run.
The FD is unchanged between stock and patched.

**Verdict: A5 `OBJ.val wrt shapexUpper` = 46.64%, graded FAIL — HOLDS as
published against the shipped toolchain, and closes to 2.2372% under the
corrected derivative.** With `PATCH_getRotationMatrix3d.md` §9.3 already showing
idx8 and idx17 falling from 207.0%/121.6% sign-flipped to 3.0e-06/7.0e-06 with
signs agreeing, a patched A5 carries no flagged component and a 2.24% aggregate
— **inside the ≤5% PASS band.**

**This is the one that moves up, so it gets the extra scrutiny.** Three things
are worth stating rather than glossing:

1. **2.24% is not zero, and it is not A1's residual.** A1's patched CD/shape
   sits at 0.037% — FD-truncation level. A5's sits **60× higher**. Whatever is
   left in A5 after the rotation term is supplied is 20× smaller than what was
   there before, but it is not nothing, and it is not explained here.
2. **It is a PASS only on the patched stack, which is not shipped.** Nothing a
   reader can install produces 2.24%. The published FAIL stands for the stock
   toolchain and `NOT_PASSING_REGISTER.md`'s ruling that both entries stay is
   unaffected.
3. **The FD did not move, and the primal did not move.** Those are the two ways
   a flattering number could have been manufactured here, and both are closed by
   identical columns rather than by argument.

### 4a. A second U-bend pair, on a different objective, reported as what it is

A U-bend case also sits in the patch tree (`W5-patch/a5_case`) and was run
stock-then-patched before it was noticed that its `runScript.py` carries the
**stock tutorial objective** `0.5*CPL − 0.5*HFX` rather than the published
rung's pure `TP1 − TP2`, and computes all six FFD DV groups rather than the one
the published `check_totals` was restricted to. Its stock run reads
`OBJ.val wrt shapexUpper` at **40.55%** where the published pressure-loss
configuration reads 46.64% — different objectives, different numbers, and the
baseline TP1 differs by a factor of 32 (88.1 against 2869.5). **It is not a
regrade of anything published.** Its stock table is on record
(`W5-regrade/a5_stock_checktotals.log`: shapexLower 42.795%, shapexUpper
40.552%, shapeyLower 35.835%, shapeyUpper 53.733%, shapezLower 11.447%,
shapezUpper 34.927%); its patched half was **stopped part-way at 139 of 324
perturbations, deliberately, to give its four cores back to the A2 run**, and
produced no table. Recorded so the log's existence is not later mistaken for a
result.

## 5. What the proposal assumed, and what is actually true

The item's rationale states that *"every adjoint shape gradient this lab has
computed was evaluated at a state where the degenerate-rotation guard fires, so
every one of them is missing the same term."*

**The first half is right and the second half is too strong.** The guard fires
at the undeformed baseline — that is where `check_totals` evaluates, so every
published verification is at a firing state, confirmed. But "missing the same
term" implies one shared magnitude, and A4 is the counterexample: the same term
was missing there too, and supplying it recovered only 11% of the gap. The term
is shared; the consequence is not. A regrade that assumed a common magnitude
would have moved A4 to PASS on A1's evidence, which the measurement says is
wrong.
