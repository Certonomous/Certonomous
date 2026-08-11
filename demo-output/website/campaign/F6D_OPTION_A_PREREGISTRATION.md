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

## 6.1 Deviation record — a two-runner collision on a control, 2026-08-11

**Recorded here rather than in a report, because a deviation belongs with the
pre-registration it deviates from. The cause was mine.**

**What happened.** The solver agent launched 8 of the 16 cases and queued the
other 8, then its turn ended — its queue died with it while the solves, launched
under `setsid`, survived. I started an independent `run_option_a_queue.sh` to
launch the remaining 8. My runner guards against collisions (it skips any case
that already has a `log.simpleFoam`); **the agent's pool did not**, and my
instruction to it not to launch those cases arrived after its pool had already
fired. For roughly 25 seconds, two `simpleFoam` processes shared
`f6d_option_a/d0.2_s000` — **one of the three controls.** The agent killed the
newer duplicate and its own driver. **I created the race by starting a second
launcher over cases another agent had already claimed; the correct order was to
stop its queue first and confirm, then launch.**

**Damage, measured independently rather than accepted on report:**

| check | result |
| --- | --- |
| live duplicate processes now | **none** — mapped every `simpleFoam` by `/proc/<pid>/cwd`; all 16 cases have exactly one solver |
| write ladder on `d0.2_s000` | **clean and monotonic** — 4500, 5000, … at a steady 35–40 s cadence, no out-of-order write, no rewrite. The duplicate died at Time ≈ 4265, *before* the first write at 4500 |
| field data | **intact**, single-writer throughout |
| log | **damaged** — a `>` redirect truncated it while the surviving process kept writing at its old offset, leaving ~1.9 MB of NULs. Iterations **4000–7000 are unrecoverable as text** |

**Effect on the pre-registered metrics: none that changes a verdict.** All three
metrics read the **end** of the run — reattachment from field snapshots (intact),
the primary value from the final 2,000 iterations (intact), settledness from the
final 500 (intact). The only exposure is that settledness normalises by the
median |pg| over the *second half*, whose window shifts when the first 3,001
iterations are missing. **Bounded by direct measurement:** recomputing every
intact log with its first 3,001 iterations deliberately discarded moves
settledness by **at most 13.7 %**, and by **0.1 %** for this case.

**Disposition: the control is RETAINED, with this disclosure.** It is not void —
no metric it contributes to is computed from the lost window. **A clean rerun of
`d0.2_s000` from its intact `4000/` fields costs ≈ 10 core-min** and is available
if its owners want the log whole; it was not taken here because it would discard
a nearly complete run to repair text that no pre-registered metric reads.

**Standing rule this earns, and it is the second time the same root cause has
bitten this experiment:** *agent watchers die, so a launcher must be durable —
but two durable launchers over one case set are worse than none.* Any
replacement launcher must (a) guard every launch on the absence of a log, which
mine did, **and** (b) be started only after the previous launcher is confirmed
dead, which I did not do.

## 6.2 The validity gate fired, and my gate was mis-specified — escalated, NOT amended

**Interim, 2026-08-11, with 10 of 16 finished. Recorded now because it must not
look like it was written after the verdict.**

The pre-registered gate has **fired VOID**: control `d0.2_s000` moved
**−0.831 x/h**, far beyond the 0.25 threshold. Reported plainly because it is
inconvenient.

**But the gate's stated inference is falsified by its own siblings.** The gate
says a control moving > 0.25 means *"the continuation has introduced a restart
transient of its own."* A restart transient is **common-mode** — it would move
every control. Measured:

| control | max excursion over the continuation | reading |
| --- | --- | --- |
| `null` (unperturbed) | **+0.049** | flat |
| `d0.2_s027` | **±0.064** | flat |
| `d0.2_s000` | **−1.337 and oscillating** (6.337 → 5.84, 5.34, 5.85, 5.00) | diverging |

**Two of three controls are rock-solid, so the restart is clean and the
mechanism the gate exists to detect is excluded by measurement.**
`d0.2_s000`'s movement is a real physical drift, not an experimental artifact —
and it cannot be the collision either, because the collision damaged only that
case's *log*, while reattachment is read from *fields*, which were verified
intact and single-writer in §6.1.

**So my gate was mis-specified, and I am saying so rather than quietly fixing
it.** It inferred a common-mode cause from a single-control observation. A
correctly specified gate would have voided on the *unperturbed* control moving,
or on all three moving together. Rewriting it now, after seeing which way it
fell, is exactly the sin a pre-registration exists to prevent, so **the gate
stands as written and the decision is escalated** to the chief and the F6d
owners:

- **Reading A — the gate as written.** The experiment is VOID. No verdict on
  the 13. Cost of redoing it with a corrected gate: the runs already exist, so
  this is a re-reading, not a re-run.
- **Reading B — the gate's stated purpose.** Its premise is measurably false;
  `null` and `d0.2_s027` establish a clean restart; the experiment is valid and
  `d0.2_s000` is reclassified from control to **finding**.

**I am not choosing between them.** What I will report either way is the
measurement, because it is the same under both.

**And the measurement is the point.** `d0.2_s000` was chosen as a control
*because it was among the best-settled members of all 84* (published swing
0.038, second only to `null`). Continued, it destabilises: settledness 0.401 and
a reattachment wandering by more than 1.3 x/h. **A member that looked settled at
4,000 iterations was passing through a quiet phase of an unsteady flow, not
sitting at a steady solution.** That is direct evidence for the pre-registered
**Outcome 3**, and it is stronger for having come from a case picked to be
well-behaved. Meanwhile `null` — the only *unperturbed* run — is the sole case
that is genuinely settled (0.053).

Provisional and not a verdict: 6 cases are still running, and **no member of the
13 has settled**, several having now passed 12,000–16,000 iterations.

## 7. Standing constraints

Read-only with respect to everything outside `f6d_option_a/` and this campaign
directory. The published `ens/` tree is not modified. Nothing is sent anywhere.
The result document will be a separate file and will cite this pre-registration
by commit hash.
