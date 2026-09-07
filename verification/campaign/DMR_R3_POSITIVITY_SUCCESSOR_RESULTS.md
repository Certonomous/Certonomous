# DMR R3 positivity-limited successor — results: **the fix held at N=60/120 and did not survive to N=240**

Run 2026-09-07 against the frozen pre-registration
`verification/campaign/DMR_R3_POSITIVITY_SUCCESSOR_PREREGISTRATION.md` (freeze
commit `08efee1a`, AUTHORISED, cfd-supervisor check-4 PERSONAL+UNDELEGATED, PASS;
est 37 / hard cap 60 core-min). Levers over the parent (frozen, confirmed by the
supervisor's check-4 diff): `maxCo` 0.2->0.1 and reconstruct rho/U/T
vanLeer/vanLeerV -> Minmod/MinmodV, nothing else. Gate V' tol and all bands HELD
EXACTLY at the frozen parent's values, not widened. Driver
`run_dmr_positivity_successor.sh`; grading path the frozen method-agnostic locator
`dmr_locator_v2.py`, hashed at grade time by the driver. Run root **absent** when
the gate was frozen. Verdicts set by the cfd supervisor (§3 crash triage taken
personally); this record files them.

## Verdicts

| level / gate | verdict | why |
| --- | --- | --- |
| **R1p** (N=60), Gate V' | **`PASS`** | x_measured = 3.0113095706127635, error = 0.01081533267368373 < tol 0.0231; planted control PASSED (shift seen, absence refused). |
| **R2p** (N=120), Gate V' | **`PASS`** | x_measured = 2.999358056724758, error = 0.006080697150548708 < tol 0.0231; planted control PASSED (shift seen, absence refused). |
| **R3p** (N=240) | — | no value produced: `rhoCentralFoam` crashed rc = 136 (SIGFPE) mid-solve. |
| **The grid triple (as a whole)** | **`NOT A RESULT`** | the triple is INCOMPLETE — R3p produced no value, so per Roache rule 5 clause 1 (a level not iteratively converged / not producing a plateau value) the triple is `NOT A RESULT`, whatever R1p/R2p read. No GCI is computed or quotable. |

**The honest finding.** The positivity-limited numerics (Minmod reconstruction,
`maxCo` 0.1) held at the two coarser levels: both R1p and R2p PASS Gate V' and the
error DECREASES with refinement (0.01082 -> 0.006081), consistent with
convergence. The fix did **not** survive to N=240 — the finest level reproduced a
resolution-dependent numerical divergence and crashed. This is a real, disclosed
result about the successor numerics, not a process failure.

## R1p / R2p — the measured Gate V' values

| level | N | x_measured | x_exact_at_row | error | tol | PASS | planted control |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1p | 60 | 3.0113095706127635 | 3.0004942379390798 | 0.01081533267368373 | 0.0231 | true | PASSED (shift seen, absence refused) |
| R2p | 120 | 2.999358056724758 | 2.9932773595742095 | 0.006080697150548708 | 0.0231 | true | PASSED (shift seen, absence refused) |

Both readers ran the two-sided planted control **before** grading and reported
`PASSED (shift seen, absence refused)` — a reader shown able to see a non-zero
before its zero was trusted (CLAUDE.md rule 3). Source:
`verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R1p/locator_result.json` and
`.../R2p/locator_result.json`.

## R3p — the crash, and its triage (set by the supervisor)

`rhoCentralFoam` crashed with **rc = 136 = 128 + 8 (SIGFPE, signal 8)** after 275 s
wall on 4 ranks. The pre-solve steps all succeeded first: `blockMesh`,
`checkMesh`, `setExprFields`, `decomposePar` each rc = 0
(`verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/PROGRESS.txt`). The FPE is in
`Foam::sqrt(Field<double>&, ...)` **inside the solve** — a negative
sound-speed / temperature argument to `sqrt`, i.e. a locally negative temperature
at h = 1/240. This is a **genuine resolution-dependent numerical divergence of the
Minmod rhoCentralFoam run at the finest level**, not a setup or infrastructure
fault. `verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/successor.rc.txt` = 136.

**The two coarser rungs are untouched and unaffected.** R1p and R2p remain Gate V'
PASS on this record.

## Cost — measured

Total spent **1432 core-s = 23.867 core-min**, under the 60 core-min cap. From
`PROGRESS.txt` cumulative core-s: R1p 0.833 core-min completed, R2p 4.300 core-min
completed, R3p crashed partway at cumulative 1432 core-s (~18.33 core-min of a
partial, aborted solve). The underspend is **partly because R3p aborted mid-run**
(a crash, not a cheaper solve) — it did not spend its full finest-level budget.
Calibration row `docs/COST_CALIBRATION.md`.

## Verdict vocabulary

`PASS` (R1p, R2p Gate V'); **`NOT A RESULT`** (the triple as a whole, Roache rule 5
clause 1). No other label is used.
