# M6I-R1 — ONERA M6 PRIMAL ON THE TMR-GENERATOR GRID FAMILY, PRE-REGISTRATION

**Item:** `M6I_R1_SOLVE`. **Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.

**Authority.** Sanaa, `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`, addendum
~21:25Z: *"stop fighting the mesher and import a grid … Run the family under the two-tier
standard — quality disclosed, not gated — and M6 is graded against the 14 bands."*
And §D / §A of `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`:
the finalization lane, **M6 with the NASA grid, 3 levels, 4 ranks each.**

**STATUS: FROZEN AT THE COMMIT THAT INTRODUCES THIS FILE. NO SOLVER HAS RUN ON ANY M6I
LEVEL.** Condition checked, and how (rule 2): at the moment of writing, each of
`verification/runs/M6I_runs/{L1,L2,L3}` holds `constant/polyMesh`, `system/`, `0.orig/`
and **no `0/` and no numeric time directory**, and none holds `RC.txt`. The age guard of
rule 4 is intact on all three.

---

## 0. WHAT IS NEW HERE AND WHAT IS NOT

**NOT new, and not touched by this document: the bands.** Cp and shock location are
graded by the document and the script **frozen at commit `4c931d97c`**:

| frozen artifact | blob sha at `4c931d97c` |
|---|---|
| `verification/campaign/A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md` | `9667e0e584d6c4f5fe21f0ab8b57626b34fe0020` |
| `scripts/grade_m6_agard_cp.py` | `e9d5c04b420b99201ab19e694b76d1b9eda62443` |

**Verified by this lane, not taken from any agent's message:** `git hash-object` on the
working-tree copy of each file returns exactly the blob sha above, and `git rev-parse
HEAD:<path>` returns the same — so the file on disk **is** the file frozen at
`4c931d97c`, unchanged since. sha256 of the reference data table
`models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat` is
`727c7247eee079b0a12f97cf13d12352782d29ad5dde4d91b039cea2b944f050`.

**NEW here: the primal.** `4c931d97c` §9 names one graded primal — the DAFoam case
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic`, a **single grid**. This document
registers a **three-level family** on the TMR-generator grids, run by OpenFOAM's
`rhoSimpleFoam`, and submits each level to the **unchanged** frozen grading path. The
frozen file is not edited and none of its gates, thresholds, definitions or labels moves.

---

## 1. THE 14 BANDS, AS CITED FROM `4c931d97c` — the values this run will be graded against

**Q1 — Cp, 12 rows (six stations × upper/lower), off-shock orifices only.**

> **`RMS(Cp_cfd − Cp_exp) ≤ 0.050`** for **each** of the 12 station/surface rows.
> (`A3_M6…PREREGISTRATION.md` §5 B1; `grade_m6_agard_cp.py:BAND_CP_RMS = 0.050`.)

The frozen document labels this **the lab's declared allowance, judgement, not derived**,
anchored at 25× AGARD AR-138's own instrument floor of **0.0020** — because AR-138 §6.1.1
is **blank** (no published Cp accuracy), §6.1.4's repeatability pairs are at other
conditions, and §6.2 applies **no wall-interference correction** at a semispan/tunnel-width
ratio of 0.7. That label travels with every number this run produces.

**The six graded stations: η = 0.20, 0.44, 0.65, 0.80, 0.90, 0.96.** η = 0.99 excluded
(tip). **0.96, not 0.95** — the community's 0.95 is a mis-citation of AR-138 §5.1.1.

**Q2 — upper-surface shock location, 2 rows.**

> **`|x_shock_cfd − x_shock_exp| ≤ Δ_local`**, one local orifice interval, measured by the
> script from the reference file itself at the interval D1 selects, asserted against the
> registered table to ±0.0125 or the script **refuses**.
> Registered table (§5 B2): **η = 0.65 → ±0.0500 c; η = 0.90 → ±0.0400 c.**
> (`grade_m6_agard_cp.py:BAND_B2_TABLE = {0.65: 0.0500, 0.90: 0.0400}`.)

**12 + 2 = the 14 bands.**

**Verdict rule (§5 B3, unchanged):** `PASS` — all 12 rows inside B1 **and** both shock
stations inside B2. `GATE FAIL` — admissible primal, any row outside. `NOT A RESULT` —
any precondition or the planted control fails; this overrides both and is never overridden.

**Preconditions the grader enforces (§6):** P1 extraction file with a `freestream` block;
**P2 CFD `M_inf` within ±0.005 of 0.8395** and α within 0.05° of 3.06°, else the
comparison is **refused, not forced**; P3 all six stations present; **P4 an `End` line in
the run log**; P5 iterative convergence read and printed whatever it says.

**Planted-zero control (§7, rule 3):** `PLANT = 1.234e-01` into the CFD Cp of
η = 0.44 lower **by index**, read back through the **same** pairing/RMS path; if the
reader cannot see it the grader exits 2 with `NOT A RESULT — PLANTED CONTROL UNSEEN`.
The plant lives in the frozen grader and is not re-implemented here.

---

## 2. 🔴 THE TURBULENCE MODEL — WHAT THE BAND REGISTRATION ACTUALLY SAYS

This lane was instructed to take the turbulence model **from** the `4c931d97c`
registration and not to choose one. **Read in full, that registration NAMES NO
TURBULENCE MODEL.** It is a grading document over an already-existing primal; it fixes
stations, definitions, bands, preconditions and the planted control, and it fixes no
solver setting of any kind. Reporting it as having named one would be false.

**What it does carry, and it is the only turbulence signal in it:** §6 P5 and §9 both
disclose that the sibling primal `A3GC-AR1` is `NOT A RESULT` **"on an internal nuTilda
convergence gate"**, and `nuTilda` is the Spalart–Allmaras working variable.
Read directly (not from any message) from the graded primal's own
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/constant/turbulenceProperties`:
**`RASModel SpalartAllmaras`**.

**REGISTERED: `SpalartAllmaras`**, carried from the primal the bands were written against
so the family and the frozen comparison stay on one model. This is a **carry-over, not a
free choice**, and the gap in the frozen document is stated here rather than papered over.

---

## 3. THE GRIDS — the family that already exists, and its disclosed quality

`verification/runs/M6I_runs/{L1,L2,L3}`, built 2026-09-01 by
`build_m6i_ladder.sh` from the **NASA TMR wing generator** (`hcf_wing` /
`hcf_coarsening`, `wing_release_072319`), **one generator call then two coarsenings**, so
`r = 2.000000` exactly in every direction and the levels are exact node subsets.

| level | cells | wing faces | symmetry faces | farfield faces | ranks | y⁺ target |
|---|---|---|---|---|---|---|
| **L1** fine | **983,040** | 7,680 | 12,288 | 7,680 | 4 | 0.25 |
| **L2** medium | **122,880** | 1,920 | 3,072 | 1,920 | 4 | 0.50 |
| **L3** coarse | **15,360** | 480 | 768 | 480 | 4 | 1.00 |

Geometry from the generator's own `input.nml`: **root chord 1.0**, semispan
**b = 1.4760179762198**, taper 0.5625159852668158, LE sweep 29.999°, farfield radius 100
root chords, sharp trailing edge, rounded tip.

**🔴 MESH QUALITY, DISCLOSED AND NOT GATED** (Sanaa's two-tier ruling, *"quality disclosed,
not gated"*). Measured by `checkMesh` on the patched meshes,
`verification/runs/M6I_runs/{L1,L2,L3}/log.checkMesh_patched`:

| level | max non-orthogonality | average | max skewness | max aspect ratio | checkMesh closing line |
|---|---|---|---|---|---|
| L1 | **87.746°** | 32.970 | **5.112** | 1578.62 | `Failed 2 mesh checks.` |
| L2 | **86.465°** | 33.371 | **8.301** | 873.82 | `Failed 1 mesh checks.` |
| L3 | **87.662°** | 34.627 | 2.775 | 1243.59 | `Failed 1 mesh checks.` |

This family was graded **`GATE FAIL` on mesh admission at R0** (`R0_RESULTS.md` §3) against
`MESH_STANDARD.md` §3.1's 70°/4 thresholds, and **that verdict stands and is not lifted by
this document.** It is run anyway because Sanaa ruled the two-tier standard applies with
quality disclosed. The maximum is **flat, not falling**, across a 64× cell increase
(87.66 → 86.46 → 87.75), and `checkMesh`'s closing line mentions non-orthogonality on
**none** of the three levels — read the maxima above, never the closing line.

**Consequence registered BEFORE the run:** an 87° non-orthogonality floor is a plausible
cause of a Cp band miss, and if the rows miss, *"the mesh is bad"* is a **prediction made
here**, not an excuse invented afterwards.

**Patches.** The converted meshes carried ONE patch (`defaultFaces`, wall). The split is
geometric and was measured before it was applied: `symmetry` = boundary faces with face
centre `y < 1e-8`; `wing` = `1e-6 ≤ y`, `|z| ≤ 1`, `−3 ≤ x ≤ 4`; `farfield` = the
remainder (the r = 100 hemisphere about (0.5, 0, 0)). It is **exhaustive and
level-independent**, and that is an arithmetic identity, not a hope:
768+480+480 = 1,728 (L3), 3,072+1,920+1,920 = 6,912 (L2), 12,288+7,680+7,680 = 27,648 (L1)
— exactly the `nFaces` each level's own pre-split `boundary` file carried.
Types: `wing` **wall**, `symmetry` **symmetry**, `farfield` **patch**.

---

## 4. THE CONDITION — AGARD AR-138 TABLE B1-14, TEST 2308

`verification/runs/M6I_runs/FREESTREAM_M6I.json`, written by the build script
**before any solve** and read by the extractor; **never re-derived from the solution.**

| quantity | value | how fixed |
|---|---|---|
| **M∞** | **0.8395** | AR-138 TABLE B1-14 header. Grader P2 tolerance ±0.005. |
| **α** | **3.06°** | same header. Imposed as the velocity direction, not by rotating the mesh. |
| T∞ | 300 K | registered |
| p∞ | 101 325 Pa | registered |
| a∞ | 347.1562754 m/s | γ = 1.3997263, R = 287.0024888 (molWeight 28.97, Cp 1005) |
| U∞ | **291.4376932 m/s** | components (291.0221558, 0, 15.55743652) |
| ρ∞ | 1.176819063 kg/m³ | perfectGas |
| q∞ | 49 977.11021 Pa | ½ρU² |
| **Re (root chord = 1.0)** | **14.6 × 10⁶** | the generator's own `target_reynolds_number`, and **= AR-138's Re 11.72e6 on the MAC re-referenced to the root chord** (11.72e6 × 0.8059/0.64607 = 14.62e6) |
| μ(300 K) | 2.349105706e-05 Pa·s | **Sutherland**, `Ts = 110.4 K`, **`As = 1.855359319e-06`** chosen so μ(300 K) lands the root-chord Re exactly on 14.6e6 |
| ν∞ | 1.996148583e-05 m²/s | |
| ν̃∞ | **5.98844575e-05** | 3ν, the standard SA freestream |

**Thermophysical:** `hePsiThermo / pureMixture / sutherland / hConst / perfectGas /
sensibleInternalEnergy`. **Transport is Sutherland, not const.**

**Boundary conditions.** `wing`: U `noSlip`, p `zeroGradient`, T `zeroGradient`, ν̃
`fixedValue 0`, νt `nutLowReWallFunction` (**every level is wall-resolved, y⁺ ≤ 1**),
αt `compressible::alphatWallFunction` Prt 0.85. `farfield`: U `freestreamVelocity`,
p `freestreamPressure`, T `inletOutlet`, ν̃ `freestream`, νt/αt `calculated`.
`symmetry`: `symmetry` on every field.

**🔴 DISCLOSED GEOMETRY DIFFERENCE.** The generator's semispan-to-root-chord ratio is
**1.47602**; the TMR/AGARD nominal M6 (semispan 1.1963 m, root chord 0.8059 m) is
**1.48443** — **0.57 % apart**. Stations are cut at `y = η × 1.4760179762198`, i.e. as a
fraction of **the semispan of the geometry that actually ran**. The 0.57 % is disclosed,
not corrected, and it is a candidate explanation for a near-tip row miss.

---

## 5. NUMERICS — identical on all three levels, from one script

`rhoSimpleFoam`, steady, `transonic yes`, `consistent yes` (SIMPLEC),
`nNonOrthogonalCorrectors 2`, `pMinFactor 0.2`, `pMaxFactor 2.0`.
Convection: `div(phi,U)`, `div(phi,e)`, `div(phi,K)`, `div(phi,Ekp)` = `bounded Gauss
linearUpwind limitedGrad`; `div(phi,nuTilda)` = `bounded Gauss upwind`; `div(phid,p)` =
`Gauss upwind`. Gradients `cellLimited Gauss linear 1` on U, e, ν̃.
**Laplacian and snGrad `limited corrected 0.33`** — the registered remedy for the family's
86–88° non-orthogonality, applied **identically on all three levels** so the family stays
similar. `wallDist meshWave`.
Linear solvers: p `GAMG/GaussSeidel` tol **1e-9** relTol 0.01; U/e/ν̃ `PBiCGStab/DILU` tol
**1e-10** relTol 0.01 — **strictly tighter than every convergence gate below**, so no gate
is satisfied by linear-solver slop.
Relaxation: fields p 1, ρ 0.05; equations p 1, U 0.7, e 0.7, ν̃ 0.7.
Decomposition: **`hierarchical (2 2 1)`, 4 subdomains — deterministic. Not `scotch`**, which
is not reproducible across runs, and the graded quantity is read off a surface field.

**🔴 NO `residualControl`, BY REGISTRATION.** A `residualControl` exit stops the solver
*before* `endTime`, and rule 4's completion clause reads `last time == endTime`. Letting
the solver decide when it has converged would make the completion rule unsatisfiable by
construction. Convergence is graded from the histories, by §7 below.

---

## 6. BUDGET, CHECKPOINTS, COST, MEMORY

| level | **iteration budget (`endTime`)** | **`writeInterval`** | `purgeWrite` | writes | exact divisor? |
|---|---|---|---|---|---|
| L3 | **3,000** | **200** | 2 | 15 | 3000/200 = 15 ✔ |
| L2 | **5,000** | **200** | 2 | 25 | 5000/200 = 25 ✔ |
| L1 | **8,000** | **200** | 2 | 40 | 8000/200 = 40 ✔ |

**Checkpoint interval: 200 iterations on every level, and the basis is the directive's own
fallback** — *"if the rate is unknown, checkpoint every 200 iterations until it is"*
(Sanaa, run instructions item 1). **The rate IS unknown: no M6I level has ever been
solved**, and no rate is declared in the queue entries, so gate A evaluates the
200-iteration fallback rather than a rate this lane would have had to invent. The exact
divisor means the last write lands **on** `endTime`, so rule 4's "fields present at
endTime" clause is satisfiable. `purgeWrite 2` keeps the last two (her item 1).

**COST (rule 12). Unit: core-minutes. Dollars DERIVED at $0.0513/core-h.**
**`cost_basis`: DERIVED, NOT MEASURED — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5); the rate is REPORTED-BY-OWNER (Sanaa 2026-08-21/22).**

The per-iteration figure is a **PROJECTION, NOT A MEASUREMENT**, and is labelled so: a
throughput of **1.2 × 10⁵ cells/s/rank** for `rhoSimpleFoam` + SA + GAMG with 2
non-orthogonal correctors. No M6I solve exists to measure, and the projection is
registered here precisely so the smoke can falsify it.

| level | cells/rank | projected s/iteration | iterations | projected wall | **core-min** | derived $ |
|---|---|---|---|---|---|---|
| L3 | 3,840 | 0.032 | 3,000 | 96 s | **6.4** | 0.005 |
| L2 | 30,720 | 0.256 | 5,000 | 1,280 s | **85.3** | 0.073 |
| L1 | 245,760 | 2.05 | 8,000 | 16,384 s (4.55 h) | **1,092.3** | 0.934 |
| | | | | **TOTAL** | **1,184** | **≈ $1.01** |

**CAP: 3 × estimate = 3,551 core-minutes (≈ $3.04), registered per level as
L3 19.2 / L2 256 / L1 3,277.**
**🔴 THE CAP IS REGISTERED AND IS NOT A KILL.** Sanaa's directive #17 (2026-09-12, *no run
stopped by time or budget cap*) and her item 7 (*"cap → NOT A RESULT, never raised"*) are
read together: a crossing grades the row **`NOT A RESULT`** and the cap is **never raised**;
**nothing kills the solver on spend or clock**, and `launch_m6i.sh` contains no timeout,
no clock check and no spend check. A **MemAvailable** guard is a physics guard and is
permitted; the runner holds it.

**MEMORY, per level. DECLARED, NOT A MEASURED PEAK RSS, and said so plainly.** Envelope
~3 GB per million cells for a compressible steady case with GAMG, summed over 4 ranks:

| level | cells | **declared footprint** | **`memory_floor_gb` in the entry** |
|---|---|---|---|
| L3 | 15,360 | **0.5 GB** | 4 |
| L2 | 122,880 | **1.0 GB** | 4 |
| L1 | 983,040 | **4.0 GB** | 8 |

Independent upper bound that does not use the per-Mcell figure: the host has **739 GiB
with 726 GiB available** (measured 2026-09-12 after the 21:32Z boot), so even a 10× miss
on the largest level clears by two orders of magnitude. The floors are set **above** the
footprints so the launcher's gate is the conservative one.

---

## 7. ITERATIVE CONVERGENCE — the criteria, fixed here, and none of them lengthens the run

A level satisfies **IC** only if **all four** hold. A level failing any one is **`NOT A
RESULT`** for its rows at the core-minutes spent, and **`endTime` is NEVER extended to
chase a limb**.

- **IC-1** no `NaN`, no floating-point exception, no `Foam::error` in the solve log.
- **IC-2** at the final iteration, initial residuals **Ux, Uy, Uz, e, nuTilda ≤ 1e-5**
  and **p ≤ 1e-4** (the transonic pressure equation is the stiff one and is gated looser,
  deliberately and in advance).
- **IC-3** over the **last 600 iterations** (an absolute count, never a fraction of
  `endTime`, so extending the run can never buy a pass): `max|CL − mean|/|mean| ≤ 1 %` and
  the same on CD.
- **IC-4** the wing-patch `yPlus` maximum at the final write is **≤ 2.0** on L1 and
  **≤ 5.0** on L2 and L3 — the low-Re wall treatment of §4 requires it, and a level that
  does not have it is not running the model that was registered.

**Grid-convergence claim, registered now so it cannot be inflated later.** Three levels at
`r = 2` exist, so a Roache triple **is** computable on CL, CD and shock location, and it
will be computed and reported. **Rule 5 governs it: a triple that is not `CONVERGING` makes
the row `NOT A RESULT` whatever its value, and no GCI is quoted when the three values are
not monotone.** The **Cp band grading itself is per level and single-grid**, exactly as
`4c931d97c` fixes it — no observed order is implied for the Cp rows.

---

## 8. 🔴 THE SMOKE PREDICTION — registered BEFORE L3 runs, so it can fail

L3 (15,360 cells, 4 ranks, 3,000 iterations) is the smoke run. Predicted, now:

1. **Cost per iteration on L3 at 4 ranks lands in [0.010, 0.150] s.** (Projection: 0.032.)
2. **Maximum wing Cp at η = 0.65 lands in [0.85, 1.19].** The isentropic stagnation Cp at
   M = 0.8395 is **1.189**; a section carrying ~24 points around it cannot sit a node on
   the stagnation point, so the measured maximum should be **at or below** 1.189.
3. **Minimum upper-surface Cp at η = 0.65 lands in [−1.40, −0.60].**
4. **CL at `endTime` lands in [0.15, 0.40].** The M6 at this condition is ≈ 0.26–0.30; a
   15k-cell level is expected to miss, and the interval says how far a miss is tolerable
   before the chain itself is suspect.
5. **Sign check:** CL **positive** and the upper surface more suctioned than the lower at
   every station. A negative CL means α was applied with the wrong sign and **stops the
   case**; it is not corrected downstream.

A smoke that violates 1, 4 or 5 is a **defect in the chain**, reported as such and fixed
before L2 and L1 are read — not absorbed.

---

## 9. STOP RULES (Sanaa's, fixed, item 12–13)

- Residual **growth**, or any field outside bounds → **stop**.
- **Plateau with a stalled linear solver** → stop, and climb the ladder **mesh first, then
  numerics, then model**.
- **Coherent oscillation in the graded quantity** → mark **"physics voting unsteady"**.
- **One registered change per run.** Never the same action twice on the same state. **Two
  stops on the same cause → climb the ladder.** Ladder exhausted → park with the action
  history, write the lesson, next case.

---

## 10. THE GRADING PATH, AND WHAT IS NEW IN IT

1. `verification/runs/M6I_runs/extract_cp_m6i.py` — **new, frozen by this commit.**
   Cuts the reconstructed `wing` patch at `y = η × b` for the six registered stations and
   writes `cp_extracted.json` in the schema the frozen grader consumes. **Axes note, stated
   because it looks like a bug and is not:** M6I's span is **y** and its thickness is **z**,
   while the frozen grader splits upper/lower on a key literally named `"y"` which it
   documents as *"the y (thickness) coordinate"*. The extractor therefore writes the
   **vertical** coordinate into `"y"` and the span into `"y_span"`. **The grader is not
   edited to fit our axes; our axes are written into the contract it already froze.**
2. `scripts/grade_m6_agard_cp.py` at blob `e9d5c04b…`, **unchanged**, invoked as
   `grade_m6_agard_cp.py models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat
   <level>/cp_extracted.json <level>/log.rhoSimpleFoam <level>/m6i_grade.json`.
   Its planted control (§1) is the rule-3 control for this run; it is not re-implemented.
3. `verification/runs/M6I_runs/build_m6i_solve_chain.sh` and `launch_m6i.sh` — **new,
   frozen by this commit.** The launcher **asserts** the registered dictionary values
   (`rhoSimpleFoam`, `writeInterval 200`, `purgeWrite 2`, `SpalartAllmaras`,
   `transonic yes`) and refuses rather than rewriting any of them.

---

## 11. ON COMPLETION OF ANY LEVEL (Sanaa's ~20:30Z addendum)

A ParaView visualisation is saved **beside the run**, showing the **COARSE level's mesh**
(medium if coarse did not converge) with the **fields from the finest completed level
available at that time**, updated when a finer level lands. **Rendered as levels complete,
never batched.**

A rule-12 estimate-versus-actual row lands in `docs/COST_CALIBRATION.md` at each level's
completion: actual core-minutes from `CORE_MINUTES.txt`, the ratio actual/predicted against
§6's projection, and the gap attributed (contention / waste / misprediction), with waste
named separately and never absorbed into the ratio.

---

## 12. WHAT THIS DOCUMENT DOES NOT DO

1. **It does not lift the R0 mesh `GATE FAIL`.** That verdict stands; this runs anyway
   under Sanaa's two-tier ruling with quality disclosed.
2. **It does not change one character of `4c931d97c`.** No band, station, definition,
   precondition, plant or label moves.
3. **It claims no wall-interference correction on either side.** The reference is
   uncorrected (AR-138 §6.2); the CFD is free-air. A disclosed bias, not a removed one.
4. **It grades no force coefficient against experiment.** CL/CD/CM are computed, reported
   and used for IC-3 and the Roache triple only; AR-138 §6.1.2 is blank.
5. **No submission.** SUBMISSIONS ARE PARKED (rule 7).

## 13. FREEZE

This file, `extract_cp_m6i.py`, `build_m6i_solve_chain.sh` and `launch_m6i.sh` are
committed together. The grading path is fixed at that commit. **No solver output existed
when it was made.** Changes after first compute land only as dated addenda that cannot
alter a gate, threshold, cap or label (rule 2); originals are struck, never rewritten.

---

# ADDENDUM 1 — 2026-09-12, after the L3 smoke run and before any other compute

**v1.0 → v1.1. Lines whose number changed above this section: 0.** Nothing above is
edited. This addendum alters **no gate, no threshold, no cap and no label** (rule 2): the
14 bands, the six stations, the verdict rule, the preconditions, the planted control, the
iteration budgets, the cost estimates and the caps are all exactly as frozen at
`47537c99`. It records one crash, its proven mechanism, one live numerical change, and two
measurements that were taken after the freeze and that sharpen predictions rather than
move gates.

## A1.1 — THE SMOKE RAN AND DIED IN TWO SECONDS. That is what a smoke run is for.

`M6I-R1-L3` launched 2026-09-12T22:01:39Z, pid 33255, 4 ranks, and ended
`rc = 136` at 22:01:41Z. **Wall 2 s, 4 ranks, 0.13 core-minutes spent** against a 6.4
core-minute estimate and a 19.2 core-minute cap. Preserved whole, nothing deleted, at
`verification/runs/M6I_runs/L3/ATTEMPT1_FPE/` (the solve log, the launch record, the
decomposition, the staged `0/` and all four processor directories).

**Verdict on attempt 1: `NOT A RESULT`.** Signal 8, floating-point exception.

**What it got right before it died, and this is registered because it is evidence:**
- `decomposePar` rc = 0 into 4 subdomains; the patched mesh loaded; the launcher's
  dictionary assertions all passed.
- **Iteration 1 completed and produced a physically-signed answer: `Cl = 0.3710`,
  `Cd = 0.2401`.** 🔴 **The §8 sign check therefore PASSES: CL is positive, so α is
  applied with the correct sign.** That was the prediction most expensive to get wrong and
  it is now settled. (Cl = 0.371 at iteration 1 of a cold start is not a converged
  coefficient and is not offered as one.)
- All five equations solved at iteration 1 with initial residuals ≈ 1 and the p GAMG
  converging in 54 iterations — the linear algebra is sound.

**Where it died:** iteration 2, immediately after `Solving for e`, inside
`libfluidThermophysicalModels.so` — the temperature-from-energy inversion — on a pressure
field that had already left the physical range. Iteration 1 printed
**`pressureControl: p max 417018`**, i.e. **4.12 × freestream, with the limiter firing.**

## A1.2 — 🔴 THE MECHANISM, PROVEN FROM THE INSTALLED SOURCE, AND IT IS A DEAD LEVER

The frozen `fvSolution` carried `consistent yes` (SIMPLEC) and, *because* of it, pressure
relaxation 1.0. **`consistent` IS SILENTLY IGNORED BY `rhoSimpleFoam`.** Measured, not
assumed, from the installed tree:

| file | occurrences of `rAtU` or `consistent` |
|---|---|
| `applications/solvers/compressible/rhoSimpleFoam/pEqn.H` | **0** |
| `applications/solvers/incompressible/simpleFoam/pEqn.H` | **8** |

`src/finiteVolume/cfdTools/general/solutionControl/solutionControl.C:51` reads the keyword
(`consistent_ = solutionDict.getOrDefault("consistent", false)`) and stores it;
**`rhoSimpleFoam` never queries it.** The keyword is accepted, recorded, and does nothing.

**So attempt 1 ran plain SIMPLE with the pressure under-relaxation set to 1.0** — which is
not a SIMPLEC setting at all once the SIMPLEC branch does not exist, it is simply an
unrelaxed pressure. From a uniform cold start at M = 0.8395 with a body suddenly present,
the first pressure correction is violent; unrelaxed it reached 4.12 × freestream, and the
energy field built on it inverted to a non-physical temperature at iteration 2.

**This is `CLAUDE.md` rule 14's class: a lever that looks set and is not connected.** It is
recorded here rather than quietly deleted, because the dangerous half was never the dead
keyword — it was the *live* setting adopted on the strength of it.

## A1.3 — THE ONE REGISTERED CHANGE (stop rule 13: one change per run)

**`relaxationFactors.fields.p : 1 → 0.3`**, applied identically to L1, L2 and L3 so the
family stays similar. Read back on all three.

Everything else that moved is **dead-lever removal and changes no arithmetic**: the
`consistent yes` line, and `relaxationFactors.equations.p 1`, which SIMPLE does not read
either. **The live change is one line.** Schemes, model, mesh, condition, budgets, bands
and caps are untouched.

**If the next attempt stops on the same cause, that is two stops on one cause and the
ladder is climbed (mesh → numerics → model), per her item 13.** The pre-declared next rung
is numerics: a `potentialFoam` initialisation plus a `limitT` `fvOption` bounding T. It is
named here so it cannot be presented later as a fresh idea.

## A1.4 — 🔴 WHERE THE BAD FACES ARE. A MAXIMUM WAS THE WRONG STATISTIC.

§3 disclosed maxima of 86–88°. **A maximum is one face.** Counted and located from
`checkMesh -writeSets`' own output (`postProcessing/constant/{nonOrthoFaces,skewFaces}/`),
face centres computed from the written geometry:

| level | faces > 70° | **at η > 0.96 (outboard of the last graded station)** | on the graded span η ≤ 0.96 | **in the far field r ≥ 5** |
|---|---|---|---|---|
| L1 | 191,794 | **179,224 — 93.45 %** | 12,570 — 6.55 % | **0 — 0.00 %** |
| L2 | 24,774 | **22,216 — 89.67 %** | 2,558 — 10.33 % | **0 — 0.00 %** |
| L3 | 3,686 | **2,820 — 76.51 %** | 866 — 23.49 % | **0 — 0.00 %** |

**The median non-orthogonal face sits at η = 1.009 (L1), 1.008 (L2), 1.003 (L3) — beyond
the wing's own semispan**, out on the rounded tip cap, reaching η = 1.34. That is where the
generator's O-grid collapses its lines (R0 §6 measured 22,704 merged nodes on L1), and it
is **not** where Cp is graded.

Per graded station, faces within |Δη| < 0.02, **L1**:

| η | 0.20 | 0.44 | 0.65 | 0.80 | 0.90 | **0.96** |
|---|---|---|---|---|---|---|
| faces > 70° | 84 | 62 | **116** | 308 | 2,502 | **12,464** |

**Skewness, the statistic that looked worst and is the thinnest:** L1 has **4** skew faces
(all at η 0.86–0.95, all at |z| = 0.000 — the sharp trailing edge); **L2 has exactly ONE**,
at **η = 0.9983**, outboard of the last graded station; **L3 has none at all.** The
family's "non-monotone skewness" 5.11 / 8.30 / 2.78 is therefore **one tip face on L2
against four trailing-edge faces on L1** — a single-face statistic, not a bulk quality
inversion, and it is far weaker evidence against the family than the raw maxima suggested.

**🔴 PREDICTION REGISTERED NOW, BEFORE THE RERUN, AND IT CAN FAIL.** The mesh defect is
outboard. Therefore: **if the Cp bands miss, they miss at η = 0.96 first and η = 0.90
second, and a miss at η = 0.20, 0.44 or 0.65 CANNOT be attributed to mesh
non-orthogonality** — those stations carry 84, 62 and 116 bad faces out of 191,794, none
of them nearer than r = 0.29 to the root leading edge. **"The mesh is bad" is hereby
disallowed in advance as an explanation for an inboard miss.**

## A1.5 — `limited corrected 0.33` IS A NUMERICAL CHOICE WHOSE EFFECT IS UNMEASURED

§5 applies `limited corrected 0.33` to the Laplacian and surface-normal gradient. At 87°
this does not only stabilise: **ψ = 0.33 deliberately under-applies the non-orthogonal
correction, so the diffusion term is not second-order on exactly the faces that need it
most.** That bias lands on the boundary layer and therefore on shock position, which is 2
of the 14 bands. It is registered here as what it is: **a numerical choice with an
unmeasured effect on a graded quantity.**

**Registered sensitivity arm, before it is run: `M6I-R1-L3-PSI1`.** L3, identical in every
respect except **`limited corrected 1.0`** on `laplacianSchemes` and `snGradSchemes`.
Cost: one more L3, **6.4 core-minutes estimated, cap 19.2**. Reported: Cp at the six graded
stations from both runs, and `max |ΔCp|` and `ΔRMS` per station/surface, plus Δ(shock x/c)
at η = 0.65 and 0.90. **It is a SENSITIVITY, not a gate**: neither run's Cp is promoted or
demoted by the other, and the ψ = 0.33 run remains the registered one. **Predicted before
either is read: `max|ΔCp| ≤ 0.02` at η = 0.20/0.44/0.65 and `> 0.02` at η = 0.96**, on
A1.4's face distribution. It runs only after a level completes; it does not delay L2 or L1.

## A1.6 — RESIDUALS ARE READ AT THE OUTER ITERATION

`nNonOrthogonalCorrectors 2` gives **three** `GAMG: Solving for p` lines per outer
iteration (confirmed in attempt 1's own log: 0.999999999, then 5.53e-04, then 2.85e-05).
**IC-2's pressure residual is the FIRST of the three — the outer iteration's initial
residual — never the last.** Registered because this team has already mis-read the third
corrector as the iteration's residual and reported a value ~100× too good.

## A1.7 — THE ROACHE TRIPLE MAY NOT BE ABOUT DISCRETISATION, AND THAT IS REGISTERED NOW

The three levels are exact node subsets at `r = 2.000000`, so they differ by refinement.
**They also differ by quality, and not monotonically:** the fraction of faces over 70° runs
**23.49 % → 10.33 % → 6.55 %** (L3 → L2 → L1), falling but plateauing rather than
vanishing, and the maximum is flat at ≈ 87° across a 64× cell increase (R0 §4). An observed
order computed from these three levels therefore **mixes refinement with a changing defect
population, and may say nothing about discretisation at all.** Registered in advance as a
named reason the triple may come out non-`CONVERGING` — in which case, **rule 5: the row is
`NOT A RESULT` whatever its value, and no GCI is quoted.** The Cp band grading is per level
and single-grid regardless, exactly as `4c931d97c` fixes it.

## A1.8 — COST SO FAR

| item | core-min |
|---|---|
| L3 attempt 1 (FPE at iteration 2) — **waste, named separately, not absorbed** | **0.13** |
| solve-chain build, patching and `checkMesh` on three levels (1 rank) | see `COST_SOLVECHAIN.tsv` |

The rule-12 estimate-versus-actual row is owed to `docs/COST_CALIBRATION.md` at each
level's completion and is not written from a projection.

---

# ADDENDUM 2 — 2026-09-12, after the second L3 stop. **IT OPENS BY WITHDRAWING ADDENDUM 1's CENTRAL CLAIM.**

**v1.1 → v1.2. Lines whose number changed above this section: 0.** No gate, threshold, cap
or label moves. The 14 bands, six stations, verdict rule, preconditions, planted control,
iteration budgets, cost estimates and caps are exactly as frozen at `47537c99`.

## A2.1 — 🔴 ADDENDUM 1 SECTION A1.2 IS WRONG AND IS WITHDRAWN. A MEASUREMENT REFUTED IT, NOT AN ARGUMENT.

A1.2 asserted that `consistent` is *"silently ignored by `rhoSimpleFoam`"* — a dead lever —
and that `relaxationFactors.equations.p` is likewise unread. **Both halves are false, and
the error was mine.** The evidence for it was a grep of **one file**, `pEqn.H`, and one file
was not the program.

| A1.2 claimed | What the source actually says |
|---|---|
| `consistent` is dead in `rhoSimpleFoam` | **`rhoSimpleFoam.C:78`: `if (simple.consistent()) { #include "pcEqn.H" } else { #include "pEqn.H" }`.** `pcEqn.H` exists and carries **10** occurrences of `rAtU`. The lever selects an entirely different pressure equation and is **fully live**. |
| `equations.p` is unread by SIMPLE | **`pEqn.H:35-36`: `// Relax the pressure equation to ensure diagonal-dominance` / `pEqn.relax();`.** `fvMatrix::relax()` with no argument does **nothing at all** when no factor is registered for that field, and `relax(1.0)` is **not** a no-op — it sets `D = max(|D|, sumMagOffDiag)` *before* dividing by α. |

**The consequence was measured, and it is the reason this is a withdrawal rather than a
footnote.** Deleting `equations { p 1; }` stripped the diagonal-dominance enforcement that
the **transonic** pressure equation needs, because `fvm::div(phid, p)` is asymmetric:

| | pressure branch | `equations.p` | `fields.p` | **`pressureControl: p max`** | outcome |
|---|---|---|---|---|---|
| attempt 1 | **pcEqn.H (SIMPLEC)** | 1 | 1 | **417,018 Pa** | SIGFPE it. 2 |
| attempt 2 | **pEqn.H (SIMPLE)** | *absent* | 0.3 | **22,368,256 Pa** | SIGFPE it. 2 |

**The repair made it 54× worse**, against a freestream of 101,325 Pa. A1.3 predicted the
change would fix the crash; it did not, and the direction of the miss is what exposed the
wrong premise. Recorded in full because the seductive part was never the dead keyword — it
was how confident the inference sounded.

**What survives from A1.2:** nothing about `consistent`. **What survives from all of
ADDENDUM 1:** A1.1's finding that iteration 1 completes physically with **CL positive**
(the §8 sign check, still passed), and A1.4's face count and location, which were
measurements and are untouched by this.

## A2.2 — THE FAULT ITSELF, NOW PROVED RATHER THAN INFERRED

`sutherlandTransportI.H:120` — **`mu = As*sqrt(T)/(1.0 + Ts/T)`.** A **negative T** makes
`sqrt(T)` raise SIGFPE inside `libm`, which is **exactly** the frame sitting directly
beneath `libfluidThermophysicalModels` in both stack traces. T goes negative because the
energy equation is solved on a pressure field that has already left physics. **Both stops
have one cause and it is the transonic cold start, not the mesh and not the model.**

The trap firing is the instrument **working**: `FOAM_SIGFPE` turned what would otherwise
have been a NaN propagating quietly into a Cp we would later have graded into a crash at
iteration 2. Registered as a finding, not an annoyance.

## A2.3 — TWO STOPS ON ONE CAUSE → THE LADDER IS CLIMBED (her item 13). RUNG 3.

The rung is the one **pre-declared in A1.3 before either pressure number was known**, so it
cannot be presented as a fresh idea. Built by
`verification/runs/M6I_runs/build_m6i_rung3.sh`, applied **identically to L1, L2 and L3**:

1. **`relaxationFactors.equations.p 1` RESTORED** — the diagonal-dominance relaxation
   `pEqn.H:36` asks for by name. A correction of A2.1's error, not a new lever.
   `consistent` stays **absent**: attempt 1 ran correct SIMPLEC and crashed anyway, so
   SIMPLEC is neither the fault nor the fix.
2. **THE THERMO IS BOUNDED.** `constant/fvOptions` on every level:
   `limitTemperature`, `selectionMode all`, **`min 100`, `max 1500` K**. A startup
   excursion now **clips** instead of **faulting**. The window is **wide on purpose**: at
   M = 0.8395 with T∞ = 300 K the stagnation temperature is **342 K**, so [100, 1500]
   cannot clip any physical state this case can reach — **a clip therefore MEANS the
   solution left physics**, and is evidence rather than a silent rescue.
3. **A 200-ITERATION FIRST-ORDER STARTUP RAMP**, then the registered second-order schemes.
   Sanaa's CRM instruction §6 prescribes a robust-startup ramp for exactly this solver
   class. `system/fvSchemes.startup` puts every convective term on `bounded Gauss upwind`;
   `system/fvSolution.startup` tightens relaxation to p 0.2 / U 0.5 / e 0.5 / ν̃ 0.5.

**🔴 THE NON-ORTHOGONALITY TREATMENT IS NOT TOUCHED.** `limited corrected 0.33` is
byte-identical in the startup and registered schemes. It survived iteration 1 intact in
both attempts, so changing it now would be a change made **against** the evidence.

**`launch_m6i_v2.sh`** runs the two stages. It is a **new file, not an edit of v1** —
precondition checked before writing, `pgrep -x rhoSimpleFoam` returned **0** live solvers.
It keeps `system/controlDict.registered` pristine, moves `endTime` **only** between the two
stages, and asserts the restored `fvSchemes`, `fvSolution` and `controlDict` **md5-identical
to the registered ones** before stage 2 begins. **THE GRADED ANSWER IS PRODUCED BY THE
REGISTERED SECOND-ORDER SCHEMES**, from iteration 201 to `endTime`; the ramp only removes
the cold-start pressure pulse. Total iterations are unchanged: 200 + (endTime − 200).

## A2.4 — IC-5, A NEW CONVERGENCE LIMB THAT ONLY EVER TIGHTENS

Added because rung 3 introduces a limiter, and an unwatched limiter is how a bounded
solution passes for a converged one:

- **IC-5** — over the **last 600 iterations** (absolute, never a fraction of `endTime`), the
  `limitTemperature` fvOption must report **ZERO** clipping events. A level still clipping
  at the end is **`NOT A RESULT`**, and `endTime` is never extended to outrun it.

IC-1 to IC-4 are unchanged. IC-5 can only make a verdict worse, never better.

## A2.5 — 🔴 PREDICTIONS FOR ATTEMPT 3, REGISTERED BEFORE IT RUNS

1. **Stage 1 completes 200 iterations with rc = 0 and no SIGFPE.**
2. **`pressureControl: p max` stays below 5 × 10⁵ Pa at every iteration of stage 1** —
   i.e. under 5 × freestream, against 4.12× and 221× on the two failed attempts.
3. **Iteration 1's Cd reproduces 0.2400 ± 0.03 and Cl reproduces 0.3710 ± 0.05.** Stage 1's
   first iteration differs from attempt 1's only in relaxation and in first-order
   convection, and iteration 1 from a uniform field is dominated by neither.
4. **`limitTemperature` clips on fewer than 20 of the 200 startup iterations, and on none
   of the last 600 iterations of stage 2** (IC-5).

**A third stop on the same cause exhausts this rung.** The next and last numerics rung is
named here in advance: a `potentialFoam` initialisation of U and φ before iteration 1.
After that the ladder is exhausted and the case is **parked with its action history and a
lesson filed**, per her item 13.

## A2.6 — COST

| item | core-min | note |
|---|---|---|
| L3 attempt 1 — SIGFPE | 0.13 | **waste, named separately, never absorbed** |
| L3 attempt 2 — SIGFPE | 0.13 | **waste, named separately, never absorbed** |
| **total waste so far** | **0.26** | against L3's 6.4 core-minute estimate and 19.2 cap |

Both attempts are preserved whole and undeleted at
`verification/runs/M6I_runs/L3/ATTEMPT1_FPE/` and `ATTEMPT2_FPE/`. **Two dead smoke runs
cost 0.26 core-minutes. The same two stack traces on L1 would have cost 1,092.** Holding L2
and L1 in `held/` is what that number bought.

---

# ADDENDUM 3 — 2026-09-12, WRITTEN WHILE L2 AND L1 ARE STILL RUNNING AND BEFORE EITHER HAS PRODUCED A Cp

**v1.2 → v1.3. Lines whose number changed above this section: 0.** No gate, threshold, cap
or label above moves. Two of the three items below **tighten** what may be claimed; the
third is a correction of something this lane stated and got wrong.

**Timing, stated so it can be checked rather than believed.** At the moment of writing, L1
is at ramp iteration ~10 of 200 and L2 at stage-2 iteration ~500 of 4,800. **Neither has
written a `cp_extracted.json`, neither has been graded, and no Cp, shock location or
observed order exists for either level.** `verification/runs/M6I_runs/{L1,L2}/RC.txt` do
not exist. §7's Roache clause is therefore being tightened **before** the numbers it governs
can exist, which is the entire point of doing it now.

## A3.1 — 🔴 WHEN THE THREE LEVELS ARE NOT THREE DISCRETISATIONS OF ONE SOLUTION

§7 registered that quality varies across the family and that the triple may come out
non-`CONVERGING`. **L3's result exposes a deeper failure mode that §7 does not cover**, and
it is registered here before L2's or L1's numbers exist.

L3 produced **no shock at all**: the grader's own `cfd_cp_rise_at_shock` was **0.087** at
η = 0.65 against the experiment's **0.424**, and **0.053** at η = 0.90 against **0.640** —
so D1 honestly selected the **trailing-edge recovery** at x/c **0.953** and **0.923** as the
largest Cp rise available. If L3 carries no shock, L2 a weak one and L1 a resolved one,
**the three levels are not three discretisations of the same solution — they are
qualitatively different flows.** Richardson extrapolation across a qualitative change has
no asymptotic range to extrapolate in, and a monotone set of three numbers would still not
mean what an observed order implies. Rule 5 forbids a GCI on non-monotone values; **this is
the stronger case, where even monotone values would not license one.**

### THE ADMISSIBILITY CONDITION, FIXED NOW

A level is **shock-bearing** at a station when **both** limbs hold, and both are keyed to the
experiment or to geometry so that **no CFD value can move either**:

- **S1 — strength.** `cfd_cp_rise_at_shock` ≥ **0.50 ×** the experimental `exp_cp_rise_at_shock`
  at that station. Numerically, from the reference and nothing else:
  **≥ 0.212 at η = 0.65** and **≥ 0.320 at η = 0.90**.
- **S2 — location.** `x_shock_cfd` < **0.85 c**. The trailing-edge recovery on this geometry
  sits aft of x/c ≈ 0.90; a "shock" located there is the trailing edge, not a shock.

**A level is shock-bearing only if S1 and S2 hold at BOTH η = 0.65 and η = 0.90.**

### WHAT FOLLOWS, FIXED NOW

1. **All three levels shock-bearing** → the three-level Roache triple is computed and rule 5
   governs it in the ordinary way.
2. **Fewer than three shock-bearing** → **NO THREE-LEVEL OBSERVED ORDER AND NO GCI IS
   COMPUTED, QUOTED OR IMPLIED.** The comparison between the shock-bearing levels is
   reported as a **two-level difference with no order claimed**, labelled on its face
   *"TWO LEVELS, NO ASYMPTOTIC RANGE DEMONSTRATED"*. A three-level order is then obtainable
   only by adding a **successor level** — a fourth grid finer than L1, or an intermediate —
   and that is a new registration, not a re-reading of this one.
3. **No level shock-bearing** → the family says nothing about shock location at all, and the
   Q2 rows are reported as `GATE FAIL` per level with the absence of a shock named as the
   reason.

### 🔴 THE HONESTY LIMB THIS RULE NEEDS, AND IT IS AGAINST THIS LANE

**L3's two numbers were already in hand when this rule was written.** 0.087 and 0.053 fail
S1 by a factor of 2.4 and 6.0, and 0.953 and 0.923 fail S2. **So for L3 this rule is
post-hoc and carries no evidentiary weight, and this document says so rather than letting
the freeze date imply otherwise.** Its weight is over **L2 and L1, whose values do not yet
exist** — which is exactly where it will decide whether a three-level order may be quoted.
The thresholds were chosen from the **experiment's** rises and from the geometry of the
trailing edge, not from any CFD number, so there was nothing about L3 available to tune them
to beyond the fact — already obvious from `cp_rise 0.087` — that L3 has no shock.

## A3.2 — 🔴 CORRECTION: THE TEMPERATURE BOUND IS BELT-AND-BRACES ON L3 AND LOAD-BEARING ON L2

ADDENDUM 2 and the L2/L1 queue entries state that the `limitTemperature` bound "did almost
no work" and is a safety net rather than the mechanism. **That is true of L3 and it is FALSE
of L2**, and this lane asserted it of the family on one level's evidence — the same error
shape as A2.1, one level standing in for the program.

Counted from each level's own stage-2 log:

| level | stage-2 iterations with a **lower**-bound clip | largest single event | `UnlimitedTmin` when clipping |
|---|---|---|---|
| **L3** | **0 of 2,800** | — | 214.8 K (never reached the floor) |
| **L2** | **88 of the first 226** | **37 cells** | pinned at **100 K** |

**On L2 the bound fires on roughly 39 % of iterations and the unlimited minimum sits ON the
floor.** Without it L2 would have met `sqrt(T)` with T ≤ 0 — the A2.2 fault — and would have
died exactly as attempts 1 and 2 did. **The ramp is still the mechanism that survives the
cold start; the bound is what is keeping L2 alive after it.** Both statements are now on the
record with the numbers that separate them.

**This makes IC-5 a live gate on L2 rather than a formality**, and IC-5 is unchanged: zero
clipping events over the last 600 iterations, or the level is **`NOT A RESULT`**, and
`endTime` is never extended to outrun it. A level held inside physics by a limiter for its
whole run has not converged to a solution of the registered equations.

## A3.3 — A REGISTERED PREDICTION HAS ALREADY FAILED, ON L2

A2.5 prediction 2 registered that `pressureControl: p max` would stay **below 5 × 10⁵ Pa**
throughout the ramp. Measured peaks over the 200-iteration ramp:

| level | ramp peak `p max` | × freestream | prediction 2 |
|---|---|---|---|
| L3 | 310,008 Pa | 3.06 | **PASS** |
| L1 | 306,703 Pa (first 10 iterations; ramp incomplete at writing) | 3.03 | pending |
| **L2** | **556,924 Pa** | **5.50** | 🔴 **FAIL** |

L2 exceeded the registered bound by 11 % and **did not crash**, which is a second reason the
temperature bound is load-bearing there. The prediction is recorded as failed rather than
widened.

## A3.4 — A FALSE POSITIVE FROM THIS LANE'S OWN MONITOR, RECORDED BECAUSE IT NEARLY BECAME A REPORT

A background monitor watching L2 and L1 reported **`FPE-DETECTED`** three times while both
runs were healthy and advancing. The cause: it matched the string `Floating point exception`
against the solver log, and **line 29 of every healthy OpenFOAM log reads
`trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`** The monitor was
matching the banner that says the trap is **armed**, not a trap that **fired**.

Checked before anything was reported upward: `rc.stage1` = 0, no `RC.txt`, and
`Time = 426` still advancing with eight live `rhoSimpleFoam` processes. The filter is
corrected to `exited on signal|sigFpe::sigHandler|FOAM FATAL`. **A watcher keyed on a string
that appears in every healthy log is a watcher that cries wolf, and one that had been
believed would have parked two live runs.**

---

# ADDENDUM 4 — 2026-09-12, L2's VERDICT AND A COST FINDING ON L1 WHILE IT RUNS

**v1.3 → v1.4. Lines whose number changed above this section: 0.** No gate, threshold, cap
or label moves.

## A4.1 — 🔴 L2: **`NOT A RESULT`.** IT DIVERGED, AND A3.2 SAW IT COMING ONE PARAGRAPH EARLY.

`M6I-R1-L2`, pid 48134, launched 22:19:03Z, **rc = 136**, SIGFPE at global iteration **668**
(stage-2 iteration 468). The 200-iteration ramp completed cleanly, `rc.stage1 = 0`.

**It is a DIVERGENCE, not a startup fault, and the clip counter is the instrument that
shows it.** Lower-bound temperature clips per stage-2 iteration:

| stage-2 iteration | 1 | 51 | 101 | 151 | 201 | 251 | 301 | **351** | **401** | **451** |
|---|---|---|---|---|---|---|---|---|---|---|
| cells clipped | 0 | 4 | 18 | 1 | 1 | 0 | 0 | **1,083** | **35,355** | **42,936** |

**42,936 of 122,880 cells — 35 % of the domain — pinned at the 100 K floor.** Force
coefficients reached **10⁴²** and the momentum residuals returned to **0.873**, i.e. the
initial-iteration value. The solution left physics between stage-2 iterations 301 and 351,
after **three hundred healthy iterations**, and the temperature bound held it up for another
hundred before the fault. **This is Sanaa's "residual growth or a field outside bounds →
stop", and it stopped itself.**

**Verdict: `NOT A RESULT`** — IC-1 fails (SIGFPE), IC-2 fails (final residuals ≈ 0.87),
IC-5 fails comprehensively. **No Cp was extracted and none will be**: `rc.extract_cp` does
not exist, `cp_extracted.json` does not exist, and the grader was never run on this level.
**No number from L2 is quoted anywhere, because there is none.**

**A3.2 is vindicated within the hour.** It recorded — before this crash — that the
temperature bound was "load-bearing on L2", firing on 39 % of its iterations with
`UnlimitedTmin` pinned at the floor, and that IC-5 was therefore "a live gate on L2 rather
than a formality". A level held inside physics by a limiter had not converged to a solution
of the registered equations, and 120 iterations later it stopped pretending to.

**NO REPAIR IS REGISTERED FOR L2 YET, DELIBERATELY.** This is L2's **first** stop and its
cause differs from L3's (a cold-start fault at iteration 2 versus a mid-run divergence at
iteration 550+). **L1 is running at this moment on identical settings and is the evidence
that says whether this cause is shared.** Guessing L2's remedy now would spend one of its
two stops on a guess while the measurement that names the remedy is still being taken.
The candidates are named here so the later choice cannot be presented as fresh: tighter
momentum and energy relaxation; or a limited (TVD) convection scheme in place of
`linearUpwind` on the registered second-order pass.

**Cost:** L2 ran 668 iterations at 4 ranks before stopping. **Waste, named separately and
never absorbed.** Against its 85.3 core-minute estimate and 256 core-minute cap.

## A4.2 — 🔴 L1's ITERATION RATE IS 2.7× THE PROJECTION, AND BOTH CONSEQUENCES ARE REGISTERED NOW

Measured from L1's own ramp log, **195.49 s of `ExecutionTime` over 35 iterations at 4
ranks = 5.585 s/iteration**, against §6's registered **projection of 2.05 s/iteration**.
**The projection is out by 2.7×** and it was labelled a projection, not a measurement,
precisely so this could be said plainly. (Measured while L2 was running concurrently on the
same box; L2 has since stopped, so the figure may improve and will be re-measured.)

**Consequence 1 — cost.** 8,000 iterations at 5.585 s is **12.4 h wall and 2,979
core-minutes**, against a registered estimate of **1,092.3** and a registered cap of
**3,277**. **Inside the cap, by 9 %.** If the rate degrades further the cap is crossed, and
what follows is already fixed and is not being decided now: **the row grades `NOT A RESULT`
on cost, the cap is never raised, and NOTHING IS KILLED** (Sanaa's directive #17 with her
item 7). `launch_m6i_v2.sh` contains no clock check and no spend check.

**Consequence 2 — the checkpoint bound, which has narrowed and still holds.** At 5.585
s/iteration, `writeInterval 200` is **1,117 s = 18.6 minutes** against Sanaa's 30-minute
bound. It holds **by 1.6×**, where L3's measured rate held it by **330×**. The margin is now
real rather than enormous, and it is recorded here rather than left as an inference from
L3's number. **No change is made**: 18.6 < 30.

## A4.3 — WHERE THE FAMILY STANDS

| level | state | verdict |
|---|---|---|
| **L3** 15,360 cells | complete, rc = 0, 3,000/3,000, converged, graded | **`GATE FAIL`** — and it is a verdict about a 15,360-cell grid carrying **no shock at all**, not about the M6 or about the method |
| **L2** 122,880 cells | stopped, rc = 136, diverged at iteration 668 | **`NOT A RESULT`** — no Cp extracted, none quoted |
| **L1** 983,040 cells | running | **`PENDING`** |

Under **A3.1** this already matters: L3 is **not shock-bearing** (S1 fails by 2.4× and 6.0×,
S2 fails at x/c 0.953 and 0.923) and L2 produced nothing. **Fewer than three shock-bearing
levels, so NO THREE-LEVEL OBSERVED ORDER AND NO GCI MAY BE COMPUTED, QUOTED OR IMPLIED** for
this family as it stands. That rule was registered while L2 and L1 held no Cp at all.

---

# ADDENDUM 5 — 2026-09-12, **A BOUND ADDED TO SURVIVE A TRANSIENT BLINDED A STOP RULE.** Registered while L1 sits at stage-2 iteration 6.

**v1.4 → v1.5. Lines whose number changed above this section: 0.** No band, threshold, cap
or label above moves. Everything below **adds a way to fail** and removes none.

**Timing, checkable rather than believed.** L1 completed its 200-iteration ramp with
`rc.stage1 = 0` and is at **stage-2 iteration 6** of 7,800. Its worst temperature clip so
far is **7 cells of 983,040 at the ceiling (0.0007 %)** and **365 at the floor (0.037 %)**,
with **zero** `bounding nuTilda` events and a Ux initial residual of **2.62e-04**. **The
threshold registered in §A5.2 is more than fifty times above anything L1 has yet produced,
and L1 has 7,794 iterations left in which to cross it.**

## A5.1 — 🔴 WHAT ACTUALLY KILLED L2, AND WHY IT TOOK 668 ITERATIONS TO SHOW

ADDENDUM 4 read L2's failure off the **lower**-bound clip counter and called it a
divergence. That was right and it was not the half that matters. Measured by this lane from
L2's own log:

| quantity | value at/near the end |
|---|---|
| `bounding nuTilda` events | 2, the last **`min -1.302e+36  max 3.078e+43`** |
| `pressureControl: p max` (pre-clip) | **265,998,746 Pa — 2,625 × freestream** |
| `limitTemperature` **upper** clip, peak | **122,535 cells of 122,880 — 99.72 % of the domain** |
| last reported limit line | `Type=Upper, LimitedCells=120197, CellsPercent=97.82, Tmax=1500, UnlimitedTmax=1500` |
| Ux initial residual at iteration 668 | 0.873 — the **first-iteration** value |

**The Spalart–Allmaras working variable reached 10⁴³.** This is a **turbulence-variable
divergence**, and it is a **different failure from L3's cold-start fault** — the ramp worked
on L2, cleanly, and the run then destroyed itself 300 iterations into the registered
second-order pass.

### 🔴 AND HERE IS THE PART THAT IS NOT ABOUT M6 AT ALL

Sanaa's stop rule (item 12) is **"residual growth or a field outside bounds → stop"**.
**With `limitTemperature` active, the temperature field was NEVER outside bounds.** It was
held *at* the bound — 97.8 % of it — while the solution destroyed itself. **The
field-out-of-bounds trigger could not fire**, and the run burned **668 iterations** until an
FPE finally stopped it by accident rather than by design.

**A BOUND ADDED TO SURVIVE A STARTUP TRANSIENT SILENTLY CONVERTED A DIVERGENCE DETECTOR INTO
A DIVERGENCE CONCEALER.** Every bounding `fvOption` — `limitTemperature`, `limitVelocity`,
`limitPressure`, and OpenFOAM's own built-in `bounding` of `k`, `omega` and `nuTilda` — has
this property. **This lane added the bound and this lane is recording the cost of it.**

**The repair is a MONITOR, NOT A REMOVAL.** Removing the bound would restore the stop rule
by restoring the crash, which is worse. A limiter doing no work is a safety net; a limiter
pinning a tenth of the domain **is the divergence**, observable a hundred iterations before
the fault.

## A5.2 — 🔴 **LC-1**, A NEW STOP RULE AND GRADING LIMB. IT ONLY EVER TIGHTENS.

**LC-1 — bound-concealed divergence.** If either `limitTemperature` bound reports
**`CellsPercent` > 2.0** on **20 consecutive reported iterations**, the level is
**`NOT A RESULT`**, labelled **`BOUND-CONCEALED DIVERGENCE`**, and the run is **stopped**
under Sanaa's item 12 — a **stop rule**, which she instructs, and **not** a cap, which never
kills anything.

**Why 2.0 %, and the honest limb.** L3's peak was **0 %** over 2,800 iterations; L1's peak
so far is **0.037 %**; L2 crossed 2 % on its way to **99.72 %** and did so **well before**
the FPE. **2.0 % is ~54× above the worst any healthy level here has produced and is crossed
early on the death trajectory.** 🔴 **L2's numbers were in hand when this threshold was
chosen, so for L2 it is post-hoc and carries no evidentiary weight — and L2 is already
`NOT A RESULT` on IC-1, IC-2 and IC-5, so LC-1 cannot change its verdict either way. Its
weight is over L1**, which is 54× below it with 7,794 iterations still to run.

**LC-2 — the turbulence variable is watched directly, not through the thermo.** Any
`bounding nuTilda` line in a level's stage-2 log with `max > 1e6` (freestream ν̃ is
5.99e-05, so this is 10¹¹ × freestream) makes the level **`NOT A RESULT`**. L2 reached
3.08e43; L1 has **zero** such lines.

**Monitoring, so the rule is readable while a run is live and not only at its post-mortem:**
`scripts/monitor_m6i_bounds.sh` reports, per level, the per-iteration
`Type=Upper`/`Type=Lower` `CellsPercent`, the count of consecutive iterations above 2.0 %,
and any `bounding nuTilda` line. It **reads logs and writes a report; it launches nothing
and kills nothing.**

**And it is said to the fleet, because it is not M6-shaped:** *anyone who adds
`limitTemperature`, `limitVelocity` or any bounding `fvOption` to get past a transient has,
in the same act, blinded the field-out-of-bounds stop rule that would have caught what comes
next.* Heat-transfer and dafoam both run bounded solvers.

## A5.3 — 🔴 IF ONLY L1 SURVIVES, THERE IS NO FAMILY, AND WHAT IS REPORTED IS FIXED NOW

A3.1 covered *fewer than three shock-bearing levels*. The live case is sharper: **L3 is
`GATE FAIL` and not shock-bearing; L2 is `NOT A RESULT` and produced no Cp at all; L1 may
converge.** That is **one level**, not a family.

**Registered now, before L1 has a Cp:** if L1 is the only level with a result, it is reported
as a **DISCLOSED SINGLE-LEVEL VALIDATION COMPARISON** — which is exactly how `4c931d97c`
frames its own primal, *"single grid, band taken from the reference"*. Then:

- **NO observed order, NO GCI, NO family band, and NO Roache triple** is computed, quoted or
  implied. Rule 5 is not invoked; there is nothing for it to gate.
- **Every row, figure and certificate slot carries `ONE LEVEL — NO GRID FAMILY` on its
  face**, beside the disclosures `4c931d97c` §9 already requires.
- The available verdicts are **`PASS` / `GATE FAIL` / `NOT A RESULT`** against the 14 frozen
  bands, per station, on that one grid. **A `PASS` here is a pass on one grid and says so.**
- A family verdict becomes available only by adding a **successor level** under a **new
  registration** — never by re-reading this one.

**A triple will not be assembled from a level with no shock, a level with no result, and a
level with a shock.** That sentence is registered before the third of those exists.

## A5.4 — L2's ONE REGISTERED CHANGE, AND THE RUNG IT SITS ON

L2's stop is its **first**, and its cause (turbulence-variable divergence at iteration 550+)
is **not** L3's (cold-start thermo fault at iteration 2). **The ramp is not reached for
again — it worked.** Ladder position: **numerics**, rung 1 of 2 before the model rung.

**THE ONE CHANGE: L2's SIMPLE relaxation set is tightened to the conservative transonic
set** — `fields { p 0.15; rho 0.02; }`, `equations { p 1; U 0.4; e 0.4; nuTilda 0.3; }` —
from p 0.3 / U 0.7 / e 0.7 / ν̃ 0.7. One named package, one purpose: damp the growth that
reached ν̃ = 10⁴³. `equations.p 1` is untouched (A2.1's lesson).

**Pre-declared rung 2, so it cannot later be presented as fresh:** `div(phi,nuTilda)` and
`div(phi,U)` moved to a limited TVD scheme (`limitedLinear 1`) on the second-order pass, and
the ramp lengthened from 200 to 1,000 iterations. **Rung 3 is the model rung:** SA-neg
(`SpalartAllmarasNeg`), whose entire purpose is tolerating the negative ν̃ excursion L2
produced — `min -1.302e+36`.

### 🔴 THE COST OF THIS CHANGE, WHICH IS A REAL ONE AND IS NOT HIDDEN

§3 and the build script promise **one script, all levels identically configured, so the
family stays similar**. **This change breaks that: L2 would run a relaxation set L1 and L3
did not.** The defence, and its limit, stated plainly: **under-relaxation affects the path
to the steady state and not the steady state itself** — the converged solution satisfies the
same discrete equations either way — **so a converged L2 is the same discretisation
regardless.** That argument holds **only if L2 converges**, and it is void if L2 is again
`NOT A RESULT`. **L1 IS NOT TOUCHED. IT IS RUNNING AND ITS DICTIONARIES ARE NOT EDITED
WHILE IT RUNS**, which is also this team's standing rule about live files.

**Hypothesis, registered as a hypothesis and NOT asserted:** L2 at 122,880 cells may sit in
the worst available regime — **fine enough to begin forming a shock and too coarse to
resolve it** — so the shock oscillates and drives ν̃ unstable, while L3 (no shock at all) and
L1 (a resolved shock) are both stable. **It is consistent with all three observations and is
not tested by any of them.** The test that would settle it is an intermediate level between
L2 and L1, which is not registered and is not being run.

---

# ADDENDUM 6 — 2026-09-12. **ALL THREE LEVELS ARE DOWN. THE RAMP IS A SUPPRESSANT, NOT A CURE, AND HERE IS THE EXPERIMENT THAT DECIDES IT.**

**v1.5 → v1.6. Lines whose number changed above this section: 0.** No band, threshold, cap
or label above moves.

## A6.1 — L1: **`NOT A RESULT`**. AND THE THREE LEVELS TOGETHER NAME ONE MECHANISM.

`M6I-R1-L1`, pid 50082, launched 22:20:08Z, **rc = 136**, SIGFPE at global iteration **296**.
Preserved whole and undeleted at `verification/runs/M6I_runs/L1/ATTEMPT1_DIVERGED/`.

**Read the STAGE, not the iteration:**

| level | stage 1 (first-order ramp, 200 it) | stage 2 (REGISTERED second-order) | outcome |
|---|---|---|---|
| **L1** 983,040 cells | **clean, `rc.stage1 = 0`** | 96 iterations, 200 → 296 | **SIGFPE** |
| **L2** 122,880 cells | **clean, `rc.stage1 = 0`** | 468 iterations, 200 → 668 | **SIGFPE** |
| **L3** 15,360 cells | clean | **2,800 iterations, completed** | rc = 0 — **and it is the level whose flow never formed a shock** |

🔴 **NEITHER L1 NOR L2 EVER DIED IN STAGE 1. BOTH DIED IN STAGE 2, WHICH IS WHERE THE
REGISTERED SECOND-ORDER SCHEMES COME BACK.** ADDENDUM 2 credited the ramp as the causal fix
for the crash, and it was — **but a fix that holds only while it is applied is a suppressant,
not a cure.** The instability reappears the moment the ramp lifts.

Measured on L1, and the trajectory is the same shape as L2's:
`limitTemperature` upper-bound `CellsPercent` over stage 2 ran **0 → 0.21 → 3.71 → 13.85 →
39.67 → 57.68 → 84.72 → 95.78 → 100.00**; `bounding nuTilda` reached
**`min -2.909e+08  max 3.635e+44`**; `pressureControl: p max` reached **2.33e+09 Pa**
— 23,000 × freestream.

**`LC-1` and `LC-2`, registered in ADDENDUM 5 while L1 sat at stage-2 iteration 6 with
0.037 % clipped and zero `nuTilda` bounding events, both fired on L1 before it faulted.**
LC-2 was breached at `max 3.635e+44` against its 1e6 threshold. **The instrument registered
twenty minutes earlier caught the thing it was registered for.**

## A6.2 — 🔴 THE MODEL RUNG IS CLOSED BEFORE IT IS REACHED, AND THAT IS A MEASUREMENT

ADDENDUM 5 §A5.4 pre-declared **SA-neg (`SpalartAllmarasNeg`)** as the model rung, because
ν̃ going negative (`min -2.909e+08` on L1, `-1.302e+36` on L2) is exactly what SA-neg exists
to tolerate. **It is not available.** Enumerated from the installed tree
`/usr/lib/openfoam/openfoam2606/src/TurbulenceModels`, the shipped Spalart–Allmaras variants
are **`SpalartAllmaras`, `SpalartAllmarasBase`, `SpalartAllmarasDES`, `SpalartAllmarasDDES`,
`SpalartAllmarasIDDES`** — **there is no negative variant, and a search for
`SpalartAllmarasNeg` across the whole turbulence-model source returns nothing.**

The shipped model's only protection against a negative ν̃ is OpenFOAM's own
`bounding nuTilda` clip — **which is the §A5.1 concealment defect one level deeper:** a clip
that keeps the variable nominally in range while the solution destroys itself. **The rung
that is written in the pre-declaration is not on this box**, and implementing SA-neg is a
solver-development task, not a run.

## A6.3 — 🔴 THE DISCRIMINATING EXPERIMENT: `M6I-R1-L3-NORAMP`. BOTH OUTCOMES NAMED BEFORE IT RUNS.

**Two readings of the same three results are on the table and they disagree.** Registering
which is which **before** the run is the whole value of it.

- **READING A (the cfd supervisor's).** `div(phi,U) bounded Gauss linearUpwind limitedGrad`
  on a grid at 87.7° maximum non-orthogonality, under `laplacian ... limited corrected 0.33`,
  is unstable **as such**: the limiter under-applies the non-orthogonal correction on exactly
  the faces whose gradients `linearUpwind` then reconstructs. **Shock or no shock.**
- **READING B (this lane's).** The instability needs **a shock**. An unbounded second-order
  upwind scheme overshoots across a captured shock; the overshoot drives T and ν̃ negative.
  L3 never formed a shock (`cfd_cp_rise_at_shock` 0.087 against 0.424) and L3 is the level
  that survived 2,800 second-order iterations with **zero** clips and **zero** ν̃ boundings.

**THE EXPERIMENT.** `verification/runs/M6I_runs/L3_NORAMP` — L3's mesh, dictionaries, `0.orig`
and `fvOptions`, copied, with **`fvSchemes.startup` and `fvSolution.startup` made identical
to the registered ones** (the fvSolution byte-identical; the fvSchemes identical below a
truthful banner). The launcher is **not modified**: its two stages simply carry one
configuration split at a checkpoint, which changes no arithmetic. **The result is the
registered second-order schemes and the registered relaxation, from iteration 1, with no
ramp.** 3,000 iterations, 4 ranks, **6.4 core-minutes estimated, cap 19.2**.

**THE PREDICTIONS, FIXED NOW:**

| outcome | what it convicts |
|---|---|
| **L3_NORAMP DIES** — SIGFPE, or LC-2 (`bounding nuTilda` max > 1e6), or LC-1 (>2 % clipped for 20 consecutive reported iterations) | **READING A.** The registered schemes are unstable on this grid *as such*, the ramp's role is proven to be suppression, and **that is a result about the imported grid and is reported as one, not engineered around** (Sanaa 2026-09-10: OpenFOAM issues are surfaced as runs, not worked around). |
| **L3_NORAMP COMPLETES** rc = 0 to 3,000 with zero ν̃ boundings and peak `CellsPercent` < 2 % | **READING B.** The instability requires a shock, L3 has none, and the story is about what L1 and L2's grids do once a shock forms. |

**🔴 THIS LANE'S PREDICTION, REGISTERED AGAINST ITS OWN SUPERVISOR'S: READING B.
L3_NORAMP COMPLETES.** If it dies, this lane was wrong and the supervisor was right, and the
record will say so in those words.

**A second limb, free with the same run:** if it completes, its Cp at the six stations must
match the ramped L3's to **max|ΔCp| ≤ 0.01** at every station — because a converged solution
of the same discrete equations cannot depend on the path taken to it. **A larger difference
would mean the ramped L3 was not converged**, and would put L3's `GATE FAIL` itself in
question. That is a way for the completed level to lose its verdict, registered before the
comparison exists.

## A6.4 — WHAT IS **NOT** DONE, NAMED SO IT CANNOT BE SLID IN LATER

🔴 **THE RAMP IS NOT EXTENDED TO COVER THE WHOLE RUN.** A solution obtained on first-order
convection **is a first-order solution**, first-order **smears a shock**, and a smeared shock
is precisely what 2 of the 14 bands measure. **Grading a first-order solution against the
frozen bands without saying so is the worst outcome available here**, and it is barred by
this section rather than left to judgement.

**No change is made to any level's numerics under this addendum.** L3_NORAMP changes nothing:
it *removes* the ramp in order to measure what the ramp was doing. The one registered
numerics change follows the experiment, not this addendum, and §A5.4's pre-declared
candidates stand: a TVD-limited convection scheme for the whole run, or a longer ramp — **and
§A5.4's ordering may be revised on this experiment's evidence, which is a choice that will be
registered with its reason rather than made quietly.**

## A6.5 — THE FAMILY, STATED PLAINLY

**One completed level. No triple. No prospect of one without the numerics rung.**

| level | verdict |
|---|---|
| L3 | **`GATE FAIL`** — converged, admissible, planted control seen; a verdict about a 15,360-cell grid carrying **no shock at all** |
| L2 | **`NOT A RESULT`** — diverged, no Cp extracted, none quoted |
| L1 | **`NOT A RESULT`** — diverged, no Cp extracted, none quoted |

**§A5.3's single-level disclosure is therefore LIVE, not contingent**, and it applies to L3:
reported as a **DISCLOSED SINGLE-LEVEL VALIDATION COMPARISON**, `ONE LEVEL — NO GRID FAMILY`
on the face of every row, **no observed order, no GCI, no family band, no Roache triple.**

**Cost so far:** L3 5.4 core-min (completed) + 0.26 (two FPE smokes) + **L2 10.60** +
**L1 41.67** on the two diverged levels = **57.9 core-minutes**, against a family estimate of
1,184 and a family cap of 3,551. **Waste is named, not absorbed: 52.5 core-minutes bought
three stack traces and one mechanism.**
