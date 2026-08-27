# F24-PRANDTL-MEYER — supersonic expansion corner (`rhoCentralFoam`, 4 ranks) — GRADED RECORD, PARTIAL LADDER

Team cfd. Pre-registration `verification/campaign/F24_PRANDTL_MEYER_PREREGISTRATION.md`
frozen at **`260ff3c13e6877183a508c34ecd8e12886ed9a45`**. Launched by the queue runner
with no agent attached; `STATUS.F24_PRANDTL_MEYER` reads `launcher_rc=3
end=2026-08-27T14:44:56Z`. Graded **2026-08-27T16:43Z** by cfd lane R at **zero new
compute**.

**`launcher_rc=3` IS NOT A CRASH.** It is the launcher's own pre-spend cap guard
firing before the fine level: `HALT BEFORE SPENDING: level fine is PROJECTED to
cross the registered cap of 1450 core-min. The cap is NOT raised. Levels not
launched stay PENDING (CLAUDE.md rule 12).` Coarse and medium completed with rc 0.
Triage of the projector itself is the cfd supervisor's (check 3, done personally,
2026-08-27) and is summarised in §6 with attribution; it is **not** re-derived here.

Grader: `python3 /home/ubuntu/Certonomous/cases/F24_PRANDTL_MEYER/grade_f24.py --prereg-commit=260ff3c13e6877183a508c34ecd8e12886ed9a45`
— **rc 0**. Stdout `verification/runs/F24_PRANDTL_MEYER_runs/F24_GRADED.out`; record
`…/F24_GRADED.json`. Gated by `scripts/roache_triple.py::grade_ladder`; 0 `assert`
nodes across 4 files, planted assert seen. **Frozen files verified before the grader
ran: 16/16 blobs byte-identical to `git show 260ff3c1:<path>`** (15 case files plus
the pre-registration).

## 1. VERDICTS — fixed vocabulary, as the FROZEN grader returned them

| gate | verdict | the grader's own reason |
|---|---|---|
| G-F24-1 `p2_over_p1_box_mean` | **PENDING** | `level 'fine': no RC.txt yet: rc not recorded; PENDING, not a verdict` |
| G-F24-2 `p_line_L2_across_fan` | **PENDING** | same |
| R-F24-M2 `box_mean` | **REPORTED-NOT-GATED** (no verdict by registration) | same |

**PENDING, not NOT A RESULT — and the distinction is the point.** The dispatch
anticipated `NOT A RESULT` for want of a third level. The frozen grader returned
`PENDING`, and it is right: **the fine level was never launched**, so there is no
incomplete or non-converged level to gate. The grader's completion check refuses at
`fine` before rule 5 is reached at all; no triple was formed, no order computed, no
band consulted. `PENDING` is exactly rule 1's display/queue state for *not yet run*.
Had the fine level RUN and failed, or had a two-level triple been offered to
`grade_ladder`, `NOT A RESULT` would be the word. **This lane did not choose either
word — the frozen comparator printed them, and this record reports what it printed.**

**No gate values are quoted for coarse and medium, and that is deliberate.** The
frozen grader stops at the completion check and therefore computed no level values;
its CLI has no level-selection option (`--root`, `--out`, `--prereg-commit`,
`--selftest` only). Computing coarse and medium gate quantities by any other path
would be a comparator outside the frozen grading path fixed at the pre-registration
commit (rule 2), so **it was not done**. The two completed levels' physics is on
disk, unread by any gate, and stays that way until a third level exists.

## 2. RULE 4 — strict completion, read from the run root by this lane

| clause | coarse | medium | fine |
|---|---|---|---|
| `RC.txt` == 0 | 0 | 0 | **absent — never launched** |
| `End` line | 1 | 1 | no log |
| last `Time =` == endTime 4 | 4 | 4 | — |
| `Time` line count == steps | 15000 == 15000 | 30000 == 30000 | — |
| `ExecutionTime` count == `Time` count | 15000 | 30000 | — |
| `processor*` directories == registered 4 ranks | 4 | 4 | 0 |
| fields at endTime in `processor0/4/` | T, U, p, rho | T, U, p, rho | — |
| **age guard**: rank field newer than the serial `0/U` | 1787839625 > 1787839199 | 1787841896 > 1787839633 | — |

**Coarse and medium are COMPLETE under rule 4. The fine level holds only
`box_before.txt`** — no mesh, no decomposition, no solver log, 0 core-minutes. It is
**PENDING and unbought** (rule 12: levels not launched stay PENDING), never a
failure.

## 3. L-342 — the split did exactly what it exists to do

The grader printed four **BOOKKEEPING DEFECT** lines, all against the fine level —
no `ClockTime`, no `box_after.txt`, no `MESH_LINE.txt`, no `log.decomposePar` — then:

    COST CLAIM REFUSED (infrastructure fields missing); physics verdicts above are unaffected (L-342)

`cost_claim.core_min_claim` is **`null`** while `partial_sum_core_min` reads
**179.0**. That is the correct behaviour on a rung that has not finished: the
missing fields are INFRASTRUCTURE, so they refuse the **rung's cost claim** and
touch **no verdict**. This is a clean live exercise of L-342 in the refusing
direction on a real partial ladder, not a selftest.

## 4. PLANTED-ZERO CONTROLS

The grader's control block ran and is recorded in the JSON (`assert_census`: 4 files
checked, 0 `assert` nodes, planted assert seen). **The per-gate planted-zero reads
did NOT run on this invocation**, because the grader refuses at the completion check
before reaching the gate readers — there is no fine-level artifact to plant into.
**Stated rather than implied: this rung carries no live planted-zero evidence on its
gate quantities**, and it cannot until the fine level exists. Nothing in §1 depends
on a zero.

## 5. COST — rule 12, and the honest form for an unfinished rung

**Measured, from the two completed `log.rhoCentralFoam` ClockTimes × 4 ranks ÷ 60:**

| level | cells | steps | cell-steps | ClockTime (wall, 4 ranks) | core-min | µs/cell-step (core) | predicted core-min | ratio |
|---|---|---|---|---|---|---|---|---|
| coarse | 45,000 | 15,000 | 0.675 G | 425 s | 28.333 | **2.519** | 8.1 | **3.50** |
| medium | 180,000 | 30,000 | 5.40 G | 2,260 s | 150.667 | **1.674** | 81.0 | **1.86** |
| fine | 720,000 | 60,000 | 43.2 G | **never launched** | **0** | — | 648.0 | **PENDING** |
| **spent so far** | | | 6.075 G | 2,685 s | **179.000** | | 89.1 (the two levels) | **2.009** |

- **179.000 core-min of the registered CAP 1450 = 12.3 %.** The cap was never
  approached in spend and was never raised.
- **Dollars: $0.153 — DERIVED, NOT MEASURED**, at $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5). Registered whole-rung estimate $0.63 derived.
- **Actual/predicted on the levels that ran = 2.009** (179.000 / 89.1). Against the
  whole-rung 737.1 estimate the figure is 0.243, and that number means only that the
  rung is a third finished — it is **not** a favourable calibration reading and is
  recorded here so nobody reads it as one.
- **Attribution.** Misprediction, and it is **not** in the same direction at both
  levels: the registered basis was a flat 0.72 / 0.90 µs per cell-step carried
  forward from F15's `rhoCentralFoam` measurements. Measured **2.519 µs at coarse
  and 1.674 µs at medium** — the rate got **faster per cell-step as the problem
  grew**, because fixed per-run overheads (mesh, decomposition, MPI startup, I/O)
  amortise over 8× the cell-steps. The registered rate is therefore too optimistic
  at small sizes and converging toward right at large ones; a flat µs/cell-step is
  the wrong model shape for a 4-rank explicit solver, and that is the calibration
  lesson.
- **Contention: not separable and not claimed.** Both levels ran on a box the
  launcher's own probe read at `free cores 0.5` — saturated — but no per-level
  free-core reading sits beside either ClockTime, so no share is attributable.
- **Waste: NONE, named as zero rather than omitted (charter §6).** No level failed,
  nothing was repeated, and the 179.000 core-min bought two complete, rule-4-clean
  levels whose physics is intact on disk. **The rung produced no verdict, but the
  spend was not wasted — it was stopped.** That distinction is the whole difference
  between this row and F21's.

## 6. WHY THE RUN STOPPED — the cfd supervisor's finding, attributed, not re-derived

The supervisor's personal triage (check 3, 2026-08-27) reads the halt to
`run_f24.sh:200`, whose pre-spend projector multiplies a frozen per-level constant
by a contention factor `ranks / max(free_cores, 0.5)`. On a saturated box `free`
pins at the 0.5 floor and a 4-rank entry's multiplier pins at its maximum **8.0×**.
Applied at the fine level that gave a projection of **5,184 core-min**, cumulative
**5,363 of 1450** → halt. **The supervisor's own two completed levels bound the
real contention effect at 1.86× at `free = 0.5`, so the formula overstated it by
about 4.3×.**

**The narrow and honest statement, which is his and is repeated here because it
matters: the halt may well have been RIGHT.** From F24's own measured rates the
fine level lands at **1,205–1,440 core-min**, cumulative **1,384–1,619 against the
1,450 cap = 95.5 % to 111.7 %**. So the fine level genuinely sits on the cap's edge
and might cross it. What is wrong is not necessarily the decision but **the
reasoning**: the launcher reached it through a multiplier its own data refutes by
4.3×. **This record does not call the halt a false positive.**

**The structural point** — that whether a registered three-level ladder ever
produces its fine level depends on the instantaneous box load at the moment the
level starts, hours after launch, which makes the instrument non-reproducible and
converts a busy box into a refusing one — is the supervisor's, and the repair is
being written against `run_f24.sh`, `run_f25.sh` and `run_f23.sh` separately.
**F24's own projector is NOT amended: F24 has spent 179 core-min, its gates are
CLOSED under rule 2, and no addendum may alter its cap, thresholds, bands or
labels.** Whether F24 gets a successor that buys the fine level is the supervisor's
call, not this lane's.

## 7. WHAT IS PENDING, AND WHAT IS NOT REGISTERED

- **PENDING:** the fine level (720,000 cells, 60,000 steps, 4 ranks), and with it
  both gates and the reported quantity. Nothing about F24's physics has been
  refuted, tested or claimed.
- No amendment to F24's pre-registration; no cap raised; no gate, threshold, band or
  label touched. **Nothing was sent, filed, uploaded or submitted** (rule 7).
