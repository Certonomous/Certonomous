# Curriculum item AV-1 — np-invariance of the DAFoam adjoint on A1's NACA0012 mesh: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-27 by lane A of the DAFoam team.** The governing document is `PREREGISTRATION.md`
in this directory, frozen before any container started at commit **`0b3ebaa4`**. **This file does not
revise the pre-registration.** No gate, threshold, cap, band edge or label was altered by this lane,
and **no grader or instrument was edited** — the defect described in §3 is reported, not repaired.

**Launched by the queue-runner daemon with no agent alive** — `verification/queue/LAUNCH_LOG.tsv`
row `2026-08-27T13:38:13Z dafoam AV1_chain 777576 777576 4 19.3 0b3ebaa4…`.

---

# 1. Item verdict: `NOT A RESULT`

The frozen comparator `av1_grade.py` **REFUSED (exit 2)** at gate G1 and printed its own label:

    REFUSAL: {"REFUSE": "G1", "detail": {"age_reference_absent":
      "/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv/X1-S/0/U"}} -> NOT A RESULT

**No row verdict is quoted. No G-NP number is quoted. No spread, no sign count, no divergence.** The
item's own composition rule (§3, frozen) is *"any refusal → `NOT A RESULT`"*, and this record honours
it. A refusal is a result to report, not a condition to route around.

**All seven arms ran to completion and every physics artefact is intact.** The refusal is not about
the solve. §3 says exactly what it is about.

## 2. The grading path, verified

`av1_grade.py` on disk hashes **`87f15e05130cfdb3cbf195d1daba6154`**, identical to the committed blob
at the freeze commit `0b3ebaa4`; so do `PREREGISTRATION.md`, `av1_x.py`, `av1_run_arm.sh`,
`av1_chain_driver.sh`, `av1_runScript.py`, `av1_aggregate_memory.py` and both `av1_decomposeParDict_np*`
— nine of nine MATCH. Re-run by this lane on the registered invocation
(`python3 av1_grade.py --root /home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv --out …`),
the grader returned **json byte-identical** to the in-chain
`AV1_grade_20260827T135029Z.json`, exit 2, the same refusal. **The refusal is reproducible on the
frozen path.**

## 3. Why it refused — established from disk, and it is NOT physics

G1's age guard is registered as *"artefact strictly newer than the arm's own `.av1_age_datum`; **`0/U`**,
or `0.orig/U` for MESH, touched last at stage"* (`PREREGISTRATION.md` §3). The code fixes that
reference at `av1_grade.py:73`:

    DATUM_REF = {a: ("0.orig/U" if a == "MESH" else "0/U") for a in ARMS_REQUIRED}

**The NACA0012 incompressible tutorial runs with `writeCompression on`** (`base/system/controlDict:27`).
On a **serial (np = 1) arm**, the solver rewrites the time-0 field back to disk **compressed**, replacing
`0/U` with `0/U.gz`. On a parallel arm the fields are written under `processor*/` and `0/U` is never
touched. Measured, on this run root:

| arm | ranks | `0/U` present | `0/U.gz` present | `.av1_age_datum` | field mtime | age guard's substance |
|---|---|---|---|---|---|---|
| X1-S | 1 | **no** | yes | 1787838035 | `0/U.gz` 1787838086 | **satisfied** — 51 s newer |
| X1-P | 1 | **no** | yes | 1787838366 | `0/U.gz` 1787838420 | **satisfied** — 54 s newer |
| X2-S | 2 | yes | no | 1787838162 | `0/U` 1787838162 | reference intact |
| X4-S | 4 | yes | no | 1787838269 | `0/U` 1787838269 | reference intact |
| X2-P, X4-P | 2, 4 | yes | no | — | — | reference intact |

**The guard's substance is satisfied on every refused arm — the artefact IS strictly newer than the
datum. Only the reference PATH vanished, by compression.** The grader iterates arms in registered
order and X1-S is the first solver arm, so the chain refused on its first check.

**This is a defect in the frozen comparator's age-datum reference, present at the freeze, and it bites
only at np = 1.** It is recorded here as a finding and is **not repaired by this lane**: after first
compute the gates are closed, and a comparator repair is the four-condition exception of
`VERIFICATION_CHARTER.md` §2d.1 — the supervisor's ruling, not a lane's. **The frozen file is
untouched.**

Under `CLAUDE.md` rule 4 and this item's own L-342 field classes the `age_guard` is a **physics** field,
and an absent physics field REFUSES. The grader did what it was frozen to do. The verdict stands.

## 4. What ran — the state of the compute, so the refusal is read correctly

Seven of seven arms `rc = 0` from `docker inspect .State.ExitCode`, `OOMKilled false` on all seven,
`chain=COMPLETE` at `20260827T135029Z`. Toolchain per arm as registered: MESH/X1-S/X2-S/X4-S on
`dafoam/opt-packages:latest`, X1-P/X2-P/X4-P on `dafoam-idwarp-rot:v1`.

| arm | row | ranks | wall s | core-min | cap | cpuset |
|---|---|---|---|---|---|---|
| MESH | SHIPPED | 1 | 10 | 0.167 | 5.0 | 0,1 |
| X1-S | SHIPPED | 1 | 61 | 1.017 | 10.0 | 0,1 |
| X2-S | SHIPPED | 2 | 41 | 1.367 | 15.0 | 0,1 |
| X4-S | SHIPPED | 4 | 31 | 2.067 | 20.0 | 0,1,12,15 |
| X1-P | PATCHED | 1 | 61 | 1.017 | 10.0 | 0,1 |
| X2-P | PATCHED | 2 | 42 | 1.400 | 15.0 | 0,1 |
| X4-P | PATCHED | 4 | 31 | 2.067 | 20.0 | 0,1,12,15 |
| **total** | | | | **9.102** | 95.0 | |

Twelve artefacts exist and are non-empty — `av1_X.json` and `av1_X_planted.json` in each of the six
solver arms — each carrying `CD_baseline`, `CL_baseline`, `adjoint`, `baseline_dvs`, `identity`,
`nprocs`, `partition` and `plant`.

**No gate reading is quoted from them, and none of P1–P7 is scored**, because the comparator that is
entitled to read them refused. Two ledger figures are stated as raw readings and explicitly **not** as
prediction outcomes: the np = 4 / np = 1 SHIPPED core-minute ratio is **2.067 / 1.017 = 2.03**, and the
total graded core-min is **9.102**. P4 and P5 remain **unscored**.

## 5. Predictions

**All seven predictions P1–P7 are `NOT_MEASURED`.** The comparator refused before scoring any of them,
and this lane does not score a prediction the frozen instrument did not.

## 6. What this item establishes, and what it does not

**It establishes** nothing about np-invariance. That is the whole point of the entry above: an adjoint
graded against itself across rank counts needs a comparator that will read the artefacts, and this one
refused.

**It establishes one thing about the lab's own instruments**, and it is worth the spend: **a
completion guard whose reference is a bare field path is not robust to `writeCompression`, and the
failure mode is invisible in every parallel arm and fatal in every serial one.** AV-2, registered
entirely at np = 1, refused for exactly the same reason on the same night. That is a two-item,
one-cause finding and it belongs in the docket.

## 7. Cost — actual against the frozen estimate, and the waste named

| arm | predicted point | actual core-min | ratio |
|---|---|---|---|
| MESH | 0.3 | 0.167 | 0.557 |
| X1-S / X1-P | 2.5 each | 1.017 / 1.017 | 0.407 / 0.407 |
| X2-S / X2-P | 3.0 each | 1.367 / 1.400 | 0.456 / 0.467 |
| X4-S / X4-P | 4.0 each | 2.067 / 2.067 | 0.517 / 0.517 |
| **total** | **19.3** | **9.102** | **0.472** |

Gross = cleaned; no arm near the 3,600-s stall figure. **$0.0078 DERIVED, NOT MEASURED** at
$0.0513/core-h, c7a.4xlarge, `cost_basis` REPORTED-BY-OWNER (`COMPUTE_BUDGET_CHARTER.md` §5).
Predicted $0.0165 DERIVED.

**WASTE: 9.102 core-min = $0.0078 DERIVED — the ENTIRE spend, named separately and never absorbed into
the ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). Seven arms ran correctly and bought **no graded number**,
because the comparator's own age reference could not survive the tutorial's `writeCompression` setting
at np = 1. The cause is named, it is not contention, and it is not the solver.

**Gap attribution on the ratio itself: misprediction of parallel scaling, in the lab's favour.** §4
assumed parallel efficiency 0.8 at np = 2 and 0.6 at np = 4, giving 3.0 and 4.0 core-min against an
np = 1 point of 2.5. Measured: np = 1 cost **1.017** (0.41 of its point — C-31's 1.483 figure covered
one primal + one adjoint, and this arm's second CL adjoint proved much cheaper than the +0.7 assumed);
np = 2 **1.367** and np = 4 **2.067**, i.e. **efficiency 0.74 at np = 2 and 0.49 at np = 4**, close to
the assumed 0.8/0.6 as *ratios* while the base was 2.5× too high. **Carry forward: the np-scaling model
was good; the np = 1 anchor was not.** Price a cold primal + two adjoints on A1's 4,032-cell mesh at
np = 1 at **1.0 core-min**, not 2.5.

The calibration row is `C-158` in `docs/COST_CALIBRATION.md`.

## 8. What is owed, and to whom

The comparator repair is **the supervisor's ruling under `VERIFICATION_CHARTER.md` §2d.1**, and a
re-fire of the arms — if one is even needed, since the artefacts are intact — is the supervisor's call
with its own cost. **This lane has proposed neither and edited neither.** The finding, the evidence
paths and this record are what the lane hands over.

## 9. Artefacts, all still on disk

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv/`:
`AV1_grade_20260827T135029Z.json` and `.out` (the refusal), `ledger.txt` (7 `ARM=` rows),
`STATUS.chain` and the seven per-arm `STATUS.*`, per-arm `*.inspect.txt` kernel records,
`X{1,2,4}-{S,P}/av1_X.json` and `av1_X_planted.json`, per-arm `.av1_age_datum`, solver logs and
memory windows.

---

## Amendment record — v1.0 to v1.1, 2026-08-30T22:51Z: THE REFUSAL RECORDED ABOVE IS SUPERSEDED BY `AVWC`, AND THE BODY ABOVE IS UNCHANGED

**Rule 6 assertion: lines whose number changed above this section: 0.** This is an APPEND at the foot
and nothing above it was edited. Proved by byte comparison, not asserted: the block was landed through
`scripts/append_block.py`, which reads the body from a file as bytes so no shell ever sees it, and
which compares the file's prefix byte-for-byte against the pre-append bytes and REVERTS on any
difference. The pre-append file hashed md5 `626b6415af42ee961a40f64e6541465a`, identical to
`git show HEAD:cases/dafoam/ladder-a/A1/curriculum_AV1/RESULTS.md` at the time of writing, and that
same prefix is intact below the amendment. **Version: this record was previously unversioned (v1.0
implied); it is v1.1 as of this amendment.** No gate, threshold, band edge, cap or label above is
altered, and no figure above is restated as a different number.

**What is superseded, precisely.** §1 above records this item's verdict as `NOT A RESULT` on
`G1 age_reference_absent .../X1-S/0/U`, and §3 identifies the cause as the age-datum reference not
surviving the tutorial's `writeCompression on` at np = 1. **That diagnosis was correct and is
confirmed.** What has changed is that the defect has since been repaired in a successor item and the
item re-graded from this same preserved run root.

**The successor's result: `PASS`.** Item `AVWC`
(`cases/dafoam/ladder-a/A1/curriculum_AVWC/`), pre-registration frozen at commit `c85eb4df`
2026-08-28T17:47:02Z before execution, re-graded AV1 from the preserved root
`/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv/` through a repaired reader and
returned **`PASS`**, with rows `SHIPPED PASS` and `PATCHED PASS`. Source:
`cases/dafoam/ladder-a/A1/curriculum_AVWC/AVWC_regrade.json` and `RESULTS.md` §1.

**Three things about that successor verdict that this record is entitled to state:**

1. **AV1 carried BOTH manifestations of the one root cause, not just the datum one.** §3 above names
   the datum reference. Measured by the successor: repairing only the datum advances AV1 from
   `G1 age_reference_absent` to `G-NP partition_cells [null, null] sum 0` against `mesh_cells 4032` —
   one `NOT A RESULT` to another — because the PRODUCER `av1_x.py:75-87` also stats an uncompressed
   `processorN/constant/polyMesh/owner` when the file on disk is `owner.gz`. Both repairs were needed.
2. **No gate was re-implemented and no frozen file here was edited.** The successor imports this
   item's own `av1_grade.py`, verifies it byte-identical to the committed blob
   (md5 `87f15e05130cfdb3cbf195d1daba6154`, re-checked at every invocation as a refusal clause),
   rebinds exactly one name — `arm_datum` — under a rebind audit that refuses on any other name, and
   runs the frozen `grade()`. Every band, threshold and composition rule that produced the `PASS` is
   the frozen code above, unedited on disk.
3. **The repaired reader was proved able to REFUSE before that `PASS` was accepted.** Five must-flag
   plants travelling the real preserved files and the real frozen grader all fired: neither datum name
   on disk, a compressed twin planted older than the datum, an uncompressed `0/U` planted with a wrong
   mtime, `owner.gz` deleted from a processor, and `nCells` rewritten inside the real gzip. Five of
   five, on five distinct clauses, in two independent readings.

**This preserved run root was never written.** An md5 manifest of every regular file in it was taken
before and after each re-grade and compared; it is byte-identical, 754 files, on every invocation.
The successor grades a `cp -a` copy, which matters because the frozen grader at
`av1_grade.py:274-291` is itself a WRITING grader.

**What this amendment does NOT do.** It does not revise §1's verdict as the verdict this item
produced: `av1_grade.py` refused, and on this item's own frozen path it still refuses. It does not
move a gate, a band, a cap, a label, a capability-grid cell or a census row. It does not restate any
cost figure in §7, and `C-158` stands as landed. It makes no claim about the physics, the mesh or the
solver — no solver ran for the re-grade, which cost zero solver core-minutes.
