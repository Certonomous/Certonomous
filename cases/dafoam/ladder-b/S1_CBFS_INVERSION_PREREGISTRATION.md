# S1 — CBFS field inversion: pre-registration

**Written 2026-08-04 ~18:50 UTC, before any inversion iteration has run.** The only
numbers that exist at this writing are the baseline objective at beta = 1
(`1.5279278906359758e-02`, measured by W4 and reproduced bit-identically by the W4 FD
control and the supervisor sweep) and the single FD-verified gradient at beta = 1
(`cbfs_beta_grad.npy`, W4 §5c–5d). **No J trajectory exists. No beta field other than
all-ones exists.** Every number that decides the outcome below is unmeasured when this
file is committed.

Item: the Stage 1 CBFS inversion minted at the close of
`fiml-adjoint-conditioning-unblock` (PRODUCT_LIST changelog 2026-08-04: "Run the Stage 1
inversion on CBFS — beta inversion toward Bentaleb LES with the verified sub-LU adjoint;
needs a costed proposal + pre-registration first"). Proposal filed alongside this file as
`agenda/proposals/s1-cbfs-field-inversion-run.json`, approved under Katie's standing
authorization. **Hard budget cap: 600 core-min**, all solver runs of this item included.

Capability being exercised (all verified, nothing new claimed here): image
`dafoam-subpclu:v1`, env `DAFOAM_SUBPC_TYPE=lu`, B3's CBFS case (21,000 cells), beta
design variable `betaFIOmega` (21,000 DVs), adjoint converges (reason 2, 667 iters),
gradient FD-verified to 0.02–0.2% on four cells (three by W4, one independently by the
supervisor sweep). `W4_ADJOINT_PC_UNBLOCK.md`,
`VERIFICATION_cbfs_unblock_supervisor_sweep.md`.

---

## 1. The label, stated before any number exists

**This is a PRODUCTION-term inversion.** DAFoam's `betaFIOmega` multiplies the SST omega
equation's production term (`DAkOmegaSST.C:743`). Wu, Zhang & Zhang invert on the
DESTRUCTION term (paper Eq. (2)/(5), W2 reading 2026-08-04). The two are not equivalent
(S1 §2), and **no number this run produces may be set beside Wu/Zhang's objective
reductions (CBFS −88.3% CLS / −74.7% CND) as like-for-like** — those belong to a
different equation, a different (sparse-point) loss, and ~140 SLSQP iterations against
our ~30-eval budget. The C2 correction of 2026-08-04 and supervisor ruling R6 both bind
here. What this run is: the lab's first actual field inversion on a closure-relevant
case, method-labeled, on the term this stack exposes and has verified.

## 2. Objective and the data entering the loss

```
J(beta) = lambda_QoI * varianceU(beta) + lambda_L2 * sum_j (beta_j - 1)^2
```

- **`varianceU`**: DAFoam's `variance` DAFunction, `mode=field`, `source=allCells`,
  against `0/UData` — **byte-for-byte the objective whose gradient is FD-verified**
  (W4 §5c, `cbfs_beta/runScript.py`). `UData` is CBFS's own Bentaleb, Lardeau &
  Leschziner LES velocity field as shipped by the public benchmark for its
  **training** case, provenance established in `W2_SPARTA_CBFS_DATA_FORENSICS.md`
  (NASA-hosted Bentaleb LES to interpolation accuracy).
- **`lambda_QoI = 6.5448114804931393e+01`** = 1 / 1.5279278906359758e-02, so that the
  QoI term of J equals exactly 1 at beta = 1 — Wu/Zhang's own normalization convention
  (paper Eq. (7), W2 reading).
- **`lambda_L2 = 1.0e-4`**, fixed now and not tuned. Their protocol tunes lambda_L2 by
  trial and error until the penalty is 10–20% of post-optimization QoI error; iterative
  tuning is not affordable inside a 600 core-min cap, so the value is pre-declared at the
  top of their stated band (1e-5–1e-4), and the achieved penalty fraction is **reported**
  after the run against their band, as a disclosure, not a gate.
- **Disclosed deviation from the reproduction target's loss:** Wu/Zhang's CBFS loss uses
  LES x-velocity at 30 sparse points in the separation region. This run uses the
  all-cells field variance instead, because that is the objective configuration whose
  gradient this lab has verified; a sparse-point `probePoint` objective would be a new,
  unverified DAFunction configuration. This is a second, independent reason (beyond
  production-vs-destruction) that this inversion is method-labeled and not a
  reproduction.

**Leakage statement, before the run:** CBFS is the benchmark's field-inversion TRAINING
case, not one of the 8 scored test cases (verified against
`closure_challenge_criterion_test_case_table.json` by the W4 sweep §5). Nothing in this
run's loop touches any scored case's data. The inversion is in-sample to CBFS **by
design** — that is what field inversion on a training case is; no benchmark score and no
generalization claim can come out of this run. Generalization is Stage 2's question
(learn beta(features) on training-case inversions, apply forward), per charter §11.

## 3. Design variable, bounds, optimizer

- **DV**: per-cell `betaFIOmega`, 21,000 components, initial value 1.0 everywhere
  (uniform prior, theirs).
- **Bounds [0.2, 4.0]**: the upper bound 4 is theirs (entry §2 — the only bound either
  artifact states); the lower bound 0.2 is **ours by choice** (neither artifact states
  one; 0.2 keeps the production multiplier positive and bounded away from an
  omega-production shutoff), disclosed as such.
- **Optimizer: SciPy L-BFGS-B** via OpenMDAO `ScipyOptimizeDriver`; `maxcor` 10,
  `maxls` 8, `ftol` 1e-10, `gtol` 1e-6.
  **Disclosed deviation from their SLSQP, with the arithmetic that forces it:** SciPy's
  SLSQP allocates a dense workspace of `3.749e9` doubles at n = 21,000 with no
  constraints — **30.0 GB, the whole of this host's RAM**. (Their inversions ran SLSQP
  at similar DV counts on their hardware; on this box the choice is L-BFGS-B or
  nothing.) L-BFGS-B is bound-constrained and O(m·n) in memory. One consequence worth
  stating in advance: L-BFGS-B evaluates objective AND gradient at every line-search
  trial point, so the budget is counted in **evaluations** (primal+adjoint pairs), not
  optimizer iterations.
- **Convergence criterion**: the optimizer's own termination (`ftol`/`gtol` above). A run
  stopped by the iteration cap, evaluation cap, or budget cap is recorded
  **capped, not converged** — a cap is a budget, not a settle criterion (charter §4).

## 4. Iteration caps, checkpointing, and the stop rule

- **Calibration run first (STEP 2 of the assignment)**: same script, `maxfun = 3`,
  one process. Purpose: measure the **marginal** per-evaluation cost (the eval-to-eval
  wall delta from the history file, which prices primal + adjoint + line-search overhead
  inside a warm process, with setup amortized out). Its evaluations are real inversion
  progress; its final `beta_latest.npy` seeds the main run (`-betafile`). The L-BFGS-B
  restart between the two runs loses 3 curvature pairs — disclosed, costs at most one
  poor early step.
- **Main run**: `maxiter = 30`, `maxfun = 36` minus calibration evals, started from the
  calibration checkpoint.
- **Checkpointing**: every evaluation appends `(walltime, neval, varianceU, J_qoi_norm,
  penalty, J)` to `J_history.csv` and rewrites `beta_latest.npy`; every 10th evaluation
  writes a numbered `beta_eval*.npy`. A kill at any moment therefore loses at most one
  evaluation.
- **Stop rule**: the launcher polls the billed ledger (cpus × wall, summed over this
  item's runs); at ≥ **585 core-min** cumulative the container is stopped
  (`docker stop`), the trajectory to the last checkpoint is the partial result, and it is
  recorded as budget-capped with no softening. The remaining ~15 core-min are reserved
  for the final-state write-out (§6).
- **CPU allotment**: 4 ranks always (the coloring cache and every verified cost number
  are at 4 ranks). `--cpus=4` when the box carries no other compute (docker ps empty and
  load low — the state measured at this writing); `--cpus=2` if another agent's solve
  appears. Oversubscribing 4 ranks onto 2 cpus is known to **waste** budget (sweep §6:
  the same solve billed 8.0 core-min at 2 cpus vs 6.1 at 4), so 4 is the default when the
  box is free, and the choice at each launch is recorded.

## 5. The cost model (to be calibrated, then amended if off by >2x)

Measured basis (W4): one cold `compute_totals` on this exact case and DV set =
243–246 s wall at 4 ranks = **16.2–16.4 core-min**, comprising process setup + warm
primal + partials/coloring + one adjoint solve (667 KSP iters). Assumption made now and
checked by the calibration run: the marginal in-loop evaluation costs about the same
(setup drops out; in-loop primals re-converge from the previous state; the adjoint
dominates either way).

| stage | est core-min |
|---|---|
| calibration process (setup + 3 evals) | ~55 |
| main run (≤ 33 further evals at ~16.4) | ~545 |
| final cold primal at beta_final + cell-centres write | ~15 |
| **hard cap, everything included** | **600** |

At this model the budget reaches **~36 evaluations** against Wu/Zhang's ~140 SLSQP
iterations — a pre-declared partial-depth inversion, which is why the success bar in §7
is set at 30% and not at their 74.7–88.3%. **If the calibrated marginal cost differs
from 16.4 core-min by more than 2x in either direction, this section is amended with a
dated amendment (never edited silently) before the main run launches.**

## 6. Final-state record (pre-declared post-processing)

After the optimizer stops (converged, capped, or killed at budget): one **fresh-process,
cold** `run_model` at `beta_final.npy` (the FD protocol's own control shape — fresh
process, cold processor dirs are NOT reset here since the case warm-start is from 0/ by
`startFrom startTime`), which (a) reproduces the final J from a state-independent solve
and (b) writes `betaFIOmega` and the flow fields to a time directory; then
`postProcess -parallel -func writeCellCentres` on that time. Field statistics and the
beta-vs-position map in the result document are read from those written OpenFOAM fields,
not from the DV vector, so the spatial mapping cannot depend on any assumed DV-to-cell
ordering.

## 7. Success criteria, fixed now

- **G1 — the inversion moves the data term.** Normalized QoI term
  `J_qoi = lambda_QoI * varianceU` falls from 1.000 to **≤ 0.70** (≥ 30% reduction) at
  the last accepted iterate within budget. This bar is ours, sized to a ~36-eval budget;
  it is NOT their bar and their numbers are not the reference (§1).
- **G2 — the beta field deviates where the physics says the model error lives.** Among
  the 2,100 cells (top decile) ranked by |beta_final − 1|, **more than 50%** have cell
  centres inside the pre-declared window **0 ≤ x/h ≤ 6, 0 ≤ y/h ≤ 2** (step crest at
  x = 0, h = 1 mesh unit — mesh extents x ∈ [−7.34, 15.4] measured before this run) —
  the recirculation bubble, separated shear layer, and near recovery region. A beta
  field that instead concentrates its correction at the inlet, the outlet, or the upper
  wall fails G2 regardless of G1.
- **Qualitative expectation, recorded as an expectation and not a gate:** in the shear
  layer the deviation should go **below 1** (less omega production → lower omega →
  higher nu_t → more mixing), the production-term mirror of Wu/Zhang's beta > 1 on
  destruction. The sign the inversion actually chooses is a finding either way.
- **Reported alongside, no gate attached**: fraction of cells pinned at either bound;
  penalty fraction vs their 10–20% band; evaluation count; core-min ledger.
- **A divergence, a stall, or a primal failure at a trial point IS the result** and is
  recorded with diagnostics, per charter §8. If a trial-point primal fails, the run
  terminates and the last checkpoint stands as the partial result.

## 8. What this run can and cannot establish

Can: that the verified gradient drives an actual descent on a closure-relevant case;
where a production-term beta wants to move on CBFS; the real per-iteration price of
Stage 1 inversions on this stack (the number Stage 2 planning needs).

Cannot: anything about the destruction-term physics (that is
`w3-beta-on-omega-destruction-model-patch`); anything about generalization (Stage 2);
any benchmark score; any like-for-like comparison with the Wu/Zhang paper or the rank-2
entry.

*Nothing below this line existed when this file was committed. The calibration and main
runs launch only after this commit lands.*

---

## Amendment 1 — dated 2026-08-05, after the calibration run and before the main run

The calibration run (2026-08-04 18:46:34–19:02:06Z, 932 s at 2 cpus, **31.07 core-min**,
`S1-cbfs-inversion/ledger.csv`, `log.calib`) did not deliver a marginal per-eval cost. It
delivered a defect, and the defect forces a mechanism change. Recorded here as a dated
amendment, not a silent edit; nothing in §1–§3 (label, loss, data, bounds, optimizer
algorithm, convergence criterion) changes.

**What was measured (log.calib):**
1. Eval 1 (initial `run_model`, cold from `0/`): varianceU = `1.5279278906359758e-02`,
   **bit-identical** to the W4 baseline. J = 1.0 exactly. The control holds.
2. The optimizer's first objective call re-ran the primal **in-process from the
   in-memory converged state** ("Running Primal Solver 002"), and that restarted primal
   **diverged**: p initial residual 0.025 at its first iteration (vs ~1e-6 converged),
   wandering to **0.2148 at the endTime-2500 cap**, omega/k pinned at their 1e-16 floors
   ("Bounding omega>1e-16" every iteration, omega residual ~1e-27 = equation decoupled),
   varianceU drifted 0.015279 → 0.016945 (+10.9%). DAFoam printed
   "Primal solution failed!" — **and then continued into the adjoint anyway** (same
   trap family as the unchecked `decomposePar` exit status, S1 §4 fault 3).
3. The adjoint assembled at that unconverged state **stagnates flat**: KSP residual
   4.6413e-02 → 4.6118e-02 over 1000 iterations (0.64%), reason **-3**, where W4's
   verified solve at the properly converged state fell six decades and converged at 667.
   (Initial residual 4.641e-02 = lambda_QoI x 7.0916e-04 — the RHS scaling behaves
   exactly as arithmetic predicts; the stagnation is the state, not the scaling.)

**Consequence:** in-process multi-evaluation optimization (one persistent DAFoam
process, `ScipyOptimizeDriver`) is **structurally unavailable on this case** — every
post-first evaluation would solve primal and adjoint at a state the restarted SIMPLE
iteration has walked away from. This is a real finding about the stack on CBFS and goes
in the result document.

**Mechanism change:** the L-BFGS-B loop moves **outside the process**. A host-side
SciPy L-BFGS-B (same algorithm, same bounds [0.2, 4.0], same maxcor 10 / maxls 8 /
ftol 1e-10 / gtol 1e-6) calls, per evaluation, a **fresh container process** running the
verified `compute_totals` configuration with `-betafile` — byte-for-byte the W4 FD
protocol shape (fresh process, `sudo rm -rf processor*` cold reset, cold start from
`0/`, one primal + one adjoint), which is the shape under which the objective is proven
bit-reproducible and the gradient FD-verified. lambda_QoI scaling and the L2 penalty
(value and gradient, both analytic) are composed on the host. The first evaluation at
beta = 1 doubles as a control: varianceU must reproduce `1.5279278906359758e-02` and the
gradient must match W4's archived `cbfs_beta_grad.npy`.

**Cost model re-based, and the §5 amendment rule applied:** the marginal per-eval cost
is now the **cold** compute_totals — 16.4 core-min at 4 ranks/4 cpus (measured twice by
W4), ~16–17.5 core-min at 4 ranks/2 cpus (sweep §6 oversubscription data). That is
**within 1.1x of the §5 model**, so the arithmetic stands; what is refuted is only the
amortization assumption behind it (in-process warm primals do not exist anymore).
Ledger: 31.07 core-min spent; **eval cap 32**; the driver refuses to launch an
evaluation whose projected completion would cross **585 core-min** cumulative, and the
last ~15 are reserved for the final-state write-out of §6. Per the supervisor's resume
instruction a sibling agent will be solving concurrently: **--cpus=2 for every
evaluation**, recorded per launch in `ledger.csv`.

**Checkpoint/restart bookkeeping under the new mechanism:** history line + beta
checkpoint per evaluation (unchanged cadence, now trivially crash-safe since every
evaluation is its own process); accepted-iterate snapshots via the optimizer callback;
on any abort the last accepted iterate is the partial result. The two-stage
curvature-loss disclosure in §4 is void (single continuous L-BFGS-B run).

*Nothing below this amendment existed when it was committed; the main run launches only
after it lands.*
