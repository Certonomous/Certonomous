# Curriculum D6RF9 — A2-wing convergence probe `P_conv`, the OUTER-LOOP-CONVERGENCE successor to D6RF7 (NOT A RESULT / G-CONV GATE FAIL)

Supersedes: **D6RF7** — A2-wing convergence probe `P_conv`, overall **`NOT A RESULT`** with a substantive
**`G-CONV GATE FAIL`** inside. D6RF7 measured, on the D4 base mesh, that Fix #1 (`Gauss linear limited
corrected 0.333`) **+** Fix #2 (`nNonOrthogonalCorrectors 3`) do **NOT** bring `p`'s first uncorrected solve
under the `1.0e-05` accept floor: `p_first_uncorrected initRes 1.625570732e-05` = **1.626×** the floor
(graded leg L1); F5 at D6RF4's original scheme gave `1.658e-05` = 1.658×, AS PREDICTED. Verdict json:
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF7-a2-wing-convergence-probe/d6rf7_official_verdict.json`
(freeze `347976d2`); RESULTS at `curriculum_D6RF7/RESULTS.md`.

**D6RF8 was the RE-MESH draft and is NOT the successor.** D6RF8 (`curriculum_D6RF8/PREREGISTRATION.md`,
`PERMISSION = NOT_FROZEN`, never run) proposed a re-mesh below the non-orthogonality limit as the lever.
**Verification ruling V-128 (commit `a2978688`, binding) overruled that diagnosis:** the mesh is NOT the
lever — it is one warped face DAFoam passes `check OK`, not a systemic non-orthogonality defect — and
**the lever is OUTER-LOOP CONVERGENCE.** D6RF9 is that successor. It holds the mesh AND the D6RF7 LIMITED
`fvSchemes` **fixed** and moves only outer-loop numerics.

**PERMISSION = NOT_FROZEN.** This is a lane's prediction-first proposal. Nothing here is a registration until
the dafoam-supervisor freezes this file by sha (CLAUDE.md rule 2), after the supervisor's non-delegable
**check-1** (the grader DELTAS diff, §4) **and** the chief's cost sign-off (§5). The freeze, the per-rung pin
fixpoints and the enqueue belong to the supervisor and are **not** taken here. **Zero compute has run for this
item.** Because D6RF9 is a NEW item, its gates are OPEN pre-compute; before first compute this file is
amendable, and any amendment must state the condition and how it was checked. After first compute the gate,
threshold, cap and label are closed (rule 2).

**Single-point by design.** As D6RF3→D6RF7, this A2 **convergence probe** is single-arm `P_conv`: it exists
to measure whether the primal reaches its own accept floor, not to optimise. It buys no F_mp/REF_off arm; the
FD/CD/off-design/price gates of D6RF7 are dropped (they would read want-of-input). The multipoint SHIPPED row
is NAMED-UNBOUGHT and priced (§6), not bought here.

**DOWNSTREAM DEPENDENCY — this item unblocks the mandatory D6R2 transonic multipoint (added 2026-09-08,
pre-compute, NOT_FROZEN).** The mandatory **D6R2 transonic-multipoint chain is BLOCKED** on the A2 accept-floor
question (`docs/LAB_STATE.md:5857,5865,5894` — "D6R2 transonic-multipoint chain stays BLOCKED pending it";
S-130 records the shared re-diagnosis that the A2 primal's over-floor first-solve residual is what bounds the
multipoint gate). V-128 (commit `a2978688`, 2026-09-08) has now ruled: `p_first_uncorrected` STANDS as the
binding field, the `GATE FAIL` is UPHELD, the gate is NOT changed (T25) — so a numerics successor is owed, and
**D6RF9 is that successor.** D6R2 stays BLOCKED until D6RF9 either (a) drives `p_first_uncorrected` below
`1.0e-05` at some rung (`STOPPED_AT_FIRST_PASS`), unblocking the A2 primal the transonic multipoint sits on, or
(b) measure-exhausts to a CAPABILITY FINDING (§2 P5) that re-opens the escalated N-D43 acceptance-rule question
for Sanaa. Either way the D6R2 blocker is not lifted here and not by the lab (§7).

---

## 0. WHY A SUCCESSOR AT ALL — the measured plateau, and the ruling that redirects it

D6RF7's finding is not a null: it is a **measured** demonstration that scheme-side aids are insufficient. The
binding residual is `p`'s uncorrected first solve. The convergence research
(`docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md:45-66`) established it is a **monotone-asymptotic steady-state
plateau**, mechanistically the **magnitude of the explicit (lagged / deferred-correction) non-orthogonal
correction term** carried into each outer iteration's first pressure assembly — *not* a linear-solver failure
(the corrected p-solve reaches `finalRes 6.3e-11`) and *not* oscillatory.

**Two facts this lane MEASURED from the existing D6RF7 log** (`.../CURRICULUM-D6RF7-a2-wing-convergence-probe/
P_conv_20260907T170829Z_108678.log`, a non-solver read of an existing artefact, zero compute):

1. **The first-uncorrected p `initRes` is FLAT by outer-iteration ~300** and does not decay to `endTime 1000`.
   Sampled trajectory of the first p-solve per outer iteration (F5/original-scheme leg): iter 100 `2.17e-04`,
   200 `1.87e-05`, 300 `1.662e-05`, 400 `1.659e-05`, 500–1000 all `1.6583e-05` to four figures. The LIMITED
   leg is the same shape at `1.6256e-05`. **The outer loop has reached a fixed floor; more iterations at the
   D6RF7 config do not move it.**
2. **The run ended at `Time = 1000` = `endTime`, NOT at the accept floor.** Since `1.6256e-05 > 1.0e-05`, the
   primal never met its convergence criterion, so `endTime` is the binding outer-iteration cap and raising it
   genuinely extends the outer loop.

**What is un-tried, and is an OUTER-LOOP lever (not a mesh or scheme lever):** the deferred non-orthogonal
correction is iterated by `nNonOrthogonalCorrectors`, and **D6RF7 only ever ran 3 correctors** (D6RF4 ran 1).
On a 71° mesh, 3 corrector sweeps may not converge the *within-iteration* correction, so the *next* outer
iteration's first assembly still sees a stale lagged correction — which is exactly the plateau's mechanism.
**No run above 3 correctors exists.** Iterating the correction to convergence, changing the pressure-velocity
coupling (SIMPLE→SIMPLEC), the outer horizon and the under-relaxation are the outer-loop levers this item
measures, IN ORDER.

**Honest scope of the redirection.** V-128 rules the lever is outer-loop convergence and that ruling binds this
draft. This lane records the genuine scientific risk plainly (§2, §8): SIMPLE, SIMPLEC and relaxation all
converge to the *same* discrete fixed point, so if the first-uncorrected floor is the deferred-correction
residual *at that fixed point*, only the corrector-depth rung (R2) attacks it directly, and the ladder may
**measure-exhaust** to a capability finding. That is registered to be MEASURED, never inferred.

---

## 1. THE GATE — INHERITED VERBATIM FROM D6RF7 (T25)

**Gate id: `G-CONV`** — per field, per graded leg, the **final-iteration `initRes`** against the accept floor.

- **Threshold / accept floor = `CONV_BAR = 1.0e-05`** = `primalMinResTol 1e-08 × primalMinResTolDiff 1000`
  (**N-D43**: the floor is the **PRODUCT**, never the tolerance alone; **N-D43 CORRECTION 2026-09-06**: on the
  A2 wing multipoint case `primalMinResTolDiff` is `1000`, read from the run — never carried from memory).
- **Binding field = `p_first_uncorrected`** (the FIRST/uncorrected p-solve of the final outer iteration),
  which V-128/T25 rules is the binding outer-loop convergence monitor; the tighter `p_corrected`
  (within-iteration linear-solve residual) CANNOT establish steady state and is reported, never gated as the
  convergence measure.
- **Verdict rule: `PASS` iff `v < CONV_BAR` else `GATE FAIL`**, per field; a leg is `PASS` only if every field
  is; a non-finite or absent field makes the leg `NOT A RESULT` (strictly restrictive, rule 5).

**Provenance the successor inherits verbatim** — cited by path+line so check-1 can hash them:
- `curriculum_D6RF7/d6rf7_grade.py:367-368` — `CONV_FIELDS` (the p-solve split into `p_first_uncorrected` /
  `p_corrected`), reproduced identically in `d6rf9_grade.py`.
- `curriculum_D6RF7/d6rf7_grade.py:2020,2029` — the scoring `ratio = v / CONV_BAR` and
  `"PASS" if v < CONV_BAR else "GATE FAIL"`, reproduced identically in `d6rf9_grade.py:gate_conv`.
- `curriculum_D6RF7/d6rf7_grade.py:566-567` — `ACCEPT_FLOOR = afc.ACCEPT_FLOOR; CONV_BAR = ACCEPT_FLOOR`,
  reproduced identically.
- `curriculum_D6RF7/d6rf7_accept_floor_control.py:63-67` — `PRIMAL_MIN_RES_TOL 1e-08`,
  `PRIMAL_MIN_RES_TOL_DIFF 1000`, `ACCEPT_FLOOR = 1.0e-05`. **Carried byte-identically** as
  `d6rf9_accept_floor_control.py` (md5 `c6e63098e7afd542ea379a03eccfaf12`, verified equal on disk).

**T25 ASSERTION.** No gate, no threshold, no floor, and no field selection is moved. `CONV_BAR` stays
`1.0e-05`; `primalMinResTol` stays `1e-08`; `primalMinResTolDiff` stays `1000`; the binding field stays
`p_first_uncorrected`. The imported accept-floor control **refuses the grading (exit 2) in BOTH directions** —
a tightened floor refuses too — so this item cannot silently earn a PASS against a bar D6RF7 did not fail.

---

## 2. THE REGISTERED PREDICTION — HONEST, and TO-BE-MEASURED (`PENDING`)

Registered **before compute**; every clause is a prediction to be MEASURED, never inferred.

- **P1 (R1, extended horizon): predicted INSUFFICIENT.** The first-uncorrected residual is MEASURED flat by
  outer-iter ~300 (§0). R1 exists to convert that observation into a MEASURED exhaustion of the run-longer
  lever at this item's own freeze, and to serve as the ladder's baseline. Registered outcome: `PENDING` →
  expected `GATE FAIL` at ~`1.626×`.
- **P2 (R2, deep corrector loop 3→12): the load-bearing rung, outcome GENUINELY UNCERTAIN.** If the plateau is
  a *lagged* correction that a deeper corrector loop converges within each outer iteration, R2 lowers the
  first-uncorrected residual and may reach the floor. If the plateau is the deferred-correction residual *at
  the fixed point* itself, R2 does not help. **Neither is inferred here.** Registered outcome: `PENDING`.
- **P3 (R3, SIMPLEC): may accelerate/deepen convergence; CD/CL shift predicted ~0.** SIMPLEC converges to the
  *same* discrete fixed point as SIMPLE, so unlike D6RF7's limited scheme it is not expected to move CD/CL
  (reported, not gated). Whether it lowers the first-uncorrected floor is `PENDING`.
- **P4 (R4, heavy under-relaxation): fallback.** Lowers the plateau only if it is a weak limit cycle; the
  measured monotone-asymptotic shape argues against that, so R4 is predicted low-probability. `PENDING`.
- **P5 (ladder-level): the ladder MAY measure-exhaust.** If all four rungs are MEASURED and none drives
  `p_first_uncorrected < 1.0e-05`, the item records a **CAPABILITY FINDING** — *measured*, not inferred: at
  this mesh and this scheme the deferred non-orthogonal-correction residual floors above `1.0e-05` under all
  standard outer-loop levers. That **re-opens the escalated N-D43 acceptance-rule question for Sanaa** and is
  **not decided by the lab**. The `1.0e-05` floor is not widened under any outcome (T25).

---

## 3. THE LADDER — ordered outer-loop-convergence rungs (cheapest-and-most-likely first)

The chain runs rungs **in order** and **STOPS at the first rung whose graded leg drives
`p_first_uncorrected < 1.0e-05`** (`STOPPED_AT_FIRST_PASS`). Each rung changes **outer-loop numerics ONLY** —
never the mesh, the geometry, the objective/constraint, the `fvSchemes` discretisation (held at D6RF7's
`Gauss linear limited corrected 0.333`), or the accept floor. Every rung is run **beside the D6RF7 frozen
config as a known-fail control** (the F5-equivalent, D4): a PASS on the control withdraws the rung's verdict.

**Current (D6RF7) config, the baseline every rung is a delta from** — read from
`curriculum_D6RF7/d6rf7_fvSolution` and the runScript:
`solverName DARhoSimpleFoam`; `SIMPLE { nNonOrthogonalCorrectors 3; }`; `p`=GAMG/GaussSeidel relTol `0.001`
tol `1e-12` minIter `5`; `U|T|e|h|nuTilda|k|omega|epsilon`=smoothSolver/GaussSeidel relTol `0.001` tol `1e-09`
nSweeps `3`; relaxation `(p|p_rgh) 0.30`, `equations 0.70`; `endTime 1000`; `primalMinResTol 1e-8`,
`primalMinResTolDiff 1e3` (**FROZEN, untouched everywhere**).

| rung | lever | EXACT key changes vs D6RF7 config | why |
|---|---|---|---|
| **R1** | extended outer horizon | `controlDict endTime 1000 → 2500` (nothing else) | cheapest; the MEASURED control on the "run longer" lever; predicted insufficient (flat by iter ~300) |
| **R2** | deep corrector loop | `SIMPLE { nNonOrthogonalCorrectors 3 → 12; }`; `endTime 1000 → 2000` | iterate the LAGGED deferred-correction (the named binding mechanism) to within-iteration convergence — un-tried above 3 |
| **R3** | SIMPLEC coupling | `solverName DARhoSimpleFoam → DARhoSimpleCFoam`; `relaxation (p\|p_rgh) 0.30 → 0.70`; keep `nNonOrthogonalCorrectors 12`; `endTime 2000` | consistent SIMPLE removes the pressure under-relaxation limit; converges to the SAME fixed point (CD/CL shift ~0, reported not gated). DARhoSimpleCFoam is the compressible SIMPLEC solver already run on A3/A6 |
| **R4** | heavy under-relaxation | `relaxation (p\|p_rgh) 0.30 → 0.15`, `equations 0.70 → 0.50`; keep `DARhoSimpleCFoam` + `nNonOrthogonalCorrectors 12`; `endTime 2000 → 4000` | damp the outer loop onto a lower plateau if the floor is a weak limit cycle (predicted low-probability) |

Notes bounding scope:
- **R3 solver-switch is support/activity-gated, not assumed.** `DARhoSimpleCFoam` is confirmed present and run
  on this box (A3/A6; `docs/dafoam/PRIOR_WORK_INVENTORY.md`). But whether `consistent`/SIMPLEC is *active* for
  this solver on the A2 setup is read back from the run's own log by `G-CONFIG` (the `solverName` echo + the
  p-solve count), and a leg that did not run the registered coupling is `NOT A RESULT`, never a PASS. This
  mirrors D6RF7's G-SCHEME anti-cheat.
- **No rung touches `fvSchemes`.** The `Gauss linear limited corrected 0.333` scheme is held at D6RF7's
  `d6rf7_fvSchemes_LIMITED` (md5 `8374443e7a374e9d353cffccdb654aaf`), carried into D6RF9 byte-identical, so the
  lever under test is purely outer-loop.
- **No rung raises `primalMinResTol` or `primalMinResTolDiff`** — DAFoam's own FAQ remedy (widen the floor) is
  forbidden (N-D43; the bright line).

---

## 4. GRADING PATH — the frozen instrument, controls, and the check-1 DELTAS

- **Grader: `d6rf9_grade.py`** (beside this file). DERIVED FROM `curriculum_D6RF7/d6rf7_grade.py`
  (md5 `d6547afe3a5420fa2e7de6e1ee38605d`). It inherits G-CONV's scoring and the per-leg container-log reader
  VERBATIM and carries **four registered DELTAS**, enumerated for the supervisor's non-delegable **check-1** in
  **`d6rf9_grade.py_DELTAS_from_d6rf7.diff`** (beside this file):
  - **D1** the leg discriminator is `fvSolution`/`solverName`, not `fvSchemes` (the scheme is fixed here);
  - **D2** `G-CONFIG` replaces D6RF7's `G-SCHEME`: the graded leg must show the rung's registered
    `solverName`, `nNonOrthogonalCorrectors` (read from the run by counting per-corrector p-solves = count−1),
    relaxation and `endTime`, read back out of the container log, else `NOT A RESULT`;
  - **D3** the printed baseline is `CONV_MEASURED_D6RF7` (D6RF7's own measured initRes), each row printing its
    improvement vs it;
  - **D4** the F5-equivalent control leg is D6RF7's frozen config (measured `p_first_uncorrected 1.625570732e-05`
    → GATE FAIL); a rung PASS with the control also passing withdraws the rung's verdict.
- **Accept-floor instrument: `d6rf9_accept_floor_control.py`** — a **byte-identical copy** of
  `d6rf7_accept_floor_control.py` (md5 `c6e63098e7afd542ea379a03eccfaf12`, asserted equal in
  `freeze_check`). Imported, not re-implemented, so this file and the floor cannot disagree; it refuses (exit
  2) if either floor term has moved in EITHER direction in the arm's own log (T25 made executable).
- **Planted-zero control (CLAUDE.md rule 3):** `run_residual_plant_control` plants a known first-uncorrected
  `initRes` (`PLANT_INITRES = 1.234e-03`) into a COPY of a log, reads it back through the SAME `read_legs` the
  gate calls, refuses if the reader cannot see it, and asserts the original is byte-unchanged.
- **`freeze_check`** asserts (a) the accept-floor control is byte-identical to D6RF7's, and (b) — a PLACEHOLDER
  until the supervisor freezes — the grader's own bytes equal the committed blob at HEAD (rule 2).
- **Drivable NOW at zero compute:** `python d6rf9_grade.py --drive` runs the planted-zero control, the freeze
  check and a gate/G-CONFIG selftest. **This lane ran it: RESULT `ALL AS REGISTERED`** — floor inherited
  verbatim, `EXERCISED-PASS` (planted `1.234e-03` read back), `v < 1e-05` ⇒ PASS scoring correct, a
  wrong-corrector leg ⇒ `NOT A RESULT`.

---

## 5. COST — costed estimate / cap (CLAUDE.md rule 12)

**Measured envelope this is grounded in.** D6RF7 `P_conv`: 3 legs at `endTime 1000`, wall `204 s`, `ranks 4` ⇒
`core_min 13.6` (frozen verdict json `spend_core_min`). Per-leg-at-`endTime 1000` ≈ **`4.53 core-min`**
(`68 s × 4 / 60`). Cost scales ~linearly with `endTime` (outer iterations) and with per-outer-iteration solver
work; deeper corrector loops and SIMPLEC add a per-outer-iteration factor (folded conservatively below).

Each rung = 1 candidate leg (at the rung's `endTime`/config) + 1 D6RF7-control leg (`endTime 1000`, `4.53`).
`ranks = 4`. Dollars are **DERIVED** at **c7a.4xlarge $0.0513/core-h**, **reported-by-owner, NOT measured**
(`COMPUTE_BUDGET_CHARTER.md` §5; the box cannot read its own billing).

| rung | candidate leg factors (endTime× · corr× · coupling×) | candidate core-min | +control | rung est (core-min) | rung cap (3× form) |
|---|---|---|---|---|---|
| R1 | 2.5 · 1.0 · 1.0 | 11.3 | 4.5 | **15.9** | 48 |
| R2 | 2.0 · 1.8 · 1.0 | 16.3 | 4.5 | **20.8** | 63 |
| R3 | 2.0 · 1.8 · 1.1 | 17.9 | 4.5 | **22.5** | 68 |
| R4 | 4.0 · 1.8 · 1.1 | 32.6 | 4.5 | **37.1** | 112 |

- **Ladder total estimate (worst case, all four rungs run): `96.3 core-min`** ⇒ **`$0.082` DERIVED**.
- **Ladder cap (family-MAX form, sum of per-rung 3× caps): `291 core-min`** ⇒ **`$0.249` DERIVED**.
- **Expected spend is LESS than the total** — the chain STOPS at the first rung that reaches the floor
  (`STOPPED_AT_FIRST_PASS`); the total is the exhaustion bound.
- The per-rung `endTime`/config × ranks × deadline reachability identity (`cap_core_min × 60 / ranks == TMO +
  frame`) is fixed per rung at freeze, as in D6RF7 `cap_reachability`.
- Under the $25 pre-authorised ceiling for CPU runs (Sanaa 2026-08-21; a blanket is not a per-item read, so the
  costed figure still goes to the chief for sign-off per §PERMISSION). **Overrun stops the run; it does not get
  a new budget** (rule 12).

**Estimate-vs-actual calibration (rule 12):** at each rung's completion the pre-registered per-rung estimate
above is compared to the actual `core_min` from the log, the ratio and its attribution recorded as a row in
`docs/COST_CALIBRATION.md` under that file's append rules and the rule-10 private-index protocol.

---

## 6. TWO-ROW RULE (DAFOAM_CHARTER.md §6)

- Row **BOUGHT**: `PATCHED` (patched IDWarp image; the same digest D6RF7 bought).
- Row **NOT BOUGHT**: `SHIPPED`, **priced anyway at `155.70 core-min`** (a multipoint F_mp on stock IDWarp at
  the same cap; F_mp's own registered estimate, carried from D6RF7 §4a). An unbought row that is priced can be
  bought by a successor; an unbought row that is unpriced quietly becomes never.

---

## 7. WHAT THIS ITEM DOES NOT DECIDE

- It does **not** re-open the acceptance rule. Whether a successor may ever register a different acceptance
  rule is **escalated to Sanaa and unruled** (N-D43, N-D43 CORRECTION); D6RF9 either reaches the *unchanged*
  floor or records a MEASURED capability finding that puts the question back on Sanaa's desk.
- It does **not** freeze, launch or enqueue anything (STEP 4 / `PERMISSION = NOT_FROZEN`). SUBMISSIONS PARKED.

---

## 8. WHAT I COULD NOT VERIFY (honest gaps)

- **Whether any rung actually reaches the floor is UNMEASURED and is the whole point of running the item.** The
  registered prediction (§2) states the genuine risk that the first-uncorrected floor is the deferred-correction
  residual *at the fixed point*, which SIMPLE/SIMPLEC/relaxation share, so the ladder may measure-exhaust. Not
  inferred either way.
- **The R3 solver switch (`DARhoSimpleCFoam`) is present on the box (A3/A6) but its SIMPLEC activity on the A2
  `P_conv` setup is not confirmed at freeze;** G-CONFIG reads it back from the run and refuses (`NOT A RESULT`)
  if the registered coupling did not run. Confirming SIMPLEC *activity* for this solver (as was done for A1 via
  a third leg, PRIOR_WORK_INVENTORY) is a supervisor/liaison follow-up before R3, not established here.
- **The per-rung cost factors (corrector× 1.8, coupling× 1.1) are ENGINEERING ESTIMATES**, not measured; only
  the `4.53 core-min`/leg-at-`endTime 1000` base is measured (from D6RF7). The rule-12 calibration row at each
  rung's completion is where these are corrected.
- **`freeze_check`'s HEAD-blob pin is a placeholder** until the supervisor freezes; the byte-identity of the
  accept-floor control to D6RF7's IS verified now (md5 equal).
