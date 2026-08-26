# D12R PHASE 1 — THE FROZEN COMPARATOR REFUSES, AND THE REFUSAL IS THE FINDING

**Dated 2026-08-26.** Lane: dafoam `lab-lane`. Item: **D12R**, pre-registration frozen at
**`f9c8b9c8`**. Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

**Nothing in this record was written by editing a frozen file.** `d12x_grade.py`,
`d12x_run_script.py`, `d12x_stage_and_run.sh` and `PREREGISTRATION.md` are **byte-unchanged**
(§1). The comparator was **not patched to get past its own refusal**, and no manifest row was
edited to dodge one.

---

## 1. THE GRADING PATH WAS VERIFIED BEFORE IT WAS RUN (rule 2)

`git hash-object` on the worktree file against `git rev-parse f9c8b9c8:<path>`, all four
instruments, **before** any grading:

| file | blob at `f9c8b9c8` | HEAD | worktree | |
|---|---|---|---|---|
| `d12x_grade.py` | `b1602722c13ecb2aba6b85b7c6c4f570613fd917` | same | same | **IDENTICAL** |
| `PREREGISTRATION.md` | `21135c70b6ed2c0e3aaa51e2b840398d96d865e8` | same | same | **IDENTICAL** |
| `d12x_run_script.py` | `0e7bd431d66cec7008c22d06d5660a4a6bb49382` | same | same | **IDENTICAL** |
| `d12x_stage_and_run.sh` | `7acc6bd4b534184b8f7695dfa5352f9eb8835064` | same | same | **IDENTICAL** |

**The file that ran IS the file that was frozen.** Rule 2's grading-path clause, executed.

### 1.1 The selftest, run immediately before grading

`python3 d12x_grade.py --selftest`, **`rc = 0`**:

- **units REGISTERED (frozen constant) 72, units in the list 72, units that RETURNED A RESULT 72, failures 0.**
  The count is checked three ways because the frozen constant is what stops the tautology
  the pre-registration §6 item 2 records catching in this lane's own draft.
- **GATES THE SELFTEST EXERCISES (14):** `G12R-0 1 10 11 2 3 3b 4 5 6 7 8 9 W`.
  **GATES EMITTED BUT NEVER EXERCISED: (none).**
- `--assert-audit`, **`rc = 0`**: **0 `assert` statements**, by AST on statement type — the
  §6 requirement that the battery survive `python3 -O`.

The selftest's own printed caveat is adopted rather than paraphrased: *"COUNTING UNITS MEASURES
THIS SELFTEST'S SIZE, NOT ITS COVERAGE."* **72 is a size. The 14-gate list is the coverage claim.**

---

## 2. THE VERDICT

Command run, verbatim from `ledger.txt`'s own handoff line (its last instruction):

    python3 .../d12x_grade.py --manifest <root>/manifest.jsonl --root <root> --plan

**`rc = 2`**, and the whole of stdout/stderr is one line:

    REFUSAL: G12R-0 S1a: JSON status=None

| gate | verdict | number | artifact |
|---|---|---|---|
| **G12R-0** (completion) | **REFUSAL, exit 2** | refused on stage **1 of 32**, `S1a` | `manifest.jsonl` row 0; `d12x_grade.py:204-205` |
| G12R-1, G12R-2, G12R-3, G12R-3b, G12R-4 | **not reached** | — | — |

> **PHASE 1 IS `NOT A RESULT`.** `G12R-0` is registered refusal-only (`PREREGISTRATION.md` §7)
> and it is the **first** gate in `plan()` (`d12x_grade.py:1520`). It refused on the **first
> row**, so **no later gate ran and no number was produced**. `step_plan.json` **does not
> exist**. This is `CLAUDE.md` rule 4's *"comparators refuse (exit 2) rather than degrade"*
> working exactly as written — **the refusal is not a malfunction of the instrument.**

**Zero graded output, for the second time on this case.** The superseded `curriculum_D12`
phase 1 also produced zero graded output (`PREREGISTRATION.md` §0). **The mechanism is
different and is recorded in §3 rather than left to be rediscovered.**

### 2.1 Nothing was imported from the superseded item to fill the gap

`PREREGISTRATION.md` §2 records three prior measurements as **NOT IMPORTED** — 221 sign
changes / p2p 19.40 % / mean `CD = 0.6563506540`; period 18.9955 steps; `δ_window = 1.274958e-03`.
**None was used here, and none could have been:** the gates that would corroborate or depart
from them (`G12R-1`, `G12R-3`) **never ran**. There is neither a corroboration nor a departure
to report — **there is an absence**, and it is reported as one.

---

## 3. THE TWO OPEN GAPS, CLOSED — AND THE SECOND ONE IS THE CAUSE

### 3.1 GAP (a): `ExecutionTime` count vs `endTime` — **NOT A DEFECT, AND REGISTERED AS SUCH**

The concern was that eight non-primal stages carry `execution_time_count != endTime`. **The
frozen comparator does not gate that at equality and says so in its own text.** `d12x_grade.py`
lines 227-232, verbatim:

    # THE STEP COUNT.  rule 4's "ExecutionTime count == endTime" limb, in the form
    # this solver carries it: the primal writes one `Time = ` line per timestep, so
    # that count must EQUAL the registered number of steps.  `ExecutionTime` lines are
    # counted too and reported, but a compute_totals stage emits them in the adjoint
    # sweep as well, so that count is required only to be >= the step count -- stated
    # rather than quietly gated at equality it cannot meet.

and the code that carries it (lines 258-261, inside `elif exp:` at 253, i.e. **unsteady only**):

    etc = st.get("execution_time_count")
    if etc is None or etc < exp:
        raise Refusal(...)

**So the gated quantity is `time_line_count == expected_steps` (EXACT), plus
`execution_time_count >= expected_steps`.** Measured on all 32 rows of `manifest.jsonl`:
**`time_line_count == expected_steps` on 31 of 31 unsteady rows**, including every row the
concern named — S4_n20 `20 == 20` (etc 25 ≥ 20), S4_n40 `40 == 40` (etc 45 ≥ 40), S4_n80
`80 == 80` (etc 85 ≥ 80), S5 `300 == 300` (etc 315 ≥ 300).

`S1a` is `stage_kind = "steady"`, where the comparator does **not** gate the step proxy at all
(lines 247-250: *"`Time =` is an OUTER-ITERATION print governed by the solver's own print
interval and is NOT a step count. It is recorded and REPORTED, never gated."*). Its `6` `Time =`
lines against `500` registered outer iterations is **the exact comparison the D4 repair was
written to stop making** (`PREREGISTRATION.md` §5, D4).

> **GAP (a) IS CLOSED AS "WORKING AS REGISTERED".** The divergence is anticipated in the
> comparator's own comment, its direction is gated (`>=`), and the exact-equality limb is met
> on every stage that carries one.

### 3.2 GAP (b): the `status` key — **THE COMPARATOR IS NOT BLIND. IT SEES IT AND REFUSES.**

**First, a correction to the brief this lane was given.** The brief said the `S1a` row has *"no
`status` key at all"*. **It is not absent.** `manifest.jsonl` row 0 carries **28 keys including
`status`**, whose JSON value is **`null`**:

    ..., "stage_kind": "steady", "status": null, "task": "shell", "time_line_count": 6, ...

The comparator's behaviour is identical either way — `dict.get()` returns `None` for both — but
**the record should say what is on disk.**

The check, `d12x_grade.py` lines 204-205:

    if st.get("status") != "COMPLETE":
        raise Refusal("G12R-0 %s: JSON status=%r" % (nm, st.get("status")))

`None != "COMPLETE"` is **True**, so it **refuses**. **This is NOT the L-302 shape.** An
instrument that silently treated absence as pass would be the defect; this one **cannot be
handed a missing status without saying so**, and its refusal is what produced this record.
**No planted control was needed to establish that, because the live run supplied the non-zero
case itself** — the reader was shown able to say NO by saying it.

### 3.3 THE ACTUAL DEFECT: **THE LAUNCHER EMITS A ROW ITS OWN COMPARATOR MUST REFUSE**

Both instruments are frozen at the **same commit**, `f9c8b9c8`, and **they disagree.**

`d12x_stage_and_run.sh` writes the stage's `status` **only** from a per-stage JSON, and has an
explicit `else` branch for a stage that has none (lines 377-413):

    jf = os.path.join(D, "d12x_%s.json" % stage)
    if os.path.isfile(jf):
        ...
        row["status"] = j.get("status")
        ...
    else:
        row["status"] = None

**`S1a`'s `task` is `shell`.** It runs the `potentialFoam` + `simpleFoam` spin-up through
`runPrimalSimple.py`, **not** through `d12x_run_script.py`, so **`d12x_S1a.json` is never
written** — confirmed absent on disk; `S1a/` holds `0 0_orig 500 FFD constant d12x_run_script.py
genMesh.py runPrimalSimple.py surfaceMesh.xyz volumeMesh.xyz` **and no `.json`**. `ledger.txt:14`
records the stage as `STAGE=S1a TASK=shell rc=0 wall_s=13`.

> **THE LAUNCHER, BY DESIGN, PRODUCES `status: null` FOR A `shell` STAGE. THE COMPARATOR, BY
> DESIGN, REFUSES ANY STAGE WHOSE `status` IS NOT `"COMPLETE"`. NEITHER IS WRONG ALONE; THE
> PAIR CANNOT GRADE PHASE 1.**

**And the shape is one this very item already diagnosed and repaired — in the limb next door.**
`PREREGISTRATION.md` §5 D4 ruled that *"every stage declares its kind; `G12R-0` REFUSES on an
unknown kind rather than comparing incomparable counts, gates the step proxy only on unsteady
stages, and reports it on steady ones."* **That stage-kind awareness was given to the step-count
limb and NOT to the status limb, thirty-six lines above it (204 vs 240).** The status limb asks a `run_model`
question of a `shell` stage — **a check of the wrong quantity for that stage kind, which is the
D4 class, inside the gate the D4 repair was written into.**

**This is a defect of the INSTRUMENT PAIR, not of the solve.** The 31 other rows are clean on
every clause: `rc=0`, `docker_exit=0`, `oomkilled=false`, `end_line_present=true`,
`age_guard_ok=true`, `coldstart_ok=true`, `last_time == endTime` on **32/32**, and
`time_line_count == expected_steps` on 31/31 unsteady rows.

---

## 4. PHASE 2 WAS NOT LAUNCHED, AND THE FROZEN LAUNCHER AGREES

Phase 2 was armed under this same committed pre-registration, and **that was verified before
any launch was attempted**: `f9c8b9c8` carries the phase-2 stage list
(`d12x_stage_and_run.sh:742,744` — `S6_s${k}_p` / `S6_s${k}_m`) and the caps
(`CAP_CORE_MIN_REGISTERED="600.0"`, `CAP_S8_REGISTERED="350.0"`, lines 103-104, asserted equal
at lines 147-150). **No new freeze was owed. Phase 2 still cannot run**, and not merely as this
lane's judgement — the frozen launcher **refuses it itself** (line 727):

    PLAN="$ROOT/step_plan.json"
    [ -f "$PLAN" ] || { echo "ABORT: $PLAN absent -- run the comparator in --plan mode first"; exit 1; }

**`step_plan.json` does not exist** because the comparator refused before writing it. The
launcher does not compute, round or choose the sweep steps (`RULING-3.3`), so **there is no
phase 2 to launch, only a phase 2 that would abort.** **Nothing was launched; nothing was spent.**

**Not a memory hold.** `MemAvailable` at the time of this record is **27 GiB**, well above the
registered **14.0 GiB** floor, and the three live heat-transfer `buoyantBoussinesqSimpleFoam`
solvers (PIDs 2203927 / 2203944 / 2203947, ~10 h 29 m elapsed) **were not touched**. **The queue
is idle for a reason that is a finding, not for want of capacity.**

---

## 5. WHAT THIS LANE DID NOT DO, AND WHY

Three routes past the refusal exist. **All three are refused at this level.**

1. **Patch `G12R-0` to exempt `shell` / `steady` stages.** This **alters a gate**, and gates are
   **CLOSED** after first compute (rule 2). §2d.1's repair exception is four-condition and was
   cut for a comparator defect; **this is not a comparator defect** (§3.2 — the comparator is
   the instrument behaving correctly). **Refused.**
2. **Set `blocked: true` on the `S1a` row**, which `plan()` filters at line 1518 (and `plan2`/`plan3` identically at 1621/1671)
   (`if not r.get("blocked")`). This is **editing the evidence to dodge a refusal**. **Refused,
   and it is the worst of the three** — it would produce a full set of gate numbers with nothing
   on the record saying a stage had been removed from the completion check.
3. **Re-run `S1a` to produce a JSON.** It would break the age-guard/cold-start chain the other
   31 rows rest on, and `run_stage`'s own guard refuses a case where a time directory exists.
   **Refused.**

**The supervisor's call, and the precedent is in this item's own §0:** the superseded D12's
defect 3 was *"in the FROZEN DOCUMENT ITSELF"* and was ruled **one re-registration, not four
patches** (`SUPERVISOR_D12_PHASE1_RULINGS.md` §7, `93966756`). **This is the same class.**
**Phase 1's 32 stage directories, logs and `manifest.jsonl` are preserved byte-for-byte and are
not deleted, cleared or re-run** — whatever is ruled, the compute is recoverable, which is why
§6 does not call it waste.

---

## 6. STANDING CAVEATS — CARRIED, NOT DROPPED

**These are repeated here in full because a record that quotes this item and drops them is the
failure they were registered to prevent.**

1. **`St` IS NEVER TO BE QUOTED AS A STROUHAL NUMBER.** The superseded item measured a period of
   18.9955 timesteps, giving `f ≈ 5.26 Hz` and **`St ≈ 0.5264`, roughly 2.6× the accepted ≈0.2**.
   On a **2,450-cell 2D URANS mesh with wall functions** that is **a RESOLUTION ARTIFACT** far
   more likely than a discovery. The estimator is **mean-crossing**, which underestimates the
   fundamental on a harmonic signal, so **18.9955 is a LOWER bound on the period and 0.5264 an
   UPPER bound on `St`**. It is a **window-sizing diagnostic and nothing else**. No
   mesh-convergence study is bought here, so **the artifact hypothesis is neither tested nor
   refuted** (`PREREGISTRATION.md` §2.1). **This item graded nothing, so it did not even
   re-measure it.**
2. **D12 MAY BE A CASE WHERE THE FD BRIGHT LINE CANNOT BE CROSSED AT ALL.** Direction-only
   arithmetic on the prior `δ_window = 1.27e-03` gives `h_min ≈ 1.10` against the registered
   `h_max = 0.05` — **~22× over**. That would be **a GENUINE FINDING ABOUT THE METHOD-CASE PAIR,
   NOT A FAILURE OF EITHER**; the `G12R-4` no-admissible-step branch is **a RESULT**
   (`PREREGISTRATION.md` §2.2). **It is registered in advance precisely so it can never be read
   as a consequence of an instrument defect** — and note that **this refusal is an instrument
   defect and is a DIFFERENT thing**; the two must not be conflated.
3. **Neither caveat softens the verdict.** Phase 1 is **`NOT A RESULT`**. Neither is a reason to
   call it anything else, and neither is a reason to call it worse.
4. **`G12R-4`'s branch was NOT reached.** The `h_min ≈ 1.10` figure above is **prior, carried,
   NOT re-measured by this item**, and this item is **not** entitled to state the
   no-admissible-step outcome as its own finding.

---

## 7. COST

**Phase 1: predicted ~70 core-min (`PREREGISTRATION.md` §8); actual 63.95 core-min; ratio 0.914.**
Measured from `ledger.txt`'s last substantive line, `PHASE1_COMPLETE spent=63.95 core-min`,
against a registered total guard of **`CAP_CORE_MIN = 600.0`** — **no overrun, no cap moved.**
**Grading and this record cost no compute.** Full attribution and the derived-dollar labelling
are the calibration row **`C-100`** in `docs/COST_CALIBRATION.md`.

**cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing).
