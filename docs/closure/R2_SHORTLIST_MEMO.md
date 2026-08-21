# R2 — Candidate shortlist memo

**For R3.** Prepared by the closure team, 2026-08-21, under
`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md` Part 3 R2. **Documentation only: nothing was
trained, fitted or solved to produce it.**

**R3 is Sanaa's decision. This memo ranks and argues; it does not choose.**

---

## 1. Summary

**The ranking is not the doctrine's listing order, and the reason is a measurement.** R2 named the
expected finalists as *TBNN-class, FIML-C, SpaRTA-class* and required them to be **argued, not
assumed**. Argued, the order inverts:

| Rank | Class | The one-sentence reason |
|---|---|---|
| **1** | **SpaRTA-class** (symbolic `bijDelta` + `kDeficit`) | It predicts the *only* correction combination this lab has measured to work, and its injection path is already built and validated here. |
| **2** | **FIML-C** (corrections inside the transported equations) | Structurally it is the doctrine's own sentence — corrections inside the solved equations, closing the `k` budget by construction — and it carries the corpus's only cross-geometry, cross-`Re`, cross-solver a-posteriori evidence; but the adjoint it needs does not exist here yet. |
| **3** | **TBNN-class** (anisotropy only) | It predicts `b` alone, which is the exact thing measured to fail here three separate ways, and it leaves the realisable set on the out-of-family case. |

### The constraint that decides the ranking

**Three measured legs, and they must be stated together.** All are re-solved, not a-priori.

**(i) `b`-only fails with `k` TRANSPORTED — even the TRUE anisotropy.** Injecting the exact LES
anisotropy and letting `k` transport makes velocity **worse**: `AR_1_Ret_360` `U_rms`
**0.32151** against the SST baseline's **0.1985**, a **+62.0% increase**; `AR_3_Ret_360`
**0.28980** against **0.1846**, **+57.0%**; `CBFS13700` **0.0843** against **0.0516**, **+63%**.
**Three of three.** Registered gate H0 was "truth injection must cut `U_rms` >= 30%". **GATE FAIL.** (`Wu2018_PIML_RF/aposteriori/RESULTS.md`, `79a73944`, `96a19d09`;
independently reproduced in `Kaandorp2020_TBRF/aposteriori/RESULTS.md`, `0ebc9d53`. Both verdicts:
**NOT A RESULT**.)

**(ii) `b`-only fails with `k` FROZEN, even at the exact `k_LES`.** Six of six ceiling cases fail
(`62f781d0`, `Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md` §1):

| case | arm S (`k` = SST) | arm L (`k` = `k_LES`) |
|---|---|---|
| `AR_1_Ret_360` | +5.9% FAIL | **-22.2%** FAIL |
| `AR_3_Ret_360` | +3.2% FAIL | **-28.9%** FAIL |
| `CBFS13700` | +110.2% FAIL | **+136.6%** FAIL |

Arm L uses information unavailable at prediction time and *still* falls short of the 30% gate on
the ducts, and makes `CBFS13700` **137% worse**.

**(iii) `bijDelta` AND `R` with `k` transported SUCCEEDS.** The `TRUTH+R` control on
`AR_1_Ret_360`: `U_rms` **0.00341** against SST's **0.1985** — a **98.3% reduction** — with
transported `k` recovering to **43.465** against a truth of **43.418** (0.1%) and secondary flow
**1.4963%** against DNS **1.508%** (0.8%), converged in **383 iterations**. On `CBFS13700`,
`U_rms` **0.03073** against **0.0516** (40.4% reduction). Independently, the W2 SpaRTA campaign
injected `b^Delta` **and** `R` as static fields on PH10595 and measured
`eps(U)/eps(U_0)` = **0.003331** (pre-registered primary convention; **0.001253** volume-weighted)
against a k-omega SST baseline of 1.0 — **a 300x error reduction**, clearing its registered
`< 0.005` band (`W2_SPARTA_FROZEN_CBFS.md` §RESULT).

> **Citation defect found while writing this memo, and it is not load-bearing but it must be
> fixed.** Five lab records — the two a-posteriori `RESULTS.md`, two drafts, and the promoted
> copies in `NUMERICS_KNOWLEDGE.md` and `LESSONS.md` — quote **0.0017** as *the lab's own* W2
> measurement and point at `W2_SPARTA_FROZEN_CBFS.md`. **That file does not contain 0.0017.**
> 0.0017 is **Schmelzer's published 0.00165 rounded to two significant figures**. The lab's measured
> value is 0.003331. The qualitative claim those records draw from it — b+R propagates, b-only does
> not — is unaffected.

> **The correction must close the `k` budget and co-evolve with the flow.** An anisotropy field,
> however accurate, is not a closure model here. **That single sentence is the ranking.**

### This memo does not lean on a-priori scores anywhere, and here is why

**A-priori `b` accuracy can invert the a-posteriori ordering.** On `CBFS13700` arm L
(`aposteriori_frozenk/RESULTS.md` §4), ranked by anisotropy accuracy the order is
TRUTH < ML < NULL; ranked by velocity it is **ML (0.0415) < NULL (0.0498) < TRUTH (0.1179)**. The
learned field is **16% better than NULL** while the **exact** anisotropy is **137% worse**, and
puts reattachment at **9.088** against an LES truth of **4.170**.

The literature says the same: **Duraisamy 2021 p. 10** — "successful a priori evaluation is neither
a necessary nor a sufficient condition"; **Beck & Kurz 2021 p. 26** — a closure at **99.9%** a-priori
cross-correlation whose "LES solution diverges strongly soon after".

### What would change this ranking

1. **A working field-inversion adjoint here** would move **FIML-C to rank 1** — it is the only
   candidate whose structure satisfies the doctrine without an added head.
2. **A TBNN-class model with an `R`/`kDeficit` head**, shown a-posteriori, would collapse the gap to
   SpaRTA-class; the choice would then be symbolic versus network, not `b` versus `b+R`.
3. **A hump a-posteriori result** for any class. There is none (§6).
4. **Evidence that SpaRTA-class cannot reach the hump's feature regime** — 31.79% of hump cells are
   out of training range on 49 of 110 features.

---

## 2. SpaRTA-class — rank 1

**What it predicts.** Two fields inside the solved equations: an anisotropy correction `bijDelta`
**and** a `k`-equation residual `kDeficit`. **This is leg (iii) exactly.**

**How it trains and embeds HERE.** Every artefact exists, verified by inspection:
`sdk/openfoam/sparta/kCorrectiveFrozenFoam/` extracts the frozen fields,
`sdk/openfoam/sparta/spartaTurbulenceModels/` carries `kOmegaSSTFrozen`/`kOmegaSSTCorrected`/
`kOmegaSSTSparta`, `sdk/scripts/sparta_regression.py` fits — validated end to end in the W2 campaign
and recorded **PASS** at both gates in `Schmelzer2020_SpaRTA/RESULTS.md`. **This is the only
candidate whose injection path is already proven here.**

**Generalisation evidence, shown.** Schmelzer Table 2 (arXiv preprint p. 15), a-posteriori
`eps(U)/eps(U_0)`, leave-one-case-out by CFD: `M(1)` **0.22287** (PH10595), **0.21146** (CD12600),
**0.30413** (CBFS13700); `M(3)` **0.22744 / 0.22422 / 0.30655`. **Every discovered model is below
0.41 on cases it was not fitted to.** The `PH37000` extrapolation — 3.5x the training Reynolds
number, against experiment — is reported as a significant improvement but **graphically, with no
number** (Fig. 12, p. 26); it is evidence, not a datum.

**What it needs to become a one-model candidate.** Little. It already emits both fields. It needs
(1) a **single** model fitted across all training families rather than per-case leave-one-out, and
(2) the FS4 frozen protocol applied to its feature library.

**Build cost.** Frozen extraction **6.0 s** per case (measured). Fit **0.04 core-hours** for the
verification pass; the underlying campaigns cost **27.7 core-min** (frozen) and **137 core-min**
(regression/discovery). Propagation solves measured at **1.08 core-hours for 33 solves =
~0.033 core-h/solve** (`aposteriori_frozenk`). **A full build is single-digit core-hours.**

**Risks.** The symbolic library is truncated — Schmelzer uses **4 of Pope's 10 tensors and 2 of 5
invariants**, a 2-D-complete quadratic form, and **no duct case appears in that paper**. Its own
frozen ceiling on `CBFS13700` is **0.22703**, so the correction *form* is weak there before any
regression. Model selection in the paper touched the a-posteriori answer (hand-selection from
52-136 candidates), which FS4 must forbid here.

---

## 3. FIML-C — rank 2

**What it predicts.** A correction field inside the transported equations — a multiplier or source
on the production term — not a stress. **Continuity by construction**, and the `k` budget closes
because the correction lives in the `k` equation.

**How it trains and embeds HERE — this is the weak leg, and it is specific.** The embedding side is
fine: `kOmegaSSTSparta` already accepts a `kDeficit` field, so a learned production correction has a
home. **The adjoint is the problem.**
  Cross-team note (2026-08-21): the DAFoam team's B3 unblock work (ILU-shift / PCLU rebuild)
  is live; if it lands, this gap narrows. Cited here as **pending**, not as existing capability.
- `import dafoam` **fails** in the lane's Python; `sdk/chief_engineer/docker_dafoam.py` is the
  **compressible transonic** `DARhoSimpleCFoam` wing pipeline (ONERA M6 / CRM acts), not a closure adjoint.
- The FD-verified adjoint is **shape/patchV design-variable class**: `A3_SUBLU_RESULT.md` says the
  gradient "**may be used as a number for patchV/shape-class work at this rung**".
  `DAFOAM_CASE_STATUS.md`: CD/patchV **0.23% PASS**, CL/patchV **0.23% PASS**, CL/shape **1.67%
  PASS**, **CD/shape FAIL** on a real sign-flipped component.
- The transonic adjoint **never converged** (`DIVERGED_BREAKDOWN` at 21,840 / 42,120 / 79,560 /
  99,840 cells), and `R5_ADJOINT_CONDITIONING.md` states verbatim: "**No finite-difference gradient
  verification was performed, on any configuration, at any point in this investigation.**"
- **No per-cell field design variable exists anywhere in `sdk/` or `cases/`.**

**So the honest statement of criterion (a) is: an FD-verified adjoint exists, for the wrong
design-variable class, and has never been run for this use.**

**Generalisation evidence, shown — and it is the best in the corpus.** Singh, Medida & Duraisamy
2017: trained on **S814 at `Re = 1e6` and `2e6` only**, applied to S805, S809 and S814 across
`1e6/2e6/3e6` with **`Re = 3e6` never in any training set**; the separation-bubble length on the
NASA wall-mounted hump was "**15% more accurate**" (arXiv preprint p. 31); overhead "**< 10% of
additional compute time**" (p. 22); and the trained model was embedded in **AcuSolve, a different
unstructured finite-element solver, and reproduced the improvement** (pp. 20-21). **That is the
only cross-solver portability demonstration in the 33-work corpus.**

**What it needs to become a one-model candidate.** A field-inversion adjoint: a per-cell design
variable over the production term, with an FD table before any gradient is trusted. The doctrine's
R4 requires exactly that ("S1's FD-verified adjoint engine ... carry over"), and **the engine that
carries over is verified for shape, not for fields.**

**Build cost.** The largest of the three and the least certain. Adjoint development is not costed
here because nothing comparable has been run; the shape-class FD arm alone cost **29.5 core-min**
for one rung, and the transonic conditioning investigation consumed multiple rungs without ever
converging. **Estimate: tens of core-hours, with a real risk of not converging** — which is why it
is rank 2 and not rank 1.

**Risks.** The adjoint may not converge for this design-variable class, exactly as it did not for
the transonic shape case. Singh 2017 reports **no error metric for any flow field** — its two
numbers are the 15% bubble length and the <10% overhead — so its evidence is directional. Its
best model was selected "by exploring several combinations of the data-sets", an unquantified
spread.

---

## 4. TBNN-class — rank 3

**What it predicts.** The anisotropy `b` alone, as `sum g^(n) T^(n)`.

**How it trains and embeds HERE.** Training is cheap and proven: TBRF trained in **17.79
core-hours** (52 forests x 100 trees, inside a 60-core-hour authorisation). The embedding path is
the same `bijDelta` injection SpaRTA uses. **The problem is not the plumbing; it is that the field
it emits is the one measured to fail.**

**Generalisation evidence — and note what kind it is.** Ling Table I (preprint p. 11) is
**a-priori**: duct `Re_b = 2000` LEVM **0.23** / QEVM **0.18** / TBNN **0.13** / plain MLP
**0.33**; wavy wall **0.18 / 0.11 / 0.08 / 0.09**. Kaandorp Table 4 (preprint p. 41) is the
class's one a-posteriori integral number: BFS `Re = 5100` reattachment RANS **5.45**, RANS+`b_TBRF`
**6.32**, DNS **6.28** — baseline 13.2% short, corrected 0.6% beyond. Kaandorp Table 3 (p. 37)
shows features dominate the model class: 5 features TBRF **0.0995** / TBNN **0.0871**; 17 features
TBRF **0.0521** / TBNN **0.0681**.

**But this lab's own runs of this class returned NOT A RESULT twice and GATE FAIL on all three
preregistered claims once.** TBNN put **6.47-15.34%** of test cells outside the barycentric triangle
against a truth of **0.79%** and SST's **0.10%** — while a plain MLP with **no** tensor basis sat at
**0.88-2.66%**, within 2x of the truth. The lane's conclusion: "**Embedding the tensor basis buys
Galilean invariance and buys nothing else**", and "**Pope's tensor basis buys in-domain accuracy and
buys out-of-domain catastrophe.**"

**The TBRF run failed constraint (1) outright.** Its held-out `b_rms` was **6.382 +/- 2.110**
against SST's **0.5843** — **10.9x worse** — and it also lost to the train-mean predictor
(**0.4718**) and to `b = 0` (**0.6002**). Realisability, claim (iii): **0.0752 +/- 0.0129** of cells
unrealisable against the truth's own **0.0159**, **4.7x**, GATE FAIL; on `CBFS13700`, **19.2%**.
**No candidate in this class has yet beaten the trivial baseline.**

**What it needs to become a one-model candidate.** A `k`-equation treatment — an `R`/`kDeficit`
head, or the FIML-style route of correcting inside the transported equations. **Without one it is
disqualified by leg (i) and leg (ii), not disfavoured.** With one, it is SpaRTA-class with a
network in place of a symbolic expression, and the realisability question remains open.

**Build cost.** Training **17.79 core-h** measured (9.69 preregistered + 8.10 post-hoc, 52 forests
x 100 trees). **Adding an `R` head is the real cost and is unestimated.**

**Risks.** Realisability (measured, three seeds). Basis rank: per-case means **3.006-3.987** on
2-D training data, so `g^(5..10)` are unconstrained and blow up out-of-family. A-priori `b` scores
do not predict a-posteriori velocity (§1).

---

## 5. Comparison

| | SpaRTA-class | FIML-C | TBNN-class |
|---|---|---|---|
| Predicts | `bijDelta` **+** `kDeficit` | correction inside transported eqns | `b` only |
| Satisfies leg (iii)? | **yes, by construction** | **yes, by construction** | **no — needs an added head** |
| Injection path here | **built + W2-validated** | `kDeficit` slot exists; **adjoint missing** | built (same slot) |
| Training engine here | `sparta_regression.py`, **proven** | **none for field design variables** | proven (17.79 core-h) |
| Cross-geometry evidence | Table 2, **0.211-0.404** a-posteriori, leave-one-out | Singh 2017: unseen `Re`, unseen airfoils, **different solver** | Table 4 reattachment **6.32** vs DNS **6.28**; rest a-priori |
| Anisotropy for duct+hill+hump | yes (4 of 10 tensors) | indirect (via production) | yes (10 tensors) |
| Realisability risk | not measured here | n/a (no `b` emitted) | **GATE FAIL x3** |
| Build cost | **single-digit core-h** | **tens, may not converge** | 17.79 core-h + unestimated head |
| Biggest risk | truncated basis; CBFS ceiling **0.22703** | adjoint may not converge for this class | emits the field that fails |

**Criterion (c), the anisotropy requirement, is not in dispute for any candidate.** Linear
kOmegaSST captures duct secondary flow at **6.1e-16%** `U_bulk` (`AR_1_Ret_360`) and **2.4e-15%**
(`AR_3_Ret_360`) against DNS **2.22%** and **2.07%** — machine-precision zero, "fail, expected &
documented" (F6c, `verification/campaign/F6_closure_aligned_flows.md`; baseline `e2c45ab9`). On the
hump, kOmegaSST over-predicts reattachment by **+63% to +66%** (F6a). **All three classes clear
criterion (c); it separates none of them.**

**FS2 constrains all three equally** (`8a380cb9`, `be02937d`,
`_common/features/FS2_DEGENERACY_REPORT.md`): duct feature-matrix rank **96 of 110** with **48
algebraically-zero features** and condition number **1.2e+33**; **no family reaches full rank**;
`NASA_2DWMH` has **31.79%** of cells outside the training range on **49 of 110** features; **58 of
110 features are not Galilean invariant**. Tensor-basis per-cell rank: **case means 3.006-3.987,
mean of case means 3.738, maximum rank 5 in any cell of any case** — so `g^(5..10)` are
unconstrained for every tensor-basis candidate. *(That table also resolves the dangling `3.24`
pointer flagged in charter §5(b): 3.24 was a pooled-sample statistic, not a case mean, and the two
are not interchangeable.)*

---

## 6. What this memo cannot see

- **No hump a-posteriori result exists, for any class, and the reason is mechanical.**
  `NASA_2DWMH` is **BLOCKED** in every lane on a missing
  `libfrozenIncompressibleTurbulenceModels.so` / `AugmentedkOmegaSST`. The hump is one of the eight
  scored cases, it is the case the a-priori study failed, and **no candidate has been re-solved on
  it.** Every propagation number above comes from ducts and `CBFS13700`.
- **`CBFS13700` is in-sample** for the Wu2018 forest in every lane that uses it, including the
  inversion result of §1, which the source file states "**carries no generalisation claim**".
- **The TBRF a-posteriori table has gaps**: `AR_3_Ret_360` ML seeds and all six `CBFS13700` rows are
  PENDING. The lane argues no pending row can move H0; the table is still incomplete.
- **The continuity instrument has a floor at the hump.** The registered continuity gate was applied
  in `96a19d09`; the div-based instrument's resolution there is not established, so a hump
  continuity claim cannot currently be graded.
- **No FIML run has ever been made in this lab.** The adjoint exists, is FD-verified for
  shape/patchV, and is **untested for field inversion**. Rank 2 rests on structure and literature,
  not on a local measurement.
- **Single-`Re` families.** The duct cases sit at one `Re_tau` each; nothing here tests `Re`
  extrapolation of any candidate.
- **All local evidence comes from one benchmark clone** (`deb91557`), one solver
  (OpenFOAM v2606), one baseline closure (k-omega SST).
- **Every candidate must still beat the train-mean tensor**, which beats SST on **8 of 8** held-out
  cases (`_common/BASELINES.md` §6.4). **No candidate has been shown to do so a-posteriori.**
- **`Xiao2016_EnKF/` exists but is empty of results**, so the derivative-free training route that
  would sidestep the adjoint is unassessed.

---

**R3 is Sanaa's decision; this memo ranks, it does not choose.**
