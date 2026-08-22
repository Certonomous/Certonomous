# A4 Ahmed body — the SHIPPED-image optimisation twin, np=1: PRE-REGISTRATION

**Filed 2026-08-22, Lane C (Opus), BEFORE any arm launched.** Predictions, bands, ceilings and
falsifiers are committed here first; `RESULTS.md` does not revise this file — departures are recorded
there as dated Amendments. **Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED
and is Sanaa's alone.**

Run root: `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/`.

---

## 1. The empty cell this item exists to fill

`../first_optimisation_np1/RESULTS.md` §5 closes with a two-row table that is empty on one side, and
says so in terms:

> **The shipped column at the optimised design is empty, and no claim is made about it.** … **So this
> item cannot say whether the rotation patch mattered to the optimisation**, in either direction. It
> would cost one more ~9.5 core-min arm to find out.

This item buys exactly that arm, and one more that is cheaper still. The state of the 2×3 table
before this item runs:

| configuration, np=1 | SHIPPED `dafoam/opt-packages:latest` | PATCHED `dafoam-idwarp-rot:v1` |
|---|---|---|
| gradient at the **undeformed baseline** | **PASS, 1.1032%** (`a4_np1_stock.log`, 2026-08-02) | **NOT MEASURED** per `../first_optimisation_np1/RESULTS.md` §5 — but see §2 below |
| **optimisation** (`run_driver`) | **NOT RUN** ← **ARM S** | **PASS**, 9 majors, `Optimal Solution Found.`, −7.478% |
| gradient at the **optimised design** | **NOT MEASURED** ← **ARM S** (in-process) | **PASS, 0.4936%** |

**The discriminating question, stated before the answer is known:** the rotation defect's *regime 1*
— the `sqrt(eps)` guard firing at a near-undeformed state — is what the patch removes, and it is
measured at the baseline. *Regime 2* — the near-threshold ill-conditioned branch — **survives the
patch by design** and acts at **deformed** designs, which is where every iterate of an optimisation
after the first lives. A1 and A5 both **FAIL shipped at the baseline** (11.43%, ~47%); **A4 shipped
passes at the baseline at 1.10%.** Nobody has yet measured a shipped gradient at a *deformed* design
point on any case. Arm S does that.

## 2. A finding made while reading, which changes one arm before it is bought

**The patched-baseline cell is not as empty as `../first_optimisation_np1/RESULTS.md` §5 records.**
`/home/ubuntu/certonomous-runs/W4-a4-stepsweep/a4_np1_patched.log` (2026-08-02, the W4 step-size
sweep) is an A4 np=1 `check_totals` on the **patched** stack and reads:

```
'scenario1.aero_post.functionals.CD' wrt 'dvs.shape'
   | 2.4150e-01 | 2.4232e-01 | 8.2218e-04 | 3.3929e-03
```

i.e. **0.33929%**, against the stock np=1 row's 1.1032% at a **bit-identical FD** (`2.4232e-01` in
both). And the patch that run used was bind-mounted from
`/home/ubuntu/certonomous-runs/W5-patch/idwarp`, whose `libidwarp.so` this item hashed today:

```
$ md5sum /home/ubuntu/certonomous-runs/W5-patch/idwarp/idwarp/libidwarp.so
85f59e87253e0a71a813f64ca6e4c425
```

**That is the same md5 the image ships** (`../../patched_build/idwarp_rot/BUILD.md` §2). So the
archival number is a measurement of the *same binary*, delivered by the *other* vehicle.

**Why that is not enough, and why a 3-core-min arm is registered anyway.** `BUILD.md` §1 exists
because *"a run that dropped the `-v` or the `export` would silently produce stock numbers under a
patched label"*, and §2 requires the identity to be proved by hashing the `.so` **from inside the
process that loaded it**. The 2026-08-02 run predates that discipline and **prints no
`IDWARP_SO_MD5`**. Its self-consistency argument is strong — a stock run would have printed the stock
`2.3965e-01`, and it printed `2.4150e-01` — but it is an inference, not a certificate.
**ARM B therefore re-measures the patched baseline on the image, with the md5 printed in-process.**
It is registered as a ≤3 core-min arm and is the "cheap `check_totals` at baseline" the task brief
conditioned on.

## 3. Arms as they will be launched

Both arms are `np=1`, no decomposition of any kind, `--cpus=4 --memory=8g`, `--rm`, foreground under
`timeout`, staged from a **pristine `base/` that has never been run in**
(`/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base`, copied from `P2-a4-opt/base`, verified today
to contain no `0.0001` and no `processor*`), with `sudo -n rm -rf processor*` before each launch and
a record-only RSS watcher that never kills anything.

| arm | image | `libidwarp.so` md5 asserted in the log | script | task | `timeout` |
|---|---|---|---|---|---|
| **S** | **`dafoam/opt-packages:latest`** | **`f0fcb488e0e98156575cd19548e91663`** (stock) | `opt_runScript.py`, md5 **`387a09b76d4774186be4b83a80f14e8a`** — **byte-identical to the patched arm's** | `run_driver` | 3000 s |
| **B** | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` (patched) | `baseline_runScript.py`, md5 `f11acac06391e0075faba3f2a9c2b2c3` — **one line** different (§3.1) | `check_totals` | 1800 s |

**Arm S is a single-variable A/B and nothing else.** Same base, same script md5, same command line,
same rank count, same container caps, same `-x PYTHONPATH`, same in-process endpoint `check_totals`.
**The only thing that differs from the 2026-08-21 patched run is the image**, and therefore the md5 of
the one shared library the patch touches. That is the strongest form the comparison can take, and it
is why the script is reused unedited rather than rewritten.

### 3.1 Arm B's one-line diff, stated so it cannot be mistaken for a different experiment

```
$ diff opt_runScript.py baseline_runScript.py
187c187
<         compact_print=True,
---
>         compact_print=False,
```
The line lives in the `-task check_totals` branch, which arm S never executes. It changes **printing
only** — `compact_print=False` emits the raw `Jfor`/`Jfd` arrays and the `Analytic Magnitude` /
`Fd Magnitude` block instead of a one-line table row. Step, form and `step_calc` are untouched:
`step=1e-3, form="central", step_calc="abs"`, the same instrument used at the patched endpoint and in
the 2026-08-02 archival rows.

### 3.2 The endpoint check runs in the same process, by prior registration

Arm S's endpoint `check_totals` is the `if True:` block at the end of `run_driver`, executing
immediately after `run_driver()` returns with the design vector already at **the shipped run's own
optimum**. This is `../first_optimisation_np1/PREREGISTRATION.md` §5's registered pattern, verbatim,
and it is the point of it: **no reload, no restart, no directory reuse** — the A2 failure mode.

**Note what this means and does not mean.** Arm S's endpoint check is taken at **arm S's** final
design, not at the patched run's. If the two optimisers stop at different points, the two endpoint
gradients are measured at different geometries. That is the correct comparison to make (each image
graded where its own optimiser stopped), and §6 registers a prediction on how far apart those two
points will be.

## 4. Trivial baseline — DECLINED BY NAME, with the reason

**Charter 2c's trivial baseline for this item is A4's `scaler=-1.0` sign-flipped-gradient control, and
it is declined because it already ran** — `../first_optimisation_np1/RESULTS.md` §4, on the patched
image, 2026-08-21: CD **rose 9.090%** and `shape` walked to the **opposite corner** `+0.04992374`,
verdict **NOT A RESULT (control behaved as designed)**.

**Why the patched run of that control covers the shipped arm.** The control grades the *driver*, not
the *derivative*: it asks whether the harness is capable of not descending. The driver is
pyOptSparse 2.10.1 + IPOPT 3.13.5, and `docs/dafoam/TOOLCHAIN_INVENTORY.md` §1 establishes that
**all three images carry identical Python-package versions and differ only in a C++/Fortran source
file and its rebuilt library**. The optimiser binary the shipped arm will drive is the same optimiser
binary that walked to the wrong corner yesterday. Re-buying it would cost ~3.7 core-min to
re-measure a component that is bit-identical across the two images.

**It is declined, not omitted, and the cost of declining is stated:** if the shipped arm descends,
this item leans on *yesterday's* control rather than its own. Should arm S produce a descent that
looks anomalous — a reduction outside the band of §6-P3, or a non-monotone objective column — the
control is **not** assumed to transfer and a shipped `scaler=-1.0` arm becomes mandatory before any
verdict is written.

**A second, free control is registered in its place** (§6-P5): the shipped run's baseline CD must
reproduce the patched run's `0.1529738469354696` **bit-for-bit**, because the patch is
derivative-only and `warpMesh` output is md5-identical patched vs unpatched
(`../../patched_build/idwarp_rot/BUILD.md` §3). It costs nothing, it is falsifiable, and it fails
loudly if anything other than the intended variable moved.

## 5. Grading band — the lab's, unchanged

`../../A_stepsize_study.md:91-93`, as applied in `../../A1/reverify_patched_idwarp_np1/RESULTS.md` §2:

* **PASS** ≤ 5% **with zero flagged components**
* **CONDITIONAL** 5–15%
* **FAIL** > 15% **or any flagged component** (a sign flip is a flagged component)

**Strict completion, registered explicitly.** The optimiser earns **PASS only on its own convergence
statement** — `EXIT: Optimal Solution Found.` with `Overall NLP error` below `tol 1e-6`. A stop on
`max_iter 15`, on the `timeout`, or on any external cap is **GATE REACHED / NOT A RESULT**, never
PASS, however good the objective looks at the point it stopped.

## 6. Predictions, with bands, filed before launch

> **P1 — the shipped optimiser converges.** `EXIT: Optimal Solution Found.` appears in
> `opt/opt_IPOPT.txt`, with `Overall NLP error` < 1e-6. **Confidence: high.**
> **Basis, and it is structural rather than optimistic:** the optimum is at an *active lower bound*.
> At an active bound, IPOPT's dual infeasibility is `∇f − z_L`, and `z_L` is a multiplier the solver
> is free to set; it does not require `∇f → 0`, and it does not require `∇f` to be *correct*. A
> gradient wrong by ~1% still certifies a bound. **This prediction is therefore weakly
> discriminating and is registered as such** — P4 is the one that discriminates.
> **FALSIFIER:** any exit other than `Optimal Solution Found.` ⇒ P1 MISS, and the arm is graded
> GATE REACHED / NOT A RESULT per §5, not PASS.

> **P2 — major iterations: 7–12, point estimate 9–10.** The patched run took **9**, of which five
> bought nothing but a KKT certificate (`../first_optimisation_np1/RESULTS.md` §2.1). A gradient
> perturbed by ~1% changes the early step lengths slightly and the barrier tail hardly at all.
> **HIT if the reported `Number of Iterations` lies in [7, 12]; MISS otherwise**, and a MISS above 12
> is more interesting than a MISS below 7 because it would mean the wrong gradient cost line searches.

> **P3 — the final CD is the same number, to ~5 significant figures.** `CD(shape)` is a property of
> the **primal**, and the primal is byte-identical across the two images (`BUILD.md` §3: `warpMesh`
> output md5-identical, max|diff| = 0.0). If both optimisers stop at the lower bound `shape ≈ −0.05`,
> they are evaluating the *same function at the same point*.
> **Registered band: final CD ∈ [0.14148, 0.14158]** (patched measured `0.1415349193489169`), i.e.
> **reduction 7.44–7.51%** (patched measured 7.4777%), and **final `shape` at the lower bound with
> |shape| ≤ 0.05 + 1e-6**.
> **FALSIFIERS.** (a) The objective **increases on an accepted step** ⇒ the shipped gradient is not a
> descent direction on this case and the whole arm fails regardless of its final number. (b) The DV
> bound is violated at the reported optimum (|shape| > 0.05 + 1e-6) ⇒ infeasible, **GATE FAIL**.
> (c) Final CD outside [0.14148, 0.14158] ⇒ P3 MISS; **below** 0.14148 would be the surprising
> direction and would mean the shipped run found a *better* point than the patched one, which on a
> one-dimensional bounded problem can only mean the two runs stopped at different `shape` values.

> ### **P4 — THE DISCRIMINATING PREDICTION: the shipped endpoint gradient PASSES, at 0.5–2.5%, point estimate ≈1.3%, zero sign flips.**
>
> This is the number the item is bought for, and the reasoning is laid out so a MISS is informative.
>
> **The arithmetic.** At the **baseline**, shipped analytic `2.3965e-01` and patched analytic
> `2.4150e-01` against a shared FD `2.4232e-01`. The regime-1 defect therefore costs the shipped
> analytic **1.85e-03**, i.e. **−0.77% of the value**, and it pushes the analytic *further below* the
> FD (both are already low). At the **patched endpoint**, analytic `0.21410121` against FD
> `0.21516329` = 0.4936%. If the shipped run's regime-1 offset at the endpoint is similar in relative
> size, shipped analytic ≈ `0.21410 × (1 − 0.0077)` ≈ **`0.21245`**, against the same FD ⇒
> **≈ 1.26%**. Registered band **[0.5%, 2.5%]** to carry the uncertainty in "similar in relative size".
>
> **Why a sign flip is close to impossible here, stated so the A1/A5 contrast is not mis-read.**
> A1 shipped FAILs at 11.43% **because of one component**, `idx6`, whose FD is `−1.05e-03` — a
> near-zero entry in an 8-component vector, which the defect flips to `+5.69e-03` (640%). A5's 47%
> has the same shape. **A4 has exactly ONE design variable and its derivative is `+0.214`** — three
> orders of magnitude away from zero relative to the defect's absolute perturbation
> (`~1.9e-03`). **The structural reason A4 shipped passes where A1 and A5 fail is not that A4's
> toolchain is healthier; it is that A4 has no near-zero component for the defect to flip.** That
> claim is registered here so that a PASS on arm S is reported as *"the defect had nowhere to bite on
> this DV"*, not as *"the rotation patch does not matter"*.
>
> **FALSIFIERS, and what each would mean.**
> (a) **> 15% or any sign flip ⇒ GATE FAIL**, and arm S's descent must be re-described as unverified
> at its own endpoint. It would also be the **first evidence that regime 2 amplifies regime 1 at
> deformed designs**, which is the mechanism nobody has yet observed, and it would make the rotation
> patch load-bearing for optimisation on this case.
> (b) **5–15% ⇒ CONDITIONAL**, same reading at lower amplitude.
> (c) **< 0.5% ⇒ P4 MISS in the benign direction** — the shipped endpoint would be *no worse* than the
> patched one, meaning regime 1 has effectively vanished at the deformed state, and the honest report
> is that the patch is immaterial to this optimisation.
> (d) **A result inside [0.5%, 2.5%] ⇒ P4 HIT**, and the verdict is **PASS with the explicit caveat**
> that a PASS on a one-DV problem does not transfer to the 8-, 96- or 105-DV cases.

> **P5 — free identity gate (the control registered in place of the declined trivial baseline).**
> `PHASE2_BASELINE_CD` in arm S equals **`0.1529738469354696`**, the patched run's value, to **all 16
> printed digits**. Basis: the patch is derivative-only; the primal and the forward warp are
> untouched.
> **FALSIFIER: any difference at all ⇒ STOP.** Something other than the registered variable moved
> between the two runs, the A/B is void, and no verdict is written until it is explained.

> **P6 — arm B reproduces the archival patched baseline.** Analytic **`2.4150e-01`**, FD
> **`2.4232e-01`**, relative error **0.33929% ± 0.05 pt**, zero sign flips ⇒ **PASS**; and the FD is
> **bit-identical** to `a4_np1_stock.log`'s `2.4232e-01`, which is the A1 §3 FD-invariance control
> applied to A4 for the first time.
> **FALSIFIERS.** (a) The log's `IDWARP_SO_MD5` is not `85f59e87253e0a71a813f64ca6e4c425` ⇒ the arm is
> void. (b) The relative error differs from 0.33929% by more than 0.05 pt ⇒ the 2026-08-02 archival
> row does **not** reproduce on the image, and §2's inference that the bind-mount and the image are
> the same stack is falsified for this case. (c) The FD moves ⇒ the patch is not derivative-only on
> this case, contradicting `BUILD.md` §3.

> **P7 — a free discriminator visible without any extra compute.** IPOPT's iteration-0 `inf_du` is
> the baseline dual infeasibility, which for this unconstrained-at-start 1-DV problem is the gradient
> magnitude. The patched run printed **`2.41e-01`** (matching its analytic `2.4150e-01` to the printed
> precision). **Predicted shipped iteration-0 `inf_du` = `2.40e-01`** (from `2.3965e-01`).
> **A HIT confirms, inside the optimiser's own log, that the two arms really did start from different
> gradients** — the single most direct evidence available that the image variable took effect.

## 7. Cost — registered from the measured basis, ceiling 40 core-min, hard

Core-minutes are `wall_s / 60 × ranks` with `ranks = 1`, the convention the P2 ledger used.

| arm | ranks | basis (measured, cited) | registered prediction | allowance |
|---|---|---|---|---|
| **S** — shipped `run_driver` + in-process endpoint `check_totals` | 1 | patched twin **567 s = 9.450 core-min** (`P2-a4-opt/ledger.txt`, 2026-08-21) | **8–13 core-min** | 20 |
| **B** — patched baseline `check_totals` | 1 | A4 coarse `check_totals` **33 s at np=4** (`../../A4_ahmed_body.md`, stage table); ≈4× wall at np=1 | **≤ 3 core-min** | 5 |
| **registered total** | | | **~12 core-min** | **25** |

**Hard ceiling: 40 core-min = 0.6667 core-hours = $0.0342** at $0.0513/core-hour. If the ceiling is
reached, no further arm is launched, the shortfall is reported, and the unlaunched cells stay
**NOT MEASURED**. Arm S is launched first; **arm B is the one dropped if the ceiling binds**, because
its cell already has an archival number (§2) while arm S's cells have nothing.

**A cost-measurement disclosure filed in advance.** The box is carrying another team's T-family
buoyant jobs (§8). Wall clocks measured under that load are **contended** and are **not** a clean
cost basis for scaling — the precedent is `../../A1/reverify_patched_idwarp_np1/RESULTS.md` §6. The
*derivative values are unaffected*: each arm is its own container with its own `--cpus=4` cap, np=1,
and a deterministic solver. Only the wall clock, and therefore the core-minute figure, is inflated.

## 8. Launch condition — a bounded loop, and the escalation registered in advance

**GATE: 1-minute load average ≤ 8 AND `MemAvailable` ≥ 8 GiB.** Implemented in
`/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/preflight.sh`: polls `/proc/loadavg` and
`/proc/meminfo` every **60 s** for at most **2400 s (40 min)**, appending every sample to
`preflight_history.txt`, and exits 0 (**gate open**) or 3 (**gate not met within the bound**).
`preflight.sh` is run as its **own** command, and its exit status is read, **before** any `docker run`
is issued.

**Why this clause is written at all.** `../first_optimisation_np1/RESULTS.md` Amendment 1 records
that yesterday's arm (c) launched at 1-minute load **16.51** because `uptime` and the launch were
issued in a *single shell command*, so the measured load could not gate anything — *"an operator
error, not a considered decision."* This item separates the check from the launch so that it can gate.

**Measured at the time of writing (2026-08-22 ~17:57Z), before any arm:** `load average: 31.08,
24.70, 14.98`; `MemAvailable 25.0 GiB`; 12 concurrent `buoyantBoussinesqSimpleFoam` processes (four
of them 19–20 h old) plus a `closure-venv` job at 321% CPU, on a 16-core box. **The gate is closed
now and may not open.**

**Registered escalation, so that no unregistered judgement call is made later.** If `preflight.sh`
exits 3, the arms are launched **only if all three of the following hold**, and the launch is
recorded as a dated Amendment in `RESULTS.md` with the `preflight_history.txt` sample series
attached:

1. `MemAvailable` ≥ 8 GiB at the moment of launch — **the memory floor is not escalatable**; the
   arm peaks at ~1.01 GiB against an 8 GiB container cap, and memory, unlike CPU, can kill it;
2. **no other DAFoam container is running** (`sudo -n docker ps` shows no `dafoam*` image), so the
   lane's 4 cores are contended only against non-DAFoam work and the team's 8-core cap is respected;
3. **every wall-clock-derived number in the cost table is marked CONTENDED** and is explicitly
   excluded from use as a cost basis for scaling.

If (1) or (2) fails, **no arm is launched**, and the item reports **GATE NOT REACHED — NOT A RESULT**
for the unlaunched arms with the load history as its evidence. **A cap-stop is never a PASS and never
a FAIL; it is an absence of measurement.**

**One further contention hazard, registered.** Arm S runs under `timeout 3000` (the brief's value)
against a 567 s uncontended basis. A ~5× contention slowdown would trip it. **A `timeout` kill is
NOT an optimiser result**: it is graded **NOT A RESULT (wall-clock cap)**, exactly like a `max_iter`
stop is graded GATE REACHED. **One re-launch is permitted** if and only if the kill was a `timeout`
(rc 124) and not a solver failure, and the re-launch is disclosed as an Amendment with its own
preflight sample.

## 9. What this item will not be able to see

1. **One design variable is not shape optimisation.** Every verdict here is about a single rear-slant
   break-line height. **It does not transfer to A1's 8, A2's 96 or A5's 105 shape DVs**, and P4's
   reasoning above explains precisely why the transfer fails: the defect's damage on those cases is
   concentrated in *near-zero* components, and this case has none.
2. **2,777 cells exist only to host a gradient.** No drag-accuracy claim and no Ahmed-body physics
   claim of any kind attaches to any CD in this item. The frozen record's 45,760-cell primal reads
   0.06998; the number here is 0.153 and the two are not comparable.
3. **`cellLimited Gauss linear 1` is live on this case's momentum equation and is not varied**
   (`../first_optimisation_np1/RESULTS.md` §1, read from `base/system/fvSchemes`). Defect **D-B2**
   reads **92.8% on A1 with the rotation patch already in place**. It could be acting on every number
   in this item, on *both* images equally, and this item cannot see it. **A PASS here is a PASS for
   this scheme configuration only.**
4. **Regime 2 is entered but not isolated.** Arm S's endpoint measurement cannot separate regime-2
   error from ordinary FD truncation or from mesh-quality degradation at a deformed state. It can
   only report the *difference* between two images at their own endpoints.
5. **The decomposition defect is absent by construction at np=1** — which is the reason np=1 was
   chosen for the patched twin and is retained unchanged here. Nothing here says anything about A4 at
   np > 1, where the shipped `scotch` default produces a gradient that is not the transpose Jacobian's
   solution at all.
6. **The two endpoint gradients are measured at two different geometries** (§3.2). If the two runs
   stop at different `shape` values, part of any difference between the two endpoint errors is the
   geometry difference, not the toolchain.
7. **`nlp_scaling_method: none` and IPOPT's own defaults are inherited unexamined** from the A2
   precedent, for comparability. No claim is made that they are optimal for this problem.

## 10. Verdict vocabulary

**PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING.** Shipped- and patched-toolchain
verdicts are reported as **separate rows**, never merged, and a cell with no measurement behind it
reads **NOT MEASURED**, never an assumption. An optimiser that stops on an iteration cap, a wall-clock
cap or any external cap is **GATE REACHED / NOT A RESULT**, never PASS.

**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**
