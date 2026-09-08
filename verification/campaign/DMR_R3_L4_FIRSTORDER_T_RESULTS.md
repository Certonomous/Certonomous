# DMR R3 L4 — FIRST-ORDER-T RECONSTRUCTION SUCCESSOR — RUN RESULTS

> **This is a NEW results record. It does NOT edit the frozen pre-registration
> body** (`DMR_R3_L4_FIRSTORDER_T_PREREGISTRATION.md`, freeze `3c202ab1`
> "PRE-REGISTRATION FROZEN + AUTHORISED"; the generator/driver/prereg were first
> landed as the freeze-ready draft at `c4df6f38` — commit shas as relayed by the
> cfd supervisor and re-verified on disk by this lane). Frozen files are never
> edited (CLAUDE.md rule 6); the verdict below was graded by the frozen
> instrument and is transcribed here, not re-decided.
>
> Authored by cfd `lab-lane`, 2026-09-08, from the cfd supervisor's first-hand
> crash triage (personal §3 check-2) and the pinned-grader outputs. Every figure
> cites the run artifact it was read from; the lane re-verified each cited value
> at source and re-verified the grader identity before recording.

---

## VERDICT — **NOT A RESULT**

Roache rule 5, **clause 1**: the grid-convergence triple is **INCOMPLETE** (2 of
3 levels). The finest level **R3 (N=240) did not complete to `endTime = 0.2`** —
`rhoCentralFoam` aborted on a **SIGFPE (signal 8), rc=136**, at `Time =
0.15463531`. A triple that is not `CONVERGING` is `NOT A RESULT` whatever the two
completed levels' values are. **The gate turns nothing here**: a `NOT A RESULT`
stands on the incomplete triple regardless of the R1/R2 Gate V' PASS values, and
the gate can only turn a PASS/GATE FAIL *into* NOT A RESULT, never the reverse
(rule 5). There is no gradeable Gate T' and no quotable GCI.

This is a **MEASURED failure of the first-order-T lever**, not a capability
finding: the full measured lever chain is not exhausted (L5 bounded-T solver
build is unmeasured), so no capability-exhaustion inference is drawn from this
crash (L-501). Under fix-until-runs the ladder continues as a dated successor;
the next rung (L5 bounded-T clip, a solver-build boundary) is a DRAFT on Sanaa's
desk.

---

## LEVELS AS MEASURED

Family: `verification/runs/DMR_R3_L4_FIRSTORDER_T_runs/`. Single lever vs the
Tadmor successor, applied uniformly across all three levels: `reconstruct(T)
Minmod;` → `reconstruct(T) upwind;` (first-order, piecewise-constant T
reconstruction; §2 of the prereg, proven exactly one `system/fvSchemes` line).
`fluxScheme Tadmor` and `maxCo 0.1` retained. Grader `dmr_locator_v2.py`
(**blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`**, byte-identical to
`HEAD:verification/runs/DMR_runs/dmr_locator_v2.py`, re-verified by this lane;
`GATEV_TOL = 0.0231`), reused unchanged; two-sided planted-zero control run
before grading each completed level.

| level | N | grid | rc | Gate V' | x_measured | error | tol | PASS | planted control |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 60 | 240×60 | 0 | — | 3.009698606595904 | **0.009204368656824169** | 0.0231 | **PASS** | **PASSED** (shift seen, absence refused) |
| R2 | 120 | 480×120 | 0 | — | 2.998595327522941 | **0.005317967948731628** | 0.0231 | **PASS** | **PASSED** (shift seen, absence refused) |
| R3 | 240 | 960×240 | 136 | — (crashed) | — | — | 0.0231 | — | — |

- **R1 / R2** both `rc=0`, both Gate V' **PASS** inside the byte-identical parent
  tolerance 0.0231. The position error **DECREASES with refinement**
  (0.009204 → 0.005318) — the two completed levels are converging. Cited:
  `R1/locator_result.json`, `R2/locator_result.json` (`"PASS": true`,
  `"planted_control": "PASSED (shift seen, absence refused)"`,
  `"control": "two-sided, run before grading"`).
- **Planted-zero control (rule 3)** additionally re-confirmed live by this lane
  with the pinned grader's `--selfcheck`: on both existing reference rungs the
  planted integer-cell shift is SEEN exactly (`0.116666667`/`0.058333333`), the
  planted absence is REFUSED, and the regression reproduces the recorded Gate V
  positions to `|delta| = 0.000e+00` — `SELFCHECK: PASS — controls live and
  instrument unchanged`. The grader refuses to overwrite an existing result file,
  so the graded per-rung JSONs above are the frozen instrument's own output at
  the grade step, not a re-run.
- **R3** (`rhoCentralFoam`): **rc=136 SIGFPE (signal 8)**, deepest named stack
  frame `Foam::sqrt(Field<double>&, UList<double> const&)` in `libOpenFOAM.so`
  (caught mid-solve). Last written `Time = 0.15463531` against `endTime 0.2` — the
  solve did **not** reach t = 0.2. Cited: `R3/log.rhoCentralFoam` (last three
  `Time` lines + the signal-8 frame), `R3/RC_rhoCentralFoam.txt` = 136,
  `successor.rc.txt` = 136, `R3/system/controlDict` (`endTime 0.2`).

### The first-order-T finding — MEASURED partial delay, not a cure

R3 fails by the **same reflecting-wall-foot T-positivity mechanism** as the
dt/Courant lever: `Foam::sqrt` of a negative sound-speed/temperature argument at
the reflecting-wall foot, exactly where T first goes negative. Compared against
the L2 Courant probe (Tadmor + maxCo 0.05, N=240), which crashed at
`t = 0.15006001`, first-order T reconstruction **delayed the collapse by ~0.004
in simulation time** (0.15463531 vs 0.15006001) **but did not cure it.** More
diffusive T reconstruction is therefore a **measured PARTIAL mitigation** — it
pushes the collapse slightly later in time but the same positivity failure
recurs. This is the **measured exhaustion of the first-order-T reconstruction
lever** for carrying the DMR to t = 0.2 at N = 240, reported not softened.

---

## COST (rule 12) — MEASURED

- **L4 family total: 30.6 core-min** (1836 core-s cumulative from `PROGRESS.txt`)
  of the **100 core-min** single registered hard family cap — **NO cap breach;
  the run stopped on the R3 SIGFPE, not on the cap** (`CAP_BREACH.txt` absent).
  Per-level (advisory §6 watermarks, not caps): **R1 0.983 core-min**
  (`R1.coresec.txt` = 59), **R2 4.483 core-min** (`R2.coresec.txt` = 269), **R3
  ~25.1 core-min** of a PARTIAL, CRASHED solve (`R3/rhoCentralFoam wall=369s
  ranks=4 used=1836core-s` cumulative; the R3 `rhoCentralFoam` step alone is
  369 s × 4 = 24.6 core-min crash-truncated). R3 never spent its ~77 core-min
  advisory budget because it aborted at t ≈ 0.155 of an `endTime` 0.2.
- **§6 advisory grand estimate ≈ 90 core-min**; measured 30.6 core-min gives ratio
  **0.34** — but this is a **CRASH-TRUNCATED underspend**, NOT a favourable
  misprediction and NOT waste (`COMPUTE_BUDGET_CHARTER.md` §6). Had R3 run to
  endTime it would have spent far more; the finest level aborting mid-solve is
  the reason the family did not spend its budget, so the estimate is neither
  credited nor faulted by the raw ratio. The rule-12 calibration row is filed in
  `docs/COST_CALIBRATION.md`.

Dollars are **DERIVED, NOT MEASURED** — 30.6 core-min = 0.510 core-h at
$0.0513/core-h (c7a.4xlarge, reported-by-owner; the box cannot read its own
billing — `COMPUTE_BUDGET_CHARTER.md` §5) = **$0.0262 DERIVED**.

---

## WHAT THIS SETTLES, AND WHAT IT DOES NOT

- **Settled (measured):** first-order (piecewise-constant, `upwind`) T
  reconstruction, uniform at maxCo 0.1 with Tadmor flux, does NOT carry the DMR to
  t = 0.2 at N = 240 — it delays the reflecting-wall-foot T-positivity collapse by
  ~0.004 in sim-time but does not prevent it. The two coarser levels (N=60, N=120)
  both PASS Gate V' inside the byte-identical parent tolerance 0.0231 and their
  errors converge with refinement; that is not a triple, and does not lift the
  verdict.
- **NOT settled:** capability exhaustion — that requires the full measured lever
  chain including the L5 bounded-T (bounded-energy) solver build, which is
  unmeasured. No capability finding is drawn from this crash (L-501).

**Ladder continues** as a dated successor. The next rung — **L5 bounded-T clip**,
a solver-build boundary — is drafted (NOT frozen, NOT authorised) at
`verification/campaign/DMR_R3_L5_BOUNDED_T_PREREGISTRATION_DRAFT.md` and is on
Sanaa's desk (a solver patch + `wmake` build crosses the authorisation boundary).

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). This record
does not alter any gate, threshold, band, cap or label of the frozen
pre-registration. No tolerance was widened.**
