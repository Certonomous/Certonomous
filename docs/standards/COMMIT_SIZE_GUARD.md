# Commit-size guard — pre-registration

**Owner:** cfd-supervisor (tooling). **Build item:** Sanaa's standing directives
2026-08-27T16:54Z §1, *"pre-commit guard blocks >50 files or >5 MB without a manifest"* and
*"logs and attempt dirs stay out of git"*. **Artifact:** `scripts/check_commit_size.py`.
**This document is the frozen behaviour spec; it is written BEFORE the guard, so the guard
cannot be shaped to pass its own test.** Every clause ships an L-314 planted-failure proof.

**Named instance this exists to catch:** heat-transfer's `05241ab2` — 172 files, 3.2 M lines
of `log.solve`, landed with no manifest. Not a rebuke; it is the measurement that sized the
thresholds.

## 1. What it does

Reads a **tree** (a private-index `write-tree` result, or `HEAD` vs a candidate tree) and
**REPORTS** its verdict. It never kills, never deletes, never touches git, never writes into
the index. Exit codes: **0** accept, **2** refuse. It is invoked by the committer before
`commit-tree`; the caller MUST test the exit code.

## 2. Refusal clauses — each independent, each separately named in the output

| clause | refuses when | rationale |
|---|---|---|
| `COUNT` | > **50** files added or modified | Sanaa §1 |
| `BYTES` | > **5 MB** total added bytes | Sanaa §1 |
| `LOGS` | any path matching `log.*`, `*/log.*`, `*.log` | logs stay out of git (§1) |
| `ATTEMPT` | any path matching `attempt*/`, `*_attempt*/`, `scratch/`, `__pycache__/` | attempt dirs stay out of git (§1) |

**The manifest exemption applies to `COUNT` and `BYTES` ONLY.** A commit may exceed either
threshold if it carries a manifest — a tracked file in the same tree naming what is being
landed and why, one line per group, with a total. **`LOGS` and `ATTEMPT` are NOT
exemptible by manifest**: a manifest explains bulk, it does not make a solver log a
repository artifact. Bulk evidence is filed by digest outside git
(`/home/ubuntu/certonomous-runs/`), per `docs/LOCATIONS.md`.

## 3. What it must NOT do

Never infer intent, never auto-generate the manifest, never rewrite paths, never `git add`,
never delete. A guard that fixes its own finding cannot be trusted to report it.

## 4. Selftest and L-314 planted-failure proof

A guard that reports on ITSELF is not a guard: **plant a failure and prove it refuses**, exactly
as a comparator plants a perturbation to prove a reader can see.

| control | tree | expected |
|---|---|---|
| 1 | 50 files, 4.9 MB, no manifest | **accept**, rc 0 — the boundary is inclusive |
| 2 | 51 files, no manifest | refuse `COUNT`, rc 2 |
| 3 | 5 MB + 1 byte, no manifest | refuse `BYTES`, rc 2 |
| 4 | 51 files **with** manifest | **accept**, rc 0 |
| 5 | one `verification/runs/X/log.solve` | refuse `LOGS`, rc 2 |
| 6 | one `log.solve` **with** manifest | refuse `LOGS` anyway, rc 2 — proves the exemption is scoped |
| 7 | one `attempt3/` path | refuse `ATTEMPT`, rc 2 |
| 8 | `05241ab2`'s real tree, replayed | refuse `COUNT` + `LOGS`, rc 2 — the named instance |

**Planted failures — each must FLIP a control, proving the clause is reachable, not merely present:**
- disable `COUNT` → control 2 accepts; disable `BYTES` → control 3 accepts;
- disable `LOGS` → controls 5 and 6 accept;
- widen the manifest exemption to `LOGS` → **control 6 accepts, which is the defect this spec
  forbids**; the selftest must show it can be reintroduced and caught.

**L-314 Instance 1, and cfd paid for it again today:** `set -e` is NOT in force in the agent
Bash context — an assertion inside a `python3` heredoc raises and **the surrounding shell
continues**. At `da7e1477` a cfd assertion aborted and the commit landed anyway. Therefore
control 9: **a caller that ignores `set -e` must still detect the refusal**, i.e. the guard's
rc is explicitly tested and its refusal line is greppable. A guard whose failure is only
printed is not a gate.

## 5. Rollout

Advisory for one working session (refusals reported, commits proceed), so its false-positive
rate is measured on real traffic before it blocks anyone. The measured rate is boarded. It
becomes blocking only after that, and never by an agent's own say-so.

---

## AMENDMENT 1 — 2026-08-27, cfd-supervisor as named Owner. Spec v1.0 → v1.1

**lines whose number changed above this section: 0** (74 lines before this heading,
74 identical lines after). The original text above is **struck nowhere and rewritten
nowhere**; every change below is stated here and only here (`CLAUDE.md` rule 6).

Occasion: the guard was built to the frozen text above and its **selftest and replay
found four things the frozen text got wrong or left open**. Rollout remains **ADVISORY**
per §5 — nothing here makes the guard blocking, and nothing may, on any agent's say-so.

### (a) Refusal wording — the message understated the guard that shipped

`COUNT` and `BYTES` said *"no manifest in the tree"*. The code requires more than that
and always did: `manifest_texts_from_tree()` iterates the **changes** and takes only
`status in ("A","M")`, so **the manifest must be Added or Modified by the very commit it
explains**. A pre-existing `COMMIT_MANIFEST.md` sitting in the repository exempts
nothing — otherwise one stale file would permanently exempt every future bulk commit.
The messages now read **"no manifest IN THIS COMMIT"** and say so.

### (b) `5 MB` is **5,000,000 bytes**, written down so nobody re-guesses it

§2 left decimal-vs-binary open. `5 * 1024 * 1024 = 5,242,880` is the **looser** reading
by 242,880 bytes. The **stricter decimal 5,000,000** is fixed here, because an
implementer must never resolve an ambiguity in the direction that widens it.

### (b2) The manifest's filename is **`COMMIT_MANIFEST.md`**, exact and reserved

§2 named no file. Measured at HEAD: **18 tracked files whose basename contains
`MANIFEST`, across eight unrelated purposes** (`TOOLCHAIN_MANIFEST.txt`,
`VM2026R1_SHA256_MANIFEST.txt`, `AV1R_RENAME_MANIFEST.txt`, `BUILD_MANIFEST.txt`,
`HEAVY_ARTEFACT_MANIFEST.md`, `MANIFEST.json`, `MANIFEST_t1..t4.txt`, `MANIFEST.md`).
**Any glob is therefore a hole that silently exempts bulk commits**, and a guard with a
silent exemption is worse than no guard. Found live: a basename pattern matched
`05241ab2`'s two `HEAVY_ARTEFACT_MANIFEST.md` files — which manifest paths *deliberately
not at HEAD* — and wrongly exempted its `COUNT`. **`COMMIT_MANIFEST.md` occurs zero
times at HEAD, so nothing is grandfathered**: every team must add the file to claim the
exemption.

### (c) `ATTEMPT` matches **leading-dot variants**

A hidden attempt directory is still an attempt directory, and a leading dot is precisely
how one would evade the clause. Found live: `05241ab2` landed `.attempt1_stale/`, which
the frozen pattern did not match. A single leading dot is stripped from each directory
component before matching.

### (d) `ATTEMPT` **does not match under `verification/runs/`**

The clause was written to keep **scratch** attempt directories out of git. It was **not**
written to reject **filed run outputs**, and `verification/runs/` is the correct filing
location for those (`FILING_CHARTER`); `attemptN_<descriptor>/` is this lab's legitimate
convention for successive attempts at a rung. **As frozen, the moment this guard went
blocking it would have refused every legitimate re-attempt the lab files.** The `0/200`
`ATTEMPT` score in the first replay concealed that completely — those paths simply were
not re-touched in the sample, so the forward-looking rate for that clause was far higher
than zero. The clause keeps its teeth everywhere outside a run tree.

### Measurements this amendment is based on, and the one that contradicts its rationale

Re-measured before and after, in **one process over one frozen commit list** (the window
drifts under live traffic — an earlier sample of a different 200 read 8.0 %):

| | commits | accepted | refused | rate | clauses |
|---|---|---|---|---|---|
| before AMENDMENT 1 | 200 | 185 | 15 | 7.5 % | LOGS 14, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |
| after AMENDMENT 1 | 200 | 185 | 15 | 7.5 % | LOGS 14, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |

**Delta on the commit sample is zero**, which is exactly why the sample was the wrong
instrument. The forward-looking exposure is where (c) and (d) act: **tracked paths at
HEAD matching `ATTEMPT` fall from 64 to 14, a delta of −50.**

**CONTRADICTED, AND RECORDED RATHER THAN QUIETLY FIXED:** the ruling's stated basis was
that *all* tracked attempt directories sit under `verification/runs/`. **They do not.**
There are **6** distinct attempt directories, not 22, and **2 of the 6 sit outside a run
tree**, carrying the **14 paths that still match** after this amendment:

- `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2`
- `cases/dafoam/ladder-a/A4/curriculum_D3_attempt2`

The other 4 (`F12_runs/attempt2_coarse_workshop_M0.734_a2.79`,
`F12_runs/mesh_ladder_attempt2_2026-08-25`, `F6a_GREENBLATT_runs/attempt2_Re936k`,
`F6a_GREENBLATT_runs/attempt3_Re936k`) are under `verification/runs/` and are now exempt.
The exemption granted here is **exactly the one ruled — `verification/runs/` and nothing
else.** Whether dafoam's two case-tree attempt directories deserve the same treatment is
**open and unruled**; the implementer did not extend the exemption to `cases/` to make
the rationale come true, because a spec quietly widened by its implementer is the defect
both guards exist to prevent.

### Controls added with this amendment (all planted, all shown able to fail)

- **7d** — `cases/X/.attempt1_stale/S_KE_x/0/T` **refuses** `ATTEMPT` (c).
- **7r** — `verification/runs/F6a_GREENBLATT_runs/attempt3_Re936k/grading.json`
  **accepts** (d); `cases/X/attempt3/case.foam` still **refuses**, so the clause keeps
  its teeth outside run trees.
- The planted failure for (d) runs the **other way**, because (d) is an *exemption*:
  removing it must make an **accepting** control **refuse**. An exemption that cannot be
  shown to change an outcome is not known to be doing anything.

`--selftest` now reports **27 controls**, rc 0; rc 2 under `python3 -O`.

---

## AMENDMENT 2 — 2026-08-27, on verification's ruling D538/D539 (`2e158e3a`), relayed by the Owner. v1.1 → v1.2

**lines whose number changed above this section: 0** (175 lines before this heading: the
74 original lines byte-identical to HEAD, plus AMENDMENT 1 untouched).

**D539 is recorded first because it governs everything else here: ADVISORY is the only
state any agent may put this guard in. Blocking is Sanaa's alone** — not a lane's, not a
supervisor's, not verification's. Nothing in this document, and no report written from
it, is a request to flip that.

### (1) The 15 `LOGS` firings, classified: **0 true / 14 false**

Re-measured on a drifted window (peers commit constantly), the count is **14**, not 15.
Verification's point decides this clause: *"8 % refused" is not "8 % defective."*

| commit | logs | bytes | ruling on `LOGS` |
|---|---|---|---|
| `ae20d137` | 6 | 20,377 | FALSE — `log.blockMesh`, `log.checkMesh.build`: mesh-admission evidence |
| `137332ae` | 1 | 2,665 | FALSE — `log.convergence_*.txt` comparator transcript |
| `27e64502` | 1 | 2,968 | FALSE — `log.analyse_t4b` transcript |
| `f684b692` | 1 | 783 | FALSE — `log.analyse_t9aR1b` transcript |
| `9f9cb54e` | 1 | 1,488 | FALSE — `log.analyse_t14` transcript |
| `4bab6aff` | 1 | 3,717 | FALSE — `log.analyse_t13` transcript |
| `feee0ab0` | 1 | 7,342 | FALSE — `log.analyse_k0f.ext1` transcript |
| `05241ab2` | 28 | 276,711,923 | FALSE on `LOGS` — **TRUE on `BYTES`** |
| `8e7d9164` | 21 | 98,289 | FALSE — 18 × `log.checkMesh` |
| `59110074` | 20 | 15,762,725 | FALSE on `LOGS` — **TRUE on `BYTES`** |
| `994daa49` | 12 | 48,874 | FALSE — `log.blockMesh`, `log.checkMesh.build` |
| `de0683c7` | 2 | 8,144 | FALSE — mesh-admission pair |
| `fd975fcf` | 2 | 8,499 | FALSE — mesh-admission pair |
| `db2c7f9a` | 81 | 20,200,150 | FALSE on `LOGS` — **TRUE on `BYTES` + `COUNT`** |

**The evidence for "false", measured, not asserted:**

- **0 of 14** carry a single log path outside `verification/runs/` — the location
  `FILING_CHARTER` mandates for run outputs. Every firing is correctly filed.
- **These logs are what records cite.** At HEAD: **132** `.md` records cite
  `log.checkMesh`, **93** cite `log.simpleFoam`, **65** cite `log.solve`, **61** cite
  `log.blockMesh`, **19** cite `log.analyse`. `docs/standards/MESH_STANDARD.md` refers to
  `checkMesh` **27** times — **mesh admission gates on that output.**
- **`CLAUDE.md` standing rule 4 cannot be evaluated without the solver log.** The strict
  completion rule requires `rc = 0`, an `End` line, last time == `endTime` and an
  `ExecutionTime` count == `endTime`. Those are read *from the solver log*; the graders
  parse `ExecutionTime` out of it. Removing solver logs from git would make the lab's
  own completion rule unverifiable from the repository.
- **`LOGS` adds nothing on the commits that were genuinely defective.** With `LOGS`
  disabled, **5 of the 14 are still refused** — by `COUNT`/`BYTES` — and those five
  include all three bulk commits. **The archetype `05241ab2` is a true positive on
  `BYTES` (276.7 MB), not on `LOGS`.** Its defect was never that a log was in git; it was
  **276.7 MB** of it.

**Consequence, stated and NOT acted on:** the false-positive rate for `LOGS` is
**material — 14 of 14** — and by the Owner's own standard the pattern needs narrowing
before anyone considers asking Sanaa for anything. A candidate narrowing is to exempt
`verification/runs/` as ruling (d) did for `ATTEMPT`, leaving `BYTES`/`COUNT` to catch
bulk. **The implementer did not make that change.** The exemption list is frozen and
widening it is the Owner's call; a spec quietly widened by its implementer is the defect
both guards exist to prevent. `LOGS` is unchanged and still fires.

### (2) `EMPTY` merge carve-out — and a corrected premise

`EMPTY` does not fire on a commit with **>= 2 parents whose tree equals its first
parent's**. It is **not silent**: the carve-out emits its own `MERGE:` note.

**MEASURED, AND IT CORRECTS THE PREMISE THE CARVE-OUT WAS ORDERED ON.** The stated basis
was that this repository has linear history by construction, so a merge is anomalous.
**Merges are rare here, not absent: 15 in the last 500 commits, 3.0 %.** Lane work under
the private-index protocol never merges, which is what makes a merge worth *reporting* —
but at 3 % a silent carve-out would have hidden real cases, so the note is load-bearing.

**L-314 proof, three controls:**

- **E1** — the **real** commit `5e45a5a9`: one parent, tree == parent tree, 0 paths.
  **Still refuses `EMPTY`.** The carve-out does not reach a non-merge.
- **E2** — 2 parents, tree == first parent's: carved out **and** reported as a `MERGE:`
  note.
- **Plant** — widen the carve-out to single-parent commits: **E1 flips to ACCEPT.**
  Without that mutation the carve-out would be an untested hole in the one clause
  verification ruled load-bearing.

**A lane error corrected on the record:** `5e45a5a9` was reported as *"a 2-parent merge"*
from `git rev-list --parents -n1 | wc -w` = 2, which is sha **plus one** parent. It is a
genuinely empty **single-parent** commit, so **its `EMPTY` firing is a TRUE positive and
`EMPTY`'s false-positive count on 200 commits is zero.** Characterise a commit from
`git log -1 --format=%P` and `diff-tree`, never from the shape expected of it.

### (3) `ATTEMPT` fired **zero times on real data**, and that is not a clean result

Boarded plainly: on 200 real commits `ATTEMPT` scored **0**. **Its only evidence of
reachability is its planted control.** Read together with AMENDMENT 1 (d), the honest
reading is that **the clause was aimed at the wrong target**: every tracked path it
matched sat under `verification/runs/`, which is correct filing, and the `0/200` score
concealed that rather than vindicating the clause. **A clause that never fires on real
traffic and whose only real-world matches are legitimate is a clause whose scope is
wrong, not a clause that is working.** After (d) its forward-looking exposure falls from
64 tracked paths to 14 — and those 14 are the `cases/dafoam/` directories AMENDMENT 1
records as open and unruled.

`--selftest` now reports **30 controls**, rc 0; rc 2 under `python3 -O`.

---

## AMENDMENT 3 — 2026-08-27, cfd-supervisor as named Owner. **Approved by Sanaa.** v1.2 → v1.3

**lines whose number changed above this section: 0** (277 lines before this heading: the
74 original lines byte-identical to HEAD, plus AMENDMENT 1 and AMENDMENT 2 untouched —
verified by byte-comparing the first 277 lines of this file against `HEAD:` blob, not by
writing the words).

**D539 still governs: the guard is ADVISORY.** This amendment narrows a clause; it does
not move the guard one step toward blocking, and nothing in it is a request to.

### The ruling

**`verification/runs/**/log.*` is EXEMPT from the `LOGS` clause; `BYTES` (5,000,000) and
`COUNT` (50) keep catching bulk.** Sanaa approved it at `8ed55f26` (`docs/LAB_STATE.md`,
CHIEF section). It is **exactly** the exemption she named and nothing else — see §3 below
for a second candidate class deliberately **not** taken.

### The basis: AMENDMENT 2 (1) measured `LOGS` at 0 true / 14 false

The clause was implemented by cfd, measured by cfd, and reported against itself.
AMENDMENT 2 (1) above records the classification on 200 real commits: **0 true positives,
14 false positives.** Zero of the 14 carried a single log path outside
`verification/runs/`. The archetype `05241ab2` is a **true** positive on `BYTES`
(276,711,923 added bytes) and a **false** one on `LOGS` — its defect was never that a log
was in git, it was 276.7 MB of it. And these logs are what the lab's own records cite:
`CLAUDE.md` standing rule 4's completion evidence — `rc = 0`, an `End` line, last time ==
`endTime`, an `ExecutionTime` count == `endTime` — is **read from the solver log**, so
evicting solver logs from git would make the lab's own completion rule unverifiable from
the repository.

### Implementation — one constant, not two

`is_log_path(path, mut=None)` returns `False` for any path under `RUN_TREE_PREFIX`. That
is the **same** constant `is_attempt_path` uses for AMENDMENT 1 (d), trailing slash
included — the trailing slash is what stops `verification/runs_backup/log.solve` slipping
through. A second, divergent prefix test would be two exemptions drifting apart.
`LOGS` remains **NOT EXEMPTIBLE BY MANIFEST**, and `BYTES`/`COUNT` are untouched.

### The sweep: 7.5 % → 3.0 %, `LOGS` 14 → 0, on ONE frozen commit list

**The original sweep harness is not on disk** — nothing under `scripts/` references
`check_commit_size`. The method was reconstructed as line 137 above describes it ("one
process over one frozen commit list") and the reconstruction was **proven, not asserted**:
replaying the pre-amendment guard blob over the reconstructed list reproduces the
"after AMENDMENT 1" row of the table at lines 139–142 **exactly**. The list is the 200
commits `94ceebe7` (newest) → `db2c7f9a` (oldest), chosen because `db2c7f9a` — the last
commit named in AMENDMENT 2 (1)'s table — falls at depth exactly 200 from `94ceebe7`.

**On the 8.0 % question, settled here so nobody re-opens it:** line 137 above states in
terms that the rate *"drifts under live traffic — an earlier sample of a different 200
read 8.0 %"*, and this document's own row is **7.5 %**. The 8.0 % on the cfd board is that
earlier, different sample. There is no discrepancy.

| | commits | accepted | refused | rate | clauses |
|---|---|---|---|---|---|
| before AMENDMENT 3 | 200 | 185 | 15 | 7.5 % | LOGS 14, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |
| after AMENDMENT 3 | 200 | 194 | 6 | **3.0 %** | **LOGS 0**, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |

- **No `BYTES`, `COUNT`, `ATTEMPT` or `EMPTY` outcome moved on any of the 200 commits** —
  checked per commit, set-difference in both directions, zero movements.
- Of the 14 commits that lost `LOGS`, **5 are still refused** by `COUNT`/`BYTES`
  (`db2c7f9a`, `05241ab2`, `59110074` on both; `994daa49`, `ae20d137` on `COUNT`),
  independently reproducing AMENDMENT 2 (1)'s "5 of the 14 are still refused".
- `LOGS`'s post-amendment split on this sample is **0 firings — 0 true, 0 false**, because
  all **178** log-pattern paths added or modified across the whole window sit under
  `verification/runs/` and **0** sit outside. Measured from raw `fnmatch` on basenames,
  independently of the amended predicate, so the zero is a reading and not a tautology.

### Forward exposure: the clause is narrowed, not gutted

Measured at HEAD by the Owner and reproduced independently by the implementer, from
`git ls-tree -r HEAD` with the same two basename patterns:

| tracked log-pattern paths at HEAD | count | share |
|---|---|---|
| total | **1,395** | 100 % |
| under `verification/runs/` — now exempt | **1,187** | 85.1 % |
| outside a run tree — `LOGS` still fires | **208** | 14.9 % |

The amendment removes **85 %** of the clause's surface — precisely the surface measured
0-true/14-false — and leaves **208 live targets**: `cases/committee-grids` 80, `cases/tmr`
47, `research/race` 39, `cases/ansys_verification` 23, `*/mesh_certificates/` 18,
`cases/mega-batch` 1.

### Controls: 30 → 35, and TWO DEPARTURES FROM THE FROZEN CONTROL TABLE, DECLARED

Both departures are recorded here because an expectation quietly edited to fit an outcome
is the defect this guard exists to prevent. **In neither case was an expectation edited to
fit.**

**(i) Controls 5 and 6 — the TREE moved, the EXPECTATION was kept.** The frozen table
(lines 52–53) writes control 5 as `verification/runs/X/log.solve` → refuse `LOGS`, and
control 6 as the same path **with** a manifest → refuse `LOGS` anyway. That path is
exactly what this amendment exempts.

- **Before:** control 5 = `verification/runs/X/log.solve` → refuses `LOGS`; control 6 =
  the same + `COMMIT_MANIFEST.md` → refuses `LOGS`.
- **After:** control 5 = `cases/X/log.solve` → refuses `LOGS`; control 6 = the same +
  manifest → refuses `LOGS`. Their **purpose** is intact — the clause fires, and a
  manifest does not exempt it — proven on a path where the clause still has all its teeth.
- The original tree is **retained verbatim** as control **L3a**, with its new and opposite
  expectation asserted. The amendment *is* that flip, and it is asserted rather than
  deleted.

**(ii) Control 8 (`05241ab2` replayed through the real git adapter) — the expectation
changed, and the control got STRICTER.** All **28** of that commit's log paths sit under
`verification/runs/` (measured on the real tree, not assumed), so `LOGS` no longer fires
on it.

- **Before:** `{COUNT, LOGS} ⊆ got`.
- **After:** `{COUNT, BYTES} ⊆ got`, **plus a new explicit failure branch if `LOGS` fires
  at all** — which would mean the exemption is not reaching the real git adapter. `BYTES`
  is now asserted where it was previously unasserted. This is the amendment's own basis
  stated as a control: the archetype is a `BYTES` catch, not a `LOGS` catch.

**New controls, all planted, all shown able to fail:**

- **L3a** — `verification/runs/X/log.solve` alone → **ACCEPTS**.
- **L3b** — the same basename outside a run tree, `cases/F27_WOMERSLEY_PIPE/log.solve` →
  **refuses `LOGS`**.
- **L3c** — a 40 MB `verification/runs/X/log.solve` with **no** manifest → **refuses
  `BYTES`**. The exemption did not open a bulk hole.
- **L3d** — 51 exempt run-tree `log.solve` paths with **no** manifest → **refuses
  `COUNT`**. `COUNT` is untouched and still catches bulk on exempt paths.
- **Plant** — AMENDMENT 3 is an *exemption*, so its planted failure runs the **other way**,
  exactly as (d)'s does: `disable_logs_runs_exemption=True` must make the **accepting**
  control L3a **refuse under `LOGS`**, and `--selftest` fails loudly if it does not. An
  exemption that cannot be shown to change an outcome is not known to be doing anything.

### 3. OBSERVED, UNRULED, AND DELIBERATELY NOT ACTED ON: mesh-admission certificates

**18** of the 208 remaining targets are `*/mesh_certificates/log.blockMesh`,
`log.checkMesh` and `log.topoSet` — deliberately filed mesh-admission evidence that
`docs/standards/MESH_STANDARD.md` requires a case to carry, and which that standard
refers to 27 times. **On the same reasoning that earned this amendment, they look like
false positives too.**

**They are NOT exempted, and this implementer did not widen the exemption to reach them.**
Sanaa approved `verification/runs/**/log.*` and nothing else. Widening her ruling to a
class she did not name would be precisely the permission laundering `CLAUDE.md` rule 9
forbids — approval of an item is approval of **its** scope, never a new ceiling — and a
spec quietly widened by its implementer is the defect both guards exist to prevent. The
class is recorded here with its count and its three basenames and is **open, unruled, and
on Sanaa's desk**.

`--selftest` now reports **35 controls** (was 30), rc 0; rc 2 under `python3 -O`, refused
at module entry before any work.
