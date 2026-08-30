# Curriculum item D6R — the A2 wing multipoint optimisation chain, re-run at a repaired cap frame: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-30 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** D6R never landed one: its own frozen comparator **refused**, and a refusal
wrote no verdict JSON and no record — so the verdict that stands for this item has until today lived
only in a successor's file and in a preserved run root outside git. A reader who came to this
directory looking for D6R's verdict found the chain's logs and nothing that told them what the item
concluded.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no artefact was written, no preserved run root was touched, and **zero solver
> core-minutes were spent.** Every verdict, gate reading, band, count, refusal string and cost figure
> below is **copied from an existing artefact and cited to it by path and by JSON key, ledger field
> or line.** Where a figure a reader might want is **not** on record, this document says so and says
> where a reader would have to go — it does not supply one. **The three places where this record
> states arithmetic rather than a copied figure are each labelled as such at the point of use**
> (§2's dollar total, §3's per-major cutback comparison, and nothing else). A results record that
> quietly derives a fresh figure is a second grading of the same item wearing a scribe's clothes.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings
> (`## 1. SPEND` … `## 6. WAITING LIST`) are **the morning report's**, matched literally so that a
> document carrying them *is* a morning report; a curriculum record wearing `## 5. REFILLED QUEUE`
> would be a malformed one. This record follows the family's own convention for a curriculum item —
> `curriculum_AV1R/RESULTS.md`, `curriculum_AV2R/RESULTS.md`, `curriculum_SO1a/RESULTS.md`,
> `curriculum_D6RG/RESULTS.md`.

---

# 1. Item verdict — `NOT A RESULT`, and TWO INSTRUMENTS REACHED IT DIFFERENTLY

**The word is the same from both instruments. The objects behind it are not, and the difference is
the whole point of this record.**

| | |
|---|---|
| **BY THIS ITEM'S OWN FROZEN GRADER**, driven unmodified | **`NOT A RESULT`** by **comparator refusal**, with **ZERO of eleven gate readings**, **exit code 2**, and **no verdict JSON written at all** |
| **BY THE SUCCESSOR `D6RG`**, one reader repaired under a fingerprint audit | **`NOT A RESULT`**, **composed from ELEVEN gate readings**, an optimiser classification, eight scored predictions and a cost census |

**Verdict of record: `NOT A RESULT`.** Source:
`cases/dafoam/ladder-a/A2/curriculum_D6RG/D6RG_regrade.json` and
`cases/dafoam/ladder-a/A2/curriculum_D6RG/RESULTS.md` §1.

**A `NOT A RESULT` that stays `NOT A RESULT` is a result and is reported as one.** The verdict did not
improve, and that is the correct outcome — the successor was built to make the item *readable*, not
to make it pass. What changed is that an item with no readings at all now has eleven.

## 1.1 THE REFUSAL, QUOTED — this item refused first, and a reader is entitled to see on what

**D6R's own frozen `d6r_grade.py` was DRIVEN, not predicted.** Before a line of successor code was
written it was run **unmodified**, on a `cp -a` copy of the preserved run root. Verbatim from
`curriculum_D6RG/RESULTS.md` §1a:

    D6R_GRADE REFUSED {"REFUSE": "G-D6R-OPT", "detail": {"n_exit": 1, "n_obj": 0,
                       "no_final_objective_or_exit": "<copy>/O_mp/opt_IPOPT.txt"}}

| | |
|---|---|
| exit code | **2** |
| verdict JSON written | **none**, at the `--out` path or beside the grader |
| gate readings printed | **zero of eleven** |
| `grader_controls/` created in the copy | **none** — the frozen planted-zero control never fired (see §6) |
| preserved root after the drive | md5 manifest of **14,546** files **identical** |

**The `EXIT:` line IS present and only the summary `Objective` line is missing**, so the refusal fires
on one limb of a two-limb test. That refinement matters and is not cosmetic: **the log is not
truncated, it is unreadable by this reader.** The distinction is the entire content of
`D6R-GRADER-DEF-2` in §4b.

## 1.2 THE VERDICT OF RECORD, AND WHAT PRODUCED IT — a SUCCESSOR, and no frozen file here was edited

| | |
|---|---|
| successor item | **`D6RG`** — `cases/dafoam/ladder-a/A2/curriculum_D6RG/` |
| its pre-registration freeze | **`5563f78533391e8ec5842db915ff70ebd7663685`**, committed **before** the comparator was executed |
| names rebound | **`["read_ipopt"]`** — exactly the registered set, fingerprint-audited |
| D6R's frozen comparator | `d6r_grade.py`, md5 **`bc8e9fec48b3f58ce7a96f4b9549590b`** — verified disk == `git cat-file blob HEAD:<path>` by the comparator itself, at execution |
| D6R's frozen pre-registration | `PREREGISTRATION.md`, md5 **`e525084daac50c82738170925894fbe1`** — same check, same direction |

**Every band, threshold, cap, label, composition rule, prediction and refusal clause that decided this
verdict is D6R's own frozen code, unedited on disk.** The successor imports it, proves the file
byte-identical to the committed blob, rebinds exactly one name under an audit that refuses on any
other, and runs the frozen `grade()`. Source: `curriculum_D6RG/RESULTS.md` §1 and §6.

> **L-370 false-drift trap, restated here because it lives in THIS file's siblings.** The grader md5
> pinned in this item's own `PREREGISTRATION.md` at **§7:414** and **§8:478** is
> `aa93ba1f6cc1dedad8d8c7efc7f2afeb` — the **pre-amendment** value. The post-Amendment-1 value is
> `bc8e9fec48b3f58ce7a96f4b9549590b`, which is what `D6R_chain_wait.json` carries as
> `grader_md5_post_amendment` and what is on disk. **A rule-2 check that stops at §7 reports a false
> `GATE FAIL` on a file that never drifted.**

# 2. THE ARMS — what ran, what never ran, and what it cost

Copied from `/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/ledger.txt` (per-arm
`ARM=` rows) and `STATUS.chain`. **This lane read those two files and wrote neither.**

| arm | rc | wall s | ranks | core-min | cap core-min | in-container deadline s | outcome |
|---|---|---|---|---|---|---|---|
| **`O_mp`** | **0** | **33,869** | 4 | **2,257.933** | **2,900.0** | 43,410 | ran to the optimiser's own exit |
| **`ACC_mp`** | **124** | **363** | 4 | **24.200** | **30.0** | **360** | **killed by `timeout` at its own in-container deadline** |
| **`F_mp`** | — | — | — | — | 300.0 | 4,410 | **NEVER RAN** |
| **`REF_off`** | — | — | — | — | 40.0 | 510 | **NEVER RAN** |
| **total** | | | | **2,282.133** | ceiling **3,270.0** | | |

`STATUS.chain` closes verbatim:
`chain=STOPPED_AT_FIRST_NONZERO arm=ACC_mp rc=124 order=[O_mp ACC_mp F_mp REF_off] not_run=[F_mp REF_off]`.
**The chain stopped at the first non-zero rc, which is the registered behaviour and not a fault of
the chain driver.** `F_mp` and `REF_off` are named `NOT_RUN` with reason
`REGISTERED_CHAIN_STOPPED_AT_FIRST_NONZERO` in the frozen census, stop arm `ACC_mp`, stop rc 124
(`curriculum_D6RG/RESULTS.md` §2).

**`ACC_mp` was not OOM-killed and did not overrun its cap.** The ledger's own
`inspect(exit,oomkilled)=[124 false]` records the kill as the deadline, not memory, and 24.200 of
30.0 core-min is inside the cap. **It ran out of clock, not out of budget** — and §4a establishes
that the clock it was given could never have been enough.

**Total spend graded: 2,282.133 core-min** against a registered item ceiling of **3,270.0**
(`curriculum_D6RG/RESULTS.md` §2, `D6RG_regrade.json` → `grade.G10`).

**Dollars: $1.951 DERIVED, NOT MEASURED**, `cost_basis` **REPORTED-BY-OWNER, NOT MEASURED** — the box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Stated plainly: this dollar figure is
THIS RECORD'S ARITHMETIC** on the on-record 2,282.133 core-min at the recorded c7a.4xlarge rate of
$0.0513/core-h (`CLAUDE.md` rule 12), **not a figure copied from any artefact.** Rule 12 requires
dollars to be derived at the recorded rate and labelled derived; that is what this is, and it is the
only monetary figure in this record.

# 3. THE PHYSICS — `rc = 0` MEANS THE PROCESS FINISHED, NOT THAT THE OPTIMISER STOPPED WHERE TOLD

**This section is the most valuable thing in the item, and it is the thing most easily lost inside the
bookkeeping above.** `O_mp` returned `rc = 0` and spent 2,257.933 core-min. A reader who stopped at
the ledger would conclude the arm behaved. It did not.

All figures from `curriculum_D6RG/D6RG_regrade.json` → `grade.G-D6R-OPT` unless another key is named.

| quantity | measured | key |
|---|---|---|
| exit line | **`EXIT: Invalid number in NLP function or derivative detected.`** | `exit_line` |
| majors completed | **73** | `n_major` |
| `max_iter` registered | **80** | `max_iter_registered` |
| restoration majors | **7** | `n_restoration_majors` |
| alpha cutbacks | **673** | `cutbacks` |
| cutbacks per major | **9.219178082191782** against a registered stall threshold of **1.0** | `cutbacks_per_major`, `stall_threshold_cutbacks_per_major` |
| dual infeasibility, tail start (major 66) | **9.23e-04** | `curriculum_D6RG/RESULTS.md` §3a |
| dual infeasibility, last (major 73) | **9.00e-04** — it **fell** | same |
| `deadline_fired` | **false** — container 33,794 s against a 43,410 s deadline | same |
| **optimiser outcome** | **`UNCLASSIFIED`** | `outcome` |

**The optimiser died on a non-finite value, seven majors short of its own registered cap.** It did not
converge, it did not hit `max_iter`, and it did not hit the container deadline. The frozen ladder is
`DEADLINE > STALLED > ITERATION_CAP > CONVERGED`, and `STALLED` requires **both** a cutback rate above
threshold (**S1 TRUE**) and a worsening dual infeasibility (**S2 FALSE** — it improved). The line
search was failing badly *while the dual infeasibility was still improving*, which is none of the four
registered outcomes. The frozen `compose()` maps `UNCLASSIFIED` to `NOT A RESULT` — **never `PASS`**.

## 3.1 THE SUCCESSOR BUILT TO FIX D6's CHAIN STOP REPRODUCED AND WORSENED D6's EVALUATION PATHOLOGY

**This is a reproducible finding about multipoint optimisation on the A2 wing under this toolchain,
and it is what the 2,257.933 core-min actually bought.**

| | D6 (predecessor) | D6R (this item) |
|---|---|---|
| alpha cutbacks | **548** | **673** |
| majors | **64** | **73** |
| restoration majors | **7** | **7** |
| dual infeasibility, tail | **WORSENING** 5.78e-04 (major 58) → 1.14e-03 (major 64) | **IMPROVING** 9.23e-04 (major 66) → 9.00e-04 (major 73) |

D6's four figures are quoted verbatim from the **registered prediction text** at
`D6RG_regrade.json` → `grade.predictions.P1.pred`, written **before** D6R ran. D6R's are from
`grade.G-D6R-OPT`.

> **Arithmetic, labelled as such.** Per-major, that is **9.2192** cutbacks for D6R (a figure the
> artefact prints) against **8.5625** for D6 (**548 ÷ 64 — THIS RECORD'S ARITHMETIC on two on-record
> integers, and NOT a figure any artefact prints**). The comparison is stated both ways so a reader
> can check it without trusting the division.

**The pathology is not merely reproduced, it is worse in the quantity that measures it.** More
cutbacks, a higher rate per major, the same seven restoration majors — and the run ended on a
non-finite NLP value rather than on any registered stopping condition. **D6R was built to repair D6's
chain stop. The chain stopped anyway**, one arm later and for a different reason (§2, §4a), **and the
evaluation pathology D6 exhibited came back intensified.**

**What this does NOT establish, stated so it is not read as more than it is:** nothing about **why**
the primal returns non-finite values at trial geometries. D6R's own `PREREGISTRATION.md` §6 declines
that question and prices it separately; neither D6R nor D6RG opened it. **The 673 cutbacks and 7
restoration majors are reported as what the log says, not as a diagnosis**
(`curriculum_D6RG/RESULTS.md` §8).

## 3.2 The recovered endpoint objective — reported, and it GATED NOTHING

The repaired reader recovered **`2.2238800e-02`** from major 73 of the iteration table, with
`provenance = ITERATION_TABLE_ROW` and **8 printed significant figures** — not the 17 the summary
line would have carried (`curriculum_D6RG/RESULTS.md` §4b). **`g_opt_outcome` consumes only `exit` and
`optimal` and never reads `objective`.** The value is **reported, not gated**, and is stated here
explicitly so that no later reader mistakes it for an input to this item's verdict.

# 4. THE TWO DEFECTS, NAMED

## 4a. `D6R-PREREG-DEF-1` — `ACC_mp`'s CAP PRICED A PROGRAM THE ARM DOES NOT RUN

**The arm could not have finished. Not on a slow day, not on an empty box, never.** Copied from
`cases/dafoam/ladder-a/A2/curriculum_D6RACC2/PREREGISTRATION.md` §1:

| | |
|---|---|
| what the registered program needed | **1,685.98 s = 112.40 core-min** |
| what it was given | **360 s deadline / 30.0 core-min cap** |
| **shortfall** | **4.68× the deadline, 3.75× the cap** |
| where it died | **53,124 of 98,959 cells still uncoloured at 335.62 s** — 46.3 % through the **FIRST of three** Jacobian colourings |

The registered `ACC_mp` program is `compute_totals` on a **cold staged copy at np = 4**, which must
colour the Jacobian three times, once per scenario. The 30.0 core-min cap traces to D6's
`3.0 × 3 (C-94)` anchor, and `C-94` is **a 45-second acceptance primal on an already-decomposed tree,
with no adjoint and no colouring**.

**AND THE PRE-REGISTRATION CITES NO CALIBRATION ROW AT ALL FOR THAT CELL — which is worse than citing
a wrong one.** Verified by this lane directly against the frozen file:

* `grep -c 'C-94' cases/dafoam/ladder-a/A2/curriculum_D6R/PREREGISTRATION.md` returns **0**. The
  anchor that actually set this cap is **named nowhere in the document that registered it.**
* The `ACC_mp` row's anchor cell, at **`PREREGISTRATION.md:270`**, reads in full:
  **`9.0 × 1.6308 (the same ×3 model, measured short by 63 %)`** — a **bare carried multiplier over an
  uncited base**. The `1.6308` correction is attributed (`C-188`, `C-182`, §4a of that file); **the
  `9.0` base is not attributed to anything.**
* **A wrong citation can be checked and refuted. An absent one cannot be checked at all** — there is
  no row for a reader to open and discover that it prices a different program. The exposure was
  disclosed in prose at `PREREGISTRATION.md:289` ("*the 1.6308× correction is applied to `ACC_mp`,
  `F_mp` and `REF_off` from the measurement of a different arm*"), **but the disclosure is about the
  multiplier, not about the base**, and the base is where the defect lives.

**AND THIS EXACT DEFECT HAD ALREADY BEEN FOUND, NAMED AND REPAIRED FOUR DAYS EARLIER.** `C-139`
(`docs/COST_CALIBRATION.md:215`) classifies D5's identical failure as **pre-registration
mis-anchoring**, in words that describe this arm verbatim. **D6R inherited the unrepaired anchor.**
That is `CLAUDE.md` rule 14's shape at the estimate level: *a lesson is not applied until every call
site asserts it*, and **a lesson recorded only in a ledger row has no call site at all.**

## 4b. `D6R-GRADER-DEF-2` — THE OPTIMISER READER HAS NO BRANCH FOR A NON-FINITE IPOPT EXIT

`d6r_grade.py:615-624`, the function `read_ipopt`, requires **BOTH** a summary
`Objective...............:` line **AND** an `EXIT:` line, and refuses at **`:620-621`** if either is
missing. **IPOPT dying on an `Eval_Error` substitutes the exception text for the summary block**, so a
run that ends on a non-finite value produces an `EXIT:` line and no summary line — and the reader
refuses on a log that is complete.

**THE READER WAS PROVED ABLE TO SEE A NON-ZERO, and that is what makes the zero evidence** (`CLAUDE.md`
rule 3's principle applied to a count rather than to a plant):

| log | summary `Objective` lines | `EXIT:` lines |
|---|---|---|
| **D6R** `O_mp/opt_IPOPT.txt` | **0** | **1** |
| **D4 control** `CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` | **1** | **1** |

The counts are on record at `docs/COST_CALIBRATION.md` row `C-214` and in
`curriculum_D6RG/RESULTS.md` §1a; **this lane confirmed both read-only against the two preserved logs
and neither was written.** D4's log has exactly one occurrence of the field D6R's log has none of, on
the same reader, so **the zero is a real absence and not a blind reader.**

**The grader is not defective in its gates.** `D6RG` repaired **one reader** and rebound **one name**;
no gate, band, threshold, cap, label or composition rule was touched, and the eleven readings in §1.2
are the frozen code's own.

# 5. `D6R-CAP-FRAME-2` — `G10` READS `GATE FAIL`, AND THE SUPERVISOR'S RULING ON IT

| arm | core-min | cap | within cap | host wall s | container wall s | frame gap s | gap ≤ 30 s |
|---|---|---|---|---|---|---|---|
| `O_mp` | 2,257.933 | 2,900.0 | **yes**, at **77.9 %** | 33,869 | 33,794 | **75** | **NO** |
| `ACC_mp` | 24.200 | 30.0 | yes | 363 | 363 | 0 | yes |

Source: `curriculum_D6RG/RESULTS.md` §3c; `D6RG_regrade.json` → `grade.gates.G10_caps`.

`G10`'s frame limb allows `FRAME_ALLOWANCE_S(90) − KILL_GRACE_S(60) = 30 s` between the host bracket
and the container's own kernel clock. **`O_mp` used 75 s while sitting comfortably inside its spend
cap.** The gate fails on **bookkeeping frame accounting, not on spend.** The recorded cause is stated
in the successor as a **hypothesis and not a finding**: `O_mp` wrote a **12.7 MB** arm log where
`ACC_mp` wrote 100 kB, and the 75 s sits in the host-side frame around a container that had already
stopped.

## 5.1 THE RULING — BOTH HALVES, AND NEITHER SOFTENS THE OTHER

**The allowance is NOT widened. `G10` reads `GATE FAIL` and it stands.** Widening a registered
threshold is **reserved to Sanaa** (`CLAUDE.md` FIRST-ACTION RULE; `ESCALATION_CHARTER.md`), and no
supervisor, lane or successor item may do it. A gate that is loosened because it fired is not a gate.

**And that `GATE FAIL` does NOT carry this item's verdict.** Sanaa's universal rule is that
**bookkeeping never voids physics**. The item verdict `NOT A RESULT` rests on the **physics
components** — a completion clause failed on an arm that ran, two registered arms never ran, and the
optimiser outcome is `UNCLASSIFIED` (§1.2, §3) — every one of which would stand if the frame limb had
passed. **Deleting `G10` from the composition changes nothing about the verdict.**

**Both halves are recorded because either alone would misrepresent the item.** Reporting only the
ruling would hide a live `GATE FAIL`; reporting only the `GATE FAIL` would let a frame-accounting
artefact appear to be the reason a 2,282-core-min optimisation campaign returned no result. **It is
not the reason.** `D6R-CAP-FRAME-2` is named, referred, and **not repaired here**; it is the successor
to `D6-CAP-FRAME-1` / L-371.

# 6. RULE 3 WAS **NOT EXERCISED** ON THIS DATA — recorded as not exercised, never as passed

**This item's frozen planted-zero control never fired, and nothing in the run reported that it
hadn't.** The frozen `g_price` **short-circuits when an arm did not run**, and `F_mp` did not run, so
the control was never reached. Confirmed by the **absence of any `grader_controls/` directory** in the
copy after the §1.1 drive of the unmodified frozen grader (`curriculum_D6RG/RESULTS.md` §1a, §4a).

**`NOT EXERCISED` is not `PASS`, and this record refuses to let it read as one.** A silent
short-circuit is the more dangerous shape precisely because nothing announces it: the grader produced
no control output and no complaint about producing none.

**Where rule 3 WAS driven, for a reader who needs it:** the successor drove the **frozen**
`planted_zero_control` **through the repaired reader** on D4's reference (unit U7) — the planted
**1.234e-03** was **seen** to within 1e-12 and the unperturbed negative control moved by **exactly
0.0**; and unit U8 measured, rather than assumed, that the frozen control binds its reader in
`__defaults__` at def time, so **D4's reference control still travels the ORIGINAL frozen code after
`read_ipopt` is rebound**. Both are `curriculum_D6RG`'s, on `curriculum_D6RG`'s data, and **neither is
a rule-3 reading on D6R's own graded arms.**

# 7. Cost — rule 12

**This item's solver spend: 2,282.133 core-min, $1.951 DERIVED** (§2, with the derivation labelled
there).

| | |
|---|---|
| registered total, all four arms (`PREREGISTRATION.md`, cost table) | **2,763.7 core-min**, ceiling **3,270.0** |
| registered dollars | estimate **$2.3630**, ceiling **$2.7958**, both DERIVED, NOT MEASURED |
| actual, two arms of four | **2,282.133 core-min** |
| `O_mp` against its own registered point | registered band **[1900, 2900]**, point **2,500.6**; observed **2,257.933** → prediction **`P5` HIT** (`curriculum_D6RG/RESULTS.md` §3b) |

**A whole-item actual-versus-predicted ratio is NOT stated here, and the omission is deliberate.** The
registered 2,763.7 prices **four** arms; the measured 2,282.133 bought **two**, one of which was
killed part-way through the first third of its program (§4a). **Dividing those two numbers would
produce a ratio that looks like a 17 % under-spend and actually describes a chain that stopped.**
That figure is not on record in any artefact, and this lane will not manufacture one.

**NO CALIBRATION ROW EXISTS FOR D6R'S OWN CHAIN SPEND, and one is owed.** `docs/COST_CALIBRATION.md`
carries `C-188` for the predecessor **D6** and `C-214` for the successor **D6RG** — the re-grade's
instrument time, 0.320 core-min, a different object entirely. **There is no row for the 2,282.133
core-min this item actually burned.** `PREREGISTRATION.md:298` records that a calibration row is owed
at completion. **Writing it is not a scribe's call**, it is the supervisor's, and rule 11 requires its
id to be re-derived from the tail as the maximum existing number **in the committing invocation**.
**It is flagged, not filled.**

**`ACC_mp`'s own estimate-versus-actual is superseded rather than calibrated**, because §4a
establishes the estimate priced the wrong program. The correctly anchored figures belong to the
successor `D6RACC2`: registered estimate **112.40 core-min**, cap **240.00 core-min**, in-container
deadline **3,510 s** (`curriculum_D6RACC2/PREREGISTRATION.md` §2, §7).

# 8. WHAT THIS ITEM DID **NOT** BUY

**It did not buy a gradient verdict.** `G-D6R-1` (three cruise-lift clauses), `G-D6R-2` (composite),
`G-D6R-3` (price) and `G-D6R-4` (FD) all read **`NOT A RESULT`**, and predictions **P2, P3, P4 and
P6** are `NOT A RESULT` ×4 because **their inputs were never produced** — `F_mp`, the arm that runs
the FD primals, never ran (`curriculum_D6RG/RESULTS.md` §2, §3b).

**It did not buy the chain completion it was built for.** Prediction **`P8`** was registered as *the
repair's own falsifier* — *"the chain COMPLETES — all four arms run"* — and it **MISSED**. The
predicted mechanism worked (`O_mp` did exit `rc = 0`, which is what D6 failed to do) **and the
predicted outcome did not** (`curriculum_D6RG/RESULTS.md` §3b). **A falsifier that fires is the
registration working, not the item failing to be honest.**

**It did not buy an optimiser classification in the registered set.** `P1` registered
`{ITERATION_CAP, STALLED}` with point `STALLED`; observed `UNCLASSIFIED` — **`MISS` on point and on
band.**

**It did not establish anything about the physics of the non-finite primal** (§3), **about `ACC_mp`,
`F_mp` or `REF_off` beyond the frozen census**, or **about any new gate, threshold, band, cap or
label** — all are D6R's own.

**What it DID buy, plainly:** a reproducible, instrumented statement of the evaluation pathology of
this multipoint problem on this toolchain (§3.1), two named pre-registration and grader defects each
with a successor already registered (§4), and 2,257.933 core-min of `O_mp` compute that produced **no
reading at all** until the successor made it readable.

# 9. WHERE THE FULL READINGS LIVE — this record is a signpost, not a duplicate

A record that restates every number drifts from its source the first time the source is corrected.
The authorities, in order of precedence:

1. **`cases/dafoam/ladder-a/A2/curriculum_D6RG/D6RG_regrade.json`** — the verdict of record, the
   eleven gate readings, `grade.G-D6R-OPT` in full, `grade.G1`, `grade.G10`, the arm census, the
   frozen `not_a_result_reasons`, and all eight scored predictions.
2. **`cases/dafoam/ladder-a/A2/curriculum_D6RG/RESULTS.md`** — §1 and §1a the two instruments, §2 the
   eleven readings, §3a–§3c the three carried-forward findings, §4 and §4a the birth requirement and
   the rule-3 status, §5 the root manifests, §6 the hash table, §7 the re-grade cost.
3. **`cases/dafoam/ladder-a/A2/curriculum_D6RG/d6rg_selftest_evidence.txt`** — 27/27 units under
   `python3` and `python3 -O`, ten of them must-FLAG plants driven on the real frozen `grade()` over
   the real preserved artefacts.
4. **`cases/dafoam/ladder-a/A2/curriculum_D6R/PREREGISTRATION.md`** (this directory, frozen) — this
   item's own gates, bands, caps, the cost table at :266–:272, the `ACC_mp` anchor at **:270**, and
   the exposure disclosure at :289.
5. **`cases/dafoam/ladder-a/A2/curriculum_D6RACC2/PREREGISTRATION.md`** — `D6R-PREREG-DEF-1` in full,
   with both independent cost anchors.
6. **`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/`** (14,546 files, outside git)
   — `ledger.txt`, `STATUS.chain`, `O_mp/opt_IPOPT.txt`, the per-arm logs, the memory windows and the
   age datums.

**If any figure in this record disagrees with the JSON or the ledger, the JSON and the ledger are
right.**

# 10. Successors

| item | what it does | status |
|---|---|---|
| **`D6RG`** | Grades the **preserved artefacts** through one repaired reader — `read_ipopt` — rebound in D6R's own frozen comparator under a fingerprint audit. Produced the verdict of record in §1. | **LANDED.** Pre-registration frozen `5563f78533391e8ec5842db915ff70ebd7663685`; calibration row `C-214`. |
| **`D6RACC2`** | Re-runs **only the cheap arm**, `ACC_mp`, at a cap derived from **two independent measurements of the program the arm actually runs** — repairing `D6R-PREREG-DEF-1`. | **Pre-registration FROZEN before compute** at commit `4e4adf66`, 2026-08-30T23:24:10Z. Registered estimate 112.40 core-min, cap 240.00. **Queued** — stated on the supervisor's record; **this lane did not open `verification/queue/`** and does not certify the queue state. |

**`D6R-CAP-FRAME-2` has no successor item and needs a ruling, not a re-run** (§5.1). **The missing
calibration row for D6R's own chain spend has no successor either** (§7).

# 11. What this record does and does not do

**It does** give D6R an item-level record where it had none, so that a reader who comes to this
directory finds the item's verdict instead of a chain of logs and a silence. **The verdict lived only
in `curriculum_D6RG/RESULTS.md` §1 and in a run root outside git**, which is the exact pattern already
closed for `AV1R`, `AV2R` and `SO1a` at commit `6f0dcdac`.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, score any
prediction, run any comparator, touch any preserved run root, or add any number that was not already
written down in a cited artefact — with the two arithmetic exceptions labelled at their point of use
(§2's dollar total, §3.1's per-major comparison).

**It does not** revise what this item's own frozen instrument produced. On D6R's own frozen path
`read_ipopt` refuses, and §1.1 stands as the record of that refusal. The eleven readings in §1.2 are
the verdict on the **preserved artefacts**, reached by a successor running D6R's own unedited
`grade()`.

**It does not** widen, soften or re-register the `G10` frame allowance (§5.1), and it does not fill
the calibration row it flags as owed (§7).

**It establishes nothing about the physics, the mesh or the solver beyond what §3 copies from the
optimiser's own log.** No solver ran for this record; **zero solver core-minutes** were spent writing
it.

# 12. Artefacts, all still on disk

In `cases/dafoam/ladder-a/A2/curriculum_D6R/`: `PREREGISTRATION.md`, `d6r_grade.py`,
`d6r_grade_selftest.py`, `d6r_grade_selftest_evidence.txt`, `d6r_chain_driver.sh`, `d6r_run_arm.sh`,
`d6r_opt_runScript.py`, `d6r_ref_off.py`, `d6r_extract_endpoint.py`, `d6r_fd_endpoint.py`,
`d4_extract_endpoint.py`, `d6r_aggregate_memory.py`, `d6r_groot5_selftest.sh`,
`d6r_groot5_selftest_evidence.txt`, the four `*_DELTAS_from_d6.diff` files, `STATUS.D6R_chain_wait`,
`WRAPPER.D6R_chain_wait.log`, `LAUNCH.D6R_chain_wait.*.out`, `QUEUE_ENTRY_DRAFT_D6R_chain_wait.json`,
`launcher.queue.out`, and this file.

Preserved run root, outside git and never written by this lane:
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/` (**14,546** files), carrying
`ledger.txt`, `STATUS.chain`, `O_mp/opt_IPOPT.txt`, the per-arm containerised logs, the per-arm
`inspect` records and the memory windows.

Reference root, read-only:
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/` (**5,085** files) — the D4 control log
that proves the reader of §4b can see a non-zero.

> **Disclosed, not hidden.** `curriculum_D6RG/D6RG_regrade.json` embeds **transient scratchpad paths**
> as keys under `reader_audit`, from the successor's own working directory. That directory no longer
> exists, and `CLAUDE.md` rule 13 says a repository document never cites a scratch path. It is a
> machine record of a transient copy rather than a handoff pointer, and this lane has **left it as
> executed** — editing an instrument's own output after the fact would be a worse defect than the one
> it discloses. **No path in this prose document is a scratch path.**
