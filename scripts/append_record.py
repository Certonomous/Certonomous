#!/usr/bin/env python3
r"""Append rows to an append-only record by MERGE, never by overwrite.

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
                 PLUMBING FREEZE directive, 2026-08-31

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
    "docs/LESSONS.md": (
        r"^##[ \t]*L-\d+[ \t]*,",
    ),
    # Two forms, measured, one line each.
    #  * a SERIES DECLARATION, which names a lane rather than a fact:
    #    `**N-D = DAFoam-team numerics facts, opened 2026-08-21**` at :2271.
    #    It carries no number at all, so it is not a lost id.
    #  * a COMPANION block under an existing id -- `## N-AV9 COMPANION - the
    #    wedge CENTROID bias.` at :4469. This is the LESSONS second-block form
    #    in another record's vocabulary: its parent `## N-AV9.` exists at :3913
    #    (checked), so excluding it drops no number from the arithmetic.
    "docs/NUMERICS_KNOWLEDGE.md": (
        r"^(?:\*\*|## )N-[A-Z]+[ \t]*=",
        r"^(?:\*\*|## )N-[A-Z]+\d+[ \t]+COMPANION\b",
    ),
    # A STRUCK id cell carrying its own annotation inside the cell, so the cell
    # does not close after the id and the pattern cannot reach the `|`.
    # Measured: exactly 1 line, `| ~~**C-104**~~ **STRUCK - DUPLICATE ID;
    # RE-ISSUED AS C-114**, ... |` at :180. A struck cell that DOES close
    # cleanly is parsed by the id pattern as normal and never reaches this
    # check, so this exclusion is as narrow as the measurement allows.
    "docs/COST_CALIBRATION.md": (
        r"^\|[ \t]*~~\**C-\d+\**~~",
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


def check_allocation(rows_text: str, path: str, *, allocate: bool,
                     expect_first_id: str | None = None,
                     apply_smuggle_guard: bool = True) -> dict:
    """The preconditions, BEFORE anything is minted or merged. Pure.

    `apply_smuggle_guard=False` reproduces this module WITHOUT the clause that
    makes it the sole producer of tool-form ids; it exists so a planted control
    can drive that mutation and show the limb flips. Nothing in `main()` passes
    it.
    """
    smuggled = re.findall(ANY_TOOL_ID, rows_text)
    if smuggled and apply_smuggle_guard:
        return {"ok": False, "code": EXIT_REFUSED_ALLOCATION, "reason": (
            f"the rows HAND-WRITE tool-allocated id(s) {sorted(set(smuggled))}. "
            f"This module is the ONLY producer of that form, and that is the "
            f"entire reason a duplicate cannot be reintroduced by an edit: a "
            f"hand-written id is a number somebody chose, which is the {path} "
            f"C-217/L-404 mechanism in new clothes. Write "
            f"{ALLOCATE_PLACEHOLDER!r} and pass --allocate-id instead (Sanaa's "
            f"PLUMBING FREEZE directive, 2026-08-31).")}
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
    return {"ok": True, "code": EXIT_OK, "reason": ""}


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


def merge(head_text: str, worktree_text: str, rows_text: str) -> dict:
    """The merge itself. Pure, so the controls can drive it on fixtures.

    Returns a dict; `ok` False means REFUSE and `merged` is None.
    """
    if not worktree_text.startswith(head_text):
        # Locate the first differing byte so the refusal is actionable.
        limit = min(len(head_text), len(worktree_text))
        at = next((i for i in range(limit)
                   if head_text[i] != worktree_text[i]), limit)
        return {
            "ok": False,
            "reason": (
                "the worktree disagrees with the committed blob inside the "
                f"committed blob's own bytes, first at byte {at} of "
                f"{len(head_text)}"
                + ("; the worktree is SHORTER than the blob, which is a "
                   "truncation, not an append"
                   if len(worktree_text) < len(head_text) else "")),
            "merged": None, "tail": None, "separator_inserted": False,
        }
    tail = worktree_text[len(head_text):]
    separator = bool(tail) and not tail.endswith("\n")
    merged = head_text + tail + ("\n" if separator else "") + rows_text
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

        # A SECOND run, same rows file, same placeholder. This is the collision
        # limb AND the exit-7 limb at once: run 1's tool-id row is now sitting
        # in the PRESERVED WORKTREE TAIL, where `shape_audit` will meet it. If
        # the tool-id clause in `shape_audit` were missing, this run would
        # refuse at exit 7 -- the tool refusing the row it had just allocated.
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


# --------------------------------------------------------------- controls
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
    for name, tail in forms.items():
        wt = head + tail
        got = merge(head, wt, rows)
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
        got_id = merge(head, head + tail, rows)
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
    cross_m = merge(head, head + cross_tail, rows)
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
        c_m = merge(c_head, c_head + tail, c_rows)
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
    d549_forms = {
        L: {
            "refuse": "## L-9999 no separator at all, so no id is parsed\n",
            "excluded": (f_comma,),
            "furniture": (),
        },
        "docs/DOCKET.md": {
            "refuse": "| D9999 the first cell never closes, so no id is parsed\n",
            "excluded": ("| D19-D20 note | a range in one cell is one note |\n",),
            "furniture": ("| # | Item | Where found | What settles it |\n",
                          "|---|------|-------------|-----------------|\n"),
        },
        "docs/NUMERICS_KNOWLEDGE.md": {
            "refuse": "**N-B9999 missing its period, so no id is parsed**\n",
            "excluded": (
                "**N-D = DAFoam-team numerics facts, opened 2026-08-21**\n",
                "## N-AV9 COMPANION - the wedge CENTROID bias.\n"),
            "furniture": (),
        },
        "docs/COST_CALIBRATION.md": {
            "refuse": "| C-9999 the first cell never closes, so no id parses\n",
            "excluded": ("| ~~**C-9104**~~ **STRUCK - DUPLICATE ID; RE-ISSUED "
                         "AS C-9114**, see that row |\n",),
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
    failures += [f"D549 candidate is too loose -- it matched furniture: {n}"
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
    print("CANNOT SEE: whether a preserved tail is wanted or abandoned; any "
          "commit (this module touches the working tree only); or a peer "
          "landing between your `git show` and your write -- capture HEAD once "
          "and pass the same rev here that you pass to `commit-tree -p`.")
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

    # The tail is needed BEFORE allocation, for the non-presence assert, so it
    # is probed with empty rows. `merge` is pure and cheap; the authoritative
    # merge is still computed below, over the rows as they will actually land.
    tail_probe = merge(head_text, worktree_text, "")
    tail_text = tail_probe["tail"] if tail_probe["ok"] else ""

    allocated: list[str] = []
    if args.allocate_id:
        rows_text, allocated = allocate_into_rows(rows_text, args.path)
        uniq = check_allocated_unique(allocated, head_text + tail_text)
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
    # see the very bytes this module is about to write: HEAD's blob plus the
    # preserved tail. The REFUSAL ORDER is deliberately unchanged -- an id
    # refusal is still reported before a prefix refusal, so exit 3 keeps its
    # precedence over exit 2 exactly as it had before this repair. When the
    # prefix test has failed there is no trustworthy tail, so the arithmetic
    # falls back to HEAD alone and the run refuses with 2 below regardless;
    # nothing is written on either path.
    got = merge(head_text, worktree_text, rows_text)
    tail_text = got["tail"] if got["ok"] else ""
    tail_ids = parse_ids(tail_text, pattern)

    print("=" * 78)
    print("append_record.py -- MERGE (D369's repair, not the overwrite)")
    print("=" * 78)
    print(f"  record           : {args.path}")
    print(f"  committed side   : {args.rev}:{args.path}  "
          f"({len(head_text)} bytes, {len(head_ids)} ids)")
    print(f"  worktree side    : {wt_file}  ({len(worktree_text)} bytes)")
    print(f"  id pattern       : {pattern}")
    print(f"  appending        : {new_ids if new_ids else '(no ids parsed)'}")
    if args.allocate_id:
        print(f"  ALLOCATED        : {allocated} -- minted HERE from a clock "
              f"reading and a hash, derived from nothing this record contains, "
              f"so there is no shared maximum to be stale about")
    if got["ok"]:
        print(f"  tail ids         : "
              f"{tail_ids if tail_ids else '(none in the preserved tail)'}")
    else:
        print("  tail ids         : (not read -- the prefix test failed, so "
              "there is no trustworthy tail; the id report below is HEAD-only "
              "and this run refuses either way)")

    # ---- D549 CLAUSE 1b, over ALL THREE SIDES -------------------------------
    # HEAD's blob and the preserved tail are ARITHMETIC INPUTS -- the maximum is
    # taken over them -- so an unparsed line on either side corrupts the answer
    # exactly as one in the rows does. That is the `L-343`-reported-while-`L-398`
    # -exists defect, and this is where it becomes a refusal instead of a number.
    offenders = (shape_audit(head_text, args.path, f"{args.rev}:{args.path}")
                 + shape_audit(tail_text, args.path, "the preserved worktree tail")
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
        v = check_first_id(head_ids, tail_ids, new_ids)
        print(f"  series {v['series']!r}: maximum existing number -- committed "
              f"blob {v['head_max']}, preserved worktree tail {v['tail_max']}, "
              f"EFFECTIVE {v['effective_max']}")
        if not v["ok"]:
            print(f"REFUSED: {v['reason']}", file=sys.stderr)
            return v["code"]
        if args.expect_first_id and args.expect_first_id != new_ids[0]:
            print(f"REFUSED: --expect-first-id {args.expect_first_id!r} but the "
                  f"rows begin {new_ids[0]!r}", file=sys.stderr)
            return EXIT_REFUSED_ID
        print(f"  ID ASSERT ok     : {new_ids[0]} == max+1 over HEAD AND the "
              f"preserved tail")

    if not got["ok"]:
        print(f"REFUSED: {got['reason']}", file=sys.stderr)
        print("Nothing was written. Inspect the difference -- never revert it "
              "(ESCALATION_CHARTER.md section 3).", file=sys.stderr)
        return EXIT_REFUSED_DISAGREES

    tail = got["tail"]
    if tail:
        print(f"  WORKTREE TAIL    : {len(tail)} bytes beyond the committed "
              f"blob, PRESERVED ahead of the appended rows")
        preview = tail if len(tail) <= 200 else tail[:200] + " ..."
        for line in preview.splitlines()[:6]:
            print(f"      | {line}")
        if got["separator_inserted"]:
            print("  NOTE             : the tail did not end in a newline (a "
                  "partial line -- somebody is mid-edit); a separator was "
                  "inserted and is reported here rather than fixed silently")
    else:
        print("  WORKTREE TAIL    : none -- the worktree equals the committed "
              "blob, so merge and overwrite coincide on this run")

    if args.dry_run:
        print("  --dry-run: nothing written")
    else:
        wt_file.write_text(got["merged"])
        print(f"  WROTE            : {wt_file} ({len(got['merged'])} bytes)")
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
    print("CANNOT SEE: whether a preserved tail is wanted or abandoned; any "
          "commit -- the private-index sequence, the CAS and the post-commit "
          "verification remain the caller's.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
