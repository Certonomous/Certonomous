# A6 CRM wing-alone, rung N=16 (41,760 cells), np=1: RESULTS

**Run 2026-08-21, Lane A (second holder of the lane; the first was stopped mid-run).**
Pre-registration: `PREREGISTRATION.md` in this directory, committed **before** any arm launched.
**This file does not revise it.** Departures from it are recorded in §10 (Amendments), dated, and
never by editing the frozen file. Nothing filed, sent or registered anywhere.

**HEADLINE — the rung bought what it was for, and then failed for a reason nobody registered.**

1. **The first A6 adjoint that has ever existed converged.** 517 GMRES iterations,
   `PetscConvergedReason: 2`, monotone descent over six decades. P3 predicted 400–1,500. **HIT.**
2. **Every FD-vs-adjoint row GATE FAILS, and the FD is why.** The registered predictions P4
   (`CD/twist` ≤5%, `CD/patchV` ≤1%) are **MISSED by more than an order of magnitude**.
   The cause is measured, not conjectured: **A6's primal never converges**, its CD carries a
   peak-to-peak wobble of **9.0e-6** over the last 200 iterations, and **eight of the nine graded
   components need the FD to resolve a ΔCD smaller than that.** The one component whose signal
   clears the noise floor — `patchV` idx1 (AoA) — is **the only one that agrees**, at 3.29%.
3. **The rung therefore cannot answer the question it was built to ask.** P4's R1-vs-R2
   discrimination needs a trustworthy FD reference on a warp-crossing DV. It does not have one.
   What it *can* still compare is the **analytic** column across images (§6), and that comparison is
   reported — but it grades the patch, not the gradient.

Raw logs: `/home/ubuntu/certonomous-runs/P2-a6-n16/{stock,patched,wrongstep}.log`, attempt-1 logs
`*_attempt1_gatefail.log`, interrupted attempt-2 log `stock_attempt2_interrupted.log`.
Ledger: `.../ledger.txt` and `.../ledger_attempt1_gatefail.txt`.

---

## 1. The case as built — both registered diffs, confirmed

Prereg §2 registered **exactly two edits** to the archived `A6-crm-wing/` recipe. Both verified by
`diff` after the fact:

```
$ diff A6-crm-wing/preProcessing.sh P2-a6-n16/base/preProcessing.sh
20a21
> cgns_utils coarsen surfMesh.cgns   # SECOND pass: A6-2b rung

$ diff A6-crm-wing/genWingMesh.py P2-a6-n16/base/genWingMesh.py
18c18
<     "N": 53,
---
>     "N": 16,
```

**Two edits, no more.** Measured mesh: `base/logMeshGeneration.txt:437` → `Mesh region0 size: 41760`,
exactly the `2,784 × 15` the prior pre-registration predicted. Patches from
`base/constant/polyMesh/boundary`: `wing` **2,784**, `inout` **2,784**, `sym` **1,020**. All as registered.

**`fvSchemes` audit (prereg §7.5), from disk.** A6 carries **NO `cellLimited` scheme anywhere**:
`gradSchemes { default Gauss linear; }` (unlimited) and `div(phi,U) Gauss linearUpwindV grad(U)`.
The serial-limiter defect D-B2 — which reads 92.8% on A1 with the rotation patch already in place —
**cannot act on this rung**, because the scheme that triggers it is not installed. No `limited`/
`default` arm was run, as registered.

## 2. Arms as executed

| arm | image | `IDWARP_SO_MD5` (printed by the run itself) | np | FD step | rc | wall |
|---|---|---|---|---|---|---|
| attempt 1, all three | both | correct on all three | 1 | 1e-3 / 1e-8 | **1** | 67–68 s |
| 1 SHIPPED | `dafoam/opt-packages:latest` | `f0fcb488e0e98156575cd19548e91663` (**stock**) | 1 | 1e-3 | 0 | 1676 s |
| 2 PATCHED | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` (**patched**) | 1 | 1e-3 | — | — |
| 3 TRIVIAL BASELINE | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` (**patched**) | 1 | **1e-8** | — | — |

**Activity proof, mandatory per prereg §3.** Every arm's `DAFoam option dictionary:` dump reads
`transonicPCOption 1;` — recorded in the ledger for attempt 1 and for every attempt-2 arm. No arm is
void on this ground. Every arm printed `nProcs : 1`; no arm is void on the decomposition ground.

## 3. Attempt 1 — recorded GATE FAIL, with the cause, which is NOT the cause on record

Attempt 1 (16:46–16:48Z) is a **GATE FAIL in its own right and is not overwritten**.
`ledger_attempt1_gatefail.txt` records `rc=1` on **all three** arms at 67–68 s
(1.117 + 1.133 + 1.133 = **3.383 core-min**).

**Cause, established from the DAFoam source rather than inferred.** All three died with
`openmdao.core.analysis_error.AnalysisError: … Primal solution failed!`
(`stock_attempt1_gatefail.log:782`). The primal had **completed all 1,000 iterations normally** and
produced a stable CD; the failure is a *post-hoc acceptance gate*, at
`DASolver::checkPrimalFailure()`, `src/adjoint/DASolver/DASolver.C:2744-2752`:

```
scalar tolMax = daOptionPtr_->getOption<scalar>("primalMinResTolDiff");
if (daGlobalVarPtr_->primalMaxRes / primalMinResTol_ > tolMax) { … return 1; }
```

| arm | `primalMaxRes` (log:716 / :714) | `primalMinResTol` | ratio | default `primalMinResTolDiff` | gate |
|---|---|---|---|---|---|
| stock | `5.55618061200622e-06` | 1e-8 | **555.6** | 1e2 | **FAIL** |
| patched | `5.908769514219209e-06` | 1e-8 | **590.9** | 1e2 | **FAIL** |
| wrongstep | `5.908769514219209e-06` | 1e-8 | **590.9** | 1e2 | **FAIL** |

**This is P2 coming true and killing the run.** P2 predicted the primal would *not* reach 1e-8. It
did not. What the prereg did not anticipate is that DAFoam converts "did not reach tolerance" into a
hard `AnalysisError` that aborts `check_totals` **before any adjoint is attempted**.

### 3.1 A correction to the record, entered because two frozen documents state otherwise

`A4/first_optimisation_np1/PREREGISTRATION.md` §5 (frozen, filed 16:49Z) attributes this death to
warm-start contamination, and states that *"a sibling arm staged from the pristine base ran cleanly
with a bit-identical cold-start continuity error."* The team briefing repeats it.

**That attribution is wrong, and the ledger on disk shows it: no arm ran cleanly. All three returned
`rc=1`, including the two cold ones.** The measured facts separate cleanly:

* **The contamination was real.** The calibration primal ran **inside the stock arm's own directory**
  (`calib_primal.log:9` → `Case   : /mnt/stock`), and stock attempt 1 duly started warm: its
  cumulative continuity error reads **−0.02855096739182514** against
  **−0.005045133651340859 bit-identical on `patched` and `wrongstep`**, which were staged cold. It
  also shifted the physics: warm CD `0.03505167364477857` vs cold `0.03506349413916734`.
* **The contamination did not kill anything.** Both cold arms failed too, on the same gate, at a
  ratio of 590.9 against a cap of 100.

Both statements matter. The warm-start house rule
(`../../WARMSTART_AUDIT.md`) is sound and was correctly applied thereafter; but it was not the
killer here, and a record that says it was would send the next lane after the wrong defect.
**Decontamination was still necessary and was performed** — see §10, Amendment 1.

## 4. P2 — the primal. GATE REACHED, as registered.

> Registered: *"the primal does NOT reach `primalMinResTol = 1e-8` and runs the full 1,000
> iterations, with CD/CL stable to ≥4 significant figures over the last 200."*
> *"Verdict language: GATE REACHED, not PASS."*

**Measured (arm 1 baseline primal, `stock.log:525-711`):** ran all 1,000 iterations; the string
`satisfied the prescribed tolerance` appears **zero** times; `primalMaxRes` = 5.556e-06, i.e.
**556× short of 1e-8**. The registered falsifier (the tolerance line printing) did **not** fire.

| t | CD | CL |
|---|---|---|
| 800 | `0.03505666073433948` | `0.4574290331652591` |
| 900 | `0.03505448562063092` | `0.4574268977152481` |
| 1000 | `0.03506349413916734` | `0.457426809939543` |

**CD peak-to-peak over the last 200 iterations: `9.00e-6` (0.026% of CD). CL: `2.2e-6` (4.8e-6
relative).** CD is stable to 4 significant figures and no further; CL to 6. **P2 HOLDS. Verdict:
GATE REACHED, not PASS.**

**That 9.00e-6 is not a footnote. It is the number that decides §5**, and it was measured from the
baseline primal of the graded arm itself, not imported.

## 5. P3 — the adjoint. The first A6 adjoint in existence, and it converged.

> Registered: *"both CD and CL adjoint solves return `PetscConvergedReason: 2`, with the CD solve in
> 400–1,500 iterations."*

**Measured (`stock.log:806-811`):**

```
Solving Linear Equation... 240.31 s
Main iteration   0 KSP Residual norm 1.491191599810e-02   263.24 s.
Main iteration 100 KSP Residual norm 6.398849288372e-03   ...
Main iteration 200 KSP Residual norm 5.602554317047e-04   384.51 s.
Main iteration 300 KSP Residual norm 3.091539918894e-05   454.13 s.
Main iteration 400 KSP Residual norm 1.862398366562e-06   530.24 s.
Main iteration 500 KSP Residual norm 2.817906320224e-08   612.09 s.
Main iteration 517 KSP Residual norm 1.441888699105e-08   627.19 s
**Completed**! Total iterations: 517. PetscConvergedReason: 2.
```

**517 iterations, reason 2, monotone descent over six decades.** Inside the registered 400–1,500
band. Neither falsifier fired: no negative reason, no `-3` at the 2,000 cap.

For scale: A3 rung 2, at 42,120 cells — 0.9% different in size, same solver, same
`transonicPCOption 1` — took **987**. A6 at 41,760 took **517**, i.e. **1.9× fewer**. The A3-derived
expectation transferred across geometry at fixed size, and transferred favourably.

**One registered prediction is NOT EVALUABLE, by construction, and it is the prereg's own doing.**
P3 predicts *"both CD and CL adjoint solves return reason 2"*, but prereg §3's second registered
edit restricts `check_totals` to `of=["CD"]`. **Only one adjoint is solved. The CL half of P3 was
unanswerable the moment §3 was written.** Recorded as an internal inconsistency in the frozen
pre-registration, not as a result and not as a miss by the solver.

**P1 — peak RSS.** **[SUPERSEDED — the figure in this paragraph is wrong; see §6.6 for the corrected
measurement of 9.787 GiB and the arithmetic behind the correction. Original text preserved below
unaltered.]** Predicted ≈6.8 GiB, hard ceiling 12 GiB. **Measured peak on arm 1: 7.396 GiB**
(computed independently — see §10, Amendment 3, for why the inherited script's own figure reads
`unmeasured`). **8.8% above the prediction, 38% below the ceiling. The 12 GiB falsifier did not
fire.** This is the **first CRM-specific adjoint memory measurement that has ever existed**; per
prereg §7.1 it is one point and **does not re-fit the scaling law** that keeps full size BLOCKED.

---

*Sections 6 onward written 2026-08-21 ~19:00Z by Lane A (third holder of the lane; the second was
lost to a session limit at 18:20Z while arm 2 was still running detached). Nothing above this line
was deleted or rewritten; the one edit made to §5 is an inserted pointer, marked as such, and the
original sentence is preserved verbatim beside it. Both graded arms had already completed on disk
(17:46Z and 18:32Z) before this lane started; **no arm was re-run to produce this section.***

## 6. P4 — FD vs adjoint. THE FULL TABLE, BOTH IMAGES, EVERY COMPONENT.

The prereg reports only two vector-norm numbers per arm. Those are the 36% and 89% that were visible
from the ledger. **The per-component table below is the actual result**, reconstructed from the raw
`Jfor`/`Jfd` arrays that `compact_print=False` dumped in full.

**Source lines.** Stock: `/home/ubuntu/certonomous-runs/P2-a6-n16/stock.log:4996-5007` (`patchV`),
`:5009-5022` (`twist`). Patched: `/home/ubuntu/certonomous-runs/P2-a6-n16/patched.log:4995-5006`
(`patchV`), `:5008-5021` (`twist`). Both arms: `of='scenario1.aero_post.functionals.CD'`,
`fd:central`, `step=1e-3`, `step_calc=abs`, 9 DVs, 19 primal solves.

### 6.1 The table

`FD` is a **single column** because it is **bit-identical between the two arms** — see §6.2.
Relative error is `|Jan − Jfd| / |Jfd|`, per component. Lab band: **PASS ≤5% and no sign flip /
CONDITIONAL 5–15% / FAIL >15% or any sign flip.**

| DV | idx | meaning | analytic STOCK | analytic PATCHED | FD (both arms) | rel err STOCK | rel err PATCHED | sign |
|---|---|---|---|---|---|---|---|---|
| `patchV` | 0 | U0 | ` 7.334000e-04` | ` 7.334000e-04` | ` 4.260410e-03` | **82.79%** | **82.79%** | same |
| `patchV` | 1 | AoA | ` 9.016840e-03` | ` 9.016840e-03` | ` 8.729600e-03` | **3.29%** | **3.29%** | same |
| `twist` | 0 | root | `-2.107940e-03` | `-2.100900e-03` | ` 8.728200e-04` | **341.51%** | **340.70%** | **FLIP** |
| `twist` | 1 | | `-1.755830e-03` | `-1.750730e-03` | `-4.130860e-03` | **57.49%** | **57.62%** | same |
| `twist` | 2 | | `-1.477690e-03` | `-1.469450e-03` | `-4.581510e-03` | **67.75%** | **67.93%** | same |
| `twist` | 3 | | `-1.023320e-03` | `-1.010980e-03` | ` 1.703510e-03` | **160.07%** | **159.35%** | **FLIP** |
| `twist` | 4 | | `-6.396600e-04` | `-6.277000e-04` | `-1.461850e-03` | **56.24%** | **57.06%** | same |
| `twist` | 5 | | `-3.873900e-04` | `-3.797300e-04` | `-3.861320e-03` | **89.97%** | **90.17%** | same |
| `twist` | 6 | tip | `-1.374800e-04` | `-1.361900e-04` | ` 2.591130e-03` | **105.31%** | **105.26%** | **FLIP** |

**Vector-norm rows as OpenMDAO printed them** (these are the ledger's 36%/89%):

| group | arm | `Analytic Magnitude` | `Fd Magnitude` | `Absolute Error` | `Relative Error` | log line |
|---|---|---|---|---|---|---|
| `patchV` | stock | `9.046613e-03` | `9.713753e-03` | `3.538694e-03` | `3.642974e-01` | `stock.log:5001` |
| `patchV` | patched | `9.046613e-03` | `9.713753e-03` | `3.538694e-03` | `3.642974e-01` | `patched.log:5000` |
| `twist` | stock | `3.366792e-03` | `8.091896e-03` | `7.196140e-03` | `8.893021e-01` | `stock.log:5014` |
| `twist` | patched | `3.349174e-03` | `8.091896e-03` | `7.198402e-03` | `8.895816e-01` | `patched.log:5013` |

Every one of these lines carries OpenMDAO's `*` warning flag.

### 6.2 Verdicts against the lab band — GATE FAIL on BOTH images

| arm | image | components in ≤5% | in 5–15% | >15% | sign flips | **verdict** |
|---|---|---|---|---|---|---|
| 1 SHIPPED | `dafoam/opt-packages:latest` | **1 of 9** (`patchV` idx1, 3.29%) | 0 | **8 of 9** | **3** | **GATE FAIL** |
| 2 PATCHED | `dafoam-idwarp-rot:v1` | **1 of 9** (`patchV` idx1, 3.29%) | 0 | **8 of 9** | **3** | **GATE FAIL** |

**89% of graded components fail; three reverse sign. Both rows are GATE FAIL, and the patched row is
GATE FAIL by a hair's-breadth *larger* margin than the shipped row** (88.958% vs 88.930% in norm — a
difference of 0.028 percentage points, which §6.4 argues is not interpretable).

**Registered predictions P4, graded honestly:**

| registered | measured | outcome |
|---|---|---|
| `CD/twist` ≤5% on BOTH images | 56.24–341.51% (stock), 57.06–340.70% (patched) | **MISSED by 11×–68×** |
| `CD/patchV` ≤1% on both | 3.29% (idx1) and 82.79% (idx0) | **MISSED** — idx1 by 3.3×, idx0 by 83× |
| `CD/patchV` BIT-IDENTICAL between images | bit-identical, all 4 numbers | **HIT** |
| every FD magnitude bit-identical between arms (THE CONTROL) | bit-identical, all 9 | **HIT** |

Two of four registered P4 clauses hit; both hits are controls, both misses are the result.

### 6.3 Why the FD is the thing that failed — the signal-to-noise arithmetic

§4 measured the baseline primal's CD peak-to-peak wobble over its last 200 iterations at **9.00e-6**.
A central difference at `step = 1e-3` divides a CD difference by `2 × 1e-3`, so **the smallest
derivative this FD can resolve above the primal's own noise is 9.00e-6 / 2e-3 = 4.5e-3.**

Ranking the nine components by how far their FD magnitude clears that floor:

| DV, idx | `|Jfd|` | × noise floor (4.5e-3) | rel err (stock) |
|---|---|---|---|
| `patchV` 1 | `8.7296e-03` | **1.94×** | **3.29%** |
| `twist` 2 | `4.5815e-03` | 1.02× | 67.75% |
| `patchV` 0 | `4.2604e-03` | 0.95× | 82.79% |
| `twist` 1 | `4.1309e-03` | 0.92× | 57.49% |
| `twist` 5 | `3.8613e-03` | 0.86× | 89.97% |
| `twist` 6 | `2.5911e-03` | 0.58× | 105.31% |
| `twist` 3 | `1.7035e-03` | 0.38× | 160.07% |
| `twist` 4 | `1.4619e-03` | 0.32× | 56.24% |
| `twist` 0 | `8.7282e-04` | 0.19× | 341.51% |

**The single component that clears the noise floor by about 2× is the single component that agrees,
and it is the only one.** Clearing it by 1.0× (`twist` idx2) is not enough. Below 1×, the FD is
reporting noise: the seven `twist` FD entries have magnitudes 0.87e-3 to 4.6e-3 with **apparently
random signs** — three positive, four negative — against an analytic column that is **monotone
negative from root to tip**, which is the physically expected shape of `dCD/dtwist` on a
washout-loaded wing. A monotone analytic column and a sign-scrambled FD column of the same magnitude
as the noise floor is the signature of a noise-dominated difference, not of a wrong adjoint.

**This is a claim about which column is untrustworthy, and it should be read as provisional.** What
is *measured* is (i) the noise floor, (ii) the ratios above, and (iii) the monotonicity. What is
*inferred* is that the analytic column is the better one. The rung contains **no independent
reference** that could settle it — that is the missing arm, and §8 records it as such.

### 6.4 Does the patch change anything? The cross-image diagnosis, from the logs only

Three controls fire cleanly and make this comparison meaningful:

1. **The baseline primal is bit-identical between images.** `stock.log:709-710` and
   `patched.log:714-715` both end at `CD: 0.03506349413916734`, `CL: 0.457426809939543`, cumulative
   continuity `-0.005045133651340859`. The patch is derivative-only, as designed.
2. **The FD column is bit-identical** (§6.1). Both arms differenced the same function.
3. **The adjoint is bit-identical in its convergence path**: `517` iterations, reason `2`, and the
   same KSP residual to 13 digits at every printed checkpoint (`stock.log:806-811` vs
   `patched.log:768-775`). Only the wall-clock stamps differ.

Against that background:

| group | changed by the patch? | magnitude |
|---|---|---|
| `CD/patchV` | **NO — bit-identical, both components** | exactly 0 |
| `CD/twist` | **YES — all seven components move** | per-component **0.29% to 1.98%**; **0.664% in L2 norm** |

Per-component analytic shift, patched minus stock:

| idx | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Δ | `+7.04e-06` | `+5.10e-06` | `+8.24e-06` | `+1.234e-05` | `+1.196e-05` | `+7.66e-06` | `+1.29e-06` |
| Δ/|stock| | 0.334% | 0.291% | 0.558% | 1.206% | 1.870% | 1.977% | 0.938% |

**Answers to the three questions this rung was built to ask:**

* **Are the large-error components the same indices on both images?** **Yes — identically so.** The
  same eight components exceed 15% on both, the same three flip sign on both, and the rank order of
  the errors is unchanged. The patch does not move a single component across a band boundary.
* **Does the patched image change the error at all?** **Effectively no.** It changes `CD/patchV` by
  exactly zero and `CD/twist` by 0.664% in norm — against an FD reference carrying 89% error. In
  error terms the patched arm is 0.028 pp *worse*, which is meaningless noise on that reference.
* **Is this the A3 precedent (rotation defect regime-1-only)?** **Yes, and this rung strengthens it
  on the axis the prereg said would discriminate.** The prereg's §5 offered R1 (the defect's reach is
  objective-dependent, and transonic-wing objectives contract weakly with the discarded rotation
  term) against R2 (the DV *class* matters, and A3's stock passes were an artifact of grading
  `patchV`, which provably never crosses the warp).
  * **R2's premise is confirmed and then discharged.** `patchV` really does not cross the warp — its
    analytic derivative is bit-identical across images, to the last digit. And `twist` really *does*
    cross it — all seven components move. **So this rung graded a genuinely warp-crossing DV.**
  * **And the warp-crossing DV moved by 0.664%.** On A1, A2, A5 and the naca0015 sail the same defect
    accounted for **97–99.5%** of the shape-derivative error. Here it accounts for **under 1%** — two
    orders of magnitude less — on a DV that demonstrably passes through `DVGeo → warpDeriv`.
  * **R1 gains; R2 does not survive as the explanation for A3.** A3's stock passes cannot be
    dismissed as "they only graded `patchV`", because A6's `twist` — same solver, same size class,
    same geometry family — behaves the same way. The prereg's registered "outcome that would most
    change the standing picture" (stock `CD/twist` large and the patch collapsing it, forcing a
    re-grade of A3 rungs 1 and 2) **did not occur.** For scale, the shift here (0.664%) is the same
    order as A2's aero-only `CD/twist`, which the patch moved from 0.389% to 0.505%.
* **Did the registered P4 falsifier fire?** Registered: *"the patched arm's `CD/twist` differing from
  the stock arm's by more than the FD's own resolution while `CD/patchV` stays bit-identical."*
  `CD/patchV` did stay bit-identical, and `CD/twist` did move — **but by at most `1.234e-05`, which
  is 365× BELOW the FD's own resolution of `4.5e-3`.** **The falsifier does NOT fire.** The condition
  was written expecting the FD to be the finer instrument; it was the coarser one by two orders of
  magnitude.

**The load-bearing point about this whole section: it is an analytic-vs-analytic comparison, and it
therefore survives the FD's collapse.** Both columns are deterministic outputs of the same
bit-identical primal and the same bit-identically-converging adjoint, differing only in
`libidwarp.so`. Nothing noisy enters. **This is the one P4 question the rung can still answer, and
it answers it: on A6 at N=16, the rotation patch moves `CD/twist` by 0.66% and `CD/patchV` by
nothing.** It grades the patch. It does not grade the gradient.

### 6.5 P5 — trivial baseline: **NOT RUN.** Registered and not executed.

The wrong-step arm (`step=1e-8`, patched image) was registered in prereg §5 and **was never launched
in attempt 2**. Evidence: `/home/ubuntu/certonomous-runs/P2-a6-n16/wrongstep/` still carries the
attempt-1 script (`diff wrongstep/runScript.py stock/runScript.py` → line 284 only, `step=1e-8` vs
`step=1e-3`), no `wrongstep.log` exists for attempt 2, and `rss_wrongstep.txt` ends at
`2026-08-21T16:48:38Z`. The §2 arm table's row 3 reads `—` for `rc` and `wall` accordingly.

**Recorded as a gap, not as a pass.** It is not being run now, and the reason is stated rather than
absorbed: P5's stated purpose was *"to prove the instrument can still fail, so a pass in P4 is a
property of the derivative and not of a harness incapable of returning a large number."* **P4 did not
pass, and the harness returned 341.51%, 160.07% and 105.31% at the *registered* step.** The specific
doubt P5 was built to remove — a harness that cannot produce a large number — is already excluded by
the graded arms themselves. Running a second arm to demonstrate that a deliberately-bad step also
fails would buy ~30 core-min of confirmation of something no longer in question, and would not change
the N=29 gate decision in §9. **Verdict: PENDING, deliberately unspent.**

### 6.6 P1 — peak RSS: CORRECTED. 9.787 GiB, not 7.396 GiB.

§5 above reports 7.396 GiB. **That figure is wrong and is superseded here.** The correct measurement,
from the record-only monitor's own file:

| arm | peak RSS | samples | peak sample line |
|---|---|---|---|
| 1 SHIPPED | **9.787 GiB** | 79 | `rss_stock.txt` → `2026-08-21T17:33:06Z stock 9.787GiB / 12GiB` |
| 2 PATCHED | **9.783 GiB** | 90 | `rss_patched.txt` → `2026-08-21T18:31:32Z patched 9.783GiB / 12GiB` |

**How the error arose, so it is not repeated.** `run_arm.sh`'s peak extractor reads `awk '{print $4}'`,
but the sample format is `<timestamp> <arm> 9.787GiB / 12GiB` — field 3 is the used figure and field
4 is the literal `/`. That is why both ledger lines read `peak_rss=unmeasured`. The 7.396 GiB figure
does not correspond to any sample in either file; the two nearby values that do exist are 6.564 GiB
(the peak of the *interrupted* attempt-2 stock arm, `rss_stock_attempt1and2.txt`, which never reached
the FD loop) and the true 9.787 GiB. **The bug is already fixed in the A4 script**
(`/home/ubuntu/certonomous-runs/P2-a4-opt/run_arm.sh`, which reads field 3 and carries a comment
naming this defect).

**Re-grading P1 against the frozen prediction:**

| | value |
|---|---|
| predicted (prereg §5 P1) | ≈6.8 GiB |
| measured | **9.787 GiB** |
| miss | **+44% above prediction**, not the +8.8% §5 claimed |
| hard ceiling / falsifier | 12 GiB |
| headroom | **18.4% below the ceiling** |

**The 12 GiB falsifier did NOT fire, so P1's registered failure condition is not met — but the
prediction itself is missed by 44%, and that miss matters downstream.** The de-biasing step in the
prereg's derivation (dividing model M2's 8,897 MiB by a measured 1.27× conservatism) is what produced
6.8 GiB. **The measurement says the conservatism factor does not apply to CRM: raw M2 gives 8,897 MiB
= 8.69 GiB, and the measurement is 9.787 GiB, i.e. M2 UNDER-predicts CRM by 12.6% rather than
over-predicting it by 27%.** Per prereg §7.1 this single point does not re-fit the scaling law, but
it points the correction in the direction that keeps full size BLOCKED **more** firmly, not less.
This measurement is carried into `../../A3/original_memory_plan/PREREGISTRATION.md` as an input.

**Instrument caveat:** `docker stats` `MemUsage` is a cgroup accounting figure, not RSS as `ps`
reports it; it can include reclaimable page cache. It is the registered instrument and both arms were
measured the same way, so the stock-vs-patched comparison (a 4 MiB difference on ~9.8 GiB) is sound;
the absolute figure should be read as an upper bound on true RSS.

## 7. Attempt 1 — the GATE FAIL, its real cause, and the unregistered edit that unblocked it

§3 established the mechanism (`DASolver::checkPrimalFailure()`). This section closes the two questions
the record still had open: **which candidate cause it was not**, and **what was changed to get past it.**

### 7.1 It was not `transonicPCOption`, and it was not the mesh

| candidate | verdict | evidence |
|---|---|---|
| `transonicPCOption` still at the dead value 2 | **EXCLUDED** | `ledger_attempt1_gatefail.txt` records `transonicPCOption 1;` for **all three** attempt-1 arms. The mandatory activity proof of prereg §3 passed on attempt 1. |
| bad mesh | **EXCLUDED** | The same `base/` mesh — 41,760 cells, `wing` 2,784 faces — ran 1,000 primal iterations, a 517-iteration adjoint and 19 FD solves to `rc=0` in attempt 2. Nothing about the mesh changed between the attempts. |
| warm-start contamination | **REAL BUT NOT THE KILLER** | §3.1: only the `stock` arm was contaminated; the two cold arms failed identically. |
| **`primalMinResTolDiff` at its default 1e2** | **THE CAUSE** | `stock_attempt1_gatefail.log:356` → `primalMinResTolDiff 100;`. Measured ratios 555.6 (stock) and 590.9 (both cold arms) against a cap of 100. All three died at `mphys_dafoam.py:345` → `AnalysisError("Primal solution failed!")` (`stock_attempt1_gatefail.log:782`), **before any adjoint was attempted.** |

### 7.2 The unregistered third edit — disclosed as an amendment, not buried

Attempt 2 got past the gate by **raising `primalMinResTolDiff` from `1.0e2` to `1.0e4`**:

```
stock/runScript.py:37   "primalMinResTolDiff": 1.0e4,
stock_attempt1_gatefail.log:356     primalMinResTolDiff 100;
stock.log:356                       primalMinResTolDiff 10000;
```

**Prereg §2 registered "exactly two edits" to the archived recipe, and §3 registered exactly two
configuration changes. This is a third configuration change and it is not in the frozen file.** It is
recorded in §10 as Amendment 2. It was necessary — without it there is no A6 adjoint at all — and it
is not concealed by the arms, since every log prints the value.

**But it should be read for what it is.** `primalMinResTolDiff` is DAFoam's own guard against
accepting a primal that has not converged, and the condition it was widened 100× to tolerate is
**exactly the condition §6.3 identifies as having destroyed the FD**: a primal sitting 556× short of
its tolerance, wobbling by 9.0e-6 in CD. **The guard was right.** Raising it bought the first A6
adjoint — a real gain, and the rung's headline — at the price of a finite-difference reference the
solver had already declined to certify. Any future rung on this case should either converge the
primal properly or choose an FD step sized against the measured wobble, and should not simply inherit
`1.0e4`.

## 8. Costs, and what this rung cannot see

### 8.1 Measured cost — under the registered ceiling, with 23% waste

| item | wall | ranks | core-min | note |
|---|---|---|---|---|
| mesh generation | — | 1 | ~1 | done before the prereg was filed; excluded from the ceiling by §6 of the prereg |
| calibration primal | 54 s exec | 1 | **0.903** | **waste** — also the source of the §3.1 contamination |
| attempt 1, 3 arms @ 67–68 s | — | 1 | **3.383** | **waste** — GATE FAIL, §7 |
| attempt 2 stock, interrupted 16:50:08→17:03:48Z | 820 s | 1 | **13.667** | **waste** — user stop at ~17:05Z, killed mid-adjoint at KSP iteration ~200 |
| **arm 1 SHIPPED (graded)** | 1676 s | 1 | **27.933** | `rc=0` |
| **arm 2 PATCHED (graded)** | 1846 s | 1 | **30.767** | `rc=0` |
| arm 3 wrong-step | — | — | **0** | not run, §6.5 |
| **TOTAL** | | | **76.653** | **47.9% of the 160 core-min ceiling** |

**Cost at $0.0513/core-hour: 76.653 core-min = 1.2775 core-hours = $0.0655.**
Of that, **17.95 core-min (23.4%, $0.0153) is waste** — one contaminated calibration, one gate-fail
attempt, one interrupted run. Graded compute alone: 58.700 core-min = **$0.0502**.
The registered ceiling was not reached and no arm was dropped for cost.

### 8.2 What this rung cannot see — the prereg's five, plus three the run added

The prereg's §7 list stands unchanged and unweakened: (1) it is 13.9× smaller than full size and
carries no drag-accuracy claim; (2) `shape` is not graded; (3) the decomposition axis is absent at
np=1; (4) regime 2 of the rotation defect is invisible at the undeformed baseline; (5) the limiter
axis is not varied — and §1 confirmed by audit that A6 carries **no `cellLimited` scheme at all**, so
defect D-B2 cannot act here.

**Three further blind spots this run created, none of them registered in advance:**

6. **It cannot tell you whether the adjoint is right.** The rung's only independent reference was the
   FD, and §6.3 shows the FD is noise-dominated on 8 of 9 components. `patchV` idx1 at 3.29% is the
   sole verified component. **The 517-iteration converged adjoint is unverified except on that one
   AoA derivative.** Everything §6.4 says about the patch is a statement about the *difference*
   between two analytic columns, and would remain true even if both were wrong in the same way.
7. **It cannot separate "FD noise" from "adjoint error" by measurement.** §6.3's ranking is a strong
   consistency argument, not a discriminator. The arm that would settle it — a converged primal
   (tighter `primalMinResTol`, or many more iterations) re-differenced at the same step, or a
   complex-step / AD reference — **was not run and is not registered anywhere.**
8. **The CL half of P3 was never evaluable** (§5), and the wrong-step control was never run (§6.5).

## 9. VERDICTS, and the N=29 GATE DECISION

### 9.1 Verdict table

| # | item | registered prediction | measured | **verdict** |
|---|---|---|---|---|
| — | attempt 1, all three arms | — | `rc=1` at 67–68 s, `primalMinResTolDiff` gate | **GATE FAIL** |
| P1 | peak RSS ≈6.8 GiB, ceiling 12 GiB | **9.787 GiB** (stock) / 9.783 (patched) | ceiling not breached; prediction missed +44% | **GATE REACHED** |
| P2 | primal does not reach 1e-8, 1,000 iters, CD stable ≥4 s.f. | `primalMaxRes` 5.556e-06, CD p2p 9.00e-6 | exactly as registered | **GATE REACHED** |
| P3 | CD adjoint `reason 2` in 400–1,500 iters | **517, reason 2**, monotone over 6 decades | **the first A6 adjoint that has ever existed** | **PASS** |
| P3 | CL adjoint `reason 2` | only one adjoint solved (prereg §3 restricted `of=["CD"]`) | prereg-internal inconsistency | **NOT A RESULT** |
| **P4** | **`CD/twist` ≤5%, SHIPPED image** | **56.24–341.51%, 3 sign flips** | 8/9 components >15% | **GATE FAIL** |
| **P4** | **`CD/twist` ≤5%, PATCHED image** | **57.06–340.70%, 3 sign flips** | 8/9 components >15% | **GATE FAIL** |
| P4 | `CD/patchV` ≤1%, both images | 3.29% (idx1), 82.79% (idx0) | missed on both components | **GATE FAIL** |
| P4 | `CD/patchV` bit-identical across images (control) | bit-identical | control held | **PASS** |
| P4 | every FD magnitude bit-identical across images (THE CONTROL) | bit-identical, all 9 | control held | **PASS** |
| P4 | R1-vs-R2 discrimination on a warp-crossing DV | `twist` confirmed warp-crossing; patch moves it **0.664%** | **R1 gains, R2 discharged** | **PASS** |
| P5 | wrong-step trivial baseline >50% | arm not launched | §6.5 | **PENDING** |

**Headline verdict for the rung: GATE FAIL on both images.** The adjoint result (P3) is a genuine
PASS and the first of its kind; the gradient verification the rung existed to obtain is a GATE FAIL
whose measured cause is the finite-difference reference, not the adjoint.

### 9.2 THE N=29 GATE — **N=29 IS NOT RUN**

**Sanaa's condition, as held by this lane: N=29 is approved ONLY if N=16 passes on the patched image.**

**N=16 does not pass on the patched image.** The numbers, restated so the decision is auditable
without reading back:

* **8 of 9 graded components exceed 15%** on the patched image — 57.06%, 57.62%, 67.93%, 82.79%,
  90.17%, 105.26%, 159.35%, 340.70%.
* **3 of 9 reverse sign** (`twist` idx 0, 3, 6). The lab band makes **any** sign flip an automatic FAIL.
* The single component inside ≤5% is `patchV` idx1 at **3.29%**.
* Vector-norm relative error on the patched image: **`8.895816e-01` (88.96%) for `twist`,
  `3.642974e-01` (36.43%) for `patchV`** — both flagged `*` by OpenMDAO.
* The patched image is **not better** than the shipped image on this rung: identical on `patchV`,
  0.664% different on `twist` analytic, and 0.028 pp *worse* in FD relative error.

**DECISION, 2026-08-21: N=29 is NOT RUN. The gate is not met.** No N=29 arm is launched, staged or
queued, and no compute is spent on it.

**And the gate should not be re-opened by re-running N=29 as-is.** §6.3 locates the failure in a
finite-difference reference that cannot resolve a derivative below 4.5e-3, caused by a primal that
stops 556× short of its tolerance. **N=29 is 79,560 cells — a 1.9× larger mesh on which the same
solver is already known to stagnate** (prereg §7.1 records this). There is no measured reason to
expect the primal to converge *better* there, and every reason from §6.3 to expect the same
noise-dominated FD, at ~2× the cost. **Fixing the reference, not enlarging the mesh, is the next
step**, and it is not registered anywhere yet.

## 10. Amendments — departures from the frozen pre-registration, dated

Recorded here per the rule that the frozen file is never edited.

**Amendment 1 (2026-08-21, ~17:15Z, predecessor lane) — decontamination of the `stock` arm.** The
calibration primal of prereg §4 step 0 was run inside `/mnt/stock` rather than a scratch copy
(`calib_primal.log:9` → `Case : /mnt/stock`), warm-starting attempt 1's stock arm (§3.1). The `stock`
arm directory was re-staged from the pristine `base/` before attempt 2. Confirmed effective: attempt
2's stock baseline primal is **bit-identical to the patched arm's** (§6.4 control 1), which the
contaminated attempt-1 run was not.

**Amendment 2 (2026-08-21, ~17:18Z, predecessor lane) — `primalMinResTolDiff` 1.0e2 → 1.0e4.**
A third configuration change beyond the two registered in prereg §3, made to clear the
`checkPrimalFailure()` gate that killed attempt 1. Necessary; disclosed; every log prints the value.
**Its scientific cost is argued in §7.2 and is not small.**

**Amendment 3 (2026-08-21, ~19:00Z, this lane) — peak-RSS extraction corrected.** The registered
record-only monitor worked; its peak extractor read the wrong `awk` field, so both ledger lines read
`peak_rss=unmeasured` and §5's independently-quoted 7.396 GiB does not match any sample on disk. The
corrected figures (9.787 / 9.783 GiB) are derived in §6.6 from the unmodified sample files. No arm
was re-run. §5's original sentence is preserved with an inserted pointer.

**Amendment 4 (2026-08-21, ~19:00Z, this lane) — P5 wrong-step arm not run.** Registered in prereg
§5, never launched. Reason stated in §6.5 rather than absorbed. Verdict PENDING, not PASS.

**Amendment 5 (2026-08-21, this lane) — arm 3's row in §2's table.** The §2 table, written before
arm 2 finished, shows arms 2 and 3 with `—` for `rc`/`wall`. Arm 2 completed: `rc=0`, **1846 s**,
30.767 core-min, `IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425`, `transonicPCOption 1;`,
`nProcs : 1` (`ledger.txt`; `patched.log:14`). Arm 3 remains `—` because it was never run.
