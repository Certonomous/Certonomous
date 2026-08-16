# Using this lab

A newcomer's guide. Every command below was executed against this repository on
2026-08-15 between 18:49Z and 19:25Z, starting from `44ac957a`, and the outputs
quoted are what it printed. Where something is stated but not measured, it says
so. HEAD moved several times during the writing — that is normal here, and it is
why §0 exists.

Read it once, top to bottom. Sections 2–4 are the ones that will cost you a day
if you skip them, so they come before the orientation and not after it.

> **SECOND PASS, 2026-08-15 19:21Z–19:50Z.** HEAD moved under it the whole time —
> `a0f89c4b` at 19:23Z, `08889ffc` at 19:24Z, `9af7e2d3` at 19:32Z, `f732ebaf` at
> 19:44Z — which is the conditions this document describes, not an excuse. A different
> agent — dispatched as *"cold-read acceptance test of the handbook"*, no part of
> writing it — followed this document from the top, ran every executable step, and
> repaired what did not hold. Its edits are marked in place: measured figures now
> carry a re-measurement, wrong claims are struck rather than deleted, and two new
> sections (**§11a**, **§11b**) cover ground the original brief did not reach.
>
> **Its verdict on the document: the demonstrations reproduce; some of the
> remedies did not.** See the addition at §13.
>
> *On independence: it cannot be shown from `git log` — every commit here carries
> one shared `Ubuntu` identity (§11a). It rests on the dispatch record: two
> distinct `agent-<id>` transcripts under the same chief session — the author's
> (`ad939a0a9…`, 18:52:28Z–19:21:04Z) carrying 1 `Write` and 13 `Edit`s to this
> file, the reader's (`aab6c8073…`) opening at 19:21:58Z with none. That is 54 s
> after the author's last recorded action and 87 s after its final commit
> `428bf008`. Note the limit honestly: the `Lab-Agent:` trailer would have read
> identically for both, because they are siblings of one session (§11a).*

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

> **Filter `DRY_RUN` out of that, or you will read a test fixture as your box.**
> Re-measured 19:32Z by the cold-read pass: of the last 200 `auto-stop` journal
> lines, **56 were `[DRY_RUN]`** — another agent's test harness exercising
> `auto-stop.sh` against temporary directories, interleaved with the real
> five-minute cron ticks. Among them, in the same minute:
>
>     [DRY_RUN] ALIVE: solver or mesher running
>     [DRY_RUN] idle 90min, shutting down
>     [DRY_RUN] WARNING: no session transcript directory matches
>               SESSIONS='/tmp/tmpg84032_8/.claude*/…' -- clause (3) is BLIND
>
> None of those is about this machine. A `[DRY_RUN] ALIVE` will reassure you that
> your hold works when it says nothing of the kind, and a `[DRY_RUN] idle 90min,
> shutting down` will alarm you for nothing. **The real lines carry no tag:**
>
>     $ journalctl -t auto-stop --no-pager -n 200 | command grep -v DRY_RUN | tail -2
>     Aug 15 19:25:01 ... auto-stop[939496]: ALIVE: hold file set 0h ago
>     Aug 15 19:30:01 ... auto-stop[946758]: ALIVE: hold file set 0h ago

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
occupied control room reads as an empty one.

> **Verified directly by the cold-read pass, rather than inferred from the
> registry.** `/usr/local/bin/auto-stop.sh` is `-rwxr-xr-x root root` — **it is
> world-readable, no `sudo` needed**, so you can read the file that actually runs
> instead of trusting a summary of it (`VERIFICATION_CHARTER.md` §14: *"name the
> file, and open it before the finding leaves the room"*). `diff` against the
> tracked copy:
>
>     installed:  SESSIONS=${SESSIONS:-/home/ubuntu/.claude-sanaa/projects/-home-ubuntu-Certonomous}
>     tracked:    SESSIONS=${SESSIONS:-/home/ubuntu/.claude*/projects/-home-ubuntu-Certonomous}
>
> and the installed clause is `find "$SESSIONS" … -newermt … | grep -q .`, which
> can only ever see the one literal directory. Confirmed, not deduced.
>
> **The two constants quoted in this section are the same in both copies** —
> `IDLE_MINUTES=${IDLE_MINUTES:-30}` and `HOLD_MAX_HOURS=24` — which is worth
> stating explicitly, because a section that tells you the two files differ and
> then quotes numbers without saying which file they came from has invited you to
> guess. They came from both.

The repair is committed and
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

**12,619 of 57,448 = 22.0%** at `44ac957a`, 18:52Z. A second agent re-measured at
`08889ffc`, 19:24Z and got **12,623 of 57,451**; four minutes later, **12,624 of
57,439**. The file counts move every few minutes under ten concurrent agents. The
**ratio does not** — it is 22.0% in all three. So do not quote a pair from this
page; compute the ratio:

    $ echo "$(grep -rl '' . | wc -l) $(command find . -path ./.git -prune -o -type f -print | wc -l)" \
        | awk '{printf "%d of %d = %.1f%%\n", $1, $2, 100*$1/$2}'
    12624 of 57439 = 22.0%

A `grep -r` that returns nothing here is a confident, clean zero over roughly a
fifth of the corpus. It is not a negative result.

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
into your shell. *(Inference, not measurement — root's cron was not run to check
it. The support is that `journalctl -t auto-stop` carries `ALIVE: Claude session
transcript written within 30min (<path>)`, which is that clause returning a hit,
and cron does not source the profile where `find` is redefined. Listed in §13.)*

Both `bfs` and `ugrep` are re-verified at 19:23Z: `find` is still a shell function
resolving to `bfs`, `/usr/bin/find` is still GNU findutils 4.9.0, `grep` is still
a function running ugrep 7.5.0.

**The fix, every time: `command grep` and `command find`.** `command` bypasses the
shell function and gives you `/usr/bin/grep` and `/usr/bin/find`. Every
`grep`/`find` in this document that is meant to see everything is written that
way. Better still, do not shell out at all: `scripts/lab_check.py` enumerates with
`git ls-files` + `os.walk` for exactly this reason, and says so in its frame line.

---

## 4. The corpus has four arms. Sweep all four.

A sweep that reads one arm and reports a count has stated a number about its own
tooling, not about the lab. Measured at `44ac957a`, 18:52Z:

| Arm | Command | Files @ `44ac957a` 18:52Z | Re-measured @ `08889ffc` 19:24Z |
| --- | --- | --- | --- |
| 1. Tracked | `git ls-files` | 20,688 | 20,690 |
| 2. Untracked, not ignored | `git ls-files --others --exclude-standard` | 2 | 4 |
| 3. **Gitignored** | `git ls-files --others --ignored --exclude-standard` | 37,256 | 37,246 |
| 4. **Outside the repo** | `command find /home/ubuntu/certonomous-runs -type f` | 132,049 | 132,049 |

Two columns, because one column would have taught you to quote it. Arm 2 doubled
and arm 3 lost ten files in thirty-two minutes without anyone doing anything
unusual. **Take your own reading — it is four lines:**

```bash
printf '%-28s %s\n' \
  "1 tracked"    "$(git ls-files | wc -l)" \
  "2 untracked"  "$(git ls-files --others --exclude-standard | wc -l)" \
  "3 gitignored" "$(git ls-files --others --ignored --exclude-standard | wc -l)" \
  "4 run tree"   "$(command find /home/ubuntu/certonomous-runs -type f | wc -l)"
```

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

**Budget for arm 4.** It is 132,049 files outside the repo and it is not a quick
command: run as written by the cold-read pass, arms 1–3 returned in seconds
(234 / 0 / 0 for that literal at 19:47Z) and **arm 4 had not finished at two
minutes** and was killed. If you are on a timeout, start arm 4 first or run it in
the background — and if you *skip* it, say in your record that you swept three
arms and not four. A sweep that quietly drops the largest arm is the shape §4
exists to prevent.

For that literal, arm 1 returned 231 files and the shell's `grep -rlI` returned
207 — and the 24-file difference is **not** the gitignored arm. It is 27 *tracked*
files that `.gitignore` patterns also match, minus 3 that git skips for a
different reason (next paragraph). The shell's grep misses tracked files too.

Re-measured at `08889ffc`, 19:25Z: 232 and 208, **difference still 24**, and
`git grep -lI --text` returns 235 — the same 3 files the `-I` arm drops for the
reason in the next section. Both absolute counts moved by one overnight-hour of
lab traffic; the two structural gaps, 24 and 3, did not.

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
`git grep -la` is the same thing in short form — verified identical, 237 files
each at 19:49Z — and `-a` is what most dispatch briefs in this lab write, so
recognise both.

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

Sizes, so you know what you are walking into. **Run these; do not read the
numbers below as current** — `docs/DOCKET.md` was 499 lines at `44ac957a` (18:52Z)
and 507 at `08889ffc` (19:26Z), which is the whole point of §0:

    $ command grep -c '^## L-' LESSONS.md            # numbered lessons
    84                                               # 84 again at 19:26Z
    $ command grep -oE '^## L-[0-9]+' LESSONS.md | tail -1
    ## L-84
    $ wc -l docs/charters/VERIFICATION_CHARTER.md docs/DOCKET.md
     1616 docs/charters/VERIFICATION_CHARTER.md      # 1616 again at 19:26Z
      499 docs/DOCKET.md                             #  507 at 19:26Z

`docs/charters/` holds **nine** `*_CHARTER.md` files plus `README.md`,
`SUPERVISOR_RULINGS.md` and two proposals — `ls docs/charters/*_CHARTER.md | wc -l`
is the count, and the rulings file is not a charter but binds like one.

---

## 6. Checking the lab's health in one command

    python3 scripts/lab_check.py --no-tests      # fast tier, ~3 min
    python3 scripts/lab_check.py                 # everything, ~20 min
    python3 scripts/lab_check.py --list          # enumerate, run nothing, seconds

I ran both. The fast tier took 188 s of measured wall time across 13 gates. The
full run took **1,221 s wall (20.4 min), 1,302 s user + 51 s system CPU**, adding
the suite: **1,830 tests in 75 files, 1 failed**. Both returned **FAIL, exit 1**.
Re-run three hours later on a busier box: **199 s** and **1,421 s (23.7 min)**,
**1,852 tests in 77 files**, both still **FAIL, exit 1** — details below. Treat
"~3 min / ~20 min" as a floor, not an estimate.

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

**Re-run by a second agent at `08889ffc`, 19:24Z — 3:19 wall, 182 s user + 9 s
system, exit 1.** Its frame block read `candidates 153 (tracked 150, on disk 153)`,
`admitted 91 (14 script gate(s), 77 test file(s))`, `skipped 62`, and carried a
line the earlier run did not print at all:

    untracked only     3 -- present here, will not travel:
                       scripts/check_summary_consistency.py,
                       sdk/tests/test_blind_spots_are_printed.py,
                       sdk/tests/test_empty_set_is_not_agreement.py

**Read that line before you trust a green.** Three of the gates that ran exist
only in this working tree. They are somebody's uncommitted work in flight, they
will not survive a clone, and a verdict that depends on them is a verdict about
this box. The four FAILs below were the same four in both runs.

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

**Re-run by the cold-read pass, 19:27:22Z–19:51:03Z, exit 1**, and every number in
that block moved inside three hours:

    test files enumerated 77        (was 75)
    test files collected  77        (was 75)
    tests collected       1852      (was 1830; failed 1, errored 0, skipped 0)
    __pycache__ purged    2 directories   (was 3)

    VERDICT: FAIL -- 15 check(s) ran, 62 not admitted, 6 unrun check(s) whose
                     skip reason could be hiding a verdict
    FAIL scripts/calibration_scorecard.py, check_absolutes.py,
         contention_audit.py, self_audit.py
    FAIL sdk/tests (pytest): 1 failed, 0 errored, out of 1852

Wall **23:40.76** against the 20.4 min above, on **1,312 s user + 57 s system** —
the run was slower while its own CPU time went *up*, because six other agents were
working the box. **The wall figure is not a property of `lab_check.py`.** If you
quote a runtime here, quote the load with it, per §7's *"a figure carries its
basis"*.

The one failure is `sdk/tests/test_exec_bits.py`, for the reason in §9.2
(re-run standalone by the cold-read pass: `1 failed, 14 passed in 1.61s`, the
failing case being `test_no_shebang_script_is_both_unexecutable_and_unregistered`).
Note also that the tracked cron file records this suite as **1,609 tests** measured
on 2026-08-14 — `scripts/installed/certonomous-lab-check.cron:29`, verified, and it
also says **69 files**; it collected **1,830** in **75 files** on 2026-08-15.
Neither number is wrong. That is what a count without a frame does, and it is why
every count in this document carries the moment it was taken.

### `__pycache__` purged 3 directories — that line is a gate, not housekeeping

The frame block above says *"stale bytecode has inverted results here"* in
parentheses. It is the most under-stated line in this document — it is
**`docs/DOCKET.md` D1**, the very first row of the rung-residual table, and the
real instance is worse than the phrase suggests: verifying V16's E3 recompute, an
equal-length source mutation plus a restore left a stale `.pyc`, and for three
consecutive runs *"the clean control **failed** and the mutated case **passed** — a
perfectly inverted mutation matrix, which a less suspicious reading would have
written up as 'the recompute is dead'."* D1's closing sentence is the one to
carry: *"until [a purging harness] exists, every mutation result in this lab is
only as good as whether its author happened to clear the cache."*

Reproduced from scratch by the cold-read pass, so you can see the shape without
reading the case:

    # pkg/rule.py, 56 bytes, correct:  return "PASS" if x > 10 else "FAIL"
    # test asserts verdict(5) == "FAIL"
    $ python3 -m pytest -q test_rule.py
    1 passed                                     # honest pass

    # now MUTATE it to a same-length source that must FAIL, and restore the mtime
    # pkg/rule.py, 56 bytes, broken:   return "PASS" if x > -1 else "FAIL"
    $ python3 -m pytest -q test_rule.py
    1 passed                                     # <-- THE MUTATION IS INVISIBLE

    $ python3 -c 'from pkg.rule import verdict; print(verdict(5))'
    FAIL                                         # the source says PASS. this is the .pyc.

    $ /usr/bin/find . -name __pycache__ -type d -exec rm -rf {} +
    $ python3 -m pytest -q test_rule.py
    1 failed                                     # the true verdict

**Read what that means before you read anything else on this page.** A test that
*passes* was the failure. The suite reported green over a source file it never
compiled. Every mutation test, every "I broke it and the gate caught it" control,
every negative control the verification charter §2a demands — all of them are
answered by the cache instead of by your change, and the answer is always "the
old behaviour", which is usually the passing one.

Two conditions have to line up, and both are ordinary here:

- **Same file size.** CPython validates a `.pyc` on the `(mtime, size)` pair, not
  a hash. A one-character edit that preserves length passes validation.
- **Unchanged mtime.** `git checkout`, `git stash pop`, a worktree materialising a
  file, or two writes inside one filesystem timestamp all produce this.

And the remedy people reach for **does not work**:

    $ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q test_rule.py
    1 passed                                     # still inverted

`PYTHONDONTWRITEBYTECODE` stops Python *writing* bytecode. It has never stopped it
**reading** bytecode that is already on disk. Measured, in the same scratch
package, immediately after the inverted run.

**The rule: purge, then measure. Every time, and in this order.**

    /usr/bin/find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null

`lab_check.py` does this for you and prints the count, which is why that line is
in the frame block. If you run `pytest` by hand — and §9.2's standalone re-run
above is exactly that case — **you are the one purging it.**

If you are mutating a source file to prove a gate can fail, purging between
*every cell* is not optional, and note that the damage takes two different shapes
depending on which state the cache is holding: the demonstration above gives you
**both cells the same verdict** (the mutation is simply invisible), while D1's
real instance gave a **fully inverted matrix** — clean control FAILED, mutated
case PASSED. The second is more dangerous because it looks like a result. D1's
requirement is therefore stronger than "purge first": a harness that *"clears
`__pycache__` between every cell and asserts the clean control and the mutated
case in the **same** run, so an inversion cannot look like a pass."* That harness
does not exist yet — D1 is open — so on any mutation work you are the harness.

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

One operational note: `lab_check.py` writes a zero-byte file for the whole run
and then everything at once.

> ~~`lab_check.py` buffers stdout when redirected. My first run wrote a zero-byte
> file for three minutes and then everything at once. Use `python3 -u` if you are
> watching a file.~~
>
> **[STRUCK 2026-08-15 by the cold-read pass — the remedy does not work, and the
> diagnosis was wrong. Original retained above per §7.]**
> This is not stdout buffering. `lab_check.py` accumulates its entire report into
> a list and emits it in a **single terminal `print("\n".join(lines))`**
> (`scripts/lab_check.py:1261` for `--list`, `:1357` for a real run). Measured:
> `python3 -u scripts/lab_check.py > full.out` left `full.out` at **0 bytes 2 min
> 12 s into a 20-minute run**. `-u` unbuffers the stream; it cannot make a program
> print something it has not printed yet. **There is no way to watch this run
> progress.** Budget the wall time, check `$?` at the end, and if you need
> progress, watch the pytest side-channel (`--junitxml`) instead of stdout.
>
> This matters beyond convenience, and is filed as docket **D148**: the box powers
> itself off on an idle timer (§2) and a usage limit can terminate every agent at
> once. An interruption at minute 19 of a 20-minute run yields **nothing at all** —
> not a partial report — and a zero-byte output file is indistinguishable from a
> run that never started, one that died, and one that is nineteen minutes healthy.
> **Hold the box before you start the full tier.**

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

> **Independently reproduced 2026-08-15 by the cold-read pass**, in a fresh
> scratch repository, both variants. Unbalanced: HEAD stayed at the baseline
> commit, `git status --short` still showed `M  a.txt` staged, nothing committed.
> Balanced: parent was `8cc8581`, the commit landed as `3a138fe`, and
> `git log -1 --format=%s` returned **`anchored at 8cc8581`** — the message names
> a commit that is not the commit it is on. `-F` with the same backticks recorded
> them literally.
>
> **And the unbalanced case is worse than "anything after it in the same
> invocation".** Run inside a script, bash fails at **parse** time on reaching
> EOF, so it aborts the **entire remaining file** — not just the rest of that
> command. Measured: a five-step script printed its first step, hit the
> unbalanced backtick, and never executed steps two through five. If you have a
> commit-then-verify script, the unbalanced backtick eats the verification too,
> which is precisely the check that would have told you.

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

#### What is actually happening, and the repair has a trap of its own

The cold-read pass reproduced the whole sequence above in a scratch repo and got
the **same four blob SHAs** (`4163036e`, `854c7ea1`, `ddd98c15`, `e197101e`), then
ran four controlled cases to find the mechanism. "Re-derives the mode from the
worktree" is nearly right, but the observable rule is sharper and more useful:

> **With `core.filemode=false`, a pathspec commit takes the mode from `HEAD`.**
> Not from the index, not from the worktree.

Measured, both directions:

| `HEAD` mode | index says (via `update-index`) | after `git commit -- run.sh` |
| --- | --- | --- |
| 100644 | 100755 | **100644** — the `+x` was discarded |
| 100755 | 100644 | **100755** — the `-x` was discarded |

So `git update-index --chmod` is **completely inert** under this lab's mandated
commit form, in both directions. That is the whole of D134: under a pathspec
commit the mode cannot be set *or cleared*, so the waiver register can only grow.

**The trap inside the repair.** The recipe above passes `-c core.fileMode=true` to
both `add` and `commit`. Only one of those is load-bearing, and it is not the
obvious one:

| where `-c core.fileMode=true` was passed | index after add | `ls-tree HEAD` |
| --- | --- | --- |
| on the **commit** only | 100644 | **100755** ✅ |
| on the **add** only | 100755 | **100644** ❌ |

Putting it on the `add` alone is the natural economy — you can *see* the index go
to 100755 — and it silently produces 100644 in the tree. **The `-c` belongs on the
commit, and the worktree file must carry the bit.** The working form:

    chmod +x <file>
    git -c core.fileMode=true commit -F <msgfile> -- <file>
    git ls-tree HEAD <file>          # <-- the verification. 100755 or you failed.

One more measurement, recorded because it is uncomfortable rather than because it
is useful: a **bare** `git commit` with 100755 in the index *does* preserve the
bit. The form that works is the form the charter forbids (`ESCALATION_CHARTER.md`
§9.6). Do not take that as a licence — take it as the reason this trap exists here
and not in most repositories.

*Both tables above are filed as docket **D147**, because D134 offered the chief
three repairs and the per-invocation `-c` is a fourth one it did not consider —
it needs neither a protocol amendment nor a repo-wide config flip. Whether that
form is protocol-conforming is the chief's call, not this document's; until it is
ruled on, treat §9.2's working form as **what git does**, not as what you are
permitted to do.*

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

> **[AMENDED 2026-08-16 at `29fd7030`. Nothing above is struck — it is still the
> rule for a shared file in general.]** For `docs/DOCKET.md` specifically there
> IS now a safe granularity, and "carry the peer's row and name it" is no longer
> the best available option: **§11b item 8** gives a private-index form that
> commits the PARENT's blob plus only your own rows, selected by row ID and never
> copied from the worktree, landed with a mandatory compare-and-swap. Measured at
> `e4c1319e`, a pathspec commit of the docket would have carried 2 foreign rows.
> Use item 8 on the docket; use the paragraph above everywhere else.

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

One more reason the single-step form is the right one here, observed while
committing this document:

    $ git add docs/USING_THIS_LAB.md
    fatal: Unable to create '.git/index.lock': File exists.
    $ git commit -F <msgfile> -- docs/USING_THIS_LAB.md
    [main 5e8a4e1d] ...  1 file changed, 2 insertions(+), 1 deletion(-)

The `git add` lost a race for the index lock against another session. The
pathspec commit succeeded anyway, because `git commit -- <paths>` takes those
paths from the **worktree** and does not need them staged first. So `git add` is
a convenience here, not a prerequisite — but check the commit's file count and
diffstat, because a form that works without staging also works when you did not
mean it to.

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

> **The `pgrep -x` half of that advice has a limit the cold-read pass hit on the
> first try.** `-x` matches the kernel's `comm`, which is capped at 15 characters:
>
>     $ pgrep -x "zzz_unique_marker_pattern" ; echo exit=$?
>     pgrep: pattern that searches for process name longer than 15 characters
>     will result in zero matches
>     exit=1
>
> It warns here, which is lucky — but it *returns 1*, and a script reading only
> the exit status sees "no such process" and carries on. For anything longer than
> 15 characters, `-x` is not available.
>
> **Subtracting `$$` is not enough either.** Measured — two PIDs match, and only
> one of them is `$$`:
>
>     $ bash -c 'PAT=zzz_unique_marker_pattern
>                pgrep -f "$PAT"                          # 961617  961637
>                pgrep -f "$PAT" | command grep -vx "$$"' # 961617  <-- still there
>
> The survivor is the **parent** shell, which also carries the pattern on its
> command line. So: `pgrep -f "$PAT" | command grep -vxe "$$" -e "$PPID"`, and for
> the killing case never `pkill -f` at all — resolve to a PID list, drop your own
> and your parent's, print what remains, and only then kill it.

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
highest `D134` (working tree only). By 19:05Z the highest was `D138`. By 19:26Z,
a second agent measured **179 rows in both frames, highest `D142`** — nine rows
and eight IDs in twenty-eight minutes. **Nothing on this page is a usable ID.**
Re-measure immediately before you allocate, and **guard the write**:

> ### ⚠ The recipe that was printed here returned the wrong answer. Struck.
>
> The original text, retained per §7's strike-and-keep rule and **not to be run**:
>
>     git show HEAD:docs/DOCKET.md | command grep -oE '^\| \*{0,2}[A-G][0-9]+' | sort -u
>     command grep -oE '^\| \*{0,2}[A-G][0-9]+' docs/DOCKET.md | sort -u
>
> **[STRUCK 2026-08-15 by the cold-read acceptance pass, measured, not reasoned.]**
> `sort -u` on `| D<n>` sorts **lexically**, so `D99` sorts after `D146`. Run as
> written at 19:41Z, when the true highest was **`D146`**, the last `D` line it
> printed was:
>
>     $ command grep -oE '^\| \*{0,2}[A-G][0-9]+' docs/DOCKET.md | sort -u | command grep '| D' | tail -1
>     | D99
>
> — and the very last line of the whole output is `| G5`, which is not a `D` at
> all. **A newcomer following this section literally allocates `D100`**, an ID
> taken weeks ago, and collides silently with an existing row instead of the
> concurrent writer the section is warning them about. This is the document's own
> signature defect class committed inside the section written to prevent it, and
> it is why §8's rule is *"a check written with the same helpers as the thing it
> checks proves only that a number was transcribed faithfully."* §10 step 6 shows
> the author's real command elided as `| ...`; the elision is where the working
> part went.

**The recipe that works — the sort must be numeric, on the number alone:**

```bash
# highest D in HEAD, and in the working tree; they can differ
git show HEAD:docs/DOCKET.md \
  | command grep -oE '^\| \*{0,2}D[0-9]+' | command grep -oE '[0-9]+' | sort -n | tail -1
command grep -oE '^\| \*{0,2}D[0-9]+' docs/DOCKET.md \
  | command grep -oE '[0-9]+' | sort -n | tail -1
```

Measured 19:41Z: `146` in both frames. Twenty minutes earlier it was `142`.

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

## 11a. How work actually gets dispatched here

*[Added 2026-08-15 by the cold-read acceptance pass. The original draft was
written against a brief that did not cover this, and a newcomer could follow the
whole of §§0–14 without ever learning that they are not supposed to do the work
themselves. Numbered `11a` rather than renumbered in, because this document is
cited by section number and §7's own rule about reference targets applies to it.]*

**First establish which of you you are.** This lab has two shapes of agent and
they have opposite duties, so a newcomer who guesses wrong will either do work
that was not theirs to do or supervise work nobody did:

- **A working agent** executes one brief, in its own lane, and reports. It does
  not dispatch, does not grade its own output, and does not settle questions on
  the chief's retained list — it escalates them.
- **A supervisor** (family or chief) **does not run the family's solves, write its
  GUI, or fetch its papers.** It issues guidelines, performs four checks
  personally, and dispatches. If you find yourself doing the work you dispatched,
  you have collapsed the two roles and the independence rules below no longer
  hold.

Your dispatch brief tells you which you are. If it does not, that is a defect in
the brief and worth saying so before you start.

`SUPERVISION_CHARTER.md` §1, the line the whole model hangs on:

> **Every big task family has a standing supervisor, and four kinds of check are
> done by a supervisor personally or they have not been done.**

And the test it gives, which is worth reading twice because it is aimed at the
most natural thing an agent does: *"for any measurement-script change, crash, big
claim or compute launch in the last week, name the supervisor who checked it and
the record of the check. **'An agent reported it clean' is not an answer to that
question. It is the thing the question exists to catch.**"*

**The four families** (§2), each with a standing supervisor agent; the list is the
owner's:

| family | scope |
| --- | --- |
| DAFoam and adjoint | gradient ladders, FD verification, defect arcs, mesh warping — anything whose product is a derivative |
| Closure and UQ | the closure challenge, field inversion, model-form studies, the three uncertainty channels |
| Cases and campaigns | case families, refinement ladders, campaign records, the gate table |
| Infrastructure and standards | the harness, monitors, audits, standards documents, the fleet's own operations |

A family supervisor **issues guidelines, personally performs the four checks, and
reports to the chief** — in that priority order. It *"does not run the family's
solves, write its GUI, or fetch its papers; those go to the family's working
agents."* The four personal checks (§3), which may **not** be delegated downward:

1. **Code diffs on measurement scripts.** *"An instrument change without a
   supervisor's read is an uncalibrated instrument."*
2. **Crash triage — a crash is guilty until shown to be a mere bug.** *"A crash
   written off without triage is a discarded measurement."*
3. **Big-claim verification before belief** — a code sweep *and* an independent
   diagnostic; *"the claim is assumed wrong until it has been defended against its
   own evidence."*
4. **Pre-registration presence before compute.** The supervisor checks *"the
   commit exists, not that somebody meant to write one."*

**Retained by the chief and not delegable** (§4): scoring-call authorization,
cross-family arbitration, negative-verdict reviews on every FAIL / NO-GO / refuted
prediction, custody of the daily list and research board, and everything the
2026-07-26 delegation doctrine already assigns — research direction, trust
verifications, new models, dispatch, synthesis.

### Independence is a dispatch property, and it is not free

Ladder V's **R-ISOLATE** (Katie, 2026-08-11, in
`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:265`) turns on a
**non-author** measuring a rung. Its opening sentence is the lesson: the rule had
been enforced by *"everyone being careful"*, and *"that is not enforcement …
independence that depends on care fails the first time two agents pick the same
filename"* (L-77, `LESSONS.md:3220` — an author overwrote a grader's held-out
evidence and nobody broke a rule).

R-ISOLATE has **four parts, all mechanical**. Only part 1 is summarised here,
because it is the one that fails silently and the one a dispatcher gets wrong
first; **go and read the other three at the line cited above before you dispatch a
grader.**

**Part 1 is worktree isolation, and it has a caveat that is bigger than the rule:**

> **A fresh worktree does not carry gitignored files.** An agent isolated into a
> worktree to audit *text or code* is correctly isolated. An agent isolated into a
> worktree to audit **evidence** is looking at a checkout where that evidence does
> not exist, and *"it will report an honest, confident, empty result — the
> fail-open shape, produced by the very mechanism adopted to make verification
> trustworthy."*

That is §4 arm 3 and §3's `ugrep` problem arriving by a third route. The rule:

- Subject is **tracked content** → worktree-isolate.
- Subject is **run output, solver logs, or any gitignored tree** (§4 arms 3 and 4)
  → work in the **main checkout**, with exclusive scratch paths assigned by the
  dispatcher.
- Unsure → *"have it print the count of evidence files it can see **before** it
  reports what it found in them."*

**And a worktree can be cut behind its own subject.** Docket **D19**: the first
agent ever dispatched under R-ISOLATE got a worktree **18 commits behind**, with
the entire author round it was sent to grade absent from the checkout. Same
fail-open shape. The repair, and it is two lines in a brief:

    # dispatcher: state the subject SHA in the brief
    # agent, before executing anything:
    git merge-base --is-ancestor <subject-sha> HEAD || echo "WRONG TREE — STOP"

### What git can and cannot tell you about who did what

Do not try to establish independence from `git log`. **Every commit on this box
carries one identity** — `Ubuntu <ubuntu@ip-172-31-43-247…>` — because there is no
`user.name`/`user.email` anywhere and git synthesises it from the unix user and
hostname (`docs/AGENT_ATTRIBUTION.md`, measured: 1,217 commits since 2026-08-01,
**one** author identity). The author field cannot discriminate between two agents.

There is a mechanism, and its adoption cost is one line appended before
committing, with a fresh token you TYPE into the command yourself:

    $ python3 scripts/check_rung_attribution.py --emit-trailer --probe <a-typed-token> >> <msgfile>
    Lab-Agent: ip-172-31-43-247/64b13819-ff95-4d4d-a50f-3720bab19084/-/agent-a51eee0d63411897c

**[CORRECTED at `d91b101a` (D230's staleness sweep). The block below said the
bare `--emit-trailer` form was the adoption line, and it was written when that
was the only form there was.]** ~~`--emit-trailer` alone, and the trailer
separates chief sessions but not siblings, so for sibling agents independence
still rests on the untracked dispatch record and not on anything in the
repository.~~ That was true until `62d5757e`, which added the fourth
`agent-<hex>` field, and the published adoption line was corrected to the
`--probe` form at `9416db99`. **Bare `--emit-trailer` still emits the SESSION
form**, which is byte-identical for every agent of one chief and therefore grades
AUTHOR for every sibling pairing — so quoting it buys adoption cost and changes
nothing. The script still says, in capitals, at `scripts/check_rung_attribution.py:90`:

    TWO AGENTS DISPATCHED BY THE SAME CHIEF SESSION READ AS THE SAME AGENT.

That sentence is about the SESSION field, and it is why `--probe` exists. The
probe's token must be typed rather than shell-substituted: the harness records
the tool call as you wrote it, and the emitter finds your own subagent transcript
under `~/.claude/projects/<project>/<session>/subagents/` by searching those
records for the token. A token whose value never reaches the record resolves to
nothing, and the emitter then **prints nothing and exits 3** rather than falling
back to the session line. Measured at `d91b101a`: `--probe "D230CTL$(od -An -N8
-tx1 /dev/urandom | tr -d ' ')"` exited 3 and emitted nothing; a typed token
resolved to exactly one file. Note what actually decides it — a `$(echo <literal>)`
probe RESOLVES, because the literal is in the recorded call. Typing the token is a
rule that is always safe, not a description of the mechanism.

**The condition, stated exactly, because this document publishes the rule:** the
token's **VALUE must be present in the tool call as the harness recorded it.** An
unpredictable substitution fails not because it contains `$(...)` but because the
shell expands it *before* the harness writes the call down, so the value the
emitter searches for was never recorded. Both directions were re-executed at
HEAD `42f3e7b4` and again at `fe54ec0a`, same results both times, exit codes
captured as `cmd > out 2>&1; rc=$?` and never through a pipe, since a pipe
replaces the status:

    $ python3 scripts/check_rung_attribution.py --emit-trailer \
        --probe "D240CTL$(od -An -N8 -tx1 /dev/urandom | tr -d ' ')"
    rc=3, no trailer — ~620 bytes of refusal text naming the probe
    $ python3 scripts/check_rung_attribution.py --emit-trailer \
        --probe "$(echo D240ECHOLITERAL8WQ)"
    rc=0, agent form emitted: .../-/agent-a2abe5ddb4adedc53

**And check the exit code, not the message file** — a sentence written here from
reasoning and then corrected by executing it. The refusal goes to **stderr**, and
stdout is empty: split-stream measured at `fe54ec0a`, **stdout 0 bytes, stderr
621**. So the adoption line's `>> <msgfile>` redirect appends **nothing at all**
on a failed probe, silently, and the commit lands with no identity while looking
exactly like a commit whose emitter ran fine. `rc=$?` is the only thing that tells
you which happened.

The second one is a `$(...)` that RESOLVES. So *"type the token"* is a
**sufficient** rule, and the whole of what it is doing is guaranteeing the value
reaches the record. The bare form was re-executed in the same pass and still
emitted the session line, `.../-` with no fourth field, rc=0 — which grades AUTHOR
for every sibling pairing, so quoting it costs adoption effort and buys nothing.

Two limits survive the repair. **The chief session itself cannot probe**, having
no per-subagent transcript of its own. And nothing before the anchor `e933e31b`
is attributable — *"backfill is impossible"*. The `--tag` slug is recorded,
printed, and **never decides a verdict**.

#### A per-agent handle is a DIFFERENCE, not independence — and a green run is not admissible as one

*[Added 2026-08-16 to close a gap this guide was measured to have: before this
paragraph the word `fork` appeared in it **zero** times, so a dispatcher could
follow §11a end to end and construct a grader that passes the attribution check
while being contextually the same reader.]*

Chief ruling, `docs/DOCKET.md` **D240** (`29fd7030`). The instrument was shown to
return the negative for the first time, at commit-pair `01e94313`/`62d5757e` —
re-executed at HEAD `4a923413` by an agent that wrote neither commit, returning
`VERDICT: NON-AUTHOR`, `GRANULARITY: agent`, exit 0, over a frame reading
`1 session, 2 per-agent, over 2 commits`. That closed the objection that it could
not discriminate. It did **not** turn a green run into an independence warrant,
and **no ladder rung may cite one as its warrant.** Three measured reasons:

- **The verdict is asymmetric.** `NON-AUTHOR` is informative; `AUTHOR` is what
  almost every pair returns out of **absence of data**, for reasons that have
  nothing to do with who did the work. Measured at `4a923413`: 6 of the 108
  commits since anchor `e933e31b` carried a per-agent handle, so **15 of the 5,778
  commit pairs — 0.26% — could be asked the agent-granularity question at all.**
  The other 99.74% answer `AUTHOR`, or answer at session granularity, because one
  side or both carried no handle.

- **A `fork` subagent defeats the measure by construction, and this is the trap
  the dispatcher walks into.** A fork inherits its parent's **entire
  conversation** — it has read everything the parent read — and it still carries
  its own `agent-<hex>`, so it grades `NON-AUTHOR`.
  `docs/AGENT_ATTRIBUTION.md:198-201`: *"a different agent by this measure, having
  read everything the parent read. R-ISOLATE's spirit is not satisfied by
  dispatching a fork, and the check cannot see the difference."* The tool prints
  the same caveat on **every** run, in its `FORGEABILITY` line, verbatim:
  *"a `fork` subagent inherits its parent's whole context and is still a different
  agent here."* **So when you need a grader that has not read the author's
  reasoning, dispatch a FRESH agent, not a fork.** Nothing in the trailer, in the
  transcripts, or in the tree records dispatch KIND, so no later reader can
  recover which one you dispatched — the choice is unauditable after the fact,
  which is why it has to be made correctly at dispatch time.

- **Existence is unverifiable from a clone, permanently.** The handles resolve
  from harness transcripts under `~/.claude/projects/<slug>/<session>/subagents/`,
  and that root is **not inside this repository**. Measured 2026-08-16 at
  `4a923413`: a fresh `git clone` of this repo contained **no `subagents`
  directory and no `agent-<hex>.jsonl`**, and `--emit-trailer --probe <typed
  token> --transcripts <clone>` exited **3**. A *verdict* still reproduced from
  inside that clone, because a verdict reads commit trailers — so the mechanism
  makes **DIFFERENCE** checkable and leaves **EXISTENCE** unverifiable. And it
  reaches nothing before the anchor: 1,858 commits up to and including
  `e933e31b`, exactly **one** of which carries a trailer (the anchor itself).

There is also a whole half of R-ISOLATE the check cannot see at all: the rule
requires a grader to **EXECUTE** the claim rather than read the author's summary
of it, and a grader that read a summary and a grader that ran the code commit
identical bytes. So rung-level independence continued to rest on the **untracked
dispatch record**, exactly as the rest of §11a says, and the attribution run is
one of two necessary conditions rather than a warrant. What would change that:
adoption reaching the point where a representative sample of grader/graded pairs
carries a probed four-field trailer on **both** sides. The distance, at
`4a923413`: 9 of 108 commits since the anchor carried any identity, 6 a per-agent
handle, across three distinct handles.

---

## 11b. When agents collide — which is constantly

Ten agents write this tree. Collisions are the normal case, not the incident, and
every mechanism below exists because one already happened.

**1. Claim the item before you dispatch it.** `docs/DOCKET.md` §B carries a live
dispatch-claim block, and the instruction is in the file's own words: *"CLAIM AN
ITEM BEFORE YOU DISPATCH IT — write your session into the Status column first."*
Added 2026-08-11 after two chief sessions independently dispatched *the same four
briefs* off the same directive. The B1 collision is the proof: two agents ran the
identical sweep brief and one's `Write` landed on the other's already-committed
`docs/SWEEP_REFRAME_AUDIT.md`, **replacing a 335-line document with a 281-line one
and dropping two sections**. It survived only because that agent went looking.
*"The failure is the dispatcher's, not the agent's … one edit before dispatch
makes the collision visible while it is still cheap — the agents do not exist
yet."*

**2. Do not leave a shared file dirty "to be polite".** §9.3 tells you a pathspec
commit sweeps in whatever anyone else left uncommitted in that file. The
considerate response — leave it for them — was tried, and it failed in the other
direction: `ESCALATION_CHARTER.md` §9.6c, *"leaving a shared file dirty does not
protect your work. It hands the decision to whoever commits next"*, which on this
tree is a matter of seconds. **On a shared tree, inaction is not neutral.**

**3. The procedure §9.3 does not give you.** §9.6c carries one, and it is short:

```bash
git diff --cached --name-only        # MUST be empty before you start. Check it.
git diff <path> > /tmp/full.patch    # everything currently uncommitted
# split the patch and keep only the hunks you wrote — do not eyeball it
git apply --cached /tmp/mine.patch   # stage YOUR hunks only
git diff --cached --stat             # confirm what is staged
git diff --cached | command grep -c '<their marker>'   # confirm theirs is NOT
git commit -F <msgfile>              # the index holds only your hunks
```

Two notes that make this safe rather than clever, both from the charter: that
final `git commit` has **no pathspec**, normally forbidden — *"it is safe only
because the index was empty and you put exactly your own hunks in it. Check that,
do not assume it."* And **say in the commit message that you did this and why**.

**4. Never revert what you did not change.** `ESCALATION_CHARTER.md` §3 forbids
`git reset --hard`, `git stash`, `git checkout -- <path>` and `git clean` on this
tree: *"An unexpected uncommitted change is inspected, never reverted."*

> **The two sources disagree here, and a newcomer should see the disagreement
> rather than a smoothed version of it.** The docket's own account of the B1
> collision says the surviving agent *"restored it with `git checkout --`"* — the
> exact command §3 forbids. Both readings are defensible: §3 protects a *live*
> uncommitted change from being destroyed, whereas B1 was a restore *to* a
> committed state after a `Write` had already destroyed one. My reading is that §3
> governs and the B1 restore was an exception justified after the fact by having
> compared both versions first, which is the part that actually made it safe.
> **I am not the one who gets to settle that.** If you are about to run
> `git checkout --` on this tree, treat it as escalation-worthy and say in your
> record what you compared before you ran it.

**5. Assume your reads are stale.** `git status` has been observed reporting a
dirty file as clean while other sessions committed (§9.3). Diff against content —
`git show HEAD:<path> | diff - <path>` — not against a summary. Re-read the
highest docket ID *immediately* before you write, not when you started thinking
about it: §10 step 6 lost that race by ninety seconds, and §11's own figures moved
by eight IDs in twenty-eight minutes.

**6. Expect to lose the index lock, and know that it does not stop you.** §9.3
records `git add` failing with `Unable to create '.git/index.lock'` while the
following pathspec commit succeeded anyway. Retry the `add`, or skip it — but read
the diffstat, because a form that commits without staging also commits when you did
not mean it to.

**7. The session scratchpad is SHARED, and a peer will overwrite your files under
you.** *[Added 2026-08-16, measured while landing `29fd7030`.]* A commit message
written to `<scratchpad>/msg.txt` was **replaced wholesale by another agent's
message** in the interval between the `Write` and the commit. It was caught only
because the identity trailer had already been appended to the file, so a `tail` of
it showed my own `Lab-Agent:` line sitting under a peer's prose — **a peer's text
would otherwise have landed under my handle, with my trailer attesting it.** A
listing of that directory at the time showed 120 entries written by many agents,
including six differently-named copies of the docket. The protocol, and it applies
to **every round-tripped intermediate file, not just commit messages**:

- Work in a **per-agent subdirectory** — `<scratchpad>/<task>-<your agent-hex>/`,
  the hex being the one `--emit-trailer --probe` resolves for you — never in the
  scratchpad root.
- **Byte-verify immediately before the file is consumed, not when you wrote it.**
  Before `commit-tree`, re-read the message and re-check the staging blob; after
  landing, compare content rather than a summary (item 5). The D240 row was
  compared byte-for-byte against its staged copy after `29fd7030` landed, and the
  message file was rewritten under a private path and re-read before use.
- **Why it matters far beyond commit messages:** a peer overwriting a
  planted-control readback converts a **broken sweep into a clean bill of
  health**. §10 step 3 and docket D239 both turn on a positive control having
  actually fired; a control you re-read from a shared path is a control you have
  not run. Same fail-open shape as the worktree-isolation caveat in §11a — an
  honest, confident, empty result.

**8. On `docs/DOCKET.md` the pathspec form is unsafe whenever a peer holds a row,
and its replacement is a private index plus a compare-and-swap.** §9.3 tells you a
pathspec isolates by file and not by author; the sharper statement is the
mechanism — `git commit -- <path>` takes the file from the **WORKING TREE**, so it
commits every foreign row sitting in it. Measured at `e4c1319e`: `git diff HEAD --
docs/DOCKET.md` showed **2 added lines, both of them foreign rows (D236, D237)**,
so a pathspec commit at that moment would have landed two other agents' work under
my message. The standing form instead, executed for D221 and again at `01e94313`,
`16bc2f7f` and `29fd7030`:

```bash
EXPECTED_OLD=$(git rev-parse HEAD)          # read ONCE; this is the CAS token
# Rebuild the blob as the PARENT's docket plus ONLY your own rows, selected by
# row ID. Never copy the worktree file — that is the capture you are avoiding.
git show $EXPECTED_OLD:docs/DOCKET.md > $D/new.md && cat $D/myrow.txt >> $D/new.md
BLOB=$(git hash-object -w $D/new.md)
export GIT_INDEX_FILE=$D/index && rm -f $GIT_INDEX_FILE   # the SHARED index holds
git read-tree $EXPECTED_OLD                               # other agents' staged files
git update-index --cacheinfo 100644,$BLOB,docs/DOCKET.md
TREE=$(git write-tree)
NEW=$(git commit-tree $TREE -p $EXPECTED_OLD -F $D/msg.txt)
unset GIT_INDEX_FILE
git update-ref refs/heads/main $NEW $EXPECTED_OLD          # MANDATORY, never optional
# AND THEN, once the CAS has succeeded — this step is part of the protocol:
# write your row into the WORKTREE copy too, inserted in numeric order by ID.
# The form above never touched the worktree file, so without this the two diverge.
```

**Why the compare-and-swap is not optional, stated plainly because its failure is
worse than the one the private index prevents.** The commit was built with
`$EXPECTED_OLD` as its only parent. If HEAD moved while you were building it, a
plain `git update-ref refs/heads/main $NEW` makes your commit **REVERT the
intervening one** — deleting a peer's work outright, silently, with a clean
diffstat. Capture publishes a peer's work under the wrong message; a lost race
**destroys** it, so the failure the CAS prevents is strictly the worse of the two.
The CAS refuses instead, and refuses loudly. Measured at `e4c1319e` against a real
stale sha, exit status captured directly:

    $ git update-ref refs/heads/main $H $(git rev-parse HEAD~3) ; echo "exit=$?"
    fatal: update_ref failed for ref 'refs/heads/main': cannot lock ref
    'refs/heads/main': is at e4c1319e... but expected f3c27a0c...
    exit=128

`f3c27a0c` in that message is the parent `29fd7030` was actually built on, about
twenty minutes earlier; HEAD had moved three commits in the interval. On this tree
that is the normal case and not the incident, which is the whole argument for the
CAS. Declare the row count with `python3 scripts/hunk_check.py docs/DOCKET.md:<n>`
and verify the landed commit with its `--at <sha>` mode — the worktree mode will
read high, because it sees the foreign rows too.

**The write-back is not an afterthought, and the protocol is incomplete without
it.** *[Added 2026-08-16 after the incompleteness was measured, not predicted.]*
The form above rebuilds the blob from **HEAD's** docket and commits it directly;
it never writes the row back into the working copy. So **every private-index
commit widens the gap between HEAD and the worktree**, monotonically, and nothing
in the repository reports it. Measured at `5a0127d3`: HEAD's docket held **244**
rows and the worktree copy held **243**, the missing one being **D241**, landed by
private index and never written back.

Why it had not bitten yet: a *conforming* agent rebuilds from HEAD's blob, so it
picks up every row it does not have and cannot drop one. Why it will bite: any
agent that edits the worktree copy and commits it **by pathspec** — the form still
mandated for every other file, and the one an agent reaches for by habit —
silently reverts every private-index row landed since the worktree last matched
HEAD. The gap is invisible in `git log` and grows with each conforming commit.

**So run the reconciliation check before you edit `docs/DOCKET.md` at all.** It is
two commands and a `diff`, and `command grep` is required because the interactive
`grep` on this box is a shell function wrapping `ugrep` (§3) — verified to run as
written at `5a0127d3`:

```bash
git show HEAD:docs/DOCKET.md \
  | command grep -oE '^\| \*{0,2}[A-G][0-9]+[a-z]?' \
  | command grep -oE '[A-G][0-9]+[a-z]?' | sort > /tmp/head.ids
command grep -oE '^\| \*{0,2}[A-G][0-9]+[a-z]?' docs/DOCKET.md \
  | command grep -oE '[A-G][0-9]+[a-z]?' | sort > /tmp/wt.ids
diff /tmp/head.ids /tmp/wt.ids && echo "RECONCILED"
```

Read the output by direction, and the two directions mean opposite things:

- **`< D<n>` — in HEAD, not in the worktree.** A row landed by private index and
  never written back. **HEAD wins.** Restore it into the worktree by **inserting
  it in numeric order by ID**. This is a worktree edit only; it is already
  committed and must not be committed again.
- **`> D<n>` — in the worktree, not in HEAD.** That is **unlanded work**, and it
  is somebody's finding living in no commit (see the orphaned-rows paragraph
  below). **Land it by ID through the form above** — never by copying the
  worktree file into a commit, which is the capture this whole item exists to
  prevent, and never by `git checkout -- docs/DOCKET.md`, which item 4 forbids and
  which would destroy it outright.

Run at `5a0127d3` it printed `< D241`; after inserting D241 in numeric order the
same commands printed nothing and `diff` exited 0, at **278 rows in both frames**
counting every lettered section. The insertion was done by a script that asserted
every pre-existing worktree line survived in order — a restore that silently drops
a peer's uncommitted row is the failure it is supposed to prevent.

> **One trap in verifying this, measured at the same time.** `git diff -- <path>`
> compares the worktree against the **INDEX**, not against HEAD, and the shared
> index on this tree may hold another agent's stale blob (item 9). Immediately
> after the reconciliation, `git diff --stat -- docs/DOCKET.md` reported **8
> insertions and 2 deletions** on a file that was byte-identical to HEAD, because
> it was measuring against a poisoned index entry. `git diff --stat HEAD --
> docs/DOCKET.md` printed nothing, correctly. **Compare against `HEAD`
> explicitly, or against `git show HEAD:<path>` — never against a bare
> `git diff`.** §9.3's `git diff -- <path>` line has the same exposure.

**And record the by-product, because somebody owns it.** An agent that declines to
commit rather than capture leaves **ORPHANED ROWS**: text that lives in the
worktree and in no commit, invisible to `git log`, and destroyed outright by any
of the reverting commands item 4 forbids. D236 and D237 sat orphaned across at
least four commits (`4a923413` at 16:59:52Z through `e4c1319e`); D238 and D239 had
been orphaned before them and were landed only because an agent was dispatched to
do it (`4a923413`). **So the protocol has a second half: whoever leaves foreign
rows uncommitted must SAY SO in their commit message, and somebody must be
dispatched to land them.** Leaving them and saying nothing is item 2's failure
arriving by a different route.

**9. The shared index is a loaded gun, and `git commit` with NO pathspec fires
it.** *[Added 2026-08-16, measured — this was found while committing the section
above, not reasoned about.]* There is **one** `.git/index` and every agent's
`git add` writes to it. At `fe54ec0a`, `git diff --cached --stat` read:

    docs/AGENT_ATTRIBUTION.md              |  11 --
    docs/DOCKET.md                         |  10 +-
    docs/USING_THIS_LAB.md                 |  49 +++------
    scripts/self_audit.py                  | 117 +++------
    sdk/tests/test_rank_claim_surfaces.py  |  67 ------
    sdk/tests/test_rank_claim_values.py    | 189 ++---------
    6 files changed, 41 insertions(+), 402 deletions(-)

None of it was mine, and it was **stale against HEAD in the reverting direction**.
`git show :docs/USING_THIS_LAB.md` returned a 1,559-line blob containing `--probe`
**zero** times — a pre-`9416db99` snapshot of §11a, which if committed would have
republished the corrected-and-struck adoption line as live text and re-broken the
citation to `scripts/check_rung_attribution.py:90` as `:92`. `git show
:docs/DOCKET.md` did not contain **D240**, so committing the index would have
**deleted a landed docket row**. A bare `git commit` by anybody, for any reason,
would have reverted 402 lines across six files with a clean-looking diffstat and a
message about something else entirely.

- **Never run `git commit` without a pathspec on this tree**, and check
  `git diff --cached --stat` before any commit form at all — `hunk_check.py` now
  reports staged-and-undeclared paths for exactly this reason, and it reported
  these.
- **Do not "clean up" the index either.** Those blobs are other agents' in-flight
  work, and item 4 plus `ESCALATION_CHARTER.md` §3 govern: inspected, never
  reverted. Report it; do not `git reset`.
- **The private-index form of item 8 is immune to all of this**, and that is a
  second reason to prefer it over a pathspec commit even for an ordinary file: it
  builds from `git read-tree $EXPECTED_OLD` in a `GIT_INDEX_FILE` of its own, so
  the shared index is neither read nor written, nothing rides along, and nobody
  else's staged work is destroyed. This section was committed that way.

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

Stated rather than omitted, per §8.2: a thing not checked is UNKNOWN, and UNKNOWN
does not get filed beside the passes.

- **Nothing about `lab_check.py` is second-hand** — both tiers were run here
  (188 s and 1,221 s, both exit 1). But note that the full run happened on a box
  that had other agents' work on it at the same time, so the CPU figure is a
  measurement of this box under load, not a clean benchmark. *[Confirmed twice
  over by the cold-read pass: an independent pair of runs three hours later gave
  199 s and 1,421 s, both exit 1, with **more** CPU (1,312 s user vs 1,302 s) in
  **more** wall time. Neither pass has a clean-box number and neither can get one
  while the fleet is working.]*
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

### Added 2026-08-15 by the cold-read acceptance pass

The list above is honest about what it did not *measure*. It has a blind spot of
its own, and it is a single shape:

> **This document executed its demonstrations. It did not always execute its
> remedies.** Every trap in §9 was reproduced. Several of the fixes offered
> alongside them were not run before they were printed — in a document whose
> subject is failures that look like successes.

Four instances, all found by running them. **The first is the serious one:**

- **§11's ID-collision recipe returned `D99` when the highest was `D146`.**
  `sort -u` is lexical. Following §11 literally, a newcomer allocates `D100` — an
  ID taken weeks ago — and collides *silently*, with an existing row rather than
  with the concurrent writer the section is about. The section written to prevent
  ID collisions was the one that caused them. Struck in place at §11 with a
  numeric-sort replacement, measured in both frames.
- **§6's `python3 -u`** — printed as the remedy for a zero-byte output file. It
  cannot work: `lab_check.py` emits its whole report in one terminal `print`.
  Struck in place at §6 with the source line cited.
- **§9.4's `pgrep -x`** — printed as the remedy for the self-match. It refuses any
  pattern over 15 characters and **returns exit 1**, which reads as "no such
  process". Caveat and a working form added at §9.4.
- **§9.2's `-c core.fileMode=true`** — the demonstration is correct and reproduces
  to the blob SHA, but it was only ever run with the flag on *both* `add` and
  `commit`. Passing it to the `add` alone — the natural economy — silently yields
  100644. Measured and added at §9.2.

Still unverified after this pass, and now marked rather than implied:

- **That the installed gate's blindness has ever actually let the box power off
  mid-session.** §2's mechanism is now verified by reading
  `/usr/local/bin/auto-stop.sh` directly. Whether it has fired is a history
  question and this is not the instrument for it.
- **§3's "root's cron gets the real GNU tools."** Not tested by running root's
  cron. The supporting evidence is indirect but real: `journalctl -t auto-stop`
  carries `ALIVE: Claude session transcript written within 30min (<path>)`, which
  is the `-newermt` clause returning a hit, and cron does not source the
  interactive profile where `find` is redefined. Treat as strongly supported
  inference, not measurement.
- **Everything in §1's headline paragraph.** The score, the interval, the board
  and the not-decided pairs are transcribed from `docs/PRODUCT_LIST.md`, whose
  live line reads `RANK 1 OF 7` (six entrants plus us) — checked to line 53 and
  its `[BOARD CORRECTED 2026-08-15]` block by this pass, and consistent. But
  transcription is all it is. No scoring call was made by either pass.
- **Whether §11a and §11b are complete.** They were written from
  `SUPERVISION_CHARTER.md`, `ESCALATION_CHARTER.md` §9.6c, R-ISOLATE and D19 in
  one pass. The delegation doctrine of 2026-07-26 is cited by the supervision
  charter but was **not opened** — anything it assigns beyond the five nouns
  §4 lists is not represented here.

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
   → `git log --oneline -1` — §9. **Read the SHA it prints**, and if your message
   claims an anchor, check that the anchor is that SHA and not its parent — §9.1.
9. Before you dispatch anything: read §11a, and **claim the item in
   `docs/DOCKET.md` §B before the agents exist** — §11b.
10. Before you run `pytest` by hand, purge `__pycache__` — §6. A green suite over
    stale bytecode is the cheapest wrong answer in this repository.
