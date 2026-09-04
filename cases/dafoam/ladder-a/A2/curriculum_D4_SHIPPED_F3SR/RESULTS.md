# Curriculum item D4S-F3SR — the A2 wing endpoint FD table re-run at a repaired cap frame: RESULTS

> ## ⚠ CORRECTED 2026-09-03 — THE VERDICT OF RECORD IS **`PASS`**. SEE **CORRECTION 1** AT THE FOOT.
>
> **The line struck immediately below is the original wording, preserved verbatim and struck, never
> rewritten.** It was composed by hand from a gate the pre-registration **excludes** from
> composition, on a premise that is false. The frozen grader's own emitted value is
> `ITEM_two_row_endpoint_fd` = **`PASS`**.
>
> **AND THE FAILING GATE DOES NOT DISAPPEAR BECAUSE THE VERDICT IMPROVED:**
> **`G12_cpu_placement_F-P` is `GATE FAIL`** — a real gate failure, on the delivered-cores limb,
> reported here beside the verdict and treated in full at §4. `PREREGISTRATION.md` §5 does not admit
> it to the item composition; that is the registration's choice, made before compute, and it is not
> a judgement this document may re-make in either direction.
>
> **A READER MUST LEAVE THIS HEADING HOLDING BOTH FACTS: the item is `PASS`, and `G12_cpu_placement_F-P`
> failed.**

~~**Item verdict: `GATE FAIL`.** Both arms completed, both rows are present, the FD bright line is
satisfied on both, and the item fails on a **resource-delivery** gate.~~ Every number below carries
its provenance tag per `DAFOAM_CHARTER.md` §18.6, and every `MEASURED` tag names its artefact.

> **AND THE ACCEPTANCE CRITERION THIS ITEM RAN UNDER IS NOT THE PRODUCER'S.** The instrument
> **DISARMS** DAFoam's own primal-acceptance clause — `primalMinResTolDiff` 1e3 → **`1.0e12`** — and
> replaces it with a stationarity rule. That was registered before compute and it is legitimate; it
> is also the reason one of the two FD tables below exists at all, and until this correction **this
> document did not mention it**. **CORRECTION 2** at the foot carries it with the measurement that
> bounds it.

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
  line of `DAFOAM_CHARTER.md` §1 is **satisfied on both rows**. ~~**⚠ AND BOTH AGGREGATES SIT BELOW `VERIFICATION_CHARTER.md:861-863`'s 2.5–5 % HARNESS-SOUND FLOOR — READ CORRECTION 3 AT THE FOOT BEFORE TAKING EITHER FIGURE AS A SUB-PERCENT VERIFICATION.**~~ **[⚠ STRUCK 2026-09-03 — CORRECTION 4. Both aggregates sit below the floor of `VERIFICATION_CHARTER.md` §2al AS AMENDED (v1.56, `fc8d06e2`), whose base is n=2 and whose qualifier is the MESH. Read CORRECTION 3 as corrected by CORRECTION 4.]**
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

---

# CORRECTION 1 — 2026-09-03. The item verdict of record is **`PASS`**, restored from this item's own frozen grader; the `GATE FAIL` in the original heading was composed by hand from a gate the registration excludes

**Ruled by the dafoam-supervisor, 2026-09-03, after reading every link himself.** Written by a
dafoam lane. **NOTHING WAS RE-GRADED AND NO COMPUTE WAS SPENT.** No instrument was run, no artefact
was written, no run root was touched. Every value below is read out of the frozen grader's own
emitted JSON, the frozen registration, or the grader's source, each cited.

**What changed above this section, stated so no reader has to diff for it:** a correction banner was
inserted at the head and the original verdict sentence was **struck with `~~…~~`, not deleted and
not reworded** — its exact wording survives on the page. Nothing else above this line was altered.
The two sections `docs/COST_CALIBRATION.md` cites (§6 and §6.1) are untouched, and nothing in the
repository cites this record by line number.

## C1.1 THE VERDICT, AND ITS AUTHORITY

| | |
|---|---|
| **verdict of record** | **`PASS`** |
| authority | `ITEM_two_row_endpoint_fd` = `PASS`, emitted by this item's own frozen grader |
| artefact | `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin/d4s_f3sr_grade_20260831T154117Z.json`, key `verdicts.ITEM_two_row_endpoint_fd` |
| the grader | `d4s_f3sr_grade.py`, `grader_md5` `9596c7bf711a934313a9b4d5801481c6` as recorded in that same JSON |
| where it is computed | `d4s_f3sr_grade.py:796-806`, under the comment `# ---- item composition (PREREGISTRATION.md section 5)` |
| superseded | **`GATE FAIL`**, the original heading, struck above |

## C1.2 THE REGISTERED COMPOSITION, QUOTED — and `G12` is not in it

`PREREGISTRATION.md` §5, frozen `ed9cda9080080b1f5f450ee3202a6d64ddb76d49` on 2026-08-27, four days
before the run, never revised. The **ITEM** row, verbatim:

> **`NOT A RESULT`** if any arm fails G1 or G-ACC, any control fails, any OOM, or any row's G5 is
> `NOT A RESULT`; else **`PASS` iff both rows' G5 `PASS`; else `GATE FAIL`** (a two-row divergence
> is a finding, D4-SHIPPED §5)

The grader implements exactly that and nothing else:

    rows_ok = all(report["G1"][a]["pass"] and report["G_ACC"][a]["pass"] and report["G6"][a]["pass"]
                  and report["G6b"][a]["pass"] and report["G7"][a]["pass"] for a in ARMS)
    g5 = [verdicts["G5_endpoint_fd_%s" % a] for a in ARMS]
    if not rows_ok or "NOT A RESULT" in g5 or oom:   item = "NOT A RESULT"
    elif all(v == "PASS" for v in g5):               item = "PASS"
    else:                                            item = "GATE FAIL"

**`G12` appears nowhere in the composition, in the registration or in the code.** So does `G9`,
`G10` and `G11`. That exclusion is the registration's own choice, made before compute.

## C1.3 THE `PASS` RESTS ON EVERY LIMB OF §5, NOT ONLY ON `G5` — read from the JSON

| arm | `G1` | `G_ACC` | `G6` planted zero | `G6b` negative control | `G7` count refusal | **`G5` bright line** |
|---|---|---|---|---|---|---|
| **F-S** (SHIPPED) | `True` | `True` | `True` | `True` | `True` | **`PASS`**, aggregate **0.350109 %** of a 5 % band — **⚠ below the harness-sound floor, see CORRECTION 3** |
| **F-P** (PATCHED) | `True` | `True` | `True` | `True` | `True` | **`PASS`**, aggregate **0.163445 %** of a 5 % band — **⚠ below the harness-sound floor, see CORRECTION 3** |

`arms_oomkilled` = `[]`. Every one of the five registered components graded on both rows
(`n_graded` 5 of `n_registered` 5), **0 sign flips**, **0 without plateau**, **0 ungradeable**,
**0 near-zero**, on both arms. So `rows_ok` is true, no `G5` is `NOT A RESULT`, no arm OOM-ed, and
both `G5` are `PASS` — the composition's `PASS` branch, on every limb.

## C1.4 THE FALSE PREMISE, QUOTED, AND WHY IT IS FALSE

The original record justified its hand-composition with this sentence (§1, unaltered above):

> **"THE FROZEN GRADER EMITS PER-GATE VERDICTS AND A REPORT. IT COMPOSES NO ITEM VERDICT.** Its
> top-level keys are exactly `grader_md5`, `registered`, `report`, `verdicts` — there is **no**
> `verdict`, `item_verdict` or `rows` key [MEASURED, `d4s_f3sr_grade_20260831T154117Z.json`, read
> by this lane]."

**THE MEASUREMENT IS TRUE. THE CONCLUSION IS FALSE.** The four top-level keys are exactly those
four; there is indeed no top-level `verdict`, `item_verdict` or `rows` key. **But the item verdict
does not live at the top level. It lives INSIDE `verdicts`, under the key
`ITEM_two_row_endpoint_fd`** — set at `d4s_f3sr_grade.py:806` and asserted as the item verdict by
that grader's own self-test in at least six legs (`:987`, `:1030`, `:1052`, `:1146`, `:1180`,
`:1186`), where a planted `G1` failure, a planted drift, a planted sign flip and an OOM row are each
required to drive `ITEM_two_row_endpoint_fd` to the matching label.

**A SEARCH LOOKED FOR THREE KEY NAMES, DID NOT FIND THEM, AND PUBLISHED THAT ABSENCE AS PROOF OF
NON-EXISTENCE RATHER THAN AS "I DID NOT LOOK WHERE IT LIVES."** That is `CLAUDE.md` rule 3's
planted-zero failure with a `[MEASURED]` tag on it, and **the tag is what makes it dangerous**: the
measurement is honest, so the inference inherits a credibility it did not earn. A reader checking
the citation would confirm the four key names and stop.

## C1.5 WHY THE HAND-COMPOSITION WAS NOT PERMITTED, IN EITHER DIRECTION

1. **The grading path is fixed at the pre-registration commit** (`CLAUDE.md` rule 2). §5 is the
   registered composition, the frozen grader implements it, and no other reader — and no hand — may
   be substituted for it.
2. **`GATE FAIL` was composed from `G12`, which §5 excludes.** That is not a stricter reading of the
   registered rule; it is a different rule.
3. **The one override direction the lab permits is the other one.** Rule 5 lets a gate turn a `PASS`
   or `GATE FAIL` **into** `NOT A RESULT`, never the reverse. **Nothing anywhere authorises a
   hand-composed `PASS` → `GATE FAIL`.** The hand-composition was unsanctioned twice over.

**AND THE UNCOMFORTABLE PART IS SAID HERE RATHER THAN ELIDED: this correction moves a verdict from
harsher to softer, and it is ruled by the same role that composed the harsher one.** That is
precisely why the authority cited in C1.1 is the frozen grader's own emitted value and not anyone's
judgement — **the correction removes a discretion that was never authorised; it does not exercise a
new one.** A hand-composed verdict is the defect whichever way it leans. **A false `GATE FAIL` is
not the safe error:** it discards a result the lab paid 77.934 core-min for, and it makes the record
wrong in the direction readers trust least to be checked. Honesty is carried by the value.

## C1.6 `G12_cpu_placement_F-P` IS STILL `GATE FAIL`, AND IT IS NOT DIMINISHED BY THIS CORRECTION

`verdicts.G12_cpu_placement_F-P` = **`GATE FAIL`**; `verdicts.G12_cpu_placement_F-S` = `PASS` on the
identical gate and the identical cpuset minutes earlier. §4 of this record treats it in full and is
unaltered. **The verdict improving does not make the gate failure smaller, and this correction
neither re-grades it, explains it away, nor moves it out of the reader's path** — the head banner
carries it beside the restored verdict for exactly that reason. What §5 says is that this item's
verdict does not turn on it. What §4 says about *why* it failed is untouched and still open.

## C1.7 ⚠ THE SAME FALSE CLAIM HAS PROPAGATED INTO A SECOND RECORD — NOT REPAIRED HERE

`docs/COST_CALIBRATION.md:316`, the landed calibration row
`C-20260831T164216.179599Z-19ea8c16`, carries **"ITEM VERDICT `GATE FAIL`"** and repeats the premise
verbatim: *"Item verdict composed by the `dafoam-supervisor` from the 19/1 per-gate split; the
grader composes no item verdict."*

**That row is NOT corrected by this document and must not be silently edited here.**
`docs/COST_CALIBRATION.md` has its own append rules and its own correction mechanism, and its cost
figures — 77.934 measured against 75.862 registered, ratio 1.0273, waste 0.000 — are **unaffected**:
nothing in this correction touches a core-minute. **The defect is confined to the row's verdict cell
and its restatement of the false premise**, and clearing it is the owning team's, through that
file's own correction path. It is named here so it is not discovered a third time.

---

# CORRECTION 2 — 2026-09-03. The acceptance criterion this item ran under was **not** the producer's: `primalMinResTolDiff` was DISARMED to `1.0e12`, and until now this document did not say so

**Zero compute. Nothing re-graded.** Every figure below is read from the run roots, the frozen
registrations or the frozen grader's output, each cited.

**THE GAP THIS CLOSES.** Before this correction the word "disarm" and the value `1e12` appeared
**zero times** in this document. Both registrations carry the disarm explicitly; the document a
reader reaches for the verdict did not. **A reader must not have to find the pre-registration to
learn that the FD table on one of the two rows exists because a convergence criterion was
disarmed.**

## C2.1 WHAT WAS DISARMED, AND WHAT THE NUMBER MEANS

`d4s_f3s_fd_endpoint.py:69-70` sets `DISARM_KEY = "primalMinResTolDiff"`,
`DISARM_TOL_DIFF = 1.0e12`, writes it into the exec'd producer's `daOptions`, and then **reads the
effective value back off the constructed `DASolver` and REFUSES (rc 2) if it did not take**.

`primalMinResTolDiff` is the **ratio bar** in DAFoam's `DASolver::checkPrimalFailure()`
(`src/adjoint/DASolver/DASolver.C:2744-2752`, quoted verbatim in this lab's own record at
`cases/dafoam/ladder-a/A6/rung_n16_np1/RESULTS.md:79-84`):

    scalar tolMax = daOptionPtr_->getOption<scalar>("primalMinResTolDiff");
    if (daGlobalVarPtr_->primalMaxRes / primalMinResTol_ > tolMax) { … return 1; }

A primal is declared failed iff `primalMaxRes / primalMinResTol > primalMinResTolDiff`, so the
effective accept floor is `primalMinResTol × primalMinResTolDiff`. Printed by the instrument itself
in **all four** arm logs of this item and its predecessor, identically:

    D4S_F3S_DISARM primalMinResTolDiff registered_before=1000.0 effective=1000000000000.0 primalMinResTol=1e-08

**So the accept floor moves from `1e-8 × 1e3` = `1e-5` to `1e-8 × 1e12` = `1e+4`** — a level no
primal reaching `endTime` can exceed. **The producer's threshold clause cannot fire.** The
instrument records that number itself, as `producer_accept_floor_now` in its `disarm` record.

*Provenance caveat, stated rather than glossed: the toolchain source was NOT read from the image by
the lane writing this correction — no container was invoked. The extract above is this lab's own
verbatim quotation of it, cited by path and line.*

## C2.2 WHAT REPLACED IT, AND WHY — this is a repair, not a relaxation

`d4s_f3s_accept.py` replaces the threshold with a **stationarity rule**: for every printed equation,
the initial residual must be stationary to `1e-3` relative over the last 200 iterations, continuity
`sum local ≤ 1e-6`, every parsed number finite, and a capture yielding zero `Time =` lines is a
**reader failure that REFUSES, never an acceptance**. **The rule never compares a residual to a
level**, so it is blind to which side of `1e-5` a floor sits.

The reason is `D4S-PREREG-DEF-1`, and it is measured, not argued
(`curriculum_D4_SHIPPED_F3S/PREREGISTRATION.md` §1, `d4s_f3s_accept.py` docstring):

| row | endpoint `nuTilda` floor | against the producer's `1e-5` |
|---|---|---|
| PATCHED (`curriculum_D4` F3) | **9.780100659e-06** | accepted, by **2.2 %** |
| SHIPPED (`D4-SHIPPED` F3 r2) | **1.115891818e-05** | rejected, by **11.6 %** |

**A threshold sitting at the instrument's own residual floor decides the arm by which side of the
floor the endpoint lands.** Both series were stationary to better than `1e-6` relative over their
last 200 iterations. The supervisor's ruling that created this repair **explicitly refused** the
alternative — restating the threshold `1e3 → 2e3` — as *"a threshold moved after seeing which side
the endpoint sat on"*, and required the one rule be applied to **both** rows, with the PATCHED row
**re-bought** so it could not be a SHIPPED-only relaxation.

## C2.3 IT IS REGISTERED BY VALUE, AND GATED

* `curriculum_D4_SHIPPED_F3S/PREREGISTRATION.md:67` — *"The producer's threshold clause is
  **DISARMED, not loosened** … set to `DISARM_TOL_DIFF = 1.0e12` — an accept floor of 1e4 that no
  primal reaching `endTime` can exceed — and the EFFECTIVE value is READ BACK from the constructed
  `DASolver`; if it is not 1e12 the instrument REFUSES (rc 2)."*
* **This item's** `PREREGISTRATION.md:50` carries the instrument forward as a **byte-identical copy**
  (md5 `9ce78caa…`) with `DISARM_TOL_DIFF 1.0e12` named in the row.
* **This item's** `PREREGISTRATION.md:184` makes gate **`G-ACC`** `PASS` only if *"every capture
  re-evaluates ACCEPTED ∧ every instrument record agrees ∧ **disarm read-back = 1e12**"*.
  `G_ACC_stationarity_F-S` and `G_ACC_stationarity_F-P` are both **`PASS`** in this item's grade JSON.

## C2.4 ⚠ THE BOUNDING MEASUREMENT — the disarm's operational effect is exactly one thing

Read from the per-primal acceptance records, `d4s_f3s_accept.jsonl`, key `r_end`, in the four arm
directories of this item and its predecessor — **88 primals**, 22 per arm:

| item / arm | row | primals | end residual (`nuTilda`, the worst equation) | against the undisarmed `1e-5` |
|---|---|---|---|---|
| `D4S-F3S` / `F-S` | SHIPPED | 22 | **1.116021650e-05** | **all 22 ABOVE** |
| `D4S-F3S` / `F-P` | PATCHED | 22 | **9.781615363e-06** | all 22 below |
| `D4S-F3SR` / `F-S` | SHIPPED | 22 | **1.116021650e-05** | **all 22 ABOVE** |
| `D4S-F3SR` / `F-P` | PATCHED | 22 | **9.781615363e-06** | all 22 below |

**44 of 88 primals — every SHIPPED-row primal — would have been rejected by the undisarmed
threshold, and none of the 44 PATCHED-row primals would.** So **the disarm's entire operational
effect is that the SHIPPED row's FD table exists at all.** It buys nothing on the patched path.

*The count above was produced by a reader whose first pass returned `primals = 0` on all four arms —
it read a key the record does not use. That false zero was caught by a control counting records
carrying an `accepted` field (22 per arm, not 0) and the reader was repaired before any number was
written here. Disclosed under rule 3.*

## C2.5 AND THE FALSIFIER THE REGISTRATION SET FOR EXACTLY THIS QUESTION WAS **HIT**

`P3` — *"PATCHED reproduces `D4` F3 to printed digits"* — was registered **before compute** as the
test of whether the disarm changed the answer on the row where the old threshold was already
satisfied. Scored in **both** items' grade JSONs:

| | |
|---|---|
| `P3_patched_reproduces_D4_F3_to_printed_digits` | **`HIT`** |
| tolerance | `1e-12` relative |
| **`worst_rel_diff` across all five components** | **`0.0`** |
| components | `shape[46]`, `shape[18]`, `shape[0]`, `twist[0]`, `patchV[1]` — each `rel_diff_J_adj` `0.0` and `rel_diff_d_hi` `0.0` |
| reference | `curriculum_D4` arm F3, produced under the **undisarmed** `primalMinResTolDiff = 1e3` |

**The PATCHED row, run with the disarm live, reproduces bit-for-bit the table produced under the
threshold. The disarm demonstrably moved nothing where the old threshold was satisfied.**
`P6_both_rows_reproduce_D4S_F3S_to_printed_digits` is likewise **`HIT`**.

## C2.6 WHAT THIS DOES AND DOES NOT LICENCE

**It does not licence relaxing a convergence criterion anywhere else.** What makes this one
admissible is the whole set together: registered by value before compute; justified by a
*measurement* of the residual floor rather than by convenience; gated by a read-back that refuses if
the disarm did not take; replaced by a rule that never compares a residual to a level and is applied
identically to both rows; and bounded by a falsifier, registered in advance, that was hit at
`0.0` relative difference. **A relaxation missing any one of those is a different object.** The
defect this correction repairs was never the disarm — it was that this document did not tell its
reader about it.

---

# CORRECTION 3 — 2026-09-03. Both FD aggregates sit **below** `VERIFICATION_CHARTER.md` §7 step 4's harness-sound floor, and until now this document did not say so

**Ruled by the dafoam-supervisor, 2026-09-03.** Written by a dafoam lane. **NOTHING WAS RE-GRADED
AND NO COMPUTE WAS SPENT.** No instrument was run, no artefact written, no run root touched, no
container invoked. **The item verdict does not move: `ITEM_two_row_endpoint_fd` remains `PASS`.**
No gate moves. No threshold moves. This is a **disclosure repair**, of the same class as
CORRECTION 2 — the defect is not the number, it is that the document let a reader meet the number
without the sentence the charter attaches to it.

**What changed above this section, stated so no reader has to diff for it.** Two edits, both
**additive markers appended inside existing lines**, so **lines whose number changed above this
section: 0**:

1. §4.1's `G5` bullet (the sentence *"the FD-vs-adjoint bright line … is satisfied on both rows"*)
   now carries a pointer to this correction. Its original wording is intact and unreworded.
2. §C1.3's two verdict cells now carry the same pointer. **The figures, the gate readings and every
   word of CORRECTION 1's reasoning are untouched.**

Nothing else above this line was altered. §6 and §6.1 — the two sections `docs/COST_CALIBRATION.md`
cites — remain untouched, and nothing in the repository cites this record by line number.

## C3.1 THE NUMBERS AND THE FLOOR

~~`VERIFICATION_CHARTER.md:861-863`, the fourth of the five reporting-protocol steps, none optional:~~ **[⚠ STRUCK 2026-09-03 — CORRECTION 4. Cite `§2al` as amended, v1.56, `fc8d06e2`, not retired line numbers.]**

> ~~*"The harness-sound floor on this stack, for a case with no flagged components, is 2.5 to 5~~
> ~~percent vector-norm relative error. A number below that is a claim about the harness."*~~ **[⚠ STRUCK 2026-09-03 — CORRECTION 4. The second sentence was REMOVED from the charter as INVENTED; "on this stack" is now "for THIS DATASET". The amended clause is quoted in CORRECTION 4.]**

The clause's precondition is met here — `n_sign_flips` `0`, `n_without_plateau` `0`,
`n_ungradeable` `0`, `n_near_zero` `0`, on both arms — so this row is **inside** the clause's scope,
not outside it.

| row | aggregate, as graded | against the floor's lower edge |
|---|---|---|
| **F-S** (SHIPPED) | **0.350109 %** | **7.14× below** |
| **F-P** (PATCHED) | **0.163445 %** | **15.30× below** |

[MEASURED, `report.G5.<arm>.aggregate_rel_err_pct` in
`/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin/d4s_f3sr_grade_20260831T154117Z.json`,
grader md5 `9596c7bf711a934313a9b4d5801481c6`. The ratios are arithmetic on those two values and the
charter's 2.5 %.]

~~**Stated plainly, in the form the charter asks for and four sibling records already use~~
~~(`curriculum_D19M/RESULTS.md:99`, `curriculum_D19O/RESULTS.md:86-93`,~~
~~`curriculum_D8/RESULTS.md:322-329`, `curriculum_SO3/RESULTS.md:195`): these are claims about the~~
~~harness. This record does not claim a sub-percent verification of the DAFoam gradient.**~~ **[⚠ STRUCK 2026-09-03 — CORRECTION 4: this leaned on the invented sentence.]** The floor
is **REPORTED HERE, NEVER GATED** — `G5`'s registered band is 5 % and it is unchanged.

## C3.2 THE SAME TABLE RESTRICTED TO THE FLOOR'S OWN INSTRUMENT

`docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md:155` records that the floor **"is calibrated on shape
derivatives through IDWarp."** This item's five graded components are **not one instrument**:

| component | class | warp in the derivative chain? |
|---|---|---|
| `shape[46]`, `shape[18]`, `shape[0]` | `nom_addLocalDV`, pyGeo | **yes** |
| `twist[0]` | `nom_addGlobalDV`, pyGeo | **yes** |
| `patchV[1]` | `"type": "patchVelocity"`, **angle of attack** | **no — a boundary condition** |

[MEASURED, `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin/d4_opt_runScript.py`
md5 `2906d52a5dbed2bacbaeaf85a37d3fe8`: `:78-79` `"patchV": {"type": "patchVelocity"`; `:166`
`self.dvs.add_output("patchV", val=np.array([U0, aoa0]))`; `:241` `designVarsComp=[1]` targeting
`CL` — index 1 is the angle of attack. `:146` twist, `:152` shape.]

Restricting the same vector norm to the four warp-chain components:

| row | as graded (5 components) | **4 warp-chain components only** | `patchV[1]` alone |
|---|---|---|---|
| **F-S** | 0.350109 % | **0.861604 %** (2.90× below the floor) | 0.001631 % |
| **F-P** | 0.163445 % | **0.391451 %** (6.39× below the floor) | 0.001487 % |

[MEASURED — recomputed by this lane from the grader's own `report.G5.<arm>.graded` array in the JSON
named above, using the grader's own reference `d_hi` and the same vector-relative statistic
`‖J_adj − J_fd‖ / ‖J_fd‖`. The full-table values reproduce the grader's to six decimal places, which
is the check that the recomputation is on the grader's convention and not on this lane's.]

**BOTH FRAMINGS ARE STATED BECAUSE THE UNRESTRICTED NUMBER ALONE IS WHAT MAKES THIS ROW LOOK
ANOMALOUS.** Restricted to the instrument the floor was actually calibrated on, the row is still
below the floor — 2.90× and 6.39× — so **the sub-floor reading is real on the floor's own stack and
is not an artefact of the instrument mix.**

## C3.3 THE MECHANISM — and this is the observation the verification amendment now turns on

**`patchV[1]` carries 91.37 % (F-S) and 90.87 % (F-P) of the vector norm's magnitude, and it has the
smallest error of the five. It pulls the aggregate down by 2.46× and 2.40×.** [MEASURED, same JSON,
same array: `|d_hi(patchV[1])| / ‖d_hi‖` and the ratio of the restricted to the unrestricted
aggregate.]

**A floor derived for a warp-chain instrument does not straightforwardly reach an aggregate that is
90 % dominated by a component with no warp chain at all.** That is stated here as the **mechanism**,
not as a finding that the clause fails to apply. `V_STANDARD_FD_VS_ADJOINT.md:176-180` already
requires that *"a DAFoam record states which instrument it is on"* and separates a shape-DV number
at 0.03 % (to which §7 step 4 *"applies in full"*) from a field-DV number at 0.03 % (to which it does
not). **This record is the mixed case that rule does not yet name**, and whether the clause reaches a
mixed aggregate is `VERIFICATION_CHARTER.md`'s to rule, not this record's. It has been routed to the
verification supervisor as a clause question. **Nothing here argues the floor does not apply.**

## C3.4 THE FLOOR'S SOURCE STUDY, AND THE SAME-MESH COMPARATOR

~~The charter states the floor at `:861-863` with no derivation on its face.~~ **[⚠ STRUCK 2026-09-03 — CORRECTION 4: TRUE WHEN WRITTEN, NO LONGER TRUE. `§2al` (v1.56, `fc8d06e2`) RESTORED the derivation, the n=2 base and the mesh qualifier into the clause itself.]** Its source is
`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A_stepsize_study.md:89-90` (md5
`b6fcde0f55e9b357d43140f591db399b`, 136 lines), whose five recommended steps are the charter's five
steps nearly verbatim:

> *"For a case with **no flagged components**, this dataset's harness-sound floor is **2.5-5%**
> vector-norm relative error (2.5-3.0% here at 4032 cells; **A2 independently achieved 1.71% at 38304
> cells / 96 DVs — consistent with the floor tightening on finer meshes**)."*

**The comparator a reader needs, and it is very close to this row** [MEASURED]:

| | the study's A2 datum | this item |
|---|---|---|
| mesh | **38,304 cells** | **38,304 cells** — `F-S_20260831T151834Z_40613.log:207` `Global Cells: 38304` |
| shape DVs | **96** | **96** — `adjoint.shape` length in `F-S/d4s_f3s_fd_endpoint.json` |
| aggregate | **1.71 %** | 0.350109 % / 0.163445 % |

**This item is on the same rung, the same mesh and the same shape-DV count as the one data point in
the floor's own establishing dataset that already sits below the floor.** The study's own words
attribute that to mesh refinement — *"consistent with the floor tightening on finer meshes"* — a
qualifier the charter clause does not carry.

**What that does and does not establish.** It establishes [MEASURED] that a sub-floor aggregate on
this mesh is what the floor's source study predicts rather than an anomaly. It does **not** establish
that the clause does not reach this row, and this record does not claim that. A reader is now able to
weigh 0.350109 % and 0.163445 % against a same-mesh, same-DV-count comparator instead of against
nothing, which is the whole purpose of this correction.

## C3.5 WHAT THIS CORRECTION DOES NOT DO

It does not move the verdict, which remains `PASS` from the item's own frozen grader. It does not
move, widen or reinterpret `G5`'s 5 % band. It does not re-grade, re-run or annotate any artefact —
every figure above is read or recomputed from artefacts already on disk. It does not amend, quote as
amended, or propose wording for `VERIFICATION_CHARTER.md`, which is not this team's document and
whose floor is a threshold. **And it does not diminish `G12_cpu_placement_F-P`, which remains
`GATE FAIL` and is treated at §4.**

**Nothing in this item or this record is filed, sent, emailed, uploaded, posted or commented outside
this box, now or ever** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

---

# CORRECTION 4 — 2026-09-03. CORRECTION 3 was written against a clause that has since been amended: the sentence it leaned on was **REMOVED FROM THE CHARTER AS INVENTED**

**Ruled by the dafoam-supervisor, 2026-09-03.** Written by a dafoam lane. **ZERO COMPUTE**, nothing
re-graded, no artefact written, no run root touched, no container invoked. **The verdict does not
move: `ITEM_two_row_endpoint_fd` remains `PASS`. No gate moves. No threshold moves.** `G5`'s
registered band is 5 % and is unchanged. `G12_cpu_placement_F-P` remains `GATE FAIL`.

## C4.1 WHAT HAPPENED, AND IT IS NOT A CHANGE OF MIND

CORRECTION 3 was drafted and committed (`65709a94`) against
`VERIFICATION_CHARTER.md:861-863` as it then stood. **While it was being drafted, the verification
team amended that clause** — `fc8d06e2`, **`VERIFICATION_CHARTER.md` v1.56, new `§2al`** — and made
three changes:

1. **`"on this stack"` → `"for THIS DATASET"`.** The transcription had widened one study into a
   whole stack.
2. **The n=2 base is RESTORED into the clause**: 2.5-3.0 % at 4,032 cells, and A2's **1.71 % at
   38,304 cells / 96 DVs**, *"consistent with the floor TIGHTENING ON FINER MESHES."*
3. **⚠ The sentence *"A number below that is a claim about the harness"* is STRUCK AS INVENTED.**
   `§2al.2`: it *"APPEARS NOWHERE IN THE SOURCE and is CONTRADICTED BY the source's own SECOND DATA
   POINT, which is BELOW the floor and is read there as CONFIRMING it. On a FINE MESH a sub-floor
   number is WHAT THE ESTABLISHING STUDY PREDICTS, not an anomaly and not a claim about the harness."*

**The third change removes the sentence CORRECTION 3 quoted and leaned on.** `§2al.2` names the
propagation it caused — two frozen pre-registrations, a grader status string, and at least five
`RESULTS` records. **CORRECTION 3, written after the referral but before the amendment landed, was a
further propagation of it, and this correction is the lane's own repair of its own record.**

## C4.2 WHAT IS STRUCK ABOVE, AND WHAT SURVIVES UNTOUCHED

**Struck in place, byte-identical inside every `~~…~~`, never reworded or deleted — FIVE sites, all
markers or citations, none a measurement:** §4.1's pointer marker; C3.1's citation of the retired
line numbers; C3.1's block quotation of the old clause; C3.1's *"these are claims about the
harness"* sentence; and C3.4's *"the charter states the floor … with no derivation on its face"*,
which **was true when written and is no longer true**, because `§2al` restored the derivation into
the clause itself. **Lines whose number changed above this section: 0** — every strike is inline and
no line was added or removed.

**EVERY MEASUREMENT IN CORRECTION 3 STANDS UNCHANGED AND IS RE-AFFIRMED HERE.** Nothing measured
depended on the invented sentence: the aggregates 0.350109 % / 0.163445 %; the restricted
0.861604 % / 0.391451 %; `patchV[1]`'s 91.37 % / 90.87 % share and the 2.46× / 2.40× ratio; the
38,304-cell, 96-shape-DV match to the source study's A2 datum. **The amendment changes what the
charter says about such numbers. It changes none of the numbers.**

## C4.3 THE CAVEAT, RESTATED AGAINST `§2al` AS AMENDED

Following the form of `curriculum_D19O/PREREGISTRATION.md:188` — **its structure, not its wording,
because D19O's own sentence quotes the struck text and `§2al.2` names it as a propagation site.**

* **The harness floor.** `VERIFICATION_CHARTER.md` **`§2al` as amended (v1.56, `fc8d06e2`)**: the
  harness-sound floor **for THIS DATASET**, for a case with no flagged components, is **2.5-5 %
  vector-norm relative error**, on a **stated base of n = 2** — 2.5-3.0 % at 4,032 cells and
  **1.71 % at 38,304 cells / 96 DVs** — and qualified by the mesh, *"consistent with the floor
  tightening on finer meshes."* **Published beside every aggregate. Turning it into a gate would
  convert an honest caveat into a `GATE FAIL` the charter does not authorise.**
* **This item's figures against it:** F-S **0.350109 %**, F-P **0.163445 %**; restricted to the
  floor's own warp-chain instrument, **0.861604 %** and **0.391451 %**. This item runs at **38,304
  cells with 96 shape DVs** — **the mesh and DV count of the amended clause's own second data
  point.**
* **This record does not describe either figure as an anomaly, and does not describe it as a claim
  about the harness.** Under `§2al` as amended, a sub-floor number on a fine mesh is what the
  establishing study predicts.

**WHAT THIS IS, FINALLY.** A **consistency-of-disclosure** repair, and only that: `curriculum_D19M`,
`curriculum_D19O`, `curriculum_D8` and `curriculum_SO3` all carry a sub-floor disclosure on the
artefact's face and this record carried none. **It is not a warning about a `PASS`.** The `PASS` is
untouched, and was never in question.

**Nothing in this item or this record is filed, sent, emailed, uploaded, posted or commented outside
this box, now or ever** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

---

# CORRECTION 5 — 2026-09-04. The `disarm` clearance is re-verified against the **armed ancestor's own log**, and the control this family had been quoting as decisive is **SATURATED AT THAT LOG'S PRINT PRECISION**

**Written by the dafoam-supervisor personally**, 2026-09-04. **NO COMPUTE WAS SPENT**: no instrument
run, no run root written, no container invoked, no artefact produced. **NO VERDICT MOVES** —
`ITEM_two_row_endpoint_fd` remains `PASS`, `G5`'s registered band remains 5 %, and no gate,
threshold, cap, band or label is touched.

**What changed above this section: nothing. Lines whose number changed above this section: 0.**

**Why it is here and not in a findings file.** `LAB_STATE` `S-43`/`S-47` recorded this as owed at
`FINDINGS_disarm_clearance_and_harness_floor.md`. **That file cannot be written by any agent in this
fleet** — the harness refuses findings-file writes, and it refused the supervisor exactly as it had
refused the lane. **The lane declined to route around its own restriction and so does the
supervisor**; the substance therefore lands in this item's own record, in the numbered-CORRECTION
form CORRECTIONS 2-4 already use, which is this family's sanctioned home for it and is not a
workaround.

## C5.1 ⚠ THE CLEARANCE, READ FROM THE ARMED ANCESTOR RATHER THAN FROM THE INSTRUMENT

CORRECTION 2 established what the disarm *is* by reading `d4s_f3s_fd_endpoint.py` and DAFoam's
`checkPrimalFailure()`. **This section establishes the same thing by reading a log written before any
of that code existed** — an independent line of evidence, and the stronger one, because it cannot be
circular with the instrument under examination.

**One named file, never a glob** (`grep` on this box is a shell function over ugrep, which emits
per-file as parallel workers finish, so a multi-file reduction has no defined last member):
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/F3_20260826T205120Z_411184.log`,
**1,151 lines**, the **armed** ancestor — its own header carries `primalMinResTolDiff 1000` at
**`:501`**.

| what | line | reading |
|---|---|---|
| solver reaches `endTime` | **`:864`** | `End` |
| failure block opens | **`:866`** | the banner |
| residual and tolerance | **`:867-868`** | `Primal min residual 1.115891818e-05` / `did not satisfy the prescribed tolerance 1e-08` |
| the declaration | **`:869`** | `Primal solution failed!` |

**`primalMinResTolDiff` IS NOT A RESIDUAL STOP.** `End` is at 864; the whole failure block is at
866-869. **It fires after the solver has already run to `endTime`, so it cannot stop, shorten or
perturb a solve.** It is a post-hoc acceptance test, and the only thing it can change is whether a
completed primal is *labelled* failed.

**The log states the decisive arithmetic itself.** Failure is declared iff
`primalMaxRes / primalMinResTol > primalMinResTolDiff`, and from the log's own two printed numbers:

```
1.115891818e-05 / 1e-08 = 1115.891818   vs the armed bar 1000
```

**The SHIPPED endpoint exceeds the armed bar by 1.116× — it fails by 12 %, not by orders of
magnitude.** Under the disarmed bar of `1e12` the same ratio cannot fire. [MEASURED, the named log
at `:501`, `:864`, `:866-869`; arithmetic on the two printed values.]

*Correction to the lab board, recorded rather than silently fixed: `LAB_STATE` `S-43` §5 gave the
failure declaration as "868-869". The block opens at **866**. Narrow by two lines; the load-bearing
claim — `864 < 866` — is untouched.*

## C5.2 ⚠ AND THE CONTROL THIS FAMILY CALLED DECISIVE IS A BOUND, NOT A BIT-IDENTITY

`S-43` §5 offered, as **the decisive control**: *"the armed run's final `CD` is `0.02112851374`
against the disarmed `0.021128513742774115` — identical to eleven digits."*

**Eleven decimal places is the entire printed precision of the armed side.** The named log prints
`CD: 0.02112851374 final: 0.02112851374` at `:827`, `:843` and `:859`, and has **no twelfth digit**.

> **The comparison is SATURATED: it cannot distinguish true identity from agreement to within
> ~5e-12, because the armed number has no digit left in which to disagree.**

It remains a real and sufficient control — the disarm plainly did not move the answer — **but it is a
bound, and it had been travelling as a bit-identity.** This is the same disease this family has been
correcting all week: **a label that overstates its own predicate**, the reader taking the NAME for
the MEASUREMENT.

**The genuinely bit-level evidence exists, is already in this document, and is stronger — quote it
instead.** C2.5: prediction `P3`, registered **before compute** as the test of whether the disarm
changed the answer where the old threshold was already satisfied, scored **`HIT`**, `worst_rel_diff`
**`0.0`** across all five components at a `1e-12` relative tolerance. **Part of this correction's
purpose is to redirect the quotation.**

*Open provenance gap, disclosed rather than papered over: the long-form `0.021128513742774115`
appears in **no repository document except the lab board** and in no artefact located so far; the
short form is cited at `curriculum_D4_SHIPPED/PREREGISTRATION.md:627` and printed in the named log.
**A number on the board with no artefact behind it is exactly what this family refuses from everybody
else.** If no source is found, the sentence is struck, not kept.*

## C5.3 WHAT IS AND IS NOT ESTABLISHED

| # | claim | status |
|---|---|---|
| 1 | `primalMinResTolDiff` fires **after** `End` and cannot stop, shorten or perturb a solve | **MEASURED** — named log `:864` vs `:866-869` |
| 2 | It is a ratio bar; the armed ancestor exceeded it by **1.116×** | **MEASURED** — `:501`, `:867-868` |
| 3 | The disarm did not move the answer where the old threshold was already satisfied | **MEASURED** — C2.5, `P3` `HIT`, `worst_rel_diff 0.0` at `1e-12`, registered before compute |
| 4 | The armed-vs-disarmed `CD` agreement is a **bound at ~5e-12**, not a bit-identity | **MEASURED**, and it **corrects** how this family had been quoting it |
| 5 | The long-form disarmed `CD` has an artefact behind it | **UNMEASURED** — no source located |
| 6 | The disarm is safe **in general**, on any other case or instrument | **NOT ESTABLISHED AND NOT CLAIMED** — C2.6 clears one relaxation under six named conditions, on two rows of one item |

**Row 6 is stated because a clearance is the easiest kind of record to over-read.**

**Nothing here is filed, sent, uploaded, posted or commented outside this box** (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

---

# CORRECTION 6 — 2026-09-04. CORRECTION 5's disclosed provenance gap is **CLOSED BY CITATION, NOT BY STRIKING**: the long-form `CD` has six artefacts. It was missed because it is stored as a JSON **STRING**, and a numeric search is blind to it

**Written by the dafoam-supervisor personally**, 2026-09-04, in the same session as CORRECTION 5. **NO COMPUTE.** **NO VERDICT MOVES.** **Lines whose number changed above this section: 0.**

## C6.1 STRUCK BY QUOTE FROM C5.2 — NOT REWRITTEN

> ~~*Open provenance gap … the long-form `0.021128513742774115` appears in **no repository document except the lab board** and in no artefact located so far … **If no source is found, the sentence is struck, not kept.**~~*

**A source WAS found — six of them — so the sentence is KEPT, and it is now cited.** The undertaking in C5.2 was to strike on absence; the honest discharge of that undertaking is to record the presence with equal prominence.

## C6.2 THE ARTEFACTS, AND THE KEY

The value is the **`CD_baseline` of the `F-S` (SHIPPED, disarmed) arm** — which is exactly the disarmed counterpart the armed-vs-disarmed comparison requires, not some other run's number:

| artefact | key |
|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin/F-S/d4s_f3s_fd_endpoint.json` | `"CD_baseline": "0.021128513742774115"` |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin/F-S/d4s_f3s_accept.jsonl` line 1 | `"CD": "0.021128513742774115"` |

and the same pair in `CURRICULUM-D4S-F3S-a2-wing-cdmin/F-S/`, plus each run root's `d4s_f3s_fd_endpoint.jsonl` — **six files.** [MEASURED: 1 occurrence in the named `.json`, 1 line in the named `.jsonl`.]

## C6.3 ⚠ WHY THE FIRST SEARCH MISSED IT, AND IT IS THE SAME DISEASE THIS RECORD IS ABOUT

**The value is stored as a JSON STRING, not as a number.** A reader that walks the parsed object comparing floats returns **zero matches on a file that contains the value** — I ran exactly that reader and it reported `exact matches: 0` while a byte search on the same named file returned 1.

> **A numeric search for a number stored as text is a reader that cannot see, and its output is `absent` — indistinguishable from the number genuinely not being there.**

**That is the ninth instance of this family in this item's records and the first inside my own triage.** The lesson generalises past JSON: **before reporting an absence, show the reader able to find the thing in a case where it IS present** — rule 3's principle applied to a search rather than to a comparator.

## C6.4 AND C5.2's READING IS CONFIRMED AND NOW QUANTIFIED

With both numbers in hand the saturation claim stops being an argument and becomes arithmetic:

```
armed, as printed   0.02112851374            (11 decimals -- the log's full precision)
disarmed, full      0.021128513742774115
absolute difference 2.7741142716e-12
relative difference 1.3129718e-10
half-width of the armed value's last printed digit   5e-12
```

**The difference sits INSIDE the armed side's own rounding interval** — `2.774e-12 < 5e-12` — so the armed print is exactly what the disarmed value rounds to at 11 decimals. **The two are consistent with being the same number, and the armed side cannot resolve it further.** C5.2's conclusion stands unchanged and is now stated with its numbers: **a bound at ~5e-12, not a bit-identity.**

**The bit-level claim remains C2.5's** — `P3` `HIT`, `worst_rel_diff = 0.0` at `1e-12` relative, registered before compute. **Quote that one.**

**Nothing here is filed, sent, uploaded, posted or commented outside this box** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**
