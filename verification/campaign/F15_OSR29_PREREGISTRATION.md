# F15 — PRE-REGISTRATION: oblique shock reflection at M∞ = 2.9

**Team:** cfd. **Written before any compute. ZERO CORE-MINUTES SPENT.**
**Status at freeze: ARMED — never run.**
Frozen by the commit that carries this file. After first compute the gates,
thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them.

---

## 1. WHY THIS CASE

**It supplies BOTH halves of the lab's largest structural gap, in one row.**
No row in this lab currently joins a **known answer** to a **converging grid
ladder**: the exact-solution rows carry no Roache triple, and the one clean
triple has no known answer. This case has a closed-form exact solution *and* a
three-level ladder graded through `grade_ladder`.

Its solution is **discontinuous**, so its L1 error can converge no faster than
first order whatever the interior scheme. Its sibling registration
`F16_SL2_PREREGISTRATION.md` is **smooth**, and must recover second order. The
two brackets the two convergence regimes deliberately.

## 2. THE CASE, AND WHERE IT COMES FROM

**Source:** Ekaterinaris, *"High-order accurate, low numerical diffusion methods
for aerodynamics"*, **Progress in Aerospace Sciences 41 (2005) 192–300, page
243** — the paragraph beginning *"The oblique shock reflection problem at
M∞ = 2.9 is chosen as test case"*. Title-page verified per standing rule 15;
identification committed at `ff5710e2`, provenance at
`docs/standards/High_order_grid_convergence_PROVENANCE.md`.

> **THAT PAPER IS CITED FOR THE CASE DEFINITION AND FOR NOTHING ELSE.** Measured
> over its 66,033-word extraction against a planted control that returned
> non-zero: `Richardson` 0, `Roache` 0, `GCI` 0, `grid convergence index` 0,
> `observed order` 0, `grid refinement` 0. **No convergence methodology is
> sourced to it and none may be.** `MESH_STANDARD.md` §10 already records it as
> NOT A SOURCE for exactly that. Rule 5 is reached through
> `scripts/roache_triple.py::grade_ladder` and through nothing else.

**What the paper gives:** M∞ = 2.9; domain −2 ≤ x ≤ 2, 0 ≤ y ≤ 1; a 200 × 50
uniform grid; free stream at the left inflow; extrapolation at the right
outflow; slip wall at y = 0; top boundary ρ = 1.69997, u = 2.61934, v = −0.506,
p = 1.528; and the graded reference *"the pressure at y = 0.5"*.

**What it does not give, and how that is closed rather than assumed:** the
incident shock angle and the free-stream primitives are **recovered** —
ρ₁ = 1, a₁ = 1, p₁ = 1/γ, u₁ = 2.9, incident shock at **β = 29°** — and the
recovery is **checked against the paper's own printed numbers**. Residuals of
the recovered region-2 state against the paper: **ρ 3.71e−06, u 2.10e−06,
v 3.20e−04, p 1.94e−04** (v and p checked at the paper's printed precision,
which is 3 and 4 digits). A **planted control** perturbs β to 31° and the check
**refuses**. Artifact: `cases/F15_oblique_shock_reflection/exact_osr.py
--selftest`.

**Independently corroborated:** OpenFOAM v2606 ships
`tutorials/compressible/rhoCentralFoam/obliqueShock`, which is **this same
case** — same M = 2.9, same top state (2.61933 −0.50632 0). Its boundary
**types**, `fluxScheme Kurganov`, vanLeer reconstruction and `endTime 10` are
inherited verbatim. **The tutorial performs no grid ladder, cites no exact
solution and has no gate; that is what this registration adds.**

## 3. THE EXACT SOLUTION (the known answer)

Three uniform regions separated by the incident and reflected shocks, from the
oblique Rankine–Hugoniot relations. Rankine–Hugoniot residuals across both
shocks: **worst 8.88e−16** (mass, normal momentum, tangential velocity, energy).

| region | ρ | u | v | p | M |
|---|---|---|---|---|---|
| 1 free stream | 1.000000000 | 2.900000000 | 0.000000000 | 0.714285714 | 2.900000000 |
| 2 behind incident | 1.699966291 | 2.619342099 | −0.506320255 | 1.528193626 | 2.378071921 |
| 3 behind reflected | 2.687226628 | 2.401505065 | 0.000000000 | 2.933980608 | 1.942419444 |

Deflection **10.940374°**; incident shock **−29.000000°** from x; reflected
shock **+23.279100°** from x; wall impingement **x_w = −0.195952244728576**;
the reflected shock exits the right (supersonic, M₃ = 1.942) boundary at
**y = 0.944777**, inside the domain — checked, because a shock leaving through
the top would contradict the imposed top state.

## 4. THE LADDER — THREE LEVELS, WHICH IS THE STANDARD

Square cells at every level, refined by exactly 2 in **both** directions, so the
three meshes are **geometrically similar** and the triple is a triple.

| level | grid | cells | Δx = Δy | ranks |
|---|---|---|---|---|
| coarse | 200 × 50 | 10 000 | 0.020 | 1 |
| medium | 400 × 100 | 40 000 | 0.010 | 4 |
| fine | 800 × 200 | 160 000 | 0.005 | 8 |

The coarse level **is the paper's own grid**. `dim = 2`; `grade_ladder` refuses
below three levels (driven: 3 → PASS, 2 → REFUSED, 1 → REFUSED).

**Solver:** `rhoCentralFoam`, **inviscid** (μ = 0), `endTime 10`, `maxCo 0.2`,
`adjustTimeStep yes`, `ddtSchemes Euler`. The graded quantities are
**steady-state** values reached by pseudo-time marching, so the temporal order
does **not** enter the spatial ladder.

**DECOMPOSITION SEED (required field):** method `simple`, coefficients
`(ranks 1 1)`. **Seed: `none`** — `simple` is a deterministic geometric
partition with no RNG, so it is bit-reproducible from the rank count alone.
`scotch` is *not* used precisely because its partition is not reproducible from
a recorded field. **At the coarse level `decomposePar` IS NOT INVOKED** (serial);
recorded explicitly rather than inferred from its absence.

## 5. THE GATES AND THEIR BANDS

**Both bands descend from ONE declared parameter, `N_CAPTURE_CELLS = 8`** — the
number of cells a limited second-order shock-capturing scheme is *allowed* to
smear one steady oblique shock over. Declared now, not measured, not fitted, not
revisable after first compute.

### G-F15-1 — normalised L1 pressure error along y = 0.5

    E1 = (1 / (L·p1)) ∫ |p_num(x) − p_exact(x)| dx

**Derivation, so a reader can check it.** A conservative scheme smears a
discontinuity over at least one cell. A step of height Δp reproduced as a
monotone linear ramp of width n·Δx contributes exactly **n·Δp·Δx / 4** to
∫|p_num − p_exact|. Two discontinuities cross y = 0.5, so

    E1(n) = n·Δx·(Δp_incident + Δp_reflected) / (4·L·p1) = n·Δx·c,
    c = (0.813908 + 1.405787) / (4 × 4 × 0.714286) = 0.194223303182

At Δx_fine = 0.005: **band = [E1(1), E1(8)] = [9.711165159e−04,
7.768932127e−03]**. Below one cell is impossible for a conservative scheme;
above eight is more smearing than the declared allowance.

### G-F15-2 — incident-shock wall impingement x_w

Half-rise crossing of the wall pressure, **linearly interpolated** between the
two bracketing cell centres so the estimate is sub-cell and continuous (a
cell-centre estimate is quantised and would make the triple `STAGNANT` for
reasons unrelated to the solution).

**Same allowance in the same units:** a shock captured over n cells places its
half-rise no better than ±(n/2)·Δx. **Band = −0.195952244729 ± 0.020000000000
= [−0.215952244729, −0.175952244729].**

**Neither number comes from a measured deviation. At freeze no run of this case
exists anywhere on this box.**

## 6. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING, and nothing else.
- **Rule 5 is reached through `grade_ladder` ONLY.** `grade_f15.py` carries
  **exactly one** `grade_ladder` call node, censused by **AST** at every entry —
  a regex counts prose, and an earlier draft of this file had a *comment* saying
  "the one and only gate call" that a naive matcher scored as a third gate. The
  text matcher is separately driven **both ways** on synthetic files (a miss on
  a file with no call, a hit on a planted call) so the terminal-reproducible
  evidence is itself controlled.
- **CONVERGENCE GATE: CLASS C**, all four elements
  (`CFD_CONVERGENCE_GATE_RULING_2026-08-25.md` §2). Sustained window **60
  samples = 3.0 time units = 2.2 flow-throughs**, longer than any single
  traverse of the domain, so a wave crossing the sampled line cannot sit inside
  the window. Trend fit rejecting a growing series at 2.0e−3 relative drift.
  Explicit two-half stationarity test on mean and variance ratio, **shown able
  to report NOT stationary**. **Element 4: fewer than 100 samples EXITS 2** — it
  does not return a state. All four limbs are driven by a planted control:
  flat → PLATEAUED, ramp → NOT_PLATEAUED_TREND, step → NOT_STATIONARY_MEAN,
  5-sample series → exit 2.
- **Rule 5 limb (1), honestly.** An **inviscid** `rhoCentralFoam` run performs
  **no linear solves**, so there is **no solver residual to read**. The
  iterative state is measured from a **whole-field** monitor — the
  volume-averaged pressure written by a `volFieldValue` functionObject — under
  the same Class C test, and the plateau state from the **graded functional
  itself**, recomputed at every sampled time from that time's own artifact.
  Two genuinely different measurements, not one relabelled twice. Reporting an
  absent residual as CONVERGED would not be honest and is not done.
- **Completion (standing rule 4):** rc = 0; an `End` line; **`latest + dt_final
  > endTime`** — never `latest >= endTime` (it refused 4 of 9 genuinely complete
  F4 runs) and never a two-sided tolerance; `T U p` present at `endTime`; and
  **every one newer than the case's own `0/T`** (age guard). **The
  `ExecutionTime count == endTime` clause is a FIXED-Δt identity and does not
  apply to this adaptive-Δt run**; the substitution is recorded here rather than
  left silent.
- **Planted-zero controls (rule 3)**, into the **real artifact**, read back with
  the **real parser**, refusing with exit 2. For E1 a known p-column offset moves
  every pointwise error by exactly that offset, so the post-plant value is
  *predicted* from the pre-plant array and must be reproduced to 1e−12. For x_w
  an x-column shift must move the crossing by **exactly** that shift (1e−10).
- **`assert` census: ZERO**, by AST parse, across `grade_f15.py` and
  `exact_osr.py` (L-332). **Hard `-O` refusal at entry, `sys.exit(2)` before
  anything else runs**, driven and confirmed: `python3 -O grade_f15.py
  --selftest` → **rc 2**. `grade_ladder` reaches its gate through four `assert`s
  in the shared `roache_triple.py` (`:195, :632, :634, :637`) carrying standing
  rules 1 and 5; **that file is referred to verification and is not cfd's to
  edit**, so the refusal is placed at the boundary F15 owns.
- **Success messages print INSIDE the passing branch.** The selftest's
  `SELFTEST GREEN` line is unreachable unless the predicate returned true.
- **Guards.** The launcher **REFUSES** a pre-existing `0/` or numeric time
  directory; it does not delete. **There is no `rm -rf` and no `shutil.rmtree`
  on any case directory anywhere in this rung** — the graders' `rmtree` calls
  act only on `tempfile.mkdtemp` scratch trees created for plant controls.
- **`--preflight` fires nothing, including `blockMesh`** — a gate a mesher
  grades is FIRED the moment the mesher runs, and that closed the M6 ladder.

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Driven at **zero compute** through the **real readers** on files in the **real
write format**, and the demonstration **refuses** if any construction lands on
the wrong side.

| gate | construction | value | band | verdict side |
|---|---|---|---|---|
| G-F15-1 | ideal capture over **1** cell | 1.167712e−03 | [9.711e−04, 7.769e−03] | **inside** |
| G-F15-1 | ideal capture over **60** cells | 5.826699e−02 | same | **outside** |
| G-F15-2 | impingement at its exact locus | −0.195952245 | [−0.215952, −0.175952] | **inside** |
| G-F15-2 | impingement displaced by 0.35 | +0.154047755 | same | **outside** |

**THE WRITE PATH, NAMED:** OpenFOAM `sets` functionObject, `setFormat raw`,
writing `<case>/postProcessing/{lineY05,lineWall}/<time>/<setName>_p.xy` with
**three coordinate columns (x y z) followed by the field**. That layout is
**measured, not assumed**: 2,690 such files already exist on this box, and
`verification/runs/F6b_runs/coarse/postProcessing/singleGraph_x0/3418/line_k_nut_omega_p_U.xy`
carries 10 columns = 3 coordinates + k + nut + omega + p + 3 U components. This
class — a gate bound to a quantity that can only ever take one value, or to one
never computed at all — has bitten VMFL059, F12's `P4`, F11's `C4`, and F5c's
M4, where the gate was bound exclusively to a Re_θ nothing computes.

**Honest limit, stated rather than glossed:** these four rows are built on
**format-faithful synthetic files**, not on this case's own solver output, and
they cannot be built on it without firing the case. The *format* is pinned
against real solver output; the *values* are constructed. That is the strongest
demonstration available at zero compute and it is labelled as such.

## 8. COST — COSTED BEFORE THE RUN, AS REQUIRED

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** `ClockTime`, **not**
`ExecutionTime` — the latter excludes startup, meshing and sampling, and on F6d
that substitution moved a calibration ratio from 0.998 to 1.0034, across 1.0, in
the flattering direction.

**Rate basis — MEASURED IN THIS LAB, not recalled.** `rhoCentralFoam`, 2-D,
three levels of `verification/runs/ansys_verification/VMFL045/R2`:

| level | cells | steps | ClockTime | µs/cell/step |
|---|---|---|---|---|
| L1 90×76 | 6 840 | 3 127 | 22 s | 1.029 |
| L2 180×152 | 27 360 | 6 305 | 160 s | 0.928 |
| L3 360×304 | 109 440 | 12 661 | 1 418 s | 1.023 |

Consistent across a 16× span in cells. **Rate used: 1.03 µs/cell/step.**

| level | cell-steps | serial s | core-min |
|---|---|---|---|
| coarse | 9.75e7 | 100 | 1.7 |
| medium | 7.80e8 | 803 | 13.4 |
| fine | 6.24e9 | 6 427 | 107.1 |

**Estimate 122.2 core-min; 140.5 with 15 % parallel overhead.**
**REGISTERED CAP: 200 core-minutes** (1.42× headroom).
**Derived dollars at the recorded $0.0513/core-h: $0.171 at the cap, $0.120 at
the estimate — DERIVED, NOT MEASURED**, because the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation.

**The cap is checked INCREMENTALLY after each level.** On a crossing the
launcher **HALTS and REPORTS** at exit 3; unlaunched levels stay `PENDING`. An
overrun **stops the run**; it does not get a new budget. The launcher and the
grader carry the same cap and **refuse to start if they disagree** — a check
that has already caught one real mismatch in this rung's own construction.

**At completion**, per Sanaa's 2026-08-23 directive, actual/predicted lands as a
row in `docs/COST_CALIBRATION.md` with the gap attributed and waste named
separately.

## 9. NEVER RUN — THE EVIDENCE

- **Tracked paths enumerated with `git ls-tree -r HEAD --name-only`: 13,725.**
  Matches for `oblique|shock_ref|shockreflect|shockRef`: **0**.
  *(`git ls-files` was NOT used and its count is 11,067 — the shared index hides
  **2,658 tracked files, 19.4 % of the population**, measured here.)*
  Planted control on the enumeration: a known tracked path is found in it.
- **Out-of-tree run roots**, by name, each with a planted control proving the
  reader sees a known entry: `/home/ubuntu/certonomous-runs` (526 top-level
  entries) **0**; `/home/ubuntu/closure-data` (22) **0**;
  `/home/ubuntu/closure-challenge-benchmark` (7) **0**.
- **F6d Option A's entire run tree lives under `cases/dafoam/`, nowhere near
  `verification/runs/`,** and a lane called it unfired when it had finished
  fifteen days earlier. Folder scope is not evidence of where a campaign ran,
  which is why the roots above were searched by name rather than by territory.
- **What I could not verify:** a content-level grep for `obliqueShock` across the
  three out-of-tree roots **timed out at 100 s and did not complete**. Its empty
  output is **not** evidence and is not offered as any. The name-level
  enumeration above is what this claim rests on.

## 10. WHAT IS **NOT** REGISTERED HERE

- No claim about high-order schemes. This is a second-order finite-volume run.
- No re-grade of any existing row, in any team.
- No amendment to any standard or charter.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).

---

# AMENDMENT 1 — 2026-08-26 — **F15 RUNS SERIAL, 1 RANK, AT ALL THREE LEVELS**

**Version 1.0 → 1.1.** Pre-first-compute amendment under rule 2 §2b.
**lines whose number changed above this section: 0** — verified by diff below,
not asserted.

**CONDITION, AND HOW IT WAS CHECKED.** `test -e` **in the same shell invocation
that wrote this amendment**, naming the directories:
`verification/runs/F15_runs` → **ABSENT**; `verification/runs/F16_runs` → **ABSENT**;
count of `RC.txt`/`log.*` artifacts under `cases/F15_oblique_shock_reflection`
→ **0**. Checked at **2026-08-26T04:33:57Z**. **First compute has not occurred.**

**IT ALTERS NO GATE, NO BAND, NO THRESHOLD, NO CAP AND NO LABEL.** The
**200 core-minute cap stands untouched**, and so does every band descending from
`N_CAPTURE_CELLS = 8`: G-F15-1 remains [9.711165159e−04, 7.768932127e−03] and
G-F15-2 remains −0.195952244729 ± 0.020000000000. **Only the rank column moves.**

## What changes

| level | grid | cells | Δy = Δx | ranks **§4 (struck)** | ranks **AS AMENDED** |
|---|---|---|---|---|---|
| coarse | 200 × 50 | 10 000 | 0.020 | ~~1~~ | **1** |
| medium | 400 × 100 | 40 000 | 0.010 | ~~4~~ | **1** |
| fine | 800 × 200 | 160 000 | 0.005 | ~~8~~ | **1** |

**DECOMPOSITION SEED, AS AMENDED — worded to match F16 word for word:**
**`none`**, identity decomposition. Every level runs **serial on 1 rank** and
**`decomposePar` IS NOT INVOKED AT ANY LEVEL.** There is no partition and no
RNG. §4's `simple`/`(ranks 1 1)` entry is **struck**, not rewritten.

## Why — and the first reason is not cost

**(a) THE DECOMPOSITION CONFOUND, WHICH IS DECISIVE.** A grid-convergence ladder
must differ **only in mesh**. Different rank counts mean different
floating-point summation orders, injecting a **non-mesh difference into exactly
the level-to-level differences the observed-order fit consumes**. F16 runs
serial at every level. **These two rungs exist to be compared** — they are this
lab's first attempt to show the ladder instrument can distinguish p ≈ 1 from
p ≈ 2. If F15's ladder changed decomposition across its levels and F16's did
not, **any difference in fitted order between them would be confounded** and the
comparison would be worth much less.

**(b) SERIAL IS CHEAPER IN THE UNIT THE CAP GOVERNS.** Core-minutes =
wall × ranks ÷ 60. Eight ranks on a contended box run each rank at a fraction of
a core: the wall inflates and the core-minute figure inflates **with the rank
multiplier still applied**. At 1 rank there is no oversubscription penalty and
no communication overhead. **Serial costs more WALL and less CORE-MINUTE, and
the cap governs core-minutes.**

**(c) IT STRENGTHENS THE REPRODUCIBILITY §4 ALREADY ARGUED FOR.** §4 chose
`simple` over `scotch` because `scotch`'s partition is not reproducible from a
recorded field. **One rank is trivially reproducible — there is no partition at
all.** This moves in the direction the frozen document's own reasoning points.

**(d) IT CANNOT BE FITTING.** Nothing has run. **There is no result to fit a rank
count to.** An amendment before first compute, to a field no measurement has yet
touched, is what rule 2 permits.

## The re-projection at 1 rank, reported before re-issue

Measured in the launcher's own unit, from the lab-measured 1.03 µs/cell/step:

| free cores | coarse | medium | fine | cumulative | vs cap 200 |
|---|---|---|---|---|---|
| **≥ 1** (drained) | 1.67 | 13.38 | 107.12 | **122.17** | **FITS**, 1.64× headroom |
| **0.50** (the reading at 2026-08-26, load1 = 16.01 of 16) | 3.33 | 26.77 | 214.23 | **244.33** | **WOULD HALT at the fine level** |

> **STATED PLAINLY BECAUSE IT WAS ASKED FOR: serial still projects OVER the cap
> on a box in this state.** The ladder is **not** quietly trimmed to fit. The
> projected-cap check halts before the fine level's spend and leaves it
> `PENDING`, and the launch waits for the box to drain rather than for the cap
> to move.

For contrast, the 1/4/8 configuration this amendment replaces projects
**1824.27 core-min at the same reading — 9.1× the cap.**

**Not changed by this amendment:** the estimate of record in §8 remains
**122.2 core-min**, because it was always the work-conserving figure and serial
is the configuration that realises it.

## Version-line note, disclosed rather than glossed

The v1.0 document carries **no version line in its header**. Bumping one would
change the line numbers of every section above this point and **falsify the
"lines whose number changed above this section: 0" assertion** this amendment is
required to make. **The version is therefore declared here and only here.**
