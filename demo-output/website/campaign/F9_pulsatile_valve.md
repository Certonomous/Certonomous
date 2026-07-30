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
- **Tooling**: every launch through `scripts/case_preflight.sh` +
  `scripts/launch_solve.sh`, per project standing rule.

## 3. Staged results

### FEASIBILITY — PASS
Mesh builds clean; `pimpleFoam` runs stably; smoke test to t=0.01 s
completed without incident (~0.085 s/timestep on this ~5k-cell mesh,
single core). No `residualControl`-references-untransported-field trap:
the case carries no turbulence fields to reference (laminar).

### PHYSICS — PASS (corrected 2026-07-29 ~23:00 UTC; the record below was stale, not the run)

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
