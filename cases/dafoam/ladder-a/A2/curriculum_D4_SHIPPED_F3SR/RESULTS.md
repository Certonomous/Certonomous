# Curriculum item D4S-F3SR — the A2 wing endpoint FD table re-run at a repaired cap frame: RESULTS

**Item verdict: `GATE FAIL`.** Both arms completed, both rows are present, the FD bright line is
satisfied on both, and the item fails on a **resource-delivery** gate. Every number below carries
its provenance tag per `DAFOAM_CHARTER.md` §18.6, and every `MEASURED` tag names its artefact.

**Zero solver compute was spent producing this record.** The chain graded itself; this document
reads artefacts.

---

# 1. Item verdict — `GATE FAIL`, **COMPOSED HERE AND NOT READ FROM THE GRADER**

**The frozen grader emits per-gate verdicts and a report. IT COMPOSES NO ITEM VERDICT.** Its
top-level keys are exactly `grader_md5`, `registered`, `report`, `verdicts` — there is **no**
`verdict`, `item_verdict` or `rows` key [MEASURED, `d4s_f3sr_grade_20260831T154117Z.json`, read
by this lane]. **So the item verdict in the heading above was composed by the dafoam-supervisor
from the per-gate verdicts, and this sentence exists so no later reader mistakes it for a number
the instrument printed.**

**The census, taken with NO assumption about the shape of a verdict cell:**

| | |
|---|---|
| gates emitted | **20** [MEASURED, the `verdicts` object] |
| `PASS` | **19** |
| non-`PASS` | **1** — `G12_cpu_placement_F-P` = **`GATE FAIL`** |

**THE SHAPE ASSUMPTION IS RECORDED BECAUSE IT ALREADY PRODUCED A FALSE ALL-CLEAR ONCE.** A walker
that assumes every gate is a dict carrying a `verdict` key reports **"non-PASS gates: none"** on
this document, because `G12_cpu_placement_F-P` maps to a **bare string**. That false clear was
produced and caught during this item's review. The census above was taken by reading every value
in `verdicts` directly against the `CLAUDE.md` rule-1 vocabulary, with no shape assumption, and
was reproduced independently by two readers.

---

# 2. The arms — both ran, both `rc = 0`, two rows as `DAFOAM_CHARTER.md` §6 requires

Both rows are present and distinct, so this **is** a verdict about DAFoam and not about one build.
`G9_two_rows_distinct` = `PASS` [MEASURED, the `verdicts` object].

| arm | row | image | `rc` | wall s | ranks | core-min | cap | OOM |
|---|---|---|---|---|---|---|---|---|
| **F-S** | SHIPPED | `dafoam/opt-packages:latest` `9d45679d…` | **0** | **454** | 4 | **30.267** | 120.0 | false |
| **F-P** | PATCHED | `dafoam-idwarp-rot:v1` `2927768a…` | **0** | **715** | 4 | **47.667** | 120.0 | false |

All cells [MEASURED, `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin/ledger.txt`,
the two `ARM=` rows, read by this lane from the run root and not copied from a relay]. Both rows
carry `inspect(exit,oomkilled)=[0 false]`, `memory=12g`, `cpuset=5,6,7,9`, `enforced_wall_s=1710`
and `enforced_core_min=120.000000`.

**The chain closed cleanly:** `arm=F-S rc=0 stamp=20260831T152616Z`, `arm=F-P rc=0
stamp=20260831T154117Z`, `chain=COMPLETE stamp=20260831T154118Z` [MEASURED, `STATUS.chain`].

**A FIGURE THAT IS EASY TO MISREAD, FLAGGED BECAUSE THIS LANE MISREAD IT FIRST.** A careless parse
of the `ARM=` rows returns `core_min=120.000000` for both arms. **That is `enforced_core_min` — the
CAP — spliced onto the wrong key.** The measured spends are **30.267** and **47.667**. The wrong
reading was produced and corrected before it reached a record, and it is named here because the
two keys sit adjacent on one line and the cap value is identical on both arms, which is exactly
the shape that survives a glance.

---

# 3. THE FREEZE IS EXECUTED, NOT ASSERTED — the frozen file IS the file that ran

`CLAUDE.md` rule 2 fixes the grading path at the pre-registration commit and requires the frozen
file be verified **by hash** against what ran. Both sides, re-verified by this lane at the moment
this record was written:

| side | md5 |
|---|---|
| `grader_md5` recorded **by the run** | **`9596c7bf711a934313a9b4d5801481c6`** [MEASURED, `d4s_f3sr_grade_20260831T154117Z.json`] |
| `md5sum` of the frozen grader **on disk** | **`9596c7bf711a934313a9b4d5801481c6`** [MEASURED, `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_F3SR/d4s_f3sr_grade.py`] |

**They are equal. The frozen file is the file that ran.**

The grading was performed **in-chain by the driver**, not by a later hand:
`grade_rc=0 stamp=20260831T154117Z out=d4s_f3sr_grade_20260831T154117Z.json
note=grader-exit-status-INFRASTRUCTURE-L-342-not-the-verdict` [MEASURED, `STATUS.chain`]. **That
note is the driver's own, and it is correct: `grade_rc` is the grader's exit status and is
infrastructure under `L-342`; it is not the verdict, and the verdict is not read from it.**

---

# 4. `G12_cpu_placement_F-P` — **THE PHYSICS PASSED. THE DELIVERY FAILED.**

**This distinction is the spine of the record, and getting it wrong would misinform every future
reader of this item.**

## 4.1 What passed, stated first, because it is the part a reader is most likely to lose

* **`G5_endpoint_fd_F-S` = `PASS` and `G5_endpoint_fd_F-P` = `PASS`.** The FD-vs-adjoint bright
  line of `DAFOAM_CHARTER.md` §1 is **satisfied on both rows**.
* **`G6_planted_zero_F-S` = `PASS` and `G6_planted_zero_F-P` = `PASS`**, and both
  `G6b_negative_control` gates `PASS`. **The reader was shown able to see a non-zero before its
  zero was taken as evidence** (`CLAUDE.md` rule 3), on both rows.
* `G1_completion_and_age` `PASS` on both; `G9_toolchain_identity` `PASS` on both;
  `G7_count_refusal_control` `PASS` on both; `G10_cap_discipline`, `G11_memory_envelope`,
  `G9_two_rows_distinct` all `PASS`; `G12_cpu_placement_F-S` = `PASS`.

**THE GRADIENT RESULT IS SOUND. THE ADJOINT DID NOT FAIL. NOTHING ABOUT THE PHYSICS IS IN
DOUBT.** The item's single failure is a statement about **how many cores the box delivered to one
container**, and about nothing else.

## 4.2 The failing cell, in full

`report.G12["F-P"]` [MEASURED, the grade JSON]:

| field | value |
|---|---|
| `cpuset_ledger` | `[5, 6, 7, 9]` |
| `cpuset_as_registered` | **`true`** |
| `affinity_inside_cpuset` | **`true`** |
| `all_ranks_on_distinct_single_cores` | **`true`** |
| `delivered_cores_mean` | **`2.3603`** |
| `delivered_floor` | **`3.0`** |
| `delivered_ok_or_not_measured` | `false` |
| `pass` | **`false`** |

**THE PLACEMENT WAS HONOURED EXACTLY AND THE DELIVERY WAS NOT.** Three of the four limbs of this
gate — the registered cpuset, the affinity mask, and one rank per core — all hold. The launcher
did what it was registered to do. **The single limb that fails is the one measuring what the
kernel actually gave the container.** F-S passed the identical gate on the identical cpuset
minutes earlier: `delivered_cores_mean 3.6440` [MEASURED, `ledger.txt`].

**The gate fired as registered and its `GATE FAIL` stands.** §5 below is a finding about the
*cause* of the low mean; it is not a challenge to the gate and it changes no verdict.

---

# 5. WHAT WAS CONTENDING FOR CORES 5,6,7,9? — **THE EVIDENCE POINTS AWAY FROM CONTENTION**, and the answer is a finding, not a conclusion

The question asked was what was competing for the registered cpuset between **15:29:21Z** and
**15:41:17Z**. It is worth asking: this family's own `SO1bR_r2` did not launch until **15:42:42Z**
[MEASURED, process start], so it was **not** us, and F-S had passed on the same four cores minutes
before.

## 5.1 The two designed instruments both say NOTHING WAS THERE

**`siblings_pre=[]` and `siblings_post=[]` on BOTH arms** [MEASURED, `ledger.txt`]. The launcher's
own co-tenancy census found **no other container** at either boundary of either arm.

## 5.2 THE PER-SAMPLE TRACE SETTLES IT, AND IT IS NOT A CONTENTION PROFILE

`delivered_cores` was sampled every ~15.1 s into `F-P_20260831T152922Z_50004.cpu.jsonl`, 46
samples over a 678 s span [all MEASURED, that file, read by this lane]:

| arm | first third | middle third | last third | mean | min | samples < 3.0 floor |
|---|---|---|---|---|---|---|
| **F-S** | 2.935 | 3.995 | 3.938 | **3.6440** | 0.324 | 3 of 29 (10 %) |
| **F-P** | **0.073** | 2.908 | **3.991** | **2.3603** | 0.015 | 20 of 46 (43 %) |

**F-P's first 271 seconds ran below 1.0 core — eighteen consecutive samples — and then it ran at
`3.991` of 4 for the rest of the arm.**

**THAT IS A STARVED START FOLLOWED BY A FULL-SPEED FINISH, WHICH IS THE OPPOSITE OF WHAT
CONTENTION LOOKS LIKE.** A competitor holding cores 5,6,7,9 could not permit a final third at
**3.991 of 4**. F-S shows the same shape, milder (2.935 in its first third). **The mean of 2.3603
is an average over a long near-zero phase and a long near-perfect phase; it is not a level.**

## 5.3 So what WAS the first 271 seconds? — **UNDETERMINED, and here is what would settle it**

A container consuming ~0.07 of 4 cores is **not being denied CPU; it is not asking for CPU.** The
candidate explanations, neither of which this record can choose between from the artefacts on
disk:

1. **An I/O-bound or image-load startup phase** — staging, decomposition, mesh read. Consistent
   with the profile and with F-S's milder version of it.
2. **External host-side load.** Named because it cannot be excluded: **the sibling census sees
   CONTAINERS ONLY and is structurally blind to un-pinned host processes** — agent shells, `git`
   operations, python graders — which the scheduler may place on cores 5,6,7,9 like any other.
   The box was busy: **14 commits landed from five teams inside F-P's 715 s window against 7 in
   F-S's 454 s** [MEASURED, `git log --since/--until` over both windows] — a rate of 1.175/min
   against 0.925/min. **A commit is not a core-second and that proxy is offered as a proxy, not as
   a measurement.** **This lane's own commit `2037ae60` (15:38:44Z) is inside that window**, so the
   host-side load being named here includes work done by the agent writing this record.

**VERDICT ON THE QUESTION: `UNDETERMINED`, and it must not be written up as a cross-team
contention finding, because the strongest evidence — the recovery to 3.991 — argues against
contention of any origin.** **What would settle it:** per-core utilisation sampled from
`/proc/stat` deltas for cores 5,6,7,9 **alongside** the cgroup samples, plus a process census at
each sample. The existing `cpu.jsonl` records only the container's own delivery and throttling
(`delivered_cores`, `throttled_usec`, `nr_throttled`) and **cannot see who else is on the core, or
whether anyone is.** That instrument does not exist and is named here rather than assumed.

**AN ASYMMETRY THAT ARGUES AGAINST THROTTLING AS THE CAUSE:** F-S recorded
`max_nr_throttled=1450` and F-P `max_nr_throttled=1215` [MEASURED, `ledger.txt`]. **The arm that
passed was throttled MORE.** Whatever depressed F-P's mean, the throttle counter did not track it.

---

# 6. COST — the tightest estimate this family produced today

| | |
|---|---|
| **Registered** | **75.862 core-min** = 2 × **37.931** per arm [REGISTERED, `PREREGISTRATION.md:144-145`, `:156`, `:161`], caps **120.0** per arm, ceiling **240.0** |
| **Frozen** | commit **`ed9cda9080080b1f5f450ee3202a6d64ddb76d49`**, 2026-08-27 21:58:16Z — **never revised** [MEASURED, `git log` on that path] |
| **Measured** | **77.934 core-min**, basis **gross** = 30.267 + 47.667 [MEASURED, `ledger.txt`] |
| **Ratio** | **1.0273** actual/registered |
| **Against the ceiling** | **0.3247×** of 240.0. **No overrun; no cap fired** — the longest arm's 715 s host wall is 41.8 % of its 1,710 s enforced deadline |
| **Cleaned** | **= gross.** The longest arm is 715 wall s, so the charter §2 3,600-s stall rule matches no row and nothing is excluded |
| **Dollars** | **$0.06663 measured-side, $0.06486 registered-side — DERIVED, NOT MEASURED** at $0.0513/core-h; `cost_basis` **REPORTED-BY-OWNER** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

**A 2.73 % miss on a registration frozen four days before the run and never touched.** The
registered figure was built from a rate model — `(115.0 + 22 × 20.635) × 4 ÷ 60 = 37.931 core-min`
per arm (`PREREGISTRATION.md:156`) — and it held.

**THE PER-ARM SPREAD IS THE WHOLE ERROR, AND IT CANCELS.** F-S came in at **0.798×** its 37.931
(30.267) and F-P at **1.257×** (47.667). **The item's excellent 1.0273 is two offsetting arm-level
misses, not two accurate ones**, and a reader should not take the aggregate as evidence that the
per-arm model is tight.

## 6.1 The PATCHED arm cost 57.5 % more than SHIPPED — **REPORTED, NOT INTERPRETED**

`47.667 / 30.267 = 1.5749` [DERIVED, arithmetic on two MEASURED figures].

**THIS IS NOT ATTRIBUTABLE TO THE PATCH AND IS NOT ATTRIBUTED TO IT HERE.** The two arms ran
**different images** — `dafoam/opt-packages:latest` against `dafoam-idwarp-rot:v1` — so the delta
carries an image term and a patch term that **this chain contains no control to separate.** A
same-image control was not run and is not implied by anything on disk.

**One observation is offered, and it is arithmetic on measured quantities rather than an
attribution:** F-P's wall exceeds F-S's by **261 s**, and F-P's sub-1.0-core startup phase lasted
**271 s** (§5.2). **The extra wall and the starved phase are the same size to within 4 %.** That is
consistent with the entire cost delta living in the startup phase rather than in the arms'
compute — **and it is equally consistent with a larger image taking longer to load, which is not a
statement about the patch either.** **Both readings require a control this item does not have.**

---

# 7. WHAT IS OWED

1. **The calibration row is OWED and is NOT filed here.** `docs/COST_CALIBRATION.md` is
   **append-blocked**: `scripts/append_record.py` refuses the whole record at **exit 7** on its
   D549 shape audit, over two strike-form lines that are not this item's. The row is owed at the
   unblock, and it will carry: registered 75.862, measured 77.934, ratio 1.0273, the per-arm
   cancellation of §6, and the §6.1 delta reported without attribution.
2. **`G12`'s mean-versus-profile question is a live finding, not a defect claim.** §5 establishes
   that `delivered_cores_mean` averages a starved startup with a full-speed finish. **Whether the
   gate should read a mean over the whole arm is a threshold question and is NOT taken here** — the
   gate fired exactly as registered, the `GATE FAIL` stands, and moving a registered threshold is
   reserved.
3. **A per-core utilisation instrument does not exist** (§5.3) and would settle the class of
   question §5 could only bound.

---

**Record written 2026-08-31 by a dafoam lane from the artefacts named above. Item verdict `GATE
FAIL` composed by the dafoam-supervisor from the 19/1 per-gate split; the grader composes no item
verdict. No gate, threshold, band, cap or label is moved by this document.**
