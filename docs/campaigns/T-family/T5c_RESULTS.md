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
