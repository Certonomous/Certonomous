# D4-DEF-4 REPAIR — PRE-REGISTRATION OF THE ACCEPTANCE TEST AND THE ARM-F RE-RUN

**Written 2026-08-25 by the D4-DEF-4 repair lane. Committed BEFORE any container starts.**

**Nothing here is sent, filed, uploaded, registered, posted or commented outside this box**
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **`D4-DEF-4` is a defect in THIS LAB'S OWN
INSTRUMENT, not in DAFoam, OpenMDAO, IPOPT or pyOptSparse — no upstream report arises and none
is drafted.**

**Authority:** `SUPERVISOR_D4DEF4_REPAIR_RULING.md` (commit `dbb88eb4`), which permits the
repair under `VERIFICATION_CHARTER.md` §2d.1 and binds it with three limits. This document is
LIMIT 1 discharged: **the repair is not frozen until one primal proves it, and the comparison
band is fixed before that primal runs.**

**This document alters NO gate, threshold, band, cap or label in `PREREGISTRATION.md`.** Bands
A, B, C, D and E stand exactly as frozen. Every band below is NEW and belongs to a NEW test.

---

## 1. Legality of this registration — the condition, and how it was checked

`CLAUDE.md` rule 2: before first compute, a registration is legal when it names the condition
and states how it was checked.

**The condition: the run roots for both arms registered here DO NOT EXIST at this commit.**

Checked at **2026-08-25T21:47Z** with a predicate that names the thing sought and whose output
cannot be truncated into a false negative — `test -e <path>`, not a listing and **not a pager**
(the generalisation of L-325 the supervisor paid for today: `head`, `tail` and every truncating
filter are enumeration instruments when their output is read for presence or absence, and they
fail silently in the "absent" direction).

| path | `test -e` |
|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/ACC` | **ABSENT** |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/F2` | **ABSENT** |

No compute has been spent against either arm. Every gate, band, cap and label below is
therefore fixed before the answer can exist.

---

## 2. THE HYPOTHESIS, AND THE THING THAT WOULD FALSIFY IT

**Hypothesis H:** `OptView.hst` holds DRIVER-SCALED design-variable values, so the optimum's
PHYSICAL design point is each extracted family divided by its registered OpenMDAO `scaler`.

**H predicts a number that already exists and cannot be changed by anything this lane does:** a
primal at that physical point returns arm O's IPOPT objective

> **`CD_OPT = 2.1125978108239574e-02`** — `O/opt_IPOPT.txt`, arm O, `EXIT: Optimal Solution Found.`

**If H is false, the primal returns something else.** The alternative is not subtle: a wrong
scaling of `patchV` is a freestream of 10 m/s instead of 100 m/s, and `CD` at a tenth of the
design speed is not within a thousandth of the optimum's. **The test can fail, and if it does,
H is refuted.**

---

## 3. THE GATE AND THE BANDS — frozen here, never touched again

Let `CD_acc` be the acceptance primal's drag coefficient, read **from a file** written by rank 0
with `fsync`, never from stdout (MPI log splicing is MEASURED on this exact case —
`per_component_table/RESULTS.md` §2.2, commit `79679a84`).

| id | quantity | band | status |
|---|---|---|---|
| **ACC-1** | `rel_CD = \|CD_acc − CD_OPT\| / CD_OPT` | **≤ 1.0e-3** | **THE GATE** |
| ACC-2 | the same `rel_CD` | ≤ 1.0e-6 | **REPORTED, GATES NOTHING** |
| ACC-CL | `rel_CL = \|CL_acc − CL_OPT\| / \|CL_OPT\|`, `CL_OPT = 0.49999992625227224` | ≤ 1.0e-3 | **REPORTED, GATES NOTHING** |

**Why 1.0e-3 and not something tighter or looser, stated before the answer exists.** The band
has one job: separate *"this is the optimum"* from *"this is not the optimum"*. The error H
attributes to D4-DEF-4 is a factor of **ten** on three design-variable families; any residual
mis-scaling would move `CD` by percent, not by parts in a thousand. Against that, the band must
absorb the only two innocent sources of difference between arm O's final function evaluation and
this one: the primal restarts from a different initial field (arm O's stored `0/U`, not a
converged endpoint field), and `DARhoSimpleFoam` is converged to `primalMinResTol = 1.0e-8` with
`primalMinResTolDiff = 1e3` rather than to machine precision. **1.0e-3 is four orders looser than
the solver's own residual floor and one to two orders tighter than any mis-scaling could
produce.** ACC-2 at 1.0e-6 is carried as a *reported* corroboration channel precisely so that a
much closer agreement can be stated without the gate having been set to demand it.

**ACC-2 and ACC-CL can never turn a PASS into a GATE FAIL or the reverse.** They are reported
beside the verdict, never instead of it.

---

## 4. THE VERDICT MAPPING — the fixed vocabulary, and the consequence of each

`CLAUDE.md` rule 1. **No synonyms, no hedging prose.**

| outcome | verdict | consequence |
|---|---|---|
| `rel_CD ≤ 1.0e-3` | **`PASS`** | H is proved by an instrument that grades nothing. **The repair is frozen and arm F re-runs.** |
| `rel_CD > 1.0e-3` | **`GATE FAIL`** | **THE DIAGNOSIS IS WRONG.** The repair is **WITHDRAWN**, D4 stays **`BLOCKED`**, and a second finding is recorded. |
| the primal crashes, or any control refuses | **`NOT A RESULT`** | The repair is **not frozen**. D4 stays **`BLOCKED`**. |

**Registered here so it cannot be reconsidered later: on `GATE FAIL` the band is NOT widened and
the correction is NOT adjusted until it fits.** `VERIFICATION_CHARTER.md` §2d.1's contrast is the
whole point of the clause — *the numbers looked wrong, so the band was widened* is never
permitted. **Nothing a verdict depends on may be repaired on the authority of the verdict it
produces.** A withdrawn diagnosis reported clearly is worth more than a repaired one reported
hopefully.

---

## 5. INSTRUMENTS — by md5, committed with this document

**LIMIT 2: zero bytes of any frozen file are edited.** The repair takes the `d8_grade_entry.py`
shape this family has already validated: a wrapper that **invokes the committed blob** and
corrects **downstream** of it.

### 5a. Frozen, NOT edited, re-asserted before every launch

| file | md5 | role |
|---|---|---|
| `d4_opt_runScript.py` | `2906d52a5dbed2bacbaeaf85a37d3fe8` | the producer; **the only admissible source of the scalers** |
| `d4_extract_endpoint.py` | `ee7d3c99fd716da23779cb651961918e` | invoked as a module, unmodified |
| `d4_fd_endpoint.py` | `c6112b0ec3bfdb5287345e350500f64a` | arm F's FD producer, unmodified |
| `d4_run_arm.sh` | `399957c616215c8f1ae078abe2e97958` | the frozen launcher — **not edited and not invoked here** |
| `d4_grade.py` | `f162ef69a7385e5d0586ef5f27657cbb` | the frozen grader — **never invoked directly** (D4-DEF-3 unrepaired) |

### 5b. NEW instruments registered by this document

| file | md5 | role |
|---|---|---|
| `d4_endpoint_locus.py` | `e63df1845771c3e67457443918f5b82e` | the scaler parser and the **two new controls**; also gate **G13** |
| `d4_endpoint_physical.py` | `74c35c80bb4d395cf8939d851bc6b3f9` | the repair wrapper — invokes the frozen extractor, corrects downstream |
| `d4_accept_primal.py` | `c339d3a8da39f3186b69481df222a215` | ONE primal at the corrected point |
| `d4_accept_compare.py` | `680a8280cd28f8239e0f42711022ab7b` | the acceptance comparator, with its planted-zero control |
| `d4_repair_instruments.md5` | `735c4bceaf288ded175e133fb20c2b8d` | the registry the launcher checks with `md5sum -c` |
| `d4_stage_ACC.sh` | `d1d19fa17ce2b31360acb17c090df8f5` | ACC tree staging |
| `d4_run_acc.sh` | `df31e39af072b09650b3d2b37a569633` | ACC launcher |

**THE SCALERS ARE READ FROM `d4_opt_runScript.py`, NEVER TYPED INTO THE REPAIR.** A typed
constant can drift from the registration and would reintroduce D4-DEF-4 somewhere new.
`d4_endpoint_locus.parse_registration()` parses the producer with `ast`, takes `lower`, `upper`
and `scaler` from its `add_design_var` calls and `U0` from its own module-level assignment, and
**REFUSES if it cannot find all three keywords for every registered design variable** or if
fewer than three design variables are registered.

---

## 6. THE CONTROLS — every one shown able to FIRE, none merely asserted

| id | control | shown able to fire by |
|---|---|---|
| **CONTROL P** | **the pinned witness.** Every component whose registered `lower` EQUALS its `upper` is definitional — no optimiser can move it. The control **DISCOVERS** them by scanning the registration and **REFUSES IF IT FINDS NONE** (a control with nothing to check is not a control, L-302). | selftest mutants: pinned off by 1e-9 relative → REFUSED; pinned left driver-scaled at 10.0 → REFUSED; a registration with zero pinned components → REFUSED |
| **CONTROL B** | **bounds containment** on every component. IPOPT does not violate bound constraints, so a component outside its registered bounds is a units or indexing error, not an optimum. | selftest mutants: `shape` 1e-6 above its upper bound → REFUSED; `twist` below its lower bound → REFUSED; an empty component set → REFUSED |
| **G-ACC-PLANT** | the **planted-zero control** (`CLAUDE.md` rule 3) on the acceptance comparator: `PLANT = 1.234e-03` into `CD` **on disk**, re-read **through the same reader**; the graded quantity must move by the exact predicted amount **and cross OUT of band ACC-1**. A **blind reader** that ignores its path must be **REFUSED**. | built into `d4_accept_compare.py`; it refuses and grades nothing if the reader cannot see the plant |
| **count refusal** | the artifact must carry the registered counts — 7 `twist`, 96 `shape`, 2 `patchV` — **refused BY COUNT, WITH THE COUNT PRINTED** | `d4_accept_compare.grade()` |
| **age guard** | `d4_endpoint_physical.py --age-datum <epoch>` refuses any extractor output not **strictly newer** than the ACC copy epoch (`CLAUDE.md` rule 4) | the datum is written by `d4_stage_ACC.sh` at copy time and is **strictly later** than arm O's carried-over datum, which would pass every arm-O artifact in the tree |
| **target cross-check** | `CD_OPT` typed in the comparator must equal `_final_CD` carried by the run's own artifact, else **REFUSE** — a typo in the comparator cannot pass silently | `d4_accept_compare.main()` |
| **double-deformation guard** | `d4_stage_ACC.sh` asserts the source tree's `constant/polyMesh/points.gz` md5 equals `base/`'s, so the IDWarp/DVGeo reference geometry is the UNDEFORMED mesh | measured: `0fb1935a9b8781b73ac4ccb136e3ec68` in `base/`, `O/` and `F/` alike, mtime 2026-07-28 |

**`d4_endpoint_locus.py --selftest` result at this commit: `D4_LOCUS_SELFTEST 22/22 PASS`**, and
**both controls fire on the ACTUAL D4-DEF-4 vector** — the raw driver-scaled extraction refuses
CONTROL P with `rel_residual = 0.9` on `patchV[0]` and refuses CONTROL B with 63 violations.

---

## 7. THE RUN — arm ACC

| item | value |
|---|---|
| tree | `ACC/`, staged `cp -a O ACC` by `d4_stage_ACC.sh`. **`F/` IS NOT TOUCHED** — condition (4) preservation |
| image | `dafoam-idwarp-rot:v1`, digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` — the registered **PATCHED** row, asserted by digest, never by tag |
| ranks | 4, `--bind-to core`, decomposition `scotch` (inherited from the case's `decomposeParDict`, unchanged) |
| cpuset | measured idle at launch and RECORDED in `acc_ledger.txt`; placement measured per rank, never inferred from the quota flag |
| memory | `--memory=8g`. Arm O's container peaked at **5.962 GiB over its first 600 s** (setup + first primals; `O_mem.jsonl`) and only reached 10.32 GiB once the adjoint and colouring were live. This arm computes **no gradient**. |
| **memory headroom guard** | the launcher **REFUSES (exit 5)** unless `MemAvailable − 8 GiB ≥ 12 GiB`. Two peer lanes are live and a run that would push the box under the floor does not get to decide that for itself. |
| ledger | **`acc_ledger.txt`, NOT `ledger.txt`** — MEASURED reason: `d4_grade_SUPPLEMENT.py:630` refuses G10 with `unregistered_arm_in_ledger` on any arm outside `{P1,P2,O,F}`. Writing an ACC row into `ledger.txt` would MOVE A GATE, and **LIMIT 3 says no gate moves.** |

### 7a. COST — predicted, with a numeric stop threshold (`CLAUDE.md` rule 12)

`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED` — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Dollars DERIVED, not measured.**

| arm | **predicted core-min** | **cap (stop threshold)** | basis |
|---|---|---|---|
| **ACC** | **20.0** | **80.0** | arm P2 (cold setup + one primal + one adjoint + colouring) measured **36.4 core-min**; this arm drops the adjoint and the colouring and keeps the cold setup and one primal. 20.0 is that arm scaled down, not a guess with no anchor. |
| **F2** (arm F re-run, conditional on ACC `PASS`) | **53.0** | **120.0** | the arm-F cap and prediction **as already frozen in `PREREGISTRATION.md` §8 and §7 — unchanged, not re-derived**. RESULTS.md §10.8 states that prediction "was sound and remains the right estimate for the arm when it can be run". |

**The overrun rule: an overrun STOPS THE RUN; it does not get a new budget.** The cap is enforced
as a wall timeout derived from the core-minute cap by arithmetic the launcher then inverts and
re-checks, so no second number can drift from the first.

**A named disagreement with my supervisor, on the record.** The brief estimates the acceptance
primal at **~0.9 core-min**. **I believe that is low by more than an order of magnitude** and I
am registering **20.0**. 0.9 core-min is 13.5 wall seconds at 4 ranks — that is the duration of
arm F's *crash*, which died during setup before one primal converged. A cold DAFoam setup on this
case (imports, `decomposePar`, `prob.setup`, the `mphys.html` N² write) plus one converged
`DARhoSimpleFoam` primal cannot complete in that. If the arm lands near 0.9 I will have been
wrong and the calibration row will say so; registering the number I actually believe is what
makes the row worth anything.

### 7b. Reserved launcher exit codes

`4` staging/identity abort · `5` cold-start, headroom or precondition abort · `64` usage ·
`65` cap-arithmetic abort. **A payload failure is `rc = 1` or `2` and is never one of these.**

---

## 8. THE ARM-F RE-RUN — registered here, CONDITIONAL, and moving nothing

**Arm F re-runs if and only if ACC-1 returns `PASS`.**

* It runs in a **third tree, `F2/`**, staged `cp -a O F2`. **`F/` is never touched.**
* Its chain is `d4_endpoint_physical.py --age-datum <epoch>` then the **FROZEN, UNEDITED**
  `d4_fd_endpoint.py` at np=4.
* **It is graded on the ORIGINAL frozen bands** — C, D and E of `PREREGISTRATION.md` §4,
  unchanged — **through `d4_grade_SUPPLEMENT.py`, never by invoking the frozen `d4_grade.py`
  directly**, because that file carries **D4-DEF-3** unrepaired: with `rows` absent its G7
  mutators index `d["rows"][:2]` and raise an uncaught `KeyError` — `rc=1`, a traceback, **no
  verdict file written at all**, on the gate whose purpose is refusing malformed input *by name*.
* **NEW GATE G13 — the endpoint locus.** `d4_endpoint_locus.py --gate <workdir>` re-reads the
  published `d4_endpoint_dvs_PHYSICAL.json` **from disk** at grading time and re-asserts CONTROL
  P and CONTROL B. **G13 can only refuse.** It cannot turn a `GATE FAIL` into a `PASS`, and a
  refusal makes the arm **`NOT A RESULT`**, never a softer word.

**A departure from the brief, disclosed rather than quietly taken.** The brief says to put the
two new controls "in the supplement". **I put them in a new sibling instrument instead, and G13
is invoked beside the supplement rather than inside it.** The reason: `d4_grade_SUPPLEMENT.py`
has *already graded arm F* and its verdict `d4_grade_ARMF_20260825T212030Z.json` is cited in
`RESULTS.md` §10.5. Editing it would make a cited verdict non-reproducible from the file that
produced it, which is the failure rule 6 exists to prevent, one level down from a frozen file.
The supervisor's intent — *not in the frozen grader* — is honoured strictly; the placement is
one step further out. **If the supervisor disagrees, the fix is one import and the controls do
not change.**

---

## 9. WHAT THIS TEST DOES NOT ESTABLISH — named plainly

1. **It does not validate D4's 28.6758 % drag reduction.** That needs the FD table, and the FD
   table needs arm F. Until then D4's optimum is **`BLOCKED`, not validated.**
2. **It does not establish band A of G2 or score P3.** `D4-DEF-5` stands: `d4_major_history.json`
   holds **125 function calls, not the 80 majors**, including the `findFeasibleDesign` AoA sweep
   that runs before `run_driver()`. Graded over that file G2 band A returns **`GATE FAIL` on 37
   of 125 rows and that `GATE FAIL` would be WRONG**. **Band A stays NOT ESTABLISHED and P3 stays
   UNSCORED.** Band B is bought and stands at `|CL − 0.5| = 7.3747727758e-08`.
3. **It does not make D4 toolchain-independent.** The **SHIPPED** row
   (`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`) **IS NOT BOUGHT and
   is `PENDING`** — not run, not failed. **D5, D6 and D14 inherit that qualifier.** D4-DEF-4 is an
   instrument defect and would occur identically on the shipped row, so nothing here narrows the
   gap the unbought row leaves.
4. **A single primal is not a repeatability measurement.** No `eta` is measured by this arm; the
   run-to-run noise floor at this design point is **NOT MEASURED** and is not claimed.
5. **The acceptance primal restarts from arm O's stored field**, not from a uniform initial
   condition. For a steady solve converged to `1.0e-8` the converged answer does not depend on the
   initial guess, but this is stated rather than assumed, and band ACC-1 is sized to absorb it.

---

## 10. FREEZE

This document and the seven new instruments of §5b are committed **before any container starts**.
**No gate, threshold, band, cap or label above may change after the first compute**; a departure
lands only as a dated addendum at the foot, which cannot alter a gate, threshold, cap or label,
and the original is struck, never rewritten (`CLAUDE.md` rules 2 and 6).

**`PREREGISTRATION.md` is not modified by this document in any way.**

---

## ADDENDUM 1 — 2026-08-25T21:58Z — the arm-F re-run's two launcher scripts, registered by md5

**This addendum alters NO gate, threshold, band, cap or label** (`CLAUDE.md` rule 2). It
registers the identity of two scripts and nothing else. The originals above are **struck
nowhere and rewritten nowhere**; every band of §3, every verdict mapping of §4 and both cost
rows of §7a stand exactly as committed at `5ed02071`.

**Why an addendum and not an edit.** Arm ACC has now run, so first compute has happened and §10's
freeze is in force. Arm F2 was already registered in §8 — its tree, its chain, its cap of **120.0
core-min carried over unchanged from `PREREGISTRATION.md` §8**, its bands (C, D and E, unchanged),
its grader and its new gate G13. What §5b did not carry is the **md5 of the two scripts that
stage and launch it**, because they did not exist when §5b was written. They are registered here.

| file | md5 | role |
|---|---|---|
| `d4_stage_F2.sh` | `cc4128b2acda649cf31fcbf98bdeadae` | stages `F2/` from `O/`; **`F/` is never opened for writing** |
| `d4_run_F2.sh` | `3c3b825f38abd78ec627c698d2f075f0` | the arm-F re-run launcher |

**Both are derived from the ACC pair registered in §5b and carry every one of its assertions**:
the internal cap table with the assertion that inverts its own arithmetic, image identity by
digest, md5 assertions on `d4_opt_runScript.py`, `d4_extract_endpoint.py` **and
`d4_fd_endpoint.py` (`c6112b0ec3bfdb5287345e350500f64a`)**, the `md5sum -c` registry check, the
cold-answer-file guard, the memory-headroom guard, `--no-rm` so the kernel's exit verdict
survives, the passive cgroup sampler, and the undeformed-reference-mesh assertion.

**`d4_run_F2.sh` writes its ledger row to `f2_ledger.txt`, NOT `ledger.txt`** — same measured
reason as ACC: `d4_grade_SUPPLEMENT.py:630` refuses G10 with `unregistered_arm_in_ledger` on any
arm outside `{P1,P2,O,F}`, so an F2 row in `ledger.txt` would **move a gate**. **LIMIT 3 holds.**

### The condition under which arm F2 is authorised to run at all

**ACC-1 returned `PASS`** at 2026-08-25T21:53Z — `CD = 0.021130918911049287` against
`CD_OPT = 2.1125978108239574e-02`, **`rel_CD = 2.3387e-04`** inside the **1.0e-3** band frozen at
`5ed02071` before the primal ran. Verdict artifact:
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/ACC/d4_accept_verdict.json`.
**The D4-DEF-4 repair is FROZEN and §8's condition is met.**
