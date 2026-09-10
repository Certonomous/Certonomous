# T5c — RESULTS. The y+ ladder gate was moved off the point maximum, it stopped firing, and the rows underneath it still do not pass: **1 GATE FAIL, 5 NOT A RESULT, 0 of 6 PASS**

> **PHYSICS RESULT THIS CYCLE.** T5 had **zero graded rows in its entire history**;
> all six T5b rows returned `NOT A RESULT` on the y+ statistic, so no row ever reached
> its physics. T5c re-graded them. **The y+ clause now clears on every wall and every
> level, and the rows are refused on their GRID TRIPLES instead.** The repair did not
> manufacture a pass — it moved the failure to where the failure actually is.

**Verdicts, by the fixed vocabulary.** Full output at
`verification/runs/T-family/T5c_runs/T5C_GRADE_OUTPUT.txt`.

| row | wall | verdict | basis |
|---|---|---|---|
| `G1a` | `cube_front` | **`NOT A RESULT`** | grid triple **`OSCILLATORY`** (rule 5 step 2); fine value **76.9543** printed, not graded |
| `G2a` | `cube_top` | **`GATE FAIL`** | fine **39.4023** vs reference **55.224**, band **± 5.66404**, **GCI 4.3550 %** |
| `G3a` | `cube_rear` | **`NOT A RESULT`** | grid triple **`OSCILLATORY`**; fine value **65.8707** printed, not graded |
| `G5a` | `cube_front` | **`NOT A RESULT`** | grid triple **`DIVERGENT`**; fine value **55.9394** printed, not graded |
| `G5b` | `cube_top` | **`NOT A RESULT`** | grid triple **`DIVERGENT`**; fine value **59.45** printed, not graded |
| `G5c` | `cube_rear` | **`NOT A RESULT`** | grid triple **`DIVERGENT`**; fine value **55.6857** printed, not graded |

**TALLY: 0 of 6 graded rows PASS.** The seven REPORTED rows (`G1 G2 G3 G4 R1 R2 R3`) are
a **row class, not a verdict**, and are excluded from the census (D534, approved
2026-08-27).

Every row carries its pre-repair state beside it, as `T5c_PREREGISTRATION.md` §7
condition (4) requires: `PRE-REPAIR STATE: NOT A RESULT (T5b y+ ladder clause on
cube_front MAX = 2.310042 against bound 2.0)`.

---

## 1. What actually changed, and what did not

**The y+ ladder clause cleared at every level** — `y+ gate: MET` on `c`, `m` and `f`,
all six registered walls inside `R_max ≤ 5.0` (Y-SUBLAYER) and `R_area` within
`2.0 × the level target` (Y-LADDER, bounds 5.2000 / 3.2000 / 2.0000). Under T5b's
statistic the identical artifacts refused on `cube_front` MAX = 2.310042 against bound
2.0. **No threshold moved. Only the statistic did**, and the comparator asserts that
byte-identity at grade time rather than claiming it: **20 constant names re-parsed from
the frozen `analyse_t5b.py` and all identical**, `YPLUS_MAX = 5.0` and
`YPLUS_TARGET_TOL = 2.0` re-read as literals from the frozen predecessor.

**The sublayer bound was never in danger.** The largest y+ on any registered wall at any
level is **3.804350** (`cube_front`, level c) against `YPLUS_MAX = 5.0`. The physics
precondition the gate exists to protect **held on every level**, before and after.

## 2. THE MEASUREMENT THAT WAS NOT KNOWN AT FREEZE — R_area is monotone on all six walls

The registration measured non-monotonicity of the point maximum on `roof` (p = −0.074)
and used it as the ground for the repair. **It did not know how the replacement statistic
behaved on the other five walls.** The re-grade measures both statistics on all six:

| wall | `R_max` p (c→m) | `R_max` p (m→f) | `R_area` p (c→m) | `R_area` p (m→f) |
|---|---:|---:|---:|---:|
| `cube_front` | 0.538 | 0.524 | **0.928** | **0.891** |
| `cube_top` | 0.518 | 0.852 | 0.399 | 1.197 |
| `cube_rear` | 0.318 | 0.600 | 0.605 | 0.652 |
| `cube_side_n` | 0.705 | 0.613 | 0.701 | 0.894 |
| `floor` | 0.787 | 0.838 | 1.387 | 0.977 |
| `roof` | **−0.074 — NON-MONOTONE** | 1.366 | 1.279 | 1.158 |

> **`R_area` is MONOTONE DECREASING on all six walls, including `roof`, where `R_max` is
> not.** This is a new measurement, not a restatement of the registration. On
> `cube_front` the replacement statistic's observed order is **0.928 / 0.891** against the
> ladder's design **1.043 / 0.992**, while the point maximum manages **0.538 / 0.524**.
>
> **SCOPE, STATED SO IT IS NOT OVERSTATED: this is a result about THIS ladder, on THESE
> three meshes.** It confirms the 2026-09-03 G7/R1 classification **by measurement rather
> than by ruling** on the case that classification was made for. **It is NOT a general
> result about area-averaging**, and nothing here licenses the claim that an area average
> is the right ladder statistic on another geometry, another wall set or another
> refinement family. A statistic that behaves on six walls of one cube ladder has been
> tested on six walls of one cube ladder.

**The comparator reports this against its own interest.** It prints, in terms, that where
`R_area` were itself to appear non-monotone *"T5c's OWN replacement statistic carries the
defect item B condemned, and that is reported rather than hidden."* On these artifacts it
does not — but the instrument was built to say so if it had.

**Margins** (against `YPLUS_TARGET[lv] × 2.0`): `R_area` on `cube_front` is flat at
**0.3569 → 0.3764 → 0.3948**, while `R_max` climbs **0.7316 → 0.9253 → 1.1550** and fires
at the fine level. Refining the mesh resolves the local peak faster than it reduces it.

## 3. THE FINDING — the y+ statistic was masking a grid-convergence problem

With the y+ clause no longer refusing every row before rule 5 is reached, the triples
became visible for the first time, and **five of six are not `CONVERGING`**: `G1a` and
`G3a` are **`OSCILLATORY`**, `G5a`/`G5b`/`G5c` are **`DIVERGENT`**. Only `G2a` produced a
gradeable triple, and it **fails its band** — fine 39.4023 against a reference 55.224 with
a ±5.66404 band, a deviation far outside it, with **GCI 4.3550 %**.

> **This is a physics finding, reported not gated** (Sanaa's clause 7 taxonomy): the T5
> cube ladder does not deliver a converged heat-transfer coefficient on these three
> meshes. It is **not** a defect in the repair, and it opens a follow-up question rather
> than triggering a rule change. **The honest reading is that T5b's y+ clause was
> concealing this**: six rows refused on a statistic looked like one problem, and are
> in fact a different and deeper one.

**No GCI is quoted for any non-monotone row** — rule 5's prohibition holds; the fine
value is printed beside each and explicitly `not graded`.

## 4. Preconditions, all met before any row graded

- **Completion (rule 4):** `COMPLETE` on all three levels, including the age guard.
- **Mesh identity:** cells **52 684 / 212 942 / 882 024**, equal to the registered counts.
  Measured ratios **r21 = 1.605978** (medium→fine) and **r32 = 1.592921** (coarse→medium).
- **Birth requirement (§6, binding):** **all five arms Y-1…Y-5 printed both limbs and
  passed** before a single graded value was read. Y-3's vacuity refusal is **armed and
  fires** on a uniform patch, and is armable here at **747.4576 % separation**.
- **The planted-zero control does not carry the T3 defect.** Y-2's strengthening requires
  **the argmax to BE the planted face**, not merely that the maximum moved — the predicate
  `VERIFICATION_CHARTER` §2d.11.1 found missing in the T3 control. The selftest reproduces
  the T3 failure deliberately: a spike at face 0 **satisfies the aggregate predicate
  (True) and fails the at-the-planted-face predicate (False)**, so the strengthening is
  shown load-bearing rather than decorative.
- **Identity proof:** field min/max/unweighted-mean reproduce `yPlus.dat`'s
  min/max/average to better than **1e-09 relative** on all six walls at all three levels.
- **No control is a bare `assert`** (0 found), and the selftest asserts it is not running
  under `python3 -O`.

## 5. Cost — rule 12, and the calibration owed

| item | figure | basis |
|---|---|---|
| registered estimate | **< 1 core-min**, comparator only | `T5c_PREREGISTRATION.md` §8 |
| **actual** | **0.132 core-min** (7.92 s wall × 1 rank ÷ 60); selftest a further 0.03 s | **MEASURED**, this run |
| actual / predicted | **≈ 0.13** | came in **an order of magnitude under** the registered ceiling |
| in dollars | **$0.000113** | **DERIVED, NOT MEASURED** — at the rule-12 reported-by-owner rate $0.0513/core-h; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5) |
| solver compute | **NONE** | re-grade of existing artifacts |
| waste | **none claimed, none hidden** | — |

**The rule-12 calibration row is OWED to `docs/COST_CALIBRATION.md` and is NOT discharged
here.** This lane was directed to stay off that file; the row is stated above so whoever
lands it has the measured figures.

## 5a. ⚠ A DISCLOSED, UNREPAIRED PROPERTY OF THE GRADER — the freeze witness is a git blob SHA-1, not a sha256 of the disk bytes

**Found by this lane during the grading pass, reported rather than repaired, and ruled
FORWARD-ONLY by the heat-transfer supervisor on 2026-09-03.**

`analyse_t5c.py` records its registration's freeze witness as
`e73a16cf5ccf4135f2d1e0b478ce9f829b01be2a` — a **40-hex git blob SHA-1**. **L-450
records that the freeze instrument is blind to exactly that form**, and to truncated
16-hex, and that a witness must be a **full sha256 of the disk bytes** to be seen. There
are **zero occurrences of `sha256`** in the grader.

**Why it is not repaired, and the reasons are Sanaa's rather than this team's:**

1. **It changes no verdict.** What is degraded is the freeze **instrument's reporting**,
   not the freeze itself: the registration really was committed at `e0c5fee8` before any
   compute, and the grader really was committed at `c9865347` before it had ever run.
   A witness the instrument cannot read is still a witness.
2. **Sanaa's 2026-09-03 §2:** a rule requiring a backfill or re-registration must state
   its cost **and the result it protects**. **No result is protected** by re-witnessing a
   grader that already graded correctly.
3. **Her clause 7** puts coverage ratios **forward-only and unreported**.

**The grader is post-compute as of this record** — it has now run — so any repair would
need the `VERIFICATION_CHARTER` §2d.1 route, and that route is **not being taken**.
**FORWARD-ONLY ADOPTION:** every **new** grader this team writes carries a **full sha256
of the disk bytes** as its freeze witness. **No backfill is scheduled** across existing
T-family comparators.

*Separately assessed and dismissed on evidence:* the concern that the grader's tolerances
might repeat the T3 bare-absolute defect. They do not — `REL_EXACT = 1e-9` and
`REL_FACE = 1e-12` are **relative to the operands they difference**, so no threshold sits
below the arithmetic noise floor and no change is owed.

## 6. What this record does not do

- It does **not** disturb T5b. Its six `NOT A RESULT` verdicts **stand as published**; the
  frozen `analyse_t5b.py` was neither edited nor imported-and-patched.
- It does **not** claim the stagnation-peak explanation of `T5c_PREREGISTRATION.md` §3.
  That remains an **untested hypothesis** and no row here depends on it.
- It does **not** grade the seven REPORTED rows. They are a row class.
- It does **not** treat `G2a`'s `GATE FAIL` or the five `NOT A RESULT`s as a reason to
  revisit any threshold. Every threshold is carried over byte-identical, and widening one
  after seeing what it did is precisely what rule 2 forbids.

---

*Graded 2026-09-03 by `verification/runs/T-family/T5c_runs/analyse_t5c.py`
(sha256 `50b484f0541cea52baea12e1058204f35b7922b40f7e75adf60bb71e13749f0b`, frozen by
commit `c9865347` before it had ever been run), against the registration frozen by
`e0c5fee8`, under the authority of `VERIFICATION_CHARTER` §2d.11.2 (`ad9eda53`).
Comparator output is unedited at
`verification/runs/T-family/T5c_runs/T5C_GRADE_OUTPUT.txt`.*

---

## AMENDMENT 1 — 2026-09-10, heat-transfer supervisor. **`G2a`'s `GATE FAIL` IS WITHDRAWN AND RESTATED AS `NOT A RESULT`. THE `GCI 4.3550 %` IS WITHDRAWN AND MUST NOT BE QUOTED.**

*Appended at the foot. **Lines whose number changed above this section: 0** —
asserted mechanically against the HEAD blob, not claimed. The original rows are
**struck, never rewritten**: every figure above stands exactly as published, and
this amendment records what supersedes it.*

**CORRECTED TALLY: 0 PASS, 0 GATE FAIL, 6 `NOT A RESULT`.** The document's title
line and §1 tally ("**1 GATE FAIL, 5 NOT A RESULT**") are **superseded by this
amendment** and are left unrewritten so the change is visible.

### The reason, measured

Standing rule 5 orders the gate, **clause (1) first**: *"any level not
iteratively converged or not plateaued → `NOT A RESULT`"*, before any triple is
classified. `T5_PREREGISTRATION.md` §5.5 (lines 466–472) registers **T5's own
instrument for that clause**, frozen before any T5 case existed, and it is
deliberately **not** a residual — *"`residualControl` is not written (L-141: in
T1c a genuinely unconverged case sat at residual 4e-05, and in T3 the residual
was again not the instrument)"*. The registered criterion is:

> **CONVERGED** means the largest change of any cell value of `T` in either
> region, and separately of `U` in the fluid, between the checkpoints at
> `endTime − 1000` and `endTime`, is at most **1e-6 of that field's range**.

`analyse_t5c.py` copies `grade_row` **verbatim** from `analyse_t5b.py`, which
**dropped that registered step and reused its number** — `analyse_t5b.py:654`
carries the docstring *"THE REGISTERED ORDER (T5 S7.5, rule 5), evaluated top to
bottom"* while its step `(1)` at line 657 is the y+ gate, with the triple at
`(2)`. So clause (1) was never evaluated for T5c.

**Applying the registered criterion now**, to the same artifacts T5c graded
(`T5b_runs/T5_CUBE_{c,m,f}/{4000,5000}/air/T`), supervisor-computed 2026-09-10:

| level | cells | max &#124;ΔT&#124; over the last 1000 iterations | field range | registered tol | result |
|---|---:|---:|---:|---:|---|
| `c` | 52,684 | **0.316753 K** | 44.4630 K | 4.446298e-05 | **NOT CONVERGED — over by 7,124×** |
| `m` | 212,942 | **29.603596 K** | 48.6851 K | 4.868511e-05 | **NOT CONVERGED — over by 608,063×** |
| `f` | 882,024 | **26.448420 K** | 48.1021 K | 4.810208e-05 | **NOT CONVERGED — over by 549,839×** |

**All three levels fail, the coarse included.** The medium moves **29.6 K in a
single cell** across its final 1000 iterations, on a field whose entire range is
48.7 K. `G2a`'s value, its band comparison and its GCI were computed from a
triple of three unconverged solutions, so under rule 5 the row is
**`NOT A RESULT`**, its value **printed, not graded**, and **no GCI may be
quoted from it**. Rule 5 permits this direction and only this direction: *"The
gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the
reverse."* This amendment does not rehabilitate any row.

**Corroborating evidence, recorded because it explains the triples above.** The
`OSCILLATORY` and `DIVERGENT` triples on the other five rows are not independent
of this: they are the signature of the same non-convergence. From each case's own
named `log.solve` — `m`'s turbulence has collapsed (`k` initial residual
8.033e-09 at iteration 500 and 8.032e-09 at 5000; `omega` 3.355e-11 → 3.343e-11,
unchanged to three significant figures across 4,500 iterations; the final
`Time = 5000` block prints `bounding k, min: 0`), and `f`'s is in a limit cycle
(`omega` swinging 4.26e-12 → 4.95e-02 → 4.44e-04 → 3.33e-01 → 9.47e-04 across
iterations 2000–5000, eleven orders). A residual that does not move is a frozen
field, not a converged one.

### What this does NOT say

- It does **not** withdraw or amend T5b. `T5b_runs/T5B_GRADE_OUTPUT.txt` reads
  *"0 of 6 graded rows PASS"* with all six `NOT A RESULT` on the y+ gate, which
  fired **first** and short-circuited every row. **No published T5b verdict ever
  rested on a non-converged level.** T5b's verdicts stand as published.
- It does **not** find fault with T5c's own reasoning about the y+ statistic,
  which stands. T5c's defect is inherited, in a `grade_row` copied verbatim.
- It does **not** claim more iterations would fix this. The measured trajectories
  say otherwise, and that is a separate finding recorded on the board.
- It is **not** a capability claim about the lab or the case.

`T5c` is **HELD** and must not be re-run until clause (1) is enforced on its
grading path — see `T5c_PREREGISTRATION.md` AMENDMENT 1. **A successor must not
"repair" this withdrawal away**; it is discharged by grading a converged ladder,
never by re-reading this note as over-caution.

— heat-transfer supervisor, 2026-09-10, [lab-attributed]
