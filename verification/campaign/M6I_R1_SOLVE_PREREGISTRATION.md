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

---

# ADDENDUM 7 — 2026-09-12. **THE EXPERIMENT ANSWERED BOTH LIMBS. THIS LANE'S READING SURVIVED AND ITS SUPERVISOR'S DID NOT — AND THE SECOND LIMB FAILED AT EXACTLY ONE STATION.**

**v1.6 → v1.7. Lines whose number changed above this section: 0.** No band, threshold, cap or
label above moves.

## A7.1 — 🔴 READING A IS REFUTED. THE 87° GRID CARRIES THE REGISTERED SECOND-ORDER SCHEMES PERFECTLY WELL.

`M6I-R1-L3-NORAMP`, pid 71585, launched 22:35:21Z. **`rc = 0`. 3,000 iterations
(200 + 2,800). `End` line present.** Registered second-order schemes and registered
relaxation **from iteration 1, with no ramp at all**, on a grid whose maximum
non-orthogonality is **87.66°**:

| LC-1 peak `CellsPercent` | LC-2 `bounding nuTilda` lines | final Ux initial residual |
|---|---|---|
| **0.00 %** over 5,600 reported lines | **zero** | **4.50e-07** |

**Not one clipped cell. Not one bounded ν̃. Not one sign of distress.**

**READING A — that `linearUpwind` under `limited corrected 0.33` at 87.7° is unstable *as
such*, shock or no shock — IS REFUTED BY THIS RUN.** It was the cfd supervisor's reading and
it was registered as theirs. **READING B — that the instability requires a shock — survives.**
It was this lane's, registered in A6.3 explicitly against its own supervisor's stated
expectation, and it held. **The ramp is not what makes the schemes survivable; the absence of
a shock is.**

**What this means for the family, and it is the opposite of a cosmetic finding.** L1 and L2
did not die of a generic scheme-plus-mesh incompatibility that a gentler scheme would cure
everywhere. **They died when and because a shock formed.** The instability is a
shock-capturing failure of an unbounded second-order upwind scheme, and the ladder's next
rung is therefore **a bounded (TVD) convection scheme**, which is §A5.4's pre-declared
candidate — **now selected on evidence rather than on order**, and that reordering is
registered here with its reason as A6.4 required.

## A7.2 — 🔴 THE SECOND LIMB FAILED, AT ONE STATION, AND IT IS THE STATION EVERYTHING ELSE POINTED AT

A6.3's free limb: two converged solutions of the same discrete equations cannot depend on the
path taken to them, so the ramped and un-ramped L3 must agree to **max|ΔCp| ≤ 0.01 at every
station**. Measured, same extractor, same 24 points per station:

| η | 0.20 | 0.44 | 0.65 | 0.80 | 0.90 | **0.96** |
|---|---|---|---|---|---|---|
| **max\|ΔCp\|** | 0.000306 | 0.000571 | 0.001703 | 0.002156 | 0.006339 | **0.016502** |
| RMS ΔCp | 0.000108 | 0.000174 | 0.000638 | 0.000968 | 0.002007 | 0.006674 |
| limb | PASS | PASS | PASS | PASS | PASS | 🔴 **FAIL** |

**Five stations agree to better than 0.0022. The sixth misses the registered 0.01 by 65 %.**
And the deviation is **monotone outboard** — 0.0003 → 0.0006 → 0.0017 → 0.0022 → 0.0063 →
0.0165, a factor of **54 from root to tip**.

**Three independently registered things point at η = 0.96, and none of them knew about the
others:**
1. **A1.4**, registered before any Cp existed: *"if the Cp bands miss, they miss at η = 0.96
   first"* — because **12,464 of L1's 191,794 faces over 70° sit within |Δη| < 0.02 of 0.96**,
   against 84, 62 and 116 at η = 0.20, 0.44 and 0.65.
2. **§4's disclosed geometry difference**: the generator's semispan/root-chord ratio is
   1.47602 against the TMR/AGARD nominal 1.48443, **0.57 % apart**, which bites hardest at the
   outermost station.
3. **§A7.3's rank co-location**, measured after both: the MPI rank that raised SIGFPE on
   **both** L1 and L2 is the rank owning η > 0.96.

**THE REGISTERED CONSEQUENCE, APPLIED.** A6.3 fixed it in advance: a larger difference *"would
mean the ramped L3 was not converged and would put L3's `GATE FAIL` itself in question"*.
Applied at the narrowest honest scope:

- **η = 0.96's two rows carry `NOT A RESULT — PATH-DEPENDENT` beside their values** on both
  L3 runs. Their RMS values (0.4111 ramped, 0.4092 un-ramped, upper surface) are printed and
  are not verdicts.
- **The other ten rows keep `GATE FAIL`.** They agree between the two runs to ≤ 0.0022 in
  max|ΔCp| and they miss the 0.050 band by factors of **3.4 to 8.7** — a 0.0022 path
  difference cannot flip a row that misses by 0.35.
- **The level's overall verdict remains `GATE FAIL`**, carried by the five clean stations.
- 🔴 **REFERRED, NOT RULED BY THIS LANE:** whether a **row**-level `NOT A RESULT` under a
  lane's own additional limb should promote to the **level** verdict. The frozen §5 B3 makes
  `NOT A RESULT` an override **for §6 preconditions and the §7 plant**, both of which passed
  here (M∞ exact, `End` line present, six stations present, **planted control seen on both
  runs**). This limb is this lane's own addition and can only tighten. **The promotion
  question is a standards question and goes to the verification supervisor.** Nothing is
  reported as settled in the meantime.

**And the un-ramped level was graded by the frozen grader too, with its own planted control
seen:** `GATE FAIL`, 12 rows, RMS agreeing with the ramped run to three decimals at five
stations. **Both paths reach the same verdict; only the tip station's value is path-dependent.**

## A7.3 — 🔴 THE FAILING MPI RANK OWNS THE TIP ON BOTH LEVELS

Both L1 and L2 raised SIGFPE on **rank 3**. Measured from each level's own preserved
decomposition (`ATTEMPT1_DIVERGED/processor*/constant/polyMesh/points`), near-field points
(r < 3 root chords):

| level | rank 3's near-field η range | fraction of its near field at **η > 0.96** |
|---|---|---|
| **L1** | 0.965 – 1.962 | **100.0 %** (129,641 of 129,641) |
| **L2** | 0.952 – 1.970 | **99.8 %** (16,787 of 16,813) |

For contrast, rank 0 holds 5.1 % / 6.4 % of its near field outboard of η = 0.96.
**Rank 3 is the outboard-and-aft octant — the tip cap, where A1.4 measured the median
non-orthogonal face at η = 1.009.**

**Stated with its strength and no more.** SIGFPE is raised on whichever rank first evaluates
the bad number, and MPI then aborts the job, so the failing rank locates **where the
excursion first became non-finite**, not necessarily where it originated. Two of two landing
on rank 3 specifically has a **1-in-16 chance** under a uniform null; two of two landing on
either *outboard* rank (2 or 3) has a 1-in-4 chance. **This is strong co-location and it is
not proof.** What it does do is remove "the 87° is out in the far field and cannot matter"
from the table: **zero of the >70° faces lie beyond r = 5 on any level**, and the rank that
owns them is the rank that died, twice.

## A7.4 — COST, AND WHAT THE EXPERIMENT WAS WORTH

| item | core-min |
|---|---|
| L3 completed (graded) | 5.40 |
| L3 attempts 1 and 2, SIGFPE — **waste, named** | 0.26 |
| **L2 diverged — waste, named** | **10.60** |
| **L1 diverged — waste, named** | **41.67** |
| **L3_NORAMP, the discriminating experiment** | **~5.4** |
| **total** | **≈ 63.3** of a 1,184 family estimate and a 3,551 family cap |

**The experiment cost about five core-minutes and refuted a hypothesis that would otherwise
have been fixed by changing the convection scheme everywhere and calling the family cured.**
A rule-12 estimate-versus-actual row is owed to `docs/COST_CALIBRATION.md` when the family
closes, and it will carry the 2.7× iteration-rate misprediction of A4.2 as its main term.

---

# ADDENDUM 8 — 2026-09-12. **RUNG 4: BOUNDED TVD CONVECTION. AND "IT SURVIVED" IS REGISTERED AS *NOT* A PASS.**

**v1.7 → v1.8. Lines whose number changed above this section: 0.** No band, threshold, cap or
label above moves. This addendum registers **one numerics change** and **one success criterion
that is harder than survival**.

## A8.1 — THE ONE REGISTERED CHANGE

Applied by `verification/runs/M6I_runs/build_m6i_rung4_tvd.sh` to **L1 and L2**, identically:
every convective term moves from the **unbounded** second-order `linearUpwind` to the
**bounded TVD** `limitedLinear(V) 1` —

| term | before | after |
|---|---|---|
| `div(phi,U)` | `bounded Gauss linearUpwind limitedGrad` | **`bounded Gauss limitedLinearV 1`** |
| `div(phi,e)`, `div(phi,K)`, `div(phi,Ekp)` | `bounded Gauss linearUpwind limitedGrad` | **`bounded Gauss limitedLinear 1`** |
| `div(phi,nuTilda)` | `bounded Gauss upwind` | **`bounded Gauss limitedLinear 1`** |
| `div(phid,p)` | `Gauss upwind` | **unchanged** |

**Relaxation, turbulence model, mesh, condition, iteration budget, bands and caps are
untouched, and the 200-iteration first-order ramp is left exactly as registered** — asserted
by the build script on both levels, which refuses if the ramp file has stopped being
first-order. **It is NOT extended** (A6.4).

**Why this rung and not A5.4's first-listed one.** A7.1: `L3_NORAMP` proved the registered
second-order schemes stable at 87.66° **without a shock**, so the instability is not generic
and tighter relaxation does not address it. **The mechanism is an unbounded second-order
upwind scheme overshooting across a captured shock.** `limitedLinear 1` is second-order where
the solution is smooth and limits **only** near the discontinuity. **The reordering within the
numerics rung is registered here with its reason**, as A6.4 required.

**NOT applied to L3.** L3 has two completed, graded runs under the `linearUpwind` schemes and
those are the record. **Registered now:** if L1 or L2 completes under rung 4, **L3 is re-run
under rung 4 as well** (6.4 core-minutes) so that any family is one configuration — and the
existing L3 rows stay on the record as graded, struck by nothing.

## A8.2 — 🔴 THE SUCCESS CRITERION IS A **CONJUNCTION**, BECAUSE THE CHEAPEST WAY TO SURVIVE A SHOCK IS TO SMEAR IT

**`rc = 0` to `endTime` IS NOT A PASS FOR THIS RUNG.** L3 survived 2,800 second-order
iterations and L3 has no shock — **those two facts are the same fact.** The ramp set that trap
once; a limiter can set it again in a better costume, by flattening the gradient until there
is nothing left to destabilise. **A limiter that buys stability with the graded quantity has
bought it with the answer.**

**REGISTERED, BEFORE THE RUN — BOTH LIMBS MUST HOLD:**

- **C1 — it ran.** `rc = 0`, last time == `endTime`, `End` line, **zero** `bounding nuTilda`
  lines (LC-2), LC-1 peak `CellsPercent` < 2.0.
- **C2 — IT STILL HAS A SHOCK.** A3.1's S1 and S2, unchanged and keyed to the experiment
  alone: **`cfd_cp_rise_at_shock` ≥ 0.212 at η = 0.65 and ≥ 0.320 at η = 0.90**, with
  **`x_shock_cfd` < 0.85 c** at both.

**C1 without C2 is NOT a cured family.** It is **`GATE FAIL`, labelled
`SURVIVED BY SMEARING — THE SAME NEGATIVE RESULT BY ANOTHER ROUTE`**, and it is reported as
that in those words. **C1 failing is `NOT A RESULT` as before.**

## A8.3 — 🔴 PREDICTIONS WITH NUMBERS THIS LANE CAN MISS

1. **L2 and L1 both reach `endTime` with `rc = 0`, zero ν̃ boundings, LC-1 peak < 2.0 %.**
2. **L1 is SHOCK-BEARING under C2** — `cfd_cp_rise_at_shock` ≥ 0.212 at η = 0.65 and ≥ 0.320
   at η = 0.90, `x_shock_cfd` < 0.85 c. **L3 gave 0.087 and 0.053 at x/c 0.953 and 0.923.**
3. **L1's upper-surface Cp RMS falls below 0.150 at η = 0.20, 0.44 and 0.65**, from L3's
   **0.2801 / 0.3639 / 0.4000**. A 2.4–2.7× improvement, and a number that can miss.
4. **L1's minimum upper-surface Cp at η = 0.65 reaches at most −0.90**, from L3's **−0.4354**;
   the experiment's own minimum there is near −1.1.
5. **L2 remains the hardest level** — if exactly one of L1 and L2 fails C1, it is **L2**, on
   the A5.4 hypothesis that 122,880 cells is the worst regime: fine enough to begin forming a
   shock, too coarse to resolve it.

**Predictions 2, 3 and 4 are the ones that would make M6 a result rather than a story about
why it is not.** None of them is implied by survival.

## A8.4 — THE η = 0.96 GEOMETRIC LIMB IS **NOT** A NUMERICS PROBLEM AND NO SCHEME WILL FIX IT

Separated from the numerics story deliberately, because it will otherwise be silently expected
to improve with rung 4 and will not. §4 disclosed it before any run: **the generator's
semispan-to-root-chord ratio is 1.47602 against the TMR/AGARD nominal 1.48443 — 0.57 %
apart.** Stations are cut at `y = η × 1.4760179762198`, i.e. as a fraction of the semispan of
**the geometry that actually ran**.

**So the η = 0.96 row may be comparing a slightly different spanwise station than AGARD
measured**, and that is a **geometry** fact. It sits **beside** A7.2's
`NOT A RESULT — PATH-DEPENDENT` label on that row, not inside it, and **rung 4 is not expected
to move it.** If η = 0.96 remains the outlier after rung 4, that is evidence **for** the
geometric limb and against a purely numerical explanation — registered now so it counts.

## A8.5 — A SMALL INSTANCE OF L-571, CAUGHT IN THIS ADDENDUM'S OWN BUILD SCRIPT

`build_m6i_rung4_tvd.sh`'s first version asserted the substitution had worked with
`grep -q 'linearUpwind' system/fvSchemes` → refuse. **It refused on a correctly patched
file** — because the comment the script itself inserts three lines above the schemes contains
the word `linearUpwind` while explaining its removal. **An assert that matches its own
documentation is not an assert.** Fixed by stripping comment lines before the grep, with the
original and the reason recorded in the script. It is the same shape as **L-571** — a check
whose referent was not what the author believed — caught this time in seconds and for nothing,
by the check failing loudly on a good file rather than passing quietly on a bad one.

---

# ADDENDUM 9 — 2026-09-12. **A PARENTHETICAL OF §4 IS FALSE AND IS CORRECTED HERE. THE GATE IT SITS BESIDE IS UNCHANGED AND IS SATISFIED.**

**v1.8 → v1.9. Lines whose number changed above this section: 0.** No band, threshold, cap or
label moves — and the limb this concerns, **IC-4, is not touched**.

## A9.1 — WHAT §4 SAYS, AND WHAT THE SOLUTIONS MEASURE

§4 registered the wall treatment as `nutLowReWallFunction` with the parenthetical
**"every level is wall-resolved, y⁺ ≤ 1"**. Measured from each level's own solver log, wing
patch, final write:

| level | y⁺ min | **y⁺ max** | y⁺ average | §4's "≤ 1" |
|---|---|---|---|---|
| **L3** | 0.4644 | **2.5455** | 1.4046 | 🔴 **FALSE — over by 2.5×** |
| **L3_NORAMP** | 0.4637 | **2.5459** | 1.4103 | 🔴 **FALSE**, and it reproduces L3 to 4 decimal places |
| **L2** | 0.0581 | **1.2144** | 0.3658 | 🔴 **FALSE — over by 1.2×** |
| L1 | `PENDING` | `PENDING` | `PENDING` | `PENDING` |

**The parenthetical was wrong and this document says so rather than quietly reinterpreting
it.** Its error was to carry a **mesh-construction target** — `input.nml`'s
`target_y_plus = 0.25` on the fine level, doubling with each coarsening to a nominal
0.25 / 0.5 / 1.0 — into a claim about **the solution**. The first cell height is built from an
*assumed* skin friction; the achieved y⁺ is whatever the converged solution makes it, and on
this wing it is **about 2.5× the nominal** at the maximum.

## A9.2 — 🔴 THE GATE IS UNCHANGED, WAS SET HIGHER THAN THE PARENTHETICAL, AND IS SATISFIED

**IC-4, registered in §7 before any solve, reads `y⁺ max ≤ 2.0 on L1 and ≤ 5.0 on L2 and
L3`** — not ≤ 1. The prose parenthetical and the gate were never the same number, and **the
gate is the one that grades.** On the measurements above, **L3 (2.55 ≤ 5.0) and L2
(1.21 ≤ 5.0) both PASS IC-4.** L1's limb is 2.0 and is `PENDING`.

**No gate is loosened, tightened or reinterpreted by this addendum.** Had IC-4 been written
as "≤ 1" it would now be failing on two levels and the honest course would have been to say
so; it was not, and the reason it was not is that §7 was written to grade the solution while
§4's parenthetical was describing the mesh.

## A9.3 — AND THE FAMILY'S y⁺ SCALING IS CONFIRMED BY MEASUREMENT, WHICH IS A POSITIVE RESULT

The ladder is one generator call plus two coarsenings, so each coarsening **doubles the first
cell height** and y⁺ should double with it. **Measured maxima: L2 1.2144, L3 2.5455 — a ratio
of 2.096 against a designed 2.000.** The family scales as constructed, and that is a fact
about the grids that survives the parenthetical being wrong about their absolute value.

**And the un-ramped run reproduces the ramped one to four decimal places in y⁺** (2.5455 vs
2.5459), which is independent corroboration of A7.2's finding that the two paths reach the
same solution everywhere except the tip station.

---

# ADDENDUM 10 — 2026-09-12. **L2 UNDER RUNG 4: C1 PASS, C2 FAIL. AND THE EVALUATOR'S OWN LABEL OVERSTATES WHAT L2 CAN SHOW.**

**v1.9 → v1.10. Lines whose number changed above this section: 0.** No band, threshold, cap
or label moves.

## A10.1 — THE NUMBERS, C2 FIRST

`M6I-R1-L2-TVD`, pid 78552, **`rc = 0`, last time 5000 == `endTime`, `End` line present.**

**C2 — IT STILL HAS A SHOCK: 🔴 FAIL, on both stations.**

| station | `cfd_cp_rise_at_shock` | S1 limb | `x_shock_cfd` | S2 limb | |
|---|---|---|---|---|---|
| η = 0.65 | **0.1031** | ≥ 0.212 | **0.8851** | < 0.85 | **NOT shock-bearing** |
| η = 0.90 | **0.0582** | ≥ 0.320 | **0.9233** | < 0.85 | **NOT shock-bearing** |

**C1 — IT RAN: PASS.** LC-1 peak `CellsPercent` **0.00 %** over 9,600 reported lines; LC-2
worst `bounding nuTilda` **0.0391** against a 1e6 threshold; final Ux initial residual
**1.28e-07**; planted control seen (RMS moved 0.0892 against a required 0.0617).

**Verdict: `GATE FAIL`.** All 12 Cp rows outside the registered RMS ≤ 0.050 band.

## A10.2 — 🔴 THE EVALUATOR PRINTS "SURVIVED BY SMEARING" AND L2 CANNOT ESTABLISH THAT

`evaluate_m6i_level.sh` emits that label mechanically whenever C1 holds and C2 fails, and
**A8.2 registered the label in exactly those terms.** Applied to L2 it **overstates**, and
this addendum says so rather than letting a registered phrase do work the data does not
support.

**Two readings fit L2's numbers and they are not distinguishable from L2 alone:**

- **(a) the limiter smeared a shock the run would otherwise have captured** — the phrase's
  meaning;
- **(b) 122,880 cells still cannot carry the M6 shock at all**, exactly as 15,360 could not,
  and there was never a shock for the limiter to smear.

🔴 **The comparison that would separate them does not exist: L2's own `linearUpwind` run
DIVERGED and produced no Cp.** There is no "before" to measure a smearing against. **A label
asserting (a) is therefore an inference and not a measurement, and it is recorded as one.**

**The evidence available leans to (b), and it is a trend rather than a proof:** against L3,
L2's upper-surface Cp RMS roughly **halves** at every station (0.2801→0.1506, 0.3639→0.2085,
0.4000→0.2453, 0.4265→0.2667, 0.4325→0.2785, 0.4111→0.2670), the lower surface likewise
(~0.17–0.19 → ~0.089–0.109), the shock rise **rises** 0.0875→0.1031 at η = 0.65, and the
shock location **moves forward** 0.9531→0.8851 c, toward the experiment's 0.4752. **Everything
is moving the right way with refinement and nothing has arrived.**

## A10.3 — 🔴 BUT THAT TREND IS CONFOUNDED, AND THE RUN THAT DECONFOUNDS IT IS ALREADY REGISTERED

**L3 was solved under `linearUpwind`; L2 under rung 4's bounded TVD.** The L3 → L2 improvement
therefore **mixes an 8× refinement with a change of convection scheme**, and neither term can
be read off it. **No observed order, no refinement claim and no scheme credit may be taken
from that pair**, and none is taken here.

**A8.1 registered the deconfounding run before this result existed:** *"if L1 or L2 completes
under rung 4, L3 is re-run under rung 4 as well so that any family is one configuration."*
**L2 has now completed under rung 4, so the condition is met and `M6I-R1-L3-TVD` is released
from `held/` to the queue.** Its case was built and validated while L2 was still running, and
its prediction was registered then: **L3_TVD's Cp matches the un-ramped L3's to
`max|ΔCp| ≤ 0.02` at η = 0.20–0.90 and its C2 limb FAILS as L3's did — because a limiter
cannot create a shock the grid could never carry.** A larger difference would mean the
convection scheme moves Cp on a **shock-free** solution, which would weaken the rung-4 reading
and is registered as a way for it to fail.

**With L3_TVD in hand the L3 → L2 comparison becomes single-variable**, and reading (a) versus
reading (b) above becomes answerable rather than arguable.

## A10.4 — COST

L2 under rung 4: **`endTime` 5000 reached.** Its predecessor's diverged attempt cost 10.60
core-minutes and is named as waste, unchanged. The rule-12 row for this level is owed when
the family closes and will carry the rung-4 actual against the registration's 85.3 estimate
and 256 cap.

---

# ADDENDUM 11 — 2026-09-12. **MY OWN REGISTERED FALSIFIER FIRED. THE TVD SCHEME MOVES Cp BY 0.12 ON A SHOCK-FREE SOLUTION, AND THAT WEAKENS THE RUNG-4 READING BY THE EXACT ROUTE A8.1 NAMED.**

**v1.10 → v1.11. Lines whose number changed above this section: 0.** No band, threshold, cap
or label moves.

## A11.1 — 🔴 THE PREDICTION FAILED, AT EVERY STATION, BY UP TO 6×

`M6I-R1-L3-TVD`, pid 104873, **`rc = 0`**, C1 **PASS**, C2 **FAIL** (rise 0.0690 / 0.0434,
`x_shock` 0.9531 / 0.9233). The C2 half went as predicted. **The other half did not.**

ADDENDUM 10 §A10.3 registered, before this run: *"L3_TVD's Cp matches the un-ramped L3's to
`max|ΔCp| ≤ 0.02` at η = 0.20–0.90."* Measured, η = 0.96 excluded because it is already
`NOT A RESULT — PATH-DEPENDENT`:

| η | 0.20 | 0.44 | 0.65 | 0.80 | 0.90 | (0.96, excluded) |
|---|---|---|---|---|---|---|
| **max\|ΔCp\|** | **0.1213** | **0.1084** | **0.1003** | **0.0698** | **0.0527** | 0.0410 |
| vs band 0.02 | **FAIL 6.1×** | **FAIL 5.4×** | **FAIL 5.0×** | **FAIL 3.5×** | **FAIL 2.6×** | — |

**🔴 THE CONSEQUENCE WAS REGISTERED IN ADVANCE AND IS NOW OWED.** A10.3's own words: *"A
larger difference would mean the convection scheme moves Cp on a **shock-free** solution,
which would weaken the rung-4 reading and is registered here as a way for it to fail."*
**It moved Cp on a shock-free solution. The rung-4 reading is weakened, by this lane's own
registered test, and the weakening is recorded before anything is built on top of it.**

`limitedLinear 1` is supposed to be second-order where the solution is smooth and to limit
**only** near a discontinuity. **On a shock-free L3 it changed the answer by up to 0.12 in
Cp.** Either the solution is not smooth in the limiter's sense, or the limiter's gradient
ratio is being corrupted — and on a grid at **87.66° maximum non-orthogonality with aspect
ratios to 1,244**, the second is entirely plausible: the ratio is formed from neighbouring
cell values across exactly those faces.

**Registered as a hypothesis, not asserted:** **(c) the limiter over-limits in smooth regions
on this grid**, depressing suction and flattening gradients everywhere, which would explain
both the 0.12 shift and the absence of a shock. **It is not tested by anything run so far.**

## A11.2 — 🔴 THE TRACE ANSWERS THE (a)-versus-(b) QUESTION DIRECTLY, FROM A FILE ALREADY ON DISK, AND IT ANSWERS (b)

A10.2 left open whether L2 **smeared** a shock (a) or **never had one** (b). The test costs
nothing: *is there any local compression near the experiment's shock at x/c **0.4752**, however
weak?* Read from L2's own `cp_extracted.json`, upper surface, both shock stations:

**There is not.** At η = 0.65 the upper surface runs from its suction peak at x/c 0.0295
(Cp −0.7324) to the trailing edge as **one continuous, monotone recovery** — successive
rises 0.054, 0.088, 0.059, 0.040, 0.033, 0.051, 0.093, **0.119**, 0.112, 0.086, 0.054,
0.030, 0.016, 0.009 — with **no local feature of any size at or near 0.4752**. η = 0.90 is the
same shape. **The steepest segment sits at x/c 0.646–0.768**, far aft of the experimental
shock, and is the **trailing-edge recovery** — the same feature D1 correctly identified on L3.

**A smeared shock would show a local MAXIMUM of `dCp/dx` near the shock location, standing
above the background recovery. There is none.** The gradient rises monotonically to its peak
two-thirds of the way back and then decays. **Reading (b) is supported directly from an
artifact: there is no shock to smear**, and the detector's 0.8851 is the steepest part of a
smooth recovery ramp, not a captured discontinuity.

**And this does not rescue rung 4** — §A11.1 stands independently. The scheme is moving Cp by
0.12 **somewhere other than a shock**, and (b) explains the missing shock without explaining
that.

## A11.3 — THE DECONFOUNDED COMPARISON IS NOW CLEAN AND THE REFINEMENT TREND IS REAL

**Same scheme (rung 4), same everything, 8× the cells.** L3_TVD → L2, upper-surface Cp RMS:

| η | 0.20 | 0.44 | 0.65 | 0.80 | 0.90 | 0.96 |
|---|---|---|---|---|---|---|
| **L3_TVD** (15,360) | 0.2806 | 0.3580 | 0.3978 | 0.4275 | 0.4365 | 0.4196 |
| **L2** (122,880) | **0.1506** | **0.2085** | **0.2453** | **0.2667** | **0.2785** | **0.2670** |
| factor | 1.86 | 1.72 | 1.62 | 1.60 | 1.57 | 1.57 |

**The improvement A10.2 declined to bank is real and it is refinement**, now measured at fixed
scheme: RMS falls by **1.57–1.86×** across an 8× cell increase, and the shock rise at η = 0.65
goes **0.0690 → 0.1031 (+49 %)** with `x_shock` moving forward **0.9531 → 0.8851** toward the
experiment's 0.4752. **Still no observed order is computed** — two levels, and A3.1's
admissibility condition is unmet because neither is shock-bearing.

## A11.4 — 🔴 THE L1 BRANCHES, REGISTERED BEFORE L1's NUMBERS EXIST

L1 is at stage-2 iteration ~444 of 7,800. **Both outcomes are fixed now so that neither is a
consolation written afterwards.**

- **IF L1's C2 ALSO FAILS** — `cfd_cp_rise_at_shock` below 0.212 at η = 0.65 or below 0.320 at
  η = 0.90 — then **the registered family-level conclusion is: THE M6I TMR-GENERATOR GRID
  FAMILY, AT 15,360 / 122,880 / 983,040 CELLS, CANNOT CARRY THE ONERA M6 SHOCK AT THE AGARD
  TEST 2308 CONDITION UNDER THIS SOLVER AND MODEL.** That is a **result about the grid family
  and the solver chain**, reported as one under Sanaa's standing instruction that OpenFOAM and
  mesh issues are **surfaced as runs, not worked around** (2026-09-10). It is **not** a result
  about the ONERA M6, about AGARD AR-138, or about the lab's method, and the report will say so.
- **IF L1's C2 PASSES** — both limbs, both stations — **the family is judged capable at 983,040
  cells and not below**, L1 is graded against the 14 bands as a **single shock-bearing level**,
  and A5.3's single-level disclosure governs: **no observed order, no GCI, no family band**,
  because L3 and L2 are not shock-bearing and A3.1 bars a triple assembled from incomparable
  levels.
- **EITHER WAY**, §A11.1's finding stands: the rung-4 scheme moves Cp by up to 0.12 on a
  shock-free solution, and any L1 number inherits that as a disclosed, unquantified scheme
  sensitivity until hypothesis **(c)** is tested.

---

# ADDENDUM 12 — 2026-09-12. **A DEFECT THIS LANE REPORTED UPWARD DOES NOT EXIST, AND THE SOLUTION-SOUNDNESS QUESTION IT RAISED IS CLOSED IN L3's FAVOUR.**

**v1.11 → v1.12. Lines whose number changed above this section: 0.** No band, threshold, cap
or label moves.

## A12.1 — 🔴 CORRECTION: `--field` IS NOT A SILENT NO-OP, AND THIS LANE SAID IT WAS

This lane reported upward — in commit message `a7dc58fd` and in its reports — that the
ParaView route to the **fields** half of Sanaa's ~20:30Z render directive was *"blocked by a
disclosed defect"*, namely that `render_openfoam_3d_paraview.py --field` was a **silent
no-op**. **That is false.**

**Measured by the cfd render lane** (`25caef4c6`; **relayed here, not verified by this lane**):
`--field` **works and always did**. The original defect finding compared `--field p` against
*"the plain mesh render"* and found them identical — **because ParaView auto-colours by the
first array it finds, so the "plain" arm was already coloured by `p`.** Immediately after
`Show()` and **before any `ColorBy` call**, `d.ColorArrayName` already reads `['POINTS','p']`.
**The comparison had no uncoloured arm.** With a true solid-colour reference, colouring by `T`
instead of `p` moves **7.07 %** of frame pixels.

**How this lane got it wrong, stated plainly: it read a script's header, found the defect
described there, and reported it as known — without verifying it.** The header was honestly
written and honestly wrong, and the lane treated **a document about a measurement as the
measurement**. *"A relayed check is a summary, not a check"* is usually aimed at a supervisor
accepting a lane's word; **it applies identically to a lane accepting a document's word.**
Carried into `MONITOR_STANDARD.md` v1.14 §10 as the amendment's own unflattering example, and
recorded here because the claim was made from this document's lane and travelled upward.

**No artifact of this registration depends on the false claim.** The Cp figure
`RENDERS/M6I_R1_L3_cp_vs_agard.png` was produced by `scripts/plot_m6i_cp.py` from the graded
`cp_extracted.json` and is unaffected; the render lane owns and has already corrected
`RENDERS/CAPTIONS.md`.

## A12.2 — THE ZERO-FIELD QUESTION AGAINST L3 IS CLOSED, AND L3's SOLUTION IS SOUND

A question was raised upstream as to whether L3's velocity and turbulence fields were
degenerate. **They are not, and the premise was a locus confusion.** Measured by the render
lane by **raw binary read of the `internalField` block** (`c2c46be07`; **relayed, not verified
by this lane**):

| field | boundary value on `wing` | **internalField range** |
|---|---|---|
| `U` | `noSlip` — zero **by boundary condition** | **1.11 – 360.13 m/s**, against a freestream of 291.44 |
| `nuTilda` | `fixedValue uniform 0` — a wall value | **5.24e-06 – 0.0431**, with `nut` tracking it |

**The renderer draws BOUNDARY PATCHES.** `U` reads zero there by no-slip while `p` reads
non-zero by `zeroGradient`; **those were never the same locus.** **The Spalart–Allmaras model
worked, the velocity field is alive, and L3's `GATE FAIL` rests on a sound solution** — which
is what makes it a verdict rather than an artefact. The rung-4 work built on L3 stands.

## A12.3 — WHAT IS STILL OPEN AT THIS DOCUMENT'S LAST ENTRY

- **L1 under rung 4 is RUNNING** — stage-2 iteration ~636 of 7,800, `rc` not yet written,
  LC-1 peak **0.00 %**, LC-2 worst ν̃ **0.0730** against 1e6, Ux initial residual **8.33e-06**.
  Detached under the runner and parented to init, so it survives any agent ending.
  **Its branches are pre-registered at §A11.4 and `evaluate_m6i_level.sh L1` produces its
  verdict mechanically.**
- **Hypothesis (c)** — that `limitedLinear` over-limits in smooth regions on this
  non-orthogonal grid, per §A11.1's measured 0.12 Cp shift on a shock-free solution — is
  **registered and untested.**
- **The η = 0.96 geometric limb** (§A8.4, the 0.57 % semispan-ratio difference) is
  **untested** and no scheme is expected to move it.

---

# ADDENDUM 13 — 2026-09-12. **L1 STOPPED AT ITERATION 844 WITH `rc = 1` AND HEALTHY PHYSICS. THE CAUSE IS UNDETERMINED AND I WILL NOT INVENT ONE. IT RESUMES FROM 800.**

**v1.12 → v1.13. Lines whose number changed above this section: 0.** No band, threshold, cap
or label moves. The only change to any instrument is **instrumentation**, §A13.3.

## A13.1 — WHAT STOPPED, AND WHAT WAS TRUE WHEN IT DID

`M6I-R1-L1-TVD`, pid 93486. Stage 1 `rc = 0`. **Stage 2 stopped mid-iteration at
`Time = 844` with `rc = 1`** — **not 136**, so **no SIGFPE**. `End` lines: **0**.

**The physics was in good order at the stop**, read from the run's own final lines: Uz initial
residual **2.06e-05**, e **1.15e-04**, GAMG on p converging in **10** iterations;
`limitTemperature` reporting **zero** limited cells at **both** bounds with `UnlimitedTmin`
**184.30 K** and `UnlimitedTmax` **339.64 K**, both physical; `pressureControl: p max`
**234,754 Pa** — **2.32× freestream** and unremarkable; the worst of 487 `bounding nuTilda`
lines reading `min −2.30e-05  max 0.0212`, **four decades below L2's 3.08e+43**. Cl 0.2512,
Cd 0.0320 at iteration 843. **Nothing in the physics was going wrong.**

## A13.2 — 🔴 THE CAUSE IS UNDETERMINED. HERE IS EVERYTHING IT IS **NOT**, MEASURED.

I was asked to report the cause and not just the resume. **I could not determine it, and that
is the report.** What is excluded is excluded by measurement, not by argument:

| candidate | verdict | evidence |
|---|---|---|
| SIGFPE / the L2–L3 divergence fault | **EXCLUDED** | `rc = 1`, not 136; **zero** `exited on signal`, `Primary job`, `sigFpe` or `FOAM FATAL` strings in the solver log |
| a truncated / half-written log | **EXCLUDED** | the final line ends with a complete `\n` (`od -c`); the solver wrote a whole GAMG line and stopped |
| the CRM lane's cause — `set -u` round the bashrc with stderr sent to `/dev/null` | **EXCLUDED** | `launch_m6i_v2.sh` sends the bashrc to `log.env` and **checks `ENV_RC`**; its only `/dev/null` uses are on `find`/`pgrep`/`grep`/`command -v` probes — **never on the solver or the environment stream** |
| the `foamDictionary -entry endTime -set` `#include`-inlining hazard | **EXCLUDED** | `system/controlDict` contains **0** `#include` directives and the launcher makes **0** `foamDictionary` calls — it uses `sed -i` with a read-back assert |
| a box-wide event | **EXCLUDED** | **no other `RC.txt` anywhere under `verification/runs` or `cases` was written in the window**; 46 solver processes were alive afterwards; `uptime -s` shows no reboot since 21:32:17Z |
| disk | **EXCLUDED** | 53 % used, 460 G free |
| **the OOM killer** | 🔴 **NEITHER CONFIRMED NOR EXCLUDED** | `dmesg` is not readable from this lane without privilege. **This is a gap, not a clearance**, and it is the single most plausible remaining candidate given the box was running 46 solvers |

**What it was: `mpirun` returned 1 with no message, no signal report and no solver error,
after a complete line, with healthy fields.** A rank exiting non-zero silently, or being
removed, both fit. **I am not choosing between them on no evidence.**

## A13.3 — 🔴 SO THE RESUME CARRIES INSTRUMENTATION, BECAUSE A CAUSE I CANNOT NAME WILL RECUR

`launch_m6i_v3.sh` — **a new file, not an edit of v2**, precondition checked by testing the
script **argument** (`ps -eo pid,cmd | grep 'bash .*launch_m6i_v[0-9]*\.sh'`) rather than
`pgrep -f`, which matches its own shell: **no launcher process held the script, and every M6I
case had written `RC.txt`.**

**IT ADDS INSTRUMENTATION AND NOTHING ELSE.** Asserted mechanically, not claimed: the v2→v3
diff touches **no** line containing `fvSchemes`, `fvSolution`, `endTime`, `writeInterval`,
`purgeWrite`, `RASModel`, `transonic`, `decomposePar` or `relaxation`. **What the solver
computes is byte-for-byte v2's.**

1. **The solver's stderr goes to its own file.** v2 merged it into a stdout that four ranks
   write concurrently — 1.4 MB of it — where a dying rank's message can be interleaved or
   lost. **That is exactly the shape of "rc = 1 with no message".**
2. **On any non-zero rc the wrapper writes `FAILURE_CONTEXT.<n>.txt`** — rc, UTC, the last
   `Time` line, the solver stderr, `free -g`, `df -h`, `/proc/loadavg`, live solver counts, a
   `dmesg` attempt for the OOM killer, and both stream tails — **captured at the moment of
   failure, while it is still true.** §A13.2's OOM gap exists precisely because nobody
   captured this at 23:18.

## A13.4 — THE RESUME, AND THE CHECKPOINT VERIFIED BY FIELD NAME RATHER THAN BY FILE COUNT

Sanaa, ~21:25Z: *"make sure now that we are able to resume all runs"*, with her standing
ruling that **a bookkeeping failure never voids physics**. **844 iterations on 983,040 cells
is real compute and it is recoverable.**

**Checkpoint 800 is COMPLETE IN ALL FOUR RANK TREES, verified BY FIELD NAME:** every one of
`processor{0,1,2,3}/800` holds `T U alphat nuTilda nut p phi rho uniform yPlus`, all written
**23:16:26Z**, well after the 22:43:33Z launch. **600 is a complete fallback in all four.**
All four trees agree that 800 is their latest, `0/` is present in the cwd and in every
processor tree (rule 4's age datum survives), and `system/controlDict` carries
**`startFrom latestTime`**.

**It resumes through the runner, never by hand** (directive item 19). The entry declares
**`resume_from: "800"`** with **`resume_fields`**, which is the validator's own declared-resume
path: the age guard steps aside **only** for a well-formed declaration, and `check_resume`
then verifies RESUME-LATEST, RESUME-FIELDS, RESUME-ZERO and RESUME-STARTFROM **against the
disk**, refusing if the declaration is not true. **Nothing is deleted to make room for it.**

**Budget:** the resume adds iterations 801→8000 to the 844 already spent. §A4.2's registered
cost consequence is unchanged and is **not** re-decided here: if the cap of 3,277 core-minutes
is crossed the row grades **`NOT A RESULT` on cost**, the cap is **never raised**, and
**nothing is killed** (directive #17). `launch_m6i_v3.sh` adds no timeout, clock check or
spend check — the v2→v3 diff is instrumentation only.

---

# ADDENDUM 14 — 2026-09-12. **THE RESUME STOPPED THE SAME SILENT WAY AT 851. THE INSTRUMENTATION PAID FOR ITSELF, THE CAUSE IS STILL UNDETERMINED, AND ONE CHANGE TESTS THE ONLY LEAD.**

**v1.13 → v1.14. Lines whose number changed above this section: 0.** No band, threshold, cap
or label moves.

## A14.1 — WHAT v3's INSTRUMENTATION BOUGHT, WHICH v2 COULD NOT HAVE TOLD ME

`M6I-R1-L1-TVD-RESUME`, pid 126494, launched 23:29:05Z with the runner logging
**`resumed_from=800`**. **It resumed correctly** — the solver's first line is `Time = 801`,
not `Time = 1` — so **844 iterations of prior compute were preserved and Sanaa's resume ruling
was honoured.** It then **stopped at `Time = 851` with `rc = 1`**, the same silent way.

**`FAILURE_CONTEXT.1.txt` captured, at the moment of failure:**

| | |
|---|---|
| 🔴 **solver STDERR** | **EMPTY — 0 bytes.** stderr is line-buffered, so this is strong evidence **nothing was ever written to it**: mpirun diagnosed nothing, and no rank aborted with a message |
| MemAvailable | **660 GB** free of 739, **swap 0 used** |
| disk | 53 %, 460 G free |
| loadavg(1) / cores | **76.68 / 96** — heavy, **not oversubscribed** |
| solvers alive | 32 `rhoSimpleFoam` + 14 `simpleFoam` (mine were 4 of them) |
| `dmesg` | **`read kernel buffer failed: Operation not permitted`** — the OOM gap **persists and is recorded as a gap** |
| physics at the stop | `LimitedCells` **0** at both bounds, `UnlimitedTmin` 199.98 K / `UnlimitedTmax` 340.10 K, worst ν̃ **0.0214**, Cl 0.2505, Cd 0.0317 — **healthy** |

**Nothing external killed it:** no other `RC.txt` anywhere was written in the window, and the
runner logged `EMPTY: no entries in any team queue; nothing launched` at 23:30, 23:31 and
23:32 — **it took no action at all while L1 died.**

## A14.2 — 🔴 THE CAUSE IS STILL UNDETERMINED, AND ONE THING I MUST SAY ABOUT MY OWN EVIDENCE

**The only pattern in two deaths is weak, and the observation behind it is unreliable.**

| | last **visible** line | wall | iterations |
|---|---|---|---|
| attempt A | GAMG p-solve **1 of 3**, `Time = 844` | 1,564 s | 644 |
| attempt B | GAMG p-solve **2 of 3**, `Time = 851` | 150 s | 51 |

Both land inside the **pressure-solve sequence**. With roughly 14 log lines per iteration of
which 3 are GAMG p-solves, **landing there twice by chance has a probability near 5 %** —
suggestive, not conclusive.

🔴 **And the observation is weaker than that number implies, for a reason that must be stated
rather than left for a reader to discover: STDOUT TO A FILE IS BLOCK-BUFFERED.** An abrupt
death discards the last unflushed block, so **"the last visible line" is a LOWER BOUND on
where the process died, not the death point.** The pattern may be an artifact of where the
buffer happened to cut. **stderr, which is line-buffered, is empty — and that is the one
strong fact I have.**

**So the cause remains UNDETERMINED.** Still excluded by measurement: SIGFPE, resource
exhaustion, an external killer, a box event, disk, and both hazards relayed from other lanes
(§A13.2). Still neither confirmed nor excluded: **the OOM killer**, because `dmesg` is closed
to this lane.

## A14.3 — THE ONE REGISTERED CHANGE: L1's PRESSURE SOLVER, AND IT MOVES NO PHYSICS

*"Never the same action twice on the same state"* (her item 13) bars simply resuming again.
The change tests the only lead the evidence offers:

> **L1's `p` linear solver: `GAMG/GaussSeidel` → `PBiCGStab/DILU`.** L1 only.

**`DILU` and not `DIC`**, deliberately: `transonic yes` puts `fvm::div(phid, p)` into the
pressure equation, which makes the matrix **asymmetric**, and `DIC` is a symmetric-matrix
preconditioner — the wrong lever, chosen by reading the equation rather than by habit.

**🔴 THIS CHANGES NO PHYSICS AND THE CLAIM IS CHECKABLE.** A linear solver solves the **same
discrete system**; at `tolerance 1e-9`, far tighter than every registered convergence gate,
the converged solution it reaches **is** the solution GAMG was reaching. Asserted rather than
claimed: after the edit, `fvSchemes` is **byte-identical to L2's rung-4 file**, `transonic yes`
stands, `fields { p 0.3; rho 0.05; }` and `equations { p 1; U 0.7; e 0.7; nuTilda 0.7; }`
stand, and **no `GAMG` remains anywhere in `L1/system/fvSolution`**. Schemes, model, mesh,
condition, budget, bands and caps are untouched.

**If this stops the same way a third time, the lead is dead and so is this rung.** Registered
now: the next and final step for L1 is **not another numerics change** but a run at **2 ranks
instead of 4** — a decomposition change that tests the MPI layer rather than the mathematics —
and if that also stops, **L1 is PARKED with its action history and a lesson filed**, per her
item 13, and the family is reported on L3 and L2 alone under §A11.4's first branch.

**Checkpoint state is unchanged and re-verified:** all four rank trees hold `0 200 600 800`,
and **800 is complete in all four by field name.** The failed resume wrote no new time
directory (it died at 851; the next write was due at 1000), so **nothing was lost and nothing
was deleted.**

## A14.4 — 🔴 A PLANTED CONTROL IDENTIFIED THE MECHANISM, SO **§A14.3's CHANGE IS WITHDRAWN PRE-COMPUTE**

**Pre-compute condition, checked and not asserted** (rule 2): **no compute ran under §A14.3.**
`L1/processor0` holds `0 200 600 800` and nothing later, and `log.rhoSimpleFoam.resume.2`
**does not exist.** An amendment before first compute is legal; this is one.

### The control, and it discriminates

The hypothesis on the table was an **external signal**. It makes a testable prediction, so it
was tested — on **throwaway processes owned by this lane, signalled BY PID only**, never by
name, because 32 `rhoSimpleFoam` processes belonging to another lane were alive:

| arm | what was signalled | **rc** | **stderr** |
|---|---|---|---|
| **A** | **the CHILD ranks**, `SIGTERM` by pid | **143** | **530 bytes** — mpirun prints *"Primary job terminated normally, but 1 process returned a non-zero exit code"* |
| **B** | **`mpirun` ITSELF**, `SIGTERM` by pid | **1** | **0 bytes** |
| — | **L1, OBSERVED, twice** | **1** | **0 bytes** |

🔴 **ARM B REPRODUCES L1's SIGNATURE EXACTLY AND ARM A DOES NOT.** The stop was **not** the
solver, and **not** a signal to the solver ranks — **it was a signal delivered to the `mpirun`
process itself.**

**And that sharpens the mechanism rather than merely confirming a suspicion.** A killer
matching `rhoSimpleFoam` by **exact name** (`pkill -x`) hits only the children and would have
produced **arm A's rc 143 with 530 bytes of stderr**. The observed signature requires the
**parent** to be hit — and the parent's command line is
`mpirun -np 4 rhoSimpleFoam -parallel`, **which contains the string `rhoSimpleFoam`.** A
pattern kill using **`-f` (full command line)** therefore catches `mpirun` itself, while `-x`
would not. **This lab already owns that lesson from the other direction** — *"pkill kills its
own shell: the pattern matches the invoking command line"* — and this is the same defect
pointed outward.

**REPORTED AS A NAMED HYPOTHESIS WITH ITS PENDING CHECK, NOT AS A CAUSE.** The control
establishes **what class of event produces this signature**; it does **not** establish that
any particular lane did it. The identification of the actor is with the cfd supervisor, who
has put the question to the lane concerned. **No attribution is made here and none will be
made on this evidence alone.**

### 🔴 AND OOM IS NOW EXCLUDED BY THIS LANE'S OWN READ, NOT BY RELAY

§A13.2 and §A14.1 recorded OOM as *"neither confirmed nor excluded"* because `dmesg` is closed
to this lane. **`/var/log/kern.log` is readable, and this lane read it rather than accepting
the exclusion second-hand.** The **only** OOM events on this box on 2026-09-12 are at
**07:01:03Z** and **07:29:40Z**, both `task=python` inside **docker cgroups**
(`CONSTRAINT_MEMCG`), **sixteen hours before these runs and unrelated to them.** Events in
either failure window (23:15–23:35): **zero**. Corroborated from the other side by
`FAILURE_CONTEXT.1.txt`: **660 GB available of 739, swap untouched.**
**OOM: EXCLUDED BY MEASUREMENT.** The §A13.2 gap is closed, and closed by a reader that was
shown able to see a non-zero — the same file returns four OOM lines for earlier today.

### What follows

**§A14.3's `GAMG → PBiCGStab/DILU` change is WITHDRAWN and GAMG is restored**, for two
reasons, either of which would suffice:

1. **It would be a confound.** With the stop identified as external, a numerics change that
   coincided with the run finally completing would take credit that belongs elsewhere.
2. 🔴 **It would have broken the family's configuration identity.** L1's `fvSolution` is now
   **identical to L2's** (comments aside, verified by `diff`), and L3_TVD's too. **The
   L3→L2→L1 comparison is only single-variable while that holds**, and §A11.3 spent a run
   buying exactly that property.

**§A14.3's escalation ladder is withdrawn with it** — a 2-rank run tests the MPI layer, and
the MPI layer is not what failed. **The registered next step is simply to resume from 800
again**, which is **not** "the same action twice on the same state": the state now includes a
control that names the failure class, and the actor is being run down rather than guessed at.
**If it stops a third time with arm B's signature, that is confirmation of an external cause,
not a solver finding, and L1 is parked pending the actor's identification.**

## A14.5 — 🔴 THE ACTOR IS IDENTIFIED AND HAS OWNED IT. THE CONTROL'S PREDICTION WAS CONFIRMED BEFORE THE CONFESSION EXISTED.

The cfd supervisor put the question to the lane concerned, which answered verbatim and without
hedge. **Both deaths were:**

```
pkill -f "rhoSimpleFoam -parallel"
```

issued by the CRM lane to stop **its own** 32-rank hand-invoked diagnostics. Its second one was
issued at **23:31:15Z** against this lane's death at **23:31:39Z**.

🔴 **§A14.4's control predicted this mechanism from first principles, before the admission
existed.** It recorded, from arm A versus arm B alone, that the signature required the
**parent** to be hit, that `mpirun -np 4 rhoSimpleFoam -parallel` **contains the string
`rhoSimpleFoam`**, and therefore that **a pattern kill using `-f` catches `mpirun` itself where
`-x` would not.** That is exactly the command that was run. **The prediction is confirmed, and
it was a prediction and not a reading of a confession.**

**`pkill -f` matches the full command line of every process on the box.** The pattern carried
no cwd, no pid and no session: it said *"kill anything on this machine whose command line looks
like mine"* — **and a graded M6 run looked like its because it is the same solver.**

**NOTHING PHYSICAL IS LOST AND NO NUMBER IS SUSPECT.** Both stops were external `SIGTERM`s
delivered to healthy solutions — §A14.1's own capture shows `LimitedCells` 0, ν̃ max 0.0214 and
Cl 0.2505 at the final iteration. **The 800 checkpoint stands, every graded L3/L2 number
stands, and no result in this document is contaminated. What was lost is wall time, twice.**

**The hazard is stopped at source**, reported by that lane: name matching abandoned entirely,
every process now identified by `/proc/<pid>/cwd` and `/proc/<pid>/cmdline` **re-read at the
moment of signalling**, an explicit pid list derived from cwd, and the cwd-scoped stopper being
written as a script so the next lane cannot reach for `pkill` out of habit. It also declined to
restart anything of its own and **explicitly refused to touch this case directory.**

**So the resume proceeds with GAMG restored and no numerics change**, exactly as §A14.4
registered **before** the actor was known — which is the point: **the withdrawal was made on
the control's evidence, not on the confession's.**

**One physics correction carried so it does not propagate:** that lane's own SIGFPE was **not**
this document's transonic startup transient. Its line was `Solving for h: solution
singularity` — under `sensibleEnthalpy` the energy variable is **`h`** and its
`relaxationFactors` named only **`e`**, so that matrix had no diagonal boost. **Same stack,
different disease** (`MONITOR_STANDARD` v1.14 member 12). **Nothing in this document rests on
that relay.**

---

# ADDENDUM 15 — 2026-09-13. **THE FREEZE-TIME SEPARATION CHECK, APPLIED TO THIS REGISTRATION WHILE L1 IS IN FLIGHT. IT PASSES, AND THE REASON IT PASSES IS NOT A DESIGN CHOICE.**

**v1.14 → v1.15. Lines whose number changed above this section: 0.** No band, threshold, cap or
label moves. **This addendum changes nothing and gates nothing; it records a check and its
result.**

The cfd supervisor made two questions binding for this team at freeze time
(`MONITOR_STANDARD.md` v1.15): **can any threshold be MET BY ARITHMETIC IDENTITY rather than
exceeded by construction, and can any registered guard FIRE DURING CORRECT ROUTINE USE?**
This registration is in the bounded **live set** — L1 is running and its shock rows are
pending — so it is checked now rather than swept later.

## A15.1 — QUESTION 1, AND IT HAD A REAL CANDIDATE

🔴 **B2 looked like a textbook instance and had to be measured, not waved through.** The band is
`|x_shock_cfd − x_shock_exp| ≤ Δ_local`, and **both sides are built from the same orifice
positions**: D1 puts `x_shock` at the **midpoint** of an orifice interval, and `Δ_local` **is
that interval's width**. **So if the CFD shock lands one interval away from the experiment's,
the difference is the adjacent-midpoint spacing — and on a UNIFORM grid that equals the
interval width EXACTLY**, landing on a `≤` boundary and passing **by arithmetic identity rather
than by measurement.**

**And the frozen document describes η = 0.90's spacing as `0.0400 c, uniform across
0.34→0.90`.**

**Measured from the reference file itself, upper surface, aft of x/c = 0.20:**

| station | orifices | distinct interval widths (first six) | midpoint-steps **exactly** equal to an adjoining width |
|---|---|---|---|
| η = 0.65 | 15 | 0.04955, 0.04973, 0.04984, 0.04995, 0.05013, 0.05014 | **0 of 13** |
| η = 0.90 | 20 | 0.03779, 0.03963, 0.03970, 0.03973, 0.03977, 0.03981 | **0 of 18** |

**QUESTION 1: CLEAN. B2 cannot be met by arithmetic identity.**

🔴 **But the reason is an empirical accident, not a design decision, and that distinction is
the whole value of having asked.** The grid is **nominally** uniform and **not exactly** so —
the widths differ in the fourth decimal, and **that irregularity is the only thing breaking the
identity.** Had ONERA drilled its orifices on an exact 0.0400 pitch, **this band would have had
a boundary reachable by construction**, and nobody would have noticed because the gate would
have read `PASS`.

**A second, smaller thing falls out and is recorded rather than filed as alarm:** the frozen
prose *"0.0400 c, uniform"* is a **rounding** — the true widths span **0.03779 to ≈0.0398**.
**No gate moves**: `grade_m6_agard_cp.py` measures Δ from the file at run time and asserts it
against the registered table to **±0.0125**, which contains the spread with two orders of room.
The prose is imprecise; **the instrument is not.**

## A15.2 — QUESTION 2: CAN ANY REGISTERED GUARD FIRE DURING CORRECT ROUTINE USE?

| guard | threshold | observed on healthy runs | separation |
|---|---|---|---|
| **LC-1** | `CellsPercent > 2.0` for 20 consecutive reported lines | **0.00 %** on L3, L3_NORAMP, L3_TVD, L2-TVD and L1 | **complete — it has never fired on a healthy run** |
| **LC-2** | `bounding nuTilda` max > **1e6** | **0.021 – 0.073** | **~7 orders of magnitude** |
| **C2 / S1** | rise ≥ 0.212 (η 0.65), ≥ 0.320 (η 0.90) | 0.069 – 0.103 | far from the boundary; no identity risk |
| 🔴 **IC-4** | y⁺ max **≤ 2.0 on L1**, ≤ 5.0 on L2/L3 | L3 **2.55**, L2 **1.21**, **L1 UNMEASURED** | **the tightest limb in the document** |

**QUESTION 2: CLEAN, with one limb named.** **IC-4's L1 threshold of 2.0 is the only registered
number in this document whose margin is not yet demonstrated.** The family halves y⁺ per
refinement (measured: L3 2.5455 → L2 1.2144, ratio 2.096), so L1 is expected near **0.6** — but
**expected is not measured, and this addendum does not pretend otherwise.** **The threshold is
NOT changed**: it was registered before compute and it stays, and if L1 lands above 2.0 the
level is `NOT A RESULT` on IC-4 exactly as written.

## A15.3 — WHY A CLEAN RESULT IS WORTH A RECORD

**Both questions were answerable by reading the document and one measurement of the reference
file. Neither cost compute.** That is the supervisor's point: **this is discoverable at freeze
time, where it is free** — and the retrospective sweep it replaces is the kind of verification
that earns an objection.

**And the null result is the informative one here.** B2 was a genuine candidate — same orifice
grid on both sides of the inequality, a `≤` comparison, and a frozen description saying
*uniform*. **It passes only because the real hardware is irregular.** A check that only ever
reports problems teaches nothing about the cases it clears; **this one names exactly how close
this band came.**

---

# ADDENDUM 16 — 2026-09-13. **I RAISED AN ALARM AGAINST MY OWN LIVE GATE AND THEN DEFUSED IT BY TRACING WHICH QUANTITY THE ASSERT ACTUALLY CONSUMES. IT IS NOT A LIVE RISK.**

**v1.15 → v1.16. Lines whose number changed above this section: 0.** Nothing moves. **This
addendum corrects two numbers and retracts an alarm this lane raised itself.**

## A16.1 — CORRECTED: THE PROSE-VERSUS-FILE ERROR, WHICH IS MUCH LARGER THAN RELAYED

A figure of *"up to 5.5 % on Δ at η = 0.65"* was relayed for what a grader would suffer had it
taken the nominal from the prose instead of measuring the file. **Measured here, it is neither
that size nor that station:**

| station | registered nominal | **true interval widths** | **max error using the nominal** |
|---|---|---|---|
| η = 0.65 | 0.0500 | **0.04955 – 0.07011** | **28.68 %** |
| η = 0.90 | 0.0400 | **0.03779 – 0.04787** | **16.44 %** |

The widest deviations come from the **aft** intervals — and **the frozen registration already
said so**: §5 B2 records *"widening to 0.060–0.070 c aft of 0.65"*. **The prose warned about
exactly the intervals that break the nominal.** The principle stands and is strengthened:
**the instrument reads the file, and that is the only reason the imprecise prose is harmless.**

## A16.2 — 🔴 THE ALARM I RAISED, AND WHY IT IS WRONG

Those widths exceed the grader's own assert tolerance. `BAND_B2_ASSERT_TOL = 0.0125` against a
registered 0.0500 admits **0.0375 – 0.0625**, and at η = 0.65 **four of fourteen intervals fall
outside it**:

| interval | width | \|w − 0.0500\| |
|---|---|---|
| 0.71034 → 0.78008 | 0.06974 | 0.01974 |
| 0.78008 → 0.85001 | 0.06993 | 0.01993 |
| 0.85001 → 0.92012 | 0.07011 | **0.02011** |
| 0.92012 → 0.98611 | 0.06599 | 0.01599 |

🔴 **And they sit at x/c 0.71–0.99 — exactly where every level's detected shock has landed**
(L3 and L3_TVD at 0.9531, L2 at 0.8851). That looked like a live trap waiting for L1: D1 picks
an aft interval, the assert fires, and a sound run grades `NOT A RESULT` on bookkeeping.

**IT IS NOT. I TRACED WHICH QUANTITY THE ASSERT CONSUMES INSTEAD OF REASONING FROM THE WIDTHS.**
`grade_m6_agard_cp.py`:

- **line 307** — `x_sh_e, dloc, _, _, rise = d1_shock_from_curve(ref_pairs)` → **`dloc` is the
  EXPERIMENTAL interval width.**
- **line 322** — `if abs(dloc - reg) > BAND_B2_ASSERT_TOL:` → **the assert is on the
  EXPERIMENTAL Δ.**
- **line 318** — the CFD's own `dloc_c` is computed and **never used** by the assert or the band.

**The experimental Cp data is identical for every level and every run, so `dloc` is INVARIANT:
0.05014 at η = 0.65 and 0.04024 at η = 0.90, both comfortably inside ±0.0125 — confirmed in all
eight shock rows already graded.** The assert is **a property of the reference file alone** and
**cannot fire for L1, or for any level, ever.**

**So the alarm is retracted, and the retraction is the point.** I computed the widths of
intervals D1 would select **only if the experimental curve's largest Cp rise sat there** — it
does not; it sits at **x/c 0.47517**. **I read a correlate (interval widths in the aft region,
where the CFD shock happens to land) instead of the quantity the rule names (the width at the
interval the EXPERIMENTAL D1 selects).** That is tonight's own mechanism, committed by the lane
that drafted the clause about it, on the third consecutive occasion — and it was caught the
same way as all the others: **by reading the artifact, which here meant the grader's source
rather than the data.**

**One genuinely dead value, noted and not dressed up:** `dloc_c` at line 318 is assigned and
never read. **Harmless** — the band and the assert both use the experimental Δ by design — but
it is a value a future reader could mistake for the one in force.

## A16.3 — WHAT REMAINS TRUE FOR L1

**Nothing in A15 changes.** B2 cannot be met by arithmetic identity (0 of 13 and 0 of 18), the
guards keep their separation, and **IC-4's y⁺ ≤ 2.0 on L1 remains the one registered number
whose margin is undemonstrated.** At endTime this lane reports **C2's two shock-rise numbers
against 0.212 and 0.320 first**, then **C1**, then **IC-4's measured y⁺** — the last because it
is the gate whose margin has not been shown on that level.
