# F7a re-gate specification — the measurement definition, pinned contractually

**Status:** SPEC v1.0, frozen 2026-08-11. Zero compute was spent producing it.
**Scope:** rung (a) of F7, the Martin & Moyce (1952) square-column dam break.
**Owner of the definition:** this file. Every other file cites it; none restates it.
**Frame for every number below:** repo `/home/ubuntu/Certonomous`, tracked working
tree at commit `c05a03e0` (the reconstruction script landed at `38d05c40`);
extraction from git-**tracked** field data only, no untracked or regenerated
fields; `demo-output/website/campaign/F7_runs/` and `F7_runs/F7a_R1/`.

---

## 0. Why this file exists, and the one thing it must not get wrong

The 2026-07-28 gate recorded **+13.6% mean / 21.3% max** and a coarse-mesh
**−13.2%** that "flipped sign under refinement". The R1 audit (2026-07-30)
retracted the sign flip and the stated root cause and re-measured the best case
at **+8.2% mean / +11.0% max**. That retraction is copied near-verbatim into six
files; `docs/MEMORY_ARCHITECTURE.md` D-12 names it *"the corpus's single largest
duplication hotspot"*.

The story attached to that retraction is that an **ambiguity in the measurement
definition** caused it. This spec exists to retire the ambiguity. But a spec
built on a wrong story is worse than no spec, so §1 tests the story against the
data before §2 writes the contract.

**The short version of what §1 found: the ambiguity is real and it is large —
and it does not explain the gate's residual failure.** Both halves of that
sentence are load-bearing, and the second half is the one nobody has written
down before.

---

## 1. THE EXHIBIT — the old ambiguity, reproduced as a measured fact

### 1.1 What the old definition actually said

The old front criterion survives verbatim in the case dictionaries, in
`F7_runs/damBreak_MM_a2p25in_medium_closedbox/system/sampling`:

> *"Horizontal line just above the floor (y = half of first cell height), used to
> locate the surge-front position (alpha.water = 0.5 crossing) as a function of
> physical time."*

with the sampled line at `start (0 0.00142875 0.00142875)`, `end (0.85725
0.00142875 0.00142875)`, `nPoints 1201`, `interpolationScheme cellPointFace`,
and `extract_front.py` taking the **last** downward crossing of α = 0.5.

Read as English, that sentence does not determine a number. "The first cell
above the floor" can mean the floor-adjacent cell or the cell above it. "The
α = 0.5 crossing" does not say interpolated or nearest-cell, nor which crossing
when α is non-monotone along the line — which it is, because the interface is
smeared over several cells, exactly as the brief anticipated. And the sentence
is silent on the time origin and on which axis the deviation is measured along.

### 1.2 Method

`F7_runs/old_spec_readings.py` (new, committed at `38d05c40`) evaluates seven
faithful readings of that sentence. It reads **only already-written, git-tracked
`alpha.water` and cell-centre `C` fields**. It launches no solver. Each reading
is one a competent agent could defend from the prose; none is a strawman:

| id | reading of the old prose |
|---|---|
| `A_row0_interp` | row 0 (centres at y = Δy/2), α = 0.5, linear interpolation between cell centres, furthest crossing — **closest to what was executed** |
| `B_row1_interp` | row 1 (y = 3Δy/2) — "the first cell **above** the floor [cell]" |
| `C_row0_cell` | row 0, no interpolation: last cell centre with α ≥ 0.5 |
| `D_row0_face` | row 0, no interpolation: downstream face of that cell |
| `E_row0_first` | row 0, interpolated, **first** crossing from the left |
| `F_row0_a005` | row 0, interpolated, threshold α = 0.05 (air-side edge of the smear) |
| `G_row0_a095` | row 0, interpolated, threshold α = 0.95 (water-side edge) |

Row grouping was verified before use: rows 0 and 1 carry the full `nx` cell
count on all 15 tracked `F7a_R1` cases.

### 1.3 Result — on the exact case that produced the retracted number

`F7_runs/damBreak_MM_a2p25in_medium_closedbox`, dx = dy = a/20, 300×40:

| reading | mean dev, 6 stations | mean dev, 8 stations | max abs, 8 stations |
|---|---|---|---|
| `A_row0_interp` | **+12.7%** | **+13.4%** | 20.4% |
| `B_row1_interp` | **−19.2%** | **−16.1%** | 30.4% |
| `C_row0_cell` | +12.4% | +13.8% | 20.7% |
| `D_row0_face` | +12.7% | +14.1% | 20.9% |
| `E_row0_first` | +12.7% | +13.3% | 20.3% |
| `F_row0_a005` | +13.4% | +13.4% | 20.2% |
| `G_row0_a095` | **−6.4%** | **−9.6%** | 23.7% |

**Reading A reproduces the published +13.6% / 21.3% to within 0.2 and 0.9
percentage points** — from tracked fields, by an independently written
extractor, at the 0.05 s write cadence rather than the 0.005 s `sets` cadence
the original used. The published number is confirmed as a faithful record of
*one* reading.

**Reading B, on the same solve, the same instant, the same data, gives −16.1%.**
A 29.5-point swing on the mean and a change of sign, produced by nothing but
which of two English readings of one clause a reader picks. Reading G moves it
another way. **The ambiguity is exhibited, not asserted.**

### 1.4 The finding that qualifies the story — the ambiguity is a function of vertical resolution

Sweeping the same seven readings across the tracked `F7a_R1` mesh ladder
(mean deviation, 6 graded stations, per reading):

| case | dx | dy | A row0 | B row1 | C cell | D face | E first | F α=.05 | G α=.95 | **spread** |
|---|---|---|---|---|---|---|---|---|---|---|
| `res8_base` | a/8 | a/8 | −9.4 | −65.2 | −10.2 | −9.4 | −11.5 | +13.1 | −51.1 | **78.2 pts** |
| `res16_base` | a/16 | a/16 | +12.0 | −34.3 | +11.8 | +12.2 | +11.3 | +13.6 | −18.9 | **48.0 pts** |
| `res20_base` | a/20 | a/20 | +12.5 | −18.4 | +12.2 | +12.5 | +12.5 | +13.2 | −6.4 | **31.6 pts** |
| `res32_base` | a/32 | a/32 | +11.4 | +11.4 | +11.2 | +11.4 | +11.4 | +11.9 | +10.2 | **1.7 pts** |
| `res32y64_base` | a/32 | a/64 | +9.7 | +9.8 | +9.4 | +9.6 | +9.7 | +10.1 | +9.2 | **0.8 pts** |
| `res32y128_base` | a/32 | a/128 | +8.2 | +8.3 | +8.1 | +8.3 | +8.2 | +8.6 | +7.8 | **0.8 pts** |
| `res32y256_base` | a/32 | a/256 | +10.8 | +10.8 | +10.6 | +10.8 | +10.8 | +11.2 | +10.5 | **0.7 pts** |
| `res64_base` | a/64 | a/64 | +11.1 | +11.2 | +11.0 | +11.1 | +11.1 | +11.3 | +10.9 | **0.4 pts** |
| `res64y128_base` | a/64 | a/128 | +9.3 | +9.3 | +9.2 | +9.3 | +9.3 | +9.5 | +9.1 | **0.4 pts** |

Read the last column. The spread across every plausible reading of the old,
un-pinned definition collapses from **78 percentage points at a/8 to 0.4 at
a/64**, monotonically. Three consequences, and they are the substance of this
spec:

1. **The old definition was not ambiguous in the abstract. It was ambiguous
   *because the meshes it was used on could not resolve the film*.** At a/8–a/20
   the leading tongue is one or two cells thick, so "which row" and "which α
   level" are questions about different fluid. At a/32 and finer they are
   questions about the same fluid and every reading agrees.
2. **Pinning the definition is therefore necessary but not sufficient.** A spec
   that pins the words and lets the mesh float would still be satisfiable two
   ways. This spec pins a **resolution floor** (§2.5) for exactly this reason.
   That clause is the one this exhibit bought, and no amount of careful prose
   about probes would have produced it.
3. **The residual failure is not a measurement artifact.** At a/32 and finer,
   every reading of the *old* definition lands between **+7.8% and +11.9%** —
   all of them fail a 5% tolerance. The gate's residual is definition-robust.

### 1.5 Two further ambiguities the old prose never addressed, also measured

**Comparison axis.** The Martin & Moyce points sit at round *Z* values
(6, 7, … 13) with measured *T* — the experiment measured a time-to-station, so
"deviation" can be taken along either axis, and the old spec never said which:

| case | deviation in **Z at reference T** | deviation in **T at reference Z** |
|---|---|---|
| `damBreak_..._medium_closedbox` (a/20) | **+12.7%** mean6 | **−11.1%** mean6 |
| `res32y128_base` (a/32, a/128) | **+8.2%** mean6 | **−8.3%** mean6 |

Same series, same reading, same data — the sign of the reported error depends
on which axis you project onto. A front that is *ahead in space* is
*early in time*, and a percentage of Z is not a percentage of T.

**Time origin.** Taking t = 0 at the first solver write instead of at release:

| case | t=0 at release (as published) | t=0 at first solver write |
|---|---|---|
| `damBreak_..._medium_closedbox` | +12.7% mean6 | **+26.4%** mean6 |
| `res32y128_base` | +8.2% mean6 | **+14.2%** mean6 |

A 6.0- to 13.7-point shift from a reading of "time origin" that a fresh agent
could adopt without noticing it had made a choice.

**Not evaluable from the archive, and recorded as such:** re-zeroing t at the
instant the front leaves the column footprint (Z = 1) is a real convention in
the dam-break literature, and it **cannot be evaluated on this data**. The front
is already at Z = 1.13–1.44 by the first written field. The write cadence
(Δt = 0.025 s, ΔT = 0.328) does not resolve the release transient. §2.3 forbids
this convention rather than leaving it available and unmeasurable.

### 1.6 What the exhibit does and does not license

| claim | status |
|---|---|
| The old definition admitted readings differing by up to 78 points, with sign changes | **MEASURED**, §1.3–1.4 |
| The recorded +13.6% / 21.3% is a faithful record of one such reading | **MEASURED**, reproduced to 0.2 / 0.9 pts |
| The retracted coarse-mesh sign flip is an artifact of the definition | **MEASURED** — reading A alone flips from −9.4% (a/8) to +12.5% (a/20) |
| The ambiguity explains the gate's residual +8.2% failure | **REFUTED.** At dy ≤ a/32 every reading lands +7.8% to +11.9%, all FAIL |
| The residual has a physical cause | Not settled here. R1 §4 names resolved bed friction as the dominant measured mechanism and R1 §6 lists what is still open. This spec does not adjudicate it |

The six files that carry the D-12 retraction narrative are **not wrong**, but
the compressed version of it that circulates — "the FAIL was a measurement
artifact" — **is**. The measurement artifact was worth ~20 points of the
*originally reported* number and essentially none of the *current* one.

---

## 2. THE CONTRACT

Everything in §2 is normative. Two independent agents given only §2 and the same
case directory must compute the same number. Where §2 says FAIL LOUD, the
extractor raises and produces no verdict; it never falls back to a default.

### 2.1 Probe row — *there is none, and that is the point*

**A row-based probe is prohibited.** §1.4 shows the row choice is worth up to
53 points. The graded quantity is a **depth integral over the whole column**,
which has no row to choose.

- **Coordinate frame.** Right-handed Cartesian, metres. Origin at the mutual
  corner of `leftWall` (x = 0), `lowerWall` (y = 0) and the z = 0 `empty` plane.
  **x** runs along the floor in the direction of surge propagation; **y** is
  vertically up, anti-parallel to `constant/g` = (0, −9.81, 0); **z** is
  spanwise, one cell, `empty`. Length scale **a = 0.05715 m exactly**
  (2¼ in × 0.0254 m/in). Reduced coordinate **Z = x / a**.
- **Fields.** The **reconstructed single-domain** `alpha.water` internal field
  at each written time, and the cell-centre field `C` written once by
  `postProcess -func writeCellCentres`. Decomposed `processor*/` data is never
  read directly. `.gz` and plain forms both accepted.
- **Columns.** Cells are grouped into columns by cell-centre x rounded to **8
  decimal places**. **Assertion, FAIL LOUD:** every column must contain exactly
  n_y cells and every row exactly n_x cells, with n_x·n_y = the internal field
  length. (9 decimal places splits rows on ASCII round-off on the a/16 family —
  20 physical rows appear as 37. This is why the digit count is pinned rather
  than left to the implementer.)
- **Quadrature.** h(x_i) = Σ_j α_ij · Δy, over **all** n_y cells of column i,
  from y = 0 to the top of the domain, with **no truncation and no free
  surface sought**. Δy is the uniform cell height. **Assertion, FAIL LOUD:**
  the mesh is uniform in y; graded on a graded mesh, the extractor refuses.
- **Units of h.** h has dimensions of length: it is water volume per unit x per
  unit span. It is *not* an interface height.

### 2.2 Front criterion

- **Definition.** The front is the **largest x at which h(x) crosses downward
  through h\* = 0.02 a**, located by **linear interpolation between the two
  adjacent column-centre x values that bracket the crossing**. The search scans
  from the far wall (x = 15a) toward x = 0 and returns the **first** crossing it
  meets, which is by construction the furthest downstream one.
- **h\* = 0.02 a = 1.143 mm**, fixed. Chosen because R1 §2 measured the metric
  to be essentially threshold-free at this level on the finest mesh (0.24%
  spread over 0.01a–0.04a) and because 1.143 mm is physically the leading sheet
  rather than a numerical tail.
- **Why not an α threshold.** An α level on an interface smeared across several
  cells is precisely the ambiguity §1 measured — readings F and G differ from A
  by up to 31 points. A depth integral is insensitive to how α is distributed
  within a column; it responds only to how much water is there.
- **When the interface is smeared across several cells** — which it will be —
  the smear redistributes α within a column and leaves h(x) almost unchanged.
  The residual sensitivity is not assumed away; it is **measured every run** by
  the mandatory sweep below.
- **Mandatory uncertainty, reported with the verdict.** The identical extraction
  is repeated at **h\* ∈ {0.01a, 0.02a, 0.03a, 0.04a}**. The spread of Z across
  those four, **at every graded station**, is the metric's own uncertainty and
  is published beside the deviation. **If that spread exceeds 1.0% of Z at any
  graded station, the verdict is UNGRADEABLE, not FAIL.**
- **No crossing found** at a graded station ⇒ that station is UNGRADEABLE.
- **Front past the far wall.** If the front reaches Z ≥ 14.5 at or before a
  graded station, that station is UNGRADEABLE (wall proximity confounds it).
  This is declared in advance precisely so it cannot be invoked selectively
  afterwards.
- **Monotonicity guard — FAIL LOUD, and it is not hypothetical.** The extracted
  front must be non-decreasing in time: a surge front does not retreat. The
  extractor walks the written times in order and **stops at the first time at
  which Z decreases by more than 0.05**; that time and every later one are
  UNGRADEABLE. *Why this clause exists:* once the surge reaches the far wall,
  h(x) no longer crosses h\* downward at the toe, and the furthest-crossing
  search silently returns a **spurious crossing far upstream** — Z ≈ 1.59, back
  in the collapsing column. `grade_f7a.py` as written has no such guard and
  averages those values into its reported mean: it prints
  *"FRONT vs EXPERIMENT: mean −0.8%"* for `res16_base` and *"mean −6.7%"* for
  `res16_papermodel`, both of which are arithmetic over two ≈ −87% artifacts.
  The R1 write-up avoided this by restricting to six stations by hand; the
  script never enforced it. **A silent garbage-in-mean is exactly the fail-open
  defect docket B2 exists to kill,** and it is fixed here by contract rather
  than by remembering. Numbers previously read off `grade_f7a.py`'s unrestricted
  mean line should be treated as unframed until re-derived under this clause.

### 2.3 Time origin

- **t = 0 is the instant of release**: the state in which α = 1 exactly on
  0 ≤ x ≤ a, 0 ≤ y ≤ a and α = 0 elsewhere, with **U = 0 everywhere**, as
  written by `setFields` into the `0` directory. Release is instantaneous, which
  is also what the comparator paper does.
- **T = t · √(g/a)**, with **g = 9.81 m/s² exactly** and **a = 0.05715 m
  exactly**. t is the OpenFOAM time value, in seconds, unshifted.
- **Explicitly NOT the first solver write.** §1.5 measures that reading at +6.0
  to +13.7 points of error.
- **Explicitly NOT re-zeroed at Z = 1** or at any front-position event. §1.5
  records that such a convention is not even evaluable at this write cadence.
- **No gate-withdrawal correction is applied.** The 1952 physical withdrawal
  time is unknown (R1 §6; the original paper is not open access and the
  secondary source does not state it). A constant time shift is in any case
  refuted as a repair: D1 measured the implied ΔT growing from 0.37 to 2.43
  across the eight stations rather than staying constant. Any residual
  attributable to release timing is **declared as an open comparison-basis
  uncertainty, not corrected out**.
- **Restart interaction — the clause that makes the above survive a restart.**
  OpenFOAM's `startFrom latestTime` preserves absolute t, so in principle a
  restart is transparent. The spec does not rely on that; it checks it:
  1. `controlDict` must carry `startFrom latestTime` (or `startTime` with
     `startTime 0` on a cold run). Any other value ⇒ UNGRADEABLE.
  2. For **every** graded time directory the extractor reads
     `<t>/uniform/time` and asserts its `value` equals the directory name to
     1e-9. Mismatch ⇒ **FAIL LOUD**.
  3. The set of written times must be exactly the arithmetic sequence
     {Δt_w, 2Δt_w, …} with a single Δt_w across the whole run. A restart that
     changes `writeInterval` changes which points get interpolated and is
     therefore a different measurement. Mismatch ⇒ UNGRADEABLE.
  4. `writeInterval` must satisfy **ΔT ≤ 0.35** (Δt_w ≤ 0.025 s at a = 0.05715),
     so every graded station is bracketed by written times.

### 2.4 The comparison

- **Reference data.** Martin & Moyce (1952), square-column collapse, a = 2¼ in.
  The original paper is **not open access and has not been read by this lab**;
  the points are digitised from **Fig. 7 (left column) of Leakey, Glenis &
  Hewett, arXiv:2108.08769** (published as *Computer Methods in Applied
  Mechanics and Engineering* 393:114763, 2022), §3.3.2. Digitised **twice
  independently** — 2026-07-28 and the 2026-07-30 R1 audit — agreeing to
  ≤ 0.01 in T and ≤ 0.005 in Z. Primary artifact:
  `F7_runs/fig7_digitised_R1.json`. **This is a digitisation of a secondary
  source's rendering of a primary source. That is a real limitation of the
  comparison basis and is carried on the verdict's face, not buried here.**
- **The frozen reference table** (T, Z), all eight points:
  (3.90, 6.00) (4.49, 7.00) (5.17, 8.00) (5.91, 9.00) (6.70, 10.00)
  (7.72, 11.00) (8.58, 12.00) (9.53, 13.00).
- **Graded stations: the first six**, T = 3.90 … 7.72, Z = 6 … 11. Frozen here,
  before the run. Reason, stated in advance: on meshes coarser than a/32 the
  surge passes the far wall before T = 8.58, so the last two are not evaluable
  across a refinement ladder, and the eighth is wall-confounded on every mesh.
- **The last two points are extracted and reported anyway**, labelled
  *reported, not graded*. They may not be moved into or out of the graded set
  after the fact.
- **Axis: deviation in Z, evaluated at the reference T.** Frozen. Sim Z(T) is
  linearly interpolated between the two written times bracketing each reference
  T; a station not bracketed on both sides is UNGRADEABLE. The **deviation in T
  at reference Z is also computed and reported** — §1.5 shows it carries the
  opposite sign — but it does **not** decide the gate.
- **Deviation** at station k: d_k = (Z_sim,k − Z_ref,k) / Z_ref,k, **relative**,
  in percent. Relative rather than absolute because Z spans 6 → 11 across the
  graded set and a fixed absolute band would be nearly twice as strict at the
  first station as at the last. The **absolute** deviation in Z units is
  reported alongside.
- **Tolerance: 5%, applied to max|d_k| over the six graded stations.**
  The gate **PASSES** iff max_k |d_k| ≤ 0.05. The **mean** of d_k is reported
  and does **not** decide the gate — a mean hides a single station at 20%,
  and the original gate's citing of both without saying which one bound is
  itself a fifth un-pinned degree of freedom.
- **Why 5% is defensible rather than arbitrary.** The comparator — the same
  figure's own published inviscid simulation, digitised in R1 — achieves
  **−4.3% to +1.8%** on this benchmark at dx = dy = a/16. 5% is the standard a
  published solver demonstrably reaches here. It is not a house number.
- **Verdict is three-valued: PASS / FAIL / UNGRADEABLE.** Per docket B2, the
  extractor answers *did the check run?* before *what did it find?* Any FAIL
  LOUD assertion, any UNGRADEABLE station, or a threshold spread over 1.0%
  yields UNGRADEABLE for the whole gate.

### 2.5 Resolution floor — the clause the exhibit bought

- **A gate verdict may be taken only on a mesh with dy ≤ a/128** (0.446 mm).
  Basis: R1 §4 measured the leading film at ≈ 2.9 mm thick at Z = 11 and showed
  the bed shear under it is under-predicted by ~40% at dy = a/32 (two cells
  across the film). At a/128 the film carries ≈ 6–7 cells and the boundary layer
  is resolved. Below this floor the *physics* of the graded quantity is not
  resolved.
- **A diagnostic or ladder rung may be run coarser, but no verdict is taken on
  it below dy ≤ a/32.** Basis: the §1.4 spread column. Above a/32 the definition
  is not stable enough for the word "verdict" to mean anything.
- **Both floors are on vertical spacing.** dx is governed by the convergence
  ladder, not by this clause; R1's isolation of dy as the controlling variable
  (a/32 y-ladder at fixed dx) is the evidence.
- **No Richardson extrapolation may be quoted** until the y-ladder increments
  are geometric. R1 §6 measured them at −3.9, −2.3, −2.1 points: shrinking but
  not geometric, so the ladder is not in an asymptotic range. Stating that is
  the requirement; extrapolating anyway is prohibited.

### 2.6 Anti-relitigation clause

Only the four thresholds in §2.2, the six stations in §2.4, and the Z-at-T axis
decide the gate. A verdict may not be revised by choosing a different threshold,
station set, axis, mesh or reading after the numbers are known. A change to any
of them is a **new version of this spec**, dated, with the reason recorded — and
it re-grades every case, not the convenient one.

---

## 3. THE GATE VERDICT, TAKEN NOW, AT ZERO COMPUTE

The contract in §2 is executable against data already in the tree. It was, and
it does not need the re-run to produce a verdict. Katie asked for a gate verdict
either way; here it is.

**Case:** `F7_runs/F7a_R1/res32y128_base` — dx = a/32, dy = a/128, 76,800 cells,
paper-matched domain 15a × 1.25a, all four boundaries walls, cAlpha = 1,
σ = 0.07, no-slip floor, laminar. The finest-dy case satisfying §2.5's verdict
floor. **Extractor:** `F7_runs/front_metrics.py` (the §2.1–2.2 metric as
written), thresholds 0.01a/0.02a/0.03a/0.04a.

| T | Z_ref | h\*=0.01a | h\*=0.02a | h\*=0.03a | h\*=0.04a | spread in Z | spread as % of Z |
|---|---|---|---|---|---|---|---|
| 3.90 | 6.00 | +9.67% | +9.45% | +9.22% | +8.99% | 0.0406 | 0.68% |
| 4.49 | 7.00 | +7.30% | +7.11% | +6.93% | +6.76% | 0.0380 | 0.54% |
| 5.17 | 8.00 | +6.96% | +6.80% | +6.65% | +6.45% | 0.0409 | 0.51% |
| 5.91 | 9.00 | +7.33% | +7.20% | +7.07% | +6.90% | 0.0388 | 0.43% |
| 6.70 | 10.00 | +8.06% | +7.89% | +7.77% | +7.65% | 0.0406 | 0.41% |
| 7.72 | 11.00 | +11.14% | +11.03% | +10.92% | +10.78% | 0.0394 | 0.36% |
| 8.58 | 12.00 | +11.47% | +11.38% | +11.28% | +11.15% | 0.0384 | 0.32% *(reported, not graded)* |
| 9.53 | 13.00 | +12.33% | +12.20% | +12.10% | +12.00% | 0.0422 | 0.32% *(reported, not graded)* |

| h\* | 6-station mean | **6-station max\|d\|** | verdict at 5% |
|---|---|---|---|
| 0.01a | +8.41% | 11.14% | FAIL |
| **0.02a (the pinned value)** | **+8.25%** | **11.03%** | **FAIL** |
| 0.03a | +8.09% | 10.92% | FAIL |
| 0.04a | +7.92% | 10.78% | FAIL |

- Metric uncertainty gate (§2.2): max spread **0.68%** of Z, against the 1.0%
  UNGRADEABLE trigger — **passes**, so the verdict stands as a verdict.
- Every §2.3 restart assertion is vacuous here (single cold run, uniform
  Δt_w = 0.025 s = ΔT 0.328 ≤ 0.35). Every §2.1 structural assertion holds.
- Reported, not graded, per §2.4: deviation in T at reference Z is **−8.3%**
  mean over the six stations — opposite sign, same data.

### **GATE (a): FAIL.** max deviation +11.03% at T = 7.72, against a declared 5% tolerance.

**This FAIL is now un-relitigable**, which the previous two were not. It does not
depend on a row, a threshold, an interpolation rule, a crossing rule, an axis, a
time origin, or a station set: §1.4 shows every reading of even the *old*
definition lands +7.8% to +11.9% on this class of mesh, and §3's own sweep
moves the answer by 0.36 points across the whole admissible threshold range.

**Rungs (b) Wigley and (c) DTMB 5415 / KCS remain blocked** by the standing
ladder rule. R1 §7's note that the failing mechanism — friction on a
sub-millimetre film at a dry-bed contact line — is not the physics a
wave-resistance case is gated on remains a live scoping question for Katie, and
this agent does not resolve it.

---

### 3.1 A second zero-compute result the archive was already holding

R1 ran a case called `res16_papermodel` and listed it in its evidence, but
**never reported its front numbers**. Its provenance is
`{'res': 16, 'calpha': 0.0, 'sigma': 0.0, 'inviscid': True}` — that is the
comparator's **own stated physical model** (inviscid, no surface tension, no
interface compression) on the comparator's **own mesh** (240 × 20, dx = dy =
a/16) in the comparator's **own domain** (15a × 1.25a, all walls). Graded here
under §2, with the §2.2 monotonicity guard applied:

| T | Z_ref (expt) | Z_sim | vs experiment | comparator's own curve | **vs comparator** |
|---|---|---|---|---|---|
| 3.90 | 6.00 | 7.104 | +18.4% | 5.768 | **+23.2%** |
| 4.49 | 7.00 | 8.157 | +16.5% | 6.701 | **+21.7%** |
| 5.17 | 8.00 | 9.388 | +17.3% | 7.676 | **+22.3%** |
| 5.91 | 9.00 | 10.714 | +19.0% | 8.727 | **+22.8%** |
| 6.70 | 10.00 | 12.029 | +20.3% | 9.846 | **+22.2%** |
| 7.72 | 11.00 | 14.235 | +29.4% | 11.134 | **+27.8%** |
| | | | **mean +20.2%** | | **mean +23.3%** |

For contrast, our ordinary baseline on the same mesh (`res16_base`: viscous,
σ = 0.07, cAlpha = 1) gives **+13.5%** vs experiment and **+16.4%** vs the
comparator.

**Read that carefully. Giving our solver the comparator's physics, on the
comparator's mesh, in the comparator's domain, moves us 6.7 points further from
the experiment and leaves us 23.3% ahead of the comparator's own published
curve** — while that curve sits at −4.3% to +1.8% of the experiment.

Three things follow, and none of them was written down before:

1. **There is a ~23% code-to-code gap that is not viscosity, not surface
   tension, not interface compression, not mesh, and not domain** — every one of
   those is matched in this case. What remains different is the discretisation
   itself (their Godunov-type Riemann solver with split pressure and a superbee
   limiter, against our MULES/PIMPLE VOF) and their **unstated front-extraction
   definition**. R1 §6 flagged the latter as an unquantified offset; this
   measures it at 23.3%, which is **larger than the gate deviation the campaign
   has been chasing**.
2. **R1's bed-friction finding survives but shrinks in significance.** Within
   our solver, friction genuinely helps — that is a measured single-variable
   result and it stands. But the comparator reaches the experiment with *no
   friction at all*, so friction cannot be the explanation of why they agree and
   we do not.
3. **This is the argument against buying more mesh.** A refinement ladder
   explores a direction in which the residual has already been shown to be
   small; the unexplained 23% lies in the comparison basis.

Stated as a limitation, not smuggled past: this is one case at one mesh, and
`--inviscid` sets ν = 1e-12 rather than solving genuinely inviscid equations.
The finding is a strong signal to redirect effort, not a closed result.

## 4. What the re-run would buy, given §3 already produced a verdict

Katie's instruction was a re-run with the definition pinned. §3 shows the
verdict does not require it: the pinned definition applied to tracked data gives
FAIL with the uncertainty measured. Spending compute to re-derive a number we
already hold would be theatre.

What compute would genuinely settle is narrower, and is priced in
`F7a_REGATE_PREREGISTRATION.md` §5 as a request to Katie, not a plan. In one
line each:

1. **Does the y-ladder ever enter an asymptotic range?** R1 measured increments
   −3.9, −2.3, −2.1 points — shrinking, not geometric — so no extrapolated
   value is quotable and the a/256 rung carries an unexplained early-time
   outlier. One dy = a/512 rung at dx = a/32 would show whether the sequence is
   converging to ≈ +8% or drifting.
2. **Is the residual transitional bed friction?** R1 §6 computed the film
   Reynolds number at the toe as ≈ 3 × 10³, above the flat-plate transition
   range, on a laminar run. Untested, and R1 itself flags that a transition
   model on a film two cells thick may not be well-posed.
3. **Is the comparison basis itself carrying the residual?** §3.1 has now
   measured the code-to-code gap at **+23.3%** with physics, mesh and domain all
   matched. Recovering the comparator's front definition, and its scheme's
   behaviour at the toe, is a **literature task costing zero compute**.

**Item 3 outranks items 1 and 2 and should be executed before either is
bought.** L-8's rule is cheapest-and-most-often-guilty first; §3.1 makes the
comparison basis both. Buying a finer mesh to chase an +8% residual, while a
+23% unexplained offset sits in the comparator, would be refining in the wrong
direction — and items 1 and 2 are priced at 760–1520 core-min between them,
against the entire R1 campaign's 387.4.

---

## 5. Sources

- `F7_runs/old_spec_readings.py` — the §1 exhibit. Reads tracked fields only.
- `F7_runs/front_metrics.py`, `F7_runs/grade_f7a.py` — the §2 metric and grading.
- `F7_runs/fig7_digitised_R1.json` — the reference points, second digitisation.
- `F7_runs/damBreak_MM_a2p25in_medium_closedbox/system/sampling` — the old
  definition, verbatim, as executed.
- `demo-output/website/campaign/F7_marine_free_surface.md` — the case record;
  R1 §§0–7 is the retraction this spec is built on top of.
- `docs/MEMORY_ARCHITECTURE.md` D-12 — the six-file duplication hotspot.
- Leakey, Glenis & Hewett, arXiv:2108.08769 / *CMAME* 393:114763 (2022), §3.3.2
  and Fig. 7. **Read in this repo's prior passes (D1, R1), not re-fetched by
  this agent.** Every statement attributed to it here is quoted from the R1
  audit's verbatim re-reading, not from recall.
- Martin & Moyce (1952). **Not open access; never read by this lab.** Present in
  this spec only through the digitisation above.

---

## 6. Amendment, 2026-08-14 — the contract was executed, and what that struck

**Landed at `86704ddf`.** §2 was not changed: its constants were transcribed
into `F7_runs/f7a_contract.py` verbatim, and `sdk/tests/test_f7a_contract.py`
re-parses them out of §2's own prose on every run, so the two cannot diverge
without a test failing. 42 tests; against the tree before that commit, 0
passed. §2.6 was not invoked and no threshold, station set, axis or mesh was
changed.

The reason for the amendment was that §2 had described itself as normative
while living only in prose. `front_metrics.py`, which §3 named as its
extractor, landed at `4aad8298`, twelve days before the spec at `1393b8b4`,
and implemented none of §2's assertions, guards, station set, tolerance or
verdict. Executing the prose found five divergences and one defect in §2
itself. The commit message at `86704ddf` records them; the two that move
recorded conclusions are struck below.

### 6.1 STRUCK, 2026-08-14 — "the deviation was roughly halved, +13.6% → +8.2%"

Carried by six surfaces (`docs/MEMORY_ARCHITECTURE.md` D-12 lists them). The
sentence is **struck as a comparison, and kept as two separate readings**,
per L-76.

It compared readings taken under **two different measurement definitions** and
on **two different meshes**, and attributed the movement to neither. The
+13.6% / 21.3% was measured by an α = 0.5 line probe on one cell row
(`gate_compare.py` via `extract_front.py`); §2 grades a depth integral over
the whole column. Holding the case fixed and changing only the definition was
measured at `86704ddf` and moves the six-station mean by **+12.7% → +13.1%**,
under half a point. The move to +8.25% was therefore **attributable to
refinement, not to the change of metric** — which is the direction that
matters, since a metric change that flattered the result would be the one
repair §5's sources say this lab must never make.

Stronger, and the reason this is a strike rather than a footnote: the case the
+13.6% / 21.3% was measured on — `damBreak_MM_a2p25in_medium_closedbox` —
**cannot carry a verdict under §2 at all.** Its write cadence was ΔT = 0.655
against §2.3.4's cap of 0.35, so its graded stations were never bracketed the
way §2.4 requires, and its mesh was a/20 against §2.5's a/128 verdict floor.
The published figure was not a stricter or looser reading of the current gate;
it was a reading of a case the current gate does not admit. **Prior gate
verdicts are not comparable to §3's, and no surface should present them as a
trend.**

### 6.2 STRUCK, 2026-08-14 — `res32y256_base` at "+10.8% mean, with an unexplained early-time outlier of +18.1%"

Recorded by R1 §6 and carried into §1.4 of this spec and
`F7_marine_free_surface.md`. **Struck and kept.** Under §2.2's mandatory
threshold sweep the T = 3.90 station is not an outlier awaiting a physical
explanation: the metric's own spread there was measured at **14.97% of Z**,
fifteen times the 1.0% UNGRADEABLE trigger, because at h\* = 0.04a the
crossing landed on a different feature (Z = 6.04 against Z = 7.07 at the other
three thresholds). The T = 4.49 station exceeded the trigger too, at 4.08%.
**The finest tracked mesh yields no verdict**, and its +10.8% mean was unframed.

### 6.3 Struck, minor — §3's own table at T = 9.53

§3 reported that station at +12.20%, labelled *reported, not graded*. §2.2's
wall clause disqualifies it outright: the front sat at Z = 14.59, past the
Z ≥ 14.5 trigger. No verdict depended on it and none moves. Corrected in the
contract's output rather than in §3's table, which records what was published.

### 6.4 A defect in §2.1, recorded and not repaired here

§2.1 pinned the column rounding at **8 decimal places** "rather than left to
the implementer". Executed, 8 dp does not close two tracked cases: `res8_base`
(211 apparent columns against 120 physical) and
`damBreak_MM_a2p25in_medium_closedbox` (329 × 72 against 300 × 40, its `C`
field having been written at 6 significant figures rather than the R1 ladder's
8). On those the contract raised rather than integrating over columns that do
not exist, which is the correct behaviour of a fail-loud instrument and is how
the defect was found.

**6 dp closed every tracked case.** Re-grading the whole ladder at 6 dp against
8 dp moved **no verdict and no number** — it only made `res8_base` and the
original gate case readable. Re-pinning is therefore a **v1.1 under §2.6**,
recorded here with its reason and its full re-grade, and **not taken by this
amendment**: the spec's owner is the spec, and a re-pin that changes nothing
is not urgent enough to justify an unauthorised edit to a frozen normative
clause. Docket **G1c** carries it.

### 6.5 The re-gate, taken under the executable contract

Every tracked case, zero compute, tracked fields only, at `86704ddf`:

| case | dx | dy | 6-station mean | 6-station max\|d\| | verdict |
|---|---|---|---|---|---|
| `res32y128_base` | a/32 | a/128 | +8.25% | **11.03%** | **FAIL** |
| `res64y128_base` | a/64 | a/128 | +9.26% | **12.23%** | **FAIL** |
| `res32y128_slip` | a/32 | a/128 | +13.65% | **19.12%** | **FAIL** |
| `res32y256_base` | a/32 | a/256 | +10.78% | 18.08% | UNGRADEABLE (§2.2 spread 14.97% of Z at T = 3.90) |
| `res64_base` | a/64 | a/64 | +11.09% | 14.92% | UNGRADEABLE (§2.5 floor) |
| `res32y64_base` | a/32 | a/64 | +9.75% | 13.11% | UNGRADEABLE (§2.5 floor) |
| `res32_base` | a/32 | a/32 | +11.60% | 16.54% | UNGRADEABLE (§2.5 floor) |
| `res20_base` | a/20 | a/20 | +12.96% | 19.56% | UNGRADEABLE (§2.5 floor) |
| `res16_base` | a/16 | a/16 | +13.46% | 20.62% | UNGRADEABLE (§2.5 floor) |
| `res16_papermodel` | a/16 | a/16 | +20.17% | 29.41% | UNGRADEABLE (§2.5 floor) |
| `res16_slip` / `_sigma0` / `_calpha0` / `_alphaco` | a/16 | a/16 | +15.56 / +16.57 / +16.79 / +15.06% | 23.03 / 25.36 / 21.91 / 22.62% | UNGRADEABLE (§2.5 floor) |
| `res8_base` | a/8 | a/8 | — | — | §2.1 FAIL LOUD at 8 dp; +12.42% / 18.69% at 6 dp, UNGRADEABLE (§2.5 floor) |
| `damBreak_..._medium_closedbox` | a/20 | a/20 | +13.12% | 19.81% | §2.1 FAIL LOUD at 8 dp; UNGRADEABLE at 6 dp (§2.3.4 ΔT = 0.655, §2.5 floor) |

**Three cases satisfied §2.5's verdict floor. All three FAILED**, at 11.03%,
12.23% and 19.12% against the declared 5%. §3's verdict was re-derived
independently and reproduced to 0.01 percentage points at every graded station.

### **GATE (a): FAIL — unchanged, and now executable rather than asserted.**

The §3 numbers stood. What changed was that the definition behind them stopped
being prose that the code could quietly disagree with, and that the readings
prior to §3 were struck as non-comparable rather than carried as a trend.

---

## 7. Addendum, 2026-08-23 — R0 executed: the comparator's front definition, recovered as far as it can be

**Dated addendum appended at the foot. Lines whose number changed above this
section: 0.** Nothing in §§1–6 was edited. This addendum alters no gate, no
threshold, no cap, no station set, no axis and no label, and §2.6 is not
invoked. **Spec version unchanged at v1.0**: §2 is untouched, and an addendum
that records a diagnostic outcome is not a new version of the contract.

**Cost: 0 core-min.** No solver, no mesh generation, no new field. Literature
retrieval plus a reader over already-written, git-tracked fields — the same
class of work as the §1 exhibit.

### 7.1 The item, in its own words

`F7a_REGATE_PREREGISTRATION.md` §5, row **R0**, verbatim:

> *Comparator front-definition recovery* — read arXiv:2108.08769 and its
> references for the extraction method behind the Fig. 7 simulation curve; if
> unstated, contact-free bound it by re-deriving their curve's implied threshold
> from our own field data

priced at **0** core-min and recommended **BUY — Highest information per unit
cost in the whole brief**. §4 of this spec ranked it above the two solver items:
*"Item 3 outranks items 1 and 2 and should be executed before either is
bought."* This addendum discharges it.

### 7.2 First half — the paper does not state the method. Searched, not assumed.

The preprint was retrieved and filed at
`docs/papers/benchmark_test_cases/leakey_glenis_hewett_arxiv2021_variable_density_riemann.pdf`,
with its `.txt` sidecar carrying a title-page verification per L-144: page 1 was
rendered and read, giving *Riemann solvers and pressure gradients in
Godunov-type schemes for variable density incompressible flows*, Shannon Leakey,
Vassilis Glenis, Caspar J.M. Hewett, Newcastle University, arXiv:2108.08769v1,
19 Aug 2021. It is the paper this campaign has been citing. The retrieved
artifact is the **arXiv v1 preprint**; the CMAME 393:114763 (2022) version of
record was not retrieved and nothing here has been checked against it.

All 36 pages were searched. **The paper states no front-extraction method.** The
only sentence in the document that touches how the plotted quantity was obtained
is §3.3.2:

> *"Figure 7 shows the post-processed results, where the column height and surge
> front position have been normalised by dividing by a, and the time multiplied
> by √(g/a)."*

That is a normalisation, not a definition. There is no threshold, no contour
level, no cell row, no interpolation rule, and no statement of which feature of
the density field is called "the surge front position". R1 §6's open item — *"the
reference simulation's own front definition is not stated in its text"* — is
**confirmed against the full text**, not merely against a paraphrase.

Four things the paper *does* supply that were not previously on this record, and
that bear on the question:

1. **They deliberately decline a contour.** §3.3.2: *"These snapshots explicitly
   show the density field, rather than a contour to represent the free surface as
   in [13, 14], meaning that the numerical diffusion is not hidden. Indeed, the
   transition between water and air straddles several cells, and there is much
   diffusion towards the end of the simulation when the surge front hits the far
   wall."* They are explicit that their front is **smeared over several cells and
   smears further with time**. This is the mechanism by which a front definition
   can be worth a great deal on their mesh, stated by the authors themselves.
2. **Their numerical parameters**, §3.3.2, none previously recorded here: two
   pseudo-time Runge–Kutta stages, artificial-compressibility coefficient
   β = 1100, convergence tolerances 0.01 on ρ, ρu, ρv and p, pseudo-time and
   real-time Courant numbers both 0.45, minmod slope limiter on density and
   velocity.
3. **Fig. 7's layout is confirmed**, by rendering p. 30: **left column is
   a = 2¼ in** (right is a = 4½ in), **top row is column height, bottom row is
   surge front position**. The panel this lab digitised is the correct one.
4. **The three scheme variants collapse.** Fig. 7 plots Bassi split-pressure
   superbee, Osher split-pressure superbee and Bassi incompressible-limit
   pressure, and the text says *"The Riemann solver and pressure gradient
   calculation do not have much of an effect on the results."* So the digitised
   curve is not sensitive to which variant was picked off the figure, and the
   offset below cannot be blamed on that choice.

**On the first half, R0 comes back empty**: the definition cannot be recovered
from the paper. The pre-registration anticipated exactly this and named the
fallback, which is executed next.

### 7.3 Second half — the implied definition, backed out of our own tracked fields

**Instrument:** `verification/runs/F7_runs/r0_implied_front_definition.py`,
NOT-NORMATIVE and taking no verdict. **Output:**
`verification/runs/F7_runs/F7a_R1/r0_implied_front_definition.json`. **Case:**
`F7a_R1/res16_papermodel` — the comparator's physics, mesh and domain, the case
§3.1 built its finding on. Column grouping at **6 dp**, not §2.1's 8, because
§6.4 measured that 8 dp does not close the a/16 family at all; docket **G1c**
carries that re-pin, and §6.4 records that 6 dp moves no verdict and no number.

**Positive control, run before any back-out and refused-on-failure** (rule 3's
principle: a reader not shown able to see the answer is not evidence). The
script first re-derives §3.1's published `res16_papermodel` front under the §2
definition. It reproduces all six published values — 7.104, 8.157, 9.388,
10.714, 12.029, 14.235 — to **≤ 0.0004 in Z**. The reader is therefore known to
be seeing the field before it is asked about a number the repo does not hold.

**The test, stated so it cannot be gamed.** A front definition is *one fixed
rule*; it cannot be re-chosen per station. So the question is not "does some
definition fit station k" — at a/16 the readings span tens of points and
something always fits — but **"is the implied definition the same at all six
stations?"**

**The implied definition is not constant. It drifts monotonically:**

| T | Z_expt | Z_ours (§2, h\*=0.02a) | Z_comparator | gap in Z | gap % | gap in *their* cells | implied h\*/a | implied floor-row α |
|---|---|---|---|---|---|---|---|---|
| 3.90 | 6.00 | 7.104 | 5.793 | 1.311 | +22.6% | 21.0 | 0.0650 | 0.785 |
| 4.49 | 7.00 | 8.157 | 6.697 | 1.459 | +21.8% | 23.3 | 0.0575 | 0.730 |
| 5.17 | 8.00 | 9.388 | 7.667 | 1.721 | +22.4% | 27.5 | 0.0525 | 0.690 |
| 5.91 | 9.00 | 10.714 | 8.729 | 1.985 | +22.7% | 31.8 | 0.0475 | 0.645 |
| 6.70 | 10.00 | 12.029 | 9.753 | 2.276 | +23.3% | 36.4 | 0.0425 | 0.615 |
| 7.72 | 11.00 | 14.235 | 11.186 | 3.048 | +27.3% | 48.8 | 0.0400 | 0.565 |
| | | | | | **mean +23.36%** | | **0.065 → 0.040** | **0.785 → 0.565** |

The re-derived mean offset, **+23.36%**, reproduces §3.1's recorded **+23.3%**
to 0.1 percentage point, by an independently written reader interpolating the
dense digitised series rather than reading §3.1's table. That is the second
control.

**What a single fixed definition achieves** — deviation of our front from the
comparator's curve, all six graded stations, under one rule:

| single fixed definition | mean | max\|d\| | station spread |
|---|---|---|---|
| **h\* = 0.02a — this spec's own pinned rule** | **+23.36%** | 27.25% | 5.46 pts |
| h\* = 0.03a | +17.67% | 19.39% | 2.71 pts |
| h\* = 0.04a | +6.21% | 13.00% | 13.96 pts |
| h\* = 0.05a | −1.59% | 10.37% | 18.08 pts |
| h\* = 0.0625a (one full floor cell) | −11.08% | 21.33% | 22.03 pts |
| α = 0.50 contour on the floor row (no tuning) | +10.44% | 13.57% | 8.61 pts |
| α = 0.60 contour on the floor row | +3.98% | 9.38% | 12.20 pts |
| **α = 0.65 contour on the floor row — best found** | **+0.70%** | **7.31%** | 14.04 pts |
| α = 0.70 contour on the floor row | −2.92% | 10.89% | 15.86 pts |
| α = 0.50 contour one row up | −28.65% | 36.20% | 14.67 pts (4 stations only) |

**Mechanism, so this is not left as a coincidence.** At a/16 the surge is a long
shallow sheet: h(x) declines gradually over a hundred-plus columns, so the front
level is a lever with enormous mechanical advantage. Moving h\* by *one cell's
worth of water* — 0.02a → 0.0625a — moves the six-station mean by **34.4
points**, roughly 32–48 of the comparator's own cells. This is the same
resolution-dependence §1.4 measured on the *old* definition (48.0 points of
spread at a/16, collapsing to 0.4 at a/64); §1.4's finding now has a second,
independent instance against a simulation curve rather than against the
experiment.

### 7.4 THE ANSWER: R0 explains most of the offset — essentially all of its mean, and none of its shape

**R0 EXPLAINS PART OF THE 23.3% CODE-TO-CODE OFFSET. The arithmetic closes on
the mean and does not close on the shape.**

- Under this spec's pinned definition the offset is **+23.36%** mean.
- Under **one** ordinary fixed definition — a α = 0.65 contour on the
  floor-adjacent row, a garden-variety smeared-interface rule requiring no
  special pleading — it is **+0.70%** mean.
- The front definition therefore accounts for **22.7 of the 23.4 percentage
  points**, about **97% of the mean offset**. Even the wholly untuned α = 0.50
  contour takes it from +23.4% to +10.4%.
- **What does not close:** no definition in the sweep removes the
  station-to-station tilt. The best-mean candidate still runs **+7.3% at
  T = 3.90 to −6.7% at T = 7.72**, a 14.0-point spread, and the smallest max\|d\|
  any candidate achieves is **7.31%**. Under a common definition our front
  starts ahead of the comparator's and ends behind it — a difference in the
  *shape* of Z(T), not an offset in it.

So the honest sentence is: **the "~23% code-to-code gap that is not viscosity,
not surface tension, not interface compression, not mesh, and not domain"
recorded in §3.1 was, to ~97% of its mean, the front definition — the one
remaining unmatched item §3.1 itself named. What survives it is a
definition-independent code-to-code difference of order ±7% in Z at a/16.**

**Six limitations, stated rather than smuggled past:**

1. **This is a back-out, not a recovery.** It establishes which definition,
   applied to *our* field, lands on *their* curve. It does not establish what
   they did to theirs. Their density field is smeared by a Godunov-type scheme
   with **no** interface-compression term; an α level on our MULES/PIMPLE field
   is not their ρ level on theirs. The identification remains open, and only the
   authors' own post-processing could close it — which rule 7 forbids seeking.
2. **The comparator curve is a digitisation of a rendered figure** (§2.4's
   standing limitation, unchanged). Interpolating the dense digitised series at
   the six reference T gives values differing from §3.1's tabulated comparator
   column by up to **0.093 in Z** (at T = 6.70); the mean offset agrees to
   0.1 point, so no conclusion here turns on it.
3. **One case, one mesh, a/16** — below §2.5's a/32 no-verdict floor. Nothing in
   §7 is a verdict and §7 takes none.
4. `--inviscid` sets ν = 1e-12 rather than solving genuinely inviscid equations;
   §3.1's own caveat, unchanged.
5. The candidate list is a sweep over two definition families (depth-integral
   level, floor-row α level) plus row index. A definition outside those families
   was not tested and could do better or worse.
6. The retrieved paper is the arXiv **v1 preprint**; the CMAME version of record
   was not read.

### 7.5 The gate is untouched, and that is not a formality

**GATE (a): FAIL — unchanged, at max deviation +11.03% at T = 7.72 against the
declared 5% tolerance, on `res32y128_base`.** §7 moves nothing about it, and
this is a substantive statement, not a disclaimer:

- The gate is graded **against the Martin & Moyce experiment**, not against the
  comparator's simulation curve. §7 concerns only the code-to-code comparison in
  §3.1, which never decided the gate.
- The gate is taken at **dy = a/128**. §7 is an a/16 diagnostic, and §1.4 already
  measured the definition spread collapsing from 78.2 points at a/8 to **1.7 at
  a/32 and 0.4 at a/64**. The definition lever §7 measures is a coarse-mesh
  lever; at the verdict mesh it is worth well under a point.
- §1.6's row stands verbatim: *"The ambiguity explains the gate's residual +8.2%
  failure — **REFUTED.** At dy ≤ a/32 every reading lands +7.8% to +11.9%, all
  FAIL."* §7 is fully consistent with it. A definition that is worth 23 points at
  a/16 and 0.4 points at a/64 explains a code-to-code comparison on a coarse mesh
  and explains nothing about a verdict taken on a fine one.
- §2.6 is not invoked; no threshold, station set, axis or mesh was changed.

### 7.6 What this does to the compute argument — recorded, not decided

§4 and prereg §2 both rest on a premise that §7 has now moved, and the record
should say so plainly rather than let the old sentence circulate:

- §4's ranking — *"Item 3 outranks items 1 and 2 and should be executed before
  either is bought"* — was **correct**, and is now **discharged** at the 0
  core-min it was priced at.
- §4's *reason*, that *"the unexplained 23% lies in the comparison basis"*, is
  confirmed in direction and **superseded in magnitude**. It does lie in the
  comparison basis; it was the front definition; it is now ~97% accounted for.
- Prereg **P5** — *"Any run in this list changes the deviation by less than the
  **23.3%** code-to-code offset already measured"* — was written against a
  number that no longer stands as an unexplained offset. Read against what
  survives, the bar is **≈ 7%**, not 23.3%. That is a materially weaker bar and
  P5 is correspondingly easier to falsify. P5 is **not** rewritten here (rule 2:
  after first compute, originals are struck, never rewritten) — it is recorded as
  **struck in its stated magnitude and kept as a reading**, per L-76.
- **This addendum does not authorise buying R1a, R1b or R1c**, and does not
  recommend it either way. The premise that argued against them has weakened;
  whether that changes the purchase is a campaign call above this addendum, and
  the caps in prereg §4 are unchanged.

### 7.7 Sources for §7

- `docs/papers/benchmark_test_cases/leakey_glenis_hewett_arxiv2021_variable_density_riemann.pdf`
  and its `.txt` sidecar — the paper, retrieved 2026-08-23, title-page verified
  per L-144. Retrieval only; nothing left this box (rules 7, 8).
- `verification/runs/F7_runs/r0_implied_front_definition.py` — the §7.3
  instrument, NOT-NORMATIVE, with its positive control and its 6 dp grouping
  disclosed in its own header.
- `verification/runs/F7_runs/F7a_R1/r0_implied_front_definition.json` — every
  number in §7.3, as written by that instrument.
- `verification/runs/F7_runs/F7a_R1/res16_papermodel` — tracked fields, read, not
  regenerated.
- `verification/runs/F7_runs/fig7_digitised_R1.json` — the comparator curve, R1's
  second digitisation, unchanged.

---

## 8. Addendum, 2026-08-24 — the R0 toe-width diagnostic is mislabelled in its own output; the threshold is 0.95·h_max, not 0.995·h_max

**Spec version unchanged at v1.0.** §2 is untouched; no gate, threshold, station
set, cap or label moves. This addendum follows the same reasoning §7 recorded at
lines 652–653 — an addendum that records a diagnostic outcome is not a new
version of the contract — and it is stated here rather than left implicit
because standing rule 6 asks for a version bump: the bump is declined on the
§7 precedent, and the decline is disclosed rather than silent. This addendum is
itself **ADDENDUM §8 v1.0**.

**lines whose number changed above this section: 0**

### 8.1 The defect

`verification/runs/F7_runs/r0_implied_front_definition.py`, at HEAD
`290fcff2`, computes the upstream end of the toe-width diagnostic at

    line 346:  x95 = cross_down(xs, rec["h"], 0.95 * max(rec["h"]))

— a crossing of **0.95 × h_max**. It then stores that crossing under the key
`x_h995_over_a` (line 350) and prints it as

    line 400:  "T=%.2f toe from h=0.995*hmax to h=0.005a spans %s cells"

Both the key and the printed sentence say **0.995 × h_max**. The code says
**0.95 × h_max**. The code is what ran; the label is wrong.

**The true window is therefore h = 0.95·h_max down to h = 0.005·a**, not
0.995·h_max down to 0.005·a. Every cell count written under `toe_width` is the
width of the **0.95 – 0.005a** window.

### 8.2 What carries the wrong label, and what does not

- **No prose in this spec quotes a toe-width figure.** §7.3, §7.4, §7.5 and
  §7.6 contain no cell count from `toe_width` and no "0.995" anywhere. The
  string "0.995" does not occur in this file.
- **The committed JSON does carry it.**
  `verification/runs/F7_runs/F7a_R1/r0_implied_front_definition.json` is
  git-tracked and holds the `toe_width` block at lines 124–167, with the
  mislabelled key `x_h995_over_a` on lines 128, 135, 142, 149, 156 and 163.
- **That JSON is cited by this spec**, at §7.7 line 894–895, as *"every number
  in §7.3, as written by that instrument"* — a blanket artifact citation. A
  reader following it reaches the wrong label. That citation path, not any
  quoted prose figure, is why this addendum exists.

For the record, the affected figures as written, now correctly attributed to the
**0.95·h_max → 0.005a** window on `F7a_R1/res16_papermodel` (dx = dy = a/16):

| T | t used | x(h=0.95·h_max)/a | x(h=0.005a)/a | span, cells |
|---|---|---|---|---|
| 3.90 | 0.30 | 0.7361 | 7.6942 | 111.3 |
| 4.49 | 0.35 | 1.2311 | 8.9748 | 123.9 |
| 5.17 | 0.40 | 1.5654 | 10.2428 | 138.8 |
| 5.91 | 0.45 | 2.0069 | 11.4857 | 151.7 |
| 6.70 | 0.50 | 2.3958 | 12.7203 | 165.2 |
| 7.72 | 0.60 | 3.2880 | null | null |

The T = 7.72 row has no downstream 0.005a crossing and its span is `null` in
the JSON; it is carried here as null and not as a number.

### 8.3 No §7 headline number depends on it

`toe_width` is computed in an isolated block (script lines 342–354), attached
to the result dict at line 377, and printed at lines 399–401. Nothing in
`stations` or in `fixed_definition_sweep` reads `x95` or `x005`. In
particular the §7.3 / §7.4 headline chain is untouched:

- the **+23.36%** six-station mean under this spec's pinned h\* = 0.02a;
- its collapse to **+0.70%** mean under the α = 0.65 floor-row contour;
- the **±7.3%** surviving residual (max|d| = 7.31%, station spread 14.04 pts);
- the "~97% of the mean offset" statement in §7.4.

None of these is a function of the toe-width window. **GATE (a): FAIL —
unchanged**, at max deviation +11.03% at T = 7.72 on `res32y128_base`; §8 moves
nothing about it, exactly as §7.5 recorded for §7.

### 8.4 The script is NOT edited, and that is deliberate

`r0_implied_front_definition.py` is the instrument that produced a committed
record (the JSON cited at §7.7). Editing it in place would silently change the
instrument behind an existing citation. A correction, if the campaign wants one,
is a **new script version, read as a diff by the supervisor** under the standing
measurement-script-diff check, producing a new output file — not an in-place
relabel. Until then the label defect is disclosed here and the JSON's
`x_h995_over_a` key is to be read as **x(h = 0.95·h_max)/a**.

**Scope of this addendum:** disclosure only. Zero compute. No gate, threshold,
station set, cap, label or published number is altered.
