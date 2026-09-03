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

---

## F. DATED SECTION — 2026-09-03T18:5xZ: THE FOURTH QUESTION, **(d) THE CALLER SIDE**

**Appended, not rewritten. Lines whose number changed above this section: 0.**

Added on the heat-transfer supervisor's instruction, sourced from verification's
completed four-faces audit — `docs/FAIL_OPEN_GATE_AUDIT.md` §28 (commit
`4b98398c`), **read at source before being applied**, not on relay. §28's own
words for the test:

> **CAN THIS CODE PATH DISTINGUISH "THE CHECK RAN AND FOUND NOTHING" FROM "THE
> CHECK DID NOT RUN"? If it cannot, its zero is UNINTERPRETABLE and must refuse.**
> That is rule 3's planted control asked one step earlier — **plant the RUN, not
> only the VALUE.**

**Still a code read. Nothing was built, nothing repaired, nothing re-graded, and
the live solver found in §F.4 was not touched.** §28 is explicit that it orders no
sweep and that three of its four faces are relayed rather than re-derived; this
section adds two measured specimens from this family and one correction, and
claims nothing broader.

### F.1 Why (d) is a different guarantee from (a)/(b)/(c)

(a), (b) and (c) are **instrument-side**: can this check emit a failure, can it
emit a pass, and is the outcome the data's. **(d) is caller-side**: was the check
ever invoked, and can a reader of the artifact tell? A planted-zero control that
answers (a)–(c) perfectly still proves nothing if no one called it, and §28's tell
is that *the absence of an error was read as the presence of a check*.

### F.2 Two (d) findings in this family. **Neither moves a verdict.**

#### F.2.1 `grade_t25R6a.py` + `compare_arms_t25R5.py:planted_control` — the verdict artifact carries **no positive evidence the rule-3 control ran**

`T25R6a_VERDICT.json` carries 23 top-level keys — `ceiling`, `censored`,
`cost_basis`, `equivalence`, `gate`, `repro`, `roache`, `rule4`, `verdict` and the
rest — and **not one of them names the plant magnitude, the recovered value or a
detection floor.** A `T25R6a_VERDICT.json` produced with the rule-3 control never
invoked would be byte-indistinguishable from this one.

**The defect is at the INTERFACE, not only at the caller.**
`compare_arms_t25R5.py:202` ends `planted_control` with a bare `return True`. It
measures `seen = maxdiff(orig, new, ...)` per region and per end, compares it to
`PLANT` within `PLANT_TOL_K`, and then **throws the measurement away** — so the
caller at `grade_t25R6a.py:347` has nothing to record even if it wanted to.

**What is sound, stated so the finding is not inflated.** The call at
`grade_t25R6a.py:341–352` is **unconditional**; it **refuses when the case
directory is absent** (`:343–345` — absence REFUSES, it does not read as nothing
to flag); and it refuses on any non-`True` return. So the control **did** run.
**The failure is that a reader of the artifact cannot establish that**, which is
exactly §28's tell.

- (d) **FAIL** on the artifact. (a), (b), (c) sound for this control — the
  neighbouring (a) failure is at `:437` and is a different predicate (§A.1).
- **Does not move a verdict:** T25R6a is already `NOT A RESULT` from §A.1.

#### F.2.2 `analyse_t24.py:973–981` — a swallowed classification, face 1 in miniature

```
try:
    if float(la.split()[0]) > float(npr):
        print("    SATURATED at launch ...")
except (ValueError, IndexError, AttributeError):
    pass
```

If `START.<case>`'s load average is malformed, absent, or not the shape expected,
the saturation classification **silently does not happen** and **nothing anywhere
records that it was attempted**. "Not saturated" and "loadavg unreadable" produce
the identical artifact and the identical silence.

This is advisory to the calibration row rather than to the verdict —
`T24_PREREGISTRATION.md` §5.5 registers a saturated launch as producing *a COST
but NOT a calibration row* — which is to say it is advisory to **the very row
landed today**.

- (d) **FAIL**, consequence **LOW**: T24's `START.T24_*` files **do** exist (the
  missing-`START` defect that `OPEN_INSTRUMENT_DEFECTS_2026-08-31.md` finding 1
  records against T23 was fixed for T24), and all twelve `gate_t24.json` rows
  carry a `start` block, so the `except` limb is not believed to have fired.
- **Does not move a verdict.**

### F.3 (d)-SOUND, recorded so a successor does not redo it

| what | evidence |
|---|---|
| **Best (d) example in the family** | `gate_t24.json` rows carry `control_Q1_at_plant`, `control_Q1_floor`, `control_Q2_at_plant`, `control_Q2_floor` — **per case, measured**. A recovered value and a demonstrated floor cannot exist unless the control ran |
| T23, weaker but sound | `T23_GRADE.json` rows carry `control_Q1_floor` / `control_Q2_floor` but **not** `at_plant`. A floor is still a measured quantity, so it is still positive evidence; T24 added `at_plant` and T23 has only the floor |
| control blocks present in the verdict artifact | `gate_t11.json` `planted_zero_control`; `gate_t14.json`, `gate_t17.json`, `gate_t18.json` `planted_zero_controls`; `T25R6c_VERDICT.json` `planted_zero`; `gate_k0c.json` and `gate_k0ct.json` `controls` + `control_predictions` |
| T15 | would have carried `planted_zero_controls=pz` in its JSON — it refused first (§A.2), and the refusal itself is captured in `T15_GRADE_OUTPUT.txt`, which is caller-side evidence of a different and adequate kind |
| **completion checks have the (d)-CORRECT polarity throughout** | absence REFUSES, it never reads as nothing-to-flag: `analyse_t14.py:238`, `analyse_t17.py:327`, `analyse_t9aR1c.py:513` all refuse on a missing `DONE` marker; `grade_t25R6a.py:343` refuses on a missing case directory; `grade_t25R5.py:84` refuses on a missing or non-zero `rc` file |
| **Roache triple is never bypassed on a PASS path** | in T11 (`:277`), T14 (`:205`), T17 (`:294`), T18 (`:234`) the triple state is consulted **before** the band test. Where there is no triple, the artifact says so **positively** rather than by omission: `T15` writes `grid_triple: false` and `triple: "NONE -- SINGLE MESH, NO GRID-CONVERGENCE EVIDENCE"` on every row, `T25R6a_VERDICT.json` writes `roache: "NOT INVOKED -- no grid claim, no order, no GCI"`. **No comparator read here can emit a PASS on a path that never consulted the triple** |
| no swallowed refusals in the runners | every `2>/dev/null` found under `T-family/*/ *.sh` and `F14-cooling-ladder/*/ *.sh` is on a `readlink`/`cat` of a possibly-absent `/proc` entry inside a launch guard (`run_one_e4a.sh:12,14`, `run_one_t11.sh:32,35` and the like). None silences an instrument |

### F.4 The supervisor's two claims: one **CONFIRMED**, one **CORRECTED**

Both were checked at source rather than taken on faith, as instructed.

**CLAIM 1 — "the live T3d run has NO monitor of any kind" — CONFIRMED, and the
case is now named.** The live run is
`verification/runs/T-family/T3_runs/R_fx` (`T3_runs/launch_t3d.sh` names `R_fx`).
Its `log.solve` was being written at **2026-09-03T18:51:10Z**, the instant it was
read, at **`Time = 1917`**. **No monitor sidecar exists anywhere under
`T3_runs/`**, and `verification/monitor/` holds only VR2 and VR5 artifacts
unrelated to this case. So "no alarm" and "nothing watching" are the same
observation, exactly as put. **This is a (d) failure at the fleet level, not in a
file, and it sits against Sanaa's 22:00Z ruling that every run is watched by its
monitor. THE RUN WAS NOT TOUCHED** — this is a read of mtimes and of the log's
last `Time` line, nothing more.

**CLAIM 2 — "`docs/COST_CALIBRATION.md` has no caller-side proof; the fix that is
allowed is that the RUNG RECORD states the debt in its own text" — the diagnosis
holds and THE PROPOSED FIX IS CORRECTED, because it already exists and it already
failed.**

Both rungs **already state the debt in their own registration text**:

- `docs/campaigns/T-family/T15_PREREGISTRATION.md:329` — *"…`docs/COST_CALIBRATION.md` at completion"*, and `T15_registered.json`'s `cost.note` ends *"Calibration row owed in `docs/COST_CALIBRATION.md` at completion."*
- `docs/campaigns/T-family/T24_PREREGISTRATION.md:902` — requires *"a row appended to `docs/COST_CALIBRATION.md`"*.

**Both debts were written into the artifact, in advance, in the rung's own words —
and both rows still went unlanded until a human noticed, twice on 2026-09-03.**

> **The correction: caller-side evidence in the artifact is NECESSARY BUT NOT
> SUFFICIENT. A debt stated on line 902 of a registration nobody re-opens at
> completion is a caller-side proof with no reader.** The (d) gap here is not that
> the obligation is unstated; it is that **nothing reads the statement at the
> moment completion occurs**. Writing the obligation down does not let the path
> distinguish "the row was considered and not needed" from "nobody looked", which
> is §28's bar, so it does not clear §28's bar.

**No detector is proposed and none was built** — instrument-on-instrument work is
restricted, and this section is a read. What is recorded is that the allowed fix
was already in place and is measurably insufficient, so that whoever disposes of
this does not spend a cycle installing it a second time.

### F.5 Scope of this section, honestly

Two (d) specimens, from the same 29 comparators §1 names, plus the eleven files
§1 already lists as **pattern-scanned but unread** — which are unread for (d) as
well. **(d) had a lower hit rate in this family than predicted**, and the reason
looks structural rather than lucky: most of these comparators write their control's
**measured** outputs into the verdict JSON rather than a pass flag, and their
completion checks refuse on absence. The two that fail are the two that recorded a
**bare boolean** or **nothing at all**.

---

## G. DATED APPENDED SECTION — 2026-09-03T19:1xZ: **THE ELEVEN §1 NAMED AS UNREAD ARE NOW READ. SIX DEFECTS, NONE MOVING A VERDICT — BUT ONE OF THEM IS BOUND INTO THE READER THAT WILL ANSWER T3d's PREDICTION P-1 TONIGHT, AND IT SITS IN A FILE §1's OWN READ SET ALREADY COVERED**

**Appended, not merged.** Nothing above this line is altered: `lines whose number
changed above this section: 0`. Sections 0–F stand as written, including §1's
coverage claim and §F.5's scope statement — this section closes the gap §1 named,
it does not restate or renumber it.

**A CODE READ, like its parent. No instrument was built.** Predicate lines were
LOCATED by an AST walk over each file (every `If`/`While`/`Assert`/`IfExp`/
`Compare`/`BoolOp`/`not` node, printed with its line number and enclosing
function); **every judgement below was made by opening the file at that line and
reading the block.** The walk emits source text and makes no judgement — it is a
`grep` with better manners, not a checker, and no program here grades another
program. Sanaa's 20:00Z precondition is satisfied on the same footing as §A's.

**REPAIRS NOTHING. RE-GRADES NOTHING.** Every file named is frozen or has fired.
Rule 6 forbids editing them; a grading-path repair after first compute is
`VERIFICATION_CHARTER` §2d.1, verification's and not heat-transfer's. **Zero
compute: 0 core-min, $0.00 derived.** No gate, threshold, band, cap or label
created, moved or retired.

### G.1 COVERAGE — what was read, and the one arithmetic correction to §1's list

**All eleven files §1 names are read to conclusion.** Two bookkeeping facts about
that list, stated because they change what "eleven files" means on disk:

- `analyse_t9a.py` is **one file at two paths** — `T9a_runs/analyse_t9a.py` and
  `T9aH_runs/analyse_t9a.py` are byte-identical
  (`dd2d6bf0ac690fdcca90719cb6586168763d311ea3b5a7ad937fdf054ecac9da`).
- `analyse_k0b_mesh.py` is **two distinct files at three paths** —
  `K0b_mesh_sensitivity/` carries a 20 189-byte build
  (`f7821a9c…`) and `K0b_D403_rerun/` + `K0b_D406_repair/` carry an identical
  16 763-byte build (`bbe45d64…`). §1's singular name covers both; **both were
  read**, and the larger one carries the D407 `final_residuals()` block the
  smaller does not.

So: **twelve distinct source files, 1,579 predicate-bearing lines located and
read, across 12,480 lines of Python.** Nothing on §1's list is left unread, and no
file is being converted into a clean one by silence.

| file | lines | predicate lines | outcome |
|---|---:|---:|---|
| `T10a_runs/analyse_t10a.py` | 1 001 | 144 | 1 unreachable (d) shape; 1 SOUND form worth copying |
| `T16_runs/analyse_t16.py` | 1 015 | 170 | clean; 1 vacuous-`all` shape not reachable |
| `T23G_runs/analyse_t23g.py` | 1 090 | 77 | §B.1 confirmed by reading; 1 mild (d) |
| `T25R2_MODULE_runs/analyse_t25R2.py` | 2 759 | 308 | **2 defects** (G.2 **D-J5**, **D-J6**) |
| `T3_runs/analyse_t3.py` | 1 150 | 168 | **1 defect** (G.2 **D-J1**) |
| `T5b_runs/analyse_t5b.py` | 1 058 | 167 | clean; the family's best completion check |
| `T5c_runs/analyse_t5c.py` | 1 611 | 213 | clean; the family's best **(d)** prior art |
| `T9aH_runs/analyse_t9aH.py` | 798 | 108 | clean; a live planted convergence control |
| `T9a_runs/analyse_t9a.py` | 638 | 82 | **1 defect** (G.2 **D-J1**) |
| `K0b_mesh_sensitivity/analyse_k0b_mesh.py` | 474 | 40 | **3 defects** (**D-J2**, **D-J3**, **D-J4**) |
| `K0b_D403_rerun/analyse_k0b_mesh.py` | 393 | 29 | clean (has no residual block to get wrong) |
| `K2b_runs/analyse_k2b.py` | 493 | 73 | 1 observation (**D-J7**); `s13` is exemplary |

**What this section still cannot see, stated as §1 states its own gaps:** the
`selftest()` bodies were read only where a predicate line fell inside one or where
a production finding needed its arm checked; satisfiability was reasoned from the
code and, where an artifact existed, checked against it — where no artifact
exists, this section says so at the finding.

### G.2 THE SIX DEFECTS. **NOT ONE OF THEM MOVES A VERDICT**, and each says how that was established

---

#### **D-J1 — `analyse_t1c.py:229`, `analyse_t3.py:278`, `analyse_t9a.py:213` — the `rng == 0 → CONVERGED` limb. Fails (b), (c) AND (d). THREE FILES, ONE PREDICATE, AND ONE OF THEM IS LIVE ON A RUNNING GATE.**

```python
dmax = max(abs(x - y) for x, y in zip(a, b))
rng  = max(b) - min(b)
rel  = dmax / rng if rng > 0 else 0.0
return dict(state="CONVERGED" if rel <= tol else "NOT_CONVERGED", ...)
```

When the LAST checkpoint's field is spatially uniform — `max(b) == min(b)` — `rel`
is set to `0.0` **irrespective of `dmax`**. Two checkpoints differing by an
arbitrarily large *uniform* amount are therefore graded **CONVERGED**.

- **(b)** on that input the predicate cannot be made FALSE — `0.0 <= tol` for
  every registered `tol`.
- **(c)** the outcome is fixed by the guard's `else` branch, not by the data.
- **(d)** "the field never developed" and "the field stopped moving" return the
  same word. §28.4 requires that zero to REFUSE; it returns the best available
  verdict instead. `state="UNJUDGED"` already exists two lines above for exactly
  this purpose and is not used here.

**⚠ THIS IS BOUND INTO A GATE THAT IS RUNNING AS THIS IS WRITTEN.**
`analyse_t3d.py:80` reads `READER = A.T1C.iterative_convergence` — the T3d frozen
grading path takes its convergence reader from `analyse_t1c.py`. **T3d's
registered PREDICTION P-1 is precisely an iterative-convergence claim**
(`T3d_PREREGISTRATION.md:54–56`: relative change ≤ 1e-06 in `T` between the last
two checkpoints). The predicate that will answer P-1 has a branch that answers it
YES for free. **This is stated to the supervisor as a finding BEFORE the grading,
not after it.**

**IT HAS NOT FIRED, AND THAT IS MEASURED, NOT ASSUMED.** Every `field_range`
recorded in `T9a_runs/gate_t9a.json`, `T9aH_runs/gate_t9a.json` and
`T9a_runs/gate_t9aD.json` lies between **12.1236** and **49.9756** K. R_fx's
seeded `T` field carries R_ff's range, tens of K. **No published verdict moves,
and none is expected to.**

**THE NEAR MISS IS THE POINT.** `W_C3` — the C3 control case, whose whole
definition at `analyse_t9a.py:31` is *"a uniform-temperature solid"*, i.e. exactly
the input shaped to trip this limb — records `field_range = 5.2296e-12` (T9aH) and
`5.0022e-12` (T9a). **It missed the branch by five picokelvin.** Its `relative` of
0.3696 / 0.9091 is a ratio of two machine-noise quantities, so the control's
`NOT_CONVERGED` is rounding residue and not physics — **the `analyse_t15.py:501`
shape from §A.2 again**, here firing in the direction the control happened to
want. `W_C3`'s state is non-load-bearing (`analyse_t9a.py:484` collects it into
`bad`, which `:630` prints and `:634` excludes from the exit condition), so
nothing turns on it either way.

**THE PLANTED CONTROL DOES NOT COVER THIS BRANCH, AND THAT IS THE (d) LESSON IN
ONE ARTIFACT.** T9aH's `RC5_planted_convergence_*` is a real, live planted control
— it plants 1.234e-03 into `T`, and `analyse_t9aH.py:429–430` asserts BOTH that
`max_change` equals the plant to 1e-12 AND that the state flipped to
`NOT_CONVERGED`; the artifact records it fired
(`field_range` 49.80/49.98, `max_change` 0.0012340000000108375, `relative`
2.4779e-05 / 2.4692e-05). **But the plant leaves `field_range` at ~50 K, so it
exercises the `rng > 0` branch only.** The control proves the reader can see a
change. It never reaches the branch that would pass in silence. *§28.3's sentence,
measured: this control proves the instrument CAN fail, and says nothing about
whether the failing path was ever entered.*

**THE FAMILY ALREADY KNOWS THE RIGHT FORM.** `analyse_t10a.py:372` writes
`state="CONVERGED" if dmax == 0.0 else "NOT_CONVERGED"` — byte-exact identity, no
division, no fallback, no degenerate input to fall through.

**AND THIS IS A GAP IN §1's OWN READ, NAMED AGAINST THIS TEAM'S INTEREST.**
`analyse_t1c.py` is **not** one of the eleven. It sits inside §1's 704-line
*read* set ("T-family, part 1", `T1c`). The instance was there to be found and was
not found. **704 predicate lines is a count, not a coverage proof** — which is the
same distinction §1 was written to make about the eleven, arriving from the other
side.

---

#### **D-J2 — `K0b_mesh_sensitivity/analyse_k0b_mesh.py:256` — `terminated_by` asserts `endTime` from an ABSENCE. Fails (d).**

```python
"terminated_by": ("residualControl"
                  if "SIMPLE solution converged in" in text else "endTime"),
```

Only the `residualControl` branch is read from the solver's own line. `endTime` is
inference from a **missing substring**, so a run that was killed, capped,
SIGTERMed or crashed is recorded as having run to `endTime` — a positive claim
manufactured out of no evidence. **The function's own docstring (`:200–202`) states the
opposite in as many words:** *"`terminated_by`, read from the solver's own line
rather than inferred"*. That is true of one branch and false of the other, and the
docstring is what a reader will believe. **Face 3 of §28.2 with a caption.**

---

#### **D-J3 — same file, `:247` with `:250–251` — a field nobody could check is invisible in the output. Fails (d).**

```python
"met_target": (resid <= tgt) if tgt else None,
...
met   = sorted(f for f, d in per_field.items() if d["met_target"] is True)
unmet = sorted(f for f, d in per_field.items() if d["met_target"] is False)
```

A field whose `residualControl` target could not be read gets `met_target=None`
and lands in **neither** list. `fields_not_meeting_target: []` is therefore emitted
both when every field met its target and when **no field had a target at all** —
the two states §28.4 says must never share a representation. `if tgt` compounds it:
it is a truthiness test on a float, so a legal `residualControl` entry of `0` is
swallowed by the same branch as a missing one.

**Reachability, measured on disk:** both committed legs declare
`p_rgh 1e-07; U 1e-08; T 1e-08;` and the solve is laminar — `Ux Uy T p_rgh`, all
four covered by `target_for()` including its `U`-governs-components rule at `:236`.
**Every solved field currently has a target, so this has not fired.** A turbulent
variant adding `k`/`omega` would fire it silently.

---

#### **D-J4 — same file — THE D407 WARRANT HAS NEVER BEEN PRODUCED FOR THE LEGS IT WAS WRITTEN FOR. Face 3 and (d), and the most instructive of the six.**

`measure()` returns `convergence=final_residuals(case)`, and `final_residuals()`
returns a dict on **every** path — `{"measured": False, "why": …}` when no log is
found, `{"measured": True, …}` otherwise. It can never return nothing.

**The published `k0b_mesh_sensitivity.json` carries NO `convergence` key at all,
in any of its three legs (`32x32`, `64x64`, `128x128`).** Not `null`, not
`measured: false` — absent.

The explanation is on the mtimes and in the log: the artifact was written
**2026-08-17 16:30**; the comparator was repaired **2026-08-18 18:32** by commit
`d9475c07`, whose subject is *"D407: the convergence warrant was a comment, so no
run could contradict it"*. **The repair landed and the comparator was never
re-run.**

> The D407 commit moved the warrant out of a comment and into code so that a run
> could contradict it. **The code has still never been executed for these legs, so
> the warrant is still uncontradictable — for exactly the same reason, one level
> down.** Nothing in the artifact distinguishes "the convergence check ran and had
> nothing to say" from "the convergence check has never run".

**No verdict moves:** the artifact's own header declares
`not_a_validation: "K0b is a capability rung graded against no published datum"`,
so there is no gate here to flip. What is gone is the evidence D407 believed it
had installed.

---

#### **D-J5 — `analyse_t25R2.py:1438` — `all()` over an EMPTY `zip`. Fails (b) and (d), and its neighbours prove it is an oversight and not a choice.**

```python
outs, ins = [], []
for t in _written_times(case_dir):
    if t <= 0.0:
        continue
    outs.append((t, read_patch_T(case_dir, t, "outlet", mc)))
    ins.append((t, read_patch_T(case_dir, t, "inlet", mc)))
d2 = all(o[1] > i[1] for o, i in zip(outs, ins))
```

`_written_times` (`:1444–1449`) refuses only when there are **no** time directories
at all. A case holding only `0/` survives that refusal, every entry is then dropped
by `if t <= 0.0: continue`, `zip` is empty, and **`all()` of nothing is `True`**:
**D2 passes having read zero data.** It feeds straight into `:1814`
`gates_ok = eb["ok"] and ac["D1"] and ac["D2"] and ac["D3"]` → `:1815`
`verdict = "PASS" if gates_ok else "GATE FAIL"`.

**The two lines above it behave correctly on the same degenerate input.** D1
(`:1430`) and D3 (`:1431`) iterate `range(N_CELLS)`, a fixed 8, and `min(diff)`
would raise loudly on an empty list. **The file refuses loudly on one degenerate
input and passes silently on the one beside it, three lines apart.**

**No verdict moves, and the reason is uncomfortable:** the path is unreachable in
production only because `read_updown(case_dir, T_PULSE, mm)` at `:1428` runs FIRST
and would fail to find `T_PULSE` on a `0/`-only case. **The protection is statement
ORDER, not a guard** — which is question (c) exactly. Reorder those four lines for
any reason and the silent pass becomes live.

---

#### **D-J6 — `analyse_t25R2.py:1671–1672` — a verdict-vocabulary distinction decided by a substring of a prose message. Fails (c).**

```python
blocked  = [x for x in oc_ready if "no case directory" not in x[1]]
oc_state = "NOT A RESULT" if blocked else "PENDING"
```

`x[1]` is a human-readable reason string. **The split between `PENDING` and
`NOT A RESULT` — a distinction `CLAUDE.md` rule 1 fixes and
`VERIFICATION_CHARTER` §9 governs — is decided by whether that prose happens to
contain the phrase `"no case directory"`.** Reword the message anywhere it is
produced and the classification flips with nothing in the diff to show it.
`oc_state` then propagates to `:1719` and `:1732–1734`, where it decides whether
graded rows read `NOT A RESULT` or `PENDING`. No verdict moves today; the coupling
is invisible to every check the rung has.

---

#### **D-J7 (OBSERVATION, not a defect row) — `analyse_k2b.py` refuses loudly where a value exists and omits silently where it does not.**

`s13` (`:183–245`) is the best null-refusal in this family and is quoted here so
the contrast is exact: it returns `verdict="REFUSED"` with `resolved_ulp`,
`run_range` and `print_resolution`, and its reason **names the score it would
otherwise have returned** — *"Scoring it against the mean would have returned
{pct_vs_mean:.6f} % — a PASS."* That is §28.4 answered in the artifact.

The same file's optional sections do the opposite. `mass_ledger` (`:356`) and the
`if tin and tout_m:` / `if tin and tout_a:` / `if tin and tin_a:` / `if umax:` /
`if tret:` / `if yplus:` / `if g:` family (`:309`, `:329`, `:346`, `:366–373`)
**drop their whole section from the record** when an input is missing, and
`emit`'s matching `if m:` / `if b:` / `if o:` / `if c:` / `if a:` prints nothing.
No `NOT MEASURED` line is written. A reader of the report cannot tell "the mass
ledger closed" from "the mass ledger was never computed".

**Checked and cleared inside the same finding:** `mass` (`:354`) is a dict
comprehension over a fixed 4-tuple of patch names, so `all(v is not None for v in
mass.values())` at `:356` is **not** vacuous — the empty-`all` hazard does not
apply there. **Reachability on disk NOT DETERMINED:** the analyser's JSON output is
optional (`--json`, `:485`) and no such artifact was found beside `K2b_runs`. This
is recorded as unresolved rather than as clean.

---

#### **D-J8 (OBSERVATION) — `analyse_t23g.py:723–725` — a control met by mutual absence, and a tolerance that goes absolute below unity. (d), mild.**

If the dT shift yields `None` for both `order` and `GCI_abs` — which a
non-CONVERGING triple does in both framings — then `(a is None) != (b is None)` is
False and `a is not None` is False, so the shift-invariance assertion passes
**having compared nothing**. The state comparison at `:717` is substantive and
fires first, so the residual exposure is small. Separately, `shift_invariant`
(`:224`) reads `abs(a - b) <= RTOL * max(1.0, abs(a), abs(b))`: the `max(1.0, …)`
floor makes the tolerance **absolute** for any quantity below unity, so the
control weakens toward unfalsifiable on small values.

**§B.1 confirmed by reading, not by scan.** `analyse_t23g.py:407`
(`if at_plant < 0.1 * PLANT:`) is present and is fully subsumed by
`:404`'s `if not (at_plant >= PLANT * (1.0 - 1e-9)):`, exactly as §B.1 records it
from the scan. The scan's finding survives the read.

### G.3 CLEARED — read, suspected, and found SOUND, so a successor does not spend the cycle

Recorded in the same spirit as §C. Several of these are lines this read expected to
be defects and was wrong about; saying so is the point.

1. **`analyse_t9a.py:418`** `if conv["state"] not in ("CONVERGING", "EXACT")`. This
   read initially suspected a type mismatch: `iterative_convergence` (`:214`) can
   only ever emit `CONVERGED` / `NOT_CONVERGED` / `UNJUDGED`, none of which is in
   that tuple, which would have made the row **always** NOT A RESULT. **Wrong** —
   `conv` here comes from `gci()` (`:227–252`), whose domain is
   EXACT/OSCILLATORY/DIVERGENT/STAGNANT/CONVERGING. Sound.
2. **`analyse_t23g.py:806`** `if extras[g]["verdict"] == "GATE FAIL" and worst ==
   "PASS"`. Suspected: a `GATE REACHED` value of `worst` would swallow an extras
   GATE FAIL. **Not reachable** — `worst` is seeded at `:748` from
   `RT.grade_ladder`, whose verdict domain is exactly {PASS, GATE FAIL, NOT A
   RESULT} (`scripts/roache_triple.py:614`, `:622`, `:636`; `band_verdict:535`
   returns only PASS or GATE FAIL), and the NOT-A-RESULT case takes the explicit
   `NOT EVALUATED` branch at `:750`. The guard is complete over the reachable
   domain.
3. **`analyse_t9aH.py:196` `collapse_fired` and `:199–209` `discrimination`** —
   both are `all()`/comprehension shapes that are vacuous on empty input.
   **Not reachable:** the only production call sites pass a fixed 3-key dict
   literal (`:515–520`) and a list built over a fixed `LEVELS` (`:544`).
4. **`analyse_t10a.py:566–568`** — `m["void"]` has an `else: m["void"] = False`
   arm, i.e. "the closure check did not run" recorded as "not void", the PASS
   direction, feeding `:594 if voided:`. **Not reachable:** `want_F` defaults
   `True` (`:451`) and the only production call passes `want_F=True` (`:820`).
   Selftest-only. Worth knowing it is one keyword argument away from live.
5. **`analyse_t16.py:395–399`** — `missing = [f for f in gated if worst[f] is
   None]` **refuses before** `bad = [f for f in gated if worst[f] > CONV_FLOOR]`,
   so an unread residual can never reach the comparison. (d)-sound. (`:331`
   `T_monotone = all(...)` is vacuous on a one-cell row, but `N` is mesh-fixed and
   `:224` refuses a mismatched `Ny`.)
6. **`analyse_t5b.py:172–184` `_l342_class`** falls through to **`"UNCLASSIFIED"`**,
   not `"INFRASTRUCTURE"`. A newly added field name cannot silently become
   non-gating. This is the fail-open direction taken deliberately the other way.
7. **`analyse_t5b.py:418–482` and `analyse_t5c.py:370–430` `check_completion`** —
   all six clauses of `CLAUDE.md` rule 4, age guard included
   (`getmtime(field) <= mtime(0/T)`), plus `FOAM FATAL` / `Signal:`. The selftest
   **FORGES** each failure mode — `rc=1`, no `End`, short `ExecutionTime` count,
   absent fields, stale mtime, FOAM FATAL — and asserts NOT COMPLETE for each
   (`t5b:906–912`), then separately asserts the record says `INFERENCE` and
   `NOT MEASURED` where it inferred (`:916–918`). **This is question (d) answered
   properly: the check is proven able to say "did not run", by making it say it.**
8. **`analyse_t5b.py:810–811` / `analyse_t5c.py:1390–1391`** —
   `idok = abs(rv - LO) >= MARGIN and abs(rv - HI) >= MARGIN`, refusing a reference
   that sits ON a band boundary. **This family already wrote the defence against
   `analyse_t15.py:501`** — the defect §A.2 measured at 1.076e-14 relative excess.
   It exists in T5b/T5c and not in T15.
9. **`analyse_t5c.py:1143–1157` with `:1170–1183`** — `read_level_statistics`
   returns `(None, why)` if ANY registered wall is unreadable, and
   `gate_yplus_t5c` iterates the fixed `YPLUS_WALLS`. The explicit `missing` check
   T5b needs at `:378` is enforced structurally upstream instead. **An improvement
   over T5b, not the regression this read went looking for.**
10. **`analyse_t5c.py:879–892` `report()`** — refuses when `self.positive is None or
    self.negative is None`: **a control lacking either a positive OR a negative arm
    cannot be reported as passed.** This is §28.4's operational test implemented in
    code, and it is the strongest (d) prior art in the family.
11. **`analyse_t5c.py:1591`** — `ok(sys.flags.optimize == 0, …)`: the file refuses
    to run under `python -O`, where every `assert` silently vanishes. A direct,
    cheap defence against "the check did not run".
12. **`analyse_t25R2.py:391 clear_pycache`** (the stale-`__pycache__` inversion) and
    **`:403–421 freeze_check`** (worktree bytes hashed against the committed blob),
    plus the **AST self-scan at `:2258–2267`** proving no residual-gate name is bound
    in its own source. Three different "did this actually run as written" defences
    in one file.
13. **`analyse_t3.py:612–616`** — `within_tolerance` is `False`, not absent, when
    `imbalance_pct` is None (`Q_wall == 0`): it refuses in the safe direction.
    **`:692`** — `conv_states.get(l) != "CONVERGED"` treats a MISSING level as bad.
    **`:549`** — `St` is `float("nan")`, not `0.0`, when `T_w == T_in`.
14. **`analyse_k0b_mesh.py:350`** — the `nu_at_time(...)` vs `mean(nu_hot)` assert is
    **not** an identity: `nu_at_time` (`:179`) uses the x-fastest shortcut
    `T[j*nx]` while `measure` uses the `writeCellCentres` `xi`/`yi` mapping. Two
    independent index derivations; the assert can genuinely fail. Sound.

### G.4 THE SHAPE OF THE SIX, SINCE SIX IS ENOUGH TO NAME ONE

Five of the six are the **same arithmetic sentence**: *a guard that exists to avoid
a division by zero, or an empty iterable, silently substitutes the value that
grades BEST.* `rng > 0 else 0.0` (D-J1). `if tgt else None` dropped from both
tallies (D-J3). `all()` of an empty `zip` (D-J5). `else: void = False` (cleared
item 4). `else "endTime"` (D-J2) is the same move in string form.

**The correct substitution is already written in this family, five times over** —
`float("inf")` in `analyse_k2b.py:209`, `analyse_k2b.py:210`,
`analyse_t16.py:317`, `analyse_t16.py:579`, `analyse_t5b.py:698`, and `nan` in
`analyse_t3.py:549`. All six choose a value that **cannot pass**. The six defects
above choose one that cannot fail. Nothing separates the two groups except which
constant the author reached for at a guard nobody expected to be taken.

*No class is declared and no sweep is ordered. Six instances in twelve files is a
pattern worth naming; it is not a measurement of the other four teams, and this
section does not make one.*

### G.5 WHAT THIS SECTION DOES NOT DO, AND THE ONE THING IT HANDS UPWARD

- It does **not** repair, re-grade, withdraw or re-run anything, and it edits no
  file named in it.
- It does **not** move a gate, band, threshold, cap or label.
- It does **not** claim any of the six moves a verdict. **None does.** Where that
  was established against an artifact it says so and names it; where it was
  reasoned from code alone (D-J5, D-J6, D-J7) it says that instead.
- It does **not** build a detector. Instrument-on-instrument work is restricted and
  the parent §F already records that the allowed fix is insufficient.
- It authorises no send. **SUBMISSIONS REMAIN PARKED** (rule 7).

**The one thing handed upward, and it is time-critical:** **D-J1 is bound into
`analyse_t3d.py:80`, the frozen grading path of the T3d continuation now running in
`R_fx` (endTime 24 000, ETA ~2026-09-04T03:48Z).** The predicate that will answer
its registered PREDICTION P-1 has a branch that answers P-1 YES on a degenerate
field. On the evidence — every `field_range` in this ladder is tens of kelvin —
that branch will not be taken. **The supervisor should know that before the row is
graded rather than after, and this is a finding, not a request to touch the run.**
