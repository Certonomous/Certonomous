# Double Mach reflection (Woodward–Colella 1984) — results

Run 2026-08-07 against `DMR_PREREGISTRATION.md` (committed `74797a57` before
any mesh existed). Docket: `double-mach-reflection-woodward-colella`.
Native openfoam2606 `rhoCentralFoam`, Kurganov flux, inviscid, inclined-shock
formulation; coded exact-kinematics top boundary compiled and ran on both
rungs. Registry: `dmr_res120_20260807T224408Z`, `dmr_res60_20260807T224510Z`.
Everything retained under `campaign/DMR_runs/` (case generator, locator,
logs, dicts, `locator_result.json` per rung, t=0.2 fields on disk in the run
tree, contour deliverable `dmr_density_contours_t0p2.png`).

## Mesh standard (guidelines §2.1, per rung, from each rung's own checkMesh)

| rung | cells | max non-ortho | max skewness | max aspect ratio |
| --- | --- | --- | --- | --- |
| res120 (Δ=1/120) | 57,600 | 0 | 6.0e-10 | 1.0000001 |
| res60 (Δ=1/60) | 14,400 | 0 | 2.7e-13 | 1.0 |

Cartesian by construction; all gates pass trivially. Both rungs reached
t = 0.2 with all ten writes (endTime is a writeInterval multiple — checked
at registration, held at runtime).

## Gate V — incident-shock kinematics vs exact theory: PASS, both rungs

Reference: x = 1/6 + (y + 4)/√3 at t = 0.2, evaluated at each rung's row
nearest y = 0.9. Tolerance ±0.0231 (1% of the 2.309 travelled distance).

| rung | row y | measured | exact at row | error | error/travel | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| res120 | 0.89583 | 2.99666 | 2.99328 | **+0.00338** | 0.15% | PASS |
| res60 | 0.90833 | 3.00448 | 3.00049 | **+0.00399** | 0.17% | PASS |

Fine-rung error < coarse-rung error (prediction 1 clause) — TRUE. The
Mach-10 shock propagates at the exact speed on this stack to 0.15% of its
travel: the numerics gate, passed.

## Gate P1 — double-Mach structure detector: **FAIL as registered, and the failure is the detector's geometry, recorded**

The registered clause demanded **two slope discontinuities on the leading
front polyline**. The pre-committed detector finds exactly one (the primary
triple point); the strongest second kink on the leading front below it
measures 0.13 cells against the declared 0.6-cell threshold, at both rungs.

Two readings, both on the record (guidelines 3.5 style), and they are not
exclusive:

1. **Registration defect, the larger share.** The canonical secondary
   triple point does not live on the leading front — it is the kink of the
   *reflected* shock, with its slip line and secondary Mach stem behind the
   primary front. The clause tested the wrong locus. This was written into
   the pre-registration and is left standing as FAIL per guidelines 1.3;
   the repair is a successor detector on the reflected-shock locus, not an
   after-the-fact edit here.
2. **Dissipation, the smaller share.** In sharp (PPM-class) solutions the
   near-wall stem also shows a jet-driven kink; at 1/120 with the
   central-upwind flux the stem is smooth to 0.13 cells — consistent with
   the pre-registered dissipation prediction.

**What the retained deliverable shows anyway:** the 30-contour density
record (`dmr_density_contours_t0p2.png`) at res120 plainly contains the
double-Mach structure — reflected-shock kink near (2.25, 0.40), slip-line
curl below it, wall jet along y < 0.05 up to the stem at x = 2.776. The
structure is present in the flow; it is the registered detector that cannot
testify to it. The jet sub-clause of P1, which the detector does decide,
passes at both rungs (res120: wall-strip ρ_max 17.26 vs plateau 10.71;
res60: 16.69 vs 10.86).

## Gate P2 — self-similar consistency

chi per the registered definition (line **from (1/6, 0)** fitted through
the six triple-point samples, t = 0.10…0.20):

| rung | chi (registered, constrained) | chi (free slope, diagnostic) | free-fit intercept − x0 |
| --- | --- | --- | --- |
| res120 | **9.07°** | 9.94° | +0.180 (= 21.6 cells) |
| res60 | **8.21°** | 9.89° | +0.354 (= 21.2 cells) |

- **Rung-to-rung clause: PASS.** |chi_R1 − chi_R2| = 0.87° ≤ 1.5°
  (registered); the *slope* of the trajectory, which cancels any constant
  detector bias, agrees across a 2× resolution change to **0.05°**.
- **Within-rung intercept clause: FAIL as registered** at both rungs — the
  free-fit trajectory extended to the wall misses (1/6, 0) by 21.6 and 21.2
  cells against a 2-cell tolerance. The diagnostic that decides whose fail
  it is: the offset is **constant in cells** (21.6 vs 21.2) and therefore
  halves in physical units with refinement — an instrument artifact of the
  lead-threshold locator on a smeared incident shock (measured 10–90 smear
  1.8 cells; per-rung implied detection bias 3.8 cells, constant), not a
  physical breach of self-similarity. A physical breach would be
  resolution-independent in physical units. Recorded as FAIL-as-written
  with the instrument diagnosis beside it; the tolerance was set without
  pricing the threshold bias, and that lesson transfers to the successor
  detector.

**chi, published as a measurement** (per the pre-launch amendment §3, no
external numeric band exists in reachable canon): registered constrained
definition **9.07° at the primary rung** (8.21° at the trend rung — the
0.87° spread is the intercept-bias interacting with the constraint); the
bias-immune free slope reads **9.94° / 9.89°** (Δ = 0.05°) and is the number
a successor should trust. Locator increment per sample ≈ 0.4° (R1). This is
the lab's transcription-in-waiting for a tiered digitisation of Woodward &
Colella's own figures.

## The dissipation note (recorded, not gated)

res120: both triple points, slip-line curl and jet visible; stem smooth.
res60: structure recognisable, secondary features strongly smeared, jet
present but diffuse — the coarse rung is visibly damped, as predicted for a
central-upwind flux against the reference's PPM.

**Corner artifact, recorded (Kemm's artifact class):** 18 cells (res120) /
9 cells (res60) at the inlet-bottom corner x < 0.15 carry ρ up to 280.7
(res120), an inflow-corner boundary artifact far left of the structure; the
flow field proper tops at ρ = 20.05. No gate reads that region. The contour
deliverable's level range is the structure range (x > 0.25) with the
artifact called out on the figure itself.

## Predictions, scored clause-by-clause

1. Gate V passes both rungs, R1 error < R2 — **TRUE**.
2. Gate P1 passes at R1 (both triple points via the detector), jet present
   but damped — **FALSE as written**: the jet clause is true, the
   two-kink-detector clause failed on its own geometry (above). Left
   standing.
3. R2 secondary structure marginal-to-absent for the detector — **TRUE**
   (absent for the detector at both rungs; visually marginal at R2).
4. Gate P2 rung-to-rung ≤ 1.5° — **TRUE** (0.87°). (The within-rung
   intercept clause of §4 failed; prediction 4 as numbered addressed the
   rung-to-rung clause.)
5. Cost ≤ 20 — **TRUE**, see below.

## Cost (measured vs filed; basis labels per P-6.2)

| piece | filed | measured | basis |
| --- | --- | --- | --- |
| res120 solve | — | 1.67 core-min (25.09 s × 4) | gross, wall × ranks, direct |
| res60 solve | — | 0.22 core-min (3.35 s × 4) | gross, same |
| mesh/init/reconstruct/locator | — | < 0.5 core-min | gross, same |
| **item total** | **20** | **~2.4** | |

**The estimate itself is graded, as its own cost_basis demanded: filed 20,
measured ~2.4 — off by ~8× on the cheap side, outside the factor-3 rule.**
The miss decomposes: the F4-anchored per-rung guess was roughly right in
cells but the acoustic-dt margin ("plus margin for the acoustic time step at
Mach 10") was priced as if dt-limiting dominated, while rhoCentralFoam at
maxCo 0.2 took only 2,111 steps on 57,600 cells. A 1/240 successor rung
prices at ~15 core-min from this measurement (8× res120), inside a fresh
filing — not run here, per the pre-registration's own refusal of quiet
extensions.

## What this bought, honestly

An unsteady self-similar shock-structure credential for the compressible
line: exact wave speed to 0.15% of travel, the double-Mach structure present
in the pre-registered contour record, trajectory-angle self-similarity to
0.05° (slope) across a 2× refinement — plus two named instrument findings
(front-locus registration defect; threshold-bias intercept artifact,
constant in cells) that price exactly what a gateable secondary-triple-point
detector needs. Numerics, not turbulence; benchmark computation, not
experiment; anchor-2-class — as pre-registered.
