# F16 — PRE-REGISTRATION: Stokes' second problem (oscillating wall)

**Team:** cfd. **Written before any compute. ZERO CORE-MINUTES SPENT.**
**Status at freeze: ARMED — never run.**
Frozen by the commit that carries this file. After first compute the gates,
thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them.

---

## 1. WHY THIS CASE

**It supplies BOTH halves of the lab's largest structural gap, in one row** — a
**known answer** joined to a **converging three-level ladder**. Its sibling
`F15_OSR29_PREREGISTRATION.md` supplies both halves too, but on a
**discontinuous** solution whose L1 error can converge no faster than first
order. **This solution is smooth and transcendental, so a second-order scheme
must recover its design order.** The pair brackets the two convergence regimes
on purpose: if F15 returns p ≈ 1 and F16 returns p ≈ 2, the ladder instrument
has been shown to distinguish them, which neither case alone can show.

It is also **deliberately cheap**. Its value is the *joint*, not the physics.
Said plainly here so nobody mistakes the modest cost for a modest claim.

## 2. THE CASE

Semi-infinite viscous fluid over a flat wall oscillating in its own plane.

    u(y, t) = U0 · exp(−k y) · sin(ω t − k y),    k = √(ω / 2ν),   v = w = 0,  p = const

| constant | value |
|---|---|
| Stokes length δ = 1/k | 0.01 m |
| period T | 1.0 s |
| ω = 2π/T | 6.283185307179586 rad/s |
| ν = ω δ²/2 | 3.14159265358979e−04 m²/s |
| U0 | 1.0 m/s |
| domain height H = 14 δ | 0.14 m |
| run length | 40 periods |

Wall: `uniformFixedValue` with a `sine` Function1, u_wall = U0 sin(ωt).
Top (y = H): `fixedValue (0 0 0)`. Four `empty` patches make it a 1-D column.
Solver `icoFoam`, laminar, `ddtSchemes backward` (second order in time).

## 3. THE REFERENCE IS **NOT A PAPER**. IT IS A SUBSTITUTION.

Standing rule 15 requires title-page verification of every **retrieved** paper.
**This case retrieves none.** The exact solution is verified **on this box, at
selftest time, by symbolic substitution into the FULL incompressible
Navier–Stokes equations** — a stronger provenance than a citation, because a
citation can be mis-transcribed and a residual of zero cannot.

Three residuals, all **identically zero**:

| check | residual |
|---|---|
| continuity ∂u/∂x + ∂v/∂y + ∂w/∂z | `0` |
| convection (u·∇)u — so it is exact for the **nonlinear** equations, not just the heat equation | `0` |
| x-momentum ∂u/∂t − ν ∂²u/∂y² | `0` |

**Planted control:** the decay exponent is perturbed to 1.37 k and the momentum
residual is required to become **non-zero**. A substitution checker that returns
zero for a wrong function proves nothing about the right one. Artifact:
`cases/F16_stokes_second_problem/exact_stokes.py --selftest`.

**Two structural conditions, checked rather than hoped:**

- **Domain truncation must not floor the ladder.** The top boundary imposes
  u = 0 where the exact solution is U0·e^{−14} = 8.3e−07. Normalised the way E2
  is, that inconsistency is **1.571e−07** — **783× below** the finest level's
  predicted discretisation error of 1.230e−04. Below 100× the selftest
  **refuses**, because a grid-independent floor makes the triple stagnate for
  reasons that have nothing to do with the scheme.
- **The initial condition is the EXACT SOLUTION at t = 0**, written cell-centre
  by cell-centre by the launcher. Starting from rest would inject a startup
  transient whose slowest mode decays at only ν(π/H)² = 0.158 s⁻¹ — a 6.3 s time
  constant, the **same order** as the discretisation error this case exists to
  measure. 40 periods then leaves any residual transient ~1.9 time constants of
  window inside the Class C test.

## 4. THE LADDER — THREE LEVELS, WHICH IS THE STANDARD

**Uniform spacing at every level**, so the three meshes are **geometrically
similar**. A fixed-expansion-ratio graded ladder is *not* similar, and an
observed order fitted across a change of mesh recipe is one of the two ways an
observed order lies (`VERIFICATION_CHARTER` §3.2). **Δy and Δt both refine by
exactly 2** — checked, and a departure refuses.

| level | cells (1×Ny×1) | Δy | steps/period | Δt | E2 predicted |
|---|---|---|---|---|---|
| coarse | 56 | 2.500e−03 | 400 | 2.500e−03 | 1.968565e−03 |
| medium | 112 | 1.250e−03 | 800 | 1.250e−03 | 4.921412e−04 |
| fine | 224 | 6.250e−04 | 1600 | 6.250e−04 | 1.230353e−04 |

`dim = 1` (refinement in one direction, r = 2 exactly). `grade_ladder` refuses
below three levels.

**Δt must refine with Δy here** — unlike F15, whose graded quantities are
steady-state and therefore free of temporal error. With `backward` differencing
both contributions are O(h²); at the finest level the temporal part is ~100×
below the spatial part, so the spatial derivation below governs.

**DECOMPOSITION SEED (required field): `none`.** Identity decomposition — every
level runs **serial on 1 rank** and **`decomposePar` IS NOT INVOKED at any
level**. There is no partition and no RNG. Recorded explicitly rather than left
to be inferred from its absence.

## 5. THE GATES AND THEIR BANDS

**Both bands descend from ONE declared parameter, `BAND_FACTOR = 3`**, applied
to an **analytic** truncation-error prediction. Declared now, not measured, not
fitted, not revisable after first compute.

**The derivation, so a reader can check it.** Write the solution as
u = Im{U0 e^{−(1+i)ky} e^{iωt}}. Then ∂⁴u/∂y⁴ carries the factor
(−(1+i)k)⁴ = −4k⁴, so a second-order central second difference has local
truncation error

    τ ≈ ν · (Δy²/12) · 4k⁴ · U0 e^{−ky}

A periodic solution error e obeys iωe − νe″ = τ, and on this layer ω = 2νk², so
|e| ≈ |τ|/ω, giving the **pointwise error amplitude**

    |e(y)| ≈ (k²Δy²/6) · U0 · e^{−ky}

**G-F16-1 — normalised L2 velocity-profile error**

    E2 = √( (1/H) ∫₀^H (u_num − u_exact)² dy ) / U0
       ≈ (k²Δy²/6) · √( (1 − e^{−2kH}) / (2kH) )

At Δy_fine = 6.25e−04 that is **1.230353102e−04**.
**Band = [prediction/3, prediction×3] = [4.101177007e−05, 3.691059307e−04].**

**G-F16-2 — u(δ)/U0 at the graded phase ωt = 0 (mod 2π)**

Exact value **−0.309559875653112** = e^{−1}·sin(−1). Linearly interpolated
between bracketing cell centres, because y = δ is a cell **face** at every level
of this ladder and a nearest-cell reading would be biased by half a cell; the
interpolation error is O(Δy²), the same order as the quantity graded, and is
absorbed in the window.

**Band = exact ± 3 × the same amplitude at y = δ = ±7.185145335e−04
= [−0.310278390187, −0.308841361120].**

**Why a factor-3 window and not an equality:** the derivation is **asymptotic**
and drops both the error's phase and the temporal contribution. An equality
would be a *wrong* band, not a strict one. Three is stated in advance and is
the only free number in this document.

**Neither band comes from a measured deviation. At freeze no run of this case
exists anywhere on this box.**

## 6. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING, and nothing else.
- **Rule 5 is reached through `grade_ladder` ONLY.** `grade_f16.py` carries
  **exactly one** `grade_ladder` call node (line 648), censused by **AST** at
  every entry — a regex counts prose. The text matcher is separately driven
  **both ways** on synthetic files (a miss on a file with no call, a hit on a
  planted call).
- **CONVERGENCE GATE: CLASS C**, all four elements
  (`CFD_CONVERGENCE_GATE_RULING_2026-08-25.md` §2), on a **phase-locked** series:
  one sample per whole period, so every sample sits at ωt = 0 (mod 2π) and the
  series measures **period-to-period change** rather than the oscillation.
  Sustained window **12 periods** — **justified, not inherited**: the slowest
  transient this domain supports decays at ν(π/H)² = 0.158 s⁻¹, a 6.3 s time
  constant, so 12 s is ~1.9 time constants and a surviving transient cannot hide
  inside it. Trend fit at 2.0e−4 relative drift; two-half stationarity on mean
  and variance ratio, **shown able to report NOT stationary**. **Element 4:
  fewer than 20 samples EXITS 2** — it does not return a state. All four limbs
  driven by a planted control.
- **Rule 5 limb (1):** `icoFoam` **does** perform linear solves, so the
  iterative state is a **census over EVERY time step's final pressure residual**
  against the solver's own `tolerance 1e-09`, reporting the count that failed.
  **This is not a Class A gate:** Class A's defect is a *two-point sample at the
  end*, and a census over all N steps is not that. A separate control refuses if
  `P_SOLVER_TOL` in the grader disagrees with `system/fvSolution` on disk — a
  census graded against a threshold nobody enforced is worse than none.
- **Completion (standing rule 4):** rc = 0; an `End` line; **`latest + dt >
  endTime`** — never `latest >= endTime`, never a two-sided tolerance; `U` and
  `p` present at `endTime`; each **newer than the case's own `0/U`** (age guard).
  Δt is **fixed** here, so the `Time`-count identity `n_times == endTime/Δt`
  **does** apply and is checked as an extra limb.
- **Planted-zero controls (rule 3)**, into the **real artifact**, read back with
  the **real parser**, refusing with exit 2. A known Ux-column offset moves every
  pointwise error by exactly that offset, so E2's post-plant value is *predicted*
  from the pre-plant array and must be reproduced to 1e−14; and the interpolated
  u(δ) must move by **exactly** the offset (1e−12).
- **`assert` census: ZERO**, by AST parse, across `grade_f16.py` and
  `exact_stokes.py` (L-332). **Hard `-O` refusal at entry, `sys.exit(2)` before
  anything else runs**, driven and confirmed: `python3 -O grade_f16.py
  --selftest` → **rc 2**. `grade_ladder` reaches its gate through four `assert`s
  in the shared `roache_triple.py` (`:195, :632, :634, :637`); **that file is
  referred to verification and is not cfd's to edit**, so the refusal sits at
  the boundary F16 owns.
- **Success messages print INSIDE the passing branch.**
- **Guards.** The launcher **REFUSES** a pre-existing `0/` or numeric time
  directory; it does not delete. **No `rm -rf` and no `shutil.rmtree` on any
  case directory anywhere in this rung** — the grader's `rmtree` calls act only
  on `tempfile.mkdtemp` scratch trees.
- **`--preflight` fires nothing, including `blockMesh`.**

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Driven at **zero compute** through the **real readers**, on files in the **real
write format**, and the demonstration **refuses** if a construction lands on the
wrong side.

| gate | construction | value | band | verdict side |
|---|---|---|---|---|
| G-F16-1 | exact + **1×** the predicted truncation amplitude profile | 1.193460e−04 | [4.101e−05, 3.691e−04] | **inside** |
| G-F16-1 | exact + **40×** the same | 4.773100e−03 | same | **outside** |
| G-F16-2 | exact + **1×** the same | −0.309126097 | [−0.310278, −0.308841] | **inside** |
| G-F16-2 | exact + **40×** the same | −0.299780847 | same | **outside** |

**THE WRITE PATH, NAMED:** OpenFOAM `sets` functionObject, `setFormat raw`,
writing `<case>/postProcessing/profile/<time>/profile_U.xy` with **three
coordinate columns (x y z) followed by the three velocity components — six
columns**. That layout is **measured, not assumed**, against real solver output
already on this box:
`verification/runs/F6b_runs/coarse/postProcessing/singleGraph_x0/3418/line_k_nut_omega_p_U.xy`
carries 10 columns = 3 coordinates + four scalars + 3 U components. The class of
defect this guards against — a gate bound to a quantity that can only take one
value, or to one never computed — has bitten VMFL059, F12's `P4`, F11's `C4`,
and F5c's M4.

**Honest limit:** these four rows are built on **format-faithful synthetic
files**, not on this case's own solver output, which cannot exist without firing
the case. The *format* is pinned against real output; the *values* are
constructed. Labelled as such rather than glossed.

## 8. COST — COSTED BEFORE THE RUN, AS REQUIRED

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** `ClockTime`, **not**
`ExecutionTime`.

Total time steps across the three levels: **112,000** (16k + 32k + 64k), on
meshes of 56 / 112 / 224 cells, all serial. The work is **per-step overhead
dominated**, not cell dominated, at these sizes:

| assumed ms/step | core-min |
|---|---|
| 0.3 | 0.56 |
| 0.6 | 1.12 |
| 1.0 | 1.87 |

**REGISTERED CAP: 20 core-minutes.**
**Derived dollars at the recorded $0.0513/core-h: $0.017 at the cap — DERIVED,
NOT MEASURED**, because the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation.

**`cost_basis`, stated honestly: ESTIMATE WITH NO MEASURED HISTORY.** Unlike
F15 — whose rate is pinned to this lab's own measured 1.03 µs/cell/step from
`verification/runs/ansys_verification/VMFL045/R2` — there is **no `icoFoam` log
of this shape on this box** to calibrate against. The cap therefore carries a
deliberately wide ~11× headroom over the central estimate, and **that width is
the admission, not a claim of precision.**

**The cap is checked INCREMENTALLY after each level**; on a crossing the
launcher **HALTS and REPORTS** at exit 3 and unlaunched levels stay `PENDING`.
An overrun **stops the run**; it does not get a new budget. Launcher and grader
carry the same cap and refuse to start if they disagree — which already caught
one real mismatch during this rung's construction.

**At completion**, per Sanaa's 2026-08-23 directive, actual/predicted lands as a
row in `docs/COST_CALIBRATION.md` with the gap attributed and waste named
separately. **This rung is the more valuable calibration row of the two**,
precisely because its estimate has no history behind it.

## 9. NEVER RUN — THE EVIDENCE

- **Tracked paths enumerated with `git ls-tree -r HEAD --name-only`: 13,725.**
  Matches for `stokes|Stokes|oscillating`: **0**.
  *(`git ls-files` was NOT used; its count is 11,067 — the shared index hides
  **2,658 tracked files, 19.4 %**, measured here.)* Planted control on the
  enumeration: a known tracked path is found in it.
- **Out-of-tree run roots**, by name, each with a planted control proving the
  reader sees a known entry: `/home/ubuntu/certonomous-runs` (526 top-level
  entries) **0**; `/home/ubuntu/closure-data` (22) **0**;
  `/home/ubuntu/closure-challenge-benchmark` (7) **0**.
- **Adjacency disclosed rather than hidden.**
  `research/agenda/proposals/taylor-green-re1600-first-rung.json` exists at
  status `proposed`, never fired. It is a **different case**: 3-D Taylor–Green
  at Re = 1600 graded against a **fetched workshop table** (and it BLOCKS if the
  table cannot be fetched). This rung is 1-D, has a **closed-form exact
  solution**, fetches nothing, and cannot block on a reference. Saying so is
  cheaper than a supervisor discovering the adjacency alone.
- **What I could not verify:** a content-level grep for `stokes second` /
  `oscillating wall` across the three out-of-tree roots **timed out at 100 s and
  did not complete**. Its empty output is **not** evidence and is not offered as
  any. The name-level enumeration above is what this claim rests on.

## 10. WHAT IS **NOT** REGISTERED HERE

- No turbulence claim. This is a laminar, exactly-soluble flow.
- No re-grade of any existing row, in any team.
- No amendment to any standard or charter.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).

---

## AMENDMENT 2 — 2026-08-26 (pre-first-compute)

**Version 1.0 → 1.1.** Pre-first-compute amendment under rule 2 §2b, permitted
under Sanaa's boarded permission at bc0e687e ("anything that leads to the lab
having more runs under its belts"). Lesson L-339.
**lines whose number changed above this section: 0** — verified by `git diff`
against the HEAD blob: this file's diff is append-only (this block, added at the
foot; 0 deletions).

**CONDITION, AND HOW IT WAS CHECKED.** `test -e` in the shell invocation that
prepared this amendment, 2026-08-26, naming the directories:
- `verification/runs/F16_runs/coarse/0` — absent
- `verification/runs/F16_runs/medium/0` — absent
- `verification/runs/F16_runs/fine/0` — absent
No solver has produced a time directory for this rung. **F16 attempt 1 evidence:**
`verification/runs/F16_runs/STATUS.F16` read `rc=1 end=2026-08-26T15:56:10Z`
and `launcher.out` ended `/usr/lib/openfoam/openfoam2606/etc/bashrc: line 184:
WM_PROJECT_DIR: unbound variable` — the launcher died at zero compute inside the
OpenFOAM source, before `blockMesh` or any solver ran (both files renamed to
`launcher.attempt1.out` / `STATUS.F16.attempt1`, untracked, never deleted).

**WHAT CHANGED — `cases/F16_stokes_second_problem/run_f16.sh` only.** `set -u` (in force from the top of the file)
is lifted across the OpenFOAM source and restored immediately after, the form
used at `scripts/launch_k0f.sh:158-169`:
```
-. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
+set +u; . "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }; set -u
```
plus a four-line dated comment above it. Launcher diff: **+5 / −1 lines**; the
original line 148 becomes line 152. **No band, cap, threshold, verdict or
label line was touched**, in the launcher or in this document.

**CHECKED AFTER THE EDIT.** `bash cases/F16_stokes_second_problem/run_f16.sh --preflight` rc 0. Replicating the
sequence `set -u; set +u; . $FOAM_BASHRC; set -u; which icoFoam blockMesh` resolves
real binaries under `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/`.
`scripts/check_launcher_can_launch.py` rc 0 on the edited file — **and rc 0 on
the frozen file that could not launch**, which is a finding against the checker,
not a clearance of the file (L-339); the checker is not edited here.

**THE `--prereg-commit` TO PASS AT LAUNCH IS THE SHA OF THIS COMMIT** — the
commit that lands this block (`git log -1 --format=%H -- verification/campaign/F16_SL2_PREREGISTRATION.md`); the graders
record it verbatim.
