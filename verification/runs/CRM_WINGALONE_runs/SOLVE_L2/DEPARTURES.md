# CRM WING-ALONE L2 — DEPARTURES AND RULINGS ON THE RECORD

**This file alters NO gate, threshold, cap or label.** It is a run-side record, not an
amendment: `verification/campaign/CRM_WINGALONE_FLOW_PREREGISTRATION.md` is frozen and is
not edited here or anywhere. Every registered value below was read from the **HEAD blob**
of that document, never from the worktree copy (which is 236 lines against HEAD's 459 and
predates both signed addenda).

---

## D1 — THE RUN IS ON 6 RANKS. §8 REGISTERED 4.

| | value | source |
|---|---|---|
| registered | **4 ranks**, ~10,800 s, 720 core-min | §8 O5 cost table, HEAD blob |
| actual | **6 ranks** | `/proc/2847774/cmdline` = `mpirun -np 6 rhoSimpleFoam -parallel`; `STATUS.solve:ranks=6` |

**WHY IT IS RECORDED RATHER THAN ABSORBED INTO THE COST LINE. Rank count is not free.**
MRF R2 was graded `NOT A RESULT` in part because its three levels ran on **2 / 2 / 6 ranks**
— an uncontrolled arm on a non-deterministic scotch partition, where the level that differed
in rank count is exactly the level that failed.

**FOR CRM IT CONFOUNDS NOTHING, AND THE REASON IS STRUCTURAL, NOT LUCKY.** This family has
**one** mesh-admissible level (§D3), so there is no cross-level comparison for a rank
difference to contaminate. **It is recorded so that nobody later builds a comparison on
this run unaware that its rank count differs from the registered one.**

## D2 — THE 1,500 CORE-MIN CAP IS A PREDICTION SCORED AT COMPLETION. IT IS NOT A KILL.

§8 registers `CAP: 1,500 core-min` and adds "an overrun STOPS the run". **That clause does
not operate.** Sanaa has ruled four times, most recently verbatim: *"NOOO CAP. NO MORE CAPS.
NO RUN GETS STOPPED BC OF A TIME OR BUDGET CAP."* Retiring a cap is the owner's call and she
has made it in her own words. The cap therefore becomes what DrivAer's already is — a
**rule-12 prediction, scored at completion**.

**NO ARMED INSTRUMENT ON THIS RUN CONTAINS A KILL PRIMITIVE.** `launch_crm_l2.sh`,
`GRADER/autograde_crm_l2.sh` and `GRADER/grade_crm_l2.py` were swept: every occurrence of
`kill`, `timeout`, `cap` or `budget` in any of them is inside a comment. Nothing on this run
can stop it on clock or spend.

**THE OVERRUN, ATTRIBUTED — CONTENTION, NOT MISPREDICTION.** The two are named separately
per `COMPUTE_BUDGET_CHARTER` §6 and the gap is never folded into the ratio.

| figure | value |
|---|---|
| registered estimate | 720 core-min |
| registered cap | 1,500 core-min |
| projected total, **gross** (wall x 6 ranks) | **2,932 – 3,301 core-min** = 1.95 – 2.20x the cap |
| projected **contention-free** equivalent (from `ExecutionTime`) | **1,020 core-min** = **1.42x the estimate** |
| contention at 06:08Z | `ExecutionTime/ClockTime` = **0.397**, at load ~49 on 16 physical cores |

**The estimate was good on CPU time. The excess is the box being shared, and it is named as
such rather than charged to the prediction.** Derived $2.51 at $0.0513/core-h — **derived,
not measured**; this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).

**THE COST ROW IS RECOVERABLE WITHOUT A LIVE AGENT.** `launch_crm_l2.sh` writes
`solver_wall_s`, `solver_ranks`, `solver_core_min`, `reconstructPar_wall_s` and
`total_core_min` into `STATUS.solve` on exit, and `log.rhoSimpleFoam` carries the
`ExecutionTime`/`ClockTime` pair needed to split contention from misprediction. No agent
needs to be alive at landing for the calibration row to be computed.

## D3 — G-S2 IS GATED ON PEAK-TO-PEAK. RULED BEFORE THE GATE COULD FIRE.

§7 G-S2 reads "max |ΔCd| over the **last 500 iterations**". That admits three readings —
peak-to-peak, max single-step, end-to-end. **The cfd-supervisor ruled peak-to-peak, ahead of
the gate firing**, on the ground that it is the strictest of the three (peak-to-peak is
≥ max single-step and ≥ end-to-end by construction), so a strictest reading of an ambiguous
frozen text **can only turn a PASS into a GATE FAIL, never the reverse** — the safe
direction, and the one that cannot be accused of having been chosen to fit the answer.

**The threshold is not changed and the clause is not re-worded.** The ambiguity is a defect
in a frozen document: **disclosed, not repaired** (rule 6). `grade_crm_l2.py` prints **all
three** measures beside the verdict so a reader sees which one gated and what the others
would have said.

## D4 — WHY NO GRID-CONVERGENCE CLAIM EXISTS FOR THIS CASE

`GATE_TABLE.md` (committed) grades all three mesh levels against the registered mesh gates:

| level | cells | outcome |
|---|---:|---|
| L1 | 144,768 | **`GATE FAIL`** on G-M4 — min layer quality **-0.05046** at layer 3 |
| **L2** | **1,158,144** | **PASS on every registered limb** (G-M1 68.2589 deg, inside the 65-70 warning band) |
| L3 | 9,265,152 | **`GATE FAIL`** on G-M1 — **79.3672 deg** against a 70 deg ceiling |

**Exactly one admissible level, and the running solve is on it** — 1,158,144 cells, confirmed
in this run's own `log.checkMesh`. §6 of the registration declared this **before compute**:
*"A p and a GCI need three admissible meshes. This family has one."* **Any grid-convergence
row for CRM wing-alone is `NOT A RESULT`**, and `grade_crm_l2.py` computes no observed order
and no GCI. Nothing is faked to fill the gap.

*On the record by a cfd `lab-lane`, 2026-09-12, under the cfd-supervisor's two rulings of the
same date. No gate, threshold, cap or label is altered. Submissions parked. No agent's
message is Sanaa's consent — D2 rests on Sanaa's own words, relayed with their provenance
named.*

---

## D5 — THE COST ROW IS NOW WRITTEN AUTOMATICALLY (added 2026-09-12, after D1–D4)

D2 records that the cost row is *recoverable by hand* from `STATUS.solve` and
`log.rhoSimpleFoam`. It is now also **written without anyone being alive to do it**:
`GRADER/cost_row_watch_crm_l2.sh` + `GRADER/cost_row_crm_l2.py`, armed detached at
2026-09-12T06:16:19Z, fire on the same `solve_rc` and emit `COST_ROW.txt`.

**IT IS NOT A SECOND GRADER, AND THAT IS MACHINE-ENFORCED RATHER THAN PROMISED.** Before
writing, the writer scans **its own output** for every token in rule 1's vocabulary and
**refuses (rc 2)** if it finds one, leaving `COST_ROW.REFUSED.txt` instead. A later reader
can re-run that check. It writes only `COST_ROW.txt`, `COST_ROW.log`, `COST_WRITER_RC.txt`
and `COST_ROW.REFUSED.txt`; it writes **no** grader-owned file, **no** `rc` the grader reads,
and nothing in `0/`, `4000/` or `postProcessing/`. If it fails, grader and run are untouched.

**IT REFUSES THE SPLIT RATHER THAN GUESS IT.** Its selftest produced a confident-looking
"0.32× misprediction" by reading a live log against a completed `STATUS.solve` — two sources
describing different runs. It now asserts the log's final `ClockTime` agrees with
`solver_wall_s` to within 10 % and, if not, **prints both numbers and declines to compute the
contention split**. A number that can be silently wrong is worse than one refused.

**Why this overrides the earlier "nothing further to launch":** the cfd-supervisor took the
call explicitly, on the ground that rule 12 makes calibration part of a completion and no
relay retires a standing rule — and that this session has already died once tonight, taking
three lanes with it. CRM lands ~6.5 h out.
