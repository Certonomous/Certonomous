# MRF_R1 — Rushton-turbine power number via whole-tank MRF (campaign prose)

**STATUS: DRAFT / UNFROZEN. NO COMPUTE. NOT A GATE.** This is the campaign-prose
companion to the frozen-location pre-registration
`verification/campaign/MRF_R1_PREREGISTRATION.md` (the authoritative document).
Where the two disagree, the pre-registration governs.

## What R1 is

The first rung of the Navier-class **MRF rotating-machinery** case (Case 2 of the
parity pack). It grades the **power number `Np`** of a standard 6-blade Rushton
disc turbine in a fully-baffled stirred tank, computed from the **steady
frozen-rotor MRF impeller torque**, against the Rushton/Costich/Everett 1950
turbulent-plateau correlation value `Np_ref = 5.0`.

    Np = 2π Q / (ρ N² D⁵)      Q = impeller torque [N·m], N = rev/s, D = impeller Ø

## Why this rung, and why MRF (not AMI)

- **Cheapest defensible rung.** One operating point, one geometry, one integral
  scalar (torque). No inlet/outlet, no diffuser, no flow-matching. The reference
  is a correlation that, for a standard geometry, behaves as a near-exact value.
- **MRF, not AMI.** A steady power number needs only a frozen-rotor MRF (Luo/
  Issa/Gosman 1994). Torque is far less frozen-position-sensitive than the local
  field. AMI sliding mesh (Farrell & Maddison 2011; transient) is deferred to a
  later rung. The ERCOFTAC pump head-flow point (Ubaldi 1996 / Combès U3) is
  deferred to R2+.
- **Reused precedent:** F8's whole-domain MRF torque gate
  (`verification/campaign/F8_MRF_HAND2001_GATE.md`) — its torque-from-
  `moment.dat` convention, `nonRotatingPatches` discipline, settledness test and
  "predict, then name the risk" structure are carried over.

## Reference tier

**bounded-agreement (provisional, capped).** Against manifest values only
(Rushton 1950 not yet fetched/title-verified), the honest ceiling is
code-verified / bounded-agreement — **NOT experiment-validated**. The §3 band is
always shown with the case; the tier is upgradable to experiment-validated once
a title-verified PDF (Rushton 1950 correlation, or Wu & Patterson 1989 LDA)
lands. This case is not yet a *completed 3D case*, so it is registered into the
frozen `reference_tier_registry.json` only on completion and only by the
verification supervisor. (A title-verified Rotor 37 reference was offered by a
retrieval lane and declined for R1 as out-of-Case-2-scope compressible physics —
see the pre-registration §1.)

## Gate, band, cap (see the pre-registration for the frozen detail)

- **Gate:** finest-level `Np`, graded by the shared instrument
  `scripts/roache_triple.py` (Roache rule-5, GCI at Fs = 1.25, dim = 3).
- **PASS band:** `Np ∈ [4.0, 6.0]` (Np_ref 5.0 widened for the 5.0–6.0
  literature spread + steady-MRF low-bias margin).
- **Prediction / named risk:** steady MRF is documented to under-predict
  Rushton `Np` (Brucato 1998); predicted low-side [3.5, 5.0]; a `Np < 4.0`
  GATE FAIL is a *result* quantifying MRF bias, not a defect.
- **Compute cap:** 420 core-minutes (≈ 7 core-h; derived ≈ $0.36, not measured).
  Overrun stops the run (rule 12).

## Mesh

`snappyHexMesh` from an STL of {tank + 4 baffles + shaft + 6-blade disc turbine};
`topoSet` builds the rotating impeller cellZone. Three geometrically-similar
levels, linear r ≈ 1.5 (~250k / ~0.85M / ~2.9M cells), for a Celik-2008 GCI
triple. Per `docs/standards/MESH_STANDARD.md`: §3 gates (non-ortho ≤ 70°, skew
≤ 4); §8.1 BUILD-BEFORE-FREEZE (coarse level built + checkMesh'd admissible
before the freeze); §9.2 per-level graded-parameter read-back; §11.4
aspect-ratio + cell-volume-ratio in each birth certificate.

## Grader (diff-read is the supervisor's check-1)

`cases/navier_class/MRF/grade_mrf_np.py` — built on the shared Roache instrument
and adding: rule-4 strict completion (incompressible field set `U p phi k omega
nut`), a **live planted-zero control** on the real `moment.dat` read path
(refuses exit 2 if a blind reader can't see `PLANT = 1.234e-03`), and the torque
→ `Np` arithmetic. `--selftest` drives the control both directions and passes
(exercised 2026-09-09). Refuses rather than degrades; fixed verdict vocabulary
only.

## Pre-flight EXERCISE smoke (A3FL1)

Before the graded freeze: build+checkMesh coarse, topoSet the zone,
potentialFoam init (MRF zone inactive during init — the F8 §15 lesson),
simpleFoam ~50 iterations, confirm rc=0, residuals falling, a finite plausibly-
signed `moment.dat` torque, no bounding cascade. A failed smoke run is a finding
(supervisor check-2), not a licence to launch.

## STOP

Freeze (sha) and graded launch are the supervisor's check-4. This lane stops
here: DRAFT/UNFROZEN, no compute.
