# F9 — Pulsatile valve-orifice CFD: replacing the reduced-order screen

**Date:** 2026-07-29
**Scope:** Family F9. The mega-batch's `reduced-order` valve family
(`sdk/workflows/valve_study.py`, `solver="reduced-order"`, ~69,000 rows,
median wall time <0.1 s) is a fitted cycle-decomposition orifice screen —
`dp = 0.5*rho*(Q/(Cd*A))^2`, Cd=0.62 fixed — never a solved flow. This
task builds a real pulsatile CFD solve of flow through the valve orifice,
gates it against the ROM three ways, and recommends whether/how the
mega-batch family should change.

**PREDICTION, written before the periodicity-gated numbers below were
read (the first two steady points were already in when this was written,
giving CFD-implied Cd ~1.9-1.95 against the ROM's fixed 0.62):** the
cycle-weighted CFD pressure loss will land far BELOW the ROM's 1849.8 Pa
at 65 deg — order 150-250 Pa, roughly (0.62/1.9)^2 x 1850 Pa if the same
quadratic Q-scaling holds through the cycle — because the ROM's Cd=0.62 is
a thin-sharp-orifice constant calibrated for beta <= 0.75 (ISO 5167), and
this geometry's beta (orifice/pipe radius ratio) at 65 deg is 0.906 — a
mildly-open valve, well outside that calibration range, where real orifice
discharge coefficients are known to run much higher (loss much lower) than
0.62. If the measured deviation lands far outside that band, or in the
wrong direction, that is the finding, not this paragraph.

**Pre-registration is not edited after the fact, so the paragraph above
stands as written. Read it with §9.4: the "CFD-implied Cd ~1.9-1.95" it
leans on was withdrawn on 2026-07-30, and §9.5 shows the discharge
coefficient accounts for 13.5 of the 94 percentage points of deviation,
not all of them. The prediction's DIRECTION was right; its stated
MECHANISM was mostly not.**

---

## 1. What the ROM claims, and what stands in for it here

`valve_study.py`'s `_phase_pressure_loss` decomposes one cardiac cycle into
3 steady phase points (accelerating/peak/decelerating systole, weights
0.25/0.50/0.25) and evaluates a closed-form sharp-orifice correlation at
each, cycle-weighting the result. It predicts: cycle-weighted pressure
loss, a loss envelope (Monte-Carlo over Cd/flow-rate spread), effective
orifice area, and Womersley alpha (~17 at the physiological root radius) —
but never solves a flow. The model channel already names what it drops:
the orifice correlation itself, neglected phase-interaction (inertially
unsteady at alpha~17), fixed leaflets, Newtonian blood.

**What this task solves instead:** the "fixed leaflets" limit of the same
geometry family — the three leaflets frozen at a chosen opening angle,
represented (like the ROM itself) as a sharp-edged axisymmetric orifice of
the identical effective area (`generate_valve.effective_orifice_area`), in
a pipe of the valve's own root radius (0.0115 m). The full 3D, three-leaflet
STL geometry is not meshed here (a snappyHexMesh build of an asymmetric,
moving-leaflet geometry is materially larger scope — it is already on the
ROM's own agenda as unsteady FSI). Opening angle: **65 deg** (mid-sweep of
the ROM's own candidate set, orifice/pipe area ratio 0.821, beta=0.906).

## 2. Method

- **Geometry**: 5-block axisymmetric wedge (5 deg total angle), sharp
  90-degree corners at both faces of a thin (0.1 D) orifice plate — a real
  vena-contracta-forming geometry, not a smoothed venturi. 4,944 cells.
  `checkMesh`: non-orthogonality 0, max skewness 0.33, only the standard
  wedge-axis small-determinant warning (6 cells, benign, documented below).
- **Inflow**: sinusoidal, Q(t) = Q_mean + Q_amp sin(2 pi t/T), Q_mean =
  Q_amp = Q_peak/2 (spans 0 -> Q_peak, the ROM's own flow range), imposed
  via native OpenFOAM `uniformFixedValue` + `Function1` `sine` (no
  runtime-compiled BC). **Not** the ROM's half-sine-with-zero-diastole
  pulse: the closed-form Womersley (1955) solution used for Gate 2 is
  itself derived for sinusoidal forcing, and a pure sinusoid lets that gate
  compare directly without first Fourier-decomposing an asymmetric pulse.
- **Solver**: `pimpleFoam`, **laminar** (no turbulence closure) — a
  deliberate choice, not an expedient one: the Womersley analytic check is
  itself a laminar solution, so RANS would break the one closed-form
  comparison available. Turbulence is therefore named, not modeled: peak
  pipe Reynolds number is ~8,400 (peak throat ~9,250 — the beta ratio is
  high, so the throat isn't much faster than the pipe), solidly in the
  transitional/turbulent range for real valve flow.
- **Two additional structural idealizations, on the record up front**:
  (1) the mesh is a true axisymmetric wedge (one cell in azimuth) — it
  cannot represent any non-axisymmetric instability or turbulent breakdown
  at *any* resolution, by construction, not just because it is laminar;
  (2) the "fixed leaflets" simplification the ROM already admits.
- **Monitors**: `probes` functionObject, every timestep — 3 centerline taps
  (upstream 3D from inlet/2D from the plate, throat mid-plane, downstream
  3D past the plate) for dp, plus a 9-point radial profile at the upstream
  station (2D upstream of the plate) for the Womersley-profile gate.
- **Reference map**: 4 independent steady solves (pimpleFoam marched to a
  stationary state) at Q = 0.25/0.50/0.75/1.00 x Q_peak — this is the
  alpha->0 quasi-steady limit by construction (no unsteady term at all),
  used for Gate 1 and to measure the CFD's own implied discharge
  coefficient for Gate 3.
  **Corrected 2026-07-30**: "marched to a stationary state" is true of the
  upstream-to-throat differential and false of the flow as a whole. Read
  it as "marched until the throat differential is stationary" — the
  downstream field at the highest flow rate never becomes stationary at
  all (§9.2), and the discharge-coefficient clause is withdrawn (§9.4).
- **Tooling**: every launch through `scripts/case_preflight.sh` +
  `scripts/launch_solve.sh`, per project standing rule.

## 3. Staged results

### FEASIBILITY — PASS
Mesh builds clean; `pimpleFoam` runs stably; smoke test to t=0.01 s
completed without incident (~0.085 s/timestep on this ~5k-cell mesh,
single core). No `residualControl`-references-untransported-field trap:
the case carries no turbulence fields to reference (laminar).

### PHYSICS — PASS (corrected 2026-07-29 ~23:00 UTC; the record below was stale, not the run)

> **Re-graded 2026-07-30 by an automated criterion (§9.1).** The periodicity
> claim below rests on a single scalar (`halves_drift` of the cycle-mean
> `dp` over the last two cycles). Criterion **F9-CYC-1** re-grades it on
> five functionals per cycle including the phase-aligned waveform. The
> verdict holds for the quantity it was applied to and **fails for a second
> quantity the same runs report**; and `pulsatile_lowalpha`, whose Gate-1
> number is quoted below, had **fewer than two complete cycles on record**,
> so its periodicity was never testable at all. Both are resolved in §9.1.

**This section was filled in from data that already existed on disk.** Both
pulsatile cases (`pulsatile_physio`, `pulsatile_lowalpha`) had already run to
their full `endTime` — clean completion, `log.pimpleFoam` ends with `End`, no
crash, bounded Courant (physio: mean 0.103, max 0.92; both < 1), continuity
errors of order 1e-10 to 1e-7 throughout — hours before this session started.
`f9_analysis.json` on disk, however, had been generated from an earlier,
mid-run snapshot (`t_end: 1.469`) and reported *"fewer than 2 full cycles
available; periodicity not established."* That was true when written and
false by the time it was read — the same stale-docket failure mode as L-1
(the Re=2000 cylinder rung marked incomplete after it had actually finished).
Caught the same way: `analyze_f9.py` (already written, never re-run since the
solve finished) was re-run against the actual files on disk. Zero core-minutes
spent; this is a P3 zero-compute check, not a new experiment.

`pulsatile_physio` ran the full 3 requested cycles (`t_end=2.7`,
`t_cycle=0.9`, alpha=16.73). Cycle-to-cycle drift (`halves_drift` over the
last two full cycles): **7.0e-7 relative** — the flow is periodic to
essentially machine precision by the third cycle, which is physically
expected for a laminar flow under purely sinusoidal forcing with no
transitional/turbulent broadband content. **Periodicity: PASS, cleanly.**

### GATE — three gates evaluated; two PASS, one FAIL with cause identified

## 4. Gate 1 — quasi-steady limit

Comparison: each pulsatile run's cycle-mean CFD Δp against the value
predicted by feeding that same run's own instantaneous Q(t) through the
power-law fit to the 4 independent steady CFD points (`dp = k·Q^n`,
**n = 1.972**, i.e. the CFD's own steady map is very nearly quadratic in Q —
consistent with a momentum/vena-contracta-dominated loss, not a
viscous-friction one, even though the solve is laminar; this is a sanity
check on the steady map itself, not the gate).

| run | alpha | cycle-mean CFD dp | quasi-steady-predicted dp | deviation |
| --- | --- | --- | --- | --- |
| `pulsatile_physio` | 16.73 | 110.71 Pa | 112.49 Pa | **−1.58%** |
| `pulsatile_lowalpha` | 8.36 | 112.73 Pa | 112.49 Pa | **+0.22%** |

**Verdict: PASS, both runs.** Both land within 1.6% of the quasi-steady
limit, and the direction is physically coherent: the lower-alpha run (slower
forcing, closer to the quasi-steady limit by definition of the Womersley
number) shows the smaller deviation. This is not a single lucky point — two
independent alpha values move in the direction inertial-unsteadiness theory
predicts.

## 5. Gate 2 — Womersley-regime sanity

Comparison: CFD radial velocity profile (9-probe radial sweep, 2 diameters
upstream of the orifice plate) against the closed-form Womersley (1955)
profile at 4 phases per cycle, using each run's own alpha and Q(t). Profiles
compared via a flatness parameter (centerline / mean velocity: 2.0 for
Poiseuille, →1.0 as a profile flattens toward plug flow) and a mean absolute
relative error across the 9 radial stations.

| run | phase t/T | CFD flatness | analytic flatness | mean abs rel. error |
| --- | --- | --- | --- | --- |
| physio (alpha=16.73) | 0.00 | 1.02 | 1.39 | 32% |
| physio | 0.25 | 1.00 | 1.22 | 20% |
| physio | 0.50 | 1.01 | 1.39 | 37% |
| physio | 0.75 | 1.82 | 2.66 | 85% |
| lowalpha (alpha=8.36) | 0.00 | 1.01 | 1.33 | 23% |
| lowalpha | 0.25 | 2.11 | 1.21 | 99% |
| lowalpha | 0.50 | 1.01 | 1.43 | 45% |
| lowalpha | 0.75 | 1.00 | 3.05 (analytic goes **negative** near the wall — predicted reversal) | 414% |

**Verdict: FAIL, as a point comparison against the closed-form Womersley
profile — reported as measured, not softened.** Errors of 20–414% at every
phase and both alpha values, and at `lowalpha` t/T=0.75 the analytic solution
predicts near-wall flow reversal (values run negative) that the CFD does not
show at all (uniform, positive, plug-like).

**Original cause, as first proposed (2026-07-29), stated then as a
hypothesis, not yet confirmed:** the profile probe station sits only **2
pipe diameters upstream** of a beta=0.906 orifice — a very weak restriction
(81% open by area), meaning the flow is already accelerating and converging
toward the plate at that station. Convective acceleration ahead of a
restriction is a well-known mechanism for flattening a velocity profile
relative to undisturbed fully-developed flow — consistent with CFD flatness
sitting close to 1.0 (plug-like) at every phase except the wall-affected
0.75 point. **Falsifiable follow-up specified at the time:** re-run the
profile probe at 4–5 diameters upstream, on the already-built mesh, and
check whether flatness/rel-error close the gap moving upstream.

### Follow-up, run 2026-07-30: the hypothesis is REFUTED

The restart case `F9_work/womersley_probe_check` reproduces
`pulsatile_physio`'s last cycle bit-for-bit (restarted from its `t=1.8`
checkpoint, same mesh/BCs/schemes — final cumulative continuity error
−2.0139e-07 vs. the original run's −2.0114e-07, i.e. the same solve),
with three additional 9-probe radial stations added at 3D, 4D and 4.5D
upstream of the plate (the original station, 2D upstream, is retained
unchanged for direct comparison). Cost: 246.32 s single-core (a restart
from the last cycle's checkpoint, not a full 3-cycle re-solve).

**Result — the error gets WORSE moving upstream, monotonically, at every
single phase tested, not better:**

| station (upstream of plate) | t/T=0.00 | t/T=0.25 | t/T=0.50 | t/T=0.75 | avg |
| --- | --- | --- | --- | --- | --- |
| 2D (original) | 31.6% | 20.0% | 36.9% | 84.6% | 43.3% |
| 3D (new) | 34.1% | 21.4% | 39.5% | 88.9% | 46.0% |
| 4D (new) | 35.7% | 22.9% | 42.4% | 94.0% | 48.8% |
| 4.5D (new) | 36.7% | 23.9% | 43.9% | 97.1% | 50.4% |

Every column increases monotonically left to right. The predicted result
if the "convective acceleration near the orifice" hypothesis were correct
was the opposite — error closing substantially moving away from the
plate. It does not close; it grows. **That hypothesis is refuted, cleanly,
not just unconfirmed.**

**What the data supports instead: the pipe is too short, relative to the
Reynolds numbers in play, for the flow to develop away from the flat inlet
condition anywhere inside it — an entrance-length problem, not an
exit/restriction problem.** The inlet BC (`uniformFixedValue`, per the
Method section) imposes a spatially uniform (flat) velocity at `x=0` by
construction. The standard laminar developing-pipe-flow entrance-length
estimate, `L_entry/D ≈ 0.05–0.06·Re`, evaluated at this case's own peak
pipe Reynolds number (Re_peak = U_peak·D/nu = 1.2034 × 0.023 / 3.3e-6 ≈
**8388**), gives `L_entry ≈ 420–500 diameters` — 9.6 to 11.6 m — against
the **5 diameters (115 mm)** actually available in this mesh before the
first monitoring station. Even at the cycle-mean Reynolds number (Re ≈
4194, half the peak), the estimate is still ≈ 210–250 diameters, still two
orders of magnitude short. Under this explanation, the profile should stay
close to the imposed flat inlet shape everywhere in the pipe, with the
mismatch to the analytic (implicitly fully-developed/undisturbed) Womersley
profile getting slightly *worse*, not better, closer to the inlet where the
flow has had the least distance to relax from the imposed condition —
exactly the monotonic trend measured. This is a **domain-length /
inlet-boundary-condition mismatch with the closed-form comparison's own
assumptions, not a solver defect and not (as first guessed) an
orifice-proximity artifact.** It generalizes: any short-pipe CFD case
driven by a flat-profile inlet BC and compared against a
fully-developed/undisturbed analytic solution should expect the same
failure mode unless the entrance length is checked against the pipe length
before the comparison is designed, the same class of domain-vs-idealization
mismatch as L-8's dam-break front-position lesson.

> **The entrance-length explanation below was turned into a falsifiable
> prediction and tested on 2026-07-30 (§9.3). It passed, on two independent
> axes, and it changes the Gate-2 verdict**: split into its steady and
> oscillatory parts, the CFD profile matches the exact Womersley
> oscillatory solution to 7.7% and misses Hagen-Poiseuille by 34%, exactly
> as an entrance-length limitation predicts and no other explanation on the
> table predicts. Read §9.3 before quoting the flat FAIL below.

**Verdict, updated: Gate 2 stays FAIL, now with a refuted first hypothesis
and a quantitatively supported second one**, not a comparison-basis
artifact as originally guessed. A genuine fix (prescribing an
entrance-appropriate inlet profile, or lengthening the upstream section
enough to matter — impractical here given the entrance-length numbers
above, since even 20-30D would still fall short at peak Re) is out of
scope for this gate; this is exactly the "turns into a genuine finding"
outcome, not a bug in the CFD or the comparison method chosen, but a real
domain-sizing constraint on what a short-pipe internal flow case can be
validated against with a closed-form entrance-flow solution. Raw follow-up
data: `F9_work/womersley_followup_results.json`,
`F9_work/womersley_probe_check/`.

## 6. Gate 3 — deviation from the ROM, with cause

> **WITHDRAWN 2026-07-30: every "CFD-implied discharge coefficient" in §6
> and §6b (the values 1.219, 1.370, 1.91–1.95).** They were computed from
> `Cd = Q / (A_orifice sqrt(2 dp/rho))`, which omits the velocity-of-approach
> factor that ISO 5167's own coefficient carries, and they were computed
> from a `dp` that is **not a loss**: the upstream and throat probes lie on
> the same centreline streamline and their total heads agree to 0.01–0.34%
> of that `dp` (§9.4). A reversible acceleration cannot be fitted to a
> discharge coefficient. The −94.0% ROM deviation is **not withdrawn** (it
> is a measured pressure against a computed one), but its attribution
> below is superseded by the three-term decomposition in §9.5, in which the
> discharge coefficient accounts for 13.5 of the 94 points, not all of them.

**Pre-registered prediction (written before this data was read — see the top
of this file):** cycle-weighted CFD loss "far BELOW" the ROM's 1849.8 Pa,
"order 150–250 Pa," reasoning from `(0.62/Cd_cfd)^2 × 1850 Pa` using the
CFD's own implied discharge coefficient.

**Measured:** `pulsatile_physio` cycle-mean CFD Δp = **110.71 Pa** vs. the
ROM's own 3-phase-weighted `_cycle_weighted_loss(65°)` = **1849.77 Pa**.
**Deviation: −94.0%.**

**Verdict: prediction direction and order of magnitude CONFIRMED; point
value not matched — reported plainly.** The measured value is even further
below the ROM than the pre-registered band's low end (110.7 Pa vs. the
150–250 Pa predicted), by about 26–56%. A same-session refinement of the
back-of-envelope check — `(0.62 / Cd_cfd,avg=1.94)^2 × 1850 Pa ≈ 189 Pa` using
the actual measured steady-map Cd rather than the prediction's assumed 1.9 —
still overshoots the real cycle-weighted CFD result by ~41%. The Cd
mismatch (ROM's fixed 0.62 vs. CFD's measured 1.91–1.95 across the whole
flow range, itself expected: ISO 5167's Reader-Harris/Gallagher correlation
is calibrated for beta ≤ 0.75, and this geometry's beta = 0.906) explains
most but evidently not all of the gap — the remainder is most plausibly the
ROM's discrete 3-phase-point cycle weighting vs. the CFD's continuous
sinusoidal integral, and the steady power-law exponent (n=1.972, not exactly
2) both integrating slightly differently over a cycle than a single-point Cd
correction assumes. Not chased further this session; flagged as an open,
cheap (zero-compute, arithmetic-only) follow-up.

**Root cause of the ROM/CFD gap, at the level that matters for the
mega-batch decision:** the ROM's Cd=0.62 constant is a thin-sharp-orifice
correlation constant validated for beta ≤ 0.75. This valve geometry at its
default 65° opening sits at beta=0.906 — outside the calibrated range in the
ROM's own cited standard — and the CFD's independently measured discharge
coefficient (1.91–1.95, tightly banded across a 4× flow-rate sweep) confirms
the real coefficient at this opening is over 3× the ROM's assumed value.
**The ROM is not wrong about the physics it models (a sharp-orifice
correlation); it is being applied outside its own calibrated domain**, which
is exactly the finding the pre-registered prediction anticipated.

## 6b. Disclaimer-boundary sweep (2026-07-30 follow-up)

Two more geometry points were run at 50° (β=0.766) and 55° (β=0.819) —
bracketing the ISO 5167 calibration edge (β≤0.75) the ROM's Cd=0.62 is
drawn from, per the recommendation in §7 — to test where between the
calibrated region and this case's own default (65°, β=0.906) the ROM's
error becomes large.

**Solver/label check, done from the primary artifacts, not inferred from
the case names.** Both runs are named `steady_beta_50deg`/`steady_beta_55deg`
and both exited with `check_convergence.py` returning `CANNOT_TELL`
("looks like a transient/unsteady run... a steady-state convergence gate
does not apply here"). That is not a mismatch: the `Exec:` line in both
logs reads `pimpleFoam`, and `system/controlDict` for both cases is
**byte-identical** to `steady_q100`'s (`diff` clean) — `application
pimpleFoam; startTime 0; endTime 1.2`, fixed-value steady inlet at
`u0=1.20344` (`0/U` also diffs clean against `steady_q100`'s except for
the mesh-dependent probe/geometry lines, same `fixedValue` BC, same value).
This is the **same convention already used and already gated** for all
four original reference-map points (`steady_q25/50/75/100`): `pimpleFoam`
marched to a fixed `endTime` under steady boundary conditions, judged
stationary by a tail-window check, not `simpleFoam` with
`residualControl` — documented in §2's Method section and independently
confirmed earlier this session by running `check_convergence.py` against
all four original points, which returned the identical `CANNOT_TELL` for
the identical reason. The label is correct; `CANNOT_TELL` is the correct
machine answer for this whole 6-run family, and always has been.

> **Two 2026-07-30 corrections apply to this section.** The `Cd_cfd`
> column in the results table below (1.219 and 1.370) is **withdrawn** for
> the reasons in §9.4, and with it the "no plateau of small error" reading
> built on it; the `(0.62/Cd_cfd)² × ROM loss` column and its implied
> deviations go with it. The measured `dp` values themselves stand. The
> §9.5 replacement analysis reaches the same practical recommendation by a
> stronger route that needs no CFD at all.
>
> **Re-graded 2026-07-30 by criterion F9-STAT-1 (§9.2).** The by-hand
> judgement below is **upheld for the quantity it checked** (`dp` upstream
> to throat: all six original steady points pass all four automated tests).
> It is **not** upheld for `dp_upstream_to_downstream`, a second quantity
> these same runs publish in `F9_pulsatile_valve.json`: at `steady_q100`,
> 50° and 55° that signal fails stationarity outright, with a peak-to-trough
> band of 39%, 113% and 128% of its own mean. It is not a settling
> transient. It is a self-sustained jet oscillation, and §9.2 shows it sits
> at the Strouhal number a shed shear layer is expected at.

**Stationarity, judged by hand, window and variation stated explicitly.**
The raw upstream probe (`p0`) alone is **not** stationary in either
case — it oscillates with relative amplitude 129–171% of its own mean
even in the last 5% of the 1.2 s run, the same global, spatially-correlated
absolute-pressure-level wobble already found and explained for
`steady_q100` (§3): upstream and throat probes move together, so it
cancels in the pressure *difference*. The quantity actually used for every
Cd/ROM figure, `dp = (p_upstream − p_throat)·ρ`, is what was checked for
stationarity, over the **last 10% of run time** (t ∈ [1.08, 1.2] s,
matching `analyze_f9.py`'s own `tail_frac=0.1` convention, chosen to match
what the original four points were judged against):

| case | window mean dp (Pa) | band (max−min) over window | relative band | first-half vs second-half drift |
| --- | --- | --- | --- | --- |
| `steady_beta_50deg` | 1499.61 | 5.76 Pa | 0.384% | 8.62e-5 |
| `steady_beta_55deg` | 908.99 | 3.74 Pa | 0.411% | 3.99e-4 |

Both bands shrink monotonically going from the full run (>3000% relative
band, dominated by the initial transient) through the middle-half and into
the tail window (converging to <0.5%), the same settling pattern the
original four points showed. **Both judged stationary; PASS on the
stationarity check**, by the same standard and the same window as the
existing four points.

**Result.** Using each angle's own orifice area and the same `Q=Q_peak`
convention as the original `steady_q100` point (chosen because Gate 1
established Cd is essentially flow-rate-invariant at 65° — a single point
per new angle is treated as a reasonable, cheap estimate of Cd(angle) on
that basis, not re-verified across a flow sweep at each new angle; that
extrapolation is disclosed, not hidden):

| angle | β (radius ratio) | area ratio | CFD dp at Q_peak (Pa) | Cd_cfd | ROM cycle-weighted loss at cd=0.62 (Pa) | (0.62/Cd_cfd)² × ROM loss, Pa | implied deviation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 50° | 0.766 | 0.587 | 1499.61 | **1.219** | 3624.14 | ~937 | **≈ −74%** |
| 55° | 0.819 | 0.671 | 908.99 | **1.370** | 2771.81 | ~568 | **≈ −80%** |
| 65° (existing) | 0.906 | 0.821 | (cycle-weighted, measured directly) | 1.91–1.95 | 1849.77 | (measured: 110.71) | **−94.0%** (measured, not scaled) |

**This does not support a clean "boundary" — say so plainly, as asked.**
The original framing in §7 ("a couple more CFD points near β=0.75–0.85
would supply the boundary") implied a transition somewhere in that range,
with the ROM presumably still reasonable near its own calibration edge.
That is not what was measured. **At β=0.766 — already past the ISO
5167 calibration edge (β≤0.75), but only just — the CFD-implied Cd (1.22)
is already ~2× the ROM's fixed 0.62, and the estimated cycle-weighted
deviation is already of order −74%,** not a small correction near the
boundary that grows gradually to −94% by β=0.906. The three points (0.766,
0.819, 0.906) show a smooth, monotonic trend in Cd_cfd and in deviation,
with no sign of a "safe" plateau anywhere in the tested range. **No point
in this sweep sits inside the ISO-calibrated domain (β≤0.75) — that
region was not tested, so this does not show the ROM is fine there
either; it only shows the ROM is already substantially wrong immediately
outside it, closer to the edge than the original recommendation assumed.**

**Revised recommendation on the disclaimer boundary:** do not word the
`valve_study.py` disclaimer as "unreliable above β≈0.8–0.9" or similar —
the data here says the error is already large (order −75%, roughly a
factor of ~2 in Cd) right at the edge of the ROM's own stated calibration
range. The defensible, conservative wording is to flag the ROM at
**β>0.75 outright** (i.e., exactly the ISO 5167 boundary already printed
in the ROM's own citation, taken at face value, with no attempt to widen
it), and to note explicitly — as an open question, not a resolved one —
that whether the ROM is trustworthy *inside* β≤0.75 for this valve's
leaflet-derived (not flat-plate) orifice shape has not been tested by any
CFD point in this study; the four original 65° points and these two new
ones are the entirety of the CFD evidence gathered, and all six sit at
β≥0.766.

Raw data: `F9_work/steady_beta_50deg/`, `F9_work/steady_beta_55deg/`,
`F9_work/beta_boundary_results.json`. Cost: 831.98 s + 678.93 s = 1510.91 s
(~25.2 min), single core each — steady solves at these narrower orifices
ran longer than `steady_q100` despite the identical pipe-level flow rate,
because a smaller orifice at the same Q means a faster throat jet and a
smaller Courant-limited timestep.

## 7. Cost and mega-batch recommendation

> **Superseded in part by §9 (2026-07-30).** Two sentences below no longer
> hold. (a) "F9 is ready to promote from 'not started' to a real, gated
> family" overstates it: every gate F9 passes is verification or internal
> consistency, and the case is validated against nothing (§9.7). (b) The
> disclaimer recommendation is right but for the wrong reason. The ROM's
> defect is not primarily that beta sits outside ISO's calibrated range;
> it is that `dp = 0.5 rho (Q/(Cd A))²` has no beta → 1 limit at all and
> reports 1248 Pa of loss through a completely unobstructed pipe (§9.5).
> The disclaimer implemented in the act names the 0.75 ceiling because
> that is the shortest true thing to say on camera; the record should
> carry the stronger reason. Cost totals below are extended in §9.9.

**Measured wall-clock cost** (from `solve_registry` logs,
`ExecutionTime`, single core, no MPI; corrected 2026-07-30 — the table
below previously understated this by ~32%, see note):

| stage | wall-clock |
| --- | --- |
| `steady_q25` | 132.94 s (~2.2 min) |
| `steady_q50` | 244.98 s (~4.1 min) |
| `steady_q75` | 363.15 s (~6.1 min) |
| `steady_q100` | 480.81 s (~8.0 min) |
| 4× steady reference points, subtotal | 1221.88 s (~20.4 min) |
| `pulsatile_physio` (3 cycles, t=0→2.7) | 646.45 s (~10.8 min) |
| `pulsatile_lowalpha` (1.5 cycles, t=0→5.4, T=4×physio) | 1227.54 s (~20.5 min) |
| original 6-run gate, subtotal | 3095.87 s (~51.6 min) |
| `womersley_probe_check` (2026-07-30, Gate 2 follow-up, restart from t=1.8) | 246.32 s (~4.1 min) |
| `steady_beta_50deg` (2026-07-30, disclaimer-boundary sweep) | 831.98 s (~13.9 min) |
| `steady_beta_55deg` (2026-07-30, disclaimer-boundary sweep) | 678.93 s (~11.3 min) |
| **grand total, all F9 compute to date** | **4853.10 s, ~80.9 min (~1.35 core-hours)** |

Total for the original 3-gate pass: **3095.87 s, ~51.6
core-minutes (~0.86 core-hours)**, single core throughout. **Correction:**
the previous version of this table quoted the steady points as "tens of
seconds each (sub-minute)" and a total "well under 35 core-minutes" — both
wrong, caught during an independent re-verification pass against the raw
`ExecutionTime` lines in `solve_registry` (the steady runs individually
take 2.2–8.0 minutes, scaling with flow rate/Courant-limited timestep, not
sub-minute; the true total is ~1.5x the originally reported figure). This
does not change any gate verdict or the ROM-deviation finding — all of
those were independently re-derived from the raw probe data and ROM source
during the same pass and matched to within numerical noise (see the
mega-batch recommendation below, which does not depend on the exact
core-minute figure). Still an order of magnitude cheaper than the
mega-batch's other 3D-viscous family (F10 Ahmed body, low-single-digit
minutes *per evaluation*, this is the whole multi-run gate).

**Recommendation:** F9 is ready to promote from "not started" to a real,
gated family. Two of three gates PASS (quasi-steady limit, and the
qualitative ROM-deviation direction/magnitude); the Womersley profile gate
FAILs, and stays FAIL after the falsifiable follow-up run 2026-07-30 (§5) —
the original "probe too close to the orifice" hypothesis was tested
directly and **refuted** (error grows, not shrinks, moving upstream, at
every phase), and the data instead supports a genuine, quantitatively
argued entrance-length limitation (the 5D pipe is ~2 orders of magnitude
shorter than this Reynolds-number range needs to relax away from the flat
inlet BC). This is a real, understood finding about what a short-pipe
internal-flow case can be checked against with a closed-form
fully-developed-flow solution, not a defect in the CFD. The reduced-order
`valve_study.py` family should carry an explicit disclaimer, worded
plainly as **β>0.75** (the ISO 5167 boundary already in the ROM's own
citation, taken at face value) — the §6b disclaimer-boundary sweep (50°/55°,
run 2026-07-30) does **not** support a gentler transition zone: the
CFD-implied Cd is already ~2× the ROM's fixed value and the estimated
cycle-weighted deviation is already of order −74% right at β=0.766, just
past that edge, with no plateau of small error found anywhere in the
0.766–0.906 range tested. Whether the ROM is trustworthy *inside* β≤0.75
for this valve's specific (leaflet-derived, not flat-plate) orifice shape
remains untested by any CFD point in this study and should not be assumed
from the ISO citation alone.

## 8. References

- Womersley, J.R. (1955) "Method for the calculation of velocity, rate of
  flow and viscous drag in arteries when the pressure gradient is known,"
  *J. Physiol.* 127(3):553-563. DOI: 10.1113/jphysiol.1955.sp005276.
- ISO 5167 (orifice-plate discharge coefficient, Reader-Harris/Gallagher
  correlation): concentric orifice plates are calibrated for beta
  (bore/pipe diameter ratio) in [0.20, 0.75]; this geometry's beta at 65
  deg opening is 0.906 (radius ratio) — outside that calibrated range.
- `sdk/workflows/valve_study.py`, `models/curriculum/aortic_valve/` (ROM
  and geometry being compared against).
- `docs/physics_rules.yaml` (`womersley.strict_quasi_steady_max`=1.0,
  `womersley.multipoint_screening_max`=25.0).

Added 2026-07-30 (round 3):

- ISO 5167-2, the orifice-plate part: the mass-flow equation carries the
  velocity-of-approach factor `E = 1/sqrt(1 - beta^4)` explicitly and
  specifies corner, D and D/2, or flange **wall** tappings. Both matter to
  §9.4: the discharge coefficient F9 quoted omitted the first and was
  measured at none of the second.
- Roache, P.J. (1994) "Perspective: A method for uniform reporting of grid
  refinement studies," *J. Fluids Eng.* 116(3):405-413 — the grid
  convergence index and the observed-order estimate used in §9.6. The
  implementation refuses to quote a GCI when the three levels are not
  monotone, because the Richardson extrapolation it rests on does not
  apply there.
- The Strouhal number of a separating shear layer sits near 0.2 over a
  wide range of geometries and Reynolds numbers; §9.2 uses only that
  order-of-magnitude expectation, to separate a physical instability from
  numerical noise, and claims nothing sharper.
- Hagen-Poiseuille friction and the laminar entrance-length estimate
  `L/D ≈ 0.05 Re` are standard textbook results, used in §9.3 and §9.5 as
  the limits the solutions must approach, not as validation references.

---

## 9. Round 3 (2026-07-30) — automated convergence criteria, a tested prediction, and what this case is actually graded against

Three things were open after §6b: stationarity was judged by hand, the
entrance-length explanation had not been turned into a prediction and
tested, and nobody had written down what this case is graded against.
This round closes all three and, in doing so, withdraws one number the
earlier record leaned on. New code: `F9_work/f9_criteria.py` (criteria and
audits, reads probe files already on disk) and `F9_work/setup_f9_round3.py`
(the new cases). Machine-readable output: `F9_work/f9_criteria.json`.

### 9.1 Criterion F9-CYC-1 — cycle-to-cycle convergence, stated as a number

**The criterion.** For a run forced at period `T`, cut whole cycles
backwards from `t_end`. For each monitored signal and each cycle take the
time-weighted cycle mean, the cycle maximum, the cycle minimum, the cycle
band (max − min), and the waveform resampled onto 256 uniform phase
points. Between consecutive cycles form five relative changes: `e_mean`,
`e_max`, `e_band` (each normalised by the later cycle's own value) and
`e_wave_inf`, `e_wave_rms` (the L∞ and L2 norms of the phase-aligned
waveform difference, normalised by the later cycle's **band**, because a
pulsatile mean passes through zero and a mean-normalised waveform error
there is meaningless). **PASS when all five are below `TOL_CYC = 1e-3` for
the most recent consecutive pair.** The threshold is chosen to sit far
below this case's measured discretization error (§9.6), so periodicity
contributes nothing to the reported uncertainty.

**Stroke volume is deliberately not the gate.** It is the obvious
candidate and it is the wrong one here: the solver is incompressible with
rigid walls and a prescribed inlet flux, so the true volume flux through
every cross-section equals the imposed inlet flux at every instant, by
mass conservation. Stroke volume is a boundary condition, not a solution
output. What a probe rake can actually measure is a 9-point quadrature of
the profile (which lands 4.4% below the exact `Q_mean` because it cannot
see the near-wall region), so it is a profile-shape metric wearing a
stroke-volume label. It is computed and reported anyway, so that no later
reader reaches for it as evidence.

**Did the by-hand judgement hold?** For the quantity it was applied to,
yes, and by a wide margin.

| run | signal | complete cycles | worst of the five, last pair | verdict |
| --- | --- | --- | --- | --- |
| `pulsatile_physio` | dp upstream→throat | 3 | **8.5e-6** | **PERIODIC** |
| `pulsatile_physio` | dp upstream→downstream | 3 | **1.39e-3** | **NOT PERIODIC** (fails 1e-3) |
| `pulsatile_physio` | rake volume-flux quadrature | 3 | 9.1e-7 | PERIODIC |
| `lowalpha_ext` | dp upstream→throat | 3 | **3.6e-8** | **PERIODIC** |
| `lowalpha_ext` | dp upstream→downstream | 3 | 9.9e-8 | PERIODIC |
| `lowalpha_ext` | rake volume-flux quadrature | 3 | 3.7e-8 | PERIODIC |
| `pulsatile_lowalpha` (as it stood) | any | **1** | not testable | **NOT TESTABLE** |

Three findings, in order of how much they matter.

**(a) `pulsatile_lowalpha`'s periodicity was never established, and its
Gate-1 number was published anyway.** The run stopped at `t=5.4` with
`T=3.6`: one complete cycle in the probe record. `analyze_f9.py` handles
this correctly (`cycle_to_cycle_drift: null`) but §4's Gate-1 table quotes
its cycle-mean of 112.73 Pa and its +0.22% deviation with no such caveat,
and §7 counts Gate 1 as PASS on the strength of *two* alpha values moving
the right way. **Fixed by running it out**: `F9_work/lowalpha_ext` restarts
from the `t=5.4` checkpoint to `t=10.8`, giving three complete cycles.
Result: periodic to **3.6e-8**, and the cycle-mean is **112.721 Pa**
against the 112.734 Pa the record published, a change of 1.2e-4. Gate 1's
low-alpha deviation becomes **+0.203%** (was +0.22%). **The published
number was right; the record had no right to be sure of it until now.**
That distinction is the whole point of having a criterion.

**(b) The downstream differential is not cycle-converged to 1e-3.** (It is
the closest thing this case has to a permanent loss, though §9.2 shows it
is not one either.) `dp_upstream_to_downstream` in `pulsatile_physio`
lands at 1.39e-3 on
`e_wave_inf` and 5.7e-4 on `e_mean`, i.e. it would pass at 2e-3 and fails
at the stated 1e-3. Reported as measured, not softened by moving the
threshold after seeing the number. §9.2 explains why this signal in
particular is the hard one.

**(c) A scalar cycle-mean test cannot see a non-periodic cycle.** Between
cycles 1 and 2 of `pulsatile_physio` the cycle MEAN of the throat `dp`
changes by only **2.1%**, while the cycle PEAK changes by a factor of
**18.5** (`e_max = 1.747e+1`) and the phase-aligned waveform by
`e_wave_inf = 1.19e+1` — the impulsive-start spike of 7110 Pa sitting in
cycle 1 against 385 Pa in cycle 2. Any criterion built on the cycle mean
alone would have called cycle 1 nearly converged. It is not. This is the
concrete argument for the five-functional form, independent of whether the
verdict changed on this particular run.

### 9.2 Criterion F9-STAT-1 — stationarity of the fixed-BC runs, and a jet that never settles

**The criterion.** Over the tail window `W = [0.9 t_end, t_end]`, all four
of: band ratio `(max−min)/|mean| < 1e-2`; halves drift `< 1e-3`; **tail
trend** `|LSQ slope|·|W|/|mean| < 1e-3`; **window shift** `|mean(10% tail)
− mean(20% tail)|/|mean| < 1e-3`. The last two are the ones the by-hand
check did not do: a slow monotone creep hides inside a narrow band, and a
mean that moves when the window moves is not a converged value however
tight its band looks.

| case | dp upstream→throat | dp upstream→downstream |
| --- | --- | --- |
| `steady_q25` | STATIONARY (band 1.4e-7) | STATIONARY (band 5.9e-5) |
| `steady_q50` | STATIONARY (band 5.7e-7) | STATIONARY (band 1.6e-6) |
| `steady_q75` | STATIONARY (band 5.7e-7) | STATIONARY (band 7.3e-5) |
| `steady_q100` | STATIONARY (band 9.0e-5) | **NOT STATIONARY** (band **0.385**, trend 2.4e-2) |
| `steady_beta_50deg` | STATIONARY (band 3.8e-3) | **NOT STATIONARY** (band **1.130**, trend 2.7e-1) |
| `steady_beta_55deg` | STATIONARY (band 4.1e-3) | **NOT STATIONARY** (band **1.281**, trend 6.3e-2) |
| `mesh_coarse_q100` | STATIONARY (band 7.2e-9) | STATIONARY (band 1.4e-8) |

**The by-hand judgement in §6b is upheld exactly as far as it went and no
further.** All six original steady points pass all four automated tests on
`dp` upstream-to-throat, the quantity §6b actually checked — including the
two tests it did not perform. So the hand call was right.

**But the same runs publish a second `dp` in
`F9_pulsatile_valve.json` — `dp_upstream_to_downstream` — and at the three
highest-loading cases it is not stationary at all.** At 50° its
peak-to-trough band is 113% of its own mean and the tail-window mean moves
22% between window halves; at `steady_q100` it is still climbing (quarter
means 214.0 → 226.5 → 237.0 → 257.1 Pa over the run). Those published
values are not converged numbers.

**It is not a settling transient; it is a shed jet.** The oscillation
persists at constant amplitude over the last 60% of the 50° and 55° runs.
Timing it and forming `St = f·d_orifice/U_throat` puts it at the Strouhal
number a separating shear layer is expected at, which is what tells the
difference between a physical instability and numerical noise:

| case | oscillation frequency | orifice diameter | throat velocity | St |
| --- | --- | --- | --- | --- |
| `steady_q100` (65°) | 17.33 Hz | 20.85 mm | 1.465 m/s | **0.247** |
| `steady_beta_50deg` | 24.77 Hz | 17.62 mm | 2.051 m/s | **0.213** |
| `steady_beta_55deg` | 20.26 Hz | 18.84 mm | 1.793 m/s | **0.213** |

Three independent geometries and flow rates land at St = 0.21 to 0.25.
Numerical noise does not do that.

The onset is ordered exactly as the physics says it should be: the three
low-flow points (`q25`, `q50`, `q75`) are quiet, and unsteadiness appears
at the highest flow rate and at the two most constricted orifices — the
three cases with the fastest throat jet. Note also that this is an
axisymmetric wedge mesh, so what is shedding can only be a ring vortex;
the real three-dimensional instability is excluded by construction (§2).

**Consequences.** (1) §2's description of the reference map as
"pimpleFoam marched to a stationary state" is true of the throat tap and
false of the downstream field; the phrase should read "marched until the
throat differential is stationary". (2) The permanent pressure loss —
which is the quantity a valve is actually judged on — **cannot be measured
on this mesh as built**. The downstream tap sits 3D past the plate, inside
the jet-redevelopment region, and the domain only offers 8D before the
outlet. A converged permanent loss needs the tap beyond redevelopment
(order 8–10D for a pipe orifice) and a mean phase-averaged over an integer
number of shedding periods, neither of which this geometry provides. That
is the same class of finding as §5's entrance-length limit, at the other
end of the pipe.

### 9.3 The entrance-length explanation made a prediction. It was tested. It holds.

§5 replaced the refuted orifice-proximity hypothesis with an
entrance-length one. An explanation that only explains is not worth much;
this one makes a sharp, falsifiable prediction, which was written into
`f9_criteria.entrance_test`'s docstring before the numbers were read.

**The prediction.** The analytic Womersley solution used in Gate 2 is a
superposition of two parts, and they have completely different development
lengths:

- the **steady** part is Hagen-Poiseuille, whose entrance length is
  `L_steady/D ≈ 0.05·Re = 210 D` at this case's cycle-mean Reynolds
  number. The pipe offers 5D. **It cannot develop, so the CFD must miss
  it.**
- the **oscillatory** part is a Stokes layer, which is established in
  about one radian of forcing, i.e. over the distance the mean flow
  carries a particle in that time: `L_osc = U_bulk/omega`, or in
  dimensionless form **`L_osc/D = Re/(4 alpha^2)`**. That is 3.75 D at
  alpha=16.73 and 14.99 D at alpha=8.36, against 3.0 D of pipe upstream of
  the sampling station. **So the CFD must match the oscillatory part well
  at the high alpha and markedly worse at the low one** — which is the
  opposite ordering from what a solver defect would produce (a defect gets
  worse as the flow gets more unsteady, not better) and is invisible in the
  total-profile error §5 reported.

**The test.** Least-squares fit `u(r,t) = a0(r) + Im[A(r) e^{i omega t}]`
to each radial probe over the last complete cycle, in absolute solver
time, so the fit is phase-locked to the inlet `Function1 sine` itself.
Grade `a0` against Hagen-Poiseuille and the complex `A` against the exact
Womersley oscillatory solution at the run's own alpha.

**Axis 1 — the two parts behave completely differently, as predicted.**
At `pulsatile_physio`'s original station:

| r/R | a0 CFD | a0 Poiseuille | \|A\| CFD | \|A\| exact | arg A CFD | arg A exact | \|A\| error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.051 | 0.6886 | 1.2003 | 0.6323 | 0.6548 | −1.06° | −5.06° | 7.7% |
| 0.256 | 0.6903 | 1.1248 | 0.6324 | 0.6549 | −1.08° | −5.04° | 7.6% |
| 0.460 | 0.6942 | 0.9488 | 0.6327 | 0.6531 | −1.14° | −5.04° | 7.4% |
| 0.664 | 0.6983 | 0.6721 | 0.6389 | 0.6651 | −1.68° | −6.02° | 8.4% |
| 0.869 | 0.5669 | 0.2949 | 0.6945 | 0.6687 | +0.73° | +7.83° | 13.2% |

The steady part is flat at ≈0.69 m/s where Poiseuille demands a parabola
from 1.20 to 0.29 — a 34.0% mismatch, the imposed flat inlet profile
essentially unrelaxed. The oscillatory part matches the exact solution to
**7.7%** in amplitude and **4°** in phase across the whole core. **These
are the same nine probes, in the same file, at the same instants.** One
part of the solution matches exact theory to single-digit percent while
the other misses by a third, and the split falls exactly where the
entrance-length argument says it must.

**Robustness of the fit, checked before the result was used.** Repeating
the whole grading on the *previous* cycle instead of the last reproduces
`pulsatile_physio` to the printed digits (34.05% and 7.75% both times), as
a periodic solution must. Adding a second harmonic to the fit changes the
first-harmonic error only from 7.75% to 7.59%, and the second-harmonic
amplitude is at most 2.8% of the first anywhere in the rake, so the
single-harmonic decomposition is adequate and the flow at this station is
effectively linear. `pulsatile_lowalpha` moves slightly between cycles
(21.26% vs 20.52%), which is the same run whose periodicity §9.1 shows was
never established.

**Axis 2 — the residual oscillatory error scales with development
length, in both directions.**

| run / station | alpha | x/D from inlet | L_osc/D | x/L_osc | steady-part error | harmonic-1 error |
| --- | --- | --- | --- | --- | --- | --- |
| `physio` 2D upstream of plate | 16.73 | 3.0 | 3.75 | 0.80 | 34.0% | **7.7%** |
| `probe_check` 3D upstream | 16.73 | 2.0 | 3.75 | 0.53 | 35.9% | **9.2%** |
| `probe_check` 4D upstream | 16.73 | 1.0 | 3.75 | 0.27 | 38.3% | **10.5%** |
| `probe_check` 4.5D upstream | 16.73 | 0.5 | 3.75 | 0.13 | 39.9% | **11.3%** |
| `lowalpha` 2D upstream of plate | 8.36 | 3.0 | 14.99 | 0.20 | 34.7% | **21.3%** |

Within one alpha the harmonic error falls monotonically as `x/L_osc`
rises, 11.3% → 7.7%, and the steady error rises toward the inlet, 34.0% →
39.9%. Across alpha, the run with a quarter of the development length
available is **2.8× worse** on the harmonic (21.3% vs 7.7%) at an
identical Reynolds number, identical mesh and identical station — while
its steady-part error is unchanged at 34.7%, exactly as it should be,
since the steady entrance length does not depend on alpha at all. **Both
predicted signs, plus a control that correctly does not move.** The
entrance-length explanation is confirmed, not merely consistent.

**What this does to Gate 2.** Gate 2 stays FAIL as posed — the total
profile does not match the total analytic profile, and no reading of this
data makes it. But the failure is now **localised and attributed**: the
solved oscillatory response, the part that is actually about the unsteady
solver, agrees with the closed-form Womersley solution to 7.7% at the best
station available, and the residual scales the way incomplete development
requires. **The one comparison against exact theory this case can support
now has a number attached instead of a verdict.** The 7.7% is an upper
bound on the solver's own error, not an estimate of it: the exact solution
assumes a fully developed base flow which this domain does not provide, so
part of that 7.7% is the same domain limitation leaking into the harmonic.

### 9.4 The discharge coefficients are withdrawn

§6 and §6b report "the CFD's independently measured discharge coefficient
(1.91–1.95)" and build the ROM root-cause on it. Three independent things
are wrong with that number and each is now measured.

**(1) The definition omits the velocity-of-approach factor.** The record
used `Cd = Q/(A_o sqrt(2 dp/rho))`, which is the coefficient of the ROM's
own formula and assumes the approach velocity is zero. ISO 5167's
coefficient carries `E = 1/sqrt(1−beta^4)` explicitly. At beta = 0.906,
E = 1.753 — the single largest term in the comparison, and the one that
diverges as the valve opens.

**(2) The measured `dp` is not a loss.** The upstream and throat probes
sit on the same centreline streamline. Their total heads `p + u²/2`:

(all tail-window time-weighted means, not single timesteps)

| case | measured dp (Pa) | head loss between the taps (Pa) | as a fraction of dp |
| --- | --- | --- | --- |
| `steady_q25` | 19.56 | −0.067 | −0.341% |
| `steady_q50` | 74.61 | −0.044 | −0.060% |
| `steady_q75` | 168.25 | +0.023 | +0.014% |
| `steady_q100` | 301.94 | +0.141 | +0.047% |
| `steady_beta_50deg` | 1499.61 | +4.494 | +0.300% |
| `steady_beta_55deg` | 908.99 | +1.936 | +0.213% |

**99.7% or more of every `dp` this study has published from the throat tap
is reversible acceleration.** A discharge coefficient is fitted
to a loss. There is no loss here to fit one to. (The loss is real and it
is downstream, in the vena contracta and the jet — which is the signal
§9.2 just showed is not converged.)

**(3) The tap is not an ISO tapping.** ISO 5167-2 specifies corner, D and
D/2, or flange wall tappings. This is a centreline probe at the plate
mid-plane, inside the contraction.

Re-derived on the same measurements with the approach factor put back:

| case | beta | E | Cd as published | C ISO-style | dp measured | inviscid Bernoulli dp |
| --- | --- | --- | --- | --- | --- | --- |
| `steady_beta_50deg` | 0.766 | 1.235 | 1.219 | **0.987** | 1499.6 Pa | 1461.4 Pa |
| `steady_beta_55deg` | 0.819 | 1.349 | 1.370 | **1.015** | 909.0 Pa | 937.2 Pa |
| `steady_q100` | 0.906 | 1.753 | 1.941 | **1.107** | 301.9 Pa | 370.1 Pa |

All three land within 12% of unity, which is the arithmetic restatement of
the total-head result: the measurement is inviscid Bernoulli, and the
residual scatter about 1.0 is the centreline-versus-section-mean bias plus
discretization (§9.6), not a discharge coefficient. **§6b's claim that
"the CFD's independently measured discharge coefficient confirms the real
coefficient at this opening is over 3× the ROM's assumed value" does not
survive. It is withdrawn.** F9 has never measured a discharge coefficient.

### 9.5 What the −94% is actually made of, and the defect it exposes

The −94.0% deviation itself stands: 110.71 Pa measured against 1849.77 Pa
computed. Its attribution does not. Stacking the three effects in order,
each independently checkable:

| step | value | share of the 94 points |
| --- | --- | --- |
| ROM as published (systolic stroke-volume weighting of a half-sine) | 1849.77 Pa | — |
| same formula, averaged over the CFD's own sinusoidal cycle | 1109.86 Pa | **−40.0** |
| plus the velocity-of-approach factor the formula omits | 361.05 Pa | **−40.5** |
| plus replacing Cd = 0.62 by the 1.12 the measurement implies (= the CFD number) | 110.71 Pa | **−13.5** |

The first step is not a ROM error at all: the ROM's "cycle-weighted loss"
is a stroke-volume-weighted average over **systole only**, while the CFD
number is a time mean over a **full sinusoidal cycle**, and for a
quadratic loss law those differ by the ratio of mean-square flows,
0.625 Q_peak² against 0.375 Q_peak². **80.5 of the 94 points come from a
definition mismatch and an omitted algebraic term, not from the discharge
coefficient the record blamed for all of it.** And the remaining 13.5
points are not really a discharge coefficient either: the implied 1.12 is
§9.4's finding restated as arithmetic, the measured differential being
inviscid Bernoulli to within the centreline-versus-section-mean bias. **No
step in this decomposition is a measurement of a loss.**

**The defect that matters for the mega-batch is simpler than beta ranges
and does not need any of the above.** `dp = 0.5 rho (Q/(Cd A))²` contains
no pipe area, so it has no beta → 1 limit: as the leaflets open, the
geometry becomes an unobstructed pipe and an *orifice* loss must vanish,
because there is no orifice. The ROM instead tends to a finite floor.

| opening | beta | area / A_pipe | ROM cycle-weighted | Poiseuille friction over the same 0.3013 m | ratio |
| --- | --- | --- | --- | --- | --- |
| 65° | 0.906 | 0.821 | 1849.8 Pa | 57.5 Pa | 32.1 |
| 80° | 0.985 | 0.970 | 1326.8 Pa | 57.5 Pa | 23.1 |
| 87.5° (the act's winner) | 0.999 | 0.998 | 1252.8 Pa | 57.5 Pa | **21.8** |
| 90° (leaflets flat on the wall, full bore) | 1.000 | 1.000 | **1248.0 Pa** | 57.5 Pa | 21.7 |

At 90° the geometry is a straight pipe and the only loss it has is wall
friction, 57.5 Pa cycle-weighted. The ROM reports **1248 Pa**. The ratio
never falls below ~22 anywhere in the sweep and the curve flattens onto
that floor exactly where the optimiser is driving. **The reduced-order
family's ranking is safe and its magnitude at the winning design is wrong
by a factor of order 20, and that second conclusion needs no CFD at all.**

On the ranking, state the strength of the evidence exactly. F9's three
solved angles give throat differentials of 1499.6, 909.0 and 301.9 Pa at
50°, 55° and 65° at `Q_peak` — monotone in the same direction as the ROM.
That is *consistent with* the ROM's ordering, not a measurement of it:
§9.4 established that this differential is a reversible acceleration, not
a loss, and F9 has no converged loss to order (§9.2). The ordering claim
rests on the physical argument that within one geometry family a narrower
orifice at fixed flow means a faster throat jet and therefore a larger
loss, with the CFD supplying the matching monotone acceleration. It is a
sound argument and it is not the same thing as data.

### 9.6 Discretization: how much of any of this is mesh and timestep

**Timestep.** `F9_work/physio_dt_half` re-solves `pulsatile_physio`'s final
cycle from the `t=1.8` checkpoint with `maxCo` halved to 0.45 on the same
mesh. Cycle-mean dp changes by **1.8e-5**, cycle peak by 7.8e-4, and the
phase-aligned waveform by 1.4e-3 of the cycle band. **The reported cycle
mean is temporally converged**, and the criterion threshold in §9.1 is
therefore not masking a timestep error.

**Grid.**

Four levels of the `steady_q100` reference point, same geometry, same
boundary conditions, same probe stations, block counts scaled uniformly.
`maxCo` is held at 0.9 throughout, so the timestep refines with the mesh;
the timestep result above says that part contributes nothing.

| level | blocks | cells | h relative | dp upstream→throat | F9-STAT-1 | wall clock |
| --- | --- | --- | --- | --- | --- | --- |
| coarse | 30/3/45 × 12/4 | 1,236 | 2 | 236.88 Pa | STATIONARY | 24.8 s |
| base (all F9 results to date) | 60/6/90 × 24/8 | 4,944 | 1 | **301.94 Pa** | STATIONARY | 480.8 s |
| med | 90/9/135 × 36/12 | 11,124 | 2/3 | 332.64 Pa | STATIONARY | 1963.5 s |
| fine | 120/12/180 × 48/16 | 19,776 | 1/2 | 338.92 Pa | STATIONARY | 3008.4 s |

The fine level was **stopped at t = 0.4284 s instead of its requested
1.2 s**, and that is admitted under a stated rule rather than by eye: it is
accepted only because (a) it passes F9-STAT-1 on its own tail window with a
band of 1.1e-6, and (b) every level that *did* run to 1.2 s was already
within **1.0e-3** of its final value by t = 0.4284 (coarse 2.6e-6, base
1.0e-3, med 3.6e-7). `f9_criteria.py` applies both conditions and downgrades
the level to `RUN INCOMPLETE` if either fails. It was stopped because its
Courant-limited timestep came out about 5× smaller than the base mesh's, not
the 2× a uniform refinement suggests, putting the full run at roughly 2.5
hours on one core with several other agents on the box.

**The observed order of convergence is not consistent across triplets, so
this solution is not in the asymptotic range.** That is the result, and it
took fixing a bug in my own first pass to see it: the familiar
`p = ln|e32/e21| / ln(r)` is only valid when the two refinement ratios are
equal, which they are not for (coarse, base, med). Solving the correct
transcendental relation instead:

| triplet | r32, r21 | observed p | Richardson f_ext | GCI on the finest level |
| --- | --- | --- | --- | --- |
| coarse, base, med | 2, 1.5 | **0.39** | 512.8 Pa | 67.7% |
| base, med, fine | 1.5, 1.333 | **3.47** | 342.6 Pa | 1.4% |
| **coarse, base, fine** (r = 2 throughout) | 2, 2 | **0.82** | **387.6 Pa** | **18.0%** |
| four-level least squares, `f(h) = f0 − C h^p` | — | **0.87** | **386.3 Pa** | (max residual 4.2 Pa) |

The sequence is monotone at every step, so nothing is diverging. But an
observed order that reads 0.39, 3.47 and 0.82 depending on which three of
the four levels you pick is the signature of a sequence not yet described
by a single power of `h`. The two estimates entitled to most weight agree
closely with each other and disagree with the other two: the **constant-ratio
triplet** (r = 2 throughout, the configuration the index was actually
derived for) gives p = 0.82 and 387.6 Pa, and the **four-level fit**, which
no single noisy level can dominate, gives p = 0.87 and 386.3 Pa. Take the
grid uncertainty as **of order 20%, not the 1.4% the flattering triplet
offers.**

**An observed order near 0.85 against schemes that are formally
second-order is itself worth recording.** The likely reason is geometric,
not numerical: the orifice plate has a sharp 90° salient edge at both
faces, where the inviscid velocity gradient is singular, and a corner
singularity caps the attainable order however good the scheme is. This is
offered as the leading explanation and it has not been tested here; the
test would be to round the edge slightly and see the order recover, which
also changes the physics being modelled and so is not a free experiment.

**What this means for every number F9 has published.** The base mesh, on
which all of §3 to §6b rests, gives 301.94 Pa where the four-level fit
extrapolates 386.3 Pa: the base mesh **under-predicts the throat
differential by about 22%**, and even the finest level is 12% low. That
error had never been quantified. Three consequences, in order:

1. **Gate 1 is unaffected.** It compares a pulsatile run against the steady
   map computed *on the same mesh*, so the discretization error is common
   to both sides and cancels almost entirely. The −1.58% and +0.203%
   deviations stand.
2. **Gate 3 survives its own discretization error with room to spare.**
   Scaling the pulsatile cycle mean by the same 1.28 factor gives roughly
   142 Pa against the ROM's 1849.77 Pa, a deviation of −92.3% instead of
   −94.0%. The conclusion does not depend on the mesh.
3. **The withdrawn discharge coefficients would not have been rescued by a
   finer mesh either.** A larger `dp` makes the ISO-style coefficient
   *smaller*, so the finest level moves 1.107 toward roughly 1.04, still
   pinned at the inviscid value rather than at anything like 0.6. §9.4's
   argument was never about resolution.

**A mechanism considered and set aside.** The obvious suspect for a
throat-tap sensitivity this large is probe placement: the tap sits at
`y = 1e-6`, so it reads the cell adjacent to the wedge axis, whose centroid
moves from 0.45 mm to 0.11 mm off-axis across these four meshes. It does
not survive arithmetic. Symmetry forces `du/dr = 0` on the axis, so the
sampling error goes as `(r/R_bore)²`, which is 5e-4 at the base mesh and
1e-4 at the fine one, four orders of magnitude too small to move the
reading 22%. The upstream rake says the same from the other side: at fixed
radii away from the axis it changes by only 0.26% between the coarse and
base meshes while the throat tap changes by 27.5%. The sensitivity is
genuine under-resolution of the contraction into the bore, localised where
the flow is accelerating hardest and next to the singular corner, not an
artefact of where the probe sits.

### 9.7 What this case is graded against — the ledger, stated plainly

The lab distinguishes verification (against exact theory or a refined
solution of the same equations, no experiment involved) from validation
(against measurement). §7 currently reads as if F9 were a gated family
ready for promotion. Here is the whole of what it actually has.

**Verification — what F9 does have:**

| claim | against | result |
| --- | --- | --- |
| unsteady oscillatory response | Womersley (1955) exact solution, first harmonic | **7.7%** amplitude, 4° phase, at the one station with enough development length; residual scales with `x/L_osc` and with alpha as predicted (§9.3) |
| steady velocity profile | Hagen-Poiseuille exact solution | **not gradeable on this domain** (entrance length 210D vs 5D; 34% error is the domain, not the solver) |
| temporal discretization | maxCo halved, same mesh | **1.8e-5** on the cycle mean (§9.6) |
| spatial discretization | four-level grid refinement of the steady reference point | **~20%** on the throat differential; observed order ~0.85 against formally second-order schemes, and NOT in the asymptotic range (§9.6) |
| periodicity | criterion F9-CYC-1 | **8.5e-6** (physio), **3.6e-8** (low alpha) on the throat differential (§9.1) |
| stationarity of the reference map | criterion F9-STAT-1 | pass on the throat differential, **fail on the downstream differential** (§9.2) |
| internal consistency, unsteady against quasi-steady | the case's own steady map | −1.58% (alpha 16.73), +0.203% (alpha 8.36) (§4, updated §9.1) |

**Validation — what F9 does not have:**

| candidate reference | why it is not usable here |
| --- | --- |
| ISO 5167 discharge-coefficient correlation | beta is 0.766–0.906 in every solved case, outside the calibrated [0.20, 0.75]; the tap is not an ISO tapping; and the measured differential is 99.7–100% reversible, so no coefficient can be fitted to it (§9.4) |
| ISO 5167 permanent pressure loss | the only signal that carries the loss (upstream→downstream) fails stationarity at the three highest-loading points, and the tap sits inside the jet-redevelopment region (§9.2) |
| published in-vitro heart-valve pressure-loss data | not attempted, and not defensible as posed: this is an axisymmetric orifice of matching effective area, not a valve, run laminar at a peak pipe Re of 8388 where real valve flow is transitional to turbulent (§2) |

**So: F9 is verified in part and validated against nothing.** Every gate
in §3 to §6b is verification or internal consistency. That is a
respectable position for a screening replacement and it is not the same
sentence as "a real, gated family", and the record should not let a reader
slide between them.

### 9.8 What changed in the control-room act

The valve act (`sdk/workflows/valve_study.py`, "Find the valve opening
angle that minimizes pressure loss over the cardiac cycle") stated nothing
this record contradicts on the **ranking** — "the ranking is trustworthy,
a solved internal flow would set the magnitude" was already the honest
line, and §9.5's three solved angles are consistent with it. But its
uncertainty channels carried a model-form band of ±98.9 Pa built from the spread
between published discharge-coefficient correlations (C = 0.60 to 0.65) on
a headline of 1253 ± 417 Pa (95%), which implies the magnitude is pinned
to about ±8% at a design where §9.5 says it is wrong by a factor of order
20. A band measuring the spread **between** correlations cannot cover the
correlation family being outside its own calibrated range.

Changed, without altering a single computed number (so the certificate and
the stored UQ study stay valid):

- `BETA_CALIBRATED_MAX = 0.75` and `_beta(angle) = sin(theta)` added, with
  the F9 evidence in the comment block.
- The Chief Researcher's conclusion beat now opens with the ceiling:
  "Orifice ratio 1.00 at the winning opening, above the 0.75 ceiling this
  correlation is calibrated to. Above that ceiling the magnitude is not
  bounded by the reported band."
- The same statement is appended to the model-form channel note and to the
  report's uncertainty list, so it survives into the certificate page and
  the saved transcript, not just the on-camera prose.
- `docs/DEMO_RUNBOOK.md`'s Act 3 beats were stale from an earlier sweep
  change (4 angles, winner 80° at 1327 ± 421 Pa) and now match the act as
  it runs (13 angles, winner 87.5° at 1253 ± 417 Pa) plus the new ceiling
  line.

`sdk/tests/test_valve.py` passes unchanged (24 tests), including the
house-style and channel-note-register checks.

### 9.9 Cost of this round

All single core, no MPI, `ExecutionTime` from each run's own
`solve_registry` log.

| run | purpose | wall clock |
| --- | --- | --- |
| `lowalpha_ext` | 3 complete cycles at alpha=8.36, so F9-CYC-1 is testable at all (§9.1) | 829.9 s |
| `physio_dt_half` | timestep sensitivity, maxCo 0.45 (§9.6) | 413.0 s |
| `mesh_coarse_q100` | grid level h=2 | 24.8 s |
| `mesh_med_q100` | grid level h=2/3 | 1963.5 s |
| `mesh_fine_q100` | grid level h=1/2, stopped at t=0.4284 under the rule in §9.6 | 3008.4 s |
| `pulsatile_fine` | **launched and cancelled**, see below | 364.2 s |
| **round 3 subtotal** | | **6603.8 s, ~110.1 min (~1.83 core-hours)** |
| rounds 1 and 2 (§7) | | 4853.1 s, ~80.9 min |
| **grand total, all F9 compute** | | **11456.9 s, ~191.0 min (~3.18 core-hours)** |

Everything in §9.1 through §9.5 except the two extension runs is
**zero-compute**: the criteria, the harmonic decomposition, the total-head
check, the discharge-coefficient audit and the whole ROM analysis read
probe files that were already on disk. The most consequential finding of
the round, that the reduced-order law has no beta → 1 limit (§9.5), cost
nothing at all.

**One cancelled run, recorded rather than dropped.** `pulsatile_fine` would
have re-solved `pulsatile_physio` on the fine mesh for a direct grid
sensitivity on the headline cycle mean. It was killed after 364.2 s once
its measured rate put it at roughly 5 hours: the fine mesh's Courant-limited
timestep came out about 5× smaller than the base mesh's, not the 2× a
uniform refinement suggests, and the same information is available from the
steady grid study plus Gate 1's same-mesh quasi-steady agreement at a
twentieth of the cost. Its partial case directory was deleted so it cannot
be mistaken for a result; its launch log survives in `solve_registry`.

### 9.10 Still open

1. **A converged permanent loss.** The quantity a valve is judged on
   cannot be measured on this mesh (§9.2). Needs the downstream tap moved
   beyond jet redevelopment (order 8–10D) with domain to match, and a mean
   phase-averaged over an integer number of shedding periods. Until then
   the field is retained in `F9_pulsatile_valve.json` but flagged under a
   new top-level `retracted_fields` key (rather than deleted, so a reader
   holding an older copy of the JSON can find out why the number they have
   is gone), and it must not be quoted.
2. **No validation of any kind exists** (§9.7). The cheapest real one is
   an ISO 5167 point *inside* the calibrated range: re-run the steady map
   at an opening angle giving beta ≤ 0.75 (about 48.6° gives beta = 0.75)
   with ISO D and D/2 wall tappings added, and compare against the
   Reader-Harris/Gallagher correlation where it is entitled to be believed.
   That is the single experiment that would tell us whether the ROM is
   trustworthy inside its own range — the question §6b correctly flagged
   and nobody has answered.
3. **The `pulsatile_physio` permanent-loss signal fails F9-CYC-1 at
   1.39e-3** (§9.1(b)). Superseded by item 1 if the tap moves.
4. **The laminar/axisymmetric idealization is untested against anything.**
   Peak pipe Re is 8388 and the mesh cannot represent a non-axisymmetric
   instability at any resolution. The ring-vortex shedding found in §9.2 is
   the axisymmetric shadow of a three-dimensional process.
