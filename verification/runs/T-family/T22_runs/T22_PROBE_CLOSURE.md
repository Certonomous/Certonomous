# T22 — PROBE CLOSED. Dated disposition record. NO VERDICT EXISTS AND NONE MAY BE QUOTED.

**Date:** 2026-09-03. **Author:** heat-transfer `lab-lane`, on the
heat-transfer-supervisor's dispatch. **Zero new compute.** Every figure below was
re-read from the artifacts in this tree today; none was carried from a summary.

---

## 0. Why this file exists

`CLAUDE.md` rule 2 exists to prevent an unregistered run tree that implies a
result. This tree held, until today, three pre-outcome documents —
`T22_FEASIBILITY_NOTE.md`, `T22_LAUNCH_1_TRIAGE.md`, `T22_LAUNCHER_REPAIR.diff` —
a `queue_drafts/` directory, **and a completed 5 000-iteration solve with fields
on disk at `T22_CHTb_L1/5000/`**, and nothing on the face of the tree that closed
it. A cold reader could have opened those fields and quoted a number from them.
**This file closes the tree.** It creates no gate and grades nothing.

**Disposition chosen: RECORD AS A CLOSED, UNGATED FEASIBILITY PROBE.**
Prospective registration was considered and **refused**: nothing in this family
names a reference dataset for a three-region conjugate wedge, so no gate,
threshold or band could have been written that was not invented after the fact.
A graded T22 remains possible and would freeze **its own** pre-registration and
**run again** — the fields in this tree are evidence about the numerics and are
not that registration's answer.

---

## 1. What T22 is, restated so this file stands alone

**T22 IS UNREGISTERED.** No `T22_PREREGISTRATION.md` exists in the working tree
or at any commit. `T22_FEASIBILITY_NOTE.md` in this directory is **not** a
pre-registration, says so on its own first line, and does not become one by being
cited. The run was queued under `prereg_commit: "FEASIBILITY"`, the tag Sanaa
ruled queue-legal on 2026-08-31 (`etc/sessions/2026-08-31T1551Z_sanaa_queue_ruling_yes_yes.md`),
whose own terms are that such outputs *"are never gradeable as verdicts."*

Consequently, and repeated here rather than left to inference:

- **No number in this tree may be quoted as a measured result, a deviation, or a
  comparison against any reference.**
- **No word of the fixed vocabulary applies to T22** — not `PASS`, not
  `GATE REACHED`, not `GATE FAIL`, not `NOT A RESULT`. Those five grade a
  registered gate; there is no gate here.
- **Nothing here may reach a demo screen, a certificate, or a table cell.**
- **Nothing here carries into a future graded T22.**

---

## 2. What was tried

Two launches of one case, `T22_CHTb_L1`: `chtMultiRegionSimpleFoam` (OpenFOAM
v2606) on a three-region 5-degree wedge — `fluid` 35 200 cells + `housing` 1 120
+ `core` 3 360 = **39 680 cells** — with **two conjugate `mappedWall`
interfaces** and a sector-scaled volumetric source in the innermost solid.
Serial, 1 rank, `endTime` 5 000, `writeInterval` 5 000.

| launch | when | outcome |
|---|---|---|
| 1 | 2026-08-31T16:35:11Z, pid 140701 | **died in the same second, before the solver line.** `run_t22.sh` sourced the OpenFOAM `bashrc` with `set -u` in force; the bashrc aborts the shell on `WM_PROJECT_DIR: unbound variable`, and a `>/dev/null 2>&1` on the source swallowed the message. `log.solve` absent, `launcher.queue.out` 0 bytes. Evidence preserved unmodified at `T22_CHTb_L1_FAILED_LAUNCH1_20260831T163511Z/`; triage in `T22_LAUNCH_1_TRIAGE.md`. |
| 2 | 2026-08-31T17:07:37Z → 17:21:42Z | **completed.** Repair per `T22_LAUNCHER_REPAIR.diff`, copied from `T20_runs/run_one_t20.sh`: `set +u` across the source, `\|\| true` on it, and a post-source `command -v` refusal so a future environment failure is loud rather than silent. |

---

## 3. What was learned — the ONE QUESTION, answered

> **Does `chtMultiRegionSimpleFoam` advance this THREE-REGION 5-degree WEDGE
> case — `fluid` + `housing` + `core`, TWO conjugate `mappedWall` interfaces,
> and a sector-scaled volumetric source in the innermost solid — from its
> `0.orig` state without dying, and do its residuals fall?**

**YES on both limbs, on launch 2.** This is an observation about the solver's
execution on this mesh. It is not a result about heat transfer.

### 3.1 Completion, `CLAUDE.md` rule 4 clause by clause, re-measured 2026-09-03

| clause | reading | measured |
|---|---|---|
| 1. `rc = 0` | `STATUS.T22_CHTb_L1` carries `launcher_rc=0`. **DERIVED, NOT READ** — see §5 defect (1). | derived |
| 2. an `End` line | count **1** in `log.solve` | ✔ |
| 3. last time == `endTime` | last `Time = 5000`; `endTime 5000` | ✔ |
| 4. fields present at `endTime` | `5000/fluid/` T U alphat k nut omega p p_rgh phi rho; `5000/housing/` T p; `5000/core/` T p | ✔ |
| 5. `ExecutionTime` count == step count | **5 000** `ExecutionTime` lines, 5 000 `Time =` lines | ✔ |
| 6. **age guard** | every `5000/**` field NEWER than the case's own dating file | ✔ |

**The dating file for this case is `0/housing/T`, not `0/T`.** This case is
**multi-region** (`constant/regionProperties` present); `0/T` does not exist and
asserting it would itself be a defect. `run_t22.sh` touches `0/housing/T` last,
immediately before launch, so that file dates the run allowed to produce the
answer. Measured today: `0/housing/T` at 17:07:37.534Z, earliest `5000/` field
17:21:41.530Z — **844 s later**. The guard was also re-run against `0/fluid/T`
and `0/core/T` independently: **PASS on all three**, zero stale fields under any
of them.

### 3.2 Residuals

Initial residual, first solved step → last solved step:

| equation | Time = 1 | Time = 5000 | fall |
|---|---:|---:|---:|
| `Uy` | 9.9999e-01 | 6.2525e-10 | 9 orders |
| `Uz` | 1.0000e+00 | 4.2235e-12 | 11 orders |
| `h` | 1.3644e-04 | 9.5859e-10 | 5 orders |
| `k` | 1.0000e+00 | 9.7301e-10 | 9 orders |
| `omega` | 1.9662e-01 | 6.0908e-10 | 8 orders |
| `p_rgh` | 1.0000e+00 | 8.6363e-09 | 8 orders |
| **`Ux`** | 9.9993e-01 | **1.3529e-01** | **flat from step ~50** |

**`Ux` DID NOT FALL, AND THAT IS NOT A CONVERGENCE FAILURE.** Re-measured today
over the last 100 steps: min 1.322e-01, max 1.406e-01, mean 1.358e-01 — a flat
band, not a descent and not a growth. **`Ux` is the identically-zero
circumferential component of a wedge**: the calibration row
`C-20260831T172527.907664Z-b006f781` in `docs/COST_CALIBRATION.md` records
max|Ux| = **3.84e-15** in the final field against max|Uz| = **20.90 m/s**
[MEASURED, `5000/fluid/U`, 35 312 vectors]. The normalised residual is a ratio
whose denominator is machine zero. **A reader that greps the last `Ux` residual
would report every run of this family as unconverged.** That finding was already
on the record before this closure; this file reproduces the flat band
independently and does not restate the mechanism as new.

---

## 4. What it cost, and the waste, named separately

**Unit: core-minutes (wall s × ranks ÷ 60), `CLAUDE.md` rule 12.** RANKS = 1
throughout, so core-min == wall-min on every figure here.

| | core-min | basis |
|---|---:|---|
| registered POINT estimate | **15.4** | `T22_FEASIBILITY_NOTE.md`, derived before launch from two MEASURED Cartesian single-solid anchors (`T5_CUBE_m` 4.1541e-06, `T5_CUBE_f` 4.6476e-06 s per cell-iteration), taking the conservative `_f` end |
| registered CAP | **50.0** | enacted as `timeout 3000s` inside the wrapper, 3.25× the point |
| **actual, launch 2** | **13.9872** | `ExecutionTime = 839.23 s` read from `log.solve`, × 1 rank ÷ 60 |
| actual, launch 1 | **≈ 0.0** | the shell aborted inside `etc/bashrc` before the solver line |
| **ratio actual/predicted** | **0.908** | |
| cap utilisation | **28.0 %** | no overrun; the cap stopped nothing |

**WASTE, NAMED SEPARATELY AND NOT ABSORBED INTO THE RATIO** (rule 12,
`COMPUTE_BUDGET_CHARTER.md` §6): launch 1 spent **0.0 core-min** of solver
compute — it bought nothing and it also cost nothing. What it did cost is **one
launch slot and one queue entry**, which is not a core-minute figure and is not
converted into one here. Gross and cleaned are identical: the charter §2 stall
rule matches a row over 3 600 wall s, and this run is 839.23 s, so no judgement
enters the figure.

**Dollars: $0.011959, DERIVED — NOT MEASURED**, at the owner-stated c7a.4xlarge
$0.0513/core-h (REPORTED-BY-OWNER 2026-08-21/22). The box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**The estimate-versus-actual comparison rule 12 requires is already filed**, as
row `C-20260831T172527.907664Z-b006f781` of `docs/COST_CALIBRATION.md`, and its
figures were re-derived from the artifacts today and reproduce. **This file adds
no second calibration row and must not be read as one.**

---

## 5. What is NOT settled, stated rather than smoothed

1. **`rc = 0` is derived, not read.** The queue runner and the wrapper both write
   `STATUS.<case_id>`, the runner's write lands last, and **0 of the wrapper's
   own fields survived**. The surviving `launcher_rc=0` is the exit status of
   `bash run_t22.sh`, whose final line propagates the solver's captured `$rc` —
   so for this wrapper it *is* the solver rc. This is a bookkeeping defect and it
   **does not void the physics** (Sanaa's universal rule 2026-08-26). It is
   recorded, not repaired here.
2. **Whether the wedge/two-solid stack produces physically right answers is
   untouched.** This probe measured that the solver advances and that residuals
   fall. It measured nothing against any reference, and no reference is named.
3. **`queue_drafts/` is left as it stands.** It holds `T22_CHTb_L1.json` and
   `T22_CHTb_L1_R2.json`, both already consumed by the runner and both present
   under `verification/queue/heat-transfer/launched/`. They are drafts of
   consumed entries, not pending work.

---

## 6. Authority

Filed by a heat-transfer `lab-lane` at the heat-transfer-supervisor's dispatch;
decisions `[lab-attributed]`. **Nothing here has been sent, filed, submitted,
uploaded, registered or posted outside this box** (`CLAUDE.md` rule 7). No
agent's message is Sanaa's consent (rule 9); the session file cited in §1 is the
chief's verbatim capture of her own words and is cited as such.
