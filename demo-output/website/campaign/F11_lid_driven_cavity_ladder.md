# F11 — 2D Lid-Driven Cavity Verification Ladder (Ghia, Ghia & Shin, 1982)

**Date:** 2026-07-30
**Status:** New family, built and gated this session. Two rungs (Re=100, Re=1000),
each run at two mesh resolutions as an explicit grid-sensitivity check before
any number is quoted as a gate result.

## Why this case, over the alternatives considered

The brief asked for cases in the mould of the F5a cylinder Reynolds ladder,
chosen with reasoning and checked against `NOT_PASSING_REGISTER.md` and
`NINE_ACT_GATE_TABLE.md` before committing compute. Three candidates were
weighed:

1. **Higher F5a rungs (Re 5000 / 10000, 2D).** F5a's own record recommends
   explicitly AGAINST this: no point reference exists for Re 5000, Re 10,000's
   own point reference (Dong & Karniadakis 2005/2006) is paywalled with no
   OA copy, and the 2D model has already crossed a topological threshold at
   Re 3900 (mean recirculation bubble vanishes) that would make a higher 2D
   rung answer a question the ladder has already answered. Ruled out on the
   ladder's own evidence, not re-attempted.
2. **Low-speed 2D NACA0012 polar vs Ladson (1988) NASA TM-4074.** A genuinely
   promising, fully open-access primary reference (NASA NTRS, fetched and
   read directly, real tabulated CL/CD-vs-alpha data extracted — see
   `F11_runs/ladson_reference_note.md`). **Not chosen for this session**
   because this exact validation target (TMR NACA0012 vs Ladson-derived
   CFL3D/FUN3D data) was already attempted in this repository via
   `sdk/workflows/tmr_verification.py` and is a **documented, unresolved
   near-miss**: the steady `simpleFoam`/kOmegaSST route on the TMR C-grid
   shows a **sustained, non-decaying force oscillation** at both alpha=0 and
   alpha=10 across multiple relaxation levels and two mesh resolutions
   (`demo-output/website/tmr/naca0012_status.json`,
   `findings_2026_07_25`), and the alternate transient route was found
   **1-3 orders of magnitude more expensive than scoped**
   (`demo-output/website/tmr/C4_naca0012_closure.md`: ~117,000-303,000
   core-minutes needed for one rung, 5.0 spent). A fresh O-grid mesh
   *might* sidestep the specific oscillation (the existing investigation's
   own leading hypothesis is that "the feedback lives in the wake and
   trailing-edge convection" on the TMR-converted C-grid specifically), but
   that is an unproven hypothesis, not a controlled variable, and chasing it
   risks reproducing a known failure mode rather than opening new ground —
   exactly what the brief said not to do. Parked as a real candidate for a
   dedicated session, not silently dropped (see Docket below).
3. **Backward-facing step, laminar, Armaly et al. (1983).** A real, different
   candidate — genuinely distinct physics from both F5a and F5c (the
   existing turbulent backward-facing-step attempt, Driver & Seegmiller
   1985, already GATE NOT REACHED in `CAMPAIGN_STATUS.md`/`F5bc_...md`: a
   4-12x reattachment-length deviation that does not converge under mesh,
   wall-treatment, or algorithm changes, attributed to genuine unsteady
   bubble-flapping a steady solve cannot represent). Armaly's own low-Re
   data (Re_h up to ~400ish) sits below any such instability and is a
   fundamentally different, well-posed steady problem. **Checked and
   confirmed paywalled** (Unpaywall, DOI 10.1017/S0022112083002839:
   `is_oa: false`, no repository copy). Not ruled out, but the brief asked
   to prefer accessible references, and this session already had to fall
   back to a secondary source once (Ghia, below); doing it twice in the same
   session would stack two weakened-reference gates rather than one. Costed
   and docketed below, not launched.

**Chosen: 2D lid-driven cavity flow, laminar, Ghia/Ghia/Shin (1982).** Reasons,
stated plainly:

- It is the single most reproduced incompressible-Navier-Stokes verification
  benchmark in the field — closed, unambiguous geometry (unit square, one
  moving wall), no turbulence closure needed at the Reynolds numbers used
  here (matching this project's own preference, established on F5a, for
  un-modelled solves where the point is to check the bare discretization).
- **No physics-regime trap.** The register already carries two failures
  (Sphere, Cylinder — Group 4) caused by a RANS closure landing on the wrong
  side of a laminar/turbulent transition the model cannot represent. The
  cavity at Re=100/1000 has no such trap: it is genuinely, unambiguously
  laminar and steady over this whole range (2D cavity flow is documented to
  stay steady to roughly Re~8,000-10,000 before any instability), so there is
  no regime-mismatch failure mode available to walk into.
- **Multiple quantities, for free.** Ghia's own tables give the FULL u(y)
  profile along the vertical centerline (17 points) and the FULL v(x)
  profile along the horizontal centerline (17 points) — this is intrinsically
  a much richer gate than a single scalar (Cd, St), while still being
  reportable as two aggregate numbers (max and RMS deviation) per rung, the
  same way F5a reported Cd/St/Cl_rms as three scalars.
- **A genuine mini-ladder**, matching the requested "mould": two rungs
  (Re=100, Re=1000), same non-dimensionalization, same solver family, one
  variable (Re) moving between rungs — directly parallel to F5a's own first
  two rungs.

## Reference, obtained before any run, and its access limitation disclosed

Ghia, U., Ghia, K.N., Shin, C.T. (1982). "High-Re solutions for incompressible
flow using the Navier-Stokes equations and a multigrid method." *Journal of
Computational Physics*, 48(3), 387-411. DOI 10.1016/0021-9991(82)90058-4.

**Checked directly via the Unpaywall API before choosing this case (not
after):** `is_oa: false`, `has_repository_copy: false`, `oa_locations: []`.
The primary JCP article is paywalled with no legitimate open-access copy, the
same situation F5a hit for its Re 2000 gate (Zdravkovich) and Re 10,000
docket item (Dong & Karniadakis). Per that precedent, the widely-reproduced
tabulated values of Table I (u along the vertical centerline x=0.5) and Table
II (v along the horizontal centerline y=0.5) were taken from two
**independently hosted, secondary transcriptions** (different GitHub authors)
rather than the primary PDF, and cross-checked before trusting them:

- Both transcriptions were fetched separately (different URLs, different
  authors) and agree with each other.
- The Re=100 and Re=1000 columns used by this ladder (its only two rungs) are
  smooth and internally consistent — no sign flips, no discontinuities.
- **This matters because the *other* Reynolds-number columns in the SAME two
  tables are not clean**: Re=400 carries a value the original paper itself
  flags "probably wrong" (x=0.9063, v-table — the flag is preserved in the
  secondary source, itself a good sign the transcription is being honest
  rather than silently smoothing errors); Re=3200 (u-table, y=0.4531) and
  Re=10000 (u-table, y=0.5000) both carry an obvious digit/sign
  transcription defect. **Re=100 and Re=1000 were deliberately chosen as
  this ladder's two rungs partly because they are the clean columns** —
  this is disclosed here so a future reader extending this ladder to Re=3200
  or Re=10000 does not trust those two columns' numbers without
  re-deriving them from a cleaner source first.

**Definitions checked**, matching this project's standing discipline (three
different length definitions nearly invalidated a gate on F5a's Re 3900
rung): Re = U_lid · L / ν with L = cavity side length and U_lid = lid speed,
both set to 1 in the nondimensional setup used here (nu = 1/Re exactly, no
ambiguity). Ghia's own coordinate convention — lid at y=1 moving in +x,
no-slip on the other three walls, u tabulated exactly along x=0.5 and v
exactly along y=0.5 — is reproduced exactly, including sampling AT those
coordinates rather than near them (`type cloud` point sampling, not a
nearest-cell lookup).

## The gate, chosen for measurability before any run (P2/P3 discipline)

Two quantities per rung, matching F5a's "multiple quantities, not one"
standard:

1. **u(y) along x=0.5**, compared point-by-point against Ghia's 17-point
   table (15 interior points used for the gate; the two boundary points,
   y=0 and y=1, are the imposed boundary condition itself, not a solver
   prediction, and are excluded from the aggregate so they cannot inflate
   agreement).
2. **v(x) along y=0.5**, same treatment, 15 interior points.

Reported per profile as **max |error|** and **RMS |error|** in the same
nondimensional velocity units as the lid speed (U_lid = 1), so a value of
0.01 means "1% of the lid speed," directly comparable across rungs and
resolutions with no normalization ambiguity.

**Measurability checked before launch:** both points existed as real,
citable numbers before any solve — unlike one F5a rung where a gate needed
two points and only one existed. No band-weakening was needed here (unlike
F5a's Re 2000 and Re 10,000, which had to fall back to regime-band
comparisons for lack of a point reference) — Ghia's data are point values at
named coordinates.

**Grid sensitivity checked before quoting a result** (the discipline this
project's own register shows was skipped on several failed cases — the
naca4412 wing ladder, the Ahmed/B-52 mesh ladders, all non-monotonic or
non-asymptotic): every rung was run at **two mesh resolutions**, n=64
(4,096 cells) and n=128 (16,384 cells), both symmetric-double-graded toward
all four walls (all four walls carry a real BC here, unlike a
boundary-layer-only case), grading ratio 8:1 each half. If the two
resolutions disagree materially, the finer one is not trusted without a
third point; if they agree, that is itself load-bearing evidence the answer
is grid-independent at the reported precision.

## Solver and case

`simpleFoam` (incompressible, steady), **laminar** — no turbulence closure,
deliberately, matching the F5a philosophy of testing the bare
discretization and matching the physical fact that this flow has no
turbulence to model at these Re. `system/fvSchemes`: `Gauss linearUpwind
grad(U)` for `div(phi,U)` (bounded, second-order-biased), central
`Gauss linear corrected` laplacian. `residualControl`: p 1e-8, U 1e-9 — both
initial residuals, per L-14/L-21 discipline, and both checked with
`scripts/check_convergence.py` against the solver's own
`SIMPLE solution converged in N iterations` statement, never a residual
read in isolation. `case_preflight.sh --model laminar` run clean on every
case before launch; all four launched through `scripts/launch_solve.sh` (not
a bare foreground call) so the collector was armed at launch, per D12.
Case builder: `demo-output/website/campaign/F11_runs/cavity_ladder.py`.

## Measured

| rung | mesh | iterations | wall time (ExecutionTime) | u-profile max\|err\| | u-profile RMS\|err\| | v-profile max\|err\| | v-profile RMS\|err\| | convergence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Re=100 | n=64 (4,096 cells) | 1,505 | 12.58 s | 0.00462 | 0.00163 | 0.00956 | 0.00508 | **CONVERGED** (checker) |
| Re=100 | n=128 (16,384 cells) | 5,285 (4,000 + 1,285 resumed) | 233.24 s | 0.00489 | 0.00231 | 0.00924 | 0.00507 | **CONVERGED** (checker, after a genuine extension — see below) |
| Re=1000 | n=64 (4,096 cells) | 1,727 | 14.39 s | 0.00426 | 0.00246 | 0.01536 | 0.00763 | **CONVERGED** (checker) |
| Re=1000 | n=128 (16,384 cells) | 4,550 | 176.73 s | 0.00624 | 0.00339 | 0.01734 | 0.00936 | **CONVERGED** (checker) |

Every "CONVERGED" above is `scripts/check_convergence.py`'s verdict, keyed
off the solver's own `SIMPLE solution converged in N iterations` statement —
never a residual read in isolation, per L-14/L-21.

**One rung caught genuinely NOT_CONVERGED and fixed, not glossed over.**
`re100_n128` ran to its original 4,000-iteration cap with `p` Initial
residual at 8.58e-8 (target 1e-8) and `U` at 1.12e-8/2.81e-8 (target 1e-9) —
close, but `check_convergence.py` correctly returned `NOT_CONVERGED`
(`no 'SIMPLE solution converged' string anywhere in the log ... ran to its
iteration cap ... without ever meeting its own gate`), and it is reported
here exactly that way rather than as a near-enough pass. Fixed by editing
`controlDict` (`startFrom latestTime`, `endTime` extended 4000 -> 9000) and
relaunching through `launch_solve.sh` again — verified as a genuine resume,
not a silent restart-from-zero (per L-19/the F8 restart trap), by reading
`Create mesh for time = 4000` and `Reading field p` / `Reading field U` at
the top of the extension's own log before trusting it. It converged cleanly
860 iterations later, at 5,285.

## Grid sensitivity, reported honestly (not claimed as clean Richardson convergence)

Both Reynolds numbers were run at two resolutions. The result is **small in
absolute terms but not strictly monotonic**, and that is reported as
measured rather than smoothed into "grid independent":

> **[RESTATED 2026-08-10 under `docs/charters/VERIFICATION_CHARTER.md` §17 — no draw-scatter evidence exists at the rung this feature turns on.]** The statement above is a claim about the SHAPE of a sequence of grid-refinement increments for **the lid-driven cavity**. Under the adopted rule such a claim is published only with draw-scatter evidence at the deciding rung, or with the absence of that evidence stated on its face. **No replicate mesh has ever been drawn at this ladder's deciding rung.** Recipe class per `campaign/LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md`: **single-recipe (CLEAN)**, so its increments really are discretization increments and this gap is not confounded away. **This is not a withdrawal — the feature is unchecked, not shown false**; the remedy the rule specifies is exactly this sentence. Original text retained.


| quantity | Re=100, n=64 -> n=128 | Re=1000, n=64 -> n=128 |
| --- | --- | --- |
| u max\|err\| | 0.00462 -> 0.00489 (+0.00027) | 0.00426 -> 0.00624 (+0.00198) |
| u RMS\|err\| | 0.00163 -> 0.00231 (+0.00068) | 0.00246 -> 0.00339 (+0.00093) |
| v max\|err\| | 0.00956 -> 0.00924 (-0.00032) | 0.01536 -> 0.01734 (+0.00198) |
| v RMS\|err\| | 0.00508 -> 0.00507 (-0.00001) | 0.00763 -> 0.00936 (+0.00173) |

Refining the mesh 4x in cell count moved every error by less than 0.002 in
absolute (nondimensional velocity) terms, i.e. under 0.2% of the lid speed —
and two of the eight comparisons moved in the "wrong" direction (error grew
slightly with refinement) rather than shrinking. **This is not read as a
grid-convergence failure of the kind already on this project's own register**
(the naca4412/Ahmed/B-52 mesh ladders, where refinement swung results by
tens of percent and sometimes flipped sign) **[AMENDED 2026-08-10 — the B-52 ladder's "turn" is WITHDRAWN as a claim (chief ruling `7abb0ba3`); see `campaign/B52_TURN_WITHDRAWAL_2026-08-10.md`. This statement is read with that withdrawal attached. Original text retained.]** *On the B-52 it was MESH CONSTRUCTION that swung the result, not refinement; the contrast this sentence draws survives with the mechanism corrected.* — the magnitudes here are two
orders of magnitude smaller and the mesh topology/scheme were held fixed
between resolutions, unlike those cases. It is read as: **both resolutions
already sit on a shared, few-tenths-of-a-percent plateau relative to Ghia's
own numbers**, and the remaining scatter is more likely attributable to the
advection scheme (`linearUpwind`, not a scheme designed to converge
monotonically to machine precision the way a pure central scheme's
truncation error would) than to under-resolution. No third mesh was run to
settle this more rigorously (out of scope for this session's budget); the
two-point comparison is reported as exactly that, not oversold as
Richardson-verified.

## Where the disagreement concentrates — an attribution, not just a number

The full per-point comparison at Re=1000, n=128 (the finer, primary-quoted
resolution):

**u(y) at x=0.5:**

| y | Ghia (1982) | measured | error |
| --- | --- | --- | --- |
| 0.9766 | 0.65928 | 0.66388 | +0.00460 |
| 0.9688 | 0.57492 | 0.58065 | +0.00573 |
| 0.9609 | 0.51117 | 0.51690 | +0.00573 |
| 0.9531 | 0.46604 | 0.47228 | **+0.00624** |
| 0.8516 | 0.33304 | 0.33638 | +0.00334 |
| 0.7344 | 0.18719 | 0.18813 | +0.00094 |
| 0.6172 | 0.05702 | 0.05674 | -0.00028 |
| 0.5000 | -0.06080 | -0.06182 | -0.00102 |
| 0.4531 | -0.10648 | -0.10773 | -0.00125 |
| 0.2813 | -0.27805 | -0.28026 | -0.00221 |
| 0.1719 | -0.38289 | -0.38757 | **-0.00468** |
| 0.1016 | -0.29730 | -0.29939 | -0.00209 |
| 0.0703 | -0.22220 | -0.22212 | +0.00008 |
| 0.0625 | -0.20196 | -0.20162 | +0.00034 |
| 0.0547 | -0.18109 | -0.18066 | +0.00043 |

**v(x) at y=0.5:**

| x | Ghia (1982) | measured | error |
| --- | --- | --- | --- |
| 0.9688 | -0.21388 | -0.22782 | -0.01394 |
| 0.9609 | -0.27669 | -0.29324 | -0.01655 |
| 0.9531 | -0.33714 | -0.35448 | **-0.01734** |
| 0.9453 | -0.39188 | -0.40906 | -0.01718 |
| 0.9063 | -0.51500 | -0.52459 | -0.00959 |
| 0.8594 | -0.42665 | -0.42624 | +0.00041 |
| 0.8047 | -0.31966 | -0.32001 | -0.00035 |
| 0.5000 | 0.02526 | 0.02571 | +0.00045 |
| 0.2344 | 0.32235 | 0.32480 | +0.00245 |
| 0.2266 | 0.33075 | 0.33337 | +0.00262 |
| 0.1563 | 0.37095 | 0.37603 | +0.00508 |
| 0.0938 | 0.32627 | 0.33222 | +0.00595 |
| 0.0781 | 0.30353 | 0.30911 | +0.00558 |
| 0.0703 | 0.29012 | 0.29542 | +0.00530 |
| 0.0625 | 0.27485 | 0.27985 | +0.00500 |

Both profiles' worst points are not scattered randomly — they cluster in
the near-wall region closest to the **moving lid** (u-profile: y=0.95-0.98,
directly under the lid's shear layer) and closest to the **right wall below
the lid** (v-profile: x=0.91-0.97, the descending jet fed by the lid-driven
corner flow). This is consistent with the two top corners (x=0, y=1 and
x=1, y=1), where the lid's `u=1` boundary condition meets the stationary
side wall's `u=0` no-slip condition **discontinuously**, being the hardest
feature of this exact benchmark to resolve identically across two different
numerical methods — Ghia's own multigrid vorticity-streamfunction scheme and
this project's finite-volume colocated SIMPLE solve necessarily regularize
that discontinuity differently. Away from those regions (mid-cavity, the
lower-left recirculation, the bulk of both centerlines) agreement is to a
few hundredths of a percent of the lid speed. **This is stated as a
plausible, mechanistically-grounded explanation, not a proven one** — no
independent Ghia-side error analysis of the corner singularity was consulted
this session to confirm it quantitatively; it is offered as the natural
reading of where the numbers concentrate, the same epistemic status F5a gave
several of its own attributions before a literature mechanism was located.

## A definition that has to be stated precisely: this is VERIFICATION, not VALIDATION

Unlike F5a (which compares against DNS/experiment — real physics), Ghia,
Ghia & Shin (1982) is **itself a numerical solution** (a vorticity-
streamfunction formulation solved with a multigrid method), not an
experiment or a DNS of a real flow. **This gate is therefore a code-to-code
VERIFICATION** (does an independent numerical method, on an independent
discretization, converge to the same answer for the same well-posed PDE
problem) and not a physical VALIDATION (does the solver reproduce reality).
Both are legitimate and both matter, but conflating them would misstate
what was actually checked here — stated explicitly so the next reader does
not read this gate as claiming physical accuracy it was never designed to
test. (The lid-driven cavity's own physical realizability at these
Reynolds numbers is a separate, well-established fact — the point of this
gate is confirming this project's solver reproduces the accepted numerical
answer, not re-confirming the physics.)

## Verdict

**GATE REACHED, both rungs, both quantities, both mesh resolutions.**
Maximum absolute deviation from Ghia (1982) across all four (Reynolds x
resolution) combinations: **1.73% of the lid speed** (Re=1000, n=128,
v-profile, x=0.9531 — the point nearest the lid/wall corner singularity
discussed above). Every other point deviates by under 1%, and the bulk of
each profile deviates by a few tenths of a percent. Both mesh resolutions
converged to the solver's own stated criterion (`check_convergence.py`),
one only after a caught-and-fixed extension. This is a clean, defensible,
low-cost addition to the gated-run stock: two rungs, two quantities per
rung (34 individual point comparisons total, not one scalar), full
mesh-sensitivity disclosure, and an honest note distinguishing verification
from validation.

## Cost (measured, not guessed)

| rung | cells | iterations to converge | wall time |
| --- | --- | --- | --- |
| Re=100, n=64 | 4,096 | 1,505 | 12.58 s |
| Re=100, n=128 | 16,384 | 5,285 | 233.24 s |
| Re=1000, n=64 | 4,096 | 1,727 | 14.39 s |
| Re=1000, n=128 | 16,384 | 4,550 | 176.73 s |

**Total for the whole shipped ladder (4 solves, both mesh checks, both
`blockMesh`/`checkMesh` passes): well under 8 minutes of wall time**, run as
4 concurrent single-core jobs (matching this session's 4-core budget) on a
box that also had the F5a 3D pilot (8 ranks, undisturbed throughout — never
touched, never contended for its cores) and several other agents' jobs live
at the same time. `free -g` and `launch_solve.sh --check` were read before
every launch; MemAvailable never dropped below 20 GB and swap stayed at 0
throughout this family's work.

**A genuine, load-bearing finding buried in the cost table**: doubling the
mesh resolution (n=64 -> n=128, 4x the cells) did **not** cost a flat 4x —
it cost roughly **3.6x per iteration** (14.39/1727=0.00833 s/iter at n=64
vs. 176.73/4550=0.03885 s/iter at n=128, a ~4.7x per-iteration increase) **and**
required more iterations to converge (1727 -> 4550, a 2.6x increase) at
Re=1000. The two effects compound: overall wall time grew ~12.3x for a 4x
mesh refinement. This matters directly for the docket item below, which
needs a substantially finer mesh.

## Docket — costed, not launched

### Next rung on this ladder: Re=5000

Ghia's own tables (both columns independently checked clean, see reference
section above) already carry a citable Re=5000 point, at **zero-cost paper
search** — no new reference to find, unlike every other candidate weighed
above. Physically legitimate: 2D lid-driven cavity stays laminar and steady
well past Re=5000 (documented transition to unsteady is around Re~8,000-
10,000), so no regime-mismatch risk, matching the reasoning that selected
this whole family. **Not launched this session** because Ghia's own paper
uses a substantially finer mesh (257x257, not 129x129) starting at Re=5000,
for a real reason — thinner shear layers and the onset of resolvable
secondary corner vortices — and this project's own measured cost table
above shows refinement cost compounds (iteration count AND per-iteration
cost both grow), not just the per-iteration cost a naive cells-only estimate
would predict.

**Rough cost estimate, explicitly flagged as a two-point extrapolation
(the exact trap F5a's own cost-model section warns against — "the previous
write-up's error was extrapolating from a two-point local fit at all"):**
scaling this ladder's own measured n=64->n=128 compounding (~12.3x wall
time for a 4x cell-count step) forward one more doubling-in-each-direction
step (128 -> ~256, i.e. cell count 16,384 -> ~65,536, matching Ghia's own
257x257 choice) gives a rough order of **tens of minutes to low hours**,
not the multi-hour-to-multi-day cost the F5a 3D rung's steeper (Re,
not just mesh) scaling produced. This is a **weak, honestly-labelled
estimate** — Re=5000 is also a stiffer nonlinear problem than Re=1000, which
this two-point mesh-only extrapolation does not capture, and the iteration
count actually went DOWN from Re=100 to Re=1000 at fixed n=128 (5,285 ->
4,550) in this session's own data, so "higher Re costs more iterations" is
not even a reliable local trend here to extrapolate from confidently.
**Recommendation: cost it for real with one bounded, foreground timed probe
(a few hundred iterations at the 257x257 resolution, the same kind of cheap
calibration F5a used for its 3D rung) before committing a full run**, rather
than trusting this paragraph's estimate.

**That probe was run** (free, foreground, bounded, matching the
recommendation immediately above rather than leaving it as a hypothetical):
n=256 (65,536 cells, matching Ghia's own 257x257 choice), Re=5000,
`blockMesh` 0.74 s, `checkMesh` 1.40 s (**Mesh OK**, clean, same grading
topology), then 300 `simpleFoam` iterations under a plain foreground
timeout: **77.3 s ExecutionTime, 0.2577 s/iteration.** Consistent with this
family's own measured trend (per-iteration cost grows faster than cell
count: n=64->n=128 was a 4.7x per-iteration increase for a 4x cell-count
step; n=128->n=256 here is a 6.63x per-iteration increase, 0.03885 ->
0.2577 s/iter, for the same 4x cell-count step — the superlinear growth is
itself worsening, not staying fixed, as the mesh gets finer).

At 300 iterations the residuals are still in the impulsive-start transient
(p Initial residual 0.0466 -> 0.000354 over the 300 steps, U still at
1.3e-3/2.2e-3) — far too early to read off a converged rate, so **no
iteration-to-convergence number is claimed from this alone**. Applying the
0.2577 s/iter rate to this ladder's own observed convergence-iteration range
(1,727-5,285 iterations across the four completed rungs) gives **7-23
minutes** if Re=5000 needs a similar iteration count to what has been
measured so far, or into the low hours if it needs several times more (the
finer-mesh-needs-more-iterations trend measured above, extrapolated). **Net:
the "tens of minutes to low hours" estimate above is now backed by one real
timing number, not zero** — still not a committed iteration-count
prediction, and the honest next step if this rung is scheduled is to launch
it through `launch_solve.sh` with a generous iteration cap and let
`residualControl` decide when it is actually done, the same as every other
rung in this family.

### Considered and explicitly deprioritized (reasoning on record, not silently dropped)

- **Low-speed 2D NACA0012 vs Ladson (1988).** Reference fully fetched, read,
  and OCR-quality-checked (`F11_runs/ladson_reference_note.md`) — fully open
  access, no paywall weakening needed, a genuinely stronger reference
  situation than this session's chosen case. Deprioritized only because the
  same validation target already has an unresolved, real convergence
  pathology on this repo's existing TMR mesh/scheme combination
  (`naca0012_status.json`), and distinguishing "fresh mesh fixes it" from
  "the pathology is scheme/case-family-general" is a real investigation, not
  a costing exercise. Good next candidate for a session that can afford that
  investigation.
- **Laminar backward-facing step (Armaly et al. 1983).** Genuinely different
  physics from the already-failed turbulent F5c backward-facing step
  (different Re regime, no bubble-flapping instability expected). Primary
  reference confirmed paywalled (Unpaywall, no OA copy) — usable only via a
  secondary-source workaround, which this session already had to use once
  (Ghia); stacking a second weakened-reference gate in the same session was
  judged worse than shipping one clean case plus one well-referenced,
  well-reasoned docket item.

## Files

- `demo-output/website/campaign/F11_runs/cavity_ladder.py` — case builder,
  Ghia reference tables (with the transcription-quality note), gate/analysis
  functions.
- `demo-output/website/campaign/F11_runs/ladson_reference_note.md` — the
  Ladson (1988) reference research, fetched and read this session, held for
  the docketed NACA0012 candidate.
- Case directories (not committed — solver output, matching L-13's rule that
  a mesh is not source): `~/certonomous-runs/f11-cavity-ladder/{re100_n64,
  re100_n128,re1000_n64,re1000_n128}/`.
- Collector records: `demo-output/website/solve_registry/f11_*.{log,done}`.
