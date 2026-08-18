# Ladder V — V15 round 9: the grade over the 2026-08-15/16 text

**Grader:** a fleet agent that wrote none of the text under audit and none of the repairs
under test. **Executed 2026-08-16 17:12Z → 18:4xZ.** No solver was launched, no scoring
call was made; the scoring ledger stands at 6. The scoring pin `deb91557` was not moved.
Nothing was sent, uploaded, filed or registered externally; the submission is PARKED and
reserved to Katie.

**The verdict the termination rule asks for is a number, and it is not zero.**

---

## 0. Independence, and exactly how far it reaches

**Git cannot establish it.** `git log --format='%an <%ae>'` returns one identity,
`Ubuntu <ubuntu@ip-172-31-43-247.us-east-2.compute.internal>`, across the whole graded
range. That is **D130**, and this round is another instance of it rather than an
exception to it.

**What does, and it is a timestamp.** This lab's per-agent dispatch records live at
`~/.claude/projects/-home-ubuntu-Certonomous/64b13819-…/subagents/`. Mine is
`agent-a49ee566ebf57398c`, whose `meta.json` reads
`{"agentType":"general-purpose","description":"Run V15 round 9",…}` and whose file was
created at **2026-08-16 17:12:40.968Z**. The **first record in my transcript is
`2026-08-16T17:12:40.961Z`** — the dispatch prompt itself — and the file holds no earlier
event.

The **last commit in my declared scope, `fe54ec0a`, is timestamped
2026-08-16 17:10:19 +0000 — two minutes and twenty-one seconds before my first recorded
action.** Every one of the 81 commits graded below predates my existence.

**What changed since round 8, and it matters to §0.** Round 8's **P15** recorded that the
attribution instrument's discriminating field had taken exactly one value across one
hundred percent of its deployed life, so a green `check_rung_attribution` run was not
independence evidence. **That has been repaired inside this round's scope and the repair
is verified here by execution, not read:**

```
$ git log --format='%H%n%b' --all | /usr/bin/grep -oE 'Lab-Agent: .*' | sort | uniq -c
   → 19 DISTINCT values (18 real + the docstring's own template line)
      8  …/64b13819-…/-/agent-a44104098e58e2737
      4  …/64b13819-…/-/agent-a7906acd0a1e114c3
      3  …/64b13819-…/v12-nonauthor-grader/agent-aaf894dca7319cd1e
      …  (and 15 more, including six distinct tagged handles on one agent)

$ python3 scripts/check_rung_attribution.py --emit-trailer --probe v15r9-4f2a9c > out 2> err ; rc=$?
rc=0   stdout 91 bytes   stderr 0 bytes
Lab-Agent: ip-172-31-43-247/64b13819-…-3720bab19084/-/agent-a49ee566ebf57398c
```

The field now varies, and it emits a per-agent handle rather than a per-session one. The
`rc` was taken from the process and not inferred from the file, because an unresolvable
probe writes zero bytes to stdout and a message to stderr and the resulting commit carries
no identity while looking healthy.

**The limits, stated rather than left to be found.**

1. The subagent directory is **untracked and per-machine**. No reader of this repository
   can re-derive paragraph two. D130 again.
2. The claim this evidence supports is bounded: **no evidence of the same authorship**,
   not proof of different agents.
3. **Twenty-six commits landed after my first recorded action and are excluded by that
   rule** — `567c7aa6` (17:13:02Z) onward, through at least `4186fdfb` (17:50:35Z). My
   non-authorship of those is *not* established by the timestamp argument, which is
   precisely why they are named here rather than quietly absorbed. The tree moved 23
   commits in the 32 minutes while this round executed.
4. **Three execution cells of this round were run by subagents dispatched by me.** Their
   findings are mine and are reported as mine. They are not independent of me; they are
   independent of the text.

---

## 1. R-CONVERGE — the scope, declared mechanically BEFORE any finding

Round 8 (`e0a4117a`) fixed its verdict at HEAD `cca64eaf` and named `840c0c27` and
`7370b3d3` as the two commits that landed after and were **not** graded. This round's
corpus is everything from there.

| item | value |
|---|---|
| base | `cca64eaf` (2026-08-15 19:53:29Z) — round 8's verdict HEAD |
| HEAD at declaration | `fe54ec0a` (2026-08-16 17:10:19Z) |
| commits | `git rev-list --count cca64eaf..fe54ec0a` → **81** |
| churn | `git diff --shortstat cca64eaf..fe54ec0a` → **88 files changed, 22,006 insertions(+), 477 deletions(-)** |
| composition | **27 added, 61 modified, 0 deleted** |
| days | **48 on 2026-08-15, 33 on 2026-08-16** |
| excluded, named | `567c7aa6` … `4186fdfb` — 26 commits landed at or after 17:13:02Z, after this grader's first recorded action |

`840c0c27` and `7370b3d3`, which round 8 excluded, **are** inside this range and are
graded here.

### 1.1 What this frame structurally cannot contain

- **Rendered text.** Everything below is bytes. A page can carry a claim its bytes do not.
- **Non-text PDF layers**, and anything in a figure or a font-embedded glyph run.
- **The live leaderboard.** Every board-relative number below is graded against the
  six-entry board fetched 2026-08-11T23:33Z, read by `ast` from `LIVE_BOARD` in
  `sdk/scripts/probability_of_rank.py` and joined to
  `demo-output/website/closure_challenge_round5_qcr.json`. **Nothing was fetched.**
- **The uncommitted working tree.** At declaration it carried another agent's in-flight
  `scripts/self_audit.py`, `docs/DOCKET.md`, `docs/AGENT_ATTRIBUTION.md`,
  `docs/USING_THIS_LAB.md` and `sdk/tests/test_rank_claim_*.py`. None is graded. Every
  measurement below was taken against `git archive fe54ec0a` extracted to scratch, or
  against `git show <rev>:<path>`, never against the worktree.
- **Struck text**, wherever an instrument is quoted, and multi-line `~~…~~` spans, which
  my blanker does not close (§1.2).

### 1.2 Method, arm by arm — and the control discipline, which caught my own instrument twice

Counts over tracked text use `git grep -a`, `git ls-tree` or a `git archive` extraction,
never the shell's `grep` (which execs `ugrep --ignore-files`, honours `.gitignore` and
passes `-I`). `find` here is `bfs`; `/usr/bin/find` was used throughout. Every sweep
pattern is written with `\s+` and **never a literal space**, because a soft-wrapped
heading defeats a literal-space pattern and did so in this lab tonight. Exit codes were
taken as `cmd > out 2>&1; rc=$?`, never through a pipe.

**The four arms, enumerated rather than assumed:**

| arm | enumerator | count |
|---|---|---|
| tracked, at `fe54ec0a` | `git archive fe54ec0a` → `/usr/bin/find -type f` | **20,704** |
| untracked | `git ls-files --others --exclude-standard` | **1** (`.autostop-hold`) |
| gitignored | `git ls-files --others --ignored --exclude-standard` | **37,245** |
| run tree | `/usr/bin/find /home/ubuntu/certonomous-runs/ -type f` | **132,049** |

**CONTROL 1 — the in-scope sweep, and it failed the first time.** A planted positive
control (`ZZPLANTZZ best score on the entire leaderboard on four of eight cases
ZZPLANTZZ`) was appended to scratch copies of four in-scope files and a struck copy to
two more, then **read back off disk before the run** (2 anchors each, last line printed).
The first run returned **5** hits: four positives and **one of the two struck negatives**.
The negative that leaked was `LADDER_V_STATE_2026-08-16.md`, which carries **3 `<s>`
openers against 1 closer**; my depth-walk blanker had paired my plant's `</s>` with an
earlier dangling opener and left the plant body live. **The instrument was wrong and the
control is the only reason I know.** Replaced with non-greedy `<s>(.*?)</s>` pairing —
under which a dangling opener blanks nothing, the conservative direction — the control
re-run returned **4 positives, 0 negatives**.

Strike balance across the 88 in-scope files: **99 `<s>` openers against 69 closers**, with
dangling openers in `LADDER_V_D227_ENTITLEMENT` (7:1), `docs/DOCKET.md` (11:4),
`LADDER_V_V15_ROUND8` (12:10), `LADDER_V_TRIPLE_VERIFICATION` (2:0),
`RULE_O_DENOMINATOR_MEASUREMENT` (2:0), `check_derived_figures.py` (3:0) and four others.
Most are prose *about* the markup rather than markup; none of them is safe for a
depth-walk blanker.

**CONTROL 2 — the four-arm sweep.** Four real files were copied out of **each** arm to
scratch, three given a live plant and one a struck plant, and every plant read back off
disk (2 anchors each) before the run. The control returned **30 hits — three needles on
each of ten positive files — and zero on all four struck negatives.** Positive controls
therefore fire on this corpus's real encodings in all four arms, including `.gz` members
and OpenFOAM field files.

**CONTROL 3 — the prefilter.** Arm 3 and arm 4 could not be regex-swept whole in
reasonable time, so a byte-level prefilter was added: a file is skipped only if it
contains none of `rank`, `leaderboard`, `eight`, `leads` (case-folded). No needle's `\s+`
falls inside a word, so the prefilter is **sound by construction**, and it was proved
empirically: with it in place the control still returned **30**, and arm 1 still returned
**194**, byte-identical to the unfiltered run. Arm 1: 19,097 prefiltered, 1,607
candidates. Arm 3: 35,608 prefiltered, 1,631 candidates, **6 files unreadable and named**
(four directories mis-listed by `find`, two `__pycache__` entries deleted under the sweep).

**CONTROL 4 — the shipping-zip sweep, and it failed the first time too.** The first
attempt planted a positive into `certonomous-demo/site/index.html`, **a member that does
not exist**; the readback printed `!! NO POSITIVE PLANT LANDED — control is dead` and the
run was discarded. This is exactly the failure the chief named: an absent anchor, a sweep
that would have returned its real hits with no evidence its instrument worked. Re-planted
into three members that do exist, the control returned **9 hits on 3 files** and **0 on
the struck negative**.

**Every zero reported below stands on a control that was confirmed live by readback.
Nothing here rests on a zero without one.**

---

## 2. F1 — the absolute this lab disproved on 2026-08-15 was re-asserted, with more force, on 2026-08-16, and the register grew by six

**Defect class B3, and it is round 8's F7 (D162) recurring inside the range that filed it.**

Round 8's F7 and **D162** recorded that `sdk/chief_engineer/exec_bits.py`'s justification —

> only an index commit with no pathspec preserves 100755. **So this register is the only
> repair a protocol-conforming agent can perform**, and D134 records that.

— is false, disproved by execution, by **D147** (`f732ebaf`, 2026-08-15T19:44:12Z, whose
own title reads *"`git -c core.fileMode=true` is a fourth repair for D134 … and it works
on the commit, not on the `git add`"*), and by `7370b3d3` acting against it.

**At `e4c1319e` (2026-08-16T17:08:01Z — 21 h 24 m after D147, 20 h 54 m after D162) the
same absolute was written into the file a second time**, in a new comment block covering
four newly registered scripts, and stated in a stronger form:

> under this repository's `core.filemode = false` a PARTIAL commit — the only form this
> lab's commit protocol permits — **re-records 100644 whatever the index holds**, so the
> register is **the only repair a protocol-conforming agent can perform**.

Measured across trees:

| tree | occurrences of *"only repair"* in `exec_bits.py` | `len(WAIVED_NO_EXEC_BIT)` |
|---|---|---|
| `26fca317` (round 7's HEAD) | 0 | — |
| `cca64eaf` (round 8's HEAD) | **1** | **245** |
| `fe54ec0a` (this round's HEAD) | **2** | **249** |
| HEAD `4186fdfb` | **2** | **251** |

**Re-executed independently here, in five throwaway repositories, `core.filemode false`
in every one.** I did not take round 8's measurement on trust:

| arm | index mode | commit | HEAD mode |
|---|---|---|---|
| **A** | `100755` (add with `-c core.fileMode=true`) | `git -c core.fileMode=true commit -F … -- s.py` | **100755** |
| **B** *(negative control)* | `100644` (plain add) | plain pathspec commit | 100644 |
| **C** | `100755` (`update-index --chmod=+x`) | plain pathspec commit, no content change | 100644, `rc=1` *(nothing to commit)* |
| **D** | `100755` (`update-index --chmod=+x`) + content change | plain pathspec commit | **100644** |
| **E** *(round 8's exact arm)* | `100644` (plain add) | `git -c core.fileMode=true commit -F … -- s.py` | **100755**, blob `9440c0cc` |
| **F** *(negative control for E)* | `100644` | plain pathspec commit | 100644, blob `9440c0cc` |

Arm E reproduces round 8's F7(a) **including its blob hash**. Arms A and E both record
`100755` from a **pathspec** commit. So the conclusion — *the register is the only repair*
— is false unless `-c core.fileMode=true` is ruled non-protocol-conforming, which is the
open chief question D147 raises.

**But the new sentence does not need that question settled to be wrong.** Arm D shows the
mechanism claim is true only of the *default*: a partial commit under `core.filemode=false`
without the override re-records 100644 — and Arm A shows it records **100755** when the
index holds 100755 and the override is present. *"Re-records 100644 whatever the index
holds"* is a claim about git, and Arm A falsifies it.

**Neither D147 nor D162 is cited anywhere in the new text.** `/usr/bin/grep -c` over
`exec_bits.py` at `fe54ec0a`: `D134` → 2, `D147` → 0, `D162` → 0, `core.fileMode=true` → 0.
Over `e4c1319e`'s commit message: `D147` → 0, `D162` → 0, `fileMode` → 0. The commit's own
**headline** states the absolute: *"…and the register was the only repair this lab's commit
protocol permits."*

**Why this is a finding and not bookkeeping.** D134 recorded that the register can only
grow. Round 8 showed it need not exist for this class. In the twenty-four hours since, the
register grew by **six** and the sentence denying the alternative was **duplicated** — in
a lab that had filed the counter-measurement, twice, before the pen was picked up.

**And it worked, which is the uncomfortable part.** Round 8's **F8** recorded
`sdk/tests/test_exec_bits.py` RED at HEAD. Run in a fresh clone checked out at `fe54ec0a`
— a real `.git`, not an extraction — it is **green, 15 passed, `rc=0`**. The red test was
closed. It was closed by the one remedy the lab had already measured to be unnecessary,
under a comment that says no other exists, twenty-one hours after the measurement that
says one does. **F8 is closed and F7 is worse.**

*(Frame note, stated because it changes a verdict: the same file run against a bare
`git archive` extraction reports **4 failed**, all four raising
`CalledProcessError: 'git ls-tree -r HEAD' returned 128` — the extraction has no `.git`.
Those four are artifacts of my frame and are not findings. This is named rather than
quietly dropped because a grader who reported them would have manufactured four.)*

**Falsifier for F1:** a chief ruling that `git -c core.fileMode=true commit -F <msg> --
<paths>` is not protocol-conforming under `ESCALATION_CHARTER` §9.6. That rescues the
*conclusion*. It does **not** rescue *"re-records 100644 whatever the index holds"*, which
Arm A falsifies with the override applied and the index at 100755.

---

## 3. F2 — the ladder's own ledger was edited ten times after round 8 landed, and still stops at round 7

**Defect class B4/B5 — a durable record asserting a state that its own tree contradicts.**

`LADDER_V_V15_ROUND8.md` landed at **`e0a4117a`, 2026-08-15T20:10:30Z**, inside this
round's declared range, with **thirty** findings and an explicit *"VERDICT: this round is
NOT belief-neutral."*

`LADDER_V_TRIPLE_VERIFICATION.md` was modified **eleven times inside the range, ten of
them strictly after round 8 landed** — `f956e348`, `e65137cd`, `78eb5530`, `9b9951a1`,
`b2668906`, `20966952`, `73588fb7`, `7c44cbe2`, `1a08e75d`, `f3c27a0c`. At `fe54ec0a`, and
still at HEAD `4186fdfb`:

- **`:979`, the V15 ledger row** (1,380-line file at `fe54ec0a`), reads *"three further rounds have run and none returned
  zero"* and enumerates rounds **5, 6, 7**, closing *"→ **round 7 FAIL, 25 findings**"*.
  Occurrences of `ROUND8` in that row: **0**. Four further rounds have run, not three.
- **`:1013`, the row that states the closing condition**, reads *"| a round of V15
  returning no new failures | **OPEN, and further from closing than it was.** Round 7
  returned **25** | `LADDER_V_V15_ROUND7.md`, `edbaa0fe` |"*. The live evidence for the
  ladder's own termination condition is one round and five findings stale.
- The file mentions `LADDER_V_V15_ROUND8` exactly **once** in its 1,380 lines — at `:274`,
  in an unrelated paragraph about a grade's two reads. **The document knows the file
  exists; the ledger row does not.**

*(Line numbers are at `fe54ec0a`, this round's declared HEAD. The file grew while this
round executed; at `ae09cb3c` (2026-08-16T17:58:45Z) the same two rows are at `:1006` and
`:1040`, both still stopping at round 7, and `LADDER_V_V15_ROUND8` still appears exactly
once. The finding is anchored to the frame it was measured at, not to a moving HEAD.)*

For contrast, an in-scope sibling **did** absorb it: `LADDER_V_STATE_2026-08-16.md:102`
and `:267` both carry *"round 8: 30 findings, four new shapes, NOT belief-neutral"* with
line anchors. So this is not a corpus that lacked the fact; it is a row that was edited
around.

**The same sentence is stale on a second surface, and round 8 predicted it.** Round 8's
**P12** recorded `docs/HANDSHAKE.md:284-285` — *"V15's **latest round** returned **25** new
failures (`LADDER_V_V15_ROUND7.md`, `edbaa0fe`)"* — as a present-tense claim its own first
commit had falsified, and declined to repair it because the file belongs to another
family. Executed at HEAD, twenty-one hours later: **still there, byte-identical.** A
finding that names its own owner and is left for that owner is not thereby closed.

**Falsifier for F2:** show that `:979` or `:1013` carries round 8 in any form.
`/usr/bin/grep -c 'ROUND8'` on the extracted row → 0; on `:1013` → 0.

---

## 4. F3 — a ratio band in the V10 repair, stated two minutes before this scope closed

**Minor, and reported as minor.** `fe54ec0a` repaired V10's C1 blocker on
`closure.html:558-570`. Its arithmetic is otherwise exact (§6), but one clause is not:

> The untrained term set a strong floor; it did not close the gap to ~~Reissmann~~
> **Yang**, which measured **0.0164, 0.0089 and 0.0103** — **between twenty and forty
> times** the 0.0004 band that separates us from the entrant we match.

Re-derived from `LIVE_BOARD`: the three gaps to Yang are `0.016370`, `0.008882`,
`0.010339` — the printed 4-dp values are exact. Against the stated `0.0004` band the
ratios are **40.93, 22.21, 25.85**. The upper end is **above forty**, and rounds to 41.

Under the other available reading — each duct's own separation from Wu & Zhang, which is
what *"the 0.0004 band that separates us from the entrant we match"* names — the
separations are `0.00002956`, `0.00008216`, `0.00033862` and the ratios are **553.8,
108.1, 30.5**, which is not "between twenty and forty" by any margin. **Under no reading
is the stated band right**; under the most favourable it is 22.2–40.9.

**Falsifier for F3:** a reading of *"the 0.0004 band"* under which the maximum ratio is at
most forty. The flat-band reading gives 40.93; the per-case reading gives 553.8.

---

## 5. What reproduced, and is therefore NOT a finding

Recorded because a round that reports only failures cannot be audited for selection.

| claim | frame | result |
|---|---|---|
| **the live board itself** | `ast` on `LIVE_BOARD` ⋈ `round5_qcr.json` | seven positions; per-case ranks **2,2,1,1,3,4,4,7**; best-on-board **2 of 8**, **0 of 8** earned; overall `0.056647191704213645` = **rank 1 of 7**; margin **0.0013528** vs published `0.0580`, **0.0013653** vs Yang's mean-of-eight `0.0580125` |
| round 8 §1's whole scope table | `26fca317..cca64eaf` | **exact** — 78 commits, 61 files, 14,875(+)/434(−), 20 A / 41 M / 0 D, all 78 on 2026-08-15, `650c1e04` in range |
| round 8 §3's 48-cell half-ulp table | re-derived, all eight rows | **exact, 8/8** — 138.11 / 26.24 / 215.84 / 58.74 / **0.59** / 1.64 / 6.77 / 335.96, ranks 2,2,1,1,3,4,4,7 |
| round 8 §10's twelve filed rows | `git show fe54ec0a:docs/DOCKET.md` | **all twelve present** (D158–D162, D164–D166, D170–D173) with matching subject lines; `bfe9b812` landed 7 insertions and 1 deletion on the docket, as stated |
| **round 8's F1 (D158) — is it closed?** | `decide()` driven directly, `__pycache__` purged | **CLOSED BY EXECUTION.** `decide(0,"",[],[],887,[])` now returns `('UNKNOWN', ['EMPTY-2: 887 … matched a mandate marker and ZERO reached a verdict … (defect class B1)'])`. Discriminating arms still live: one decided PASS → `PASS`, one decided FAIL → `FAIL` |
| **round 8's P15 (D173) — is it closed?** | all `Lab-Agent` trailers at HEAD | **CLOSED.** 19 distinct values where there was one; the emitter now yields a per-agent handle, `rc=0` |
| `fe54ec0a`'s repair of V10 C1 (`closure.html`) | 48-cell re-derivation | **every figure exact** — Wu & Zhang `0.0455/0.0399/0.0350` against ours `0.0455/0.0400/0.0353`, separations `0.00003/0.00008/0.00034`; Reissmann **2nd, 2nd, 2nd of seven**; the duct leader **Yang at 0.0291/0.0311/0.0250**; our duct placements **3rd, 4th, 4th of seven**; `099b2827` really is 2026-08-07T21:00:07Z and really did write the struck sentence |
| `fe54ec0a`'s repair of V10 C2 (`benchmarks.html` wall) | 4 rows re-derived cell by cell | **every figure exact** — live minima `0.0432 / 0.0998 / 0.0569 / 0.0748`; margins `+16.0% / +1.3% / −19.0% / −3.9%`; placements `2nd, 2nd, 1st, 1st of 7`; both surviving rows really are the organisers' unmodified RANS field (`rans_identity_floor_per_case` = `round5_per_case` on both `alpha_05` cases, to the last digit) |
| `benchmarks.html`'s *"three deletions wide … 2nd, 3rd and 2nd"* | leave-one-out over all eight cases, means recomputed for all seven entrants | **exact** — dropping `alpha_15_…_4048` → 2nd, `alpha_15_…_2024` → 3rd, `alpha_05_…_4048` → 2nd; the other five deletions leave us 1st |
| `benchmarks.html`'s *"four of eight cases won"* against Yang | head-to-head | **true** — we beat Yang on cases 1–4 and lose 5–8 |
| `CLOSURE_THREE_STRANDS_2026-08-15.md` §2.1's control table | `/usr/bin/grep -ic` over the pinned clone | **all twelve counts exact**, and the frame too: 116 lines, mtime 2026-07-26. Four positives fire (1/1/2/7), eight absence terms return 0 |
| `docs/AGENT_ATTRIBUTION.md`'s measurement table | at **its own declared frame**, `e639796e` (which the document states) | **exact** — 1,849 commits / 4 identities, 1,217 / 1, 36 / 1, and 11 `Claude <noreply@anthropic.com>` commits. At `fe54ec0a` the same windows read 1,972 / 4 and 1,340 / 1; **that is drift, not a defect, because the document anchors its frame and says so** |
| **R-VALUE's own count** | whole tracked corpus at `fe54ec0a`, strike-blanked, `\s+` patterns, control 1/1 positive and 0/1 struck negative | **`is/was belief-neutral` → ZERO occurrences in 20,721 files.** `NOT belief-neutral` → **9**, in five documents. **R-VALUE stands at zero, re-derived rather than quoted, and no round of any rung has ever declared itself neutral** |

### 5.1 Round 8's thirty findings, one round later — what the range actually closed

The most useful thing a V15 round can measure about its predecessor is whether the
corpus moved. Measured by execution at `fe54ec0a`, not read off any repair note:

| round 8 | state at `fe54ec0a` | evidence |
|---|---|---|
| **F1** — `decide()` PASS from an empty decision set | **CLOSED** | the identical call now returns `UNKNOWN / EMPTY-2 … (defect class B1)`; PASS and FAIL arms still discriminate |
| **F8** — `test_exec_bits.py` RED at HEAD | **CLOSED** | 15 passed, `rc=0`, in a fresh clone at `fe54ec0a` |
| **M1** — `check_derived_figures.main()` has no test at all | **CLOSED** | `test_derived_figure_check.py:150` now calls `cdf.main()`; its own docstring reads *"Until today nothing in this repo called `check_derived_figures.main`"* |
| **P15** — one identity across the instrument's whole deployed life | **CLOSED** | 19 distinct `Lab-Agent` values; a per-agent handle emitted |
| **F2** — the undecidable `3rd of 7` on `AR_1_Ret_360` | **LIVE** | `closure.html:505` unchanged |
| **F3** — the true disclosure sitting inside `<s>…</s>` | **LIVE** | *"ties Wu & Zhang at published precision"* is still the **only** occurrence of any printing-interval language on the page, and it is still struck |
| **F4** — the page contradicting itself at `:122`/`:431` vs `:505`/`:506` | **LIVE** | all four lines present and unstruck |
| **F5** — *"every second-column cell"* is seven of eight | **LIVE** | `closure.html:495` unchanged |
| **F7** — the register's false absolute | **WORSE** | §2 |
| **P12** — `HANDSHAKE.md`'s *"latest round returned 25"* | **LIVE** | byte-identical at HEAD, 21 hours on |

**Four closed, five live, one worse.** A rung whose previous round is 40% closed after
twenty-one hours has not converged, and that is a measurement rather than an opinion.

---

## 6. What this round could not measure, and why

- **Rendered output.** No HTML was rendered, no PDF rasterised. `\sout{}` is
  strike-and-keep and a PDF text layer carries a withdrawn figure exactly as a stale one
  does; nothing here is a statement about what a reader sees.
- **The full pytest tier** was not run to completion by me; §7's cell reports what it ran.
- **Multi-line `~~…~~` spans** are not blanked by my instrument (only line-local ones).
  This produced one known false positive, `ACTIVE_RESEARCH.md:747`, whose struck block
  opens on one line and closes on another; it is a false positive of mine, not a defect of
  the corpus, and it is named here rather than counted.
- **The worktree** was never graded. It carried five foreign uncommitted files throughout.
- **Six files in arm 3 were unreadable** and are named in §1.2 rather than absorbed into a
  clean total.

---

## 7. The four-arm sweep result, and the shipped archive

### 7.1 Three arms clean, one not

With the controls of §1.2 live in every arm:

| arm | files read | prefiltered | candidates | unreadable | live hits |
|---|---|---|---|---|---|
| tracked at `fe54ec0a` | 20,704 | 19,097 | 1,607 | 0 | 194, **all accounted for** |
| untracked | 1 | 0 | 1 | 0 | **0** |
| gitignored | 37,239 | 35,608 | 1,631 | **6, named** | **9** |
| run tree | **132,049** | 127,335 | 4,714 | **0** | **0** |

The 194 tracked hits were read; none is a live false board claim. The nine gitignored hits
are all in `dist/`.

### 7.2 The shipped archive still carries the two blockers V10 was graded FAIL on

**Out of this rung's declared scope — `dist/` is gitignored and is not among the 88 files
— and therefore FILED, not appended.**

`dist/certonomous-demo.zip`, **built 2026-08-14T21:16:50Z**, 103 members, opened with
`zipfile` and never byte-grepped, carries **unstruck**:

- **`certonomous-demo/site/closure.html:430` and `:431` — two gold `OUR MODEL LEADS`
  badges**, on `Periodic hill, steep, coarse` (`0.0592` / `0.0501`) and
  `Periodic hill, steep, fine` (`0.1195` / `0.1011`). Occurrences of `OUR MODEL LEADS`
  inside a strike span: **0 of 2.** Against the live board those two cases are **2nd of 7
  and 2nd of 7**, both lost to Tian, Buchanan, Hickel & Dwight at `0.0432` and `0.0998`.
- **`certonomous-demo/site/benchmarks.html` — the heading *"Cases where we lead the entire
  public leaderboard"***, soft-wrapped across a line break (a literal-space pattern misses
  it; `\s+` finds it), over a four-row wall with **four gold `#1` tags**, the four-entry
  `Best published` column `0.0592 / 0.1195 / 0.0569 / 0.0760` and green `win` margins
  `−15.4% / −15.4% / −19.0% / −5.4%`. Two of the four are losses and both margins flip
  sign, to **+16.0%** and **+1.3%**.
- `certonomous-demo/site/closure.html` — one live `rank 1 of 5`.

**These are exactly the two blockers the V10 grade of 2026-08-16 named**, and both were
repaired in the *tracked* copies inside this round's range — `closure.html` at `cca64eaf`,
`benchmarks.html` at `fe54ec0a`, the latter **forty minutes before this scope closed**.
The archive predates both by two days.

**What is already filed, and what is not.** The class is well covered: **D56**, **D112**,
**D180** (which enumerates *eight* live four-entry claims in this archive), **D200** (a
ninth), **D207**, **D224** (*"all three faults on the gating arm are a shipping bundle
built BEFORE the corrections landed"*) and **D252** (the two rank statements in the
unpacked mirror). **Neither the gold `OUR MODEL LEADS` badges nor the wall heading is
among any of them** — D180's `benchmarks.html` entry is `:148-149`, about the margin, and
D149 covers the badges only on the tracked page. That delta is what is filed here.

### 7.3 The three dispatched execution cells

Three cells were dispatched to run in parallel: **B** (document verification over
`LADDER_V_V10_GRADE_2026-08-16.md`, `LADDER_V_STATE_2026-08-16.md`,
`LADDER_V_D227_ENTITLEMENT_2026-08-16.md`), **C** (over `LADDER_V_V16_ROUND11.md`,
`LADDER_V_V12_V13_V14_GRADE_2026-08-15.md`, `LADDER_V_V5_V8_GRADE_2026-08-15.md`,
`LADDER_V_V5_V14_REGRADE_2026-08-16.md` and the `RULE_O` pair), and **D** (the
instrument/mutation cell over the sixteen scripts and eight test files added or modified
in the range). All three were killed mid-flight by a session-wide network drop and were
resumed from their transcripts rather than restarted.

**Their results are NOT transcribed into this record, and the reason is stated rather than
hidden.** Cells B and C completed and reported **eight** and **fourteen** findings
respectively — including, as relayed to me, two defects in the V10 grade (*"all eight
second-column cells"* which is seven of eight, and *"three of the four `Best published`
values"* which is four of four), a wrong `ACTIVE_RESEARCH.md` locator, and a **dead
positive control inside a grading record**. **I have not read their evidence.** A
fleet-wide hold for a repository reorganization landed before their detail reached me, and
transcribing a count I have not verified is precisely the B4 defect this rung exists to
catch. **Cell D was still running when the hold landed** and its mutation results are
therefore unmeasured here.

**So this round's count is reported as a FLOOR, not a population** — four findings
established by my own execution and set out in full above, against **twenty-seven** if the
cells' twenty-three are admitted on relay. The floor is what this document asserts.

### 7.4 Three ways my own instruments failed, all caught by controls

Recorded because a round that reports only the corpus's defects and none of its own
cannot be trusted about either.

1. **The strike blanker leaked.** A depth-walk pairing let a planted *struck* control
   through on a file carrying 3 `<s>` openers against 1 closer. Caught by the negative
   control on the first run; replaced with non-greedy pairing.
2. **A planted positive control never landed.** The first zip sweep planted into
   `certonomous-demo/site/index.html`, **a member that does not exist**. The readback
   printed `!! NO POSITIVE PLANT LANDED — control is dead` and the run was discarded. Had
   the readback been skipped, a real result would have shipped with no evidence its
   instrument worked. **This is the exact failure the chief named tonight**, reproduced
   here on the first attempt.
3. **A background completion notification is not evidence the work finished.** A
   `nohup`-ed run-tree prefilter reported "completed" when its launcher shell exited; the
   output file then held 514 lines, and a sweep over it returned **0**. Re-reading the
   same file minutes later gave 828, then 927, then 2,834 — **the process was still
   running and the zero was over a partial, still-growing list.** The zero was discarded.
   The arm-4 figure reported in §7.1 is from the completed Python run over the full
   132,049-file enumeration, `FILES SKIPPED: 0`.

**What the controls do and do not prove.** Every control above plants the exact string the
sweep then searches for, so it proves **REACHABILITY** — that the instrument opens that
file, in that arm, in that encoding, and that a struck copy is masked. It does **not**
prove **RECOGNITION**: that the instrument would catch the same claim reworded or
inflected. Where this round asserts an absence, that distinction is stated at the point of
the claim (§9).

---

## 8. Filed, not appended

Findings outside the declared scope are filed as append-only docket rows rather than
folded into the rung. A rung that absorbs every new finding never closes; one that drops
them is worse.

| row | finding |
|---|---|
| **D288** | §7.2 — the shipped archive's two gold `OUR MODEL LEADS` badges and its *"Cases where we lead the entire public leaderboard"* wall: the two surfaces V10 was graded FAIL on, repaired in the tracked copies inside this range and live in the artifact that travels, and not among the eight/ninth/three/two already enumerated for that archive |

**D288 landed at `42177709`** by the private-index form: `GIT_INDEX_FILE` at a temp file,
`git read-tree HEAD`, the blob rebuilt as **HEAD's blob plus this one row** — the worktree
copy was never read, because it held a peer's unlanded rows and a pathspec commit takes the
file from the working tree — and a **mandatory compare-and-swap** on `refs/heads/main`
(`f7caa9b8 -> 42177709`). The ID was allocated by **numeric** high-water inside the same
process that hashed the blob and re-asserted against HEAD's blob immediately before
hashing; `sort -u` is lexical and returns `D99` where the highest is `D287`. Verified
after: 286 rows before and 287 after, **one** differing line between the two blobs,
`hunk_check docs/DOCKET.md:1-0 --at 42177709` → **PASS, declared 1+/0- actual 1+/0-**, and
the row then written back into the worktree copy in numeric order and confirmed
byte-identical to HEAD's, so the two do not silently diverge.

**Nothing in this round was repaired.** `demo-output/website/closure.html`,
`demo-output/website/benchmarks.html`, `scripts/self_audit.py`,
`scripts/check_rung_attribution.py`, `docs/AGENT_ATTRIBUTION.md`,
`docs/USING_THIS_LAB.md` and `sdk/tests/test_rank_claim_*.py` are on this grader's
do-not-touch list; they were read and never written. `dist/` was read and never written.
A grader that repairs its own findings cannot then grade them.

---

## 9. The count, the verdict, and the falsifier

### New material findings established by this grader's own execution: **four**, and the count is a floor

| # | finding | class | new shape? |
|---|---|---|---|
| **F1** | The absolute this lab disproved on 2026-08-15 — *"the register is the only repair a protocol-conforming agent can perform"* — was re-asserted at `e4c1319e` on 2026-08-16, 21 h 24 m after D147 and 20 h 54 m after D162, in a **new** comment block and in the commit's own headline, in a **stronger** form (*"re-records 100644 whatever the index holds"*) that six throwaway repositories falsify directly; the register grew 245 → 251 and the sentence went from one occurrence to two; neither D147 nor D162 is cited | **B3, absolutes** | no — but it is a *recurrence inside the range that filed the counter-measurement*, which round 8's F7 was not |
| **F2** | `LADDER_V_TRIPLE_VERIFICATION.md` was edited **ten times after round 8 landed inside this same range** and its V15 ledger row (`:979`) and its closing-condition row (`:1013`) both still stop at round 7 — *"round 7 FAIL, 25 findings"*, *"Round 7 returned 25"* — while the file names `LADDER_V_V15_ROUND8` exactly once, at `:274`, in an unrelated paragraph. `docs/HANDSHAKE.md:285` carries the same stale sentence, which round 8's own P12 recorded and left | **B4/B5** | **yes** — *the ladder's own ledger is the one durable surface no round updates, because every round writes its record and none owns the row* |
| **F3** | `closure.html`'s V10 repair states the duct gaps as *"between twenty and forty times the 0.0004 band"*; re-derived they are **40.93, 22.21, 25.85** on the flat-band reading and **553.8, 108.1, 30.5** on the per-case reading. Under no reading is the stated band right | B4 | no (minor, and reported as minor) |
| **F4** | **The lab's headline `R-VALUE = 0` is established only to the strength of a token search whose control plants the tokens it searches for.** `LADDER_V_D227_ENTITLEMENT_2026-08-16.md` §1 and `LADDER_V_STATE_2026-08-16.md` §5 — both added inside this range — assert *"no round in this ladder's record has ever declared itself belief-neutral"*; their zeros are real and their controls fired, but they prove **reachability**, not **recognition**. The defensible claim is a floor over tokens. A round writing *"nothing here changes what an outside reader believes"* satisfies R-VALUE's own wording and shares no token with any probe ever run | **B1, the silent-zero class, in its recognition form** | **yes** — a zero can be controlled, honest, reproducible **and still not be the population it is quoted as** |

Twenty-two further findings were returned by cells B and C and are **not** counted here,
for the reason given in §7.3.

### **VERDICT: THIS ROUND IS NOT BELIEF-NEUTRAL.**

**Said in the words the rule requires: round 9 of V15 did NOT find nothing. It found
things. R-VALUE's consecutive-belief-neutral count therefore remains at ZERO, and this
round contributes nothing toward closing V15.**

**The reasoning, and why it is not a formality.**

- **F2 is a new shape and it is about this rung's own instrument.** Every other V15
  finding has been about text the ladder graded. F2 is about the ledger the ladder grades
  *with*: a row that eleven commits passed through in one range without one of them
  absorbing the round that landed in the middle of it. A rung whose ledger runs a round
  behind cannot report its own convergence, and the closing-condition row at `:1013` — the
  single line that says whether V15 can close — was the stalest thing in the file.
- **F1 is worse than the finding it repeats.** Round 8 recorded a false absolute shipped
  in code. This round records the lab **writing it again**, in a new place, in a stronger
  form, with the disproof already filed under two IDs, and using it to justify growing the
  register by four more files. The measurement that would have stopped it existed for
  twenty-one hours.
- **Five of round 8's ten tracked findings are still live and one is worse** (§5.1). Four
  are genuinely closed, and closed *well* — F1's guard now names its empty arms, M1's
  entry point is now driven, P15's field now varies nineteen ways. But a round cannot be
  neutral over a predecessor that is 40% closed.
- **F4 is a new shape and it lands on the number this rung is graded by.** A zero can be
  controlled, honest and reproducible and still not be the population it is quoted as. The
  lab's `R-VALUE = 0` is such a zero. Finding that is, by definition, a change in what
  someone believed — which is the test.
- **A round that found only closures would still not be neutral if it found F1.** The
  count would be non-zero at one.

**What would falsify this verdict**, each cheaply:

1. **F1 falsified** by a chief ruling that `git -c core.fileMode=true commit -F <msg> --
   <paths>` is not protocol-conforming under `ESCALATION_CHARTER` §9.6 — which rescues the
   *conclusion* and not the mechanism sentence, since Arm A records `100755` from a
   pathspec commit over an index holding `100755`.
2. **F2 falsified** by showing `:979` or `:1013` carries round 8 in any form.
   `/usr/bin/grep -c ROUND8` on each row → 0, at `fe54ec0a` and at `ae09cb3c`.
3. **F3 falsified** by a reading of *"the 0.0004 band"* whose maximum ratio is at most
   forty. The flat-band reading gives 40.93.
4. **F4 falsified** by a recognition control: vary the *semantic content* of a neutrality
   declaration — do not plant the probe's own tokens — and show the sweep still finds it.
   Until that is run, `R-VALUE = 0` is a floor over tokens and should be reported as one.
5. **The neutrality verdict falsified** by showing F1, F2, F3 and F4 are each already recorded
   in `docs/DOCKET.md` or a prior round document before `cca64eaf`. Checked by ID and by
   phrase: D134/D147/D162 record F1's *premise* and none records the re-assertion;
   nothing records F2, F3 or F4.

### The R-VALUE measurement itself, and the limit of its control

Because this is the only number that can close V15, it was re-derived rather than quoted,
and the sweep was widened past its first form when the reachability/recognition
distinction was raised:

- **First form:** `(is|was|are|were)\s+belief[-\s]+neutral` over all 20,721 tracked paths
  at `fe54ec0a`, strike-blanked, control 1/1 positive and 0/1 struck negative →
  **ZERO occurrences.** `NOT belief-neutral` → **9**, in five documents.
- **Widened to the root word**, because a phrase control proves recognition only of that
  phrase: **every one of the 145 occurrences of `neutral` in the tracked corpus was read
  and classified.** They are: the nine `NOT belief-neutral` declarations; the audit tables
  in `LADDER_V_D227_ENTITLEMENT_2026-08-16.md` §1 and `LADDER_V_STATE_2026-08-16.md` §5
  that measure this same question and reach the same answer; two *"do not score neutrality
  early"* **warnings** in `LADDER_V_V15_ROUND8.md:619` and `LADDER_V_V16_ROUND11.md:712`;
  and the rest are unrelated senses — a neutral colour stop, neutrally buoyant particles,
  behaviour-neutral patches, a neutral UI label.
- **No round of any rung has ever declared itself belief-neutral, and R-VALUE is zero.**
  The two *"round 10 was scored neutral"* sentences are the **warning** against scoring
  neutrality early, not a record that a round was neutral — the misreading this round was
  dispatched not to repeat, confirmed here by reading both in place.

**AND THE LIMIT, WHICH IS A FINDING ABOUT THE LAB'S OWN HEADLINE NUMBER AND IS STATED
HERE RATHER THAN BURIED.** Every instrument that has ever established *"R-VALUE stands at
zero"* — `LADDER_V_D227_ENTITLEMENT_2026-08-16.md` §1, `LADDER_V_STATE_2026-08-16.md` §5,
and this section — is a **token search**, and its positive control plants the tokens it
then searches for. That proves **reachability**, not **recognition**. The defensible
statement is:

> **No round document contains the tokens `R-VALUE`, `belief-neutral`, or any inflection
> of the word `neutral` used to declare a round neutral.**

The strong form — *"no round has ever declared itself belief-neutral"* — **does not follow
from that instrument.** A round that wrote *"nothing here changes what an outside reader
believes"* satisfies the rule's own wording and shares no token with any probe ever run.
**R-VALUE is zero as a FLOOR until someone runs a recognition control**, and every place
this lab reports it — including to the owner — should say so. My sweep widens the token
set from a phrase to the root word and reads all **145** occurrences in place, which
narrows the gap and does not close it.

*(This limit was reached independently by cell B, whose F-9 states the same floor from a
different instrument. Two routes to one boundary is why it is written here as a boundary
and not as a caveat.)*

---

## 10. What this round could not do, and the hold

A fleet-wide hold for a repository reorganization landed while this record was being
written. **Cell D was mid-cell and is unmeasured. Cells B and C completed and their
twenty-two findings are not transcribed here.** Both are named in §7.3 rather than absorbed
or dropped, and the count in §9 is stated as a floor for exactly that reason. The three
findings this document asserts were each established by execution before the hold, at the
frame each is anchored to.

*W-5: every claim above is anchored to the tree it was measured at. Nothing here is
written in the present tense about a moving HEAD.*
