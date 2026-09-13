# PPTC VP1304 — cfdsupport / TCFD, Sanaa's §J source. **No layer settings. But it is the FIRST source at OUR rotation rate.**

**Team:** cfd. **Lane:** lab-lane under `cfd-supervisor`. **Date:** 2026-09-13.
**Source named by Sanaa, §J:** `https://www.cfdsupport.com/potsdam-propeller-benchmark/`.
Fourth PPTC ingest; companions `99cacfb12`, `074d702bf`, `26dd894bd`.

**Nothing left the box** (rules 7, 8). No solver. No frozen file edited. Nobody contacted — the page
carries an `info@cfdsupport.com` address and a "questions happily answered on request" line; **no
contact was made and none will be** (rule 7).

---

## 0. THE TWO HEADLINES, IN THE ORDER THEY MATTER

**(a) IT PUBLISHES NO LAYER SETTING. It does not bear on the `nSurfaceLayers 6 → 2` ruling.**
Token counts, **both** on the web page and in the linked 6-page benchmark report:
`relativeSizes` **0**, `nSurfaceLayers` **0**, `expansionRatio` **0**, `finalLayerThickness` **0**,
`firstLayer` **0**, `minThickness` **0**, `featureAngle` **0**, `y+` **0**. **The fourteen
NOT PUBLISHED rows stay fourteen.** Its near-wall mesh is Pointwise **T-Rex**, described
qualitatively only — *"anisotropic tetrahedral cells were grown until reaching a desired stop
criteria, colliding with another front, or violating quality criteria"* — with **no count, no growth
ratio, no first-cell height.** The supervisor's ruling stands unaffected.

**(b) IT IS THE FIRST PPTC SOURCE THIS LAB HAS FOUND AT n = 15 s⁻¹ — OUR RATE.**
> **"Rotation speed: 900 RPM"** = **15.0 s⁻¹**, exactly ours.

Sikirica n=10, Cheng n=25, Klerebrant unstated — **this one matches.** Its J range and inlet
velocities corroborate it internally: with n = 15 and D = 0.25, `V = 3.75 J`, so J 0.5→1.6 gives
1.875→6.000 m/s, and the page states the velocity *"varies from 1.7 to 5.9 m/s in 11 points"*
(→ J 0.453 to 1.573). **Consistent. n = 15 s⁻¹ and D = 0.250 m are confirmed by two independent
statements on the page.**

**This does NOT by itself make its results a band** — see §4, where the fluid properties differ.

---

## 1. PROVENANCE — a web page has no title page, so this stands in its place

| | |
|---|---|
| **URL** | `https://www.cfdsupport.com/potsdam-propeller-benchmark/` |
| **Retrieved (UTC)** | **2026-09-13T18:01:50Z** |
| **HTTP** | 200, `text/html; charset=UTF-8`, 214,863 bytes |
| **sha256 of the fetched HTML** | `ef7be038c4a4bd98f24cd830744ae27462aefaaa640c5a223aec91bb45789e0b` |
| **Server `Date` header** | `Sun, 13 Sep 2026 18:01:50 GMT`; **no `Last-Modified`** |

**Sanaa's note that there is no case download is CONFIRMED** — no `.zip`, `.tgz`, `.tar` or case
archive is linked. **But the page does link a 6-page benchmark report PDF**, which is now filed:

| | |
|---|---|
| **URL** | `https://www.cfdsupport.com/download/TCFD-POINTWISE-Potsdam-Propeller-Benchmark.pdf` |
| **Retrieved (UTC)** | **2026-09-13T18:03:02Z** |
| **Filed as** | `docs/papers/propeller_rotating_machinery/lacroix_maca_2020_tcfd_pointwise_pptc_benchmark.pdf` (+ `.txt` sidecar) |
| **Bytes / sha256** | 498,525 / `86abf7f797c3ded1a21eed8eb079800b1ad833d0e845632671f5e28055a0ddfb` |
| **First page, quoted** | **"Potsdam Propeller CFD Benchmark"**; **"Daniel LaCroix — dlacroix@pointwise.com"**, **"Radek Máca — radek.maca@cfdsupport.com"** |
| **Date** | **no date printed in the document.** PDF `ModDate` **2020-03-26**; used for the filename year and labelled as file metadata, **not as a stated publication date** |

**The PDF and the web page carry substantially the same text**, so the page's claims are
corroborated by a second artifact rather than resting on one fetch.

---

## 2. WHICH SOLVER — and therefore which half of §G it may fill

> **The solver is TCFD® (CFD Support). Neither the page nor the report contains the string
> "OpenFOAM" — 0 occurrences in both.**

**Under Sanaa's §G split this source therefore files under the NUMERICS HALF ONLY.** Mesher rows may
come only from a source that *is* an OpenFOAM source, and this one **does not say it is**.

**One observation, labelled as inference and NOT used to reclassify it.** The report's mesh table
(p. 3) is laid out as *points / faces / internal faces / faces per cell / hexahedra / prisms /
pyramids / tet wedges / polyhedra / cells* — **that is the field list and column order of OpenFOAM's
own `checkMesh` output.** It is suggestive that TCFD is OpenFOAM-based. **It is not a statement by
the source that it is OpenFOAM, so it does not satisfy §G**, and this lane does not treat it as
though it did. Recorded so the supervisor can weigh it; **not acted on.**

Its mesher is in any case **Pointwise**, not snappyHexMesh — so even reclassified it would not fill
a snappy row.

---

## 3. PAPER | OURS — the rows it does supply

| # | parameter | **PAPER (cfdsupport/TCFD)** | **OURS** | verdict |
|---|---|---|---|---|
| 1 | **rotation rate** | **900 RPM = 15.0 s⁻¹** | **15.0 s⁻¹** | **AGREE — the first source that does** |
| 2 | propeller diameter | 0.25 m (implied, and consistent to 3 s.f. via `V = 3.75 J`) | 0.250 m | **AGREE** |
| 3 | turbulence model | **k-ω SST** (`kOmegaSST`) | k-ω SST | **AGREE** |
| 4 | **wall treatment** | **"Wall treatment: Wall functions"** | wall functions, `nutkWallFunction` | **AGREE — third OpenFOAM-family source to corroborate our wall-modelled choice** |
| 5 | turbulence approach | RANS | RANS | **AGREE** |
| 6 | time management | **steady-state** | steady | **AGREE** |
| 7 | flow model | incompressible | incompressible | **AGREE** |
| 8 | rotating-frame method | **MRF** | MRF | **AGREE** |
| 9 | **MRF zone diameter** | **1.5 D** | **1.3 D**, sensitivity at **1.6 D** | **our registered pair BRACKETS it again** — as it does Klerebrant's 1.47 D |
| 10 | MRF zone length | **≈4.8 D**, *"starts just upstream of the propeller and extends downstream into the wake"* | ±0.5 D | **DISAGREE** — theirs carries the wake, like Klerebrant's 9.77 D. Strengthens the registered reason already drafted for that row |
| 11 | **farfield domain** | **10 D long × 2.6 D diameter** (radius **1.3 D**) | length 9 D (3 D up + 6 D down), radius **4 D** | **radius: ours 3.1× theirs.** Fourth independent source with a radius ≤ 2.6 D. **Ours is the outlier on radius across every source.** |
| 12 | J range | **0.5 to 1.6**, **11 points** | 0.7985 to 1.4594, 6 points | theirs wider; ours fixed to measured points |
| 13 | inlet | velocity, 1.7→5.9 m/s | velocity, `V = 3.75 J` | **AGREE in form** |
| 14 | outlet | **static pressure** | fixed pressure | **AGREE** |
| 15 | **KT, KQ, J, η definitions** | `J = Va/(nD)`, `KT = T/(ρn²D⁴)`, `KQ = Q/(ρn²D⁵)`, `η₀ = J·KT/(2π·KQ)` | identical | **AGREE — fifth independent corroboration** |
| 16 | **fluid** | **ρ 997.71 kg/m³, μ 9.559e-4 Pa·s → ν = 9.581e-7 m²/s** | **ρ 998.99, ν 1.124e-6 m²/s** | **DISAGREE — theirs is warmer water; ν is 0.852× ours.** See §4 |
| 17 | mesh size | **4,088,985 cells** ("just below 4.1 M"), whole propeller | 0.8 / 2.7 / 9 M per 72° passage ≈ 4 / 13.5 / 45 M full | **their production mesh ≈ our COARSE level** |
| 18 | mesh composition | 1,018,546 points; 8,753,113 faces; **788,137 prisms** (≈19 % of cells); 39,373 pyramids; 2,052 hexahedra; 0 polyhedra; 4.203 faces/cell | — | their layer fraction is ≈19 % of cells |
| 19 | mesh quality | **average max included angle 101°, maximum 170°**; average volume ratio 1.8, **max 28** | maxNonOrtho 65 (relaxed 70), skewness 4, **cell-volume growth capped 1.25** | **their max included angle 170° and volume ratio 28 would FAIL our registered gates.** Recorded; not a reason to loosen ours |
| 20 | mesher | **Pointwise**, T-Rex anisotropic layers + Delaunay isotropic tets | snappyHexMesh | **NOT AN OpenFOAM MESHER SOURCE** (§2) |
| 21 | **layer settings** | **NOT PUBLISHED** — T-Rex described qualitatively, no count / ratio / first height | 6 (→2 proposed), 1.2, 3.125e-4 (→3.4091e-4 proposed) | **NOT PUBLISHED.** §0(a) |
| 22 | **y+** | **NOT PUBLISHED — 0 occurrences** | 30–60 registered | **NOT PUBLISHED** |
| 23 | schemes, relaxation, residual targets | **NOT PUBLISHED** | registered | **NOT PUBLISHED** |
| 24 | cost | **30 core-hours per point** = 1800 core-min/point | — | **useful calibration anchor** for our own per-point budget at a comparable 4 M-cell mesh |

---

## 4. CAN ITS RESULTS BAND OUR ACT? — **NO, AND NOT FOR THE USUAL REASON**

**The rotation-rate objection that killed every previous source does not apply here** — n = 15 s⁻¹
matches ours exactly (§0b). That is genuinely new.

**But two other things stop it:**

1. **The fluid differs.** ν = 9.581e-7 m²/s against our 1.124e-6 — **0.852×**, i.e. their water is
   warmer. At the same n and J the Reynolds number is **1.17× ours**, so the friction coefficients
   and the KQ they report are not at our condition. Small, but it is a real offset and it is **in
   the direction that matters for a torque comparison.**
2. **No numeric results are published.** The page and the report present KT, 10KQ and η **only as
   plotted curves against J** — there is **no table of values** in either artifact. **Nothing can be
   read off to the precision a band requires.** Digitising a marketing chart is not a comparator.

> **VERDICT: context only. Not a band.** For a different reason than Sikirica, Cheng and Klerebrant —
> which is worth saying, because "the rate matches" is exactly the kind of partial agreement that
> invites a wrong validation.

**Two internal inconsistencies in the source, recorded rather than smoothed:**
- The page says **11** simulation points in one place and *"10 propeller modes (flow rates),
  corresponding to the 10 guide vanes openings"* in another. **PPTC has no guide vanes.** That
  sentence is template text carried over from a water-turbine case study.
- The heading **"Results #2 — Main Propeller Characteristics — snappyHexMesh"** appears with **no
  snappyHexMesh settings, no snappyHexMesh mesh statistics, and body text identical to Results #1**
  (guide-vane boilerplate again). **`snappyHexMesh` does not occur at all in the downloadable
  report.** **This heading must not be read as a published snappyHexMesh PPTC setup** — there is no
  setup under it. Flagged explicitly because it is the one string on the page that could mislead a
  later reader into thinking the snappy gap had been closed.

---

## 5. WHAT THIS ADDS, AND WHAT IT DOES NOT

**Adds:** a fourth independent corroboration of **MRF + steady + incompressible + k-ω SST + wall
functions** on this propeller; a **fifth** corroboration of the non-dimensionalisation; an **MRF zone
diameter of 1.5 D** that our registered 1.3/1.6 D pair brackets; a **fourth** domain radius at or
below 2.6 D against our 4 D; and a **cost anchor of 30 core-hours per point** at ≈4 M cells.

**Does not add:** any layer setting, any y+, any scheme, any relaxation factor, any residual target,
any numeric result, and anything at all to the **mesher half** of §G.

**No gate, threshold, cap or label is altered by this file.** Rows 9, 10, 11, 16, 19 and 24 are
offered to the supervisor for the reconciliation table and the new registered configuration;
**proposals only.**

## 6. COST

No solver. Two fetches, text extraction, scans. **Measured: 2.9 core-minutes**, single rank. Lane
cumulative **32.8 core-minutes** ≈ **\$0.0281 derived, not measured** at the owner-stated
\$0.0513/core-h — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). No
pre-registered estimate for a retrieval task, so no calibration ratio is claimable.
