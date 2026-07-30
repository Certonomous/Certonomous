# F7 — Marine / Free-Surface Capability

**Date:** 2026-07-28 (D1 diagnosis appended 2026-07-29)
**Repo:** /home/ubuntu/Certonomous @ 4824eb7
**Solver:** vanilla OpenFOAM v2606, `interFoam` (VOF, laminar), native (no Docker).
NavyFOAM ruled out per `NAVYFOAM_FINDING.md` (gated behind HPCMP CREATE-SH, 1–2 week
DoD-aligned approval; not pursued).
**Process:** all runs foreground, ≤4 MPI ranks, nothing left running.

---

## Ladder status

| Rung | Case | Status |
|---|---|---|
| (a) Dam break vs Martin & Moyce | square-column collapse, a=2.25in | **REACHED — FEASIBILITY pass, GATE fail** |
| (b) Wigley hull wave resistance | — | **BLOCKED** — not started; hard rule is "do not start (b) until (a) passes its gate," and (a) did not. |
| (c) Workshop hull (DTMB 5415 / KCS) | — | **BLOCKED** — depends on (b). |

---

## Rung (a): Dam break vs Martin & Moyce (1952)

### Configuration chosen and why

Martin & Moyce (1952) is a multi-part paper; the sub-case reproduced here is the
**square-column collapse** ("Part IV"), which is the configuration most commonly
re-run in the CFD-validation literature with a citable, explicit geometry statement.
Specifically I followed the geometry and non-dimensionalisation stated in:

> S. Leakey, V. Glenis, C.J.M. Hewett, "Riemann solvers and pressure gradients in
> Godunov-type schemes for variable density incompressible flows," arXiv:2108.08769
> (2021) / *Computers & Methods in Applied Mechanics and Engineering* 393:114763
> (2022), §3.3.2 and Fig. 7.
> **Correction (D1 diagnosis, see below):** previously mis-cited in this report as
> "C. Xie" — same paper (arXiv ID, title, content all correct), wrong author byline.

That paper states: *"we recreated Martin and Moyce's dam break experiments for
square columns with dimension a = 2¼ inches = 0.05715 metres and a = 4½ inches =
0.1143 metres,"* with front position and column height "normalised by dividing by
a, and the time multiplied by √(g/a)." I used the **a = 2¼ in** case (verified by
re-rendering the paper's page image and reading the equation directly, not just
the text-extraction layer, to rule out a dropped coefficient).

- Column: square, width = height = a = 0.05715 m, in the corner of the tank.
- Domain: 15a wide × 2a tall (thin single-cell slab in z, `empty` front/back — 2D case).
  **Correction (D1 diagnosis):** the cited paper's own domain for this benchmark
  is actually **15a wide × 1.25a tall**, 240×20 cells (dx=dy=a/16), all four
  boundaries walls — not 2a tall as stated here. Our runs used a taller domain
  than the source. Assessed in the D1 diagnosis as a real mismatch but unlikely
  to be the cause of the reported deviation (the source's own *tighter* 1.25a
  domain tracked its reference well, so a *more generous* 2a domain should not
  inflate the front speed).
- Gravity: (0, −9.81, 0). Fluids: water (ρ=1000, ν=1e-6), air (ρ=1, ν=1.48e-5), σ=0.07 — OpenFOAM tutorial defaults, laminar model (consistent with the cited paper's own inviscid/laminar treatment; the physical Re≈4×10⁴ means this is a simplification shared with essentially all VOF dam-break validations in the literature, not unique to this run).
- T = t·√(g/a), Z = x_front/a — Martin–Moyce's own convention, as stated in the cited paper, and confirmed correct in the D1 diagnosis (not a source of error).

### Reference data

**No tabulated numeric data for Martin & Moyce (1952) could be located** (original
paper not open-access; several secondary sources reproduce it only as a figure).
Per the campaign's rule against eyeballing-without-disclosure, I **digitised**
Fig. 7 of the Xie (2021) paper (which plots the original 1952 experimental points
as black crosses against its own simulation) using **pixel-position detection**,
not manual eyeballing:
1. Rendered the PDF page at 600 dpi.
2. Located axis-tick pixel positions programmatically (tick-mark clusters) to
   build a pixel→data calibration.
3. Located cross-marker pixel centroids programmatically (color/shape threshold)
   and mapped them through the calibration.

Digitised points landed almost exactly on round numbers (e.g. T=3.90→Z=6.00,
T=8.58→Z=12.00), which is strong evidence the calibration is correct.
**Digitisation uncertainty: ≈±0.05 in T, ±0.02 in Z**, set by cross-marker pixel
size relative to the axis scale; well below the deviations reported below.

Front-position reference points (a=2.25in): (T,Z) =
(3.90,6.00), (4.49,7.00), (5.17,8.00), (5.91,9.00), (6.74,10.00), (7.72,11.00),
(8.58,12.00), (9.53,13.00).

Column-height reference points (independent secondary check, same figure):
(T,h) = (0,1.00), (0.80,0.89), (1.29,0.78), (1.74,0.67), (2.15,0.56), (2.57,0.44),
(3.08,0.33), (4.27,0.22), (6.30,0.11).

### Runs

| Case | Mesh | Cells | BC (top) | Wall time | Core-min | Result |
|---|---|---|---|---|---|---|
| `damBreak_MM_a2p25in_coarse` | dx=a/8 | 1,920 | atmosphere (open) | 2.62 s (serial) | 0.04 | FEASIBILITY |
| `damBreak_MM_a2p25in_medium` | dx=a/20 | 12,000 | atmosphere (open) | 12.50 s (4 ranks) | 0.83 | control (BC sensitivity) |
| `damBreak_MM_a2p25in_medium_closedbox` | dx=a/20 | 12,000 | wall (closed box, matches ref. paper) | 18.34 s (4 ranks) | 1.22 | **GATE (primary)** |

Config hashes (sha256 of blockMeshDict+controlDict+fvSchemes+fvSolution+
setFieldsDict+0.orig/{alpha.water,U,p_rgh}+constant/{transportProperties,g}):
- coarse: `11a773ca7105`
- medium (open): `e8b76eafc854`
- medium (closed box): `bf44ead3c90a`

Total: **~2.4 core-minutes** for the whole rung, including the BC-sensitivity
control run and both post-processing passes. `MemAvailable` checked before the
heaviest stage: 30 GB free (well above the 6 GB caution threshold).

### FEASIBILITY (coarse, does it run) — PASS

- `blockMesh`/`checkMesh` clean (max skewness 1e-13, aspect ratio 1, orthogonal).
- `interFoam` ran to completion, `endTime=0.8s` (T≈10.5), no floating-point traps,
  no solver divergence. Max Courant ≈0.52 (capped target 0.5).
- `alpha.water` stayed bounded to within MULES numerical tolerance (min ≈ −1e-6,
  max ≈ 0.53–0.94 depending on mesh; no unbounded blow-up).
- Water-volume conservation: coarse mesh drifted ~1.6% over the run (0.0333→0.0328);
  medium closed-box conserved to machine precision (0.033333 constant, exact 1/30).
- Column visibly collapses and a surge front forms and propagates — qualitatively
  correct dam-break phenomenology. **PHYSICS stage (does the phenomenon appear) also
  passes** on this qualitative basis, and is further supported by the column-height
  cross-check below.

### GATE (fine, does the number land) — **FAIL**

**Primary metric — surge front position Z vs T, medium closed-box mesh:**

| T | Z (ref) | Z (sim) | deviation |
|---|---|---|---|
| 3.90 | 6.00 | 6.62 | +10.4% |
| 4.49 | 7.00 | 7.64 | +9.2% |
| 5.17 | 8.00 | 8.82 | +10.2% |
| 5.91 | 9.00 | 10.09 | +12.1% |
| 6.74 | 10.00 | 11.50 | +15.0% |
| 7.72 | 11.00 | 13.14 | +19.4% |
| 8.58 | 12.00 | 14.56 | +21.3% |
| 9.53 | 13.00 | 14.42 | +10.9%* |

*last point affected by the front approaching the domain's far wall (15a);
treat with reduced confidence.

**Mean deviation +13.6%, max |deviation| 21.3%, systematically growing with time
until wall proximity confounds the last point. Gate FAILS** — this is well outside
any credible tolerance for a "does the number land" claim, and it is monotonically
diverging, not oscillating around zero.

**Mesh-sensitivity check (coarse vs medium):** coarse mesh gives mean deviation
**−13.2%** (undershoot, max −22.7%) against the *same* reference points — i.e.
refining the mesh from a/8 to a/20 **flipped the sign of the error** rather than
converging toward the reference. This rules out "just needs a finer grid" as the
explanation; a genuine mismatch (not a bracketed convergence issue) is present at
medium resolution, and a proper Richardson-style 3-mesh study would be needed to
find the truly grid-converged interFoam answer — out of scope for this pass,
flagged as a lesson below.

**BC-sensitivity control:** the primary reference paper closes all four tank
walls (no venting); the standard OpenFOAM `damBreak` tutorial convention (which
the first medium run used) instead vents the top as an open `atmosphere` patch.
Rerunning the medium mesh with the top changed to a wall (matching the paper's
own setup exactly, and requiring `pRefCell`/`pRefValue` to fix the now-singular
pressure reference) gave an **essentially identical** front trajectory to the
open-top run (same overshoot, same shape). **Hypothesis "open-top BC lets air
escape too easily and over-speeds the front" is REFUTED** by this control test.

**Secondary/independent check — column-height decay, medium closed-box:**

| T | h (ref) | h (sim) | deviation |
|---|---|---|---|
| 0.80 | 0.89 | 0.848 | −4.7% |
| 1.29 | 0.78 | 0.713 | −8.6% |
| 1.74 | 0.67 | 0.601 | −10.4% |
| 2.15 | 0.56 | 0.507 | −9.4% |
| 2.57 | 0.44 | 0.423 | −3.9% |
| 3.08 | 0.33 | 0.344 | +4.3% |
| 4.27 | 0.22 | 0.223 | +1.2% |
| 6.30 | 0.11 | 0.131 | +19.2%* |

Mean deviation **−1.5%**, max |deviation| 19.2% (last point, hardest to digitise
precisely and interpolated near the edge of the reference range). This bulk
quantity — how much water remains in the original footprint over time — tracks
the reference **much more closely** (within ~10% through the middle of the run)
than the leading-edge front position does. This says the bulk collapse physics is
roughly right; the discrepancy is concentrated at the thin, fast-moving leading
edge of the surge, which is exactly the region a VOF method with a fixed near-wall
sampling height is most sensitive to numerical smearing (confirmed by the
coarse/medium sign-flip above: the two meshes' "first cell above the floor" sit
at different absolute heights — 0.0625a vs 0.025a — and the alpha=0.5 crossing at
those two different heights gives materially different apparent front positions
because the true toe is thin and non-vertical at this resolution).

### Cause — UPDATED, now fully isolated (see D1 diagnosis below)

The original pass below is superseded by the D1 diagnosis (next section), which
converts item 3 from a correlation into a confirmed, isolated mechanism and
directly tests (and refutes) two more candidate explanations (adaptive-timestep
confounding, wall friction). Kept here for the historical record of what was
known before D1:

1. Front-position gate failure is **not** a boundary-condition artifact (ruled out
   by direct A/B test, closed box vs open top).
2. It is **not** simple under-resolution — refining the mesh moved the error in
   the *wrong* direction (coarse undershoots, medium overshoots), so "run it
   finer" is not a safe fix without a proper convergence study.
3. It **is** correlated with the near-wall sampling height used to define "front
   position" from the discretised VOF field — the leading edge is thin and not a
   clean vertical wall of water at these resolutions, so where exactly you probe
   for the alpha=0.5 crossing materially changes the answer.
4. The bulk quantity (column-height decay) that isn't as sensitive to this effect
   agrees with the reference to within ~10%, suggesting the volume-averaged
   physics is closer to correct than the point-quantity gate suggests.

---

## D1 diagnosis: full isolation of the F7a sign flip

**Directive:** D1. **Protocol:** LESSONS.md L-8 (cheapest-and-most-often-guilty
first), P2 (predictions written before each test), P5 (one change per rung).
Turbulence already ruled out at zero cost per the D1 briefing (laminar
throughout) — not revisited. Full stage-by-stage data in
`F7_runs/F7a_diagnosis.json`.

### Stage (a) — the comparison itself (zero-compute)

- **Prediction:** at least one genuine documented mismatch exists against the
  cited source; digitisation uncertainty (±0.05T, ±0.02Z) converts to well
  under 2% of Z and cannot explain 10–24% deviations; if the cause were a
  constant gate-release time delay, the implied time-shift needed to map each
  simulated point onto the reference curve should be constant across all 8
  reference points.
- **Tested:** fetched the full text of arXiv:2108.08769 and read §3.3.2/Fig. 7
  verbatim; compared non-dimensionalisation, domain, BC and gate-release
  assumption against our dictionaries; arithmetic inversion of the reference
  Z(T) table to solve for the implied time-shift at each of the 8 gate points.
- **Findings:**
  - Citation author was wrong ("C. Xie" → actually Leakey, Glenis & Hewett,
    2022) — same paper, byline-only error, now corrected above.
  - Non-dimensionalisation **confirmed correct** (T=t√(g/a), Z=x/a) — not a
    source of error.
  - **Domain mismatch found**: cited paper used 15a×1.25a (240×20 cells), all
    walls closed; we used 15a×2a — genuine mismatch, now corrected above, but
    assessed as unlikely to be causal (the source's own tighter domain tracked
    its reference fine; ours is more generous, if anything less likely to bias
    the front via top-wall proximity).
  - BC (all four walls closed) **confirmed matching** ours.
  - Gate release: the cited paper's own CFD is instantaneous, matching ours;
    the real 1952 experiment's physical gate-withdrawal time is not stated in
    this secondary source and could not be checked further at zero cost.
  - Digitisation uncertainty converts to **≤1.5%** — two orders of magnitude
    below the 10–24% observed deviations. Ruled out.
  - Time-shift arithmetic: the implied dT **grows** from 0.37 (T=3.90) to 2.43
    (T=8.58) — not constant. A pure gate-release time-shift is **refuted**.
- **Verdict:** comparison definition checks out; domain-height documentation
  error found and fixed but not causal; digitisation uncertainty and pure
  time-shift both quantitatively ruled out. **Sign flip not yet explained —
  proceed.**

### Stage (b) — boundary/initial conditions: wall treatment

- **Prediction:** the medium mesh (dy=a/20) is far too coarse to resolve a
  genuine viscous sublayer at Re≈10⁴–10⁵; slip vs no-slip floor will make
  little difference (<3%) — wall friction is not the cause.
- **Tested:** new case `damBreak_MM_a2p25in_medium_slipfloor` — **one change**
  from the GATE case: floor `noSlip`→`slip`, everything else identical.
  `case_preflight.sh` passed; ran foreground, 4 ranks, 14.83s (0.99 core-min).
- **Finding:** control (no-slip) +13.6% mean/+21.3% max → slip floor +15.9%
  mean/+24.2% max. A ~2-point *worsening*, same sign, small magnitude — moves
  in the predicted direction (less friction → very slightly faster front) but
  far too small to explain the deviation, and the wrong direction to be "the"
  cause of an overshoot (no-slip already mildly suppresses the front).
- **Verdict:** wall treatment **refuted** as the driver. Sign flip not
  explained — proceed.

### Stage (c) — extraction-height sensitivity (reused existing field dumps, zero new solve)

- **Prediction:** if the sign flip were a genuine PDE-convergence effect,
  front position at nearby probe heights *within the same mesh's own
  solution* should behave consistently; if it's an extraction artifact,
  adjacent rows within one mesh should show comparably large — possibly
  sign-flipping — swings, since "front position" = alpha=0.5 crossing at
  y = half the first-cell height, an **absolute** height that scales with
  mesh resolution (a/16 coarse vs a/40 medium), not a fixed physical probe.
- **Tested:** reused the medium_closedbox and coarse runs' **already-computed**
  full-field `alpha.water` dumps (reconstructPar on the decomposed medium case
  — no new PIMPLE solve); parsed the structured cell ordering directly and
  extracted the alpha=0.5 crossing at every row (every available absolute
  height) at t=0.2/0.4/0.6/0.8; separately swept the crossing threshold
  (0.9/0.5/0.1/0.01/0.001) at the native row to separate "which height" from
  "what threshold."
- **Finding:** at t=0.6 (T=7.86, ref Z=11.0 @ T=7.72) on the medium mesh:
  row 0 (y=0.025a, the mesh's own native probe) gives **Z=13.38** (≈+22%);
  row 1 (y=0.075a, one cell up, same solve, same instant) gives **Z=7.72**
  (≈−30%). A single row change **flips the sign** and swings **>40
  percentage points** — bigger than the entire cross-mesh deviation being
  explained. Threshold sensitivity at the fixed row is **<2%** — small.
  The coarse mesh has no alternative row to probe: its first cell spans the
  *entire* 0–0.125a range as one FVM value, forcing a coarse spatial average
  that plausibly biases toward smaller x (undershoot) by blending in
  slower/thicker upstream fluid — mechanistically consistent with the
  observed sign flip.
- **Verdict:** **sign-flip mechanism identified.** The metric samples an
  absolute height tied to mesh resolution; the surge's toe is a thin,
  rapidly-thinning wedge whose alpha field is extremely height-sensitive.
  This effect alone is large enough to account for both the sign and
  magnitude of the reported deviation. **Sign flip explained.**

### Stage (d) — mesh and timestep convergence, separated

- **Prediction:** (i) at fixed dt, mesh refinement alone will *still* flip the
  sign, because stage (c) already shows the effect tracks absolute probe
  height, not timestep — if fixing dt instead removed the flip, that would
  implicate L-8's adaptive-timestep/mesh confound as the real cause instead;
  (ii) at fixed mesh, timestep refinement (first-order Euler ddt) will produce
  a small, monotonic, non-sign-flipping shift.
- **Tested:** three new cases, **one change per rung**, `case_preflight.sh`
  passed on each, foreground:
  - `coarse_fixeddt`: a/8 mesh, converted to closed-box BC to match the GATE
    baseline, `adjustTimeStep no`, dt fixed 5e-4s. Serial, 9.98s (0.17 core-min).
  - `medium_fixeddt`: a/20 mesh, closed box, dt fixed **5e-4s** (same dt as
    coarse_fixeddt — isolates MESH). 4 ranks, 25.84s (1.72 core-min).
  - `medium_fixeddt_coarsedt`: same a/20 mesh as `medium_fixeddt`, dt fixed
    **1.2e-3s** (2.4× larger — isolates TIMESTEP). 4 ranks, 12.13s (0.81 core-min).
- **Finding:**
  - `coarse_fixeddt`: −13.2%/−21.1% — essentially identical to the original
    adaptive-dt coarse run (−13.2%/−22.7%).
  - `medium_fixeddt`: +14.6%/+21.7% — essentially identical to the original
    adaptive-dt closed-box GATE run (+13.6%/+21.3%).
  - **Mesh-only comparison (identical dt): sign flip persists** — coarse
    undershoots, medium overshoots, unchanged from the adaptive-dt result.
    This **refutes** the L-8-flagged "adaptive-timestep aliased into the mesh
    effect" hypothesis.
  - `medium_fixeddt_coarsedt`: +13.9%/+21.6% — within **<1 percentage point**
    of `medium_fixeddt` despite a 2.4× larger dt. **Timestep-only comparison
    (identical mesh): no meaningful effect, no sign reversal.**
- **Verdict:** mesh is the variable that flips the sign; timestep is
  confirmed, independently, to not be a meaningful contributor. **Sign flip
  explained, not merely reduced.**

### D1 summary

- **Sign flip: EXPLAINED.** Cause: the front-position metric (alpha=0.5
  crossing at "half the first cell above the floor") ties the probe's
  absolute height to mesh resolution; the surge toe's alpha field is
  extremely height-sensitive (>40-point sign-flipping swing between adjacent
  rows of the *same* solve), which dominates over genuine PDE-level mesh
  convergence and is independent of timestep (confirmed by separated
  mesh-only / timestep-only rungs) and largely independent of wall friction
  (~2-point effect, wrong direction to be causal).
- **Ruled out:** turbulence (zero-cost, pre-D1), open/closed-top BC (prior
  A/B), digitisation uncertainty, pure gate-release time-shift, wall
  friction, adaptive-timestep/mesh confounding, timestep discretisation error.
- **GATE STATUS: FAIL — unchanged.** Explaining the mechanism does not make
  the reported number correct; using the metric as currently defined, the
  medium closed-box mesh still overshoots by +13.6% mean/+21.3% max.
- **Recommended next step (out of scope for this diagnosis):** re-define
  front position via a mesh-independent extraction (true free-surface
  isosurface/contour, or point-interpolated sampling at a fixed absolute
  height well below both meshes' first-cell heights) and re-run a genuine
  Richardson-style 3+ mesh convergence study before re-attempting the gate.
- **New compute this session:** 4 new cases, 3.69 core-minutes total, all
  foreground, all preflighted, nothing left running. Full per-stage
  prediction/test/result/verdict data: `F7_runs/F7a_diagnosis.json`.

### Lesson

- A single alpha=0.5 crossing at "the first cell above the floor" is not a
  mesh-independent definition of surge-front position for VOF dam-break
  validation — **now confirmed, not just suspected (D1)**: swapping which row
  of the *same* mesh's *same* solve you probe swings the answer by >40
  percentage points and flips its sign, which is larger than the entire
  cross-mesh deviation this campaign was trying to explain. It needs either
  (a) a fixed absolute probe height much smaller than either mesh's
  first-cell height, or (b) extracting the true free-surface contour (e.g.
  via `interFoam`'s isosurface or ParaView contouring) rather than a line
  probe, followed by a genuine 3+-mesh Richardson study.
- **A sign flip under mesh refinement is not automatically a mesh-convergence
  question** — here it was entirely an artifact of how a *derived diagnostic*
  (front position) was extracted, not of the underlying velocity/pressure
  solution. Separating mesh and timestep (D1 stage (d)) was what proved this:
  the flip persisted unchanged at fixed dt, and disappeared as a candidate
  once timestep refinement (2.4×) moved the result by <1 point.
- Digitising a published figure via programmatic pixel-position detection
  (calibrated against detected axis-tick pixel clusters) rather than eyeballing
  produced self-consistent, near-round-number data points — worth reusing as the
  default method for any future "must digitise a plot" situation in this campaign.
- Always re-derive citation details (author, exact domain/mesh) from the
  source text itself, not from a first pass's paraphrase — D1 found both a
  wrong author byline and an unnoticed domain-height mismatch (2a vs 1.25a)
  in the original write-up of this same rung, at zero compute cost, just by
  reading the cited PDF directly.
- Gate FAILED as measured, and STILL FAILS after D1 — explaining a sign flip
  is not the same as fixing the number. Per the hard rules, this ships as a
  documented failure, not a shipped capability, and rungs (b) and (c) are
  correctly blocked by the ladder rule.

### What is blocked

- (b) Wigley hull wave resistance: **not started**, blocked by (a)'s failed gate
  (still FAIL after D1 — the mechanism is now known, the number is not fixed).
- (c) Workshop hull (DTMB 5415/KCS): **not started**, depends on (b).
- To unblock (a) itself: a genuine 3-mesh (or more) grid-convergence study with a
  resolution-independent front-tracking definition (isosurface-based, not a fixed
  line probe) is the next concrete step, followed by re-checking against the same
  digitised reference. D1 has now confirmed this is necessary AND sufficient in
  principle to attempt — the sign flip that made a naive convergence study
  meaningless before is explained and attributable to the extraction method, not
  to an unresolved physical/numerical instability.

### Artifacts

- Cases: `demo-output/website/campaign/F7_runs/damBreak_MM_a2p25in_{coarse,medium,medium_closedbox}/`
- D1 diagnosis cases (one change per rung vs the above):
  `demo-output/website/campaign/F7_runs/damBreak_MM_a2p25in_{coarse_fixeddt,medium_fixeddt,medium_fixeddt_coarsedt,medium_slipfloor}/`
- Extraction/comparison scripts: `demo-output/website/campaign/F7_runs/{extract_front.py,gate_compare.py}`
- D1 diagnosis data: `demo-output/website/campaign/F7_runs/F7a_diagnosis.json` (full
  per-stage prediction/test/result/verdict), plus ad hoc analysis scripts used
  during D1 (row-height and alpha-threshold sensitivity, both reusing existing
  field dumps at zero new solve cost).
- Comparison plot: `demo-output/website/campaign/F7_runs/F7_damBreak_gate_comparison.png`
- Digitisation source: arXiv:2108.08769 (Leakey, Glenis & Hewett, 2021/2022 —
  corrected author, see D1 above), Fig. 7, page image re-rendered at 600 dpi for
  calibration.

---

## D2 diagnosis (2026-07-30): D1's own recommended next step carried out — the
gate's systematic bias is NOT an extraction artifact after all

**Directive:** owner-level task naming F7a's sign-flip signature directly
("recorded as producing a sign flip when the mesh is refined... that signature
should be familiar" — matching the airfoil case's own refinement-worsening
signature, which turned out to be a real defect, not a discretisation
artifact). Method: find WHERE before proposing a mechanism; check the case
setup against the template/reference it came from. Budget: cheap, foreground,
`launch_solve.sh`-registered runs; nothing left running.

### Step 0 — re-verify D1's own headline number independently, before building on it

Per this lab's standing rule (do not trust a prior conclusion without
re-deriving it), D1's stage-(c) row-height claim (row 0 at t=0.6 gives
Z=13.38, row 1 gives Z=7.72 — a >40-point, sign-flipping swing) was
re-derived from scratch this session, reading `0.6/alpha.water` and a freshly
generated `0.6/C` (cell centres) directly, grouping cells into rows by y, and
independently re-implementing the alpha=0.5 crossing search. **Result: row 0
Z=13.3800, row 1 Z=7.7175 — matching D1's reported values to 4 significant
figures.** D1's row-height finding is real and reproducible, not an error.
This re-verification cost zero new solves (reused the existing field dumps).

### Step 1 — check the case setup against its reference (D1 flagged, never tested)

D1 found and disclosed a real, uncorrected mismatch: the domain used here is
15a × **2a** tall; the cited reference paper (Leakey, Glenis & Hewett,
arXiv:2108.08769, §3.3.2) states 15a × **1.25a**. D1 reasoned this was
"unlikely causal" (the source's own tighter domain tracked its reference
fine, so a more generous one should not inflate the front) but never actually
ran the comparison.

**Single-variable test:** `damBreak_MM_a2p25in_medium_closedbox_paperdomain`
— identical to the gate case in every respect (cell size dx=dy=a/20, BCs,
schemes, solution controls) except domain height, corrected to 1.25a (ny
25 cells instead of 40, following directly from holding cell size fixed).
Preflight passed; foreground smoke test (20s, healthy Courant/bounded alpha)
before the full run, launched via `launch_solve.sh`, collector armed, nothing
left running.

| T | Z_ref | Z_sim (2a domain, gate) | Z_sim (1.25a domain, paper-matched) |
|---|---|---|---|
| 3.90 | 6.00 | 6.62 (+10.4%) | 6.62 (+10.3%) |
| 4.49 | 7.00 | 7.64 (+9.2%) | 7.63 (+9.0%) |
| 5.17 | 8.00 | 8.82 (+10.2%) | 8.80 (+10.0%) |
| 5.91 | 9.00 | 10.09 (+12.1%) | 10.07 (+11.9%) |
| 6.74 | 10.00 | 11.50 (+15.0%) | 11.47 (+14.7%) |
| 7.72 | 11.00 | 13.14 (+19.4%) | 13.10 (+19.1%) |
| 8.58 | 12.00 | 14.56 (+21.3%) | 14.51 (+20.9%) |

**Mean +12.9%, max 20.9% — essentially identical to the gate's own +13.6%/
21.3%.** D1's reasoning is confirmed by direct test, not just argument: the
domain-height mismatch is **refuted** as a contributor. This is a real,
disclosed template deviation from the cited reference that turned out not to
matter — reported as a genuine negative result, not silently dropped.

### Step 2 — carry out D1's own recommended next step: a resolution-independent front metric

D1 left this explicitly open: *"re-define front position via a mesh-
independent extraction... before re-attempting the gate."* Implemented
`integrated_front.py` (new): instead of a line probe at one absolute height
(which D1 showed is extremely sensitive to which row it sits on), this sums
`alpha.water * dy` down each x-column of the ALREADY-WRITTEN full 2D field
(zero new solve — reuses the gate case's own 16 written time dumps) to get a
depth-integrated water height h(x), then locates the front as the x where
h(x) first drops below 1% of the column height a. This is not tied to any
particular row and cannot be dominated by a single thin/noisy cell the way
the line probe can.

| T | Z_ref | Z (near-floor line probe, D1's metric) | Z (depth-integrated, new) |
|---|---|---|---|
| 3.90 | 6.00 | 6.62 (+10.3%) | 6.69 (+11.5%) |
| 4.49 | 7.00 | 7.64 (+9.1%) | 7.71 (+10.1%) |
| 5.17 | 8.00 | 8.82 (+10.3%) | 8.89 (+11.1%) |
| 5.91 | 9.00 | 10.09 (+12.1%) | 10.16 (+12.9%) |
| 6.74 | 10.00 | 11.50 (+15.0%) | 11.57 (+15.7%) |
| 7.72 | 11.00 | 13.14 (+19.5%) | 13.22 (+20.1%) |

**The depth-integrated metric shows the SAME systematic, time-growing
overshoot as the near-floor line probe — not the >40-point swing D1 found
between row 0 and row 1.** This is the decisive result of this session:
**the row-to-row swing D1 found is real, but it is not what explains the
gate's systematic bias.** At t=0.6, the depth-integrated front (13.45) sits
close to row 0's line-probe value (13.38), not row 1's (7.72) — meaning row
0 (the gate's own native probe, nearest the floor) is actually the more
representative of the two, consistent with a dam-break surge's leading tip
being physically a thin film hugging the floor; row 1, one cell up, is the
outlier, most likely because the thin film has already passed that height's
threshold going the other way. D1's conclusion "sign flip explained, not
merely reduced" is correct for the CROSS-MESH sign flip specifically (coarse
undershoot vs. medium overshoot); it does not extend to, and should not have
been read as explaining, the gate's own within-mesh systematic bias — D1's
own text was in fact careful about this distinction ("GATE STATUS: FAIL —
unchanged. Explaining the mechanism does not make the reported number
correct"), but the open question of *why* the number is wrong was not
resolved there. This session answers it partially (Step 3) and reports the
rest as unresolved (Step 4), rather than letting the row-height finding stand
in for a fuller explanation it was never shown to provide.

**Triangulation with the already-recorded column-height (bulk) metric:**
that metric tracks the reference to within ~10% through the middle of the
run (mean −1.5%) — a genuinely different, spatially-averaged quantity over
the ORIGINAL column footprint, not the advancing tip. Two metrics (line
probe, depth-integration) that measure the TIP agree with each other and
disagree with the reference; one metric (column height) that measures the
BULK agrees with the reference. **This localises the discrepancy specifically
to the advancing tip of the surge, not a generic overspeed of the whole
flow** — a real "where" finding, per this session's standing method.

### Step 3 — one mechanism found and confirmed to matter, partially

Candidate: VOF interface compression. `cAlpha=1` (the OpenFOAM tutorial
default, confirmed identical in our case's `fvSolution` — checked directly
against `$FOAM_TUTORIALS/multiphase/interFoam/laminar/damBreak/damBreak`, no
other difference in `fvSchemes`/`fvSolution`/`transportProperties`/`g` beyond
the already-disclosed `pRefCell`/`pRefValue` addition needed for the closed
top wall) adds an artificial compressive velocity along the interface normal
to counter numerical smearing. At a thin, fast, near-horizontal surge toe,
this normal-direction correction is geometrically closest to the flow
direction and is a physically plausible source of extra forward push.

**Single-variable test:** `damBreak_MM_a2p25in_medium_closedbox_calpha0` —
identical to the gate case except `cAlpha: 1 -> 0` (interface compression
off). Preflight passed, foreground smoke test clean, launched via
`launch_solve.sh`.

| T | Z_ref | Z_sim (cAlpha=1, gate) | Z_sim (cAlpha=0) |
|---|---|---|---|
| 3.90 | 6.00 | 6.62 (+10.4%) | 6.46 (+7.7%) |
| 4.49 | 7.00 | 7.64 (+9.2%) | 7.41 (+5.8%) |
| 5.17 | 8.00 | 8.82 (+10.2%) | 8.48 (+5.9%) |
| 5.91 | 9.00 | 10.09 (+12.1%) | 9.60 (+6.6%) |
| 6.74 | 10.00 | 11.50 (+15.0%) | 10.81 (+8.1%) |
| 7.72 | 11.00 | 13.14 (+19.4%) | 12.16 (+10.6%) |
| 8.58 | 12.00 | 14.56 (+21.3%) | 13.30 (+10.8%) |

**Mean +8.4% (down from +13.6%), max 11.7% (down from 21.3%) — roughly a
40% reduction in both mean and max deviation from a single parameter
change.** Interface compression is confirmed to be a real, material
contributor to the overshoot, not a red herring. **It is not the whole
story**: the deviation is smaller but still positive, still systematic, and
still grows with time (7.7%→10.8%, the same qualitative shape as before at a
lower level) — some other mechanism is also contributing, not yet
identified.

### Step 4 — verdict and what remains open

**What this session established, stated precisely:**
- D1's row-height sensitivity finding is real and re-verified independently
  (exact match to 4 sig figs) — but it explains the CROSS-MESH sign flip,
  not the WITHIN-MESH systematic bias the gate actually fails on. This is a
  narrowing of D1's scope, not a contradiction of it.
- The domain-height mismatch vs. the cited reference (2a vs. 1.25a), flagged
  by D1 but never tested, is **refuted by direct A/B run** (deviation
  unchanged to within 1 percentage point).
- A resolution-independent, depth-integrated front metric — D1's own
  recommended next step — shows the **same** systematic, time-growing
  overshoot as the original near-floor probe. The gate's failure is real,
  not a probe-height artifact, matching the pattern the coordinator flagged
  from the airfoil case.
- The discrepancy is localised to the advancing tip specifically (bulk
  column-height agrees with the reference; tip-tracking metrics do not).
- VOF interface compression (`cAlpha`) is a confirmed, material,
  single-variable-tested contributor — turning it off cuts both mean and max
  deviation by roughly 40% — but does not eliminate the bias.

**What remains unidentified:** the residual ~6-11% (cAlpha=0) to ~10-21%
(cAlpha=1) systematic, time-growing overshoot at the tip. Candidates not yet
tested: (a) the reference paper's OWN front-extraction methodology may differ
systematically from either metric used here (a comparison-basis question,
per L-8's own stage-1 priority — not checked this session, since the paper's
methodology section does not appear to state its own extraction technique in
enough detail to rule this in or out without further digging); (b) further
reduction/tuning of MULES sub-cycling (`nAlphaSubCycles`, `nAlphaCorr`) at
the thin toe; (c) mesh resolution specifically at the toe height (a
Richardson-style study, not yet run, now that the row-to-row extraction
confound is understood well enough not to alias into it).

**Per the standing stopping rule:** two real, testable mechanisms were found
this session (one refuted: domain height; one confirmed material but
partial: interface compression), and D1's own recommended next step was
carried out and answered (resolution-independent extraction does not rescue
the gate). This is reported as an honest partial result, not chased to a
third or fourth new hypothesis tonight. **GATE STATUS: FAIL — unchanged, now
with a materially better-characterised cause** (a real, partially-explained,
tip-localised bias, not a comparison or extraction-method artifact). Rungs
(b) and (c) remain correctly blocked.

### D2 evidence

- `demo-output/website/campaign/F7_runs/damBreak_MM_a2p25in_medium_closedbox_paperdomain/`
  — domain-height A/B test (refuted)
- `demo-output/website/campaign/F7_runs/damBreak_MM_a2p25in_medium_closedbox_calpha0/`
  — interface-compression A/B test (confirmed, partial)
- `demo-output/website/campaign/F7_runs/integrated_front.py` — new,
  depth-integrated resolution-independent front extraction
- `demo-output/website/campaign/F7_runs/{paperdomain_front.txt,calpha0_front.txt,integrated_front_rows.json}`
  — raw extraction output behind the tables above
