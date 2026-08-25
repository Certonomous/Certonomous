# The worktree-staleness defect class — mechanism established by measurement, one cfd file repaired, and a clause PROPOSED

**Team:** cfd (lane, for cfd-supervisor). **Date:** 2026-08-25.
**Compute:** ZERO. This is a records-and-instrument item; no solver was launched,
no core-minute was spent, and **no `docs/COST_CALIBRATION.md` row is owed** — an
empty calibration row would be noise, not a calibration.

**Status of §5 below: PROPOSAL — NOT ADOPTED. Nothing in this document is in
force.** It changes no charter, no `CLAUDE.md` rule and no `.claude/`
configuration, and the author of this document changed none of them. Adoption is
Sanaa's alone.

---

## 1. What was asked, and what the answer turned out to be

The dispatch hypothesis was that **the private-index protocol permits committing
content that was never written to the working tree** — a blob built in a scratch
file and inserted with `git hash-object -w` + `git update-index --cacheinfo`,
never passing through the worktree — and that rule 10's mandated post-commit
verify (`git diff HEAD~1 HEAD --stat`) grades **the commit** and is **silent about
the disk**.

**That hypothesis is CONFIRMED as to mechanism, and it is ONE mechanism, not
several.** It is also **not new**: the lab established it two days earlier and
landed it as `docs/LESSONS.md` **L-253** (2026-08-23, verification) —

> "a private-index protocol that never writes the worktree makes the worktree
> stale BY DESIGN — and it selectively destroys the work of exactly the teams
> that follow it"

— with **L-307** adding that the gap is **non-stationary** (its size *and
direction* move within minutes, so every figure about it is void without a sha and
a UTC stamp). The honest finding is therefore not the mechanism. It is this:

> **L-253 was diagnosed on 2026-08-23 and is still producing fresh instances on
> 2026-08-25. Five of the six files still BEHIND at the time of writing were put
> there by commits made AFTER L-253 landed.** The interim discipline L-253
> prescribes is unenforced prose; nothing mechanised it. That is the gap this
> item closes, and it closes it with an instrument, not with a rule.

## 2. The measurement that establishes the mechanism

Three independent lines of evidence, all taken from the repository's own history.

**(a) Every BEHIND disk copy is byte-identical to an ancestor commit's blob, and
its mtime falls a few seconds BEFORE that ancestor's commit.** The worktree write
for that commit happened normally; it is the *next* commit's write that never
happened.

| file | disk mtime (UTC) | disk == blob at | commit time (UTC) |
|---|---|---|---|
| `docs/FAIL_OPEN_GATE_AUDIT.md` | 08-23 19:59:19 | `f14fca9c` | 08-23 19:59:38 |
| `docs/ansys_verification/ARCHIVE_HOME_RULING.md` | 08-24 17:19:24 | `e9737c5f` | 08-24 17:21:01 |
| `docs/ansys_verification/CASE_MAP_AUDIT.md` | 08-25 01:05:11 | `eb0feb8b` | 08-25 01:05:11 |
| `docs/ansys_verification/RECORDS_DRAFTS.md` | 08-25 00:06:27 | `a89da095` | 08-25 00:07:48 |
| `docs/ansys_verification/RUN_STATUS_EVIDENCE.md` | 08-25 01:09:55 | `1149daa5` | 08-25 01:10:26 |
| `docs/charters/ANSYS_VERIFICATION_CHARTER.md` | 08-25 00:46:25 | `e05bd728` | 08-25 00:46:26 |
| `verification/campaign/F11_CONVERSION_PREREGISTRATION.md` | 08-25 01:08:05 | `34219bf5` | 08-25 01:09:03 |

**(b) `ctime == mtime` on every one of the seven** (`RECORDS_DRAFTS.md` differs by
13 ms, a normal write-and-close). No inode was replaced, no rename-over occurred,
no `cp -p` or archive extraction touched them. **The files have not been written
since the commit whose content they hold.** This is what rules out the competing
reading: a plain concurrent-overwrite race also produces a strict prefix, but an
overwrite sets a *new* mtime, necessarily *after* the commit it lost. None of the
seven shows that.

**(c) Every unlanded commit is a pure append — 11 of 11.** Walking each file from
its disk-matching ancestor to HEAD, every intervening commit adds bytes to the end
and changes nothing above:

| file | unlanded commits | each append |
|---|---|---|
| `docs/FAIL_OPEN_GATE_AUDIT.md` | `c4937603`, `02a84b18` | +2 996 B, +6 159 B |
| `docs/ansys_verification/ARCHIVE_HOME_RULING.md` | `17527f40`, `fc68bd19` | +2 376 B, +331 B |
| `docs/ansys_verification/CASE_MAP_AUDIT.md` | `565ea88c` | +4 509 B |
| `docs/ansys_verification/RECORDS_DRAFTS.md` | `991b12b1` | +1 186 B |
| `docs/ansys_verification/RUN_STATUS_EVIDENCE.md` | `96e2bbef` | +3 835 B |
| `docs/charters/ANSYS_VERIFICATION_CHARTER.md` | `649aa42a`, `3abac11f`, `75030b12` | +4 264 B, +4 468 B, +15 776 B |
| `verification/campaign/F11_CONVERSION_PREREGISTRATION.md` | `53298a45` | +5 893 B |

**Eleven appends, eleven frozen mtimes, zero exceptions.** A race would give mixed
signatures. This gives one. The route is the base-from-git append that
`docs/BOARD_BASE_RULE_PROPOSAL.md` §1 already documents verbatim —
`git show $H:<path>` → `git hash-object -w` → `git update-index --cacheinfo` —
"a path that writes the commit and **never the worktree file**".

**Corroborating instrument already on disk:** `scripts/check_docket_reconciliation.py`
names this exact defect for docket rows — *"A row landed by private index and never
written back… HEAD WINS: restore it into the worktree… Do NOT commit it again"*
(`:24-28`, `:337-343`). The defect class was known for one file shape. **What this
item establishes is that it is not confined to the shared board file: it reaches a
CHARTER and a PRE-REGISTRATION.**

## 3. Why this is charter-level and not housekeeping

Rule 6 makes an appended, dated amendment **the only lawful way a frozen document
changes**. If amendments reliably fail to reach the disk, **rule 6's mechanism is
silently broken for every reader who does not use `git show`.** Two measured
instances make that concrete:

- `docs/charters/ANSYS_VERIFICATION_CHARTER.md` on disk **stopped at v1.2**,
  missing four appended amendments — 373 lines, 24 508 bytes, including the v1.4
  "TWO STANDING SETUP OBLIGATIONS". A lane reading its own charter off disk read a
  charter that does not exist at HEAD.
- `verification/campaign/F11_CONVERSION_PREREGISTRATION.md` on disk was missing
  **AMENDMENT 2 entirely — the amendment that WITHDRAWS a "Sanaa's directive,
  verbatim" attribution.** A lane grading against that worktree copy would have
  graded against withdrawn text, with nothing on disk to warn it.

## 4. What was repaired, what was not, and who owns the rest

**Repaired — cfd's file, and cfd's only.**
`verification/campaign/F11_CONVERSION_PREREGISTRATION.md`.

The repair is lawful under rule 10 ("inspected, never reverted") because it is a
**restore, not a revert**, and the distinction is *proved per file* rather than
asserted: **a strict prefix carries no information that is not already in HEAD.**
The proof, taken and re-taken in the same shell invocation as the write:

- disk blob `00d62c82ec2521534e2dd5348e33452241fd700e`, **60 016 bytes**
- HEAD blob `fd34c3b0b1c4e5050dbddcd4040d8e2b459bde8d`, **65 909 bytes**
- `cmp -n 60016` of the HEAD blob against the whole disk file: **identical** —
  the disk file *is* the first 60 016 bytes of the HEAD blob, and is strictly
  shorter. HEAD adds **5 893 bytes with no counterpart on disk**, so the write
  destroyed nothing.
- after the write, `git hash-object` of the worktree file == the HEAD blob sha.

No forbidden command was used: no `git checkout --`, no `reset --hard`, no
`stash`, no `clean`. The restore is `git cat-file blob <sha> > <path>` — a write.
**It is deliberately NOT re-committed**, per `check_docket_reconciliation.py`'s own
guidance; the content is already in HEAD and re-committing identical bytes is
noise.

**NOT repaired — reported only, and untouched. These are not cfd's to fix.**

| file | class | owning team |
|---|---|---|
| `docs/charters/ANSYS_VERIFICATION_CHARTER.md` | BEHIND, −24 508 B | **ansys-verification** |
| `docs/ansys_verification/CASE_MAP_AUDIT.md` | BEHIND, −4 509 B | **ansys-verification** |
| `docs/ansys_verification/RUN_STATUS_EVIDENCE.md` | BEHIND, −3 835 B | **ansys-verification** |
| `docs/ansys_verification/ARCHIVE_HOME_RULING.md` | BEHIND, −2 707 B | **ansys-verification** |
| `docs/ansys_verification/RECORDS_DRAFTS.md` | BEHIND, −1 186 B | **ansys-verification** |
| `docs/FAIL_OPEN_GATE_AUDIT.md` | BEHIND, −9 155 B | **verification** (`docs/*_AUDIT.md`) |
| `docs/ansys_verification/CASE_MAP.md` | **DIVERGENT** | **ansys-verification** |
| `docs/campaigns/F14-cooling-ladder/K0d_LANE_REPORT_FIRE.md` | **AHEAD** | **heat-transfer** |
| `docs/campaigns/T-family/T10aR_PREREGISTRATION.md` | **AHEAD** | **heat-transfer** |

**The two AHEAD and the one DIVERGENT must not be touched by anyone doing this
repair.** They carry bytes that exist in no commit — live uncommitted work — and
the strict-prefix proof does not apply to them. `CASE_MAP_AUDIT.md` matches both
`docs/ansys_verification/` (ansys-verification) and the `docs/*_AUDIT.md` pattern
(verification); the more specific folder governs, but the ambiguity is flagged
rather than resolved here.

Routing these repairs is the chief's call, not a lane's and not a supervisor's.

## 5. PROPOSED clause — NOT ADOPTED, and deliberately NOT filed as a new proposal

**This does not belong in a new proposal document, and here is why.** `D480` is
**already on Sanaa's desk**: *"ADOPTION DECISION FOR SANAA: THE CLAUDE.md RULE-10
AMENDMENT (BASE-FROM-GIT BOARD COMMITS)… THE INSTRUMENTS EXIST AND ARE VERIFIED…
AND THEY GATE NOTHING UNTIL SHE RULES."* Filing a second proposal for the same
defect class would be duplicate dispatch. **This section is EVIDENCE FOR D480, not
a rival to it**, and its one substantive addition is scope: D480 was argued from
`docs/LAB_STATE.md`, a shared multi-team board file. §3 above shows the same
mechanism reaching **a charter and a frozen pre-registration** — single-owner
documents, where the "concurrent writers" framing does not apply at all.

Proposed text, for `docs/charters/ESCALATION_CHARTER.md` §9.6 (the git rules),
offered as wording only:

> **§9.6d (proposed).** The post-commit verify is not complete at the commit. After
> `git diff HEAD~1 HEAD --stat` confirms the commit, **assert that the WORKTREE
> file matches the committed blob** — `git hash-object -- <path>` against
> `git rev-parse HEAD:<path>` — for every path in the commit. The existing verify
> grades the commit and is silent about the disk, and a commit built from a
> base read out of git never writes the worktree at all. Where the worktree copy
> is left behind deliberately, say so in the commit message and name the path, so
> the next reader is not the one who discovers it.

**Three constraints on this section, stated so they cannot be read past.**
`ESCALATION_CHARTER.md` is the **verification** team's territory, not cfd's.
Adding, widening or retiring a charter clause is **reserved to Sanaa**. And no
supervisor's instruction is her consent — a lane that edited another team's
charter on a supervisor's say-so would be laundering permission, whatever the
merits of the clause. **Nothing was edited. This is a draft, and it stops here.**

## 6. The instrument

`scripts/check_worktree_matches_head.py` — sweeps tracked `.md` under
`verification/` and `docs/` and classifies each as
`MATCH` / `BEHIND` / `AHEAD` / `DIVERGENT` / `ABSENT` / `UNREADABLE`.

- **It refuses rather than degrades.** A file it cannot read is reported
  `UNREADABLE` and forces exit 2; it is never reported `MATCH`.
- **It gates nothing.** Default exit is 0. `--strict` is opt-in. Per D480, wiring
  an instrument of this class into `check_harness` or any gate is **not
  authorized ahead of Sanaa's ruling**, and this script is written to respect that.
- **Controls.** `--selftest` plants 9 value controls (MATCH, two BEHIND including a
  zero-byte disk copy, AHEAD, three DIVERGENT shapes, ABSENT, UNREADABLE) in a
  throwaway git repo and asserts each classification, plus the exit-2 refusal.
  It then applies **4 source mutations** and asserts the controls **FLIP** —
  BEHIND mislabelled AHEAD; each prefix test removed so a DIVERGENT reads as
  BEHIND / AHEAD; and a fail-open that reports an unreadable file as MATCH.
  **A control that cannot fail is not a control.** `__pycache__` is deleted
  before every control run, because stale bytecode inverts mutation tests and
  `PYTHONDONTWRITEBYTECODE` does not fix it.
- **It declares its blind spots and prints them beside every verdict** (L-307:
  a passing plant proves an instrument sees what it measures and proves nothing
  about what it does not). It cannot see *why* a file is BEHIND, whether a repair
  is wanted or whose file it is, anything untracked or non-`.md`, or whether HEAD
  itself is correct.

**One correction to the dispatch, and it is load-bearing.** The dispatch specified
`git ls-files` for the tracked walk. **`git ls-files` consults the shared index,
which L-294/L-307 rule out as an instrument in this repository, and the cost is
measured, not theoretical:** at HEAD `57de4025`, `git ls-tree -r HEAD --
verification docs` listed **565** tracked `.md` while `git ls-files` listed
**464** — **the index hid 101 tracked files, 18 % of the population.** An
instrument for worktree staleness built on the index would have been blind to
exactly the files it hunts. The script walks `git ls-tree -r HEAD` and strips
`GIT_INDEX_FILE` from its own environment. This lane's own first measurement was
wrong for precisely this reason and had to be retaken.

**Live reading, 2026-08-25T21:17:03Z, HEAD `b530da3686f0ad989b16d07f0062d2e524655fd9`**
(void without that sha and stamp — L-307): population **565**; `MATCH` 556,
`BEHIND` 6, `AHEAD` 2, `DIVERGENT` 1. cfd's file is absent from `BEHIND` because
it was repaired; the six remaining are listed in §4 and belong to other teams.

## 7. Verdict

**No gate verdict is owed and none is claimed.** This item pre-registered no gate
and graded no physical quantity; the fixed vocabulary
(`PASS`/`GATE REACHED`/`GATE FAIL`/`NOT A RESULT`/`BLOCKED`/`PENDING`) grades
gates, and using any of those words here would be a category error.

**What this lane could not verify, stated plainly:**

1. **The route is inferred, not observed.** Three converging lines of evidence
   (frozen mtimes, `ctime == mtime`, 11/11 append-only) make the base-from-git
   blob route the only reading consistent with all of them, and
   `BOARD_BASE_RULE_PROPOSAL.md` §1 documents that route in use. But **no command
   transcript of the eleven commits survives on this box.** Nobody was watched
   doing it. If a transcript exists elsewhere it would upgrade this from a strong
   inference to an observation.
2. **Whether the other six will be repaired.** They are reported, not touched, and
   routing is the chief's.
3. **Whether the sweep is complete beyond its declared population.** Untracked
   drafts, non-`.md` records and paths outside `verification/`/`docs/` were not
   examined, and `cases/` (225 tracked `.md`) was not swept at all.
4. **This instrument's own diff has not yet been read by the supervisor.** It
   produces a graded classification, so under the supervision charter's check 1 it
   is a measurement script whose diff must be read as a diff before any conclusion
   rests on it. **This lane's selftest passing is evidence, not that read.**
