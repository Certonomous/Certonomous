# T3 — fourth mesh level `R_ff`: pre-registration (FROZEN, BUILT, NOT FIRED)

**Document v1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS ITERATED ON `R_ff`.**
Campaign T, rung **T3** (heated backward-facing step at Vogel & Eaton 1985
conditions). This document registers the **fourth mesh level** that
`T3_RESULTS.md` §14.8 proposed and did not run, and `T3_EXT1_AMENDMENT.md` §6 P3
anticipated. Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE
REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.** Nothing here
authorises a launch: **the fire order is the heat-transfer supervisor's**, after
the personal checks of `SUPERVISION_CHARTER.md` §3.

**Condition (`CLAUDE.md` rule 2), and how it was checked.** At the moment this
file is committed, `verification/runs/T-family/T3_runs/R_ff/` holds
`0.orig/ constant/ system/ CASE.txt log.blockMesh log.checkMesh` and **no `0/`,
no numeric time directory, no `processor*`, no `log.solve`, and no
`STATUS.R_ff`** (checked with `ls R_ff` immediately before the commit; the
launcher refuses on any of them). Zero core-minutes have been spent on `R_ff`
beyond `blockMesh`/`checkMesh` (the birth certificate, §4) and the one-timestep
launch check of §9, which ran **in scratch outside the run tree** and whose
fields were discarded.

---

## 0. Why a fourth level, in one paragraph

After ext1 (`T3_RESULTS.md` §14) the medium and fine levels are iteratively
CONVERGED, the coarse level `R_c` is in a limit cycle at the 80 000 cap and will
not converge, and the graded triple `(R_c, R_m, R_f)` therefore fires gate (1)
on every row. Of the triples themselves, G2 `x_peak/H` is CONVERGING with an
observed order `p = 4.30` that exceeds the scheme's formal order — read there
as *levels too close to resolve an order* — and G3/G4 are STAGNANT at
`p ≈ 0.22`. The registered response (§14.8) is a triple built from three
**converged** levels, **`(R_m, R_f, R_ff)`**, not a re-run of `R_c`. This
document is that response, costed and frozen.

## 1. What `R_ff` is — geometry and mesh family, identical by construction

- **Geometry, schemes, boundary conditions, turbulence, transport, gravity:
  byte-identical to `R_f`.** Measured with `diff` against
  `T3_runs/R_f/` before the freeze: `system/fvSchemes`, `system/fvSolution`,
  `constant/transportProperties`, `constant/turbulenceProperties`,
  `constant/g`, `0.orig/{U,p_rgh,T,alphat,k,omega,nut}` — **IDENTICAL, all
  twelve files.** `system/controlDict` differs in **exactly one line**:
  ```
  14c14
  <     endTime         78000;      (R_f, post-ext1)
  >     endTime         118000;     (R_ff, §3)
  ```
  `system/blockMeshDict` differs only in the three block count triples and the
  grading numbers those counts imply (§1.1). One file is **new**:
  `system/decomposeParDict` (`simple`, `n (8 1 1)`), because the family ran
  serial and had none (§5).
- **Built through the frozen builder, not beside it.** `build_t3_rff.py`
  (sha256 `a9c5bba6c7e88905`, 83 lines) imports `build_t3.py` (HEAD blob
  `340a5079`) and calls its `design()`/`build()` with a level `ff` injected
  into `LEVELS` at runtime; `build_t3.py` is not edited. The grading ratios are
  found by the same `cell_ratio()` bisection as `R_c/R_m/R_f`.

### 1.1 The refinement, stated as numbers

The mesh is **2D** (one empty cell in `z`), so the family's ratio applies in
two directions and the cell count scales as **`r²`**, not `r³`.

| | `R_m` | `R_f` | **`R_ff`** |
|---|---:|---:|---:|
| `nx_up` × `ny_up` (B1) | 160 × 128 | 256 × 204 | **410 × 326** |
| `nx_down` × `ny_low` (B2) | 320 × 96 | 512 × 154 | **819 × 246** |
| `nx_down` × `ny_up` (B3) | 320 × 128 | 512 × 204 | **819 × 326** |
| wall `y+` target | 1.0 | 0.625 | **0.390625** (= 0.625 / 1.6) |
| first wall cell (m) | 7.0083e-05 | 4.3802e-05 | **2.737608e-05** |
| `nCells` **read from `log.checkMesh`** | 92 160 | 235 520 | **602 128** |

**Derivation of the count:** `R_f`'s `nCells` read from disk, 235 520, × `r²`
with `r = 1.6` = 602 931; the integer counts (each `R_f` count × 1.6, rounded,
`ny` kept even for the two-sided grading) give **602 128**, i.e. `R_f × 2.5566`,
**effective `r_32 = √2.5566 = 1.5989`**, against the family's existing
`r21 = 1.5986`, `r32 = 1.6000` (`gate_t3.json`). The comparator of record
computes effective ratios from `polyMesh/owner`, never from this table.

## 2. Solver and numerics — inherited, none changed

`buoyantBoussinesqSimpleFoam`, `g = (0 0 0)`, `beta = 0`, `kOmegaSST`
wall-resolved with the low-Re wall functions, `Pr_t = 0.85`, the bounded
second-order scheme set of `T3_PREREGISTRATION.md` §3, `deltaT 1`,
`writeInterval 2000`, `purgeWrite 2`, **no `residualControl`** (L-141).

## 3. `endTime`, the iteration cap and the completion rule

- **`endTime = 118 000`** = `R_f`'s converged requirement **78 000 × 1.5 =
  117 000, rounded UP to the next multiple of the 2 000 `writeInterval`.** The
  factor 1.5 is the stated allowance for the finer mesh's slower `T` decay
  (`R_f` decayed at 0.0527 decades per 1 000 iterations against `R_m`'s
  0.1775, `T3_EXT1_AMENDMENT.md` §3; a further ×1.6 refinement is not expected
  to be faster). §14.8 named "iterations at least 78 000" as the assumption
  most likely to be optimistic; this factor is the registered response.
- **Iteration cap (inherited in form from ext1's 80 000): 160 000 total.** If
  `R_ff` is NOT CONVERGED at 118 000 it may be extended **once**, from
  `latestTime`, under the ext1 decision rule (`T3_EXT1_AMENDMENT.md` §3, fitted
  on the last 5 000 iterations) to an `endTime` ≤ 160 000, with a dated
  amendment stating the fit and the new `endTime` **before** the extension
  starts. A case STALLED at the cap is reported as such; no average is taken.
- **Convergence criterion, unchanged:** largest change of any cell value of
  `T`, and separately `U`, between the checkpoints at `endTime − 2000` and
  `endTime` ≤ `1e-6` of that field's range (`T3_PREREGISTRATION.md` §5).
- **Completion rule (rule 4), strict and all-or-nothing:** `rc = 0` in
  `STATUS.R_ff`; an `End` line in `log.solve`; last time == `endTime`; fields
  `T U p_rgh alphat phi nut k omega` present at that time (**reconstructed** —
  the launcher runs `reconstructPar -newTimes` and records its rc; a failed
  reconstruction is NOT DONE); `^ExecutionTime` count == `endTime` (one per
  iteration, written by the master rank); **every field at `endTime` newer than
  the case's own `0/T`** (touched last at launch). If extended, the
  **two-segment rule** of `mark_done_t3_ext1.py` §8 applies verbatim (both
  `rc = 0`, both `End`s, summed `ExecutionTime` == `endTime`, first ext `Time`
  == segment-1 count + 1, second age datum `STATUS.R_ff`).
  `mark_done_t3.check(root, "R_ff")` is case-agnostic and is the function of
  record; its `main()` iterates the frozen eight-case list, so the marker for
  `R_ff` is written by the owed reader of §8, never by hand.

## 4. Birth certificate — issued before the freeze

`python3 check_t3_mesh.py R_ff` (frozen, HEAD blob `0e4afc3c`) ran `blockMesh`
and `checkMesh` and checked contract items A–G from `constant/polyMesh/points`:
**MESH CHECK PASSED** — heated-wall cell `2.737608e-05` m = design, the
smallest in its block; step `x` cell `1.1400e-03` m on both sides; halves
geometric; blocks conformal; counts match `CASE.txt`. `checkMesh`
(`R_ff/log.checkMesh`, sha256 `dc140caaf2a0dd6f`): **cells 602 128, Mesh OK,
max aspect ratio 414.8** (expected on a wall-resolved mesh; `R_f` reports the
same class of number), non-orthogonality 0, max skewness 3.2e-11.
`scripts/check_case_provenance.py --case R_ff`: **clean** (no
compressible-family tokens). `polyMesh` is **not committed** (the family's
convention); it is regenerated by `blockMesh` from the committed dictionary and
the certificate is the log.

## 5. Ranks — 8, and the confound that choice injects, disclosed

- **T3 ran serial throughout** (`T3_PREREGISTRATION.md` §3 "all serial";
  `nProcs = 1` on all eight cases in both segments). **F15's decomposition
  ruling applies** (`docs/LAB_STATE.md`, "RULING 2": *a grid-convergence ladder
  must differ ONLY IN MESH; different rank counts mean different floating-point
  summation orders — a non-mesh difference injected into exactly the
  level-to-level differences the observed-order fit consumes*).
- **Serial does not fit.** POINT wall serial = 1.093e6 s = **12.65 days**
  (§6), about 6.7× the 45 h `R_f` critical path — far outside the 24 h the
  brief allows serial. So `R_ff` runs **decomposed**, and the triple
  `(R_m, R_f, R_ff)` carries **one non-mesh difference: summation order.** Its
  magnitude is expected at the 1e-12 to 1e-10 relative level (N-D
  decomposition-invariance measurements in `NUMERICS_KNOWLEDGE.md`, e.g.
  `~1e-04` invariance quoted at :2885 is for a gradient statistic; the graded
  quantities here are wall-integral and station values). **It is disclosed as
  a caveat on every row of the new triple, and the record must quote it. It is
  not a reason to skip the level: a serial 12.65-day critical path on a shared
  16-core box is the larger risk to the result.**
- **8 ranks, not 4:** 602 128 / 8 = **75 266 cells per rank**, above the ~50 k
  per rank below which 2D `simple` decompositions on this box lose efficiency;
  4 ranks (150 532 per rank) would take 3.5 days of wall at 0.9 efficiency
  against ≈ 1.9 days at 8 (§6). No prior T-family decomposition exists to
  copy; the F15 registration's fine level (160 000 cells at 8 ranks = 20 000
  per rank) is the nearest lab precedent and is coarser per rank than this.
  **`simple n (8 1 1)`** — slabs in `x`, deterministic, no seed, bit-reproducible
  from the rank count (F15's form). The launcher **refuses any other rank
  count** (§7).
- **Memory estimate:** the same solver on a 50 176-cell 2D `kOmegaSST` case
  measured **128 MB RSS** live on this box (K0f `B_hi`/`I_hi`/`M1_m_seed`,
  `VmHWM` 134–135 MB, read from `/proc` on 2026-08-26) ≈ 2.6 kB/cell including
  fixed cost → **≈ 1.5 GB serial-equivalent, ≈ 2 GB across 8 ranks** with halo
  overhead. **`memory_floor_gb = 3`** for the queue entry. Box: 30 GB total,
  21 GB available at registration. Estimate, not measurement — the first
  measured `VmHWM` of the run is to be recorded in the results.

## 6. Cost — rule 12, from the measured rate

Rate: **6.50e4 cell-iterations per core-second**, the §14.8 figure derived
from the measured degradation `R_m` 1.12e5 → `R_f` 8.53e4 (0.762× per 2.56×
cells), applied once more. No fixed-cost term is added: at this length the
§14.7 startup/IO term (≈ 1 400–1 900 s) is < 0.2 % of the wall.

| figure | value | derivation |
|---|---:|---|
| **POINT** | **18 218 core-min** (303.6 core-h; **USD 15.58 derived**) | 602 128 × 118 000 / 6.50e4 = 1.093e6 core-s |
| **CEILING (cap)** | **27 400 core-min** (456.7 core-h; **USD 23.43 derived**) | 1.504 × POINT: covers parallel efficiency down to 0.85 and a further ~20 % rate degradation; **an overrun stops the run** |
| **timeout** | **205 500 s = 57.1 h wall** | cap × 60 / 8 ranks |
| expected wall | ≈ 38 h ideal, **≈ 45 h at 0.85 efficiency** | 1.093e6 / 8 / eff |
| **10× runaway guard** | **182 182 core-min** | 10 × POINT; unreachable behind the 1.5× timeout, registered so the figure exists for the monitor |
| serial-equivalent wall | 12.65 days | why §5 decomposes |

Dollars at the owner-stated **$0.0513/core-h** are **derived, not measured**
(`COMPUTE_BUDGET_CHARTER.md` §5). **Against §14.8's rough bound of 150–200
core-h:** POINT is 303.6 core-h — the difference is the 1.5 iteration factor
of §3, which §14.8 did not include and named as its optimistic assumption.
**Against the rung's USD 25 pre-authorised ceiling:** T3 has spent USD 6.171
derived (§14.9); POINT brings it to **USD 21.75**, the CEILING to **USD 29.60 —
over the USD 25 line if the cap is reached.** Larger CPU runs are covered by
Sanaa's 2026-08-21 blanket (`CLAUDE.md` rule 12) **and a blanket is not a
per-item read (rule 9)**: the supervisor's fire order must name this figure.
Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at completion.

## 7. The launcher — `launch_t3_rff.sh` (sha256 `cb151a939517e064`, 105 lines)

Modelled on `scripts/launch_k0f.sh`: the caller starts it and returns; it
re-execs itself **once** under `setsid`; inside the detached copy the solver
runs under **`timeout` in the foreground with no `setsid` between them**, so
`rc` is the solver's own (the measured `setsid ... ; rc=$?` = 0-for-a-crash trap
in that file's header). It:
- **refuses** `--ranks ≠ 8`, `--timeout ≠ 205 500`, any case not named `R_ff`,
  an existing `STATUS.R_ff`, an existing `0/`, any numeric time directory
  (regex, never a glob — ARM 1), any `processor*`, a missing mesh, a process
  already in the case directory (G2), an unresolvable solver or `mpirun`, and a
  failed `check_case_provenance.py` — all **before** writing anything;
- arms `0/` from `0.orig` and touches `0/T` **last**; runs `checkMesh`
  (`log.checkMesh.run`) and `decomposePar -force`, refusing with a `STATUS`
  `rc=126` if decomposition fails;
- runs `timeout --signal=TERM --kill-after=120 205500 mpirun -np 8
  buoyantBoussinesqSimpleFoam -parallel`, captures `rc`, runs
  `reconstructPar -newTimes`, and writes `STATUS.R_ff` atomically with `rc`,
  `wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`, **`capped`**
  (`wall_s ≥ timeout_s`, the independent expiry witness), `checkmesh_rc`,
  `decomposepar_rc`, `reconstructpar_rc`, `solver_path`, `note`, timestamps;
  and exits with the solver's `rc`, never 0.
- **Checks run before this freeze:** `bash -n` clean; the three refusal arms
  (ranks 4, timeout 100, case `R_f`) each `rc = 2` with the reason named;
  `scripts/check_launcher_can_launch.py --worktree` ARM 1: **0 suspect globs**;
  ARM 2 `--one-iteration R_ff` with the **real solver in scratch**: **PASS —
  `rc = 0`, reached `Time = 1`** (serial, one timestep; fields discarded).

**The launch command the supervisor would issue** (and the queue entry's argv):
```
/home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/launch_t3_rff.sh \
    --case-dir /home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/R_ff \
    --timeout 205500 --ranks 8
```

## 8. The comparator — frozen `analyse_t3.py` CANNOT grade this triple; a reader is OWED

`analyse_t3.py` (HEAD blob **`d5e4a9eb`**, 1 150 lines, sha256
`f41c544d…498741` as recorded in `T3_EXT1_AMENDMENT.md` §11) hard-codes
`LADDER = {"c": "R_c", "m": "R_m", "f": "R_f"}` (`:78`) and refuses unless all
eight `DONE.<case>` markers of its `CASES` list exist (`:793`). **It cannot
take `(R_m, R_f, R_ff)` and it is not amended** — it is the comparator of the
graded record and stays frozen. **Owed, and to be frozen by sha in a dated
amendment to this file BEFORE `R_ff` is graded:** `analyse_t3_rff.py`, which
**imports** `analyse_t3`'s measurement functions (`measure`, `gci_unequal`,
`graded_verdict`, the planted-zero control at `:307`/`:801`, `PLANT =
1.234e-03`) and evaluates the ladder `{"c": "R_m", "m": "R_f", "f": "R_ff"}`
with the same gate order, the same `Fs = 1.25`, the same `P_MIN`-class refusal
the T-family adopted at `352aef0d` (observed order below 0.5 → no GCI), and a
`mark_done_t3_rff.py` that calls `mark_done_t3.check(root, "R_ff")` (and the
two-segment rule if extended). Until that amendment lands, **no verdict on
`R_ff` exists and none is written by hand.**

## 9. Predictions — registered before compute

Existing numbers (`gate_t3.json`, ext1): `x_peak/H` = 6.0895 / 6.13516 /
6.14120 on `(c, m, f)`; `St_peak` = 0.00336772 / 0.00343791 / 0.00350859.

**P1 — G2 `x_peak/H` on `(R_m, R_f, R_ff)`.** If the medium→fine step 0.00604
is second-order behaviour, `R_ff` ≈ **6.1436** (step 0.0024 at `r = 1.599`);
first-order would give 6.1450. **Registered expectation: `x_peak/H(R_ff)` in
[6.141, 6.148] and the triple CONVERGING with observed order `p` in
[0.5, 3.0].** A `p` above 3.0 again means the levels cannot resolve an order
(the §14.4 reading, not superconvergence); a `p` below 0.5 is refused as no
demonstrated order. Either is reported with the numbers.

**P2 — G1 `St_peak` on the new triple.** `St_peak` moved +7.02e-5 then
+7.07e-5 across `(c, m, f)` — equal steps, i.e. no convergence with mesh at
this `y+` sequence. **Registered expectation: the triple is NOT CONVERGING
(STAGNANT or DIVERGENT), `St_peak(R_ff)` ≈ 0.00358 if the equal-step pattern
holds.** If instead it comes in near **0.003536** (the second-order value) and
the triple is CONVERGING with `p` in [0.5, 3.0], that is the informative
surprise and is recorded as P2 **wrong**. G3/G4 `St(10H)`, `St(20H)` are
predicted to follow G1.

**P3 — iterative convergence.** `R_ff` reaches the `1e-6` criterion by
118 000: **registered YES.** If NOT CONVERGED, every row is NOT A RESULT at
gate (1) on the new triple, the ext1 decision rule is applied once (§3), and
if STALLED at 160 000 the rung says so.

**What the verdicts would mean.** A CONVERGING `(R_m, R_f, R_ff)` triple on a
row lifts that row from gate (1)/(2) to gate (3): **BLOCKED** (the primary is
not held, §10) with value, triple, GCI and the deviation from the secondary
digitisation REPORTED beside it. A DIVERGENT / STAGNANT / OSCILLATORY triple
leaves the row **NOT A RESULT** with the numbers printed — and would say that
the family's `y+`-tracking refinement does not converge the wall heat transfer,
which is itself the finding T1b's 15 % wall-treatment sensitivity predicts.
The `delta_99/H` inlet-window flag (0.67 against a registered [0.80, 1.35])
stands regardless and is not addressed by a fourth level.

## 10. What this cannot earn

- **The primary, Vogel & Eaton (1985), DOI 10.1115/1.3247522, is NOT
  OBTAINED** (`T3_reference_primary.json` absent, `primary_sha256 = null`).
  Gate (4) is unreachable: **no row can return PASS or GATE FAIL, and HOLDS is
  unreachable. This level earns `V`/`G` — a grid statement on a converged
  triple — and nothing beyond it.** Obtaining the primary remains necessary
  and, with the inlet-window flag live, not sufficient.
- It does not amend `analyse_t3.py`, `mark_done_t3.py`, `build_t3.py` or any
  frozen T3 file. It does not authorise the launch. It does not authorise any
  send — **SUBMISSIONS REMAIN PARKED** (rule 7).

## 11. The freeze set — committed in the same commit as this document

| file | sha256 (first 16) | lines / note |
|---|---|---|
| `verification/runs/T-family/T3_runs/build_t3_rff.py` | `a9c5bba6c7e88905` | 83; AST `assert` count 0; `--check` identical under `python3` and `python3 -O` |
| `verification/runs/T-family/T3_runs/launch_t3_rff.sh` | `cb151a939517e064` | 105 |
| `T3_runs/R_ff/system/blockMeshDict` | `eb9aac44f49fc21e` | counts of §1.1 |
| `T3_runs/R_ff/system/controlDict` | `1d5b4b701c535a35` | `endTime 118000` |
| `T3_runs/R_ff/system/decomposeParDict` | `2980bb179f3b8b6d` | `simple n (8 1 1)` |
| `T3_runs/R_ff/CASE.txt` | `305fda81988446b4` | builder lines + R_ff restatements |
| `T3_runs/R_ff/log.checkMesh` | `dc140caaf2a0dd6f` | the birth certificate, 602 128 cells |
| `T3_runs/R_ff/{0.orig/*, constant/{g,transportProperties,turbulenceProperties}, system/{fvSchemes,fvSolution}}` | byte-identical to `R_f` | §1 |

Frozen inherited instruments, by HEAD blob: `build_t3.py` `340a5079`,
`check_t3_mesh.py` `0e4afc3c`, `mark_done_t3.py` `5da28c73`,
`mark_done_t3_ext1.py` `e4cbb992`, `analyse_t3.py` `d5e4a9eb`.

---

## AMENDMENT 1 — 2026-08-26 (PRE-FIRST-COMPUTE): the grading path, frozen. Document v1.0 -> v1.1

**Condition (`CLAUDE.md` rule 2), and how it was checked.** Immediately before
this commit `ls verification/runs/T-family/T3_runs/` shows **no `STATUS.R_ff`,
no `DONE.R_ff`, no `gate_t3_rff.json`**, and `R_ff/` holds no `0/`, no time
directory and no `processor*` — `R_ff` has not iterated; zero core-minutes
spent. Both new instruments **refuse** on the live tree today (`exit 2`:
"no completion marker DONE.R_ff" / "no STATUS.R_ff"). The supervisor's ruling
(2026-08-26) is the reason: a comparator written after the data exist is the
Charter §2d hazard, so §8's owed reader is delivered and frozen **now**.

**The frozen grading path — two files, named by git blob (content-safe staged):**

| file | git blob | sha256 (first 16) | lines |
|---|---|---|---:|
| `verification/runs/T-family/T3_runs/analyse_t3_rff.py` | `44e3e2b8038b9274` | `e1aaf61b236fa72a` | 230 |
| `verification/runs/T-family/T3_runs/mark_done_t3_rff.py` | `9436399f8682efb6` | `0ad4f08ee0ee10b6` | 157 |

**`analyse_t3_rff.py`** grades the triple `{"c": "R_m", "m": "R_f", "f": "R_ff"}`
by **importing** the frozen `analyse_t3.py` (blob `d5e4a9eb`), which is not
edited. Reused from it, by name: `measure` (the reader every graded number
passes through), `planted_zero_control` (`PLANT = 1.234e-03` K, planted into
`R_f`, the medium level, refusal if unseen), `gci_unequal` (Celik unequal
ratios, `Fs = 1.25`; **its `p < 0.5 -> STAGNANT` branch is the observed-order
floor `P_MIN = 0.5` that T11 adopted at `352aef0d` — it is the frozen file's
own floor, stated here, not re-implemented**; exactly equal steps return
`DIVERGENT` at `p = 0`), `graded_verdict` (the ordered gate: level not
CONVERGED → NOT A RESULT; triple not CONVERGING → NOT A RESULT; outlet test;
no primary → **BLOCKED**; band), `ratios_from_ncells`, `triple_of`,
`load_secondary`, `load_primary`, `GRADED`, `VERDICTS`. Not reused: `main()`'s
c/m/f wiring and eight-case loop, and `read_status` (single-line pool format;
`launch_t3_rff.sh` writes key=value lines). The G4 outlet-independence input is
the graded record's own `gate_t3.json` row `DO` (`criterion_met`), not
re-measured; absent → NOT MEASURED, disclosed. Refuses on any absent
`DONE.R_m` / `DONE.R_f` / `DONE.R_ff`. Writes `gate_t3_rff.json` only; the
decomposition-confound caveat of §5 is carried on every row. `--selftest`
(**PASS under `python3` and `python3 -O`, 13/13**) drives: the P1-shaped
triple → CONVERGING `p = 1.993` → BLOCKED; equal steps → `p < P_MIN` → NOT A
RESULT with no GCI; `p = 0.6` CONVERGING vs `p = 0.4` STAGNANT (the floor is
live); a NOT_CONVERGED fine level → NOT A RESULT at gate (1); DIVERGENT and
OSCILLATORY → NOT A RESULT; the outlet guard → NOT A RESULT; the closed
vocabulary; **refusal `exit 2` on an absent `DONE.R_ff` driven in a scratch
root**; the plant read back at `1.2340000000108e-03`; the negative arm
(identical checkpoints → change 0). AST `assert` count **0**.

**`mark_done_t3_rff.py`** calls the frozen `mark_done_t3.check(root, "R_ff")`
(blob `5da28c73`; clauses 1–6: rc from the in-wrapper `STATUS.R_ff`, `End`
line, last time == `endTime`, fields present, `ExecutionTime` count, age guard
vs `0/T`) and, if `log.solve.ext1` exists, the frozen
`mark_done_t3_ext1.check_ext` (blob `e4cbb992`) verbatim; adds
**`reconstructpar_rc = 0`** as physics-critical (the fields are reconstructed).
**Field classes per L-342 (Sanaa's rule, `LESSONS.md:14663`): physics-critical**
= solver rc, End, last time, fields, age guard, reconstructPar rc — any failure
is NOT DONE, an **absent `STATUS.R_ff` is a refusal (`exit 2`)**;
**infrastructure** = `wall_s`, `ranks`, `core_min`, `timeout_s`, `capped`,
`checkmesh_rc`, `decomposepar_rc`, the `log.launch` / `log.decomposePar` /
`log.reconstructPar` / `log.checkMesh.run` presence — reported, **absent →
NOT MEASURED, disclosed in the marker, never a refusal**. Never retracts;
`--dry-run`. `--selftest` (**PASS under `python3` and `python3 -O`, 8/8**):
clean → DONE; `rc=1`, `reconstructpar_rc=3`, no `End`, short
`ExecutionTime` count, fields older than `0/T` → each NOT DONE with no marker;
absent STATUS → `exit 2`; infrastructure fields absent → DONE with NOT MEASURED
disclosed. AST `assert` count **0**.

**Cost ruling recorded [lab-attributed, from the heat-transfer supervisor's
ruling of 2026-08-26; not Sanaa's words as read by this lane]:** the POINT
**USD 15.58 derived** is inside the rung's authorisation under Sanaa's
2026-08-25 CPU cost directive — caps are runaway guards, not budget gates; the
USD 25 line predates it and is superseded for CPU spend. **The CEILING 27 400
core-min stands as the registered stop** (timeout 205 500 s at 8 ranks). §6's
figures are unchanged.

**No gate, threshold, cap or label moves. Lines whose number changed above
this section: 0.** The launch remains the supervisor's order; nothing here fires.

---

## AMENDMENT 2 — 2026-08-26 (PRE-FIRST-COMPUTE): the launcher's G2 cwd-holder guard refused its own ancestor shell under the queue runner's `cd` form — one zero-compute refusal; the T10aR2/T4b repair applied; launcher re-frozen. Document v1.1 -> v1.2

**Lines whose number changed above this section: 0** (appended to the worktree copy after verifying it byte-identical to the HEAD blob `f35c4cc6` of commit `33dbe337`). Ruled by the heat-transfer supervisor `[lab-attributed]` after crash triage of the refused launch; drafted by a lab lane. **Condition (`CLAUDE.md` rule 2), and how it was checked:** zero core-minutes have been spent on `R_ff`. Checked at 20:48:56Z, immediately before this commit: `ls verification/runs/T-family/T3_runs/R_ff` shows `0.orig CASE.txt STATUS.T3_R_ff constant launcher.queue.out log.blockMesh log.checkMesh system` — **no `0/`**, no `processor*`, and the numeric-time-directory regex (`find -maxdepth 1 -type d -regex '.*/[0-9]+(\.[0-9]+)?'`) returns nothing; `ls verification/runs/T-family/T3_runs/` shows **no `STATUS.R_ff`** (the in-wrapper record §7 names) and **no `DONE.R_ff`**. The only two files newer than the freeze are the queue runner's own: `R_ff/STATUS.T3_R_ff` (`launcher_rc=2 end=2026-08-26T17:43:48Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc` — the runner's bookkeeping of the argv's exit, not a solver record) and `R_ff/launcher.queue.out`, neither of which is edited by this amendment. No solver process was ever started: the refusal sits before the arming block (`cp -r 0.orig 0`).

**The refusal, verbatim** (`verification/runs/T-family/T3_runs/R_ff/launcher.queue.out`, runner launch 2026-08-26T17:43:48Z, entry `verification/queue/heat-transfer/launched/T3_R_ff.json`, pid 313461 / sid 313461):

```
REFUSE: G2: pid 313462 already running in R_ff
```

**Ground.** The queue runner's fixed form `setsid nohup bash -c 'cd <cwd>; <argv> > <cwd>/launcher.queue.out 2>&1; …'` (`scripts/queue_runner.py` line 26) makes the wrapper shell — the launcher's own parent, pid 313462 here — hold the case directory as cwd. The G2 guard at `launch_t3_rff.sh:55` (blob `fe9fda5c`) refused **any** process whose cwd is the case directory, excluding not even `$$`; under the runner it refuses its own launch by construction. This is the defect already repaired on `launch_t10aR2.sh` (commit `9fa66065`, three refusals) and `launch_t4b.sh` (commit `51618879`, pre-empted).

**The repair — the only change in the file.** Line 55 is replaced by the same lineage-aware scan used in `9fa66065`: a `ppid_of()` reader of `/proc/<pid>/stat`, the launcher's ancestor chain `LINEAGE` walked from `$PPID` to pid 1, an `own_lineage()` test that also walks a candidate's ancestors to `$$` (descendants), and the same `/proc` scan, which now `continue`s on the launcher's own lineage and still refuses, naming the pid, on any foreign process — the message text `REFUSE: G2: pid <pid> already running in R_ff` is unchanged. Nothing else moves: `--ranks` must still equal 8, `--timeout` 205 500, the case name, `STATUS.R_ff` / `0/` / time-dir / `processor*` / `0.orig` / mesh refusals, `check_case_provenance.py`, `0/T` touched last, `checkMesh`, `decomposePar -force`, the solver in the foreground under `timeout`, `capped`, `reconstructPar -newTimes`, the atomic `STATUS.R_ff`, `exit "$RC"`.

**Driven on a scratch copy of `R_ff` (outside the run tree, `endTime` set to 1, deleted afterwards), with the repaired launcher from the worktree and `--no-detach`:** (a) a planted foreign `sleep` with cwd = the scratch case directory → `REFUSE: G2: pid 393000 already running in R_ff`, rc 2, the planted pid named, nothing written; (b) the runner's exact form `setsid nohup bash -c 'cd <scratch R_ff>; launch_t3_rff.sh --case-dir <scratch R_ff> --timeout 205500 --ranks 8 --no-detach > launcher.queue.out 2>&1'` → the guard passed, `check_case_provenance.py` passed, `0/` armed, `checkMesh` rc 0, `decomposePar` rc 0, `mpirun -np 8` ran one iteration to `Time = 1` / `End`, wall 3 s, **in-wrapper `STATUS.R_ff` `rc=0`**, `core_min=0.400` (scratch, not charged to the rung). That scratch STATUS carried `reconstructpar_rc=1` — `reconstructPar -newTimes` reported "No times selected" because the scratch `endTime 1` is below the registered `writeInterval 2000`; the registered `endTime 118000` is a multiple of 2000, so this is a property of the one-iteration arm, not of the launcher.

**Freeze set, §11 row for the launcher — STRUCK, not deleted:** ~~`verification/runs/T-family/T3_runs/launch_t3_rff.sh` | `cb151a939517e064` | 105~~ → **`verification/runs/T-family/T3_runs/launch_t3_rff.sh` | git blob `10159789` (full `1015978981240c5278c6923b2e70d905f968ab83`) | sha256 `b104030495bcc7e8` | 130 lines; `bash -n` clean; the two guard arms above driven.** The §7 heading's `cb151a939517e064`, 105 lines describes the struck version. Every other row of §11 and the AMENDMENT 1 grading path (`analyse_t3_rff.py` `44e3e2b8`, `mark_done_t3_rff.py` `9436399f`) are unchanged. No gate, band, threshold, floor, control, cap, timeout or cost moves; §6's POINT 18 218 core-min and the CEILING 27 400 core-min stand; the launch command of §7 is unchanged.

**Status after this amendment: PRE-REGISTERED, BUILT, NOT FIRED; re-enqueued as `verification/queue/heat-transfer/T3_R_ff_v2.json` citing this amendment's commit.**
