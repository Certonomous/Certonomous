# Queue entry — HOST SCOPE

**Status: SPEC, FROZEN AT ITS COMMIT. No code exists yet.** This document is written
**before** the implementation precisely so the implementation cannot be shaped to pass its
own test (`CLAUDE.md` rule 2's discipline applied to tooling). The commit that lands this
file is the freeze; the code that follows cites that sha, and any departure from what is
written here is a dated amendment at the foot, never an edit above it (rule 6).

**Owner:** cfd-supervisor (`scripts/queue_entry_check.py` is cfd tooling).
**Provenance:** the ordering defect was found by the cfd-supervisor on 2026-08-28 by
reading `scripts/queue_runner.py::tick()`. Every file:line, count and similarity figure in
this document was **re-verified against the code and the tree by cfd lane SPEC** the same
day; three statements in the supervisor's framing were falsified on that check and are
corrected in §2a rather than carried forward. Sibling precedents:
`QUEUE_ENTRY_TEAM_BINDING.md` (spec-first, amended where implementation falsified it) and
`QUEUE_ENTRY_VALIDATOR_RULINGS.md` (R-AGE-CWD, which created the `EXEC` clause this
document scopes).

**This document adds no gate, no threshold, no cap and no label.** It **narrows** the
conditions under which `scripts/queue_entry_check.py` refuses, and it **adds a new
reporting obligation** — `NOT EVALUATED` — that did not previously exist. A narrowing is
the dangerous direction, which is why §8 carries a negative control before it carries a
positive one.

> **REFERRAL, NOT A DECISION — for the chief.** `docs/standards/QUEUE_ENTRY_STANDARD.md`
> enumerates the entry contract; `host` is a field the runner reads
> (`queue_runner.py:707`) and the validator does not. Whether **narrowing** a validator
> refusal is a tooling ruling of the kind `QUEUE_ENTRY_VALIDATOR_RULINGS.md` already
> carries, or an **amendment to that standard** — which is Sanaa's alone — is not cfd's
> call to make for the lab. `EXEC` itself landed by the rulings route and is the live
> precedent. **This document is written; the code does not land until that is ruled.**

---

## 1. The invariant

**A clause that reads the LOCAL filesystem on behalf of a path the entry supplies MUST NOT
produce a refusal for an entry declared to run on ANOTHER host.** For such an entry the
clause is **NOT EVALUATED**, and `NOT EVALUATED` is reported in its own channel, distinct
from a pass, on every output path the tool has.

Formally: for an entry `e` with `host(e)` outside `{absent, "", "local", "localhost",
os.uname().nodename.lower()}` — the exact set `queue_runner.py:708` already uses — the
host-sensitive clauses enumerated in §3 contribute **zero strings** to `validate()`'s
failure list and **one string each** to its unevaluated list.

## 2. Why — the defect, and it is an EVICTION, not a misread number

The consequential fact is an **ordering** in `scripts/queue_runner.py::tick()`, verified
line by line:

| line | code | effect |
|---|---|---|
| `:695` | `entry, fails = qec.load_entry(path)` | the file is parsed |
| `:702` | `fails = qec.validate(entry, REPO, path)` | **every clause runs, including the host-sensitive ones** |
| `:703-705` | `if fails: move_refused(path, fails, log); any_refused = True; continue` | **the file is physically moved** to `<team>/refused/` (`move_refused`, `:444-451`, `shutil.move` at `:448`) |
| `:707` | `host = str(entry.get("host", "local")).strip().lower()` | the host field is read **for the first time** |
| `:708-710` | `if host not in (...): log(f"SKIP ...")`; `continue` | the foreign host is excused |

**Validation and the physical move both complete before the host clause can excuse the
entry.** So a false refusal here is not a misread number that a reader can discount later:
it **evicts a good entry from the queue**, writes a `<CASE_ID>.REFUSED.txt` beside it
naming a cause that is not the entry's fault, and the entry never launches on the box that
could have run it.

`scripts/queue_entry_check.py` contains the string `host` **zero times** — verified by
reading that one named file. The validator has no way to know a host exists.

**The trigger condition, and it is not hypothetical.** The disarm today is a property of
**tree layout**, not of the code: every `cwd` any cross-host entry has ever carried lies
under `/home/ubuntu/Certonomous/`, a path mirrored at the same location on both boxes, so
`Path(cwd).is_dir()` returns True here and `EXEC` stays quiet. The moment an entry names an
**instance-local** tree the disarm is gone. The lab occupied exactly such a path the night
of 2026-08-27: the GPU instance's `~/laneW_freeze005` freeze tree, which does not exist on
this box. An entry pointing there, dropped in a team drop path here, is refused and moved
on the next tick.

**A guard whose safety rests on nobody having yet used a directory is not a guard.**

## 2a. THREE STATEMENTS IN THE FRAMING THAT WERE FALSIFIED ON CHECK

Recorded here, at the head of the spec, because a specification built on an unchecked
premise inherits the premise's error and hides it under formatting.

1. **There is no `check_age_guard_cwd()`.** The function is `check_age_guard()`, defined at
   `queue_entry_check.py:285`; its local-filesystem reads are at `:309`, `:310`, `:316` and
   `:317`. The name in the framing does not exist in the file.

2. **The "further local `Path(cwd).is_dir()` sites at ~:480-498" are NOT production
   sites.** They are `_mutant_age_guard_without_scan` (`:478`, read at `:483`) and
   `_mutant_age_guard_pointed_at_absence` (`:488`, read at `:496`) — **selftest mutants**,
   declared at `:466-471` as *"never registered in CHECKS; they are handed to validate() as
   a one-off override and never reach a live entry"*, and confirmed absent from the `CHECKS`
   table at `:414-422`. They are host-sensitive **as code**, are exercised only against
   planted controls, and require no repair. Counting them as live sites would have produced
   a repair to dead code.

3. **`COMMIT-EXISTS` and `PREREG-AT-COMMIT` are NOT host-independent**, contrary to the
   framing's "presumably". Both consult the **local git object store** —
   `_git(["cat-file","-e", f"{sha}^{{commit}}"], root)` at `:252` and `:274`, and
   `_git(["cat-file","-e", f"{sha}:{path}"], root)` at `:276`. An object store is **per-host
   state**, not a property of a sha. A pre-registration committed on the GPU instance and
   never fetched here does not exist here, and both clauses would refuse it. §3 treats them
   as host-sensitive-in-principle and §4 rules that they are nonetheless **evaluated for
   every host**, with the residual named — which is a different and stronger answer than
   the one an unexamined "presumably" would have produced.

The three ordering line numbers in the framing — `:702`, `:704`, `:707-709` — are **exactly
right** and are reproduced in §2's table with `:703` and `:705` filled in.

## 3. THE COMPLETE ENUMERATION — every site in `queue_entry_check.py` that touches the local filesystem

Read off the one named file, top to bottom. "Entry-supplied" means the path came from the
entry's JSON content; "caller-supplied" means it came from the glob or the command line.

| file:line | site | path origin | touches local FS | **host-sensitive?** | ruling |
|---|---|---|---|---|---|
| `:133` | `repo_root()` → `_git(["rev-parse","--show-toplevel"])` | caller (this file's own dir) | yes (git) | **No** | locates the repo we are running in; there is only one |
| `:165` | `containing_team_dir()` → `Path(entry_path).resolve().parent` | caller (the glob) | yes (`resolve()` follows symlinks) | **No** | the entry FILE is on this box by definition — we are reading it |
| `:171-244` | `check_schema()` | — | **none** | **No** | pure dict and regex inspection; opens nothing |
| `:252` | `check_commit_exists()` → `cat-file -e <sha>^{commit}` | entry (`prereg_commit`) | yes (git object store) | **In principle YES** | **evaluated for every host** — see §4.3 and the named residual |
| `:274`, `:276` | `check_prereg_at_commit()` → `cat-file -e <sha>` then `<sha>:<prereg_path>` | entry (`prereg_commit`, `prereg_path`) | yes (git object store) | **In principle YES** | **evaluated for every host** — §4.3 |
| `:309`, `:310` | `check_age_guard()` → `Path(cwd)`, `target.is_dir()` | **entry (`cwd`)** | **yes (working tree)** | **YES** | **NOT EVALUATED for a foreign host** |
| `:316`, `:317` | `check_age_guard()` → `target.iterdir()`, `child.is_dir()` | **entry (`cwd`)** | **yes (working tree)** | **YES** | same clause, same ruling |
| `:348` | `check_cwd_launchable()` → `Path(cwd).is_dir()` | **entry (`cwd`)** | **yes (working tree)** | **YES** | **NOT EVALUATED for a foreign host** |
| `:359-366` | `check_ranks()` | — | **none** | **No** | pure integer comparison |
| `:369-412` | `check_team_binding()` | caller (via `containing_team_dir`) | yes, via `:165` | **No** | compares the entry's own field to its own directory; both are here |
| `:483`, `:496` | the two AGE-GUARD **mutants** | entry (`cwd`) | yes | **not live** | selftest-only (`:466-471`); not in `CHECKS` (`:414-422`); no repair |
| `:524` | `load_entry()` → `path.read_text()` | caller | yes | **No** | reads the entry file itself |
| `:547` | `ast_self_check()` → `Path(__file__).read_text()` | the instrument | yes | **No** | reads its own source |
| `:1198` | `main()` → `Path(args.dir).is_dir()` | **operator (`--dir`)** | yes | **No** | a CLI argument naming a directory on the box the operator is typing on |
| `:1206` | `main()` → `repo_root(Path(__file__)...)` | the instrument | yes (git) | **No** | as `:133` |
| `:663-668`, `:748`, `:757`, `:849`, `:871`, `:903-909`, `:1060-1077`, `:1094` | selftest scaffolding | scratch | yes | **not live** | `--selftest` only; creates and reads its own `tempfile` trees |

**Two live clauses are host-sensitive in the consequential sense** — they read the
**working tree** at a path the entry supplies: `AGE-GUARD` and `EXEC`. **Two more are
host-sensitive in a weaker sense** — they read the **git object store**, which is also
per-host state: `COMMIT-EXISTS` and `PREREG-AT-COMMIT`. **Three are host-independent by
construction and this is stated with its reason, not assumed:**

- **`SCHEMA`** — inspects the parsed dict and nothing else. Every field it reads is
  transported inside the entry file. There is no filesystem call in `:171-244`. A schema
  verdict computed on this box is the same verdict on any box.
- **`RANKS`** — one integer comparison (`:362-365`). Same argument.
- **`TEAM-BINDING`** — reads only `entry["team"]` and the **entry file's own path**
  (`containing_team_dir`, `:153-169`). The entry file is on the box doing the reading, by
  the fact that the reading is happening. The invariant it enforces is a property of where
  the file sits, not of where the run will execute; a foreign-host entry sitting in the
  wrong team's drop path is exactly as self-contradictory as a local one.

## 4. WHAT A HOST-AWARE VALIDATOR DOES — the three candidates, and the ruling

### 4.1 The candidates

- **(a) SKIP the host-sensitive clauses and report them as NOT EVALUATED** — never as
  passed.
- **(b) REFUSE TO GRADE AT ALL** — a distinct third outcome for a foreign-host entry;
  neither accepted nor refused.
- **(c) EVALUATE THEM OVER SSH.**

### 4.2 RECOMMENDED: (a). And (c) is refused first, because it is refused on a fact

**(c) is REFUSED.** `queue_runner.py:29` states, of the runner, *"It never dispatches to
another host"*, and `:27-28` states that the only git it runs is *"the validator's
read-only allowlist"*. The validator's own opening docstring (`:1-17`) says the only child
process it ever starts is `git`, in a read-only subcommand allowlist enforced by `_git()`
(`:112-129`) which refuses anything outside `{cat-file, rev-parse, ls-tree}` by a `raise`
rather than by convention. **Adding ssh does not extend the validator; it changes what the
validator IS** — from a passive local reader with an enforced process allowlist into a
thing that opens network sessions to other machines and executes there. That is a different
instrument with a different threat surface, a different failure mode when the remote is
down or slow, and a different answer to "what could this run while nobody is watching",
which is the question the docstring's first section exists to answer. It also introduces a
new way to be wrong that is worse than the defect: **an ssh that fails for a network reason
returns the same "cannot see the directory" as an ssh that succeeds and finds nothing**,
so the repaired clause would refuse good entries on transient network conditions. Refused.

**(b) is REFUSED, and the reason generalises.** A third outcome sounds honest and is
operationally worse. Both call sites are binary: `queue_runner.py:703` is `if fails:` and
`queue_entry_check.py:1213` is the same shape. A third outcome must therefore be
encoded either as a failure — which reproduces the eviction this spec exists to stop — or
as an absence of failure, which is (a) with extra ceremony. Worse, (b) throws away the
**host-independent** clauses at the same time: an entry with a malformed `cost_basis`, a
missing `prereg_commit`, a shell-string `launch_cmd` or a `team` contradicting its
directory would be **ungraded** merely because it names another box. Those defects are
detectable here, are permanent properties of the file, and are exactly what a validator is
for. **A foreign host is a reason not to look at this box's filesystem. It is not a reason
not to read the file.**

**(a) is ADOPTED.** It is the only option that keeps every clause that can be correctly
evaluated here, drops exactly the clauses that cannot, and — critically — **says which
ones it dropped**. Its whole risk is that a skipped clause is mistaken for a satisfied one,
and §5 exists to make that mistake unavailable.

### 4.3 The object-store clauses stay evaluated — the narrow ruling, with its residual named

`COMMIT-EXISTS` and `PREREG-AT-COMMIT` are host-sensitive in principle (§2a item 3) and are
nonetheless **evaluated for every entry, including a foreign-host one.**

**Why.** These two clauses are the mechanical half of `CLAUDE.md` rule 2 — they establish
that the freeze cites a sha that exists and a document that exists at it. Skipping them for
a foreign-host entry would remove the freeze guard from **precisely the runs the lab cannot
watch**: those executing on another box. That inverts the safety argument. And the box
holding the canonical repository is the right place to answer "does this freeze exist" — a
freeze verifiable only on the machine that made it is not a lab freeze.

**NAMED RESIDUAL, stated here rather than discovered later by whoever it bites.** A
pre-registration committed on the other instance and **not yet fetched into this box's
object store** will draw a `COMMIT-EXISTS` refusal here, and that refusal **evicts the
entry** under the §2 ordering. This is a real false refusal and it is being accepted, not
overlooked. Mitigation is procedural and belongs in the enqueue procedure, not in this
clause: **the freeze is fetched into this repository before the entry is filed** — which is
what "committed before compute" already means when the lab has one canonical tree.
Referred to the cfd-supervisor as a follow-up in case the two-instance topology becomes
routine; **not fixed here, because fixing it means making the freeze guard host-conditional,
which is a change to the invariant and not to its implementation.**

## 5. NOT EVALUATED IS NOT PASS — the exact channel

This is the load-bearing section. A skipped check silently reported as a pass is the defect
this lab keeps finding; a repair that produces it is worse than the defect it repairs.

### 5.1 What `validate()` returns, and what it now requires

```
def validate(entry, root, entry_path, unevaluated, checks=None, require_binding=False) -> list[str]
```

- **The return type does not change.** It stays `list[str]` of failure strings. This is not
  a style choice, it is forced: both call sites test `if fails:`, and returning a
  **2-tuple** would make that test **always true** — every entry silently refused, with no
  exception raised anywhere. A signature change that turns a truthiness test into a
  tautology is a catastrophe that prints nothing. **Do not return a tuple.**
- **`unevaluated` is a POSITIONAL, REQUIRED parameter**, a mutable `list[str]` the caller
  supplies and the validator appends to. It is **never** given a default. This follows
  `QUEUE_ENTRY_TEAM_BINDING.md` §5 P2 exactly: a caller that cannot receive the
  not-evaluated report raises `TypeError` **at the call**, loudly, rather than discarding
  it. A default of `None` is the silent skip this spec exists to forbid.
- Each skipped clause appends **one** string, opening with the literal token
  `NOT EVALUATED:` followed by the clause name, so the string names its own cause exactly
  as every failure string already does (`:139-141`):

  ```
  NOT EVALUATED: EXEC -- entry declares host='ip-172-31-44-162' which is not this box
      (ip-172-31-43-247). EXEC reads the LOCAL filesystem (queue_entry_check.py:348) and
      cannot see that host's tree. This clause was NOT CHECKED. It is not satisfied; it is
      unknown. Check it on ip-172-31-44-162.
  ```

  and the same shape for `AGE-GUARD`, citing `:309-317`.

**`NOT CHECKED` over `NOT BOUND` is the same wording ruling `QUEUE_ENTRY_TEAM_BINDING.md`
amendment 1 §3 already took**, for the same reason: `NOT BOUND` would describe the entry's
state and `NOT CHECKED` describes the limit of our knowledge, and the planted-zero
principle is about knowledge. The token here is `NOT EVALUATED` and the body says `NOT
CHECKED`; both are deliberately not the word `pass` and not the word `ok`.

### 5.2 What the CLI prints

The per-entry verdict token for an entry with a non-empty `unevaluated` list is
**not the bare `ACCEPTED`.** It is:

```
ACCEPTED [HOST-SCOPE: 2 clause(s) NOT EVALUATED] <path>
```

followed by the enumerated block, one clause per entry, indented. **rc stays 0** — the
entry is legitimately launchable on its own host and refusing it here would be the eviction
again. The count is in the verdict line itself, so a reader skimming only verdict lines
cannot see a bare `ACCEPTED` for an entry whose launchability was never checked. Per the
instrument's own rule at `:37-42` and the shape already used at `:1218-1226`, the line is emitted **from inside the branch that
computed the count**, so deleting the reporting deletes the claim rather than leaving the
claim behind.

### 5.3 What the runner logs

At `queue_runner.py`, after `validate()` returns and **before** the `if fails:` branch, the
runner emits **one log line per unevaluated string**, prefixed `NOT-EVALUATED`, naming the
path. This is unconditional on the outcome: an entry can be both refused (by a
host-independent clause) and carry unevaluated clauses, and the reader needs both. The
existing `SKIP` line at `:709-710` is **kept, unchanged**; the two are different facts —
`SKIP` says the runner will not launch it here, `NOT-EVALUATED` says the validator did not
check part of it here — and collapsing them would lose the second.

### 5.4 The permitted edit to `queue_runner.py`

Following the precedent of `QUEUE_ENTRY_TEAM_BINDING.md` amendment 1 §1, which was written
narrowly and then had to be amended: the changes permitted in `scripts/queue_runner.py` by
this spec are **exactly two**, and the second is stated up front so no amendment is needed
for it:

1. at `:702`, one additional argument — the `unevaluated` sink list, constructed
   immediately above the call;
2. immediately after `:702`, a loop emitting one `NOT-EVALUATED` log line per element.

**No new branch, no new state, no reordering, no change to `move_refused` routing.** Any
further edit to that file is outside this spec and requires its own dated amendment.

## 6. SHOULD THE RUNNER'S ORDERING ALSO CHANGE? — argued both ways, and NO

**The case FOR moving the host check above `validate()` (`:707-709` before `:702`).** It is
one move of three lines and it kills the eviction outright, with no signature change, no
new parameter and no new output channel. It is the smallest possible diff, and small diffs
to a daemon are worth something on their own.

**The case AGAINST, which prevails, in three parts.**

1. **It throws away the checks that DO work.** A foreign entry would never be
   schema-validated on this box at all. A malformed foreign entry — a `launch_cmd` written
   as a shell string, an abbreviated `prereg_commit`, a `cost_basis` that omits *"not
   measured"*, a `team` contradicting its directory — would sit in the drop path
   **indefinitely and silently**, skipped every tick with a message about hosts that says
   nothing about the malformation. The queue would accumulate broken entries that read as
   merely waiting. **Compared against the alternative failure — a well-formed foreign entry
   evicted to `refused/` with a written reason — the eviction is LOUD and the silent
   accumulation is QUIET, and this lab's whole method prefers a loud wrong answer to a
   quiet one.** But (a) delivers neither, so the comparison only decides the fallback.

2. **It cannot fix the CLI, which is where the check is supposed to bite.** The team
   READMEs and `QUEUE_ENTRY_TEAM_BINDING.md` amendment 1 §2 both direct a supervisor to run
   `queue_entry_check.py` **before** dropping. A supervisor validating a GPU-instance entry
   by hand gets a false `EXEC` refusal, and no reordering inside `queue_runner.py` touches
   that. This is the same argument `QUEUE_ENTRY_TEAM_BINDING.md` §3 used to reject
   enforcing team binding in the runner: **the check must be right at the moment it can
   still prevent the drop.** A defect that survives in the tool a human runs has not been
   fixed.

3. **Reordering leaves the validator still wrong and merely unreachable on one path.** The
   host-blindness would remain in the code, disarmed by call order in one caller. The next
   caller — a supervisor, a script, a future runner — re-arms it. §1's invariant is a
   property of the validator and belongs in the validator.

**RECOMMENDATION: the runner's ordering does NOT change.** `:702` → `:703-705` → `:707-709`
stays exactly as it is. The two permitted edits are those in §5.4.

**The failure I prefer, stated plainly since it was asked for.** If forced to choose
between the two failures the reordering trades — a well-formed foreign entry **evicted**
versus a malformed foreign entry **silently accumulating** — I prefer the eviction, because
it writes a `REFUSED.txt` naming a cause and a human finds it. But this spec is not forced
to choose: (a) evicts neither, and refuses the malformed one loudly.

## 7. A SECOND DISARM, MEASURED, THAT THE FRAMING DID NOT NAME

The two foreign-host entries that exist sit in `verification/queue/ansys-verification/held/`.
`list_entries()` at `queue_runner.py:433-441` globs `d.glob("*.json")` on the **team
directory only** — `:439`, non-recursive. **`held/` is never globbed.** So the daemon has
not merely failed to refuse these two entries; it has never seen them.

This strengthens the latency finding rather than weakening it. The defect today is disarmed
**twice over** — once by `held/` not being globbed, once by the mirrored repo path making
`is_dir()` true — and **neither disarm is a property of the validator.** Both are facts
about where files currently sit. Moving one of those two entries into the drop path removes
the first; naming an instance-local `cwd` removes the second.

## 8. Controls — `--selftest`, planted, with mutations that must flip

Per `CLAUDE.md` rule 3 and `COMMIT_INTEGRITY_STANDARD.md` **G1** (*do not relax an
invariant to make a test pass; make the test exercise what production does*), every
end-to-end control below uses a queue root of **production's shape**,
`<scratch>/…/verification/queue/<team>/` — the shape `QUEUE_ENTRY_TEAM_BINDING.md`
amendment 2 made mandatory after a control passed vacuously on `c9root/cfd/`. Nothing real
is touched.

| # | control | plant | required outcome — the exact assertion |
|---|---|---|---|
| **H1** | **THE MANDATORY ONE: a cwd that exists ONLY on the remote host** | valid entry, `host: "ip-172-31-44-162"`, `cwd: "/nonexistent-remote-tree/<uuid>/laneW_freeze005"` — a path asserted absent locally by `Path(cwd).exists() is False` **in the control itself, before the call** | `validate()` returns a failure list containing **no** string starting `EXEC:` and **no** string starting `AGE-GUARD:`; **and** `unevaluated` has **len == 2**, one string containing `NOT EVALUATED: EXEC` and one containing `NOT EVALUATED: AGE-GUARD`, and each contains the declared host string |
| **H2** | **THE NEGATIVE CONTROL: the clause was not simply disabled** | the **same** entry dict with `host` **absent** (and, as H2b, with `host: "local"`, and as H2c with `host` set to `os.uname().nodename`) — identical absent `cwd` | `validate()` returns a failure list containing **exactly one** string starting `EXEC:` and containing the literal `cwd` value; `unevaluated` is **empty** (`len == 0`). All three of H2/H2b/H2c required — the host-equality set at `queue_runner.py:708` has three accepting forms and a repair that honoured only one would pass a single-form control |
| **H3** | **MUTATION OF H2** | the host-scope predicate forced to return "foreign" unconditionally | **H2 FLIPS** — the local entry stops drawing the `EXEC` failure. If it does not flip, H2 never tested the predicate |
| **H4** | **MUTATION OF H1 — the control that enforces §5** | the clause still skipped, but the `unevaluated` append **suppressed** | **H1 FLIPS** on its `len == 2` limb. This is the control that proves H1 read the **note** and not merely the **absence of a refusal** — without it, H1 cannot distinguish NOT EVALUATED from PASS, which is the exact confusion this spec exists to prevent |
| **H5** | **host-awareness is NARROW: the freeze guard still bites** | foreign-host entry, absent remote `cwd`, `prereg_commit = NONEXISTENT_SHA` (`:565`) | **REFUSED** — failure list contains a string starting `COMMIT-EXISTS:`. Proves §4.3's ruling is implemented and that "foreign host" did not become a blanket exemption |
| **H6** | **same, for the pure-dict clauses** | foreign-host entry with `prereg_commit` **absent**, `launch_cmd` a **string**, and `team: "closure"` while sitting in `<scratch>/…/verification/queue/cfd/` | **REFUSED** with **three** failures: one `SCHEMA:` naming the missing field, one `SCHEMA:` naming the argv list, one `TEAM-BINDING:` naming both `closure` and `cfd`. Proves a foreign host is not a reason not to read the file |
| **H7** | **BLIND CALLER REFUSES** | `validate()` called with the `unevaluated` argument omitted | raises **`TypeError`**; no silent pass, no default |
| **H8** | **MUTATION OF H7** | `unevaluated` given a default of `None` and the appends guarded | **H7 FLIPS** — the call succeeds and the notes vanish, proving H7 tested the loudness and not the happy path |
| **H9** | **END TO END THROUGH THE DAEMON — the eviction, or its absence** | H1's entry written into `<scratch>/…/verification/queue/cfd/`, one real `tick()` | the entry is **still at its original path**; `<scratch>/…/cfd/refused/` **does not exist**; `LAUNCH_LOG.tsv` unchanged; `tick()` returns `"HELD"` (not `"REFUSED-ONLY"`); and the runner log contains **both** the `SKIP` line naming the host **and** two `NOT-EVALUATED` lines naming `EXEC` and `AGE-GUARD` |
| **H10** | **MUTATION OF H9 — the defect, driven** | host-scope removed from the validator (the pre-repair behaviour, reintroduced as a registered mutant clause in the manner of `:488-501`) | **H9 FLIPS**: the entry **is** moved to `refused/`, `<CASE_ID>.REFUSED.txt` is written naming `EXEC`, and `tick()` returns `"REFUSED-ONLY"`. **This control is the demonstration that the defect is real end to end**, not an argument that it would be |
| **H11** | **`queue_runner.py` control 6's PLANT IS REPAIRED** | `:884-891`'s `good3 = dict(good)` currently inherits `cwd=str(case_dir)` from `:796`, a directory **created at `:796` and existing**. Repaired: `good3["cwd"]` set to a path asserted absent locally | control 6's existing assertion (`:891-893`: `r6 == "HELD"`, entry still at its path, `LAUNCH_LOG` line count unchanged) is **unchanged and must still hold** |
| **H12** | **MUTATION OF H11 — the old plant is shown to be blind** | control 6 run with its **original** existing `cwd` **and** the host-scope repair removed | control 6 **PASSES ANYWAY**. This is the finding stated as a control: **the plant, not the assertion, was the defect.** Control 6's assertion *can* fail in the direction that matters — if the host clause is deleted the entry launches and `r6 != "HELD"` — but its **plant** could never reach the EXEC path, so it was blind to the interaction between EXEC and the host clause. A control that cannot fail in the direction the clause exists for is not a control, and H12 is what makes that sentence a measurement |
| **H13** | **AST SELF-CHECK UNBROKEN** | the instrument parses itself (`:540-543`) | still **zero** `ast.Assert` nodes (L-332), and `queue_runner.py`'s own `_count_asserts()` (`:754-756`, asserted at `:767-768`) likewise zero |
| **H14** | **THE PRE-EXISTING CONTROL SET IS UNMOVED** | the full pre-repair control sets of both instruments, re-run after the change | `queue_entry_check.py --selftest` returns the **same count** of controls at rc 0 as before the change plus exactly the rows added here; `queue_runner.py --selftest` likewise. **A repair that quietly changes another control's outcome has changed a decision nobody reviewed** — the sorted check-name-plus-status sets are compared and must differ by nothing but the new rows, as `QUEUE_ENTRY_TEAM_BINDING.md` amendment 2 required of itself |

**H1 without H4 is not evidence.** H1 alone passes if the clause is skipped and nothing is
reported — which is the silent pass. The pair is the control.

## 9. Blast radius — MEASURED, 2026-08-28, not inherited

Measured by cfd lane SPEC by parsing every `*.json` under `verification/queue/`
recursively. **Not taken from any report**: a state reading has a shelf life.

| reading | value |
|---|---|
| this box's `os.uname().nodename` | `ip-172-31-43-247` |
| entries lab-wide carrying a `host` field | **4** |
| of those, declaring a **foreign** host | **2** — `ansys-verification/held/VMFLGPU001.json` and `held/VMFLGPU001-R2.json`, both `host: ip-172-31-44-162` |
| of those, declaring **this** box | **2** — `ansys-verification/launched/VMFL011-R3.json` and `launched/VMFL076-R2.json`, both `host: ip-172-31-43-247` |
| foreign-host entries whose `cwd` **exists locally** | **2 of 2** — both under `/home/ubuntu/Certonomous/verification/runs/ansys_verification/`, mirrored at the same path |
| foreign-host entries **in a globbed drop path** | **0 of 2** — both are in `held/`, which `list_entries()` does not glob (`:439`) |
| `refused/` directories existing under `verification/queue/` | **0** — `find verification/queue -maxdepth 2 -name refused -type d` returns nothing |
| entries ever refused lab-wide | **0**, by the line above |

**Therefore the defect is LATENT and no landed verdict is exposed.** It has never fired,
and it could not have: §7's double disarm. **The change refuses nothing currently queued
and invalidates no completed launch** — it only narrows, and §8's H2/H5/H6 are what
establish the narrowing did not become a hole.

**RE-MEASUREMENT IS MANDATORY.** This table dates from before the code was written. The
implementing lane **re-runs the sweep in the same shell invocation that lands the code**
and records the fresh counts in the commit message. Every team can write to the drop path
and the ansys team is actively filing GPU-instance work; a count that was two an hour ago
is not a count that is two now.

## 10. What this spec does NOT do

- It changes **no gate, no threshold, no cap and no label.** No pre-registration is
  amended; no verdict vocabulary word is added or retired; `PASS`/`GATE REACHED`/`GATE
  FAIL`/`NOT A RESULT`/`BLOCKED`/`PENDING` are untouched. `NOT EVALUATED` is a
  **validator-clause reporting token**, not a verdict, and it is deliberately not one of
  the six — it never appears on a result row.
- It does **not** make the validator dispatch to, contact, or read anything on another
  host. `_git()`'s read-only allowlist (`:105`, enforced at `:112-129`) is unchanged and no
  subcommand is added to it.
- It does **not** change the runner's decision order, its refusal routing, its
  round-robin, its GPU clause or its cap watch. §5.4 fixes the permitted edits at two.
- It does **not** relax `AGE-GUARD` or `EXEC` for a **local** entry by one condition —
  H2/H2b/H2c are the proof.
- It does **not** touch `enqueued_by`, for the reason `QUEUE_ENTRY_TEAM_BINDING.md` §8
  gives: every process on this box shares one Ubuntu identity, so a check on it would
  return PASS for any string an agent chose while looking like an authorisation control.
- It does **not** back-fill, re-grade or re-open anything already launched or refused.
  There is nothing to back-fill: zero entries have ever been refused.
- It sends nothing anywhere (`CLAUDE.md` rule 7).
