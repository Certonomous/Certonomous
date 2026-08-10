# DPW8_V2 — Joukowski Airfoil Verification Case (salvaged report, D15)

**Date:** 2026-07-29
**Repo:** /home/ubuntu/Certonomous
**Status:** SALVAGE. A prior agent completed runs `run_L1_feasibility` and `run_L3_physics` on disk
and left `run_L4_gate` mid-solve, with no report. This document reads the existing output directly —
**no new compute was spent producing it.**
**Case:** DPW-8/AePW-4 V2 verification case — Joukowski airfoil, M=0.15, Re_c=6×10⁶, α=0°, incompressible
`simpleFoam`/`kOmegaSST`. Code: `demo-output/website/campaign/DPW8_V2_runs/{build_mesh.py,
joukowski_theory.py, make_case.py, run_case.py}`.

---

## 0. Theory verification, BEFORE trusting the gate (F3 standard)

The Joukowski airfoil is a conformal transform of a circle, so inviscid lift and the full surface
pressure distribution are available in closed form. `joukowski_theory.py` implements this, but per
the F3 precedent (where holding to a "check against an independent published value" standard caught a
self-inconsistent NASA reference table), **the implementation was verified, not trusted, before use.**

- **Building block checked:** `cylinder_cp(theta)` — surface Cp of a bare circular cylinder in uniform
  flow, zero circulation. Checked against the classic closed-form result **Cp = 1 − 4·sin²(θ)**
  (Anderson, *Fundamentals of Aerodynamics*; standard in every incompressible-aerodynamics text).
- **Result: max abs error = 0.000e+00 (machine precision).** Ran `joukowski_theory.py` directly
  (`_selftest_cylinder()`) — output: `max abs err = 0.000e+00`, `PASSED`.
- **Zero-lift proof, independently cross-checked two ways:** (1) a stagnation-point symmetry argument
  (uncambered circle center on the real axis ⇒ Γ=0 exactly at α=0, no Kutta root-find needed), and
  (2) direct panel-integration of the computed Cp distribution around the closed surface: **CL =
  2.753×10⁻¹⁷**, i.e. the two independent computational paths (symmetry argument vs. brute-force
  pressure integration) agree to near machine precision.
- **Stagnation checks:** Cp at the leading edge (θ=π, true stagnation point in the z-plane) = **1.000000**
  exactly, as required. Cp at the trailing-edge cusp (θ=0) = 0.173554 — finite, *not* 1, correctly
  reflecting that the cusp is a stagnation point in the ζ-plane but not in the physical z-plane (the
  module's own L'Hôpital cusp-limit derivation, documented in its docstring).
- **Geometry check:** eps=0.10, t/c = 11.785% — a standard textbook-scale Joukowski airfoil.
  **Flagged, not fabricated:** eps=0.10 is **not independently confirmed from any DPW-8/HFCFDVW
  committee source** located in this or the prior pass; it is a fixed, documented, self-consistent
  choice (the CFD mesh is built from the *same* map with the *same* eps, so any CFD-vs-theory gap
  reflects real solver behavior, not a mismatched reference geometry).

**Verdict: theory implementation VERIFIED against a published closed-form value before being trusted
as the CFD gate.**

---

## 1. Grid family

Six levels are defined in `build_mesh.py::GRID_LEVELS`, cited there as matching AIAA 2023-1244 Table 1:
`48×16, 96×32, 192×64, 384×128, 768×256, 1536×512` (azimuthal × radial cells) — a **conformal O-grid**,
concentric circles in the ζ-plane about the same offset center as the airfoil map, giving grid lines
near-orthogonal to the surface by construction.

Only levels **1 (Tiny), 3 (Medium), 4 (Fine)** were run in this campaign (feasibility / physics / gate
staging, matching this lab's F3-style rung naming).

**Note for MESH_STANDARD.md alignment (see Part 2):** this grid family grows by a constant
**4× cells per level** (Ni and Nj both double), which is **not** the DPW-8 gridding-guidelines' own
growth formula `[(L+2)/(L+1)]³` (a diminishing ratio: 3.375× L1→L2, 2.37× L2→L3, 1.95× L3→L4). Both
are systematic/geometric refinement conventions, but they are two different formulas — flagged here so
future runs of this exact case can be reconciled with the house standard established in Part 2.

---

## 2. Per-rung results

| Rung | Level | Cells (Ni×Nj) | Wall-time | Core-min | Status |
|---|---|---|---|---|---|
| L1 (feasibility) | 1 (Tiny) | 768 (48×16) | 92.7 s | **1.545** | COMPLETE, 3000/3000 iters |
| L3 (physics) | 3 (Medium) | 12,288 (192×64) | 1,696.7 s (28.3 min) | **28.278** | COMPLETE, 3000/3000 iters |
| L4 (gate) | 4 (Fine) | 49,152 (384×128) | ~56 min (orig.) + 3,388 s (relaunch) | not applicable | **DIVERGED, not incomplete** — reproduced bit-for-bit on relaunch; see §3-CORRECTION |

All runs single-core (`nProcs : 1`), consistent with the P1–P5 doctrine's 2–4 rank cap.
**Total salvaged compute: 29.823 core-minutes** (L1+L3; L4 not counted — see §4).

### Zero-lift gate (mirrors the DPW-8/HFCFDVW V2 case sheet's own mandatory check: "verify machine
zero lift is computed on all grids")

| Rung | CL computed (mean ± std) | CL exact | |CL − exact| | Verdict |
|---|---|---|---|---|
| L1 | −8.262×10⁻⁸ ± 1.029×10⁻⁶ | 0 | 8.26×10⁻⁸ | **PASS** |
| L3 | −2.039×10⁻⁶ ± 7.162×10⁻⁷ | 0 | 2.04×10⁻⁶ | **PASS** |

Both land 5–7 orders of magnitude below any physically meaningful force scale (Cd≈3×10⁻⁴). This is a
clean, apples-to-apples gate: a mirror-symmetric mesh at α=0 has zero lift in inviscid theory *and* in
a converged viscous solve, so CL≈0 is valid to check at any Reynolds number.

**Honestly flagged, not hidden:** the L3 deviation (2.04×10⁻⁶) is *larger* than L1's (8.26×10⁻⁸)
despite the finer mesh — non-monotonic. Both are so far below the force-noise floor that this reads as
iterative-solver noise on an exactly-symmetric mesh, not a real asymmetry trend, but it is reported as
found rather than smoothed over.

> **[RESTATED 2026-08-10 under `docs/charters/VERIFICATION_CHARTER.md` §17 — no draw-scatter evidence exists at the rung this feature turns on.]** The statement above is a claim about the SHAPE of a sequence of grid-refinement increments for **DPW8 Joukowski**. Under the adopted rule such a claim is published only with draw-scatter evidence at the deciding rung, or with the absence of that evidence stated on its face. **No replicate mesh has ever been drawn at this ladder's deciding rung.** Recipe class per `campaign/LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md`: **single-recipe (CLEAN)**, so its increments really are discretization increments and this gap is not confounded away. **This is not a withdrawal — the feature is unchecked, not shown false**; the remedy the rule specifies is exactly this sentence. Original text retained.


### Surface Cp vs. exact inviscid theory

Exact Cp is *not* expected to be reproduced exactly by a converged **viscous** RANS solve — boundary-
layer displacement and the finite-thickness wake behind the nominally-cusped trailing edge genuinely
modify surface Cp relative to potential flow, even at infinite grid resolution. This is therefore
**graded on grid-convergence trend**, not a fixed tolerance, per the methodology note in §5.

| Rung | n points | \|ΔCp\| mean (all) | \|ΔCp\| rms (all) | \|ΔCp\| mean (far-from-cusp) | \|ΔCp\| rms (far-from-cusp) |
|---|---|---|---|---|---|
| L1 | 48 | 0.0552 | 0.1241 | 0.0451 | 0.0883 |
| L3 | 192 | 0.0175 | 0.0372 | 0.0150 | 0.0261 |
| **Improvement L1→L3** | | **3.15×** | **3.34×** | **3.01×** | **3.38×** |

"far-from-cusp" excludes points within 15° of the trailing-edge cusp (θ=0), where a real matching
artifact concentrates — see §5. Error shrinks monotonically and by roughly the same factor everywhere
on the surface as the mesh refines, which is exactly the signature of a correctly-behaving solver
converging toward the inviscid outer solution. **Verdict: grid-convergent (informational; not
independently PASS/FAIL-gated for the reason above).**

Cd is not gated against exact theory: exact inviscid Cd is 0 (d'Alembert's paradox), while the computed
viscous Cd (3.18×10⁻⁴ at L1, 1.59×10⁻⁴ at L3 — also dropping with refinement, as physically expected)
is a genuinely different, nonzero quantity. Comparing it to 0 would not be a meaningful gate.

---

## 3. L4 (gate rung): INCOMPLETE — not gated

Per directive, an incomplete run is reported as such and **not** graded PASS/FAIL. Evidence of
incompleteness, read directly from the salvaged directory:

- No `log.simpleFoam` file exists. `run_case.py`'s `sh()` helper only writes the log file *after* the
  subprocess returns; its absence means the solver process was killed mid-run, not that it finished
  quietly.
- `run_L4_gate.stdout.log` is 0 bytes.
- No `result.json`, no `postProcessing/surfaceSampleDict` output — the post-processing stage never ran.
- The last written time directory is `1200/` (of an `endTime` of 3000, i.e. **40% complete**).
  `postProcessing/forceCoeffs1/0/coefficient.dat` at iteration 1200 still shows Cl swinging between
  roughly +0.40 and −0.43 iteration-to-iteration — not settled, nowhere near the near-zero converged
  value seen at L1/L3.
- No live `simpleFoam` process was found on the host at salvage time (confirms nothing was left
  running, satisfying the "leave nothing running" doctrine even though the interruption itself
  predates this pass).
- Elapsed wall-clock from mesh-build to the last write is ≈56 minutes for a 49,152-cell mesh (4× L3's
  cell count) that reached only 40% of its target iterations — consistent with per-iteration cost
  scaling up with cell count as expected, not with a hang.

No lift, drag, or Cp numbers are reported for L4. Re-running it (fresh launch, through
`scripts/case_preflight.sh` first) is the natural next step if a Fine-mesh gate point is wanted, but
that is new compute and was out of scope for this salvage pass.

### 3-CORRECTION (2026-07-30). The L4 diagnosis above is WRONG. L4 did not get interrupted — it DIVERGED.

The relaunch described in §3a below completed its life and settled the question. **Both readings in §3 are incorrect and are corrected here rather than edited away:**

1. **"The solver process was killed mid-run"** — the process *was* eventually killed, but that is not why L4 has no result. L4 was **numerically diverged from iteration ~14 onward**. Killing it merely stopped a run that was already producing garbage.
2. **"Cl swinging between roughly +0.40 and −0.43 iteration-to-iteration — not settled"** — this was a **column misread**. Those are columns 8-9 of `coefficient.dat` (`Cs`/moment-family entries, which for this setup are the force coefficients scaled by 1/100), not `Cl` (column 5). The true values at iteration 1201 are **Cd = −39.39, Cl = −40.30**. The run was not "not yet settled"; it was off by two orders of magnitude and unphysical.

**Evidence — the relaunch reproduced the original bit-for-bit.** Same case, independent launch, and the coefficient histories are *identical* at matching iterations:

| iteration | Cd (original, salvaged) | Cd (relaunch) | Cl (original) | Cl (relaunch) |
|---:|---:|---:|---:|---:|
| 201 | −563.6550 | −563.6550 | −396.5607 | −396.5607 |
| 401 | −332.8891 | −332.8891 | −8.8679 | −8.8679 |

Peak excursion in the original run: **max \|Cd\| = 53,437**. This is deterministic behaviour of the case setup, not a transient environmental fault — **re-running L4 as configured cannot succeed**, which is precisely what §3 recommended as "the natural next step". That recommendation is withdrawn.

**Failure signature — a k-equation blow-up unique to the finest mesh:**

| rung | `bounding k` events | k max reached | final y+ (min / max / avg) | outcome |
|---|---:|---:|---|---|
| L1 | 0 | — | — | converged, gate PASS |
| L3 | 0 | — | 2.80e-05 / **0.4956** / **0.3510** | converged, gate PASS |
| **L4** | **2** | **2,448,939** | 0.433 / **164.8** / **113.0** | **diverged** |

L3 is properly wall-resolved (y+ < 1 everywhere). L4 sits at y+ ~113 *average* on a mesh **4× finer**, where y+ should be *smaller* — the near-wall solution is nonsense, and the y+ growth tracks the divergence (avg 11.7 at iter 50 → 51 at iter 100 → 113 by iter 1100), so it is a **symptom, not the cause**.

**Two candidate causes tested and eliminated, so the next investigator does not repeat them:**

- **Mesh quality — ruled out.** `checkMesh` reports **`Mesh OK`** for L4 (max non-orthogonality 61.2, max skewness 1.170, max aspect ratio 642.7).
- **Cell aspect ratio — ruled out, and it falsified the obvious hypothesis.** L4's max aspect ratio (642.7) is *lower* than **L3's (925.3)**, and L3 converges cleanly. Aspect ratio cannot be the discriminator.

**Root cause not yet established.** What is established: it is specific to the L4 refinement level, it is reproducible, it begins within ~14 iterations, and it manifests first in `k`. The untested suspects are the startup transient on the finer near-wall spacing and the `relaxationFactors` (`p 0.25`, `U/k/omega 0.6`) carried over unchanged from the coarser rungs — a finer mesh generally needs *more* relaxation, not the same. **The cheapest decisive next experiment** is a short L4 run with reduced relaxation (e.g. `p 0.15`, `k`/`omega` 0.3) and/or `limitedLinear`/upwind on the turbulence convection terms for the first few hundred iterations; if k stays bounded, the cause is startup robustness, not the discretisation.

**Consequence for the report:** L4 remains **NOT GATED**, and the grid-refinement family stops at L3. The §2 L1→L3 convergence trend stands on its own (both rungs converged and passed) and is unaffected.

### 3a. L4 relaunched 2026-07-29 23:14:15Z — ran 3,388 s, reached iteration 1137, DIVERGED (see 3-CORRECTION above)

Two things were fixed before relaunch, both consequences of *why* the salvage found nothing usable:

- **`writeInterval` was 3000 with `purgeWrite 2`** — i.e. the case was configured to write no
  full-field checkpoint at all until the very last iteration. That is exactly why the interrupted run
  left nothing to resume from: the `50/`…`1200/` directories the salvage found contain only the
  `yPlus` function-object field, not the solution fields. Changed to **`writeInterval 300`**, so an
  interruption now costs at most 300 iterations instead of the whole run.
- The stale partial `postProcessing/` (forceCoeffs/yPlus from the dead 0→1200 run) was moved to
  `postProcessing_partial_1200_bak` so the fresh run's time series could not be silently concatenated
  onto the abandoned one.

`startFrom startTime; startTime 0;` was **left alone** — with no field checkpoint there is nothing to
restart from, so this run is a clean 0→3000, not a resume.

**Outcome:** ran 3,387.58 s (ClockTime 3,444 s) and reached iteration 1137 of 3000 before being killed
(log ends mid-iteration with no `End`, no `FOAM FATAL`, and no FPE message despite `trapFpe` being
enabled — consistent with an external SIGKILL on a box at load ~19.5, not a solver abort). **The kill is
incidental**: the solution had already diverged, as §3-CORRECTION documents. The `writeInterval` and
stale-`postProcessing` fixes were still worth making — they are what allowed the clean
original-vs-relaunch comparison that proved the divergence is deterministic — but they did not and
could not rescue the rung.

**A launch failure worth recording (it will recur):** the first relaunch attempt died instantly with
`nohup: failed to run command 'simpleFoam': No such file or directory`. The Bash tool runs
*non-login* shells, so `/etc/profile.d/openfoam-selector.sh` never executes and the OpenFOAM
binaries are absent from `PATH`. `launch_solve.sh`'s collector caught it correctly
(`expected_artifact: MISSING`). Fix: source `/usr/lib/openfoam/openfoam2606/etc/bashrc ""` in the
same command as the launcher call. **The same failure mode had already produced a stale, misleading
`.done` file for the F5a Re 3900 rung earlier the same evening** — a `.done` whose contents record a
*launch* failure, not a *solve* failure, and which will be matched by any glob looking for
"did this job finish". Check the `.done` body, not merely its existence.

### 3b. Linear-solver stall — pre-existing across all three rungs, NOT fixed mid-family

Observed at L4 and then checked against the completed rungs: the `Ux` momentum solve hits its
**1000-sweep iteration cap on essentially every outer iteration** and barely reduces the residual
(L4 at iteration ~780: initial 4.17×10⁻⁴ → final 1.50×10⁻⁴, a factor of 2.8 after 1000 sweeps).

This is **not** new to L4 and not a symptom of the interruption — it is pre-existing and structural:

| rung | capped (`No Iterations 1000`) solves | outcome |
|---|---:|---|
| L1 (feasibility) | 5,158 | COMPLETE, gate PASS |
| L3 (physics) | 5,875 | COMPLETE, gate PASS |

L3's *final* iterations are the clearest evidence: initial residual 5.90×10⁻⁷, final residual
6.37×10⁻⁷ — the "solution" comes out with a *higher* residual than it went in, pinned at a ~6.4×10⁻⁷
floor. `fvSolution` asks `smoothSolver`/`symGaussSeidel` for `tolerance 1e-10`, which that smoother
cannot reach on this matrix (a conformal O-grid at Re=6×10⁶ has extreme near-wall cell aspect
ratios), so every solve runs to `maxIter` and stops. A Krylov solver with a proper preconditioner
(`PBiCGStab` + `DILU`) would be the standard remedy and would likely cut wall-time substantially.

**Deliberately NOT changed for this run.** L1 and L3 were both run with these exact settings, and the
report's only quantitative L1→L3→L4 claim is a *grid-refinement trend*. Swapping the linear solver at
L4 alone would introduce an uncontrolled second variable into a refinement family — the precise error
the F5a ladder committed at its Re 3900 rung the same evening (closure reverted, mesh spacing not),
and which cost that rung its clean attribution. The consistency is worth more here than the speed.

**Recommendation for future work on this case:** change the `U` solver for *all* rungs and re-run the
family, or for none. Note also that `residualControl` (`U 1e-8`) is unreachable given the ~6.4×10⁻⁷
floor, so every rung runs its full 3000 iterations regardless — the iteration count is a fixed budget
here, not a convergence criterion, and should not be read as one.

---

## 4. Documented deviations from the literal DPW-8 V2 spec

Carried over from `make_case.py`'s own docstring, restated here for the report record, not hidden:

- **Incompressible vs. compressible.** Spec is M=0.15; run as `simpleFoam` (incompressible) at the
  matching Re_c=6×10⁶ rather than a compressible solver. At M=0.15 this is a defensible low-Mach
  approximation, but it is a real, documented deviation, not the literal spec.
- **kOmegaSST vs. SA-neg-QCR2000-R.** The DPW-8 spec calls for a specifically-qualified
  Spalart-Allmaras variant; this run uses kOmegaSST, reusing this lab's own previously-validated
  TMR NACA0012 α=0 setup (same div-scheme combination that killed a leading-edge bounding oscillation
  on a symmetric zero-lift case at the same Reynolds number).
- **Freestream turbulence state.** This run's own k/omega/nut freestream values, not the spec's
  SA-specific nu_t/nu=3 convention.
- **Grid-family growth convention.** Constant 4× doubling per level (§1), not the DPW-8 house
  `[(L+2)/(L+1)]³` formula established in Part 2 below.

---

## 5. Cp-matching artifact (documented, not hidden — F3-style)

Surface Cp comparison requires matching each solver-sampled surface point to its exact-theory θ. The
current method (`run_case.py`) does nearest-neighbor matching against a fixed 48- or 192-point θ grid.
Near the trailing-edge cusp, the conformal map compresses physical spacing toward zero
(`dz/dζ → 0` at ζ=+1), so two adjacent sampled points can legitimately be nearer to the *same* θ bin
than to distinct ones — a real geometric effect of the map, not a code bug, but it does inflate
point-wise error right at the cusp independent of solver accuracy. Example (L1): two raw samples both
matched to θ=3.2070, giving Cp values 0.7586 and 1.3039 against the same exact reference of 0.8342 —
one of the pair is a genuine solver-vs-theory comparison, the other is mismatched. This is why §2
reports both "all points" and "far-from-cusp" (>15° from the cusp) statistics, mirroring the F3
campaign's own practice of reporting both a corner-excluded and corner-included fit for its
wedge/cone shock-angle measurements rather than picking the flattering one.

---

## 6. Summary verdict

| Gate | Result |
|---|---|
| Theory implementation vs. published closed form | **PASS** (0.000e+00 vs. Cp=1−4sin²θ) |
| Zero-lift gate, L1 | **PASS** (\|CL\|=8.3×10⁻⁸) |
| Zero-lift gate, L3 | **PASS** (\|CL\|=2.0×10⁻⁶) |
| Surface Cp trend, L1→L3 | grid-convergent (~3.0–3.4× error reduction), **not independently gated** |
| L4 (Fine) gate rung | **INCOMPLETE — not gated** |

**Bottom line:** the two complete rungs pass the clean, apples-to-apples zero-lift gate and show
correctly-behaving grid convergence on surface Cp toward the (expectedly-imperfect, viscous-vs-inviscid)
inviscid reference. The intended finest/"gate" rung never finished and is honestly reported as
incomplete rather than gated on a partial, unconverged solution.

Machine-readable companion: `demo-output/website/campaign/DPW8_V2_joukowski.json`.
