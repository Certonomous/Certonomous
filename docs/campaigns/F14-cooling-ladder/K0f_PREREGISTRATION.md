# K0f. Turbulent mixed convection, Blay–Mergui–Niculae ventilated cavity: PRE-REGISTRATION

**Registered 2026-08-26T03:25:14Z, BEFORE ANY K0f COMPUTE.** Zero core-minutes
have ever been spent against K0f.
`verification/runs/F14-cooling-ladder/K0f_runs/` does not exist at this write,
and this document does not create it. **This document authorises no solve.**

**The absence was CHECKED, not asserted, and under a planted control** (standing
rule 3): in the invocation that wrote this section `test -e
verification/runs/F14-cooling-ladder/K0f_runs` returned **ABSENT** while the
same reader returned **PRESENT** on
`verification/runs/F14-cooling-ladder/K0cS_runs`, which does exist. A zero from
a reader not shown able to see a non-zero is not evidence.

---

## −1. THE RUNG ID, AND WHY IT IS NOT `K0e`

**The heat-transfer supervisor's ruling of 2026-08-26 (R2) directed that the
successor be a new rung with a new id, `K0e`, and named the file
`K0e_PREREGISTRATION.md`. `K0e` IS NOT A NEW ID. IT IS ALREADY IN USE, IN THIS
CAMPAIGN, FOR A DIFFERENT PHYSICS PROBLEM.**

`docs/campaigns/F14-cooling-ladder/K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` —
the forced-convection flat plate against Bahrami (2005) — was written
2026-08-19, zero compute, specification only, rung not run. It is live on the
board and cited by name in **`docs/DOCKET.md` D431 and D434**,
`docs/THERMAL_CAPABILITY_STATE.md`, `docs/campaigns/T-family/T_FAMILY_INDEX.md`,
`docs/campaigns/T-family/T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md`,
`docs/inventory/2026-08-24/LAB_INVENTORY.md` and
`verification/runs/T-family/T1_runs/build_t1c.py`. D434 carries the sentence
*"K0e arms none and is BLOCKED and PENDING by construction"* — a sentence that
becomes ambiguous the moment a second `K0e` exists in the same folder.

**R2's entire content is that the successor must be DISTINGUISHABLE from its
predecessor. An id that collides with a live rung defeats that.** The id is
therefore **`K0f`**, verified textually free repo-wide (`git grep K0f` over
`*.md *.py *.sh *.json *.txt` returns nothing) at this write.

**THE ID IS THE SUPERVISOR'S, NOT THIS LANE'S.** No K0f compute has run, so a
rename before launch is legal under standing rule 2 and costs one commit. It is
recorded here rather than taken silently, and the supervisor may overrule it.

---

## 0. THIS DOCUMENT STATES ITS OWN CEILING, ON ITS FACE

**K0f CANNOT REACH `HOLDS`, AND AS REGISTERED IT CANNOT REACH THE `G` COLUMN
EITHER.**

| column | reachable on K0f as registered | why |
| --- | --- | --- |
| **`V`** | **PARTLY** | the extraction equivalence, the strict completion rule, the five guards, convergence and achieved `y⁺` are all measurable without a reference — **but the Roache/GCI arm of `V` is not, for the same reason `G` is not** |
| **`G`** | **NO** | a Roache triple needs THREE levels. §8 registers **L1 and L2 only**; **L3 is not authorised by this document.** Without L3 there is no triple, so there is no observed order and no GCI |
| **`P`** | **NO** | Blay, Mergui and Niculae (1992) is **`NOT OBTAINED`** |

**THE BEST VERDICT THIS RUNG CAN REACH AS REGISTERED IS `GATE REACHED`, NAMING
BOTH `P` AND `G` AS UNREACHED COLUMNS.** Nobody may later read a completed run
of this rung as a graded result, and nobody may read it as a grid-convergence
result either. §8.3 records the arithmetic under which L3 would be added, and
§10 item 2 records that the exclusion of L3 rests on a cost reading this lane
could not reproduce.

---

## 1. CASE — CARRIED OVER UNCHANGED

**Adopted by citation, byte-unchanged, from `K0d_REREGISTRATION.md` (v1.3, the
frozen operative K0d document) §§1, 1.1, 1.2, 1.3.** Blay–Mergui–Niculae
ventilated cavity; 2D, `x ∈ [0, 1.04]`, `y ∈ [0, 1.04]`; inlet `x = 0,
y ∈ [1.022, 1.040]`; outlet `x = 1.04, y ∈ [0, 0.024]`; solver
`buoyantBoussinesqSimpleFoam`, OpenFOAM v2606 stock, steady, `g = (0, −9.81, 0)`.

| quantity | **registered value** |
| --- | ---: |
| `T_ref` | **298.00 K** |
| `β` | **1/298 = 3.3557047e-03 K⁻¹**, by identity |
| `ν` | **1.569e-5 m²/s** |
| `Pr` | **0.71** |
| `Pr_t` | **0.85**, never tuned |
| `ΔT` | **exactly 20.0 K** |
| `Ra` | **2.135970e9 — DERIVED, REPORTED, NEVER A TARGET** |

**`K0d_REREGISTRATION.md` IS NOT EDITED BY THIS DOCUMENT** (standing rule 6). It
stays on disk byte-unchanged, as do `K0d_PREREGISTRATION.md` and all five of its
amendments, and both preserved failed build trees.

---

## 2. REFERENCE — GROUND `P`, UNCHANGED AND NOT TO BE WORKED AROUND

**PRIMARY: Blay, D., Mergui, S. and Niculae, C. (1992), ASME HTD-213 — `NOT
OBTAINED`.** Every graded reference value is `PENDING` on it and every graded
row is `BLOCKED` under the §7.4 verdict ladder's order 4.

**OBTAINING IT IS FROM OUTSIDE THE BOX, IS SANAA'S ALONE (standing rules 7 and
8), AND IS NOT TO BE ATTEMPTED BY ANY AGENT.** No search was made, no fetch was
attempted and none is authorised by this document.

Secondaries (Zou 2018, Oulghelou 2020) supply **the case** and may never supply
a graded reference value — both only plot the Blay symbols.

---

## 3. QUANTITIES, AND 4. BANDS — CARRIED OVER UNCHANGED

**Adopted by citation from `K0d_REREGISTRATION.md` §3 and §4, and through them
from the superseded §7.2/§7.3 and `AMENDMENT 4` §A4.5:** the ten graded rows
`G1 G2 G3 G4 G5a G5b G6 G7 G8 S1`; the thirteen graded stations; the reported
rows `M0` and `R1`; the five guards `HB B I DC MB`; the dual-scheme control of
`AMENDMENT 1` §A1.3b; the seed control `M1_m_seed` of §A1.2b and its frozen
criterion.

**NO BAND IS SET, WIDENED, NARROWED OR REINTERPRETED BY THIS DOCUMENT.**
`± 1.00 K`, `± 0.0570 m/s`, `± 0.0208 m`, `± 0.104 m`, `± 10 % of |q_ref|`,
`EXACT MATCH REQUIRED`, the §7.2 conversion rule with its `max` form and its
anti-widening guard, `ΔT_band = 20.0 K`, the 0.5 % heat-balance tolerance, the
25 % discrimination threshold, and the `y⁺` windows **`≤ 5.0` on L1** and
**`≤ 3.3` on L2** are every one adopted byte-unchanged.

**Every change in this document either REPAIRS AN INSTRUMENT or MOVES THE MESH
to satisfy a refusal condition that is itself untouched.**

---

## V. GROUND `V` — THE WALL READER, REPAIRED, AND THE REPAIR IS **THREE** CHANGES

### V.1 What the ruling ordered, and why it was not enough

The supervisor's R4 ordered one change: *"`_vertex_value()` … must take the
BOUNDARY FACE VALUE at a vertex lying on a patch, as OpenFOAM `cellPoint` does,
instead of averaging interior cells only."*

**THAT CHANGE IS NECESSARY AND IT IS NOT SUFFICIENT. IT LEAVES THE READER 93×
OUTSIDE ITS OWN REGISTERED CRITERION.** Measured on the preserved `M1_c` at
`endTime` 40000 against OpenFOAM's own `postProcess -func sample` at the
registered §A1.3a parameters — not argued, and not relayed:

| reader state | worst \|diff\| `T`, vertical mid-plane | verdict |
| --- | ---: | --- |
| K0d as frozen | **1.141331 K** | DISAGREE |
| **+ boundary face values (R4's change, alone)** | **1.854106e-03 K** | **still DISAGREE** |
| + inverse-distance point weights, in 3D | } | |
| + tet decomposition carrying the CELL value | } **3.988237e-08 K** | **AGREE** |

against the registered **2.00e-05 K**.

**THE 1.141331 K FIGURE REPRODUCES `K0d_FORENSICS_2026-08-25.md` ADDENDUM 4
EXACTLY** — `308.150000 − 307.008669 = 1.141331` — which is the independent
confirmation that the defect identified here is the defect that was measured
there.

### V.2 The three mechanisms, each traced to the installed source

Read from `/usr/lib/openfoam/openfoam2606/src/finiteVolume/lnInclude/`, not
from recall:

1. **`volPointInterpolation` OVERRIDES the point value on every non-constraint
   patch with that patch's own FACE values.** It does not blend them with the
   interior average, which is why a `fixedValue` floor reads back as **exactly**
   the registered boundary condition. This is R4's change.
2. **`volPointInterpolation` weights cell values into a point by INVERSE
   DISTANCE from the CELL CENTRES, in THREE dimensions.** The mesh is one cell
   thick, so every vertex sits a half-thickness in `z` from every cell centre it
   draws on; at the registered `t = 0.010 m` that offset is the same order as
   the in-plane spacing. Equal weighting is wrong by up to **1.4e-03 K** in the
   graded near-wall rows — measured.
3. **`interpolationCellPointI.H` computes
   `psi_[cell]*w[0] + psip_[faceVertices[0..2]]*w[1..3]`** — a barycentric blend
   over a **TETRAHEDRON whose fourth vertex is the CELL CENTRE**, from
   `polyMeshTetDecomposition`. **A bilinear blend of vertex values contains no
   cell value at all.** This is why the horizontal mid-plane — graded in `x`
   along its whole length — was the worse of the two sets at **1.774491e-02 K**.

**THE K0d READER WAS NOT A `cellPoint` INTERPOLANT AT ALL.** It was a bilinear
blend of four equally-weighted vertex averages, with no boundary value and no
cell value. Naming the defect as one change understated it by two.

### V.3 The result, on both preserved closures

The registered `ADDENDUM 1` §AD1.1 check, run through `analyse_k0f.py`'s
repaired reader on the two preserved K0d L1 cases:

| case | set | field | worst \|diff\| | criterion | verdict |
| --- | --- | --- | ---: | ---: | --- |
| `M1_c` | vertical | `T` | **3.988237e-08 K** | 2.00e-05 K | agree |
| `M1_c` | vertical | `U.x` | **2.528072e-09 m/s** | 5.70e-07 m/s | agree |
| `M1_c` | horizontal | `T` | **1.772185e-08 K** | 2.00e-05 K | agree |
| `M1_c` | horizontal | `U.x` | **1.117403e-10 m/s** | 5.70e-07 m/s | agree |
| `M2_c` | vertical | `T` | **2.960030e-08 K** | 2.00e-05 K | agree |
| `M2_c` | vertical | `U.x` | **1.638474e-09 m/s** | 5.70e-07 m/s | agree |
| `M2_c` | horizontal | `T` | **2.501457e-08 K** | 2.00e-05 K | agree |
| `M2_c` | horizontal | `U.x` | **4.130605e-11 m/s** | 5.70e-07 m/s | agree |

**8 of 8 AGREE, on two different closures, at 500× and 225× inside the two
registered criteria.**

**AND THAT IS AN INSTRUMENT RESULT, NOT A RUNG RESULT.** It is measured on
**K0d's preserved evidence**, on cases that are themselves **NOT DONE** under
the strict completion rule (§R6). It establishes that the reader is repaired. It
establishes nothing about K0f, which has not run.

### V.4 THE TIGHTENING: A STANDING PRE-GRADING GATE

**REGISTERED: `analyse_k0f.py` REFUSES (exit 2) unless
`check_k0f_extraction_equivalence.py` has PASSED on the graded level IN THE SAME
INVOCATION.**

`AD1.1` registered the equivalence check as a one-off, to be run once after L1.
It was, and it said `DISAGREE`. **The lesson is not that the check was worth
running once; it is that FOR THE WHOLE LIFE OF K0d THE GRADED PATH RESTED ON AN
EQUIVALENCE NOBODY HAD MEASURED.** A reader never compared against the reference
implementation is a planted zero with no control. The comparison is therefore
not a milestone that can be passed and left behind.

**The gate REFUSES if the checker file is merely ABSENT**, because a check
omitted in silence reads as a check passed.

### V.5 THE CRITERION IS NOT NARROWED, AND THE MITIGATION IS RECORDED AS MATERIAL

**`AD1.1`'s criterion is written on the SAMPLED LINE, not on the station
subset, and this document does not re-read it.** Recorded because it is material
to the ruling and **not** because it excuses anything: on the K0d snapshot only
**71 of 2 081** points exceeded, the median difference was **2.86e-06 K**, and
**all thirteen registered graded stations agreed**. **That does not soften
anything.** Re-reading a criterion as "at the stations" after seeing which
points failed is the move `VERIFICATION_CHARTER` §2d.1 forbids. The 71-of-2081
figure stands here as **material, never as mitigation**.

---

## G. GROUND `G` — THE MESH MOVES, THE REFUSAL CONDITION DOES NOT

### G.1 The contradiction being repaired

§4 condition D requires the first wall-normal cell to be the design value **and
the smallest in its block**. §5 registers **two-sided geometric grading** with
one registered first cell. **Block A's K0d L2 count is 17 — odd — and an odd
count cannot be split into two equal halves**, so the two ends receive different
first cells and the smaller lands at the slot lip. Measured from the built K0d
mesh: floor `7.864662e-04` (**0.000 % off**), lip `7.004187e-04`, **NOT SMALLEST
IN BLOCK**. L1 (12) and L3 (24) are even and symmetric and pass.

**CONDITION D IS NOT TOUCHED BY THIS DOCUMENT.** Relaxing a refusal condition
because a mesh cannot satisfy it is precisely *"the numbers looked wrong, so the
band was widened."* **If anything moves, the mesh moves.**

### G.2 THE SUPERVISOR'S DERIVATION, RECORDED VERBATIM AS DIRECTED

R3 directed that the supervisor's own re-derivation be carried here verbatim,
*"because a derivation that only one agent has done is not a derivation"*:

> `r21 = sqrt(nA*224 / 1920)` with block-A L1 = `12*160 = 1920` cells;
> `r32 = sqrt(7536 / (nA*224))` with block-A L3 = `24*314 = 7536` cells.
> Condition C `[1.35, 1.45]` on `r21` gives `nA <= 18.021` and `nA >= 15.62`; on
> `r32` gives `nA >= 15.997` (so `nA = 16` gives `r32 = 1.45006`, ABOVE the
> ceiling — refused) and `nA <= 18.455`. Condition C therefore admits exactly
> `{17, 18}`. Condition B forces `nA >= 17`. Condition D's parity requirement
> forces even. **`nA = 18` is the unique survivor.** `r21 = 1.44914` clears 1.45
> by 0.00086 (0.059 %); `r32 = 1.36713` sits mid-window.

### G.3 RE-DERIVED INDEPENDENTLY HERE — THE CONCLUSION HOLDS, TWO BOUNDS DO NOT

**The conclusion `nA = 18` is CONFIRMED and is unique. Two of the four stated
bounds are arithmetically wrong, and both corrections are recorded rather than
propagated.** A correction quietly made is worse than one visibly made
(`K0d_REREGISTRATION.md` §A2.2's own standard).

| bound | as stated in R3 | **re-derived here** | effect |
| --- | ---: | ---: | --- |
| `r21 ≤ 1.45 → nA ≤` | 18.021 | **18.021429** | agrees |
| `r21 ≥ 1.35 → nA ≥` | 15.62 | **15.621429** | agrees |
| **`r32 ≤ 1.45 → nA ≥`** | **15.997** | **16.001359** | **corrected** |
| `r32 ≥ 1.35 → nA ≤` | 18.455 | **18.459730** | corrected, immaterial |

**THE FIRST CORRECTION REPAIRS THE RULING'S OWN INTERNAL CONSISTENCY.** At the
stated bound of 15.997, `nA = 16` would be admitted by condition C — yet the
same sentence correctly says `nA = 16` gives `r32 = 1.45006` and is refused, and
then correctly concludes that C admits exactly `{17, 18}`. **The correct bound
16.001359 is what makes that conclusion true.** The stated 15.997 contradicted
it. The correction makes the ruling right, not wrong.

**The full search, all four conditions at once, re-derived here:**

| `nA` | parity | block-A L2 cells | `r21` | `r32` | cond B | cond C | cond D |
| ---: | --- | ---: | ---: | ---: | --- | --- | --- |
| 16 | even | 3 584 | 1.36626 | **1.45006** | **no** | **NO** | ok |
| 17 | **ODD** | 3 808 | 1.40831 | 1.40677 | ok | ok | **NO** |
| **18** | **even** | **4 032** | **1.44914** | **1.36713** | **ok** | **ok** | **ok** |
| 19 | ODD | 4 256 | **1.48885** | 1.33067 | ok | **NO** | **NO** |
| 20 | even | 4 480 | **1.52753** | 1.29697 | ok | **NO** | ok |

**`nA = 18` is the UNIQUE survivor of B ∧ C ∧ D. It is forced by the registered
constraints, not selected.**

### G.4 THE REGISTERED MESH

| level | `Nx` | `nA` | `nB` | `nC` | `Ny` | cells | first wall cell |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **L1** | 160 | 12 | 138 | 10 | 160 | 25 600 | 1.101053e-03 m |
| **L2** | 224 | **18** | **192** | 14 | 224 | 50 176 | 7.864662e-04 m |
| **L3** | 314 | 24 | 270 | 20 | 314 | 98 596 | 5.610459e-04 m |

**`Ny` = 224, the total 50 176, `R21` = 1.400000, `R32` = 1.401786 and the whole
first-wall-cell column ARE UNCHANGED.** Only `nA` and `nB` move, and they move
against each other. Nothing that feeds `observed_order()` or the GCI is touched.

**Condition C passes on ALL THREE BLOCKS at BOTH level pairs**, re-run here
through the instrument's own `condition_C_spec`:

```
  L1->L2   block A 1920->4032, r=1.4491; block B 22080->43008, r=1.3956;
           block C 1600->3136, r=1.4000
  L2->L3   block A 4032->7536, r=1.3671; block B 43008->84780, r=1.4040;
           block C 3136->6280, r=1.4151
```

Condition B at L2: outlet slot `18 ≥ 17`, inlet slot `14 ≥ 14`. Both hold.

### G.5 THE MARGIN, DISCLOSED — AND IT IS EXACT ARITHMETIC ON INTEGERS

**`nA = 18` clears condition C's 1.45 ceiling on `r21` by 0.00086 — 1.44914
against 1.45, a margin of 0.059 %.** That is the weakest number in this
registration and it is stated out loud.

**AND A CORRECTION TO THE DRAFT'S REASONING ABOUT IT, WHICH MAKES THE
REGISTRATION STRONGER RATHER THAN WEAKER.** The draft warned that *"a 0.06 %
margin sits well inside the range where the real geometry of a rebuilt graded
mesh could flip it."* **That is not true of condition C as implemented.**
`condition_C` computes `r = (hi_cells / lo_cells) ** 0.5` from **INTEGER cell
counts counted off the mesh** — `Nx = len(x_lines) - 1` and `_count_between` on
the block bands. There is no floating geometry in it. **`r21` for block A will
read exactly `sqrt(4032/1920) = 1.449138` or it will not read 4032 cells at
all.** The margin cannot drift by 0.059 % or by anything else.

**The residual risk is therefore a DIFFERENT one, and naming it correctly is the
point:** condition C can only flip **discretely**, if `_count_between` counts a
different number of `y` rows in a block band — a **topology** question about
whether `blockMesh` places a `y` line exactly on 0.024 and 1.022, not a rounding
question. That is what §G.6 requires be measured.

### G.6 WHAT MUST BE RE-CHECKED, AND THE FAILURE DISPOSITION IS PRE-DECIDED

**Conditions C and D must be RE-RUN against the rebuilt L2 mesh and shown to
pass, before any solver on any level fires. A derived number is a hypothesis
until the instrument reads the mesh.**

**THE PARITY PREDICTION CARRIES A PLANTED POSITIVE, and it was planted before
the prediction was believed.** The grading model used to predict `nA = 18`'s
behaviour was first driven at `nA = 17` and **reproduced the OBSERVED K0d L2
failure byte-identically**:

```
  nA=17  split 8+9   floor 7.864662e-04 (0.000% off)   lip 7.004187e-04
                     smallest-in-block: False      <- the observed D FAIL
  nA=18  split 9+9   floor 7.864662e-04 (0.000% off)   lip 7.864662e-04
                     smallest-in-block: True
```

**A model that could not reproduce the failure would not have been trusted about
the repair.** It is still a model of `blockMesh`, not `blockMesh`, which is why
§G.6's re-check on the built mesh is required and not optional.

**PRE-DECIDED NOW, BEFORE THE MESH IS BUILT, ADOPTED VERBATIM FROM THE DRAFT'S
§2.3 AS R3 DIRECTED:**

> **If condition C reads the rebuilt mesh and `r21` lands ABOVE 1.45, the answer
> is NOT to widen condition C.** It is that **no `nA` satisfies all four
> conditions**, and **the mesh family must be re-chosen at a level above
> `nA`** — which is **a re-registration, not a repair**.

**A failure disposition written after seeing the failure is not a disposition;
it is an accommodation.**

### G.7 WHY THE MARGIN IS INHERITED GEOMETRY, NOT SLOPPINESS

**Registered so that no later reader mistakes the thin margin for carelessness
in K0f.** `nA = 17` is the **CENTRED** value of the feasible set —
`r21 = 1.40831`, `r32 = 1.40677`, both within 0.6 % of the design 1.40 — and it
is the value K0d registered. **`nA = 18` sits at the `r21` lip because the
registered L1 and L3 block-A counts, 12 and 24, were themselves chosen around an
ODD L2.** The thin margin is the arithmetic consequence of a parity defect two
levels away, inherited by the only even value the constraints leave standing.

**And the symmetry is deliberate:** refusing `nA = 18` *because its margin feels
thin* would be the mirror image of widening a threshold *because a value feels
close*. **Both substitute comfort for the registered criterion.** `nA = 18`
passes condition C as written and is the unique member of the feasible set.

---

## 3A. THE CONSUMER-SIDE COMPLETENESS ASSERTION

**REGISTERED: before any solver starts, `build_k0f.py --preflight <case>`
enumerates the field set the SOLVER REQUIRES and REFUSES (exit 2) if any is
absent from `0/`.** The assertion is against **what the consumer demands**,
never against a hash of what the producer wrote — both readers of a hash agree
on the same wrong files.

**THE ENUMERATION, REGISTERED RATHER THAN LEFT TO AN IMPLEMENTER:**

1. the **closure is READ FROM `constant/turbulenceProperties`**, never from the
   builder's own table — the table is what was meant, the file is what the
   solver will consume, and their divergence is this section's whole subject;
2. `system/fvSolution`'s solver regex `"(U|T|k|omega|epsilon)(Final)?"` and
   relaxation regex `"(k|omega|epsilon)"` are the **OVER-SET**: **both name
   `omega` AND `epsilon`**, because one dictionary serves all three closures.
   **A naive enumeration from `fvSolution` alone would demand `epsilon` of a
   `kOmegaSST` case and refuse a correct run;**
3. the required set is the **registered §7.2 per-closure completion set**, minus
   the solver-generated fields;
4. **`phi` is EXCLUDED** — the solver generates it, it is never staged, and that
   is why `0/` correctly holds seven files where the completion set names eight;
5. the two are **RECONCILED**: a **SOLVED** closure variable that `fvSolution`
   does not name is a finding and REFUSES.

### 3A.1 THE ASSERTION CAUGHT A DEFECT IN ITS OWN FIRST DRAFT, BEFORE ANY LAUNCH

**Recorded rather than quietly corrected, because it is the strongest evidence
the assertion works.** Clause 5's variable tuple first read
`("k", "omega", "epsilon", "nut")`, and the assertion then **REFUSED every
correct turbulent case**: *"the registered completion set for kOmegaSST names
'nut' but system/fvSolution never mentions it."*

**IT WAS RIGHT TO REFUSE AND THE ENUMERATION WAS WRONG.** `nut` and `alphat` are
**CALCULATED** fields — staged in `0/` because the solver reads them, never
solved — so `fvSolution` correctly has no entry for either. **This is §3A's own
warning arriving from the opposite direction:** the naive enumeration demands
`epsilon` of a `kOmegaSST` case; the over-eager reconciliation demands an
`fvSolution` entry for a field that has no equation. **Both are the same
mistake — reading one dictionary as though it described the whole consumer.**

It is a footnote instead of a refused batch in a detached queue **only because
the assertion was DRIVEN on all three closures before any launch.**

### 3A.2 DRIVEN, BOTH DIRECTIONS

| arm | result |
| --- | --- |
| `M1_c` (`kOmegaSST`) | requires `T U p_rgh alphat nut k omega` — **clean** |
| `M2_c` (`RNGkEpsilon`) | requires `T U p_rgh alphat nut k epsilon` — **clean, and `omega` is NOT demanded** |
| `C_lam` (laminar) | requires `T U p_rgh alphat` — **clean, and `k`/`omega`/`nut` are NOT demanded** |
| each of the seven required fields hidden in turn | **REFUSED, exit 2, naming the field** (7 of 7) |
| `phi` absent from `0/` | **STAYS QUIET** — correctly never demanded |

**It tightens and cannot loosen:** it adds a refusal channel and removes none.

---

## 3B. THE `.gz` BRANCH IS EXERCISED ANYWAY

`AMENDMENT 2` §A2.1c registers `writeCompression = off`, so this rung will not
produce a gzipped field. **`mark_done_k0f.py`'s selftest exercises the `.gz`
branch regardless**, in both required arms:

1. a **gzipped clean case** that still satisfies all seven clauses — **PASSES**;
2. a **gzipped case whose fields are older than its own `0/T`** — the **age
   guard still FIRES**.

**A branch kept alive in the code and dead in the test is a branch that will be
believed the first time it is used.** Eleven legacy `mark_done_*.py` scripts in
this family carry no `.gz` handling at all and fail safe **by coincidence**;
failing safe by coincidence is not the same as being correct.

---

## 3C. NO `assert` IN A K0f INSTRUMENT MAY CARRY A REFUSAL, GUARD, CONTROL OR GATE

**`assert` statements are REMOVED by `python3 -O` / `PYTHONOPTIMIZE=1`.** A
refusal written as an assert is therefore not a refusal under every interpreter
the script can be launched with. Elsewhere in this lab the defect was
exploitable, not theoretical: a repository guard refused under `python3` and
**proceeded to `git add -A` on the shared tree under `python3 -O`**; and a
measurement script whose planted controls were all asserts **lost every control
under `-O` and exited 0 — standing rule 3 defeated by an interpreter flag.**

**REGISTERED, BINDING IN THIS RUNG, and enforced by
`scripts/check_k0f_instrument_standard.py` in three arms:**

1. **STATEMENT TYPE** — every K0f instrument's own AST must carry **zero
   `Assert` nodes**. This catches a revert without running anything.
2. **DRIVEN UNDER `-O`** — every registered refusal is **EXECUTED** under
   `python3 -O` and must fire **identically**, *not* merely "the selftest passes
   under `-O`", because **a passing selftest proves only the clean path, and the
   clean path is exactly the one an evaporated guard still walks.**
3. **MUTATION** — arm 1 is itself shown able to FIRE: a guard reverted to an
   `assert` is caught on statement type alone, and the same guard written as
   `sys.exit(2)` is **not** flagged.

**Result at this registration: 6 instruments, 0 Assert nodes; 8 registered
refusals, `python3` and `python3 -O` identical on every one; mutation caught,
negative control quiet.**

**THIS DOCUMENT DOES NOT MAKE §3C BINDING BEYOND THIS RUNG.** Adopting it
lab-wide is a charter matter and is **neither a lane's nor a supervisor's to
land.**

---

## R6. THE LAUNCHER — rc CAPTURE, AND THE TRAP IN THE OBVIOUS REPAIR

### R6.1 What actually happened at bf7e9428

**K0d HAD NO LAUNCHER AT ALL.** The L1 launch was an ad-hoc `setsid` + `timeout`
command line, so no `STATUS.<case>` was ever written, so standing rule 4's
`rc = 0` limb could not be evaluated. `M1_c` and `M2_c` are **NOT DONE** despite
passing **six of seven clauses** — `End` line, last time == `endTime`, every
registered field present for the case's own closure, full `ExecutionTime` count,
and the age guard.

**THE LANE THAT REFUSED TO BACK-DATE `rc=0` WAS RIGHT, AND THAT IS RECORDED HERE
AS CORRECT CONDUCT.** The log's `End` line is what `rc=0` normally accompanies —
and that is an **inference**, not the measurement the clause requires. The
completion rule is all-or-nothing precisely so that it cannot be satisfied by a
plausible reconstruction.

### R6.2 **`setsid` DISCARDS THE SOLVER'S EXIT STATUS. MEASURED ON THIS BOX.**

util-linux 2.39.3, GNU coreutils 9.4, run in the invocation that wrote this
section:

```
  setsid        timeout 5 bash -c 'exit 7'   ->  rc = 0      <-- NOT 7
  setsid --wait timeout 5 bash -c 'exit 7'   ->  rc = 7
```

`setsid` **forks** when it is not already a process-group leader and the parent
exits **0 immediately**, while the child carries the real status into a new
session where nothing collects it.

**CONSEQUENCE, AND IT IS THE MOST IMPORTANT SENTENCE IN THIS SECTION: THE
OBVIOUS REPAIR — "capture rc into a STATUS file" — WRITTEN AS
`setsid timeout … ; rc=$?` WOULD HAVE FABRICATED `rc=0` FOR A CRASHED SOLVER.**
That is **strictly worse than the defect it replaces**: an absent STATUS
produced an honest `NOT DONE`; a fabricated `rc=0` produces a **FALSE PASS on
the load-bearing limb of the completion rule**, with nobody watching.

### R6.3 The registered architecture

**`scripts/launch_k0f.sh` detaches by re-executing ITSELF under bare `setsid`,
and then runs the solver in its OWN FOREGROUND** — no `setsid` between the
wrapper and the solver — so `$?` is genuinely the solver's status. Detachment
and true rc capture are both obtained; `setsid --wait` would also propagate the
status but would block the caller, which a queue cannot afford.

**The statuses, recorded distinguishably, all measured here:**

| condition | rc | meaning |
| --- | ---: | --- |
| clean | 0 | complete |
| solver exits `n` | `n` | `timeout` passes the child's status through |
| solver dies on signal `n` | `128 + n` | SIGSEGV → 139 |
| **cap expires** | **124** | a **CAP-STOP** (rule 12), not a crash |

**`timeout --preserve-status` IS REFUSED IN THE SOURCE.** Measured here it turns
expiry into **143 = 128 + SIGTERM**, which **collides with a genuine SIGTERM
death** and destroys the very distinction the ruling required.

**RESIDUAL AMBIGUITY, DISCLOSED RATHER THAN PAPERED OVER:** a solver that itself
exits 124 is indistinguishable from an expiry. `STATUS` therefore also records
`timeout_s` and `wall`, so a reader can see whether the wall clock reached the
cap. **That is a discriminator, not a proof.**

### R6.4 Registered launcher behaviour

1. **`STATUS.<case>`**, that exact name, in the pool format
   `rc= wall= checkMesh_rc=`, written **ATOMICALLY** (temp file in the same
   directory, then `mv`) so no reader sees a half-written STATUS and a crash
   mid-write leaves **no** STATUS rather than a truncated one.
2. **The consumer-side completeness assertion runs BEFORE the solver** (§3A).
   **A pre-flight refusal writes NO STATUS** — nothing ran, so there is no rc,
   and inventing one is the back-dating this whole section exists to prevent.
3. **`0/T` is touched LAST**, immediately before the solver, so its mtime dates
   the run allowed to produce the answer. **A missing `0/T` REFUSES**: the age
   guard would otherwise be deciding on a `None`.
4. **`--ranks` other than 1 REFUSES** — K0f is registered SERIAL (§6).
5. **`mark_done_k0f.py` REFUSES (exit 2) on an ABSENT `STATUS`**, distinct from
   exit 1 `NOT DONE`. **A missing rc is not a passing rc**, and under a detached
   queue the two must not read alike. **Every case is reported FIRST and the
   refusal is raised after**, because a refusal that destroys the report it was
   about to make is a worse instrument than the one it replaced.

### R6.5 Written to a lab-wide interface, and why

The heat-transfer supervisor relayed on 2026-08-26 that cfd is building a
**detached lab-wide queue runner**, on Sanaa's directive that the box must not
sit idle. **With no agent watching a detached run, `STATUS.<case>` is the ONLY
evidence the run terminated cleanly — it IS standing rule 4's `rc = 0` limb.**
`launch_k0f.sh` therefore takes its case directory, cap and ranks as arguments,
hard-codes no rung, and writes the name `mark_done_*.py` already parses, so it
drops into that runner unchanged.

**AND THE §R6.2 MEASUREMENT IS RELEVANT TO THAT RUNNER, NOT ONLY TO K0f.** The
description relayed to this lane was that the runner *"uses `setsid` and
captures rc into `STATUS.<case>`"* — which is exactly the composition measured
above to return 0 unconditionally. **Referred to the supervisor to relay to
cfd.** This lane changed nothing outside its own territory.

### R6.6 Driven, nine arms

`bash scripts/launch_k0f_selftest.sh` — **9 passed, 0 failed**: clean `rc=0`;
`rc=7` on a non-zero exit; `rc=139` on SIGSEGV; `rc=124` on expiry; **DETACHED, a
crashing solver still records `rc=7`**; the detached child proved to be in a new
session id; a pre-flight refusal writes **no** STATUS; a missing `0/T` refuses; a
non-serial `--ranks` refuses.

**A launcher never shown able to write a NON-ZERO rc is a planted zero with no
control.** Every arm drives a real process to a real exit state through the real
launcher and reads the rc back off disk.

---

## 5. LADDER, and 6. DECOMPOSITION SEED

**Three levels are DEFINED** (§G.4) and **TWO ARE AUTHORISED** by this document:
**L1 and L2. L3 IS NOT AUTHORISED** (§8.3).

**Serial. `nProcs = 1`. No decomposition, on every case.** No
`decomposeParDict` is written, `decomposePar` is never run, the solver is
invoked directly rather than through `mpirun`. **There is no partitioner,
therefore no seed and no partition-dependence to record.** The launcher
**refuses** any `--ranks` other than 1, so this is asserted and not assumed.

**THE EIGHT AUTHORISED CASES:**

| case | closure | level | cells | `endTime` | purpose |
| --- | --- | --- | ---: | ---: | --- |
| `M1_c` | `kOmegaSST` | L1 | 25 600 | 40 000 | ladder |
| `M1_m` | `kOmegaSST` | L2 | 50 176 | 40 000 | ladder |
| `M2_c` | `RNGkEpsilon` | L1 | 25 600 | 40 000 | ladder |
| `M2_m` | `RNGkEpsilon` | L2 | 50 176 | 40 000 | ladder |
| `C_lam` | laminar | L2 | 50 176 | 40 000 | Charter 2c discrimination control |
| `B_hi` | `kOmegaSST`, floor 35.5 °C | L2 | 50 176 | 40 000 | the `ΔT` arbitration guard |
| `I_hi` | `kOmegaSST`, inlet `k`, `ε` × 4 | L2 | 50 176 | 40 000 | inlet-turbulence sweep |
| `M1_m_seed` | `kOmegaSST`, hot start | L2 | 50 176 | 40 000 | seed-perturbation CONTROL |

`M1_f` and `M2_f` (L3) are **defined and NOT authorised.**

**A CONSEQUENCE REGISTERED RATHER THAN DISCOVERED: `analyse_k0f.py` REFUSES
(exit 2) unless all TEN `DONE` markers are present, and its graded level is
`M1_f` — an L3 case. UNDER THIS REGISTRATION THE COMPARATOR CANNOT RUN AT ALL.**
What K0f as authorised produces is the meshes, the solves, the rc-captured
completion records, `checkMesh` birth certificates, convergence histories,
achieved `y⁺` and the pre-flight and mesh refusals — **not a graded row, not a
Roache triple and not a GCI.** §8.3 records what adding L3 would cost.

---

## 7. CRITERIA — CARRIED OVER UNCHANGED

**7.1 Convergence — the residual is NOT the instrument.** `residualControl` is
not written. **CONVERGED** means the largest change of any cell value of `T`,
and separately of `U`, between the checkpoints at `endTime − 4000` and
`endTime` is at most **`1e-6` of that field's range**. `endTime 40000`,
`deltaT 1`, `writeInterval 4000`, `purgeWrite 2`. **One** extension of +20 000
iterations is registered; a second is not authorised. **The decision to extend
is taken on the convergence state alone, never with a graded value in view.**

**7.2 Strict completion rule with the age guard**, all seven clauses, and the
registered per-closure completion field sets — `kOmegaSST`
`T U p_rgh alphat nut k omega phi`; `RNGkEpsilon`
`T U p_rgh alphat nut k epsilon phi`; laminar `T U p_rgh alphat phi`. **No
exemption and no field substitution may be inferred at grading time**, and
`mark_done_k0f.py` refuses (exit 2) rather than infer one.

**7.3 Roache triple gating**, standing rule 5, at `Fs = 1.25`, unchanged — and
**unreachable under this registration** (§0, §5).

**7.4 Planted-zero control.** The three registered plants P1/P2/P3 are carried
unchanged, into the field on disk, by line index, read back through the
production reader.

**7.5 Order of operations, and the comparator freeze.**
`check_k0f_mesh.py` → `build_k0f.py --preflight` → `launch_k0f.sh` →
`mark_done_k0f.py` → `check_k0f_extraction_equivalence.py` →
`analyse_k0f.py`. **Every comparator is hashed against its committed blob before
analysis**; the grading path is fixed at this document's commit.

**7.6 No verdict may be assigned by the lane that runs this.**

### 7.7 THE GRADING PATH, FIXED AT THIS COMMIT (standing rule 2)

Committed at `HEAD` before this document, so this document can name them:

| instrument | committed blob sha1 |
| --- | --- |
| `scripts/analyse_k0f.py` | `764dedc6dadf38660becbc5d727184a363eb2d77` |
| `scripts/build_k0f.py` | `0881fa08163f984283ba1db5cb31ae488d1bdf5e` |
| `scripts/check_k0f_mesh.py` | `587e6693d7d2f38d8b4b64cbfadc82d7160c8ee8` |
| `scripts/mark_done_k0f.py` | `f01e3fce18c982bdd14038598a0f10c33465d924` |
| `scripts/check_k0f_extraction_equivalence.py` | `31c902de918e0c7855b0f97285a5393c27d25248` |
| `scripts/check_k0f_instrument_standard.py` | `8fa5bd2246ff370dcc6ab4ce925621f1e603d559` |
| `scripts/launch_k0f.sh` | `25071702e6c4b49442ed82af59e7d39488eaad56` |
| `scripts/launch_k0f_selftest.sh` | `c54b7f9af0d0d2493d69ab5ccef47835ba56e272` |

**Each descends from a named K0d ancestor at HEAD `e2250a6f`, verified CLEAN
against its HEAD blob before copying**, and every K0f instrument's header states
which. `launch_k0f.sh` and `launch_k0f_selftest.sh` have **no ancestor** — K0d
had no launcher, and that absence is the defect they repair.

**THE K0d INSTRUMENTS ARE NOT EDITED.** All five stay byte-unchanged; other
records cite them.

---

## 8. COST, REGISTERED BEFORE THE RUN (standing rule 12)

**Basis:** sibling **K0cS**, measured on this box 2026-08-18 at **1.593e-6 s per
cell-iteration**, **× 1.6 developed-flow contingency**; **POINT rate 2.549e-6 s
per cell-iteration; CEILING rate 2 × POINT.** Carried unchanged from
`K0d_REREGISTRATION.md` §8 — the per-case lines below are its own figures, not
re-derived, because nothing in this document changes a cell count or an
iteration count.

| case | cells | **core-min** |
| --- | ---: | ---: |
| `M1_c` | 25 600 | 43.50 |
| `M2_c` | 25 600 | 43.50 |
| `M1_m` | 50 176 | 85.27 |
| `M2_m` | 50 176 | 85.27 |
| `B_hi` | 50 176 | 85.27 |
| `I_hi` | 50 176 | 85.27 |
| `M1_m_seed` | 50 176 | 85.27 |
| `C_lam` | 50 176 | **63.95** — 0.75 × the L2 turbulent line, a registered **ESTIMATE**, a named calibration item |
| **SOLVER SUBTOTAL `S`** | | **577.30** |

| instruments, bounded | core-min |
| --- | ---: |
| meshing | 2.00 |
| `check_k0f_mesh.py` mesh reader | 0.50 |
| `mark_done_k0f.py` + `analyse_k0f.py` + selftests | 1.00 |
| dual-scheme extraction (§A1.3b) | ≤ 8.00 |
| **NEW: the standing pre-grading equivalence gate, `check_k0f_instrument_standard.py`, `launch_k0f_selftest.sh`** | **≤ 2.00** |
| **`I` = instruments, bounded** | **13.50** |

**The new line's basis, MEASURED at this registration and stated as a bound, not
as a measurement of the run:** the equivalence gate on one L1 case took **1.07
wall s** (0.018 core-min at `ranks = 1`); the instrument standard **1.35 wall
s**; the launcher selftest **3.48 wall s**; `analyse_k0f.py --selftest` **0.16
wall s**. ≤ 2.00 core-min bounds them generously.

```
  REGISTERED POINT   = S + I  = 577.30 + 13.50 =   590.80 core-min
  REGISTERED CEILING = 3S + I = 1731.90 + 13.50 = 1745.40 core-min
```

`CEILING = 2S` (first pass at the ceiling rate) `+ S` (one registered
continuation reserve) `+ I`, the structure carried from §A2.2b.

**Derived dollars at the owner-reported $0.0513/core-h — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5; this box cannot read its own billing):

```
  POINT     590.80 / 60 =  9.8467 core-h  x $0.0513 = $0.5051
  CEILING  1745.40 / 60 = 29.0900 core-h  x $0.0513 = $1.4923
```

**`cost_basis`:** the per-cell-iteration rate is **MEASURED** (K0cS pilot on this
box). The $0.0513/core-h rate is **REPORTED-BY-OWNER**. The dollar figures are
**DERIVED, NOT MEASURED**. The `C_lam` 0.75 laminar factor, the 1.6×
developed-flow contingency, the §9 memory estimates, the ≤ 24 core-s per
extraction and the ≤ 2.00 new-instrument bound are all **named calibration
items** and none is called measured.

**Sanaa has lifted cost constraints this session and nothing here stops to save
compute. Every run is still costed and still calibrated** (rule 12) — a blanket
is not a per-item read (rule 9).

### 8.1 THE CARRIED OUTER RUNAWAY GUARD

**R7 directs that K0d's 2 748.64 core-min ceiling be carried as K0f's own
runaway guard. It is carried, and it does not bind.**

| figure | status |
| --- | --- |
| **1 745.40 core-min** | **REGISTERED K0f CEILING**, derived from this rung's own eight cases. **THIS BINDS FIRST.** |
| 2 748.64 core-min | **CARRIED OUTER RUNAWAY GUARD** per R7, from `K0d_REREGISTRATION.md` §A2.2b. Never reached under this scope. |

**Registering the lower derived figure as the operative cap is a TIGHTENING**, and
carrying the outer guard costs nothing.

### 8.2 STOP RULES AND THE CAPS AS ENFORCED

1. **THE TOTAL CAP IS 1 745.40 core-min. Reaching it STOPS THE RUN**, reported
   to the supervisor with the unrun cases named. **An overrun does not get a new
   budget** (rule 12).
2. **PER-CASE HARD STOP: 10× that case's POINT line.** **A CAP ENFORCED AS A
   WALL-CLOCK `timeout` IS NOT A CORE-MINUTE CAP UNLESS IT IS CONVERTED:**
   `timeout = cap_core_min × 60 ÷ ranks`, `ranks = 1` throughout.

| case | 10× POINT (core-min) | **enforced `timeout` (s)** |
| --- | ---: | ---: |
| `M1_c`, `M2_c` | 435.00 | **26 100** |
| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 852.70 | **51 161** |
| `C_lam` | 639.50 | **38 370** |

   These reproduce `build_k0f.py`'s frozen `FROZEN_TIMEOUT_S` table exactly.
   Both caps are in force; whichever is reached first stops the run.
3. **RE-ESTIMATE TRIGGER at 1.6× a case's own line.** It does not stop the run;
   it forces the estimate to be re-made and the difference disclosed **before**
   the next case launches.
4. **A case that cannot meet §7.1 after its one registered continuation has its
   rows REPORTED AS REFUSED with the measured spread.**

**No authorised K0f case exceeds 3 600 wall s at the POINT rate** (the longest
is `M1_m` at 5 116 wall s at the CEILING rate), so a row over 3 600 s is
reported and examined rather than assumed to be a stall.

### 8.3 WHAT L3 WOULD COST, REGISTERED SO THE DECISION CAN BE MADE FROM ARITHMETIC

**R7 excludes L3 on the ground that *"two L3 caps at 1 675.50 each exceed the
whole ceiling"*. THIS LANE CANNOT REPRODUCE THAT READING, and the disagreement
is registered rather than argued away.**

**1 675.50 core-min is the per-case 10× RUNAWAY GUARD for an L3 case, not its
expected cost.** An L3 case's POINT line is **167.55 core-min**; the two
together are **335.10 core-min**. `K0d_REREGISTRATION.md` §8.1 already states
that for every case except the two coarse ones **the rung cap binds BEFORE the
10× per-case threshold**, and both caps are in force.

**AND THE CARRIED 2 748.64 CEILING WAS ITSELF DERIVED WITH BOTH L3 CASES IN
IT.** §A2.2b's solver subtotal `S = 912.38` is `577.30 + 335.10 = 912.40` — this
document's eight cases plus the two L3 cases, to rounding. `3 × 912.38 + 11.50
= 2 748.64`. **The carried ceiling exists BECAUSE of L3.**

| scope | `S` | CEILING `3S + I` | derived $ |
| --- | ---: | ---: | ---: |
| **as registered (L1+L2, eight cases)** | **577.30** | **1 745.40** | **$1.4923** |
| with L3 (ten cases) | 912.40 | 2 750.70 | $2.3519 |

**ADDING L3 IS A FURTHER REGISTRATION AND IS NOT TAKEN BY THIS DOCUMENT.** It is
the supervisor's call, and the arithmetic above is what it would be made from.
**Without it the `G` column is unreachable and `analyse_k0f.py` cannot run
(§5).**

### 8.4 CALIBRATION OBLIGATION (rule 12), REGISTERED NOW

At rung completion the comparison is **not optional and a completion report
without it is incomplete**: actual core-minutes from `STATUS.<case>` and
`ExecutionTime`; the ratios **actual/POINT** and **actual/CEILING**; the gap
attributed; **waste and contention NAMED SEPARATELY and never absorbed into the
ratio** (`COMPUTE_BUDGET_CHARTER.md` §6); dollars derived at $0.0513/core-h and
**labelled derived**; landing as a row in **`docs/COST_CALIBRATION.md`**, id
**re-derived at append time** under the rule-10 private-index protocol — six
teams append continuously, and K0d's own row moved from a relayed `C-76` to an
actual `C-99` in the course of one night.

**K0d's row `C-99` is the standing prior for this rung:** predicted 87.00
core-min for two L1 cases, actual **105.10**, ratio **1.208**, attributed to
**rate** (measured 3.140e-06 and 3.019e-06 s/cell-iteration against the
registered POINT 2.549e-06) under 5–9 foreign solvers. **K0f's L1 cases should
be expected at ≈ 1.2× their POINT lines under comparable contention**, and that
expectation is registered here rather than discovered afterwards.

---

## 9. SCHEDULING

**REGISTERED CONCURRENCY CAP: 8.** One batch of the eight authorised cases,
serial, `nProcs = 1`. Memory, from the measured **2.4 kB/cell** rate
(`K0d_REREGISTRATION.md` §9.2; the ~60 MB baseline is **INFERRED from a
different solver** and the rate is **MEASURED** — the two statuses are not the
same status): L1 ~113 MB, L2 ~164 MB each; **eight concurrent ≈ 1.21 GB
estimated, ≈ 1.62 GB on the conservative bound**, against this family's standing
**12 GiB floor**. **If `MemAvailable` is under 14 GiB at launch the batch is
staged rather than fired whole** — a batch that OOMs is worse than a batch that
queues.

**THE UTILISATION DECAY IS REGISTERED IN ADVANCE, NOT DISCOVERED.** The ladder is
imbalanced (85.27 against 43.50), so the batch cannot hold Sanaa's 80–90 %
saturation band for its own window; the retiring cores **must be backfilled from
the team's queue** rather than the batch being inflated. **Under-loaded-with-a-
queue is the same defect as idle, at lower severity.**

**Contention is NAMED SEPARATELY at completion and never absorbed into the
actual/predicted ratio.**

---

## 10. DISCLOSURES — CARRIED UNSOFTENED

1. **The primary, Blay, Mergui and Niculae (1992), is `NOT OBTAINED`.** No
   graded verdict is reachable until it lands and is **title-page verified**
   (L-144). Obtaining it is Sanaa's alone and was not attempted.
2. **THE `G` COLUMN IS UNREACHABLE UNDER THIS REGISTRATION, and the ground for
   excluding L3 is a cost reading this lane could not reproduce** (§8.3).
   Recorded as a disagreement with the ruling it implements, not resolved by it.
3. **The `r21` margin at `nA = 18` is 0.059 %** (§G.5). It is exact integer
   arithmetic and cannot drift; the residual risk is a **block-band counting**
   question, which §G.6 requires be measured on the built mesh.
4. **The nA = 18 parity prediction is a MODEL of `blockMesh`, not `blockMesh`**,
   validated by reproducing the observed `nA = 17` failure byte-identically.
   §G.6's re-check on the built mesh is required, not optional.
5. **The §V equivalence result is measured on K0d's PRESERVED EVIDENCE**, on two
   cases that are themselves **NOT DONE**. It establishes that the reader is
   repaired. **It establishes nothing about K0f, which has not run.**
6. **A 124 exit cannot be distinguished from a solver that itself exits 124**
   (§R6.3). `wall` and `timeout_s` are a discriminator, not a proof.
7. **`RNGkEpsilon` takes high-Re wall functions against a `y⁺ ≤ 1` mesh.** The
   measured-and-reported `y⁺` window is the instrument that surfaces this; a
   case outside it is **REPORTED, not graded**.
8. **The `AMENDMENT 5` §A5.7.4 `ΔT` exposure is CARRIED, not closed.** If the
   primary establishes `ΔT = 20.5 K`, this rung ran at a `ΔT` 2.5 % low — a
   **DISCLOSED INPUT ERROR reported as one**, never a licence to widen a band.
9. **The Sutherland fluid-state argument is a CONSISTENCY argument, NOT an
   ATTRIBUTION.** Nothing here establishes that `ν = 1.569e-5` is the right
   viscosity for this experiment.
10. **`scripts/check_filing.py` reports 27 pre-existing filing violations across
    5 rules at this write. NONE is on a K0f path.** They are inspected and left
    for their owners (standing rule 10), not repaired here.
11. **The shared working tree carries other teams' uncommitted work** (closure,
    ansys-verification, cfd). **Inspected, never reverted.** Every K0f commit
    used the private-index protocol and named its own paths only.

---

## 11. WHAT THIS DOCUMENT DOES NOT DO

- **It authorises no solve.** The supervisor reads the three named diffs
  **personally, as diffs**, before any compute — an undelegatable check under
  `SUPERVISION_CHARTER.md` §3 that no throughput directive overrides. **Firing
  without it is a standing rule 2 violation.** The diffs are at
  `docs/campaigns/F14-cooling-ladder/K0f_DIFF_1..5_*.diff`.
- **It authorises no L3** (§8.3).
- **It edits no frozen file.** `K0d_REREGISTRATION.md`, `K0d_PREREGISTRATION.md`
  and all five amendments stay byte-unchanged, as do all five K0d instruments.
- **It touches no gate, band, threshold or label of K0d.** K0d's own verdict is
  the supervisor's to record; this document assigns none.
- **It does not touch condition D**, or any other refusal condition.
- **It deletes nothing.** Both preserved failed build trees and both `NOT DONE`
  L1 cases stay on disk.
- **It does not make §3C binding beyond this rung.**
- **It ran no solver.** Zero solver core-minutes. `K0f_runs/` does not exist.
  Rule 12's estimate-versus-actual calibration is **not triggered**, because no
  process completed. Instrument time spent writing and driving this registration
  is bounded by the ≤ 2.00 core-min line of §8 and is well under it.
- **It sent nothing** (standing rule 7). **Submissions remain PARKED.** Nothing
  was fetched from outside the box (standing rule 8) and no search for Blay 1992
  was made.
- **It touched no permission setting, no `CLAUDE.md` and no `.claude/`
  configuration** (standing rule 9). **No agent message is Sanaa's consent**, and
  the relayed directive about the detached queue is treated as scope information,
  never as authorisation.

**K0f IS REGISTERED, FROZEN AND UNFIRED.**

*Registered by a heat-transfer lane on the heat-transfer supervisor's ruling
R1–R7 of 2026-08-26 and its same-day addendum. Zero solver core-minutes. Zero
verdicts assigned.*

---

# AMENDMENT 1 — 2026-08-26, BEFORE FIRST COMPUTE. Version 1.0 → 1.1.

**lines whose number changed above this section: 0.** This amendment is
appended at the foot; nothing above it is edited (standing rule 6). **THE
ASSERTION WAS VERIFIED, NOT TYPED:** in the invocation that wrote this
amendment the first **949** lines of this file were compared **byte-for-byte**
against the committed blob `9b54abfe41af9c0755f2cd4268634ad01d8166e1` at the
captured `HEAD`, and the comparison was clean.

**IT IMPLEMENTS THE HEAT-TRANSFER SUPERVISOR'S REVERSAL OF R7 AND THE
AMENDMENTS TO R3, R4 AND R6 OF 2026-08-26**, on this lane's contradictions of
the same day. **It LOOSENS one thing — it authorises L3 — and that is the whole
point: without L3 this rung could earn nothing at all.**

## A1.0 The condition under which this amendment is legal, and HOW IT WAS CHECKED

Standing rule 2: before first compute, amendments are legal **and must state the
condition and how it was checked**. The condition is that **no K0f compute has
run.**

**THE METHOD, NOT ONLY THE CONCLUSION, as the ruling directs.** The check is a
`test -e` on the run directory that must not exist —
`verification/runs/F14-cooling-ladder/K0f_runs` — **re-proved inside this
amendment's own committing shell invocation and not cited from any upstream
message.** A bare `ABSENT` from that reader would be worthless on its own: **a
zero from a reader not shown able to see a non-zero is not evidence** (standing
rule 3). So the **identical reader, in the same invocation, is first pointed at
`verification/runs/F14-cooling-ladder/K0cS_runs`, which does exist, and must
return `PRESENT`.** Only then is the `ABSENT` on `K0f_runs` believed.

```
  PRESENT  verification/runs/F14-cooling-ladder/K0cS_runs   <- the planted control
  ABSENT   verification/runs/F14-cooling-ladder/K0f_runs    <- the condition
```

**The control is what makes the zero admissible.** Had the same reader returned
`ABSENT` on `K0cS_runs` too, the `ABSENT` on `K0f_runs` would have proved
nothing except that the reader was broken.

**This amendment alters NO band, NO threshold and NO label.** It alters **the
authorised level set** and, in consequence, **the cost registration** and **which
verdict columns are reachable**. §A1.7 states exactly what moved.

## A1.1 RULING — **R7 IS REVERSED. L3 IS AUTHORISED. THE FAMILY IS THREE LEVELS.**

**REGISTERED: L1, L2 and L3, all three, and all TEN cases** — `M1_c`, `M1_m`,
`M1_f`, `M2_c`, `M2_m`, `M2_f`, `C_lam`, `B_hi`, `I_hi`, `M1_m_seed`. §5's
"**TWO ARE AUTHORISED**" and its list of eight are **STRUCK**; §5's `M1_f` and
`M2_f` are no longer "defined and NOT authorised".

| case | closure | level | cells | `endTime` | purpose |
| --- | --- | --- | ---: | ---: | --- |
| `M1_f` | `kOmegaSST` | **L3** | 98 596 | 40 000 | ladder, **graded level** |
| `M2_f` | `RNGkEpsilon` | **L3** | 98 596 | 40 000 | ladder, **graded level** |

**§7.3 ROACHE TRIPLE GATING IS NOW REACHABLE AND IS IN FORCE, UNCHANGED**, in
the standing-rule-5 order, at **`Fs = 1.25`**, with the observed order and the
GCI printed and **no GCI quoted when the three values are not monotone**. A
triple that is not `CONVERGING` is **`NOT A RESULT`**, whatever its value, and
the gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the
reverse.

**Sanaa's standing grid ruling, recorded as received and relaxing nothing:** *"A
converging three-level family with observed order and GCI is the lab's gate
standard (Roache-standard minimum). More levels are a research option, never a
gate requirement."* K0f's family is **exactly three — confirmed, not extended.**

### A1.1a THE GROUND ON WHICH L3 WAS EXCLUDED WAS CIRCULAR, AND IT IS RECORDED AS CIRCULAR

R7 excluded L3 because *"two L3 caps at 1 675.50 each exceed the whole
ceiling"*. **Every step of that fails on inspection, and the supervisor accepted
all of it:**

1. **1 675.50 core-min is the per-case 10× RUNAWAY GUARD, not an expected
   cost.** An L3 case's POINT line is **167.55**; both together **335.10
   core-min**.
2. **335.10 is 12.2 % of the carried 2 748.64 ceiling**, not an overrun of it.
3. **AND THAT CEILING WAS ITSELF DERIVED WITH BOTH L3 CASES INSIDE IT.**
   `K0d_REREGISTRATION.md` §A2.2b's solver subtotal `S = 912.38` is
   `577.30 + 335.10` — the eight L1/L2 cases **plus the two L3 cases**.

> **L3 WAS EXCLUDED ON THE AUTHORITY OF A CEILING THAT EXISTS BECAUSE OF L3.**
> Recorded here in those terms, on the supervisor's own instruction that it be
> recorded as circular rather than quietly reversed.

4. **And there was never a cost argument to make.** Sanaa lifted cost
   constraints this session; a cap is a **runaway guard, not a budget gate**
   (`K0d_REREGISTRATION.md` §A2.2c).

**THE CONSEQUENCE HAD IT STOOD IS THE SHARPER POINT, and it is registered so the
class of error is not repeated:** without L3 there is no Roache triple, so no
`G`; `P` is unreachable while Blay 1992 is `NOT OBTAINED`; and `V` was closed by
measurement in §V. **K0f would have run eight cases and 577.30 core-min to earn
NOTHING** — the compute-that-cannot-become-a-result that this same supervisor
refused for K0d hours earlier.

## A1.2 THE COST, RE-DERIVED WITH L3 IN

**Re-derived from the registered per-case lines, not scaled.** The rate basis is
unchanged (K0cS, 1.593e-6 s per cell-iteration **MEASURED** on this box, × 1.6
developed-flow contingency, POINT rate 2.549e-6; CEILING rate 2 × POINT).

| case | cells | core-min |
| --- | ---: | ---: |
| `M1_c`, `M2_c` | 25 600 | 43.50 each |
| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 50 176 | 85.27 each |
| `C_lam` | 50 176 | 63.95 (ESTIMATE, 0.75 × the L2 turbulent line) |
| **`M1_f`, `M2_f`** | **98 596** | **167.55 each** |
| **SOLVER SUBTOTAL `S`** | | **912.40** |

**`I` = 13.50 core-min, UNCHANGED, and the reason is stated rather than
assumed:** every line of §8's instrument enumeration was **already sized for TEN
cases** — meshing 2.00 (ten), the mesh reader 0.50 (three levels), the
comparators 1.00, the dual-scheme extraction ≤ 8.00 (ten cases × two schemes),
and this document's new ≤ 2.00. Adding L3 adds no instrument.

```
  REGISTERED POINT   = S + I  =  912.40 + 13.50 =   925.90 core-min
  REGISTERED CEILING = 3S + I = 2737.20 + 13.50 = 2 750.70 core-min
```

**Derived dollars at the owner-reported $0.0513/core-h — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5; this box cannot read its own billing):

```
  POINT     925.90 / 60 = 15.4317 core-h  x $0.0513 = $0.7916
  CEILING  2750.70 / 60 = 45.8450 core-h  x $0.0513 = $2.3518
```

### A1.2a A 2.06 core-min DISCREPANCY AGAINST THE CARRIED GUARD, DECOMPOSED RATHER THAN ABSORBED

**The derived CEILING 2 750.70 is 2.06 core-min ABOVE the carried outer guard of
2 748.64** (§8.1). A reader is owed the cause, not the difference:

| component | core-min |
| --- | ---: |
| **this document's own new instrument line** (§8, the equivalence gate, the instrument standard, the launcher selftest) | **+2.00** |
| K0d's §8 subtotal rounding (`827.11` where its own per-case lines sum to `827.13`), tripled by `3S` | **+0.06** |
| **total** | **+2.06** |

**THE OPERATIVE RUNAWAY GUARD IS THE LOWER OF THE TWO — 2 748.64 core-min**
(derived $2.3501). Taking the **tighter** figure means the cap can stop the run
2.00 core-min before this document's own envelope, which is a **tightening**;
taking the higher one could be read as a ceiling chosen to make room for the
work it was about to authorise. **A cap is a runaway guard: a case that reaches
it is REPORTED TO THE SUPERVISOR, who decides** (`K0d_REREGISTRATION.md`
§A2.2c). **An overrun does not get a new budget** (standing rule 12).

### A1.2b PER-CASE HARD STOPS, WITH L3

**A CAP ENFORCED AS A WALL-CLOCK `timeout` IS NOT A CORE-MINUTE CAP UNLESS IT IS
CONVERTED:** `timeout = cap_core_min × 60 ÷ ranks`, `ranks = 1` throughout.

| case | 10× POINT (core-min) | enforced `timeout` (s) |
| --- | ---: | ---: |
| `M1_c`, `M2_c` | 435.00 | 26 100 |
| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 852.70 | 51 161 |
| `C_lam` | 639.50 | 38 370 |
| **`M1_f`, `M2_f`** | **1 675.50** | **100 530** |

These reproduce `build_k0f.py`'s frozen `FROZEN_TIMEOUT_S` table exactly, **the
L3 row included — it was already there.**

**THE TWO L3 ROWS EXCEED 3 600 WALL s BY DESIGN**: 10 052.8 wall s at the POINT
rate, 20 105.6 at the CEILING rate. `COMPUTE_BUDGET_CHARTER.md`'s over-3600
stall rule does **not** apply to them and **they are not to be cleaned as
stalls.** A stall here means `ExecutionTime` stops advancing, which
`STATUS.<case>` and the log detect separately. **Registered in advance so a
legitimate row is not cleaned later.**

### A1.2c CALIBRATION EXPECTATION, REGISTERED IN ADVANCE

K0d's row **`C-99`** measured **1.208 × POINT** on two L1 cases under 5–9 foreign
solvers, attributed to **rate** (3.140e-06 / 3.019e-06 s per cell-iteration
against the registered 2.549e-06), not to iteration count. **K0f is expected at
≈ 1.2 × its POINT lines under comparable contention**, i.e. ≈ **1 111 core-min**
against the 2 748.64 guard. That expectation is registered **now**, not
discovered afterwards, and **contention and waste are named separately at
completion and never absorbed into the actual/predicted ratio**
(`COMPUTE_BUDGET_CHARTER.md` §6).

## A1.3 §G.5's RATIONALE IS **STRUCK**; ITS DISPOSITION **STANDS**, WITH A NEW REASON

**STRUCK, and reproduced here so a reader sees what was withdrawn rather than
only what replaced it:** the draft's reason, adopted into §G.5, that *"a 0.06 %
margin sits well inside the range where the real geometry of a rebuilt graded
mesh could flip it"*, with the T8 `7/3` centroid analogy beside it.

**IT IS FALSE, and the correction was accepted by the supervisor.**
`condition_C` computes `r = (hi_cells / lo_cells) ** 0.5` from **INTEGER cell
counts counted off the mesh**. There is no floating geometry in it. **`r21` for
block A will read exactly `sqrt(4032/1920) = 1.449138` or it will not read 4032
cells at all.** The margin is **exact and cannot drift**. **The T8 analogy does
not transfer: that was a CENTROID ratio and this is a COUNT ratio.**

**THE REPLACEMENT REASON, which is the risk that is actually live:** condition C
can only flip **DISCRETELY**, if `_count_between` counts a different number of
`y` rows inside a registered block band — a **topology** question about whether
`blockMesh` places a `y` line exactly on 0.024 and on 1.022, **not a rounding
question**. §G.6's re-check on the built mesh measures precisely that.

**THE PRE-DECIDED FAILURE DISPOSITION IS UNCHANGED AND STANDS:**

> **If condition C reads the rebuilt mesh and `r21` lands ABOVE 1.45, the answer
> is NOT to widen condition C.** It is that **no `nA` satisfies all four
> conditions**, and **the mesh family must be re-chosen at a level above
> `nA`** — which is **a re-registration, not a repair**.

**A pre-decided disposition costs nothing and a disposition written after seeing
a failure is an accommodation.** The reason moved; the disposition did not.

## A1.4 §0's REACHABILITY TABLE IS AMENDED

| column | reachable | why |
| --- | --- | --- |
| **`V`** | **YES** | the extraction equivalence is **CLOSED BY MEASUREMENT** (§V.3, 8 of 8 AGREE); and with three levels the Roache/GCI arm is reachable too |
| **`G`** | **YES — CHANGED BY THIS AMENDMENT** | a CONVERGING three-level Roache triple with observed order and GCI at `Fs = 1.25` is a **grid property**, measurable without any reference |
| **`P`** | **NO** | Blay, Mergui and Niculae (1992) is **`NOT OBTAINED`** |

**THE BEST VERDICT THIS RUNG CAN REACH IS `GATE REACHED`, NAMING `P` — AND ONLY
`P` — AS THE UNREACHED COLUMN. IT CAN NEVER READ `HOLDS` IN THIS STATE.** §0's
"naming BOTH `P` AND `G`" is **STRUCK**.

**Obtaining Blay 1992 is from OUTSIDE THE BOX, is Sanaa's alone (standing rules
7 and 8), and IS NOT TO BE ATTEMPTED BY ANY AGENT.** No search was made and none
is authorised. **`V` and `G` are exactly the columns this lab is short of, and
that is a reason to RUN this rung, not a reason to withhold it.**

## A1.5 §5's COMPARATOR CONSEQUENCE IS **STRUCK**

§5 registered that *"`analyse_k0f.py` REFUSES (exit 2) unless all TEN `DONE`
markers are present, and its graded level is `M1_f` — an L3 case. UNDER THIS
REGISTRATION THE COMPARATOR CANNOT RUN AT ALL."* **That consequence is removed
by this amendment**: all ten cases are authorised, so the ten markers are
obtainable and `M1_f` exists. **The comparator can run.**

**AND NO INSTRUMENT CHANGES, WHICH IS THE PART THAT MATTERS FOR THE FREEZE.**
The refusal at ten markers, the graded level `M1_f`, the three-level `LEVELS`
tables in `build_k0f.py` and `check_k0f_mesh.py`, and the L3 rows of
`FROZEN_TIMEOUT_S` were **all already present** — the restriction to two levels
lived **only in the prose of §5**, never in the code. **THE GRADING PATH IS
THEREFORE BYTE-UNCHANGED AND EVERY BLOB SHA IN §7.7 REMAINS VALID.** This
amendment cannot be accused of moving the grading path, because it does not
touch it.

## A1.6 SCHEDULING, WITH TEN CASES

**REGISTERED CONCURRENCY CAP: 9** — `K0d_REREGISTRATION.md` §9.1's figure,
carried unchanged, so **this amendment raises no concurrency cap.** Ten cases
against a cap of nine means **one case QUEUES and is launched as the first
retires.** Serial, `nProcs = 1`. Memory from
the **MEASURED** 2.4 kB/cell rate (the ~60 MB baseline remains **INFERRED from a
different solver** — the two statuses are not the same status):

| level | cases | estimate | conservative bound |
| --- | ---: | ---: | ---: |
| L1 | 2 | ~113 MB each | ~162 MB each |
| L2 | 6 | ~164 MB each | ~220 MB each |
| L3 | 2 | ~265 MB each | ~337 MB each |
| **all ten concurrent** | | **~1.70 GB** | **~2.26 GB** |

against this family's standing **12 GiB floor**. **If `MemAvailable` is under
14 GiB at launch the batch drops to the eight non-L3 cases and the two L3 cases
queue behind them** — a batch that OOMs is worse than a batch that queues.

**AND THE HEADROOM IS A MEASUREMENT ARGUMENT, NOT A COST ONE, WHICH IS WHY IT
SURVIVES SANAA'S LIFTING OF COST CONSTRAINTS INTACT.** Nine of sixteen cores
plus the five held by other teams is `14/16 =` **87.5 %**, inside Sanaa's 80–90 %
band. Saturating the box past that would inflate the per-cell-iteration rate
that **§A1.2c's calibration expectation is measured against**, and a cost
calibration taken on a contended box measures the contention, not the estimate.
**Leaving headroom preserves the wall-clock basis the calibration depends on.**

**THE UTILISATION DECAY IS REGISTERED IN ADVANCE, INCLUDING THE UNFLATTERING
PART.** The ladder is imbalanced (167.55 against 43.50), so mean K0f occupancy
over its own critical path is `912.40 / 167.55 =` **5.45 cores. K0f ALONE CANNOT
HOLD SANAA'S 80–90 % SATURATION BAND FOR ITS OWN WINDOW**, and the retiring
cores **must be backfilled from the team's queue** rather than the batch being
inflated. **Under-loaded-with-a-queue is the same defect as idle, at lower
severity.**

**Contention measured at this write, and NOT rationalised:** four foreign
solvers are live on the box (three `buoyantBoussinesqSimpleFoam`, one
`simpleFoam`), untouched and not reniced. **The box is not idle**, and the
staging arithmetic must be re-taken at launch rather than carried from this
document.

## A1.7 WHAT MOVED, AND IN WHICH DIRECTION

**THIS AMENDMENT LOOSENS ONE THING AND THAT IS ITS PURPOSE.** It is stated
plainly rather than dressed as a tightening:

- **THE AUTHORISED LEVEL SET WIDENS**, from two levels and eight cases to three
  levels and ten. **This is a LOOSENING**, taken by the supervisor, legal only
  because no compute has run (§A1.0), and taken because the narrower scope could
  **earn nothing**.
- **THE COST REGISTRATION RISES**: POINT 590.80 → **925.90**; CEILING 1 745.40 →
  **2 750.70**, with the operative runaway guard at the **lower** 2 748.64.
- **THE REACHABLE COLUMN SET WIDENS**: `G` becomes reachable (§A1.4).
- **§G.5's RATIONALE IS WITHDRAWN AND REPLACED** by a strictly more accurate
  one (§A1.3), and the **disposition it supported is unchanged**.

**AND WHAT DID NOT MOVE:**

- **NO BAND, THRESHOLD OR LABEL.** Every band of §4 stands byte-unchanged.
- **NO REFUSAL CONDITION.** Condition D is untouched. Conditions A–G stand.
- **THE PHYSICS.** `ν` = 1.569e-5, `β` = 1/298, `T_ref` = 298.00 K, `Pr` = 0.71,
  `Pr_t` = 0.85, `ΔT` = 20.0 K, `Ra` = 2.135970e9 derived-and-reported.
- **THE MESH.** `nA` = 18, `nB` = 192, `Ny` = 224, 50 176 cells, `R21` =
  1.400000, `R32` = 1.401786, the first-wall-cell column — all as §G.4.
- **THE GRADING PATH.** Byte-unchanged; §7.7's eight blob shas remain valid
  (§A1.5).
- **GROUND `P`.** Blay 1992 is still `NOT OBTAINED`. Nothing was searched for,
  fetched or requested.

## A1.8 WHAT THIS AMENDMENT DID NOT DO — each stated explicitly

- **IT LAUNCHED NOTHING.** No case directory, no mesh, no solver, no pid. **Zero
  solver core-minutes.** `K0f_runs/` does not exist (§A1.0). Rule 12's
  estimate-versus-actual calibration is **not triggered**, because no process
  completed.
- **IT DOES NOT AUTHORISE THE FIRE.** The supervisor's undelegatable
  `SUPERVISION_CHARTER.md` §3 reads of **DIFF 1 (the wall reader)** and **DIFF 3
  (the completeness assertion)** are **OUTSTANDING**. **DIFF 2 (the launcher)
  was read personally and CLEARED on 2026-08-26.** **No solver may start until
  all three are cleared**, and firing before that is a standing rule 2
  violation.
- **It edited no frozen file.** `K0d_REREGISTRATION.md`,
  `K0d_PREREGISTRATION.md`, all five K0d amendments and all five K0d instruments
  stay byte-unchanged, verified in this invocation.
- **It edited nothing above its own heading** in this file; the 949-line prefix
  was verified byte-for-byte against the committed blob.
- **It touched no other repository file.** Not `docs/LAB_STATE.md`, not
  `docs/DOCKET.md`, not `docs/LESSONS.md`, not `docs/COST_CALIBRATION.md`. **No
  lesson, docket or record id was pre-assigned or reserved.**
- **It changed no instrument.** The grading path is byte-unchanged (§A1.5).
- **It sent nothing** (standing rule 7). **Submissions remain PARKED.** Nothing
  was fetched from outside the box (standing rule 8).
- **It touched no permission setting, no `CLAUDE.md` and no `.claude/`
  configuration** (standing rule 9). **No agent message is Sanaa's consent** —
  the supervisor's ruling is a supervisor's ruling, exercised inside a
  supervisor's own authority over level set and cost registration, and this
  amendment does not claim otherwise.

*Amendment written by a heat-transfer lane on the heat-transfer supervisor's
reversal of R7 and amendments to R3, R4 and R6, 2026-08-26, before first
compute. Zero solver core-minutes. Zero verdicts assigned.*

---

# AMENDMENT 2 — 2026-08-26, BEFORE FIRST COMPUTE. Version 1.1 → 1.2.

**lines whose number changed above this section: 0.** Appended at the foot;
nothing above is edited (standing rule 6). **THE ASSERTION WAS VERIFIED, NOT
TYPED:** the first **1 299** lines were compared byte-for-byte against the
committed blob at the captured `HEAD` in this amendment's own committing shell
invocation, and the comparison was clean.

**IT REGISTERS THE REPAIR OF A GRADING-PATH INSTRUMENT — `launch_k0f.sh` — AND
IT MOVES A BLOB SHA IN §7.7.** That is why it is an amendment and not a silent
edit.

## A2.0 The condition, and how it was checked — WITH A PLANTED POSITIVE

Standing rule 2: before first compute, amendments are legal **and must state the
condition and how it was checked.**

**THE CONDITION: no K0f compute has run.** Attempt 1 fired seven cases and
**every one died at `exec`**. Checked three independent ways, in the committing
invocation:

```
  numeric time directories under K0f_runs      : 0
  log.solve files containing a "Time = " line  : 0
  STATUS files reporting wall=0                : 7 of 7   (rc=127 on every one)
```

**AND THE ZERO IS NOT BELIEVED UNTIL THE READER IS SHOWN ABLE TO SEE A
NON-ZERO** (standing rule 3, L-337). **The identical three readers were pointed
at `K0d_runs`, which really did run 40 000 iterations:**

```
  numeric time directories under K0d_runs      : 4        <- non-zero
  log.solve files containing a "Time = " line  : 2        <- non-zero
  last Time in K0d_runs/M1_c/log.solve         : 40000    <- the positive
```

**A condition statement whose reader cannot see a positive is not a condition
statement; it is a formatting exercise.**

## A2.1 §2d.1 IS NOT INVOKED, AND THAT IS THE SUPERVISOR'S RULING

**This is a PRE-COMPUTE AMENDMENT.** The supervisor's test, applied for the
third time tonight and answered consistently: **can the change move a number?**

**It cannot.** Zero iterations ran; no graded value exists; no completion marker
exists. **Sourcing an environment changes WHETHER THE SOLVER CAN BE FOUND, never
WHAT IT COMPUTES.** `VERIFICATION_CHARTER` §2d.1 is a narrow exception for a
grading-path change that **moves a number**, and **invoking it where it is not
needed stretches it** — the same answer this supervisor gave for T8's
`assert`→`exit 2` conversion and for T4's glob idiom.

## A2.2 THE DEFECT, AND WHY EVERY ARM OF ITS SELFTEST PASSED

**Attempt 1: seven cases fired, all seven `rc=127 wall=0 checkMesh_rc=na`**,
`"timeout: failed to run command 'buoyantBoussinesqSimpleFoam': No such file or
directory"`. **`launch_k0f.sh` sourced NO OpenFOAM environment** — `grep -c
'etc/bashrc|WM_PROJECT'` returned **0**. A wrapper re-exec'd under `setsid`
inherits no login shell.

**IT IS AN EXEC FAILURE, NOT A SOLVE FAILURE.** Zero iterations on every arm.

**AND THE rc CAPTURE WORKED — THIS IS ITS FIRST REAL FAILURE AND IT PASSED.**
`rc=127` was captured truthfully and written atomically, and `checkMesh_rc=na`
recorded honestly that `checkMesh` was equally unreachable **rather than
inventing a pass.** The instrument reported its own environment's absence
correctly; the environment was the defect.

> **WHY NINE GREEN ARMS PROVED NOTHING: EVERY ARM INSTALLED A FAKE SOLVER ON
> PATH. A LAUNCHER SELFTEST THAT SUPPLIES ITS OWN FIXTURES IS TESTING THE
> LAUNCHER AGAINST ITSELF.** It proves the code paths and says nothing about the
> one thing a launcher exists to do — **reach a real solver in a real
> environment.**

**IT IS THE SAME SHAPE AS THREE FAILURES ALREADY ON THIS RUNG'S RECORD**, and
the repetition is the finding, not the instance: K0d's `blockMesh` readability
arm passed while `0/U` was unreadable **because `blockMesh` never reads `0/`**;
the `-O` lesson, where a passing selftest proves only the clean path **and the
clean path is exactly the one an evaporated guard still walks**; and T4's
launcher, which failed the same night on a shell glob matching `0.orig` **with a
green selftest of its own**. **Two frozen launchers, two green selftests,
neither able to launch a single real case.** Every one exercised the channel the
author was thinking about rather than the channel that consumes the artifact.

## A2.3 THE REPAIR, AND THE SECOND DEFECT THE NEW ARM CAUGHT BEFORE IT FIRED

**REGISTERED, three parts, and the refusal is the point rather than the
sourcing:**

1. **`--foam-bashrc`**, default `/usr/lib/openfoam/openfoam2606/etc/bashrc`,
   carried across the detaching re-exec. **An absent environment file REFUSES.**
2. **The solver is RESOLVED and REFUSES if unresolvable** — `command -v` after
   sourcing, and the run uses the **absolute** resolved path, recorded in STATUS
   as `solver_path=`. **Sourcing alone would turn a loud 127 into a quiet
   success-until-it-is-not.**
3. **AN UNREACHABLE SOLVER WRITES NO STATUS.** Nothing ran, so there is no rc,
   and inventing one is the back-dating this file exists to prevent. **`rc=127`
   is a solver that ran and failed; an unresolvable solver never started, and
   the two must not read alike.**

### A2.3a THE NEGATIVE-CONTROL ARM CAUGHT A DEFECT IN THIS VERY REPAIR

**REGISTERED AS REQUIRED: the launcher selftest carries an arm that resolves the
REAL solver binary on the REAL PATH, with no fixture, and REFUSES if it cannot.**

**ON ITS FIRST RUN IT FAILED — ON THE REPAIR ABOVE.** `launch_k0f.sh` sets
`-u` at line 58, and **MEASURED ON THIS BOX** the OpenFOAM bashrc aborts under
`set -u`:

```
  /usr/lib/openfoam/openfoam2606/etc/bashrc: line 184: WM_PROJECT_DIR: unbound variable
```

**So the first version of the repair sourced an environment that silently did
not load, and the solver was still not on PATH.** `set -u` is now lifted across
the source and restored immediately after.

**THE ARM ORDERED AS A CONSEQUENCE OF ATTEMPT 1 CAUGHT THE DEFECT IN ATTEMPT
1's OWN REPAIR, BEFORE ATTEMPT 2 FIRED.** That is the whole argument for it, and
it cost nothing.

**Selftest now 13 arms, 13 passing**, including: the real solver resolving to
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/buoyantBoussinesqSimpleFoam`;
the launcher reaching it with `rc != 127` and `solver_path` recorded; an
unresolvable solver refusing with **no STATUS**; and an absent `--foam-bashrc`
refusing.

### A2.3b THE GRADING PATH MOVES, AND §7.7 IS AMENDED

**`scripts/launch_k0f.sh` and `scripts/launch_k0f_selftest.sh` change; the other
six instruments do not.** §7.7's two launcher rows are **STRUCK** and replaced
by the blob shas committed with this amendment. **The six comparator and builder
shas are unchanged and remain valid** — no reader, grader, mesh check or builder
is touched, so **nothing that produces or judges a number moves.**

## A2.4 CLAUSE 7 IS NOT WEAKENED; THE CASES ARE REBUILT

**`mark_done_k0f.py` clause 7 refuses a relaunch because `0/` now exists on all
ten. THE GUARD IS RIGHT.** A case whose `0/` predates its own launch cannot be
dated by its own `0/T`, so its age guard is unevaluable. **Relaxing a refusal
condition because the cases cannot satisfy it is the exact move forbidden for
condition D: if anything moves, the cases move, never the guard.**

**PRESERVED, THEN REBUILT**, on this team's own K0d precedent of keeping two
failed build trees rather than deleting them:

- **`verification/runs/F14-cooling-ladder/K0f_runs.attempt1_exec_127_FAILED`** —
  ten case directories, **seven `rc=127` STATUS files**, seven `log.solve`.
  **The STATUS files are evidence and are the record of what a correct rc
  capture looks like on a real failure.** Nothing is deleted.
- All ten cases are then rebuilt from `build_k0f.py` so each is armed fresh
  immediately before its own solve.

**THE TEN `polyMesh` TREES ARE UNAFFECTED** — `blockMesh` writes
`constant/polyMesh`, never a time directory — **so the meshing is not repeated
and §G.6's measured result stands: condition D passes on all six L2 cases at
`nA = 18`, floor/ceiling/leftWall/rightWall all 7.864662e-04, 0.000 % off, and
condition C reads block A `1920→4032, r = 1.4491` from the mesh.**

**Meshing waste stays NAMED at ~0.2 core-min and is NEVER absorbed** into any
actual/predicted ratio (`COMPUTE_BUDGET_CHARTER.md` §6). **Zero solver
core-minutes were consumed by attempt 1** — `wall=0` on all seven.

## A2.5 `FROZEN_TIMEOUT_S`'s L2 ROW — DISCLOSED, DELIBERATELY NOT REPAIRED

**The frozen table enforces 51 161 s on the L2 row where the registered
conversion `cap × 60 ÷ ranks` gives 51 162.0 s.** Inherited from K0d.

| cap (core-min) | frozen table | `cap × 60 ÷ ranks` | delta |
| ---: | ---: | ---: | ---: |
| 435.00 | 26 100 | 26 100.0 | 0 |
| **852.70** | **51 161** | **51 162.0** | **−1.0** |
| 639.50 | 38 370 | 38 370.0 | 0 |
| 1 675.50 | 100 530 | 100 530.0 | 0 |

**THE DIRECTION IS THE RULING. One second TIGHTER can only stop a run EARLIER,
never later.** It cannot cause an overrun; at worst it cap-stops one second
early out of 51 161 (0.002 %). **A tightening is never the direction that needs
repair**, and repairing it would move a grading-path blob for nothing.

> **THIS IS RECORDED WITH ITS REASONING ATTACHED SPECIFICALLY SO THAT NOBODY
> LATER "FIXES" IT INTO A LOOSENING.** An unexplained conservative number is
> exactly the kind of thing a future tidy-up turns into a real defect.

## A2.6 WHAT THIS AMENDMENT DID NOT DO

- **It launched nothing.** Zero solver core-minutes at this write.
- **It moved no band, threshold, cap or label.** POINT 925.90 and CEILING
  2 750.70 stand, with the operative runaway guard at 2 748.64 (§A1.2a).
- **It moved no refusal condition.** Condition D untouched; clause 7 untouched
  and deliberately not weakened.
- **It changed no reader, grader, builder or mesh check.** Six of eight §7.7
  shas are unchanged.
- **It deleted nothing.** Attempt 1's tree is preserved whole.
- **It edited no peer's file.** A peer lane's uncommitted
  `scripts/check_launcher_can_launch.py` was found at a path this lane had also
  written; **it was inspected, verified intact, and left alone** (standing rule
  10). This lane does not ship a duplicate of it.
- **It sent nothing** (rule 7); **fetched nothing** (rule 8); **touched no
  permission setting, `CLAUDE.md` or `.claude/` config** (rule 9).

*Amendment written by a heat-transfer lane on the heat-transfer supervisor's
triage ruling of 2026-08-26, before first compute. Zero solver core-minutes.*
