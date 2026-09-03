# T5c — THE GRADING PATH, REGISTERED AND FROZEN BY THE COMMIT THAT LANDS IT

> **STATUS: FROZEN BY THIS COMMIT. NOT ENQUEUED BY THIS LANE.**
> This document registers the **comparator** for `T5c_PREREGISTRATION.md`. It
> **creates no gate, moves no threshold, sets no band and changes no label** —
> every one of those was frozen at commit `e0c5fee8` and is carried here by
> reference and by an executable assertion, never restated in a way that could
> drift. **SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).
>
> **THE FREEZE IS TRUE BY CONSTRUCTION, NOT BY ASSERTION.** This document and
> `verification/runs/T-family/T5c_runs/analyse_t5c.py` land in **one commit**,
> and that commit is made **before any case directory named below exists** and
> **before the comparator has read a single gated value**. The pattern is the one
> `2b9bd20b` set: register the instrument in the same commit as the thing that
> depends on it, so no window exists in which the gate is known and the
> instrument is still editable.
>
> **`VERIFICATION_CHARTER.md` §2u BINDS THIS DOCUMENT AND IS THE REASON IT
> EXISTS AS A COMMITTED FILE.** Ruled at `ad9eda53`: *"A SHA WITNESS IS A CLAIM
> MADE BY THE REPOSITORY, NOT BY A FILE. A digest recorded in an artifact that is
> not committed witnesses nothing, however correct the digest is, because nothing
> fixes WHEN it was written."* The witness in §2 below is worthless until the
> commit carrying it exists; that is the whole point of landing it here rather
> than reporting it upward.

**Team:** heat-transfer. **Rung:** T5c. **Ladder:** T5.
**Gate document (frozen, NOT edited by this file):**
`docs/campaigns/T-family/T5c_PREREGISTRATION.md`, blob
`e73a16cf5ccf4135f2d1e0b478ce9f829b01be2a`, first landed by commit `e0c5fee8`.
**Grading path (frozen at this commit):**
`verification/runs/T-family/T5c_runs/analyse_t5c.py`.

---

## 0. WHY THIS RUNG CAN NOW RUN, AND ON WHOSE AUTHORITY

`T5c_PREREGISTRATION.md:287-289` registered its own stopping line:

> *"NOT RULED HERE. No row of T5c may be graded until verification has ruled on
> §2d.1."*

**That condition is DISCHARGED.** `VERIFICATION_CHARTER.md` v1.45 **§2d.11.2**,
commit `ad9eda53`, line `5242`, verbatim:

> *"T5c's own §7 stop line at `:287` is hereby discharged: 'No row of T5c may be
> graded until verification has ruled on §2d.1.' **Verification has now ruled.
> The rung is unblocked, subject to the four conditions above.**"*

**Item B was GRANTED on a ground the petition did not lead with** (`:5229`):

> *"A LADDER-CONSISTENCY CLAUSE IS A CLAIM ABOUT HOW RESOLUTION SCALES UNDER
> REFINEMENT, AND A STATISTIC THAT INCREASES UNDER REFINEMENT CANNOT ESTIMATE IT.
> That is a demonstrable error in the ESTIMATOR, not a preference about
> strictness."*

**No part of that grant licenses a verdict.** §2d.11.1 condition 5 states the
principle for item A and it is carried here for item B without being weakened:
rule 5's one direction stands, and this comparator can only turn a `PASS` or
`GATE FAIL` **into** `NOT A RESULT`, never the reverse.

## 1. THE FOUR BINDING CONDITIONS, AND WHERE EACH ONE IS IMPLEMENTED

`VERIFICATION_CHARTER.md:5235-5240` attaches four conditions to the grant. They
are **binding**, not advice, and each one is a named code path.

| # | condition (charter line) | implementation in `analyse_t5c.py` |
|---|---|---|
| **1** | *"The §6 birth arms `Y-1`…`Y-5` PRINT before any row grades. T5c registered this against itself; I make it binding rather than self-imposed."* (`:5237`) | `run()` calls `birth_requirement()` **before** the first graded value is read. Every arm is an `Arm` object whose `report()` **refuses (exit 2) if either limb is missing** — T5c §6.2's *"an arm that prints one limb is a FAILED control"* made executable. |
| **2** | *"`Y-3`'s refusal must be armed and must fire as designed — refusing when area-weighting and face-count agree within 1 % rather than passing vacuously. That is the anti-vacuity control and the grant rests on it."* (`:5238`) | `arm Y-3` inside `birth_requirement()` computes the area prediction and the face-count prediction, and calls `refuse()` when their separation is **not** more than `Y3_MIN_SEPARATION = 0.01`. **The refusal is driven in `--selftest`** by control `Y-3 CONTROL`, which feeds it a **uniform-area** patch and requires the separation to come back at `0.000000 %`, i.e. requires the refusal condition to hold. |
| **3** | *"The sublayer bound stays on the point maximum. A condition of this grant, not a courtesy."* (`:5239`) | `gate_yplus_t5c()` clause **Y-SUBLAYER** reads `R_max` against `YPLUS_MAX = 5.0` and is evaluated **first**, before Y-LADDER. Unchanged from `analyse_t5b.py:382-387` in statistic, threshold and verdict. |
| **4** | *"⚠ BECAUSE THE REPAIR IS PERMISSIVE IN OUTCOME, EVERY GRADED ROW PRINTS BOTH STATISTICS — area average and point maximum, with the maximum's non-monotonicity shown where it occurs. A reader must be able to see what the old clause would have said, from the row."* (`:5240`) | `print_both_statistics()` prints `R_area`, `R_max`, `R_q95` and the face-count mean **for every registered wall at every level**, each with its margin against the **same** bound, then the observed order of **both** statistics and an explicit `*** NON-MONOTONE UNDER REFINEMENT ***` flag per wall per statistic. It is called for **every** row regardless of verdict, and each printed row additionally carries `PRE_REPAIR_STATE` (T5c §7 condition 4) and both statistics on that row's own wall. |

**AND ONE THING CONDITION 4 IS DELIBERATELY POINTED AT T5c ITSELF.**
`print_both_statistics()` flags non-monotonicity on **`R_area` as well as
`R_max`**. If T5c's own replacement statistic turns out to be non-monotone on
some wall, the instrument says so in the same words it uses against the statistic
it replaced. **A repair that hid the same defect in its successor would be worse
than the defect**, and `§2e`'s companion principle — a discrepancy computed and
then suppressed is worse than one never computed — cuts that way.

## 2. THE FREEZE WITNESS — FULL `sha256` OF THE DISK BYTES

**L-450**: the freeze instrument is blind to a git-blob `sha1` and to a truncated
16-hex digest. The witness below is therefore the **full 64-hex `sha256` of the
file's bytes on disk**, and the git blob `sha1` is recorded **beside** it as a
second, differently-computed referent — never as a substitute.

| artifact | full `sha256` of disk bytes | git blob `sha1` | lines |
|---|---|---|---|
| `verification/runs/T-family/T5c_runs/analyse_t5c.py` | `50b484f0541cea52baea12e1058204f35b7922b40f7e75adf60bb71e13749f0b` | `b32d7e628f3ad70ca02e147faca3e7128ec1dd30` | 1611 |
| `docs/campaigns/T-family/T5c_PREREGISTRATION.md` (the gate, unchanged) | `ba1520191defc1a714bbfaeef19755548176500ff4ba448f02d0b90425065f59` | `e73a16cf5ccf4135f2d1e0b478ce9f829b01be2a` | 318 |

**THE GATE DOCUMENT IS BYTE-IDENTICAL TO THE ONE `e0c5fee8` FROZE.** Verified by
this lane, at this write, by hashing the disk file and comparing against
`git rev-parse HEAD:docs/campaigns/T-family/T5c_PREREGISTRATION.md` — both
`e73a16cf5ccf4135f2d1e0b478ce9f829b01be2a`. **This document does not edit,
amend or supersede it** (rule 6): it registers an instrument that implements it.

**The queue's `GRADER-FREEZE` clause** (`scripts/queue_entry_check.py:455`,
reading `scripts/grader_freeze_gate.py:191-267`) compares the **git blob sha1**
at `<prereg_commit>:<grading_path>` against the disk. That clause is satisfied
only if the queue entry names **this commit** as its `prereg_commit` — which is
why the entry does, and why the entry is written after this commit exists rather
than predicted from it.

## 3. THE CARRY-OVER, ASSERTED RATHER THAN CLAIMED

T5c §5's central rule-2 defence is: *"No number in this section is new. All are
`analyse_t5b.py:142-146` unchanged."* **A claim in prose is a claim.**
`assert_thresholds_carried_over()` re-parses the frozen predecessor at grade time
and `refuse()`s on **any** difference across **20 names**:

`YPLUS_WALLS`, `YPLUS_MAX`, `YPLUS_TARGET`, `YPLUS_TARGET_TOL`,
`CELLS_REGISTERED`, `FS`, `ENDTIME`, `REQUIRED_FIELDS`, `T_REF_K`,
`INTRINSIC_FLOOR_PCT`, `GRADED_H`, `GRADED_T`, `REPORTED_ROWS`,
`G5_IDENTITY_MARGIN_K`, `G5_BOUND_LO_C`, `G5_BOUND_HI_C`, `PLANT_OFFSET`,
`PLANT_SPIKE`, `LEVELS`, `CASE_OF`.

**Driven and passing** in `--selftest` (`THRESHOLD CARRY-OVER: 20 names
re-parsed … and ALL identical`). If a future edit to either file moves a
threshold, **the comparator stops rather than grades**.

## 4. THE RULE-3 CONTROL DEFECT THIS INSTRUMENT DOES NOT INHERIT

`VERIFICATION_CHARTER.md` §2d.11.1, **the same commit**, granted item A and named
the mechanism at `:5194`:

> *"`seen` is the reader's MAXIMUM CHANGE OVER ALL CELLS. **The predicate never
> asks whether that maximum is AT THE PLANTED CELL.**"*

and ruled it *"a rule-3 violation INSIDE a rule-3 control"* — it returned `True`
on a **2.47 K** change while the planted cell **was never the argmax**.

**Every arm in `analyse_t5c.py` reads the plant back AT THE PLANTED FACE, BY
INDEX**, in addition to the aggregate predicate T5c §6.2 registers:

| arm | the registered aggregate predicate | the added at-the-planted-face readback |
|---|---|---|
| **Y-1** | `R_area` moves by exactly `PLANT_OFFSET`, ≤ `1e-9` relative | **every** planted face reads back as `base + plant`, worst-case ≤ `1e-12` relative |
| **Y-2** | `R_max` moves by ≥ `0.9 × PLANT_SPIKE` | the **argmax of the planted field IS the planted face index**; that face reads back as `base + spike`; **every other face is byte-for-byte unchanged**, so the blindness bound is about the plant and nothing else |
| **Y-3** | `R_area` moves by the **area** prediction and NOT by the face-count one | — (the decile plant's discriminating power is the two predictions' separation, re-measured every run) |
| **Y-4** | `R_q95` moves by ≈ `PLANT_OFFSET`; the area-weighted **median** moves by **exactly 0.0** | the 95 % **crossing face** reads back as `base + plant`; the **median face is byte-for-byte unchanged**, so its zero move is a fact about the plant, not about the reader |

> **⚠ THESE ARE STRENGTHENINGS AND THE DIRECTION IS STATED SO NOBODY HAS TO
> INFER IT.** Each added readback can only turn a **passing** arm into a
> **REFUSAL**; none can turn a refusal into a pass. A strengthening in that
> direction cannot loosen a registered control and therefore does not amend
> T5c §6.2. They print under the label `strengthening`, distinct from
> `POSITIVE` and `NEGATIVE`, so a reader can always separate the registered
> predicate from the addition.

**AND THE STRENGTHENING IS SHOWN TO BE LOAD-BEARING, NOT DECORATION.**
`--selftest` carries a **planted failure** that reproduces item A's defect
deliberately: a spike at face 0 rather than at the planted face **satisfies the
aggregate predicate (`True`) and FAILS the at-the-planted-face predicate
(`False`)**. Without that control, the addition would be an untested claim about
itself.

## 5. WHAT THE INSTRUMENT DOES BEFORE IT GRADES — the order is the gate

1. `assert_thresholds_carried_over()` — 20 names against the frozen predecessor.
2. Per level: `patch_areas` + `check_wall_set` (**both directions**), cell count
   re-read from that case's own `log.checkMesh` and compared to
   `CELLS_REGISTERED`, rule-4 `check_completion` **including the age guard**.
3. Per level: `assert_section_6_1()` — T5c §6.1's four rows re-asserted, as that
   section requires (*"MUST re-assert all four rows at grade time and refuse if
   any fails"*): **PRODUCER** (`type yPlus;` in the case's own `controlDict`),
   **ARTIFACT** (the producer's `FoamFile` header carries `class volScalarField`
   **and** `object yPlus`), **READER** (`read_patch_field` + `patch_areas`, and
   **arm Y-5** across **all six** registered walls, not only the planted one),
   **WRITE PATH** (refuses if the scratch directory resolves inside the case
   tree).
4. Per level: `identity_proof()` — **T5c §4.2 re-executed on the bytes about to
   be graded**, not inherited from the registration's prose. Field
   min/max/unweighted-mean against `yPlus.dat`'s min/max/average on every
   registered wall, refusing above `1e-9` relative. This simultaneously proves
   (i) the field is the same data the frozen gate read and (ii) `yPlus.dat`'s
   `average` column is the **unweighted face-count** mean.
5. `birth_requirement()` — arms Y-1…Y-5, both limbs each, on the real producer's
   field through the real reader, planted into a scratch copy.
6. `print_both_statistics()` — binding condition 4.
7. **Only then** the six graded rows, through `grade_row()` **copied verbatim**
   from `analyse_t5b.py:654-710`, i.e. rule 5's registered order unchanged.

**Any refusal above exits 2 and grades nothing.** Comparators refuse rather than
degrade.

## 6. WHAT THIS LANE DELIBERATELY DID NOT DO, SO THAT RULE 2 KEEPS ITS CONTENT

To register a cost from a measurement rather than a guess (§7), this lane timed
the comparator's **readers** against the run tree: `patch_areas` on all three
meshes, `read_patch_field` on one wall, and the `log.solve` regex pass.

> **⚠ NO GATED VALUE WAS COMPUTED. `R_area` and `R_max` were NOT evaluated on the
> real fields by this lane, on any wall, at any level.** The timing calls read
> mesh geometry and one patch's raw values; **no statistic was formed, no
> threshold was compared, and no verdict was produced.** T5c §4.3's claim that
> *"the value of the gated statistic is genuinely not known at freeze"* therefore
> **remains true of this lane at this commit**, and rule 2's evidentiary content —
> that the gate could not have been chosen to fit the answer — is intact.
> Recorded here rather than left for someone to wonder about.

**What the timing did incidentally establish, and it is reported because it is a
fact about the inputs rather than about the gate:** all three levels' `log.solve`
carry `ExecutionTime` line count `5000` and last `Time = 5000`. That is **two of
rule 4's clauses out of six** and it is **not** a completion finding — the age
guard, `rc`, the `End` line and the field presence were **not** checked by this
lane and are the comparator's to check at grade time.

## 7. COST — RULE 12, WITH THE CAP ARITHMETIC SHOWN

**No solver compute.** The `yPlus` fields, the meshes and the three completed
runs are all on disk; T5c re-grades artifacts that already exist.

| item | figure | basis |
|---|---|---|
| **POINT (predicted)** | **1.0 core-min** at `ranks 1` | `T5c_PREREGISTRATION.md` §8, frozen: *"T5c re-grade — **< 1 core-min**, comparator time only"*. **Carried, not re-chosen.** This is the **optimistic** figure and it is the **predicted-vs-actual denominator**. |
| **measured no-optimism basis** | **≈ 8 s wall** at `ranks 1` | **MEASURED by this lane at this write**, reader timing only (§6): `patch_areas` 0.3 / 1.2 / **5.3 s** on the c/m/f meshes = 6.8 s, plus 0.4 s for the three `log.solve` regex passes, plus per-face field reads at < 0.05 s each. The **fine mesh dominates** and it is the term a misprediction would come from. |
| **HARD PER-RUN CAP** | **3.0 core-min**, enforced as a **180 s** `timeout` at `ranks 1` | **estimate 1.0 → ×3 → cap 3.0 core-min.** `1.0 × 3 = 3.0`; `3.0 core-min ÷ 1 rank × 60 = 180 s` wall. Set by **this team**, per Sanaa's 18:00Z item 2 (*"a hard per-run cap (set by the team at ~3× its own estimate, not by me)"*). |
| **headroom against the measurement** | **≈ 22×** | `180 s ÷ 8 s = 22.5`. The cap is built on the **frozen optimistic POINT**, and the **measured** basis sits 22× inside it, so the cap is **not** a censoring cap. |
| **in dollars, POINT** | **$0.00086** | **DERIVED, NOT MEASURED** — `1.0 / 60 × $0.0513/core-h`. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); the rate is **reported-by-owner** (rule 12). |
| **in dollars, CAP** | **$0.00257** | **DERIVED, NOT MEASURED** — `3.0 / 60 × $0.0513/core-h`. |

**DOES THE CAP CENSOR A FALSIFIER?** Stated explicitly because the supervisor's
18:00Z law requires it to be. **No.** T5c's falsifier is a **value** — `R_area`
breaching `YPLUS_TARGET[lv] × 2.0`, or a graded row's triple failing rule 5 — and
**neither outcome costs more comparator time than the passing one**. The
comparator reads the same bytes and evaluates the same predicates whichever way
every clause falls. There is no branch on which the answer "no" is more expensive
than the answer "yes", so no cap can suppress a negative result here. **This is
the case in which the ×3 rule is safe to apply directly**, which is why the
no-speed-up substitution the supervisor accepted for `T25R6a` is **not** invoked.

**ESCALATION TRIGGERS — checked, none fires.** A single run projected over **$150**:
the cap is **$0.00257**, four orders of magnitude below. The envelope at **80 %**:
this rung draws on **no envelope** — the **$1,000 benchmark-ladder envelope is
cfd's, Rungs 0–3, and is neither cited nor charged here** (reading it as lab-wide
funding is the permission laundering rule 9 names). A **third attempt at a
twice-failed thing**: this is T5c's **first** execution; T5b ran once and closed.

**CALIBRATION OWED AT COMPLETION (rule 12).** `actual/predicted` against the
**1.0 core-min** denominator, with waste **named separately and folded into no
ratio**, landing as a row in `docs/COST_CALIBRATION.md`. **A completion report
without it is incomplete.**

> **⚠ A SEPARATE CALIBRATION ROW IS ALREADY OWED AND IS NOT DISCHARGED HERE.**
> `T5c_PREREGISTRATION.md` §8 records `actual/predicted = 451.833 / 419.2 =
> 1.0778` for the **T5b ladder** — 7.8 % over POINT, 46 % under CAP — and states
> that row *"is owed to `docs/COST_CALIBRATION.md` and is NOT discharged by this
> document."* **It is still owed. This document does not discharge it either**,
> and says so rather than letting it disappear between two records.

## 8. WHAT RUNS, WHERE, AND THE RUN DIRECTORY THAT DOES NOT EXIST

| | |
|---|---|
| **command** | `python3 verification/runs/T-family/T5c_runs/analyse_t5c.py --root verification/runs/T-family/T5b_runs` |
| **cwd** | `/home/ubuntu/Certonomous/verification/runs/T-family/T5c_runs` |
| **ranks** | 1 |
| **reads** | `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}` — **read-only**; plants go to a `tempfile.mkdtemp()` scratch copy and the §6.1 WRITE PATH row refuses if that resolves inside the case tree |
| **writes** | stdout only. **This comparator writes nothing into the run tree.** |
| **exit** | `0` every graded row PASS · `1` a graded row did not PASS · `2` refusal |

**RULE 2's PRE-COMPUTE CONDITION, PROVEN THE WAY THIS LAB PROVES IT — by naming
the directory that does not exist.** At this commit,
`verification/runs/T-family/T5c_runs/` contains **`analyse_t5c.py` and nothing
else**: no `0/`, no time directory, no `STATUS.*`, no output. Verified by this
lane immediately before the commit that lands this file.

## 9. WHAT THIS DOCUMENT DOES NOT DO

- It **does not** edit, amend or supersede `T5c_PREREGISTRATION.md`,
  `analyse_t5b.py`, or any other frozen file (rules 2 and 6). T5b's six
  `NOT A RESULT` verdicts **stand as published**.
- It **does not** create, move, widen or retire a gate, threshold, band, cap or
  label. Retiring or widening any of those is **reserved to Sanaa**.
- It **does not** grade anything, and **it does not launch anything.** The
  queue entry is a **proposal on a list**; the launch decision and the
  `SUPERVISION_CHARTER.md` §3 check-4 behind it are the supervisor's own and
  live outside this tree.
- It **does not** predict the outcome. `R_area`'s value on the registered walls
  was **not computed by this lane** (§6), and this rung may yet return
  `NOT A RESULT` on the Y-LADDER clause, on the sublayer clause, or on rule 5's
  grid triples. **A first graded row is not a first PASS**, and nothing here
  should be read as forecasting one.
