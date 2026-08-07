# F8 — gating the existing MRF blade forces against Hand et al. 2001

Proposal: `f8-mrf-forces-against-hand-2001` (approved under Katie's blanket
approval 2026-08-05, slate rank 1, rank_value 0.500). Case on disk:
`F8_runs/phase6_mrf/` — UAE Phase VI Sequence S, 230,135 cells, checkMesh OK,
`simpleFoam` + whole-domain MRF at omega = 7.5398 rad/s (72 RPM) about +x,
inlet 7 m/s, run to t=1500 (2026-07-29) and restarted to t=3000 (2026-07-30),
`SIMPLE solution converged` appearing zero times in either log.

## 1. Pre-registration (written 2026-08-07, BEFORE the force history was read)

**What has and has not been seen at the time of writing.** The slate and the
campaign status already quote coarse envelope numbers for this history (Fx
span 508 N over t=1500–2250 and 729 N over t=2250–3000; Fy swinging −775 to
+1276 N; "force still oscillating ±30% at t=1500") and those numbers are in
this agent's context. Additionally, reading the `moment.dat` header to learn
its column format exposed four data rows at t=50–200 (startup transient,
Mx ≈ −500 to −3800 N·m), which sit far outside any plausible averaging
window. No other force or moment value has been read, no window statistic has
been computed, and the Hand et al. 2001 torque value has not yet been fetched.

**Torque conversion, declared in advance.** The `bladeForces` function object
writes the moment exerted by the fluid on the `blade` patch about
CofR = (0 0 0), which lies on the rotation axis (1 0 0). The blade STL spans
z = −5.029 to +5.029 m: **both blades are in the one patch**, so no
blade-count multiplier applies, and no radius factor applies because the
function object integrates r × dF itself. `rhoInf = 1.225 kg/m³` is already
applied, so the output is dimensional N·m. Therefore:

    Q_LSS(t) = total_x column of postProcessing/bladeForces/*/moment.dat

The comparison is |window-mean of Q_LSS| against the published low-speed-shaft
torque magnitude; the raw sign will be reported alongside, with the convention
stated (omega is +x; a wind turbine's aerodynamic driving torque acts in the
direction of rotation).

**Averaging window, declared in advance:** t = 2000 to 3000 inclusive — the
final 1000 iterations, entirely inside the restarted segment, discarding 500
iterations after the t=1500 restart as restart transient.

**Maximum band width, declared in advance:** the measured band is the
peak-to-peak spread of Q_LSS over the declared window. If that spread exceeds
**50% of the published torque** (i.e. a half-width of ±25%), the verdict is
**NO VERDICT** — reported as such and not as a fail — because a mean with a
half-width wider than the entire deviation range this comparison exists to
resolve (steady-MRF bias on this case is interesting at the 10–20% level) is
not a measurement of anything. This operationalises the monitor standard's
L-24 ("a run is not converged, a quantity is") for a quantity that never
printed a convergence sentence.

**Settledness check, declared in advance (monitor standard S12):** over the
declared window, the relative drift (mean of the window's second half minus
mean of its first half, over the window's mean magnitude) and the monotone
fraction will both be reported. If relative drift ≥ 1e-3 AND monotone
fraction ≥ 0.90, the quantity was still travelling when the run stopped and
the verdict is NO VERDICT (unsettled) regardless of band width.

**Gate:** PASS if the published value lies inside [mean − spread/2,
mean + spread/2] AND the spread ≤ 50% of the published value. FAIL, reported
as a result, if the published value lies outside that band and the spread is
within the cap. NO VERDICT if either the width cap or the S12 drift test
trips.

**Prediction (carried from the proposal, still before the data):** the window
mean lands within the oscillation half-width of the published torque; the
named risk is the opposite — that the series has no meaningful mean, in which
case NO VERDICT is the honest outcome and the deliverable becomes a
convergence-fix diagnosis plan.

**Reference to fetch:** Hand, Simms, Fingersh, Jager, Cotrell, Schreck,
Larwood (2001), *Unsteady Aerodynamics Experiment Phase VI*, NREL/TP-500-29494
— low-speed-shaft torque at the 7 m/s Sequence S point. If the tabulated value
cannot be reached, the item stops and reports BLOCKED at 0 core-min; a
secondary source may be used only with its provenance tier stated.
