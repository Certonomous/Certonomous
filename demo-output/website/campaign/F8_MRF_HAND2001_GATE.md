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

## 2. The reference, fetched — and a citation correction (2026-08-07)

**The docket's citation conflated two reports.** Fetched and read in full text:

- **NREL/TP-500-29494** is Simms, Schreck, Hand & Fingersh (2001), *NREL
  Unsteady Aerodynamics Experiment in the NASA-Ames Wind Tunnel: A Comparison
  of Predictions to Measurements* (June 2001) — the blind-comparison report.
  Its low-speed-shaft torque appears **only as Figure 8 curves** (upwind, 0°
  yaw, 7–25 m/s); the data points are graphics, not extractable text. Its own
  text at 7 m/s: "Turbine power predictions ranged from 25% to 175% of
  measured."
- **NREL/TP-500-29955** is Hand, Simms, Fingersh, Jager, Cotrell, Schreck &
  Larwood (2001), *Unsteady Aerodynamics Experiment Phase VI: Wind Tunnel Test
  Configurations and Available Data Campaigns* (December 2001) — the report
  the docket's title and author list actually name. Fetched and read: it
  documents Sequence S (Table C-18: upwind, no probes, tip pitch 3°, 72 RPM,
  5–25 m/s in 1 m/s steps including 7.0 m/s at 0° yaw — **exactly the
  condition the case on disk is set at**) and defines the LSSTQ channel and
  its gravity correction (LSSTQCOR = LSSTQ + 252.82·cos(B3AZI − 177.35) for
  the upwind turbine), but **publishes no mean-torque-vs-wind-speed table**;
  the measurements live in the campaign data files.

So neither primary report publishes a tabulated 7 m/s torque, and the numeric
value must come from the validation literature at a stated provenance tier:

- **Q_ref = 800 N·m** — secondary tier (digitised from the Hand et al. 2001
  data by a validation paper): *Processes* 12(9):1994 (2024), Table 6,
  "experimental torque, 7 m/s: 800 N·m" (also 8 m/s: 1100, 9 m/s: 1390,
  10 m/s: 1340 N·m), attributed to Hand et al. 2001.
- Corroboration: *Fluids* 8(7):201 (2023) computes 827 N·m at 7 m/s and
  describes it as matching the NREL measurement closely (Figure 5);
  TP-29494's "25% to 175% of measured" spread at 7 m/s is consistent with a
  measured value of this order; and 800 N·m × 7.5398 rad/s = 6.03 kW, the
  ~6 kW aerodynamic power this turbine is known to produce at 7 m/s.

The pre-declared cap is therefore **50% × 800 N·m = 400 N·m peak-to-peak**.

## 3. The gate, read against the pre-registration

Window t = 2000–3000, 21 samples (writeInterval 50), both segments of the
existing history concatenated:

| quantity | value |
| --- | --- |
| window mean Mx | **−1037.1 N·m** (|mean| = 1037.1) |
| window peak-to-peak spread | **7678.7 N·m** (min −7725.2, max −46.5) |
| spread as % of Q_ref | **959.8%** — 19.2× the pre-declared 50% cap |
| S12 relative drift | −0.854 (≥ 1e-3) |
| S12 monotone fraction | 0.500 (< 0.90 — S12 itself does not fire; the signal oscillates rather than travels) |
| |mean| vs Q_ref | +29.6% — **void**, not a measurement, per the cap |

**VERDICT: NO VERDICT — and that is the result.** The published value lies
numerically inside the measured band only because the band is enormous; the
band is 19 times wider than the pre-declared maximum, so the window mean of
this history is not a measurement of anything. Per the monitor standard's
L-24 (a run is not converged, a quantity is) and the hump lesson, unconverged
forces are not gateable: steady MRF as this case is built **cannot gate the
F8 family**, and the MRF branch closes on evidence rather than staying open.
The prediction carried from the proposal (mean within the oscillation
half-width of the published torque) is scored **not evaluable** — its named
risk, that a series which never settled has no meaningful mean, is what
happened.

## 4. The confirmation restart the budget priced — and the mechanism it found

The proposal's 6 core-min priced "one short confirmation restart." Before
spending it, one zero-cost observation set its direction: **the window-mean
torque is negative about the rotation axis while omega is positive.** A wind
turbine extracting power carries its aerodynamic torque in the direction of
rotation (TP-29955's own sign convention: LSSTQ positive "because of a force
in the direction of rotation"). A rotor whose mean aero torque opposes its
rotation is being motored, not driven — the case as built never operated as a
turbine.

Test run (`phase6_mrf_omegaflip/`, evidence retained): identical mesh,
numerics and BCs, `MRFProperties omega` flipped to −7.5398 rad/s, fresh start,
600 iterations, 4 ranks, 87 s wall = **5.8 core-min** (budget 6).

| | original (+omega), t=300–600 | flipped (−omega), t=300–600 |
| --- | --- | --- |
| mean Mx | −1465.9 N·m | +450.2 N·m |
| peak-to-peak | 2831.6 N·m | **132.8 N·m — 21× calmer** |
| character | wild oscillation from the first sample | smooth monotone decline (761.8 → 365.5), unsettled — S12 would fire |

The reversed-rotation history is 21 times calmer over the identical window on
the identical mesh. That is a mechanism-grade signal that the violent
non-convergence of the original run is physics of a rotor spun against its
blade geometry (massively separated, unsteady), not a numerics defect of the
mesh or schemes. What the flip run does NOT yet establish: its torque was
still travelling monotonically at t=600, and its sign (+Mx against −x
rotation) still reads as motoring, so either it has not yet found its settled
sign or the geometry/convention question below is still open. No settled
value is claimed from it.

## 5. Deliverable: the convergence-fix diagnosis plan

In cost order:

1. **Zero compute — rotation-direction audit.** Establish from the blade STL
   itself (S809 camber orientation, twist sign) which rotation direction this
   geometry is built for, and compare against the DAFoam
   `NREL6_Wind_Turbine` tutorial this case's MRFProperties says it derives
   from (axis, omega sign, and STL handedness together). The original case's
   +7.5398 about +x with inflow +x is now the prime suspect; the flip test
   moved the history by 21× in width, which is what a wrong-direction fix
   would do.
2. **~13 core-min — settle the flipped case.** Extend `phase6_mrf_omegaflip`
   to t≈2000 (measured rate 0.145 core-s/iteration at 4 ranks). Gate its
   torque under the same pre-registration discipline: window, 400 N·m cap,
   S12 drift test declared before reading. If it settles near ±800 N·m with
   the driving sign, F8 has its first gateable number and the Hand et al.
   comparison is back on. If it settles motoring-signed, the STL orientation
   (item 1) is the remaining variable and must be resolved first.
3. **Only then** re-run the +omega configuration if item 1 exonerates the
   original direction — with relaxation/pseudo-transient treatment, because
   a correctly-configured rotor that still oscillates ±3800 N·m is a
   genuinely unsteady flow and belongs to the transient branch the product
   list already names ("MRF first, then transient").

## 6. Cost

| item | core-min |
| --- | --- |
| gate (read existing history, fetch reference) | 0 |
| omega-flip confirmation run (600 iters, 4 ranks, 87 s) | 5.8 |
| **total, vs 6 approved** | **5.8** |
