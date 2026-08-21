# RESULTS — Xiao et al. 2016 iterative ensemble Kalman: **BLOCKED at the forward model**

**No ensemble was run.** The registered H0 forward-model harness gate failed at
the frozen Reynolds number (PH10595) and failed again at the lower Reynolds number
registered in DEPARTURE 1 (PH5600). Under the decision rule frozen before that
re-test, **the conditioning explanation is REFUTED as sufficient and this case
ships BLOCKED with the refutation as the cause.**

Total compute spent to reach that conclusion: **0.87 core-hours, $0.045.** The
ensemble it prevented was costed at 16.6 core-hours (full design) to 161.3
core-hours (registered worst case).

Preregistration: `PREREGISTRATION.md` in this directory — frozen text §1-§8, plus
`DEPARTURE 1` appended and dated **before** the re-test, containing the case name,
both gates, and the decision rule verbatim.

---

## 1. Verdicts

| gate | registered band | PH10595 (`Re_H` = 10595) | PH5600 (`alpha_10_9000_3036`, `Re_H` = 5600) | **VERDICT** |
|---|---|---|---|---|
| **G0** forward-model identity | \|`U_rms` − baseline\| < 1e-3 | **0.15658** vs 0.1565 (Δ 8e-5) | **0.15547** vs 0.1556 (Δ 1.3e-4) | **PASS at both** |
| **H0** truth-stress harness | `U_rms` ≤ 0.036 / ≤ 0.0358 (≥ 77 % reduction) | **0.29799** / **3.8815** | **0.31210** / **0.47467** | **GATE FAIL at both** |
| **H1** posterior mean beats baseline | ≤ 0.1252 | not run | not run | **BLOCKED** |
| **H2** credible-interval coverage | ≥ 0.80 held-out | not run | not run | **BLOCKED** |
| **H3** realisability of posterior samples | 0.0000 | not run | not run | **BLOCKED** |
| conditioning explanation (DEPARTURE 1) | H0 PASS at 5600 | — | H0 FAILED | **REFUTED as sufficient** |

G0 passing at both Reynolds numbers matters: it says the forward model is
*correct* — prescribe the baseline stress and it returns the baseline field to
1e-4 — so H0's failure is not a plumbing bug. The model is right and the problem
is hard.

---

## 2. The harness numbers, both Reynolds numbers, both implicit-viscosity choices

Forward model: `kOmegaSSTCorrected` with `turbulence off;` so `k` and `nu_t` are
frozen fields, `tau_model = (2/3)k I − 2 nu_t S + 2k bijDelta` with
`bijDelta = b_target + (nu_t/k)S`, so `tau_model` equals `tau_target` exactly once
`S` converges. An outer deferred-correction loop refreshes `bijDelta` as `S`
moves. This is the `tauFoam` role of the paper's §5.1, built from the validated
interface; **no new solver was written.**

| `Re_H` | implicit viscosity | `U_rms` (gate) | `U_mae` | outer-loop `max|dU|/|U|` per iteration | `nu_t^L` clipped at 0 |
|---|---|---|---|---|---|
| 10595 | frozen baseline SST `nu_t` | **0.29799** (≤ 0.036) | 0.25462 | 0.58, 0.18, 0.31 — oscillating | n/a |
| 10595 | optimal `nu_t^L`, clipped ≥ 0 | **3.8815** (≤ 0.036) | 3.19520 | 0.19, 0.13, 1.21, 1.21, 1.14, 1.22 — **diverging** | 1,872 → **7,337 = 47.0 %** |
| 5600 | frozen baseline SST `nu_t` | **0.31210** (≤ 0.0358) | 0.26447 | 0.571, 0.160, 0.285, 0.163, 0.116, 0.091 — decaying, still 9 % at outer 6 | n/a |
| 5600 | optimal `nu_t^L`, clipped ≥ 0 | **0.47467** (≤ 0.0358) | 0.41187 | 0.221, 0.425, 0.715, 0.436, 0.587, 0.490 — oscillating | 1,944 → **3,722 = 23.9 %** |

Baselines to beat, from `BASELINES.md` §3: **0.1565** (PH10595), **0.1556**
(`alpha_10_9000_3036`). **Every H0 configuration is worse than the baseline it was
meant to bound** — by 1.9x, 24.8x, 2.0x and 3.1x respectively.

`optimal nu_t^L = −⟨tau_dev : S⟩ / (2⟨S : S⟩)`, clipped at zero — Wu, Sun, Xiao &
Wang's conditioning fix (flag F16; **that paper is not in the corpus** and remains
flagged for retrieval).

---

## 3. What halving the Reynolds number did, and why it is still a refutation

DEPARTURE 1 predicted: *"if the conditioning explanation is right, halving `Re`
should move the harness measurably toward the gate."* It moved, and not far enough.

| quantity | `Re` = 10595 | `Re` = 5600 | change | direction predicted? |
|---|---|---|---|---|
| `nu_t^L` clip fraction | 47.0 % | **23.9 %** | halved | **yes** |
| `U_rms`, optimal `nu_t^L` | 3.8815 | **0.47467** | 8.2x better | **yes** |
| `U_rms`, frozen SST `nu_t` | 0.29799 | **0.31210** | 4.7 % **worse** | **no** |
| best `U_rms` against its gate | 8.3x over | **8.7x over** | unchanged | **no** |
| outer loop converges? | no | no | — | **no** |

**Three of five diagnostics moved the way the conditioning story predicts, and the
two that decide the gate did not.** The clip fraction halving is real and is
exactly what a conditioning argument predicts. But the best configuration remains
**8.7x above its gate** — no better, relative to the gate, than at twice the
Reynolds number — and neither outer loop converges at either `Re`.

Extrapolating the one clean trend (clip fraction ~ `Re`) to the paper's own
`Re_b` = 2800 would give roughly 12 % clipping, still an eighth of the domain
carrying an explicit stress with no implicit stabiliser. **The benchmark contains
no periodic hill below `Re_H` = 5600, so that extrapolation cannot be tested here
and is not offered as a result.**

**Registered rule, applied as written:** H0 FAIL at 5600 → the conditioning
explanation is REFUTED, no ensemble runs, the case ships BLOCKED with the
refutation as the cause. The directional evidence above is reported as data; it
does not rescue the explanation, because the gate is what decides and the gate
failed. What is refuted is the explanation's **sufficiency** — that Reynolds
number alone accounts for the gap between this machine and the paper. Something
else is also carrying it, and the mesh disparity (15,600 cells against the paper's
1,500) is the obvious remaining suspect, untested.

---

## 4. The PH10595 finding stands

Recorded here because moving down in Reynolds number does not erase it, and the
supervisor's condition 2 requires it to stay in the record:

**Prescribing the true Reynolds stress explicitly on a separated periodic hill at
`Re_H` = 10595 on a 120 x 130 mesh diverges.** `U_rms` = 0.29799 with an
oscillating outer loop under a frozen baseline eddy viscosity; `U_rms` = 3.8815
with a diverging outer loop under the optimal linear projection; the projection's
clip fraction rises to **7,337 of 15,600 cells = 47 %**. Xiao et al. ran
`Re_b` = 2800 on 1,500 cells — **3.78x lower Reynolds number and 10.4x fewer
cells**. Writing the missing `tauFoam` would reproduce the divergence in C++; the
gap is conditioning and scale, not code.

---

## 5. The one path that does work on this case, and why it cannot serve an EnKF member

Measured, on PH10595: `b^Delta` **and** `R` together — `R` extracted by
`kCorrectiveFrozenFoam` and `k` transported — gives

**`U_rms` = 0.009319 against the SST baseline's 0.1565, a 94.0 % reduction**,
comfortably inside the H0 band that the prescribed-tau model missed by 8x.

It independently reproduces the W2 SpaRTA campaign record, which reports
`eps(U)/eps(U_0)` = 0.003331 on this case: `sqrt(0.003331) x 0.1565 = 0.00903`,
**agreement to 3 %**. Two implementations, same case, same number.

**It cannot be used for an ensemble member**, and the reason is structural, not
practical: `kCorrectiveFrozenFoam` computes `R` as the residual of the steady `k`
equation with the **true** velocity field frozen in. An EnKF member has a
perturbed stress and an unknown velocity. `R` is not available to it. Option 1 of
`PREREGISTRATION.md` §7 — recompute `R` per member from the member's own current
`U` — remains **shelved as a possible future NEW registered test**, untested, and
is explicitly **not** a fallback of this one.

---

## 6. Compute

| item | core-hours |
|---|---|
| PH10595 G0 + H0, frozen baseline `nu_t` | 0.232 |
| PH10595 G0 + H0, optimal `nu_t^L` | 0.296 |
| PH10595 `b^Delta`+`R` control (frozen extraction + propagation) | 0.106 |
| PH5600 G0 + H0, optimal `nu_t^L` | 0.137 |
| PH5600 H0, frozen baseline `nu_t` | 0.097 |
| **total charged to this lane** | **0.868** |

**$0.045** at $0.0513/core-hour. All single-core; the 487-core-hour hard stop was
never approached. Measured one-member forward-evaluation cost, recorded as
required: **0.0277 core-hours**, giving 16.6 core-hours for the paper's
60 x 10 design and 161.3 core-hours at the registered per-member caps — **the
ensemble this harness prevented.**

---

## 7. What this record CANNOT see

* **It cannot grade Xiao's method.** No ensemble ran. H1-H3 are BLOCKED, not
  failed, and nothing here is evidence about ensemble Kalman inversion.
* **It cannot separate Reynolds number from mesh.** Both differ from the paper
  (3.78x and 2.0x in `Re`; 10.4x in cells) and only `Re` was varied. A
  mesh-coarsening test at fixed `Re` is the obvious next falsifier and was not run.
* **It cannot reach the paper's regime.** The benchmark holds no periodic hill
  below `Re_H` = 5600, so `Re_b` = 2800 is unreachable with the data on this
  machine.
* **The forward model is not the paper's `tauFoam`.** It is a partially implicit
  substitute that is exact at convergence and identity-correct at G0; whether the
  paper's fully explicit solver would behave the same at these `Re` and mesh is
  inference from the clip fraction, not a measurement.
* **`nu_t^L` clipping at zero is a choice**, registered, and it is the thing that
  fails. An unclipped negative eddy viscosity is unconditionally unstable, so the
  choice is forced, but a different splitting might not need it.
* **Continuity here is estimator-limited.** On the PH mesh
  `of_read.structured_gradient` returns RMS `div(U)`/gradient scale of
  **9.45e-3 for the shipped converged SST field** and **5.90e-3 for the LES
  truth** — that is the instrument's floor, not those fields' continuity error, so
  the `divU` column in §2 is diagnostic only.
* **Two forward-model configurations, one case family.** No seed spread exists
  because nothing stochastic was run.
