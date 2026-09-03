# PRE-REGISTRATION — VMFL046-INVISCID (the decisive Euler/inviscid arm of the CD-nozzle shock)

**DRAFT by `ansys-lane-opus48`. NOT FROZEN, NOT COMMITTED, no solver run, no queue entry filed.**
The supervisor does `SUPERVISION_CHARTER` §3 check 4 (pre-registration committed before compute)
personally, freezes it, and queues it.

- **What this is:** a NEW registration that runs the **inviscid (Euler) arm** of VMFL046's
  converging–diverging nozzle to answer the open hypothesis charter **§24.7** records —
  *"the decisive inviscid/Euler comparison has not been run."* It is a controlled experiment:
  the frozen viscous VMFL046 case with viscosity removed and nothing else changed.
- **It does NOT re-grade VMFL046.** Row #54's `GATE FAIL` is permanent (§24.7); this is a
  separate case with its own verdict.
- **Prediction-first, frozen before compute (rule 2), under Sanaa's launch rule of 2026-09-03
  ~21:00Z** (`etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md`, read verbatim): *"A
  pre-registration mismatch never prevents a launch. It's recorded as a prediction, the run
  launches under the monitor, and the outcome is compared to the prediction… Pre-registration
  predicts; the monitor watches; the grader judges afterward."* Accordingly the risk lines in §9
  are **predictions to be tested, not reasons to cap or wait**; the freeze-before-compute
  requirement is unchanged (this document IS the prediction being tested), and the frozen grader
  applies every gate **afterward**, on evidence.

---

## 1. The question §24.7 leaves open

The viscous VMFL046 shock location moves **upstream** of the analytical inviscid prediction and
**drifts further with mesh refinement** (`RESULTS.md` §1.1):

| level | cells | viscous `x_shock` (m) | dev. from analytical 1.250 |
|---|---|---|---|
| L1 | 3 200 | 1.257629 | +0.610 % |
| L2 | 12 800 | 1.192596 | −4.592 % |
| L3 | 51 200 | 1.152576 | −7.794 % |
| grid-converged | — | **1.0885** | **−12.92 %** |

The register row #54 and §24.7 state the −12.92 % as an **open hypothesis**: that viscous
stagnation-pressure loss through the diverging section moves the shock upstream of the inviscid
analytical 1.250. **This arm is the decisive test.** Remove viscosity; see where the shock lands.

## 2. THE PREDICTION — committed numerically BEFORE the run

**I predict the inviscid CFD grid-converged shock lands NEAR the analytical 1.250 and FAR from
the viscous 1.0885 — specifically `x_shock(inviscid, grid-converged) ∈ [1.19, 1.31]` (within the
frozen 5 % band of 1.250).** And I predict the inviscid triple is **mesh-stable** (small drift),
in contrast to the viscous upstream drift, because the drift's hypothesized cause (a boundary
layer / stagnation-pressure loss that resolves better at finer mesh) is **absent** in an inviscid
solve. The pre-shock station Mach `M(0.9)` is isentropic (upstream of the shock) and I predict it
reproduces the analytical **1.882125** in both viscous and inviscid solves — so the δ_M plateau
(§5) applies identically.

**The three outcomes, each committed with its meaning:**

- **A — inviscid ≈ 1.250 (within 5 %, x ∈ [1.1875, 1.3125]).** Hypothesis **CONFIRMED**: the
  viscous −12.92 % is real viscous physics (stagnation-pressure loss). The viscous `GATE FAIL` is
  vindicated as a genuine model-form/physics difference, not a defect. The inviscid arm **passes
  its own gate** (shock vs analytical ≤ 5 %) → a solver-verification credential. **This is the
  expected outcome.**
- **B — inviscid ≈ 1.0885 (drifts upstream like the viscous).** Hypothesis **REFUTED**: the
  displacement is NOT viscous — it is a setup or discretisation defect (contour, back-pressure,
  or a numerical issue) shared by both solves. This is the **more serious** finding: it would put
  VMFL046's `GATE FAIL` in a different light (a defect, not physics) and is **escalated**, not
  quietly absorbed.
- **C — neither (some other x, or no steady shock / plateau not met).** Recorded as the prediction
  outcome per the launch rule (§9); the shock location is still read diagnostically from whatever
  the run produces.

**The diagnostic payoff, regardless of the verdict:** the viscous-minus-inviscid grid-converged
shock gap, `1.0885 − x_shock(inviscid)`. If inviscid ≈ 1.250 the gap ≈ −0.16 m, which is the
viscous displacement isolated — the mechanism quantified.

## 3. §12.2 MODEL-SAMENESS — RULED **SAME**, and it is the cleanest sameness claim in this territory

The reference (`quasi1d_reference.py`, frozen) solves the **quasi-1D inviscid Euler** equations
(isentropic branches + normal-shock jump) for γ = 1.4, R = 287, the frozen contour's area
distribution, P0 = 301325 Pa, Pexit = 176325 Pa. The inviscid CFD solves the **2-D Euler**
equations (rhoSimpleFoam, μ = 0, slip walls, adiabatic since κ = μ·Cp/Pr = 0) for the **same** γ,
R, contour, P0, Pexit, perfectGas EOS.

> **RULED SAME.** Both sides solve the *same* governing equations (inviscid compressible Euler,
> same gas, same EOS, same boundary conditions). The only differences are **dimensionality** (2-D
> CFD vs the quasi-1D area-averaged limit of the *same* equations — a resolution difference within
> the model, not a model-form difference) and **discretisation** (a captured shock a few cells wide
> vs a sharp jump — the §23.4 shock-width bound, which refines away).

**Why this is cleaner than the viscous case, which is the whole point of the arm:** the viscous
VMFL046 compared viscous Navier–Stokes CFD against an **inviscid** Euler reference — a genuine
model-form difference (viscosity present in one, absent in the other), and that difference *is* the
−12.92 %. Its sameness was contentious (§21.2 ruled DIFFERENT → capped at `GATE REACHED`; §23.3
promoted it under a bounded-channel argument that §24 then largely refuted). **Here viscosity is
absent from BOTH sides, so there is no model-form difference to bound — the sameness is exact up to
dimensionality and discretisation.** Therefore **`PASS` is available** (credential-grade), and the
primary gate can yield a genuine `PASS`, not a capped `GATE REACHED`.

## 4. THE GATE, BAND, AND GRADING PATH (frozen) — the frozen VMFL046 grader, reused unchanged

**Grading path:** `cases/ansys_verification/VMFL046/grade_vmfl046.py`, blob
**`cbe98dc821cdbeaba0c27363117b65b7ee199dcf`** (verified == HEAD), run on the inviscid run root.
It is reused **unchanged** because the inviscid arm uses the **same solver** (rhoSimpleFoam → same
`log.rhoSimpleFoam`), the **same fields** (`U T p`), the **same contour/BCs**, the **same
first-order scheme**, and the **same analytical reference** (`quasi1d_reference.py`, inviscid
shock 1.250) — which is *exactly* the right reference for an inviscid CFD solve. No new comparator
is written; a frozen, already-audited one grades this arm.

- **PRIMARY limb (credential-capable under §3 SAME):** grid-converged shock location vs the
  analytical 1.250, `|x_shock − 1.250| / 1.250 ≤ SHOCK_TOL = 0.05` (5 %), on a **CONVERGING**
  Roache triple (rule 5), with the M(0.9) plateau (§5) met at every level. This is the grader's
  frozen primary (`SHOCK_TOL = 0.05`).
- **Verdict vocabulary (grader-emitted):** `PASS` (CONVERGING triple + shock ≤ 5 % + plateau met +
  secondaries not demoting) / `GATE FAIL` / `NOT A RESULT` (triple not CONVERGING, or plateau not
  met, or a control refuses). Secondaries (`p` in [0.5, 2.5], GCI ≤ 15 %, Mdev ≤ 10 %) are
  **demote-only** (§21.3), unchanged.
- **Credential vs diagnostic (honest framing):** under the SAME ruling this arm **is
  credential-capable** — a `PASS` here is a legitimate solver-verification credential (2-D Euler
  reproduces the analytical CD-nozzle shock). But its **scientific purpose is diagnostic**
  (resolve §24.7). If the primary cannot produce a credential (plateau fails, or the triple is not
  CONVERGING → `NOT A RESULT`), the **diagnostic reading still stands**: the shock location the run
  produces answers the mechanism question, and is reported beside the verdict. It is registered as
  a credential-capable gate with an honest diagnostic floor, not dressed as a gate it cannot meet.

## 5. CONVERGENCE / PLATEAU (frozen a-priori) — δ_M = 4.25e-4, W = 500, reused and justified

The grader's convergence criterion is the **M(0.9) plateau**: `|M(0.9)_last − M(0.9)_{last−W}| <
δ_M` over `W = 500` iterations, with `δ_M = 4.25e-4` Mach (§22.5). **Reused unchanged**, and it is
*more* appropriate here than for the viscous case: δ_M was set from §18's reference-reproduction
spread `|1.882125 − 1.8817|` at M(0.9), and M(0.9) is the **pre-shock, supersonic, isentropic**
Mach — a quantity the inviscid CFD reproduces by construction (it is inviscid/isentropic upstream
of the shock). Iteration noise below the reference's own uncertainty cannot move a verdict that
compares to it, viscous or inviscid.

- **Binding including if it fails.** If any level's M(0.9) does not plateau within δ_M over W, the
  grader returns **`NOT A RESULT`** (no loosened floor).
- **Fallback, pre-committed:** on plateau failure the verdict is `NOT A RESULT` and the shock
  location is read **diagnostically** from the last sample (it still answers §24.7's mechanism
  question); **no re-run with a loosened floor**. A dedicated local-time-stepping (LTS) arm is
  future work, not an automatic escalation of this run.

## 6. SOLVER CHOICE — rhoSimpleFoam with μ = 0 (+ slip walls), argued; NOT rhoCentralFoam

**Chosen: rhoSimpleFoam with μ = 0 and slip walls.** Reasons:

1. **It is the exact controlled experiment.** Only viscosity changes from the frozen viscous
   VMFL046 (μ = 1.7894e-5 → 0; no-slip → slip walls, required for a well-posed Euler wall). Same
   steady solver, same first-order upwind (whose numerical dissipation captures the shock, as in
   the viscous run), same mesh, same contour, same P0/Pexit, same endTime. The −12.92 % hypothesis
   is precisely *"viscosity moves the shock"*; setting μ = 0 in the same solver is that hypothesis's
   one-variable test.
2. **It preserves the frozen grader** (`log.rhoSimpleFoam`, fields `U T p`, same reference) — a
   frozen audited comparator grades it unchanged (§4).

**Rejected: rhoCentralFoam** (the density-based shock-capturing solver used by VMFL045/VMFL051).
Changing the solver would **confound** the comparison — any inviscid-vs-viscous shock difference
could then be solver-vs-solver rather than viscosity — and would **break grader reuse** (different
log, different numerics). Per the launch rule a solver change would be *recorded as a prediction*,
but recording it does not remove the confound; the controlled experiment is strictly better served
by μ = 0 in the same solver.

**The two changes, exactly (everything else byte-identical to the frozen VMFL046 `case/`):**
1. `constant/thermophysicalProperties`: `mu 1.7894e-05` → **`mu 0.0`** (Pr unchanged; with μ = 0,
   κ = μ·Cp/Pr = 0 → adiabatic Euler, the correct inviscid limit).
2. `0/U` boundaryField `wall`: `type noSlip;` → **`type slip;`** (the physically correct Euler wall;
   a no-slip wall with μ = 0 is degenerate — no viscous stress to enforce it).

Mesh (`blockMeshDict.template`, NXA/NXB/NY → 3200/12800/51200), contour, P0/Pexit, `fvSchemes`
(first-order upwind), `fvSolution`, `controlDict.template` (endTime 20000), the centreline
`postProcessing` sampler (every W = 500), and `momentumTransport` (laminar) are **UNCHANGED**.

**To be built with this registration (two-line change + a driver), on the supervisor's go-ahead —
NOT built or run here:** `cases/ansys_verification/VMFL046/INVISCID/case/` (the VMFL046 `case/`
with the two changes above) and `INVISCID/run_vmfl046_inviscid.sh` (modelled on
`run_vmfl046.sh`: same NXA/NXB/NY, `ENDTIME 20000`, `RANKS 1`, `CAP_CORE_MIN 84`, run root
`verification/runs/ansys_verification/VMFL046_INVISCID/`, the same HEAD-blob input-integrity
check and rule-4 age guard).

## 7. COST — filed, capped at ~3×, reconciled against its own method (§26.2, §26.3, §27.3)

- **Filed estimate: 28 core-min.** **Cap: 84 core-min** (~3× per §26.2; the driver's running-total
  `CAP_CORE_MIN`). An overrun stops the run (rule 12); the fleet safety ceiling (min(3× cap,
  remaining box budget), Sanaa's launch rule) is the hard structural stop.
- **§27.3 reconciliation — filing-time inputs only, re-priced for every config choice this
  registration makes:** the apples-to-apples basis is the **measured viscous run — same solver,
  same meshes, same 20 000 iterations**: L1 57 s / L2 310 s / L3 1316 s = 1683 s = **28.05
  core-min** (RANKS = 1, from `launcher.queue.out`). The inviscid arm keeps the mesh, iteration
  count (endTime 20000) and solver, and removes the viscous-stress assembly + laminar transport.
  - **The inviscid per-iteration saving is NOT priced from cfd's 0.70 µs vs 1.03 µs figure — that
    ratio is `rhoCentralFoam` (density-based), and this arm is `rhoSimpleFoam` (pressure-based),
    where the pressure Poisson solve dominates and the viscous-assembly saving is a smaller
    fraction.** No measured inviscid figure exists for rhoSimpleFoam, so the filed estimate applies
    **no unmeasured saving** (factor 1.0): filed 28 core-min = the measured viscous total, the
    safe direction (§27's lesson: do not under-file).
  - **This is itself a prediction to be tested (the launch rule's payoff):** I predict the actual
    inviscid cost comes in at **0.85–1.0× the viscous, i.e. 24–28 core-min**, and this run
    **measures** the rhoSimpleFoam inviscid/viscous per-iteration ratio for the first time — a
    calibration datum, recorded predicted-vs-actual on the certificate.
  - Conditioning caveat (a cost prediction, not a cap): μ = 0 changes the momentum-equation
    conditioning; if the pressure solve needs more inner iterations the cost could approach the
    cap. Recorded as a prediction; the cap and fleet ceiling bound it.
- **Dollars (derived, not measured):** estimate 28 core-min = 0.4667 core-h × $0.0513 =
  **$0.02394**; cap 84 core-min = **$0.07182**. Derived at $0.0513/core-h, c7a.4xlarge,
  reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Estimate-vs-actual (rule 12):** at completion, actual core-min from `launcher.queue.out` × 1
  core vs the filed 28, ratio + attribution → `docs/COST_CALIBRATION.md`; the inviscid/viscous
  per-iteration ratio is the headline calibration output.

## 8. WHAT THIS DOES NOT DO

It does **not** re-grade VMFL046 (#54's `GATE FAIL` is permanent, §24.7). It does **not** touch the
frozen VMFL046 `case/`, grader, or reference (all reused read-only / copied). It does **not** claim
the mechanism before the run — it *tests* the §24.7 hypothesis and commits its prediction in §2.

## 9. RISK / PREDICTION LINES (launch rule: recorded as predictions, launched, graded afterward)

Per Sanaa's 2026-09-03 rule, these are **predictions on the certificate, not reasons to cap or
wait** (none is a physically ill-posed setup — the CD-nozzle Euler problem with fixed back-pressure
is well-posed with an outlet and consistent BCs; only a resource gate would queue):

1. **The inviscid steady shock may limit-cycle** (no physical dissipation, only first-order
   upwind). Predicted: M(0.9) (pre-shock, isentropic) **plateaus** (stable); the shock cell may
   oscillate ±1 cell. If M(0.9) does not plateau → `NOT A RESULT`, shock read diagnostically.
2. **The shock may sit at a location other than 1.250 or 1.0885** (outcome C, §2) — recorded, not
   blocked.
3. **Cost may reach 0.85–1.0× viscous (24–28 core-min)** — a cost prediction; the run measures the
   inviscid/viscous rhoSimpleFoam ratio.
4. **Slip walls change the near-wall flow** vs the viscous no-slip case — this is the intended
   model change (viscous → inviscid), recorded as such, not a defect.
5. **First-order upwind smears the shock** over a few cells — the §23.4 width bound (≪ 5 % band,
   refines away); the Roache triple + plateau are the guards.

---

### Freeze checklist (supervisor)

1. Read this registration; confirm the §2 prediction, §3 SAME ruling, §4 grader reuse, §7 cost/cap.
2. Approve the two-line case change (§6); the case/ + driver are built to spec and their blobs
   recorded (they are part of the frozen set).
3. Verify the grader blob is still `cbe98dc8…` at freeze; hash the case inputs and the driver.
4. Commit this file (+ the built case/ + driver) via the rule-10 private-index protocol; record
   the freeze sha; do §3 check 4 personally.
5. Queue the run (run root `verification/runs/ansys_verification/VMFL046_INVISCID/`); the monitor
   watches; the frozen grader `grade_vmfl046.py` judges afterward; predicted-vs-actual (shock
   location AND cost ratio) lands on the certificate.
