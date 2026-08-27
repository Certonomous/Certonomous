# VMFLGPU003 — PRE-REGISTRATION (frozen before any compute)

**Case:** VMFLGPU003 — *Laminar Flow in a Triangular Cavity* — Ansys Fluid Dynamics
Verification Manual, Release 2026 R1, **p. 229** (domain and material table p. 230,
results figure p. 231).
**CPU parent:** `VMFL011` (manual p. 41 — the same cavity, the same reference, the same
digitised benchmark curve).
**Object under verification:** **the lab's GPU solver path** (OpenFOAM v2606 +
petsc4Foam + PETSc-CUDA on the NVIDIA L4, `sm_89`).
**Drafted by** `ansys-lane-opus` (lane G) **on the supervisor's brief** `[lab-attributed]`.

**This document is frozen by commit sha before the solver starts. That freeze is its
entire evidentiary content: it proves the gate could not have been chosen to fit the
answer** (CLAUDE.md rule 2; `VERIFICATION_CHARTER.md` §2b, §2d).

**PRE-COMPUTE CONDITION, STATED AND CHECKED.** At the moment of writing,
`verification/runs/ansys_verification/VMFLGPU003/` **does not exist** — checked with
`ls -d`, which returned *"No such file or directory"* at **2026-08-27T16:57:22Z**. No
core-minute and no GPU-second has been spent on this case. Everything measured below
was measured on **other cases' completed artifacts** or on **guard fixtures in a
scratch directory**, and every such measurement is labelled where it appears.

**SUBMISSIONS PARKED.** Nothing here leaves this box (rules 7, 8).

---

## 1. Title-page verification of the source (CLAUDE.md rule 15, L-144)

**Never by filename, file type or hash.** The PDF beside the sidecar was opened and its
title page read:

```
Ansys Fluid Dynamics Verification Manual
ANSYS, Inc.  Southpointe  2600 Ansys Drive  Canonsburg, PA 15317
Release 2026 R1
March 2026
```

PDF metadata: `Title: Fluid Dynamics Verification Manual`, `Creator: DocBook XSL
Stylesheets V1.76.1`, `Producer: XEP 4.22 build 2013`, **290 pages** — matching the
fingerprint `ANSYS_VERIFICATION_CHARTER.md` §4.2 records. The `.txt` sidecar's opening
lines carry **the same title-page text**, and its running footer for this case reads
`Release 2026 R1 - © ANSYS, Inc. … 229` with `VMFLGPU003` as the page header — so the
sidecar page this document is built from **is** manual p. 229, checked and not assumed.

## 2. What the manual says, read from the sidecar page for THIS case

| item | value, manual pp. 229–231 |
|---|---|
| reference | R. Jyotsna, S.P. Vanka, *"Multigrid Calculation of Steady, Viscous Flow in a Triangular Cavity"*, **J. Comp. Phys., Vol 122, pp. 107–117, 1995** |
| solver (Ansys) | Ansys Fluent GPU |
| physics | *"Viscous flow, driven by a moving wall"*; steady; pressure-based solver |
| fluid | **ρ = 1 kg/m³**, **μ = 0.01 kg/m·s** ⇒ ν = 0.01 m²/s |
| geometry | **height of the triangular cavity = 4 m**, **width of the base = 2 m** |
| boundary conditions | **velocity of the top (base) wall = 2 m/s**; *"Other walls are stationary"* |
| mesh (Ansys) | *"A hybrid mesh with tetrahedral and hexahedral cells is used"* |
| quantity | Figure .gpu003.2, *"Comparison of Distribution of Normalized X-Velocity Along a Vertical Line that Bisects the Base of the Cavity"*; *"X-velocity is normalized by the velocity of the moving wall"* |
| **results table** | **THERE IS NONE. The manual prints a FIGURE and no discrete target.** |

Reynolds number, derived from the manual's own numbers: `Re = U_wall · base / ν =
2 · 2 / 0.01 = 400`. Laminar, and the manual says so.

**The Ansys Fluent GPU curve on p. 231 is CONTEXT ONLY** (`ANSYS_VERIFICATION_CHARTER`
§5.1): this lab has no Fluent, has opened no VM2026R1 archive for this case, and gates
against nothing that came out of one. It is a figure and carries no number this document
could gate on even if it wanted to.

## 3. The reference, what kind of thing it is, and the CEILING

**The manual gives no number.** The gate is therefore built on the **digitised benchmark
curve** the CPU parent already carries, and its provenance is stated in full because a
reference without provenance is not a reference:

- File: `cases/ansys_verification/VMFLGPU003/reference/vmfl011_benchmark_xnorm.csv`,
  git blob **`9f11191b8c823eb32edd3f2b74bd29da855aab55`** — **byte-identical to the blob
  committed with `VMFL011-R3`**, verified by `git hash-object` against
  `git rev-parse HEAD:cases/ansys_verification/VMFL011-R3/reference/vmfl011_benchmark_xnorm.csv`.
  Copied, not re-derived, and nothing re-fitted or smoothed.
- The curve is **Ansys's own digitisation** of the cited reference, carried in the
  parent case's project archive as a two-column file titled *"Benchmark x-norm"*
  (`VMFL011_WB.wbpz → VMFL011_WB_0_files/dp0/FLU/Fluent/VMFL011_xvel.xy`).
- 46 rows, columns `y_m , u_x/U_wall`, `y = 0` the moving base, `y = −4` the apex.
  Measured span: first abscissa `−4.00`, last `−0.0181012`; minimum value
  **`−0.318062`**, maximum `0.995744`.

| | |
|---|---|
| reference kind | **code-to-code / numerical benchmark** (another code's solution) |
| what it buys | **NEITHER validation NOR prediction** (`PREREG_TEMPLATE` Amendment 1) |
| **CEILING** | **`GATE REACHED`** — **this case CANNOT earn `PASS`, however well it agrees** |

**Registered here, before any number exists, so it cannot be revisited when one does.**
The comparator hard-codes `TIER_CEILING = "GATE REACHED"` and emits it as the in-band
verdict; `--selftest` executes the claim (`rec_band_is_the_parents()`), so the ceiling
is a property of the instrument and not a sentence in this document.

**Honest note on the digitisation's own noise floor, registered in advance.** In the
quiescent lower half of the cavity the benchmark reports values between `−2.7e-04` and
`+1.1e-02`, changing sign, where the physical velocity is essentially zero. An
error-versus-reference norm therefore **cannot converge to zero** on this reference. That
is why the Roache triple runs on a **solution functional** and not on the error norm —
see §6.4.

## 4. The three-limb gate

Per the family's common gate (`DRAFT_PREREGISTRATIONS_VMFLGPU.md`, "THE GPU-SOLVER-PATH
GATE", Sanaa's ruling 2026-08-25), and **a miss on limb A is `NOT A RESULT` whatever the
physics says**.

### 4.1 LIMB A — GPU EXECUTION (binary, physics-critical)

**THIS LIMB IS NOT INHERITED FROM VMFLGPU001/002. IT IS REBUILT.** The supervisor ruled
on 2026-08-27 that those cases' frozen tells were **broken before compute, provably from
the frozen file alone**: their tell 1 fired on *any* CUDA-configured build — including
the forced-CPU control — so `limb_A` refused at clause A2 by construction; and their
tell 3 looked for a `type: aijcusparse` line **this build never prints** (it echoes
`-eqn_p_mat_type` in the options block only), so it false-negatived a genuine GPU run.
Neither is carried forward.

The replacement is **PETSc's own `-log_view` per-event accounting**, and it was
**MEASURED on the real VMFLGPU002 artifacts on the GPU instance itself**
(`.../VMFLGPU002/{gpu,cpu}/L1_N20/log.simpleFoam`, read 2026-08-27):

| event | arm | Total Mflop/s | GPU Mflop/s | CpuToGpu count | **GPU %F** |
|---|---|---|---|---|---|
| `MatMult` | gpu | 1184 | 2834 | 6000 | **100** |
| `MatMult` | cpu | 2460 | 0 | 0 | **0** |
| `KSPSolve` | gpu | 424 | 680 | 3601 | **100** |
| `KSPSolve` | cpu | 2056 | 0 | 0 | **0** |

The three tells, as frozen:

| tell | what it reads | frozen threshold |
|---|---|---|
| 1 | max **GPU %F** over `MatMult` and `KSPSolve` rows of the GPU arm | `≥ GPU_PCTF_MIN = 99.0` (a floor below the measured 100, above the measured 0) |
| 2 | the solver PID holding **non-zero device memory** during the solve, from `gpusample.txt` | unchanged from 001/002 — this tell was sound |
| 3 | total **host-to-device transfer count** over those events on the GPU arm | `> 0` (measured 9601 on 002 L1) |

**The forced-CPU control is the discriminator**, and it now discriminates: the control
arm must report `GPU %F ≤ 0.0` **and** zero transfers. If it reports any GPU work the
comparator **refuses at A2** — because then the tells cannot tell GPU from CPU on this
build and the row certifies nothing.

**An ABSENT `-log_view` table is ABSENT, never a zero.** `gpu_accounting()` returns
`(None, None)` when neither event has a row, and the comparator refuses at A3/A4 rather
than reading silence as a negative.

**The `-eqn_p_mat_type` options echo is INFRASTRUCTURE** (L-342): it records what was
**requested**, never what ran, and it never refuses.

### 4.2 LIMB B — GPU ≡ CPU (the heart of the verification)

`|q_GPU − q_CPU| / |q_CPU| ≤ TOL_B = 1e-4`, on **BOTH gate channels**, at **EVERY
level** — six ratios, and the worst one decides.

**Derivation of 1e-4, and it is not a round number chosen for looking tight.** The two
arms are byte-identical in mesh, schemes, relaxation, outer loop, outer iteration count
and linear-solver tolerances; the ONLY difference is `mat_type`/`vec_type`, i.e. where
the same linear system is solved. The registered linear-solver relative tolerances are
`p: relTol 0.01`, `U: relTol 0.1` with `tolerance 1e-12` — the parent's own values. Two
solves of the same system to the same relative tolerance may differ by at most that
tolerance in the *linear residual*, but the SIMPLE outer loop is a contraction driven to
a fixed point, and at the fixed point both arms satisfy the same discrete equations to
the same residual floor (`RESID_FLOOR = 1e-7`, §6.3). The gate channels are functionals
of the converged field, so their arm-to-arm difference is bounded by the residual floor
divided by the problem's sensitivity, which is `O(1)` here. `1e-4` is **three orders
looser than the residual floor** — deliberately, because limb B must fail on a *broken
GPU path*, not on floating-point associativity in a different summation order.

### 4.3 LIMB C — PHYSICS (the reference gate)

`rms_vs_benchmark` at the **finest GPU level** `≤ BAND_RMS = 0.030`.

**`BAND_RMS = 0.030` IS THE PARENT'S CONSTANT, CARRIED CHARACTER FOR CHARACTER.** It is
`BAND_RMS = 0.030` in `VMFL011-R3`'s frozen comparator, which carries it from
`VMFL011-R2`, which carries it from the original `VMFL011` freeze. **It has never been
met and it has never been moved.** Choosing a band here would be gate-fitting; inheriting
one is the only way this case's band can be **older than this case**. A mutation that
widens it to 0.900 is caught by `--selftest` (driven; see §12).

`rms_vs_benchmark` is the RMS, over the benchmark's own 46 abscissae, of
`(lab profile interpolated there) − (benchmark there)`, with the lab profile normalised
by `U_WALL = 2.0`. It is an **absolute band on an error norm**, not a relative ratio —
the benchmark passes through zero, so a relative form would have no denominator.

## 5. The quantities, named before the run

| channel | definition | role |
|---|---|---|
| `rms_vs_benchmark` | RMS over the 46 benchmark abscissae of the profile difference | **limb C** (the physics gate) and a limb-B channel |
| `u_min_norm` | `min(u_x)/U_wall` over the 401 bisector samples — the most negative normalised X-velocity | the **Roache triple** channel, a limb-B channel, and the **plateau** channel |

Both are read from **one artifact by one reader**, registered in advance: the `bisector`
`sets` function object in `case/system/controlDict.template`, 401 uniform points from
`(0, −4, 0.05)` to `(0, 0, 0.05)`, `interpolationScheme cellPoint`, at **fixed physical
locations** so the sample set is identical at all three levels.

**What differs from the parent, deliberately:** that object writes **one profile per
SIMPLE iteration** (`writeControl timeStep`, `writeInterval 1`). The SAME artifact
therefore carries the gate value (the directory named exactly `endTime`) and the plateau
history (§6.3). A plateau measured in something other than the gate quantity is not a
plateau in the gate quantity, and this comparator does not accept a proxy for it.

**The gate is read AT `endTime`, never at "the last directory".** `_bisector_dirs()`
sorts **numerically** — `'999'` sorts after `'3500'` as a string, and the gate value
would then be read from the wrong iteration and would still print to twelve figures.

## 6. The ladder, the durations, and the convergence clauses

### 6.1 The grid triple

| level | NB × NH | cells | `endTime` |
|---|---|---|---|
| `L1_20x40` | 20 × 40 | **800** | 1000 |
| `L2_40x80` | 40 × 80 | **3200** | 1500 |
| `L3_80x160` | 80 × 160 | **12800** | 3500 |

`r = 2` exactly (NB and NH double together; cells ×4). This is the CPU parent's own mesh
family, unchanged. **NB is EVEN at every level**, so the bisector `x = 0` is a cell-FACE
plane at all three levels and the sample line is identically placed under refinement.
The mesh is **one degenerate hex collapsed onto the cavity apex** — the idiom blockMesh
recognises, which emits prism cells with the apex faces properly collapsed; declaring two
separate coincident vertices instead leaves zero-area faces and killed simpleFoam with
SIGFPE when the parent measured it.

**MEASURED, pre-freeze, in a scratch directory (not a run root):** `blockMesh` and
`checkMesh` were run at all three levels on the lab box. `Mesh OK` at all three;
**800 / 3200 / 12800 cells**, exactly the registered counts. The launcher re-checks this
at launch and aborts on any mismatch.

### 6.2 `endTime`, and why these numbers are not guesses

**Basis: the parent's own completed run.** In `VMFL011-R2`'s `log.simpleFoam` — the same
cavity, the same outer numerics, character for character — the initial residuals of
`Ux`, `Uy` **and** `p` all fall below `1e-7` **and stay below it** from iteration:

| level | parent converged at | registered `endTime` | margin |
|---|---|---|---|
| L1 | **259** | 1000 | **3.9×** |
| L2 | **488** | 1500 | **3.1×** |
| L3 | **1455** | 3500 | **2.4×** |

Those iteration numbers are recorded in the comparator as
`PARENT_CONVERGED_AT = {800: 259, 3200: 488, 12800: 1455}` (by level name), and
`--selftest` checks that every registered `endTime` is at least **2×** its parent
convergence point — so the margin is a number in the instrument, not a claim in this
paragraph.

**An `endTime` is a DURATION, not a gate.** It cannot move a band, a threshold or a
label, and it is registered here because CLAUDE.md rule 12 requires the cost to be
registered and the cost is `cells × endTime`. **The risk is registered too:** the GPU arm
runs the linear solves through PETSc CG/BiCGStab with **Jacobi** preconditioning rather
than the parent's DIC/DILU. The SIMPLE *outer* convergence rate is set by relaxation and
by the linear solves reaching their `relTol`, not by which preconditioner reaches it — so
the outer iteration count should be unchanged. **If it is not, and a level fails to reach
`RESID_FLOOR` by its `endTime`, the comparator REFUSES (clause I3) and the GPU-hours are
lost.** The 2.4×–3.9× margin is the protection against that. It is not extended after the
fact: an overrun stops the run and does not get a new budget.

**There is NO `residualControl`.** The run always reaches `endTime`, so rule 4's
"last time == `endTime`" clause and the `Time =` line-count clause both bite, and **both
arms take the same number of outer iterations** — which is what makes limb B a statement
about the linear algebra and about nothing else.

### 6.3 Iterative convergence — residuals AND a plateau with a LIVENESS FLOOR

1. **Residuals.** The final initial residual of `Ux`, `Uy` and `p` must each be below
   `RESID_FLOOR = 1e-7` (the parent's frozen value). Read from `log.simpleFoam` by a
   regex **verified against real petsc4Foam output** (VMFLGPU002's own log prints
   `PETSc-cg:  Solving for p, Initial residual = …`), and independently written to disk
   by the `solverInfo` function object.
2. **Plateau, on the gate quantity's own history.** `u_min_norm` per iteration; a
   **FIXED** window of `PLATEAU_WINDOW = 400` samples (never a fraction); fewer than
   `PLATEAU_MIN = 400` available samples refuses as CANNOT_TELL, never a pass;
   peak-to-peak over the window must be below `PLATEAU_TOL = 1e-6` m/s.
3. **THE NULL-RANGE RULE, and it is new here.** A window peak-to-peak of *exactly* zero
   is ambiguous: a dead channel and a perfectly converged one look identical to a
   tolerance. **This is not hypothetical — it is why VMFLGPU001 has no verdict**: its L1
   probe rose to `4.639246e-03` and then went bit-identical for its final 1662
   iterations, a perfectly converged double-precision fixed point, and the null-range
   guard refused it. Conflating the two cases is what cost that run.

   So this comparator **separates** them, with evidence from the same run: a null window
   range is accepted **only** when the channel is shown to have been ALIVE earlier —
   full-history peak-to-peak strictly greater than **`PLATEAU_ALIVE_MIN = 1e-3` m/s**. A
   channel that never moved at all is still refused. **This is strictly MORE
   discriminating than a bare null-range refusal, not a relaxation**: it adds a
   requirement (aliveness) to the case a bare refusal simply rejected, and it removes no
   requirement from any other case. Both branches are driven under `python3 -O` (§12).

### 6.4 The Roache triple

On **`u_min_norm`**, on the **GPU arm**, `r = 2`, `Fs = 1.25`, `P_MIN = 0.05`,
**ratio-first** classification (`|R − 1| ≤ 1e-3` is `STAGNANT` *before* any observed
order is computed, so a floating-point crumb cannot become a valid-looking near-zero
order). A triple that is not `CONVERGING` is **`NOT A RESULT`**, whatever the value, and
**no GCI is printed** off it.

**Why `u_min_norm` and not the error norm:** the benchmark is a plot digitisation with
its own noise floor (§3), so `rms_vs_benchmark` cannot converge to zero under refinement
and would grade `STAGNANT` for a reason that has nothing to do with this lab's
discretisation. `u_min_norm` is a **solution functional** and refines properly. This is
the parent's registered reasoning, carried.

**Expected order:** `p_f = 2` (Gauss linear, corrected). An observed `p > 2.3` is
`SUSPICIOUS` and is reported as such, never quietly accepted.

### 6.5 THE PREDICTION, made before the run

**Predicted outcome: `GATE FAIL` on limb C, or `NOT A RESULT` on the triple.** The
parent has never met `BAND_RMS = 0.030` and has never once been given a verdict on it —
rows #26 and #31 are both `NOT A RESULT` from comparator refusals, not from physics.
Limbs A and B are expected to hold. **This is written down so that a `GATE FAIL` here
reads as the gate working rather than as a disappointment**, and so that a `GATE REACHED`
— if it comes — is a result nobody could have arranged.

## 7. Controls (CLAUDE.md rule 3), all of them, and where each plant goes

**THREE plants, three different readers, three different placements.** Every one runs and
is **REPORTED BEFORE ANY EXIT** (L-347 clause 2) — a control standing behind another
control's refusal is an untested control, and that is exactly how the parent's `u_min`
plant survived two freezes without ever executing on real bisector bytes.

| control | reader | plant | placement | threshold |
|---|---|---|---|---|
| `u_min_norm` | `min()` over 401 samples — a **point** reader | `UMIN_PLANT = −0.1234` (`−abs(1.234e-3)·100`, the parent's magnitude **exactly**) | **the ARGMIN row** — the row a `min()` reader selects (**L-347**) | `δ > 0.1·\|plant\|` |
| `rms_vs_benchmark` | RMS over 46 abscissae — an **averaging** reader | `K·U_WALL·max(\|base\|, 1e-6)`, `K = 4` (**L-340** sizing) | **all data rows** | `δ > 0.1·\|plant\|` |
| **plateau** (new) | peak-to-peak over a 400-sample window | `\|UMIN_PLANT\|` | **the iteration carrying the window MAXIMUM** — the row a peak-to-peak reader selects | `δ > 0.1·\|plant\|` |

**The threshold rule `δ > 0.1·|plant|` is carried CHARACTER FOR CHARACTER from the
parent. The repairs are all LOCATION and SIZING, never a loosened test.**

**Why the plateau needs its own plant, registered rather than argued later:** the plateau
clause can vote a graded row `NOT A RESULT`. A clause that can do that must be shown able
to see a non-zero, exactly as a gate reader must.

**The run tree is NEVER modified.** Every plant goes into a temporary copy; the plateau
plant is substituted for one iteration through an override map, so nothing is written
into `postProcessing/` at all.

**Negative arm.** Both gate readers are re-run on an **unplanted** copy and must report
**exactly zero** movement. A reader that moves where nothing was planted is as useless as
one that misses a real plant.

**L-347 driven on the run's own bytes, not on a fixture.** `umin_placement_control()`
shows, on **this run's** finest GPU profile, that the parent's row-0 placement moves the
`min()` reader by ≤ the threshold (it would REFUSE) while the argmin placement moves it
by **exactly `|plant|`**. If the argmin happens to *be* row 0 the discriminator is
degenerate and the control **says so** rather than reporting a pass it did not earn.

**MEASURED, pre-freeze, on real OpenFOAM output** (5-iteration smoke, lab box, scratch
directory, wall < 1 s): the bisector's **row 0 is exactly `0.0`** — the collapsed apex,
where no-slip gives `u ≡ 0` — and the **argmin is row 340**. So the L-347 discriminator
is live on real bytes of this exact case, and the geometry that defeated the parent's
plant is present here too.

## 8. Strict completion (CLAUDE.md rule 4), with FIELD CLASSES (L-342)

**PHYSICS-CRITICAL** — a failure refuses or votes `NOT A RESULT`:

1. solver `rc = 0`, from `RUN_RC.<level>.<arm>` (run root) or `RUN_RC.txt` (level).
   **An ABSENT rc is `NOT MEASURED`**: the verdict becomes `NOT A RESULT`, the physics is
   still read and printed, and it is **not** a voiding refusal. A **present, non-zero** rc
   refuses — a non-zero rc is a finding, not a retry.
2. an `End` line in `log.simpleFoam`.
3. last time directory == the level's registered `endTime`.
4. `U` and `p` present at `endTime` (`X` or `X.gz`).
5. **the `Time =` line count == `endTime`.**
6. the **age guard**: every field at `endTime` strictly newer than the case's own `0/U`,
   which the launcher touches **last** before launch.

Plus the **mesh birth certificate** (`Mesh OK` and the registered cell count) and the
**launch-time sha freeze** (`LAUNCH_RECORD.txt` must show the prereg and comparator blobs
on disk equal to the blobs at HEAD).

**R-RC (Sanaa's desk ruling, 2026-08-27T16:54Z), implemented as a PURE, UNIT-DRIVEN
RULE.** Her words, verbatim: *"rc value is physics, rc record is infrastructure; absent
record -> NOT MEASURED only when the other four rule-4 conditions hold."* The comparator
carries `rrc_classify(rc_record_present, other_four)`, and **`--selftest` drives all
sixteen combinations of the four conditions**: an absent record is `NOT MEASURED` **only**
when `end_line ∧ last_time_is_endtime ∧ fields_present ∧ age_guard`, and `REFUSE`
otherwise; a present record is always `MEASURED`. Without that conjunction *"the rc record
is missing"* would be a blanket pass, and it is not. A mutation replacing the conjunction
with a constant is caught by `--selftest` (§12.3). The classification is **deferred to the
foot of the completion check** rather than made at the top, because a classification made
before its own premises have been read is not a classification.

**INFRASTRUCTURE — recorded, never refused on, never voids a verdict:**

- **THE `ExecutionTime` LINE COUNT.** **MEASURED on this instance on VMFLGPU002's own
  completed L1 log: 1200 `Time =` lines and 1202 `ExecutionTime` lines at
  `endTime = 1200`** — petsc4Foam prints `endTime + 2` timing lines. **VMFLGPU001 was
  frozen with this count as a physics-critical clause, its six arms all finished `rc 0`,
  and it has NO VERDICT because of it** (post-compute amendment 4, commit `59110074`).
  It is INFRASTRUCTURE here **from the first line of the comparator**, and a mutation that
  restores the refusing behaviour is caught by `--selftest`.
- `COST.txt` and every GPU-hour / core-minute figure; `LAUNCH_RECORD.txt`'s non-sha
  bookkeeping lines; `CAP_EXCEEDED.txt`; pids, sids, memory figures, bookkeeping mtimes;
  the `-eqn_p_mat_type` options echo.

*Provenance:* Sanaa's universal rule of 2026-08-26, verbatim — *"a bookkeeping failure
invalidates the bookkeeping, never the physics artifacts — and graders must separate
physics-critical fields from infrastructure fields so a dead poller can never void a run
again."*

## 9. Risks, named before the run rather than explained after it

1. **The linear-solver change could slow outer convergence.** Jacobi preconditioning
   instead of DIC/DILU. Mitigated by the 2.4×–3.9× `endTime` margin (§6.2); if it is not
   enough the comparator refuses at I3 and the GPU-hours are a loss, reported as such.
2. **`use_gpu_aware_mpi 0` is required or every GPU solve aborts at rc 76.** Measured on
   this instance during VMFLGPU002's build. This case runs at **one rank**, so the
   device-to-device MPI path the option governs is never exercised: it declines a
   *performance* feature, not a correctness one, and it cannot move a number. It is
   passed to **both** arms so the two differ only in `mat_type`/`vec_type`.
3. **The triple may not be `CONVERGING`.** The parent's own triple has never been graded.
   If it is `OSCILLATORY` or `STAGNANT` the row is `NOT A RESULT` — the rule working, and
   registered here as a likely outcome (§6.5).
4. **The benchmark is a digitisation, not a table.** Its noise floor is quantified in §3
   and is the reason the triple channel is a solution functional. Limb C is graded against
   it anyway, honestly, at a band inherited from the parent.
5. **Per-iteration profile writing creates ~`endTime` directories per arm-level**
   (~12,000 small directories over six arms). Disk measured at 62 GB free on the
   instance. If the filesystem refuses a write the solver's rc carries it and clause 1
   bites.

## 9a. If it does not converge — the rung, named BEFORE the run (Sanaa's §3)

**One change per run; every fallback is a pre-registered diagnostic arm with its own cap;
and this document names the rung in advance so no ladder step can be chosen to suit an
answer.**

**L0 DIAGNOSE FIRST, and the diagnosis is already instrumented.** The comparator
separates the three failure shapes rather than reporting "did not converge": residual
level per field (`Ux`, `Uy`, `p` independently); **plateau peak-to-peak over a fixed
window versus full-history range**, which distinguishes *oscillation* from *plateau* from
a *dead channel*; and the **location** of the gate functional (`_argmin_row` reports which
of the 401 bisector samples carries `u_min`, so "where in the domain" is a number, not an
impression).

If a level misses `RESID_FLOOR` at its `endTime`, the registered order of arms is:

| rung | arm, if needed | why it is the right rung here |
|---|---|---|
| **L1** numerics dials | relaxation `U`/`p` from 0.7 downward; no channel's tolerance tightened relative to its siblings | the parent converged at 0.7/0.7 in 259/488/1455 iterations, so a miss here means the *linear* solves are not closing the outer loop, which is a dial |
| **L2** linear solver | `pc_type jacobi` → `bjacobi`/`asm`/`gamg` on the GPU arm, **and the identical change on the CPU arm** | this is the FIRST rung the GPU path itself can be responsible for, and the two arms must stay byte-identical or limb B stops meaning anything |
| **L5** initialisation | `potentialFoam` start | a lid-driven cavity from a zero field is the standard case for it |

**L3 (discretization), L6 (model swap) and L7 (formulation) are NOT available to this
case as fallbacks.** They are answer-changing, and under Sanaa's absolute anti-gaming
clause an answer-changing choice is **never** selected by agreement with the reference. If
the case converges and misses the band, that is **`GATE FAIL` with a diagnosis, not a
parameter hunt**. If it does not converge at all after L1/L2/L5, the honest outcome is
`NOT A RESULT` with the diagnosis printed — **not** a scheme change until the number
improves.

**The schemes and the model were chosen on PHYSICS GROUNDS, before any number existed,
and the justification is written here so nobody can later ask whether the reference picked
them:**

- **Laminar, no turbulence model.** `Re = U_wall · base / ν = 2 · 2 / 0.01 = 400`, from
  the manual's own material and geometry numbers. 400 is laminar for a driven cavity by a
  wide margin, and the manual itself says *"Viscous flow, driven by a moving wall"* with a
  pressure-based steady solver and no turbulence model.
- **`bounded Gauss linear` for `div(phi,U)`** — second-order central, the correct choice
  for a steady laminar recirculating flow at this Reynolds number, where an upwind blend
  would add numerical diffusion that is indistinguishable from physics in exactly the
  quantity being graded. The `bounded` form subtracts the `div(phi)U` term for the steady
  solver; it is not a limiter and does not blend.
- **`Gauss linear corrected` laplacian and `corrected` snGrad**, with **three
  non-orthogonal correctors** — the mesh is a collapsed-prism mesh with real
  non-orthogonality at the apex, and the corrector count is the parent's, under which its
  measured convergence record was obtained.
- **`consistent yes` (SIMPLEC)** — the parent's, and the reason relaxation can stay at
  0.7/0.7 rather than the 0.3/0.7 a plain SIMPLE would need.

**Every one of these is the CPU parent's, carried character for character. Not one was
chosen after seeing a number, and the only thing this case changes is the linear solver —
which is the object under verification.**

## 10. Solver, model, mesh, and the two arms

- `simpleFoam` (OpenFOAM v2606) + `petsc4Foam` (`libs (petscFoam)`), steady laminar,
  incompressible, `ν = 0.01 m²/s`.
- Outer numerics **are the parent's, character for character**: `consistent yes`,
  `nNonOrthogonalCorrectors 3`, `pRefCell 0`/`pRefValue 0`, relaxation `U 0.7` / `p 0.7`,
  `bounded Gauss linear` divergence, `Gauss linear corrected` laplacian. Three
  correctors are not a free parameter: the mesh is a collapsed-prism mesh with real
  non-orthogonality, and the parent's measured convergence record was obtained under
  them.
- **Only the linear solvers change**, and the linear solver **is** the object under
  verification: `p` → petsc `ksp_type cg` + `pc_type jacobi`; `U` → petsc
  `ksp_type bcgs` + `pc_type jacobi`; tolerances `1e-12`, `relTol` `p 0.01` / `U 0.1`,
  the parent's own values.

| arm | `mat_type` | `vec_type` | role |
|---|---|---|---|
| `gpu` | `aijcusparse` | `cuda` | the object under verification |
| `cpu` | `aij` | `standard` | limb A's discriminator **and** limb B's baseline — one run serving both, so it *is* the forced-CPU control by construction |

Both arms are otherwise **byte-identical**: same mesh, same schemes, same relaxation,
same outer loop, same outer iteration count, same tolerances, same `-log_view`.

## 11. COST — registered before the run (CLAUDE.md rule 12)

**Basis: the two MEASURED points this family already has**, both from six-arm runs on
this same instance:

| case | cells (L1/L2/L3) | `endTime` (L1/L2/L3) | measured |
|---|---|---|---|
| VMFLGPU001 | 1024 / 4096 / 16384 | 3000 / 3000 / 3000 | **0.4417 GPU-h** |
| VMFLGPU002 | 3600 / 14400 / 57600 | 1200 / 1600 / 2200 | **0.89694 GPU-h** (against a 1.0 cap — within 10.3 % of firing) |

From VMFLGPU002's per-level split (L3 GPU arm 967 s over 2200 iterations at 57600 cells;
GPU-arm total 1395 s; CPU-arm total 1834 s = 30.567 core-min) a two-term per-outer-
iteration model solves to **`t ≈ 0.0945 + 5.99e-6 · cells` seconds** on the GPU arm, with
the forced-CPU arm at **1.31×** the GPU arm. VMFLGPU003 runs **4** p-solves per outer
iteration against VMFLGPU002's 3 (three non-orthogonal correctors against two), so the
per-iteration term is scaled by **1.25**:

| level | cells | iterations | GPU arm | CPU arm |
|---|---|---|---|---|
| L1 | 800 | 1000 | 124 s | 163 s |
| L2 | 3200 | 1500 | 213 s | 279 s |
| L3 | 12800 | 3500 | 749 s | 981 s |
| **total** | | **12,000 outer iterations ×2 arms** | **1086 s** | **1423 s** |

- **ESTIMATE: 0.70 GPU-h** (2509 s), of which the CPU arm is **23.7 core-min**.
- **RUNAWAY CAP: `CAP_GPU_H = 1.5`** — **2.1× the estimate**. A cap is a runaway guard,
  not a target; VMFLGPU002's 1.0 cap came within 10.3 % of firing on a healthy run and a
  cap that kills a healthy run manufactures a loss. Secondary cap
  `CAP_CPU_ARM_CORE_MIN = 90` (3.8× the CPU-arm estimate).
- **`cost_basis`: GPU-hours at the AWS PUBLISHED PRICE LIST `$0.8048/GPU-h` for
  `g6.xlarge` `us-east-2` (retrieved 2026-08-23, `GPU_CAPABILITY_STATE.md` §9). Dollars
  are DERIVED, NOT MEASURED — this box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5), and it is NOT a console figure. THE CONSOLE FIGURE IS
  STILL OWED AND SUPERSEDES.** Derived: estimate **$0.56**, cap **$1.21**.
- The CPU arm runs on the same billed instance, so its core-minutes are **work, not a
  separate charge**.
- **The cap is enforced IN THE EXECUTABLE PATH**, by `timeout` with the rc captured
  inside the launcher, by the general formula
  `timeout_s = remaining_core_min · 60 / RANKS`, and it draws down across levels. An
  overrun **stops the run**; it does not get a new budget.

**Estimate-versus-actual calibration is OWED at completion** (rule 12): one row in
`docs/COST_CALIBRATION.md` stating the ratio actual/predicted, with contention, waste and
misprediction named separately. A completion report without it is incomplete.

## 12. The instrument, and every guard DRIVEN rather than read

**Comparator** `grade_vmflgpu003.py`, git blob **`3242084665d86baeff50fc59ab2b650e53cbb995`**.
**Launcher** `run_vmflgpu003.sh`, git blob **`df0af1afc5b8e93dcbeaf2563d92a726e8102412`**.
The launcher verifies both against HEAD at launch and aborts if either differs.

### 12.1 `--selftest`: **61 of 61, exit 0**, and again under `python3 -O`

Including: zero `Assert` nodes in its own AST (and the counter shown able to count a
planted one); the verdict vocabulary; the ceiling; the inherited band; the plant
magnitude and threshold; `r = 2`; the `endTime` margins; the benchmark's 46 rows and its
span; both readers on a benchmark-shaped fixture; the L-340 dilution **measured** (a
point-sized plant does NOT move the averaging reader; the sized one does); the L-347
placement (row-0 fails, argmin moves by exactly `|plant|`); the negative arm; all five
Roache classes; and every verdict **routing** decision driven end to end.

### 12.2 Refusals DRIVEN under `python3 -O` (each must exit 2)

`endline`, `time-lines`, `age-guard`, `control-leak`, `gpusample`, `logview-absent`,
`short-plateau`, `dead-channel`, `plant-blind`, `plateau-plant-inert`, `no-benchmark`,
`freeze`, `vocabulary`. Plus: a **FORGED GPU-arm log whose GPU %F is 0** drives the whole
six-arm grade and prints `VERDICT: NOT A RESULT`, exit 2.

### 12.3 MUTATION ARM — eleven mutations, **every one exits non-zero**

**Every guard ships its planted-failure proof (Sanaa's §1, the L-314 standard): a guard
without a demonstrated failure is not a guard.**

| mutation | `--selftest` |
|---|---|
| move the L-347 plant back to row 0 | **exit 1** |
| delete the P6 planted-zero refusal | **exit 1** |
| delete the plateau-plant refusal | **exit 1** |
| loosen the plant threshold to 0 | **exit 1** |
| widen `BAND_RMS` to 0.900 | **exit 1** |
| drop `GPU_PCTF_MIN` to 0.0 (accept a CPU run as GPU) | **exit 1** |
| read an ABSENT `-log_view` table as a zero | **exit 1** |
| delete the forced-CPU control refusal | **exit 1** |
| remove the plateau liveness floor | **exit 1** |
| restore VMFLGPU001's refusing `ExecutionTime` clause | **exit 1** |
| turn R-RC's four-condition conjunction into a blanket pass | **exit 1** |

### 12.4 Launcher guards, driven on fixtures with the guards' OWN bytes

Extracted from the file on disk by `sed`/`grep`, never retyped:

- **MOVING WALL** (§13) — **7 fixtures, 1 accept / 6 abort**: the frozen `0/U` passes;
  wall speed `1.0` aborts; `zeroGradient` aborts; `movingWall` deleted aborts;
  `sideWalls slip` aborts; `sideWalls` deleted aborts; **wall speed `2.0000001` aborts** —
  the guard is **exact, not banded**.
- **SMOKE GATE** — the regex extracted from the launcher's own **line 183**, driven on 8
  `STATUS.smoke` strings: 3 accept / 5 refuse. **It ACCEPTS the exact string that
  self-refused VMFLGPU001 three times** (`smoke_rc=0 end=… note=…`), and refuses
  `smoke_rc=1`, `smoke_rc=NOT-PROVEN`, `smoke_rc=01`, `presmoke_rc=0` and an empty file.
- **`is_time_dir`** — 9 names: `0`, `250`, `1e-05`, `0.1`, `3500` true; `0.orig`,
  `constant`, `system`, `processor0` false. A `[0-9]*` glob would have matched `0.orig`.
- **AGE GUARD** — 3 trees: empty passes; a tree holding `0` aborts; a tree holding `3500`
  aborts.
- **MESH BIRTH** — `blockMesh` + `checkMesh` at all three levels: `Mesh OK`,
  800 / 3200 / 12800 cells.
- **GATE READER PATH** — a 5-iteration `simpleFoam` smoke on the lab box wrote
  `postProcessing/bisector/{1,2,3,4,5}/bisect_U.xy`, 401 rows each; the comparator read
  them (`u_min_norm`, `rms_vs_benchmark`, `_argmin_row`, `umin_series`,
  `residual_history` all parsed), row 0 exactly `0.0`, argmin at row 340. **This is the
  single most expensive thing a freeze can get wrong — a gate artifact whose filename or
  layout the comparator cannot read — and it is checked, not assumed.**

All of §12.4 ran in a scratch directory. **No run root exists and no graded compute was
spent.**

## 13. The registered launcher control: THE MOVING WALL

The manual gives this cavity exactly one driving datum — *"Velocity of the top (base)
wall = 2 m/s"*, every other wall stationary — and the gate quantity is the X-velocity
**normalised by that velocity**, with the comparator dividing by a hard-coded
`U_WALL = 2.0`.

**If `0/U` carried a different wall speed, or drove the wrong patch, every graded number
would be normalised by a constant the field never saw — and nothing downstream would show
it.** The solve converges, the mesh is clean, the residuals fall, and **limbs A and B
both still pass, because both arms carry the same error**. Only limb C moves, so the case
would report a *physics* miss when what it actually had was a boundary condition it never
checked.

So it is checked, once per materialised case, **before the mesher runs**: `movingWall`
must be `fixedValue` `(2 0 0)` **exactly**, and `sideWalls` must be `noSlip` (or
`fixedValue (0 0 0)`). Driven on 7 fixtures (§12.4).

## 14. Hazards this launcher carries because they were paid for

- **NO `set -u`** — categorically incompatible with OpenFOAM v2606's `etc/bashrc`
  (measured rc 127). Two frozen launchers of this team shipped it and aborted before any
  compute.
- **NO `set -e`** — it does not gate at a Bash tool's top level. Every step gates
  explicitly with `|| { echo "ABORT: …"; exit 1; }`.
- **The rc is captured INSIDE the script**, from `$?` of the pipeline that ran the
  solver, never around a `setsid` line — `setsid timeout cmd` exits 0 for every outcome.
  It is written to `RUN_RC.<level>.<arm>` and `<level>/RUN_RC.txt` by **one statement**,
  so the two cannot disagree.
- **`USER`/`LOGNAME` exported BEFORE the bashrc** — the cron-started runner has no
  `USER`, `${USER:-user}` then expands to the literal string `user`, and VMFLGPU001's
  second launch aborted on a phantom `.../user-v2606/...` tree.
- **EXCLUSIVE DEVICE**: `nvidia-smi --query-compute-apps=pid` must be **empty** before
  any solve, else the launcher REFUSES (exit 2) **naming the pids**. Two GPU solves on
  one L4 corrupt both cases' evidence and neither notices: tell 2 samples a **shared**
  instrument, so a foreign solver's device memory would land in this case's
  `gpusample.txt` and could fire tell 2 for a case whose own linear algebra never touched
  the card.
- **`-log_view` on BOTH arms**, asserted at zero compute: limb A reads PETSc's accounting
  on the GPU arm **and** on the forced-CPU control, and without the table on the control
  there is nothing to discriminate against.
- **Bookkeeping never voids physics**: after a solver completes, a failed bookkeeping
  write is a WARNING and the exit code stays the solver's rc.

## 15. Verdict mapping (CLAUDE.md rule 1), in rule 5's order

| condition | verdict |
|---|---|
| limb A misses at any level | **`NOT A RESULT`** (printed with the tells) |
| a control is broken (forced-CPU arm shows GPU work; absent accounting; a plant unseen) | **refuse, exit 2** — no number is produced |
| a completion clause fails | **refuse, exit 2** |
| `rc` NOT MEASURED at any arm-level | **`NOT A RESULT`**, physics printed |
| triple not `CONVERGING` | **`NOT A RESULT`**, no GCI |
| limb B misses | **`GATE FAIL`** |
| limb C misses (`rms > 0.030` at L3) | **`GATE FAIL`** |
| all limbs hold | **`GATE REACHED`** — the ceiling. **`PASS` IS UNREACHABLE AND IS NOT IN THE ROUTING.** |

## 16. Where things live

| what | where |
|---|---|
| this document | `cases/ansys_verification/VMFLGPU003/PREREGISTRATION.md` |
| comparator | `cases/ansys_verification/VMFLGPU003/grade_vmflgpu003.py` — blob `3242084665d86baeff50fc59ab2b650e53cbb995` |
| launcher | `cases/ansys_verification/VMFLGPU003/run_vmflgpu003.sh` — blob `df0af1afc5b8e93dcbeaf2563d92a726e8102412` |
| reference | `cases/ansys_verification/VMFLGPU003/reference/vmfl011_benchmark_xnorm.csv` — blob `9f11191b8c823eb32edd3f2b74bd29da855aab55` |
| case dictionaries | `cases/ansys_verification/VMFLGPU003/case/` |
| run outputs | `verification/runs/ansys_verification/VMFLGPU003/` — **absent at this freeze** |
| record | `cases/ansys_verification/VMFLGPU003/RESULTS.md` (owed at grading) |
| register row | `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (owed) |
| calibration row | `docs/COST_CALIBRATION.md` (owed at completion) |

---

## Amendment record

| version | date | change |
|---|---|---|
| 1.0 | 2026-08-27 | Created, pre-compute. Run root `verification/runs/ansys_verification/VMFLGPU003/` checked ABSENT at 2026-08-27T16:57:22Z. Lines whose number changed above this section: n/a (first version). |
