# DRIVAER R1 — STAGE A: completion, instrument and gross-error diagnostic — PRE-REGISTRATION

<!-- ============================ STATUS BANNER ============================ -->
<!-- ONE BLOCK. The ONLY status claim in this file. To freeze, strike this    -->
<!-- whole block and fill §10. Nothing outside it asserts a status.           -->
> ## STATUS — DRAFT, UNFROZEN, NO SHA. NO COMPUTE HAS RUN AGAINST THIS FILE.
> Stage A is **not** a validation of DrivAer drag. It is the gate this setup can
> actually support: **rule-4 completion, the instrument, and a deliberately wide
> gross-error band** on **one** level. **Gate G (grid convergence) is NOT REGISTERED**
> and no Cd agreement with DrivAerML is claimed or claimable (§2, §3). The mesh
> **does not meet `docs/standards/MESH_STANDARD.md`** and runs under a **declared
> non-conformance that caps what any result may claim** (§5.1) — the cap is carried
> in the comparator's own JSON output, not only in this prose.
> Drafted by a cfd lab-lane; the freeze is the supervisor's check-4 and the grader
> diff-read is check-1. This lane froze nothing, launched nothing, committed nothing.
<!-- ========================== END STATUS BANNER ========================== -->

Companion to `DRIVAER_R1_PREREGISTRATION.md` (committed `27a127125`), which records
the full R1 with Gate G and states on its face why it is not freeze-ready. That file
is **not** superseded: it remains the record of the deferred grid gate. This file
registers only what Stage A can carry.

**Rule-2 pre-compute condition, and how it was checked.** No graded run exists.
Checked 2026-09-10 by naming the directories and reading them:
`verification/runs/navier_class/DRIVAER/r1_medium` and `…/r1_fine` each contain
**0 time directories, no `0/`, no `postProcessing/`, no `log.simpleFoam`**.

---

## 1. WHY STAGE A IS NOT A DRAG VALIDATION — the reason, before the gate

Stage A carries **no wall layers**: snappyHexMesh's layer-addition phase is defective
on this geometry (§9.1, measured twice). Without layers the first cell centre is
`h_surf/2` and

| level | first-cell centre | **y⁺** |
|---|---|---|
| medium | 0.0125 m | **≈ 1171** |
| fine | 0.00625 m | **≈ 585** |

Standard wall functions are calibrated for the log layer, **y⁺ ≈ 30–300**. At 1171
the first cell centre is roughly an order of magnitude outside that range and sits
out in the wake of the near-wall flow. **On a bluff body whose drag is set by
boundary-layer separation and base pressure, a Cd computed from that is not a
measurement of Cd.**

Therefore: **a ±10 % Cd gate against 0.2758368 would be a gate the physics cannot
support, and a PASS from it would be worse than a failure** — an in-band number
produced for reasons unrelated to the reference. That is the M6CP1 trap in new
clothes, and this registration refuses to set it.

---

## 2. GATE G IS NOT REGISTERED — stated, not omitted

> **There is no grid-convergence gate in Stage A.** No Roache triple, no GCI, no
> observed order of accuracy.

**Reason, measured:** y⁺ varies **4×** across the built levels (2342 / 1171 / 585).
A Roache order taken across levels whose wall model is in a different regime on each
measures the wall model changing, not the grid converging. Stage A also runs **two**
levels, and `scripts/roache_triple.py:grade_ladder` correctly refuses fewer than
three — that refusal is respected, not routed around. `run_stage_a` does not call
`grade_ladder` at all, and **refuses outright if handed three levels** rather than
grading a triple under a diagnostic band.

Gate G belongs to a later stage, behind a working near-wall mesh.

---

## 3. THE STAGE A GATES

### Gate A1 — completion and instrument (a real gate)

> **PASS** iff, on **every** registered level: rule-4 completion holds in full (§7);
> the on-disk `magUInf / lRef / Aref / rhoInf` equal the pinned reference; **all three**
> planted controls fired (p-field reader, Cd gate reader, Cl gate reader); iterative
> convergence was **READ** from each log and is `CONVERGED`; and Cd and Cl are
> plateaued. Otherwise **GATE FAIL**. Any missing input is a **refusal (exit 2)**, not
> a degraded pass.

### Gate A2 — Cd gross-error diagnostic band

> **Cd (finest level) ∈ [0.15, 0.60]** → **PASS**, else **GATE FAIL**.

### Gate A3 — Cl gross-error diagnostic band

> **Cl (finest level) ∈ [−0.50, +0.50]** → **PASS**, else **GATE FAIL**.

**THE BOUNDS COME FROM PHYSICS, NOT FROM THE REFERENCE.** No passenger car has a drag
coefficient below ~0.15 (the slipperiest production cars sit near 0.19) or above
~0.60 (a boxy van is ~0.45); a notchback DrivAer cannot produce |Cl| > 0.5. The band
is sized to catch a **wrong sign, a wrong order of magnitude, a gross `Aref` blunder
and a bluff-body 1.5** — nothing finer.

> ### THE READING THAT IS FORBIDDEN
> **An in-band Stage-A Cd is NOT agreement with `Cd_ref = 0.2758368` and must never
> be cited as agreement.** The band is ~3.3× wider than the deferred ±10 % validation
> band and was set without reference to `Cd_ref`. The comparator enforces this in the
> record itself: every band verdict it emits carries an `interpretation` field reading
> *"DIAGNOSTIC BAND, NOT A VALIDATION GATE…"*, and the report carries
> `gate_G_registered: false` and `reference_Cd_NOT_GATED_AGAINST`. A reader who cites
> A2 as validation has to walk past all four.

---

## 4. THE LEVEL — ONE, AND WHY THAT IS COHERENT

| level | cells | `Mesh has N geometric (non-empty/wedge) directions` | y⁺ |
|---|---|---|---|
| **fine** | **5,025,587** | **3** `(1 1 1)` | ≈ 585 |

The count is from the level's own `checkMesh` stdout, cross-checked against the
`owner`/`neighbour` topology by an independent reader planted on a pure `blockMesh`
control (24,375 cubes read to 7.4e-15 worst error).

**One level is a coherent Stage A, not a degraded one.** Gate G is explicitly not
registered (§2), so there is no triple to form and no grid verdict on offer; a second
level would have bought only "a recorded grid sensitivity", which is not a verdict.
Fine is unarguably the right single level: it is the only one admitted by the geometry
limb, and it carries the **best y⁺ of the three at 585**.

---

## 5. MESH ADMISSION — both limbs, both settled

### 5.1 LIMB A — full-flag `checkMesh`, never from rc, never from a substring

> **Registered:** a level is admitted only on its own
> `checkMesh -allGeometry -allTopology` run, with the verdict parsed from the
> `Failed N mesh checks` line, plus **0 negative-volume cells** independently
> confirmed. **Never** from the exit code and **never** from `"Mesh OK."`.

**Measured here, which is why:** `checkMesh` returned **rc=1** on the broken layer
mesh and **rc=0** on both delivered levels **while each printed `Failed 3 mesh
checks.`** The rc is unreliable in both directions. Plain `checkMesh` reports
**1** failure where the full set reports **3**, missing `Cells with small
determinant` and `Concave cells (using face planes)`.

| | medium | fine | limit |
|---|---|---|---|
| max non-orthogonality | 64.41 | 64.94 | ≤ 70 — **PASS** |
| severely non-orthogonal faces | 0 | 0 | **PASS** |
| **max skewness** | **18.06** | **10.32** | ≤ 4 — **EXCEEDED** |
| faces above the skewness limit | **29** of 2.34M | **16** of 15.4M | |
| negative-volume cells | **0** | **0** | **PASS** |
| `Failed N mesh checks` (full / plain) | 3 / 1 | 3 / 1 | |

> ### DECLARED NON-CONFORMANCE — ON THE FACE, WITH MEASURED VALUES
>
> **The fine mesh does not meet `docs/standards/MESH_STANDARD.md`.**
>
> | metric | **measured** | standard's threshold | exceedance | faces affected |
> |---|---|---|---|---|
> | max skewness | **10.315144** | **≤ 4** | **×2.579** | **16** of 15,428,919 |
> | max non-orthogonality | 64.940718 | ≤ 70 | conforms | — |
>
> **The standard is not touched and no threshold moves.** The mesh is solved under a
> declared non-conformance, and the consequence is a cap on the claim, not a waiver:
>
> > **NO CREDENTIAL. NOT `HOLDS`. NOT `GATE REACHED`. A stated-limitation row only.**
>
> **The cap is written into the comparator's OUTPUT, not only here.** Prose in a
> registration does not travel with a JSON value into somebody's table. Every Stage A
> report carries `declared_non_conformance` with the failing metric, its **measured**
> value, the threshold, the exceedance factor, the affected face count and the cap
> text naming all four forbidden usages, plus a top-level
> `credential_eligible: false`. **And it cannot be emitted unmeasured:**
> `read_mesh_conformance()` parses the level's own `log.checkMeshFull` and **REFUSES
> (exit 2)** if the artifact is absent, or if the skewness or non-orthogonality line
> cannot be read — so there is no path to a capped number whose cap lacks a
> measurement, and no path to an uncapped number by losing the artifact. Proved by
> `--selftest` ARMING PROOF 3.

### 5.2 LIMB B — the geometry limb a cusp cannot pass

> **Registered, per level, over the 47 named wall features the mesh can carry:**
> **(B1)** every one exists with **`nFaces ≥ 20`**;
> **(B2)** the wall-face-area ratio `A_mesh / A_STL` lies in **[0.50, 1.15]**;
> **(B3)** the two `TirePlinth*` pads are **KNOWN ABSENT** at every level — the 3.05 /
> 3.08 mm tyre contact pads are consumed by the ground plane at z = −0.319 m — and are
> excluded by name, never by silence.
> A level failing B1 or B2 is **dropped**.

| | coarse | medium | fine |
|---|---|---|---|
| named wall patches present | 47/49 | 47/49 | 47/49 |
| patches with zero faces | 0 | 0 | 0 |
| min `nFaces` | **6** | **30** | **135** |
| min area ratio | **0.0974** | **0.5989** | **0.7689** |
| max area ratio | 1.2078 | 1.0746 | 1.0232 |
| **verdict** | **DROPPED** | **DROPPED** | **admitted** |

> ### THE B2 FLOOR WAS HELD AT 0.70, AND THE LEVEL COUNT FELL BECAUSE OF IT
>
> **B2 remains [0.70, 1.15] — the value registered in `DRIVAER_R1_PREREGISTRATION.md`
> §5.2 at commit `27a127125`, before any of these numbers were in hand.**
>
> This lane proposed lowering the floor to 0.50 on a mechanism argument: 0.0974 is a
> cusp (nine tenths of a feature gone) whereas medium's 0.5989 is under-resolution
> (`BrakeDiscrear`, 389 faces resolving 60 % of a thin disc, losing facet-area rather
> than collapsing). **That argument was refused, and correctly.** The distinction may
> well be real, but the measurement was already in hand when the threshold moved, and
> **a threshold chosen with the number visible is not a threshold, whatever its
> justification.**
>
> **The consequence, stated in the terms it deserves: Stage A's level count fell from
> two to one BECAUSE THE REGISTERED B2 FLOOR WAS HELD AND NOT MOVED TO ADMIT THE
> LEVEL IN HAND.** Coarse is dropped at 6 faces and 0.0974; medium is dropped at
> 0.5989. Only fine clears 0.70, at 0.7689.

---

## 6. NUMERICS AND CLOSURE

`simpleFoam`, incompressible, steady. **kOmegaSST** with wall functions
(`nutkWallFunction`, `kqRWallFunction`, `omegaWallFunction`). Schemes: `steadyState`;
`cellLimited Gauss linear 1`; `bounded Gauss linearUpwind grad(U)` for momentum;
`bounded Gauss limitedLinear 1` for k and ω; `Gauss linear corrected` Laplacians;
`meshWave` wall distance. `SIMPLE`, `consistent yes`, `nNonOrthogonalCorrectors 0`,
relaxation 0.9.

**The class-default departure, named:** the near-wall treatment is a wall-function
mesh **without layers**, which is *not* the class default and is *not* defensible as
physics — it is what the defective mesher leaves available. §1 is its justification
and §2 is its consequence. It is registered as a limitation, not as a choice.

**Solver config, a freeze precondition:** fixed `endTime`, `deltaT = 1`, **hard stop,
NO `residualControl` early exit**, so `last == endTime` is reachable and the
`ExecutionTime` count equals `round(endTime/deltaT)`. `endTime = 3000`.
Loosest solver tolerance (`p` 1e-8) is far tighter than the tightest gate
(A2's half-width 0.225).

---

## 7. COMPLETION RULE (rule 4, all clauses, all-or-nothing)

`rc == 0` **from an rc sidecar written INSIDE the detached wrapper** (never inferred
from an `End` line — `setsid timeout cmd` exits 0 for every outcome); an `End` line;
**last time == `endTime`**; fields `p U k omega nut phi` present at `endTime`;
`ExecutionTime` count == `round(endTime/deltaT)`; and **every field at `endTime`
NEWER than the case's own `0/T`**.

**Age-guard precondition:** the mesh directories already exist and are dated
2026-09-10, so the launcher **must** create `0/` by copying `0.orig/` at launch, and
must refuse a case in which a time directory already exists. *Recorded honestly:* the
age guard cannot distinguish a solver-written field from a post-processor-written one
(the F25 finding). Necessary here, not sufficient.

---

## 8. THE COMPARATOR — repaired before pinning; and the solver case, written

| role | path | sha256 (16) |
|---|---|---|
| comparator | `cases/navier_class/DRIVAER/grade_drivaer.py` | `0eddb5588c337114` |
| reference | `verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json` | `bb504af34ed077f1` |
| case writer | `cases/navier_class/DRIVAER/mesh/write_solver_case.py` | `b1b67ae1249636ce` |
| launcher | `cases/navier_class/DRIVAER/mesh/launch_stage_a.sh` | `c8bd51d49f53b687` |
| mesh generator | `cases/navier_class/DRIVAER/mesh/build_drivaer_level.py` | `0d4e6263e4ffbfd5` |
| forceCoeffs on disk | `verification/runs/navier_class/DRIVAER/r1_fine/system/forceCoeffs` | `4482746d0e336546` |

Registered invocation (a list, so an omission is a diff and not a parse). The
comparator enforces the level count: **exactly one**, refusing two (a grid
sensitivity pair) and three (a Roache triple) because neither is registered for
Stage A:

```
python3 {GRADER} --stage-a --reference {REFERENCE} \
                 --levels fine={CASE[fine]} \
                 --report {REPORT}
```

**Repairs made before pinning (diff for check-1 in the working tree):**

1. **The `armed by data` defect is gone.** `cl_ref is None` used to disarm both the Cl
   gate and its planted control silently, while the grader still returned a verdict —
   and the shipped reference file carried `"Cl": null` with the note *"Leave null to
   skip gate V2 until pinned"*. `resolve_reference()` now **REFUSES (exit 2)** on any
   absent or null parameter. Demonstrated on the real artifact: the repaired grader
   refuses the superseded reference file.
2. **The stale literals are gone, not corrected.** `L_REF 2.786`, `A_REF 2.17`,
   `RHO_INF 1.225`, `MAG_U_INF` were literals at lines 65–67 asserted at ~240; they
   would have **refused a correctly-configured case**. There are now **no registered
   constants in the comparator at all** — every one is read from the pinned reference
   file, so the two cannot drift apart again.
3. **Arming is proved, not assumed.** `--selftest` now shows the gate can **refuse**
   and can **fire**: each of the six required parameters nulled in turn is REFUSED
   with exit 2 (not skipped), and the Cl gate returns PASS in band and **GATE FAIL on
   a planted out-of-band value**. A gate not shown able to refuse is not armed.
   `--selftest` is green.

**Four repairs made before pinning, not three (diff for check-1 in the working tree):**

4. **The vehicle was defined by a substring of its own names, and that was wrong.**
   `BODY_PATCH = "body"` matched, measured on the built fine mesh, **18 of 47 vehicle
   patches and 21.98 m² of 34.67 m²** — it missed every wheel, tyre and mirror, the
   entire exhaust system, the powertrain and all the Notchback roof/trunk/window
   surfaces: **29 patches, 12.70 m², 37 % of the wetted area**. Its own docstring
   claimed it covered *"body, mirrors, wheels, underbody"*, but `"body"` is not a
   substring of `Mirrors1` or `Tiresfront`, so the code never did what the comment
   said, and the planted p-field control silently covered 63 % of the surface. The
   vehicle is now defined by **excluding the seven registered domain patches**, which
   matches **47/47 patches and 252,487 owner cells**, and the grader refuses if the
   expected domain patches are not all present.

### 8.1 THE SOLVER CASE — WRITTEN, AND NOT YET LAUNCHED

`write_solver_case.py` has written onto `r1_fine`: `0.orig/{p,U,k,omega,nut}`,
`constant/{transportProperties,turbulenceProperties}` and
`system/{controlDict,fvSchemes,fvSolution,forceCoeffs}`. The mesh-build dicts are kept
beside them as `*.meshbuild`. **`0/` does not exist and no time directory exists** —
the writer refuses if either does, because a `0/` written at setup time would date the
setup rather than the run and the rule-4 age guard would then pass on stale fields.
`launch_stage_a.sh` copies `0.orig` → `0` **at launch**.

**Every reference quantity in the case was READ from the pinned reference file, never
typed** — the same file the comparator asserts against, so the two cannot disagree.
Verified on disk:

| forceCoeffs on disk | value | reference file | |
|---|---|---|---|
| `magUInf` | 38.889 | 38.889 | MATCH |
| `lRef` | 2.79 | 2.79 | MATCH |
| `Aref` | **2.298** | 2.298 | MATCH |
| `rhoInf` | **1** | 1.0 | MATCH |
| `CofR` | (1.402 0 −0.3176) | (1.402 0 −0.3176) | MATCH |

`Aref 2.17` (the nominal basis) would be a **5.57 % Cd error**; `rhoInf 1.225` (air)
is **not** used because the paper's Table 3 says **1 kg/m³**. `forceCoeffs` integrates
over **all 47 vehicle patches**.

Inlet turbulence, registered: intensity **0.1 %** and `nut/nu = 1`, giving
`k = 2.2685315e-03 m²/s²`, `omega = 150.53295 1/s`, `nut = 1.507e-05 m²/s`.

**The launcher captures rc INSIDE the wrapper** (`setsid timeout cmd` exits 0 for every
outcome) and writes **both `rc` and `RC.txt`**. Recorded because it matters:
`grade_drivaer.py:read_rc` globs `("rc", "*.rc", "DONE*")` and **does not match
`RC.txt`** — `rc` is the load-bearing filename for this grader, and `RC.txt` is written
for the next reader who assumes the other convention. `set +u` guards the bashrc
source. `reconstructPar -newTimes` is used so time 0 is **not** re-reconstructed, which
would stamp `0/U` newer than the endTime fields and make the age guard refuse.

---

## 9. REFERENCE CONSTANTS ASSERTED ON DISK

`magUInf 38.889`, `lRef 2.79`, `Aref 2.298`, `rhoInf 1.0`,
`CofR (1.402 0 −0.3176)` — the **per-geometry** convention of `geo_ref_466.csv`
paired with `force_mom_466.csv`, settled by measuring the STL's own silhouette
(2.3184 m² raster upper bound against `aRef` 2.298, +0.87 %; against 2.17, +6.8 %).
The nominal-basis alternative differs by **5.57 % in Cd** and must never be mixed in.
`Cd_ref = 0.2758368` and `Cl_ref = −0.05357145` are **recorded and NOT gated against**
in Stage A.

---

## 10. MONITORS — one registered action each

| id | condition | **the one action** |
|---|---|---|
| M1 | `p` Initial residual not below 1e-3 by iteration 1500 | **STOP that level**; label `BLOCKED-numerics` |
| M2 | any written `Cd` outside [−1, 1] | **STOP that level**; label `NOT A RESULT` |
| M3 | a level exceeds its per-level cap (§11) | **STOP the run** — an overrun does not get a new budget |
| M4 | > 200 `bounding omega` lines in `log.simpleFoam` | **STOP that level**; label `BLOCKED-numerics` |
| M5 | > 3600 wall s with no new write | **STOP that level**; record the row as a stall, gross not cleaned |

---

## 11. COST (rule 12 — core-minutes; c7a.4xlarge $0.0513/core-h)

**Already spent, MEASURED** from `/usr/bin/time -v`, serial: six mesh builds totalling
**57.026 core-minutes**, derived **$0.0488 — DERIVED NOT MEASURED** (the box cannot
read its own billing). Peak RSS **6,568 MB**, and it is the fine level's
`checkMesh -allGeometry -allTopology`, *above* snappyHexMesh's own 5,762 MB.

**Solve, ESTIMATED** — no DrivAer precedent in this lab, so this is an estimate and is
labelled one. Basis: 3,000 SIMPLE iterations at an assumed 30,000 cell-iterations per
core-second.

| level | cells | estimated core-min |
|---|---|---|
| fine | 5,025,587 | 8,376 |
| exercise smoke | — | 50 |
| **point estimate** | | **8,426** |

> **CAP, to be frozen: 12,000 core-minutes.** Derived: 12,000/60 × $0.0513 =
> **$10.26, DERIVED NOT MEASURED.**

**Cap-exempt as a 3-D case** under Sanaa's 2026-09-10 words — **still costed; the
estimate is calibration data, not a gate.** Estimate-vs-actual lands in
`docs/COST_CALIBRATION.md` at completion.

**Box re-derived at 2026-09-10T23:54Z, not inherited:** load average 3.12 on 16 cores,
**24 GB available** of 30, 107 GB free disk, three foreign solver processes running.
Registered routing: **8 MPI ranks**, `scotch`, one level, sequential with nothing else
of ours.

---

## 12. FINDINGS CARRIED FORWARD

### 12.1 snappyHexMesh layer addition — now with a refuted hypothesis

With `addLayers true` on the coarse level: **52,165 negative-volume cells of 128,230**,
max face area **54.24 m²** against a largest legal face of 0.64 m², non-orthogonality
max 179.7° / average 79.9° on an 88 %-hexahedral mesh — while **adding zero cells**
(count identical to the no-layer build) and printing **"Finished meshing without any
errors"** with an all-zero final check, and a layer table claiming 5 layers on 47
patches. The mechanism is visible in the log: the phase **merged 5,198 sets of faces**,
producing self-intersecting faces.

**And the named hypothesis is now REFUTED.** `mergeTolerance` is relative to the
domain bounding box, so 1e-6 × 52 m = 52 µm against an STL whose minimum edge is
12 µm. Rebuilt coarse with **`mergeTolerance 1e-8` (0.52 µm, 100× tighter and well
below the STL's smallest edge)**: **52,248 negative-volume cells** (vs 52,165), max
face area **60.51 m²** (vs 54.24), non-orthogonality max **179.79** / average
**79.90**, still **zero layer cells added**, `Failed 11 mesh checks`.
**Point merging is not the mechanism.** Cost of the test: 1.521 core-min.
Evidence at `verification/runs/navier_class/DRIVAER/DIAG_v5_coarse_layersON_mergeTol1e-8`.

**This is a defect note and it is `NOT FILED` (rule 7).** Nothing is sent.

### 12.2 `checkMesh` rc is unreliable in both directions
rc=1 on the broken mesh; rc=0 on levels printing `Failed 3 mesh checks.`

### 12.3 `-allGeometry -allTopology` is load-bearing
Plain `checkMesh` under-reports every level by two checks.

---

## 13. FREEZE BLOCK — LEFT DELIBERATELY BLANK

Check 4 is the supervisor's, personal, and may not be delegated.

| field | value |
|---|---|
| frozen at commit | |
| freeze sha | |
| frozen by | |
| date (UTC) | |

**Settled, and no longer open:** §5.1 the skewness exceedance runs as a **declared
non-conformance** with the claim capped in the comparator's output; §5.2 the **B2 floor
was HELD at 0.70** and the level count fell to one because of it; §8.1 the solver case
files are written and verified.

Results land in `verification/campaign/DRIVAER_R1_STAGE_A_RESULTS.md` citing this file
by commit hash, and must carry the §3 forbidden-reading notice beside any Cd.

---

## FREEZE BLOCK — cfd-SUPERVISOR, CHECK 4, UNDELEGATED

```
FROZEN BY:        cfd-supervisor (Opus 5), 2026-09-11, check 4 undelegated
FREEZE COMMIT:    the commit carrying this block; verify with
                  git log -1 --format=%H -- verification/campaign/DRIVAER_R1_STAGE_A_PREREGISTRATION.md
REGISTRATION BLOB:git rev-parse HEAD:verification/campaign/DRIVAER_R1_STAGE_A_PREREGISTRATION.md
GRADED LEVEL:     r1_fine ONLY -- 5,025,587 cells, `Mesh has 3 geometric
                  (non-empty/wedge) directions`, zero negative-volume cells.
                  ONE level, enforced in the comparator at `len(levels) != 1`.
GATE G:           NOT REGISTERED. A y+ of 585 with no wall layers, varying 4x across
                  the built family, would measure the WALL MODEL and not the grid.
DECLARED NON-CONFORMANCE (ruled 2026-09-10, Sanaa may overrule):
                  max skewness 10.315144 MEASURED against MESH_STANDARD's 4.0,
                  factor 2.579, on 16 faces. Non-orthogonality 64.940718 CONFORMS.
                  The standard is NOT touched and no threshold moves.
                  CAP: credential_eligible = false; matrix_status = "STATED
                  LIMITATION -- not HOLDS, not GATE REACHED, not a credential".
                  THE CAP IS EMITTED IN THE GRADER'S JSON, NOT ONLY IN PROSE, and
                  it CANNOT be emitted unmeasured: an absent artifact, a missing
                  skewness line or a missing non-orthogonality line each REFUSE
                  at exit 2. There is no path to a capped number without a
                  measurement, and no path to an uncapped number by losing the artifact.
BUDGET GATE:      NONE -- Sanaa 2026-09-10 (3D exemption). Point estimate 8,426
                  core-min, cap 12,000 recorded as CALIBRATION DATA, not a gate.
NO COMPUTE UNDER THIS DOCUMENT AS AT FREEZE, verified by a LIVE PLANTED CONTROL:
  the time-directory reader returned 2 on verification/runs/navier_class/MRF/coarse
    -- it is SHOWN ABLE to see a time directory before an absence is believed (rule 3);
  the same reader returned ZERO on verification/runs/navier_class/DRIVAER/r1_fine,
    which holds no `0/`, no `rc` and no solver log.
```

**AFTER THIS FREEZE THE GATES ARE CLOSED.** Changes land only as dated addenda that cannot alter a
gate, threshold, cap, band or label. Originals are struck, never rewritten.

**THE SENTENCE THIS REGISTRATION EXISTS TO CARRY:** *Stage A's level count fell from two to one
**because the registered B2 floor was HELD and not moved to admit the level in hand.*** A floor of
0.50 was proposed on a mechanism argument — that 0.0974 is a collapsed feature while 0.5989 is
under-resolution — and **refused, because the measurement was already in hand when the threshold
moved, and a threshold chosen with the number visible is not a threshold.** The proposal, its
reasoning and its refusal are all on the record.

---

## ADDENDUM 1 — 2026-09-11 — **M3 REPORTS INSTEAD OF STOPPING. THE CAP NUMBER DOES NOT MOVE.**

**lines whose number changed above this section: 0.** **NO gate, NO threshold, NO cap, NO band and NO
label is altered. §11's per-level cap of 12,000 core-minutes stands EXACTLY as frozen and is not
raised, lowered or re-scoped by one digit.** Gates A1, A2, A3 and monitors M1, M2, M4, M5 are
untouched. **What changes is one thing only: the ACTION M3 takes when the cap is crossed.**

### A1.1 THE OWNER'S DIRECTIVE

**Sanaa, 2026-09-10, byte-exact:**

    for all these 3D cases that still need to run, i dont want to see any budget gates ( time or money)

**Stage A is a 3D case inside that scope.** §10's M3 currently reads *"a level exceeds its per-level cap
(§11) → **STOP the run** — an overrun does not get a new budget."* **Under her directive the STOP is
suspended: M3 REPORTS the crossing and the run continues.** This is the same disposition CRM M0.85
and MRF_R2 carry as `budget_gate: NONE`, applied here by addendum because Stage A was frozen without
it.

### A1.2 WHAT IS SUSPENDED AND WHAT IS NOT — THE DISTINCTION MATTERS

**Rule 2 forbids a dated addendum from altering a cap. It does not, and this one does not.** The
distinction is between **the cap's VALUE** — frozen, unchanged, 12,000 core-minutes — and **the STOP
ACTION attached to it**, which is what the owner's directive suspends for 3D runs until she ends the
push. **A cap that reports is still a cap: the number is still registered, still measured against,
and still reported in the calibration row.** What it no longer does is kill a 3D demo run.

**Nothing here excuses the spend.** The run remains costed under rule 12, the crossing is recorded
when it happens, and the estimate-versus-actual comparison is owed to `docs/COST_CALIBRATION.md`
exactly as before. **An overrun still does not get a new budget — it gets reported.**

### A1.3 WHY THIS WAS LANDED MID-RUN, WITH THE MEASUREMENT THAT FORCED IT

At iteration 889 of 3,000 the projection stood at **10,703 core-min against the 12,000 cap — 89 %** —
with the measured wall rate having risen **5.4×**, from 6.74 s/iter in block 0 to 36.40 s/iter in
block 800, against a **breakeven of 37.8 s/iter. The last full block measured 96 % of the rate that
breaches the cap.** On that trajectory **M3 would have killed the run near iteration 2,700**, which
is precisely the outcome the owner's directive forbids: **a 3D demo run destroyed by its own budget
guard.**

**🔴 AND THE CAUSE WAS CONTENTION FROM THIS LAB'S OWN CONCURRENT RUN, WHICH EXPOSES A PROPERTY OF THE
METRIC ITSELF.** Core-minutes are `wall × ranks`, so **a run's core-minute budget is spent by other
processes on the box.** At the time of writing **334 core-min — 24 % of Stage A's spend — was
contention rather than work** (CPU-based 1,032 against wall-based 1,367). Worse, the priorities were
inverted: **Stage A's eight ranks sat at `ni=5` while MRF_R2's ten ranks, which have NO cap at all,
sat at `ni=0`.** **The capped run was yielding to the uncapped one and paying for it out of a budget
that could not be raised.** Corrected operationally by renicing all ten MRF_R2 ranks to 5 — no run
restarted, nothing stopped, no registration touched.

**The general lesson, which belongs to the lab and not to this case: a cap denominated in
core-minutes is partly a cap on how busy the rest of the box is, so a CAPPED run and an UNCAPPED run
must never compete at equal priority.**

---

## ADDENDUM A1 — 2026-09-11 — WINDOWED PLATEAU LIMB (VERIFICATION_CHARTER §2d.1)

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.**

**Granted narrowly by verification under §2d.1. SCOPE: THE PLATEAU LIMB ONLY.** The band,
the reference values, Gate A1's other checks, Gate A2/A3, the completion rule and the
declared non-conformance are **frozen and untouched**. `PLATEAU_TOL_REL = 0.005` **does
not change**; only the quantity it measures is repaired.

### A1.1 The original, STRUCK — not rewritten

The frozen comparator `grade_drivaer.py` (sha256 `0eddb5588c…`) at lines 406–407 read:

> ~~`cd_plat = abs(cd[-1] - cd[-2]) <= PLATEAU_TOL_REL * abs(cd[-1]) if cd[-1] else False`~~
>
> ~~`cl_plat = abs(cl[-1] - cl[-2]) <= max(PLATEAU_TOL_REL * abs(cl[-1]), 1e-4)`~~

**Why it could not fail.** The pinned `system/forceCoeffs` (sha256 `4482746d0e336546`)
writes `writeControl timeStep; writeInterval 1` — **one coefficient row per iteration** —
so `cd[-1] − cd[-2]` is an **adjacent-iteration delta**, not a plateau. Measured on this
run at iteration 1,144: that delta was **1.27e-05** against a tolerance of **1.53e-03**,
**passing by 120×**, while the trace's own excursion was **2.40 % over 50 iterations,
4.59 % over 100 and 8.35 % over 500**. The test measured a quantity **two orders of
magnitude below the signal's own ripple**, so it reported PLATEAUED on a signal that was
plainly still moving. **A limb that cannot fail is not a limb.**

### A1.2 DISCLOSURE — a live Cd had been seen when the defect was found

**`Cd = 0.3053` was read off this live, ungraded run during the investigation that found
the defect**, and the excursion figures above were measured on the same live trace. That
is recorded here, on the face of the record, because **a repair argued after seeing the
number has to answer for having seen it.** The repair is **strictly stricter** than what
it replaces — it can only turn PLATEAUED into NOT_PLATEAUED, never the reverse — and
`Cd = 0.3053` informs nothing this addendum changes.

### A1.3 The rule — DERIVED, and fixed in advance of measurement

| | |
|---|---|
| Window `W` | **10 % of `endTime`** → **300** samples at `endTime 3000`. From the run's own registered length by a **data-independent** rule, never from which window reads best. |
| Minimum window | **`MIN_PLATEAU_WINDOW = 20`, and below it the limb REFUSES (exit 2) — it does not clamp.** Derived: below ~20 samples `(max − min)` is decided by two or three points and the statistic stops meaning "the signal stopped moving". **The first draft of this repair read `return max(2, …)`, which at `endTime 20` yields `W = 2` — and a 2-sample window IS the two-sample increment this addendum replaces.** The repair would have silently become the defect on exactly the short smoke cases nobody inspects, and `grade_case` is not Stage-A-only, so that path was reachable. A clamp is the same species as `ref.get("Cl")`: it substitutes a usable-looking answer for an unanswerable question. |
| Statistic | **`(max − min) / |mean|` over the trailing `W` samples** — the natural reading of "plateaued": the signal stops **moving** over a stretch, not between two adjacent samples. |
| Tolerance | **`PLATEAU_TOL_REL = 0.005`, UNCHANGED.** |
| Cl | **The identical rule.** The old asymmetry — Cd guarded by `if cd[-1] else False`, Cl floored by `max(..., 1e-4)` — is **not carried forward**. |
| Zero-value edge case | A zero window mean makes a relative excursion undefined. It **REFUSES (exit 2)**; it is **not** silently floored to an absolute tolerance, which is what the old Cl branch did. |

**Can it see what it must — and the band must be named by KIND, because the limb feeds
two paths whose bands are of different kinds.** Citing one alone is how the ambiguity
arises, and the first draft of this addendum cited the wrong one for this run:

| consumer | band | kind | criterion resolves |
|---|---|---|---|
| **Gate V1** | ±0.10 | **RELATIVE** (`band_cd = (cd_ref*(1−CD_BAND_REL), cd_ref*(1+CD_BAND_REL))`, line 527) — the **tightest** band among the limb's consumers, but on the `grade_ladder` path, which **Stage A never executes** | **20× finer** |
| **Gate A2** | [0.15, 0.60] | **ABSOLUTE** — the band **actually in force for this Stage A run**; half-width 0.225 about a midpoint of 0.375 = 0.60 relative | **≈120× finer** at its midpoint |

Both figures are true of different things. The comparator therefore emits **both**, each
named by kind, in `resolves_finer_than_V1_RELATIVE_band_by` and
`resolves_finer_than_A2_ABSOLUTE_band_by`, with a `band_kinds` string stating which path
is executed. **Reporting the absolute beside the relative is what stops the ambiguity
arising at all.**

**Arming (§2cx).** The limb reports **`armed_by`** and reports **NOT-ARMED rather than
falling silent**: fewer coefficient rows than the window is a **REFUSAL (exit 2)**, never
a pass. **An unarmed gate is a refusal.** This is the defect `ref.get("Cl")` had, where a
missing value removed a gate, its control and its refusal at once and said nothing.

### A1.4 UNSATISFIABILITY GUARD — the mirror of PRD's defect

PRD registered a plateau tolerance **tighter than its own converged ripple**, making it a
criterion a correct run could not satisfy. This repair could commit that sin in reverse.
**So it is written here in advance: if a CONVERGED run's excursion over the 300-sample
window exceeds 0.005, THIS CRITERION IS UNSATISFIABLE, AND THAT IS A FINDING TO REPORT,
NOT A FAIL TO RECORD.** A criterion that cannot be met is as broken as one that cannot
fail. The comparator therefore emits the **measured excursion beside the verdict**, so
the question can be asked of the number rather than of the label.

**And the diagnosis required before that call is written into the note the comparator
emits.** Over 300 samples `(max − min)` is set by the **tails**, so **a single blip
dominates it**. That property is kept deliberately — it makes the criterion conservative,
which is the correct direction for a repair that must not favour the run. But it means
**an unsatisfiability finding must separate genuine drift from one outlier: only genuine
drift means "run longer".**

### A1.5 THE PREDICTION, REGISTERED BEFORE THE DATA

**Registered 2026-09-11T04:50:04Z, at iteration 1175 of 3000 — before this run reaches `endTime` and
before the 300-sample window at `endTime` exists.**

> **PREDICTION: the repaired plateau limb will return `NOT_PLATEAUED` for Cd on this run.**
> By rule 5 limb (1) the rung is then **NOT A RESULT**.
> **If it instead returns PLATEAUED, that is a FINDING and will be reported as one.**

This timestamped prediction **against our own interest** is the evidentiary content this
repair has **in place of a freeze**. Stated honestly: the prediction is **not blind** —
the excursions in A1.1 were measured on the live trace before the rule was fixed. What
protects it is that **the rule in A1.3 was fixed by the supervisor in advance and
implemented without tuning**, that the window is derived from `endTime` rather than
chosen, and that **the 300-sample excursion at `endTime` has not been computed by this
lane**.

**`NOT A RESULT` here is the honest outcome, not a failure of the case.** An 8.35 %
excursion over 500 iterations says the case must run **longer**, not differently. It
routes to a dated successor with a longer run and the repaired criterion registered up
front. **It is not a numerics escalation: the signal is drifting, not oscillating.**

### A1.6 The pin, re-recorded — the §8 row is NOT silently broken

Repairing the comparator changes its hash. Both are recorded:

| | sha256 |
|---|---|
| **OLD** (frozen §8 row) | `0eddb5588c3371140d6e7b75ee763c05048b0f83f8d1917fe3297d9c68908c72` |
| **NEW** (repaired) | `1b51dc1d4438f66a852b104c22f5756c6ca38282e02891fe4f4469e6fe9be44d` |

**The §8 row's pin now refers to the repaired file by this addendum's authority.** §8 is
not edited; this addendum supersedes its comparator hash and nothing else.

### A1.7 Shown able to say both words, and mutation-tested

`--selftest` (ARMING PROOF 4), no arguments, synthetic traces only:

- flat trace → **PLATEAUED** (excursion 6.67e-05)
- drifting trace → **NOT_PLATEAUED** (excursion 3.38e-02)
- oscillation ±0.100 % → **PLATEAUED**; ±2.000 % → **NOT_PLATEAUED**
- **the superseded two-sample test on that same drifting trace → PLATEAUED** — the defect
  demonstrated in the test suite rather than argued
- 10 samples against a 300 window → **REFUSED (exit 2)**, not passed
- zero window mean → **REFUSED (exit 2)**, no silent absolute floor
- `endTime` 20 / 100 / 190 → `W` = 2 / 10 / 19, all below the minimum → **REFUSED
  (exit 2), not clamped**; `endTime` 200 → `W` = 20 → armed
- both band ratios asserted: **20× relative (V1)** and **120× absolute (A2)**

Mutation-tested, as `scripts/openfoam_fault_pattern.py` was: reverting to the two-sample
form, loosening the tolerance 10×, dropping the arming refusal, shrinking the window
fraction to 0.1 %, **reinstating the `max(2, …)` clamp**, and lowering
`MIN_PLATEAU_WINDOW` to 2 — **all six make `--selftest` FAIL**; the unmutated control
passes. The fifth and sixth exist because that clamp was a real defect in the first
draft of this repair, caught in a diff read, and a test now stops it returning. **A criterion
shown able to say only one of the two words is not shown to work.**
