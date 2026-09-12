# T5e — the T5b ladder re-graded with registered clause (1) back in position (1): pre-registration (FROZEN)

**Version 1.0. Rung `T5e`. Family: T. Team: heat-transfer. Dated 2026-09-11.**
**Status: FROZEN at this commit. ZERO SOLVER COMPUTE. No T5e case exists, no T5e case will be built, and no solver will be started under this registration.**

> **WHAT THIS RUNG IS, IN ONE PARAGRAPH.** T5e re-grades artifacts that **already
> exist** — the three completed T5b levels at
> `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}` — and changes **exactly
> one** thing against `analyse_t5c.py`: it restores the registered step **(1)**
> that `analyse_t5b.py` dropped and whose number its `y+` gate took. **No solver
> runs. No new threshold is registered.** Every threshold below is parsed out of
> a frozen predecessor or the frozen T5 registration, and the comparator refuses
> if any of them disagrees with the file it was parsed from.

> **T5d IS NOT SUPERSEDED AND IS NOT REPAIRED BY THIS RUNG.** T5d remains stopped
> for the reason its own DATED ADDENDUM 1 of 2026-09-10 records, and that
> addendum stands untouched. T5e does not build T5d, does not launch T5d, does
> not amend T5d and does not lift T5d's stop. The successor **solve** rung is
> `T5f` and it is a separate registration.

---

## 1. THE DEFECT THIS RUNG EXISTS TO MEASURE, CITED FROM BYTES

`T5_PREREGISTRATION.md:646` registers the graded order's step 1 as:

> *"1. any ladder level NOT CONVERGED → **NOT A RESULT**;"*

`analyse_t5b.py:654` is `def grade_row(...)`. Its docstring reads *"THE REGISTERED
ORDER (T5 §7.5, rule 5), evaluated top to bottom"*, and its step `(1)` at
`:656-657` is the **`y+` gate**, with the triple at `(2)`.

**The registered step 1 is not misnumbered. It is absent, and its number is
taken.** `analyse_t5c.py:532-533` says in terms that it carries
*"VERBATIM analyse_t5b.py:654-710"* and inherits the defect whole.

**Consequence, and it is the reason this rung is worth zero-compute time:** a
ladder can fail to converge — or diverge outright — and be graded without
anything noticing, because the clause that would have caught it is not in the
instrument.

## 1.1 WHAT THE T5b LADDER ACTUALLY DID — measured 2026-09-11, BEFORE this registration was written

**This section is disclosed first and deliberately, because it is what makes the
prediction in §4 an informed one rather than a blind one.** The lane that wrote
this registration read the three `log.solve` files on 2026-09-11 **before**
writing it. **The prediction in §4 is therefore NOT blind, and §4 says so again
in terms.** What has **not** happened is the run of the grading instrument: at
this commit `analyse_t5e.py` has never been executed against `T5b_runs` in any
mode, and its verdict is unknown.

`bounding omega`, read from each level's own `log.solve`:

| level | fires | t=1 | worst seen | t=5000 |
|---|---:|---|---|---|
| `c` | **5000 of 5000** | max 1.3575e+06, avg 2.3482e+04 | — | max 1.3575e+06, avg 2.3876e+04, **min −1.6362e+03** |
| `m` | 346, then **stops at t=402** | max 1.5720e+06, avg 3.9179e+04 | **max 3.7769e+24** at t=100 | field frozen; `k`,`omega` at `nIter=0` |
| `f` | **4681 of 5000** | max 2.1527e+06, avg 6.3823e+04 | **max 5.3338e+31, avg 6.0496e+25** at t=1000 | max 2.9500e+27, avg 3.4376e+21, **min −6.3228e+16** |

Initial residuals and linear-solver iteration counts at `Time = 5000`:

| level | `k` | `omega` | `h` |
|---|---|---|---|
| `c` | 1.101426161e-04, nIter=1 | 4.118385714e-06, nIter=1 | 4.878071963e-06, nIter=1 |
| `m` | 8.032026407e-09, **nIter=0** | 3.342986221e-11, **nIter=0** | 2.607598536e-03, nIter=1 |
| `f` | 5.688656468e-03, nIter=1 | 9.473633542e-04, nIter=1 | 1.994936635e-03, nIter=1 |

`bounding k, min: 0` fires **4,594 times** on level `m`. Its `k` initial residual
moved from 8.032992001e-09 at `Time = 500` to 8.032026407e-09 at `Time = 5000` —
**0.012 % across 4,500 iterations, at nIter=0.** That is a field the solver has
stopped solving, reported as a small number. L-141 is the standing reason this
lab never reads a small residual as convergence.

**All three levels reported `rc=0`, `note=clean`, `completion: COMPLETE`, passed
the six-clause rule and reached grading.** T5b returned `0 of 6` for the **`y+`**
reason (`T5B_GRADE_OUTPUT.txt:11-16`). **Nothing tested for the above.**

**Artifacts:** `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/log.solve`;
`verification/runs/T-family/T5b_runs/STATUS.T5_CUBE_{c,m,f}`;
`verification/runs/T-family/T5b_runs/T5B_GRADE_OUTPUT.txt`.

**SCOPE, AND IT IS NARROW.** This is measured on **T5b's three levels and nowhere
else.** T5 and T5c ran the same setup; **this lane has not read their logs and
this registration makes no claim about them.** That scoping question is on the
heat-transfer supervisor's board as a named open item.

---

## 2. THE INSTRUMENT FOR CLAUSE (1) — a checkpoint field-delta, never a residual

Registered here as the frozen comparator already implements it, and **parsed by
the comparator out of the frozen T5 registration rather than typed into it**, so
that restoring the clause registers **no new number**:

| quantity | value | where the comparator gets it |
|---|---|---|
| relative tolerance | **1e-6** | parsed from `T5_PREREGISTRATION.md` §5.5 (lines 466-472) |
| checkpoint stride | **1000** | parsed from the same clause |
| checkpoint pair | `endTime − 1000` and `endTime` = **4000** and **5000** | `CONV_CHECKPOINT_LO/HI` |
| fields compared | `(air, T)`, `(epoxy, T)`, `(air, U)` | `CONV_FIELDS` |
| criterion | max per-cell \|Δ\| ≤ tol × field range | `clause1_one_field` |

`analyse_t5e.py` **refuses (exit 2)** if the tolerance or stride it carries
differs from the registration it parsed them from. That refusal is exercised:
mutating `CONV_REL_TOL` to `1e6` produces
`REFUSED: CLAUSE (1) TOLERANCE MISMATCH: the frozen registration says 1e-06, this file carries 1000000.0` — **measured 2026-09-11, not asserted.**

**THE RESIDUAL IS REFUSED AS AN INSTRUMENT**, per `T5_PREREGISTRATION.md` §5.5,
which registers the checkpoint delta and expressly declines `residualControl`
(L-141: *"in T1c a genuinely unconverged case sat at residual 4e-05"*). §1.1
above is that clause earning its keep: level `m` carries an `8.03e-09` residual
on a dead field.

**The three checkpoints 3000, 4000 and 5000 exist on all three levels with both
regions and every field**, verified on disk 2026-09-11. The instrument's input
is present; nothing needs to be computed to grade.

---

## 3. THE REGISTERED ORDER — rule 5, with clause (1) back in position (1)

1. **any ladder level NOT CONVERGED → `NOT A RESULT`** *(restored; T5 §7.5 step 1)*
2. any level's `y+` gate not MET → `NOT A RESULT`
3. triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → `NOT A RESULT`
4. reference absent → `BLOCKED`
5. `G5` identity guard → `NOT A RESULT — identity`
6. deviation below the 1.7 % intrinsic floor → `GATE REACHED`
7. otherwise `PASS` inside the band, else `GATE FAIL`, GCI printed

**No GCI is quoted when clause (1) fires** — the triple is never classified, so
there is nothing to quote. **No threshold in steps 2-7 is changed by this rung**;
the comparator re-parses `YPLUS_MAX = 5.0`, `YPLUS_TARGET_TOL = 2.0` and
`YPLUS_TARGET = {c: 2.6, m: 1.6, f: 1.0}` from **both** frozen predecessors and
refuses on any disagreement.

**Graded rows (6):** `G1a G2a G3a G5a G5b G5c`.
**Reported, never graded (7):** `G1 G2 G3 G4 R1 R2 R3` (D534).

---

## 4. THE PREDICTION — REGISTERED BEFORE THE COMPARATOR HAS EVER BEEN RUN, AND LOSABLE

**HONESTY FIRST, BECAUSE IT DETERMINES WHAT THIS PREDICTION IS WORTH.** The lane
writing this has read the three `log.solve` files (§1.1) and therefore **knows
the ladder's turbulence diverged**. The prediction below is **informed, not
blind.** What is genuinely unknown at this commit is **what the registered
instrument will say**, because clause (1) is a *checkpoint field-delta on T and
U between t=4000 and t=5000* — **not** a test on `omega`, on bounding counts or
on residuals. A field that diverged early and then **froze** can present a very
small checkpoint delta. **The instrument may therefore score a physically dead
level as CONVERGED.** That is the losable part and it is the reason this rung is
worth running.

**P1 — the row verdict.** All **6** graded rows return **`NOT A RESULT`**, and
the printed clause is **`(1) T5 §5.5 convergence`**, not the `y+` clause.
*Falsified if* any graded row returns `PASS`, `GATE FAIL` or `GATE REACHED`, or
if every row's `NOT A RESULT` is attributed to a clause other than (1).

**P2 — the per-level clause-(1) states, which is where I expect to be wrong
somewhere.**

| level | predicted clause-(1) state | the reasoning, stated so it can be attacked |
|---|---|---|
| `c` | **CONVERGED** | `h` initial residual 4.878e-06 and the `omega` max identical to five figures from t=1 to t=5000 — the field is stationary, whatever else is wrong with it |
| `m` | **CONVERGED** | the turbulence is frozen from t=402 (`nIter=0`); a frozen field has a small checkpoint delta. **If this is right, the restored clause (1) still does not see a dead level, and that is a finding against the instrument, not for it.** |
| `f` | **NOT CONVERGED** | `h` 1.995e-03, `k` 5.689e-03, `omega` 9.474e-04, all at nIter=1, with `omega` max still 2.95e+27 at t=5000 |

*Falsified if* the measured states differ from this row-for-row. **P1 survives
any single-level miss** as long as at least one level is NOT CONVERGED; P1 and P2
are graded separately for exactly that reason.

**P3 — no GCI is quotable.** The comparator prints *"NO GCI IS QUOTABLE FROM ANY
ROW ABOVE"*. *Falsified if* any GCI or observed order is printed for a graded row.

**P4 — the planted-zero control fires and passes.** `PLANT_OFFSET = 1.234e-03`
and `PLANT_SPIKE = 9.876e+02` are planted and read back; the comparator refuses
if the reader cannot see them (rule 3). *Falsified if* the control does not run,
or runs and cannot see its own plant.

---

## 5. THE FREEZE SET

| file | sha256 (disk bytes, never a git blob SHA-1 — L-450) |
|---|---|
| `verification/runs/T-family/T5e_runs/analyse_t5e.py` | `8b453650078912fd484fdd94fdd3ccdbb251f0aca1c0988e1e7d3b037029e462` |

Committed **as found and unmodified** at `6fd480b9` before this registration was
written, so that any later repair to it reads as a real diff.

**TWO PINS ARE DELIBERATELY LEFT UNSET AND THEY ARE THE SUPERVISOR'S TO SET, NOT
THIS LANE'S.** `analyse_t5e.py:185-186` carries
`GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"` and
`REGISTRATION_SHA256 = "PIN-AT-FREEZE"`. While either is unset the comparator
prints *"THIS FILE IS NOT YET FROZEN"* and labels its own output **`DRY RUN …
NOT A GRADED RECORD`** (`:1940-1949`, `:2092-2094`). The comparator's own
selftest at `:2165-2171` **requires** both to read `PIN-AT-FREEZE` and refuses if
this file set them itself.

**A BINDING T5e VERDICT THEREFORE REQUIRES A SUPERVISOR ACT AFTER THIS COMMIT:**
set `GRADING_PATH_FREEZE_COMMIT` to this registration's commit sha and
`REGISTRATION_SHA256` to this file's sha256, then re-run. **Any output produced
before that is a DRY RUN and is labelled one by the instrument itself.**

**DISCLOSED TENSION, NOT RESOLVED HERE:** setting those pins will make the
selftest checks at `:2165-2171` fail, because they assert the pins are unset. The
selftest is a **pre-freeze** instrument as written. This is recorded rather than
repaired; it belongs to the lane that owns the file.

---

## 6. THE INSTRUMENT'S OWN DEFECTS, DISCLOSED BEFORE IT GRADES ANYTHING

Measured 2026-09-11 by driving the comparator's own eight mutations, parsed out
of its source rather than retyped.

**The mutation arms are broken as written.** `:2520-2547` writes each mutant into
`tempfile.mkdtemp()` and runs it with `cwd=d`. `_find_t_family` at `:156-165`
walks up from `HERE` **and** `os.getcwd()` looking for
`T5b_runs/analyse_t5b.py`; from a `/tmp` directory both start points miss, the
frozen predecessors and `T5_PREREGISTRATION.md` become unreachable, and the child
refuses. **Each arm asserts only `returncode != 0`, so all eight passed for a
reason unrelated to their mutations.** The unmutated control arm failed for the
same reason, which is how the defect was visible at all.

**Driven externally with `cwd=HERE` — the one-word fix:**

| arm | result | rejects for its own reason? |
|---|---|---|
| control (unmutated) | `SELFTEST PASS (0 failed)` | — *(was rc=1)* |
| N1 N3 N4 N6 N8 | rc≠0, each on a `FAIL` line specific to its mutation | **yes** |
| N2 | rc=2, `CLAUSE (1) TOLERANCE MISMATCH` | **yes**, by refusal |
| N5 | `SELFTEST PASS` | **no — and the arm is inert by construction:** its mutation only adds an unused keyword argument `residual_state=None` and makes no residual gate anything |
| N7 | `SELFTEST PASS` | **no — and its mutation is real:** it replaces the planted-zero arm's argmax predicate `arg_s == i0` with the tautology `arg_s == arg_s`, and the selftest does not see it |

**So six of eight arms are genuine controls, one tests nothing, and one exposes a
real blind spot in the rule-3 planted-zero control's self-verification.** N6
still covers the reader-blinding case; that specific predicate is not covered.

**NONE OF THIS IS REPAIRED BY THIS REGISTRATION**, and the file is frozen above
by sha256 in the state that carries these defects. **What it means for the
verdict, stated plainly:** clause (1)'s own tolerance and stride refusal (N2) and
its ordering ahead of the `y+` clause (N1) are both **exercised and rejecting**,
so the mechanism this rung turns on is controlled. The two weak arms sit on the
planted-zero self-check and on a no-op. **A reader may weigh the verdict
accordingly, and is told rather than left to discover it.**

---

## 7. RULE 12 — COST

**Zero solver core-minutes.** No solver runs under this registration.

| item | figure | basis |
|---|---:|---|
| solver core-min | **0.000** | no case is built, no case is launched |
| comparator run, predicted | **≤ 1 core-min**, 1 rank | reads 3 levels × 2 checkpoints × 3 fields under `T5b_runs`; no solve |
| instrument diagnosis already spent | **≈ 14 core-min**, 1 rank | 10 selftest/mutant children plus the determinant identity work, wall-clock at 1 rank from artifact mtimes |

**USD is derived at $0.0513/core-h and is DERIVED, NOT MEASURED** — this box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Estimate-versus-actual is owed at completion** and lands in
`docs/COST_CALIBRATION.md`, per rule 12.

---

## 8. WHAT THIS RUNG CANNOT DO

- **It cannot make the T5b ladder converge.** It grades what is on disk. A rung
  that changes the setup so the ladder can converge is **`T5f`**, separately
  registered.
- **It cannot see a divergence directly.** Clause (1)'s instrument is a
  checkpoint delta on `T` and `U`. It does not read `omega`, bounding counts or
  `nIter`. §4's P2 registers the possibility that it scores a dead level
  CONVERGED, and T5f is where a criterion that catches that belongs.
- **It does not re-open T5, T5b or T5c.** T5b's `0 of 6` stands; this rung
  reaches the same tally by a different and registered clause.
- **It does not touch T5d**, whose addendum stands.
- **Nothing here is sent, filed, uploaded, registered, posted or commented
  outside this box** (rule 7).

---

## DATED AMENDMENT 1 — 2026-09-12: THE FREEZE ACT WAS PERFORMED, AND §5's SHA NAMED THE UNPINNED BYTES

**Version 1.1.** Appended by the lane at the heat-transfer supervisor's direction.
**Lines whose number changed above this section: 0.** Nothing above is edited,
struck or renumbered; this section is appended at the foot and the bytes above it
are byte-identical to the freeze commit `e6730df8`.

### 1. THE PIN-SETTING IS THE FREEZE ACT, NOT A CHANGE TO A FROZEN FILE

§5 reserved two pins to the supervisor and recorded that while either read
`PIN-AT-FREEZE` the comparator labels its own output `DRY RUN … NOT A GRADED
RECORD`. **The supervisor performed that act on 2026-09-12** and set, in
`analyse_t5e.py:185-186`:

| pin | value |
|---|---|
| `GRADING_PATH_FREEZE_COMMIT` | `e6730df82fbe7e7cfaa2705b4e637480c6f9cb1e` |
| `REGISTRATION_SHA256` | `8a5df140dc42014f2d57c505408f14b405a4171d1e688079065347f382f32413` |

**The file said of itself `THIS FILE IS NOT YET FROZEN`.** Filling placeholders
the author left expressly for this purpose **completes** the freeze; it is not a
departure from a frozen file, and rule 6 is not engaged by it.

### 2. §5's RECORDED SHA NAMED THE UNPINNED BYTES — CORRECTED HERE, NOT REWRITTEN

§5 recorded `analyse_t5e.py` at sha256
`8b453650078912fd484fdd94fdd3ccdbb251f0aca1c0988e1e7d3b037029e462`. **That is
the sha of the bytes BEFORE the pins were set**, i.e. of a file that labelled its
own every output a dry run. §5 is **struck as to that value and not rewritten**.
The operative freeze witness is:

| file | sha256 (disk bytes; never a git blob SHA-1 — L-450) |
|---|---|
| `verification/runs/T-family/T5e_runs/analyse_t5e.py` | `c97d355d278b6523021d40a7a4925b8b9f3430bec25250b24238fdaa9daabfbc` |

**`REGISTRATION_SHA256` is NOT disturbed by this addendum.** It names this
registration's bytes **as frozen at `e6730df8`**, which is what a freeze witness
is for. The comparator only prints it and never verifies it against this file, so
no circularity arises from appending here; that was checked in the source
(`:186` defines it, `:1949` prints it, `:2165-2171` asserts it), not assumed.

### 3. THE SELFTEST ASSERTION WAS NARROWED, AND WHAT IT WAS FOR IS PRESERVED

`:2165-2171` asserted both pins `== ["PIN-AT-FREEZE"]`. **That is a pre-freeze
assertion: it fails the moment the supervisor performs the very act it exists to
reserve to them**, and a frozen instrument whose own selftest fails is a red with
an innocent explanation. It is narrowed to admit **exactly two** values per pin —
the placeholder, or the registration's own frozen value quoted from this document
— and **any third value still fails**.

**Measured, not asserted, after the narrowing** (driven with `cwd=HERE`, the
comparator's own eight mutations parsed out of its source):

| arm | result |
|---|---|
| control, unmutated, pinned and narrowed | **`SELFTEST PASS (0 failed)`** |
| N8 (`GRADING_PATH_FREEZE_COMMIT` → `deadbeefdeadbeef`) | **rejects**, on the narrowed assertion's own message |
| N1 N3 N4 N6 | reject, each on a `FAIL` line specific to its mutation |
| N2 | rejects by refusal, rc=2, `CLAUSE (1) TOLERANCE MISMATCH` |
| N5, N7 | unchanged from §6 — inert-by-construction, and the real blind spot |

### 4. A CONTROL THIS LANE BROKE, AND REPAIRED, DISCLOSED AS ITS OWN DAMAGE

N8's mutation anchored on the literal
`GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"`. **Setting the pin destroyed that
anchor, and the arm reported `the mutation anchor is not in the source` — a
control that had silently stopped being drivable, caused by this lane's own
edit.** The anchor is updated to mutate the pin **as set**, which asks the same
question it always asked. **This is recorded as the lane's own defect and not as
a finding against anybody else.** It was caught because the arm says out loud
when its anchor is missing; an arm that had failed silently would not have been.

### 5. WHAT IS STILL RED, AND IT IS THE §6 DEFECT, UNREPAIRED BY RULING

`--selftest` still reports **2 failed**: the control arm and the `python3 -O`
arm. **Both are the `cwd=d` defect disclosed in §6** — the arms run children in a
temp directory where `_find_t_family` cannot reach the frozen predecessors, so
every child refuses. **The one-word fix (`cwd=d` → `cwd=HERE`) is proven and is
deliberately NOT applied here:** the heat-transfer supervisor ruled it, and the N7
blind spot, **findings routed to verification against another lane's file rather
than repairs taken by this team.**

**So the binding verdict this instrument produces carries that disclosed caveat,
stated here rather than left for a reader to find:** the mechanism the rung turns
on — clause (1)'s ordering ahead of the `y+` clause (N1) and its tolerance and
stride refusal (N2) — is exercised and rejecting under `cwd=HERE`, and the
unmutated file passes cleanly. The two red arms are the harness around the
controls, not the controls themselves.

### 6. NO GATE, THRESHOLD, CAP, LABEL OR PREDICTION IS TOUCHED

§3's order, §2's tolerance and stride, §4's P1-P4 and §7's cost are unchanged by
this addendum. **P2 was already registered as losable and is graded as written.**
