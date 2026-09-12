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
