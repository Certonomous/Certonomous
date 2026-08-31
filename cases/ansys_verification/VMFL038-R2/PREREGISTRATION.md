# PRE-REGISTRATION — VMFL038-R2: Falling Film Over an Inclined Plane

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — printed
p.131-132 (Overview, Test Case, Geometry, Boundary Conditions, Results Comparison;
sidecar L3509-3557).** Sidecar title-page verified against the PDF beside it under
`CLAUDE.md` rule 15 **by this lane, independently, at 2026-08-31T18:5xZ** — not
inherited from R1, not by filename, file type or hash. The sidecar's first page
(`.txt` L1-14) and the PDF's extracted page 1 both read *"Ansys Fluid Dynamics
Verification Manual / ANSYS, Inc. / Southpointe / 2600 Ansys Drive / Canonsburg, PA
15317 / ansysinfo@ansys.com / http://www.ansys.com / Release 2026 R1 / March 2026"*,
and the p.131 footer reads *"Release 2026 R1 - © ANSYS, Inc. All rights reserved. -
Contains proprietary and confidential information of Synopsys, Inc., ANSYS, Inc.,
subsidiaries and affiliates."*

Drafted by `ansys-lane-opus` (Opus 5), **2026-08-31**, for the supervisor's read. This
is a **frozen file** under `CLAUDE.md` rule 6 from the moment its freeze commit lands:
departures are dated addenda at the foot, never edits above.

**THIS IS A NEW REGISTRATION SUCCEEDING VMFL038-R1. IT IS NOT AN EDIT OF R1.** R1's
frozen files at `cases/ansys_verification/VMFL038/` are untouched by this package, and
**R1's register row #47, `NOT A RESULT`, STANDS**. R1 is superseded as a *plan*, never
retracted as a *record*: its verdict was correct on its own evidence and its grading
record `verification/runs/ansys_verification/VMFL038/GRADING_RECORD_2026-08-31T1710Z.json`
is the source of several numbers quoted below.

---

## 0. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**THE GRADED SOLVER HAS NOT STARTED FOR R2.** The gates, the bands, the floors, the
GCI ceiling, the mesh family, the cap, the labels **and the numerical point
predictions of §10** below are predictions — the entire evidentiary content of this
document.

Checked at **2026-08-31T18:2xZ** by this lane, stated so a reader can re-run each check:

| condition | how it was checked | result |
|---|---|---|
| the R2 graded run root does not exist | `test -e verification/runs/ansys_verification/VMFL038-R2` | **ABSENT** (re-asserted with a UTC timestamp in the freeze commit message) |
| the register carries no VMFL038-R2 row | `grep -c 'VMFL038-R2'` on `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | **0** |
| this case directory holds no `0/` or numeric time directory | the case directory holds only `case/`, this file, the comparator, the mesh generator and the launcher | **no answer on disk** |
| R1's frozen files are untouched | nothing in this package writes to `cases/ansys_verification/VMFL038/` | **untouched** |

### 0.1 A PRE-FREEZE DIAGNOSTIC PROBE WAS RUN, IT MEASURED THE GATE QUANTITIES, AND THE DISCLOSURE IS THE POINT

**This is the most important disclosure in this document and it is made first, not
buried.** Before this freeze, in the scratchpad and **outside `verification/runs/`**,
this lane ran a three-level diagnostic probe of this case at the same geometries the
R2 ladder will use, and **it computed both gate quantities.** R1's registration
forbade itself this and it was right to be careful; this lane did it anyway, on
purpose, because R1 died of a defect that could only be found by looking, and the
honest handling is to say so and to price the cost in evidentiary content.

**What the probe was.** `simpleFoam`, the R2 case inputs, no `residualControl`, run to
a fixed large iteration count at (Nx x Ny) = 90x20 (300 000 iterations, 386 wall-s,
serial), 180x40 and 360x80. Scratch paths only; nothing under
`verification/runs/`; no graded artefact produced.

**What it measured, quoted exactly:**

| probe | quantity | measured |
|---|---|---|
| 90x20, iteration 300 000 | mean physical wall shear over the window, `tau_w` | **39.24000000001422 Pa** — relative deviation from the exact 39.24 of **3.62e-13** |
| 90x20 | column mean streamwise velocity `u_bar` | **0.13096350000002649 m/s** |
| 90x20 | peak cell-centre `u_max` | **0.19620000000000001 m/s** — the analytic peak, to the last digit |
| 90x20 | mean profile error vs the analytic parabola | **1.226250e-04 m/s**, with a spread across the 20 cells of **1.001e-13 m/s** |
| 90x20 | `max\|Uy\|` | **9.85e-12 m/s** |

**THE COST TO THIS FREEZE'S EVIDENTIARY CONTENT, STATED PLAINLY.** A pre-registration's
whole value is that the gate could not have been chosen to fit the answer. **For
`tau_w` and `u_bar` an answer at one of the three graded geometries WAS seen before
this document was written, so that protection is weakened and a reader must discount
it.** What replaces it, and this lane submits it is stronger rather than weaker:

1. **The bands and floors below are derived from arguments stated before any number
   is used** — a round-off scaling argument for the limb-A floor (§5.1), and for the
   limb-B band a criterion fixed by what a KNOWN PAST DEFECT would have done to it
   (§5.2), not by what R2 is expected to do.
2. **§10 registers NUMERICAL POINT PREDICTIONS, to eight or more significant figures,
   for all three levels — including the two levels the probe has NOT converged.** A
   prediction that specific is falsifiable in a way that "we did not look" can never
   be: the analytic error law of §4.3 predicts every value at every mesh, so declining
   to look would have bought the appearance of blindness and none of its substance.
3. The probe is disclosed with its numbers **in the frozen bytes**, so no reader can
   be surprised by it later.

**Amendments before the first GRADED compute are legal and must restate this condition
and how it was checked, naming the run directory that does not exist. After the first
graded compute the gates close: dated addenda only, none altering a gate, threshold,
band, floor, cap or ceiling.**

---

## 1. THE TEN-LINE FORM

```
1.  CASE       : VMFL038-R2 -- Falling film over an inclined plane, manual p.131-132.
                 Solver = simpleFoam (OpenFOAM v2606), steady incompressible laminar,
                 2-D planar (empty front/back), SINGLE-PHASE, GRAVITY-OFF,
                 PRESSURE-DRIVEN. Film delta=0.01 m, plane length L=0.18 m, nu=1/800,
                 outlet kinematic p = -0.8829. IDENTICAL PHYSICS TO R1.
2.  REFERENCE  : Bird, Stewart & Lightfoot, Transport Phenomena p.45 -- the manual's
                 OWN cited Reference. The exact solution of the SAME continuum model
                 simpleFoam discretises; model-form error zero by construction.
                 LIMB A: tau_w = 39.24 Pa.   LIMB B: u_bar = 0.1308 m/s.
3.  GATE VALUES: DERIVED in the comparator to full double precision, two independent
                 routes each, NEVER transcribed:
                 tau_w = mu*2*u_max/delta  and  (dp/L)*delta          -> 39.24 Pa
                 u_bar = (dp/L)*delta^2/(3*mu)  and  (2/3)*u_max      -> 0.1308 m/s
4.  CEILING    : LIMB A: PASS-capable as a FLOOR DEMONSTRATION under VERIFICATION
                 sec.2h.4's five conditions (no triple; sec.2f.3 does not reach it --
                 sec.2h.2). LIMB B: PASS-capable on a CONVERGING triple under ANSYS
                 sec.11.1 -> CLAUDE.md rule 5 step 3.
5.  GATES      : LIMB A (no triple): |tau_w - 39.24|/39.24 <= FLOOR_REL = 1e-8 at
                 EVERY level run, AND the three levels agree with each other to 1e-8.
                 LIMB B (triple):    |u_bar - 0.1308|/0.1308 <= TOL_B = 0.005 at the
                 finest level L3, AND the Roache triple on u_bar is CONVERGING with
                 observed order p >= P_MIN = 1.0, AND fine-grid GCI <= GCI_MAX = 0.02.
6.  DIAGNOSTIC : u_max at the top cell centre (PREDICTED machine-exact, NOT gated --
                 the VMFL070 trap); full-profile error vs the analytic parabola and its
                 spread; wall-shear streamwise uniformity; residual histories.
7.  FAMILY     : ISOTROPIC triple, r=2 in BOTH directions. (Nx,Ny) = (90,20) /
                 (180,40) / (360,80); cells 1 800 / 7 200 / 28 800 -- x4 per level;
                 cell aspect ratio dx/dy = 4 CONSTANT at all three levels. Fs=1.25.
8.  COMPLETION : CLAUDE.md rule 4 IN ITS ORIGINAL FORM, age guard included: last time
                 == endTime, ExecutionTime count == endTime. R1's declared adaptation
                 ("last time STRICTLY LESS THAN endTime") is WITHDRAWN, because R2 does
                 not terminate on residualControl. Iterative convergence is a SEPARATE
                 DISJUNCTIVE clause (sec.6) proved satisfiable in both regimes.
9.  CONTROLS   : planted zero on BOTH channels at ALL THREE levels, to disk, through
                 the production reader, RUN BEFORE ANY CLAUSE THAT CAN REFUSE; GCI
                 ceiling beside the P_MIN floor; NUMERIC time-dir selection with a
                 cardinality refusal; AST guard (0 asserts) over the comparator's own
                 bytes; --selftest green under python3 AND python3 -O; a machine-
                 readable JSON grading record frozen WITH the comparator; value-
                 position placeholder discriminators; writeFields on every
                 surfaceFieldValue/volFieldValue.
10. COST       : EXTRAPOLATED from R1's MEASURED per-cell-per-iteration cost. BRACKET
                 17.0 - 46.4 core-min (lower = uncontended, upper = the contention
                 measured during the probe). CAP 90 core-min RUNNING TOTAL. RANKS=1.
                 Overrun STOPS the run. cost_basis $0.0513/core-h reported-by-owner;
                 dollars DERIVED. 90 core-min = $0.0770 derived.
```

---

## 2. THE CASE, DERIVED FROM THE MANUAL

Manual p.131, quoted for the load-bearing numbers:

> *"Laminar flow of a fluid over an inclined plane, driven by the pressure difference
> due to gravity head is modeled. The flow channel is inclined at an angle β = 30° with
> the horizontal direction."* Material: **density 800 kg/m3, viscosity 1 kg/m-s**.
> Geometry: **1 m X 18 m**, Angle with X-axis = 30°. BCs: **Gauge Pressure at Inlet =
> 0 N/m2, Gauge Pressure at Outlet = -706.32 N/m2**. Reference: **R.B. Bird, W.E.
> Steward, E.N. Lightfoot, Transport Phenomena, p.45, 2005**. Results Comparison:
> **Figure .38.2: Comparison of Velocity Profile at Outlet.**

**The manual's only printed RESULT for this case is a VELOCITY PROFILE** (Figure
.38.2). It prints no wall shear stress. Both of this registration's reference values
are therefore *derived* from the manual's printed inputs via the manual's own cited
closed-form reference — `tau_w` no less than `u_bar` — and neither is transcribed from
Ansys. **Of the two, `u_bar` is the one closer to the quantity the manual actually
reports.** This is recorded because R1's §1 line 6 called velocity a mere
"DIAGNOSTIC"; on the manual's own face it is the reported result.

**THE PHYSICS IS UNCHANGED FROM R1 AND IS NOT RE-OPENED HERE:** single-phase, laminar,
gravity-off, pressure-driven; the free surface is a zero-shear `symmetryPlane`, not a
VOF interface; steady `simpleFoam`, 2-D planar with `empty` front/back.

**THE GEOMETRY IS DERIVED FROM THE MANUAL'S OWN PRINTED NUMBERS, and the archive is
corroboration only:**

| step | identity | value |
|---|---|---|
| L | `Delta_p / (rho*g*sin(beta))` = `706.32 / (800*9.81*sin30)` | **0.18 m** |
| check | `rho*g*sin(beta)*L` reproduces the printed outlet gauge | **706.32 N/m2** exactly |
| delta | `L / 18` from the printed **1:18** aspect ratio | **0.01 m** |
| dp/L | `Delta_p / L` = `rho*g*sin(beta)` (two routes agree) | **3924 Pa/m** |
| u_max | `(dp/L)*delta^2/(2 mu)` | **0.1962 m/s** |
| u_bar | `(dp/L)*delta^2/(3 mu)` = `(2/3) u_max` | **0.1308 m/s** |
| tau_w | `(dp/L)*delta` = `mu*2*u_max/delta` | **39.24 Pa** |

**THE PRINTED "1 m X 18 m" IS A UNITS ERROR — 100x the self-consistent geometry**,
recorded as a finding in `cases/ansys_verification/VMFL038/MANUAL_DEFECT_geometry_units.md`
(**NOT FILED**; submissions are parked, `CLAUDE.md` rule 7). The derived geometry is
used; the printed absolute dimensions are not. **A setup input may come from the
archive; a gate value may not, ever** — no number in this registration comes from
`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/`, and neither archive copy is written
to, moved or deleted by this case.

Under the defect, `tau_w = Delta_p/18` is **scale-invariant** while `u_bar` scales by
100. That cuts both ways and is registered as such: it makes limb A robust to the
defect, and it makes **limb B a live falsifier of the derived geometry** — if the
geometry were wrong by the printed factor, limb B reads 100x high and **GATE FAIL**s
(§11 outcome 4).

**Kinematic conversion.** `nu = mu/rho = 1/800 = 0.00125 m2/s`; outlet kinematic
pressure `-706.32/800 = -0.882900 m2/s2`. `simpleFoam`'s `wallShearStress` is KINEMATIC
(m2/s2); the comparator multiplies by `RHO = 800` to recover physical Pa.

---

## 3. WHY R1 DIED, AND WHAT R2 CHANGES

### 3.1 The supervisor's diagnosis, verified against R1's own frozen artefacts

R1's `run_vmfl038.sh:33` set `NY=(40 80 160)` with **Nx pinned at 180**. Verified from
R1's grading record and `RUN_RC.*`:

| R1 level | Nx | Ny | cells | dx/dy | `tau_w` (Pa) | `u_bar` (m/s) | final Ux residual |
|---|---|---|---|---|---|---|---|
| L1 | 180 | 40 | 7 200 | 4 | 39.23440288031822 | 0.1308167548752285 | 7.889e-07 |
| L2 | 180 | 80 | 14 400 | 8 | 39.209011897243556 | 0.13067972266826913 | 1.4667e-06 |
| L3 | 180 | 160 | 28 800 | 16 | 38.979197204778664 | 0.12972316224257838 | 3.7207e-06 |

Cells went **x2** per level, not x4; the aspect ratio degraded **4 -> 8 -> 16**; the
level-to-level change GREW (`R = d32/d21 = 9.051`) where a 2nd-order scheme must shrink
it fourfold; **the coarsest mesh was the most accurate**; the triple graded `DIVERGENT`
and the row was `NOT A RESULT`. **All of that is confirmed and none of it is disputed.**

### 3.2 A SECOND CAUSE THE R1 POST-MORTEM DID NOT NAME, AND IT IS THE LARGER ONE

**The final `Ux` residual GREW monotonically down R1's ladder — 7.889e-07, 1.4667e-06,
3.7207e-06 — because `residualControl { p 1e-10; }` stops the solve at a fixed
*pressure* residual while the *momentum* field is still moving, and it is further from
settled the finer the mesh.** The probe of §0.1 measured the whole history and makes
this quantitative: the `p` residual first crosses 1e-10 at **iteration 839**, at which
point `Ux` is still at **~1e-7**; `Ux` does not reach its double-precision floor until
**iteration 2597**. R1's levels were stopped, respectively, at 2093, 5340 and 13330
iterations on a criterion that is blind to the quantity being graded.

Consistency check on that claim, using R1's own numbers: at R1's L1 the `tau_w`
shortfall is `1.43e-4` relative and the `u_max` shortfall `2.08e-4` relative — the same
order, in the same direction, at a level whose *discretisation* error §4.3 predicts to
be identically zero. **R1's grid triple was a triple of iterative errors.**

### 3.3 AND A THIRD FINDING, WHICH IS THE ONE THAT FORCED THE GATE STRUCTURE TO CHANGE

This is a disagreement with the ruling this lane was given, stated openly as the brief
invited, and it is settled by proof and by measurement rather than by preference.

> **`tau_w` ON THIS PROBLEM CARRIES NO DISCRETISATION ERROR AT ALL. It is pinned to
> the exact value by DISCRETE GLOBAL MOMENTUM CONSERVATION, on ANY mesh, uniform or
> not, at every refinement level. A Roache triple on `tau_w` is therefore structurally
> `EXACT` — `CLAUDE.md` rule 5 limb (2) — and can only ever grade `NOT A RESULT`. No
> mesh family, isotropic or otherwise, can repair that.**

**The proof.** Take a column of cells at fixed `x` in the developed region and sum the
discrete x-momentum equation over it. The in-column diffusive fluxes telescope, leaving
the free-surface face (zero, `symmetryPlane`) minus the wall face. The streamwise
convective and diffusive fluxes cancel because the field is uniform in `x`. The
pressure source sums to `(dp/L)*delta` per unit width, exactly, because `p` is linear
in `x` and a Gauss gradient of a linear field on this mesh is exact. Hence the discrete
wall flux **equals** `(dp/L)*delta` identically, and `wallShearStress` on a `noSlip`
patch is that same flux, `nu*(U_P - 0)*deltaCoeff`. **`tau_w = 39.24 Pa` to round-off,
independent of `h`.**

**The construction, which gives the whole discrete solution in closed form.** With
`u'' = -K`, `K = (dp/L)/mu = 3924`, the exact profile is `u(y) = K(delta*y - y^2/2)`.
On a uniform mesh of `Ny` cells the interior second-difference is exact on a quadratic
and the `symmetryPlane` cell equation is satisfied exactly; **only the wall cell is
not**, because the one-sided wall gradient `u_1/(h/2)` under-reads `du/dy(0)` by
`K*h/2`. Solving the resulting discrete correction gives a **constant** offset:

> **`u_i^discrete = u_i^exact + K h^2 / 8` for EVERY cell `i`.**

and therefore `u_1^discrete = K*delta*h/2` exactly, so
`tau_w = mu * u_1/(h/2) = mu*K*delta = (dp/L)*delta` — **exact, as the conservation
argument requires.**

**The measurement.** At 90x20 the probe read **39.24000000001422 Pa** (3.62e-13
relative), the mean profile error **1.226250e-04** against the closed-form prediction
`K h^2/8 = 3924*(5e-4)^2/8 =` **1.226250e-04** — agreement to six significant figures —
with a spread across the twenty cells of **1.001e-13**, i.e. the error is a constant
shift to machine precision, exactly as constructed. `u_max` at the top cell centre read
**0.19620000000000001**, the analytic peak: the same construction shows the constant
shift exactly cancels the parabola's curvature deficit at `y = delta - h/2`, so
**`u_max` is machine-exact too — the VMFL070 trap, and the brief was right to fear it,
just about a different channel.**

### 3.4 THE PREDICTION R2 RE-TESTS, AND THE ONE THE SUPERVISOR GOT WRONG

R1's §0 predicted, from its feasibility solve, that *"the velocity field is
machine-exact (`max|Ux| = 0.196200`)"*. **R1's graded run MEASURED it not to be**:
`u_max` came in at **0.194457909143** against the analytic **0.1962** — **0.89 % low** —
with a profile RMS/`u_max` of **6.123e-03**. **The prediction was wrong and it is
recorded as wrong.** §3.3 gives the reason: `u_max` is machine-exact only at
convergence, and R1's L3 was a full 0.89 % short of converged. **R2 re-tests exactly
that prediction** and registers it in §10: `u_max` machine-exact at every level, as a
NON-GATED diagnostic whose failure would falsify §3.3's construction and would be
reported as such.

### 3.5 WHAT R2 CHANGES, AND WHAT IS BYTE-IDENTICAL

Three changes, each named, and the rest held fixed. `diff -rq` of the staged case
inputs against R1's (`cases/ansys_verification/VMFL038/case/`) reports **six files
identical, three differing, and one file present only in R2 by name** — see the
manifest in §12.3.

| # | change | why |
|---|---|---|
| **1 — THE ONE SUBSTANTIVE CHANGE THE SUPERVISOR ORDERED** | `blockMeshDict.template` refines **BOTH `Nx` AND `Ny` by 2** per level. Cells x4; `dx/dy = 4` CONSTANT. | §3.1 — a Roache triple presumes systematic refinement by a constant ratio in all directions. |
| **2 — FORCED BY §3.2** | `fvSolution`: `residualControl` REMOVED; the run goes to a fixed `endTime` past the momentum residual floor. Convergence is decided by the comparator on the disjunctive clause of §6. | R1's stop criterion was blind to the graded quantity and its error grew with refinement. |
| **3 — FORCED BY §3.3** | The **triple moves off `tau_w` and onto `u_bar`**; `tau_w` is kept as a NO-TRIPLE **floor demonstration** (§5.1). `controlDict.template` gains the two history channels the convergence clause reads. | `tau_w` is structurally `EXACT`; `u_bar` carries a genuine, provably 2nd-order discretisation error. |

**Change 3 is a departure from the brief this lane was given, and it is flagged as
one.** The brief fixed the gate on `tau_w` with a Roache triple. Had that been built,
R2 would have graded `NOT A RESULT` via `EXACT` — R1's own registered outcome #3 —
whatever the mesh family. The supervisor may amend this document under rule 2 at any
time before the first graded compute; §0 states the condition and how it was checked so
that such an amendment is legal. **No section of this document defers a gate, band,
threshold, floor, cap, level, ceiling or label to a later decision (ANSYS `§11.2`).**

---

## 4. THE MESH FAMILY, THE TRIPLE, AND THE ANALYTIC ERROR LAW

2-D planar, all-hex, single block, `blockMesh` from
`case/system/blockMeshDict.template` via `make_mesh_vmfl038r2.py`. **UNIFORM grading
(1 1 1).** Origin at the inlet on the plane: `x` streamwise (0 -> 0.18 m), `y`
film-normal (0 = the no-slip `wall`, 0.01 m = the zero-shear `freeSurface`), `z` a
1-cell span (`empty`). Boundaries and their types are byte-identical to R1's.

### 4.1 The three levels — ISOTROPIC, r = 2 IN BOTH DIRECTIONS

| level | Nx | Ny | cells | dx (m) | dy (m) | **dx/dy** |
|---|---|---|---|---|---|---|
| **L1** | 90 | 20 | **1 800** | 2.0e-3 | 5.0e-4 | **4** |
| **L2** | 180 | 40 | **7 200** | 1.0e-3 | 2.5e-4 | **4** |
| **L3** | 360 | 80 | **28 800** | 5.0e-4 | 1.25e-4 | **4** |

**Cells x4 per level. Aspect ratio CONSTANT at 4.** Compare R1: 7 200 / 14 400 / 28 800,
x2 per level, aspect ratio 4 / 8 / 16. The ladder is modelled on VMFL006's, which does
this correctly (4 000 / 16 000 / 64 000, max AR 8.84 / 8.75 / 8.71).

`Ny` runs 20 / 40 / 80 where R1's ran 40 / 80 / 160. **The R2 family is coarser in the
film-normal direction than R1's by one level and finer in the streamwise direction by
one to two.** This is registered rather than glossed: §4.3's error law makes the
film-normal resolution the whole of the discretisation error, so the R2 ladder's finest
level carries a LARGER discretisation error than R1's finest did. That is the price of
holding the aspect ratio constant at a bounded cost, and §5.2's band is set wide enough
to absorb it by a factor of sixty-four.

### 4.2 The functionals

- **LIMB A — `tau_w`:** `RHO` x the mean over the fully-developed streamwise window
  `[0.09, 0.18] m` of `|kinematic wallShearStress_x|` on the `wall` patch, in Pa. Read
  from the WRITTEN FIELD FILE at the converged time, which is what the planted-zero
  control plants into.
- **LIMB B — `u_bar`:** the volume-weighted mean of `U_x` over all cells whose centre
  lies in the same window `[0.09, 0.18] m`, in m/s. On a uniform mesh this is the
  arithmetic mean of the developed columns and equals `Q/delta` per unit width. Read
  from the WRITTEN `U` FIELD FILE, likewise plantable.

Both windows are the downstream half, past any entrance effect. The comparator
**REFUSES** if the wall shear's streamwise peak-to-peak over the window exceeds
`UNIFORM_TOL = 0.05` relative: a non-developed flow makes a single-value gate
meaningless. This is a quality control, not a band.

### 4.3 THE ANALYTIC DISCRETISATION-ERROR LAW, REGISTERED BEFORE THE RUN

From §3.3's construction, on a uniform `Ny`-cell film of thickness `delta` with
`h = delta/Ny` and `K = (dp/L)/mu = 3924`:

| functional | discrete minus exact | order |
|---|---|---|
| `tau_w` | **0** (pinned by discrete global momentum conservation) | — no discretisation error to refine |
| `u(y_i)` at every cell | **`K h^2 / 8`**, a CONSTANT shift | 2 |
| `u_max` at the top cell centre | **0** (the shift cancels the curvature deficit at `y = delta - h/2`) | — machine-exact |
| **`u_bar`** | **`K h^2 / 6`** = `0.0654 / Ny^2` m/s | **2, exactly** |

`u_bar`'s law is the composite midpoint-rule error `K h^2 delta/24` on the exact
parabola plus `delta * K h^2/8` from the constant shift, divided by `delta`. **It is
the reason limb B is gradeable and limb A is not**, and it is what makes §10's point
predictions possible.

### 4.4 The triple, and rule 5

- Functional: **`u_bar`**, per level. `roache(f_L1, f_L2, f_L3)` with `r = 2.0`,
  **`Fs = 1.25`**, observed-order floor **`P_MIN = 1.0`**, round-off floor
  `EXACT_REL = 1e-8`.
- `P_MIN = 1.0` and not R1's 0.05: every scheme in `fvSchemes` is formally second
  order, so a triple that cannot demonstrate even first order has not demonstrated
  systematic refinement. This is a floor on the instrument, fixed a priori.
- A triple that is not `CONVERGING` makes limb B `NOT A RESULT` whatever the value
  (`DIVERGENT`, `OSCILLATORY`, `STAGNANT`, `EXACT`, or `p < P_MIN`). **No GCI is quoted
  in any non-CONVERGING state.** Rule 5 is ONE-WAY: the gate may only turn a would-be
  `PASS` or `GATE FAIL` into `NOT A RESULT`, never the reverse.

---

## 5. THE GATES

### 5.1 LIMB A — `tau_w`, a FLOOR DEMONSTRATION, no triple

```
tau_w(level) = RHO * mean over x in [0.09, 0.18] m of |kinematic wallShearStress_x|
GATE A: |tau_w(level) - 39.24| / 39.24 <= FLOOR_REL = 1e-8   AT EVERY LEVEL RUN
AND     max over levels |tau_w(i) - tau_w(j)| / 39.24 <= FLOOR_REL   (mesh invariance)
```

**THE LIMB'S SENTENCE, WHICH IS THE TEST OF ITS OWN CLASSIFICATION (`§2h.4` cond. 4):**

> *"The discretisation error in the wall shear stress is below 1e-8 relative at 1 800,
> 7 200 and 28 800 cells."*

It says **nothing** about meshes not run (`§2h.4` cond. 5) and it makes **no continuum
claim** — it does not say the solution is correct to 1e-8; it says the discretisation
error is below 1e-8 at the three meshes measured.

**WHY IT IS `PASS`-CAPABLE, AND UNDER WHICH CLAUSE.** `VERIFICATION §2f.3` caps a
CONTINUUM limb without a triple at `GATE REACHED`. `§2h.2` ruled that that cap **does
not reach a floor demonstration**, because §2f.3's ground — *"discretisation error is
not separable from the claim"* — is **inverted** here: the discretisation error IS the
claim. `§2h.4` gives the five conditions, all five declared here before compute:

| # | condition | how R2 meets it |
|---|---|---|
| 1 | the reference is the exact solution of the SAME continuum model | Bird/Stewart/Lightfoot p.45 reduces the steady, fully-developed, unidirectional, laminar, constant-property incompressible Navier-Stokes **exactly** to `mu u'' = dp/dz`. Model-form error zero by construction. |
| 2 | iterative error separately gated by rule 5 limb (1), one-way | §6's disjunctive clause; a level failing it is `NOT A RESULT` regardless of the floor result. |
| 3 | round-off stated with its magnitude and shown negligible | §5.3. |
| 4 | the wording makes no continuum claim | the sentence above. |
| 5 | the claim is bounded by the levels actually run | the sentence names the three cell counts and nothing else. |

**`ANSYS §11.1` point 2 is respected and not overread:** this registration does **not**
decide the question §2h.3 refers to Sanaa, does not claim to, and rests limb A on
`§2h.4`'s express classification, which `§2h.2` holds to govern meanwhile.

**WHERE `FLOOR_REL = 1e-8` COMES FROM — an a-priori round-off argument, stated before
any measured number is used.** Double precision `eps = 2.22e-16`. A functional formed
from `O(N_cell)` face values after `O(N_iter)` sweeps accumulates round-off no faster
than `sqrt(N_cell * N_iter) * eps`; at the worst level of this ladder,
`sqrt(28 800 * 32 000) * 2.22e-16 = 6.7e-12`. `FLOOR_REL = 1e-8` sits **1 500x above**
that estimate, which is the margin a floor should carry when the estimate is a scaling
argument rather than a measurement. It is also 500 000x below limb B's band, so limb A
cannot be met by accident.

### 5.2 LIMB B — `u_bar`, gated on a CONVERGING triple

```
u_bar(level) = volume-weighted mean of U_x over cells with x in [0.09, 0.18] m
GATE B: |u_bar(L3) - 0.1308| / 0.1308 <= TOL_B = 0.005     at the FINEST level
AND     the Roache triple on u_bar is CONVERGING with observed order p >= P_MIN = 1.0
AND     the fine-grid GCI <= GCI_MAX = 0.02
```

**WHERE `TOL_B = 0.5 %` COMES FROM, AND IT IS NOT SET BY WHAT R2 IS EXPECTED TO DO.**
The band is fixed by what a **known past defect** would do to it:

- **R1's measured L3 `u_bar` deficit was 0.82 % relative** (0.12972316224257838 against
  0.1308). **A 0.5 % band GATE FAILs that run.** The band is therefore strictly capable
  of catching the exact failure mode that killed R1, which a 2 % band would not have.
- It is 4x the coarsest level's own analytic discretisation error (`1/(2*20^2)` =
  0.125 %) and 64x the finest's (0.0078 %), so it is a-priori satisfiable by a
  correctly converged solve without being satisfiable by a broken one.
- It would not absorb the manual's units defect: a geometry wrong by the printed factor
  reads 100x high and fails by four orders.

**THE GCI CEILING, BESIDE THE `P_MIN` FLOOR.** `GCI_MAX = 0.02`. A `CONVERGING` triple
whose value sits inside `TOL_B` but whose fine-grid GCI **exceeds** `GCI_MAX` is
**`NOT A RESULT`, not `PASS`**: the discretisation uncertainty would be larger than the
band it must sit inside, and a `PASS` cannot be certified through it. This is the
instrument fix bought twice already (VMFL063 GCI 120.62 %, VMFL069-R2 GCI 145.91 %).
Rule 5 permits the gate to turn a would-be `PASS` into `NOT A RESULT`; it never permits
the reverse.

### 5.3 ROUND-OFF, WITH ITS MAGNITUDE (`§2h.4` condition 3)

The solver is `linux64GccDPInt32Opt` — **double precision**, `eps = 2.22e-16`; the
binary is recorded per level in `RUN_RC.<level>`. Fields are written `ascii` at
`writePrecision 12`, so a written value carries ~1e-12 relative quantisation, which is
**four orders below `FLOOR_REL`** and **nine orders below `TOL_B`**. The scaling
estimate of §5.1 puts accumulated arithmetic round-off at `6.7e-12` relative at the
worst level. **Round-off is negligible against both bands, by the numbers, not by
assurance.**

### 5.4 THE KINEMATIC -> PHYSICAL CONVERSION, ASSUMED AND FALSIFIABLE

The comparator reads the incompressible KINEMATIC wall shear and multiplies by
`RHO = 800`. **ASSUMED:** `simpleFoam`'s `wallShearStress` function object reports
kinematic stress (m2/s2). **Falsifier:** if it carried physical units the limb-A value
would read 800x high and fail the floor by eleven orders — a named outcome (§11
outcome 5), not a silent error.

---

## 6. COMPLETION AND CONVERGENCE — AND THE SATISFIABILITY ARGUMENT

### 6.1 Strict completion (`CLAUDE.md` rule 4, IN ITS ORIGINAL FORM)

Applied at every level; the comparator **REFUSES (exit 2) rather than grading a partial
run.** R2 does not terminate on `residualControl`, so rule 4's canonical clause applies
unadapted and **R1's declared adaptation is WITHDRAWN, not inherited.**

**PHYSICS-CRITICAL — each clause gates:**

1. **`rc = 0`** from `RUN_RC.<level>`, captured **inside** the detached subshell.
2. **An `End` line** in `log.simpleFoam` (exact name, cardinality-guarded).
3. **last `Time` == `endTime`** — rule 4's original clause, restored.
4. **`ExecutionTime` count == `endTime`.**
5. **Fields present at that time:** `U`, `p`, `wallShearStress`, `Cx`, `Cy`.
6. **The NUMERICALLY-latest time directory (`key=float`) equals the log's last `Time`**,
   with a **cardinality refusal** on the match. `sorted(glob(...))[-1]` appears nowhere
   in the comparator (L-339).
7. **AGE GUARD, PER LEVEL.** Every field at `endTime` in **that level's own directory**
   strictly NEWER than **that level's own** `0/U`, which the launcher `touch`es LAST,
   immediately before the solver for that level. The launcher additionally refuses to
   launch into a level directory already holding `0/` or a numeric time directory,
   matched by **regex**, never by a `[0-9]*` glob.

**INFRASTRUCTURE (L-342):** `RUN_RC.<level>`, `COST.txt`, the two history `.dat` files
insofar as they are used only for cost or display. Absent -> reported `NOT MEASURED`,
disclosed, and the grade PROCEEDS on the physics clauses. Present and non-zero rc ->
REFUSE.

### 6.2 THE CONVERGENCE CLAUSE — A DISJUNCTION, AND WHY NO COMBINATION IS UNSATISFIABLE

A level counts as iteratively converged (rule 5 limb (1)) if **C1 OR C2** holds.

- **C1 — DESCENDED.** The final `Ux` **initial** residual in `log.simpleFoam` is
  `<= ITER_RES_FLOOR = 1e-10`.
- **C2 — FLOORED AND FLAT.** Over the final `PLATEAU_FRAC = 25 %` of the sampled
  history: (i) **both** history channels — `tauHistory` (areaAverage of the kinematic
  wall shear on `wall`) and `uBarHistory` (volAverage of `U`) — have relative
  peak-to-peak `<= PLATEAU_TOL = 1e-9`, **AND** (ii) the `Ux` initial residual is no
  longer descending: the median of its last decile is within a factor of 10 of the
  median of its first decile over that window.

> **A RANGE OF EXACTLY ZERO SATISFIES C2(i). It is what full convergence looks like,
> and it is NOT an instrument failure.** VMFL006 died today on the opposite reading —
> a null-range REFUSAL — and this clause is written against that. What licenses
> accepting a null range is not optimism: it is that **the planted-zero control has
> ALREADY RUN, at every level, before this clause is evaluated** (§8), so the reader
> has been shown able to see a non-zero.

**THE SATISFIABILITY ARGUMENT, STATED EXPLICITLY BECAUSE VMFL006 DID NOT HAVE ONE:**

| regime | C1 | C2 | outcome |
|---|---|---|---|
| residual descends past 1e-10 by `endTime` | **holds** | typically also holds | **ACCEPTED** |
| residual floors ABOVE 1e-10 at machine precision, solution stops moving | fails | **holds** — floored is not descending, and a stopped solution has a null or near-null range | **ACCEPTED** |
| residual still descending at `endTime`, above 1e-10 | fails | **fails** — a moving solution has a range far above 1e-9 | **REFUSED**, correctly: rule 5 limb (1) |
| one level floored-and-flat, another still descending | each level is judged on its own limbs | | **each level gets the limb it satisfies** |

**C1 and C2 are ALTERNATIVES, never conjuncts.** VMFL006's clause was a CONJUNCTION —
it demanded a residual floor **and** a non-null functional range, and machine
convergence makes those two jointly unsatisfiable. **No pair of clauses in R2 can be
jointly unsatisfiable, because there is no pair: there is one disjunction, and each
disjunct is individually reachable in the regime it names.** The `--selftest` drives
**every row of that table** over synthetic histories, including an arm that proves the
null-range case is **ACCEPTED** and an arm that proves the still-descending case is
**REFUSED**.

**MEASURED EVIDENCE THAT C1 IS REACHABLE AT EVERY LEVEL** (probe, §0.1, scratch):
the `Ux` initial residual first crosses 1e-10 at iteration **1 495** at 90x20 and
**4 293** at 180x40, and floors at **1.95e-13** and **4.03e-14** respectively. The
`endTime` of each level (§7) is set at 2.5x to 5x the iteration at which C1 is first
satisfied.

---

## 7. THE RUN PLAN AND COST (`CLAUDE.md` rule 12)

### 7.1 `endTime` per level

| level | cells | `endTime` | `Ux < 1e-10` first at (probe) | margin |
|---|---|---|---|---|
| L1 | 1 800 | **8 000** | 1 495 (measured) | 5.4x |
| L2 | 7 200 | **16 000** | 4 293 (measured) | 3.7x |
| L3 | 28 800 | **32 000** | ~12 000 (**EXTRAPOLATED** at the measured x2.8 per level) | ~2.7x |

`__HIST__` = **100** for all levels, so each level yields 80 / 160 / 320 history
samples and `endTime % HIST == 0` (asserted by the launcher).

### 7.2 Cost — EXTRAPOLATED, WITH A BRACKET

| item | value |
|---|---|
| **ranks** | 1 (serial, all three solves) |
| **basis** | R1's MEASURED per-cell-per-iteration cost, from `RUN_RC.*`: L1 14 s / (7 200 x 2 093) = **9.29e-7 s**, L2 79 s / (14 400 x 5 340) = **1.028e-6 s**, L3 372 s / (28 800 x 13 330) = **9.69e-7 s**. Uncontended box. |
| **work** | 8 000 x 1 800 + 16 000 x 7 200 + 32 000 x 28 800 = **1.051e9 cell-iterations** |
| **ESTIMATE — LOWER BRACKET** | at R1's 9.69e-7 s: 1 018 wall-s = **17.0 core-min** |
| **ESTIMATE — UPPER BRACKET** | at **2.65e-6 s**, the rate this lane MEASURED during the probe at 28 800 cells **while two peer 4-rank jobs held 8 of 16 cores**: 2 785 wall-s = **46.4 core-min** |
| **CAP** | **90 core-min, RUNNING TOTAL across L1+L2+L3** — 1.94x the upper bracket. Headroom, and its ground: the upper bracket assumes the contention measured at 18:20Z persists; if it worsens, the cap and not a re-plan is what stops the run. |
| `cost_basis` | c7a.4xlarge at **$0.0513/core-h**, owner-stated 2026-08-21/22 — **REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **DERIVED**. |
| **$ at bracket** | **$0.0145 - $0.0397 derived** |
| **$ at cap** | **$0.0770 derived** |

**LABEL: EXTRAPOLATED, NOT MEASURED.** No R2 solve has run. The per-cell-per-iteration
rates are measured (R1's from its own `RUN_RC.*`, the contended one from this lane's
probe); the iteration counts at L3 are **extrapolated** at the x2.8-per-level scaling
measured across the probe's L1 and L2.

**AN OVERRUN STOPS THE RUN (rule 12).** `endTime` is NEVER reduced to fit the cap.

**THE OPERATIVE GUARD IS THE LAUNCHER'S PER-LEVEL `timeout_s`**, computed as
`remaining_core_min * 60 / RANKS` before each level and applied as
`timeout ${TIMEOUT_S}s` around the solver, with the rc captured **inside** the detached
subshell. **The runner's own cap enforcement is NOT relied on and is NOT claimed to be
`ENFORCE`:** `docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md:3` records it as
ADVISORY/INERT/OFF. That false claim already sits in one frozen file of this team's;
it is not repeated here.

**ESTIMATE-VERSUS-ACTUAL CALIBRATION IS OWED AT COMPLETION** (rule 12): actual
core-minutes from `COST.txt` against this bracket, the ratio, the attribution, and a
row in `docs/COST_CALIBRATION.md`.

### 7.3 Pre-flight smoke (`ANSYS` Amendment 1.4 Clause B)

The launcher's `VMFL_SMOKE=1` mode runs L1 at `endTime 200` **in scratch only** — it
refuses any run root not under a scratch path — proving the toolchain STARTS and that
all three function objects CONSTRUCT (the `writeFields` trap of §8 requirement 8 aborts
at construction, so the smoke catches it before a core-minute is spent on L3). **A
smoke proves the case will START, never that the numerics will hold** — VMFL069-R1
passed a 3-step smoke and diverged at step 65.

---

## 8. THE CONTROLS — eight requirements, each declared here and each DRIVEN TO REFUSAL on real bytes before the freeze

### Requirement 1 — PLANTED ZERO AT EVERY LEVEL, ON BOTH CHANNELS, TO DISK, AND ORDERED FIRST

*A zero from a reader not shown able to see a non-zero is not evidence* (`CLAUDE.md`
rule 3). Two channels x three levels = **six plant records**, all in the JSON.

| stage | what is planted | what must happen |
|---|---|---|
| **P-A** | a SIZED offset `K_PLANT * max\|tau_kin\|` (`K_PLANT = 0.05`), magnitude-INCREASING, on the x-component of **EVERY** `wall` face of a **COPY of the real solver bytes** (header, dimensions and other patches untouched) | every value read back **FROM DISK through the production reader** moves by exactly the plant, and the FULL limb-A functional moves by exactly `RHO * plant` Pa |
| **P-B** | a SIZED offset `K_PLANT * max\|U_x\|` added to the x-component of **EVERY** internal cell of a COPY of the real `U` bytes | the FULL limb-B functional moves by exactly the plant, m/s |

**AND THE ORDERING, WHICH IS THE PART VMFL006 GOT WRONG.** VMFL006's plant registered
**zero entries** because a refusal fired before its plant loop ran, and an absent
control is indistinguishable in a JSON from a control that passed vacuously. The
comparator's phases are therefore **fixed and asserted**:

```
PHASE 0  AST guard over the comparator's own bytes
PHASE 1  discovery only: level dirs, NUMERIC latest time dir, cardinality refusals
PHASE 2  PLANTED ZERO, both channels, ALL THREE LEVELS      <-- BEFORE ANY OTHER CLAUSE
PHASE 3  strict completion (rule 4)
PHASE 4  convergence (sec.6.2 disjunction)
PHASE 5  functionals, uniformity, diagnostics
PHASE 6  triple, limb A floor, limb B gate, verdict
```

Nothing in phases 3-6 can execute before phase 2 has written its six records. **The
`--selftest` proves it with an arm in which a level fails a PHASE 3 completion clause
and the JSON still carries all six plant records.**

**AND THE CONTROL IS SHOWN ABLE TO FAIL.** `--selftest` monkeypatches the writer to a
no-op so the plant never reaches disk, and checks that the control then **REFUSES**; it
also checks the control refuses on a channel that is identically zero. A control never
shown failing is untested.

### Requirement 2 — A GCI CEILING BESIDE THE `P_MIN` FLOOR

`P_MIN = 1.0` (floor on the observed order) and `GCI_MAX = 0.02` (ceiling on the
fine-grid GCI), both registered in §5.2, both reachable arms in `--selftest`.

### Requirement 3 — NUMERIC TIME-DIRECTORY SELECTION WITH A CARDINALITY REFUSAL

`numeric_latest_time_dir()` sorts `key=float`, and every file read goes through
`one_match()`, which **REFUSES unless the pattern matches exactly one path**.
`sorted(glob.glob(...))[-1]` appears nowhere (L-339). `--selftest` builds `0`, `950`,
`2000`, `32000` and shows the numeric selector returns `32000` where the lexicographic
answer would be `950`, and drives the cardinality refusal on a zero-match and on a
two-match.

### Requirement 4 — ZERO `assert`, ENFORCED BY AN AST GUARD OVER THE COMPARATOR'S OWN BYTES

`_ast_guard()` parses the comparator's **own source bytes** and REFUSES if the
`ast.Assert` count is not 0 — `python3 -O` strips asserts, so an `assert` is a control
that vanishes under the optimiser (L-332). The guard reads source, so its count is
identical under both interpreters. It runs in `--selftest` **and** on the grading path,
as PHASE 0.

### Requirement 5 — `--selftest` GREEN UNDER BOTH `python3` AND `python3 -O`

With `__pycache__` cleared before each. Arms prove the gate can return **`PASS`**,
**`GATE FAIL`**, and **EVERY** registered NOT-A-RESULT cause of §11. The launcher runs
both interpreters, requires equal PASS/FAIL counts and rc, the AST marker in both
outputs, and every named control marker present — so a selftest that silently stopped
driving a control cannot pass the launcher.

### Requirement 6 — A MACHINE-READABLE JSON GRADING RECORD, FROZEN WITH THE COMPARATOR

`GRADING_RECORD_<UTC>.json` in the run root, written by the comparator, carrying: both
derivations to full precision, every level's completion and convergence evidence, all
six plant records, both limbs' values and verdicts, the triple with `R`, `p`, GCI and
state, the cost roll-up and the frozen blob shas. **The schema is fixed in the frozen
comparator's own bytes, so the record is frozen with it.** VMFL033-R2 had none and its
verdict had to be read out of stdout; that does not recur here.

### Requirement 7 — VALUE-POSITION DISCRIMINATOR FOR EVERY PLACEHOLDER GUARD

A guard that greps the whole file for `__NY__` cannot tell a **surviving substitution
site** from **the word appearing in a comment**, and it aborts a correct run on the
second. Both sides are therefore checked:

- **Value position:** after substitution the mesh generator parses the
  `hex (...) (NX NY 1) simpleGrading` line and refuses unless the three block counts
  are integers **equal to the requested `Nx`, `Ny`, 1**; the launcher parses
  `endTime <n>;` and the two `executeInterval`/`writeInterval` values in the same way.
- **Token-set containment:** the launcher extracts every `__[A-Z0-9_]+__` token from
  each template and refuses unless that set is a **subset of that launcher's own sed
  set**. **No token appears in a template comment that is not in the sed set** — both
  templates' comments mention only `__NX__`, `__NY__`, `__ENDTIME__` and `__HIST__`,
  all four of which are substituted.

### Requirement 8 — `writeFields` ON EVERY `surfaceFieldValue` / `volFieldValue`

Both `tauHistory` and `uBarHistory` carry `writeFields false;`. In v2606 the source
reads this key unconditionally at construction even though the documentation calls it
optional, and an omission **MPI_ABORTs before the first time step**. The launcher
asserts the key is present in the generated `controlDict` for **every**
`surfaceFieldValue`/`volFieldValue` block, and the pre-flight smoke (§7.3) exercises
construction for real.

---

## 9. ERROR BUDGET — disclosed BEFORE the freeze

**`ANSYS` Amendment 1.4 CLAUSE A (the axisymmetric-wedge bias) DOES NOT APPLY.**
VMFL038-R2 is 2-D planar with `empty` front/back — no wedge, no azimuthal
discretisation, no `sec(t/2)` bias. Recorded as not applying so its absence is not read
as an omission.

| source | magnitude / direction | how obtained |
|---|---|---|
| **Discretisation, limb B** | `K h^2/6` = `0.0654/Ny^2` m/s, positive, exactly 2nd order — the SIGNAL the triple measures and the GCI bounds | §4.3, derived; confirmed to 6 s.f. at 90x20 by the probe |
| **Discretisation, limb A** | **identically zero**, pinned by discrete global momentum conservation | §3.3, proved and measured at 3.62e-13 |
| **Iterative** | `Ux` residual `<= 1e-10` at every level; the residual-to-error amplification measured on R1 is ~180x, so the induced error is `~2e-8` relative — **4 000x below limb B's finest-level discretisation error and 250 000x below `TOL_B`** | §6.2, R1's grading record |
| **Round-off** | `6.7e-12` relative at the worst level; ascii `writePrecision 12` quantisation `~1e-12` | §5.3 |
| **Kinematic->physical** | **ASSUMED** kinematic; falsifier reads 800x high -> limb A fails by eleven orders | §5.4 |
| **Manual units error** | the printed `1 m x 18 m` is 100x; the derived `0.01 x 0.18` is used. Limb A is scale-invariant to it; **limb B is a live falsifier of it** | §2 |
| **Reference resolution** | `39.24` and `0.1308` are exact rationals of the printed inputs, not rounded table entries | §2 |
| **Free-surface idealisation** | fixed-thickness zero-shear top (`symmetryPlane`) — the manual's own model, so it is a property of the case, not an error against it | manual p.131 |
| **Streamwise resolution** | now refined with `Ny`; the developed field is uniform in `x` to `~1e-10` (probe p2p), so this contributes nothing measurable and is listed to say so | §4.1 |

**None of these widens a band. The bands are `FLOOR_REL = 1e-8` and `TOL_B = 0.005`,
and the disclosure obligation is on the disclosure, never on the tolerance.**

---

## 10. THE NUMERICAL POINT PREDICTIONS — the falsifiable content of this document

Registered **before** any graded compute, to eight or more significant figures, from
§4.3's analytic law. `K = 3924`, `delta = 0.01`, `h = delta/Ny`.

| level | Ny | predicted `u_bar` (m/s) | predicted rel. dev. | predicted `tau_w` (Pa) | predicted `u_max` (m/s) | predicted profile shift (m/s) |
|---|---|---|---|---|---|---|
| L1 | 20 | **0.13096350000** | +1.2500e-03 | **39.24** to <1e-8 | **0.1962** machine-exact | 1.2262500e-04 |
| L2 | 40 | **0.13084087500** | +3.1250e-04 | **39.24** to <1e-8 | **0.1962** machine-exact | 3.0656250e-05 |
| L3 | 80 | **0.13081021875** | +7.8125e-05 | **39.24** to <1e-8 | **0.1962** machine-exact | 7.6640625e-06 |

Derived triple quantities, likewise predicted:

| quantity | prediction |
|---|---|
| `d21 = f2 - f1` | **-1.22625000e-04** |
| `d32 = f3 - f2` | **-3.06562500e-05** |
| `R = d32/d21` | **+0.25** -> `0 < R < 1` -> **`CONVERGING`** |
| observed order `p` | **2.0000000** |
| fine-grid GCI at `Fs = 1.25` | **9.7648e-05** = **0.0097648 %** — 205x below `GCI_MAX` |

**HOW EACH PREDICTION CAN FAIL, WHICH IS WHAT MAKES IT A PREDICTION.** If `u_bar` at
L3 misses 0.13081021875 by more than the iterative-error budget of §9, §4.3's law is
wrong and the observed order will say so. If `p` comes back near 1 rather than 2, the
wall-cell treatment is not what §3.3 derives. If `tau_w` drifts across levels, discrete
global momentum conservation is not doing what §3.3 proves, and **limb A fails its own
floor** — this lane would rather be caught by that than protected from it. **This lane
declines to say which of §11's outcomes lands.**

---

## 11. NAMED LIVE OUTCOMES — every one can happen, each written down now

The fixed vocabulary and nothing else (`CLAUDE.md` rule 1). Limbs are graded and
reported **separately**; the ROW verdict is the **weakest** limb verdict, in the order
`NOT A RESULT` < `GATE FAIL` < `GATE REACHED` < `PASS`.

| # | outcome | the condition that produces it |
|---|---|---|
| 1 | **`PASS` on limb A** | `tau_w` within `FLOOR_REL = 1e-8` of 39.24 at all three levels AND mesh-invariant to 1e-8, with every level iteratively converged. A floor demonstration under `§2h.4`. |
| 2 | **`PASS` on limb B** | triple `CONVERGING` with `p >= 1.0`, L3 inside the 0.5 % band, fine-grid GCI <= 2 %. A credential. |
| 3 | **`GATE FAIL` on limb A** | `tau_w` outside `1e-8` at any level, or the levels disagreeing by more than `1e-8`. **This falsifies §3.3's conservation proof and would be the single most valuable finding R2 can produce**, and it is recorded with its numbers, not explained away. |
| 4 | **`GATE FAIL` on limb B** | triple `CONVERGING` but L3 outside the 0.5 % band. Includes the geometry falsifier (a 100x reading if the printed dimensions were right after all) and the R1-style iterative deficit (0.82 % would fail). |
| 5 | **`GATE FAIL` — the units assumption** | `wallShearStress` turning out to be physical rather than kinematic: limb A reads 800x high. |
| 6 | **`NOT A RESULT` — triple `EXACT`** | both `u_bar` differences fall below `EXACT_REL*\|f3\| = 1e-8*0.1308 = 1.3e-9`. **Predicted differences are 1.2e-4 and 3.1e-5, five orders above the floor, so this is not expected on limb B — but it is registered as live, and it is exactly what §3.3 shows WOULD have happened had the triple been left on `tau_w`.** |
| 7 | **`NOT A RESULT` — GCI > `GCI_MAX`** | triple `CONVERGING`, value inside the band, fine-grid GCI > 2 %. |
| 8 | **`NOT A RESULT` — `p < P_MIN`** | observed order below 1.0: the family has not demonstrated systematic refinement. |
| 9 | **`NOT A RESULT` — triple not `CONVERGING`** | `DIVERGENT` (`R >= 1`), `OSCILLATORY` (`R < 0`), `STAGNANT`. No GCI printed in any of these states. |
| 10 | **`NOT A RESULT` — a level not iteratively converged** | §6.2's disjunction failing at any level: still descending at `endTime` and not flat. Rule 5 limb (1), one-way. |
| 11 | **`NOT A RESULT` — completion clause failed** | missing `End`, last `Time != endTime`, `ExecutionTime` mismatch, a missing field, the per-level age guard, a recorded non-zero rc, or the numeric time-directory cross-check disagreeing. |
| 12 | **`NOT A RESULT` — a control did not fire** | either plant stage unseen at any level on either channel; `one_match()` matching != 1; the AST guard finding an `assert`; a non-developed (non-uniform) wall window. |
| 13 | **`BLOCKED`** | the toolchain is absent (no `simpleFoam`, no `blockMesh`), or `blockMesh` fails, or a function object fails to construct. **A crash is a FINDING, not a retry.** |
| 14 | **`PENDING`** | registered and not yet run — the state this document is in as it is committed. |

**THE PREDICTION, and it is the falsifiable content of this document:** the gates above
can return any of outcomes 1-13; they are not constructed so that only one answer is
possible. The `--selftest` proves the machinery CAN return `PASS`, `GATE FAIL` and
**every** registered `NOT A RESULT` cause, each on an end-to-end arm.

---

## 12. THE GRADING PATH, FROZEN

### 12.1 Artefacts

| artefact | path |
|---|---|
| pre-registration | `cases/ansys_verification/VMFL038-R2/PREREGISTRATION.md` (this file) |
| comparator | `cases/ansys_verification/VMFL038-R2/grade_vmfl038r2.py` |
| mesh generator | `cases/ansys_verification/VMFL038-R2/make_mesh_vmfl038r2.py` |
| launcher | `cases/ansys_verification/VMFL038-R2/run_vmfl038r2.sh` |
| case inputs | `cases/ansys_verification/VMFL038-R2/case/` — 9 files |
| manual-defect note (R1's, cited not copied) | `cases/ansys_verification/VMFL038/MANUAL_DEFECT_geometry_units.md` (**NOT FILED**) |
| graded run root | `verification/runs/ansys_verification/VMFL038-R2/` — **does not exist at this freeze** |

### 12.2 What the launcher refuses to spend a core-minute without

At launch: this file, the comparator, the mesh generator and all 9 case inputs hash
equal to their **HEAD blobs**; the comparator's `--selftest` green under **both**
interpreters with equal PASS/FAIL counts, equal rc, the AST marker in both, and every
named control marker present; each level directory holding no `0/` and no numeric time
directory; `endTime % HIST == 0`; the placeholder value-position and token-subset checks
of requirement 7; and `writeFields` present in every fieldValue block. It records the
blobs in `LAUNCH_RECORD.txt` and mints a `birth_certificate.json` per level.
`grade_vmfl038r2.py --verify-frozen` re-hashes this file and the comparator against
HEAD at grade time and returns rc 2 on any mismatch.

**A FILE'S STATE IS ASSERTED AGAINST `git show HEAD:<path>`, NEVER against `git status`
or `git diff HEAD`** (`ANSYS §11.5`): the shared index is three days stale and holds
foreign staged deletions, so porcelain reports intact files as deleted.

### 12.3 What is byte-identical to R1, and what is not

`diff -rq cases/ansys_verification/VMFL038/case cases/ansys_verification/VMFL038-R2/case`:

| file | state |
|---|---|
| `0/U` | **IDENTICAL** to R1, byte for byte |
| `0/p` | **IDENTICAL** |
| `constant/transportProperties` | **IDENTICAL** |
| `constant/momentumTransport` | **IDENTICAL** |
| `constant/turbulenceProperties` | **IDENTICAL** |
| `system/fvSchemes` | **IDENTICAL** |
| `system/blockMeshDict.template` | **DIFFERS** — `Nx` becomes `__NX__` (change 1) |
| `system/controlDict.template` | **DIFFERS** — fixed `endTime`, the two `__HIST__` history channels with `writeFields` (changes 2, 3) |
| `system/fvSolution` | **DIFFERS** — `residualControl` removed (change 2) |

**Six identical, three differing. The physics files are all in the identical set; every
differing file is one of the three named changes of §3.5.** The exact `diff -rq` output
is recorded in the freeze commit message.

---

## 13. WHAT THIS REGISTRATION DOES NOT CLAIM

- **It is not a statement about Ansys.** This box has no Ansys solver. It is a
  statement about this lab's `simpleFoam` against Bird/Stewart/Lightfoot's exact
  solution.
- **It does not retract R1.** Row #47 `NOT A RESULT` stands on its own evidence.
- **It does not claim the archive's setup.** Geometry is derived from the manual; the
  archive is corroboration only, never a source.
- **It establishes nothing about meshes outside 1 800 - 28 800 cells**, nor about the
  aspect ratios R1 explored and R2 does not.
- **It does not decide the question `VERIFICATION §2h.3` refers to Sanaa** — whether an
  exact-solution reference should be `PASS`-capable in a no-triple registration
  generally. Limb A rests on `§2h.4`'s five express conditions and nothing wider.
- **`u_max` is a diagnostic, not a result.** No verdict rests on it, precisely because
  it is predicted machine-exact (the VMFL070 trap).
- **Nothing here is sent anywhere.** Submissions are parked; the manual is proprietary
  Ansys documentation held for this lab's private use (`CLAUDE.md` rules 7 and 8).
