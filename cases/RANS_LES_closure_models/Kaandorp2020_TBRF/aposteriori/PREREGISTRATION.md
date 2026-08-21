# PREREGISTRATION — a-posteriori re-solve of the TBRF anisotropy correction

**Written before any scored solve.** The only solver runs that preceded this file
are two 5-iteration **interface checks** with all corrections set to zero
(sec. 2.1); they establish that the solver starts and reads its fields, and they
produce no scored quantity.

Lane 1 of two, 2026-08-21. Parent record: `../RESULTS.md` (the a-priori TBRF
reproduction) and `../PREREGISTRATION.md`.

* Charter clauses this test exists to satisfy: **§22.2** (corrections live inside
  the solved equations), **§7** (RMS `div(U)` reported), **§2** (an a-priori score
  alone is NOT A RESULT), **§3/2c** (the trivial comparator).
* Solver: `kOmegaSSTCorrected` from `sdk/openfoam/sparta/spartaTurbulenceModels`,
  the model used by the W2 SpaRTA propagations
  (`verification/campaign/W2_SPARTA_FROZEN_CBFS.md`, validated there against an
  independent Python implementation and sign-verified by controlled experiment).
  **No new solver is written.** Nothing under `sdk/` or the benchmark clone is
  modified; every case is copied to
  `/home/ubuntu/closure-data/aposteriori/kaandorp/<case>__<label>/` first.
* OpenFOAM v2606, `/usr/lib/openfoam/openfoam2606`. Library
  `libspartaTurbulenceModels.so` already compiled in `FOAM_USER_LIBBIN`.

---

## 1. This is a VARIANT of a VARIANT — said once, plainly

The forest injected here is the **POST-HOC, D2-removed** configuration of
`../RESULTS.md` §6, not the preregistered one. That configuration was itself run
after seeing the preregistered result and carries no a-priori verdict; its
a-priori number on the primary case is `b_rms_F` = **0.3160 ± 0.0080**. The
a-priori reproduction was already a labelled VARIANT of Kaandorp & Dwight (wrong
duct, wrong Reynolds number, one of three training flows missing). **So the
verdicts below are verdicts about this variant's propagation behaviour and about
nothing in the paper.** Kaandorp's Table 4 remains BLOCKED-ON-DATA.

---

## 2. The mechanism, registered exactly

### 2.1 Interface, verified before this file was written

`kOmegaSSTCorrected` `MUST_READ`s two static fields at start-up. **Read from the
source, not from a summary:** they are named **`kDeficit`** (volScalarField,
`[0 2 -3 0 0 0 0]`) and **`bijDelta`** (volSymmTensorField, dimensionless). A peer
message described the first as `R`; the identifier in
`kOmegaSSTCorrected.C` is `kDeficit_` with `IOobject("kDeficit", ...)`, and the
runs below use that name. It carries the coefficient `RScale_` in the equations,
which is why "R" is the right *physics* name and the wrong *file* name.

Two 5-iteration checks with `kDeficit = 0` and `bijDelta = 0` completed cleanly:

| case | cells | result | cost |
|---|---|---|---|
| `AR_1_Ret_360` | 3,025 | `Selecting RAS turbulence model kOmegaSSTCorrected`, 5 iterations, `End` | 0.10 s |
| `CBFS13700` | 21,000 | same | 0.63 s |

**The solver accepts a `b^Delta` field with `R = 0`. No gap, no minimal change
needed, nothing new written.** Two case-plumbing fixes were required and are
recorded because they are departures from the shipped cases: the benchmark
`system/residuals` `#includeEtc` resolves only under an OpenFOAM.org build, so the
`functions` block is emptied and residuals are read from the solver log instead;
and `libs` is switched from the benchmark's
`libfrozenIncompressibleTurbulenceModels.so` (absent on this machine) to
`libspartaTurbulenceModels.so`.

### 2.2 The split of `tau`, and the sign convention

The linear part stays **implicit** through `nu_t` (the stock SST
`fvm::laplacian(nuEff, U)`); the nonlinear part is the **explicit, static** field
`bijDelta`, entering momentum as `+ fvc::div(dev(2 k bScale bijDelta))`. This is
the W2 record's Eq. 2-3 convention, so with `b_Bouss = -(nu_t/k) S`:

```
bijDelta  :=  b_target  -  b_Bouss  =  b_target  +  (nu_t / k) S
```

`S = symm(grad U)`; `nu_t`, `k` and `S` are taken **once**, from the case's own
shipped converged k-omega SST solution, and held static. Registered consequence,
stated now rather than discovered later: because `k` is transported, the injected
stress at convergence is `2 k_new bijDelta_static`, so the total modelled
anisotropy at convergence is `-(nu_t_new/k_new) S_new + bijDelta_static`, which is
**not** equal to the forest's `b`. That is the SpaRTA propagation form and it is
what "frozen nonlinear part" means here.

`S` is computed with `of_read.structured_gradient` where `gradU` is not shipped
(all three cases here), verified to 0.47-0.96 % interior relative L2
(`_common/BASELINES.md` sec. 1).

**Masking.** Cells with `k_RANS < 1e-4 * mean(k_LES)` get `bijDelta = 0` — the
`(nu_t/k) S` term is meaningless there. The masked count is reported per case.

### 2.3 `kDeficit` (R) = 0 — a registered choice

The TBRF predicts `b` and nothing else. Schmelzer's `R` is a separate
**k-equation** correction that this model does not produce, and inventing one
would be fitting a second model. `R = 0` therefore, everywhere, in every
configuration including the truth-injection ceiling. **Consequence, registered:
our truth-b ceiling is a `b`-only ceiling and is necessarily weaker than
Schmelzer's Table 1 (`b^Delta` *and* `R`).** Comparing our ceiling to their
0.22703 would be a category error and is not done.

### 2.4 `k` and `omega` are TRANSPORTED, not frozen

`kOmegaSSTCorrected` is stock SST plus corrections: both transport equations are
solved every iteration, with the production augmented by
`Gextra = -2 k bScale (bijDelta : grad U)` in the `k` equation (inside Menter's
limiter) and by `gamma (Gextra + R)/nu_t` in the `omega` equation. **Justification
for transporting rather than freezing:** the momentum correction is `2 k b^Delta`,
so a frozen `k` would inject a stress inconsistent with the velocity field being
solved; Schmelzer's frozen-RANS *propagation* transports them, and this is the
same solver that reproduced that propagation. Freezing is not run.

### 2.5 Blending factor

**`bScale` = 1.0 — no blending, no clipping — in every scored configuration.**
This is stricter than Kaandorp, whose own continuation stops at `γ_max` = 0.8
found by raising `γ` in steps of 0.1 until the solver diverged (flag F19).
**Registered contingency, fixed now:** if and only if a configuration fails to
converge at `bScale` = 1.0, the ladder `bScale ∈ {0.8, 0.5}` is run for that
configuration **as a labelled divergence diagnostic**. The ladder is two fixed
numbers chosen before any solve; a ladder result never becomes the headline and
never converts a GATE FAIL into a pass.

---

## 3. Cases and configurations

Three held-out cases. None was in the forest's training set.

| tag | case | cells | why |
|---|---|---|---|
| **T1** | `AR_1_Ret_360` | 3,025 | the a-priori primary; strict benchmark TEST case |
| T2 | `AR_3_Ret_360` | 8,748 | second strict TEST duct; cheap |
| T3 | `CBFS13700` | 21,000 | the paper's own case C1 |

Six configurations per case, all re-solved from the shipped converged SST field:

| label | `bijDelta` built from | role |
|---|---|---|
| `NULL` | 0 | **control**: proves the corrected solver reduces to stock SST. Registered prediction: `U_rms` reproduces the SST row to within 1e-3 absolute |
| `TRUTH` | `b_LES` | the **propagation ceiling** (b-only, sec. 2.3) |
| `MEANB` | the constant train-mean `b` of **this lane's own 20-case group-clean split**, `[[0.1358,-0.0536,0],[-0.0536,-0.1410,0],[0,0,0.0052]]` | the Charter-2c trivial comparator |
| `MEANB64` | the published `BASELINES.md` §6.4 constant | secondary, **T1 only**, and labelled **LEAKY**: its 23-case training set contains `AR_1_Ret_180` and `CBFS13700`, which are held out here |
| `ML0/1/2` | the post-hoc D2-removed forest, seeds 0, 1, 2 | the model under test (3 seeds) |

19 solves total.

---

## 4. Metrics

`_common/BASELINES.md` §1 definitions, over **all cells of the case's own mesh**,
against the shipped interpolated LES/DNS truth, so the numbers are directly
comparable to the published SST rows:

* `U_rms = sqrt(mean(|U - U_LES|^2)) / mean(|U_LES|)`
* `U_mae = mean(|U - U_LES|) / mean(|U_LES|)`
* `k_rms`, and `b_rms` of the **total** modelled anisotropy of the re-solved field.
* **Ducts:** in-plane (secondary) velocity magnitude as a percentage of bulk.
* **CBFS:** `x_reatt` by the first-cell-row sign criterion (BASELINES §1).
* **Every configuration:** RMS `div(U)`, volume-weighted, normalised by
  `U_bulk / L` (charter §7).
* **Every configuration:** iterations run, wall time, and the initial-residual
  history of `Ux`, `p`, `k`, `omega`.
* **Every configuration:** realisability of the **total** anisotropy of the
  re-solved field, `b_total = -(nu_t/k) S + bijDelta`, as the fraction of cells
  outside the barycentric triangle (tolerance 1e-7, as in `../RESULTS.md` §7).

### The frozen gates, from `BASELINES.md`

| case | SST `U_rms` | SST `U_mae` | SST `x_reatt` | LES `x_reatt` | in-plane \|U\| LES (% bulk) | in-plane \|U\| RANS |
|---|---|---|---|---|---|---|
| `AR_1_Ret_360` | **0.1985** | — | — | — | **1.508** | 3.96e-16 |
| `AR_3_Ret_360` | **0.1846** | — | — | — | **1.411** | 7.58e-16 |
| `CBFS13700` | **0.0516** | **0.0258** | 5.891 | **4.241** | — | — |

`U_mae` is not tabulated for the ducts in `BASELINES.md` §4; the `NULL`
configuration supplies it and is the registered gate for the duct `U_mae` rows.

---

## 5. Hypotheses, bands and falsifiers

All ML numbers are mean ± sample std over **3 forest seeds**. Verdicts use the
fixed vocabulary {PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING}.

### H0 — the propagation works at all (a gate on the whole test)

> Injecting the **true** anisotropy must substantially improve the velocity field.

* **NOT A RESULT for the entire lane** if `TRUTH` fails to reduce `U_rms` on
  **T1** by **≥ 30 %** relative to the SST gate 0.1985.
* 30 %, not 50 %, and the reason is registered now: Schmelzer's published
  frozen-field ceiling on CBFS (`eps(U)/eps(U_0)` = 0.22703, a squared-error
  ratio) is a 52 % RMS reduction **with `R` included**, and sec. 2.3 omits `R`.
  A b-only ceiling must be allowed to be weaker. **The supervisor's suggested
  50 % bar is reported alongside every `TRUTH` row as a stricter reading**, so a
  reader can apply either.
* If H0 fails, H1-H3 are reported as **NOT A RESULT**, not as failures of the
  model — a broken propagation path cannot grade a closure.

### G0 — solver identity gate (runs FIRST; the lane stops if it fails)

Registered to match Lane 2 (Wu2018) so the two lanes are comparable, and
**tightened**, because the naive form of this gate cannot pass.

* **G0a, the identity test that is actually a test of the solver:** run stock
  `kOmegaSST` and `kOmegaSSTCorrected` with `bijDelta = 0`, `kDeficit = 0`,
  `bScale = RScale = 1`, from the **same** shipped start field for the **same**
  200 iterations, and require relative L2 difference in `U` below **1e-10**.
  This is the property `kOmegaSSTCorrected` claims in its own header ("reduces
  exactly to kOmegaSST at RScale = bScale = 0") and it is measurable to round-off.
* **Why not "re-solve to convergence and compare to the shipped field < 1e-10".**
  Because the shipped fields are not converged to 1e-10: the interface check
  measured an initial `Ux` residual of **1.8e-5** on `AR_1_Ret_360` when
  restarting the shipped solution. Any further iteration moves `U` by far more
  than 1e-10 for reasons that have nothing to do with the correction terms, so
  that form of the gate would fail on a perfectly correct solver. G0a compares
  two solvers over an identical trajectory instead, which removes the drift.
* **G0b, the weaker convergence-level check, kept as well:** the `NULL`
  configuration run to full convergence must reproduce the published SST `U_rms`
  row to within **1e-3 absolute**.
* **The lane stops and reports BLOCKED if G0a fails.** No scored solve is graded
  against a solver that is not the model it claims to be.

### H1 — the ML correction beats the SST baseline, re-solved

* **PASS** iff `mean(U_rms | ML) + 2·sd < ` the SST gate for that case.
* **GATE REACHED** iff the mean is below the gate but the 2σ band crosses it.
* **GATE FAIL** iff `mean(U_rms | ML) ≥` the gate, or any ML seed diverges or
  fails to converge (sec. 6).
* **Falsifier, stated in advance:** an a-priori `b_rms_F` improvement of 45.9 %
  over SST that does not survive being put inside the momentum equation is the
  central negative result this lane exists to be able to report.

### H2 — the ML correction beats the trivial train-mean correction

* **PASS** iff `mean(U_rms | ML) + 2·sd < U_rms(MEANB)`.
* **GATE FAIL** iff `mean(U_rms | ML) ≥ U_rms(MEANB)` — i.e. a constant tensor
  with no inputs propagates as well as the forest.

### H3 — the ML correction is within a stated factor of the ceiling

* **PASS** iff `mean(U_rms | ML) ≤ 2.0 × U_rms(TRUTH)`.
* **GATE REACHED** iff `≤ 4.0 ×`. **GATE FAIL** iff `> 4.0 ×`.

### H4 — secondary flow in the ducts (registered, carries a verdict)

A linear eddy-viscosity model produces **exactly zero** secondary flow
(measured 4e-16 of bulk). Any injected `b` with non-zero `b_23` and `b_22 - b_33`
must produce some.

* **PASS** iff ML in-plane `|U|` ≥ **0.3 %** of bulk on T1 (DNS: 1.508 %).
* **GATE REACHED** iff ≥ 0.1 % and < 0.3 %.
* **GATE FAIL** iff < 0.1 % — the correction did not reach the mechanism it was
  supposed to reach.

### H5 — continuity (charter §7)

* **Registered prediction: volume-weighted RMS `div(U)` normalised by
  `U_bulk / L` is below 1e-3 for every re-solved configuration**, against this
  lab's own published post-hoc figures of **10.5 % and 9.7 %**
  (`Certonomous_closure_challenge/description/METHOD.md` §6.2) — a ≥ 100x
  improvement, "about 0 by construction" made into a number.
* **GATE FAIL on H5** for any configuration exceeding 1e-3. Reported for all 19.

### Realisability (reported; no verdict, by design)

The a-priori claim (iii) already returned GATE FAIL at 0.1339 for this forest
configuration. The re-solved fraction is reported for every configuration beside
the truth's own rate (`AR_1_Ret_360` 0.0159, `CBFS13700` 0.0000) and beside the
a-priori number, so the reader can see whether re-solving repairs or worsens it.
**No clipping is applied** (sec. 2.5).

---

## 6. Convergence, and how the run ends without `kill`

* **Converged** iff the initial residual of `p` **and** of `Ux` are both below
  **1e-6**, sustained for 100 consecutive iterations. `Uy`/`Uz` residuals are
  **excluded** from the criterion: the duct's baseline has `Uy, Uz ≈ 0`, so
  OpenFOAM's normalisation makes their initial residuals O(0.3) at restart even
  with zero corrections (observed in the interface check). Recording that here
  rather than being surprised by it later.
* **Stagnation fallback:** if residuals plateau, `max |ΔU| / U_bulk` over the last
  500 iterations below 1e-6 also counts as converged, and is labelled as such.
* **Hard iteration cap: 30,000** (`endTime`), and a **wall-clock `timeout` of
  3600 s per solve inside the script**. Every solve therefore terminates on its
  own; `kill` is never needed and is not available.
* **Divergence is a result, not an error.** A configuration whose residuals rise
  monotonically, or that ends on a floating-point exception, is recorded with the
  iteration number and the residual history at that iteration and graded
  **GATE FAIL**.

---

## 7. Compute

Measured in the interface checks: **0.126 s per iteration** on CBFS (21,000
cells) and **0.004 s** on `AR_1_Ret_360` (3,025 cells), single core. At the
30,000-iteration cap that is 63 min for a CBFS solve and 2 min for a duct solve.
Worst case for 19 solves: 6 × 1.05 + 13 × 0.06 ≈ **7.1 core-hours**.

**Lane cap: 15 core-hours.** If the lane would exceed it, the remaining solves are
dropped in the order T2 → T3 and the omission is reported. Nothing here approaches
the 487-core-hour authorisation.

---

## 8. What this test CANNOT see

* **One Reynolds number per case.** Two ducts and one step; no `Re` sweep, no
  mesh-refinement study. A converged answer on one mesh is not a grid-converged
  answer.
* **`k` and `omega` are transported with a correction that omits `R`** (sec. 2.3),
  so the turbulence scales are only partly corrected and the ceiling is a b-only
  ceiling.
* **`bijDelta` is static**, frozen at the baseline SST `nu_t`, `k`, `S`. The total
  anisotropy at convergence is therefore not the forest's `b` (sec. 2.2), and this
  test cannot separate "the forest's `b` is wrong" from "the frozen-`b^Delta`
  propagation form loses information".
* **The ducts are streamwise-periodic with a `meanVelocityForce`**, so the bulk
  velocity is imposed by construction and cannot be got wrong; the whole `U` error
  lives in the profile shape and the secondary flow.
* **The forest is the post-hoc D2-removed configuration** — a variant of a variant
  (sec. 1). Nothing here grades Kaandorp's published numbers, and Table 4 stays
  BLOCKED.
* **Three seeds**, so the ± is a 3-sample std and the 2σ bands are wide.
* **No uncertainty band accompanies the LES/DNS truth**, so no error here can be
  compared against a data uncertainty.
* **The `NULL` control tests the solver, not the model.** If `NULL` fails to
  reproduce the SST row, every other number in the lane is void, and that is the
  first thing reported.
