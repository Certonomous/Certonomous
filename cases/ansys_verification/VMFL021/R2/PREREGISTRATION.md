# VMFL021-R2 — PRE-REGISTRATION (frozen before compute; CLAUDE.md rule 2)

Cavitation over a sharp-edged orifice, **Case A: High Inlet Pressure**. Ansys
Fluid Dynamics Verification Manual, Release 2026 R1, **p. 85**. Frozen file
(rule 6): after first graded compute, only dated addenda that cannot alter gate,
threshold, cap or label.

## This is a NEW ROW citing the old, under VERIFICATION_CHARTER §6

VMFL021 **attempt 1** is `NOT A RESULT` (validation register **row #18**), frozen
at commit **`605d5593`**. **That row is NOT removed, NOT re-labelled, NOT
softened.** This R2 is a fresh registration citing it, per `VERIFICATION_CHARTER`
§6 and `ANSYS_VERIFICATION_CHARTER` §6 ("A re-run after a repair is a new row
citing the old one").

**Attempt 1's two defects were both INSTRUMENT-SIDE — the physics was correct:**

1. **`controlDict` carried `writeInterval 0.01` against `endTime 0.003` under
   `writeControl adjustable`, so NO `endTime` field directory was ever written**
   at any level. L1 and L2 finished `rc=0` but held only a `0` time directory;
   rule 4's strict completion could not certify them. (Confirmed from disk: the
   attempt-1 `controlDict` is `writeControl adjustable; writeInterval 0.01;` with
   `endTime 0.003`.)
2. **L3 has NO `RUN_RC.txt`** — the L3 lane was killed mid-run by a supervisor
   dispatch error, not by anything wrong with the case.

Neither defect touched the reference, the gate, the geometry, the solver choice
or the physics. This R2 carries the sound design forward unchanged and fixes the
machinery.

## What is CARRIED FORWARD UNCHANGED (verified sound in attempt 1)

- **The gate design — inlet-flux discharge coefficient. DO NOT MOVE IT.**
  `Cd = |Q_inlet| / (A2 · V_theo)`, flux read at the **pure-liquid inlet**
  (`alpha.water = 1`, so `rho_l` cancels exactly in `mdot`). The outlet is used
  ONLY to read the throat area from the function-object header and cross-check it
  against the geometric flat-wedge `A2`. **Case A SUPERCAVITATES TO THE OUTLET**
  (independently found: outlet volumetric flux 4.29e-4 against inlet 3.18e-4), so
  grading on outlet **volume** flux would give `Cd ≈ 0.869`, badly wrong, while
  conserved mass at the inlet gives `≈ 0.645`. The comparator reads at the inlet
  for exactly this reason. **Preserved. The measurement is NOT moved to the
  outlet and the gate is NOT switched to an outlet flux.**
- **The physics check, which PASSED.** Nurick's cavitation number
  `K = (P1 − Pv)/(P1 − P2) = 249,996,460 / 249,905,000 = 1.00037`; his
  correlation `Cd = Cc·√K` with `Cc = 0.62` gives `0.6201` against the manual's
  `0.620` — agreement 0.02%. `P1 = 2.5e8 Pa` is **LOAD-BEARING, not a typo**:
  only `P1 ≫ P2` drives `K → 1` so `Cd → Cc = 0.62`. Confirmed against the manual
  p.85 material-properties panel (`P1 = 250,000,000 Pa`).

## The ten-line freeze (PREREG_TEMPLATE standard form + all four amendments)

```
1. CASE            : VMFL021-R2 — Cavitation over a sharp-edged orifice, Case A
                     (high P1) — manual p.85. Solver = interPhaseChangeFoam
                     (OpenFOAM v2606), SchnerrSauer cavitation, kEpsilon RAS,
                     axisymmetric 5deg wedge. NEW ROW citing attempt 1
                     (register row #18, NOT A RESULT, commit 605d5593). NOT YET
                     RUN; verification/runs/ansys_verification/VMFL021/R2/ absent
                     at 2026-08-25T22:16:32Z (checked: dir does not exist at freeze).
2. REFERENCE       : Cd = 0.620 (coefficient of discharge), source = W.H. Nurick,
                     "Orifice Cavitation and Its Effects on Spray Mixing",
                     J. Fluids Engineering 98, 681-687, 1976. Ansys Fluent
                     reported Cd = 0.631 (ratio 1.018), Ansys CFX 0.637 (1.03) —
                     CONTEXT ONLY, never the gate.
3. REFERENCE KIND  : measured/experimental → CAN buy P (Nurick 1976 experimental).
                     DISCLOSED NUANCE: the target 0.620 coincides with Nurick's
                     correlation Cd = Cc*sqrt(K) in the K→1 fully-cavitated limit,
                     i.e. essentially the contraction coefficient Cc itself; read
                     strictly as a correlation it would buy V. Tier ceiling (line 4)
                     set so neither reading over-claims.
4. TIER CEILING    : GATE REACHED. Team ceiling (Sanaa); safe under the
                     experimental-vs-correlation ambiguity on line 3.
5. QUANTITIES      : Cd = |Q_inlet| / (A2 * V_theo); Q_inlet = time-averaged
                     sum(phi) [m3/s] over the INLET patch (pure liquid there);
                     A2 = orifice flat-wedge sector = 6.9725e-7 m2 (READ from the
                     outlet FO header, cross-checked vs geometric A2 to 0.5%);
                     V_theo = sqrt(2*(P1-P2)/rho_l) = 706.97 m/s. Flux read at the
                     inlet, never the (supercavitating) outlet — see above.
6. BANDS (THE GATE): |Cd_lab - 0.620| / 0.620 <= 0.05 at the finest converged
                     level. JUSTIFICATION (not from any run): manual's stated 3%
                     accuracy goal (p.609) + ~2% for the SchnerrSauer-vs-ZGB
                     cavitation-model substitution (OpenFOAM has no ZGB) = 5%.
7. LADDER          : interPhaseChangeFoam / SchnerrSauer / kEpsilon + standard
                     wall functions (matches manual p.85). SchnerrSauer FROZEN
                     (inertia-driven default; NOT tuned). ZGB unavailable on this
                     box. Mesh: axisymmetric 5deg wedge, 3 blocks, birth-certified
                     by the launcher (MESH_STANDARD §6).
8. DECOMPOSITION   : grid triple, spatial ratio r=2, orifice-radial N2R =
   SEED              12 / 24 / 48 (L1/L2/L3), all directions x2 per level; L1 ~
                     832 cells. dt Courant-limited (adjustTimeStep, maxCo=2), so
                     the triple measures COMBINED space-time error. SERIAL (RANKS=1).
9. PRINCIPAL RISK  : the ONE predicted failure mode — NUMERICAL STIFFNESS at
                     2.5e8 Pa (ideal jet ~707 m/s, water Mach ~0.48 vs the
                     incompressible assumption the manual itself makes). PREDICTED
                     failure: the solve does not reach a plateau within the cap (or
                     diverges) -> NOT A RESULT, an honest statement of this
                     incompressible solver's limit, not a fabricated number. If it
                     stabilises, the deep-cavitation Cd should saturate near Cc=0.62.
10. EXPECTED ORDER : formal p_f = 1 (linearUpwind/vanLeer at a sharp-edge
                     singularity); expect p_obs in [0.5, 1.5]; p_obs > 2.0
                     SUSPICIOUSLY HIGH (flagged, not celebrated).
11. WEDGE/GEOM BIAS: N-AV9 sin(t)/t = 0.127% at 5deg; CANCELS in Cd (same
                     flat-wedge patch area in numerator flux and denominator
                     normalisation). Residual << 0.05 gate. Carried.
12. COST + CAP     : estimate ~40 core-min total (L1 ~0.6, L2 ~5, L3 ~34; serial
                     RANKS=1; basis: Case A endTime 0.003 s with Courant-limited
                     dt ~1e-6 s; reported-by-owner). CAP = 180 core-min RUNAWAY
                     GUARD, enforced PER LEVEL from a running draw-down
                     (timeout_s = remaining_core_min*60/RANKS, refuse at zero) —
                     NOT a shared blind drawdown; each RUN_RC.txt records
                     remaining_core_min and prereg_blob at launch. Overrun STOPS
                     the run (rule 12); a crossing is reported to the supervisor.
13. CONTROLS       : planted-zero (rule 3) PLANT=1.234e-6 m3/s, read back, refuses
                     if unseen; strict completion (rule 4, adaptive-dt form);
                     Roache triple (rule 5); PLATEAU CLAUSE (Amendment 4, all five
                     items — see §A4 below); REGIME PRECONDITION (see §REGIME);
                     LAUNCHER FREEZE CHECK (Amendment 2); endTime/writeInterval
                     assertion + field-dir-at-endTime check (Amendment 3 + the two
                     new launcher artifacts). grade_vmfl021_r2.py --selftest green.
```

## WHAT MUST CHANGE — the four fixes registered on this freeze

### FIX 1 — the `controlDict` write-control defect (the reason attempt 1 was ungradeable)
The frozen R2 `controlDict` is `writeControl adjustableRunTime; writeInterval
0.0005;` with `endTime 0.003` — so `0.003 / 0.0005 = 6` EXACT and `adjustableRunTime`
forces a write AT `endTime`. **The launcher ASSERTS, before any solver starts
(new required artifact, ARTIFACT 7):** `endTime` is an exact integer multiple of
`writeInterval` under a `runTime`-form write control, aborting explicitly with
`|| { echo ABORT; exit 1; }` if not. **And after each level's solver
(ARTIFACT 8):** a field directory at `endTime` (with `U`) must exist before the
level is called complete, recorded as `endtime_ok` in `RUN_RC.txt`. Amendment 3's
six checks all passed on attempt 1 yet it wrote nothing gradeable; these two
artifacts close that hole. They are non-droppable for this team going forward.

### FIX 2 — per-level caps, not a shared drawdown
The orchestrator draws the 180-core-min budget down **per level** from
`remaining_core_min` and refuses to launch a level at zero; each `RUN_RC.txt`
records `remaining_core_min` and `prereg_blob` at launch. This is what let the
supervisor distinguish a starved level from a genuinely failed one in triage.

### §REGIME — a regime precondition on the triple (the VMFL022 trap)
VMFL022 graded `NOT A RESULT` because its coarse level **never cavitated**
(`Min alpha = 1`) while the finer two did — the three levels were not solving the
same problem and the Roache triple came out `OSCILLATORY` (R = −0.104878). **The
R2 comparator reads `min(alpha.water)` at `endTime` for every level and, if any
level is not in the cavitating regime (`min alpha > 0.99`, i.e. < 1% vapour
anywhere), returns `NOT A RESULT` and does NOT difference the levels** — the
regime is the FIRST gate in the verdict cascade, before the triple is computed,
so a wrong-regime level is never averaged into an observed order. For Case A
(deep cavitation, K→1) every level should reach `alpha ~ 0` at the vena
contracta; the guard is registered regardless (it bites Case B harder).

### §A4 — the plateau clause is now the Amendment-4 required artifact
Attempt 1 (and VMFL022) used a windowed **coefficient of variation alone**, which
PREREG_TEMPLATE Amendment 4 classes "Weakest": a monotonically rising series can
have a small CoV. The R2 comparator replaces it with the required artifact,
modelled on the VMFL007 reference, carrying ALL FIVE items:
1. a fractional window (last 30%) **with an explicit minimum-sample floor**
   (`PLATEAU_MIN_SAMPLES = 20`);
2. a **REFUSAL** below the floor → `CANNOT_TELL`, never a pass;
3. a **growing-series-rejecting statistic** — final-window `|Q|` peak-to-peak as
   a fraction of the whole-run range (`PLATEAU_PTP_FRAC_OF_RANGE = 0.03`); CoV is
   kept only BESIDE it (also gated at 3%), never instead of it;
4. a **null-range REFUSAL** — a `|Q|` series that never resolvably moved
   (`whole-run range < 1e-7 m3/s`) is refused, `CANNOT_TELL`;
5. the realised sample count (`n_window`) recorded in the grading JSON.
The selftest demonstrates the point Amendment 4 exists for: a growing series with
a final-window CoV of 0.81% (which the old CoV-only gate would pass) is correctly
rejected by ptp/range at 30%.

## PHYSICS CONSISTENCY CHECK (carried forward from attempt 1 — PASSED)

- Nurick K = (P1 − Pv)/(P1 − P2) = 1.00037 (deep cavitation).
- Nurick's correlation Cd = Cc·√K, Cc ≈ 0.62 → **0.6201** vs manual **0.620**,
  agreement **0.02%**. At very high inlet pressure the flow is fully cavitated at
  the vena contracta (K→1), so Cd saturates at Cc = 0.62 independent of pressure
  magnitude — which is why "high inlet pressure" gives the LOWER Cd (0.620) and
  Case B (weak cavitation, K=1.59) gives the HIGHER Cd (0.780). Both are Nurick's
  own physics; neither is a mis-specified regime.

## Grading path (fixed at this commit)

`cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py`, verified by the
launcher to hash equal to its HEAD blob before any solver starts. Launcher:
`cases/ansys_verification/VMFL021/R2/run_vmfl021_r2.sh` (Amendment-3 six artifacts
+ the two new required artifacts: endTime/writeInterval assertion, field-dir-at-
endTime completeness check). Run root:
`verification/runs/ansys_verification/VMFL021/R2/`.
