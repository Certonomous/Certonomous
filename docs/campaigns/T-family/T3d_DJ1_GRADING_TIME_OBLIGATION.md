# T3d — **D-J1 IS BOUND INTO T3d's FROZEN GRADING PATH TWICE. NOTHING IS REPAIRED. WHAT IS CREATED HERE IS A GRADING-TIME OBLIGATION: THE CLOSER MUST RECORD THE TWO DENOMINATORS `gate_t3d.json` DOES NOT CARRY.**

**Rung:** T3d — `verification/runs/T-family/T3_runs/`, ladder `c = R_m`, `m = R_f`,
`f = R_fx` (`analyse_t3d.py:68`).
**Status at this write:** `R_fx` is **LIVE**. Solver rank 0 `pid 342276`, 8 ranks,
cwd `verification/runs/T-family/T3_runs/R_fx`.
**Written:** 2026-09-03, by a heat-transfer lane, on the supervisor's ruling.

> ## **THIS DOCUMENT REPAIRS NOTHING AND RE-GRADES NOTHING.**
> **T3d's first compute has happened.** The grading path is frozen under `CLAUDE.md`
> rule 2 and rule 6. A repair to a bound reader after first compute is
> `VERIFICATION_CHARTER.md` §2d.1 — **verification's ruling, not heat-transfer's** —
> and the forward-only petition for it is
> `docs/campaigns/T-family/T3d_DJ1_2D1_FORWARD_ONLY_PETITION.md`. **No comparator's
> bytes were touched by this lane.** `analyse_t1c.py` on disk is sha256
> `60893b28e284127f…` and `analyse_t3d.py` is `980ae3b203cb7d75…`; **both are
> byte-identical to their HEAD blobs at this write**, verified by hashing
> `git show HEAD:<path>` against the file.
>
> **The live run was not disturbed:** no kill, no restart, no renice, no signal,
> nothing attached. Every reading here is from `ps`, from the case's own files, and
> from read-only calls into the frozen readers.

---

## 1. THE DEFECT, AT SOURCE

**D-J1**, recorded in section G of
`docs/campaigns/T-family/GATE_PREDICATE_SATISFIABILITY_READ_2026-09-03.md`
(commit `cc8994fe`), and re-read at source by this lane:

```python
dmax = max(abs(x - y) for x, y in zip(a, b))
rng  = max(b) - min(b)
rel  = dmax / rng if rng > 0 else 0.0
return dict(state="CONVERGED" if rel <= tol else "NOT_CONVERGED", ...)
```

**MEASURED, by `grep -n` at this write** — the identical line, character for
character, at four paths:

| path | line |
|---|---|
| `verification/runs/T-family/T1_runs/analyse_t1c.py` | **229** |
| `verification/runs/T-family/T3_runs/analyse_t3.py` | **278** |
| `verification/runs/T-family/T9a_runs/analyse_t9a.py` | **213** |
| `verification/runs/T-family/T9aH_runs/analyse_t9a.py` | **213** (byte-identical file) |

**When the LAST checkpoint's field is spatially uniform — `max(b) == min(b)` — `rel`
is set to `0.0` irrespective of `dmax`, and `0.0 <= tol` for every registered `tol`.**
Two checkpoints differing by an arbitrarily large *uniform* amount grade
**`CONVERGED`**. The guard written to avoid a division by zero substitutes **the
value that grades best**. `state="UNJUDGED"` already exists in the same function for
exactly this case and is not used here.

**The family already knows the right form.** `analyse_t10a.py:372` writes
`state="CONVERGED" if dmax == 0.0 else "NOT_CONVERGED"` — byte-exact identity, no
division, no fallback, no degenerate input to fall through. That line is the model
and is cited here so a successor need not rediscover it.

---

## 2. **HOW IT REACHES T3d — AND IT IS BOUND TWICE, NOT ONCE**

Section G names one binding. **Tracing the call chain at source, this lane measured
two**, and the second one is on a different field:

1. **`analyse_t3d.py:80` — `READER = A.T1C.iterative_convergence`.** This is the
   module-level production reader the rule-3 planted control drives (`:122`, `:127`,
   `:151`). It is `analyse_t1c.py:229`'s function, default `field="T"`, `tol=1e-6`.
2. **`analyse_t3.py:625–631` — the composition that actually produces the gated
   word.** T3d gates on `M[lv]["convergence_state"]` (`analyse_t3d.py:200`), and
   `A.measure()` builds that state from **two** readers:

   ```python
   conv_T = T1C.iterative_convergence(case_dir, "T")        # analyse_t1c.py:229
   conv_U = iterative_convergence_vector(case_dir, "U")     # analyse_t3.py:278
   state  = conv_T["state"]
   if state == "CONVERGED" and conv_U["state"] == "NOT_CONVERGED":
       state = "NOT_CONVERGED"
   ```

**So D-J1's limb sits on BOTH sides of the composition.** The `U` limb can only ever
**demote** `CONVERGED` to `NOT_CONVERGED`; if `rng` over `|U|` were zero, `conv_U`
would read `CONVERGED` for free and **could not demote**. If `rng` over `T` were
zero, `conv_T` would read `CONVERGED` for free and there is nothing above it.
**Two independent entrances to the same failing branch, and the composition removes
neither.**

**A NAMING TRAP, RECORDED SO THE NEXT READER DOES NOT WALK INTO IT.** `analyse_t3d.py`
uses `P-1` and `P-2` at `:29–31` and `:152` for the **planted-zero control limbs**
(`VERIFICATION_CHARTER` §2d.11.1). The **pre-registration's** `PREDICTION P-1`
(`T3d_PREREGISTRATION.md:54–56`, relative change ≤ 1e-06 in `T` between the last two
checkpoints) is a **different P-1**. They are not the same object and a grep for
`P-1` in the comparator does not find the prediction.

**AND THERE IS NO `P-3`.** `grep -c "P-3"` over
`docs/campaigns/T-family/T3d_PREREGISTRATION.md` returns **0**. The frozen
registration declares **`P-1`, `P-2`, falsifiers `F-1`…`F-4`, and ONE terminal cost
point**. Any record that names a `P-3` for T3d is wrong.

---

## 3. ⚠ **THE OPERATIONAL FINDING: `gate_t3d.json` WILL NOT CARRY EITHER DENOMINATOR**

`analyse_t3d.py:242–245` builds the emitted `measurements` block from a fixed key
list:

```python
{k: M[lv][k] for k in ("nCells", "time", "convergence_state", "St_peak", "x_peak_H",
                       "St_10H", "St_20H", "x_R_H", "Re_achieved", "yplus_min",
                       "yplus_max", "delta99_floor_H")}
```

**`convergence_T` and `convergence_U` are not in that list.** They are the only two
dicts that carry `field_range` — the `rng` of the branch. `A.measure()` computes
them (`analyse_t3.py:649`) and `analyse_t3d.py` **drops them before `json.dump` at
`:413`.**

> ### **THEREFORE: the registered artifact will record the WORD `CONVERGED` and will NOT record either denominator that produced it. A successor auditing `gate_t3d.json` alone CANNOT distinguish "the check ran and `rng` was positive" from "the `rng == 0` limb answered for free".**

**That is `FAIL_OPEN_GATE_AUDIT.md` §28's face (d) — *the absence of an error read as
the presence of a check* — arriving inside our own registered record.** §28.4's
operational test asked literally: *"Can this code path distinguish 'the check ran and
found nothing' from 'the check did not run'?"* For `gate_t3d.json`'s reader, **no.**

---

## 4. THE TWO FACTS THAT SHARPEN IT — **RE-MEASURED, AND ONE INHERITED FIGURE IS WRONG**

### 4.1 The C3 uniform-solid control missed the branch by picokelvin — **CONFIRMED**

`W_C3`'s whole definition (`analyse_t9a.py:31`) is *"a uniform-temperature solid"* —
**the input deliberately shaped to trip this limb.** Measured from the gate files at
this write:

| artifact | `W_C3` `field_range` | `max_change` | `relative` | `state` |
|---|---|---|---|---|
| `T9aH_runs/gate_t9a.json` | **5.229594535194337e-12 K** | 1.9327e-12 | 0.36957 | `NOT_CONVERGED` |
| `T9a_runs/gate_t9a.json` | **5.002220859751105e-12 K** | 4.5475e-12 | 0.90909 | `NOT_CONVERGED` |

**It missed the `rng == 0` branch by five picokelvin.** Its `relative` is a ratio of
two machine-noise quantities, so that `NOT_CONVERGED` is rounding residue, not
physics — the control landed on the *right answer* for a reason that has nothing to
do with the property it was built to test.

### 4.2 ⚠ **THE "12.12–49.98 K" INTERVAL IS FALSE AS STATED, AND IT IS THE PREMISE THE "WILL NOT FIRE" ARGUMENT RESTS ON**

Section G asserts *"Every `field_range` recorded in `T9a_runs/gate_t9a.json`,
`T9aH_runs/gate_t9a.json` and `T9a_runs/gate_t9aD.json` lies between 12.1236 and
49.9756 K."* **Re-measured by this lane over all 22 `field_range` values in those
three files, that sentence is wrong at both ends:**

- **Minimum = 5.002220859751105e-12 K** (`W_C3`, `T9a_runs/gate_t9a.json`) — **not
  12.1236 K.** The 12.1236 K floor holds only over the **21 non-`W_C3` rows**.
- **Maximum = 49.98474017626177 K** (`D_B_x`, `T9a_runs/gate_t9aD.json`) — **not
  49.9756 K.**

**Section G contradicts itself: the same section states the C3 near-miss at
5.2e-12 K two paragraphs later.** The claim and its own counterexample sit in one
document. **This is recorded against this team's interest and nothing above it in
section G is altered — that file is a dated frozen record and this is a citation of
it, not an edit to it.**

**What this changes:** the interval was the whole of the inherited evidence that
D-J1 "cannot fire", and it is **not true over the population it names**. It is true
over the 21 production rows and the one row it excludes is precisely the one shaped
to enter the branch. **An argument that survives only by excluding its own hardest
case is not a measurement, and is not treated as one below.**

### 4.3 The live planted control **does not cover this branch** — face (d) in one artifact

T9aH's `RC5_planted_convergence_*` is a real, live planted control:
`analyse_t9aH.py:429–430` asserts **both** that `max_change` equals the plant to 1e-12
**and** that the state flipped to `NOT_CONVERGED`; the artifact records it fired
(`field_range` 49.80 / 49.98, `max_change` 0.0012340000000108375, `relative`
2.4779e-05 / 2.4692e-05).

**But the plant leaves `field_range` at ~50 K, so it exercises the `rng > 0` branch
ONLY.** It proves the instrument **can** fail; it says **nothing** about whether the
failing path was ever entered. **§28.3's sentence, measured, inside our own live
control.**

---

## 5. **INTERIM MEASUREMENT — TWO OF THE THREE GRADED LEVELS ARE ALREADY CLEAR, MEASURED, NOT INHERITED**

Read-only calls into the **frozen readers themselves** — `analyse_t1c.iterative_convergence`
and `analyse_t3.iterative_convergence_vector`, the exact functions `A.measure()`
calls — on the two finished ladder members. **No file was written; no comparator was
run; no solver was touched. Solver cost 0 core-min.**

| level | case | `T` `field_range` | `U` `field_range` | `T` `max_change` | checkpoint pair | branch |
|---|---|---:|---:|---:|---|---|
| `c` | `R_m` | **51.2959 K** | **11.0155** | 7.8752e-07 | (34000, 36000) | **`rng > 0` — TAKEN** |
| `m` | `R_f` | **50.7293 K** | **11.0257** | 4.9103e-06 | (76000, 78000) | **`rng > 0` — TAKEN** |
| `f` | `R_fx` | **NOT YET MEASURABLE** | **NOT YET MEASURABLE** | — | will be (22000, 24000) | **UNMEASURED** |

**`R_fx`'s graded checkpoint pair does not exist yet.** At this write the case holds
`processor*/0` and `processor*/2000` only. **What IS measurable now, and was
measured:** `T` at `t = 2000`, read across all 8 processor directories,
**602,128 cells, min 300 K, max 350.2884011 K, range 50.28840106 K.** That is
positive by fifty kelvin — but **it is the wrong checkpoint.** The graded pair is
`(22000, 24000)`, twenty thousand iterations away, and a range measured at 2000 is
evidence about 2000.

> **So the position is: two of three levels MEASURED clear at their own graded pair; one level UNMEASURED and not measurable until the run writes it. The obligation below exists to close exactly that one hole and nothing more.**

---

## 6. ⚠⚠ **THE OBLIGATION — BINDING ON WHOEVER CLOSES T3d**

> ## **T3d MAY NOT BE CLOSED UNTIL `R_fx`'s OWN MEASURED `field_range` FOR BOTH `T` AND `|U|`, AT THE GRADED CHECKPOINT PAIR, IS RECORDED BESIDE THE VERDICT.**
>
> **The point is not the number. The point is that "the `rng > 0` branch was taken"
> becomes a MEASURED statement instead of an INHERITED one.** A closer who writes
> "D-J1 did not fire" without those two figures has asserted face (d): the absence of
> an error read as the presence of a check.

**HOW TO DISCHARGE IT — read-only, changes nothing, touches no frozen byte.** After
`R_fx` completes, from `verification/runs/T-family/T3_runs/`:

```
python3 -c "
import sys; sys.path[:0]=['.','../T1_runs']
import analyse_t1c as T1C, analyse_t3 as A3
t=T1C.iterative_convergence('R_fx','T'); u=A3.iterative_convergence_vector('R_fx','U')
print('T', t['state'], t['field_range'], t['max_change'], t['between'])
print('U', u['state'], u['field_range'], u['max_change'])"
```

These are the **same frozen functions** `A.measure()` calls, invoked out-of-band.
They return `field_range` in their own dict; `gate_t3d.json` drops it (§3).

**WHAT MUST BE WRITTEN, and where:**

1. **In `T3d`'s results record**, beside the P-1 verdict, in these terms:
   *"`R_fx` `T` `field_range` = ⟨value⟩ K and `|U|` `field_range` = ⟨value⟩ at the
   graded pair ⟨t1, t2⟩, both MEASURED; the `rng > 0` limb of `analyse_t1c.py:229`
   and `analyse_t3.py:278` was therefore TAKEN and D-J1's `rng == 0` limb was not
   entered."*
2. **If either range is `0.0` or is not measurable**, the level is
   **`NOT A RESULT`** and P-1 is **unanswered**, not answered `CONVERGED`. The
   `CONVERGED` the frozen grader would print in that case is the defect's output, not
   a finding. **Say so in those words; do not soften it.**
3. **Either way, state which of the two it was.** "Checked, and `rng` was positive"
   and "never looked" are different records and must not share a representation
   (§28.4).

**THIS OBLIGATION CREATES NO GATE AND MOVES NO THRESHOLD.** It is a recording
requirement on the closer. It cannot turn a `PASS` into a `GATE FAIL` or the reverse;
its only power is to convert an inherited assertion into a measured one, or to
expose that it cannot be made.

---

## 7. WHERE THIS IS ALSO WRITTEN, AND THE HONEST ASSESSMENT OF WHETHER IT WILL BE READ

**This obligation is carried in two places and neither is redundant:**

- **`docs/LAB_STATE.md`, heat-transfer section, in the top block's NEXT ACTIONS.**
  L-186: the board is **the only handoff channel between sessions**. **This is the
  copy a recovering session will actually read**, because reading the board is the
  FIRST-ACTION rule and reading this file is not required by anything.
- **This file** — the durable record with the derivation, the line numbers, the
  interim measurements and the discharge recipe. **The board entry points here.**

**THE HOMES THAT DO NOT WORK — the predecessor lane's finding, RE-VERIFIED here
rather than inherited:** `CASE.txt` appears in `T3_runs/*.py` only in **builders**
(`build_t3.py:505`, `build_t3d.py:89`, `build_t3_rff.py:72`) which **write** it —
**no grader reads it and nothing refuses without it**. And `launch_t3d.sh:96` is
literally `} > "$tmp"; mv -f "$tmp" "$STATUS"`, so `STATUS.R_fx` is **atomically
replaced at completion** and a note placed there is **destroyed by the very run it
was meant to inform**.

**AND THE HONEST PART: BELT-AND-BRACES DOES NOT SOLVE THIS.** Nothing *enforces*
either copy. No script refuses to close T3d without the two figures, and this lane
did not build one — Sanaa's 22:00Z ruling forbids *"the instrumentalisation of
instruments instead of running"*, and her 20:00Z ruling forbids building an
instrument to measure another instrument's reach until the first has changed a
verdict once. **D-J1 has changed no verdict.** So the obligation rests on the board
being read, which is a convention and not a mechanism. **A successor who closes T3d
without meeting it will not be stopped by anything written here.** That is stated
plainly rather than dressed up as coverage.

---

## 8. GOVERNANCE POSTURE

- **Sanaa 20:00Z — reported, not gated.** This document creates **no gate**. It is a
  reporting obligation on the closer.
- **Sanaa 20:00Z — a petition must name a blocked result.** The petition is a
  separate document — `docs/campaigns/T-family/T3d_DJ1_2D1_FORWARD_ONLY_PETITION.md`
  — and names its blocked result there. **This document is not a petition and asks
  for nothing.**
- **Sanaa 21:00Z — running is not blocked by governance.** Nothing here touches the
  live run, and the run was launched, is monitored by its own `timeout` cap
  (`122445 s`, deadline `2026-09-05T04:05:42Z`, a full day past the endTime ETA), and
  is not stopped, extended or renegotiated by this document.
- **Sanaa 17:30Z — no re-grading of past results unless a specific comparator is
  shown to have moved.** **No comparator has moved.** `analyse_t1c.py` and
  `analyse_t3d.py` are byte-identical to HEAD (§0). **Nothing is re-graded, and the
  T9a / T9aH / T1c verdicts already on the record are untouched.**
- **`CLAUDE.md` rule 7 — SUBMISSIONS PARKED.** Nothing here is sent, filed, uploaded,
  registered, posted or commented anywhere outside this box.

## 9. WHAT THIS LANE COULD NOT SETTLE

- **Whether the `rng == 0` limb has EVER been entered anywhere in the T-family.** Only
  the three T9a gate files and the two finished T3 levels were measured. **`T1c`'s own
  runs, and every other consumer of `analyse_t1c.iterative_convergence`, are
  UNMEASURED by this lane** and are not claimed clean.
- **Whether `analyse_t3.py:278`'s vector form has any additional failure mode** beyond
  the shared `rng == 0` limb — the magnitude reduction `mags = [sqrt(sum(c*c))]` was
  read but its degenerate cases were not enumerated.
- **`R_fx`'s graded-pair ranges** — by construction not yet measurable. That is the
  hole §6 exists to close.
