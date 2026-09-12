# VMFL078 — Polyhedral Mesh Accuracy / 3-D Lid-Driven Cubic Cavity (Re = 1000) — PRE-REGISTRATION

**Status: FROZEN 2026-09-12. THE COMMIT CONTAINING THIS LINE IS THE FREEZE.**
Frozen by the ansys-verification-supervisor after personal check 1 (`row_verdict` read as a diff:
four returns, none `PASS`; `plant_into_probe` rewrites the real bytes on disk and is called in the
REAL grading path at `grade_vmfl078.py:611`, not only in `--selftest`; zero bare `assert` in 1,022
lines) and check 4 (run root `verification/runs/ansys_verification/VMFL078` ABSENT, re-asserted in
the committing invocation). Every core-minute figure in sec.7 is a CALIBRATION PREDICTION AND NOT A
CAP-STOP, per Sanaa's directive of 2026-09-12T01:10Z; nothing here may be re-armed as a stop.** Completed by `ansys-lane-opus`
(`claude-opus-5[1m]`) 2026-09-10 for the `ansys-verification-supervisor`, on the
build-plan draft written by `ansys-lane-opus48` 2026-09-02. **No graded solver run has
happened.** The graded run root `verification/runs/ansys_verification/VMFL078/`
**DOES NOT EXIST** — checked 2026-09-10 in the same invocation that wrote this file;
that is the condition under which CLAUDE.md rule 2 makes pre-compute amendment legal,
and it is how it was checked. This registration is frozen by the supervisor's commit;
until that commit exists nothing here has evidentiary force and no solver may start.

This case runs under **`CASE_PROTOCOL_CHARTER.md` v1.0** (in force 2026-09-10), which
governs every 3-D case.

---

## 0. WHAT THIS CASE CAN AND CANNOT PRODUCE — read this before anything else

**`PASS` IS UNAVAILABLE FOR VMFL078 IN THIS ROUND, BY CONSTRUCTION. THE REGISTERED
CEILING IS `GATE REACHED`, AND IT IS REGISTERED HERE BEFORE ANY COMPUTE.**

The reason is a fact about the manual, verified against the PDF and not the sidecar
(rule 15, `ANSYS_VERIFICATION_CHARTER §25.5`):

> **VMFL078 prints no numeric result of any kind.** Its entire "Results Comparison for
> Ansys Fluent" section is one plate — *"Figure .78.2: Comparison of X-Velocity along
> the vertical centerline in the symmetry plane"*, printed page 224 (PDF page 238).
> There is no table, no scalar, no tolerance. The only numbers in the whole case block
> are **inputs** (Re = 1000; density 1 kg/m³; viscosity 0.001 kg/m-s; 1 × 1 × 0.5 m;
> lid 1 m/s) and Ansys's own **mesh size** (279,894 polyhedral cells).

So there is nothing published by VMFL078 that a value can be gated against. A digitized
gate on plate .78.2 is the route, and it is **shut**: `ANSYS_VERIFICATION_CHARTER §25.7`
forbids gating on a digitized reference until a **per-case** digitizer registration
freezes prediction, per-case `u_read` on *that plate's* answer-blind format, band
arithmetic and plate hash. The DIGITIZER instrument itself is certified (R2, both
quantities `PASS`, 2026-09-03) but its own RESULTS record states in terms that it
*"gates no VMFL case"*. No per-case registration exists for plate .78.2.

Therefore the registration is deliberately built as **two limbs with different
ceilings**, and the row verdict is capped:

| limb | what it claims | reference | ceiling | why |
|---|---|---|---|---|
| **A — grid convergence** | our own r = 2 hex family converges at a bounded observed order with bounded GCI on the manual's own centreline quantity | none external | `PASS`-capable **on its own terms** | it is a property of our discretisation and compares against nothing outside the lab |
| **B — the manual comparison** | our centreline profile agrees with Figure .78.2 | Fig. .78.2, p.224 | **`BLOCKED`** | `§25.7` per-case digitizer registration not filed |
| **ROW** | VMFL078 reproduced | — | **`GATE REACHED` maximum** | `VERIFICATION_CHARTER §2`: *"A gate that was not reached is stated as not reached, never replaced by a nearer gate that was."* Limb A **is** the nearer gate. |

**This is not a novel call.** `VMFL054-R3` — the same flow class, a lid-driven cavity
whose manual reference is also *"only a plotted profile"* — landed exactly here:
`GATE REACHED`, register row #69, with the sentence *"A GATE-REACHED row is not a
credential."* VMFL078 is registered at the same ceiling for the same reason, in advance.

**The comparator enforces this in code, not in prose.** `row_verdict()` in
`grade_vmfl078.py` **cannot return `"PASS"`** for any pair of limb verdicts, and the
selftest drives that over the whole verdict cross-product. A mutation that removes the
ceiling turns the suite red (mutation M1, measured).

**What this case IS for.** It is the soonest-runnable genuinely three-dimensional case
in the manual, it reproduces a canonical 3-D benchmark geometry at a scale that is a
real demo (L3 = 1,048,576 cells), and reaching Ansys's own case at all is this team's
win. It is registered honestly as `GATE REACHED`-capped so that nobody discovers the
ceiling after spending the compute.

---

## 1. Case identity and manual provenance

- **Case:** VMFL078, *Polyhedral Mesh Accuracy* — physically the **3-D lid-driven
  CUBIC cavity at Re = 1000**.
- **Manual:** Ansys Fluid Dynamics Verification Manual, **Release 2026 R1, March 2026**,
  printed **pp. 223–224** = **PDF pp. 237–238**.
- **Title-page verification (rule 15, L-144), done 2026-09-10:** PDF page 1 read
  directly with `pdftotext` gives *"Ansys Fluid Dynamics Verification Manual / ANSYS,
  Inc. / Southpointe / 2600 Ansys Drive / Canonsburg, PA 15317 / Release 2026 R1 /
  March 2026"*, and the sidecar
  `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
  head carries the same title, publisher, address, release and date. **Match.** The
  VMFL078 case block itself was then re-read **from the PDF** (pp. 237–238) and agrees
  with the sidecar line for line; every manual quotation below is from that PDF read.
- **Manual's reference:** Jifei Wang & Decheng Wan, *"Parallel Simulation of 3D
  Lid-driven Cubic Cavity Flows by Finite Element Method"*, Proceedings of the
  Twenty-first (2011) International Offshore and Polar Engineering Conference, Maui,
  Hawaii, USA, June 19–24, 2011. **NOT HELD ON THIS BOX** — it is not in
  `docs/papers/`. No number from it is cited anywhere in this registration, and none
  may be cited from recall.
- **Ansys's own run:** *"The flow is steady. Polyhedral mesh of 279894 cells is used to
  discretize the domain."*

## 2. Physics, geometry, boundary conditions

Steady, incompressible, laminar. Manual, verbatim: *"The laminar incompressible flow in
3D driven cavity is solved at Reynolds number = 1000. The study demonstrates accuracy
of polyhedral mesh."*

- ρ = 1 kg/m³, μ = 0.001 kg/m-s ⇒ **ν = 0.001 m²/s**. Re = U·L/ν = 1 × 1 / 0.001 =
  **1000**, the manual's stated number, on the cavity side L = 1 m and lid speed
  U = 1 m/s.
- **THE HALF DOMAIN.** Manual, verbatim: *"A half domain is modeled with height = 1 m,
  length = 1 m and breadth = 0.5 m … using symmetry boundary condition."* The physical
  cavity is the unit **cube** (the reference title says *cubic* cavity); the manual
  halves it across its mid-span plane. Registered domain:

  | axis | extent | meaning |
  |---|---|---|
  | x | [0, 1] | length |
  | y | [0, 1] | height; lid at y = 1 |
  | z | [0, 0.5] | breadth = **half** the cube's 1 m span |

  **⇒ z = 0.5 IS THE MID-SPAN PLANE OF THE FULL CUBE and carries `symmetryPlane`;
  z = 0 is a REAL stationary end wall of the cube.** Getting this the wrong way round
  models a 1 × 1 × 0.5 box rather than half a cube, and it is a mis-specification that
  would still grid-converge and still pass limb A. It is therefore gated exactly, on the
  run's own bytes — see §6.
- **BCs.** Manual, verbatim: *"Moving boundary condition is at the top of the domain
  with a velocity= 1 m/s"* / *"All other walls are stationary"*.
  - `lid` (y = 1): `fixedValue uniform (1 0 0)`
  - `floor` (y = 0), `sideXmin` (x = 0), `sideXmax` (x = 1), `wallZmin` (z = 0): `noSlip`
  - `symmetry` (z = 0.5): `symmetryPlane`
  - pressure: `zeroGradient` on all walls, `symmetryPlane` on the symmetry face; the
    cavity is closed so the level is pinned by `pRefCell 0 / pRefValue 0`.
- **THE MANUAL'S REFERENCE QUANTITY IS DEFINED ON THE SYMMETRY PLANE.** Figure .78.2 is
  *"X-Velocity along the vertical centerline in the symmetry plane"* — that is the line
  **x = 0.5, z = 0.5**, y running up the cavity. In the full cube that is the classic
  cavity centreline. Our sample line **is** that line (§4).

## 3. Grid triple — r = 2, declared a priori

| level | nx × ny × nz | cells | Δx = Δy = Δz | cell Re = U·Δx/ν |
|---|---|---|---|---|
| L1 | 32 × 32 × 16 | 16,384 | 1/32 | 31.25 |
| L2 | 64 × 64 × 32 | 131,072 | 1/64 | 15.63 |
| L3 | 128 × 128 × 64 | **1,048,576** | 1/128 | 7.81 |

- **The 1 : 1 : 0.5 count ratio is deliberate and correct**, and it is *measured*, not
  asserted: it matches the 1 : 1 : 0.5 edge-length ratio exactly, so every cell is a
  **cube**. Stage-2 `checkMesh` on L1 measured **max aspect ratio 1**, max skewness 0,
  max non-orthogonality 0, `Mesh OK`, 0 failed checks. Refinement therefore halves all
  three cell dimensions systematically — the condition a Roache triple rests on.
- **Three levels, ONE triple, so there is no selection freedom** and no anti-fitting
  selection rule is needed. (VMFL054-R3 ran four levels and had to freeze a selection
  rule; this registration removes that degree of freedom instead of constraining it.)
- **DECLARED MESH DIFFERENCE, carried forward from the draft and reaffirmed.** The
  manual demonstrates a **POLYHEDRAL** mesh of 279,894 cells; this lab runs **structured
  hex** (OpenFOAM builds no polyhedra natively). This is a **disclosed modelling
  difference, not a defect** — and it is a further reason `PASS` is unavailable: a hex
  triple can give a clean Roache order while saying nothing about the manual's actual
  claim, which is about polyhedra. **The registration does not pretend otherwise.**
  Limb A's stated claim is about *our* family, and it says so.

## 4. The gate functional — frozen

Sampled on the **frozen line x = 0.5, z = 0.5**, at **201 fixed abscissae**
y = 0.005 … 0.995 (uniform step 0.00495), **identical at every level**, with
`interpolationScheme cellPoint`.

**J = sqrt( (1/(y_hi − y_lo)) ∫ u_x(0.5, y, 0.5)² dy )**, trapezoid over those 201
abscissae. Units m/s.

Three frozen choices and the reason for each:

1. **`cellPoint` interpolation and a frozen abscissa list.** VMFL054 **measured** that
   the default containing-cell sampler reads a slightly different physical location on
   each mesh of an r = 2 family and **polluted the observed order** (p ≈ 0.21, GCI ≈ 11 %).
   That defect is already paid for and is carried here. It is **live, and measured to be
   live**: in the stage-2 dead-lever audit, a `cellPoint` probe and an otherwise
   identical default-interpolation probe on the same solution differ by
   **max 1.7257e-01 m/s across all 201 points**. The comparator **refuses** a
   `controlDict` from which the `cellPoint` line has been deleted, and the mutation
   control confirms that refusal has teeth (M7).
2. **An INTEGRAL functional, not a point value and not an extremum.** An extremum
   carries a locator error that shifts between meshes; a single point at the cavity
   centre is small in magnitude and near a sign change, which inflates relative
   differences. An L2 norm of the whole profile is smooth, O(0.1–0.3), has no locator,
   and is a functional **of the very profile the manual plots**.
3. **The window excludes y = 0 and y = 1.** Those two points carry *exactly* the imposed
   boundary values (0 and 1 m/s) at every level. Including them puts an **identity**
   component into the gate — `VERIFICATION_CHARTER §2a` permits reporting an identity
   and forbids gating on one. y = 0.005 and y = 0.995 lie strictly inside the first and
   last cell at **every** level (the finest, L3, has Δy = 1/128 = 0.0078), so no level
   is treated differently by the choice.

**Secondary, REPORTED and DEMOTE-ONLY:** `min_y u_x` on the same line and its `y`
location, with their own Roache triple. They may turn the row into `NOT A RESULT`; they
can never licence a `PASS`.

## 5. Solver and numerics

- **Solver: `simpleFoam`** (OpenFOAM v2606), steady laminar, **SIMPLEC**
  (`consistent yes`), relaxation U 0.9 / p 0.9. Justification: the manual says *"The
  flow is steady"* and the 3-D cubic cavity at Re = 1000 has a steady solution;
  `simpleFoam` reaches it directly. `icoFoam` would integrate a transient to steady
  state, costing far more for the same answer and forcing a stationarity criterion in
  place of `residualControl`. `simpleFoam` is also this lab's proven instrument for this
  exact flow class (VMFL054-R3, VMFL063).
- **Schemes — CLASS DEFAULT, carried unchanged from VMFL054-R3** (same flow class),
  recorded per Case Protocol §1 as **"class default, first use in 3-D"**:
  `ddt steadyState`; `grad Gauss linear`; `div(phi,U) bounded Gauss linear`;
  `laplacian Gauss linear corrected`; `snGrad corrected`.
- **`div(phi,U)` is UNLIMITED central differencing on purpose.** A limiter is nonlinear
  in the solution and destroys the clean asymptotic order a Roache triple exists to
  measure. **THE DISCLOSED PRICE, STATED BEFORE COMPUTE:** the cell Reynolds number is
  **31.25 / 15.63 / 7.81** at L1 / L2 / L3, above the CD monotonicity limit of 2 at every
  level. Wiggles are **expected** at L1. They are **discretisation error, not
  instability** — and refinement removing them is precisely what the triple measures.
  **The named risk this creates:** the wiggles could break monotone convergence of J and
  return an `OSCILLATORY` triple, which is `NOT A RESULT` under rule 5. That outcome is
  registered here as a foreseen possibility so it can never be offered afterwards as an
  excuse. **The successor path if it happens** is a **new registration** (VMFL078-R2)
  with a family based at L1 = 64, or a limited scheme with a re-derived order band —
  **never a repair of this one.**
- **THE SCHEME IS FROZEN ACROSS ALL THREE LEVELS.** Changing it mid-family voids the
  triple.
- **Solver tolerance is STRICTLY TIGHTER than any gate** (Case Protocol §1, the T23G2Rn2
  rule): `residualControl { p 1e-08; U 1e-09; }`, linear solvers `p` GAMG tol 1e-10 /
  `U` smoothSolver tol 1e-11. Expected level-to-level differences in J are ~1e-3 – 1e-2
  relative; the iterative error is orders below that. The comparator additionally
  **evaluates and gates** the Case Protocol §5 condition that iterative error is at
  least **10×** smaller than the level-to-level difference.
- **`nNonOrthogonalCorrectors 0`**, justified by measurement: the mesh is a perfectly
  orthogonal cube of cubic cells (stage-2 `checkMesh` max non-orthogonality **0**).
- **Ranks: 4, CONSTANT across all three levels**, so that between levels **only the mesh
  changes**. Verified in stage 2: `decomposePar` rc 0, `mpirun -np 4 simpleFoam
  -parallel` rc 0, `End` line present, probes written by the master,
  `reconstructPar -latestTime` yields `U p phi`.
- **`endTime` = 40,000 iterations.** This is an **ITERATION ceiling, not a budget gate**:
  `residualControl` is expected to stop every level well below it (pessimistic estimate
  for L3 is ~19,200 iterations, §7). A level that **reaches** `endTime` without
  converging is `NOT A RESULT` under rule 5 limb 1.

## 6. THE GATE, and its §2a identity test

**LIMB A — grid convergence. Classification: DISCRETE.** It claims a property of our own
r = 2 family and compares against nothing external, so it makes no continuum claim.
(`VERIFICATION_CHARTER §2f.3`'s cap table is headed *"ceiling without a triple"* and does
not fire here: this registration **declares** a triple.)

- Roache at **r = 2, Fs = 1.25** on **J**.
- **`PASS` iff** the triple is `CONVERGING` **and** observed order **p ∈ [1.0, 3.0]**
  **and** **GCI_fine ≤ 5.0 %** **and** the iterative-error margin holds.
- **`GATE FAIL`** if `CONVERGING` but outside either band.
- **`NOT A RESULT`** if any level is not iteratively converged, or the triple is
  `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` (rule 5, in its fixed order, one-way).
- **PROVENANCE OF THE BAND — it is not tuned for this case.** `p ∈ [1.0, 3.0]` and
  `GCI ≤ 5.0 %` are the **class default**, carried **unchanged** from VMFL054-R3, where
  they were frozen before compute for the same flow class, same solver, same SIMPLEC
  settings, same `cellPoint` centreline probe. **A-priori expectation, stated before
  compute:** VMFL054-R3 *measured* **p = 1.195** on that band. Corner/edge singularities
  at the lid dominate the global order in a driven cavity, so ~1.2 is what this case
  should be expected to show, not 2. **THE LIVE FAILURE MODE IS THEREFORE THE BAND'S
  LOWER EDGE:** a genuine p slightly below 1.0 would be a `GATE FAIL`, and that is
  named here rather than discovered later. The band is neither narrowed (which would be
  tuning) nor widened (which would be laxness).

**LIMB B — the manual comparison. `BLOCKED`.** Reference: Figure .78.2, p.224. Blocked
behind `ANSYS_VERIFICATION_CHARTER §25.7`. It takes **no argument from the run** in the
comparator, because nothing the run does could change its answer. **The band arithmetic
is nevertheless frozen here, now, pre-compute AND pre-read-off** — which is exactly what
`§25.2` rule 1 asks for and is the strongest position a later digitized limb can be put
in: `|CFD − ref_digitized| ≤ sqrt(tol² + u_read²)` with **tol = 5 % of the local |u_x|
range**, `u_read` re-derived per `§25.4` on plate .78.2's own answer-blind format, and
`§25.6`'s cap (`u_read ≥ tol/3` ⇒ `GATE REACHED`) applying on top. **Evaluating limb B
requires a separate registration and is not authorised by this one.**

### The §2a identity test, answered in the two required forms

> **(1) What result would make this gate FAIL?** A `CONVERGING` triple with observed
> order outside [1.0, 3.0] — most plausibly *below* 1.0, given the sibling's measured
> 1.195 — or GCI_fine above 5 %. A non-`CONVERGING` triple makes it `NOT A RESULT`.
> J is not derivable from its own inputs: it is a functional of the solved velocity
> field, and the selftest drives that it moves when the profile moves.

> **(2) Could a wrong treatment still PASS it?** **YES, and here is the one that
> could.** A case that put a **no-slip wall at z = 0.5** instead of the symmetry plane
> would model a 1 × 1 × 0.5 box, would still grid-converge cleanly, and would still show
> a respectable observed order — **and it would not be VMFL078.** A wrong lid speed
> would do the same. **So that is gated exactly, and not by a statistic:** the
> comparator reads **each level's own** `constant/polyMesh/boundary` and `0/U` and
> **REFUSES (exit 2)** unless all six patches carry their registered types, the
> `symmetry` patch is `symmetryPlane` in **both** files, and the lid value is exactly
> (1, 0, 0). Measured in the stage-2 dead-lever audit: replacing the symmetry plane with
> a wall changes the centreline by **max 4.56e-01 m/s** — it is a live lever, so this is
> a real failure mode and not a hypothetical one. The mutation control confirms the
> refusal has teeth (M5), and a dedicated selftest covers the case where the mesh and
> the field **disagree**, which only the mesh-type check can catch.
>
> **What remains unguarded, stated plainly:** limb A cannot detect an error that is
> smooth and grid-convergent and *not* expressible as a boundary-condition or mesh
> departure — for instance a wrong viscosity. `ν` is checked only by the case-input
> HEAD-blob hash at launch, which proves the file that runs is the file that was frozen
> but not that the frozen value is right. The frozen value is quoted from the PDF in §2.

## 7. Cost (rule 12) — measured-anchored, and it supersedes three earlier figures

**`cost_basis`: the per-cell-per-iteration rate is MEASURED, on this case's own mesh.
The iteration-growth exponent is MEASURED on sibling cases. The L1 base iteration count
is REASONED, and it is the dominant uncertainty. Dollars are DERIVED, never measured —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER §5`).**

**Measured inputs**

| datum | value | artifact |
|---|---|---|
| 3-D rate on **this case's own L1 mesh** | **2.79e-06 s/cell/iter** | stage-2 bug-check solve, 16,384 cells, marginal over iterations 2–20, box loadavg ≈ 18 on 16 cores ⇒ this is an **UPPER** bound |
| 2-D driven-cavity rate (sibling) | 1.455e-06 s/cell/iter | `verification/runs/ansys_verification/VMFL054-R3/L4/log.simpleFoam`, 102,400 cells × 7,118 iters, ExecutionTime 1060.42 s |
| **⇒ 3-D penalty, MEASURED** | **1.92×** | the ratio of the two above — the "×2 for 3-D" is no longer a guess |
| iteration growth per r = 2 refinement | q = 1.10, 1.35 (VMFL063-R2 L1→L2→L3), **1.84** (VMFL054-R3 L3→L4) | the same logs; q **rises** with refinement, so 1.84 is the right end for our finest step |
| L1 base iterations, sibling anchor | 741 at linear dimension 40 | VMFL054-R3 L1 |

**Reasoned input:** L1 base iterations **N₁ ∈ [741, 1500]**, central **1000** (the
sibling's 741 at nearly the same linear resolution, plus a margin for the stiffer 3-D
pressure–velocity coupling). **The post-freeze smoke pins this**, and it is the single
number most worth measuring first.

**Model:** cost per level scales as 8 × 2^q (cells ×8, iterations ×2^q).

| scenario | rate | N₁ | q | L1 | L2 | L3 | **TRIPLE** | L3 iters |
|---|---|---|---|---|---|---|---|---|
| optimistic | 1.4e-06 | 741 | 1.10 | 0.3 | 4.9 | 83 | **88** | 3,404 |
| **central (REGISTERED)** | **2.8e-06** | **1000** | **1.45** | **0.8** | **16.7** | **365** | **383** | **7,464** |
| conservative | 2.8e-06 | 1000 | 1.84 | 0.8 | 21.9 | 627 | **650** | 12,817 |
| pessimistic | 2.9e-06 | 1500 | 1.84 | 1.2 | 34.0 | 974 | **1,010** | 19,225 |

*(core-minutes; `endTime` = 40,000 has headroom over even the pessimistic 19,225.)*

- **REGISTERED ESTIMATE: 383 core-minutes for the triple**, band **88 – 1,010**.
- **Reference 3× figure: 1,148 core-minutes — RECORDED FOR CALIBRATION, NOT A CAP-STOP
  (§8).**
- **Dollars, DERIVED** at the owner-stated c7a.4xlarge rate $0.0513/core-h (Sanaa
  2026-08-21/22), reported-by-owner and not measured: central **$0.33**, band
  $0.08 – $0.86. Under the $25 pre-authorisation across the whole band; **the binding
  cost here is wall-clock, not money** — ~1.6 h at 4 ranks centrally, up to ~4.2 h
  pessimistically, and longer under the contention this box currently carries.
- **Pre-freeze compute already spent: 0.0547 core-minutes**, all in the scratchpad
  (four short bug-check solves: 1, 20, 20 and 20 iterations on the L1 mesh, plus a
  4-rank parallel check). **No graded run root was created or touched.**

**THIS SUPERSEDES THREE EARLIER FIGURES, and the working is shown so the supersession
can be checked rather than taken:**

1. **The 2026-09-02 draft's "~20–40 core-min"** — low by roughly **10–19×** against the
   registered central figure, and it carried no measured anchor at all.
2. **The supervisor's brief figure, 175–290 core-min** — right order of magnitude, wrong
   model: it assumed a **flat 3,000–5,000 iterations at every level**. Iteration counts
   grow with refinement (measured: q = 1.10 … 1.84), and at L3 that is what dominates.
3. **The supervisor's correction, ~75 core-min** — low by roughly **5×**. Reconstructing
   it: 75 core-min with L3 dominating implies **~1,370 iterations at 128³**, which is
   below the *2-D* sibling's own count at a **coarser** linear resolution (VMFL054-R3
   ran 1,990 iterations at 160²). Its per-cell rate was sound; its iteration base was
   too small.

**Rule 12 calibration duty stands.** At completion the actual is compared with the 383,
the ratio and its attribution (contention / waste / misprediction, waste named
separately) recorded, and a row landed in `docs/COST_CALIBRATION.md`. The exemption in
§8 removes the cap, **not** the calibration.

## 8. THE BUDGET-GATE EXEMPTION — Sanaa's words, and exactly what it does

`CASE_PROTOCOL_CHARTER.md` v1.0, her own closing sentence, verbatim:

> *"and for all these 3D cases that still need to run, i dont want to see any budget
> gates ( time or money). Bc i want to shoot them so we at least have hard 3D demos to
> show and then we can go back to having some restraint"*

VMFL078 is squarely inside that scope: a 3-D case still to run. **Operative effect,
registered:**

- **NO CAP AND NO `timeout` STOPS THIS RUN.** `run_vmfl078.sh` contains no cap
  arithmetic, no running-total drawdown and no `timeout` wrapper. Case Protocol §4's
  *"cap reached: stop, NOT A RESULT"* and CLAUDE.md rule 12's *"an overrun stops the
  run"* are **suspended for this case only**.
- **The only ceiling is `endTime` = 40,000 iterations**, which is a **numerics**
  criterion (the `residualControl` fallback that makes an unconverged level
  `NOT A RESULT` under rule 5), not a budget gate.
- **A non-zero solver rc still stops the run.** That is crash triage, not a budget stop,
  and the exemption does not touch it.
- **Cost is still registered (§7), still MEASURED per level, and still calibrated at
  completion.** The exemption withdraws the gate, not the arithmetic.
- **This run is recorded as having run under the exemption**, per the charter's
  provenance block (*"supervisors record which runs ran under it"*).
- **The exemption is Sanaa's own written directive**, recorded `[SANAA-DIRECT]` in a
  charter at HEAD. It is not any agent's say-so (rule 9).

## 9. Stage-2 bug check — RESULTS (Case Protocol §2), all green

Run 2026-09-10 in the scratchpad on the L1 mesh; **no graded run root exists or was
touched**. Total solver time across all bug-check runs: **3.28 s = 0.0547 core-min.**

| # | check | result |
|---|---|---|
| 1 | `checkMesh` on the coarsest level | **16,384 cells**, `Mesh OK`, **0 failed checks**, max aspect ratio **1**, max skewness **0**, max non-orthogonality **0** |
| 2 | dictionary / schema validation | `foamDictionary` parses all 8 dictionaries and fields: **8/8 OK** |
| 3 | BC closure | all **6** mesh patches present in **both** `0/U` and `0/p`; **0** missing, **0** extra, **no** wildcard or default that could silently fill a hole; `symmetryPlane` present in the mesh boundary file |
| 4 | dead-lever audit | `cellPoint` **LIVE** (max Δ = **1.7257e-01** m/s over 201 points vs default interpolation); `consistent yes` **LIVE** (max Δ = 7.48e-01); `symmetryPlane` **LIVE** (max Δ = 4.56e-01 vs a wall); `ν = 0.001` present; `residualControl` present; `centreHistory` fires (2 rows at 20 iters, interval 10) |
| 4b | probe cardinality | **201/201** centreline probes FOUND, **0** not-found warnings — including those exactly on the symmetry plane (z = 0.5) and on an internal face (x = 0.5). No fallback abscissa needed. |
| 5 | instrument check, **through the real path on real solver output** | P1a: planted **1.234e-03** m/s into one probe, reader saw **1.234000e-03** exactly, no leak to other probes. P1b: all-probe plant moved the **gate functional** by **−1.914e-05** m/s (non-zero). P1c: a **blind writer** (plant to a decoy, graded file untouched) moved it by **0.000000e+00**. BC provenance read all six patch types and the lid value (1, 0, 0) off the run's own bytes. |
| 6 | dry run, **rc read from the PROCESS** | `blockMesh` rc 0; `simpleFoam` rc **0** captured from the process (not a marker); one `End` line; `Time = 1`. Parallel path also proven: `decomposePar` rc 0, `mpirun -np 4 simpleFoam -parallel` rc 0, `reconstructPar` rc 0, `U p phi` present, age-guard ordering correct (fields **newer** than `0/U` in both serial and parallel). |

**No red. Nothing to escalate.**

## 10. The comparator (`grade_vmfl078.py`) — controls

- **`--selftest`: 54/54 PASS, rc 0, under BOTH `python3` and `python3 -O`**, agreeing on
  PASS count, FAIL count and rc. **`ast.Assert` count is 0** in the file and the selftest
  prints that marker under both interpreters — `-O` deletes asserts, so a control written
  as an assert is not a control (L-332).
- **Planted-zero (rule 3):** three plants, all written into the **real bytes on disk** of
  a scratch copy and read back through the **real** reader — single-probe, all-probe
  (must move the gate functional), and a blind-writer negative control. A blind reader
  is **refused**.
- **Strict completion (rule 4) with the AGE GUARD:** rc, `End` line, converged stop,
  `n_exec == steps written`, `U p phi` present at the latest time, and **every field
  newer than the case's own `0/U`**. **Declared frozen departure**, the same one
  VMFL054-R3/VMFL063 froze: this is a `residualControl`-terminated steady solve, so
  *last time == endTime* is the **failure** case; the frozen rule requires a convergence
  line **and** a stop strictly below `endTime`, and treats reaching `endTime` unconverged
  as `NOT A RESULT`.
- **Refuses (exit 2), never degrades**, on: an absent or ambiguous artifact (`one_match`
  refuses on two matches as well as none), a wrong probe count, NaN/Inf, a missing
  `cellPoint`, abscissae that have drifted from the `controlDict` the solver reads, any
  BC departure, an unplanted-but-moving reader.
- **MUTATION CONTROL — the suite is proven able to go RED. Ten mutations, ten red:**

| # | mutation | result |
|---|---|---|
| M1 | remove the `GATE REACHED` ceiling | RED (3 FAIL) |
| M2 | neuter the planted-zero plant | RED (exit 2, refusal) |
| M3 | disable the age guard | RED (2 FAIL) |
| M4 | report a `DIVERGENT` triple as `CONVERGING` | RED (1 FAIL) |
| M5 | accept any mesh patch type | RED (1 FAIL) |
| M6 | widen the frozen order band | RED (3 FAIL) |
| M7 | drop the `cellPoint` requirement | RED (1 FAIL) |
| M8 | probe reader truncates instead of refusing | RED (2 FAIL) |
| M9 | `one_match` picks the first of two | RED (1 FAIL) |
| M10 | limb B stops being `BLOCKED` | RED (3 FAIL) |

**THE MUTATION CONTROL FOUND TWO REAL DEAD CHECKS AND BOTH WERE FIXED BEFORE THIS
REGISTRATION WAS WRITTEN.** On the first pass M5 and M7 stayed **GREEN**: the
mesh-patch-type check had no test that only it could fail (every case was also caught by
the `0/U` check), and the `cellPoint` test was refusing on probe **count** rather than on
the missing fix. Two selftests were added — a mesh/field **disagreement** case, and a
`controlDict` with the right 201 abscissae but `cellPoint` deleted plus its restored
twin — and both mutations then went red. **This is recorded because a mutation control
that finds nothing is usually a mutation control that was not trying.**

## 11. Escalation, registered in advance (Case Protocol §3/§4)

One registered first action per cause class; one change per run; never the same action
twice on the same state; two stops on one cause ⇒ climb; ladder exhausted ⇒ park as
`NOT A RESULT` with the action history and a lesson.

| cause class | registered first action | then |
|---|---|---|
| residual growth / field out of bounds | relaxation U, p 0.9 → 0.7 | pseudo-transient (`ddt` → local Euler with `LTS`) |
| plateau above target, linear solver stalled | GAMG `relTol` 0.01 → 0.001 | `nNonOrthogonalCorrectors` 0 → 1 |
| coherent oscillation in J (the CD-wiggle risk, §5) | **no in-family repair — the scheme is frozen.** Park and register **VMFL078-R2** with an L1 = 64 base or a limited scheme and a re-derived order band | — |
| level reaches `endTime` unconverged | `NOT A RESULT` for the triple (rule 5 limb 1); report the residual reached | successor registration with more iterations |

## 12. Deliverables and freeze list

Files to be committed **in one private-index commit** to constitute the freeze:

- `cases/ansys_verification/VMFL078/PREREGISTRATION.md`  ← this file
- `cases/ansys_verification/VMFL078/grade_vmfl078.py`
- `cases/ansys_verification/VMFL078/run_vmfl078.sh`
- `cases/ansys_verification/VMFL078/QUEUE_ENTRY_STAGED.json`
- `cases/ansys_verification/VMFL078/case/0/U`
- `cases/ansys_verification/VMFL078/case/0/p`
- `cases/ansys_verification/VMFL078/case/constant/transportProperties`
- `cases/ansys_verification/VMFL078/case/constant/momentumTransport`
- `cases/ansys_verification/VMFL078/case/constant/turbulenceProperties`
- `cases/ansys_verification/VMFL078/case/system/blockMeshDict.template`
- `cases/ansys_verification/VMFL078/case/system/controlDict.template`
- `cases/ansys_verification/VMFL078/case/system/fvSchemes`
- `cases/ansys_verification/VMFL078/case/system/fvSolution`

**The grading path is fixed at this commit.** `run_vmfl078.sh` verifies at launch that
`PREREGISTRATION.md`, `grade_vmfl078.py` and **all nine case inputs** are byte-identical
to their HEAD blobs, and aborts otherwise: the file that runs must be the file that was
frozen. `grade_vmfl078.py --verify-frozen` does the same check independently.

**The queue entry is STAGED IN THIS DIRECTORY and has deliberately NOT been written into
`verification/queue/`.** Enqueueing is the supervisor's act, after the freeze commit
exists and its sha can be filled into `prereg_commit`.

**Nothing has been committed and nothing has been launched by the lane that wrote this.**
