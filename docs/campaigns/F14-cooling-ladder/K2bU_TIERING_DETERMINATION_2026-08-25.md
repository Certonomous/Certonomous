# K2bU / K2bU3 — the verification team's open question, SETTLED FROM DISK

**Date:** 2026-08-25. **Author:** heat-transfer lane, for the heat-transfer
supervisor. **Zero compute.** No solver was launched, no case directory was
created, no frozen file was edited.

**The question, as the verification team's cross-team audit put it:**

> *"Two heat-transfer rows cannot be tiered from HEAD at all — K2bU and K2bU3.
> Prereg, case inputs and comparators are tracked; no results record, no sub-row,
> and their run output would be gitignored. NEVER RUN cannot be separated from
> completed-but-unfiled."*

---

## 1. THE ANSWER: NEITHER. Both are **COMPLETED AND FILED.**

**The premise "no results record" is false.** The records exist, are committed at
HEAD, and are complete — they are simply **not in a file named after the rung.**
Both diagnostic arms were written into the parent rung's results document:

| arm | results record | location |
|---|---|---|
| **K2bU** (2D unsteadiness discriminator) | `K2b_PILOT_RESULTS.md` **§14** (§14.1–§14.6) | `docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md:1395–1547` |
| **K2bU3** (3D survival check + gate) | `K2b_PILOT_RESULTS.md` **§15** (§15.1–§15.7) | same file, `:1548–1690` |

The audit searched for `K2bU_RESULTS.md` / `K2bU3_RESULTS.md`. Those files do not
exist and were never meant to. **This is a filing-name defect in the audit's
search, not an evidentiary gap in the family.**

## 2. The disk evidence that decides it

Run output is gitignored, so `git` cannot see it and `grep -r` on this box
(ugrep, honours ignore files) is blind to exactly these archives. Read with
`find` and `stat` against explicit paths under
`verification/runs/F14-cooling-ladder/K2b_runs/`:

| case | time dirs on disk | solver log | last write (UTC) | state |
|---|---|---|---|---|
| `K2bU_trans` | `5 10 15 20 25 30 35 40` | 4,278,817 B | 2026-08-18T05:52:18Z | **RAN, COMPLETE** |
| `K2bU3_M` (the gate control) | `20 40 60 80` | 1,024,825 B | 2026-08-18T06:05:27Z | **RAN, COMPLETE** |
| `K2bU3_L050` | `20 40 60 80` | 1,976,311 B | 2026-08-18T06:07:20Z | **RAN, COMPLETE** |
| `K2bU3_L025` | `20 40 60 80` | 3,991,033 B | 2026-08-18T06:12:23Z | **RAN, COMPLETE** |
| `K2bU3_D` (Test D, 3D) | **none** — only `0.orig/`, `constant/`, `system/` | none | inputs 2026-08-18T06:05Z | **NEVER RUN, BY REGISTERED DESIGN** — see §4 |

## 3. The strict completion rule, clause by clause, on the four that ran

CLAUDE.md rule 4, all six clauses, checked against the artifacts:

| clause | `K2bU_trans` | `K2bU3_M` | `K2bU3_L050` | `K2bU3_L025` |
|---|---|---|---|---|
| **1. rc = 0** | inferred from a clean `End` with no `FOAM FATAL`; **no exit-code file was written by this chain**, so this clause is **evidenced, not recorded** | same | same | same |
| **2. `End` line** | 1 | 1 | 1 | 1 |
| **3. last time == `endTime`** | 40 == 40.0 | 80 == 80.0 | 80 == 80.0 | 80 == 80.0 |
| **4. fields present at `endTime`** | `T U p_rgh alphat nut k omega` all present (+ `p`, `phi`) | all present | all present | all present |
| **5. `ExecutionTime` count == `endTime`** | **NOT APPLICABLE AS WRITTEN** — 1,978 | 459 | 927 | 1,918 |
| **6. age guard — every field at `endTime` newer than the case's own `0/T`** | **PASS**, `0/T` 05:24:20Z vs fields 05:52:18Z | **PASS**, 06:05:24Z vs 06:05:27Z | **PASS**, 06:07:05Z vs 06:07:20Z | **PASS**, 06:07:20Z vs 06:12:23Z |

**Clause 5 is stated honestly and not waved through.** The clause equates the
`ExecutionTime` count with `endTime` because the thermal family's steady `SIMPLE`
cases advance one time unit per iteration. **These four are transient
`buoyantBoussinesqPimpleFoam` runs on `adjustableRunTime` at `maxCo` 2.0**, where
the count is the number of *adaptive time steps*, not the physical end time. The
substantive form of the clause — one `ExecutionTime` per advanced step, no
truncated tail — **holds exactly on all four**: the `ExecutionTime` count equals
the `Time =` count in every case (1978/1978, 459/459, 927/927, 1918/1918). The
literal `== endTime` form is not satisfiable by a variable-`Δt` case and is
reported as **not applicable**, not as passed.

**Clause 1 is the one real gap.** No `rc` was persisted for these four runs. The
evidence for rc = 0 is a clean `End` line with the final `surfaceFieldValue`
writes intact and no fatal error in the log — strong, but it is an inference from
the log, **not a recorded exit code.** Any future re-grade of these arms should
treat clause 1 as evidenced-not-recorded.

## 4. `K2bU3_D` never ran, and its absence is a **pre-registered refusal**

`K2b_3D_UNSTEADINESS_PREREGISTRATION.md` §2 put a control in front of Test D and
fixed both branches before anything ran:

> *"Control M shows it damping → mesh and dimensionality are confounded at this
> price and Test D cannot answer the question. Outcome P3, declared without
> running Test D, with the cost of the un-confounded experiment stated."*

**The gate FAILED.** `K2bU3_M` (725 cells, 80 s, 459 steps): p2p 0.7792 K over
60–80 s against 1.6156 K over 40–60 s, **ratio 0.482** against the registered 0.5
damping threshold. Test D was therefore **not run and no 3D verdict was claimed**
— `K2b_PILOT_RESULTS.md` §15.1. **The absence of `K2bU3_D/0` is the pre-registered
outcome being honoured, not an unfinished run.** Firing Test D today would produce
a number the frozen pre-registration says cannot answer the question, and would be
a rule-2 violation.

## 5. What the two arms actually returned

- **K2bU → outcome O1, PHYSICALLY UNSTEADY.** `K2bU_trans`: 1,978 adaptive steps,
  mean Δt 20.2 ms, continuity ~1e-9. Both pre-registered window pairs graded:
  30–40 s vs 20–30 s gives 1.1088 K / 1.1293 K, **ratio 0.982**; 12.5–20 s vs
  5–12.5 s gives 1.1508 K / 1.2717 K, ratio 0.905. **PHYSICAL on both.** Dominant
  period 6.000 s by autocorrelation (+0.96 at one period).
- **K2bU3 → outcome P3, and the price of the un-confounded experiment MEASURED.**
  The 2D ladder: 100 mm DAMPS (0.482), 50 mm DAMPS (0.318), 25 mm DAMPS (0.377),
  12.5 mm SURVIVES (0.982). The limit cycle exists **only at 12.5 mm**. The
  un-confounded 3D experiment at 12.5 mm costs **22,064 core-min ≈ 368 core-h**,
  32–59× the graded pair it would be checking.

## 6. TWO CORRECTIONS THIS TURNS UP, both against records this family owns

**(a) `MATRIX_CONTRIBUTION.md` cell C18 is wrong in the same way the audit was.**
It reads: *"K2b 3D pre-registration exists and run directories exist; no results —
PENDING, which is a queue state, not a tier."* **The tier `NEVER RUN` is correct**
for C18 (3D mixed convection — no 3D solver ran). **The parenthetical is not.**
There are results: outcome P3 is filed at `K2b_PILOT_RESULTS.md` §15, and the
state is not `PENDING` — nothing is queued. **It is a pre-registered refusal with
a measured price.** Recommended restatement of the parenthetical, for the
supervisor to rule on: *"K2bU3 Test D was refused under its own frozen gate
(Control M DAMPS at ratio 0.482); outcome P3 is filed at `K2b_PILOT_RESULTS.md`
§15 with the un-confounded cost measured at 22,064 core-min. The cell is NEVER RUN
because the refusal was correct, not because the work is outstanding."*

**(b) The general defect: a diagnostic arm filed under its parent rung is
invisible to every rung-name search.** K2bU and K2bU3 are complete, artifacted and
graded, and were reported to a cross-team audit as untierable. **Recommended, and
escalated rather than taken:** a one-line pointer stub or an index row mapping
sub-arm ids to the section that carries them. This is a filing convention change
and is not a call this lane takes.

## 7. Verdict

**K2bU: COMPLETED AND FILED** (outcome O1). **K2bU3: COMPLETED AND FILED**
(outcome P3), with `K2bU3_D` correctly **NEVER RUN** under its own registered gate.
**Neither row is "completed-but-unfiled," and neither is "NEVER RUN" in the sense
the audit meant.** No verdict in either arm moves; nothing here creates, moves or
retires a gate, threshold, band, cap or label.

**Cost of this determination: zero core-minutes** (disk reads only). Nothing was
sent, filed or submitted anywhere.
