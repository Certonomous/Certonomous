# PENDING COMMIT -- case_protocol_freeze_hook :245 refusal-reason repair

> **STATUS: LANDED at `c185d7508`, 2026-09-11, by the verification supervisor.
> THIS RECORD IS CLOSED — DO NOT RE-LAND IT; a second landing would duplicate
> the commit. The original status is STRUCK below, not rewritten (CLAUDE.md
> rule 6). The closing addendum is at the foot.**

~~**STATUS: PREPARED, NOT COMMITTED -- blocked by this session's permission
classifier, reason [Modify Shared Resources], on `git update-ref
refs/heads/main`. Not retried, not routed around, not delegated to a peer.**~~

The block is a PERMISSION decision, not a failed check. Every check this work
had to pass, passed. Landing it requires either a Bash permission rule for the
ref update in this repository or Sanaa running the commit herself. No agent's
instruction to commit is that authorisation (CLAUDE.md rule 9), and asking a
peer session whose own `update-ref` calls are going through would be
cross-session permission laundering.

| field | value |
|---|---|
| target path | `scripts/case_protocol_freeze_hook.py` |
| pinned expectation | **206 insertions / 7 deletions / 1 file** |
| HEAD verified against | `5349795d3eb0c52bc384a8ac72521965b0665888` (re-derived at this write; the expectation held unchanged across `cc2a2e039`, `f9330964955babe3eb8ee55757a2783da6538a54` and this sha -- peer traffic never touched this path) |
| selftest, before | 24 checks, 0 failures |
| selftest, after | 41 checks, 0 failures under `python3`; 41 checks, 0 failures under `python3 -O` |
| pre-existing cases | all 24 labels still present and still passing (label sets diffed) |
| mutation controls | repair reverted -> 3 FAILED (both ARM A plants `expected True, got False`; ARM B anchor `expected 1, got 0`). Print-once latch defeated -> 2 FAILED (ARM C both plants `expected 1, got 2`). |
| bare asserts | 0 (`ast.Assert` node count 0) |
| decision logic touched | nothing -- no predicate, no exit code, no threshold |
| frozen instrument | `scripts/check_comparator_freeze.py` byte-identical to HEAD; not repaired here |
| supervisor review | diff READ PERSONALLY by the verification supervisor before this record (SUPERVISION_CHARTER §3 check 1), not relayed |
| verdict on the instrument work | **PASS** |
| verdict on the landing | **BLOCKED** |

## The assertion a future invocation must satisfy

Do not re-derive this from memory. Inside the SAME shell invocation as
`write-tree`, on the tree actually being committed:

    git diff-tree -r --numstat $H $T

must produce EXACTLY this one line, and nothing else:

    206	7	scripts/case_protocol_freeze_hook.py

Assert BOTH clauses -- that the only path is
`scripts/case_protocol_freeze_hook.py` AND that the counts read `206 7`. A
path-only assertion is a proxy, not the property: it is scoped to PATHS, and a
path more than one team writes defeats it. That is what cost the lab
`bf27b070f`, where a 31/1 worktree numstat was asserted, a second team wrote the
same file on disk between invocations, and `update-index` staged 81 insertions
under the first team's message. Assert on the tree, never on the worktree, and
never in a prior invocation.

**If the numstat has drifted from 206/7 by the time anyone lands this, the
correct action is to STOP and re-derive -- never to edit the expectation to
match the observation.** An expectation adjusted to fit what was observed is not
an assertion.

Everything else from CLAUDE.md rule 10 still applies: capture `H` ONCE for
`read-tree`, the assertion and `-p`; the empty-tree guard; sha-regex guards on
`H`, `T` and `C` (an empty commit sha makes `update-ref` a silent no-op that
still prints OK); `update-ref` CAS with retry; and the post-commit
`git diff HEAD~1 HEAD --stat` verify, which is not optional.

The commit message below is the durable copy and is the one to use. It was
prepared before this record and is reproduced VERBATIM; re-assert it is
non-empty and read back its first line before `commit-tree`, because `-F` never
fails merely because the path exists.

## Commit message, verbatim

```text
verification REPAIR case_protocol_freeze_hook :245 -- a REFUSAL now prints the frozen instrument's OWN ACCOUNT unconditionally, and the mandate that --show-check-output be passed in every documented invocation is RETIRED

THE DEFECT. The stage-1 exit gate captured the frozen instrument's stdout and
stderr and then DISCARDED them unless --show-check-output happened to be passed.
So when the hook REFUSED -- an unexpected rc, an inventory disagreement, any
downstream limb -- the operator was shown a one-line status and NOT the account
of why. The reason existed, was captured, and was thrown away. The board's
standing mitigation was to make the flag mandatory everywhere; this repair
retires that mitigation rather than restating it.

THE SHAPE, AND WHY. A module-level holder is filled the instant the subprocess
returns, and refuse() flushes it before status_line/sys.exit. A single choke
point, NOT a print at each refusal site: every refusal in this file leaves
through refuse(), so the flush reaches both inventory-disagreement limbs, the rc
limb, the strict-flag limb, the unreadable-registration limb, AND every limb a
later hand adds. A per-site print covers only the sites that existed when it was
written, and a refusal that forgets to print its evidence is the very defect
being repaired. A printed-once latch makes no-double-print STRUCTURAL rather
than a coincidence of flag ordering.

  :228  _CAPTURED holder; :231 capture_check_output; :238 emit_captured
  :260  the flush, inside refuse(), before the status line
  :312  capture at the old :245 site; :314 the flag path now calls emit_captured

WHAT THE DIFF TOUCHES IN THE DECISION LOGIC: NOTHING -- no predicate, no exit
code, no threshold. refuse() already ended in an unconditional
sys.exit(EXIT_REFUSE); this adds output strictly before it, and nothing branches
on emit_captured()'s return. The single removed line carrying a control-flow
token is `if r.stderr:`, a PRINT guard, moved verbatim into emit_captured().

DELIBERATE, NOT AN ACCIDENT: the new header line "STAGE1 the frozen instrument's
own account follows" is added output on the PASS path under the flag too. It is
judged harmless and an improvement -- recorded here so nobody later reads it as
an oversight.

NAMED, DEFERRED item: subprocess.TimeoutExpired carries .stdout/.stderr partials
that this repair does NOT recover, so a TIMEOUT refusal still has no account.
That is a known gap, not a silent one; widening the holder to the timeout path is
a different change and was deliberately not made here.

THE SELFTEST IS HALF THE DELIVERABLE -- BOTH ARMS. 24 checks before, 41 after;
41/41 under python3 AND under python3 -O; all 24 pre-existing labels still
present and still OK (label sets diffed). __pycache__ cleared before every run.

  ARM A  a refusal after the subprocess returned, invoked WITHOUT the flag,
         shows a planted marker emitted by a selftest stub instrument and by
         nothing else in the pipeline.
  ARM B  the control that makes A evidence: the selftest builds an UNREPAIRED
         copy of this file from its own source by mutating the anchored flush
         line, and shows the plant is LOST -- then shows the mutant still
         reveals it under the flag, so the control is a faithful stand-in for
         the old code and not a build that merely captured nothing.
  ARM C  flag AND refusal: the plant appears EXACTLY once.
  ARM D/E  --show-check-output keeps its old PASS-path meaning, against the
         REAL frozen instrument.

SHOWN ABLE TO FAIL, by hand-mutation on scratch copies (CLAUDE.md rule 3's
principle -- a test never shown able to fail is not a test):
  * repair reverted to HEAD's exact behaviour -> rc=2, 34 OK, 3 FAILED:
    both ARM A plant checks (expected True, got False) and the ARM B anchor
    count (expected 1, got 0).
  * print-once latch defeated -> rc=2, 39 OK, 2 FAILED: ARM C both plants
    (expected 1, got 2).

scripts/check_comparator_freeze.py is FROZEN and is byte-identical to HEAD; it
is not repaired here and its three recorded defects (D597/D600) remain Sanaa's.
No bare `assert` anywhere in the file, selftest included (:105, D594/L-332);
ast.Assert node count 0.

Diff read personally by the verification supervisor before this commit
(SUPERVISION_CHARTER §3 check 1), not relayed.

Committed under the STRENGTHENED rule-10 assertion ruled today after
bf27b070f: the shared working tree made a PATH-scoped assertion insufficient --
ansys-verification asserted a 31/1 worktree numstat, cfd wrote the same file on
disk between invocations, and update-index staged 81 insertions under ansys's
message. The assertion here is on `git diff-tree -r --numstat $H $T` -- the tree
actually being committed -- in the same shell invocation as write-tree, pinned
to BOTH the single path AND the exact counts 206/7.

Foreign uncommitted rows: the working tree carries many other teams' unfinished
changes (cases/, verification/queue/, sdk/, docs/campaigns/ and others). NONE of
them are in this commit; somebody should be dispatched to land them.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cnj49MxgvKnUeUkkxfiAiC
```

---

## DATED ADDENDUM, 2026-09-11 — LANDED at `c185d7508`. The block was a PERMISSION state, not a defect, and it did not survive a new session.

`lines whose number changed above this section: 0`, apart from the status block
at the head, which is STRUCK and not rewritten.

**THE PINNED EXPECTATION HELD, UNCHANGED, ACROSS A FOURTH HEAD MOVE.** This
certificate pinned **206 insertions / 7 deletions / 1 file** against
`5349795d3`, and recorded it surviving `cc2a2e039` and `f93309649`. Measured
again at landing against `b06e0526b`: `git diff-tree -r --numstat $H $T`
returned exactly `206	7	scripts/case_protocol_freeze_hook.py`, one path, no
other. **The expectation was never adjusted to fit an observation.** Both
clauses — the single path AND the exact counts — were asserted on the TREE being
committed, inside the same shell invocation as `write-tree`. Asserting on the
worktree instead is what cost the lab `bf27b070f`.

**WHAT THIS SUPERVISOR RE-MEASURED BEFORE LANDING** — personally, not relayed,
and deliberately NOT taken from this certificate's own claims (`SUPERVISION_CHARTER`
§3 check 1; and check 3, which says a claim is assumed wrong until defended
against its own evidence — a certificate asserting its own correctness is
exactly such a claim):

| claim in this certificate | re-measured this session | agrees |
|---|---|---|
| diff read personally, as a diff | read in full, both halves | yes |
| selftest 41 checks, 0 failures | 41 `OK`, rc 0 | yes |
| 41/41 also under `python3 -O` | 41 `OK`, identical closing line | yes |
| bare asserts: 0 | `ast.Assert` node count **0** | yes |
| decision logic untouched | confirmed — `refuse()` already ended in an unconditional `sys.exit(EXIT_REFUSE)`; the flush is added strictly BEFORE it, and nothing branches on its return | yes |
| one removed control-flow token | confirmed `if r.stderr:` — a PRINT guard, moved verbatim into `emit_captured()` | yes |

`__pycache__` was cleared before every run — the stale-bytecode trap inverts
mutation tests, and this repair rests on a mutation control.

**THE LIMB THAT MAKES ARM B EVIDENCE, AND WHY I ACCEPTED THE REPAIR ON IT.** A
control that builds an unrepaired copy and finds the plant ABSENT proves nothing
by itself: an absence is equally well explained by a build that captured nothing
at all. This selftest closes that hole explicitly — `r6b2` re-runs the SAME
mutant under `--show-check-output` and shows the plant REAPPEARS. The mutant is
therefore a faithful stand-in for the pre-repair code rather than a broken
build, and ARM B's zero is a READ zero rather than a blind one. That is
CLAUDE.md rule 3's discipline applied to a mutation control, and it is the
reason this repair is believable rather than merely green.

**DISCLOSED TENSION, RECORDED SO NOBODY LATER READS IT AS AN OVERSIGHT.** The
module docstring says the flag "keeps exactly its old meaning" on the PASS path,
while the commit message discloses that the new header line `STAGE1 the frozen
instrument's own account follows` IS added output on that path under the flag.
Both are true at different grains — the SEMANTICS are unchanged, the BYTES are
not. It is disclosed in the commit message rather than hidden, and ARM D pins
the PASS-path behaviour. Judged harmless; named here rather than smoothed over.

**THE GAP THIS REPAIR DOES NOT CLOSE, STATED AS A GAP.**
`subprocess.TimeoutExpired` carries `.stdout`/`.stderr` partials the holder never
receives, because the holder is filled only when the subprocess RETURNS. **A
TIMEOUT refusal therefore still has no account** — the same defect, on a path
this repair does not reach. Known, named, deliberately deferred. It is owed.

**THE GENERAL FINDING, WHICH OUTLIVES THIS FILE.** A permission refusal is a
state of one SESSION, not a property of the WORK. Every check this work had to
pass had passed; it then sat undone for a day because the session that finished
it could not move a ref. **The prior session was RIGHT to stop.** Retrying,
routing around, or handing it to a peer whose `update-ref` was going through
would have been permission laundering (rule 9) — a peer's willingness is not
Sanaa's consent, and a peer session's permissions are not a wider grant.

**The correct artifact for a permission block is exactly this: a certificate
that pins the expectation tightly enough that a LATER session can land it
without re-deriving trust from memory.** It worked. This landing believed none
of the certificate's claims and re-measured all six, and the pin is what made
that cheap rather than a re-investigation. **Recommend the shape be reused
whenever a session is blocked on PERMISSION rather than on EVIDENCE** — the two
are different states and only one of them is a finding about the work.
