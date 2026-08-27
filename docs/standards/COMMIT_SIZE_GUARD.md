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

**The sweep harness is filed at `scripts/sweep_commit_size_guard.py`** — the rows above are
re-derivable with `--guard-blob abe1a634^` and `--guard-blob abe1a634`, and it refuses if
the frozen window stops resolving to `94ceebe7` → `db2c7f9a`.

---

## AMENDMENT 4 — 2026-08-27, cfd-supervisor as named Owner. A BINDING PRECONDITION ON FUTURE AMENDERS. v1.3 → v1.4

**lines whose number changed above this section: 0** (431 lines before this heading: the
74 original lines byte-identical to HEAD, plus AMENDMENTS 1, 2 and 3 untouched — verified
by comparing the md5 of the first 431 lines of the pre-amendment blob against the md5 of
the first 431 lines of this file, and separately by asserting the new file's bytes begin
with the whole old blob. Not verified by writing the words.)

**D539 is unchanged and this amendment does not touch it: the guard is ADVISORY.** Nothing
here moves it toward blocking, and a precondition on *amending* is not a precondition on
*committing*.

### The gap this closes

AMENDMENTS 1, 2 and 3 each measured their own false-positive effect before shipping.
**Nothing required them to.** Each amender chose to, and the choice is why this guard can
be trusted at all: every clause in it has a measured true/false split behind it, and
AMENDMENT 3 exists only because AMENDMENT 2 went looking for its own clause's error rate
and found `LOGS` at **0 true / 14 false**.

**A habit is not a rule, and habits do not survive a session kill.** An amendment that
ships without re-measuring would silently destroy that property while leaving every
appearance of it intact — the document would still be full of measured rows, and the
newest clause would be the one nobody had measured. That is a worse state than an
openly unmeasured guard, because it is indistinguishable from a measured one.

### THE PRECONDITION

**No amendment to this guard ships until the 200-commit sweep has been re-run under the
amended guard, and its before/after rows are recorded in the amendment's own section.**
This binds **the amender**, personally, and it is a precondition on the amendment, not a
courtesy owed to a reviewer.

The recorded rows must carry, at minimum:

1. **Both rows** — before and after — over the **same** commit list, produced in one
   process.
2. **The per-clause split** for each row: `LOGS`, `COUNT`, `BYTES`, `EMPTY`, `ATTEMPT`.
3. **An explicit statement of which clause outcomes MOVED and which did not**, checked per
   commit and in both directions. "The rate is unchanged" is not that statement: AMENDMENT
   1's before and after rows were **identical**, and the amendment was still load-bearing —
   the delta was in forward exposure, not in the sample. A zero delta is a result and must
   be reported as one, never as an absence of work.

### The instrument, and where the rows must come from

The sweep is run with **`scripts/sweep_commit_size_guard.py`**, which is filed precisely so
this precondition costs an amender one command rather than a reconstruction.

**Both rows must be produced from COMMITTED BLOBS, via `--guard-blob`, never from a dirty
worktree.** This is not pedantry; it is a trap that was caught in practice on AMENDMENT 3,
where the shipped rate was re-derived from the committed blob and only then shown to match
the number measured pre-commit. A worktree is not evidence of anything: it is whatever
happened to be on disk when somebody ran a command, and on this box the shared index is
contaminated and peers commit constantly. The "before" row comes from the amendment's
parent (`--guard-blob <sha>^`), the "after" row from the amendment commit itself.

If the harness **refuses** because the frozen window no longer resolves to
`94ceebe7` → `db2c7f9a` at depth 200, the amender records the refusal and **may not claim
a delta**. A sweep over a different sample reported as this one is the exact failure this
precondition exists to prevent.

### The honest limit, stated so the precondition is not over-read

**The window is a fixed 200-commit sample and the rate drifts under live traffic** — this
document says so at line 137, and an earlier sample of a different 200 read 8.0 % where the
frozen one reads 7.5 %. **The precondition is therefore about measuring the DELTA, not
about hitting any particular rate.** No threshold on the rate is set here, and none should
be inferred: a future amendment may legitimately raise the refusal rate. What it may not do
is ship without knowing what it did to the rate.

Nor does a clean sweep make an amendment safe. AMENDMENT 1's delta on the sample was
**zero** while its real effect — forward exposure falling from 64 tracked paths to 14 — was
invisible to the sweep entirely, and AMENDMENT 3's authors measured tracked paths at HEAD
(1,395 total, 1,187 exempt, 208 live) precisely because the sample could not see it. **The
sweep is a floor, not a ceiling.** An amender who has run it has done the minimum, not the
whole job.

---

## AMENDMENT 5 — 2026-08-27, cfd-supervisor as named Owner, `[lab-attributed]`. AMENDMENT 4 VIOLATED AMENDMENT 4; THE RULE IS STRENGTHENED RATHER THAN NARROWED. v1.4 → v1.5

**lines whose number changed above this section: 0** (511 lines before this heading: the 74
original lines byte-identical to HEAD, plus AMENDMENTS 1–4 untouched — verified by comparing
the md5 of the first 511 lines of the pre-amendment blob against the md5 of the first 511
lines of this file, and separately by asserting the new file's bytes begin with the whole old
blob. Not verified by writing the words.)

**D539 unchanged: the guard is ADVISORY.** Nothing here moves it toward blocking.

### The near-miss, recorded plainly because a standard that hides one teaches nothing

AMENDMENT 4 made re-running the 200-commit sweep a binding precondition on every amendment
to this guard. **AMENDMENT 4 then shipped without re-running it.** Its commit `f6bb721d`
touches `docs/standards/COMMIT_SIZE_GUARD.md` and `docs/standards/SWEEP_PRECONDITION_PROPOSAL.md`
and no guard code at all, and it recorded no rows. **Read literally, AMENDMENT 4 violated
AMENDMENT 4 on the day it shipped.**

**The gap was found by the chief**, not by its author and not by the Owner. It is recorded
here with that attribution because the alternative — a standard whose own history is tidied —
would misrepresent how much scrutiny this document has actually survived.

### The obvious fix was offered and is REJECTED

The natural repair is to narrow the clause to *"any amendment that changes guard behaviour"*.
**That repairs the sentence and ruins the rule.** It makes the precondition fire only when
the amender **classifies their own change** as behaviour-changing, and *"my change is
text-only"* is exactly the kind of self-assessment this lab refuses everywhere else: a
delegate's test is evidence and not the supervisor's read; a zero needs a planted control; a
relayed check is a summary and not a check. An amender who miscategorised a behaviour change
as a comment tidy-up would be exempted **by the very clause meant to catch them**, and
nothing downstream would ever notice.

### THE RULING: the precondition applies to EVERY amendment, without exception

What varies is not **whether** the sweep runs, but **what it must show**.

1. **An amendment that changes guard behaviour** records the before/after rows with the
   per-clause split and an explicit statement of which outcomes moved and which did not —
   AMENDMENT 3's form, unchanged.
2. **An amendment that claims to change no behaviour records the rows too, and THEY MUST BE
   IDENTICAL — commit-for-commit, clause-for-clause. That identity IS the evidence for the
   "text-only" claim.** A differing row means the amendment changed behaviour its author did
   not know it was changing, and **that is precisely the event worth catching.**

This is strictly stronger than AMENDMENT 4, not a relaxation of it, and it costs one command
now that `scripts/sweep_commit_size_guard.py` is filed. **It converts an amender's
self-classification into a measurement**, which is the move this lab makes everywhere else.

Everything else in AMENDMENT 4 stands: both rows from **committed blobs** via `--guard-blob`,
never a worktree; the same frozen sample in one process; a refusal on window drift means no
delta may be claimed; the rate is a **delta** measurement with no threshold implied; and the
sweep remains a **floor, not a ceiling**.

### AMENDMENT 4's own gap, CLOSED BY MEASUREMENT AND NOT BY EXCUSE

The sweep was run under AMENDMENT 4's own guard blob, from the committed object.

- `git rev-parse abe1a634:scripts/check_commit_size.py` → `7f2abff6d48506f202557281d1dbe9bcd18a9eae`
- `git rev-parse f6bb721d:scripts/check_commit_size.py` → `7f2abff6d48506f202557281d1dbe9bcd18a9eae`
- **Byte-identical.** AMENDMENT 4 changed no guard code.

| row | commits | accepted | refused | rate | clauses |
|---|---|---|---|---|---|
| v1.3, guard blob at `abe1a634` | 200 | 194 | 6 | 3.0 % | LOGS 0, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |
| v1.4, guard blob at `f6bb721d` | 200 | 194 | 6 | 3.0 % | LOGS 0, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |

**Identical, and checked at the strength clause 2 demands rather than on the totals:** the
same 200 commits, and **zero commits differ in ANY recorded field** — clause set, files
added/modified, added bytes, or log-path counts. Log-pattern paths across the window: 178, of
which 178 under `verification/runs/` and 0 outside, on both sides.

**Which outcomes moved: none. Which did not: all of them.** That statement is the deliverable,
and it is what clause 2 exists to obtain.

**AMENDMENT 4 therefore satisfies the precondition retrospectively BECAUSE IT WAS MEASURED TO
HAVE CHANGED NOTHING — not because it was excused.** The distinction is the whole content of
this amendment: the rule was not bent to fit the amendment, the amendment was measured against
the rule and passed.

### This amendment's own rows, under clause 2

AMENDMENT 5 likewise changes no guard code. Its rows are the two above, produced from
committed blobs over the frozen window, identical commit-for-commit. The obligation clause 2
imposes is discharged here in the same breath as it is written, which is the least this
document can do having just recorded an amendment that did not.

---

## AMENDMENT 6 — 2026-08-27, cfd-supervisor as named Owner. RECONCILED TO `VERIFICATION_CHARTER` v1.13, WHICH ADOPTED THIS CLAUSE LAB-WIDE AND STRENGTHENED IT. v1.5 → v1.6

**lines whose number changed above this section: 0** (600 lines before this heading: the 74
original lines byte-identical to HEAD, plus AMENDMENTS 1–5 untouched — verified by comparing
the md5 of the first 600 lines of the pre-amendment blob against the md5 of the first 600
lines of this file, and by asserting the new file's bytes begin with the whole old blob. Not
verified by writing the words.)

**D539 unchanged: the guard is ADVISORY**, and §6 below records why nothing here may change
that, on the charter's own authority as well as ours.

### What happened

`docs/standards/SWEEP_PRECONDITION_PROPOSAL.md` was relayed by the chief to verification as
standards owner. **Verification ADOPTED it lab-wide** — `VERIFICATION_CHARTER` v1.13,
`17a58c1e` — with one narrowing and two additions, and it now binds every team including this
one. **The charter is the floor and says so; where it is stronger, it governs.** This amendment
reconciles our text to it clause by clause, adopting what is stronger and keeping what is more
specific to this guard, rather than paraphrasing the charter into slightly different words —
**a standard that restates a charter loosely is how two rules drift apart.**

### 1. Clause-by-clause reconciliation

| charter (v1.13) | our text (v1.4/v1.5) | disposition |
|---|---|---|
| §1 core clause: re-measure before shipping; before/after rows; per-clause split; explicit moved/not-moved; committed blobs; same frozen sample; one process; instrument filed, never scratch | AMENDMENT 4, same requirements | **Identical in substance. Ours KEPT** — it additionally names `--guard-blob`, names the instrument by path, and rules that a refusal on window drift forbids claiming a delta. More specific to this guard, not weaker. |
| §2 no "no behaviour change" exemption; the sweep runs anyway; **the identical row IS the compliance** | AMENDMENT 5's two limbs | **Identical in substance, arrived at independently.** Charter's phrasing **ADOPTED** for the case where the sweep genuinely cannot apply — a typo, a citation, a strike-in-place: the amendment records the rows it did produce and their identity, **which is a measurement, not an assertion.** |
| §3 **the harness ships a planted control, EXECUTED IN THE SAME INVOCATION as the sweep and RECORDED BESIDE ITS ROWS**; a deliberate mutation of the instrument under test must MOVE the rows | **ABSENT.** Our harness had controls, but only under `--selftest` — a *different* invocation, never printed beside a row | **ADOPTED, and implemented.** See §2 below. This is the charter's load-bearing addition and it is right: under §2 identical rows are the *expected* outcome of most amendments, which is exactly when a broken harness is least likely to be noticed. |
| §4 **every recorded rate carries its sample's DEFINITION — the commit range and the count — beside the number** | Partial: the window was named in prose, and an ad-hoc run printed the requested depth but not the resolved range | **ADOPTED, and implemented.** See §2 below. |
| §5 an instrument carrying **no** measured rate incurs one sentence saying so | Absent (not previously needed) | **ADOPTED.** Discharged for the harness in §3 below. |
| §1 **BOUNDARY: no executable check may be made to refuse on the precondition, by any agent at any level** | Absent | **ADOPTED and recorded on our face.** See §6. |

**One correction to the record, because a mischaracterisation of a charter is how drift
starts:** §2 of the charter is sometimes read as a *carve-out* exempting typos and citations
from the sweep. **It is not an exemption.** It says such an amendment records **the rows it
did produce and their identity**. The sweep still runs. Nothing in the charter lets an
amendment ship with no rows.

### 2. The harness is hardened to §3 and §4 — and a REAL DEFECT was found doing it

`scripts/sweep_commit_size_guard.py` now, **on every run**:

- **Applies the charter's planted control in the same invocation**, mutating the guard under
  test with its own `Mutations` machinery and **REFUSING (rc 2) if the mutation does not move
  the rows.** The control's row is **printed beside** the measured row so an amender pastes
  both. `disable_count` is the mutation, chosen over the more topical
  `disable_logs_runs_exemption` because it exists in **every** version of the guard's tuple
  including blobs predating AMENDMENT 3 — a control that breaks on half the inputs it must run
  against is not a control. The mutation is taken **from the guard**, never copied: *a control
  that carries its own copy of the thing it is testing tests the copy.*
- **Prints the sample's resolved definition** — `FROZEN 94ceebe7..db2c7f9a (newest..oldest),
  200 commits` — built from the **resolved** endpoints rather than from what was requested.
- **Emits the "matches the recorded row" line ONLY for the frozen window.** Previously a
  *different* sample that happened to produce the same numbers could claim that match.
- **Validates the frozen anchor on EVERY run, ad-hoc included**, refusing if `94ceebe7` is
  unreachable or `db2c7f9a` is no longer at depth 200.

**THE DEFECT, MEASURED AND DISCLOSED RATHER THAN QUIETLY FIXED.** Before this amendment,
`--depth 199` **swept a different 199-commit sample and printed a confident 2.5 % at rc 0.**
The endpoint check existed but was reachable only when the caller asked for the default window
*and* depth.

**And the worse half:** the harness's own `S3` control passed throughout, because it called
`resolve_window()` **directly with the expectation set** — proving a refusal **on a code path
the command line never took.** *A control that exercises a path the entry point does not use
tests the control, not the instrument.* `S3` is retained with that limitation stated in its own
output, and a new **`S6`** plants a wrong endpoint into the constant and shows **the function
`main()` actually calls** refusing. Controls: **7 → 10**, rc 0; rc 2 under `python3 -O`.

**What is a refusal and what is a disclosure, stated so it is not over-read:** the harness
**refuses** when the frozen anchor is *broken* — that is drift, and the charter's §4 adopts
refusal as sufficient for it. An **explicitly requested** ad-hoc window is not drift; it runs,
carries its resolved range and count, and is stamped *not comparable*. Refusing a window the
caller deliberately asked for would be a different rule from the one adopted.

### 3. This amendment's own rows, under §2 — and the §5 disclosure

**The guard's rate is unchanged, by construction: this amendment changes no guard code.**

| row | sample | commits | accepted | refused | rate | clauses |
|---|---|---|---|---|---|---|
| guard blob at `abe1a634` | FROZEN `94ceebe7..db2c7f9a`, 200 | 200 | 194 | 6 | 3.0 % | LOGS 0, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |
| guard blob at HEAD | FROZEN `94ceebe7..db2c7f9a`, 200 | 200 | 194 | 6 | 3.0 % | LOGS 0, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |

**Which outcomes moved: none. Which did not: all of them.** The guard blob is
`7f2abff6d48506f202557281d1dbe9bcd18a9eae` at `abe1a634`, at `f6bb721d`, at `3caa655d` and at
this amendment — identical throughout.

**Planted control, same invocation, recorded beside the rows as §3 requires:** guard mutated
with `disable_count=True` → **4 refused, 2.0 %**, clauses LOGS 0, COUNT 0, BYTES 3, EMPTY 1,
ATTEMPT 0. **The rows MOVED (6 → 4), so the identity above is a measurement and not a stuck
reading.**

**Because this amendment changes the HARNESS, the same measurement was taken across the
harness change**, over the same frozen sample and the same guard blob: **all 200 rows identical
in every recorded field, and the summaries identical.** The hardening changed what the harness
*reports about itself*, not what it measures.

**§5 disclosure, discharged:** `scripts/sweep_commit_size_guard.py` **carries no measured
false-positive rate of its own, and none was re-measured.**

### 4. AN AMBIGUITY IN AMENDMENT 5, NAMED AND LEFT OPEN

AMENDMENT 5 binds "every amendment to this guard". **It does not say whether an amendment that
changes only the HARNESS — the instrument — carries the obligation, or only one that changes
the guard.** A harness change cannot move the guard's rate by construction, yet the harness is
what *produces* the rate, so a defect in it is at least as dangerous as one in the guard.

**This is OPEN and UNRULED. The implementer did not resolve it**, because resolving it is a
change to a clause in a rule-6 file and that is the Owner's call. **It was complied with in the
stricter direction** — the harness before/after rows are recorded in §3 — so no reading of the
clause is unsatisfied while it stands open.

### 5. THE RESIDUAL, BOARDED AS **OPEN AND UNENFORCED**, IN THOSE WORDS

**The precondition is honoured by a person reading it. Nothing mechanically prevents a future
amendment landing with no rows in its section.** That is stated plainly rather than papered
over.

### 6. WHAT WE DELIBERATELY DID NOT BUILD, AND WHY IT WAS NEVER OURS TO BUILD

A bespoke checker over this file, asserting that every `## AMENDMENT` section carries a
recorded row pair, was proposed as the way to close §5. **It is not built.** The Owner's three
grounds: verification has already chosen the enforcement mechanism — the same-invocation
planted control recorded beside the rows, which makes a missing row pair visible in the
document itself — and a second, differently-shaped local mechanism would drift from the
charter; an enforcement instrument for a lab-wide charter clause belongs to the team that owns
the clause, and building one unilaterally would be this team legislating for the lab; and it is
turtles — an unenforced checker enforcing an unenforced clause, which only *appears* to close
the gap.

**And the charter forecloses it outright, which settles it above the Owner's level.**
`VERIFICATION_CHARTER` v1.13 §1: *"This is a documentation obligation on amenders. **No
executable check may be made to refuse on it, by any agent, at any level.**"* Verification's
D539 reasoning is that a checker which refuses is a gate on lab process, and **adding** a gate
is reserved to Sanaa exactly as retiring one is. The charter goes further and names the failure
mode by name: *"Anyone who reads this adoption as authority to write that check has laundered a
permission (rule 9)."*

**So the residual stays open by ruling, not by neglect**, and this team's offer stands: we will
implement such a check **to verification's specification** if verification asks for one. We
will not write it on our own authority, and no reading of the charter's adoption of our own
proposal makes it ours to write.

---

## AMENDMENT 7 — 2026-08-27, cfd-supervisor as named Owner. THE OPEN QUESTION OF AMENDMENT 6 §4 IS RULED: A HARNESS-ONLY CHANGE CARRIES THE OBLIGATION. v1.6 → v1.7

**lines whose number changed above this section: 0** (746 lines before this heading: the 74
original lines byte-identical to HEAD, plus AMENDMENTS 1–6 untouched — verified by comparing
the md5 of the first 746 lines of the pre-amendment blob against the md5 of the first 746
lines of this file, and by asserting the new file's bytes begin with the whole old blob. Not
verified by writing the words.)

**D539 unchanged: the guard is ADVISORY**, and AMENDMENT 6 §6 records why no clause here may
be made to refuse on anything.

### 1. First, the finding that prompted this, named rather than left as a table row

AMENDMENT 6 added control `S6` and kept `S3`. The reason belongs beside them:

> **`S3` tested a code path `main()` never took.** It called `resolve_window()` **directly,
> with the expectation argument set**, and passed — for as long as the command line was
> reaching that function **without** the expectation set, so that `--depth 199` swept a
> different 199-commit sample and reported a confident 2.5 % at `rc 0`.

**A control that exercises a path the program never executes is not a control. It is a
decoration that reports PASS forever.** It is the same family as a planted zero read by a
reader never shown able to see a non-zero (`CLAUDE.md` standing rule 3), and the same family
as a structural splice check that passes while the wrong text goes in: in every case the
instrument reports on something adjacent to the thing that matters, and the report is
indistinguishable from a real one.

**It was found in this team's own instrument, unprompted, and reported rather than quietly
repaired.** `S3` is retained — with its limitation printed in its own output, so the record of
the defect travels with the control — and `S6` plants a wrong endpoint into the constant and
exercises **the function `main()` actually calls.** The general lesson has been carried up.

### 2. THE RULING: a harness-only change carries the AMENDMENT 5 obligation

AMENDMENT 6 §4 left open whether an amendment changing only the **harness** — the instrument —
must record rows, or only one changing the **guard**. **It must. The rows are mandatory.**

**What varies is not whether the rows are recorded, but what they MEAN — and the inversion is
the whole reason to require them:**

- For a **guard** change, the rows detect an unintended change in **what the guard does**.
- For a **harness** change, the guard has not moved at all. The rows can therefore only detect
  a change in **what the instrument measures** — so **any movement is, by construction, a
  measurement artefact.** That is precisely the failure most worth catching: a harness that
  quietly starts measuring something else **keeps producing confident, comparable-looking
  rates that mean something different from the ones beside them in the same table.**

> **A harness-only change records the before/after rows, and THEY MUST BE IDENTICAL —
> commit-for-commit, clause-for-clause, over the same frozen sample and the same guard blob.**

AMENDMENT 6 already did this, unprompted: its rows were 194 / 6 / 3.0 % on both sides with all
200 rows identical in every recorded field. **This ruling makes what was done the rule rather
than the habit** — the same move AMENDMENT 4 made, and the same one AMENDMENT 5 made in
refusing the self-classification qualifier.

### 3. THE ONE EXCEPTION, written explicitly so it cannot be abused

Where the harness change **is itself a correction to the measurement** — the window-resolution
refusal added in AMENDMENT 6 is exactly this class, and a genuine fix to a mis-specified window
or sample would be another — **the rows may legitimately move.** In that case, and only in that
case:

1. **Both rows are recorded.**
2. **The movement is attributed to the specific correction** — which line of the diff caused it,
   not "the fix".
3. **The OLD row is marked in the table as having been WRONG**, not merely superseded. **A
   superseded row invites a reader to average it in with the others; a row marked wrong does
   not.**

**What is never acceptable is a harness change that moves the rows and explains the movement as
"expected".** "Expected" is a statement about the amender's intent; "this correction changed
what was being counted, and here is the line that did it" is a statement about the code.

**The distinction is decidable FROM THE DIFF, not from the amender's intent.** *"Did this change
what the instrument measures?"* is answerable by looking at the change. *"Did I mean to?"* is
not, and a rule that turns on the second is the self-classification exemption AMENDMENT 5
already refused, re-entering through the instrument instead of the guard.

**Applied retrospectively to AMENDMENT 6, honestly:** that harness change **was** of the
correcting class, and the exception was nonetheless **not needed** — its rows did not move,
because the defect it fixed affected only **non-default invocations**, and every recorded row in
this document is taken over the default frozen window. No row in this document is marked wrong.
The 2.5 % that the broken `--depth 199` path once printed **was never a recorded row here**, and
is named in AMENDMENT 6 §2 as a defect rather than as a measurement.

### 4. This amendment's own rows, under §2

**AMENDMENT 7 changes neither guard code nor harness code**, so under §2 its rows must be
identical — and they were **run and recorded, not asserted as exempt.**

| row | sample | commits | accepted | refused | rate | clauses |
|---|---|---|---|---|---|---|
| guard blob at `abe1a634` | FROZEN `94ceebe7..db2c7f9a`, 200 | 200 | 194 | 6 | 3.0 % | LOGS 0, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |
| guard blob at HEAD | FROZEN `94ceebe7..db2c7f9a`, 200 | 200 | 194 | 6 | 3.0 % | LOGS 0, COUNT 5, BYTES 3, EMPTY 1, ATTEMPT 0 |

**Which outcomes moved: none. Which did not: all of them.**

**Planted control, same invocation, recorded beside the rows** (`VERIFICATION_CHARTER` v1.13
§3): guard mutated with `disable_count=True` → **4 refused, 2.0 %**, clauses LOGS 0, COUNT 0,
BYTES 3, EMPTY 1, ATTEMPT 0, on **both** rows. **The rows MOVED (6 → 4), so the identity above
is a measurement and not a stuck reading.**

Blob identity across the whole amendment chain, so the "no code changed" claim is checkable
rather than trusted:

- **guard** `7f2abff6d485` at `abe1a634`, `f6bb721d`, `3caa655d`, `959fdb47` **and HEAD** —
  unchanged since AMENDMENT 3.
- **harness** `b5fea2b9ded6` at `05f7e726` through `3caa655d`, then `bf5bebf81d9a` at
  `959fdb47` **and HEAD** — the single change is AMENDMENT 6's hardening, whose identical rows
  are recorded in AMENDMENT 6 §3.

**§5 disclosure (`VERIFICATION_CHARTER` v1.13):** `scripts/sweep_commit_size_guard.py` carries
no measured false-positive rate of its own, and none was re-measured.
