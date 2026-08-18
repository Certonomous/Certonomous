# F5c — isolating the algorithm lever from relaxation: results

Pre-registration: `F5C_LEVER_ISOLATION_PREREGISTRATION.md`, commit **`9eaefc7f`**,
committed before the run existed. Chief-approved at ≈2.4 core-min. Record:
`F5c_runs/a4_record.json`; case archived at `F5c_runs/stage_a_A4/`.

---

## 1. The verdict

> ### **O-I2 — relaxation is attributable, the algorithm is not.**
> **The 1.313 H that Stage A's M2 attributed to SIMPLEC was RELAXATION.** The
> record's standing claim — *"SIMPLEC moved the number substantially"* — is not
> merely unproven, as Stage A reported. It is **misattributed**.

| contrast | isolates | \|Δx_r/H\| | bar (larger of the two runs' own second-half spread) | verdict |
| --- | --- | --- | --- | --- |
| **A1 vs A4** | **`consistent` alone** | 2.911 | 6.560 | **NOT attributable** |
| **A4 vs A3** | **relaxation alone** | **4.224** | 2.578 | **ATTRIBUTABLE** (1.64× the bar) |

Hash precondition met: A4 echoed `system/fvSolution` sha256 `02f62dd3d4b9c081…`,
different from both A1's `2569808326111612…` and A3's `94150fe67f56a6e5…`. The
run did what it was asked, provably.

**O-I4 did not fire.** Plain SIMPLE at SIMPLEC's relaxation (p 0.3 / U 0.6) ran to
its 2 000-iteration cap without diverging. The factorial corner was reachable.

## 2. The factorial, completed

| | relax p 0.15 / U 0.4 | relax p 0.3 / U 0.6 |
| --- | --- | --- |
| **SIMPLE** (`consistent no`) | **A3: x_r/H = 6.876** | **A4: x_r/H = 2.652** ← new |
| **SIMPLEC** (`consistent yes`) | *(corner not run)* | **A1: x_r/H = 5.564** |

The two configurations the record has carried since 2026-07-29 are A1 and A3 —
the **diagonal**. A4 fills the corner that makes either lever readable. Both
detectors agree on A4 as they did on every Stage A leg: wall-Cf crossing 2.652,
convention-free near-wall U_x 2.666, 0.014 H apart.

## 3. The finding that outranks the verdict: relaxation-dependence *is* proof of non-convergence

**Relaxation factors cannot move a converged SIMPLE fixed point.** They are
under-relaxation on the path; they change how you get there, not where. Two solves
of the same equations on the same mesh with the same algorithm, differing only in
relaxation, must agree at convergence — that is what convergence *means*.

**A3 and A4 differ only in relaxation and disagree by 4.224 H — a factor of
2.6 in the gate quantity.**

> **This is direct proof that neither solve has converged, and it does not depend
> on reading any residual at all.**

That matters more than it first appears. This entire thread began because the
original F5c record read the **linear solver's final** residuals instead of
SIMPLE's **initial** ones and concluded "deep numerical convergence." The
relaxation test is immune to that class of error: it needs no residual, no
threshold, and no judgement about which number to read. **It is the check that
should have been run in 2026-07-29, and it costs one extra run.**

The residual evidence agrees, for what it is worth: A4 finishes 51× off its p
gate (5.05e-4 against 1e-5) and 276× off Uy.

## 4. Honest reading of the two contrasts

**"Algorithm not attributable" does not mean "the algorithm does nothing."** The
bar for that contrast is 6.560 H, and it is set entirely by **A1's own wander** —
the SIMPLEC leg swings 6.56 H across the second half of its run. The honest
statement is narrower and less flattering to the experiment: **A1 is too unsettled
to be compared against anything.** The algorithm question is not answered here; it
is shown to be unanswerable at 2 000 iterations on this mesh.

**The relaxation result clears its bar by 1.64×, which is a margin worth stating
rather than rounding up.** It is a real separation, not a comfortable one. What
makes it convincing is not the margin but §3: relaxation-dependence at this size
has only one interpretation, and it does not require the bar at all.

**A4's own spread is the anomaly of the set, and it is reported, not explained.**

| leg | algorithm | relax | second-half x_r spread |
| --- | --- | --- | --- |
| A1 | SIMPLEC | 0.3 / 0.6 | 6.560 H |
| A2 | SIMPLEC | 0.3 / 0.6 (8 000 it) | 1.262 H |
| A3 | SIMPLE | 0.15 / 0.4 | 2.578 H |
| **A4** | **SIMPLE** | **0.3 / 0.6** | **0.171 H** |

A4 is by far the *steadiest* of the four and sits *furthest* from all of them
(2.652 against 5.56–7.00). A quiet history is not evidence of a right answer —
a solve parked on a spurious branch is quiet too, and A4 is 51× off its residual
gate, so quiet it is not converged. **No claim is made about why A4 is both the
most settled and the most deviant; it is recorded as an open observation.**

## 5. What this closes

- **`F5bc_unsteady_statistics.md`'s diagnostic table, row 4** attributes the
  SIMPLE→SIMPLEC move (0.56–0.68 H → 1.07–1.49 H, pre-sign-fix) to *"SIMPLE
  algorithm / relaxation"* and its verdict text to SIMPLEC specifically
  (*"SIMPLEC moved the number substantially (confirms algorithm/relaxation
  matters)"*). **The algorithm half of that attribution is withdrawn; the
  relaxation half is confirmed.** The table's own label already named both — the
  narrative that followed named only one.
- **Stage A's M2** is completed rather than overturned: it scored PROVEN on the
  bar as written, its author reported the bar as too low, and this arm shows the
  effect it measured belonged to the other variable. The charter's demand — that
  the algorithm choice be made log-provable — **remains satisfied**: `consistent`
  is readable and hash-bound in every archived log from here on. What was never
  established is that it *matters*.

## 6. Cost

| | basis (Stage A's A3 — same mesh, iterations, sampling, `consistent no`) | approved | measured |
| --- | --- | --- | --- |
| A4 | 2.11 core-min | ≈2.4 | **2.715** |

**13% over the approved figure and 29% over its own basis.** The cause is named
rather than absorbed: A3 ran on an idle box; A4 ran at load average 5.1 beside the
A3 family's `a3_diag_rung3` container. This is the contended-wall-clock effect
`B52_RUNG7_RESULTS.md` §5 already documented — *"a cost basis taken from a
contended run's wall clock over-predicts by whatever the contention was"* — here
in the other direction. On CPU time the two are far closer; the wall-clock gap is
the box, not the case.

## 7. What is NOT claimed

- **A4's x_r/H = 2.652 is not a candidate headline** and must never be quoted as
  an F5c result. It is a factorial corner at an iteration count now proven far
  from convergence. F5c still has **no headline reattachment number**.
- No wander verdict, in either direction — chief policy: none from a `coarse`
  detector. §4's spreads are reported as data.
- No claim that SIMPLE or SIMPLEC is *correct*, or that either is preferable. This
  arm measured separability, not correctness.
- No second attempt was made at a different relaxation after A4 ran, and none
  will be: the pre-registration forbade it as a different experiment.
- The missing corner (SIMPLEC at p 0.15 / U 0.4) was **not** run. It would make
  the factorial complete and is **not** proposed: §3 already answers the question
  the factorial was completing, and spending on a fourth corner of an unconverged
  design would be measuring the path more precisely instead of the answer.
