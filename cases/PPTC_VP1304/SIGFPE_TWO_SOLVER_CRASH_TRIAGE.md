# PPTC VP1304 — TWO `simpleFoam` SIGFPEs ON ONE MESH, AND WHY A THIRD LINEAR SOLVER IS NOT TRIAGE

**FILING STATUS, 2026-09-14 — NOT IN `docs/NUMERICS_KNOWLEDGE.md`, AND NOT IN `docs/LESSONS.md`.**
Both registers refuse an append today. `scripts/append_record.py --dry-run` exits **7**
(`EXIT_REFUSED_UNPARSEABLE_SHAPE`, the D549 shape audit) on each:

| record | exit | lines that match the id shape and yield no id |
|---|---|---|
| `docs/NUMERICS_KNOWLEDGE.md` | **7** | `HEAD:docs/NUMERICS_KNOWLEDGE.md:6723` — `**N-D44 EVIDENCE ADDENDUM — 2026-09-10, same day — …` |
| `docs/LESSONS.md` | **7** | `HEAD:docs/LESSONS.md:27929` — `## L-570 (second block) — …`; `HEAD:docs/LESSONS.md:28255` — `## L-573 (second block) — …`; `HEAD:docs/LESSONS.md:28306` — `## L-<n> block count      : 576` |

The tool names its own repair — *"one of TWO REGISTER EDITS in `scripts/append_record.py`,
never an edit to the record"*. **That instrument belongs to verification, and the cfd team has
not touched it.** This document is filed beside the case so the block is visible rather than
silent; when the registers reopen, the finding below is what is owed to
`docs/NUMERICS_KNOWLEDGE.md`.

---

## 1. THE TWO CRASHES

Both ran in one case directory,
`/home/ubuntu/certonomous-runs/PPTC_VP1304/dead_lever_SMOKE360_J0.7985/registered`, OpenFOAM
**v2606** build `_481094f-20260618`, 4 ranks, `trapFpe` enabled, on the mesh symlinked at
`constant/polyMesh -> /home/ubuntu/certonomous-runs/PPTC_VP1304/SMOKE360_J0.7985/constant/polyMesh`
(**19,700,035 cells**, sum of the four `Number of cells` rows at
`…/registered/log.decomposePar:54,63,73,83`).

| | run A | run B |
|---|---|---|
| artifact | `…/registered/log.simpleFoam.GAMG.SIGFPE` | `…/registered/log.simpleFoam.PCG` |
| start (`Time :` header) | **16:33:31**, 2026-09-13 | **16:45:29**, 2026-09-13 |
| PID | 1543762 | 1555215 |
| signal | **8, Floating point exception** (`:113`) | **8, Floating point exception** (`:165`) |
| rank that took it | **2** | **0** |
| died at | **`Time = 1`** | **`Time = 5`** |
| `p` solver | GAMG | `PCG`/`DIC`, `maxIter 100` |

Full paths are `/home/ubuntu/certonomous-runs/PPTC_VP1304/dead_lever_SMOKE360_J0.7985/registered/log.simpleFoam.GAMG.SIGFPE`
and `…/log.simpleFoam.PCG`.

### 1.1 Run A — the top OpenFOAM frame, quoted

`log.simpleFoam.GAMG.SIGFPE:101`:

> `[2] #3  Foam::GAMGSolver::scale(Foam::Field<double>&, Foam::Field<double>&, Foam::lduMatrix const&, Foam::FieldField<Foam::Field, double> const&, Foam::UPtrList<Foam::lduInterfaceField const> const&, Foam::Field<double> const&, unsigned char) const`

reached through `Foam::GAMGSolver::Vcycle(...)` (`:102`), `Foam::GAMGSolver::solve(...)` (`:103`),
**`Foam::fvMatrix<double>::solveSegregated(Foam::dictionary const&)`** (`:104`) and
**`Foam::fvMesh::solve(Foam::fvMatrix<double>&, Foam::dictionary const&) const`** (`:106`).
The matrix type is **`fvMatrix<double>`** — a scalar equation. In `simpleFoam` the scalar
equation solved immediately after `Ux`, `Uy`, `Uz` is **pressure**. `GAMGSolver::scale` forms a
ratio of two inner products and divides by it.

### 1.2 Run B — the top OpenFOAM frame, quoted

`log.simpleFoam.PCG:154`:

> `[0] #3  Foam::symGaussSeidelSmoother::smooth(Foam::word const&, Foam::Field<double>&, Foam::lduMatrix const&, Foam::Field<double> const&, Foam::FieldField<Foam::Field, double> const&, Foam::UPtrList<Foam::lduInterfaceField const> const&, unsigned char, int)`

reached through the member `symGaussSeidelSmoother::smooth` (`:155`),
`Foam::smoothSolver::solve(...)` (`:156`) and
**`Foam::fvMesh::solve(Foam::fvMatrix<Foam::Vector<double>>&, Foam::dictionary const&) const`**
(`:158`). The matrix type is **`fvMatrix<Vector<double>>`** — a vector equation, i.e.
**momentum**. Gauss–Seidel's first act on each row is a division by the diagonal.

**Both readings VERIFY against the traces. Two different linear solvers, two different
equations.**

---

## 2. THE CONTROL THAT MAKES THE COMPARISON SINGLE-VARIABLE

The three momentum lines of `Time = 1` are **byte-identical** between the two logs — `cmp` of
lines 94–96 of each returns 0:

> `smoothSolver:  Solving for Ux, Initial residual = 0.9999809, Final residual = 0.005658409, No Iterations 6`

and the `Uy` and `Uz` lines likewise. The two runs therefore differ **only** in the pressure
solver, and every difference between them is attributable to that one change.

---

## 3. THE FALSIFIER — CHECKED, AND IT DOES NOT COME BACK CLEAN IN BOTH DIRECTIONS

The alternative to a degenerate-geometry explanation is a **field** explanation: a diverging
solution produces an Inf/NaN that poisons the diagonal, and the mesh is innocent. The two runs
answer that question **differently**, and saying so is the point of this section.

**Run A points at geometry.** It died in `Time = 1` with **zero** `Solving for p` lines and
**zero** `bounding` lines in the whole file (`grep -c`, on the one named artifact). It never
printed a pressure residual, so the FPE landed inside the *first* pressure solve, with the
momentum residuals healthy and no field pathology of any kind on the record. Early and clean.

**Run B, taken alone, points at the field.** It survived four iterations and the field came
apart while it did. Worst values in the file, by `sort -g | tail -1` / `head -1` on the one
named artifact — the extremum question, not the frequency question:

| quantity | worst value in `log.simpleFoam.PCG` | line |
|---|---|---|
| `time step continuity errors : sum local` | **1.6315773e+17** (from 0.14583691 at `Time = 1`) | `:141` |
| `bounding omega, min` | **−8.5313877e+09** | `:143` |
| `bounding k, min` | **−3.3047978e+09** | `:145` |

A `bounding` cascade is present and escalating from `Time = 1` onward (`:101`, `:103`, `:115`,
`:117`, `:129`, `:131`, `:143`, `:145`). Late and dirty. **The proximate arithmetic of run B's
SIGFPE is not established as a division by a zero diagonal** — at magnitudes of 1e+17 and 1e+22
an *overflow* inside the smoother is at least as consistent with the trap, and `FOAM_SIGFPE`
traps overflow and invalid as well as divide-by-zero. This record does not claim it was a zero
diagonal, because that was not measured.

### 3.1 The discriminator that closes the question anyway

The field explanation for run B is **true and downstream**, not a competing root cause, and one
line settles it — `log.simpleFoam.PCG:97`, the **first** pressure solve of `Time = 1`, before
any `bounding` line and before any continuity error had been printed:

> `DICPCG:  Solving for p, Initial residual = 1, Final residual = 1.7856178, No Iterations 100`

The residual **grew by 1.79×** across 100 iterations. The second solve grew again, 0.33124386 →
0.55437931 (`:98`). The largest amplification in the run is at `:139`, 0.99998897 → **3.8260438**
(3.83×). **A DIC-preconditioned conjugate gradient cannot amplify the residual on a symmetric
positive-definite matrix** — monotone reduction in the A-norm is a property of the method. The
amplification is therefore a property of the **matrix**, measured at iteration 1 on pristine
initial fields, before any field could have been poisoned.

**Outcome of the falsifier: the field explanation accounts for the *timing and location* of run
B's crash and is rejected as its *root*. Run A is unambiguous — iteration 1, healthy residuals.
Run B's crash is a consequence of a pressure operator that was already non-SPD at iteration 1.**

---

## 4. THE MESH — AND A CORRECTION TO THE CITATION THIS TRIAGE WAS FIRST GIVEN

**The SPD gate's `A_PP = −3.422338033e+04` at witness cell 1,858,792
(`verification/runs/PPTC_VP1304_runs/HUB_ROOT_MESH_RUNG_RESULTS.md:154`, commit `0d37987c8`) was
NOT measured on the mesh that crashed.** That row is the SHAFT-4 rung's rebuilt mesh, **19,829,120
cells** (same file, `:122`, `:224`; its `constant/polyMesh/points` is 805,695,743 bytes). The two
SIGFPE runs ran on **19,700,035** cells. Citing it here would be a cross-mesh comparison.

**The same-mesh measurement exists and is this one.**
`/home/ubuntu/certonomous-runs/PPTC_VP1304/spd_gate_baseline2_status` (mtime 2026-09-13 17:21),
cited in the repository at `verification/runs/PPTC_VP1304_runs/CFM1_READER_ARMING.md:230`:

| quantity | value |
|---|---|
| cells / faces / internal faces | 19,700,035 / 59,833,297 / 59,079,066 |
| internal faces with `w_f <= 0` (or `S_f·d_f = 0`) | **953** |
| cells with `A_PP <= 0` | **480** |
| **witness cell index** | **1,334,283** |
| **its `A_PP`** | **−5.240107530e+01** |
| witness cell centre | (0.131803, −0.004472, 0.004606) m |
| geometry control vs OpenFOAM `0/cellVolume` | max rel. diff **4.998e-08**, negative volumes **316 / 316** — **PASSED** |
| verdict | **GATE FAIL** |

Do **not** cite the sibling artifact `…/spd_gate_baseline_status` (17:12) for any of this: its
geometry control reports a max relative cell-volume difference of **2.144e+09** and 9,809,857
negative volumes against OpenFOAM's 316 — that is the stale-points reader signature, and the
verdict beside it is void in either direction.

### 4.1 Same-mesh identity, proven by bytes rather than by cell count

`SMOKE360_J0.7985/constant/polyMesh` is F360_coarse's connectivity plus the repaired point
array. `cmp` returns 0 on all five:

- `SMOKE360_J0.7985/constant/polyMesh/points` ≡ `F360_coarse/0/polyMesh/points` (798,680,547 bytes);
- `faces`, `owner`, `neighbour`, `boundary` ≡ `F360_coarse/constant/polyMesh/*`.

The geometry files carry mtimes 16:27:49–16:27:53, i.e. **before** both crashes (16:33:31,
16:45:29) and before the gate run (17:21); nothing rewrote them in between.
`F360_coarse/constant/polyMesh/points` is a *different* array (799,096,490 bytes, 20,518,324
entries, 10,620 orphan points) and `spd_gate.py` **refuses** it outright — the refusal is quoted
at `CFM1_READER_ARMING.md` §4. It is the only consistent 19.7 M staging on disk.

**Provenance limit, stated rather than glossed:** `spd_gate_baseline2_status` was produced by a
prior lane. `CFM1_READER_ARMING.md:236-241` already records that no lane has witnessed that run
or asserted the identity of the binary that wrote it. The mesh identity above is proven; the
gate invocation's provenance is cited, not re-witnessed.

---

## 5. THE CONSEQUENCE — DO NOT GO SOLVER-SHOPPING ON THIS MESH

Two linear solvers, two equations, one mesh, and the pressure operator is measurably not SPD at
iteration 1. Swapping the solver moved **where** and **when** the trap fired and changed nothing
about the system being solved: GAMG died at iteration 1 inside `scale`; PCG delayed the crash by
four iterations and died at iteration 5 inside the momentum smoother, having amplified the
pressure residual on the way.

> **A third linear solver is not triage. It is a search for one that fails quietly.** A solver
> that gets a four-gate-failing mesh through a pressure solve is evading the mesh gate, not
> passing it, and would buy a `KT` that converges and means nothing.

That is not this lane's invention: the prior lane declared it **before** running the PCG test —
`/home/ubuntu/certonomous-runs/PPTC_VP1304/stage360_status`, block `=== DECLARED BEFORE THE TEST
IS RUN, NOT AFTER (16:52Z) ===` — and every number the PCG run produced is **NOT A RESULT** by
that pre-declaration, including the two force values (`−3.96081259e+10 N`, `−7.47301220e+22 N`)
which are overflow, not thrust, and do not trigger the registered negative-`KT` rotation-sign
clause.

The registered solver for this act remains GAMG per pre-registration §7. Nothing here amends it.

---

## 6. THIS IS ARGUABLY A HARDER BLOCKER THAN THE MRF-ZONE ITEM

The open MRF blocker at `cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md:1977` —
*the MRF `cellZone` is not proven on the mesh that will run* — is a **dictionary-and-zone**
question. It is repaired by writing a `cellZone` and re-running `topoSet`: a `topoSet`
invocation, not a mesh rebuild.

**These two SIGFPEs are the mesh itself.** 480 cells with `A_PP <= 0` and 953 faces with
`w_f <= 0` are produced by 316 negative-volume cells and inverted face pyramids; no dictionary
edit removes them and no solver setting tolerates them. Repair means **re-meshing**, which is
the expensive end of the ladder.

**And the MRF lever was not the obstacle in these two runs.** Both logs print
`creating MRF zone: MRF1` at line 79, and the zone is live on this mesh — `cellZoneSet MRFzone
now size 11412958` (`/home/ubuntu/certonomous-runs/PPTC_VP1304/stage360_status`, `topoSet_rc=0`
block; independently confirmed by the LEVER 0 audit at
`…/SMOKE360_J0.7985/DEAD_LEVER_AUDIT.txt`). The `:1977` blocker concerns the **production** mesh,
not `SMOKE360_J0.7985`. A successor must not read this record as evidence either way about that
blocker.

---

## 7. WHAT THIS RECORD DOES NOT SAY

- It mints **no new verdict**. The act's state on this mesh was already declared **BLOCKED** by
  the prior lane (`stage360_status`, *"VERDICT: BLOCKED. simpleFoam cannot complete one pressure
  solve on this mesh."*). This document records the triage behind that word; it does not restate
  it as a fresh grading.
- It does **not** establish the proximate arithmetic of run B's trap (§3). Divide-by-zero and
  overflow are both consistent with the evidence on disk, and neither was measured.
- It says nothing about cfMesh, about `PRISM_A2_absthick`, or about the SHAFT-4 rebuilt mesh
  beyond the correction in §4.
- **No compute was run for it.** No solver, no mesher, no mesh reader was launched: the work is
  reading five artifacts, two `append_record.py --dry-run` calls and five `cmp` invocations on
  already-written files. The lane's own spend is single-core file I/O and was not separately
  instrumented; it is **not** reported as a measured core-minute figure. The 16.7 core-min charged
  as WASTE for run A, and run B's `wall_s=534` at 4 ranks (**35.6 core-min**), are the prior lane's
  figures and are recorded in `stage360_status`, not re-derived here.
