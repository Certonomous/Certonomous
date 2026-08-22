# T10a-VF. Characterisation of the view-factor row-sum defect in `viewFactorsGen`

**FROZEN before any sweep run.** Directive H-3(b) (`THERMAL_BUILDUP_DIRECTIVE.md`
line 19): *"the view-factor quadrature defect gets the characterization treatment
(mesh-family sweep, geometry sweep, reproducer from clean case) and joins the
upstream queue as candidate #4 — filing remains Sanaa's call."*

This is a **defect characterisation**, not a validation rung. There is no
reference band and none is armed. The graded observable is a **conservation
identity**, not a measurement: for any CLOSED enclosure of opaque surfaces,
`sum_j F_ij = 1` **exactly**, for every emitting face `i`, independently of how
coarsely the surfaces are faceted and independently of the flow, the material
and the temperatures. `rowSum - 1` therefore needs no reference of any kind and
cannot be argued with. Verdict vocabulary is the Charter §2 set:
**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.**

Run tree: `verification/runs/T-family/T10aVF_runs/`. **Mesh-side preprocessing
only** (Charter §2d): `blockMesh` + `viewFactorsGen`. No solver is invoked in
this arm, no case in the tree will ever hold a time directory, and nothing in
`verification/runs/T-family/T10a_runs/` is written to — T10a is read-only input.

**SUBMISSIONS PARKED.** The upstream draft this arm produces carries
`NOT FILED` in its opening line. Nothing is sent anywhere. Filing is Sanaa's
call alone.

---

## 0. Frozen file set and hashes

Committed together with this file, before any sweep case is built or run:

| path | sha256 |
| --- | --- |
| `docs/campaigns/T-family/T10aVF_PREREGISTRATION.md` | *(this file; hashed by the commit)* |
| `verification/runs/T-family/T10aVF_runs/build_t10avf.py` | `a1d289bee11fce40260ce1b6986ad343a1c0dd2b7d4ee96310ee79d1f078a462` |
| `verification/runs/T-family/T10aVF_runs/run_t10avf.sh` | `7fb1b12cefe03a7a308163457bf54ad6007d9a99e9c466230fe0a5acaeb2f49a` |
| `verification/runs/T-family/T10aVF_runs/analyse_t10avf.py` | `2e198d3fa59331186390ce41d380248f20112d4bc7e348cc6edeb118a2822f80` |
| `verification/runs/T-family/T10aVF_runs/vf_rowsum.py` | `3740c07d6d2647ed3856c3d006511f1785698491bead23ea0d5057e5f08515ad` |
| `verification/runs/T-family/T10aVF_runs/vf_edge_probe.py` | `9f06b38364a56e59ce7dfd118daf432e94590e572870e99d4724d6a551d339c8` |

The commit sha of this freeze is cited in `T10aVF_RESULTS.md`, not here.

---

## 1. Toolchain

OpenFOAM ESI **v2606** at `/usr/lib/openfoam/openfoam2606`, build string as
printed by every utility banner in this arm:

```
Using: OpenFOAM-2606 (2606) - visit www.openfoam.com
Build: _481094f-20260618
Arch:  LSB;label=32;scalar=64
```

Utility under characterisation: **`viewFactorsGen`**
(`applications/utilities/preProcessing/viewFactorsGen/viewFactorsGen.C`, 1323
lines, source present on this box). It is the utility T10a used for all 3D
cases (`build_t10a.py:549,554`). It is **not** `createViewFactors`, which is a
separate newer utility with its own `viewFactorModels` (2AI / 2LI / Hottel) and
its own dictionary keys; T10a used `createViewFactors` only for the 2D case
`H_2d`, and **`H_2d` is excluded from every claim in this arm** (§9).

`viewFactorsGen -help` exposes no quadrature options: every knob is a
`viewFactorsDict` key. The keys the utility actually reads are, verbatim from
`viewFactorsGen.C:476-486`:

| key | default in code | meaning |
| --- | ---: | --- |
| `GaussQuadTol` | `0.01` | relative-change acceptance for the 2LI Gauss order loop |
| `distTol` | `8` | `R/average(rm)`; **above** it a pair is "far" and uses 2AI, below it 2LI |
| `alpha` | `0.21` | *"Use for common edges for 2LI"* — the regularisation length fraction for the coincident-edge log singularity |
| `intTol` | `1e-2` | integration tolerance (2D/Hottel path) |

plus the non-quadrature keys `writeViewFactorMatrix`, `writePatchViewFactors`,
`dumpRays`, `debug`, `writeFacesAgglomeration`, `patchAgglomeration`,
`maxDynListLength` (confirmed against `etc/caseDicts/annotated/viewFactorsDict`
and the two tutorials that use the utility,
`heatTransfer/chtMultiRegionSimpleFoam/multiRegionHeaterRadiation` and
`heatTransfer/chtMultiRegionFoam/externalSolarLoad`). **There is no
`nRayPerFace` key in `viewFactorsGen`** — ray density is not a knob of this
utility; the visibility test is a CGAL AABB segment query, not a Monte-Carlo
ray sample. Agglomeration is optional and is OFF unless `constant/finalAgglom`
exists (`viewFactorsGen.C:504-514`); T10a ran no `faceAgglomerate`, so all
T10a view factors are un-agglomerated.

---

## 2. The pre-check, and what it already settled

The directive required, before any design, that the T10a outer-sphere row-sum
defect be shown to be a property of `viewFactorsGen` **rather than** of face
orientation on an enclosing sphere, of agglomeration, or of a visibility test
against a concave enclosure. That pre-check was run read-only against the
existing frozen T10a matrices (`vf_rowsum.py`, `vf_edge_probe.py`,
`analyse_t10avf.py`), and it is reported here because it fixes what the sweeps
are for. **It costs no compute beyond ~4 core-min of Python and touched no case
file.**

**PC-0 — the T10a numbers reproduce exactly.** Max `|rowSum-1|` over the outer
patch: **4.77258 / 4.27405 / 4.47372 %** at c/m/f, against T10a_RESULTS'
recorded 4.77 / 4.27 / 4.47 %. Inner patch: 0.47757 / 0.30049 / 0.11455 %,
against T10a's 0.48 / 0.30 / 0.11 %. The reader is reading the same numbers.

**PC-1 — the sign. It is an EXCESS, not a deficit.** Every outer-sphere row sum
is **greater** than 1: mean 1.04103 / 1.04035 / 1.03962 at c/m/f. T10a recorded
the magnitude `|rowSum-1|` and called it a "defect"; the direction was not
recorded. This matters, because a missing-visibility or over-shadowing
explanation can only *lower* a row sum. **Every such explanation is excluded by
the sign alone.**

**PC-2 — it is not orientation, and not the visibility test.** The
outer-to-inner block of the matrix is right: mean `sum_j F_2j` over the inner
patch is **0.250518 / 0.250478 / 0.250188** against the exact concentric-sphere
value `F_21 = (r1/r2)^2 = 0.25` — errors of 0.21 / 0.19 / 0.075 %, converging.
The visibility list is right too: an outer face sees 74.87 % of the other outer
faces against the exact 75 % blocked-fraction complement. Normals, enclosure
closure and the CGAL segment test are all behaving.

**PC-3 — it is not agglomeration.** `constant/finalAgglom` does not exist in
any T10a case; `useAgglomeration` is false in every T10a run.

**PC-4 — it is not the faceting of a sphere.** A closed enclosure of *flat*
facets still has exact row sums of 1. The faceting deficit is a different
quantity, already measured by T10a (−0.538 / −0.211 / −0.080 %) and already
shown to converge `O(h^2)`.

**PC-5 — the whole excess sits on four matrix entries.** For a representative
outer face of `S_f` (`vf_edge_probe.py`, row 2028, rowSum 1.0447367):

| receiving faces | count | `sum F` (utility) | exact `A_j/(4 pi R^2)` | excess |
| --- | ---: | ---: | ---: | ---: |
| share an EDGE with the emitter | 4 | 0.0435269 | 0.0006652 | **+0.0428617** |
| share a POINT only | 3 | 0.0006387 | 0.0005195 | +0.0000119 |
| share no vertex (outer patch) | 3064 | 0.7504821 | 0.7493716 | +0.0011106 |
| the inner patch | 984 | 0.2500889 | (0.25 exact, see PC-2) | +0.0000889 |

**95.9 % of the entire row-sum excess is carried by the four edge-sharing
neighbours**, whose view factors are over-estimated by a factor of ~64. The
remaining 3064 same-patch entries are collectively correct to 0.15 %.

**PC-6 — the mechanism, read out of the source.** `viewFactorsGen` sends a face
pair to the 2LI double-contour branch when `dist <= distTol`
(`viewFactorsGen.C:969`); two edge-sharing faces always are. Inside the 2LI
edge double loop, an edge pair whose midpoints coincide — which is exactly the
**shared edge**, traversed in opposite senses so `cos_ij = -1` — has its
quadrature order forced to 0 (`viewFactorsGen.C:1054-1058`), and `GaussQuad`
then evaluates the log singularity by the substitution
`r -> alpha*|s_i|` (`viewFactorsGen.C:390-394`), i.e.

```
    integral  ->  cos_ij * L^2 * 2 ln(alpha L)   =   cos_ij * L^2 * (2 ln L + 2 ln alpha)
```

whereas the exact self-edge contour integral over a segment of length `L` is

```
    integral_0^L integral_0^L ln((s-t)^2) ds dt  =  L^2 * (2 ln L - 3).
```

The substitution is therefore exact **iff** `2 ln(alpha) = -3`, i.e. iff
`alpha = exp(-3/2) = 0.223130160148...`. The shipped default is
`alpha = 0.21`. The residual, after the `1/(4 pi A_i)` normalisation of the 2LI
branch (`viewFactorsGen.C:1096-1097`) and with `A_i = L^2`, is a **pure number
with no `h` in it**:

> **e(alpha) = −(2 ln alpha + 3) / (4 pi)**, added to `F_ij` once per
> edge-sharing, mutually-visible neighbour.
>
> `e(0.21) = +0.0096524`. `e(0.22313016) = 0`. `e(0.10) = +0.1277`. `e(0.30) = −0.0471`.

Measured against that: the S_f probe gives **0.0428617/4 = 0.0107154 per
shared-edge pair** (11 % above the ideal-square prediction, the faces being
neither square nor planar). The T10a box `B_c/B_m/B_f` corner faces, which have
exactly 2 mutually-visible edge-sharing neighbours across a box edge and whose
geometry is exact, give max excess **1.92853 / 1.91321 / 1.90893 %** against the
predicted `2 e(0.21) = 1.9305 %` — agreement to 0.1 / 0.9 / 1.1 %.

**PC-7 — why it does not converge, and why the box looked as if it might.** The
per-pair error is `h`-independent, so a row's error is `n_edge_vis * e(alpha)`,
where `n_edge_vis` is the number of edge-sharing neighbours that are also in the
emitter's visibility list. On a **convex** patch, adjacent faces are coplanar or
face away and are not visible — `n_edge_vis = 0` — which is why T10a's inner
sphere rows are clean (0.11 %) and why they show `inner -> inner = 0.00000000`.
On a **concave, self-viewing** patch, all four are visible, `n_edge_vis = 4`,
and the row carries `4 e(alpha) = 3.86 %` at every resolution forever. On a
**box**, only the faces lying along the 12 box edges have a visible edge-sharing
neighbour, so the patch *maximum* is pinned at `1 or 2 * e(alpha)` while the
patch *mean* falls like `O(h)` purely because the affected faces are a
one-dimensional subset — T10a's box means, 0.414 / 0.248 / 0.152 % on the floor,
are exactly that `O(h)` dilution and not a converging quadrature.

**PC-8 — why `GaussQuadTol` was inert.** The coincident-edge term is forced to
quadrature order 0 *regardless of the outer Gauss order*, so no tightening of
the Gauss-order acceptance tolerance can reach it. T10a measured the `_q` twin
at 10x tighter as moving the row sum by ≤0.006 %; the reanalysis here puts it at
`1.4e-6` absolute on the outer-patch mean. That is not a small effect — it is
**structurally zero**.

**Pre-check verdict: the row-sum excess is a defect of the `viewFactorsGen`
utility — specifically of the `alpha` regularisation of the coincident-edge term
in its 2LI branch — and is not an orientation artefact, not an agglomeration
artefact, not a visibility-test failure against a concave enclosure, and not the
expected behaviour of a faceted sphere.** The sweeps below exist to establish
that claim on clean-room geometry, across a mesh family, across convexity, and
against the knobs, and to give it a reproducer.

**Disclosure of prediction provenance.** The directive's suggested predictions
for Sweep 3 were *"none of the generator knobs moves the concave-row defect by
>0.5 pp"*. The pre-check's source reading falsifies that in advance for `alpha`
and for `distTol`, so the registered predictions below are the ones this lane
actually holds, and they are sharper and far easier to fail than the suggested
ones. Nothing below was fitted to a sweep result: no sweep case has been built,
meshed or run at the time of this freeze.

---

## 3. What is built and run

Clean-room cases only, `verification/runs/T-family/T10aVF_runs/cases/`.
Mesh route: `blockMesh` alone, the same route as T10a
(`build_t10a.py:sphere_block_mesh`, `box_block_mesh`) — `searchableSurface`
`project` for curved patches, plain hexes otherwise. **No `snappyHexMesh`
anywhere**, so every case is exactly reproducible from four small text files.

| geometry | description | enclosure character |
| --- | --- | --- |
| `BOX` | closed cube, 6 flat wall patches | convex, flat |
| `SHELL` | concentric cubes (outer 1.0, inner 0.5) | convex, flat, with an inner body |
| `SPH` | concentric spheres `r1=0.05`, `r2=0.1` (the T10a `S` geometry) | **outer patch concave, curved** |
| `BALL` | solid sphere `R=0.1`, one patch, no inner body | **fully concave, curved** |
| `CYL` | closed cylinder `R=0.1`, `H=0.2`, patches `side` / `ends` | **side concave in one direction only** |

34 cases in three sweeps, listed by `build_t10avf.py --list`.

**Sweep 1 — mesh family.** `SPH` at four resolutions, 768 / 1728 / 3072 / 4800
radiative faces (a **6.25x** face-count range, `h` down by 2.5x), identical
`viewFactorsDict` in all four. Plus an `_afix` twin of each at
`alpha = exp(-3/2)`.

**Sweep 2 — geometry / convexity.** `BOX`, `SHELL`, `BALL`, `CYL` at two
resolutions each, plus an `_afix` twin of each at the finer level. `SPH` is
covered by Sweep 1.

**Sweep 3 — generator knobs**, on one fixed mesh (`SPH` at 1728 faces):
`alpha` ∈ {0.10, 0.15, 0.20, **0.21**, 0.22, **exp(-3/2)**, 0.25, 0.30};
`GaussQuadTol` ∈ {**0.01**, 0.001, 1e-6}; `distTol` ∈ {1, 4, **8**, 100};
`intTol` ∈ {**0.01**, 1e-4}; agglomeration off / on
(`patchAgglomeration { viewFactorWall { nFacesInCoarsestLevel 10; } }`, via
`faceAgglomerate`), the latter also with `alpha = exp(-3/2)`.
Bold = the shipped default.

---

## 4. Registered predictions and gates

Gates are **PASS / GATE FAIL against these thresholds and nothing else**. No
reference band exists or is armed. Symbols: `E` = patch-mean `rowSum - 1`;
`n_ev` = patch-mean number of mutually-visible edge-sharing neighbours;
`e(a) = -(2 ln a + 3)/(4 pi)`.

| gate | prediction | PASS threshold | falsifier (GATE FAIL) |
| --- | --- | --- | --- |
| **VF-1** non-convergence | The `SPH` outer-patch `E` does not converge across a 6.25x face-count range | `max(E)/min(E) <= 1.30` over the four levels **and** every level's `E` in `[0.029, 0.049]` | monotone decrease by `>2x` across the family |
| **VF-2** localisation | The excess lives on the edge-sharing entries | at the finest `SPH` level, the edge-sharing entries carry `>= 85 %` of the outer-patch mean excess | `< 85 %` |
| **VF-3** per-pair constant | The per-pair excess is a constant of `alpha`, not of `h` | `E/n_ev` in `[0.0080, 0.0130]` on **every** concave patch of Sweeps 1–2 at `alpha=0.21`, and its spread across the `SPH` mesh family `<= 15 %` | outside that interval, or spread `> 15 %` |
| **VF-4** convexity law | `E ≈ n_ev * e(alpha)` patch by patch | for every patch of Sweeps 1–2: `\|E - n_ev*e(0.21)\| <= 0.30*\|E\| + 0.002`; and convex/flat patch means fall by `>= 1.6x` per mesh doubling while concave patch means do not | any patch outside the tolerance |
| **VF-5** `alpha` is the lever | `E(alpha)/n_ev` follows `e(alpha)` and crosses zero at `exp(-3/2)` | over `alpha` in `[0.15, 0.30]`: `\|E/n_ev - e(alpha)\| <= 0.20*\|e(alpha)\| + 0.003`; and the zero crossing within `±0.005` of `0.223130` | outside |
| **VF-6** `alpha`-fix twins | Setting `alpha = exp(-3/2)` removes the defect on **every** geometry | every `_afix` case: **all** patch means `\|E\| <= 0.005` | any `_afix` patch mean `\|E\| > 0.005` |
| **VF-7** other knobs inert | `GaussQuadTol` and `intTol` cannot reach the coincident-edge term | `GaussQuadTol` 0.01→0.001→1e-6 and `intTol` 0.01→1e-4 each move the `SPH` outer `E` by `<= 0.05 pp` | `> 0.05 pp` |
| **VF-8** `distTol` workaround | Dropping `distTol` below the adjacency ratio (`≈ 2/sqrt(pi) = 1.128` for square faces) routes edge-sharing pairs to 2AI and removes the defect | `distTol = 1` gives `SPH` outer `E <= 0.005`; `distTol` 4 and 100 leave `E` within `0.3 pp` of the `distTol=8` value | otherwise |
| **VF-9** agglomeration | Agglomeration does not remove it (coarse faces still share edges) | **REPORTED ONLY, no gate.** Recorded either way | — |
| **VF-10** reproducer | The shipped reproducer reproduces the numbers from clean | its printed row-sum table matches the expected table registered in its README to `±0.0010`, in `<= 120 s` wall on 1 core | outside, or over time |

**Quantitative predictions written down now, to be scored later.**

| geometry | patch | predicted `n_ev` | predicted `E` at `alpha=0.21` |
| --- | --- | ---: | ---: |
| `SPH` | `outer` (concave) | 4 | **+0.0386** (+3.86 pp) |
| `SPH` | `inner` (convex) | 0 | ~0 |
| `BALL` | `outer` (fully concave) | 4 | **+0.0386** |
| `CYL` | `side` (concave circumferentially, flat axially) | **2** | **+0.0193** (+1.93 pp) |
| `CYL` | `ends` (flat) | O(h) | small, converging `O(h)` |
| `BOX` | any wall | O(h) | small, converging `O(h)`; **patch max pinned at 1.93 %** |
| `SHELL` | `outer`, `inner` | O(h) | small, converging `O(h)` |

The `CYL` row is the sharpest single test in the arm: a curved concave patch
that is concave in **one** direction only must show **half** the sphere's
defect. Nothing about "curvature" or "concavity" as such predicts a factor of
exactly two; the edge-counting mechanism does.

---

## 5. Cost

`viewFactorsGen` scales as `n^2` in radiative faces. Anchor: T10a spent
**9.4 core-min** of `viewFactorsGen` across its 13 built cases
(`T10a_RESULTS.md` cost section, line 228/333), whose `sum n^2 = 4.00e8`, i.e.
**2.35e-8 core-min per `n^2`**. Box rate **$0.0513/core-h = $0.000855/core-min**
(owner-stated).

| item | `sum n^2` | core-min | USD |
| --- | ---: | ---: | ---: |
| Sweep 1 (8 cases) | 7.2e7 | 1.69 | 0.0014 |
| Sweep 2 (12 cases) | 3.4e7 | 0.80 | 0.0007 |
| Sweep 3 (14 cases) | 4.2e7 | 0.99 | 0.0008 |
| `blockMesh` + `checkMesh`, 34 cases | — | ~2.0 | 0.0017 |
| analysis Python (34 sweep cases + 11 T10a re-reads) | — | ~12.0 | 0.0103 |
| reproducer build + 3 runs + README verification | — | ~1.0 | 0.0009 |
| **registered total** | 1.48e8 | **~18.5** | **~$0.016** |
| **registered ceiling incl. 3x contingency and reruns** | | **~56** | **$0.048** |

**Arm cap: 1.00 USD.** The registered estimate is 3 % of it. **If the cap is
approached, the cut order is: (1) `S1_SPH_L4` and its `_afix` twin (4800 faces,
the single most expensive pair, costs 0.54 of the 3.5 core-min of
`viewFactorsGen`) — Sweep 1 then spans 4x rather than 6.25x face count and VF-1
is scored on three levels; (2) `S2_SHELL_f` and its twin; (3) the `distTol=100`
and `intTol` knob cases.** Nothing in Sweeps 1–3 requires a solver, so no cut
touches a flow result.

**Concurrency.** At most 2 cores, serial utilities, `MAXJOBS=2`. The box is
shared: ~13 cores are held by other lanes (4 T1b L4, 8 T3 ext1, T10a-R), load
average 22–27 of 16 at launch. This arm adds at most 2.

---

## 6. Analysis method

`analyse_t10avf.py` streams `constant/F` together with
`constant/globalFaceFaces` (`F` is stored compactly, one row per radiative face,
its columns indexed by the visibility list) and, per patch, reports
`meanRowSum`, `min`, `max`, `median`, `meanEdgeNbrsVisible` (`n_ev`),
`meanF_on_edge_nbrs`, the row-sum split by receiving patch, and
`excess_per_edge_pair = E/n_ev`. Edge adjacency is built from
`constant/polyMesh/faces` — two boundary faces are edge-sharing iff they share
an ordered pair of point labels. No case file is written.

`vf_rowsum.py` and `vf_edge_probe.py` are the read-only pre-check tools, kept
because the pre-check numbers in §2 are theirs.

---

## 7. What this arm cannot show, registered in advance

1. **It does not measure any flux, any temperature, any heat transfer
   coefficient.** No solver runs. The consequence of the defect for a solved
   field is bounded only by what T10a already recorded (C3b uniform-300 K box:
   max `|qr| = 13.95 W/m^2 = 3.0 %` of `sigma T^4`), and that bound is quoted,
   not re-measured.
2. **It does not re-grade T10a.** T10a's S0/S1 remain **NOT A RESULT** on
   T10a's own registered grounds. This arm changes the *description* of the
   T10a floor (an excess with a named mechanism, not an unexplained defect) and
   nothing else.
3. **It says nothing about `createViewFactors`**, whose 2AI/2LI/Hottel models
   are separate code with a different `alpha`-free 2AI (`viewFactor2AI.C` uses
   *signed* cosines, where `viewFactorsGen` takes `mag()` of both). T10a's
   `H_2d` used `createViewFactors`/Hottel, shows a row-sum **deficit** of
   2.7–3.3 % rather than an excess, and is a different phenomenon that this arm
   reports and does not claim.
4. **It does not show that the row-sum excess is the largest error in a
   radiation solve**, or that any published result is wrong.
5. **It does not test the fix.** No patched binary is built. `alpha = exp(-3/2)`
   is applied only as a *dictionary* value through the existing shipped code
   path; that it drives the residual to zero is evidence about the mechanism,
   not a verified patch.
6. **`smoothing true` hides all of it** by row-renormalisation and is not
   graded here; T10a already registered that choice.

---

## 8. Deliverables

1. `docs/campaigns/T-family/T10aVF_RESULTS.md` — sweep tables, verdicts against
   §4, actual-vs-registered cost, "what this does NOT show", and the
   classification (utility defect / mesh-orientation artefact / expected
   faceting behaviour).
2. `docs/upstream/T10a_viewFactorsGen_rowsum_NOT_FILED.md` — the upstream draft,
   opening line `NOT FILED — draft for Sanaa's decision`, as **candidate #4**.
3. `verification/runs/T-family/T10aVF_runs/reproducer/` — minimal self-contained
   case, `Allrun`, `README.md` with the expected output.
4. `docs/upstream/UPSTREAM_QUEUE.md` — see §9.

## 9. Note on the queue file

There is no numbered upstream-queue file in the repo at freeze time.
`grep -ril "NOT FILED"` finds candidates #1–#3 as free-standing documents under
`cases/dafoam/` (`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`,
`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`,
`DEFECT_CANDIDATE_ksp_options_override.md`, plus the ILU zero-pivot note), and
the only place they are enumerated as a queue is the prose line
*"four upstream defect drafts, all NOT FILED"* in `docs/LAB_STATE.md:317` and
*"the T10a view-factor defect as upstream candidate #4"* at
`docs/LAB_STATE.md:66-67`. Those are DAFoam-family documents in a
DAFoam-family directory; a T-family OpenFOAM defect does not belong there.
**This arm therefore creates `docs/upstream/UPSTREAM_QUEUE.md` as the
lab-level queue file, transcribing candidates #1–#3 by reference (path,
target project, status) without moving or editing them, and adding this
work as candidate #4.** The supervisor may relocate or fold it; nothing in
`cases/dafoam/` is touched.

---

*Pre-registration written by the T10a-VF characterisation lane, 2026-08-22,
before any sweep case was built, meshed or run.*
