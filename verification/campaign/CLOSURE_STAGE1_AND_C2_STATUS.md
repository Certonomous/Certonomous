# Closure family status — G2 is not a localisation gate, C2's referent, and what the submission rules actually say

Frame, stated once and applying to every number below. Repo `/home/ubuntu/Certonomous`
at commit `64281b6b`, branch `main`, 2026-08-11. Run evidence read from
`/home/ubuntu/certonomous-runs/` — **outside the repo**, therefore invisible to any
repo-scoped sweep, and `grep -r` here execs `ugrep --ignore-files` which additionally
skips gitignored paths; every sweep in this document used `find` + `/usr/bin/grep`.
Benchmark clone read at `/home/ubuntu/closure-challenge-benchmark/`, local HEAD
`deb9155`. **No solver, no inversion, no container was launched for this document.**
Every computation here is host-side arithmetic on already-written files: **0 core-min.**
**Nothing was sent, filed, uploaded, registered or published.**

---

# 1. G2 is not a localisation gate — proven by construction, at zero compute

**The question put to this investigation was whether G2's 26.9% is a real physical
finding about where model-form error lives, or an artefact of the window definition,
the top-decile threshold, or the loss's spatial support.**

**Answer: artefact — and a stronger statement than "artefact" is available and proven.
G2 is not a monotone function of the property it exists to measure. It awards its worst
possible score to the most perfectly localised correction that can be constructed.**

The localisation the gate was built to detect **is present, and is overwhelming**. It is
the gate, not the physics, that fails.

## 1.1 What G2 says, and what it was checked against

G2, frozen in `dafoam/ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md` §6 (shape before
any compute) and §D of Amendment 1 (numbers before launch):

> **G2 — the correction lives where the physics says the model error lives:** among the
> top-decile |beta_final − 1| cells, **> 50%** inside **0 ≤ x/h ≤ 6, 0 ≤ y/h ≤ 2**.

Implemented at `/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/audit_final.py:54-60`.
I re-implemented that definition independently from the written OpenFOAM fields and
reproduce both published values exactly:

| field | G2 | record | verdict |
| --- | --- | --- | --- |
| equal-weight reinversion, eval 16 (`cbfs_inv/2500/betaFIOmega`) | **26.9%** | 26.9% | reproduced |
| weighted arm, eval 7 (`S1-cbfs-weighted-arm/cbfs_inv/2500/betaFIOmega`) | **42.7%** | 42.7% | reproduced |

Window = **1773 of 21000 cells = 8.44%** (record: 8.4%). W2 support = **2970 cells =
14.14%** (prereg: 2,970). Both reproduce.

A second, independent recomputation by a separate agent with its own field reader
returned **26.8571%** (563 of 2100) and reproduced every unreviewed side-number in the
result document as well: 39.57% upstream (doc 39.6%), 31.48% at y>2 (31.5%), 75.62%
below 1 (75.6%), mean window β 0.829577 (0.8296), rms|β−1| 0.139628 (0.1396), limiter
24.79%/51.62% (24.8%/51.6%), residual y>2 loss share 77.61% (77.6%). Both plausible
top-decile recipes (`np.quantile(dev,0.9)` with `>=`, and `N//10` by argsort) select the
identical 2100-cell set, so **the published verdict is not recipe-sensitive.**

**One correction to the brief this investigation was given.** G2 did **not** fail at
26.9% both before and after the repair. Pre-repair it was **29.0476%**
(`S1-cbfs-inversion/cbfs_inv/1563/`, and independently confirmed from that run's archived
`idx_topdecile.npy` × `mask_win.npy`); post-repair **26.8571%**. Different β fields,
different thresholds (|β−1| ≥ 0.0058 vs ≥ 0.1216), different top-decile sets. **The
reinversion did not inherit or restate the failed run's number** — the two verdicts
happen to round near each other and are otherwise unrelated.

**A recording gap, not an accuracy gap.** Unlike the failed run, the reinversion captured
no stdout from `audit_final.py` and archived no intermediate arrays. A targeted
`/usr/bin/grep` for its output strings across all three CBFS run trees returns only the
script. **The primary artifact for the G2 row is therefore a script plus its inputs, not
an output.** The number survives independent recomputation to four decimals, so the claim
is sound — but it was reproducible rather than recorded, and the cheap fix is to tee the
audit to a `log.audit`. Same applies to the loss-geography percentages in headline 4.

**Referent label for this section, per Verification Charter §6a: SELF-REFERENTIAL.** I
checked the lab's number against the lab's own written fields with my own arithmetic.
That establishes transcription and implementation fidelity. It establishes nothing about
whether the number means what the gate says it means — which is the next three sections.

## 1.2 The localisation is real, and G2 fails it anyway

| quantity | value |
| --- | --- |
| top-decile cells | 2100 |
| in-window | 564 |
| expected under no localisation | 177.3 |
| **enrichment** | **3.18x** |
| hypergeometric P(X ≥ 564 \| N=21000, K=1773, n=2100) | **5.16e-160** |

The correction concentrates in the separated-flow window at 3.18x the base rate, at a
significance beyond any reasonable doubt. **G2 reads FAIL on this field**, because its
bar is an **absolute share** of the top decile, not an enrichment over the window's own
base rate. A window occupying 8.44% of the domain was asked to hold >50% of the top
decile — a 5.9x enrichment demand — and the bar was never argued for against that base
rate anywhere in the pre-registration.

**The loss support and the gate window are different regions by construction, and this is
readable in the config, not inferred.** `S1-cbfs-reinversion/cbfs_inv/runScript.py:78-89`
declares the objective as `"source": "allCells"` over all three velocity components — the
loss sees **all 21,000 cells × 3 = 63,000 observations, the whole domain**. `0/UData` has
zero all-zero rows, so the LES reference is defined everywhere and the free channel
genuinely enters the loss; 69.6% of cells sit at y > 2. **The optimizer is graded on a
domain 12x larger than the gate's window.**

**Worse, the bar sits above what the loss could deliver.** Amendment 1 §D recorded, in
the very act of confirming the window, that the window *"now carries 41.2% of the loss
with 8.4% of cells"*. An equal-weight loss directs effort where the loss is. A gate
demanding that >50% of the largest deviations land in a window holding 41.2% of the loss
asks the optimizer to concentrate **more sharply than the objective it is minimising
does**. The achieved 26.9% is 65% of that 41.2% loss-proportional ceiling. **The bar was
measurably above the ceiling at the moment it was confirmed, and that arithmetic was
available pre-launch at zero cost.**

## 1.3 The decisive test — a field that passes G2 by containing strictly less

`beta_masked.npy` is on disk at
`/home/ubuntu/certonomous-runs/S1-cbfs-weighted-arm/cbfs_inv/beta_masked.npy`. Its
construction, from `S1_CBFS_WEIGHTED_ARM_PREREGISTRATION.md` Part A: eval-16's β
retained inside the W2 support, **1.0 everywhere else**. It is a pure amputation. No
inversion, no adjoint, no solver, no new information — strictly less than the field it
came from.

I mapped it to serial order through `dv_to_serial_perm.npy` (direction established
against the written field: `|serial[perm] − dv| = 5.107e-15`, matching the record's
5.1e-15 control) and evaluated G2 on it:

| field | G2 (bar >50%) | verdict | window fix retained (gate A, on record) |
| --- | --- | --- | --- |
| equal-weight eval-16 β | 26.9% | **FAIL** | R_W1 = 0.9494 (full) |
| **the same field, amputated** | **53.7%** | **PASS** | R_W1 = 0.9458 — **99.6%** |

**A strict deletion of information converts G2 FAIL into G2 PASS, while making the
physics slightly worse.** Gate A already measured that the amputated field retains 99.6%
of the window fix — so the deviations G2 penalises as mislocated are contributing 0.4%
of the correction, while carrying **58.5% of the top-decile |β−1| mass**. G2 counts
deviation magnitude. Magnitude is not the quantity that carries the fix, and the lab has
already measured the gap between them.

## 1.4 A wrong treatment passes G2 — and the negative control confirms the instrument

Verification Charter §2a asks two questions of every gate. The second is *could a wrong
treatment still pass it?* Here is the answer, computed:

| candidate β field | G2 | verdict |
| --- | --- | --- |
| **pure Gaussian noise on the W2 support — zero physics, no inversion** | **60.8%** | **PASS** |
| equal-weight inversion, eval 16 | 26.9% | FAIL |
| weighted arm, eval 7 | 42.7% | FAIL |
| pure noise over the whole domain (**negative control**) | 8.3% | FAIL |

**A random field with no physical content whatsoever passes G2 more comfortably than
either real inverted field.** The negative control returns 8.3% ≈ the 8.44% base rate,
confirming the instrument is calibrated and that **G2 can fail** — it is therefore not an
*identity* under §2a. It is something else, and arguably worse: **a gate that can fail,
and that fails on the right answer while passing on noise.**

## 1.5 The degeneracy — G2 is non-monotone in localisation

The top-decile threshold has a failure mode nobody registered. `np.quantile(dev, 0.9)`
on a field where fewer than 10% of cells deviate returns **0.0**, so `dev >= thr` selects
the entire domain and G2 collapses to the base rate. Pure noise, confined inside the
window, support shrunk progressively:

| correction confined to | % of domain | top-decile n | G2 | verdict |
| --- | --- | --- | --- | --- |
| 1773 cells (**the whole window, perfect localisation**) | 8.44% | 21000 | **8.4%** | **FAIL** |
| 1241 cells | 5.91% | 21000 | 8.4% | FAIL |
| 531 cells | 2.53% | 21000 | 8.4% | FAIL |
| 2376 cells (W2 support, *less* localised) | 11.31% | 2100 | 49.3% | FAIL |
| 2970 cells (full W2 support, *least* localised) | 14.14% | **59.5%** | **PASS** |

**A correction living entirely inside the separated-flow window scores 8.4% and fails.
A correction smeared over 14% of the domain scores 59.5% and passes.** G2 ranks fields
in the opposite order to the property it names. A localisation metric that is minimised
by perfect localisation is not a localisation metric.

**Stated honestly and without inflation: this degeneracy is not what produced 26.9%.**
Both real β fields deviate in essentially every cell, so both sit far from the threshold
collapse. The degeneracy is independent proof that the metric is invalid, not the
explanation of the observed value. The observed value is explained by §1.2 and §1.6.

## 1.6 Sensitivity to the two free choices

| top-decile threshold | equal-weight | weighted | masked |
| --- | --- | --- | --- |
| top 5% | 40.4% | **62.8% PASS** | 67.0% |
| **top decile (as registered)** | **26.9%** | **42.7%** | 53.7% |
| top quintile | 19.7% | 29.0% | 8.4%¹ |
| top half | 15.5% | 16.2% | 8.4%¹ |

¹ threshold degeneracy, §1.5.

**The weighted arm passes G2 at a top-5% threshold and fails at a top-decile threshold.**
The verdict on that arm turns on a free parameter never argued for. Window geometry is
better behaved — enrichment holds at 3.05–3.18x across every window variant I tried,
which is itself evidence that **the enrichment, not the share, is the stable quantity**:

| window | base rate | G2 | enrichment |
| --- | --- | --- | --- |
| 0≤x≤6, 0≤y≤2 (registered) | 8.4% | 26.9% | 3.18x |
| 0≤x≤6, 0≤y≤3 | 10.7% | 26.9% | 2.52x |
| 0≤x≤9, 0≤y≤2 | 12.8% | 39.0% | 3.05x |
| 0≤x≤4, 0≤y≤2 | 5.4% | 16.6% | 3.08x |

## 1.7 The verdict on G2, and what it does and does not overturn

**G2 is an artefact on three independent counts**, each separately sufficient:

1. **Wrong bar.** An absolute >50% share against an 8.44% base rate, set above the
   window's own 41.2% loss share, measured in the amendment that confirmed it.
2. **Wrong quantity.** It counts |β−1| magnitude. Gate A measured that magnitude is not
   what carries the fix — 99.6% of the window fix survives amputating every deviation
   G2 penalises.
3. **Wrong direction.** Non-monotone in localisation (§1.5), and passable by noise
   (§1.4).

**What this does NOT overturn.** The chief's existing ruling on entry 12 of
`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` — *"the remaining G2 gap is a
loss-support vs metric-support ACCOUNTING mismatch… not a model failure, not a placement
failure"* — is **confirmed and strengthened**, not contradicted. The ruling refused a
G2-bar revision on the grounds that *"the bar caught a real property of the equal-weight
loss"*, and that remains true. What is new here is that the bar **also** encodes three
defects of its own, and that the field which passes it is the one with less information
in it. The recorded gate verdicts stand as failures on the record, correctly, under
§2b — **this document changes no bar and repairs no gate.** It files a finding.

**The physical question G2 was built to ask has already been answered, better, by a
different measurement.** Gate A of the weighted arm — mask every out-of-support deviation
and re-solve — returned R_W1 0.9458 against 0.9494 full. That is an **intervention** on
the field measuring **effect**, not a census measuring magnitude. It says the window fix
is local, at 99.6%. **That is the localisation result. G2 never was.**

## 1.8 The replacement, if one is wanted

Not proposed as a bar, and **nothing here amends anything**: the enrichment ratio with
its hypergeometric tail is base-rate-free, monotone in localisation, window-robust
(3.05–3.18x across variants), and computable at zero compute from fields already on
disk. It also fails the noise control correctly. Whether the S1-with-priors line adopts
it is a design decision belonging to that line's own pre-registration, made **before its
first compute** per §2b.

---

# 2. Stage 1 FIML — what the record establishes and what I verified

## 2.1 What Stage 1 is

Field inversion on the benchmark's **CBFS training case**: a spatially varying β(x)
multiplying the SST ω-equation **production** term (`betaFIOmega_`, `DAkOmegaSST.C:743`),
21,000 design variables, inverted by host-side SciPy L-BFGS-B against
J = λ_QoI·varianceU + λ_L2·Σ(β−1)², with DAFoam's discrete adjoint supplying gradients.
Stage 2 — training an ML map from features to β — is **held** and has not run.

**The term matters and the record is emphatic about it.** Wu, Zhang & Zhang invert on the
ω-**destruction** term; DAFoam exposes β only on **production**; the two are not
equivalent. Nothing in Stage 1 is comparable to their scores. This is carried correctly
in `closure_challenge_C2_error_decomposition.md` (R6 correction) and in
`S1_CBFS_REINVERSION_RESULT.md` §1.

## 2.2 What has actually run

Three items, each pre-registered before its own solves, all budget-capped rather than
converged (charter §4):

| item | cost | G1 | G2 | outcome |
| --- | --- | --- | --- | --- |
| first inversion (corrupted objective) | — | FAIL (−0.149%) | FAIL | diagnosis: objective was measuring the inlet |
| `s1-cbfs-objective-repair-and-reinversion` | **424.80 / 450 core-min** | **PASS 0.25847 (−74.2%)** | **FAIL 26.9%** | repair vindicated |
| `s1-cbfs-weighted-reinversion-arm` (+ eval-8 addendum) | **267.07 / 278** amended cap | **FAIL** G1w 0.05710 vs ≤0.05320 | FAIL 42.7% | localisation answered; G1w unresolvable as posed |

**A stale header found in that arm's record, filed not edited.**
`S1_CBFS_WEIGHTED_ARM_RESULT.md` line 10 reads "229.07 core-min of the 250 hard cap"
while its own addendum at line 124 reads "267.07 against the amended 278 cap". The ledger
sums to **267.07**; the difference (38.00) is exactly `ext001` + `ext002`. **The addendum
is right and the header is pre-addendum** — not an error, but a document stale against
itself, which is precisely the failure mode W-5 was adopted against.

**The inlet diagnosis, verified.** The pre-repair case carried a **uniform 0.72** in
`0/U` where the benchmark ships a developed profile at **bulk 0.914922**. Restoring it
collapsed the β=1 baseline **24.8x** (1.5279e-2 → 6.1509e-4) against a pre-registered
"< 7.6e-3", and moved the inlet-adjacent bulk RANS/LES ratio from 1.272 to 1.0005.

**What I verified myself, and how.** Independently, from primary artifacts, not from the
documents:

| claim | primary artifact | verdict |
| --- | --- | --- |
| **424.80 / 450 core-min** | `S1-cbfs-reinversion/ledger.csv`, 36 END lines summed | **VERIFIED to the cent**; every §7 stage row reconciles line-by-line. Cap is pre-registered (prereg:7), guard in code at `invert_lbfgsb.py:29` (`BUDGET_STOP = 435.0`); `driver.out` terminator reads `OPT ABORTED BudgetStop: cap reached: neval=16 spent=416.70` — **budget-capped, not converged**, as recorded |
| **G1 PASS 0.25847, −74.2%, bar ≤0.70** | `J_history_main.csv` last row, `J_qoi = 2.5846573449516069e-01` | **VERIFIED.** 1 − 0.2584657 = 74.153% → 74.2%. varianceU re-derived from the written 2500 fields as `1.5897973285391019e-04` vs the driver's `…003` — last-bit float agreement, so the reported J_qoi **is** the field state on disk. Bar and its equivalent varianceU ≤ 4.3056e-04 fixed pre-launch at prereg:219-220 |
| **G2 FAIL 26.9%, bar >50%** | `cbfs_inv/2500/{betaFIOmega,C}` | **VERIFIED by recomputation** (26.8571%), twice, by two independent readers — see §1.1 |
| **`0/U` uniform 0.72 → developed profile, bulk 0.9149** | `S1-cbfs-inversion/cbfs_inv/0/U` vs `S1-cbfs-reinversion/cbfs_inv/0/U` | **VERIFIED, and stronger than documented** — see below |
| 21,000 DVs, bounds [0.2, 4.0], per-cell, no basis reduction | `runScript.py:58`, `add_design_var("beta", lower=0.2, upper=4.0)` | VERIFIED |

**The inlet claim is the cleanest-verified item in the set.** Corrupted `0/U` inlet patch:
`nonuniform List<vector> 150`, Ux **exactly uniform 0.72 on all 150 faces**. Repaired: Ux
0.202035889 → 1.00537467, face-mean **0.9149216132** (doc: 0.914922). **Uz max abs diff
between corrupted and repaired = exactly 0** — the overwrite fingerprint confirmed at the
byte level rather than asserted. And the repaired list is **byte-exact against the
benchmark's own file**: `/home/ubuntu/closure-challenge-benchmark/data/CBFS/0/U` gives max
abs diff **0.0 in all three components**. **This is the one place in the S1 line with a
true external referent — the benchmark's shipped inlet.** `0/UData` is byte-identical
between the two cases, so the repair touched only `0/U`, as claimed.

**A mechanism detail the records do not spell out, and it closes the causal story.** The
benchmark file's own `internalField` is `uniform (0.72 0 0)` — 0.72 is the benchmark's
*initial internal* value, exactly what a `patchVelocity` write-back would smear onto the
inlet patch.

**Two wording caveats found and not smoothed over.** (a) 0.9149 is the **face-value
arithmetic mean**, not an area-weighted mass-flux average; the docs call it "bulk", which
is identical only if the 150 inlet faces are equal-area, and face areas were not
confirmable from the files present. **Treat "bulk" as loose usage.** (b) The result doc
says "−74.2% in **16** evaluations" (headline 2) and "in **15** optimization evaluations"
(§5). Both are defensible readings — eval 1 is the β=1 control — but they disagree in
print.

## 2.3 The gates, under the identity test (Verification Charter §2a)

Every gate this document touches, with both questions answered:

| gate | can it FAIL? | can a WRONG treatment PASS? | identity? |
| --- | --- | --- | --- |
| **G1** (norm. J_qoi ≤ 0.70) | **Yes, demonstrated** — the corrupted run reached 0.99851 | **Yes.** J_qoi is the training loss the optimizer directly minimises with 21,000 free parameters. The record documents this happening: late iterations chased the 77.6% of residual loss at y>2, which is reference-interpolation mismatch, not closure physics. **G1 PASS is a capability verdict — the adjoint and optimizer can move the loss — not a correctness verdict.** | No |
| **G2** (>50% top-decile in window) | **Yes, demonstrated twice** (26.9%, 42.7%) — and my noise control returns 8.3% | **Yes, demonstrated.** Pure noise on the W2 support passes at 60.8%. A strict amputation of the failing field passes at 53.7%. | No — **but see §1.5: it is non-monotone, which is a distinct and worse defect than being an identity** |
| **G1w** (norm. Jw ≤ 0.05320) | Yes — it failed, twice, finally | Yes, same structure as G1: a bar on the training objective | No |
| **A** (masked-β nonlocality, R ≥ 0.70) | **Yes** — if the window fix rode on out-of-window β through the flow, R would drop | **Not by any route I can construct.** It is an *intervention* (amputate, re-solve) measuring *effect*. **This is the strongest gate in the family.** Referent: SELF-REFERENTIAL (the field's own unmasked R). | No |
| **P1** (β=1 varU < 7.6e-3) | Yes — the prereg names the falsifying outcome explicitly | Only by a different inlet defect of the same magnitude; low risk | No |
| **P2** (y>2 loss share < 50%) | Yes | Yes, weakly — a share can move for reasons other than the repair | No |
| C2's "sanity check" (8-case means reproduce the published overall) | Barely | — | **YES — see §3.2** |

## 2.4 §2b compliance, checked rather than assumed

The reinversion's Amendment 1 fixed λ_QoI numerically **after** stage A's 1.73 core-min
re-baseline had run. Under §2b as written today, gates close at first compute. **My
reading is that this is compliant, and I state the reasoning so a grader can attack it:**
the *shape* of both gates was frozen in §6 before any compute, including the conditional
rule for the window (*"if the repaired baseline's error concentrates elsewhere… the
window is re-stated there WITH the audit numbers"*). Executing a pre-frozen decision rule
on data is not tuning; only changing the rule after seeing the data would be. λ_QoI is a
normalisation that makes G1 mean "reduce the loss by 30%", which is what §6 said before
any number existed. **Also noted: §2b was added 2026-08-11 and the run is 2026-08-07/08,
so this is a retrospective reading of a clause that did not exist at run time.**

## 2.5 What remains before Stage 1 is publishable rather than runnable

**This is the honest gap, and it is not small.**

1. **Stage 1 has no external referent.** Every verdict in the S1 line is checked against
   the lab's own fields, the lab's own baseline, and the lab's own bars. The FD tables
   check the adjoint against finite differences **of the same primal solver** — the audit
   at `docs/EXTERNAL_REFERENT_AUDIT.md` §5.2 already classifies that pattern as
   SELF-REFERENTIAL. There is no published β field, no independent implementation, and no
   benchmark distribution anywhere in the chain. **Under §6a the correct sentence is: S1
   is verified in depth and validated against nothing external.**
2. **The term mismatch blocks the one comparison that would supply a referent.**
   Wu/Zhang's numbers are destruction-term; ours are production-term.
   `w3-beta-on-omega-destruction-model-patch` is the named unblock and has not run.
3. **Both G2 verdicts on the record rest on a gate this document shows is invalid.** They
   stand as recorded failures (§2b forbids repairing them), but any publication reciting
   "G2 failed" as evidence about the physics would be reciting an artefact. **The
   publishable localisation claim is gate A's 99.6%, not G2's 26.9%.**
4. **G1 was budget-capped while still descending**, and G1w is recorded UNRESOLVABLE as
   posed after the seventh fleet kill destroyed the L-BFGS-B curvature state. Neither is
   a converged optimum.
5. **Stage 2 has not run and is held**, with a named unblock: the S1-with-priors redesign.

---

# 3. C2 error decomposition — what it decomposes, and its external referent

## 3.1 What it decomposes, verified

`closure_challenge_C2_error_decomposition.md` decomposes the round-2 entry's 8-case score
two ways: against the RANS identity floor (where the correction helps and hurts), and —
in its addendum — against the public leaderboard (where the lab's deficit to rank 2
lives).

**I recomputed every load-bearing number in it from
`closure_challenge_trained_entry_round2.json` with my own implementation.** All reproduce:

| C2 claim | recomputed | verdict |
| --- | --- | --- |
| floor mean 0.1036 | 0.103637 | ✓ |
| entry mean 0.0741 | 0.074063 | ✓ |
| damage on 3 degraded cases = 0.0528 summed, 0.0066 on the mean | 0.0528 / 0.006600 | ✓ |
| withheld-where-it-hurts score 0.0675 | 0.067462 | ✓ |
| recoverable term = 1.7x the margin over rank 4 | 1.72x | ✓ |
| alpha_05 = 98% of the damage | 97.9% | ✓ |
| Pearson r(floor, delta) = −0.9418 on n=5 | **−0.9418** | ✓ |
| gap to rank 2 = +0.0117 | +0.0117 | ✓ |
| AR_1 31.5%, AR_3 31.4%, together 62.9% | 31.5% / 31.4% | ✓ |

**One labelling defect found.** The header reads *"Decomposing the +0.0117 gap to rank
2"*, but the shares are of the **gross positive gap** (0.1475 summed, 0.0184 on the mean),
not of the net +0.0117 — three cases where the lab beats rank 2 offset it by 0.0068. The
conclusion is unaffected and is if anything understated: against the **net** deficit,
AR_1 and AR_3 alone are ~99%. **Filed, not edited** — C2 is another owner's document and
its supersession discipline is intact.

## 3.2 The "sanity check" is an identity — §2a applies

C2's opening reads:

> **Sanity check passed first:** recomputing the 8-case means from the per-case values
> reproduces the published overall figures exactly… **The decomposition is therefore
> trustworthy.**

The benchmark's own scorer is `closure_challenge/eval.py:17` —
`return np.mean(list(scores.values()))`. **The overall is an unweighted mean of the
per-case values by construction.** Recomputing it from those same values is therefore
derivable from its own inputs: an **IDENTITY under §2a**, reportable, never gateable. It
can fail only on a transcription error or a non-mean aggregation, and it is worth
reporting for exactly that. **What it cannot do is support the sentence that follows it.**
"Therefore trustworthy" is L-74 verbatim: a check written against the same data as the
thing checked, read as though it established correctness.

**My own recomputation in §3.1 is a step better — an independent implementation — and
still not external.** It reads the same JSON. It proves the arithmetic, not the scores.

## 3.3 The external referent — C2 has one, in part, and it is verified

**Under §6a, C2's verdicts split cleanly and must be labelled separately:**

**§1–§5 of C2 (floor-relative decomposition): SELF-REFERENTIAL.** Both the floor and the
entry come from the lab's own single scoring call. The check is arithmetic on that call's
own output.

**The addendum (leaderboard-relative decomposition): EXTERNAL, and I verified it.**
`/home/ubuntu/closure-challenge-benchmark/README.md:6-9` carries the published
leaderboard. Wu & Zhang's per-case row is
`0.0813 | 0.1195 | 0.0569 | 0.0848 | 0.0455 | 0.0399 | 0.035 | 0.0364` — **byte-for-byte
what C2 tabulates**, and their published overall 0.0624 reproduces from it (0.062412). I
independently confirmed all eight "best on board" entries as the column minima across the
four ranked rows, and confirmed the claim that the lab holds the board best on three of
eight cases. **This is a published value from the benchmark's own repository. It is a
genuine external referent and C2's central conclusion — that AR_1 and AR_3 carry the
deficit — rests on it.**

**One boundary that must travel with that label:** the leaderboard is external for
*competitors'* scores. The lab's own 0.0741 is its own scoring call through the
benchmark's unmodified scorer against the benchmark's shipped ground truth — **externally
defined, locally executed, and unaudited by the organisers.** It is not a leaderboard
placement and the lab's records say so.

**A staleness caveat C2 does not carry.** The local clone is at `deb9155` (2026-05-04);
the live leaderboard at 2026-08-05 has **six rows, not four**, with a new rank 1 (Yang,
0.0580) and a new rank 4 (Tian, Buchanan, Hickel, Dwight, 0.0641). **C2's addendum is a
correctly-anchored external verification of a snapshot that has since moved.** Under W-5
this is exactly the rot a commit anchor prevents: C2 anchors the harness commit but the
leaderboard rows are undated in the table itself.

## 3.4 C2 and the External Referent Audit

**C2 is not in `docs/EXTERNAL_REFERENT_AUDIT.md`.** Positive control for that negative:
the same `/usr/bin/grep` over the same file returns 10 hits for `SELF-REFERENTIAL`, so
the method finds what is there; `C2`, `closure_challenge_C2` and `error decomposition`
return nothing. C2 falls in the audit's own named frontier — §8 item 1, the ~950
screened-UNDECLARED sections below travel-rank ~26, *"unadjudicated, not cleared"*.
**§3.2 and §3.3 above are that adjudication.**

## 3.5 C2's recommendation was executed — and audited for the leakage it warned about

C2 warned that per-case selection on test scores would be leakage, and specified the
legitimate route: a trust criterion built on training and validation cases only. That
route was built. `closure_challenge_generalization_criterion.json` fits it on probe cases
with `official_test_cases_touched: false` and
`closure_challenge_score_call_made: false`; `closure_challenge_decline_gate_audit.json`
records `official_scoring_calls_made_by_this_script: 0` and verifies that the declined
cases ship the benchmark's own supplied SST field (residual ~5e-10, the CSV write
precision) while the applied cases deviate by ~12% of local velocity scale — **a
discriminating positive control on the audit itself.** By round 5 the entry of record is
0.056647. **C2's diagnosis drove the work and the leakage discipline it demanded held.**

---

# 4. Submission policy — what the published rules say, and the five that do not exist

**PARKED, and nothing was done.** No registration, no email, no issue, no upload, no
contact of any kind. This is research *about* sending. Every send remains Katie's.

**The benchmark, identified:** The Closure Challenge,
`github.com/rmcconke/closure-challenge-benchmark`, steward Ryley McConkey (MIT).
Preprint arXiv:2603.28884 (McConkey, Buchanan, Smidt, Bodner, Dwight, Cinnella),
fetched and verified real. `rmcconke/ml-turbulence-benchmark` 301-redirects to it — same
repo, old name.

| # | Point | Finding | Status |
| --- | --- | --- | --- |
| 1 | Registration | **None required** for the ongoing benchmark | VERIFIED (negative, control passed) |
| 1b | Registration, workshop round | Existed for the ERCOFTAC ML4Fluids round; **lapsed** | VERIFIED |
| 2 | Attribution | Email the `test` subdirectory plus *"a list of all authors, and any relevant references"* | VERIFIED — README:101 |
| 3 | Entries per team | No limit stated — **and no statement that multiple are allowed** | **SOURCE UNAVAILABLE** |
| 4 | Corrected resubmission | No published policy; tolerated in practice (open PR #3; steward re-scored all entries in place at `44540c8f`) | **SOURCE UNAVAILABLE as a rule** |
| 5 | Training-data disclosure | Minimal and informal; steward asks *"which cases were in your train/val/test datasets?"* unprompted by any written rule. **Hyperparameter disclosure: no requirement anywhere** | VERIFIED (minimal) / SOURCE UNAVAILABLE (hyperparameters) |
| 6 | Licensing of submissions | **No license exists.** GitHub API returns `license: null` for both repos; accepted submissions are committed into that public unlicensed repo | VERIFIED (absence) / SOURCE UNAVAILABLE (terms) |
| 7 | Leakage | *"It is **strictly forbidden** to train or validate on any data from the **test cases**… your submission will be automatically withdrawn"* | VERIFIED — README:63-65, arXiv §2.1, eval README:113 |
| 8 | Deadline | *"Submissions are accepted anytime!"* — ongoing, not tied to any event | VERIFIED — README:13, 23 |

**The single most decision-relevant finding.** The eval package **ships
`ground_truth_test.npz`** and the README *instructs* previewing your score with it.
**There is no limit on scoring calls and there cannot be one.** The lab's "four official
scoring calls, ever" *(as this round-3-era finding was written; the cumulative count is
six after round 5's 2026-08-07 call -- the ledger stood at six as of frame `c143d4c0`)*
is **self-imposed discipline, not compliance** — which
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:169-172` already states correctly. The lab has
been holding itself to a stricter standard than the organisers impose. That is a
defensible choice and it should be named as a choice.

**Positive controls, all passed.** The same `/usr/bin/grep -ic` over the live README
found `strictly forbidden`→1, `anytime`→1, `authors`→2 while `registration`,
`deadline`, `resubmi`, `license`, `per team`, `scoring call` all →0. The same method over
the fetched arXiv full text found `only strict rule`→1, `CC BY 4.0`→1 with the same terms
at 0. The `license: null` API call returns `spdx_id: MIT` on a control repository.
**The zeros are real absences, not broken searches.**

**A trap worth naming.** The ERCOFTAC ML4Fluids 2026 page states *"To participate: Send
an expression of interest to…"* and *"January 2026: Initial submissions due"*. **That
governed the workshop-synchronised round, which has passed.** arXiv §4 reconciles it:
*"this is a continuously running benchmark, not associated with any event."* Nobody
should cite that page as a live requirement.

**What cannot be established from open sources — say this plainly, before any send is
contemplated:**

1. How many entries a team may make.
2. Whether a corrected resubmission is permitted after scoring.
3. Whether hyperparameter tuning must be disclosed.
4. What licence submitted predictions and code fall under.
5. Whether a company, rather than named individuals, may occupy the "Authors" row.

**All five are steward questions, not document questions.** The README invites exactly
that (line 27, "please open an issue in this repo"). **Asking is an external interaction
and is Katie's alone.** It was not done.

**One stale belief corrected.** `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:188` reasons over
*"all four current rows"*. There are six, and the rank-1 target has moved from 0.0595 to
0.0580. **The round-5 entry of record at 0.056647 is still below it** — but the rank-1
campaign's target number is out of date and any rank claim must be re-anchored before it
travels. Note also that the new rank-4 entry includes Tyler Buchanan, a challenge
co-author.

---

# 5. Priced compute requests

**Nothing below was run. Compute authorisation is Katie's.**

| # | Request | Cost | What it settles |
| --- | --- | --- | --- |
| 1 | **None required for the G2 question.** | **0** | Already settled — §1, entirely on written fields |
| 2 | W1-only arm (loss support ≡ G2's window, term-for-term) | ~150 core-min | Whether matching loss support to metric support closes G2. **Recommendation: still NO-GO.** §1.5 shows the answer would be uninterpretable — a window-only loss makes the deviating set ≈ the window ≈ 8.44% < a decile, landing squarely in the threshold degeneracy. **It would score 8.4% and FAIL by construction.** This is a new reason to decline it, and it is arithmetic, not judgement |
| 3 | `w3-beta-on-omega-destruction-model-patch` | not priced here (patched + rebuilt turbulence model) | The **only** route to an external referent for the S1 line: term-parity with Wu/Zhang's published inversion |
| 4 | `beta_final_ext` field write-out | ~8.5 core-min | Nothing currently — chief already ruled SKIP until a consumer exists. **I did not need it** |
| 5 | Sparse-point separation-region loss (Wu/Zhang's own) | needs its own FD gate first | Removes the free-channel term both G2 verdicts foundered on. Lower priority now: §1 shows the G2 verdicts were the metric's fault, not the loss's |

---

# 6. Filed to the docket

Three findings, appended as **D29–D31** at commit `281a6dc9` (IDs append-only per W-4;
D28 was highest).

- **D29** — a quantile-based spatial gate inverts when the deviating support is smaller
  than the quantile. The general form, beyond G2. Owner: fleet.
- **D30** — the scoring-call budget is lab discipline, not benchmark compliance, and
  should be recited as a choice. Owner: fleet.
- **D31** — the five submission rules that do not exist in any open source. **Owner:
  Katie**, because settling them means contacting the steward, which is hers.

Not filed to the docket, because they belong to their own documents' owners and are
recorded here instead: the C2 gross-vs-net share labelling (§3.1), the 15-vs-16
evaluation-count disagreement and the loose use of "bulk" for a face-value mean (§2.2),
the stale 229.07 header in the weighted-arm record (§2.2), and the uncaptured
`audit_final.py` stdout (§1.1).

---

# 7. Referent labels for this document's own verdicts (§6a)

- §1 (G2 is invalid): **EXTERNAL to the gate under test** — the gate is falsified by
  synthetic fields and by an amputation the lab itself constructed, not by re-running the
  gate's own helpers. The negative control (noise → base rate) demonstrates the
  instrument can return the null.
- §2 (S1 numbers): **SELF-REFERENTIAL** — independent implementation, same fields.
- §3.1 (C2 arithmetic): **SELF-REFERENTIAL** — independent implementation, same JSON.
- §3.3 (leaderboard): **EXTERNAL** — the benchmark repository's own published table.
- §4 (submission rules): **EXTERNAL** — fetched primary sources, quoted, with positive
  controls; five points explicitly SOURCE UNAVAILABLE.
