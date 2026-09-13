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

---

## ADDENDUM 1 — 2026-09-13 — RESULT. `GATE REACHED`: **H-AGGLOM**. Instrument control passed first.
## No gate, threshold, cap or label above is altered by this addendum.

Log `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/DIAG_AGGLOM1_20260913T200108Z.log`.

**Instrument control — checked before anything else, and it passed.** With `GAMGAgglomeration 1`
armed, instance 1 printed step 1 `p initRes 0.9999999999942178 finalRes 0.09743304254827717
nIters 24`, `CD 0.04113505209953232`, `CL 0.008857601366306839`, and step 100
`p initRes 0.002789709311072428` — every digit the registered control demanded. The debug switch
moved nothing.

**H-AGGLOM: CONFIRMED.** Both instances build an 11-level `faceAreaPair` hierarchy. **Level 0 —
the fine mesh — is identical in every printed column** (`20681 / 20887` cells, `2.882 / 2.896`
faces per cell, `9 / 14` interfaces, `0.1861 / 0.2507`, profile `8.579e+06`). That row is the
arm's own built-in control: the two instances hold the same mesh. **Every one of levels 1-10
differs**:

| level | inst 1 avg nCells | inst 2 | inst 1 avg nFaces/nCell | inst 2 | inst 1 profile | inst 2 |
|---|---|---|---|---|---|---|
| 0 | 20681 | 20681 | 2.882 | 2.882 | 8.579e+06 | 8.579e+06 |
| 1 | 10338 | 10336 | 3.021 | **3.193** | 4.076e+06 | 4.113e+06 |
| 2 | 5158 | 5159 | 3.528 | **3.747** | 1.474e+06 | 1.599e+06 |
| 3 | 2570 | 2563 | 4.163 | **4.364** | 5.633e+05 | 5.733e+05 |
| 4 | 1274 | 1276 | 4.784 | **4.953** | 1.891e+05 | 1.991e+05 |
| 5 | 633 | 630 | 5.217 | **5.371** | 6.102e+04 | 6.376e+04 |
| 6 | 312 | 312 | 5.443 | **5.505** | 1.903e+04 | 1.956e+04 |
| 7 | 154 | 153 | 5.402 | 5.400 | 5702 | 5659 |
| 8 | 75 | 75 | 5.080 | 5.002 | 1609 | 1554 |
| 9 | 37 | 36 | 4.495 | 4.339 | 436.4 | 415.8 |
| 10 | 17 | 17 | 3.570 | 3.437 | 111.8 | 103.8 |

Instance 2's coarse levels are systematically **denser** (higher faces-per-cell at every level 1-6,
larger bandwidth profile at levels 1-6). Its step-1 pressure solve then reads
`p initRes 0.9999999999942178 finalRes 0.09727830036032596 nIters 21` — the position-2 signature,
bit-identical to `P0`'s `cl05` and to `DIAG_ORDER1`'s `cl04`.

**So the thing that differs between instance 1 and instance 2 is the GAMG coarse-grid hierarchy,
and nothing else does.** The chain, every link measured: identical staged files (hashed, planted
control) -> identical resolved `DAOption` (byte-identical dumps) and unmutated Python dicts (md5
before/after, planted control) -> identical fine mesh (`checkMesh` block byte-identical; GAMG
level-0 row identical) -> identical momentum and energy solves (`U0 U1 U2 he` initRes AND finalRes
to 16 digits) -> identical pressure matrix and RHS (`p initRes` identical to 16 digits) ->
**DIFFERENT coarse hierarchy** -> different V-cycle count at the published `relTol 0.1`
(24 vs 21) -> a differently partially-converged `p` -> the whole SIMPLE trajectory diverges ->
pressure residual floor `1.757696578179007e-06` against `5.678212567273067e-08`, max residual
175.8x `primalMinResTol` against 11.95x -> `Primal solution failed!`.

**What is NOT demonstrated, and is labelled a HYPOTHESIS.** The *carrier* of the hierarchy
difference. `pairGAMGAgglomeration.H:63` declares `static bool forward_` — one value per PROCESS,
shared by every mesh — initialised `true` at `pairGAMGAgglomeration.C:36`, used to set the cell
loop direction at `pairGAMGAgglomerate.C:230,310`, used to reverse the coarse-cell map at
`pairGAMGAgglomerate.C:319-329`, and flipped at `pairGAMGAgglomerate.C:333` at the end of every
level. That is consistent with everything measured here — ordinality, a mirrored-and-denser second
hierarchy, an identical fine level — but **no experiment in this arm isolates it**, and a parity
argument from the printed level counts is not available because the number of `agglomerate()` calls
is not the number of accepted levels and is not printed. **Named, not adopted.**

The experiment that WOULD isolate it, offered and not run on this lane's own judgment: deny
instance 1 its agglomeration (a non-agglomerating `p` solver in `mp04` only, `mp05` and `mp06`
untouched) and predict that `mp05`, now the FIRST agglomeration in the process, prints instance 1's
table and reproduces the control bit-for-bit. Risk to disclose before it is registered: an
unsuitable preconditioner/solver pairing for this `p` matrix can abort instance 1 and waste the arm.
