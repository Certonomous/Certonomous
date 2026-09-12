# MRF_R4 — THE BLADE-THICKNESS RUNG: our tank rebuilt at `t/D = 0.0155`, graded against an EXPERIMENT at our own ratios

<!-- ===================== STRIKABLE DRAFT BANNER — BEGIN ===================== -->
> ~~**STATUS: FREEZE-READY DRAFT. NOT FROZEN. NOT LAUNCHED. NOT A GATE YET.**~~
> 🔴 **STRUCK AT THE FREEZE, 2026-09-12T20:41:26Z, BY THE cfd-SUPERVISOR PERSONALLY.**
> **THIS DOCUMENT IS FROZEN. §11 is the freeze attestation and GOVERNS.** The banner is
> struck in place rather than deleted, per its own instruction that it *"is struck whole
> at the freeze"* — and left legible so a reader can see what it said. **A lane found it
> still standing in the blob I had frozen and REQUESTED the strike rather than taking it,
> because striking it asserts something about a supervisor's own check 4. Correct.**
<!-- ====================== STRIKABLE DRAFT BANNER — END ====================== -->

- **Case family:** `navier_class` / `MRF`. **Rung R4**, and it is sequenced
  **BEFORE** the R3 zone sweep (`cases/navier_class/MRF/R3/MRF_R3_ZONE_SENSITIVITY_DRAFT.md`),
  which stays drafted and unlaunched.
- **Predecessor:** `verification/campaign/MRF_R2_PREREGISTRATION.md` — verdict
  **`NOT A RESULT`** (`ET8000` row; fine level not iteratively converged, triple
  `DIVERGENT` at observed order −0.297).
- **Reference registration:** `verification/campaign/MRF_PAPER_REGISTRATION_REID2025.md`,
  especially §11.
- **Inputs:** `cases/navier_class/MRF/` (generator `mesh/generate_geometry.py`,
  thin-feature override proved inert in §3.1).
- **Outputs (none yet):** `verification/runs/navier_class/MRF/R4/`

---

## 1. THE ONE CHANGE, AND WHY IT IS THE WHOLE RUNG

**R4 changes exactly one number:** the blade, disc and baffle thickness, from
`t = 0.004 m` (`t/D = 0.0400`) to **`t = 0.00155 m` (`t/D = 0.0155`)**.

Everything else is held, and the holding is the experiment:

- **the MRF zone stays at 1.200 D diameter × 2.00 W thick** — `topoSet`
  `cylinderToCell`, `radius 0.060`, `z 0.080 → 0.120`, byte-identical to R2's.
  **The zone is not the mechanism** (`…REID2025.md` §5: the paper's own Fig. 12 has
  `Np` *rising* 5.4 → 6.2 across our zone size, so it predicts the wrong sign) and
  **varying it in the same arm would test two things and settle neither**;
- tank, impeller diameter, clearance, fill height, baffle count and width, shaft,
  blade length and width, `N`, `ν`, `ρ`, closure, wall treatment, schemes,
  relaxation, `endTime`, solver and OpenFOAM build: all unchanged from R2.

**Why this one number.** At `t/D = 0.0155` our geometry becomes **identical, ratio
for ratio, to the small test rig of Beshay et al. (2001)** — a stirred tank whose
power number was **measured with a strain-gauge torquemeter**. Once the geometry
is the same, *"different tank"* stops being an available explanation for any gap.
That is the point of the rung and it is Sanaa's.

---

## 2. WHAT IS **NOT** DONE HERE, BY RULING

**THE THREE-LEVEL GRID FAMILY IS DROPPED.** Sanaa, 2026-09-12, relayed:

> *"we dont need to do the fine mesh conv, provided that we dont have exactly the
> same thickness or exactly same dimensions; if we do but we dont record the same
> values, thats an issue."*

Her reasoning, as the lane reads it and records it as her ruling and not as the
lane's: **a grid-convergence family is not owed while the geometry differs from
the reference, because there is no reference value we are entitled to land on** —
and once the geometry *matches*, the question that matters is whether we record
the reference value, not what our own grid extrapolates to. **R4 is therefore a
SINGLE-GRID run**, and no three-level family is drafted, frozen or launched.

### 2.1 WHAT A SINGLE GRID COSTS US IN VERDICT VOCABULARY — STATED BEFORE THE RUN

A single grid has **no Roache triple**, so the rule-5 machinery cannot run. The
honest consequence, registered in advance so it cannot be narrated afterwards:

- **`PASS` IS NOT CLAIMABLE BY THIS RUNG.** In this lab `PASS` means a
  `CONVERGING` triple landing inside a pre-registered band (CLAUDE.md rule 5).
  R4 has no triple, so it cannot earn one, whatever it lands on.
- The verdicts available are **`GATE REACHED`** (inside the §4 band, single grid,
  no grid-convergence claim), **`GATE FAIL`** (outside it), **`NOT A RESULT`**
  (the §5 iterative criterion refuses), **`BLOCKED`** (cannot complete),
  **`PENDING`** (not yet run).
- Every row, figure and certificate slot produced by this rung carries, on its
  face, **`SINGLE GRID — NO GRID-CONVERGENCE CLAIM`**. That is Sanaa's own
  certificate wording from the same directive (*"certificate slot honest (single
  grid, band pending)"*).
- **This mapping is the lane's conservative reading and is REFERRED to the
  verification supervisor**, because fixing what `GATE REACHED` may mean on a
  single grid touches a standard, and retiring or loosening a standard is reserved
  (CLAUDE.md, FIRST-ACTION RULE). **Nothing here loosens rule 5**; it declines to
  invoke it.

---

## 3. THE GEOMETRY CHANGE, AND THE PROOF IT TOUCHES NOTHING ELSE

`cases/navier_class/MRF/mesh/generate_geometry.py` gains an **override inserted
with an assert, never replacing the existing values** (CLAUDE.md rule 14). It is
**inert unless `MRF_FEATURE_THICKNESS_M` is set**, and it refuses outside
`[0.0005, 0.010] m` rather than meshing a feature it cannot honestly resolve.
`BAF_T`, `BLADE_T`, `DISC_T` remain on lines 36, 37, 38; the constants block
(lines 21–38) is untouched, so every existing citation by line still lands.

### 3.1 Controls run BEFORE the override was believed (CLAUDE.md rule 3)

| control | result |
|---|---|
| **inertness** — with the variable unset, regenerate all six surfaces and byte-compare against **the as-run R2 surfaces** at `…/R2/ET8000/fine/constant/triSurface/` | `tankWall`, `tankBottom`, `tankLid`, `baffles`, `shaft`, `impeller` — **all six IDENTICAL** |
| **the reader can see a non-zero** — set `0.00155` and re-compare | `impeller` **CHANGED**, `baffles` **CHANGED**, `tankWall` **UNCHANGED** (correct: the tank has no registered thickness) |
| **refusal arm** — set `0.02` | `AssertionError`, the run stops |
| **read-back from the written STL**, not from the requested value (`MESH_STANDARD` §9.2) — max \|y\| on the θ = 0 blade beyond the disc rim | default **4.000 mm, `t/D` 0.0400**; override **1.550 mm, `t/D` 0.0155** — **both MATCH** |

---

## 4. THE GATE — TWO REGISTERED RECORDS, NEITHER OVERWRITING THE OTHER

### 4.1 PRIMARY REFERENCE AND BAND (Sanaa's, and it is the gate)

**Beshay, Kratěna, Fořt & Brůha, *Power Input of High-Speed Rotary Impellers*,
Acta Polytechnica 41(6) 2001** — title page **rendered and read** (rule 15);
`docs/papers/stirred_tanks_and_mixing/beshay_2001_acta_polytechnica_impeller_power_input.pdf`
with its `.txt` sidecar. Its small rig, its Table 1 and Table 3:

| ratio | Beshay small rig | R4 | match |
|---|---|---|---|
| T | 0.300 m | 0.300 m | ✔ |
| H/T | 1.0 | 1.0 | ✔ |
| baffles | 4 at b = 0.1 T | 4 at T/10 | ✔ |
| D | 100 mm | 100 mm | ✔ |
| D/T | 1/3 | 1/3 | ✔ |
| l/D | 0.25 | 0.25 | ✔ |
| w/D | 0.2 | 0.2 | ✔ |
| D₁/D (disc) | 0.75 | 0.75 | ✔ |
| blades | 6 | 6 | ✔ |
| **t/D** | **0.0155** | **0.0155** | **✔ — this rung's whole change** |
| Re | 3×10⁴ – 6×10⁴ | 5.0×10⁴ | ✔ inside |
| fluid | water, 20 °C | water, ν = 1.0e-6, ρ = 998 | ✔ |

**MEASURED REFERENCE: `Po = 5.41`** (h/T = 0.33; 5.44 at h/T = 0.5).

**PRE-REGISTERED BAND — the gate:**

    GATE BAND:  Np ∈ [5.29, 5.53]        ( 5.41 ± 2.3 % )
    OUTER ENVELOPE (reported, not gated): Np ∈ [4.54, 6.28]   ( 5.41 ± 16 % )

The paper states its scatter as an **average relative standard deviation in the
range 2.3 % to 16 %** across its impellers and speeds, and **does not give a
per-impeller figure for the SRTI**. Which end applies to the `Po = 5.41` row is
therefore **unknown**. The **tight** reading is registered as the gate because it
is the demanding one; the wide one is printed beside every result so a reader can
see the envelope. **Choosing the tight end is a decision of this registration, made
before the run, and it is the harder of the two for us.**

**🔴 SANAA'S SENTENCE, REGISTERED BEFORE THE RUN SO THE OUTCOME CANNOT BE
NARRATED AFTERWARDS:**

> **At `t/D = 0.0155` our geometry is Beshay's geometry in every ratio. If the run
> does not land on 5.41 within Beshay's scatter, THAT IS THE PROBLEM TO REPORT AND
> FIX — not to explain away.** "Different tank" is no longer available as an
> explanation, and neither is any variant of it.

### 4.2 THE LANE'S PREDICTION, FROZEN EARLIER AND UNCHANGED

Registered on 2026-09-12 **before** this document and **before** any compute, in
`…REID2025.md` §11.4 and `…/R3/MRF_R3_ZONE_SENSITIVITY_DRAFT.md` §5:

    PREDICTION:  Np ∈ [5.2, 5.4]

derived as `5.41 × 0.8312` (the Bujalski thickness factor) **from the other
direction** — i.e. it already carries the expected steady-MRF under-prediction.
**It is not amended, not widened and not deleted**, because it is the falsifiable
thing and its value is that it was written first.

**THE TWO RECORDS DO NOT COINCIDE, AND THAT IS REGISTERED TOO.** The prediction
`[5.2, 5.4]` sits **slightly BELOW** the gate band `[5.29, 5.53]`; they overlap
only on `[5.29, 5.40]`. Three outcomes, all named in advance:

| where `Np` lands | gate | prediction | what it means |
|---|---|---|---|
| **[5.29, 5.40]** | **GATE REACHED** | satisfied | both records satisfied; thickness is the mechanism |
| **[5.20, 5.29)** | **GATE FAIL** | satisfied | **both records satisfied and THE GAP IS THE FINDING** — a steady-MRF deficit of a few per cent on geometry that is no longer an excuse. Reported and investigated per §4.1, never explained away |
| (5.40, 5.53] | **GATE REACHED** | **refuted** | the correlation over-corrected; the prediction is wrong and is recorded as wrong |
| outside [4.54, 6.28] | **GATE FAIL** | refuted | the mechanism is refuted and §11 of the reference registration falls |

### 4.3 REID 2025 REMAINS THE CFD COMPARATOR, UNCONDITIONALLY

Sanaa's standing instruction is unchanged: **every plot and quantity Reid et al.
report is reproduced for our case.** The full set already exists at
`verification/runs/navier_class/MRF/R2/PAPER_PARITY/` (index `PARITY_INDEX.md`,
twelve figures) and **is regenerated for R4 from R4's own fields** — velocity
profiles at `r/D` = 0.538 / 0.645 / 0.753, TKE against the exactly-digitised
Wu & Patterson points, agitation index, turbulence intensity under both
normalisations, `y+` per surface, the MRF zone geometry. Reid is a **comparator**;
Beshay is the **primary** reference.

### 4.4 THE RESULT ALREADY ON RECORD, WITH ITS CAVEATS, WHICH ARE NOT OPTIONAL

R2's `Np = 4.382` against the thickness-corrected Beshay value `4.497` is
**−2.6 %**. Every caveat travels with that number, in these words:

- **Bujalski et al. (1987) is NOT on this box.** The correlation
  `Po = 2.512 (t/D)^-0.195 (T/T0)^0.063` is a **secondary-source reproduction**
  (Beshay eq. 5) and **the source we hold does not state its range of validity in
  `t/D`**, so our `0.0400` is an **extrapolation of unknown reach**.
- **2.6 % sits inside the correlation's own 2–3 % accuracy and inside the
  experiment's 2.3–16 % scatter. It is AGREEMENT, NOT PRECISION**, and must not be
  quoted as a validation.
- **NO VERDICT MOVES.** `4.382` remains part of a row graded **`NOT A RESULT`**,
  and **a number that is not a result cannot be vindicated by a correlation.** If
  R4 lands in band, that is evidence about the **mechanism**, not a rehabilitation
  of the R2 row.

### 4.5 TWO DIFFERENCES THAT STAY ON THE RECORD RATHER THAN BEING QUIETLY DROPPED

1. **Reid's narrow `D/10` baffles.** The correlation has no baffle term and the
   difference falls out of the Beshay comparison because Beshay's baffles are
   `T/10` like ours. It is **untested** and stays named.
2. **A clearance DEFINITION difference, found by this lane and not corrected
   for.** Beshay measures `h` *"from the bottom of the vessel to the lower edge of
   the impeller"*; our `C = 0.100 m` is the **disc mid-plane**. Our `h` on their
   definition is `0.100 − W/2 = 0.090 m`, i.e. **`h/T = 0.300`, not 0.333.** Their
   own two rows (5.41 at 0.33, 5.44 at 0.50) give a linear read-across to
   `h/T = 0.30` of **5.405, i.e. −0.1 %** — far inside their scatter, and the paper
   itself reports only a 3 % change in SRTI `Po` over `C/T` 0.33 → 0.5. **The band
   is therefore NOT adjusted for it.** It is recorded because an unrecorded
   definitional mismatch is exactly the kind of thing that gets waved through.

---

## 5. ITERATIVE CONVERGENCE — A CRITERION LENGTHENING THE RUN CANNOT SATISFY

R2's `fine` was graded `NOT_CONVERGED` by a tell whose **window is a fraction of
`n_iters`** (`q = max(n//4,1)`, `cascade = late > early`), so the verdict flipped
from `NOT_CONVERGED` to `CONVERGED` at `n = 9000` **on the same events, without the
solution improving by one cell** (`MRF_R2_PREREGISTRATION.md` §A1.14). A
self-relaxing window is unfit as a stopping rule. R4 registers the replacement.

### 5.1 THE RULE THE CRITERION MUST OBEY — sharpened, and the sharpening is disclosed

The instruction this lane was given is *"write the criterion so that 'would this
have said CONVERGED at a longer n on the same events?' answers no."* **Read
literally that forbids every legitimate convergence criterion too**, since a
solver that genuinely settles must eventually be allowed to pass. The rule is
therefore sharpened, and the sharpening is the lane's, stated so the supervisor can
reject it at check 4:

> **No limb may use a window or a threshold whose SIZE or POSITION is a function
> of `n_iters`.** A limb may be passed only by the SOLUTION changing, never by the
> bookkeeping re-classifying events it has already seen. Where a limb can be made
> **monotone** — once failed, failed for every longer run on the same events — it
> is made monotone.

### 5.2 THE LIMBS

**IC-1 — bounding quiescence, ABSOLUTE and MONOTONE.** With `N_warmup = 2000`
iterations, **a pre-registered absolute iteration number, never a fraction**:

    count of bounding / limiting events at iterations i > 2000  ==  0

The window is `(2000, n]`: its left edge is **pinned** and its right edge only
grows, so **extending the run can only ADD events, never remove one.** Once
failed, failed forever. Applied to R2's own event list
`[1, 2, 74, 4356, 4848, 6335, 6340, 6641, 6642, 7817]` it returns **FAIL at every
`n`** — including 9000, 10000 and 12000, where the R2 tell returned `CONVERGED`.
**That is the defect closed, demonstrated on the data that exposed it.**

**IC-2 — no NaN and no floating-point exception, anywhere in the log.** Already
absolute and already monotone.

**IC-3 — residual floor at the final state, FIXED thresholds.** Final-iteration
initial residuals: `Ux, Uy, Uz, k, omega ≤ 1e-5`, and **cumulative continuity
error ≤ 1e-6**. **`p`'s raw initial residual is NOT gated**: this is a closed
domain with a floating pressure reference, where the normalised `p` initial
residual can plateau at O(0.1–0.4) on a fully converged field
(`docs/NUMERICS_KNOWLEDGE.md` N-X4). Passing IC-3 requires the field to change,
not the window to move.

**IC-4 — stationarity of the graded quantity over a FIXED-LENGTH window.** Over
the last **2000** iterations — an absolute count, not `n/4`:
`max|Np_i − mean| / mean ≤ 0.5 %` **and** `|linear drift over the window| / mean
≤ 0.2 %`. Absolute length; a longer run evaluates a later window and can pass only
if `Np` has actually flattened there.

**A level is iteratively converged only if IC-1 ∧ IC-2 ∧ IC-3 ∧ IC-4.** Any limb
failing ⇒ **`NOT A RESULT`**, reported at the core-minutes spent. **`endTime` is
NOT extended to chase a limb**, and a restart is not a re-run: if `endTime` is ever
judged insufficient, the run is repeated **from `0`** under a **new** registration,
as `MRF_R2_PREREGISTRATION.md` §9 already forecloses.

---

## 6. CONTROLLED DECOMPOSITION — THE UNCONTROLLED VARIABLE R2 CARRIED

**Measured from R2's own run records** (`RANKS.txt`, `decomposeParDict`):

| level | ranks | method | wall s | core-min |
|---|---|---|---|---|
| coarse | **2** | scotch | 8,753 | 291.77 |
| medium | **2** | scotch | 21,657 | 721.90 |
| fine | **6** | scotch | 41,103 | 4,110.30 |

**Three levels, two different rank counts, across exactly the levels being
compared.** Parallel reduction order is not associative, so rank count is a real
input to the last digits of an integral torque, and R2 varied it inside its own
grid triple. R4 removes the variable by construction:

- **`numberOfSubdomains 6`, fixed, registered, and the ONLY rank count this rung
  may run at.** A run at any other rank count is **not this registration's run**.
- `method scotch`, and the decomposition is **recorded** — `log.decomposePar` kept,
  and the per-processor cell counts read back into the run record.
- Core guard (Sanaa item 8): **6 solver ranks + fleet ≤ 16.** The runner schedules
  it in a wave; it is never oversubscribed.
- With a single grid there is no cross-level comparison left to contaminate, so
  this clause is belt and braces — **and it is registered anyway, because the R2
  defect was invisible until someone read `RANKS.txt`.**

---

## 7. MESH — THE THIN-FEATURE RISK, MEASURED BEFORE IT IS REGISTERED

A 1.55 mm blade is **2.58× thinner** than the 4.00 mm blade R2 meshed. Cells across
the blade at the R2 impeller refinement `level (2 3)`:

| level | base (mm) | cell at lvl 3 (mm) | across 4.00 mm | **across 1.55 mm** |
|---|---|---|---|---|
| coarse | 10.000 | 1.2500 | 3.20 | **1.24** |
| medium | 6.275 | 0.7843 | 5.10 | **1.98** |
| **fine** | **3.902** | **0.4878** | **8.20** | **3.18** |

**At `level (2 3)` the graded fine level would resolve the new blade with 3.18
cells — the resolution R2's COARSE level gave its own blade, and R2's coarse-to-fine
spread was 4.5 %, against a gate band of ±2.3 %.** That is not good enough for a
measurement that must land within a few per cent.

**REGISTERED: the impeller surface refinement is raised one level, to `(2 4)`,**
giving **0.2439 mm cells and 6.36 cells across the blade** at the graded level.
Every other refinement entry, `nCellsBetweenLevels`, and the base cell size are
unchanged from R2 fine.

- **Graded level: the R2 `fine` base cell, 3.902 mm (82³ background), impeller at
  `(2 4)`.**
- **This is a mesh change relative to R2 and is disclosed as one.** The R2-vs-R4
  `Np` comparison is therefore **across two mesh families**, and thickness is
  confounded with resolution to the extent that resolution still matters at 6.36
  and 8.20 cells across the blade respectively. **Both are well resolved; the
  confound is named, not hidden.**
- **`MESH_STANDARD` §8.1 — BUILD BEFORE FREEZE. This document may not be frozen
  until the graded level is built and shown admissible** against `MESH_STANDARD`
  §3: max non-orthogonality ≤ 70°, max skewness ≤ 4. A §6 birth certificate is
  written with `points_sha256`, cell count, max non-orthogonality, max skewness,
  `max_aspect_ratio` and whole-mesh `cell_volume_ratio`, **read back from the built
  mesh**, never from the requested values (§9.2).
- **Named risk, reported as a result if it happens:** `snappyHexMesh` fails to
  capture the 1.55 mm feature, or captures it with unacceptable skewness. That is
  a **`BLOCKED`** at the core-minutes spent and a mesh finding — **not an
  invitation to hand-write `polyMesh` or to quietly thicken the blade**
  (`MESH_STANDARD` §8.2).

---

## 8. COMPLETION RULE (rule 4) — the incompressible field set

A run is **done** only if all hold, exactly as `MRF_R2_PREREGISTRATION.md` §5
registers them: `rc == 0` from an rc sidecar captured **inside** the detached
wrapper; an `End` line; `ExecutionTime` count == `round(endTime/deltaT)` (`deltaT`
= 1, so == `endTime`); last written time == `endTime`; fields **`U p phi k omega
nut`** present at `endTime` (the isothermal-incompressible analogue of the rule-4
canonical list, disclosed there and unchanged here); and **every field at
`endTime` NEWER than the case's own `0/`** — the age guard. The launcher refuses a
case where `0` or a time directory already exists.

**Checkpoints (Sanaa items 1–5):** fields written every **1000** iterations, last
two kept, older purged. At R2 fine's measured rate (41,103 s for 8,000 iterations
at 6 ranks ⇒ ≈ 5.14 s/iteration) 1000 iterations is **≈ 86 minutes**, which
**exceeds her 30-minute loss ceiling**; the writeInterval is therefore set to
**300 iterations ≈ 26 minutes** at the measured rate, and is **re-checked against
the actual rate after the first 300 iterations** and tightened if the rate is
slower. `endTime = 8000`, matching R2's so the two rows are compared at equal
iteration count.

---

## 9. COMPUTE (rule 12) — costed, from R2's ACTUALS

Unit: core-minutes = wall s × ranks ÷ 60. The box cannot read its own billing, so
every dollar figure is **derived, reported-by-owner, not measured**.

| item | basis | est. core-min |
|---|---|---|
| geometry + `blockMesh` + `snappyHexMesh`, graded level | R2 fine build, scaled for the `(2 4)` impeller shell | ~250 |
| `checkMesh` + birth certificate | — | ~15 |
| `potentialFoam` init + smoke | R2 precedent | ~40 |
| `simpleFoam`, 8000 iterations, 6 ranks | R2 fine **4,110.3 core-min measured** at 2.42 M cells, scaled **×1.9** for the estimated 4.6 M cells at `(2 4)` | ~7,800 |
| post-processing, Reid parity set | measured tonight, < 25 core-min | ~25 |
| **total estimate** | | **~8,130 core-min** |

**Registered cap: 3× the estimate = 24,400 core-minutes** (≈ 407 core-h; derived
≈ **$20.86** at $0.0513/core-h — derived, not measured; **under the $25
pre-authorised ceiling**).

**How the cap behaves, and it matters.** Sanaa's directive #17 of 2026-09-12
(**NO CAP** — no run stopped by time or budget) and her item 7 (*"cap → NOT A
RESULT, never raised"*) are read together as the chief reads them: **the cap is
REGISTERED; if it is crossed the row is graded `NOT A RESULT` and the cap is never
raised; the run is NOT killed by a wrapper.** No guard in this rung stops a solver
on time or spend.

**The cell-count estimate is the weak number here.** 4.6 M is a projection from a
refinement-level change, not a measurement. §7's build-before-freeze **measures it
before the freeze**, and if the built mesh differs materially the estimate is
corrected in the same pre-compute amendment — legal under rule 2 because no
compute has run, and it must **name the run directory that does not exist**.

**Estimate-vs-actual calibration (rule 12, Sanaa 2026-08-23)** is owed at rung
completion as a row in `docs/COST_CALIBRATION.md`.

---

## 10. WHAT THIS DOCUMENT IS NOT

- **Not frozen, not launched.** The freeze is the cfd-supervisor's check 4, and
  §7 bars it until the graded mesh is built and admissible.
- **Not a grid-convergence study.** Dropped by ruling (§2); `PASS` is not
  claimable (§2.1).
- **Not a rehabilitation of R2.** `4.382` stays inside a `NOT A RESULT` row (§4.4).
- **Not a zone study.** The zone is held identical on purpose; the sensitivity is
  R3's, still drafted and unlaunched.
- **Not a test of Reid's narrow baffles** (§4.5), and not a test of the Bujalski
  correlation's validity range, which the box still cannot see.
- **An open choice the supervisor may amend before the freeze, flagged rather than
  buried:** §7 registers the impeller at `(2 4)`. Holding it at `(2 3)` would cost
  roughly half and resolve the blade with 3.18 cells instead of 6.36. The lane
  registers `(2 4)` because the blade is the torque-producing surface and the gate
  band is ±2.3 %. **Pre-compute amendment is legal (rule 2) and this is the first
  place to look for one.**

---

*Drafted by a cfd `lab-lane`, 2026-09-12, freeze-ready. NOT FROZEN. NOT LAUNCHED.
Submissions parked. No agent's message is Sanaa's consent.*

---

# §11. FREEZE ATTESTATION — cfd-SUPERVISOR, CHECK 4, PERSONAL AND UNDELEGATED — 2026-09-12T20:18:24Z

Appended under rule 6. **`lines whose number changed above this section: 0`.** The §0 banner reading *"FREEZE-READY DRAFT. NOT FROZEN"* is **superseded by this section and left in place, legible**, because other records cite this document by line.

## §11.1 LITERAL PINS — VALUES, NEVER COMMANDS

```
FROZEN BY:          cfd-supervisor, PERSONALLY (check 4, undelegated)
DATE (UTC):         2026-09-12T20:18:24Z
REGISTRATION BLOB:  fa0069709d19511e601aeb20a9694d7c3b6353c3   (this document at the parent of the freeze commit)
FREEZE COMMIT:      the commit carrying THIS section, whose PARENT is ac9e70ace34e734cb6fe5cd43fb5bc99b8ef6639
MESH CERTIFICATE:   verification/runs/navier_class/MRF/R4/fine/MESH_BIRTH_CERTIFICATE.json
  sha256:           508a28a527347faafefaa38939286dbacaee9f4c166761dfd0a98623e43fe27d
```

## §11.2 §8.1 SATISFIED — THE GRADED MESH EXISTS AND I READ ITS GATES

Build rc=0, 1,337 s wall (22.3 core-min), **3,641,246 cells**, 21 % under the registered 4.6 M projection. `MESH_STANDARD` §3, read from `checkMesh` output rather than from dictionaries: **max non-orthogonality 49.622 ≤ 70** (average 6.096); **max skewness 3.041 ≤ 4**; aspect ratio 4.399. **ADMISSIBLE.**

🔴 **`checkMesh` reports "Failed 1 mesh checks" and it is NOT buried: 62,538 concave cells, 1.72 %.** Concave cells are **not** one of §3 gates. It is the **family signature, measured not assumed** — every R2 level failed the same single check and R2 was graded on those meshes: **coarse 2.72 %, medium 2.13 %, fine 1.10 %.** R4 sits inside the range the family already spans. **Disclosed here so no reader meets it first in a log.**

## §11.3 THE ONE REGISTERED CHANGE IS IN THE MESH — TWO INDEPENDENT READ-BACKS

1. **Blade thickness measured from the STL THIS BUILD WROTE** (max |y| on the theta=0 blade beyond the disc rim): **1.550 mm, t/D = 0.0155** — the registered value, read back from the artifact rather than from the request that produced it.
2. **A check nobody asked for, and the better of the two:** thinner solids displace less liquid, so mesh volume **must** rise. Geometry alone predicts **+1.082e-04 m3** against R2 fine; `checkMesh` measures **+1.071e-04 m3**. **Agreement to 1 %.** Two independent quantities, one of them a physical consequence rather than a restatement.

## §11.4 WHAT THIS AUTHORISES

The **single graded fine level** may be queued **through the runner only** (item 19 — a hand launch is not a case), at the registered rank count, checkpoints inside the ceiling. **It authorises no grid-convergence claim of any kind**: §2.1 fixes the available vocabulary before the run, and **`PASS` is not among them** — rule 1 reserves `PASS` for a CONVERGING triple inside a pre-registered band, and this rung has one grid by ruling. The band is **`Np` in [5.29, 5.53]**; the +/-16 % envelope is **reported, never gated**.

**The cost re-derivation from the BUILT mesh is accepted:** 7.735 s/it measured against 9.8 projected, total **6,275 core-min against the frozen 8,130 — 23 % below**, so the cap is untouched and needs no amendment. **Calibration point owed at completion and already in hand: the meshing term was estimated at 250 core-min and MEASURED at 22.3 — an 11x over-estimate, attributed to misprediction, not contention and not waste.**

*Signed by the cfd-supervisor, personally, 2026-09-12T20:18:24Z. Submissions parked. No agent message is Sanaa consent.*
