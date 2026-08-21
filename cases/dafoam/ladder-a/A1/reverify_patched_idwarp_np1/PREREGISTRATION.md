# A1 NACA0012 — re-verification at np=1, shipped vs patched IDWarp: PRE-REGISTRATION

**Filed 2026-08-21, Lane A, BEFORE any arm of this run was launched.** Predictions, acceptance
bands and falsifiers below are committed first; `RESULTS.md` is written afterwards and does not
revise this file. Nothing filed upstream.

---

## 1. Question

Does the published A1 verdict — **FAIL against the shipped toolchain, `CD wrt shape` 11.43% with
component idx6 sign-flipped** — reproduce **at np=1**, where no mesh decomposition exists at all;
and does the IDWarp rotation patch, **delivered this time as a container image rather than as a
bind-mount**, still collapse it?

Two things make this worth the ~5 core-minutes it costs:

1. **Every published A1 gradient number was measured at np≥2.** The frozen record ran np=2
   (`../../A1_naca0012_incompressible.md`); the W5 regrade ran np=2
   (`W5-regrade/run_a1_checktotals.sh:2`). The only np=1 A1 numbers in the archive are from the
   **limiter/freestream transplant** arms (`W4-defect-robustness/a1fs_np1.log` etc.), which are a
   *different case setup*. **There is no np=1 stock-A1 `check_totals` on record.** This run creates
   the first one, and it is the arm that removes the decomposition axis entirely.
2. **The patched image is new** (`dafoam-idwarp-rot:v1`, built today, `../../patched_build/BUILD.md`).
   Every prior patched number came from `-v W5-patch:/patch` + `PYTHONPATH`. If the image is a
   faithful delivery of the same patch, it must reproduce the bind-mount's numbers; if it does not,
   the image is wrong and must not be used. **This run is as much a test of the image as of A1.**

## 2. Case and configuration

Reused **exactly** from the recorded regrade arms; every departure is listed in §3.

| item | value | source |
|---|---|---|
| case | `/home/ubuntu/certonomous-runs/W5-regrade/a1_unpatched` (stock arm) and `a1_patched` (patched arm) — the two directories the published regrade used | `W5-regrade/run_a1_checktotals.sh` |
| mesh | 4,032 cells, NACA0012 official DAFoam tutorial, unmodified | `../../A1_naca0012_incompressible.md:32` |
| solver | `DASimpleFoam`, `primalMinResTol=1e-8` | frozen record |
| task | `python runScript.py -task check_totals` | unchanged |
| FD | `step=1e-3, form="central", step_calc="abs"` — hard-coded in the case's own `runScript.py` | `a1_unpatched/runScript.py`, `check_totals` branch |
| design variables | 8 shape (FFD) + 2 `patchV`; 21 primal solves per sweep | frozen record |
| container caps | `--cpus=2 --memory=8g` (unchanged from the recorded script; 2 ≤ the 4-core lane cap) | `run_a1_checktotals.sh:16` |
| convection scheme | **`div(phi,U) bounded Gauss linearUpwindV grad(U)` — the tutorial default, UNLIMITED** | see §6 |

## 3. Departures from the recorded run, each disclosed

1. **`mpirun -np 2` → `-np 1`.** Instructed (serial before parallel). This is the substantive
   departure and it is what §1 makes the point of the arm.
2. **Patched arm uses the image `dafoam-idwarp-rot:v1`** instead of
   `dafoam/opt-packages:latest` + `-v /home/ubuntu/certonomous-runs/W5-patch:/patch` +
   `export PYTHONPATH=/patch/idwarp`. The patched **bytes** are identical either way — the image
   COPYs the same `libidwarp.so`, md5 `85f59e87253e0a71a813f64ca6e4c425` — but the delivery
   mechanism differs and is itself under test.
3. **Coloring cache.** The case directories carry `dRdWColoring_{2,4,8,16}.bin` but **no
   `dRdWColoring_1.bin`**, so the np=1 arms will compute a fresh coloring. This costs wall time and
   changes nothing numerically.
4. `sudo rm -rf processor*` before every arm (standing trap,
   `../../A1_naca0012_incompressible.md` Lesson).

Everything else — mesh, `runScript.py`, `daOptions`, FD step, DV set, `fvSchemes`, `fvSolution` — is
byte-identical to the recorded arms.

## 4. Arms, predictions, and falsifiers

Grading band (`../../A_stepsize_study.md:91-93`): **PASS ≤5%** with zero flagged components;
**CONDITIONAL 5-15%**; **>15% or any flagged component → FAIL**. The reported statistic is
OpenMDAO's vector-relative error `‖Jan − Jfd‖/‖Jfd‖` on `CD wrt dvs.shape` unless stated.

### Arm 1 — SHIPPED

Image `dafoam/opt-packages:latest`, stock IDWarp (`libidwarp.so` md5
`f0fcb488e0e98156575cd19548e91663`), np=1, step 1e-3.

> **PREDICTION.** `CD wrt shape` **11.4% ± 0.5 percentage points** (published np=2 value:
> `1.142743e-01`), with **exactly one sign-flipped component, at index 6**. `CL wrt shape` ≈ 1.67%.
> `CD`/`CL` wrt `patchV` ≈ 0.232%. Geometric constraints at machine precision (1e-14 to 1e-10).
> **Verdict predicted: GATE FAIL.**
>
> The ±0.5 pt band is not decoration: np=1 is a genuinely different arm from the published np=2, and
> A1's recorded decomposition-invariance (analytic invariant to **3.9e-04** across np=1 vs
> np=4-scotch, `../../VERIFICATION_A1_serial_limiter_supervisor_sweep.md` axis 2) was measured on
> the *limiter/freestream* variant, not on this one. I expect near-exact reproduction and am
> registering a band rather than a point because I have not measured it.
>
> **FALSIFIERS.** (a) `CD wrt shape` outside 10.9–11.9% → A1 is **not** decomposition-invariant on
> the stock case, which would be a new finding and would need its own arm. (b) No sign flip, or a
> flip at an index other than 6 → the published root-cause localisation is wrong. (c) Geometric
> constraints worse than 1e-8 → the harness is broken and no other number in the run means anything.

### Arm 2 — PATCHED

Image `dafoam-idwarp-rot:v1` (patched `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425`), np=1,
step 1e-3. Everything else identical to arm 1.

> **PREDICTION.** `CD wrt shape` **0.0375% ± 0.01 pt** (bind-mount np=2 value: `3.744509e-04`),
> **zero sign flips**, idx6 right-signed. `CL wrt shape` ≈ 0.0149%. **Verdict predicted: PASS.**
>
> **THE CONTROL THAT MAKES THIS READABLE, and it is the strongest single check in the run: the FD
> column must not move.** The patch touches only `src/adjoint/output{Reverse,Forward}/
> vectorUtils_{b,d}.f90` — derivative code — and the primal warp is md5-identical patched vs
> unpatched (`../../PATCH_getRotationMatrix3d.md` §9.5). So **every `Fd Magnitude` in arm 2 must be
> bit-identical to arm 1**. If it is not, the two arms are measuring different functions and nothing
> can be concluded from the comparison.
>
> **FALSIFIERS.** (a) Any `Fd Magnitude` differing between arms 1 and 2 → **stop and report**; the
> image is not a clean single-variable change. (b) `CD wrt shape` above 1% → the image is not
> delivering the patch, even if `IDWARP_IMPORTED_FROM` looks right. (c) The `patchV` and geometric
> constraint rows moving at all → they do not cross `warpDeriv` and cannot legitimately move
> (this is identity-gate **IG-2**, `../../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §5.2 — it is
> reportable evidence but must not be *gated on*, so it is listed as a falsifier of the image, not
> as a pass criterion for the patch).

### Arm 3 — TRIVIAL BASELINE (Charter 2c), deliberately wrong FD step

Image `dafoam-idwarp-rot:v1` (**patched** — the stack predicted to PASS), np=1, **`step=1e-8`**,
everything else identical to arm 2.

> **PREDICTION.** `CD wrt shape` **> 50%**, i.e. a **GATE FAIL on a stack that passes at the
> registered step.** From the step-size study on this exact case
> (`../../A_stepsize_study.md`, sweep table): the full-8-vector error at `step=1e-8` is **94.95%**
> against 11.43% at 1e-3, cosine 0.407 — the roundoff-dominated branch.
>
> **Why 1e-8 and not the 0.1× or 10× the brief suggested.** On A1 those are `1e-4` and `1e-2`, and
> the step study *measured* both: **11.52%** and **8.94%** — i.e. both sit **inside the
> well-converged plateau** (1e-4 through 3e-2, flat at 2.5–3.0% excluding the flagged components).
> A step inside the plateau is not a wrong step on this case; using one would produce a control that
> passes for the same reason the real arm does, which is exactly the failure mode a trivial baseline
> exists to exclude. The measured roundoff branch starts below 1e-4 and is severe by 1e-8. **This
> departure is deliberate and is justified by a measurement, not by preference.**
>
> **What it discriminates.** It proves the instrument can still return a large number after the
> patch — i.e. that arm 2's 0.0375% is a property of the derivative and not of a harness that has
> been rendered incapable of failing.
>
> **FALSIFIERS.** (a) Arm 3 returning ≤5% → the FD reference is not sensitive to step size at all,
> which would invalidate every FD number in this record including the published ones. (b) A primal
> solve failing to converge → the arm is NOT EVALUABLE, not a pass (the step study records genuine
> solver failures at 5e-2 and 1e-1, not at 1e-8, so this is not expected).

## 5. Cost, registered before the runs

Anchor: the published np=2 pair cost 65 s + 53 s wall at 2 ranks = **3.9 core-min**
(`../../W5_GRADIENT_REGRADE.md` §5).

| arm | ranks | predicted wall | predicted core-min | predicted $ @ $0.0513/core-hr |
|---|---|---|---|---|
| 1 SHIPPED | 1 | ~130 s | ~2.2 | $0.0019 |
| 2 PATCHED | 1 | ~130 s | ~2.2 | $0.0019 |
| 3 TRIVIAL BASELINE | 1 | ~130 s | ~2.2 | $0.0019 |
| **total** | | | **~6.6** | **~$0.006** |

**Registered ceiling: 20 core-min / $0.02.** If the run exceeds it, the overrun is reported against
this number rather than explained. Each arm is bounded by an explicit `timeout` on the container and
runs foreground-or-polled; no unbounded process is started. Host `uptime` load and `nproc` are
checked before each launch and the arm waits if load > 10.

## 6. What this run will not be able to see, stated in advance

1. **The limiter defect.** These arms use the tutorial's **unlimited** `div(phi,U) bounded Gauss
   linearUpwindV grad(U)`. The second, independent A1 defect — `cellLimited Gauss linear 1` feeding
   `linearUpwind`, which reads **92.8%** at np=1 with the rotation guard *already patched*
   (`../../DEFECT_ROBUSTNESS_mesh_and_setup.md` R7) — **cannot appear in any arm of this run**,
   because the scheme that triggers it is not installed. A PASS in arm 2 is a PASS *for this scheme
   configuration only* and must not be read as "A1 is fixed".
2. **The decomposition axis**, by construction: np=1 has no partition.
3. **Regime 2 of the rotation defect.** `check_totals` evaluates at the undeformed baseline, where
   the `sqrt(eps)` guard fires and regime 1 dominates. The near-threshold ill-conditioned regime —
   measured at ~1.26% on IDWarp's own `onera_m6` mesh and **unpatched** — only appears at deformed
   states and is invisible here (`../../ROOTCAUSE_getRotationMatrix3d.md` §6.4, §4.9).
4. **Per-component behaviour beyond the aggregate**, unless the raw `Jfor`/`Jfd` vectors are
   extracted. `compact_print=False` is set, so they will be in the logs; extracting them is planned
   and is free.

## 7. Verdict vocabulary

PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING. Shipped-toolchain and
patched-toolchain verdicts are reported as **two separate rows**, never merged.
