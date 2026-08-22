# T10a-VF. Results: characterisation of the view-factor row-sum defect in `viewFactorsGen`

**Pre-registration frozen at commit `7ed70d6b88922ee6b3f3aea88e0d833a269c7f9d`**
(`T10a-VF pre-registration frozen before compute`), which contains
`docs/campaigns/T-family/T10aVF_PREREGISTRATION.md` and the five scripts, and
under which **no sweep case existed**. Every case in
`verification/runs/T-family/T10aVF_runs/cases/` was built after it.

**SUBMISSIONS PARKED.** The upstream draft
`docs/upstream/T10a_viewFactorsGen_rowsum_NOT_FILED.md` opens with
`NOT FILED — draft for Sanaa's decision`. Nothing has been sent anywhere, no
issue has been opened, no maintainer contacted. Filing is Sanaa's call alone.

Toolchain: OpenFOAM ESI **v2606**, `/usr/lib/openfoam/openfoam2606`,
`Build: _481094f-20260618`, `Arch: LSB;label=32;scalar=64`.

Verdict vocabulary: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING**.

---

## 1. Headline

The T10a outer-sphere "view-factor quadrature defect" is a **defect of the
`viewFactorsGen` utility**, not a mesh artefact, not an orientation artefact,
not an agglomeration artefact, and not the expected behaviour of a faceted
sphere. It has a single named cause, a closed-form size, and a one-key
workaround.

> `viewFactorsGen`'s 2LI branch evaluates the coincident-edge log singularity by
> substituting `r -> alpha*|s_i|`, which is exact only at
> `alpha = exp(-3/2) = 0.223130160148...`; the shipped default is `0.21`, and
> the resulting error, **`e(alpha) = -(2 ln alpha + 3)/(4 pi) = +0.0096524`,
> contains no mesh size** and is added to `F_ij` once for every mutually-visible
> edge-sharing neighbour of the emitting face.

A face on a **concave** patch sees all four of its edge neighbours, so its row
sum is wrong by `4 e(alpha) = +3.86 %` **at every resolution, forever**. A face
on a **convex or flat** patch sees none of them and is clean. This is why
T10a's outer sphere sat at 4.3–4.8 % across its whole ladder while its inner
sphere converged 0.48 -> 0.30 -> 0.11 %, and why 10x tighter `GaussQuadTol`
moved nothing: the coincident-edge term is forced to quadrature order 0
regardless of the Gauss order, so no Gauss tolerance can reach it.

**Two corrections to the T10a record**, neither of which changes any T10a
verdict:

1. **The sign.** T10a recorded `|rowSum - 1|`. The row sums are **above** 1 —
   it is an **excess**, not a deficit. This is decisive: no missing-visibility
   or over-shadowing explanation can raise a row sum.
2. **The box row sums do not converge either.** T10a's box patch *means*
   (0.41 -> 0.25 -> 0.15 %) fall like `O(h)`, but only because the affected
   faces are the one-dimensional set lying along the 12 box edges. The box
   patch *maxima* are pinned at **1.9285 / 1.9132 / 1.9089 %** = `2 e(0.21)`
   and do not move at all.

---

## 2. Pre-check (read-only, against the frozen T10a matrices)

Reported in full in the pre-registration §2; the numbers, for the record:

| check | result |
| --- | --- |
| T10a numbers reproduce | max `\|rowSum-1\|` outer sphere **4.77258 / 4.27405 / 4.47372 %** at c/m/f vs T10a's 4.77 / 4.27 / 4.47; inner **0.47757 / 0.30049 / 0.11455 %** vs 0.48 / 0.30 / 0.11 |
| sign | **excess**: outer mean rowSum 1.04103 / 1.04035 / 1.03962 |
| orientation / cross-patch | outer→inner block **0.250518 / 0.250478 / 0.250188** vs exact `F_21 = 0.25`; error 0.21 / 0.19 / **0.075 %**, converging |
| visibility test | an outer face sees **74.87 %** of the other outer faces vs the exact 75 % |
| agglomeration | `constant/finalAgglom` absent in every T10a case; `useAgglomeration` false |
| localisation | at `S_f`, the **4 edge-sharing entries carry 0.0428617 of the 0.0447367 row excess = 95.9 %**; the other 3064 same-patch entries are collectively right to 0.15 % |

**Pre-check verdict: PASS** — the defect is a property of `viewFactorsGen`.

---

## 3. Sweep 1 — mesh family (concentric spheres, identical settings)

`SPH`, `r1=0.05`, `r2=0.1`, `blockMesh` projected shell, `alpha=0.21`,
`GaussQuadTol=0.01`, `distTol=8`, `intTol=0.01`, no agglomeration.

| case | faces | patch | mean rowSum | max rowSum | mean excess | excess / edge-pair |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `S1_SPH_L1` | 768 | outer (concave) | 1.0340923 | 1.0407 | **+3.409 %** | 0.0085231 |
| `S1_SPH_L2` | 1728 | outer | 1.0402552 | 1.0440 | **+4.026 %** | 0.0100638 |
| `S1_SPH_L3` | 3072 | outer | 1.0403450 | 1.0427 | **+4.035 %** | 0.0100863 |
| `S1_SPH_L4` | 4800 | outer | 1.0395530 | 1.0432 | **+3.955 %** | 0.0098882 |
| `S1_SPH_L1` | 768 | inner (convex) | 0.9893824 | — | −1.062 % | n/a (`n_ev = 0`) |
| `S1_SPH_L2` | 1728 | inner | 1.0030814 | — | +0.308 % | n/a |
| `S1_SPH_L3` | 3072 | inner | 1.0019404 | — | +0.194 % | n/a |
| `S1_SPH_L4` | 4800 | inner | 1.0012772 | — | +0.128 % | n/a |

Face count spans **6.25x**, `h` down by 2.5x. Concave-patch excess
`max/min = 1.1834`, and it is **not monotone** (it rises from L1 to L3, then
falls). The convex patch on the same meshes converges as `O(h^1.6..1.9)`.

Adding T10a's own three levels (600/1536/4056 faces, a different `nr`/`N`
family) the concave excess is +4.103 / +4.035 / +3.962 % — seven independent
resolutions, all between **+3.41 % and +4.10 %**.

**VF-1: PASS** (`max/min = 1.1834 <= 1.30`; every level inside `[0.029, 0.049]`;
falsifier "monotone decrease by >2x" not observed).

**Independent confirmation from the utility itself.** With
`writeViewFactorMatrix true`, `viewFactorsGen` writes its own per-face row-sum
field to `0/viewFactorField` (`viewFactorsGen.C:1200-1243`). On `S1_SPH_L2` it
reports `inner` mean 1.0030814 (min 1.0007469, max 1.0048224) and `outer` mean
**1.0402552** (min 1.0368391, max 1.0440224) — **identical to the analysis
above to every digit**. Nothing in this arm's arithmetic is needed to see the
defect: the utility prints it. (`writeViewFactorMatrix` gates only this
diagnostic field; `constant/F` is written unconditionally at line 1172, so the
key does not affect the matrix.)

**VF-2: PASS.** Using the `alpha = exp(-3/2)` twin of each mesh as the corrected
value on the *same* matrix entries, the edge-sharing entries carry

| case | patch | mean excess | `dF` on edge pairs | fraction carried |
| --- | --- | ---: | ---: | ---: |
| `S1_SPH_L1` | outer | 0.0340923 | 0.0393054 | 115.3 % |
| `S1_SPH_L2` | outer | 0.0402552 | 0.0392608 | 97.5 % |
| `S1_SPH_L3` | outer | 0.0403450 | 0.0392558 | 97.3 % |
| **`S1_SPH_L4` (finest, the registered gate)** | outer | 0.0395530 | 0.0392466 | **99.2 %** |
| `S2_BALL_f` | outer | 0.0405625 | 0.0392558 | 96.8 % |
| `S2_CYL_f` | side | 0.0275338 | 0.0265137 | 96.3 % |

Note that `dF` on the edge pairs is **0.03925 ± 0.00003 across the whole mesh
family** — a constant to four digits while the face count changes 6.25-fold.
That is the clearest single statement of the defect in this document.

**VF-3: GATE FAIL** (second limb). First limb passes: `E/n_ev` for every
concave patch of Sweeps 1–2 lies in `[0.0085, 0.0130]`, inside the registered
`[0.0080, 0.0130]`. Second limb fails: the spread across the `SPH` family is
`0.0100863/0.0085231 = 1.1834`, i.e. **18.3 % against a registered ceiling of
15 %**. The whole of the spread is the coarsest level `L1` (`N=8`), whose
convex control patch is also anomalous (−1.06 %, against +0.13..+0.31 % at every
other level) — at `N=8` the sphere's faceting and shadow-boundary errors are
themselves percent-level and are not separable from the quantity being
measured. Excluding `L1`, the spread is **2.0 %**. *That exclusion is stated as
a diagnosis and is not used to change the verdict: the registered threshold was
set over the whole family and the whole family missed it.*

---

## 4. Sweep 2 — geometry and convexity

`alpha = 0.21` throughout. `n_ev` = patch-mean number of edge-sharing
neighbours that are also in the emitter's own visibility list.

| case | faces | patch | character | `n_ev` | mean rowSum | mean excess | max excess |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| `S2_BOX_c` | 384 | all 6 walls | flat, convex | 0.500 | 1.0072588 | +0.726 % | **+1.987 %** |
| `S2_BOX_f` | 1536 | all 6 walls | flat, convex | 0.250 | 1.0037553 | +0.376 % | **+1.923 %** |
| `S2_SHELL_c` | 768 | outer | flat, convex | 0.500 | 0.9999481 | −0.005 % | +3.287 % |
| `S2_SHELL_c` | 768 | inner | flat, convex | 0.000 | 0.9969035 | −0.310 % | −0.257 % |
| `S2_SHELL_f` | 3072 | outer | flat, convex | 0.250 | 1.0061958 | +0.620 % | +2.926 % |
| `S2_SHELL_f` | 3072 | inner | flat, convex | 0.000 | 1.0023152 | +0.232 % | +0.403 % |
| `S2_CYL_c` | 384 | side | **concave in 1 direction** | 2.336 | 1.0303025 | **+3.030 %** | +4.167 % |
| `S2_CYL_f` | 1536 | side | **concave in 1 direction** | 2.254 | 1.0275338 | **+2.753 %** | +4.137 % |
| `S2_CYL_c` | 384 | ends | flat | 0.609 | 1.0099732 | +0.997 % | +3.908 % |
| `S2_CYL_f` | 1536 | ends | flat | 0.250 | 1.0047810 | +0.478 % | +3.373 % |
| `S2_BALL_c` | 384 | outer | **fully concave** | 4.000 | 1.0439484 | **+4.395 %** | +4.606 % |
| `S2_BALL_f` | 1536 | outer | **fully concave** | 4.000 | 1.0405625 | **+4.056 %** | +4.386 % |
| `S1_SPH_*` | 768–4800 | outer | **concave** | 4.000 | see §3 | **+3.41..+4.03 %** | +4.40 % |
| `S1_SPH_*` | 768–4800 | inner | convex | 0.000 | see §3 | +0.13..+0.31 % (`L1` −1.06 %) | — |

Read the `n_ev` column against the excess column. It is the whole mechanism:

* `n_ev = 4` (fully concave, curved) -> **+3.9 to +4.4 %**, at every resolution.
* `n_ev ≈ 2.3` (cylinder side wall: concave circumferentially, **flat
  axially**) -> **+2.8 to +3.0 %**. This was the sharpest registered
  prediction in the arm — a curved concave patch that is concave in one
  direction only must show roughly **half** the sphere's defect, and it does.
  Nothing about "curvature" or "concavity" as such predicts that; only edge
  counting does.
* `n_ev -> 0` as `h -> 0` (flat/convex patches, where only faces along a
  geometric edge of the enclosure have a visible edge neighbour) -> patch means
  fall like `O(h)` while the patch **maxima stay pinned** at `1 or 2 e(alpha)`.
  `S2_BOX` max: **1.9868 % -> 1.9234 %** for a 4x face count; T10a's box:
  **1.9285 / 1.9132 / 1.9089 %** for a 6.9x face count. `2 e(0.21) = 1.9305 %`.

**VF-4: GATE FAIL.** 28 of 32 patch-rows satisfy
`|E - n_ev*e(0.21)| <= 0.30|E| + 0.002`. Four do not: `S1_SPH_L1 inner`
(|d| = 0.0106 vs tol 0.0052), `S1_SPH_L2 inner` (0.00308 vs 0.00292),
`S2_SHELL_c inner` (0.00310 vs 0.00293), `S2_SHELL_c outer` (0.00488 vs
0.00202). **All four are patches whose predicted excess is ~0**, i.e. the
registered tolerance asked a near-zero prediction to be met to within 0.002
absolute while the *alpha-independent* background — ordinary faceting and
quadrature error, which T10a separately measured at −0.538 % on the coarse
sphere — is several times that at coarse resolution. The threshold was
mis-specified: it carried no faceting allowance. Every failing row is a
convex/flat patch, and every one of them is **bit-identical between the
`alpha=0.21` case and its `alpha=exp(-3/2)` twin**, so none of the failure is
this defect. The verdict stands as registered.

Second limb of VF-4 (convex means fall `>= 1.6x` per mesh doubling): the `SPH`
family is not a doubling family (`N` 12->16->20), and over those steps the
convex mean falls 1.588x and 1.519x, i.e. `O(h^1.61)` and `O(h^1.87)`. The
criterion is **ambiguous as registered** for a non-doubling family and is
recorded as such rather than scored.

---

## 5. Sweep 3 — generator knobs (fixed mesh, `SPH` `L2`, 1728 faces)

### 5.1 `alpha` — the lever

| `alpha` | mean rowSum, outer | `E/n_ev` measured | `e(alpha)` predicted | `\|diff\|` | tol | |
| ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 0.10 | **1.5212611** | +0.1303153 | +0.1277354 | 0.00258 | 0.02855 | PASS |
| 0.15 | **1.2586230** | +0.0646557 | +0.0632036 | 0.00145 | 0.01564 | PASS |
| 0.20 | 1.0718490 | +0.0179623 | +0.0174176 | 0.00054 | 0.00648 | PASS |
| **0.21 (shipped default)** | **1.0402552** | +0.0100638 | +0.0096524 | 0.00041 | 0.00493 | PASS |
| 0.22 (value in the source header) | 1.0101421 | +0.0025355 | +0.0022485 | 0.00029 | 0.00345 | PASS |
| **`exp(-3/2)` = 0.223130** | **1.0009944** | +0.0002486 | 0 | 0.00025 | 0.00300 | PASS |
| 0.25 | **0.9273640** | −0.0181590 | −0.0180968 | 0.00006 | 0.00662 | PASS |
| 0.30 | **0.8094318** | −0.0476420 | −0.0471142 | 0.00053 | 0.01242 | PASS |

A **71 percentage-point swing** in a quantity that is exactly 1 by definition,
driven by one dictionary key, tracking a closed form derived from the source
to within 3 % over the whole range. Zero crossing by linear interpolation:
**`alpha_0 = 0.223493`** against `exp(-3/2) = 0.223130` — a difference of
**3.6e-4**, registered tolerance 5e-3.

**VF-5: PASS.**

### 5.2 `GaussQuadTol`, `intTol`

| knob | value | mean rowSum, outer | move vs default |
| --- | ---: | ---: | ---: |
| `GaussQuadTol` | 0.01 (default) | 1.0402552 | — |
| `GaussQuadTol` | 0.001 | 1.0402632 | **+0.0008 pp** |
| `GaussQuadTol` | 1e-6 | 1.0402632 | **+0.0008 pp** |
| `intTol` | 0.01 (default) | 1.0402552 | — |
| `intTol` | 1e-4 | **0.8342475** | **−20.6 pp** |

`GaussQuadTol` is **structurally inert**, exactly as the mechanism requires: the
coincident-edge term is forced to quadrature order 0 whatever the outer Gauss
order, so no tightening can reach it. A 10 000x tightening moves the concave
row sum by 8e-6 absolute. (T10a's `_q` twins measured this as "≤0.006 %"; it is
0.0008 %.)

`intTol` **is not an integration tolerance at all** — the pre-registration's
table entry for it was wrong, and this sweep corrected it.
`shootRays_CGAL.H:58,61` uses it as the fractional **shrink applied to each end
of the visibility ray**, to stop the ray hitting its own endpoint faces. At
`intTol = 1e-4` the shrink is too small, rays are blocked by their own source
and target, and **648 of 1728 faces come back seeing nothing at all**
(`0()` rows in `globalFaceFaces`); the inner-patch mean row sum collapses to
0.1614. This is a second, separate fragility of the same utility. It is
**reported, not claimed**, and it is noted in the upstream draft as a remark.

**VF-7: GATE FAIL** on the `intTol` limb (20.6 pp against a registered ceiling
of 0.05 pp); **the `GaussQuadTol` limb passes** with 0.0008 pp.

### 5.3 `distTol`

| `distTol` | mean rowSum, outer | mean excess |
| ---: | ---: | ---: |
| 1 | **1.0012815** | **+0.128 %** |
| 4 | 1.0403902 | +4.039 % |
| **8 (default)** | 1.0402552 | +4.026 % |
| 100 | 1.0373161 | +3.732 % |

`distTol` is the "far" threshold in equivalent radii: above it a pair is
integrated by the one-point 2AI double-area rule, below it by 2LI. Two
edge-sharing square faces sit at `dist = 2/sqrt(pi) = 1.128`. Setting
`distTol = 1` therefore pushes the edge-sharing pairs out of the 2LI branch
and **the defect vanishes** (+4.03 % -> +0.13 %), which both confirms the
mechanism and gives a second one-key workaround — though at the price of using
the crude 2AI rule for *all* near pairs, which is not recommended.

**VF-8: PASS** (`distTol=1` gives `E = 0.00128 <= 0.005`; `distTol` 4 and 100
sit 0.013 pp and 0.294 pp from the default, inside the registered 0.3 pp).

### 5.4 Agglomeration — VF-9, REPORTED ONLY, no gate

`patchAgglomeration { viewFactorWall { nFacesInCoarsestLevel 10; featureAngle
10; } }` via `faceAgglomerate` collapsed the 1728-face `SPH` `L2` mesh to
**15 coarse faces**. Row sums then range from 0.87 mean to +17.7 % max — an
agglomeration error far larger than the defect under study. The
`alpha = exp(-3/2)` twin is **bit-identical** (`cmp constant/F` reports no
difference), i.e. at that coarsening no two coarse faces share a coincident
edge and the `alpha` term is never exercised. **This neither confirms nor
excludes the defect under agglomeration**; the registered agglomeration level
was far too aggressive to be informative, and a useful agglomeration sweep
(`nFacesInCoarsestLevel` in the hundreds) was not run. Recorded as a gap.

---

## 6. Reproducer — VF-10: PASS

`verification/runs/T-family/T10aVF_runs/reproducer/` — four cases
(`box`, `box_alphafix`, `sphere`, `sphere_alphafix`), `blockMesh` only, five
small text files each, an `Allrun`, a stdlib-only `rowsum.py`, and a `README.md`
carrying the expected table. **No snappyHexMesh, no solver, no solution
time directory** (each case's `0/` holds only the `viewFactorField` the utility
itself writes).

**Three** independent runs from clean printed the expected table to the last
digit shown — **16.1 s wall / 87 % of one core**, **39.1 s / 39 %**, and
**19.2 s / 74 %**, differing only in how busy the shared box was; about 14–15
core-seconds every time, against the registered ceiling of 120 s. The third run
was made after stripping the directory back to its shipped state, which is
**172 KB of 22 text files** — no mesh, no matrix, no time directory.

Its two load-bearing numbers: `box` max rowSum **1.019234** (= `1 + 2 e(0.21)`,
on exact cube geometry with no curvature and no faceting error at all), and
`sphere` `outer` mean **1.040255** (= `1 + 4 e(0.21)`).

---

## 7. Verdicts against §4 of the pre-registration

| gate | what it tested | verdict |
| --- | --- | --- |
| **VF-1** | concave-patch excess does not converge over a 6.25x face-count range | **PASS** (`max/min = 1.1834 <= 1.30`, non-monotone) |
| **VF-2** | the excess lives on the edge-sharing entries | **PASS** (99.2 % at the finest level; `dF` constant to 4 digits across the family) |
| **VF-3** | per-pair excess is a constant of `alpha`, not of `h` | **GATE FAIL** — interval limb passes, spread limb 18.3 % vs registered 15 %, entirely from the coarsest level |
| **VF-4** | `E ≈ n_ev * e(alpha)` patch by patch | **GATE FAIL** — 28/32 rows inside; the 4 failures are all near-zero-prediction convex patches where the registered tolerance carried no faceting allowance |
| **VF-5** | `alpha` is the lever and the law is `e(alpha)` | **PASS** (8/8 points; zero crossing 0.223493 vs 0.223130) |
| **VF-6** | `alpha = exp(-3/2)` removes it on every geometry | **GATE FAIL** — 17/20 patch means inside `\|E\| <= 0.005`; the 3 outside are `S1_SPH_L1_afix` inner/outer (coarsest mesh) and `S3_agglom_10_afix` (15 coarse faces) |
| **VF-7** | `GaussQuadTol` and `intTol` cannot reach the term | **GATE FAIL** — `GaussQuadTol` limb passes at 0.0008 pp; `intTol` limb fails at 20.6 pp because `intTol` is a ray-shrink epsilon, not a quadrature tolerance |
| **VF-8** | `distTol` below the adjacency ratio removes it | **PASS** |
| **VF-9** | agglomeration | **REPORTED ONLY** — level chosen was too aggressive to be informative; recorded as a gap |
| **VF-10** | reproducer runs from clean inside 120 s and matches | **PASS** (two runs, 16.1 s and 39.1 s) |

**5 PASS, 4 GATE FAIL, 1 REPORTED ONLY.** Every one of the four GATE FAILs is a
threshold this lane set too tightly against the *alpha-independent* background
error — none of them is evidence against the mechanism, and none of them is
repaired here by moving a threshold. In particular: not one measured number
contradicts `E = n_ev * e(alpha)`; the failures are all cases where a
registered tolerance demanded that a *different*, already-known, converging
error also be small.

---

## 8. Classification

| candidate classification | verdict |
| --- | --- |
| **utility defect** (`viewFactorsGen`, 2LI coincident-edge regularisation) | **THIS ONE.** The row-sum identity is exact for closed enclosures; the violation is produced by one substitution in the utility; its size is a closed form in one dictionary key; setting that key to its analytically exact value removes it on five geometries and four resolutions |
| mesh / face-orientation artefact | **excluded** — the sign is an excess; the cross-patch block is exact to 0.075 %; the visibility fraction is 74.87 % vs an exact 75 %; the defect appears on exact cube geometry with no curvature at all |
| expected behaviour of a faceted sphere | **excluded** — a closed faceted enclosure has exactly unit row sums; the faceting deficit is a different, converging quantity (T10a: −0.538 / −0.211 / −0.080 %, `O(h^2)`); and a cube exhibits the same constant |
| agglomeration artefact | **excluded** — no agglomeration was used in T10a or in Sweeps 1–2 |
| user error in the T10a dictionaries | **excluded** — T10a wrote out the v2606 source defaults verbatim; the reproducer uses those same defaults from a clean case |

**Severity, stated conservatively.** This is a silent wrong-answer in a
preprocessing utility, on a quantity with an exact known value, whose size does
not shrink with mesh refinement, on the geometry class radiation enclosures are
usually made of. It is invisible by default because `smoothing true` in
`viewFactorCoeffs` renormalises the rows before the radiosity solve. T10a's
already-recorded consequence for a solved field is a uniform-300 K box giving
`max |qr| = 13.95 W/m^2 = 3.0 %` of `sigma T^4` where the exact answer is zero.

---

## 9. Cost — registered vs actual

| item | registered | actual |
| --- | ---: | ---: |
| `blockMesh` + `viewFactorsGen`, 34 sweep cases | 3.48 + ~2.0 core-min | **4.20 core-min** (measured, sum of per-case `STATUS wall_s`) |
| aborted first attempt (`maxDynListLength`, §10) | not registered | ~1.0 core-min |
| analysis Python (34 sweep cases + 11 T10a re-reads + pre-check) | ~12.0 core-min | ~10.1 core-min (wall-clock of the analysis jobs) |
| reproducer build + 3 runs | ~1.0 core-min | ~0.8 core-min |
| **total** | **~18.5 core-min = $0.016** | **~16.1 core-min = $0.0138** |

At $0.0513/core-h. **Arm cap 1.00 USD; actual 1.4 % of it. Nothing was cut**;
the registered cut order (`S1_SPH_L4` and twin first) was never invoked.
Concurrency held at `MAXJOBS=2` throughout, on a box whose load average was
22–27 of 16 cores from other lanes. **No solver was run in this arm.**

*Correction to the pre-registration.* §0 and §3 of the frozen pre-registration
say no case in `T10aVF_runs/` "will ever hold a time directory". Every case in
fact holds a `0/` directory containing exactly one file, `viewFactorField`,
which **`viewFactorsGen` itself writes** when `writeViewFactorMatrix true`
(`viewFactorsGen.C:1200-1243`). It is preprocessing output from the utility
under test, not a solution: no solver has ever been started in this tree and no
case holds a field a solver could have written. The claim as frozen was wrong
and is corrected here rather than in the frozen file.

---

## 10. Post-freeze amendments, disclosed

Three changes were made to frozen scripts after commit `7ed70d6b`. All three
are plumbing; none can select, alter or hide a measured number, and each is
commented in place in the file it changed.

| file | frozen sha256 | post-amendment sha256 | change and why |
| --- | --- | --- | --- |
| `run_t10avf.sh` | `7fb1b12c…f2e49f` | `f1fe3d0d…f497a` | removed `set -e` and made the OpenFOAM `bashrc` source non-fatal. The v2606 `etc/config.sh/setup:209` `pop_var_context` returns non-zero, which killed the frozen script at its first line of work. Every utility call in the script already checks its own exit status explicitly |
| `build_t10avf.py` | `a1d289be…f078a462` | `5fe4b548…918ae9f` | removed the `maxDynListLength 200000;` key, copied from the `externalSolarLoad` tutorial. It is a **resource ceiling** on the visible-pair list, far below the pair count of every case here, so `viewFactorsGen` aborted at `shootRays_CGAL.H:82` **before computing anything**. Omitting the key restores the compiled-in CGAL default of 1e9 — which is exactly what T10a used, its `viewFactorsDict` never having set the key. A ceiling is either hit (abort, no output) or not hit (unchanged output) |
| `analyse_t10avf.py` | `2e198d3f…822f80` | `c06dc4a9…83ca0e1` | taught the stream parser OpenFOAM's inline short-list form `N(v1 … vN)` / `0()`. The frozen parser **raised** on it rather than mis-reading it, on exactly two cases (the agglomerated pair and `intTol=1e-4`). Every block-form case re-parses bit-identically |

The pre-registration file itself was not touched after the freeze. Its `intTol`
description ("integration tolerance (2D/Hottel path)") is **wrong** and is
corrected in §5.2 above; it is left standing in the frozen file.

---

## 11. What this does NOT show

Restating the pre-registration's §7, plus what the sweeps added.

1. **No flux, no temperature, no heat transfer coefficient was measured.** No
   solver ran in this arm. The consequence for a solved field is quoted from
   T10a (C3b: `max |qr| = 13.95 W/m^2 = 3.0 %` of `sigma T^4`), not re-measured.
2. **T10a is not re-graded.** S0/S1 remain **NOT A RESULT** on T10a's own
   registered grounds. What changes is the *description* of the floor.
3. **No claim about `createViewFactors`.** Its 2AI is different code — it uses
   *signed* cosines where `viewFactorsGen` takes `mag()` of both, and it has no
   `alpha`. T10a's 2D `H_2d` used `createViewFactors`/Hottel and shows a row-sum
   **deficit** of 2.7–3.3 % (floor/ceiling 1.03 %, side walls 2.10 % mean),
   which is a **different phenomenon**, reported here and claimed nowhere.
4. **No patched binary was built and no fix is verified.**
   `alpha = exp(-3/2)` was applied only as a *dictionary value through the
   shipped code path*. `alpha` is additionally used for a second purpose in
   `GaussQuad` (the `mag(r) < SMALL` guard in the order>0 branch, line 411),
   which this arm did not isolate; changing `alpha` globally is therefore
   evidence about the mechanism, not a recommended fix.
5. **No claim that this is the largest error in a radiation solve**, and no
   claim that any published result is wrong.
6. **No novelty search was done.** Whether this is already known upstream —
   reported, fixed on a development branch, or discussed in the forum — has
   **not been checked**. The upstream draft says so in its own words. Candidates
   #1–#3 each carry a recorded novelty sweep; this one does not, and must not be
   filed until it does.
7. **The agglomeration question is open** (§5.4).
8. **`smoothing true` hides all of it** by row renormalisation, and is not
   graded here.

---

## 12. Deliverables and paths

| what | where |
| --- | --- |
| pre-registration (frozen, commit `7ed70d6b`) | `/home/ubuntu/Certonomous/docs/campaigns/T-family/T10aVF_PREREGISTRATION.md` |
| this file | `/home/ubuntu/Certonomous/docs/campaigns/T-family/T10aVF_RESULTS.md` |
| upstream draft, candidate #4, **NOT FILED** | `/home/ubuntu/Certonomous/docs/upstream/T10a_viewFactorsGen_rowsum_NOT_FILED.md` |
| upstream queue | `/home/ubuntu/Certonomous/docs/upstream/UPSTREAM_QUEUE.md` |
| reproducer | `/home/ubuntu/Certonomous/verification/runs/T-family/T10aVF_runs/reproducer/` |
| builder / runner / analyser | `/home/ubuntu/Certonomous/verification/runs/T-family/T10aVF_runs/{build_t10avf.py,run_t10avf.sh,analyse_t10avf.py}` |
| pre-check tools | `/home/ubuntu/Certonomous/verification/runs/T-family/T10aVF_runs/{vf_rowsum.py,vf_edge_probe.py}` |
| 34 sweep cases | `/home/ubuntu/Certonomous/verification/runs/T-family/T10aVF_runs/cases/` |
| machine-readable results | `/home/ubuntu/Certonomous/verification/runs/T-family/T10aVF_runs/{t10avf_analysis.json,t10a_reanalysis.json}` |
| raw logs | `.../T10aVF_runs/{run_t10avf.out,t10avf_analysis.out,t10a_reanalysis.out,precheck_t10a_existing.out}` |

**Disk, for the supervisor's commit decision.** `T10aVF_runs/` is **1.4 GB**, of
which **1.3 GB is the 34 cases' `constant/F` and `constant/globalFaceFaces`**.
Everything else — dictionaries, `blockMesh`/`checkMesh`/`viewFactorsGen` logs,
`STATUS`, `CASE.json`, the two analysis JSONs, the five scripts and the whole
reproducer — is **43 MB**, and the reproducer alone is **172 KB**. Every matrix
is regenerable from the committed dictionaries in the times recorded in §9.
This lane commits none of it; the recommendation is to commit the small set and
leave the matrices on disk, as T10a's own run tree already is.

*Written by the T10a-VF characterisation lane, 2026-08-22. Not committed by
this lane: the supervisor commits `T10aVF_RESULTS.md`, the upstream draft and
the queue file.*
