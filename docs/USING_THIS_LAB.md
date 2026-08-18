# Using this lab

For an engineer who has just been given a brief in this repository and has not
worked here before. It is an operator's handbook, not a tour: it covers the
tooling that behaves differently here than elsewhere, the standards every result
is held to, and the mechanics of committing work into a tree that ten agents
write at once.

Every count in this document is a **reading at a stated frame**, never a
constant. The tree moves several times an hour, so each table gives the command
that reproduces its figure and the commit the figure was read at. Re-measure
before you quote. Where a claim was reasoned rather than measured, section 13
says so.

Unless a table names a different frame, figures were read at commit
**`8cefb4e9`** (2026-08-17T00:56:27Z).

Sections 3 and 4 are the ones that cost a day if skipped, so they come before
the orientation rather than after it.

---

## 0. How a number is stated here

The house rule is `docs/MEMORY_ARCHITECTURE.md` §8.1a: *"A state claim carries
its commit anchor. 'As of `08a87cc7`, X holds', never a bare 'X holds'."* The
test is whether the world could change without the sentence changing. Rules and
definitions are exempt; counts are not.

Two consequences for anything you write:

| Requirement | Source |
|---|---|
| A count carries the frame it was taken in | `docs/MEMORY_ARCHITECTURE.md` §8.1a |
| A verdict carries the thing it was checked against | `VERIFICATION_CHARTER.md` §6a |
| A sweep names which corpus arm it read | §4 below |
| A figure states its basis, per figure class | `COMPUTE_BUDGET_CHARTER.md` §2 |

---

## 1. What this lab is, and what it produces

An autonomous CFD laboratory. State an engineering objective in plain language;
the lab interprets it, forms a team of agents, runs real OpenFOAM solves, and
reports every result with a trust tier and a confidence envelope.

Its three stated principles: **real numbers only** ("hardcode the path, never
the result"); **the lab bounds its own trust**, so nothing is labelled VALIDATED
without an experimental comparison per ASME V&V 20 and everything else is TREND
ONLY; and **honest uncertainty**.

What it produces, in rough order of how much of the tree each occupies:

| Product | Where |
|---|---|
| A round-5 entry to an external turbulence-closure benchmark, scored locally | `demo-output/website/CLOSURE_*`, `campaign/` |
| Verification and validation records: ladders, rungs, gate verdicts | `demo-output/website/campaign/` |
| Solve case trees (OpenFOAM, DAFoam, VSPAERO) | `/home/ubuntu/certonomous-runs/`, outside the repository |
| Sealed one-page PDF certificates with a SHA-256 evidence seal | `demo-output/website/certificates/` |
| A control-room server and the SDK behind it | `sdk/chief_engineer/` |
| The lab's own instrument corpus: checks, guards, sweeps | `scripts/`, `sdk/tests/` |

**Before you read any campaign record, read
`docs/VALIDATION_INVENTORY.md`.** It is one row per gate or rung across every
campaign, with what each was checked against, whether that reference was ever
obtained, the tier of record with its commit anchor, and whether the gate can
fail at all. It is the only page that holds the shape of the whole, and its
headline is that almost nothing here is validated against the world.

### The headline result, with the clauses that are part of it

| Quantity | Value | Provenance |
|---|---|---|
| Round-5 overall closure score | 0.056647 | `demo-output/website/closure_challenge_round5_qcr.json` |
| Scored at benchmark commit | `deb91557` | pinned clone, scores but does not rank |
| Board | 6 entrants plus this entry, 7 positions | fetched 2026-08-11T23:33Z |
| Overall standing on that board | rank 1 of 7, at P(rank 1) 50.2% on a 0.2-96.9% at 95% interval, and not statistically decided against 4 of the 6 | `sdk/scripts/probability_of_rank.py` |
| Margin over Yang, the board leader | 0.001365 | Yang 0.058013 |
| P(rank 1) | 50.2% | 400,000-draw case bootstrap |
| Interval on P(rank 1) | 0.2-96.9% at 95% | double bootstrap, 2,000 x 4,000 |
| Pairwise comparisons not statistically decided | 4 of 6, Yang among them | same script, section 3 |
| Best-on-board individual cases | 2 of 8 | both of them declined rows |
| Individual cases won by the lab's own model | 0 of 8 | declined rows carry the organisers' RANS field |
| One-seed uncertainty bound on the overall | 0.002419 | `closure_challenge_seed_sensitivity.json` |
| That bound as a fraction of the margin | 177% | **the bound exceeds the margin** |

The last row is the one that governs how the result may be stated. The entry is
first on the point estimate and **not first within noise**. `docs/PRODUCT_LIST.md`
§4B makes the clauses mandatory rather than decorative: no surface, internal or
outward, may print "rank 1" without the interval, the not-decided pairs, and the
board named by entrant count and retrieval date. A commit anchor is not an
admissible board identifier.

**Submissions are PARKED.** Nothing is sent, uploaded, registered or filed
outward. See §5.

---

## 2. The box turns itself off

Root cron runs `/usr/local/bin/auto-stop.sh` every five minutes and powers the
machine down after a period of idleness.

| Constant | Value | Present in |
|---|---|---|
| `IDLE_MINUTES` | 30 | tracked and installed copies alike |
| `HOLD_MAX_HOURS` | 24 | tracked and installed copies alike |
| cron period | 5 minutes | `sudo -n crontab -l` |

The gate decides "is anyone working?" from three facts: a solver or mesher
process name, a worker process whose working directory is in the repository and
which is burning CPU, and a recently written session transcript. One override
exists and it needs no `sudo`:

    touch /home/ubuntu/Certonomous/.autostop-hold

That holds the box for 24 hours and then lapses by itself. A hold that never
lapses is a bill, which is why it expires, and the expiry is real rather than
nominal. Observed in the journal at 2026-08-17T01:15Z:

    auto-stop[49128]: hold file is 30h old (>24h) -- expired, ignoring
    auto-stop[49154]: ALIVE: worker pid 43488 busy in repo (300 CPU ticks in 3s)

Confirm the gate is honouring your hold with `journalctl -t auto-stop`.

### Filter `DRY_RUN` out of the journal, or read a test fixture as your box

Another agent's test harness exercises `auto-stop.sh` against temporary
directories, and its output interleaves with the real five-minute cron ticks.

| Journal reading at 2026-08-17T01:16Z | Count |
|---|---|
| Lines returned by `journalctl -t auto-stop -n 200` | 201 |
| Of those, tagged `[DRY_RUN]` | 41 |
| Real cron lines, which carry no tag | 160 |

A `[DRY_RUN] ALIVE` will reassure you that your hold works when it says nothing
of the kind, and a `[DRY_RUN] idle 90min, shutting down` will alarm you for
nothing. The real lines carry no tag:

    journalctl -t auto-stop --no-pager -n 200 | command grep -v DRY_RUN | tail -2

### The tracked gate and the installed gate are different files

| File | `SESSIONS` value |
|---|---|
| tracked `scripts/auto-stop.sh` | `/home/ubuntu/.claude*/projects/-home-ubuntu-Certonomous` |
| installed `/usr/local/bin/auto-stop.sh` | `/home/ubuntu/.claude-sanaa/projects/-home-ubuntu-Certonomous` |

The tracked copy scans a glob of every session-config directory. The installed
copy names exactly one. Both directories exist on this box and both hold
transcripts: 10 `.jsonl` files under `.claude-sanaa` and 10 under `.claude` at
`8cefb4e9`. A session running under `~/.claude` is therefore invisible to the
installed gate, and an occupied control room reads as an empty one.

The installed file is `-rwxr-xr-x root root`, so it is world-readable and you
can open the file that actually runs rather than trusting a summary of it. Its
`find "$SESSIONS" ... -newermt ... | grep -q .` clause can only ever see the one
literal directory.

`python3 scripts/installed_registry.py` reports the divergence as **PENDING**
with a declared waiver. The repair is committed and deliberately not installed,
because `/usr/local/bin/` is the box's power control and that belongs to the
owner. Until it is installed, the only thing holding this box is
`.autostop-hold`, which lapses after 24 hours.

**Practical rule:** touch the hold file when you start, and do not assume your
session is keeping the machine alive.

---

## 3. Your shell's `grep` and `find` are not GNU's

This is the highest-yield item in this document. It is `LESSONS.md` L-75.

| Command | What it actually resolves to |
|---|---|
| `grep` | a shell function running `ugrep -G --ignore-files --hidden -I --exclude-dir=.git` |
| `find` | a shell function running `bfs -S dfs -regextype findutils-default` |
| `command grep` | `/usr/bin/grep`, GNU |
| `/usr/bin/find` | GNU findutils |

`--ignore-files` honours `.gitignore`. This lab gitignores its large artefacts,
so the interactive `grep` sees a minority of the tree:

| Quantity at `8cefb4e9` | Value | Command |
|---|---|---|
| Files the shell's `grep` visits | 12,694 | `grep -rl '' . \| wc -l` |
| Files actually present, excluding `.git` | 57,522 | `/usr/bin/find . -path ./.git -prune -o -type f -print \| wc -l` |
| Fraction visited | 22.1% | ratio of the two |

Both absolute counts move every few minutes under a working fleet. The ratio has
held near 22% across every frame measured. Compute it rather than quoting a
pair:

```bash
echo "$(grep -rl '' . | wc -l) $(/usr/bin/find . -path ./.git -prune -o -type f -print | wc -l)" \
  | awk '{printf "%d of %d = %.1f%%\n", $1, $2, 100*$1/$2}'
```

**A `grep -r` that returns nothing here is a confident, clean zero over the
fifth of the corpus it visited, and says nothing whatever about the other four
fifths.** It is not a negative result.

`bfs` rejects GNU expressions. `find . -newermt "-30 min"` returns
`bfs: error: ... Invalid timestamp.` and exit 1, while `/usr/bin/find` with the
same expression works. Root's cron gets the real GNU tools, which is why
`auto-stop.sh`'s own `-newermt` clause works in production and fails if you paste
it into your shell. That last point is inference rather than measurement and is
listed in §13.

**The fix, every time: `command grep` and `/usr/bin/find`.** Better still, do not
shell out at all. `scripts/lab_check.py` enumerates with `git ls-tree` plus
`os.walk` for exactly this reason, and says so in its frame line.

---

## 4. The corpus has four arms. Sweep all four.

A sweep that reads one arm and reports a count has stated a number about its own
tooling, not about the lab.

| Arm | Files at `8cefb4e9` | Command |
|---|---|---|
| 1. Tracked | 20,764 | `git ls-files` |
| 2. Untracked, not ignored | 1 | `git ls-files --others --exclude-standard` |
| 3. Gitignored | 37,243 | `git ls-files --others --ignored --exclude-standard` |
| 4. Outside the repository | 132,049 regular files | `/usr/bin/find /home/ubuntu/certonomous-runs -type f` |

Arm 2 and arm 3 move on a timescale of minutes. Arm 3 is larger than arm 1 and
is invisible to the shell's `grep`. Arm 4 is larger than the whole repository and
is invisible to every git command. For arm 4, **say which population you mean**:

| Population | Count at `8cefb4e9` |
|---|---|
| Regular files | 132,049 |
| Regular files plus 748 symlinks | 132,797 |

Take your own reading; it is four lines:

```bash
printf '%-28s %s\n' \
  "1 tracked"    "$(git ls-files | wc -l)" \
  "2 untracked"  "$(git ls-files --others --exclude-standard | wc -l)" \
  "3 gitignored" "$(git ls-files --others --ignored --exclude-standard | wc -l)" \
  "4 run tree"   "$(/usr/bin/find /home/ubuntu/certonomous-runs -type f | wc -l)"
```

The sweep itself, all four arms:

```bash
cd /home/ubuntu/Certonomous
PAT='0\.056647'

# 1. tracked
git grep -la "$PAT" -- .

# 2. untracked, not ignored
git ls-files --others --exclude-standard -z | xargs -0 -r command grep -lI "$PAT"

# 3. gitignored  <-- the one everyone forgets
git ls-files --others --ignored --exclude-standard -z | xargs -0 -r command grep -lI "$PAT"

# 4. the run tree, outside the repo
command grep -rlI "$PAT" /home/ubuntu/certonomous-runs/
```

**Budget for arm 4.** It is 132,049 files outside the repository and it is not a
quick command; arms 1 to 3 return in seconds while arm 4 runs for minutes. Start
it first or run it in the background, and if you skip it, say in your record that
you swept three arms and not four. A sweep that quietly drops the largest arm is
the shape this section exists to prevent.

### Reach limits inside the tracked arm alone

Even confined to arm 1, no single `git grep` mode sees everything.

| Limit at `8cefb4e9` | Count | How derived |
|---|---|---|
| Tracked blobs | 20,764 | `git ls-files` |
| Reached by `git grep -a` | 20,738 | `git grep -a -l -e ''` |
| Unreachable in **any** mode | 26 | 17 symlinks (mode 120000) plus 9 empty blobs |
| Additionally skipped by `git grep -I` | 1,476 | set difference of the two reaches |
| Of those, marked binary by `.gitattributes` | 981 | `git check-attr binary` |
| Of those, auto-detected binary from NUL bytes | 495 | 1,476 minus 981 |

The 26-file gap has been stable across every frame measured this week even as
both totals moved. It is a property of the blob types, not of the corpus size.

### The `.gitattributes` blind spot

`git grep -I` skips files git *considers* binary, and git's opinion comes from
`.gitattributes` rather than from the bytes:

    *.pdf binary
    *.png binary
    *.jpg binary
    *.stl binary
    *.obj binary

| Marked-binary tracked files at `8cefb4e9` | Count |
|---|---|
| `.png` | 875 |
| `.stl` | 54 |
| `.pdf` | 50 |
| `.obj` | 2 |
| **Total carrying `binary: set`** | **981** |

Of those 981, some are plain text that every `-I` sweep in this lab silently
drops. The count depends on the test, so the test is named:

| Test for "contains no NUL byte" | Files |
|---|---|
| First 8,000 bytes only | 12 |
| Whole blob | 11 |

The single file separating the two is `docs/papers/Paper3.pdf`, which is
NUL-free in its first 8,000 bytes and not thereafter. Both figures are correct
answers to different questions, which is why neither travels without its test.

**Five of the eleven are sealed product certificates**, the lab's most
claim-bearing artefact, and their claim text is uncompressed ASCII that GNU
`grep` reads directly. That makes the blind spot material rather than a
curiosity.

**When a sweep must be complete, add `--text`.** `git grep -la "$PAT"` is the
same thing in short form, and `-a` is what most dispatch briefs here write, so
recognise both.

---

## 5. The standing rules

Sourced from the charters. Where a rule you have been told is *not* in the
charters, this section says so. That distinction matters more than the rule,
because the lab must never present its own invention as the owner's policy.

**Submissions are PARKED, and all external interaction is the owner's.**
`GOALS_AND_PROPOSALS_CHARTER.md` §8: *"every 'submission' action is parked at her
discretion. Challenge and measurement work continues at full priority. Nothing
external gets sent."* The class covers the closure-challenge entry, an upstream
DAFoam report, a workshop entry, and contacting a steward.
`SUPERVISOR_RULINGS.md` R9 adds that anything outward-facing *"carries the
company's name and stays hers."* Parked is not cancelled. What no longer exists
is any reading under which readiness slides into sending.

**Compute authorization is the owner's.** `ESCALATION_CHARTER.md` §1: *"Initiative
comes from the lab. The veto stays with the human."* Note honestly that the
numeric free-spend threshold is **not enacted**: §4 is marked *"PROPOSAL. Nobody
has set a number."* What binds is `COMPUTE_BUDGET_CHARTER.md` §3:

| Work class | Default budget |
|---|---|
| New capability | 60 core-minutes |
| Written report | 20 core-minutes |
| One ladder rung | 20 core-minutes |

and the charter's own line, *"A budget overrun stops the run. It does not get a
new budget."* Until you are told otherwise, you run no solves.

**Scoring calls are chief-authorized.** `SUPERVISION_CHARTER.md` §4, under
"retained and not delegable": *"No agent at any level makes a scoring call on the
challenge; the chief authorizes, and the outward act stays the owner's per ruling
R9."* The ledger stood at **6** at `8cefb4e9`. That count is not in the charters:
it lives in `docs/PRODUCT_LIST.md` and the closure surfaces, and the whole
scoring-call discipline is self-imposed rather than a benchmark rule. Quote it as
lab discipline, with its source.

**Commits are single-step pathspec.** `ESCALATION_CHARTER.md` §9.6: *"every commit
stages its files BY EXPLICIT PATH. `git add -A`, `git add .`, and `git commit -a`
are forbidden."* §9.6a requires `git commit -- <paths>` in a single step, and
forbids the bare `git commit` after it. §9.6b makes a `git diff <path>` read
mandatory before committing a shared file. The charter's own header warns that
the git rule lives at the very end of the file, below `## Related`, because the
earlier form in §3 no longer governs and carries a dated amendment saying so.
Mechanics and traps are in §7 below.

**Docket IDs are append-only and never renumbered.** Not a charter: it is
`docs/DOCKET.md`'s own header, W-4, 2026-08-11. *"IDs ARE APPEND-ONLY AND STABLE.
NOTHING IS EVER RENUMBERED."* On collision *"both keep their text and the later
one takes the next free ID."* Withdrawn IDs are struck in place and kept, never
reused. *"An ID is a reference target; moving it breaks every citation you cannot
see."*

**Durable records carry commit anchors, not present tense.** Not a charter:
`docs/MEMORY_ARCHITECTURE.md` §8.1a, quoted in §0 above.

**Strike and keep; never silently overwrite.** `docs/MEMORY_ARCHITECTURE.md`
§8.1: *"A record whose claim has been superseded is amended in place, dated, with
the original text retained. Never a silent edit, and never a deletion."* And: *"A
commit that refutes a standing record must amend that record in the same
commit."* Charter instances live at `VERIFICATION_CHARTER.md` §2b (*"Originals are
always retained and struck, never rewritten"*) and `SUPERVISION_CHARTER.md` §5.

This convention has a consequence for reading. A withdrawn figure stays visible
forever, on purpose, one line above the live one. **Read what the strikes say
before you copy a figure out of this corpus**, and note that a PDF cannot be
graded from its text layer, because a struck figure sits in the text stream
exactly as a live one does.

**A figure carries its basis.** Binding per figure class rather than as one
general rule: spend figures state gross or cleaned and name the cleaning rule
(`COMPUTE_BUDGET_CHARTER.md` §2, and *"A figure that is neither, or that does not
say which it is, is not published"*); no cost is presented as measured without a
record; a caption is derived from the value's provenance or it is not printed
(`VERIFICATION_CHARTER.md` §6); a reported order never appears alone (§3.2). The
sweeping general version is folklore rather than charter text, so cite the
specific clause for your figure class.

---

## 6. The verification standards

This is the actual method, and it is the reason the lab's output is worth
anything. Learn these before you write a check.

**1. A gate must be able to fail.** `VERIFICATION_CHARTER.md` §2a:

> Every gate answers two questions before it is a gate: (1) What result would make
> this gate FAIL? (2) Could a wrong treatment still PASS it?
> **A gate whose quantity is derivable by construction from its own inputs is an
> IDENTITY, not a control. It may be reported. It may never be gated on.**

Both answers go into the pre-registration where the gate is fixed. The honest
alternative, *"we know of no way a wrong treatment passes this"*, is allowed.
Silence is not.

**2. Three-valued, and never PASS from an empty set.** `VERIFICATION_CHARTER.md`
§9: *"absence of error evidence is not evidence of a clean result."* Every parser
and gate answers **did the check run** before **what did it find**, and carries a
third verdict for unknown that is not collapsed into the bad one. The lab's
canonical failure here: a mesh-quality parser returned `clean` on a log where the
tool had fatally errored, because it matched error *patterns* and a crashed log
contains none. *"A gate that reads silence as success can manufacture a pass,
which outranks every gate that merely misses one."* `SUPERVISION_CHARTER.md` §3a
writes the empty-set clause in: *"PASS / FAIL / UNKNOWN (an empty candidate set is
UNKNOWN, never PASS)"*.

**3. Every instrument needs a positive control AND a must-not-match control.**
`LESSONS.md` L-84: *"A control that only shows an instrument firing is half a
control. The other half is a set it must NOT fire on."* Plant outside the frame
to test reach, and just inside the boundary to test precision. A widened matcher
needs a near-miss it must reject, measured, before the figure ships. §12 runs all
three kinds.

**4. Findings are verified by re-derivation, not by an instrument's silence.**
`VERIFICATION_CHARTER.md` §10: check the primary source, and *"Treat agreement
with expectation as a reason for more scrutiny, not less."* §14: *"An attribution
is a claim, and it is a claim about a file. Name the file, and open it before the
finding leaves the room."* §6a warns that a check written with the same helpers as
the thing it checks proves only that a number was transcribed faithfully. "I
searched and it is not there" is evidence about your search.

**5. A claim states its frame.** `VERIFICATION_CHARTER.md` §6a, *"The referent
travels with the verdict"*: a verdict label carries the thing it was checked
against, on every surface it appears on. Three admissible answers: EXTERNAL, and
name it, because *"validated against the literature"* names nothing;
SELF-REFERENTIAL, which *"is not a defect and must not be hidden"*; or NONE. §3.3
requires that a guard states the sample it measured over, and that the sample is
the sample the quantity was computed from.

**The bright line the whole charter turns on** (§1):

> Done means a gate has a verdict, the verdict cites an artifact, and the artifact
> is still on disk.

Four more worth knowing on day one: a failed gate blocks every downstream rung
(§3); a gate that was not reached is stated as not reached, never replaced by a
nearer gate that was (§2); nothing the lab fits, inverts or tunes on may be a
scored case of a benchmark it reports a score against (§11); and pre-register
before compute, with no exception for short runs (`ESCALATION_CHARTER.md` §9).

---

## 7. Checking the lab's health in one command

    python3 scripts/lab_check.py --list          # enumerate, run nothing, seconds
    python3 scripts/lab_check.py --no-tests      # fast tier
    python3 scripts/lab_check.py                 # everything, including the suite

`lab_check.py` is the enumerated runner everything reports through. Its exit
contract is a severity ladder rather than a taxonomy: `{0: PASS, 1: FAIL, 2:
FAIL, 3: UNKNOWN}`, with 4 meaning a blocking UNKNOWN.

### What a run costs, and why the wall figure is not a property of the runner

| Tier at `8cefb4e9` | Wall | User CPU | System CPU | Exit |
|---|---|---|---|---|
| `--list` | 0.6 s | negligible | negligible | 3 (UNKNOWN, nothing ran) |
| `--no-tests` | 325.6 s | 315.2 s | 12.9 s | 1 (FAIL) |
| full tier including the suite | not measured at this frame | | | |

Both tiers were run against a box carrying other agents' work at the same time.
The wall figure is therefore a measurement of this box under load, not a clean
benchmark. **If you quote a runtime, quote the load with it.**

### The report is streamed, and a truncated log says so

Every line is written and flushed at the moment it is produced, and a complete
run ends with a `LAB-CHECK-END COMPLETE` line. A log that stops before one is a
run that was interrupted, **not** a run that found nothing. That distinction is
the whole reason the marker exists: the box powers itself off on an idle timer
(§2) and a usage limit can terminate every agent at once, so an interruption at
minute 19 of a 20-minute run must be distinguishable from a clean finish.

### The frame block is the coverage statement

    FRAME -- what was looked at, and how it was found
      repo               /home/ubuntu/Certonomous
      HEAD               8cefb4e9
      enumeration        git ls-tree -r HEAD (not the index) + os.walk over
                         scripts, sdk/tests (never the shell's grep/find)
      candidates         183  (tracked 183, on disk 183)
      admitted           109  (19 script gate(s), 90 test file(s))
      skipped            74  (13 of them could be hiding a verdict)

`skipped` is the coverage statement, not a footnote. At `8cefb4e9` the 74 broke
down by named reason:

| Skip reason | Count |
|---|---|
| not an executable module (data, prose or fixture) | 22 |
| shell | 15 |
| writes-to-tree | 13 |
| cannot-fail | 10 |
| no-entry-point | 8 |
| requires-arguments | 5 |
| the runner itself | 1 |
| **Total** | **74** |

Thirteen of those are reported as UNKNOWN rather than as passes, because their
skip reason could be hiding a verdict. **UNKNOWN is not a soft pass**: it is a
statement about the instrument, not about the lab.

If the frame block prints an `untracked only` line, read it before you trust a
green. Gates that exist only in this working tree are somebody's uncommitted work
in flight; they will not survive a clone, and a verdict that depends on them is a
verdict about this box.

### The FAIL is correct, not broken

At `8cefb4e9` the fast tier returned FAIL, exit 1, with 19 of 19 checks run:

| Check returning FAIL | Exit |
|---|---|
| `scripts/check_absolutes.py` | 1 |
| `scripts/check_pdf_surfaces.py` | 1 |
| `scripts/check_proposal_surface_coverage.py` | 1 |
| `scripts/contention_audit.py` | 1 |
| `scripts/docket_citation_guard.py` | 1 |
| `scripts/self_audit.py` | 1 |

Each is a real finding about the lab that someone has not yet closed. The runner
is doing its job; the lab is not green. **Do not "fix" the runner, and do not
widen a gate to make it pass.** That is forbidden outright:
`VERIFICATION_CHARTER.md` §8, *"A gate is never widened after a result misses
it."*

### Nothing schedules any of this

| Installed item at `8cefb4e9` | State |
|---|---|
| auto-stop gate | PENDING, declared divergence under waiver |
| root crontab, ubuntu crontab, provision script, lab launcher | MATCH |
| pre-commit index guard | MATCH |
| nightly lab-check cron | ABSENT |
| pre-push hook | ABSENT |

`scripts/installed/certonomous-lab-check.cron` is tracked and inert. Every check
in this lab reddens only when a person types its name.

### `__pycache__` is a gate, not housekeeping

`lab_check.py` purges `__pycache__` before it runs and prints the count. This is
`docs/DOCKET.md` D1, and the real instance is worse than housekeeping suggests:
an equal-length source mutation plus a restore left a stale `.pyc`, and for three
consecutive runs *"the clean control failed and the mutated case passed, a
perfectly inverted mutation matrix, which a less suspicious reading would have
written up as 'the recompute is dead'."*

The mechanism reproduces in a scratch package in four commands:

    # pkg/rule.py, 56 bytes, correct:  return "PASS" if x > 10 else "FAIL"
    # test asserts verdict(5) == "FAIL"
    $ python3 -m pytest -q test_rule.py
    1 passed                                     # honest pass

    # MUTATE to a same-length source that must FAIL, and restore the mtime
    # pkg/rule.py, 56 bytes, broken:   return "PASS" if x > -1 else "FAIL"
    $ python3 -m pytest -q test_rule.py
    1 passed                                     # <-- THE MUTATION IS INVISIBLE

    $ python3 -c 'from pkg.rule import verdict; print(verdict(5))'
    FAIL                                         # the source says PASS. this is the .pyc.

    $ /usr/bin/find . -name __pycache__ -type d -exec rm -rf {} +
    $ python3 -m pytest -q test_rule.py
    1 failed                                     # the true verdict

**A test that passed was the failure.** The suite reported green over a source
file it never compiled. Every mutation test and every "I broke it and the gate
caught it" control is answered by the cache instead of by your change, and the
cache's answer is the old behaviour, which is usually the passing one.

Two conditions have to line up, and both are ordinary here:

| Condition | Why it is ordinary |
|---|---|
| Same file size | CPython validates a `.pyc` on the `(mtime, size)` pair, not a hash |
| Unchanged mtime | `git checkout`, `git stash pop`, a worktree materialising a file, or two writes inside one filesystem timestamp |

And the remedy people reach for does not work. `PYTHONDONTWRITEBYTECODE=1` stops
Python *writing* bytecode; it has never stopped it **reading** bytecode already
on disk. Measured in the same scratch package immediately after the inverted run:
still `1 passed`, still inverted.

**The rule: purge, then measure, in that order.**

    /usr/bin/find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null

`lab_check.py` does this for you. **If you run `pytest` by hand, you are the one
purging it.** If you are mutating a source file to prove a gate can fail, purging
between every cell is not optional, and note the damage takes two shapes: the
demonstration above gives both cells the same verdict, so the mutation is simply
invisible, while D1's real instance gave a fully inverted matrix. The second is
more dangerous because it looks like a result. D1 remains open: no harness yet
clears the cache between every cell and asserts the clean control and the mutated
case in the same run, so on mutation work **you are the harness**.

---

## 8. Git here has seven traps, and six of them are silent

### 8.1 Backticks in `git commit -m`

The message goes through the shell. Two failure modes, both executed in scratch
repositories:

| Form | What happens |
|---|---|
| Unbalanced backtick | bash fails at **parse** time; the commit never runs, HEAD does not move, the file stays staged |
| Balanced backticks | the commit **succeeds and lies**: the substitution ran before the commit existed, so `$(git rev-parse HEAD)` names the **parent** |

A commit-anchored record that anchors at the wrong commit is exactly the failure
the anchor rule exists to prevent.

The unbalanced case is worse than "anything after it in the same invocation".
Run inside a script, bash aborts the **entire remaining file** rather than just
the rest of that command. A five-step script printed step one, hit the unbalanced
backtick, and never executed steps two through five. If you have a
commit-then-verify script, the unbalanced backtick eats the verification too,
which is precisely the check that would have told you.

**The working form:**

    printf 'use `git ls-tree HEAD` to verify\n' > <msgfile>
    git add <paths>
    git commit -F <msgfile> -- <the same paths>
    git log --oneline -1        # <-- always. This is the verification.

`git log --oneline -1` is not optional politeness. It is the only thing that
distinguishes "committed" from "the shell ate it".

### 8.2 `core.filemode=false` silently discards the exec bit

`git config --get core.filemode` returns `false` in this repository. The
observable rule is sharper than "the mode comes from the worktree":

> **With `core.filemode=false`, a pathspec commit takes the mode from `HEAD`.**
> Not from the index, not from the worktree.

Measured in both directions:

| `HEAD` mode | Index says, via `update-index --chmod` | After `git commit -- run.sh` |
|---|---|---|
| 100644 | 100755 | **100644**, the `+x` was discarded |
| 100755 | 100644 | **100755**, the `-x` was discarded |

So `git update-index --chmod` is completely inert under this lab's mandated
commit form, in both directions. That is the whole of docket D134: under a
pathspec commit the mode can be neither set nor cleared, so the exec-bit waiver
register can only grow.

**The trap inside the repair.** The fix passes `-c core.fileMode=true`, and only
one of the two obvious places is load-bearing:

| Where `-c core.fileMode=true` was passed | Index after add | `ls-tree HEAD` |
|---|---|---|
| on the **commit** only | 100644 | **100755**, correct |
| on the **add** only | 100755 | **100644**, wrong |

Putting it on the `add` alone is the natural economy, because you can *see* the
index go to 100755, and it silently produces 100644 in the tree. **The `-c`
belongs on the commit, and the worktree file must carry the bit:**

    chmod +x <file>
    git -c core.fileMode=true commit -F <msgfile> -- <file>
    git ls-tree HEAD <file>          # <-- the verification. 100755 or you failed.

**Verify with `git ls-tree HEAD`, never `git ls-files -s`.** `ls-tree` is what a
clone materialises; `ls-files -s` is what your index believes.
`sdk/tests/test_exec_bits.py` reads `ls-tree` on purpose, and returned **15
passed** at `8cefb4e9`.

One uncomfortable measurement, recorded because it explains why the trap exists
here and not in most repositories: a **bare** `git commit` with 100755 in the
index does preserve the bit. The form that works is the form the charter forbids.
Do not take that as a licence.

### 8.3 A pathspec isolates by FILE, not by AUTHOR

Ten agents write this tree. `ESCALATION_CHARTER.md` §9.6b states the rule:
committing your row commits whatever anyone else has left uncommitted in that
file. §9.6b makes the `git diff <path>` read before the commit mandatory, and
§9.6c forbids the polite alternative of leaving it uncommitted.

**It cuts both ways, which is the half people miss.** A docket row written and
left for fourteen minutes before committing was found already committed, intact
and byte-for-byte, inside **another session's** commit whose message was about
something else and did not mention it. Nobody did anything wrong: that session
read the diff, saw a complete row, and committed the file it was told to commit.
**On a shared file, "I will commit it in a minute" is not a plan.** Write it and
commit it in the same breath, and when you go looking for the commit that carries
your work, search by content with `git log -S` rather than by your own commit
messages.

For `docs/DOCKET.md` specifically there is now a safe granularity, and it is
§9 item 8: a private-index form that commits the parent's blob plus only your own
rows, selected by row ID and never copied from the worktree, landed with a
mandatory compare-and-swap. Use that on the docket, and the paragraph above
everywhere else.

Also forbidden on a shared tree (`ESCALATION_CHARTER.md` §3): `git reset --hard`,
`git stash`, `git checkout -- <path>`, `git clean`. *"An unexpected uncommitted
change is inspected, never reverted."*

`git status` has been observed reporting a dirty file as clean while other
sessions committed. Read content, not summaries. §9 item 5 gives the forms that
do not consult the index.

Finally, `git add` here loses races for `.git/index.lock`, and the following
pathspec commit succeeds anyway, because `git commit -- <paths>` takes those
paths from the worktree and does not need them staged. So `git add` is a
convenience rather than a prerequisite. Check the commit's file count and
diffstat, because a form that works without staging also works when you did not
mean it to.

### 8.4 `pgrep` and `pkill` match their own invoking shell

    $ bash -c 'pgrep -f "zzz_unique_marker_pattern"; echo exit=$?'
    839893
    839916
    exit=0

That pattern appears nowhere on this box. Both PIDs are the shells running the
command. A `pkill -f <pattern>` kills its own shell, and the chained command after
it silently never runs.

The obvious remedy has two limits, both measured:

| Remedy | Limit |
|---|---|
| `pgrep -x <name>` | matches the kernel's `comm`, capped at **15 characters**; a longer pattern **returns exit 1**, which a script reads as "no such process" |
| `pgrep -f "$PAT" \| command grep -vx "$$"` | not enough: the **parent** shell also carries the pattern on its command line and survives the filter |

The working form filters both, and for the killing case never uses `pkill -f` at
all:

```bash
pgrep -f "$PAT" | command grep -vxe "$$" -e "$PPID"
# resolve to a PID list, drop your own and your parent's, PRINT what remains,
# and only then kill it.
```

### 8.5 The mandated commit form cannot express an untracking

`git commit -F <msgfile> -- <paths>` takes those paths' content **from the
working tree**. Untracking a file that stays on disk is therefore the one
operation the charter's own commit form cannot perform: `git rm --cached` stages
the removal, and the pathspec commit puts the file straight back from the
worktree, with no error and an ordinary-looking diffstat.

Demonstrated in a scratch repository at `52cdf6dd`, not inferred:

| Step | Result |
|---|---|
| `git rm --cached junk.log` | index shows `D junk.log` |
| `git add -- .gitignore` | index shows `M .gitignore`, `D junk.log` |
| `git commit -F msg -- .gitignore junk.log` | commit lands |
| `git ls-files` afterwards | **`junk.log` is back**, and the deletion is gone from the tree |

The working form is the index-isolated one, which is the same instrument §9
item 8 gives for the docket and for the same underlying reason: it states the
tree it intends to write instead of inheriting one.

```bash
OLD=$(git rev-parse HEAD)
BLOB=$(git hash-object -w .gitignore)          # any file you are also changing
export GIT_INDEX_FILE=$(mktemp)                # a PRIVATE index; never the shared one
git read-tree "$OLD"
git ls-files <paths> | git update-index --force-remove --stdin
git update-index --cacheinfo 100644,"$BLOB",.gitignore
TREE=$(git write-tree)
NEW=$(git commit-tree "$TREE" -p "$OLD" -F <msgfile>)
unset GIT_INDEX_FILE
git diff --name-status "$OLD" "$NEW"           # <-- ASSERT before the ref moves
git update-ref refs/heads/main "$NEW" "$OLD"   # compare-and-swap on the parent
```

Three properties are load-bearing and none is optional. The index is **private**,
so a concurrent agent's staged work is never read into your tree. The
**tree-diff assertion runs before `update-ref`**, because after the ref moves
there is nothing left to refuse. And `update-ref` is given the **observed
parent**, so it fails rather than clobbers if HEAD moved while you worked.

**The final step is an index cleanup, and it must be surgical under a live
fleet.** A blanket `git read-tree HEAD` on the shared index is the obvious
tidy-up and it will un-stage whatever anyone else has staged. When batch B of the
untracking ran, the shared index held another session's staged docket rows, a
staged ladder edit and a staged deletion of a grade record. The cleanup was
`git update-index --force-remove --stdin` over **only the paths this agent
removed**, and the other session's three entries were compared before and after
and were byte-identical. Remove your own paths; leave everything else alone.

### 8.6 `git check-ignore` is silent about tracked files, which is the only kind you are asking about

`git check-ignore` skips paths that are in the index. Asking it "does this
tracked file match an ignore rule?" therefore returns **nothing and exit 1**,
which reads exactly like "no rule matches it".

| Invocation | Result on a tracked path that `.gitignore` matches |
|---|---|
| `git check-ignore -v <path>` | no output, exit 1 |
| `git check-ignore --no-index -v <path>` | `.gitignore:48:**/processor[0-9]*/  <path>` |

An audit of 6,938 tracked files against the committed `.gitignore` returned zero
rows on the first pass for this reason. Zero rows was the shape of the answer
that would have justified doing nothing, and it was produced by the instrument
rather than by the corpus. **Pass `--no-index` whenever the question is about a
file that is already tracked**, which is every interesting case, because a file
that is both ignored and untracked raises no question.

Two further habits from the same family:

- **Gate on the exit code, not on the printed rule.** `check-ignore -v` prints
  the matching line for a negation such as `!/uq_batch.log` as readily as for a
  positive rule, so the printed line does not tell you which way the answer went.
  `git check-ignore -q <path>; echo $?` returns 0 for ignored and 1 for not.
- **Test the class on files that do not exist.** A rule proven only against
  today's filenames has been proven to match those filenames. Running
  `--no-index` against `mbc_retry7.log` and `scipy-1.2.3-cp312.whl`, neither of
  which is on disk, is what shows the pattern is doing the work.

### 8.7 `git ls-files` cannot see a file this lab's own commit protocol landed

The private-index commit form of 8.5 and of section 9 item 8 writes a tree and
moves the ref. It never touches the shared index. A file that entered the
repository that way is therefore **in `HEAD` and absent from `git ls-files`**,
and any instrument that takes `git ls-files` to mean "the tracked set" reports
it as untracked.

`scripts/check_verdict_cells.py` was the specimen. It was reported as untracked,
and as existing only in the working tree, by five separate sessions on
2026-08-17. It was in `HEAD` for all five, mode **100755**, landed at `12f8a83e`
and extended at `a5080f6e`, and the answers below were re-taken at three
different HEADs across the day and did not move.

| The question you meant to ask | The command that answers it | Answer at `3af826ed` |
|---|---|---|
| Is it in the commit? | `git cat-file -e HEAD:scripts/check_verdict_cells.py; echo $?` | **0**, it is |
| What does a fresh clone materialise? | `git ls-tree HEAD scripts/check_verdict_cells.py` | **`100755 blob 126ba8e9`** |
| What does the shared index believe? | `git ls-files -- scripts/check_verdict_cells.py` | **nothing, and exit 0** |

The third row is the whole trap. `ls-files` exits **0** while printing nothing,
so a caller that gates on the exit code reads success and a caller that gates on
the output reads "untracked". Both readings are wrong and neither errors, which
is why this one survived five tellings in a single day.

**`HEAD` is the referent. The index is never the frame.** Section 8.2 already
said so for the exec bit, *"`ls-tree` is what a clone materialises; `ls-files -s`
is what your index believes"*, and the rule generalises from modes to existence.
Before writing that a file is untracked, run `git cat-file -e HEAD:<path>`, which
answers the question that was actually asked. A detached worktree checked out of
`HEAD` is the second and independent check rather than a rerun of the first: the
gate worktrees cut at `32d4ae0d`, `e9f66498` and `3af826ed` while this section
was written each materialised the file on disk.

**The blast radius is not one file, and it grows on its own.** `902b72fc`
measured **160** files that live in `HEAD` and that `git ls-files` cannot see,
and a reorganisation had built its entire rule set by classifying `git ls-files`
output, so three trees, one of them 1.51 GB, appeared in no rule at all. D348
re-measured it at `3af826ed` and found **477 paths present in `HEAD` and absent
from the index, and zero the other way** -- the asymmetry is what identifies them
as landed work rather than deletions. Worse, the invisible files skew NEWEST,
because every commit made this way adds one: `scripts/check_absolutes.py` was
condemning citations to the lab's own freshest tests as `CITES_MISSING_CHECK`.

A census whose frame is `git ls-files` is a census of the index, and this lab
does not write the index. State the frame as `git ls-tree -r HEAD` and the count
moves. `scripts/lab_check.py:tracked_frame` already carries that referent under
D274; prefer it to rolling your own.

---

## 9. When agents collide, which is constantly

Ten agents write this tree. Collisions are the normal case rather than the
incident, and every mechanism below exists because one already happened.

**1. Claim the item before you dispatch it.** `docs/DOCKET.md` §B carries a live
dispatch-claim block: *"CLAIM AN ITEM BEFORE YOU DISPATCH IT, write your session
into the Status column first."* Added after two chief sessions independently
dispatched the same four briefs off the same directive. The proof is the B1
collision: two agents ran the identical sweep brief and one's `Write` landed on
the other's already-committed document, **replacing a 335-line document with a
281-line one and dropping two sections**. It survived only because that agent went
looking. *"One edit before dispatch makes the collision visible while it is still
cheap: the agents do not exist yet."*

**2. Do not leave a shared file dirty "to be polite".**
`ESCALATION_CHARTER.md` §9.6c: *"leaving a shared file dirty does not protect your
work. It hands the decision to whoever commits next"*, which on this tree is a
matter of seconds. **On a shared tree, inaction is not neutral.**

**3. Committing only your own hunks.** §9.6c carries the procedure:

```bash
git diff --cached --name-only        # MUST be empty before you start. Check it.
git diff <path> > /tmp/full.patch    # everything currently uncommitted
# split the patch and keep only the hunks you wrote -- do not eyeball it
git apply --cached /tmp/mine.patch   # stage YOUR hunks only
git diff --cached --stat             # confirm what is staged
git diff --cached | command grep -c '<their marker>'   # confirm theirs is NOT
git commit -F <msgfile>              # the index holds only your hunks
```

Two notes from the charter make this safe rather than clever. That final
`git commit` has **no pathspec**, normally forbidden, and *"it is safe only
because the index was empty and you put exactly your own hunks in it. Check that,
do not assume it."* And **say in the commit message that you did this and why**.

**4. Never revert what you did not change.** `ESCALATION_CHARTER.md` §3 forbids
`git reset --hard`, `git stash`, `git checkout -- <path>` and `git clean`.

The two sources disagree on one point and a newcomer should see the disagreement
rather than a smoothed version of it. The docket's account of the B1 collision
records the surviving agent restoring the file with `git checkout --`, the exact
command §3 forbids. Both readings are defensible: §3 protects a *live*
uncommitted change from destruction, whereas B1 was a restore *to* a committed
state after a `Write` had already destroyed one. The reading offered here is that
§3 governs and B1 was an exception justified after the fact by having compared
both versions first, which is the part that made it safe. That is not settled.
**If you are about to run `git checkout --` on this tree, treat it as
escalation-worthy and say in your record what you compared before you ran it.**

**5. Assume your reads are stale, and compare content rather than summaries.**
`git diff -- <path>` compares the worktree against the **index**, and the index
on this tree is shared with every other agent (item 9). `git diff HEAD -- <path>`
walks the index too: a path with no index entry reads as **deleted** even though
the file is byte-present on disk. Measured on a file that was 288 lines on disk,
289 in HEAD, and whose true difference was one line, `git diff HEAD --numstat`
returned `0 289`, a whole-file deletion, because `git ls-files -s` on it printed
nothing at all.

That is a by-product of the private-index protocol itself, so it recurs: a commit
built with `GIT_INDEX_FILE` never writes the shared index, so a new file it lands
has no entry there until somebody runs `git add` or `git reset`.

**The two forms that actually compare content, neither of which consults the
index:**

```bash
git show HEAD:<path> > /tmp/head.copy && diff /tmp/head.copy <path>
test "$(git rev-parse HEAD:<path>)" = "$(git hash-object <path>)"
```

`scripts/check_docket_reconciliation.py` is built on the first of these for
exactly this reason.

**6. Expect to lose the index lock, and know it does not stop you.** See §8.3.

**7. The session scratchpad is SHARED, and a peer will overwrite your files under
you.** A commit message written to `<scratchpad>/msg.txt` was replaced wholesale
by another agent's message between the `Write` and the commit. It was caught only
because the identity trailer had already been appended, so a `tail` showed one
agent's `Lab-Agent:` line sitting under a peer's prose. **A peer's text would
otherwise have landed under that handle, with that trailer attesting it.** A
listing of the directory at the time held 120 entries written by many agents,
including six differently named copies of the docket. The protocol applies to
every round-tripped intermediate file, not only commit messages:

- Work in a **per-agent subdirectory**, `<scratchpad>/<task>-<your agent-hex>/`,
  never in the scratchpad root.
- **Byte-verify immediately before the file is consumed, not when you wrote it.**
- **This matters far beyond commit messages.** A peer overwriting a planted
  control's readback converts a broken sweep into a clean bill of health. A
  control you re-read from a shared path is a control you have not run.

**8. On `docs/DOCKET.md`, the pathspec form is unsafe whenever a peer holds a
row.** `git commit -- <path>` takes the file from the **working tree**, so it
commits every foreign row sitting in it. Measured at one frame,
`git diff HEAD -- docs/DOCKET.md` showed 2 added lines, both of them foreign
rows, so a pathspec commit at that moment would have landed two other agents'
work under one message. The standing form instead:

```bash
EXPECTED_OLD=$(git rev-parse HEAD)          # read ONCE; this is the CAS token
# Rebuild the blob as the PARENT's docket plus ONLY your own rows, selected by
# row ID. Never copy the worktree file -- that is the capture you are avoiding.
git show $EXPECTED_OLD:docs/DOCKET.md > $D/new.md && cat $D/myrow.txt >> $D/new.md
BLOB=$(git hash-object -w $D/new.md)
export GIT_INDEX_FILE=$D/index && rm -f $GIT_INDEX_FILE   # the SHARED index holds
git read-tree $EXPECTED_OLD                               # other agents' staged files
git update-index --cacheinfo 100644,$BLOB,docs/DOCKET.md
TREE=$(git write-tree)
NEW=$(git commit-tree $TREE -p $EXPECTED_OLD -F $D/msg.txt)
unset GIT_INDEX_FILE
git update-ref refs/heads/main $NEW $EXPECTED_OLD          # MANDATORY, never optional
# AND THEN, once the CAS has succeeded, this step is part of the protocol:
# write your row into the WORKTREE copy too, inserted in numeric order by ID.
# The form above never touched the worktree file, so without this the two diverge.
```

**Why the compare-and-swap is not optional.** The commit was built with
`$EXPECTED_OLD` as its only parent. If HEAD moved while you were building it, a
plain `git update-ref refs/heads/main $NEW` makes your commit **revert the
intervening one**, deleting a peer's work outright, silently, with a clean
diffstat. Capture publishes a peer's work under the wrong message; a lost race
**destroys** it. The CAS refuses loudly instead:

    $ git update-ref refs/heads/main $H $(git rev-parse HEAD~3) ; echo "exit=$?"
    fatal: update_ref failed for ref 'refs/heads/main': cannot lock ref
    'refs/heads/main': is at e4c1319e... but expected f3c27a0c...
    exit=128

Declare the row count with `python3 scripts/hunk_check.py docs/DOCKET.md:<n>` and
verify the landed commit with its `--at <sha>` mode. The worktree mode reads
high, because it sees the foreign rows too.

**The write-back is part of the protocol, not an afterthought.** The form above
rebuilds from HEAD's docket and commits it directly, never writing the row back
into the working copy. So **every private-index commit widens the gap between
HEAD and the worktree**, monotonically, and nothing in the repository reports it.
A conforming agent rebuilds from HEAD's blob and so cannot drop a row. Any agent
that edits the worktree copy and commits it **by pathspec**, the form still
mandated for every other file and the one habit reaches for, silently reverts
every private-index row landed since the worktree last matched HEAD.

**So run the reconciliation check before you edit `docs/DOCKET.md` at all**, and
read its output by direction, because the two directions mean opposite things:

| Diff direction | Meaning | Action |
|---|---|---|
| `< D<n>`: in HEAD, not in the worktree | a row landed by private index and never written back | **HEAD wins.** Insert it into the worktree in numeric order by ID. It is already committed and must not be committed again |
| `> D<n>`: in the worktree, not in HEAD | **unlanded work**, somebody's finding living in no commit | land it by ID through the form above, never by copying the worktree file, and never by `git checkout --` |

`scripts/check_docket_reconciliation.py` runs this. Treat the divergence as the
**steady state of this file rather than as an incident**: it reappears every time
anybody follows item 8 without the write-back step.

**And record the by-product, because somebody owns it.** An agent that declines
to commit rather than capture leaves **orphaned rows**: text that lives in the
worktree and in no commit, invisible to `git log`, destroyed outright by any of
the reverting commands item 4 forbids. Rows have sat orphaned across four or more
commits and were landed only because an agent was dispatched to do it. **Whoever
leaves foreign rows uncommitted must say so in their commit message, and somebody
must be dispatched to land them.**

**9. The shared index is a loaded gun, and `git commit` with NO pathspec fires
it.** There is one `.git/index` and every agent's `git add` writes to it. At one
frame `git diff --cached --stat` read:

    docs/AGENT_ATTRIBUTION.md              |  11 --
    docs/DOCKET.md                         |  10 +-
    docs/USING_THIS_LAB.md                 |  49 +++------
    scripts/self_audit.py                  | 117 +++------
    sdk/tests/test_rank_claim_surfaces.py  |  67 ------
    sdk/tests/test_rank_claim_values.py    | 189 ++---------
    6 files changed, 41 insertions(+), 402 deletions(-)

None of it belonged to the agent that found it, and it was stale against HEAD **in
the reverting direction**. `git show :docs/DOCKET.md` did not contain the newest
landed row, so committing the index would have **deleted a landed docket row**. A
bare `git commit` by anybody, for any reason, would have reverted 402 lines across
six files with a clean-looking diffstat and a message about something else.

- **Never run `git commit` without a pathspec on this tree**, and check
  `git diff --cached --stat` before any commit form at all. `hunk_check.py`
  reports staged-and-undeclared paths for exactly this reason.
- **Do not "clean up" the index yourself.** Those blobs may be another agent's
  in-flight work. Item 4 and `ESCALATION_CHARTER.md` §3 govern: inspected, never
  reverted. **Escalate it; the clearing is the chief's call.**
- **The private-index form of item 8 is immune to all of this**, and that is a
  second reason to prefer it: it builds from `git read-tree $EXPECTED_OLD` in a
  `GIT_INDEX_FILE` of its own, so the shared index is neither read nor written.

The safe clearing procedure, when the index is found dirty with work that is not
yours, is three steps and none of them is a reflex: **read what is staged** with
`git show :<path>` rather than the diffstat alone, because a diffstat that looks
like a tidy 41/402 can be a reverting snapshot; **report it**; and **let the owner
or the chief decide.** Clearing is safe only after each staged path has been shown
to be byte-identical between worktree and HEAD, which is a measurement rather than
an assumption. **A dirty index is a state this tree passes through continuously**,
so the check belongs before every commit. Note that `git diff --cached` exits `0`
whether it is empty or not: **measure the byte count, not the exit code.**

---

## 10. How work gets dispatched, and what independence costs

**First establish which of you you are.** This lab has two shapes of agent with
opposite duties, so a newcomer who guesses wrong will either do work that was not
theirs or supervise work nobody did:

| Role | Does | Does not |
|---|---|---|
| Working agent | executes one brief in its own lane, and reports | dispatch, grade its own output, or settle questions on the chief's retained list |
| Supervisor (family or chief) | issues guidelines, performs four checks personally, dispatches | run the family's solves, write its GUI, or fetch its papers |

Your dispatch brief tells you which you are. If it does not, that is a defect in
the brief and worth saying so before you start. If you find yourself doing the
work you dispatched, you have collapsed the two roles and the independence rules
below no longer hold.

`SUPERVISION_CHARTER.md` §1 is the line the whole model hangs on:

> **Every big task family has a standing supervisor, and four kinds of check are
> done by a supervisor personally or they have not been done.**

And the test it gives: *"for any measurement-script change, crash, big claim or
compute launch in the last week, name the supervisor who checked it and the
record of the check. **'An agent reported it clean' is not an answer to that
question. It is the thing the question exists to catch.**"*

**The four families** (§2), each with a standing supervisor:

| Family | Scope |
|---|---|
| DAFoam and adjoint | gradient ladders, FD verification, defect arcs, mesh warping: anything whose product is a derivative |
| Closure and UQ | the closure challenge, field inversion, model-form studies, the three uncertainty channels |
| Cases and campaigns | case families, refinement ladders, campaign records, the gate table |
| Infrastructure and standards | the harness, monitors, audits, standards documents, the fleet's own operations |

**The four personal checks** (§3), which may not be delegated downward:

| Check | The charter's words |
|---|---|
| Code diffs on measurement scripts | *"An instrument change without a supervisor's read is an uncalibrated instrument."* |
| Crash triage, guilty until shown to be a mere bug | *"A crash written off without triage is a discarded measurement."* |
| Big-claim verification before belief | a code sweep **and** an independent diagnostic; *"the claim is assumed wrong until it has been defended against its own evidence."* |
| Pre-registration presence before compute | the supervisor checks *"the commit exists, not that somebody meant to write one."* |

**Retained by the chief and not delegable** (§4): scoring-call authorization,
cross-family arbitration, negative-verdict reviews on every FAIL, NO-GO or
refuted prediction, custody of the daily list and research board, and everything
the 2026-07-26 delegation doctrine assigns.

### Independence is a dispatch property, and it is not free

Ladder V's **R-ISOLATE** turns on a **non-author** measuring a rung
(`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md`). Its opening
sentence is the lesson: the rule had been enforced by *"everyone being careful"*,
and *"that is not enforcement ... independence that depends on care fails the
first time two agents pick the same filename"*. `LESSONS.md` L-77 is the instance,
where an author overwrote a grader's held-out evidence and nobody broke a rule.

R-ISOLATE has four mechanical parts. Only part 1 is summarised here, because it
is the one that fails silently. **Read the other three at the source before you
dispatch a grader.**

**Part 1 is worktree isolation, and its caveat is bigger than the rule:**

> **A fresh worktree does not carry gitignored files.** An agent isolated into a
> worktree to audit *text or code* is correctly isolated. An agent isolated into a
> worktree to audit **evidence** is looking at a checkout where that evidence does
> not exist, and *"it will report an honest, confident, empty result, the
> fail-open shape, produced by the very mechanism adopted to make verification
> trustworthy."*

That is §4 arm 3 arriving by a third route. The rule:

| Subject | Isolation |
|---|---|
| tracked content | worktree-isolate |
| run output, solver logs, any gitignored tree (§4 arms 3 and 4) | work in the **main checkout**, with exclusive scratch paths assigned by the dispatcher |
| unsure | *"have it print the count of evidence files it can see **before** it reports what it found in them."* |

**And a worktree can be cut behind its own subject.** Docket D19: the first agent
ever dispatched under R-ISOLATE got a worktree 18 commits behind, with the entire
author round it was sent to grade absent from the checkout. Same fail-open shape.
The repair is two lines in a brief:

    # dispatcher: state the subject SHA in the brief
    # agent, before executing anything:
    git merge-base --is-ancestor <subject-sha> HEAD || echo "WRONG TREE -- STOP"

### What git can and cannot tell you about who did what

**Do not try to establish independence from `git log`.**

| Quantity at `8cefb4e9` | Value |
|---|---|
| Commits since 2026-08-01 | 1,434 |
| Distinct author identities across them | **1** |

There is no `user.name` or `user.email` anywhere, so git synthesises one identity
from the unix user and hostname. The author field cannot discriminate between two
agents.

The mechanism that can costs one line appended before committing, with a fresh
token you **type** into the command yourself:

    python3 scripts/check_rung_attribution.py --emit-trailer --probe <a-typed-token> >> <msgfile>
    Lab-Agent: ip-172-31-43-247/<session>/-/agent-<hex>

Bare `--emit-trailer` emits the **session** form, which is byte-identical for
every agent of one chief and therefore grades AUTHOR for every sibling pairing.
The script says so in capitals at `scripts/check_rung_attribution.py:90`:

    TWO AGENTS DISPATCHED BY THE SAME CHIEF SESSION READ AS THE SAME AGENT.

That sentence is about the session field, and it is why `--probe` exists.

**The condition, stated exactly:** the token's **value must be present in the tool
call as the harness recorded it.** An unpredictable substitution fails not because
it contains `$(...)` but because the shell expands it *before* the harness writes
the call down, so the value the emitter searches for was never recorded. Typing
the token is a rule that is always safe rather than a description of the
mechanism: a `$(echo <literal>)` probe resolves, because the literal reaches the
record.

| Probe form | Result |
|---|---|
| typed literal, 12 to 128 chars | rc 0, agent form emitted |
| `$(echo <literal>)` | rc 0, agent form emitted; the literal reached the record |
| `$(od -An -N8 -tx1 /dev/urandom ...)` | **rc 3**, nothing emitted |
| a token shorter than 12 characters | **rc 3**, nothing emitted, malformed |

**Gate on the exit code, not on the message file.** The refusal goes to
**stderr** and stdout is empty: split-stream measured at **stdout 0 bytes, stderr
621**. So the `>> <msgfile>` redirect appends nothing at all on a failed probe,
silently, and the commit lands with no identity while looking exactly like a
commit whose emitter ran fine. `rc=$?` is the only thing that tells you which
happened, and it must be captured directly rather than through a pipe, since a
pipe replaces the status.

**Exit 3 has more than one cause**, and reading it as "I must have used `$(...)`"
sends you after the wrong bug. The emitter rejects a **malformed** probe before it
ever looks at a transcript, on the stated grounds that *"a short token matches
transcripts by accident, and an accidental match names the wrong agent"*. The
token must be 12 to 128 characters of `[A-Za-z0-9._:-]` starting alphanumeric.
**Read the refusal text, which says which of the two happened.**

Two limits survive the repair. The chief session itself cannot probe, having no
per-subagent transcript of its own. And nothing before the anchor `e933e31b` is
attributable: *"backfill is impossible"*. The `--tag` slug is recorded, printed,
and never decides a verdict.

### A per-agent handle is a DIFFERENCE, not independence

Chief ruling, `docs/DOCKET.md` D240. A green attribution run is **not** an
independence warrant and **no ladder rung may cite one as its warrant.** Three
measured reasons:

| Reason | Measurement |
|---|---|
| **The verdict is asymmetric.** `NON-AUTHOR` is informative; `AUTHOR` is what almost every pair returns out of **absence of data** | 6 of 108 commits since the anchor carried a per-agent handle, so 15 of 5,778 commit pairs, **0.26%**, could be asked the agent-granularity question at all |
| **A `fork` subagent defeats the measure by construction** | a fork inherits its parent's **entire conversation**, having read everything the parent read, and still carries its own `agent-<hex>`, so it grades `NON-AUTHOR` |
| **Existence is unverifiable from a clone, permanently** | a fresh `git clone` contained no `subagents` directory and no `agent-<hex>.jsonl`; `--probe ... --transcripts <clone>` exited 3 |

`docs/AGENT_ATTRIBUTION.md`: *"a different agent by this measure, having read
everything the parent read. R-ISOLATE's spirit is not satisfied by dispatching a
fork, and the check cannot see the difference."* The tool prints the same caveat
on every run. **So when you need a grader that has not read the author's
reasoning, dispatch a FRESH agent, not a fork.** Nothing in the trailer, the
transcripts, or the tree records dispatch **kind**, so no later reader can recover
which one you dispatched. The choice is unauditable after the fact, which is why
it has to be made correctly at dispatch time.

There is also a half of R-ISOLATE the check cannot see at all: the rule requires a
grader to **execute** the claim rather than read the author's summary of it, and a
grader that read a summary and a grader that ran the code commit identical bytes.
Rung-level independence therefore rests on the **untracked dispatch record**, and
the attribution run is one of two necessary conditions rather than a warrant.

---

## 11. When you find something wrong

It goes in `docs/DOCKET.md`. The docket exists because of a real tension: *"a rung
that absorbs every new finding never closes; a rung that drops them is worse."*
Its header: **"This is a queue, not an archive. An item leaves it by being
executed or by the owner ruling it out, never by ageing."**

**The ID rules, which are absolute:**

- IDs are append-only and stable. **Nothing is ever renumbered.**
- Take a fresh ID. **Check the highest in use first, in HEAD *and* in the working
  tree**, because a concurrent session's row may not be committed yet.
- On a collision, both writers keep their text and the **later** one takes the next
  free ID. The earlier one is not moved.
- Withdrawn IDs are struck in place and kept, never reused.

Sections are lettered:

| Letter | Section |
|---|---|
| `A` | the owner's |
| `B` | machinery |
| `C` | memory |
| `D` | rung residuals, the bulk |
| `E` | standing task items |
| `F` | repo professionalization, blocked by design |
| `G` | naval campaign |

Sub-items take a letter suffix: `D8b`, `B3a`, `G1c`.

| Docket reading at `8cefb4e9` | Value |
|---|---|
| Rows across all lettered sections | 371 |
| Highest `D` in the working tree | D334 |
| File length | 699 lines |

IDs race several per hour, so **nothing on this page is a usable ID**.

**The recipe: the sort must be numeric, on the number alone.** A `sort -u` over
`| D<n>` sorts **lexically**, so `D99` sorts after `D146` and a reader following
it allocates an ID taken weeks ago, colliding silently with an existing row rather
than with the concurrent writer they were warned about.

```bash
# highest D in HEAD, and in the working tree; they can differ
git show HEAD:docs/DOCKET.md \
  | command grep -oE '^\| \*{0,2}D[0-9]+' | command grep -oE '[0-9]+' | sort -n | tail -1
command grep -oE '^\| \*{0,2}D[0-9]+' docs/DOCKET.md \
  | command grep -oE '[0-9]+' | sort -n | tail -1
```

Do not hand-type the append. Write it with something that **asserts the ID is
free at the moment of writing**, because checking and writing are two moments and
four IDs have been allocated by another session in the ninety seconds between
them.

**What a row must contain**, from the docket header and from what every good row
in it does:

| # | Element |
|---|---|
| 1 | **The finding, stated so it can be wrong.** Bold the claim |
| 2 | **Where it was found**: a file, a line, a commit, a timestamp. Named, opened |
| 3 | **What it would take to settle it**, concretely, including "no compute needed" |
| 4 | **What it cannot see.** The best rows all carry this |
| 5 | **Who owns it**: fleet, chief, or the owner |

There is a live dispatch-claim block in section B: **claim an item there before
you dispatch work on it**, because two chief sessions reading the same directive
will otherwise dispatch the same agent twice.

`scripts/docket_citation_guard.py` runs over this. It exists because the dangerous
defect is not a dangling citation: it is a citation to an ID you have not filed
yet, which silently comes **true** when another session allocates that number for
something else.

---

## 12. Worked example, executed end to end

**The task.** §4 claims `git grep -I` has a blind spot created by
`.gitattributes`. Measure it, control it both ways, and decide whether it is
material.

### Step 1: state the frame before measuring

Repository `/home/ubuntu/Certonomous` at `8cefb4e9`. Population: tracked files
only. "Binary" means *git's* opinion via `git check-attr binary`, not the bytes.
"Text" means no NUL byte, and the byte window is stated with the answer.

### Step 2: measure

```bash
git ls-files -z | xargs -0 -r git check-attr -z binary --
```

The result is the table in §4: 981 files carrying `binary: set`, of which 12 are
NUL-free in their first 8,000 bytes and 11 across the whole blob.

### Step 3: three controls

`LESSONS.md` L-84 requires all three; a positive control alone is half a control.

| Control | Command | Result |
|---|---|---|
| **Positive**: a literal provably present in a marked file | `command grep -c '0\.056647' demo-surfaces/motorBike.obj` | 3 matches |
| the same file through the sweep | `git grep -lI '0\.056647' -- demo-surfaces/motorBike.obj` | **exit 1, nothing seen** |
| recovered with `--text` | `git grep -lI --text '0\.056647' -- demo-surfaces/motorBike.obj` | the file, exit 0 |
| **Must-not-match**: the same literal in an ordinary tracked file, to prove the miss is specific to the mark rather than a broken pattern | `git grep -lI '0\.056647' -- docs/PRODUCT_LIST.md` | the file, exit 0 |
| **Boundary**: a genuinely binary marked file must *stay* skipped, or the finding would be "git grep skips binaries", which is correct behaviour | `b'\0' in open('demo-output/Gui_issue.png','rb').read(200)` | `True` |

The finding is therefore scoped to exactly the text-but-marked files, and no
wider.

### Step 4: re-derive rather than trust the instrument's silence

Does the blind spot cover anything claim-bearing? Open the files.

    $ command grep -aoE '\(([^)]{3,60})\) *Tj' \
        demo-output/website/certificates/b52-certificate-current.pdf | head -4
    (CERTONOMOUS) Tj
    (CERTIFICATE OF AUTONOMOUS SOLVE) Tj
    (Mission geometry-study-b52) Tj
    (GEOMETRY) Tj

The certificate PDFs are uncompressed: their claim text is plain ASCII that GNU
`grep` reads directly. Five of the lab's sealed product certificates, its most
claim-bearing artefact, are invisible to every `git grep -I` sweep in this
repository. That makes the blind spot material.

### Step 5: state what it cannot see

This measurement cannot see whether any past sweep actually missed a live claim
in those files, which is a history question rather than a mechanism question;
whether the compressed PDFs elsewhere carry claims a `--text` sweep would still
miss, since compression defeats `grep` regardless of the mark; or the same class
of mark in arms 3 and 4, which `git grep` never reaches at all.

### Step 6: file a docket row

Check the highest ID **first**, and check it in both frames, with the numeric sort
of §11. Then write the row with something that asserts its own ID is free. A
guarded append has fired in practice: between checking the highest ID and writing
the row about ninety seconds later, another session appended four rows, and the
assertion refused rather than producing a duplicate ID.

### Step 7: commit

    git add -- <paths>
    git commit -F <msgfile> -- <the same paths>
    git log --oneline -1

On `docs/DOCKET.md`, use the private-index form of §9 item 8 instead, and do the
write-back.

---

## 13. Limits: what this handbook does not establish

Stated rather than omitted, per §6.2: a thing not checked is UNKNOWN, and UNKNOWN
does not get filed beside the passes.

1. **The full `lab_check.py` tier was not run at this frame.** The `--list` and
   `--no-tests` tiers were run at `8cefb4e9` and their figures are in §7. No
   figure is offered for the full tier or for the test suite's collection count,
   rather than carrying an older one forward.

2. **No clean-box timing exists for any tier.** Every measurement was taken while
   other agents were working the box. The wall figures are measurements of this
   box under load.

3. **Solver and scoring behaviour is read from records, not executed.** No solve
   was run and no scoring call was made, under §5. Everything about OpenFOAM and
   DAFoam execution here is second-hand by design.

4. **The closure figures in §1 are re-derived, but locally.** They come from
   `sdk/scripts/probability_of_rank.py` joined to
   `demo-output/website/closure_challenge_round5_qcr.json`, and every entrant row
   reproduces its published overall. This is local scoring against a board
   retrieved 2026-08-11T23:33Z. It is **not** an official placement, and nothing
   has been submitted.

5. **Whether the blind-spot files ever hid a live claim** is unmeasured. §12
   measures the mechanism, not its history.

6. **The `git status` staleness trap was not reproduced here.** It is recorded
   from `LESSONS.md` and `ESCALATION_CHARTER.md` §9.6b, whose text was verified,
   and it needs a race that cannot be scheduled.

7. **§3's claim that root's cron gets the real GNU tools is inference.** The
   support is that `journalctl -t auto-stop` carries
   `ALIVE: Claude session transcript written within 30min (<path>)`, which is the
   `-newermt` clause returning a hit, and cron does not source the interactive
   profile where `find` is redefined. Treat it as strongly supported inference,
   not measurement.

8. **Whether the installed gate's blindness has ever let the box power off
   mid-session** is a history question. §2's mechanism was verified by reading
   `/usr/local/bin/auto-stop.sh` directly; whether it has fired was not.

9. **§10 was written from the supervision and escalation charters, R-ISOLATE and
   D19.** The delegation doctrine of 2026-07-26 is cited by the supervision
   charter and was not opened, so anything it assigns beyond the nouns §4 of that
   charter lists is not represented here.

10. **A quotation you cannot locate should be treated as absent.** One line
    offered during drafting as `LESSONS.md` L-75, reading *"a number is defined by
    its frame, its filter, and the moment it was taken"*, does not exist in this
    corpus. L-75 is the `grep`/`--ignore-files` lesson. It was cut rather than
    paraphrased into place. Do the same, and say so.

---

## 14. Known-open state: read the sources, not this paragraph

Anything enumerated here would be stale within hours. Three places carry the
truth.

**The verification ladder.**
`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md`. Sixteen
pre-registered rungs in four passes (re-derivation, adversarial, cold
reproduction, structural), gating the closure entry. A rung is a named criterion
with a declared closing condition, graded by a **non-author**, shipping an
evidence record. Its green rule is a fixed point rather than a clean sweep: every
rung PASS, **and** a full re-run over the previous round's text introducing zero
new failures, measured by someone who wrote none of it. Its own status line reads
**"STANDING PROTOCOL, EXECUTION PARKED."**

**The ladder is not green.** Its live block carries a table of what is still open
and closes *"Nothing here marks any rung green, and this pass has no standing
to."* Go and read that block; do not take a rung list from here or from anywhere
else. Several agents edit that file concurrently and it carries struck entries and
dated amendments that disagree with each other by design, which is a grader's job
to resolve rather than a reader's. The one durable statement is that the gate is
shut.

**The docket.** `docs/DOCKET.md`. Note honestly that the `D` table has **no status
column** by design, so open-versus-closed cannot be counted mechanically without
inventing a frame. The header's rule is the reading: an item that has not been
executed or ruled out is still in the queue.

**The lab check.** `python3 scripts/lab_check.py --no-tests` returned FAIL at
`8cefb4e9`, and §7 explains why that is the correct output.

**What is validated, and against what.** `docs/VALIDATION_INVENTORY.md`, one row
per gate or rung across every campaign. Like everything else in this section it
is a frame rather than a constant: it states the commit it was taken at, and two
commits landed while it was being written.

---

## 15. Your first hour, as a checklist

1. `touch .autostop-hold`, and confirm the journal is honouring it (§2).
2. `type grep` and confirm it is a function. Prefix everything with `command`,
   and use `/usr/bin/find` (§3).
3. `git status`, to see who else is mid-write before you touch anything (§8.3).
4. `git diff --cached --stat`, and **stop** if it is not empty and not yours
   (§9 item 9).
5. `python3 scripts/lab_check.py --no-tests`, to see the lab's real state, FAIL
   and all (§7).
6. Read `docs/VALIDATION_INVENTORY.md`, then `docs/charters/README.md`, then
   `VERIFICATION_CHARTER.md` §1, §2a, §9. The inventory first, because it tells
   you which of this lab's numbers are checked against the world and which are
   only checked against the lab.
7. Read the docket header rules, then skim the last ten `D` rows for house style
   (§11).
8. Sweep all four arms before you claim any count (§4).
9. When you commit: `git add -- <paths>`, then
   `git commit -F <msgfile> -- <the same paths>`, then `git log --oneline -1`
   (§8). **Read the SHA it prints**, and if your message claims an anchor, check
   the anchor is that SHA and not its parent (§8.1).
10. Before you dispatch anything, read §10, and **claim the item in
    `docs/DOCKET.md` §B before the agents exist** (§9 item 1).
11. Before you run `pytest` by hand, purge `__pycache__` (§7). A green suite over
    stale bytecode is the cheapest wrong answer in this repository.


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/Paper3.pdf` | `docs/papers/verification_validation/oberkampf_roy_2011_verification_validation.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.
