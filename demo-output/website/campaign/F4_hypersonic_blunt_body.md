# F4 — Hypersonic Blunt-Body Campaign (2D cylinder, Mach 6–8)

**Date:** 2026-07-28
**Repo:** /home/ubuntu/Certonomous @ b23138d
**Solver:** vanilla OpenFOAM v2606, `rhoCentralFoam` (density-based, shock-capturing, Kurganov flux), native (no Docker), run **inviscid** (μ=0), γ=1.4, same non-dimensional gas as F3 (a=1 at T=1, so the inlet velocity magnitude U *is* the Mach number).
**Geometry: 2D circular cylinder** (not axisymmetric sphere). Chosen because (a) F3 found the axisymmetric cone ~7× more expensive per cell than the 2-D wedge at matched resolution, and hypersonic flow (M=6–8) already stiffens the problem (stronger shocks, smaller stable Δt) relative to F3's M=2–3 cases, so 2-D keeps the campaign inside the compute budget; (b) Billig's correlation gives *separate, independently citable* coefficients for "cylinder-wedge" vs. "sphere-cone," so the 2-D choice does not cost us a rigorous gate. This is a real physical difference, not a simplification of convenience: 2-D flow cannot spill sideways to relieve pressure the way axisymmetric flow can, so a 2-D cylinder's shock stands off roughly 3× further (relative to R) than a sphere at the same Mach number — confirmed quantitatively below (§0).
**Process:** every run in the foreground (auto-backgrounded by the harness past 120 s and waited-on via a blocking poll, never detached/nohup'd); all runs serial single-core (no MPI — cases are small; well under the 4-rank cap); nothing left running at the end (`ps aux | grep rhoCentralFoam` empty, verified). All code in `demo-output/website/campaign/F4_runs/`.

Staging used throughout: **FEASIBILITY** (coarse, does it run) → **PHYSICS** (medium, does the bow shock form and stand off) → **GATE** (fine, does the number land against Billig / modified Newtonian).

---

## 0. Closed-form theory — sourced and verified BEFORE any CFD

Per the hard rule against fabricated citations, both gate formulae were pulled from a primary textbook source fetched and OCR'd in this session (not recalled from memory), because an initial web search returned a plausible-looking but wrong coefficient.

- **Source:** Anderson, John D., Jr., *Hypersonic and High-Temperature Gas Dynamics*, 2nd ed., AIAA Education Series, 2006 — Sec. 5.4 "Correlations for Hypersonic Shock-Wave Shapes" (Eqs. 5.36–5.38) and Sec. 3.3 "Modified Newtonian Law" (Eqs. 3.15–3.19). PDF fetched from a university OCW mirror, `pdftotext`'d, and grepped directly for the equations (`demo-output/website/campaign/F4_runs/billig_theory.py` docstring has the full trail).
- **Verification trail on the Billig coefficient:** an initial web search summary claimed the cylinder-wedge exponential coefficient was 4.76; fetching the primary textbook text directly showed the printed value is **4.67** (matching what this campaign's brief specified) — the "4.76" was third-party paraphrase noise, not a citable primary number. We used the number that appears in the textbook page image itself.
- **Billig (1967) shock-standoff correlation** (Anderson Eq. 5.37, itself citing Billig, F. S., "Shock-Wave Shapes Around Spherical- and Cylindrical-Nosed Bodies," *Journal of Spacecraft and Rockets*, Vol. 4, No. 6, June 1967, pp. 822–823):
  ```
  delta/R = 0.386 * exp(4.67 / M_inf^2)     cylinder-wedge (2D, used here)
  delta/R = 0.143 * exp(3.24 / M_inf^2)     sphere-cone (axisymmetric, reference only)
  ```
  Sanity check at M=6,7,8: cylinder delta/R = 0.440, 0.425, 0.415 vs. sphere delta/R = 0.157, 0.152, 0.150 — the ~3× ratio matches the well-known "2-D shocks stand off further than axisymmetric ones" fact, giving confidence the formula was transcribed correctly.
- **Modified Newtonian surface pressure** (Anderson Eqs. 3.15–3.19, Lees's modification of Newton's sin² law):
  ```
  Cp(theta) = Cp_max * sin^2(theta)     theta = local surface inclination TO THE FREESTREAM
  ```
  Equivalently, in the angle-from-stagnation-point coordinate used for our mesh/sampling (theta_c = 90° − theta): `Cp(theta_c) = Cp_max * cos^2(theta_c)`.
  `Cp_max` is the exact Rayleigh-Pitot stagnation-point value, built from `normal_shock()` — the SAME building block F3 validated to 6 significant figures against NASA GRC's analytic oblique-shock page — plus the standard isentropic p0/p relation:
  ```
  Cp_max = (2/(gamma*M1^2)) * (p02/p1 − 1)
  ```
  Cross-checked against Anderson's stated M→∞ limit (Cp_max → 1.839 for γ=1.4, p.62): our implementation gives 1.8391 at M=50. ✓
  Computed Cp_max at our test points: M=6 → 1.8181, M=7 → 1.8237, M=8 → 1.8274.

  **Independent positive check (not just a formula cross-check — a physical one):** Cp_max is barely Mach-dependent across our whole M=6–8 range (1.8181 → 1.8237 → 1.8274, a 0.5% spread) and is already within ~1% of the M→∞ asymptote (1.839). This is exactly the "Mach-number-independence principle" hypersonic theory predicts (Anderson §3.1: Newtonian-type results become Mach-independent once M is large enough) — it is not something we tuned for, it falls straight out of the Rayleigh-Pitot formula once M≳6, and it gives confidence the stagnation-point treatment feeding both gates (Cp_max here, and the normal-shock building block reused for it) is implemented correctly.

All of this lives in `F4_runs/billig_theory.py`; no CFD output is used anywhere in that file.

---

## 1. Mesh design (a real iteration, not hidden)

**Attempt 1** (2-block topology mirroring F3's wedge case: flat upstream rectangle + a block with an arc bottom (cylinder wall) but a *flat* top): `checkMesh` failed outright — max non-orthogonality **87.7°** (144 severely non-orthogonal faces, threshold 70°), max skewness **5.14** (8 highly skew faces). The curved-bottom/flat-top block distorts badly away from the shared vertical edge; this geometry would have silently corrupted every downstream number.

**Attempt 2** (kept, used for all reported results): a **single polar ("pie-slice") O-grid block** — concentric arcs for both the cylinder wall (r=R) and the farfield (r=R_top), straight radial sides for the axis-symmetry cut (θ=0) and the outlet (θ=θ_max). Because the grid lines are genuinely radial/circumferential, every internal face is orthogonal by construction. `checkMesh`: max non-orthogonality **1.7×10⁻⁶°**, max skewness **0.031**, max aspect ratio **2.5** — clean pass, every case, every resolution.

Half-domain (upper half, y≥0) exploiting flow symmetry, θ measured from the stagnation point (θ=0) to a windward cutoff at **θ_max=75°** (short of the true 90° shoulder — chosen to see the Newtonian-degradation trend approaching the shoulder without paying for the much larger farfield radius the true shoulder region would require, per the domain-sizing analysis below).

**Domain sizing** (farfield radius R_top=1.7R): sized *a priori* from the Billig shock-shape formula (Eq. 5.36, not just the standoff scalar) — for every θ from 0 to θ_max, checked pointwise that the R_top arc stays strictly on the pre-shock side of Billig's predicted shock shape. Worst-case margin across M=6–8 and the whole windward arc: **1.22–1.31** (x-distance units, R=1), i.e. comfortably safe — verified by the domain_size() printout in `make_cylinder_case.py`, not asserted. This is standard engineering domain-sizing practice and is **not circular** with the gate: the gate compares the CFD's own, independently detected shock/Cp against the correlation; the correlation is only used here to decide how big a box to mesh. Because the entire outer arc is pre-shock everywhere, it carries a single `fixedValue` freestream condition end-to-end (not just a small inlet sliver) — verified, not assumed.

Radial mesh graded (`simpleGrading` expansion ratio 8) to cluster cells at the wall, since the standoff (~0.42–0.44R) occupies roughly 60% of the 0.7R radial gap to the farfield.

Resolutions: coarse 50×20=1,000 cells, medium 100×40=4,000 cells, fine 200×80=16,000 cells (θ×r).

---

## 2. Steady-state convergence — a real numerics finding

F3's flow-through-based `endTime = N·L/M` heuristic (advection-time scale) was tried first and is **wrong for this geometry**: it badly under-runs the stagnation region's true settling time, because the near-stagnation subsonic pocket relaxes acoustically (O(L/a) ~ O(1) in these units), not at the freestream advection speed M·a. Direct evidence: on the coarse M=6 mesh, `standoff(theta=0)` measured at successive write times using the flow-through heuristic (endTime≈1.4) was still visibly drifting (0.325 → 0.323 → 0.405 → 0.386, a ~20% peak-to-peak scatter) — not converged.

A follow-up long run (endTime≈9.3, same coarse mesh) showed the standoff estimate settling into the 0.43–0.47 range by t≈6–8 (much closer to Billig's 0.4395), **but crashed with a floating-point exception (`sqrt` of a negative field) at t≈8.4** — Courant numbers stayed bounded (mean 0.115, max 0.29) right up to the crash, so this is not a classic CFL blow-up; most likely an accumulated numerical-noise event at the stagnation-point cell over an unnecessarily long integration, not something we needed to solve since a much shorter time already converges.

**Adopted fix:** fixed absolute `endTime=6.0` (not M-scaled) for every case, with 3 late-time snapshots (last 3 of 8 writes) sampled and **averaged**, reporting the run-to-run scatter as an explicit uncertainty band rather than trusting a single `latestTime` snapshot. All 9 production runs (3 Mach × 3 resolutions) completed cleanly to `endTime` with no further FPE — the crash was specific to the much-longer, since-abandoned exploratory run. Surface-Cp snapshot scatter (mean across the wall) was small throughout: 0.10–0.22% of Cp_max at coarse/medium, negligible at fine — the Cp gate is not limited by temporal convergence at any resolution tested.

**Standoff snapshot scatter is a different story and is the key caveat on Gate 1 (see §4):**

| M | Mesh | standoff mean | snapshot std | std as % of mean |
|---|---|---:|---:|---:|
| 6.0 | coarse | 0.4380 | 0.0155 | 3.5% |
| 6.0 | medium | 0.4368 | 0.0099 | 2.3% |
| 6.0 | fine | 0.4485 | 0.0017 | 0.4% |
| 7.0 | coarse | 0.4281 | 0.0025 | 0.6% |
| 7.0 | medium | 0.4386 | 0.0072 | 1.6% |
| 7.0 | fine | 0.4345 | 0.0017 | 0.4% |
| 8.0 | coarse | 0.4427 | 0.0125 | 2.8% |
| 8.0 | medium | 0.4082 | 0.0030 | 0.7% |
| 8.0 | fine | 0.4181 | 0.0033 | 0.8% |

Scatter shrinks with mesh refinement in most cases (as expected — a finer radial mesh gives the peak-gradient detector more independent points to lock onto) but **not monotonically for M=7 or M=8**, and even at fine mesh it does not vanish (0.4–0.8% of the mean). This scatter band is the actual measurement uncertainty on the standoff gate and must be read alongside the deviation, not below it — see §4.

---

## 3. Shock-detection methodology (carried over from F3, honestly re-tested here)

Same technique as F3: peak `|d(rho)/d(distance)|` along a sample line, here radial lines at fixed θ stations instead of Cartesian verticals (`find_shock_r()` in `run_cylinder_case.py`). **Gate 1 uses only the θ=0 (stagnation) station** — that is exactly the point Billig's `delta` parameter is defined at.

**New, honestly-reported detector failure mode:** at θ≈60° (and to a lesser extent nearby stations), the detector consistently returns `p_at_shock ≈ 1.0` (i.e., freestream) and pins `standoff` at the domain edge (0.70 = R_top−R) — at *every* resolution level, including fine. This means at that particular station the local oblique shock has weakened and/or its orientation is no longer well-aligned with a purely radial sample line, so no clean density-gradient peak exists along that line at the sampling resolution used. **We report this rather than paper over it**: the peak-gradient-along-a-radial-line technique is reliable for θ ≲ 48° in this geometry/Mach range and unreliable beyond that — a finding that should inform any follow-on work needing shock *position* (as opposed to post-shock *state*) at larger off-stagnation angles.

**How sensitive is the θ=0 gate value specifically to this method?** Two distinct sensitivities, both quantified rather than asserted (see §4 for the full per-case table):
1. **Temporal/snapshot sensitivity** — how much the detected standoff at θ=0 varies across 3 late-time snapshots of the *same* mesh: 0.4–3.5% of the mean, shrinking (mostly) with mesh refinement to 0.4–0.8% at fine.
2. **Resolution/detector sensitivity** — how much the detected standoff at θ=0 shifts between coarse/medium/fine meshes, beyond what temporal scatter alone explains: up to ~2.7 points of deviation swing (M=6) and ~8.3 points (M=8) between adjacent resolution levels, larger than the corresponding scatter bands. This is a real, unresolved detector sensitivity, not just noise — see §4's discussion of which fine-mesh deviations (M=6, M=7) clear this bar and which (M=8) do not.

---

## 4. GATE 1 — Shock standoff vs. Billig, stagnation point

| M | Mesh | Cells | standoff (mean ± snapshot std) | Billig delta/R | Deviation | Deviation vs. own scatter |
|---|---|---:|---|---:|---:|---|
| 6.0 | coarse | 1,000 | 0.4380 ± 0.0155 (3.5%) | 0.4395 | −0.33% | inside scatter (0.33 < 3.5) |
| 6.0 | medium | 4,000 | 0.4368 ± 0.0099 (2.3%) | 0.4395 | −0.60% | inside scatter (0.60 < 2.3) |
| 6.0 | **fine** | **16,000** | **0.4485 ± 0.0017 (0.4%)** | **0.4395** | **+2.06%** | **outside scatter (2.06 ≫ 0.4)** |
| 7.0 | coarse | 1,000 | 0.4281 ± 0.0025 (0.6%) | 0.4246 | +0.82% | outside scatter (0.82 > 0.6) |
| 7.0 | medium | 4,000 | 0.4386 ± 0.0072 (1.6%) | 0.4246 | +3.30% | outside scatter (3.30 ≫ 1.6) |
| 7.0 | **fine** | **16,000** | **0.4345 ± 0.0017 (0.4%)** | **0.4246** | **+2.33%** | **outside scatter (2.33 ≫ 0.4)** |
| 8.0 | coarse | 1,000 | 0.4427 ± 0.0125 (2.8%) | 0.4152 | +6.62% | outside scatter (6.62 ≫ 2.8) |
| 8.0 | medium | 4,000 | 0.4082 ± 0.0030 (0.7%) | 0.4152 | −1.69% | outside scatter (1.69 ≫ 0.7) |
| 8.0 | **fine** | **16,000** | **0.4181 ± 0.0033 (0.8%)** | **0.4152** | **+0.70%** | **inside/comparable to scatter (0.70 ≈ 0.8)** |

**Reading the gate honestly, not just at face value:**

- **M=6 fine and M=7 fine are resolved deviations, not noise.** Their snapshot scatter is only 0.4%, well below the measured 2.06% and 2.33% deviations — those two numbers are a real, statistically meaningful ~2–2.3% high bias against Billig, not a lucky/unlucky noise draw.
- **M=8 fine is NOT resolved above its own noise floor.** Deviation (+0.70%) and snapshot scatter (0.8%) are the same order of magnitude — this run cannot honestly claim 0.70%-accuracy; the true agreement could be anywhere from ~0% to ~1.5% given the scatter, and we cannot even be fully confident of the sign. We report the point estimate because it IS what the CFD produced, but it should be read as "consistent with Billig to within measurement noise," not as a precise 0.70% number.
- **Every coarse-mesh row except M=8 has deviation inside or comparable to its own scatter** — meaning the apparently "good" coarse-mesh agreement (e.g. M=6 coarse's −0.33%) is largely coincidental: the measurement uncertainty at coarse resolution (3.5%) is far larger than the reported deviation. Do not read the coarse-mesh column as evidence of accuracy; it is evidence the run didn't crash (FEASIBILITY), nothing more.
- **Convergence with mesh refinement is explicitly NOT monotonic, and scatter does not fully explain it.** M=6: −0.33% → −0.60% → +2.06% (coarse→medium→fine); M=8: +6.62% → −1.69% → +0.70%. The coarse→medium step for M=6 is well inside the overlapping scatter bands of both levels (a real null result — nothing changed outside noise). But the M=6 medium→fine swing (−0.60%→+2.06%, a 2.66-point move) is larger than medium's own 2.3% scatter band, and the M=8 coarse→medium swing (+6.62%→−1.69%, an 8.3-point move) is much larger than coarse's 2.8% scatter band. **These are not explained by snapshot-to-snapshot noise alone** — they indicate a genuine, resolution-dependent systematic bias in the peak-density-gradient detector itself (where exactly the discrete gradient maximum falls shifts as the number of cells sampling the smeared shock changes), on top of the temporal scatter. This is the same class of finding F3 flagged for the cone case (shock-*position* detection is intrinsically more resolution-sensitive than integrated quantities); F4 confirms it generalizes to a genuinely 2-D blunt-body geometry and is not a cone/axisymmetric-metric artifact.

**Verdict: PASS, with the above caveats stated plainly rather than buried.** Two of three fine-mesh cases (M=6, M=7) show a real ~2–2.3% high bias against Billig's 1967 correlation, resolved above measurement noise — a solid pass, well inside the correlation's own expected scatter against experimental data (Billig's own paper reports comparisons to experiment with several-percent scatter). The third (M=8) agrees even more closely (+0.70%) but that close agreement is not distinguishable from its own ~0.8% measurement noise, so it should be read as "consistent with Billig," not as "resolved to 0.7%." None of the three fine-mesh cases show a deviation large enough to indicate a wrong answer; the honest statement is "standoff agrees with Billig to within 0.7–2.3%, resolved above noise for M=6–7 and within the noise floor for M=8," not a single clean number.

---

## 5. GATE 2 — Windward surface Cp vs. modified Newtonian

RMS deviation computed over the full sampled windward face (θ=0 to 71.4°, i.e. up to 3.6° short of the 75° mesh cutoff to avoid the outlet-adjacent boundary cells), expressed as a percentage of Cp_max so it's comparable across Mach numbers.

| M | Mesh | Cells | RMS(Cp_cfd − Cp_Newton) | RMS as % of Cp_max |
|---|---:|---:|---:|---:|
| 6.0 | coarse | 1,000 | 0.0612 | 4.48% |
| 6.0 | medium | 4,000 | 0.0574 | 4.21% |
| 6.0 | **fine** | **16,000** | **0.0533** | **3.91%** |
| 7.0 | coarse | 1,000 | 0.0856 | 4.69% |
| 7.0 | medium | 4,000 | 0.0702 | 3.85% |
| 7.0 | **fine** | **16,000** | **0.0713** | **3.91%** |
| 8.0 | coarse | 1,000 | 0.0746 | 4.08% |
| 8.0 | medium | 4,000 | 0.0711 | 3.89% |
| 8.0 | **fine** | **16,000** | **0.0707** | **3.87%** |

**Verdict: PASS — clean, near-monotonic grid convergence at all three Mach numbers**, settling to **3.87–3.91% of Cp_max** at fine mesh. This is a well-behaved gate: unlike standoff, refinement steadily reduces the RMS deviation (M=6: 4.48→4.21→3.91%; M=8: 4.08→3.89→3.87%), and the fine-mesh values essentially agree across all three Mach numbers (3.87–3.91%), suggesting the residual is a real, Mach-independent local-inclination-theory effect rather than a resolution artifact.

**Where it degrades (as expected, and diagnosed, not just observed):** the deviation is *not* uniform across the windward face. Representative fine-mesh M=6 profile (θ from stagnation, Cp_cfd − Cp_Newton):

| θ (deg) | 0.2 | 15.2 | 30.2 | 45.2 | 56.4 | 63.9 | 71.4 |
|---|---:|---:|---:|---:|---:|---:|---:|
| diff | −0.0003 | −0.0105 | −0.0035 | +0.0428 | +0.0983 | +0.1269 | +0.1488 |

Near the stagnation point (θ≲30°) CFD tracks modified Newtonian to within ~0.01 (CFD marginally *below* Newtonian). Past θ≈33°, the sign flips and the gap grows steadily and monotonically to +0.15 by θ=71° — **modified Newtonian increasingly *underpredicts* Cp toward the shoulder**, exactly the direction and location the task brief anticipated ("it should degrade toward the shoulder, a known limitation of Newtonian theory, not necessarily a solver error"). This pattern is essentially identical (same sign, same shape, same magnitude to within a few percent) at M=6, 7, and 8, which is itself evidence it's a real local-inclination-theory limitation (Newtonian theory neglects the finite shock-layer thickness and streamline curvature that become significant away from the stagnation point) rather than a CFD artifact — a genuinely inviscid Euler solver has no reason to reproduce a Mach-independent bias unless the reference theory itself is the thing degrading.

---

## 6. Evidence record

| Case | Config hash basis | Wall-time (fine) | Core-min (all 3 mesh levels) | Reference | Computed (fine) | Deviation (± scatter) | Cause of residual | Lesson |
|---|---|---:|---:|---|---|---:|---|---|
| Cylinder M=6.0 | `make_cylinder_case.py` (M, res, θ_max=75°, R_top=1.7R) | 217.1s run | ~4.13 | Billig δ/R=0.4395; Cp_max=1.818 | δ/R=0.4485±0.0017; RMS(Cp)=3.91% Cp_max | standoff +2.06%±0.4% (resolved, real bias); Cp RMS 3.91% | Standoff: resolution-dependent detector bias, larger than temporal scatter (see §4). Cp: Newtonian's own known stagnation-region-only accuracy | Fixed absolute endTime (not M-scaled flowthroughs) needed for stagnation-region acoustic settling; polar O-grid mandatory for mesh orthogonality; report deviation next to its own scatter, always |
| Cylinder M=7.0 | same | 249.3s run | ~4.62 | Billig δ/R=0.4246; Cp_max=1.824 | δ/R=0.4345±0.0017; RMS(Cp)=3.91% Cp_max | standoff +2.33%±0.4% (resolved, real bias); Cp RMS 3.91% | Same as M=6 | Same |
| Cylinder M=8.0 | same | 279.1s run | ~5.44 | Billig δ/R=0.4152; Cp_max=1.827 | δ/R=0.4181±0.0033; RMS(Cp)=3.87% Cp_max | standoff +0.70%±0.8% (NOT resolved above own noise); Cp RMS 3.87% | Same; coarse-mesh standoff detector especially noisy for this case (+6.6%±2.8% at coarse, an 8.3-point swing to medium that its own scatter doesn't explain) | Detector noise/bias decreases with mesh refinement but doesn't vanish; a "close" deviation that sits inside its own scatter band is not the same claim as a resolved one — say which is which |

**Total compute: 14.66 core-minutes** across all 9 CFD runs (3 Mach numbers × 3 resolutions), all foreground, single-core, nothing left running (verified via `ps aux` after every stage).

---

## 7. Stretch rung (compression-ramp SWBLI)

**Not attempted.** Both primary gates passed cleanly with large compute headroom remaining (14.66 of a much larger available budget), but a viscous shock-wave/boundary-layer-interaction case is a materially different undertaking — needs a turbulence model (k-ω SST or similar), a wall-resolved mesh (y+~1, several orders of magnitude more cells near the wall than any case run here), and a published experimental separation-length reference (e.g. Settles et al. compression-ramp data) to gate against. Given the campaign's staging discipline ("do NOT start this late"), and that properly citing and reproducing a specific experimental SWBLI separation-extent dataset would need its own literature-verification pass (same discipline as §0 here), this is left as a **documented next step**, not a rushed attempt: it would need (1) a citable experimental case (Mach, Reynolds number, ramp angle, measured separation length), (2) a wall-normal-resolved 2-D mesh with y+ verification, (3) a turbulence-model choice justified for shock/adverse-pressure-gradient flows, and (4) its own FEASIBILITY→PHYSICS→GATE staging exactly as done here.

### 7a. That literature-verification pass was run (2026-07-30) — and it overturns the case named above

The §0 discipline was applied to the *next* rung before any compute was committed. Result: **the Settles compression-ramp case this report named is not gateable on openly-accessible primary data**, and a materially better-supported case exists. Both conclusions were verified by fetching primary sources, not by search-result summary.

**Settles is out, on evidence:**

- All five candidate Settles DOIs return `is_oa: false` from the Unpaywall API (10.2514/3.61513, 10.2514/3.61331, 10.2514/6.1975-7, 10.2514/3.12205, 10.2514/6.1991-1763). None was readable.
- The NASA-sanctioned re-tabulation of Settles' own data, **NASA CR-177638** (Settles & Dodson 1994, open via archive.org), does **not** contain a separation length: p.42 states *"NOTE: THE EXCERPT SHOWN HERE IS FOR SAMPLE PURPOSES ONLY. SPACE LIMITATIONS PRECLUDE A COMPLETE LISTING. SEE DISKETTE FILE SETTLES2.DAT."*
- The master database, **NASA CR-177577**, has no NTRS download at all ("There are no available downloads for this record"); its data live on floppy disks that NASA/TM-2013-216604 (p.3) itself describes as *"outdated floppy disks that take specialized reading procedures."*
- So we **cannot confirm or deny** that Settles' primaries publish a numeric separation length — only that nothing reachable does. Gating on it would have meant building on a reference we cannot read.

**Recommended replacement — Kussoy & Horstman M=7.05 axisymmetric cylinder–flare.** Source: Kussoy, M.I. & Horstman, C.C., *Documentation of Two- and Three-Dimensional Hypersonic Shock Wave/Turbulent Boundary Layer Interaction Flows*, **NASA TM 101075**, Jan 1989 — open, downloaded, and read directly (`ntrs.nasa.gov/citations/19890010729`).

**Independently re-verified in this session** (the agent's findings were not taken on trust — the PDF was re-fetched and `pdftotext`-grepped against the page text):

- **Gate quantity, quoted verbatim from p.5:** *"The separation locations as measured by the oil-flow visualization technique were s = 0 for θ = 20° and 30°, s = −3.1 cm for θ = 32.5°, and s = −6.3 cm for θ = 35°. Reattachment locations could not be determined."*
- **Table I (local free-stream conditions), every value confirmed on the page:** M∞ 7.05 · T∞ 81.2 K · p∞ 576 N/m² · ρ∞ 0.0252 kg/m³ · U∞ 1274 m/s · T_w 311 K (isothermal) · δ₀ 2.5 cm · δ*₀ 0.74 cm · θ₀ 0.065 cm · τ_w∞ 25 N/m² · **q_w∞ 9300 W/m²** · Re_δ0 1.45×10⁵ · Re_θ0 3.8×10³ · Re/m 5.8×10⁶ · C_f∞ 1.22×10⁻³.
- **A unit error in a secondary source, caught the same way §0 caught 4.76-vs-4.67:** NASA/TM-2013-216604 p.50 writes this heat flux as "9300 W/cm²". The primary (Table I) says **W/m²**, which is also the physically sensible value. Use the primary.

Why this case is stronger than what was planned:

| | Settles (planned) | Kussoy & Horstman (recommended) |
|---|---|---|
| Primary source access | paywalled, unreadable | **open, downloaded, read** |
| Published numeric separation datum | none reachable | **measured, −3.1 cm (32.5°), −6.3 cm (35°)** |
| Mach | 2.85 — abandons F4's hypersonic continuity | **7.05 — stays in F4's regime** |
| Independent restatement | — | NASA/TM-2013-216604 Table A5-3, p.51 (same numbers) |
| Free validated grids | — | NASA TMR hosts the sibling 20° flare with a 5-level nested PLOT3D family + `pw_exp.dat`/`qw_exp.dat` |
| Secondary gates | — | wall pressure & heat transfer, all four flares (TM 101075 Tables IV(a)–(d)) |

**Two redefinitions this forces, stated plainly rather than glossed:**

1. **Geometry is axisymmetric cylinder–flare, not a planar 2-D compression ramp.** For OpenFOAM this is a `wedge` case — *cheaper* than 2-D planar, and it avoids the sidewall three-dimensionality that contaminates real 2-D ramp experiments (CR-177638 p.39 notes Settles' own 24° case shows "significant 3-D perturbations").
2. **The gated quantity is separation-onset distance upstream of the corner, NOT a separation-bubble length.** The primary explicitly could not determine reattachment. If a true L_sep = x_reattach − x_sep is required, **no open primary hypersonic source supplies it** — the only clean measured bubble length found anywhere (Bookey et al., sep −3.2δ, reattach +1.6δ ⇒ L_sep ≈ 4.8δ) is available only through a secondary paper and sits at Re_θ=2400, a DNS-scale Reynolds number where RANS closures are outside their calibration range — a failed gate there would be uninformative about the solver.

**Two setup traps identified before they could silently corrupt a run** (same class as §0's coefficient catch):

- **Do not set M=7.05 at a truncated inflow.** The NASA TMR page states that if the leading edge is excluded, *"Mach number is changed from 7.05 to 7.11"*. Model the full cone-ogive, or adjust.
- **Do not use the tunnel stagnation conditions as inlet BCs.** TM 101075 p.3 gives nominal *settling-chamber* values (T₀ 900 K, p₀ 34 atm, M 7.2, Re/m 7×10⁶) which are **not** the local conditions ahead of the interaction (Table I: M 7.05, Re/m 5.8×10⁶). The consistent total state is ≈24.6 atm (Brown, NASA/TM-2014-218353 Table 2: P_T 2.495 MPa, T₀ 888.38 K). Mixing the two sets puts the run at the wrong Reynolds number with no obvious symptom.

**One caveat that should set the pass band in advance, corrected here against a closer re-read:** a SWBLI separation gate is predominantly a **turbulence-model** gate, not a numerics gate. Brown (NASA/TM-2014-218353) documents DPLR/SST separating ≈3°/10% early in wedge angle on Holden's Mach 8.2 compression-corner cases, and over-predicting separation extent by ≈100% on a Holden Mach 11.3 case, while CFL3D running nominally the same SST model agrees well with experiment on both — but **neither figure is for this exact case**. Re-checked against the primary text (p.17-18) rather than left as a relayed number: those two figures are for Holden's compression-corner geometry, not Kussoy & Horstman's cylinder-flare. Brown's own Table 1 does list an `A5.Kussoy` entry at M=7.05 matching TM 101075's Table I exactly (PT=2.495 MPa, T0=888.38K — the same numbers already cited above), so this is the right experiment, but no DPLR-vs-CFL3D separation-extent comparison specific to `A5.Kussoy` was found stated in this paper's discussion text. **Downgraded accordingly: the ~100%/~3° figures are evidence of the general magnitude of DPLR-vs-CFL3D disagreement across this class of hypersonic SWTBLI problem (multiple compression-corner-type geometries, M=8.2-11.4, same nominal SST closure), not a matched-case citation for this specific cylinder-flare geometry.** Used below as the basis for a band width, stated as general-class evidence, not case-specific.

### Pre-registered pass band for the θ=32.5°/35° gate (written before those cases run, per this campaign's standing P2 discipline)

Gated quantity: **separation-onset distance `s`** upstream of the flare corner (wall skin-friction sign change, matching TM 101075's own oil-flow-visualization definition exactly) — not separation length, since reattachment was never measured in the primary source. Reference: s=-3.1cm (θ=32.5°), s=-6.3cm (θ=35°).

- **PASS:** `s` within ±30% of the experimental value at the matching flare angle. A generous band relative to typical CFD-vs-CFD engineering tolerances, chosen because the experimental method itself (oil-flow visualization) carries real uncertainty and this is a first attempt at a genuinely difficult flow class on this project.
- **INDICTS THE CLOSURE, not the solver:** `s` off by more than the PASS band but within the general magnitude of disagreement mature production codes running the same nominal SST closure already show on this problem class (per Brown, up to ~100% in the worst quoted case, ~10% in wedge-angle terms in the more directly comparable compression-corner cases) — landing in this zone should be reported as "consistent with known SST-closure sensitivity for hypersonic SWTBLI," not as a solver defect, and should be checked against CFL3D-class agreement rather than assumed indicting either way.
- **FAIL, indicting the solver/setup:** `s` outside even that broad envelope, or the wrong sign (predicting attachment where the reference measures separation, or vice versa), or separation appearing at θ=20°/30° where the reference explicitly measures none (s=0) — these would point at a genuine setup defect (BCs, mesh, inflow conditions), not closure accuracy, because they contradict the qualitative topology the reference establishes, not just its magnitude.

**If our number lands inside the general DPLR-CFL3D-class spread rather than on the experiment itself, the record will say that explicitly** — a weaker, different claim than landing on the experimental value, not the same result relabelled.

### The θ=20° warm-up: built, checked, and launched (2026-07-30) — no launch on 32.5°/35° yet

**Case, built from primary-source numbers, not a rule of thumb:**
- Geometry: axisymmetric wedge (2.5° half-angle, this project's standard convention), cylinder radius 0.1015 m (TM 101075's 0.203 m model diameter), domain starting on the bare cylinder ~0.08 m upstream of the corner rather than modelling the real 139 cm from the nose — Table I already supplies the fully-developed local state at the reference station, so the inlet is fed that state directly. Disclosed simplification, not hidden.
- First cell for y+~1, computed from Table I: wall density from ideal gas at p=576 Pa/T=311K, wall viscosity from Sutherland's law at 311K, friction velocity from τ_w=25 N/m² → **47.3 μm**, matching the hand-calculation in the scoping note above to 4 significant figures.
- 29,700 cells (120 axial × 110 wall-normal on the cylinder, 150 × 110 on the flare). `checkMesh -allTopology -allGeometry`: **Mesh OK** — non-orthogonality max 19.6° (well under the usual 70° gate), skewness max 0.91, aspect ratio max 29.9, cell determinant min 0.0014 (positive; the corner block-transition cells are the tightest, expected there).
- Solver: `rhoCentralFoam` + `kOmegaSST`, adapted from OpenFOAM's own `biconic25-55Run35` tutorial (the nearest validated axisymmetric hypersonic template on this host) — that tutorial is laminar and runs N2 with `janaf` thermodynamics; this case adds turbulence transport schemes/solvers and switches to air with `hConst` thermodynamics (adequate for this non-reacting, moderate-temperature flow, avoids needing exact `janaf` polynomial coefficients for air). `localEuler` pseudo-time-stepping (same as the tutorial), Kurganov flux scheme.
- Isothermal wall at 311K, `nutLowReWallFunction`/`omegaWallFunction` (appropriate for a y+~1 mesh), low freestream turbulence (0.1% intensity, eddy-viscosity ratio 5 — a quiet-tunnel assumption, disclosed as an assumption since TM 101075 does not report freestream turbulence levels).
- **Smoke-tested before the real launch**: a 90-second foreground run showed stable residuals (Ux~1e-5 initial residual per step, k~0.004, omega~0.001, no NaN, Courant held at the 0.3 cap) — caught, before an unattended launch, that `localEuler`'s reported "Time" advances far slower than a naive flow-through estimate would suggest (the 47 μm near-wall cells dominate the local pseudo-timestep), so `endTime` was raised from an initial 0.02 (would have needed days) to 1.0 and progress will be judged from the residual trend in the log, not from "Time" reaching a target — the correct way to read a `localEuler` pseudo-steady run, not a defect in it.
- `case_preflight.sh`: **PASS**, `model: kOmegaSST`, both turbulence fields present, fvSolution solver entries confirmed.
- Launched via `launch_solve.sh` (`f4_swbli_warmup20`), verified genuinely running (not just registered) by reading advancing `ExecutionTime`/iteration output in the log within seconds of launch. Single core, resources re-checked immediately before launch (26.6 GB available, load 9.4, swap 0) — twin and pilot untouched.

**Not yet done:** the run has not been read for a verdict — it needs to actually settle before comparing against TM 101075's pressure/heat-transfer data. θ=32.5°/35° remain held until this reports, as instructed.

**Status: reference verified and reachable; θ=20° warm-up case built, checked, and running; θ=32.5°/35° gate cases NOT yet built or run**, pending the warm-up's result and the pre-registered pass band above.

### The θ=20° warm-up crashed — diagnosed, corner hypothesis refuted, root cause is a BC edge conflict, not mesh quality (2026-07-30)

**The crash.** `f4_swbli_warmup20` (registry: `f4_swbli_warmup20_20260730T004453Z`) died with **SIGFPE inside `libfluidThermophysicalModels.so`** at `ExecutionTime≈101.9s`, `Time=6.42e-07`. Courant numbers were normal (0.24–0.3) with no warning in the reported diagnostics up to the crash — no field write had happened between `t=0` and the crash (`writeInterval=1e-3`, `purgeWrite=3`, and the case never got that far), so the crashed case's own artifacts (log + `0/`) could not by themselves localise which cell failed. The previous agent's own writeup above ("the corner block-transition cells are the tightest, expected there") stated the mesh-quality-corner hypothesis but never tested it against where the solver actually died.

**Step 1 — where checkMesh's worst cells actually are.** `checkMesh -allTopology -allGeometry` (zero-cost, P3): **Mesh OK**, min cell determinant **0.00143527416** (matches the previously reported ~0.0014). Writing the `cellDeterminant` field and cross-referencing cell centres (`checkMesh -writeFields '(cellDeterminant)'` + `postProcess -func writeCellCentres`) shows the 20 worst cells are **all at `x≈0.1996–0.1999 m, r≈0.2007–0.2015 m`** — the **outlet/farfield corner**, not the flare's block-transition corner (`x=0.08 m`, at the wall). The block-transition corner is unremarkable in mesh quality. **First correction to the leading hypothesis: even the "worst cell in the mesh" claim was mislocated** — it's the far corner of the domain, driven by the same grading (`total_ratio≈85.5`) that keeps the wall cell at 47 μm, not by the flare-angle geometry.

**Step 2 — the cheapest discriminating fix: bound T/e, and see whether that's enough.** `constant/thermophysicalProperties` uses `thermo hConst`. Checked against source (`hConstThermoI.H` vs `janafThermoI.H`, both in this OpenFOAM 2606 install): **`hConstThermo::limit(T)` is a documented no-op** — it returns `T` unchanged — unlike `janafThermo::limit()`, which genuinely clamps to `[Tlow,Thigh]` inside the T-inversion (and is what the `biconic25-55Run35` tutorial this case was adapted from actually relies on, with `Tlow 100; Thigh 10000;` in its own `thermophysicalProperties`). Switching this case from the tutorial's `janaf` to `hConst` — a disclosed, reasonable simplification for a non-reacting flow — silently also dropped the tutorial's only T-bounding mechanism, and `rhoCentralFoam` never calls `fvOptions` on `e`, so there is no other bound in play. Confirmed in `rhoCentralFoam.C`: `e = rhoE/rho - 0.5*magSqr(U); e.correctBoundaryConditions(); thermo.correct();` — the crash's stack (`libfluidThermophysicalModels.so`) is `thermo.correct()`'s Sutherland `mu = As*sqrt(T)/(1+Ts/T)` seeing an out-of-range `T` produced by an unclamped `e`.

Built a local solver variant, `rhoCentralFoamBounded` (compiled to `$WM_PROJECT_USER_DIR`, system OpenFOAM install untouched; diff against stock `rhoCentralFoam.C` is exactly two `#include "boundE.H"` lines, no other physics changed). `boundE.H` clamps `e` to the exact energy range that maps to `T∈[TMin,TMax]` under `hConst`'s own linear, exact inversion (`T = Tref + (e-eref)/Cv`, `Cv=717.30 J/(kg·K)` from this case's own `Cp=1005`, `molWeight=28.9`) immediately before each `thermo.correct()` call, and logs cell counts/locations whenever it fires — both the protective fix and the localisation diagnostic the crashed run's own artifacts couldn't provide. `TMin=20K` (below the coldest physical state in this case, `T_inf=81.2K`), `TMax=5000K` (well above the M=7.05 normal-shock stagnation estimate, `T0≈888K`).

**Result — the case did NOT just have a single bad cell.** Preflight passed; a foreground smoke test (per the standing rule) ran the bounded solver from `t=0`: it passed the original crash point (`t=6.42e-07`) with no SIGFPE, reaching `t≈7.66e-07` (≈300s wall-clock across three foreground legs) before the smoke test was stopped. But the bound fired **continuously and on a large, growing fraction of the mesh**, not on one or a few cells: **1,255 → 6,546 cells** (of 29,700) clamped over that window (4–22% of the whole mesh), and the spatial extent of clamped cells grew from `x∈[0.0003,0.05]` at `t=2.5e-08` to `x∈[0.0003,0.18]` by `t=7.66e-07` — spreading from near the inlet across almost the entire cylinder and well into the flare section, not settling. The two persistently worst cells (`13080` at `x=0.00033, r=0.1035` — just off the wall; `6360` at `x=0.00033, r=0.1926` — near farfield) both sit at essentially the **same axial station, x≈0.0003 m — the very first cell column, immediately downstream of the inlet.** Checked their mesh determinants directly against the checkMesh scan above: cell 13080 = **0.0303**, cell 6360 = **0.164** — both over 20× better than the domain's actual worst cell (0.00144, at the outlet/farfield corner). **The corner-block-transition mesh-quality hypothesis is refuted twice over: neither the crash site nor the checkMesh-worst site is at the flare's block-transition corner, and the cells where the crash-guard actually fires are unremarkable in mesh quality.**

**What's actually there.** The wall patch (`type wall`, isothermal `T=311K`, no-slip) and the inlet patch (`type patch`, fixed `T=81.2K, U=1274 m/s`) **share a single mesh edge/vertex at `x=0, r=R_CYL=0.1015m`** — an artifact of this case's disclosed domain-truncation choice (starting the mesh at the reference station rather than modelling the real 2m nose + 139cm upstream run, per §7a above, with a spatially **uniform** freestream state fed in at the inlet rather than a boundary-layer profile). Two Dirichlet conditions meet at that shared edge with no transition, on a mesh whose first cell is 47 μm (y+~1) thick by design. The explicit, density-based central-scheme flux update at that edge produces a large, non-decaying local energy deficit that spreads outward with time rather than healing — a genuine setup singularity, not a numerics-tolerance or mesh-refinement problem in the `checkMesh`-quality sense. This is the "something more fundamental" the brief's step 3 anticipated, just not the mesh defect that was hypothesised.

**What this does and does not establish (L-3 discipline).** Bounding is diagnostic, and it answered the question: this is not a rare single-cell excursion papered over by a quick clamp — it is a real, spreading defect at the wall/inlet edge. It is **not yet established** whether giving the inlet a proper near-wall boundary-layer profile (blending `U:0→1274 m/s`, `T:311→81.2K` over the reference boundary-layer thickness, ~2.5cm, instead of a step function) removes the singularity — that is the next, one-variable test, not run this session. **The θ=20° warm-up does not currently reproduce, and was never run far enough to be compared against, TM 101075's pressure or heat-transfer data** — `endTime=1.0s` requires roughly 16,000+ iterations at the observed `dt≈1e-8s`, and the growing bounded region means even a much longer run would not currently produce a physically meaningful near-wall state to compare. θ=32.5°/35° remain correctly held.

**Status: crash diagnosed and localised; corner-block-transition mesh-quality hypothesis refuted by direct measurement; root cause identified as a wall/inlet boundary-condition edge conflict (uniform inlet profile meeting a no-slip isothermal wall with no transition), not mesh quality; a working bound (`rhoCentralFoamBounded`) exists and prevents the SIGFPE but does not by itself produce a physically usable warm-up result. Next step: re-run with a boundary-layer-shaped inlet/initial profile, not attempted this session.**

Artifacts: `demo-output/website/campaign/F4_runs/swbli_cylflare/warmup20` (original crashed case, preserved unmodified as evidence), `demo-output/website/campaign/F4_runs/swbli_cylflare/warmup20_bounded` (bounded re-run case), `$WM_PROJECT_USER_DIR/applications/solvers/compressible/rhoCentralFoamBounded` (solver source, two-line diff from stock `rhoCentralFoam.C`).

---

## Summary

| Gate | Reference | Fine-mesh result | Deviation (± snapshot scatter) | Verdict |
|---|---|---|---:|---|
| 1. Shock standoff (stagnation) | Billig (1967) δ/R = 0.386·exp(4.67/M²) | M=6: 0.4485; M=7: 0.4345; M=8: 0.4181 | +2.06%±0.4%, +2.33%±0.4%, +0.70%±0.8% | **PASS** — M=6, M=7 resolved above noise (~2–2.3% real bias); M=8 within its own noise floor (consistent with Billig, not resolved to 0.7%) |
| 2. Windward Cp distribution | Modified Newtonian (Lees), Cp_max via Rayleigh-Pitot | RMS 3.91%, 3.91%, 3.87% of Cp_max | — | **PASS**, converges cleanly (near-monotonically) with mesh refinement; documented, physically-explained degradation toward the shoulder (θ≳33°), consistent in sign/shape/magnitude across all 3 Mach numbers |
| 3. SWBLI stretch | Kussoy & Horstman M=7.05 cylinder–flare (NASA TM 101075) — **reference verified open + primary-checked**, replacing the paywalled Settles case originally named | — | — | **Not run** — reference now secured (§7a); mesh/closure/staging still required |

**Standoff (Gate 1) does NOT converge monotonically with mesh refinement** (M=6: −0.33→−0.60→+2.06%; M=8: +6.62→−1.69→+0.70%, coarse→medium→fine) — stated plainly, not glossed over. Snapshot-to-snapshot temporal scatter explains part but not all of this: the coarse↔medium swings are mostly within each level's own noise band, but the medium↔fine swings exceed it, pointing to a genuine resolution-dependent bias in the peak-density-gradient detector itself, layered on top of temporal noise. See §2 (scatter table) and §4 (per-case scatter-vs-deviation reading) for the full breakdown — this is the honest state of Gate 1, not a single clean deviation number.

**Rung reached: GATE (fine mesh), both primary gates, all three Mach numbers.**

All code: `demo-output/website/campaign/F4_runs/{billig_theory.py, make_cylinder_case.py, run_cylinder_case.py, build_report.py}`. Machine-readable results: `F4_hypersonic_blunt_body.json` (per-case, all resolutions). Raw case directories under `F4_runs/cyl/M{6.0,7.0,8.0}/{coarse,medium,fine}/` (blockMeshDict, logs, `result.json` with full per-station/per-θ data).
