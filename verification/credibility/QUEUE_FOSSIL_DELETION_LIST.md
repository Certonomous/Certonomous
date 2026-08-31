# QUEUE FOSSIL DELETION LIST — 17 EXPLICIT PATHS, TWO REFUSALS

**COMMITTED AND OPERATIVE — THIS IS THE AUTHORISATION.** Drafted by a verification lane;
**re-verified and landed by the verification-supervisor**, who independently re-ran the
decisive discriminator before publishing it: across all 45 citation lines the citing files are
**17 distinct paths, extensions `.md`, `.json`, `.log` only — ZERO `.py` and ZERO `.sh`**. No
executable in this repository reads any of the 17 by path, which is exactly the property
`G1_grid_triple.json` fails and why it is refused in §3.2.

**Owners act against THIS FILE and nothing else.** Deletions land one commit per team under the
rule-10 private-index protocol. **The two refusals in §3 are binding on every team**, and the
scope fence below is binding on every reader.

**Re-verified 2026-08-31T15:32:09Z against HEAD `12b1bd84766117d99c88dedf391470bb8bf47e5c`.**
Every row below was re-measured at that clock, not carried forward from an earlier pass.
The tree moved seven times during the audit (`becd0863` → `d910023e` → `e831a4a6` →
`927924f1` → `79d2e467` → `12b1bd84`); a deletion list without its clock and HEAD is not a
measurement.

**⚠ THE COUNT IS 17, AND IT HAS BEEN TESTED TWICE.** This audit reported 19, then 18, then
17. The last move was evidence: a full-path citation sweep (§1.1, pass 1) found that
`verification/queue/closure/G1_grid_triple.json` is a **registered control specimen inside a
frozen pre-registration**, refused in §3.2. **A second, independent basename sweep was then run
against all 17 and classified every one of its 27 citations (§1.2): all 27 are NARRATIVE, none
is load-bearing, and the count HOLDS AT 17.** It did not move because nothing was found — it
did not move because what was found does not block. **The count is a result, not a target.**

---

## ⚠ SCOPE FENCE — READ BEFORE ANYTHING ELSE

**THIS COVERS THE 17 EXPLICIT PATHS NAMED IN §2 AND NOTHING ELSE. IT IS NOT AN
AUTHORISATION TO DELETE "THE FOSSIL CLASS".**

Sanaa's ruling (5) of 2026-08-31 — *"The 19 queue fossils: delete (they're fossils)"*
(`etc/sessions/2026-08-31T1505Z_sanaa_rulings_six.md:3`) — rules on a **count of 19 taken on
2026-08-27T22:44:16Z**, four days before the ruling. That count is recorded in
`docs/standards/QUEUE_ENTRY_VALIDATOR_RULINGS.md` §R-QCOMMIT.9.1, which states in the same
breath that **the count grows by one per launch under current practice** (17 at 22:25:34Z,
19 at 22:44:16Z, nineteen minutes apart).

**The same predicate now returns 135.** Measured at the clock and HEAD above:

| reading | 2026-08-27T22:44:16Z | 2026-08-31T15:32:09Z |
|---|---|---|
| fossils (tracked at HEAD, absent from disk) | **19** | **135** |
| of those, `launched/` counterpart **at HEAD** | 18 | **18** |
| of those, `launched/` counterpart **on disk only** | 1 | **117** |

**117 of the 135 have a `launched/` counterpart that exists ONLY on disk and has never been
committed.** Deleting one of those from HEAD is a **pure deletion that strands the last
tracked trace** — precisely the failure this team already recorded at
`docs/LAB_STATE.md:17027`: *"the 19 are renames, not fossils, and deleting them without
adding `launched/` loses 35 launch records."*

**An owner who reads this file as a class deletion destroys the last tracked trace of 117
launch records.** Delete the enumerated paths. Do not delete the class. A future clean of the
remaining 117 requires their `launched/` records to be committed **first**, at which point the
removal is a rename and not a deletion at all (§R-QCOMMIT.9).

**And a class deletion breaks a frozen instrument twice over.**
`verification/campaign/R3_COMMIT_RENAME_MODE_PREREGISTRATION.md` registers **two** of the
fossil class as byte-asserted control specimens fetched **by path at HEAD**:
`verification/queue/closure/G1_grid_triple.json` (2,557 B — controls R1, R4, R7) and
`verification/queue/cfd/F25_DUCT3D.json` (6,535 B — control R6). Both sizes were re-measured
at the clock above and match the registration exactly. **Neither may be deleted by anyone**;
G1 is refused in §3.2, and F25_DUCT3D is not on this list at all but is named here because a
class sweep would take it.

---

## 1. WHAT MAKES A PATH SAFE, AND HOW IT WAS TESTED

A fossil is a path tracked at HEAD under `verification/queue/<team>/<case>.json` with **no
file on disk** — the old drop path of an entry the queue runner moved into `launched/` at
launch.

A fossil is **safe to delete** only if its content survives at a path that is **itself at
HEAD**. The test compares the fossil's **HEAD blob** against the counterpart's **HEAD blob** —
never against the counterpart's disk copy, which would score a stale survivor as safe
(the `R-QCOMMIT.4` trap: *"a tracked-but-stale entry is worse than an untracked one, because
it carries a HEAD blob that a reader will trust and that is not what ran"*).

Differences confined to the named runner-key set `_launch`, `_field_classes`,
`status_seen_utc` are launch metadata, not content (`R-QCOMMIT.9.2`: a byte-equality test
*"would refuse all eighteen genuine pairs"*).

**Result for all 17 below: zero non-runner-key differences.** `prereg_commit`, `prereg_path`,
`cost_core_min_estimate`, `cap_core_min_registered`, `ranks` and `grading_path` are preserved
verbatim at the tracked `launched/` path in every case.

**Planted controls, both directions, in the same invocation as the measurement** (rule 3 — a
reader not shown able to see a non-zero cannot certify a zero): the HEAD-blob reader returned
content for a known-tracked path and `None` for a fabricated one; the `LAUNCH_LOG.tsv` reader
returned `[92]` for a known-launched `case_id` and `[]` for a fabricated one; the fossil
classifier was shown not to classify a present-on-disk path as absent.

**These 17 are genuine fossils, not merely old.** Every one carries a `LAUNCH_LOG.tsv` row —
the entry was consumed by the runner and the launch happened. The control that gives this
force: the four never-launched held entries `P_Ts_f`, `P_Ts_m`, `P_q_f`, `P_q_m` return **no
rows at all** from the same reader, so the reader distinguishes launched from never-launched.
No path below is stale-but-never-run.

**No fossil carries an rc, timeout, kill, elapsed, actual-cost or GPU-hour field.** Checked
across all 19 candidates: those facts live in `STATUS.*` files and `LAUNCH_LOG.tsv`, so no
launcher rc, kill record or cost actual dies with any deletion below.

### 1.1 THE CITATION SWEEP — TWO PASSES, AND THE SECOND ONE CLEARED NOTHING BY ITSELF

Content survival is not the only way a path can be load-bearing. A path can also be **cited**,
and a deletion makes the citation unresolvable. Two sweeps were run, and the method of the
second matters as much as its result.

**Pass 1 — full-path match.** Single pass over the repository text corpus matching each
candidate as an exact full-path string. This found the stop condition that moved the count
from 18 to 17: `verification/queue/closure/G1_grid_triple.json` (§3.2).

**Pass 2 — basename match, and a warning about the key that was tried first.** A sweep keyed
on the bare **stem** (`D17_chain`, `T5_S_m`) returns *"17 of 17 cited"* — a **false positive**,
because the stem is the *case* name and every case is discussed in its registration, results,
docket and board. **The stem measures discussion of the case; only the BASENAME measures
reference to the QUEUE FILE.** Pass 2 therefore keys on basename only, excluding each entry's
own file and its `launched/` counterpart.

**Controls, both passes, in the same invocation as the measurement (rule 3):** an impossible
token returned 0 hits; a known-present token returned 272; and a sentinel planted into the real
corpus was read back through the real reader and disappeared when removed. The reader was
additionally shown able to find the **known load-bearing** citer — it returns 6 files for
`queue/closure/G1_grid_triple.json`. **So the negative results below are evidence, not
blindness.**

**Result: 27 citations, 10 entries cited, 7 entries clean.** Clean, cited by nothing anywhere:
`D_Ts_Re25_U_c/f/m.json`, `L_Ts_U_c/f/m.json`, `T16_MC_c.json`.

### 1.2 THE CLASSIFICATION TEST, AND ALL 27 ROWS

**The test, taken from the G1 block that established it:** a citation is **LOAD-BEARING** only
if a **frozen registration or a live control PATH-ADDRESSES the file such that deleting or
renaming it kills the control** — as R3's driver does, fetching `HEAD:<path>` with `git
cat-file` and asserting a byte size. A board, docket, cost row, README or registration merely
**recording that the entry existed and what it contained** is **NARRATIVE** and does not block.

**THE DECISIVE NEGATIVE, measured: not one of the 27 citations lives in an executable.** Across
all 45 citation lines the citing files are **41 `.md` and 4 `.json`, and ZERO `.py` or `.sh`.**
No script, driver, comparator or selftest anywhere in this repository reads any of the 17 by
path. The same reader finds the `.md` registration that makes G1 load-bearing, so this zero is
a plant-controlled zero and not an artefact of the sweep.

| # | citing file | cited entry | quoted citing line | verdict | reason |
|---|---|---|---|---|---|
| 1 | `docs/LAB_STATE.md` | `VMFL011-R3.json` | board prose recording the entry | **NARRATIVE** | session board; records that it existed |
| 2 | `docs/standards/QUEUE_ENTRY_HOST_SCOPE.md:394` | `VMFL011-R3.json` | *"of those, declaring **this** box \| **2** — `ansys-verification/launched/VMFL011-R3.json` and `launched/VMFL076-R2.json`, both `host: ip-172-31-43-247`"* | **NARRATIVE** | ⚠ **it cites the `launched/` path, not the drop path** — the deletion does not touch what the standard names; and the row is a census reading, not a fixture |
| 3 | `docs/LAB_STATE.md` | `VMFL076-R2.json` | board prose | **NARRATIVE** | as row 1 |
| 4 | `docs/standards/QUEUE_ENTRY_HOST_SCOPE.md:394` | `VMFL076-R2.json` | same line as row 2 | **NARRATIVE** | cites the `launched/` path |
| 5 | `docs/LAB_STATE.md` | `F17c_KV40_FLOOR.json` | board prose | **NARRATIVE** | records the entry |
| 6 | `verification/campaign/F17c_KV40_FLOOR_PREREGISTRATION.md:518` | `F17c_KV40_FLOOR.json` | *"`cases/F17c_kovasznay_floor/queue_entry_F17c_KV40_FLOOR.json` and is **HELD**"* | **NOT A CITATION** | ⚠ **basename collision — a DIFFERENT FILE**, `queue_entry_F17c_KV40_FLOOR.json` under `cases/`, not the queue entry |
| 7 | `verification/campaign/F17c_KV40_FLOOR_RESULTS.md:528` | `F17c_KV40_FLOOR.json` | *"`launcher.queue.out` and `queue_entry_F17c_KV40_FLOOR.json` under the case"* | **NOT A CITATION** | same collision — the case-directory file |
| 8 | `cases/dafoam/curriculum_D17_cone_supersonic/PREREGISTRATION.md:105` | `D17_chain.json` | *"**Queue entry `verification/queue/dafoam/D17_chain.json`:** team `dafoam`, `prereg_commit` = the sha of the commit introducing this file, `launch_cmd` = …"* | **NARRATIVE** | §9 "FREEZE AND QUEUE" **declares what will be filed**; nothing reads the file. The registration's controls are `d17_grade.py` md5 `a940b0ee…` and the driver guards |
| 9 | `docs/LAB_STATE.md` | `D17_chain.json` | board prose | **NARRATIVE** | records the entry |
| 10 | `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_F3S/PREREGISTRATION.md:127` | `D4S_F3S_chain.json` | *"**Launch path of record:** the queue runner — `verification/queue/dafoam/D4S_F3S_chain.json` with `prereg_commit` = the sha of this commit, argv …, validated by `scripts/queue_entry_check.py`"* | **NARRATIVE** | names the launch path of record; the *validator* is the control, and it validates whatever entry is presented, not this path |
| 11 | `docs/LAB_STATE.md` | `D4S_F3S_chain.json` | board prose | **NARRATIVE** | records the entry |
| 12 | `cases/dafoam/ladder-a/A2/curriculum_D6/PREREGISTRATION.md:286, :321` | `D6_chain_wait.json` | *"The live entry is **`verification/queue/dafoam/D6_chain_wait.json`**: `case_id D6_chain_wait`, `prereg_commit` = the commit that lands this addendum…"* | **NARRATIVE** | an addendum **recording which entry is live**; no control reads it. ⚠ goes stale on deletion — see §5 |
| 13 | `docs/LAB_STATE.md` | `D6_chain_wait.json` | board prose | **NARRATIVE** | records the entry |
| 14 | `verification/queue/dafoam/held/D6_chain.json:19` | `D6_chain_wait.json` | *"The CURRENT governing record for this item is `verification/queue/dafoam/launched/D6_chain_wait.json`, which is NOT back-filled…"* | **NARRATIVE** | ⚠ **it cites the `launched/` path, which is retained** — the retained held record points at the survivor, not at the deleted drop path |
| 15 | `verification/queue/dafoam/held/D6_chain_wait.e43bdf61.json:28` | `D6_chain_wait.json` | identical `cap_annotation_note` wording, naming `launched/D6_chain_wait.json` | **NARRATIVE** | ⚠ **also cites the `launched/` path** — same finding |
| 16 | `verification/queue/dafoam/held/README.md:21, :25` | `D6_chain_wait.json` | *"is SUPERSEDED by the drop-path entry **`D6_chain_wait.json`**"* | **NARRATIVE** | a supersession record. **This one DOES name the drop path** and goes dangling — §5 |
| 17 | `cases/dafoam/ladder-a/A2/curriculum_D6R/QUEUE_ENTRY_DRAFT_D6R_chain_wait.json:40` | `D8R_chain_wait.json` | *"`two_row_rule`: DAFOAM_CHARTER.md SECTION 6 — not section 11 … a STRUCK SLIP that D8R_chain_wait.json and D6's own launcher comment both carry"* | **NARRATIVE** | ⚠ **not a dependency at all** — prose noting which files carry a struck charter-section slip |
| 18 | `verification/queue/dafoam/launched/D6R_chain_wait.json:39` | `D8R_chain_wait.json` | same `two_row_rule` string | **NARRATIVE** | same struck-slip prose |
| 19 | `verification/queue/dafoam/D6R_chain_wait.json` (**HEAD blob**) | `D8R_chain_wait.json` | same `two_row_rule` string | **NARRATIVE** | ⚠ **and it is NOT a live entry:** `D6R_chain_wait.json` is itself a member of the 135 fossil class — tracked at HEAD, absent from disk, already moved to `launched/`. It cannot depend on anything |
| 20 | `verification/queue/dafoam/held/README.md:25` | `D8R_chain_wait.json` | *"`D8R_chain.357a2648.json` here is the first-fit D8R entry, SUPERSEDED by the drop-path **`D8R_chain_wait.json`**"* | **NARRATIVE** | supersession record; names the drop path and goes dangling — §5 |
| 21 | `docs/LAB_STATE.md` | `D8R_chain_wait.json` | board prose | **NARRATIVE** | records the entry |
| 22 | `docs/LAB_STATE.md` | `T15_UP_f.json` | board prose | **NARRATIVE** | records the entry |
| 23 | `docs/COST_CALIBRATION.md:268` | `T16_MC_m.json` | *"`verification/queue/heat-transfer/launched/T16_MC_m.json` carries `cost_core_min_estimate: 132.888` and **no `cap_core_min_registered` key at all**"* | **NARRATIVE** | ⚠ **cites the `launched/` path, which is retained**; a defect note recording a past reading |
| 24 | `docs/DOCKET.md:936` | `T5_S_m.json` | *"`verification/queue/heat-transfer/launched/T5_S_m.json` is schema-valid, cites a real freeze commit and a real registration…"* | **NARRATIVE** | ⚠ **cites the `launched/` path, which is retained** |
| 25 | `docs/campaigns/T-family/T5_PREREGISTRATION.md:1608` | `T5_S_m.json` | *"The held draft `verification/runs/T-family/T5_runs/queue_drafts/T5_S_m_BLOCKED.json` is re-pointed at the built case, re-validated and renamed `T5_S_m.json`, citing **this amendment's commit as `prereg_commit`**"* | **NARRATIVE** | ⚠ **names a BARE BASENAME as the rename destination of a draft under `verification/runs/`** — it does not path-address the queue entry, and no control reads it |
| 26 | `cases/RANS_LES_closure_models/_common/MULTIMODEL_SWEEP_FEASIBILITY_DRAFT.md:575` | `T5_S_m.json` | *"`verification/queue/heat-transfer/T5_S_m.json` records the state as…"* | **NARRATIVE** | a **DRAFT**, not frozen; records a state reading |
| 27 | `docs/LAB_STATE.md` | `T5_S_m.json` | board prose | **NARRATIVE** | records the entry |

**ALL 27 ARE NARRATIVE. NONE IS LOAD-BEARING. THE COUNT STAYS AT 17.**

Four independent reasons the classification is not a soft pass: **(i)** zero of the 27 sit in
an executable, against a reader proven able to find the one load-bearing `.md`; **(ii)** two
are **basename collisions naming a different file entirely** (rows 6, 7); **(iii)** seven cite
the **`launched/` counterpart, which this list retains** (rows 2, 4, 14, 15, 18, 23, 24); and
**(iv)** the one citation from a queue entry (row 19) comes from a **file that is itself a
fossil**, so the "a live entry depends on it" reading is refuted at the source. What remains
is boards, dockets, cost rows and supersession records — documents that record history, and
whose value does not depend on the recorded file still being fetchable.

## 2. THE 17 SAFE PATHS, BY OWNING TEAM

Owner is the queue subdirectory. **Each team deletes its own rows.** Paths are absolute and
complete; nothing below needs re-deriving or re-typing.

`LAUNCH_LOG.tsv` line numbers cite `/home/ubuntu/Certonomous/verification/queue/LAUNCH_LOG.tsv`
as it stood at the re-verification clock. **That file is NOT at HEAD** (verified), so it is
named here as corroboration only — the load-bearing survivor in every row is the committed
`launched/` record, which is at HEAD.

### ansys-verification — 2 paths

| # | delete (absolute) | surviving record at HEAD | corroboration |
|---|---|---|---|
| 1 | `/home/ubuntu/Certonomous/verification/queue/ansys-verification/VMFL011-R3.json` | `/home/ubuntu/Certonomous/verification/queue/ansys-verification/launched/VMFL011-R3.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:47`, 2026-08-26T23:18:53Z |
| 2 | `/home/ubuntu/Certonomous/verification/queue/ansys-verification/VMFL076-R2.json` | `/home/ubuntu/Certonomous/verification/queue/ansys-verification/launched/VMFL076-R2.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:50`, 2026-08-26T23:32:58Z |

### cfd — 1 path

| # | delete (absolute) | surviving record at HEAD | corroboration |
|---|---|---|---|
| 3 | `/home/ubuntu/Certonomous/verification/queue/cfd/F17c_KV40_FLOOR.json` | `/home/ubuntu/Certonomous/verification/queue/cfd/launched/F17c_KV40_FLOOR.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:91`, 2026-08-27T22:30:04Z |

### closure — 0 paths

**Closure's only member, `verification/queue/closure/G1_grid_triple.json`, is REFUSED in
§3.2.** It passes the content-survival test but fails the citation test. Closure has nothing
to delete under this list.

### dafoam — 4 paths

| # | delete (absolute) | surviving record at HEAD | corroboration |
|---|---|---|---|
| 4 | `/home/ubuntu/Certonomous/verification/queue/dafoam/D17_chain.json` | `/home/ubuntu/Certonomous/verification/queue/dafoam/launched/D17_chain.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:79`, 2026-08-27T11:34:40Z |
| 5 | `/home/ubuntu/Certonomous/verification/queue/dafoam/D4S_F3S_chain.json` | `/home/ubuntu/Certonomous/verification/queue/dafoam/launched/D4S_F3S_chain.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:82`, 2026-08-27T13:47:58Z |
| 6 | `/home/ubuntu/Certonomous/verification/queue/dafoam/D6_chain_wait.json` | `/home/ubuntu/Certonomous/verification/queue/dafoam/launched/D6_chain_wait.json` — at HEAD, 0 non-runner diffs; carries `prereg_commit 0aa9a82a`, `cost_core_min_estimate 1694.7`, `ranks 4` | `LAUNCH_LOG.tsv:83`, 2026-08-27T13:49:03Z, pid 790394 — **§4 and §5 apply to this row** |
| 7 | `/home/ubuntu/Certonomous/verification/queue/dafoam/D8R_chain_wait.json` | `/home/ubuntu/Certonomous/verification/queue/dafoam/launched/D8R_chain_wait.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:84`, 2026-08-27T13:58:49Z — **§4 applies to this row** |

### heat-transfer — 10 paths

| # | delete (absolute) | surviving record at HEAD | corroboration |
|---|---|---|---|
| 8 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/D_Ts_Re25_U_c.json` | `…/heat-transfer/launched/D_Ts_Re25_U_c.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:71`, 2026-08-27T09:01:52Z |
| 9 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/D_Ts_Re25_U_f.json` | `…/heat-transfer/launched/D_Ts_Re25_U_f.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:72`, 2026-08-27T09:12:42Z |
| 10 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/D_Ts_Re25_U_m.json` | `…/heat-transfer/launched/D_Ts_Re25_U_m.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:73`, 2026-08-27T09:13:48Z |
| 11 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/L_Ts_U_c.json` | `…/heat-transfer/launched/L_Ts_U_c.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:74`, 2026-08-27T09:43:03Z |
| 12 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/L_Ts_U_f.json` | `…/heat-transfer/launched/L_Ts_U_f.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:75`, 2026-08-27T09:54:58Z |
| 13 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/L_Ts_U_m.json` | `…/heat-transfer/launched/L_Ts_U_m.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:76`, 2026-08-27T11:02:09Z |
| 14 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/T15_UP_f.json` | `…/heat-transfer/launched/T15_UP_f.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:70`, 2026-08-27T08:57:32Z |
| 15 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/T16_MC_c.json` | `…/heat-transfer/launched/T16_MC_c.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:88`, 2026-08-27T17:30:03Z |
| 16 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/T16_MC_m.json` | `…/heat-transfer/launched/T16_MC_m.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:89`, 2026-08-27T17:42:51Z |
| 17 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/T5_S_m.json` | `…/heat-transfer/launched/T5_S_m.json` — at HEAD, 0 non-runner diffs | `LAUNCH_LOG.tsv:86`, 2026-08-27T17:27:53Z |

**Per-team counts: ansys-verification 2, cfd 1, closure 0, dafoam 4, heat-transfer 10 — total
17.**

For reconciliation against Sanaa's 19: the per-team decomposition at `docs/LAB_STATE.md:10133`
reads *"ansys 2, cfd 1, closure 1, dafoam 4, heat-transfer 11"* = 19. The two differences are
the two refusals in §3 — closure's `G1_grid_triple.json` (§3.2) and heat-transfer's eleventh
member `T5b_c.json` (§3.1). **19 − 2 = 17.**

---

## 3. BLOCKED — TWO PATHS ARE REFUSED

### 3.1 `BLOCKED` — `T5b_c.json`, no tracked survivor

**`/home/ubuntu/Certonomous/verification/queue/heat-transfer/T5b_c.json` is NOT authorised for
deletion.** Owner: heat-transfer.

This is the nineteenth member of Sanaa's 19 — the one `R-QCOMMIT.9.2` already singled out:
*"AND THE NINETEENTH HAS NO COUNTERPART AT HEAD AT ALL. It is named as unpaired rather than
assumed into the class; the pairing is 18 of 19, not 19 of 19, and that one must be resolved
by its owner before any cleanup touches it."*

Re-measured at the clock above:

- fossil at HEAD: **yes**; on disk: **no**
- `/home/ubuntu/Certonomous/verification/queue/heat-transfer/launched/T5b_c.json` — **on disk,
  NOT at HEAD**
- `/home/ubuntu/Certonomous/verification/queue/LAUNCH_LOG.tsv` — **NOT at HEAD**
- repo-wide search for `T5b_c` outside the queue returns `docs/LAB_STATE.md` and that
  untracked log, and nothing else

**Deleting it removes the last tracked trace.** The facts that would survive only in untracked
files are: `prereg_commit 35df976233a46a5068fd87d32c10534f187b3c87`,
`prereg_path docs/campaigns/T-family/T5b_PREREGISTRATION.md`,
`cost_core_min_estimate 16.4`, `cap_core_min_registered 32.8`, and the launch record
`LAUNCH_LOG.tsv:92` — 2026-08-27T22:31:09Z, pid 1596175, 1 rank.

**The refusal is conditional and cheap to clear.** The fossil and the on-disk `launched/`
copy differ in **zero non-runner keys** (measured). The moment
`verification/queue/heat-transfer/launched/T5b_c.json` is committed, the pair is a genuine
rename and the removal is safe. **Commit the launched record first; then this path joins the
list above.** Until then it stays.

### 3.2 `BLOCKED` — `G1_grid_triple.json`, a registered control specimen

**`/home/ubuntu/Certonomous/verification/queue/closure/G1_grid_triple.json` is NOT authorised
for deletion.** Owner: closure.

**It passes every content test and fails on a dependency the content test cannot see.** Its
`launched/` counterpart is at HEAD with zero non-runner-key differences, and both its launches
survive as `LAUNCH_LOG.tsv:87` (2026-08-27T17:28:58Z, `prereg_commit 03be2015`) and `:90`
(2026-08-27T21:31:31Z, `prereg_commit a90077df`). On the §1 test it would be safe.

**But it is a byte-asserted control fixture inside a FROZEN pre-registration.**
`verification/campaign/R3_COMMIT_RENAME_MODE_PREREGISTRATION.md` registers, at `:145-159`
(BR-1, headed *"THE DEMONSTRATION, MANDATORY, AND THE INSTRUMENT REFUSES WITHOUT IT"*):

> *"R1's fixture is built from bytes the real producer wrote. The old side is the **HEAD blob**
> of `verification/queue/closure/G1_grid_triple.json` (2,557 B) and the new side the **HEAD
> blob** of `verification/queue/closure/launched/G1_grid_triple.json` (2,883 B)… **THE
> REFUSAL.** Before it grades anything, the driver asserts, in the same invocation: (i) both
> blobs are fetched with `git cat-file` from **this repository's HEAD**, and their byte sizes
> are asserted **2557** and **2883** — a synthesised or hand-edited pair is refused."*

The fetch is **path-addressed at HEAD** (`HEAD:<path>`), not object-addressed. **Deleting the
drop path from HEAD makes that fetch fail, and with it control R1 — plus R4, "the control that
reproduces the exact defect the mode exists to fix", and R7, the similarity-floor control,
which both build on R1's pair** (`:504`, `:507`, `:510`).

**Verified live at the re-verification clock**, and the registered sizes reproduce exactly:

| registered fixture | registered size | measured at HEAD `12b1bd84` |
|---|---|---|
| `verification/queue/closure/G1_grid_triple.json` | 2,557 B | **2,557 B — fetchable** |
| `verification/queue/closure/launched/G1_grid_triple.json` | 2,883 B | **2,883 B — fetchable** |
| `verification/queue/cfd/F25_DUCT3D.json` (control R6) | 6,535 B | **6,535 B — fetchable** |

**No rename saves this one.** A rename also removes the old path from HEAD, and the
registration asserts the **old** path. And because R3 is frozen with **zero compute spent**,
the fixture cannot be re-pointed by editing it — rule 6 forbids editing a frozen file, and
rule 2 forbids an amendment that would alter a registered control.

**Disposition: retain until the R3 item is graded or formally withdrawn by its owner.** That
is closure's and verification's call jointly, not this list's.

**⚠ Note for anyone widening the sweep:** `verification/queue/cfd/F25_DUCT3D.json` is control
R6's fixture, is **also a member of the 135-strong fossil class**, and is **not** on this
list. A class deletion takes it and breaks R6.

---

## 4. OPERATING INSTRUCTION — DELETE BY PATH, NEVER BY `case_id`

**Every deletion below is keyed on the explicit path. No owner may key a deletion on
`case_id`, on a basename glob, or on any predicate that enumerates the fossil class.**

**The specimen that forces this rule.** The `case_id` `D6_chain_wait` names **three distinct
objects** in this repository:

| object | state | `prereg_commit` | disposition |
|---|---|---|---|
| `verification/queue/dafoam/D6_chain_wait.json` | fossil — HEAD, absent from disk | `0aa9a82a` (D6 Addendum 3) | **row 7 above — DELETE** |
| `verification/queue/dafoam/launched/D6_chain_wait.json` | HEAD + disk | `0aa9a82a` | **the surviving record — KEEP** |
| `verification/queue/dafoam/held/D6_chain_wait.e43bdf61.json` | HEAD + disk | `e43bdf61` (D6 Addendum 2) | **FOSSIL-RETAIN — NEVER DELETE** |

The held entry is a **different generation of registration**, not a copy: it alone carries
`cap_core_min_registered = 2230.0` and its
`cap_core_min_registered_source` naming `PREREGISTRATION.md:93-99`. It is one of the 13 held
entries this team ruled **FOSSIL-RETAIN, NOT DELETE** on 2026-08-31
(`docs/LAB_STATE.md:16752`), whose deletion would destroy a `launcher_rc=124` record and
license re-spending **1,694.7 core-min**.

**A deletion keyed on `case_id = "D6_chain_wait"` matches all three and reaches the retained
held entry.** A deletion keyed on the explicit path in row 7 matches exactly one. Use the path.

---

## 5. THE DANGLING-CITATION NOTE — WHAT GOES STALE, AND WHAT DOES NOT

Every citation in §1.2 is narrative, so none blocks a deletion. But narrative citations still
**go stale**, and three of the 27 name a drop path this list deletes. They are listed here so
the owner lands the removal knowingly rather than discovering it later.

**The three that go dangling** — all in one file,
`/home/ubuntu/Certonomous/verification/queue/dafoam/held/README.md` (tracked at HEAD, 35 lines),
the document that exists to record dafoam's premature launcher fires:

| citing line | names | after deletion |
|---|---|---|
| `held/README.md:21` | `D6_chain_wait.json` | *"`D6_chain.json` here … is SUPERSEDED by the drop-path entry **`D6_chain_wait.json`**"* — names a path no longer at HEAD |
| `held/README.md:25` (i) | `D6_chain_wait.json` | *"`D6_chain_wait.e43bdf61.json` here … SUPERSEDED by the drop-path `D6_chain_wait.json`"* |
| `held/README.md:25` (ii) | `D8R_chain_wait.json` | *"`D8R_chain.357a2648.json` here … SUPERSEDED by the drop-path **`D8R_chain_wait.json`**"* |

Plus, in a **frozen** registration that rule 6 forbids editing:
`cases/dafoam/ladder-a/A2/curriculum_D6/PREREGISTRATION.md:286` and `:321`, which name
`verification/queue/dafoam/D6_chain_wait.json` as *"the live entry"*. **That sentence becomes
false-on-its-face at HEAD after deletion and cannot be corrected in place.** Disclosed, not
fixed — the fix, if any, is a dated addendum, and it is dafoam's call.

**What does NOT go dangling, and this is the reassuring half of the finding.** The concern that
*"the retained set cites the deletion set"* does not survive inspection: **both retained held
JSON records point at the `launched/` survivor, not at the drop path.**
`held/D6_chain.json:19` and `held/D6_chain_wait.e43bdf61.json:28` both read, verbatim and
identically:

> *"The CURRENT governing record for this item is
> `verification/queue/dafoam/launched/D6_chain_wait.json`, which is NOT back-filled and
> therefore still carries no cap field."*

`held/README.md:31` says the same. **So the retained evidence of the premature fires points at
a file this list keeps.** Only the three supersession sentences above name the drop path, and
each is a historical record of a supersession that genuinely happened — its truth does not
depend on the superseded-by file remaining fetchable.

**Two ways to close it, either acceptable, both dafoam's call:**

- **land the two dafoam removals as renames** (`R-QCOMMIT.9`: *"the launched record lands as a
  RENAME of the committed root entry — git's `R100`, same blob, new path"*), so the blob
  survives at the path the README already calls the governing record; **or**
- **append a dated addendum to `held/README.md`** redirecting the three sentences to
  `verification/queue/dafoam/launched/D6_chain_wait.json` and
  `verification/queue/dafoam/launched/D8R_chain_wait.json`.

**No other fossil in the 17 is named by any `held/README.md`** — checked across all three
teams' held directories for all 19 candidate `case_id`s and all 17 basenames; only these
matched.

## 6. WHAT THIS FILE DOES NOT DO

- It **authorises nothing on its own.** Authority is Sanaa's ruling (5) plus the chief's
  routing condition — *"owners delete via private index after verification confirms none is
  sole surviving evidence"*. This file is the confirmation the condition asks for, for 17
  paths, and the two refusals in §3.
- It does **not** rule on the 13 `held/` entries. Those are a separate set, ruled
  **FOSSIL-RETAIN, NOT DELETE** (`docs/LAB_STATE.md:16752`), and the **overlap with this list
  is EMPTY by resolved absolute path and by basename** — verified at the clock above against
  both the 19 and the full 135, with all 13 held entries confirmed present on disk. The one
  `case_id` collision is handled in §4.
- It does **not** touch the remaining 117. Those need their `launched/` records committed
  before any removal is anything but a loss.
- **No file was deleted, moved or committed in producing it.** Compute: zero core-minutes —
  the audit is read-only against HEAD blobs and the working tree.
