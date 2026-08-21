# A5 U-bend — re-verification at np=1, shipped vs patched IDWarp: RESULTS

**Run 2026-08-21, Lane A.** Pre-registration: `PREREGISTRATION.md` in this directory, committed
**before** any arm launched; it is not revised by this file. Nothing filed upstream.

**Headline: the shipped FAIL and both sign flips reproduce at np=1; the patched arm passes the
aggregate band; the FD-invariance control is bit-exact on all 27 components — and two registered
predictions MISSED, one of which turned out to be the most useful result of the run.**

Raw logs: `/home/ubuntu/certonomous-runs/P1-a5-np1/{stock,patched}.log`. Ledger: `.../ledger.txt`.
Staged copies of `W5-regrade/a5pl_stock` were used; the published directory was not run in.

---

## 1. Arms as executed

| arm | image | `IDWARP_SO_MD5` printed by the run | np | `nProcs : 1` lines in log | rc | wall | core-min |
|---|---|---|---|---|---|---|---|
| 1 SHIPPED | `dafoam/opt-packages:latest` | `f0fcb488e0e98156575cd19548e91663` (**stock**) | 1 | 4 | 0 | 374 s | 6.233 |
| 2 PATCHED | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` (**patched**) | 1 | 4 | 0 | 372 s | 6.200 |

Departure 3(1) checked as registered: the log reports `nProcs : 1` and no 4-way decomposition, so
DAFoam did rewrite `decomposeParDict` (which on disk still says `numberOfSubdomains 4; method
scotch;`) to match the actual rank count. **The arm is genuinely undecomposed.** 55 primal solves
per arm (1 baseline + 27 × 2 central-difference legs), as designed.

## 2. Verdict rows — SHIPPED and PATCHED separate

Band (`../../A_stepsize_study.md:91-93`): PASS ≤5% aggregate with zero flagged components;
CONDITIONAL 5-15%; >15% or any flagged component → FAIL.

| row | arm | image | predicted | measured | verdict |
|---|---|---|---|---|---|
| `OBJ.val` wrt `shapexUpper` (27) | **SHIPPED** | `dafoam/opt-packages:latest` | 46.6% ± 2 pt, 2 flips at idx8/idx17 | **46.840%** (`4.684019e-01`); AN `1.938870e+01`, FD `3.358985e+01`; **2 flips, idx8 205.52% and idx17 121.86%** | **GATE FAIL** |
| `OBJ.val` wrt `shapexUpper` (27) | **PATCHED** | `dafoam-idwarp-rot:v1` | 2.24% ± 0.3 pt, 0 flips, 26/27 in band, idx16 ≈17.3% | **2.768%** (`2.768361e-02`); AN `3.351123e+01`, FD `3.358985e+01`; **0 flips**; **22/27 within ±12%**; **idx16 = 0.90%** | **PASS on the aggregate band**, with the per-component caveat in §5 |

**Prediction scorecard, stated plainly rather than rounded into agreement:**

| registered prediction | outcome |
|---|---|
| SHIPPED aggregate 46.6% ± 2 pt | **HELD** — 46.840%, inside 44.6–48.6 |
| SHIPPED: two flips at idx8 and idx17 | **HELD** — exactly those two, 205.52% and 121.86% (published 207.6% / 121.6%) |
| SHIPPED: 5 of 27 within ±12% | **MISSED** — 4 of 27. See §5 |
| PATCHED: zero sign flips | **HELD** |
| PATCHED: aggregate 2.24% ± 0.3 pt | **MISSED** — 2.768%, outside the registered band by 0.23 pt |
| PATCHED: 26/27 in band | **MISSED** — 22/27 |
| PATCHED: idx16 the single out-of-band component at ≈17.3% | **MISSED, decisively — and this is the run's most valuable result.** idx16 reads **0.90%**. See §4 |
| FD column bit-identical between arms | **HELD** — 27 of 27 |

## 3. The control: the FD did not move, on any component

Registered falsifier: *"If any FD entry moves, stop and report."* It did not fire.

```
max |FD_stock − FD_patched| = 0.0        27/27 components bit-identical
analytic changed on 27 of 27 components
```

Both arms report the same `Fd Magnitude` `3.358985e+01`. The patch is derivative-only, the primal
warp is md5-identical, and **`dafoam-idwarp-rot:v1` is confirmed a clean single-variable change on a
second, independent case** (A1 was the first). The image is validated for further use.

## 4. `W4_IDX16`'s anomaly is decomposition-specific, and it vanishes at np=1

This was not the question the arm was run to answer, and it is the strongest thing in this file.

`../../W4_IDX16_IS_THE_REFERENCE.md` established that `check_totals`' own reported FD at idx16,
**`−4.30296296`**, is not reproducible by any independent finite difference of the same function at
the same step in the same container: three re-measurements — cold from `0/`, warm from the converged
baseline, and warm from the state `check_totals`' own component sequence leaves — returned
**−4.98068, −5.05964, −5.04286**. The same harness reproduced the neighbouring idx15 to 8.8e-08
relative, so it was the same instrument. That record closes with the anomaly **open**:

> Why `check_totals` reports −4.30296296 at this one component remains open. It is deterministic
> across both runs and all four ranks, and it is not the decomposition, the step, one-sidedness, a
> kink, or the component sequence.

**At np=1, `check_totals`' own FD at idx16 is `−5.00483123`.**

| reference | value | distance from this run's np=1 FD |
|---|---|---|
| this run, np=1, `check_totals`' own FD | **−5.00483123** | — |
| W4 re-measurement, cold from `0/` | −4.98068 | **0.485%** |
| W4 re-measurement, warm from converged baseline | −5.05964 | **1.083%** |
| W4 re-measurement, sequence-faithful | −5.04286 | **0.754%** |
| published np=4 `check_totals` FD | −4.30296296 | **16.311%** |
| neighbour idx15, np=1 vs published np=4 | −24.27140348 vs −24.27272 | **0.0054%** — the rest of the vector is unaffected |

**The np=1 `check_totals` lands inside the cluster of independent re-measurements and 16.3% away
from the np=4 value, while its immediate neighbour agrees across rank counts to 5 parts in 100,000.**
The anomaly is therefore a property of the **np=4 FD path**, not of the component, the step, the
objective or the harness in general. The last clause of W4's open question — *"it is not the
decomposition"* — was reached by comparing `scotch` against other **np=4** partitions; it did not
test **np=1 versus np=4**, which is what this arm did. **The open item narrows to: something in the
decomposed `check_totals` FD path corrupts this one component's reference.** It is not closed — no
mechanism is offered here — but it is now localised to a much smaller place.

**Consequence for the two registered numbers.** The 2.2372% / 0.1826% distinction the
pre-registration was built around **does not arise at np=1**, because the correction it applies is
already unnecessary:

| aggregate | np=4 (published) | np=1 (this run) |
|---|---|---|
| as `check_totals` reports it | 2.2372% | **2.768%** |
| with idx16's FD replaced by the sequence-faithful −5.04286 | 0.1826% | **2.765%** |

At np=4 the substitution moved the aggregate by a factor of 12; at np=1 it moves it by 0.1%, because
np=1's own FD at idx16 is already essentially the sequence-faithful value. **Registering both
numbers was the right call and the reason is now visible: neither was going to be the answer.**

## 5. Where the two "missed" predictions came from — the analytic held, the FD moved

The aggregate reproduces well (46.84% vs 46.64%; 2.77% vs 2.24%) and both flips reproduce, but the
per-component band membership does not. The cause is visible in the columns:

| idx | analytic, published np=4 | analytic, this run np=1 | FD, published np=4 | FD, this run np=1 |
|---|---|---|---|---|
| 2 | −0.41766 | **−0.4178920** | −0.41319 | **−0.8719458** |
| 3 | +1.96884 | **+1.9703715** | +0.70507 | **+0.2582442** |
| 8 | −0.84337 | **−0.8445469** | +0.78391 | **+0.8004033** |
| 15 | −13.86042 | **−13.8641054** | −24.27272 | **−24.2714035** |
| 17 | −0.62881 | **−0.6302625** | +2.90530 | **+2.8828273** |
| 26 | −1.95654 | **−1.9578629** | −1.90572 | **−1.9043901** |

**A5's analytic gradient is decomposition-invariant to roughly four significant figures on every
component checked. Its FD reference is not.** On the large-magnitude components (idx15, idx9, idx12)
the FD agrees across rank counts to 0.005–0.1%; on several small-magnitude components (idx2, idx3)
it moves by factors of 2–3. That is what pushes idx2 from 1.1% to 52.1% and idx3 from 179.2% to
663.0% in the shipped arm, and what leaves 5 components outside ±12% in the patched arm
(idx0 51.6%, idx2 53.3%, idx3 174.9%, idx5 27.1%, idx21 12.4%) while the aggregate — dominated by
the large components, which agree at 0.04–2% — still passes.

This is consistent with a path-dependent FD: `check_totals` warm-starts each leg from the previous
one, A5 sits on a genuine residual limit cycle, and changing the rank count changes the path every
leg takes. The record already measured that mechanism directly — the reset-vs-warm control found a
**reproducible** 1.05e-05 offset in the objective from warm-start path alone
(`../../A5_ubend_internal.md`, Control 2) — and this run is the same effect appearing across rank
counts instead of across probe protocols. **Offered as the consistent reading, not as a proven
mechanism; no controlled arm was run for it here.**

**Q2 answered, with a caveat that matters.** The pre-registration's second question was whether A5
is decomposition-invariant on the **shipped** stack, a claim `S1 §2.2` flagged as cited from a
patched-stack run. **The answer is: the analytic gradient is, to ~4 significant figures; the
`check_totals` FD reference is not, on small-magnitude components; and the graded aggregate is
(46.84% vs 46.64%).** The flag in `S1 §2.2` was justified — the claim was resting on the wrong
evidence — and the claim itself now has the right evidence and survives, with the FD caveat newly
attached and not previously stated anywhere.

## 6. A free correction to the frozen record's in-band list

`../../A5_ubend_internal.md:194-196` states: *"5 of 27 components (idx 1, 2, 16, 24, 25) fall within
the ≤12% band"*. Read against that record's own per-component table on the same page, **the count is
right and the membership is wrong**: idx16 is listed at **12.3%**, which is outside ≤12%, while
idx26 at **2.7%** is inside and is omitted. The in-band set at np=4 is **{1, 2, 24, 25, 26}**, still
five. No number changes and no verdict moves; recorded because the list gets quoted.

(At np=1 the in-band set is **{1, 24, 25, 26}** = 4, idx2 having left the band for the FD reason in
§5.)

## 7. Cost, against the registered ceiling

Registered ceiling: **45 core-min / $0.04.** Predicted ~23 core-min.

| arm | ranks | wall | core-min | $ @ $0.0513/core-hr |
|---|---|---|---|---|
| 1 SHIPPED | 1 | 374 s | 6.233 | $0.0053 |
| 2 PATCHED | 1 | 372 s | 6.200 | $0.0053 |
| **total** | | **746 s** | **12.433** | **$0.0106** |

**12.43 core-min against a 45 core-min ceiling — 28% of budget, and 46% under the prediction.** The
np=1 wall (≈374 s) came in well below the ≈700 s predicted from scaling the np=4 anchor, so the
registered cost-risk (arm 1 exceeding 1800 s and forcing a re-scope to np=2) did not arise.

**Measurement-condition disclosure:** both arms ran while another lane held a container on this box
(host load 4.7–6.0 during the window). Wall clocks are **contended** and are not a clean cost basis;
the derivative values are unaffected — each arm had its own `--cpus=4` cap, which is exactly the
lane's core cap and was never exceeded.

## 8. A free audit that answers one of the pre-registration's own caveats

`PREREGISTRATION.md` §6.4 listed as unknown: *"A5's `fvSchemes` was never audited for a `cellLimited`
gradient scheme."* Audited from the staged case, zero compute:

```
gradSchemes { default  Gauss linear; }                                  <- UNLIMITED
divSchemes  { div(phi,U)  bounded Gauss linearUpwindV grad(U);          <- no `limited` token
              div(pc)     bounded Gauss upwind;
              div(phi,nuTilda) bounded Gauss upwind; }
```

**A5 carries no `cellLimited` limiter.** The limiter defect (D-B2) therefore cannot be present in
this case, and A5 joins the set of cases whose cleanliness on that axis is now verified from disk
rather than assumed. This directly corroborates the decomposition report's correlate — *"every clean
case lacks the limiter (verified from each `fvSchemes` on disk), both defective cases carry it"* —
with one more independently checked case.

## 9. What this run still cannot see

1. **The residual after the patch is reproduced, not explained.** 2.77% at np=1 against A1's 0.038%
   — the same 60×-ish gap the record calls *"genuinely open and must not be described as
   root-caused"*. The priced attack is **C-2** (`useRotations=False`, ~16 core-min); not run here.
2. **`dF/dW`'s scaling anomaly** (`AN/FD` = 35.28 for TP1, 8.4 for TP2, exactly,
   direction-independent) is untouched; `getdFScaling` remains the named place to look.
3. **Only `shapexUpper` is graded** — the other five FFD groups (162 components total) are computed
   but outside the `check_totals` restriction, exactly as in the published rung.
4. **Regime 2 of the rotation defect** — invisible at the undeformed baseline, unpatched by design.
5. **The idx16 localisation in §4 names no mechanism.** It shows *where* the anomaly lives (the
   np>1 FD path), not *what* it is. Closing it would need an instrumented comparison of the
   decomposed and serial FD legs at that one component.

## 10. Ledger

| item | value |
|---|---|
| solver core-minutes | **12.433** (against a registered ceiling of 45) |
| dollars | **$0.0106** |
| containers started | 2, both `--rm`, both rc=0, both `--cpus=4` = the lane cap |
| processes needing a kill | 0 |
| frozen files edited | 0 |
| published case directories written into | 0 (staged copies used) |
| filed upstream | nothing |
