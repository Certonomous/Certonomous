# K0b — D406 script repair. Pre-registration

**Campaign F14, rung K0b. Written 2026-08-18 BEFORE any solver was launched for
it and committed before the first solve.** Every change to be made, every
prediction, every threshold, the verdict mapping and the cost estimate were
fixed here first.

---

## 1. Why this exists, and why it is a separate task

`docs/DOCKET.md` D406 recorded that
`verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity/build_and_run.sh`
runs every leg to the source case's `endTime 4000` and contains **no
continuation step**, while the published 128x128 leg was continued by hand to
16000 iterations. `K0b_D403_RERUN_RESULTS.md` §8 measured the consequence: the
two commands the rung's README documents, in the order it documents them,
produced `Nu_avg_hot = 4.3254648850` against the published `4.5288167412` — a
deviation of **4.490 %** — and an observed order of **−1.25** against the
published **+1.94**, five of six orders negative and the sixth non-monotone.
A reader of that table would conclude the case diverges under refinement.

That lane predicted the number before its first solve and then **deliberately
did not repair it**, on the stated grounds that a re-run which edits the
instrument it grades has graded the edit. This is the separate task with the
separate pre-registration that its reasoning implies.

**What is not in question.** With the continuation applied by hand, all three
legs reproduced the published numbers exactly — 13 of 13 quantities on each —
and the freshly solved 64x64 leg came out bit-for-bit identical to the
committed archive case. The physics is not under test here. The script is.

## 2. The cost estimate — written before the run, and it is the instrument

Sanaa's standing authority of 2026-08-18 covers any run under **$25 by the
running agent's own estimate**, at a measured **$0.0513 per core-hour**
(c7a.4xlarge on-demand, us-east-2, verified against the AWS public pricing
feed). The clause makes the estimate an instrument, and this campaign carries a
VOID cost estimate on record, so it is written here rather than afterwards.

Built from this rung's own recorded measurements, not from a guess:

| Item | Basis | Estimate (core-seconds) |
| --- | --- | ---: |
| 32x32 solve | `K0b_m32/COST.txt` 3.623 s | 4 |
| 128x128 solve to t = 4000 | `K0b_m128/COST.txt` 189.550 s | 190 |
| 128x128 continuation to t = 16000 | `K0b_m128/COST.txt` 575.880 s | 576 |
| One end-to-end `analyse_k0b_mesh.py` pass over three legs | D403 re-run measured 8.705 s for five `measure()` passes plus the end-to-end analysis | 60 |
| **Sub-total** | | **830** |
| Contention contingency, 20 % | three foreign solvers were on the box when this was written; the D403 lane measured wall clock inflated 1.5 % over solver CPU under a load average of 12.83 | 166 |
| **Total** | | **996 core-seconds = 16.6 core-minutes** |

**Pre-registered estimate: 17.0 core-minutes, i.e. 17/60 x $0.0513 =
$0.0145.** That is **0.058 %** of the $25 authorisation.

**Hard stop, fixed here: 45.0 core-minutes, i.e. $0.0385.** If the run exceeds
that it is to be stopped and re-estimated, not pressed on.

No 64x64 solve is charged: `build_and_run.sh` builds only the 32x32 and 128x128
legs and `analyse_k0b_mesh.py` reads the 64x64 in place from the committed
archive. This task is therefore smaller than the D403 re-run it follows, which
cost 13.974 core-minutes with a fresh 64x64 leg and five measurement passes in
it.

## 3. What will be changed — declared here, before it is written

Two tracked files, and no others.

### 3.1 `build_and_run.sh` — the continuation becomes a step of the script

1. **An explicit second stage**, entered by a leg that did **not** stop itself
   on `residualControl`. The stopping reason is READ from the solver's own
   statement — `SIMPLE solution converged in N iterations`, which
   `buoyantBoussinesqSimpleFoam` prints when `residualControl` fires and does
   not print when it runs out at `endTime`. It is not inferred from the time
   directories, which cannot distinguish the two, nor from a residual read off
   the last iteration, which is D407's shape.

2. **The stage-2 dictionary is DERIVED by the script**, every invocation, from
   the source case's own `system/controlDict`, by rewriting exactly three keys:
   `startFrom` to `latestTime`, `endTime` to **16000**, `writeInterval` to
   **2000**. These are the three the published leg's `controlDict.4000`
   fingerprint records, and no others.

3. **The clobber is removed at its cause.** The copy step overwrites
   `system/controlDict` from the source case on every invocation. The repair
   does not stop it doing so; it removes the dependency, so that there is no
   hand edit for it to destroy. `system/controlDict.4000` is still written —
   the published leg carries it — but as an **output** of the script rather
   than as an input to it. It is preserved immediately before the rewrite and
   `cmp`-proved against the source case's own dictionary at that moment, rather
   than assumed to have survived the solve.

4. **A guard that the rewrite moved those three keys and nothing else**: the
   two dictionaries with the three key lines removed must be identical, and
   each of the three new lines must be present in the declared form. A
   continuation dictionary that had also picked up a scheme, a relaxation
   factor or a `residualControl` target would be a different case wearing the
   same leg's name.

5. **Per-PID `wait` with each status checked.** The legs run as background
   subshells and the script ended in a bare `wait`, which returns 0 however its
   jobs ended. A leg that REFUSED, or a continuation that never ran, would have
   left the script exiting 0 with a half-built rung behind it — the same class
   of silence D406 is about. This is declared here as part of the repair rather
   than slipped in.

**What will NOT change:** the mesh edit, the 11-file `cmp` guard, the archive
resolution through `lab_paths.run_archive`, the leg list `for n in 32 128`, the
`COST.txt` format including its stage-1-only `core_minutes` line (which
`analyse_k0b_mesh.cost` already corrects by summing both keys), and every
dictionary the study is defined by.

**`analyse_k0b_mesh.py` will not be edited at all.**

### 3.2 `README.md` — two stale paths, declared rather than smuggled

The rung's README names
`demo-output/website/campaign/THERMAL_K0_RESULTS.md` and
`demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5` in prose. R20
and R21 moved both and neither directory exists. These are D403's defect in the
instruction document rather than in the code, and they are corrected here and
named here so that the change stays characterisable. The README's account of
the continuation is also rewritten from a historical note about a hand edit
into a description of a step the script performs.

**No published result document is edited.** `k0b_mesh_sensitivity.json` and
`K0b_D403_RERUN_RESULTS.md` are records of runs that happened and are not
touched.

## 4. Where this will be run, and the archive rule

A **distinct output path**, fixed in advance:
`verification/runs/F14-cooling-ladder/K0b_D406_repair/`.

The rung tree `K0b_mesh_sensitivity/` will **not** be re-run in place. Its two
legs hold **36 tracked files** — both `COST.txt`, every solver log,
`system/controlDict.4000` — and `build_and_run.sh` opens each leg with
`rm -rf "$dst"`. Re-running in place would destroy the published record this
run exists to grade, which is the same reason the D403 lane gave for the same
decision.

`build_and_run.sh` and `analyse_k0b_mesh.py` will be copied into that tree and
run there **with no edit of any kind** — this task's whole claim is that the
committed script needs none. Byte-identity of both copies with the committed
blobs will be proved by `git hash-object` and by `cmp`, and both figures
reported. `$HERE` is the only thing that differs, and it decides only where the
legs are built; the 64x64 leg is resolved by name through `lab_paths` in both
trees.

**The committed archive case at `verification/runs/THERMAL_K0_runs/` will not
be written to.** All of its files will be md5-summed before and after, and the
count of changed files reported whatever it is. The D403 lane recorded 88 of 89
unchanged with `log.cellCentres` the exception, an untracked OpenFOAM log the
analysis regenerates by design; the same exception is expected and will be
named rather than absorbed.

## 5. Predictions, fixed before the first solve

### P-A — the repaired script alone reproduces the published fine leg

**Predicted: yes, exactly.** Running only the two commands the README
documents, from a clean start, with no hand edit, the 128x128 leg shall be
continued automatically to t = 16000 and produce
`Nu_avg_hot = 4.528816741169209`.

| |Nu_avg_hot(128x128) − 4.528816741169209| / 4.528816741169209 | reading |
| --- | --- |
| **< 0.1 %** | the published fine leg REPRODUCED by the script unaided |
| 0.1 % – 1 % | reproduced in kind, deviating in value; every deviation quoted as a number |
| **> 1 %** | **NOT REPRODUCED. D406 does not close**, and this is to be reported ahead of every other result in the record |

The stronger prediction, made because the D403 re-run showed this solver to be
deterministic on this box: **bit-for-bit, on all 13 quantities of both legs the
script builds** — `Nu_avg_hot`, `Nu_avg_cold`, `Nu_max_hot`, `Nu_min_hot`,
`V_star_max`, `V_star_min`, `U_star_max`, `U_star_min`, `x_over_L_at_v_max`,
`stratification_S_leastsq_mid25pct`, `energy_balance_pct`, `Pr`, `dT_K`.
Deviation predicted to be **0**, not merely under threshold.

### P-B — the 32x32 leg is NOT continued

**Predicted: the coarse leg stops itself at t = 1386 on `residualControl`, the
script reads that from its log and does not enter the second stage.** Its
written times, its 139-entry `Nu_history_by_time` and its published
`Nu_avg_hot = 4.649689954678544` are therefore unchanged. `K0b_m32/system/`
shall carry **no `controlDict.4000`**, because none is created for a leg that
is not continued — the published `K0b_m32` carries none either.

A continuation that fired on the 32x32 leg would be a **defect of this repair**
and would be reported as one: it would move a published number for no reason.

### P-C — the ladder statistics

Predicted, with the 64x64 read in place from the archive: the triple monotone
on all six graded quantities, `Nu_avg_hot` observed order **p = 1.9404946505**,
Richardson extrapolate **4.52001514525647**, fine-pair **GCI = 0.24293310 %**,
64→128 change **0.5516276644 %**. Predicted deviation from the published
`richardson` block: **0 on every leaf**.

### P-D — the artifacts the second stage leaves

Predicted, and each is checkable independently of the physics:

1. `K0b_m128/log.buoyantBoussinesqSimpleFoam.continue` exists, opens at
   `Create mesh for time = 4000`, and ends at `Time = 16000`.
2. `K0b_m128/COST.txt` carries a `continue_wall_clock_s` line, appended not
   rewritten, so that `analyse_k0b_mesh.cost` sums both halves.
3. `K0b_m128/system/controlDict.4000` is **byte-identical to the published
   one**, and to the archive case's own `system/controlDict`.
4. `K0b_m128/system/controlDict` after the run is **byte-identical to the
   published one**.

**Registered here as already executed, before any solve, because it is a static
check and pretending otherwise would be dishonest:** the three-key rewrite was
applied offline to the archive case's own `system/controlDict` and the output
`cmp`-compared to the published `K0b_m128/system/controlDict`. Exit **0** —
byte-identical. That establishes the derivation is right; it does not establish
that the script performs it, which is what the run is for.

### P-E — the end-to-end JSON

Predicted: `k0b_mesh_sensitivity.json` produced by the unmodified
`analyse_k0b_mesh.py` differs from the published one only in **wall-clock and
derived-cost leaves** and in the **`case` path strings** that D403's own path
repair changed. **Zero physics leaves.** Every differing leaf will be
enumerated and classified whatever the count turns out to be.

## 6. The convergence criterion, and D407

Unchanged from the D403 pre-registration §5, restated so this run is graded by
the same rule: a leg counts as **CONVERGED** only if the initial residuals of
all four solved variables met the case's own `residualControl` — `p_rgh 1e-07`,
`U 1e-08`, `T 1e-08` — or the run terminated because `residualControl` fired.

**Registered before this run rather than discovered by it:** D407 records that
across the whole ladder exactly one leg met that criterion, the 32x32, and that
`analyse_k0b_mesh.py:264-265` offers the 64x64 leg's convergence warrant as one
residual of four — the smallest, standing 9.6x above its own target while U
stands 16x above.

**This repair is predicted NOT to change that picture** (P-F): the continued
128x128 leg is predicted to stop at `endTime 16000` at 2.36e-08 / 2.77e-08 /
2.51e-08 / 3.44e-08, meeting only the `p_rgh` target, exactly as the published
leg did. The second stage's gate reads the solver's termination statement,
which is not the reporting habit D407 names.

**D407 is not repaired here and is not folded into this task.** Its repair is
one line of `analyse_k0b_mesh.py`, this task does not edit that file, and a
repair landed inside the commit that also grades this one would not be
separately checkable. Whether the picture moved will be stated explicitly in
the results record either way.

## 7. Verdict mapping, fixed here

Vocabulary is the fixed set — PASS, GATE REACHED, GATE FAIL, NOT A RESULT,
BLOCKED, PENDING.

| Item | PASS if | GATE FAIL if |
| --- | --- | --- |
| **W1 — the repaired script reproduces the published rung unaided** | the two documented commands, unmodified, from a clean start, land every graded quantity of both built legs within 0.1 % of its published value | any graded quantity deviating > 1 % |
| **W2 — the repair does not disturb the converged leg** | the 32x32 leg is not continued, stops at t = 1386, and reproduces its published numbers | the 32x32 leg is continued, or its stopping time or any published number moves |
| **W3 — the ladder statement survives the repair** | the triple monotone, `Nu_avg_hot` order and GCI reproducing the published values | the triple non-monotone on `Nu_avg_hot` |
| **W4 — the committed archive case is untouched** | every tracked file of `verification/runs/THERMAL_K0_runs/K0b_cavity_Ra1e5` md5-unchanged, and `git status` on that tree empty | any tracked file changed |

Anything between 0.1 % and 1 % is reported as a number and carries no verdict.

**NOT A RESULT** if a leg failed to mesh, failed to solve, or produced a field
the analysis could not parse. **BLOCKED** if the archive could not be resolved,
or if the §2 hard stop was reached.

**D406 closes only on W1 PASS.** W1 is the whole of D406's own "to settle":
*"encode the continuation in `build_and_run.sh` … so that the script alone
reproduces the published leg, and re-run the rung once against the amended
script to prove it."*

## 8. What this is not

**Not a validation.** K0b is a capability rung graded against no published
datum and nothing here changes that. The de Vahl Davis reference values live in
K0c next door and are not applied: these cases keep K0b's `Pr = 0.706814` and
its `limitedLinear`/`linearUpwind` schemes deliberately.

**Not a re-measurement of the physics.** The D403 re-run already established
that the published numbers reproduce bit-for-bit under the published protocol.
What is under test here is whether the committed script performs that protocol
without a human in the middle of it.

**Not a re-costing of the original rung.** The core-minutes charged here are
this repair's proof run.

**`energy_balance_pct` is reported and never gated on.** It is an identity on
this sealed, Dirichlet-walled case, per `VERIFICATION_CHARTER.md:106-111`, and
an identity is not a control. The same holds for the internal assertion at
`analyse_k0b_mesh.py:270`, which checks one estimator of the hot-wall Nusselt
number against another estimator of the same cells.
