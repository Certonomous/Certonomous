# SUBOFF A1 — RESULTS RECORD — 2026-09-12

**Graded against `verification/campaign/SUBOFF_A1_PREREGISTRATION.md`, frozen at commit
`05ca555084a225273d898f07374cf2a28c26de6c`, document blob
`c1060c6c67148bbb8f91d51d7e8f4bc3517d897c`.** The file on disk at grading time was
verified to BE that blob by `git hash-object` against `git rev-parse HEAD:<path>`, not
assumed.

**Authority:** Sanaa, 2026-09-10, verbatim: *"3D SUBOFF. Papers read and mesh selected
accordingly. Also must run asap."* **Every ruling recorded below is the cfd-supervisor's
and is marked `[lab-attributed]`. Nothing here was put to Sanaa and nothing here is her
instruction.**

---

## 1. THE HEADLINE, AND IT IS NOT THE ONE ANYONE EXPECTED

> ## 🔴 THE REGISTERED SUBOFF A1 SOLVE PROGRAMME IS **`BLOCKED`**, AND THE BLOCKER IS A **MACHINE LIMIT**, NOT A MESH DEFECT.

`SOLVE_L1` and `SOLVE_L2` are both **`BLOCKED`**. **No solver has ever run on SUBOFF A1.**

**Why, in the order that matters.** §5.1 defines Gate M verbatim as *"`PASS` iff M-a, M-b,
M-c and M-d all hold at **L1, L2 and L3**"*, and carries a launch bar: *"Any limb failing
at any level ⇒ `GATE FAIL`, **and no solver is launched**."*

**L3 cannot be built on this machine.** Holding the delivered ratio 1.4079 puts it at
**25.45 M cells**, predicted peak **41.7 GiB** against **30 GiB** of RAM.

> **So Gate M is quantified over a three-level family whose third level does not exist and
> cannot be made to exist here. GATE M CANNOT REACH `PASS` UNDER ANY MESH REPAIR, HOWEVER
> CLEAN, AND UNDER ANY CONTENTION CONDITION, HOWEVER IDLE THE BOX.**

**The L1 determinant failure is real, measured, and stays on the record — and it is NOT
what stops the solves.** Letting one cell in 3,268,613 take the blame would misdescribe
the blocker to whoever reads this next: it would read as a mesh problem with a mesh fix,
and there is no mesh fix.

**The narrow reading was offered and REFUSED, `[lab-attributed]`.** This lane put two
readings of the launch bar to the cfd-supervisor at equal strength and did not adopt
either. The supervisor upheld the **literal** one, on a ground that outlives this case:
**a launch bar that yields whenever someone can argue its purpose is not engaged is a gate
that can never bar anything** — the "gate that cannot fail" defect, arriving this time in
the costume of a permission.

**What was refused along the way, and none of it was tried:** `minDeterminant` was not
moved in either direction; L1 was not dropped from the family to make the gate pass; no
level was renamed; and no new rung was invented that the failing gate happens not to
reach. **A rung invented to escape a gate is the gate not applying to itself.**

**The only thing that unblocks this programme is a larger instance, and that is Sanaa's
decision alone.** It goes to her desk through the chief with the arithmetic attached. No
agent at any level may take it.

---

## 2. THE VERDICTS, IN THE FIXED VOCABULARY

| item | verdict | the number it cites |
|---|---|---|
| **Gate M (family)** | **`GATE FAIL`** | not evaluable at L3; `GATE FAIL` at L1 on M-d |
| Gate M-d at **L1** | **`GATE FAIL`** | min cell determinant **8.6227045e-04** vs floor **1.0e-03** — **1 cell in 3,268,613** |
| Gate M-a/b/c at **L1** | `PASS` | nonOrtho 64.953 ≤ 70; skew 2.913 ≤ 4; `3 geometric (non-empty/wedge) directions`; TE base full-equivalent **min 8 / median 10** vs floor 8; layers 98.507 %; negative volumes **0** |
| **Gate M (all four limbs) at L2** | **`PASS`** | determinant **1.5198839e-03**; nonOrtho 64.906; skew 3.126; 3 geometric directions; layers 98.640 %; negative volumes **0** |
| **L3** | **`BLOCKED`** | 25.45 M cells ⇒ **41.7 GiB** predicted peak vs **30 GiB** RAM. **ESTIMATED**, two-point fit. |
| **`SOLVE_L1`** | **`BLOCKED`** | never started — barred by §5.1's launch bar, which cannot be cleared because L3 cannot be built |
| **`SOLVE_L2`** | **`BLOCKED`** | same |
| **Gate S-W (`y+`)** | **`BLOCKED`** | unarmed: no solve, therefore no `yPlus.dat`. §11.2 fixes the unarmed verdict at `BLOCKED`, never `PASS`. |
| **Gate S-CT / D2 (`CT`)** | **`NOT A RESULT`** | pre-committed before any compute; no CONVERGING triple exists (rule 5) |

**THE VOCABULARY SPLIT USED HERE, adopted as this family's standing usage
`[lab-attributed]`:** a level that **started** and was stopped short of `endTime` is
**`NOT A RESULT`**; a level **never started** because the box could not host it, or
because a gate barred it, is **`BLOCKED`** with the measured number beside it.
**Conflating them would let an infrastructure limit masquerade as a physics outcome.**

---

## 3. WHAT WAS MEASURED BEFORE ANY SOLVER COULD HAVE RUN — AND IT SETTLED TWO THINGS

### 3.1 THE `y+` ARITHMETIC, FROM `M`, `Re` AND HULL LENGTH ALONE

From `Re = 1.2e7`, `ν = 1e-6 m²/s`, `L = 4.3561001 m`: `U = 2.7547576 m/s`,
ITTC-1957 `Cf = 2.90719285e-03`, **`u_τ = 0.1050281 m/s`**. First-cell height **measured**
from each built level's own `log.snappyHexMesh` layer table (the `near-wall` column):

| level | hull `y₁` | sail `y₁` | **hull `y⁺`** | sail `y⁺` | hull `y⁺` local max (est.) |
|---|---|---|---|---|---|
| **L1** | 953.0 µm | 183.0 µm | **50.0** | 9.6 | **87** |
| **L2** | 532.0 µm | 102.0 µm | **27.9** | 5.4 | **48** |

> **`y⁺` FORBIDS NOTHING HERE.** Every level sits inside `nutUSpaldingWallFunction`'s
> valid range and every estimated local maximum is below Gate W's ceiling of 300. This is
> **the opposite of M6**, whose same pre-compute arithmetic returned `y⁺ ≈ 9,447` — 31× the
> top of the wall-function range — and forbade every aerodynamic claim in advance.
> **SUBOFF A1's wall treatment was sound and the solve was barred for an unrelated reason.**

### 3.2 🔴 A REGISTERED PREDICTION OF THIS DOCUMENT WAS FALSIFIED **BEFORE** ANY COMPUTE

§11.7's **P5** registers measured hull `y⁺` within **±50 %** of §11.5's 30 / 20 / 13.3,
i.e. **L1 ∈ [15, 45]**. The built layer stack gives **50.0**.

> **P5 IS FALSIFIED AT L1.** Reported as falsified, per §11.7's own requirement that *"a
> falsified prediction is written up as falsified, not quietly dropped."*
> **P5 WAS NOT TOUCHED, WIDENED OR RESTATED** — amending a registered prediction to match
> arithmetic obtained afterwards is fitting, whether or not compute has run.

**The mechanism, which is the transferable part.** §11.5 derived `y₁ = 286 µm` for the
family **as sized in §4** (0.95 M / 3.21 M / 10.83 M). The built family is different and
its layers are `relativeSizes true`, so `y₁ = 0.5 × (hull surface cell) / 1.2^(nLayers−1)`.
That formula reproduces the **measured** `y₁` to **96.4 %** at L1 and **96.8 %** at L2.
**§11.5's number was never wrong arithmetic — it was ARITHMETIC ABOUT A MESH THAT WAS NOT
BUILT.**

### 3.3 🔴 A FINDING THAT OUTRUNS THIS CASE: THE BOUNDARY LAYER AND THE BULK REFINE AT DIFFERENT RATES

| quantity | L1 → L2 |
|---|---|
| delivered cell-count ratio `(N₂/N₁)^(1/3)` | **1.4079** |
| near-wall first-cell ratio `y₁,coarse / y₁,fine` | **1.7914** |

`nSurfaceLayers` runs **5-6-7-8** down this family, so each level gains a layer **on top
of** the 1.5 surface-cell refinement: `1.5 × 1.2 = 1.80` at the wall against 1.4079 in the
bulk.

> **A FAMILY WHOSE BOUNDARY LAYER REFINES AT 1.80 WHILE ITS BULK REFINES AT 1.41 IS NOT
> GEOMETRICALLY SIMILAR, AND ROACHE'S OBSERVED ORDER ASSUMES IT IS.**

**This is not a SUBOFF fact.** It applies to **every family in this lab that varies
`nSurfaceLayers` by level**, which is the normal way they are built. It is registered as a
named weakness, **no threshold is moved because of it**, and it has been routed to the
chief for independent verification. It is **not** ruled on here.

---

## 4. `L0c` — THE LEVEL BUILT TONIGHT, AND WHAT IT SETTLED

Built 2026-09-12T01:04:27Z → 01:27:17Z, rc = 0, **1370 s × 4 ranks = 91.33 core-min**.
`free -g` read **immediately before launch**: available **17 GiB**, ceiling
`available − 4 = 13 GiB`, predicted peak 3.19 GiB ⇒ proceeded clear by ~4×.
Full grading at `SUBOFF_A1_PREREGISTRATION.md` §14.2–§14.7.

| # | prediction | verdict |
|---|---|---|
| **P9** | cells ∈ [1.05 M, 1.30 M] | **HOLDS** — 1,206,389; delivered ratio **1.394094** against L1→L2's own **1.407873**, within **1.0 %**, and **produced by the family's own generating rule without being tuned to it** |
| **P10** | TE-base count below the floor of 8 | **CONFIRMED** — predicted 5.69, **measured 6** ⇒ **`GATE FAIL` on `L0c`'s M-b-1 limb**, the failure registered in advance. Floor not moved, limb not dropped. |
| **P11** | `L0c` clears M-d | **HOLDS — §4.1** |
| **P12** | peak ∈ [2.2, 4.6] GiB | **HOLDS** — measured **3.8928 GiB** against **3.2734** predicted, ratio **1.1892** — §4.2 |
| **P13** | hull axial faces ≥ 400 | **🔴 NOT GRADED — a defect in the registration itself.** No instrument in the frozen grading path emits a hull-generator face count. **A prediction was registered whose falsifier nothing could fire** — §4.3 of this table's companion status document names that exact defect, and it recurred one section after the repair for it was written. Building an instrument now would fix the grading path **after** the compute (rule 2), so it stays **NOT GRADED**. |

### 4.1 🟢 **L1 IS AN ISLAND, NOT A FLOOR** — 1.21 M CLEAN, 3.27 M DEGENERATE, 9.12 M CLEAN

| level | cells | min cell determinant | floor `1.0e-03` |
|---|---:|---|---|
| `L0c` | 1,206,389 | **3.4590623e-03** | **CLEAR by 3.5×** |
| L1 | 3,268,613 | **8.6227045e-04** | **FAILS by 13.8 %** |
| L2 | 9,121,237 | **1.5198839e-03** | CLEAR |

**The degeneracy is not monotone in resolution.** A1 §12.8 established, correctly, that
~3.27 M **reproducibly** fails — invariant to partitioning and to alignment. **It never
established that everything at or below 3.27 M fails, and that is what anyone would have
assumed from it.** **Measured false.** It also sharpens what the L1 failure *is*: not *"coarse
meshes degenerate"* but **something specific to that one build**, consistent with the
instrument disagreement at §4.2 of the status table where `snappyHexMesh` reports
*"faces on cells with determinant < 0.001 : 0"* on the very mesh `checkMesh` flags with one.

### 4.2 THE MEMORY CURVE HAS A THIRD POINT, AND THE LAB'S L3 FIGURE BECOMES A RANGE

> **🔴 THE 41.7 GiB FIGURE IS RETIRED FROM QUOTATION. THE LAB'S STATEMENT FOR L3 IS
> 37–49 GiB** — three-point fit **37.13**, two-point fit **41.72**, pure linear scaling from
> L2 as a pessimistic bound **49.43**. **Every member of that range exceeds 30 GiB**, so the
> `BLOCKED` ruling is untouched, and **a range that still clears the decision threshold is a
> STRONGER argument than a point estimate** — the conclusion survives our own uncertainty.

**The caveat travels with it.** `L0c` sits **below** both fitted points and constrains the
curve's **low** end; L3 is a **forward** extrapolation **2.8× beyond the highest measured
point**. **The two extrapolations run in opposite directions and must not be read as one
validation.** What the third point genuinely establishes: **the curve is smooth and monotone
across 1.21–9.12 Mcell, has no knee there, and the model form is not wrong in kind.**

---

## 5. WHAT RAN TONIGHT UNDER THE SUCCESSOR REGISTRATION

**A1 produced no solve and never will. `SUBOFF_A1b_PREREGISTRATION.md`, frozen at
`8efe38e8f5bcf7c82cf34e68344bd02b457419aa`, asks a smaller and satisfiable question of the
same two meshes** — see that document's §0 for what it refuses to claim.

| | state |
|---|---|
| **`SOLVE_L1`** | **RUNNING.** 4 ranks, relaunched 01:46:28Z (`free -g` available **11 GiB**). Residuals falling: `Ux` 1.0 → 4.8e-04, `p` 1.0 → 8.4e-05. Watcher armed at a **derived** 53 h ceiling that **escalates and never kills**. |
| **`SOLVE_L2`** | **`BLOCKED` ON MEMORY, AND IT IS A DIFFERENT KIND OF BLOCKED FROM L3's** — §6. A detached memory-gated launcher is armed and will start it unattended when the box frees. |
| first `SOLVE_L1` launch | **crashed at iteration zero**, 4.80 core-min, on an **upstream OpenFOAM documentation defect** — §7. Case **moved, never cleared**. |

**🟢 THE COST DERIVATION WAS RIGHT TO 0.8 %.** §6 of A1b derived L1 at **31.4 s/iteration**
from the supervisor's 01:15Z MRF rate times an itemised ×1.55 mechanism correction.
**Measured over the run's first steady iterations: 31.67 s/iteration — ratio 1.008.** That
projects **26.4 h wall / 6,333 core-min** against the registered **26.2 h / 6,280**.
**An anchor taken from the same solver class on the same box on the same night, corrected by
named mechanism rather than by a blanket margin, predicted this run's cost to under one
percent.** That is the method working, and it is worth more than the number.

---

## 6. WHAT IS BLOCKED, AND WHAT WOULD UNBLOCK EACH — THE TWO ARE NOT THE SAME KIND

| | why | what unblocks it |
|---|---|---|
| **L3 (25.45 M cells)** | **UNCONDITIONAL.** 37–49 GiB against **30 GiB** of RAM. **However empty the box, it does not fit.** | **A larger instance. SANAA'S DECISION ALONE**, and the only thing that revives the A1 triple. |
| **`SOLVE_L2` (9.12 M cells)** | **CURRENT OCCUPANCY, NOT THE HARDWARE.** Measured **1.54–1.71 kB/cell** from L1's running ranks ⇒ **13.4–14.9 GiB**; the box holds 30 GiB and other teams held ~19 of it. | **PATIENCE.** It fits on this machine the moment the machine is less busy. The gated launcher fires at `available ≥ 19 GiB` — **derived from the UPPER end of the measured range (14.9 + 4), not its middle**, because *a memory prediction is not a best estimate, it is a bound, and the only error that hurts is the low one.* |

> **🔴 CONFLATING THESE TWO WOULD TURN A SCHEDULING PROBLEM INTO A HARDWARE ARGUMENT AND
> INFLATE THE INSTANCE ASK WITH A LEVEL THAT DOES NOT NEED IT.** An instance ask padded with
> a level that only needed patience discredits the level that genuinely needs the hardware.

---

## 7. AN UPSTREAM OPENFOAM DEFECT, SURFACED RATHER THAN WORKED AROUND

Sanaa, 2026-09-10: OpenFOAM issues are to be **surfaced**, not worked around. This one cost
a run.

**`SOLVE_L1`'s first launch aborted at ITERATION ZERO** — 72 s, 4.80 core-min — with
*"FOAM FATAL IO ERROR: Entry 'liftDir' not found"*. **The dictionary had been written from
the header's own documentation.**

`forceCoeffs.C:293` calls `setCoordinateSystem(dict, "liftDir", "dragDir")` — **both names
non-empty, always**. `forces.C:67-78`'s `CofR` branch evaluates
`e3Name.empty() ? vector(0,0,1) : dict.get<vector>(e3Name)`, so **the ternary always takes
the hard read and the implicit-default arm is UNREACHABLE from `forceCoeffs`.** Meanwhile
**`forceCoeffs.H:112-113`** documents *"implicit directions e1=(1 0 0) and e3=(0 0 1)"*
beside `CofR`, and **`forceCoeffs.H:213-218` is a DEFAULTS TABLE** giving those same values
for entries that have no default. **The header advertises defaults twice and the branch
implements neither. A defaults table is the last place a reader expects to be wrong.**

Repaired under `VERIFICATION_CHARTER` §2d.1 with all four conditions addressed — the
establishing instrument being **OpenFOAM's own dictionary reader, which grades nothing** —
and **nothing moved, because zero iterations had produced any value to move.**
**`dragDir (1 0 0)` IS the documented `e1` default, so `Cd` and therefore `CT` are
definitionally unchanged.** Full paragraph at
`verification/runs/navier_class/SUBOFF_A1/OPENFOAM_forceCoeffs_DOC_DEFECT.txt`.
**NOT FILED, NOT DRAFTED AS A REPORT: submissions are parked and sending is Sanaa's alone.**

---

## 8. TWO INSTRUMENT DEFECTS OF MY OWN, AND THE PATTERN THEY SHARE

1. **The memory sampler selected ranks BY PROCESS NAME** and summed another team's
   `snappyHexMesh` into this level's total. **It would have read as a P12 near-miss that was
   entirely my instrument's fault.** Caught by an `n_ranks` column reading **5** where the
   case has **4**. Fixed by selecting on `/proc/<pid>/cwd`: **scope the measurement the way
   the JOB is scoped, not the way the process table is.**
2. **The `controlDict` followed a Usage block describing a branch the code cannot reach.**

> **BOTH ARE THE SAME MISTAKE: I TRUSTED A DESCRIPTION OF BEHAVIOUR INSTEAD OF THE
> BEHAVIOUR.** And **the planted controls caught neither, because both were CONFIGURATION
> rather than MEASUREMENT — a plant validates a reader, not the dictionary that decides
> whether the reader ever gets data.** **That is a real gap in this lab's discipline and no
> repair for it is offered here**, because none has been earned. The honest mitigation is
> what happened: **cheap failures that fail loudly and early.** A 72-second abort at
> iteration zero is the cheapest possible failure. **The class to fear is the configuration
> defect that runs to completion and grades.**

**One near-miss that was checked rather than reasoned about:** the smoke test's top-level
`endTime` directory was **empty** after `End`, which would have read as a `writeInterval`
defect costing 26 hours. **It was not** — the run was parallel and every field was in
`processor0/12/`, with `reconstructPar` simply not yet run. **Verified by listing the
directory, not by arithmetic on `writeInterval`.**

---

## 9. COST (rule 12)

| item | predicted | actual | ratio |
|---|---|---|---|
| `L0c` build | 27.62 core-min | **91.33** | **3.31×** |
| `SOLVE_L1` rate | 31.4 s/iteration | **31.67** | **1.008×** |
| `SOLVE_L1` projected | 6,280 core-min | 6,333 (projection) | 1.008 |
| crashed first launch | — | **4.80 core-min** | waste, separately named |
| mesh building to date | — | **534.13 core-min** | 77.07 + 228.53 + 67.07 + 70.13 + 91.33 |

**ATTRIBUTION, kept apart because averaging destroys both.** `L0c`'s 3.31× is **contention,
not misprediction**: the same estimator predicted that build's **peak memory to 18.9 %** and
its **near-wall first-cell height to 1.1 %**, and `SOLVE_L1`'s rate to **0.8 %**. The build
ran through a window where load went **64.69 → 76.41 on 16 cores** against the **~20–25**
that prevailed when L1's anchor was taken. **Contention gets its own line and is never
folded into the actual/predicted ratio.**

**Derived USD at the owner-stated $0.0513/core-h — DERIVED, NOT MEASURED**, because the box
cannot read its own billing: `L0c` **$0.078**; the crashed launch **$0.004**;
`SOLVE_L1` projected **$5.41**.

**Caps stop nothing.** Sanaa, ~2026-09-12T01:10Z: *"dont forget i dont want any cap on any
run"*. The registered figures are **calibration predictions to be scored**, never kills.
**The memory rule is untouched: she lifted caps, she did not add RAM.**
