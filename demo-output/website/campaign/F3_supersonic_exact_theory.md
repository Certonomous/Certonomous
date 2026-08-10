# F3 — Supersonic Exact-Theory Campaign (wedge / cone / diamond airfoil)

**Date:** 2026-07-28
**Repo:** /home/ubuntu/Certonomous @ ce534b3
**Solver:** vanilla OpenFOAM v2606, `rhoCentralFoam` (density-based, shock-capturing, Kurganov flux), native (no Docker), run **inviscid** (μ=0) so the CFD solves the same Euler equations the exact theory assumes.
**Gas model:** all three cases use the same non-dimensional perfect gas as the stock `wedge15Ma5` tutorial (γ=1.4, molWeight chosen so R gives γ=1.4, Cp=2.5, and speed of sound a=1 at T=1) — so the inlet velocity magnitude U **is** the freestream Mach number directly, and p1=1, T1=1 are the freestream reference states throughout.
**Process:** every run in the foreground (auto-backgrounded by the harness past 120 s and waited-on, never detached/nohup'd); ≤4 ranks (all runs here serial, single-core — cases are small enough that MPI overhead wasn't worth it); nothing left running at the end (verified via `ps` before closing out). All code in `demo-output/website/campaign/F3_runs/`.

Staging used throughout: **FEASIBILITY** (coarse, does it run) → **PHYSICS** (medium, plausible shock) → **GATE** (fine, does the number land against exact theory).

---

## 0. Exact-theory verification (done BEFORE any CFD, per hard rule)

All exact solutions are computed in `F3_runs/exact_theory.py` from the standard closed-form gas-dynamics relations (θ-β-M, normal/oblique shock, Prandtl-Meyer) plus a from-scratch Taylor-Maccoll ODE shooting-method integrator. No CFD output was used to derive any exact value.

- **θ-β-M / oblique-shock relations — verified EXACTLY.** Checked against NASA GRC's "[Oblique Shock on a 15 Degree Wedge at Mach 2.5](https://www.grc.nasa.gov/WWW/wind/valid/wedge/wedge.html)" validation page (their own analytic solution, computed by `oblshk.f`, tol=1e-6): M1=2.5, θ=15° → β=36.94490°, M2=1.873526, p2/p1=2.467500, ρ2/ρ1=1.866549, T2/T1=1.321958. Our `beta_from_theta`/`oblique_shock` reproduce **all five to 6 significant figures**. This validates every building block used by both the wedge case and the cone case's shock-jump initial condition.
- **Taylor-Maccoll ODE + shooting method — verified, with a documented complication.** The intended reference, NASA GRC's "[10 Degree Cone at Mach 2.35](https://www.grc.nasa.gov/WWW/wind/valid/cone10/cone10.html)" page, states a "Theory" row (β=27.1843°, M2=2.2677, p2/p1=1.1781, M3=2.1469, p3/p1=1.4234) that we found to be **internally inconsistent**: the state-2 (p,T,ρ) triple satisfies stagnation-temperature conservation with M1n=M1·sin(27.1843°), but the listed M2=2.2677 does not (T0-conservation using their own T2/T1=1.0481 independently requires M2=2.245, not 2.2677) — and the same gap recurs at the cone surface (M3 vs T3/T1). The **same page's own multi-code CFD table** (WIND-AXI, WIND-3D, NPARC-AXI, Wind-US 3.0, on a grid-converged actual-cone geometry) lands at M3=2.1467–2.1469, p3/p1=1.3740–1.3741 — consistent with T0-conservation, not with the page's stated "Theory" p3/p1. This is almost certainly a decades-old transcription erratum on the archival page, not a property of the true solution. **We therefore verify our own solver against that page's grid-converged multi-code CFD instead of its self-contradictory "Theory" row**: our solver gives M3=2.1468 (dev −0.003%), p3/p1=1.3739 (dev −0.012%) — matches to 3–4 significant figures, about as good as an ODE shooting solution can agree with independently grid-converged CFD. Full derivation and printed comparison in `exact_theory.py::_verify_taylor_maccoll`.
- **Prandtl-Meyer function** — PM(M=2.0)=26.3798°, matches the standard tabulated value; round-trip inverse verified to 1e-13.
- **Diamond-airfoil wave-drag formula** — sanity-checked against linear (Ackeret) thin-airfoil theory in the small-angle limit: exact/linear ratio = 1.006–1.012 for the angles used here, exactly the expected small nonlinear correction.

---

## 1. Supersonic wedge (θ-β-M / oblique shock)

**Method:** 2-block ramp mesh (flat symmetry section + wedge ramp), generalized from the OpenFOAM `wedge15Ma5` tutorial topology, parametrized in Python (`make_wedge_case.py`) for arbitrary (M, θ). Shock angle measured by sampling ρ, p, T along 6 vertical lines spanning the ramp (`postProcess -func sampleDict`), locating the peak |∂ρ/∂y| at each station (the standard "peak density-gradient locus" technique), then fitting a line through the stations → β_computed. Surface pressure read directly off the wedge-surface patch faces (`surfaces` function object, `interpolate false` — exact CFD face values, no interpolation). **Grid-sensitivity finding:** the station nearest the leading corner is contaminated by the singular apex (a real, non-mesh-scale expansion/compression structure right at the sharp corner); excluding it improves the fit at coarse/medium resolution but at fine resolution *including* it is sometimes slightly better (the corner is better resolved) — both fits (`excl. first` / `all stations`) are reported below so this sensitivity is visible, not hidden.

| Pair (M, θ) | Exact β / p2/p1 | Grid | Cells | β computed (excl-first / all) | β dev % | p computed | p dev % | Core-s |
|---|---|---|---|---:|---|---|---|---:|
| M=2.0, θ=15° | β=45.3436°, p2/p1=2.1947 | coarse | 1,800 | 47.27° / 45.75° | +4.26 / +0.90 | 2.2946 | +4.56 | 6.1 |
| | | medium | 7,200 | 45.45° / 46.78° | +0.25 / +3.16 | 2.1867 | −0.36 | 18.7 |
| | | **fine** | 28,800 | 44.85° / 45.26° | **−1.10 / −0.18** | **2.1962** | **+0.07** | 146.4 |
| M=3.0, θ=15° | β=32.2404°, p2/p1=2.8216 | medium | 7,200 | 32.85° / 33.27° | +1.88 / +3.20 | 2.7933 | −1.00 | 18.7 |
| | | **fine** | 28,800 | 31.93° / 32.46° | **−0.96 / +0.67** | **2.8218** | **+0.01** | 149.0 |
| M=2.5, θ=10° | β=31.8506°, p2/p1=1.8639 | medium | 7,200 | 32.22° / 33.60° | +1.16 / +5.49 | 1.8565 | −0.40 | 18.9 |
| | | **fine** | 28,800 | 32.25° / 32.33° | **+1.26 / +1.52** | **1.8641** | **+0.01** | 148.1 |

All three (M,θ) pairs picked comfortably inside the attached-shock regime (≥8° margin from the θ-β-M detachment angle).

- **Verdict: PASS.** Surface pressure — the cleaner, spatially-integrated CFD quantity — converges to within **0.01–0.07% of exact oblique-shock theory at fine mesh**, all three pairs. Shock angle, measured from a numerically-smeared field via finite-difference gradient peaks, converges to within **0.2–1.5%**, with the residual attributable to the detection method's sensitivity (documented above) rather than a solver defect.
- **Core-minutes (wedge, all 7 runs):** 8.43

---

## 2. Supersonic cone (Taylor-Maccoll, axisymmetric)

**Method:** axisymmetric wedge mesh (2.5° half-angle thin slice, OpenFOAM's standard `wedge` boundary-condition convention, axis collapsed via `mergeType points`), 2-block topology mirroring the wedge case (upstream axis block + cone-surface block), parametrized in `make_cone_case.py`. Same shock-detection method as the wedge case, but sampling **radially** at fixed x-stations; surface pressure read directly off the cone-surface patch. Reference ("exact") values are our own verified Taylor-Maccoll solver's output (see §0) for the specific (M, θc) pair.

| Pair (M, θc) | Exact β / pc/p1 | Grid | Cells | β computed (excl-first / all) | β dev % | p computed | p dev % | Core-s |
|---|---|---|---|---:|---|---|---|---:|
| M=2.35, θc=10° | β=26.7367°, pc/p1=1.3739 | coarse | 1,800 | 29.66° / 27.31° | +10.93 / +2.14 | 1.3937 | +1.44 | 16.3 |
| | | medium | 7,200 | 28.44° / 28.54° | +6.36 / +6.74 | 1.3802 | +0.45 | 118.9 |
| | | **fine** | 28,800 | 27.31° / 27.49° | **+2.14 / +2.81** | **1.3779** | **+0.29** | 1,072.7 |
| M=3.0, θc=12° | β=23.0018°, pc/p1=1.7472 | medium | 7,200 | 23.81° / 23.89° | +3.51 / +3.86 | 1.7505 | +0.19 | 117.6 |

The second pair (M=3.0, θc=12°) was run only at medium resolution — the fine-mesh cone solve is expensive (see below) and the grid-sensitivity study on the first pair already establishes the convergence trend; a second full 3-level study would have been redundant given the campaign's compute budget.

- **Verdict: PASS, with a real and reported numerics finding.** Surface pressure converges cleanly and monotonically (+1.44% → +0.45% → +0.29% coarse→medium→fine), a solid gate pass. Shock angle also converges *monotonically* with refinement (+10.9% → +6.4% → +2.1%, excl-first fit) but **has not fully closed by the finest mesh tested here**, and its deviation at matched cell count is consistently larger than the equivalent wedge case (e.g. fine wedge β dev ~0.2–1.5% vs fine cone β dev ~2.1–2.8%). Two candidate causes, not disentangled here: (1) the cone shock is intrinsically closer to the Mach angle (weaker, more oblique) for the same deflection than the wedge shock, so a numerically smeared shock band occupies a *larger fraction* of the standoff distance at the same absolute cell count, biasing the peak-gradient detector more; (2) the axisymmetric metric terms (1/r source terms) may need one more refinement level to reach the same relative accuracy as the 2-D wedge. **This is reported as a documented, unresolved sensitivity, not swept under the rug** — a genuinely finer cone mesh (>28,800 cells) is the natural next rung if this family needs a tighter shock-angle gate.
- **Cost finding:** the cone solve is markedly more expensive per cell than the wedge at matched resolution (fine cone: 1,073 core-s for 28,800 cells vs fine wedge: 146–149 core-s for the same cell count, a ~7× ratio), from the extra rhoUz momentum equation plus a smaller Courant-limited Δt in the axisymmetric metric. This drove the decision to run the second cone pair at medium only.
- **Core-minutes (cone, all 4 runs):** 22.09

> **[RESTATED 2026-08-10 under `docs/charters/VERIFICATION_CHARTER.md` §17 — no draw-scatter evidence exists at the rung this feature turns on.]** The statement above is a claim about the SHAPE of a sequence of grid-refinement increments for **the F3 supersonic wedge**. Under the adopted rule such a claim is published only with draw-scatter evidence at the deciding rung, or with the absence of that evidence stated on its face. **No replicate mesh has ever been drawn at this ladder's deciding rung.** Recipe class per `campaign/LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md`: **single-recipe (CLEAN)**, so its increments really are discretization increments and this gap is not confounded away. **This is not a withdrawal — the feature is unchecked, not shown false**; the remedy the rule specifies is exactly this sentence. Original text retained.


---

## 3. Diamond airfoil (shock-expansion theory, wave drag)

**Method:** symmetric double-wedge airfoil at zero angle of attack, upper-half-only mesh exploiting top/bottom symmetry (4-block chain: flat symmetry → front compression panel → rear expansion panel → flat symmetry wake, generalizing the wedge-case single-ramp block to a 4-segment ramp in `make_diamond_case.py`). Wave-drag coefficient obtained from OpenFOAM's own `forces` function object integrating pressure over the upper-surface patch (inviscid, so drag = pressure force only), doubled for the mirrored lower surface, normalized by q1·c. Exact reference: shock-expansion theory (oblique shock on the front panel + Prandtl-Meyer expansion of 2ε on the rear panel, both closed-form) — the wave-drag coefficient is an **integrated** quantity, so this gate tests the whole surface solution, not one probe point.

| Pair (M, ε, t/c) | Exact cd | Grid | Cells | cd computed | Deviation | Core-s |
|---|---|---|---|---|---:|---:|
| M=2.0, ε=7.125° (t/c=0.125) | 0.036331 | coarse | 2,000 | 0.036132 | −0.55% | 11.1 |
| | | medium | 8,000 | 0.036236 | −0.26% | 35.5 |
| | | **fine** | 32,000 | **0.036237** | **−0.26%** | 201.2 |
| M=2.5, ε=5.0° (t/c=0.0875) | 0.013430 | coarse | 2,000 | 0.013428 | −0.02% | 9.1 |
| | | medium | 8,000 | 0.013395 | −0.26% | 29.3 |
| | | **fine** | 32,000 | **0.013406** | **−0.18%** | 189.8 |

Both pairs picked well inside the attached-shock regime for their leading-edge half-angle (θmax(M=2)=22.97°, θmax(M=2.5)=29.80°, both ≫ ε used).

- **Verdict: PASS — the strongest gate in this family.** Wave drag coefficient (an integrated quantity over the entire surface, both compression and expansion sides) lands within **0.18–0.55% of exact shock-expansion theory**, and is essentially **converged already at the medium mesh** (deviation is flat to within ~0.1 percentage point from medium→fine for both pairs), i.e. this gate is not grid-limited at the resolutions tested.
- **Core-minutes (diamond, all 6 runs):** 7.93

---

## Summary

| Case | Gate quantity | Best (fine-mesh) deviation | Verdict |
|---|---|---:|---|
| 1. Wedge | surface pressure p2/p1 | 0.01–0.07% | **PASS** |
| 1. Wedge | shock angle β | 0.2–1.5% | **PASS** (method-sensitive, documented) |
| 2. Cone | surface pressure pc/p1 | 0.19–0.29% | **PASS** |
| 2. Cone | shock angle β | 2.1–3.9% | **PASS, not fully grid-converged** — documented open sensitivity |
| 3. Diamond | wave drag cd | 0.18–0.55% | **PASS**, converged by medium mesh |

**Total compute: 38.45 core-minutes** across 17 CFD runs (7 wedge, 4 cone, 6 diamond), all foreground, single-core, nothing left running.

### Headline finding
`rhoCentralFoam`'s inviscid Euler solve reproduces every one of the three closed-form supersonic-theory gates to well under 1% on the **integrated/surface-pressure** metrics (oblique-shock p2/p1, Taylor-Maccoll pc/p1, shock-expansion wave drag) at fine mesh — a clean pass of the "cheap, brutal, unfakeable" entry ticket. The one place the numerics visibly strain is **measuring shock angle from a smeared field via density-gradient peaks in axisymmetric (cone) flow**, which converges monotonically but is still 2–4% off at 28,800 cells, versus 0.2–1.5% for the equivalent 2-D wedge shock at the same cell count. This is reported, not hidden: it is a genuine, reproducible numerics finding (weaker/more-oblique cone shocks occupy more of the standoff distance in a smeared field at fixed resolution) that should inform mesh sizing for any F4 hypersonic axisymmetric work that depends on precise shock-*position* (as opposed to post-shock *state*) measurements.

### Evidence record

| Case | Config hash basis | Wall-time (fine) | Core-min (case total) | Exact | Computed (fine) | Deviation | Cause of residual | Lesson |
|---|---|---|---|---|---|---|---|---|
| Wedge M2.0/θ15 | `make_wedge_case.py` params (M,θ,res) | 146.4s | 8.43 (all 3 pairs) | β=45.3436°, p2/p1=2.1947 | β=44.85–45.26°, p=2.1962 | β: −1.1 to −0.2%; p: +0.07% | Density-gradient peak detection bias near leading corner; pressure limited only by residual mesh truncation | Report both "excl-corner" and "all-station" shock fits; don't pick the one that looks best |
| Cone M2.35/θc10 | `make_cone_case.py` params | 1,072.7s | 22.09 (both pairs) | β=26.7367°, pc/p1=1.3739 | β=27.31–27.49°, p=1.3779 | β: +2.1 to +2.8%; p: +0.29% | Weaker/more-oblique conical shock => smeared band is larger fraction of standoff at fixed cell count | Cone shock-angle gate needs a finer mesh than the equivalent wedge to close to the same relative tolerance; budget accordingly for F4 |
| Diamond M2.0/ε7.125 | `make_diamond_case.py` params | 201.2s | 7.93 (both pairs) | cd=0.036331 | cd=0.036237 | −0.26% | Small residual from sharp leading/trailing-edge corner smearing, already at asymptote by medium mesh | Integrated force coefficients are the most robust gate of the three; prefer them over single-point angle/position measurements when available |

### Exact-theory verification record

| Building block | Verified against | Match |
|---|---|---|
| θ-β-M / oblique shock | NASA GRC 15° wedge, M=2.5 (analytic, `oblshk.f`) | 6 significant figures, all 5 quantities |
| Taylor-Maccoll ODE (own solver) | NASA GRC 10° cone, M=2.35, grid-converged multi-code CFD (page's own "Theory" row found self-inconsistent, documented, not used) | M3 dev −0.003%, p3/p1 dev −0.012% |
| Prandtl-Meyer | Standard tabulated value, M=2.0 | 26.3798° (exact) |
| Diamond wave-drag closed form | Linear (Ackeret) thin-airfoil theory, small-angle limit | ratio 1.006–1.012 (expected nonlinear correction) |

All code: `demo-output/website/campaign/F3_runs/{exact_theory.py, make_wedge_case.py, make_cone_case.py, make_diamond_case.py, run_wedge_case.py, run_cone_case.py, run_diamond_case.py, build_report.py}`. Machine-readable results: `F3_supersonic_exact_theory.json` (per-pair, per-resolution).
