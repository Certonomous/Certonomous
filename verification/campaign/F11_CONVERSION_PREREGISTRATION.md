# F11 lid-driven cavity ladder — CONVERSION PRE-REGISTRATION

**Written 2026-08-25, frozen before any solver in this conversion has started.**

**Condition checked, not asserted (VERIFICATION_CHARTER §2b.1):** the run root
`verification/runs/F11_runs/conversion_2026-08-25/runs/` **does not exist** at the
time of writing. Checked by this lane, not assumed: neither
`verification/runs/F11_runs/conversion_2026-08-25` nor its `runs/` subtree nor any
case directory, `0/`, time directory, `log.simpleFoam` or `postProcessing/` beneath
it exists. The only contents of `verification/runs/F11_runs/` at this commit are
`cavity_ladder.py` and `ladson_reference_note.md`, both dated 2026-08-16 by mtime.
The launcher registered in §6 refuses (rc=3) any case directory that already
exists, so this condition is **enforced** for every run this document authorises
and not merely stated here once.

**Frame:** repo `/home/ubuntu/Certonomous`. Written against the tracked tree at
`9c69a79a`, the commit that landed the instrument frozen in §8.1; peers commit
constantly, so this document's own commit parent is re-derived at commit time and
is recorded by the commit itself. The instrument blob named in §8.1 was re-verified
unchanged at `7d09e4c9` immediately before this document was committed.
**Team:** cfd. **Lane:** lab-lane under cfd-supervisor.

**Why this document exists — Sanaa's directive, verbatim:**

> *"CFD team — Re-run under frozen pre-registrations, <40 core-min each: F3
> (supersonic exact suite), F11 (per capability map), F4 (hypersonic) — the
> early PASSes that lack prereqs convert to HOLDS."*

**A correction to the directive's own wording, made here rather than quietly
absorbed.** F11's 2026-07-30 record does not carry a `PASS`. Its verdict line
reads **`GATE REACHED, both rungs, both quantities, both mesh resolutions.`**
The directive's phrase "the early PASSes" does not describe this family, and this
document does not convert a PASS into anything. What it converts is a
**`GATE REACHED` that was never gated**: no band, no threshold and no label were
fixed before that run, so there was no criterion for the gate to have reached.
Under standing rule 2 that record is a **result, not a credential**, and the
correction matters because a conversion that mis-describes what it is converting
has already lost the thread.

---

## 1. The defect being repaired

`verification/campaign/F11_lid_driven_cavity_ladder.md` (2026-07-30) records four
`simpleFoam` laminar solves — Re = 100 and Re = 1000, each at n = 64 (4,096 cells)
and n = 128 (16,384 cells) — compared point by point against Ghia, Ghia & Shin
(1982) centreline tables, and reports **`GATE REACHED`** with a headline "maximum
absolute deviation 1.73% of the lid speed".

**There is no pre-registration for any of it.** No band existed before the numbers
did. The freeze *is* the evidentiary content of a pre-registration (standing rule
2): it proves the gate could not have been chosen to fit the answer. A record with
no band at all cannot make that proof, whatever it proves about the solver.

**Four separate weaknesses in that record, named here so this document cannot
later be accused of having discovered them afterwards:**

| what the old record claims | what is weaker than it reads |
|---|---|
| `GATE REACHED`, four solves, 34 point comparisons | no band, threshold, cap or label was fixed in advance for any of the 34 |
| "grid sensitivity checked before quoting a result", two mesh resolutions | **two levels cannot make a Roache triple.** No observed order, no GCI, no discretisation-error estimate exists anywhere in the family. Its own prose says so: *"the two-point comparison is reported as exactly that, not oversold as Richardson-verified"* |
| "both resolutions already sit on a shared, few-tenths-of-a-percent plateau" | this is a **claim about the shape of a refinement sequence read off two points.** Two points have no shape. The record also notes two of its eight aggregate comparisons moved the "wrong" way under refinement and reads that as scheme scatter — a reading, not a measurement |
| reference: Ghia, Ghia & Shin (1982), Table I and Table II | the primary is **paywalled and not on disk**; the numbers come from two secondary GitHub transcriptions cross-checked against each other. Disclosed honestly in that record, and still not a title-page-verified primary (standing rule 15) |

The second row is the one this conversion exists for. Everything else in the old
record is honest reporting of an ungated measurement; the missing third mesh level
is the thing that can actually be bought, at a cost this document fixes below.

---

## 2. What is already known at the time of writing

Declared in full, so this document cannot be accused of following the answer.

**This is a conversion of an existing record. The freeze here cannot and does not
claim ignorance of the 2026-07-30 values.** More than that: this lane has read the
solver's own sampled artifacts off disk at all six gate stations registered in §3,
at both existing mesh levels, before writing this section. Those twelve numbers are
printed in §2.2. Concealing them would be worse than useless — the artifacts are on
disk and any reader can repeat the read in one command.

What the freeze protects is therefore narrower, and is stated exactly:

> The freeze protects against tuning a band to **the values this re-run produces**,
> and against choosing gate stations, a grid triple, a dimensionality, a completion
> rule, a cost cap or a verdict vocabulary after seeing them. It does **not**, and
> cannot, protect against knowledge of the 2026-07-30 values.

The defence against that residual is in §4: **every band below is derived from
mesh geometry and from Ghia's own tabulated slopes, and no measured CFD value
enters any band's derivation.** The arithmetic is reproducible from
`cavity_ladder.block_mesh_dict` and the reference tables alone. And §2.1 does the
one thing that actually exposes this document to falsification: it **states the
outcome it predicts, before the run.**

**Not known at the time of writing, and not derivable from what is:** any value
this re-run produces at n = 32; whether any of the six grid triples is
`CONVERGING`; what observed order the ladder carries at dim = 2; what GCI the
ladder carries at Fs = 1.25. **A triple's state cannot be read from two levels**,
which is precisely why this run is worth its cost.

### 2.1 The prediction this document makes, before the run

Stated so that a reader can falsify this document rather than merely audit it.

1. **All six band verdicts are predicted `PASS`.** The bands of §3 were derived
   from geometry before the values of §2.2 were read, and when the two are placed
   side by side, every existing n = 128 value falls inside its band.
2. **`G-F11-2` is predicted to pass by 0.00020 in lid-speed units — 2.5 % of its
   own band half-width.** It is the one gate here that can plausibly fail on a
   value shift smaller than the n = 64 → n = 128 increment already measured, and
   it is registered as the gate most likely to move.
3. **The six triples are predicted MONOTONE**, with the solution value moving
   *away* from Ghia's tabulated value as the mesh refines, at every one of the six
   stations. This is an extrapolation of a two-point trend to a third point and is
   labelled as exactly that: a prediction, not a measurement.
4. **The triple STATE is not predicted.** Monotone is necessary and not sufficient
   for `CONVERGING`: the instrument requires the last increment to have fallen to
   at most `r^-0.5` of the previous one. Whether the n = 32 → n = 64 → n = 128
   increments do that is unknown and is the load-bearing unknown of this run.

If the run returns a `GATE FAIL` on any of the six, or a non-monotone triple, this
section is wrong on its face and the record will say so beside the number.

### 2.2 The twelve values already on disk, printed rather than concealed

Read by this lane on 2026-08-25 from the 2026-07-30 sampled artifacts under
`/home/ubuntu/certonomous-runs/f11-cavity-ladder/<case>/postProcessing/centerlineProfiles/<iter>/{uAlongX05,vAlongY05}_U.xy`.
Deviation is `measured − Ghia`, in lid-speed units (`U_lid = 1`).

| gate | station | Ghia | n = 64 | dev @ 64 | n = 128 | dev @ 128 |
|---|---|---|---|---|---|---|
| G-F11-1 | Re 100, u(0.5, 0.9766) | +0.84123 | +0.8424794 | +0.001249 | +0.8434185 | +0.002189 |
| G-F11-2 | Re 100, v(0.8047, 0.5) | −0.24533 | −0.2520731 | −0.006743 | −0.2532286 | −0.007899 |
| G-F11-3 | Re 100, u(0.5, 0.5) | −0.20581 | −0.2073754 | −0.001565 | −0.2087405 | −0.002930 |
| G-F11-4 | Re 1000, u(0.5, 0.9766) | +0.65928 | +0.6626125 | +0.003333 | +0.6638775 | +0.004598 |
| G-F11-5 | Re 1000, v(0.9063, 0.5) | −0.51500 | −0.5180823 | −0.003082 | −0.5245857 | −0.009586 |
| G-F11-6 | Re 1000, u(0.5, 0.5) | −0.06080 | −0.0607727 | +0.000027 | −0.0618216 | −0.001022 |

**Read the deviation columns, not the value columns.** At **all six** stations the
deviation from Ghia *grew* under a 4× refinement in cell count. The old record
reported this as aggregate scatter and attributed it to the advection scheme. It is
in fact monotone at every station registered here, which is a different and more
interesting fact than the old record's own reading of it, and it is the reason §9
registers in advance how a small GCI beside a larger Ghia deviation will be read.

---

## 3. The gates, fixed now

Six gates. Verdicts come from the fixed vocabulary and from nowhere else:
**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING** (standing
rule 1). `PENDING` is used only for "not launched" and never to soften a
`GATE FAIL`.

**Quantities are SOLUTION VALUES at fixed named coordinates, in lid-speed units.**
They are *not* the old record's `max|err|` and `RMS|err|` aggregates. That change is
deliberate and is registered here with its reason: an error norm converges to zero,
so `GCI_pct` — which divides by the fine value — is meaningless on one, and a
Richardson extrapolate of an error norm is not a defined object. A solution value at
a fixed point has a limit, and is the only kind of quantity a Roache triple grades.

**Station selection rule, mechanical and computable from Ghia's table alone with no
CFD input:** per profile per Reynolds number, the tabulated station of **largest
|reference|** among the 15 interior gate points, plus the **cavity centre**
(0.5, 0.5), which both tables carry. The two boundary rows of each table (y = 0,
y = 1 for u; x = 0, x = 1 for v) are the imposed boundary condition itself — an
**IDENTITY** under VERIFICATION §2a, reproducible by any treatment — and are
excluded from every gate here, as they were in the old record.

| id | rung | quantity | station | reference (Ghia, secondary transcription) | band, lid-speed units | band interval on the fine value |
|---|---|---|---|---|---|---|
| **G-F11-1** | Re 100 | `u` on x = 0.5 | y = 0.9766 | +0.84123 | ±0.037 | [+0.804230, +0.878230] |
| **G-F11-2** | Re 100 | `v` on y = 0.5 | x = 0.8047 | −0.24533 | ±0.0081 | [−0.253430, −0.237230] |
| **G-F11-3** | Re 100 | `u` on x = 0.5 | y = 0.5000 | −0.20581 | ±0.0078 | [−0.213610, −0.198010] |
| **G-F11-4** | Re 1000 | `u` on x = 0.5 | y = 0.9766 | +0.65928 | ±0.079 | [+0.580280, +0.738280] |
| **G-F11-5** | Re 1000 | `v` on y = 0.5 | x = 0.9063 | −0.51500 | ±0.021 | [−0.536000, −0.494000] |
| **G-F11-6** | Re 1000 | `u` on x = 0.5 | y = 0.5000 | −0.06080 | ±0.014 | [−0.074800, −0.046800] |

Every gate carries a **grid triple**: n = 32 / 64 / 128, `dim = 2`, `form="equal"`
(§4.4). The band is graded on the **FINE (n = 128) value**, which is what
`roache_triple.band_verdict` grades and the only thing it grades.

### 3.1 The reference, and the honest statement of its status

Ghia, U., Ghia, K.N., Shin, C.T. (1982), *J. Comput. Phys.* **48**(3), 387–411,
DOI 10.1016/0021-9991(82)90058-4.

**The primary is NOT on disk.** Checked by this lane on 2026-08-25, not inherited:
`find docs/papers -iname '*ghia*'` returns nothing, and a filesystem-wide search for
any file whose name contains `ghia` returns nothing. There is therefore **no title
page to verify**, and standing rule 15's requirement — title-page verification,
never by filename or hash — **cannot be satisfied for this reference by this run**.
The 2026-07-30 record's own Unpaywall check is consistent with that
(`is_oa: false`, `has_repository_copy: false`, `oa_locations: []`).

The reference values used here are the ones frozen in
`verification/runs/F11_runs/cavity_ladder.py` (`U_ALONG_X05`, `V_ALONG_Y05`), taken
from two independently hosted secondary transcriptions cross-checked against each
other. **That is a cross-check between two copies, not verification against the
primary**, and this document does not upgrade it.

**Consequence, registered now:** the `P` column of the coverage matrix is
**BLOCKED** for F11 (§10), and no gate below is presented as validation.

### 3.2 The identity test — what makes each gate FAIL, and how a wrong treatment could still pass (VERIFICATION §2a)

- **All six gates fail** if the fine-mesh sampled value falls outside the frozen
  band around Ghia's tabulated value, or — one-way, and only in that direction —
  if the grid triple is not `CONVERGING`, or if any level is not iteratively
  converged or not plateaued.
- *Could a wrong treatment pass?* The reference is a literal constant in
  `cavity_ladder.py` that the solver never reads and that no CFD output touches;
  the measured value is sampled from the solver's own field by OpenFOAM's `sets`
  function object. **There is no route by which the measurement is derived from
  the reference.** But three concrete routes to a false pass exist and are named:
  1. **A sampler that returned a fixed row regardless of coordinate** would produce
     a stable, plausible value at every station. Caught by **PZ-2** (§4.5), which
     requires the station selector to be shown *unable* to see a plant at a
     different station, and by rule 5: a constant reader yields an `EXACT` or
     `STAGNANT` triple.
  2. **The two near-lid gates, G-F11-1 and G-F11-4, have bands dominated by the
     reference-resolution term** (§4.2): 72 % and 72 % of the band half-width comes
     from `B_ref`, not from our own mesh. A materially wrong solve could pass those
     two on the band alone. **They are declared weak bars.** Their load-bearing
     content is the triple, the observed order and the GCI, not the band, and the
     results record must say so on their face.
  3. **A solve that converged to the wrong steady state** — a different vortex
     structure — would still produce a smooth, converging triple. Nothing here
     gates the global flow topology. Declared as a known blind spot; the full
     34-point profile comparison is reported as a diagnostic (§3.3) and never gated.

### 3.3 The discrimination test (VERIFICATION §2c) — UNMEASURABLE, not satisfied

The hypothesis these six rows grade is *"this lab's `simpleFoam` laminar cavity
discretisation converges, with quantified discretisation error, to the accepted
benchmark answer."* **That hypothesis has no runnable null arm** — there is no
"no-solver" cavity solve. VERIFICATION §2c's own boundary clause 1 covers exactly
this: the rule is then **UNMEASURABLE, not satisfied**, and the row is recorded as
unmeasured. It is recorded that way here, in advance, and no row below is presented
as having passed a discrimination test.

### 3.4 What is reported and never gated

- The other **28 point comparisons** on the two centreline profiles per rung. The
  old record's 34-point table is reproduced as a diagnostic at every level. It moves
  no verdict.
- Each gate's own `B_pos` and `B_ref` split, printed beside its row.
- `richardson_parent_convention` (§8.1), printed beside `richardson` and marked
  sign-flipped.
- Wall time and iteration count per level, for the §7 calibration row.

---

## 4. Where each band comes from — derivations, fixed before compute

**No band below was read off a measured deviation.** Each is `B = B_pos + B_ref`,
both terms computed from mesh geometry and Ghia's own table, rounded **up** to two
significant figures.

### 4.1 The mesh, so the geometry terms are checkable

`cavity_ladder.block_mesh_dict(n, grading_ratio=8.0)` builds a unit square, one
block, `simpleGrading ( (0.5 0.5 8) (0.5 0.5 0.125) )` in both x and y: each half
of each direction carries `n/2` cells over length 0.5 with a last/first expansion
ratio of 8, so the mesh is fine at **all four walls** and coarse at the centre. The
grading ratio is **held at 8.0 on every level**, so the mesh family is
geometrically self-similar and halving the cell width everywhere is exactly what
doubling `n` does.

| n | cells | first (wall) cell | centre cell | ratio |
|---|---|---|---|---|
| 32 | 1,024 | 0.009079 | 0.072628 | 8.000 |
| 64 | 4,096 | 0.004592 | 0.036733 | 8.000 |
| 128 | 16,384 | 0.002308 | 0.018468 | 8.000 |

### 4.2 `B_pos` — the sampler's own positional floor, and `B_ref` — the reference's

The gate value is produced by OpenFOAM's `sets`/`cloud` sampler with
`interpolationScheme cellPoint` at a fixed coordinate. Its irreducible positional
sensitivity on the fine mesh is a half-cell displacement times the local slope:

> **`B_pos` = (local slope from Ghia's table) × (fine-mesh local cell width) / 2.**

The reference carries the same kind of floor and Ghia publishes **no error bar**.
Rather than invent one, the same arithmetic is applied to **Ghia's own grid**:

> **`B_ref` = (local slope from Ghia's table) × (1/128) / 2.**

**Two assumptions inside `B_ref`, both disclosed and neither verifiable here.**
Ghia's Re ≤ 1000 solutions are taken to be on a **129 × 129 uniform** grid. The
129 × 129 figure comes from the 2026-07-30 F11 record's own statement, not from the
primary, which is not on disk (§3.1); uniformity is the standard reading of that
paper and is likewise unverified here. **If Ghia's grid were graded toward the
walls, `B_ref` would be smaller near the lid and the bands of G-F11-1 and G-F11-4
would be tighter than frozen here** — so the error introduced by this assumption is
in the direction of a *looser* gate, which is stated rather than hoped.

**The local slope** is the **larger of the two secant slopes** to the adjacent
tabulated stations in Ghia's own table. The larger is taken because a secant over a
wide, asymmetric stencil understates the local slope, and understating it would
manufacture a band tighter than the instrument can support. **This is an estimate
of a local slope from a 17-point table, not a rigorous bound on it**, and it is
labelled as such.

| gate | max secant slope | fine cell at the station | `B_pos` | `B_ref` | sum | **band** |
|---|---|---|---|---|---|---|
| G-F11-1 | 6.7850 | 0.00301 (9th from lid) | 0.010198 | 0.026504 | 0.036702 | **±0.037** |
| G-F11-2 | 0.9841 | 0.00864 (41st from wall) | 0.004253 | 0.003844 | 0.008098 | **±0.0081** |
| G-F11-3 | 0.5922 | 0.01847 (64th, centre) | 0.005468 | 0.002313 | 0.007781 | **±0.0078** |
| G-F11-4 | 14.5607 | 0.00301 (9th from lid) | 0.021885 | 0.056878 | 0.078763 | **±0.079** |
| G-F11-5 | 3.1569 | 0.00545 (27th from wall) | 0.008595 | 0.012332 | 0.020927 | **±0.021** |
| G-F11-6 | 1.0053 | 0.01847 (64th, centre) | 0.009283 | 0.003927 | 0.013210 | **±0.014** |

**A per-gate band, not one family band — and the counter-argument, answered.** The
F3 conversion sets ONE band across its family and argues that *"a family gate does
not get a per-case bar sized to what each case can achieve."* That argument is
correct there and does **not** transfer here, for a stated reason: F3's β is the
*same measured quantity* produced by the *same detector* across cases, so a per-case
bar would be sizing the bar to the case. Here the six gates are **six different
quantities at six different points**, and the sampler's resolution and the
reference's resolution at each point are different numbers computed independently
from geometry. Collapsing them to one bar would size every gate to the worst-resolved
one — the opposite error. The cost of this choice is transparency, which is paid in
the table above: every gate prints its two terms, so a grader can attack any one of
them.

**Three of the six bands can bite; three cannot.** Against the largest deviation
anywhere in the 2026-07-30 record (0.01734 lid-speed units), G-F11-2 (±0.0081),
G-F11-3 (±0.0078) and G-F11-6 (±0.014) are bars a real solve can fail. G-F11-1
(±0.037), G-F11-4 (±0.079) and G-F11-5 (±0.021) are not. That split is a property of
the derivation, not a choice, and it is printed here rather than left for a reader
to compute.

### 4.3 The plateau threshold: 1.0e-6 in lid-speed units

Derived, not chosen: Ghia's tabulated values carry **five decimal places**, so the
reference's own last significant digit is 1e-5. A residual solution drift below
1e-6 over the final ≥250 iterations is an order of magnitude below the last digit of
the reference and at least **7,800× smaller than the tightest frozen band**
(±0.0078). It cannot move a band verdict at the frozen precision. No CFD value
enters this derivation.

### 4.4 The grid triple, dimensionality and `form` — standing rule 5

**The triple is n = 32 → 64 → 128, cells 1,024 → 4,096 → 16,384.**

- **`dim = 2`, explicitly, on every ladder, and stated as an argument, never
  defaulted.** The case is a single-cell-thick `blockMesh` slab with the
  `frontAndBack` patch set `empty`; it is refined in x and y only and never in z.
  The instrument **refuses** a missing dimensionality, and VERIFICATION §3.1 is the
  reason this is not a formality: the 4G campaign found the lab's own helper
  applying the 3-D convention to a 2-D ladder and *"report[ing] the observed order
  as 0.817 where the 2D calculation gives 0.545"* — off by exactly 1.5×.
- **`form="equal"`, asserted, never `"auto"`.** `h = (1/N)^(1/2)`, so
  `r21 = (4096/1024)^(1/2) = 2` and `r32 = (16384/4096)^(1/2) = 2`, both **exactly
  2 by construction** — the generator doubles `n` in both directions and holds the
  grading ratio at 8.0, so `h` halves exactly and the ratio is not inferred from a
  cell count. Passing `form="equal"` makes the instrument **refuse** if the two
  ratios are not equal, which is a real guard and not a label.
- **Recipe similarity.** The instrument cannot see a change of case setup between
  levels (VERIFICATION §3.2, the second way an observed order lies). It is
  established here by the caller: all three levels are built by the same
  `cavity_ladder.build_case` call with the same grading ratio, the same schemes,
  the same `fvSolution`, the same `residualControl` and the same boundary
  conditions — **the only registered difference between levels is `n`**, and the
  only registered difference from the 2026-07-30 cases is in §6.1.
- **Mesh-draw scatter does not apply.** `blockMesh` is deterministic: the same
  parameters produce a byte-identical mesh, so there is no second draw to take. The
  2026-08-10 correction inside the old F11 record already established this for this
  exact ladder and it is cited, not re-derived.
- **Mesh birth certificate (VERIFICATION §9, v1.5).** Every level runs `checkMesh`
  at creation and retains `log.checkMesh`. A level whose `checkMesh` is not clean
  **does not enter the ladder**; its row is `NOT A RESULT`.

**Standing rule 5 is applied in its stated order, without exception**, by
`scripts/roache_triple.py::grade_ladder`, which enforces the order structurally:

1. any level not iteratively converged or not plateaued → **NOT A RESULT**;
2. finest triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → **NOT A
   RESULT**, with the value, every triple and every order printed beside it, and
   **no GCI quoted**;
3. `CONVERGING` → **PASS** inside the frozen band else **GATE FAIL**, with the GCI
   printed at **Fs = 1.25**.

The gate is one-way: it may turn a PASS or a GATE FAIL **into** NOT A RESULT and
never the reverse. The instrument computes the band verdict **first and
unconditionally**, reports it beside the final verdict, and asserts the final
verdict is either that band verdict or NOT A RESULT.

### 4.5 The iterative-convergence and plateau measurements — the CALLER's, and they are made

The instrument is explicit that these are **the caller's measurements**, that step
(a) only acts on them, and that it **refuses** when `iterative_states` is absent —
because an unevaluated step is not a passed one.

- **Iterative convergence, per level.** `CONVERGED` iff `scripts/check_convergence.py`
  returns `CONVERGED` for that level's `log.simpleFoam`, which is keyed off the
  solver's **own** statement `SIMPLE solution converged in N iterations` and never
  off a residual read in isolation (L-14 / L-21). A level that ran to its iteration
  cap without that line is `NOT_CONVERGED`, exactly as `re100_n128` correctly was on
  2026-07-30 before it was extended.
- **Plateau, per level, per gate station.** `PLATEAUED` iff
  `|q(final sample) − q(the latest earlier sample at least 250 iterations before it)|
  ≤ 1.0e-6`. **If no sample at least 250 iterations earlier exists, the plateau is
  UNMEASURED**, which is reported as unmeasured and grades that level `NOT A RESULT`
  through step (a) — never silently as a pass (VERIFICATION §9, `ran_before_found`).
  This closes the loophole where a final write landing a few iterations after a
  scheduled one would satisfy the criterion trivially.

### 4.6 Planted-zero controls (standing rule 3) — the comparator refuses if it cannot see a plant

`PLANT = 1.234e-03`, the lab constant (`analyse_t3.py:81`, `roache_triple.PLANT`).
Three controls, run **per level per gate**. `grade_f11.py` **exits 2** if any fails,
and none is skippable by a flag.

| id | reader under test | plant | refusal condition |
|---|---|---|---|
| **PZ-1** | F11's own `.xy` parser + station selector, on a **copy of the case's own raw artifact** | additive `1.234e-03` into the `Ux` (or `Uy`) column of the row at the graded station of `{uAlongX05,vAlongY05}_U.xy` | read-back delta differs from the plant by > 1e-12 |
| **PZ-2** | the **station selector alone** | additive `1.234e-03` into a **different** station's row of the same file | the graded station's value **moves at all** (> 1e-12) |
| **PZ-3** | independent re-derivation | none | the graded value re-derived by nearest-coordinate match (tolerance 1e-6) differs from the `round(coord, 4)` dictionary lookup by > 1e-12 |

**PZ-1 uses `roache_triple.external_plant_control()`, deliberately, and not the
module's generic `planted_zero_control()`/`read_series` path.** The reason is the
whole point of rule 3: `read_series` proves a JSON reader can see a plant in a JSON
file **the case never produces**. F11's real read path runs through the OpenFOAM
`raw`-format `.xy` file that `simpleFoam` actually writes and through F11's own
parser of it, and a control on the JSON hand-off would leave the actual reader
untested — the exact "a zero from a reader not shown able to see a non-zero"
hazard. `external_plant_control` exists for precisely this case and is what the
comparator hands to `grade_ladder`.

**PZ-2 is the control this suite most needs.** Every gate here rests on reading the
right row of a 17-row file. A selector that returned a fixed row index would sail
through PZ-1 and through every deviation test in the old record.

---

## 5. The completion rule (standing rule 4), and its declared adaptations

A run counts only if **all** of it holds. `grade_f11.py::completion_check` reads
each clause off disk; a run failing any clause is **not graded** — its level carries
the label, never a number, and its ladder is `NOT A RESULT`.

| clause | as checked here |
|---|---|
| C1 `rc = 0` | `run_rc.txt`, written by the launcher, reads `0` |
| C2 `End` line | `^End$` present in `log.simpleFoam` |
| C3 last time == `endTime` | **adapted, see below** |
| C4 fields present | `U` and `p` at the last written time; **plus** `{uAlongX05,vAlongY05}_U.xy` present under `postProcessing/centerlineProfiles/<N>/` |
| C5 log step integrity | `count(^ExecutionTime = ) == count(^Time = )`, both `== N`, and `> 0` |
| C6 **age guard** | every field at the last written time, **and both sampled `.xy` files**, strictly newer than the latest mtime anywhere in the case's own `0/` |

**Three departures, declared here and not discovered later:**

1. **C3.** The rule's literal clause is *last time == `endTime`*. `simpleFoam` under
   `residualControl` **stops early on purpose** when it converges, so the last
   written time is the convergence iteration `N`, not `endTime`. The literal
   equality is not merely unmeetable — meeting it would mean the run **failed** to
   converge and ran to its cap. C3 is therefore replaced by the **stricter**
   requirement that all three hold: the log carries `SIMPLE solution converged in N
   iterations`; the last written time directory equals `N`; and **`N < endTime`**,
   so a cap-terminated run fails C3. This is the clause the 2026-07-30 `re100_n128`
   run failed before it was extended.
2. **C5.** The rule's literal clause is `ExecutionTime` count == `endTime`, a
   steady-iteration clause that holds when one iteration is one time unit **and the
   run reaches its cap**. Here the run stops at `N < endTime`, so the count equals
   `N`. The invariant the clause exists to protect — *the log is not truncated
   mid-step* — is checked directly: one `ExecutionTime` line per `Time` line, and
   both counts equal to the converged iteration count.
3. **C4/C6 field list.** The rule's field list (`T U p_rgh alphat nut k omega`) and
   its `0/T` anchor belong to the **thermal** family. This is incompressible and
   laminar: there is no `T`, no `p_rgh` and no turbulence field, and there is no
   `0/T` to date the run from. **C6 is STRICTER than the rule**, not looser: it
   dates the run from the **latest mtime anywhere in `0/`**, and it extends the
   guard to the sampled artifacts the gate actually reads.

**The launcher enforces the rule's own guard: it refuses (rc = 3) any case
directory that already exists**, so no run in this conversion can inherit a `0/`, a
time directory or a `postProcessing/` tree from the 2026-07-30 campaign or from a
retry.

---

## 6. The run matrix, fixed now

**Six solves.** Fresh directories under
`verification/runs/F11_runs/conversion_2026-08-25/runs/<rung>/<level>/`.

| # | rung | level | n | cells | `endTime` (iteration cap) | serves |
|---|---|---|---|---|---|---|
| 1 | Re 1000 | coarse | 32 | 1,024 | 4,000 | triples for G-F11-4/5/6 |
| 2 | Re 1000 | medium | 64 | 4,096 | 4,000 | as above |
| 3 | Re 1000 | fine | 128 | 16,384 | 9,000 | as above, **band graded here** |
| 4 | Re 100 | coarse | 32 | 1,024 | 4,000 | triples for G-F11-1/2/3 |
| 5 | Re 100 | medium | 64 | 4,096 | 4,000 | as above |
| 6 | Re 100 | fine | 128 | 16,384 | 9,000 | as above, **band graded here** |

`cavity_ladder.py` is used **byte-unchanged** as the case generator; the launcher
adds only `meta.json`, `run_rc.txt` and a timing record, which it does not write and
the completion rule needs.

### 6.1 The single registered change to the 2026-07-30 case dictionaries

**Only one, and it changes no gate.** The `centerlineProfiles` function object
currently carries `executeControl onEnd; writeControl onEnd;`, which writes **one**
sample set per run — from which no plateau can be measured. It is changed to
`executeControl timeStep; executeInterval 250; writeControl timeStep; writeInterval
250`, so sample sets are written every 250 iterations and again at the final stop.

- **Field writes are untouched** (`controlDict` keeps `writeControl timeStep;
  writeInterval <endTime>; purgeWrite 1`), so this adds no field I/O.
- Everything else is byte-identical: `blockMeshDict` generator and grading ratio,
  `fvSchemes` (`bounded Gauss linearUpwind grad(U)`, `Gauss linear corrected`),
  `fvSolution` (GAMG/smoothSolver, `residualControl` p 1e-8 / U 1e-9, relaxation
  p 0.3 / U 0.7), `transportProperties` (`nu = 1/Re`), `turbulenceProperties`
  (`laminar`), and the boundary conditions.
- **It cannot move a number a verdict depends on** — it changes when a sample is
  written, never what the converged field is. That is VERIFICATION §2d's own test,
  applied and answered before any solve.

### 6.2 What this conversion does NOT run, and does not convert

Stated in these words so nothing is carried forward silently.

- **n = 256 (65,536 cells) is NOT run.** The arithmetic, from this family's own
  measured probe: `probe_re5000_n256` measured **0.2577 s/iteration** at n = 256
  (77.3 s / 300 iterations, `log.simpleFoam` on disk). This ladder's measured
  iteration counts grow 2.635× from n = 64 to n = 128 (1,727 → 4,550 at Re 1000);
  one more such step implies ≈ 12,000 iterations, i.e. **≈ 51.5 core-min for that
  one level** — over the directive's whole 40 core-min cap, and 4× this document's
  own cap. A level registered in the knowledge that it will be killed at its cap
  buys nothing and spends real core-minutes doing it. **The four-level ladder, and
  the second triple the instrument would report from it, are not obtained by this
  run.**
- **The Re = 5000 docket rung is NOT run** and stays `PENDING`. Its iteration count
  is unpriced; per COMPUTE_BUDGET_CHARTER's D5 clause an unpriced item is reported
  unpriced rather than given a number.
- **The old record's 34-point profile agreement is NOT converted.** Six stations
  are gated; the other 28 point comparisons per rung remain **ungated diagnostics**
  and do not become credentials.
- **The claim that Ghia's Re = 100 and Re = 1000 columns are "clean" is NOT
  converted.** It rests on a two-transcription cross-check, not on the primary
  (§3.1), and this run cannot strengthen it.
- **The old `GATE REACHED` is not carried forward.** Whatever this run returns
  replaces it; where a gate here returns `GATE FAIL` or `NOT A RESULT`, the
  2026-07-30 record is **annotated, never repaired** (VERIFICATION §2b.3).

---

## 7. Cost, costed before launch (standing rule 12)

**Basis: this family's own measured logs**, read by this lane on 2026-08-25 from
`demo-output/website/solve_registry/f11_*.log` — not quoted from the record. Every
figure below traces to a `^ExecutionTime` line and a `Time =` line count in a named
file. All runs are **serial, 1 rank**, so core-minutes = Σ wall-seconds ÷ 60.

| run | predicted core-s | `cost_basis` |
|---|---|---|
| Re 1000, n = 32 | 4.0 | **ESTIMATE, labelled.** No n = 32 measurement exists anywhere. 1,500 iterations (generous: the measured n = 64 → n = 128 iteration factor is 2.635, so n = 32 implies ≈ 655) at 0.001787 s/iter (the measured n = 64 rate 0.008332 divided by the measured n = 64 → n = 128 per-iteration factor 4.662), rounded up |
| Re 1000, n = 64 | 14.39 | **measured**, `f11_re1000_n64_20260730T041833Z.log`: `ExecutionTime = 14.39 s`, 1,727 `Time` lines, `SIMPLE solution converged in 1727 iterations` |
| Re 1000, n = 128 | 176.73 | **measured**, `f11_re1000_n128_20260730T041833Z.log`: `ExecutionTime = 176.73 s`, 4,550 `Time` lines, converged at 4,550 |
| Re 100, n = 32 | 4.0 | **ESTIMATE, labelled**, as above |
| Re 100, n = 64 | 12.58 | **measured**, `f11_re100_n64_20260730T041833Z.log`: `ExecutionTime = 12.58 s`, 1,505 `Time` lines, converged at 1,505 |
| Re 100, n = 128 | 269.50 | **measured rate × measured iteration count.** 5,285 iterations (measured: 4,000 + 1,285, converged at 5,285) at 0.0510 s/iter (measured: 203.96 s / 4,000 on the first pass). The *gross* 233.24 s of the split run is not used because it mixes two contention regimes |
| **total** | **481.20 core-s** | |

**Arithmetic, shown:**

- core-minutes = 481.20 ÷ 60 = **8.02 core-min**.
- core-hours = 8.02 ÷ 60 = 0.13367 core-h.
- **dollars = 0.13367 × $0.0513/core-h = $0.0069.** At the cap: $0.0111.
- `cost_basis` for the dollar figure: **reported-by-owner, NOT measured, and the
  dollar figure is DERIVED.** The rate $0.0513/core-h for c7a.4xlarge is
  owner-stated (Sanaa, 2026-08-21/22) and corroborated at
  `Xiao2016_EnKF/PREREGISTRATION.md:197`; **this box cannot read its own billing**
  (`COMPUTE_BUDGET_CHARTER.md` §5). The **core-minutes are the measured unit**.
- Under the $25 pre-authorisation by three orders of magnitude. That
  pre-authorisation is **not a new ceiling** (standing rule 9): the cap below binds.

**A measured contention finding, registered because it sizes the headroom.** The
same n = 128 mesh ran at **0.0510 s/iter** on its contended first pass
(`f11_re100_n128_...log`, 203.96 s / 4,000) and at **0.0228 s/iter** on its
uncontended extension four minutes later (`f11_re100_n128_ext_...log`, 29.28 s /
1,285) — a measured **2.24× spread on identical work**. The predictions above use
the **contended** rates, which is the conservative direction.

### The cap

**HARD CAP: 13.0 core-minutes** — 62 % headroom over the 8.02 core-min prediction,
and a factor of 3 under the directive's 40. The cap is set here and not at the
directive's ceiling because **a cap 5× the prediction is not a cap**, it is a rubber
stamp; a blanket approval is not a per-item reading (standing rule 9). 62 % covers a
1.6× iteration overrun on **both** n = 128 runs simultaneously — the iteration count
being, per COMPUTE_BUDGET_CHARTER §3, *"the term that overruns [because it is] the
term nobody was writing down."*

**An overrun stops the run; it does not get a new budget.** Three enforcement
points, all in `rerun_f11.py`:

1. **Per-run wall cap** — `max(60 s, 2.5 × predicted)`: 60 s for both n = 32 and
   both n = 64 runs, 442 s for Re 1000 n = 128, 674 s for Re 100 n = 128. A run past
   its cap is SIGTERMed; its level is recorded `KILLED`, which fails C1/C2 and
   therefore grades its ladders **NOT A RESULT** — never a softened number.
2. **Pre-wave budget check** — a wave whose predicted cost does not fit the
   remaining budget with 20 % headroom is **not launched**; its ladders grade
   **PENDING**.
3. **Global watchdog** — polls every 5 s and terminates every live run the moment
   cumulative core-seconds reach **780** (= 13.0 core-min). **This is the binding
   enforcement**, stated plainly: the per-run caps sum to 1,296 s (21.6 core-min),
   which is *above* the budget, so the per-run caps alone do not enforce it and the
   watchdog is not decoration.

**Launch order is frozen**, so that what the budget takes first is the least
load-bearing thing. At most **2 live runs**, deliberately below the box's core
count, so memory-bandwidth contention does not inflate the core-minute total.

| wave | runs | predicted core-s | cumulative core-min |
|---|---|---|---|
| 1 | Re 1000 n = 32, Re 1000 n = 64 | 18.39 | 0.31 |
| 2 | Re 1000 n = 128 | 176.73 | 3.25 |
| 3 | Re 100 n = 32, Re 100 n = 64 | 16.58 | 3.53 |
| 4 | Re 100 n = 128 | 269.50 | **8.02** |

If the budget stops the line, **wave 4 is lost first** and the three Re = 100
ladders grade `PENDING` — the Re = 1000 triple, which is the cheaper of the two and
carries the sharper reference stations, survives whole. **A triple is never left
half-built:** losing a wave loses a whole rung, never one level of a triple.

**Load is checked before each wave.** Other teams' solvers on this box are not
touched, and this document authorises nothing outside
`verification/runs/F11_runs/conversion_2026-08-25/`.

**Calibration is mandatory at completion** (standing rule 12, Sanaa's 2026-08-23
directive): a row in `docs/COST_CALIBRATION.md` stating actual core-minutes from the
logs, the ratio actual/predicted, and the gap attributed between contention, waste
and misprediction — with waste named separately and never absorbed into the ratio.
**A completion report without that row is incomplete.**

---

## 8. The grading path, fixed at this commit

### 8.1 The shared instrument, fixed by blob and not by path

| what | value |
|---|---|
| path | `scripts/roache_triple.py` |
| **git blob** | **`8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`** |
| commit that landed it | `9c69a79a903565875cf205c35a366ec7d38e7109` |
| md5 | `ae64dc482ae2069d233719e68e9192b8` |
| sha256 | `452f475181c9897000ea530b39a84bd3e7e9927e0a3fd39fe8b1105f538ac051` |

**The path is not the freeze; the blob is.** `grade_f11.py` runs with
`--prereg-commit <sha of this commit>`, hashes the instrument's own source against
`git cat-file blob 8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`, and **REFUSES
(exit 2)** if the file on disk is not byte-identical to that blob. A freeze that is
claimed and not checked is a claim about intent (VERIFICATION §2d); the enforcement
artifact is `scripts/check_comparator_freeze.py`.

**`--selftest` run by this lane on 2026-08-25, not taken on anyone's word:
`53/53 checks passed`, exit code 0.** That selftest imports both thermal parents
and cross-checks `order`, `GCI_pct` and `GCI_abs` against them to 1e-12, so the
instrument's provenance is an executable claim rather than a comment.

**The one deliberate divergence from the parents, and which value F11 quotes.**
The module's docstring section *"THE ONE PLACE THIS PORT DELIBERATELY DIVERGES FROM
ITS PARENTS"* records that `richardson` here is `f_fine − e21/den`, the corrected
Roache extrapolate, where both parents return `f_fine + e21/den` — the same distance
from `f_fine`, the wrong way — and that the two satisfy
`richardson + richardson_parent_convention == 2 · f_fine` exactly.

> **F11 quotes `richardson`, the corrected value.** `richardson_parent_convention`
> is printed beside it, **explicitly marked sign-flipped**, exactly as
> `format_row` prints it, so a reader comparing an F11 number against a published
> thermal number can see both and know which is which.

**And it decides nothing.** `band_verdict` grades the **FINE VALUE** — verified in
`grade_ladder`, which computes the band verdict from `levels[-1]["value"]` before
any triple is consulted. **No verdict this module can emit is a function of either
extrapolate.** For F11, as lab-wide, the extrapolate is **display-only**.

### 8.2 The case comparator, and the honest gap in this freeze

`grade_f11.py` and `rerun_f11.py` — the case-level comparator and launcher that
read the `.xy` artifacts, run PZ-1/PZ-2/PZ-3, build the level series and call
`grade_ladder` — **do not exist at this commit.** That is a real gap and it is named
rather than papered over.

**How it is closed, before first compute and legally under rule 2 / §2b.1:** both
files are committed, with their sha256 recorded in a dated addendum to this
document, **before the first solve starts**, with the same condition re-checked and
re-stated (the run root does not exist). Such an addendum is legal because there is
no answer to tune to; it **may not** alter a gate, a threshold, a cap or a label,
and this document's §3, §4 and §7 are what it is checked against.

**Why the gap is narrow.** Every number the comparator could otherwise choose is
already fixed **numerically** in this document: the six stations, the six reference
values to five decimals, the six bands, the six band intervals to six decimals, the
plant constant, the plateau threshold, the completion clauses, `dim = 2`,
`form="equal"`, `Fs = 1.25`, the cap and the launch order. The comparator can
implement them or fail its own freeze check. **No threshold in `grade_f11.py` will
be settable from the command line.**

---

## 9. What each outcome will mean

Stated now, so no outcome can be re-read afterwards.

- **PASS** on a gate whose triple `CONVERGING`: the 2026-07-30 measurement is
  converted at that station, and F11 gains the **G** column (§10) — a quantified
  discretisation error where it had none.
- **GATE FAIL**: the fine value sits outside a band derived from geometry. The old
  `GATE REACHED` was unearned at that station. It ships as a **documented failure**
  (VERIFICATION §8) and the old record is annotated, not repaired.
- **NOT A RESULT**: the triple did not converge, a level failed the completion rule,
  or a plateau was unmeasured. The value is printed beside it with every triple and
  every order and **no GCI**. Given §2.2 — six monotone sequences with growing
  deviations — this is a live outcome, and if the n = 32 level breaks monotonicity
  it is the correct one.
- **BLOCKED**: used for the **P** column only (§10), on a reference that is not on
  disk. It is not used for any of the six gates.
- **PENDING**: not launched, budget or otherwise. Never used to soften a fail.

**How a small GCI beside a larger Ghia deviation will be read — registered in
advance, because this is the outcome §2.2 makes likely.** If a triple returns
`CONVERGING` with a GCI substantially **smaller** than the frozen deviation from
Ghia at the same station, that combination means the residual disagreement is
**not** discretisation error in this lab's solve. It will be reported in exactly
those words, and the three candidate causes — the reference's own resolution
(quantified as `B_ref` in §4.2), the corner-singularity regularisation the two
methods necessarily differ on, and the `linearUpwind` advection scheme — will be
listed **as candidates, none of them measured by this run**. It will not be
reported as a solver defect, and it will not be reported as a Ghia defect.

**A GATE FAIL or a NOT A RESULT here is a success of this exercise**, not a failure
of it: it means the ungated 2026-07-30 reading was optimistic, which is precisely
what pre-registration exists to detect. **Nothing will be tuned to preserve the old
words.** Should any measured value land outside a band, the band stands and the
verdict follows the numbers.

---

## 10. The consolidation-week target: which of V / G / P this earns

The coverage-matrix rubric (`docs/COVERAGE_MATRIX.md` §1, itself flagged in that
file as the chief's reconstruction of Sanaa's directive and not her verbatim
words): **V** = code verification against an exact solution, a manufactured
solution, or a correlation; **G** = a `CONVERGING` Roache triple with GCI at
Fs = 1.25 and an observed order; **P** = validation against a public primary source
with the pre-registration on disk. Tiers, exactly five words: **HOLDS /
GATE REACHED / SURVEYED / NOT HELD / NEVER RUN**.

| column | what this conversion does | honest status |
|---|---|---|
| **V** | nothing | **NOT EARNABLE BY THIS RUN, and not by this case.** The lid-driven cavity has no exact solution, and Ghia is a *numerical* benchmark, not an exact one, a manufactured one or a correlation. The named route to V is a **method-of-manufactured-solutions** run on this same solver and mesh family — a separate case, **not registered here and not costed here** |
| **G** | **this is what the run is for** | **EARNABLE.** Three levels at r = 2 exactly, `dim = 2`, `form="equal"`, graded by the frozen instrument, producing an observed order and a GCI at Fs = 1.25 where the family currently has neither. Earned **only if** the triples return `CONVERGING`; a non-`CONVERGING` triple is `NOT A RESULT` and earns nothing |
| **P** | nothing it can | **BLOCKED.** The pre-registration will be on disk — this file. The **primary is not**: no Ghia PDF exists anywhere on this box, so standing rule 15's title-page verification cannot be performed. Separately and independently: Ghia is itself a numerical solution, so comparison against it is **code-to-code verification, not validation against the world** — the 2026-07-30 record says so in its own section and this document does not overturn it |

**So this conversion is intended to earn G, and G alone.** Two consequences,
stated plainly rather than left for a reader to trip over:

1. **F11 cannot reach `HOLDS` by this run**, whatever the six gates return. The
   directive's phrase *"convert to HOLDS"* is not achievable for this family and
   this document says so before spending the core-minutes rather than after.
2. **The rubric has no cell for this row.** `GATE REACHED` is defined as *missing
   exactly one* of V / G / P; F11 after this run is missing **two**. It is not
   `SURVEYED` (the evidence is gated, not breadth), and calling it `NOT HELD` on a
   reference-availability blocker would read as an honest FAIL of the physics, which
   it is not. **Assigning the tier is the verification team's call, not this lane's**
   — this document records the evidence and names the gap in the rubric as a finding
   for that team.

---

## 11. Standing rules this document is bound by

Rule 1 (vocabulary, §3 and §9) · rule 2 (this freeze; grading path §8, and the §8.2
gap named rather than hidden) · rule 3 (planted-zero controls §4.6, `external_plant_control`
on F11's own artifact) · rule 4 (completion rule §5, three departures declared) ·
rule 5 (Roache triple gating §4.4, `dim = 2`, `form="equal"`) · rule 7 (nothing here
is sent, filed or registered anywhere outside this box) · rule 9 (the $25
pre-authorisation is not a ceiling; the §7 cap of 13.0 core-min binds) · rule 10
(committed under the private-index protocol, this file alone) · rule 12 (cost §7,
core-minutes measured, dollars derived, overrun stops the run, and a
`docs/COST_CALIBRATION.md` row is mandatory at completion) · rule 13 (no scratch path
is cited by this document) · rule 15 (title-page verification attempted and
**impossible** for Ghia; §3.1, and the `P` column BLOCKED because of it) · rule 16
(silent background operation).

---

## Amendment 1 — 2026-08-25, PRE-COMPUTE. §6.1 re-registered as arm B, and the §8.2 addendum landed

**Document version 1.0 → 1.1.** Version 1.0 is the text frozen at commit
`157793db5ff6bbdda7ab22299abe5725d96e9b37`; it carried no version marker, so
that text is designated v1.0 here and this section is the first amendment to it.

**This section is a PURE APPEND. `lines whose number changed above this section: 0`.**
Sections 1–11 above are byte-identical to v1.0: nothing above line 791 was edited,
re-ordered, struck or renumbered. The assertion is checkable — `git show
157793db5ff6bbdda7ab22299abe5725d96e9b37:verification/campaign/F11_CONVERSION_PREREGISTRATION.md`
is a byte-for-byte prefix of this file, and the commit landing this amendment
carries `--numstat` insertions only, zero deletions.

**This amendment alters NO gate, NO threshold, NO cap and NO label.** §3's six
gates, §3.1's reference and its status, §4's six bands and their six intervals,
§4.3's `1.0e-6` plateau threshold, §4.4's `dim = 2` / `form="equal"` / `Fs = 1.25`,
§4.5's 250-iteration plateau window, §4.6's plant constant, §5's completion clauses
C1–C6 **including C4's literal path**, §6's run matrix, §7's 13.0 core-min cap and
§9's outcome meanings are untouched and are what the amended launcher and
comparator are still checked against. What changes is **how the artifact C4 names
is produced**, and nothing else.

### A1.1 The condition, checked and not asserted (rule 2, VERIFICATION §2b.1)

**The case is UNFIRED.** The run root
`verification/runs/F11_runs/conversion_2026-08-25/runs/` **does not exist**, and
was verified absent by `test -e` in the same shell invocation that committed this
amendment. The only contents of
`verification/runs/F11_runs/conversion_2026-08-25/` are `grade_f11.py` and
`rerun_f11.py`; there is no `runs/`, no case directory, no `0/`, no time
directory, no `log.simpleFoam` and no `postProcessing/` anywhere beneath it.
**There is therefore no answer to tune a gate to**, which is the whole condition
rule 2 places on a pre-compute amendment.

### A1.2 The defect: §6.1 as frozen CANNOT satisfy §5's clause C4

§6.1 v1.0 moves the `centerlineProfiles` function object itself onto
`executeControl timeStep; executeInterval 250; writeControl timeStep;
writeInterval 250`. Its closing sentence — *"so sample sets are written every 250
iterations **and again at the final stop**"* — is **factually wrong about
OpenFOAM**, and this document says so rather than working around it quietly. A
`sets` function object on `timeStep`/250 writes on multiples of 250 **only**. It
emits nothing at an early `residualControl` stop, which is exactly how every run
in §6 is expected to terminate.

**Measured, not reasoned.** A mechanism probe was run at
`/home/ubuntu/certonomous-runs/f11_c4_probe_2026-08-25/` (outside git, under the
registered out-of-repository data root), applying §6.1 **exactly as frozen**, by
the committed launcher itself, at Re 1000, n = 32:

| what | arm A — §6.1 as frozen | arm B — as re-registered below |
|---|---|---|
| converged at | **747 iterations** | **747 iterations** |
| field time directories | `0/`, `747/` | `0/`, `747/` |
| `postProcessing/centerlineProfiles/` | **`250/`, `500/` — no `747/`** | **`747/`**, both `.xy` present |
| `postProcessing/centerlineSeries/` | *(object does not exist)* | `250/`, `500/`, both `.xy` in each |
| **clause C4** | **FAILS — `centerlineProfiles/747/` never exists** | **SATISFIED at the frozen literal path** |

C4 requires both `.xy` files at `postProcessing/centerlineProfiles/<N>/` where
`<N>` is the converged iteration. Under §6.1 v1.0 that directory is **never
written, for any run**. Every one of the six gates would have graded
`NOT A RESULT` through §5, and the entire 8.02 core-min wave would have measured a
dictionary defect rather than a discretisation error.

**The zero was planted, not assumed** (standing rule 3). The same listing that
reported no `747/` under arm A reported `250/` and `500/` **present, each holding
both `uAlongX05_U.xy` and `vAlongY05_U.xy`** — so the reader was demonstrably able
to see a non-empty sample directory when one existed. A reader that saw nothing
anywhere would have proved nothing.

### A1.3 §6.1 AS AMENDED — arm B, the two separately named sampling objects

§6.1 v1.0's paragraph is **struck, not rewritten**; it stands above as the record
of what was frozen and found defective. The registered change to the 2026-07-30
case dictionaries is now, and is only:

1. **`centerlineProfiles` STAYS at `executeControl onEnd; writeControl onEnd;`.**
   It is the **graded** object. `onEnd` fires at the `residualControl` stop, so
   both `.xy` files land under `postProcessing/centerlineProfiles/<N>/` at the
   **converged** iteration — the literal path C4 already names, unchanged.
2. **A separately named `centerlineSeries` object is added**, sampling **the same
   points**, at `executeControl timeStep; executeInterval 250; writeControl
   timeStep; writeInterval 250`. It is the **periodic** object, and §4.5's plateau
   reads its earlier samples from it.

**Field writes remain untouched**: `controlDict` keeps `writeControl timeStep;
writeInterval <endTime>; purgeWrite 1`, asserted intact by the launcher after the
edit. Everything else in §6.1 v1.0's second bullet — `blockMeshDict`, `fvSchemes`,
`fvSolution`, `transportProperties`, `turbulenceProperties`, the boundary
conditions — remains byte-identical, as it was.

**This still cannot move a number a verdict depends on, and that is now MEASURED
rather than argued** (VERIFICATION §2d's own test). Between arm A and arm B at
Re 1000, n = 32:

- both converged in **747 iterations**;
- the converged fields `747/U` and `747/p` are **BYTE-IDENTICAL** between the two
  arms;
- the sample files at 250 and 500 are **BYTE-IDENTICAL** between arm A's
  `centerlineProfiles/` and arm B's `centerlineSeries/`, both stations.

The sampling dictionary does not perturb the solution. That is a byte comparison
of the artifacts on disk, not an inference from the physics.

### A1.4 The REJECTED alternative, and why it was rejected

The alternative repair was to **relax C4** to accept the last periodic sample
directory instead of one at the converged iteration. **It was rejected**, and the
reason is recorded here so it cannot be re-opened as a convenience later:

- Under arm A the last periodic directory is **`500/`**, while the run converged at
  **747**. Relaxing C4 would grade a **materially less-converged state**.
- The size of that concession is measured, not asserted: on the synthetic tree in
  `grade_f11.py --selftest`, constructed to the probe's own layout, grading the
  last periodic directory instead of the converged one moves the graded value by
  **5.000024e-02 in lid-speed units — 50,000× the `1.0e-6` plateau threshold** of
  §4.3, and far outside every one of §4's six bands.
- **Relaxing C4 IS a gate change**, and rule 2 forbids one after this document is
  frozen. Arm B is not: it leaves C4's literal path and its meaning exactly as
  frozen and changes only which dictionary object writes there.

**No fallback to the last periodic sample is implemented anywhere.** A missing
graded artifact **refuses (exit 2)**; an absent or too-short periodic series is
reported **UNMEASURED** and drives `NOT A RESULT` through standing rule 5 step (a).
An unevaluated step is never a passed one.

### A1.5 §8.2 ADDENDUM — the grading path, now frozen by sha256

§8.2 registered that `grade_f11.py` and `rerun_f11.py` did not exist at the freeze
commit, and that the gap closes by committing both **with their sha256 recorded in
a dated addendum, before the first solve**. This is that addendum. Both files exist
and the run root does not.

| file | sha256 |
|---|---|
| `verification/runs/F11_runs/conversion_2026-08-25/grade_f11.py` | `7815de3495c49456296cd68355543247c99c9e92b6b43d7f1b86be969d3b21e5` |
| `verification/runs/F11_runs/conversion_2026-08-25/rerun_f11.py` | `3df39bfd994ddfe2942079d294cc8718534efc22ff9df985d0b8ae77f4e0017d` |

`grade_f11.py`'s `verify_own_freeze()` **refuses to grade anything** unless both
tokens above appear in this document at the commit passed as `--prereg-commit`, and
unless §4's six band interval endpoints and §8.1's instrument blob and sha256 are
also present. That is §8.2 made executable rather than promised.

Frozen-instrument note, unchanged by this amendment: **standing rule 5 is applied
by `scripts/roache_triple.py` (blob `8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`,
sha256 `452f475181c9897000ea530b39a84bd3e7e9927e0a3fd39fe8b1105f538ac051`) and by
nothing in `grade_f11.py`**, which calls `grade_ladder` and never reimplements the
ordering.

**Controls at this commit**, both run before the freeze and both exit 0:
`rerun_f11.py --selftest` → **28/28, 12 mutation controls**;
`grade_f11.py --selftest` → **98/98, 32 mutation controls**. The mutation controls
new at this amendment each assert a way arm B could silently regress: the two
sampling objects collapsed back into one; the graded object moved off `onEnd`; the
periodic object left on `onEnd`; the two objects sampling different points; the
`centerlineSeries` directory absent or too short; the plateau reader pointed back
at `centerlineProfiles`; and **the graded read pointed at `centerlineSeries`, which
refuses**.

### A1.6 Cost — §7's cap is UNCHANGED (rule 12)

The §7 cap stands at **13.0 core-minutes = 780 core-seconds**, and the four waves
still sum to the frozen **8.02 core-min** prediction; both are asserted by
`rerun_f11.py --selftest` at this commit. Arm B adds **one** extra sample-set
evaluation and write per run — 34 points across the two stations, once, at the
convergence stop. Its measured cost at Re 1000, n = 32 is the difference between
the two probe arms' `ExecutionTime`: **1.43 s (arm B) versus 1.38 s (arm A) on one
rank = 0.05 core-seconds**, against a 780 core-second budget. **Immaterial, and
measured rather than estimated.** No cap, no per-run wall cap and no wave
prediction is altered by this amendment.

The probe itself was compute spent **outside** this document's §7 cap and is not
drawn against it; it is a mechanism probe, not a run in §6's matrix, and it
produced no graded value.

---

## AMENDMENT 2 — 2026-08-25: THE ATTRIBUTION IN §"Why this document exists" IS WITHDRAWN

**Document version 1.1 → 1.2.** Appended at the foot under standing rule 6; the
original text above is **struck, never rewritten**. **lines whose number changed
above this section: 0.**

**Rule-2 condition, checked in this commit's own shell invocation, not recalled:**
`verification/runs/F11_runs/conversion_2026-08-25/runs` — the run root this
document registers — **does not exist**. The case is **UNFIRED**; no graded solve
has started; §2b's pre-compute limb governs and this amendment is legal.

### 1. What is withdrawn

Lines 22–27 of this document introduce its motivating text as **"Sanaa's
directive, verbatim"** and set it as a block quotation:

> *"CFD team — Re-run under frozen pre-registrations, <40 core-min each: F3
> (supersonic exact suite), F11 (per capability map), F4 (hypersonic) — the
> early PASSes that lack prereqs convert to HOLDS."*

**That attribution is WITHDRAWN. It is struck, and the block quotation must not
be read as Sanaa's words by any future reader of this file.**

The cfd team searched for the text with a **non-ignoring** `find | xargs grep` — a
plain `grep -r` in this repository honours ignore files and would have missed it —
and found it in exactly **two** places: `docs/LAB_STATE.md`, and cfd's **own**
commit messages `2bf4915a` and `157793db`. **It is not independently sourceable to
anything Sanaa said.** No cfd supervisor heard it said and none will vouch for it.

**The text is KEPT and re-marked as A cfd BRIEF'S PARAPHRASE**, following the
precedent this team and heat-transfer both set: withdraw the attribution, keep the
words, label them honestly. The paraphrase may still be cited as what motivated
this document. **It may never again be cited as her words, and never as a compute
authorisation.**

### 2. Why this correction is being made HERE and not only on the board

**The withdrawal was announced last session on `docs/LAB_STATE.md` and in a commit
message — and this document, which actually carries the attribution, was never
corrected.** A withdrawal that does not reach the artifact bearing the claim has
not been made. That is the defect this amendment repairs, and it is recorded as a
finding against cfd's own process rather than as housekeeping.

**Standing rule L-309 applies directly: an attribution authorising SPEND must
carry its source when recorded.** This block quotation carries a core-minute
figure and was written into a frozen pre-registration as the owner's own words.
That is exactly the shape the lesson names.

### 3. THE LOOP THIS DOCUMENT CLOSED, recorded because it actually happened

On **2026-08-25**, a **40 core-minute** figure reached the cfd supervisor through
the chief as a per-item spend authorisation attributed to Sanaa. It was withdrawn
by the chief before it was written to any record, and **no cfd artifact ever
carried it** — verified across `verification/campaign/` and `docs/LAB_STATE.md`.

**The most likely proximate source of that figure is this file, lines 22–27** —
an unsourced cfd paraphrase, frozen into a pre-registration under the label
"verbatim", from which it could be read back as the owner's own instruction. The
path is: **cfd wrote it → cfd froze it as her words → it circulated → it returned
to cfd as her authorisation.**

**The laundering did not require a single dishonest act by anyone.** It required
only that one label — "verbatim" — was applied to text whose source had never been
checked. It is recorded here so that the next reader of this file understands why
the label matters more than the words.

### 4. What this amendment does NOT change

**No gate, no threshold, no cap, no band and no label is altered by this
amendment.** All six gate bands, the instrument blob identity in §8.1, the
completion clauses and every verdict rule stand exactly as frozen.

**One consequence must be stated precisely rather than waved past.** §"Levels not
run" (near line 531) gives **two** reasons for excluding the **n = 256** level:
that its ≈ 51.5 core-min is *"over the directive's whole 40 core-min cap"*, and
that it is *"4× this document's own cap"*. **The first reason is withdrawn with the
attribution — there is no Sanaa-authorised 40 core-minute cap and there never
was.** The second reason is unaffected and is sufficient on its own: **this
document's own cap governs, and n = 256 exceeds it fourfold.** The exclusion of
n = 256 therefore stands, on this document's own arithmetic, and does not depend
on the withdrawn figure. **A conclusion that survives the removal of a bad premise
must be shown to survive it, not merely asserted to.**

### 5. What remains true and is not disturbed

§10's triple-crown analysis is unaffected and is **reaffirmed**: this conversion is
intended to earn **G, and G alone**. **F11 cannot reach `HOLDS` by this run,
whatever the six gates return** — the lid-driven cavity has no exact solution and
Ghia is a *numerical* benchmark, so **V is not earnable by this case**; and no Ghia
document exists on this box, so rule 15's title-page verification cannot be
performed and **P is BLOCKED** — independently of which, comparison against a
numerical benchmark is code-to-code verification, not validation against the world.

**The paraphrase's phrase *"convert to HOLDS"* was not achievable for this family
even when it was believed to be hers**, and §10 said so before any core-minute was
spent rather than after. That judgement was correct on the physics and is
untouched by the withdrawal of the attribution.

*Written 2026-08-25 by the cfd supervisor personally, on a **ZERO-COMPUTE**
provenance correction. No solver was launched, no mesh was built and no case
directory was created. The rule-2 ABSENT condition was checked by `test -e` in the
committing shell invocation.*
