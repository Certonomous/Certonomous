# F7 — Marine / Free-Surface Capability

**Date:** 2026-07-28
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

> C. Xie, "Riemann solvers and pressure gradients in Godunov-type schemes for
> variable density incompressible flows," arXiv:2108.08769 (2021), §3.3.2 and Fig. 7.

That paper states: *"we recreated Martin and Moyce's dam break experiments for
square columns with dimension a = 2¼ inches = 0.05715 metres and a = 4½ inches =
0.1143 metres,"* with front position and column height "normalised by dividing by
a, and the time multiplied by √(g/a)." I used the **a = 2¼ in** case (verified by
re-rendering the paper's page image and reading the equation directly, not just
the text-extraction layer, to rule out a dropped coefficient).

- Column: square, width = height = a = 0.05715 m, in the corner of the tank.
- Domain: 15a wide × 2a tall (thin single-cell slab in z, `empty` front/back — 2D case).
- Gravity: (0, −9.81, 0). Fluids: water (ρ=1000, ν=1e-6), air (ρ=1, ν=1.48e-5), σ=0.07 — OpenFOAM tutorial defaults, laminar model (consistent with the cited paper's own inviscid/laminar treatment; the physical Re≈4×10⁴ means this is a simplification shared with essentially all VOF dam-break validations in the literature, not unique to this run).
- T = t·√(g/a), Z = x_front/a — Martin–Moyce's own convention, as stated in the cited paper.

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

### Cause (best evidence obtained this session, not fully isolated)

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

### Lesson

- A single alpha=0.5 crossing at "the first cell above the floor" is not a
  mesh-independent definition of surge-front position for VOF dam-break
  validation; it needs either (a) a fixed absolute probe height much smaller than
  either mesh's first-cell height (attempted at a/40 physical height for both
  meshes was actually what was already closest — worth extending to a genuine
  3+-mesh Richardson study before trusting any single-mesh number), or
  (b) extracting the true free-surface contour (e.g. via `interFoam`'s isosurface
  or ParaView contouring) rather than a line probe.
- Digitising a published figure via programmatic pixel-position detection
  (calibrated against detected axis-tick pixel clusters) rather than eyeballing
  produced self-consistent, near-round-number data points — worth reusing as the
  default method for any future "must digitise a plot" situation in this campaign.
- Gate FAILED as measured. Per the hard rules, this ships as a documented failure,
  not a shipped capability, and rungs (b) and (c) are correctly blocked by the
  ladder rule.

### What is blocked

- (b) Wigley hull wave resistance: **not started**, blocked by (a)'s failed gate.
- (c) Workshop hull (DTMB 5415/KCS): **not started**, depends on (b).
- To unblock (a) itself: a genuine 3-mesh (or more) grid-convergence study with a
  resolution-independent front-tracking definition (isosurface-based, not a fixed
  line probe) is the next concrete step, followed by re-checking against the same
  digitised reference.

### Artifacts

- Cases: `demo-output/website/campaign/F7_runs/damBreak_MM_a2p25in_{coarse,medium,medium_closedbox}/`
- Extraction/comparison scripts: `demo-output/website/campaign/F7_runs/{extract_front.py,gate_compare.py}`
- Comparison plot: `demo-output/website/campaign/F7_runs/F7_damBreak_gate_comparison.png`
- Digitisation source: arXiv:2108.08769 (Xie, 2021), Fig. 7, page image re-rendered
  at 600 dpi for calibration.
