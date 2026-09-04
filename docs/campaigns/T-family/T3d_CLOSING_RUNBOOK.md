# T3d CLOSING RUNBOOK — `R_fx`, the fourth level of the T3 ladder

**Written 2026-09-04T01:1xZ by a heat-transfer lane WHILE `R_fx` IS STILL
RUNNING.** Nothing in this file grades anything, closes anything or writes a
marker. It is the sequence a cold successor executes *after* the solver stops.

**NOTHING ENFORCES THIS RUNBOOK.** It is a convention, not a mechanism. No
script reads it, nothing refuses without it, and a closer who does not open it is
in exactly the position of the closer who did not open the pre-registration —
which is the failure mode `R_fx/CASE.txt`'s own appended block already names
about itself. Treat this document as proximity and ordering, not as a guard.

**Registration:** `docs/campaigns/T-family/T3d_PREREGISTRATION.md` (sha256
`92ca57fff5574dfe73051cf3f52f16eaed72de129af663ae2f7988830e916e2a`, byte-identical
to its HEAD blob as of 2026-09-04T01:05Z).
**Case:** `verification/runs/T-family/T3_runs/R_fx` — `buoyantBoussinesqSimpleFoam`,
8 ranks, `endTime 24000`, `writeInterval 2000`, `purgeWrite 2`, mesh byte-identical
to `R_ff` (602 128 cells), seeded from `R_ff/118000`.
**Ladder graded:** `LADDER = {"c": "R_m", "m": "R_f", "f": "R_fx"}`
(`analyse_t3d.py:68`).

---

## 0. BEFORE ANYTHING — is it actually finished?

Do not start at step 1 on a running solver. The run is finished when the solver
process is gone **and** `STATUS.R_fx` exists in `verification/runs/T-family/T3_runs/`
(the launcher writes it in-wrapper, `launch_t3d.sh:44`, `STATUS="$ROOT/STATUS.$CASE"`).
An absent `STATUS.R_fx` means the run never finished — **an absent rc is not a
zero**, and the frozen marker logic refuses on it.

Read-only:

```
ps -o pid=,etime=,stat=,args= -p <rank-0 pid>
ls -la /home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/STATUS.R_fx
```

---

## 1. THE RULE-4 SIX-CLAUSE COMPLETION CHECK, SPELLED OUT

Standing rule 4 is all-or-nothing. The frozen implementation is
`verification/runs/T-family/T3_runs/mark_done_t3.py`, function `check(root, case)`
(HEAD blob `5da28c73`), and it is **parametric in the case name** — it is called
on `"R_fx"`, nothing is restated and nothing is re-implemented.

Root for every command below:

```
R=/home/ubuntu/Certonomous/verification/runs/T-family/T3_runs
```

| # | clause | exact expectation for `R_fx` | where the frozen check does it |
|---|---|---|---|
| 1 | `rc = 0` | `grep -o 'rc=[0-9]*' $R/STATUS.R_fx` → `rc=0` | `mark_done_t3.check`, `re.search(r"rc=(\d+)")` |
| 2 | an `End` line | `grep -c '^End$' $R/R_fx/log.solve` → `1` | `re.search(r"^End\s*$", body, re.M)` |
| 3 | last time == `endTime` | `ls -d $R/R_fx/[0-9]*` → the largest numeric directory is **`24000`** | `last != et` → fail |
| 4 | fields present at `endTime` | `ls $R/R_fx/24000` contains **`T U p_rgh alphat phi nut k omega`** — **EIGHT**, not seven | `NEEDED + NEEDED_TURBULENT` (`mark_done_t3.py:34-35`) |
| 5 | `ExecutionTime` count == `endTime` | `grep -c '^ExecutionTime' $R/R_fx/log.solve` → **`24000`** | `n_exec != int(et)` → fail |
| 6 | **age guard** | every one of those eight files at `24000` has an mtime **NEWER than `$R/R_fx/0/T`** | `os.path.getmtime(t0)` vs each field |

**Clause 4 is stricter than CLAUDE.md rule 4's prose.** The constitution lists
seven fields for the thermal family; the frozen check also demands `phi`. The
frozen check governs. `R_ff/118000` carries `phi`, so `reconstructPar` does
produce it — this is expected to hold, not hoped for.

### 1a. `0` versus `0.orig` — WHICH ONE DATES THE RUN, verified on disk

`R_fx` holds **both** `0/` and `0.orig/`. The age guard uses **`0/T`, not
`0.orig/T`** — this is not a reading of the prose, it is what the frozen code
does: `mark_done_t3.check` opens `os.path.join(d, "0", "T")` and compares every
field's mtime against that one file. `0.orig/T` is never consulted.

That is also the correct datum by construction. `launch_t3d.sh` arms the case in
this order (lines 108-111): `cp -r 0.orig 0`, then `sleep 1`, then **`touch 0/T`**
— the header calls it "the age-guard datum" in as many words. So `0/T` is touched
*last* at launch and dates the run allowed to produce the answer.

**Verified on disk 2026-09-04T01:03Z, before this file was written:**

| file | mtime |
|---|---|
| `R_fx/0.orig/T` | `2026-09-03 17:23:41.922915140 +0000` |
| `R_fx/0/T` | `2026-09-03 18:04:05.113277023 +0000` |

`0/T` is the **later** of the two by 40m 24s, so it is both the code's datum and
the stricter one. A closer who instead used `0.orig/T` would be applying a
*weaker* guard by 40 minutes. Re-verify the two mtimes yourself before relying on
this table — it is a measurement with a timestamp, not a property.

### 1b. The command

There is **no `mark_done_t3d.py`** (see §6, BLOCKING GAP 1). To read the six
clauses without writing anything:

```
cd $R && python3 -c "
import sys; sys.path.insert(0,'.'); import mark_done_t3 as MD
f = MD.check('.', 'R_fx')
print('CLAUSES 1-6: ' + ('ALL HOLD' if not f else 'NOT DONE'))
[print('  - '+x) for x in f]"
```

Plus the physics-critical clause the R_ff marker adds and rule 4's prose does not:

```
grep -o 'reconstructpar_rc=[0-9]*' $R/STATUS.R_fx    # must be reconstructpar_rc=0
```

A failed reconstruction is not a result: the graded fields are the reconstructed
ones, and `analyse_t3.measure` reads the **top-level** time directory, not
`processor*/`. With `purgeWrite 2` the surviving pair after `reconstructPar
-newTimes` is **(22000, 24000)** — the pair this rung is graded on.

**If ANY clause fails, stop.** The rung is `NOT A RESULT` for that reason and no
grading is run. A run that fails one clause is not done.

---

## 2. THE D-J1 DENOMINATOR STEP — run this BEFORE the grader, every time

### What D-J1 is

`rel = dmax / rng if rng > 0 else 0.0` at

* `verification/runs/T-family/T1_runs/analyse_t1c.py:229` — the `T` limb
* `verification/runs/T-family/T3_runs/analyse_t3.py:278` — the `|U|` limb

is a divide-by-zero guard that, on the `rng == 0` branch, substitutes **the value
that grades best**. `rel = 0.0` is unconditionally `<= tol`, so the level reads
`CONVERGED` **irrespective of `dmax`**. Both limbs are composed at
`analyse_t3.py:625-631` into `convergence_state`, which `analyse_t3d.py:200` gates
the entire T3d ladder on. **The defect is bound into T3d's frozen grading path
twice.**

### Why `gate_t3d.json` cannot answer this on its own

`analyse_t3d.py:242-245` builds the emitted `measurements` block from a fixed key
list — `nCells, time, convergence_state, St_peak, x_peak_H, St_10H, St_20H,
x_R_H, Re_achieved, yplus_min, yplus_max, delta99_floor_H`. It carries
`convergence_state` and carries **neither `convergence_T` nor `convergence_U`**,
the only two dicts that hold `field_range`. **The JSON will record the word
`CONVERGED` and not one denominator that produced it.** Reading the JSON is
therefore not a check on D-J1; it is the thing D-J1 hides behind.

### The command

```
cd $R && python3 probe_djone_denominator.py R_m R_f R_fx
```

`probe_djone_denominator.py` imports the two frozen readers out-of-band and calls
them unmodified — it cannot drift from the grader because it *is* the grader's
readers. It writes nothing into any case directory, runs no solver and grades
nothing. It carries its own rule-3 control in three limbs (witness on real disk
bytes; a plant into a scratch copy whose baseline is a true zero; and a synthetic
case that reproduces D-J1 itself) and **refuses at exit 2** if any limb fails —
a `field_range = 0.0` reported by a reader never shown able to read ~51 K off
`R_m` would not be evidence.

**Already measured, by two independent lanes, and cited rather than re-derived:**

| level | case | pair | `T` field_range | `\|U\|` field_range | branch |
|---|---|---|---|---|---|
| `c` | `R_m` | (34000, 36000) | **51.2959 K** | **11.0155** | `rng > 0` TAKEN |
| `m` | `R_f` | (76000, 78000) | **50.7293 K** | **11.0257** | `rng > 0` TAKEN |
| `f` | `R_fx` | (22000, 24000) | **NOT YET MEASURED** | **NOT YET MEASURED** | **UNKNOWN** |

### THE REFUSAL RULE, in the words a reader outside this lab needs

**T3d may not be closed until `R_fx`'s own measured `field_range` for BOTH `T`
and `|U|`, at the graded checkpoint pair (22000, 24000), is written down beside
the verdict.**

**If either range comes back `0.0`, or cannot be measured, then the level is
`NOT A RESULT` and prediction P-1 is UNANSWERED — not answered `CONVERGED`. The
`CONVERGED` the frozen grader prints in that case is the defect's output, not a
finding.** Say it in those words, in the results record, and do not soften it.

`rng > 0` clears D-J1 and clears nothing else. It is necessary, not sufficient: a
level can take the honest branch and still be `NOT_CONVERGED`, and that is a real
answer to P-1 (falsifier F-1) rather than an artifact.

---

## 3. THE GRADING INVOCATION, EXACTLY AS FROZEN

```
cd $R && python3 analyse_t3d.py --root .
```

Output is `gate_t3d.json` beside the comparator (`analyse_t3d.py:72`).
`gate_t3.json` and `gate_t3_rff.json` are never written.

`analyse_t3d.py:174-177` refuses at exit 2 unless `DONE.R_m`, `DONE.R_f` **and
`DONE.R_fx`** all exist — "the triple is graded whole or not at all". `DONE.R_m`
and `DONE.R_f` are on disk from 2026-08-24. `DONE.R_fx` is not, and §6 explains
why that is a blocking gap and not a formality.

**Grading MUTATES the case.** `analyse_t3.measure` shells out to
`postProcess -func writeCellCentres` / `writeCellVolumes` (`analyse_t3.py:443`),
which writes `C Cx Cy Cz` into the graded time directory. Run the §1 completion
check **first**; a case that has been graded is no longer the case that was
completed.

### THE `rc = 0` TRAP — read the verdict strings, never `$?`

**`analyse_t3d.py` returns `EXIT_OK` unconditionally.** Verified in the frozen
file itself, `analyse_t3d.py:408-414`: `main` calls `grade(root)`, dumps the JSON,
prints `wrote ...` and `return EXIT_OK`. There is no branch on the tally. A run
in which **every graded row is `NOT A RESULT`** exits **0**.

The precedent relayed to this lane is T16c, whose grading returned `rc = 0` on
four `NOT A RESULT` rows, so a reader checking `$?` would have recorded a clean
grade. *This lane could not locate the T16c record on disk and does not vouch for
that anecdote* — but it does not need it: the mechanism is verifiable in
`analyse_t3d.py` at HEAD, above, and that is the citation to use.

**So: `$?` from the grader carries no verdict information whatsoever.** Read the
`verdict` strings in `gate_t3d.json` and the `tally` block. A `$?` of 0 means the
comparator did not crash. It does not mean anything passed. Exit 2 is a refusal
and exit 1 a failed selftest — those *are* informative; 0 is not.

---

## 4. RULE-5 GATING — the Roache triple

* A row whose grid triple is not `CONVERGING` is **`NOT A RESULT`**, whatever the
  value says. The gate can only turn a `PASS` or `GATE FAIL` **into**
  `NOT A RESULT`, never the reverse.
* Order, and it is an order: (1) any level not iteratively converged or not
  plateaued → `NOT A RESULT`; (2) triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY`
  or `EXACT` → `NOT A RESULT`, with the value and both triples and orders printed
  beside it; (3) `CONVERGING` → `PASS` inside the pre-registered band else
  `GATE FAIL`, with the GCI printed.
* **GCI at `Fs = 1.25`** (`analyse_t3.py:80`, three levels).
* **Never quote a GCI when the three values are not monotone.** A GCI beside a
  non-monotone triple is a number with no meaning attached, and printing it
  invites it to be quoted downstream.
* The registered expectation (`T3d_PREREGISTRATION.md` §3, and it is a disclosure
  *against* the document's own interest): **T3d will not produce a `PASS`.** The
  primary — Vogel & Eaton (1985) — is NOT OBTAINED, so gate (3) fires `BLOCKED`
  on `G1`, `G3`, `G4`; `G2` (`x_peak_H`) stays `NOT A RESULT` because its triple
  is `OSCILLATORY`. Three rows move `NOT A RESULT` → `BLOCKED`; one does not move.
  **If a `PASS` appears, something is wrong — investigate it, do not bank it.**

---

## 5. THE RULE-12 COST CALIBRATION ROW — OWED AT COMPLETION, NOT OPTIONAL

Sanaa's directive of 2026-08-23 requires estimate-versus-actual at every process
completion. A completion report without this comparison is incomplete. The row
lands in **`docs/COST_CALIBRATION.md`** under that file's append rules and the
rule-10 private-index protocol.

**Registered figures** (`T3d_PREREGISTRATION.md:137-139`, frozen):

| item | value | basis |
|---|---|---|
| rate basis | **0.226755 core-min/iteration** | MEASURED from `R_ff`'s own `STATUS.R_ff`: 26 757.067 core-min ÷ 118 000 iterations, same mesh, same ranks |
| **ESTIMATE (POINT)** | **5 442.1 core-min** | `0.226755 × 24 000` |
| **HARD CAP** | **16 326 core-min** | `3 × point` |
| registered `timeout_s` | 122 445 s | `16 326 × 60 ÷ 8` |
| USD at point | $4.653 | **DERIVED, NOT MEASURED** |

**Measured en route** (this lane, 2026-09-04T01:06:57Z, iteration 16 773,
`ExecutionTime = 25 218.83 s`): **0.200472 core-min/iteration cumulative**, ratio
0.8841, projected total 4 811 core-min. The 2 000-iteration window read
**0.178933**, projecting 4 294 core-min — **the run is speeding up, and that drift
is stated, not smoothed** (the 8 000-iteration window reads 0.183449; the
19:26Z reading was 0.199674). A projection quoted from any single window is a
window, not a forecast.

**At completion, compute the ACTUAL and do not reuse any projection:**

```
E=$(grep '^ExecutionTime' $R/R_fx/log.solve | tail -1 | awk '{print $3}')
python3 -c "e=$E; print('ExecutionTime_s', e); print('ACTUAL core-min %.1f' % (e*8/60)); \
print('ratio actual/predicted %.4f' % (e*8/60/5442.1)); \
print('USD DERIVED %.3f' % (e*8/60/60*0.0513))"
```

Cross-check against `core_min` in `STATUS.R_fx`, which `launch_t3d.sh` computes as
`wall_s × ranks ÷ 60` — the two should agree to within the launcher's non-solver
steps (`checkMesh`, `decomposePar`, `reconstructPar`), and **any gap is named, not
absorbed**.

The row must state: the ratio actual/predicted; the attribution of the gap
(contention, waste, misprediction — **waste stays separately named and is never
absorbed into the ratio**, `COMPUTE_BUDGET_CHARTER.md` §6); the actual in
core-minutes as the measured unit; and the dollars **DERIVED at $0.0513/core-h,
labelled derived-not-measured, because this box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5). It must also record whether **F-3** (cost within
the 16 326 cap) held.

The precedent this rung is trying not to repeat is named in `R_fx/CASE.txt`:
`T15_PREREGISTRATION.md:329` and `T24_PREREGISTRATION.md:902` each required their
calibration row at completion and neither row landed until a human noticed.

---

## 6. WHAT WOULD MAKE T3d `NOT A RESULT` — the explicit list

A closer must be able to fail this rung. Every route below ends in
`NOT A RESULT`, `BLOCKED` or `GATE FAIL` — none of them ends in a `PASS`, and
none of them is repaired by re-running with different settings.

**Completion (rule 4) — any one of these, alone:**

1. `STATUS.R_fx` absent → **refusal**; an absent rc is not a zero.
2. `rc != 0` in `STATUS.R_fx` — including `124` (cap expired) and `128+n` (killed
   by signal n).
3. No `End` line in `log.solve`.
4. Last written time directory `!= 24000`.
5. Any of `T U p_rgh alphat phi nut k omega` missing at `24000`.
6. `ExecutionTime` line count `!= 24000`.
7. Any field at `24000` older than `R_fx/0/T` — **age guard**; a field that
   pre-dates the launch was not written by this run.
8. `reconstructpar_rc != 0` — the graded fields are the reconstructed ones.
9. `capped=yes` / `wall_s >= 122445` — the cap expired; the cap is not widened
   after the fact and the run does not get a new budget (rule 12).

**Denominator (D-J1, §2):**

10. `R_fx`'s `T` `field_range == 0.0` at (22000, 24000) → **`NOT A RESULT`**, P-1
    **UNANSWERED**, and the printed `CONVERGED` is the defect's output.
11. `R_fx`'s `|U|` `field_range == 0.0` → the same, independently.
12. Either range **not measurable** (fewer than two checkpoints; checkpoint sizes
    differ; the probe refuses) → **`NOT A RESULT`**, not "assume fine".
13. The probe's rule-3 control fails (exit 2) → **no level may be classified from
    that run at all**; the probe has not been shown able to see a non-zero.
14. The pair the probe reports is not `('22000','24000')` → you measured a
    different pair from the one graded; re-measure, do not reconcile in prose.

**Convergence and the triple (rule 5):**

15. Any of the three levels reads `NOT_CONVERGED` or `UNJUDGED` → `NOT A RESULT`,
    and for `R_fx` that is falsifier **F-1** losing honestly.
16. The triple is `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` →
    `NOT A RESULT` regardless of the value. (`G2 x_peak_H` is expected here.)
17. `r21 <= 1` or `r32 <= 1` → the ladder does not refine; the comparator refuses.
18. The three values are not monotone → **no GCI is quotable**, and any row
    resting on one is `NOT A RESULT`.

**Freeze and provenance (rule 2, rule 6):**

19. `analyse_t3d.py`, `analyse_t3.py`, `analyse_t1c.py` or
    `T3d_PREREGISTRATION.md` is not byte-identical to its HEAD blob → **STOP**.
    The grading path is fixed at the pre-registration commit; a moved file is a
    finding, and you do not grade around it.
20. `DONE.R_fx` exists but was not produced by the frozen completion check — a
    hand-written marker is not a completion, and the comparator cannot tell the
    difference (`analyse_t3d.py:394` forges markers in its own selftest, which is
    exactly the point).

**Reference (rule 1 vocabulary):**

21. The primary (Vogel & Eaton 1985) remains unobtained → `G1/G3/G4` are
    **`BLOCKED`**, which is the registered expectation, not a surprise, and
    **`BLOCKED` is not a softened `PASS`**.

### BLOCKING GAP 1 — `DONE.R_fx` has no registered producer

**There is no `mark_done_t3d.py`.** `mark_done_t3_rff.py` hard-codes
`CASE = "R_ff"` (line 30) and cannot be pointed at `R_fx`.
`T3d_PREREGISTRATION.md` names `build_t3d.py`, `launch_t3d.sh` and
`analyse_t3d.py` as the fixed path and **names no completion marker at all**. Yet
`analyse_t3d.py:174-177` refuses to grade without `DONE.R_fx`.

So the closer is in this position: the grader demands a marker that no registered
instrument produces, and **first compute has already happened**, so a new marker
script cannot be registered before compute the way `mark_done_t3_rff.py` was
(`T3_R_FF_PREREGISTRATION.md` AMENDMENT 1, frozen before `R_ff` iterated).

**Do not hand-write `DONE.R_fx`.** It would satisfy the grader and certify
nothing, and route 20 above is exactly that failure.

**This is a supervisor's ruling, not a lane's.** The candidate dispositions, none
of them taken here: (a) a thin wrapper that imports the frozen
`mark_done_t3.check` and `mark_done_t3_ext1` unmodified and calls them on
`"R_fx"`, landed as a dated addendum under rule 2 — it alters no gate, threshold,
cap or label, but it *is* a post-compute addition to the closing path and must be
read as a diff by the supervisor personally (`SUPERVISION_CHARTER.md` §3 check 1);
or (b) escalate. Until one is ruled, **T3d is `PENDING` on this gap** — that is a
queue state, not a verdict on the physics.

### BLOCKING GAP 2 — the denominator is not in the record the rung publishes

Covered in §2: `gate_t3d.json` records the word and not the number. Until
`R_fx`'s two `field_range` values are written beside the verdict — in the results
record, not only in a lane's report — the rung is not closed. The probe supplies
them; nothing forces anyone to run it. That is the same convention-not-mechanism
caveat this file opens with, and it is the reason this section exists rather than
a `refuse()` somewhere.

---

## 7. ORDER OF OPERATIONS, one line each

1. Confirm the solver is gone and `STATUS.R_fx` exists (§0).
2. Re-hash the four frozen files against HEAD (§6 route 19). Any drift → STOP.
3. Run the rule-4 six-clause check read-only (§1b) **and** `reconstructpar_rc`.
   Any fail → `NOT A RESULT`, stop.
4. Run `probe_djone_denominator.py R_m R_f R_fx` (§2). Record both `R_fx`
   ranges. Either zero or unmeasurable → `NOT A RESULT`, P-1 **UNANSWERED**, stop.
5. Resolve BLOCKING GAP 1 with the supervisor before `DONE.R_fx` exists.
6. Grade (§3). **Read the verdict strings, never `$?`.**
7. Apply rule 5 to every row (§4).
8. Land the cost calibration row (§5).
9. Write the results record carrying: the six clauses, both `R_fx` denominators
   with their pair, every verdict from the fixed vocabulary, the GCI only where
   monotone, and the P-1/P-2/F-1..F-4 outcomes stated as won or lost.

---

## 8. Provenance of the numbers in this file

| claim | measured | when |
|---|---|---|
| four frozen files byte-identical to HEAD | `sha256sum` vs `git show HEAD:<path>` | 2026-09-04T01:05Z |
| `R_fx/0/T` mtime `2026-09-03 18:04:05`, `0.orig/T` `17:23:41` | `ls --time-style=full-iso` | 2026-09-04T01:03Z |
| `R_m` 51.2959 / 11.0155 at (34000,36000); `R_f` 50.7293 / 11.0257 at (76000,78000) | `probe_djone_denominator.py`, frozen readers imported, three-limb control PASS | 2026-09-04T01:05Z |
| iteration 16 773, `ExecutionTime` 25 218.83 s, 3 362.5 core-min | `R_fx/log.solve` | 2026-09-04T01:06:57Z |
| `analyse_t3d.py` returns `EXIT_OK` unconditionally | read at `analyse_t3d.py:408-414` | 2026-09-04T01:08Z |
| no `mark_done_t3d.py`; `mark_done_t3_rff.py` hard-codes `R_ff` | directory listing; `mark_done_t3_rff.py:30` | 2026-09-04T01:04Z |
| T16c's `rc = 0` on four `NOT A RESULT` rows | **NOT VERIFIED BY THIS LANE** — relayed; the record was not located on disk. The mechanism is verified independently at `analyse_t3d.py:408-414` | — |
