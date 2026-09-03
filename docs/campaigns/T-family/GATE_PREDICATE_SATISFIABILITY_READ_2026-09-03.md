# GATE PREDICATE SATISFIABILITY READ — T-family and F14-cooling-ladder, 2026-09-03

**This is a CODE READ. It is not an instrument, and none was built.** No checker,
linter, sweeper or satisfiability tool was written, and no program was written
that grades another program. `grep` was used only to LOCATE candidate lines; every
judgement below was made by reading the line and its surrounding block. Sanaa's
20:00Z ruling — *"No instrument is built to measure another instrument's reach
unless the first instrument has already changed a verdict at least once"* — sets a
precondition that was already satisfied before this read began: the same read
changed two verdicts on 2026-09-03 (the T25R6a equivalence predicate and the T15
S1 constant-offset arm, §A.1 and §A.2 below).

**This document RECORDS; it REPAIRS NOTHING.** Every file named here is frozen or
has fired. `CLAUDE.md` rule 6 forbids editing a frozen file, and a repair on a
grading path after first compute is a `VERIFICATION_CHARTER` §2d.1 matter for
verification, not for heat-transfer. The petition route is already open at
`docs/campaigns/T-family/T25R6a_2D1_EQUIVALENCE_PREDICATE_PETITION.md`. **No past
result is re-graded here** (Sanaa 2026-09-03 17:30Z: *"No re-grading of past
results unless a specific comparator is shown to have moved"*). Where a finding
would move a verdict, this record says so and stops there.

Sibling register, no overlap with it:
`docs/campaigns/T-family/OPEN_INSTRUMENT_DEFECTS_2026-08-31.md`.

---

## 0. The defect class, and the three questions

**The class.** A gate or completion predicate that **no run can satisfy**, or that
**no run can fail**, or **whose outcome is not determined by the data at all**.

A gate no run can pass is not a strict gate; it is a broken one. A control that
cannot fire is decoration. A predicate decided by a type, an evaluation order or
an algebraic identity is decided by something other than the measurement it claims
to check.

**The three questions**, asked of each candidate and answered from the code:

- **(a)** can a real run make this predicate TRUE?
- **(b)** can a real run make it FALSE?
- **(c)** is the outcome determined by the DATA, or by types, evaluation order,
  or an identity?

A predicate is reported below when the answer to (a) or (b) is **no**, or (c) is
**"not by the data"**.

**What is deliberately NOT reported.** A structural check on a value the case
builder writes (patch counts, `valueFraction` formulas, ladder refinement ratios)
answers (a) and (b) YES — a hand-edited or mutated case flips it — and is
determined by bytes on disk. Those are strict, not broken, and none is listed. A
loop clause that is vacuous on one of its three iterations but data-determined on
the other two (the `Bi`/`Fo_end` cross-level identity at `analyse_t14.py:244`,
`analyse_t17.py:336`, `analyse_t18.py:273`, where the reference level is compared
against itself) is a redundancy, not a defect, and is recorded here only so that a
successor does not re-derive it.

---

## 1. Method and coverage — stated so the gaps are visible

**Enumerated:** 72 comparator and grader scripts under
`verification/runs/T-family/` and `verification/runs/F14-cooling-ladder/`. Of
these, **40 carry a graded output artifact** on disk (a `gate_*.json`,
`*_VERDICT.json`, `*_GRADE*.txt/json`, or a regrade record) and are therefore
comparators that have **actually graded a rung**. Those 40 are the priority set
this read was asked to cover.

**Read line by line:** every conditional carrying a comparison operator in **29**
of those graded comparators — **704 predicate lines** in total, in three batches:

| batch | files | predicate lines |
|---|---:|---:|
| T-family, part 1 (`T10aR2`, `T10aR`, `T11`, `T13`, `T14`, `T17`, `T18`, `T19b`, `T1b_L4`, `T1c`) | 10 | 244 |
| T-family, part 2 (`T23`, `T24`, `T25R4` probe, `T25R5`, `T25R6c`, `T4`, `T4b`, `T9aR1c`) | 8 | 263 |
| F14 (`K0cG`, `K0cP`, `K0cQ`, `K0cR`, `K0cS`, `K0cT`, `K0cX`, `K0c`, `K2e`, `grade_d403`, `grade_d406`) | 11 | 197 |

**Read as full blocks, in addition:** ~30 gate, control and completion blocks
opened and read in their entirety — `grade_t25R6a.py`'s equivalence control and
its delegate `compare_arms_t25R5.py` (`compare`, `planted_control`),
`analyse_t15.py`'s planted-zero control and `apply_gate`, `build_t19.py`'s
`fv_solution` against `mark_done_t19.py`'s six clauses and all six T19 arm logs,
`analyse_t23.py` / `analyse_t23g.py` / `analyse_t24.py` / `analyse_t25R2.py`
planted-zero acceptance limbs, `analyse_t19b.py`'s planted-zero control,
`grade_t25R5.py`'s R-bands, `grade_probe_t25R4.py`'s verdict branch,
`analyse_t9aR1c.py`'s `apply_gate`, `analyse_k0c.py` / `analyse_k0cQ.py` /
`analyse_k0cg.py` / `grade_d403.py` verdict branches, and the field tuples of all
39 `mark_done_*.py` scripts in the family.

**COULD NOT SEE — the honest gap.** Eleven of the 40 graded comparators were
**pattern-scanned only**, for the two defect shapes this read had already found,
and were **not** read predicate by predicate: `analyse_t10a.py`,
`analyse_t16.py`, `analyse_t23g.py`, `analyse_t25R2.py`, `analyse_t3.py`,
`analyse_t5b.py`, `analyse_t5c.py`, `analyse_t9aH.py`, `analyse_t9a.py`,
`analyse_k0b_mesh.py`, `analyse_k2b.py`. Together they are roughly 480 kB of
Python. **A clean scan of those eleven is not a clean read of them**, and this
record does not claim one. The scan did find one of the two new instances (§B.1,
in `analyse_t23g.py`), which is evidence the shapes transfer — and equally
evidence that a shape this read has not yet thought of would not have been caught
there.

**Also could not see:** anything about the four non-T-family, non-F14 teams; the
`selftest()` bodies of the 29 read files were read only where a predicate line
fell inside one; and whether a predicate reported clean here is clean against
*inputs that have never occurred*, since satisfiability was reasoned from the code
and, where possible, checked against artifacts on disk.

---

## A. The four known instances — confirmed, with one correction and one measurement

### A.1 `T25R6a_C5_OUTER_runs/grade_t25R6a.py:437` — **CONFIRMED, UNSATISFIABLE**

```
r = cmp_mod.compare(os.path.join(HERE, "C5_%s" % lvl),
                    os.path.join(HERE, "B0_%s" % lvl))
equiv["C5_%s" % lvl] = str(r)
if r is not True and r != 0:
    equiv_ok = False
```

The delegate is `T25R5_LINSOLVER_runs/compare_arms_t25R5.py:253`. It builds a dict
`res`, and **`return res` at line 292 is its only return statement** — every other
exit is a `SystemExit` propagating out of `maxdiff`/`gather`. So `r` is **always a
dict**. `r is not True` is therefore always True; `dict != 0` is always True.
`equiv_ok` is set False on the first level and the control **always fires**,
producing `NOT A RESULT` regardless of what the two arms contain.

- (a) can a run make the *pass* branch true? **NO.**
- (c) determined by **the return TYPE**, not by the data.

The value the comparator actually computes and that the predicate ignores is
`res["fired"]` — the list the delegate fills at lines 264, 269, 274 from the E1 /
E2 / E1U thresholds. **This is the instance that hid the Sigma CAP number for
days.** Disposition is verification's under §2d.1; the petition is already open.

### A.2 `T15_runs/analyse_t15.py:501` — **CONFIRMED, and now MEASURED**

```
orig, n = _plant_probe_file(p, col, t0, t1, 1.0 * mean_scale, alternate=False)
got_const = _s1_of(dst, reg)
...
d_const = abs(got_const - ref)
if d_const > 0.5 * ref:
    refuse(...)
```

`mean_scale = abs(st_ref["mean"])` (`:462`). The arm adds a **constant equal to
the window mean** to every sample in the window. `_s1_of` returns
`window_stats(...)["rel_sd"] = sd / |mean|` (`:293`, `:529`). A constant offset
leaves `sd` untouched and, for a positive mean, doubles the mean — so
`got_const = ref/2` and `d_const = ref/2`, which is **exactly the threshold**.
The predicate sits on its own boundary and is decided by the floating-point
summation residue of `sum(vs)/n` over the shifted series.

**Verified against the file, then measured on the actual T15 probe series**
(`T15_UP_f/postProcessing/axisProbes/0/U`, probe column 1 at z = 3.0 m, registered
window [120, 240] s, n = 1201 samples), reproducing the arm's arithmetic exactly:

| quantity | value |
|---|---|
| window mean | +0.711597973876 m/s (**positive**, so the `inf` branch does not apply) |
| window sd | 1.41674788594e-04 |
| `ref` = sd/\|mean\| | 1.99093861696e-04 |
| `0.5 * ref` (the threshold) | **9.9546930847766257e-05** |
| `d_const` (reproduced) | **9.9546930847767328e-05** |
| relative excess over threshold | **+1.076e-14** (≈ 48 ULP) |

The grader's own captured output (`T15_runs/T15_GRADE_OUTPUT.txt`, last line)
records the refusal at `9.95e-05`, agreeing with the reproduction.

- (a) TRUE? yes, by 48 ULP. (b) FALSE? yes, by 48 ULP the other way.
- (c) **not determined by the data.** Determined by summation order over 1201
  samples: √1201 · ε ≈ 7.7e-15, which is the size of the observed excess.

**CORRECTION to the brief's reading.** The predicate is not merely
nondeterministic in principle: on T15's real data it landed 1.08e-14 above its own
threshold, and **that rounding residue is what refused the rung**. The mean-below-
zero branch (where `rel_sd` returns `inf` and refusal is certain) is real in the
code but did **not** apply here, because the axial vertical velocity in the plume
is positive.

**CONSEQUENCE — this one would move a verdict, and this record stops there.** T15
carries **no row verdict**: `analyse_t15.py` exited 2 in this arm before
`apply_gate` was reached, so S1, V1, V2 and V3 are ungraded. The three other
planted-zero readers (`w_axis`, `T_axis`, `b_th`) all PASSED. Whether the S1 arm's
refusal stands is **verification's call under §2d.1**, not heat-transfer's, and
nothing here re-grades it.

### A.3 T19 — **CONFIRMED, and it is worse than the brief stated**

`build_t19.py:211` writes, into every one of the six cases:

```
SIMPLE { ... residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; } }
```

`docs/campaigns/T-family/T19_PREREGISTRATION.md:50` and `:116` register
`endTime` = 30 000 as an **iteration count** at `deltaT` = 1, and the prereg's
own control table binds completion to `mark_done_t19.py`, *"rule 4 in full
including the age guard"*. `mark_done_t19.py:101–102` is clause 3 —
`last written time != endTime` → NOT DONE — and `:110` is clause 5,
`ExecutionTime` lines != `endTime`/`deltaT` = 30 000.

Once the solver converges, it stops and writes at the converged iteration, so the
last written time is **not** 30 000 and the `ExecutionTime` count is **not**
30 000. The registered `residualControl` and the registered completion rule are
**mutually exclusive**, and the run cannot be marked complete no matter what the
physics does.

**Confirmed against the artifacts. All six arms converged early — not two:**

| arm | converged at | time dirs written | `ExecutionTime` lines | core-min | started |
|---|---:|---|---:|---:|---|
| `P_Ts_c` | 541 | `0 541` | 541 | 0.033 | 2026-08-30T23:50:19Z |
| `P_q_c` | 828 | `0 828` | 828 | 0.050 | 2026-08-30T23:53:34Z |
| `P_Ts_m` | 1929 | `0 1929` | 1929 | 0.517 | 2026-09-03T17:32:14Z |
| `P_q_m` | 3203 | `0 2000 3203` | 3203 | 0.683 | 2026-09-03T17:34:24Z |
| `P_Ts_f` | 7238 | `0 2000 4000 6000 7238` | 7238 | 12.033 | 2026-09-03T17:27:54Z |
| `P_q_f` | 12437 | `0 … 12000 12437` | 12437 | 15.817 | 2026-09-03T17:31:09Z |

Every arm reports `rc=0` and `SIMPLE solution converged in N iterations`; **no arm
reaches 30 000, so no arm can pass clause 3 or clause 5.** Total spend on a rung
that is structurally unable to be marked complete: **29.133 core-min**.

- (a) can a run make the completion predicate TRUE? **NO**, not while the
  registered `residualControl` stands.
- (c) determined by **a contradiction between two registered clauses**, not by the
  data.

**Already repaired forward, and this record does not duplicate that.**
`T19b_runs/build_t19b.py:6–17` states the defect in its own header and drops the
`residualControl` block so the solver runs to the registered `endTime`;
`T19b_runs/gate_t19b.json` pins T19's own frozen registration and moves no gate,
threshold, band, floor, cap or label. **The repair is to the CASE, not to the
gate**, which is the correct disposition. What is new here is the confirmation
that **all six** arms are affected, not two.

**Also confirmed, and it bounds the class:** the `residualControl`-versus-`endTime`
contradiction is **confined to T19**. L-141 (*no `residualControl`; convergence is
judged from written checkpoints*) is applied in `build_t9a.py:40`,
`build_t9aD.py:35`, `build_e4a.py:254`, every `T9a_runs/*/CASE.txt`,
`T25R6a_C5_OUTER_runs/*/system/fvSolution:17` and `build_t19b.py`. T19 is the one
case family that departed from it.

### A.4 `CLAUDE.md` rule 4, "ExecutionTime count == endTime"

Read literally, unsatisfiable for any case with `deltaT != 1`. **Already escalated
to the docket by another lane; not duplicated here.** Noted only because the
family's own completion scripts have quietly repaired it in place —
`mark_done_t19.py:13–14` writes the clause as *"`ExecutionTime` line count ==
`endTime`/`deltaT` … the steady rungs' `count == endTime` expressed for
`deltaT != 1`, T11 form"*, and `:110` implements the division. That is a
divergence between the constitution's wording and the family's practice, and the
practice is the correct one.

---

## B. Two further instances found by this read

Both are of the class and both fail question **(a)**. Both are of **LOW
consequence** — neither gates a rung's verdict, and **neither would move one** —
and they are reported at that weight, per the instruction to prioritise by
consequence rather than by count.

### B.1 `T23_runs/analyse_t23.py:377` and `T23G_runs/analyse_t23g.py:407` — **UNSATISFIABLE, subsumed limb**

Both files carry, consecutively, inside the rule-3 planted-zero control:

```
if not (at_plant >= PLANT * (1.0 - 1e-9)):
    refuse("...read at PLANT is %.6e, below PLANT*(1-1e-9) = %.6e" ...)
if at_plant < 0.1 * PLANT:
    refuse("...read at PLANT is %.6e, below 0.1 x PLANT" ...)
```

`PLANT = RT.PLANT = 1.234e-03` K, imported from `scripts/roache_triple.py` and
never redefined (`analyse_t23.py:85`, `analyse_t23g.py:123`). Reaching the second
limb requires `at_plant >= 0.999999999 × 1.234e-03`, which is strictly greater
than `0.1 × PLANT = 1.234e-04`. **The second limb can never fire.**

- (a) can a real run make it TRUE? **NO** — it is fully subsumed by the limb four
  lines above it, which is nine orders of magnitude stricter.
- (b) FALSE? always.
- (c) determined by **the ordering of two limbs**, not by the data.

**Consequence: LOW, and it does not move a verdict.** The subsuming limb is the
real gate and it is data-determined and satisfiable in both directions; the
control is sound. The dead limb is decoration that reads as a second, independent
check and is not one — which is the same misreading risk the class is named for,
at a fraction of the cost.

**Bounded, and the family already drifted away from it without recording why.**
The two successors dropped the limb: `analyse_t24.py:517` and
`analyse_t25R2.py:889` carry only the relative predicate (with the constant
promoted to a named `PLANT_REL_SLACK`). So the defect lives in exactly two files,
`analyse_t23.py` and `analyse_t23g.py`, both of which have graded
(`T23_GRADE.json`, `T23G_GRADED.json`).

### B.2 `T19b_runs/analyse_t19b.py:325` — **UNREACHABLE limb**

```
for mag in (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7):
    ...
    if d > 0.0:
        floor = mag                       # :309
...
if seen[PLANT] == 0.0:
    refuse("...the REGISTERED plant moved the read by exactly zero...")   # :321
if floor > PLANT:
    refuse("...the demonstrated detection floor is COARSER than the registered
            plant...")                                                    # :325
```

The ladder descends, so `floor` ends as the **smallest** visible magnitude. `d` is
an `abs()`, so `d > 0.0` and `d == 0.0` are exactly complementary. If
`seen[PLANT] > 0` then `floor` was assigned at `mag == PLANT` at the latest and can
only have been lowered afterwards, so `floor <= PLANT`. If `seen[PLANT] == 0` the
limb at `:321` has already refused. **`floor > PLANT` is therefore unreachable.**

- (a) TRUE? **NO.** (c) determined by **the ladder's ordering and the
  complementarity of `d > 0` with `d == 0`**, not by the data.

**Consequence: LOW, and it does not move a verdict.** It is a belt-and-braces
limb behind a limb that already refuses on the identical condition. T19b has not
yet graded a rung (`gate_t19b.json` is a pinned registration, not a verdict), so
nothing rests on it today.

**Note the contrast with T15, which is why T15's is the serious one.** T15's
ladder limb at `analyse_t15.py:492` reads `if seen[PLANT] <= 1e-9`, not
`== 0.0` — those are **not** complementary with `d > 0.0`, so T15's `floor` and
its refusal limb are genuinely independent, and its defect is elsewhere (§A.2).

---

## C. Predicates examined and found SOUND — recorded so a successor need not redo them

Each answers (a) YES, (b) YES, and (c) *by the data*.

| site | predicate | why it is sound |
|---|---|---|
| `grade_t25R6a.py:347` | `cmp_mod.planted_control(d) is not True` | `planted_control` (`compare_arms_t25R5.py:167`) returns literal `True` or refuses via `SystemExit`. **Well-typed** — the neighbouring `:437` is not, and the contrast is the whole point |
| `analyse_t15.py:533` `apply_gate` | `lo <= value <= hi` → PASS else GATE FAIL; gate (1) overrides to NOT A RESULT | one-way, band-determined; no triple, no GCI quoted |
| `analyse_t9aR1c.py:497–503` `apply_gate` | band → PASS/GATE FAIL; ceiling can only weaken | one-way; nothing turns NOT A RESULT into PASS |
| `grade_t25R5.py:235–244` | `R < 1.0` / `R <= 1.5` / `R >= 3.0` / else | all four bands reachable; `else` covers the gap |
| `grade_probe_t25R4.py:62–66` | `verdict != "NOT A RESULT" and len(mean) == 3 and min(...) > 0` | both branches reachable — a level can `continue` out, and `No Iterations 0` gives a zero mean |
| `analyse_k0cQ.py:196–212` | NOT A RESULT / SMALL / LARGE / INTERMEDIATE | exhaustive with a terminal `else` |
| `grade_d403.py:55–61` | `< REPRODUCED_PCT` / `> NOT_REPRODUCED_PCT` / gap | three-way, all reachable (the gap band is 0.1–1 %). **Separate issue, not this class:** its labels are outside the rule-1 vocabulary |
| `analyse_t14.py:244`, `analyse_t17.py:336`, `analyse_t18.py:273` | `abs(float(metas[lv]["Bi"]) - Bi) > 0` | vacuous on the reference level only (`Bi` is read from `metas["f"]`); data-determined on the other two. **Redundancy, not a defect** |
| `analyse_t17.py:341` | `valueFraction_radial >= valueFraction_axial` | a check on bytes the builder wrote; a mutated case flips it |
| all 39 `mark_done_*.py` field tuples | per-rung tuples: `("T","U","p_rgh","alphat")` T19, `("T","DT")` T9a, `("T","qr")` T10a, `("T","U","p","p_rgh","alphat","nut","k","omega")` T23/T24/T25R* | each is matched to its own registered closure. **The K0d defect — a `nut k omega` tuple demanded of a `laminar` case, 829 core-min lost — has not recurred anywhere in the family** |

---

## D. What this changes, and where it stops

**Nothing, by itself.** This record grades nothing, marks nothing, edits no frozen
file and re-runs no case.

1. **§A.1 and §A.2 are the two that would move a verdict**, and both are already
   where they belong: A.1 in the open §2d.1 petition, A.2 in T15's ungraded state.
   Heat-transfer does not resolve either. Verification does.
2. **§A.3 is already repaired forward** by T19b, and the repair is to the case, not
   to a gate. What is added here is that **all six** T19 arms are affected and
   **29.133 core-min** sits behind a completion rule none of them can satisfy.
3. **§B.1 and §B.2 are low-consequence and are recorded, not petitioned.** Under
   the 20:00Z ruling — *"Petitions, rulings, and charter amendments require a
   blocked result to name. No result blocked → no petition; the team decides
   locally and records the decision as a lesson"* — neither blocks a result, so
   neither gets a petition. **The local decision is: leave both files untouched
   (rule 6; both are frozen and both have fired), and let the successors that
   already dropped the B.1 limb stand as the forward-only fix.**
4. **The eleven unread comparators in §1 remain unread.** If this class matters
   enough to close, that is the work — and it is a code read, not an instrument.

---

## E. Artifacts every claim above cites

| claim | artifact |
|---|---|
| A.1 predicate and its delegate | `verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py:434–441`; `verification/runs/T-family/T25R5_LINSOLVER_runs/compare_arms_t25R5.py:253–292` |
| A.2 predicate | `verification/runs/T-family/T15_runs/analyse_t15.py:462, 492, 497–503, 271–297, 524–529` |
| A.2 refusal as it actually fired | `verification/runs/T-family/T15_runs/T15_GRADE_OUTPUT.txt` (final line) |
| A.2 probe series measured | `verification/runs/T-family/T15_runs/T15_UP_f/postProcessing/axisProbes/0/U`; window and station from `T15_runs/T15_registered.json` |
| A.3 registration | `docs/campaigns/T-family/T19_PREREGISTRATION.md:50, 116, 200–214` |
| A.3 case build | `verification/runs/T-family/T19_runs/build_t19.py:211` |
| A.3 completion clauses | `verification/runs/T-family/T19_runs/mark_done_t19.py:8, 13–14, 94–118` |
| A.3 six arms | `verification/runs/T-family/T19_runs/P_{Ts,q}_{c,m,f}/log.solve` and `STATUS.P_*` |
| A.3 forward repair | `verification/runs/T-family/T19b_runs/build_t19b.py:6–17, 326–337`; `T19b_runs/gate_t19b.json` |
| B.1 | `verification/runs/T-family/T23_runs/analyse_t23.py:85, 374–379`; `verification/runs/T-family/T23G_runs/analyse_t23g.py:123, 404–409`; successors at `analyse_t24.py:517` and `analyse_t25R2.py:889` |
| B.2 | `verification/runs/T-family/T19b_runs/analyse_t19b.py:299–326` |
| cost figures quoted in A.3 | `verification/runs/T-family/T19_runs/STATUS.P_*` (`core_min`) |
