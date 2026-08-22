# A3 ONERA M6, sweep rung 2 (42,120 cells) — the patched-IDWarp arm at np=4: PRE-REGISTRATION

**Filed 2026-08-22, Lane A, BEFORE any arm of this run was launched.** Predictions, acceptance
bands and falsifiers below are committed first; `RESULTS.md` is written afterwards and does not
revise this file. Departures discovered after the commit are recorded as dated Amendments, never by
editing the text above them. **Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED
and is Sanaa's alone.**

---

## 1. Question

`LADDER_A_STATUS.md` row 12 reads **PENDING — NOT MEASURED**, quoting
`A3/grading_confirmation/RESULTS.md` §3: *"No patched-IDWarp arm was ever run on A3, at any mesh
size."* This item buys exactly one cell of that column: **sweep rung 2, 42,120 cells, np=4.**

The question is sharper than "does the patch help", because on this rung there is almost nothing
left to help. The stock row is the **tightest on the whole ladder** — `patchV[1]` **0.0077%**,
`twist[1]` **0.2740%**, `shape[115]` **0.0172%**, all three evaluable and step-consistent
(`A3_RUNG2_N28_RESULT.md`; `../grading_confirmation/RESULTS.md` §2c). The grading confirmation names
this as an unexplained fact and as the thing its own reading cannot see (§5.1):

> *"A3's PASS rows are stock-IDWarp results, so they carry whatever rotation-defect content this
> case's `dObj/dXv` field happens to contract with — which on A1, A2, A5 and the sail was 97–99.5%
> of the error. That A3's rungs pass at 0.0077–0.93% **without** the patch is genuinely interesting
> and is not explained."*

So the measurement this arm buys is **not** an improvement figure. It is the size of the rotation
defect's contribution to *this* case's shape and twist gradients — the analytic-vs-analytic patch
effect — against a fixed FD reference that must not move. Three outcomes are all informative and all
are pre-mapped in §6.

## 2. Case and configuration

Reused **exactly** from the graded rung-2 arm B; every departure is listed in §3.

| item | value | source |
|---|---|---|
| case | staged copy of `/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/` (itself the staged copy the graded rung-2 arms ran in) | `A3_RUNG2_N28_PREREGISTRATION.md` §7 |
| **run root (new)** | `/home/ubuntu/certonomous-runs/P3-a3-rung2-patched/` — arms in `patched/` and `wrongstep/` | this file |
| mesh | **42,120 cells**, pyHyp N=28 on the 3×-coarsened M6 surface; `points_sha256 7eb9866ec3a810f4557c1ced08977d4b7553a6c04e5f06a3f364722b8d342d24`; `constant/birth_certificate.json` verdict **clean** carried with the copy | `A3_RUNG2_N28_PREREGISTRATION.md` §1 |
| solver | `DARhoSimpleCFoam`, `primalMinResTol 1e-8`, `primalMinResTolDiff 1e4` | `runScript_fd3.py` |
| adjoint | `transonicPCOption 1`, stock ILU(0) (`pcFillLevel 0`), `jacMatReOrdering natural`, `gmresRestart 200`, `gmresRelTol 1e-4`, `gmresMaxIters 2000`, `DAFOAM_SUBPC_TYPE` **unset** | `runScript_fd3.py` |
| task | `-task fd3` — 1 cold primal, 1 CD adjoint, runtime `argmax|g|` per DV group, central FD at h=1e-2 and 2h=2e-2 on 3 components, repeat-baseline noise floor | `runScript_fd3.py` |
| FD convention | central, `step_calc` abs, h = 1e-2 / 2h = 2e-2 (the sizes that cleared this rung's measured floor) | `A3_RUNG2_N28_PREREGISTRATION.md` §5 |
| **np / decomposition** | **np = 4**, `decomposeParDict` `numberOfSubdomains 4`, `method scotch` — **the same np as the stock row**, because an FD reference is never carried across np (Charter §5) | `system/decomposeParDict` |
| container caps | `--cpus=4 --memory=12g`, `--rm`, foreground under `timeout`, `-x PYTHONPATH` | this file, §7 |
| image, PATCHED arm | **`dafoam-idwarp-rot:v1`**, image ID `2927768a16ac`, `libidwarp.so` md5 **`85f59e87253e0a71a813f64ca6e4c425`** | `../../../patched_build/idwarp_rot/BUILD.md` §2, §5 |
| image, stock row | **not re-run** — cited from `dafoam-subpclu:v1` (`DAFOAM_SUBPC_TYPE` unset), stock IDWarp md5 `f0fcb488e0e98156575cd19548e91663` | §3 departure 1 |

### The two-image comparability argument, stated before the run rather than after

`dafoam-idwarp-rot:v1` is built **FROM `dafoam/opt-packages:latest`** and is explicitly *not*
layered onto `dafoam-subpclu:v1` (`BUILD.md` §7 limit 4), so it carries **stock `DALinearEqn.C`**,
md5 `f6a89e33b0f4772a0563cb0c8633ac48`, 507 lines (`TOOLCHAIN_INVENTORY.md` §3). The stock rung-2
arm ran on `dafoam-subpclu:v1`, whose `DALinearEqn.C` is +19 lines — **all inside a branch entered
only when `DAFOAM_SUBPC_TYPE` equals `lu`**, with `env unset ⇒ stock behaviour` and the absence of
the banner `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` as the standing proof
(`TOOLCHAIN_INVENTORY.md` §3 table, §7 row for the A3 sweep rungs). The rung-2 arms ran with the env
unset and no banner. **The numeric path of the two images is therefore the same code**, and the
prediction that settles it empirically is **P3**: if the adjoint solve does not reproduce stock's
987 iterations and residual path bit-for-bit, that argument is wrong and the arm stops.

This is a stated gap, not a hidden one: it is why the stock row keeps the **‡ SHIPPED-equivalent**
label it carries in `LADDER_A_STATUS.md`, and §8 item 5 records what this item still cannot close.

## 3. Departures, each disclosed with its reason

1. **The shipped-image twin (`dafoam/opt-packages:latest`) is NOT run, and the existing stock row is
   cited instead.** The brief's condition for re-buying it is that the rung-2 stock logs do not
   already carry the raw arrays needed for per-component comparison. **They do**, and this was
   checked before filing:
   * `A3-rung2-n28-tpc1/fd3_run.log` carries, at 14–15 printed digits, the baseline `CD`
     (`:821`), the runtime component selection with its adjoint values (`:878–880`), **every** raw
     perturbed `CD(+h)`, `CD(−h)` at h and 2h for all three components (`:1105`–`:3585`), the
     repeat baseline and drift (`:3810–3811`), and the final per-component table
     (`:3813–3815`).
   * `A3-rung2-n28-tpc1/tpc1_computetotals_attempt2.log:899–1370` carries the **full analytic
     totals dict**, including the complete 120-component `CD wrt dvs.shape` row and the
     2-component `CD wrt dvs.patchV` row, printed by `print(totals)`.
   Re-buying that row would cost ~30 core-min and produce numbers already on disk. **Declined by
   the brief's own condition.**
2. **The `dRdWColoring_4.bin` cache is carried into the staged copy and NOT deleted**, against the
   brief's staging sentence and **in accordance with the binding family guidance it would
   contradict**. `FAMILY_SUPERVISION_GUIDELINES.md` §8 item 1 reads, of cold-start restoration:
   *"Partition and coloring caches stay untouched."* The cold-start hazard the rule exists for is
   pyDAFoam writing primal end state into time-0 — a **field-state** hazard, not a coloring one —
   and it is closed here by items 3 and 4 below plus prediction **P2**. Cost of the departure,
   measured not guessed: a fresh coloring pass on this exact mesh at np=4 took **460.02 − 39.44 =
   420.6 s** (`A3-onera-m6-sweep-n28_42120/run_opt5_onera_n28_42120.log:826,:885`) = **28.0
   core-min**, which is 76% of this item's entire predicted spend and buys no number. Carrying the
   cache also keeps the patched arm on the identical coloring the stock arm used, which is the
   comparability this item exists for. **If the supervisor wants the fresh-coloring variant it is
   +28.0 core-min and, the coloring being a deterministic function of mesh and partition, is
   predicted to change no digit.**
3. **Cold start proved, not assumed.** The staged copy is made from `A3-rung2-n28-tpc1` with
   `processor*`, `_bak_att*`, `reports/`, `mphys.html` and every `*.log` excluded. Its serial `0/`
   was verified **byte-identical to `0.orig`** by `diff -r` before filing (both untouched since
   2026-07-29; pyDAFoam writes state into `processor*/0`, not the serial `0/`). `decomposePar
   -force` runs inside the copy, and **P2** asserts this rung's cold-from-uniform signature in the
   log.
4. **`runScript_fd3.py` → `runScript_fd3p.py`, three changes, all disclosed and asserted by `diff`
   before launch:**
   * **(D1)** a provenance stamp block after the imports, printed **per MPI rank**: rank,
     `idwarp.__file__`, the md5 of the `libidwarp.so` adjacent to the loaded package, and the
     `idwarp` version string. Log-only, executes before any numeric call. It exists because
     `BUILD.md` §6 warns that Open MPI may not forward the parent environment to every rank and *"a
     rank that silently fell back to site-packages would produce a mixed-stack run"* — a per-rank
     hash is the only thing that closes it, and §2 of `BUILD.md` is explicit that the md5 is the
     **only** discriminator (version string and file size are identical across the two stacks).
   * **(D2)** one added line, `log0(repr(totals))`, immediately after `compute_totals` in the `fd3`
     branch — the same `print(totals)` form the stock arm-A log used, at default numpy print
     options so the two are directly diffable. Log-only. It is what makes prediction **P9**, the
     full-row analytic-vs-analytic patch effect, measurable at all.
   * **(D3)** a new `fd1wrong` task branch for the trivial baseline (§5, arm P-B). It touches no
     existing branch.
   **No numeric option, DV set, scheme, tolerance or step in the `fd3` branch is changed.**
5. **`-x PYTHONPATH` is added to the `mpirun` line** on both arms, per `BUILD.md` §6. On the stock
   arm it was absent and irrelevant (nothing was on `PYTHONPATH`).

Everything else — mesh, `constant/`, `system/`, `FFD/`, `daOptions`, `meshOptions`, DV set, FD steps,
`decomposeParDict`, the coloring cache, ranks — is byte-identical to the graded rung-2 arm B.

## 4. Grading bands

**Aggregate band** (`../../A_stepsize_study.md:91-93`, as cited by `LADDER_A_STATUS.md`):
**PASS ≤ 5%** with zero flagged components; **CONDITIONAL 5–15%**; **> 15% or ANY sign flip ⇒
FAIL.**

**This rung's stricter pre-registered per-component rule**, inherited unchanged from
`A3_RUNG2_N28_PREREGISTRATION.md` §5 and applied here so the two rows are graded by one instrument:

* **Evaluability gate:** a component is evaluable only if `|CD(+h) − CD(−h)| > 10 ×` the measured
  repeat-baseline drift.
* **Step-consistency gate:** `|FD(h) − FD(2h)| / |FD(h)| < 1%`.
* **Per-component verdict on evaluable components:** PASS < 5%, CONDITIONAL 5–15%, FAIL > 15% or
  sign flip.
* **Arm verdict:** PASS = all evaluable components PASS with ≥ 2 evaluable; CONDITIONAL = an
  evaluable component at 5–15% with none failing; FAIL = any FAIL; **NOT EVALUABLE** = < 2 evaluable,
  reported with the noise numbers and carrying no verdict either way.

**Error convention, named at the number** (Charter §2): the per-component figure is
`|J_an − J_fd(h)| / |J_fd(h)|`, a **per-component relative error**, not a vector norm. The **patch
effect** in §5 P9 is a **vector L2 relative difference** `‖g_patched − g_stock‖₂ / ‖g_stock‖₂` between
two **analytic** vectors with no FD in it. These are three different statistics and none is quoted
against another.

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING. No other
word grades an arm here. **The SHIPPED-equivalent row and the PATCHED row are two rows and are never
merged**, and per R11 a patched number never moves a shipped grade
(`FAMILY_SUPERVISION_GUIDELINES.md` §3.4).

## 5. Arms and predictions, with bands

### Arm P-A — PATCHED

`dafoam-idwarp-rot:v1`, np=4, `-task fd3`, everything else as §2.

> **P1 — provenance and activity proofs. Band: exact, all four.**
> **(a)** every one of the 4 ranks prints `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425` and
> `IDWARP_IMPORTED_FROM: /opt/idwarp_patched/idwarp/__init__.py`;
> **(b)** the DAOption dump contains `transonicPCOption 1;`;
> **(c)** **zero** occurrences of `ASM sub-block PC set to complete LU`;
> **(d)** the `idwarp` version string reads `2.6.2` — recorded as the demonstration that it
> discriminates nothing (`BUILD.md` §2), not as a check.
> **Falsifier:** any rank reporting `f0fcb488…`, or a missing/`2;` `transonicPCOption` line, or a
> sub-LU banner → **the arm is void and stops.** A run without its stamp does not count
> (`FAMILY_SUPERVISION_GUIDELINES.md` §1, sweep finding W-2).

> **P2 — cold start. Band: exact to all 16 digits.** The first
> `Time step continuity errors : sum local` printed is **`0.6833296303785072`**, this mesh's
> cold-from-uniform signature (`A3_RUNG2_N28_PREREGISTRATION.md` §2), with `initRes ≈ 1` on all six
> fields.
> **Falsifier:** any other value → the copy warm-started, the arm is void and stops.

> **P3 — the adjoint. Band: exact.** The single CD adjoint returns
> **`PetscConvergedReason: 2` at exactly `Total iterations: 987`**, iteration-0 KSP residual
> **`2.121211553380e-02`**, and every printed `Main iteration N KSP Residual norm` bit-identical to
> `A3-rung2-n28-tpc1/fd3_run.log:863–874`.
> **Why exact and not a band:** the IDWarp patch touches
> `src/adjoint/output{Reverse,Forward}/vectorUtils_{b,d}.f90` only (`BUILD.md` §3) — the mesh-warp
> derivative, which enters the chain **after** `Aᵀψ = −∂F/∂W` is solved. The Krylov solve cannot see
> it. This is simultaneously the empirical test of §2's two-image comparability argument.
> **Falsifier:** a different iteration count, a different reason, or any residual difference → the
> two images do **not** share a numeric path, the stock-vs-patched comparison is void, **stop and
> report**. (Charter §6: a `reason 2` is not a verified gradient, so P3 is an *identity* check, not
> a pass criterion.)

> **P4 — THE CONTROL THAT MAKES THIS READABLE: the FD column must not move. Band: bit-identical,
> every printed digit.** The primal warp is untouched by the patch and `warpMesh` output is
> md5-identical patched vs unpatched, max|diff| = 0.0 (`BUILD.md` §3;
> `PATCH_getRotationMatrix3d.md` §9.5). So against `fd3_run.log`:
> baseline1 CD **`3.31180586539945e-02`**; baseline2 CD **`3.31188679497014e-02`**; drift
> **`8.093e-07`**; and all **twelve** perturbed CD values and **six** FD estimates identical,
> including `FD patchV[1] h=1e-2 = 7.90232345405165e-03`, `FD twist[1] h=1e-2 =
> 1.80882368935528e-03`, `FD shape[115] h=1e-2 = -1.30078077925157e-01`.
> This is the same control that held **8/8** on A1, **27/27** on A5, all 18 rows on A2 and all 9 on
> A6 (`LADDER_A_STATUS.md` reading 2). It has never failed and is registered anyway.
> **Falsifier:** any FD or baseline digit differing → the two arms are measuring different
> functions, nothing can be concluded from the comparison, **stop and report.**

> **P5 — component selection. Band: exact.** The runtime `argmax|g|` selection picks
> **`patchV[1]` of 2, `twist[1]` of 5, `shape[115]` of 120** — the same three the stock arm chose
> (`fd3_run.log:878-880`), so the two rows are component-matched with no index transcribed by hand.
> **Named alternative, not a falsifier:** if the patch moves an argmax, that is itself a finding
> (the patch reordered the gradient's largest component); the arm continues, the moved component is
> reported with its own numbers, and the per-component comparison against stock is explicitly
> **NOT A RESULT** for that group because no stock FD exists at the new index.

> **P6 — `patchV` is bit-identical, and it is evidence, not a gate. Band: exact.** `patchV` (U₀,
> AoA) is a boundary-condition DV and does not cross `warpDeriv`, so the patched analytic
> `dCD/dpatchV` reads **`[0.00068038, 0.00790293]`**, component 1 = **`7.90292882576689e-03`**,
> unchanged, and its per-component error is therefore **0.0077%** — the stock figure, to the digit.
> Precedent: A6 row 27, `CD/patchV` **bit-identical across images**; A1 §3, `patchV` and the three
> geometric-constraint rows identical to every printed digit.
> **Reported as identity-gate IG-2 evidence and explicitly NOT gated on**
> (`S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §5.2, sweep rule W-2). A difference here is a
> falsifier **of the image**, not a failure of the patch: it would mean the image changed something
> outside the warp chain → stop and report.

> **P7 — `twist[1]`, patched. Band: per-component relative error in `0.05% – 2.0%`, sign unchanged
> (positive), verdict predicted PASS.** Stock reads **0.2740%**. `twist` provably crosses the warp
> chain (A6 row 27 settled that its analytic derivative moves), and the two measured priors bracket
> the band from both sides: A6's `twist` analytic moved only **0.664% in L2** under this same patch,
> while A2's `CD/twist` is the one row on the ladder that the patch makes **worse** (0.389% →
> 0.505%). A band that admits both improvement and mild degradation is the honest one; I have not
> measured this row and am registering a band rather than a point.
> **Falsifier:** > 5% (CONDITIONAL) or any sign flip (FAIL) → the patch materially damages a row
> the stock toolchain gets right, which would be the first such result on this ladder and needs its
> own arm.

> **P8 — `shape[115]`, patched. Band: per-component relative error in `0.001% – 1.5%`, sign
> unchanged (negative), verdict predicted PASS.** Stock reads **0.0172%** — so on this rung the FD
> reference says the stock analytic is already right to 1 part in 5,800, and **there is essentially
> no error left for the patch to remove.** The prediction is therefore that the patched value stays
> in band; the *interesting* number is not this one but P9.
> **Falsifier:** > 5%, or a sign flip → the patch moves A3's largest shape component **away** from
> a fixed, independently-measured FD reference, which would be a genuine counter-example to
> "the patch is a fix" and is the single most consequential outcome this arm can produce.

> **P9 — the patch effect, analytic vs analytic, and the reason this arm is worth 30 core-min.
> Band: `‖g_patched − g_stock‖₂ / ‖g_stock‖₂` over the full 120-component `CD wrt dvs.shape` row in
> `0.005% – 5%`.** Both vectors are analytic; no FD enters. Stock's row is
> `tpc1_computetotals_attempt2.log:899-938`, patched's comes from D2.
> This is the number that addresses `../grading_confirmation/RESULTS.md` §5.1's open question
> directly: on A1/A2/A5 the rotation defect carried **97–99.5%** of the gradient error, on A6's
> `twist` it moved the answer **0.664%**, and on A3 the stock gradient is already correct to
> 0.0172%. Either the defect's contraction with **this** case's `dObj/dXv` is small (band low end,
> consistent with A6), or it is large and A3's stock PASS was luck (band high end).
> **Named alternative, registered so it cannot be re-read favourably:** a measured effect **> 15%**
> would mean the stock and patched shape gradients are materially different vectors while the stock
> one matches FD at 0.0172% — i.e. the patched one must then be the wrong one. That outcome is
> reported as **the patched row FAILing against the FD reference**, and the §5.1 question is
> answered in the surprising direction. It is not reported as a patch success.
> A measured effect **< 0.001%** (below the 8-digit resolution of the stock printout) is reported as
> **NOT A RESULT** for P9 — resolution-limited, no claim either way — with the raw vectors kept.

> **P10 — memory. Band: container aggregate peak RSS `9.0 – 11.5 GiB` against a `12 GiB` cap;
> host `MemAvailable` never below `8 GiB`.** Basis: the record aggregate peak at this exact member
> is **9,991.9 MiB = 9.76 GiB** (D3 Option 5, uncensored, quoted in
> `A3_RUNG2_N28_PREREGISTRATION.md` §7). The stock arm ran at `--memory=16g` and never approached
> it; **this arm runs at 12g, which leaves 2.24 GiB (23%) of headroom over the record peak, and that
> is a real and disclosed risk.** Watcher is **record-only** — it never kills anything.
> **Falsifier / stop rule (Charter §7):** an OOM kill, or a watcher sample above **11.5 GiB**, or
> host `MemAvailable` below **8 GiB** → the arm is **stopped by memory and recorded as such. It is
> NOT A RESULT about the patch, no conditioning or gradient claim is made in either direction, the
> cap is NOT raised, and no new budget is taken** (`COMPUTE_BUDGET_CHARTER.md`: a budget overrun
> stops the run; it does not get a new budget).

> **P11 — wall and cost. Band: wall `271 – 633 s` (measured stock basis 452 s ± 40%), core-min
> `18.1 – 42.2`.** The box is shared; contention is disclosed in `RESULTS.md` either way.

### Arm P-B — TRIVIAL BASELINE (Charter §4 / VERIFICATION_CHARTER §2c), deliberately wrong FD step

`dafoam-idwarp-rot:v1` — **the patched stack, the one predicted to PASS** — np=4, `-task fd1wrong`:
**one component subset, `patchV[1]` only, `step = 1e-8`, one step, no adjoint.**

**Why this design.** Charter §4 fixes the DAFoam trivial baseline as *"the same probe at a step
chosen to be wrong — an order of magnitude off the registered one"*, and requires it named before
its own run. Three choices are recorded here rather than left to the reading:

1. **Why 1e-8 and not 1e-3 or 1e-1.** On this rung the registered step is **1e-2**, chosen *from
   this rung's own measured noise floor*. A step one decade off (1e-3) was measured at **rung 1** to
   land in the NOT-EVALUABLE branch, not the wrong-answer branch, and would produce an ambiguous
   control. 1e-8 is the step the A1 step-size study measured at **94.95%** on the roundoff-dominated
   branch, and at which A1's registered control returned **132.75%** on a stack that reads 0.03796%
   at its own step (`../../A1/reverify_patched_idwarp_np1/RESULTS.md` §4.3). **The choice is
   justified by measurement, not preference.**
2. **Why `patchV[1]` and why one component.** It keeps the control under 10 core-min (§7). The index
   is **not** a hand transcription from any printed output — `patchV` is `[U0, aoa0]` with `U0`
   registered at `lower = upper = U0`, so index 1 (AoA) is the only free component by construction.
   The rung-1 mis-parse hazard is therefore not reopened.
3. **Why no adjoint.** The adjoint is ~204 s of the fd3 cost and would put the control over the
   "cheap" bar. Its analytic reference is arm P-A's own `patchV[1]` value, and **the check that
   licenses that reuse is registered**: P-B's baseline CD must equal P-A's baseline CD
   **bit-identically**, which proves the two arms are at the same primal state. If it does not, the
   control is reported as **NOT A RESULT** rather than compared.

> **P12 — the wrong step fails the rung's own evaluability gate, by four to five orders of
> magnitude. Band: `|CD(+h) − CD(−h)|` in `1.0e-10 – 2.5e-10`, against an evaluability threshold of
> `10 × drift`.** Arithmetic, from the stock log: at h=1e-2 the measured
> `CD(+h) − CD(−h) = 3.31966846004201e-02 − 3.30386381313391e-02 = 1.58046469081e-04`; the
> derivative being smooth, at h=1e-8 the true difference is `~1.58e-10`. The measured repeat-baseline
> drift is `8.093e-07` and the threshold `8.09e-06`. **The signal is predicted ~5×10⁴ below the
> threshold**, so **the registered rung-2 protocol REFUSES the wrong step and returns NOT EVALUABLE
> rather than a verdict.** That refusal *is* the discrimination this baseline is bought to
> demonstrate: the gate cannot be passed by a step that carries no signal.
> **P13 — and if the ratio is computed anyway, it is large. Band: `> 20%`** against P-A's patched
> analytic `7.90292883e-03`. Registered gray zone, stated so no outcome can be re-read favourably:
> a noise-dominated estimate is **random**, so a small percentage is possible by luck and would
> **not** be evidence that 1e-8 is a good step — the discriminating quantity is P12's delta-vs-floor,
> not P13's percentage. P13 is reported with its number and, on its own, carries no verdict.
> **THE FALSIFIER THAT WITHDRAWS ARM P-A'S VERDICT:** if the wrong step both **clears** the
> evaluability gate **and** returns ≤ 5%, then the gate is not measuring what it claims, and per
> Charter §4 **arm P-A's verdict is withdrawn**, not defended.
> **Second falsifier:** a primal failing to converge under the perturbation → the arm is NOT
> EVALUABLE, not a pass.
> **P14 — cost. Band: wall `60 – 200 s`, core-min `4.0 – 13.3`; peak RSS `< 3 GiB`** (no adjoint,
> no Jacobian assembly).

## 6. Outcome mapping, fixed before the run

| P8 / P9 outcome | what is written |
|---|---|
| `shape[115]` ≤ 5% **and** P9 in band | **PATCHED row: PASS.** Row 12's rung-2 cell moves PENDING → PASS, beside the SHIPPED-equivalent PASS, never replacing it (R11). The patch effect is quoted as the answer to §5.1: the rotation defect's contraction with A3's `dObj/dXv` is *this* size, against 97–99.5% on A1/A2/A5. |
| `shape[115]` 5–15% | **CONDITIONAL**, with the per-component breakdown, and the counter-instance carried at the headline per `FAMILY_SUPERVISION_GUIDELINES.md` §7. |
| `shape[115]` > 15% or any sign flip | **PATCHED row: GATE FAIL.** The first ladder row where the patch moves a gradient away from a fixed FD reference. Escalate before any regrade (§6 item 3 of the guidelines names the FD-gate percentages as headline numbers). |
| P3 or P4 falsifier fires | **NOT A RESULT.** The comparison is void; the numbers are reported as an image-identity finding, no gradient claim in either direction. |
| P10 falsifier fires | **NOT A RESULT — stopped by memory** (Charter §7). No conditioning claim, no cap raise. |
| P13 falsifier fires | **Arm P-A's verdict WITHDRAWN** (Charter §4). |
| launch condition (§7) never met | **BLOCKED on host contention, $0.00 spent.** Nothing staged is run. |

**Nothing in any branch moves the SHIPPED grade.** Row 10 of `LADDER_A_STATUS.md` stands as it is.

## 7. Mechanics, launch condition, and stop rules

* **Staged copy.** `/home/ubuntu/certonomous-runs/P3-a3-rung2-patched/{patched,wrongstep}/`, each a
  fresh copy carrying `0/ 0.orig/ FFD/ constant/ system/ dRdWColoring_4.bin{,.info}`, the scripts,
  and `log.checkMesh`; **no** `processor*`, `_bak_*`, `reports/`, `mphys.html` or `*.log` is copied.
  `A3-rung2-n28-tpc1` and the archived D3 member are **read-only** to this item — copied, never run
  in.
* **Cores.** `--cpus=4`. Max 4 cores, inside the 4-core lane cap and the 8-core team cap shared with
  two other lanes.
* **Memory.** `--memory=12g`, per P10.
* **Foreground, bounded.** `timeout 1050` on arm P-A, `timeout 300` on arm P-B. `1050 + 300 = 1350 s
  × 4 ranks / 60 = 90.0 core-min` — **the registered ceiling is reachable but not exceedable by
  construction.** No unbounded process is started; nothing is detached without a self-writing ledger.
* **RSS watcher, record-only.** A background loop sampling
  `sudo -n docker stats --no-stream --format '{{.MemUsage}}' <container>` every 5 s into
  `rss_<arm>.txt`, taking the first whitespace field (the usage side of `USAGE / LIMIT`). **The
  watcher records; it never kills.** Explicit `--format` is used in preference to a positional field
  index so the parse is unambiguous in the record.
* **Ledger.** One line per arm in `ledger.txt`: arm, image, image ID, `.so` md5, ranks, `t0`, `t1`,
  wall s, `core-min = wall × 4 / 60`, rc, peak RSS.
* **LAUNCH CONDITION, checked in a bounded polling loop immediately before each arm:** host
  **1-minute load average ≤ 8** and **`MemAvailable` ≥ 12 GiB**. Polled every 60 s for at most
  **100 minutes**. If the condition is not met inside that window, **no arm launches**, the item is
  recorded **BLOCKED on host contention with $0.00 of solver compute spent**, and the staged tree is
  left in place for a later window. At filing the box carries **12 `buoyantBoussinesqSimpleFoam`
  processes** (T-family) and a 1-minute load average of **21.8–32.4** on 16 cores, with
  `MemAvailable` 24.9 GiB — so this condition is **not** met at filing and is expected to be the
  binding constraint on this item.
* **Overrun rule.** A `timeout` expiry stops the run. The arm is reported at its measured cost with
  no number, and **no second budget is requested** for it.
* **Escalation.** Any outcome that moves one of the guidelines' §6 headline numbers — which includes
  the FD-gate percentages — is reported, not acted on. No regrade, no verdict move, no satellite
  edit is made by this item.

## 8. Cost, registered before the runs

**Measured basis** (not an estimate): the stock rung-2 arm B ran this exact task, on this exact
mesh, at np=4, in **452 s** wall — `.t0 1786374916`, `.t1 1786375368` in
`/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/`, `rc=0` — = **30.13 core-min**, and
`A3_RUNG2_N28_RESULT.md`'s own spend table records it as **30.1**. The patched arm is the same task
on the same mesh with the same coloring cache; the only difference is one shared library.

| arm | ranks | predicted wall | predicted core-min | band | $ @ $0.0513/core-hour |
|---|---|---|---|---|---|
| **P-A** PATCHED `fd3` | 4 | 452 s | **30.1** | 18.1 – 42.2 | $0.0258 |
| **P-B** trivial baseline, `fd1wrong` | 4 | ~100 s | **6.7** | 4.0 – 13.3 | $0.0057 |
| shipped twin | — | **not run** (§3 departure 1) | **0** | — | **$0.00** |
| fresh coloring pass | — | **not run** (§3 departure 2) | **0** | (would be +28.0) | **$0.00** |
| **predicted total** | | | **36.8** | 22.1 – 55.5 | **$0.0315** |
| **REGISTERED CEILING** | | | **90.0** | | **$0.0770** |

**Nothing here approaches $25.** The worst case this item can reach — both timeouts expiring in full
— is **90.0 core-min = $0.0770**, which is **0.31%** of the $25 bar at which an item is listed for
Sanaa instead of run (Charter §12). The predicted spend is $0.0315.

The estimate is registered here and **the miss is reported as a miss** in `RESULTS.md`, against this
table and not against a re-derived one.

## 9. What this item cannot see, stated in advance

1. **The full-vector aggregate.** Like the stock row, this arm verifies **three components** against
   FD, not a full `check_totals` vector norm over the whole DV set. P9 measures the patch effect
   across the full 120-component shape row, but **that row has no FD beside it** — it is
   analytic-vs-analytic. A5's `idx16` is the standing demonstration that a component nobody looked
   at can be the one that matters (`../grading_confirmation/RESULTS.md` §5.2).
2. **The decomposition axis.** np=4, `scotch`, one partition, on both arms — because an FD reference
   is never carried across np (Charter §5) and the stock row is np=4. A4's **16,600×** split between
   two decompositions of the same mesh is the reason this is a real limitation and not a formality.
   Nothing here says A3 rung 2 is decomposition-invariant.
3. **Regime 2 of the rotation defect.** `fd3` evaluates at the undeformed baseline and at ±1e-2 DV
   perturbations, where the `sqrt(eps)` guard fires and regime 1 dominates. The near-threshold
   ill-conditioned `acos` regime survives the patch **by design** (`BUILD.md` §7 limit 2) and is not
   probed here.
4. **The limiter lever and the DAFoam-side defects.** The patch does not touch DAFoam
   (`BUILD.md` §7 limit 3). A3's `fvSchemes` is unchanged and has no counterpart to A1's
   92.8% → 0.121% `limited`/`default` arm (`../grading_confirmation/RESULTS.md` §5.4).
5. **The literal shipped image at this rung.** The stock row cited is `dafoam-subpclu:v1` with the
   env unset — **SHIPPED-equivalent (‡), which is not the same thing as
   `dafoam/opt-packages:latest`**. §2 argues the numeric paths coincide and P3 tests it empirically,
   but **this item does not run `dafoam/opt-packages:latest` at rung 2 and does not close that
   gap.** The ‡ label stays on the stock row.
6. **The other rungs.** This buys rung 2 only. `LADDER_A_STATUS.md` rows 9 (rung 1, 21,840 cells) and
   11 (rung 3, 79,560 cells) keep **PENDING** in the PATCHED column, as does the original 399,360-cell
   campaign, which is BLOCKED for reasons this arm does not touch.
7. **The `CL` rows.** `fd3` computes totals for **CD only**. `dCL/d*` on the patched image at this
   rung is not measured by this item, on either image.
8. **Whether a converged adjoint licenses the gradient.** P3's `reason 2` is an identity check
   between two images, not evidence of a correct operator (L-35, L-36; Charter §1). The FD table is
   what grades the gradient, and it grades three components of it.

## 10. Standing statements

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.

**Two rows, never merged.** The SHIPPED-equivalent row is cited from
`../grading_confirmation/RESULTS.md` §2c and `A3_RUNG2_N28_RESULT.md`; the PATCHED row is measured
here. A patched grade never replaces a shipped grade — that requires the fix shipping upstream or
Sanaa formally adopting a forked toolchain, and it is her call, not a session's (R11,
`FAMILY_SUPERVISION_GUIDELINES.md` §3.4).

**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**

This item edits no frozen file, and edits none of `docs/LESSONS.md`, `docs/DOCKET.md`,
`docs/NUMERICS_KNOWLEDGE.md`, `cases/dafoam/INDEX.md`, `LADDER_A_STATUS.md` or any charter. Drafted
text for those is delivered to the supervisor, who owns the append.

---

# AMENDMENT 1 — 2026-08-22, PRE-COMPUTE: the arms move to np = 1 twins

**Version 1.1.** **Lines whose number changed above this section: 0.** This amendment is appended
at the foot with `cat >>`; the frozen body of §1–§10 is untouched and was verified byte-identical to
its committed blob `663c6aabf7cf012815d0f1a0fba684cb898610e5` immediately before this text was
written. Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.

## A1.0 This amendment is legal because no compute has been spent on any arm

CLAUDE.md rule 2 permits amendment **before first compute** and requires the condition and the check
to be stated, naming the run directory that does not exist. Stated:

* **No arm of this item has ever launched.** `/home/ubuntu/certonomous-runs/P3-a3-rung2-patched/`
  contains the staged trees `patched/` and `wrongstep/`, and
  `find … \( -name '*.log' -o -name 'processor*' \)` over both returns **nothing** but the copied-in
  `log.checkMesh`. **The files `P3-a3-rung2-patched/patched.log` and
  `P3-a3-rung2-patched/wrongstep.log` DO NOT EXIST**, no `processor*` directory exists in either
  tree, and no `decomposePar.log` exists.
* **The only compute this item has spent is 0.200 core-min** — a 3-second, 4-rank identity check
  with **no solver, no case and no mesh** (`ledger.txt` line 1, `note=identity-only-no-solver`). It
  started no OpenFOAM process and wrote nothing into any case directory.
* **No gate, threshold, band, cap or label from §4–§6 is loosened by this amendment.** The grading
  band, the evaluability and step-consistency gates, the verdict vocabulary, the two-row rule and the
  $25 rule are carried through unchanged. The registered ceiling **rises from 90.0 to 120.0
  core-min**, which is the ceiling the dispatching brief set for this item from the start and which
  §8 sat below; it is re-derived from measurement in A1.4, not from convenience.

## A1.1 The condition that forced it, and how it was checked

The §7 launch condition — 1-minute load average ≤ 8 **and** MemAvailable ≥ 12 GiB — **was polled 12
times and never met.** Poll log: `/home/ubuntu/certonomous-runs/P3-a3-rung2-patched/launch_condition.txt`.

| | |
|---|---|
| polls | **12**, 18:07:13Z → 18:18:14Z |
| **minimum `load1` observed** | **18.28** against a gate of 8 |
| range | 18.28 – 26.17 |
| MemAvailable | **20.96 – 23.57 GiB throughout — the memory limb never bound, on any poll** |

**The load limb cannot clear, and this is read from the owning team's own record rather than
assumed.** `docs/LAB_STATE.md` — which this lane does not edit — states at `:59-60` that lab-wide
live compute is *"12 single-core solvers, all `buoyantBoussinesqSimpleFoam`, all owned by
heat-transfer"*, and gives their ETAs at `:231-234`: three T1 runs at **~2026-08-26 06–08Z**, one
(`R_10k_x`, endTime 20000) at **~2026-08-23 01:40Z**; and at `:249` the T3 ext1 critical path `R_f`
at **2026-08-25T14:54Z**. Twelve single-core solvers on a 16-core box put `load1 ≥ 12` **by
construction**, so a gate of 8 is unreachable for the next three to four days. **The T-family has
priority and is not to be touched.**

**Why the gate is replaced rather than relaxed, and the distinction matters.** Choosing a gate after
seeing that it blocks you is the failure `DAFOAM_CHARTER.md` §8 names (*"a token chosen after the
number is not a verdict"*). This amendment does not lower the number; it **changes the
configuration** so that the resource the gate was proxying for is no longer contended. The old gate
was a proxy for *"are there 4 free cores for a 4-rank MPI job"*. The arms now take **one** core.

## A1.2 What changes: np = 4 → np = 1, and it moves the item toward the charter, not away

| | registered (frozen §2) | amended |
|---|---|---|
| ranks | 4 | **1** |
| container | `--cpus=4 --memory=12g` | **`--cpus=1 --memory=12g`** |
| `decomposePar` | `-force` before each arm | **not run** — at 1 rank pyDAFoam reads the serial case directly; no `processor*` directory is created or read |
| arms | PATCHED + control; shipped twin declined | **PATCHED np=1 + SHIPPED np=1 + control** — three arms |
| shipped image | not run (§3 departure 1) | **`dafoam/opt-packages:latest`**, `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663` |
| launch condition | load1 ≤ 8 **and** MemAvailable ≥ 12 GiB | **MemAvailable ≥ 12 GiB only** (A1.5) |
| ceiling | 90.0 core-min | **120.0 core-min** |

**Three consequences, and two of them are improvements the np=4 plan could not buy.**

1. **The shipped twin comes back, and it must.** `DAFOAM_CHARTER.md` §5 forbids carrying an FD
   reference across np: *"A gradient verified at one np is a statement about that np and is never
   carried to another."* The np=4 stock row (0.0077% / 0.2740% / 0.0172%) is therefore **a prior, not
   a comparator**, for anything measured at np=1. Without a shipped np=1 arm the patched np=1 arm
   would have **no valid stock comparator at all**, and the two things this item exists to measure —
   the FD-invariance control of §5 P4 and the patch effect of §5 P9 — would both be unmeasurable.
   §3 departure 1's reasoning was sound at np=4 and does not survive the move to np=1. **It is
   hereby withdrawn**: the raw arrays in the rung-2 stock logs are np=4 arrays.
2. **This closes the gap §9 item 5 admitted it could not close.** The frozen §9.5 records that the
   cited stock row is `dafoam-subpclu:v1` with the env unset — *"SHIPPED-equivalent (‡), which is not
   the same thing as `dafoam/opt-packages:latest`"*. The amended shipped arm runs **the literal
   shipped image**. The ‡ caveat does not apply to the new row.
3. **It is the configuration the charter asks for first.** `DAFOAM_CHARTER.md` §5: *"A new case's
   first FD verification is run at np = 1 before any parallel figure is graded."* **A3 has never been
   run at np=1 at any mesh size, on either image.** The np=4 rungs were graded without it.

**Everything else in §2 is unchanged**: mesh, birth certificate, `daOptions`, `transonicPCOption 1`,
`primalMinResTol 1e-8`, `pcFillLevel 0`, `gmresMaxIters 2000`, DV set, FD steps h=1e-2 / 2h=2e-2,
`runScript_fd3p.py` and its three-insertion diff, cold-start proof, `-x PYTHONPATH`, record-only RSS
watcher, per-arm ledger.

**One new departure, disclosed.** There is **no `dRdWColoring_1.bin`** on disk — the cached coloring
is `dRdWColoring_4.bin`, keyed to a 4-way partition and useless at 1 rank. **Arm N-P (first) computes
the coloring fresh and pays for it; arms N-S and N-C reuse the `dRdWColoring_1.bin` it writes**, by
copying that one file between staged trees. This is the same reuse the graded np=4 arms already
relied on (they inherited `dRdWColoring_4.bin` from a different run entirely, the D3 Option-5 run),
and it is legitimate across images because the coloring is computed by DAFoam from mesh connectivity
with **no IDWarp in the chain** — the two images carry identical DAFoam 5.0.0. **The check is
registered, not assumed:** both logs must print `Reading Coloring dRdWColoring_1` and the **same
colour count**, and that assertion is prediction **P18b**.

## A1.3 Predictions restated for np = 1. The np=4 numbers are a PRIOR, not a prediction

Numbering continues from §5. Bands are wider than §5's because **np=1 is a configuration this case
has never been run in**, and saying so is the point.

> **P15 — provenance, all three arms. Band: exact.** Arm N-P and arm N-C print
> `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425`; **arm N-S prints
> `f0fcb488e0e98156575cd19548e91663`** and `IDWARP_IMPORTED_FROM:` a site-packages path. All three:
> `transonicPCOption 1;` in the DAOption dump, **zero** sub-LU banners. At 1 rank the mixed-stack
> risk of `BUILD.md` §6 cannot arise, and the np=4 forwarding was already proved by the 0.200
> core-min pre-flight (all 4 ranks `85f59e87…`).
> **Falsifier:** wrong md5 on any arm → that arm is void and stops.

> **P16 — cold start. Band: agreement with `0.6833296303785072` to ≥ 10 significant figures, NOT to
> all 16.** The 16-digit signature is an **np=4** artifact: it is a sum over the same cells but in a
> different summation order, and serial-vs-4-way reduction order is not required to agree in the last
> digits. Registering the exact-match band here would be carrying an np=4 number across np, which is
> the very thing §5 of the charter forbids. `initRes ≈ 1` on all six fields is required exactly.
> **Falsifier:** disagreement in the first 10 significant figures → the copy warm-started; void.

> **P17 — the np=1 adjoint. Band: `PetscConvergedReason: 2`, iterations in `300 – 1400`.** Prior:
> **987** at np=4 on this mesh. At 1 rank the ASM preconditioner has a single block, i.e. plain
> ILU(0) on the whole matrix, which is normally better conditioned than a 4-block ASM — and the
> ladder has a measured instance: A6's N=16 rung at **41,760 cells converged in 517 iterations at
> np=1**, which `LADDER_A_STATUS.md` row 24 explicitly contrasts with *"A3 rung 2 needed 987 at the
> same size"* at np=4. So fewer is expected and the band is asymmetric downward.
> **Falsifier:** `reason -3` at the 2000 cap → np=1 conditioning is *worse* at this rung, which is a
> new finding and its own escalation; the arm yields no analytic and is **NOT SCORED**, not failed.

> **P18 — the two images give the same adjoint. Band: bit-identical.** Arms N-P and N-S must return
> the same iteration count, the same reason and the same printed residual path, because the IDWarp
> patch enters after the Krylov solve. This is now an identity check between **the literal shipped
> image and the patched image**, which is stronger than the frozen P3 (which compared
> `dafoam-subpclu:v1` against the patched image).
> **P18b — coloring reuse. Band: exact.** Both logs print `Reading Coloring dRdWColoring_1` and the
> **same colour count**; arm N-P's log additionally prints `Writing Colors to dRdWColoring_1`.
> **Falsifier (either):** a difference → the images do not share a numeric path, or the reused
> coloring is not the coloring the second arm would have computed; **stop and report**.

> **P19 — THE CONTROL: the FD column must not move between the two np=1 arms. Band: bit-identical,
> every printed digit** — both baselines, all 12 perturbed `CD` values, all 6 FD estimates, and the
> drift. This is the §5 P4 control, now measured at a **single, matched np**, which is the only way
> it is admissible.
> **Falsifier:** any digit differing → the arms measure different functions; **stop and report.**

> **P20 — selection. Band: `patchV[1]`, `twist[1]`, `shape[115]` on both arms**, as at np=4. **Named
> alternative:** a moved argmax at np=1 is a finding (decomposition changing which component is
> largest); the arm continues and the moved component is reported with its own numbers.

> **P21 — `patchV` bit-identical between the two images. Band: exact.** It does not cross
> `warpDeriv`. IG-2 evidence, **reported and not gated on**.

> **P22 — SHIPPED np=1, three per-component relative errors. Band: `patchV[1]` 0 – 1%, `twist[1]`
> 0 – 3%, `shape[115]` 0 – 3%; verdict predicted PASS, zero sign flips.** Prior at np=4: 0.0077% /
> 0.2740% / 0.0172%. Bands are wider than the prior because A4 measured a **16,600×** spread between
> two decompositions of one mesh, so np is not a free variable on this stack.

> **P23 — PATCHED np=1, same three. Band: same as P22; verdict predicted PASS, zero sign flips.**
> **Falsifier (both P22 and P23):** > 5% ⇒ CONDITIONAL; > 15% or any sign flip ⇒ GATE FAIL for that
> row, and — for the patched arm moving *away* from a fixed FD reference the shipped arm matches —
> escalation before any regrade.

> **P24 — the patch effect, analytic vs analytic, and it is now a cleaner measurement than the frozen
> P9 could have been. Band: `‖g_patched − g_stock‖₂ / ‖g_stock‖₂` over the full 120-component
> `CD wrt shape` row in `0.005% – 5%`.** The frozen P9 would have compared a patched `fd3` row at
> `primalMinResTol 1e-8` against a stock arm-A row at **1e-6** — two tolerances, a confound that
> would have had to be disclosed. Both np=1 arms run `fd3` at 1e-8, so **the only difference between
> the two vectors is the shared library.** Named alternative and the > 15% reading are carried
> forward from §5 P9 unchanged, as is the `< 0.001%` NOT A RESULT (resolution-limited) branch.

> **P25 — a free by-product, registered so it is not claimed as a discovery afterwards: A3's first
> decomposition datum, ever. Band: `‖g_np1 − g_np4‖₂ / ‖g_np4‖₂` on the stock `CD wrt shape` row in
> `0.001% – 20%`, reported with no gate on it.** `../grading_confirmation/RESULTS.md` §5.5 records
> that *"the decomposition axis was never varied on A3"*. Comparing arm N-S against the archived np=4
> stock row varies it for the first time. It is **not** a verdict — the two rows are different
> configurations — and it is reported as evidence with its band, in the A1/§5 "unregistered bonus"
> class.

> **P26 — memory at 1 rank. Band: peak RSS `6.5 – 11.5 GiB` against the `12 GiB` cap; host
> `MemAvailable` never below `8 GiB`.** Model, from this case's own family: `LADDER_A_STATUS.md`
> row 7's serial fit predicts **66.0 – 93.6 GiB at 399,360 cells**, i.e. **0.169 – 0.240 MiB/cell**,
> giving **6.95 – 9.87 GiB at 42,120 cells**. Cross-check: the np=4 **aggregate** record peak at this
> exact member is 9,991.9 MiB = **9.76 GiB**, and the reverse sweep builds a mesh-sized
> `d[R]/d[Xv]` block whether or not it is partitioned, so serial and 4-way aggregate should be close.
> **Falsifier / stop rule (Charter §7), unchanged from §5 P10:** OOM, a watcher sample > 11.5 GiB, or
> host `MemAvailable` < 8 GiB → **stopped by memory, NOT A RESULT about the patch, no cap raised, no
> new budget.**

> **P27 — the trivial baseline at np=1.** Design unchanged from §5 arm P-B: patched stack,
> `patchV[1]` only, step **1e-8**, no adjoint. Band: `|CD(+h) − CD(−h)|` in `1.0e-10 – 2.5e-10`,
> **four to five orders below the evaluability threshold**, so the rung's own gate returns **NOT
> EVALUABLE** rather than a verdict — which is the discrimination it is bought for. **Disclosure:
> the constant printed in the log line `FD1W evaluability threshold (10x drift 8.093e-07)` is the
> np=4 drift and is a hard-coded reference only; the threshold actually graded against is recomputed
> from arm N-P's OWN measured np=1 drift**, and both numbers are reported. P13's `> 20%` band, its
> registered gray zone (a noise-dominated estimate is random, so a small percentage is luck and is
> not evidence for 1e-8) and **the falsifier that withdraws the real arms' verdicts** all carry
> forward unchanged. Licence check for reusing arm N-P's analytic: arm N-C's baseline CD must equal
> arm N-P's **bit-identically**, else the control is NOT A RESULT rather than compared.

> **P28 — clock inflation, stated in advance and reported measured.** Predicted wall inflation np=4 →
> np=1 is **4.0× ideal, 4.0 – 5.0× with single-rank contention** on a box where the T-family holds 12
> cores and two other lanes each hold one. Core-minutes are predicted to be roughly **conserved**
> across the change, since core-min = cores × wall. The measured inflation is reported in
> `RESULTS.md` against this band whether it lands or misses.

## A1.4 Cost, re-derived from measurement before the runs

**Measured bases, both from this exact mesh at np=4:** the `fd3` task ran in **452 s** wall × 4 =
**30.13 core-min** with a warm coloring (`A3-rung2-n28-tpc1/.t0/.t1`); a **fresh** `dRdW` coloring
pass cost **460.02 − 39.44 = 420.6 s** wall × 4 = **28.0 core-min**
(`A3-onera-m6-sweep-n28_42120/run_opt5_onera_n28_42120.log:826,:885`). Core-minutes are conserved
under the rank change (P28); wall is not.

| arm | order | ranks | coloring | predicted wall | predicted core-min | `timeout` | worst case core-min |
|---|---|---|---|---|---|---|---|
| **N-P** PATCHED `fd3` | 1st | 1 | **computes it** | ~3,830 s | **63.8** | 4,200 s | 70.0 |
| **N-S** SHIPPED `fd3` | 2nd | 1 | reuses | ~1,990 s | **33.1** | 2,400 s | 40.0 |
| **N-C** control `fd1wrong` | 3rd | 1 | none | ~440 s | **7.3** | 540 s | 9.0 |
| pre-flight (already spent) | — | 4 | — | 3 s | **0.200** | — | 0.200 |
| **total** | | | | **~1 h 45 m sequential** | **104.4** | | **119.2** |
| **REGISTERED CEILING** | | | | | | | **120.0** |

Contention factor 1.1× is included in the predicted column. **The three timeouts sum to 119.2
core-min, so the ceiling is reachable but not exceedable by construction**, exactly as §7 built it at
np=4. At $0.0513/core-hour the ceiling is **$0.1026** and the prediction is **$0.0893**. **Nothing
here approaches $25** — the worst case is **0.41%** of that bar.

**Patched runs FIRST and that ordering is deliberate.** It is the row `LADDER_A_STATUS.md` row 12
actually needs, so if the budget stops the item after one arm, the item still delivers what it was
dispatched for rather than a stock row.

**Registered decision rule, so no budget escape is decided in the moment:** if arm N-P expires on its
`timeout`, **arms N-S and N-C are NOT launched**, the item reports what it has, and **no second
budget is requested** (`COMPUTE_BUDGET_CHARTER.md`: a budget overrun stops the run; it does not get a
new budget). If arm N-P succeeds but N-S expires, the control still runs and the patched row is
reported with the stock comparator recorded as **PENDING**, never as absent.

## A1.5 Launch condition, amended

**MemAvailable ≥ 12 GiB**, checked immediately before each arm, polled every 60 s for at most 100
minutes. **The load limb is removed**, and the rationale is registered rather than left implicit:

1. Each arm is **one rank in a `--cpus=1` container** — one core of sixteen, inside the 4-core lane
   cap and the 8-core team cap shared with two other lanes, both of which are currently holding one
   container each.
2. At `-np 1` there is **no MPI spin-wait**: the busy-wait progress engine that makes an oversubscribed
   multi-rank job pathological on a loaded box has no peer to poll.
3. Arms run **strictly sequentially** — never more than one container from this item at a time.

**The cost of removing it is stated rather than hidden:** the arms will run against a loaded box, so
**their wall clocks are contended and are not a clean cost basis for scaling** — the same disclosure
A1's `RESULTS.md` §6 had to make. The measured inflation is reported against P28.

## A1.6 What this amendment does NOT change

§4's bands and gates; §6's outcome mapping; §9's eight "cannot see" limits, **except** item 5, which
this amendment closes by running the literal shipped image, and item 2, which it partly addresses by
producing A3's first decomposition datum (P25) while still not making a decomposition claim; §10's
two-row rule, R11, and the standing statement that **nothing is filed, sent, uploaded or pushed, and
filing stays NOT APPROVED and is Sanaa's alone.**

**Verdict vocabulary unchanged:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
**Three rows, and the shipped and patched rows are never merged.**
