# T5 clause-(1) restoration — DESIGN OPTIONS FOR THE SUPERVISOR'S RULING

> **DRAFT / NOT FROZEN / NO COMPUTE.** This is not a pre-registration and registers
> no gate, threshold, cap or label. No solver was launched, no process signalled, no
> comparator run, no run directory created, no frozen file edited. The design
> decision below is the heat-transfer supervisor's and is **not taken here**.
> Drafted by a lab-lane, 2026-09-10, on the supervisor's brief. [lab-attributed]

---

## 0. THE TWO FINDINGS THAT CHANGE THE BRIEF

**FINDING 1 — the unsound verdict is not prospective. It is already published.**
`AMENDMENT 1` at the foot of `T5c_PREREGISTRATION.md` holds T5c so that it *cannot*
grade a triple built from non-converged levels. But **T5c was already run on
2026-09-03** — `verification/runs/T-family/T5c_runs/T5C_GRADE_OUTPUT.txt` (mtime
2026-09-03 17:25) and the repository record `docs/campaigns/T-family/T5c_RESULTS.md`
carry, at its line 1 and line 15:

| row | verdict as published | basis as published |
|---|---|---|
| `G2a` | **`GATE FAIL`** | fine 39.4023 vs reference 55.224, band ± 5.66404, **GCI 4.3550 %** |

That `GATE FAIL` and that `GCI` are graded output from a triple whose three levels
**all fail T5's own registered convergence criterion** (§0 FINDING 2, measured
below). Under standing rule 5 clause (1) the row is `NOT A RESULT` and no GCI is
quotable. **The hold prevents a re-run; it does not withdraw what is on disk.**
A successor must therefore supersede `T5c_RESULTS.md`, not merely precede the next
run.

**FINDING 2 — clause (1)'s registered instrument for T5 is NOT the residual, and
`gate_converged` is not wired to anything.** Both matter for option (a).

`T5_PREREGISTRATION.md` §5.5 (lines 466–472, blob `fc26e51b`) registers, verbatim:

> **`residualControl` is not written** (L-141: in T1c a genuinely unconverged case
> sat at residual 4e-05, and in T3 the residual was again not the instrument).
>
> **CONVERGED** means: the largest change of any cell value of `T` in either region,
> and separately of `U` in the fluid, between the checkpoints at `endTime − 1000`
> and `endTime`, is at most **1e-6 of that field's range**.

So T5's clause (1) is a **checkpoint field-delta**, and the registration *expressly
rejects* the residual as the instrument. `gate_converged` in `analyse_t5.py` is a
**residual-series predicate** (sustained floor + not growing). Carrying it verbatim
would import an instrument T5 registered against, and would require registering a
**new floor and a new sustain** — which is a pre-registration act, not a copy.

Second, `gate_converged` has **no production call site**. In `analyse_t5.py`
(HEAD blob `9c2c1d44`, matching the §16.9 freeze-set row) its only callers are
`selftest()` at lines 330–335 and `_drive_oneway_violation()` at line 381. `main()`
(line 393) runs `check_completion` per level and prints the fixed sentence *"No case
has run: no rows are graded and no verdict is written."* There is no residual
extractor in the file and no `CONV_FLOOR`/`SUSTAIN` constant — the only floor and
sustain values present are the selftest literals `1e-6` and `2`. The registration
already records this at `T5_PREREGISTRATION.md:1579`: *"the frozen `analyse_t5.py`
contains no reference reader and no grading driver at all."*

**Consequence for the brief.** `analyse_t5.py:213` is a *correct and self-tested
predicate wired to a correct grade order* (`grade_row` line 281, clause (1) before
the triple at 287) — but it is **dead code with no data path and no registered
constants**. "T5b is a regression from a working guard" is right about the *order*
and about the *intent*; it overstates the *instrument*, which was never fed.

---

## 1. THE MEASUREMENT THAT DECIDES THE COST QUESTION

### 1a. T5's registered criterion, evaluated on the artifacts already on disk

Both checkpoints exist on all three levels — `4000/` and `5000/`, with `T` in `air`
and `epoxy` and `U` in `air` (ASCII). Read-only diagnostic, nothing written to any
run directory, not a graded artifact:

| level | field | range | max &#124;Δ&#124; 4000→5000 | tol = 1e-6 × range | exceeds tol by |
|---|---|---:|---:|---:|---:|
| `T5_CUBE_c` | air/`T` | 44.463 | 0.316753 | 4.4463e-05 | **7,124×** |
| `T5_CUBE_c` | epoxy/`T` | 35.2003 | 0.0059407 | 3.52003e-05 | **169×** |
| `T5_CUBE_c` | air/`U` | 8.05291 | 0.0860004 | 8.05291e-06 | **10,679×** |
| `T5_CUBE_m` | air/`T` | 48.6851 | 29.6036 | 4.86851e-05 | **608,063×** |
| `T5_CUBE_m` | epoxy/`T` | 36.4775 | 8.8444 | 3.64775e-05 | **242,462×** |
| `T5_CUBE_m` | air/`U` | 9.76783 | 6.40454 | 9.76783e-06 | **655,677×** |
| `T5_CUBE_f` | air/`T` | 48.1021 | 26.4484 | 4.81021e-05 | **549,839×** |
| `T5_CUBE_f` | epoxy/`T` | 38.1417 | 9.48608 | 3.81417e-05 | **248,706×** |
| `T5_CUBE_f` | air/`U` | 10.0523 | 5.2643 | 1.00523e-05 | **523,693×** |

Artifacts: `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/{4000,5000}/{air,epoxy}/{T,U}`.

**ALL THREE LEVELS ARE `NOT CONVERGED` BY T5'S OWN REGISTERED CRITERION — the coarse
included.** The medium changes by **29.6 K** in its last 1000 iterations. This is
wider than the brief assumed: the brief named medium and fine; the coarse fails too,
by 7,124× on air `T`.

### 1b. Residual trajectory — stalled, not slowly converging

`p_rgh` initial residual per outer iteration, from each case's own named `log.solve`
(5000 `Time` blocks each; `chtMultiRegionSimpleFoam`, steady SIMPLE, one `p_rgh`
solve per iteration, no `residualControl` so every case ran the full 5000):

| level | 100 | 1000 | 3000 | 5000 | last-500 min–max | log₁₀ slope, last 500 (dec/1000 it) | last 2000 |
|---|---:|---:|---:|---:|---|---:|---:|
| `c` | 8.10e-02 | 2.26e-03 | 2.26e-03 | 3.21e-03 | 1.19e-03 – 4.52e-03 | **+0.555** | −0.034 |
| `m` | 2.14e-01 | 2.31e-01 | 2.74e-01 | 1.91e-01 | 1.68e-01 – 2.83e-01 | −0.074 | −0.014 |
| `f` | 2.12e-01 | 2.14e-01 | 2.50e-01 | 2.30e-01 | 2.18e-01 – 2.64e-01 | **+0.055** | **+0.017** |

Artifacts: `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/log.solve`.

- **`f`: slope is POSITIVE on every window** (last 500, 1000 and 2000). There is no
  finite `endTime` on this trajectory.
- **`m`: flat band.** max/min over the last 2000 is **1.73** — a plateau reached by
  iteration ~100 and unmoved for 4,900 iterations. The −0.014 dec/1000 it slope is
  noise within that band; taken literally it implies **~375,900 further iterations**
  to 1e-6, which is an extrapolation of noise, not a rate.
- **`c`: wandering plateau** at ~2e-3, **293 sign changes in 498 steps**, positive
  slope over the last 500. Not descending.

**None of the three is "converging slowly." `c` and `m` are STALLED; `f` is stalled
with positive drift.**

### 1c. Why — visible in the same logs, and it is not an iteration-count problem

- **`m`: the turbulence has collapsed.** `k` initial residual is **8.033e-09 at
  iteration 500 and 8.032e-09 at 5000**; `omega` is **3.355e-11 at 500 and 3.343e-11
  at 5000** — unchanged to three significant figures across 4,500 iterations. A
  residual that does not move is a **frozen field, not a converged one**. The final
  `Time = 5000` block of `T5_CUBE_m/log.solve` prints `bounding k, min: 0 max:
  0.3273259146 average: 0.007122671879` — `k` is being clipped at zero.
- **`f`: the turbulence is in a limit cycle.** `omega` initial residual across the
  run: 4.26e-12 (2000), 4.95e-02 (3000), 4.44e-04 (4000), 3.33e-01 (4500), 9.47e-04
  (5000) — **eleven orders of magnitude of swing**. `k` likewise 8.0e-07 (1000) to
  5.7e-03 (5000).
- Both cases run `nNonOrthogonalCorrectors 0` with `p_rgh` relaxation 0.3
  (`T5_CUBE_m/system/air/fvSolution`).

**ANSWER TO THE BRIEF'S CRUX QUESTION: no `endTime` converges `T5_CUBE_m` or
`T5_CUBE_f` as configured.** More iterations is the wrong prescription. T5 §5.5 does
*permit* extension from `latestTime` ("the decision to extend is taken on the
convergence state alone"), so the mechanism is legal — the measurement simply says
it is futile. Confidence: **high** for `f` and `m`; **moderate-to-high** for `c`
(its turbulence is alive, but it sits three orders above a 1e-6 floor with a
positive recent slope).

---

## 2. THE OPTIONS

### Option (a) — successor carrying `gate_converged` VERBATIM plus T5c's y+ change
**Not viable as stated.** Per §0 FINDING 2: it imports a residual instrument the T5
registration expressly rejected, it has no extractor to feed it, and it has no
registered floor or sustain — so "verbatim" is not a copy, it is a **new threshold**,
and a new threshold in a successor is a fresh pre-registration act that must be
frozen before compute anyway. It would also grade against a criterion *weaker* than
the one T5 already registered. Cost of the re-grade itself: free. Cost in
defensibility: it substitutes an unregistered instrument for a registered one.

### Option (b) — restore clause (1) only, defer T5c's y+ question
Cheap and narrow, but it leaves **`T5c_RESULTS.md`'s published `GATE FAIL` and
`GCI 4.3550 %` standing** (§0 FINDING 1). A clause-(1) rung that does not supersede
the record carrying the unsound verdict fixes the instrument and leaves the error in
the repository. It also splits one re-grade of one artifact set into two rungs for
no compute saving — both are free.

### Option (c) — RECOMMENDED. `T5e`: a dated successor on T5's OWN registered criterion, superseding T5b and T5c
Name checked: **`T5e` is unused** across `docs/campaigns/T-family/` and
`verification/runs/T-family/` (`T5`, `T5b`, `T5c`, `T5d` exist; no `T5e` anywhere).

`T5e` would:
1. Implement clause (1) as **`T5_PREREGISTRATION.md` §5.5 registers it** — max
   &#124;Δ cell value&#124; between `4000` and `5000` ≤ 1e-6 × field range, on `T` in
   both regions and `U` in the fluid — evaluated **per level, before the triple**,
   in `grade_row`'s position (1), with the y+ clause moved to (0) as
   `analyse_t5.py:277` already orders it. **No new threshold is registered**: the
   number is T5's own, frozen before any T5 case existed.
2. Carry T5c's **area-averaged y+** change unchanged (it is a statistic change, not a
   threshold change, and T5c's own record documents the byte-identity assertion of
   20 constants against frozen `analyse_t5b.py`).
3. Carry `analyse_t5.py`'s **`gate_converged` shape as a SECOND, subordinate report**
   — printed as `REPORTED`, never gating — so the residual evidence of §1b is on the
   record without an unregistered instrument writing a verdict.
4. **Supersede `T5c_RESULTS.md`**, withdrawing `G2a`'s `GATE FAIL` and its `GCI` to
   `NOT A RESULT`, with the pre-supersession state printed beside each row exactly as
   T5c printed its own pre-repair states.
5. Plant a **live control** on the clause-(1) reader (rule 3): perturb a copied `T`
   checkpoint by a known amount, read it back, and **refuse (exit 2)** if the reader
   cannot see it. A zero from an unproven reader is not evidence — and this reader's
   whole job is to emit a non-zero delta.

**Predicted outcome, stated before the run (this is a prediction, not a result):**
**6 of 6 rows `NOT A RESULT` on clause (1)**, on all three levels, from §1a.

**Cost: < 1 core-min, comparator time only, no solver — and it is genuinely free.**
Established, not assumed: the criterion needs only `4000/` and `5000/` `T` and `U`,
and both checkpoints are present on all three levels (§1a). No new solver compute is
required *to grade honestly*.

**What the free re-grade buys, stated plainly:** it buys the **withdrawal of an
unsound published `GATE FAIL` and `GCI`**, and an honest `NOT A RESULT` in its place.
It does **not** buy a physics result. That is the correct outcome and it is worth the
core-minute — but the supervisor should not expect a graded row from it.

### 2d. If a physics result on T5 is wanted, what it actually costs
Not an `endTime` extension (§1c). It requires a **setup change** — turbulence
initialisation and wall treatment on `m` and `f`, `nNonOrthogonalCorrectors`,
relaxation — which is a **new rung with its own pre-registration and its own solver
budget**, not an addendum to T5e.

Measured basis, from the T5b `STATUS` files (`verification/runs/T-family/T5b_runs/STATUS.T5_CUBE_{c,m,f}`,
all `capped=0`, `note=clean`, `ranks=1`), at `endTime 5000`:

| level | wall_s | core_min (measured) | cap_core_min |
|---|---:|---:|---:|
| `T5_CUBE_c` | 1007 | **16.783** | 32.8 |
| `T5_CUBE_m` | 5252 | **87.533** | 154.4 |
| `T5_CUBE_f` | 20851 | **347.517** | 651.2 |

Triple at 5000 = **451.83 core-min** (measured). A 4× longer run scaled linearly
(**estimated, not measured** — linear in iterations for fixed-mesh steady SIMPLE)
≈ **1,807 core-min ≈ 30.1 core-h**, derived **$1.55** at the recorded
$0.0513/core-h — *derived, not measured*; the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **Recommendation: do not spend it on an extension.**
The measurement in §1b–§1c says the iterations would not converge.

---

## 3. RECOMMENDATION

**Option (c), `T5e`.** It restores clause (1) using **T5's own registered
instrument** rather than importing an unregistered one; it is free because the
checkpoints are on disk; and it is the only option that reaches the verdict already
published in `T5c_RESULTS.md`. The `T5c` hold stays in force until `T5e` is frozen.

**Reserved to the supervisor, and not taken here:** whether to open `T5e`; whether
the withdrawal of `T5c`'s `G2a` row is a T5e supersession or a separate correction
record; and whether the clause-(1) instrument question warrants the `verification`
ruling `AMENDMENT 1` already routed.
