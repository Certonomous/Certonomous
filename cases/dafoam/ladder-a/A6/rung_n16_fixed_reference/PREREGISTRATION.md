# A6 CRM wing-alone, rung N=16 (41,760 cells), np=1: FIXING THE FD REFERENCE — PRE-REGISTRATION

**Filed 2026-08-22, DAFoam team LANE B, BEFORE any arm launched.** Predictions, gates, ceilings and
falsifiers are committed first. `RESULTS.md` will not revise this file; departures go to a dated
Amendments section there. **Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and
is Sanaa's alone** (`DAFOAM_CHARTER.md` §10; `FAMILY_SUPERVISION_GUIDELINES.md` §3.6).

**This is a PATCHED-IMAGE row.** Every arm below runs on `dafoam-idwarp-rot:v1`
(`IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425`), the image Sanaa's N=29 gate was written against.
Per `DAFOAM_CHARTER.md` §6 a patched row never replaces a shipped row and the two are never merged.
No shipped-toolchain arm is run here; the shipped row for this rung already exists at
`../rung_n16_np1/RESULTS.md` §6 and stands unchanged.

**Run root:** `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/`.
**Predecessor item (frozen, never edited by this one):** `../rung_n16_np1/{PREREGISTRATION,RESULTS}.md`.

---

## 0. Ordering disclosure — what was read before this file was written, and at what cost

**No solver arm has been launched for this item.** Everything quoted below as "measured" was read out
of artefacts that already existed on disk before this file was opened, at **zero new compute**:

* `/home/ubuntu/certonomous-runs/P2-a6-n16/stock.log` (the predecessor's graded shipped arm),
* `/home/ubuntu/certonomous-runs/P2-a6-n16/{patched.log,ledger.txt,rss_stock.txt}`,
* four `docker run --rm` *inspection* commands against `dafoam-idwarp-rot:v1` that ran `ls`, `nm`,
  `grep` and one `import` — no solver, no mesh, no primal. Billed in §7 as **0.4 core-min**.

**Two of those readings are load-bearing and are stated here, before the predictions that use them,
so it is visible that the predictions are derived from prior data rather than retrofitted to a new
run.** They are §1.1 (the primal is stagnant) and §1.2 (forward-mode AD is present and reachable).

## 1. What this item is for, and the two facts that shape it

The predecessor rung is **GATE FAIL on both images** and its own record locates the cause in the
**finite-difference reference, not the adjoint**: the primal stops at 1,000 iterations with
`primalMaxRes` 5.556e-06 against `primalMinResTol` 1e-8 (**556× short**), CD carries a peak-to-peak
wobble of **9.00e-6** over the last 200 iterations, and at `step=1e-3, form=central` that leaves a
derivative noise floor of `9.00e-6 / (2 × 1e-3)` = **4.5e-3** which **8 of 9 graded components do not
clear**. Only `patchV` idx1 clears it (1.94×) and it is the only component that agrees (3.29%).
The predecessor's closing sentence is the charge this item answers: *"Fixing the reference, not
enlarging the mesh, is the next step, and it is not registered anywhere yet."*

This item registers it, and buys it in two stages.

### 1.1 MEASURED, from `stock.log`, at zero compute: the primal does not stagnate *slowly* — it is flat

The predecessor recorded the endpoint (`primalMaxRes` 5.556e-06 at iteration 1,000) but not the
trajectory. The trajectory is in the same log and is pasted here because it is the basis of P1 and
it points the opposite way from "converge harder":

```
$ awk '/^Time = /{t=$3} /nuTilda initRes/{print t, $3}' stock.log | head -11
1     0.9999999999971881
100   6.014163529988668e-06
200   5.629310539034155e-06
300   5.482368911903452e-06
400   5.778127843221405e-06
500   5.565514164069021e-06
600   5.707866831262859e-06
700   5.647389885321282e-06
800   5.742484505861402e-06
900   5.686896638518553e-06
1000  5.908769514219209e-06
```

and the maximum initial residual over **all** equations at each printed step of the same primal:

```
1    1.0        400  1.88134e-05      800  1.60156e-05
100  1.16057e-02 500  1.62889e-05     900  1.60654e-05
200  5.48817e-04 600  1.65384e-05    1000  1.69181e-05
300  4.05780e-05 700  1.73426e-05
```

**`nuTilda` is flat to within ±4% of its own value from iteration 100 to iteration 1,000, and the
all-equation maximum is flat to within ±5% from iteration 400.** This is not slow convergence. It is a
residual limit cycle: nine decades of iteration budget would not move it. `VERIFICATION_CHARTER.md`
§7's caution — *"do not prescribe 'converge harder' before checking whether convergence is
available"* — and `DAFOAM_CHARTER.md` §3's A5 instance (tightening tolerances and running 10× longer
moved 46.64% → 46.21% and made the sign flips **worse**) both apply directly. **Stage 1 buys the
check anyway, because a registered prediction that the gate fails is worth more than an assumption
that it does, and because the same arm measures the wobble at 6,000 iterations, which nothing has.**

### 1.2 MEASURED, at zero compute: forward-mode AD is present, reachable, and this is Charter §2's clause

`DAFOAM_CHARTER.md` §2: *"where a complex-step or forward-AD reference is available, it is the
reference … A record that reports only an FD table where a forward-AD or complex-step reference was
reachable states that it did not reach for it, and why. **No lane has yet done this.**"* Four
inspection commands against `dafoam-idwarp-rot:v1` establish that it is reachable here:

| probe | command | result |
|---|---|---|
| the forward-AD library ships | `find / -name "libDASolverAD*.so"` | `/home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so` (9,534,464 B) and `…ADR.so` |
| **this case's solver is compiled into it** | `nm -D --defined-only libDASolverADF.so \| c++filt \| grep -c DARhoSimpleCFoam` | **28 symbols**, including `DARhoSimpleCFoam::solvePrimal()` and `::initSolver()` |
| the Python binding imports | `from dafoam.libs.ADF.pyDASolvers import pyDASolvers` | imports; **67 methods** including `solvePrimal`, `getTimeOpFuncVal`, `setSolverInput` |
| IDWarp's forward warp derivative exists | `dir(idwarp.USMesh)` | `warpDeriv`, **`warpDerivFwd`**, `verifyWarpDeriv` |

**How the derivative comes back out**, read from the source in the image
(`repos/dafoam/src/adjoint/DASolver/DASolver.C`):

```
DASolver.C:445    #if defined(CODI_ADF)
                      return funcVal.getGradient();      // getTimeOpFuncVal returns the DERIVATIVE
DASolver.C:376    #ifdef CODI_ADF
                      Info << " ADF-Deriv: " << timeOpVal.getGradient();   // printed every write step
```

so in `useAD mode=forward` the **function output of `run_model` IS `dF/dDV[seedIndex]`**, and the log
additionally prints an ` ADF-Deriv:` value on every objective line — which lets the tangent's own
settling be measured the same way the primal's wobble was. **One full primal per seed, no step.**

**DAFoam's own regression harness uses exactly this protocol** (`repos/dafoam/tests/testFuncs.py`
`run_tests`, lines 33–52): set `useAD.mode="forward"`, then for each `(dvName, seedIndex)` rebuild the
`om.Problem`, `prob.setup(mode="rev")`, `prob.run_model()`, and read `prob.get_val(funcName)[0]` as
the forward-AD derivative to compare against `compute_totals`. **This item follows the toolchain's
own reference protocol rather than inventing one.** It is also the protocol Kenway, Mader, He &
Martins (PAS 2019) §5.1 used to measure the DAFoam adjoint to 10 digits, where the same table's
FD-Jacobian option reached only 3–4 digits (`DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`).

**The seed path differs by DV class, and both are exercised** (`pyDAFoam.py:1350-1414`):
* `patchV` **is** a key of `inputInfo`, so the seed is set directly: `seeds[seedIndex] = 1.0`. **No
  mesh warp is in this chain at all.**
* `twist` is **not** a key of `inputInfo`, so the `volCoord` input takes
  `calcFFD2XvSeeds(DVGeo)` = `DVGeo.totalSensitivityProd(xDvDot)` → **`mesh.warpDerivFwd(xSDot)`**.
  This requires `add_dvgeo` to have been called on the solver component; the archived A6 `runScript.py`
  does **not** call it, so one line must be added — registered as Edit 4 in §3.

### 1.3 The unregistered edit that is NOT inherited silently

The predecessor's Amendment 2 raised `primalMinResTolDiff` from `1.0e2` to `1.0e4` and its own §7.2
says why that is not free: *"the guard was right … Any future rung on this case should either
converge the primal properly or choose an FD step sized against the measured wobble, and should not
simply inherit `1.0e4`."*

**This item does not inherit it silently. It is registered, with its reason, as Edit 3 in §3, and
Stage 1's gate arm S1a deliberately runs with the guard at its shipped default `1.0e2` so that the
guard's own verdict is on this item's record too.** The reason it is then raised for the reference
arms is stated in §3 and is not "to get past the gate": the object of this item is to supply the
independent reference whose absence is exactly what the guard is warning about, and a reference
cannot be measured on a run the harness refuses to complete.

## 2. Case as constructed — unchanged from the predecessor, and asserted per arm

| item | value | how it is asserted at run time |
|---|---|---|
| mesh | the predecessor's `base/`, 41,760 cells, `wing` 2,784 / `inout` 2,784 / `sym` 1,020 | copied file-for-file; `Mesh region0 size: 41760` grepped from each log |
| image | **`dafoam-idwarp-rot:v1`** (image ID `2927768a16ac`) | `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425` printed by the arm itself and asserted; an arm printing anything else is **void** |
| solver | `DARhoSimpleCFoam`, `primalMinResTol 1e-8` | unchanged |
| decomposition | **NONE — np=1, serial, undecomposed** (`DAFOAM_CHARTER.md` §5) | `nProcs : 1` grepped from each log; absent ⇒ arm void |
| `transonicPCOption` | **1** (the only live value) | `transonicPCOption 1;` in the `DAFoam option dictionary:` dump; reads `2` ⇒ arm void |
| cold start | fresh staged copy of `base/` per arm; `rm -rf processor* dRdWColoring_*.bin` before launch | first `Time step continuity errors … cumulative` must read `-0.00504349133910657` (the predecessor's cold value, `stock.log:533`); a different value ⇒ warm-start contamination, arm void (`WARMSTART_AUDIT.md`; `FAMILY_SUPERVISION_GUIDELINES.md` §8) |
| DV set | `twist` 7, `shape` (~10²), `patchV` 2 | `shape` is **not** graded here either, on cost, exactly as in the predecessor |

## 3. The registered edits — four, and no more

**Edit 1 — `transonicPCOption: 2 → 1`.** Inherited from the predecessor's §3, same justification
(`== 1` is the only live value for `DARhoSimpleCFoam`). Asserted in every log.

**Edit 2 — `endTime`.** `1000` (the archived value) for every reference arm, so that the reference is
measured at **the identical primal state the stored adjoint column was computed at**
(`DAFOAM_CHARTER.md` §5: *"an FD reference is part of a configuration, not a property of a case"*).
The single exception is gate arm **S1a**, which sets `endTime 6000` because measuring what 6,000
iterations does is its entire purpose.

**Edit 3 — `primalMinResTolDiff: 1.0e2 → 1.0e4`, on the reference arms only, registered, not
inherited.** Rationale, in full: with the primal in the residual limit cycle of §1.1,
`DASolver::checkPrimalFailure()` (`DASolver.C:2744-2752`) raises `AnalysisError("Primal solution
failed!")` at ratio 556–591 against a cap of 100, **before any function value is returned**, so no
reference of any kind — FD or forward-AD — can be measured with the guard at its default. The guard's
warning is not dismissed: it is the finding this item is buying the reference to answer, and **gate
arm S1a runs with the guard at its shipped `1.0e2` precisely so this item's record carries the
guard's own verdict, unwidened, in its own logs.** Expected consequence, registered in advance:
**S1a returns `rc=1` and that is not a failure of the probe** — its measurements (residual trace, CD
trace, wobble) are all printed before the gate fires.

**Edit 4 — one line, forward-AD arms only:
`self.scenario1.coupling.solver.add_dvgeo(self.geometry.DVGeo)` in `configure()`.** Required for the
`twist` seed path (`pyDAFoam.calcFFD2XvSeeds` raises `Error("calcFFD2XvSeeds is call but no DVGeo
object found! Call add_dvgeo in the run script!")` without it). It is the same line DAFoam's own
`tests/runRegTests_DAHisaFoam.py:108` carries. **It is inert for the FD arms and is not added to
them**, so the FD arms remain line-for-line the predecessor's script apart from Edits 1–3 and the FD
driver of §4.2.

**No other edit.** In particular `primalMinResTol` stays `1e-8` and is **not** loosened: loosening it
would make DAFoam stop at its *first* tolerance crossing, which is the `S1_CBFS_REINVERSION`
Amendment-1 incident (`DAFOAM_CHARTER.md` §3) — a primal stopped at iteration ~383 that missed the
adjoint by `fd/adj ≈ 0.7` on all three cells. Keeping `1e-8` unmet is what forces the full iteration
count.

## 4. The arms

All arms: `dafoam-idwarp-rot:v1`, np=1 (`mpirun -np 1 -x PYTHONPATH`), `--cpus=4 --memory=12g`,
`--rm`, **foreground under `timeout`**, record-only RSS watcher, one ledger line per arm.

### 4.1 STAGE 1 — the gate and the feasibility probes

| arm | what it does | `endTime` | `primalMinResTolDiff` | task |
|---|---|---|---|---|
| **S1a** | primal convergence probe | **6000** | **1.0e2 (shipped default)** | `run_model` |
| **S1b** | forward-AD reachability, `patchV` idx1 (no warp in the chain) | **10** | 1.0e4 | `run_model`, `useAD {mode:forward, dvName:patchV, seedIndex:1}` |
| **S1c** | forward-AD reachability, `twist` idx0 (**warp-crossing**, exercises `warpDerivFwd`) | **10** | 1.0e4 | `run_model`, `useAD {mode:forward, dvName:twist, seedIndex:0}` + Edit 4 |
| **S1d** | **FD instrument repeatability** — two back-to-back `run_model` calls with DVs unchanged, in one process | 1000 | 1.0e4 | `run_model` ×2 |

**S1d is the arm nothing on the record has bought and it may matter more than S1a.** The predecessor's
noise figure (9.00e-6) is the *within-run* peak-to-peak of one primal. The FD instrument does not
difference two points of one run; it differences **two separate primal solves**, and DAFoam's
perturbed solves warm-start from the previous solve's state (measured: primal 001 costs 72.17 s cold,
primals 002–019 cost 56–58 s each, `stock.log`). **Solve-to-solve reproducibility is the correct
denominator for an FD noise floor and it has never been measured on this case.** S1d measures it as
`δ_repeat = |CD_2 − CD_1|` at an identical design point.

### 4.2 STAGE 2 — the reference, on a four-component subset

**Subset, and why these four** (sized to the ceiling, §7): `twist` **idx 0, 3, 6** — the three
components that **reverse sign** against the FD in the predecessor's table, i.e. the three the lab
band makes an automatic FAIL — and `patchV` **idx 1**, the one component that agreed (3.29%) and the
only one whose FD cleared the old noise floor. The four together give the **calibration triangle**:
on `patchV` idx1 all three of {adjoint, FD, forward-AD} will exist, so if two of them agree the third
is graded rather than merely disagreed with.

**The adjoint column is NOT re-run.** It already exists, converged (`517` GMRES iterations,
`PetscConvergedReason: 2`), on this exact image and configuration, in
`../rung_n16_np1/RESULTS.md` §6.1. Re-running it would cost ~11 core-min and change nothing.
The values graded against are, patched image:

| DV, idx | adjoint (patched) | adjoint (shipped, for reference only) | FD @1e-3 (both) | old rel err |
|---|---|---|---|---|
| `twist` 0 | `-2.100900e-03` | `-2.107940e-03` | `+8.728200e-04` | 340.70% **FLIP** |
| `twist` 3 | `-1.010980e-03` | `-1.023320e-03` | `+1.703510e-03` | 159.35% **FLIP** |
| `twist` 6 | `-1.361900e-04` | `-1.374800e-04` | `+2.591130e-03` | 105.26% **FLIP** |
| `patchV` 1 | ` 9.016840e-03` | ` 9.016840e-03` | ` 8.729600e-03` | 3.29% |

**(a) Forward-AD arms — one primal per seed, no step at all.**

| arm | seed | chain exercised |
|---|---|---|
| **S2a-pV1** | `patchV`, idx1 | direct seed, **no mesh warp** |
| **S2a-t0** | `twist`, idx0 | `DVGeo.totalSensitivityProd` → `warpDerivFwd` |
| **S2a-t3** | `twist`, idx3 | same |
| **S2a-t6** | `twist`, idx6 | same |

**(b) FD arms at a step sized from the measured wobble. THE RULE, stated before the measurement.**

> **Noise amplitude** `η` := `max( CD peak-to-peak over the last 200 iterations at the endTime used,
> 2 × δ_repeat )`, with `δ_repeat` from S1d. Registered prior value from the predecessor: `η = 9.00e-6`.
> **Derivative noise floor at step `s`** := `η / (2s)` (central difference).
> **Clearance** `C(s) := |J| / (η/(2s))`, using the stored adjoint magnitude as the proxy for `|J_fd|`
> because `|J_fd|` at the new steps is not yet known — **stated as a proxy, not as a measurement.**
> **A component is graded on FD only at a step with `C(s) ≥ 5`. A component with no such step
> anywhere in the registered sweep is FLAGGED and excluded by name from every aggregate**
> (`DAFOAM_CHARTER.md` §3), never rescued by a step at which it happens to cross.

Clearance table, computed now from `η = 9.00e-6` and the patched adjoint magnitudes above:

| step `s` | floor `η/2s` | `twist` 0 | `twist` 3 | `twist` 6 | `patchV` 1 |
|---|---|---|---|---|---|
| 1e-3 (the predecessor's) | 4.50e-3 | 0.47× | 0.22× | **0.03×** | 2.00× |
| **1e-2** | 4.50e-4 | 4.67× | 2.25× | **0.30×** | **20.0×** |
| **3e-2** | 1.50e-4 | **14.0×** | **6.74×** | **0.91×** | **60.1×** |
| **1e-1** (`twist` only) | 4.50e-5 | **46.7×** | **22.5×** | **3.03×** | — |

**Registered sweep:** `twist` idx 0/3/6 at `{1e-2, 3e-2, 1e-1}`; `patchV` idx1 at `{1e-2, 3e-2}`. The
predecessor's `1e-3` column is carried in as a fourth/third point at **zero cost**, giving a
per-component sweep of 4 and 3 points respectively, which is what `DAFOAM_CHARTER.md` §3 requires and
what the predecessor did not have.

**A step of 1e-1 is registered for `twist` and not for `patchV`, and the asymmetry is deliberate.**
`twist` is in **degrees** with design bounds `[-10, 10]`, so `s = 0.1°` is 0.5% of the design range —
geometrically tiny. The A1 sweep's primal failures at `5e-2` and `1e-1` (`A_stepsize_study.md`) were
on **FFD shape coordinates in length units**, a different variable in different units, and are **not**
evidence about a 0.1° twist. `patchV` idx1 is AoA in degrees about a base of 2.11°; `3e-2` already
clears 60× there and a larger step buys nothing but truncation error.

| arm | contents | primals |
|---|---|---|
| **S2b-pV** | baseline + `patchV` idx1 central at `{1e-2, 3e-2}` + **the trivial baseline (below)** | 1 + 4 + 2 = **7** |
| **S2b-tw** | baseline + `twist` idx 0/3/6 central at `{1e-2, 3e-2, 1e-1}` | 1 + 18 = **19** |

Both S2b arms use a **hand-written FD driver, not `prob.check_totals`**, because `check_totals` cannot
be restricted to individual DV indices and would spend 19 primals to grade 9 components when 4 are
wanted. The driver calls `prob.run_model()` at the baseline and at each perturbed design, reads
`prob.get_val("scenario1.aero_post.CD")`, and forms `(CD⁺ − CD⁻)/(2s)`. **It computes no adjoint**,
which is also why its memory envelope is a primal envelope (§5, P-RSS).

**THE REGISTERED TRIVIAL BASELINE (`DAFOAM_CHARTER.md` §4; `VERIFICATION_CHARTER.md` §2c).**
The predecessor registered a wrong-step arm at `step=1e-8` and **never launched it** (its §6.5,
Amendment 4, verdict `PENDING`). **It is named, inherited and bought here**, on one component that
fits the ceiling: **`patchV` idx1, central, `step=1e-8`, patched image, otherwise identical**, folded
into S2b-pV as 2 extra primals (~2.3 core-min). Its clearance is `C(1e-8) = 9.017e-3 / (9.00e-6/2e-8)`
= **2.0e-5×**, i.e. the signal is fifty thousand times below the noise. **Prediction P9 below.**
It is not declined; the predecessor's `PENDING` is closed by this item.

### 4.3 Priority order, so a stop at the ceiling is principled and not arbitrary

**S1a → S1b → S1c → S1d → S2b-pV → S2a-pV1 → S2a-t0 → S2b-tw → S2a-t3 → S2a-t6.**

`S2b-pV` and `S2a-pV1` come first among the Stage-2 arms because together with the stored adjoint
they close the **calibration triangle** on the one component where all three references exist; a stop
after them still leaves this item with a genuine charter-§2 result. Arms not reached are reported
`PENDING` by name with their price, never absorbed.

## 5. Predictions and falsifiers — bands, committed before any launch

### P1 — S1a, the primal at 6,000 iterations. **PREDICTED: it stagnates; the gate FAILS.**

> **Predicted:** `primalMaxRes` at iteration 6,000 lies in **[3e-6, 1.2e-5]** — i.e. within a factor
> of ~2 of its value at 1,000 (5.909e-06) and **nowhere near** `primalMinResTol` 1e-8; the string
> `satisfied the prescribed tolerance` appears **zero** times; the ratio to tolerance stays
> **> 100**, so the shipped `primalMinResTolDiff 1.0e2` guard fires and the arm returns `rc=1`.
> **Basis:** §1.1's trace — `nuTilda initRes` flat within ±4% over iterations 100→1000, all-equation
> max flat within ±5% over 400→1000. **Band width chosen to be falsifiable**: a factor-2 window
> around a quantity that has not moved by more than ±5% in 900 iterations.
>
> **FALSIFIER:** `primalMaxRes` < 1e-6 at any iteration ≤ 6,000, or the tolerance line printing.
> Either fires ⇒ P1 **REFUTED**, and the reference is then bought at the converged primal instead
> (§6 gate branch A), which also obliges a **fresh adjoint arm** (+~11 core-min, inside the ceiling)
> because the stored adjoint would then be at the wrong primal state.

### P2 — S1a, the wobble at 6,000 iterations. **PREDICTED: no material improvement.**

> **Predicted:** CD peak-to-peak over the last 200 of 6,000 iterations lies in **[3e-6, 1.5e-5]**,
> i.e. the same order as the 9.00e-6 measured at 1,000 and **not** 5× smaller. Reported at 1,000 /
> 2,000 / 4,000 / 6,000 so the trend, not just the endpoint, is on the record.
> **Basis:** a residual limit cycle at fixed amplitude produces an objective limit cycle at fixed
> amplitude; the residual amplitude is measured flat.
>
> **FALSIFIER:** p2p ≤ 1.8e-6 (a 5× improvement). That would mean the wobble *is* iteration-limited
> and the cheapest repair to the FD reference is simply a longer primal — a materially different and
> better outcome than the one predicted, and it would be reported as such.

### P3 — S1d, solve-to-solve repeatability. **PREDICTED: `δ_repeat` is the same order as the wobble.**

> **Predicted:** `δ_repeat = |CD_2 − CD_1|` at an identical design point lies in **[1e-7, 2e-5]**,
> with a central expectation near **5e-6** — the same order as the within-run p2p, because the second
> solve starts warm from the first solve's limit-cycle phase rather than from `0/`.
> **Basis:** the two available cold-start data points are *bit-identical* between images
> (`0.03506349413916734` on both), so the solver is deterministic; what is unmeasured is whether a
> *warm* restart lands on the same limit-cycle phase. Contaminated-vs-cold in the predecessor moved
> CD by **1.18e-5** (`0.03505167364477857` warm vs `0.03506349413916734` cold, §3.1) — that is the
> one prior measurement of a start-state effect on this case and it sits at the top of the band.
>
> **FALSIFIER (either direction, and both are informative):** `δ_repeat` < 1e-8 ⇒ the FD instrument is
> far quieter than the within-run wobble suggests, the noise floor should be recomputed from
> `δ_repeat` and **more** of the predecessor's components become gradeable. `δ_repeat` > 2e-5 ⇒ the
> instrument is *noisier* than the predecessor assumed, and the predecessor's 4.5e-3 floor was an
> **under**-estimate — which would make the FD repair harder, not easier, and would be reported as
> the finding it is.

### P4 — S1b / S1c, forward-AD reachability. **PREDICTED: both run.**

> **P4a (`patchV` idx1, no warp):** predicted `rc=0`, an ` ADF-Deriv:` value printed on the CD line,
> and `prob.get_val` returning a finite non-zero number. **Confidence: high.** `DARhoSimpleCFoam` is
> compiled into `libDASolverADF.so` (28 symbols) and the binding imports (§1.2).
> **P4b (`twist` idx0, warp-crossing):** predicted `rc=0` likewise. **Confidence: lower** — it
> additionally requires `DVGeo.totalSensitivityProd` and `IDWarp.warpDerivFwd` to work under Edit 4.
>
> **FALSIFIERS, and each is a Charter-§2 finding in its own right rather than a failed arm:**
> an `ImportError` on `dafoam.libs.ADF`; a DAFoam `Error(...)` from `calcFFD2XvSeeds`; no `ADF-Deriv:`
> line; a returned derivative of exactly `0.0` (the signature of a seed that never reached the tape);
> or an OpenMDAO `fwd`-mode warning path being taken (`mphys_dafoam.py` raises
> *"the forward mode functions are not implemented for DAFoam!"* in **11** places — all of them in
> `compute_jacvec_product`/`apply_linear`, none of them on the `run_model` path this item uses, which
> is why the protocol is `run_model`-per-seed and not `compute_totals` in `fwd` mode). **If forward
> mode does not run, that is recorded with the exact error and Stage 2 proceeds FD-only.**

### P5 — the forward-AD cost factor. **PREDICTED 2.0×–4.0× the plain primal, per iteration.**

> Measured from the 10-iteration probes against the plain primal's measured 4.74 s for its first 10
> iterations (`stock.log:540`). **FALSIFIER:** < 1.5× or > 6.0×. A factor above 6 would blow S2a's
> budget and S2a would be cut to `patchV` idx1 + `twist` idx6 only, disclosed.

### P6 — the forward-AD reference against the adjoint. **PREDICTED ≤ 1% on all four components.**

> **Predicted:** `|J_adj − J_ADF| / |J_ADF| ≤ 1%` on every subset component whose tangent is settled
> (P7's test), **and no sign flip on any of them** — i.e. the three components the FD called
> sign-flipped are predicted to be **correctly signed and correct in magnitude**, confirming the
> predecessor's *provisional* reading (its §6.3: *"what is inferred is that the analytic column is
> the better one"*) and converting it from an inference into a measurement.
> **Basis:** PAS 2019 §5.1 measures the DAFoam Jacobian-free adjoint to **10 digits** against a
> full-code-AD reference. The band is set 8 orders looser than that because this primal is in a limit
> cycle and its tangent will be too.
>
> **FALSIFIERS.** (a) Any component > 15% or any sign flip between adjoint and forward-AD ⇒ **the
> adjoint is wrong on that component**, the predecessor's §6.3 reading is REFUTED, and this is the
> single largest change to the standing picture this item could produce. (b) 5–15% ⇒ CONDITIONAL,
> per-component breakdown mandatory. (c) A forward-AD value that agrees with the *FD* column and not
> the adjoint on the sign-flipping components would mean the adjoint is the broken one — registered
> explicitly so that outcome cannot be reported as anything else.

### P7 — the tangent's own settling. **PREDICTED: the tangent limit-cycles too.**

> **Predicted:** the relative peak-to-peak of ` ADF-Deriv:` over the last 200 iterations of each S2a
> arm lies in **[1e-4, 1e-1]** of its endpoint value. **Basis:** a primal in a residual limit cycle
> drives its tangent at the same amplitude; there is no reason for the tangent to be quieter.
> **This is a number nothing on the record has, in either direction, and it is what decides whether
> forward AD is a *usable* reference on a non-converged primal or merely a *reachable* one.**
>
> **FALSIFIER:** relative p2p > 1e-1 ⇒ the tangent is as noise-dominated as the FD and forward AD does
> **not** rescue this rung — a genuine negative result, reported as `GATE FAIL` on the reference
> repair rather than dressed as a caveat. Relative p2p < 1e-4 ⇒ the tangent is *quieter* than the
> primal, which would be a surprising and reportable N-D fact.

### P8 — the FD sweep at the fixed step. **PREDICTED: two recovered, one flagged, one steady.**

> * **`twist` idx0 and idx3:** predicted to **change sign back to negative** at `s ≥ 1e-2` and to
>   reach `≤ 15%` against the adjoint at `s = 3e-2` or `1e-1`, with the estimate **flattening** across
>   the top two steps (the plateau signature of `A_stepsize_study.md`).
> * **`twist` idx6:** predicted to **remain FLAGGED at every registered step** — maximum clearance
>   **3.03×** at `s = 1e-1`, never reaching the registered `C ≥ 5` bar. **Registered consequence: FD
>   cannot grade `twist` idx6 on this rung at any step, and only the forward-AD reference can. This is
>   `DAFOAM_CHARTER.md` §2's clause arriving as an operational necessity rather than as good practice.**
> * **`patchV` idx1:** predicted to stay `≤ 5%` at both new steps and to move **closer** to the
>   adjoint than its 3.29% at `1e-3` (predicted `≤ 2%` at `1e-2`).
>
> **FALSIFIERS.** (a) `twist` idx0/idx3 not recovering their sign at any registered step ⇒ the
> sign flip is **not** a noise artefact and the adjoint's monotone-negative column is in doubt.
> (b) `patchV` idx1 leaving the ≤5% band at a step where its clearance is 20–60× ⇒ the step is in a
> truncation-dominated regime and the whole sweep is re-read as such. (c) Any perturbed primal raising
> `AnalysisError` at `s = 1e-1` ⇒ that step is dropped **for that component by name**, its row reads
> `NOT OBTAINED`, and no value is estimated or filled in.

### P9 — the trivial baseline, `patchV` idx1 at `step = 1e-8`. **PREDICTED > 50% error.**

> **Basis:** A1's own sweep reads **94.95%** at `1e-8` against 11.43% at `1e-3`, and the clearance
> here is **2.0e-5×** — the perturbation moves CD by ~9e-11 against a solve-to-solve noise of order
> 1e-6 to 1e-5. **FALSIFIER: ≤ 5%, which would invalidate every FD number in this item**, because a
> harness that "passes" at a step five orders below its own noise floor is not measuring a derivative.
> This closes the predecessor's `PENDING` (its Amendment 4).

### P-RSS — peak memory. **PREDICTED ≤ 4.5 GiB (FD/primal arms), ≤ 8.0 GiB (forward-AD arms).**

> **The predecessor's 9.787 GiB is an ADJOINT figure and does not transfer.** Read from the
> predecessor's own record-only sample file (`rss_stock.txt`, using field **3**, not the buggy field
> 4 — see §8): the container sat at **0.637 GiB** through setup, was at **3.197 GiB** during the
> baseline primal, and only crossed 4 GiB **after** the primal ended and `dRdWT` assembly began,
> reaching 7.396 GiB and then jumping to 9.768 GiB inside the KSP solve. **No arm in this item
> computes an adjoint** (unless P1 is refuted), so the primal envelope is what binds.
> Forward-AD arms instantiate **two** solvers (`solver` + `solverAD`, `pyDAFoam._initSolver`), the
> second in forward mode, which stores a tangent per state and **no tape** — hence 8.0 GiB, not 12.
> **Hard ceiling 12 GiB per arm** (`--memory=12g`). **FALSIFIER: any sample above 12 GiB** ⇒ over
> budget, the observation is recorded, and **no further arm is launched**.

### P-COST — **PREDICTED 74 core-min total.** See §7. **FALSIFIER: > 120 core-min**, the hard ceiling.

## 6. THE STAGE-2 GATE — written now, before S1a runs

**Branch A — P1 REFUTED (the primal converges by 6,000 iterations).** Stage 2 runs at the converged
`endTime`, the noise floor is recomputed from the new p2p, the FD steps are re-selected by the §4.2(b)
rule at that floor, **and a fresh adjoint arm is added** (+~11 core-min) because the stored adjoint
belongs to the `endTime 1000` configuration. Reported as a positive surprise.

**Branch B — P1 HELD (the primal stagnates), the expected branch.** Stage 2 runs at `endTime 1000`
and launches iff **both** sub-gates below are evaluated; each independently enables its half:

* **Gate B-FD (enables S2b-pV, S2b-tw).** Passes iff, with `η` as measured by §4.2(b)'s rule,
  **at least 2 of the 4 subset components have some registered step with `C(s) ≥ 5`.** Pre-computed
  at `η = 9.00e-6`: 3 of 4 qualify (`twist` 0 at 14.0×/46.7×, `twist` 3 at 6.74×/22.5×, `patchV` 1 at
  20.0×/60.1×). **Therefore Gate B-FD fails only if S1a/S1d measure `η > 8.0e-5`** — the value at
  which `twist` idx0 drops below 5× at `s = 1e-1` and only `patchV` idx1 survives. That threshold is
  registered now as the gate's arithmetic, not chosen later.
* **Gate B-AD (enables S2a-*).** Passes iff **at least one** of S1b/S1c returned `rc=0` with a finite
  non-zero ` ADF-Deriv:` for CD. If only S1b passed, S2a runs the `patchV` seed only and the three
  `twist` seeds are `BLOCKED` with the recorded reason. If only S1c passed, S2a runs the `twist`
  seeds only.

**Branch C — both sub-gates fail.** **STOP.** No Stage-2 arm is launched. The item is reported
`GATE FAIL` on the reference repair, with the measured reason, the money not spent, and the statement
that the A6 N=16 adjoint remains **unverified except on `patchV` idx1 at 3.29%** — which is exactly
what the predecessor already says, and this item will have bought the proof that it cannot be
cheaply improved rather than the improvement.

**Grading rule, registered before any reference exists.** Per component the **best reference** is:
forward-AD if its own settling test passes (P7: relative ` ADF-Deriv:` p2p over the last 200
iterations ≤ 5% of the endpoint value); else FD at the registered step with the **highest** clearance
among those with `C ≥ 5`; else **the component is FLAGGED, named, and excluded from every aggregate**.
Grading band (`DAFOAM_CHARTER.md` §2, `A_stepsize_study.md` §"Recommended FD tolerance"):
**PASS ≤ 5% with zero flagged components among those graded / CONDITIONAL 5–15% with a mandatory
per-component breakdown / FAIL > 15% or any sign flip, regardless of the aggregate.**
The aggregate, if quoted, is named as the statistic it is — this lab's vector-relative error
`‖J_an − J_ref‖ / ‖J_ref‖` over the graded subset — and is **never** compared against the DAFoam
papers' per-component average (`DAFOAM_CHARTER.md` §2).

## 7. Cost — registered before the spend, ceiling 120 core-min hard

**Basis, measured, from the predecessor's own graded arm** (`stock.log`, `ledger.txt`): 1,676 s wall
for 19 primals + one 517-iteration adjoint at np=1 = **27.933 core-min**. Decomposed from the log's
`ExecutionTime` deltas: **cold primal 72.17 s** (1,000 iterations), **warm perturbed primal 56–58 s**,
**adjoint 616 s**, container setup ≈ 11 s. Per-iteration cost after the first 100: **0.0748 s/iter**.

**Billing convention.** Core-minutes are quoted **at np = 1** — `ranks × wall` — which is the basis
the predecessor's ledger and cost table use (1,676 s → 27.933 core-min) and the only basis on which
this item's figures are comparable to it. **Disclosed, not buried:** the containers are capped at
`--cpus=4`, and `COMPUTE_BUDGET_CHARTER.md`'s "cores × wall, full occupancy for the whole clock"
convention read against the **cap** rather than the **rank count** would multiply every figure below
by 4. The np=1 basis is used for continuity with the row this item extends; the ×4 reading is stated
here so a reader can convert.

| # | arm | basis | wall (predicted) | core-min |
|---|---|---|---|---|
| 0 | pre-launch image inspection (already spent) | 4 × `docker run --rm` of `ls`/`nm`/`grep`/`import` | ~24 s | **0.4** |
| 1 | **S1a** primal, 6,000 iterations | 4.74 + 5,900 × 0.0748 = 446 s + 60 s setup | 506 s | **8.5** |
| 2 | **S1b** fwd-AD probe, 10 iterations | 60 s setup + 3× × 4.74 s | ~75 s | **1.3** |
| 3 | **S1c** fwd-AD probe, 10 iterations (+ warp seed) | 60 s setup + 3× × 4.74 s + `warpDerivFwd` | ~90 s | **1.5** |
| 4 | **S1d** repeatability, 2 primals | 60 + 72 + 57 s | 189 s | **3.2** |
| | *Stage 1 subtotal* | | | **14.5** |
| 5 | **S2b-pV** FD, 7 primals | 60 + 72 + 6 × 57 s | 474 s | **7.9** |
| 6 | **S2a-pV1** fwd-AD, 1,000 iterations | 60 s + 3.0 × 72 s | 276 s | **4.6** |
| 7 | **S2a-t0** fwd-AD | 276 s | | **4.6** |
| 8 | **S2b-tw** FD, 19 primals | 60 + 72 + 18 × 57 s | 1,158 s | **19.3** |
| 9 | **S2a-t3** fwd-AD | 276 s | | **4.6** |
| 10 | **S2a-t6** fwd-AD | 276 s | | **4.6** |
| | *Stage 2 subtotal* | | | **45.6** |
| | **subtotal** | | | **60.5** |
| | contingency: one re-stage / one retried arm, +22% | | | **13.5** |
| | **REGISTERED TOTAL** | | | **74.0** |
| | **HARD CEILING** | | | **120.0** |

**$ at \$0.0513/core-hour: registered 74.0 core-min = 1.233 core-h = \$0.0633. Ceiling 120 core-min =
\$0.1026.** Both are far below the \$25 line of `DAFOAM_CHARTER.md` §12, so no Sanaa listing is
required on cost grounds. **If the running total reaches 120 core-min, the remaining arms are not
launched, are reported `PENDING` by name with their price, and the shortfall is reported rather than
absorbed** (`COMPUTE_BUDGET_CHARTER.md`: *"a budget overrun stops the run. It does not get a new
budget"*).

**Contention risk, disclosed in advance because it is billed.** At the time of filing the box carries
`load average: 18.06` from another family's `buoyantBoussinesq*` jobs and two other DAFoam lanes share
an 8-core team cap. Under `ranks × wall` billing **every minute of contention is billed as
compute this item did not receive.** Wall inflation of 1.5–2× is plausible and is inside the ceiling
for Stage 1 but not for both Stage-2 halves; the §4.3 priority order exists for that case.

## 8. Bounded execution — no kill is ever needed

* **Iteration caps are the bound, not a timer.** `endTime` caps every primal. Every arm terminates on
  its own. `timeout` on each `docker run` is a backstop set at **3× the predicted wall**, never the
  mechanism.
* `--rm`, `--cpus=4` (the lane cap), `--memory=12g` (the RSS cap), foreground, np=1, `-x PYTHONPATH`.
* **RSS monitoring is record-only. It never kills anything.** A polling loop writes
  `docker stats --no-stream` samples to `rss_<arm>.txt`. **The peak extractor reads field `$3`, not
  `$4`** — the predecessor's `run_arm.sh` read `$4`, which is the literal `/` in
  `<ts> <arm> 9.787GiB / 12GiB`, and that is why both of its ledger lines read `peak_rss=unmeasured`
  and why a wrong 7.396 GiB reached its §5 before being corrected in its §6.6 (its Amendment 3). Fixed
  here at the source.
* **Launch condition, bounded loop, per arm:** `load1 ≤ 8` **and** `MemAvailable ≥ 12 GiB`, polled
  every 20 s for at most **40 minutes**. If the window does not open, the arm is **not** launched, the
  item records **BLOCKED on host contention** with the measured load and the owner of it, and no cap
  is quietly raised. Any override of `load1 ≤ 8` is a **departure** and is disclosed in `RESULTS.md`
  Amendments with the measured load, or it does not happen.
* **Cold start per arm:** a fresh `rsync`/`cp -a` of `base/`, then `rm -rf processor* dRdWColoring_*.bin`,
  then the continuity-error assertion of §2. No arm reuses another arm's directory.
* Every arm writes one ledger line: `ARM IMG rc wall_s ranks core_min peak_rss`, plus the asserted
  `IDWARP_SO_MD5`, `transonicPCOption` and `nProcs` greps.

## 9. What this item will NOT be able to see — stated before it runs

1. **It is not 579,072 cells, and it is not N=29.** Nothing here re-opens the full-size `BLOCKED`
   verdict or Sanaa's N=29 gate on its own. It can only change the *input* to that decision.
2. **`shape` is still not graded**, and neither are `twist` idx 1, 2, 4, 5. Four components of nine.
   Any statement this item makes is about those four and is not carried to the others.
3. **The forward-AD reference is NOT independent of the IDWarp rotation patch.** The patch record
   (`PATCH_getRotationMatrix3d.md` §4) says `GETROTATIONMATRIX3D_D` — the forward/tangent routine
   `warpDerivFwd` calls — carries "the dual defect" and **was patched**, and its unit test **T5
   forward-mode vs reverse-mode agrees to 4.3e-15**. So on `dafoam-idwarp-rot:v1` the forward and
   reverse rotation derivatives are the *same* corrected quantity. **Consequence, stated plainly:
   forward AD here independently checks the DAFoam flow-solver derivative chain and the FD reference;
   it CANNOT detect an error in the rotation term itself, because both sides of the comparison
   contain the same patched term.** This item also does not re-verify at the `.so` level that the
   built library contains the forward-mode hunk — it asserts the md5 and cites the record.
4. **`np = 1` only.** The decomposition axis is absent by construction (`DAFOAM_CHARTER.md` §5).
5. **Regime 2 of the rotation defect stays invisible**: every arm sits at the undeformed baseline
   where the `sqrt(eps)` guard is guaranteed to fire.
6. **A settled tangent is not a correct tangent.** P7's settling test measures whether the forward-AD
   value has stopped moving, not whether it is right. The only cross-check on that is the calibration
   triangle at `patchV` idx1 — one component.
7. **It cannot separate FD truncation error from FD noise** at the large steps. A `twist` estimate
   that flattens across `3e-2` and `1e-1` is evidence of a plateau; a single step is not.
8. **It does not re-run the adjoint** (unless P1 is refuted), so it inherits the predecessor's adjoint
   column exactly as recorded and any error in that transcription would propagate. The source lines
   are cited in §4.2 so the transcription is checkable.

## 10. Verdict vocabulary

`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING` — the six tokens, adopted
for DAFoam by `DAFOAM_CHARTER.md` §8 from `CLOSURE_MODELLING_CHARTER.md` §12. No other word grades an
arm here. A verdict is valid only against a falsifier written in this file before the run.
An arm stopped by the host-contention launch condition is `BLOCKED`, never `GATE FAIL`. An arm not
reached at the ceiling is `PENDING`, never absorbed. A stop is not a measurement
(`DAFOAM_CHARTER.md` §7).

**This is a PATCHED-image row and it says so. It does not replace, merge with, or re-grade the
shipped-toolchain row at `../rung_n16_np1/RESULTS.md` §6.2.**

**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**
