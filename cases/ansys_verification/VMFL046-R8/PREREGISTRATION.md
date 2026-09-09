# VMFL046-R8 — PRE-REGISTRATION (DRAFT, NOT FROZEN)

**Case:** VMFL046 — Supersonic Flow with a Normal Shock in a Converging-Diverging Nozzle
(Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155; title-page verified against
the PDF, rule 15).
**Successor axis:** SOLVER CHOICE. `rhoCentralFoam` (density-based, R6/R7) → `rhoPimpleFoam`
(pressure-based, PIMPLE) with R5's documented numerics.
**Predecessor:** VMFL046-R7, register **row #70 = NOT A RESULT** (L1 core-dumped rc 134,
"Negative initial temperature T0 ≈ -18.33" at Time ≈ 0.02813 s; comparator refused exit-2 at
strict completion).
**Status:** DRAFT written by an ansys-lane-opus48. NOT committed, NOT frozen. The §3 check-1
comparator diff-read and the sha-freeze are the supervisor's, separately gated. This document
is amendment-legal until first compute (rule 2); the graded run directory
`verification/runs/ansys_verification/VMFL046-R8/{L1,L2,L3}` **does not yet exist** and no
solver has run against this registration.

---

## 1. WHY R8 — R7 #70 IS NOT A TERMINAL NOT A RESULT

R6 and R7 ran the density-based `rhoCentralFoam`. Both core-dumped in the impulsive transonic
startup with a **negative reconstructed temperature** — R6 at Time ≈ 1.86e-4 s (impulsive IC),
R7 at Time ≈ 0.02813 s (after R7's start-from-rest IC fix cleared the *early* onset, a *later*
onset appeared). This is a **solver-specific numerics artifact** of `rhoCentralFoam`'s
explicit, UNBOUNDED face-reconstruction e→T inversion (verified at source: it reads no
`fvOptions`/`fvConstraints`/`bound` on T), **not a capability limit**. Two in-solver levers
were driven to exhaustion and answer-blind-**FALSIFIED**:

- **Reconstruction diffusion + Courant (option B).** An answer-blind two-stage smoke
  (`verification/runs/ansys_verification/VMFL046-R8/SMOKE_optB_L1`) with the most-diffusive
  shipped TVD limiter Minmod/MinmodV at maxCo 0.05 (10× below the central-scheme stability
  limit) **still core-dumped** at Time ≈ 0.03233 s (negative T0 = -0.4967). It *delayed* the
  onset (0.02813 → 0.03233 s) and *softened* the excursion 37× (-18.33 → -0.497) but did not
  clear it. Courant was pinned at 0.050 throughout — not a Courant runaway; not a reconstruction
  overshoot that more diffusion can remove.
- **Solver-level energy floor (option A).** `bound(e)` at TMIN=50 K clears the onset but fires
  PERSISTENT + GROWING through the run (229 → 812 hits per 5 ms bin), so the floored field ≠
  the stock field: confounded, and predicts NOT A RESULT.

**The SOLVER-CHOICE lever succeeds.** The manual's regime is a supersonic (max Mach 2.2)
moderate normal shock in a CD nozzle, solved in Ansys Fluent — a code that is pressure-based by
default. A pressure-based compressible OpenFOAM solver (`rhoPimpleFoam`) is an **admissible
numerics choice** for this regime: the same governing physics (compressible laminar
Navier-Stokes, ideal gas, one normal shock), a different pressure-velocity-energy coupling.
`rhoCentralFoam` is **not physics-mandated**. Evidence:

- The lab's own **R5** ran `rhoPimpleFoam` to `End` at 0.08 s on **all three levels** L1/L2/L3
  (rc 0; L1 3.1 / L2 22.6 / L3 171.583 core-min); its only failure was an outlet **washout**
  (lInf 2.0), REPAIRED at R6 (lInf 0.3). No negative-T startup crash.
- An answer-blind fresh smoke on the FROZEN R7 physical case + R5 numerics
  (`SMOKE_rhoPimple_L1`, rc 0, `End` at 0.08 s, 7.68 core-min) **cleared the ~0.028–0.032 s
  onset** (cell-min T 224.2 K at t ≈ 0.02970 s, positive) **and held through the frozen graded
  window** (0.064, 0.080] with **no negative-T recurrence** (min T 225.0 K). Only min/max(T)
  was read — never `x_shock`, Δp or Mach.

R8 is the fix-until-runs (§2ay) successor: the density-based startup crash is a characterized
solver-specific artifact, and an admissible startup-stable solver exists.

## 2. THE LEVER — SOLVER + NUMERICS, AND WHY IT IS ANSWER-BLIND

R8 changes the SOLVER and its numerics and **nothing about the physical case or the gate**:

- **Solver:** `application rhoCentralFoam → rhoPimpleFoam`.
- **Numerics = R5's documented, measurement-forced pressure-based set**, carried BYTE-IDENTICAL
  from `cases/ansys_verification/VMFL046-R5/case`:
  - `system/fvSchemes`: `ddt Euler`; convection `Gauss vanLeer(V) 1` (second-order TVD);
    `grad(U)` cellLimited.
  - `system/fvSolution`: PIMPLE `nOuterCorrectors 3`, `nCorrectors 2`, relaxation p/U/e 0.7,
    `transonic no`, `consistent no`, `pMinFactor/pMaxFactor 0.1/3.0`. Every constant was fixed
    by R5's coarsest-and-fine-level stability probe (R5 PREREGISTRATION §5.3), none is a
    threshold/band/cap.
  - `constant/fvOptions`: `limitTemperature` active, min 150 K / max 2000 K — a transient
    stabilizer `rhoPimpleFoam` **HONORS** (a no-op in `rhoCentralFoam`), non-binding at
    convergence.
  - `maxCo 0.2 → 0.5`: R5's L3-validated PIMPLE Courant limit (the explicit acoustic 0.2 of the
    density-based path does not apply).
- **Physical case carried from R7 BYTE-IDENTICAL:** mesh (`blockMeshDict.template`),
  start-from-rest `0/U`, `0/p` (waveTransmissive lInf 0.3 — R6's washout repair), `0/T`, and
  the thermo (`momentumTransport`, `thermophysicalProperties`, `turbulenceProperties`).

**Why gate-blind / answer-blind:** the steady shock position in a CD nozzle is uniquely set by
the FROZEN pressure BCs (inlet totalPressure p0 301325 Pa, outlet waveTransmissive fieldInf
176325 Pa), not by the discretization; a settled transient's plateau is discretization-detail-
independent within the r=2 convergence the Roache triple then tests. The solver was selected by
an **answer-blind robustness criterion only** ("clears the onset and holds through the window
with no negative-T recurrence"); **no `x_shock`, outlet Δp or Mach was read** to select it (the
smokes ran min/max(T) only, no centreline sampler).

## 3. THE GATE — CARRIED FORWARD FROM R1–R7 BYTE-IDENTICAL (L-487)

| quantity | value |
|---|---|
| primary reference `x_shock` | **1.250 m** (F. M. White, *Fluid Mechanics*, quasi-1D) |
| band `SHOCK_TOL` | **±5 %** (half-width 0.0625 m) |
| plateau `DELTA_X` | **6.250e-04 m** |
| `endTime` | **0.080 s** |
| sampler `SAMPLE_DT` | **5.0e-04 s** (160 samples; nPoints = 2·(NXA+NXB)+1) |
| plateau window | `W = endTime/10`, two adjacent windows → registered window t ∈ (0.064, 0.080] |
| r=2 triple | L1 (40/120/20) → L2 (80/240/40) → L3 (160/480/80) |
| reader | INTERPOLATING last downward Mach=1 crossing (D3) |

The comparator's gate constants, gate logic (`shock_location`, `plateau`, `windows`, `roache`),
W1/W2/W3, the planted controls A/B/C1/C2/D, and the rule-4 completion arithmetic are
**byte-for-behaviour identical** to R7 (the diff below is off-gate only; verified by the
line-diff escalated to the supervisor).

## 4. OFF-GATE COMPARATOR CHANGES (the whole diff — §3 check-1 subject)

`grade_vmfl046_r8.py` (selftest **75 ok / 0 FAILED**) changes vs `grade_vmfl046_r7.py`, all
off-gate:

- **(a) completion + config for `rhoPimpleFoam`.** `log.rhoCentralFoam → log.rhoPimpleFoam`;
  `MAXCO_GRADED 0.2 → 0.5`; new `check_pressure_based_config` pins the PIMPLE `fvSolution`
  (nOuterCorrectors), the frozen `fvOptions` clamp bounds [150, 2000] active, and PIMPLE
  iterations in the log. The rule-4 arithmetic (rc 0, End, ExecutionTime==Time count, last
  time == endTime within maxDeltaT, strictly-increasing time, age guard) is UNCHANGED.
- **(b) `check_T_clamp_nonbinding` REPLACES `check_T_physical_range`.** `rhoPimpleFoam` HONORS
  `fvOptions`, so R5's original "the limitTemperature clamp must be NON-BINDING" limb is back in
  force. It reads min/max(T) over the graded window — the windowed centreline samples AND the
  endTime T field — and REFUSES (exit 2) if T comes within 1e-3 relative of either clamp bound
  [150, 2000] K (a binding clamp truncates the field and could bias `x_shock`). ANSWER-BLIND:
  reads T bounds only, never a shock location; the in-window centreline reads are set-deduped by
  the W1 audit, so `n_read` is unchanged.
- **(c) `check_shock_stands` (NEW) — WASHOUT / shock-stand guard.** For every window sample the
  shock must STAND at an interior location `X_STAND_MIN 0.5 m < x_shock < X_EXIT − WASHOUT_STANDOFF
  = 1.898 m`, else the outlet has washed it to the exit (register #62 mode) and no gate quantity
  is meaningful → REFUSE. PURE GEOMETRY, ANSWER-BLIND: the band upper edge 1.3125 m is 0.585 m
  clear of 1.898 m, so it NEVER trips a shock near the reference; it can only turn a would-be
  verdict into NOT A RESULT, never license one (rule 5). The shock-ABSENT case (no downward M=1
  crossing) is already refused upstream by `shock_series`. This is the answer-blind washout
  question R8's smoke deliberately left to grade time.

## 5. THE VERDICT TREE — AND THE CEILING

Rule-5 order unchanged: (1) any level not plateaued → NOT A RESULT; (2) triple not CONVERGING →
NOT A RESULT (value + triple printed); (3) CONVERGING → inside ±5 % band = **GATE REACHED**,
outside = **GATE FAIL**; a fired demote-only secondary (observed order p ∉ [0.5, 2.5], or fine
GCI > 0.15) turns a would-be reach into GATE FAIL. GCI at Fs = 1.25.

**CEILING = GATE REACHED, and the comparator contains no code path that prints PASS.** Per the
carried §21.2 model-sameness ruling: the reference is an **inviscid quasi-1D** analytical shock
location and the run is a **viscous 2-D Navier-Stokes** solve — model-sameness DIFFERENT, so
PASS is unreachable and GATE REACHED is the ceiling. (This is the §12.2 grounding the supervisor
asked be stated rather than over-claimed: an exact-vs-code-to-code / model-different reference
caps at GATE REACHED.)

## 6. COST (rule 12)

Basis is **MEASURED** for `rhoPimpleFoam` (unlike R6/R7, which had no completed density-based
run): R5 ran all three levels to End — L1 3.1 / L2 22.6 / L3 171.583 core-min
(`VMFL046-R5/launcher.queue.out`, impulsive IC). R8 uses the start-from-rest IC; the L1
answer-blind smoke measured **7.68 core-min** (`SMOKE_rhoPimple_L1`, with box contention),
≈2.5× R5's impulsive L1. Point estimate applies a ~2.0 start-from-rest factor to R5's L2/L3.

| level | measured basis | R8 point estimate | per-level cap (≈3×) |
|---|---|---|---|
| L1 | 7.68 core-min (R8 start-from-rest smoke) | ~7.7 core-min | 24 core-min |
| L2 | 22.6 core-min (R5 completed) | ~45 core-min | 140 core-min |
| L3 | 171.583 core-min (R5 completed) | ~345 core-min | 1040 core-min |
| **total** | | **~398 core-min** | **1200 core-min (running total)** |

cost_basis: c7a.4xlarge $0.0513/core-h, owner-stated — **reported-by-owner, not measured**; $
derived. An overrun STOPS the run (rc 124). The est-vs-actual calibration (`docs/COST_CALIBRATION.md`)
is OWED at R8 completion. The comparator's W2 probe-length floor (0.25) is carried from R7
(fractions 1.0 / 0.9148 / 0.9921, all ≥ 0.25); R8's true basis is R5's three completed runs
(fraction 1.0 each), further above the floor — the carried constant is conservative and
gate-irrelevant.

**§2bb pre-flight:** `LADDER_PREFLIGHT.json` PASSES `check_ladder_preflight.py` (rc 0; 3 rungs,
one distinct solver path `rhoPimpleFoam|none|1` covered by the passing L1 smoke; deadlines =
per-level caps, sized from the measured per-step wall with the ≥1.25× margin holding with wide
room).

## 7. §12 — THE REAL SOLVER-WRITTEN PATHS (interface evidence)

Per level under the graded run root: `RUN_RC`, `log.rhoPimpleFoam`, `system/controlDict`
(rhoPimpleFoam, maxCo 0.5, endTime 0.08, the two writeIntervals {0.08, 5e-4}),
`system/fvSolution` (PIMPLE), `constant/fvOptions` (limitTemperature [150,2000]),
`system/blockMeshDict`, `0/T`, `<endTime>/{T,U,p}`, and
`postProcessing/centreline/<k·5e-4>/line_T_U.xy` for k = 1..160. The smoke `SMOKE_rhoPimple_L1`
is the on-disk proof this solver path writes these cleanly.

## 8. PARITY ASSERT (driver `run_vmfl046_r8.sh`, both directions, exit 7 on violation)

- DIRECTION 1 — seven physical inputs byte-identical to R7 (mesh, 0/T, 0/U, 0/p, thermo).
- DIRECTION 2 — the deliberate change present and registered: `fvSchemes`, `fvSolution`,
  `fvOptions` byte-identical to R5; `fvSchemes` DIFFERS from R7; `controlDict.template` carries
  `application rhoPimpleFoam` and `maxCo 0.5`; `fvOptions` carries `limitTemperature`; 11 files.

## 9. FREEZE CONDITIONS (rule 2 — amendment-legal until first compute)

This registration is freezable when, and only when: (i) the supervisor's §3 check-1 diff-read of
`grade_vmfl046_r8.py` vs `grade_vmfl046_r7.py` confirms the diff is off-gate only; (ii) the
comparator's disk `git hash-object` == the committed blob (grading path fixed at the
pre-registration commit); (iii) the graded run directory
`verification/runs/ansys_verification/VMFL046-R8/{L1,L2,L3}` **does not exist** at freeze (it
does not now). At launch (post-freeze, supervisor-gated on capacity): §2ba requires BOTH a live
monitor and a detached grader; §2bb pre-flight is on disk (§6). Nothing in this document may be
changed after first compute except as a dated addendum that cannot alter a gate, threshold, cap
or label.
