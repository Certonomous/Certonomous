#!/usr/bin/env python3
r"""Append rows to an append-only record: HEAD's committed blob plus your rows.

AMENDMENT 2026-09-07 -- THE WORKTREE TAIL IS DISCARDED, NOT PRESERVED
====================================================================
THE HISTORICAL BODY BELOW describes the ORIGINAL design, in which this module
built the output by MERGE -- HEAD's blob PLUS the worktree's own tail PLUS your
rows -- to keep D369 from destroying worktree bytes on write-back. That merge is
NO LONGER the production behaviour, and every "preserves the tail", "the tail is
an arithmetic input" and "PRESERVED ahead of the appended rows" claim below is
superseded by this amendment. The historical text is kept, not rewritten,
because it is the provenance for WHY the merge machinery exists.

WHAT CHANGED, AND WHY. The merge PRESERVED the shared worktree tail by design,
and that turned an aborted append into a cross-team sweep: an append that dies
after writing its row but before committing leaves that row in the SHARED
worktree, and THE NEXT TEAM'S APPEND folded the orphan into ITS commit. It bit
twice; most recently ansys's aborted VMFL046-R5 append orphaned a row that
dafoam's next append swept into commit 9bf38155 (2026-09-07).

THE REPAIR. The base is now HEAD's committed blob ALONE. `merge()`'s production
path (`preserve_worktree_tail=False`, the default and the only path `main()`
takes) writes `head_text + rows_text` and NOTHING from the worktree beyond HEAD.
So:
  * the tool's output for a path = (HEAD blob of the path) + (this run's rows),
    never HEAD + worktree-orphans + rows;
  * an aborted append leaves nothing a peer can sweep -- the orphan sits in the
    worktree and is simply DISCARDED by the next append;
  * the worktree tail is NO LONGER an arithmetic input: the id maximum, the D549
    shape audit and the tool-allocated-id uniqueness backstop all judge the
    bytes actually written (HEAD's blob + the rows), never the discarded tail;
  * the UNCONDITIONAL prefix test is KEPT: an edit INSIDE HEAD's own committed
    bytes still refuses (exit 2) rather than being silently reverted -- that is
    the D369 protection, and it is independent of the tail question;
  * multi-row batching is unaffected -- every row in a single --rows file lands,
    because they are all inside `rows_text`;
  * the id-minting, format/column validation, D549 shape-audit, smuggle-guard
    and `corrects:` logic are UNCHANGED -- only the BASE CONTENT SOURCING moved
    from "HEAD + worktree tail" to "HEAD".
The old preserve-the-tail path is RETAINED behind `preserve_worktree_tail=True`
SOLELY as the RED reference the selftest's discard limb drives, proving the
production path actually differs from the pre-fix behaviour.

WHY THIS EXISTS (docket D369, D461/D-13; docs/USING_THIS_LAB.md section 8.5)
===========================================================================
The private-index protocol rebuilds an append-only file as **HEAD's blob plus
the author's own rows** and then, "as part of the protocol, not an
afterthought", writes that result into the working tree. That last step is a
plain OVERWRITE, and it destroys anything the worktree held beyond HEAD's blob.

It has now bitten twice.

  * `D369`: applied at `12b7ed42` to a `docs/LESSONS.md` whose worktree copy was
    LONGER than HEAD's blob. `cmp` reported "EOF on - after byte 313171"; the
    trailing bytes were destroyed and are not recoverable. D369 closes with the
    repair -- "**The write-back must be a MERGE, not an overwrite**: rebuild
    HEAD's blob plus your rows, then re-apply whatever the worktree held beyond
    HEAD's blob, and refuse if the two disagree anywhere inside HEAD's own
    bytes" -- and records it as **OPEN**, owed to section 8.5.
  * `D461` / `RESULTS.md` departure D-13: the R4 lane was instructed to use the
    overwrite form and did. Nothing was lost, as far as every ID-level check can
    see -- and that qualifier is the whole problem, because D369's loss was
    bytes that matched no ID regex.

Sanaa's standing rule (H-7, the L-221 rule) is that a defect class which has
bitten twice gets an ASSERT AT EVERY CALL SITE, never a paragraph in a report.
This module is that assert. The paragraph has been written twice already.

WHAT "DISAGREE INSIDE HEAD'S OWN BYTES" MEANS, AND WHY IT IS A REFUSAL
=====================================================================
An append-only record's worktree copy should be HEAD's blob with zero or more
bytes appended. So the test is a PREFIX test:

    worktree[:len(head)] == head        -> tail = worktree[len(head):]
    anything else                       -> REFUSE, write nothing

The second case means somebody edited or truncated content that is already
committed. That is not an append, and this module has no way to know whose edit
it is or whether it is deliberate, so it stops rather than guessing. Refusing is
cheap; the alternative is the D369 outcome.

ORDER OF THE MERGE
==================
    HEAD's blob  +  the worktree's own tail  +  your rows

The tail goes BEFORE the rows because the tail is somebody else's work that was
already sitting there, and an append-only record is chronological. If the tail
does not end in a newline it is a partial line -- somebody is mid-edit -- so a
separator is inserted and the fact is REPORTED, never silently fixed.

THE ID ASSERTION, AND WHY THE TAIL IS CONSULTED FOR ARITHMETIC ONLY
==================================================================
The first ID in the rows being appended must equal max + 1 for its own series.
Series-aware, because `docs/NUMERICS_KNOWLEDGE.md` numbers per lane -- N-B, N-D,
N-K, N-X, N-T -- and `N-B26` follows `N-B25` regardless of what N-T is up to.
Never from a number remembered from earlier in the session, which is the
L-43/L-52 trap (CLAUDE.md rule 11: the maximum existing number, never a count).

That assert used to read HEAD's blob ALONE. But the merge above lands HEAD's
blob PLUS the preserved worktree tail plus your rows, so an assert that reads
only HEAD is asserting against a different document than the one it writes.

That gap is the THIRD BITE of the D369 family, found by the closure team at
`52e5de39`: HEAD's `docs/DOCKET.md` maxed at D470, a peer's unlanded
`| D471 | ... |` sat in the worktree tail, and a caller appending D471 passed
the assert because 471 == 470 + 1. The merged file then carried D471 twice --
a duplicate minted by the very module written to stop this family of loss.

So the effective maximum is taken over HEAD's ids AND the ids parsed out of the
PRESERVED TAIL, with the same pattern and per series:

    effective max = max(max over HEAD's ids, max over the preserved tail's ids)

and the tail additionally REFUSES (exit 6) whenever it already holds an id AT OR
ABOVE the first id being appended, printing that series' tail ids and the correct
next number. It refuses rather than renumbering, for two reasons: renumbering the
caller's rows would silently change what the caller believes it filed, and the
tail's rows are somebody else's work -- `check_docket_reconciliation`'s own rule
is ASK, never renumber. The caller re-derives and retries, at commit time and in
the same shell invocation; that is rule 11 discipline, not a courtesy.

THE TAIL IS AN ARITHMETIC INPUT, NEVER AN ID AUTHORITY FOR WHAT IS COMMITTED.
Nothing about what gets written changed: the merge order is unchanged, the tail
is still preserved verbatim ahead of the appended rows, never renumbered and
never dropped, and a preserved tail is still not permission to commit somebody
else's bytes. The tail's ids are read for exactly one purpose -- to know which
numbers are already spoken for IN THE FILE THIS MODULE IS ABOUT TO WRITE -- and
for no other. A tail id is never treated as landed, never licenses an append,
and never crosses series: a tail id in a DIFFERENT series is arithmetically
irrelevant and is deliberately ignored, because `D3` cannot collide with `G7`.

WHAT THIS MODULE CANNOT SEE
===========================
  * WHETHER THE TAIL IT PRESERVED IS WANTED. A worktree-only paragraph may be a
    peer's live work or an abandoned scrap. This module preserves it and reports
    it; it never judges it, and a preserved tail is not permission to commit
    somebody else's bytes.
  * A REORDERING INSIDE HEAD'S BYTES that happens to preserve length and
    content -- there is none, the prefix test is exact -- but equally, an edit
    that HEAD already carries because a peer landed it between your `git show`
    and your write. Capture HEAD ONCE and pass the same revision here that you
    pass to `commit-tree -p`.
  * ANYTHING ABOUT THE COMMIT. This module touches the working tree only. The
    private-index sequence, the compare-and-swap and the post-commit
    verification are still the caller's.
  * WHICH IDS A TAIL HOLDS WHEN THE PREFIX TEST HAS ALREADY FAILED. There is no
    trustworthy tail in that case, so the id arithmetic falls back to HEAD alone
    and the run refuses with exit 2 anyway. Nothing is written on either path,
    so no duplicate can escape through the gap -- but the id report on such a
    run is HEAD-only and says so rather than pretending otherwise.

TOOL-ALLOCATED IDS, AND WHY THE COUNTER IS GONE
===============================================
Sanaa's PLUMBING FREEZE directive, 2026-08-31, captured verbatim at `86f58af3`
(`etc/sessions/2026-08-31T*_sanaa_plumbing_freeze.md`):

    "No more counters. Lesson/docket/row ids become tool-allocated at append
    time from timestamp+hash -- no sequential numbers anywhere, so collision and
    stale-tail are impossible, not policed."

    "Instrument repairs are done once, with the fail-closed + planted-control
    standard, then the topic closes."

WHAT THE COUNTER ACTUALLY COST, MEASURED 2026-08-31 AT `c428cbed`, not recalled:
`scripts/check_record_reconciliation.py` on a BARE RUN reports rc 4 and names
TWO LIVE DUPLICATE IDS -- `C-217`, held by a `dafoam` row at
`docs/COST_CALIBRATION.md:301` and a `closure` row at `:305`, and `L-404` in
`docs/LESSONS.md`. Neither is struck. Both are two findings wearing one name in
an append-only record, and both were minted the same way: two agents read the
same maximum and each added one. The ledger additionally carries SIX rows struck
for that same reason (`C-69`, `C-104`, `C-165`, `C-215`, `C-216`, `C-218`),
which is the repair, not the defect. THE MAXIMUM IS SHARED STATE, and every
collision this lab has recorded came from deriving a new id from it.

THE ID SPACES ARE TWO, AND THEY ARE KEPT APART ON PURPOSE
---------------------------------------------------------
  * LEGACY IDS ARE NEVER RENUMBERED. `L-411`, `C-226`, `D549`, `N-B26` keep
    their identity forever; `RECORDS` still parses them, `check_first_id` still
    judges them, and nothing about a historical record changes. This is
    ADDITIVE.
  * A TOOL-ALLOCATED ID is `<PREFIX>-<YYYYMMDDThhmmss.ffffffZ>-<8 hex>`, e.g.
    `C-20260831T154707.481920Z-a3f91c4d`. It is minted HERE, at append time,
    and it is derived from NOTHING THE RECORD CONTAINS: a UTC clock reading,
    the process id, the host, the record path, the row's own bytes, a
    per-process monotonic counter, and 16 bytes of `os.urandom`.
  * SORTABLE: every field is fixed width, so within a prefix a lexicographic
    sort IS chronological order -- to the microsecond, which is the resolution
    the planted control forced (see `TOOL_ID_BODY`; the first version of this
    format was second-resolution and the control caught it sorting two
    same-second ids backwards). CITEABLE: the date and time are readable in
    prose. NON-COLLIDING ACROSS THE FOUR RECORDS: the prefix differs per
    record, so a `docs/LESSONS.md` id cannot be a `docs/DOCKET.md` id even if
    the clock and the hash agreed.
  * The four legacy patterns REJECT the new form structurally, and this was
    checked rather than assumed: `C-\d+` followed by a closing cell cannot match
    `C-20260831T...` because a `T` follows the digits; `[A-G]\d` cannot match
    `D-2026` because a hyphen follows the letter; `N-[A-Z]+\d` cannot match
    `N-2026` for the same reason; `L-\d+` followed by a period or an em-dash
    cannot match `L-20260831T...`. A planted limb drives all four.

WHY COLLISION AND STALE-TAIL ARE IMPOSSIBLE BY CONSTRUCTION RATHER THAN POLICED
-------------------------------------------------------------------------------
STALE-TAIL first, because it is the cleaner claim: a stale tail is only a hazard
for a value DERIVED from the tail. `allocate_id` reads neither HEAD nor the tail
nor the rows' neighbours -- there is no shared state to be stale about, so the
failure mode has no mechanism, not merely no instance. The tail is still read,
once, for a NON-PRESENCE assert; that assert can only make the tool REFUSE, and
a refusal cannot mint a duplicate.

COLLISION: the only way a duplicate can now enter a record THROUGH THIS TOOL is
for a caller to HAND-WRITE a tool-form id into its rows, and `check_allocation`
REFUSES exactly that (exit 9), whether or not `--allocate-id` was passed, and for
ANY record's prefix rather than only this record's. A tool-form id therefore has
exactly one producer. Stated as the acceptance question asks it -- what would
someone have to do to reintroduce a duplicate? They would have to bypass this
module entirely and hand-edit the record file, typing a 34-character
timestamp-and-hash id that already exists somewhere else in it. That is not an
edit a careful person makes by accident; it is not the `C-217` mechanism, where
two people each did the correct thing with the same shared number.

THE HONEST RESIDUE, STATED PLAINLY BECAUSE THE READER IN THREE WEEKS WILL NOT
REMEMBER THE CONVERSATION THAT SETTLED IT
-----------------------------------------------------------------------------
**COLLISION IS NOT IMPOSSIBLE HERE. IT IS IMPROBABLE.** Anyone who needs the
stronger sentence should read this one instead, and the difference is not
pedantry -- it decides what this tool may be cited for.

WHAT IS IMPOSSIBLE BY CONSTRUCTION: **derivation from shared state.**
`allocate_id` reads neither HEAD, nor the preserved tail, nor a neighbouring
row. There is no maximum to be stale about, so `max + 1` -- the mechanism that
minted `C-217`, `L-404` and the four struck calibration pairs, always by two
agents each doing the correct thing with the same number -- has no mechanism
here, not merely no instance. That disease is gone.

WHAT IS MERELY IMPROBABLE: two ids minted in the SAME MICROSECOND, in different
processes, whose 32-bit blake2b digests ALSO agree. That is not zero, and no
sentence in this file makes it zero. It is (a) unreachable by any human edit,
(b) not a failure mode that has ever fired here, and (c) loud rather than silent
when it does, which is the substantive trade: a silent systematic collision has
been exchanged for a detectable improbable one.

AND THE BACKSTOP HAS A NAMED BLIND SPOT. `check_allocated_unique` refuses a
minted id that is already in HEAD or in the preserved worktree tail. **IT
CANNOT SEE A TWIN SITTING IN ANOTHER AGENT'S UN-MERGED ROWS FILE** -- that id
is in no file this process reads, and the two runs would only meet at the
second one's merge, by which time the first may already have landed. So the
backstop narrows the residue; it does not close it, and it is a backstop rather
than the uniqueness mechanism.

THE FORMAT THAT WOULD CLOSE IT, recorded so it is an option rather than a
rediscovery: the id would have to CARRY `(host, pid, in-process sequence)`
rather than hash them, since those are unique among concurrently live minting
processes. That is a format change and it is NOT taken today; it is on Sanaa's
desk as an option (verification-supervisor, 2026-08-31). Until she rules, this
tool's claim is the one written above and no wider.

THE READER LANDS WITH THE WRITER, IN ONE COMMIT
-----------------------------------------------
`parse_record_ids(text, path)` reads BOTH id spaces -- the legacy pattern and
this record's ANCHORED tool-id pattern -- and it is what both reconcilers use.
That is not a convenience. `check_record_reconciliation.py` parsed the legacy
patterns ALONE, so on the day allocation was used a tool-allocated row sitting
unlanded in a worktree would have been invisible to the guard whose entire job
is to name unlanded work: rc 0, VERDICT PASS, over a row it could not see. That
is this team's own fail-open class, twice recorded -- `FAIL_OPEN_GATE_AUDIT`
sections 13 and 14 -- and a tool that writes ids its own reconciler cannot read
is a dead lever the day it ships. So the two land together or neither lands.

The tool-id reader is ANCHORED to each record's entry position, not to the
unanchored `tool_id_pattern`, for a measured reason: `allocate_into_rows` fills
every placeholder ON A LINE, so a row may carry its own id twice, and an
unanchored count reads that correct row as a DUPLICATE (rc 4). A planted control
drives that row and requires the anchored reader to count it ONCE while showing
the unanchored one counting it twice.

HOW A CALLER USES IT
--------------------
Write `{{ALLOCATE_ID}}` where the id goes and pass `--allocate-id`. One id is
minted PER LINE that carries the placeholder, and every occurrence on that line
is replaced with that line's id -- so a row may cite its own id in its own prose.
Passing the placeholder WITHOUT `--allocate-id` is a refusal, not a literal
write, because a record row reading `{{ALLOCATE_ID}}` is worse than either
outcome. `--allocate-id` with `--expect-first-id` is a refusal too: an id that
does not exist until this call cannot have been expected.

EXIT CONTRACT
=============
    0  OK        merged and written (or --dry-run and it would have been)
    2  REFUSED   the worktree disagrees with HEAD inside HEAD's own bytes
    3  REFUSED   the first appended id is not max + 1 for its series, over
                 HEAD's ids and the preserved tail's ids together
    4  UNKNOWN   a side could not be read, or the pattern parsed zero ids
    5  SELFTEST  a planted control did not behave as required
    6  REFUSED   the PRESERVED WORKTREE TAIL already holds that id, or a higher
                 one in the same series -- appending would land a duplicate in
                 the merged file. Re-derive the next id and retry; the tail is
                 neither renumbered nor dropped (closure `52e5de39`, D369 family)
    7  REFUSED   a line matches the record's id-bearing CANDIDATE SHAPE but the
                 id pattern parses NO id from it, and it is not in that record's
                 KNOWN-EXCLUDED set. The arithmetic below would be judged against
                 a maximum that silently omits that line (D549)
    8  REFUSED   `--expect-first-id` was passed and ZERO ids were parsed from the
                 rows, so the expectation could not be EVALUATED. An expectation
                 that could not be evaluated is not an expectation that was met
                 (D549 clause 1a; independent of any pattern change)
    9  REFUSED   a TOOL-ALLOCATED ID precondition failed: a tool-form id was
                 hand-written into the rows (this module is its only producer);
                 or `--allocate-id` was passed with no `{{ALLOCATE_ID}}`
                 placeholder to fill, or with `--expect-first-id`; or a
                 placeholder was present without `--allocate-id`; or a minted id
                 was already present in HEAD or the preserved tail. Sanaa's
                 PLUMBING FREEZE directive, 2026-08-31.
                 ALSO, from the ALLOCATION SCOPE ruling of 2026-09-03:
                 `--allocate-id` was passed for a record listed in
                 `ALLOCATION_REFUSED` -- a record over which the constitution
                 prescribes an INTEGER derivation that MISREADS the minted form.
                 This is a REFUSAL and deliberately reuses this code rather than
                 VERIFICATION_CHARTER section 2ak's `70`, which that clause
                 reserves for a comparator's INTERNAL ERROR and rules is NOT a
                 refusal.
                 ALSO, from Sanaa's PLUMBING AMENDMENT of 2026-09-03: a
                 `corrects:[...]` field on a row that is not a correction row;
                 a malformed or unterminated `corrects:[...]` field; or a
                 correction row carrying an accepted citation but no id of its
                 own at this record's entry position

An id refusal is reported BEFORE a prefix refusal, so 3 and 6 keep precedence
over 2 exactly as 3 did before this repair. The two D549 refusals, 7 and 8, are
reported BEFORE all of those, because both say the id report itself cannot be
trusted -- and nothing is written on any of those paths, so the relative order
of 3, 6 and 2 is unchanged in every observable way.

The allocation refusal, 9, is reported BEFORE EVERYTHING, because it is decided
on the ROWS ALONE and must be settled before an id is minted, a merge is
computed or a byte is read from the record. Two consequences, both deliberate:
a run that would have failed the prefix test refuses at 9 rather than 2 when its
rows hand-write an id -- the more specific and more actionable diagnosis wins --
and a minted id whose run then refuses for any later reason is simply DISCARDED.
Under a counter a burned number was a real problem, because the next caller's
`max+1` would skip it and somebody would eventually ask why; under allocation
there is no sequence for a gap to appear in, so an unused id costs nothing and
is never reused.

THE FAIL-OPEN, AND WHY AN UNPARSED LINE IS A REFUSAL RATHER THAN AN ABSENCE
==========================================================================
Docket `D549`, raised by closure and UPHELD by verification at `a0e2e9a2`.

`main()` wrapped the ENTIRE id gate -- including the `--expect-first-id`
comparison -- in `if new_ids:`, and `new_ids` came from `parse_ids(rows_text,
pattern)` using the SAME per-record pattern. So rows whose heading the pattern
could not parse yielded `new_ids == []`, the whole gate was skipped, and the
tool returned rc 0 AND WROTE.

Measured 2026-08-28, both directions, because a zero from a reader not shown
able to see a non-zero is not evidence (CLAUDE.md rule 3):

  * an em-dash lesson heading with `--expect-first-id L-396` printed
    `appending: (no ids parsed)` and exited **0**;
  * the same tool, same flag, given a PERIOD-form heading and a deliberately
    wrong id `L-999`, refused with **3** and named its arithmetic.

The machinery worked. The precondition disabled it. Verification's ruling, which
is what the two clauses below implement: **a line that matches the record's
id-bearing SHAPE but whose id the pattern cannot parse is a REFUSAL CONDITION,
not an absence.**

  * CLAUSE 1a (exit 8) -- if `--expect-first-id` is passed and zero ids were
    parsed, REFUSE. This clause is deliberately INDEPENDENT of every pattern: it
    closes the reported hole even if no regex is ever changed, and its planted
    control drives it with no record pattern involved at all.
  * CLAUSE 1b (exit 7) -- every record carries a CANDIDATE SHAPE, broader than
    its id pattern, plus an explicit KNOWN-EXCLUDED set. Any line matching the
    candidate that yields no id and is not known-excluded is named, with its
    line number and which side it came from, and REFUSED. This applies to ALL
    FOUR RECORDS, not just the one that was reported: the fail-open is generic
    and CLAUDE.md rule 14 is explicit that a lesson is not applied until EVERY
    call site asserts it.

CLAUSE 1b IS RUN OVER ALL THREE SIDES -- HEAD's blob, the preserved worktree
tail, and the rows -- because the maximum this module asserts against is taken
over HEAD and the tail, so an unparsed line on EITHER of those sides corrupts
the arithmetic just as surely as one in the rows. That is not hypothetical: it
is exactly how `docs/LESSONS.md` came to report `L-343` as the next id when
`L-398` already existed.

WHAT KNOWN-EXCLUDED IS FOR, AND THE TRAP INSIDE IT
==================================================
An excluded form is a line that LOOKS id-bearing and deliberately is not. The
canonical one is `## L-43, second corollary.` -- a SECOND BLOCK under an id that
already exists elsewhere in the file. It matches any sane candidate and must
never be parsed as an id, so a candidate-shape refusal written without an
exclusion set would start refusing legitimate structure.

Every excluded expression below was derived BY MEASUREMENT against the real
files, on both the worktree and HEAD's blob, and each records the count it
matched. None was taken from a description of the file, including this module's
own older comments -- one of which named `### L-63 - CORRECTION` as an excluded
form when that line does not match the candidate at all (an h3, measured).

No status is ever taken through a pipe: every subprocess is run with a list
argument and its `returncode` read from the completed process.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import itertools
import os
import re
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_kind  # noqa: E402

EXIT_OK = 0
EXIT_REFUSED_DISAGREES = 2
EXIT_REFUSED_ID = 3
EXIT_UNKNOWN = 4
EXIT_SELFTEST = 5
EXIT_REFUSED_TAIL_ID = 6
EXIT_REFUSED_UNPARSEABLE_SHAPE = 7
EXIT_REFUSED_EXPECTATION_UNEVALUABLE = 8
EXIT_REFUSED_ALLOCATION = 9

#: One entry per append-only record this lab keeps. The pattern must match the
#: record's OWN id vocabulary; the traps each one is anchored around are in the
#: comments, because a pattern without its trap is copied wrongly.
#: L-401: every CANNOT SEE line carries an owner AND a re-read trigger.
CANNOT_SEE_OWNER = (
    "OWNER verification-supervisor (assigned 2026-08-28 [lab-attributed], chief dispatch; roster territory 'cross-team gate audits' -- this guards four lab-wide registers). RE-READ 2026-09-28, AND IMMEDIATELY ON TRIGGER: any change to a guarded record's heading/row grammar. Per L-401 a DECLARED blindness is not a DISCHARGED one -- the date is the floor, the TRIGGER is the real guard, because a date alone passes fine the day after the format changes."
)

RECORDS = {
    # The whole first cell, modulo bold/strike -- `check_docket_reconciliation`'s
    # pattern, unchanged, including its `D19-D20 note` exclusion.
    "docs/DOCKET.md": r"^\|\s*(?:\*\*|~~)*\s*([A-G]\d+[a-z]?)\s*(?:~~|\*\*)*\s*\|",
    # `## L-<n>` at h2, followed EITHER by a literal period OR by whitespace and
    # an em-dash. REPAIR 2 of D549: the period-only form
    # `r"^## (L-\d+)\."` was written when the period form was the only one, and
    # the file's now-dominant heading form is `## L-350 - TITLE` with an EM-DASH.
    # THE INVARIANT, which is what is actually asserted, because the absolute
    # counts drift every time a peer lands a lesson (one landed DURING this
    # repair): the ids this pattern parses must be the SAME SET, and carry the
    # same maximum, as CLAUDE.md rule 11's own command
    # `grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n`
    # sees, once the second-block form is set aside. Re-derive, never recall.
    # Measured 2026-08-28, both patterns against the SAME bytes in ONE shell
    # invocation, beside a rule-11 truth of 397 distinct ids / maximum 399:
    #   period-only pattern : 308 ids parsed, maximum 342  <- 57 ids BELOW truth
    #   this pattern        : 397 ids parsed, maximum 399  <- equals the truth
    # The old pattern's own refusal message therefore named `L-343` as the next
    # id while `L-398` already existed, so a team following the tool would have
    # minted a duplicate. Verification offered this expression as a VERIFIED
    # CANDIDATE, explicitly not an order; it is used because it was measured to
    # hold on every line of the real file, not because it was offered.
    # The two counts reconcile like this, and the two quantities are different
    # ones: 398 lines match the candidate shape; 90 are unparsed by the OLD
    # pattern; 88 of those 90 are genuinely em-dash headings and the other 2 are
    # the comma second-block form. 396 distinct ids with maximum 398 is what the
    # rule-11 command sees, because L-43 and L-61 each appear twice under the
    # loose form -- as a heading AND as a second block -- and a second block is
    # not a duplicate id.
    # TRAP: this must NOT be "tidied" to `^## (L-\d+)`. Dropping the trailing
    # alternation would start parsing `## L-43, second corollary.` as a bare id
    # and mint a duplicate out of legitimate structure; a planted control drives
    # exactly that mutation and requires it to flip.
    # `### L-63 - CORRECTION` (an h3 amendment) is not matched either, and does
    # not need excluding: it fails at `^## ` before the id is reached (checked).
    "docs/LESSONS.md": r"^## (L-\d+)(?:\.|\s+\u2014)",
    # Entries are written either bold or as an h2, and both forms are live:
    # 50 bold and 20 headings at the time of writing.
    "docs/NUMERICS_KNOWLEDGE.md": r"^(?:\*\*|## )(N-[A-Z]+\d+)\.",
    # The cost-calibration ledger (Sanaa's directive 2026-08-23; the calibration
    # bullet of `CLAUDE.md` rule 12). WHY THE C SERIES EXISTS AT ALL: this file
    # is appended CONCURRENTLY by all five teams -- that is its own append rule 5
    # -- and until 2026-08-23 its rows carried no id, so this module's tail
    # arithmetic had nothing to hold on to. Two teams could each land a row and
    # neither the tail check nor any reconciliation could NAME the collision,
    # which is precisely the D369 family's third bite (closure `52e5de39`). A
    # chief-ruled format amendment on 2026-08-23 added the leading `id` column;
    # the series is one flat `C-`, not per-team, because the ledger is a single
    # chronological record and a per-team series would let two teams mint the
    # same physical row position.
    # TRAP: the id carries a HYPHEN, so `split_id('C-4')` reads the series as
    # `'C-'` and `next_id` renders `C-5`. Do not "tidy" this to `C\d+`.
    # TRAP: the table's own header row and its `|---|` separator both begin with
    # a pipe. The planted negatives in `run_controls` assert this pattern parses
    # NEITHER of them as an id -- a looser pattern would mint ids out of table
    # furniture and the arithmetic would be judged against them.
    "docs/COST_CALIBRATION.md": r"^\|\s*(?:\*\*|~~)*\s*(C-\d+)\s*(?:~~|\*\*)*\s*\|",
}

#: CANDIDATE SHAPES -- one per record, keyed identically to `RECORDS`.
#:
#: WHY A SEPARATE MAPPING RATHER THAN A RICHER `RECORDS`. `RECORDS` is a
#: PUBLISHED CONTRACT, not a private table: `scripts/check_record_reconciliation`
#: imports it (`:135`), asserts it is THE SAME OBJECT rather than an equal one
#: (`:142`), passes its VALUES straight to `parse_ids` (`:336`, `:396`, `:416`)
#: and prints them (`:567`). Turning those values into objects would break a
#: second team's instrument. So `RECORDS` keeps its exact shape -- path -> the
#: id pattern STRING -- and the new data lives alongside it, under the key-set
#: guard below, which is that same module's `CONTROL_FORMS` idiom (`:249-253`).
#:
#: A candidate is deliberately BROADER than the id pattern. It answers the
#: question the id pattern cannot: "is this line TRYING to be an id-bearing
#: line?" -- so an unparsed line becomes a refusal instead of an absence.
#:
#: TRAP -- `\s` CROSSES A NEWLINE. `re.compile(r"^##\s*L-", re.M)` MATCHES the
#: two-line string `"## \nL-3. x"`, because `\s` includes `\n`; `^##[ \t]*L-`
#: does not (both measured 2026-08-28). Verification's ruling spelled the
#: LESSONS candidate `^##\s*L-`; it is implemented here as `^##[ \t]*L-`, which
#: is the same shape on every real line of the file (both give 398 candidate
#: lines) and is not fooled by a line boundary. Every candidate below spells its
#: intra-line whitespace `[ \t]`, never `\s`.
#:
#: TRAP -- TABLE FURNITURE. For the two table records the candidate must NOT
#: match the table's own header row or its `|---|` separator. The existing
#: planted negatives assert the ID PATTERN parses neither; the negatives added
#: for D549 assert the CANDIDATE does not match them either, and drive the
#: mutation -- a candidate loosened to a bare `^\|` -- to prove that property is
#: load-bearing rather than accidental.
CANDIDATE_SHAPES = {
    # A docket row whose first cell OPENS with a docket-series letter followed
    # by a digit, modulo bold/strike. Measured on the worktree and on HEAD's
    # blob: 596 candidate lines, 594 parsed, 2 residue (both excluded below).
    # The table's own `| # | Item | ... |` header and its `|---|---|` separator
    # are NOT candidates -- `#` and `-` are not in `[A-G]` (measured).
    "docs/DOCKET.md": r"^\|[ \t]*(?:\*\*|~~)*[ \t]*[A-G]\d",
    # An h2 that opens with `L-`. Measured: 398 candidate lines in the worktree
    # and in HEAD's blob -- the same 398 that CLAUDE.md rule 11's own command
    # sees. The two h3 amendments in the file (`### L-63 - CORRECTION` at :2745
    # and `### L-241 - CORRECTION` at :9575) do NOT match this candidate, since
    # `#` is not `[ \t]`; that was CHECKED rather than assumed, because this
    # module's older comment listed `### L-63` as an excluded form and it never
    # needed excluding.
    "docs/LESSONS.md": r"^##[ \t]*L-",
    # Either live entry form -- bold or h2 -- opening with `N-`. Measured: 124
    # candidate lines, 122 parsed, 2 residue (both excluded below).
    "docs/NUMERICS_KNOWLEDGE.md": r"^(?:\*\*|## )N-",
    # A ledger row whose first cell opens with `C-` and a digit. Measured: 197
    # candidate lines, 196 parsed, 1 residue (excluded below). The ledger's
    # `| id | date | ... |` header does not match (`i` is not `C`), nor does
    # `|---|---|` -- the same two forms the id pattern's own planted negatives
    # already reject.
    "docs/COST_CALIBRATION.md": r"^\|[ \t]*(?:\*\*|~~)*[ \t]*C-\d",
}

#: KNOWN-EXCLUDED -- lines that match a candidate, carry no parseable id, and
#: are DELIBERATELY not ids. Every expression here was derived by reading the
#: real files, and the count each one matches is recorded beside it so a future
#: reader can re-measure rather than re-trust. An entry that stops matching
#: anything is not harmless: it means the file changed shape.
#:
#: THE COST OF AN EXCLUSION, STATED PLAINLY: an excluded line's id, if it has
#: one, is NOT in the arithmetic. That is correct for a second block (the id is
#: counted at its primary heading) and it is a real, named loss for the struck
#: cost row (`C-104`), whose number is below the ledger's maximum anyway
#: (measured max 194) -- so the loss changes no answer today, and it is written
#: down here rather than discovered later.
KNOWN_EXCLUDED = {
    # A RANGE in the first cell is one note, not two rows -- the exclusion
    # `check_docket_reconciliation`'s pattern was written around. Measured: 2
    # lines, `| D19-D20 note |` at :211 and `| D167-D169 note |` at :540.
    "docs/DOCKET.md": (
        r"^\|[ \t]*(?:\*\*|~~)*[ \t]*[A-G]\d+[a-z]?-[A-G]?\d+[a-z]?[ \t]+note[ \t]*\|",
    ),
    # A SECOND BLOCK under an id that already exists, marked by a COMMA
    # immediately after the number. Measured: exactly 2 lines,
    # `## L-43, second corollary.` at :1928 and
    # `## L-61, addendum 2026-08-25 - ...` at :11788, and both parent headings
    # exist (`## L-43.` at :1885, `## L-61.` at :2545), which is what makes
    # these second blocks rather than lost ids.
    # TRAP: L-61's heading CONTAINS an em-dash LATER IN THE LINE. An exclusion
    # written as "has no em-dash" would fail on it, and any rule that tests
    # anywhere-in-line rather than the character immediately after the id would
    # misclassify one of the two. This rule is anchored to the comma directly
    # after the number, which is why it covers both.
    # A SECOND BLOCK written as `AMENDMENT`, with WHITESPACE and no comma after
    # the number. Measured 2026-09-01: exactly 1 line,
    # `## L-426 AMENDMENT 1 - 2026-09-01, heat-transfer. ...` at :19170, and its
    # parent `## L-426 -` exists at :18729 (checked), which is what makes this a
    # second block rather than a lost id. Excluding it drops NO number from the
    # arithmetic: L-426 is counted at its primary heading.
    # SAME TRAP AS L-61, and it is why this is anchored the way it is: this line
    # CONTAINS an em-dash later on, so an exclusion written as "has no em-dash"
    # would fail on it. This one is anchored to the literal word AMENDMENT
    # immediately after the number's whitespace, so it cannot reach a genuine
    # new lesson heading -- those carry a period or whitespace+em-dash, which is
    # exactly what the id pattern above requires, and a planted negative control
    # asserts the two sets stay disjoint.
    # THIRD SPELLING, AND THE HONEST NOTE: the record now writes one convention
    # -- "a second block under an existing id" -- four ways: `L-43,` and `L-61,`
    # (comma), this `AMENDMENT` form, and `### L-63 - CORRECTION`, which needs no
    # entry only because h3 fails the candidate shape. Four spellings for one
    # convention is a RECORD-level inconsistency, and standardising LESSONS.md on
    # the comma form would retire this whole class instead of growing this
    # register once per spelling. REFERRED, NOT IMPOSED: docs/LESSONS.md is not
    # this tool's to reshape, and widening the pattern to guess at future
    # spellings is exactly the over-reach the comma rule was anchored to avoid.
    "docs/LESSONS.md": (
        r"^##[ \t]*L-\d+[ \t]*,",
        r"^##[ \t]*L-\d+[ \t]+AMENDMENT\b",
    ),
    # Two forms, measured, one line each.
    #  * a SERIES DECLARATION, which names a lane rather than a fact:
    #    `**N-D = DAFoam-team numerics facts, opened 2026-08-21**` at :2271.
    #    It carries no number at all, so it is not a lost id.
    #  * a COMPANION block under an existing id -- `## N-AV9 COMPANION - the
    #    wedge CENTROID bias.` at :4469. This is the LESSONS second-block form
    #    in another record's vocabulary: its parent `## N-AV9.` exists at :3913
    #    (checked), so excluding it drops no number from the arithmetic.
    #
    # THREE FURTHER SECOND-BLOCK / CITATION SPELLINGS, added 2026-09-03 for
    # docket D-20260903T184847. THE DEFECT WAS IN THIS REGISTER, NOT IN THE
    # RECORD: `docs/LESSONS.md` gained its `AMENDMENT` exclusion on 2026-09-01
    # (:562) and this record -- which writes the SAME convention, the CLAUDE.md
    # rule 6 departure grammar -- never gained the parallel spelling. So the
    # tool refused (exit 7) on five lines whose ids are ALL already counted at
    # their primary entries, which is the definition of a second block, not of a
    # lost id. Measured on HEAD's blob AND the worktree, identical on both: 138
    # candidate lines, 131 parsed, 7 residue -- the 2 above plus these 5. No
    # expression below matches a line the id pattern parses (measured: zero
    # clashes), and KNOWN_EXCLUDED feeds `shape_audit` ALONE, never `parse_ids`,
    # so this edit cannot move an id, a series maximum or a next-id: 131 ids /
    # 131 distinct before and after, byte for byte.
    #  * an AMENDMENT block. Measured: exactly 1 line, `## N-T9 AMENDMENT 1 --
    #    2026-09-01, heat-transfer. ...` at :5297, parent `## N-T9.` at :5142
    #    (checked). This is the LESSONS `L-426 AMENDMENT` rule spelled in THIS
    #    record's vocabulary -- bold OR h2 -- never borrowed (CLAUDE.md rule 14).
    #    SAME TRAP as L-61, and it is why the anchor is what it is: the line
    #    CONTAINS an em-dash later on, so an exclusion written as "has no
    #    em-dash" would fail on it. `AMENDMENT\b` cannot reach a genuine entry
    #    (an entry carries a literal period straight after the id), and the `\b`
    #    is load-bearing: a planted `## N-Z3 AMENDMENTS to a theory` must still
    #    refuse, and does.
    #  * a DATED ADDENDUM block. Measured: exactly 2 lines, `## N-C6 -- DATED
    #    ADDENDUM, 2026-09-01: ...` at :5343 and `## N-C6 -- DATED ADDENDUM 2,
    #    ...` at :5458, parent `## N-C6.` at :4682 (checked). Anchored on the
    #    LITERAL WORDS after the em-dash, deliberately: a bare `id + em-dash`
    #    exclusion would swallow a GENUINELY LOST new fact written
    #    `## N-Z1 -- a title`, which must keep refusing. A planted violation
    #    drives exactly that line, and a second drives `-- UNDATED ADDENDUM`.
    #  * a BOLD PROSE CITATION -- a paragraph OPENING with a bolded id, which is
    #    prose and not an entry at all. Measured: exactly 2 lines,
    #    `**N-C9**'s bounding evidence are the neighbours:` at :5968 and
    #    `**N-C10** and **N-C11** were appended;` at :5975; all three primaries
    #    exist (:5780, :5864, :5910, checked). The distinguishing byte is WHERE
    #    THE BOLD CLOSES: an entry is `**N-B26. text**` (bold closes at the end
    #    of the title), a citation is `**N-C9**` (bold closes immediately after
    #    the number). Anchoring on that closing `**` is what keeps this narrower
    #    than "any bold line"; a planted `**N-Z2 a bold entry with no period**`
    #    must still refuse, and does.
    #  * a CORRECTION block -- a SIXTH spelling, added 2026-09-10 after the tool
    #    refused EVERY team's NUMERICS append at exit 7 (reproduced: --dry-run
    #    with a well-formed probe row, exit 7, ONE offender named). Measured
    #    2026-09-10 on the worktree and on HEAD's blob, identical: exactly 1
    #    line, `**N-D43 CORRECTION - 2026-09-06 - the "REACHED on the S1 CBFS
    #    case" half of N-D43 is WITHDRAWN as UNESTABLISHED. ...**` at :6511, and
    #    its parent primary heading `**N-D43. The DAFoam primal accept floor
    #    is ...**` EXISTS at :6507 (checked) -- which is what makes this a
    #    SECOND BLOCK under an existing id and not a lost id. Excluding it drops
    #    NO number from the arithmetic: N-D43 is counted at :6507, and the id
    #    count is 138 / 138 distinct before and after, byte for byte.
    #    SAME TRAP as L-61 / N-T9, and it is why the anchor is what it is: this
    #    line CONTAINS em-dashes LATER IN THE LINE, so an exclusion written as
    #    "has no em-dash" -- or any rule testing anywhere-in-line -- would
    #    misclassify it. It is anchored to the literal word CORRECTION
    #    immediately after the id's whitespace. DISJOINT BY CONSTRUCTION from a
    #    genuine entry: the id pattern requires a literal `.` immediately after
    #    the digits, this requires `[ \t]+`, so no string can satisfy both; the
    #    (ii) fixture limb asserts the excluded form parses NO id, and the `\b`
    #    is load-bearing -- a planted `## N-Z4 CORRECTIONS to a theory` must
    #    still refuse, and does (new near-miss control).
    #    SIXTH SPELLING, AND THE PREDICTION THAT CAME TRUE: the LESSONS comment
    #    above called FOUR spellings for one convention a RECORD-level
    #    inconsistency and warned this register would grow once per spelling.
    #    It has: this record alone now writes "a second block under an existing
    #    id" SIX ways (`=`, `COMPANION`, `AMENDMENT`, `- DATED ADDENDUM`, the
    #    bold-mention citation, and now `CORRECTION`). STILL REFERRED, STILL NOT
    #    IMPOSED: docs/NUMERICS_KNOWLEDGE.md is not this tool's to reshape (and
    #    rule 6 forbids editing a frozen record here anyway), and widening the
    #    pattern to guess at future spellings is exactly the over-reach the
    #    anchored rules were written to avoid.
    "docs/NUMERICS_KNOWLEDGE.md": (
        r"^(?:\*\*|## )N-[A-Z]+[ \t]*=",
        r"^(?:\*\*|## )N-[A-Z]+\d+[ \t]+COMPANION\b",
        r"^(?:\*\*|## )N-[A-Z]+\d+[ \t]+AMENDMENT\b",
        r"^(?:\*\*|## )N-[A-Z]+\d+[ \t]+—[ \t]+DATED ADDENDUM\b",
        r"^\*\*N-[A-Z]+\d+\*\*",
        r"^(?:\*\*|## )N-[A-Z]+\d+[ \t]+CORRECTION\b",
    ),
    # A STRUCK id cell carrying its own annotation inside the cell, so the cell
    # does not close after the id and the pattern cannot reach the `|`.
    # Measured: exactly 1 line, `| ~~**C-104**~~ **STRUCK - DUPLICATE ID;
    # RE-ISSUED AS C-114**, ... |` at :180. A struck cell that DOES close
    # cleanly is parsed by the id pattern as normal and never reaches this
    # check, so this exclusion is as narrow as the measurement allows.
    "docs/COST_CALIBRATION.md": (
        r"^\|[ \t]*~~\**C-\d+\**~~",
        # TWO REAL DATA ROWS with MALFORMED tool-id BODIES, hand-landed by
        # private-index appends that bypassed `--allocate-id` (which mints a valid
        # 8-hex body).  Their bodies fail TOOL_ID_BODY -- `w4reanc` is 7 chars and
        # non-hex, `vmfl046r5` is 9 and non-hex -- so no id pattern parses them,
        # yet each matches the id-bearing candidate shape, and clause 1b (which
        # audits HEAD's WHOLE blob) therefore refused EVERY team's future
        # COST_CALIBRATION append at exit 7: a lab-wide rule-12 block.
        # RULED by verification 2026-09-07: excluded by EXACT id (the full unique
        # timestamp+suffix), NOT by a "malformed body" pattern that would silently
        # admit FUTURE bad ids and hollow the smuggle guard.  These stay real data
        # rows -- parse_ids never saw them either way, and this register feeds
        # shape_audit ALONE; append-only rule 1 is intact (zero rows edited), and
        # the owning teams (dafoam, ansys) may append a CORRECTION ROW re-issuing a
        # valid id via `--allocate-id`.  PREVENTION: a tool-form id is MINTED by
        # `--allocate-id`, never hand-typed.  The near-miss fixture drives a
        # DIFFERENT bad body to prove this exclusion does not over-reach.
        r"^\|[ \t]*C-20260906T232437\.922647Z-w4reanc[ \t]*\|",
        r"^\|[ \t]*C-20260907T030000\.000000Z-vmfl046r5[ \t]*\|",
        # A THIRD hand-landed poison row (verification 2026-09-07). Its body IS a
        # valid 8-hex (`b826b62e`), but its fractional seconds are 9 digits
        # (NANOseconds) -- hand-rolled with `%N`, an S-119 / hand-typed-id
        # RECURRENCE that bypassed `--allocate-id` (which mints `%f` = 6 micro).
        # RULED: exclude by EXACT id and keep TOOL_ID_BODY STRICT at `\.\d{6}` --
        # WIDENING to 6-or-9 would legitimize hand-rolled nano ids and erode the
        # always-mint-via-`--allocate-id` discipline; a future non-excluded nano id
        # must STILL refuse. Excluded id: C-20260907T195722.461339981Z-b826b62e
        # (COST_CALIBRATION:466, commit bcb10b80). Feeds shape_audit ALONE; parse_ids
        # never saw it; append-only rule 1 intact; dafoam may append a CORRECTION row
        # re-issuing a valid `--allocate-id` id. Referral: verification-supervisor 2026-09-07.
        r"^\|[ \t]*C-20260907T195722\.461339981Z-b826b62e[ \t]*\|",
        # FOUR MORE hand-landed rows carrying MNEMONIC bodies, not the minted
        # 8-hex form (verification 2026-09-09). Measured on HEAD's blob at
        # :489-:492: `t23g2rl3` is 8 chars but NON-hex, `t23g2rn` is 7, `m1ccomp`
        # is 7, `supbe1` is 6 -- every one fails TOOL_ID_BODY (`\.\d{6}Z-[0-9a-f]{8}`),
        # so `tool_id_pattern` correctly does NOT recognise them and the id
        # pattern parses no id, yet each matches the id-bearing candidate shape.
        # Clause 1b (which audits HEAD's WHOLE blob) therefore refused EVERY
        # team's COST_CALIBRATION append at exit 7 -- a lab-wide rule-12 block,
        # reproduced 2026-09-09 (dry-run --allocate-id, exit 7, these 4 named).
        # SAME RULING as w4reanc/vmfl046r5/b826b62e above: exclude by EXACT id,
        # NOT by widening TOOL_ID_BODY -- a body pattern loosened to admit
        # mnemonic/non-hex suffixes would legitimize hand-typed ids and hollow
        # the smuggle guard (`--allocate-id` is the sole minter; a well-formed
        # 8-hex id is already cleared by tool_id_pattern with no exclusion, which
        # the new positive control drives). These stay real data rows: parse_ids
        # never saw them, KNOWN_EXCLUDED feeds shape_audit ALONE, append-only
        # rule 1 intact (zero rows edited); the owning teams (heat-transfer,
        # closure, cfd) may append a CORRECTION row re-issuing a valid
        # `--allocate-id` id. A DIFFERENT non-excluded mnemonic body still
        # refuses (near-miss control), so the guard is not blinded.
        r"^\|[ \t]*C-20260909T171040\.973304Z-t23g2rl3[ \t]*\|",
        r"^\|[ \t]*C-20260909T183500\.000000Z-t23g2rn[ \t]*\|",
        r"^\|[ \t]*C-20260909T193000\.000000Z-m1ccomp[ \t]*\|",
        r"^\|[ \t]*C-20260909T214553\.000000Z-supbe1[ \t]*\|",
    ),
}

# REFUSE ON DISAGREEMENT, never pick one. Three tables keyed by the same paths
# or this module does not load. A record that gained a pattern but no candidate
# would be the D549 fail-open again, silently, for that one record -- which is
# precisely what CLAUDE.md rule 14 says a lesson is not allowed to be. This is
# `check_record_reconciliation.py`'s own load-time guard (:249-253) in this
# module's idiom.
_D549_MISSING = {
    "CANDIDATE_SHAPES": sorted(set(RECORDS) - set(CANDIDATE_SHAPES)),
    "KNOWN_EXCLUDED": sorted(set(RECORDS) - set(KNOWN_EXCLUDED)),
}
_D549_EXTRA = {
    "CANDIDATE_SHAPES": sorted(set(CANDIDATE_SHAPES) - set(RECORDS)),
    "KNOWN_EXCLUDED": sorted(set(KNOWN_EXCLUDED) - set(RECORDS)),
}
if any(_D549_MISSING.values()) or any(_D549_EXTRA.values()):  # pragma: no cover
    raise SystemExit(
        f"REFUSED: the D549 shape tables and RECORDS disagree. Records with an "
        f"id pattern but no entry: {_D549_MISSING}. Entries for no registered "
        f"record: {_D549_EXTRA}. Add the missing entry IN THAT RECORD'S OWN "
        f"VOCABULARY, measured against the real file -- do not let a record "
        f"borrow another's shapes (CLAUDE.md rule 3, rule 14).")


# ------------------------------------------------------- tool-allocated ids
#: One PREFIX per record, keyed identically to `RECORDS`. The prefix is what
#: makes a tool-allocated id unable to collide ACROSS the four records even if
#: the clock and the hash agreed, and it is what keeps the id legible: a reader
#: seeing `L-20260831T154707Z-a3f91c4d` knows which register it lives in without
#: looking it up.
#:
#: WHY ONE PREFIX PER RECORD AND NOT ONE PER SERIES. The legacy series existed to
#: PARTITION COUNTERS -- `N-B26` follows `N-B25` regardless of `N-T`, and `D3`
#: cannot collide with `G7`, because each series carried its own maximum. Sanaa's
#: directive removes the counters, and with them the only thing a series was
#: doing arithmetically. A NUMERICS family (`N-AV`, `N-D`) remains a real
#: editorial grouping and keeps being written in the entry's TEXT; it is simply
#: no longer load-bearing for uniqueness. THIS IS A DECISION, NOT A DERIVATION,
#: and it is written here so it can be overruled rather than discovered.
TOOL_ID_PREFIX = {
    "docs/DOCKET.md": "D",
    "docs/LESSONS.md": "L",
    "docs/NUMERICS_KNOWLEDGE.md": "N",
    "docs/COST_CALIBRATION.md": "C",
}

_TOOL_MISSING = sorted(set(RECORDS) - set(TOOL_ID_PREFIX))
_TOOL_EXTRA = sorted(set(TOOL_ID_PREFIX) - set(RECORDS))
if _TOOL_MISSING or _TOOL_EXTRA:  # pragma: no cover - a load-time refusal
    raise SystemExit(
        f"REFUSED: TOOL_ID_PREFIX and RECORDS disagree. Records with an id "
        f"pattern but no allocation prefix: {_TOOL_MISSING or 'none'}. "
        f"Prefixes for no registered record: {_TOOL_EXTRA or 'none'}. A record "
        f"that gained a pattern but no prefix would silently keep minting "
        f"sequential ids (CLAUDE.md rule 14; Sanaa 2026-08-31).")
if len(set(TOOL_ID_PREFIX.values())) != len(TOOL_ID_PREFIX):  # pragma: no cover
    raise SystemExit(
        f"REFUSED: two records share an allocation prefix "
        f"({TOOL_ID_PREFIX}) -- the cross-record non-collision property is the "
        f"prefix, so sharing one destroys it.")

#: RECORDS WHERE ALLOCATION IS REFUSED, and the reason is a MEASUREMENT.
#:
#: A record lands here when THE CONSTITUTION PRESCRIBES AN INTEGER DERIVATION
#: OVER IT THAT MISREADS THE MINTED FORM. That is a narrower test than "the
#: minted form is unusual here", and the difference decides three of the four
#: records, so it is spelled out:
#:
#:   * MISREAD  -- a prescribed reader PARSES the minted id and gets a WRONG
#:                 NUMBER. Silent, and it corrupts every later derivation.
#:   * INVISIBLE -- a reader cannot see the minted id at all. Also a defect, but
#:                 a DIFFERENT one, and its repair is on the READER, not here.
#:
#: MEASURED 2026-09-03, on HEAD's real bytes, one record at a time:
#:   docs/LESSONS.md            MISREAD.  CLAUDE.md rule 11 prescribes, verbatim,
#:     `grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n
#:      | tail -1`. That expression is a PREFIX match with NO TRAILING ANCHOR,
#:     while `RECORDS['docs/LESSONS.md']` requires a `.` or whitespace+em-dash
#:     after the digits. So the tool's reader is blind to the minted id and the
#:     CONSTITUTION'S reader is WRONG about it. Driven: over HEAD the derivation
#:     returns 479; over the same file plus ONE minted heading it returns
#:     20260903 -- about 42,000x the true maximum. ONE use would silently
#:     renumber every future lesson to a date, and nothing in this module would
#:     refuse: `parse_record_ids` is content, because `ANCHORED_TOOL_ID`
#:     recognises the minted id at entry position.
#:   docs/NUMERICS_KNOWLEDGE.md INVISIBLE, NOT MISREAD -- and therefore NOT here.
#:     The minted body opens with a DIGIT (`N-20260903T...`), and the family
#:     expressions that read this record are `N-[A-Z]+`, which requires a
#:     LETTER. Measured: `re.findall(r'N-[A-Z]+', 'N-20260903T...')` returns
#:     `[]`. Nothing misreads it; `scripts/check_numerics_index.py` simply does
#:     not list it. That is the reader's repair and it is already docketed.
#:   docs/DOCKET.md             INVISIBLE. Rule 11 names docket numbers but
#:     prescribes no grep for them -- it routes to
#:     `scripts/check_docket_reconciliation.py`, whose pattern requires the id
#:     cell to CLOSE after `[A-G]\d+[a-z]?`. Driven over a poisoned docket: 623
#:     ids parsed before and 623 after, delta 0. And 7 tool ids are already in
#:     production here.
#:   docs/COST_CALIBRATION.md   INVISIBLE, and the most-used record of the four:
#:     96 tool-allocated ids on HEAD (91 distinct). No integer derivation is
#:     prescribed over it anywhere.
#:
#: THE HONEST CAVEAT, WRITTEN DOWN RATHER THAN DISCOVERED LATER: DOCKET's and
#: COST_CALIBRATION's safety is the ABSENCE OF A PRESCRIBED READER, not
#: structural immunity. A loose `D-?[0-9]+` or `C-?[0-9]+` would extract
#: `D-20260903` / `C-20260903` exactly as rule 11's expression does for lessons
#: (measured). If a future document prescribes such a derivation, that record
#: belongs in this table THAT DAY. The re-read trigger in `CANNOT_SEE_OWNER`
#: already covers a heading-grammar change; this is the other half.
#:
#: THE ARM GENERALISES UNTESTED, AND THAT IS WRITTEN HERE RATHER THAN LEFT TO BE
#: DISCOVERED. `docs/LESSONS.md` is the ONLY member of this table, so every
#: control below it -- the refusal through `main()`, the near-misses, the
#: rule-11 regression, the clause-parity limbs -- has only ever been driven with
#: a ONE-ENTRY table. The code is written over `ALLOCATION_REFUSED` generally
#: and the clause-parity limbs already loop over every member, so a second entry
#: SHOULD be covered on the day it is added; that is a reasoned expectation and
#: NOT a measurement. WHOEVER ADDS THE SECOND RECORD: re-run `--selftest` and
#: check the new record appears in the clause-parity and near-miss limb NAMES,
#: because a limb that silently covers one record while reading as if it covers
#: the table is exactly the shape this module refuses elsewhere.
#:
#: WHY NOT MINT THE NEXT INTEGER INSTEAD, which is the obvious alternative:
#: `allocate_id`'s whole property is that it READS NOTHING THE RECORD CONTAINS,
#: "so the stale-tail failure mode has no mechanism here rather than merely no
#: instance" (its own docstring). Minting an integer requires reading the tail,
#: which hands that mechanism straight back -- a repair that reintroduces the
#: defect the design eliminated is not a repair. The caller uses
#: `--expect-first-id <integer>` here, which is the arithmetic-checked path.
ALLOCATION_REFUSED = {
    "docs/LESSONS.md": (
        "CLAUDE.md rule 11 prescribes an INTEGER derivation over this record -- "
        "`grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n "
        "| tail -1` -- and that expression has NO TRAILING ANCHOR, so it PARSES "
        "a minted id's leading DATE as the maximum. Measured 2026-09-03: 479 "
        "over the record as it stands, 20260903 over the same record plus ONE "
        "minted heading. One allocated lesson would silently renumber every "
        "later lesson to a date, and this module would not notice, because its "
        "own reader recognises the minted form and the constitution's does not. "
        "USE `--expect-first-id <integer>` INSTEAD: that is the arithmetic-"
        "checked path and it is judged against HEAD AND the preserved tail. "
        "Minting the next integer here was considered and REJECTED -- it would "
        "require reading the tail, which is precisely the stale-tail mechanism "
        "`allocate_id` was built to have no mechanism for"),
}
_ALLOC_REFUSED_EXTRA = sorted(set(ALLOCATION_REFUSED) - set(RECORDS))
if _ALLOC_REFUSED_EXTRA:  # pragma: no cover - a load-time refusal
    raise SystemExit(
        f"REFUSED: ALLOCATION_REFUSED names records that are not registered: "
        f"{_ALLOC_REFUSED_EXTRA}. A refusal keyed to a path no caller can pass "
        f"is a guard that cannot fire.")

#: The placeholder a caller writes where the id goes. Deliberately a form that
#: cannot occur in a lesson, a docket row or a cost row by accident, and that is
#: LOUD if it ever escapes into a record -- which is why a placeholder without
#: `--allocate-id` is a refusal rather than a literal write.
ALLOCATE_PLACEHOLDER = "{{ALLOCATE_ID}}"

#: The body of every tool-allocated id: a fixed-width UTC stamp, TO THE
#: MICROSECOND, and 8 hex. Fixed width is not cosmetic -- it is what makes a
#: lexicographic sort within a prefix equal a chronological one.
#:
#: WHY THE MICROSECONDS ARE VISIBLE, AND HOW THAT WAS DECIDED. This constant
#: first read `\d{8}T\d{6}Z-[0-9a-f]{8}` -- second resolution, on the reasoning
#: that seconds are what a human cites and the sub-second component could live
#: inside the hash. THE PLANTED CONTROL REFUSED IT. Its limb "the ids on disk
#: sort chronologically as plain strings" failed on the first run, because both
#: ids of the two-run limb were minted inside the SAME second
#: (`C-20260831T155703Z-7ea719d2` then `C-20260831T155703Z-6cebd14b`) and so
#: sorted by their HASHES, in the reverse of the order they were written. The
#: sortability requirement was therefore FALSE AS WRITTEN, at exactly the
#: resolution at which this tool is used -- two agents appending in the same
#: second is the normal case here, not the corner. Seven characters buy the
#: property outright, and they also narrow the honest residue: two ids now have
#: to share a MICROSECOND as well as a 32-bit hash to collide. The limb was
#: fixed by fixing the format, not by weakening the claim to "non-decreasing
#: timestamps", which is what a limb written after the measurement would have
#: said.
TOOL_ID_BODY = r"\d{8}T\d{6}\.\d{6}Z-[0-9a-f]{8}"

#: ANY record's tool-allocated id, whatever the prefix. `check_allocation` uses
#: THIS rather than the per-record form, so a caller cannot smuggle a hand-
#: written id in by spelling it with another record's letter.
ANY_TOOL_ID = rf"(?<![0-9A-Za-z])([A-Z]{{1,3}}-{TOOL_ID_BODY})(?![0-9A-Za-z-])"

# ------------------------------------------------- THE `corrects:` FIELD
# Sanaa's PLUMBING AMENDMENT, 2026-09-03, captured verbatim at
# `etc/sessions/2026-09-03T1600Z_sanaa_five_rulings.md:5-8`:
#
#     "Plumbing amendment: append_record.py accepts tool-allocated ids solely
#     inside a structured corrects: field on correction rows; refusal unchanged
#     everywhere else. The side-file workaround is retired and its parked ids
#     migrated."
#
# WHAT WAS BROKEN, MEASURED AND DOCKETED BEFORE THIS EXISTED
# ----------------------------------------------------------
# `docs/COST_CALIBRATION.md`'s append rule 1 requires a correction to be "a new
# row naming the row it corrects". `check_allocation`'s smuggle guard refuses
# (exit 9) any rows file carrying a tool-form id ANYWHERE in its text, "for ANY
# record's prefix rather than only this record's". Once ids became
# tool-allocated the two became JOINTLY UNSATISFIABLE, and the refusal was
# reproduced TWICE on 2026-09-02: on the calibration correction row itself, and
# again on the docket row filed to describe the collision, which was refused for
# citing the id of the correction row it described
# (`docs/DOCKET.md` row `D-20260902T224505.958199Z-e02eb14e`).
#
# The workaround adopted then, and RETIRED by this amendment: the rows named
# their target by date, team, subject and its 8-hex suffix, and the full ids were
# parked in `docs/campaigns/T-family/T23G2_RESULTS.md` §16.1, a file this tool
# does not append. Its own disclosure is the argument for this repair -- "it
# degrades a citation from an exact key to a description, and a reader grepping
# a full id will not find the row that cites it."
#
# THE SCOPING, AND WHY IT IS THREE CLAUSES AND NOT ONE
# ---------------------------------------------------
# The guard's purpose was never "no tool id in the bytes". Its purpose is that
# THIS MODULE IS THE ONLY PRODUCER OF AN ID AT AN ENTRY POSITION, so a duplicate
# cannot be reintroduced by an edit. A prose citation is not an entry. So the
# acceptance is scoped by three INDEPENDENT clauses, each with its own planted
# limb and its own mutation:
#
#   (C1) FIELD-SCOPED. The id sits inside a well-formed `corrects:[...]` field.
#        Anything malformed REFUSES rather than degrading to "not a field" --
#        a half-written field must not fall through to a message about
#        smuggling, which would be the right refusal with the wrong diagnosis.
#   (C2) CORRECTION-ROW-SCOPED. The line carrying that field declares itself a
#        correction IN ITS OWN RECORD'S VOCABULARY, anchored at the head of the
#        entry. Measured against the live corpus 2026-09-03, not assumed.
#   (C3) NEVER AT AN ENTRY POSITION. The line must ALSO carry its own legitimate
#        id -- an `{{ALLOCATE_ID}}` placeholder about to be filled, or a legacy
#        id this record's own pattern parses. A row whose only id is a citation
#        is refused, so an accepted citation can never BE the row's id.
#
# The acceptance is implemented as a MASK, not as a second refusal path: every
# field satisfying C1-C3 is blanked out of a COPY of the rows text and the
# EXISTING smuggle scan then runs over the residue, byte-for-byte the code it
# was before. That is what makes "refusal unchanged everywhere else" a property
# of the construction rather than a claim about it -- there is one scan, and the
# amendment only decides what it is shown.
#
# WHAT WOULD DEFEAT THIS SCOPING, STATED PLAINLY
# ----------------------------------------------
#   * A CALLER WHO DECLARES A NON-CORRECTION ROW A CORRECTION. C2 reads a
#     DECLARATION; no instrument can verify the semantic claim behind it. What
#     C2 buys is that the declaration is explicit, anchored and greppable -- not
#     that it is true.
#   * A CITATION TO AN ID THAT DOES NOT EXIST. Deliberately NOT checked, and the
#     reason is the case that motivated the amendment: the docket row cites
#     `C-` ids, so resolution would have to read a DIFFERENT record. Reading a
#     second record here would give this module a new failure mode and a new
#     blindness, so the dangling-citation residue is NAMED rather than closed.
#   * `docs/LESSONS.md` AND `docs/NUMERICS_KNOWLEDGE.md` HAVE NO LIVE CORRECTION
#     ROW. Measured 2026-09-03: `CORRECTION ROW` occurs 17 times in
#     COST_CALIBRATION and 0 times in either of those two. Their markers below
#     are spelled in their own vocabulary and are UNEXERCISED BY THE CORPUS --
#     only the planted controls drive them. A record must never borrow another's
#     shapes (this module's standing rule; CLAUDE.md rule 14).
#
#: The opener. MEASURED 2026-09-03: `corrects:[` occurs ZERO times anywhere in
#: the repository, while the bare prose form `corrects:` occurs 4 times in the
#: guarded records (`corrects: \`C` x3, `corrects: th` x1) -- so the bracket is
#: what separates the field from every live prose usage, and it is not
#: decoration. A line carrying this opener is COMMITTED to being a field: if it
#: then fails to parse, it REFUSES.
CORRECTS_OPENER = "corrects:["

#: The whole field, opener to close, on ONE line. `[^\]\n]*` cannot cross a line
#: boundary or swallow a second field.
CORRECTS_FIELD = re.compile(re.escape(CORRECTS_OPENER) + r"(?P<body>[^\]\n]*)\]")

#: The body: one or more tool-allocated ids, `;`-separated, NO whitespace and
#: nothing else. DELIBERATELY NARROW. A LEGACY id needs no field -- it was never
#: refused by the smuggle guard -- so admitting one here would widen the parse
#: for a case that has no defect, and a widened parse is what has to be argued
#: about later. A legacy citation in a field is therefore MALFORMED, and the
#: refusal says so in those words rather than reporting a smuggle.
CORRECTS_BODY = re.compile(
    rf"[A-Z]{{1,3}}-{TOOL_ID_BODY}(?:;[A-Z]{{1,3}}-{TOOL_ID_BODY})*")

#: THE CORRECTION DECLARATION, one per record, keyed identically to `RECORDS`.
#:
#: MEASURED 2026-09-03 against the real files, both worktree and HEAD's blob,
#: and the anchor is load-bearing rather than tidy:
#:   docs/COST_CALIBRATION.md : 17 lines carry `CORRECTION ROW`; ALL 17 open the
#:                              ENTRY CELL with it, modulo `**` -- the form below
#:                              matches 17 of 17.
#:   docs/DOCKET.md           : 1 line carries `CORRECTION ROW` (`:957`) and it
#:                              opens `**A CORRECTION ROW CANNOT NAME THE ROW IT
#:                              CORRECTS`. That row is ABOUT the defect; it is
#:                              NOT a correction row. The anchor EXCLUDES it,
#:                              and a planted negative drives that exact live
#:                              line -- an unanchored `CORRECTION ROW` anywhere
#:                              in the line would classify it wrongly.
#:   docs/LESSONS.md          : 0 lines. UNEXERCISED BY THE CORPUS.
#:   docs/NUMERICS_KNOWLEDGE.md: 0 lines. UNEXERCISED BY THE CORPUS.
#:
#: TRAP: the table form counts CELLS -- `^\|` then three `[^|]*\|` groups gets
#: past `| id | date | team |` to the entry cell, so the declaration cannot be
#: satisfied from the id cell, the date cell or the team cell. It assumes no
#: cell contains a bare `|`, which is the assumption every one of this record's
#: patterns already makes.
_CORRECTION_TABLE_ROW = (r"^\|(?:[^|]*\|){3}[ \t]*(?:\*\*|~~)*[ \t]*"
                         r"CORRECTION ROW\b")
CORRECTION_MARKER = {
    "docs/DOCKET.md": _CORRECTION_TABLE_ROW,
    "docs/COST_CALIBRATION.md": _CORRECTION_TABLE_ROW,
    # The heading's own vocabulary: an h2 entry whose TITLE opens `CORRECTION`,
    # after the id and its period-or-em-dash separator. Spelled from this
    # record's live heading grammar (`RECORDS`/`CANDIDATE_SHAPES` above), never
    # borrowed from the table records.
    "docs/LESSONS.md": r"^##[ \t]*\S+[ \t]*(?:\.|[ \t]+—)[ \t]*"
                       r"(?:\*\*)*[ \t]*CORRECTION\b",
    # Either live entry form -- bold or h2 -- whose title opens `CORRECTION`.
    "docs/NUMERICS_KNOWLEDGE.md": r"^(?:\*\*|## )\S+\.[ \t]*(?:\*\*)*[ \t]*"
                                  r"CORRECTION\b",
}

_CORR_MISSING = sorted(set(RECORDS) - set(CORRECTION_MARKER))
_CORR_EXTRA = sorted(set(CORRECTION_MARKER) - set(RECORDS))
if _CORR_MISSING or _CORR_EXTRA:  # pragma: no cover - a load-time refusal
    raise SystemExit(
        f"REFUSED: CORRECTION_MARKER and RECORDS disagree. Records with an id "
        f"pattern but no correction declaration: {_CORR_MISSING or 'none'}. "
        f"Declarations for no registered record: {_CORR_EXTRA or 'none'}. A "
        f"record with no marker could never file a correction row through this "
        f"tool, which is the defect this field exists to repair, and one that "
        f"borrowed another record's marker would accept a shape its own file "
        f"does not write (CLAUDE.md rule 14; Sanaa 2026-09-03).")

#: Minted strictly in-process and folded into the hash, so two ids minted in the
#: same microsecond by the SAME process cannot agree even before the urandom
#: contribution is considered.
_ALLOC_SEQ = itertools.count()


def tool_id_pattern(path: str) -> str:
    """The regex recognising *this* record's tool-allocated ids ANYWHERE.

    UNANCHORED, deliberately. Two callers need it that way and neither is a
    reader of entries: `shape_audit`, which must recognise a tool id anywhere on
    a candidate line before deciding the line is an offender, and the smuggle
    guard, which must catch a hand-written id wherever a caller hid it. For
    COUNTING ENTRIES use `ANCHORED_TOOL_ID` -- see the trap recorded there.
    """
    return (rf"(?<![0-9A-Za-z])({re.escape(TOOL_ID_PREFIX[path])}-"
            rf"{TOOL_ID_BODY})(?![0-9A-Za-z-])")


def is_tool_id(row_id: str) -> bool:
    """True for a well-formed tool-allocated id of ANY record's prefix."""
    return re.fullmatch(rf"[A-Z]{{1,3}}-{TOOL_ID_BODY}", row_id) is not None


#: THE ENTRY-POSITION ANCHOR of each record, with `{id}` where the id sits.
#: Each is its own `RECORDS` entry with the LEGACY id expression lifted out and
#: nothing else changed, so a tool-allocated entry is recognised at EXACTLY the
#: position a legacy entry is recognised -- first table cell, or the head of an
#: h2/bold heading -- and nowhere else.
#:
#: THE TRAP THIS EXISTS FOR, AND IT IS NOT HYPOTHETICAL. `tool_id_pattern` is
#: unanchored, and `allocate_into_rows` replaces EVERY occurrence of the
#: placeholder ON A LINE with that line's id -- a documented feature, so a row
#: can cite its own id in its own prose. Counting entries with the UNANCHORED
#: pattern therefore reads such a row as TWO ids wearing one name, and
#: `check_record_reconciliation`'s duplicate branch would return rc 4 on a row
#: that is perfectly correct. A planted control drives exactly that row.
#:
#: The same anchoring is what stops a tool id MENTIONED IN PROSE from being
#: counted as an entry -- the property every legacy pattern already has, and
#: which every record's control asserts as a NEGATIVE form.
_TOOL_ID_ANCHOR = {
    "docs/DOCKET.md": r"^\|\s*(?:\*\*|~~)*\s*({id})\s*(?:~~|\*\*)*\s*\|",
    "docs/LESSONS.md": r"^## ({id})(?:\.|\s+—)",
    "docs/NUMERICS_KNOWLEDGE.md": r"^(?:\*\*|## )({id})\.",
    "docs/COST_CALIBRATION.md": r"^\|\s*(?:\*\*|~~)*\s*({id})\s*(?:~~|\*\*)*\s*\|",
}

_ANCHOR_MISSING = sorted(set(RECORDS) - set(_TOOL_ID_ANCHOR))
_ANCHOR_EXTRA = sorted(set(_TOOL_ID_ANCHOR) - set(RECORDS))
if _ANCHOR_MISSING or _ANCHOR_EXTRA:  # pragma: no cover - a load-time refusal
    raise SystemExit(
        f"REFUSED: _TOOL_ID_ANCHOR and RECORDS disagree. Records with an id "
        f"pattern but no entry-position anchor: {_ANCHOR_MISSING or 'none'}. "
        f"Anchors for no registered record: {_ANCHOR_EXTRA or 'none'}. A record "
        f"with no anchor would have its tool-allocated entries counted by the "
        f"UNANCHORED pattern, which reads a self-citing row as a duplicate "
        f"(CLAUDE.md rule 14).")

#: One ANCHORED tool-id pattern per record, built from the anchor above and
#: `TOOL_ID_PREFIX`, so the prefix has exactly one definition and cannot drift.
ANCHORED_TOOL_ID = {
    path: anchor.format(id=re.escape(TOOL_ID_PREFIX[path]) + "-" + TOOL_ID_BODY)
    for path, anchor in _TOOL_ID_ANCHOR.items()
}

# EXACTLY ONE CAPTURING GROUP PER PATTERN, asserted rather than assumed:
# `parse_record_ids` builds a two-branch alternation and reads group 1 or
# group 2. A pattern that grew a second group would silently shift that
# numbering and the reader would return fragments of ids instead of ids.
for _p in sorted(RECORDS):
    for _label, _pat in (("RECORDS", RECORDS[_p]),
                         ("ANCHORED_TOOL_ID", ANCHORED_TOOL_ID[_p])):
        _n = re.compile(_pat).groups
        if _n != 1:  # pragma: no cover - a load-time refusal
            raise SystemExit(
                f"REFUSED: {_label}[{_p!r}] has {_n} capturing groups, not 1. "
                f"parse_record_ids reads group 1 or group 2 of a two-branch "
                f"alternation, so any other count returns the wrong text as an "
                f"id. Spell every inner group `(?:...)`.")
del _p, _label, _pat, _n


def parse_record_ids(text: str, path: str) -> list[str]:
    """EVERY id in *text* for *path* -- LEGACY and TOOL-ALLOCATED -- in order.

    THIS IS THE READER THE RECONCILERS USE, and it is the other half of Sanaa's
    2026-08-31 directive. `parse_ids(text, RECORDS[path])` sees legacy ids ONLY,
    so the day allocation is used a tool-allocated row sitting unlanded in a
    worktree is INVISIBLE to `check_record_reconciliation` -- it would report
    PASS over a row it cannot see, which is this team's own fail-open class
    (`docs/FAIL_OPEN_GATE_AUDIT.md` sections 13 and 14). A writer whose reader
    cannot see what it writes is a dead lever the day it ships.

    Both branches are `^`-anchored, so at a line start the legacy branch is
    tried first and a line can satisfy at most one; the result is document
    order, and the legacy id list is BYTE-FOR-BYTE the list `parse_ids` returned
    before this reader existed. That equality is measured on the four real
    records by a planted control, not asserted here.
    """
    combined = re.compile(f"(?:{RECORDS[path]})|(?:{ANCHORED_TOOL_ID[path]})",
                          re.M)
    return [m.group(1) if m.group(1) is not None else m.group(2)
            for m in combined.finditer(text)]


def allocate_id(path: str, row_bytes: bytes, *,
                now: datetime | None = None,
                entropy: bytes | None = None) -> str:
    """Mint ONE tool-allocated id for *path*.

    READS NOTHING THE RECORD CONTAINS. That is the whole property: a value
    derived from no shared state cannot be stale with respect to it, so the
    stale-tail failure mode has no mechanism here rather than merely no
    instance. Everything folded into the hash is either local to this process or
    random.

    `now` and `entropy` exist ONLY so a planted control can FORCE a collision
    and show the non-presence assert catch it -- a guard never driven into its
    refusal is a guard nobody has seen work. `main()` passes neither.
    """
    prefix = TOOL_ID_PREFIX[path]
    t = datetime.now(timezone.utc) if now is None else now
    stamp = t.strftime("%Y%m%dT%H%M%S.%fZ")   # %f is zero-padded to 6, so the
    #                                           width is fixed and the sort holds
    material = b"\x1f".join([
        prefix.encode(),
        path.encode(),
        t.isoformat().encode(),            # carries the microseconds
        str(os.getpid()).encode(),
        socket.gethostname().encode(),
        str(next(_ALLOC_SEQ)).encode(),
        row_bytes,
        os.urandom(16) if entropy is None else entropy,
    ])
    return f"{prefix}-{stamp}-{hashlib.blake2b(material, digest_size=4).hexdigest()}"


def allocate_into_rows(rows_text: str, path: str, *,
                       now: datetime | None = None,
                       entropy: bytes | None = None) -> tuple[str, list[str]]:
    """Replace every `{{ALLOCATE_ID}}`, ONE FRESH ID PER LINE that carries it.

    Per line, not per occurrence, so a row can cite its own id inside its own
    prose and still be one row with one id. Pure with respect to the record --
    it never consults HEAD, the tail, or any other row.
    """
    out, ids = [], []
    for line in rows_text.splitlines(keepends=True):
        if ALLOCATE_PLACEHOLDER not in line:
            out.append(line)
            continue
        row_id = allocate_id(path, line.encode(), now=now, entropy=entropy)
        ids.append(row_id)
        out.append(line.replace(ALLOCATE_PLACEHOLDER, row_id))
    return "".join(out), ids


def scan_corrects(rows_text: str, path: str, *,
                  require_correction_marker: bool = True,
                  require_own_entry: bool = True) -> dict:
    """C1-C3. Decide which `corrects:[...]` fields are ACCEPTED, and MASK them.

    Pure, and it never accepts anything on its own: it returns a MASKED COPY of
    the rows, and the existing smuggle scan is what refuses. Masking replaces an
    accepted field with spaces of the SAME LENGTH, so every line number and
    column reported downstream is the caller's own.

    Returns `{ok, code, reason, masked, cited, rows}` -- `rows` being the line
    numbers that carried an accepted field, for the report.

    The two mutation knobs reproduce this function with exactly one clause
    removed, so a planted control can drive each and show its limb flip. Nothing
    in `main()` passes either.
    """
    marker = re.compile(CORRECTION_MARKER[path])
    entry = re.compile(RECORDS[path], re.M)
    out, cited, rows = [], [], []
    for n, line in enumerate(rows_text.splitlines(keepends=True), 1):
        if CORRECTS_OPENER not in line:
            out.append(line)
            continue
        # (C2) the line must DECLARE itself a correction, in this record's own
        # vocabulary and ANCHORED at the head of its entry. A citation field on
        # an ordinary row is refused: the acceptance is for correction rows and
        # for nothing else (Sanaa 2026-09-03).
        if require_correction_marker and not marker.search(line):
            return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
                f"line {n} of the rows carries a {CORRECTS_OPENER!r} field but "
                f"is NOT a correction row for {path}: it does not open its "
                f"entry with this record's correction declaration "
                f"({CORRECTION_MARKER[path]!r}). Sanaa's 2026-09-03 amendment "
                f"admits a tool-allocated id SOLELY inside a structured "
                f"corrects: field ON A CORRECTION ROW, so a citation field "
                f"anywhere else is refused rather than ignored -- ignoring it "
                f"would leave the id to be reported as a smuggle, which is the "
                f"right refusal with the wrong diagnosis. Line: "
                f"{line.strip()[:160]!r}"),
                "masked": None, "cited": [], "rows": []}
        # (C1) every opener on the line must parse. A line carrying the opener
        # is COMMITTED to being a field; a half-written one refuses.
        masked, cursor, n_fields = [], 0, 0
        for m in CORRECTS_FIELD.finditer(line):
            body = m.group("body")
            if CORRECTS_BODY.fullmatch(body) is None:
                return {"ok": False, "code": EXIT_REFUSED_ALLOCATION,
                        "reason": (
                            f"line {n} of the rows carries a MALFORMED "
                            f"corrects: field {m.group(0)[:120]!r}. The body "
                            f"must be one or more TOOL-ALLOCATED ids, "
                            f"';'-separated, with no whitespace and nothing "
                            f"else -- e.g. "
                            f"{CORRECTS_OPENER}C-20260902T215932.385336Z-"
                            f"ef920ed2]. A LEGACY id ('C-179', 'D471') needs no "
                            f"field: the smuggle guard never refused one, so "
                            f"citing it in prose is unchanged and correct. This "
                            f"parse is deliberately narrow, and a field that "
                            f"does not parse is a refusal rather than a "
                            f"fallback to prose."),
                        "masked": None, "cited": [], "rows": []}
            cited.extend(body.split(";"))
            masked.append(line[cursor:m.start()])
            masked.append(" " * (m.end() - m.start()))
            cursor = m.end()
            n_fields += 1
        masked.append(line[cursor:])
        if n_fields == 0:
            # The opener is present and `CORRECTS_FIELD` matched nothing at all:
            # it never closes on this line.
            return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
                f"line {n} of the rows opens a {CORRECTS_OPENER!r} field that "
                f"never closes with ']' on that line. The field is one line, "
                f"opener to close; an unterminated one is refused rather than "
                f"read as prose."),
                "masked": None, "cited": [], "rows": []}
        # (C3) the row must carry its OWN id at its OWN entry position -- a
        # placeholder about to be filled, or a legacy id this record parses.
        # This is what makes an accepted citation structurally unable to BE the
        # row's id: a row whose only id is a citation does not land.
        #
        # HARDENED 2026-09-03, ON THE SUPERVISOR'S READING OF THE DIFF, and it
        # is the difference between correct and correct-for-a-reason. This
        # clause first read `entry.search(line)` -- the RAW line, which still
        # carries the cited id inside its `corrects:[...]` field. The cited id
        # was therefore itself a CANDIDATE for satisfying "the row has its own
        # id". It could not win TODAY, and only because every pattern in
        # `RECORDS` happens to be `^`-anchored: with `re.M` on a single line
        # `^` matches at position 0 alone, so a mid-line citation can never
        # match. That is a property of a DIFFERENT constant, not of this
        # clause -- loosen any record's id pattern to an unanchored one and
        # this clause silently stops guarding, while the arm that "proves" it
        # keeps passing for the wrong reason. VERIFICATION_CHARTER §2p.5: a
        # repair that changes which coincidence you depend on is not a repair.
        # Searching the MASKED line removes the dependency outright -- the
        # citation is blanked to same-length spaces before this clause looks,
        # so it cannot be the row's own id under ANY pattern, anchored or not.
        # The placeholder limb keeps reading the raw line on purpose: a
        # placeholder is never inside a `corrects:` field (the body parse
        # admits tool-allocated ids and nothing else), so masking cannot hide
        # one, and reading the raw line there is the honest statement of what
        # is being asked. The masked line is what `out` already receives below,
        # so this clause and the smuggle scan now see the SAME bytes.
        masked_line = "".join(masked)
        own = (ALLOCATE_PLACEHOLDER in line) or bool(entry.search(masked_line))
        if require_own_entry and not own:
            return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
                f"line {n} of the rows carries an accepted corrects: field but "
                f"NO id of its own at {path}'s entry position -- neither "
                f"{ALLOCATE_PLACEHOLDER!r} nor an id this record's pattern "
                f"({RECORDS[path]!r}) can parse. A correction row is a NEW ROW "
                f"and must carry its own id; accepting a citation on a row with "
                f"no id of its own would let the cited id be the only id in the "
                f"line, which is the entry-position case the smuggle guard "
                f"exists to refuse. Write {ALLOCATE_PLACEHOLDER!r} in the id "
                f"cell and pass --allocate-id."),
                "masked": None, "cited": [], "rows": []}
        rows.append(n)
        out.append(masked_line)
    return {"ok": True, "code": EXIT_OK, "reason": "",
            "masked": "".join(out), "cited": cited, "rows": rows}


def check_allocation(rows_text: str, path: str, *, allocate: bool,
                     expect_first_id: str | None = None,
                     apply_smuggle_guard: bool = True,
                     apply_corrects: bool = True,
                     require_correction_marker: bool = True,
                     require_own_entry: bool = True,
                     apply_allocation_scope: bool = True) -> dict:
    """The preconditions, BEFORE anything is minted or merged. Pure.

    `apply_smuggle_guard=False` reproduces this module WITHOUT the clause that
    makes it the sole producer of tool-form ids; it exists so a planted control
    can drive that mutation and show the limb flips. Nothing in `main()` passes
    it.

    `apply_corrects=False` reproduces this module BEFORE Sanaa's 2026-09-03
    amendment -- no citation is ever accepted -- and the other two knobs remove
    clause C2 and clause C3 respectively. All three exist for the same reason
    and `main()` passes none of them.

    `apply_allocation_scope=False` reproduces this module BEFORE the 2026-09-03
    scope ruling -- allocation permitted on EVERY registered record, including
    `docs/LESSONS.md`. It exists so the rule-11 regression control can BUILD the
    file that would otherwise exist and measure what rule 11 reads off it.
    `main()` passes none of these knobs.

    THE SMUGGLE SCAN BELOW IS UNCHANGED. It runs over `scan_text`, which is the
    rows themselves in every case except an accepted correction-row citation, so
    "refusal unchanged everywhere else" is a property of the construction: there
    is one scan and one message, and the amendment only decides what it sees.
    """
    # ---- ALLOCATION SCOPE, decided on `path` and `allocate` ALONE -----------
    # FIRST, because it is settled before a byte of the rows matters and before
    # anything is minted; and it is a REFUSAL, not an instrument error, so it
    # takes this module's existing allocation-precondition code rather than
    # VERIFICATION_CHARTER section 2ak's `70`, which that clause reserves for a
    # comparator's INTERNAL ERROR and explicitly rules "is not a refusal".
    # No new exit value is invented: section 2ak's own finding is that
    # `EXIT_REFUSE` had already drifted to two values, so adding a third
    # spelling of "refused" is the error it names.
    if allocate and apply_allocation_scope and path in ALLOCATION_REFUSED:
        return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
            f"--allocate-id is REFUSED for {path}. "
            f"{ALLOCATION_REFUSED[path]}.")}
    scan_text = rows_text
    corrects = None
    if apply_corrects and CORRECTS_OPENER in rows_text:
        corrects = scan_corrects(
            rows_text, path,
            require_correction_marker=require_correction_marker,
            require_own_entry=require_own_entry)
        if not corrects["ok"]:
            return {"ok": False, "code": corrects["code"],
                    "reason": corrects["reason"]}
        scan_text = corrects["masked"]
    smuggled = re.findall(ANY_TOOL_ID, scan_text)
    if smuggled and apply_smuggle_guard:
        return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
            f"the rows HAND-WRITE tool-allocated id(s) {sorted(set(smuggled))}. "
            f"This module is the ONLY producer of that form, and that is the "
            f"entire reason a duplicate cannot be reintroduced by an edit: a "
            f"hand-written id is a number somebody chose, which is the {path} "
            f"C-217/L-404 mechanism in new clothes. Write "
            f"{ALLOCATE_PLACEHOLDER!r} and pass --allocate-id instead (Sanaa's "
            f"PLUMBING FREEZE directive, 2026-08-31). "
            # APPENDED 2026-09-03, and it changes WHAT IS SAID, never WHAT IS
            # REFUSED: the sentence above was the whole advice when the only way
            # a tool id could reach the rows was a hand-written entry, and it is
            # now incomplete for the CITATION case that Sanaa's amendment
            # admits. The refusal itself, its code and its population are
            # unchanged, which is what the planted arms measure.
            f"IF THIS IS A CITATION rather than an id cell -- a correction row "
            f"naming the row it corrects -- put it in a structured "
            f"{CORRECTS_OPENER}<id>] field on a row that opens with this "
            f"record's correction declaration, which is the SOLE place a "
            f"tool-allocated id is accepted (Sanaa's PLUMBING AMENDMENT, "
            f"2026-09-03).")}
    has_placeholder = ALLOCATE_PLACEHOLDER in rows_text
    if allocate and expect_first_id:
        return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
            f"--allocate-id was passed with --expect-first-id "
            f"{expect_first_id!r}. An id that does not exist until this call "
            f"cannot have been expected, and an expectation that could not be "
            f"evaluated is not one that was met (the D549 clause 1a reasoning, "
            f"applied to allocation).")}
    if allocate and not has_placeholder:
        return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
            f"--allocate-id was passed but the rows contain no "
            f"{ALLOCATE_PLACEHOLDER!r} to fill, so nothing would be allocated "
            f"and the rows would land carrying whatever id they already have. "
            f"Refusing rather than writing, because a silent no-op here is how "
            f"a caller comes to believe the tool minted an id it did not.")}
    if has_placeholder and not allocate:
        return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
            f"the rows carry {ALLOCATE_PLACEHOLDER!r} but --allocate-id was not "
            f"passed, so the placeholder would be written into the record "
            f"LITERALLY. A record row whose id reads {ALLOCATE_PLACEHOLDER!r} "
            f"is worse than either intended outcome, so this refuses.")}
    return {"ok": True, "code": EXIT_OK, "reason": "",
            "cited": corrects["cited"] if corrects else [],
            "corrects_rows": corrects["rows"] if corrects else []}


def check_allocated_unique(allocated: list[str], existing_text: str) -> dict:
    """The non-presence assert: a minted id must be new to the merged file.

    This is the ONLY place allocation reads the record, and it is read-only in
    the direction that matters -- it can make the tool REFUSE, and a refusal
    cannot mint a duplicate. So it is a backstop on the honest residue (two
    processes, same UTC second, same 32-bit hash), never the uniqueness
    mechanism, which is that nothing is derived from shared state at all.
    """
    dup_in_batch = sorted({i for i in allocated if allocated.count(i) > 1})
    already = sorted({i for i in allocated if i in existing_text})
    if dup_in_batch or already:
        return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
            f"a minted id is not new: repeated within this batch "
            f"{dup_in_batch or 'none'}; already present in the committed blob "
            f"or the preserved worktree tail {already or 'none'}. Nothing was "
            f"written. This is the backstop, not the mechanism -- if it ever "
            f"fires, the clock, the entropy source or the batch loop is wrong "
            f"and that is a finding, not a retry.")}
    return {"ok": True, "code": EXIT_OK, "reason": ""}


def split_id(row_id: str) -> tuple[str, int, str]:
    """('N-B26') -> ('N-B', 26, ''). Series prefix, number, optional suffix."""
    m = re.match(r"^(.*?)(\d+)([a-z]?)$", row_id)
    if m is None:  # pragma: no cover - the patterns cannot produce this
        return (row_id, 0, "")
    return (m.group(1), int(m.group(2)), m.group(3))


def parse_ids(text: str, pattern: str) -> list[str]:
    """Every id in *text*, in order. Duplicates preserved for the caller."""
    return re.compile(pattern, re.M).findall(text)


def max_for_series(ids: list[str], series: str) -> int | None:
    """The MAXIMUM EXISTING NUMBER in *series*, never a count (CLAUDE.md 11)."""
    nums = [n for (p, n, _) in map(split_id, ids) if p == series]
    return max(nums) if nums else None


#: A candidate that can never match anything, used by the planted controls to
#: reproduce the PRE-REPAIR state -- clause 1b removed -- and show the limb
#: flips. It is a named constant rather than a literal inside the control so
#: that the mutation is visible from the code being mutated.
NEVER_A_CANDIDATE = r"(?!)"


def shape_audit(text: str, path: str, origin: str, *,
                pattern: str | None = None,
                candidate: str | None = None,
                excluded: "tuple[str, ...] | None" = None,
                apply_excluded: bool = True,
                apply_tool_ids: bool = True) -> list[dict]:
    """D549 CLAUSE 1b. Lines that LOOK id-bearing but yield no id.

    Returns one dict per offending line -- `{line_no, line, origin}` -- so the
    refusal can NAME the line and where it came from rather than reporting a
    count. An empty list means every candidate line either parsed or is
    known-excluded; it does NOT mean the file has no ids.

    A line carrying a well-formed TOOL-ALLOCATED id for this record is NOT an
    offender, and that clause is load-bearing rather than cosmetic: every
    candidate shape is broader than its id pattern, so `## L-20260831T...` and
    `| C-20260831T... |` match their record's candidate while the LEGACY id
    pattern correctly parses nothing from them. Without this clause the tool
    would refuse, at exit 7, every row it had itself just allocated -- on the
    very next append, when that row is sitting in the preserved worktree tail.
    `apply_tool_ids=False` is that state, and a planted control drives it.

    Pure and fully parameterised, so the planted controls drive the mutations
    directly: `candidate=NEVER_A_CANDIDATE` is this module BEFORE the repair,
    and `apply_excluded=False` is the repair with its exclusion set removed.
    Each of those must flip a limb, or the limb was testing nothing.

    Line matching uses `search` on ONE line at a time with `re.M`, so a
    `^`-anchored pattern -- all four are -- decides exactly as `parse_ids`
    would over the whole text, and no expression can straddle a line boundary.
    """
    pat = re.compile(RECORDS[path] if pattern is None else pattern, re.M)
    cand = re.compile(CANDIDATE_SHAPES[path] if candidate is None
                      else candidate, re.M)
    excl = [re.compile(e, re.M) for e in
            ((KNOWN_EXCLUDED[path] if excluded is None else excluded)
             if apply_excluded else ())]
    tool = re.compile(tool_id_pattern(path), re.M) if apply_tool_ids else None
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if not cand.search(line):
            continue
        if pat.search(line):
            continue
        if tool is not None and tool.search(line):
            continue
        if any(e.search(line) for e in excl):
            continue
        out.append({"line_no": n, "line": line, "origin": origin})
    return out


def check_expectation(expect: str | None, new_ids: list[str], *,
                      legacy_gate: bool = False) -> dict:
    """D549 CLAUSE 1a. An expectation that could not be EVALUATED is a refusal.

    Deliberately independent of every id pattern: it takes the expectation and
    the parsed ids and nothing else, so its planted control proves the reported
    hole is closed WITHOUT any regex change standing behind the proof.

    `legacy_gate=True` reproduces `main()`'s PRE-REPAIR shape, in which the
    whole id gate sat inside `if new_ids:` and an unparseable heading therefore
    returned OK. That branch exists ONLY so a planted control can drive the
    mutation and show the limb flips; nothing in `main()` passes it.
    """
    if legacy_gate and not new_ids:
        return {"ok": True, "code": EXIT_OK, "reason": (
            "PRE-REPAIR SHAPE: the entire id gate was skipped because no ids "
            "were parsed. This is the D549 fail-open itself, reachable only "
            "from the planted controls.")}
    if expect and not new_ids:
        return {"ok": False, "code": EXIT_REFUSED_EXPECTATION_UNEVALUABLE,
                "reason": (
                    f"--expect-first-id {expect!r} was passed and the id "
                    f"pattern parsed ZERO ids from the rows, so the "
                    f"expectation could not be EVALUATED. An expectation that "
                    f"could not be evaluated is not an expectation that was "
                    f"met, and returning 0 here is how this tool wrote rows "
                    f"whose id nothing had checked (D549, verification "
                    f"a0e2e9a2). Either the rows carry no id at all, or they "
                    f"carry one in a form this record's pattern cannot see -- "
                    f"and those two are not the same finding, so neither is "
                    f"assumed.")}
    return {"ok": True, "code": EXIT_OK, "reason": ""}


def check_first_id(head_ids: list[str], tail_ids: list[str],
                   new_ids: list[str]) -> dict:
    """Judge the first appended id against HEAD **and the preserved tail**.

    Pure, so the planted controls drive it on fixtures rather than on a repo.

    The tail is an ARITHMETIC input only (see the module docstring): its ids say
    which numbers are already spoken for in the file the merge is about to
    write. They are never treated as landed and never cross series.

    Returns a dict; `ok` False means REFUSE with `code`:
      * `EXIT_REFUSED_TAIL_ID` -- the tail already holds this id or a higher one
        in the same series. This is checked FIRST, because it is the actionable
        diagnosis: the caller must re-derive, and the numbers it needs are the
        tail's own ids and the combined next id.
      * `EXIT_REFUSED_ID` -- the first id is not max + 1 over the two sides.
    """
    series, first_n, _ = split_id(new_ids[0])
    head_max = max_for_series(head_ids, series)
    tail_max = max_for_series(tail_ids, series)
    tail_in_series = [i for i in tail_ids if split_id(i)[0] == series]
    known = [n for n in (head_max, tail_max) if n is not None]
    effective = max(known) if known else None
    out = {
        "ok": True, "code": EXIT_OK, "reason": "",
        "series": series, "first_n": first_n,
        "head_max": head_max, "tail_max": tail_max, "effective_max": effective,
        "tail_in_series": tail_in_series,
        "next_id": f"{series}{(effective if effective is not None else 0) + 1}",
    }
    if tail_max is not None and tail_max >= first_n:
        out.update(ok=False, code=EXIT_REFUSED_TAIL_ID, reason=(
            f"the PRESERVED WORKTREE TAIL already holds {series}-series id(s) "
            f"{tail_in_series} -- at or above the first appended id "
            f"{new_ids[0]!r}. The merge lands HEAD's blob, that tail AND your "
            f"rows, so appending here would write two rows with the same id "
            f"(closure 52e5de39, the D369 family's third bite). The correct "
            f"next id over HEAD (max {head_max}) and the tail (max {tail_max}) "
            f"together is {out['next_id']}. Re-derive and retry -- the tail is "
            f"neither renumbered nor dropped, because renumbering another "
            f"agent's row is that agent's call (ASK, never renumber)."))
        return out
    if effective is None or first_n != effective + 1:
        out.update(ok=False, code=EXIT_REFUSED_ID, reason=(
            f"first appended id {new_ids[0]!r} is not max+1 ({out['next_id']}) "
            f"for its series over HEAD (max {head_max}) and the preserved "
            f"worktree tail (max {tail_max})"))
    return out


def read_committed(repo: Path, rev: str, path: str) -> tuple[str | None, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        capture_output=True, text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        reason = detail[-1] if detail else f"git exited {completed.returncode}"
        return None, f"could not read {rev}:{path} -- {reason}"
    return completed.stdout, ""


def utf8_len(text: str) -> int:
    """The size of `text` IN BYTES, which is the only size a reader can check.

    WHY THIS EXISTS. Every size this module reported was `len(str)` -- a COUNT
    OF CHARACTERS -- printed under the label `bytes`. On Python 3 a `str` is a
    sequence of code points, so `read_text()` and `git show` (run with
    `text=True`) both hand this module DECODED text, and its length is the
    character count. For ASCII the two agree and the label is harmless; for the
    real records they do not. MEASURED 2026-09-04 on `docs/COST_CALIBRATION.md`,
    both sides, in one invocation:

        HEAD's blob : 1468456 bytes, 1456715 characters, delta 11741
        worktree    : 1458319 bytes, 1446578 characters, delta 11741

    So the report understated the record by ~11.7k units while naming the unit
    `bytes`. That is not cosmetic here, and the reason is this module's PURPOSE:
    the numbers exist so a caller can see a stale HEAD or a short write. Every
    instrument they would cross-check against speaks BYTES -- `git cat-file -s`,
    `wc -c`, `ls -l`, and `cmp`, whose "EOF on - after byte 313171" is the very
    message D369 is named for. A character count is comparable to NONE of them,
    so a healthy run looked like a 11,741-unit size mismatch: exactly the
    STALE-HEAD symptom, and it has already cost one lane a full investigation
    round chasing a phantom.

    THE REPAIR DIRECTION WAS A CHOICE BETWEEN TWO, and it went this way rather
    than relabelling the output `chars` because the label was never the load-
    bearing half -- the CROSS-CHECK is. Relabelling would make the report
    truthful and still leave it uncomparable to git and to the filesystem, which
    is what the number is for.

    THE MERGE ITSELF IS UNTOUCHED AND WAS NEVER WRONG. The prefix test, the tail
    slice and the write all operate on `str`, and for valid UTF-8 a character
    prefix is a byte prefix and back -- UTF-8 is self-synchronising, so no code
    point boundary can fall inside another. This function changes what is
    REPORTED, never what is decided or written.
    """
    return len(text.encode("utf-8"))


def merge(head_text: str, worktree_text: str, rows_text: str, *,
          preserve_worktree_tail: bool = False) -> dict:
    """Build the file content to write. Pure, so the controls drive it on fixtures.

    The prefix test is UNCONDITIONAL: if the worktree diverges from `head_text`
    INSIDE the committed blob's own bytes, this REFUSES (`ok` False, `merged`
    None), because that is an edit to committed content, not an append.

    On success the output depends on ONE keyword:
      * preserve_worktree_tail=False (DEFAULT, and the only path main() takes):
        the base is HEAD's committed blob and the worktree tail is DISCARDED --
        `merged` = head_text + rows_text. An aborted append leaves nothing a peer
        can sweep (2026-09-07; see the module amendment at the head of the file).
      * preserve_worktree_tail=True: the pre-2026-09-07 behaviour, folding the
        worktree tail in ahead of the rows. RETAINED ONLY so run_controls can
        drive the old sweep as the RED reference for the discard limb.

    `tail` in the returned dict is always the actual worktree bytes beyond HEAD,
    for REPORTING what was discarded; it is not folded into `merged` unless the
    keyword asks for it.
    """
    if not worktree_text.startswith(head_text):
        # Locate the first differing CHARACTER -- `at` indexes `str`, so it is a
        # character index, NOT a byte offset. It is converted to bytes at the
        # point of REPORT (`utf8_len(head_text[:at])`), because the reader takes
        # this offset straight to `cmp`, whose "EOF on - after byte 313171" is
        # the message D369 is named for, and to `git cat-file -s`. Both speak
        # BYTES. Do not "tidy" the conversion away: on a record carrying `§`,
        # `—` or `⚠` the two offsets differ, and a character offset sends the
        # reader to the wrong place in the file at the exact moment they are
        # diagnosing a real truncation. A planted control drives this refusal on
        # a specimen whose divergence sits AFTER multi-byte content and requires
        # the two offsets to differ before it grades either.
        limit = min(len(head_text), len(worktree_text))
        at = next((i for i in range(limit)
                   if head_text[i] != worktree_text[i]), limit)
        return {
            "ok": False,
            "reason": (
                "the worktree disagrees with the committed blob inside the "
                f"committed blob's own bytes, first at byte "
                f"{utf8_len(head_text[:at])} of "
                f"{utf8_len(head_text)}"
                # SITE 6, and the subtlest of the family: this ternary decides
                # whether to say TRUNCATION, and it compared CHARACTER lengths.
                # A worktree can be character-SHORTER and byte-LONGER at the
                # same time -- replace 10 ASCII characters with 4 of `§ — ⚠ ⚡`
                # and it loses 6 characters while gaining 1 byte. Under the
                # character comparison this module then told the reader the file
                # had been TRUNCATED while it had actually GROWN on disk, which
                # is worse than saying nothing: `ls -l` and `git cat-file -s`
                # would contradict it, and the reader would disbelieve the
                # refusal rather than the sentence. It selects WORDING only --
                # `ok` is already False above -- so nothing about what refuses,
                # when, or with which exit code depends on this line. A planted
                # control builds exactly that specimen and requires the clause to
                # be ABSENT, with a genuinely byte-shorter worktree as the
                # paired positive that requires it to still be PRESENT.
                + ("; the worktree is SHORTER than the blob, which is a "
                   "truncation, not an append"
                   if utf8_len(worktree_text) < utf8_len(head_text) else "")),
            "merged": None, "tail": None, "separator_inserted": False,
        }
    tail = worktree_text[len(head_text):]
    if preserve_worktree_tail:
        # THE PRE-2026-09-07 BEHAVIOUR, RETAINED ONLY AS A TEST REFERENCE. It
        # folds the worktree tail into the output ahead of the rows. main() never
        # takes this path; it exists so run_controls can drive the OLD sweep and
        # prove the production path below actually differs from it (RED-then-GREEN).
        separator = bool(tail) and not tail.endswith("\n")
        merged = head_text + tail + ("\n" if separator else "") + rows_text
    else:
        # PRODUCTION, 2026-09-07: the base is HEAD's committed blob and the
        # worktree tail is DISCARDED, never folded in. `merged` is HEAD's blob
        # plus this invocation's own rows and NOTHING else, so an ABORTED append
        # -- which leaves its row in the SHARED worktree -- leaves nothing the
        # next team's append can sweep into its commit (the VMFL046-R5 sweep into
        # 9bf38155, 2026-09-07, and one before it). Multi-row batching is
        # unaffected: every row in a single --rows file is inside rows_text and
        # all still land. The separator guards the (committed records do not hit
        # it) case of a blob not ending in a newline.
        separator = bool(head_text) and not head_text.endswith("\n")
        merged = head_text + ("\n" if separator else "") + rows_text
    return {"ok": True, "reason": "", "merged": merged, "tail": tail,
            "separator_inserted": separator}


def _clean_git_env() -> dict:
    """A git environment with EVERY `GIT_*` variable stripped.

    NOT hygiene -- a correctness requirement, and a near miss worth naming. The
    private-index protocol (CLAUDE.md rule 10) exports `GIT_INDEX_FILE`, and
    this module's controls are run by exactly the agents who have it set. A
    `git -C <tempdir> add` inheriting that variable would write into the
    CALLER'S PRIVATE INDEX from inside a selftest -- a selftest with a side
    effect on the shared repository's staging state. `GIT_DIR` and
    `GIT_WORK_TREE` would be worse still: the seed commit would land in the real
    repository. So the whole namespace goes, rather than the three names this
    lane happened to think of.
    """
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def run_allocation_disk_control() -> tuple[dict, dict, list[str]]:
    """TOOL-ALLOCATED IDS, driven through the REAL production path on disk.

    VERIFICATION_CHARTER section 2j, asked the way section 2j asks it: WHO WROTE
    THE BYTES THIS CONTROL READS? Not this function, and not a fixture it
    shaped. Every assertion below reads `docs/COST_CALIBRATION.md` back off the
    filesystem AFTER `main()` -- the same `main()` the lab invokes, with the
    same argument vector, ending in the same `wt_file.write_text(got["merged"])`
    -- has written it. This function only supplies a throwaway repository and a
    rows file; the record's bytes are the producer's.

    The negative limbs read bytes written by that same producer ON THE PREVIOUS
    RUN and require them UNCHANGED, which is the planted-zero discipline in its
    proper shape: limb group A shows the writer CAN write to this file, so limb
    group B's "nothing changed" is a measurement rather than a reader that was
    never able to see anything.

    Returns `(planted, negative, notes)`.
    """
    planted, negative, notes = {}, {}, []
    path = "docs/COST_CALIBRATION.md"
    env = _clean_git_env()

    def git(repo: Path, *args: str) -> None:
        # A list argument and the returncode read from the completed process --
        # never a status through a pipe (this module's standing rule).
        done = subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, env=env)
        if done.returncode != 0:  # pragma: no cover - a broken box, not a defect
            raise RuntimeError(f"git {args[0]} failed in the control repo: "
                               f"{done.stderr.strip()[:200]}")

    def run_main(repo: Path, rows: Path, *extra: str) -> int:
        """`main()` itself, output captured so the selftest stays readable."""
        buf_o, buf_e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
            return main(["--path", path, "--rows", str(rows),
                         "--repo", str(repo), *extra])

    with tempfile.TemporaryDirectory(prefix="append_record_alloc_") as td:
        repo = Path(td) / "repo"
        (repo / "docs").mkdir(parents=True)
        record = repo / path
        record.write_text(
            "| id | date | team | process |\n|---|---|---|---|\n"
            "| C-1 | 2026-08-31 | verification | a seeded LEGACY row, which "
            "keeps its identity forever |\n")
        # `git init` in a THROWAWAY tree with a scrubbed environment, and every
        # `add` naming an explicit path. CLAUDE.md rule 10's prohibitions are
        # about the SHARED index and the shared working tree; neither exists
        # here, and `_clean_git_env` is what guarantees that.
        subprocess.run(["git", "init", "-q", str(repo)],
                       capture_output=True, text=True, env=env, check=True)
        git(repo, "config", "user.email", "control@certonomous.invalid")
        git(repo, "config", "user.name", "append_record control")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "seed the control record")

        rows_ok = Path(td) / "rows_ok.md"
        rows_ok.write_text(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-08-31 | verification | a row "
            f"whose id the TOOL allocates |\n")

        # ---- limb group A: the producer writes, and we read what it wrote ----
        before = record.read_text()
        rc1 = run_main(repo, rows_ok, "--allocate-id")
        after1 = record.read_text()          # <- bytes written by main()
        ids1 = re.findall(tool_id_pattern(path), after1)
        planted["a run with --allocate-id returns OK"] = (rc1 == EXIT_OK)
        planted["the record ON DISK gained exactly one tool-allocated id"] = (
            len(ids1) == 1)
        planted["the placeholder is GONE from the bytes on disk"] = (
            ALLOCATE_PLACEHOLDER not in after1 and ALLOCATE_PLACEHOLDER in
            rows_ok.read_text())
        planted["the file actually changed (the writer can write)"] = (
            after1 != before)

        # 2026-09-07: each real append is COMMITTED before the next builds on it
        # (the private-index workflow), so run 1's row must land in HEAD before
        # run 2 -- the production base is HEAD's committed blob, not the worktree.
        # An uncommitted run 1 would be DISCARDED by run 2, which is the whole
        # point of the repair and is proved by the sweep-discard limb elsewhere.
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "land run 1's allocated row")

        # A SECOND run, same rows file, same placeholder. This is the collision
        # limb AND the exit-7 limb at once: run 1's tool-id row is now in HEAD's
        # committed blob, where `shape_audit` will meet it. If the tool-id clause
        # in `shape_audit` were missing, this run would refuse at exit 7 -- the
        # tool refusing the row it had just allocated.
        rc2 = run_main(repo, rows_ok, "--allocate-id")
        after2 = record.read_text()          # <- bytes written by main(), again
        ids2 = re.findall(tool_id_pattern(path), after2)
        planted["a second run over its own previous output returns OK"] = (
            rc2 == EXIT_OK)
        planted["two runs of the SAME rows minted two DISTINCT ids"] = (
            len(ids2) == 2 and len(set(ids2)) == 2)
        planted["the ids on disk sort chronologically as plain strings"] = (
            sorted(ids2) == ids2)
        # The legacy arithmetic must be untouched by any of it.
        planted["the LEGACY pattern parses no tool id out of the real bytes"] = (
            parse_ids(after2, RECORDS[path]) == ["C-1"])
        notes.append(f"    allocation control: ids read back off disk {ids2}, "
                     f"minted by main() itself in two separate runs")

        # ---- MUTATION of the shape_audit clause, on the REAL bytes ----------
        # Removing the tool-id clause must turn those same on-disk lines into
        # exit-7 offenders. Driven, not asserted in prose.
        planted["removing shape_audit's tool-id clause refuses those very "
                "bytes"] = (
            len(shape_audit(after2, path, "disk", apply_tool_ids=False)) == 2
            and shape_audit(after2, path, "disk") == [])

        # ---- limb group B: the negatives, read from the same producer -------
        rows_hand = Path(td) / "rows_hand.md"
        rows_hand.write_text(
            f"| {ids2[0]} | 2026-08-31 | verification | a HAND-WRITTEN id, "
            f"copied from a row that already exists |\n")
        rc3 = run_main(repo, rows_hand)
        after3 = record.read_text()
        negative["a hand-written tool id is accepted"] = (rc3 == EXIT_OK)
        planted["a hand-written tool id refuses with the allocation code"] = (
            rc3 == EXIT_REFUSED_ALLOCATION)
        planted["and the record on disk is BYTE-IDENTICAL after that refusal"] \
            = (after3 == after2)

        rows_ph = Path(td) / "rows_placeholder.md"
        rows_ph.write_text(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-08-31 | verification | a "
            f"placeholder with no --allocate-id |\n")
        rc4 = run_main(repo, rows_ph)
        after4 = record.read_text()
        negative["a placeholder without --allocate-id is written literally"] = (
            rc4 == EXIT_OK or ALLOCATE_PLACEHOLDER in after4)
        planted["a placeholder without --allocate-id refuses"] = (
            rc4 == EXIT_REFUSED_ALLOCATION)
        planted["and the record on disk is BYTE-IDENTICAL after that refusal "
                "too"] = (after4 == after2)

        rc5 = run_main(repo, rows_ok, "--allocate-id",
                       "--expect-first-id", "C-2")
        planted["--allocate-id with --expect-first-id refuses"] = (
            rc5 == EXIT_REFUSED_ALLOCATION and record.read_text() == after2)

        # ---- MUTATION of the smuggle guard: the limb must flip --------------
        smuggled_rows = rows_hand.read_text()
        planted["dropping the smuggle guard lets that hand-written id "
                "through"] = (
            check_allocation(smuggled_rows, path, allocate=False,
                             apply_smuggle_guard=False)["ok"]
            and not check_allocation(smuggled_rows, path,
                                     allocate=False)["ok"])

        # ---- the non-presence backstop, DRIVEN into its refusal -------------
        # `allocate_id` is given a frozen clock AND fixed entropy, which is the
        # only way to force the residue case. It must be caught.
        frozen = datetime(2026, 8, 31, 15, 47, 7, tzinfo=timezone.utc)
        twin_a = allocate_id(path, b"row", now=frozen, entropy=b"\x00" * 16)
        twin_b = allocate_id(path, b"row", now=frozen, entropy=b"\x00" * 16)
        planted["the per-process sequence alone separates two otherwise "
                "identical mints"] = (twin_a != twin_b)
        forced = check_allocated_unique([twin_a], f"| {twin_a} | already here |")
        planted["a minted id already present in the record is REFUSED"] = (
            not forced["ok"] and forced["code"] == EXIT_REFUSED_ALLOCATION)
        planted["a genuinely new minted id is not refused"] = (
            check_allocated_unique([twin_a], "| C-1 | nothing else |")["ok"])

    # ---- every legacy pattern must be STRUCTURALLY blind to the new form ----
    # Checked, not assumed: this is what keeps a tool-allocated id out of the
    # `max+1` arithmetic and out of every record's historical series.
    for rec_path in sorted(RECORDS):
        specimen = allocate_id(rec_path, b"specimen")
        line = {"docs/LESSONS.md": f"## {specimen} — a heading\n",
                "docs/NUMERICS_KNOWLEDGE.md": f"**{specimen}. an entry**\n",
                }.get(rec_path, f"| {specimen} | 2026-08-31 | a | row |\n")
        # THE SAME ENTRY, citing its own id in its own prose -- the documented
        # `allocate_into_rows` behaviour (one id per LINE, every occurrence on
        # that line filled), spelled in each record's own vocabulary.
        selfcite = {
            "docs/LESSONS.md": f"## {specimen} — a heading citing {specimen}\n",
            "docs/NUMERICS_KNOWLEDGE.md":
                f"**{specimen}. an entry citing {specimen}**\n",
        }.get(rec_path,
              f"| {specimen} | 2026-08-31 | a | row citing {specimen} |\n")
        tag = rec_path.rsplit("/", 1)[-1]
        planted[f"{tag}: the LEGACY pattern parses no id from a tool id"] = (
            parse_ids(line, RECORDS[rec_path]) == [])
        planted[f"{tag}: the record's own tool pattern DOES see it"] = (
            re.findall(tool_id_pattern(rec_path), line) == [specimen])
        planted[f"{tag}: a tool-id line is not a shape-audit offender"] = (
            shape_audit(line, rec_path, "fixture") == [])

        # ---- THE READER THE RECONCILERS USE -----------------------------
        # Every limb below is about `parse_record_ids`, which is the half of
        # Sanaa's directive that makes the write side legible to the guards.
        # A writer whose reader cannot see it is a dead lever.
        planted[f"{tag}: the COMBINED reader sees the tool id as an entry"] = (
            parse_record_ids(line, rec_path) == [specimen])
        # A LEGACY entry must still parse, and must parse to the SAME LIST the
        # legacy reader alone returned -- the past is not renumbered and is not
        # re-read.
        legacy_line = {
            "docs/LESSONS.md": "## L-9401. a legacy heading\n",
            "docs/NUMERICS_KNOWLEDGE.md": "**N-B9401. a legacy entry**\n",
        }.get(rec_path, "| %s9401 | 2026-08-31 | a | row |\n"
              % ("C-" if rec_path.endswith("COST_CALIBRATION.md") else "D"))
        planted[f"{tag}: the combined reader returns the legacy list "
                f"UNCHANGED"] = (
            parse_record_ids(legacy_line, rec_path)
            == parse_ids(legacy_line, RECORDS[rec_path]) != [])
        # BOTH FORMS TOGETHER, in document order, which is the mixed record
        # every one of these files becomes on the first allocated append.
        mixed = legacy_line + line
        planted[f"{tag}: a MIXED record yields both ids in document order"] = (
            parse_record_ids(mixed, rec_path)
            == parse_ids(legacy_line, RECORDS[rec_path]) + [specimen])
        # THE SELF-CITING ROW. `allocate_into_rows` fills every placeholder on
        # a line, so a row may legitimately carry its own id twice. Counted with
        # the UNANCHORED pattern that is a duplicate and the reconciler returns
        # rc 4 on a correct row. Anchoring is what stops it, and the mutation
        # below drives the unanchored reader to prove the limb is load-bearing.
        n_anchored = len(parse_record_ids(selfcite, rec_path))
        n_unanchored = len(re.findall(tool_id_pattern(rec_path), selfcite))
        planted[f"{tag}: a row citing its OWN id is ONE entry, not a "
                f"duplicate"] = (n_anchored == 1)
        planted[f"{tag}: the UNANCHORED pattern would read that row as two -- "
                f"so the anchor is load-bearing"] = (n_unanchored == 2)
        # NEGATIVE: a tool id MENTIONED IN PROSE is not an entry. Scored as a
        # negative so a reader loosened to `find it anywhere` is caught here
        # rather than by a false duplicate weeks later.
        negative[f"{tag}: a tool id mentioned mid-sentence in prose is counted "
                 f"as an entry"] = bool(
            parse_record_ids(f"a mid-sentence mention of {specimen} in prose\n",
                             rec_path))
    notes.append(
        f"    tool-id/legacy separation proved on all {len(RECORDS)} records: "
        f"each legacy pattern parses ZERO ids from its own record's tool-id "
        f"form, so no allocated id can enter a historical series' arithmetic; "
        f"and the COMBINED reader parse_record_ids sees both forms, in document "
        f"order, counting a self-citing row ONCE")
    return planted, negative, notes


# ------------------------------ THE `corrects:` FIELD, DRIVEN NOT ASSERTED
#: The cited id used by every fixture below, rendered in each record's own
#: prefix. A FIXED LITERAL rather than a minted one, deliberately: a citation IS
#: a hand-written tool-form id -- that is the entire subject of Sanaa's
#: 2026-09-03 amendment -- so minting it here would exercise the minter instead
#: of the guard, and the guard is what is on trial.
_CITED_STAMP = "20260902T215932.385336Z-ef920ed2"

#: One CORRECTION-declaration entry opener per record, in that record's OWN
#: vocabulary, and one ORDINARY opener beside it. Never borrowed across records
#: (CLAUDE.md rule 14; this module's standing rule), because `CORRECTION_MARKER`
#: itself is spelled per record and a fixture that borrowed another record's
#: shape would grade the wrong grammar. The `docs/LESSONS.md` and
#: `docs/NUMERICS_KNOWLEDGE.md` markers are UNEXERCISED BY THE LIVE CORPUS
#: (measured 2026-09-03: `CORRECTION ROW` occurs 0 times in either), so these
#: fixtures are the ONLY thing that drives them -- which is exactly what the
#: comment above `CORRECTION_MARKER` promises and what, until this control
#: existed, nothing delivered.
_CORR_ENTRY = {
    "docs/DOCKET.md": "**CORRECTION ROW** -- it restates the row it names",
    "docs/COST_CALIBRATION.md": "**CORRECTION ROW** -- append rule 1, a new "
                                "row naming the row it corrects",
    "docs/LESSONS.md": "CORRECTION -- it restates the lesson it names",
    "docs/NUMERICS_KNOWLEDGE.md": "CORRECTION -- it restates the fact it names",
}
_ORD_ENTRY = {
    "docs/DOCKET.md": "an ordinary docket row, declaring nothing",
    "docs/COST_CALIBRATION.md": "an ordinary cost row, declaring nothing",
    "docs/LESSONS.md": "AN ORDINARY LESSON, declaring nothing",
    "docs/NUMERICS_KNOWLEDGE.md": "AN ORDINARY FACT, declaring nothing",
}
#: A LEGACY id per record -- the second accept form, which proves the acceptance
#: is a property of the FIELD and not a side effect of `--allocate-id`.
_LEGACY_OWN = {
    "docs/DOCKET.md": "D9001",
    "docs/COST_CALIBRATION.md": "C-9001",
    "docs/LESSONS.md": "L-9001",
    "docs/NUMERICS_KNOWLEDGE.md": "N-B9001",
}
#: An id cell / heading token this record's pattern CANNOT parse and which is
#: not the placeholder either -- the C3 case. One token, never `a note` for the
#: heading records, because the marker's `\S+` cannot span a space.
_NO_OWN_ID = {
    "docs/DOCKET.md": "a note",
    "docs/COST_CALIBRATION.md": "a note",
    "docs/LESSONS.md": "no-id",
    "docs/NUMERICS_KNOWLEDGE.md": "no-id",
}
for _tbl_name, _tbl in (("_CORR_ENTRY", _CORR_ENTRY), ("_ORD_ENTRY", _ORD_ENTRY),
                        ("_LEGACY_OWN", _LEGACY_OWN), ("_NO_OWN_ID", _NO_OWN_ID)):
    if set(_tbl) != set(RECORDS):  # pragma: no cover - a load-time refusal
        raise SystemExit(
            f"REFUSED: {_tbl_name} and RECORDS disagree. Every registered record "
            f"gets its `corrects:` fixtures in ITS OWN vocabulary; a record with "
            f"no fixture would have Sanaa's 2026-09-03 amendment proved on some "
            f"OTHER record's grammar, which is the borrowed-shape defect "
            f"(CLAUDE.md rule 14).")
del _tbl_name, _tbl


def _corrects_row(path: str, id_cell: str, entry: str) -> str:
    """One row/heading in *path*'s OWN live entry grammar. Fixtures only."""
    if path in ("docs/DOCKET.md", "docs/COST_CALIBRATION.md"):
        return f"| {id_cell} | 2026-09-03 | verification | {entry} |\n"
    if path == "docs/LESSONS.md":
        return f"## {id_cell}. {entry}\n"
    return f"**{id_cell}. {entry}**\n"


def _corrects_specimens() -> list[dict]:
    """The whole corpus, ONE definition, shared by every limb below.

    Shared on purpose: the acceptance arms, the refusal arms and the regression
    arm must be judging the SAME bytes, or "refusal unchanged everywhere else"
    would be a claim about two different corpora. Each specimen carries the
    verdict it is REGISTERED to produce, so a fixture that silently changed
    class would fail its own arm rather than quietly widen the pass.
    """
    ph = ALLOCATE_PLACEHOLDER
    out: list[dict] = []
    for path in sorted(RECORDS):
        cid = f"{TOOL_ID_PREFIX[path]}-{_CITED_STAMP}"
        corr, ordy = _CORR_ENTRY[path], _ORD_ENTRY[path]
        tag = path.rsplit("/", 1)[-1]
        # HOW THE ROW CARRIES ITS OWN ID, per record, ADDED 2026-09-03 with the
        # allocation-scope ruling. Sanaa's `corrects:` amendment is about the
        # CITATION FIELD, which is orthogonal to how the row's OWN id is
        # obtained -- but every specimen below used to obtain it by ALLOCATION,
        # and allocation is now refused on some records. Grading those rows
        # under the old expectation would have measured the scope refusal and
        # called it a `corrects:` verdict.
        #
        # SO, AND THIS IS THE JUDGEMENT CALL IN THIS EDIT: on a record where
        # allocation is refused, the specimens carry a LEGACY own-id instead --
        # which is the path that record actually has (`--expect-first-id` with
        # an integer). COVERAGE IS PRESERVED, NOT REDUCED: every clause C1, C2,
        # C3 and the smuggle scan is still exercised on ALL FOUR records, in
        # each record's own vocabulary; only the way the row gets its own id
        # changes, and that is the variable the amendment does not speak to.
        # The scope refusal itself is asserted by its own specimen below rather
        # than left implicit.
        refused_here = path in ALLOCATION_REFUSED
        own = _LEGACY_OWN[path] if refused_here else ph
        alloc = not refused_here
        if refused_here:
            spec_scope = {
                "name": f"{tag}: --allocate-id is REFUSED here even on a "
                        f"well-formed correction row (allocation scope)",
                "path": path, "allocate": True, "accepted": False,
                "clause": "allocation-scope", "core": False,
                "rows": _corrects_row(path, ph, f"{corr} corrects:[{cid}]"),
                "cited": cid}
            out.append(spec_scope)

        def spec(name, rows, allocate, accepted, clause):
            # `cited` is DERIVED from the bytes, never declared: two specimens
            # below (a legacy id in the body, an empty body) deliberately carry
            # NO tool-form id at all, and a control that declared one would
            # then plant a zero it could not see.
            # `core` marks a specimen produced by THIS SHARED LOOP, i.e. one
            # every record gets. It is what makes the coverage claim
            # MEASURABLE instead of a comment: the record-specific extras
            # appended after the loop are `core: False`, so a set comparison
            # over the core specimens compares like with like. See
            # `run_allocation_scope_control`'s clause-parity limbs.
            out.append({"name": f"{tag}: {name}", "path": path, "rows": rows,
                        "allocate": allocate, "accepted": accepted,
                        "clause": clause, "core": True,
                        "cited": cid if cid in rows else ""})

        spec("a correction row with a well-formed corrects: field is ACCEPTED",
             _corrects_row(path, own, f"{corr} corrects:[{cid}]"),
             alloc, True, "ACCEPT")
        spec("a correction row carrying its own LEGACY id is ACCEPTED too",
             _corrects_row(path, _LEGACY_OWN[path],
                           f"{corr} corrects:[{cid}]"),
             False, True, "ACCEPT")
        spec("the SAME id outside any field still REFUSES (unchanged)",
             _corrects_row(path, own, f"{corr} it corrects {cid} in prose"),
             alloc, False, "smuggle")
        spec("a corrects: field on a NON-correction row REFUSES (C1/C2)",
             _corrects_row(path, own, f"{ordy} corrects:[{cid}]"),
             alloc, False, "C2")
        spec("a LEGACY id inside the field is MALFORMED, not prose (C1)",
             _corrects_row(path, own,
                           f"{corr} corrects:[{_LEGACY_OWN[path]}]"),
             alloc, False, "C1")
        spec("an UNTERMINATED field REFUSES rather than reading as prose (C1)",
             _corrects_row(path, own, f"{corr} corrects:[{cid} and on it goes"),
             alloc, False, "C1")
        spec("whitespace inside the body is MALFORMED (C1)",
             _corrects_row(path, own, f"{corr} corrects:[ {cid}]"),
             alloc, False, "C1")
        spec("an EMPTY body is MALFORMED (C1)",
             _corrects_row(path, own, f"{corr} corrects:[]"),
             alloc, False, "C1")
        spec("a correction row with NO id of its own REFUSES (C3)",
             _corrects_row(path, _NO_OWN_ID[path], f"{corr} corrects:[{cid}]"),
             False, False, "C3")
    # THE MOTIVATING CASE ITSELF, and it is cross-record: `docs/DOCKET.md` row
    # `D-20260902T224505.958199Z-e02eb14e` was refused for citing the `C-` ids
    # of the calibration rows it described. Two ids, `;`-separated, neither of
    # this record's prefix.
    dk = "docs/DOCKET.md"
    out.append({
        "name": "DOCKET.md: the MOTIVATING case -- two CROSS-RECORD C- ids in "
                "one field on a docket correction row",
        "path": dk, "allocate": True, "accepted": True, "clause": "ACCEPT",
        "core": False,
        "cited": f"C-{_CITED_STAMP}",
        "rows": _corrects_row(
            dk, ALLOCATE_PLACEHOLDER,
            f"{_CORR_ENTRY[dk]} corrects:[C-{_CITED_STAMP};"
            f"C-20260902T215932.385337Z-ef920ed3]")})
    # NO `corrects:` OPENER ANYWHERE. These are the specimens the amendment must
    # not touch AT ALL -- same verdict, same code, same MESSAGE BYTES.
    out.append({
        "name": "COST_CALIBRATION.md: a plain hand-written id, no field in "
                "sight, still REFUSES",
        "path": "docs/COST_CALIBRATION.md", "allocate": False,
        "accepted": False, "clause": "smuggle-untouched", "core": False,
        "cited": f"C-{_CITED_STAMP}",
        "rows": f"| C-{_CITED_STAMP} | 2026-09-03 | verification | a "
                f"hand-written id in the id cell |\n"})
    out.append({
        "name": "COST_CALIBRATION.md: a placeholder with no --allocate-id "
                "still REFUSES",
        "path": "docs/COST_CALIBRATION.md", "allocate": False,
        "accepted": False, "clause": "placeholder-untouched",
        "core": False, "cited": "",
        "rows": f"| {ALLOCATE_PLACEHOLDER} | 2026-09-03 | verification | no "
                f"allocation flag |\n"})
    # EVERY specimen declares `core` explicitly. A specimen that merely OMITTED
    # the key would read as non-core and vanish from the clause-parity limbs --
    # silently shrinking the very assertion that justifies editing a Sanaa
    # directive's arms. So the omission is a load-time refusal, not a default.
    _no_core = [s["name"] for s in out if "core" not in s]
    if _no_core:  # pragma: no cover - a load-time refusal
        raise SystemExit(
            f"REFUSED: these corrects: specimens declare no `core` flag, so "
            f"they would be invisible to the clause-parity limbs: {_no_core}")
    return out


#: CLAUDE.md rule 11's derivation, VERBATIM. Copied as a string rather than
#: paraphrased, because the whole finding is that its exact shape -- a prefix
#: match with no trailing anchor -- is what misreads a minted id. A paraphrase
#: that "tidied" it would test a reader the constitution does not prescribe.
RULE_11_DERIVATION = (
    "grep -oE '^## L-[0-9]+' {f} | grep -oE '[0-9]+' | sort -n | tail -1")


def run_allocation_scope_control() -> tuple[dict, dict, list[str]]:
    """THE 2026-09-03 ALLOCATION SCOPE RULING, DRIVEN THROUGH `main()` ON DISK.

    Four arms, and the fourth is the one that makes the guard load-bearing
    rather than decorative:

      A POSITIVE -- the records where allocation is ALLOWED still mint and still
        round-trip. A refusal that refuses everything is indistinguishable from
        a correct one by its verdicts alone, so this arm is what separates
        RESTRICTED from DISABLED.
      B THE REFUSAL -- `docs/LESSONS.md` refuses through the PRODUCTION path,
        real argv, and returns `EXIT_REFUSED_ALLOCATION`.
      C NEAR-MISS -- one byte outside the refusal, which must still be allowed:
        the SAME record without `--allocate-id`, and the CLOSEST NEIGHBOUR
        record (NUMERICS, also zero tool ids in production, also an unusual
        minted form) WITH it. The refusal keys on `(path, allocate)` and both
        near-misses move exactly one of those two.
      D THE RULE-11 REGRESSION -- build the file that would exist if the guard
        were absent, run rule 11's own derivation VERBATIM over it, and require
        the misread; then run the same rows through `main()` WITH the guard and
        require that file cannot be produced. Without arm D the refusal is a
        rule nobody has shown to prevent anything.

    Returns `(planted, negative, notes)`.
    """
    planted, negative, notes = {}, {}, []
    env = _clean_git_env()
    L = "docs/LESSONS.md"

    def git(repo: Path, *args: str) -> None:
        done = subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, env=env)
        if done.returncode != 0:  # pragma: no cover - a broken box
            raise RuntimeError(f"git {args[0]} failed in the scope control repo: "
                               f"{done.stderr.strip()[:200]}")

    def run_main(repo: Path, path: str, rows: Path, *extra: str) -> int:
        buf_o, buf_e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
            return main(["--path", path, "--rows", str(rows),
                         "--repo", str(repo), *extra])

    # Each record is seeded in ITS OWN vocabulary -- never borrowed, which is
    # `check_record_reconciliation`'s 2026-08-24 defect (CLAUDE.md rule 14).
    seed = {
        L: "# Lessons\n\n## L-1. a seeded legacy lesson.\n",
        "docs/NUMERICS_KNOWLEDGE.md": "# Numerics\n\n**N-B1. a seeded fact**\n",
        "docs/DOCKET.md": "| id | date | team | item |\n|---|---|---|---|\n"
                          "| D1 | 2026-09-03 | verification | a seeded row |\n",
        "docs/COST_CALIBRATION.md": "| id | date | team | process |\n"
                                    "|---|---|---|---|\n"
                                    "| C-1 | 2026-09-03 | verification | a row |\n",
    }
    row_form = {
        L: "## {id} — a lesson whose id the tool allocates\n",
        "docs/NUMERICS_KNOWLEDGE.md": "**{id}. a fact whose id the tool "
                                      "allocates**\n",
        "docs/DOCKET.md": "| {id} | 2026-09-03 | verification | a row |\n",
        "docs/COST_CALIBRATION.md": "| {id} | 2026-09-03 | verification | a "
                                    "row |\n",
    }

    with tempfile.TemporaryDirectory(prefix="append_record_scope_") as td:
        root = Path(td)

        # A per-call counter, because two ARMS legitimately seed the SAME record
        # (NUMERICS is both a permitted-allocation record in arm A and the
        # near-miss neighbour in arm C) and a name derived from the path alone
        # collided. Each arm must get a repo no other arm has written to, or one
        # arm's tail becomes another arm's input.
        _repo_seq = itertools.count(1)

        def fresh(path: str) -> Path:
            """A throwaway repo seeded with ONE record. No shared index exists
            here, which is what makes `git add -- <path>` legitimate: CLAUDE.md
            rule 10's prohibitions are about the SHARED tree."""
            repo = (root / f"{next(_repo_seq)}_"
                    f"{path.replace('/', '_').replace('.', '_')}")
            (repo / "docs").mkdir(parents=True)
            (repo / path).write_text(seed[path])
            subprocess.run(["git", "init", "-q", str(repo)], capture_output=True,
                           text=True, env=env, check=True)
            git(repo, "config", "user.email", "control@certonomous.invalid")
            git(repo, "config", "user.name", "append_record scope control")
            git(repo, "config", "commit.gpgsign", "false")
            git(repo, "add", "--", path)
            git(repo, "commit", "-q", "-m", "seed")
            return repo

        # ---- ARM A: allocation still WORKS where it is allowed -------------
        allowed = [p for p in sorted(RECORDS) if p not in ALLOCATION_REFUSED]
        for path in allowed:
            repo = fresh(path)
            rows = root / f"rows_{TOOL_ID_PREFIX[path]}.md"
            rows.write_text(row_form[path].format(id=ALLOCATE_PLACEHOLDER))
            rc = run_main(repo, path, rows, "--allocate-id")
            on_disk = (repo / path).read_text()      # bytes written by main()
            minted = re.findall(tool_id_pattern(path), on_disk)
            tag = path.rsplit("/", 1)[-1]
            planted[f"{tag}: --allocate-id STILL MINTS (restricted, not "
                    f"disabled)"] = (rc == EXIT_OK and len(minted) == 1)
            # The round-trip, off the bytes the producer wrote, not off a
            # fixture this function shaped.
            planted[f"{tag}: the minted id round-trips through "
                    f"parse_record_ids"] = (
                bool(minted) and minted[0] in parse_record_ids(on_disk, path))
        notes.append(
            f"    allocation still mints on all {len(allowed)} permitted "
            f"records ({', '.join(p.rsplit('/', 1)[-1] for p in allowed)}), "
            f"read back off the bytes main() wrote -- so the refusal below is "
            f"RESTRICTIVE, not a feature switched off")

        # ---- ARM B: the refusal, through the production path ---------------
        repo_l = fresh(L)
        rows_l = root / "rows_L.md"
        rows_l.write_text(row_form[L].format(id=ALLOCATE_PLACEHOLDER))
        before_l = (repo_l / L).read_text()
        rc_refuse = run_main(repo_l, L, rows_l, "--allocate-id")
        after_l = (repo_l / L).read_text()
        planted["LESSONS.md: --allocate-id REFUSES through main()"] = (
            rc_refuse == EXIT_REFUSED_ALLOCATION)
        planted["LESSONS.md: the refusal wrote NOTHING to the record"] = (
            after_l == before_l)
        # The code is a REFUSAL code and NOT section 2ak's instrument-error 70.
        planted["the refusal code is an allocation refusal, not section 2ak's "
                "instrument-error 70"] = (
            rc_refuse == EXIT_REFUSED_ALLOCATION and rc_refuse != 70)

        # ---- ARM C: near-misses, one byte outside the refusal --------------
        # C1: the SAME record, WITHOUT --allocate-id. Must still append.
        rows_int = root / "rows_L_int.md"
        rows_int.write_text("## L-2. a lesson with a HAND-DERIVED integer id.\n")
        rc_int = run_main(repo_l, L, rows_int, "--expect-first-id", "L-2")
        after_int = (repo_l / L).read_text()
        planted["LESSONS.md NEAR-MISS: the integer path is UNTOUCHED -- "
                "--expect-first-id still appends"] = (
            rc_int == EXIT_OK and "## L-2." in after_int)
        # C2: the CLOSEST NEIGHBOUR record, WITH --allocate-id. Must still mint.
        # NUMERICS is the neighbour that matters: it also carries zero tool ids
        # in production and its minted form is also unusual for the record, so
        # a refusal written one notch too wide would take it too.
        N = "docs/NUMERICS_KNOWLEDGE.md"
        repo_n = fresh(N)
        rows_n = root / "rows_N.md"
        rows_n.write_text(row_form[N].format(id=ALLOCATE_PLACEHOLDER))
        rc_n = run_main(repo_n, N, rows_n, "--allocate-id")
        planted["NUMERICS NEAR-MISS: allocation is NOT refused there (the "
                "minted form is INVISIBLE to N-[A-Z]+, never MISREAD)"] = (
            rc_n == EXIT_OK)
        # ... and the invisibility claim itself, measured rather than asserted.
        n_minted = re.findall(tool_id_pattern(N), (repo_n / N).read_text())
        planted["NUMERICS: the family expression N-[A-Z]+ finds NOTHING in the "
                "minted id, which is why it is invisible and not misread"] = (
            bool(n_minted) and re.findall(r"N-[A-Z]+", n_minted[0]) == [])

        # ---- ARM C3: CLAUSE PARITY -- the claim that made it legal to edit
        # a Sanaa directive's control arms, MEASURED instead of asserted.
        #
        # WHY THIS LIMB EXISTS. The scope ruling forced the `corrects:`
        # specimens on a refused record onto the LEGACY own-id form, and the
        # justification for touching those arms is "coverage is preserved, not
        # reduced: every clause is still exercised on ALL FOUR records". As a
        # COMMENT that claim is worth nothing -- a later edit could drop a
        # clause from the refused-record branch and nothing would fire, turning
        # the edit into a silent REDUCTION of her directive's coverage. So the
        # sentence is a limb.
        #
        # The sets are DERIVED FROM THE SPECIMEN LIST, never written down here:
        # a hand-written expected set would pass by agreeing with itself.
        # `core` selects the specimens the SHARED per-record loop produces, so
        # record-specific extras (DOCKET's motivating case, COST's two
        # untouched-refusal rows, and this ruling's own scope specimen) do not
        # make like look unlike.
        core_clauses: dict[str, set] = {}
        for s in _corrects_specimens():
            if s["core"]:
                core_clauses.setdefault(s["path"], set()).add(s["clause"])
        allowed_sets = {p: frozenset(c) for p, c in core_clauses.items()
                        if p not in ALLOCATION_REFUSED}
        refused_sets = {p: frozenset(c) for p, c in core_clauses.items()
                        if p in ALLOCATION_REFUSED}
        planted["clause parity: the PERMITTED records all exercise ONE core "
                "corrects: clause set (so there is a baseline to compare to)"] = (
            len(set(allowed_sets.values())) == 1 and bool(allowed_sets))
        # A baseline that exists only because every set is empty would satisfy
        # the limb above and prove nothing -- the planted-zero shape.
        planted["clause parity: that baseline is NON-EMPTY, so the comparison "
                "below is not two empty sets agreeing"] = (
            bool(allowed_sets) and all(allowed_sets.values()))
        baseline = (next(iter(allowed_sets.values())) if allowed_sets
                    else frozenset())
        planted["clause parity: at least one record is actually REFUSED, so "
                "this arm has something to measure"] = bool(refused_sets)
        for p, got in sorted(refused_sets.items()):
            tag = p.rsplit("/", 1)[-1]
            missing = sorted(baseline - got)
            extra = sorted(got - baseline)
            # The limb NAME carries the computed difference, so a failure says
            # WHICH clause went missing rather than only that something did.
            planted[f"{tag}: every core corrects: clause is still exercised on "
                    f"this REFUSED record -- missing "
                    f"{missing or 'none'}, unexpected {extra or 'none'}"] = (
                got == baseline)
        notes.append(
            f"    clause parity, derived from the specimen list: permitted "
            f"records exercise {sorted(baseline)} and every "
            f"ALLOCATION_REFUSED record exercises the same set -- so the "
            f"legacy-own-id re-scoping preserved Sanaa's corrects: coverage "
            f"rather than shrinking it, and that is now a limb rather than a "
            f"comment")

        # ---- ARM D: THE RULE-11 REGRESSION ---------------------------------
        # (i) BUILD the file that would exist if the guard were absent. The
        #     guard is removed at its own knob, so this is this module WITHOUT
        #     the repair rather than a hand-written imitation of it.
        pre = check_allocation(rows_l.read_text(), L, allocate=True,
                               apply_allocation_scope=False)
        planted["rule-11 regression: with the scope clause REMOVED the same "
                "call is ACCEPTED, so the limb below measures the guard"] = (
            pre["ok"])
        poisoned_rows, poisoned_ids = allocate_into_rows(rows_l.read_text(), L)
        would_be = before_l + poisoned_rows
        # (ii) Run rule 11's OWN derivation, verbatim, over both files.
        f_true = root / "rule11_true.md"; f_true.write_text(before_l)
        f_pois = root / "rule11_poisoned.md"; f_pois.write_text(would_be)

        def rule11(f: Path) -> str:
            done = subprocess.run(
                ["bash", "-c", RULE_11_DERIVATION.format(f=str(f))],
                capture_output=True, text=True)
            return done.stdout.strip()

        true_max, poisoned_max = rule11(f_true), rule11(f_pois)
        planted["rule-11 regression: over the record as it stands the "
                "derivation returns the TRUE maximum"] = (true_max == "1")
        planted["rule-11 regression: over the file the tool WOULD have written "
                "it returns the minted DATE instead"] = (
            poisoned_max == "20260903" or
            (poisoned_max.isdigit() and int(poisoned_max) > 10 ** 7))
        planted["rule-11 regression: and the misread number is ORDERS larger "
                "than the true maximum, so it wins every sort"] = (
            poisoned_max.isdigit() and true_max.isdigit()
            and int(poisoned_max) > int(true_max) * 1000)
        # (iii) WITH the guard, that file cannot be produced through the tool.
        planted["rule-11 regression: WITH the guard, main() refuses and the "
                "poisoned file is NOT produced"] = (
            rc_refuse == EXIT_REFUSED_ALLOCATION
            and not re.findall(tool_id_pattern(L), (repo_l / L).read_text()))
        # NEGATIVE: the poisoned id must NOT be visible to the LEGACY reader --
        # that asymmetry (tool reader content, constitution reader wrong) is the
        # whole defect, and if it ever stopped holding the diagnosis changes.
        negative["the LEGACY LESSONS pattern parses the minted id, which would "
                 "mean the defect was a plain parse failure"] = bool(
            parse_ids(poisoned_rows, RECORDS[L]))
        # NEGATIVE: allocation must not be refused on a record with no
        # prescribed integer derivation -- that would be DISABLED, not scoped.
        negative["allocation is refused on COST_CALIBRATION, the most-used "
                 "record"] = not check_allocation(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-09-03 | verification | r |\n",
            "docs/COST_CALIBRATION.md", allocate=True)["ok"]
        notes.append(
            f"    rule 11's own derivation, run VERBATIM: {true_max} over the "
            f"record as it stands, {poisoned_max} over the file --allocate-id "
            f"would have written ({len(poisoned_ids)} minted id). The guard is "
            f"what stands between those two numbers")

    return planted, negative, notes


def run_corrects_control() -> tuple[dict, dict, list[str]]:
    """SANAA'S 2026-09-03 PLUMBING AMENDMENT, DRIVEN THROUGH THE PRODUCTION PATH.

    The amendment has two halves and they need DIFFERENT kinds of proof:

      * "accepts tool-allocated ids solely inside a structured corrects: field
        on correction rows" -- a POSITIVE control (`VERIFICATION_CHARTER`
        `§2p.3(e)`): a restrictive-looking repair that refused everything it
        newly sees would be indistinguishable, from its verdicts alone, from a
        correct one. So the accept arms are the first thing here.
      * "refusal unchanged everywhere else" -- a REGRESSION control, and it is
        the one that matters. `check_allocation`'s `apply_corrects=False` knob
        reproduces this module BEFORE the amendment, so every specimen can be
        graded TWICE, by the same function, on the same bytes. The property
        asserted is not "the refusals look similar" but: the set of specimens
        whose verdict CHANGED is EXACTLY the set registered as newly accepted,
        and everything else keeps its code -- with the no-field specimens
        keeping their refusal MESSAGE byte-for-byte.

    Every arm calls `check_allocation` -- the function `main()` itself calls at
    `main`'s allocation gate, with the arguments `main()` passes -- and the disk
    block below calls `main()` end to end (`§2p.3(d)`: a test that exercises a
    redundant copy of the guarded logic tests nothing). NOTHING here
    re-implements `scan_corrects`; the masking is read back OUT of the
    production function rather than recomputed.

    Returns `(planted, negative, notes)`.
    """
    planted, negative, notes = {}, {}, []
    specs = _corrects_specimens()

    # ---- PLANT THE ZERO, before any refusal is credited -------------------
    # A refusal that failed to fire and a reader that cannot see the id look
    # identical from the outside. Every specimen that carries a tool-form id
    # must be VISIBLE to the very expression the smuggle guard uses.
    for s in specs:
        if s["cited"]:
            assert s["cited"] in re.findall(ANY_TOOL_ID, s["rows"]), s["name"]
    # THE OTHER HALF OF THE PLANT, and it is the sharper one. Two C1 specimens
    # -- a LEGACY id in the body, and an empty body -- carry NO tool-form id at
    # all, so the smuggle scan is STRUCTURALLY unable to refuse them: a legacy
    # id was never refused by that guard and never will be. Their refusal
    # therefore comes from clause C1 ALONE. If C1 degraded a malformed field to
    # "not a field" they would land silently, which is why the code refuses
    # instead of falling back to prose.
    c1_no_tool_id = [s for s in specs
                     if s["clause"] == "C1" and not s["cited"]]
    planted["the C1 specimens carrying NO tool-form id are invisible to the "
            "smuggle scan, so only C1 can refuse them"] = (
        bool(c1_no_tool_id)
        and all(not re.findall(ANY_TOOL_ID, s["rows"]) for s in c1_no_tool_id))

    # ---- limb group A: the two halves, specimen by specimen ---------------
    n_accept = 0
    newly_accepted, newly_refused, kept_code, kept_message = [], [], [], []
    for s in specs:
        on = check_allocation(s["rows"], s["path"], allocate=s["allocate"])
        off = check_allocation(s["rows"], s["path"], allocate=s["allocate"],
                               apply_corrects=False)
        if s["accepted"]:
            n_accept += 1
            planted[s["name"]] = bool(on["ok"])
            # ... and the SAME bytes were refused before the amendment. An
            # accept arm whose specimen would have passed anyway proves nothing
            # about the amendment.
            planted[f"{s['name']} -- and was REFUSED before the amendment"] = (
                (not off["ok"]) and off["code"] == EXIT_REFUSED_ALLOCATION)
            negative[f"{s['name']} -- pre-amendment code ALSO accepted it"] = (
                bool(off["ok"]))
        else:
            planted[s["name"]] = (
                (not on["ok"]) and on["code"] == EXIT_REFUSED_ALLOCATION)
            negative[f"{s['name']} -- but it was ACCEPTED"] = bool(on["ok"])
        # THE REGRESSION LEDGER, over every specimen without exception, and it
        # is kept DIRECTIONAL. "Refusal unchanged everywhere else" is a claim
        # about ONE direction: nothing that refused before may pass now. The
        # opposite direction is not a regression and the amendment makes it on
        # purpose -- a MALFORMED field refuses rather than degrading to prose.
        if off["ok"] and not on["ok"]:
            newly_refused.append(s["name"])
        elif on["ok"] and not off["ok"]:
            newly_accepted.append(s["name"])
        if on["ok"] == off["ok"] and not on["ok"]:
            kept_code.append(on["code"] == off["code"])
            if CORRECTS_OPENER not in s["rows"]:
                # No field in the bytes: `scan_corrects` is never reached, so
                # the message must be IDENTICAL, not merely similar.
                kept_message.append(on["reason"] == off["reason"])

    # ---- limb group B: THE REGRESSION ARM, stated as an equality ----------
    # This is the mechanical form of "refusal unchanged everywhere else", and
    # it is stated as a SET EQUALITY rather than a sampling: the specimens the
    # amendment newly admits are EXACTLY the ones registered as field-scoped
    # correction-row citations, and there is no tenth.
    accepted_names = sorted(s["name"] for s in specs if s["accepted"])
    planted["the ONLY inputs the amendment newly ADMITS are the registered "
            "field-scoped correction-row citations, and no others"] = (
        sorted(newly_accepted) == accepted_names)
    # The other direction, named rather than hidden: the amendment ADDS
    # refusals, and only for malformed fields carrying no tool-form id -- the
    # specimens the smuggle scan could never have refused. That widening is
    # documented at `CORRECTS_OPENER` and is strictly safer, but it is a
    # verdict change and this control states it as one.
    c1_names = sorted(s["name"] for s in specs
                      if s["clause"] == "C1" and not s["cited"])
    planted["the amendment ADDS refusals for exactly the malformed fields the "
            "smuggle scan was structurally unable to see, and for nothing "
            "else"] = (sorted(newly_refused) == c1_names)
    planted["every specimen that refused before the amendment and still "
            "refuses kept its EXIT CODE"] = (bool(kept_code) and all(kept_code))
    planted["a refusal on rows carrying NO corrects: field keeps its message "
            "BYTE-FOR-BYTE across the amendment"] = (
        bool(kept_message) and all(kept_message))
    no_field_names = {s["name"] for s in specs
                      if CORRECTS_OPENER not in s["rows"]}
    negative["the amendment moved a verdict on a specimen that carries no "
             "corrects: field at all"] = bool(
        no_field_names & (set(newly_accepted) | set(newly_refused)))

    # ---- limb group C: the two mutation knobs, each removing ONE clause ----
    # C2 and C3 are INDEPENDENT clauses, so each gets the mutation that deletes
    # it and each must flip a limb. A clause whose removal changes no verdict
    # was never load-bearing.
    c2_flipped, c3_flipped = [], []
    for s in specs:
        if s["clause"] == "C2":
            c2_flipped.append(check_allocation(
                s["rows"], s["path"], allocate=s["allocate"],
                require_correction_marker=False)["ok"])
        if s["clause"] == "C3":
            c3_flipped.append(check_allocation(
                s["rows"], s["path"], allocate=s["allocate"],
                require_own_entry=False)["ok"])
    planted["removing clause C2 lets a field on a NON-correction row through "
            "-- so C2 is load-bearing"] = (
        bool(c2_flipped) and all(c2_flipped))
    planted["removing clause C3 lets a correction row with NO id of its own "
            "through -- so C3 is load-bearing"] = (
        bool(c3_flipped) and all(c3_flipped))

    # ---- limb group D: the MASK is what the smuggle scan is shown ----------
    # Read back OUT of `scan_corrects`, never recomputed here. The mask must
    # remove the cited id and must preserve every column, or a downstream line
    # or column report would be the control's arithmetic and not the caller's.
    mask_spec = next(s for s in specs if s["accepted"] and s["allocate"])
    sc = scan_corrects(mask_spec["rows"], mask_spec["path"])
    planted["the accepted field is MASKED out of what the smuggle scan sees"] = (
        sc["ok"] and mask_spec["cited"] not in sc["masked"]
        and mask_spec["cited"] in mask_spec["rows"])
    planted["masking is length-preserving, so every reported line and column "
            "is the caller's own"] = (
        sc["ok"] and len(sc["masked"]) == len(mask_spec["rows"])
        and sc["rows"] == [1])
    planted["the accepted citation is REPORTED, not silently swallowed"] = (
        sc["ok"] and sc["cited"] == [mask_spec["cited"]])
    # AND THE MASK MEASURED AT ITS EDGE, which is the limb that discriminates a
    # real mask from "the guard stopped running on this line": one row, a
    # legitimate legacy id of its own, ONE well-formed field, and a SECOND
    # tool-form id sitting in prose OUTSIDE the field. The smuggle guard must
    # still fire, and its message must name the OUTSIDE id and NOT the cited
    # one. A guard that had merely been switched off for the line would refuse
    # nothing; a mask that blanked the whole line would name neither.
    cp = "docs/COST_CALIBRATION.md"
    inside = f"C-{_CITED_STAMP}"
    outside = "C-20260901T101112.131415Z-0badc0de"
    edge = (f"| C-9002 | 2026-09-03 | verification | "
            f"{_CORR_ENTRY[cp]} corrects:[{inside}] and it also mentions "
            f"{outside} in plain prose |\n")
    assert inside in re.findall(ANY_TOOL_ID, edge), "edge fixture: inside id"
    assert outside in re.findall(ANY_TOOL_ID, edge), "edge fixture: outside id"
    edge_r = check_allocation(edge, cp, allocate=False)
    planted["a tool id OUTSIDE the field on an otherwise-accepted correction "
            "row still REFUSES -- the mask is per-field, not per-line"] = (
        (not edge_r["ok"]) and edge_r["code"] == EXIT_REFUSED_ALLOCATION)
    planted["and that refusal names the OUTSIDE id and not the cited one -- "
            "the mask, measured at its edge"] = (
        outside in edge_r["reason"] and inside not in edge_r["reason"])
    negative["the refusal on a mixed row names the CITED id, so the mask "
             "leaked"] = (inside in edge_r.get("reason", ""))

    # ---- limb group E: THE EMPTY-INPUT ARM (`§2p.2`) ----------------------
    # Feed the guard nothing and see what it says. Two honest halves:
    empty_alloc = check_allocation("", "docs/COST_CALIBRATION.md",
                                   allocate=True)
    empty_plain = check_allocation("", "docs/COST_CALIBRATION.md",
                                   allocate=False)
    planted["EMPTY rows with --allocate-id REFUSE (the empty-input arm)"] = (
        (not empty_alloc["ok"])
        and empty_alloc["code"] == EXIT_REFUSED_ALLOCATION)
    # The other half is NOT a refusal and must not be dressed up as one: empty
    # rows with no allocation request are a legal no-op, and this module's
    # semantics are Sanaa's, not this control's. What the arm asserts is the
    # part that WOULD be a fail-open -- that nothing was ACCEPTED out of
    # nothing, so the "clean" cannot be an acceptance in disguise.
    planted["EMPTY rows manufacture NO accepted citation out of nothing"] = (
        empty_plain["ok"] and empty_plain.get("cited") == []
        and empty_plain.get("corrects_rows") == [])
    negative["empty rows report an accepted corrects: field"] = bool(
        empty_plain.get("cited"))
    # ... and the pairing that makes the empty result a MEASUREMENT rather than
    # blindness: the SAME reader, over the SAME call, DOES report an acceptance
    # on the planted rows.
    live = check_allocation(mask_spec["rows"], mask_spec["path"], allocate=True)
    planted["the same reader that saw nothing in empty rows DOES see the "
            "planted citation"] = (
        live["ok"] and live.get("cited") == [mask_spec["cited"]])

    # ---- limb group F: the LIVE lines the code's own comments name --------
    # `CORRECTION_MARKER`'s comment says a planted negative drives the one live
    # `docs/DOCKET.md` line carrying `CORRECTION ROW` -- a row ABOUT the defect,
    # which the anchor must EXCLUDE. Both fixtures below are copied verbatim
    # from the real files (2026-09-03) rather than invented, because the claim
    # in the comment is about those lines and nothing else.
    live_docket = (
        "| D-20260902T224505.958199Z-e02eb14e | 2026-09-02 | heat-transfer | "
        "**A CORRECTION ROW CANNOT NAME THE ROW IT CORRECTS: "
        "`scripts/append_record.py`'s smuggle guard AND "
        "`docs/COST_CALIBRATION.md`'s append rule 1 CANNOT BOTH BE SATISFIED** |")
    live_cost_prose = (
        "| C-20260903T162543.364120Z-e486a4a1 | 2026-09-03 | "
        "ansys-verification | **VMFL046 -- a cost row whose entry cell opens "
        "with something else.** The verdict is not what this row is about. "
        "**CORRECTION ROW IN SUBSTANCE, AND IT NAMES ITS TARGET** |")
    live_cost_true = (
        "| C-44 | 2026-08-24 | verification | **CORRECTION ROW. It corrects "
        "row `C-42` of this ledger (commit `6f005e19`) and nothing else** |")
    dk_marker = re.compile(CORRECTION_MARKER["docs/DOCKET.md"])
    ct_marker = re.compile(CORRECTION_MARKER["docs/COST_CALIBRATION.md"])
    planted["a REAL cost correction row from the live ledger IS recognised "
            "(the anchor is not vacuous)"] = bool(ct_marker.search(live_cost_true))
    negative["the live DOCKET row that DESCRIBES the defect is classified as a "
             "correction row"] = bool(dk_marker.search(live_docket))
    negative["a live cost row that only MENTIONS 'CORRECTION ROW' mid-cell is "
             "classified as one"] = bool(ct_marker.search(live_cost_prose))

    # ---- limb group G: ON DISK, through main(), on the real production path -
    planted_disk, negative_disk, notes_disk = _corrects_disk_control()
    planted.update(planted_disk)
    negative.update(negative_disk)
    notes += notes_disk

    notes.append(
        f"    corrects: amendment proved on all {len(RECORDS)} registered "
        f"records, each in its OWN correction vocabulary -- and LESSONS and "
        f"NUMERICS have NO live correction row, so these fixtures are the only "
        f"thing that drives their markers at all")
    notes.append(
        f"    REGRESSION ARM (the 'refusal unchanged everywhere else' half): "
        f"{len(specs)} specimens graded TWICE by check_allocation, "
        f"apply_corrects False then True. NEWLY ADMITTED "
        f"{len(newly_accepted)}, registered as newly accepted {n_accept}, sets "
        f"{'EQUAL' if sorted(newly_accepted) == accepted_names else 'DIFFERENT'}"
        f"; NEWLY REFUSED {len(newly_refused)} -- malformed fields the smuggle "
        f"scan could not see, which is a widening and is named as one, not a "
        f"regression; {len(kept_code)} unchanged refusals kept their exit code "
        f"and {len(kept_message)} of them their message byte-for-byte")
    return planted, negative, notes


def _corrects_disk_control() -> tuple[dict, dict, list[str]]:
    """The amendment driven END TO END through `main()`, read back off disk.

    `VERIFICATION_CHARTER` `§2j`, asked the way `§2j` asks it: WHO WROTE THE
    BYTES THIS CONTROL READS? `main()` did -- the same `main()` the lab invokes,
    the same argument vector, ending in the same `wt_file.write_text`. This
    function supplies a throwaway repository and a rows file and nothing else.

    The sharpest limb here is the one no in-memory arm can reach: after an
    ACCEPTED correction row lands, the cited id is IN THE RECORD'S BYTES TWICE
    -- once as its own row's entry and once as a citation -- and
    `parse_record_ids`, the reader both reconcilers use, must count it ONCE.
    An acceptance that made the reconcilers report a duplicate would be a
    repair that broke the record it repaired.
    """
    planted, negative, notes = {}, {}, []
    path = "docs/COST_CALIBRATION.md"
    env = _clean_git_env()

    def git(repo: Path, *args: str) -> None:
        done = subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, env=env)
        if done.returncode != 0:  # pragma: no cover - a broken box, not a defect
            raise RuntimeError(f"git {args[0]} failed in the corrects control "
                               f"repo: {done.stderr.strip()[:200]}")

    def run_main(repo: Path, rows: Path, *extra: str) -> int:
        buf_o, buf_e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
            return main(["--path", path, "--rows", str(rows),
                         "--repo", str(repo), *extra])

    with tempfile.TemporaryDirectory(prefix="append_record_corrects_") as td:
        repo = Path(td) / "repo"
        (repo / "docs").mkdir(parents=True)
        record = repo / path
        record.write_text(
            "| id | date | team | process |\n|---|---|---|---|\n"
            "| C-1 | 2026-08-31 | verification | a seeded LEGACY row |\n")
        subprocess.run(["git", "init", "-q", str(repo)],
                       capture_output=True, text=True, env=env, check=True)
        git(repo, "config", "user.email", "control@certonomous.invalid")
        git(repo, "config", "user.name", "append_record corrects control")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "seed the corrects control record")

        # (1) A NORMAL row lands, so there is a REAL id to correct. Its id is
        # minted by main(); nothing below cites an id this control invented.
        target_rows = Path(td) / "rows_target.md"
        target_rows.write_text(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-09-03 | verification | the row "
            f"that will be corrected |\n")
        rc_t = run_main(repo, target_rows, "--allocate-id")
        after_target = record.read_text()
        target_ids = re.findall(tool_id_pattern(path), after_target)
        planted["disk: the row to be corrected landed at OK"] = (
            rc_t == EXIT_OK and len(target_ids) == 1)
        target = target_ids[0]
        n_entries_before = len(parse_record_ids(after_target, path))
        # 2026-09-07: land the target row in HEAD before the correction builds on
        # it -- the production base is HEAD's committed blob, and an uncommitted
        # target would be DISCARDED by the next append rather than corrected.
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "land the row to be corrected")

        # (2) THE POSITIVE CONTROL (`§2p.3(e)`), through main(): a correction
        # row citing that very id inside the field.
        corr_rows = Path(td) / "rows_correction.md"
        corr_rows.write_text(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-09-03 | verification | "
            f"**CORRECTION ROW** -- append rule 1, and it names the row it "
            f"corrects: corrects:[{target}] |\n")
        rc_c = run_main(repo, corr_rows, "--allocate-id")
        after_corr = record.read_text()          # <- bytes written by main()
        planted["disk: a correction row citing a REAL id inside the field "
                "lands at OK"] = (rc_c == EXIT_OK)
        planted["disk: the record CHANGED, so the writer can write"] = (
            after_corr != after_target)
        planted["disk: the cited id is IN THE RECORD'S BYTES twice -- its own "
                "row and the citation"] = (after_corr.count(target) == 2)
        planted["disk: and parse_record_ids -- the reader both reconcilers "
                "use -- counts it ONCE, so the citation is not an entry"] = (
            len(parse_record_ids(after_corr, path)) == n_entries_before + 1
            and parse_record_ids(after_corr, path).count(target) == 1)
        planted["disk: the correction row carries its OWN freshly minted id, "
                "distinct from the one it cites"] = (
            len(set(re.findall(tool_id_pattern(path), after_corr))) == 2)
        notes.append(
            f"    corrects: disk control -- main() wrote a correction row "
            f"citing {target}; the id appears "
            f"{after_corr.count(target)}x in the bytes and "
            f"{parse_record_ids(after_corr, path).count(target)}x as an entry")

        # 2026-09-07: land the correction too, so the empty-input arm below reads
        # a HEAD that carries it (the production base is HEAD's committed blob).
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "land the correction row")

        # (3) THE REFUSALS, through the same main(), with the record required
        # BYTE-IDENTICAL afterwards. A refusal that wrote anything would be a
        # different defect wearing a refusal's message.
        bare_rows = Path(td) / "rows_bare.md"
        bare_rows.write_text(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-09-03 | verification | "
            f"**CORRECTION ROW** -- it corrects {target}, named in prose |\n")
        rc_b = run_main(repo, bare_rows, "--allocate-id")
        planted["disk: the SAME id OUTSIDE the field refuses at the allocation "
                "code, and the record is byte-identical"] = (
            rc_b == EXIT_REFUSED_ALLOCATION and record.read_text() == after_corr)
        negative["disk: a bare citation on a correction row is accepted"] = (
            rc_b == EXIT_OK)

        ord_rows = Path(td) / "rows_ordinary.md"
        ord_rows.write_text(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-09-03 | verification | an "
            f"ordinary cost row corrects:[{target}] |\n")
        rc_o = run_main(repo, ord_rows, "--allocate-id")
        planted["disk: the field on a NON-correction row refuses, and the "
                "record is byte-identical"] = (
            rc_o == EXIT_REFUSED_ALLOCATION and record.read_text() == after_corr)
        negative["disk: a corrects: field on an ordinary row is accepted"] = (
            rc_o == EXIT_OK)

        mal_rows = Path(td) / "rows_malformed.md"
        mal_rows.write_text(
            f"| {ALLOCATE_PLACEHOLDER} | 2026-09-03 | verification | "
            f"**CORRECTION ROW** -- corrects:[{target} |\n")
        rc_m = run_main(repo, mal_rows, "--allocate-id")
        planted["disk: an UNTERMINATED field refuses, and the record is "
                "byte-identical"] = (
            rc_m == EXIT_REFUSED_ALLOCATION and record.read_text() == after_corr)

        noid_rows = Path(td) / "rows_noid.md"
        noid_rows.write_text(
            f"| a note | 2026-09-03 | verification | **CORRECTION ROW** -- "
            f"corrects:[{target}] |\n")
        rc_n = run_main(repo, noid_rows)
        planted["disk: a correction row with NO id of its own refuses, and the "
                "record is byte-identical"] = (
            rc_n == EXIT_REFUSED_ALLOCATION and record.read_text() == after_corr)

        # (4) THE EMPTY-INPUT ARM on the production path (`§2p.2`).
        empty_rows = Path(td) / "rows_empty.md"
        empty_rows.write_text("")
        rc_e1 = run_main(repo, empty_rows, "--allocate-id")
        planted["disk: an EMPTY rows file with --allocate-id refuses, and the "
                "record is byte-identical"] = (
            rc_e1 == EXIT_REFUSED_ALLOCATION and record.read_text() == after_corr)
        rc_e2 = run_main(repo, empty_rows)
        planted["disk: an EMPTY rows file adds NO entry -- the empty path "
                "cannot produce an accepted citation"] = (
            len(parse_record_ids(record.read_text(), path))
            == n_entries_before + 1)
        notes.append(
            f"    corrects: empty-input arm on the production path -- "
            f"--allocate-id over empty rows returns exit {rc_e1}; without it "
            f"main() returns exit {rc_e2} and adds no entry. THE SECOND IS NOT "
            f"A REFUSAL, and is reported as what it is: an empty rows file is a "
            f"legal no-op in this module, unchanged by the amendment and NOT "
            f"this control's to change")

        # (5) THE AMENDMENT'S OWN MUTATION, on the bytes main() just wrote:
        # neutering the mask must turn that accepted row back into a refusal.
        landed_row = [ln for ln in after_corr.splitlines(keepends=True)
                      if CORRECTS_OPENER in ln]
        planted["disk: exactly one landed row carries the field"] = (
            len(landed_row) == 1)
        # (5a) The bytes main() ACTUALLY graded -- the rows file, placeholder
        # intact -- accept under the amendment and refuse without it. Same
        # bytes, same function, one knob.
        graded = corr_rows.read_text()
        planted["disk: the bytes main() graded ACCEPT under the amendment and "
                "REFUSE with apply_corrects=False"] = (
            check_allocation(graded, path, allocate=True)["ok"]
            and not check_allocation(graded, path, allocate=True,
                                     apply_corrects=False)["ok"])
        # (5b) AND THE FIELD IS NOT A LAUNDERING CHANNEL. Resubmit the LANDED
        # row verbatim: its `corrects:` field is still well-formed and still
        # accepted, but the row now carries a TOOL-FORM id at its entry
        # position, with no placeholder left to fill. It must still refuse.
        #
        # WHICH CLAUSE REFUSES IT IS ITSELF A MEASUREMENT, and it is not the
        # one a reader would guess: C3 fires, not the smuggle guard, because
        # C3's own-id test reads `RECORDS[path]` -- the LEGACY pattern -- so a
        # landed TOOL-allocated id does not count as "an id of its own". That
        # is exactly what C3's own comment says it admits (a placeholder, or a
        # legacy id this record parses) and it is FAIL-CLOSED, so it is
        # recorded here as the measured behaviour rather than assumed away. The
        # limb asserts only what matters: the row does not land twice.
        #
        # AND IT DEGRADES TO A GRADED FAILURE, NEVER TO AN EXCEPTION. Every
        # mutation that stops the correction row from landing empties
        # `landed_row`, and an unguarded `landed_row[0]` would kill those
        # mutants with an `IndexError` at rc 1 instead of a control failure at
        # exit 5 -- which is the shape this lab docketed on 2026-09-02 (three
        # mutations stopping a comparator as uncaught exceptions). A mutant
        # killed by a crash is killed for the wrong reason and reports nothing.
        if len(landed_row) == 1:
            own_ids = sorted(
                set(re.findall(tool_id_pattern(path), landed_row[0]))
                - {target})
            replay = check_allocation(landed_row[0], path, allocate=False)
            planted["disk: replaying the LANDED row verbatim still REFUSES -- "
                    "an accepted field is not a channel for an entry-position "
                    "id"] = (
                len(own_ids) == 1 and (not replay["ok"])
                and replay["code"] == EXIT_REFUSED_ALLOCATION)
            negative["disk: the landed row, resubmitted verbatim, would land a "
                     "second time"] = bool(replay["ok"])
            notes.append(
                f"    corrects: the landed row resubmitted verbatim refuses at "
                f"exit {replay['code']}, and the clause that fires is C3 (no id "
                f"of its OWN that this record's LEGACY pattern parses), not the "
                f"smuggle guard -- measured, and fail-closed either way")
        else:
            planted["disk: replaying the LANDED row verbatim still REFUSES -- "
                    "an accepted field is not a channel for an entry-position "
                    "id"] = False
            notes.append(
                f"    corrects: the replay limb could not be evaluated -- "
                f"{len(landed_row)} landed row(s) carry the field, not 1, so "
                f"the accepted row did not land. Reported as a control FAILURE, "
                f"never as a pass and never as a crash")
    return planted, negative, notes


# --------------------------------------------------------------- controls
#: The near-miss specimen for the size-report control: characters this lab's
#: records are genuinely full of, every one of them multi-byte in UTF-8. The
#: point is not decoration -- it is that `len(str)` and `len(bytes)` must DISAGREE
#: on this text, so the limb below cannot pass by the two happening to coincide.
#: Measured widths: `§` 2 bytes, `—` 3, `⚠` 3, `⚡` 3, `≈` 3.
SIZE_CONTROL_MULTIBYTE = "§ — ⚠ ⚡ ≈"


def run_size_report_control() -> tuple[dict, dict, list[str]]:
    """THE REPORTED SIZES ARE BYTES, driven through `main()` on a real record.

    THE DEFECT THIS LIMB EXISTS FOR. Every size in the run report was
    `len(str)` -- characters -- printed under the label `bytes`. Nothing refused,
    nothing was mis-written; the report simply named a unit it was not using, and
    a healthy run therefore LOOKED like an 11,741-unit size mismatch against
    `git cat-file -s` on `docs/COST_CALIBRATION.md`. That is indistinguishable
    from the stale-HEAD symptom this module reports sizes in order to expose.

    WHY IT IS DRIVEN THROUGH `main()` AND NOT AGAINST `utf8_len`. Asserting
    `utf8_len(x) == len(x.encode())` restates the function's own definition and
    would have passed on the day the defect shipped, because the defect was never
    in a size function -- there was none -- it was at the four PRINT SITES. So
    this control reads the REPORT `main()` actually emitted, parses the numbers
    back out of it, and compares them to the true UTF-8 length of the artifact
    each one claims to describe. VERIFICATION_CHARTER section 2j's question --
    who wrote the bytes this control reads? -- answers: `main()` did, on the same
    argument vector the lab uses.

    THE NEAR-MISS CONTROL, AND WHY THE LIMB IS WORTHLESS WITHOUT IT. On
    ASCII-only text characters and bytes are EQUAL, so an equality limb over an
    ASCII specimen passes under the defect and under the repair alike -- it would
    not have caught this bug and is not a control. Every artifact this limb
    grades therefore carries `SIZE_CONTROL_MULTIBYTE`, and the FIRST thing
    asserted is that characters and bytes genuinely DIFFER on each of them. The
    negative form is the pre-repair behaviour itself, computed alongside: if any
    reported number equals the CHARACTER count of its artifact, the old defect is
    back, and it is scored as a negative that must not fire.

    Returns `(planted, negative, notes)`.
    """
    planted, negative, notes = {}, {}, []
    path = "docs/COST_CALIBRATION.md"
    env = _clean_git_env()
    mb = SIZE_CONTROL_MULTIBYTE

    def git(repo: Path, *args: str) -> None:
        done = subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, env=env)
        if done.returncode != 0:  # pragma: no cover - a broken box, not a defect
            raise RuntimeError(f"git {args[0]} failed in the size control repo: "
                               f"{done.stderr.strip()[:200]}")

    with tempfile.TemporaryDirectory(prefix="append_record_size_") as td:
        repo = Path(td) / "repo"
        (repo / "docs").mkdir(parents=True)
        record = repo / path

        # ---- the committed side: multi-byte, and a legacy id the pattern sees.
        head_text = (
            "| id | date | team | process |\n|---|---|---|---|\n"
            f"| C-1 | 2026-09-04 | verification | a seeded LEGACY row {mb} |\n")
        record.write_text(head_text)
        subprocess.run(["git", "init", "-q", str(repo)],
                       capture_output=True, text=True, env=env, check=True)
        git(repo, "config", "user.email", "control@certonomous.invalid")
        git(repo, "config", "user.name", "append_record size control")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "seed the size control record")

        # ---- the worktree tail: multi-byte, and DELIBERATELY id-less, so it is
        # the D369 invisible-tail form. An id here would refuse at exit 6 and the
        # WROTE line -- one of the four numbers graded -- would never be printed.
        tail_text = f"\nA peer's unlanded paragraph, no row id, {mb}\n"
        record.write_text(head_text + tail_text)

        rows = Path(td) / "rows.md"
        rows_text = f"| C-2 | 2026-09-04 | verification | an appended row {mb} |\n"
        rows.write_text(rows_text)

        buf_o, buf_e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
            rc = main(["--path", path, "--rows", str(rows), "--repo", str(repo)])
        report = buf_o.getvalue()
        planted["the graded run reached OK, so all four sizes were printed"] = (
            rc == EXIT_OK)

        # The four artifacts each reported number claims to describe. `merged` is
        # read BACK OFF DISK rather than recomputed, so the WROTE limb grades the
        # bytes that actually landed.
        merged_text = record.read_text() if rc == EXIT_OK else ""
        artifacts = {
            "committed side": head_text,
            "worktree side": head_text + tail_text,
            "WORKTREE TAIL": tail_text,
            "WROTE": merged_text,
        }

        # ---- THE NEAR-MISS GUARD, asserted BEFORE the equality limbs ----------
        # If characters and bytes coincided on any of these, that limb would pass
        # under the defect too and prove nothing.
        for name, text in artifacts.items():
            planted[f"NEAR-MISS: {name} is genuinely multi-byte -- its character "
                    f"count and byte count DIFFER"] = (
                utf8_len(text) > len(text) > 0)

        # ---- parse the numbers back out of the report main() emitted ----------
        found = {
            "committed side": re.search(r"committed side\s*:.*?\((\d+) bytes,",
                                        report),
            "worktree side": re.search(r"worktree side\s*:.*?\((\d+) bytes\)",
                                       report),
            "WORKTREE TAIL": re.search(r"WORKTREE TAIL\s*:\s*(\d+) bytes beyond",
                                       report),
            "WROTE": re.search(r"WROTE\s*:.*?\((\d+) bytes\)", report),
        }
        for name, hit in found.items():
            planted[f"the report actually printed a size for {name!r}"] = bool(hit)

        for name, text in artifacts.items():
            hit = found[name]
            reported = int(hit.group(1)) if hit else None
            planted[f"{name}: the reported size EQUALS the UTF-8 byte length "
                    f"of what it describes"] = (reported == utf8_len(text))
            # NEGATIVE: the pre-repair value. `len(str)` is what the four sites
            # printed before this repair, and on a multi-byte specimen it is a
            # DIFFERENT number -- so this firing means the defect returned.
            negative[f"{name}: the report prints the CHARACTER count, which is "
                     f"what the defect printed"] = (reported == len(text))

        deltas = {n: utf8_len(t) - len(t) for n, t in artifacts.items()}
        notes.append(
            "    size report graded on a MULTI-BYTE specimen, so characters and "
            f"bytes cannot coincide: byte-minus-character delta {deltas}")
        notes.append(
            "    the four graded numbers were parsed out of the report main() "
            f"itself printed (rc {rc}), not recomputed from its inputs; the "
            "WROTE limb grades the merged file read back off disk")

    # ---- THE FIFTH SITE: the OFFSET inside the exit-2 refusal reason ---------
    # THE SAME DEFECT ONE LAYER DEEPER, AND THE MOST LOAD-BEARING INSTANCE OF IT.
    # `merge` scans `str`, so `at` is a CHARACTER index; it was printed as
    # `first at byte {at}`. That number is what a reader sees AT THE MOMENT THEY
    # ARE DIAGNOSING A REAL STALE HEAD OR TRUNCATION, and the next thing they do
    # is take it to `cmp`, which reports a BYTE offset. Handing them a character
    # offset to compare against a byte offset is the phantom chase this whole
    # repair exists to end, at the one moment it costs the most.
    #
    # THE NEAR-MISS IS SHARPER HERE THAN FOR THE FOUR SIZES, and it is why the
    # specimen is built the way it is: the DIVERGENCE POINT must sit AFTER the
    # multi-byte content. A specimen that diverges inside a pure-ASCII prefix has
    # character offset == byte offset, so it would pass under the defect and
    # prove nothing -- even if the file as a whole contains multi-byte text
    # further on. So the marker below is placed after the multi-byte run, and the
    # difference between the two offsets is asserted BEFORE either is graded.
    #
    # THE REFUSAL IS DRIVEN, NOT DESCRIBED: `main()` returns exit 2 here, and the
    # offset is parsed back out of the reason string it actually emitted.
    with tempfile.TemporaryDirectory(prefix="append_record_offset_") as td:
        repo = Path(td) / "repo"
        (repo / "docs").mkdir(parents=True)
        record = repo / path

        # The marker is 8 characters and its replacement is 8 characters, so the
        # worktree is neither shorter nor longer -- this is a pure in-place EDIT
        # inside the committed bytes, which is the exit-2 case, and the
        # "SHORTER ... truncation" clause deliberately does NOT fire.
        marker, edited_marker = "ORIGINAL", "MUTATED!"
        head_text = (
            "| id | date | team | process |\n|---|---|---|---|\n"
            f"| C-1 | 2026-09-04 | verification | a seeded row {mb} {marker} |\n")
        record.write_text(head_text)
        subprocess.run(["git", "init", "-q", str(repo)],
                       capture_output=True, text=True, env=env, check=True)
        git(repo, "config", "user.email", "control@certonomous.invalid")
        git(repo, "config", "user.name", "append_record offset control")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "seed the offset control record")

        worktree_text = head_text.replace(marker, edited_marker)
        record.write_text(worktree_text)

        # The expected divergence point, derived INDEPENDENTLY of `merge`'s own
        # scan: the two strings are identical up to the marker by construction,
        # and that identity is asserted rather than assumed.
        at = head_text.index(marker)
        char_off, byte_off = at, utf8_len(head_text[:at])
        planted["the offset specimen diverges exactly where the control "
                "intends"] = (
            head_text[:at] == worktree_text[:at]
            and head_text[at] != worktree_text[at])

        # ---- THE NEAR-MISS GUARD, asserted BEFORE the offset is graded -------
        planted["NEAR-MISS: the divergence sits AFTER multi-byte content, so the "
                "CHARACTER offset and the BYTE offset genuinely differ"] = (
            byte_off > char_off > 0)

        rows_off = Path(td) / "rows_off.md"
        rows_off.write_text(
            f"| C-2 | 2026-09-04 | verification | a row that never lands {mb} |\n")

        buf_o, buf_e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
            rc_off = main(["--path", path, "--rows", str(rows_off),
                           "--repo", str(repo)])
        reason = buf_e.getvalue()

        # The refusal fired, with its exit code and its write-nothing property
        # intact. This repair touched a MESSAGE; if it had touched the logic,
        # these three limbs are where that would show.
        planted["the exit-2 refusal still fires on an edit inside the committed "
                "bytes"] = (rc_off == EXIT_REFUSED_DISAGREES)
        planted["the refusing run wrote NOTHING -- the record is unchanged"] = (
            record.read_text() == worktree_text)

        hit = re.search(r"first at byte (\d+) of (\d+)", reason)
        planted["the refusal reason actually printed an offset and a total"] = (
            bool(hit))
        got_off = int(hit.group(1)) if hit else None
        got_total = int(hit.group(2)) if hit else None

        planted["the refusal offset is the UTF-8 BYTE offset of the divergence"] = (
            got_off == byte_off)
        planted["the refusal total is the UTF-8 BYTE length of the committed "
                "blob"] = (got_total == utf8_len(head_text))
        # NEGATIVE: the pre-repair values. Both are DIFFERENT numbers on this
        # specimen, so either one firing means the defect returned.
        negative["the refusal prints the CHARACTER offset, which is what the "
                 "defect printed"] = (got_off == char_off)
        negative["the refusal prints the CHARACTER length of the blob, which is "
                 "what the defect printed"] = (got_total == len(head_text))

        notes.append(
            f"    exit-2 refusal DRIVEN (rc {rc_off}) on a specimen whose "
            f"divergence sits after multi-byte content: character offset "
            f"{char_off}, byte offset {byte_off}, delta {byte_off - char_off}; "
            f"blob {len(head_text)} characters / {utf8_len(head_text)} bytes. "
            f"The offset was parsed back out of the reason string main() emitted")

    # ---- THE SIXTH SITE: the TRUNCATION clause's own comparison --------------
    # THE SHARPEST NEAR-MISS OF THE FAMILY, and the only site where the defect
    # produced an outright FALSE SENTENCE rather than a misleading number.
    #
    # The clause is selected by comparing the two lengths. Compared as
    # CHARACTERS, a worktree that replaced a run of ASCII with fewer multi-byte
    # characters is "shorter" -- while being LONGER on disk. The tool then said
    # TRUNCATION about a file that had GROWN, and `ls -l` would have flatly
    # contradicted it. That is worse than an unhelpful number: it teaches the
    # reader to distrust the refusal itself.
    #
    # TWO SPECIMENS, AND THE SECOND IS NOT OPTIONAL. Asserting only that the
    # clause is ABSENT on specimen (a) would pass just as well if the clause had
    # been deleted outright -- a reader that can never say "truncation" is not
    # this module working. So specimen (b) is a genuinely byte-shorter worktree
    # and requires the clause to still be PRESENT. That is the planted-zero
    # discipline in its proper shape (CLAUDE.md rule 3): (b) shows the sentence
    # CAN be produced, which is what makes (a)'s silence a measurement.
    with tempfile.TemporaryDirectory(prefix="append_record_trunc_") as td:
        repo = Path(td) / "repo"
        (repo / "docs").mkdir(parents=True)
        record = repo / path

        # 10 ASCII characters, replaced by 4 multi-byte ones: -6 characters,
        # +1 byte. The whole site-6 near-miss lives in that pair of signs.
        ascii_run, mb_run = "ABCDEFGHIJ", "§—⚠⚡"
        head_text = (
            "| id | date | team | process |\n|---|---|---|---|\n"
            f"| C-1 | 2026-09-04 | verification | a seeded row {ascii_run} |\n")
        record.write_text(head_text)
        subprocess.run(["git", "init", "-q", str(repo)],
                       capture_output=True, text=True, env=env, check=True)
        git(repo, "config", "user.email", "control@certonomous.invalid")
        git(repo, "config", "user.name", "append_record truncation control")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "add", "--", path)
        git(repo, "commit", "-q", "-m", "seed the truncation control record")

        rows_t = Path(td) / "rows_trunc.md"
        rows_t.write_text(
            f"| C-2 | 2026-09-04 | verification | a row that never lands {mb} |\n")

        def refuse_reason(wt_text: str) -> tuple[int, str]:
            record.write_text(wt_text)
            bo, be = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(bo), contextlib.redirect_stderr(be):
                code = main(["--path", path, "--rows", str(rows_t),
                             "--repo", str(repo)])
            return code, be.getvalue()

        # ---- specimen (a): CHARACTER-shorter, BYTE-longer -------------------
        wt_a = head_text.replace(ascii_run, mb_run)

        # THE NEAR-MISS GUARD, asserted BEFORE the clause is graded. If the
        # specimen were not character-shorter AND byte-longer at once, the limb
        # below would pass under the defect and prove nothing.
        planted["NEAR-MISS: the specimen is CHARACTER-SHORTER than the blob"] = (
            len(wt_a) < len(head_text))
        planted["NEAR-MISS: the SAME specimen is BYTE-LONGER than the blob, so "
                "the two comparisons genuinely disagree"] = (
            utf8_len(wt_a) > utf8_len(head_text))

        rc_a, reason_a = refuse_reason(wt_a)
        planted["(a) the exit-2 refusal still fires on the byte-longer "
                "specimen"] = (rc_a == EXIT_REFUSED_DISAGREES)
        planted["(a) a byte-LONGER worktree is NOT called a truncation"] = (
            "truncation" not in reason_a)
        negative["(a) the refusal calls a byte-LONGER worktree a TRUNCATION, "
                 "which is what the defect said"] = ("truncation" in reason_a)

        # ---- specimen (b): the PAIRED POSITIVE, genuinely byte-shorter ------
        # Without this the limb above would be satisfied by a clause that can
        # never fire at all.
        wt_b = head_text[:-14]
        planted["NEAR-MISS: specimen (b) is genuinely BYTE-shorter than the "
                "blob"] = (utf8_len(wt_b) < utf8_len(head_text))
        rc_b, reason_b = refuse_reason(wt_b)
        planted["(b) the exit-2 refusal still fires on a real truncation"] = (
            rc_b == EXIT_REFUSED_DISAGREES)
        planted["(b) a genuinely byte-shorter worktree IS still called a "
                "truncation -- the clause can fire, so (a)'s silence is a "
                "measurement and not a dead reader"] = (
            "truncation" in reason_b)
        negative["(b) the truncation clause has gone silent altogether, so (a) "
                 "proves nothing"] = ("truncation" not in reason_b)

        notes.append(
            f"    truncation clause graded BOTH WAYS. (a) character-shorter but "
            f"byte-longer -- blob {len(head_text)} chars / "
            f"{utf8_len(head_text)} bytes vs worktree {len(wt_a)} chars / "
            f"{utf8_len(wt_a)} bytes: clause correctly ABSENT (rc {rc_a}). "
            f"(b) genuinely byte-shorter -- worktree {len(wt_b)} chars / "
            f"{utf8_len(wt_b)} bytes: clause correctly PRESENT (rc {rc_b}), "
            f"which is what makes (a) a measurement")

    return planted, negative, notes


def run_controls() -> tuple[control_kind.ControlLedger, int, list[str]]:
    """Plant D369's OWN invisible case and prove BOTH forms on it.

    WHY THIS NEEDS A RECOGNITION CONTROL, NOT A REACHABILITY ONE. This module's
    success is a zero: zero worktree bytes lost. Proving it can read the two
    files would not touch that. What has to be shown is that the merge PRESERVES
    content the id pattern cannot see -- because that is exactly what D369 lost,
    and exactly what every ID-set reconciliation is blind to. So each planted
    form below is worktree-only content that matches NO id pattern, and the
    NEGATIVE form is the overwrite itself: if the overwrite did not drop them,
    this module would have no reason to exist.

    A SECOND control was added for the tail-id repair (closure `52e5de39`, the
    D369 family's third bite). Its claim is the opposite shape -- not "bytes
    survived" but "a collision was refused" -- so it plants peer tails that DO
    carry ids and requires a refusal with `EXIT_REFUSED_TAIL_ID` while the tail
    is still preserved verbatim, with a cross-series tail as the negative form
    that must NOT block. Both id forms are asserted VISIBLE to the pattern
    first: a refusal that failed to fire and a reader that could not see the id
    look identical from the outside, and only one of them is this module working.
    """
    head = "# R\n\n| D1 | one |\n| D2 | two |\n"
    rows = "| D3 | three |\n"
    forms = {
        "an id-less paragraph": "\nAn in-progress paragraph naming no row id.\n",
        # A row whose first cell is not yet CLOSED. `| D9 | half-written`
        # would not do: the docket pattern matches it, so it is not invisible
        # and the control below rejected it -- which is the control working.
        "a partial row, first cell unclosed": "| D9 mid-typing, no closing pipe",
        "a bare trailing blank line": "\n",
        "a fenced block naming no id": "\n```\nscratch\n```\n",
    }
    pattern = RECORDS["docs/DOCKET.md"]
    planted, notes = {}, []
    # 2026-09-07 REFRAME. Production (main) NO LONGER preserves the worktree tail
    # -- it discards it (see limb group 8 below and the module amendment). The
    # tail-preservation and tail-id limbs in this group and the next three now
    # drive the RETAINED old path explicitly via `preserve_worktree_tail=True`,
    # so they still prove that path behaves exactly as the pre-fix code did. That
    # is what makes the old path a MEANINGFUL RED reference for the discard limb:
    # a negative that no longer reproduces the bug is a no-op, and these limbs
    # prove it still does. The prefix-test refusals (edited/truncated, below) are
    # unconditional and need no keyword.
    for name, tail in forms.items():
        wt = head + tail
        got = merge(head, wt, rows, preserve_worktree_tail=True)
        preserved = bool(got["ok"]) and tail.rstrip("\n") in (got["merged"] or "")
        # Control (d) after the tail-id repair: an ID-LESS tail must still merge,
        # still be preserved, AND still not block the append. A repair that made
        # the id assert tail-aware could easily have made an invisible tail
        # refuse; this asserts it did not.
        id_ok = check_first_id(parse_ids(head, pattern),
                               parse_ids(got["tail"] or "", pattern),
                               parse_ids(rows, pattern))["ok"] if got["ok"] \
            else False
        planted[name] = bool(preserved and id_ok)
        if got["ok"] and got["separator_inserted"]:
            notes.append(f"    separator inserted for {name!r} (partial line)")
        # And the id pattern genuinely cannot see it -- that is the claim.
        assert not parse_ids(tail, RECORDS["docs/DOCKET.md"]), name

    # NEGATIVE: the overwrite form. It must DROP every one of them.
    overwrite_kept = any(
        tail.rstrip("\n") and tail.rstrip("\n") in (head + rows)
        for tail in forms.values())

    # ---- the id arithmetic, planted against the tail (closure 52e5de39) ----
    # The defect: HEAD max D2, a peer's unlanded row in the worktree tail, and a
    # caller appending the id that peer already used. Old assert read HEAD only,
    # so 3 == 2 + 1 passed and the merged file carried D3 twice. Each form below
    # must REFUSE with EXIT_REFUSED_TAIL_ID **and** still preserve the tail --
    # refusing by dropping somebody's row would be a different defect.
    id_forms = {
        "a peer tail carrying the would-be next id":
            "| D3 | peer, unlanded, same number |\n",
        "a peer tail already several numbers ahead":
            "| D7 | peer, unlanded, further ahead |\n",
    }
    id_planted = {}
    for name, tail in id_forms.items():
        # Plant the zero: the reader must be shown able to SEE this id, or a
        # refusal that failed to fire would be indistinguishable from blindness.
        assert parse_ids(tail, pattern), name
        got_id = merge(head, head + tail, rows, preserve_worktree_tail=True)
        v = check_first_id(parse_ids(head, pattern),
                           parse_ids(got_id["tail"] or "", pattern),
                           parse_ids(rows, pattern))
        refused = (not v["ok"]) and v["code"] == EXIT_REFUSED_TAIL_ID
        preserved_too = bool(got_id["ok"]) and tail in (got_id["merged"] or "")
        id_planted[name] = bool(refused and preserved_too)
        if refused:
            notes.append(
                f"    id refusal proved ({name}): exit {v['code']}, tail ids "
                f"{v['tail_in_series']}, HEAD max {v['head_max']}, tail max "
                f"{v['tail_max']}, correct next id {v['next_id']}; tail still "
                f"preserved verbatim: {preserved_too}")

    # NEGATIVE FORM: a tail id in a DIFFERENT series must NOT block this append.
    # Ids are per-series (rule 11; N-B26 follows N-B25 whatever N-T is doing), so
    # `G7` cannot collide with `D3` and the append must proceed. Asserting the
    # pattern DOES see `G7` is what stops this from being a vacuous pass.
    cross_tail = "| G7 | another series, unlanded |\n"
    assert parse_ids(cross_tail, pattern) == ["G7"], "cross-series form vacuous"
    cross_m = merge(head, head + cross_tail, rows, preserve_worktree_tail=True)
    cross_v = check_first_id(parse_ids(head, pattern),
                             parse_ids(cross_m["tail"] or "", pattern),
                             parse_ids(rows, pattern))
    cross_blocked = not cross_v["ok"]
    if not cross_blocked:
        notes.append(
            "    cross-series decision proved: the tail's 'G7' IS parsed by the "
            "pattern and is deliberately ignored for the D-series arithmetic "
            f"(effective max {cross_v['effective_max']}), so the D3 append "
            "proceeds -- a tail id in another series is arithmetically "
            "irrelevant and must not block")

    # ---- the C series: the cost-calibration ledger's own pattern ----------
    # `docs/COST_CALIBRATION.md` is appended by all five teams, so it is the
    # record most exposed to the collision the block above refuses. Its ids
    # arrived in a 2026-08-23 format amendment, and this control exercises the
    # NEW pattern rather than assuming the D-series proof carries over: the C
    # ids carry a hyphen, so a pattern copied without its trap would parse
    # nothing at all and every check below would pass vacuously.
    c_pattern = RECORDS["docs/COST_CALIBRATION.md"]
    c_head = ("| id | date | team | process |\n|---|---|---|---|\n"
              "| C-1 | 2026-08-23 | a | one |\n"
              "| C-2 | 2026-08-23 | b | two |\n")
    c_rows = "| C-3 | 2026-08-23 | c | three |\n"
    # Plant the zero on the reader itself, before anything is concluded from it.
    assert parse_ids(c_rows, c_pattern) == ["C-3"], "C-series rows unreadable"
    assert max_for_series(parse_ids(c_head, c_pattern), "C-") == 2, \
        "C-series max is not the maximum existing number"
    c_forms = {
        "a peer cost row carrying the would-be next id":
            "| C-3 | 2026-08-23 | peer | unlanded, same number |\n",
        "a peer cost row already several numbers ahead":
            "| C-9 | 2026-08-23 | peer | unlanded, further ahead |\n",
    }
    c_planted = {}
    for name, tail in c_forms.items():
        # Visible first, exactly as the D-series forms above: a refusal that
        # failed to fire and a reader that cannot see the id look identical.
        assert parse_ids(tail, c_pattern), name
        c_m = merge(c_head, c_head + tail, c_rows, preserve_worktree_tail=True)
        c_v = check_first_id(parse_ids(c_head, c_pattern),
                             parse_ids(c_m["tail"] or "", c_pattern),
                             parse_ids(c_rows, c_pattern))
        c_refused = (not c_v["ok"]) and c_v["code"] == EXIT_REFUSED_TAIL_ID
        c_preserved = bool(c_m["ok"]) and tail in (c_m["merged"] or "")
        c_planted[name] = bool(c_refused and c_preserved)
        if c_refused:
            notes.append(
                f"    C-series id refusal proved ({name}): exit {c_v['code']}, "
                f"tail ids {c_v['tail_in_series']}, HEAD max {c_v['head_max']}, "
                f"tail max {c_v['tail_max']}, correct next id {c_v['next_id']}; "
                f"tail still preserved verbatim: {c_preserved}")
    # NEGATIVE FORMS: the ledger's own header row and its `|---|` separator both
    # begin with a pipe. Either one parsed as an id would put table furniture
    # into the arithmetic, so both must be rejected.
    c_negative = {
        "the ledger's own header row is parsed as an id":
            bool(parse_ids("| id | date | team | process |\n", c_pattern)),
        "the table separator row is parsed as an id":
            bool(parse_ids("|---|---|---|---|\n", c_pattern)),
    }

    # ================= D549: the fail-open, and its two clauses =============
    # Docket D549, raised by closure, UPHELD by verification at `a0e2e9a2`.
    #
    # WHY THESE LIMBS ARE SHAPED THE WAY THEY ARE. Every limb below is paired
    # with a MUTATION that removes exactly the clause the limb guards, and the
    # mutation is DRIVEN -- the pre-repair code path is a real argument to a
    # real function, not a sentence claiming what would happen. A limb that
    # passes both with and without the repair tests nothing, and the module
    # already holds three controls built that way; these are the fourth, fifth
    # and sixth.
    #
    # Every fixture is a real string put through the real code path -- the same
    # `parse_ids`, `shape_audit` and `check_expectation` that `main()` calls.

    # ---- limb group 1: the LESSONS heading forms (repair 2) ---------------
    L = "docs/LESSONS.md"
    L_NEW = RECORDS[L]
    L_PERIOD_ONLY = r"^## (L-\d+)\."          # the pattern BEFORE repair 2
    L_EMDASH_ONLY = r"^## (L-\d+)\s+\u2014"    # narrowed the other way
    L_OVERWIDE = r"^## (L-\d+)"                # the tempting "tidy"
    f_emdash = "## L-9350 \u2014 an em-dash heading, the now-dominant form\n"
    f_period = "## L-9003. a heading in the original period form\n"
    f_comma = ("## L-43, second corollary. a second block filed under an id "
               "that already exists\n")

    parse_planted = {
        "an em-dash heading parses to its own id": (
            parse_ids(f_emdash, L_NEW) == ["L-9350"]),
        "removing repair 2 blinds the reader to that em-dash heading": (
            parse_ids(f_emdash, L_PERIOD_ONLY) == []),
        "a period heading still parses, unchanged by the repair": (
            parse_ids(f_period, L_NEW) == ["L-9003"]),
        "narrowing to em-dash alone would lose the period form": (
            parse_ids(f_period, L_EMDASH_ONLY) == []),
        "the comma second-block form is NOT read as an id": (
            parse_ids(f_comma, L_NEW) == []),
        "over-widening to a bare id would mint one out of that second block": (
            parse_ids(f_comma, L_OVERWIDE) == ["L-43"]),
    }
    # NEGATIVE: the h3 amendment form. This module's older comment declared it
    # an excluded form; it is not one, because it never matches. Asserting that
    # is what stops a stale comment being carried forward as fact.
    parse_negative = {
        "an h3 CORRECTION heading is parsed as an id": bool(
            parse_ids("### L-63 - CORRECTION, an h3 amendment\n", L_NEW)),
        "an h3 CORRECTION heading even matches the CANDIDATE shape": bool(
            re.compile(CANDIDATE_SHAPES[L], re.M).search(
                "### L-63 - CORRECTION, an h3 amendment")),
    }

    # ---- limb group 2: clause 1b, the candidate shape, ALL FOUR records ----
    # CLAUDE.md rule 14: a lesson is not applied until EVERY call site asserts
    # it. The fail-open is generic, so every registered record gets a fixture
    # that must REFUSE and a fixture that must NOT, in ITS OWN vocabulary --
    # never borrowed from another record, which is `check_record_reconciliation`
    # 's 2026-08-24 defect.
    # `near_miss`: a line that SITS ONE BYTE OUTSIDE an exclusion expression and
    # must therefore STILL REFUSE. Added 2026-09-03 for docket
    # D-20260903T184847. WHY IT IS A SEPARATE KEY FROM `refuse`, AND WHY IT IS
    # THE ARM THAT WAS MISSING: `refuse` proves clause 1b fires AT ALL, and its
    # mutation is `NEVER_A_CANDIDATE` -- the candidate clause removed. Neither
    # touches the EXCLUSION set, so neither can catch an exclusion that is too
    # WIDE. The `excluded` limbs cannot catch it either: they prove an exclusion
    # matches what it should, never that it fails to match what it should not.
    # An over-wide exclusion is silent in both directions, because
    # `KNOWN_EXCLUDED` feeds `shape_audit` ALONE and never `parse_ids` -- so it
    # can only ever turn a refusal into an acceptance, never move an id. That is
    # exactly the permissive direction VERIFICATION_CHARTER §2p.3(e) requires a
    # control for, and until this key existed the NUMERICS exclusions added
    # earlier today carried none: MEASURED 2026-09-03 by deleting each of the
    # three one at a time -- the selftest stayed rc 0 GREEN on all three, while
    # `--dry-run docs/NUMERICS_KNOWLEDGE.md` flipped to rc 7 on all three. The
    # register entry was load-bearing on the real file and wholly unproven by
    # the controls, and this module's own comments at the exclusions asserted
    # planted controls that did not exist.
    d549_forms = {
        L: {
            "refuse": "## L-9999 no separator at all, so no id is parsed\n",
            "excluded": (f_comma,),
            # `AMENDMENT\b` must not reach a longer word; the parallel NUMERICS
            # near-miss is the same trap in that record's vocabulary.
            "near_miss": ("## L-9998 AMENDMENTS to a theory\n",),
            "furniture": (),
        },
        "docs/DOCKET.md": {
            "refuse": "| D9999 the first cell never closes, so no id is parsed\n",
            "excluded": ("| D19-D20 note | a range in one cell is one note |\n",),
            # The range exclusion ends in the literal word `note`; a first cell
            # that merely CONTAINS a hyphen is an ordinary unparseable row.
            "near_miss": ("| D9998-D9999 summary | not the word note |\n",),
            "furniture": ("| # | Item | Where found | What settles it |\n",
                          "|---|------|-------------|-----------------|\n"),
        },
        "docs/NUMERICS_KNOWLEDGE.md": {
            "refuse": "**N-B9999 missing its period, so no id is parsed**\n",
            "excluded": (
                "**N-D = DAFoam-team numerics facts, opened 2026-08-21**\n",
                "## N-AV9 COMPANION - the wedge CENTROID bias.\n",
                # The three added earlier today, now actually driven. Each is
                # the REAL committed line, trimmed, not a paraphrase of it.
                "## N-T9 AMENDMENT 1 — 2026-09-01, heat-transfer. Six "
                "call sites, not four.\n",
                "## N-C6 — DATED ADDENDUM, 2026-09-01: THE SCOPE IS "
                "NARROWED.\n",
                "**N-C9**'s bounding evidence are the neighbours: in all "
                "three the field\n",
                # Added 2026-09-10 with the CORRECTION exclusion: the REAL
                # committed line at :6511, trimmed, not a paraphrase. Its (ii)
                # limb asserts it parses NO id (disjointness) and does not
                # refuse; its (ii-mutation) asserts that dropping the exclusion
                # set makes it refuse again, so the entry is load-bearing.
                "**N-D43 CORRECTION — 2026-09-06 — the \"REACHED on the S1 "
                "CBFS case\" half of N-D43 is WITHDRAWN as UNESTABLISHED.**\n"),
            # Each near-miss is the specimen this record's own exclusion
            # comments already NAME as "must still refuse". They now do so in
            # code rather than in prose.
            "near_miss": (
                # `AMENDMENT\b` must not reach `AMENDMENTS`.
                "## N-Z3 AMENDMENTS to a theory\n",
                # A bare id + em-dash is a GENUINELY LOST new fact, and is what
                # a lazier `id + em-dash` exclusion would have swallowed.
                "## N-Z1 — a title\n",
                # ... and the addendum exclusion is anchored on the word DATED.
                "## N-Z2 — UNDATED ADDENDUM, 2026-09-01: text\n",
                # The bold-citation exclusion is anchored on the bold CLOSING
                # immediately after the number. A bold ENTRY missing its period
                # must still refuse.
                "**N-Z2 a bold entry with no period**\n",
                # DISCIPLINE CONTROL (2026-09-10) for the CORRECTION exclusion:
                # `CORRECTION\b` must not reach a longer word, the same trap the
                # AMENDMENT/AMENDMENTS pair drives. A genuinely lost fact
                # written this way MUST still refuse -- if this limb flips, the
                # exclusion was widened past the convention it was written for.
                "## N-Z4 CORRECTIONS to a theory\n"),
            "furniture": (),
        },
        "docs/COST_CALIBRATION.md": {
            "refuse": "| C-9999 the first cell never closes, so no id parses\n",
            "excluded": ("| ~~**C-9104**~~ **STRUCK - DUPLICATE ID; RE-ISSUED "
                         "AS C-9114**, see that row |\n",
                         # the two exact hand-landed malformed-body ids (see
                         # KNOWN_EXCLUDED): candidates that parse no id, so the
                         # (ii) limbs prove each neither parses nor refuses AND
                         # that dropping the exclusion set makes it refuse again.
                         "| C-20260906T232437.922647Z-w4reanc | 2026-09-06 | dafoam | probe |\n",
                         "| C-20260907T030000.000000Z-vmfl046r5 | 2026-09-07 | ansys | probe |\n",
                         # THIRD exact-excluded id (2026-09-07): a VALID 8-hex body
                         # but 9 (nano) fractional digits, hand-rolled with %N (an
                         # S-119 recurrence bypassing --allocate-id).  Excluded by
                         # EXACT id while TOOL_ID_BODY stays strict at 6 -- the (ii)
                         # limb proves it neither parses nor refuses, and the
                         # (ii-mutation) proves dropping the exclusion set refuses it
                         # again: the poison row clears WITHOUT widening the format.
                         "| C-20260907T195722.461339981Z-b826b62e | 2026-09-07 | dafoam | probe |\n",
                         # FOUR MORE exact-excluded ids (2026-09-09): MNEMONIC
                         # bodies (non-hex / wrong length), the real HEAD lines
                         # trimmed. The (ii) limb proves each neither parses nor
                         # refuses (the fix clears them) and the (ii-mutation)
                         # proves dropping the exclusion set refuses each again --
                         # the register clears WITHOUT widening TOOL_ID_BODY.
                         "| C-20260909T171040.973304Z-t23g2rl3 | 2026-09-09 | heat-transfer | probe |\n",
                         "| C-20260909T183500.000000Z-t23g2rn | 2026-09-09 | heat-transfer | probe |\n",
                         "| C-20260909T193000.000000Z-m1ccomp | 2026-09-09 | closure | probe |\n",
                         "| C-20260909T214553.000000Z-supbe1 | 2026-09-09 | cfd | probe |\n"),
            # The struck exclusion needs the `~~` to OPEN the cell; a row that
            # is merely bold is an ordinary unparseable row.
            "near_miss": ("| **C-9105** annotated in-cell, never struck |\n",
                          # a DIFFERENT malformed-body pseudo-tool-id: an 8-char
                          # NON-hex body, matching the candidate, parsing no id,
                          # and NOT one of the two exact-excluded ids -- so it MUST
                          # still refuse.  This is the arm the reported gap lacked:
                          # without it a "malformed body" bug ships unseen
                          # (selftest rc 0 while the live file blocks at rc 7).
                          "| C-20260102T030405.060708Z-nothexch | 2026-01-02 | x | probe |\n",
                          # DISCIPLINE CONTROL (2026-09-07): a DIFFERENT 9-digit
                          # NANOsecond id -- valid 8-hex body, NOT in KNOWN_EXCLUDED.
                          # It MUST STILL REFUSE, proving the fix is an EXACT-id
                          # exclusion and NOT a widened 6-or-9 pattern: a future
                          # hand-rolled nano id is still caught at clause 1b (exit 7).
                          "| C-20260907T195722.999888777Z-deadbeef | 2026-09-07 | x | probe |\n",
                          # DISCIPLINE CONTROL (2026-09-09): a mnemonic-body id in
                          # the EXACT family of the four just excluded (:489-:492)
                          # but NOT one of them -- `t23g2rxx` is 8-char non-hex.
                          # It MUST STILL REFUSE, proving the four exact-id
                          # exclusions did not blind the guard against future
                          # hand-typed mnemonic ids (still caught at clause 1b).
                          "| C-20260909T171040.973304Z-t23g2rxx | 2026-09-09 | x | probe |\n"),
            "furniture": ("| id | date | team | process |\n",
                          "|---|---|---|---|\n"),
        },
    }
    # The tables are keyed the same or the fixtures are graded under the wrong
    # record's shapes -- the same refusal the module takes at import.
    if set(d549_forms) != set(RECORDS):  # pragma: no cover
        raise SystemExit("REFUSED: the D549 control fixtures and RECORDS "
                         "disagree; every record gets its own fixtures "
                         "(CLAUDE.md rule 14).")
    # EVERY record carries a near-miss, or the arm covers a subset of the
    # records it knows about -- `check_record_reconciliation`'s 2026-08-24
    # defect, and CLAUDE.md rule 14's whole point.
    _nm_missing = sorted(p for p, s in d549_forms.items() if not s["near_miss"])
    if _nm_missing:  # pragma: no cover
        raise SystemExit(
            f"REFUSED: these records have no D549 near-miss fixture, so their "
            f"exclusion set is unproven in the PERMISSIVE direction: "
            f"{_nm_missing}")

    shape_planted, shape_negative = {}, {}
    for path, spec in sorted(d549_forms.items()):
        tag = path.rsplit("/", 1)[-1]
        # (i) an unparseable candidate line REFUSES ...
        hit = shape_audit(spec["refuse"], path, "fixture")
        shape_planted[f"{tag}: a candidate line with no parseable id refuses"] \
            = (len(hit) == 1 and hit[0]["line_no"] == 1)
        # ... and (i-mutation) with clause 1b REMOVED -- the candidate never
        # matching, which is this module before the repair -- it does not.
        shape_planted[f"{tag}: removing the candidate clause lets it through"] \
            = (shape_audit(spec["refuse"], path, "fixture",
                           candidate=NEVER_A_CANDIDATE) == [])
        # (ii) a KNOWN-EXCLUDED line must NOT refuse and must yield no id ...
        for k, form in enumerate(spec["excluded"], 1):
            shape_planted[f"{tag}: known-excluded form {k} neither parses "
                          f"nor refuses"] = (
                parse_ids(form, RECORDS[path]) == []
                and shape_audit(form, path, "fixture") == [])
            # ... and (ii-mutation) with the exclusion set REMOVED it DOES
            # refuse. This is the limb that stops clause 1b over-reaching: for
            # LESSONS the excluded form is `## L-43, second corollary.`, a
            # legitimate second block that a naive candidate refusal would
            # start rejecting.
            shape_planted[f"{tag}: dropping the exclusion set makes form {k} "
                          f"refuse"] = (
                len(shape_audit(form, path, "fixture",
                                apply_excluded=False)) == 1)
        # (ii-b) A NEAR-MISS must STILL REFUSE. This is the arm that catches an
        # exclusion widened past the convention it was written for, and it is
        # scored BOTH ways on purpose: the positive limb says the refusal is
        # still there, and the negative limb -- "the exclusion set swallows it"
        # -- must be FALSE, so a future edit that quietly broadens an expression
        # is caught by a limb whose failure text names the swallowing directly.
        for k, form in enumerate(spec["near_miss"], 1):
            hit = shape_audit(form, path, "fixture")
            shape_planted[f"{tag}: near-miss {k} still refuses, so the "
                          f"exclusion set did not over-reach"] = (
                len(hit) == 1 and parse_ids(form, RECORDS[path]) == [])
            shape_negative[f"{tag}: near-miss {k} is SWALLOWED by the "
                           f"exclusion set"] = (hit == [])
        # (iii) table furniture -- the header row and the `|---|` separator --
        # yields no id AND does not refuse; the mutation is a candidate
        # loosened to a bare `^\|`, which turns every table into a refusal.
        for k, form in enumerate(spec["furniture"], 1):
            shape_planted[f"{tag}: table furniture row {k} parses no id and "
                          f"stands"] = (
                parse_ids(form, RECORDS[path]) == []
                and shape_audit(form, path, "fixture") == [])
            shape_planted[f"{tag}: a candidate loosened to a bare pipe would "
                          f"refuse furniture {k}"] = (
                len(shape_audit(form, path, "fixture",
                                candidate=r"^\|")) == 1)
            # NEGATIVE, scored separately: furniture must not even be a
            # candidate. The id pattern's own planted negatives already assert
            # it parses no id; this asserts the BROADER shape does not reach it.
            shape_negative[f"{tag}: table furniture row {k} matches the "
                           f"candidate shape"] = bool(
                re.compile(CANDIDATE_SHAPES[path], re.M).search(form))

    # ---- COST_CALIBRATION tool-id repair, 2026-09-09: the two named controls
    # this fix stands on, driven EXPLICITLY (not only through the fixture loop).
    # (i) POSITIVE, THE PROPERTY THAT WAS ASSUMED BUT UNPROVEN FOR THIS RECORD:
    # a WELL-FORMED tool-allocated id (8-hex body, 6-digit microseconds) in
    # COST_CALIBRATION parses NO legacy id yet is NOT an offender -- it is
    # cleared by tool_id_pattern with NO KNOWN_EXCLUDED entry. This is exactly
    # WHY the four hand-typed rows could not be "recognised" instead of excluded:
    # the machinery already clears every well-formed id, so a row it does not
    # clear is malformed by construction and belongs in KNOWN_EXCLUDED, never in
    # a widened TOOL_ID_BODY.
    _cc = "docs/COST_CALIBRATION.md"
    _wf = "| C-20260909T171040.973304Z-0123abcd | 2026-09-09 | probe | probe |\n"
    shape_planted["COST_CALIBRATION.md: a well-formed tool-allocated id parses "
                  "no legacy id yet does NOT refuse (cleared by tool_id_pattern, "
                  "no exclusion)"] = (
        parse_ids(_wf, RECORDS[_cc]) == []
        and shape_audit(_wf, _cc, "fixture") == [])
    # (i-mutation) with tool-id RECOGNITION removed (apply_tool_ids=False, the
    # state before the timestamp machinery existed) the SAME well-formed id
    # REFUSES -- so the limb above is load-bearing, not vacuously true.
    shape_planted["COST_CALIBRATION.md: without tool-id recognition the "
                  "well-formed id refuses (proves the clear is real)"] = (
        len(shape_audit(_wf, _cc, "fixture", apply_tool_ids=False)) == 1)
    # (ii) NEGATIVE, THE GUARD-NOT-BLINDED PROOF: a genuinely malformed C-id --
    # hand-typed mnemonic body in the family of the four just excluded, but NOT
    # one of them -- STILL REFUSES (parses no id, one offender). If the exact-id
    # exclusions had been widened into a "malformed body" pattern this would
    # PASS, and this limb would flip. It does not.
    _bad = "| C-20260909T171040.973304Z-t23g2rXX | 2026-09-09 | probe | probe |\n"
    shape_planted["COST_CALIBRATION.md: a non-excluded malformed mnemonic C-id "
                  "still refuses (exact-id exclusions did not blind clause 1b)"] \
        = (parse_ids(_bad, RECORDS[_cc]) == []
           and len(shape_audit(_bad, _cc, "fixture")) == 1)

    # ---- limb group 3: clause 1a, and it stands on NO regex ---------------
    # The reported hole, exactly: `--expect-first-id` passed, zero ids parsed,
    # rc 0, rows written. Driven here with no record and no pattern in sight, so
    # the proof that the hole is closed does not lean on repair 2 at all.
    ev_none = check_expectation("L-9999", [])
    ev_legacy = check_expectation("L-9999", [], legacy_gate=True)
    ev_match = check_expectation("L-9350", ["L-9350"])
    ev_silent = check_expectation(None, [])
    expect_planted = {
        "an expectation with zero parsed ids is refused": (
            not ev_none["ok"]
            and ev_none["code"] == EXIT_REFUSED_EXPECTATION_UNEVALUABLE),
        "restoring the pre-repair gate lets that same call through at OK": (
            ev_legacy["ok"] and ev_legacy["code"] == EXIT_OK),
        "an expectation that CAN be evaluated is left alone": ev_match["ok"],
        "no expectation and no ids is not turned into a refusal": (
            ev_silent["ok"]),
    }
    # NEGATIVE: clause 1a must not become a blanket "empty ids is an error".
    # The module has always accepted rows carrying no id when the caller made
    # no claim about them, and that behaviour is unchanged.
    expect_negative = {
        "zero parsed ids refuses even when nothing was expected": (
            not ev_silent["ok"]),
    }

    # ---- limb group 4: tool-allocated ids, on the REAL production path -----
    alloc_planted, alloc_negative, alloc_notes = run_allocation_disk_control()
    notes += alloc_notes

    # ---- limb group 5: Sanaa's 2026-09-03 `corrects:` amendment ------------
    # Its POSITIVE half and its REGRESSION half, both driven; see
    # `run_corrects_control` for why those are different kinds of proof.
    corr_planted, corr_negative, corr_notes = run_corrects_control()
    notes += corr_notes

    # ---- limb group 6: the 2026-09-03 ALLOCATION SCOPE ruling --------------
    scope_planted, scope_negative, scope_notes = run_allocation_scope_control()
    notes += scope_notes

    # ---- limb group 7: the reported sizes are BYTES, not characters ---------
    size_planted, size_negative, size_notes = run_size_report_control()
    notes += size_notes

    # ---- limb group 8: THE WORKTREE TAIL IS DISCARDED, NOT SWEPT (2026-09-07) --
    # THE DEFECT, measured and docketed: an ABORTED append leaves its row in the
    # SHARED worktree, and until this repair the NEXT team's append FOLDED that
    # orphan into its own commit -- two cross-team sweeps, most recently the
    # VMFL046-R5 row swept into commit 9bf38155 on 2026-09-07. THE REPAIR sources
    # the base from HEAD's committed blob and DISCARDS the worktree tail, so an
    # aborted append leaves nothing a peer can sweep.
    #
    # RED-then-GREEN ON ONE FIXTURE, so the limb catches a real sweep and not a
    # no-op. GREEN is the PRODUCTION path -- `merge(...)` with the default
    # `preserve_worktree_tail=False`, exactly as main() calls it, and exactly the
    # bytes main() writes at `wt_file.write_text(got["merged"])`. RED drives the
    # RETAINED old preserve path on the SAME inputs and must reproduce the sweep;
    # if it did not, the GREEN "orphan absent" assertions would be vacuous.
    sweep_head = ("| id | date | team | process |\n|---|---|---|---|\n"
                  "| C-1 | 2026-09-07 | a | one |\n"
                  "| C-2 | 2026-09-07 | b | two |\n")
    sweep_orphan = ("| C-3 | 2026-09-07 | ABORTED-PEER | orphan left in the "
                    "shared worktree by an aborted append |\n")
    sweep_worktree = sweep_head + sweep_orphan   # HEAD + an orphan NOT in HEAD
    sweep_rows = "| C-4 | 2026-09-07 | mine | my new row |\n"
    # PLANT THE ZERO on the reader: the orphan MUST genuinely be in the worktree
    # fixture, or "the orphan did not appear in the output" is indistinguishable
    # from a fixture that never carried a sweepable orphan (CLAUDE.md rule 3).
    assert sweep_orphan in sweep_worktree, "sweep fixture: orphan not planted"
    green = merge(sweep_head, sweep_worktree, sweep_rows)          # production
    red = merge(sweep_head, sweep_worktree, sweep_rows,           # retained old
                preserve_worktree_tail=True)
    sweep_planted = {
        "the fixed append keeps HEAD's own committed rows": (
            green["ok"] and "| C-1 |" in green["merged"]
            and "| C-2 |" in green["merged"]),
        "the fixed append lands this invocation's own new row": (
            green["ok"] and sweep_rows in green["merged"]),
        "the fixed append DISCARDS the aborted peer's orphan row": (
            green["ok"] and sweep_orphan not in green["merged"]),
    }
    # NEGATIVE (must be FALSE): the retained old path must DIFFER -- it must still
    # fold the orphan in. If it ALSO dropped the orphan, the fix changes nothing
    # and the GREEN discard assertion above proves nothing about this repair.
    sweep_negative = {
        "the retained old preserve path ALSO drops the orphan (fix is a no-op)": (
            red["ok"] and sweep_orphan not in red["merged"]),
    }
    if red["ok"] and sweep_orphan in red["merged"]:
        notes.append(
            "    sweep proved BOTH WAYS on one fixture: production path DISCARDS "
            "the aborted peer's orphan (C-3 ABORTED-PEER), the retained old "
            "preserve path FOLDS it in -- reproducing the VMFL046-R5 cross-team "
            "sweep the repair closes")

    ledger = control_kind.ControlLedger(
        claim_class="worktree-only bytes that match no id pattern")
    ledger.plant("merge preserves the invisible tail",
                 vocabulary="append-only record worktree tails",
                 planted=planted,
                 negative={"the overwrite form drops it": overwrite_kept})
    ledger.plant("the id assert judges HEAD AND the preserved tail",
                 vocabulary="peer rows sitting unlanded in a worktree tail",
                 planted=id_planted,
                 negative={"a tail id in a DIFFERENT series blocks the append":
                           cross_blocked})
    ledger.plant("the C-series pattern carries the same tail-id refusal",
                 vocabulary="cost-calibration rows sitting unlanded in a "
                            "worktree tail",
                 planted=c_planted,
                 negative=c_negative)
    ledger.plant("the LESSONS pattern sees every live heading form (D549 r2)",
                 vocabulary="lesson headings as the file actually writes them",
                 planted=parse_planted,
                 negative=parse_negative)
    ledger.plant("a candidate-shaped line with no parseable id REFUSES (D549 1b)",
                 vocabulary="id-bearing shapes in all four records' own "
                            "vocabularies",
                 planted=shape_planted,
                 negative=shape_negative)
    ledger.plant("an expectation that could not be evaluated REFUSES (D549 1a)",
                 vocabulary="--expect-first-id against parsed-id sets",
                 planted=expect_planted,
                 negative=expect_negative)
    ledger.plant("ids are ALLOCATED BY THIS TOOL, and the bytes read back were "
                 "written by main() itself (Sanaa 2026-08-31)",
                 vocabulary="tool-allocated ids in a real record on disk",
                 planted=alloc_planted,
                 negative=alloc_negative)
    ledger.plant("a tool-allocated id is accepted SOLELY inside a structured "
                 "corrects: field on a correction row, and the refusal is "
                 "unchanged everywhere else (Sanaa 2026-09-03)",
                 vocabulary="correction rows and citation fields in all four "
                            "records' own declarations",
                 planted=corr_planted,
                 negative=corr_negative)
    ledger.plant("--allocate-id is REFUSED exactly where the constitution "
                 "prescribes an integer derivation that MISREADS the minted "
                 "form, and still mints everywhere else (2026-09-03)",
                 vocabulary="tool-allocated ids in each record's own heading "
                            "grammar, on disk, plus CLAUDE.md rule 11's own "
                            "shell derivation run verbatim",
                 planted=scope_planted,
                 negative=scope_negative)
    ledger.plant("every size AND every offset this tool reports is a UTF-8 BYTE "
                 "figure -- the unit it is labelled with, and the unit git, cmp "
                 "and the filesystem speak (all 5 sites, CLAUDE.md rule 14)",
                 vocabulary="sizes printed by main() for a record, its worktree, "
                            "its preserved tail and the merged write, plus the "
                            "divergence offset inside the exit-2 refusal reason; "
                            "graded on MULTI-BYTE text, with the divergence "
                            "placed AFTER it, so characters and bytes cannot "
                            "coincide",
                 planted=size_planted,
                 negative=size_negative)
    ledger.plant("the worktree tail is DISCARDED, not swept into the commit -- "
                 "the output is HEAD's blob plus these rows only (2026-09-07)",
                 vocabulary="an aborted peer's orphan row sitting in the shared "
                            "worktree tail, on the production path main() takes",
                 planted=sweep_planted,
                 negative=sweep_negative)

    failures = [n for n, ok in planted.items() if not ok]
    if overwrite_kept:
        failures.append("the overwrite form did NOT drop the tail")
    failures += [f"tail-id control did not refuse-and-preserve: {n}"
                 for n, ok in id_planted.items() if not ok]
    if cross_blocked:
        failures.append("a tail id in a DIFFERENT series blocked the append")
    failures += [f"C-series tail-id control did not refuse-and-preserve: {n}"
                 for n, ok in c_planted.items() if not ok]
    failures += [f"C-series negative form WAS matched (pattern too loose): {n}"
                 for n, hit in c_negative.items() if hit]
    failures += [f"D549 heading-form limb did not hold: {n}"
                 for n, ok in parse_planted.items() if not ok]
    failures += [f"D549 heading-form negative WAS matched: {n}"
                 for n, hit in parse_negative.items() if hit]
    failures += [f"D549 candidate-shape limb did not hold: {n}"
                 for n, ok in shape_planted.items() if not ok]
    # `shape_negative` now carries TWO kinds of negative, so the old wording --
    # "it matched furniture" -- would MISNAME an over-wide exclusion as a loose
    # candidate and send the next reader to the wrong table. Measured
    # 2026-09-03: widening the COST_CALIBRATION exclusion printed exactly that
    # false diagnosis. The limb NAME already says which kind it is, so the
    # prefix states only what is true of both.
    failures += [f"D549 negative form WAS matched -- a shape reached what it "
                 f"must not: {n}"
                 for n, hit in shape_negative.items() if hit]
    failures += [f"D549 expectation limb did not hold: {n}"
                 for n, ok in expect_planted.items() if not ok]
    failures += [f"D549 expectation negative WAS matched: {n}"
                 for n, hit in expect_negative.items() if hit]
    failures += [f"tool-allocation limb did not hold: {n}"
                 for n, ok in alloc_planted.items() if not ok]
    failures += [f"tool-allocation NEGATIVE WAS matched (the guard is not "
                 f"load-bearing): {n}"
                 for n, hit in alloc_negative.items() if hit]
    failures += [f"corrects: amendment limb did not hold: {n}"
                 for n, ok in corr_planted.items() if not ok]
    failures += [f"corrects: NEGATIVE WAS matched -- the field scoping is NOT "
                 f"load-bearing: {n}"
                 for n, hit in corr_negative.items() if hit]
    failures += [f"allocation-scope limb did not hold: {n}"
                 for n, ok in scope_planted.items() if not ok]
    failures += [f"allocation-scope NEGATIVE WAS matched -- the refusal is "
                 f"wider than the measurement that justifies it: {n}"
                 for n, hit in scope_negative.items() if hit]
    failures += [f"size-report limb did not hold: {n}"
                 for n, ok in size_planted.items() if not ok]
    failures += [f"size-report NEGATIVE WAS matched -- a reported size is a "
                 f"CHARACTER count wearing the label 'bytes': {n}"
                 for n, hit in size_negative.items() if hit]
    failures += [f"sweep-discard limb did not hold: {n}"
                 for n, ok in sweep_planted.items() if not ok]
    failures += [f"sweep-discard NEGATIVE WAS matched -- the retained old path "
                 f"also dropped the orphan, so the RED reference no longer "
                 f"reproduces the sweep and the discard proof is a no-op: {n}"
                 for n, hit in sweep_negative.items() if hit]
    notes.append(
        "    D549 clause 1a proved BOTH WAYS on the same call: repaired -> "
        f"exit {ev_none['code']} (refused); pre-repair gate restored -> exit "
        f"{ev_legacy['code']} (the fail-open, rc 0 and the rows written)")
    notes.append(
        f"    D549 clause 1b proved on all {len(d549_forms)} registered "
        f"records, each in its own vocabulary: "
        f"{len(shape_planted)} planted limbs, "
        f"{len(shape_negative)} negative forms; every refusal limb is paired "
        f"with the mutation that removes its clause and must flip it")

    # Two further refusals, proved rather than asserted in prose.
    edited = merge(head.replace("| D2 | two |", "| D2 | EDITED |"),
                   head, rows)
    if edited["ok"]:
        failures.append("an edit inside the committed bytes was not refused")
    else:
        notes.append("    refusal proved: edit inside committed bytes -> "
                     + edited["reason"].split(",")[0])
    truncated = merge(head, head[:-12], rows)
    if truncated["ok"]:
        failures.append("a truncated worktree was not refused")
    else:
        notes.append("    refusal proved: truncated worktree -> REFUSED")
    ids = parse_ids(head, RECORDS["docs/DOCKET.md"])
    if max_for_series(ids, "D") != 2:
        failures.append("max_for_series is not the maximum existing number")
    else:
        notes.append("    id assertion proved: max existing D = 2, so the only "
                     "acceptable first id is D3")
    return ledger, len(failures), notes + [f"    FAILURE: {f}" for f in failures]


def selftest() -> int:
    ledger, n_fail, notes = run_controls()
    print("=" * 78)
    print("append_record.py -- PLANTED CONTROL SELF-TEST")
    print("=" * 78)
    print(ledger.render(n_fail))
    for line in notes:
        print(line)
    print("-" * 78)
    verdict = "PASS" if n_fail == 0 else "FAIL"
    print(f"VERDICT: {verdict}   ({n_fail} control failure(s))")
    print(f"CANNOT SEE [{CANNOT_SEE_OWNER}]")
    print("CANNOT SEE: whether every OTHER consumer of a record id reads the "
          "tool-allocated form. The two reconcilers do -- both import "
          "`parse_record_ids` from here and their planted controls drive a "
          "tool id through the real production path -- and that coupling landed "
          "in the SAME commit as allocation, because a writer whose reader "
          "cannot see it is a dead lever. `scripts/check_numerics_index.py` is "
          "NAMED as one that does not: it reads the N- SERIES INDEX TABLE with "
          "its own `N-[A-Z]+` expressions, and a tool-allocated NUMERICS entry "
          "carries no series letter, so it is absent from that index. That is a "
          "stated residue, not a discovered one.")
    print("CANNOT SEE: the worktree tail is DISCARDED (2026-09-07), not "
          "preserved, so this module no longer judges whether it was wanted or "
          "abandoned; any commit (this module touches the working tree only); or "
          "a peer landing between your `git show` and your write -- capture HEAD "
          "once and pass the same rev here that you pass to `commit-tree -p`.")
    return EXIT_OK if n_fail == 0 else EXIT_SELFTEST


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted controls and exit")
    ap.add_argument("--path", help="record file, repo-relative")
    ap.add_argument("--rows", help="file holding the rows to append")
    ap.add_argument("--rev", default="HEAD",
                    help="the revision to merge onto; pass the SAME one you "
                         "pass to `commit-tree -p` (default HEAD)")
    ap.add_argument("--repo", default=".", help="repository root")
    ap.add_argument("--expect-first-id",
                    help="assert the first appended id equals this, and that "
                         "it is max+1 for its series over the committed blob "
                         "AND the preserved worktree tail")
    ap.add_argument("--allocate-id", action="store_true",
                    help=f"mint a tool-allocated id for every row carrying "
                         f"{ALLOCATE_PLACEHOLDER!r} (Sanaa 2026-08-31: no more "
                         f"counters). Mutually exclusive with --expect-first-id")
    ap.add_argument("--dry-run", action="store_true",
                    help="report and write nothing")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.path or not args.rows:
        ap.error("--path and --rows are required unless --selftest")

    repo = Path(args.repo).resolve()
    pattern = RECORDS.get(args.path)
    if pattern is None:
        print(f"UNKNOWN: {args.path} is not a registered append-only record. "
              f"Known: {', '.join(sorted(RECORDS))}", file=sys.stderr)
        return EXIT_UNKNOWN

    head_text, why = read_committed(repo, args.rev, args.path)
    if head_text is None:
        print(f"UNKNOWN: {why}", file=sys.stderr)
        return EXIT_UNKNOWN
    wt_file = repo / args.path
    if not wt_file.is_file():
        print(f"UNKNOWN: no such file in the working tree: {wt_file}",
              file=sys.stderr)
        return EXIT_UNKNOWN
    worktree_text = wt_file.read_text()
    rows_text = Path(args.rows).read_text()

    # ---- TOOL-ALLOCATED IDS: preconditions FIRST, before anything is minted,
    # merged or written. The smuggle guard runs whether or not --allocate-id was
    # passed, because "this module is the only producer" is only true if a
    # hand-written id is refused on EVERY path (Sanaa 2026-08-31).
    alloc = check_allocation(rows_text, args.path, allocate=args.allocate_id,
                             expect_first_id=args.expect_first_id)
    if not alloc["ok"]:
        print(f"REFUSED: {alloc['reason']}", file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        return alloc["code"]

    # 2026-09-07: the worktree tail is DISCARDED, not folded into the output, so
    # a minted id only has to be unique against the bytes actually written --
    # HEAD's committed blob. It CANNOT collide with a worktree-only row that this
    # run will not write, so the uniqueness backstop is judged against HEAD alone
    # rather than HEAD + tail.
    allocated: list[str] = []
    if args.allocate_id:
        rows_text, allocated = allocate_into_rows(rows_text, args.path)
        uniq = check_allocated_unique(allocated, head_text)
        if not uniq["ok"]:
            print(f"REFUSED: {uniq['reason']}", file=sys.stderr)
            return uniq["code"]

    head_ids = parse_ids(head_text, pattern)
    head_tool_ids = re.findall(tool_id_pattern(args.path), head_text)
    if not head_ids and not head_tool_ids:
        print(f"UNKNOWN: neither the legacy id pattern nor the tool-allocated "
              f"id form parsed a single id from {args.rev}:{args.path} -- the "
              f"pattern or the file changed shape", file=sys.stderr)
        return EXIT_UNKNOWN
    new_ids = parse_ids(rows_text, pattern)

    # The merge is computed HERE, before the id assert, so the arithmetic can
    # see the very bytes this module is about to write. 2026-09-07: those bytes
    # are HEAD's committed blob plus these rows and NOTHING ELSE -- the worktree
    # tail is DISCARDED, not folded in -- so the tail is NOT an arithmetic input:
    # the maximum below, the shape audit and the uniqueness check all judge the
    # written bytes only. The REFUSAL ORDER is deliberately unchanged -- an id
    # refusal is still reported before a prefix refusal, so exit 3 keeps its
    # precedence over exit 2 exactly as before. The prefix test still runs, so an
    # edit INSIDE HEAD's own bytes still refuses (exit 2) rather than reverting;
    # nothing is written on that path.
    got = merge(head_text, worktree_text, rows_text)
    discarded = got["tail"] if got["ok"] else ""
    tail_ids: list[str] = []

    print("=" * 78)
    print("append_record.py -- MERGE (D369's repair, not the overwrite)")
    print("=" * 78)
    print(f"  record           : {args.path}")
    print(f"  committed side   : {args.rev}:{args.path}  "
          f"({utf8_len(head_text)} bytes, {len(head_ids)} ids)")
    print(f"  worktree side    : {wt_file}  ({utf8_len(worktree_text)} bytes)")
    print(f"  id pattern       : {pattern}")
    print(f"  appending        : {new_ids if new_ids else '(no ids parsed)'}")
    if alloc.get("cited"):
        print(f"  CORRECTS         : {alloc['cited']} -- cited, NOT minted, "
              f"inside a structured {CORRECTS_OPENER}...] field on correction "
              f"row(s) at rows line(s) {alloc['corrects_rows']}. This is the "
              f"SOLE place a tool-allocated id is accepted (Sanaa's PLUMBING "
              f"AMENDMENT, 2026-09-03); everywhere else the refusal is "
              f"unchanged. NOT RESOLVED against any record -- a citation may "
              f"cross records, so this module does not read a second one to "
              f"check it exists (a NAMED residue)")
    if args.allocate_id:
        print(f"  ALLOCATED        : {allocated} -- minted HERE from a clock "
              f"reading and a hash, derived from nothing this record contains, "
              f"so there is no shared maximum to be stale about")
    if got["ok"]:
        if discarded:
            print(f"  DISCARDED tail   : {utf8_len(discarded)} worktree bytes "
                  f"beyond HEAD -- NOT folded in and NOT counted (an aborted peer "
                  f"append leaves nothing this run can sweep; 2026-09-07)")
        else:
            print("  DISCARDED tail   : none -- the worktree equals HEAD's blob")
    else:
        print("  DISCARDED tail   : (not read -- the prefix test failed; this "
              "run refuses at exit 2 below either way)")

    # ---- D549 CLAUSE 1b, over the WRITTEN bytes -----------------------------
    # HEAD's blob and the rows are the bytes being written, so the maximum is
    # taken over them and an unparsed line on either side corrupts the answer.
    # 2026-09-07: the worktree tail is NO LONGER audited here, because it is
    # DISCARDED -- it is not in the output, so a candidate-shaped orphan sitting
    # unlanded in the worktree can no longer refuse a peer's append (exit 7); it
    # is simply dropped. That is the `L-343`-reported-while-`L-398`-exists defect
    # over the written sides, and this is where it becomes a refusal, not a number.
    offenders = (shape_audit(head_text, args.path, f"{args.rev}:{args.path}")
                 + shape_audit(rows_text, args.path, args.rows))
    if offenders:
        print(f"  SHAPE AUDIT      : {len(offenders)} line(s) match the "
              f"candidate shape {CANDIDATE_SHAPES[args.path]!r} but yield no id")
        print("REFUSED: a line matches this record's id-bearing CANDIDATE SHAPE "
              "and the id pattern parses NO id from it. That is a REFUSAL "
              "CONDITION, not an absence (D549, upheld by verification at "
              "a0e2e9a2): the maximum this module asserts against would silently "
              "omit these lines.", file=sys.stderr)
        for off in offenders[:20]:
            print(f"    {off['origin']}:{off['line_no']}: {off['line'][:140]}",
                  file=sys.stderr)
        if len(offenders) > 20:
            print(f"    ... and {len(offenders) - 20} more", file=sys.stderr)
        print("Nothing was written. The fix is one of TWO REGISTER EDITS in "
              "scripts/append_record.py, never an edit to the record: widen "
              "that record's entry in RECORDS if the line carries a real id in "
              "a form the pattern cannot see, or add its form to KNOWN_EXCLUDED "
              "if it deliberately is not an id (a second block under an "
              "existing id is the canonical case). Measure which, on the real "
              "bytes, before choosing.", file=sys.stderr)
        return EXIT_REFUSED_UNPARSEABLE_SHAPE

    # ---- D549 CLAUSE 1a, OUTSIDE the `if new_ids:` gate ---------------------
    # This is the whole reported defect: the comparison below used to sit INSIDE
    # that gate, so zero parsed ids skipped it and the tool wrote at rc 0.
    ev = check_expectation(args.expect_first_id, new_ids)
    if not ev["ok"]:
        print(f"REFUSED: {ev['reason']}", file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        return ev["code"]

    if new_ids:
        # tail_ids is [] since 2026-09-07 (the tail is discarded, not counted),
        # so the effective maximum is HEAD's alone. check_first_id is unchanged.
        v = check_first_id(head_ids, tail_ids, new_ids)
        print(f"  series {v['series']!r}: maximum existing number -- committed "
              f"blob {v['head_max']} (the discarded worktree tail is NOT counted)")
        if not v["ok"]:
            print(f"REFUSED: {v['reason']}", file=sys.stderr)
            return v["code"]
        if args.expect_first_id and args.expect_first_id != new_ids[0]:
            print(f"REFUSED: --expect-first-id {args.expect_first_id!r} but the "
                  f"rows begin {new_ids[0]!r}", file=sys.stderr)
            return EXIT_REFUSED_ID
        print(f"  ID ASSERT ok     : {new_ids[0]} == max+1 over HEAD (the "
              f"discarded tail is not counted)")

    if not got["ok"]:
        print(f"REFUSED: {got['reason']}", file=sys.stderr)
        print("Nothing was written. Inspect the difference -- never revert it "
              "(ESCALATION_CHARTER.md section 3).", file=sys.stderr)
        return EXIT_REFUSED_DISAGREES

    if discarded:
        print(f"  WORKTREE TAIL    : {utf8_len(discarded)} bytes beyond the "
              f"committed blob, DISCARDED -- the output is HEAD's blob plus these "
              f"rows ONLY, so an aborted peer append leaves nothing to sweep "
              f"(2026-09-07)")
        preview = discarded if len(discarded) <= 200 else discarded[:200] + " ..."
        for line in preview.splitlines()[:6]:
            print(f"      | {line}")
    else:
        print("  WORKTREE TAIL    : none -- the worktree equals the committed "
              "blob")

    if args.dry_run:
        print("  --dry-run: nothing written")
    else:
        wt_file.write_text(got["merged"])
        print(f"  WROTE            : {wt_file} ({utf8_len(got['merged'])} bytes)")
    print("-" * 78)
    print("VERDICT: OK")
    print(f"CANNOT SEE [{CANNOT_SEE_OWNER}]")
    print("CANNOT SEE: whether every OTHER consumer of a record id reads the "
          "tool-allocated form. The two reconcilers do -- both import "
          "`parse_record_ids` from here and their planted controls drive a "
          "tool id through the real production path -- and that coupling landed "
          "in the SAME commit as allocation, because a writer whose reader "
          "cannot see it is a dead lever. `scripts/check_numerics_index.py` is "
          "NAMED as one that does not: it reads the N- SERIES INDEX TABLE with "
          "its own `N-[A-Z]+` expressions, and a tool-allocated NUMERICS entry "
          "carries no series letter, so it is absent from that index. That is a "
          "stated residue, not a discovered one.")
    print("CANNOT SEE: the worktree tail is DISCARDED (2026-09-07), so this "
          "module no longer judges whether it was wanted or abandoned -- it is "
          "simply not written; any commit -- the private-index sequence, the CAS "
          "and the post-commit verification -- remains the caller's.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
