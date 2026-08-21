# PREREGISTRATION — Shelf-D eigenspace machinery (Part A) + NASA hump equivalence gate (Part B)

Written and posted before any solve and before any envelope number was computed.
Lane cap **10 core-hours**. Verdicts from {PASS, GATE REACHED, GATE FAIL,
NOT A RESULT, BLOCKED, PENDING}.

Zero-shot discipline: **the only contact with a test-family case in this lane is
the hump equivalence gate of Part B, and that contact is gate-only** — a
solver-behaviour comparison against the shipped baseline, with no model fitted, no
correction injected and no quantity carried forward into any other lane. Part A
touches **training-family cases only**.

---

# PART A — eigenspace perturbation machinery (shelf D)

## A.1 Sources, cited from the files on disk

* **Emory, Larsson & Iaccarino**, *Modeling of structural uncertainties in
  Reynolds-averaged Navier-Stokes closures*, **Phys. Fluids 25, 110822 (2013)**.
  On disk: `docs/papers/closure/Emory2013_structural_uncertainty_rans.pdf`,
  published article, title page checked.
  * **eq. (4), p. 110822-5**: `R_ij = 2k (delta_ij/3 + v_in Lambda_nl v_jl)`,
    with `v` and `Lambda` ordered so that `lambda_1 >= lambda_2 >= lambda_3`.
  * **eq. (5), p. 110822-5**: `x = x_1c (l1 - l2) + x_2c (2 l2 - 2 l3) + x_3c (3 l3 + 1)`,
    an invertible linear map written `x = B lambda`. Realisability <=> `x` inside
    the triangle.
  * **eq. (7), p. 110822-6**: `x* = x + Delta_B (x^(t) - x)`, where `Delta_B` is
    the **relative distance** of movement toward target corner
    `x^(t) in {x_1c, x_2c, x_3c}` and `x` is the base-model prediction.
  * **eq. (8a), p. 110822-6**: `lambda* = B^{-1} x*`.
  * **Naming note, because the paper reuses one symbol for two objects:** `B` is
    both the perturbation magnitude (eqs. 7 and Sec. IV) and the linear map matrix
    (eq. 5). The code calls the scalar `delta_B` and the matrix `M`.
* **Iaccarino, Mishra & Ghili**, *Eigenspace perturbations for uncertainty
  estimation of single-point turbulence closures*, **Phys. Rev. Fluids 2, 024605
  (2017)**. On disk: `docs/papers/closure/Iaccarino2017_eigenspace_perturbations.pdf`,
  the **accepted manuscript via CHORUS**, so equation and page numbers may differ
  from the journal of record and are quoted as manuscript numbering.
  * **eq. (3)**: `<A,R>_F in [l1 g3 + l2 g2 + l3 g1, l1 g1 + l2 g2 + l3 g3]`,
    where `g1 >= g2 >= g3` are the eigenvalues of the symmetric part of `A`, i.e.
    the mean rate of strain.
  * The paragraph after eq. (3): in the coordinate system of the strain
    eigenvectors, the bounding alignments are
    `v_min = [[0,0,1],[0,1,0],[1,0,0]]` and `v_max = [[1,0,0],[0,1,0],[0,0,1]]`.
  * The paragraph before Sec. III: **"we need a set of only 5 RANS simulations"** —
    3 componentiality limits (1C, 2C, 3C) and 2 extremal alignments
    (`v_min`, `v_max`), with 3C degenerate under rotation because its ellipsoid is
    spherical. **The five states are `{1C, 2C} x {v_min, v_max}` plus `3C`.**

## A.2 What is built

`cases/RANS_LES_closure_models/_common/uq_eigenspace/eigenspace.py`, importable
by the BUILD lane, exposing:

| function | contract |
|---|---|
| `barycentric_coords(b)` | eq. (5) forward map, returns `(x, y)` and sorted `lambda` |
| `perturb_eigenvalues(b, target, delta_B)` | eq. (7) then eq. (8a); `target in {"1C","2C","3C"}` |
| `permute_eigenvectors(b, gradU, which)` | Iaccarino alignment, `which in {"vmin","vmax","base"}`, applied **in the strain-eigenvector frame** |
| `five_states(b, gradU, delta_B)` | the five extremal states, in the paper's own order |
| `envelope(quantity_fn, states)` | per-cell `[min, max]` over the states |

Realisability is preserved by construction: eq. (7) is a convex move toward a
corner of a triangle whose interior is exactly the realisable set, so
`delta_B in [0,1]` cannot leave it. The implementation asserts this and reports
any violation as an implementation defect, not a finding.

## A.3 THE REGISTERED QUESTION — first deliverable, a-priori, frozen fields

> **Does the LES/DNS truth lie inside the eigenspace envelope?** Per case, per
> quantity, as a fraction of cells — closing the loop L-157 left open, which is
> that Xiao et al.'s own uncertainty space provably excludes the truth because it
> never perturbs orientation. The eigenspace method *does* perturb orientation.
> If its envelope also excludes the truth, then neither published uncertainty
> framework on this shelf contains the thing it is meant to bound.

**Cases (TRAINING family only, frozen shipped fields, no solve):**
`PHLL10595`, `CBFS13700`, `AR_1_Ret_180`, `AR_3_Ret_180`, and four hills
spanning the geometry axis — `alpha_10_9000_3036` (standard), `alpha_05_7071_3036`,
`alpha_15_10929_3036`, `alpha_125`. **Eight cases. No TEST case, no hump.**

**Quantity 1 — anisotropy shape (`b` eigenvalues).** Coverage = fraction of
masked-valid cells whose truth barycentric point `x_LES` lies inside the convex
hull of the five perturbed states' barycentric points, at each
`delta_B in {0.25, 0.50, 0.75, 1.00}`. Reported as a ladder, because the
interesting number is **how large a perturbation magnitude is required**, which is
Emory's own Sec. IV question (p. 110822-12: they deduce `B` from DNS by minimising
the barycentric distance to the perturbed state).

**Quantity 1b — the required magnitude, per cell.** `delta_B_req` = the smallest
`delta_B` at which the truth is contained, computed directly rather than by
laddering. Reported as median, p95 and the fraction needing `delta_B > 1`
(i.e. never contained). This is the sharpest form of the registered question.

**Quantity 2 — momentum-forcing proxy.** Turbulence production
`P_k = - R_ij dU_i/dx_j`, the quantity Iaccarino's eq. (3) bounds and the term
through which the Reynolds stress actually forces the momentum equation. Envelope
= per-cell `[min, max]` of `P_k` over the five states at each `delta_B`; coverage
= fraction of cells with `P_k^LES` inside it. `R` is reconstructed with the
**RANS `k`** in all five states (the perturbation is of shape and orientation, not
magnitude — Emory eq. 4 keeps `k` outside the bracket), and this is stated because
it bounds what the envelope can contain: **a `k`-magnitude error is outside the
eigenspace envelope by construction.**

**Registered predictions, before computing anything:**

* **P-A1:** shape coverage at `delta_B = 1.0` is **>= 0.95** on every case. At
  `delta_B = 1` the three eigenvalue states are the triangle corners, so the hull
  is the whole realisable set and the only cells that can fail are those where the
  **truth itself is unrealisable** — `BASELINES.md` §5 measures that at 0.0000 to
  0.0246 per case. A number materially below 0.95 means the implementation is
  wrong, not that the method is.
* **P-A2:** production coverage at `delta_B = 1.0` is **< 0.95** on at least one
  case, because `k` is not perturbed. Falsified if every case exceeds 0.95.
* **P-A3:** median `delta_B_req` for shape lies in **[0.2, 0.8]**. Emory's own
  DNS-deduced magnitudes are O(0.5). Falsified outside that band.

**Verdicts.** This deliverable answers a question; it does not grade a method.
Each prediction P-A1..P-A3 gets PASS or GATE FAIL against the band above. The
envelope-coverage fractions themselves are **reported, not graded** — they are the
measurement L-157 asked for.

## A.4 OPTIONAL Part A.4 — five-perturbation re-solves, only if under cap

Registered **before** any solve so the coverage question is not chosen after
seeing the a-priori answer:

* One training hill, `alpha_10_9000_3036`, five re-solves (`1C`,`2C`,`3C` x the
  registered alignments) at `delta_B = 1.0` through the **validated injection
  path** (`kOmegaSSTCorrected` with `bijDelta` from the perturbed `b` and
  `kDeficit = 0`, the interface proved bit-identical to stock at zero correction).
* **Registered question:** what fraction of cells have `U_LES` inside the
  per-cell `[min, max]` envelope of the five re-solved velocity fields?
* **Registered prediction P-A4:** velocity coverage **< 0.50**. Reason stated in
  advance: the injection path holds `k` fixed at the RANS value and transports it,
  and the Kaandorp lane measured that a b-only injection with transported `k`
  collapses `k` to 0.33x and cannot carry even the truth. An envelope built on
  that path is expected to be too narrow and mis-centred. **If P-A4 is falsified
  (coverage >= 0.50) that is a positive surprise and is reported as such.**
* **Skipped and recorded as PENDING if the lane is within 2 core-hours of the
  10-core-hour cap when Part B finishes.**

---

# PART B — NASA hump equivalence gate

## B.1 The finding this gate tests

`/home/ubuntu/closure-challenge-benchmark/data/NASA_2DWMH/log.run` selects
**`AugmentedkOmegaSST`** and prints its coefficient dictionary, verified by
reading the file:

```
RASModel AugmentedkOmegaSST;  turbulence on;  omegaMin 0.1;  baseline true;
alphaK1 0.85; alphaK2 1; alphaOmega1 0.5; alphaOmega2 0.856;
gamma1 0.555556; gamma2 0.44; beta1 0.075; beta2 0.0828; betaStar 0.09;
a1 0.31; b1 1; c1 10; F3 false;
usekDeficit false; usebijDelta false; useSigma false;
modelbijDelta false; modelkDeficit false; modelSigma false;
bijDeltastabilizer 1; kDeficitstabilizer 1;
rampStartTime 0; rampEndTime 100; xi_ramp 1;
```

Every coefficient is the stock Menter SST value and **every augmentation flag is
false with `baseline true`**. The source is private, so equivalence to stock
`kOmegaSST` can only be established **behaviourally**. That is what this gate does.

**Two features of the shipped case that the gate must carry, found by reading and
recorded now:** `omegaMin 0.1` (not the stock default) and an active `fvOptions`
`limitVelocity` source on all 51,626 cells. The shipped run was also **parallel**
(`log.decomposePar`, `log.reconstructPar`); this gate runs **serial**, a disclosed
departure.

**`libs` handling, per the operational lesson from the Xiao lane:** the hump
`controlDict` **does** carry `libs ( "libfrozenIncompressibleTurbulenceModels.so" );`
— unlike the 29 parametric hills, which carry none. That library does not exist on
this machine. The gate therefore **rewrites the `libs` list to name
`libspartaTurbulenceModels.so` and asserts the result contains it**; it never
relies on a string-replace succeeding silently.

## B.2 The gate, two parts (the G0a / G0b form, as the shipped-field-drift lesson requires)

* **B-G0a — fixed-iteration behavioural equivalence.** Restart from the shipped
  converged field `2000/` and run **200 iterations** twice: once with the shipped
  `AugmentedkOmegaSST` dictionary as-is, once with `kOmegaSSTCorrected`
  (`bijDelta = 0`, `kDeficit = 0`, `omegaMin 0.1`, same `fvOptions`).
  **PASS iff relative L2 difference in `U` < 1e-6.**
  Band justification: `kOmegaSSTCorrected(0,0)` was measured **bit-identical**
  (rel-L2 = 0.0) to stock `kOmegaSST` on `AR_1_Ret_360`, so any difference here
  is `AugmentedkOmegaSST` not being stock. 1e-6 rather than 0 allows for
  `omegaMin` handling differing between the two implementations while still being
  four orders below anything physically meaningful.
  **If the shipped model cannot be selected at all on this machine** (its library
  is absent), B-G0a is **BLOCKED**, not failed, and B-G0b alone decides.
* **B-G0b — converged NULL against the published row.** Run
  `kOmegaSSTCorrected(0,0)` to the registered stopping rule and compare `U_rms`
  against `BASELINES.md` §3, `NASA_2DWMH`: **`U_rms` = 0.1260**, `U_mae` = 0.0620.
  **PASS iff |`U_rms` - 0.1260| < 5e-3.**
  Band justification, stated before running: the same test on `AR_1_Ret_360` gave
  2.4e-4 and on `AR_3_Ret_360` gave 1.92e-3 and **failed** a 1e-3 band purely
  through drift of the shipped field under further iteration. The hump is 3.3x
  larger and has an active velocity limiter, so 1e-3 would be a band about the
  shipped field's convergence, not about model equivalence. 5e-3 is 4 % of the
  quantity and is registered as such.
* **Stopping rule:** `residualControl` `p` and `U` at 1e-6, hard cap **5,000
  iterations**, in-script `timeout` 1800 s. Convergence state reported per the
  Kaandorp lane's vocabulary (`CONVERGED-residualControl` /
  `CONVERGED-stagnation` / `CAPPED-NOT-CONVERGED` / `DIVERGED`).

## B.3 Decision rule, verbatim and binding

> **Both parts PASS (or B-G0a BLOCKED and B-G0b PASS)** -> the hump row becomes
> **scorable comparably** through the `kOmegaSSTCorrected` path, and dated
> appended notes are written to `_common/FEASIBILITY.md` and to the BLOCKED-hump
> lines of `Wu2018_PIML_RF/aposteriori/RESULTS.md`,
> `Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md` and
> `Xiao2016_EnKF/RESULTS.md`, citing `log.run`'s coefficient dictionary.
> **Appended dated notes only — no edit of frozen text anywhere.**
>
> **Either part FAILS** -> the hump **stays BLOCKED** and the failure numbers are
> the record. No note claiming unblockability is written.

## B.4 What this gate CANNOT see

* **It cannot inspect the source.** `AugmentedkOmegaSST` is private; equivalence
  is behavioural on one case, over one restart, at one operating point.
* **A pass shows the two models agree at zero augmentation on this case.** It does
  not show they agree anywhere else, nor that the shipped baseline field was
  produced by the code path this machine runs.
* **Serial versus the shipped parallel run**, and this machine's OpenFOAM v2606
  against the case's OpenFOAM-7-era provenance (`log.run` header paths).
* **The `limitVelocity` `fvOptions` source is active** and is carried unchanged;
  if it is doing work, both sides of the comparison inherit it, which is what
  makes the comparison fair and also what makes it blind to the limiter itself.
* **No LES/DNS quantity other than `U_rms`/`U_mae` is touched**, and nothing from
  the hump enters any other lane's fit. Gate-only, as registered.

## B.5 Compute

Hump = 51,626 cells. Measured elsewhere on this machine: ~0.126 s/iteration at
21,000 cells, so ~0.31 s/iteration here. B-G0a = 2 x 200 iterations ~ 0.03
core-hours. B-G0b <= 5,000 iterations ~ 0.43 core-hours. Part A is pure numpy on
frozen fields, minutes. Part A.4 if run: 5 x <= 5,000 iterations on a 15,600-cell
hill ~ 0.7 core-hours. **Lane total estimate 1.2 core-hours against a 10-core-hour
cap.**
