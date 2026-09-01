# A1-WR — WALL-RESOLVED ALPHA POLAR, BOTH REGIMES — PRE-REGISTRATION

**Item:** `A1WR` — NACA0012 α = 0…18° polar on a **wall-resolved** mesh family,
incompressible (`DASimpleFoam`) and compressible (`DARhoSimpleFoam`).
**Team:** dafoam **Lane:** lab-lane **Written:** 2026-09-01
**Status at freeze:** NO COMPUTE HAS BEEN SPENT ON THIS ITEM.
**Verdict class:** `FEASIBILITY` — see §1.3. **Verdict ceiling:** `GATE REACHED`.

---

## 0. THE ORDER THIS ITEM ANSWERS, AND THE MESH DECISION

Sanaa, at `6d4acd89`, verbatim:

> the sweeps must be done at converged mesh. not coarse mesh... Dafoam team
> launches the sweep at fine mesh for both compressible and incompressible.

and, in the same turn:

> if not yet, state the honest ETA rather than launching on an unproven mesh.

Her reasoning, as relayed: on the coarse mesh nobody can tell whether the 9°
break is physics or resolution.

### 0.1 The obvious candidate mesh is wrong, twice

It was suggested that the wing ladder's **A2-GC L2 (~100k cells)** is the natural
fine mesh. It is not, for two independent reasons, both established before this
document was written:

1. **A2-GC L2 is 306,432 cells, not ~100k.** `cgns_utils coarsen`/`refine` are
   factor-2-only, so that ladder is quantised to powers of two and **there is no
   ~100k level on it at all**: the reachable family is 4,788 / 38,304 / 306,432 /
   2,451,456.
2. **Decisively: A2 is the 3-D MACH Tutorial Wing. The α sweeps ran on A1, the
   2-D NACA0012 aerofoil.** Moving to A2-L2 is not "a finer mesh" — it is a
   different geometry, a different dimensionality and a different case. A polar
   on the 3-D wing is not comparable to the A1 polar in any way, and presenting
   it as the fine-mesh version of the same sweep would be a category error.

**And there is no fine A1 mesh anywhere in the tree.** A1 is 4,032 cells, full
stop (`cases/dafoam/ladder-a/A1_naca0012_incompressible.json`, `mesh_cells: 4032`).
This item therefore **builds** the mesh; it does not select one.

### 0.2 The deeper point, which is Sanaa's own reasoning

The existing A1 mesh is **wall-modelled**, at y+ measured **16.7–92.4**
(`cases/dafoam/ladder-a/A1/feasibility_aoa_polar/AOAI_PREREGISTRATION.md:223-225`).
**Refining it in-plane would not settle whether the 9° break is physics or
resolution, because a wall-modelled mesh cannot resolve a separating boundary
layer at ANY angle, no matter how many cells it carries in the chord direction.**

Her §0 says near-wall spacing scales with r and y+ stays under 1 where the case
is wall-resolved. The mesh this sweep needs is therefore **wall-resolved,
y+ < 1** — which is not "more cells" but a change of near-wall treatment.
Getting this wrong would spend real compute to produce a second polar nobody can
interpret, which is the outcome her order exists to prevent.

**This item's registered position: more cells alone would have been a wasted
run. The wall treatment is the variable that matters, and the cell count follows
from it.**

---

## 1. SCOPE, AND WHAT THIS ITEM MAY AND MAY NOT CONCLUDE

### 1.1 What runs

Two arms, identical mesh, identical numerics, differing only in solver and
free-stream state:

| arm | solver | U0 | state | Re_c |
|---|---|---|---|---|
| `A1WR-I` | `DASimpleFoam` | 10 m/s | ν = 1.5e-5 | 6.667e5 |
| `A1WR-C` | `DARhoSimpleFoam` | 100 m/s | p0 = 101325, T0 = 300, ρ0 = 1.176829, ν_w = 1.568622e-5 | 6.375e6 |

19 points per arm, α = 0, 1, 2, …, 18°, **continuation upward**, with **cold
controls at α = 4, 14, 17** — exactly the design the coarse sweeps registered.
That design worked, and its cold controls are what proved the 9° failure was a
property of the operating point and not of the chain.

### 1.2 The Reynolds ratio is 9.563, and it drives the mesh

The two arms are **not** at the same Reynolds number; the ratio is **9.563**.
This is the "tenfold Reynolds difference" the coarse result already reported.
Its consequence for THIS item is §2.3 and is the single most important design
decision in this document: **the compressible arm sets the wall spacing.**

### 1.3 Verdict class: `FEASIBILITY`, and why

**This mesh family's own grid convergence is PENDING.** No Roache triple has
been run on it. Therefore **no band exists on any number this item produces**,
and no value from it may be graded `PASS` against a threshold. The item is
registered `FEASIBILITY` for exactly the reason the coarse sweep was: it reports
**convergence behaviour and measured y+**, not physics.

The generator (§2) is built to seed that triple later — L1/L2/L3 with a
registered r = 2 — but running it is a **separate rung** (`A1WR-GC`), not this
one. **Nothing in this item may be quoted as a grid-converged result.**

### 1.4 The verdict ceiling

`VERDICT_CEILING = GATE REACHED`, reason: an item whose subject mesh has no grid
convergence cannot publish `PASS`. Composition is D19M's repaired `compose_item`
(`cases/dafoam/ladder-a/A1/curriculum_D19M/d19m_grade.py:1525`), composing from
**`verdict_before_ceiling`**, and testing the hard-gate list for **both**
`GATE FAIL` and `NOT A RESULT` — the `D19M-COMPOSE-DEF-1` repair. A hard gate
reporting `NOT A RESULT` must not fall through to `PASS` and then be capped to
`GATE REACHED`; that inverts `CLAUDE.md` rule 5's direction.

---

## 2. THE MESH FAMILY — REGISTERED ON THE FACE

Generator: **`a1wr_genmesh.py`** in this directory, sha recorded at freeze (§11).
Derived from the DAFoam tutorial `genAirFoilMesh.py`; the airfoil profile
handling and pyHyp option block are the tutorial's, the R-parameterisation and
the wall-resolved `s0` are new.

### 2.1 One refinement factor, and everything scales off it

**Registered refinement ratio: r = 2, in all three directions** — chordwise,
wall-normal cell count, and near-wall spacing.

| | L1 (R=1) | L2 (R=2) | L3 (R=4) |
|---|---|---|---|
| chordwise spacings dX1/dX2/dXMax | ÷1 | ÷2 | ÷4 |
| clustering ratio Alpha | 1.2 | 1.09545 | 1.04664 |
| blunt-TE points NpTE | 5 | 10 | 20 |
| wall-normal cells | 64 | 128 | 256 |
| first cell height s0 | 3.0e-6 | 1.5e-6 | 7.5e-7 |
| **marchDist (far field)** | **20.0** | **20.0** | **20.0** |
| implied growth ratio | 1.2510 | 1.1179 | 1.0572 |

**The clustering ratio scales as Alpha^(1/R).** Without this the leading and
trailing edges would refine more slowly than the mid-chord and the family's
effective refinement ratio would not be r. This is **L-430** — "a generator
parameter that does not scale with the ladder builds three clean meshes and a
meaningless observed order" — and it is the reason the generator carries a
`--selfcheck` that drives R = 1, 2, 4 and **refuses at exit 2** if any
must-scale parameter is equal at two levels, or if `marchDist` moved.

**The selfcheck was driven before this document was frozen and returned rc 0**,
including its mutation control: it forces `s0` at L2 to L1's value, asserts the
mutation actually landed (refusing if writing the value left it unchanged), and
requires the equality predicate to fire on it. A control that silently no-ops
proves nothing — three of the AoA lane's eleven controls were written against
fixture literals and no-opped on real bytes, one of them the zero-passing
control.

### 2.2 Far-field extent, growth ratio and trailing edge — stated, because at stall the wake matters as much as the boundary layer

- **Far-field extent: marchDist = 20.0 chords, HELD FIXED across all levels.**
  It is a physical choice, not a resolution parameter; if it moved between
  levels the three meshes would not be the same problem.
- **20 chords is on the small side for a lift polar.** Common practice is 50–100
  chords, and blockage at 20 chords biases CL by order a few percent.
  **It is retained deliberately and the confound is registered here**: the
  coarse sweeps ran at marchDist = 20, and changing far-field extent, in-plane
  resolution and wall treatment simultaneously would make a fine-vs-coarse
  comparison uninterpretable in a third way. **The comparison Sanaa asked for
  survives only if resolution and wall treatment are the ONLY things that move.**
  A far-field sensitivity study is registered here as a named successor rung
  (`A1WR-FF`) and is **not** part of this item.
- **Growth ratio ceiling: 1.35, registered.** A level whose implied growth ratio
  exceeds 1.35 is refused before it runs. All three levels pass (1.2510 /
  1.1179 / 1.0572).
- **Trailing edge: blunt, closed by NpTE linear segments, NpTE scaling with R
  (5/10/20).** The tutorial truncates PS and SS at ~99.8 % chord and closes the
  gap. A blunt TE whose point count did not scale would be the L-430 defect in
  precisely the region where the wake leaves the body.

### 2.3 The compressible arm set the wall spacing, and one mesh serves both arms

y+ for a given wall spacing is roughly an order of magnitude larger on the
compressible arm (Re ratio 9.563). **A mesh sized to give y+ < 1 at U = 10 gives
y+ of order 1.5–2 at U = 100 on the same cells.** The compressible arm is
therefore the binding constraint and this family is sized on it.

**Both arms share ONE mesh family deliberately.** Building a separate mesh per
regime would confound the regime comparison — the finding under test is that
both arms broke at the same angle *to the degree* across a tenfold Reynolds
difference, and that comparison survives only if the discretisation is
identical. The incompressible arm is consequently over-resolved near the wall.
That costs iterations; it does not cost correctness, and it is disclosed here
rather than discovered later.

### 2.4 Which level the sweep runs on

**The sweep runs on L3** (s0 = 7.5e-7, 256 wall-normal cells, growth 1.0572).
L1 and L2 are built in the same stage so the triple rung `A1WR-GC` can be run
without rebuilding, and so that **all three levels are wall-resolved on both
arms** — which is what Sanaa's §0 asks when it says near-wall spacing scales
with r *and* y+ stays under 1. Predicted y+ at L1, the coarsest level, is 0.95
on the compressible arm: under 1, and only just. That is stated so a reader can
see the family was sized to keep the whole ladder wall-resolved, not just its
finest member.

Chordwise cell count is a **built** quantity — it emerges from the spline
interpolation, is printed by the build, and is **not asserted** here. Predicted
total cell count at L3 is of order 1.3e5; **the built figure is read off the
build log and the mesh, never from this document.**

---

## 3. y+ — PREDICTED HERE, MEASURED ON EVERY POINT, NEVER ASSERTED

### 3.1 The prediction, labelled EXTRAPOLATED

Sizing used Cf = 0.0576·Re^-0.2 with an estimated leading-edge factor and an
estimated incidence factor, anchored on the measured y+ 16.7–92.4 at s0 = 4e-3
on the existing wall-functioned mesh.

| | incompressible | compressible |
|---|---|---|
| predicted y+ at L3, α = 18° | ~0.06 | ~0.24 |
| predicted y+ at L2, α = 18° | ~0.12 | ~0.48 |
| predicted y+ at L1, α = 18° | ~0.24 | ~0.95 |

**EVERY NUMBER IN THIS TABLE IS A PREDICTION FROM A FLAT-PLATE CORRELATION AND
IS NOT EVIDENCE THAT THE MESH IS WALL-RESOLVED.** It is registered so the
measurement can be compared against something written down first.

### 3.2 Sizing was done at the HIGHEST α, not at α = 0

y+ rises with incidence, and a mesh sized at α = 0 will not hold at 18°. The
incidence factor above is applied at α = 18°, and the y+ probe (§5.1) is run at
**α = 18**, the binding point, not at a convenient one.

### 3.3 The measurement, and the gate on it

**y+ is MEASURED on every point of every arm and published**, via the OpenFOAM
`yPlus` function object, written per point. `G-YPLUS`:

- reports min / mean / **max** y+ on the wall patch for **every** α on both arms;
- **`GATE FAIL` if measured y+max ≥ 1.0 at any point**, with the point named;
- refuses at **exit 2** if the y+ field is absent, empty, or all-zero for a point
  whose primal produced a flow field — a y+ reader that reads zero everywhere is
  not evidence of a fine mesh (rule 3).

### 3.4 What happens if the measurement disagrees with the prediction — registered in advance

**If measured y+max ≥ 1, the wall-resolved claim is WITHDRAWN for the affected
points and the item reports that, with the measured values published.**

**The mesh is NOT re-cut until it passes.** A re-mesh-until-y+-passes loop is
result-shopping and is forbidden on this item. A y+ overshoot is a registered
outcome of this item, is reported as `GATE FAIL` on `G-YPLUS`, and any successor
mesh is a NEW rung with its own pre-registration.

---

## 4. WALL TREATMENT — THE CAPABILITY IS MEASURED IN THE IMAGE, NOT ASSUMED

**The question "can this image build and run a wall-resolved A1?" was answered
before this document was written, by reading the installed source, not by
recall.** Evidence, all read inside `dafoam/opt-packages:latest`:

1. **`useWallFunction` is a first-class DAFoam option**, read in
   `src/adjoint/DAField/DAField.C`. With it **True** (what both coarse sweeps
   ran, `aoa_runScript.py:49`) DAFoam sets the wall `nut` BC to
   `nutUSpaldingWallFunction` for SA models. With it **False**, at
   `DAField.C:1207-1230`, DAFoam sets the wall `nut` BC to
   **`nutLowReWallFunction`** with a wall value of 1e-14.
   **This is the supported wall-resolved code path in the installed build. It is
   not a substitution invented by this lane.**
2. **The branch fires only on patches of `type wall`.** The A1 `wing` patch is
   `type wall` (`constant/polyMesh/boundary`), so the branch will fire. A patch
   typed `patch` would have made `useWallFunction: False` a **silent** no-op —
   this was checked, not assumed.
3. **`nutLowReWallFunction` is present in the installed OpenFOAM v2506**
   (`libturbulenceModels.so`), alongside `nutUSpaldingWallFunction` and
   `nutkWallFunction`.
4. **DAFoam's SA does not hardcode a wall treatment.**
   `DASpalartAllmaras::correctNut` computes `nut_ = nuTilda_ * fv1` then calls
   `nut_.correctBoundaryConditions()` — it dispatches to whatever BC is set, so
   the option above is honoured by the model that actually runs.
5. **The low-Re formulation needs no different model.** Standard Spalart–Allmaras
   is already the integrate-to-the-wall formulation (the fv1 damping function is
   the near-wall treatment); unlike k-ε it has no separate low-Re variant. The
   wall BC on `nuTilda` for the wall-resolved case is `fixedValue uniform 0`,
   which is **already** what `0/nuTilda` carries.
6. **pyHyp and pySpline import and are functional in the image**, and `s0` is a
   direct pyHyp option — the y+ knob is a first-class generator parameter.

**Reader controls on the evidence above.** The symbol reader was driven with a
negative plant (a fabricated symbol name, correctly not seen) and a positive
plant. **The positive plant initially FAILED and is recorded as such**: querying
`libturbulenceModels.so` for `SpalartAllmaras` returned absent. That was a
misplaced control, not a blind reader — SA lives in
`libincompressibleTurbulenceModels.so`, where the same reader returns **218**
matching symbols. The control was re-placed and passes. **The failed first
placement is recorded because a control that was moved until it passed, without
the move being disclosed, is worthless.**

**Registered consequence:** the three wall-function readings above are `PRESENT`
verdicts, whose failure mode is a false positive, and the negative plant guards
that. No `ABSENT` verdict is load-bearing anywhere in this document.

### 4.1 What is NOT claimed

`useWallFunction: False` is exercised here on the **primal only**. This item runs
no adjoint, no optimiser, no FFD deformation and no CL trim. **Whether DAFoam's
adjoint differentiates correctly through `nutLowReWallFunction` is NOT tested by
this item and nothing here may be read as evidence about it.**

---

## 5. THE STAGED DESIGN — THREE STAGES, IN THIS ORDER

### Stage 0 — build the mesh family (L1, L2, L3)

`a1wr_genmesh.py --selfcheck` (must return rc 0), then `--level L1/L2/L3`, then
`plot3dToFoam -noBlank`, `autoPatch 30 -overwrite`, `createPatch -overwrite`,
`renumberMesh -overwrite`, then `checkMesh`. **Mesh building is compute and is
costed in §7.** Built cell counts, growth ratios and `checkMesh` output are
recorded; the growth-ratio ceiling of 1.35 is applied here.

### Stage 1 — the y+ probe, BEFORE the sweep is spent

**One point per arm, at α = 18 — the binding angle — on L3, run to a fixed 1,500
iterations regardless of convergence.** y+ is read from that state.

This is a **mesh-adequacy measurement, not a flow result**, and is registered as
such: at α = 18 the primal is not expected to converge (§6), and it does not need
to — the boundary layer only needs to be developed for y+ to be meaningful. No
CL, CD or convergence claim may be taken from Stage 1.

**If Stage 1 measures y+max ≥ 1 on either arm, Stage 2 does not launch**, and the
item reports the measured y+ with the wall-resolved claim withdrawn (§3.4). This
stage exists so that a mesh which fails its own premise costs ~65 core-minutes
instead of ~1,200.

### Stage 2 — the two sweeps

Per arm: one process, all 19 α ascending, `0/` reset from `0.orig` **once**
before the process starts so α = 0 is cold and every later point inherits its
predecessor's converged state in memory. Then the three cold controls, each in a
**separate case directory** with `0/` reset immediately before it, so they cannot
disturb Stage-2 artefacts.

**`0/` must be reset from `0.orig` for a genuinely cold start** — pyDAFoam renames
the converged solution back into `0/` when a primal finishes, so a "cold" start
that does not reset `0/` is not cold. This is carried unchanged from the coarse
sweeps, where it was verified on disk.

**No point is retried, relaxed, re-tuned or dropped.** A point that fails is
recorded with its residual history and the sweep continues, with every subsequent
point flagged `after_exception=TRUE`. **A missing point on a polar is a lie by
omission.**

Frozen numerics: `primalMinResTol = 1.0e-8`, `maxIter = 4000`, SA, settings
otherwise as the coarse sweeps. No relaxation, scheme or solver change is applied
to make a point converge.

---

## 6. THE STALL TRAP, IN BOTH DIRECTIONS

Carried from `AOAI_PREREGISTRATION.md` §4.2–§4.5, because both halves apply here
and the second half applies *more* on this mesh, not less.

**NO STALL ANGLE IS REPORTED BY THIS ITEM AND NONE MAY BE DERIVED FROM IT.**
`G-STALL` refuses at exit 2 on any output binding a stall word to a numeric
angle, with a mutation control proving it fires on a planted claim and does not
fire on the honest caveat.

**Direction 1 — a non-converged point is not evidence of stall.** It is evidence
that the steady solver stopped converging. Reported with its residual history.

**Direction 2 — a converged high-α point on an inadequate mesh is not evidence of
attached flow.** On the coarse mesh this was decisive: a 4,032-cell
wall-functioned mesh at y+ 16.7–92.4 cannot resolve a separated boundary layer at
any angle, so convergence and correctness were independent there.

**On THIS mesh the second direction changes shape but does not go away.** A
wall-resolved mesh *can* represent a separating boundary layer in a way the
coarse one could not — that is the entire point of building it. But:

- **the mesh's own grid convergence is PENDING** (§1.3), so no value carries a
  band;
- **2-D steady RANS with SA past stall is not a valid model of the flow**
  regardless of resolution — separation there is unsteady and three-dimensional,
  and a converged steady answer at 16° is a converged solution of a model that
  cannot represent the flow at 16°;
- **y+ < 1 is necessary, not sufficient.** Chordwise and wake resolution, and the
  20-chord far field (§2.2), all remain in play.

**THIS ITEM REPORTS CONVERGENCE AND MEASURED y+ ONLY**, and the reader prints
that scope statement on every run.

---

## 7. COST — REGISTERED BEFORE COMPUTE, WITH THE ANCHOR NAMED

### 7.1 The anchor NOT used, and why

**The A2-GC L1 "70 core-min" figure is not used.** A2-GC L1 **cap-stopped at
91.99 core-min against its 90 core-min cap** (`cost.txt`: `overrun=YES-RUN-STOPPED`,
rc 124), after three prior attempts (`ENVFAIL`, `MPIROOT`, `CAPSTOP`). **It did
not complete, so its true cost is above 91.99, not 70**, and a completed-run
figure cannot be read off it. Its one genuinely useful measured output is **peak
RSS 11,885.2 MiB (11.6 GiB)**, used for memory sizing only.

**Per-primal costing is also not used.** `ExecutionTime` is a cumulative process
clock; dividing it by a primal count is meaningless when a primal can converge in
under ten iterations. That error produced a ~19,000 core-min L3 projection that
was withdrawn as wrong by ~25× (`b7374db2`).

### 7.2 The anchor used

**s/SIMPLE-iteration, measured, at 4,032 cells, 1 rank:**

| arm | s/iteration | s/cell/iteration |
|---|---|---|
| compressible | 0.011500 | 2.852e-6 |
| incompressible | 0.011024 | 2.734e-6 |

**They agree to 4.3 %, so no solver-class correction factor is applied** — this
was checked rather than assumed, and the two figures are carried **separately**
rather than averaged, which is more honest and costs nothing.

### 7.3 The extrapolation — **LABELLED EXTRAPOLATED**

Scaling is by cell count (×32 from 4,032 to ~1.3e5) and by the higher iteration
count a wall-resolved mesh needs. Iteration scaling is taken as √(cell ratio) ≈
5.7, giving ~2,500 iterations for a converging point against the coarse sweeps'
389–502. Parallel efficiency at np = 4 is assumed 0.75.

| | incompressible | compressible |
|---|---|---|
| s/iteration at L3 | 0.353 | 0.368 |
| iterations per arm (9 converged + 10 capped + 3 cold) | ~71,500 | ~71,500 |
| **core-minutes per arm** | **~560** | **~585** |

**Every figure in §7.3 is EXTRAPOLATED, not measured.** The iteration-count
scaling in particular is a modelling assumption with no measurement behind it on
this mesh, and it is the term most likely to be wrong.

### 7.4 Registered caps — an overrun STOPS THE RUN

| | cap (core-min) |
|---|---|
| Stage 0, mesh build, all three levels | **40** |
| Stage 1, y+ probe, both arms | **120** |
| Stage 2, per arm | **800** |
| **ITEM CEILING** | **1,800** |

**An overrun stops the run; it does not get a new budget.** A2-GC L1's cap firing
correctly is the precedent that matters. A cap-stop on a registered cap is
**`NOT A RESULT`**.

Derived cost at the recorded rate (c7a.4xlarge, $0.0513/core-h, **owner-stated,
reported-by-owner, NOT measured** — the box cannot read its own billing):
1,800 core-min = 30.0 core-h = **$1.54, derived, not measured**.

`cost_basis`: anchors MEASURED from the coarse sweeps' logs; all scaling
EXTRAPOLATED; dollars DERIVED at the owner-stated rate. **Contention disclosure:
two cfd `simpleFoam` jobs were live on this box at freeze time**, so any wall
time measured for this item will carry contention and the actual/predicted ratio
must attribute it separately rather than absorbing it.

Memory: ~11.6 GiB peak observed on A2-GC L1 at 306k cells; L3 here is ~1.3e5
cells, so the 16.0 GiB box is not expected to bind. Registered floor: refuse to
launch below 4.0 GiB MemAvailable.

### 7.5 Calibration at completion

Per `CLAUDE.md` rule 12, at each stage's completion the pre-registered estimate is
compared against the actual incurred cost, actual stated in core-minutes from
logs, dollars derived and labelled, the ratio actual/predicted stated and the gap
attributed (contention / waste / misprediction, waste named separately and never
absorbed into the ratio). Row lands in `docs/COST_CALIBRATION.md`.
**The iteration-scaling assumption of §7.3 is named in advance as the term most
likely to carry the error.**

---

## 8. WHAT EACH OUTCOME WOULD MEAN — REGISTERED BEFORE THE ANSWER EXISTS

The coarse result: **both regimes converged 0–8° and failed 9–18°, the same
boundary to the degree across a tenfold Reynolds difference** (`e169e382`).

**Registered in advance, so that neither outcome is a surprise and neither can be
narrated after the fact:**

**(A) If the fine mesh MOVES the boundary** — say convergence now holds to 12–14°
— then the coarse boundary was substantially a **resolution** artefact. The 9°
figure would then be a property of the 4,032-cell wall-functioned mesh and not of
the flow, and every statement resting on "the same boundary across a tenfold
Reynolds difference" weakens, because that coincidence would then be a shared
property of a shared inadequate mesh rather than a physical fact.

**(B) If the fine mesh does NOT move the boundary** — the break stays at 9° on
both arms — then the boundary is a property of the **operating point and the
steady formulation**, not of resolution. This is the more likely outcome on the
lane's reading, because 2-D steady RANS losing convergence near the onset of
significant separation is expected behaviour of the steady formulation itself,
which a finer mesh does not repair and can sharpen. **It would still not be a
stall angle** (§6).

**(C) If the boundary moves DOWN** — convergence fails earlier than 9° — that is
consistent with a wall-resolved mesh capturing separation onset that the wall
function suppressed. Informative, and **not** a regression.

**A registered expectation is being written for (B) as the lane's prior. That
prior was wrong last time** — the coarse sweeps' registered expectation said
12–14° and was refuted by the measured 9° (`e01d363d`). It is recorded again
anyway, because a prior that is only recorded when it turns out right is not a
prior.

---

## 9. GATES

| gate | subject | verdict rule |
|---|---|---|
| `G-MESHFAM` | generator selfcheck rc 0; growth ratio ≤ 1.35 at every built level; built cell counts recorded | refuse (exit 2) on rc ≠ 0 |
| `G-YPLUS` | measured y+ min/mean/max on the wall patch, every α, both arms | `GATE FAIL` if y+max ≥ 1.0 anywhere; exit 2 if the field is absent/empty/all-zero for a point with a flow field |
| `G-WALLTREAT` | `useWallFunction: False` present in the run script AND `BCType=nutLowReWallFunction` present in the solver log for the `wing` patch | exit 2 if the log does not confirm the BC that actually ran |
| `G-COMPLETE` | rule 4, all clauses: rc 0, `End` line, last time == `endTime`, fields present, `ExecutionTime` count == `endTime`, **every field newer than the case's own `0/T`** (age guard) | refuse (exit 2) rather than degrade |
| `G-COLD` | cold controls executed and their iteration counts differ from the continued points | a cold point matching the continued count means the warm start was not inherited and the "continued" label is false |
| `G-STALL` | no output binds a stall word to a numeric angle | exit 2 on a planted claim |
| `G-CAPS` | every stage within its registered cap | cap-stop ⇒ `NOT A RESULT` on that stage |
| `G-NOBAND` | no output presents a value from this item as grid-converged or inside a band | exit 2 — §1.3 |

**Composition:** D19M's repaired `compose_item`, from `verdict_before_ceiling`,
hard-gate list tested for **both** `GATE FAIL` and `NOT A RESULT`. Ceiling
`GATE REACHED` (§1.4). Per `CLAUDE.md` rule 5's direction, a gate may turn a
`PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse.

---

## 10. PLANTED-ZERO CONTROLS — AND THE CONTROL ON THE CONTROLS

Rule 3: a zero from a reader not shown able to see a non-zero is not evidence.
At grade time, every reader that can return a zero or an absence is driven with a
**live planted perturbation, read back through the real reader function on real
bytes, refusing at exit 2** if the reader cannot see it.

**And the lesson this item is built around: a control must REFUSE IF ITS OWN
MUTATION DID NOT LAND.** Three of the AoA lane's eleven controls were written
against fixture literals and **silently no-opped on real bytes** — one of them
the zero-passing control. Therefore every control here:

1. reads the target bytes **before** mutating,
2. writes the mutation,
3. **asserts the bytes actually changed** — refusing at exit 2 if they did not,
   because a no-op mutation followed by a passing check is a control that proves
   nothing,
4. drives the **real reader function**, not a copy of it, on the mutated bytes,
5. asserts the reader's verdict flipped,
6. restores and re-asserts the restore landed.

Registered controls: y+ reader sees a planted non-zero y+ field; y+ reader flags a
planted y+ ≥ 1; completion reader refuses a planted truncated log; completion
reader's age guard refuses a planted stale field; `G-STALL` fires on a planted
stall claim and does not fire on the honest caveat; `G-WALLTREAT` refuses a log
with the `nutUSpaldingWallFunction` line planted in place of the low-Re one;
convergence reader flips on a planted residual. **The selfcheck of §2.1 already
carries its own mutation control and passed.**

---

## 11. FREEZE

The gate, threshold, cap and label above are committed **before** the solver
starts. After first compute, gates are closed; changes land only as dated addenda
that cannot alter a gate, threshold, cap or label, with originals struck and never
rewritten.

The grading path is fixed at this commit. The frozen file is verified to be the
file that ran by hashing it against the committed blob.

**Instruments frozen by this document** (sha recorded in the commit that lands it):

- `a1wr_genmesh.py` — the parametric generator, selfcheck rc 0 at freeze
- `A1WR_PREREGISTRATION.md` — this file

Stage-2 driver, run script and grader are **not yet written** and are registered
as **owed before Stage 2**, each frozen by a dated addendum to this document
before the compute it governs. Stage 0 and Stage 1 are governed by this document
as it stands.

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---
---

# AMENDMENT 1 — 2026-09-01 — PRE-COMPUTE — v1.0 → v1.1

**`lines whose number changed above this section: 0`**

Nothing above this line has been edited. Every superseding value is stated
here, and §12.2 lists exactly which earlier statements it replaces.

## 12.1 THE CONDITION, AND HOW IT WAS CHECKED

Rule 2 permits an amendment **before first compute** and requires it to state
the condition and how the condition was checked.

**Condition: no compute has been spent on this item.**

**How it was checked, not asserted:** the run root `A1WR` **does not exist**.
`ls -d /home/ubuntu/certonomous-runs/*A1WR*` returns no match; there is no
`verification/runs/` tree for this item; no mesh has been built; the generator
has been executed **only** in `--selfcheck` mode, which imports no pyHyp, writes
no file and touches no case. The gates, thresholds, caps and label of v1.0 are
therefore still open, and this amendment may lawfully move them.

**It was independently checked by the supervisor**, who reports the run root
absent by their own search and both v1.0 blobs matching on disk. **That check is
theirs and is recorded as corroboration, not as a substitute for the lane's own**
— a delegate's test is evidence, not the supervisor's read, and the reverse
holds equally.

## 12.2 WHAT WAS WRONG: A CONSTANT NOBODY READ

v1.0 registered the compressible viscosity as **ν = 1.568622e-5**, derived from
**μ = 1.846e-5** — the Sutherland value for air at 300 K. **That number was
INFERRED from physical recall and was never read from the case.** The case's own
dictionary specifies:

```
transport             const;
mu                    0.000018;
```

μ is **1.8e-5**, constant, not 1.846e-5 and not temperature-dependent.

**This is the defect in its purest form. Three different compressible Re values
were in circulation in the lab on the day this was written — this lane's
6.375e6, another lane's 6.54e6, and a 6.667e6 derived from the `nuTilda0 = 3ν`
convention — AND NOT ONE OF THE THREE HAD BEEN READ FROM THE CASE'S OWN
DICTIONARY. A number nobody measured has no place in a freeze, least of all the
one that sizes the mesh.** The dictionary settles it and is now cited by path.

**Sources, read for this amendment:**

| quantity | value | read from |
|---|---|---|
| ν incompressible | 1.5e-5 | `CURRICULUM-AOAI-…/case_cold/constant/transportProperties` |
| μ compressible | 1.8e-5, `transport const` | `CURRICULUM-AOAC-…/case/constant/thermophysicalProperties` |
| molWeight | 28.97, `equationOfState perfectGas` | same dictionary |
| chord | built extent 0.99882687 | `ladder-a1-naca0012/surfaceMesh.xyz`, measured |

**The error direction was the safe one and it is stated because it does not
excuse the error.** Re was UNDERSTATED, so `s0` was LOOSE, so measured y+ would
have come out HIGHER than predicted — pushing toward the Stage-1 stop rather
than past it. **It failed closed.** A registered constant that is wrong is wrong
regardless of which way it leans.

## 12.3 SUPERSEDING VALUES

**Replaces the Reynolds figures in §1.1, §1.2, §2.3 and the y+ table in §3.1.**

Constants, all read (§12.2). ρ from `perfectGas`: R = 8314.47/28.97 = 287.0028,
ρ = p0/(R·T0) = **1.1768179**; ν_w = μ/ρ = **1.529548e-5**.

**A distinction v1.0 did not draw:** the run scripts' `rho0 = p0/T0/287 =
1.1768293` is the **force-scaling** density for CD/CL and is **not** the
thermodynamic density. They differ by 9.6e-6 relative — negligible here, but
they are different quantities and v1.0 used the scaling one for a
thermodynamic purpose.

| | v1.0 (struck) | **v1.1 (read)** |
|---|---|---|
| ν compressible | ~~1.568622e-5~~ | **1.529548e-5** |
| Re incompressible | ~~6.667e5~~ | **6.666667e5** (unchanged in substance) |
| Re compressible | ~~6.375e6~~ | **6.537877e6** — v1.0 was **2.5 % low** |
| ratio | ~~9.563~~ | **9.8068** |

**Chord, which v1.0 assumed and did not read.** Every Re above depends on it
**linearly**. The built surface extends to **x = 0.99882687**, not 1.0, because
the tutorial truncates PS and SS at ~99.8 % chord for the blunt TE (the profile
files end at 0.99941610). Re is nonetheless quoted at a **reference chord of
1.0**, because `A0 = 0.1` is a reference **area** consistent with chord 1.0 ×
span 0.1 and the force coefficients are already normalised by it. Using the
built extent instead gives Re_comp = **6.530208e6**, a **0.117 %** shift, far
inside the sizing margin. **Both are now on the record; neither is assumed.**

**`transport const`, not Sutherland — stated on the face.** μ does not vary with
temperature in this case. At M = **0.288** the stagnation temperature rise is
**4.98 K**, so the modelling choice is defensible; it is stated because a reader
meeting a compressible solver will otherwise assume Sutherland and mis-derive ν
at the wall — which is precisely the mistake v1.0 made.

## 12.4 s0 RE-DERIVED FROM THE CORRECTED Re — NOT LEFT BESIDE IT

**Replaces the `s0` row of §2.1's table and the whole y+ table of §3.1.**

Re-running the sizing chain on the read constants: Cf = 0.0576·Re^-0.2 gives
u_τ(flat plate) = 3.53307 m/s compressible, 0.44392 m/s incompressible; the
leading-edge/peak factor **1.5611 is ANCHORED** on the measured y+max = 92.4 at
y_c = 2e-3 on the existing coarse mesh; the incidence factor **1.8 at α = 18
remains an ESTIMATE and is the weakest link in the chain.** The compressible arm
binds by **7.81×**, so §2.3's argument stands unchanged — indeed it **binds
harder** than v1.0 claimed.

**At the v1.0 spacing the corrected numbers put L1 at predicted y+ = 0.974 —
under 1 by 3 %. That is not a margin, it is a coin toss on an estimated
incidence factor.** `s0` is therefore re-derived, not merely re-labelled:

| | v1.0 s0 (struck) | **v1.1 s0** | predicted y+ comp | y+ inc | growth |
|---|---|---|---|---|---|
| L1 | ~~3.0e-6~~ | **2.5e-6** | **0.811** | 0.104 | 1.2548 |
| L2 | ~~1.5e-6~~ | **1.25e-6** | **0.406** | 0.052 | 1.1196 |
| L3 | ~~7.5e-7~~ | **6.25e-7** | **0.203** | 0.026 | 1.0580 |

All three levels remain wall-resolved on **both** arms; margin at the binding
level rises from 3 % to **19 %**. Growth ratios move by <0.4 % and stay far
under the registered 1.35 ceiling. **Cell counts, refinement ratio r = 2, the
1.35 ceiling, marchDist = 20, the staging, the caps and the item ceiling are
UNCHANGED** — only `s0` moves, so §7's cost stands (a marginally higher
near-wall aspect ratio is well inside the EXTRAPOLATED band, and the caps bind
regardless).

## 12.5 WHAT THIS AMENDMENT DOES NOT CHANGE

The wall-treatment finding (§4) is untouched and was evidence, not inference:
`useWallFunction: False` → `nutLowReWallFunction` at `DAField.C:1207-1230`, the
branch firing only on `type wall` patches with A1's `wing` patch **checked** to
be one. Standard SA needs no low-Re variant — fv1 **is** the near-wall damping.
§3.4 stands: **the mesh is not re-cut until y+ passes; an overshoot is a
registered outcome, and that line holds even though the corrected Re makes an
overshoot more likely.** §6's two-directional stall trap, §8's registered
outcomes and the lane's prior all stand.

## 12.6 RE-PINNED INSTRUMENT

`a1wr_genmesh.py` is amended in the same commit: `BASE["s0"]` 3.0e-6 → 2.5e-6,
and its header block now carries the read constants, the measured chord, the
`transport const` note and the anchored-vs-estimated split. **Its `--selfcheck`
was re-driven after the edit and returns rc 0**, including the mutation control
(which now reports `s0 L2 1.25e-06 -> 2.5e-06`, confirming the control re-armed
against the new value rather than passing on a stale literal).

Its sha is re-pinned by the commit landing this amendment, superseding the
v1.0 pin in §11. **The grading path is re-fixed at that commit.**
