# Shelf D — eigenspace perturbation envelopes, and whether they contain the truth

Machinery: `eigenspace.py` (importable by the BUILD lane). Driver for the
registered a-priori question: `run_envelope.py`. Optional re-solves:
`run_resolves.py`. Preregistration:
`../../NASA_hump_gate/PREREGISTRATION.md` Part A, frozen before any number here
was computed.

**Nothing is fitted. Nothing here is a model.** This is the band that doctrine R1
means when it says *every prediction ships its model-form band*.

## 0. Sources, cited from the files on disk

* **Emory, Larsson & Iaccarino**, Phys. Fluids **25**, 110822 (2013) —
  `docs/papers/closure/Emory2013_structural_uncertainty_rans.pdf`, published article.
  * eq. **(4)**, p. 110822-5 — `R_ij = 2k (d_ij/3 + v_in L_nl v_jl)`, `l1 >= l2 >= l3`
  * eq. **(5)**, p. 110822-5 — `x = x_1c (l1-l2) + x_2c (2l2-2l3) + x_3c (3l3+1)`
  * eq. **(7)**, p. 110822-6 — `x* = x + delta_B (x^(t) - x)`
  * eq. **(8a)**, p. 110822-6 — `l* = M^{-1} x*`
* **Iaccarino, Mishra & Ghili**, Phys. Rev. Fluids **2**, 024605 (2017) —
  `docs/papers/closure/Iaccarino2017_eigenspace_perturbations.pdf`, the **accepted
  manuscript via CHORUS**; equation and page numbering may differ from the journal
  of record and is quoted here as manuscript numbering.
  * eq. **(3)** — `<A,R>_F in [l1 g3 + l2 g2 + l3 g1, l1 g1 + l2 g2 + l3 g3]`
  * after eq. (3) — `v_min = [[0,0,1],[0,1,0],[1,0,0]]`, `v_max = I`, in the
    strain-eigenvector frame
  * before sec. III — **"we need a set of only 5 RANS simulations"**: `{1C,2C}` x
    `{v_min,v_max}` plus `3C`, which is rotationally degenerate.

**Symbol warning, carried into the code.** Emory writes `B` for both the
perturbation magnitude (eq. 7) and the linear map (eq. 5). The code calls them
`delta_B` and `M`.

## 1. The registered question

> Does the LES/DNS truth lie inside the eigenspace envelope? Per case, per
> quantity, as fractions.

This closes the loop **L-157** left open. Xiao et al.'s uncertainty space provably
excludes the truth wherever the error is an orientation error, because that method
never perturbs eigenvectors. The eigenspace method **does**. So: does *its*
envelope contain the truth?

## 2. Coverage, eight TRAINING-family cases, frozen fields

`shape` = fraction of masked-valid cells whose truth barycentric point lies inside
the triangle spanned by the three eigenvalue-perturbed states.
`prod` = fraction whose truth production `P_k = -R_ij dU_i/dx_j` lies inside the
per-cell `[min,max]` envelope of the **five** states.

| case | cells | truth unreal. | shape @0.25 | @0.50 | @0.75 | **@1.00** | prod @0.25 | @0.50 | @0.75 | **@1.00** |
|---|---|---|---|---|---|---|---|---|---|---|
| `PHLL10595` | 15,563 | 0.0000 | 0.3673 | 0.6473 | 0.8396 | **1.0000** | 0.7637 | 0.8761 | 0.9122 | **0.9415** |
| `CBFS13700` | 18,016 | 0.0000 | 0.2839 | 0.4788 | 0.6467 | **0.9983** | 0.7850 | 0.8746 | 0.9138 | **0.9378** |
| `AR_1_Ret_180` | 1,854 | 0.0000 | 0.0086 | 0.0895 | 0.2023 | **1.0000** | 0.9137 | 0.9930 | 1.0000 | **1.0000** |
| `AR_3_Ret_180` | 5,849 | 0.0000 | 0.0233 | 0.1590 | 0.2930 | **1.0000** | 0.8495 | 0.9638 | 0.9949 | **0.9998** |
| `alpha_10_9000_3036` | 15,409 | 0.0047 | 0.3680 | 0.6621 | 0.8357 | **0.9953** | 0.7416 | 0.8755 | 0.9150 | **0.9433** |
| `alpha_05_7071_3036` | 15,385 | 0.0051 | 0.3899 | 0.6861 | 0.8452 | **0.9949** | 0.8929 | 0.9475 | 0.9689 | **0.9789** |
| `alpha_15_10929_3036` | 15,413 | 0.0046 | 0.3206 | 0.6083 | 0.8179 | **0.9954** | 0.7944 | 0.8841 | 0.9126 | **0.9315** |
| `alpha_125` | 15,418 | 0.0048 | 0.3447 | 0.6250 | 0.8301 | **0.9952** | 0.7686 | 0.8761 | 0.9085 | **0.9279** |

All twelve columns are read from `/home/ubuntu/closure-data/uq_eigenspace/envelope.json`.

## 3. The sharp form: how large a perturbation does containing the truth require?

`delta_B_req` is the smallest `delta_B` at which the truth enters the perturbed
triangle, computed in closed form rather than by laddering — Emory's own Sec. IV
construction (p. 110822-12, where they deduce `B` from DNS by minimising the
barycentric distance).

| case | median | p95 | fraction needing `delta_B > 1` |
|---|---|---|---|
| `alpha_05_7071_3036` | **0.310** | 0.954 | 0.0051 |
| `alpha_10_9000_3036` | **0.342** | 0.959 | 0.0047 |
| `PHLL10595` | **0.351** | 0.965 | 0.0000 |
| `alpha_125` | **0.372** | 0.961 | 0.0048 |
| `alpha_15_10929_3036` | **0.396** | 0.963 | 0.0046 |
| `CBFS13700` | **0.535** | 0.998 | 0.0000 |
| `AR_3_Ret_180` | **0.954** | 0.999 | 0.0000 |
| `AR_1_Ret_180` | **0.981** | 0.999 | 0.0000 |

## 4. Verdicts on the registered predictions

| prediction | band | measured | verdict |
|---|---|---|---|
| **P-A1** shape coverage @`delta_B`=1.0 `>= 0.95` on every case | self-check on the implementation | min **0.9949** | **PASS** |
| **P-A2** production coverage @1.0 `< 0.95` on at least one case | tests the `k` gap | min **0.9279**, max 1.0000 | **PASS** |
| **P-A3** median `delta_B_req` in `[0.2, 0.8]` | Emory's DNS magnitudes are O(0.5) | **0.310 to 0.981** | **GATE FAIL** |
| implementation: cells leaving the simplex under eq. (7) | must be 0 | **0** | **PASS** |

**P-A1 is a self-check and it behaved exactly as the preregistration said it
would.** At `delta_B` = 1 the three states are the triangle corners, so the hull
is the whole realisable set and the only cells that can fail are those where the
truth itself is unrealisable. Measured shape coverage is `1 - truth_unrealisable`
to four decimals on every case. The machinery is doing what eqs. (5), (7) and (8a)
say.

**P-A3 fails, and the way it fails is the finding.** The eight cases split cleanly
into two families:

* **2-D separated flows** — hills and the curved step — need `delta_B_req` of
  **0.31 to 0.54**, squarely inside Emory's own O(0.5) experience.
* **Square and rectangular ducts** need **0.95 to 0.98** — essentially the whole
  way to a corner of the barycentric triangle.

That is the secondary-flow structural failure, re-expressed in the perturbation
magnitude. A linear eddy-viscosity model in a duct produces `b_23 = 0` and
`b_22 - b_33 = 0` identically (`BASELINES.md` §4 measures the resulting in-plane
velocity at `4e-16` of bulk against a DNS `1.5 %`), so the model's barycentric
point is not merely displaced from the truth — it sits near the wrong vertex, and
only a near-total move contains the truth. **Emory's perturbation magnitudes are
calibrated on flows where the model is qualitatively right. On a flow where the
model is structurally wrong, the required magnitude saturates at 1.**

## 5. What the envelope does and does not contain

* **Shape (anisotropy eigenvalues): contained, at `delta_B` = 1, up to the truth's
  own realisability.** 0.9949 to 1.0000. But that is nearly a tautology — at
  `delta_B` = 1 the envelope is the entire realisable set. The honest statement is
  §3's: containment is achieved, and on the ducts it costs the whole triangle.
* **Production: NOT fully contained. Below 0.95 on 5 of the 8 cases** — every
  hill and the curved step, 0.9279 to 0.9433 — while the two ducts and
  `alpha_05_7071_3036` clear it (0.9789 to 1.0000). The
  reason is structural and was registered in advance: Emory's eq. (4) keeps `k`
  outside the bracket, so the eigenspace family perturbs **shape and orientation
  only**. A `k`-magnitude error is outside the envelope by construction. Across
  these cases the RANS `k` is 0.59 to 0.72 of the LES `k` in the mean, so between
  2 % and 7 % of cells have a production the envelope cannot reach whatever
  `delta_B` does.
* **Answering L-157 directly:** the eigenspace envelope contains the truth's
  *shape* where Xiao's cannot, because it perturbs orientation — but it still
  fails to contain the truth's *momentum forcing* in 2-7 % of cells, for a
  different reason (magnitude). **Neither published framework on this shelf
  contains the thing it is meant to bound, and they fail on different axes.**
  Emory and Iaccarino both say so about `k`; this file measures how much it costs.

## 6. What this cannot see

* **Eight training-family cases at one Reynolds number each.** No TEST case and no
  hump were touched by Part A.
* **A-priori, on frozen fields.** Containment of a stress envelope is not
  containment of a velocity envelope; the momentum equation is not monotone in
  `b`. Part A.4 addresses that on one case and its result is reported there.
* **`k` is not perturbed**, by the method's own construction. Every production
  number above inherits that.
* **`delta_B_req` is a per-cell quantity**; a spatially uniform `delta_B` large
  enough for the worst cell is much larger than the median, and Emory's Sec. IV is
  precisely about not doing that.
* **The five states use the RANS `k` and the RANS strain field**, both frozen.

---

## 7. PART A.4 — five eigenspace re-solves on one training hill

Registered in `../../NASA_hump_gate/PREREGISTRATION.md` A.4 **before solving**,
including the prediction. Case `alpha_10_9000_3036`, `delta_B` = 1.0, five states
injected through the validated `kOmegaSSTCorrected` path (`bijDelta` from the
perturbed `b`, `kDeficit = 0`), 5,000-iteration cap.

| state | iterations | `U_rms` | RMS `div(U)`/grad scale | convergence |
|---|---|---|---|---|
| `2C_vmin` | 5,000 | **0.1505** | 1.08e-2 | CAPPED-NOT-CONVERGED |
| `1C_vmin` | 5,000 | 0.3129 | 2.27e-2 | CAPPED-NOT-CONVERGED |
| `3C` | 5,000 | 0.6186 | 1.17e-2 | CAPPED-NOT-CONVERGED |
| `2C_vmax` | 5,000 | 0.8793 | 4.42e-2 | CAPPED-NOT-CONVERGED |
| **`1C_vmax`** | 5,000 | **1637.94** | 2.10e-1 | CAPPED-NOT-CONVERGED |

Baseline for the case: SST `U_rms` = **0.1556**. **All five hit the cap; none
converged.** The estimator floor for `div(U)` on this mesh class is ~9.5e-3
(`../../Xiao2016_EnKF/NUMERICS_DRAFT.md` N-X1), so the two smallest values sit at
the floor and `1C_vmax` is 22x it.

**Velocity envelope coverage (all components): 0.7440.** `U_x` 0.8588,
`U_y` 0.9493.

### Verdict on P-A4 — falsified, and not a positive surprise

The registered prediction was **coverage < 0.50**, with the reason stated in
advance: the injection path holds `k` at the RANS value, and the Kaandorp lane
measured that a b-only injection with transported `k` collapses `k` to 0.33x and
cannot carry even the truth, so the envelope should be **too narrow**.

Coverage came out **0.7440**, so **P-A4 is FALSIFIED**. The preregistration said a
falsification would be a positive surprise and should be reported as such.
**It is not one, and the number that says so is the envelope width: the mean
per-cell envelope is 1,344 times the mean velocity magnitude.** One member —
`1C_vmax`, the one-component limit aligned for maximum production — reaches
`U_rms` = 1638, four orders above the baseline. An interval 1,344x wider than the
signal contains 74 % of the truth for the same reason a blindfold contains the
dartboard.

**So both halves of the prediction failed, in opposite directions, and the record
says so:** the band was wrong (0.744, not < 0.50) *and* the stated mechanism was
wrong (the envelope is not too narrow, it is unusably wide). The coverage figure
is reported as **NOT A RESULT** as a statement about uncertainty quantification.
What it does establish is a solver fact worth carrying: **the maximum-production
eigenvector alignment at the 1C limit is not propagatable through this injection
path on a separated hill** — which is consistent with Iaccarino's own framing that
`v_max` is chosen to maximise production, and with the a-priori finding in §5 that
the path cannot carry magnitude.

A meaningful a-posteriori eigenspace envelope on this benchmark needs either
(a) a forward model that carries `k` — the same requirement the Xiao lane hit and
recorded as its H0 gate failure — or (b) `delta_B` well below 1, where §3's
`delta_B_req` says 0.35 would already contain the truth's shape on this case.
Neither was run here; both are registered as unrun.
