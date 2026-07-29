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
| L4 (gate) | 4 (Fine) | 49,152 (384×128) | ~56 min elapsed (partial) | not applicable | **INCOMPLETE, 1200/3000 iters (40%)** |

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
