# D6R3 — DIAGNOSTIC PRE-REGISTRATION: ARM `DIAG_AGGLOM1` (what actually differs)

DRAFT. Nothing sent, filed, uploaded or registered outside this box (rule 7). Committed **before**
any compute for this arm (rule 2).

- Run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/DIAG_AGGLOM1`
- Producer: the **FROZEN** `d6r3_opt_runScript.py`, md5 `efc3e62699690edd32e4ee910aad09c8`,
  unedited, in the published point order (`cl04`, `cl05`, `cl06`). Task `run_model`, 28 ranks.
- `primalMinResTol` 1e-8 UNCHANGED. `primalMinResTolDiff` ABSENT, UNCHANGED. `endTime` 2000
  UNCHANGED. `fvSolution` UNCHANGED. Mesh UNCHANGED. No convergence criterion is loosened.
- The **only** change from arm `P0` is one line of staging: `GAMGAgglomeration 1;` is added to the
  `DebugSwitches` block each condition's `controlDict` already carries.

## 1. What arm `DIAG_ORDER1` established (measured, not assumed)

Running the identical job with `cl05` FIRST moved the whole signature with the POSITION, not the
point, to the last printed digit:

| position | point | step-1 `p` finalRes / nIters | converged CD / CL |
|---|---|---|---|
| 1st (arm `P0`) | cl04 | `0.09743304254827717` / 24 | `0.02090109066417552` / `0.5000136952243076` |
| 1st (arm `DIAG_ORDER1`) | **cl05** | `0.09743304254827717` / 24 | `0.02090109066417552` / `0.5000136952243076` |
| 2nd (arm `P0`) | cl05 | `0.09727830036032596` / 21 | fails, plateau 1.76e-06 |
| 2nd (arm `DIAG_ORDER1`) | **cl04** | `0.09727830036032596` / 21 | (running) |

`P00`, the published tutorial in its own process, is the 1st-position row exactly. So: the defect
is **ordinal** — the second primal in a process differs — and every point-specific,
input-specific and file-specific explanation is excluded.

The `D6R3_DIAG_OPTSIG` probe also killed the handed `daOptions` lead with a live planted control:
`daOptions` md5 `f129ca31c6f85a782192ec0a8d505a46` **before and after** every builder's
`initialize()`, all three builders, one shared object id; each `meshOptions` md5 unchanged
before/after; `plant_visible: true` on every line, so the reader was shown able to report a
difference before its silence was believed.

## 2. The candidate mechanism, from source, NOT yet demonstrated

`OpenFOAM-v2506/src/OpenFOAM/matrices/lduMatrix/solvers/GAMG/GAMGAgglomerations/pairGAMGAgglomeration/`

- `pairGAMGAgglomeration.H:63` — `static bool forward_;`  *"Direction of cell loop for the current level"*
- `pairGAMGAgglomeration.C:36` — `bool pairGAMGAgglomeration::forward_(true);` — one value per PROCESS
- `pairGAMGAgglomerate.C:230,310` — `celli = forward_ ? cellfi : nFineCells - cellfi - 1;`
- `pairGAMGAgglomerate.C:319-329` — the coarse-cell map is reversed when `!forward_`
- `pairGAMGAgglomerate.C:333` — `forward_ = !forward_;` at the end of **every level**

`fvSolution` selects `GAMG` for `p` with no `agglomerator`, so the default `faceAreaPair` runs,
which is a `pairGAMGAgglomeration`. The agglomeration is built lazily at a mesh's FIRST pressure
solve and cached. A second mesh in the same process therefore begins its hierarchy at whatever
parity the first mesh's hierarchy left behind. **Hypothesis, not a finding until this arm measures it.**

## 3. PREDICTIONS — frozen before the run

- **INSTRUMENT CONTROL (checked first, and it can void the arm).** Instance 1 must still print step 1
  `p initRes 0.9999999999942178 finalRes 0.09743304254827717 nIters 24`, `CD 0.04113505209953232`,
  `CL 0.008857601366306839`. If the debug switch has moved any of those digits it changed the
  physics, and this arm is **NOT A RESULT** whatever else it prints.
- **H-AGGLOM (the claim under test).** The `printLevels()` table that `GAMGAgglomeration::New`
  emits for instance 2 **differs** from instance 1's — in level count, in per-level cell counts,
  in interface counts or in the bandwidth profile — on two meshes this lane has already hashed
  byte-identical. Reading: what differs between the two instances is the **coarse-grid hierarchy**,
  and nothing else does.
- **H-AGGLOM-DEAD.** The two tables are identical. Reading: the hierarchy is NOT what differs, the
  `forward_` static is exonerated as the carrier, and this lane says so and reports the mechanism
  as **undemonstrated** with `forward_` still only a source-level hypothesis.
- No verdict about D6R3 physics is produced by this arm. Outcome vocabulary: `GATE REACHED`
  (H-AGGLOM or H-AGGLOM-DEAD decided) or `NOT A RESULT` (instrument control fails, or run does
  not complete).

## 4. Cost

28 ranks. Expected wall 640 s (setup ~120 s + 2 x ~260 s) to abort after the second primal;
**predicted 299 core-min**, upper bound 420 core-min. Derived dollars at the owner-stated
c7a.4xlarge $0.0513/core-h: **$0.26, derived, not measured**. Directive #17: no run is stopped by
a cap; a crossing is REPORTED and the arm graded `NOT A RESULT`. Cores `min(free, 96-48-20) = 28`,
per-core idle measured over a 5 s window at launch, launcher REFUSES below 28.
Estimate-vs-actual owed to `docs/COST_CALIBRATION.md` at completion (rule 12).
