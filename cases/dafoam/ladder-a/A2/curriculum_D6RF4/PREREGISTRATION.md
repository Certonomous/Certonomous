# ⚠ DRAFT — NOT A REGISTRATION, NOT FROZEN, NOT ENQUEUED

**`D6RF4` — A2 MACH wing, multipoint FD verification. Successor to `D6RF3`.**

Drafted 2026-09-06 by a `lab-lane` on the dafoam-supervisor's brief. **The freeze and the enqueue
belong to the dafoam-supervisor and are not taken here.** No gate, threshold, cap or label in this
file is registered until that supervisor freezes it by sha.

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed or uploaded anywhere
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**`primalMinResTol` AND `primalMinResTolDiff` DO NOT MOVE IN THIS ITEM.** They are carried forward
byte-identical at `1e-08` and `1000`, the effective accept floor stays `1.0e-05`, and §2.4 registers
an executable refusal that reads both values back out of the container log and stops the grading if
either differs. Whether a successor may ever register a different acceptance rule is **escalated to
Sanaa and unruled**; this item does not pre-empt it and takes no position on it.

---

## 0. WHY A SUCCESSOR, AND WHAT THIS ITEM ACTUALLY CHANGES

`D6RF3` (frozen `9c079a84`, graded 2026-09-05, **`NOT A RESULT`**, **2.067 core-min of a 480.0
core-min cap**) died at its first point-primal. The primal **converged in every physical sense** and
printed `End`, and was then refused by DAFoam's **post-`End` acceptance test** (`N-D42`): measured
`primalMaxRes` **`1.316217833e-05`** against the accept floor `primalMinResTol ×
primalMinResTolDiff` = `1e-08 × 1000` = **`1.0e-05`**. **The miss is `1.3162×`, i.e. over the floor
by 31.6 %** (`N-D43`; the `1316×` figure that circulated first divided by the tolerance alone and is
wrong).

**This item changes exactly one thing about the primal, and it is not the acceptance rule.**
`D6RF3`'s residual had **plateaued** — §1 shows the arithmetic — and the plateau's height is set by
the **linear-solver stopping rule in `system/fvSolution`**, not by the iteration count and not by the
acceptance bar. `D6RF4` tightens that stopping rule. **A tighter inner solve is a strictly better
solve at an unchanged bar**; it is working the case, which Sanaa's 2026-09-04 ruling requires, and it
is the same repair `DAFOAM_CHARTER.md` §3 incident (i) already records on `S1`, where *"the step was
never the problem; the primal's stopping rule was."*

**What this item may not conclude is in §9, and the first entry is that it may not conclude anything
about whether the accept floor is reachable in general.**

---

## 1. THE CENTRAL MEASUREMENT — THE RESIDUAL HAD **PLATEAUED**, AND MORE ITERATIONS BUY NOTHING

Source, single artifact, read in full:
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd/F_mp_20260905T222250Z_43793.log`.
The primal printed at `Time = 1` and then every 100 steps to `endTime = 1000` (`:1926`–`:2100`);
`SIMPLE: no convergence criteria found` (`:167`) confirms `endTime` was the only stopping condition.

### 1.1 `p initRes` across the whole run, and the per-100 decrement beside it

`primalMaxRes = 1.316217833e-05` **is** the `p initRes` at `Time = 1000`, exactly — so `p` is the
binding field and its trajectory is the whole question.

| `Time` | `p initRes` | decrement over previous 100 | ratio to previous decrement | `nuTilda initRes` |
|---|---|---|---|---|
| 1 | 9.9999999980e-01 | — | — | 1.000000000e+00 |
| 100 | 2.5886424110e-04 | 9.997411e-01 | — | 1.346497780e-05 |
| 200 | 1.8788410790e-05 | 2.400758e-04 | 0.0002 | 1.057423698e-05 |
| 300 | 1.3261702560e-05 | 5.526708e-06 | 0.0230 | 1.051985539e-05 |
| 400 | 1.3181947110e-05 | 7.975545e-08 | 0.0144 | 1.051238104e-05 |
| 500 | 1.3170071120e-05 | 1.187599e-08 | 0.1489 | 1.050918840e-05 |
| 600 | 1.3166454020e-05 | 3.617100e-09 | 0.3046 | 1.050717755e-05 |
| 700 | 1.3164476460e-05 | 1.977560e-09 | 0.5467 | 1.050585942e-05 |
| 800 | 1.3163514380e-05 | 9.620800e-10 | 0.4865 | 1.050499526e-05 |
| 900 | 1.3162764650e-05 | 7.497300e-10 | 0.7793 | 1.050468287e-05 |
| **1000** | **1.3162178330e-05** | 5.863200e-10 | 0.7820 | **1.050443706e-05** |

The log prints one block per 100 steps, so the *"last 20 consecutively"* the brief asked for does not
exist as data. **Stated rather than fabricated.** The last three sampled decrements are the tail, and
they are what the extrapolation is built on.

### 1.2 THE VERDICT: **PLATEAUED.** The arithmetic, written out

The per-100 decrements decay geometrically at the tail with ratio `r = 5.8632e-10 / 7.4973e-10 =
0.78204` (the previous ratio is `0.77928` — stable to three figures, so `r` is a measurement, not a
fit to two points).

Remaining descent available from **infinitely many further iterations**:

> `Σ = d₁₀₀₀ · r / (1 − r) = 5.8632e-10 × 0.78204 / 0.21796 = 2.1037e-09`
>
> **asymptotic `p initRes` = 1.3162178e-05 − 2.1037e-09 = 1.3160075e-05**

Against the requirement:

> **required descent** = `1.3162178e-05 − 1.0e-05` = **`3.162178e-06`** — **24.02 %** of the current value
> **available descent, from infinite iteration** = **`2.1037e-09`** — **0.01598 %** of the current value
> **`3.162178e-06 > 2.1037e-09` — shortfall factor `1503×`**

**The residual is not still descending toward the floor. It is asymptoting to `1.3160e-05`, which is
`1.3160×` the accept floor.** Iterating forever leaves the run failing by 31.6 %.

**The most optimistic arithmetic available, offered only to show it does not rescue the case:** if the
last observed rate `5.8632e-10` per 100 iterations persisted forever — which the decaying ratios
refute — the floor is reached in `3.162178e-06 / 5.8632e-10 × 100 = 5.393e+05` iterations, costing
`5.393e+05 × 0.01636 s × 4 ÷ 60 =` **588 core-min**, which already exceeds `D6RF3`'s own 480 core-min
cap. **Both the honest number and the dishonest one say no.**

> **THEREFORE THIS DRAFT PROPOSES NO ITERATION BUDGET, AND REFUSES TO.** There is no `endTime` at
> which this `fvSolution` reaches `1.0e-05`. A budget for more iterations would be a budget my own
> extrapolation contradicts.

### 1.3 WHAT SETS THE PLATEAU — MEASURED, AND IT IS THE LINEAR-SOLVER STOPPING RULE

`system/fvSolution` in the run tree
(`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd/F_mp/system/fvSolution`):

* `"(p|p_rgh|G)"` — `GAMG`, **`relTol 0.1`**, **`tolerance 0`**
* `"(U|T|e|h|nuTilda|k|omega|epsilon)"` — `smoothSolver`, **`relTol 0.1`**, **`tolerance 0`**, `nSweeps 1`
* `SIMPLE { nNonOrthogonalCorrectors 0; }`

`tolerance 0` means no absolute tolerance ever terminates an inner solve; **every equation stops at a
single 10× relative reduction and no tighter.** At `Time = 1000` every field sits at ~12× its own
inner-solve final residual, and the ratio is the requested `relTol` in every one:

| field | `initRes` | `finalRes` | `finalRes/initRes` |
|---|---|---|---|
| `U0` | 1.381820e-07 | 1.132916e-08 | 0.0820 |
| `U1` | 5.862106e-07 | 2.242738e-08 | 0.0383 |
| `U2` | 3.746856e-08 | 3.062485e-09 | 0.0817 |
| `he` | 7.035339e-09 | 3.089045e-10 | 0.0439 |
| **`p`** | **1.316218e-05** | 1.098440e-06 | **0.0835** |
| **`nuTilda`** | **1.050444e-05** | 4.697819e-07 | **0.0447** |

**Six fields, one signature.** At the outer fixed point the state increment *is* the inner solve's
leftover error, and the next outer iteration reports it back as `initRes`. The floor is the inner
tolerance, amplified.

### 1.4 CORROBORATION FROM THE CASE THAT **REACHED** THE SAME BAR — ARTIFACT, NOT ARGUMENT

`N-D43` records that in the **same image and at the same `1e-08 × 1000` floor**, all eight `S1FDP`
primals exited `rc=0` with the refusal banner absent. Its `fvSolution`
(`/home/ubuntu/certonomous-runs/S1-fd-plateau/cbfs_inv/system/fvSolution`) differs from `D6RF3`'s in
exactly the two places §1.3 names, and in the same direction:

| setting | `D6RF3` `F_mp` — **plateaus at 1.316e-05** | `S1FDP` `cbfs_inv` — **reaches the floor** |
|---|---|---|
| `p` `relTol` | **0.1** | **0.001** (100× tighter) |
| `p` `tolerance` | **0** | **1e-12** |
| `p` `minIter` / `maxIter` | absent | `5` / `200` |
| `U`/turbulence `tolerance` | **0** | **1e-09** |
| `nNonOrthogonalCorrectors` | **0** | **1** |

**Independent third corroboration for the corrector:** this mesh reports **`Mesh non-orthogonality
Max: 71.47582467 average: 11.65405026`** (log `:1910`) under `laplacianSchemes Gauss linear
corrected` / `snGradSchemes corrected`. With `nNonOrthogonalCorrectors 0` the explicit correction
term is lagged one outer iteration at a max non-orthogonality of 71.5°, and a lagged term is exactly
the kind of thing that pins a fixed-point residual above zero.

**Honest limit on the corroboration.** `S1FDP` differs from `D6RF3` in geometry, mesh, solver
(`DARhoSimpleFoam` vs incompressible), turbulence model and `endTime`. **This is a strong
artifact-backed hypothesis about the mechanism. It is not a measurement that the repair works, and
this item exists to make that measurement.** §3's `G-CONV` is where it is tested and §6's `F5` is
where it can fail.

### 1.5 A SECOND FIELD IS ALSO OVER THE FLOOR, AND A REPAIR THAT ONLY FIXES `p` DOES NOT PASS

`nuTilda initRes` at `Time = 1000` is **`1.050443706e-05` — `1.0504×` the floor.** `primalMaxRes` is a
maximum, so even a perfect repair of `p` leaves the run refused at `1.050×` unless `nuTilda` moves
too. **Every gate and report in this item is per field, never on `primalMaxRes` alone**, so this
cannot be missed a second time.

---

## 2. THE PER-POINT COMPARISON — **ONLY `cl04` RAN, AND THE OTHER TWO POINTS ARE UNMEASURED**

The brief's trap is real and the answer is that the trap has no data in it.

* **`Time = ` blocks in the whole log: 11, all one primal.** `Setting UMag = 100 AoA = 0.8829754496
  degs` appears **exactly once** (`:1900`). **One point-primal ran.**
* `CL` at `Time = 1000` is `0.3999751808` → the point that ran is **`cl04`** (CL target 0.4), the
  **lowest-lift and mildest** of the three.
* The refusal names `cl04.coupling.solver` and `STATUS.chain` reads
  `chain=STOPPED_AT_FIRST_NONZERO`. **`cl05` and `cl06` never received a primal.**
* The three `DAOption` dumps (`:333`–`:600`, `:941`–`:1208`, `:1547`–`:1814`) are **byte-identical
  under `diff`** — same `primalMinResTol 1e-08`, same `primalMinResTolDiff 1000`, same
  `normalizeStates { U 100; p 5000; T 300; nuTilda 0.001; phi 1; }`, same everything. The three
  points differ only in the angle of attack the CL-target constraint drives them to.

> **STATED AS THE LIMIT IT IS: `cl05` and `cl06` are `PENDING`, not "the same". No number exists for
> either.** That the numerics are identical and that `cl04` is the mildest point makes it
> *implausible* that the other two plateau lower — but implausible is not measured, and this item
> registers per-point rows (§3.1) so the successor reports three measurements rather than one and an
> inference. **`D6RF3` generalised nothing from `cl04`; neither does this.**

---

## 3. GATES — REGISTERED BEFORE COMPUTE, EVERY ONE POST-HOC

### 3.1 ⚠ `G-CONV` — **NEW.** The bar is the INHERITED accept floor, restated, not moved

> **`G-CONV`. For each point-primal the arm runs, the final-iteration `initRes` of EVERY field in
> `{U0, U1, U2, he, p, nuTilda}` must be `< 1.0e-05`, and the arm must exit `rc=0` with the string
> `Primal solution failed!` absent from its log.**
>
> **Threshold `1.0e-05` = `primalMinResTol × primalMinResTolDiff` = `1e-08 × 1000`, carried forward
> unchanged from `D6RF3`.** This gate does not introduce a bar; it makes the bar DAFoam already
> applies post-`End` gradeable per field, so a failure names the field instead of a maximum.
>
> **Reported beside the verdict, always, pass or fail:** the full per-field `initRes` table at the
> final iteration, per point; each field's ratio to `1.0e-05`; and the `p initRes` trajectory at the
> print interval, so the successor's reader can see plateau-versus-descent for itself rather than
> take this section's word for it.
>
> `PASS` if every field of every point-primal that ran is `< 1.0e-05`. `GATE FAIL` if any field of any
> point-primal that ran is `≥ 1.0e-05`. `NOT A RESULT` if a point-primal did not run, or if any field
> value is non-finite (§3.4).

**Registered prediction, before compute, so it can be wrong on the record:** with `p` at `relTol
1e-3` / `tolerance 1e-12` the inner residual falls ~100× further per outer iteration than at `relTol
0.1`; if §1.3's mechanism holds, the outer floor falls by up to the same factor, `1.3162e-05 →
~1.3e-07`. **The requirement is a `1.3162×` drop and the mechanism predicts up to `100×` — a margin
of roughly 76×.** Even a factor-2 realisation of the mechanism clears the bar. **If it does not clear,
that is a measurement this item is built to report, and §9 says what it may then conclude.**

### 3.2 ⚠ `G-SOLN` — **NEW.** The anti-cheat gate: prove we tightened convergence, not changed the physics

The one honest objection to §0's change is that a different `fvSolution` computes a different answer,
where `N-D42` establishes that `primalMinResTolDiff` computes the *same* answer and changes only the
label. **`G-SOLN` is registered so that objection is answered by measurement.**

> **`G-SOLN`. The tightened `cl04` baseline primal's `CD` must agree with `D6RF3`'s measured
> `CD = 0.0184758685` (log `:2098`, `Time = 1000`) to within `1.0e-03` relative, and its `CL` with
> `0.3999751808` to within `1.0e-03` relative.**
>
> **Predicted value, with the inequality written out:** the two solutions differ by the residual
> level, `O(1e-05)` relative. **`1e-05 < 1e-03` — predicted `PASS` with two decades of margin.**
>
> A `GATE FAIL` here means the `fvSolution` change **moved the solution** rather than converging it,
> and the item reports that as its finding: the repair would then be a different case, not a better
> solve, and no `G-CONV` `PASS` may be quoted as `D6RF3`'s answer.

### 3.3 CARRIED FROM `D6RF3` UNCHANGED — and the conjunction structure is carried deliberately

`G-OFF` ×3, `G-PRICE`, `G-FD` + band D, `G-DVL`, `G-CAPS`, `G1`, `R-RED` (reported, not gated),
`X-CDLOG` (reported, not gated — repaired at §4). Bands, thresholds and labels are `D6RF3`'s,
re-cited and not re-derived.

**The conjunction structure is preserved verbatim**, `d6rf3_grade.py:1162-1164`:
`verdict = PASS if in_band AND plateau_pass AND not sign_flip`. Band D at **5.0 %** binds **before**
the plateau bar at 10 %, so the tighter bar decides first — `DAFOAM_CHARTER.md` §21.4 names this the
structure where the loose plateau bar is redundant rather than load-bearing, and this item does not
migrate to the exclusion structure.

### 3.4 THE FINITENESS CLAUSE — CARRIED, AND STILL **STRICTLY RESTRICTIVE**

`D6RF3`'s `§3f` clause is carried unchanged: a non-finite value folds into its gate as **`NOT A
RESULT`** naming the artifact, the key and the value. **It can turn a `PASS` or a `GATE FAIL` INTO a
`NOT A RESULT` and can do nothing else; it can never produce a `PASS` and can never move a row in the
permissive direction** (`d6rf3_grade.py` `_nar_non_finite`, `:189-190`, `:328-336`). `G-CONV` and
`G-SOLN` are wired into the same fold, so the two new gates inherit the restriction rather than
sitting outside it. **This is a non-regression requirement, and §7 asserts it executably.**

---

## 4. ⚠ REPAIR 1 — `D6RF4-DEF-7`: `X-CDLOG` NEVER FIRED BECAUSE ITS SOURCE DOES NOT EXIST

**The defect, measured.** `X-CDLOG` (`d6rf3_grade.py:1319`, `report_cdlog`) reads
`points.<pt>.CD` from **`d6rf3_fd_endpoint.json`**. On disk the run tree holds
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd/F_mp/d6rf3_fd_endpoint.jsonl`
— 136 bytes, one line, `{"kind": "endpoint_dvs", "n_patchV": {...}, "n_shape": 96, "n_twist": 7,
"source": "/mnt/F_mp/OptView.hst"}` — and **no `.json` at all.** The row did not fire.

**And the precise shape of the defect is a token gap, not a missing file.** `report_cdlog`'s only
absent-source branch is `res.update({"reason": "ARM_DID_NOT_RUN", ...})`. **The arm DID run.** The
grader had one token for two different states and the run landed in the state it had no token for —
so the record could have read `ARM_DID_NOT_RUN` about an arm that consumed 2.067 core-min.

**The repair, two parts, both registered before compute:**

1. **The producer writes the gated artifact incrementally.** `d6rf4_fd_endpoint.py` writes
   `d6rf4_fd_endpoint.json` with the `points.<pt>.CD` block **as each baseline point-primal
   completes, before any FD leg begins**, and re-writes it after each subsequent leg. A run that dies
   at point *k* leaves the CD block for points `0..k−1` on disk and readable. The `.jsonl` stays as
   what it is — a progress log — and is never a gated source.
2. **Registered token set, three states, distinguishable:**
   * source file **absent** and the producing arm **did not run** → `X-CDLOG: NOT PRODUCED`,
     `cause = ARM_DID_NOT_RUN`, naming the arm.
   * source file **absent** and the producing arm **ran** → `X-CDLOG: NOT PRODUCED`,
     `cause = ARM_RAN_ARTEFACT_NOT_WRITTEN`, naming `d6rf4_fd_endpoint.json`, the arm, its `rc`, and
     the last leg that completed. **This is the state `D6RF3` actually hit and had no token for.**
   * source present, some points missing → the present points are reported; each missing point reads
     `NOT PRODUCED` by name. **A partial source reports partially; it never reports silently.**

**`X-CDLOG` stays REPORTED AND GATED BY NOTHING** — §2b's three registered reasons are unchanged, and
this repair gives a non-gating row a source that exists rather than promoting it. **The repair cannot
move a gate, by construction.**

---

## 5. ⚠ REPAIR 2 — `D6RF4-DEF-8`: A RUN-DERIVED BAR DOES NOT EXIST WHEN ITS PRODUCING LEG DOES NOT RUN

**The defect, measured.** `F1`'s yardstick is `eta_raw` — `|J − J_repeat|`, the primal's own
repeatability, **measured in the same run** by `baseline` vs `baseline_repeat`. `baseline_repeat`
never ran. **`F1` is `UNRESOLVED` because its bar does not exist** (`D6RF3/RESULTS.md` §4.3).

**And the virtue and the vulnerability are the same property.** `DAFOAM_CHARTER.md` §21.6 singles
this design out as *"the design this family should prefer, and it is already here"*, precisely
because a bar derived from the run **cannot be mis-sized against what it bounds** — the failure
§21.1 charges `S1FDP` with. That is correct and this item keeps the design. **What 2026-09-05 added
is the other half: a bar that is derived from the run does not exist when the run stops early.**

**The repair, three parts:**

1. **Order.** `baseline_repeat` runs **immediately after `baseline`, before any FD leg**, in every
   arm that has one. `eta_raw` then exists as soon as two primals exist — the cheapest possible point
   in the program. Priced in §8, not absorbed.
2. **Registered null reading, before compute.** Every run-derived falsifier and gate in this item
   declares, in this frozen file, exactly what it reads as when its producing leg does not run: the
   token, the field name, and the artifact the token names. For `F1`:
   `verdict = UNRESOLVED`, `bar_state = BAR_NOT_PRODUCED`, `producing_leg = "baseline_repeat"`,
   `bar_artefact = "d6rf4_fd_endpoint.json:eta_raw"`, `n_primals_completed = <k>`.
   **`UNRESOLVED` is an honest token; silence is not**, and a `null` with no cause beside it is
   silence.
3. **The rule generalised, as a table the grader emits and `freeze_check` asserts:**

| falsifier / gate | run-derived quantity | producing leg | token if that leg does not run |
|---|---|---|---|
| `F1` | `eta_raw` = `\|J − J_repeat\|` | `baseline_repeat` | `UNRESOLVED`, `bar_state=BAR_NOT_PRODUCED` |
| `F3` | `G-FD` aggregate, sign-flip count | the FD legs | `UNRESOLVED`, `bar_state=BAR_NOT_PRODUCED` |
| `F5` (§6) | per-field final `initRes` | `P_conv` tight baseline | `UNRESOLVED`, `bar_state=BAR_NOT_PRODUCED` |
| `X-CDLOG` | `points.<pt>.CD` | the baseline point-primals | `NOT PRODUCED` + §4's cause token |
| `G-SOLN` | tightened `CD`, `CL` | `P_conv` tight baseline | `NOT A RESULT` for want of an input |

**A row absent from this table is a run-derived quantity nobody registered a null reading for, and
`freeze_check` refuses on it** (§7).

---

## 6. FALSIFIERS — **§21-COMPLIANT.** Each names the gate it is predicted to fail, with the arithmetic

`DAFOAM_CHARTER.md` §21.3: a trivial baseline **names the gate it is predicted to fail**, that gate
**must be the one whose verdict the withdrawal clause withdraws**, and the pre-registration **shows
the predicted value beside that gate's own bar with the inequality written out.** A falsifier whose
predicted value does not fail its named gate **is not a falsifier**.

> ### `F5` — **NEW, and it is `G-CONV`'s trivial baseline.** THE DELIBERATELY WRONG SETTING
>
> **Probe:** the identical `cl04` baseline primal re-run with `D6RF3`'s **original** `fvSolution` —
> `p` `relTol 0.1` / `tolerance 0`, `nNonOrthogonalCorrectors 0` — one decade loose on `relTol` and
> the correction lagged, everything else held.
>
> **Named gate: `G-CONV`.** **That gate's own bar: `1.0e-05`.**
>
> **Predicted value: `p initRes = 1.3162e-05`.** This is not an estimate — it is
> `D6RF3`'s **measured** `primalMaxRes`, from the log named in §1, at the identical settings.
>
> **The inequality: `1.3162e-05 > 1.0e-05`. `G-CONV` FAILS at the wrong setting, by `1.3162×`.**
> The prediction is arithmetically bound to fail its named gate at zero compute, which is the exact
> property §21.1 found missing in `S1FDP`'s limb 2.
>
> **Withdrawal clause, and it withdraws the gate it names and no other:** if the wrong setting
> **also passes** `G-CONV`, then `G-CONV` is not measuring the linear-solver stopping rule, §1.3's
> mechanism is refuted, **`G-CONV`'s verdict is withdrawn**, and no claim about the repair may be
> made from this item.

> ### `F1` — CARRIED, with its null reading now registered (§5)
>
> **Named gate: none — `F1` is a REPORTED falsifier and moves `G-OFF` and `G-PRICE` in neither
> direction**, whose source was fixed before either number existed. Registered as a **reported
> probe**, which §21.3 explicitly permits; **no withdrawal clause rests on it**, so it is not counted
> as a falsifier for §21's purposes and this file does not claim it is.

> ### `F2` — the finiteness clause. CARRIED VERBATIM
>
> If the §3.4 mutation harness fails in **either** direction — a planted `NaN`/`±Inf` that does not
> produce `NOT A RESULT`, or an unmutated control that does — the clause is not established, and the
> item reports `NOT A RESULT` for want of a working guard rather than shipping gates it cannot trust.

> ### `F3` — the FD bright line. CARRIED VERBATIM, with §5's null reading attached
>
> If every arm runs clean and every gate reads, and `G-FD`'s aggregate lands **above 5.0 %** or with
> **≥ 2 sign flips**, that is the FD bright line failing on a multipoint composite objective — a
> physics finding this item is built to report, as `GATE FAIL` or `NOT A RESULT` respectively, never
> softened.

**`G-SOLN` (§3.2) carries its own arithmetic in the §21 shape and is graded, not merely reported:**
predicted `1e-05` relative against its own bar of `1e-03` — `1e-05 < 1e-03`, predicted `PASS`. It is
a **gate**, not a trivial baseline, so §21.3's withdrawal clause does not attach to it; the
arithmetic is shown because a gate whose predicted value nobody wrote down is a gate nobody sized.

---

## 7. INSTRUMENTS AND CONTROLS — THE THREE STRENGTHS ARE CARRIED, AND NON-REGRESSION IS EXECUTABLE

`DAFOAM_CHARTER.md` §18.3: every file this item EXECUTES or IMPORTS is enumerated, existence
asserted before any md5, and the frozen set verified against `git cat-file blob HEAD:` at execution.

**Carried without regression, each with the assertion that proves it:**

1. **The finiteness clause is strictly restrictive.** Asserted by the §3.4 mutation harness in both
   directions, and by a static check that `_nar_non_finite` has exactly one `verdict` assignment and
   its literal is `"NOT A RESULT"`.
2. **The planted controls import the literal function the gate calls.** `d6rf3_grade.py:265`
   `import d6rf3_cd_plant_control as cdc`, and the gate reads through `cdc.read_cd` — **the control
   plants into the same object the gate calls, not a copy of it.** Carried, and `freeze_check`
   asserts the identity of the imported symbol rather than the module name. `PLANT = 1.234e-03`,
   `PLANT_REL_TOL = 1.0e-9`, three controls, **none skippable**: a control that finds nothing to
   plant into REFUSES (`refuse("PLANT_FD", {"no_PLANNED_row_with_an_ok_s_hi_leg": True, ...})`)
   rather than reporting a silent pass. `CLAUDE.md` rule 3.
3. **`freeze_check`'s list is extracted from the code, not written from memory** — carried
   unchanged from `d6rf3_grade.py:463`, and extended to cover §5's null-reading table, so a
   run-derived quantity added later without a registered null reading refuses at freeze rather than
   at grading.

**New, and it is this item's own non-regression instrument:**

4. **`ACCEPT_FLOOR_UNMOVED`.** The grader reads `primalMinResTol` and `primalMinResTolDiff` **back
   out of the arm's own container log** and **REFUSES (exit 2)** unless they are exactly `1e-08` and
   `1000`. It also refuses if the product differs from `1.0e-05`. **This item cannot silently widen
   the bar it was forbidden to widen, and the refusal is executable rather than promised.** It is
   planted both ways per the `PRODUCT_WRITER` pattern: a mutated log with `primalMinResTolDiff 1e12`
   must trigger the refusal, and the unmutated log must not.

---

## 8. COST — PER ARM, IN THIS FILE, NOT IN A QUEUE ROW

**`cost_basis`: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER, NOT MEASURED**; the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **DERIVED**. Unit: core-minutes,
`wall_s × ranks ÷ 60`. Ranks `4`. `FRAME_ALLOWANCE_S = 90`.

### 8.1 The measured basis, and the multiplier derived from it

**Measured, from `D6RF3`'s own log and ledger:** one 1000-iteration point-primal, `ExecutionTime
19.71 s` at ranks 4 → **`1.3140` core-min of solve**; the whole one-primal arm `wall_s=31` →
`2.067` core-min gross, of which the container frame is the balance. `D6RF3/RESULTS.md` §7 states the
forward-useful figure directly: **"an `F_mp` arm that dies at its first primal costs ≈ 2.1 core-min,
of which ≈ 1.9 is container frame … that is what a successor should price a first-primal probe at."**
This section prices from that sentence and from the 19.71 s, both measured.

**The multiplier for the tightened inner solves, derived from §1.3's measured per-sweep reductions:**

* `p`, GAMG, one V-cycle achieves **0.083454**. Cycles to reach `relTol 1e-3`:
  `ln(1e-3)/ln(0.083454) = 2.7815` → **3 cycles**.
* worst smoothSolver field, `U0`, one sweep achieves **0.081987**. Sweeps to reach `1e-3`:
  `ln(1e-3)/ln(0.081987) = 2.7618` → **3 sweeps**.
* `nNonOrthogonalCorrectors 0 → 1` solves `p` **twice** per outer iteration.

> **Outer-iteration cost multiplier: `3 × 2 = 6`, registered as an UPPER BOUND.** It is an upper
> bound because the `×2` applies only to `p` while the `×3` applies to all fields, and because a
> tighter inner solve typically needs no more outer iterations. **This multiplier is DERIVED from
> measured reduction factors; it is not itself measured, and §8.3 says what happens if it is wrong.**

`endTime` stays **1000**. §1.1 shows the case is at its plateau by `Time = 400`, so 1000 is already
generous and is carried unchanged rather than raised — **this item buys no extra iterations.**

### 8.2 The arm, its legs and its cap

**`D6RF4` registers ONE arm at this freeze: `P_conv`.** The full `F_mp` FD arm and `REF_off` are
**not registered here** and are not priced here. **The reason is arithmetic, not caution:** `D6RF3`
priced `F_mp` at 155.70 core-min at the loose settings; at `×6` that is **934 core-min**, nearly
double `D6RF3`'s own 480 cap, and the multiplier is derived rather than measured. **It is not
defensible to buy a 934 core-min arm to learn a 17.9 core-min fact.** `P_conv` measures the actual
per-primal cost at the tightened settings, and the full arm is priced **from that measurement** in
this item's successor.

| leg | what it is | basis | core-min |
|---|---|---|---|
| `L1` | `cl04` baseline primal, **tightened** `fvSolution`, `endTime 1000` | `1.3140 × 6` | **7.884** |
| `L2` | `cl04` `baseline_repeat`, tightened — §5 repair 1, and it buys `eta_raw` | `1.3140 × 6` | **7.884** |
| `L3` | `cl04` baseline primal, **original** `fvSolution` — falsifier `F5` | `1.3140 × 1` | **1.314** |
| | container frame, one container for all three legs | `2.067 − 1.314` | **0.800** |
| | **estimate** | | **17.90** |

**Cap, by the family's ADOPTED form** `max(3.0 × estimate, 1.25 × (4/3) × estimate)` — **a MAX, never
a product** (`docs/LAB_STATE.md` block `S-29` §7.4):

`max(3.0 × 17.90, 1.6667 × 17.90) = max(53.70, 29.83) =` **53.70 → registered cap `54.00` core-min.**

**Cap-versus-deadline reachability check, run as arithmetic (`D6RF3` §4a.1's instrument, carried and
executable as `--cap-arithmetic`):**

| arm | `cap × 60 ÷ ranks` | `TMO + frame` | residual | max spend at `TMO` | cap headroom | predicted ≤ cap? |
|---|---|---|---|---|---|---|
| `P_conv` | `54.00 × 60 ÷ 4` = **810.0 s** | `720 + 90` = **810.0 s** | **`+0.0e+00 s`** | `720 × 4 ÷ 60` = **48.00 core-min** | **6.00 core-min** | `17.90 ≤ 54.00` **OK** |

**Residual exactly zero; neither stopping condition is decorative.** The 6.00 core-min of headroom is
the 90 s frame allowance re-expressed (`90 × 4 ÷ 60 = 6.00`). `TMO = 720 s`.

**Dollars, DERIVED at $0.0513/core-h, NOT MEASURED:** estimate 17.90 core-min = 0.2983 core-h →
**$0.0153**; at the 54.00 cap = 0.9000 core-h → **$0.0462**. Both far under the $25 pre-authorisation.
**An overrun stops the run; it does not get a new budget** (`CLAUDE.md` rule 12).

### 8.3 Estimate-versus-actual is OWED AT COMPLETION, and the `×6` is what it calibrates

`CLAUDE.md` rule 12: at completion this item compares the pre-registered estimate against the actual
in core-minutes from the ledger, states the ratio, attributes the gap (contention / waste /
misprediction, waste named separately and never absorbed), and lands a row in
`docs/COST_CALIBRATION.md` under that file's append rules and the rule-10 private-index protocol.

**The specific quantity this item calibrates, named in advance: the `×6` multiplier.** `L1` and `L3`
are the same primal at the two `fvSolution` settings in the same container, so their measured
`ExecutionTime` ratio **is** the multiplier, measured directly. **A completion report that does not
state `ExecutionTime(L1) / ExecutionTime(L3)` against the registered `6` is incomplete.**

**Lineage cost, carried and not written off:** `D6RF2` 4.6 + `D6RF3` 2.067 = **6.667 core-min**;
with `P_conv`'s estimate, lineage-to-date would reach **24.57 core-min, $0.021 derived.**

---

## 9. WHAT THIS ITEM MAY NOT CONCLUDE

1. **Nothing about whether `1e-08 × 1000` is reachable in general.** `N-D43` already records it as
   case- and budget-dependent: unreachable on this case at `D6RF3`'s settings, reached on `S1` CBFS at
   `endTime 2500`. A `G-CONV` `PASS` here says this case reaches it at these settings, and no more.
2. **Nothing about `cl05` or `cl06`** until a primal runs at each. §2 is a statement about `cl04`.
3. **Nothing about the acceptance rule.** `primalMinResTol` and `primalMinResTolDiff` are untouched
   and §7 instrument 4 refuses if they are not. Whether a successor may register a different
   acceptance rule is **escalated to Sanaa and unruled**, and a `G-CONV` `GATE FAIL` here is
   **evidence for that desk, not a licence to widen anything.**
4. **Nothing about the `×6` multiplier** beyond what `ExecutionTime(L1)/ExecutionTime(L3)` measures.
5. **Nothing about `D6RF3`, which stays `NOT A RESULT`.** This item does not regrade it.
6. **Nothing about the FD gradient.** `G-FD`, band D, `G-OFF` and `G-PRICE` have no inputs in
   `P_conv` and read as `NOT A RESULT` for want of an input, per §3.3 and §5's table.

---

## 10. STATE OF THIS DRAFT — WHAT A FREEZE STILL OWES

**Done here:** the plateau measurement and its arithmetic (§1); the mechanism and its two independent
corroborations (§1.3, §1.4); the second over-floor field (§1.5); the per-point census (§2); the two
new gates with their predictions written out (§3.1, §3.2); both defect repairs (§4, §5); the
§21-compliant falsifier whose predicted value is already measured (§6); the non-regression
instruments (§7); the budget with its multiplier derived from measured reduction factors and its
reachability identity at exactly zero residual (§8).

**Owed before any freeze, and NOT done here:**

1. **The tightened `fvSolution` written as a file**, diffed against `D6RF3`'s, with the diff in this
   item's directory — the settings are named in §1.4 but no file has been written.
2. **`d6rf4_grade.py`, `d6rf4_fd_endpoint.py`, `d6rf4_run_arm.sh`** derived from the `D6RF3`
   instruments, with `*_DELTAS_from_d6rf3.diff` beside each, per this family's convention.
3. **The instrument table with md5s** (`DAFOAM_CHARTER.md` §18.3), existence asserted before any
   hash.
4. **The `ACCEPT_FLOOR_UNMOVED` control planted both ways** (§7 instrument 4) and shown to fire.
5. **The supervisor's four personal §3 checks**, none of which a lane may discharge: the
   measurement-script diffs read **as diffs**; the crash triage; the big-claim verification —
   **§1.4's mechanism is a big claim and is corroborated, not measured**; and this file **committed
   before any compute**.
6. **The freeze itself, by sha, by the dafoam-supervisor.** Not taken here.

**SUBMISSIONS PARKED.**

---

## AMENDMENT — 2026-09-06T02:32:20Z — **`G-SOLN` GATE FAIL PROMOTES THE ITEM TO `NOT A RESULT`. RATIFIED AS A REGISTERED LADDER RUNG, NOT LEFT AS A LANE'S READING OF PROSE.**

**PRE-FIRST-COMPUTE AMENDMENT, `CLAUDE.md` rule 2.** Condition stated and **CHECKED BY EXECUTION in this invocation**: the run root is **ABSENT**; this item has burned **0 solver core-minutes**. **After first compute this could not have been made.**

### THE THING BEING RATIFIED, AND WHY IT NEEDED A SUPERVISOR

The building lane implemented §3.2's registered consequence as `compose` **rung 3b** — a `G-SOLN` `GATE FAIL` promotes the item to `NOT A RESULT` — and then **said in terms that this was its reading of prose and not something the draft states as a ladder rung**, and asked for ratification.

**That escalation was correct and it is the behaviour I want.** A ladder rung decides what token an item reports. **Deriving one from prose is interpretation, and interpretation of a registered consequence is not a lane's to make** — however obviously right it looks, and this one does look obviously right.

### RATIFIED, WITH THE REASONING ON THE RECORD RATHER THAN MERELY AGREED

> **`G-SOLN` `GATE FAIL` ⇒ ITEM `NOT A RESULT`. Registered here as rung 3b.**

`G-SOLN` establishes that the solver settings **are the registered tightened ones**. If it fails, then whatever `G-CONV` measured, **it measured a DIFFERENT CONFIGURATION from the one registered.** A `G-CONV` `PASS` under a failed `G-SOLN` is therefore not evidence about the registered case at all, and quoting it would **attach a number to a case nobody registered** — which is §3.2's own sentence, *"no `G-CONV` PASS may be quoted as D6RF3's answer"*, in ladder form.

**It is STRICTLY RESTRICTIVE and that is why it is safe to ratify pre-compute:** it can only turn a `PASS` or a `GATE FAIL` **into** a `NOT A RESULT`, never the reverse — `CLAUDE.md` rule 5's own permitted direction of travel. **It cannot rescue a row and cannot manufacture a pass.**

**NOTHING ELSE MOVES.** No band, threshold, cap, deadline, ceiling, label or prediction changes. `primalMinResTol` and `primalMinResTolDiff` remain **untouched everywhere**, and whether a successor may ever register a different acceptance rule remains **escalated to Sanaa and unruled** — `ACCEPT_FLOOR_UNMOVED` makes that boundary executable rather than promised, and it refuses **tightening as well as loosening**, because the registered value is a value and not an inequality.

### ⚠ CARRIED INTO THIS ITEM'S FREEZE FROM TONIGHT'S W3S EXPERIENCE

**Every freeze act destroys the controls that assert the pre-freeze state.** On W3S, two supervisor acts killed **three** controls in sequence, each discovered only after the previous was repaired — and **the fourth instance was not a control at all but PROSE**, a launcher first-screen still reading *"IT LAUNCHES NOTHING"* on a file that could by then start a container. **The near-miss worth carrying: that item's selftest had a zero-compute guarantee resting on a disabled flag, so raising the flag would have made `--selftest` start containers** had its fixture not independently placed a refusal ahead of every `docker run`.

**So this item's freeze is preceded by a pre-emptive sweep of three categories** — controls whose premise the freeze changes, prose asserting the pre-freeze state, and **any safety property currently resting on a value the freeze changes** — replanted **before** the act rather than repaired after it. `d6rf4_run_arm.sh` carrying `PERMISSION=NOT_FROZEN` and aborting **rc 3 before any staging** is the right shape — *"do not enqueue is an exit code, not a sentence"* — and the sweep must establish whether any drive's zero-compute property depends on it.

**AND A NAMED HAZARD, WHICH HAS NOW PAID TWICE IN ONE NIGHT: DUPLICATE ASSIGNMENT WHERE THE LAST WINS.** This item's own drives caught `MD5_ANCHOR_GATE` **assigned twice in the launcher with the stale value second** — it would have won and aborted staging at rc 4 — and it was caught **only because the refresh asserts a hit count of exactly one**. The same shape appeared in W3S, where `LAUNCH_ENABLED=0` occurred **four times** and a uniqueness assertion refused rather than editing the wrong line. **Pin the count, not the appearance (L-493).**

**SUBMISSIONS PARKED.**

### CORRECTION — 2026-09-06T02:34:27Z — **ONE CITATION IN THE SECTION ABOVE WAS DELETED BY THE SHELL THAT WROTE IT, AND THE MECHANISM IS WORTH MORE THAN THE TYPO**

**The corrupted line is repaired in place above** (this document is UNFROZEN and pre-first-compute, so rule 2 permits it outright; nothing frozen is edited). It read *"never the reverse —  rule 5's own permitted direction of travel"* with a missing citation and a doubled space. It now reads **`CLAUDE.md` rule 5**. **No meaning changed; a citation was restored.**

**WHAT HAPPENED, because it will happen to somebody else tonight.** The section was written through an **unquoted shell heredoc** (`<<EOF`, not `<<'EOF'`), which was necessary to interpolate the timestamp. **In an unquoted heredoc the shell performs command substitution on backticks — and markdown prose is made of backticks.** The span `` `CLAUDE.md` `` was executed as a command, failed with `CLAUDE.md: command not found`, and **substituted the empty string**, silently deleting the citation from the committed text.

> **THIS IS THE `git commit -m` BACKTICK TRAP IN A NEW PLACE, AND IT IS WORSE HERE.** There, the commit loudly never runs. Here **the write SUCCEEDS and the artefact is quietly wrong** — and the failure is asymmetric in a way that matters: a backtick span naming something that is **not** a command deletes itself and leaves a scar you can grep for (a doubled space); a span naming something that **is** a command — `` `date` ``, `` `ls` ``, `` `pwd` `` — **injects its output into the record and leaves no scar at all.**

**How it was caught, and it was luck of the honest kind:** the shell printed `CLAUDE.md: command not found` in the invocation's own output, and that one line was read rather than skimmed past. **Had the span been `` `date` ``, nothing would have printed and the corruption would have entered the frozen record silently.**

**Scoped rather than assumed.** Every section appended to this family's documents tonight was scanned for the signature (a mid-line multi-space run) inside its own bounds: `DAFOAM_CHARTER.md` §21, `A1WRT3` §13, `D6RF3` §12 and §13, `A1WRT2` §13, `N-D43`, and the board blocks — **all clean; this was the only instance.** They survived because their backticks were escaped (`` \` ``); this one span was not.

**The rule this supports, and it costs nothing:** **write markdown through a QUOTED heredoc (`<<'EOF'`) and substitute variables afterwards** — never through an unquoted one. A document is not a shell string, and the shell cannot tell the difference.

---

## AMENDMENT — 2026-09-06T03:51:07Z — **FOUR RULINGS: the unregistered `memory_floor_gb`, the banner that still denies this document's own freeze, the unregistered image identity, and two corrections against my own figures**

**PRE-FIRST-COMPUTE, `CLAUDE.md` rule 2.** Condition stated and **CHECKED BY EXECUTION in this invocation**: all three candidate run roots **ABSENT**, **0 solver core-minutes**. **No band, threshold, cap, deadline or label moves.** One field that this document never carried is **registered for the first time** — that is an addition, not a move.

### 1. `memory_floor_gb` = **20.0 (GiB, unconverted)**, and the DERIVATION is registered with it because it is not a measurement

**The lane refused to fill this from the launcher and was right to refuse.** `--memory 20g` is the **cgroup CEILING** — a bound on what the container may consume. **`memory_floor_gb` is a FLOOR on host `MemAvailable`** which *holds* the entry before it starts (`queue_runner.py:932`, `:943-944`). **They are different quantities and this document registered neither.**

> **RULED: `memory_floor_gb = 20.0`, and its basis is that it EQUALS THIS ITEM'S OWN REGISTERED CGROUP CAP — a container permitted 20 GiB must not be admitted to a host with less than 20 GiB available.**
>
> **THIS IS A DERIVATION FROM THE CAP, NOT A MEASUREMENT OF PEAK RSS.** No artefact on this box records what this arm **needs**; the cap records only what it **may take**. The figure is therefore *sufficient by construction and of unknown necessity*, and it is registered saying so rather than as a measured requirement.

**UNIT, ruled and recorded so it is never re-litigated:** `scripts/queue_runner.py:195-200` computes `MemAvailable` as `int(kB) / (1024*1024)` — **GiB** — despite the `_gb` field name **and** its own log line printing "GB". **A registered GiB floor goes in UNCONVERTED.** Converting would over-ask by ~7.4 %, which is itself a change to a registered figure.

### 2. ⚠ STRUCK — LINE 1 AND §10 STILL DENY THIS DOCUMENT'S OWN FREEZE

Line 1 reads **`⚠ DRAFT — NOT A REGISTRATION, NOT FROZEN, NOT ENQUEUED`** and §10 still lists the freeze among items *"Owed before any freeze"*. **This document was FROZEN at `c1f309e8`**, `PERMISSION=648a6ea1` filled at `d6rf4_run_arm.sh:97` (assignment count measured = 1). **Both are STRUCK by this section and neither is edited** — the originals stand as the record of what the document was.

**AND THIS IS THE PROSE CATEGORY SURVIVING MY OWN PRE-EMPTIVE SWEEP.** I commissioned that sweep precisely to stop the W3S pattern, and it found and fixed four prose claims **in the instruments** — and **not this one, in the registration itself.** **The sweep's scope was the instruments; the document was not in it, and that omission is mine.** The lesson generalises past this item: **a freeze-fragility sweep that covers the code and not the registration has swept the smaller half**, because the registration is what a reader opens first.

### 3. THE IMAGE IDENTITY IS REGISTERED HERE, having been carried only structurally

`dafoam-idwarp-rot:v1` is **not named anywhere in this document**. It is forced by the frozen launcher (`:529-536`, `G-ROW` PATCHED-ONLY, digest-checked at `:325-326`/`:534`, every other value aborting `rc 4`) — **structurally binding but never registered**, which `DAFOAM_CHARTER.md` §6 asks for directly. **Registered now: image `dafoam-idwarp-rot:v1`, and the DIGEST is the identity, not the tag** (§11: *the hash is the identity; the version string is not*). The launcher's digest check is the operative gate and this section records what it pins rather than replacing it.

### 4. TWO CORRECTIONS AGAINST MY OWN FIGURES, both measured by a lane against my recollection

* **The D6RF3 grader derivation diff is 1292 lines, not 1,293.** I quoted 1,293 repeatedly tonight, including in a commit message and to the chief. `wc -l` and `grep -c ''` agree at **1292**. D6RF4's own grader diff is a different and larger artefact — **1765 lines, 1744 rename-stripped**.
* **"Ceiling 54.0" conflated two quantities.** `54.0` is the **grader's** `ceiling_core_min = sum(CAPS)` (`:696`, `:2792`), equal to the cap **only because one arm is registered**. The **launcher's** `CEILING = 3.0 × CAP = 162.0` (`:1267`) is a different thing with a different consequence: **the cap only REPORTS and lets the run continue (`:1275-1278`); the ceiling DOCKER-STOPS it (`:1279-1284`).** Two numbers, two behaviours, one word — and I used the word without the distinction.

**SUBMISSIONS PARKED.**
