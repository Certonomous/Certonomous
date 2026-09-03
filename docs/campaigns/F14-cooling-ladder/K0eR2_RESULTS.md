# K0eR2 — RESULTS

**Rung:** K0eR2, DC-cooling / F14 cooling ladder — forced-convection flat plate,
`beta`/`g` neutralisation test.
**Frozen registration:** `docs/campaigns/F14-cooling-ladder/K0eR2_PREREGISTRATION.md`,
`prereg_commit f306ce662d2ce205f6fb70dd407e9248e1d7c03b`, committed before any
K0eR2 compute.
**Graded:** 2026-09-03, by one pinned invocation of `scripts/analyse_k0e.py`.

---

## 1. THE VERDICT

# `NOT A RESULT`

| row | verdict | figure |
| --- | --- | --- |
| **M4b** — the ONLY gated row | **`NOT A RESULT`** | **not measured** — `NOT DONE` under the strict completion rule: `FP_T00` |
| **RUNG** | **`NOT A RESULT`** | — |

**Verbatim from the grader's stdout**, landed at
`verification/runs/F14-cooling-ladder/K0eR2_runs/K0eR2_GRADE_STDOUT.txt`:

```
M4b      NOT A RESULT   NOT DONE under the strict completion rule: FP_T00
RUNG     NOT A RESULT
```

**THE VERDICT IS TAKEN FROM STDOUT AND THE VERDICT ARTIFACT, NEVER FROM THE EXIT
CODE. The grader exited `rc = 0` on this `NOT A RESULT`** — the standing trap in
this family, which fired on T16c the same evening (rc 0 on four `NOT A RESULT`
rows). A reader who scripts against `$?` here reads success.

**No ULP figure exists for M4 or M4b.** Neither comparison was reached. §8.2's
both-arms requirement returns before the comparison
(`scripts/analyse_k0e.py:757-761`), exactly as designed: *a gated row that cannot
be measured cannot yield a `PASS`.*

**`GATE FAIL` was unreachable by construction** and is not the verdict here: no
band is armed anywhere in this rung (§0 `:25-27`). The reachable verdicts were
`PASS` (M4b at 0 ULP) or `NOT A RESULT`, and the registration named this exact
outcome in advance — §0 `:25` registers `NOT A RESULT` for "M4b non-zero, **or a
completion clause failed on either arm**". Five failed. **This verdict was
pre-registered, not invented after the fact.**

---

## 2. STRICT COMPLETION RULE (standing rule 4) — PER ARM, FROM ARTIFACTS

### 2.1 `FP_T10` — DONE, all six conjuncts hold

| clause | verdict | artifact evidencing it |
| --- | --- | --- |
| 1. `rc = 0` | PASS | `K0eR2_runs/STATUS.FP_T10`: `rc=0`, `reconstruct_rc=0`, `cellcentres_rc=0`, `note=clean` |
| 2. `End` line | PASS | exactly one `End` in `FP_T10/log.solve` |
| 3. last time == `endTime` | PASS | last `Time = 9000`; `FP_T10/system/controlDict` `endTime 9000` |
| 4. fields at `endTime` | PASS | `T U p_rgh alphat nut k omega` all present in `FP_T10/9000/` |
| 5. `ExecutionTime` count == `endTime` | PASS | 9000 lines; final `ExecutionTime = 2813.03 s  ClockTime = 2843 s` |
| 6. age guard | PASS | `FP_T10/0/T` mtime 1788464813; every `9000/` field 1788467656–57 — **2843–2844 s newer** |

### 2.2 `FP_T00` — NOT DONE, five conjuncts fail outright

| clause | verdict | artifact evidencing it |
| --- | --- | --- |
| 1. `rc = 0` | **FAIL** | `K0eR2_runs/STATUS.FP_T00`: `rc=124`, `wall=3151`, `timeout_s=3150`, `note=CAP_EXPIRED_or_child_exit_124` |
| 2. `End` line | **FAIL** | zero `End` lines in `FP_T00/log.solve`; it ends mid-`Time = 350` at `mpirun: Forwarding signal 18 to job` |
| 3. last time == `endTime` | **FAIL** | last `Time = 350` ≠ 9000 |
| 4. fields at `endTime` | **FAIL** | **no `FP_T00/9000/` directory exists**; the case holds `0/` only |
| 5. `ExecutionTime` count | **FAIL** | 349 ≠ 9000 |
| 6. age guard | PASS — **VACUOUSLY** | see §2.3 |

### 2.3 An observation on clause 6, recorded because it would be invisible otherwise

**Clause 6 reports `PASS` on `FP_T00`, and that PASS is vacuous.** At
`analyse_k0e.py:501-506` the guard builds `older` by filtering `REQUIRED_FIELDS`
on `field_path(tdir, f)` being truthy. With no `9000/` directory every
`field_path` returns `None`, `older` is empty, and the clause reports
`PASS every endTime field newer than 0/T` — **over an empty set.**

**This changes no verdict and is not asserted as a defect.** Clause 4 fails on
exactly the same missing fields and `ok` is `False` regardless, so the guard is
never load-bearing alone. It is recorded because *the age guard cannot, by
itself, detect a missing `endTime` directory*, and a future reader who leans on
clause 6 as an independent check should know it is only meaningful when clause 4
has already passed.

### 2.4 The age-guard datum, verified at source rather than accepted

Rule 4 dates a run from `<case>/0/T`, which is valid **only** if the launcher
touches that file last. **That ordering claim was checked in the launcher, not
taken on trust:**

- `scripts/launch_k0e.sh:117` — `touch "$CASE_DIR/0/T"` — stands immediately
  before the solver at `:121`, under the header comment at `:19-20`
  ("touch 0/T — LAST, immediately before the solver starts").
- `:114` refuses the case outright if `0/T` is absent after the build, so the
  guard can never run without a datum.

**Corroborated empirically on both arms:** `FP_T10/0/T` mtime 1788464813 =
2026-09-03T19:46:53Z, which is that arm's `started_utc` **exactly**; `FP_T00/0/T`
= 20:46:29Z, its `started_utc` **exactly**. The launcher's claim and the disk
agree.

---

## 3. WHY `FP_T00` DID NOT COMPLETE — TRIAGE

**`FP_T00` was killed by its registered cap**: `rc=124`, `wall=3151` against
`timeout_s=3150`, started 20:46:29Z, ended 21:39:00Z, having reached **iteration
350 of 9000**.

**The loss is total and there is no restart point.** `writeInterval 9000`, so
nothing is written before the end: `FP_T00/` holds `0/` only, and
`processor0/`, `processor1/` hold `0` and `constant`.

### 3.1 The two arms differ in exactly one line

`diff -r` over `0/`, `constant/` and `system/` returns **a single difference**:

```
FP_T00/0/T:39   plate  value  uniform 300
FP_T10/0/T:39   plate  value  uniform 310
```

Same binary, same 52,224-cell mesh, same dictionaries, same decomposition, same
rank count. **That one line is the entire cause.**

### 3.2 The mechanism — THE READING THE EVIDENCE SUPPORTS, NOT AN INSTRUMENTED MEASUREMENT

In `FP_T00` the `0/T` field sets `internalField uniform 300`, inlet `fixedValue
300` and plate `fixedValue 300`, with `zeroGradient` at outlet and top and
`symmetry` at the bottom. **`T ≡ 300` is therefore simultaneously the initial
condition and the exact steady solution.** The temperature equation is satisfied
to machine precision before the first sweep; OpenFOAM's residual normalisation
factor degenerates to round-off; and the normalised residual the solver reports
and tests against tolerance is **a ratio of two round-off quantities.**

The evidence, all from `FP_T00/log.solve` and `FP_T10/log.solve`:

1. **All 349 T solves in `FP_T00` hit `No Iterations 1000`** — the smoothSolver's
   default iteration cap. No `maxIter` is registered;
   `FP_T00/system/fvSolution:20-26` gives `"(U|k|omega|T)"` → smoothSolver,
   symGaussSeidel, `tolerance 1e-10`, `relTol 0.01`.
2. **The very first solve reads `Initial residual = 0.5053587649, Final residual =
   0.6092429219` — the final residual is LARGER than the initial.** A genuinely
   converging linear solve on a well-posed system cannot do that. It is the
   signature of round-off-level arithmetic under a degenerate normaliser.
3. **The control arm settles the question.** `FP_T10`, same binary, same mesh,
   same dictionaries, ran **9000** T solves with **zero** hitting the 1000
   cap — they converge in 2–3 iterations, and the initial residual falls to
   `8.18e-08`.

**HONEST LIMIT, AND IT IS KEPT RATHER THAN QUIETLY DROPPED: `normFactor` was NOT
instrumented.** The mechanism above is the reading these three observations
support; it is not a measurement of the normaliser, and no claim is made that it
was measured.

### 3.3 The cost consequence, measured

1000 symGaussSeidel sweeps per outer iteration on 52,224 cells instead of ~3:

| | `FP_T10` | `FP_T00` |
| --- | ---: | ---: |
| iterations completed | 9000 | 349 |
| final `ExecutionTime` | 2813.03 s | 3137 s |
| **s / iteration** | **0.3126** | **8.99** |

**A factor of 28.8 — and the rate is flat, not improving.** Successive
`ExecutionTime` deltas across the run run 8.85, 8.91 and 9.08 s/it. There is no
convergence trend that a longer run would have caught.

**Extrapolated to 9000 iterations, `FP_T00` needs ~80,900 s ≈ 2,696 core-min:
25.7× its own registered 105.00 core-min ceiling, and 12.8× the whole rung's
210.30 core-min ceiling.**

**THERE IS NO VERSION OF THIS RUNG, UNDER ITS REGISTERED CEILING, IN WHICH
`FP_T00` FINISHES AS CONFIGURED.**

### 3.4 The cap worked, and that is recorded as a success of the rule

The cap **stopped a run that could never have completed** rather than buying it a
new budget — `CLAUDE.md` rule 12 doing precisely its job. `timeout 3150` s at 2
ranks is the registered 105.00 core-min per-arm ceiling converted by the
launcher's own documented rule (`launch_k0e.sh:39`: *cap_core_min × 60 / ranks*).

**And the cap could not have been widened in any case.** K0eR2 has had first
compute, so under `CLAUDE.md` rule 2 its gates, thresholds, caps and labels are
closed, and a dated addendum may not move one.

---

## 4. ⚠ THE FINDING THAT MATTERS MOST — A DESIGN CONFLICT, NOT A TUNING PROBLEM

**The property that makes `M4b` a valid neutralisation test is that the two arms
are identical in every operator and every setting except the wall temperature.**
That identity is what cancels the discrete-operator confound exactly, and it is
the whole evidentiary basis of the comparison.

**That same identity is precisely what makes the zero-dT arm degenerate.** The
control arm is defined by setting the plate temperature equal to the ambient,
inlet and reference temperature — which is exactly the condition that makes its
temperature equation exactly satisfied at initialisation, and its residual
normaliser degenerate.

**The two requirements are in direct conflict:**

- **Any fix that makes `FP_T00` runnable by changing its solver settings — adding
  a `maxIter`, loosening a tolerance, freezing or disabling the T equation —
  BREAKS the same-operator-set premise that `M4b` depends on.** The arms would
  no longer differ in one line, and the comparison would no longer isolate what
  it claims to isolate.
- **Any fix that preserves the premise leaves the degeneracy in place**, and the
  control arm remains uncompletable within any sane budget.

**A SUCCESSOR MUST RESOLVE THIS AT THE LEVEL OF THE CONTROL'S DESIGN, NOT BY
TUNING A DICTIONARY.** This is the transferable content of the rung, and it is
stated here so that no successor spends another 105 core-min discovering it by
running into the same cap.

---

## 5. THE M4b GATED QUANTITY — A THREAT CHECKED AND CLOSED

The 349,000 round-off-level symGaussSeidel sweeps churn `T` at round-off
amplitude. **If `T` could reach the momentum equation, that churn would move `U`
and would be indistinguishable from exactly the `beta`/`g` leak that `M4b`
exists to detect.** The threat was checked rather than assumed:

- `constant/transportProperties` reads **`beta 0`** in **both** arms.
- `constant/g` reads **`value (0 0 0)`**.

**Two independent closed routes.** The thermal field cannot enter the momentum
equation at all, so the degenerate T solve cannot contaminate the gated
quantity. The M4b premise registered at `:238-244` holds. This does not rescue
the rung — the arm still did not complete — but it means the failure is one of
completion, not of contamination.

---

## 6. THE REGISTERED READING OF M4b / M4, CARRIED BUT NOT EXERCISED

Registered at `:242-244`, quoted so the reading is not invented afterwards:

> **`M4b` at 0 ULP with `M4` non-zero is the signature of the operator
> difference and of nothing else.** `M4b` non-zero is a `beta`/`g` leak, whatever
> `M4` reads.

**Neither figure was produced.** The comparison was never reached. This reading
stands armed for a successor and is discharged by nothing in this record.

---

## 7. CONTROLS — WHAT WAS AND WAS NOT EXERCISED

### 7.1 The three planted-zero controls (standing rule 3) — **NOT EXERCISED**

**THIS RUNG CARRIES NO PLANTED-CONTROL EVIDENCE, AND THAT IS STATED PLAINLY
RATHER THAN LEFT TO INFERENCE.**

The three registered plants (§8.1) — P1 `1.234e-03` K through the production
**scalar** reader, P2 `1.234e-03` m/s into the **X-component** through the
production **vector** reader, P3 exactly `0.0` as the negative control that must
**not** fire — are implemented at `analyse_k0e.py:364-440` and invoked at
`:771`.

**`:771` is AFTER the both-arms early return at `:757-761`.** On a `NOT DONE`
arm the plants are **structurally unreachable**, and the grader's stdout contains
no `PLANTED-ZERO CONTROLS` section at all.

**This is correct ordering, not a defect:** the completion gate properly precedes
the comparison, because a gated row that cannot be measured cannot yield a
`PASS`, and there is nothing to plant into when the graded comparison never runs.
But it means **no claim of a demonstrated reader is available for this rung**,
and none is made here. P2's separate existence — *a scalar plant does not
exercise a vector reader, and the gated row reads vectors* — remains registered
and remains undischarged.

### 7.2 The orthogonality refusal (§8.4) — **NOT EXERCISED**

The grader's `max_non_orthogonality` refusal path (`analyse_k0e.py:594-603`,
which refuses if `constant/birth_certificate.json` is absent or carries no such
field or a non-zero value) sits inside the M-row computation, well after the
early return, and was not reached.

**Read directly from disk for this record, and NOT through the grader:**
`FP_T10/constant/birth_certificate.json` carries `"max_non_orthogonality": 0.0`
and `"cells": 52224`. The mesh datum is what the registration says it is — **but
the grader's refusal path did not run, and this record does not claim it did.**

### 7.3 The grader pin — **ARMED AND MATCHED**

`--expect-sha` was armed, per `:473` — *"The grade is only valid with
`--expect-sha` armed."* The flag is optional to argparse (`:937`), so omitting it
would have silently disarmed the check; it was not omitted.

`git hash-object scripts/analyse_k0e.py` =
**`25ecaa6bca8cd99f4ca1e0a84dba998cde923aaa`**, matching the registered pin
exactly. Re-confirmed in the same shell invocation immediately before the run.
The value is a **git blob SHA-1**, not a sha256 (`:465-467`).

**One invocation was made. The grader was not re-run.**

---

## 8. NO ROACHE TRIPLE — RULE 5 DOES NOT ENGAGE

**Registered at §8.3, and recorded here as the registration requires:** K0eR2 is
two arms on **one** 52,224-cell mesh. There is no grid triple, and **none may be
invented.**

**Standing rule 5 does not engage. NO GCI IS COMPUTED AND NONE IS QUOTED. No
observed order of accuracy is computed or quoted.**

**EVERY K0eR2 NUMBER CARRIES NO DISCRETISATION BOUND AT ALL.** Any figure taken
from this rung — including any figure a successor lifts from it — is a
single-mesh number with no grid-convergence evidence behind it whatsoever.

---

## 9. THE REPORTED ROWS — **REPORTED, NOT GATED**

M1 (Stanton), M2 (`Cf`), M3 (`Prt_eff`), M5 and M6 are **REPORTED rows, never
gated** (§0 `:26`: *a `PASS` on the Stanton comparison* is unreachable by
construction; §5.1: *`M4` is now REPORTED, NOT GATED*).

**None of them carries a figure in this record.** The grader returned before any
M row was computed, so no value exists for any of them. They are named here so a
reader sees that they were owed and are absent, rather than finding silence.

**M4b was the ONLY gated row in this rung**, its threshold was **0 ULP**, and it
is `NOT A RESULT`.

---

## 10. RULE 12 — ESTIMATE VERSUS ACTUAL

### 10.1 The figures

| | POINT | CAP / ceiling | actual | ratio |
| --- | ---: | ---: | ---: | ---: |
| `FP_T10` | 35.00 | 105.00 | **94.77** | 2.708 |
| `FP_T00` | 35.00 | 105.00 | **105.03** | 3.001 |
| **RUNG (solver)** | **70.10** | **CEILING 210.30** | **199.80** | **2.8502** |

Basis: `wall s × ranks ÷ 60`. `FP_T10` = 2843 × 2 ÷ 60 = 94.767. `FP_T00` =
3151 × 2 ÷ 60 = 105.033. Both wall figures from the arms' own `STATUS` files,
and both corroborated by their `started_utc`/`ended_utc` stamps.

**Dollars: POINT `$0.05993`, actual `$0.17083` — DERIVED at the owner-stated
c7a.4xlarge rate of $0.0513/core-h, `cost_basis` REPORTED-BY-OWNER, NEVER
MEASURED.** This box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**The grader's own cost is not separately instrumented.** Its registered POINT is
0.10 core-min against a 0.30 cap; the single invocation returned in ~1 s wall at
1 rank, so it is bounded far below its point, but that is a bound, not a
measurement, and it is not entered as one.

### 10.2 WASTE — NAMED SEPARATELY, NEVER FOLDED INTO THE RATIO

**`FP_T00`'s 105.03 core-min is WASTE** under `COMPUTE_BUDGET_CHARTER.md` §6: a
total loss, zero fields written, no restart point, nothing recoverable.

**BOTH FIGURES ARE STATED SO A READER SEES THE WHOLE PICTURE:**

- **Total rung spend: 199.80 core-min.**
- **Of which bought nothing: 105.03 core-min — 52.6 %.**
- **Productive spend: 94.77 core-min** (`FP_T10`, complete and usable).

**The ratio is NOT quietly computed on the productive arm alone, and the waste is
NOT quietly absorbed into the total.** The rung ratio 2.8502 is the honest
all-in figure against the registered POINT; the 52.6 % waste share sits beside
it, named, and is not netted out of either column.

**The 0.03 core-min over the 105.00 ceiling is the one second of `TERM` handling**
(`wall=3151` against `timeout_s=3150`) **and must not be read as an overrun.**
The cap fired and stopped the run; it did not fail to hold.

### 10.3 ATTRIBUTION — TWO DIFFERENT CAUSES, AND THEY ARE NOT MERGED

**The rung ratio 2.8502 mixes two unrelated failures, and collapsing them into one
explanation would be false.**

**(a) `FP_T10`, ratio 2.708 — a LOW BASE ESTIMATE, with a measured contention
confound.** The registered `cost_basis` (§7.1) applied a **1.25×** solver factor
to a **28.00 core-min** `simpleFoam` reference on this exact mesh, itself flagged
in the registration as *"an ESTIMATE, not a measurement"* (segregated solves 6 →
7 for `+T`, i.e. 1.167, rounded up for `alphaEff` and `alphat`). **The measured
multiplier is 3.38×** (94.77 ÷ 28.00) — the added `T` equation cost 2.7 times
what the registration allowed for it.

**The contention confound is named honestly rather than used to excuse the
miss:** the same binary on the same mesh has been measured at **1.440 s/it under
load and 0.112 s/it free — a factor of 12.9** (carried forward from the `FP_T10`
completion finding). `FP_T10`'s own run-average of 0.3126 s/it sits between those
bounds, so **an unknown part of the 3.38× is box load and an unknown part is a
genuinely low base estimate, and these logs cannot split them.** No split is
asserted on a guess.

**(b) `FP_T00`, ratio 3.001 — NEITHER contention NOR a low base estimate. It is
the DESIGN DEGENERACY of §3.2 and §4.** The arm does not merely cost more per
iteration than predicted; it performs ~333× the linear-solver work per outer
iteration (1000 sweeps against ~3) on a system that is already satisfied. **No
estimating improvement would have predicted this figure, because the figure is
not a cost of the physics — it is the cost of a solver iterating on round-off.**
Attributing it to contention or to a low reference rate would be wrong and would
teach the lab's estimator the wrong lesson.

### 10.4 EXCLUSIONS — §7.3 STANDS, NEITHER ENTERS THE RATIO

| item | core-min | class |
| --- | ---: | --- |
| K0e attempt 1 (`FP_T10`, rc=1, `wall=0`) | **0.00** solver time | **WASTE** — it bought nothing |
| K0eR2 preflight (5 iterations, 2 ranks, `ClockTime 3 s`) | **0.10** | **PREFLIGHT, not waste** — it answered the function-object question and found two instrument defects (§6.4) |

**Neither figure enters the §7.2 POINT and neither is absorbed into this rung's
actual/predicted ratio**, exactly as §7.3 requires. Both are carried into the
`docs/COST_CALIBRATION.md` row.

### 10.5 The lesson for the lab's estimates

**A control arm defined by nulling a driving difference must be costed as a
DIFFERENT solve, not as a sibling of the arm it controls.** K0eR2 priced both
arms at an identical 35.00 core-min POINT because they share a binary, a mesh and
a rank count — and the arms then differed in cost by a factor of 28.8. **Sharing
every dictionary is not sufficient grounds for sharing a cost estimate when one
arm nulls the very gradient the solver is iterating on.**

---

## 11. PROVENANCE

| what | where |
| --- | --- |
| Frozen registration | `docs/campaigns/F14-cooling-ladder/K0eR2_PREREGISTRATION.md`, `prereg_commit f306ce66` |
| Grader | `scripts/analyse_k0e.py`, git blob `25ecaa6bca8cd99f4ca1e0a84dba998cde923aaa`, pin armed and matched |
| Verdict of record | `verification/runs/F14-cooling-ladder/K0eR2_runs/K0eR2_GRADE_STDOUT.txt` |
| Completion evidence | `K0eR2_runs/STATUS.FP_T10`, `STATUS.FP_T00`, both arms' `log.solve`, `FP_T10/9000/` field mtimes, both arms' `0/T` mtimes |
| Launcher (age-guard datum ordering) | `scripts/launch_k0e.sh:114,117,121` |
| Mesh datum | `FP_T10/constant/birth_certificate.json` (`max_non_orthogonality 0.0`, `cells 52224`) — read directly, NOT through the grader |
| Queue rows | `verification/queue/heat-transfer/launched/K0eR2_FP_T10.json`, `K0eR2_FP_T00.json` |

### 11.1 A provenance discrepancy a reader must not have to infer

**The grader's stdout banner prints the PREDECESSOR's registration path.**
`analyse_k0e.py:735` emits, hard-coded:

```
prereg: docs/campaigns/F14-cooling-ladder/K0e_PREREGISTRATION.md
```

**The registration this rung actually ran under is
`K0eR2_PREREGISTRATION.md`** (`prereg_path` and `prereg_commit f306ce66` in the
queue row). This is a **banner string only** — the grader reads no
pre-registration file, and nothing in the verdict depends on it — and it follows
from the registration's own deliberate decision (`:475-479`) to keep the `k0e`
stem on the script filenames so the diff would stay readable. **It is recorded
here because the verdict artifact carries that line, and a reader of that
artifact alone would otherwise attribute this grade to the wrong document.**

**The frozen grader was NOT edited to correct it** — `CLAUDE.md` rule 6, and any
edit would break the registered pin.

### 11.2 No unattended relaunch is possible — a DEMONSTRATED zero, not an assertion

Checked at source because the arm died mid-run and a silent retry would burn
another ~105 core-min to the identical total loss: nothing about the degeneracy
has changed, and nothing can write a field before the cap.

**The instrument is `scripts/queue_runner.py` (cfd's file; daemon live, pid
1664). It was READ, NOT MODIFIED.**

**(a) The enumerator is non-recursive — with line numbers, so the claim rests on
the code and not on the glob's reputation.** `list_entries()` at `:433-441`:

```
d = root / team
files = sorted((p for p in d.glob("*.json")), key=lambda p: p.stat().st_mtime)
```

`Path.glob("*.json")` over `root/<team>` matches that directory's own entries
only; it does not descend, so `<team>/launched/` and `<team>/refused/` are
**structurally invisible** to the scan. **The single location the daemon
enumerates is `root/<team>/*.json`.**

**(b) The row leaves that location at launch.** `:583-585` sets
`dst = launched_dir / path.name` and `:591` performs
`shutil.move(str(path), str(dst))`.

**(c) NO PRODUCTION PATH WRITES A `.json` BACK INTO THE SCAN LOCATION.** Every
write, move, rename and `os.replace` in the module was enumerated and each
target resolved. `selftest()` begins at **`:979`**; the split is exact:

| line | target | verdict |
| ---: | --- | --- |
| `:132-133` | `_write_json` helper — only caller is `:702` | see below |
| `:413` | pidfile | not a queue row |
| `:449-450` | `refused/` + `.REFUSED.txt` | **out of** the scan location |
| `:522` | `dst = p.with_name(...)`, `p` from `launched_dir.glob` (`:487`) — `with_name` keeps the **same parent**, so this archives a record **within `launched/`** | never leaves `launched/` |
| `:591` | `launched/` | **out of** the scan location |
| `:634` | `dst.write_text(...)`, `dst` = `launched_dir / path.name` (`:585`) | inside `launched/` |
| `:702` | `_write_json(p, meta)`, `p` enumerated from `root/<team>/"launched"` (`:684-687`) — cap_watch stamping `status_seen_utc` in place | inside `launched/` |
| `:753` | a flag `.txt` in a case cwd | not a queue row |
| 22 further writes into `root/"cfd"/*.json` | **all at line ≥ 979, i.e. inside `selftest()`**, into a temporary root | test fixtures only |

**(d) No retry concept exists anywhere in the module.** Search terms and their
hit counts, all case-insensitive: `retry` **0**, `requeue` **0**, `re-queue`
**0**, `re-launch` **0**, `resubmit` **0**, `rerun` **0**, `attempt` **0**,
`backoff` **0**, `schedule` **0**, `timer` **0**, `unhold` **0**, `release`
**0**.

The four non-zero terms were classified individually rather than counted:
- **`relaunch` — 9 hits, NONE executable production logic.** Comments at `:60`,
  `:463`, `:1041`, `:1168`, `:1199`, `:1880`; `check(...)` assertions inside
  `selftest()` at `:1044`, `:1222`, `:1886`.
- **`cron` — 1 hit**, the comment at `:1974`: *"so the process dies loudly and
  cron (`queue_runner.sh`) restarts it with a record."* **That restarts the
  DAEMON PROCESS, not a row** — and a restarted daemon re-enumerates the same
  non-recursive glob, so it cannot see `launched/` either.
- **`while True` — 1 hit** at `:1976`, the daemon's tick loop. Each tick
  re-runs the same enumeration.

**(e) PLANTED CONTROL — the reader is shown able to see a positive.** The same
`grep` reader, over the same file, searching for a write path **known to be
present** — `shutil.move`, the launch-time move — returns **2 hits, `:449` and
`:591`**, and `mkdir` returns **22**. The zeros in (d) are therefore
demonstrated by a reader proven non-blind, not assumed. *(A bare count already
produced one false positive this evening in the cost ledger, which is why every
zero here is planted and every non-zero is classified rather than tallied.)*

**(f) The module's own selftest asserts the behaviour directly** at `:1044`:
*"second tick does not relaunch a launched entry"*, checking `r2 == "EMPTY"` and
that the launch count stays at 1.

**CONCLUSION: `K0eR2_FP_T00.json` sits in
`verification/queue/heat-transfer/launched/`. NOTHING IN THE MODULE CAN PUT IT
BACK IN PLAY. No re-drop path was found, so nothing was moved and nothing was
quarantined.** Only a deliberate owner re-enqueue could relaunch it, and that is
an agent action, not the daemon's. **No ambiguity arose, so nothing is referred
to the cfd supervisor** — had any branch resisted classification it would have
been reported rather than resolved here, since the file is cfd's.

*One code-hygiene observation, offered as an observation and NOT as a defect
claim about another team's instrument:* `SKIP_DIRS = ("launched", "refused")` at
`:114` is **defined and never referenced** anywhere in the module. The exclusion
is achieved by the non-recursive glob and the move — **the constant that looks
protective in review is not the guard doing the work.** The protection is real,
structural and selftested; only its apparent source is misleading.

---

## 12. WHAT THIS RUNG DID AND DID NOT ESTABLISH

**Established:** `FP_T10` is a complete, rule-4-clean solve on a 52,224-cell mesh
at `endTime 9000`, available to a successor. The `beta = 0` / `g = (0 0 0)`
neutralisation is confirmed present in both arms' dictionaries. The design
conflict of §4 is identified and is the rung's transferable finding.

**NOT established:** the `beta`/`g` neutralisation was **not demonstrated** —
M4b, the only gated row and the only test of it, is `NOT A RESULT`. **No Stanton
attribution is licensed by this rung.** No reader may take any K0eR2 figure as
evidence that `beta` and `g` were shown neutral.

**The rung verdict is `NOT A RESULT`.**
