# Using this lab

A newcomer's guide. Every command below was executed against this repository on
2026-08-15 between 18:49Z and 19:25Z, starting from `44ac957a`, and the outputs
quoted are what it printed. Where something is stated but not measured, it says
so. HEAD moved several times during the writing — that is normal here, and it is
why §0 exists.

Read it once, top to bottom. Sections 2–4 are the ones that will cost you a day
if you skip them, so they come before the orientation and not after it.

---

## 0. Frame for everything in this document

    $ git rev-parse --short HEAD
    44ac957a
    $ date -u +%Y-%m-%dT%H:%M:%SZ
    2026-08-15T18:58:51Z

Counts in this file are stamped with the frame they were taken in. That is not
decoration — it is the house rule (`docs/MEMORY_ARCHITECTURE.md` §8.1a, *"The
present tense is banned from durable records"*: a state claim carries its commit
anchor, never a bare "X holds"). The tree moves several times an hour under ten
concurrent agents. **Re-measure rather than quote this file's numbers.** Every
count below is printed with the command that produced it, so you can.

---

## 1. What this lab is, and what it produces

An autonomous CFD laboratory. `README.md`:

> State an engineering objective in plain language; the lab interprets it, forms
> a team of agents, runs **real OpenFOAM solves**, and reports every result with
> a trust tier and a confidence envelope — bounding its own trust rather than
> overclaiming.

Its three stated principles: **real numbers only** ("Hardcode the path, never the
result"); **the lab bounds its own trust** (nothing is labelled VALIDATED without
an experimental comparison per ASME V&V 20 — everything else is TREND ONLY);
**honest uncertainty**.

What it actually produces, in rough order of how much of the tree they occupy:

| Product | Where |
| --- | --- |
| A round-5 entry to an external turbulence-closure benchmark, scored locally | `demo-output/website/CLOSURE_*`, `campaign/` |
| Verification and validation records — ladders, rungs, gate verdicts | `demo-output/website/campaign/` |
| Solve case trees (OpenFOAM/DAFoam/VSPAERO) | `/home/ubuntu/certonomous-runs/` (outside the repo) |
| Sealed one-page PDF certificates with a SHA-256 evidence seal | `demo-output/website/certificates/` |
| A control-room server and the SDK behind it | `sdk/chief_engineer/` |
| The lab's own instrument corpus — checks, guards, sweeps | `scripts/`, `sdk/tests/` |

The headline result, as the record states it (`docs/PRODUCT_LIST.md` §4B): a
round-5 closure score of **0.056647**, scored **locally** at benchmark commit
`deb91557`, with `P(rank 1) = 50%` and an interval of **0–97% at 95%**, against a
**six-entry** board retrieved **2026-08-11T23:33Z** (re-verified unchanged
2026-08-14T21:01Z), with four not-decided pairs, one of them the leader.

Those clauses are not garnish. The rule in that file: no surface, internal or
outward, may print "rank 1" without the interval, the not-decided pairs, and the
board named **by entrant count and retrieval date** — and *"a commit anchor is not
an admissible board identifier: `deb91557` is the four-entry scoring clone and it
scores but does not rank."*

**A warning that applies to this paragraph.** My first draft of it said the
interval was 2–100%. That figure is in the file — struck through, superseded on
2026-08-15, sitting one line above the live one. Strike-and-keep (§7) means the
wrong number stays visible forever, on purpose, and a careless read picks it up.
**Read what the strikes say before you copy a figure out of this corpus.**

**Submissions are PARKED.** Nothing is sent, uploaded, registered or filed
outward. See §7.

---

## 2. The box turns itself off

Root cron runs `/usr/local/bin/auto-stop.sh` every five minutes and powers the
machine down after 30 idle minutes.

    $ sudo -n crontab -l
    */5 * * * * /usr/local/bin/auto-stop.sh

It decides "is anyone working?" from three facts: a solver/mesher process name, a
worker process whose CWD is in the repo *and* burning CPU, and a recently-written
Claude session transcript. There is one override, and it needs no sudo:

    touch /home/ubuntu/Certonomous/.autostop-hold

That holds the box for 24 hours and then lapses by itself (`HOLD_MAX_HOURS=24`).
A hold that never lapses is a bill, which is why it expires. Confirm it is being
honoured:

    $ journalctl -t auto-stop --no-pager -n 3
    Aug 15 18:45:01 ... auto-stop[838608]: ALIVE: hold file set 20h ago
    Aug 15 18:50:01 ... auto-stop[838948]: ALIVE: hold file set 20h ago

### The live gap you must know about

The tracked `scripts/auto-stop.sh` and the installed `/usr/local/bin/auto-stop.sh`
are **not the same file** as of `44ac957a`. Measured:

    $ python3 scripts/installed_registry.py | head -3
    PENDING  auto-stop gate  (scripts/auto-stop.sh -> /usr/local/bin/auto-stop.sh)
             declared divergence, waiver expires 2026-08-21. D65: ...

The tracked copy scans a **glob** of every session-config directory. The installed
copy names exactly one, `/home/ubuntu/.claude-sanaa/projects/...`. Both directories
exist on this box and both hold transcripts:

    $ ls /home/ubuntu/.claude-sanaa/projects/-home-ubuntu-Certonomous/*.jsonl | wc -l
    10
    $ ls /home/ubuntu/.claude/projects/-home-ubuntu-Certonomous/*.jsonl | wc -l
    9

So a session running under `~/.claude` is invisible to the installed gate: an
occupied control room reads as an empty one. The repair is committed and
deliberately **not installed**, because `/usr/local/bin/` is the box's power
control and that belongs to the owner (docket row A4). The registry's own words:
*"Until it is installed, the ONLY thing holding this box is `.autostop-hold`,
which lapses after 24 hours."*

**Practical rule:** touch the hold file when you start, and do not assume your
session is keeping the machine alive.

---

## 3. Your shell's `grep` and `find` are not GNU's

This is the single highest-yield thing in this document. It is `LESSONS.md` L-75,
and it is still true.

    $ type grep
    grep is a function
    grep () { ... exec -a ugrep "$_cc_bin" -G --ignore-files --hidden -I
                   --exclude-dir=.git ... }
    $ grep --version | head -1
    ugrep 7.5.0 ...

`--ignore-files` honours `.gitignore`. This lab gitignores its large artefacts, so
the interactive `grep` sees a minority of the tree. Measured:

    $ grep -rl '' . | wc -l                                    # what grep visits
    12619
    $ command find . -path ./.git -prune -o -type f -print | wc -l
    57448

**12,619 of 57,448 = 22.0%.** A `grep -r` that returns nothing here is a confident,
clean zero over roughly a fifth of the corpus. It is not a negative result.

`find` is `bfs`, which rejects GNU expressions:

    $ find . -maxdepth 1 -newermt "-30 min" ; echo $?
    bfs: error: ... Invalid timestamp.
    1
    $ command find . -maxdepth 1 -newermt "-30 min" ; echo $?
    ./.autostop-hold
    ./.git
    0

Root's cron gets the real GNU tools, which is why `auto-stop.sh`'s own
`find ... -newermt "-30 min"` works in production and would fail if you pasted it
into your shell.

**The fix, every time: `command grep` and `command find`.** `command` bypasses the
shell function and gives you `/usr/bin/grep` and `/usr/bin/find`. Every
`grep`/`find` in this document that is meant to see everything is written that
way. Better still, do not shell out at all: `scripts/lab_check.py` enumerates with
`git ls-files` + `os.walk` for exactly this reason, and says so in its frame line.

---

## 4. The corpus has four arms. Sweep all four.

A sweep that reads one arm and reports a count has stated a number about its own
tooling, not about the lab. Measured at `44ac957a`, 18:52Z:

| Arm | Command | Files |
| --- | --- | --- |
| 1. Tracked | `git ls-files` | 20,688 |
| 2. Untracked, not ignored | `git ls-files --others --exclude-standard` | 2 |
| 3. **Gitignored** | `git ls-files --others --ignored --exclude-standard` | 37,256 |
| 4. **Outside the repo** | `command find /home/ubuntu/certonomous-runs -type f` | 132,049 |

Arm 3 is bigger than arm 1 and is invisible to the shell's `grep`. Arm 4 is bigger
than the whole repository and is invisible to every git command.

The sweep, all four arms:

```bash
cd /home/ubuntu/Certonomous
PAT='0\.056647'

# 1. tracked
git grep -lI "$PAT" -- .

# 2. untracked, not ignored
git ls-files --others --exclude-standard -z | xargs -0 -r command grep -lI "$PAT"

# 3. gitignored  <-- the one everyone forgets
git ls-files --others --ignored --exclude-standard -z | xargs -0 -r command grep -lI "$PAT"

# 4. the run tree, outside the repo
command grep -rlI "$PAT" /home/ubuntu/certonomous-runs/
```

For that literal, arm 1 returned 231 files and the shell's `grep -rlI` returned
207 — and the 24-file difference is **not** the gitignored arm. It is 27 *tracked*
files that `.gitignore` patterns also match, minus 3 that git skips for a
different reason (next paragraph). The shell's grep misses tracked files too.

### The fifth blind spot: `.gitattributes`

`git grep -I` skips files git *considers* binary, and git's opinion comes from
`.gitattributes`, not from the bytes:

    $ cat .gitattributes
    *.pdf binary
    *.png binary
    *.jpg binary
    *.stl binary
    *.obj binary

981 tracked files carry that mark at `44ac957a`, and **12 of them contain no NUL
byte at all** — they are plain text that every sweep in this lab silently skips.
Five are sealed product certificates. See §10, where this is worked end to end.

**When a sweep must be complete, add `--text`:** `git grep -lI --text "$PAT"`.

---

## 5. The map

| Where | What lives there |
| --- | --- |
| `docs/charters/` | The nine standing rules. A charter is a rule the lab holds itself to when nobody is watching. `docs/charters/README.md` first. |
| `docs/DOCKET.md` | The queue of real findings that are not this rung's. Where your finding goes. §11. |
| `LESSONS.md` | Numbered lessons, one per thing that actually went wrong. Large and growing — do not read cold. |
| `demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md` | The verification ladder: 16 pre-registered rungs gating the closure entry. §12. |
| `docs/PRODUCT_LIST.md` | The canonical task list. `[x]` only when fully done with evidence linked; every cross-off adds a new item. |
| `demo-output/website/ACTIVE_RESEARCH.md` | The outward-facing status board, measured numbers only. |
| `scripts/` | The lab's instruments — checks, guards, sweeps, the runner. |
| `sdk/` | The product source: control-room server, OpenFOAM adapter, certificates, and `sdk/tests/`. |
| `models/` | Input geometry and the validation curriculum. |
| `mission-output/`, `demo-output/` | Mission artefacts and the published surface. |
| `/home/ubuntu/certonomous-runs/` | The solve case trees. Outside the repo, gitignored by being elsewhere. |

Sizes, so you know what you are walking into (measured 2026-08-15):

    $ command grep -c '^## L-' LESSONS.md            # numbered lessons
    84
    $ command grep -oE '^## L-[0-9]+' LESSONS.md | tail -1
    ## L-84
    $ wc -l docs/charters/VERIFICATION_CHARTER.md docs/DOCKET.md
     1616 docs/charters/VERIFICATION_CHARTER.md
      499 docs/DOCKET.md

---

## 6. Checking the lab's health in one command

    python3 scripts/lab_check.py --no-tests      # fast tier, ~3 min
    python3 scripts/lab_check.py                 # everything, ~20 min
    python3 scripts/lab_check.py --list          # enumerate, run nothing, seconds

I ran both. The fast tier took 188 s of measured wall time across 13 gates. The
full run took **1,221 s wall (20.4 min), 1,302 s user + 51 s system CPU**, adding
the suite: **1,830 tests in 75 files, 1 failed**. Both returned **FAIL, exit 1**.

The fast tier's frame block:

    FRAME -- what was looked at, and how it was found
      repo               /home/ubuntu/Certonomous
      HEAD               44ac957a
      tree               live working tree (6 path(s) modified or untracked)
      enumeration        git ls-files + os.walk over scripts, sdk/tests
                         (never the shell's grep/find)
      candidates         150  (tracked 149, on disk 150)
      admitted           88  (13 script gate(s), 75 test file(s))
      skipped            62  (6 of them could be hiding a verdict)

and its verdict:

    VERDICT: FAIL
      exit 1 -- BLOCKING. A check that ran returned a finding.
      frame: 13 check(s) ran, 62 not admitted, 7 unrun check(s) whose skip
             reason could be hiding a verdict
      FAIL scripts/calibration_scorecard.py: exit 2
      FAIL scripts/check_absolutes.py: exit 1
      FAIL scripts/contention_audit.py: exit 1
      FAIL scripts/self_audit.py: exit 1

### This FAIL is correct, not broken

Read that as designed. `lab_check.py` is three-valued, and each of those four
verdicts is a real finding about the lab that someone has not yet closed —
`self_audit.py` alone reported 2 of 1,204 repo-rooted citations not resolving,
5 shipped-bundle files behind the tree, and 25 lab records claiming rank 1
without what the ladder requires. The runner is doing its job; the lab is not
green. **Do not "fix" the runner. Do not widen a gate to make it pass** — that is
forbidden outright (`VERIFICATION_CHARTER.md` §8: *"A gate is never widened after
a result misses it."*).

The full run adds a second frame block, and it is worth reading because it is the
answer to "what did *the suite* mean on this run" — a question this lab got wrong
once by reporting a single file's 115 passes as a full suite:

    SUITE FRAME -- what 'the suite' meant on this run
      argv                  /usr/bin/python3 -m pytest sdk/tests -q
                            -p no:cacheprovider --junitxml=/tmp/...xml
      test files enumerated 75
      test files collected  75
      tests collected       1830  (failed 1, errored 0, skipped 0)
      __pycache__ purged    3 directories, before the run
                            (stale bytecode has inverted results here)

The one failure is `sdk/tests/test_exec_bits.py`, for the reason in §9.2. Note
also that the tracked cron file records this suite as **1,609 tests** measured on
2026-08-14; it collected **1,830** on 2026-08-15. Neither number is wrong. That is
what a count without a frame does, and it is why every count in this document
carries the moment it was taken.

Two more things a newcomer must read correctly:

- **`skipped` is the coverage statement, not a footnote.** 62 of 150 candidates
  were not run, in named classes: `shell` (15), `cannot-fail` (10),
  `writes-to-tree` (6), `requires-arguments` (4), `no-entry-point` (6). Six of
  them "could be hiding a verdict" and are reported as UNKNOWN, not as passes.
- **UNKNOWN is not a soft pass.** `--no-tests` returns
  `UNKNOWN sdk/tests (pytest): skipped -- needs-compute`. That is a statement
  about the instrument, not about the lab.

Nothing schedules this. `scripts/installed/certonomous-lab-check.cron` exists,
is tracked, and is **inert** — the registry reads it `ABSENT`, as it does the
pre-push hook. Every check in this lab still reddens only when a person types
its name.

    $ python3 scripts/installed_registry.py | command grep -E '^(ABSENT|PENDING)'
    PENDING  auto-stop gate  ...
    ABSENT   nightly lab check cron  (scripts/installed/certonomous-lab-check.cron
             -> /etc/cron.d/certonomous-lab-check)
    ABSENT   pre-push hook  ...

One operational note: `lab_check.py` buffers stdout when redirected. My first run
wrote a zero-byte file for three minutes and then everything at once. Use
`python3 -u` if you are watching a file.

---

## 7. The standing rules

Sourced from the charters. Where a rule you have been told is *not* in the
charters, this section says so — that distinction matters more than the rule,
because the lab must never present its own invention as the owner's policy.

**Submissions are PARKED, and all external interaction is the owner's.**
`GOALS_AND_PROPOSALS_CHARTER.md` §8: *"every 'submission' action is parked at her
discretion. Challenge and measurement work continues at full priority. Nothing
external gets sent."* The class includes the closure-challenge entry, an upstream
DAFoam report, a workshop entry, contacting a steward.
`SUPERVISOR_RULINGS.md` R9: anything outward-facing *"carries the company's name
and stays hers."* Parked is not cancelled; what no longer exists is any reading
under which readiness slides into sending.

**Compute authorization is the owner's.** `ESCALATION_CHARTER.md` §1: *"Initiative
comes from the lab. The veto stays with the human."* Note honestly: **the numeric
free-spend threshold is not enacted.** §4 is marked *"PROPOSAL. Nobody has set a
number."* What binds is `COMPUTE_BUDGET_CHARTER.md` §3's per-rung defaults (new
capability 60 core-min, written report 20, one ladder rung 20) and *"A budget
overrun stops the run. It does not get a new budget."* Docket A2: *"Katie
authorises compute, or does not. Nothing runs meanwhile."* Until you are told
otherwise, you run no solves.

**Scoring calls are chief-authorized.** `SUPERVISION_CHARTER.md` §4, under
"retained and not delegable": *"No agent at any level makes a scoring call on the
challenge; the chief authorizes, and the outward act stays the owner's per ruling
R9."* The ledger stands at **6** — but that count is **not** in the charters; it
lives in `docs/PRODUCT_LIST.md:1803` and the closure surfaces, and `docs/DOCKET.md`
D30 records that the whole scoring-call discipline is self-imposed rather than a
benchmark rule. Quote it as lab discipline, with its source.

**Commits are single-step pathspec.** `ESCALATION_CHARTER.md` §9.6/§9.6a/§9.6b —
and note the charter's own header warns the git rule lives at the very end of the
file, below `## Related`, because §3's earlier form is superseded. §9.6: *"every
commit stages its files BY EXPLICIT PATH. `git add -A`, `git add .`, and
`git commit -a` are forbidden."* §9.6a: commit with `git commit -- <paths>` *"in a
single step ... the bare `git commit` after it is what the rule now forbids."*
§9.6b adds a mandatory `git diff <path>` read before committing a shared file.
Mechanics and traps in §9 below.

**Docket IDs are append-only and never renumbered.** Not a charter — it is
`docs/DOCKET.md`'s own header, attributed to Katie, W-4, 2026-08-11: *"IDs ARE
APPEND-ONLY AND STABLE. NOTHING IS EVER RENUMBERED."* On collision *"both keep
their text and the later one takes the next free ID."* Superseded IDs are struck
in place and kept, never reused. *"An ID is a reference target; moving it breaks
every citation you cannot see."*

**Durable records carry commit anchors, not present tense.** Not a charter —
`docs/MEMORY_ARCHITECTURE.md` §8.1a: *"A state claim carries its commit anchor.
'As of `08a87cc7`, X holds' — never a bare 'X holds'."* The test: could the world
change without this sentence changing? Rules and definitions are exempt.

**Strike and keep; never silently overwrite.** `docs/MEMORY_ARCHITECTURE.md` §8.1:
*"A record whose claim has been superseded is amended in place, dated, with the
original text retained. Never a silent edit, and never a deletion."* And: *"A
commit that refutes a standing record must amend that record in the same commit."*
Charter instances: `VERIFICATION_CHARTER.md` §2b (*"Originals are always retained
and struck, never rewritten"*) and `SUPERVISION_CHARTER.md` §5, which is itself a
worked example — a struck clause left visible with its explanation deliberately
unstruck beside it.

**A figure carries its basis.** Charter-binding per figure class rather than as
one general rule: spend figures state gross or cleaned and name the cleaning rule
(`COMPUTE_BUDGET_CHARTER.md` §2, and *"A figure that is neither, or that does not
say which it is, is not published"*); no cost is presented as measured without a
record; a caption is derived from the value's provenance or it is not printed
(`VERIFICATION_CHARTER.md` §6); a reported order never appears alone (§3.2). The
sweeping general version is folklore rather than charter text — cite the specific
clause for your figure class.

---

## 8. The verification standards

This is the actual method, and it is the reason the lab's output is worth
anything. Learn these before you write a check.

**1. A gate must be able to fail.** `VERIFICATION_CHARTER.md` §2a:

> Every gate answers two questions before it is a gate: (1) What result would make
> this gate FAIL? (2) Could a wrong treatment still PASS it?
> **A gate whose quantity is derivable by construction from its own inputs is an
> IDENTITY, not a control. It may be reported. It may never be gated on.**

Both answers go into the pre-registration where the gate is fixed. The honest
alternative — *"we know of no way a wrong treatment passes this"* — is allowed;
silence is not. `GOALS_AND_PROPOSALS_CHARTER.md` §1 states the same as a
disqualifier: *"A metric that cannot fail is not a gate."*

**2. Three-valued, and never PASS from an empty set.**
`VERIFICATION_CHARTER.md` §9, `ran_before_found`: *"absence of error evidence is
not evidence of a clean result."* Every parser and gate answers **did the check
run** before **what did it find**, and carries a third verdict for *unknown* that
is not collapsed into the bad one. The lab's canonical failure here: a
mesh-quality parser returned `clean` on a log where the tool had fatally errored,
because it matched error *patterns* and a crashed log contains none. *"A gate that
reads silence as success can manufacture a pass, which outranks every gate that
merely misses one."* The empty-set clause is written into
`SUPERVISION_CHARTER.md` §3a: the sweep returns *"PASS / FAIL / UNKNOWN (an empty
candidate set is UNKNOWN, never PASS)"*.

**3. Every instrument needs a positive control AND a must-not-match control.**
`LESSONS.md` L-84: *"A control that only shows an instrument firing is half a
control. The other half is a set it must NOT fire on"* — planted outside the frame
to test reach, and planted just inside the boundary to test precision. A widened
matcher needs a near-miss it must reject, measured, before the figure ships.
§10 below runs all three kinds.

**4. Findings are verified by re-derivation, not by an instrument's silence.**
`VERIFICATION_CHARTER.md` §10: check the primary source, and *"Treat agreement
with expectation as a reason for more scrutiny, not less."* §14: *"An attribution
is a claim, and it is a claim about a file. Name the file, and open it before the
finding leaves the room."* §6a warns that a check written with the same helpers as
the thing it checks proves only that a number was transcribed faithfully.
"I searched and it is not there" is evidence about your search.

**5. A claim states its frame.** `VERIFICATION_CHARTER.md` §6a, *"The referent
travels with the verdict"*: a verdict label — VALIDATED, PASS, verified,
confirmed, reproduces — carries the thing it was checked against, on every surface
it appears on. Three admissible answers: EXTERNAL (name it — *"validated against
the literature"* names nothing), SELF-REFERENTIAL (*"This is not a defect and must
not be hidden"*), or NONE. §3.3: a guard states the sample it measured over, and
that sample is the sample the quantity was computed from.

**And the bright line the whole charter turns on** (§1):

> Done means a gate has a verdict, the verdict cites an artifact, and the artifact
> is still on disk.

Four more worth knowing on day one: a failed gate blocks every downstream rung
(§3); a gate that was not reached is stated as not reached, never replaced by a
nearer gate that was (§2); nothing the lab fits, inverts or tunes on may be a
scored case of a benchmark it reports a score against (§11); pre-register before
compute, no exceptions for short runs (`ESCALATION_CHARTER.md` §9).

---

## 9. Git here has four traps, and three of them are silent

### 9.1 Backticks in `git commit -m`

The message goes through the shell. Three variants, all executed in a scratch
repository:

**Unbalanced backtick — the commit never runs, and neither does anything after
it in the same invocation:**

    $ git commit -m "use `git ls-tree HEAD" -- a.txt
    /bin/bash: eval: line 28: unexpected EOF while looking for matching ``'
    $ git log --oneline -1
    fbaf9b8 fix  handling          # unchanged. HEAD did not move.
    $ git status --short
    M  a.txt                       # still staged, nothing committed

**Balanced backticks — worse, because it succeeds and lies:**

    $ git commit -m "anchored at `git rev-parse --short HEAD`" -- a.txt
    [master 4e4dc1d] anchored at fbaf9b8

The message anchors at `fbaf9b8`, the **parent**. The substitution ran before the
commit existed. A commit-anchored record that anchors at the wrong commit is
exactly the failure the anchor rule exists to prevent.

**The working form:**

    printf 'use `git ls-tree HEAD` to verify\n' > /tmp/msg.txt
    git add <paths>
    git commit -F /tmp/msg.txt -- <the same paths>
    git log --oneline -1        # <-- always. This is the verification.

`git log --oneline -1` is not optional politeness. It is the only thing that
distinguishes "committed" from "the shell ate it".

### 9.2 `core.filemode=false` silently discards the exec bit

    $ git config --get core.filemode
    false

Executed in a scratch repo with `core.filemode false`, one shebang file:

    $ git update-index --chmod=+x run.sh
    $ git ls-files -s run.sh
    100755 4163036e... 0   run.sh          # the INDEX has the bit
    $ git commit -q -m "content change" -- run.sh
    $ git ls-files -s run.sh
    100755 854c7ea1... 0   run.sh          # index still says 755
    $ git ls-tree HEAD run.sh
    100644 blob 854c7ea1...   run.sh       # THE COMMIT SAYS 644

A pathspec commit re-derives the mode from the worktree, and with
`core.filemode=false` the worktree has no opinion. Even `chmod +x` first does not
help:

    $ chmod +x run.sh; git add run.sh; git commit -q -m c3 -- run.sh
    $ git ls-tree HEAD run.sh
    100644 blob ddd98c15...   run.sh
    $ chmod +x run.sh
    $ git -c core.fileMode=true add run.sh
    $ git -c core.fileMode=true commit -q -m c4 -- run.sh
    $ git ls-tree HEAD run.sh
    100755 blob e197101e...   run.sh       # works

**Verify with `git ls-tree HEAD`, never `git ls-files -s`.** `ls-tree` is what a
clone materialises; `ls-files -s` is what your index believes. `sdk/tests/test_exec_bits.py`
reads `ls-tree` on purpose — its own first draft read `ls-files -s` and passed on
a mode that was staged and never committed.

This interacts badly with the pathspec rule, and the interaction is already filed
as docket **D134** by another session: under a partial commit the mode cannot be
set at all, so the exec-bit waiver register can only grow. That test is red right
now for exactly this reason:

    $ python3 -m pytest sdk/tests/test_exec_bits.py -q
    1 failed, 14 passed in 1.64s

### 9.3 `git status` reads stale under concurrency, and a pathspec isolates by file, not by author

Ten agents write this tree. `git status` has been observed reporting a dirty file
as clean while other sessions committed. Read the content, not the summary:

    git diff -- <path>                 # your uncommitted delta
    git show HEAD:<path> | diff - <path>   # against what is actually committed

And understand what a pathspec commit does and does not buy you.
`ESCALATION_CHARTER.md` §9.6b: **a pathspec isolates by FILE, not by AUTHOR.** On
a shared, high-traffic file like `docs/DOCKET.md` there is no safe granularity —
committing your row commits whatever anyone else has left uncommitted in that
file. §9.6b makes the `git diff <path>` read before the commit mandatory, and
§9.6c forbids the polite alternative of leaving it uncommitted. So: read the diff,
commit, and **name in your commit message what else you carried**.

**And it cuts both ways, which is the half people miss.** While this guide was
being written I appended a docket row and went to finish a paragraph before
committing it. Fourteen minutes later:

    $ git log --oneline -3 -S'| D139 |' -- docs/DOCKET.md
    c298f5b3 Correction to D135: 16 wall-clock call sites, not 19

My row is committed, intact, byte-for-byte — inside **another session's** commit,
whose message is about something else entirely and does not mention it. Nobody
did anything wrong: that session read the diff, saw a complete row, and committed
the file it was told to commit. **On a shared file, "I will commit it in a
minute" is not a plan.** Write the row and commit it in the same breath, and when
you go looking for the commit that carries your work, search by content
(`git log -S`) rather than by your own commit messages.

Also forbidden on a shared tree (`ESCALATION_CHARTER.md` §3): `git reset --hard`,
`git stash`, `git checkout -- <path>`, `git clean`. *"An unexpected uncommitted
change is inspected, never reverted."*

### 9.4 `pgrep` and `pkill` match their own invoking shell

    $ bash -c 'pgrep -f "zzz_unique_marker_pattern"; echo exit=$?'
    839893
    839916
    exit=0

That pattern appears nowhere on this box. Both PIDs are the shells running the
command. A `pkill -f <pattern>` kills its own shell, and the chained command after
it silently never runs. This is not hypothetical — it happened while writing this
document: `pgrep -af 'lab_check'` returned the PID of the `bash -c` running the
`pgrep`. Match on process name with `pgrep -x`, or filter your own PID out.

---

## 10. Worked example, executed end to end

**The task.** §4 claims `git grep -I` has a blind spot created by
`.gitattributes`. Measure it, control it both ways, and decide whether it is
material.

### Step 1 — state the frame before measuring

Repository `/home/ubuntu/Certonomous` at `44ac957a`, live working tree,
2026-08-15T18:58Z. Population: tracked files only (`git ls-files`). "Binary" means
*git's* opinion via `git check-attr binary`, not the bytes. "Text" means no NUL
byte in the first 8,000 bytes.

### Step 2 — measure

```bash
git ls-files -z | xargs -0 -r git check-attr -z binary --
```

981 tracked files carry `binary: set`, distributed
`{.png: 875, .stl: 54, .pdf: 50, .obj: 2}`. Reading the first 8,000 bytes of each:
**12 contain no NUL byte.** They are:

    demo-output/acts/round3/airliner_certificate.pdf
    demo-output/acts/round3/naca_certificate.pdf
    demo-output/acts/round3/valve_certificate.pdf
    demo-output/website/campaign/F8_runs/phase6_mrf/constant/triSurface/blade.stl
    demo-output/website/certificates/b52-certificate-current.pdf
    demo-output/website/certificates/b52-certificate-redesign.pdf
    demo-surfaces/motorBike.obj
    docs/papers/Paper3.pdf
    models/airplane/airplane.stl
    sdk/geometry/airliner_wing_span52.stl
    sdk/geometry/airplane.stl
    sdk/geometry/motorBike.obj

### Step 3 — three controls (L-84: a positive control is half a control)

**Positive control** — a literal that provably is in one of the 12:

    $ command grep -c '0\.056647' demo-surfaces/motorBike.obj
    3
    $ git grep -lI '0\.056647' -- demo-surfaces/motorBike.obj ; echo "exit=$?"
    exit=1                                    # the sweep sees nothing
    $ git grep -lI --text '0\.056647' -- demo-surfaces/motorBike.obj
    demo-surfaces/motorBike.obj               # --text recovers it

**Must-not-match / instrument-capability control** — the same literal in an
ordinary tracked file, to prove the miss is specific to the mark and not a broken
pattern:

    $ git grep -lI '0\.056647' -- docs/PRODUCT_LIST.md ; echo "exit=$?"
    docs/PRODUCT_LIST.md
    exit=0

**Boundary control** — a genuinely binary marked file must *stay* skipped, or the
finding would be "git grep skips binaries", which is correct behaviour and not a
defect:

    $ python3 -c "print(b'\0' in open('demo-output/Gui_issue.png','rb').read(200))"
    True

The finding is therefore scoped to exactly the 12 text-but-marked files, and no
wider.

### Step 4 — re-derive rather than trust the instrument's silence

Does the blind spot cover anything claim-bearing? Open the files.

    $ command grep -aoE '\(([^)]{3,60})\) *Tj' \
        demo-output/website/certificates/b52-certificate-current.pdf | head -4
    (CERTONOMOUS) Tj
    (CERTIFICATE OF AUTONOMOUS SOLVE) Tj
    (Mission geometry-study-b52) Tj
    (GEOMETRY) Tj

The certificate PDFs are uncompressed: their claim text is plain ASCII that GNU
`grep` reads directly. So five of the lab's **sealed product certificates** —
its most claim-bearing artefact — are invisible to every `git grep -I` sweep in
this repository. That makes it material rather than a curiosity.

### Step 5 — state what it cannot see

This measurement cannot see: whether any past sweep actually missed a live claim
in those 12 (that is a history question, and this measures the mechanism); whether
the compressed PDFs elsewhere carry claims a `--text` sweep would still miss
(compression defeats grep regardless of the mark); and the same class of mark in
arms 3 and 4, which `git grep` never reaches at all.

### Step 6 — file a docket row

Check the highest ID **first**, and check it in both frames, because another
session's row may be uncommitted:

    $ git show HEAD:docs/DOCKET.md | command grep -oE '^\| \**[A-G][0-9]+' | ...
    highest D in HEAD:      133
    highest D in worktree:  134     # D134 exists only in the working tree

So the next free ID looked like **D135**. **It was not.** Between checking the
highest ID at 19:03Z and writing the row about ninety seconds later, another
session appended D135, D136, D137 and D138 to the working tree. The append was
guarded by an assertion and it fired:

    AssertionError: D135 already taken -- re-check the highest ID

This is the docket's collision rule doing its job, live: *"both keep their text
and the later one takes the next free ID; the earlier one is not moved."* I am
the later writer, so the row is filed as **D139** and nobody's ID moves. Had the
append been unguarded it would have produced two rows numbered D135 and every
citation to either would have become ambiguous — which is why the row is written
by a script that asserts its own ID is free, not by hand.

Row filed as D139 in `docs/DOCKET.md` §D, carrying the finding, where it was
found, its frame, what it cannot see, what would settle it, and its owner.

### Step 7 — commit

The intent was one pathspec commit carrying this document and the D139 row:

    git add docs/USING_THIS_LAB.md docs/DOCKET.md
    git commit -F <msgfile> -- docs/USING_THIS_LAB.md docs/DOCKET.md
    git log --oneline -1

**That is not what happened, and the difference is the lesson.** In the minutes
between appending D139 and reaching this step, another session committed
`docs/DOCKET.md` for its own reasons and carried D139 with it:

    $ git show HEAD:docs/DOCKET.md | command grep -c '^| D139'
    1
    $ git log --oneline -3 -S'| D139 |' -- docs/DOCKET.md
    c298f5b3 Correction to D135: 16 wall-clock call sites, not 19

Verified intact — the committed row and the worktree row have the same MD5. So
the commit here carries only `docs/USING_THIS_LAB.md`; re-committing an already
committed row would have been a no-op at best. See §9.3: a pathspec isolates by
file, not by author, and on `docs/DOCKET.md` that is true in both directions.

The honest summary of this worked example: the sweep, the controls, the
re-derivation and the row all went as planned; **the commit step did not**, and
the guide says so rather than printing the command it meant to run.

---

## 11. When you find something wrong

It goes in `docs/DOCKET.md`. The docket exists because of a real tension: *"a rung
that absorbs every new finding never closes; a rung that drops them is worse."*
Its header: **"This is a queue, not an archive. An item leaves it by being
executed or by Katie ruling it out — never by ageing."**

**The ID rules, which are absolute:**

- IDs are append-only and stable. **Nothing is ever renumbered.**
- Take a fresh ID. **Check the highest in use first — in HEAD *and* in the working
  tree**, because a concurrent session's row may not be committed yet.
- On a collision, both writers keep their text and the **later** one takes the next
  free ID. The earlier one is not moved.
- Superseded IDs are struck in place and kept, never reused.
- Sections are lettered: `A` Katie's, `B` machinery, `C` memory, `D` rung
  residuals (the bulk), `E` standing task items, `F` repo professionalization
  (blocked by design), `G` naval campaign. Sub-items take a letter suffix: `D8b`,
  `B3a`, `G1c`.

Measured at 18:58Z on 2026-08-15: 170 rows in the working tree, 169 in HEAD,
highest `D134` (working tree only). By 19:05Z the highest was `D138`. Re-measure
immediately before you allocate, and **guard the write**:

```bash
git show HEAD:docs/DOCKET.md | command grep -oE '^\| \*{0,2}[A-G][0-9]+' | sort -u
command grep -oE '^\| \*{0,2}[A-G][0-9]+' docs/DOCKET.md | sort -u
```

Do not hand-type the append. Write it with something that asserts the ID is free
at the moment of writing — checking and writing are two moments, and four IDs
were allocated by another session in the ninety seconds between them while this
guide was being written (§10, step 6).

**What a row must contain** (from the docket header, and from what every good row
in it actually does):

1. **The finding, stated so it can be wrong.** Bold the claim.
2. **Where it was found** — a file, a line, a commit, a timestamp. Named, opened.
3. **What it would take to settle it** — concretely, including "no compute needed".
4. **What it cannot see.** The best rows in that file all carry this.
5. **Who owns it**: fleet, chief, or Katie.

There is a live dispatch-claim block in section B: **claim an item there before
you dispatch work on it**, because two chief sessions read the same directive and
will otherwise dispatch the same agent twice.

A citation guard runs over this:

    $ python3 scripts/docket_citation_guard.py ; echo "exit=$?"
    ... exit=0

It exists because the dangerous defect is not a dangling citation — it is a
citation to an ID you have not filed yet, which silently comes **true** when
another session allocates that number for something else.

---

## 12. Known-open state — read the sources, not this paragraph

Anything enumerated here would be stale within hours. Two places carry the truth.

**The verification ladder.**
`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md` — 16 pre-registered
rungs in four passes (re-derivation, adversarial, cold reproduction, structural),
gating the closure entry. A rung is a named criterion with a declared closing
condition, graded by a **non-author**, shipping an evidence record. Its green rule
is a fixed point, not a clean sweep: every rung PASS, *and* a full re-run over the
previous round's text introducing zero new failures, measured by someone who wrote
none of it.

The file's own status line (line 3): *"**STANDING PROTOCOL, EXECUTION PARKED.**
Katie parked submissions on 2026-08-07"*.

**The ladder is NOT green as of 2026-08-15.** Its live block, at line 624 at the
time of writing, reads *"**GREEN REQUIRES, as of 2026-08-15 — and the gate is
still shut:**"* over a table of what is still open, and closes
*"**Nothing here marks any rung green, and this pass has no standing to.**"*

**Go and read that block; do not take a rung list from here or from anywhere
else.** The file is 1,000 lines, several agents edit it concurrently, and it
contains struck entries, dated amendments and superseded status tables that
disagree with each other by design — its own summary table and its live
green-requires block did not agree on two rungs when I read them, and resolving
that is a grader's job, not a reader's. The one durable statement is the one
above: the gate is shut.

**The docket.** `docs/DOCKET.md`. Note honestly: the D table has **no status
column** by design, so open-versus-closed cannot be counted mechanically without
inventing a frame. The header's rule is the reading — an item that has not been
executed or ruled out is still in the queue. Row D42 records the failure mode:
an item that was executed and stayed.

**The lab check.** `python3 scripts/lab_check.py --no-tests` returns FAIL today,
and §6 explains why that is the correct output.

---

## 13. What this document could not verify

Stated rather than omitted, per §8.5.

- **Nothing about `lab_check.py` is second-hand** — both tiers were run here
  (188 s and 1,221 s, both exit 1). But note that the full run happened on a box
  that had other agents' work on it at the same time, so the CPU figure is a
  measurement of this box under load, not a clean benchmark.
- **Solver and scoring behaviour.** No solve was run and no scoring call was made,
  under §7. Everything about OpenFOAM/DAFoam execution here is read from records.
- **Whether the 12 blind-spot files ever hid a live claim.** §10 measures the
  mechanism, not its history.
- **The `git status` staleness trap specifically.** I recorded it from
  `LESSONS.md` and from `ESCALATION_CHARTER.md` §9.6b, whose text is verified; I
  did not reproduce a *stale read* myself, because it needs a race I cannot
  schedule. The related author-isolation failure in §9.3 I did not have to
  simulate — it happened to this document's own docket row while it was being
  written.
- **Charter clauses cited via a reading pass.** Every quotation in §7 and §8 was
  re-checked by locating its exact line in its file. One quotation offered to me
  during drafting — a supposed `LESSONS.md` L-75 line reading *"a number is defined
  by its frame, its filter, and the moment it was taken"* — **does not exist in
  this corpus** (L-75 is the `grep`/ignore-files lesson) and was cut rather than
  paraphrased into place. If you find a quote here you cannot locate, treat it the
  same way and say so.

---

## 14. Your first hour, as a checklist

1. `touch .autostop-hold` — §2.
2. `type grep` and confirm it is a function; prefix everything with `command` — §3.
3. `git status` — see who else is mid-write before you touch anything.
4. `python3 scripts/lab_check.py --no-tests` — see the lab's real state, FAIL and
   all — §6.
5. Read `docs/charters/README.md`, then `VERIFICATION_CHARTER.md` §1, §2a, §9.
6. Read the docket header rules, then skim the last ten `D` rows for house style.
7. Sweep all four arms before you claim any count — §4.
8. When you commit: `git add <paths>` → `git commit -F <msgfile> -- <same paths>`
   → `git log --oneline -1` — §9.
