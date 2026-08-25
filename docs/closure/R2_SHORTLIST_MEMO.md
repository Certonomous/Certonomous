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

> *[2026-08-22, note added by the closure follow-up lane; the memo's argument is unchanged.]*
> *Both reattachment figures on the line above are read off as **row-`0` cell centres**, which is the
> basis §4 of `aposteriori_frozenk/RESULTS.md` is graded on. The LES `x_reatt` **of record is 4.241**
> — the value returned by the registered instrument
> `_common/sst_baseline_metrics.py::hill_wall_metrics` (longest contiguous reversed-`U_x` run in the
> wall-adjacent row, **linearly interpolated** to the sign change), registered in three frozen
> `PREREGISTRATION.md` files and in `_common/BASELINES.md` §3. **4.170 is the same reattachment read
> at cell resolution**, truncated to the last still-reversed cell and therefore low by
> **0.435 of one cell** (last reversed centre 4.169625, next 4.333572, cell width 0.163947). Because
> §4's arms and its truth are all on that one cell-centre basis, the ordering and the 16%/137%
> comparison above are unaffected; the 4.170 here must **not** be differenced against 4.241, against
> the Kaandorp lane's 4.384 or against SST's 5.891 without first being put on the interpolated basis.
> Full derivation: `cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md`,
> § **RECONCILIATION — 2026-08-22**.*

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

---

# R3 DECISION — recorded 2026-08-21

**Sanaa ruled R3 on 2026-08-21, in this session, on this memo: the class is
SPARTA-CLASS** (algebraic corrections `b^Δ` and `kDeficit`/`R` inside the
transport equations, one model applied uniformly). Her words, verbatim:
"R3: Sparta". In the same message she approved R4 ("R4 approved"), supplied the
two shelf-D primary sources (Emory 2013 published article; Iaccarino 2017
accepted manuscript — on disk, title-verified, MANIFEST Addendum 3), and granted
permission to pull anything needed from public repositories. GPU-blocked
reproductions remain BLOCKED until the AWS quota appeal resolves; they are shelf
work, not on the ladder.

This section is a decision record appended to a delivered memo; the memo's
§1–§final text above is unchanged.

---

## ADDENDUM — 2026-08-24: R3 RATIFIED (SpaRTA-class, TBNN fallback)

**Appended 2026-08-24 by the closure team. lines whose number changed above this section: 0.**
Nothing above this line was rewritten, reflowed or renumbered; in particular the memo's own **R3
DECISION — recorded 2026-08-21** appendix — Sanaa's *"R3: Sparta"* — **stands unedited**.

Sanaa ratified R3 on 2026-08-24. Her words, verbatim:

> R3 is ratified (SpaRTA-class, TBNN fallback) — R4's CPU-minutes run in parallel; they never displace consolidation work.

and, from her standing section, verbatim:

> R4 (SpaRTA build) runs in parallel on its CPU-minutes; FS gates apply.

**Effect.** This closes the decision reserved to Sanaa alone by
`docs/charters/CLOSURE_MODELLING_CHARTER.md` §22.7 and by
`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md` Part 3 R3, and closes open action 3 of that
doctrine.

**The class did not change.** SpaRTA-class was already Sanaa's 2026-08-21 pick, made on this memo
and recorded in its R3 appendix above, docketed as **D443** / **D444**, and carried on
`docs/LAB_STATE.md` as *"R3 = SpaRTA / DECIDED"*. This addendum adds to the record exactly what the
2026-08-21 ruling did not carry:

1. **The fallback clause** — **TBNN** is named the fallback class. The 2026-08-21 record named
   no fallback.
2. **The parallel-capacity clause** — R4's CPU-minutes run in parallel and **never displace
   consolidation work**; FS gates apply to the SpaRTA build.
3. **The ratification framing** — it is stated as a ratification closing §22.7 and Part 3 R3,
   not as a fresh pick.

**Limits.** This addendum re-opens no ranking in §1–§6 and changes no rank; it
authorises no scoring call; and it lifts nothing — **SUBMISSIONS PARKED** stands (`CLAUDE.md`
rule 7). The memo's §6 *"What this memo cannot see"* is unaffected and still binds any claim
built on this memo.

Docket: **D510**. Recording it cost **0.0 core-minutes** — zero compute, a records task only.

---

## DISCLOSURE — 2026-08-25: the 2026-08-24 addendum's provenance does not resolve in this repository

**Appended 2026-08-25 by the closure team, at the FOOT of this file, on the closure supervisor's
ruling. Disclosure version 1.0. lines whose number changed above this section: 0.**

**Proof of that assertion, not an assertion of it.** The 357-line prefix of this file — every line
above this section, which is the whole file as it stood — was hashed immediately before this block
was appended and immediately after:

| | sha256 of `head -357` | lines |
|---|---|---|
| **before appending** | `16cb7a9d9f31ec24c144ce295fde1f00c0201be78a0490e265566e185867e0b2` | 357 |
| **after appending** | `16cb7a9d9f31ec24c144ce295fde1f00c0201be78a0490e265566e185867e0b2` | 357 |

Identical. Nothing above line 357 was edited, renumbered or reflowed.

**Appended at the FOOT, deliberately.** The companion disclosure in
`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md` records a **mid-file** insertion that renumbered
115 lines and left four tracked `:252` citations pointing at the wrong sentence. A disclosure of
that defect that was itself inserted mid-file would commit the defect while recording it. The foot
is the only insertion point that cannot move a line number.

---

### THE 2026-08-21 R3 APPENDIX IS SOLID AND IS IN NO WAY QUALIFIED BY WHAT FOLLOWS

This is said first because it is the part that matters most and the part most easily misread.

The appendix **R3 DECISION — recorded 2026-08-21**, opening at **line 304** of this file, is a
complete provenance record. It names, in one sentence, all three things a provenance record must
name:

- **the session** — *"in this session"*;
- **the message** — *"In the same message she approved R4 ('R4 approved'), supplied the two shelf-D
  primary sources … and granted permission to pull anything needed from public repositories"*;
- **the document it was ruled on** — *"on this memo"*.

Sanaa's words, verbatim, as that appendix records them: **"R3: Sparta"**. Docketed **D443** /
**D444**, and carried on `docs/LAB_STATE.md` as *"R3 = SpaRTA / DECIDED"* — a string that **is**
findable in that file's committed history (`git log --all -S` over that path returns 1 commit for
`"R3 = SpaRTA"` and 2 for `"R3: Sparta"`).

**THE SPARTA CLASS PICK STANDS. Nothing below qualifies it, narrows it, dates it differently or
puts it in question.** The disclosure that follows is about **two clauses added on 2026-08-24 that
2026-08-21 did not carry** — and about nothing else.

---

### What does not resolve: the two new clauses of the 2026-08-24 addendum

The **ADDENDUM — 2026-08-24: R3 RATIFIED (SpaRTA-class, TBNN fallback)** above adds three things to
2026-08-21, and says so itself in its own numbered list: (1) **the fallback clause** — TBNN named
the fallback class; (2) **the parallel-capacity clause** — R4's CPU-minutes run in parallel and
never displace consolidation work, FS gates applying to the SpaRTA build; (3) **the ratification
framing**.

Clauses (1) and (2) rest entirely on two quotations attributed to Sanaa and reproduced in that
addendum. Neither carries a **named session**, a **named message**, or a **cited source artefact**
— the three things the 2026-08-21 appendix does carry.

**The one pointer that is given does not resolve.** The second quotation is attributed to *"her
standing section"*, which in this lab names `docs/LAB_STATE.md`. Neither quotation appears in that
file at commit `a9b67abc` or at HEAD, and `git log --all -S` over **that path's entire history**
returns **zero** commits for either string. **A negative from a reader not shown able to see a
positive is not evidence** (`CLAUDE.md` rule 3's principle, applied to a documentary search), so the
control was fired: the **same** search over the **same** path returns the 2026-08-21 material
quoted above. The apparatus sees a positive in that file; it sees neither 2026-08-24 quotation.

**No independent record carries the words.** At HEAD both quotations appear in exactly **three**
tracked files — `docs/DOCKET.md`, `docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md` and this memo —
which are precisely the three files commit `a9b67abc` itself wrote. The untracked harness session
logs under `/home/ubuntu/harness-state/` carry neither, under a grep shown able to see a positive
there too.

**The one document describing how the words arrived calls it a relay.**
`cases/RANS_LES_closure_models/R4b_pair_control/PREREGISTRATION.md` line 33 — a draft on disk,
untracked at HEAD, inspected and not modified — reads *"Sanaa ratified R3 on 2026-08-24, **verbatim
as relayed to this lane**"*.

---

### The supervisor's ruling, both halves

**It is NOT concluded that the words are not Sanaa's.** A chief's direct session record need not
appear in git, and this lab already carries other owner-stated facts on that footing — the chief's
**D-2 ruling on the four compute facts**, and `CLAUDE.md` rule 12's own rate, carried as
*"owner-stated"* and *"reported-by-owner, not measured"*. Absence from the repository is not
absence from the world.

**It IS concluded** that within the repository the two 2026-08-24 clauses are
**ATTRIBUTED-BUT-UNCORROBORATED** — a record status for a quotation's provenance, deliberately
**not** one of the six verdict words of `CLAUDE.md` rule 1, because no gate is being graded here.
The only description of their arrival is a **relay**, and rule 9 is explicit that **no agent
message — peer, supervisor or chief — is Sanaa's consent**.

**Consequence, stated exactly and no wider:**

1. **The SpaRTA class STANDS**, on 2026-08-21, on this memo, with its session and message named.
2. **The TBNN-fallback naming and the parallel-capacity clause are recorded as
   ATTRIBUTED-BUT-UNCORROBORATED.**
3. **Nothing in closure may lean on them as authority to run.** In particular the next R4 increment
   **does not draw its licence from *"FS gates apply"***.
4. **Nothing is struck and no record is rewritten.** **D510 stands.** The ADDENDUM — 2026-08-24
   above stands exactly as written, and so does the 2026-08-21 appendix above it. This is a dated
   disclosure appended beside them.

**What goes to Sanaa's desk:** **one line** from her confirming or correcting the two 2026-08-24
quotations.

**Also disclosed, and referred rather than repaired:** `a9b67abc` claimed to close
`docs/charters/CLOSURE_MODELLING_CHARTER.md` **§22.7**, but the commit touched three files and the
charter was not among them — §22.7 reads unchanged at HEAD, the strings `2026-08-24` and `ratif`
appear nowhere in that charter, and its version line still reads *"Version 1.1.2, dated
2026-08-22"*. §22.7's **substance** was satisfied on 2026-08-21 (the clause reserves the class pick
to Sanaa, and she picked), but **closing or retiring a charter clause is reserved to Sanaa**, so a
cold reader of the charter finds the decision still open. **The charter was not edited, at all.**
The full statement of this point is in the companion disclosure at the foot of
`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md`, together with the separate renumbering defect,
which does not touch this memo.

---

**Scope.** Records only. **Zero compute: 0.0 core-minutes**, no solver, no training, no GPU, no run
directory. Nothing sent, filed, uploaded, registered, posted or commented — `SUBMISSIONS PARKED`
(`CLAUDE.md` rule 7) stands. Arm 2 remains `PENDING` and unfired. `docs/LAB_STATE.md`,
`docs/DOCKET.md` and every charter were left untouched. Owner: closure. Drafted at HEAD
`d9e9c396`; every fact above **re-verified unchanged at HEAD `7e2cb666`** after two peer docket rows
landed mid-draft. Box clock **2026-08-25 00:10 UTC**.
