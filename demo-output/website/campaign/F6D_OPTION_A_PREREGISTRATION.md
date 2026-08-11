# F6d Option A — pre-registration

**Written and committed BEFORE any compute.** Approved by the chief on
2026-08-11 following `F6D_ENSEMBLE_CONVERGENCE_AUDIT.md`. No member of this
experiment had been launched when this file was committed; the commit hash of
this document precedes the commit hash of any result derived from it, and that
ordering is the point.

---

## 1. The one question

The audit found that across the F6d ensemble, **reattachment tracks how
unsettled a member is** — most-settled quartile mean 7.21, least-settled 5.25,
against a baseline of 7.64 and an LES truth of 4.6–4.7 — and that **the members
carrying the ensemble's agreement with the LES truth are the least settled in
it**. Two explanations survive that observation and the audit could not separate
them on existing data:

- **ARTIFACT** — being unconverged moves a member toward shorter reattachment,
  so the agreement is a transient, and it will disappear as the member settles.
- **PHYSICS** — a genuinely stronger stress perturbation *both* shortens
  reattachment *and* makes the case harder to converge, so the agreement is
  real and the correlation is a common cause.

**Option A continues the members that carry the agreement and watches which
happens.** Nothing else in this experiment is a deliverable.

---

## 2. Frame and members, fixed now

**Continued members — the 13 that carry the LES coverage** (every member whose
published reattachment is at or below the LES upper bound of 4.7):

| group | members |
| --- | --- |
| δ = 0.2 (6) | `s015`, `s019`, `s020`, `s022`, `s023`, `s036` |
| δ = 0.6 (7) | `s000`, `s007`, `s011`, `s021`, `s022`, `s035`, `s039` |

**Controls — declared as part of the experiment, not as an extra.** A
continuation can introduce its *own* restart transient, and if it does, every
number above is unreadable. These exist to detect that:

| control | n | what it must do for the experiment to be valid |
| --- | --- | --- |
| `null` (settled, `R_sample = R_bar`) | 1 | **must not move.** It is already settled to 0.0008 and sits on the baseline. |
| best-settled members `d0.2_s000`, `d0.2_s027` | 2 | **must not move.** Settled to 0.038 / 0.054, reattachment well away from LES. |

**Validity gate, declared in advance: if any of the three controls moves its
reattachment by more than 0.25 x/h, the continuation has introduced a restart
transient of its own, the experiment is VOID, and no conclusion is drawn from
the 13.** This is the negative control, and it can fail.

**Preservation.** The published run tree is **not** touched. Every case is
copied to `f6d_option_a/<case>/` and restarted there from its own `4000/`
fields. The original `ens/` directories remain exactly as published, so the
audit and the record stay reproducible.

**Deliberately NOT changed:** `residualControl { p 1e-15; }` stays. This is a
diagnostic and we want the full trajectory, not an early stop. Changing it would
also make the continuation a different case from the one being diagnosed.

**Changed, and only this:** `endTime 4000 → 16000` (+12,000 iterations), and
`writeInterval 4000 → 500`. **The second change is the one that matters** — the
original defect that made this question unanswerable was that `writeInterval`
equalled `endTime`, so only one snapshot existed and the QoI could never be
trended. This experiment writes 24 of them.

---

## 3. Metrics, defined before the data exists

1. **Reattachment** `x/h`, by the *unmodified* `analyse.analyse_case`, at each
   written snapshot. The published value at 4,000 is the baseline for each
   member. Primary reported value is the **mean over the final 2,000
   iterations** of snapshots, which is defined whether or not the member settles.
2. **Settledness** = peak-to-peak swing of the `meanVelocityForce` pressure
   gradient over the final 500 iterations, normalised by the median |pg| over
   the second half of the continuation. Same instrument as the audit, unchanged.
3. **Δreattachment** = (primary reported value) − (published value at 4,000).

**Settled** means settledness < 0.10. **Moved** means |Δreattachment| ≥ 1.0.
**Held** means |Δreattachment| < 0.5. The band 0.5–1.0 is declared **ambiguous**
now, so it cannot be argued into a verdict later.

---

## 4. The three outcomes, all three writable before the start

Each of the 13 is classified independently; the verdict is by **majority of the
13**, and the counts are reported whatever they are.

### Outcome 1 — ARTIFACT
**Predicted signature:** the members settle (settledness < 0.10) **and**
reattachment **moves toward the baseline** — Δreattachment ≥ +1.0 for the
majority, and the count of members at or below 4.7 falls from 13 toward 0.

**Then:** the agreement with LES was a transient. Claims 8, 11, 12 and 13 of the
audit stay INVALID and become *settled* rather than *suspected*. The δ = 0.2
coverage claim is withdrawn outright. F6d's headline — that gating discards the
members nearest the truth — is confirmed as a convergence artifact, and the
`W2` §4.3 rule and proposal gate G3 must be amended, not merely annotated.

### Outcome 2 — PHYSICS
**Predicted signature:** the members settle (settledness < 0.10) **and hold
position** — |Δreattachment| < 0.5 for the majority, with the count at or below
4.7 substantially preserved.

**Then:** the audit's §3 correlation had a common cause, and the competing
reading the audit refused to exclude is the right one. Claims 8, 11, 12 and 13
are **recoverable** and are restored with a convergence caveat naming the
iteration count at which each member settled. F6d's original reading of the
gating bias stands, and the `W2`/G3 rules need only the settledness gate added,
not reversal. **The audit's central finding would be wrong in its implication,
and this document says so in advance.**

### Outcome 3 — NO STEADY SOLUTION EXISTS
**This is the outcome nobody will want to find, and it is as writable as the
other two.**

**Predicted signature:** the members **do not settle even at 16,000
iterations** — settledness stays above 0.5 for the majority, and/or the driving
pressure gradient keeps reversing sign — while the three controls remain settled
(proving it is the perturbation and not the continuation).

**Then:** the perturbed cases have **no steady solution to converge to**, and
this is the strongest of the three findings even though it retracts the most.
No `residualControl` target and no iteration cap will ever produce one; a fixed
cap simply samples an arbitrary phase of a limit cycle, which is exactly what
the published band did. **A steady RANS ensemble was the wrong instrument for
this question**, the band is not recoverable at any price, and Option C (the
25.7 core-hour clean re-run) must **not** be funded, because it would buy 80
more arbitrary phases. The honest instrument becomes a time-averaged unsteady
statistic, and the correct next step is to price that rather than to re-run
this. Under this outcome the ensemble's *relative* claims (audit rows 9, 10)
also fall, because a phase average is not a member.

### Mixed result
If the 13 split without a majority, **no aggregate verdict is declared.** The
per-member classification is published with its counts, and the question is
reported as unresolved at this budget. This bucket exists so that a split cannot
be narrated into whichever outcome is most convenient.

---

## 5. Cost, and an honest deviation from the approved figure

| item | members | iterations | core-min |
| --- | --- | --- | --- |
| the 13 coverage-carrying members | 13 | +12,000 | **152** |
| controls (`null`, `d0.2_s000`, `d0.2_s027`) | 3 | +12,000 | **26** |
| **total** | **16** | | **≈ 178** |

**The chief approved 152 core-min; this asks for ≈ 178.** The 26 core-min
difference is the three controls, and it is requested rather than assumed. The
reason is the audit's own doctrine: a continuation that moves every member —
including ones that were already settled — would look exactly like Outcome 1
while actually being a restart artifact, and without the controls that failure
is undetectable. **If the extra 26 core-min is refused, the correct response is
to run the controls and drop three of the 13, not to run 13 without controls.**

Rates are this ensemble's own measured ones (`cost.json`: 194 s/member/4,000
iterations at δ = 0.2, 269 s at δ = 0.6, 135 s for `null`, serial, 1 core).

---

## 6. What would falsify this experiment itself

- **Any control moving > 0.25 x/h** → VOID (§2). Reported as such, no verdict.
- **A member failing to restart cleanly** (missing `4000/` fields, crash in the
  first 100 iterations) → that member is reported as a failure with its mode and
  is excluded from the majority count, with the reduced denominator stated.
- **`analyse.analyse_case` returning no reversed-flow region** at a snapshot →
  recorded, not silently dropped; the member's trace is reported as fragmented.

---

## 7. Standing constraints

Read-only with respect to everything outside `f6d_option_a/` and this campaign
directory. The published `ens/` tree is not modified. Nothing is sent anywhere.
The result document will be a separate file and will cite this pre-registration
by commit hash.
