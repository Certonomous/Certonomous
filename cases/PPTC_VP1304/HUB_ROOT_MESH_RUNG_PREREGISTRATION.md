# PPTC VP1304 — MESH REPAIR RUNG: PRE-REGISTRATION

**FROZEN 2026-09-13 by cfd-supervisor. This commit IS the freeze and discharges standing
check 4 (pre-registration committed before compute). The gates, thresholds, cap and labels
below are closed as of this commit; changes land only as dated addenda that cannot alter
them. THE RUNG MAY NOW BUILD.** Companion to the frozen act pre-registration
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` (Amendment 4 at commit
`c0cd9038f`, blob `6a27740da10c77d813bbe94db564d0fbee5b03b4`). **This rung adds no gate to
that document and alters none of its gates, thresholds, caps or labels.** It registers a
mesh-build variant and its own gate.

**Status: pre-compute for this rung.** No mesh of this variant exists. *How that was
checked:* `/home/ubuntu/certonomous-runs/PPTC_VP1304/` contains no directory for this
variant, and the reader was shown able to see one — the identical listing returns the six
existing build directories (`F360_coarse`, `L1_cm1`, `L1_prod7`, `L1_prod7s`, `L2_prod7s`,
`SMOKE360_J0.7985`).

---

## 1. THE PREMISE THIS RUNG WAS RULED IN ON, AND THE MEASUREMENT THAT PARTLY REFUTES IT

The rung was ruled in on the **geographic** localisation of the 316 negative-volume cells in
`F360_coarse`: 217 of 316 within |x| < 20 mm of the propeller plane, r = 0–75.7 mm, spread
over 357.2° of azimuth, on SVA's closed-hub-fillet CAD with the fillet resolved at 2.3 cells
across the leading-edge radius. That reading pointed at the **hub/blade-root junction**.

**Before drafting a prediction I measured the refinement level of those cells, and it does
not support the blade root.** Instruments: `constant/polyMesh/{cellLevel,owner,neighbour}`
and the `zeroVolumeCells` set of the staged case. The `cellLevel` reader was controlled
against snappyHexMesh's own "Cells per refinement level" block and matched on all six levels
(83820 / 18960 / 79680 / 212280 / 18532547 / 772748).

| measurement | value | baseline | enrichment |
|---|---|---|---|
| bad cells at refinement level 5 (the blade surface level) | **0 of 316** | 3.92% of mesh | **0.0×** |
| bad cells at refinement level 4 | 316 of 316 | 94.07% | 1.1× |
| bad cells with a face-neighbour at level 5 | **0 of 316** | 0.54% of level-4 faces | **0.0×** |
| bad cells touching **any** refinement-level jump | 191 of 316 (60.4%) | 6.60% | **9.2×** |
| their faces that are a **4↔3** jump | 206 of 1558 (13.2%) | 0.42% | **31.2×** |

**MY OWN HYPOTHESIS — that the 5↔4 transition wrapping each blade was the mechanism — IS
REFUTED BY ITS OWN TEST: not one of the 316 cells touches a level-5 cell.** The blade
surface is excluded. What the population *is* enriched on, by **31.2×**, is the **4↔3**
transition. And it is not a complete explanation either: **39.6% (125 of 316) sit on no
refinement transition at all.** A transition is neither necessary nor sufficient here, which
is the same shape as the already-registered N-X5 finding in
`CONCAVE_CELL_PREDICTION_REGISTRATION.md` §2.

**This is disclosed rather than smoothed over, and the supervisor may re-rule on it.** The
registered change below follows the 31.2× measurement, not the geographic reading.

## 2. THE ONE REGISTERED CHANGE

> **`refinementSurfaces { shaft { level (3 3); } }` becomes `level (4 4);` in
> `cases/PPTC_VP1304/mesh/` — and nothing else changes.**

Level 3 is the only wall level below 4 inside the level-4 refinement regions
(`bladeRegion`, radius 0.1325 m, x ∈ [−0.100, +0.060]; `tipVortex`, radius 0.130 m,
x ∈ [−0.250, +0.030]). Raising `shaft` to 4 removes the 4↔3 transition from the interior of
those regions, which is the transition the population is 31.2× enriched on.

**Explicitly NOT bundled:** the 70× layer-thickness collapse (snappy asks 1.79e-06 m
near-wall on blades against the 1.256e-4 m its own dictionary implies, and 17× below its own
`minThickness` floor of 3.125e-5 m). That is a separate lead on a separate lane and merging
the two would make neither testable. `blades` stays at 5, `hub` and `cap` stay at 4,
`shaftExtension` stays at 2, the layer dictionary is untouched, and the domain, MRF zone,
solver and comparator are untouched.

## 3. THE GATE — THE MATRIX PROPERTY ITSELF, NOT A SOLVER'S BEHAVIOUR

### 3.1 What this lane and its supervisor both got wrong, retracted here before the freeze

Both of us claimed that a DIC-preconditioned CG amplifying its residual is *arithmetic proof*
that the pressure Laplacian is not SPD. **That is wrong and it is retracted. The conjugate
gradient method minimises the error in the A-norm, not the residual norm; ‖r‖ is not monotone
in CG even on a perfectly SPD system**, and routinely rises before falling under a weak
preconditioner. Residual growth is therefore **evidence, not proof**. The completed probe
shows exactly the non-monotone pattern the theory predicts: 8 solves, 3 amplifying
(1 → 1.7856178; 0.33124386 → 0.55437931; 0.99998897 → 3.8260438) and 5 reducing.

### 3.2 THE GATE (blocking) — direct, solver-free, and it yields a witness

> On the built mesh, for every internal face compute the Laplacian weight
> **w_f = |S_f|² / (S_f · d_f)**, with `S_f` the outward face-area vector of the owner and
> **d_f = C_N − C_P** the owner-to-neighbour cell-centre vector. Form the zero-row-sum
> symmetric operator `A` with off-diagonals `−w_f` and `A_PP = Σ_f w_f`.
>
> **GATE FAIL if any `w_f ≤ 0`, or if any cell diagonal `A_PP ≤ 0`.**
> **PASS if every `w_f > 0`.**

**Why this is a proof and the CG test is not.** For a zero-row-sum symmetric Laplacian,
`xᵀAx = Σ_f w_f (x_P − x_N)²`. If every `w_f > 0` the form is positive semi-definite by
inspection. If some cell has `A_PP ≤ 0`, then **x = e_P is an explicit witness with
`xᵀAx = A_PP ≤ 0`** — a constructed counterexample to positive-definiteness, not an
inference from a solver's behaviour. **The gate must report the witness cell index and the
value of `A_PP`, or it has not fired.** `S_f · d_f ≤ 0` — a face-area vector pointing against
the owner-to-neighbour direction — is the mechanism that produces `w_f ≤ 0`, and a flipped
face area is exactly what an inverted cell supplies.

**Instrument:** a script under `verification/runs/PPTC_VP1304_runs/`, reading
`constant/polyMesh/{points,faces,owner,neighbour}` only. It must be shown able to return a
non-zero before its zero is believed (CLAUDE.md rule 3): it is run first on a deliberately
inverted two-cell mesh and must report that face.

### 3.2a SAME-MESH ASSERT — BINDING ON EVERY PAIRED OR DIFFERENCED QUANTITY IN THIS RUNG

> **Every paired or differenced quantity in this rung must assert, IN THE SAME INVOCATION AS
> THE COMPARISON, that its arrays have equal length and that the length equals the cell or
> face count of the mesh being graded. A comparison that cannot show this assert did not
> happen.**

**The same-invocation requirement is not decoration**, and it is there for the reason
CLAUDE.md rule 10 gives about capturing HEAD once: a check performed in a separate step is a
check against a state that may no longer hold when the comparison runs.

**Why this rung needs it more than most.** `P1`, `P3`, `P4`, `P6` and `P7` all compare the
rebuilt mesh against `F360_coarse` baselines, and **the rebuilt mesh will have a different
cell count by construction** — raising `shaft` to level 4 adds cells. So a cross-mesh pairing
here is not a risk, it is **the expected condition unless something refuses it**, and it
would yield **a plausible number rather than an error**: all five predictions would read
cleanly and all five would be wrong.

**Provenance — this clause was paid for twice in one night, by both agents on this rung.**
A supervisor's verification of §3.3 paired `minPyrVolume` from `F360_coarse` (19,700,035
cells) against `cellVolume` from `L2_prod7s` (13,103,459 cells) and got a clean-looking
confirmation; it was caught only because the two array lengths disagreed *and happened to be
printed*. This lane's own §3.3 measurement was correct **only because both paths were built
from one hardcoded directory variable — safe by construction, not by an assert** — and
nothing in it would have caught the error had the paths differed. **Neither agent had a
check; one of them had luck.**

### 3.3 SUPPORTING MEASUREMENT ALREADY ON DISK — and it shows the volume gate understates the damage

Measured on `F360_coarse` from `0/minPyrVolume` and `0/cellVolume`, both readers first
controlled against `checkMesh`'s own printed numbers (minimum cell volume `−5.7249909e-10`
and count `316`, matched exactly):

| quantity | value |
|---|---|
| cells with **minimum face-pyramid volume ≤ 0** | **1,028** (0.00522% of the mesh) |
| minimum face-pyramid volume | **−1.6626933e-09 m³** |
| of those, cells that are also negative-volume | 316 |
| **of those, cells with POSITIVE volume and an inverted face** | **712** |
| **cells with negative volume but a POSITIVE pyramid** | **0** |

**The last row is the load-bearing one: the 316 negative-volume cells are a STRICT SUBSET of
the 1,028 inverted-pyramid cells.** The volume gate does not catch a single cell the pyramid
test misses. That forecloses the natural defence — that the two tests are different views
catching different things. **They are not. One is a proper subset of the other, so the gate
this lab has been quoting sees 30.7% of what exists, with no compensating coverage
anywhere.**

**The lab's min-cell-volume gate sees 316 of these 1,028 cells. It misses 712 — a population
3.25× larger than the one it catches — because those cells have positive volume and an
inverted face pyramid.** A non-positive pyramid means `S_f` points into its own cell, which is
the sign flip §3.2 gates on. This is recorded as a **disclosure about the existing gate's
coverage**, not as a change to it: retiring or altering a gate is Sanaa's alone.

### 3.4 The CG probe is retained as a DISCLOSURE, never as a gate

The PCG/DIC probe is still run and reported — residual trajectory, `maxIter` hits, and
whether the solver completes — because it is what a production run would experience. **It
carries no PASS or FAIL.** On `F360_coarse` it recorded `rc=136` (SIGFPE) at iteration 5,
7 of 8 solves at `maxIter` 100 without reaching `relTol` 0.01, and force values reaching
`−7.47301220e+22` N.

**Sanaa's §5 gates and the lab's min-cell-volume gate are unchanged and still block.**
This rung adds a gate; it retires none.

## 4. THE PREDICTIONS — each a number, each able to fail

Measured on the rebuilt mesh by `checkMesh -allGeometry -allTopology`, against
`F360_coarse`'s measured values.

| # | prediction | baseline (`F360_coarse`) | falsified if |
|---|---|---|---|
| **P1** | negative-volume cells **< 200** | **316** | count ≥ 200 |
| **P2** | negative-volume cells **> 0** — this change is *not* predicted to cure the mesh | 316 | count = 0 |
| **P3** | `wrongOrientedFaces` **< 1,800** | **2,089** (checkMesh's own "incorrectly oriented" count is **2,548**; both are recorded and P3 is on the **set**) | count ≥ 1,800 |
| **P4** | the **4↔3** enrichment among surviving negative-volume cells falls **below 10×** | **31.2×** | enrichment ≥ 10× |
| **P5** | the §3.2 SPD gate **still FAILS** — at least one `w_f ≤ 0` survives, with a named witness cell | not yet measured on `F360_coarse`; 1,028 cells carry an inverted face pyramid | every `w_f > 0` |
| **P6** | cells with **minPyrVolume ≤ 0** fall to **< 700** | **1,028** | count ≥ 700 |
| **P7** | cells with **positive volume but an inverted face** remain **> 0** — the min-cell-volume gate still under-reports | **712** | count = 0 |

**P2, P5 and P7 are the load-bearing ones and they predict this rung does NOT fix the mesh.**
Only 60.4% of the population touches any transition and only 13.2% of their faces are 4↔3,
so removing that transition cannot remove them all. **Registering the expectation of a
partial result is the point:** if P1 and P3 hold while P2 and P5 also hold, the 4↔3
transition is confirmed as *a* contributor and the residual 39.6% becomes the next rung with
its cause still unidentified. **If P5 is falsified — if the SPD gate passes — that is a
larger result than predicted and it is recorded as a prediction miss, not quietly upgraded.**

## 5. COST — core-minutes, dollars derived

**Estimate basis, measured tonight rather than assumed.** The 360° coarse build measured
**12,763 wall s × 1 rank = 212.7 core-min** (`build_360coarse_status`). The SPD probe's rate
is measured from `log.simpleFoam.PCG`: **396.97 s ExecutionTime for 4 SIMPLE iterations on 4
ranks = 6.6 core-min per iteration** on 19,700,035 cells. **That is an UPPER BOUND for this
rung**, because PCG ran to `maxIter` 100 in every solve; it is **6.7× §9's declared estimate
basis** of 3.0e-6 core-s/cell/iteration (which predicts 0.985 core-min/iteration), and that
discrepancy is itself reported to `docs/COST_CALIBRATION.md`.

| item | ranks | core-min |
|---|---|---|
| rebuild, 360° coarse, shaft at level 4 | 1 | 230 (212.7 measured + ~8% for the added shaft surface cells) |
| `checkMesh -allGeometry -allTopology` | 1 | 15 |
| `decomposePar`, 4 ranks | 1 | 10 |
| **§3.2 direct SPD gate** — mesh-only script, no solver, serial | 1 | 20 |
| PCG/DIC probe (§3.4 disclosure), 5 iterations, at the measured 6.6 core-min/iter | 4 | 33 |
| **TOTAL ESTIMATE** | | **308 core-min** |

**Registered cap: 3× the estimate = 924 core-min.** Per Sanaa's NO CAP ruling (directive
#17) **no run is stopped by this cap and no wrapper kills one**; a run that crosses it
**grades NOT A RESULT**, and the cap is **never raised**. A **liveness watchdog is
permitted** — it fires only on a log that has not advanced for 600 s, which is a deadlock
guard and not a time or budget cap, and it is what the 16:35Z MPI deadlock showed is needed.

**Cost: 308 core-min = 5.13 core-h × $0.0513/core-h = $0.26.**
**`cost_basis`: the rate is REPORTED BY THE OWNER, NOT MEASURED — the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5), so the dollar figure is DERIVED. Core-minutes are
measured from logs.** Estimate-versus-actual calibration is mandatory at completion
(CLAUDE.md rule 12) and lands as a row in `docs/COST_CALIBRATION.md` with waste named
separately.

## 6. WHAT THIS RUNG DOES NOT CLAIM

It does not produce a KT, a KQ or a y+ of any grade; it produces a mesh and a gate reading.
It does not cure the mesh (P2, P5 predict the opposite). It does not address the 70× layer
collapse, the zero prism-layer coverage, the stale-`points` staging defect, or the
blade-root fillet resolution of 2.3 cells across the LE radius. It says nothing about the
open-water curve.

---

## ADDENDUM 1 — 2026-09-13, before the rung's first build. THE REGISTERED CHANGE MOVES TWO DICTIONARY LINES, AND THEY CARRY ONE QUANTITY

*lines whose number changed above this section: 0*

**Version 1.1.** This addendum **alters no gate, threshold, cap or label.** The §3.2 SPD gate,
§3.2a same-mesh assert, predictions P1–P7, the 924 core-min cap and every verdict label are
untouched. It records the **scope** of §2's one registered change, before the build rather
than after it.

**Condition and how it was checked.** No mesh of this variant exists:
`/home/ubuntu/certonomous-runs/PPTC_VP1304/F360_coarse_shaft4` is absent from disk, and the
reader was shown able to see such a directory — the same listing returns the six that do
exist (`F360_coarse`, `L1_cm1`, `L1_prod7`, `L1_prod7s`, `L2_prod7s`, `SMOKE360_J0.7985`).

### A1.1 What §2 says, and the second line it does not name

§2 registers `refinementSurfaces { shaft { level (3 3); } }` → `level (4 4);`. In the
generator `cases/PPTC_VP1304/mesh/make_snappy.py` the `LEVELS` dictionary is read at **two**
sites, so raising it moves **two** lines of `snappyHexMeshDict`:

```
86c86   <  { file "shaft.eMesh"; level 3; }      >  { file "shaft.eMesh"; level 4; }
109c109 <          level (3 3);                  >          level (4 4);
```

Measured by generating the dictionary both ways and diffing: **those two lines are the only
difference, and with the flag unset the dictionary is `cmp`-identical to the one every
earlier build used.**

### A1.2 Why the feature-edge level moves WITH it, and is not held back

**Holding `shaft.eMesh` at 3 while the surface goes to 4 would leave the feature edges
coarser than the surface they bound.** That mismatch is a mesh defect of exactly the kind
this rung exists to remove — and it would be one **we introduced**, on the single patch the
rung touches, while claiming to repair it. Holding it back is not restraint; it is a second
and worse change wearing restraint's clothes.

**One registered quantity — "the shaft's refinement level" — expressed in two dictionary
lines is ONE change.** Two *quantities* would be two changes; two lines carrying one quantity
is one.

### A1.3 How it is implemented, and the control that proves the default did not move

`--shaft-level` was **added** to `make_snappy.py` (default **3**) and a `PPTC_SHAFT_LEVEL`
pass-through **added** to `build_level.sh` (default **3**): `+13/−0` and `+4/−0` lines, no
deletions, no existing line altered. **The default is the registered pre-rung value, so every
other level of the family still builds byte-for-byte identically** — verified by `cmp` of the
generated dictionary against the pre-edit generator's output. The rung's build sets
`PPTC_SHAFT_LEVEL=4`; nothing else in the pipeline differs from the `F360_coarse` build.

### A1.4 Status

**Pre-build. No gate, threshold, cap or label is altered.** Disclosed before the build so the
second dictionary line is **scope**, not a change discovered in a log afterwards.

---

## ADDENDUM 2 — 2026-09-13, before the rung's first build. TWO REFUSAL LIMBS ON THE §3.2 INSTRUMENT, AND WHY THE GATE'S EXPECTED ANSWER WAS THE DANGEROUS ONE

*lines whose number changed above this section: 0*

**Version 1.2.** This addendum **alters no gate, threshold, cap or label.** Both limbs below
are **REFUSAL-ONLY**: each can turn a verdict into `NOT A RESULT`/VOID and **neither can
produce, improve or rescue one.** That is the only direction CLAUDE.md rule 5 permits a check
to move a verdict, and it is why these are legal as an addendum at all. The §3.2 gate, §3.2a
assert, P1–P7 and the 924 core-min cap are untouched.

### A2.1 What happened, stated against the instrument rather than around it

Driven at the known-bad `F360_coarse` as §3.2 requires, the gate returned **GATE FAIL — the
expected direction — and the verdict was VOID.** The geometry control caught it; the verdict
did not.

| control quantity | value |
|---|---|
| max relative difference in cell volume vs OpenFOAM `0/cellVolume` | **2.144e+09** |
| negative-volume cells, this instrument | **9,809,857** |
| negative-volume cells, OpenFOAM | **316** |
| internal faces flagged `w_f ≤ 0` | 29,417,841 of 59,079,066 (**49.8%**) |
| cells flagged `A_PP ≤ 0` | 9,809,842 of 19,700,035 (**49.8%**) |

**No mesh fails half its cells. 49.8% is the signature of a reader, not of a mesh.**

**Cause.** §3.2 registers the instrument to read `constant/polyMesh/{points,faces,owner,
neighbour}`. In `F360_coarse` that `points` is the **stale snapped array of 20,518,324
entries** (mtime 11:17:38) while `faces` and `owner` beside it are the layer-phase arrays
referencing **20,507,704**. Every index past the first merged point addresses the wrong
coordinate, **and no index is out of range, so nothing errors.** This lane found and reported
that defect earlier the same day, repaired it in the staging path, did not repair it at the
source, and then registered a gate whose input path **is** the source.

### A2.2 THE STOP-RULE WAS ONE-DIRECTIONAL, AND THAT IS THE FINDING

The supervising instruction read: *"If it returns PASS on `F360_coarse`, stop — that means
the gate is broken."* **It returned FAIL, and under that rule as written the build would have
proceeded on a void verdict.**

> **A gate that gives the EXPECTED answer from garbage is worse than one that gives the wrong
> answer, because the expected answer is the one nobody checks.**

**Widened, binding on this rung: STOP UNLESS THE GEOMETRY CONTROL PASSES — IN EITHER
DIRECTION.** A confirming result gets the same scrutiny as a surprising one.

### A2.3 The two limbs

**LIMB 1 — points/faces consistency.** `nPoints` must equal `max(face vertex index) + 1`;
otherwise **REFUSE (exit 2), never grade.** Measured: `F360_coarse/constant` carries **10,620
orphan points** → REFUSE; `SMOKE360_J0.7985/constant` carries exactly **20,507,704** →
consistent, may grade. **Checked at header level, so the limb is provable without parsing
2.2 GB** — a control nobody can afford to run is a control nobody runs.

**LIMB 2 — the geometry control is promoted to BLOCKING** (exit 2, verdict VOID) on a max
relative cell-volume difference above `1e-6` or a negative-volume count disagreeing with
OpenFOAM's. **It was informational, and it printed AFTER the verdict — the worst possible
placement for the only check that worked.** A supporting check found to be load-bearing is
moved in front of the thing it protects.

**Re-armed after both limbs:** valid two-cell mesh PASS, deliberately inverted mesh GATE FAIL
with witness cell 0, `A_PP = −8.842105263e-01` — **unchanged**, which is what makes the limbs
safe to add.

### A2.4 Cost of the void run, named not absorbed

**301 s serial = 5.0 core-min, peak RSS 33.4 GB, charged as WASTE**
(`COMPUTE_BUDGET_CHARTER` §6 — waste is named, never absorbed into a ratio). §5 registered
the gate at 20 core-min and **declared no memory footprint at all**, unlike §9.1 of the act
pre-registration which declares one for every solver and mesher run. **That omission is a gap
in the estimate, disclosed before the run rather than after it**, and it lands in the
calibration row with the measured figure beside it.

### A2.5 Status

**Pre-build. Refusal-only. No gate, threshold, cap or label is altered.** The baseline is
being re-driven on `SMOKE360_J0.7985`, whose `constant/polyMesh` is the same geometry with
`0/polyMesh/points` staged over the stale array. **No build starts until the baseline fires
on geometry the control accepts.**
