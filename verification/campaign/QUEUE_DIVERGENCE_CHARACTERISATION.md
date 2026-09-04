# QUEUE DIVERGENCE — characterisation, not a verdict

**Team:** cfd (lab-lane, on the cfd supervisor's instruction)
**Date:** 2026-09-04, readings 22:14Z–22:18Z
**Status:** CHARACTERISATION ONLY. **Nothing was launched, withdrawn, deleted, moved,
re-filed or edited.** Zero solver compute.
**Reader:** `scripts/queue_divergence_census.py` (read-only; writes nothing under
`verification/queue/`).

The brief that commissioned this named "roughly 129 rows". **That figure does not
reproduce in any sense tested.** Section 6 records what was tried. The counts below
are the ones measured.

---

## 0. The measurement is taken against a MOVING TREE, and that is disclosed

`scripts/queue_runner.py --daemon` was **live** throughout (pid 1771, ~7.4 h uptime),
and peers commit continuously. HEAD moved three times during the census —
`2d919796` → `ed202dee` → `7e1b981e` — and the untracked-under-`launched/` count moved
164 → 165 between the two full passes. **Every substantive count below was identical
across both passes**, four minutes and three HEAD moves apart. Where a number can
drift, it is stated with its timestamp.

A foreign `rhoPimpleFoam` (pid 216458) was running. It was not touched.

---

## 1. What the divergence IS — by sense, with each reader's plant line

Rule 3: a zero from a reader not shown able to see a non-zero is not evidence. Every
reader below plants a known perturbation, reads it back **through the same code path
that produces the census**, and prints its discrimination.

### Sense (i) — rows on disk diverging from HEAD

`git status --porcelain -- verification/queue/` — **367 status lines** at 22:14Z:
151 `D`, 174 `??`, 42 `M`. This is the raw surface, and on its own it is **not a
finding**: senses (ii)–(iv) decompose it, and almost all of it is the daemon working.

### Sense (iv) + HAZARD 1 — is a deleted pending row a LAUNCH or a WITHDRAWAL?

> `PLANT[pairing] injected=1 unmatched-deletion seen_as_unpaired=True
> matched-deletion absorbed=True -> DISCRIMINATED`

The plant is two-sided: a synthetic deletion that *cannot* have a launched copy must be
reported unpaired, and the same name *with* a counterpart must be absorbed. Both held.

| | count |
|---|---|
| deleted rows at PENDING paths | **144** |
| ... paired to a `launched/` copy = **DAEMON LAUNCH** | **144** |
| &nbsp;&nbsp;— by exact basename | 143 |
| &nbsp;&nbsp;— by **archiver rename** (`archive_previous_records`) | 1 |
| deleted rows that are a candidate **WITHDRAWAL** | **0** |

**Not one deletion is a withdrawal.** The mechanism is `launch()` in
`scripts/queue_runner.py`: `shutil.move(pending → launched/)` followed by
`dst.write_text(meta)`. One launch necessarily prints one `D` and one `??`/`M`.

The single non-exact pair is the trap the supervisor's hazard 1 warns about, and it is
foreign: `verification/queue/heat-transfer/T20_LC_c.json` has **no**
`launched/T20_LC_c.json`. An exact-basename reader would call it a withdrawal. It is
not — `archive_previous_records()` renames a shadowed record to
`<stem>.<its _launch.utc, colons stripped>.json`, and
`launched/T20_LC_c.2026-08-31T001242Z.json` matches `LAUNCH_LOG.tsv` row
`2026-08-31T00:12:42Z` exactly. It was launched, then archived on re-arm.

### Sense (ii) — committed row vs the copy the daemon actually launched

> `PLANT[sense-ii] target=VMFL006-R2.json injected=1 substantive key;
> reader newly reported it=True -> DISCRIMINATED`

| | count |
|---|---|
| launched copies differing from their committed row — **RAW** | **180** |
| ... after subtracting the daemon's own keys | **1** |
| launched copies with no committed origin at HEAD | 43 |

Differing-key histogram across the raw set — `_launch` **180**, `_field_classes`
**140**, `_grading_freeze` **9**, and then five keys occurring **once each**, all on one
file. The first three are written by `launch()` itself (`meta["_launch"]`,
`meta["_field_classes"]`, `meta[gfg.GRADING_FREEZE_STAMP]`).

**The supervisor's hazard 2 is confirmed and quantified: 179 of the 180 raw
differences are the daemon's own behaviour, present once per launch. Reporting them as
findings would be reporting one daemon behaviour ~180 times.** The daemon-subtracted
residue is **1**, and it is cfd's own — §3.

### Sense (iii) — LAUNCH_LOG.tsv rows vs run roots

> `PLANT[sense-iii] injected=1 log row naming a directory that cannot exist;
> seen_as_missing=True delta=1 -> DISCRIMINATED`

366 rows; **366 run roots exist; 0 absent; 0 malformed.** No divergence in this sense.

The file is also **append-only**: 321 lines at HEAD, 366 on disk, 45 appended, and the
first 321 lines are **byte-identical** to the committed blob.

> `PLANT[launchlog] injected=1 mutated prefix line; reader reported a difference
> -> DISCRIMINATED`

No history was rewritten. Appended rows: ansys 13, cfd 7, dafoam 17, heat-transfer 8.

---

## 2. Classification — kind, count, one named example

| # | Kind | Count | Cause | Reading | Named example |
|---|---|---|---|---|---|
| K1 | Pending row consumed by a launch (`D` + `??`) | 144 | **DAEMON** | benign | `cfd/F28G_L1_dp1000_U20.json` → `cfd/launched/F28G_L1_dp1000_U20.json` |
| K2 | Daemon metadata injected into the launched copy | 179 | **DAEMON** | benign | `cfd/launched/JF1G_P0_C4_CMU010_A0.json` — differs in `_launch` **only** |
| K3 | Archiver rename on re-arm | 15 | **DAEMON** | benign | `cfd/launched/RUNG0_MESH_IMPORT.2026-09-03T173317Z.json` |
| K4 | Pending row never committed before the daemon consumed it | 28 | **TEAM** (foreign) | filing gap | `heat-transfer/launched/K0eR3_D0_A.json` |
| K5 | **Team edit to a launched row** | **1** | **TEAM (cfd)** | see §3 | `cfd/launched/RUNG0_MESH_IMPORT.json` |
| K6 | Non-sha `prereg_commit` (`FEASIBILITY` / `PHYSICS`) | 18 | TEAM | **convention, not a defect** | `cfd/launched/F28_FEAS_L1_dp1000_U20.json` |
| K7 | `LAUNCH_LOG.tsv` appended since HEAD | 45 rows | DAEMON | benign | append-only, verified byte-wise |

**K1+K2+K3 = the daemon doing its job**, and they account for essentially the whole
367-line surface. Only **K4** and **K5** are team-caused at all.

**K4** is entirely foreign — **dafoam 9, heat-transfer 19, cfd 0**. Each row was
enqueued and consumed before anyone committed it, so the queue entry exists only in
`launched/`. Tested for consequence: 25 of 28 carry a `prereg_commit` that **is a real
commit in this repo and whose `prereg_path` resolves at that commit**; the other 3 are
K6, below. **Named for their owners, inspected, not touched.**

> `PLANT[prereg] injected=1 all-zero sha; reader classified it as a real commit=False
> -> DISCRIMINATED`

**K6 is a correction to this lane's own first reading, recorded rather than quietly
dropped.** The census initially printed three rows as `DEFECT — COMMIT-NOT-IN-REPO`
(`dafoam/SO3AF.json`, `heat-transfer/T22_CHTb_L1_R2.json`,
`heat-transfer/T25_MOD_L1_DT025.json`). They are not defects. `FEASIBILITY` is an
established lab convention for non-verdict-bearing probes, and **cfd is its heaviest
user (13 of the 18)**; all 14 cfd instances are self-labelled `FEASIBILITY` or
`DIAGNOSTIC`. The three flagged rows were simply the uncommitted subset of a convention
already in wide use. **That label is withdrawn.** It is exactly the failure the brief
warned against — a bookkeeping difference dressed up as a physics finding.

---

## 3. Rows where the divergence could change a VERDICT

**Count: ZERO. No row is named here.**

There is exactly one candidate, and it does not survive inspection as a physics matter:

**`verification/queue/cfd/launched/RUNG0_MESH_IMPORT.json`** — cfd's own, and the sole
daemon-subtracted residue in sense (ii). On disk `attempt = 3`; at HEAD `attempt = 2`.
The on-disk copy adds `attempt_3_authorisation`, `attempt_3_preconditions_satisfied`,
`cost_note_attempt_3`, and rewrites `attempt_2_disclosure`. A third launch **did**
occur — `LAUNCH_LOG.tsv` 2026-09-03T17:46:32Z, pid 292747 — and left artifacts under
`verification/runs/RUNG0_MESH_IMPORT_runs/`.

The rule-2 test is whether a **gate, threshold, cap or label** moved. Field by field:

| field | HEAD | disk |
|---|---|---|
| `prereg_commit` | `d127d83d…` | **unchanged** |
| `prereg_path` | `verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md` | **unchanged** |
| `grading_freeze` | `…/analyse_rung0.py` | **unchanged** |
| `cost_core_min_estimate` | 7.5 | **unchanged** |
| `cap_core_min_registered` | 23.0 | **unchanged** |
| `launch_cmd`, `cwd`, `ranks` | — | **unchanged** |
| `label` | "NO `PASS` IS REACHABLE FROM THIS ITEM" | **unchanged** |

**Nothing that could move a verdict moved.** The divergence is an attempt counter and
disclosure prose — a **bookkeeping defect**: the record of attempt 3 lives on disk and
not at HEAD. Sanaa's universal rule of 2026-08-26 holds and so does its converse; this
is not dressed up as a physics finding. The honest statement is that
`verification/queue/cfd/launched/RUNG0_MESH_IMPORT.json` is **uncommitted**, and the
remedy is a commit, not a re-run.

---

## 4. Recommended route — either/or

**This lane is not authorised to act and has not.** Both options need the cfd
supervisor's instruction; neither is started.

**Option A — commit the cfd residue only (RECOMMENDED).** One file,
`verification/queue/cfd/launched/RUNG0_MESH_IMPORT.json`, under the rule-10
private-index protocol. Closes the only team-caused cfd divergence. Cost: **< 1
core-min**, no solver compute. Needs: the supervisor's instruction, and their personal
confirmation that attempt 3's authorisation prose is theirs — this lane cannot verify a
supervisor's own authorisation on their behalf (rule 9).
*Risk:* effectively none; no gate, threshold, cap or label moves.

**Option B — lab-wide queue reconciliation.** Commit all 144 launch-consumption pairs
and the 28 never-committed rows across four teams. Cost: **~5–10 core-min** of
inspection, no solver compute. **This lane must not do it** — 143 of the 144 pairs and
all 28 never-committed rows belong to closure, dafoam, heat-transfer and ansys, and
re-filing another team's rows is exactly what the scope forbids.
*Risk:* one agent committing four teams' queue state is how foreign rows get landed
without their owners' reading.

**Recommendation: A, and refer B to the chief.**

---

## 5. What goes to the chief rather than to the cfd supervisor

**The divergence is lab-wide, not cfd's**, and that routing is the main structural
finding. Of the 144 launch-consumption pairs, **cfd owns 1**; closure owns 80. Of the
28 never-committed rows, **cfd owns 0**. cfd's entire team-caused share of a 367-line
surface is **one file**.

Three items are the chief's, not this supervisor's:

1. **The uncommitted-queue-state backlog is a lab-wide habit, not a team defect.** No
   team commits its queue rows before the daemon consumes them. That is a standing
   condition of running a live daemon against a shared tree, and it needs one ruling,
   not five.
2. **`queue_runner.py:598-606` overwrites every team's `_field_classes` with a fixed
   template on every launch.** Measured here: it fires on **140** launched rows across
   **all six** teams. Whether the daemon should be overwriting a field teams author is a
   cross-team question about a shared instrument. *(Established independently by the cfd
   supervisor on F28G L1; this census quantifies its reach.)*
3. **Any reader that diffs a committed row against its launched copy will report ~180
   differences of which 179 are the daemon's.** Any future queue audit needs the
   daemon-key subtraction or it will manufacture a false finding at scale.

---

## 6. The 129 figure — NOT REPRODUCED

The commissioning brief named "roughly 129 rows" and flagged it as unverified. **No
reading of the queue surface yields 129.** Tested, at 22:18Z:

| value | reading |
|---|---|
| 367 | all status lines under `verification/queue/` |
| 151 | all `D` |
| **144** | `D` at PENDING paths *(nearest structural quantity)* |
| **130** | `D` at PENDING, excluding ansys *(nearest value)* |
| 143 | `D` at PENDING, excluding cfd |
| 174 / 165 | all `??` / `??` under `launched/` |
| 42 / 193 | all `M` / `D`+`M` |
| 180 | raw sense-(ii) differences |

129 is not among them, and no combination tested produces it. The nearest neighbours
are **130** and **144**. Reported as the brief directed: a number that cannot be
reproduced is itself a finding.

---

## 7. Cost

Zero solver compute. Inspection only: two full census passes plus targeted git reads,
~4 wall-minutes at 1 rank ≈ **4 core-min**, against no pre-registered estimate because
no compute was pre-registered — this is an inspection task, not a run.
`cost_basis`: **derived from wall time at 1 rank, not read from billing** — the box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 8. Verdict

**NOT A RESULT is not the right label and is not used here** — this is a
characterisation, not a gate. No gate was pre-registered and none was read.

On the one question that carries the fixed vocabulary — *are there rows whose
divergence could change a verdict?* — the answer is measured, with the reader's plant
line printed for each sense: **zero such rows.** The cfd-owned residue
(`RUNG0_MESH_IMPORT.json`) is a bookkeeping defect and is named as one.
