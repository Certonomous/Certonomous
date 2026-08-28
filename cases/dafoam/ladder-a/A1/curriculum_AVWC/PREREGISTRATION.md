# AVWC — PRE-REGISTRATION (FROZEN). The `writeCompression` cluster: AV1, AV2, AV1R

**Item:** `AVWC` — successor re-grade of **three** curriculum items from their **preserved
run roots**, through readers repaired for **one root cause**.
**Team:** dafoam. **Lane:** AA. **Date:** 2026-08-28.
**Solver compute: ZERO.** Nothing meshed, nothing solved, no container, no GPU.
**Provenance:** Phase 2 of Sanaa's ordered re-grade sweep
(`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md` §2),
cluster assigned by the dafoam supervisor 2026-08-28. **AV1 and AV2 are in scope by the
supervisor's ruling that the sweep is by DEFECT, not by Sanaa's starting list of seven.**

---

## 1. THE ROOT CAUSE, ONE SENTENCE

**A reader that stats an UNCOMPRESSED filename when `writeCompression on` has written the
`.gz`.** Read, not assumed: `writeCompression` is `on` in the arm's own
`system/controlDict` and this comparator reads it there and records it beside every
resolution.

**Two manifestations.**

| variant | defective reader | what it produced |
|---|---|---|
| **DATUM** | `av1_grade.py:198-200`, `av2_grade.py:186-188` — `DATUM_REF = "0/U"`, `os.path.isfile()` | `G1 age_reference_absent` → `NOT A RESULT`, every physics artefact intact |
| **PARTITION** | `av1_x.py:75-87` and `av1r_x.py:75-87` — **THE PRODUCER**, stats `processorN/constant/polyMesh/owner` | `nCells: null` per processor → the grader refuses `G-NP partition_cells [null, null], sum 0` against `mesh_cells 4032` |

**The two producer functions are BYTE-IDENTICAL** (`diff` of `av1_x.py:75-87` against
`av1r_x.py:75-87` is empty): AV1R inherited the defect verbatim.

## 2. ⚠ A CORRECTION TO THE ASSIGNING BRIEF, MADE BEFORE THE FREEZE

The brief assigns *"AV1R — the partition variant; AV1 and AV2 — the age datum"*.
**Measured, and it is wrong for AV1.**

* **AV1 carries BOTH manifestations.** Repairing only the datum advances AV1 from
  `G1 age_reference_absent` to `G-NP partition_cells [null, null] sum 0` — **one
  `NOT A RESULT` to another.** AV1 has `np = 1, 2, 4` arms (`av1_grade.py:69`) and its
  `X2-*`/`X4-*` artefacts record `nCells: None`.
* **AV2 is datum-only, and for a reason worth stating:** every AV2 arm is serial
  (`av2_grade.py:59`, `ARM_RANKS` all 1). It has no `processor*` directory at all, so the
  PARTITION manifestation cannot reach it.
* **AV1R is partition-only**: its datum variant was already repaired in-item at
  `av1r_grade.py:83` (`DATUM_REF_CANDIDATES`).

So `repairs` is registered as a **set per item**, not a single kind. Registered:
**AV1 = {DATUM, PARTITION}, AV2 = {DATUM}, AV1R = {PARTITION}.**

## 3. HOW IT RE-GRADES — IT RE-IMPLEMENTS NO GATE

For each item the successor imports **that item's own frozen comparator**, verifies the
file on disk is byte-identical to the committed blob, **rebinds at most ONE name** in the
imported module, and runs **the frozen `grade()`**. Every band, threshold, composition
rule, planted control and refusal clause that decides the verdict is **literally the frozen
code, unedited on disk**.

| item | frozen comparator (md5, disk == HEAD blob verified at execution) | names rebound |
|---|---|---|
| AV1 | `av1_grade.py` `87f15e05130cfdb3cbf195d1daba6154` | **`arm_datum`** (1) |
| AV2 | `av2_grade.py` `4bde0ad7dbdd3e460dcef1fe6d063979` | **`arm_datum`** (1) |
| AV1R | `av1r_grade.py` `b5c1d0092c6d2a2608ad3cc0899ed0fd` | **none (0)** |
| AV1 producer | `av1_x.py` `74011a9c5e6c760b8aec1c78e928b4d2` | read-only |
| AV1R producer | `av1r_x.py` `7313bab8b15629c9d872a39d0654aa08` | read-only |

**`AV1R'S GRADER IS NOT DEFECTIVE AND IS NOT MODIFIED.** It refused on absent data, which is
the correct behaviour. The defect is upstream in the producer, so AV1R is repaired by running
the adopted producer reader over the **preserved** processor directories and writing the
recovered record into a **copy** of the artefact.

**The rebind is audited, not asserted.** The comparator fingerprints every callable in the
imported module before and after, diffs the fingerprints, and **REFUSES** if the set of
rebound names is not exactly the registered set.

## 4. NO FOURTH IMPLEMENTATION — BOTH READERS ARE ADOPTED

| repaired reader | adopted from | the part that is easy to lose and is preserved |
|---|---|---|
| `resolve_datum()` | `curriculum_SO1a/so1a_grade.py:292-338` (`resolve_datum_ref`) + `:277-290` (`read_write_compression`) | **the mtime rule follows the file that was FOUND**: the UNCOMPRESSED name is the one the launcher touched and must still carry the datum **exactly**; the COMPRESSED twin was written by the solver **after** and may only be **newer**. Losing that asymmetry turns a repaired guard into no guard |
| `partition_record()` | `curriculum_D12R2/d12y_w3_stage_and_run.sh:799-808` (`for cand in ("owner", "owner.gz")`, `gzip.open` when `.gz`) — the same loop as `d12y_stage_and_run.sh`, `d12y_w2_stage_and_run.sh`, `d12y_w2r_stage_and_run.sh` | a processor whose `owner` is unreadable in **either** name yields `nCells: None`; the reader reports what it could not read and lets the **frozen** grader refuse |

The candidate list is **derived from the frozen module's own `DATUM_REF`**, so candidate[0]
is always exactly what the frozen document registered; the successor cannot quietly
re-register a different reference. Refusals are raised through **the frozen module's own
`refuse()`**, so the successor never invents a refusal vocabulary.

## 5. PRESERVED ROOTS ARE NEVER WRITTEN — AND IT IS ASSERTED, WITH THE METHOD NAMED

Every item and every control runs on a `cp -a` **copy** in scratch. Before and after each
re-grade the comparator takes an **md5 manifest of every regular file** in the preserved
root and **REFUSES** (`PRESERVED_ROOT_MUTATED`, naming the moved paths) if a single hash
moves. **It reads the disk, not git** — a run root is not in git, so a git-based cleanliness
check is blind to exactly the thing being protected.

## 6. REFUSAL SET

1. Frozen grader md5 ≠ registered. 2. Frozen producer md5 ≠ registered. 3. Preserved root
absent. 4. Rebind audit: rebound names ≠ registered names. 5. A repair asked for that the
item does not register. 6. Preserved-root manifest moved. 7. Verdict outside the fixed
vocabulary. 8. `ast.Assert` count non-zero in either successor file (L-332).
**Every refusal of the FROZEN graders is passed through unchanged and reported as
`NOT A RESULT` with its clause.**

## 7. BIRTH REQUIREMENT — BOTH DIRECTIONS, REAL PATH

A repaired reader's entire risk is that it **launders a genuine absence into a pass**, so
the MUST-FLAG direction is the point here, not decoration. Every plant travels real
preserved files, the real adopted reader and the real frozen grader.

| direction | plant | required |
|---|---|---|
| **MUST-NOT-flag** (DATUM) | none — the real preserved roots | resolves `0/U.gz`, the `age_reference_absent` refusal is **gone** |
| **MUST-FLAG** (DATUM) | neither `0/U` nor `0/U.gz` on `X1-S` | still **REFUSED**, on `age_reference_absent_in_every_registered_name` |
| **MUST-FLAG** (DATUM) | compressed twin planted **older** than the datum | **REFUSED** on `compressed_datum_twin_older_than_the_datum` — the guard's substance survives |
| **MUST-FLAG** (DATUM) | an uncompressed `0/U` planted beside the real `.gz` with a wrong mtime | candidate[0] wins, **REFUSED** on `age_reference_moved` — ordering and the uncompressed branch both proved live |
| **MUST-NOT-flag** (PARTITION) | none — the real preserved roots | 2016+2016 and 1008×4, sum **4032** |
| **MUST-FLAG** (PARTITION) | `owner.gz` deleted from one processor | `nCells: None` → the **frozen** grader refuses |
| **MUST-FLAG** (PARTITION) | `nCells` rewritten **inside the real gzip** | sum ≠ 4032 → the **frozen** grader refuses — proving the reader reads the **file**, not a constant |

**THE SUCCESSOR'S OWN INSTRUMENTS, FROZEN BY MD5 WITH THIS DOCUMENT:**

| file | md5 |
|---|---|
| `cases/dafoam/ladder-a/A1/curriculum_AVWC/avwc_grade.py` | **`6e390f8f3c0df5d4229dd3640590ca44`** |
| `cases/dafoam/ladder-a/A1/curriculum_AVWC/avwc_reader.py` | **`1a7f3f211f44c7b67b4f8f2d4c65bf4a`** |

The grading path is fixed at this commit; before execution each is hashed against the
committed blob and the run refuses on a mismatch.

**Frozen unit count `EXPECTED_UNITS = 20`**, selftest must pass under `python3` **and**
`python3 -O`, `__pycache__` cleared before each. Producers are imported with
`sys.dont_write_bytecode = True` so importing a frozen case's comparator cannot drop a
`__pycache__` into its directory.

## 8. WHAT THIS RE-GRADE MAY NOT CONCLUDE

* **Nothing about the physics, the mesh or the solver.** No solver ran. The verdicts are the
  frozen instruments' own, over artefacts those instruments were always able to read.
* **No new gate, threshold, band, cap or label.** All are the frozen items' own.
* **Nothing about any defect other than `writeCompression`.** If a repaired item then
  refuses on a **different** clause, that refusal is **reported as the verdict** and is
  **not** repaired here — it needs its own registration.
* **Nothing is claimed about AV2R**, whose refusal is a different defect entirely.
* **No capability-grid cell moves and no census moves from this item.**
* **A `NOT A RESULT` that stays `NOT A RESULT` is a result and is reported as one.**

**Honest disclosure (as at `curriculum_D18R_P7/PREREGISTRATION.md` §4):** the instrument was
exercised during development, so this is not an outcome-blind freeze and does not claim to
be. What the freeze buys is the **repair semantics**, the **repairs set per item**, the
**rebind audit**, the **refusal set**, the **unit count** and the **both-directions
controls** — all fixed and committed before the recorded execution.

## 9. COST (rule 12; `COMPUTE_BUDGET_CHARTER.md` §5)

**Solver compute: ZERO core-minutes.** No mesh, no solve, no container, no GPU. The live D6R
chain at 4 ranks is not disturbed and `verification/queue/` is not touched.

| | |
|---|---|
| Registered estimate | **3.00 core-min**, ranks = 1 throughout (≈ 12 `cp -a` copies of ≈ 20 MB roots, ≈ 24 md5 manifests of ≈ 750 files each, ≈ 12 frozen `grade()` calls, two selftests) |
| Cap | **10.00 core-min.** An overrun **stops the item**; it does not get a new budget |
| Rate | **$0.0513 / core-h**, c7a.4xlarge, owner-stated 2026-08-21/22 |
| Dollars, estimate | **$0.002565 DERIVED**, not measured |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Disk | ≈ 240 MB transient in the session scratchpad, deleted on completion. **No record here cites a scratch path** (L-186) |

A calibration row per item is owed in `docs/COST_CALIBRATION.md`, with ids **re-derived at
commit time in the same shell invocation** — a peer landed two rows inside an eleven-minute
window earlier today.

## 10. RULE-2 CONDITION — the run directory that does not exist

Checked at this freeze, 2026-08-28:

* `ls -d /home/ubuntu/certonomous-runs/*AVWC*` → **0 entries**.
* `ls -d /home/ubuntu/Certonomous/verification/runs/*AVWC*` → **0 entries**.
* `cases/dafoam/ladder-a/A1/curriculum_AVWC/` contains **only** `avwc_reader.py`,
  `avwc_grade.py` and this document. No `AVWC_regrade.json`, no `RESULTS.md`, no evidence
  file exists yet.

**No such run directory will ever exist**: this item registers **no solver arm**. Its output
is a re-grade JSON and an evidence file beside this document, and the gates close the moment
the comparator is first executed against the preserved roots.

## 11. WHAT LANDS, AND WHAT DOES NOT

Lands: `RESULTS.md` here, the re-grade JSON, the selftest evidence, and one
`docs/COST_CALIBRATION.md` row.

**Does not land from this lane:** any edit to AV1's, AV2's or AV1R's frozen files (rule 6);
any edit to their `RESULTS.md` bodies — an appended successor note is the **supervisor's**
call and this lane proposes wording only; any repair of a defect outside this root cause.
**Nothing is sent, filed, uploaded, registered, posted or commented outside this box** (rule 7).
