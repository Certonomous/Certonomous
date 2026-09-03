#!/usr/bin/env python3
"""grader_freeze_gate.py -- STEP (1) of Sanaa's freeze-enforcement wiring order
(SANAA-DIRECT 2026-09-03 ~17:30Z, item 6, verbatim in
etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md:42-44):

    "(1) the queue daemon refuses to grade any run whose comparator's sha does not
     match its frozen registration -- enforcement at the choke point first,
     primitive is fine"

⚠⚠ THIS FILE IS A RECORDER AND NOT A REFUSER, AND IT USED TO BE A REFUSER.
SANAA-DIRECT 2026-09-03 ~21:00Z (etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md),
verbatim: "A pre-registration mismatch never prevents a launch. It's recorded as a
prediction, the run launches under the monitor, and the outcome is compared to the
prediction on the certificate.  Pre-registration predicts; the monitor watches; the
grader judges afterward."  On this exact category -- her list's "Freeze or procedural
state -- registration not frozen, pin missing, lesson not filed" -- she is explicit:
"record and launch.  A missing pin or unfiled lesson is bookkeeping and can be completed
while the solve runs."  NOTHING HERE STOPS A LAUNCH ANY MORE; `refusals()` returns the
empty list unconditionally, on its first statement, with no branch above it.

WHAT THIS FILE IS.  The primitive that answers ONE question about ONE queue entry:
does the comparator this entry names still hash to what its frozen registration
pinned?  It reads; it never moves, writes, launches, refuses or grades anything.
Two callers use it and NEITHER can refuse:

  * queue_entry_check.CHECKS["GRADER-FREEZE"] -- RECLASSIFIED TO REPORTING under
    Sanaa's ~20:00Z reform ("reporting checks run, log, and attach to the certificate;
    they never block a solve from starting").  It is still mounted in the live validator
    so the classification is visible AT THE MOUNT POINT rather than being an absence a
    reader has to notice, and it contributes no refusal.
    CITED BY SYMBOL, NOT BY LINE, DELIBERATELY.  Every by-line citation of
    queue_runner.py in this repository that was checked on 2026-09-03 was STALE --
    four records cite `queue_runner.py:223` for list_entries(), which lives at :440,
    an error of 217 lines.  A citation that rots silently is worse than none.
  * queue_runner.launch() -- THE RECORD, AND NOW THE WHOLE POINT.  Stamps the harvestable
    prediction on the launched record under gfg.GRADING_FREEZE_STAMP.

WHERE THE READING SITS, AND WHY IT IS NOT A DEAD LIMB.  Measured 2026-09-03, not
assumed: scripts/queue_runner.py has NO grading step.  main() loops on tick(); tick()
runs cap_watch() (which reports, never grades) and launch().  Of the 306 queue entries
on disk carrying a launch_cmd, exactly TWO name a grader (ansys VMFL033-R2 and
VMFL076-R2); the other 304 launch a solver and grading happens afterwards.

So the reading attaches at the launch -- the one place in this daemon where every run
passes through and a record can be written against it.  Under the old design that was
the refusal point; under Sanaa's rule it is the PREDICTION point, and the prediction is
worth more than the refusal was, because it accumulates.  What it does NOT cover is
stated plainly below, because a claim wider than its mechanism is the failure
this lab keeps paying for.

THE PIN IS DERIVED, NEVER DECLARED.  The entry names only a PATH.  The pinned sha is
read from the entry's own `prereg_commit` -- `git rev-parse <prereg_commit>:<path>`.
A `grader_sha` field stated BY the entry would be self-certifying: whoever drifted the
comparator would write the drifted sha beside it and the gate would pass.  The freeze
commit is already validated to exist (COMMIT-EXISTS) and to hold the pre-registration
(PREREG-AT-COMMIT), so it is the one thing in the row that the row's author cannot
retrofit.  The disk side is hashed in pure Python (git's blob rule, sha1 over
`blob <len>\\0<bytes>`), so this instrument needs no git subcommand beyond the
read-only `rev-parse` and `cat-file` that queue_entry_check already allowlists.

AND THE CHOICE OF FILE IS DERIVED TOO, SINCE 2026-09-03 (VERIFICATION_CHARTER §2s.6).
The paragraph above was true about the SHA and silent about the SCOPE, and that gap was
the whole of the remaining hole: control A9 proves the drifter cannot write the pinned
sha, but until `registration_declaration()` existed the drifter could still pick WHICH
FILE got pinned -- drift comparator X, enqueue a row naming comparator Y, or naming
nothing at all.  The pin was honest about a file its adversary chose.  §2s.6's
precedence now governs: THE FROZEN REGISTRATION FIRST, the entry second, and REFUSE if
both exist and disagree -- never choose.  See `registration_declaration()` for the
honest note on where this is an adaptation of §2s.6 rather than a transcription of it.

INSTRUMENT STATES ARE NOT GATE VERDICTS.  The words below -- PINNED, MISMATCH,
ABSENT-AT-FREEZE, ABSENT-ON-DISK, UNPINNED, UNREGISTERED, MALFORMED -- describe this
instrument's reading of a queue row.  They are deliberately OUTSIDE CLAUDE.md rule 1's
fixed gate vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING), which grades physics results and is not this file's to spend.  Nothing here
attaches a verdict to any run.

EVERY STATE IS RECORDED AND EVERY STATE LAUNCHES.  There is no longer a "tolerant
default" set against a strict one -- UNPINNED, MISMATCH and everything between are read,
written down, and launched.  What was once the tolerance is now the rule, and the reading
is made COUNTABLE in three places, none of them prose:
    1. the harvestable prediction stamped on every launched record under
       GRADING_FREEZE_STAMP (queue_runner.launch);
    2. a `GRADER-FREEZE <case>: <state>` line in verification/queue/runner.log;
    3. `--pin-reading <queue root>`, which walks the queue and prints the per-state
       breakdown with the commit it was walked at.

THE SUNSET QUESTION IS DISSOLVED, NOT ANSWERED, AND THAT ITEM COMES OFF SANAA'S DESK.
VERIFICATION_CHARTER §2s.2 required the proceed-and-count outcome to "carry a sunset or
it is permanent" -- at the sunset, UNPINNED would become a refusal -- and the date was
referred to Sanaa as an open item.  HER ~21:00Z RULING REMOVES THE THING THE SUNSET WOULD
HAVE ARRIVED AT: nothing refuses at launch, so there is no stricter state to sunset into
and no date to set.  `--strict` was the mechanism and IS REMOVED rather than left dormant,
because a flag that no longer means what its name says is worse than no flag.  The §2s.2
clause is not violated by this; it is superseded on its own subject by a later and higher
ruling, and the referral is WITHDRAWN rather than left open on her desk.

THIS FILE EMITS NO §2s.4 COVERAGE FIGURE, DELIBERATELY.  §2s.4's coverage is
judged / total over the GRADER population that check_comparator_freeze walks (40 of
189 at its measurement).  `--pin-reading` counts QUEUE ROWS -- a different object over
a different population, not convertible into that one and not a check on it.  The two
must never be quoted as though they were the same number.  §2s.9.1 also rules that any
such figure is meaningless without the commit it was walked at, so every reading this
file prints carries its HEAD sha; and a stop condition written as a bare count -- the
"145/145" an earlier draft of this docstring cited -- names a target that RECEDES as
the lab works, and is not used here.

THE FIELD NAME IS RULED: `grading_freeze` (chief, 2026-09-03), chosen to match the
runner's existing `_grading_freeze` stamp key so no second vocabulary enters the schema.
`grading_paths` -- this lane's earlier proposal -- REMAINS A TOLERATED ALIAS and must
stay one: a live row is written against it (T25R6a, the only PINNED row on disk), and
dropping the spelling would silently return it to UNPINNED.  Sanaa's 2026-09-03 ~20:00Z
reform makes the pin backfill FORWARD-ONLY, so old spellings are read, never rewritten.

⚠ AND THE RULED NAME CREATES A FAIL-OPEN SHAPE, WHICH IS WHY field_pairing_check()
EXISTS.  The INPUT field `grading_freeze` and the OUTPUT stamp `_grading_freeze` now
differ by ONE LEADING UNDERSCORE.  A typo in either direction reads as an absent field
-> UNPINNED -> A PREDICTION SILENTLY NOT MADE.  Under the old refusing design the typo
would have opened a hole in a gate; under the recording design it does something quieter
and, for a calibration dataset, just as bad -- IT DROPS ROWS OUT OF THE DATASET WITHOUT
ANY ROW SAYING SO, and a dataset with silent holes is the planted-zero failure wearing a
different coat.  So the stamp is DERIVED from the field rather than typed twice,
queue_runner writes it through that constant instead of a string literal, and the pairing
is CHECKED AT IMPORT and refuses.  A guard that only works when nobody makes the mistake
it guards against is not a guard.

CLASSIFICATION UNDER SANAA'S 2026-09-03 ~20:00Z REFORM: **REPORTING**, and after her
~21:00Z launch ruling that classification is not a judgement call -- reporting checks
"run, log, and attach to the certificate; they never block a solve from starting", which
is exactly and only what this file now does.
THE GATING REASON STILL EXISTS AND STILL BITES, ONE STEP DOWNSTREAM.  *"Without a
comparator present at freeze and present on disk, the verdict on that run cannot be
trusted, because nothing computed it"* -- and for MISMATCH: without a comparator whose
bytes are the bytes its registration froze, the verdict cannot be trusted, because the
script that produced it may have been chosen after the answer was known (rule 2).  Those
sentences are TRUE and they GATE AT GRADING, in the frozen comparator, which refuses
(exit 2) rather than degrade under rule 4.  Sanaa: "The rule changes WHEN the gate
applies -- after the fact, on evidence -- not WHETHER it applies."

⚠ COVERAGE REPORTING IS SUSPENDED AND THIS FILE PUBLISHES NO RATIO.  Her reform: *"no
instrument is built to measure another instrument's reach unless the first instrument has
already changed a verdict at least once"*, and *"coverage ratios forward-only,
unreported."*  THIS ENFORCER HAS CHANGED ZERO VERDICTS -- it fires at launch, and every
row it has met was already launched.  Verification has suspended their own limb-(2)
coverage report on the same ground.  `--pin-reading` therefore prints the per-state
census as an INTERNAL ENGINEERING FIGURE and DELIBERATELY PRINTS NO FRACTION; the
counts stay available in the returned dict for a caller that needs them and are not
published, quoted upward, or logged as a ratio.

USAGE
    python3 scripts/grader_freeze_gate.py <entry.json> [<entry.json> ...]
    python3 scripts/grader_freeze_gate.py --pin-reading verification/queue
    python3 scripts/grader_freeze_gate.py --selftest
Exit 0 = nothing refused; 2 = at least one entry REFUSED (or the instrument refused
itself).  Rule 4's precedent: refuse, never degrade.

NO `assert` ANYWHERE (L-332): `python3 -O` deletes them, and a gate that vanishes
under a flag is not a gate.  ast_self_check() below enforces that on this file.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

EXIT_REFUSE = 2

# THE RULED SCHEMA FIELD (chief, 2026-09-03). THE SINGLE PLACE THE NAME IS WRITTEN.
# A list, because a rung can be graded by more than one comparator, and because a
# scalar that later needs to be a list is a migration nobody performs.
GRADING_FREEZE_FIELD = "grading_freeze"
# THE OUTPUT STAMP IS DERIVED, NEVER TYPED A SECOND TIME. queue_runner.launch() writes
# meta[gfg.GRADING_FREEZE_STAMP], not a string literal, so there is exactly ONE spelling
# of this name in the codebase and the underscore-typo has nowhere to live. The import
# guard below still checks the pairing, because a derivation can itself be edited.
GRADING_FREEZE_STAMP = "_" + GRADING_FREEZE_FIELD
# Tolerated spellings, read in order, first present wins. `grading_paths` is NOT dead
# history: the only PINNED row on disk is written against it, and Sanaa's 2026-09-03
# reform makes the pin backfill FORWARD-ONLY -- old rows are read, never rewritten.
GRADING_PATHS_ALIASES = (GRADING_FREEZE_FIELD, "grading_paths", "grader_paths",
                         "comparator_paths")
# Kept as the old symbol name so no caller or record that referenced it is stranded.
GRADING_PATHS_FIELD = GRADING_FREEZE_FIELD


def field_pairing_check() -> list[str]:
    """THE INPUT FIELD AND THE OUTPUT STAMP MUST BE THE UNDERSCORE PAIR. Refuses at import.

    THE HAZARD, STATED BEFORE THE MECHANISM. `grading_freeze` (what an entry declares)
    and `_grading_freeze` (what the launched record is stamped with) differ by one
    character. A typo in either -- `grading_freezes`, `_grading_freez`, a dropped
    underscore -- makes the field read as ABSENT. An absent field is UNPINNED, UNPINNED
    is the tolerant default, and the tolerant default LAUNCHES. The failure is silent,
    logs nothing unusual, and is indistinguishable from the state 290 rows are in today.

    This returns the reasons it is unhappy rather than raising, so a control can plant
    the typo in each direction and watch it fire (a guard never seen to fail is not known
    to be load-bearing, L-314). The module-level caller below turns a non-empty list into
    a refusal at import time.

    NO `assert` (L-332): `python3 -O` deletes asserts, and this guard must survive it.
    """
    bad: list[str] = []
    if GRADING_FREEZE_STAMP != "_" + GRADING_FREEZE_FIELD:
        bad.append(
            f"FIELD-PAIRING: the entry field {GRADING_FREEZE_FIELD!r} and the record "
            f"stamp {GRADING_FREEZE_STAMP!r} are not the underscore pair. A row written "
            f"against either spelling would read as declaring NOTHING, and an entry that "
            f"declares nothing LAUNCHES under the tolerant default.")
    if GRADING_FREEZE_FIELD not in GRADING_PATHS_ALIASES:
        bad.append(
            f"FIELD-PAIRING: the ruled field {GRADING_FREEZE_FIELD!r} is absent from the "
            f"alias tuple actually read by declared_paths(), so a correctly written entry "
            f"would be invisible to the reader and would launch unpinned.")
    # THE OUTPUT SIDE, CHECKED WHERE IT IS ACTUALLY WRITTEN. The pairing above is a
    # statement about two constants in this file; the stamp that reaches disk is written
    # by queue_runner, and a literal reintroduced there would defeat both constants
    # without touching either. This limb is skipped only if the file is absent (this
    # instrument is legitimately runnable standalone), and the skip is reported, not
    # silent -- "could not check" and "checked clean" must never be the same reading.
    qr_src = Path(__file__).resolve().parent / "queue_runner.py"
    if qr_src.is_file():
        try:
            text = qr_src.read_text()
        except OSError as exc:
            bad.append(f"FIELD-PAIRING: queue_runner.py exists and could not be read "
                       f"({exc}); the stamp it writes could not be checked, which is not "
                       f"the same as checking it clean.")
            text = ""
        if text:
            literals = set(re.findall(r"""["'](_?grading_freeze\w*)["']""", text))
            if literals:
                bad.append(
                    f"FIELD-PAIRING: queue_runner.py writes the stamp as STRING "
                    f"LITERAL(S) {sorted(literals)} instead of gfg.GRADING_FREEZE_STAMP. "
                    f"A second spelling of this name is exactly the typo surface this "
                    f"guard exists to remove.")
            if "GRADING_FREEZE_STAMP" not in text:
                bad.append(
                    "FIELD-PAIRING: queue_runner.py references GRADING_FREEZE_STAMP "
                    "nowhere, so nothing stamps the launched record under the ruled name "
                    "and every launch would silently record no freeze reading at all.")
    return bad



FULL_SHA_CHARS = set("0123456789abcdef")

# Sanaa's 2026-08-31 ruling (9154c8ef), already honoured by queue_entry_check: an
# UNREGISTERED feasibility/physics rung is queue-legal with a tag in place of a freeze
# sha, and ITS OUTPUTS ARE NEVER GRADEABLE. Such a row has no freeze to pin against and
# is EXEMPT here -- exempt is not covered, and --pin-reading counts it in its own column.
UNREGISTERED_PREREG_TAGS = frozenset({"FEASIBILITY", "PHYSICS"})

# The states that ARE a pre-registration mismatch. THEY REFUSE NOTHING. The name says
# `RECORDED` because that is now the whole of their effect: each is written onto the
# launched record as a prediction that grading will refuse, and the run launches.
#
# ⚠⚠ THIS SET REFUSED LAUNCHES UNTIL 2026-09-03 ~21:00Z AND THE HISTORY IS RECORDED
# BECAUSE IT WENT THREE WAYS IN ONE HOUR -- a reader who sees only the current state
# would reasonably assume nobody had thought about it.
#   1. cfd built ABSENT-AT-FREEZE and ABSENT-ON-DISK as refusals, noticed that §2s.2
#      assigns unconditional refusal to MISMATCH alone, and REFERRED the two rather than
#      conforming quietly or moving a gate on its own reading.
#   2. Verification UPHELD the stricter reading: §2s.2's third outcome was written for
#      rows where the FREEZE EVIDENCE is absent, while these are rows where the ARTIFACT
#      is absent -- a different and worse condition. A row declaring a grading path not
#      present at its own freeze commit HAS REGISTERED NOTHING; a comparator absent on
#      disk CANNOT GRADE AT ALL.
#   3. SANAA INVERTED THE CONSEQUENCE, and hers governs: record and launch, judged after.
#      "A pre-registration mismatch never prevents a launch."
# VERIFICATION'S DISTINCTION IS KEPT because it is still TRUE and still worth recording --
# artifact-absent and evidence-absent are different findings and the record names which.
# WHAT IS DROPPED IS THE CONSEQUENCE, NOT THE REASONING. The gating reason it was framed
# with -- "without a comparator present at freeze and present on disk, the verdict on
# that run cannot be trusted, because nothing computed it" -- REMAINS TRUE AND STILL
# GATES; it now gates AT GRADING, where the frozen comparator refuses rather than
# degrades (rule 4), instead of at launch. Sanaa: "The rule changes WHEN the gate
# applies -- after the fact, on evidence -- not WHETHER it applies."
#
# THE LAST TWO ARE §2s.6's, ADDED 2026-09-03 WITH D8, AND NEITHER OCCURS ON ANY ROW ON
# DISK TODAY -- measured, not assumed: zero registrations in this repository carry a
# GRADING_FREEZE (or legacy GRADING_PATHS) declaration.
RECORDED_MISMATCH_STATES = ("MISMATCH", "ABSENT-AT-FREEZE", "ABSENT-ON-DISK", "MALFORMED",
                            "DECLARATION-CONFLICT", "REGISTRATION-UNREADABLE")

# Every verdict this instrument can return. One tuple so the census tally, the printed
# breakdown and the states themselves cannot drift apart -- a tally keyed on a
# hand-written list is how a new state becomes invisible to the count that exists to
# see it.
ALL_STATES = ("PINNED", "UNPINNED", "UNREGISTERED") + RECORDED_MISMATCH_STATES


class Refusal(Exception):
    """A condition that must stop this instrument under ANY flag."""


# THE FIELD-PAIRING GUARD FIRES AT IMPORT, DELIBERATELY, and it sits here rather than
# beside its function only because `Refusal` must exist before it can be raised.
# queue_entry_check imports this module UNGUARDED so the daemon fails loudly rather than
# validating without the check; this refusal rides that same path. A misspelt field name
# must stop the daemon, not quietly pass its whole queue under the tolerant default.
_PAIRING = field_pairing_check()
if _PAIRING:
    raise Refusal("; ".join(_PAIRING))


def is_full_sha(s) -> bool:
    return isinstance(s, str) and len(s) == 40 and set(s) <= FULL_SHA_CHARS


def blob_sha(data: bytes) -> str:
    """git's own blob hash, computed here rather than shelled out.

    `git hash-object` is NOT in queue_entry_check's enforced read-only allowlist
    (GIT_READ_ONLY = {cat-file, rev-parse, ls-tree}), and widening an allowlist whose
    whole purpose is to keep a write subcommand away from a shared tree would be a
    weakening bought for a convenience. sha1 over `blob <len>\\0<bytes>` is the format.
    """
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\0")
    h.update(data)
    return h.hexdigest()


def _git_rev_parse(repo: Path, spec: str) -> str | None:
    """Read-only. Returns the object sha for `<commit>:<path>`, or None if absent.

    `rev-parse` is on queue_entry_check's GIT_READ_ONLY allowlist, so this instrument
    adds no new git capability to the daemon's process.
    """
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify",
                              "--quiet", spec],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    sha = out.stdout.strip()
    return sha if is_full_sha(sha) else None


def declared_paths(entry: dict) -> tuple[list, str | None]:
    """(the declared grading paths, the field name they came from).

    ([], None) when the row declares none -- the tolerant-default case. A field
    present but not a list of non-empty strings is returned AS FOUND so the caller
    can call it MALFORMED; it is never quietly coerced into an empty list, because
    a malformed declaration reading as "no declaration" is how a gate goes silent.
    """
    for name in GRADING_PATHS_ALIASES:
        if name in entry:
            v = entry[name]
            if isinstance(v, str):
                v = [v]
            return (v if isinstance(v, list) else [v]), name
    return [], None


# ------------------------------------------------- D8 / §2s.6: WHERE THE DECLARATION COMES FROM
# VERIFICATION_CHARTER §2s.6, verbatim: "A declaration is accepted from the frozen
# registration first (it cannot move after first compute), the comparator's own source
# second; if both exist and DISAGREE, REFUSE -- never choose."
#
# HONEST SCOPE NOTE -- THIS IS AN ADAPTATION, NOT A TRANSCRIPTION, AND SAYING SO IS THE
# POINT.  §2s.6 governs the pairing COMPARATOR -> RUN TREE inside check_comparator_freeze,
# and its second-precedence source is the comparator's own source file.  The pairing here
# is QUEUE ROW -> COMPARATOR and the fallback source is the queue entry.  What is
# transcribed EXACTLY is the part that carries the enforcement: the PRECEDENCE (frozen
# registration wins) and the REFUSE-ON-DISAGREEMENT rule (never choose).  What differs is
# which two objects those rules range over.  Authorised as conformance with an
# already-ruled clause by cfd-supervisor, 2026-09-03; it creates no gate and moves none.
#
# THE DECLARATION FORMAT, and why it is this narrow.  A line whose first non-decoration
# token is `GRADING_FREEZE:` -- the ruled vocabulary -- followed by one or more
# repo-relative paths.  The legacy `GRADING_PATHS:` spelling is read too, and BOTH FEED
# THE SAME CONFLICT CHECK, so a registration carrying one of each that disagree is a
# CONFLICT and not a precedence puzzle: §2s.6's "never choose" applies inside one
# document exactly as it does between two.  Leading markdown decoration (`>`, `*`, `_`,
# backtick, `-`) is tolerated because registrations are markdown; anything else on the
# left is not a declaration.
REGISTRATION_DECL_RE = re.compile(
    r"^[\s>*_`+-]*GRADING_(?:FREEZE|PATHS)\s*:\s*(.+?)\s*$", re.MULTILINE)


def _split_decl(text: str) -> list[str]:
    """The paths on one declaration line. Commas or whitespace; markdown stripped."""
    out = []
    for tok in re.split(r"[,\s]+", text.strip()):
        tok = tok.strip().strip("`'\"*_")
        if tok:
            out.append(tok)
    return out


def _git_cat_blob(repo: Path, sha: str) -> bytes | None:
    """Read-only. The blob's bytes, or None if it could not be read.

    `cat-file` is already on queue_entry_check's GIT_READ_ONLY allowlist, so this adds
    no git capability to the daemon's process.
    """
    try:
        out = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", sha],
                             capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def registration_declaration(entry: dict, repo: Path) -> tuple[list, str]:
    """(paths, state) read from the FROZEN REGISTRATION BLOB -- never from the entry.

    state is one of:
      NONE               no registration blob is reachable, or it carries no
                         declaration. A MISSING or unreachable registration is already
                         refused upstream by COMMIT-EXISTS / PREREG-AT-COMMIT and is not
                         double-reported here.
      DECLARED           exactly one declaration (or several that agree); `paths` holds it.
      UNREADABLE         the blob EXISTS and its bytes could not be read.
      CONFLICT-INTERNAL  two declarations in one registration that disagree.

    ⚠ WHY `UNREADABLE` IS A SEPARATE STATE AND NOT FOLDED INTO `NONE`.  This is
    VERIFICATION_CHARTER §2s.9.2's finding applied to this file before it could happen
    here.  There, `check_comparator_freeze` initialises `modified = None`, assigns it
    only when three subprocess calls all succeed, and then writes
    `"MODIFIED_AFTER_COMMIT" if modified else "FROZEN"` -- so a comparison that COULD
    NOT BE PERFORMED reports the reassuring answer, and from the row alone "checked and
    clean" is indistinguishable from "never checked".  Returning `[], "NONE"` on a failed
    `cat-file` would reproduce that exactly: the authority would be unreadable and the
    row would silently fall back to the entry's own word, which is the one source §2s.6
    ranks second.  A guard that cannot read its authority refuses.
    """
    sha = entry.get("prereg_commit")
    ppath = entry.get("prereg_path")
    if not is_full_sha(sha) or not isinstance(ppath, str) or not ppath.strip():
        return [], "NONE"
    rel = _normalise(repo, ppath.strip())
    if rel is None:
        return [], "NONE"                      # SCHEMA owns a malformed prereg_path
    blob = _git_rev_parse(repo, f"{sha}:{rel}")
    if blob is None:
        return [], "NONE"                      # PREREG-AT-COMMIT owns a missing prereg
    raw = _git_cat_blob(repo, blob)
    if raw is None:
        return [], "UNREADABLE"                # the blob EXISTS; see the docstring
    hits = [h for h in REGISTRATION_DECL_RE.findall(raw.decode("utf-8", errors="replace"))]
    decls = [d for d in (_split_decl(h) for h in hits) if d]
    if not decls:
        return [], "NONE"
    first = tuple(sorted(set(decls[0])))
    for d in decls[1:]:
        if tuple(sorted(set(d))) != first:
            return [], "CONFLICT-INTERNAL"
    return decls[0], "DECLARED"


def _same_paths(repo: Path, a: list, b: list) -> bool:
    """Do two declarations name the same set of files? Compared on the NORMALISED
    repo-relative path, so `./x/y.py` and `x/y.py` are one file and not a conflict; a
    path that will not normalise falls back to its literal text rather than to None,
    because two different unnormalisable paths must not compare equal."""
    def key(xs):
        out = set()
        for x in xs:
            n = _normalise(repo, x) if isinstance(x, str) and x.strip() else None
            out.add(n if n is not None else repr(x))
        return out
    return key(a) == key(b)


def _normalise(repo: Path, p: str) -> str | None:
    """Repo-relative POSIX path, or None if it escapes the repo."""
    q = Path(p)
    if q.is_absolute():
        try:
            q = q.resolve().relative_to(Path(repo).resolve())
        except ValueError:
            return None
    s = q.as_posix()
    if s.startswith("../") or s == ".." or not s:
        return None
    return s


def _freeze_reading(entry: dict, repo: Path) -> dict:
    """THE PRIMITIVE'S CORE. A dict reading of one entry. Never raises on entry content.

    Not called directly by production: `grading_freeze_record()` wraps this and adds the
    harvest envelope. Split so the reading logic and the record's schema can each be read
    without the other.
    """
    repo = Path(repo)
    sha = entry.get("prereg_commit")
    case = str(entry.get("case_id", "<no case_id>"))
    paths, field = declared_paths(entry)

    if isinstance(sha, str) and sha in UNREGISTERED_PREREG_TAGS:
        return dict(
            verdict="UNREGISTERED", detail=(
                f"prereg_commit is the {sha!r} tag (Sanaa 2026-08-31, 9154c8ef): this row "
                f"carries NO freeze and its outputs are never gradeable as verdicts, so "
                f"there is nothing for a comparator pin to be checked against. EXEMPT, "
                f"which is not the same as covered."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=False)

    if not is_full_sha(sha):
        # SCHEMA/COMMIT-EXISTS already refuse this shape; do not double-report.
        return dict(verdict="UNPINNED", detail=(
            "prereg_commit is not a 40-hex sha; the freeze checks upstream own this "
            "row and there is no commit to derive a pin from."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=False)

    # ---- §2s.6 PRECEDENCE (D8): the frozen registration outranks the entry ----------
    reg_paths, reg_state = registration_declaration(entry, repo)
    if reg_state == "UNREADABLE":
        return dict(verdict="REGISTRATION-UNREADABLE", detail=(
            f"the frozen registration {entry.get('prereg_path')!r} EXISTS at commit "
            f"{sha[:8]} and its bytes could not be read, so the authority §2s.6 ranks "
            f"FIRST could not be consulted. This is refused rather than silently "
            f"downgraded to the entry's own declaration: 'could not check' and 'nothing "
            f"to check' must never be the same reading (VERIFICATION_CHARTER §2s.9.2)."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=True)
    if reg_state == "CONFLICT-INTERNAL":
        return dict(verdict="DECLARATION-CONFLICT", detail=(
            f"the frozen registration {entry.get('prereg_path')!r} at {sha[:8]} carries "
            f"TWO GRADING_PATHS declarations that disagree. §2s.6: if declarations exist "
            f"and disagree, REFUSE -- never choose. A disagreement about which comparator "
            f"grades a case is precisely the condition in which a silent pick is worst."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=True)
    if reg_state == "DECLARED" and paths and not _same_paths(repo, reg_paths, paths):
        return dict(verdict="DECLARATION-CONFLICT", detail=(
            f"the frozen registration at {sha[:8]} declares {sorted(reg_paths)} and this "
            f"entry's {field!r} declares {sorted(str(p) for p in paths)}. They name "
            f"different comparators. §2s.6: REFUSE -- never choose. The registration is "
            f"the senior source because it cannot move after first compute; an entry that "
            f"contradicts it is the shape a drifted comparator would be hidden behind."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=True)
    source = "ENTRY" if paths else "NONE"
    if reg_state == "DECLARED":
        # The senior source spoke. Whether or not the entry agreed, THIS is what is pinned.
        paths, field = reg_paths, f"the frozen registration ({entry.get('prereg_path')})"
        source = "REGISTRATION"

    if not paths:
        return dict(verdict="UNPINNED", detail=(
            f"entry declares no {GRADING_FREEZE_FIELD!r}: no comparator is named, so the "
            f"sha of the script that will grade case {case} is NOT pinned to freeze "
            f"{sha[:8]}. Nothing is predicted about this run's grading, and that absence "
            f"is recorded rather than read as a pass."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=True,
            source=source)

    rows = []
    worst = "PINNED"
    for raw in paths:
        if not isinstance(raw, str) or not raw.strip():
            rows.append(dict(path=repr(raw), frozen_sha=None, disk_sha=None,
                             state="MALFORMED"))
            worst = "MALFORMED"
            continue
        rel = _normalise(repo, raw)
        if rel is None:
            rows.append(dict(path=raw, frozen_sha=None, disk_sha=None,
                             state="MALFORMED"))
            worst = "MALFORMED"
            continue
        frozen = _git_rev_parse(repo, f"{sha}:{rel}")
        disk_p = repo / rel
        try:
            disk = blob_sha(disk_p.read_bytes()) if disk_p.is_file() else None
        except OSError:
            disk = None
        if frozen is None:
            state = "ABSENT-AT-FREEZE"
        elif disk is None:
            state = "ABSENT-ON-DISK"
        elif disk != frozen:
            state = "MISMATCH"
        else:
            state = "PINNED"
        rows.append(dict(path=rel, frozen_sha=frozen, disk_sha=disk, state=state))
        if state != "PINNED" and worst == "PINNED":
            worst = state

    bad = [r for r in rows if r["state"] in RECORDED_MISMATCH_STATES]
    if not bad:
        return dict(verdict="PINNED", detail=(
            f"{len(rows)} comparator(s) named by {field!r} hash EXACTLY as commit "
            f"{sha[:8]} froze them."),
            field=field, paths=rows, prereg_commit=sha, refusal_eligible=False,
            source=source)
    return dict(verdict=worst, detail=(
        f"{len(bad)} of {len(rows)} comparator(s) named by {field!r} do NOT match "
        f"freeze {sha[:8]}."),
        field=field, paths=rows, prereg_commit=sha, refusal_eligible=True,
        source=source)


# ------------------------------------------------- THE HARVEST ENVELOPE (Sanaa, item 3)
# Her words, 2026-09-03 ~21:00Z: "What you gain: a calibration dataset for every
# pre-registration standard... The standards get corrected by data instead of by
# petition."  A RECORD A HUMAN CAN READ BUT A SCRIPT CANNOT AGGREGATE DOES NOT PRODUCE
# THAT DATASET, so the envelope below is designed to be joined, not merely filed:
# a stable schema tag, the machine-readable prediction, the state that produced it, the
# commit it was walked at, a timestamp, and an `actual` slot the after-the-fact outcome
# is written into.
GRADING_FREEZE_SCHEMA = "grading_freeze/2"

# The testable claim, as an enum a harvester can group by. The dependent variable of the
# calibration dataset: for each row, did grading actually do what this predicted?
PREDICTS = {
    "PINNED": "GRADING_WILL_PROCEED",
    "UNPINNED": "NO_PREDICTION_NOT_PINNED",
    "UNREGISTERED": "NO_PREDICTION_EXEMPT",
}


def grading_freeze_record(entry: dict, repo: Path) -> dict:
    """THE PRIMITIVE. One entry's freeze reading, wrapped as a HARVESTABLE PREDICTION.

    ⚠ THIS IS A PREDICTION, NOT A VERDICT, AND SINCE 2026-09-03 ~21:00Z IT BLOCKS
    NOTHING.  Sanaa, verbatim: "A pre-registration mismatch never prevents a launch. It's
    recorded as a prediction, the run launches under the monitor, and the outcome is
    compared to the prediction on the certificate. Pre-registration predicts; the monitor
    watches; the grader judges afterward."  This record is the "predicts" half.

    KEYS, and they are a contract -- a harvester reads these:
      schema           "grading_freeze/2". Bump when a key's meaning changes, never
                       silently; a dataset whose rows mean different things by date is
                       worse than no dataset.
      kind             "PREDICTION". Never a verdict; carries none of CLAUDE.md rule 1's
                       gate vocabulary, which is the grader's to spend and not this file's.
      verdict          the instrument state: PINNED / UNPINNED / UNREGISTERED /
                       MISMATCH / ABSENT-AT-FREEZE / ABSENT-ON-DISK / MALFORMED /
                       DECLARATION-CONFLICT / REGISTRATION-UNREADABLE.
      predicts         the testable claim as an enum -- GRADING_WILL_PROCEED,
                       GRADING_WILL_REFUSE, NO_PREDICTION_NOT_PINNED,
                       NO_PREDICTION_EXEMPT. THE COLUMN THE CALIBRATION JOINS ON.
      actual           null at launch. THE JOIN SLOT: what grading actually did, written
                       after the fact. `null` means not yet observed and must never be
                       read as agreement.
      case_id          so rows aggregate without parsing filenames.
      paths            one row per declared comparator: path, frozen_sha, disk_sha, state.
      source           REGISTRATION / ENTRY / NONE -- which declaration §2s.6's precedence
                       actually used. A calibration that cannot see this cannot tell a
                       registration-declared pin from an entry-declared one.
      prereg_commit    the freeze the pin was derived from.
      walked_commit    the HEAD this reading was taken at. §2s.9.1: a freeze figure
                       without its walked commit is meaningless, because the population
                       moves under the measurement.
      recorded_utc     when.
      detail, field    prose and the field name the declaration came from.
      refusal_eligible LEGACY, kept because 289 launched records on disk already carry it
                       and a harvester reading them must not break. IT NO LONGER MEANS
                       "this launch may be refused" -- nothing is refused at launch. It
                       now means only "this state is a recorded mismatch". New readers
                       should use `predicts`.
    """
    rec = _freeze_reading(entry, Path(repo))
    v = rec.get("verdict")
    rec["schema"] = GRADING_FREEZE_SCHEMA
    rec["kind"] = "PREDICTION"
    rec["predicts"] = PREDICTS.get(v, "GRADING_WILL_REFUSE")
    rec["actual"] = None
    rec["case_id"] = entry.get("case_id")
    rec.setdefault("source", "NONE")
    rec["walked_commit"] = _git_rev_parse(Path(repo), "HEAD^{commit}")
    rec["recorded_utc"] = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return rec


def refusals(entry: dict, repo: Path, strict: bool = False) -> list[str]:
    """ALWAYS EMPTY. THE SHAPE queue_entry_check.CHECKS expects, and it never refuses.

    ⚠ `strict` IS ACCEPTED AND IGNORED, AND IT IS KEPT DELIBERATELY. IT PAID FOR ITSELF.
    Removing this parameter took the lab's validator DOWN FOR ABOUT TWO MINUTES: while the
    signature change and its call site were half-applied IN THE SHARED WORKING TREE,
    `refusals(..., strict=False)` raised TypeError for EVERY TEAM'S entries and nothing
    could launch through the validator. It self-closed when the second file was saved.
    A PARAMETER IS AN INTERFACE OTHER CODE CALLS; A FLAG IS A USER AFFORDANCE. Deleting
    the `--strict` CLI flag was right and it is gone. Deleting the parameter broke every
    caller in the window between two edits, and on shared queue plumbing that is a
    lab-wide outage, not a cfd inconvenience. The argument does nothing: nothing refuses
    at launch under Sanaa's 2026-09-03 ~21:00Z rule, whatever is passed here.

    ⚠⚠ THIS FUNCTION USED TO REFUSE AND SANAA RULED THAT IT MUST NOT, 2026-09-03 ~21:00Z
    (etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md), verbatim:

        "A pre-registration mismatch never prevents a launch. It's recorded as a
         prediction, the run launches under the monitor, and the outcome is compared to
         the prediction on the certificate. Pre-registration predicts; the monitor
         watches; the grader judges afterward."

    and, on this exact category -- "Freeze or procedural state -- registration not frozen,
    pin missing, lesson not filed" -- her handling is explicit: "record and launch. A
    missing pin or unfiled lesson is bookkeeping and can be completed while the solve
    runs."

    THE `return []` IS UNCONDITIONAL AND IS THE FIRST STATEMENT, DELIBERATELY. There is no
    branch above it, no flag that re-enables a refusal, and no state -- MISMATCH included
    -- that reaches a non-empty list. THAT IS THE MECHANISM, not a promise about one:
    read this function and there is nowhere for a refusal to come from. `--strict` is
    REMOVED rather than left dormant, because a flag that no longer means what its name
    says is worse than no flag, and its removal DISSOLVES the §2s.2 sunset question
    entirely -- there is nothing left to sunset into.

    WHAT IS NOT WEAKENED, AND IT IS THE LOAD-BEARING HALF. Her words: "The grader is
    unchanged, and that matters: the frozen grader still judges against the
    pre-registration... The rule changes WHEN the gate applies -- after the fact, on
    evidence -- not WHETHER it applies." A run whose comparator drifted still cannot be
    graded by that comparator: the frozen comparator refuses (exit 2) rather than degrade,
    per rule 4's standing precedent, and nothing here touches any comparator. Rule 2 is
    untouched; registrations still freeze before compute, because they are the predictions
    being tested.

    ⚠ THE HONEST COST, STATED RATHER THAN BURIED. Under this rule a run with a drifted
    comparator SPENDS ITS COMPUTE AND THEN CANNOT BE GRADED BY THAT COMPARATOR. That is a
    real cost, it is not a defect in this design, and she weighed it explicitly:
    "Refusing to widen the gate was right; refusing to launch was the expensive part."
    The fleet safety ceiling -- min(3x registered cap, remaining box budget), the
    monitor's, NOT this check's -- is what protects the box.

    The reading itself is unchanged and is MORE valuable than before, not less: it is
    written to the launched record by queue_runner.launch() as a harvestable prediction,
    and the predicted-versus-actual comparison is the calibration dataset Sanaa's item 3
    is about.
    """
    return []


# ---------------------------------------------------------------- the queue-row pin reading
def coverage(root: Path, repo: Path) -> dict:
    """Walk a queue root and count what freeze enforcement DOES and DOES NOT reach.

    ⚠ THIS IS NOT §2s.4's COVERAGE FIGURE and must never be quoted as one. §2s.4's
    coverage is judged / total over the GRADER population check_comparator_freeze walks.
    This counts QUEUE ROWS. Different objects, different populations, not convertible.
    Verification owns the weekly report; this is a reading off disk so nobody has to take
    this lane's word for the queue's half.

    TWO REPAIRS, 2026-09-03, each with a control that FAILED BEFORE IT:

    (D1) AN EMPTY POPULATION REFUSES. It used to print `0/0` and return 0 -- verbatim
    what FREEZE_ENFORCEMENT_SPEC §2 forbids and what §2p.2 already made law, reproduced
    one level up from where verification had just found the same class in their own
    instrument. A metric that reads clean on an empty population is the degenerate path
    wearing the metric's clothes.

    (D2) `refused/` IS WALKED. It used to glob only `*/*.json` and `*/launched/*.json`.
    A MISMATCH row is refused by tick(), moved to `<team>/refused/`, and so LEFT THE
    POPULATION ENTIRELY -- measured on a planted row: the walk over the very root holding
    it reported `total=0, MISMATCH=0`. That made the number improvable BY HIDING A
    VIOLATION, which §2s.4 names as the one way this kind of metric can leave the lab
    worse off than no metric at all. Refused rows are now counted in the tally AND
    reported in their own column, so a violation is visible twice and absorbed nowhere.
    """
    root, repo = Path(root), Path(repo)
    tally = {k: 0 for k in ALL_STATES}
    refused_tally: dict[str, int] = {}
    rows, unparsed = [], []
    walked = ([("queued", p) for p in sorted(root.glob("*/*.json"))]
              + [("launched", p) for p in sorted(root.glob("*/launched/*.json"))]
              + [("refused", p) for p in sorted(root.glob("*/refused/*.json"))])
    for where, p in walked:
        try:
            e = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            # COUNTED, not skipped. A row the walk cannot parse is a hole in the reading,
            # and a hole that is silently dropped is the same defect as D2 in miniature.
            unparsed.append((str(p), f"{type(exc).__name__}: {exc}"))
            continue
        if not isinstance(e, dict):
            unparsed.append((str(p), "not a JSON object"))
            continue
        rec = grading_freeze_record(e, repo)
        tally[rec["verdict"]] = tally.get(rec["verdict"], 0) + 1
        if where == "refused":
            refused_tally[rec["verdict"]] = refused_tally.get(rec["verdict"], 0) + 1
        rows.append((str(p), where, rec["verdict"]))
    total = sum(tally.values())
    if total == 0:
        raise Refusal(
            f"EMPTY POPULATION at {root}: {len(walked)} queue file(s) found, "
            f"{len(unparsed)} unparseable, 0 rows read. A reading over nothing is "
            f"REFUSED, not reported as 0/0 and not reported as clean -- an instrument "
            f"that answers cleanly on an empty input has been shown to pass a repository "
            f"whose every comparator was rewritten this morning (FREEZE_ENFORCEMENT_SPEC "
            f"section 2; VERIFICATION_CHARTER section 2p.2).")
    eligible = sum(v for k, v in tally.items() if k != "UNREGISTERED")
    return dict(tally=tally, rows=rows, eligible=eligible, pinned=tally["PINNED"],
                total=total, refused_tally=refused_tally,
                refused_total=sum(refused_tally.values()), unparsed=unparsed)


def walked_at(repo: Path) -> str:
    """The commit a reading was walked at. §2s.9.1: a figure without its walked commit
    is meaningless, because the population GREW BY ONE GRADER INSIDE A SINGLE TASK and
    every new grader enters unjudged by construction."""
    return _git_rev_parse(repo, "HEAD^{commit}") or "UNKNOWN-HEAD"


# ---------------------------------------------------------------- instrument self-check
def count_assert_nodes(source: str) -> int:
    return sum(1 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert))


def ast_self_check() -> list[str]:
    n = count_assert_nodes(Path(__file__).read_text())
    if n:
        return [f"AST-NO-ASSERT: this instrument carries {n} `assert` statement(s); "
                f"`python3 -O` deletes every one (L-332). A gate is a `raise` or a "
                f"`sys.exit(2)`, never an assert."]
    return []


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("entries", nargs="*")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--pin-reading", dest="pin_reading", metavar="QUEUE_ROOT",
                    help="walk a queue root and print the per-state breakdown with the "
                         "commit it was walked at. THIS IS NOT A COVERAGE FIGURE: it "
                         "counts QUEUE ROWS, while VERIFICATION_CHARTER 2s.4's coverage "
                         "is judged/total over the GRADER population.")
    # The old spelling still works so no record that cites it is stranded, but it prints
    # the rename and the disclaimer rather than quietly answering to the wrong word.
    ap.add_argument("--coverage", dest="coverage_alias", metavar="QUEUE_ROOT",
                    help=argparse.SUPPRESS)
    # `--strict` IS REMOVED, NOT DEPRECATED. It converted UNPINNED into a launch refusal,
    # and nothing refuses at launch since Sanaa's 2026-09-03 ~21:00Z ruling. Left in place
    # it would be a switch whose name promises an effect it can no longer have. Its
    # removal also dissolves the §2s.2 sunset question: there is nothing to sunset into.
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        import grader_freeze_gate_selftest as st  # noqa: E402
        return st.run()

    bad = ast_self_check()
    if bad:
        for b in bad:
            print("REFUSED (instrument): " + b)
        return EXIT_REFUSE

    repo = Path(a.repo)
    target = a.pin_reading or a.coverage_alias
    if a.coverage_alias:
        print("NOTE: --coverage is renamed --pin-reading. The old spelling still works "
              "and the reading is unchanged; the WORD was wrong.")
    if target:
        cov = coverage(Path(target), repo)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        print(f"GRADER-FREEZE QUEUE-ROW PIN READING over {target}")
        print(f"  walked at HEAD {walked_at(repo)}  {stamp}  (repo {repo})")
        print(f"  ⚠ NOT the VERIFICATION_CHARTER 2s.4 COVERAGE FIGURE. That is "
              f"judged/total over the GRADER population; this counts QUEUE ROWS. "
              f"Different objects over different populations -- neither is convertible "
              f"into the other and neither checks the other.")
        for k in sorted(cov["tally"]):
            print(f"  {k:24s} {cov['tally'][k]:5d}")
        print(f"  {'-'*30}")
        print(f"  rows walked              {cov['total']:5d}   "
              f"(queued + launched + refused)")
        print(f"  of which in refused/     {cov['refused_total']:5d}   "
              f"{dict(sorted(cov['refused_tally'].items())) or '{}'}")
        print(f"  NO RATIO IS PRINTED, AND THE OMISSION IS THE POINT. Sanaa 2026-09-03 "
              f"~20:00Z: coverage ratios are FORWARD-ONLY AND UNREPORTED, and no "
              f"instrument measures another's reach until the first has changed a "
              f"verdict at least once. THIS ENFORCER HAS CHANGED ZERO VERDICTS -- it "
              f"fires at launch and every row it has met was already launched. The "
              f"counts above are an INTERNAL ENGINEERING CENSUS: not a coverage figure, "
              f"not a compliance figure, not for quoting upward or into a record.")
        if cov["unparsed"]:
            print(f"  ⚠ {len(cov['unparsed'])} row(s) could not be parsed and are in NO "
                  f"tally above -- they are a HOLE in this reading, not a clean result:")
            for p, why in cov["unparsed"]:
                print(f"      {p}: {why}")
        # A refused violation is reported TWICE on purpose -- once in its state's tally
        # and once in the refused column -- because the defect this repairs was a
        # violation that vanished from the population by being acted on correctly.
        return 0

    if not a.entries:
        print("No entries given. Nothing was read; nothing was recorded.")
        return 0

    # THE CLI READS AND REPORTS. IT DOES NOT REFUSE AN ENTRY ON ITS FREEZE STATE, because
    # the launch path does not either, and a command-line tool that answered `2` where the
    # daemon answers `launch` would be a second, contradictory authority on the same
    # question. The ONLY non-zero exit left is the instrument refusing ITSELF -- an
    # unreadable file, a non-object, or the AST/pairing self-checks -- which is a
    # statement about this tool, never about the run.
    unreadable = 0
    for s in a.entries:
        p = Path(s)
        try:
            e = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"REFUSED (instrument) {p}: cannot read as JSON: {exc}")
            unreadable += 1
            continue
        if not isinstance(e, dict):
            print(f"REFUSED (instrument) {p}: not a JSON object")
            unreadable += 1
            continue
        rec = grading_freeze_record(e, repo)
        mark = "PREDICTS-REFUSE" if rec["predicts"] == "GRADING_WILL_REFUSE" else "RECORDED"
        print(f"{mark} {p}  [{rec['verdict']}] predicts={rec['predicts']} "
              f"source={rec['source']}")
        print(f"    {rec['detail']}")
        if rec["predicts"] == "GRADING_WILL_REFUSE":
            print("    THIS DOES NOT STOP THE LAUNCH (Sanaa 2026-09-03 ~21:00Z). It is "
                  "recorded as a prediction that the FROZEN GRADER will refuse this run "
                  "afterwards, and the certificate compares predicted against actual.")
    if unreadable:
        print(f"\n{unreadable} of {len(a.entries)} file(s) could not be read. That is a "
              f"refusal BY this instrument ABOUT ITS INPUT, not a verdict on any run.")
        return EXIT_REFUSE
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        sys.exit(EXIT_REFUSE)
