# Double Mach reflection (Woodward–Colella 1984) — pre-registration

Written 2026-08-07, before any mesh or solve existed for this item. Docket:
`double-mach-reflection-woodward-colella` (filed by the 2026-08 challenge
slate, measurement, criterion 2, 20 core-min). Solver line: native
openfoam2606 `rhoCentralFoam`, Kurganov flux, inviscid — the proven F3/F4
stack (`F3_supersonic_exact_theory.md`, `F4_hypersonic_blunt_body.md`).
Precedent: F6b two-gate canon; detector-first per the F3 shock-locator
lesson.

## 1. Formulation (one chosen, per the launch prompt)

**Inclined-shock on the rectangular domain** — the literature's own frame,
so contours compare without rotation. Chosen over the physical 30° ramp
because the canon's conventions (domain, t = 0.2, contour counts,
resolutions quoted as 1/N) are all stated in this frame, and a Cartesian
mesh removes mesh-shear as a nuisance variable.

- Domain [0,4] × [0,1], 2D (one cell, `empty` front/back).
- Mach 10 shock inclined 60° to the wall, through x0 = 1/6 at t = 0.
- Initial states (Kemm 2014, arXiv:1404.6510, §2, transcribed from the
  conserved-variable form; identical to Woodward & Colella's):
  - post-shock (left): rho = 8.0, u = 7.1449625, v = −4.125, p = 116.5
  - pre-shock (right): rho = 1.4, u = v = 0, p = 1.0, gamma = 1.4
- Initialisation by `setExprFields` on the exact line
  x < 1/6 + y/sqrt(3).
- Thermo: the F3/F4 nondimensional convention — perfectGas,
  molWeight 11640.3 (R = 5/7), Cp = 2.5, mu = 0, so T_pre = 1 and
  a_pre = 1 exactly; T_post = 116.5/(8 · 5/7) = 20.3875.
- BCs: left inlet fixed post-shock; bottom x < 1/6 fixed post-shock,
  x ≥ 1/6 slip wall; right outflow (zeroGradient); **top: time-dependent
  Dirichlet tracking the exact shock trace** x_s(t) = 1/6 + (1 + 20t)/sqrt(3)
  (coded BC on p, T, U — the fiddly part, stated).
- endTime 0.2; writes every 0.02 (0.2 is a writeInterval multiple — the F8
  §7 trap checked at registration time); adjustable dt on the acoustic
  Courant number, maxCo 0.2.

## 2. Rungs

| rung | 1/dx | cells | role |
| --- | --- | --- | --- |
| R1 | 120 | 480 × 120 = 57,600 | primary (the tasking's "1/120 to start"; the finest of Woodward & Colella's own displayed set 1/30, 1/60, 1/120) |
| R2 | 60 | 240 × 60 = 14,400 | resolution-trend / self-similarity check |

1/240 is deliberately outside this item's 20 core-min budget; if wanted, it
is a successor filing, not a quiet extension.

## 3. Reference amendment — dated, pre-launch, per guidelines §1.4

The filed proposal intended to gate the primary triple-point trajectory
angle against "the published reference with its provenance tier". The
genuine search (2026-08-07, this date, before any solve) found the canon
does **not** carry a shared numeric value for it in reachable form:

- Woodward & Colella (1984), JCP 54:115–173 — the reference computation —
  is paywalled; its figures are the reference and no open numeric
  transcription of the triple-point trajectory or Mach-stem position was
  found.
- Kemm (2016/arXiv:1404.6510), read in full this date: gives the setup,
  ICs, and artifact taxonomy — **no numeric trajectory angle**.
- Vevek, Zang & New, J. Sci. Comput. (2019) (alternative setups): paywalled,
  no open copy found.
- NASA LAVA DMR tutorial (fetched this date): conventions only ("30
  uniformly spaced contour levels", domain, ICs) — no gate numbers.
- DTIC ADA185690 (analytical Mach-reflection tables): HTTP 403.

This matches what the slate's own reference table already recorded: *"the
reference IS the benchmark computation; grading is against its self-similar
structure, stated as such."* The amendment: the external-band trajectory
gate is replaced, before launch, by the three gates below; the measured
trajectory angle is **published with its locator increment as a
measurement**, becoming the lab's transcription-in-waiting for when the
W&C figures are obtained and tiered. This is the guidelines-5.4 route
(secondary handling with provenance stated) rather than a full BLOCKED,
because the case retains an exact analytic reference for its kinematics —
below — and a detector-decidable structure criterion.

## 4. Gates

**Gate V — kinematics against exact theory (both rungs).** The undisturbed
incident shock's position is analytic: at t = 0.2 its trace on the line
y = 0.9 is x = 1/6 + (0.9 + 4)/sqrt(3) = **2.99568**, having travelled
2.30940 in x from its t = 0 trace. Measured by the density-gradient locator
along y = 0.9 (sampled far right of the reflection structure).

- Locator increment = one cell: R1 0.00833 (0.36% of travel), R2 0.01667
  (0.72% of travel). Tolerance: **±1.0% of the travelled distance**
  (±0.0231 in x). Detector-first check: the increment expresses the
  tolerance at both rungs (0.36% and 0.72% < 1.0%) — stated before any
  solve, so the proposal's NO-VERDICT branch does not fire.
- PASS iff |x_measured − 2.99568| ≤ 0.0231 at both rungs. This gates flux
  and wave-speed correctness — numerics, which is all an Euler benchmark
  can gate.

**Gate P1 — the double-Mach structure exists (R1, t = 0.2).** The shock
front extracted by the density-gradient locator between the wall and the
undisturbed incident shock must show **two triple points** (two slope
discontinuities of the front polyline, by the pre-committed detector in
`DMR_runs/dmr_locator.py`) and a wall-jet density roll-up behind the
primary Mach stem (max density in y < 0.1 exceeding the post-primary-stem
plateau). Binary PASS/FAIL as detected; the detector script is retained
with the runs.

**Gate P2 — self-similar consistency across rungs.** The primary
triple-point trajectory angle chi (angle at the wall between the wall and
the line from (1/6, 0) fitted through the triple-point positions at
t = 0.10 … 0.20, six writes) must satisfy:

- within-rung self-similarity: the linear fit of triple-point positions,
  extended back, passes within 2 locator increments of (1/6, 0);
- rung-to-rung: **|chi_R1 − chi_R2| ≤ 1.5°** (declared now; the R2 locator
  increment translated through the ~2.3-long trajectory arm subtends ~0.4°,
  so 1.5° is expressible by the instrument).
- chi_R1 is then **reported** with its locator increment. No external band
  is claimed, per §3.

**Recorded, not gated:** density at t = 0.2 on [0,3] × [0,1] with **30
uniformly spaced contour levels** (the convention the canon uses; count per
the LAVA tutorial capture), one plot per rung; the wall-jet qualitative
state per rung as the dissipation note.

## 5. Predictions (scored afterwards, left as written)

1. Gate V passes at both rungs, R1 error < R2 error.
2. Gate P1 passes at R1: rhoCentralFoam at 1/120 resolves both triple
   points; the wall jet is present but visibly more damped than published
   PPM figures (central-upwind flux is more dissipative than PPM).
3. At R2 (1/60) the jet is strongly damped and the secondary triple point
   is marginal — if the P1 detector run on R2 finds only one kink, that is
   the expected dissipation reading and is recorded as such (P1 is gated on
   R1 only).
4. Gate P2 passes: chi consistent across rungs within 1.5°.
5. Cost: R1 + R2 + locator ≤ 20 core-min gross (4 ranks each; anchored to
   F4's single-digit-core-min rungs at comparable cell counts, explicit
   acoustic dt at Mach 10 priced in).

## 6. Budget, disqualifiers, honesty clause

- Budget **20 core-min**, 4 MPI ranks, setsid, native. Runs and retained
  artifacts under `demo-output/website/campaign/DMR_runs/` (logs,
  controlDict, locator script, final fields) per the launch prompt.
- Disqualifiers: solver crash (recorded per guidelines §4, not softened);
  shock reaching x = 4 before t = 0.2 (setup error — the exact kinematics
  say it cannot: wall trace 2.476 at t = 0.2); any edit to gates after
  first solve.
- **What this benchmark gates, honestly:** this is inviscid Euler against a
  published *benchmark computation*, not an experiment. A pass extends the
  compressible line's credential from steady shock positions (F3/F4) to an
  unsteady self-similar shock structure and stands as the regression anchor
  for any future flux/limiter change. It says **nothing about turbulence
  closures** — there is no RANS model in the loop — and it carries no
  experimental anchor: anchor-2-class at best, per the slate's own
  convention for Liska–Wendroff-style references.

---
*Nothing below this line existed when the runs were launched.*
