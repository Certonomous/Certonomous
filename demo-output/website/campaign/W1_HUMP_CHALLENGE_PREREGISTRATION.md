# W1 hump at challenge conditions + QCR2000 arm — pre-registration

Written 2026-08-07, before any solve of this item. Items:
`w1-hump-challenge-conditions` (approved 2026-07-31; **repriced this date
from 60 to 6 core-min** by dated correction on the docket entry — measured
basis, F6a's own 5.25 core-min ladder on the identical case) and
`f6a-hump-qcr-arm-on-the-challenge-run` (the supervisor's negative-verdict
review §2 diagnostic, 8 core-min marginal, wording binding). Precedent
followed: F6b (`31b0be16`) — verification gate and physics gate separate,
committed before the first iteration.

## 1. The case, and what "challenge conditions" means exactly

The closure challenge's scored hump case is the benchmark's shipped
`NASA_2DWMH` OpenFOAM case: Glauert-Goldschmied hump, chord c = 0.42 m,
**Re_c = 936,000, M = 0.1** (U_inf = 34.625 m/s from the shipped `caseDef`),
51,626-cell shipped mesh, shipped inlet/outlet profiles
(`0/inletOutletFields`), `simpleFoam`, SIMPLEC, shipped `residualControl`
(U/p/k 5e-7, omega 1e-10). These are verified identical to NASA TMR's stated
case conditions (F6a record, `dafoam/f6a_nasa_hump/F6a_nasa_hump.md`,
deviations 1–4 inherited verbatim, including the stock-`kOmegaSST`
substitution proven inert to 0.02% against the shipped baseline field).

The F6a gate (2026-07-28) was already run on this case, so the honest
content of the approved run is: (a) a **fresh, pre-registered two-gate pass
in the F6b canon** on the challenge case — F6a's gate predates the
verification/physics gate separation — and (b) the **QCR2000 arm**, the
constitutive probe the review ordered so the hump/hills two-leg
separated-flow pattern is probed identically on both legs.

Two legs, one variable between them:

| leg | RASModel | everything else |
| --- | --- | --- |
| SST | `kOmegaSST` (stock v2606) | shipped case as F6a ran it |
| SST+QCR | `kOmegaSSTQCR` (the lab-built QCR2000 term, `libkOmegaSSTQCRTurbulenceModels.so` — the identical library and model name that produced the round-5 duct result) | identical |

Native openfoam2606, `mpirun -np 4` (shipped `decomposeParDict`, the family
convention). Run directories:
`/home/ubuntu/certonomous-runs/w1-hump-challenge/{sst,sst_qcr}`.

## 2. Gate V — verification (decided on the SST leg alone)

Our pipeline must reproduce the known answer on this mesh before any physics
sentence is written. Reference: F6a's converged, three-way cross-checked
values on this identical case (sep x/c 0.6544, reatt x/c 1.2534 at 1772
iterations), themselves within 0.06% / published-range of NASA's own SST
(CFL3D/FUN3D: 0.654, 1.25–1.27).

- **PASS** if the fresh SST leg converges on the shipped `residualControl`
  and lands separation x/c in **0.6544 ± 0.005** and reattachment x/c in
  **1.2534 ± 0.005** (Cf sign crossings via `hump_gate_analysis.py`,
  unmodified).
- **FAIL** otherwise. A Gate-V FAIL voids Gate P and the QCR comparison on
  this run (a physics claim without a verified pipeline is an argument, not
  a result) and escalates per guidelines §5.

## 3. Gate P — physics (each leg separately, only if Gate V passes)

Reference: the CFDVAL2004 experiment (Greenblatt et al., AIAA-2004-2220 /
AIAA J 44(12), 2006), as carried by NASA TMR's hump validation page and the
on-disk fetched data (`nasa_experimental_reference/{noflow_cf,noflow_cp}.exp.dat`)
— the reference conventions the evaluation protocol's census records for the
hump class (`CLOSURE_EVALUATION_PROTOCOL.md` §2.3, classes 2–3: Cf along the
wall with separation/reattachment as its sign crossings; Cp as the shape
check; station list x/c = −2.14, 0.65, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3).

- Metric: separation and reattachment x/c from Cf sign crossings
  (`Cf = -wallShearStress_x / (0.5 U_inf^2)`, the F6a sign convention).
- Experimental values: **separation x/c = 0.665, reattachment x/c = 1.100**
  (NASA TMR, fetched live 2026-07-28, on disk).
- Tolerance, declared now: **±5%** of each experimental x/c value —
  separation PASS iff |dev| ≤ 5% (x/c 0.632–0.698), reattachment PASS iff
  |dev| ≤ 5% (x/c 1.045–1.155).
- Secondary (reported, not gated): Cp scaled MAE vs `noflow_cp.exp.dat`
  under F6a's documented p_ref convention (deviation 3 caveat carries).

## 4. QCR arm gate (the review's §2 wording, made numeric before the solve)

The QCR2000 term is the single change. Outcomes, defined now:

- **Outcome one (constitutive)**: reattachment moves **toward** 1.100 by
  more than **0.010 x/c** relative to the SST leg (i.e., reatt_QCR ≤
  reatt_SST − 0.010). The finding is then compared leg-against-leg with the
  hills QCR arm (`f6b-qcr2000-on-the-hills`, approved 12 core-min — **not
  yet run as of this writing**; if still unrun when this closes, the
  comparison row states "hills arm pending" rather than inventing it, and
  the ducts' round-5 QCR result stands in as the anisotropy-mechanism
  contrast).
- **Outcome two (omega budget)**: any smaller or wrong-direction movement.
  The constitutive route is then ruled out on this leg too, implicating the
  turbulent-shear-stress magnitude (omega budget), matching the review's
  own dichotomy.

## 5. Predictions (numeric, scored clause-by-clause afterwards)

1. Gate V passes: the fresh SST leg reproduces F6a within ±0.005 x/c on
   both crossings.
2. SST leg Gate P: separation **PASSES** (predicted dev −1% to −2%);
   reattachment **FAILS** at **+12% to +16%** — the documented
   linear-eddy-viscosity bubble-length bias, the same family as the hills'
   +72%.
3. QCR arm lands **outcome two**: |reatt_QCR − reatt_SST| < 0.03 x/c, and
   specifically less than the 0.010 materiality bar, because the hump/hills
   failure is a separated-shear-layer stress-magnitude deficit, while the
   ducts' QCR win was normal-stress-anisotropy-driven secondary flow — a
   different mechanism. (If this is falsified — QCR materially shortens the
   bubble — that is the more interesting result and clause 3 stays in the
   record as written.)
4. Cost: SST leg ≤ 6 core-min, QCR leg ≤ 8 core-min (QCR priced with margin
   for slower convergence of the nonlinear constitutive term), both gross,
   wall × 4 ranks, direct measurement.

## 6. Budget, caps, disqualifiers

- Budget: **14 core-min total** (6 repriced + 8 QCR arm), 4 ranks each leg.
- Iteration cap: `endTime 5000` (F6a converged at 1772; the cap is sized for
  the `residualControl` criterion per guidelines 3.4, not a settle-watcher
  number). A leg that hits 5000 without meeting `residualControl` is
  reported **unconverged, not gateable** (L-24/3.2); its numbers are
  labelled and no gate verdict is issued for that leg.
- Solver crash: recorded per the guidelines §4 triage table, leg excluded,
  gate not softened.
- No scoring call, no challenge-scorer submission from this item (that
  authority is the chief's; the gates above need no scorer).

---
*Nothing below this line existed when the runs were launched.*
