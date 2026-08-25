# ansys-lane-opus48 — VMFL021 / VMFL022 — LANE REPORT + DUPLICATE-DISPATCH COLLISION

**Written to the RUN dir (not the contested `cases/` dir) to preserve findings
without clobbering a concurrent lane's uncommitted work. UTC 2026-08-25.**

## COLLISION (the headline — needs supervisor arbitration)

Two lanes independently built VMFL021 AND VMFL022 (the SAME two cases).

- **My build is COMMITTED at `605d5593`** (parent `fc531df1`), 32 files, verified
  post-commit (only my two case dirs; foreign-count 0). It is an ancestor of HEAD.
  My build: phi-based Cd (measured at the pure-liquid inlet so rho cancels),
  meshes 832/3328/13312 cells, PLANT 1.234e-6, SchnerrSauer.
- **A concurrent lane OVERWROTE my files on disk (UNCOMMITTED).** Their build:
  rhoPhi-based Cd, meshes 1040/4160/16640, PLANT 3.21e-4, a different launcher
  (RUN_ROOT as arg, VMFL_SMOKE hook), different prereg wording. Their disk files
  are UNTRACKED; HEAD still carries MY committed version.
- **The shared index is DECAYED**: `git status` shows my 32 files as staged
  DELETIONS (`D`) with the dirs reappearing as `??`. Per CLAUDE.md rule 10 I did
  NOT touch the index and did NOT revert their untracked work.

**I did not overwrite their disk files. I graded MY run against MY frozen
comparator extracted from HEAD (`git show HEAD:...`), touching no disk file.**
Which build is canonical is cross-lane arbitration = the supervisor's call.

## FEASIBILITY GATE (decided first, honestly): OPEN

interPhaseChangeFoam EXISTS (OpenFOAM v2606) with Kunz/Merkle/SchnerrSauer →
VMFL021/022 NOT BLOCKED on solver capability. ZGB (Ansys's model) is absent;
SchnerrSauer substituted, priced into the gate. VMFL017 fallback NOT triggered.

## PHYSICS CONSISTENCY CHECK (mandatory): BOTH PASS

The manual's targets reproduce through Nurick's own law Cd = Cc·√K, Cc=0.62,
K=(P1−Pv)/(P1−P2):
- Case A (VMFL021): K=1.00037 → 0.6201 vs target 0.620 (0.02%). Deep cavitation,
  Cd saturates at Cc; the extreme P1=2.5e8 Pa is LOAD-BEARING, not a typo.
- Case B (VMFL022): K=1.59006 → 0.7818 vs target 0.780 (0.23%). Weak cavitation.
Neither is a mis-specified regime (contrast VMFL036 Re=100-vs-50, VMFL059).

## VMFL022 (Case B) — VERDICT: NOT A RESULT (my run, my frozen comparator)

Fully graded (comparator sha 1c750397, = HEAD blob; planted-zero FIRED and
passed; strict completion passed all three levels to endTime 0.06 with fields):

| Level | cells | Cd | window CoV | Min(alpha.water) |
|---|---|---|---|---|
| L1 | 832 | 0.74442 | 0.010% | 1.0 (NO cavitation) |
| L2 | 3328 | 0.76091 | 0.081% | 0.264 (cavitated) |
| L3 | 13312 | 0.75918 | 0.224% | (cavitated) |

- Roache triple: **OSCILLATORY** (R = −0.105) → **NOT A RESULT (rule 5)**.
- L3 Cd 0.759 is INSIDE the 5% band (2.67% off Nurick 0.780) — but the triple is
  not converging, so it cannot be certified. The gate can only turn a result INTO
  NOT A RESULT, never the reverse.
- **ROOT CAUSE = a genuine physics finding: cavitation onset is MESH-DEPENDENT.**
  At L1 (coarse) the vena-contracta pressure peak is under-resolved, p_min never
  reaches pSat, and the solve is single-phase (Cd 0.744). At L2/L3 the cavity
  forms (Cd ~0.76). The regime change between grid levels breaks the monotonic
  convergence a Roache triple needs. This is exactly the Case-B principal risk I
  pre-registered.
- Grading JSON: `verification/runs/ansys_verification/VMFL022/GRADING_VMFL022.json`.

## VMFL021 (Case A) — attempt-1: NOT A RESULT (my case-setup defect), STOPPED

- My run L1/L2 completed (rc=0), STRONGLY cavitated (Min alpha 0.064 → 0.0022),
  Cd 0.663 (L1) → 0.642 (L2), CONVERGING DOWN toward Cc=0.620 — physically right.
  My setup was STABLE at 2.5e8 Pa (no blow-up; upwind k/epsilon + deltaT ramp
  1e-9 under maxCo 2). (The other lane reported an epsilon→1e170 FPE for Case A;
  my scheme choice avoided it.)
- **DEFECT (mine): controlDict writeInterval 0.01 > endTime 0.003 with
  `adjustable` write control → NO endTime field dir is written**, so the frozen
  strict-completion clause 3/4 cannot certify the run even though it reached
  endTime (End line, FO series to 0.0030002). The Cd data is complete in the FO;
  the FIELD output is missing.
- I STOPPED my VMFL021 L3 (was ~15 min in, ungradeable, and the collision needs
  arbitration first) — my own processes only, targeted by cwd.
- Repair staged (writeInterval → 0.001, so 0.003 becomes a write multiple), NOT
  committed pending arbitration.

## NUMERICS / LESSONS drafts (for the supervisor to land, per charter §7)

- **N-AV (Nurick orifice law):** VMFL021/022 targets ARE Nurick's Cd=Cc·√K,
  Cc=0.62. High P1 → K→1 → Cd→Cc=0.62; low P1 → K=1.59 → Cd=0.78. A
  physics-consistency anchor for cavitating-orifice verification targets.
- **N-AV (cavitation onset is mesh-dependent):** a coarse mesh under-resolves the
  vena-contracta suction peak, suppresses cavitation, and gives the single-phase
  Cd; the cavity appears only on finer meshes. This breaks Roache monotonicity of
  cavitating-orifice Cd — a grid triple can be OSCILLATORY purely from the onset
  transition. Measured: VMFL022 L1 no cavity, L2/L3 cavity.
- **N-AV (OpenFOAM has no Zwart-Gerber-Belamri):** interPhaseChangeFoam v2606
  ships Kunz/Merkle/SchnerrSauer only; Ansys VM cavitation cases use ZGB, so the
  lab must substitute and price the substitution into the gate.
- **N-AV (ratio-QoI wedge cancellation):** measuring Cd = |Q_inlet|/(A2·V_theo)
  at the pure-liquid inlet cancels BOTH ρ and the N-AV9 sin(t)/t wedge deficit
  (same flat-wedge area in flux and normalisation).
- **L- (phi vs rhoPhi):** `rhoPhi` is not visible to surfaceFieldValue in
  interPhaseChangeFoam ("Requested field rhoPhi not found in database"); `phi`
  (volumetric) works. Measure at a single-phase patch so ρ is known/cancels.
  [NOTE: the concurrent lane graded on rhoPhi — arbitration should check whether
  their rhoPhi FO actually populated.]
- **L- (wedge axis faces):** the axisymmetric-wedge axis produces zero-area/skew
  faces; checkMesh prints "Failed 2 mesh checks" with rc=0 — benign, must not be
  read as a mesh failure.
- **L- (writeInterval > endTime):** with `adjustable` write control and
  writeInterval > endTime, OpenFOAM writes NO endTime field dir even though the
  run reaches endTime — silently breaks any strict-completion clause that checks
  the endTime field. (My VMFL021 attempt-1.)
- **L- (duplicate dispatch):** two ansys lanes built VMFL021/022 independently and
  collided on disk and in the shared index — the docket-claim-first rule was not
  honoured. Reported for the supervisor.

## COST (measured, my runs)

- VMFL022: L1 0.20 + L2 0.78 + L3 ~ (finished; see ORCH.log) core-min, serial
  RANKS=1. Basis: owner-stated $0.0513/core-h; dollars DERIVED not measured.
- VMFL021 attempt-1: L1 0.38 + L2 2.82 core-min + L3 partial (stopped ~15 min).
- Estimate-vs-actual calibration deferred to the canonical build post-arbitration.
