# A5 U-bend — re-verification at np=1, shipped vs patched IDWarp: PRE-REGISTRATION

**Filed 2026-08-21, Lane A, BEFORE any arm of this run was launched.** Predictions, acceptance
bands and falsifiers are committed first; `RESULTS.md` is written afterwards and does not revise
this file. Nothing filed upstream.

---

## 1. Questions — there are two, and the second one is the reason this arm is worth more than a repeat

**Q1 (the stated one).** Does A5's published verdict — **FAIL against the shipped toolchain,
`OBJ.val wrt shapexUpper` 46.64%, idx8 and idx17 sign-flipped** — reproduce **at np=1**, and does
the rotation patch, delivered as the new image `dafoam-idwarp-rot:v1`, still collapse it?

**Q2 (the one that closes a live open item).** **Is A5's gradient decomposition-invariant on the
SHIPPED stack?** The record asserts it is, but the assertion is **mis-sourced**, and my own Phase-0
inventory flagged it as still live:

> **Merely asserted:** that A5 is decomposition-invariant. `W4-a5-decomp/run.sh:28` sets
> `PYTHONPATH=/patch/idwarp`, so the cited measurement covers the **patched** gradient, not the
> stock one it is cited for.
> — `../../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §2.2, first flagged 2026-08-11 and
> re-confirmed live 2026-08-15.

Every published stock A5 number was measured at **np=4** (`W5-regrade/run_a5_checktotals.sh:2`).
**A stock np=1 A5 `check_totals` does not exist anywhere in the archive.** Arm 1 of this run creates
it, and by comparing it against the published np=4 stock number it settles, by measurement, a claim
that has been carried on the wrong evidence for ten days. That is a free by-product of an arm that
had to be run anyway.

## 2. Case and configuration

Reused **exactly** from the recorded regrade arms; every departure is in §3.

| item | value | source |
|---|---|---|
| case | staged copies of `/home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock` — the **pressure-loss** configuration the published 46.64% came from, *not* the stock-objective sibling in the patch tree | `../../W5_GRADIENT_REGRADE.md` §4, §4a |
| mesh | **4,800 cells** (`nCells: 4800`), 6-block `blockMesh`, half-model with a `sym` plane | `../../A5_ubend_internal.md:56` |
| solver | `DASimpleFoam`, SA, `endTime 1000`, **stock `fvSolution`** (not the tightened 2026-07-30 variant) | frozen record |
| objective | `OBJ.val = TP1 − TP2`, pure pressure loss | `A5_work/.../runScript.py:160` |
| task / DVs | `check_totals(of=["OBJ.val"], wrt=["shapexUpper"], step=1e-4, form="central", step_calc="abs")` — 27 components, 55 primal solves | `a5pl_stock/runScript.py`, `check_totals` branch |
| container caps | `--cpus=4 --memory=8g` (unchanged from the recorded script) | `run_a5_checktotals.sh:12` |

## 3. Departures from the recorded run, each disclosed

1. **`mpirun -np 4` → `-np 1`.** Instructed, and the substance of Q2. The case's own
   `system/decomposeParDict` says `numberOfSubdomains 4; method scotch;`; DAFoam rewrites that file
   from `daOptions` at startup to match the actual rank count, so np=1 runs undecomposed. **If the
   log shows a 4-way decomposition anyway, the arm is invalid and stops.**
2. **Patched arm uses image `dafoam-idwarp-rot:v1`** instead of stock +
   `-v W5-patch:/patch` + `PYTHONPATH`. Same patched bytes (`libidwarp.so` md5
   `85f59e87253e0a71a813f64ca6e4c425`), different delivery.
3. **Coloring cache.** The staged copies carry `dRdWColoring_4.bin`; np=1 will build a fresh
   coloring. Wall-time cost only.
4. `sudo rm -rf processor*` before each arm.
5. **No trivial-baseline arm here.** A1 carries the Charter-2c wrong-step control for this pair of
   runs; adding a third A5 arm would roughly double this item's cost for a control already
   exercised on the cheaper case. Named as a deliberate omission, not an oversight.

## 4. Arms, predictions, falsifiers

Band (`../../A_stepsize_study.md:91-93`): **PASS ≤5%** with zero flagged components;
**CONDITIONAL 5-15%**; **>15% or any flagged component → FAIL**.

### Arm 1 — SHIPPED

`dafoam/opt-packages:latest`, stock IDWarp (`libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663`),
np=1, step 1e-4.

> **PREDICTION.** Aggregate **46.6% ± 2 percentage points** (published np=4: `4.663773e-01`), with
> **two sign-flipped components at idx8 and idx17**, idx8 ≈ 207.6% and idx17 ≈ 121.6%, and **5 of 27
> components inside ±12%** (idx 1, 2, 16, 24, 25). **Verdict predicted: GATE FAIL.**
>
> The ±2 pt band is wider than A1's because — per Q2 — **nobody has ever measured this case's stock
> gradient at any rank count other than 4.** I am predicting invariance; I am not entitled to
> predict it tightly.
>
> **FALSIFIERS, and each maps to a different conclusion.** (a) Aggregate outside 44.6–48.6% **but
> still failing with both flips** → A5 is decomposition-*sensitive* on the stock stack, the
> `S1 §2.2` flag was justified, and a new item opens. (b) Aggregate ≤15%, or either flip absent →
> the published stock number is decomposition-dependent in a strong sense, which would be a
> significant new finding and would need its own arm before anything is concluded. (c) A different
> pair of components flipping → the idx8/idx17 localisation does not survive serial execution.

### Arm 2 — PATCHED

`dafoam-idwarp-rot:v1`, np=1, step 1e-4, otherwise identical to arm 1.

**Two published patched numbers exist for this row, and the brief requires both to be registered
along with which one this run will actually print. They are not alternatives — they are outputs of
two different instruments, and only one of them is a thing `check_totals` can emit.**

| number | what it is | will this run print it? |
|---|---|---|
| **2.2372%** (`2.237182e-02`) | the aggregate **OpenMDAO's own `check_totals` reports**, computed against **its own internally-generated FD column** — which at component **idx16** reads `−4.30296296` | **YES — this is what arm 2 will print** |
| **0.1826%** | the aggregate obtained by **substituting idx16's FD reference** with a re-measured, sequence-faithful value of **−5.04286**, then recomputing the vector norm from the extracted per-component table | **NO — `check_totals` cannot print this.** It is a post-hoc correction applied to the extracted table, not an alternative run |

> **PREDICTION. Arm 2 will print an aggregate of 2.24% ± 0.3 pt, with ZERO sign flips** (idx8 and
> idx17 both right-signed), **26 of 27 components inside ±12%**, and **idx16 as the single
> out-of-band component at ≈17.3%**. **Verdict predicted: PASS on the ≤5% aggregate band.**
>
> **Why 2.2372% and not 0.1826%, stated as the mechanism rather than the preference.** The 0.1826%
> figure comes from `../../W4_IDX16_IS_THE_REFERENCE.md`, which found that
> `check_totals`' own reported FD at idx16 (`−4.30296296`) **is not reproducible by any independent
> finite difference of the same function at the same step in the same container**: three
> measurements — cold from `0/`, warm from the converged baseline, and warm from the state
> `check_totals`' own component sequence leaves — return **−4.98068, −5.05964 and −5.04286**, none
> of them `−4.30296296`, while the *same* harness reproduces `check_totals`' FD at the neighbouring
> idx15 to **8.8e-08 relative**. Against the sequence-faithful `−5.04286`, idx16's analytic error is
> **25.1% stock → 0.10% patched**, not 12.27% → 17.31%, and the corrected aggregate is 0.1826% with
> the table in band **27 of 27**.
>
> **`check_totals` will nonetheless recompute its own `−4.30296296`-flavoured reference, because
> that behaviour is deterministic** — it reproduced across both runs and all four ranks in the
> published pair — **and nothing in this arm changes the primal or the FD path.** So arm 2 prints
> 2.2372%; recovering 0.1826% requires extracting the 27-row table and substituting the re-measured
> idx16 FD, which is a free post-processing step and **is planned as part of `RESULTS.md`**. Both
> numbers will be reported, each labelled with the instrument that produced it. Neither is "the"
> answer on its own.
>
> **THE CONTROL: the FD column must not move between arms 1 and 2.** The patch is derivative-only
> and the primal warp is md5-identical (`../../PATCH_getRotationMatrix3d.md` §9.5). Every
> `Fd Magnitude`, and every one of the 27 raw FD components, must be **bit-identical** across the
> two arms. **If any FD entry moves, stop and report** — the comparison is then between two
> different functions and no conclusion survives, and it would also mean the new image is not a
> clean single-variable change.
>
> **FALSIFIERS.** (a) Any FD entry differing between arms → stop. (b) Aggregate above 10% → the
> image is not delivering the patch, whatever `IDWARP_SO_MD5` says. (c) Either idx8 or idx17 still
> sign-flipped → the patch does not reach this case at np=1, contradicting four prior measurements.
> (d) idx16 *inside* the band at ≈12% → the published 17.31% is itself rank-dependent, which would
> reopen `W4_IDX16` rather than settle it.

## 5. Cost, registered before the runs

Anchor: the published np=4 pair cost 235 s + 250 s wall at 4 ranks = **32.3 core-min**
(`../../W5_GRADIENT_REGRADE.md` §5) for 55 primal solves per arm on 4,800 cells.

| arm | ranks | predicted wall | predicted core-min | predicted $ @ $0.0513/core-hr |
|---|---|---|---|---|
| 1 SHIPPED | 1 | ~700 s | ~11.7 | $0.010 |
| 2 PATCHED | 1 | ~700 s | ~11.7 | $0.010 |
| **total** | | | **~23** | **~$0.020** |

**Registered ceiling: 45 core-min / $0.04.** Container `timeout` 1800 s per arm; arms run
sequentially at `--cpus=4`, i.e. exactly the lane's 4-core cap and never beyond it. `uptime` and
`nproc` are checked before each launch and the arm waits on a bounded loop if load > 10. Nothing is
started that cannot be waited out; no `kill` is required.

**Cost risk, stated up front:** a 4× rank reduction on a 55-solve sweep is the one place this item
could overrun. If arm 1 exceeds 1800 s the arm is recorded as **BLOCKED (wall)** and arm 2 is
re-scoped to np=2 rather than silently extended.

## 6. What this run will not be able to see

1. **The 2.24% (or 0.18%) residual after the patch is not explained by this run and will not
   become explained by it.** A1's patched residual is 0.037%; A5's is 60× higher on the same patch.
   `../../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §2.2 is explicit that it *"is genuinely open
   and must not be described as root-caused"*. This arm reproduces it; it does not attack it. The
   priced attack is **C-2** (`useRotations=False`, ~16 core-min) and is not part of this item.
2. **`dF/dW`'s scaling anomaly** (`AN/FD = 35.28` for TP1, `8.4` for TP2, exactly,
   direction-independent) is untouched and stays open; `getdFScaling` remains the named place to look.
3. **Only `shapexUpper` is graded.** The other five FFD DV groups (`shapexLower`, `shapey*`,
   `shapez*`, 162 components in total) are computed by the solver but are outside the `check_totals`
   restriction, exactly as in the published rung.
4. **The limiter axis.** A5's `fvSchemes` was never audited for a `cellLimited` gradient scheme and
   no `limited`/`default` arm exists for this case. Whatever A5's convection scheme is, this run
   does not vary it.
5. **Regime 2 of the rotation defect** — `check_totals` sits at the undeformed baseline where the
   guard fires; the near-threshold ill-conditioned regime is invisible here and remains unpatched.

## 7. Verdict vocabulary

PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING. Shipped and patched verdicts are
reported as **two separate rows**, never merged.
