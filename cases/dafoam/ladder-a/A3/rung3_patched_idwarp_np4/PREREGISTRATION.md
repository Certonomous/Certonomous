# A3 ONERA M6, sweep rung 3 (79,560 cells) — the patched-IDWarp column at np=4: PRE-REGISTRATION

**Filed 2026-08-23, dafoam lane, BEFORE any arm of this item was launched and before any run
directory named in this file existed.** Predictions, acceptance bands, gates, caps and falsifiers
below are committed first; `RESULTS.md` is written afterwards and does not revise this file.
Departures discovered after this commit land as dated amendments appended at the foot, never by
editing the text above them. **Nothing is filed, sent, uploaded, posted or pushed. Filing stays
NOT APPROVED and is Sanaa's alone.**

**Companion item:** `../rung1_patched_idwarp_np4/PREREGISTRATION.md`, the same column at sweep
rung 1. The two are separate items with separate budgets, separate ceilings and separate commits.

---

## 1. Question, and the honest shape of it

`LADDER_A_STATUS.md:193` row **12b** reads **PENDING — NOT MEASURED** for *"A3 rungs 1, 3 and the
399,360 campaign"* in the PATCHED column. This item buys the **rung 3** cell, 79,560 cells, np = 4.

**Rung 3 is not a gradient question, and pretending otherwise would be the whole error.** The
shipped column at this rung reads **GATE FAIL** on the *adjoint*, not on a gradient
(`LADDER_A_STATUS.md:35`, row 11): the CD adjoint ran to its **4000-iteration cap**, returned
**`PetscConvergedReason: -3`**, and achieved a total residual reduction of **1.31×** —
`2.121343646203e-02 → 1.615245992220e-02` (`/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log:873,913`).
The FD stage was **correctly not launched**, being pre-registered as conditional on stage 1
converging, so the shipped column's FD cell at rung 3 is **NOT A RESULT**, not a number
(`../grading_confirmation/RESULTS.md:206-207`, `../../A3_RUNG3_N52_RESULT.md:82-83`).

And this is a **conditioning** wall rather than a memory one, which is what makes any verdict here
sayable at all: peak container usage was **11.65 GiB against a 22 GiB cap**, host `MemAvailable`
never below 17 GB, no swap growth, no OOM (`../../A3_RUNG3_N52_RESULT.md:50-53`). Under the family
rule a memory death is NOT EVALUABLE and never a conditioning verdict; memory was comfortable and
the solver still would not converge.

**So the question this item can actually answer is narrow, and it is stated narrowly:**

> **Does the patched toolchain inherit rung 3's conditioning wall unchanged?**

The mechanism says it must. The rotation patch touches two Tapenade-generated files,
`src/adjoint/output{Reverse,Forward}/vectorUtils_{b,d}.f90`, and *"the primal is untouched"* —
`warpMesh` output is md5-identical patched vs unpatched with max|diff| = 0.0
(`../../patched_build/idwarp_rot/BUILD.md` §3). That is the **mesh-warp derivative**, which enters
the chain **after** `Aᵀψ = −∂F/∂W` is solved. **The Krylov solve cannot see it.** Rung 2 measured
exactly that: **11 of 11** printed `(iteration, KSP residual)` pairs bit-identical between the two
images, `2.121211553380e-02` at iteration 0 through `2.119555554540e-06` at **987**
(`../rung2_patched_idwarp_np4/RESULTS.md:156-163`).

**This item is therefore bought to confirm a strong prediction cheaply, and to make the one outcome
that would overturn rung 2 visible immediately.** §6 registers all three branches; §4 registers, in
advance, exactly what a patched-arm conditioning failure would and would not mean; and §7 wires
every stop to a named script line, because a registered stop with nothing able to trigger it is not
a guard (L-239).

## 2. Case and configuration

| item | value | source, read at the line |
|---|---|---|
| archived case | `/home/ubuntu/certonomous-runs/A3-rung3-n52/` — **read-only to this item; copied, never run in** | `../../A3_RUNG3_N52_RESULT.md` |
| **run root (new, does not exist at filing)** | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/` — arm in `patched/` | this file |
| mesh | **79,560 cells**, pyHyp **N=52** layers on the 3×-coarsened M6 surface | `constant/birth_certificate.json`; per-processor counts in `decomposePar.log` sum to 79,560 |
| mesh certificate | verdict **clean**, `points_sha256` **`cf35cf1446830d880bded657d59dea0417c2dd3d01b238e1e37514ecd9432caa`**, max AR **608.2096897908551**, max non-orthogonality **61.49368843892955**, max skewness **2.279056246183647** | `A3-rung3-n52/constant/birth_certificate.json`; the hash convention (sha256 of `constant/polyMesh/points.gz`) was verified by this lane against rungs 2 and 3 before filing |
| solver | `DARhoSimpleCFoam`, **`primalMinResTol 1.0e-6`**, `primalMinResTolDiff` **unchanged at the default 100** | `A3-rung3-n52/runScript_rung3.py:69` and its comment at `:67` |
| adjoint | `transonicPCOption 1`, stock ILU(0) (`pcFillLevel 0`), `jacMatReOrdering natural`, `gmresRestart 200`, **`gmresMaxIters 4000`**, `DAFOAM_SUBPC_TYPE` **unset** | `runScript_rung3.py:103,105`; `A3-rung3-n52/lever_echo.txt` |
| **np / decomposition** | **np = 4**, `scotch`, 4 subdomains — matched to the shipped row | `A3-rung3-n52/decomposePar.log` |
| colouring cache | `dRdWColoring_4.bin`, md5 **`f91c25c1c6be0d9427d32b2ada482870`**, **1355 colours** — carried into the staged copy and READ, never rebuilt | archived case; `rung3_stage1.log:843,847` |
| container caps | **`--cpus=4 --memory=16g`**, `--rm`, foreground under `timeout`, `-x PYTHONPATH` | §3 departure 3, §7 |
| image, PATCHED arm | **`dafoam-idwarp-rot:v1`**, image ID `2927768a16ac`, `libidwarp.so` md5 **`85f59e87253e0a71a813f64ca6e4c425`** — **identity is the hash, never the version string** (`DAFOAM_CHARTER.md` §6) | `../../patched_build/idwarp_rot/BUILD.md` §2, §3 |
| shipped comparator | **not re-run** — cited from `A3-rung3-n52/rung3_stage1.log`, image `dafoam-subpclu:v1` with the env unset, i.e. **SHIPPED-equivalent ‡, not `dafoam/opt-packages:latest`** | §3 departure 1; `../grading_confirmation/RESULTS.md:94-96` |

### Why the shipped twin is not re-run here, when the rung-1 companion item does run it

Rung 1's companion buys a literal-shipped arm because **rung 1 has no full-row analytic dump on
disk** and because a patch-effect L2 there needs one. **Neither reason applies at rung 3, and the
reason it does not is the finding itself:** the shipped rung-3 arm **produced no gradient at all**.
There is no analytic vector to compare against, because the adjoint never converged. What the
shipped run *did* produce — the CD adjoint's printed residual path — is on disk at
`rung3_stage1.log:873-913`, at full printed precision, at matched np, matched image family, matched
colouring cache and matched configuration. **That is the entire comparator this item needs**, and
re-buying it would cost ~95 core-min to reproduce numbers already on disk.

**The ‡ caveat therefore stays on the comparator**, exactly as it did at rung 2
(`../rung2_patched_idwarp_np4/RESULTS.md:352-355`), and §9 item 4 carries it as a stated limit
rather than a closed one.

## 3. Departures, each disclosed with its reason

1. **The shipped image is not re-run (see above).** Declined by name, not omitted.
2. **The `dRdWColoring_4.bin` cache is carried into the staged copy and NOT deleted.**
   `../../FAMILY_SUPERVISION_GUIDELINES.md` §8 item 1: *"Partition and coloring caches stay
   untouched."* The cold-start hazard the staging rule exists for is a **field-state** hazard, closed
   by departure 4 and prediction **R3-P2**. Carrying the cache keeps the arm on the identical
   colouring the shipped row read. **GUARDED, not merely asserted:** `coloring_guard.sh:55` kills the
   arm on `Calculating dRdW Coloring` and `:63` kills it on a colour count other than **1355**.
3. **`--memory=16g`, not the shipped arm's 22g. This is a real departure and it carries a real
   registered risk.**
   * **Why it changes.** This box has **`MemTotal` 30.64 GiB** (`/proc/meminfo`, read 2026-08-23).
     A 22 GiB cap is **72% of the machine's entire RAM** and would leave 8.6 GiB for every co-tenant
     — the T-family's solvers and another lane's live DAFoam W4 container — **breaching this item's
     own 8 GiB neighbourliness floor by construction**. Registering a floor a cap makes unreachable
     is the L-239 failure in a different costume.
   * **Why 16g is defensible.** The shipped arm at this exact mesh, np and configuration measured a
     peak of **11.65 GiB** (`../../A3_RUNG3_N52_RESULT.md:50-51`), which sits inside 16 GiB with
     **27% headroom**.
   * **The risk, stated where the threshold is stated rather than in a footnote.**
     `A3-rung3-n52/lever_echo.txt` records a *"record peak 17603.8 MiB"* = **17.19 GiB** for the
     rung-3 **stage-0 baseline** configuration — **which exceeds a 16 GiB cap.** The two figures come
     from **different configurations** (the 11.65 GiB one is the measured peak of the arm this item
     reproduces; the 17.19 GiB one is a record for a different lever set) and this item does not
     claim to know which governs. **If the arm approaches it, `mem_guard.sh` stops it and the result
     is NOT A RESULT — stopped by memory, with no conditioning claim in either direction and no cap
     raise** (R3-P7).
4. **Cold start proved, not assumed.** The staged copy is made from the archived case with
   `processor*`, `reports/`, `mphys.html` and every `*.log` excluded. `diff -rq 0 0.orig` over the
   archived case was run before filing and returned **no differences** — the serial `0/` is
   byte-identical to `0.orig`. `decomposePar -force` runs inside the copy, and **R3-P2** asserts this
   mesh's cold-from-uniform signature. A guard refuses any staged tree in which a `processor*`
   directory or a non-`0` time directory already exists.
5. **`runScript_rung3.py` → `runScript_rung3p.py`, three insertions, all log-only or new-branch, all
   asserted by `diff` before launch and the `diff` pasted into `RESULTS.md`:**
   * **(D1)** a per-MPI-rank provenance stamp after the imports: rank, `idwarp.__file__`, the md5 of
     the adjacent `libidwarp.so`, and the `idwarp` version string. Log-only, before any numeric call.
     `BUILD.md` §6 warns Open MPI may not forward the parent environment to every rank, and a
     per-rank hash is the only thing that closes it — the version string reads `2.6.2` on **both**
     stacks and discriminates nothing (`BUILD.md` §2).
   * **(D2)** one added line, `log0(repr(totals))`, immediately after `compute_totals`. Log-only. It
     produces nothing in the predicted branch (no convergence ⇒ no totals) and is inserted **for the
     branch that is predicted not to occur**: if the patched adjoint converges, this is what makes
     the gradient readable at all.
   * **(D3)** a new **`ct_cd`** task branch computing totals for **CD only**. It touches no existing
     branch — the same discipline the rung-2 script's `fd1wrong` branch used.
6. **The `ct_cd` departure is retired by measurement, not by argument, and here is the measurement.**
   The shipped run used `-task compute_totals`, which solves **CD then CL**; this arm solves **CD
   only**. If that changed the CD solve, the identity claim would be confounded. **At rung 2, both
   forms were run on this exact case family, np, image and configuration, and their CD adjoints are
   bit-identical on all 11 printed checkpoints:** `A3-rung2-n28-tpc1/fd3_run.log:863-874` (CD-only,
   via `fd3`) against `A3-rung2-n28-tpc1/tpc1_computetotals_attempt2.log:862-872` (CD **and** CL) —
   `2.121211553380e-02` at iteration 0 through `2.119555554540e-06` at **987**, `reason 2`, with only
   the wall-clock stamps differing. **Requesting CL as well does not perturb the CD solve on this
   case.**
   * **Why the departure is taken at all:** it bounds the arm. `compute_totals` in the
     *converging* branch would pay for a CL solve this item does not need and has not budgeted, and
     the CD gradient is the ladder's standing FD class.
   * **Registered fallback if R3-P4's falsifier fires anyway:** the first hypothesis to test is
     **not** the patch but the departure, and the discriminator is named — re-run the **shipped**
     image at `ct_cd`, which isolates the task branch from the library. That discriminator is
     **not** launched by this item, is costed in §8, and needs a supervisor's go.
7. **`-x PYTHONPATH` is added to the `mpirun` line**, per `BUILD.md` §6.

Everything else — mesh, `constant/`, `system/`, `FFD/`, `daOptions`, `meshOptions`, DV set,
`decomposeParDict`, the colouring cache, ranks, and every numeric option in §2 — is byte-identical
to the archived shipped rung-3 arm.

## 4. What a patched-arm conditioning failure WOULD and WOULD NOT mean — registered in advance

**This is the section the item exists to write before the run, not after it.** The predicted outcome
is that the patched arm stagnates exactly as the shipped one did. Registered now, so no reading of
it can be chosen to fit the number:

### It WOULD mean

1. **The patched toolchain inherits rung 3's conditioning wall unchanged.** Adopting
   `dafoam-idwarp-rot:v1` buys nothing at rung 3 **and costs nothing at rung 3**. That is a direct,
   usable input to the toolchain-adoption question on Sanaa's desk: the patch is not a conditioning
   remedy, was never claimed to be one, and this measures that rather than assuming it.
2. **A second, independent confirmation that the patch enters strictly after the Krylov solve.**
   Rung 2 showed it on a **converging** solve (11/11 pairs, `reason 2`). Rung 3 would show it on a
   **stagnating** one, at a different mesh size and a different residual regime. Two regimes, one
   conclusion, is worth more than two instances of the same regime.
3. **The PATCHED column's rung-3 cell becomes `GATE FAIL — adjoint, inherited`**, graded on the
   *same instrument* as the shipped row's GATE FAIL: the terminal `PetscConvergedReason`, the
   iteration count and the total residual reduction. Row 12b's rung-3 cell moves
   **PENDING → GATE FAIL (adjoint)**. It does **not** move to any gradient verdict.

### It WOULD NOT mean

1. **It says NOTHING about the rotation patch's correctness.** The patch is downstream of the solve
   that failed; attributing the stagnation to it is a category error. `RESULTS.md` will state this
   at the headline, not in a limits section.
2. **It is NOT a gradient verdict of any kind.** No convergence ⇒ no analytic gradient ⇒ no FD table
   ⇒ per `DAFOAM_CHARTER.md` §2 there is nothing to grade. **The patched FD cell at rung 3 stays
   `NOT A RESULT`**, exactly as the shipped column's does — not `PASS`, not `FAIL`, and explicitly
   not "clean by omission".
3. **It does NOT extend rung 2's degradation finding to rung 3 in either direction.** Rung 2
   measured the patch making `shape[115]` **9.2084×** and `twist[1]` **3.39×** worse against a fixed
   FD reference (`../rung2_patched_idwarp_np4/RESULTS.md:169-171`, Correction 1). **Rung 3 is silent
   on whether the patch degrades gradients.** Only rungs 1 and 2 can speak to that, and the rung-1
   companion item is where that question is actually bought.
4. **It does NOT locate the ladder's conditioning ceiling.** The reopened ladder's ceiling is
   bracketed between 42,120 and 79,560 cells and **is not located**
   (`../grading_confirmation/RESULTS.md:262-265`). Nothing here narrows that bracket, and nothing
   here says the M6 adjoint is unreachable at 79,560 cells by any means.
5. **It is NOT a memory result.** If memory binds first, `mem_guard.sh` stops the arm and the outcome
   is **NOT A RESULT — stopped by memory**, with **no conditioning claim in either direction** — the
   family rule that made the *shipped* rung-3 verdict sayable
   (`../../A3_RUNG3_N52_RESULT.md:50-53`) cuts the same way here.
6. **It does NOT make the shipped rung-3 GATE FAIL any more or less true.** Per R11 a patched number
   never moves a shipped grade (`../../FAMILY_SUPERVISION_GUIDELINES.md` §3.4). Row 11 stands as it
   is.

### And the outcome that would overturn rung 2

If the patched CD residual path **differs** from the shipped one at any printed checkpoint **while
still stagnating**, then *"the patch enters after the Krylov solve"* is **falsified**, and rung 2's
two-image comparability argument — on which the whole rung-2 PASS rests — is in question. That is
an immediate **stop and escalate**, wired at `identity_stop.sh:98`, and no conditioning or gradient
claim is drawn from the arm in either direction.

## 5. Grading instrument, and the stage-2 gate

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING. No other
word grades an arm here.

**Stage R3-1 (this item) is graded on an adjoint gate, not an FD band.** Its instrument is exactly
the shipped row's: terminal `PetscConvergedReason`, iteration count, and total residual reduction,
with the pre-registered rung-2/rung-3 distinction between *a `-3` that is a budget* and *a `-3` that
is a wall* applied unchanged (`../grading_confirmation/RESULTS.md:191-199`):

| | a `-3` that is a budget | a `-3` that is a **wall** |
|---|---|---|
| total residual reduction | large, monotone (rung 2 CL: 1407×) | small (rung 3 CD: **1.31×**) |
| behaviour at the cap | still descending | **flat** |
| resolved by raising the cap? | yes | **no** — 3.79e−07 relative change over iterations 1300→4000 |

**Stage R3-2 (the FD arm) is CONDITIONAL and is NOT launched by this item.** Its gate is frozen here
so it cannot be chosen later: **it launches only if stage R3-1 returns `PetscConvergedReason: 2`**,
and then only on a supervisor's go, and then only under **its own pre-registration**. The reason it
needs its own pre-registration rather than an addendum here is stated plainly:

> **There is no FD plateau evidence at rung 3, of any kind, because no FD arm has ever run there.**
> `DAFOAM_CHARTER.md` §3 requires the step proved in the plateau by a sweep run at the graded run's
> primal tolerance and read **per component**. Rungs 1 and 2 both landed on **h = 1e-2 / 2h = 2e-2**
> from their own measured noise floors (rung 1 drift `1.626e-06`, rung 2 drift `8.093e-07`), and
> that is a **prior, not evidence at rung 3** — a floor is a property of the mesh and the primal's
> stopping behaviour, and rung 3 runs at `primalMinResTol 1e-6` where rungs 1 and 2 ran the FD arm
> at `1e-8`. **Carrying rungs 1–2's step to rung 3 unmeasured would be exactly the "selecting the
> step after seeing which one agrees" that §3 forbids.**
>
> **Registered design for stage R3-2, so it is not invented after the fact:** measure this rung's
> own repeat-baseline drift first; then a **three-point** per-component read at
> **h ∈ {5e-3, 1e-2, 2e-2}** rather than the two-point step-consistency check rungs 1 and 2 used —
> because at rung 3 there is no archived FD column whose bit-identity must be preserved, so the
> reason that forbade a third step at rung 1 (`../rung1_patched_idwarp_np4/PREREGISTRATION.md` §5)
> does not apply. Components that do not stabilise are **flagged by name and excluded**, never
> rescued. **Estimated cost ~60–70 core-min**, cited as the figure the shipped rung-3 item itself
> carried (`../../A3_RUNG3_N52_RESULT.md:82-83`) and **marked an estimate, not a measurement.**

## 6. Arm and predictions, with bands

One solver arm. It runs strictly alone; never more than one container from this item at a time.

### Arm R3-A — PATCHED, stage 1

`dafoam-idwarp-rot:v1`, np=4, `runScript_rung3p.py -task ct_cd`, `--cpus=4 --memory=16g`,
`timeout 2600`.

> **R3-P1 — provenance and activity proofs. Band: exact, all five limbs.**
> **(a)** every one of the 4 ranks prints `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425` and an
> `IDWARP_IMPORTED_FROM:` path under the patched package; **(b)** the DAOption dump contains
> `transonicPCOption 1;`; **(c)** **zero** occurrences of
> `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU`; **(d)** the **solver's** header reads
> `nProcs : 4` and 4 `processor*` directories are created — *not the `decomposePar` utility's own
> `nProcs : 1` header, which appears earlier and would make this limb say the opposite of what it
> says* (`../rung2_patched_idwarp_np4/RESULTS.md:66-68`); **(e)** the `idwarp` version string reads
> `2.6.2`, recorded as the demonstration that it **discriminates nothing**, never as a check.
> **Falsifier:** any rank reporting `f0fcb488…`, a missing or `2;` `transonicPCOption` line, or a
> sub-LU banner → **the arm is void and stops.** A run without its stamp does not count.

> **R3-P2 — cold start. Band: exact to all 16 digits.** The first
> `Time step continuity errors : sum local` printed is **`1.018123970654079`**, this mesh's np=4
> cold-from-uniform signature (`A3-rung3-n52/rung3_stage1.log:631`), with `initRes ≈ 1` on all six
> fields.
> **Falsifier:** any other value → the copy warm-started; the arm is void and stops.
> *Registered caveat, learned at rung 2: this signature is **np-specific** and is asserted exactly
> here only because the arm runs at the matched np=4 (`../rung2_patched_idwarp_np4/RESULTS.md:264-269`,
> P16 scored MISS).*

> **R3-P3 — the colouring is READ, not rebuilt. Band: exact, and it is WIRED.** The log prints
> `Checking if Coloring file exists..`, `dRdWColoring_4.bin exists.`, `Reading Coloring
> dRdWColoring_4`, `Validating Coloring...` and `dRdWTPC: 0 of 1355`, with **zero** occurrences of
> `Calculating dRdW Coloring`. Cache md5 **`f91c25c1c6be0d9427d32b2ada482870`**, asserted before
> launch. *A rebuild also prints a `Reading Coloring` line afterwards, so the discriminator is the
> **presence** of `Calculating`, never the absence of `Reading`.*
> **Stop rule, and what executes it:** `coloring_guard.sh:55` `docker kill`s the arm on a rebuild
> (exit 3), `:63` kills it on a colour count other than 1355 (exit 5); the kill is `:38`. Fired ⇒
> the arm's warm-cache cost basis is void, the arm is **NOT A RESULT**, no second budget is taken.

> **R3-P4 — THE IDENTITY, and it is the measurement this item is bought for. Band: bit-identical on
> all 11 printed checkpoints, iterations 0 through 1000.** The patched CD adjoint prints, digit for
> digit, the shipped path at `A3-rung3-n52/rung3_stage1.log:873-883`, frozen alongside this file in
> `shipped_cd_checkpoints.txt`:
> `0 → 2.121343646203e-02`, `100 → 1.758648818311e-02`, `200 → 1.618871466028e-02`,
> `300 → 1.618861640231e-02`, `400 → 1.615428564220e-02`, `500 → 1.615395949809e-02`,
> `600 → 1.615266903444e-02`, `700 → 1.615266448650e-02`, `800 → 1.615249844486e-02`,
> `900 → 1.615249565219e-02`, `1000 → 1.615247229756e-02`.
> **Why exact and not a band:** the patch is downstream of the Krylov solve (§1), and rung 2
> measured this identity 11/11 on a converging solve.
> **Why iteration 1000 and not 4000, said as a cost decision and not smuggled in:** the shipped
> residual is already flat from iteration 200 and its full 1.31× reduction is reached by iteration
> 1000; the remaining 3000 iterations reproduce a known stagnation at **~69% of the arm's wall**
> (shipped `ExecutionTime` 435.44 s at iteration 1000 against 1416.00 s at 4000, `:883,:913`).
> **The stop is DELIBERATE and is NOT a measurement failure** — `DAFOAM_CHARTER.md` §7: a stop is
> not a measurement. **The identity finding rests on the 11 matched checkpoints, which are complete
> before the stop fires, and NOT on the stop.**
> **WIRED:** `identity_stop.sh` compares each printed checkpoint against the frozen file as a
> **string**, and on a full match through iteration 1000 kills the container and exits 5
> (`identity_stop.sh:114-115`).

> **R3-P5 — the named alternative that must survive its own guard: the patched adjoint CONVERGES.
> Band: `PetscConvergedReason: 2` at any iteration count.** Registered as **not predicted** —
> mechanistically it would require the patch to affect a solve it is downstream of — but it is the
> largest result this arm could produce, and **a guard that killed it would be the worst possible
> failure of this design.** `identity_stop.sh:79-83` therefore **stands down** whenever a checkpoint
> residual falls below the registered converging threshold **1.0e-03** — three decades below the
> shipped plateau of `1.6152e-02` and far above the `1e-4` relative target of ~`2.12e-06`, so no
> stagnating path can reach it and no converging path can miss it. `:119-121` also stands down on a
> printed `PetscConvergedReason: 2`.
> **Disposition if it fires:** **stop reporting and escalate before anything else.** Stage R3-2
> becomes reachable, under its own pre-registration (§5), and **not** under this one.

> **R3-P6 — the falsifier that would overturn rung 2: the path DIFFERS while still stagnating.
> Band: any printed checkpoint differing from the frozen value while remaining ≥ 1.0e-03.**
> **Disposition, fixed now:** `identity_stop.sh:85-96` writes `PATH_DIVERGED`, `:98` kills the arm
> and exits 6. *"The patch enters strictly after the Krylov solve"* is **falsified at rung 3**, rung
> 2's two-image comparability argument is in question, and this is **STOP AND ESCALATE** with **no
> conditioning or gradient claim in either direction**.
> **The first hypothesis to test is the `ct_cd` departure, not the patch** — §3 departure 6 names
> the discriminator (re-run the *shipped* image at `ct_cd`), costs it in §8, and requires a
> supervisor's go. *That the departure is unlikely to be the cause is itself measured, not assumed:
> at rung 2 the CD-only and CD+CL forms produced bit-identical CD adjoints on 11/11 checkpoints.*

> **R3-P7 — memory. Band: container aggregate peak RSS `9.0 – 14.0 GiB` against a `16 GiB` cap;
> host `MemAvailable` never below `8 GiB`.** Basis: **11.65 GiB measured** at this exact mesh, np
> and configuration (`../../A3_RUNG3_N52_RESULT.md:50-51`); the band is widened downward because this
> arm is stopped at iteration 1000 and may not reach the shipped run's peak, and upward toward the
> disclosed 17.19 GiB stage-0 record (§3 departure 3) without reaching it.
> **Stop rule, and what executes it — this is the L-239 repair.** Rung 2 registered this exact
> host floor with a **record-only** watcher, drove host `MemAvailable` to **5.85 GiB** for **82 of
> 156 samples**, and **no stop fired** (`../rung2_patched_idwarp_np4/RESULTS.md` §9.1; L-239).
> Here: **`mem_guard.sh` polls the container's own RSS and `/proc/meminfo` MemAvailable every 5 s
> (`:79` and `:80` are the two threshold tests), requires 3 consecutive breaching samples (`:25`,
> `:85`), then `sudo -n docker kill`s at `:98` and exits 4 (`:100`)**, writing
> `MEMORY_STOP_FIRED.<arm>`. Thresholds passed by `drive.sh`: **RSS ceiling 15.0 GiB, host floor
> 8.0 GiB.** A `docker stats` parse failure is a **refusal**, not a silent pass (`:73`) — the guard
> will not run blind.
> **Disposition if it fires:** **NOT A RESULT — stopped by memory.** No conditioning, gradient or
> patch claim in any direction; **the cap is NOT raised and no new budget is taken**
> (`COMPUTE_BUDGET_CHARTER.md`). This is the same rule that made the shipped rung-3 verdict sayable.

> **R3-P8 — wall and cost. Band: wall `445 – 1157 s`, core-min `29.7 – 77.1`; point estimate
> `757 s` / `50.5 core-min`**, in the predicted identity-confirmed branch. See §8. The box is
> shared; contention is disclosed in `RESULTS.md` either way and a contended wall is **not** offered
> as a clean cost basis for scaling.

### The trivial baseline (`VERIFICATION_CHARTER.md` §2c / `DAFOAM_CHARTER.md` §4)

**This arm's claim is a NEGATIVE one** — *"the patched residual path is indistinguishable from the
shipped one"* — and `DAFOAM_CHARTER.md` §4 fixes the trivial baseline for an **FD gate**, which
this stage is not. The right control for an identity claim is not another solve; it is a
**planted-difference control on the comparator**, and CLAUDE.md rule 3 is explicit about why: *"a
zero from a reader not shown able to see a non-zero is not evidence."*

> **R3-P9 — the comparator is proved able to SEE a difference, at ZERO solver cost, before the arm
> runs. Band: exit 5 / 6 / 7 on three planted inputs.** `guard_selftest.sh` limbs 6, 7 and 8:
> * **limb 6** (`:110`) runs `identity_stop.sh` against **the real shipped rung-3 log** and requires
>   **exit 5, identity confirmed** — which also proves the comparator parses genuine DAFoam output,
>   not only planted text;
> * **limb 7** (`:125`) plants **A3 rung 2's real CD adjoint path**
>   (`A3-rung2-n28-tpc1/fd3_run.log:863-864`) — a genuine path from the same solver and case family
>   that differs from rung 3's **in the 5th significant figure at iteration 0**
>   (`2.121211553380e-02` vs `2.121343646203e-02`) — and requires **exit 6, DIVERGED**. *A comparator
>   that cannot see this cannot certify a match.*
> * **limb 8** (`:141`) plants a path matching at iteration 0 then dropping below the converging
>   threshold, and requires the guard to **stand down and not kill** (exit 7).
> **Disclosure:** this lane exercised limbs 6, 7 and 8 at filing, against the real shipped log and
> the two planted paths, and observed exit codes **5, 6 and 7** as designed, plus the three
> file-only `coloring_guard.sh` limbs at **3, 0 and 5**. **That exercise is NOT the licence.**
> `guard_selftest.sh` must pass **in the launching session**, because the kill path depends on live
> `docker` and `sudo -n` state that a test on another day does not certify, and because
> `GUARD_SELFTEST_PASS` must be newer than the guard files it names.
> **A solver-side negative control at rung 3 — the `transonicPCOption 2` arm that reproduces double
> `reason -5` — is DECLINED BY NAME**, not omitted: it costs real compute at this rung for a
> discrimination the ladder already owns at rung 1, where the control reproduced the 2026-07-30
> record **bit-for-bit** including the terminal denormal (`../grading_confirmation/RESULTS.md:107-117`).

## 7. Mechanics, launch condition, and stop rules

* **Staged copy.** `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/patched/`, carrying
  `0/ 0.orig/ FFD/ constant/ system/ dRdWColoring_4.bin{,.info}` and the scripts; **no**
  `processor*`, `reports/`, `mphys.html` or `*.log` is copied. The archived case is **read-only**.
* **Staging asserts, all before any launch:** `sha256(constant/polyMesh/points.gz)` equals
  `cf35cf14…` and matches `constant/birth_certificate.json`, whose verdict reads **clean**;
  `md5(dRdWColoring_4.bin)` equals `f91c25c1c6be0d9427d32b2ada482870`; `diff -rq 0 0.orig` is empty;
  no `processor*` and no non-`0` time directory exists; `diff runScript_rung3.py
  runScript_rung3p.py` shows only D1, D2, D3. Any failure ⇒ **BLOCKED**, nothing launches.
* **Cores.** `--cpus=4`, inside the 4-core lane cap and the 8-core team cap.
* **Memory.** `--memory=16g`, per §3 departure 3 and R3-P7.
* **Foreground, bounded.** `timeout 2600`. `2600 × 4 / 60 = 173.333 core-min` — **the registered
  ceiling is reachable but not exceedable by construction.** No unbounded process is started;
  nothing is detached without a self-writing ledger.
* **GUARDS — every registered stop names what polls it and what performs the stop (L-239).**

  | threshold / condition | polled by | fired by | on fire |
  |---|---|---|---|
  | 11 checkpoints bit-identical through iteration **1000** | `identity_stop.sh` loop, 5 s | `:114` `docker kill` (via `:56`), exit 5 at `:115` | **DELIBERATE STOP, identity CONFIRMED.** Not a measurement failure; the finding is complete before the stop |
  | any checkpoint differs **and** residual ≥ **1.0e-03** | `identity_stop.sh:85` | `:98` kill, exit 6 | **STOP AND ESCALATE.** Rung 2's comparability argument is in question. No claim in either direction |
  | any checkpoint differs **and** residual < **1.0e-03** | `identity_stop.sh:79` | **nothing — the guard STANDS DOWN** | the patched adjoint is converging; **it must not be killed by its own guard** |
  | `PetscConvergedReason: 2` printed | `identity_stop.sh:119` | stands down, exit 0 | R3-P5; escalate before anything else |
  | checkpoints file missing | `identity_stop.sh:48` | refusal, exit 2 | comparator has no reference ⇒ **BLOCKED** |
  | own RSS > **15.0 GiB**, 3 consecutive 5 s samples | `mem_guard.sh:79` | `:98` kill, exit 4 at `:100` | **NOT A RESULT — stopped by memory**; cap NOT raised |
  | host `MemAvailable` < **8.0 GiB**, 3 consecutive 5 s samples | `mem_guard.sh:80` | `:98` kill, exit 4 | same |
  | `docker stats` unparseable | `mem_guard.sh:73` | refusal, exit 2 | must not run blind ⇒ **BLOCKED** |
  | `Calculating dRdW Coloring` present | `coloring_guard.sh` loop | `:55` (exit 3) via `:38` | warm-cache basis **VOID**, arm **NOT A RESULT** |
  | colour count ≠ **1355** | `coloring_guard.sh` | `:63` (exit 5) via `:38` | not the same colouring, arm **NOT A RESULT** |
  | guards not proved able to fire, **in this session** | `guard_selftest.sh` limbs 1–8 | writes `GUARD_SELFTEST_PASS` at `:165` only on a clean sweep; exits 1 at `:170` otherwise | **`drive.sh` refuses to launch the arm** ⇒ **BLOCKED** |
  | wall > `timeout` 2600 s | `timeout(1)` | SIGTERM, rc 124 | arm stopped at its measured cost with no number; **no second budget** |

  **The selftest is what makes the rest of this table true rather than decorative**, and its
  identity limbs are the planted-difference control of R3-P9. `GUARD_SELFTEST_PASS` must be **newer
  than every guard file it names** — `mem_guard.sh`, `coloring_guard.sh`, `identity_stop.sh` and
  `shipped_cd_checkpoints.txt`, whose md5s it records (`guard_selftest.sh:159-162`) — so editing a
  guard invalidates its own licence to run.
* **LAUNCH CONDITION, checked in a bounded polling loop immediately before the arm:**
  **`free_cores ≥ 4` AND `MemAvailable ≥ 16 GiB`**, with
  ```
  busy       = median over 5 samples taken 2 s apart of ( `ps -eo state= | grep -c '^R'` − 1 )
  free_cores = nproc − busy                                    ( nproc = 16 )
  ```
  Polled every 60 s for at most **240 polls (4 h)**. The memory limb is **16 GiB here, not 12**,
  matched to this arm's larger cap. This is the gate Amendment 2 of the rung-2 item derived and
  which opened in 9 polls where `load1 ≤ 8` had failed in 12
  (`../rung2_patched_idwarp_np4/RESULTS.md:75-92`); the load-average limb is **not** used, because it
  never measured the resource a `--cpus=4` container consumes.
  **Reading at filing, 2026-08-23:** `MemTotal` **30.64 GiB**, `MemAvailable` **26.10 GiB**,
  `load1` 7.83, runnable threads **9** ⇒ `free_cores ≈ 7` — the gate is **open at filing**. Live
  compute at filing: 4 `buoyantBoussinesqSimpleFoam` (T-family), 1 `simpleFoam`, and **a live
  4-rank DAFoam W4 run in container `w4m1m2_m2` on `dafoam-subpclu:v1`** — **another lane's, not
  touched.** The W4 container is precisely why the poll is retained rather than skipped: it may
  finish, or a successor may start, between filing and launch, and **the gate decides, not this
  reading.**
  If the condition is not met inside the window, **no arm launches**, the item is recorded
  **BLOCKED on host contention with $0.00 of solver compute spent**, and the staged tree is left for
  a later window.
* **RSS trace.** `mem_guard.sh` writes every sample to `rss_patched.txt` — the same trace rung 2's
  record-only watcher produced, now written by the process that can also act on it.
* **Ledger.** One line in `ledger.txt`: arm, image, image ID, `.so` md5, ranks, `t0`, `t1`, wall s,
  `core-min = wall × 4 / 60`, rc, peak RSS, and every guard's exit code.
* **Registered decision rule, so no budget escape is decided in the moment:** if arm R3-A expires on
  its `timeout`, the item reports what it has — the checkpoints matched so far, named — and **no
  second budget is requested** (`COMPUTE_BUDGET_CHARTER.md`: an overrun stops the run; it does not
  get a new budget). Neither the `ct_cd` discriminator of §3 departure 6 nor stage R3-2 is launched
  by this item under any branch.
* **Escalation.** Any outcome that moves one of the guidelines' §6 headline numbers is reported, not
  acted on. No regrade, no verdict move, no board edit and no satellite edit is made by this item.

## 8. Cost, registered before the run

**Measured basis, not an estimate.** The shipped rung-3 stage-1 arm ran this exact mesh, np,
configuration and colouring cache in **1426 s** wall — `.t0 1786376709`, `.t1 1786378135`, `.rc 1`
in `/home/ubuntu/certonomous-runs/A3-rung3-n52/` — = **95.067 core-min**, and
`../../A3_RUNG3_N52_RESULT.md:25` records it as **95.07**.

**How the early-stop wall is derived, arithmetically and from the same log.** The shipped run's
adjoint `ExecutionTime` reads **151.36 s at iteration 0**, **435.44 s at iteration 1000** and
**1416.00 s at iteration 4000** (`rung3_stage1.log:873,883,913`). The wall this arm needs to reach
the identity stop is therefore `1426 − (1416.00 − 435.44)` = **445 s** on an idle box.

**How this item scales, said plainly.** It does **not** scale by cell count. Rung 3 has its own
task-matched, np-matched, warm-cache measured wall, so the only quantity carried across from another
rung is the **contention inflation factor** — taken from rung 2's measurement on **this** box (arm
P-A ran **955 s** against a **452 s** idle basis, **2.11×**,
`../rung2_patched_idwarp_np4/RESULTS.md:292`) and widened to **1.0× – 2.6×**, point **1.7×**. The
upper end is 2.6× and not 2.1× for a stated reason: **rung 2's own inflation band was 1.0–2.1× and
was scored a MISS by 5 s of wall** (`RESULTS.md:260-262`); a band that only just fails to contain
the last measurement is not a band.

| item | ranks | predicted wall | predicted core-min | band | `timeout` | worst-case core-min | $ @ $0.0513/core-h |
|---|---|---|---|---|---|---|---|
| **R3-A** PATCHED stage 1, `ct_cd`, identity stop at iteration 1000 | 4 | 757 s | **50.5** | 29.7 – 77.1 | 2600 s | 173.333 | $0.0432 |
| guard selftest (2 `alpine` containers + 6 file-only limbs) | 1 | ~110 s | **1.8** | 0.5 – 2.0 | — | 2.000 | $0.0015 |
| per-rank provenance pre-flight (no solver, no case) | 4 | 3 s | **0.200** | — | — | 0.200 | $0.0002 |
| launch-condition polling | — | — | **0.000** | — | 4 h | 0.000 | $0.00 |
| shipped twin re-run | — | **not run — declined by name, §2** | **0** | — | — | 0 | **$0.00** |
| fresh colouring pass | — | **not run — cache carried, §3 departure 2** | **0** | — | — | 0 | **$0.00** |
| `ct_cd` discriminator (§3 departure 6) | — | **not run — conditional on R3-P6 firing, supervisor's go** | **0** | (would be ~50) | — | 0 | **$0.00** |
| **stage R3-2, the FD arm** | — | **not run — conditional on R3-P5, needs its own pre-registration (§5)** | **0** | (**estimated** 60–70) | — | 0 | **$0.00** |
| **predicted total** | | | **52.5** | 32.0 – 79.1 | | | **$0.0449** |
| **worst case by construction** | | | | | | **175.533** | $0.1501 |
| **REGISTERED CEILING** | | | | | | **176.0** | **$0.1505** |

**`cost_basis`: c7a.4xlarge at $0.0513/core-hour, owner-stated 2026-08-21/22 and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure here is REPORTED-BY-OWNER, NOT MEASURED.
The core-minute figures are measured or derived from measurement as stated above; the dollars are
not.**

**Why the ceiling is 176.0 when the prediction is 52.5, said rather than left to look like slack.**
The `timeout` must cover the branch this item predicts **will not** occur: a patched adjoint that
actually converges (R3-P5), where the guard correctly stands down and the solve runs on. Sizing that
branch from the shipped log's own rate — a converging CD at, say, ~2500 iterations would reach
`ExecutionTime ≈ 941 s`, so ~950 s idle, ~2470 s at 2.6× — gives the 2600 s cap. **That sizing is
an ESTIMATE and is marked one**; the 445 s figure is arithmetic from measured `ExecutionTime`
stamps. **173 core-min ($0.148) of headroom is cheap insurance against missing the largest result
this arm could produce**, and in the predicted branch it is never spent.

**HARD STOP: total item spend must stay ≤ 176.0 core-min.** The single timeout plus the two bounded
pre-flights make the worst case **175.533** by construction. **Nothing here approaches $25** — the
worst case is **0.60%** of the bar at which an item is listed for Sanaa instead of run. An overrun
**stops the run; it does not get a new budget.** The estimate is registered here and **the miss is
reported as a miss** in `RESULTS.md`, against this table and not against a re-derived one.

## 9. What this item cannot see, stated in advance

1. **Any gradient at all, in the predicted branch.** No convergence ⇒ no analytic vector ⇒ no FD
   table ⇒ nothing to grade (`DAFOAM_CHARTER.md` §2). The patched FD cell at rung 3 stays **NOT A
   RESULT**. **This item measures an inherited conditioning wall and nothing else** (§4).
2. **Whether the patch degrades gradients at rung 3.** Untestable here for the reason in item 1.
   Rung 2 measured degradation; the rung-1 companion tests whether that direction holds; **rung 3 is
   silent on it and will say so.**
3. **Where the ladder's conditioning ceiling actually is.** It stays bracketed between 42,120 and
   79,560 cells and unlocated (`../grading_confirmation/RESULTS.md:262-265`). Nothing here narrows
   the bracket, and nothing here says the M6 adjoint is unreachable at this size by any means — only
   that the configuration working at two rungs stagnates at this one with memory to spare.
4. **The literal shipped image at this rung.** The comparator is `dafoam-subpclu:v1` with the env
   unset — **SHIPPED-equivalent ‡, not `dafoam/opt-packages:latest`** — and this item does not close
   that gap, exactly as rung 2 did not (`../rung2_patched_idwarp_np4/RESULTS.md:352-355`). The ‡
   label stays on the comparator row.
5. **The decomposition axis.** np=4, `scotch`, one partition. A4's **16,600×** split between two
   decompositions of one mesh is why this matters, and **A3 still has no decomposition datum** —
   rung 2's np=1 attempt was stopped before it produced a gradient. `DAFOAM_CHARTER.md` §5's *"serial
   before parallel"* remains unsatisfied on A3.
6. **Regime 2 of the rotation defect.** The near-threshold ill-conditioned `acos` regime survives the
   patch **by design** (`BUILD.md` §7 limit 2) and is not probed here — and in the predicted branch
   the warp derivative is never reached at all.
7. **The `CL` rows.** `ct_cd` computes totals for CD only, and the shipped run never reached CL
   either — DAFoam raised `AnalysisError("Adjoint solution failed!")` after CD
   (`../grading_confirmation/RESULTS.md:186`). `dCL/d*` at rung 3 is unmeasured on every image.
8. **The 399,360-cell campaign.** BLOCKED for reasons this item does not touch; it keeps **PENDING**
   in the PATCHED column, as does row 12b's third cell.
9. **Whether the identity, if confirmed, generalises.** Two rungs of one case in two residual
   regimes is stronger than one, and is still two rungs of one case.

## 10. Standing statements

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.

**Two rows, never merged.** The SHIPPED-equivalent ‡ row is cited from
`../grading_confirmation/RESULTS.md` §2d and `A3-rung3-n52/rung3_stage1.log`; the PATCHED row is
measured here. **A patched grade never replaces a shipped grade** — that requires the fix shipping
upstream or Sanaa formally adopting a forked toolchain, and it is her call, not a session's (R11,
`../../FAMILY_SUPERVISION_GUIDELINES.md` §3.4). Row 11 stands as it is.

**Toolchain identity is an image ID and a library hash, never a version string**
(`DAFOAM_CHARTER.md` §6). `idwarp` reports `2.6.2` on both stacks.

**A stop is not a measurement** (`DAFOAM_CHARTER.md` §7). The deliberate stop of R3-P4 carries no
claim of its own; the identity finding rests on the matched checkpoints.

**Nothing is filed, sent, uploaded, posted, registered or pushed. Filing stays NOT APPROVED and is
Sanaa's alone.**

This item edits no frozen file, and edits none of `docs/LAB_STATE.md`, `docs/LESSONS.md`,
`docs/DOCKET.md`, `docs/NUMERICS_KNOWLEDGE.md`, `cases/dafoam/INDEX.md`, `LADDER_A_STATUS.md` or any
charter. Drafted text for those is delivered to the supervisor, who owns the append.

## 11. Frozen-file manifest

The grading path is fixed at this commit and is verified before launch by hashing each file against
its committed blob (CLAUDE.md rule 2). The five files frozen by this pre-registration are:

| file | role |
|---|---|
| `PREREGISTRATION.md` (this file) | gates, thresholds, bands, caps, labels |
| `shipped_cd_checkpoints.txt` | **the comparator's reference data** — the shipped CD residual path, transcribed from `rung3_stage1.log:873-883` |
| `identity_stop.sh` | the wired identity stop, its escalation branch and its stand-down branch (R3-P4, R3-P5, R3-P6) |
| `mem_guard.sh` | the wired memory stop (R3-P7) |
| `coloring_guard.sh` | the wired colouring-cache stop (R3-P3) |
| `guard_selftest.sh` | the proof that all three guards can fire, the planted-difference control (R3-P9), and the launch licence |

`mem_guard.sh` and `coloring_guard.sh` are **duplicated from the rung-1 item rather than shared**,
and that is deliberate: each item's grading path must be a file frozen at **its own**
pre-registration commit and hashable against **its own** blob; a shared script could be edited by
the other item between the two freezes. Their bodies are byte-identical to the rung-1 copies below
their header comments — verified by `diff` before filing — so the duplication is auditable rather
than a fork.

**No run directory named in this file exists at the time of this commit.**
`/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/` was checked and does not exist, and neither
does `patched/` beneath it.

## 12. The exact launch sequence a phase-2 lane runs

Registered so the launch is executed rather than re-designed, and so `RESULTS.md` can be checked
against what was supposed to happen. **Nothing below is run by this item.**

```
# 0. freeze check — every file that runs must BE the committed blob
cd /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4
for f in PREREGISTRATION.md shipped_cd_checkpoints.txt identity_stop.sh \
         mem_guard.sh coloring_guard.sh guard_selftest.sh; do
  git cat-file blob HEAD:cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4/$f | cmp - $f || exit 1
done

# 1. stage, with every §7 assert. Refuses on any mismatch.
./stage.sh            # asserts points.gz sha256 cf35cf14... against birth_certificate.json,
                      # cache md5 f91c25c1..., diff -rq 0 0.orig, no processor*, and the
                      # runScript_rung3 -> runScript_rung3p diff (D1, D2, D3 only)

# 2. prove all three guards can fire — IN THIS SESSION, BEFORE any solver starts.
#    Limbs 6-8 are the planted-difference control: the comparator must MATCH the real shipped log,
#    must SEE rung 2's real path as different, and must STAND DOWN on a converging path.
./guard_selftest.sh /home/ubuntu/certonomous-runs/P4-a3-rung3-patched "$PWD"
test -f /home/ubuntu/certonomous-runs/P4-a3-rung3-patched/GUARD_SELFTEST_PASS || exit 1

# 3. per-rank provenance pre-flight: 4 ranks, no solver, no case, ~3 s
sudo -n docker run --rm --cpus=4 dafoam-idwarp-rot:v1 bash -lc \
  'source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 4 -x PYTHONPATH \
   python -c "import idwarp,hashlib,os;p=os.path.dirname(idwarp.__file__); \
   print(idwarp.__file__, hashlib.md5(open(os.path.join(p,\"../libidwarp.so\"),\"rb\").read()).hexdigest())"'

# 4. the arm. Guards armed BEFORE the container starts; gate polled immediately before it.
./drive.sh            # preconditions: GUARD_SELFTEST_PASS exists and is newer than mem_guard.sh,
                      #   coloring_guard.sh, identity_stop.sh and shipped_cd_checkpoints.txt;
                      #   free_cores >= 4; MemAvailable >= 16 GiB
                      # arms:  mem_guard.sh      p3_a3r3_patched 15.0 8.0 <root> patched
                      #        coloring_guard.sh p3_a3r3_patched <log> dRdWColoring_4 1355 <root> patched
                      #        identity_stop.sh  p3_a3r3_patched <log> shipped_cd_checkpoints.txt \
                      #                          1.0e-03 <root> patched
                      # then: timeout 2600 docker run --rm --name p3_a3r3_patched --cpus=4 \
                      #        --memory=16g ... dafoam-idwarp-rot:v1 \
                      #        'decomposePar -force && mpirun -np 4 -x PYTHONPATH \
                      #         python runScript_rung3p.py -task ct_cd'
                      # decision rule: rc=124 -> report what matched, NO second budget, and neither
                      #   the ct_cd discriminator nor stage R3-2 is launched under any branch
```

`stage.sh` and `drive.sh` are written by the phase-2 lane **after** this file is committed, are
committed **before** they run, and may change no gate, threshold, band, cap or label in this
document.
