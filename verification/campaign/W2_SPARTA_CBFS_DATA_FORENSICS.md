# W2 SpaRTA — CBFS data forensics: the benchmark's packaging vs Bentaleb's published LES

Date run: 2026-08-01 (UTC). Zero-compute rung: records and data forensics only — no
solver was launched, no graded number of `W2_SPARTA_FROZEN_CBFS.md` or
`W2_SPARTA_REGRESSION.md` is altered. Every analysis below that departs from the
pre-registered convention is labelled as such and sits beside the graded results, not in
place of them. Reproduction script: `sdk/scripts/cbfs_bentaleb_forensics.py` (arithmetic
on already-extracted fields plus archived-web downloads; runs in seconds).

## The hypothesis under test

The regression rung closed with a coherent set of CBFS-only discrepancies (its section
8): discovered R coefficient 0.5448 vs the paper's 0.93 (Eq. 24), with 0.93 provably
unreachable from our fields (OLS bound 0.594); training eps(R) 2x the paper's; Table 1
velocity ratio 75% high unweighted — while the SAME harness reproduces the PH column to
3.4% and the PH coefficient to 0.66%. Hypothesis: **one unstated CBFS processing
difference explains all of it**, candidate being that the benchmark clone's CBFS
packaging differs from the Bentaleb, Lardeau & Leschziner LES the paper used.

## RESULT IN ONE PARAGRAPH

**The packaging-difference hypothesis is refuted at the data level**: the benchmark's
CBFS fields are the NASA-hosted Bentaleb LES to interpolation accuracy (scaled MAE
~1e-6, regression slope 1.000000, every field). **But the search found the mechanism of
the CBFS-side discrepancies anyway, and it is a region, not a convention: the
under-resolved top-wall strip of the LES.** Cells above y/H = 8 — where the source LES
resolves an incidental top-wall boundary layer with ~4 coarse cells and where the
benchmark's interpolation had to extrapolate — contribute 34% of the candidate's
sum(x^2) at a local slope of 0.20, dragging the {T1} coefficient from 0.79 down to the
graded 0.59 (OLS). Excluding that strip moves every CBFS discrepancy toward the paper at
once (coefficient 0.545 -> 0.70-0.87 depending on gradient operator; eps(R) from 2x-high
to the paper's order; K from 21,000 to 14,560 ~ the paper's "K ~ 15000"), while the same
trims move the PH coefficient by at most 8%. **0.93 remains unreachable under every
transformation tested** — the ceiling is OLS 0.87, with the paper's own published
velocity-derivative file and the strip excluded — so the mutual-inconsistency finding
(Eq. 24 vs the paper's own Table 2 CBFS entry in our validated harness) stands, now
sharpened: whatever produced 0.93 was not a trim, weighting, gradient operator, or data
packaging that we can construct from the published LES.

## 1. What the benchmark ships for CBFS — characterised and diffed against source

**Provenance chain.** The benchmark README names its CBFS source: NASA TMR,
`turbmodels.larc.nasa.gov/Other_LES_Data/curvedstep.html` — the agency hosting of the
Bentaleb, Lardeau & Leschziner data ("The data on this page were provided by S. Lardeau
of CD-ADAPCO"). That live URL now redirects to a generic nasa.gov page (TMR site
restructured); the page and data files were retrieved from the Internet Archive,
snapshots 2021-03-18/19 (timestamps recorded in the script). The clone's `log.run`
header traces the case assembly to `TurbFOAM-7-Cases/.../Curved-Backward-Facing-Step`
(OpenFOAM 7, "TylerLaptop", Aug 2025); the clone's git history is a single squashed
commit, so the packaging history lives outside the repo.

**What NASA/Bentaleb publish** (READMEs + page text, archived): 768x160 cell-centred
2-D fields x, y, p, u, v, w, u'u', v'v', w'w', u'v', u'w', v'w', k, with
k = (uu+vv+ww)/2; velocities normalised by U_in (centre-channel inlet velocity), lengths
by step height H=1; Re_H = 13,700; domain x/H in [-7.34, 15.4], upstream duct height
8.52H (wall-quantities header: 1.0 < y/H < 9.52 at inlet); a separate velocity-derivative
file (dudx..dwdy, provided by Lardeau, revised 2012-03-12); wall quantities on the
**lower** wall only.

**What the benchmark ships** (`data/CBFS/0/`): U_LES, k_LES, tauij_LES, p_LES as
OpenFOAM fields assembled by `#include` from `0/interpolatedFields/*`, on the 140x150 =
21,000-cell mesh (the paper's own mesh size), cell centres x in [-7.26, 15.32], y in
[0.008, 9.512]; `nu = 1/13700` — i.e. the identical U_in/H non-dimensionalisation.
tauij is the full 6-component symmTensor in +u_i'u_j' convention; k_LES equals the
half-trace of tauij_LES to 8.5e-5 mean relative deviation (checked in the frozen rung).

**Field-by-field diff** (independent linear interpolation of the archived NASA files
onto the benchmark's cell centres; nearest-neighbour where outside the LES hull):

| Field | scaled MAE | slope (bench vs source) |
| --- | --- | --- |
| Ux | 7.1e-7 | 1.000000 |
| Uy | 3.4e-6 | 1.000000 |
| k | 1.1e-6 | 1.000000 |
| tau_xx / xy / yy / zz | 0.8-1.6e-6 | 0.999999-1.000001 |
| p | 3.8e-6 | 1.000002 |

Same domain (no trimming), same frame, same normalisation, same Reynolds convention,
same field set, linear interpolation. **The benchmark's CBFS is Bentaleb's published LES
as hosted by NASA, faithfully.** The recirculation statistics of the source data —
tau_w zero crossings at x/H = 0.828 and 4.355 from the archived wall-quantities file —
match the published LES values (0.83 / 4.36, quoted from Bentaleb's Table via secondary
sources, e.g. the IDDES reproduction, doi:10.3390/fluids10060145).

**The one packaging artifact found**: 303 benchmark cells — exactly the top two RANS
cell rows, y in [9.481, 9.512], all 140 columns and beyond the last LES cell-centre row
at y ~ 9.484 — lie outside the LES data hull and were filled by extrapolation
(benchmark values match nearest-neighbour fill to 5e-10). This is a faithful-packaging
consequence of a source-data limitation, not an error: the LES's top-wall region is
where the source itself is coarsest.

**Access statement.** Bentaleb, Lardeau & Leschziner, *J. Turbulence* 13(4) (2012) and
Lardeau & Leschziner, *JFM* 683 (2011) are paywalled from this box; claims about the LES
above rest on the archived NASA distribution (primary, checkable), its READMEs, and the
paper's numbers as quoted by accessible secondary literature. The near-top profile shape
in the data (u falling 0.76 -> 0.46 across the final ~0.08H-tall cell row) shows a
severely under-resolved top-wall boundary layer; McConkey et al.'s curated-dataset paper
(arXiv:2103.11515), which repackaged the same LES independently, likewise treats the
CBFS top boundary as a wall and notes the max-inlet-velocity Reynolds convention.

## 2. The transformation search (labelled analyses; graded numbers untouched)

All rows recomputed from the frozen fields of `cbfs_frozen/354` (and `ph_frozen/1492`
for the control) by the same candidate construction as the graded regression; "ridge" is
Eq. 20 at the pre-registered primary lambda_r = 0.0316. The graded row reproduces
exactly.

| # | Transformation | K | OLS | ridge | eps(R) at ridge c |
| --- | --- | --- | --- | --- | --- |
| 0 | none — graded convention | 21,000 | **0.5944** | **0.5448** | 3.75e-5 |
| 1 | volume-weighted (declared secondary) | 21,000 | 0.5674 | — | — |
| 2 | top strip excluded, y < 8 | 14,560 | **0.7925** | 0.6968 | 1.28e-5 |
| 3 | y < 9 | 17,780 | 0.7922 | 0.6966 | 1.05e-5 |
| 4 | any y-cutoff in [1.5, 8] | 5,022-14,560 | 0.7925-0.7927 | 0.697 | — |
| 5 | x-window trims (all tested) | 9,880-20,700 | 0.55-0.61 | — | — |
| 6 | candidate from LES-published velocity derivatives | 21,000 | 0.6175 | 0.5766 | 3.52e-5 |
| 7 | #6 + top strip excluded (closest approach) | 14,560 | **0.8697** | 0.7560 | 1.18e-5 |
| 8 | published 0.93 imposed, y < 8 | 14,560 | — | — | 1.29e-5 |

Structure of the graded 0.5944, decomposed: cells y < 8 carry the step physics at local
OLS 0.7925; the strip 8 < y < 9 is nearly orthogonal to the candidate (local slope
-0.08, negligible sum(x^2)); the top-wall strip y > 9 (3,220 cells, 15% of the domain)
contributes **33.6% of the total sum(x^2) at local slope 0.203** — in it the frozen
omega is 1.5-110 (nowhere near wall-function magnitude, because the interpolated LES
"wall layer" is a few coarse cells), k_LES is 0.005-0.012, and kDeficit is partly
*negative* where the candidate is large. One under-resolved incidental boundary layer,
faithfully interpolated, owns a third of the least-squares weight.

**PH control (the asymmetry explained).** The same trims applied to the PH frozen
fields move its {T1} coefficient only within 1.34-1.51 OLS (ridge 1.33-1.48) around the
published 1.39. Breuer's periodic-hill LES has two genuinely resolved walls and no
incidental under-resolved boundary; CBFS's top wall is unique to it. This is why every
PH quantity matches the paper while every CBFS quantity is off in a correlated
direction — the pre-registered all-internal-cells convention is *the same* on both
cases, but only CBFS has a data region that punishes it.

**Coherence with the other CBFS discrepancies.**
- Coefficient: 0.545 -> 0.70-0.87 (toward 0.93, not reaching it).
- Training eps(R): 3.75e-5 (2x the paper's 1.70-1.85e-5 axis range) -> 1.05-1.28e-5,
  i.e. from 2x high to ~30% low — the strip owns the eps(R) discrepancy too, though no
  single trim lands both the coefficient and eps(R) on the paper's numbers at once.
- Training-set size: K = 14,560 after the y<8 trim, against the paper's stated
  "K ~ 15000" (our full CBFS grid is 21,000; PH is 15,600). Consistent with — not proof
  of — the paper having trained CBFS on a wall-strip-free subset it did not describe.
- The paper's Fig. 4 CBFS colour (~0.4-0.5 by colourbar reading, per the regression
  record's section 4) sits *below* even our graded 0.545; no trim explains that either.

**Transformations ruled out entirely**: global convention rescalings (e.g. a beta*
factor in the time scale) are excluded because they would shift the PH coefficient
identically, and PH matches to 0.66%; domain trimming of the benchmark relative to the
LES (none exists — extents match); normalisation/frame/Reynolds differences (identical
by direct diff); tau sign or component conventions (identical); k 2-component vs
3-component (source k is (uu+vv+ww)/2, and the shipped k equals it).

**The remaining untestable step (declared, not smoothed over)**: the paper's own frozen
solve. If their omega boundary handling or solver version treated the top boundary
differently from ours (e.g. slip rather than a wall, or their omega wall function on
their mesh), both their candidate *and* their kDeficit would differ in exactly the strip
this analysis identifies — testing that requires re-running the frozen solve under
alternative top-boundary treatments, which is compute and belongs to a future docketed
rung if anyone judges it worth core-minutes. The arithmetic bound stands regardless: no
weighting or subset of *our* frozen fields reaches 0.93, and the strip-free ceiling is
0.87.

## 3. Verdict as it affects the ladder's findings

1. **The benchmark clone is exonerated.** Its CBFS packaging is the published LES,
   verified field-by-field against the archived NASA distribution at 1e-6. The
   regression record's alternative "or in the benchmark clone's CBFS packaging of
   Bentaleb's LES" clause of section 8 can be retired.
2. **The coherent-discrepancy finding is explained in mechanism and re-scoped, not
   overturned.** The CBFS-side discrepancies share a single dominant cause: the
   under-resolved top-wall strip of the source LES, which the pre-registered
   all-internal-cells convention weights heavily and the paper (which never states its
   training domain, weighting, or wall handling for CBFS) evidently treated
   differently. This is the third unstated-convention finding of the ladder, and the
   sharpest: the published CBFS coefficient is reproducible neither with the strip
   (0.545) nor without it (0.70-0.87).
3. **The mutual-inconsistency finding stands, strengthened.** Eq. 24's 0.93 remains
   outside the reachable set of every transformation constructible from the published
   LES data, while 0.93-as-written still fails to reproduce the paper's own Table 2
   CBFS velocity error in a harness that reproduces its PH column to 3%.
4. **Guidance forward** (supersedes nothing, informs the cross-validation rung): any
   future CBFS training or scoring should pre-register a top-strip policy explicitly
   (include / exclude / down-weight), because a third of the least-squares weight of
   the standard convention rides on data the source LES itself does not resolve.

## 4. In-sample gate

`sdk/scripts/closure_in_sample_gate.py`: **PASS**, run after all data touches of this
rung (see commit). Only CBFS13700 and PH10595 — benchmark training cases — and archived
public LES source files were opened; no scored case was touched.
