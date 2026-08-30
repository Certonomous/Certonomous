# Curriculum item AVWC — the `writeCompression` cluster (AV1, AV2, AV1R) re-graded from preserved run roots: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-30 by a lane of the DAFoam team.** The governing document is `PREREGISTRATION.md`
in this directory, frozen at commit **`c85eb4df`** (2026-08-28T17:47:02Z) **before** the comparator
was executed. **This file does not revise the pre-registration.** No gate, threshold, cap, band edge
or label was altered by this lane, and **no frozen file of AV1, AV2 or AV1R was edited** — §6 below
proves that by hash.

**SOLVER COMPUTE: ZERO core-minutes.** Nothing was meshed, nothing was solved, no container was
started, no GPU was touched, `verification/queue/` was not opened. Every number below was read from
artefacts that already existed on disk before this lane began.

> **A note on this record's shape, stated rather than left to be inferred.** The assigning brief asked
> for `REPORTING_CHARTER.md`'s six fixed headings. Read in full, that charter's six headings
> (`## 1. SPEND` … `## 6. WAITING LIST`, §2) are **the morning report's**, and §2 rule 1 says they are
> matched literally so that a document carrying them *is* a morning report. A curriculum record with
> `## 5. REFILLED QUEUE` and `## 6. WAITING LIST` would be a malformed morning report, which is the
> single failure that section exists to prevent. This record therefore follows the shape its two
> siblings use — `curriculum_AV1/RESULTS.md` and `curriculum_AV2/RESULTS.md` — and honours
> `REPORTING_CHARTER.md` §10 and §11, which bind any record: no number without its artefact, no label
> the number did not earn, and no curation. The conflict is reported to the supervisor, not resolved
> silently.

---

# 1. Item verdicts

| item | verdict BEFORE (frozen, superseded) | verdict AFTER the repaired reader | repairs applied |
|---|---|---|---|
| **AV1** | `NOT A RESULT` — `G1 age_reference_absent .../X1-S/0/U` | **`PASS`** | `{DATUM, PARTITION}` |
| **AV1R** | `NOT A RESULT` — `G-NP partition_cells [null, null] sum 0` vs `mesh_cells 4032` | **`PASS`** | `{PARTITION}` |
| **AV2** | `NOT A RESULT` — `G1 age_reference_absent .../X-S/0/U` | **`NOT A RESULT`** — refusal **MOVED** to `G-DP`, `gmresRelTol_in_artefact: null` against registered `1e-06` | `{DATUM}` |

Source: `cases/dafoam/ladder-a/A1/curriculum_AVWC/AVWC_regrade.json`.

**Every one of these three verdicts is the FROZEN instrument's own.** The successor re-implements no
gate. For each item it imports that item's own frozen comparator, proves the file on disk is
byte-identical to the committed blob, rebinds **at most one name**, and runs the frozen `grade()`.
AV1R rebinds **nothing at all** — its grader was never defective, and this record does not treat it as
though it were.

**AV2's `NOT A RESULT` is a result and is reported as one** (`PREREGISTRATION.md` §8). It is not
softened, and §4 below establishes that it is a finding about the item's own artefact rather than a
second defect in the repaired reader.

## 2. The re-run after the reboot — the verdicts reproduce, and this is what saves the item

The recorded execution wrote its working copies into the session scratchpad. **The reboot destroyed
them**: `…/scratchpad/laneAA` does not exist. That is `CLAUDE.md` rule 13 charging its fee, and the
only reason the item survived is that the *preserved run roots* live outside the scratchpad and
outside git, and were never written.

This lane re-ran the frozen comparator from a clean state — `__pycache__` cleared before each
invocation, under `python3` and `python3 -O` — into its own working directory, and compared the new
JSON against the recorded one **field by field, recursively, every leaf**:

| reading | result |
|---|---|
| Preserved roots present and readable | **3 of 3** — AV1 754 files, AV1R 755, AV2 378, matching the counts the recorded run wrote |
| Selftest, `python3` | **PASS 20/20** against the frozen `EXPECTED_UNITS = 20`, 0 failures |
| Selftest, `python3 -O` | **PASS 20/20**, 0 failures, `python_O=True` |
| Re-grade, all three items | rc 0; **AV1 `PASS`, AV1R `PASS`, AV2 `NOT A RESULT`** on clause `G-DP:gmresRelTol_in_artefact,note,registered,row` |
| Recursive field comparison, recorded vs re-run | **24 differing leaves, all 24 the transient working-directory path prefix** (`…/avwc_<pid>/root_<ITEM>/`), which carries the process id and cannot repeat |
| The same comparison with that one prefix normalised | **0 differences** |

**Every verdict, every refusal string, every gate reading, every mtime, every
`seconds_newer_than_datum` and every partition sum reproduces exactly.** Decisive fields checked
explicitly and identical on all three items: `verdict`, `refusal`, `repairs_applied`,
`names_rebound`, `root_manifest_identical`, `preserved_root_files`, `frozen_grader_md5`,
`original_refusal`, `preserved_root`.

`AVWC_full_grades.json` was **not regenerated**, because `avwc_dump_full_grades.py` writes that file
in place and would have overwritten the recorded artefact. It was instead cross-checked read-only:
**0 disagreements across 15 shared fields** (5 fields × 3 items) between `AVWC_full_grades.json`,
`AVWC_regrade.json` and this lane's re-run.

Source: `AVWC_regrade.json`, `AVWC_full_grades.json`, `avwc_selftest_evidence.txt`, all in this
directory; the preserved roots named in §7.

## 3. The preserved roots were not mutated — read from the disk, not from git

A run root is not in git, so a `git status` cleanliness check is blind to exactly the thing being
protected. The comparator therefore takes an **md5 manifest of every regular file** in each preserved
root before and after each re-grade and refuses (`PRESERVED_ROOT_MUTATED`) if a single hash moves.

`root_manifest_identical` is **`true` for all three items in the recorded run and true again in this
lane's re-run** — and true on every one of the seven planted runs in §5 as well. `PRESERVED_ROOT_MUTATED`
never fired, on any invocation.

**This is not decoration, and the reason is worth stating.** `av1_grade.py:274-291`
(`grader_plant_control`) **writes** — it creates `<root>/grader_controls/` and plants an artefact
there in order to read it back. The frozen graders are *writing* graders. Running one directly on a
preserved root would mutate it. The copy-then-grade design is what prevents that, and the manifest is
what proves it did. The file counts corroborate: **AV1's preserved root holds 754 files and has no
`grader_controls/` directory at all**, while AV1R's holds 755 — the extra file being
`grader_controls/X_X2S_planted.json` left by AV1R's own in-chain grading on 2026-08-28, present before
this item existed and unchanged by it.

## 4. THE CHECK THAT DECIDES WHETHER THE TWO PASSES LAND

Two of three items moved to `PASS`. That is the flattering direction, and it is exactly where a
repaired reader launders a genuine absence into a pass. The question is not whether the reader
produced a pass; it is whether the reader **was still able to refuse**. It was, on five distinct
clauses, on the real path.

Each plant travels real preserved files, the real adopted reader and the real frozen grader. The
outcomes below are quoted twice: from `avwc_selftest_evidence.txt` (the recorded run) and from this
lane's own independent driver, which imported the frozen module and called `regrade()` with each
plant directly — so the evidence does not rest on the selftest's own bookkeeping.

| plant | required | recorded run | this lane's independent re-run |
|---|---|---|---|
| **neither `0/U` nor `0/U.gz` on `X1-S`** | still REFUSED | `[OK] U17` — clause `G1:age_reference_absent_in_every_registered_name` | **FIRED**, same clause |
| **compressed twin planted OLDER than the datum** | REFUSED on the age asymmetry | `[OK] U18` — clause `G1:compressed_datum_twin_older_than_the_datum,…` | **FIRED**, `recorded 1787838035`, `on_disk 1787837935` — exactly the planted 100 s older |
| **uncompressed `0/U` planted beside the real `.gz` with a wrong mtime** | candidate[0] wins, REFUSED on exact-mtime | `[OK] U19` — clause `G1:age_reference_moved,…` | **FIRED**, `resolved_name "0/U"`, `on_disk 1`, `recorded 1787838035` |
| **`owner.gz` deleted from `X2-S/processor0`** | `nCells: None` → the FROZEN grader refuses | `[OK] U20` (first of two) | **FIRED** — `G-NP`, `partition_cells [null, 2016]`, `sum 2016` vs `mesh_cells 4032` |
| **`nCells` rewritten INSIDE the real gzip on `X4-S`** | sum moves off 4032 → the FROZEN grader refuses | `[OK] U20` (second of two) | **FIRED** — `G-NP`, `partition_cells [1007, 1008, 1008, 1008]`, `sum 4031` |

**Five of five must-flag plants fired, in both readings. Not one was silent.** The registered
`EXPECTED_UNITS` is **20**; units run were **20** under `python3` and **20** under `python3 -O`, with
**0 failures** in each — units run equals 20, the frozen count, in both.

**The plants are non-vacuous, checked on the preserved roots themselves.** A plant that deletes a file
that was never there proves nothing:

* `…CURRICULUM-AV1…/X1-S/0/U` is **ABSENT** and `0/U.gz` is **PRESENT at 112,245 bytes** — so
  dropping both names removes a file the repaired reader genuinely resolves, and planting an
  uncompressed `0/U` creates a candidate[0] that did not previously exist.
* `…CURRICULUM-AV1R…/X2-S/processor0/constant/polyMesh/owner` is **ABSENT** and `owner.gz` is
  **PRESENT at 8,312 bytes** — so deleting it removes the only readable name and creates a real
  absence.

**The control in the other direction was run on the same path**: with no plant, AV1 and AV1R return
`PASS` with `refusal: None`. A reader that refuses on everything is as useless as one that refuses on
nothing; this one does neither.

**The frozen graders' own two controls also fired**, independently of anything this successor did:
`grader_plant_X2S` reports `grader_plant_seen: true`, 20 values, worst residual **1.79e-16**; and
`sign_flipped_X4S_read_as_GATE_FAIL` reports `seen: true`, **20 flips of 20 expected** — the
deliberately wrong transpose is read as a failure. That is `CLAUDE.md` rule 3 satisfied inside the
instrument that issued the verdict, on top of the five plants above.

**On this evidence the two `PASS` verdicts land.** Source: `avwc_selftest_evidence.txt` lines 17–22 and
39–44; `AVWC_full_grades.json` (`grade.controls`); this lane's re-run of the same frozen entry points.

### 4a. The gate readings behind the two passes

Quoted from `AVWC_full_grades.json`, which carries the payload `AVWC_regrade.json` drops for brevity.
Registered bands: `objective_spread_rel 2.2e-05`, `gradient_spread_rel 1.0e-03`, `sign_flips 0`
(`ADJOINT_VERIFICATION_STANDARD.md` §3; `PARALLEL_GATE_DOCTRINE.md:38`).

* **AV1 and AV1R both**: `G1_completion PASS`, `G-M2_mesh_identity PASS`, rows `SHIPPED PASS` and
  `PATCHED PASS`, `mesh_cells 4032`, no cap crossed on any arm (`G10_caps`, `crossed: false`
  throughout).
* Maximum objective spread **7.0775e-09** against the `2.2e-05` band — inside by three and a half
  orders of magnitude.
* **P5 is a `MISS`** on both items — the total core-minute band prediction. It is stated here rather
  than omitted; a record that prints only the hits is a curated record.

**No capability-grid cell moves and no census moves from this item** (`PREREGISTRATION.md` §8), and
nothing here is a claim about the physics, the mesh or the solver. No solver ran.

**One reading checked adversarially because it looked too clean.** AV1 and AV1R report **bit-identical**
`CD 0.02091051000679216` and `CL 0.49876526415423195`. That is not cross-contamination: the two values
were read from two different files in two different preserved roots, written **2026-08-27T13:41:26Z**
and **2026-08-28T07:04:50Z**, by the same producer (`producer_md5` prefix `0557da51`). Two separate
executions of a deterministic case on one machine agreeing to the last bit is a determinism reading,
and it is reported as that and nothing more.

## 5. AV2 — the refusal MOVED, and it is the registered branch, not an artefact of the repair

`PREREGISTRATION.md` §8 registers this branch in advance: *"If a repaired item then refuses on a
DIFFERENT clause, that refusal is REPORTED AS THE VERDICT and is NOT repaired here — it needs its own
registration."* AV2 took exactly that branch. **The verdict is `NOT A RESULT`.**

**Is `gmresRelTol` genuinely absent, or is the reader looking in the wrong place?** It is genuinely
absent, and the distinction was settled by reading the artefact rather than reasoning about it:

* The frozen grader reads `j["identity"]["gmresRelTol"]` at `av2_grade.py:252` and refuses at
  `av2_grade.py:442-443` when it is not the registered `1e-06`.
* In `…CURRICULUM-AV2…/X-S/av2_X.json` the `identity` block **exists** and carries exactly two keys —
  `idwarp_file` and `libidwarp_so_md5`. The string `gmresRelTol` **does not appear anywhere in that
  file at all**. Same for `X-P/av2_X.json` and both `av2_X_planted.json`.
* So the reader is looking in the right place, in a block that is present; the key is simply not in
  it. **This is not a second reader defect.**

**Where the value actually went, read from the producer.** `av2_xf.py:152-155` computes
`ident = idwarp_identity()` and then emits a jsonl record carrying `gmresRelTol` as a **sibling** of
`**ident`, not as a member of it. At `av2_xf.py:203` the final artefact is written with
`"identity": ident` — the bare dict. **The key is emitted to the jsonl stream and never carried into
the `.json` artefact the grader reads.** Corroborated on disk: `X-S/av2_X.jsonl` carries
`"gmresRelTol": 1e-06` and the run log carries `gmresRelTol 1e-06;`, while `X-S/av2_X.json` carries
neither.

**The tolerance actually used is `1e-06`, which is exactly the registered value.** That is stated as a
reading of the jsonl and the log, and it changes nothing: the frozen grader is entitled to read the
artefact it was frozen to read, it found no value there, and it refused. `NOT A RESULT` stands.

**Proof that the repair did not create this condition.** The G-DP clause sits **downstream** of the
datum gate. Before the repair, G1 refused first and G-DP was never reached; after the repair, G1
passes and G-DP is reached for the first time. The repair **exposed** a pre-existing condition, it did
not manufacture one — and the condition is dated: `X-S/av2_X.json` was written **2026-08-26T23:23:14Z**,
two days before this item's freeze, and the preserved root is byte-identical (378 files) before and
after. Nothing this lane ran could have put that key there or taken it away.

**INDEPENDENTLY CONFIRMED BY A PEER LANE THAT DID NOT SEE THIS RECORD.** While this lane was
re-running, a second dafoam lane froze `curriculum_AV2RG` (commit `2f827746`) on the sibling item
**AV2R** and reached the same diagnosis from the same evidence class: its `PREREGISTRATION.md` lines
21-25 name `av2r_xf.py:56-63` returning only `{idwarp_file, libidwarp_so_md5}`, `:203` writing that
dict verbatim as `out["identity"]`, and `:152-156` emitting `gmresRelTol` into the jsonl sidecar **one
statement earlier**. Its line 35 adds the reading this record could not have made alone:
**`idwarp_identity()` is byte-identical between `curriculum_AV2/av2_xf.py` and
`curriculum_AV2R/av2r_xf.py`** — the defect is *inherited*, not local, and it is a two-item defect.
That registration cites this item's `gmresRelTol_in_artefact: null` as its corroboration, so the two
readings are convergent rather than circular: two lanes, two run roots, two producers, one cause.

**A second, independent defect is therefore recorded and NOT repaired here.** It is an artefact-plumbing
defect in `av2_xf.py`, distinct from `writeCompression`, and repairing it needs its own
pre-registration — which is a supervisor's ruling under `VERIFICATION_CHARTER.md` §2d.1, not a lane's.
For contrast, `av1_grade.py` and `av1r_grade.py` contain **zero** occurrences of `gmresRelTol`: the
G-DP clause is AV2-specific (`av2_grade.py:10` — G-NP is replaced by G-DP), which is why AV1 and AV1R
cannot hit it. Nothing was selected.

## 6. The frozen files were never edited — proved by hash, not asserted

Every file hashed on disk against `git show HEAD:<path>`, and the successor's three against the freeze
commit `c85eb4df` as well:

| file | disk md5 | vs freeze `c85eb4df` | vs `HEAD` |
|---|---|---|---|
| `curriculum_AVWC/PREREGISTRATION.md` | `81d120a7ddb15478763a1f4b0ee334e2` | IDENTICAL | IDENTICAL |
| `curriculum_AVWC/avwc_grade.py` | `6e390f8f3c0df5d4229dd3640590ca44` | IDENTICAL | IDENTICAL |
| `curriculum_AVWC/avwc_reader.py` | `1a7f3f211f44c7b67b4f8f2d4c65bf4a` | IDENTICAL | IDENTICAL |
| `curriculum_AV1/av1_grade.py` | `87f15e05130cfdb3cbf195d1daba6154` | — | IDENTICAL |
| `curriculum_AV1/av1_x.py` | `74011a9c5e6c760b8aec1c78e928b4d2` | — | IDENTICAL |
| `curriculum_AV2/av2_grade.py` | `4bde0ad7dbdd3e460dcef1fe6d063979` | — | IDENTICAL |
| `curriculum_AV1R/av1r_grade.py` | `b5c1d0092c6d2a2608ad3cc0899ed0fd` | — | IDENTICAL |
| `curriculum_AV1R/av1r_x.py` | `7313bab8b15629c9d872a39d0654aa08` | — | IDENTICAL |
| `curriculum_AV1/RESULTS.md` (before §7's amendment) | `626b6415af42ee961a40f64e6541465a` | — | IDENTICAL |
| `curriculum_AV2/RESULTS.md` (before §7's amendment) | `c43fe8c84fb24b359676e366b837fe66` | — | IDENTICAL |

**Ten of ten match.** The four grader/producer md5s are additionally re-verified by the comparator at
every single invocation — `FROZEN_GRADER_MD5` and `FROZEN_PRODUCER_MD5` are refusal clauses, not
comments — and neither fired on any of the eleven re-grades this lane ran.

**Pre-registration before compute, re-stated because it is the document's entire evidentiary content.**
The freeze commit is `c85eb4df` at **2026-08-28T17:47:02Z**; the first output artefact,
`avwc_selftest_evidence.txt`, is stamped **17:47:23.74Z** — **21.7 s after** the freeze — followed by
`AVWC_regrade.json` at 17:47:24.51Z and `AVWC_full_grades.json` at 17:48:06.80Z. The gates were closed
before the comparator was first executed. This lane did not re-derive that check; it is the
supervisor's, performed personally, and is recorded here as relied upon.

## 7. Cost — actual against the frozen estimate

Registered (`PREREGISTRATION.md` §9): **3.00 core-min**, cap **10.00**, ranks **1** throughout.

**A necessary honesty about which execution this measures.** The original 2026-08-28 execution's wall
time was **never instrumented and is not recoverable** — the session died before it was recorded and
the working directory was destroyed by the reboot. What is measured here is this lane's **reproduction**
of the same registered work, and the row is labelled as that.

| scope | wall s | ranks | core-min | basis |
|---|---|---|---|---|
| Selftest, `python3` (cold page cache) | 75.2358 | 1 | 1.25393 | `/usr/bin/time -v` |
| Selftest, `python3 -O` (warm) | 3.7372 | 1 | 0.06229 | `/usr/bin/time -v` |
| Re-grade of all three items | 1.0389 | 1 | 0.01731 | `/usr/bin/time -v` |
| **REGISTERED SCOPE, total** | **80.0119** | **1** | **1.33353 MEASURED** | |
| Lane-added independent must-flag driver (§4), timed | 1.3059 | 1 | 0.02177 MEASURED | reported beside, **not folded in** |

**Ratio actual/predicted = 1.33353 / 3.00 = 0.4445.** **13.3 % of the 10.00 cap** — the cap was never
approached, nothing was stopped, no gate moved. Gross = cleaned; no invocation is within two orders of
magnitude of the 3,600-s stall figure.

**Dollars: $0.0011402 DERIVED, NOT MEASURED**, at $0.0513/core-h, c7a.4xlarge; `cost_basis`
**REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Registered estimate was $0.002565 DERIVED. Bounded total including
the lane-added control: **≤ 1.37706 core-min, ≤ $0.0011774 DERIVED**.

**WASTE, named separately and never folded into the ratio** (`COMPUTE_BUDGET_CHARTER.md` §6):
**0.02177 core-min = $0.0000186 DERIVED**. The must-flag driver was run twice — the first run untimed
by this lane's own oversight, the second run existing only to put a measured wall figure on it. It
bought a number, not a verdict. The first run's cost is stated as **NOT MEASURED** and bounded at
**≤ 0.02177 core-min** by the second, which performed identical work.

**Gap attribution — misprediction, and the dominant term is page-cache state, not the work.** The
identical selftest costs **75.24 s cold and 3.74 s warm — a 20.1× spread on byte-identical work**. This
re-run is the first read of these roots after a 32-hour box shutdown and a reboot at 22:33Z, so all
~1,887 files across the three roots came off disk. The registered estimate's basis is an **operation
count** — "≈12 `cp -a` copies, ≈24 md5 manifests, ≈12 frozen `grade()` calls, two selftests" — with **no
cache-state term at all**, and cache state moves this workload by 20×. Contention was present but is
**not** the dominant term: load average was 7.22 on 16 cores with peers committing concurrently, yet
the warm/cold spread on identical work under that same load is 20× while the whole miss is only 2.25×
under.

**Calibration lesson to carry forward: a manifest-heavy re-grade estimate built from an operation
count is not complete without a cache-state term.** Price a cold first pass at roughly 20× the warm
figure for this shape, or state which of the two the estimate assumes. An estimate that does not say
whether it assumes a warm cache is unfalsifiable by a factor of twenty.

The calibration row is **`C-211`** in `docs/COST_CALIBRATION.md`.

## 8. What this item establishes, and what it does not

**It establishes** that one root cause — a reader that stats an uncompressed filename when
`writeCompression on` has written the `.gz` — accounts for the refusals of **two** of the three items,
and that with that one cause repaired the frozen instruments themselves return `PASS` on AV1 and AV1R.
That is a three-item, one-cause finding, and the repaired reader was demonstrated able to refuse on
five distinct clauses before either pass was accepted.

**It establishes** that AV2's refusal was **two** defects stacked, not one, and that the second is a
producer plumbing defect distinct from `writeCompression`, needing its own registration.

**It establishes nothing about the physics, the mesh or the solver**, and no solver ran. It moves no
gate, no threshold, no band, no cap, no label, no capability-grid cell and no census row. Nothing is
claimed about AV2R.

**Honest disclosure, carried forward from `PREREGISTRATION.md` §7.** The instrument was exercised
during development, so this is not an outcome-blind freeze and does not claim to be. What the freeze
bought is the repair semantics, the repairs set per item, the rebind audit, the refusal set, the unit
count and the both-directions controls — all fixed and committed before execution.

## 9. Two defects in this item's own record, disclosed rather than patched

1. **`AVWC_regrade.json` and `AVWC_full_grades.json` embed scratchpad paths.** Fields
   `datum_resolution.*.resolved_path`, `write_compression_source` and `controls.*.file` carry the
   transient working-directory prefix, and those directories no longer exist. `CLAUDE.md` rule 13 says
   a repository document never cites a scratch path. These are machine records of a transient copy
   rather than handoff pointers, and they are **left as executed** — editing an instrument's own output
   after the fact would be a worse defect than the one it fixed. **No path in this prose document is a
   scratch path.** The remedy belongs in the successor's next revision, which is a supervisor's call.
2. **`avwc_dump_full_grades.py` is not part of the frozen grading path.** It is not among the two
   instruments registered by md5 at `PREREGISTRATION.md` §7, and it writes `AVWC_full_grades.json` in
   place. It is landed as a lane-written evidence dump, is cited nowhere as a grading authority, and
   was deliberately **not** run by this lane.

## 10. What is owed, and to whom

* **AV2's `gmresRelTol` plumbing defect** needs its own pre-registration before any repair. That is the
  supervisor's ruling under `VERIFICATION_CHARTER.md` §2d.1. This lane has proposed no repair and
  edited no instrument. **A sibling registration already exists for the same defect in AV2R** —
  `curriculum_AV2RG`, frozen at `2f827746` — and its §35 establishes that `idwarp_identity()` is
  byte-identical across the two producers. **Whether AV2 itself falls inside that registration's scope
  or needs a third is a supervisor's call**, and this lane flags it rather than assuming either way.
* **AV1R has no `RESULTS.md`**, neither on disk nor at HEAD — the item's 18 tracked files do not include
  one. Its superseded refusal is recorded only in its run root, at
  `/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv/AV1R_grade_20260828T071352Z.json`,
  which is not in git. This lane has **not** created one: writing a first `RESULTS.md` for an item it
  did not grade is a supervisor's call, not a lane's.
* **Whether these two `PASS` verdicts advance anything on the ladder** is the supervisor's reading, not
  this lane's. The lane hands over the verdicts, the controls that entitle them, and this record.

## 11. Artefacts, all still on disk

In `cases/dafoam/ladder-a/A1/curriculum_AVWC/`: `PREREGISTRATION.md`, `avwc_grade.py`,
`avwc_reader.py`, `avwc_dump_full_grades.py`, `AVWC_regrade.json`, `AVWC_full_grades.json`,
`avwc_selftest_evidence.txt`, and this file.

Preserved run roots, outside git and never written:
`/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv/` (754 files),
`/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv/` (755 files),
`/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality/` (378 files) — each carrying its
own original grade JSON, per-arm artefacts, per-arm age datums, solver logs and memory windows.

This lane's re-run working directory was transient and is **not** cited by this record.

---

## Amendment record — v1.0 to v1.1, 2026-08-30T23:50Z: §7's CALIBRATION ROW ID IS WRONG. IT IS `C-212`, NOT `C-211`, AND `C-211` BELONGS TO ANOTHER TEAM

**Rule 6 assertion: lines whose number changed above this section: 0.** This is an APPEND at the foot
and nothing above it was edited. **Proved by byte comparison, not asserted.** The block was landed
through `scripts/append_block.py`, which reads the body from a file as bytes so that no shell ever
sees it, compares the landed tail byte-for-byte against the bytes intended, and REVERTS the write on
any difference. Independently of that tool, this lane took a copy of the file before the append: the
pre-append file was **26,306 bytes**, md5 **`5239e81640cac0c0bb39cfab0038377e`**, identical to
`git cat-file blob HEAD:cases/dafoam/ladder-a/A1/curriculum_AVWC/RESULTS.md` at the time of writing,
and the first 26,306 bytes of the file after the append were compared against that copy and are
**byte-identical**. **Version: this record was previously unversioned (v1.0 implied); it is v1.1 as of
this amendment.** No gate, threshold, band edge, cap or label above is altered, no verdict above is
restated, and no cost figure above is changed.

### What is wrong, precisely

§7 above closes: *"The calibration row is `C-211` in `docs/COST_CALIBRATION.md`."*

| | |
|---|---|
| id written in §7 | **`C-211`** — **WRONG** |
| id of this item's row | **`C-212`** |
| what `C-211` actually is | an **`ansys-verification`** row — **VMFL063**, *Separated Laminar Flow Over a Blunt Plate*, register row #44, verdict `GATE FAIL`, landed by that team |

**The wrong id points at another team's record.** `C-212` is the row that carries AVWC's own numbers,
and it is identified as AVWC's by its content and not merely by its position: it is dated 2026-08-30,
team **dafoam**, subject **AVWC**, and it records **1.33353 core-min MEASURED** against a registered
**3.00** core-min at ratio **0.4445** and 13.3 % of the 10.00 cap — the same figures §7 above states.
`C-211` records 13.8333 core-min against a registered 16 for a four-solve `simpleFoam` family, which
is not this item and shares no figure with it.

**Nothing in the ledger is wrong and nothing there needs to move.** `docs/COST_CALIBRATION.md` carries
AVWC's row at the correct id. The defect is confined to this one sentence of prose in this record.

### The cause — ESTABLISHED FROM THE COMMIT TIMELINE, not offered as an inference

This lane can state the mechanism as measured rather than supposed, and does so because a diagnosis
labelled "likely" when it is checkable is a diagnosis that was not checked:

1. Immediately before the `ansys-verification` commit, the maximum `C-` id in
   `docs/COST_CALIBRATION.md` was **`C-210`**, read from
   `git show bf27e151^:docs/COST_CALIBRATION.md`. **A rule-11 tail read taken at any moment before
   that commit therefore yields `C-211` as the next free id, and `C-211` was the correct answer.**
2. `ansys-verification` took `C-211` at commit **`bf27e151`**, committed **2026-08-30T22:55:14Z**.
3. This record landed at commit **`7fd01e25`**, committed **2026-08-30T22:57:01Z** — **107 seconds
   later**. From 22:55:14Z onward, `C-211` was no longer free.
4. **The decisive evidence is internal to that single commit.** `7fd01e25` wrote the ledger row into
   `docs/COST_CALIBRATION.md` as **`C-212`** — correct, because rule 11 requires the id to be
   re-derived from the tail *in the committing invocation* — while writing **`C-211`** into §7 of this
   file. **One commit, two ids for one row, disagreeing.** That is the signature of an id re-derived
   at commit time for the ledger and carried from an earlier reading in the prose.

**What remains genuinely unestablished, and is not dressed up as established:** the exact moment §7's
sentence was authored is not recorded anywhere, so this lane cannot name the instant of the stale
read. What is established is that `C-211` was correct until 22:55:14Z, wrong from then on, and that
the prose and the ledger written in the same commit 107 seconds later do not agree — which is
sufficient to locate the mechanism without guessing at the clock.

**This is rule 11's hazard in its exact registered form**, and it caught two teams in the same
minute in opposite directions: `docs/LAB_STATE.md` records the `ansys-verification` lane finding that
*"`C-211` as I briefed it was STALE: dafoam landed `C-212` mid-flight"* on the same evening. The
remedy rule 11 already names — re-derive the maximum in the committing invocation — was applied to
the ledger row here and not to the prose citing it. **A record that cites an id it did not re-derive
at commit time is citing a reading, not a row.**

### Scope of this correction, and what it deliberately does not touch

* **§7's cost figures are untouched and none is restated as a different number.** The 1.33353
  core-min, the 3.00 registered estimate, the 0.4445 ratio, the 10.00 cap, the $0.0011402 DERIVED
  dollars and the REPORTED-BY-OWNER `cost_basis` all stand exactly as landed. **Only the row id is
  wrong.**
* **No other record is edited by this lane.** `cases/dafoam/ladder-a/A1/curriculum_AV1R/RESULTS.md`
  §7 already carries a correct flag of this discrepancy and already gives the right id, `C-212`; it
  needs no change, and its caveat that the cause was *"an inference, not a measurement"* was honest
  when written and is now superseded by the timeline above.
* **`docs/COST_CALIBRATION.md` is another team's file at `C-211` and was NOT touched.**
* **One further occurrence of `C-211` exists outside dafoam territory and is reported, not
  corrected:** `docs/campaigns/T-family/T3c_PREREGISTRATION.md` cites *"the C-211 cost row"* for a
  T-family draft row. That is heat-transfer's document and a **separate** misnumbering — the board at
  `docs/LAB_STATE.md` already records the underlying T3 draft row as misnumbered and to be renumbered
  when landed. **Correcting another team's record is not this lane's call**, and it is flagged upward
  rather than fixed.

**Nothing in this amendment is filed, sent, uploaded, registered, posted or commented outside this
box.** SUBMISSIONS PARKED (`CLAUDE.md` rule 7).
