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

1. **Zero compute — rotation-direction audit.** *EXECUTED 2026-08-07, see
   §10: the geometry is exonerated — chord, twist distribution, handedness
   and camber all match TP-500-29955 for the original +x rotation, and the
   defect hunt moves to the §10 BC/frame list, led by the missing
   potentialFoam initialisation.* (Original text: establish from the blade
   STL itself which rotation direction this geometry is built for; the
   original +7.5398 about +x was then the prime suspect.)
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

## 7. Step 2 of the diagnosis plan — pre-registration (2026-08-07, before launch)

Authorised by the supervisor under the blanket approval as a rider on this
item: settle the flipped-omega case. **Written before the extension is
launched; the only flip-case data in context is the t=50–600 history already
recorded in §4** (12 samples, +761.8 declining monotonically to +365.5).

**Run:** restart `phase6_mrf_omegaflip` from its latest written fields
(t=500 — the t=600 stop wrote no fields because 600 is not a writeInterval
multiple, the known endTime trap; noted so the restart provenance is clean),
`endTime` 2000, `startFrom latestTime`, everything else untouched. 4 MPI
ranks — the F8 case's own convention from every prior run of this mesh (the
2-rank convention belongs to the B-52 family, not this one). Predicted cost:
1500 iterations at the measured 0.145 s/iter wall ≈ 218 s × 4 ranks ≈
**14.5 core-min**.

**Averaging window, declared now:** t = 1500–2000 inclusive (final 500
iterations, 11 samples at writeInterval 50).

**Settle gate, declared now (monitor-standard S12):** over the window,
relative drift = (mean of second half − mean of first half)/|window mean|,
monotone fraction = largest directional fraction of successive steps.
UNSETTLED if relative drift ≥ 1e-3 AND monotone fraction ≥ 0.90. Also
gateability cap, same convention as §1: window peak-to-peak spread must be
≤ 50% of the 800 N·m reference (≤ 400 N·m).

**Torque gate, declared now:** if settled and within the cap — PASS if
800 N·m lies inside [|mean| − p2p/2, |mean| + p2p/2]; FAIL, reported as a
result, if outside; NO VERDICT if the cap or S12 trips. Q_ref = 800 N·m,
secondary tier per §2, unchanged.

**Sign rule, declared now:** rotation is −x (omega = −7.5398), so a
power-extracting turbine carries mean aero torque Mx < 0 (parallel to
omega). The raw sign is reported. **If the window mean settles positive
(anti-parallel — motoring), the configuration is still not a turbine and no
MRF milestone is claimed regardless of magnitude agreement**; the step-1
STL-orientation audit then becomes the blocker and the verdict is recorded
as "settled, wrong sign". A milestone claim requires settled + cap met +
turbine sign + 800 N·m inside the band.

**Prediction, weak and stated as such:** at t=600 the history was still
falling at ≈0.55 N·m/iter with no visible deceleration; if that continues it
crosses zero near t≈1265 and reads turbine-signed by t=2000. Predicted: the
window lands turbine-signed (Mx < 0). Named risks, either reported as
written: (a) it decays to a positive (motoring) plateau — then step 1 is the
blocker; (b) it is still travelling at t=2000 — then S12 fires, the verdict
is NO VERDICT (unsettled), and the steady-MRF branch is closed a second time
on evidence, making the transient branch the filed next step.

*Nothing below this line existed when the restart was launched.*

## 8. Step 2 result: it settles, and it settles wrong-signed — no milestone

Restart resumed genuinely (first new log line `Time = 501`), ran to t=2000,
203.8 s × 4 ranks = **13.6 core-min** (predicted 14.5). Still zero
"SIMPLE solution converged". Read against §7, clause by clause:

| pre-registered test | measured | verdict |
| --- | --- | --- |
| S12 unsettled (drift ≥ 1e-3 AND mono ≥ 0.90) | drift −0.164, mono fraction 0.700 | does NOT fire |
| cap: window p2p ≤ 400 N·m | **143.2 N·m** (17.9% of Q_ref) | within |
| sign (turbine = Mx < 0 for −x rotation) | window mean **+138.0 N·m** | **MOTORING — wrong sign** |
| 800 N·m inside [|m|−p2p/2, |m|+p2p/2] | band [66.5, 209.6] | outside, −82.7% |

**Verdict: settled by the declared rule, wrong sign — NO MILESTONE**, exactly
the outcome the §7 sign rule refused to dress up. The prediction (turbine-
signed by t=2000) scored **FALSE**; named risk (a) is what happened: the
decline from +761.8 decayed onto a positive plateau wobbling around
+100–230 N·m instead of crossing zero. One honesty note recorded against our
own rule: the S12 clause requires drift AND monotone travel, and this window
wobbles with a −16% halves-drift, so "settled" here means "not travelling
monotonically", not "flat"; the p2p cap is what carries the gateability
finding, and it passes.

**What this means for the diagnosis, and why it sharpens step 1 rather than
opening the transient branch:** the case has now been run in both rotation
directions on the same mesh. With +omega it oscillates violently around
−1000 N·m (opposing rotation); with −omega it settles calmly at +138 N·m
(opposing rotation again). **Neither direction extracts power.** A geometry
that motors both ways at |λ| = 5.4 with a torque magnitude 6× below the
measurement is a blade at the wrong pitch/twist orientation (mirrored STL,
mis-set tip pitch, or an inflow/axis inconsistency) — a configuration
defect, not a numerics one and not yet a frozen-rotor limitation. The
steady-MRF branch therefore stays closed for gating (twice over: the
original history is ungateable at 960% of the cap, and the calmed flipped
history gates FAIL-by-configuration at −82.7%), and **the filed next step is
the §5 step-1 STL-orientation audit at zero compute — before any transient
core-minute is spent on a rotor that may be built wrong.** Running the
transient branch on an unaudited geometry would spend two orders of
magnitude more compute measuring the same defect.

## 9. Cost, final

| item | core-min |
| --- | --- |
| gate (existing history + reference fetch) | 0 |
| omega-flip confirmation (600 iters) | 5.8 |
| step-2 settle extension (1500 iters, rider approval) | 13.6 |
| step-1 STL-orientation audit (§10, second rider) | 0 |
| **total** | **19.4** (6 approved on the item + ~13 rider estimate; measured 19.4 vs 19 authorised) |

## 10. Step 1 executed: the geometry is EXONERATED, and it convicts the flip run instead (2026-08-07, zero compute)

The §5 step-1 audit was run entirely on the STL and existing outputs — no
solver launched. Sections were cut from `blade.stl` (330,950 triangles) at
r/R = 0.30, 0.63, 0.95 on both blades and measured against Hand et al.
TP-500-29955 Table A-1 (chord/twist, twist axis 30% chord, S809 root to tip,
Sequence S tip pitch 3°).

**(1) Chord and twist:**

| r/R | chord measured | chord published | geometric angle vs rotor plane, measured | published twist + 3° pitch |
| --- | --- | --- | --- | --- |
| 0.30 | 0.713 m | 0.711 m | +19.1° | 17.3° |
| 0.63 | 0.545 m | 0.542 m | +5.9° | 4.1° |
| 0.95 | 0.382 m | 0.381 m | +3.3° | 1.5° |

Chord matches to 2–3 mm at every station. The measured **twist distribution
matches exactly**: Δ(0.30R→0.95R) = 15.8° measured vs 15.76° published. The
uniform +1.8° offset at all three stations is the max-distance-chord
measurement bias on a cambered section (and/or ≤2° of pitch), not a twist
error — a constant offset cannot produce a motoring rotor.

**(2) Handedness:** blade− sections are blade+ sections mapped by
(x, y, z) → (x, −y, −z) — a **proper 180° rotation about the x axis**, not a
reflection. No STL mirror defect.

**(3) Orientation and camber:** for ω = +7.5398 (the ORIGINAL setting),
blade+ moves toward −y and the relative wind arrives from the −y/−x
quadrant. Measured blade+ LE at (−0.070, −0.202): pointing exactly there
(LE identified by thickness — 0.085 m at 8% chord vs 0.019 m at 92%). The
camber midline bulges toward +x (downwind) — suction side downwind, correct
for a turbine. With 1/3 axial induction the geometry meets the flow at
**AoA +3.2° / +5.2° / +4.1°** at the three stations — textbook attached
operation at the Sequence S 7 m/s point. Instrument sanity: the +omega run's
window-mean thrust is +811.5 N, positive and the right order against the
experiment's ~1.2 kN, so the forces object and axes read correctly.

**VERDICT: the geometry is built correctly for the original +x rotation.**
Which revises §8's inference, and the record says so plainly: "neither
direction extracts power" was the wrong reading. The −omega flip run was the
genuinely backwards configuration, and its calm +138 N·m IS the expected
drag torque of a rotor dragged backwards — the flip test measured a
correctly-built blade running in reverse, not a defect. The real anomaly is
the original +omega run: correct geometry at +4° attached-flow AoA should
drive at ≈+800 N·m, and instead the solution oscillates violently around
−1000 N·m (motoring). A correct geometry producing a stalled, oscillating,
torque-reversed field is a **flow-solution defect, not a configuration
defect**.

**Where the hunt moves (BC/frame terms, in cost order):**

1. **Impulsive start** — the prime suspect, and the family already owns the
   fix: `runSolve.sh` goes straight from uniform (7,0,0) into
   simpleFoam+MRF with no `potentialFoam -writephi` initialisation. F5b hit
   exactly this ("impulsive-start divergence, fixed by potentialFoam
   -writephi"), and the B-52 family runs potentialFoam before every solve.
   An impulsive MRF start sheds a massive starting vortex, stalls the
   blade, and a steady SIMPLE solve can limit-cycle in that stalled basin
   indefinitely — which reproduces every symptom on the record: torque
   opposing rotation (drag of a stalled rotor), plausible thrust, violent
   oscillation that more iterations never fix. Re-run +omega with
   potentialFoam init and reduced relaxation: ~14 core-min at the measured
   rate, to be filed/approved before running.
2. **MRF term audit against the derivation source** — the whole-domain
   `region0` zone with `nonRotatingPatches (sides inlet outlet)` follows
   the DAFoam NREL6 tutorial pattern; verify against that tutorial the
   omega sign convention, the nonRotatingPatches list, and that the
   cellZone genuinely covers every cell (topoSet log), before trusting the
   frame terms.
3. **Relaxation/scheme sensitivity** only if 1–2 exonerate themselves —
   and if a properly-initialised, properly-framed +omega solve still
   oscillates, that is finally the genuine unsteadiness the transient
   branch exists for, and the transient case inherits a quantified target:
   settle to within the §1 cap of 800 N·m.

## 11. §10 item 1 — pre-registration of the initialised +omega re-run (2026-08-07, before launch)

Authorised by the supervisor as the final rider. **Written before the case
directory exists.** One convention correction carried on the record: the
rider's brief phrased the prediction as "≈−800 N·m"; for THIS run the
rotation is the original ω = +7.5398 about +x, and power extraction means
torque parallel to omega, so **turbine-signed here is Mx > 0** — the −800
convention belonged to the flipped case in §7. The magnitude prediction is
unchanged.

**Case:** `phase6_mrf_pfinit`, copied from `phase6_mrf` (same mesh, same
+omega MRFProperties, same BCs), with exactly three declared changes:
(1) `potentialFoam -writephi` initialisation before the solve — the §10
prime-suspect fix, the F5b cure applied to this family for the first time;
(2) reduced relaxation, p 0.3 → 0.2, U 0.7 → 0.5, nuTilda 0.7 → 0.5;
(3) endTime 1500 from a fresh start (a writeInterval-250 multiple, so final
fields persist). **2 MPI ranks per the supervisor's instruction** — a
declared deviation from this case's own prior 4-rank runs, accepted because
decomposition perturbs a steady SIMPLE solve only at linear-solver
tolerance; core-min cost is rank-independent.

**Window, declared now:** t = 1000–1500 inclusive (11 samples at
writeInterval 50).

**Settle gate, declared now:** identical conventions to §7 — UNSETTLED if
relative drift ≥ 1e-3 AND monotone fraction ≥ 0.90 over the window;
gateability cap: window peak-to-peak ≤ 400 N·m (50% of Q_ref = 800 N·m,
secondary tier per §2).

**Quantified prediction (the diagnosis put at risk):** the solve settles
**turbine-signed, window mean Mx ∈ [+400, +1200] N·m** (800 ± the cap), with
p2p within the 400 N·m cap. MILESTONE requires all four: settled + cap met +
Mx > 0 + 800 N·m inside [mean − p2p/2, mean + p2p/2].

**FAIL branches, each a result:**
- (a) settles motoring-signed (Mx < 0) → the impulsive-start hypothesis is
  refuted as the sole cause; §10 item 2 (MRF term audit vs the DAFoam
  tutorial) is next.
- (b) settles turbine-signed but 800 N·m outside the band → F8 has a real,
  quantified bias to chase (model/BC investigation), and the MRF milestone
  is a bias statement rather than a pass.
- (c) will not settle (S12 fires or cap exceeded) → with initialisation and
  geometry both clean, the oscillation is genuine unsteadiness; the
  steady-MRF branch closes finally and the transient branch inherits the
  quantified target (settle within 400 N·m of 800).

**Predicted cost:** 1500 iterations at the measured ≈0.58 core-s/iteration ≈
**14.5 core-min** (wall ≈ 7.3 min at 2 ranks).

*Nothing below this line existed when the run was launched.*

## 12. §11 result: the run DIVERGED — no pre-registered branch fired, and the record says so rather than picking the nearest one

One mechanical addition was needed before the solver would start and is
recorded: `fvSolution` had no `Phi` solver entry, so potentialFoam could not
run; the `Phi { GAMG; DIC; 1e-6; 0.01 }` block and
`potentialFlow { nNonOrthogonalCorrectors 10; }` were copied from the B-52
family's own fvSolution (first attempt aborted at 0 solver cost; case
relaunched clean).

**Result:** potentialFoam converged in 2.2 s; simpleFoam ran all 1500
iterations without aborting, and the blade moment **diverged exponentially
from the first sample** — Mx = −1.5e4 at t=50, −1.5e8 at t=250, −1e27 at
t=850, −2.5e99 at t=1500. The window statistics are meaningless and are not
quoted as physics. The settle verdict is **FAILED RUN (numerical
divergence)** — which is none of §11's three branches: (a) and (b) require a
settled field and (c) described bounded oscillation, not exponential
blow-up. The prediction (turbine-signed, +400 to +1200 N·m) is scored **not
evaluable — the run it bet on did not produce a flow**.

**The monitor standard called this one:** at t=1500 the Ux residual reads
1.4e-8 — "converged" to any residual-only monitor — while p sits at 0.51 and
the force history is at 1e99, with 692 `bounding nuTilda` lines along the
way. That is S10, divergence behind a converged residual, detected here the
way S12/L-24 prescribe: from the quantity, not the residual block.

**What can and cannot be concluded, honestly:** §11 changed TWO things at
once (potentialFoam initialisation AND reduced relaxation), so this
divergence cannot be attributed to either alone — a confound of this
record's own making, named as such. The mechanism suspicion for the next
test: `potentialFoam -writephi` writes an **absolute** potential-flow flux,
and inside a whole-domain MRF zone simpleFoam expects the frame's relative
correction on the face flux — an initial phi missing the ω×r face
contribution is a large spurious mass source at iteration 1, and the F5b
cure this plan borrowed came from a non-rotating case. The impulsive-start
hypothesis for the original limit cycle is NOT refuted (this run never
tested it — it replaced one bad start with a worse one), and the §10 item-2
MRF term audit now rises in priority since flux/frame handling is implicated
twice.

**Filed next step (not run — the rider's budget is spent):** split the
confound at ~14 core-min per arm: (arm 1) potentialFoam init WITHOUT
`-writephi` (U/p only, let simpleFoam build its own MRF-consistent flux) at
the ORIGINAL relaxation; (arm 2) if arm 1 diverges too, original uniform
init at reduced relaxation. Either arm isolates one variable; both inherit
the §11 gate and prediction verbatim.

**Dated note (2026-08-08, chief-ordered per entry 3 of
`demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`, outcome block at
commit df755b49; evidence: the S10/S12 monitor-standard replay in
`demo-output/website/campaign/ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md` Task 3, commit
6d806733):** this section's claim that the run read "'converged' to any residual-only
monitor" **overstates**. The replay of the archived history with the standard's own detector
functions, verbatim, shows p sat at 0.51 — loudly unconverged — and detector **S6 does flag
the run** (residual stall on p and nuTilda against the case's declared `residualControl`
1e-4), so a residual-only monitor was not, in fact, uniformly satisfied. The true gap the
specimen exposes is narrower and worse: the flags that fire say only "unconverged" —
FLAG-class, same as a mild stall — and **no rule in the standard converts a
monitored-quantity magnitude explosion (Mx ~ 1e99 behind a 1e-8 momentum residual) into
FATAL**. That gap is exactly what the filed S10d amendment
(`agenda/proposals/s10d-monitored-quantity-magnitude-explosion.json`) addresses, with its
adoption evidence already attached (974 archived histories replayed: fires on exactly the 5
genuinely diverged runs, zero false positives); adoption is routed to the Infra family. The
original wording above stands unedited per the supersede-don't-delete convention.

## 14. §10 item 2 executed: the MRF flux/frame audit — three conventions verified correct, one concrete defect named, with source lines (2026-08-07, zero compute)

Read against the OpenFOAM v2606 sources installed on this box
(`/usr/lib/openfoam/openfoam2606/`).

**(1) Omega sign vs verified handedness — CONSISTENT.** `MRFProperties`:
omega +7.5398 about axis (1 0 0); §10 established the blade geometry is
built for +x rotation. No sign defect.

**(2) nonRotatingPatches — COMPLETE AND CORRECT.** `(sides inlet outlet)`
excluded; `blade` included. `simpleFoam/UEqn.H:3` calls
`MRF.correctBoundaryVelocity(U)`, and `MRFZone.cxx:508–535` overwrites every
included-patch face velocity to `Omega ^ (Cf − origin)` each iteration — so
the blade wall rotates correctly despite `0.orig/U`'s
`fixedValue uniform (0 0 0)` (that entry is dead text, not a defect).

**(3) cellZone coverage — COMPLETE.** `log.topoSet`: `cellSet allcells`
230,135 → `cellZoneSet region0` 230,135 = every cell in the mesh.

**(4) The flux question — CONCRETE DEFECT FOUND, and it convicts §11's
initialisation, not the case.** The convention chain:

- simpleFoam stores the flux RELATIVE on zone faces: `pEqn.H:5`
  `MRF.makeRelative(phiHbyA)`, `pEqn.H:37` `phi = phiHbyA − pEqn.flux()`,
  with the Coriolis term added at `UEqn.H:8` (`MRF.DDt(U)`).
- potentialFoam solves in the relative frame (`potentialFoam.C:165`
  `MRF.makeRelative(phi)`) but then `potentialFoam.C:187`
  `MRF.makeAbsolute(phi)` and `:193` `U = fvc::reconstruct(phi)`, writing U
  (`:201`) and, under `-writephi`, phi (`:206`) — both ABSOLUTE.
- `makeAbsolute` adds `Omega ^ (C − origin)` over every zone cell and face
  (`MRFZone.cxx:447–489`). **This zone is the whole domain**, so the §11
  initial U field contained the frame's full solid-body sweep — |Ω×r| up to
  ~150 m/s at the domain corners against a 7 m/s physical inflow.

The §11 run was therefore initialised with a domain-wide hurricane and asked
to unwind it through `inletOutlet` far-field patches: the log agrees —
iterations 1–2 look healthy (Ux 0.38 → 0.14, continuity 4e-4), then the
nuTilda bounding cascade builds (692 events) and the forces grow
exponentially from t≈50. The "F5b cure" was borrowed from a case with no
rotating frame; **in a whole-domain MRF zone, `potentialFoam -writephi`
initialisation is actively toxic**, and the divergence needed no second
variable. (For completeness: the original run's `createPhi` startup flux is
also absolute, but that inconsistency lasts exactly one pressure solve and
every MRF tutorial survives it — it is not the disease.)

**Consequence:** the §12 two-arm split collapses to one corrected arm, per
the supervisor's re-scope authority. Reduced relaxation is no longer
implicated by any evidence and is dropped.

## 15. Amendment to §11 (dated 2026-08-07, before the arm is launched): the one corrected arm

**Arm A (the only arm):** initialise with potentialFoam run with the MRF
zone **deactivated** (`active false` during the init step only) — a pure
absolute-frame potential flow past the stationary blade: divergence-free,
blade-conforming, impulsive pressure transient removed, **no frame sweep and
no phi file written**. Then restore `active true` and run simpleFoam at the
**ORIGINAL relaxation** (p 0.3, U 0.7, nuTilda 0.7). Exactly one variable
differs from the original limit-cycling run: the initial U/p field.

**Gate, window, cap and prediction inherited from §11 verbatim:** window
t=1000–1500, UNSETTLED iff drift ≥ 1e-3 AND mono ≥ 0.90, p2p cap 400 N·m,
prediction turbine-signed mean Mx ∈ [+400, +1200] N·m, milestone = all four
conditions. Branches, updated per §14: (a) settles motoring-signed or (c)
oscillates/diverges → with geometry (§10), frame terms (§14) and
initialisation (this arm) all clean or tested, **the steady branch closes
the third way** and the transient branch inherits the quantified target
(settle within 400 N·m of 800); (b) settles turbine-signed with 800 outside
the band → a real quantified bias to chase. Predicted cost ≈ 13.5 core-min
(1500 iterations, 2 ranks).

*Nothing below this line existed when arm A was launched.*

## 16. Arm A result: the corrected initialisation lands in the same basin — the steady branch closes the third way

Init clean by its own numbers: potentialFoam (MRF inactive) continuity error
5.7e-7, 1.8 s. simpleFoam, original relaxation, 1500 iterations, 446 s at
2 ranks = **14.9 core-min**: no divergence (14 bounding events against
§12's 692), no convergence sentence, and the blade moment oscillates from
the first sample exactly as the original run does — window t=1000–1500:

| §11/§15 test | measured | verdict |
| --- | --- | --- |
| S12 unsettled (drift ≥ 1e-3 AND mono ≥ 0.90) | drift 1.14, mono 0.600 | does not fire — oscillation, not travel |
| cap: p2p ≤ 400 N·m | **3634.6 N·m (454% of Q_ref)** | **OVER — not gateable** |
| sign | mean **−1004.2 N·m** | **motoring-signed** |
| prediction: turbine-signed ∈ [+400, +1200] | −1004.2 | **FALSE** |

**The pre-registered prediction is scored FALSE and the diagnosis chain is
complete.** One variable was changed (the initial field, now divergence-free
and blade-conforming) and the solution reproduced the original limit cycle
almost exactly (original window: mean −1037, p2p 7679; arm A: −1004, 3635).
So: geometry verified correct (§10), frame terms verified correct to the
source line (§14), initialisation now tested clean (this arm) — and the
+omega steady solution still oscillates motoring-signed with an ungateable
band.

**THE STEADY-MRF BRANCH IS CLOSED, THREE WAYS ON EVIDENCE:**
1. the existing history's mean is not a measurement (§3 — band 960% of the
   cap);
2. every configuration suspect is eliminated — geometry (§10), frame/flux
   conventions (§14), initialisation (arm A);
3. the corrected single-variable re-run reproduces the limit cycle rather
   than escaping it (§16).

What steady tools cannot decide — whether the oscillation is genuinely
unsteady rotor-wake physics or a SIMPLE algorithm that cannot reach the
attached solution — is precisely the transient branch's question, and it
inherits the quantified target this record built: **settle the low-speed-
shaft torque, turbine-signed (+Mx for +omega), with a window band ≤ 400 N·m,
against the 800 N·m secondary-tier reference (Processes 12(9):1994 Table 6,
digitised from Hand et al. 2001).** The product list's "MRF first, then
transient" has completed its first clause on evidence.

## 17. Cost, final (supersedes §13)

| item | core-min |
| --- | --- |
| gate (existing history + reference fetch) | 0 |
| omega-flip confirmation (600 iters, 4 ranks) | 5.8 |
| step-2 settle extension (1500 iters, 4 ranks) | 13.6 |
| step-1 STL-orientation audit (§10) | 0 |
| §11 initialised re-run (diverged) | 13.4 |
| §14 MRF flux/frame audit | 0 |
| §15/§16 arm A (corrected init, original relaxation) | 14.9 |
| **total across the item and its riders** | **47.7** |

## 13. Cost, final (supersedes §9)

| item | core-min |
| --- | --- |
| gate (existing history + reference fetch) | 0 |
| omega-flip confirmation (600 iters, 4 ranks) | 5.8 |
| step-2 settle extension (1500 iters, 4 ranks) | 13.6 |
| step-1 STL-orientation audit (§10) | 0 |
| §11 initialised re-run (1500 iters, 2 ranks, diverged) | 13.4 |
| §14 MRF flux/frame audit | 0 |
| **total across the item and its riders** | **32.8** (before arm A) |
