# B-52 rung 6 — two same-recipe replicate meshes: pre-registration

**Written 2026-08-10, before any replicate mesh exists and before any command
was run against this arm.** Nothing below this document's commit hash has been
meshed, solved, or read. The two division triples, the admission gate on cell
count, the fork, and the materiality bar are all fixed here.

Docket item: `b52-replicate-meshes-at-rung-6` (well W3, `est_core_min` 14.0),
raised by entry 4 of
`demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`. This is
the last unexecuted diagnostic from that review.

Model rule, per SUPERVISION_CHARTER §5: this arm was designed and is being run
on the session default model. Stated, not silent.

---

## 1. The question, and why it is not the B-52 ladder's question

The B-52 ladder's own question is closed. `B52_RUNG8_RESULTS.md` measured an
eighth rung whose increment (−2.78 × 10⁻⁴) is **15% of the measured 1.91 × 10⁻³
mesh-construction noise floor**, the surface-resolution alternative was refuted
for the cost of reading the meshes, and the verdict stands at `conclusive:
false` with no reportable band. A ninth rung buys another noise sample.

What is **not** closed is the floor's origin. The floor is one number,
1.9146 × 10⁻³, and it was measured exactly once:
`W3_MESH_NOISE_FLOOR_RESULTS.md` §4 built one replicate of rung 7 (441 079
cells against rung 7's 441 057, **22 cells apart, 0.005%**) and differenced the
two drags. That is a **single pairwise difference between two draws at one
resolution on one body**. Everything the lab now says about the B-52 family —
including that its eighth rung is noise — is scaled against that one number.

This arm asks whether a second, independent pair of draws at a *different* rung
of the *same* recipe reproduces it.

## 2. The pre-declared fork — written verbatim, before compute

From entry 4 of the supervisor review, verbatim:

> If replicates reproduce the floor, the recipe owns it (castellation); if not,
> the floor is iteration-history noise and the settle gate needs work.

From the launch instruction for this arm, verbatim:

> replicates reproduce the floor → the RECIPE owns it (castellation-driven draw
> sensitivity); replicates do NOT reproduce it → the floor is iteration-history
> noise and the settle gate needs work.

Both statements are the fork this arm is run to decide. The dividing line
between them is §3, fixed before any mesh is built.

## 3. The materiality bar — the dividing line, fixed now

**The deciding statistic is `D6 = |Cd(6b) − Cd(6c)|`**: the absolute drag
difference between the two *new* replicate draws, both built and solved in this
arm under byte-identical settings.

**Why that statistic and not a range or a standard deviation.** The floor is a
single pairwise difference. `W3_MESH_NOISE_FLOOR_RESULTS.md` §3 corrected itself
on precisely this point — *"A range over n = 4 and a single pairwise difference
are different statistics and are not directly comparable"* — after the four-mesh
replay moved the fitted exponent from 1.98 to 1.42. So the comparison is
like-for-like by construction: one pairwise difference against one pairwise
difference, at the same recipe, both at the same nominal resolution.

**The bar:**

| branch | criterion on `D6` | absolute | verdict |
| --- | --- | --- | --- |
| **REPRODUCE** | `D6 ≥ 0.50 × 1.9146e-3` | **≥ 9.573 × 10⁻⁴** | the RECIPE owns the floor — castellation-driven draw sensitivity |
| **NOT REPRODUCE** | `D6 ≤ 0.10 × 1.9146e-3` | **≤ 1.915 × 10⁻⁴** | the floor is not draw-generated at this rung; the fork's second branch (iteration-history noise, settle gate needs work) is the reading |
| **UNDECIDED** | `1.915e-4 < D6 < 9.573e-4` | between | **no branch is claimed**; reported as undecided, with the cost of a third and fourth draw priced in the record |

**Why a factor of 2 for "reproduce".** A single pairwise difference from n = 2
is a one-sample estimator of a scale, and the lab has measured how badly it can
misstate one: on the NACA 0012 the pairwise statistic and the 4-mesh range
disagreed by a factor of 1.63 in ratio terms (W3 §3), and on the NACA 4412 the
draw scatter spanned a factor of 158 across four rungs of the same recipe.
Nothing in that record supports a bar tighter than a factor of 2 on a one-pair
estimator, and a bar looser than that would make "reproduce" unfalsifiable.

**Why a factor of 10 for "not reproduce".** An order of magnitude below the
floor is where the draw scatter can no longer manufacture a 1.91 × 10⁻³
difference under any reasonable one-sample uncertainty on either measurement.
It is also comfortably above the family's iterative noise (rung 6's own
final-window 2σ is 2.25 × 10⁻⁶, per `b52.json` `iterative_audit`), so the
"not reproduce" branch cannot be won by an artefact of the settle window.

**The gap is deliberate and it is declared as a possible outcome, not a
loophole.** A one-pair estimator that lands between 10% and 50% of the floor
distinguishes nothing, and this arm will say so rather than argue itself onto a
branch after the fact.

**Third possibility, stated now so it cannot be discovered later.** If `D6`
lands in the REPRODUCE band the recipe owns *draw sensitivity at rung 6*; that
is what is claimed and no more. If `D6` lands in the NOT-REPRODUCE band, the
strict logical reading is that **the draw scatter is rung-dependent** — rung 7's
pair differed by 1.91 × 10⁻³ and rung 7 and rung 7b were also two draws — so
"the floor is iteration-history noise" is the fork's stated consequence but is
not the only account available. The record will state the fork's branch AND this
distinction, rather than let the fork's wording carry an inference the data
cannot.

## 4. Secondary readings — declared now, not verdict-bearing

Reported alongside `D6`, none of them deciding the fork:

1. **`R6` = range over three draws** {finer2, 6b, 6c}. finer2 is a legitimate
   third draw of the same recipe at the same rung — verified §5 — but it was
   solved in the 2026-08-01/02 campaign, so it is reported as a third draw with
   its date on its face and it does not enter `D6`.
2. **`D6 / 2σ`** — draw scatter against each replicate's own iterative scatter.
   Rung 7 gave 53×. This is the number that separates the fork's two branches
   mechanically.
3. **`D6` against the family's increments**: −4.055 × 10⁻³ (rung 6 → rung 7) and
   −2.78 × 10⁻⁴ (rung 7 → rung 8, the increment already called noise).
4. Mesh quality (max skewness, max non-orthogonality, cell count) from each
   replicate's birth certificate, so a quality cliff is on the record or ruled
   out rather than available as an after-the-fact explanation.

## 5. The recipe, and the proof that the replicates are the same recipe

Rung 6 is the case the corpus calls **finer2**:
`/home/ubuntu/certonomous-runs/study-b52-finer2-uq`, **330 950 cells**, background
blockMesh divisions **(51 45 75)**, published **Cd = 0.052275**.

Recipe held fixed at production/fine-uq/finer2/rung7/rung8: `nearBody`
refinement-shell level 2, `refinementSurfaces body { level (3 4); }`,
`b52.eMesh` feature level 3, kOmegaSST, magUInf 100, lRef 48.5, Aref 600.598,
rhoInf 1.225, 300 iterations, 2 MPI ranks hierarchical `n (2 1 1)`.

**Verified by checksum before this document was written** (finer2 against
rung 8, the most recent member of the family):

| file | result |
| --- | --- |
| `system/fvSchemes`, `fvSolution`, `controlDict`, `decomposeParDict`, `snappyHexMeshDict` | md5-identical |
| all of `constant/` except `polyMesh`/`extendedFeatureEdgeMesh` | `diff -rq` clean |
| `constant/triSurface/b52.stl` | md5 `c27eec6c710f0a937ec8cfe84aec2cfe`, identical |
| initial fields `k`, `omega`, `p`, `nut` (finer2's pre-solve `0/` vs rung 8's `0.orig`) | byte-identical |
| `system/blockMeshDict` | **the only file that differs** |

So the family really is one recipe with one knob, and the replicates are built
by moving that one knob without changing the rung.

**The draw mechanism.** snappyHexMesh has no random seed. The lab's established
way to draw a different mesh from the same recipe — used for every replicate in
`W3_MESH_NOISE_FLOOR_RESULTS.md` and for rung 7b specifically — is to move the
**background blockMesh division triple** while holding the target resolution,
which relocates the castellation lattice relative to the geometry and therefore
changes which cells are cut, refined and snapped. That is the "seed variation"
entry 4 names, and it is the only one this generator offers.

**The two draws, fixed now.** Rung 7b was drawn from rung 7 by the transform
(+1, −1, +1): (55 49 82) → (56 48 83). Applied to rung 6:

| draw | divisions | transform from (51 45 75) | background product vs finer2 |
| --- | --- | --- | --- |
| **6b** | **(52 44 76)** | (+1, −1, +1) — rung 7b's own transform | +1.02% |
| **6c** | **(50 46 75)** | (−1, +1, 0) | +0.22% |

Both cases are built by copying `/home/ubuntu/certonomous-runs/study-b52-rung8-uq`
verbatim (it carries `0.orig`, `mesh.sh`, `solve.sh` and the full verified
recipe) and editing the single `hex (...)` line.

## 6. Gates, fixed now

**G1 — admission on cell count (decided before any Cd exists).** Each replicate's
achieved cell count must land within **±2.0% of 330 950** (324 331 – 337 569) and
within **±2.0% of the other replicate**. Rationale for ±2.0%: rung 7/7b landed
0.005% apart, and W3's wing replicates ranged −0.66% to +8.25% on the same
transform class; ±2% keeps both draws at the same nominal resolution while
allowing for the snappy cascade's known nonlinearity in background density.
A draw that misses is **re-drawn**, with the missed attempt and its cell count
recorded (the rung-7 attempt-1/attempt-2 precedent: meshing produces a cell
count, not a force, so a re-draw at this stage is experiment design, not tuning).
**At most two re-draws per replicate.** If the gate cannot be met, that is the
arm's finding and it is reported as one.

**G2 — mesh birth certificate (MESH_STANDARD v1.1 / Verification Charter v1.5
§9, adopted 2026-08-08).** Every mesh this arm generates gets its
`birth_certificate.json` written **at creation**, beside its `polyMesh`, from
its own `log.checkMesh`, via `sdk/chief_engineer/mesh_certificate.py`
(`write_certificate`). Before either solver launches,
`mesh_certificate.certificate_admits()` must return True — certificate present,
`points_sha256` matching the points file actually there, verdict in
`("clean", "flagged")`. **An uncertified or born-broken mesh is refused at
launch and no solve is spent on it.** The certificate contents (verdict, cells,
max aspect ratio, max non-orthogonality, max skewness) go into the results
record verbatim.

**G3 — the settle gate, carried forward from rungs 7 and 8.** Each replicate's
final-20% window (60 of 300 rows of
`postProcessing/forceCoeffs1/0/coefficient.dat`) must have **2σ below 5% of
|Cd|** — the ceiling `run_uq_studies` applies before it will store a rung. Halves
drift (rows 150–225 vs 225–300) is reported alongside. The Cd of record is the
**mean over that same final-60 window**, the family's convention, on both
replicates and on finer2 when it is re-read.

Note on what G3 is *not*: the rung-7/8 form of this gate also required 2σ below
10% of *the increment*. There is no increment here — the quantity being measured
IS `D6` — and gating on it would make the gate circular. So the |Cd| limb is the
gate, and `D6 / 2σ` is reported as a secondary reading (§4.2) rather than used as
a pass condition.

**G4 — lever echo (Verification Charter v1.5 §9, `levers_verified_active`,
adopted 2026-08-08).** Both solves launch through the shared solver runner
(`sdk/workflows/tmr_verification.py::_foam`), which writes the fenced,
sha256-bound `LEVER-ECHO` block at the head of the solver log via
`sdk/chief_engineer/lever_echo.py`. `levers_verified_active` is then built
**mechanically from the log itself** by `lever_echo.levers_verified_active()`
and stored in each replicate's `record.json`. Since the two replicates are
supposed to differ in nothing but the mesh, the echoed sha256 set for
`system/fvSchemes`, `system/fvSolution`, `constant/turbulenceProperties`,
`constant/transportProperties` and every `0/` field **must be identical between
6b and 6c**. That equality is itself a pre-registered check: if any hash
differs, the two solves were not the same experiment and `D6` measures something
other than the mesh draw. **A hash mismatch voids the arm's verdict**; it would
be reported rather than patched over.

**Defect found while reading the runner, and declared here before use.**
`tv._foam` fires the echo on `args[0] in lever_echo.SOLVERS`. The B-52 family
launches its solver as `mpirun -np 2 simpleFoam -parallel`, so `args[0]` is
`mpirun` and **the echo would not fire on any MPI-parallel launch**. No caller
anywhere in the repo currently passes `mpirun` to `_foam` (verified by grep), so
generalising the test to "any argument is a known solver" is a provable no-op for
every existing call site and is made as part of this arm. It is recorded here
because a lever gate that silently does not fire is worse than no gate, and this
one had never been exercised in parallel.

## 7. Cost, priced from the nearest measured basis

**The basis is named, and it is a measurement, not a factor.** Per the
calibration finding (*"the predictor is the basis, not a factor"*), the price
below is taken from **the finer2 case itself** — the same rung, the same recipe,
the same 330 950 cells, the same 2 MPI ranks, the same 300-iteration cap. No
scaling law is applied to anything.

| phase | measured basis | source | core-min per replicate |
| --- | --- | --- | --- |
| surfaceFeatureExtract + blockMesh + snappyHexMesh + checkMesh | finer2's own snappy: **58.16 s**, plus the 6.4 s of surrounding utilities measured at rung 8 (189 s phase vs 182.63 s snappy) ≈ 65 s at 1 core | `study-b52-finer2-uq/log.snappyHexMesh`; `B52_RUNG8_RESULTS.md` cost table | **1.08** |
| potentialFoam + decomposePar | ~10 s at 1 core | `B52_RUNG8_RESULTS.md` cost table | **0.17** |
| simpleFoam, 300 iterations, 2 ranks | finer2: **ClockTime 284 s** (ExecutionTime 183.26 s) | `study-b52-finer2-uq/log.simpleFoam` | **9.47** |
| | | **per replicate** | **10.72** |
| | | **two replicates** | **21.4** |

Convention: core-min = ClockTime × ranks / 60, the convention `B52_RUNG8_RESULTS.md`
used (473 s × 2 / 60 = 15.77). The corpus is not consistent here —
`W3_MESH_NOISE_FLOOR_RESULTS.md` priced rung 7b off ExecutionTime instead
(271.04 × 2 / 60 = 9.03) — so **both numbers are reported in the results** and
the ClockTime one, which is larger, is the one budgeted against.

**Declared overrun, before launch: 21.4 core-min against the docket's
`est_core_min` 14.0 — a factor of 1.53.** The cause is named rather than
discovered: the review's 14 core-min priced two rung-6 solves at roughly 7
core-min each; the measured basis at this exact rung and rank count is 9.47, and
meshing plus the serial pre-steps add 1.25 that the estimate omitted. **Rank
count is not available as a saving.** Rung 7's pre-registration §2 fixed 2 ranks
across the family on the explicit ground that decomposition perturbs a steady
SIMPLE solve at the linear-solver tolerance level; varying it here would put a
decomposition artefact directly into `D6`, which is the one thing this arm
exists to measure. The overrun is declared now because silent overrun is
forbidden; measured cost is reported whatever it turns out to be.

## 8. Machine discipline

The A3 ladder agent is running rung-3 container work (`a3_rung3_n52`) on this
16-core box, memory-heavy. Load, free memory and running containers are checked
before each launch; meshing (1 core each) runs sequentially, and the two solves
(2 ranks each, 4 cores total, ~1 GB expected at 331k cells) are launched only if
the box has headroom at that moment. Solves are `setsid`-detached with
`.t0`/`.rc`/`.t1` ledgers and polled inline. Per L-41, a busy peer is invisible
to `pgrep`, so `git log --since` and run-directory mtimes are checked too.

## 9. What will NOT be claimed

- No band, order, or ladder verdict changes on the strength of this arm. The
  B-52 family's verdict (`conclusive: false`, no reportable band) is untouched
  whichever branch fires.
- Two draws at one rung do not establish a law for the recipe, a body, or a
  generator. W3 already measured two geometries behaving two different ways;
  nothing here generalises to a third without measuring it.
- The 1.9146 × 10⁻³ floor is not revised by this arm. It stays exactly what it
  is — one pairwise difference at rung 7 — and this arm adds a second, at a
  different rung, beside it.

*Nothing below this line existed when this document was committed.*
