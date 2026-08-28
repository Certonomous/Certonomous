# T5c — successor to T5b: the y+ ladder-tolerance gate moved off a POINT MAXIMUM onto an AREA-AVERAGED statistic, with the point maximum retained as a reported diagnostic beside the sublayer bound

> **STATUS: FROZEN BY COMMIT. NOT ENQUEUED.**
> This document is frozen by the commit that first lands it, per standing rule 2:
> the gate, threshold, cap and label are committed BEFORE any compute. **It is
> deliberately NOT enqueued** — dropping T5c into the run/re-grade queue is the
> heat-transfer supervisor's decision and is explicitly withheld from the lane
> that wrote this. Nothing here is sent anywhere (rule 7).
>
> **This document does not edit, amend or supersede `analyse_t5b.py`.** That file
> is frozen and post-compute; rule 2 bars a gate change after first compute and
> rule 6 bars editing a frozen file at all. The repair lives here, in a
> successor, or nowhere.
>
> **OPENING DISCLOSURE — WHAT WAS ALREADY KNOWN WHEN THIS GATE WAS WRITTEN, AND
> WHAT WAS NOT.** Diagnosing T5b's refusal required reading the y+ statistic on
> every level, so **the point MAXIMUM and the FACE-COUNT average are both already
> known** on all six registered walls (§2 tables them). Under the thresholds
> carried over below, the face-count average would clear every level with better
> than 2× margin, so **T5c does not claim to be blind to the SIGN of the outcome
> for an average-like statistic.** What it does claim, and what §4.3 proves by
> measurement rather than assertion, is that **the AREA-AVERAGED statistic this
> gate is actually written on is NOT the face-count average and its value is NOT
> known**: the registered walls carry face areas spanning **16.05:1** on
> `cube_front` and **8 883:1** on `floor`/`roof` at the fine level, so the two
> statistics are materially different numbers. **No threshold in this document
> was chosen; every one is carried over VERBATIM from `T5b_PREREGISTRATION.md`
> (§5). Only the STATISTIC changes.** That is the whole of T5c's rule-2 defence
> and it is stated here rather than buried.
>
> **THE BIRTH REQUIREMENT (Sanaa, 2026-08-28) BINDS EVERY CONTROL IN §6.**
> Verbatim: *"A control defined in terms of the thing it controls is not a
> control. A planted control must travel the real production path — written by
> the real producer's code, read through the real reader — and prove the
> instrument sees a non-zero the same way reality would deliver one. A control
> that empties the tuple it tests, or writes a schema the producer never emits,
> tests nothing and certifies blindness."* Companion rule: *"no instrument grades
> anything until that answer is yes, demonstrated."* **§6 discharges it and is
> binding: no row of T5c is graded until every arm in §6.2 has printed both its
> positive and its negative limb.**

Drafted and frozen 2026-08-28 by a heat-transfer `lab-lane`. Every number below
was re-derived by this lane from the raw artifacts named beside it, through the
frozen module's own readers, never from a summary handed down.

---

## 0. Why a successor exists

`T5b` graded **0 of 6** rows. All six returned **NOT A RESULT**, every one on the
same clause and the same patch:

> `y+ gate not MET on level(s) f: y+ exceeds 2.0x the level target 1.00 on: cube_front=2.310 -- the ladder is not the registered ladder`

recorded at `verification/runs/T-family/T5b_runs/T5B_GRADE_OUTPUT.txt`. Every
level completed cleanly (`STATUS.T5_CUBE_{c,m,f}`: `rc=0`, `capped=0`,
`note=clean`), the reference was in hand, and the refinement ratios were measured
from the real cell counts. **Nothing about the run failed. The gate fired on its
own statistic.**

## 1. The reader is NOT defective — the registered STATISTIC is. Verified two ways.

This distinction is the whole finding and this lane verified it independently
before relying on it.

`postProcessing/air/yPlus/0/yPlus.dat` carries the header

```
# Time            	patch             	min               	max               	average
```

so **the MAXIMUM IS THE MIDDLE COLUMN and a reader taking the trailing column
reads the average.** `analyse_t5b.py:360-361` takes
`max=float(parts[3]), mean=float(parts[4])` — **correct.** `gate_yplus` at
`analyse_t5b.py:382,389` then gates on `got[w]["max"]`, i.e. on the true point
maximum, exactly as registered. **There is no reader bug to repair.**

> **A TRAP THIS LANE RECORDS BECAUSE IT ALREADY CAUGHT SOMEONE IN THIS CAMPAIGN.**
> An earlier reading of these files published a table with `avg` and `MAX`
> swapped, and it was caught only by an independent cross-read. The columns are
> `min max average`; **the middle one is the maximum.** Any successor reader must
> assert the header line it parsed, not assume the order.

## 2. The mechanism, re-derived from the raw files

Source: `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/postProcessing/air/yPlus/0/yPlus.dat`, rows at `Time = 5000`.

**Refinement ratios.** `analyse_t5b.py:716-718` defines
`r21 = (cells_f/cells_m)^(1/3)` and `r32 = (cells_m/cells_c)^(1/3)` — Celik/Roache
subscripting, **1 = finest**. From the registered cell counts 52 684 / 212 942 /
882 024: **`r21 = 1.605978` is the MEDIUM→FINE ratio and `r32 = 1.592921` is the
COARSE→MEDIUM ratio.**

> **CORRECTION OF FACT, RECORDED AGAINST THE BRIEF THIS LANE WAS HANDED (docket
> D566).** The observed orders supplied to this lane were computed with `r21` and
> `r32` applied to the wrong steps. The corrected values are below. **No
> conclusion moves**, and the margin figures — which contain no ratio at all —
> are unchanged and exact.

`cube_front` at `Time = 5000`, and the observed order `p` of each statistic:

| statistic | c | m | f | p (c→m) | p (m→f) |
| --- | ---: | ---: | ---: | ---: | ---: |
| min | 0.354181 | 0.149288 | 0.066224 | 1.856 | 1.716 |
| **MAX** (the gated one) | **3.804350** | **2.960969** | **2.310042** | **0.538** | **0.524** |
| average (face-count) | 1.960511 | 1.275376 | 0.842657 | 0.924 | 0.875 |

The ladder's own design exponents, implied by the registered targets
`{c: 2.6, m: 1.6, f: 1.0}`, are **1.043 (c→m)** and **0.992 (m→f)**.

**The average very nearly meets the ladder's design assumption; the maximum does
not come close.** And `cube_front`'s MAX is not merely low — across the six
registered walls it is the outlier, while `roof`'s MAX is **non-monotone**:

| wall | MAX p (c→m) | MAX p (m→f) | average p (c→m) | average p (m→f) |
| --- | ---: | ---: | ---: | ---: |
| `cube_front` | 0.538 | 0.524 | 0.924 | 0.875 |
| `cube_rear` | 0.318 | 0.600 | 0.514 | 0.745 |
| `cube_top` | 0.518 | 0.852 | 0.383 | 1.272 |
| `cube_side_n` | 0.705 | 0.613 | 0.745 | 0.905 |
| `floor` | 0.787 | 0.838 | 0.862 | 0.928 |
| `roof` | **−0.074** | 1.366 | 1.353 | 1.103 |

**THE DECISIVE MEASUREMENT.** Margin against the registered bound
`YPLUS_TARGET[lv] × YPLUS_TARGET_TOL` — `{c: 2.6, m: 1.6, f: 1.0} × 2.0`. **These
carry no ratio and are exact.**

| statistic on `cube_front` | c (bound 5.2) | m (bound 3.2) | f (bound 2.0) | behaviour |
| --- | ---: | ---: | ---: | --- |
| **MAX** | 3.804350/5.2 = **0.7316** | 2.960969/3.2 = **0.9253** | 2.310042/2.0 = **1.1550** | **climbs monotonically and FIRES at f** |
| face-count average | 1.960511/5.2 = **0.3770** | 1.275376/3.2 = **0.3986** | 0.842657/2.0 = **0.4213** | **flat — clears every level with >2× margin** |

**THE GATE FIRES BECAUSE IT IS WRITTEN ON A POINT MAXIMUM OVER A FIELD THAT
CARRIES A LOCAL PEAK.** Refining the mesh resolves the peak better than it
reduces it, so the maximum falls more slowly than the bound tightens, and the
margin necessarily climbs whatever the mesh does. **The mesh is fine. The
statistic is the defect.**

**The sublayer bound was never breached.** `YPLUS_MAX = 5.0` at
`analyse_t5b.py:144`; the largest y+ anywhere on any registered wall at any level
is **3.804350** (`cube_front`, level c). The physics precondition the gate exists
to protect **held on every level.**

## 3. Why `cube_front` specifically — FLAGGED AS AN UNTESTED HYPOTHESIS, NOT A MEASUREMENT

The heat-transfer supervisor's explanation is that `cube_front` is the windward
face and carries a **stagnation peak**, where the boundary layer is thinnest and
`u_τ` largest, producing a sharp local y+ maximum that a point statistic latches
onto.

> **THIS IS A HYPOTHESIS. IT HAS NOT BEEN MEASURED AND T5c DOES NOT REST ON IT.**
> Nothing in §2 is evidence for a stagnation mechanism; §2 measures only that
> `cube_front`'s MAX is flat under refinement. **A successor must test it** — e.g.
> by locating the argmax face on `cube_front` and checking it sits at the
> stagnation line, and by checking whether the peak's y+ is set by `u_τ` or by the
> wall-normal spacing. **T5c registers no row that depends on the answer**, and
> the hypothesis is recorded here so it is not later mistaken for a finding.

## 4. The replacement statistic, its producer, and the identity proof

### 4.1 The artifact — the producer already writes it

The `yPlus` function object writes **both** `postProcessing/air/yPlus/0/yPlus.dat`
(the three summary columns) **and a full `volScalarField` `yPlus`** into each
written time directory. Verified present on disk on all three levels at
`T5_CUBE_{c,m,f}/5000/air/yPlus` (45 804 / 116 840 / 301 182 bytes), each carrying
the producer's own `FoamFile` header (`class volScalarField`, `location "5000/air"`,
`object yPlus`) and a `boundaryField` in which every registered wall appears as
`type calculated; value nonuniform List<scalar>`. **This is per-face y+ from the
real producer, and no new compute is needed to obtain it.**

Per-face areas come from `analyse_t5b.py:265-277 patch_areas`, which reads the
mesh's own `points`/`faces`/`boundary` — **an already-exercised production path**
in T5b, where it feeds the area-weighted `face_mean_T_C`.

### 4.2 IDENTITY PROOF — the new reader reads the same physical quantity as the old gate. MEASURED, not assumed.

A successor that gates on a different file must prove that file carries the same
quantity. This lane drove the frozen module's own `read_patch_field` over
`5000/air/yPlus` and the frozen `read_yplus_dat` over `yPlus.dat`, on **all three
levels × the walls `cube_front`, `floor`, `roof`**, and compared:

- **field `min` == `.dat` min, field `max` == `.dat` max, field unweighted mean ==
  `.dat` average — all nine wall×level pairs agreeing to better than 1e-9
  relative.**

**Two things follow, and both are load-bearing.** (i) The `yPlus` field is the
same data the frozen gate read, so T5c changes the STATISTIC and nothing else.
(ii) **`yPlus.dat`'s `average` column is proven to be the UNWEIGHTED, FACE-COUNT
arithmetic mean** — not an area average. That is measured here, not inferred from
OpenFOAM's source.

### 4.3 The area weighting is materially different from the face count — MEASURED

Per-face areas on the registered walls, from `patch_areas`:

| level | wall | nFaces | total area m² | min face m² | max face m² | **max/min** |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| f | `cube_front` | 648 | 1.125000e-04 | 1.5000e-08 | 2.4080e-07 | **16.05** |
| f | `floor` | 9 790 | 3.138750e-02 | 2.5000e-09 | 2.2209e-05 | **8 883.48** |
| f | `roof` | 10 384 | 3.150000e-02 | 2.5000e-09 | 2.2209e-05 | **8 883.48** |
| m | `cube_front` | 242 | 1.125000e-04 | 4.0000e-08 | 6.4286e-07 | 16.07 |
| c | `cube_front` | 98 | 1.125000e-04 | 9.6000e-08 | 1.6000e-06 | 16.67 |

**The patches are strongly non-uniform.** An area-weighted mean and a face-count
mean are therefore different numbers on every registered wall, which (i) makes
§6's weighting control **armable rather than vacuous**, and (ii) means the
**value of the gated statistic is genuinely not known at freeze**, notwithstanding
the opening disclosure about the face-count average.

### 4.4 The three readers T5c registers

| id | reader | role |
| --- | --- | --- |
| **R_area** | `Σ(y+_i · A_i) / Σ A_i` over the patch faces, from `5000/air/yPlus` boundaryField and `patch_areas` | **THE GATED STATISTIC** |
| **R_q95** | the **area-weighted 95th percentile**: sort faces by y+, accumulate area, report the y+ at 95 % of total patch area | **REPORTED diagnostic** |
| **R_max** | the point maximum over the patch | **GATED against the sublayer bound only; REPORTED against the ladder** |

## 5. The gate — every threshold carried over VERBATIM, none chosen

**No number in this section is new.** All are `analyse_t5b.py:142-146` unchanged.

| clause | statistic | threshold | verdict on breach | changed from T5b? |
| --- | --- | --- | --- | --- |
| **Y-SUBLAYER** | **R_max** | `R_max ≤ YPLUS_MAX = 5.0` on every registered wall, every level | **NOT A RESULT** | **NO — identical clause, identical statistic, identical threshold.** It is a *physics* precondition (viscous-sublayer resolution), not a ladder-consistency test, and dropping it would weaken the certificate. |
| **Y-LADDER** | **R_area** | `R_area ≤ YPLUS_TARGET[lv] × YPLUS_TARGET_TOL`, with `YPLUS_TARGET = {c: 2.6, m: 1.6, f: 1.0}` and `YPLUS_TARGET_TOL = 2.0` — **verbatim** | **NOT A RESULT** | **STATISTIC ONLY.** `R_max` → `R_area`. **The targets and the tolerance are byte-identical to T5b's.** |
| **Y-REPORT** | `R_max`, `R_q95`, the face-count average, and each one's margin against the same bound | — | **REPORTED, never gated** | new, and reported-only |
| registered walls | `cube_front, cube_top, cube_rear, cube_side_n, floor, roof` | both-directions cross-check against the mesh's own `boundary` | **NOT A RESULT** | **NO — verbatim.** |

**Everything else carries over unchanged from `T5b_PREREGISTRATION.md`:** the same
physical case and the same three meshes, the reference
`T5_runs/T5_reference_primary.json`, the six graded rows `G1a G2a G3a G5a G5b G5c`
and the seven REPORTED rows, the row bands, the L-342 field classes, the
completion rule, the measured refinement ratios, and the Roache ordering of rule 5.
**T5c re-grades; it does not re-design.**

**Why the sublayer clause stays on the maximum and the ladder clause does not.** A
sublayer bound is a statement about **the worst face on the wall** — one face
outside the viscous sublayer invalidates the wall treatment there, and an average
would hide it. A ladder-consistency clause is a statement about **how the
resolution of the wall as a whole scales with the mesh**, and a point maximum is
the wrong estimator for that because it is dominated by a single local feature.
**The two clauses want different statistics, and T5b gave them the same one.**

## 6. THE BIRTH REQUIREMENT, DISCHARGED ARM BY ARM — binding, and no row grades until it prints

### 6.1 The artifact, the producer and the reader — named and verified on disk

| element | identity | verified how |
| --- | --- | --- |
| **producer** | OpenFOAM `yPlus` function object (`system/controlDict:28-30`, `type yPlus;`) under `buoyantBoussinesqPimpleFoam` | the case's own `controlDict` and `STATUS.T5_CUBE_*` |
| **artifact** | `T5_CUBE_{c,m,f}/5000/air/yPlus`, a `volScalarField` whose `boundaryField` carries `type calculated; value nonuniform List<scalar>` for every registered wall | present on disk on all three levels; the producer's own `FoamFile` header read by this lane |
| **reader** | `read_patch_field` + `patch_areas` — **the identical call chain the graded rows travel** | both are already production paths in `analyse_t5b.py` |
| **write path** | plants are written into a **scratch copy** of the field file; the run tree is never written | the arm refuses if the scratch copy resolves inside the case tree |

**T5c's comparator MUST re-assert all four rows at grade time and refuse if any
fails**, and must assert that the file it plants into carries the producer's
`FoamFile` header with `object yPlus` — a control that plants into a file it wrote
itself is the exact failure the directive names.

### 6.2 The arms — each with a POSITIVE limb that must be SEEN and a NEGATIVE limb that must NOT FIRE

| arm | POSITIVE limb — must be SEEN | NEGATIVE limb — must NOT fire |
| --- | --- | --- |
| **Y-1 OFFSET (R_area sees a real signal)** | Add a constant `+1.234e-03` to **every** face value of `cube_front` in the scratch copy of the real field; **`R_area` must move by exactly `1.234e-03` to within 1e-9 relative** — the closed-form answer, since a weighted mean is affine. | **Two reads of identical bytes must differ by EXACTLY 0.0.** A reader that is noisy on unchanged bytes cannot be credited with any move. |
| **Y-2 SPIKE SPECIFICITY (R_area is NOT the old statistic)** | A **single-face** spike of `+9.876e+02` on the largest-area face of `cube_front` must move **`R_max` by ≥ 0.9 × 9.876e+02** — the max reader sees it. | **The same spike must move `R_area` by no more than `1.001 × 9.876e+02 × A_face/ΣA`** — i.e. the area average is shown NEARLY BLIND to a point peak, which is precisely the property §2 says the gate needed and did not have. |
| **Y-3 AREA WEIGHTING IS REAL (not a face count in disguise)** | Offset **only** the faces in the largest-area decile by `+1.234e-03`; **`R_area` must move by `1.234e-03 × (Σ_decile A / Σ A)` to within 1e-9 relative.** | **`R_area` must NOT move by the FACE-COUNT prediction `1.234e-03 × 0.10`.** The two predictions must additionally be shown to differ by **> 1 %**; if they do not, the arm **REFUSES** — a weighting control on a uniform patch is vacuous and must say so rather than pass. §4.3 measured 16.05:1 and 8 883:1 area spreads, so the arm is armable on this mesh, **but the comparator re-measures it and never assumes it.** |
| **Y-4 QUANTILE SENSITIVITY (R_q95 is a quantile)** | Offset the faces above the 95th area-percentile by `+1.234e-03`; **`R_q95` must move by ≈ `1.234e-03`.** | **The area-weighted MEDIAN must move by EXACTLY 0.0** under the same plant. A "quantile" that responds to a perturbation confined to the far tail of the distribution the way the median does is not a quantile. |
| **Y-5 SCHEMA / TUPLE INTEGRITY** | The comparator asserts, before any plant, that the parsed patch entry carries `nFaces` values matching the mesh's `boundary` `nFaces` for that patch. | **REFUSE if the count is zero, or if it disagrees with the mesh** — the directive's *"empties the tuple it tests"* failure, closed explicitly. |

**No arm may be reported PASS without both limbs printed.** An arm that prints one
limb is registered here as a **failed control**, not a passing one.

## 7. Registration under `VERIFICATION_CHARTER.md` §2d.1 — written for verification to rule, NOT ruled here

T5c re-grades artifacts that **already exist**, so a grading-path change is being
made after first compute. §2d.1 is **verification's clause**; this section states
the case in its own four conditions and stops.

| §2d.1 condition | T5c's claim | this lane's honest assessment |
| --- | --- | --- |
| **(1) DEMONSTRABLE ERROR, not a preference** | A point maximum cannot estimate how a wall's resolution scales with the mesh when the field carries a local peak. **Measured (§2):** the MAX margin climbs **0.7316 → 0.9253 → 1.1550** and fires, while the average margin is **flat at 0.3770 → 0.3986 → 0.4213**; the MAX's observed order is **0.52–0.54** against the ladder's design **0.99–1.04**, and on `roof` the MAX is **non-monotone (p = −0.074)** — a statistic that increases under refinement is not a convergence measure. | **Strong on the estimator question.** **Honestly weaker on one point:** a tighter gate is not automatically a wrong gate, and this lane cannot exclude that some reader would prefer to keep the maximum and loosen `YPLUS_TARGET_TOL`. **T5c deliberately does NOT do that** — loosening the tolerance would be *"the numbers looked wrong, so the band was widened"*, which §2d.1 names as the thing the exception does **not** permit. Every threshold is carried over byte-identical. |
| **(2) established by an instrument INDEPENDENT OF THE HYPOTHESIS** | The instruments are (i) the **observed-order calculation**, which grades nothing, and (ii) `roof`'s **non-monotonicity**, which is a pure sanity property with no verdict attached and no knowledge of which direction any row would move. Neither can have been selected to move a verdict, and (ii) in particular condemns the statistic on a wall that **was never the one that fired**. | **This lane rates (ii) the strongest limb** precisely because `roof` is not `cube_front`: the defect is visible on a wall whose verdict was never at issue. |
| **(3) discloses, names the instrument, QUANTIFIES what moved** | §1–§2 disclose and quantify; §4.2 proves the reader identity by measurement; §4.3 quantifies the weighting difference; the opening disclosure states exactly what was known at freeze; **docket D566** records this lane's correction of the `r21`/`r32` assignment in the brief it was handed. | **Met.** |
| **(4) pre-repair values recorded beside the published ones** | The pre-repair state is **a refusal, not a value**: all six rows read `NOT A RESULT` on the identical clause. **T5c must print, beside every row it publishes, `PRE-REPAIR STATE: NOT A RESULT (T5b y+ ladder clause on cube_front MAX = 2.310042 against bound 2.0)`**, and must print `R_max` and its margin on every wall and level regardless of verdict. | **Met.** |

**NOT RULED HERE.** No row of T5c may be graded until verification has ruled on
§2d.1. If verification rules against re-grading the existing artifacts, §8's
costed fresh run is the fallback and it is not a blocker.

## 8. Cost — rule 12

**No new solver compute is proposed.** The `yPlus` field, the meshes and the
completed runs are all on disk.

| item | figure | basis |
| --- | --- | --- |
| T5c re-grade | **< 1 core-min**, comparator time only | reads existing artifacts; no solver |
| fresh three-level ladder, if ruled necessary | **451.833 core-min** (c 16.783 + m 87.533 + f 347.517) | **MEASURED**, `STATUS.T5_CUBE_{c,m,f}`, all `rc=0`, `capped=0`, `note=clean` |
| in dollars | **$0.3863** | **DERIVED, NOT MEASURED** — `451.833 / 60 × $0.0513/core-h` at the rule-12 reported-by-owner rate; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| registered POINT / CAP | **419.2 / 838.4 core-min** | `T5b_PREREGISTRATION.md` §9, carried over |
| **calibration owed under rule 12** | **actual/predicted = 451.833 / 419.2 = 1.0778** | the ladder ran **7.8 % over POINT and 46 % under CAP**. **Attribution, stated and not absorbed:** the POINT was built from an earlier same-case measurement plus a declared 2 % allowance for the repaired function objects' extra field writes; the residual is contention on a saturated box. **No waste is claimed and none is hidden.** This row is owed to `docs/COST_CALIBRATION.md` and is **NOT** discharged by this document. |

Both figures sit far under the $25 pre-authorisation, so **cost cannot be a
reason to rule §7 either way.**

## 9. What this document does not do

- It **does not** edit, amend or supersede any frozen file, `analyse_t5b.py`
  included. T5b's six `NOT A RESULT` verdicts **stand as published**.
- It **does not** enqueue anything. It **is** frozen and committed — that is
  rule 2's requirement and the whole of this document's evidentiary content —
  but the drop is the supervisor's separate act and has not been taken.
- It **does not** grade anything. Every T5b row remains as T5b left it.
- It **does not** loosen `YPLUS_TARGET`, `YPLUS_TARGET_TOL` or `YPLUS_MAX`, and a
  successor that does so is doing a different and more dangerous thing.
- It **does not** claim the stagnation-peak explanation of §3. That is an untested
  hypothesis and is labelled as one.
