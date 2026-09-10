# M6 GRID (b) — LE- AND SHOCK-RESOLVED, y+<1 TEST GRID (Sanaa's grid-vs-model ruling, option b)

> ## 🟡 THIS FILE IS A **DRAFT** AND **UNFROZEN**.
> No gate, threshold, cap or label in it is in force. It registers a MESH-GENERATION recipe
> and its intended eventual-solve gates for the cfd-supervisor to FREEZE (rule 2) when the
> solve is sequenced. **Freezing this document — committing the gate, threshold, cap and label
> before any solve, and hashing the grading path against its committed blob — is the
> supervisor's personal check-4 and is NOT delegated.** No message from this lane, or from any
> agent, is Sanaa's consent (rule 9).
>
> Drafted by a cfd `lab-lane` on the cfd-supervisor's grid-(b) brief and Sanaa's refined ruling
> (via chief, 2026-09-09). **NO SOLVER HAS RUN. NO PRODUCTION MESH HAS BEEN GENERATED.** A
> single cheap coarse dry-run was done to prove the recipe (§3.4, §6).

---

## 0. WHY THIS FAMILY EXISTS — SANAA'S GRID-vs-MODEL RULING, OPTION (b)

The lab's own-family pyHyp mesh (71,760 / 574,080 cells, AR ~305, y+~35 wall-function, faceted
1,560-face parent surface with NO leading-edge clustering) **under-resolves the M6 leading-edge
suction peak by 20–60× the ±0.02 `Cp` band and diverges under uniform refinement**. Sanaa
classified this a **MESH LIMITATION** (not a model-form error) and ordered option (b): a
**properly resolved test grid**. Her refined ruling (via chief, 2026-09-09):

1. **RE-BASE on the A3 primal-validated M6 mesh lineage** — do NOT build a from-scratch O-grid
   off a generic M6 definition. Use the A3 surface whose primal `Cp` validated vs AGARD.
2. **Curvature-refine with NOSE clustering AND SHOCK clustering** — the LE suction peak
   (x/c ≈ 0.03–0.05) AND the transonic λ-shock (x/c ≈ 0.20–0.58 across span). Size BOTH from
   physics BEFORE generating.
3. **y+ < 1 (integrate-to-wall), three geometrically-similar levels from ONE script.**
4. Each level clears the hard mesh gates; the graded (finest) level passes the **new
   curvature-based surface-resolution admission check** (LE **and** shock resolved).
5. **RETIRE the own-family 72k/574k pyHyp mesh** — it is DEAD and is NOT carried forward as a
   level or a comparator.

**The own-family registration `verification/campaign/M6_OWN_FAMILY_PREREGISTRATION.md` and its
fine-triple grader `verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py` are
SUPERSEDED for grid (b).** Their measurement CORE is reused (see §5).

---

## 1. GEOMETRY PROVENANCE — THE A3 PRIMAL-VALIDATED SURFACE (READ-ONLY source)

**Starting surface:** `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/m6_surfaceMesh_fine.cgns`
- sha256 `197efa09d838b276a8967da9532d9c4d57edca18cb777bd640257606d2d83327`, 2,535,424 bytes.
- **This sha256 == `analyse_m6sr.SHA_SURFACE_MASTER` (the FROZEN grader already pins this exact
  surface, `cases/M6SR/analyse_m6sr.py:74`).** The provenance is therefore corroborated by the
  frozen instrument itself.
- **Provenance:** the canonical DAFoam ONERA-M6 surface, downloaded by that tree's
  `preProcessing.sh` from `github.com/dafoam/files` release v1.0.0
  (`m6_surfaceMesh_fine.cgns.tar.gz`). It is the surface whose **A3 primal `Cp` validated vs
  AGARD** — `A3-onera-m6-transonic/cp_comparison.json` (per-station RMS/max deviation vs the
  271 taps) and `shock_location.json` (CFD shock x/c 0.22–0.67 vs exp 0.20–0.58).
- Structure (cgns_utils info, measured): 9 zones / 101,913 nodes; the two wing surfaces are
  **257 chordwise × 161 spanwise each** (upper + lower).

**⚠ Honest limit of provenance (rule 15):** `m6_surfaceMesh_fine.cgns` is a MESH file, not a
paper — there is no title page to verify. Its provenance rests on (i) the sha256 matching the
frozen grader's `SHA_SURFACE_MASTER`, (ii) the download URL in the A3 `preProcessing.sh`, and
(iii) its A3 primal having validated vs the (title-verified, rule 15) AGARD AR-138 reference.
The AGARD reference `case_2308.dat` was independently sha- and header-verified by this lane
(sha256 `020c5fcc…` == `analyse_m6sr.SHA_CASE_2308`; ZONE header reads "Run= 308, Mach= 0.8395,
Alpha= 3.06, Re= 11.72×10**6").

**Why the A3 lineage under-resolved before, and what grid (b) changes** (measured, §3.1):
the A3 master surface already has LE clustering to Δx/c ≈ 0.0013 (adequate for the nose), but
the dead own-family **coarsened it 2× to 1,560 faces**, destroying that clustering (Δx/c ≈ 0.02
near the LE) and ran a y+~35 wall-function volume. Grid (b): (i) do NOT coarsen the master,
(ii) ADD shock-band clustering, (iii) march to y+<1.

---

## 2. PHYSICS-FIRST SIZING (deliverable 1; the input to the recipe)

Measured from `case_2308.dat` via the FROZEN grader core (`A.read_case_2308`,
`A.split_curve_upper_lower` UNCHANGED), driver
`verification/runs/M6_LE_RESOLVED_runs/size_from_physics.py`, output `PHYSICS_SIZING.json`.
Rule-3 planted control fired (a planted nose peak Cp=−9.87654 at x/c=0.037 was read back
exactly before any real read was trusted).

**Suction peak (nose), per graded station (y/b 0.44/0.65/0.80/0.90/0.96):**
- peak at **x/c 0.034–0.050**, peak `Cp` **−1.13 to −1.23**;
- LE gradient width W (Cp≈0 → peak) **0.029–0.048 x/c**;
- value-capture floor N=6 cells (effective vertex curvature 2|Cp_pk|/W²); **DESIGN N = 18
  cells** across W (floor × √4 curvature-uncertainty × 1.5 gradient-shape margin, because the
  sparse AGARD taps SMOOTH and thus under-estimate the true peak curvature);
- **DESIGN nose Δx/c = 0.0016 (≈ 1.03 mm at MAC = 0.646 m).**

**Transonic λ-shock, per station** (tap-measured, corroborated **exactly** by the A3 primal's
`shock_location.json` exp_xoc — 0.524/0.475/0.375/0.280/0.200 at y/b 0.44/0.65/0.80/0.90/0.96):
- shock sweeps **x/c 0.20 (tip) → 0.52 (inboard)**; compression-zone width W_shock 0.04–0.10;
  Cp jump 0.37–0.85; per-cell-band floor N 29–65;
- **DESIGN shock Δx/c ≈ 0.0008 (tightest station 0.90) to 0.003 (inboard).**

**Wall-normal y+<1 (flat-plate/Cf estimate):** Re=11.72e6 on MAC, Cf=0.026/Re^(1/7)=0.00254,
τ_w=127.1 Pa, u_τ=10.18 m/s, ν=1.575e-5 m²/s → **first-cell height s0 = 1.546e-6 m** (first cell
centre at y+≈0.5). Integrate-to-wall at every level.

---

## 3. THE MESH RECIPE — CURVATURE-REFINE THE A3 MASTER, y+<1 MARCH (ONE script, 3 levels)

Driver: `verification/runs/M6_LE_RESOLVED_runs/gen_m6_gridb.py`. Steps:
1. read the master surface (converted to plot3d by `cgns_utils cgns2plot3d`, READ-ONLY);
2. assemble each spanwise station's CLOSED section (lower reversed + upper);
3. build a physics-based chordwise clustering — nose Δx/c ≤ 0.0016 (built to 0.0009), shock
   band **x/c [0.13, 0.62]** (bracketing the measured 0.20–0.52) Δx/c ≤ 0.0012 (built to
   0.0010), TE tightened — and re-cluster each section by arc-length interpolation of the
   master geometry (**SHAPE is the master's; only the point DISTRIBUTION changes**);
4. loft to a refined structured surface, 3 geometrically-similar levels (chordwise ×2, spanwise
   ×2, wall-normal layers ×2 per level; **s0 fixed at 1.546e-6 for y+<1 at every level**);
5. `cgns_utils plot3d2cgns` → pyHyp hyperbolic march to y+<1 → `plot3dToFoam -noBlank` →
   `autoPatch`/`createPatch` (wing/symmetry/farfield) → `checkMesh`.

**pyHyp smoothing parameters** are the PROVEN gate-clearing set (own-family L2 cleared
non-orth 61.46° / skew 2.06 with these from this same A3 lineage): `cMax 0.1, epsE 1.0,
epsI 2.0, theta 3.0, volCoef 0.25, volBlend 0.0005, volSmoothIter 100, kspreltol 1e-4`,
`marchDist 12.0`. Only N (layers), s0 (y+<1) and the surface distribution change per grid (b).

### 3.1 THE THREE LEVELS — cells and per-level cost (rule 12)

The GRADED finest level `Lf` resolves the physics (measured density ⇒ 541 chordwise cells/surf
to meet nose+shock); the coarse ends are r=2 geometric coarsenings (a Roache coarse end is MEANT
to under-resolve; the curvature admission check is applied to the GRADED level, the hard shape
gates to EVERY level).

Exact-nesting dims (n_{i+1}=2·n_i−1 for chord/span) give surface faces ×4 and cells ×8 on
integers. **CORRECTED (dry-run finding): a y+<1 mesh at s0=1.546e-6 needs ~150 wall-normal
layers to reach the 12-unit farfield with acceptable growth** (the coarse march CONFIRMED N=150
reaches it; an earlier draft's 35/70/140 were far too few). This couples the cost to the
observed-order choice (§7). **Two families, both costed:**

**(I) ×8 3-D-refinement family (observed order) — layers 150/300/600:**

| level | n_chord/surf | n_span | n_layers | surface faces | volume cells | solve core-min | $ derived |
|---|---|---|---|---|---|---|---|
| **Lc** coarse | 140 | 45 | 150 | 12,232 | **1,834,800** | 374 | 0.320 |
| **Lm** medium | 279 | 89 | 300 | 48,928 | **14,678,400** | 2,994 | 2.560 |
| **Lf** fine (graded) | 557 | 177 | 600 | 195,712 | **117,427,200** | 23,955 | **20.48** |

**Total ×8 triple ≈ 27,324 core-min ≈ $23.4 derived** (fine level $20.5, under the $25 pre-auth).

> 🔴 **PRE-FREEZE CORRECTION 1 — 2026-09-10, cfd `lab-lane`. THE §3.1 SURFACE-FACE COUNTS OMIT
> THE TIP CAP, AND THE `Lf` COST IS UNDERSTATED BY 17 %.**
>
> **THE CONDITION FOR A PRE-FREEZE CORRECTION, AND HOW IT WAS CHECKED (rule 2).** This
> document has **never been committed**, so no committed blob exists that any gate could be
> pinned against and there is nothing to strike an addendum onto. Checked, not assumed:
> `git ls-files --error-unmatch verification/campaign/M6_LE_RESOLVED_GRIDB_PREREGISTRATION.md`
> answers *"Did you forget to 'git add'?"*, and `git log -- <that path>` returns **0 commits**.
> **No solver has run under it**, checked by naming the directories that DO NOT EXIST:
> `verification/runs/M6_LE_RESOLVED_runs/Lc/solve/0`,
> `verification/runs/M6_LE_RESOLVED_runs/Lm/solve/0`, and
> `verification/runs/M6_LE_RESOLVED_runs/Lf` — all absent, and neither solve root holds a
> single time directory. These are therefore **pre-freeze corrections, not addenda**. They
> change **no gate, no threshold, no band, no cap and no label**, and they **do not freeze**
> this document: the freeze is the cfd-supervisor's personal check-4 (rule 2, SUPERVISION §3).
>
> **WHAT IS WRONG.** The table above counts **the wing loop only**: `surface faces =
> (2·n_chord−2)·(n_span−1)`, which for `Lf` is `1112 × 176 = 195,712`. The A3 master surface
> this family is re-based on is a **9-zone** surface, and the seven zones that are not the two
> wing surfaces — the rounded tip cap, its two corner caps, the LE nose strip and the TE strip —
> carry real faces that were never counted. `plot3dToFoam` meshes them, `checkMesh` counts
> them and the solver integrates them.
>
> **HOW IT WAS RE-DERIVED (measured, not asserted).** A re-clustered 9-zone `Lf` surface was
> actually BUILT at exactly the registered resolution (chord 557, span 177) and its faces
> counted zone by zone:
> `verification/runs/M6_LE_RESOLVED_runs/build_reclustered_surface.py`, report
> `verification/runs/M6_LE_RESOLVED_runs/Lf_recluster/work/RECLUSTER_Lf.json`
> (`surface_faces_all9: 228544`, `surface_faces_wing_loop: 195712`). The wing-loop half
> reproduces the registered 195,712 exactly, which is what makes the missing 32,832 attributable
> to the omitted zones and not to a different surface.
>
> 🔴 STRUCK BY QUOTE: ~~"| **Lc** coarse | 140 | 45 | 150 | 12,232 | **1,834,800** | 374 | 0.320 |
> | **Lm** medium | 279 | 89 | 300 | 48,928 | **14,678,400** | 2,994 | 2.560 |
> | **Lf** fine (graded) | 557 | 177 | 600 | 195,712 | **117,427,200** | 23,955 | **20.48** |"~~
> and ~~"**Total ×8 triple ≈ 27,324 core-min ≈ $23.4 derived** (fine level $20.5, under the $25
> pre-auth)."~~
>
> **CORRECTED TABLE — family (I) ×8, ALL 9 ZONES.** The wrap family (the 17 points that wrap the
> nose strip and the cap collars) is coarsened WITH the family, 5 / 9 / 17, which is what keeps
> the exact nesting the row above claims:
>
> | level | n_chord/surf | n_span | n_wrap | n_layers | wing-loop faces | tip+strip faces | **surface faces** | **volume cells** | solve core-min | $ derived |
> |---|---|---|---|---|---|---|---|---|---|---|
> | **Lc** coarse | 140 | 45 | 5 | 150 | 12,232 | 2,052 | **14,284** | **2,142,600** | 437.1 | 0.374 |
> | **Lm** medium | 279 | 89 | 9 | 300 | 48,928 | 8,208 | **57,136** | **17,140,800** | 3,496.7 | 2.990 |
> | **Lf** fine (graded) | 557 | 177 | 17 | 600 | 195,712 | 32,832 | **228,544** | **137,126,400** | 27,973.8 | **23.918** |
>
> **Total ×8 triple ≈ 31,908 core-min ≈ $27.28 derived** (same cost basis: 3.40e-8
> core-min/cell/iteration, 6,000 iterations, $0.0513/core-h; **dollars DERIVED, NOT MEASURED** —
> the box cannot read its own billing, COMPUTE_BUDGET_CHARTER §5).
>
> **NESTING IS UNHARMED, and that was checked rather than hoped.** faces 14,284 → 57,136 →
> 228,544 is **×4.000000 exactly**, cells 2,142,600 → 17,140,800 → 137,126,400 is **×8.000000
> exactly**. Holding the wrap at 17 on every level instead (20,824 / 65,600 / 228,544) would
> break it — ×3.15 and ×3.48 — so the wrap coarsening is load-bearing and is now written down.
>
> **WHAT THIS DOES TO THE PRE-AUTHORISATION CLAIM.** `Lf` is **$23.92**, not $20.48. It is still
> under the $25 per-run pre-authorisation, but on **$1.08 of margin, not $4.52** — a 4× thinner
> margin, and thin enough that any further increase in `Lf` (more layers, a finer wrap, a
> restart) crosses it. **No cap and no gate is moved by this correction**; the sequencing
> decision on that margin is the supervisor's.

**(II) surface-only family (M6SR-style lower-bound band) — fixed ~150 layers, cells ×4:** Lc
1.83M / Lm 7.34M / Lf 29.4M; **total ≈ 7,860 core-min ≈ $6.7 derived** (fine $5.1).

**Cost basis:** measured rate 3.40e-8 core-min/cell/iteration (A3-onera-m6-transonic
run_model_run3.log; `M6SR_PREREGISTRATION.md:462`), 6,000 iterations, $0.0513/core-h, **dollars
DERIVED not measured** (COMPUTE_BUDGET_CHARTER §5).

> ⚠ **FLAG (corrected cost).** My first draft quoted ~$5.6 — that was the **surface-only** cost
> mislabelled; the ×8 **observed-order** family the grader wrapper grades is **~$23.4** (fine
> $20.5, under $25/level, inside the $1,000 IBL envelope). The gap from Sanaa's ~$1 target comes
> from **her own added shock + y+<1 requirements** (physics sizing governs; not scope creep). The
> choice between family (I) ×8 (observed order, $23) and (II) surface-only ($6.7, lower-bound
> band) is the §7 observed-order decision — **now cost-quantified for Sanaa / verification.**

### 3.4 DRY-RUN — WHAT THE COARSE SMOKE PROVED (sub-$1, costed)

- 🔴 **SEE PRE-FREEZE CORRECTIONS 2 AND 3 BELOW — this bullet's count is wrong and its
  verdict must not be cited.** ~~**Curvature admission check on the GRADED (fine) surface: PASS.** All 180 sections
  ADMISSIBLE — nose Δx/c 0.00098 (≤0.0016), cells across LE radius 8 (≥8), shock-band Δx/c
  0.00097 (≤0.0012). The coarse end `Lc` is correctly REFUSED (nose 0.0119, shock 0.0039) —
  it is the deliberately under-resolved coarse end. Rule-3 controls fired on every run
  (coarse-nose REFUSED, fine-nose PASS). Report: `CURVCHECK_Lf.json`. Cost: negligible (host
  Python, seconds).~~
- **Hard-gate (checkMesh) proof: march STALL solved; a y+<1 NON-ORTHOGONALITY OBSTACLE found.**
  Two coarse y+<1 dry-runs on the A3 lineage (one-coarsen, 6,240-face surface, s0=1.546e-6):
  1. **Stall solved.** With **N=150, cMax=0.15** the march REACHES the farfield (March Distance
     12.0 at layer 150, Min Quality 0.410, positive volumes) — the earlier stall was too few
     layers, fixed.
  2. **checkMesh on the completed 929,760-cell mesh: skewness 1.44 (OK, <4), 0 negative volumes,
     regions 1 — but MAX NON-ORTHOGONALITY 87.19° (avg 15.09°) FAILS the 70° hard gate**, and max
     aspect ratio 10,069 (advisory, expected for y+<1). **Finding:** the tiny y+<1 first cell
     (s0=1.546e-6, wall-normal AR ~10⁴) drives a localized cluster of near-wall cells to ~87°
     non-orthogonality where the surface curves (LE/tip) — the own-family avoided this by running
     y+~35 (s0=2e-4, 61.46°).
  3. **Stronger-smoothing / gentler-march retune (N=200, cMax=0.1, epsE=2, epsI=4,
     volSmoothIter=300): max non-orthogonality 87.66° (avg 15.03°) — STILL FAILS, marginally
     worse.** So across TWO independent parameter regimes the y+<1 march sits at ~87°.
  - **CONCLUSION: this is a STRUCTURAL y+<1-vs-non-orthogonality tension on the pyHyp hyperbolic
    route, not a tuning miss** (two smoothing regimes both ~87°; the localized 1,062–1,394-cell
    near-wall cluster at ~87° is inherent to the s0=1.5e-6 first cell against a curved surface).
    The march STALL is solved and skewness/volumes are clean; **the 70° non-orthogonality gate is
    the blocker for a y+<1 mesh on this route.** Flagged for the supervisor / Sanaa (§9 item 5).
    Cost ~30 core-min across the dry-runs (~$0.03 derived), sub-$1.

> 🔴 **PRE-FREEZE CORRECTION 2 — 2026-09-10, cfd `lab-lane`. §3.4's "All 180 sections" IS 177.**
>
> The artifact holds **177** sections, not 180: `CURVCHECK_Lf.json` field `"n_sections": 177`,
> and `sections_Lf.json` deserialises to 177 entries of 1,113 points. A count that does not match
> its own artifact cannot be cited, whichever way it errs.
>
> 🔴 STRUCK BY QUOTE: ~~"All 180 sections ADMISSIBLE"~~ → **All 177 sections were reported
> ADMISSIBLE** — and see CORRECTION 3, which is why that verdict must not be cited at all.

> 🔴 **PRE-FREEZE CORRECTION 3 — 2026-09-10, cfd `lab-lane`. `CURVCHECK_Lf.json`'s HEADLINE
> NUMBERS ARE THE SYNTHETIC PLANTED CONTROL, NOT THE M6, AND ITS SECTION LIST HAS NO LEADING
> EDGE. THE `ADMISSIBLE` VERDICT MUST NOT BE CITED AS EVIDENCE THAT A BUILDABLE CLUSTERED
> SURFACE EXISTS.**
>
> **(a) The headline numbers are a control.** `CURVCHECK_Lf.json`'s eye-catching
> `nose_dx_over_c = 5.799e-14`, `cells_across_LE_radius = 443` and
> `shock_band_max_dx_over_c = 3.929e-04` sit under the key **`rule3_controls.fine_control`**.
> They are produced by `scripts/check_le_surface_resolution.py:253`,
> `_synthetic_section(n_per_surface=900, le_cluster=2.4, shock_cluster=True)` — a **synthetic
> analytic section**, not the M6. The rule-3 control is working exactly as intended; what is
> wrong is quoting its numbers as the mesh's.
>
> **THE REAL M6 NUMBERS, stated separately and without the control anywhere near them**
> (`CURVCHECK_Lf.json`, `per_section[0].metrics`): **nose Δx/c = 9.874e-04**,
> **shock-band max Δx/c = 9.739e-04**, **cells across the LE radius = 8**. Those are the values
> §3.4 actually meant, and they do clear the registered thresholds.
>
> **(b) But the section list they were measured on is not a buildable surface.** Measured on
> `verification/runs/M6_LE_RESOLVED_runs/sections_Lf.json`:
> * **NO LEADING EDGE.** `gen_m6_gridb.py:147` (`master_surface_blocks`) keeps only the two
>   largest zones and **discards master zone 2, the 161×17 LE nose strip**. Each section
>   therefore jumps from the lower surface to the upper surface across a **single straight
>   segment of 0.0283 c** (section 0: index 556→557, from x=0.00495, y=−0.01092 to x=0.00574,
>   y=+0.01170). The 1-D chordwise clustering LAW clears the gate; the surface it was measured
>   on has the nose cut out of it.
> * **16 DUPLICATE SECTIONS.** `gen_m6_gridb.py:167` (`chord_line`) **snaps** to
>   `int(round(span_frac*(nspan-1)))` instead of interpolating in span, so the 177 requested
>   stations hold only **161 distinct** ones and **16 are exact byte-for-byte duplicates**
>   (measured by `numpy` on the section arrays, and by 161 unique span z of 177).
> * `gen_m6_gridb.py:236` resamples **linearly in x/c**, not in arc length.
>
> **CONSEQUENCE, and it is narrow on purpose.** `CURVCHECK_Lf.json`'s `ADMISSIBLE` verdict is
> **NOT** evidence that a buildable, LE-carrying, clustered `Lf` surface exists, and §3.4 must
> not be read as if it were. It is not withdrawn as a check of the clustering law. **The
> separate, buildable evidence now on disk** is the re-clustered 9-zone surface
> (`build_reclustered_surface.py`, `Lf_recluster/work/RECLUSTER_Lf.json`), which HAS the nose
> strip, has **177 distinct** span stations, and measures **nose Δx/c 1.256e-03 (≤0.0016)** and
> **shock-band Δx/c 9.788e-04 (≤0.0012)** — worst over all 177 stations, not at one of them.
> **No threshold is moved by any of this.**

> 🔴 **PRE-FREEZE CORRECTION 4 — 2026-09-10, cfd `lab-lane`. §3.4's "STRUCTURAL TENSION"
> CONCLUSION IS SUPERSEDED BY MEASUREMENT. A y+<1 MESH CLEARS THE 70° GATE ON THIS ROUTE.**
>
> 🔴 STRUCK BY QUOTE: ~~"**CONCLUSION: this is a STRUCTURAL y+<1-vs-non-orthogonality tension on
> the pyHyp hyperbolic route, not a tuning miss** (two smoothing regimes both ~87°; the localized
> 1,062–1,394-cell near-wall cluster at ~87° is inherent to the s0=1.5e-6 first cell against a
> curved surface). ... **the 70° non-orthogonality gate is the blocker for a y+<1 mesh on this
> route.**"~~
>
> **THE ORIGINAL TEXT IS STRUCK, NOT DELETED, and its two 87° measurements stand as measured.**
> What is wrong is the *inference* drawn from them, and it was wrong in the strongest way an
> inference can be: a third route was not tried. Both 87° runs marched **directly at
> s0 = 1.546e-6**. They therefore measured that route, and only that route.
>
> **THE MEASUREMENT THAT SUPERSEDES IT.** Marching at the well-behaved **y+~35** first cell
> (s0 = 1.0e-4) and then **respacing the wall-normal distribution to y+<1 afterwards**
> (`verification/runs/M6_LE_RESOLVED_runs/respace_wallnormal.py`) produces y+<1 meshes that
> **CLEAR the 70° hard gate at both levels built so far**:
>
> | level | cells | max non-orthogonality | max skewness | min cell volume | max aspect ratio (advisory) |
> |---|---|---|---|---|---|
> | `Lc` | 936,000 | **63.94726886790374°** | 1.441392914429642 | 1.811e-13 (`Cell volumes OK.`) | 9,816.6 on 1,086 cells |
> | `Lm` | 7,488,000 | **60.97416318542714°** | 1.441904873677684 | 4.295e-14 (`Cell volumes OK.`) | 6,659.4 on 3,186 cells |
>
> Logs: `verification/runs/M6_LE_RESOLVED_runs/Lc/solve/log.checkMesh` and `.../Lm/solve/log.checkMesh`
> (committed copies, since `log.*` under a run root is gitignored:
> `Lc/work/CHECKMESH_Lc_MEASURED.txt`, `Lm/work/CHECKMESH_Lm_MEASURED.txt`).
>
> Both are under 70°, by 6.05° and 9.03° respectively — margins, not squeakers, and the two levels
> move in the right direction under refinement. **The 70° gate is therefore NOT the blocker for a
> y+<1 mesh on this route**; the march regime was.
>
> **STATED PLAINLY BECAUSE IT WOULD OTHERWISE READ AS A CLEAN SWEEP:** `checkMesh` reports
> **`Failed 1 mesh checks`** at BOTH levels. That one failure is the **high-aspect-ratio
> advisory**, which §3.4 already records as expected for a y+<1 mesh (`Max aspect ratio 10,069`
> in the original dry-run). It is **not** the non-orthogonality gate and it is not a negative
> volume — `Cell volumes OK.` at both levels, no negative-volume line at either. Whether the
> aspect-ratio advisory is acceptable is a §5/§7 question, untouched here.
>
> **WHAT IS NOT CLAIMED.** `Lf` has not been built, so nothing here says the ×8 fine end will
> also clear 70°; and this correction moves **no gate and no threshold** — the 70° hard gate and
> every band in §5 stand exactly as drafted. It removes an obstacle that the draft recorded as
> structural and that measurement says is not.

---

## 4. THE DELIVERABLE — M6 `Cp` AT THE AGARD SPAN STATIONS, WITH THE FAMILY BAND

Span stations (AGARD AR-138 B1): **y/b = 0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99**, 271
pressure orifices in 7 sections. The section→y/b mapping (A-MAP) is INHERITED from the frozen
`M6SR` / own-family registrations, NOT re-opened.

---

## 5. INTENDED GATES — TRANSCRIBED BYTE-IDENTICAL FROM THE FROZEN M6 GATE (T25, no threshold move)

- **Solver:** `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST**, fully turbulent.
- **Momentum divSchemes:** `bounded Gauss linearUpwind grad(U)` (second order).
- **Flow:** M∞ = 0.8395, α = 3.06°, Re = 11.72×10⁶ (test 2308).
- **Gate P (Sanaa's deliverable):** M6 surface `Cp` vs the 271 AR-138 tapped values, with the
  grid-family band on every station.
  - **reference accuracy `ΔCp = ±0.02`** — AR-138 B1-4 §6.1, published. **UNCHANGED (T25 — no
    threshold move); widening a gate is reserved to Sanaa (rule 9).**
  - **Gate P graded on x/c ≤ 0.90;** the rear 10 % plotted and reported, never graded.
  - **Gate P sits BEHIND Gate G.** A PASS on a family that is not `CONVERGING` is `NOT A RESULT`
    (rule 5).
- **Gate G (Roache triple):** the three-level grid-(b) family must be `CONVERGING`; a
  non-`CONVERGING` triple is `NOT A RESULT` whatever its value. GCI at Fs = 1.25.

The exact gate literal is pinned by hashing the frozen source registration at freeze; the
supervisor sets and signs it at check-4. This DRAFT sets no number of its own.

### 5.1 GRADING PATH — HOW THE FROZEN GRADER APPLIES TO GRID (b) [SUPERVISOR RULING NEEDED]

The pinned **measurement CORE** is `cases/M6SR/analyse_m6sr.py` (git blob
`8007b23da5bb3173dacb6eda1d67ca5d90ce9139`): `read_case_2308` (271 taps, sha-refused),
`d1_discriminator`, `cfd_sections_for_case`, `gate_p`, `set_to_set_assignment`, `roache_triple`,
`gci_fine_from_gate_g`, `completion_clauses`, the planted controls — **all UNCHANGED**.

The own-family grader `analyse_m6_own_family.py` (blob `da0df95c…`) is a **thin adaptation
layer** over that core, HARD-WIRED to the DEAD own-family: its `_discover_levels_own_family`
pins level ids `L2/L1/L0`, run root `M6_OWN_FAMILY_runs/L{2,1,0}/solve`, cell counts
`(71760, 574080, 4592640)`, patch names `{wing, symmetry, farfield}` and endTimes `6000`.
**Grid (b) has DIFFERENT level ids, run root, and cell counts (428,120 / 3,476,340 / 28,017,080),
so `analyse_m6_own_family.py` as-invoked CANNOT grade grid (b)** — its `refinement_ratio_own_family`
and `completion_clauses` would refuse on the count/path mismatch.

**Two rule-2-compliant options; this DRAFT recommends (b):**
- **(a) place grid-(b) meshes at the own-family expected paths** and reuse
  `analyse_m6_own_family.py` — **NOT viable:** that grader's cell counts are hard-wired to the
  own-family triple; grid (b) does not match them and the derived-ratio guard would refuse.
- **(b) author a new thin READ-ONLY wrapper `analyse_m6_gridb.py`** that IMPORTS the frozen core
  `analyse_m6sr.py` UNCHANGED and supplies grid-(b)'s own level ids/paths/cell counts/patch
  names/endTimes, grading Gate P via `A.gate_p` / `A.set_to_set_assignment` and Gate G via
  `A.roache_triple` — **exactly the pattern `analyse_m6_own_family.py` itself was authored under**
  (its docstring cites the frozen `M6SR` §12.3 ruling and the **T23G2R re-pin precedent**: an
  own-family harness "must be authored and pass check-1 before any grade, and be pinned by a
  dated FREEZE ADDENDUM that re-pins the grading-path blob and alters no gate/threshold/band/
  cap/label"). Gate P ±0.02 and the 271 taps are the core's `gate_p`/`read_case_2308`, UNCHANGED.
  The existing read-only diagnostic `verification/runs/M6_OWN_FAMILY_runs/L2_arfix_diag/gatep_diag_n5.py`
  is the working precedent for such a wrapper (imports the core, re-hashes both blobs, plants a
  live rule-3 control before any read).

**→ Supervisor's check-4 ruling required:** confirm option (b), and that authoring
`analyse_m6_gridb.py` + passing check-1 + pinning it by a dated FREEZE ADDENDUM (re-pinning the
grading-path blob, altering no gate/threshold/band/cap/label) is the lawful grading path. This
lane did NOT author that wrapper (it grades nothing until the supervisor rules).

---

## 6. §2ba / §2bb / COMPLETION — MONITOR, AUTOGRADER, PRE-FLIGHT

- **§2ba (monitor + committed detached autograder):** the own-family precedent
  `verification/runs/M6_OWN_FAMILY_runs/autograde_watch_m6_own_family.sh` (setsid-detached,
  survives fleet death, invokes the PINNED grader with rc captured inside the wrapper) is
  adapted to grid (b)'s run root and grader at freeze. It grades NOTHING itself.
- **§2bb (per-rung pre-flight):** the frozen core's **Section-7 launch screen** (patch types,
  boundary openness ≤1e-12, regions==1, min cell volume >0, patch names) runs per level BEFORE
  each solve and can only turn a launch OFF (rule 5). Grid (b)'s wrapper carries the own-family
  patch-name set {wing, symmetry, farfield}.
- **Completion (rule 4), registered:** `rhoSimpleFoam` unit-step SIMPLE, **deltaT = 1**,
  **endTime = 6,000** per level (the §3.1 cost basis; the supervisor confirms/raises for Lf
  plateau at check-4). The core's `completion_clauses` requires rc=0, an `End` line, last time
  == endTime, `ExecutionTime` count == endTime, RULE4_FIELDS present at the endTime dir, and the
  age guard (every field newer than the case's own `0/U`). A run failing any clause is REFUSED
  (exit 2), never degraded.

---

## 7. CAP AND LABEL

- **Cap:** the 3-level solve is costed at **~6,512 core-min ≈ $5.57 derived** (§3.1); with a
  generous ×1.5 restart allowance ≈ $8.4 derived, inside the $1,000 IBL envelope; **each level
  under the $25 pre-auth.** An overrun STOPS the run (rule 12); it does not get a new budget.
- **Label:** grid (b) is an r=2 three-level family refining chordwise ×2, spanwise ×2 AND
  wall-normal layers ×2 per level. **⚠ Observed-order caveat (verification-owned, flagged):**
  s0 is held FIXED at 1.546e-6 for y+<1 at every level (Sanaa's integrate-to-wall directive),
  so the wall-normal FIRST cell does not scale with the level — the wall-normal refinement comes
  from layer count / outer spacing. Whether the resulting Gate-G order is a full observed order
  or carries the own-family §4.1-style honest caveat is a **rule-5 / verification-team question**
  the supervisor refers before freeze; this DRAFT does not decide it.

---

## 8. WHAT IS AND IS NOT DONE

- **DONE (drafts/instruments for the supervisor):** physics sizing (nose+shock, rule-3 control
  fired); the curvature admission check `scripts/check_le_surface_resolution.py` (LE curvature +
  nose Δx/c + shock-band Δx/c, rule-3 planted+positive controls firing); the mesh-gen recipe
  `gen_m6_gridb.py` (3 levels, cells + cost); the coarse dry-run proving the graded surface
  clears the curvature check; this DRAFT.
- **DONE since:** the grading wrapper `analyse_m6_gridb.py` AUTHORED (imports the frozen core
  UNCHANGED, re-hash-pins both blobs da0df95c + 8007b23d and refuses on drift, live rule-3 plant
  on the actual fields, A's Cp pipeline + Gate P ±0.02 UNCHANGED, grid-b counts as local
  constants; A's planted controls fire, `--grade` on missing meshes refuses on rule-4 completion,
  r=2 derives exactly from the ×8 counts) — ready for the supervisor's check-1 diff. The y+<1
  march STALL solved (N=150 reaches the farfield).
- **NOT DONE / BLOCKED:** **no gate-clearing y+<1 mesh exists** — the y+<1 march FAILS the 70°
  non-orthogonality gate at ~87° across two smoothing regimes (§3.4, §9 item 5), a structural
  obstacle needing the supervisor's/Sanaa's ruling before any level is generated. No flow solve;
  this document NOT frozen; the own-family 72k/574k mesh RETIRED. Freeze + launch are the
  cfd-supervisor's non-delegable check-4.

---

## 9. OPEN RULINGS FLAGGED FOR THE SUPERVISOR / SANAA

1. **Grading-path application (§5.1)** — confirm option (b): a new thin read-only wrapper over
   the frozen core, pinned by a FREEZE ADDENDUM (T23G2R precedent). **cfd-supervisor.**
2. **Cost vs ~$1 target (§3.1)** — the shock+y+<1 resolution drives the triple to ~$5.6 derived
   (fine ~$4.9, under $25 pre-auth). Confirm the cost or name a knob to relax. **Sanaa (rule 9).**
3. **Observed-order / wall-normal similarity (§7)** — s0 fixed for y+<1 vs geometric similarity;
   whether Gate G yields a full observed order or an honest-caveat band. **verification-team /
   rule 5.**
4. **Cost is coupled to the observed-order choice (§3.1, §7)** — ×8 observed-order family ~$23.4
   (fine $20.5); surface-only lower-bound family ~$6.7 (fine $5.1). **Sanaa / verification.**
5. **★ y+<1 vs the 70° non-orthogonality gate — STRUCTURAL OBSTACLE, needs a ruling (§3.4).**
   The march stall is solved (N=150+ reaches the farfield, skew 1.44, 0 neg-vol), but the y+<1
   first cell (s0=1.546e-6, AR ~10⁴) drives a localized near-wall cluster to **max
   non-orthogonality ~87°** — **FAILS the 70° hard gate across TWO smoothing regimes** (not a
   tuning miss). No gate-clearing y+<1 mesh exists yet. **Options for the supervisor / Sanaa:**
   (a) a near-wall-orthogonal meshing method (true O-grid with elliptic/orthogonal smoothing that
   enforces wall-orthogonality — the pyHyp hyperbolic route may not deliver y+<1 within 70°);
   (b) a documented, scoped exemption for the localized tip/LE non-orth cluster (only Sanaa widens
   a gate, rule 9); (c) a modest y+ relaxation (larger s0) to lower the near-wall AR/non-orth.
   **This blocks item-1 completion; I did not resolve it and did not route around the gate.**
