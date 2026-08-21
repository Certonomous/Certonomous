# T10a. The radiation tier's exact-theory entry: view-factor enclosures against analytic surface-to-surface exchange

**FROZEN 2026-08-21, before any solve.** This file promotes
`T10a_PREREGISTRATION_DRAFT.md` (2026-08-20, left untouched beside this file)
to the frozen pre-registration. **Every INTERPRETATION 1..7 is resolved in
§11, each in the draft's recommended reading, approved by Sanaa 2026-08-21 on
the team's recommendation.** Authorship and the interruption that split it are
disclosed in §12; the freeze set of paths to commit before any solve is in
§12.1. Run tree `verification/runs/T-family/T10a_runs/` — at freeze it holds
scripts, 13 built cases (dictionaries, `0.orig`, blockMesh meshes, checkMesh
logs, and the view-factor matrices `constant/F` from the generators, which are
mesh-side preprocessing under Charter §2d), and **no time directory of any
kind: no case has ever been handed to a solver in the tree.**

Campaign T, rung T10a, tier **EXACT** (`T_FAMILY_INDEX.md`). Template:
`T9a_PREREGISTRATION.md`. Verdict vocabulary fixed by the Verification Charter
§2: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.**

---

## 1. Why this rung, and what it grades

**T10a is the second of only two EXACT-tier rungs in the T-family.** Its
references are closed-form solutions of the surface-to-surface (S2S) exchange
problem, so **there is nothing to obtain and the reference cannot be wrong.**
It opens the radiation tier: T10b (natural convection + radiation) and every
room-scale rung that carries a radiative wall load rest on the view-factor
exchange being right.

**This rung grades two things and nothing else:** (i) the view factors the
toolchain computes between the faces of a closed enclosure, and (ii) the
grey-diffuse radiosity solve built on them. **It grades no participating
medium, no spectral effect, no convection and no conjugate coupling** (§9).

The toolchain facts of the draft's §1.1 were re-verified at build: OpenFOAM
v2606 at `/usr/lib/openfoam/openfoam2606` ships `viewFactorsGen` (2AI/2LI,
CGAL AABB visibility — confirmed compiled in from the binary's CGAL symbols),
`createViewFactors` (auto-selects the 2D-only `viewFactorHottel` crossed
strings on a 2D mesh), the `viewFactor` radiation model with a cached-LU
direct solver for `constantEmissivity true` (`viewFactor.C`: the C matrix is
LU-decomposed once at the first radiation solve and back-substituted
afterwards), and the `greyDiffusiveRadiationViewFactor` patch condition.
**σ is graded as σ_OF = 5.670408558e-08 W/m²K⁴**, rebuilt from the k, h, c in
`etc/controlDict` and READ from that file by `exact_t10a.py`
(+6.02e-06 relative to the exact SI 5.670374419e-08).

### 1.2 The exactness condition that decides the geometry (INTERPRETATION 1, resolved)

The lumped radiosity network is exact only where irradiation is uniform on
every surface: by symmetry (concentric spheres) or for black surfaces (any
geometry with known finite-surface view factors). A truncated "infinite"
plate or cylinder pair carries a 1-10 % model floor that is not EXACT-tier
(draft §1.2, quantified there). **Therefore: the grey F₁₂ = 1 row is
concentric spheres; the non-trivial view-factor row is a black rectangular
box; a grey non-symmetric enclosure is not registered because it has no exact
answer.** Approved by Sanaa 2026-08-21 on the team's recommendation.

---

## 2. T10a-1 — concentric grey spheres, against the two-surface network

| quantity | value |
| --- | ---: |
| inner radius r₁ | 0.05 m |
| outer radius r₂ | 0.10 m |
| A₁ = 4πr₁² | 0.03141593 m² |
| A₂ = 4πr₂² | 0.12566371 m² |
| ε₁ (inner) | **0.6** |
| ε₂ (outer) | **0.4** |
| T₁ (inner) | 600 K |
| T₂ (outer) | 300 K |

**View factors, exact:** F₁₂ = 1, F₁₁ = 0, **F₂₁ = A₁/A₂ = 0.25**,
**F₂₂ = 0.75** (reciprocity; independently the cone integral
∫₀^α 2 sinθ cosθ dθ = sin²α, α = asin(r₁/r₂), returns 0.2500000000).

**Net flux leaving the inner sphere, closed form:**
q₁ = σ(T₁⁴ − T₂⁴) / [1/ε₁ + (A₁/A₂)(1/ε₂ − 1)], denominator 49/24 =
**2.041666667**.

| | σ_OF (graded) | σ exact SI |
| --- | ---: | ---: |
| **q₁, inner, net leaving** | **3374.471705 W/m²** | 3374.451389 W/m² |
| **q₂, outer, net leaving** | **−843.617926 W/m²** | −843.612847 W/m² |
| Q = A₁q₁ | 106.012155 W | 106.011517 W |

Second derivation (the 2×2 system in `viewFactor.C`'s own assembly) agrees to
2.2e-16 relative; `exact_t10a.py` re-derives every constant both ways at every
comparator run and **the comparator refuses to run if they disagree**
(verified: it runs today and agrees; it refuses on a planted disagreement).

**Sign convention, read from the code and registered:** OpenFOAM's `qr` is the
net flux INTO the wall; registered `qr` is **−3374.471705 on the inner patch,
+843.617926 on the outer.** A sign disagreeing with both the code reading and
the physics is a GATE FAIL, not a convention.

**Why ε = 0.6 / 0.4 and r₁/r₂ = 0.5** (INTERPRETATION 7, resolved as
registered): black treatment departs **+104.17 %** (control C1),
parallel-plate F departs **−35.53 %** (C2), outer-black +22.50 %, swapped
emissivities −23.44 %; q₁ moves 0.816 % per 1 % of ε₁ and 0.306 % per 1 % of
ε₂, so both emissivities are load-bearing and no limit that would hollow the
row is near. Approved by Sanaa 2026-08-21 on the team's recommendation.

---

## 3. T10a-2 — a black rectangular box, against closed-form view factors

Box 1 × 1 × 0.5 m; six planar patches, all black (ε = 1); floor (z = 0)
600 K, ceiling (z = 0.5) 300 K, x-walls 400 K, y-walls 350 K; areas 1.0 /
1.0 / 0.5 × 4 m².

**View factors (Howell C-11 / C-14 closed form, independently confirmed by a
Stokes contour integral to ≤ 2.9e-14):**

| pair | value |
| --- | ---: |
| floor → ceiling | **0.415253284** |
| floor → one wall | **0.146186679** |
| wall → floor (reciprocity) | **0.292373358** |
| wall → opposite wall | **0.116653692** |
| wall → adjacent wall | **0.149299796** |

Row sums 1.000000000000000; reciprocity defect 0.0.

**Registered face-mean net fluxes (exact for black surfaces):**

| row | patch | net LEAVING, σ_OF (graded) | σ exact SI |
| --- | --- | ---: | ---: |
| B0 | floor | **6484.920941 W/m²** | 6484.881898 |
| B1 | ceiling | **−3265.532221 W/m²** | −3265.512561 |
| B2 | x-walls (each) | **−1254.691645 W/m²** | −1254.684091 |
| B3 | y-walls (each) | **−1964.697075 W/m²** | −1964.685246 |

The squat H/W = 0.5 box (not a cube) and these temperatures are chosen so no
row sits near radiative equilibrium and the planted cube matrix fails by
2.3-41 % (§6); **B0 is registered as the least view-factor-sensitive row** and
§5.4's discrimination condition decides whether it may be graded at all.

### 3.1 T10a-3 — a 2D Hottel rectangle, REPORTED ONLY (INTERPRETATION 5, resolved)

Kept, never gated, not counted, as approved by Sanaa 2026-08-21 on the team's
recommendation. Registered crossed-strings values for the 1 × 0.5 black
section: F_floor→ceiling 0.618033989, fluxes 6510.513314 / −4637.006925 /
−1873.506388 W/m² (σ_OF). **Amendment at freeze, from the disclosed scratch
smoke test (§12.3): the draft called this row an identity under Charter §2a
("exact to round-off at every resolution"). The v2606 implementation is NOT
that identity** — at N = 32 the smoke run returned 6517.19 / −4573.39 /
−1833.22 W/m² (0.10 / 1.37 / 2.15 % from the crossed-strings closed form, with
raw row-sum defects of 2.7-3.3 %), i.e. the utility's strip visibility and
assembly add real discretisation error. The row's status does not change — it
was never gated — but its value is now stated correctly: it is a reported
observation of a second utility, not a round-off check, and the §2a identity
rationale is withdrawn.

---

## 4. Solver path (INTERPRETATION 2, resolved), and what is READ rather than assumed

**`buoyantSimpleFoam`, single region, laminar, g = (0 0 0), quiescent
non-participating air, every wall `fixedValue` T, `radiationModel
viewFactor`.** Approved by Sanaa 2026-08-21 on the team's recommendation. With
every wall temperature fixed, `qr` is determined by T, ε and F at the first
radiation solve and cannot move afterwards; the fluid is a carrier, exactly as
`laplacianFoam` was in T9a.

Dictionary lines as BUILT (none left to a default; `check_t10a_mesh.py` reads
them back per case and refuses on any mismatch):

- `constant/radiationProperties`: `radiation on; radiationModel viewFactor;
  viewFactorCoeffs { smoothing false; constantEmissivity true; useDirectSolver
  true; nBands 1; } solverFreq 1; absorptionEmissionModel none; scatterModel
  none; sootModel none;` (`smoothing true` only in the twins S_f_s, B_f_s).
- `constant/boundaryRadiationProperties`: per patch `type lookup; emissivity
  <ε>; absorptivity <ε>;`.
- `constant/viewFactorsDict`: `writeViewFactorMatrix true; GaussQuadTol 0.01;
  distTol 8; alpha 0.21; intTol 0.01;` — the v2606 source defaults written
  out; `GaussQuadTol 0.001` in the twins S_f_q, B_f_q. (H_2d instead carries
  `createViewFactors`' entries: `raySearchEngine voxel; agglomerate false;
  nRayPerFace 100; writeViewFactors true;`.)
- `constant/polyMesh/boundary`: every radiating patch
  `inGroups (wall viewFactorWall)`; H_2d's empty pair out of the group.
- `0.orig/qr`: `greyDiffusiveRadiationViewFactor; qro uniform 0;` on every
  radiating patch; `0.orig/T` fixedValue per patch; `0.orig/U` noSlip;
  `0.orig/p_rgh` fixedFluxPressure; closed-domain `pRefCell 0 / pRefValue 1e5`
  in `fvSolution`.
- `system/controlDict`: `endTime 20; deltaT 1; writeInterval 5; purgeWrite 0;
  writePrecision 16;` — **writeInterval STRICTLY less than endTime, four
  checkpoints retained (L-140).** `system/fvSolution` carries **no
  residualControl** (L-141).
- **No `faceAgglomerate`** (INTERPRETATION 4, resolved as registered, approved
  by Sanaa 2026-08-21 on the team's recommendation): `finalAgglom` absent,
  identity agglomeration, one radiating face per mesh face.

**READ, never assumed, by the frozen comparator:** patch areas/centres/
vertices from `constant/polyMesh` (L-142); the view-factor matrix from the
`constant/F` the utility wrote, with `globalFaceFaces` addressing, never from
the generator's inputs; `qr` from the last two written checkpoints; σ from
`etc/controlDict`; ε from `boundaryRadiationProperties`; smoothing deltas and
model selection from the logs.

**The attribution lever, registered before it is needed:** the comparator
solves the radiosity system itself (numpy, `viewFactor.C`'s exact assembly) on
the written F and compares face by face with the solver's `qr`. Python-on-F ==
solver != exact means the view factors are wrong; Python-on-F != solver means
the assembly or BC is wrong.

---

## 5. Band derivation protocol

### 5.1 The ladder — MESHES BUILT AND READ FROM constant/polyMesh/points BEFORE ANY SOLVE

**The band is derived, never chosen.** Three levels at nominal ratio 1.6 in
radiating-face edge count; quadrature settings held fixed across the ladder.
The table below is **measured from the written meshes** by
`check_t10a_mesh.py` (2026-08-21, exit 0, all 13 cases, planted positives
fired — §12.2):

| case | N (nr) | radiating faces | cells | read from the mesh |
| --- | ---: | ---: | ---: | --- |
| S_c | 10 (4) | 1 200 | 2 400 | vertex radii on 0.05 / 0.10 m to 4.2e-16 rel; faceting deficit −0.5382 % |
| S_m | 16 (6) | 3 072 | 9 216 | deficit −0.2108 % |
| S_f | 26 (10) | 8 112 | 40 560 | deficit −0.0799 % |
| B_c | 16 /m | 1 024 | 2 048 | extents 1 × 1 × 0.5 exact; areas exact to 1e-10 |
| B_m | 26 /m | 2 704 | 8 788 | same |
| B_f | 42 /m | 7 056 | 37 044 | same |

Refinement ratios read from the meshes: spheres **1.6000, 1.6250**; box
**1.6250, 1.6154**. The faceting deficit is monotone shrinking (−0.538 →
−0.211 → −0.080 %, O(h²) as registered): **inside the ladder, not a floor.**
The twins S_C1, S_f_q, S_f_s and B_C3, B_f_q, B_f_s share the finest meshes
(identical points, verified); H_2d is 32 × 16 (512 cells, 96 faces).

### 5.2 The rule — BINDING (D440)

Roache GCI at **Fs = 1.25 on the finest level**, computed by the same `gci()`
as T1c and T9a (imported from `T1_runs/analyse_t1c.py`; the comparator refuses
if the registered Fs/r differ from that module's). **BINDING: a graded row
whose grid triple is not CONVERGING — OSCILLATORY, STAGNANT, DIVERGENT or
EXACT — returns NOT A RESULT, never PASS (D440). A row any of whose levels is
not iteratively CONVERGED returns NOT A RESULT before the triple is even
formed.** The `--selftest` proves every one of those states returns NOT A
RESULT even with the fine value sitting exactly on the reference, and that
CONVERGING reaches both PASS and GATE FAIL (§12.2). A reportable band is not a
demonstrated asymptotic order; the observed p is quoted beside every band.

### 5.3 Intrinsic floors — now partly MEASURED at build

| floor | size | handling |
| --- | ---: | --- |
| σ_OF vs exact σ | 6.0e-06 rel | graded against σ_OF; not a floor in practice |
| sphere faceting | measured −0.538/−0.211/−0.080 % | inside the ladder, converges, not a floor |
| view-factor quadrature | **measured raw row-sum defects, smoothing false: inner sphere 0.11-0.48 %; outer sphere 4.3-4.8 % AT EVERY LEVEL (does not converge — held fixed, as registered); box patches 1.9-3.9 %; H_2d 2.7-3.3 %** | the GaussQuadTol 0.001 finest twins S_f_q, B_f_q measure its effect on flux; REGISTERED CONDITION: a row whose armed band is smaller than the twin's change on that row is REPORTED AND NOT GRADED, verdict GATE REACHED |
| smoothing | row-renormalisation hides the defect | **graded with smoothing false** (INTERPRETATION 3, resolved as registered, approved by Sanaa 2026-08-21 on the team's recommendation); smoothing-true finest twins REPORTED |
| truncation | none | both geometries closed and exact |

### 5.4 Discrimination condition (Charter §2c)

**A row is graded only if its armed band is less than one tenth of its C2
departure.** For B0 that requires a band below 0.23 %; for every other row the
requirement is looser than 2.5 %. A row that fails this is REPORTED, GATE
REACHED, not counted.

### 5.5 Convergence — from written fields, never residualControl

A level is CONVERGED only if `qr` on every radiating patch is **identical
value for value between the last two written checkpoints** (15 and 20; L-141).
**Every zero is controlled live: 1.234e-03 W/m² is planted into a scratch copy
of the earlier checkpoint by line index, read back off disk through the same
reader, and the recovered maximum change must EXACTLY equal the float the
plant produced, fl(old + plant) − old** — a zero from a broken reader is
indistinguishable from a real one (T1c, 2026-08-20). §12 disclosure: the first
instance's tolerance (|rec − plant| ≤ 1e-12·plant) was unsatisfiable against
the ulp of a ~6.5e3 W/m² base value and was completed to the exact-float rule
by the second instance before the freeze; the selftest exercises the plant
through both nonuniform and uniform patch entries.

---

## 6. Controls — rows that MUST fail if the rung is sound — and guards

| control | definition | expected departure |
| --- | --- | ---: |
| **C1 black-body** | S_f graded against σ(T₁⁴ − T₂⁴) = 6889.546 W/m² | **+104.17 %** |
| **C1-live** | S_C1: finest sphere case solved with ε₁ = ε₂ = 1, graded against the grey 3374.471705 | must FAIL against grey and must NOT reproduce S_f; **if it reproduces S_f, the emissivity dictionary is unread and every sphere row is VOID / BLOCKED** |
| **C2 spheres** | S_f against the parallel-plate network 2175.646 W/m² | **−35.53 %** (S1: 157.90 %) |
| **C2 box** | B_f against the cube-matrix fluxes (0.19982490 / 0.20004378) | **−2.30 / −40.89 / −40.95 / −25.59 %** |
| C2b (reported) | B_f against opposite-only | +6.24 / +110.98 / −100 / −100 % |
| **C3a trivial baseline (Charter §2c) — MUST FAIL** | a qr ≡ 0 field through the identical pipeline | **−100 % on every row** |
| **C3b trivial baseline — MUST FAIL** | B_C3: the finest box SOLVED with all six patches at 300 K; every registered flux is 0 by symmetry | every graded box row must fail it; also the cleanest test that the solver's qr is zero when it must be |

**Guards (withdraw the RUN, never counted):**

- **closure** (INTERPRETATION 6, resolved and refined at build as its own
  approved wording required — "tighten after the first level's row-sum defect
  is known, before any graded solve"; approved by Sanaa 2026-08-21 on the
  team's recommendation): the void test is
  **|c_raw − c_F| > 1e-2**, where c_raw = |Σ A q| / Σ |A q| from the solver's
  written qr and c_F is the same quantity from the comparator's own radiosity
  solve on the written F with the same areas and emissivities. The measured
  build-time row-sum defects (§5.3: up to 4.8 % at every level with smoothing
  false) mean a raw-closure threshold of 1e-2 would void a correct run for the
  utility's own quadrature defect, which the ladder and twins already measure;
  what |c_raw − c_F| voids is a run whose assembly or addressing departs from
  its own view-factor matrix — the Charter §2c GUARD referent. **c_raw is
  ALWAYS printed** beside the row-sum defect, and c_raw > 1e-2 is flagged in
  the report.
- **row sums and reciprocity of the written F** at every level, reported
  (build-time values in §5.3).
- **convergence and the planted 1.234e-03 W/m² control** (§5.5); a failed
  plant is a comparator REFUSAL, not a graded row.
- **mesh read-back**: §5.1's table, re-checked by the comparator at analysis
  (sphere vertex radii to 1e-9 relative, box extents to 1e-12, refusal on
  mismatch).
- **stale-write guard** (L-143): launcher and runner refuse any numeric time
  directory other than 0 (G3), refuse a case another process is working in
  (G2), refuse without / duplicate the atomic launch lock (G1); the runner
  additionally refuses a case with no `constant/F`; `mark_done_t10a.py`
  refuses final-time fields older than the case's own `0/T`, which the runner
  re-copies at the start of the run allowed to answer.
- **pair symmetry** on B2/B3: both walls of each pair reported with their
  difference.

## 7. Falsifying outcomes and §8 carried-forward rules

Registered unchanged from the draft (§7 and §8 there): the
spheres-pass/box-fails and box-passes/spheres-fail attributions via
Python-on-F; the same-sign-both-fail constant check (σ, sign, wrong time);
STAGNANT ladders as the quadrature floor dominating (NOT A RESULT, no band
improvised); S_C1 reproducing S_f as BLOCKED; clean row sums with failed
closure as an addressing fault; everything-passes-below-1e-6 as the identity
signature reported as a question. **If none of these patterns appears and a
row still fails, the honest report is GATE FAIL with no identified cause.**

---

## 9. What this rung cannot see

- **No participating media** (absorption, emission, scattering; fvDOM/P1) —
  that is T10b and beyond.
- **No spectral or non-grey behaviour**: nBands 1, one grey emissivity per
  surface, no specular reflection.
- **No coupling to convection or conduction**: every wall T is imposed, the
  fluid is inert, nothing responds to qr. Combined modes are T10b; conjugate
  walls T9b/T9c.
- **No grey non-symmetric enclosure** — no exact answer exists; the grey path
  is graded on the spheres, the geometric path on the black box, and their
  product on an arbitrary room is not thereby validated.
- **Nothing about faceAgglomerate**, deliberately bypassed; a production case
  that agglomerates inherits an approximation this rung did not grade.
- **Nothing about the iterative (non-direct) radiosity solver or parallel
  operation**: useDirectSolver true, serial, one region.

---

## 10. Budget — preprocessing MEASURED, solve PREDICTED

**Measured at build (2026-08-21, serial, nice 10, load average ~17 on 16
cores from the concurrently running T3 rung — these are contended upper
bounds):** blockMesh + checkMesh ≤ 5.2 s per case; view-factor generation
S_c/S_m/S_f 7.1/15.7/108.2 s, S_C1 82.3 s, S_f_q 64.6 s, S_f_s 62.7 s,
B_c/B_m/B_f 1.5/7.8/49.7 s, B_C3 50.5 s, B_f_q 52.3 s, B_f_s 55.7 s, H_2d
0.1 s. **Total preprocessing 9.4 core-minutes, spent; recorded per case in
BUILD.txt.** Largest `constant/F` 923 MB ascii; run tree 6.4 GB.

**Predicted solve, basis named:** the smoke test (§12.3) measured 1.35 s for
20 iterations of S_c (1 200 faces) and 0.15 s for H_2d; the fine cases add a
one-off dense LU of the cached C matrix (8 112² or 7 056²), which scales as
n³ from S_c's share: **predicted 3-6 min per sphere-fine case, 2-4 min per
box-fine case, seconds for coarse/medium — total predicted solve ≤ 35
core-minutes, grand total ≤ 45 core-minutes ≈ $0.04 at T1b's measured
$0.051 per core-hour** (`T1b_ATTEMPT1_MESH_FAULT.md`: 56.6 core-hours ≈
$2.90 — the named throughput figure). Peak solver memory ≈ 1.1 GB at S_f
(dense F plus its LU copy), against 30 GB on the host. A solve exceeding this
prediction by more than 10× is stopped and investigated, not waited out.

---

## 11. INTERPRETATION 1..7 — resolved at freeze

Each decision below is frozen in the draft's §11 recommended reading, and each
carries the same approval: **approved by Sanaa 2026-08-21 on the team's
recommendation.**

1. **Geometry of T10a-1: concentric spheres**, not parallel plates or
   concentric cylinders (§1.2). Approved by Sanaa 2026-08-21 on the team's
   recommendation.
2. **Solver path: buoyantSimpleFoam + viewFactor, g = 0, fixed-T walls, inert
   air, single region** (§4). Approved by Sanaa 2026-08-21 on the team's
   recommendation.
3. **Graded with smoothing false; smoothing true reported** (finest twins
   S_f_s, B_f_s) (§5.3). Approved by Sanaa 2026-08-21 on the team's
   recommendation.
4. **No faceAgglomerate**: one radiating face per mesh face (§4). Approved by
   Sanaa 2026-08-21 on the team's recommendation.
5. **T10a-3, the 2D Hottel rectangle, kept and REPORTED ONLY** (§3.1,
   including the identity-claim amendment recorded there). Approved by Sanaa
   2026-08-21 on the team's recommendation.
6. **Closure guard threshold 1e-2 relative**, with the number always printed,
   and the reading's own instruction — revisit once the first level's row-sum
   defect is known, before any graded solve — executed at build: referent
   refined to |c_raw − c_F| (§6), raw closure always reported. Approved by
   Sanaa 2026-08-21 on the team's recommendation.
7. **Emissivities 0.6 / 0.4, radius ratio 0.5, box 1 × 1 × 0.5 m at
   600 / 300 / 400 / 350 K** (§2-3), with the stated choice criteria.
   Approved by Sanaa 2026-08-21 on the team's recommendation.

---

## 12. Status: FROZEN, BUILT, MESH-VERIFIED, NOT RUN

**Frozen 2026-08-21. Built: 13 cases, meshed, checkMesh rc = 0 on all,
view-factor matrices generated (9.4 core-minutes of preprocessing, the only
compute spent). Mesh-verified: `check_t10a_mesh.py` exit 0 with all three
planted positives fired. NOT RUN: no solver has been launched in the run
tree; no case holds any time directory; every graded number in this document
is closed-form theory, not a measurement.**

### 12.0 Two-instance authorship, disclosed

**This rung was specified across two sessions and an interruption.** The
Fable supervisor session drafted `T10a_PREREGISTRATION_DRAFT.md` on
2026-08-20. A first execution instance began promoting it on 2026-08-21 and
**was killed by a session limit at about 18:20 UTC mid-write**, leaving
`exact_t10a.py`, `T10a_registered.json` and `analyse_t10a.py` in the run tree
— with no builder, no frozen pre-registration, no cases and no solve. A
second instance (this author) validated those three files against the draft
and completed the rung the same day, **before any freeze and before any case
existed** (Charter §2b's condition, checked: the tree held only those three
files and `__pycache__`). Specifically, the second instance:

- **ran `exact_t10a.py`** — every reference derived two independent ways,
  every registered decimal matched (exit 0);
- **diffed `T10a_registered.json` against the draft's §2-3 tables** — all
  registered values identical; its two additions beyond the draft are
  recorded here: (a) EXACT added to the non-CONVERGING triple states (stricter
  than the draft's list, consistent with D440), (b) the closure-guard referent
  refinement now in §6. One assertion in it — build-time row-sum defects
  "2-5 % at the coarse levels", written before any build existed — was
  **corrected to the measured figures** (§5.3) by the second instance before
  the freeze, and the JSON says so on its face;
- **completed `analyse_t10a.py`**: the planted-control equality test was
  unsatisfiable as left (1e-15-scale tolerance against a 9.1e-13 ulp) and was
  finished as the exact-float rule of §5.5; nothing on any other part of the
  grading path was changed;
- wrote `build_t10a.py`, `check_t10a_mesh.py`, `mark_done_t10a.py`,
  `launch_t10a.sh`, `run_one_t10a.sh`, built and mesh-verified the 13 cases,
  ran the disclosed smoke test (§12.3), and froze this document.

### 12.1 The freeze set — commit BEFORE any solve (Charter §2d)

    docs/campaigns/T-family/T10a_PREREGISTRATION.md
    verification/runs/T-family/T10a_runs/exact_t10a.py
    verification/runs/T-family/T10a_runs/T10a_registered.json
    verification/runs/T-family/T10a_runs/analyse_t10a.py
    verification/runs/T-family/T10a_runs/build_t10a.py
    verification/runs/T-family/T10a_runs/check_t10a_mesh.py
    verification/runs/T-family/T10a_runs/mark_done_t10a.py
    verification/runs/T-family/T10a_runs/launch_t10a.sh
    verification/runs/T-family/T10a_runs/run_one_t10a.sh

sha256 prefixes at freeze: exact 8efb4d61d445, registered bdfbd8120ff2,
analyse 674bac302193, build 534947076a53, check 346363b6e9f7, mark_done
7659ccc86162, launch d66eddab002c, run_one 61c2695a8238. **The 6.4 GB of case
trees are NOT for the index**: dictionaries and meshes are reproduced by the
committed builder, and each case's BUILD.txt + logs carry the generator
provenance; the comparator reads the F actually on disk and its provenance is
those logs. 2d's enforcement test applies: the freeze commit must predate the
earliest completion marker, and the comparator hash at analysis time must
match the committed blob.

### 12.2 Instrument evidence at freeze

- `analyse_t10a.py --selftest`: **PASSED, 24/24** — OSCILLATORY / STAGNANT /
  DIVERGENT / EXACT triples each return NOT A RESULT with the fine value
  sitting exactly on the reference; CONVERGING reaches PASS inside the band
  and GATE FAIL outside it (reachable both ways); an unconverged level and a
  closure-voided level each force NOT A RESULT; the quadrature-floor and
  discrimination gates return GATE REACHED; the readers parse a synthetic
  polyMesh, F/globalFaceFaces, uniform and nonuniform qr; the planted
  1.234e-03 is recovered exactly through the reader both ways; a 3e-7
  checkpoint drift reads NOT_CONVERGED; σ read from etc/controlDict matches
  the registered σ_OF.
- `analyse_t10a.py` (main): refuses today with **"rung is PENDING -- no
  completion marker for S_c, ..."** after re-deriving every reference — the
  no-DONE-marker refusal works.
- `check_t10a_mesh.py`: exit 0; §5.1's table; three planted positives fired
  (scaled sphere points, scaled box points, overridden emissivity). One
  checker defect found and fixed during this verification (plane counting by
  round(x, 15) over-counted planes of non-dyadic spacings by 1 ulp; replaced
  by 1e-9 clustering) — a checker bug, not a mesh fault: cell counts, extents
  and areas were right throughout.

### 12.3 Compute and answer-adjacent reads before the freeze, disclosed

- **Preprocessing (allowed, mesh-side):** blockMesh, checkMesh and the
  view-factor generators ran per case at build; 9.4 core-minutes; wall times
  in §10 and per-case BUILD.txt. The generator's 0/viewFactorField was moved
  to viewFactorField.build and the empty 0/ removed, so the tree holds no
  time directory.
- **Tooling smoke test (scratch only, deleted):** copies of S_c and H_2d ran
  buoyantSimpleFoam for exactly 20 iterations each in the session scratchpad
  (t10a_smoke/), 1.35 s and 0.15 s; both wrote checkpoints 5/10/15/20 with
  qr identical between 15 and 20, 20 ExecutionTime lines and an End line
  (mark_done's tests 2-5 will pass on real runs). The copies and their time
  directories were deleted afterwards; nothing in the run tree was touched.
- **Answer-adjacent numbers seen by this author before the freeze, listed
  exhaustively:** the S_c coarse-level fluxes (Python-on-F 3316.2500 /
  −906.0223 W/m², and the smoke solve's identical 3316.249996 — which also
  demonstrates the attribution lever's Python assembly agrees with the solver
  to 10 significant figures at the coarse level); the H_2d fluxes in §3.1;
  and the raw row-sum defects of every case (§5.3). **No medium- or
  fine-level flux, no radiosity solve on any F beyond S_c, and no graded
  quantity has been computed.** The graded bands cannot have been tuned to
  these: the bands are derived from the solver ladder by the frozen rule, the
  references are closed form, and the verdict logic predates the builds in
  the first instance's comparator. The residual exposure — that the F
  matrices plus registered temperatures determine the answers in principle —
  is exactly why the freeze set above must be committed before any solve, and
  why the comparator re-derives, refuses and self-tests rather than trusting
  this document.

**Ordering note:** `T_FAMILY_INDEX.md` recommends pulling T10a forward; that
recommendation is recorded, not applied, and this rung displaces nothing. **A
plan is not a capability**: T10a is a capability only when it has reported.
