# Curriculum D6RF — `F_mp` and `REF_off`, the only unrun arms in the D6 lineage, bought once, at caps derived from measured anchors, behind a repair the lineage has needed since D4 and never applied

**Item id:** `D6RF` (dafoam curriculum; the two arms `D6R` registered and never bought).
**Team:** dafoam. **Date:** 2026-09-03. **Version 1.0 — FROZEN by the commit that introduces this file.**
**Committed BEFORE any container starts** (`CLAUDE.md` rule 2).
Permission for detached launches: **`bc0e687e`** (Sanaa's words, boarded verbatim).
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7; `DAFOAM_CHARTER.md` §10).
**No frozen file is edited** (rule 6).
**This item has burned 0 core-min, started no container, and IS NOT ENQUEUED.**

> **ID-NAMESPACE WARNING.** `docs/DOCKET.md` carries fleet-defect rows numbered D5, D6, D14, D15 —
> different objects from the dafoam curriculum items. Every `D<n>` in this file is the **curriculum**
> item.

> **LAUNCH LAW, stated at the top because it governs every gate below.** Sanaa's ~21:00Z and ~22:00Z
> rulings of 2026-09-03: *a pre-registration mismatch never prevents a launch*, and *no
> non-physics / non-ill-posedness gate blocks a run.* **Every gate in §3 is POST-HOC.** None of them
> is consulted before or during a solve; the launcher consults exactly two things — the physical
> resource gates (H5 memory floor and the aggregate ceiling, which QUEUE rather than block) and the
> blocking-physics repair of §1, which exists precisely because an ill-posed setup *"will diverge and
> teach nothing"*. The item's own §4 cap is enforced as a container deadline, which is the fleet
> safety ceiling doing its job, not a gate refusing a launch.

---

## 0. WHAT `F_mp` AND `REF_off` ARE, AND WHY THEY HAVE NEVER RUN

`D6R` (`cases/dafoam/ladder-a/A2/curriculum_D6R/`) registered a four-arm detached chain on the A2
wing multipoint problem — three `ScenarioAerodynamic` scenarios `cl04`/`cl05`/`cl06` at CL targets
0.4/0.5/0.6, composite `J = Σ wᵢ·CDᵢ` with `w = (0.25, 0.50, 0.25)`, FFD 6×2×8 (96 shape DVs) plus
7 twist plus a per-point `patchV` angle of attack, at `np = 4` on the PATCHED
`dafoam-idwarp-rot:v1` image. The four arms, in chain order:

| arm | what it is | state of record |
|---|---|---|
| `O_mp` | the IPOPT optimisation itself, `run_driver`, `max_iter` 80 | **RAN, `rc = 0`, 2,257.933 core-min** |
| `ACC_mp` | `compute_totals` on a cold staged copy — three primals, three colourings, three adjoints | killed at its own 360 s deadline in `D6R`; **re-run to `rc = 0` as `D6RACC2`, 119.933 core-min** |
| **`F_mp`** | **the endpoint FINITE-DIFFERENCE table on the composite `J`** — `d6r_extract_endpoint.py` reads the optimiser's final design point out of `OptView.hst`, then `d6r_fd_endpoint.py` takes a two-step central-difference derivative of `J` at that point over **five components named in advance** (`shape[46]`, `shape[18]`, `shape[0]`, `twist[0]`, `patchV_cl05[1]`) and compares each against the **adjoint** gradient from one `compute_totals`. It is the FD-versus-adjoint **bright line** on a multipoint composite objective, and **this lab has never measured one.** | **NEVER RAN** |
| **`REF_off`** | **the OFF-DESIGN REFERENCE.** D4's PATCHED single-point optimum geometry (staged read-only, md5 `0d956d6ccbc010402915710f662d3b11`) is re-trimmed to CL 0.4, 0.5 and 0.6 by `findFeasibleDesign` **on the three `patchV` angles of attack only** — no shape, no twist change — and its three drag coefficients are written to `d6r_ref_off.json`. It is the thing that makes *"did multipoint optimisation actually buy off-design performance?"* a measurable question rather than a claim. | **NEVER RAN** |

**Why neither ran.** `D6R`'s `STATUS.chain` closes verbatim
(`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/STATUS.chain`):

    chain=STOPPED_AT_FIRST_NONZERO arm=ACC_mp rc=124 order=[O_mp ACC_mp F_mp REF_off] not_run=[F_mp REF_off]

`ACC_mp` hit its 360 s in-container deadline, the chain stopped at the first non-zero rc — the
registered behaviour — and the two arms behind it bought **0 core-min**. `D6RACC2` then bought
`ACC_mp` alone at a corrected cap and **demonstrated the predecessor's cap was 4.00× short**
(119.933 measured against 30.0). `D6RACC2` registered **exactly one arm** and explicitly declines
`F_mp` and `REF_off` (`curriculum_D6RACC2/PREREGISTRATION.md` §5). **No registration for these two
arms exists anywhere in the lab.**

**Why `D6R`'s own verdict does not travel here.** `D6R` is **`NOT A RESULT`**, graded by the
successor `D6RG` (`curriculum_D6RG/D6RG_regrade.json`), and it stays so; §9 forbids this item from
touching it. `D6R`'s §0 in turn records `D6` as `NOT A RESULT` by comparator refusal with zero gate
readings. **This item repairs nothing upstream and re-opens nothing. It buys two arms that were
never bought.**

### 0a. ⚠ THE PRODUCING OPTIMISATION FAILED, AND THAT IS DISCLOSED HERE, NOT DISCOVERED LATER

`F_mp` reads the endpoint of `O_mp`. `O_mp` exited `rc = 0` — but not because it converged and not
because it hit `max_iter`. Its own IPOPT file
(`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp/opt_IPOPT.txt:806, :822`):

    Number of Iterations....: 73
    EXIT: Invalid number in NLP function or derivative detected.

and `D6R`'s frozen grader classified it, through `D6RG`, as **`G-D6R-OPT` outcome `UNCLASSIFIED`**,
with 673 alpha cutbacks over 73 majors (9.22 per major) and 7 restoration majors
(`curriculum_D6RG/D6RG_regrade.json`, keys `grade/G-D6R-OPT/*`).

**What this does and does not cost this item.**
* The **FD bright line does not need an optimum.** It needs a valid geometry, a converged primal and
  an adjoint at the same point. `G-FD` is therefore a full gate here, and it is the item's centre.
* The **off-design comparison does need context.** `CDᵢ(mp)` is the LAST ACCEPTED MAJOR of a failed
  optimisation. `G-OFF` and `G-PRICE` still produce their own `PASS`/`GATE FAIL` rows, and the
  caveat is printed beside every one of them by the instrument itself (`d6rf_grade.py`,
  `gate_off`'s `caveat` key). **No claim of optimality is made anywhere in this item.**
* The **composite reduction is REPORTED, NOT GATED** (§3f). A reduction along the trajectory of an
  optimisation that died on a non-finite objective is a number, not a verdict.

---

## 1. THE THREE DEFECTS THIS ITEM REPAIRS, EACH MEASURED ON AN ARTEFACT STILL ON DISK

All three are **blocking physics fixes** in Sanaa's ~20:00Z taxonomy — *"a result can't be produced
or trusted without them"* — and under her ~21:00Z ruling an ill-posed setup is the one class where
*"launch anyway"* is wrong. They are repaired here, before compute, and the lesson is recorded
afterwards, not before.

### 1a. `D6RF-DEF-1` — **the endpoint design variables are DRIVER-SCALED, and `F_mp` would set the wing to ten times its deformation.** MEASURED.

OpenMDAO's `pyOptSparseDriver` applies each design variable's `scaler` **before** pyOptSparse sees
the problem, so `OptView.hst` holds **driver-scaled** values and the extractor's
`getValues(..., scale=False)` argument is **inert**. D4 met this as `D4-DEF-4` and preserved both
vectors side by side. Read off D4's own files today:

| | `d4_endpoint_dvs_DRIVERSCALED.json` | `d4_endpoint_dvs_PHYSICAL.json` |
|---|---|---|
| `patchV[0]` | **10.0** | **100.0** |
| `shape[0]` | 3.168962317413609 | 0.3168962317413609 |
| `twist[0]` | −0.023042706064274512 | −0.23042706064274512 |

(`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/F3/`, both files.)

The producer's own bytes give the factors — `d6r_opt_runScript.py:215-218`: `twist` `scaler=0.1`
bounds ±10.0; `shape` `scaler=10.0` bounds ±1.0; `patchV_<pt>` `scaler=0.1` bounds
`[U0, 0.0]`–`[U0, 10.0]` with `U0 = 100.0` at `:47`. **physical = driver-scaled ÷ scaler**, and
`10.0 ÷ 0.1 = 100.0 = U0` closes the identity exactly.

**`d6r_extract_endpoint.py` carries the same inert flag and has NO physical repair beside it**, and
`d6r_fd_endpoint.py:96-99` feeds its output straight into `prob.set_val`, which is PHYSICAL. With
`shape`'s scaler of 10.0 the wing is set to **ten times** its deformation, an order of magnitude
outside the registered `[-1, 1]` bound, and idwarp destroys the mesh. **That is D4's arm `F`,
`rc = 1` at 15 s** (`CURRICULUM-D4-a2-wing-cdmin/ledger.txt`, `ARM=F ... rc=1 wall_s=15`), whose log
ends `AnalysisError: 'scenario1.coupling.solver' <class DAFoamSolver>: Error calling
solve_nonlinear(), Mesh quality error!`.

**AND THE CRASH IS THE LUCKY OUTCOME.** Had `shape`'s scaler been 1.0, every primal would have
converged and the arm would have produced a complete, well-formed, plausible FD table **at a design
point that is not the one registered.** A units error is invisible to every count-, plant- and
order-based control this family owns. That is why the repair carries **two controls that establish
WHERE**, not merely that five components were measured.

**REPAIRED HERE** by `d6rf_endpoint_physical.py` (§7), a wrapper that edits zero bytes: it invokes
the committed `d6r_extract_endpoint.py` blob under an asserted md5, reads the scalers **from the
registering source**, divides each family by its own scaler, drives CONTROL P (three pinned
witnesses, one per point, each `patchV_cl0k[0] == U0`) and CONTROL B (bounds containment), preserves
the driver-scaled pre-image byte-for-byte, and writes the corrected artefact beside it.
**The same defect reaches `REF_off`** through `d4_extract_endpoint.py`, and is repaired there by
**D4's own `d4_endpoint_physical.py`, staged unmodified** — the instrument that already ran to
`rc = 0` in D4's arm F3.

> **A parser refusal, disclosed because it is why this repair never happened.** D4's
> `d4_endpoint_locus.py` (md5 `e63df1845771c3e67457443918f5b82e`) was pointed at the D6 producer and
> **REFUSED**: `parse_registration: {"add_design_var_first_arg_not_a_literal_string": true}`, because
> `d6r_opt_runScript.py:217-218` builds the three per-point names inside a loop. **D4's instrument
> was correct to refuse and the D6 lineage has therefore had no locus control at all.**
> `d6rf_endpoint_locus.py` widens the parser by **exactly one form** — `"<literal>" + <loop variable
> over a module-level list of strings>` — and every other form still refuses, driven at §7b.

### 1b. `D6RF-DEF-2` — **`D6R`'s `F_mp` runs in place inside `O_mp/`, on top of 912 of the optimiser's own output time directories.** MEASURED.

`d6r_run_arm.sh:310` takes the branch `if [ "$ARM" != "F_mp" ]` — i.e. for `F_mp` it does **not**
stage a case at all; it sets `WORK="$BASE/O_mp"` (`:341`) and runs inside the optimiser's finished
directory. That directory today holds, per point, **77 time directories in each of four processor
directories** (`O_mp/mp04/processor0` … `mp06/processor3`), of which **76 are outputs** (`0.*` plus
`1000`) — **912 output directories across the three points.**

DAFoam's `pyDAFoam.py:1543` `renameSolution` refuses to move a solution onto a directory that
already exists: `raise Error("%s already exists, moving failed!" % dst)`. **That is D4's arm `F2`,
`rc = 1` at 56 s** (`CURRICULUM-D4-a2-wing-cdmin/f2_ledger.txt`, `ARM=F2 ... rc=1 wall_s=56`), whose
log ends in exactly that traceback.

**D4's arm `F3` — `rc = 0`, 709 s, the ONLY successful FD-endpoint arm in this lineage — fixed it by
STAGING A COPY and dropping the outputs**, and its staging record says so verbatim
(`CURRICULUM-D4-a2-wing-cdmin/F3_STAGING_EVIDENCE.txt`):

    D4_STAGE_F3 (f) removed 333 arm-O output directories from the COPY
    D4_STAGE_F3 (f) pseudo-time directories remaining under .../F3 = 0 (required 0)
    D4_STAGE_F3 (f) SOURCE INTACT assertion: time directories under .../O/processor0 = 84 (required > 1, arm O's evidence is NOT touched)

**REPAIRED HERE** by §2a's staging contract, which is F3's, applied to three points instead of one.
`F_mp` gets **its own arm directory** in **this item's own run root**; `D6R`'s preserved root is
read-only source and goes at the head of `FORBIDDEN_ROOTS`. The `ARM_DIR["F_mp"] = "O_mp"` mapping
that `D6R` §3b defends is **not carried forward**, and the reason is not that the mapping was wrong
in `D6R` — it is that a copy is the only way to drop the outputs without writing into the directory
that holds `O_mp`'s 2,257.933 core-min of graded evidence.

### 1c. `D6RF-DEF-3` — **`REF_off`'s registered cap was 3.16× short of its measured cost, and its deadline was 1.63× short. It could not have finished either.** MEASURED.

`D6R` §4 registered `REF_off` at **17.1 core-min predicted, cap 40.0, in-container deadline 510 s**,
from an anchor written `10.5 × 1.6308`. **This lane could find no source, artefact or ledger row
anywhere for the 10.5**, and says so rather than repeating it.

The measured anchor exists and is in `D6R`'s own `O_mp` log. `d6r_opt_runScript.py:283-288` makes
`run_driver` call `findFeasibleDesign` on the three `patchV` **first**, before `prob.run_driver()` —
so the opening segment of `O_mp`'s log **is** the program `REF_off` runs. Measured in
`O_mp_20260828T162849Z_1898072.log`: the first `Design Vars: ['patchV_cl04', 'patchV_cl05',
'patchV_cl06']` at line **2115**; the last `ClockTime` before the first
`Driver debug print for iter coord` (line **10870**, the first IPOPT major) reads **`ClockTime = 833 s`**
at line **10842**.

**833 s × 4 ranks ÷ 60 = 55.53 core-min** — against a registered cap of 40.0 and a registered
deadline of 510 s. **`REF_off` would have been killed `rc = 124` at 510 s, roughly 61 % of the way
through its trim.** This is the `D6R-PREREG-DEF-1` class — the defect `D6RACC2` named for `ACC_mp` —
**present a second time in the same registration, in a second arm, and never exposed because the
chain stopped before it.**

**REPAIRED HERE** by §4's cap, derived from that measurement.

---

## 2. ARMS — TWO, IN THIS ORDER, ONE DETACHED CHAIN

| arm | kind (G1) | task | work dir | ranks | container mem | cpuset |
|---|---|---|---|---|---|---|
| `F_mp` | SOLVER | `d6rf_endpoint_physical.py --age-datum <epoch>` then `mpirun -np 4 python d6r_fd_endpoint.py` | `F_mp/` — **this item's own staged copy of D6R's `O_mp/`**, §2a | 4 | 20g | `2,3,4,14` |
| `REF_off` | SCRIPT | `d4_endpoint_physical.py --age-datum <epoch>` then `mpirun -np 4 python d6r_ref_off.py` | `REF_off/` — a cold copy of `base/` | 4 | 20g | `2,3,4,14` |

Chain: `F_mp` then `REF_off`, stopping at the first non-zero rc — **and that stop is a GRADEABLE
outcome**, not a refusal (§3a). **The five FD components, NAMED IN ADVANCE and unchanged from
`D6R`:** `shape[46]`, `shape[18]`, `shape[0]`, `twist[0]`, `patchV_cl05[1]`.

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF-a2-wing-multipoint-fd`.

### 2a. THE STAGING CONTRACT — frozen here so the launcher is written to it, not the other way round

`F_mp`'s directory is built by these steps, in this order, **every one aborting the arm rather than
degrading**, and each carrying its own printed evidence line into the arm's staging record. The
pattern is D4's arm F3 (`d4_stage_F3.sh`), extended from one point to three.

| # | step | assertion |
|---|---|---|
| S1 | source named: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp` | exists, holds `OptView.hst`; **destination `F_mp/` does not exist** |
| S2 | `D6R`'s preserved root is at the **head of `FORBIDDEN_ROOTS`** | a launcher pointed at it ABORTS and NAMES the evidence it just protected |
| S3 | reference-mesh identity, **the double-deformation confound eliminated by MEASUREMENT** | `md5(<src>/mp0k/constant/polyMesh/points.gz)` == `md5(base/constant/polyMesh/points.gz)` == **`0fb1935a9b8781b73ac4ccb136e3ec68`** for k ∈ {04, 05, 06}. *Measured true today; the decomposed `processor*/constant/polyMesh/points.gz` carries the `decomposePar` mtime of 2026-08-28T16:32:03Z and was never rewritten, so idwarp deformed in memory only.* **A moved md5 ABORTS** |
| S4 | `cp -a` the source to `F_mp/`, mtimes preserved; copy epoch recorded | source md5 manifest re-asserted intact AFTER the copy |
| S5 | **drop every output time directory FROM THE COPY**: `0.*` and `1000` under `F_mp/mp0k/` and under each `F_mp/mp0k/processor*/`; `postProcessing/`, `reports/`, `mphys.html`, `opt_IPOPT.txt` | **`0` is KEPT** (initial fields and the restart state); **`constant/`, `system/`, `FFD/`, `dRdWColoring_4.bin(.info)` and `OptView.hst` are KEPT**; assert **0 output time directories remain in the copy** and assert the **SOURCE still holds 77 per processor** — `D6R`'s evidence is not touched |
| S6 | stage the instruments, each md5-asserted against §7 | `d6r_extract_endpoint.py`, `d6r_fd_endpoint.py`, `d6r_opt_runScript.py`, `d6rf_endpoint_locus.py`, `d6rf_endpoint_physical.py` |
| S7 | remove any pre-existing product of this arm | the five names in `REGISTERED_PRODUCTS["F_mp"]` |
| S8 | the **AGE DATUM** is written LAST | `touch F_mp/0/*`; `stat -c %Y F_mp/0/U` → `F_mp/.d4_age_datum`. Every product must be strictly newer or it did not come from this run (rule 4) |

`REF_off/` is staged the ordinary cold way — `cp -a base REF_off`, G-COLD assertions (no
`processor*`, no time directory, no `OptView.hst`, no `reports`, `0/U` present), then D4's history
staged **read-only and md5-asserted at `0d956d6ccbc010402915710f662d3b11`** *before* the datum so the
age guard dates it as an input, then `d4_extract_endpoint.py`, `d4_opt_runScript.py`,
`d4_endpoint_locus.py`, `d4_endpoint_physical.py`, `d6r_opt_runScript.py`, `d6r_ref_off.py` staged
under their §7 md5s, then the datum.

### 2b. ROOT ABSENCE IS ASSERTED **BY EXECUTION**, THREE TIMES

1. **At freeze**, BY EXECUTION, output quoted verbatim:

       ROOT_ABSENCE_ASSERTED_BY_EXECUTION utc=2026-09-03T18:25:11Z
         /home/ubuntu/certonomous-runs/CURRICULUM-D6RF-a2-wing-multipoint-fd=ABSENT
         /home/ubuntu/certonomous-runs/CURRICULUM-D6RF=ABSENT

   This is rule 2's literal *"name the run directory that does not exist"* condition, **checked by
   running the check**, not asserted; the sibling name is asserted in the same invocation so a
   near-miss root cannot satisfy it.
2. **By the guard selftest** (§7c), which creates the root as a temporary EMPTY directory, drives the
   launcher into it, asserts zero entries gained, `rmdir`s it and asserts its absence again — with a
   container census before == after.
3. **By the launcher itself at first fire**, which refuses if the root exists with any content and
   stages nothing on a second fire (`ALREADY_BOUGHT`).

---

## 3. GATES — REGISTERED BEFORE COMPUTE, AND EVERY ONE OF THEM POST-HOC

`d6rf_grade.py` (md5 in §7) is **the grading path**, fixed at this commit. It verifies at execution
that its own bytes on disk equal the committed blob at `HEAD` and REFUSES if they do not.
Vocabulary: **`PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`** and no other word.

> **`GATE REACHED` IS DELIBERATELY NOT REGISTERED.** It labels an optimiser stopped by a wall clock,
> an iteration cap or a budget (`DAFOAM_CHARTER.md` §9). **This item runs no optimiser.** A word that
> can never fire is not registered, and the grader does not contain it.

### 3a. THE ARM CENSUS — a chain stop is GRADED, never refused

Before any gate, the grader builds a census of the two registered arms, in this fixed order:

1. **a ledger row exists** → `RAN`.
2. **no ledger row, and the driver's own `STATUS.chain` accounts for the absence** → `NOT_RUN`, with
   `reason = REGISTERED_CHAIN_<OUTCOME>`, the stop arm and the stop rc written into the verdict
   artefact. Registered accounting outcomes: `STOPPED_AT_FIRST_NONZERO`, `STOPPED_H5`, `BLOCKED_H5`,
   `BLOCKED_AGGREGATE`, `REFUSED_ALREADY_BOUGHT`, `ABORT`. **`COMPLETE` accounts for nothing.**
3. **otherwise → REFUSE.**

**Consequences, registered:** a gate whose input artefact's producing arm did not run returns
**`NOT A RESULT`** naming that arm, the artefact and the reason `ARM_DID_NOT_RUN` — **never
`GATE FAIL`, because nothing was measured that could fail**; a gate whose artefact is absent although
its producer DID run still **REFUSES**; arms that did not run bought **0 core-min** and are named as
such. **`G1` reports two separate facts** — `ran_clean` and `all_arms_ran` — **and they are never the
same verdict.** A **duplicate arm row REFUSES** (never last-wins), and **two `chain=started` lines
REFUSE** (`D6R` AMENDMENT 1's multiplicity guard, carried forward).

### 3b. `G-DVL` — THE ENDPOINT LOCUS. **The gate this item exists to add.**

The published physical artefact of **each** arm is **re-read from disk at grading time** and both
locus controls are **re-asserted**; the producer's own say-so is never trusted.

* **CONTROL P — the pinned witnesses.** A design-variable component whose registered `lower` equals
  its registered `upper` is DEFINITIONAL. This producer has **three**, `patchV_cl04[0]`,
  `patchV_cl05[0]`, `patchV_cl06[0]`, each pinned at `U0`. The control **discovers** them by scanning
  the registration and **REFUSES if it finds none** (L-302). Tolerance `1.0e-12` relative — a
  representation tolerance, four orders of margin on one IEEE-754 divide and four orders tighter than
  the smallest error it exists to catch (a factor of ten).
* **CONTROL B — bounds containment.** IPOPT does not violate bound constraints, so a reconstructed
  component outside its registered bounds is a units or indexing error. Tolerance `1.0e-9` absolute.
* the artefact must declare `_units: PHYSICAL`, and every registered design variable must be present.

`PASS` if both controls hold on both arms; `GATE FAIL` otherwise; `NOT A RESULT` where the producing
arm did not run. **Neither control grades anything** — they have no direction to be selected toward,
because they do not know which direction a verdict wants.

### 3c. `G-FD` — THE FD BRIGHT LINE ON THE COMPOSITE `J`. **The item's centre.**

Per registered component, from `d6r_fd_endpoint.json`:

* **relative error** `|d(s_hi) − J_adj| / |d(s_hi)| ≤ 5.0 %`
* **no sign flip** between `d(s_hi)` and `J_adj`
* **plateau** `|d(s_hi) − d(s_lo)| / |d(s_hi)| ≤ 10.0 %`

and across the planned components an **aggregate vector-relative error ≤ 5.0 %**.
**`≥ 2` sign flips → `NOT A RESULT`** — the pathology, named in advance. A component whose status is
not `PLANNED`, or either of whose FD legs did not evaluate, makes the gate `NOT A RESULT` for want of
an input, never `GATE FAIL`.

**The band is band D, `FD_BAND_PCT 5.0` / `AGG_BAND_PCT 5.0` / `PLATEAU_TOL_PCT 10.0`, inherited BY
CITATION from `D6R` §3e** (`VERIFICATION_CHARTER.md` §7 through D6 §3 and `DAFOAM_CHARTER.md` §2) and
**not re-derived here.** `D6R` §3e's reasoning transfers unchanged and is restated so it cannot be
lost: band D is the instrument band for **a finite difference against an adjoint at one `np` on one
decomposition**, which is exactly what this arm does. The far tighter `1.0e-3 / 2.2e-5` band at
`docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md:91-92` governs **np-invariance and partition
comparisons**, and **this item registers no such limb**: both arms run at `np = 4` on one
decomposition. **If a decomposition or np arm is ever added here it must carry that band, not this
one.** **No grid family exists, so no GCI is quoted anywhere in this item.**

### 3d. `G-OFF` — the three per-point off-design verdicts

For each of `cl04`, `cl05`, `cl06`: `CDᵢ(mp) ≤ CDᵢ(REF_off)` → `PASS`, else `GATE FAIL`. **Three
verdicts, always all three reported**, with `CL` and the trimmed angle of attack beside each.
`CDᵢ(mp)` is the last row of `d6r_major_history.json`; `CDᵢ(REF_off)` is `d6r_ref_off.json`.
**§0a's caveat is printed by the instrument beside every row of this gate.**

### 3e. `G-PRICE` — the single-point price at CL 0.5, behind a planted-zero control

`CD₀.₅(mp) − CD_f(D4) ∈ [0, 1.0e-3]` → `PASS`; `> 1.0e-3` → `GATE FAIL`; **negative → `NOT A RESULT`
pending triage** (a finding about D4, named in advance). `CD_f(D4)` is **re-read** from
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` (read-only, the single
`^Objective` line, refused if there is not exactly one) and **REFUSED if it differs from the recorded
`2.1125978108239574e-02`**.

### 3f. `R-RED` — **REPORTED, NOT GATED**

The composite reduction `(J₀ − J_f)/J₀` is computed and printed with the reference band `[15, 40] %`
beside it, and **gates nothing**. Sanaa's ~20:00Z default applies and the reason is stated in the
required form: this row **cannot** support *"without this, the verdict on the FD bright line cannot
be trusted"*, because the producing optimisation exited on a non-finite objective (§0a). It is a
**physics finding**, reported with its evidence.

### 3g. `G-CAPS`, `G9`, `G12`

* **`G-CAPS`** binds four limbs: `core_min ≤ cap`; the frame inversion
  `(TMO + FRAME_ALLOWANCE_S) × RANKS ÷ 60 == cap` to 0.02 core-min; `container_wall_s ≤ TMO +
  KILL_GRACE_S`; and `host_wall − container_wall ≤ FRAME_ALLOWANCE_S − KILL_GRACE_S = 30 s`, plus
  `frame_allowance_s` cross-pinned against the ledger's own field. **An absent container clock is
  INFRASTRUCTURE** (L-342): the frame limbs go `NOT_MEASURED` and the gate falls back to the host
  bracket alone — **the stricter reading, so the fallback can never turn a failing cap into a pass.**
* **`G9`** — the PATCHED digest on every row, `PATCHED` in the `ROW` field, and the PATCHED
  `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425` in every log.
* **`G12`** — `cpuset == 2,3,4,14` and `memory == 20g` on every row; delivered cores ≥ 3.0 of 4 where
  measured, `NOT_MEASURED` **disclosed and not failed** where the sampler produced nothing.

### 3h. THE PLANTED-ZERO CONTROLS (`CLAUDE.md` rule 3) — two, and neither is skippable

Both plant a known perturbation **`PLANT = 1.234e-03`** into a **COPY**, read it back **from disk
through the SAME reader**, and **REFUSE (exit 2)** if the reader cannot see it. Both also assert the
**unperturbed original is byte-unchanged** by md5 before and after — a control that modifies the
artefact it grades is not a control.

* **the FD reader** — planted **by key** into the first `PLANNED` row's `s_hi` derivative; refuses if
  there is no plantable row at all (L-302).
* **the price reader** — planted **by line index** into a copy of D4's `opt_IPOPT.txt`; **D4's
  preserved artefact itself is never written to.**

Both refusals are DRIVEN at §7b against deliberately blind readers.

### 3i. THE VERDICT LADDER, in order

A `NOT A RESULT` can only turn a `PASS` or `GATE FAIL` **into** a `NOT A RESULT`, never the reverse.

1. a completion clause failed on an arm that **ran** → **`NOT A RESULT`**;
2. a registered arm **did not run** → **`NOT A RESULT`**, arms named (the item can never be `PASS`
   with an arm unbought);
3. **`G-DVL` `GATE FAIL`** → **`NOT A RESULT`** — the design point on disk is not the one the
   registration names, so nothing downstream of it measures what it says;
4. the registered pathologies — `G-FD` `≥ 2` sign flips, `G-PRICE` negative → **`NOT A RESULT`**;
5. any gate `NOT A RESULT` for want of an input → **`NOT A RESULT`**;
6. else any gated row `GATE FAIL` → **`GATE FAIL`**;
7. else → **`PASS`**.

---

## 4. COST — BOTH ARMS ANCHORED ON MEASUREMENTS OF THE PROGRAMS THEY ACTUALLY RUN

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Dollars are DERIVED, never measured.**
The unit is **core-minutes** (`wall_s × ranks ÷ 60`). **An overrun stops the run; it does not get a
new budget** (rule 12).

### 4a. The measured anchors, each with its artefact

| tag | value | artefact and line |
|---|---|---|
| **A1** | `O_mp` **rc=0, wall_s 33869, ranks 4 → 2,257.933 core-min** | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/ledger.txt`, the `ARM=O_mp` row (`container_wall_s=33794 delivered_cores_mean=[3.9791 n=2240]`). **Spent, graded and NOT re-bought here** — it is `F_mp`'s INPUT, not its cost |
| **A2** | `ACC_mp` **rc=0, wall_s 1799, ranks 4 → 119.933 core-min** | `/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint/ledger.txt`, the sole `ARM=ACC_mp` row (`cap_core_min=240.0 container_wall_s=1793 delivered_cores_mean=[3.9819 n=118]`). The **multipoint** `compute_totals`, cold |
| **A3** | D4 `P2` **rc=0, wall_s 546, ranks 4 → 36.4 core-min** | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/ledger.txt`, the `ARM=P2` row. The **single-point** `compute_totals`, cold (`curriculum_D4/PREREGISTRATION.md:266`) |
| **A4** | D4 `F3` **rc=0, wall_s 709, ranks 4 → 47.267 core-min** | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/f3_ledger.txt`, the sole `ARM=F3` row. **The only FD-endpoint arm that has ever succeeded in this lineage** — same five components, same step ladder, colouring CACHED (`F3_20260825T220706Z_2733788.log:1113` `dRdWColoring_4.bin exists.`) |
| **A5** | the multipoint `findFeasibleDesign` trim **833 s wall, ranks 4 → 55.53 core-min** | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log`: trim starts at line **2115** (`Design Vars: ['patchV_cl04', 'patchV_cl05', 'patchV_cl06']`), last `ClockTime = 833 s` at line **10842**, first IPOPT major at line **10870** |
| **A6** | setup + one multipoint primal **≤ 68.15 s** | `/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint/ACC_mp_20260830T235332Z_1606819.log:2789`, `Calculating dRdW Coloring... 68.15 s` — the elapsed clock at which the first colouring begins, so everything before it is start-up plus the three point primals |

### 4b. `F_mp` — 155.70 core-min, by two routes that share no arithmetic

**PRIMARY (Route A): a measured FD arm × a measured multipoint factor.**

    A4  the FD program at ONE point, measured                 47.267 core-min
    A2 / A3  the SAME program at three points ÷ at one point   119.933 / 36.4 = 3.2949x
    F_mp  =  47.267 x 3.2949                              =   155.74 core-min

Both terms are measurements and **no invented correction is applied.** The multipoint factor is a
ratio of two measurements of *the identical program* (`compute_totals` on a cold staged copy of this
wing at `np = 4`, on the same PATCHED digest), one at three scenarios and one at one. That is
`D6RACC2` §2's two-measurement pattern, and it is why **`D6R`'s `1.6308` correction is NOT used
here**: `1.6308` was measured on `O_mp`'s **per-major optimiser rate**, a quantity `F_mp` does not
have, and the family's only measured estimate-versus-actual for a non-optimiser multipoint arm is
**`C-220`: 119.933 against 112.40 registered, ratio 1.0670.**

**CORROBORATION (Route B): the segment model, from A6 and A2's own log.**

    22 multipoint primals (2 baseline + 5 components x 2 steps x 2 signs) x 68.15 s   1,499.3 s
    compute_totals with the colouring CACHED: 3 adjoints at the mean of the two
      measured (110.10 s and 120.89 s in A2's log, lines 2852->2900 and 2963->3011)     346.5 s
                                                                        total        1,845.8 s
                                                        x 4 / 60      =              123.05 core-min

**155.74 against 123.05 — a spread of 26.5 %, and it is wider than `D6RACC2`'s 4.7 %, so it is
named rather than smoothed.** The spread has a direction and a reason: Route B prices all 22 primals
at A6's *staged-baseline* primal, and `F_mp`'s FD primals are at **perturbed geometries** that must
be re-warped and re-converged, so Route B **under-states**. **The larger route is registered.**

**Registered estimate: `F_mp` = 155.70 core-min.**

### 4c. `REF_off` — 60.07 core-min, from the same program measured in `D6R`'s own log

    A5  the multipoint findFeasibleDesign trim, measured           55.53 core-min
    A6  the one closing prob.run_model() after the trim (68.15 s)   4.54 core-min
                                                        total      60.07 core-min

Both exposures are stated rather than buried. **(i)** A5's trim started from `base`'s geometry at
`aoa0`; `REF_off` starts from **D4's optimum geometry at D4's endpoint AoA**, so its iteration count
may differ — **direction unknown, and it is not assumed in either direction.** **(ii)** A6's 68.15 s
covers start-up plus three point primals on a staged tree, so charging it whole to one closing primal
**over-states** slightly, which is the conservative direction.

**Registered estimate: `REF_off` = 60.07 core-min.** Compare `D6R`'s registered 17.1 and its 40.0
cap: §1c.

### 4d. THE CAP — the family's ADOPTED form, the MAX of two risks and never their product

    effective_cap  >=  max( 3.0 x estimate-at-a-MEASURED-anchor ,
                            1.25 x wall-at-registered-max-occupancy )

Adopted by the dafoam-supervisor after his own error of compounding a 3× envelope onto a 9.5×
occupancy factor (`docs/LAB_STATE.md`, block `S-29` §7.4). **It is a MAX, never a product**, and
that is why the two legs are printed separately below.

**The occupancy leg's registered max occupancy, stated so the leg is checkable.** `G12` registers a
**delivered-cores floor of 3.0 of 4**; an arm delivered 3.0 instead of 4.0 cores takes `4/3 ×` its
solo wall, and the recorded `core_min = wall × ranks ÷ 60` grows in the same proportion because
`ranks` is fixed at 4. Registered max occupancy is therefore **`estimate × 4/3`**.
*Measured context, disclosed:* every arm in this lineage that recorded a delivered-cores sample
recorded **3.93–3.99 of 4**, with siblings present in `D6RACC2`'s case and absent in `D6R`'s — so on
this box, under `--cpuset-cpus` pinning, **occupancy has had no measurable effect on delivered
cores**, and the occupancy leg is a registered conservatism rather than an observed one.

| arm | estimate | leg 1: `3.0 ×` | leg 2: `1.25 × (4/3) ×` | `max` | **REGISTERED CAP** |
|---|---|---|---|---|---|
| `F_mp` | 155.70 | **467.1** | 259.5 | 467.1 | **480.0** |
| `REF_off` | 60.07 | **180.2** | 100.1 | 180.2 | **190.0** |
| | **215.77** | | | | **ceiling 670.0** |

### 4e. THE DEADLINE IDENTITY — the arithmetic that made `D19T` unrunnable forever, checked here arm by arm

`D19T` was frozen, md5-pinned, gate-checked and launched twice, and **no check ever executed its own
cap arithmetic**: `TMO = int(CAP × 60 / RANKS) − CAP_MARGIN_S` with `CAP_MARGIN_S = 60` gave its
`MESH` arm `TMO = 0 s` at cap 1.0 and 1 rank, the `TMO > 0` guard fired, and no arm behind it could
ever run (`docs/LAB_STATE.md` `S-28` §4). **The identity is executed here, at freeze, for both arms,
under BOTH margin conventions.**

**This lineage's registered convention is `FRAME_ALLOWANCE_S = 90`, not `CAP_MARGIN_S = 60`** —
`d6r_run_arm.sh:251-256` — and 90 is the larger, hence the stricter, reserve. The `60` of the `D19T`
identity is the `A1` family's (`d19o_run_arm.sh:153`), and `180` is `SO3`'s
(`so3_run_arm.sh:208`). **All three are recorded so the difference is not mistaken for drift.**
The registered form here is `TMO = round(CAP × 60 / RANKS) − 90`, guarded `TMO > 0`, and the
inversion `(TMO + 90) × RANKS ÷ 60` must return the cap to **0.02 core-min** in **both** the launcher
and the grader — **so no edit to the allowance can silently widen the cap.**

| arm | cap (core-min) | ranks | **`TMO` (s), margin 90** | inversion | `TMO` at margin 60 | measured-anchor wall | `TMO / anchor wall` | derives from |
|---|---|---|---|---|---|---|---|---|
| `F_mp` | **480.0** | 4 | **7,110** | `(7110+90)×4/60 = 480.000000` ✓ | 7,140 | **2,335.5 s** | **3.04×** | A4 × (A2/A3) |
| `REF_off` | **190.0** | 4 | **2,760** | `(2760+90)×4/60 = 190.000000` ✓ | 2,790 | **901.0 s** | **3.06×** | A5 + A6 |

**Every arm's `TMO` is comfortably positive under both conventions, and every arm's `TMO` is more
than `1.5 ×` its measured-anchor wall** — the registration-defect test this item was required to
apply before freezing, not after. **The margin is 3.04× and 3.06×, roughly double the 1.5× floor.**

**Disclosed, because `D6RACC2` §2d chose its cap partly to avoid it:** `F_mp`'s deadline of 7,110 s
sits **above** rule 12's 3,600-second stall convention, so an arm that runs all the way to its own
deadline would also be a stall row. `REF_off`'s 2,760 s sits below it. **`F_mp`'s deadline cannot be
brought under 3,600 s without cutting the cap below its own `3.0 ×` leg** — 3,600 s at 4 ranks is
246.0 core-min against a required 467.1 — so the property is **given up knowingly and named**, not
lost. `F_mp`'s *estimate* is 2,335.5 s, well under 3,600, so a healthy run is never itself a stall
row; only a run that has already overrun by 1.54× is, **and that is itself the finding.**

### 4f. Dollars, DERIVED

| | core-min | core-h | **$ DERIVED at $0.0513/core-h** |
|---|---|---|---|
| estimate | **215.77** | 3.5962 | **$0.1845** |
| ceiling | **670.00** | 11.1667 | **$0.5728** |

Both far inside the $25 pre-authorisation, and inside the $1,000 industrial-ladder envelope without
touching it. **A rule-12 calibration row is OWED at completion** in `docs/COST_CALIBRATION.md`,
stating actual/predicted per arm, attributing the gap, and naming waste separately.

### 4g. Memory and the H5 gate — a RESOURCE gate, which QUEUES and does not block

Both arms 20g; **H5 floor 24.0 GiB** (cap + 4 GiB headroom, the D4-SHIPPED §4.4 formula); aggregate
ceiling **30.6 GiB**. **Never 8g** — D4-SHIPPED's `ACC` arm was OOM-killed by its 8g cgroup
(`rc = 137`). `D6RACC2` measured `OOMKilled=false` for the identical multipoint program at 20g, so
20g is a measured floor, not a guess. **Measured live at freeze:** one container on this box,
`d12y_w3_S3b_c0_am_20260903T172242Z_179692`, **cpuset `1`, 8 GiB** — read read-only by
`sudo -n docker inspect`, **not signalled, not written to, not otherwise touched**. Its cpuset is
**disjoint** from this item's `2,3,4,14`. Its 8 GiB cap plus this item's 20 GiB plus host
non-container RSS sits **at or just over the 30.6 GiB aggregate ceiling**, so the driver's own
wait-and-retry gate **may hold the first arm until that chain finishes.** Under Sanaa's ~21:00Z
ruling that is a **resource gate: queue, don't launch — and queueing is not blocking.** It is
registered here rather than discovered at fire.

---

## 5. PREDICTIONS — scored HIT / MISS / NOT A RESULT afterwards, never adjusted

| # | prediction | band / point |
|---|---|---|
| **P1** | **the repair is load-bearing: `G-DVL` `PASS` on both arms, and the preserved driver-scaled pre-image differs from the published physical vector by exactly the registered scalers** | `patchV_cl0k[0]` reads **10.0** driver-scaled and **100.0** physical, on all three points. **A MISS here means the scaler mechanism is not what §1a says it is, and that is worth knowing** |
| **P2** | **the chain COMPLETES — both arms run** | because the two failure modes that killed D4's `F` and `F2` are both repaired by construction (§1a, §1b). HIT/MISS by `chain=COMPLETE` and an empty `not_run` list |
| **P3** | `G-FD` aggregate relative error | **≤ 5 %**, point **1.5 %**. The adjoint on this case has never been checked against an FD on a *composite* objective; the point estimate is D4's single-point experience carried across, and it is a prediction, not a measurement |
| **P4** | sign flips | **0**. `≥ 2` fires the registered pathology |
| **P5** | `F_mp` cost | **[110, 480]** core-min, point **155.7** |
| **P6** | `REF_off` cost | **[45, 190]** core-min, point **60.1** |
| **P7** | off-design gain `CDᵢ(REF_off) − CDᵢ(mp)` at 0.6 and at 0.4 | **> 0** at both, point **+8.0e-4** and **+2.0e-4**. `D6R` P4's points, carried unchanged, **and now with §0a's caveat attached: the multipoint point is not an optimum** |
| **P8** | single-point price `CD₀.₅(mp) − 2.1125978e-02` | **[0, 1.0e-3]**, point **+3.0e-4** |
| **P9** | no arm OOM-killed at 20g | regression check on a question `D6` and `D6RACC2` already answered; **not re-bought** |

**Predicted outcome, written before compute so it cannot be written afterwards.** The most likely
item verdict is **`PASS`** if the adjoint is sound on the composite objective and **`GATE FAIL`** if
it is not — and **either is a real result**, because the FD-versus-adjoint bright line on a
multipoint composite `J` has never been measured in this lab. The outcome this lane rates least
likely and would find most interesting is **`NOT A RESULT` by the sign-flip pathology**, which would
say the composite adjoint disagrees with finite differences in *direction* at more than one
component.

---

## 6. TWO ROWS OR IT IS NOT A VERDICT — and this item's honest position

`DAFOAM_CHARTER.md` **§6** (not §11, which is the lessons-numbering clause and is a **struck slip**
carried by `D8R`'s queue entry and `D6`'s launcher comment).

| row | image | digest | state in `D6RF` |
|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **the only row bought**; the launcher's `G-ROW` refuses anything else and `G9` is driven to `GATE FAIL` on a SHIPPED digest and on a moved `libidwarp.so` md5 (§7b legs 25 and its toolchain sibling) |
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **NAMED UNBOUGHT** — no `D6RF` number is a statement about the shipped toolchain |

**STATED PLAINLY, AND NOT WAIVED:** with one row, **this item produces no DAFoam verdict under
§6** — the same position `D6RACC2` reached and recorded (`curriculum_D6RACC2/RESULTS.md` §1). What
it produces is a **PATCHED-row measurement** with its own gate verdicts, exactly as `D6R` and `D13`
did, disclosed on that precedent. **Narrowing or waiving §6 is reserved to Sanaa** and is not
proposed here.

---

## 7. INSTRUMENTS — the md5 table, and the ONE deliverable still outstanding

### 7a. Frozen at this commit

| file | md5 | role |
|---|---|---|
| `d6rf_grade.py` | **`240cd657acc75287ed962e08fe715509`** | **THE GRADING PATH.** Verifies disk == committed blob at HEAD at execution |
| `d6rf_grade_selftest.py` | `d55ed774f178216562fef76daf0c0345` | drives every outcome and every refusal |
| `d6rf_endpoint_locus.py` | `341189ca866f302a7e1bba8eefad3a57` | the two locus controls and the widened parser |
| `d6rf_endpoint_physical.py` | `ea0a83410c773f753a7750eb3becefdf` | the `F_mp` repair wrapper (edits zero frozen bytes) |
| `d6rf_selftest_evidence.txt` | `6bf6e234dc4414bf3d8cdda46a7c7d60` | the driven evidence, both interpreters |

### 7b. Staged from elsewhere, UNMODIFIED, each md5-asserted before use

| file | md5 | source |
|---|---|---|
| `d6r_extract_endpoint.py` | `1743dd4232a7f06785f71be2f285f08d` | `curriculum_D6R/`, frozen |
| `d6r_fd_endpoint.py` | `7491c3a73c232fb6744990fd8109fd63` | `curriculum_D6R/`, frozen |
| `d6r_opt_runScript.py` | `93edb4a231e13a7af065368f61a468ef` | `curriculum_D6R/`, frozen — the producer, and the source of every scaler |
| `d6r_ref_off.py` | `ad67bbeb0c7b502262ebf5d4e8fa21cd` | `curriculum_D6R/`, frozen |
| `d4_extract_endpoint.py` | `ee7d3c99fd716da23779cb651961918e` | D4's, unmodified |
| `d4_opt_runScript.py` | `2906d52a5dbed2bacbaeaf85a37d3fe8` | D4's, unmodified — the scaler source for `REF_off` |
| `d4_endpoint_locus.py` | `e63df1845771c3e67457443918f5b82e` | D4's, unmodified |
| `d4_endpoint_physical.py` | `74c35c80bb4d395cf8939d851bc6b3f9` | D4's, unmodified — **the instrument that already ran to `rc = 0` in D4's arm F3** |
| D4's `OptView.hst` | `0d956d6ccbc010402915710f662d3b11` | `CURRICULUM-D4-a2-wing-cdmin/O/`, staged READ-ONLY into `REF_off/` |
| `D6R`'s `OptView.hst` | `70fafa07bdee618fef13039433c01114` | `CURRICULUM-D6R-.../O_mp/`, carried by the §2a copy; **`D6R`'s copy is never written to** |

**THE INSTRUMENTS ARE DRIVEN, NOT ASSERTED — evidence at `d6rf_selftest_evidence.txt`, four drives,
zero containers created, zero solver core-minutes:**

| drive | interpreter | result |
|---|---|---|
| `d6rf_endpoint_locus.py --selftest` | `python3` | **30/30 PASS** |
| `d6rf_endpoint_locus.py --selftest` | `python3 -O` | **30/30 PASS** |
| `d6rf_grade_selftest.py` | `python3` | **37/37 PASS** |
| `d6rf_grade_selftest.py` | `python3 -O` | **37/37 PASS** |

What those 67 legs actually drive, so the number is not the claim: the **live defect vector itself**
(a driver-scaled endpoint) firing **both** locus controls; a pinned witness off `U0` by 0.1 % and by
`1e-9`, and NOT firing at `1e-13`; every parser widening bounded (an f-string name, a bare-variable
name, a loop over `range`, a `POINTS` that is not a module list, an ambiguous loop variable — all
refuse); every FD band, the plateau, one sign flip versus two; a component with no FD pair;
`rc != 0`; `OOMKilled`; **a registered product older than the arm's own age datum**; an arm missing
with the chain accounting for it, and an arm missing while the chain says `COMPLETE` (refuses); a
duplicate ledger row and a second `chain=started` (both refuse); cap, container clock, frame gap,
`NOT_MEASURED` fallback, SHIPPED digest, cpuset, delivered cores, memory; D4's reference moved on
disk; the freeze check on an absent path; and **both planted-zero controls seeing a live
`1.234e-03` plant, refusing a deliberately blinded reader, refusing an artefact with nothing to
plant into, and leaving both originals byte-unchanged.**

### 7c. ⚠ THE ONE DELIVERABLE STILL OUTSTANDING, NAMED RATHER THAN GLOSSED

**`d6rf_run_arm.sh` and `d6rf_chain_driver.sh` ARE NOT WRITTEN.** They are the launcher and the
detached driver, and they land as a **dated pre-compute addendum** to this file — legal under rule 2
because gates are open until first compute, and the condition is stated and checked by execution:
**the run root `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF-a2-wing-multipoint-fd` does not exist**
(§2b, asserted in the committing invocation). **No queue row may be enqueued and no container may
start until that addendum lands** carrying:

1. the two files' md5s, added to §7a;
2. `d6rf_guard_selftest.py` **DRIVEN**, with a container census before == after and **zero containers
   created** — a launcher containing `sudo -n rm -rf "$WORK"` is trusted only after its guards are
   shown to abort, and `D6RACC2` §4's 16/16 is the standard;
3. the guards driven specifically against **`D6R`'s preserved run root** (must ABORT and NAME it),
   against every arm name but `F_mp` and `REF_off` (must ABORT, by equality not prefix), against the
   §4e cap identity in the file (`TMO` 7,110 and 2,760, inverting exactly), and against **§2a's S3
   and S5** — the reference-mesh md5 and the output-directory drop, with the source asserted intact;
4. the assertion that **every guard precedes the first destructive step**, with both line numbers
   **recomputed from the file**.

**Nothing in §1–§6 changes when that addendum lands.** No gate, threshold, band, cap, label,
prediction or cost may move in it, and if any needs to, this registration is withdrawn and a
successor is written instead.

---

## 8. WHAT THIS ITEM MAY NOT CONCLUDE

* **Nothing about `D6R`'s verdict.** `D6R` is `NOT A RESULT`; `D6RG` graded it and that record
  stands. This item does not re-open, revise or repair it, and
  **`VERIFICATION_CHARTER.md` §2d.1 is NOT invoked** — refused seven times in this family and not
  proposed an eighth.
* **Nothing about `D6`.** `NOT A RESULT`, gates CLOSED, rule 5 one-way.
* **Nothing about `O_mp`.** Its 2,257.933 core-min are spent and are not re-bought; its
  `UNCLASSIFIED` optimiser outcome stands and is quoted, never re-graded.
* **Nothing about the SHIPPED toolchain** (§6).
* **No claim that the endpoint is an optimum** (§0a). The two locus controls say the FD table is at
  the design point the registration names. **Only a solve says more, and `D6R`'s solve failed.**
* **Nothing about WHY the primal returns non-finite values at trial geometries.** `D6R` §6 declined
  that question and priced it separately; so does this item. It is the obvious follow-up and it is
  a separate registration.
* **No GCI, anywhere.** There is no grid family here (§3c).
* **A `GATE FAIL` or a `NOT A RESULT` here is a result and is reported as one.**

---

## 9. THE BUY QUESTION, PUT ON THE SUPERVISOR'S DESK BEFORE ANY ENQUEUE

**What 215.8 core-min buys:** the FD-versus-adjoint bright line on a **multipoint composite
objective** — never measured anywhere in this lab; the **off-design reference** that makes
single-point-versus-multipoint a measurable comparison rather than a claim; three per-point verdicts;
and a **locus control the D6 lineage has needed since D4 and has never had**, which §1a shows would
have silently certified a wrong-design-point FD table had one scaler been 1.0 instead of 10.0.

**What it does not buy:** an optimality claim, a second toolchain row, or any repair to `D6R`.

**The honest risk, stated once:** §1's three repairs are established by measurement and driven at the
instrument level, but **no container has ever run `F_mp` or `REF_off`, at any point in this
lineage.** D4's F3 is the closest precedent and it is a single-point arm. **If the chain still fails,
`P2` MISSES and that is the finding** — reported, not absorbed, and not given a new budget.

**`CLAUDE.md` check-4 — the pre-registration committed before compute — is the SUPERVISOR'S, and this
lane claims none of it.** Enqueueing is not authorisation.
