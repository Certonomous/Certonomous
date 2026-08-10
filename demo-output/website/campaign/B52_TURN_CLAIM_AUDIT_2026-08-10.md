# Audit — every standing claim that rests on the B-52 ladder's turn

**Ordered by the chief, ruling (1) of the entry-4 outcome
(`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`, commit `1a0e9a37`):**
*"an audit is ordered of every standing claim that rests on the B-52 ladder's
turn — each either gains this scatter as a stated uncertainty or is withdrawn."*

**Zero solver cost.** Nothing in this document has been withdrawn, edited or
amended. It is a list with a recommendation per claim; the chief rules.

---

## 0. FIRST — a correction to the number that triggered this audit, and it is mine

The finding that ordered this audit was stated as: *three draws at rung 6 span
5.35 × 10⁻³, which is **1.32×** the −4.055 × 10⁻³ turn, so the turn sits inside
its own draw scatter.* That ratio is arithmetically right and **statistically
mis-stated, by me, in `B52_RUNG6_REPLICATE_RESULTS.md` §3** — and the chief's
outcome block has since quoted it.

**The error is the exact one `W3_MESH_NOISE_FLOOR_RESULTS.md` §3 corrected itself
on:** a range over n = 3 and a single pairwise difference are different
statistics and must not be compared. The turn is a **pairwise difference**
(one draw at rung 6 against one draw at rung 7). The like-for-like comparison is
not `R6` but `D6`:

| comparison | value | statistic |
| --- | --- | --- |
| turn / `R6` (range over 3 draws) | **0.76×** | **mixes statistics — do not use alone** |
| turn / `D6` (pairwise, rung 6) | **2.98×** | like-for-like |
| turn / floor (pairwise, rung 7) | **2.12×** | like-for-like |

**Done properly.** Convert every estimator this lab owns to a common σ
(`E|X₁−X₂| = 1.128 σ`; `E[range of 3] = 1.693 σ`), then note that an *increment*
differences two rungs each represented by one draw, so its own standard
deviation is **√2 σ**, not σ:

| estimator | value | n | implied σ |
| --- | --- | --- | --- |
| rung-7 pair (the published floor) | 1.9146 × 10⁻³ | 2 | 1.70 × 10⁻³ |
| rung-6 pair (`D6`, this arm) | 1.3599 × 10⁻³ | 2 | 1.21 × 10⁻³ |
| rung-6 range over three draws (`R6`) | 5.3546 × 10⁻³ | 3 | 3.16 × 10⁻³ |

σ is bracketed at **1.21 × 10⁻³ to 3.16 × 10⁻³** — a factor of 2.6, which is what
n = 2, 2 and 3 buys. An increment therefore carries **√2 σ = 1.70 × 10⁻³ to
4.47 × 10⁻³**.

> ### The defensible statement
> **The turn (−4.055 × 10⁻³) is between 0.91× and 2.38× its own
> mesh-construction uncertainty.**
>
> It is **not established as signal** — that needs ≥ 3× and it does not reach it
> at either end of the σ bracket. It is **not established as pure noise** either
> — the upper end of the bracket puts it at 2.4×. **Three draws cannot separate
> those two readings**, and no claim in this audit is graded as if they could.

This is a weaker refutation than the 1.32× headline implies and a much firmer one
than the record it replaces. Every recommendation below is graded against
**0.91–2.38×**, not against the 1.32×. The rung 7→8 increment (−2.78 × 10⁻⁴) is
**0.06–0.16×** — that one is unambiguously noise, and every claim resting on
*it* survives.

**Recommendation 0 (self-correcting):** `B52_RUNG6_REPLICATE_RESULTS.md` §3 and
the entry-4 outcome block at `1a0e9a37` both carry the 1.32× framing. I can amend
my own record on the chief's word; **the outcome block is the chief's and I have
not touched it.**

## 1. Grading key

| code | meaning |
| --- | --- |
| **W** | **Withdraw as written** — the claim is not supportable at 0.91–2.38× |
| **A** | **Amend** — claim survives with the measured scatter attached as stated uncertainty |
| **S** | **Survives** — unaffected, or strengthened; no action |
| **N** | No action — passing mention, identity, or a different measurement entirely |

---

## 2. TIER 1 — the core shape claims

| # | site | claim | rec | reasoning |
| --- | --- | --- | --- | --- |
| 1.1 | `b52.json` L212 | *"the turn is signal and not iterative noise ... 113 times the rung's own window 2-sigma"* | **A** | The second clause is **true and independently reconfirmed** by this arm (D6 is 94.6× the rung-6 2σ). The first clause does not follow from it: iterative noise was the wrong noise source, and against the right one the turn is 0.91–2.38×. Amend to state both floors. |
| 1.2 | `b52.json` L156; `NOT_PASSING_REGISTER.md` L516 | *"The increments grow because the discretization does, and the ladder is diverging for a reason more iterations cannot reach."* | **W** (causal clause only) | *"more iterations cannot reach"* survives. *"because the discretization does"* is precisely what is now unsupported — the increments are consistent with mesh-construction scatter at every step. **Flag: both charters cite `NOT_PASSING_REGISTER.md` by LINE NUMBER (516). Any edit silently rots those citations** — see 5.3. |
| 1.3 | `B52_RUNG7_RESULTS.md` L35-36; `b52.json` L212; docket L3177 | *"the ladder does not diverge. It oscillates. Down, up, up, down, with the swings getting wider: 0.001857, 0.002377, 0.002702, 0.004055"* | **W** (the trend), **A** (the sequence) | The four increments each carry √2σ = 1.70–4.47 × 10⁻³. **No difference between any two of them is resolved** — 1.857 vs 2.377 vs 2.702 vs 4.055 all sit inside one uncertainty of each other. *"the swings get wider"* is an ordering claim on unresolved numbers and cannot stand. The sign pattern may be reported with the scatter attached. |
| 1.4 | `W3_MESH_NOISE_FLOOR_RESULTS.md` L155-157; docket L4660; `b52.json` L238-240 (`scatter_over_increment: 0.47`) | *"the turn is −4.055 × 10⁻³ ± 47% from mesh construction alone"* | **A** (supersede the number) | ±47% came from one pair at one rung. With rung 6 measured too the honest band is **±42% to ±110%**. The stored `scatter_over_increment: 0.47` should become a range with its n stated. Not a withdrawal: the *form* of the statement was right and it was the first to attach any band at all. |
| 1.5 | `B52_RUNG7_RESULTS.md` L141-153 | *"Two of this lab's two genuine single-knob ladders now both turn. That is the finding worth taking further, and it is a finding about steady RANS on refined snapped-hex meshes, not about either body."* | **W** | A cross-family generalization from n = 2 families, one of which is now unresolved. **Consequence: the Ahmed 25° (R4) half needs the same treatment** — R4's `c4b` is a single replicate pair, so its turn has exactly the evidentiary standing the B-52's had this morning. Recommend the generalization be withdrawn and re-asked as an open question. |
| 1.6 | `W3_WING_VALID_FAMILY_RESULTS.md` L177-195 | corpus table row *"B-52 ... turns twice"*; *"**Four for four.**"* | **A** | The row must carry the scatter. Note in the lab's favour: **L189-195 of that same record predicted this outcome** — *"the B-52's turn at 441 057 cells and the Ahmed 25°'s at 454 691 sit in the same band ... It should be [checked], before the B-52's oscillation is treated as physics."* That prediction has now returned and should be **scored**, not quietly absorbed. |
| 1.7 | `NOT_PASSING_REGISTER.md` L515 | *"oscillation suggests possible interaction between nearBody shell level 2 refinement and background blockMesh boundary-layer growth"* | **A** | Partly vindicated, in the wrong place. `B52_RECIPE_NOTE_BACKGROUND_PRODUCT.md` measures a real stepwise interaction between the background lattice and the refinement shell — **in the delivered cell count**. As an explanation of the *Cd* shape it is unsupported. Recommend re-homing rather than deleting. |
| 1.8 | `NOT_PASSING_REGISTER.md` §B-52 L511-542 | *"six mesh rungs spanning 40.7k to 331k cells"* | **A** — **stale independently of this audit** | Omits rungs 7 and 8 entirely. Needs a refresh whatever the chief rules on the rest. |

## 3. TIER 2 — fits and bands derived from the shape

| # | site | claim | rec | reasoning |
| --- | --- | --- | --- | --- |
| 2.1 | `b52.json` L76-97 `numerical` | `band_abs 4.931e-4`, `band_rel 0.01029`, `richardson_extrapolated 0.0479418`, `observed_order 28.675`, `monotone true` | **A — highest priority in this audit** | `conclusive: false` and `reportable_band: None` are doing their job and no band is published. But **`band_rel = 0.01029` (±1.03%) is a quotable number sitting in a machine-readable record, and the measured single-rung draw scatter is 5.35 × 10⁻³ = ±11.2% of the same value — the stored band is 10.9× SMALLER than the mesh-construction scatter.** Recommend the draw scatter be attached to the record itself so no consumer can read `band_rel` as an uncertainty. |
| 2.2 | `b52.json` L215-223 `which_numbers_moved`; L242-246 `refit_on_replicate` (`band_abs 0.0033775`, held by `monotone`) | every flip (`order 2.253→None`, `monotone true→false`, `richardson 0.0648→None`) | **A** | The flips are correct *as recomputations* — the fit really does do this on this input. What is unsupported is that they were **caused by a physical turn**. Amend to say the flips are driven by an increment inside the draw scatter. |
| 2.3 | `b52.json` L295, L300-306; `B52_RUNG8_RESULTS.md` L42-45 | *"the non-monotonicity keeps its measured explanation, the 1.91e-3 mesh-construction noise floor"* | **S**, amend the number | **This claim is strengthened, not weakened** — it already named mesh construction as the mechanism, and the mechanism is now confirmed on a second rung by the protocol built for it. Only the magnitude updates (σ bracket, not a single 1.91 × 10⁻³). |
| 2.4 | `B52_RUNG8_RESULTS.md` L60-62, L103-105 | rung 7→8 increment *"15% of the mesh-construction noise floor"*; *"a ninth rung would buy another noise sample, not an order"* | **S** | At 0.06–0.16× of √2σ this is unambiguously noise on any estimator. The conclusion is untouched and the arm reinforces it. |
| 2.5 | `W3_GUARD_SWEEP.md` L32, L74-76; `W3_GUARD_SWEEP.json` L91-117 | b52 row: `p 2.253`, `richardson 0.064842`, guards failed | **S** | A record of **what the guards did on a given triple**, not a physics claim. It stays true regardless of why the triple looks like that. |
| 2.6 | `docs/NUMBERS-AUDIT.md` L155-157 | B-52 band provenance pointer to `b52.json` | **A** | Points a reader at the band flagged in 2.1. Should carry the same caveat. |

## 4. TIER 3 — SDK code and calibrated thresholds (handle with care)

**I recommend NO code-logic or threshold change anywhere in this tier.** The
guards reject this ladder; they should still reject it, and more firmly than
before. What is wrong is the *stated reason* in the comments — and a threshold
calibrated on a fixture whose mechanism was misdescribed is fragile even when the
number is right.

| # | site | claim | rec | reasoning |
| --- | --- | --- | --- | --- |
| 3.1 | `sdk/chief_engineer/uq.py` L252-255, L443-448 | rationale for `increment_trend` / `extrapolation_sanity`: *"its Cd increments GROW with refinement"* | **A — comments only** | The guard behaviour is correct and must not change. The justifying sentence describes a **noise realization** as if it were a divergence. Amend the docstring; leave every number alone. |
| 3.2 | `sdk/chief_engineer/uq.py` L335-354, L362-366 | the B-52 as one of **only two fixtures** calibrating the `extrapolation_sanity` tolerance 0.15 (*"clears the good case by 1.30× ... a factor of 16 below the bad case"*) | **A + ESCALATE** | **The most consequential item in the audit, and not mine to close.** The two anchors are the TMR flat plate at 11.58% (the good case, which must be accepted) and **the B-52 at 246.6% — the bad case, the upper anchor**. A Richardson extrapolate computed on a noise-dominated triple is not a stable quantity: **a different draw triple would put that 246.6% somewhere else entirely**, so the 16× gap is not a measurement of how far a bad ladder sits from a good one. The tolerance is probably still right — the B-52 *should* be rejected, and now for a firmer reason — but the **margin** is no longer evidence. **The code already anticipated this in its own words** (*"If a future ladder lands between 11.6% and 15% this number needs re-deriving from more than two fixtures, not nudging"*); this arm converts that hypothetical into a measured defect in one of the two fixtures. **Recommend routing to the UQ/Infra family** alongside the lever-echo referral. **Do not change 0.15 on the strength of this arm** — that would be tuning the gate to the answer, which the same comment forbids. |
| 3.3 | `sdk/tests/test_uq.py` L48, L56-57, L85-115, L291, L303-350, L374 | `B52_CELLS` / `B52_CD` regression fixtures; `test_b52_increments_grow_and_are_rejected` | **S — DO NOT TOUCH THE DATA**, amend comments | These assert what the **fit code** does on a **frozen input array**. They are regression coverage for the guards, not physics claims, and editing the arrays would silently delete that coverage. The surrounding prose calling it *"a diverging ladder"* should be amended. Explicitly recommending **against** any change to the assertions. |
| 3.4 | `sdk/scripts/run_uq_studies.py` L515-524 | rung-placement reasoning: *"the non-monotone signature is a dip at the medium rung"* | **A — comment only** | The placement used coarse/medium, which `recipe_audit` later excluded from the family anyway, and the "dip" is a noise realization. The rung is long since run; no code change is needed. |
| 3.5 | `scripts/self_audit.py` L990 | audit rule anchored on `b52_fourth_rung()` | **N** | Structural pointer, not a shape claim. |
| 3.6 | `B52_RUNG6_REPLICATE_runs/run_rung6_replicates.py` L444-445; `record.json` | hardcoded `4.055e-3`, `2.78e-4` | **N** | These are ratios computed *against* a named reference, and the results record states the reference. No claim is embedded. |

## 5. TIER 4 — charters (where the lesson actually improves)

| # | site | claim | rec | reasoning |
| --- | --- | --- | --- | --- |
| 5.1 | `VERIFICATION_CHARTER.md` L210-220 | *"a credible order on a diverging ladder ... increments grow ... Richardson lands 24 percent above the highest rung"* | **A — and it gets better** | The example still teaches the right reflex (a credible-looking `p` on a ladder you must reject). The **reason** changes from *"it diverges"* to *"its increments are inside a mesh-construction scatter nobody had measured"* — which is a **stronger** charter lesson, because it generalizes to every ladder rather than to diverging ones. |
| 5.2 | `REPORTING_CHARTER.md` L303-312 | same example, same numbers | **A** | Same treatment. |
| 5.3 | both charters | cite `NOT_PASSING_REGISTER.md` **line 516** by number | **A — mechanical hazard** | Recommendation 1.2 edits that line. **A by-line-number citation across files rots silently on any edit.** Recommend the amendment and the citation updates land in the same commit, or that the citations be changed to quote-anchored. |
| 5.4 | `VERIFICATION_CHARTER.md` L243, L282 | *"A recipe audit precedes an order"*; *"the B-52 still fails it by a factor of 16"* | **S** / **A** | The recipe-audit precedent is untouched and good. The *factor of 16* is the calibration margin flagged in 3.2 and inherits its caveat. |
| 5.5 | — | **new rule, recommended** | **propose** | `W3_MESH_NOISE_FLOOR_RESULTS.md` §5 asked for a per-rung replicate-scatter refusal and it was never adopted. This is now the **second family** to demand it and the first where the scatter exceeds the family's largest increment. Recommend it be raised as a charter rule: **no order is fitted, and no band published, on a ladder with no measured draw scatter at its rungs.** |

## 6. TIER 5 — cross-case, docket, product surfaces

| # | site | claim | rec | reasoning |
| --- | --- | --- | --- | --- |
| 6.1 | `R4_PREREGISTRATION.md` L75-80 | *"Even the B-52's 4.65× amplification acts on a signal **253× above the floor**"* | **W as written** | That floor is the **iterative** 2σ (1.07 × 10⁻⁵). Against the mesh-draw floor the B-52's finest increment (2.702 × 10⁻³) is **0.60–1.59×** — at or below it, not 253× above. The sentence inverts its own conclusion once the right noise source is used. |
| 6.2 | `R4_ASYMPTOTIC_RESULTS.md` L139-144 | *"The B-52 was not re-run, and the reason is in the pre-registration"* | **A** | The reason is 6.1, which does not survive as written. Recommend the **decision be revisited** — not necessarily reversed; a re-run may still be the wrong spend, but it can no longer rest on "253× above the floor". |
| 6.3 | `F11_lid_driven_cavity_ladder.md` L154, L224 | B-52 shape used as a contrast baseline (*"refinement swung results by tens of percent and sometimes flipped sign"*) | **A** | *Refinement* did not swing it; *mesh construction* did. The contrast survives with the mechanism corrected — and is arguably sharper. |
| 6.4 | `4G_tmr_mesh_aspect_ratio.md` L626, L678 | *"the B-52 extrapolation guard doing its job"* | **S** | Methodological precedent about guard behaviour, not about B-52 physics. |
| 6.5 | `CALIBRATION_SCORECARD_2026-08.md` L66 | G4 *"SCORED FALSE ... increment sign-flipped (−0.004055)"* | **S** | Records that a prediction scored FALSE. Cd did fall; the scoring is unaffected, and the scorecard does not interpret why. |
| 6.6 | `docket.json` L2671, L3164, L3177, L3194, L3245, L3504, L3520, L4660, L4974, L5335-5336 | assorted shape assertions (*"a divergence wearing a credible number"*, *"oscillates with widening swings"*, *"the turn is signal"*, *"±0.0063 on a Cd of 0.0472, which is 13 percent"*) | **A** | Same treatment as their source records. L3099 already carries the correction. **Flag: L3194 and L3520 are duplicated text** — both need any amendment, or the duplicate needs removing. |
| 6.7 | `proposals/b52-eighth-rung-with-the-alternative-preregistered.json`; `proposals/b52-replicate-meshes-at-rung-6.json`; `scripts/add_proposals_r4.py` L253-280; `scripts/add_proposals_supervisor_review_2026_08_07.py` L398-455 | shape text, and the **generator scripts that emit it** | **A** | Amending the docket without amending its generators means the next regeneration reintroduces the withdrawn text. Recommend generator and output move together. |
| 6.8 | `docs/PRODUCT_LIST.md` L144-149 | *"B52: why the mesh doesn't converge smoothly — ANSWERED ... the ladder is NOISE"* | **S** | **Already correct**, and this audit strengthens it. The open *"B52 floor decision"* item beside it is now answerable: the recipe owns the floor. |
| 6.9 | `NEXT_CASES_SLATE.md` L112-116 | seven-rung Cd list, *"band taken as largest spread × 1.25 = 0.00507"* | **A** | The band figure predates rung 8 and carries no scatter. |
| 6.10 | Tier B of the inventory — display names, routing, filming, Cp/pressure-slice validation, mesh-quality audits, cost/contention precedents, geometry registry, certificates | ~150 sites | **N** | Verified as identity, a **different measurement** (the 193,880-cell Cp slice validation), or timing precedent. **No committed figure anywhere in the repo draws the B-52 ladder**, so there is no plot to correct. |

## 7. What would actually settle it, priced

The audit's own weakness is that σ is bracketed by a factor of 2.6 on n = 2, 2
and 3. Closing that is cheap and it is the difference between "not established
either way" and a verdict:

| arm | what it buys | basis | core-min |
| --- | --- | --- | --- |
| two further draws at rung 6 (n = 5) | σ at rung 6 to ~±30% instead of ~±60% | measured, this arm: 10.7 each | **21.4** |
| one further draw at rung 7 (n = 3) | the turn's *other* end, currently n = 2 | rung 7 measured: 1.28 mesh + 8.73 solve | **10.0** |
| | | **total** | **≈31.4** |

At ≈31 core-min the turn either clears 3σ and the shape claims are reinstated
with a band, or it does not and Tier 1 withdraws on evidence rather than on a
bracket. **I am not proposing this as approved work** — it is the price of the
alternative to ruling on 0.91–2.38×, stated so the chief can choose between them.

## 8. Summary

| tier | **W** | **A** | **S** | **N** |
| --- | --- | --- | --- | --- |
| 1 — core shape | 3 | 5 | 0 | 0 |
| 2 — fits and bands | 0 | 4 | 3 | 0 |
| 3 — SDK / thresholds | 0 | 3 (+1 escalated) | 1 | 2 |
| 4 — charters | 0 | 4 | 1 | 0 (+1 new rule proposed) |
| 5 — cross-case / docket / product | 1 | 6 | 3 | ~150 |
| **total** | **4** | **22** | **8** | **~152** |

**Nothing here has been changed.** Four claims are marked for withdrawal, 22 for
amendment, one item (the `extrapolation_sanity` calibration at 3.2) is escalated
rather than ruled on, one new charter rule is proposed, and three mechanical
hazards are flagged: the by-line-number charter citations (5.3), the duplicated
docket text (6.6), and the proposal generators that would re-emit withdrawn text
(6.7).
