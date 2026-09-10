# A3FL2 pre-flight exercise — SUPERVISOR'S GREEN CALL AND VERDICT — 2026-09-10

**GREEN call: `NOT GREEN`. A3FL2 stays `DRAFT / NOT FROZEN` and is NOT enqueued.**
**Exercise verdict on the question it was built to answer: `NOT A RESULT`** — the instrument could not
distinguish its own smoke truncation from the configuration failure it exists to detect, so it
measured nothing about the `nd` lever downstream of the option parser. **One half of it IS a measured
`PASS`** (see §3), and that half is worth having.

The GREEN call and the freeze are the supervisor's alone; this is that call, made personally, on
artifacts I read first-hand and on a lane's report whose load-bearing claims I re-derived myself
before believing them (§4). Recorded `[lab-attributed]` under the owner's 2026-09-10T03:45Z
directive. **SUBMISSIONS PARKED** (rule 7): nothing here is filed, sent or posted anywhere.

**Run root:** `/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE/`
**Ran:** 2026-09-10T05:51:06Z → 05:51:53Z, unattended, **10 hours before this session opened.**
**Image:** `dafoam-subpclu:v1@sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517`

---

## 1. IT HAD ALREADY RUN, AND THE CONTENTION GATE WORKED EXACTLY AS DESIGNED

The board carried this exercise as awaiting dispatch. It was not: `a3fl2_exercise_gate.sh` armed at
2026-09-10T03:59:17Z, **waited 6,709 s**, and released itself at 05:51:06Z on
`loadavg1 5.70 ≤ 8.0` with the D6RF10 R3 container `<absent>` — both halves of its conjunction held
for three consecutive reads. `GATE_RC=0`, `EXERCISE_RC=0`
(`/home/ubuntu/certonomous-runs/a3fl2_exercise_gate_20260910T035917Z_1030927.log`).
**The gate discharged its own contention condition without an agent alive to watch it, which is what
it was built for.** The instruments then correctly REFUSED a second run, because the exercise root
already exists — a guard doing its job, not a failure.

All seven case instruments and both baseline inputs were verified byte-identical to their HEAD blobs
and the image digest matched its registration, at two different HEADs.

## 2. WHAT IT MEASURED — from `exercise_ledger.txt`, read first-hand

| leg | `delta` | rc | wall_s | ranks | core_min | `invalid_option` | traceback |
|---|---|---|---|---|---|---|---|
| CONTROL | `nd` | **1** | 16 | 4 | 1.067 | **no** | yes |
| BASELINE_R3 | `natural` | **1** | 16 | 4 | 1.067 | **no** | yes |
| TEST_R3 | `nd` | **1** | 15 | 4 | 1.000 | **no** | yes |

`A3FL2_EXERCISE_VERDICT=no`, `core_min_total=3.134`, `cap_core_min=48`, `cap_stopped=no`,
`budget_aborted_legs=no`. **No overrun; the cap never bound** (6.5% of it used).

**The frozen GREEN criterion, quoted literally** (`a3fl2_exercise.sh`, enforced as
`{ [ "$rc" = "0" ] && [ "$invalid" = "no" ]; } || GREEN=no`):

> `rc = 0` on **all three** legs **AND** the invalid-option string absent from **every** leg log.

## 3. THE TWO HALVES SPLIT CLEANLY, AND ONLY ONE OF THEM FAILED

- **Half 2 — `PASS`, measured, on all three legs.** `not a valid PYDAFOAM option` appears **zero
  times** in every leg log (verified by count, by me). Each log's DAOption dump carries the lever
  installed and accepted: `jacMatReOrdering nd` in CONTROL and TEST_R3, `jacMatReOrdering natural` in
  BASELINE_R3, alongside `transonicPCOption 1`, `adjStateOrdering cell`, `pcFillLevel 0`,
  `gmresMaxIters 30`. **The A3FL1 confound — an invalid daOption rejected at construction — is CLOSED
  by measurement.** That is a real result and it survives everything below.
- **Half 1 — `FAIL`, on all three legs**, at `rc=1`. Not 124 (deadline) and not 125 (start failure):
  15–16 s wall against a 180 s deadline, so **~165 s of deadline went unused and contention is
  excluded**.

## 4. CRASH TRIAGE — A FINDING ABOUT THE INSTRUMENT, NOT ABOUT THE CONFIG

First error line, identical in all three legs:

    File ".../dafoam/mphys/mphys_dafoam.py", line 345, in solve_nonlinear
      raise AnalysisError("Primal solution failed!")

**Mechanism.** `a3fl2_exercise.sh:98` sets `SMOKE_PRIMAL_ENDTIME=25` and `:171` rewrites each leg's
`controlDict endTime` to it. `processor0/25` exists in the leg directories, so time 25 was reached
and written — **the override ran to its truncated end.** DAFoam then judged the primal against
`primalMinResTol 1e-06` / `primalMinResTolDiff 100`, found it unconverged, and raised. **The adjoint
never started:** `dRdWTPC`, `Mat ReOrdering` and `GMRES Restart` appear **zero times** in all three
logs (verified by count).

**Root cause of the bad override, and I re-derived it myself rather than taking it on report.**
`a3fl2_exercise_gate.sh:24` records the reference run as *"26 primal outer iters ExecutionTime
30.97 s"*. That is a **misreading**. `/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log`
contains **exactly 11 `Time = ` lines** (`Time = 1`, then 100, 200 … 1000), **one**
`Running Primal Solver` banner, and `printInterval 100` at line 440. **The primal ran 1000 outer
iterations and printed 11 blocks.** The "26" figure has no referent in the log, and it is the premise
behind `endTime → 25`.

**Consequence, and this is the finding.** A 25-iteration smoke of a primal that needs 1000 iterations
**cannot** return `rc = 0`, whatever the daOptions say. So half 1 of the GREEN criterion is
**structurally unreachable for this case family**, and the exercise cannot separate its own truncation
from a genuine config failure. `a3fl2_exercise_gate.sh`'s own header warns of exactly this
indistinguishability — *"a tripped leg exits non-zero, which the GREEN criterion reads as rc != 0 and
therefore NOT GREEN — INDISTINGUISHABLE from a genuine config failure"* — anticipating it from
contention, and it arrived from the smoke override instead.

**Class: NEW, and it is the third class in this family, not the A3FL1 class.** A3FL1 was an invalid
daOption rejected at construction; that string is absent here and the option dictionary printed. This
is *the pre-flight instrument's own smoke override making its GREEN criterion unreachable.*

**And it is the third item today killed by the same DAFoam clause.** A2-B2R
(`cases/dafoam/A2_B2R_INDEPENDENT_TRIM_TRIAGE_2026-09-10.md`, `3b1b4cae`) and D6RF10 R3
(`.../curriculum_D6RF10/D6RF10_GRADE_RECORD.md`, `cadc459c`) carry the same
`mphys_dafoam.py:345` raise, on a different case and a different image. Here the trigger is a
deliberately truncated horizon and the abort is arguably correct behaviour; on A2-B2R it destroyed a
row whose physics had already passed its gates. **Same clause, three items, two images — that is now
the dafoam family's largest single blocker**, and a lane is establishing the clause's definition from
DAFoam's source.

## 5. COST (rule 12) — a MISPREDICTION, and NOT waste

Registered: cap **48 core-min**, most-likely **34 core-min** (`A3FL2_EXERCISE_START` ledger line).
Actual: **3.134 core-min** = 0.0522 core-h → **$0.0027 DERIVED, NOT MEASURED** at $0.0513/core-h,
reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing). 0 GPU-h.
**Ratio actual/predicted = 0.092.**
**Attribution: misprediction, not waste, and not contention.** AMENDMENT A1 sized both R3 legs at the
180 s deadline on the ground that ~119 s of `dRdWTPC` assembly is mandatory. The adjoint never ran, so
that cost was never incurred — the estimate priced work the instrument's own override prevented.
Termination was the exercise's own end (all three legs ran, DONE marker written), **not** cap,
deadline or harness crash. **Waste, named separately per charter §6: 0 core-min** — the 3.134
core-min bought §3's measured PASS on option acceptance and §4's instrument diagnosis, both of which
stand.

## 6. WHAT FOLLOWS, AND WHAT I AM NOT DOING

- **A3FL2 is NOT frozen and NOT enqueued.** The freeze cannot proceed on a GREEN that does not exist.
- **No frozen file is edited here** (rule 6). The exercise script, the gate script and the
  pre-registration are untouched; the corrections §4 identifies — the `SMOKE_PRIMAL_ENDTIME` value,
  how a truncated primal's `rc` is interpreted, and the stale *"26 primal outer iters"* line — are
  **named as needed, not made.** Since **no compute has been spent on the GRADED arm**, a
  pre-first-compute amendment is legal under rule 2 provided it **states the condition and how it was
  checked** (the graded A3FL2 run root does not exist), and it must **not** move a gate, threshold,
  cap or label. Re-running the exercise additionally needs
  `/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE/` archived by `mv`, which is a departure to
  be recorded, not performed silently.
- **§4's `nd` proof is only HALF closed, and that is the decision-relevant gap.** The exercise proves
  *pyDAFoam's option parser* accepts `nd`. It does **not** prove PETSc accepts it at KSP setup: the
  required `Mat ReOrdering: nd` echo is absent from every log because the adjoint never ran. **The
  A3FL1-class risk — an option that installs and is rejected downstream — remains open**, and no
  freeze should treat it as closed.
- **A re-run should not be attempted at the current box reading.** Load was 21.12 at 15:51Z with
  foreign solvers live, above the gate's own 8.0 release condition — the gate would refuse, correctly.
