# F12 pre-registration: RAE 2822, AGARD AR-138 Case 9

**Written 2026-07-30, before any solver was launched on this case.** Nothing
below is edited after the fact. If the result falsifies the prediction, the
prediction stays as written and the record says so, exactly as F6b's did.

## The case

RAE 2822 aerofoil, AGARD AR-138 Case 9. Re = 6.5e6 on chord, transonic,
shock-bearing, attached (Case 10 is the separated one; this is not that).

**Conditions solved.** Two, because the published corrected conditions for this
case do not agree and picking one silently is the classic way to be confidently
wrong here.

| Convention | Mach | alpha (deg) | Where it comes from |
| --- | --- | --- | --- |
| Workshop (primary) | 0.734 | 2.79 | International Workshop on High-Order CFD Methods, case C2.2 / ADIGMA MTC5 |
| Tape | 0.730 | 2.79 | The reference data's own record: measured Mach, corrected incidence |

The incidence correction, 3.19 deg geometric to 2.79 deg corrected, is common
to both and is carried by the reference data itself. Only the Mach differs, by
0.004. The primary grade is at the workshop condition; the tape condition is
solved at one mesh level so the sensitivity to the disagreement is measured.

A third convention, M = 0.734 with alpha = 2.54 deg, circulates in the
literature and is **not** used: 2.54 deg is the tape's corrected incidence for
Case 6, not Case 9.

## The reference

Cook, P.H., McDonald, M.A., Firmin, M.C.P., "Aerofoil RAE 2822 - Pressure
Distributions and Boundary Layer and Wake Measurements", AGARD AR-138 (1979).
Digitised as AFOSR-HTTM/Stanford flow case 8621 (evaluator R. E. Melnik, 1981),
hosted by the NASA Turbulence Modeling Resource. Secondary but authoritative:
it is a transcription made by the experiment's own AGARD evaluator, not the
AR-138 document itself, and it is labelled secondary everywhere it is used.

Measured quantities graded against: 52 upper-surface and 50 lower-surface
pressure taps, CN = 0.803, CM = -0.099, CD = 0.0168. The experimenters quote
their tap uncertainty as Cp to within +/- 0.0026 at this Reynolds number.

## Gates, declared now

A run is admitted as evidence only if the mesh gate and the convergence gate
both pass. The physics gates are then graded on the **finest mesh at the
workshop condition**.

**Admission gate A, mesh.** Every mesh in the ladder: max non-orthogonality
<= 70 degrees and max skewness <= 4, boundary faces included, per
`docs/standards/MESH_STANDARD.md`. Aspect ratio is advisory there and is
recorded with its alignment justification, not gated.

**Admission gate B, convergence.** The solver must print its own convergence
statement. A small-looking residual is not a substitute (LESSONS L-14, L-15).
A run that does not converge is not a result and is not graded.

**Gate 1, surface pressure (primary).** RMS deviation of the computed Cp from
the measured taps, CFD interpolated onto the tap stations:

- upper surface RMS <= **0.08**
- lower surface RMS <= **0.04**

Basis for the numbers: F1 (ONERA M6, 3D, 399k cells) was recorded GATE REACHED
at upper-surface RMS 0.049 to 0.114 with pressure-side 0.013 to 0.027. This is
a two-dimensional, wall-resolved case with far more surface resolution per
chord, so the bar is set inside F1's achieved band rather than at it.

**Gate 2, shock location.** |x_shock(CFD) - x_shock(experiment)| <= **0.020**
chord, both measured by the same definition: the chordwise station where
upper-surface Cp crosses the critical (sonic) value from below on the
recompression, linearly interpolated between bracketing points.

Why this definition and not steepest-gradient: F2's record documents that a
steepest-gradient detector can only return values on the sample lattice, that
its resolution there was 0.052 chord, and that a deviation smaller than one
lattice step was wrongly narrated as a physical shift. The sonic crossing is
continuous in x, is identically defined on the experimental taps and the CFD,
and does not quantise. Steepest-gradient is also recorded, with its own
resolution quoted beside it, and is never quoted alone.

Basis for 0.020: the experimental tap spacing through the shock is 0.025 chord,
so the reference's own shock position is resolved to roughly +/- 0.0125. A
tolerance of 0.020 is a little over one tap interval and cannot be met by luck.

**Gate 3, normal force.** |CN - 0.803| / 0.803 <= **5%**.

**Gate 4, drag.** |CD - 0.0168| / 0.0168 <= **20%**. Declared generous, and
declared generous *now* rather than after seeing the number: the reference CD
is a wake-traverse total drag from a tunnel, and the comparison is against a
fully turbulent, free-air, finite-domain RANS. It is a one-sided comparison and
20% is the honest width for it.

**Reported, not gated: CM.** The measured CM is -0.099. Pitching moment on this
section is dominated by the aft-loaded lower surface and by the trailing-edge
closure, both of which are interpolation-sensitive on a 65-station coordinate
table. It is reported with its deviation and it does not decide the verdict.
Saying so in advance is the point.

**Overall verdict.** PASS requires admission gates A and B plus Gates 1, 2, 3
and 4, all on the fine mesh at the workshop condition. Anything less is
recorded as a documented failure in the campaign record and does not become a
filmed act, per the standing no-failures-on-camera rule.

## Mesh study

Three levels, factor two in every direction, so an observed order of
convergence is meaningful:

| Level | surface cells per quarter | wake | wall-normal | cells |
| --- | --- | --- | --- | --- |
| coarse | 48 | 48 | 80 | 23,040 |
| medium | 96 | 96 | 160 | 92,160 |
| fine | 192 | 192 | 320 | 368,640 |

Wall-normal first cell 2e-6 chord, targeting y+ below 1 so the boundary layer
is resolved rather than bridged. Reported for every level: cells, mesh quality,
convergence statement, CN, CD, CM, both shock measures and both Cp RMS values.
A single-mesh result is not shipped.

Two further runs, both at medium: the tape condition (M = 0.730) to measure the
correction-convention sensitivity, and a doubled far-field radius to measure
the domain-size sensitivity of a lifting transonic case.

## Prediction, recorded before the data is seen

1. The shock will sit **downstream** of the measured position, by 0.01 to 0.03
   chord. Linear eddy-viscosity closures under-predict the shock-induced
   thickening of the boundary layer, which is what pushes the shock forward;
   the same one-sided bias is already on this lab's record as F6a's +13.95%
   reattachment and F6b's +63% to +66%.
2. CN will be **over-predicted** by 0 to 4%, for the same reason.
3. CD will be **under-predicted**, by 5 to 20%, because a fully turbulent
   free-air RANS omits both the tripped laminar run and the tunnel's own
   contributions to the measured wake momentum deficit.
4. Upper-surface Cp RMS will be dominated by a small number of taps inside the
   shock foot, not spread evenly along the chord.

If the shock lands upstream of experiment, prediction 1 is falsified and the
record will say so in those words.
