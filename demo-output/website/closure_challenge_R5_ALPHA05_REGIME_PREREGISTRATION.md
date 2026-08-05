# R5 pre-registration — the alpha_05-regime model: what would be scored, the accept/reject criterion, and the pre-declared gate it failed

**Written 2026-08-04 (UTC), after training and held-out validation, and before
any scoring call — which this document concludes must NOT be made.** This is
the pre-registration C2's "Recommended next action" asked for, and its verdict
is the negative branch: the candidate exists, its validation evidence is
strong on average, and it fails the hurt-cap rule that was fixed in the
committed training script before any correction delta existed. **Round 4
(0.0654) remains the entry of record. No new prediction set is scored.**

Evidence record: `closure_challenge_alpha05_regime_model.json` (this
directory), produced by `sdk/scripts/train_closure_alpha05_regime_model.py`.
Cost: 62 s wall at a 2-core cap — ~2 core-min. In-sample gate
(`sdk/scripts/closure_in_sample_gate.py`): PASS before and after this work; no
test-case file was opened (the script wraps `open()` to raise on any test-case
path, and the guard was armed before the first field was read).

---

## 1. The premise, checked against the record first

C2 recommended: *if the training split contains alpha_05-regime cases, train a
second regime-specific model on them — strictly better than gating, because it
recovers the term instead of merely declining to lose it.*

**The naming premise is wrong and C2's own addendum already said so.** The
training split contains five alpha_05-named cases, the round-1 model trained
on them, and it still hurt alpha_05 at test; NASA_2DWMH is in the same
degraded group without being a hill. The framing that survives C2 is baseline
quality: **the correction hurts where raw RANS is already good.** So "the
alpha_05 regime" is defined here the only test-blind way it can be — by the
same frozen C1 gate that makes the test-time decision:

> a case is in-regime iff the C1 top-3 gate (p90_I4_W2S, frac_backflow,
> p90_I3_S3; Ridge alpha 0.7499) predicts baseline scaled-MAE ≤ 0.1263 (the
> train-LOO-median threshold).

The gate refit in this run reproduces C1/round-3 exactly (alpha 0.7499,
threshold 0.1263) — checked before membership was computed, and the script
exits rather than defining membership from a drifted gate.

**Qualifying training cases exist: 11 of 21.** By gate LOO prediction
(variant A): all five alpha_05 cases, alpha_075, and five alpha_10 cases. By
actual baseline error (variant B): the same set minus alpha_10_9000_2024
(gate-underpredicted; actual baseline 0.1799) plus alpha_10_12000_4048. One
validation case is gate-declined and therefore in-regime:
alpha_05_10071_4048 (gate 0.0723 ≤ 0.1263) — the same branch the two alpha_05
test cases took at rounds 3/4. Both variants were trained (round-1
architecture and hyperparameters unchanged, nothing tuned) because the
membership rules disagree on 2 of 21 cases and neither is obviously right:
A matches the deployment feature distribution, B matches the mechanism (learn
small corrections from cases that only need small corrections).

## 2. What would be scored — fixed here so the event is defined even though it will not run

The round-5 prediction set is the round-4 entry of record with **exactly two
cases changed**: the gate-declined PH test cases alpha_05_4071_4048 and
alpha_05_4071_2024 replace their raw-RANS floor predictions with the selected
regime model's corrected field (features only at inference; interpolated to
the evaluation points exactly as rounds 1–4). The other six predictions stay
byte-identical to round 4, verified by the same SHA-256 manifest discipline
round 4 used. It would be the 6th distinct prediction set this lab has ever
scored on this benchmark, in a single call.

**Accept/reject at scoring, fixed now:** ACCEPT iff round5_overall <
round4_overall (0.0654) — equivalently, the summed delta on the two changed
cases is negative. Per-case floors (0.0461, 0.0719) reported alongside. If
either case degrades and the sum still improves, that is reported as written;
if the sum degrades, the regime model is recorded as a validated-then-failed
candidate and round 4 stands. No re-grade, no per-case cherry-pick after the
call — choosing per case *after seeing test scores* is the leakage this line
has refused three times already.

**Stakes, stated honestly:** the decline branch already banked C2's 0.0066
"avoid the loss" term at round 3, and the round-4 floor values are already
best-on-board on both alpha_05 cases. R5 could only convert "decline" into
"win beyond best-on-board" — worth at most a few thousandths on the mean. The
deficit to rank 2 lives in the ducts and NASA, not here.

## 3. The selection and GO/NO-GO rules, and where they were when the numbers arrived

Declared in the training script's docstring before any LOO delta existed
(the script is committed as written; stated plainly: it was committed in this
same session, not in an earlier one — the chronology inside the run is
enforced by the script itself, which computes memberships and rules before
deltas):

- Comparison set: the 10 cases in both memberships, each under its
  leave-one-case-out model, plus the held-out in-regime validation case.
- Select the variant with the lower mean LOO delta (corrected − baseline).
- **GO iff** the selected variant (i) improves the validation case, (ii) has
  mean LOO delta < 0, and (iii) **hurts no comparison-set case by more than
  +0.010**.

**Added 2026-08-05 — the rule has a name, and our version of it is the weaker
one.** Per the method-priority review (`CLOSURE_METHOD_PRIORITY_REVIEW.md`
§2.4 and §7, commit `d84b649f`): "adopt the retrained model only if it is
certified not to be worse than the incumbent" is a named research problem —
**Thomas, Theocharous & Ghavamzadeh**, *High Confidence Policy Improvement*,
**Proc. 32nd ICML, PMLR 37 (2015) 2380–2388**. **[ABSTRACT READ 2026-08-05**
from the PMLR record.**]** Verbatim: their algorithm "provides probabilistic
guarantees about the quality of each policy that it proposes, and ... has no
hyper-parameter that requires expert tuning. Specifically, the user may select
any performance lower-bound and confidence level". Three comparisons, and two
of them cut against us:

1. **Against us, and it is the point of citing them: our +0.010 is
   hand-chosen and this document never says why.** Rule (iii) was declared
   before any correction delta existed — that is the part that matters for
   leakage and it is unchanged — but *0.010* has no derivation anywhere in
   our record, where Thomas et al. parameterise the bound by a stated
   performance floor and confidence level. This fires
   `docs/charters/LITERATURE_CHARTER.md` §6 trigger 2 (a method whose
   admissibility could be written as thresholds), and the fix is owned by a
   filed proposal, not by an edit here:
   `agenda/proposals/w8-a-hurt-cap-that-states-where-it-came-from.json`.
2. **Against us, in the framing**: clinical trials pre-specify a
   **non-inferiority margin** in the protocol precisely so it cannot be chosen
   after the data. Our per-case hurt cap is that idea under another name.
   Saying so is more honest and more legible than presenting it as bespoke.
3. **For us**: their guarantee is about the *aggregate*; ours binds *per case*,
   which is stricter — and it is the reason §4 records a NO-GO on one case
   while eight of ten improved.

## 4. The measurements

Selected: **variant B** (mean LOO delta −0.0195 vs A's −0.0172).

| Rule | Measured | Verdict |
| --- | --- | --- |
| (i) validation case improves | alpha_05_10071_4048: 0.0759 → **0.0447** (−0.0312; the global round-1 model gives 0.0772, a HURT) | **PASS** |
| (ii) mean LOO delta < 0 | **−0.0195** over 10 cases (8 of 10 improved, two by > 0.035) | **PASS** |
| (iii) no LOO case hurt by > +0.010 | alpha_05_4071_3036: 0.0492 → 0.0659, **+0.0167** (variant A: +0.0159) | **FAIL** |

**Verdict: NO-GO.** The rules are not revisited after the numbers; the scoring
call defined in §2 is not authorized by this document, and nothing in this
session scored anything.

## 5. Why the failing case is the one that decides — the finding

The case the regime model still hurts is **alpha_05_4071_3036 — the training
sibling of both test cases** (same alpha_05, same 4071 parameter, differing
only in the third index; the test pair is alpha_05_4071_4048 and
alpha_05_4071_2024). It is also the lowest-baseline case in the entire
training split (0.0492), sitting next to the test pair's floors (0.0461,
0.0719). The LOO table splits cleanly on baseline: every case with baseline
≥ 0.058 improves, both cases below ~0.055 get worse (+0.0167 at 0.0492,
+0.0073 at 0.0548) — in both variants.

**C2's mechanism is recursive.** Train only on the low-baseline regime and the
hurt-where-RANS-is-already-good boundary does not disappear — it moves down
(from ~0.07–0.13 to ~0.055) and reappears inside the regime. A correction
model fitted to a population still damages the best-baseline members of that
population. Extrapolating to the test pair: the regime model would plausibly
help alpha_05_4071_2024 (floor 0.0719, the helped range) and hurt
alpha_05_4071_4048 (floor 0.0461, below the recursive boundary and the
sibling of the case it measurably damages) — the net sign is unknowable
without the scoring call, and the pre-declared gate says the call is not
earned.

## 6. What a successor candidate would need (not claimed, not started)

A second-stage test-blind threshold — decline even the regime model where the
gate predicts baseline below ~0.055 — is the obvious next candidate, and on
the current gate predictions it would submit the regime correction on
alpha_05_4071_2024-like cases while keeping the floor elsewhere. **It is not
adopted here**, because it was conceived after these LOO numbers existed;
adopting it now would be exactly the rules-revisited-after-the-fact move this
document's own §3 forbids. It would need its own membership audit, its own
held-out design (the n=1 in-regime validation set is the binding weakness —
only one validation case falls below the threshold, so any second-stage rule
leans entirely on LOO evidence), and its own pre-registration before any
scoring call. Filed as the recommendation, nothing more.

*Nothing above was altered after the GO/NO-GO verdict was computed; the
verdict and every number in §4 trace to
`closure_challenge_alpha05_regime_model.json`.*
