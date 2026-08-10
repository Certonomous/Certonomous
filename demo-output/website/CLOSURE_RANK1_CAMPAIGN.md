# The rank-1 campaign — costed, ranked, and pre-registerable

> **SUPERSESSION NOTE, added 2026-08-10 (Ladder V rung V14, stale-surface item 4).
> This plan's starting position is round 4 and round 4 is no longer the entry of
> record.** Round 4 held that status until **2026-08-07**, when round 5 (untrained
> QCR2000 duct forward solve, the sixth pre-registered scoring call) superseded it at
> **0.056647** overall. Every present-tense *"our entry of record is round 4,
> 0.065438"* below — §1's opening sentence, its per-case table, and the *"today
> (round 4)"* row of §1's *what fixing the ducts is worth* scenario table — is
> **the position as it stood on 2026-08-05**, not the lab's current standing. Current
> standing: `closure_challenge_round5_qcr.json`; caveats: `CLOSURE_CHALLENGE_STATUS.md` §0f.
>
> **The plan's own arithmetic is deliberately left as written.** The −0.005913 deficit,
> the per-case gaps and the route pricing are the reasoning that produced the round-5
> decision; re-basing them onto round 5 would rewrite a plan into a report of its own
> outcome and destroy the record of what was decided on what evidence.
>
> **On the figure 0.065438.** It is the mean of the eight *rounded* per-case values
> (0.0654375), not the full-precision round-4 overall, which is 0.06543140783850523
> (`closure_challenge_trained_entry_round4_duct.json`). §1 states that construction
> itself — *"Both reproduce from their per-case columns exactly"* — and the comparison
> it is used for, against Reissmann's 0.059525, is like-for-like on the same
> construction. So it is left exactly as written: changing it would break the
> like-for-like comparison the whole section rests on. Recorded here because the same
> mean-of-rounded construction is a Pass-2 finding (claim C8) against the word
> *"published"* on 0.059525.
>
> **The premise has since been met, and a rank claim carries its companion.** Round 5
> stands at **rank 1 of 5 scored locally** at benchmark commit `deb91557` — a local
> scoring, not an official placement; nothing has been submitted. **P(rank 1) = 68%**,
> and an eight-case sample cannot pin it tighter than **2–100% at 95%**. The leads over
> Reissmann and Wu & Zhang are **not statistically decided** (t = −0.50 and −0.95); the
> leads over Liu and Montoya are (98.7%, 99.8%). Source:
> `campaign/PROBABILITY_OF_RANK_2026-08-10.md`.

Drafted 2026-08-05. Katie's directive: *the closure challenge continues until
we are #1.* This document is the plan that follows from it, built only from
numbers the lab has measured or read, with every route's expected gain bounded
by the C2 decomposition and every cost anchored to a run on this box.

**TEST-BLIND.** No test-case ground truth is read anywhere in this plan. Test
*scores* already known from prior scoring calls are quoted, because they are on
the record and hiding them would not unknow them — but §6 states the discipline
that keeps knowing them from becoming selection on them, and it is the
load-bearing paragraph of the whole document.

Sources: `CLOSURE_METHODS_COMPARISON.md` (audit, 2026-08-04),
`closure_challenge_C2_error_decomposition.md`,
`closure_challenge_C6_hump_decision.md`,
`closure_challenge_trained_entry_round4_duct.json`,
`campaign/W3_QCR_DUCT_FALSIFIER.md` (measured today),
`/home/ubuntu/certonomous-runs/S1-cbfs-inversion/` (running now).

---

## 1. The deficit, per case, against rank 1

Our entry of record is round 4, **0.065438**. Rank 1 is Reissmann, Fang &
Sandberg at **0.059525**. Both reproduce from their per-case columns exactly.

| # | case | ours (R4) | Reissmann | our delta | contribution to the overall gap (delta / 8) |
|---|---|---|---|---|---|
| 1 | `alpha_15_13929_4048` | 0.0501 | 0.0592 | **−0.0091** | −0.00114 |
| 2 | `alpha_15_13929_2024` | 0.1011 | 0.1339 | **−0.0328** | −0.00410 |
| 3 | `alpha_05_4071_4048` | 0.0461 | 0.0606 | **−0.0145** | −0.00181 |
| 4 | `alpha_05_4071_2024` | 0.0719 | 0.0760 | **−0.0041** | −0.00051 |
| 5 | `AR_1_Ret_360` | 0.0811 | 0.0387 | **+0.0424** | **+0.00530** |
| 6 | `AR_3_Ret_360` | 0.0775 | 0.0341 | **+0.0434** | **+0.00543** |
| 7 | `AR_14_Ret_180` | 0.0325 | 0.0325 | 0.0000 | 0.00000 |
| 8 | `NASA_2DWMH` | 0.0632 | 0.0412 | **+0.0220** | **+0.00275** |
| | **overall** | **0.065438** | **0.059525** | | **+0.005913** |

**We need −0.005913 to draw level and anything beyond it to lead.**

### The one fact that sets the whole campaign

**We are already ahead of rank 1 on four of eight cases, by a combined
−0.00756 on the overall.** The entire deficit and more sits in three cases:

- **`AR_1_Ret_360` + `AR_3_Ret_360` = +0.01073.** That is **1.8× the whole
  deficit**, in two cases, in one flow family, on the family whose training
  data we hold and whose physics we measured today.
- `NASA_2DWMH` = +0.00275, the remaining 0.47× — and C6 has already
  established that this one cannot be legitimately attacked (§4).

So the campaign is not eight problems. It is **two ducts**, and everything else
is either already won or already ruled out.

### What "fixing the ducts" is worth, arithmetically

| scenario | AR_1_360 | AR_3_360 | AR_14_180 | resulting overall | vs Reissmann |
|---|---|---|---|---|---|
| today (round 4) | 0.0811 | 0.0775 | 0.0325 | 0.065438 | +0.0059 (rank 3) |
| **match rank 2's ducts** | 0.0455 | 0.0399 | 0.0325 | **0.056288** | **−0.0032 → RANK 1** |
| match rank 1's ducts | 0.0387 | 0.0341 | 0.0325 | **0.054713** | −0.0048 → rank 1 |

**Matching the rank-2 entry's duct scores — not rank 1's, rank 2's — takes the
lab to rank 1 outright, without touching the hump and without touching the
hills.** That is the whole campaign in one line, and it is why the rank-2
parity items (`w3-qcr-constitutive-term-for-rank2-parity`,
`w3-beta-on-omega-destruction-model-patch`) stopped being a bookkeeping
exercise in like-for-like comparison and became the score plan.

---

## 2. Why we lose the ducts: it is a model-class gap, not a tuning gap

Read from the entrants' own documents (`CLOSURE_METHODS_COMPARISON.md` §2):

| entrant | duct correction | where it acts | AR_1_360 / AR_3_360 |
|---|---|---|---|
| Reissmann (1) | GEP symbolic anisotropic Reynolds-stress correction + refitted SST coefficients | **inside the PDE, twice** | 0.0387 / 0.0341 |
| Wu & Zhang (2) | SST-QCRC: QCR2000 constitutive term + conditioned beta on omega destruction | **inside the PDE, twice** | 0.0455 / 0.0399 |
| **ours (3)** | gradient-boosted `δU` added to a converged field | **outside the PDE, post hoc** | **0.0811 / 0.0775** |
| Liu/Wang (4) | — | — | 0.0875 / 0.0805 |
| Montoya (5) | — | — | 0.0895 / 0.0866 |

The board splits cleanly on that column and nothing else. **Both entrants above
us solve a modified equation; all three entrants at or below us post-process a
field.** Reissmann trains on `AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`,
`AR_10_Ret_180` — the *same four training ducts* the lab holds — so the gap is
not a data gap either. It is the model class.

**Independent corroboration, from a sweep that was not looking for this.** The
method-priority review of 2026-08-05 (`d84b649f`) went looking for prior art on
our method and reported, as a by-product of 27 searches and 20 fetches:

> Inside the turbulence-closure literature the sweep found no other post-hoc
> velocity correction at all — **every located data-driven RANS correction
> re-enters the equations**.

That is the same finding as the table above, reached from the literature rather
than from the leaderboard, and it is the stronger form of it. Our post-hoc
`δU` is not merely behind the two entrants above us on the board; it is
**outside the class the field uses**, and the nearest located prior for it
(Hanna, Dinh, Youngblood & Bolotnov 2017) is a grid-error surrogate on a
lid-driven cavity, not a closure correction at all. Two independent lines of
evidence now say the same thing, and neither was collected to say it.

And the mechanism is now measured on this box, not inferred
(`W3_QCR_DUCT_FALSIFIER.md`): stock SST produces duct secondary flow at
**3e-16 of bulk** against a reference **0.66–0.81 percent**, on all four
training ducts. A post-hoc `δU` regression is being asked to synthesise, from
features, an entire flow structure the underlying solve does not contain. An
in-PDE term is asked only to let the solve produce it.

---

## 3. The routes, costed from measured numbers

### Route A1 — untrained QCR2000 forward on the ducts ★ TOP-RANKED

**What it is.** The library built and validated today
(`sdk/openfoam/qcr/kOmegaSSTQCR/`, ~180 lines, `Ccr1 = 0.3` from Spalart 2000)
run as a plain forward primal on the duct meshes. **No training of any kind.**

**Measured evidence, today, on the four training ducts:**

| case | SST scaled MAE | QCR scaled MAE | ratio | in-plane r vs reference |
|---|---|---|---|---|
| `AR_1_Ret_180` | 0.1076 | 0.0632 | 0.587 | 0.953 |
| `AR_3_Ret_180` | 0.1122 | 0.0477 | 0.425 | 0.935 |
| `AR_5_Ret_180` | 0.0958 | 0.0437 | 0.456 | 0.930 |
| `AR_10_Ret_180` | 0.0604 | 0.0401 | 0.664 | 0.877 |

**Expected gain, bounded honestly.** Transferring the ratio to the published
test-duct floors (0.1288, 0.1243) — and keeping the existing ML prediction on
`AR_14_Ret_180`, where our 0.0325 already ties rank 1 and the AR_10-analogue
ratio would make it worse:

| ratio used | AR_1_360 | AR_3_360 | overall | rank |
|---|---|---|---|---|
| best observed (0.425) | 0.0547 | 0.0528 | **0.05905** | **rank 1**, by 0.0005 |
| aspect-matched (0.587 / 0.425) | 0.0756 | 0.0528 | **0.06166** | rank 2 |
| worst observed (0.664) | 0.0855 | 0.0825 | 0.06661 | rank 3, **worse than now** |

**Central estimate 0.0617 (rank 2); the band spans rank 1 to a regression.**
That spread is the honest state of knowledge and it is exactly why §5's
validation arm is mandatory rather than nice-to-have.

**The structural advantage that no ML route has.** Round 4's demonstrated
failure mechanism is feature extrapolation — `Re_y` reaching 1.85× and 2.07×
the trained maximum on the two ducts we trail, and a gradient-boosted tree
cannot extrapolate. **QCR has no training range.** It is a closed-form
constitutive relation with a published constant; the Reynolds-number transfer
from `Ret 180` training to `Ret 360` test, which is the single axis that has
cost this entry points, **does not apply to it at all**. It also carries the
smallest leakage surface of anything the lab could submit: nothing is fitted,
so there is nothing that could have been fitted on the wrong data.

**Cost, from today's measured wall times (1 core per arm):**

| solve | cells | baseline iters (shipped log) | est. core-min |
|---|---|---|---|
| `AR_7_Ret_180` QCR (validation arm) | 15,463 | 3,636 | 7 |
| `AR_7_Ret_180` SST (validation control) | 15,463 | 3,636 | 7 |
| `AR_1_Ret_360` QCR | 3,025 | 405 | 1 |
| `AR_3_Ret_360` QCR | 8,748 | 1,540 | 4 |
| `AR_14_Ret_180` QCR | 31,819 | 7,009 | 28 |
| subtotal | | | 47 |
| ×1.5 for the cap-stop reruns AR_5/AR_10 already demonstrated | | | **70** |
| contingency to 2× | | | **95** |

Anchors: `AR_10_Ret_180` (22,090 cells, 3,000 iters) measured **8.15 core-min**;
`AR_3_Ret_180` (6,627 cells, 1,725 iters) measured **3.03 core-min**.
Interpolation to the 1,000 evaluation points reuses existing machinery at
zero solver cost.

**Expected-gain-per-core-min: 0.0037 / 95 ≈ 3.9e-5 per core-min.**

---

### Route A2 — the full rank-2 parity model (QCR + beta on omega destruction)

**What it is.** Route A1's constitutive term *plus* the trained
conditioned beta on the SST omega destruction term — i.e. SST-QCRC, the rank-2
entry as it actually is. Half of it is built. The other half is
`w3-beta-on-omega-destruction-model-patch`, whose full patch spec already
exists (W2 reading §5: two lines at `DAkOmegaSST.C:745` and `:870`, plus a
mirrored `READ_IF_PRESENT` field; registration is name-only via
`DAInputField.C:107`).

**Expected gain.** This is the only route with a *demonstrated* target: rank 2
achieved 0.0455 / 0.0399 with exactly this model. Matching it gives
**0.056288 — rank 1 by 0.0032** (§1). Gain **0.0091**, the largest on the board.

**Cost, and the honest part is the unpriced part.**

| component | est. core-min | basis |
|---|---|---|
| DAFoam rebuild with the destruction hook | **0 solver, unbounded risk** | never done for DAFoam; `dafoam-subpclu:v1` on this box is precedent for *a* patched rebuild; build wall-time still unmeasured |
| FD verification of the new hook | 30 | S1 protocol, ~1.7 core-min per gradient on the 5k tutorial |
| field inversion on 4 training ducts | 300–600 | S1 CBFS (21,000 cells) cost **283 core-min for 15 evaluations** and is still running; the four ducts are 2.2k–22k cells |
| symbolic/feature regression beta(features) | ~0 | host-side |
| forward solves | 95 | = route A1 |
| **total** | **425–725 + a build that may not work** | |

**Expected-gain-per-core-min: 0.0091 / 575 ≈ 1.6e-5 per core-min**, and that
number is optimistic because it prices the build at zero.

---

### Route B — the hump via the legally-trained CBFS route

C6 ruled this **legal but undemonstrated**. Asked to state exactly what blocks
demonstration and what unblocks it:

**What blocks it, precisely.** Not legality — the README (lines 63–67) and the
challenge preprint (§2.1, verbatim quotation verified 2026-08-02) both permit
training on CBFS. What blocks it is that **the evidence which would justify the
choice does not exist inside the benchmark**:

1. **No legal held-out flow sits at the hump's Reynolds number.** The hump is
   Re_h ≈ 9.3×10⁵ (Buchanan et al. 2025, §2.4/Table 2). Every non-test
   separating flow the benchmark ships is within a factor of ~2 of 10⁴ — CBFS
   at 1.37×10⁴, the hills at ~10⁴. A CBFS-trained model would be **validated on
   nothing resembling the target regime**.
2. **CBFS extrapolates on the hump on 7 of 7 features** (measured,
   `closure_challenge_cbfs_donor_coverage.json`), and is the *worse* donor
   precisely on `Re_y` — 26.2% of hump cells outside its range against the
   hills' 18.2% — which is the one axis round 4 demonstrated with scores costs
   this entry points.
3. **We already know the hump's score.** 0.0632 from round 2. Any model choice
   made now is made by somebody who has seen it.

C6's verdict stands verbatim: *"That is not a pre-registration that could be
honoured; it is a coin flip with a paper trail."*

**What would unblock it, and whether anything has.** Three unblockers were
conceivable, and the honest answer is that **none of them has fired**:

- *A donor at the hump's Reynolds number.* Would unblock it completely. None
  exists in the benchmark and importing outside data is a new-family question
  with its own charter cost. **Not available.**
- *The sub-LU adjoint + S1 inversion changing the picture.* It has changed it,
  **against** the route — see Route C. The inversion machinery now works, and
  the first thing it measured is that the beta hook has almost no authority.
- *A route that needs no donor at all.* This one is real and it is new: **QCR
  is untrained.** Applying it to the hump requires no donor, no training set
  and no Reynolds-number match, and so escapes objections 1 and 2 entirely.
  Objection 3 (we know the score) still binds and is handled by §6's protocol.

**Route B′, therefore — the sub-route worth naming.** Before spending anything
on the hump, run **QCR on CBFS**, a *training* case with LES truth. It answers,
legally, the only question that matters: *does the QCR term help a
two-dimensional smooth-wall separation at all, or is it a corner-flow term
only?* Prior expectation from the literature is that QCR2000 is a
secondary-flow/corner term with little effect on 2D separation, so **the most
likely outcome is a clean no**, which retires the hump.

> **COST CORRECTION, and it changes this route's ranking.** An earlier draft of
> this document priced B′ at 10 core-min "as a cheap rider on A1." **That was
> wrong by a factor of about eight and is corrected here rather than left to be
> discovered at launch.** The error was pricing on cell count alone and never
> opening the case's `controlDict`. CBFS is 21,000 cells but runs to a **fixed
> `endTime` of 30,000 iterations** with `residualControl` effectively disabled
> (`p` at 1e-15, `U`/`k`/`omega` commented out) — it is designed not to
> auto-stop, and its shipped `log.run` runs the full 30,000. Re-priced from
> today's measured anchor (`AR_10_Ret_180` QCR: 22,090 cells × 3,000 iters =
> 8.15 core-min): (21,000/22,090) × (30,000/3,000) × 8.15 ≈ **78 core-min for a
> single QCR arm**, comparing against the shipped baseline field so no SST arm
> is needed. B′ is therefore **not a rider on A1 — it costs most of what A1
> costs**, and it must be ranked as its own item competing for the same budget,
> not waved through as small. Imposing a `residualControl` to stop it early
> would cut this, but that is a deviation from the shipped case setup and would
> owe its own justification.

**Best available hump move remains C6's Route A: decline to correct it.**
0.0632 → 0.0621, worth **+0.00014 on the overall, for zero compute**. It does
not move the rank and it must not be sold as if it does.

**Expected-gain-per-core-min:** decline = 0.00014 / 0 core-min (take it, but
it is a rounding error); B′ gate = 0 direct gain / **78** core-min, valued as a
**decision**, not a score — and at 78 core-min it is a decision the campaign
can defer until A1 has reported, since A1's outcome may make the hump
irrelevant either way.

---

### Route C — learned-beta forward solves from the S1 inversion

**What it is.** Stage 2 of the roadmap: regress beta(features) from the S1 CBFS
field inversion and apply it forward — the Wu-Zhang-class route, now that the
inversion machinery runs.

**This route must be re-ranked downward on evidence produced while this
document was being written, and that evidence is the most important negative
result in the plan.**

The S1 CBFS inversion (`/home/ubuntu/certonomous-runs/S1-cbfs-inversion/`) has
run 16 evaluations over 310 core-min and has **plateaued** — gradient norm down
to 9.0e-6, J flat to eight figures across evaluations 11–16:

| eval | J_qoi (normalised, 1.0 at beta ≡ 1) | total J (with L2) | beta range | ‖g‖ |
|---|---|---|---|---|
| 1 | 1.00000000 | 1.00000000 | 1.000 – 1.000 | 9.53e-04 |
| 5 | 0.99859936 | 0.99910404 | 0.729 – 1.116 | 1.01e-04 |
| 10 | 0.99850747 | 0.99907935 | 0.735 – 1.144 | 1.45e-05 |
| 14 | 0.99850656 | 0.99907903 | 0.735 – 1.145 | 9.24e-06 |
| **16** | **0.99850655** | **0.99907903** | 0.735 – 1.145 | **9.01e-06** |

**It missed its own pre-registered bar by more than two orders of magnitude.**
`S1_CBFS_INVERSION_PREREGISTRATION.md` §7, gate G1, fixed before the run:

> `J_qoi = lambda_QoI * varianceU` falls from 1.000 to **≤ 0.70** (≥ 30%
> reduction) at the last accepted iterate within budget.

Measured: **0.99851 — a 0.149 percent reduction against a 30 percent bar**, or
**0.092 percent** net of the L2 penalty on the total objective. The inversion
delivered one two-hundredth of what it pre-registered. It did so while moving
beta by up to ±26 percent per cell, under a penalty so light it contributes
0.00057 of a 0.99908 objective — a converged weak optimum, not a regularisation
artefact, and not a budget shortfall either: the gradient is flat.

**What that bounds.** A Stage-2 regression beta(features) is bounded above by
the inversion field it is fitted to. If the *optimal* beta field recovers 0.15
percent of the discrepancy, a smooth regression of it recovers less. **Route C
is measured to have essentially no authority on its own objective**, before any
question of transfer to a different case even arises.

### 3.C.1 The production-versus-destruction question this forces open

The plateau does not by itself say *why*, and the three candidate causes have
very different consequences for Route A2, which also depends on a beta
inversion. Naming them is the re-pricing this result demands:

| candidate cause | consequence for A2 | how it would be told apart |
|---|---|---|
| **(a) The production hook is the wrong lever.** Ruling R6 restated Stage 1 onto omega *production* because that is what DAFoam exposes; Wu & Zhang invert on *destruction*, with a wall-distance conditioning `f_d = 1 − tanh((8 r_d)³)` that confines the correction away from walls. Scaling production by beta and destruction by 1/beta are **not** equivalent equations, because the remaining omega terms do not scale. | **Best case for A2**: the destruction patch is not a parity nicety, it is the difference between a lever that works and one that does not — and A2 becomes the *necessary* route rather than the expensive one. | Build the destruction hook and invert the same CBFS case against the same bar. The comparison is like-for-like by construction. |
| **(b) The CBFS case or the `varianceU` objective is the weak part.** An all-cells field variance may simply be a poorly-conditioned target. | **Neutral to bad for A2**: the duct inversions would need their own objective design, and the 300–600 core-min estimate is optimistic. | Invert one *duct* on the existing production hook. Cheap relative to A2 (the ducts are 2.2k–22k cells against CBFS's 21k) and it separates case from hook. |
| **(c) Scalar field inversion on this solver has little authority generally.** | **Worst case for A2**: its inversion stage is not worth funding at all. | Follows if both (a) and (b) are tested and neither recovers authority. |

**The lab cannot currently distinguish these, and should say so rather than
assume (a).** Assuming (a) is the comfortable reading — it is the one that
keeps the roadmap intact — and it is exactly the kind of assumption the
supervisor-adversarial standard exists to refuse. What can be said is that
**the discriminating experiment is cheap relative to the route it gates**: one
duct inversion on the hook that already exists, at a fraction of A2's cost,
tells the lab whether A2's 300–600 core-min inversion stage has a lever at all.
That check belongs in front of A2's budget approval, and A2's cost basis should
absorb it.

**This is also why the A1-first sequencing is not merely cheapest but
risk-correct.** A1's QCR half is *measured to work* (33–57 percent scaled-MAE
reduction, §3 Route A1). A2 = A1 + a beta whose lever is now in question. So
**A2 degrades gracefully to A1**: if the beta half proves to have as little
authority on ducts as it had on CBFS, the campaign still holds everything A1
delivered. Running A2 first would have put the measured half behind the
unmeasured one.

Three further points, each independently sufficient to de-rank it:

1. **CBFS is not a scored case.** Route C's target is the hump, via Route B,
   which §4 has already established is not demonstrable.
2. **The hook is the wrong one.** Ruling R6 restated Stage 1 onto the omega
   *production* term because that is what DAFoam exposes. Wu & Zhang invert on
   *destruction*. Route C as buildable today is not the paper's route — it is
   the route that fits the tool, which is how the lab got here.
3. **It shares its blocker with Route A2 and A2 is worth six times more.** If
   the destruction-term patch is going to be built, build it for the ducts,
   where the deficit is.

**Expected-gain-per-core-min: indistinguishable from zero**, against 283
core-min already spent.

Stated plainly so the record is not read backwards later: **the 283 core-min
was not wasted.** It bought a measured bound on the production hook's authority
that no amount of reasoning would have produced, and it is what lets this plan
de-rank a route it would otherwise have funded.

---

## 4. The ranking

| rank | route | expected overall gain | cost, core-min | gain per core-min | build risk |
|---|---|---|---|---|---|
| **1** | **A1 — untrained QCR forward on ducts** | **+0.0037** (band −0.0007 to +0.0063) | **95** | **3.9e-5** | **none — built and validated today** |
| 2 | A2 — full rank-2 parity (QCR + beta destruction) | +0.0091, **now conditional** (§3.C.1) | 425–725, **+ a discriminating duct inversion its basis must absorb** | 1.6e-5 | **high**: unpriced DAFoam rebuild **and** a beta lever measured weak on CBFS |
| 3 | B-decline — ship the hump uncorrected | +0.00014 | **0** | — | none |
| 4 | B′ — QCR-on-CBFS gate for the hump | 0 (a decision, not a score) | **78** (was mispriced at 10) | n/a | none |
| 5 | C — learned-beta forward from S1 | ~0, **measured**: 0.149% against a 30% bar | 310 spent | ~0 | — |

**A1 leads on every axis that matters**: highest gain per core-min, lowest
cost, zero build risk, zero leakage surface, and it is the only route whose
enabling artifact already exists and has already been validated against a
bit-exact control. A2 has the larger prize and should follow A1 rather than
replace it — **A1's forward-solve infrastructure is A2's forward-solve
infrastructure**, so A1 is not a detour, it is A2's first stage delivered early
and cheaply.

**Two changes since this ranking was first drafted, both of which widened A1's
lead rather than narrowed it:**

- The S1 plateau (§3.C.1) moved A2's beta half from *assumed to work* to
  *measured weak on the one case it has been tried on*. A1 is unaffected,
  because A1 contains no beta.
- B′ turned out to cost 78 core-min, not 10, so the campaign's cheapest probe
  is no longer cheap and the hump recedes further.

**The sequencing that follows:** A1 → A2 **only after** the discriminating duct
inversion of §3.C.1 shows the beta lever has authority → B′ and the hump last,
if at all. Note from §1 that if A1's *best* observed ratio transfers, **A1
alone reaches 0.05905 and takes rank 1 without A2, B or C at any point.**

---

## 5. Pre-registration requirements, per route

Nothing here may run against a test case before its pre-registration is
written, committed, and frozen.

**Route A1 must pre-register, before any test duct is solved:**

1. **The model, frozen.** `kOmegaSSTQCR`, `Ccr1 = 0.3`, the exact library
   commit hash. `Ccr1` is **never** to be tuned — the moment it is fitted, the
   route loses the no-training-range property that is its entire advantage, and
   it acquires a leakage surface it does not currently have.
2. **The validation arm, run first and reported whatever it says.**
   `AR_7_Ret_180` is the benchmark's own suggested duct validation case and the
   lab already used it to select Variant D. Run SST and QCR on it, score both
   against its LES field, and record the ratio **before** any test duct runs.
3. **The per-case application rule, stated in advance and honoured.** This is
   the clause that carries the integrity of the whole route, because we already
   know our three test-duct scores. The rule must be a function of validation
   evidence alone. Proposed form, to be frozen before running: *apply QCR to a
   test duct if and only if QCR beat SST on `AR_7_Ret_180` by more than X
   percent of scaled MAE; apply it to all three test ducts or none.* An
   all-or-none rule is deliberately chosen over per-case selection precisely
   because per-case selection is where a known test score would leak in.
4. **The `AR_14_Ret_180` question, decided in advance.** Our ML model scores
   0.0325 there and the AR_10 analogue ratio suggests QCR would do worse. That
   suggestion comes from *training* data and may legitimately inform the
   pre-registered rule; the 0.0325 *test score* may not. If the rule is
   all-or-none, this case follows the rule and the possible loss is accepted in
   writing beforehand.
5. **The convergence criterion.** `AR_14_Ret_180`'s shipped baseline took 7,009
   iterations; today's runs demonstrated `residualControl` cap-stops at 3,000.
   Set the cap from the shipped log per case, and report any cap-stop as a
   cap-stop (`w7-cap-stopped-is-a-monitor-signature`).
6. **A physicality check on the submitted field**, closing audit finding G2 for
   this route at least: QCR fields come out of a solenoidal solve, so unlike
   the ML `δU` they satisfy continuity by construction — measure it and say so,
   since it is a genuine advantage over the current entry and costs nothing.

**Route A2 additionally pre-registers:** the FD-agreement threshold for the new
destruction hook (S1 achieved 2.67 percent), the inversion's regularisation and
stopping rule, the regression family, and a commitment to ship the result
whatever it is. It also owes **two** measurements before its solver budget is
approved, not one:

1. **The build cost.** Its own cost basis says to price the build before the
   solve, and that is still unpriced.
2. **The discriminating duct inversion of §3.C.1**, on the production hook that
   already exists. A2's inversion stage is 300–600 core-min premised on a lever
   that has been tried exactly once and returned 0.5 percent of its
   pre-registered bar. Approving that budget without first establishing whether
   the lever works on a duct at all would be funding an assumption. **And its
   success bar must be set before it runs, and set at a level that can fail** —
   S1's G1 bar was honest precisely because 0.99851 could not be dressed up as
   a pass.

**Route B′ pre-registers** its threshold — what improvement on CBFS would
justify a hump probe, written before CBFS is scored — and, at 78 core-min, now
also owes the comparison against simply spending those 78 core-min on A1's
contingency instead.

---

## 6. The scoring-call policy for round 5

**Round 5 is one scoring call, and everything is validated before it.**

The benchmark imposes no limit and explicitly invites previewing; this is
self-imposed discipline, and it is the reason the entry's provenance chain
survives audit. What it means operationally:

- Every model decision — which cases QCR is applied to, which keep the ML
  correction, whether the hump is declined — is **fixed by the pre-registered
  rules of §5 acting on validation evidence**, and committed, before the call.
- The call produces the round-5 per-case table. **Whatever it says is what
  ships.** If QCR turns out worse on a test duct than the ML model, that is
  reported, exactly as the NASA_2DWMH +0.0011 regression was reported in round
  2 rather than quietly fixed.
- **The known round-4 scores are the sharpest hazard in this campaign** and
  should be named as such in the round-5 record. We know we score 0.0811 /
  0.0775 / 0.0325 on the three test ducts. Any protocol that lets those numbers
  choose between two candidate models is test-truth-informed model selection —
  the same defect C2 named and refused, one level up. The all-or-none rule of
  §5.3 exists specifically to remove the degree of freedom through which they
  would enter.
- Before the call: all four audit gaps that touch the round-5 submission are
  closed — the manifest hashes (G4, now done for round 4), a finiteness
  assertion, the baseline-convergence citation (G3), and the divergence
  measurement (G2) for every submitted field.

---

## 7. What is filed

`w3-qcr-forward-on-the-ducts-is-the-rank-1-route` — **Route A1**, filed as a
docket proposal alongside this document: 95 core-min, `source_kind: challenge`,
HARD criterion 6 (challenge-aligned), schema-clean at intake.

Routes A2, B′ and C are recorded here and deliberately **not** filed:

- **A2** is blocked behind two unpriced measurements, not one — the DAFoam
  rebuild its own item already names, and now the discriminating duct inversion
  of §3.C.1. It should be filed when those are priced, not before.
- **B′** was going to be filed as a cheap rider and is not, because it turned
  out to cost 78 core-min rather than 10. It competes with A1's contingency and
  loses.
- **C** is de-ranked by its own measurement, against its own pre-registered bar.

**A note on how this document should be read if A1 succeeds.** Nothing here
claims QCR is a better model than the ML correction in general. It claims
something narrower and better supported: on a flow family whose defining
structure the linear closure expresses at machine zero, a term that puts the
structure into the equation beats a term that predicts it from features — and
the two ducts where that is true happen to be where the entire rank-1 deficit
sits. That is a statement about ducts, not a thesis about turbulence modelling,
and the round-5 record should say so in those words.
