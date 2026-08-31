# D6RG — PRE-REGISTRATION (FROZEN). Successor re-grade of D6R through ONE repaired reader

**Item:** `D6RG` — successor re-grade of **D6R** from its **preserved run root**, through
D6R's own frozen comparator with **exactly one** name rebound.
**Team:** dafoam. **Date:** 2026-08-30.
**Solver compute: ZERO.** Nothing meshed, nothing solved, no container, no GPU.
**Predecessor:** `cases/dafoam/ladder-a/A2/curriculum_D6R/` — run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint`, `CHAIN_DONE` written
2026-08-29T02:00:26Z, chain outcome `STOPPED_AT_FIRST_NONZERO` at `ACC_mp`.

---

## 1. THE DEFECT, ONE SENTENCE

**`d6r_grade.py:615-624` `read_ipopt()` has no branch for a non-finite IPOPT exit.** It
requires **BOTH** an `Objective...............:` summary line **AND** an `EXIT:` line, and
refuses at `:620-621` if either is missing. When IPOPT dies on `Eval_Error` it prints the
exception text **where the summary block would have gone**, so a log that is otherwise
complete cannot be read at all.

**Measured with a control, never inferred.** D6R's `O_mp/opt_IPOPT.txt` has **zero** matches
of `^Objective\.+:` and **one** `EXIT:` line; D4's
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` has **exactly one
of each** (`EXIT: Optimal Solution Found.`, 80 iterations). The reader is demonstrably able to
see a non-zero, so the absence is real (rule 3).

**The frozen grader was DRIVEN, not traced.** Unmodified, against a `cp -a` copy of the
preserved root, 2026-08-30:

| | |
|---|---|
| exit code | **2** |
| stdout | `D6R_GRADE REFUSED {"REFUSE": "G-D6R-OPT", "detail": {"n_exit": 1, "n_obj": 0, "no_final_objective_or_exit": ".../O_mp/opt_IPOPT.txt"}}` |
| verdict JSON written | **none** |
| gate readings printed | **zero of eleven** |
| preserved root after | md5 manifest of **14,546** files **identical** |

This is `D6R-GRADER-DEF-2`. It is a **second, different** defect: `D6-GRADER-DEF-1` (the arm
census) **is genuinely repaired** in `d6r_grade.py` and does not recur — the census correctly
names `F_mp` and `REF_off` `NOT_RUN` under `REGISTERED_CHAIN_STOPPED_AT_FIRST_NONZERO`.

## 2. WHY A SUCCESSOR AND NOT A RE-RUN OF `O_mp`

`O_mp` **spent 2,257.933 core-min** and its artefacts are **intact**: no file under the run
root carries an mtime later than 2026-08-29T02:01:00Z, and the box went down 12 h 40 m later,
so nothing was torn. Re-running `O_mp` would spend ≈ 2,500 core-min to reproduce the **same
numerical failure** — buying the same answer twice. The preserved artefacts are read instead.

## 3. HOW IT RE-GRADES — IT RE-IMPLEMENTS NO GATE

D6RG imports **D6R's own frozen comparator**, verifies the file on disk is byte-identical to
the **committed blob**, rebinds **exactly one name**, and runs the **frozen `grade()`**. Every
band, threshold, cap, label, composition rule, prediction and refusal clause that decides a
verdict is **literally the frozen code, unedited on disk**.

| frozen file | registered md5 | checked against |
|---|---|---|
| `cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_grade.py` | **`bc8e9fec48b3f58ce7a96f4b9549590b`** | disk **and** `git cat-file blob HEAD:<path>` |
| `cases/dafoam/ladder-a/A2/curriculum_D6R/PREREGISTRATION.md` | **`e525084daac50c82738170925894fbe1`** | disk **and** `git cat-file blob HEAD:<path>` |

`bc8e9fec…` is the value **after D6R's AMENDMENT 1**, the one `D6R_chain_wait.json` carries as
`grader_md5_post_amendment`. **L-370 false-drift trap:** the pins at D6R's
`PREREGISTRATION.md` §7:414 and §8:478 are **pre-amendment**; a check that stops there reports
a false `GATE FAIL`.

**REGISTERED REBIND SET, and it is audited rather than asserted:** exactly
**`("read_ipopt",)`**. The comparator fingerprints every callable in the imported module
before and after and **REFUSES** (`REBIND_AUDIT`) if the rebound set is not exactly that.

**Refusals are raised through the FROZEN module's own `refuse()`**, so the successor never
invents a refusal vocabulary.

## 4. THE ONE REPAIR, AND WHAT IT MAY NOT DO

The repaired `read_ipopt` **delegates to the frozen function verbatim** whenever the summary
line is present, so the must-NOT-flag direction is **structural, not a promise**. The repair
branch is reachable **only** when the summary `Objective` line is absent, and then:

* **IT MUST NOT INVENT AN OBJECTIVE.** The final objective is **recovered from the iteration
  table that is in the file** — major 73's row, `2.2238800e-02`.
* **PROVENANCE IS RECORDED AS A DIFFERENT CLAIM.** Every recovered reading carries
  `objective_provenance = "ITERATION_TABLE_ROW"`, `summary_line_present = false`, the row's
  major number and the **printed significant figures**. The iteration table prints **8**
  significant figures; the summary line prints **17**. *This is the table's number at the
  table's precision and is not the summary's number.*
* **THE TWO OBJECTIVE COLUMNS ARE EQUATED ONLY ON A SETTING READ FROM THE FILE.** The table
  has **one** objective column; the summary has **two** (scaled, unscaled) and the frozen
  reader returns the **unscaled** one. They may be equated only when the log's own
  `nlp_scaling_method` is `none` — **read from the log**, and **refused on otherwise**.
  Both D6R's and D4's logs state `none` at line 13.
* **THE RECOVERED NUMBER DECIDES NOTHING.** `g_opt_outcome` consumes only `exit` and
  `optimal`; it never reads `objective`. The recovered value is **reported, not gated** —
  which is stated here so no later reader mistakes it for an input to a verdict.

**Seven registered refusal gates stand between an unreadable log and a recovered number**, all
raised through the frozen `refuse()`: `no_exit_line`, `exit_not_registered`,
`nlp_scaling_method`, `number_of_iterations_absent`, `no_iteration_table`,
`iteration_table_torn`, `iteration_table_not_contiguous`, `recovered_objective_not_finite`.
The **registered non-finite exit set is exactly one string**:
`EXIT: Invalid number in NLP function or derivative detected.` Widening it is a registration
change, not a reader change.

## 5. PRESERVED ROOTS ARE NEVER WRITTEN — AND IT IS ASSERTED, WITH THE METHOD NAMED

Every regrade runs on a **`cp -a` copy**. An **md5 manifest of every regular file** in **both**
preserved roots — `CURRICULUM-D6R-a2-wing-multipoint` (14,546 files, ≈ 1.07 GB) and
`CURRICULUM-D4-a2-wing-cdmin/O` (5,085 files, ≈ 384 MB) — is taken before and after the whole
execution and the run **REFUSES** (`PRESERVED_ROOT_MUTATED`, naming the moved paths) if a
single hash moves. **It reads the DISK, not git** — a run root is not in git, so a git-based
cleanliness check is blind to exactly the thing being protected.

**Registered honestly:** the manifest is taken **once before and once after the whole
execution**, not around each plant. Taking it around each of eleven regrades would read
≈ 16 GB to prove the same property. Between plants the **single file under test** is restored
from a pristine byte copy and its **md5 re-verified against the preserved original**, so every
plant starts from the real file.

## 6. BIRTH REQUIREMENT — BOTH DIRECTIONS, ON THE REAL FROZEN GRADER

A repaired reader's entire risk is that it **launders a genuine absence into a reading**, so
the **MUST-FLAG direction is the point, not decoration.** Every plant travels the **real**
preserved artefacts and the **real** frozen `grade()` — none is driven in a mock.

| # | direction | plant | required outcome |
|---|---|---|---|
| U4 | **must-NOT-flag** | none — D4's real complete log | read by the **ORIGINAL** summary-line path, `provenance = SUMMARY_LINE`, every consumed key equal to the frozen reader's own return |
| U5 | **must-NOT-flag** | none — D6R's real log | recovers `2.2238800e-02` from major 73, `provenance = ITERATION_TABLE_ROW`, 8 printed figures |
| U9 | **must-FLAG** | every major row removed, tail intact | REFUSE `repair_declined_no_iteration_table` |
| U10 | **must-FLAG** | file truncated after major 40, whole tail gone | REFUSE `repair_declined_no_exit_line` |
| U11 | **must-FLAG** | majors 68–73 deleted, tail still reports 73 | REFUSE `repair_declined_iteration_table_torn` |
| U12 | **must-FLAG** | last objective rewritten to `nan` | REFUSE — see the clause note below |
| U13 | **must-FLAG** | last objective rewritten to `1e999` (floats to `inf`) | REFUSE `repair_declined_recovered_objective_not_finite` |
| U14 | **must-FLAG** | `nlp_scaling_method` flipped `none` → `gradient-based` | REFUSE `repair_declined_nlp_scaling_method` |
| U15 | **must-FLAG** | `EXIT:` replaced with an unregistered non-optimal exit | REFUSE `repair_declined_exit_not_registered` |
| U16 | **must-FLAG** | `EXIT:` surgically deleted, table intact | REFUSE `repair_declined_no_exit_line` |
| U17 | **must-FLAG** | `Number of Iterations` deleted | REFUSE `repair_declined_number_of_iterations_absent` |
| U18 | **must-FLAG** | hole punched at majors 30–35, both ends intact | REFUSE `repair_declined_iteration_table_not_contiguous` |

**REGISTERED CLAUSE NOTE FOR U12, BEFORE IT IS RUN.** The frozen `MAJOR_ROW_RE` objective
class is `[-+0-9.eE]+` and **cannot express `nan`**. A `nan` objective therefore makes the row
stop matching, and the refusal lands on the **torn-table** clause, **not** on the non-finite
one. The requirement — *refuse, never coerce* — holds either way; the clause is **named in
advance, not claimed after the fact**. `1e999` (U13) is expressible in that same class and
floats to `inf`, so it is **U13, not U12, that proves there is no silent coercion.**

**Rule 3 is driven here.** The frozen `g_price` short-circuits when `F_mp` did not run, so the
frozen grader **never drove its own planted-zero control on D6R's data**. D6RG therefore drives
the frozen `planted_zero_control` **through the repaired reader** on D4's reference: the
planted `1.234e-03` must be **seen** and the unperturbed negative control must **not move**.

**Registered and measured, not assumed:** the frozen `planted_zero_control` binds its reader in
`__defaults__` at def time, so **D4's reference control still travels the ORIGINAL frozen code
after `read_ipopt` is rebound.**

## 7. WHAT THIS RE-GRADE MAY NOT CONCLUDE

* **Nothing about WHY the primal returns non-finite values at trial geometries.** D6R's §6
  declines that and prices it separately. **This item does not open it.**
* **Nothing about the `ACC_mp`, `F_mp` or `REF_off` arms beyond what the frozen census already
  records.** `ACC_mp` ran and hit its deadline (`rc = 124`); `F_mp` and `REF_off` never ran.
* **No new gate, threshold, band, cap or label.** All are D6R's own.
* **Nothing about the physics, the mesh or the solver.** No solver ran.
* **A `NOT A RESULT` that stays `NOT A RESULT` is a result and is reported as one.**

## 8. THREE FINDINGS CARRIED FORWARD — REGISTERED BEFORE EXECUTION, REPORTED WHATEVER THE VERDICT

1. **`G-D6R-OPT` classifies `O_mp` `UNCLASSIFIED`, not `STALLED`.** S1 is TRUE (673 alpha
   cutbacks over 73 majors = 9.2192/major against a registered 1.0) but **S2 is FALSE**: dual
   infeasibility **fell** from 9.23e-04 at major 66 to 9.00e-04 at major 73. The registered
   ladder needs both. **Prediction P1's registered set `{ITERATION_CAP, STALLED}` therefore
   scores MISS on point AND band.**
2. **P8 — "the chain COMPLETES, all four arms run" — is a clean MISS.**
3. **`G10` `GATE FAIL` on `O_mp`'s frame gap:** host 33,869 s − container 33,794 s = **75 s**
   against a registered allowance of `FRAME_ALLOWANCE_S(90) − KILL_GRACE_S(60) = 30 s`. The arm
   was **inside its cap** (2,257.933 of 2,900.0 core-min). **`D6R-CAP-FRAME-2`: the 30 s frame
   allowance is under-registered for a 12.7 MB log.** This is a **third candidate defect**,
   reported and **not repaired here** — it needs its own registration.

**None of the three is softened.** A gate that fails is reported failing.

## 9. THE SUCCESSOR'S OWN INSTRUMENTS, FROZEN BY MD5 WITH THIS DOCUMENT

| file | md5 |
|---|---|
| `cases/dafoam/ladder-a/A2/curriculum_D6RG/d6rg_grade.py` | **`14356162837faece73acf40b323927c9`** |
| `cases/dafoam/ladder-a/A2/curriculum_D6RG/d6rg_reader.py` | **`61bb9dbe1adab6e9b2cdb3a13f53cff1`** |

The grading path is fixed at this commit. **Frozen unit count `EXPECTED_UNITS = 27`**; the
selftest must pass under `python3` **and** `python3 -O` with `__pycache__` cleared before each.
**Zero `assert` statements** in either file, AST-counted before anything runs, with the counter
shown able to see a planted one — so `-O` cannot strip a check. Producers are imported with
`sys.dont_write_bytecode = True`, set **before any local import**, so importing a frozen case's
comparator cannot drop a `__pycache__` into its directory.

**Honest disclosure (the `curriculum_D18R_P7` §4 / `curriculum_AVWC` §8 form):** the instrument
was exercised during development, so this is **not an outcome-blind freeze and does not claim to
be**. What the freeze buys is the **repair semantics**, the **registered non-finite exit set**,
the **seven refusal gates**, the **rebind audit**, the **unit count**, the **both-directions
controls**, the **U12 clause note** and the **three carried-forward findings** — all fixed and
committed before the recorded execution.

## 10. RULE-2 CONDITION — the run directory that does not exist

Checked at this freeze, 2026-08-30:

* `ls -d /home/ubuntu/certonomous-runs/*D6RG*` → **0 entries**.
* `ls -d /home/ubuntu/Certonomous/verification/runs/*D6RG*` → **0 entries**.
* `cases/dafoam/ladder-a/A2/curriculum_D6RG/` contains **only** `d6rg_reader.py`,
  `d6rg_grade.py` and this document. No `D6RG_regrade.json`, no `RESULTS.md`, no evidence file
  exists yet.

**No such run directory will ever exist**: this item registers **no solver arm**. Its output is
a re-grade JSON and an evidence file beside this document, and the gates close the moment the
comparator is first executed against the preserved roots.

**DISCLOSED, because it bears on "the frozen file IS the file that ran":** at this freeze the
**shared git index carries 489 staged deletions** across every team, including
`curriculum_D6R/d6r_grade.py` and `curriculum_D6R/PREREGISTRATION.md`. **Every one of those
files is present on disk and present in `HEAD`** — the deletion is staged only. It is
**inspected and NOT reverted** (rule 10: the index is the chief's call). D6RG is unaffected
because it commits by the private-index protocol, which `read-tree`s from `HEAD` and never
touches the shared index; and its rule-2 check hashes the disk against
`git cat-file blob HEAD:<path>`, which reads the **commit**, not the index.

## 11. COST (rule 12; `COMPUTE_BUDGET_CHARTER.md` §5)

**Solver compute: ZERO core-minutes.** No mesh, no solve, no container, no GPU. No queue entry
is disturbed and no running solver is touched.

| | |
|---|---|
| Registered estimate | **1.50 core-min**, ranks = 1 throughout (one `cp -a` of a 1.07 GB root, four md5 manifests totalling ≈ 3 GB, eleven frozen `grade()` calls, 27 units) |
| Cap | **5.00 core-min.** An overrun **stops the item**; it does not get a new budget |
| Rate | **$0.0513 / core-h**, c7a.4xlarge, owner-stated 2026-08-21/22 |
| Dollars, estimate | **$0.001283 DERIVED, NOT MEASURED** |
| Dollars at cap | **$0.004275 DERIVED, NOT MEASURED** |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Disk | ≈ 1.1 GB transient in the session scratchpad, deleted on completion. **No record here cites a scratch path** (L-186) |

A calibration row is owed in `docs/COST_CALIBRATION.md`, with ids **re-derived at commit time
in the same shell invocation** (rule 11).

## 12. WHAT LANDS, AND WHAT DOES NOT

**Lands:** `RESULTS.md` here, `D6RG_regrade.json`, `d6rg_selftest_evidence.txt`, and one
`docs/COST_CALIBRATION.md` row.

**Does not land from this item:** any edit to D6R's frozen files (rule 6); any repair of
`D6R-CAP-FRAME-2`, which is reported and left to its own registration; any statement about the
non-finite primal evaluations. **Nothing is sent, filed, uploaded, registered, posted or
commented outside this box** (rule 7) — "filed in the queue" means the local
`verification/queue/` directory and nothing else.

---

## ADDENDUM A-1 — 2026-08-31: §7's FIRST BULLET PRESUPPOSES A CAUSE THE GRADING RECORD DOES NOT SUPPORT

**Dated 2026-08-31. APPENDED ONLY. POST-COMPUTE — THE GATES OF §3 ARE CLOSED AND NONE OF THEM MOVES.** Lane: dafoam `lab-lane`, on the `dafoam-supervisor`'s ruling.
**NOT FILED ANYWHERE.** Nothing in this addendum is filed, sent, uploaded, registered, posted or commented outside this box (`CLAUDE.md` rule 7). **SUBMISSIONS PARKED.**

**⚠ THIS ADDENDUM MOVES NO GATE, NO THRESHOLD, NO BAND, NO CAP, NO LABEL AND NO VERDICT** — the only thing `VERIFICATION_CHARTER.md` §2b permits a post-compute addendum to do, and the only thing this one does. This document's freeze at **`5563f78533391e8ec5842db915ff70ebd7663685`** stands; every registered gate, cap, label, md5 and cost line above stands exactly as frozen; the item's verdict stands exactly as graded. **This addendum is disclosure only: it qualifies a causal presupposition in one prose bullet of §7 and registers nothing.**

**VERSION CONVENTION — read from this document rather than invented.** This file carries **no numeric version field**; there is no `Version n.n` line above. The family's convention for it is **dated, appended, sequentially-lettered sections** (`curriculum_D6R/PREREGISTRATION.md:526` `AMENDMENT 1 — 2026-08-28`; `curriculum_SO3aR/PREREGISTRATION.md:265` `ADDENDUM A-1`). **This section conforms as `ADDENDUM A-1`, dated, and invents no version number for a document that has none.** It is styled an ADDENDUM, not an AMENDMENT, because compute has happened and §2b permits only addenda thereafter.

**lines whose number changed above this section: 0** — proved mechanically. The pre-edit bytes were copied aside before anything was appended (**16,290 bytes, 252 lines**); afterwards the post-edit file's leading **16,290** bytes were compared byte-for-byte against that copy (`cmp -n 16290`, exit 0). **A live planted control ran in the same invocation** (`CLAUDE.md` rule 3): a second copy carried **one byte altered on line 157 — a NON-BLANK line, and the exact line this addendum qualifies** (`N` → `O` at column 4) — and the reader had to **see** it before the empty diff was accepted as evidence. A plant on a blank line returns a false "identical"; that is why this one is on the load-bearing line.

### 1. THE SENTENCE, STRUCK, NOT REWRITTEN

§7's first bullet stands, struck, and remains legible:

> ~~"**Nothing about WHY the primal returns non-finite values at trial geometries.** D6R's §6 declines that and prices it separately. **This item does not open it.**"~~ (`:157–158`)

The clause is a disclaimer that **asserts while declining**: it treats *"the primal returns non-finite values"* as settled and withholds only the explanation. **The record settles that evaluations failed. It does not settle that they failed by returning non-finite values.**

### 2. WHAT THE RECORD SUPPORTS INSTEAD

**D6R's recorded cause is `BOOKKEEPING`; no gradient was ever measured.** From this item's own graded output, `D6RG_regrade.json`: `grade/G-D6R-1..4` all `verdict = NOT A RESULT`, `reason = ARM_DID_NOT_RUN`; `grade/G1/arms_not_run` lists **`F_mp` (the FD referee) and `REF_off`** as `NOT_RUN`, `reason = REGISTERED_CHAIN_STOPPED_AT_FIRST_NONZERO`, `stop_arm = ACC_mp`, `stop_rc = 124`. D6R's own frozen grader refused on a record defect — `n_exit = 1`, **`n_obj = 0`**, `no_final_objective_or_exit` in `O_mp/opt_IPOPT.txt`. §7's second bullet already records, correctly and unchanged, that **`F_mp` and `REF_off` never ran**; this addendum only draws the consequence the first bullet stepped past.

**The IPOPT message is disjunctive.** `IpOrigIpoptNLP.cpp:487` guards on `success && IsFiniteNumber(ret)`, throwing on a **false status OR** a **non-finite value** and printing `EXIT: Invalid number in NLP function or derivative detected.` either way (`cases/dafoam/ladder-a/A2/curriculum_SO3D/PREREGISTRATION.md:74`). The measured exception text (`:47`) is itself that disjunction and names no limb.

**Corroboration for the failed-status limb, from the grading record:** `grade/G-D6R-OPT` carries **`S1_line_search_failing: true`**, **`S2_dual_infeasibility_not_decreasing: false`**; **671 `Primal solution failed!` banners against 673 cutbacks**; objective **finite at `0.0222388`** immediately before the final cutback (`curriculum_SO3D/PREREGISTRATION.md:50`, `:53`, `:78`, `:79`).

### 3. WHAT IS NOT CLAIMED

**No non-finite census has been computed** (`curriculum_SO3D/PREREGISTRATION.md:64`, in terms). The only search on record is an **ungated pre-freeze search for the literal token `nan`** returning 0 over the `CD:`/`CL:` prints (`:80`); **that is not a census of non-finite values**, and generalising it would repeat the over-statement withdrawn in `docs/dafoam/GRADING_CHAIN.md`. The census is **SO3D's registered `P1` / gate `G-SO3D-1`, still uncomputed** (`:108`, `:124`), planted control **`PLANT-A`** waiting (`:145`). **The non-finite-value limb is neither established nor excluded**, and the class does not rest on it.

**Governing record:** `docs/dafoam/GRADING_CHAIN.md`, cause-class row **D6R** and the appended **CORRECTION, 2026-08-31**.
