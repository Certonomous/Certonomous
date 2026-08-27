# VMFLGPU007 — audit of the INHERITED case skeleton

**Written by `ansys-lane-opus` (lane R2), 2026-08-27, before any pre-registration exists and
at ZERO COMPUTE.** The `case/` and `reference/` trees in this directory were left uncommitted
on disk by the lane killed at ~17:50Z. My brief was to *inspect it, do not assume it is
right, and commit what you keep*. This file records exactly what I checked, what passed, and
what I did **not** check — so that nothing here is mistaken for a verified input later.

**Compute state, measured, not assumed:** there is **no `VMFLGPU007` run root anywhere** —
not `verification/runs/ansys_verification/VMFLGPU007` on the lab box, not on the GPU
instance, and `find /home/ubuntu -iname '*VMFLGPU007*'` outside this case directory returns
nothing on either machine. (`VMFL007` and `VMFL007_R2` under the run tree are the CPU case
VMFL007 — a **different case**, not this one.) **Zero core-minutes and zero GPU-seconds have
been spent on VMFLGPU007.**

`BAND_DECISION_ORDER.md` (inherited, kept) refers to *"a 20-iteration smoke of this case runs
`rc = 0` and writes every artefact"*. **No artefact of that smoke survives on either box**, so
I cannot verify it and **I do not carry it as a measurement.** It is recorded here as an
inherited claim with no surviving evidence. Nothing in the band rests on it.

## VERIFIED IN THIS LANE

| input | what I checked | result |
|---|---|---|
| `reference/VMFL013_htc.xy` | parsed it myself and took the maximum | **peak Nu = 64.8530 at x/H = 5.8209**, 19 two-column rows, x/H spans 0.8206–15.8999. **Exactly the numbers `BAND_DECISION_ORDER.md` fixes the band on** — that document's central claim is independently confirmed. The leading `0 0 0 0` line is a 4-column padding row and is correctly not one of the 19. |
| `constant/thermophysicalProperties` | recomputed the Prandtl number from the manual's own three properties | `Pr = mu·Cp/k = 1e-4 × 10000 / 1.408 = 0.7102272727…`, and the file carries `Pr 0.7102272727272728`. **Internally consistent with the manual's table**, and an air-like Pr as the case requires. `rhoConst rho = 1.0`, `Cp = 10000`, `mu = 1e-4` all match the manual's Material Properties column. |
| `constant/turbulenceProperties` | read against the manual | `RAS { RASModel kEpsilon; … }` — the standard k-ε the manual's Analysis Assumptions block specifies. |
| `constant/g` | read | `(0 0 0)` — gravity off. With `g = 0` the buoyant solver's `p_rgh` is identically `p`; the choice buys a temperature field without introducing buoyancy the manual does not specify. Registered as a modelling choice, not a physical claim. |
| `system/fvSolution.template` | read | solvers `p_rgh` and `"(U|h|k|epsilon)"`, all routed through `petsc` with `__MATTYPE__` / `__VECTYPE__` placeholders — the two-arm GPU/forced-CPU substitution this family uses. |
| `0/T` | read | inlet `fixedValue 300`; **`heatedWall` = `externalWallHeatFluxTemperature`, `mode flux`, `q uniform 1000`** — matching the manual's *"Wall heat transfer, Q̇ = 1,000 W/m²"*. `stepFace`, `ductBottom`, `topWall` are `zeroGradient` (adiabatic). |
| `0/` completeness | drove the repaired guard against a materialised copy | `FIELD COMPLETENESS OK: closure=kEpsilon required={T, U, epsilon, k, p_rgh} all present in 0/` |

## NOT VERIFIED — stated plainly so it is not assumed

- **The mesh.** `system/blockMeshDict.template` has not been read line by line, no `blockMesh`
  has been run, no cell counts confirmed and **no mesh birth certificate exists**. The
  geometry the manual omits (expansion ratio, channel width, upstream and downstream domain
  lengths) has **not** been traced back to the `VMFL013_WB.wbpz` archive by me.
- **The 101-point inlet.** `constant/boundaryData/inlet/{points,0/U,0/k,0/epsilon}` and their
  provenance from `reference/VMFL013_step_ve.set.prof` are **unchecked**; the header comment
  claims 101 points at x = −3.8 H and I did not count them or confirm the mapping.
- **`0/U`, `0/k`, `0/epsilon`, `0/nut`, `0/alphat`, `0/p`, `0/p_rgh` boundary conditions**,
  beyond their existence.
- **`system/fvSchemes`, `system/controlDict.template`** — not read.
- **`reference/VMFL013_nu2.xy`** (Fluent's own wall-4 Nu, 101 rows) — not parsed. It is
  Ansys's own result and is **context, never the gate** (charter §5.1).
- **The adiabatic choice** on the step face and opposite wall is a real degree of freedom —
  Vogel & Eaton heated the downstream wall — and must be registered explicitly in the
  pre-registration as a modelling decision.

**Consequence: this skeleton is committed as INHERITED WORK IN PROGRESS, not as a frozen
input set.** It is not a pre-registration, it freezes nothing, and no gate rests on it. The
unchecked items above must be closed before VMFLGPU007 can be frozen.

## The manual defect, verified in this lane rather than taken on report

The manual's **Test Case** paragraph for VMFLGPU007 (p.243) is **byte-identical to
VMFLGPU006's** (p.239) — 493 bytes, sha256 `97e3b55607077c11…`, sidecar lines 6229–6233
against 6168–6172, confirmed by `cmp`. It describes *"airflow over a Goldman stator blade at
the mid-span … typical of turbomachinery applications"*. **This case is a backward-facing
step. The paragraph is about a different geometry and is not a source of setup for it.**

**A third instance exists and it is legitimate:** the same paragraph appears at sidecar line
5453 under **VMFL071: Mid-Span Flow Over a Goldman Stator Blade** — the CPU Goldman case,
where it belongs — differing only in *"2D"* against VMFLGPU006/007's *"2.5D"*. So the defect
is specifically that **VMFLGPU007 carries VMFLGPU006's paragraph verbatim**, not that the
manual repeats a stock paragraph everywhere.

**What is NOT defective on that page, and this matters for the freeze** — the supervisor's
brief treats the prose as wholly unusable, and it is not:

- The **Reference** field is intact and correct: *J.C. Vogel, J.K. Eaton, "Combined Heat
  Transfer and Fluid Dynamic Measurements Downstream of a Backward-Facing Step", Journal of
  Heat Transfer, Vol. 107, pp. 922–929, 1985.*
- **Physics/Models** is correct and case-specific: *"Incompressible, turbulent flow with heat
  convection and reattachment."*
- **Input File** is correct: `vt007.msh, vmfl007.jou`.
- **The Analysis Assumptions and Modeling Notes block (p.244) is entirely correct and
  case-specific**, and IS a legitimate source of setup: *"The flow is steady and
  incompressible. Fluid properties are considered constant. Pressure based solver is used.
  The inlet boundary conditions are specified using the fully developed profiles for the
  velocity, k, and epsilon. The incoming boundary layer thickness is 1.1 H. Under the given
  pressure conditions, the Reynolds number, ReH is about 28,000. The standard k-ε model with
  standard wall functions is used for accounting turbulence."*
- The **Material Properties** column is correct and complete (ρ, μ, k, Cp) and passes the
  Prandtl consistency check above.

**The Geometry column IS truncated**: it gives `H = 1 m` and nothing else — no expansion
ratio, no channel width, no upstream or downstream domain length. The Boundary Conditions
column also carries a stray bare `I` before the velocity-profile entry.

**So the honest statement the pre-registration must carry is narrower and stronger than
"the prose is defective":** the **Test Case paragraph** is a verbatim copy of another case's
and is not the source of anything; the **Analysis Assumptions block and Material Properties
are sound and ARE sources**; and the **geometry is truncated and must come from the
`VMFL013_WB.wbpz` archive** (charter §2: archives are read for setup and reference numbers
only, never to make a claim about Ansys). The band comes from the digitised Vogel & Eaton
data in `reference/`, not from the manual's figure and not from Ansys's own curve.

**Archive location, measured:** `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/VMFL013_WB.wbpz`.

---

## A BLOCKER FOUND AT COMMIT TIME: the gate's reference data was GITIGNORED

**`.gitignore` line 68 is `*.xy`.** Both inherited reference files —
`reference/VMFL013_htc.xy` (the Vogel & Eaton measurements the band is built on) and
`reference/VMFL013_nu2.xy` (Fluent's own wall-4 curve) — are matched by it and were
therefore **invisible to git**. Confirmed with `git check-ignore -v`, not inferred.

**Why that is a freeze blocker and not a tidiness issue.** Under CLAUDE.md rule 2 the freeze
is the document's entire evidentiary content, and the gate here is
`|Nu_peak − 64.8530| / 64.8530 ≤ 0.20` — a band computed **from that file**. An untracked
reference cannot be cited by blob sha, cannot be shown unchanged between the freeze and the
grade, and could be edited after the answer was known with nothing in git to show it. **A
gate whose reference is untracked is not frozen.** This is the class of the standing lesson
*gitignored is not filed*: a check that asks git is blind to exactly the file that matters.

**The repair follows this family's own precedent rather than inventing one.** VMFLGPU003
faced the same rule and solved it by copying the archive's two-column data **byte-for-byte**
into a `.csv` beside the case (`reference/vmfl011_benchmark_xnorm.csv`, tracked). The same is
done here:

| tracked file (committed) | copied byte-for-byte from (on disk, untracked) | content |
|---|---|---|
| `reference/vmfl013_vogel_eaton_nu.csv` | `reference/VMFL013_htc.xy` | the EXPERIMENTAL reference — Vogel & Eaton 1985 as digitised by Ansys; **this is the file the band cites** |
| `reference/vmfl013_fluent_wall4_nu.csv` | `reference/VMFL013_nu2.xy` | Fluent's own wall-4 Nu, 101 rows — **context only, never the gate** (charter §5.1) |

Byte-identity was verified with `cmp` in the same invocation that made the copies; nothing
was re-digitised, re-fitted, smoothed or re-ordered. **The `.xy` originals stay on disk,
untracked, as the extraction artifacts they are** — they are not force-added past the ignore
rule, because the fix is to have a tracked artifact, not to defeat a rule other teams rely
on. **`.gitignore` is NOT edited by this lane.**

**The pre-registration must cite the `.csv` blob shas**, not the `.xy` paths.

`reference/VMFL013_step_ve.set.prof` is **not** matched by any ignore rule and is committed
under its own name.

---

## AUDIT CLOSURE — 2026-08-27, second pass: the gaps above are now closed except the mesh

Everything listed as *NOT VERIFIED* above has now been read and, where it made a checkable
claim, **checked against the data rather than against its own comments.** Still at zero
compute. Results below; two discrepancies found, one of them in a comment and one in my own
first framing.

### The inlet profile — VERIFIED, and it pins Re_H exactly

`reference/VMFL013_step_ve.set.prof` parsed directly: **101 points**, blocks `x y z
u-velocity v-velocity k epsilon`.

| claim in `blockMeshDict.template` | measured | verdict |
|---|---|---|
| inlet at x = −3.8 H at all points | `x` is −3.8 at all 101 points | **holds** |
| inlet duct spans y = 1..5 | `y` min 1.000000, max 5.000000 — duct height exactly 4 H | **holds** |
| outlet at x = 30 H | `vmfl013_fluent_wall4_nu.csv` carries 101 positions spanning exactly 0.000000..30.000000 | **holds** |
| expansion ratio 5/4 = 1.25 | downstream channel 5 H (y = 0..5) over inlet duct 4 H (y = 1..5) = **1.25** | **holds** — and it is Vogel & Eaton's rig |
| 2-D | `z` ≡ 0 and `v-velocity` ≡ 0 at every point | **holds** |

**A numerics fact worth recording, and it is an exact hit rather than an approximate one.**
The manual says only *"the Reynolds number, ReH is about 28,000"* and never says which
velocity scale defines it. Measured from the archive's own profile with the manual's own
properties (ρ = 1, H = 1, μ = 1e-4, so Re = U × 1e4):

- from **u_max = 2.800000 m/s** → Re_H = **28,000 exactly**
- from the bulk mean (trapezoid over the duct) u_bulk = 2.570882 m/s → Re_H = 25,709

**So Re_H is defined on the FREE-STREAM/MAXIMUM velocity, not the bulk mean.** The exactness
is itself the evidence: 2.8 × 1e4 lands on the manual's figure to the digit, and the bulk
value misses it by 8.2 %. This also confirms the inherited profile really is this case's
profile and not a plausible substitute. The pre-registration must state the velocity scale,
because a reader who assumed "bulk" would compute a different Reynolds number from the same
file and think the case was set up wrongly.

`0/U` applies it with `timeVaryingMappedFixedValue`, **`setAverage false`** — the profile is
used as given, not rescaled to a target mean, which is what makes the u_max identity above
survive into the run.

### `constant/boundaryData/inlet/points` — a COMMENT DISCREPANCY, not a data error

The file's own header says *"101 points"*. **It contains 202.** Measured: **101 distinct y
values spanning 1..5, duplicated across exactly 2 distinct z planes (z = 0.0 and z = 0.1)** —
101 × 2 = 202. `0/U` likewise carries 202 vectors with `ux` max exactly **2.800000**,
matching the `.prof`.

**The data is correct and the duplication is necessary, not sloppy.**
`timeVaryingMappedFixedValue` interpolates from the sample cloud to the patch face centres,
and this 2-D mesh is one cell thick in z with its face centres at z = 0.05; a single plane of
samples at one z would leave the face centres outside the cloud. Bracketing them with two
planes is the standard way to make the mapping well-posed. **Only the header comment is
wrong** — it describes the source profile's point count, not the file's. Recorded here rather
than silently corrected, because the file is inherited and I would rather the discrepancy be
on the record than tidied away.

### The gate reader and the controls — read, and they are named before any run

`system/controlDict.template` (`buoyantSimpleFoam`, `deltaT 1`, `writeControl timeStep`,
`writeInterval = __ENDTIME__`, **no `residualControl`** so the run always reaches `endTime`
and rule 4's *last time == endTime* clause bites):

- **`wallT`** — the GATE READER, and the only one: raw face-centre `T` on `heatedWall` at
  write time. The comparator is to derive `Nu(x) = q''·H / (κ·(T_w(x) − T_inlet))` itself from
  the frozen constants rather than trusting a solver-side Nusselt number. Correct: with a
  fixed wall flux the wall temperature carries the whole gate.
- **`wallTmin`** — the plateau channel, `min(T)` on the heated wall once per SIMPLE iteration.
  Peak Nu occurs where `(T_w − T_in)` is minimum, so this is a **monotone map of the graded
  number, not a proxy for it** — the right choice, and the same liveness lesson VMFLGPU001-R2
  was re-registered for applies to it.
- **`wallFlux`** (`wallHeatFlux`) — control on the flux **actually applied**. The gate divides
  by `q''`; if the BC delivered something else every Nu would be wrong by that ratio and
  nothing else in the run would reveal it.
- **`yPlusFO`** — control on wall-function validity. The manual specifies *standard* wall
  functions, which are only valid in the log layer.
- **`resid`** (`solverInfo` on `U p_rgh h k epsilon`) — per-iteration residuals.

### Schemes and the remaining boundary conditions — read, coherent

`fvSchemes`: `div(phi,U) bounded Gauss linearUpwind grad(U)`; energy, `k` and `epsilon` on
`bounded Gauss limitedLinear 1`. Second-order upwind-biased throughout, with the turbulence
discretisation capping the observed order — consistent with the committed draft's *"p_f ≤ 2;
turbulence caps observed order"*.

`0/k`, `0/epsilon`: `timeVaryingMappedFixedValue` inlet, `kqRWallFunction` /
`epsilonWallFunction` on all four walls. `0/nut`: `nutkWallFunction`. `0/alphat`:
`compressible::alphatJayatillekeWallFunction`, `Prt 0.85`. `0/p_rgh`, `0/p`:
`fixedFluxPressure` walls, `fixedValue 1e5` outlet. **A standard k-ε high-Re wall-function
set, internally consistent, and the closure the manual specifies.**

*Minor observation, not a blocker:* `0/p` carries explicit `fixedFluxPressure` /
`fixedValue` entries where buoyantSimpleFoam normally leaves `p` as `calculated` from
`p_rgh`. With `g = (0 0 0)` the two fields are identical, so this cannot move a number here;
it is noted so nobody later reads it as significant.

### STILL OPEN — the one gap that remains, and it is a real one

- **No mesh has ever been built.** `blockMeshDict.template` is a template: `__NXI__`,
  `__NXD__`, `__NYU__`, `__NYL__`, `__GU__`, `__GUINV__`, `__GC__` and `__H1__` are all
  unresolved, and **no `blockMesh` has run, no cell counts are confirmed, no `checkMesh` has
  passed and no mesh birth certificate exists.** Every geometric dimension the template hard-
  codes is now verified against the archive data, but *the mesh generated from it is not.*
- **The three-level family is NOT a Roache `r = 2` family, and this is load-bearing for the
  gate.** The template holds the first-cell height fixed at a registered `__H1__` across all
  three meshes by solving the grading for it. That is the correct thing to do with standard
  wall functions — refining a wall-function mesh uniformly changes **the model**, not only the
  discretisation, because `y+` moves out of the log layer. But it means **CLAUDE.md rule 5's
  grid triple does not apply in its usual form**: this is a mesh-**sensitivity** family. The
  pre-registration must say so explicitly and must register what the three levels are for,
  because a reader who assumes a Roache triple will expect a GCI that cannot honestly be
  computed here.

**Consequence: the skeleton's INPUTS are now audited and sound; its MESH is not yet real.**
VMFLGPU007 still cannot be frozen — a pre-registration, a launcher and a comparator do not
exist, and the mesh must be built and certified before any of them can cite it.
