# B-52 turn closure — five draws at rung 6, three at rung 7: pre-registration

**Written 2026-08-10, before any new mesh exists.** Chief-approved: *"The ≈31
core-min closure arm (2 more draws at rung 6, 1 at rung 7) is APPROVED. Five
draws is what separates 0.91–2.38× into signal or noise... Pre-register the
discriminating bracket BEFORE meshing: what σ-multiple counts as signal, what as
noise, and what the honest verdict is if five draws still cannot separate them —
that third branch is the likeliest and the one most open to motivated reading."*

Parent measurement: `B52_RUNG6_REPLICATE_RESULTS.md` (`e40eceb3`, prereg
`5c6825c7`). Audit: `B52_TURN_CLAIM_AUDIT_2026-08-10.md`. Model rule per
SUPERVISION_CHARTER §5: session default. Stated, not silent.

---

## 1. READ THIS FIRST — the approved arm almost certainly cannot deliver the verdict it was approved for

The chief called the third branch *"the likeliest"*. **The arithmetic, done
before meshing, says it is closer to certain, and it misses a verdict by
0.011.** This is stated here, before any compute, rather than discovered in the
results.

The deciding statistic (§3) is `T = |turn| / √(s₆² + s₇²)`. Both `s` are sample
standard deviations from small n, so **T itself carries sampling error**, and a
verdict read off the point estimate would be exactly the motivated reading the
chief warned about. The honest rule puts the confidence interval on T (§4).

At the approved sample sizes — **n₆ = 5, n₇ = 3**, Welch df ν = 5.33 — the 90%
CI on T spans **[0.494 × T̂, 1.474 × T̂]**. So:

| to declare | requires | plausible? |
| --- | --- | --- |
| **SIGNAL** (CI lower ≥ 3) | T̂ ≥ **6.07** | **No.** The current estimate is 0.91–2.38 |
| **NOISE** (CI upper ≤ 1) | T̂ ≤ **0.68** | Possible, at the very bottom of the current range |
| **MARGINAL** (CI wholly inside (1, 3)) | **2.02 ≤ T̂ ≤ 2.04** | A window **0.02 wide**. Effectively no |

**If the truth is near the middle of the current bracket (T ≈ 2.0), the approved
arm returns CI = [0.989, 2.947] — indeterminate by 0.011 on the lower bound.**

**One more draw at each rung fixes it.** At n₆ = 6, n₇ = 4 the CI at T̂ = 2.0
becomes [1.142, 2.809] — wholly inside (1, 3), a **MARGINAL verdict**:

| n₆ | n₇ | ν | CI at T̂ = 2.0 | outcome | new draws | **core-min** |
| --- | --- | --- | --- | --- | --- | --- |
| **5** | **3** | 5.33 | [0.989, 2.947] | indeterminate | 2 + 1 | **27.4 (approved)** |
| **6** | **4** | 7.50 | **[1.142, 2.809]** | **MARGINAL — a verdict** | 3 + 2 | **≈47.6** |
| 8 | 6 | 11.67 | [1.310, 2.656] | verdict, tighter | 5 + 4 | ≈93.5 |

> **EXPLICIT ASK, not taken: +1 draw at each rung, ≈20.2 core-min beyond the
> approved scope, converts an almost-certain non-verdict into a verdict.**
> **I have not spent it and will not without approval.** The approved arm runs
> exactly as approved. This is filed here so the chief can rule on the extension
> while reading the pre-registration rather than after a wasted round trip.

**The approved arm is still worth its 27.4 core-min even if it lands
indeterminate**, and this is not a consolation: it replaces a σ *bracket spanning
a factor of 2.6* — assembled from three mismatched estimators at n = 2, 2 and 3 —
with a **direct sample standard deviation at n = 5, and rung 7's σ measured for
the first time at n = 3**. The 22 amendments the audit recommends would then carry
a measured number with a stated CI instead of "0.91–2.38×". That is the arm's
guaranteed deliverable; the verdict is its stretch goal.

## 2. The draws

**Rung 6** (330 950 cells; existing draws: finer2 (51 45 75), 6b (52 44 76),
6c (52 45 74)) — two new, to reach n = 5:

| draw | divisions | fallbacks if G1 refuses |
| --- | --- | --- |
| **6d** | **(50 45 77)** | (53 45 73), (49 45 78) |
| **6e** | **(53 45 73)** | (49 45 78), (54 45 72) |

**Rung 7** (441 057 cells; existing: rung7 (55 49 82), rung7b (56 48 83)) — one
new, to reach n = 3:

| draw | divisions | fallbacks |
| --- | --- | --- |
| **7c** | **(54 49 84)** | (57 48 82), (55 48 84) |

**Scope statement, declared because it bounds what σ means here.** All candidates
hold `ny` at the value that keeps the delivered cell count inside G1's ±2.0% band
— because `B52_RECIPE_NOTE_BACKGROUND_PRODUCT.md` measured that `ny` steps the
delivered count by ~6.5% while the product moves 0.22%. **The σ this arm measures
is therefore draw scatter AT FIXED DELIVERED RESOLUTION, conditional on the G1
gate.** That is the right quantity — a draw delivering 6.5% more cells is a
different resolution, not a different draw of the same one — but it is a
*conditional* σ and it is not claimed to be the scatter of the unrestricted draw
space. A future arm wanting the latter must drop G1 and compare like with like.

**Gates carried forward unchanged** from `B52_RUNG6_REPLICATE_PREREGISTRATION.md`
§6: **G1** delivered cells within ±2.0% of the rung's reference count (330 950 /
441 057), re-draw allowed with every refused attempt recorded, at most two
re-draws; **G2** mesh birth certificate written at creation and `certificate_admits`
before launch; **G3** final-60 2σ below 5% of |Cd|; **G4** lever echo, with
equality checked over the lever dictionaries and pre-solve `0.orig` only — the
amended form, after the original wording failed on `potentialFoam` outputs.
**2 MPI ranks, hierarchical `n (2 1 1)`, 300 iterations** on every draw: rank
count is fixed across this family and varying it would inject a decomposition
artifact into the very quantity being measured.

## 3. The statistic

- `s₆` = sample standard deviation of Cd over the **five** rung-6 draws (n−1
  denominator). `s₇` = the same over the **three** rung-7 draws.
- The turn differences two rungs, each represented by **one** draw, so its
  standard deviation is **√(s₆² + s₇²)** — not `√2 σ`, which assumed the two rungs
  share one σ. This arm measures them separately and stops assuming.
- **`T̂ = |−4.055 × 10⁻³| / √(s₆² + s₇²)`.**
- Degrees of freedom by Welch–Satterthwaite:
  `ν = (s₆² + s₇²)² / (s₆⁴/4 + s₇⁴/2)`, computed from the measured `s`, not
  assumed equal.
- 90% CI on T: `[T̂·√(ν/χ²₀.₀₅,ᵥ)⁻¹ … ]` — concretely,
  `T_lo = T̂ / √(ν/χ²₀.₀₅,ᵥ)`, `T_hi = T̂ / √(ν/χ²₀.₉₅,ᵥ)`.

## 4. The discriminating bracket — fixed now

> | branch | criterion | meaning |
> | --- | --- | --- |
> | **SIGNAL** | **T_lo ≥ 3.0** | the turn is real structure. The withdrawn shape claims are **reinstated, with a band** |
> | **NOISE** | **T_hi ≤ 1.0** | the turn is indistinguishable from a draw-to-draw difference. The Tier-1 withdrawals become **permanent** |
> | **MARGINAL** | **1.0 < T_lo and T_hi < 3.0** | **a verdict, not a shrug:** the turn is *genuinely* between noise and signal, established as such. No amount of further drawing makes it a signal, so the shape claims stay withdrawn/amended **permanently** and the matter closes |
> | **INDETERMINATE** | CI straddles 1.0 or 3.0 | **precision failure, not a physical finding.** No branch claimed. The record states T̂, the CI, and what n would decide it |

**The verdict is read off the interval, never the point estimate.** Pre-refused,
by name, because each is available and each is wrong:

1. **Reading T̂ against 3.0 or 1.0 and ignoring the CI.** This is the whole trap.
2. **Widening SIGNAL to 2σ** because T̂ landed near 2. The 3σ threshold is the one
   the audit already graded 22 claims against; moving it after seeing the data
   re-grades them by fiat.
3. **Pooling rung 6 and rung 7 into one σ** to buy degrees of freedom. §3 measures
   them separately on purpose; pooling is only valid if they agree, and whether
   they agree is one of the things being measured.
4. **Dropping an outlier draw.** No draw is excluded for its Cd. G1 excludes on
   *delivered cell count*, decided before any solve, and that is the only
   exclusion in this arm.
5. **Calling INDETERMINATE a result about the flow.** It is a statement about the
   sample size, and §1 says in advance that it is the expected one.

## 5. Predictions, on the record before meshing

- **P1: the branch will be INDETERMINATE.** Stated as the expected outcome from
  §1's arithmetic, not as a hedge. Scored either way.
- **P2: `s₆` at n = 5 will land between 1.2 × 10⁻³ and 3.2 × 10⁻³**, the bracket
  the three existing draws imply. If it lands outside, the n = 3 estimate was
  worse than its own arithmetic suggested and that is the finding.
- **P3: `s₇` ≠ `s₆` by more than a factor of 2** — i.e. the two rungs do *not*
  share one σ. The 0012's scatter fell with refinement and the 4412's did not
  (`W3_MESH_NOISE_FLOOR_RESULTS.md` §3), so a rung-dependent σ is the prior. If
  P3 is false, the √2σ shorthand this lab has been using is vindicated.

## 6. Cost, from measured bases

**Priced from this lab's own measurements of these exact rungs, no scaling
factor.** The predictor is the basis.

| item | basis | core-min |
| --- | --- | --- |
| 6d, 6e — mesh + potentialFoam/decomposePar + 300-it solve at 2 ranks | measured clean-pass of 6b/6c: **17.2 core-min for two draws** (`B52_RUNG6_REPLICATE_RESULTS.md` §6) | **17.2** |
| 7c — same, at rung 7 | measured rung 7: mesh 1.28 + serial steps 0.15 + simpleFoam 8.73 = **10.16** (`B52_RUNG7_RESULTS.md` §5) | **10.2** |
| | **total** | **27.4** |

**27.4 against the chief's ≈31 — under, and the difference is real rather than
optimistic:** the review's 31 used my audit's 10.7/draw figure, which was the
*pre-registered* per-draw price; the *measured* clean-pass price came in 20%
below it. Re-draws under G1 are extra and are reported as measured; one draw in
two missed the band last time, so a refused attempt is likely and is budgeted as
≈1.1 core-min each rather than being discovered.

## 7. What will NOT be claimed

- **No ladder verdict, band, or order changes on this arm** regardless of branch.
  The B-52 family stays `conclusive: false` with no reportable band. This arm
  measures the uncertainty *on* a difference; it does not fit anything.
- **A NOISE branch does not make the B-52's Cd values wrong**, only the *shape*
  read from their differences.
- **A SIGNAL branch does not reinstate the mechanism**, only the increment. *"The
  increments grow because the discretization does"* would still need its own
  evidence.
- **σ measured here is conditional on G1** (§2) and is not the unrestricted
  draw-space scatter.
- Nothing is withdrawn, amended or reinstated by this arm directly; the audit's
  22 amendments and 4 withdrawals remain the chief's to rule on.

*Nothing below this line existed when this document was committed.*
