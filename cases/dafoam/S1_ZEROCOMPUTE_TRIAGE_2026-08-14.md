# S1 zero-compute triage — the second-QoI map was already on disk, G-P4 cannot fail, and the curvature is reconstructible

**Executed 2026-08-14, 21:54–22:15 UTC (`date -u`, run). Repo commit anchor at writing: `c966bf7e`.**
**Compute spent: zero.** No solver, no container, no inversion, no scoring call, no network. Every
number below is arithmetic over arrays and logs written before this file was opened. Nothing was
submitted, sent or registered.

Brief: extract results from data already on disk, and find which open closure questions can be
killed or settled without spending a core-minute. The precedent is R1
(`ladder-b/S1_SENSITIVITY_VS_ERROR.md`), which killed R5 (340 core-min) and R8 at zero compute by
noticing that a reported ρ = +0.9742 was uninformative against a null pinned at +1.0000.

**Three of the four results below are of that shape, and the largest one is at R1's own expense.**

---

## 0. Headline, in the order the evidence forces

1. **PR-1 — the one thing R1 asked to buy, at 25 core-min — was already on disk when R1 was
   written, and it returns the answer R1 pre-registered as closing the question.**
   `S1-cbfs-weighted-arm/cbfs_inv/grad_anchorw.npy` is `dJw/dβ` at **β = 1** against a genuinely
   different functional (`Jw = 5319·varUwin + 3591·varUrec`, supported on 2,970 cells in two
   boxes, against varianceU's all 21,000). It was billed 16.83 core-min on 2026-08-08. Scored
   against the first map: **Spearman +0.9894, top-decile overlap 94.05% against a 10% chance
   level, upstream shares 45.76% vs 45.57% — agreeing to 0.19 percentage points.**
2. **G-P4, the restored control gate on a 260 core-min item, cannot fail.** All three of its legs
   are functions of (β, g_QoI, λ_L2). A treatment that reports the prior as the posterior —
   the exact shape falsifier F1 exists to catch — reproduces **all three to 0.0e+00 relative
   error**. This is the same defect the 2026-08-11 withdrawal removed, restored in three parts.
3. **The curvature R1 declared unreconstructible is on disk, twice.** R1 prices the whole Bayesian
   line on "buying curvature as fresh gradients is **forced, not chosen**". That is true of
   consecutive-iterate pairs and false of **secant** pairs, which is all a curvature probe needs.
   Two runs archived matched (β, ∇) pairs at two states each.
4. **G2 is numerically exact.** Under a domain-decomposition change — a lever proven to break other
   cases' adjoints — G2 moves by **0.0000 percentage points** and the top-decile set agrees
   **2,100 of 2,100**. This is the first uncertainty figure attached to any G2 number in the corpus,
   and it *strengthens* the "G2 scores the adjoint" finding rather than weakening it.

---

## 1. Inventory of the open closure questions, in three classes

Frame for this inventory: `demo-output/website/CLOSURE_CHALLENGE_STATUS.md`,
`demo-output/website/ACTIVE_RESEARCH.md`,
`demo-output/website/campaign/CLOSURE_STAGE1_AND_C2_STATUS.md`,
`demo-output/website/campaign/RESEARCH_DIRECTIONS_2026-08.md`, `docs/DOCKET.md` §D/§E, and the
`ladder-b/S1_*` family, all read in full at `c966bf7e`. Items outside the closure/DAFoam line
(naval G-series, filming, repo professionalization) are out of frame and not classified.

### (a) Settleable from data already on disk

| item | what settles it | status |
|---|---|---|
| **PR-1** second-QoI sensitivity map (filed at 25 core-min) | score `grad_anchorw.npy` against `grad_eval001.npy` | **EXECUTED, §2.1** |
| **Curvature scale** for S1-priors' F2 and its 120 core-min Hv budget | secant pair from the archived eval-1/eval-10 arrays | **EXECUTED, §2.3** |
| **G2's numerical reproducibility** — no G2 figure in the corpus carries an uncertainty | the archived decomposition-replicate pair | **EXECUTED, §2.4** |
| **G-P2's stated mechanism** | prior pull vs likelihood pull at the archived pinned cells | **EXECUTED (bounded), §2.5** |
| **G-W1**, R5's reproduction control | reproduce 26.8571% and 29.0476% | discharged again here (§2.0 C3); first discharged by D45 |
| **R4** per-family cost scaling laws (0 core-min) | 477 archived run directories + ledgers | open, all inputs on disk |
| **R6** band-containment census (0 core-min) | counting admissible (band, external truth) pairs | open, pure counting |
| **R3 / R7** literature triangulation (0 core-min) | reading two papers | open; not compute-blocked, reading-blocked |
| **D41** proposal rot: gates whose source pre-registration moved after the proposal | `t_preregistration > t_proposal` over `agenda/proposals/` | open, file-timestamp arithmetic; **live — an agent acting on that JSON executes the withdrawn G-P4** |
| `ACTIVE_RESEARCH.md:671` still reads "best on four of eight cases" | already struck to 2-of-8 at `:583`; same file, 90 lines apart | open, one edit |

### (b) Genuinely needs compute

| item | cost | note |
|---|---|---|
| **M-A / R2** `-ksp_view` two-arm | 8 core-min | settles D10, D40 and 257 archived runs at once |
| **W1** stokesI wave tutorial | 5–15 core-min | B7's only capability-scale dead lever: wave machinery shipped into three solvers, **0 tracked files reference it**, against 1,825 for `alpha.water` |
| **Hump adjoint characterisation** | 40 core-min (A2) | the hump adjoint is **UNCHARACTERISED, not diagnosed**; it is R1 §6 item 2's second configuration |
| **PR-1 respecified** to a structurally different QoI | ~25 core-min | see §3 — the *support*-change version is now answered; the *quantity*-change version is not |
| **`w3-beta-on-omega-destruction-model-patch`** | unpriced | the **only** route to an external referent for the S1 line (S1C2 §2.5 item 2) |
| **Duct streamwise-profile deficit** | unpriced, needs a solving budget | ≥76% of the duct error; the largest open closure item |
| **Ladder B3 Stage 3** adjoint GMRES `KSP_DIVERGED_NANORINF` | unmeasurable until it runs | the cost itself is the unknown |
| **S1-priors** MAP arm + Hv | 260 core-min | **hold** until G-P4 is replaced (§2.2) |

### (c) Ill-posed, already answered, or the gate is broken

| item | why |
|---|---|
| **G2** | now **six** independent ways: bar 50% above the loss's own 32.71% top-decile ceiling; it scores the adjoint not the closure; noise passes at 60.8% while a strict amputation with worse physics passes at 53.7%; non-monotone under `np.quantile` when the deviating set is smaller than the quantile (D29); and — added here — it is **objective-invariant** (§2.1), so it cannot discriminate between objectives either, and it is **numerically exact** (§2.4), so none of the spread between published G2 values is noise |
| **G-P4** | **NEW (§2.2).** All three legs derivable from (β, g_QoI, λ_L2); a wrong posterior passes at 0.0e+00. Filed **D67**. Gates a 260 core-min item |
| **G-P2** | **NEW (§2.5).** Its stated mechanism — an 8.2× stronger prior pull unpins cells — is measured not to hold at the only archived state where it can be checked. Filed **D69** |
| **C2 sanity check** | already declared an identity by the lab ("reportable, never gateable") |
| **R5 / G-W2** | enabling premise measured false (D45); bar above ceiling; §2.1 removes the last route by which the premise could have been rescued |
| **R8 condition (a)** | measured absent (D45); §2.1 makes it worse — the geography survives a 7× change in the objective's support, so there is even less physical structure to key a transferable prior to |
| **PR-1 as specified** | **NEW (§2.1).** The support-change version is answered from disk. Filed **D68** |
| **W1-only arm** (~150 core-min) | "would score 8.4% and FAIL by construction" (S1C2 §5 #2) — arithmetic, not judgement |
| **R1's "nine gradient arrays"** premise | frame-scoped; 14 exist and two secant pairs are reconstructible. Filed **D70** |

**The brief asked specifically whether any other open question is gated on a measurement broken the
way G2 is. It is G-P4, and it gates the most expensive unrun item on the S1 board.**

---

## 2. The executed results

### 2.0 Controls, run before any new arithmetic was trusted

| control | result |
|---|---|
| C1 — evaluation 1 is the unperturbed state | `J_history` row 1 has penalty exactly 0 and β_min = β_max = 1.000000; `grad_eval001` vs the separately measured `grad_anchor8`, max abs diff **0.000e+00** |
| C2 — permute-invert-assert (R1's declared kill switch) | bijection **True**; `perm[inv]` and `inv[perm]` both the identity; `\|fields_beta[perm] − β_final_dv\|max` = **5.107e-15** against the record's 5.1e-15 |
| C3 — both published G2 values reproduce | **26.8571%** and **29.0476%**, to the digits published; window base rate 8.4429% (1,773 of 21,000) |
| C4 — the W2 support rebuilt from the objective's own box definitions | **2,970 cells = 14.14%**, against the pre-registration's stated 2,970 |
| C5 — the `cellProcAddressing` parser written for §2.4 | reproduces the archived `dv_to_serial_perm.npy` **entry for entry** |

**A provenance fact that governs every scaled quantity below, and that is not stated on any
existing surface:** `grad_eval*.npy` holds the **raw** `∂varianceU/∂β`, not the total gradient.
`invert_lbfgsb.py:95` saves `gv` straight from `runScript`'s `-gradout`; `:114` composes
`g_total = λ_QoI·gv + 2·λ_L2·(β−1)` host-side and never writes it. `‖gv1‖ = 1.221837e-04` and
`λ_QoI·‖gv1‖ = 1.986435e-01`, which is the `1.986e-01` the trajectory table prints. R1's
correlations are invariant to that positive scalar and are unaffected; **any curvature or balance
arithmetic is not**, and §2.2–§2.3 apply the scaling explicitly.

### 2.1 PR-1, settled from disk — and it closes R1's own question by R1's own rule

**What PR-1 asked for.** `S1_SENSITIVITY_VS_ERROR.md` §7: *"a second-QoI sensitivity map on CBFS at
β = 1 … Priced at 25 core-min"*, with the decision rule pre-registered in the same section:
*"If the second map's geography matches the first, reading 2 is confirmed outright and R5/R8 are
closed."*

**What is on disk.** `S1-cbfs-weighted-arm/cbfs_inv/grad_anchorw.npy`. Provenance established three
independent ways, because this is the load-bearing claim of the document:

1. `runScript_w.py:144` sets `b0 = np.ones(NCELLS)` unless `-betafile` is given, and `log.anchorw`
   carries no `-betafile`.
2. `driver_w.py:24` comments `LQOI = 1.0 / 27.465931825190644  # 1 / Jw_raw(beta=1), anchorw`, and
   `log.anchorw:18720` prints `OBJ Jw: 2.7465931825190644e+01` — an exact match.
3. `log.anchorw:18721` prints `GRAD n=21000 norm=7.3228773523e+00`; measured here
   **7.3228773523e+00**.

`ledger.csv`: `anchorw,END,…,rc=0,wall=505,core_min=16.83`. DV-order control: the weighted arm's
`dv_to_serial_perm.npy` is identical to the reinversion's.

**The objective is genuinely different.** `Jw = 5319·varUwin + 3591·varUrec`, two disjoint
`boxToCell` variances over `[0,6]×[0,2]` and `[6,16]×[−1,0.5]` (`runScript_w.py:79–105`) — 2,970
cells, against varianceU's 21,000. Same case, same mesh, same β = 1, same repaired inlet.

**Measured. Frame: all 21,000 cells, DV order, top decile = 2,100 cells by `|g|`, window
0 ≤ x/h ≤ 6, 0 ≤ y/h ≤ 2, cell centres from `2500/C`.**

| region | base rate | top decile of `\|g_varianceU\|` | top decile of `\|g_Jw\|` |
|---|---|---|---|
| in-window | 8.44% | 35.38% (×4.19) | 36.52% (×4.33) |
| upstream x<0 | 32.14% | **45.76%** (×1.42) | **45.57%** (×1.42) |
| above shear layer y>2 | 69.60% | 9.76% (×0.14) | 4.48% (×0.06) |
| downstream | 13.60% | 12.52% (×0.92) | 15.29% (×1.12) |
| on the W2 support | 14.14% | 42.33% (×2.99) | 45.33% (×3.21) |

| statistic | measured | chance |
|---|---|---|
| **Spearman(`\|g_varU\|`, `\|g_Jw\|`)** — carries the claim | **+0.9894** | ≈0 |
| Pearson — tail-dominated, reported not relied on | +0.9992 | — |
| **top-decile set overlap** | **1,975 of 2,100 = 94.05%** | 10% |
| G2 scored on each map | 35.3810% | 36.5238% |

**The comparator that gives this its scale.** R1's own *"second independent baseline gradient"* —
the same objective on a different (corrupted) inlet — agrees far *less* well: Spearman **+0.9450**
(R1's published figure, reproduced), top-decile overlap **61.14%**. **Changing the objective's
spatial support by a factor of seven moves the sensitivity geography less than repairing the inlet
did.**

**The identity hazard, stated rather than buried.** `Jw` is supported on the two boxes, so a high
**in-window** share of its top decile is partly derivable by construction from the mask, and it is
reported but not gated on. The leg that is **not** derivable is the share lying **off** the
support — reachable only by adjoint propagation — and the upstream share in particular, because no
box touches x < 0:

| | off the W2 support | upstream x<0 |
|---|---|---|
| `\|g_varianceU\|` top decile | 57.67% | 45.76% |
| `\|g_Jw\|` top decile | 54.67% | 45.57% |

The majority of the strongest sensitivities of an objective supported entirely on two boxes lie
**outside those boxes**, and the upstream shares agree to **0.19 percentage points**.

**Verdict, against R1's pre-registered rule.** The second map's geography matches the first.
By R1 §7's own text that confirms reading 2 outright and closes R5 and R8 — now on a measurement
with no null-pinning problem, no fitted first step, and no reference to β at all.

**What is NOT established, because the tempting conclusion overreaches.** R1 §6 named the second QoI
as *"e.g. reattachment length, or wall shear over the step face"* — a different **quantity**. `Jw`
is the same *kind* of functional (velocity variance against the same LES field) on a different
**support**. So this settles the support-change version of PR-1 and not the quantity-change
version. That distinction is the whole of §3's recommendation on PR-1: the remaining half is worth
buying, and it must be pre-registered as a structurally different quantity, because a
velocity-variance-on-a-sub-box variant is now **measured** not to be one.

### 2.2 G-P4 is degenerate — the restored gate cannot fail a wrong posterior

**The gate.** `S1_PRIORS_PREREGISTRATION.md` §4, restored by the chief 2026-08-11:
*"The gate is the ratio AND the cosine, against the plateau state … ratio 0.998441, cos 0.999542,
with rms‖β−1‖ 0.016502 as the third leg. A posterior treatment that cannot recover all three to 1%
fails its own control."* The restoration's stated reason: *"The **cosine** is the informative leg:
it is the only number here that carries whether the prior pull actually opposed the likelihood
gradient."*

**The withdrawal it replaced was right, and the replacement is the same defect in three parts.**
Recomputed from `beta_eval010.npy` + `grad_eval010.npy` (S1-cbfs-inversion, λ_QoI = 65.448,
λ_L2 = 1e-4): ratio **0.998441**, cos **0.999542**, rms **0.016502**, `‖g_total‖` **1.450369e-05**
— D9's figures, reproduced. Then:

| leg | what a treatment needs to reproduce it |
|---|---|
| rms‖β−1‖ | **β alone** — and β is an *input* to the gate. Zero new information. |
| ratio r | `2·λ_L2·‖β−1‖₂ / ‖g_QoI‖`. The numerator is the identity the withdrawal removed. The only new content is the scalar `‖g_QoI‖`. |
| cosine c | **fixed by the other two.** `ε² = 1 + r² − 2rc` with `ε = ‖g_total‖/‖g_QoI‖`. Solving for c gives **0.999542138470174**; measured directly, **0.999542138470174** — agreement **2.2e-16**. |

So the triple has exactly **one** degree of freedom beyond `‖g_QoI‖` — the angle between `g_QoI` and
`(β−1)` — and the gate reports it three times.

**Exhibited, not asserted.** Treatment W reports the **prior as the posterior**: covariance = prior
covariance, credible intervals straddling β = 1 in 100% of cells, rank 0. That is precisely the
shape falsifier **F1** exists to catch (*"the posterior credible intervals straddle β = 1 in a
majority of the separated-flow window cells"*). Handed the archived β and re-evaluating the same
`g_QoI`, its G-P4 is `ratio 0.998441, cos 0.999542, rms 0.016502` — **all three legs agree with the
targets to 0.0e+00 relative error. G-P4: PASS.** None of the three legs is a function of any
covariance, credible interval or Hessian, so the gate cannot see the defect.

**And the cosine is near 1 for a reason unrelated to the prior being right.** At any interior
stationary point `g_QoI + g_pen = 0`, hence `r = c = 1` exactly. The plateau is stationary to within
ε = 3.03e-02, so `c ≥ 1 − ε²/(2r) = 0.999540922` is **forced by convergence alone**; measured
c = 0.999542138. The published 0.9995 is *"the run converged"*, restated as an angle.

**What G-P4 does test, stated so a replacement can keep it.** Exactly two scalars: `‖g_QoI‖` at the
plateau state, and the angle between `g_QoI` and `(β−1)`. That is a sound **reproduction control on
the gradient**, and it would have caught the mismatched-evaluation error that produced the 1.684×
confusion. It is not, and cannot be, a control on a posterior. Filed **D67**. **S1-priors should not
buy 260 core-min against it.**

### 2.3 The secant curvature pair — R1's pricing premise, and what the archive actually holds

**The premise.** R1: *"No L-BFGS curvature pair (`y_k = g_{k+1} − g_k`) is reconstructible from any
completed run — the step `s_k` survives in the accepted-iterate files and its partner does not.
Buying curvature as fresh gradients is **forced, not chosen**, which is what prices the whole
Bayesian line."*

That is exact for **consecutive-iterate** pairs. It does not hold for **secant** pairs, which is all
a curvature probe needs: `invert_lbfgsb.py:96–97,120–121` keeps evaluation 1 *and every tenth
evaluation*, both the β and the gradient. Availability, executed:

| run | `grad_eval001` | `grad_eval010` | `beta_eval010` | secant pair |
|---|---|---|---|---|
| S1-cbfs-inversion | yes | yes | yes | **available** |
| S1-cbfs-reinversion | yes | yes | yes | **available** |
| S1-cbfs-weighted-arm | yes | — | — | no |

**Frame:** state A = evaluation 1 (β ≡ 1 exactly, control C1); state B = evaluation 10 (the matched
pair D9 established was written by the same `run_eval` call). `s = β₁₀ − 1`,
`y_QoI = λ_QoI·(gv₁₀ − gv₁)`, `y_penalty = 2·λ_L2·s`. By the mean-value form of the gradient map,
`sᵀy = sᵀH̄s` **exactly**, where `H̄` is the Hessian averaged over the segment — this is not a
finite-difference approximation.

| | S1-cbfs-reinversion (repaired) | S1-cbfs-inversion (corrupted) |
|---|---|---|
| ‖s‖ | 4.312344e+00 | 2.391395e+00 |
| `sᵀy_penalty` — **IDENTITY** `2λ_L2‖s‖²` | +3.719261e-04 (**0.05%** of `sᵀy_total`) | +1.143754e-03 (**62.17%**) |
| `sᵀy_QoI` — **the measurement** | +7.313133e-01 (99.95%) | +6.960815e-04 (37.83%) |
| `R_qoi = sᵀy_QoI/‖s‖²` | +3.932573e-02 | +1.217187e-04 |
| `R_prior = 2λ_L2`, every direction | +2.000000e-05 | +2.000000e-04 |
| **prior-preconditioned Rayleigh quotient** | **+1.966e+03** | **+6.086e-01** |
| free cells only (bounds inactive) | ρ = +1.952e+03 | — |

**Identity versus measurement, stated as the brief requires.** `sᵀy_penalty = 2λ_L2‖s‖²` is
derivable by construction from (β, λ_L2): any treatment knowing those reproduces it exactly,
*including one whose curvature is wrong*. It is reported above and is **never gated on**. `sᵀy_QoI`
requires `grad_eval010.npy`, an adjoint solve no closed form supplies. It is a measurement.

**Nulls, stated before the numbers.** N1: a flat objective (`H_qoi = 0`) gives `sᵀy_QoI = 0`, ρ = 0.
N2: the two gradients being the same array is identical to N1. N3: sign-randomised `y_QoI`, 200
draws, `E[sᵀy_QoI] = 0`. **Measured against N3: reinversion 6.6 sd, inversion 10.0 sd from the
null.** *Not* a null: anything computable from β and λ alone.

**Negative control — cross-pairing** `s` from one run with `y` from the other, a mismatched pair
with no shared state: `s(reinv)ᵀy(inv)/‖s‖²` = +1.289e-04 against the matched +3.933e-02;
`s(inv)ᵀy(reinv)/‖s‖²` = +1.764e-02 against the matched +1.217e-04. Two orders of magnitude wrong in
both directions.

**Out-of-sample control — does the secant curvature predict the objective history?** `J_history_main.csv`
is written from solver stdout and shares no array with `grad_eval*.npy`, so this scores the
curvature against an independent quantity:

| | actual ΔJ | linear only `gᵀs` | linear + ½`sᵀy` |
|---|---|---|---|
| S1-cbfs-inversion | −0.000921 | −0.001841 (**99.98% error**) | **−0.000921 (0.06% error)** |
| S1-cbfs-reinversion | −0.562398 | −0.758439 (34.86% error) | −0.392597 (30.19% error) |

On the corrupted run the objective is essentially exactly quadratic along `s` and the secant
curvature closes the gap the linear term leaves to **0.06%**, with the linear term alone 99.98%
wrong — the curvature carries the entire prediction. On the repaired run the step is 1.8× longer and
J moves 56% rather than 0.09%, so a quadratic leaves a 30% cubic-and-higher remainder; the sign and
magnitude are still right. Reported both ways rather than only the flattering one.

**What this establishes and what it does not.** It measures the **scale** of the data-versus-prior
curvature ratio in the one direction the optimiser actually travelled: ρ ≈ **1.97e+03** on the
repaired problem — strongly data-dominated — and ρ ≈ **0.61** on the corrupted one, prior-dominated,
which is the quantitative form of that run's plateau being a penalty/likelihood cancellation.
It does **not** answer falsifier **F2**, which asks about *decay* across several eigenvalues: one
direction per run, and the two runs are different problems (λ_QoI 24.8× apart, different baselines),
so they are not a spectrum. **The scale is free; the decay still costs gradient evaluations.**

**What it changes about the 260 core-min ask.** The prereg budgets ~120 core-min for 6 Hessian-vector
products and notes only that the first two will be checked for symmetry — a self-consistency check.
There is now a **correctness** check available at zero compute: an Hv along `s` must reproduce
`sᵀy_QoI` to the accuracy of the FD step. That converts the first Hv from a purchase into a
validated instrument before the remaining five are bought, against a measured external value rather
than against itself. Filed **D70**.

**Heavy-tail discipline.** Spearman carries every claim in this document. `|g(eval1)|` has
max/median **2.05e+06** (reinversion) and **1.14e+07** (inversion); a Pearson coefficient over that
dynamic range is a statement about a few hundred extreme cells and moves with tail shape. Reported
alongside throughout — `|g(eval1)|` vs `|g(eval10)|`: Spearman +0.9741 / Pearson +0.6449
(reinversion), Spearman +0.9976 / Pearson +0.8421 (inversion) — and relied on nowhere.

### 2.4 G2's numerical reproducibility, and the ordering trap that nearly manufactured a finding

`W4-defect-reach/run_cbfs_arm.sh` copies `0/`, `constant/`, `system/` and `runScript.py` from
`W4-adjoint-pc-unblock/cbfs_beta` and changes **one** thing: `decomposeParDict` to `simple [4,1,1]`.
Same image, same `DAFOAM_SUBPC_TYPE=lu`, np=4, β ≡ 1, same objective. Pure numerics, and the record
arm's gradient is bitwise identical to `S1-cbfs-inversion/cbfs_inv/grad_eval001.npy` (md5 `06fe8c50`)
— the array R1 scores at 31.19%.

**The trap, exhibited first because this document nearly fell into it.** Design-variable order
follows the decomposition, so the two arrays are in **different DV orders** and are a permutation of
one another: `max |sorted(|A|) − sorted(|B|)|` = **7.269e-10**, i.e. they hold the same values.
Compared unpermuted, Spearman is **+0.0901** and G2 reads **31.19% vs 14.10%** — a 17-point
"decomposition destroys the geography" finding is available to anyone who skips the permutation.
`DEFECT_REACH_decomposition_cases.md:256–266` did **not** skip it and says so explicitly
(*"Gradients mapped to serial cell ordering via each arm's `cellProcAddressing` … both maps verified
as exact permutations"*); this section is an independent confirmation of that statement, not a
correction to it.

**Permuted, in serial cell order.** Both arms' `cellProcAddressing` survive on disk. The parser
written for this was validated first: **the map it builds for arm A is identical to the archived
`dv_to_serial_perm.npy`, entry for entry.** Per-rank cell counts A `[5254, 5204, 5262, 5280]`
(scotch) and B `[5250, 5250, 5250, 5250]` (simple 4×1×1).

| quantity | measured | independently published |
|---|---|---|
| `‖A−B‖/‖A‖` | **1.132e-04** | 1.13e-04 (`DEFECT_REACH…:263`) |
| top-20 `\|g\|` cells, max rel / median rel | **1.582e-04 / 3.955e-05** | 1.58e-04 / 4.0e-05 (same row) |
| Spearman(`\|A\|`,`\|B\|`) | +0.99999988 | — |
| **G2, arm A (scotch)** | **31.1905%** | 31.19% (R1) |
| **G2, arm B (simple 4×1×1)** | **31.1905%** | — |
| **delta under a lever with no physics in it** | **+0.0000 pp** | — |
| top-decile set agreement | **2,100 of 2,100 = 100.00%** | — |

Reproducing two independently published figures from a different route is the positive control on
the whole pipeline.

**Reading, with its frame.** Every G2 figure in the corpus — 29.0476, 26.8571, 35.38, 31.19, 32.71,
42.7 — is published to four or more significant figures with **no stated uncertainty**. This supplies
one, and the frame is narrow: it is reproducibility under a **domain-decomposition change** on the
corrupted-inlet baseline gradient, **one replicate**, not a general error bar. What it licenses is
narrow and useful: **none of the spread between published G2 values is numerical noise from this
source**, so every difference between them is a difference in the field being scored. That
strengthens R1's conclusion — the 35.38% baseline-sensitivity figure is not an artefact — and it
removes "the decomposition defect might be moving G2" from the list of live doubts.

### 2.5 G-P2's stated mechanism, at the one state where it can be checked

**The gate.** *"Under the lognormal prior the restoring pull at β = 0.2 is `2λ_LN·log(0.2)/0.2` =
1.309e-4 against the Gaussian's `2λ_L2·(0.2−1)` = 1.600e-5 — **8.2× stronger**. Prediction: the count
of cells at the lower bound falls from 223 to fewer than 60."*

The two pulls reproduce: **1.3090e-04** and **1.6000e-05**, ratio **8.18×**. But whether a cell
unpins is not decided by prior-versus-prior. It is decided by prior pull versus **likelihood** pull
at that cell, and the likelihood pull is on disk.

**Frame, stated rather than glossed.** The **final** state has 223 low + 1 high, but its gradient is
deleted by `invert_lbfgsb.py:96–97`. Evaluation 10 is the only archived state where β and its
gradient can both be read, and it is early in the trajectory: **5 cells** sit at the lower bound
there, not 223.

At those 5 cells, `|g_QoI| = λ_QoI·|gv₁₀|`: min 4.6498e-04, median 6.8796e-04, max 1.8206e-03.
**100% (5 of 5) exceed the lognormal restoring pull**, and 100% exceed the Gaussian pull actually in
force. The median likelihood pull is **5.3×** the lognormal prior's restoring pull.

**Bounded reading.** At every archived pinned cell the likelihood pull already exceeds the *stronger*
prior's restoring pull by a factor of several, so the 8.2× prior ratio does not by itself imply
unpinning — the comparison G-P2 makes is between two priors, and the quantity that decides the
outcome is a third. n = 5 and the state is not the one G-P2 grades: **this is a caution on the
mechanism, not a measurement of the gate**, and it is filed as such (**D69**). It is enough to say
that G-P2's "<60" is not supported by the argument given for it, and that a gate whose stated
mechanism is the wrong comparison should be re-derived before 260 core-min is spent partly to test
it.

---

## 3. The compute asks, ranked, with the discriminating outcome for each

The chief's standing list, re-ranked from the data. **Nothing here is authorised and nothing was
run.** Compute authorisation is Katie's.

### Rank 1 — **M-A / R2, `-ksp_view` two-arm, ~8 core-min. BUY FIRST.**
Unchanged from the chief's ranking, and the data supports it. **Discriminating outcome, all three
pre-stated and all three move belief:** the two PETSc dumps report the **same** ordering → the lever
is **DEAD**, 257 archived runs' `rcm` citations are void and D40's prediction P6 must be struck
rather than cited as confirmed; they **differ** and each matches its request → **ACTIVE**, P6's null
becomes meaningful and the 257 runs inherit a proven lever; **neither dump carries an ordering
line** → NO VERDICT, which is itself a statement about what this build exposes and is the direct
argument for the effective-value echo D10 asks for. It is the only item on the board that answers a
question for 257 runs at once, and it is the cheapest.

### Rank 2 — **W1 stokesI wave tutorial, ~5–15 core-min. BUY SECOND.**
**Discriminating outcome:** the wave machinery runs and produces a wave → a capability three solvers
declare and no run has ever exercised is real, and R9/S6 becomes blocked on development rather than
on an unknown; it fails to run → the entire seakeeping branch, including the filed 135 core-min
`f7-seakeeping-added-resistance-capability-step`, is blocked on **development**, and buying that
proposal now would be buying a stage that cannot execute. Either outcome changes what the naval
queue is allowed to claim. B7's measurement — **zero tracked files reference any wave machinery
against 1,825 mentioning `alpha.water`** — is a dead-lever finding at capability scale, and this is
its cheapest possible test.

### Rank 3 — **Hump adjoint characterisation, ~40 core-min (A2). BUY THIRD, and reframe why.**
Its usual justification is R8, and R8's condition (a) is measured absent (D45) and made worse by
§2.1 — so *"buy the hump to enable R8"* is buying the second half of a direction whose first half
failed. **The justification that survives is different and better:** R1 §6 item 2 names a second
configuration as the *other* discriminating experiment, and §2.1 has just closed the first one.
**Discriminating outcome:** the hump adjoint converges → a second flow becomes available and the
question *"does the sensitivity geography move with the boundary layer or with the objective"* gets
its second half, which §2.1 cannot supply because it never leaves CBFS; it does not converge → the
record replaces *"UNCHARACTERISED, not diagnosed"* with a diagnosis, which is itself the thing
`PRODUCT_LIST.md` §4A was corrected on 2026-08-11 to admit it lacks. *Caveat stated: I did not read
A2's M1/M2 arm designs. I am ranking the hump-adjoint characterisation, not adjudicating that
specific two-arm spec.*

### Rank 4 — **PR-1 at 25 core-min. DO NOT BUY AS SPECIFIED. Respecify, then it is worth it.**
§2.1 executed PR-1's comparison at zero compute and it returned the outcome R1 pre-registered as
closing the question. Buying a third velocity-variance-style map would be buying a measurement whose
result is now predictable: two objectives differing by a factor of seven in support agree at
Spearman +0.9894 and 94.05% top-decile overlap, so a third of the same kind will agree too.
**An experiment whose every outcome leaves belief unmoved should not be run, and PR-1 as filed is
now in that condition.** Respecified, it is the best 25 core-min on the board: the QoI must be a
**structurally different quantity** — a force, an integrated wall shear over the step face, a
reattachment location — not another velocity-matching functional on another region, and the
pre-registration must argue *why* it is structurally different, since the support-change version has
now been measured not to be. **Discriminating outcome of the respecified item:** the new map's
geography differs → sensitivity geography is objective-dependent after all and the upstream
deposition is partly a property of what we asked for; it matches → the geography is a property of
the linearised flow operator itself, which is a genuinely publishable identifiability statement and
the strongest form of R1's reading 2.

### Rank 5 — **a/512 rung, 760–1,520 core-min. DO NOT BUY. The chief's recommendation is right.**
Confirmed, and on independent grounds: G1a already records it as exploring a direction shown to be
small, and **R3 costs zero and would decide whether the reference is where the disagreement lives**.
Buying 760–1,520 core-min of mesh before a zero-cost check on whether the benchmark is
single-sourced is the ordering the calibration scorecard's 0-of-3 record exists to discourage.

### Held rather than ranked — **S1-priors, 260 core-min.**
Not a "no". **Hold until G-P4 is replaced** (§2.2, D67) and G-P2 re-derived (§2.5, D69). Two of its
four gates cannot presently fail or rest on the wrong comparison, and the proposal JSON that an
agent would dispatch from still carries the **withdrawn** G-P4 (D41). Spending 260 core-min against
gates in that condition is the defect this lab spent 2026-08-11 cataloguing.

### Cheaper experiments proposed, that discriminate more per core-minute

- **Z-1 — the free first-Hv correctness control. 0 core-min of new compute.** Whichever Hv machinery
  S1-priors builds, its first product along `s = β₁₀ − 1` must reproduce `sᵀy_QoI` = **+7.313133e-01**
  (reinversion) to FD accuracy. **Discriminating outcome:** it reproduces → the instrument is
  validated against an external measured value before five more are bought; it does not → the Hv
  machinery is wrong and 120 core-min is saved. The prereg's planned symmetry check
  (`v₁ᵀHv₂` vs `v₂ᵀHv₁`) is self-consistency and passes for a consistently-wrong operator; this does
  not. Costs nothing and strictly dominates.
- **Z-2 — the proposal-rot sweep (D41). 0 core-min.** `t_preregistration > t_proposal` over
  `agenda/proposals/`. **Discriminating outcome:** it returns rot → dispatch surfaces are stale and
  the detector becomes standing machinery; it returns clean → D41 is a single instance and closes.
  D41 is already a confirmed positive (the S1-priors JSON gates on the withdrawn G-P4), so the sweep
  has a guaranteed positive control built in. It is the only finding on the board sitting on a
  surface an agent **acts** from.
- **Z-3 — recover the S1 line's remaining secant information. 0 core-min.** §2.3 used one pair per
  run. `beta_accept_iter001..011` are all archived; each accepted iterate paired with `grad_eval001`
  gives a further *directional* first-order check, and `beta_fd.npy` plus the FD logs at
  `primalTol 1e-8` are an independent curvature probe on three cells nobody has cross-read against
  the secant. **Discriminating outcome:** the FD-derived and secant-derived curvatures agree → the
  scale in §2.3 is confirmed on a second route; they disagree → one of the two is wrong and it
  matters before any Hv is priced.

---

## 4. What this document does not establish

- **No submission, no send, no registration, no scoring call.** The scoring-call ledger stands at 6
  and calls are chief-authorized. None was made. Nothing was uploaded or contacted.
- **No physics claim about where model-form error lives.** §2.1 sharpens an identifiability
  statement and does not refute the physical reading, which R1 correctly recorded cannot be refuted
  by measurements of this kind: the adjoint is loud upstream partly *because* upstream β propagates
  into the downstream loss, which is the mechanism the physical reading posits.
- **No answer to falsifier F2.** §2.3 measures the curvature *scale* in one direction per run, not
  the *decay* of a spectrum.
- **No general error bar on G2.** §2.4 is one replicate under one lever.
- **No verdict on G-P2 itself.** §2.5 checks its stated mechanism at n = 5 in a state the gate does
  not grade.
- **The hump was not opened**, no A2/M1/M2 arm design was read, and no naval artifact was touched.

## 5. Reproduction

One script, host-side, numpy + scipy only, ~25 s, no solver:
`S1_zerocompute_2026-08-14/scripts/s1_zerocompute.py`, full output archived beside it at
`S1_zerocompute_2026-08-14/logs/s1_zerocompute.out`. It runs as `__main__` and imports no
scratchpad-local module, so docket D1/D1a's stale-bytecode hazard does not apply; `__pycache__` was
cleared before each execution regardless.

Every input array is named with the evaluation it came from, in §2 and in the script's §S0. All
inputs live **outside the repo** at `/home/ubuntu/certonomous-runs/`, invisible to any repo-scoped
grep — this shell's `grep` is `ugrep --ignore-files` and honours `.gitignore`. The gradient
enumeration used `find`; the log reads used `/usr/bin/grep`.

**Frames used, never mixed:** cell centres come off disk in **serial** cell order; the gradient and
β arrays are in **DV** order; `C_serial[perm[i]]` is the centre for DV index *i*. §2.1–§2.3 and
§2.5 work in DV order; §2.4 works in serial order, because the two decomposition arms have different
DV orders and serial is the only frame common to them. *An earlier draft of §2.4 scored serial-order
arrays against a DV-order window mask and returned G2 = 0.0000% for both arms; the published-value
control (R1's 31.19%) caught it. The control is in the script for that reason.*

## 6. Docket rows filed

**D67** (G-P4 cannot fail), **D68** (PR-1's deliverable was already on disk), **D69** (G-P2's stated
mechanism is the wrong comparison), **D70** (the archive holds 14 gradient arrays and two secant
pairs; R1's pricing premise is frame-scoped). IDs checked against `docs/DOCKET.md` immediately before
filing, per W-4. **D63–D66 were all taken by concurrent sessions while this work was running** — the
highest free ID moved twice between opening the docket and writing to it — so these took the next
free numbers rather than colliding, and nothing was renumbered. **D66 is the sibling of §2.2**: a
separate W-2 sweep landed the same defect class (a gate whose answer is derivable from its own
inputs) on four other pre-registrations the same evening. G-P4 is a fifth instance and is filed as
its own row rather than merged into theirs, because its item is unrun and therefore repriceable.

## Related

- `ladder-b/S1_SENSITIVITY_VS_ERROR.md` (R1 — the document this one extends and, in §2.1 and §2.3,
  corrects at its own request)
- `ladder-b/S1_PRIORS_PREREGISTRATION.md` §4 (G-P1–G-P4), §8 (the withdrawal G-P4 was restored from)
- `ladder-b/S1_CBFS_WEIGHTED_ARM_RESULT.md` (the arm whose anchor gradient §2.1 reads)
- `DEFECT_REACH_decomposition_cases.md` §CBFS (the decomposition pair, and the permutation §2.4 confirms)
- `campaign/RESEARCH_DIRECTIONS_2026-08.md` (R1–R10), `campaign/CLOSURE_STAGE1_AND_C2_STATUS.md` §5
- `docs/DOCKET.md` D9, D29, D40, D41, D45
