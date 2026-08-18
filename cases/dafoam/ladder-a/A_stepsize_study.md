# A1 finite-difference step-size study (Ladder A priority probe)

Date: 2026-07-28. Case: `ladder-a1-naca0012` (`/home/ubuntu/certonomous-runs/ladder-a1-naca0012`),
4032 cells, 2 MPI ranks, `dafoam/opt-packages:latest`, `--network=host --memory=4g`, same
`daOptions`/`Top` class as A1's own `runScript.py` (`primalMinResTol=1e-8`). Only the central-difference
step size varies. Full data: `A_stepsize_study.json`; raw run logs: `logs_A1_stepsize/`.

Objective checked: `CD wrt shape` (8 FFD design variables), the same derivative A1 reported at 11.43%.

## Sweep table (full 8-component vector-norm relative error)

| step | rel err (full 8-vector) | rel err (excl. idx0,1,6) | cosine (full) | status |
|---|---|---|---|---|
| 1e-8 | 94.95% | 91.71% | 0.407 | ok, roundoff-dominated |
| 1e-7 | 52.88% | 51.68% | 0.948 | ok, roundoff-dominated |
| 1e-6 | 17.64% | 14.90% | 0.989 | ok, roundoff-dominated |
| 1e-5 | 12.27% | 5.24% | 0.993 | ok (1 transient container failure, retried) |
| 1e-4 | 11.52% | 2.99% | 0.993 | ok |
| **1e-3** | **11.43%** | **2.69%** | 0.993 | **ok — A1's original baseline, reproduced independently** |
| 5e-3 | 10.47% | 2.64% | 0.995 | ok |
| 1e-2 | 8.94% | 2.61% | 0.996 | ok |
| 2e-2 | 4.28% | 2.54% | 0.999 | ok — coincidental low point, see below |
| 3e-2 | 9.83% | 2.48% | 0.995 | ok |
| 5e-2 | — | — | — | **FAILED**: primal did not converge for idx6 (+step); residual stalled at 4.8e-5 vs 1e-8 tolerance |
| 1e-1 | — | — | — | **FAILED**: primal solution failed on the very first perturbed solve (idx0) |

- Adjoint recomputed fresh at every invocation; stable to 7+ significant figures throughout (not in question).
- `rel_err_pct_excl_idx0_1_6` = same metric with the three previously-flagged (PROOF.md) components dropped from both vectors.

## Curve shape

- **Full 8-vector norm: noisy / non-monotonic on the well-converged plateau, not a clean V.** From
  step=1e-3 down through 1e-4 it's flat-ish (11.4-11.5%); across 1e-3 to 3e-2 it wanders
  11.4% → 10.5% → 8.9% → **4.3%** → 9.8%, then the solver itself fails at 5e-2. Below 1e-4 it rises
  steeply and monotonically (11.5% → 17.6% → 52.9% → 95.0%) — that part *is* the textbook
  roundoff-noise V-branch.
- **The 4.28% dip at step=2e-2 is not a genuine minimum.** It is caused entirely by one component
  (idx6) whose FD estimate is sign-flipped and unstable at every other step, happening to cross near
  the adjoint's magnitude at that one step size before overshooting 2x at 3e-2 and breaking the
  primal solver outright at 5e-2. There is no step at which idx6 is a trustworthy estimate.
- **Excluding idx0, idx1, idx6: dead flat, 2.5-3.0%, at every step from 1e-4 to 3e-2**, cosine 0.99998
  throughout. This is the textbook "flat curve = real, step-independent agreement" signature for 5 of
  the 8 components — the harness and adjoint are sound there, matching the machine-precision
  geometric-constraint checks and the 0.23% flow-parameter checks already on record.
- **idx0 and idx1 individually: flat and step-independent, -8% to -16%, across 1e-6 to 3e-2.** A real
  step artifact shrinks toward zero somewhere in a 3-decade window; these don't.
- **idx6 individually: wrong sign and unstable across nearly the whole range** (-88% to -119% relative
  error from 1e-6 to 1e-2, a brief correct-order-of-magnitude crossing near 2e-2, +110% by 3e-2, then
  the solver fails to converge for this exact component at 5e-2).

## Verdict: is 11.43% a step-size artefact, or real?

**Predominantly real — the flat-curve branch, per component.** idx6 alone accounts for **82.7%** of the
squared-difference norm at A1's original step (an exact match to PROOF.md's independently-derived
82.7%), and its FD estimate never stabilizes at any step tested. idx0 and idx1 add another ~12% of the
squared-error norm and disagree by a stable ~9-16% across three decades of step size — not shrinking,
so not a step-size artifact by definition. This independently reconfirms PROOF.md's prior leading-edge
localization (idx0, idx1 near the LE; idx6 the LE combo mode) with a freshly-written script and a fresh
set of runs.

Cross-checks against PROOF.md's earlier, separately-run investigation (different script, same case):
squared-error contribution of idx6 at step=1e-3 — 82.70% here vs 82.7% there; cosine excluding
idx0/1/6 — 0.999983 here vs 0.999983 there; cosine including all 8 — 0.993451 here vs 0.993452 there.
Independent reproduction to 5-6 significant figures.

**A1's specific step choice (1e-3) was not itself the problem** — it sits inside the well-converged
plateau (1e-4 to 3e-2), not the roundoff-dominated regime. But the aggregate vector-norm percentage on
that plateau is a fragile statistic: it swings from 4.3% to 11.5% purely because of idx6's instability,
unrelated to step quality. The 5 well-behaved components are unaffected by step choice across that
entire window and agree to ~2.5-3.0%.

## Recommended FD step size

**1e-3 to 1e-2**, central, `step_calc=abs`. Below ~1e-4 the CD difference falls below the primal's
residual noise floor (`primalMinResTol=1e-8`) and FD degrades severely (11.5% → 95% from 1e-4 to
1e-8). Above ~3e-2 the leading-edge control point (idx6) pushes the primal solver into non-convergence
(documented failures at 5e-2 and 1e-1). A1's original 1e-3 was already inside this safe window.

## Recommended FD tolerance for grading future shape derivatives on this stack

Do **not** grade on the aggregate vector-norm percentage alone — it is provably fragile (4.3% to 11.5%
swing on the exact same well-converged plateau, same case, only step size changing). Recommended
protocol:

1. Confirm the step is in the well-converged plateau with a 2-3 point mini-sweep (not assumed).
2. Report per-component or cosine-similarity agreement alongside the aggregate percentage.
3. Flag any component whose FD value changes sign or moves by >50% of its own magnitude across one
   decade of step — that is the idx6 signature, diagnostic of a real defect, not noise.
4. For a case with **no flagged components**, this dataset's harness-sound floor is **2.5-5%**
   vector-norm relative error (2.5-3.0% here at 4032 cells; A2 independently achieved 1.71% at 38304
   cells / 96 DVs — consistent with the floor tightening on finer meshes).
5. Bands: **PASS ≤5%** with zero flagged components; **CONDITIONAL 5-15%**, requires a per-component
   breakdown before grading; **>15% or any flagged component → FAIL pending investigation**, regardless
   of the aggregate percentage.

The previous 1-12% band (inferred from A1 alone, n=1) is retired: its sole supporting data point is now
shown to conflate a genuine ~2.5-3% harness-sound floor, an 83%-idx6-driven sign-flip defect, and a
stable ~10-16% two-component bias into one misleading aggregate number.

## Should A4's 10.04% still read as a PASS?

**No — downgrade to CONDITIONAL / UNVERIFIED, not FAIL.** A4 was not itself step-swept here or
previously; nothing in this probe proves A4's adjoint is wrong. But: A4 has a single scalar shape DV,
so it cannot exhibit A1's vector-norm dilution effect (there's no "one bad component hides among eight"
dynamic possible with n=1). A4's 10.04% is therefore a raw, undiluted single-component disagreement —
and in the one case examined in this detail (A1), a *single* component (idx0 or idx1) legitimately
carries a real, step-independent ~9-16% disagreement that no step-size choice resolves. A4's number
sits in that same range, not in the ~2.5-5% harness-sound floor this probe established. The sole basis
for A4's original PASS (the now-retired 1-12% band) no longer supports it. Recommended next action: run
this identical step-sweep protocol (1e-3, 1e-2, plus a roundoff check at 1e-5 and a large-step check
around 3e-2) directly on A4 before re-confirming or reversing its verdict.

## Failures recorded honestly (hard rule: never fabricate)

- **step=1e-5, first attempt**: container exited 1 partway through (~19s in, during idx0/idx1 perturbed
  solves). No OOM signature in `dmesg`/docker events; likely a transient container/mesh-redecompose
  race. Retried once with an identical command; the retry completed cleanly and its result is what's
  used in the table. The failed attempt's log is kept on disk, unused for any number.
- **step=5e-2**: genuine solver failure. idx0-idx5 converged and are recorded; the +step solve for idx6
  stalled at residual 4.8e-5 (vs the 1e-8 tolerance) and hit the 1000-iteration cap, so DAFoam raised
  `AnalysisError('Primal solution failed!')`. idx6, idx7 not obtained at this step — not estimated, not
  filled in.
- **step=1e-1**: genuine solver failure on the very first perturbed solve (idx0, +step). Not swept
  further at this step size.

## Compliance with the process rules

- All 12 step invocations ran in the foreground, MPI capped at 2 ranks, `--network=host --memory=4g`
  (never raised).
- `sudo rm -rf processor0 processor1 processor*` was run before every single invocation (known trap).
- Only the `-step` argument varied across runs; `daOptions`, mesh, MPI rank count, `primalMinResTol`,
  and the FFD/DV setup are byte-identical to A1's own `runScript.py` in every run.
- All docker containers exited (`--rm`); verified zero running containers at the end
  (`docker ps -a` empty of this probe's containers). `processor0`/`processor1` removed after the final
  run — nothing left running.
- Commit is local only; not pushed.
