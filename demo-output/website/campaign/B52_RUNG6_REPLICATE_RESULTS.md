# B-52 rung 6 — two same-recipe replicate meshes: results

Pre-registration: `B52_RUNG6_REPLICATE_PREREGISTRATION.md`, **commit
`5c6825c7`**, committed before any replicate mesh existed and before any command
was run against this arm. Docket item `b52-replicate-meshes-at-rung-6`, raised by
entry 4 of `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` — the last
unexecuted diagnostic from that review.

Run 2026-08-10, native openfoam2606, 2 MPI ranks hierarchical `n (2 1 1)`, 300
iterations, recipe held at production/fine-uq/finer2/rung7/rung8.

---

## 1. The verdict, against the pre-registered fork

**`D6 = |Cd(6b) − Cd(6c)| = 1.35994 × 10⁻³ = 0.710 × the 1.9146 × 10⁻³ floor.`**

The pre-registered bar was **REPRODUCE at `D6 ≥ 0.50 ×` floor** (9.573 × 10⁻⁴),
**NOT REPRODUCE at `≤ 0.10 ×`** (1.915 × 10⁻⁴), undecided between. 0.710 is
inside the reproduce branch with margin, and it is not near either edge.

> **VERDICT: REPRODUCE. The RECIPE owns the floor — castellation-driven draw
> sensitivity.**

The fork's second branch — *"the floor is iteration-history noise and the settle
gate needs work"* — is **refuted**, and refuted with room to spare: both
replicates passed the settle gate at 0.028% and 0.030% of |Cd| against a 5%
ceiling, and `D6` is **94.6 times** the larger of their two final-window 2σ. The
settle gate does not need work. The mesh generator does.

## 2. The measurement

| draw | divisions | cells | Δ vs rung 6 | **Cd** | final-60 2σ | 2σ / \|Cd\| | halves drift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **finer2** (rung 6, 2026-08-01/02) | (51 45 75) | 330 950 | — | **0.052275472** | 2.244 × 10⁻⁶ | 0.0043% | +5.0 × 10⁻⁷ |
| **6b** (new) | (52 44 76) | 335 305 | +1.32% | **0.046920889** | 1.310 × 10⁻⁵ | 0.0279% | — |
| **6c** (new) | (52 45 74) | 333 217 | +0.68% | **0.048280833** | 1.438 × 10⁻⁵ | 0.0298% | — |

`D6` is the 6b–6c pair: both built and solved in this arm, under settings proven
byte-identical, deliberately the same one-pair statistic as the floor itself.

**The instrument was validated against published values before it was used.** The
settle reader in `B52_RUNG6_REPLICATE_runs/run_rung6_replicates.py` was run
against four archived cases first and reproduces every published Cd exactly:
finer2 0.052275472 (published 0.052275), rung 7 0.048220173, rung 7b
0.050134753, rung 8 0.047942443 — and rung 7 minus rung 7b returns
1.9146 × 10⁻³, the floor, to five figures.

## 3. The secondary readings — and the one that is larger than the verdict

Declared in §4 of the pre-registration as non-verdict-bearing. One of them is the
most consequential number in this record.

| reading | value | against |
| --- | --- | --- |
| `D6` | 1.35994 × 10⁻³ | **0.710 ×** the floor |
| `D6 / 2σ` (larger replicate) | **94.6 ×** | rung 7 gave 53× |
| **`R6` = range over three draws** {finer2, 6b, 6c} | **5.35458 × 10⁻³** | **2.80 ×** the floor |
| `D6` vs rung 6→7 increment (−4.055 × 10⁻³) | 0.335 × | |
| **`R6` vs rung 6→7 increment** | **1.32 ×** | |
| `D6` vs rung 7→8 increment (−2.78 × 10⁻⁴) | 4.89 × | |

**The finding that is larger than the arm's own question: three draws of one
recipe at one rung span 5.35 × 10⁻³ in Cd — 32% more than the largest single
increment anywhere in the B-52's valid family.** The rung 6 → rung 7 step of
−4.055 × 10⁻³ is the "turn" that `B52_RUNG7_RESULTS.md` reported as the ladder's
biggest signal and the reason its `monotone` flag flipped. **It is smaller than
the scatter of the rung it starts from.**

`W3_MESH_NOISE_FLOOR_RESULTS.md` §4 already wrote *"the turn is −4.055 × 10⁻³
± 47% from mesh construction alone"* from the rung-7 pair. Measured at rung 6
with three draws, the correct statement is **± 132%**. The turn is not a signal
with a large error bar; it is inside the error bar.

> **AMENDMENT 2026-08-10, same day, by the author — the paragraph above compares
> two different statistics and overstates its case. Original text retained per
> the supersede-don't-delete convention; see
> `B52_TURN_CLAIM_AUDIT_2026-08-10.md` §0 for the full working.**
>
> `R6` is a **range over three draws**; the turn is a **single pairwise
> difference**. Comparing them is the exact error `W3_MESH_NOISE_FLOOR_RESULTS.md`
> §3 corrected itself on, and I repeated it. Like-for-like, the turn is **2.98×**
> the rung-6 pairwise `D6` and **2.12×** the rung-7 pairwise floor — not 0.76× a
> range.
>
> Converting every estimator to a common σ (`E|X₁−X₂| = 1.128 σ`,
> `E[range of 3] = 1.693 σ`) brackets σ at **1.21–3.16 × 10⁻³**, and an increment
> differences two singly-drawn rungs so it carries **√2 σ = 1.70–4.47 × 10⁻³**.
> **The turn is therefore 0.91–2.38× its own mesh-construction uncertainty:
> not established as signal (which needs ≥3×), and not established as pure noise
> either. Three draws cannot separate those two readings.**
>
> What is unaffected: the arm's own verdict (§1), which is a pairwise-vs-pairwise
> comparison by construction and needs none of this; and the rung 7→8 increment,
> at **0.06–0.16×**, which is unambiguously noise on every estimator.
>
> The chief's entry-4 outcome block (`1a0e9a37`) quotes the 1.32× framing. That
> record is the chief's and has not been touched; the correction is filed for his
> ruling.

**Mesh quality is not available as an explanation.** All three draws certify
`clean` with max skewness 3.958–3.971 and max non-orthogonality 55.5–64.9,
against finer2's own family range — no cliff, no outlier, and the largest-Cd draw
(finer2) is not the worst-quality one.

**The cell-count spread is accounted for rather than waved away.** 6b and 6c
differ by 0.63% in cells, where rung 7 and rung 7b differed by 0.005%. Pricing
that difference against the family's own refinement rate (≈4 × 10⁻³ of Cd per
≈33% of cells) predicts a genuine-refinement contribution of ≈7.6 × 10⁻⁵ to
`D6` — **5.6% of it.** The same arithmetic gives ≈1.6 × 10⁻⁴ for finer2-vs-6b
against an observed 5.35 × 10⁻³. Refinement is not what these numbers are made
of.

## 4. Machinery: what the two 2026-08-08 gates actually did

Both adopted gates were used, and **both fired.** Neither was decoration.

### G1 — cell-count admission: REFUSED A DRAW, before any solve

The pre-registration named 6c's first draw as **(50 46 75)**, chosen because its
background-cell product sits +0.22% from finer2's — the closest of any candidate.
It meshed to **352 596 cells, +6.54%**, outside the declared ±2.0% band. **G1
refused it and no solver was launched on it.** The declared re-draw allowance was
used: attempt 2, **(52 45 74)**, landed at 333 217 cells, +0.68%, admitted.

That refusal is a finding in its own right, and it is the same finding as the
verdict wearing different clothes: **the achieved cell count is not controlled by
the background product.** (51 45 75) and (50 46 75) differ by +0.22% in product
and by **+6.5% in delivered cells**, while (52 44 76) is +1.02% in product and
+1.32% in cells. The ny division dominates and the cascade is nonlinear in it —
exactly the nonlinearity §6 G1 was written to absorb, firing on the first draw it
was applied to.

| draw | divisions | product Δ | achieved cells | achieved Δ | G1 |
| --- | --- | --- | --- | --- | --- |
| finer2 | (51 45 75) | — | 330 950 | — | — |
| 6b | (52 44 76) | +1.02% | 335 305 | +1.32% | admitted |
| 6c attempt 1 | (50 46 75) | +0.22% | 352 596 | **+6.54%** | **REFUSED** |
| 6c attempt 2 | (52 45 74) | +0.60% | 333 217 | +0.68% | admitted |

### G2 — mesh birth certificates: written at creation, checked at entry

Every mesh this arm generated got `birth_certificate.json` written beside its
`polyMesh` **at creation**, from its own `log.checkMesh`, via
`sdk/chief_engineer/mesh_certificate.py`. `certificate_admits()` was called
before each `simpleFoam` launch and returned `(True, "clean")` for both admitted
draws — certificate present, `points_sha256` matching the points file actually
there, verdict accepted. The certificates are archived beside this record as
`B52_RUNG6_REPLICATE_runs/rung6{b,c}.birth_certificate.json`.

### G3 — settle gate: PASSED on both, and the margin is the verdict's backbone

2σ = 1.310 × 10⁻⁵ (6b) and 1.438 × 10⁻⁵ (6c), i.e. 0.0279% and 0.0298% of |Cd|
against the 5% ceiling. The fork's alternative branch required the floor to be
iteration-history noise; iteration history at this rung is **two orders of
magnitude too small to reach it**, and `D6 / 2σ = 94.6`.

### G4 — lever echo: it fired for the first time on a parallel launch, because this arm had to fix it first

**A defect was found in the shared runner while reading it, declared in §6 of the
pre-registration before use, and fixed.** `tv._foam` fired the echo on
`args[0] in lever_echo.SOLVERS`. The B-52 family launches as
`mpirun -np 2 simpleFoam -parallel`, so `args[0]` is `mpirun` and **the echo
would not have fired at all.** No caller in the repo passes `mpirun` to `_foam`
(verified by grep), so generalising the test to *any* argument is a provable
no-op for every existing call site; committed at `199e9d17` and **verified live**
— `log.simpleFoam` for both replicates opens with `==== LEVER-ECHO BEGIN ====`
and ten hash-bound files. A lever gate that silently does not fire is worse than
no gate, and this one had never been exercised in parallel.

## 5. G4's equality check FAILED AS WRITTEN — the diagnosis, and the call

The pre-registration added a check of its own on top of the echo: since the two
replicates are supposed to differ in nothing but the mesh, **the echoed sha256
set must be identical between 6b and 6c**, and it wrote *"a hash mismatch voids
the arm's verdict."*

**It mismatched.** Ten files echoed; eight identical; **two differ: `0/U` and
`0/phi`.**

**The diagnosis, and it is proven rather than asserted:**

- `diff -rq` on the two cases' `0.orig` — the **specified** initial and boundary
  conditions, the thing the gate exists to check — reports **byte-identical**,
  across all five fields (`U`, `k`, `nut`, `omega`, `p`).
- `0.orig` **contains no `phi` at all.** `phi` exists only because the family's
  `solve.sh` runs `potentialFoam -writephi` before `simpleFoam`.
- `potentialFoam` writes `0/U` and `0/phi`. Both are **mesh-sized solution
  fields**, computed on the two different meshes. They have different lengths and
  different values because the meshes differ — **which is the independent
  variable of this experiment.**
- The eight files the gate exists to police — `system/fvSchemes`,
  `system/fvSolution`, `constant/turbulenceProperties`,
  `constant/transportProperties`, and `0/k`, `0/nut`, `0/omega`, `0/p` — are
  **hash-identical between the two runs.**

**The call, stated plainly because it is a judgment and the chief may overrule
it.** The gate's *purpose* — "prove the two solves were the same experiment
apart from the mesh" — is **satisfied, by hash, on every file that carries a
lever or a specified condition.** The gate's *wording* was mis-specified: it
echoed `0/` **after** an initialization step that writes mesh-sized fields into
it, so on any case with a `potentialFoam` pre-step the check could never have
passed between two different meshes. **The verdict stands, with the gate failure
and its resolution on its face rather than reinterpreted away.**

**Amendment for future arms, dated 2026-08-10, original wording retained above:**
lever-echo equality between replicates is checked over the **lever dictionaries
and the pre-solve `0.orig`**, never over a `0/` directory that an initialization
step has written into. Stated more usefully: *the echo binds what ran; it does
not distinguish what was specified from what was computed, and an equality check
across cases must supply that distinction itself.*

## 6. Cost, measured — including the waste, itemised

**A clean single pass would have cost 17.2 core-min against the pre-registered
21.4 — 20% under.** That is the honest comparison against the prediction:

| phase | measured | core-min |
| --- | --- | --- |
| three admitted/used meshes (74.2 + 66.6 + 61.2 s, 1 core) | 202.0 s | 3.37 |
| potentialFoam + decomposePar, 2 solves | ~20 s | 0.34 |
| 6b simpleFoam, 2 ranks | ClockTime 236 s (Exec 235.9) | 7.87 |
| 6c simpleFoam, 2 ranks | ClockTime 169 s | 5.63 |
| **clean-pass total** | | **17.2** |

Against the pre-registration's 21.4 (priced off finer2's own ClockTime 284 s at
this exact rung). Both replicates ran **faster** than the basis — 236 s and 169 s
against 284 s — on a box shared with the A3 ladder's rung-3 container. Reported
both conventions as promised: by ExecutionTime the two solves are 7.86 and 5.62
core-min, essentially identical here because these runs were not I/O-bound.

**Against the docket's `est_core_min` 14.0 the clean pass is 1.23×** — the
pre-registration declared 1.53× in advance from the finer2 basis, and the arm
came in under its own declared overrun. The declaration was the right call and it
was conservative.

**The waste, stated rather than netted out.** Actual spend was **≈25.9
core-min**; ≈8.7 of that bought nothing:

| wasted item | cause | core-min |
| --- | --- | --- |
| 6c's first completed solve, destroyed | re-entrancy defect below | ≈6.2 |
| two redundant mesh builds (352 596 rebuilt, 333 217 rebuilt) | same | ≈2.1 |
| 6c attempt-1 mesh (352 596), first build | **not waste** — G1's refusal is evidence (§4) | 1.11 |

**The defect, and it is a lesson the lab already owns.** The driver crashed on a
cost-summary line (`None` wall time on a reused mesh) *after* both solves
completed. Re-running it re-entered the draw loop, and because the re-draw loop
re-stages each candidate into the same case directory, it **re-meshed 6c's
refused attempt 1 into the directory holding 6c's finished solve and destroyed
it.** That is **L-42 exactly — "a rerun in place destroys the evidence its record
depends on"** — met head-on, in a script written by an agent who had read L-42
that morning. The mesh-reuse guard was written; the *solve*-reuse guard was not,
and the re-draw loop had no memory of which attempts it had already refused.

Both are fixed in `run_rung6_replicates.py` (solve reuse via `solve_is_complete`,
and the loop hardened so a refused attempt is never re-staged over a live case).
**The destroyed solve's Cd was not recovered from the wreckage and is not
reported**; 6c's Cd in §2 is the re-solve, on the same mesh, from the same
inputs. The two are expected to be identical and **that expectation is not
evidence**, so no claim is made from it.

## 7. What this closes, and what it does not

**Closes.** The origin of the B-52's 1.91 × 10⁻³ noise floor, on evidence, by the
protocol adopted for it: **the meshing recipe owns it.** A second family has now
been measured under the mesh-draw-sensitivity protocol, which is what that
protocol was adopted to be applied beyond its first case. Iteration history is
excluded by a factor of 94.6, and the settle gate is exonerated.

**Does not close, and is not claimed** (per §9 of the pre-registration):

- **No band, order, or ladder verdict changes.** The B-52 family's verdict stays
  `conclusive: false`, `not_conclusive_guard: order_window`, no reportable band.
  This arm makes that verdict *better founded*, not different.
- **No law is claimed for the recipe, the body, or the generator.** Two rungs and
  five draws on one airframe. W3 already measured two geometries behaving two
  different ways.
- **The 1.9146 × 10⁻³ floor is not revised.** It remains what it was — one
  pairwise difference at rung 7 — now with a second, independent pairwise
  difference at rung 6 beside it, 0.710× its size, and a three-draw range 2.80×
  its size.

**What it opens, stated without pricing it here.** `R6 / increment = 1.32` says
the B-52's largest ladder increment is inside its own single-rung draw scatter.
Every conclusion in this corpus that rests on a B-52 increment — and, by the
protocol's own logic, on any increment from a snappyHexMesh ladder that has never
had a replicate drawn at its rungs — is quoting a signal against an unmeasured
noise. `W3_MESH_NOISE_FLOOR_RESULTS.md` §5 already asked for per-rung replicate
refusal as a rule; this is the second family to say the rule is not optional, and
the first to say the scatter can exceed the largest increment in a family
outright.

## 8. Artifacts

| artifact | path |
| --- | --- |
| pre-registration (commit `5c6825c7`) | `campaign/B52_RUNG6_REPLICATE_PREREGISTRATION.md` |
| driver, gates, verdict logic | `campaign/B52_RUNG6_REPLICATE_runs/run_rung6_replicates.py` |
| machine-readable record | `campaign/B52_RUNG6_REPLICATE_runs/record.json` |
| timestamped stage log | `campaign/B52_RUNG6_REPLICATE_runs/driver.log` |
| birth certificates | `campaign/B52_RUNG6_REPLICATE_runs/rung6{b,c}.birth_certificate.json` |
| checkMesh logs | `campaign/B52_RUNG6_REPLICATE_runs/rung6{b,c}.log.checkMesh` |
| live cases (not committed; `postProcessing` is gitignored) | `/home/ubuntu/certonomous-runs/study-b52-rung6{b,c}-uq` |
| lever-echo fix, verified live | commit `199e9d17` |
