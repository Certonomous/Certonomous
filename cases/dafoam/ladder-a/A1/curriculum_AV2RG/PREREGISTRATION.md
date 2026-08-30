# AV2RG — PRE-REGISTRATION (FROZEN). AV2R re-graded through the recovered `gmresRelTol`

**Item:** `AV2RG` — successor re-grade of **`AV2R`** from its **preserved run root**, through a
repair for **one root cause on the PRODUCER side**.
**Team:** dafoam. **Lane:** `lab-lane`. **Date:** 2026-08-30.
**Solver compute: ZERO.** Nothing meshed, nothing solved, no container, no GPU.
**Provenance:** item 4 of 7 of Sanaa's ordered re-grade sweep, assigned by the dafoam
supervisor 2026-08-30. Pattern adopted from `curriculum_AVWC/PREREGISTRATION.md` and
`curriculum_AVWC/avwc_grade.py` (frozen at `c85eb4df`), which is the sweep's precedent for a
producer-side defect.

---

## 1. THE ROOT CAUSE, ONE SENTENCE, MEASURED FROM DISK AND NOT FROM THE RECORD

**The PRODUCER never wrote `gmresRelTol` into the artefact identity, although it held the
value in the same process one statement earlier.**

| where | what is there |
|---|---|
| `av2r_xf.py:56-63` `idwarp_identity()` | returns `{"idwarp_file", "libidwarp_so_md5"}` and **nothing else** |
| `av2r_xf.py:203` (mode `X`), `av2r_xf.py:259` (mode `FAD`) | writes that dict verbatim as `out["identity"]` |
| `av2r_xf.py:152-156` | **emits `(daOptions.get("adjEqnOption") or {}).get("gmresRelTol")` into the JSONL sidecar ONE STATEMENT EARLIER** — the producer had it and did not copy it across |
| `av2r_grade.py:321` | `"gmresRelTol": (j.get("identity") or {}).get("gmresRelTol")` → `None` |
| `av2r_grade.py:511-513` | `if X[rk]["gmresRelTol"] != GMRES_REL_TOL_REGISTERED: refuse("G-DP", …)` |

Measured on the preserved artefacts: `X-S/av2r_X.json` and `X-P/av2r_X.json` carry
`identity` keys **exactly** `['idwarp_file', 'libidwarp_so_md5']`, and the string `gmres`
does not occur anywhere in either file.

**THE GRADER IS NOT DEFECTIVE. IT REFUSED ON ABSENT DATA, WHICH IS THE CORRECT BEHAVIOUR**,
and this successor does not treat it as though it were. That is why the registered rebind
set below is **the empty set**.

**The defect is inherited, not local.** `idwarp_identity()` is **byte-identical** between
`curriculum_AV2/av2_xf.py` and `curriculum_AV2R/av2r_xf.py`, which is why AVWC's independent
re-grade of AV2 landed on the same `G-DP` refusal with the same
`gmresRelTol_in_artefact: null` (`curriculum_AVWC/AVWC_regrade.json`). Two items, two run
roots, one omission, one line of source.

## 2. THE VALUE IS RECOVERABLE, AND IT IS RECOVERABLE THREE WAYS

`gmresRelTol` is **dimensionless** — a relative Krylov residual tolerance on the adjoint
linear solve. Read from the preserved root, before this freeze, on **every** arm:

| source | file | value |
|---|---|---|
| **R** run-time record | `<arm>/av2r_X.jsonl` / `av2r_FAD.jsonl`, the single `{"kind":"identity"}` record | `1e-06` on X-S, X-P, FAD-S, FAD-P |
| **C** the container's own DAOption echo | the arm's solver log, `gmresRelTol 1e-06;` | X-S line 350, X-P line 349; 1 echo on each X arm, 6 on each FAD arm, **all `1e-06`** |
| **F** the frozen input | `<arm>/av2r_runScript.py:69`, `"adjEqnOption": {"gmresRelTol": 1.0e-6, …}` | `1.0e-6`, md5 `0557da51f6f179f6de865144343c499f` on every arm |

So the answer to *"was the measurement ever taken"* is **yes**, and the failure is a
recording failure, not an absence.

## 3. HOW IT RE-GRADES — IT REBINDS NOTHING AND RE-IMPLEMENTS NO GATE

The successor imports **AV2R's own frozen comparator**, verifies the file on disk is
byte-identical to the committed blob, **rebinds NO name**, and runs **the frozen `grade()`**.
The repair is upstream, so it is applied where AVWC applied AV1R's producer repair
(`avwc_grade.py:171-190`): the recovered value is written into a **copy** of the artefact and
the frozen grader is then run **completely unmodified**.

| file | md5 (disk **==** `HEAD` blob, both verified at this freeze) | rebound |
|---|---|---|
| `curriculum_AV2R/av2r_grade.py` | `8a2dcebd954f56d9970601fc7761787a` | **none (0)** |
| `curriculum_AV2R/av2r_xf.py` | `32a755bc9fa84bc0e03ab02bb6ec3c3c` | read-only (the md5 pin for source **F** is taken from **its own** `PRODUCER_MD5` constant) |

`8a2dcebd954f56d9970601fc7761787a` is also the md5 registered at
`curriculum_AV2R/PREREGISTRATION.md:141` and `:162`, and `32a755bc9fa84bc0e03ab02bb6ec3c3c`
at `:144` — checked against both, not accepted from either.

**The rebind is audited, not asserted.** The comparator fingerprints every callable in the
imported module before and after and **REFUSES** (`REBIND_AUDIT`) if the rebound set is not
exactly `()`.

## 4. THE REGISTERED SOURCE IS NOT CHANGED — AND THIS IS THE POINT WORTH READING TWICE

`curriculum_AV2R/PREREGISTRATION.md:72` registers that *"the grader reads `gmresRelTol` from
the artefact identity and REFUSES if it is not 1e-6"*. **It still does.** `av2r_grade.py:321`
and `:511-513` run untouched and read the same key of the same file. What this successor
restores is the field the producer was supposed to put there. The frozen document's
registered source is honoured **literally**; the producer's **omission** is undone, not
routed around. Had the successor instead taught the grader to read a log, it would have
re-registered a source after the answer was known, and that is the one thing it may not do.

## 5. NO FOURTH IMPLEMENTATION — WHAT IS ADOPTED, AND THE ONE HONEST GAP

| adopted | from | what is preserved |
|---|---|---|
| the **three-source agreement rule** | `av2r_grade.py:466-479` `g_toolchain` — the frozen module's own rule: ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print, the artefact's in-process md5, **all three or `GATE FAIL`** | the *shape* of the rule: a run-time record, the container's own print, and the frozen input, as **peers**. No majority vote, no fallback ordering |
| the copy / manifest / rebind-audit / refuse-through-the-frozen-module machinery | `curriculum_AVWC/avwc_grade.py:117-261` | preserved roots read never written; refusals carry **no new vocabulary** |
| the producer-defect repair shape | `avwc_grade.py:171-190` (AV1R) | recover into a **copy** of the artefact; **rebind nothing** |
| the semantic definition of the quantity | `av2r_xf.py:155`, key path `daOptions["adjEqnOption"]["gmresRelTol"]` | the successor cannot quietly redefine what the quantity is |
| the md5 pin for source **F** | the frozen producer's **own** `PRODUCER_MD5` constant | the successor cannot quietly pin a different `runScript` — AVWC's rule of deriving candidates from the frozen module's own constant |

**THE HONEST GAP, STATED RATHER THAN GLOSSED:** a search of `cases/`, `scripts/` and
`verification/` found **no existing reader anywhere in this repository that recovers
`gmresRelTol` from disk**. Every other occurrence is either a `runScript` literal or the
producer-side expression at `av1_x.py:139` / `av1r_x.py:139` / `av2_xf.py:155` /
`av2r_xf.py:155`. So `av2rg_reader.py`'s three source readers are the **first** disk-side
implementation, and this document does not claim an adoption that does not exist. What is
adopted is the **rule** they are governed by, and it is adopted from the frozen module
itself.

**Agreement is EXACT.** The frozen grader compares with `!=` because *"a different tolerance
is a different band"*. A reader that reconciled near-equal sources would be choosing a band,
which is the one thing a successor may not do. **A missing source is a refusal, not a vote.**

## 6. PRESERVED ROOT IS NEVER WRITTEN — AND IT IS ASSERTED, WITH THE METHOD NAMED

Every run and every plant works on a `cp -a` **copy** in scratch. Before and after each
re-grade the comparator takes an **md5 manifest of every regular file** in the preserved root
(`/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality`, **378 regular files,
25.7 MB**, counted at this freeze) and **REFUSES** (`PRESERVED_ROOT_MUTATED`, naming the
moved paths) if a single hash moves. **It reads the disk, not git** — a run root is not in
git, so a git-based cleanliness check is blind to exactly the thing being protected.

## 7. REFUSAL SET

1. Frozen grader md5 ≠ registered. 2. Frozen producer md5 ≠ registered. 3. Preserved root
absent. 4. Rebind audit: rebound names ≠ `()`. 5. Any registered source absent or
unparseable. 6. The arm's `runScript` md5 ≠ the frozen producer's own `PRODUCER_MD5`.
7. The three sources disagree. 8. The repair not visible on read-back from disk.
9. Preserved-root manifest moved. 10. Verdict outside the fixed vocabulary. 11. `ast.Assert`
count non-zero in either successor file (L-332).
**Every refusal of the FROZEN grader is passed through unchanged and reported as
`NOT A RESULT` with its clause**, and every refusal raised by the repair is raised through
**the frozen module's own `refuse()`**.

## 8. BIRTH REQUIREMENT — BOTH DIRECTIONS, REAL PATH, AND THE MUST-FLAG DIRECTION IS THE POINT

A repaired reader's entire risk is that it **launders a genuine absence into a `PASS`**.
Every plant travels real preserved files, the real recovery reader and the real frozen
grader; none is driven in a mock.

| unit | direction | plant | required |
|---|---|---|---|
| U1–U4 | reader in isolation | none — the real preserved files | all three sources read `1e-06` on **X-S and independently on X-P** |
| U5–U6 | **MUST-NOT-flag** | none | the `G-DP gmresRelTol_in_artefact null` refusal is **gone**; the repaired field is visible on disk where the preserved artefact has no key at all |
| U7 | audit | — | rebound set **exactly** `()` |
| U8 | audit | — | preserved root byte-identical, 378 files |
| U9 | audit | — | verdict in the fixed vocabulary |
| U10 | **MUST-FLAG** | all three sources removed from X-S | still **REFUSED**, `gmresRelTol_source_absent` |
| U11 | **MUST-FLAG** | source **R** alone removed | **REFUSED** — there is **no two-of-three vote** |
| U12 | **MUST-FLAG** | source **C** alone removed (echo stripped from the log copy) | **REFUSED** — proves the log is genuinely read |
| U13 | **MUST-FLAG** | source **F** alone removed | **REFUSED** |
| U14 | **MUST-FLAG** | `1e-5` planted into source **R** alone | **REFUSED** on `gmresRelTol_sources_disagree`, all three values printed — proves all three are read |
| U15 | **MUST-FLAG** | one byte appended to X-S's `runScript` | **REFUSED** on `gmresRelTol_runscript_md5_moved`, **before** any value is parsed |
| U16 | **MUST-FLAG, the laundering test** | after the repair, `identity.gmresRelTol` overwritten to `1e-5` | the **frozen grader's own** clause `av2r_grade.py:511-513` fires, `gmresRelTol_in_artefact` reads `1e-05`, verdict `NOT A RESULT` |
| U17 | **MUST-FLAG, the gate can still fail** | after the repair, `CD/shape[3]` reverse total **doubled** — five orders outside the frozen band `1.0e-5` | the item does **NOT** read `PASS` (see the registered conditional below) |
| U18 | audit | — | preserved root byte-identical after **all nine** re-grades |

**⚠ A CORRECTION TO THE ASSIGNING BRIEF, MADE BEFORE THE FREEZE.** The brief specifies that
the plant *"value present but OUTSIDE the band must **`GATE FAIL`**, not `PASS`"*. **That is
not what the frozen code does and the registration follows the frozen code.** A
`gmresRelTol` that is present but not `1e-6` hits `av2r_grade.py:511-513`, which is a
**refusal**, so the frozen instrument's outcome is `NOT A RESULT`, not `GATE FAIL` (U16). The
`GATE FAIL` direction the brief is reaching for is registered separately and properly at U17,
where a **reverse total** — not the tolerance — is moved outside the band `DP_BAND = 1.0e-5`.
Registering `GATE FAIL` for U16 would have registered an outcome the frozen code cannot
produce.

**U17's REGISTERED CONDITIONAL, fixed before execution.** If the SHIPPED forward row returns
`MEASURED` components, the frozen `G-DP` reads `GATE FAIL` on the perturbed component or
refuses on it. If that row carries `blocked`, the frozen composition maps the item to
`BLOCKED` (`av2r_grade.py:563-564`). **Either branch satisfies U17; what is forbidden is
`PASS`.** The branch taken is recorded beside the unit. **`blocked_any` was deliberately NOT
read from AV2R's own `FAD` artefacts before this freeze**, so which branch fires is not known
to this lane at the freeze.

**PREDICTION, scored and never adjusted (one only, because one is all this item earns).**
**P1: the re-graded item will not read `PASS`.** AV-2's forward rows on this same case were
`5/5 BLOCKED` with `control_fail false` (`ADJOINT_VERIFICATION_STANDARD.md:186`), and AV2R
inherits the case and the producer; the most likely outcome is therefore `BLOCKED` from the
`FAD` rows. Recorded as a prediction, not a gate — **the item verdict is whatever the frozen
instrument returns**.

**THE SUCCESSOR'S OWN INSTRUMENTS, FROZEN BY MD5 WITH THIS DOCUMENT:**

| file | md5 |
|---|---|
| `cases/dafoam/ladder-a/A1/curriculum_AV2RG/av2rg_grade.py` | **`c26d2fa8a6c834c116eff9f1cd18b14b`** |
| `cases/dafoam/ladder-a/A1/curriculum_AV2RG/av2rg_reader.py` | **`3ea234a97b4b2c7058c9a07dca20f685`** |

The grading path is fixed at this commit; before execution each is hashed against the
committed blob and the run refuses on a mismatch.

**Frozen unit count `EXPECTED_UNITS = 18`**, selftest must pass under `python3` **and**
`python3 -O`, `__pycache__` cleared before each. Frozen modules are imported with
`sys.dont_write_bytecode = True` so importing AV2R's comparator cannot drop a `__pycache__`
into its directory. `EXPECTED_UNITS_GMRES_REL_TOL` (`av2rg_reader.py:52`) is frozen here as
**dimensionless — a relative Krylov residual tolerance**, before execution.

**HOW THE FROZEN CONSTANTS WERE CHECKED WITHOUT EXECUTING THE INSTRUMENT.** Neither
`selftest()` nor `regrade()` has been run. The two files were **syntax-compiled only** and
their `unit()` calls counted **statically by `ast`** (18, matching `EXPECTED_UNITS`), and
`ast.Assert` counted (0 in each). Nothing was executed against the preserved root, and this
item has produced no number. **This is a stricter freeze than AVWC's, which disclosed that
its instrument had been exercised during development; this one has not been.**

## 9. WHAT THIS RE-GRADE MAY NOT CONCLUDE

* **Nothing about the physics, the mesh or the solver.** No solver ran. The verdict is the
  frozen instrument's own, over artefacts it was always able to read once the producer's
  omission was undone.
* **No new gate, threshold, band, cap or label.** All are AV2R's own, frozen at its own
  commit. `DP_BAND`, `GMRES_REL_TOL_REGISTERED`, `NEAR_ZERO_ABS`, `MIN_GRADED`, the caps and
  the composition rule are untouched.
* **Nothing about any defect other than the missing `identity.gmresRelTol`.** If the repaired
  item then refuses on a **different** clause, **that refusal is reported as the verdict** and
  is **not** repaired here — it needs its own registration.
* **Nothing is claimed about AV2**, whose identical refusal is a separate item with a separate
  run root. That AV2 shares this root cause byte-for-byte is **reported to the supervisor as a
  scope question**; widening the sweep is not this lane's call.
* **No FD verdict is quoted** — see §10, which travels with any verdict this item produces.
* **No capability-grid cell moves and no census moves from this item.**
* **A `NOT A RESULT` that stays `NOT A RESULT` is a result and is reported as one.**

## 10. THE CHARTER'S BRIGHT LINE — THE FD TABLE, AND IT DOES NOT STAND WHERE IT IS NEEDED

`DAFOAM_CHARTER.md:24-25`: *"A DAFoam gradient is not a result until a finite-difference table
stands beside it at a step proved to lie in the plateau."* Stated plainly, and it travels with
any verdict this item produces:

1. **AV2R carries no FD table at all**, and says so in its own frozen text —
   `curriculum_AV2R/PREREGISTRATION.md:76` (*"no FD table → no FD verdict is quoted"*) and
   `:156` (*"It carries **no FD table**"*).
2. **An FD table for the same case, the same baseline design point and both rows does exist
   in a sibling item**: `cases/dafoam/ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` §2
   @ `be35dcad` — `CD` wrt `shape` SHIPPED **11.4274 %**, one flip at idx6 (**640.3696 %**),
   `GATE FAIL`; PATCHED **0.03796 %**, zero flips, `PASS`; `CD` wrt `patchV` **0.2442 %** on
   both rows; central, `step_calc=abs`, step `1e-3`, with a trivial-baseline control at
   `1e-8` reading **132.75 %**, `GATE FAIL — as designed`.
3. **But the plateau that step sits in is PER COMPONENT, and it does not cover AV2R's
   registered set.** `cases/dafoam/ladder-a/A_stepsize_study.md` proves a flat curve
   (**2.5–3.0 %, cosine 0.99998, 1e-4 to 3e-2**) only **excluding idx0, idx1 and idx6** —
   *"the real plateau, and it belongs to five of eight components, not to the vector"*
   (`DAFOAM_CHARTER.md:108-111`), and of idx6: *"**There is no step at which idx6 is a
   trustworthy estimate**"* (`A_stepsize_study.md:40`). AV2R registers `shape[0]`,
   `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]`. **Two of its four shape components —
   `shape[0]` and `shape[6]` — lie OUTSIDE the proved plateau**, and `shape[6]` is the
   component AV2R's own prediction P2 (`av2r_grade.py:549`) expects to fail.

**So, for AV2R's registered component set, an FD table at a step proved to lie in the plateau
does NOT stand.** It stands for `shape[3]`, `shape[7]` and `patchV[1]`; it provably does not
for `shape[0]` and `shape[6]`. This is a **separate finding**, it is **not repaired here**,
and it is **reported with any verdict**. Whether it bars AV2R from a `PASS` under
`DAFOAM_CHARTER.md` §1–§2 is **the supervisor's ruling and not this lane's** — noting that
§2's own second clause (*"where a complex-step or forward-AD reference is available, it is the
reference"*, PAS 2019 §5.1: 10 digits forward-AD against 3–4 digits FD) is the argument on the
other side, and that AV2R **is** that forward-AD reference.

## 11. COST (rule 12; `COMPUTE_BUDGET_CHARTER.md` §5)

**Solver compute: ZERO core-minutes.** No mesh, no solve, no container, no GPU.
`verification/queue/` is not opened and nothing is enqueued.

| | |
|---|---|
| Registered estimate | **2.50 core-min**, **ranks = 1** throughout (10 `cp -a` copies of a 25.7 MB / 378-file root, 20 md5 manifests of that root, 10 frozen `grade()` calls, two selftest passes) |
| Cap | **8.00 core-min.** An overrun **stops the item**; it does not get a new budget |
| Rate | **$0.0513 / core-h**, c7a.4xlarge, owner-stated 2026-08-21/22 |
| Dollars, estimate | **$0.002138 — DERIVED, NOT MEASURED** |
| Dollars at cap | **$0.006840 — DERIVED, NOT MEASURED** |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Disk | ≈ 260 MB transient in the session scratchpad, deleted on completion. **No record here cites a scratch path** (L-186) |

A calibration row is owed in `docs/COST_CALIBRATION.md` at completion, with its id
**re-derived at commit time in the same shell invocation**.

## 12. RULE-2 CONDITION — the run directory that does not exist, and how it was checked

Checked at this freeze, 2026-08-30, on the disk:

* `ls -d /home/ubuntu/certonomous-runs/*AV2RG*` → **0 entries**.
* `ls -d /home/ubuntu/Certonomous/verification/runs/*AV2RG*` → **0 entries**.
* `ls cases/dafoam/ladder-a/A1/curriculum_AV2RG/` → **exactly** `av2rg_grade.py`,
  `av2rg_reader.py` and this document. No re-grade JSON, no `RESULTS.md`, no evidence file
  exists.
* `ls -a cases/dafoam/ladder-a/A1/curriculum_AV2R/ | grep -c pycache` → **0**: importing the
  frozen module has not yet happened and has left nothing behind.

**No such run directory will ever exist**: this item registers **no solver arm**. Its output
is a re-grade JSON and a selftest evidence file beside this document, and the gates close the
moment the comparator is first executed against the preserved root.

## 13. WHAT LANDS, AND WHAT DOES NOT

Lands after execution: `RESULTS.md` here, the re-grade JSON, the selftest evidence, and one
`docs/COST_CALIBRATION.md` row.

**Does not land from this lane:** any edit to AV2R's frozen files (rule 6) — a departure would
be a dated amendment appended at the foot with a version bump and *"lines whose number changed
above this section: 0"* proved by byte comparison, and none is proposed; any edit to AV2R's
`RESULTS.md` body — an appended successor note is the **supervisor's** call and this lane
proposes wording only; any repair of a defect outside this root cause; any widening of the
sweep to AV2. **Nothing is sent, filed, uploaded, registered, posted or commented outside this
box** (rule 7).

**Execution is withheld.** This document and its two instruments are frozen and committed and
the lane stops. The pre-compute gate is the supervisor's: the comparator diff read personally
as a diff, and the freeze commit confirmed to exist. Neither is delegable and neither is
claimed here.
