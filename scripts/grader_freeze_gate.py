#!/usr/bin/env python3
"""grader_freeze_gate.py -- STEP (1) of Sanaa's freeze-enforcement wiring order
(SANAA-DIRECT 2026-09-03 ~17:30Z, item 6, verbatim in
etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md:42-44):

    "(1) the queue daemon refuses to grade any run whose comparator's sha does not
     match its frozen registration -- enforcement at the choke point first,
     primitive is fine"

WHAT THIS FILE IS.  The primitive that answers ONE question about ONE queue entry:
does the comparator this entry names still hash to what its frozen registration
pinned?  It decides; it never moves, writes, launches or grades anything.  Two
callers use it, and only the first can refuse:

  * queue_entry_check.CHECKS["GRADER-FREEZE"] -- the LIVE refusal.  queue_runner.tick()
    calls qec.validate(entry, REPO, path) and routes any non-empty failure list
    straight into move_refused().  That is the daemon's one and only refusal choke
    point and this check now sits in it.
    CITED BY SYMBOL, NOT BY LINE, DELIBERATELY.  Every by-line citation of
    queue_runner.py in this repository that was checked on 2026-09-03 was STALE --
    four records cite `queue_runner.py:223` for list_entries(), which lives at :440,
    an error of 217 lines.  A citation that rots silently is worse than none.
  * queue_runner.launch() -- the RECORD.  Stamps `_grading_freeze` on the launched
    record so step (2) can COUNT coverage off disk instead of re-deriving it.

WHERE THE CHOKE POINT ACTUALLY IS, AND WHY THIS IS NOT A DEAD LIMB.  Measured
2026-09-03, not assumed: scripts/queue_runner.py has NO grading step.  main() loops
on tick(); tick() runs cap_watch() (which reports, never grades) and launch().  Of
the 306 queue entries on disk carrying a launch_cmd, exactly TWO name a grader
(ansys VMFL033-R2 and VMFL076-R2, both `run_vmfl0XX_r2.sh graded`); the other 304
launch a solver and grading happens afterwards, by hand or inside the run script.

So a hook placed at "where the daemon grades" would never fire -- the pathology this
codebase already carries twice (`launcher_rc`: one write, six selftest references,
zero production reads; `cap_watch` retiring on `status.exists()` without ever parsing
it).  THE HONEST CHOKE POINT IS THE LAUNCH, and refusing there is strictly STRONGER
than refusing at grading: a run whose comparator cannot be pinned never burns the
core-minutes in the first place.  What it does NOT cover is stated plainly in
COVERAGE below, because an enforcement claim wider than its mechanism is the failure
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

THE TOLERANT DEFAULT, AND HOW IT STAYS VISIBLE.  An entry with no grading-path field
is UNPINNED and is NOT refused.  That is a deliberate choice with a measured reason:
all 306 entries on disk lack the field, so refusing on absence would refuse the
lab's entire queue on the day it landed -- a brick, not a gate.  But "no field,
therefore grade it anyway" silently reproduces today's state, so UNPINNED is made
COUNTABLE in three places, none of them prose:
    1. `_grading_freeze.verdict` stamped on every launched record (queue_runner.launch);
    2. a `GRADER-FREEZE <case>: UNPINNED` line in verification/queue/runner.log;
    3. `--pin-reading <queue root>`, which walks the queue and prints the per-state
       breakdown with the commit it was walked at.
UNPINNED is refusal-ELIGIBLE, not refused: flipping `--strict` turns the same reading
into a refusal with no change to what is measured.

THE SUNSET IS SANAA'S AND NO AGENT SETS IT.  VERIFICATION_CHARTER §2s.2 rules that the
third outcome (proceed-and-count) "carries a sunset or it is permanent" -- at the sunset
UNPINNED becomes a refusal.  THE MECHANISM EXISTS HERE (`--strict`, one flag, nothing
else changes) AND THE DATE DOES NOT.  The date is recorded, when she sets it, in
`docs/charters/VERIFICATION_CHARTER.md` §2s -- named here so its ABSENCE IS VISIBLE
RATHER THAN IMPLIED.  `--strict` has no default-on path and never self-activates; no
figure this file emits may be read as having reached a sunset condition.

THIS FILE EMITS NO §2s.4 COVERAGE FIGURE, DELIBERATELY.  §2s.4's coverage is
judged / total over the GRADER population that check_comparator_freeze walks (40 of
189 at its measurement).  `--pin-reading` counts QUEUE ROWS -- a different object over
a different population, not convertible into that one and not a check on it.  The two
must never be quoted as though they were the same number.  §2s.9.1 also rules that any
such figure is meaningless without the commit it was walked at, so every reading this
file prints carries its HEAD sha; and a stop condition written as a bare count -- the
"145/145" an earlier draft of this docstring cited -- names a target that RECEDES as
the lab works, and is not used here.

THE FIELD NAME IS PROPOSED, NOT SETTLED.  `grading_paths` is this lane's proposal;
the schema field name is an OPEN QUESTION ON THE CHIEF'S DESK (cfd board 47).
GRADING_PATHS_FIELD and GRADING_PATHS_ALIASES below are the single place it is
written down; a ruling renames it there and nowhere else.

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

# THE PROPOSED SCHEMA FIELD. Name NOT final -- on the chief's desk (cfd board 47).
# A list, because a rung can be graded by more than one comparator, and because a
# scalar that later needs to be a list is a migration nobody performs.
GRADING_PATHS_FIELD = "grading_paths"
# Tolerated spellings, so a ruling that picks another name does not strand rows
# written against this one. Read in order; the first present wins.
GRADING_PATHS_ALIASES = (GRADING_PATHS_FIELD, "grader_paths", "comparator_paths")

FULL_SHA_CHARS = set("0123456789abcdef")

# Sanaa's 2026-08-31 ruling (9154c8ef), already honoured by queue_entry_check: an
# UNREGISTERED feasibility/physics rung is queue-legal with a tag in place of a freeze
# sha, and ITS OUTPUTS ARE NEVER GRADEABLE. Such a row has no freeze to pin against and
# is EXEMPT here -- exempt is not covered, and --pin-reading counts it in its own column.
UNREGISTERED_PREREG_TAGS = frozenset({"FEASIBILITY", "PHYSICS"})

# States that must stop a launch. Everything else is a reading, not a refusal.
#
# THE LAST TWO ARE §2s.6's, ADDED 2026-09-03 WITH D8, AND NEITHER CAN FIRE ON ANY ROW
# ON DISK TODAY -- measured, not assumed: zero registrations in this repository carry a
# GRADING_PATHS declaration, so there is nothing yet for a conflict to be between and
# nothing yet to be unreadable. They refuse a condition that does not exist yet, which
# is the only honest moment to install a refusal.
REFUSING_STATES = ("MISMATCH", "ABSENT-AT-FREEZE", "ABSENT-ON-DISK", "MALFORMED",
                   "DECLARATION-CONFLICT", "REGISTRATION-UNREADABLE")

# Every verdict this instrument can return. One tuple so the coverage tally, the
# printed breakdown and the states themselves cannot drift apart -- a tally keyed on a
# hand-written list is how a new state becomes invisible to the count that exists to
# see it.
ALL_STATES = ("PINNED", "UNPINNED", "UNREGISTERED") + REFUSING_STATES


class Refusal(Exception):
    """A condition that must stop this instrument under ANY flag."""


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
# token is `GRADING_PATHS:` followed by one or more repo-relative paths.  Leading
# markdown decoration (`>`, `*`, `_`, backtick, `-`) is tolerated because registrations
# are markdown; anything else on the left is not a declaration.  A registration carrying
# TWO declarations that disagree is a CONFLICT, not a menu -- §2s.6's "never choose"
# applies inside one document exactly as it does between two.
REGISTRATION_DECL_RE = re.compile(r"^[\s>*_`+-]*GRADING_PATHS\s*:\s*(.+?)\s*$", re.MULTILINE)


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


def grading_freeze_record(entry: dict, repo: Path) -> dict:
    """THE PRIMITIVE. A dict reading of one entry. Never raises on entry content.

    Keys: verdict, detail, field, paths (one row per declared path with `path`,
    `frozen_sha`, `disk_sha`, `state`), prereg_commit, refusal_eligible.
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
    if reg_state == "DECLARED":
        # The senior source spoke. Whether or not the entry agreed, THIS is what is pinned.
        paths, field = reg_paths, f"the frozen registration ({entry.get('prereg_path')})"

    if not paths:
        return dict(verdict="UNPINNED", detail=(
            f"entry declares no {GRADING_PATHS_FIELD!r}: no comparator is named, so the "
            f"sha of the script that will grade case {case} is NOT pinned to freeze "
            f"{sha[:8]} and this launch is NOT covered by freeze enforcement. Tolerated "
            f"by the default policy and COUNTED as uncovered -- it is not a pass."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=True)

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

    bad = [r for r in rows if r["state"] in REFUSING_STATES]
    if not bad:
        return dict(verdict="PINNED", detail=(
            f"{len(rows)} comparator(s) named by {field!r} hash EXACTLY as commit "
            f"{sha[:8]} froze them."),
            field=field, paths=rows, prereg_commit=sha, refusal_eligible=False)
    return dict(verdict=worst, detail=(
        f"{len(bad)} of {len(rows)} comparator(s) named by {field!r} do NOT match "
        f"freeze {sha[:8]}."),
        field=field, paths=rows, prereg_commit=sha, refusal_eligible=True)


def refusals(entry: dict, repo: Path, strict: bool = False) -> list[str]:
    """The refusal strings for one entry. THE SHAPE queue_entry_check.CHECKS expects.

    Empty list = nothing to refuse. A refusal is returned ONLY for a state in
    REFUSING_STATES -- or, under `strict`, also for UNPINNED. `strict` is OFF on the
    live path today and is the single switch a ruling flips AT THE SUNSET; nothing else
    changes when it does. THE SUNSET DATE IS SANAA'S, IT DOES NOT EXIST YET, and its
    home is named in this module's docstring so its absence is visible. The earlier
    wording here named "coverage reaches 145/145" as the trigger: VERIFICATION_CHARTER
    §2s.9.1 has since ruled that a stop condition written as a BARE COUNT names a target
    that RECEDES as the lab works -- every new grader enters the population unjudged, so
    normal productive work moves the target away faster than evidence accrues. The
    condition is a ratio at a stated walked commit, never a count, and this flag does not
    read any figure to decide anything.
    """
    rec = grading_freeze_record(entry, repo)
    v = rec["verdict"]
    if v in ("DECLARATION-CONFLICT", "REGISTRATION-UNREADABLE"):
        # A DIFFERENT REFUSAL FROM THE ONE BELOW, and it must not borrow its wording:
        # nothing here says a comparator moved. The claim is that this row cannot say
        # WHICH comparator is pinned, which is refused before it spends core-minutes.
        return [
            f"GRADER-FREEZE [{v}]: {rec['detail']}\n"
            "        TO CLEAR: make the frozen registration and the queue entry name the "
            "same comparator, or remove the entry's declaration and let the registration "
            "speak alone. Nothing here edits, reverts or stages anything."
        ]
    if v in REFUSING_STATES:
        lines = []
        for r in rec["paths"]:
            if r["state"] not in REFUSING_STATES:
                continue
            lines.append(
                f"        {r['path']}: {r['state']} "
                f"frozen={str(r['frozen_sha'])[:12]} disk={str(r['disk_sha'])[:12]}")
        return [
            "GRADER-FREEZE: the comparator named by this entry does not match the "
            f"sha its frozen registration ({rec['prereg_commit']}) pinned.\n"
            + "\n".join(lines)
            + "\n        A run graded by a script that has moved since the freeze cannot "
              "show the gate was not chosen to fit the answer (CLAUDE.md rule 2), so this "
              "run is REFUSED BEFORE it spends core-minutes rather than graded after.\n"
              "        TO CLEAR: commit the comparator, re-freeze the registration at the "
              "new commit, and re-enqueue. Nothing here edits, reverts or stages anything."
        ]
    if strict and v == "UNPINNED":
        return ["GRADER-FREEZE (--strict): " + rec["detail"]]
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
    ap.add_argument("--strict", action="store_true",
                    help="also REFUSE an entry that names no comparator (UNPINNED). "
                         "OFF on the live path; the switch a ruling flips AT THE SUNSET. "
                         "The sunset date is Sanaa's, does not exist yet, and this flag "
                         "never self-activates.")
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
        print(f"  PINNED / ELIGIBLE        {cov['pinned']}/{cov['eligible']}   "
              f"(UNREGISTERED rows are EXEMPT and excluded from the denominator; "
              f"exempt is not covered)")
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
        print("No entries given. Nothing was checked; nothing was refused.")
        return 0

    refused = 0
    for s in a.entries:
        p = Path(s)
        try:
            e = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"REFUSED {p}: cannot read as JSON: {exc}")
            refused += 1
            continue
        if not isinstance(e, dict):
            print(f"REFUSED {p}: not a JSON object")
            refused += 1
            continue
        rec = grading_freeze_record(e, repo)
        fails = refusals(e, repo, strict=a.strict)
        if fails:
            refused += 1
            print(f"REFUSED {p}  [{rec['verdict']}]")
            for f in fails:
                print("    " + f)
        else:
            # printed INSIDE the accepting branch, so the claim cannot outlive the check
            print(f"OK {p}  [{rec['verdict']}] {rec['detail']}")
    if refused:
        print(f"\n{refused} of {len(a.entries)} entr"
              f"{'ies' if len(a.entries) != 1 else 'y'} REFUSED by GRADER-FREEZE.")
        return EXIT_REFUSE
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        sys.exit(EXIT_REFUSE)
