#!/usr/bin/env python3
"""The manifest of per-team board sources, and the validator both board tools share.

Sanaa's PLUMBING FREEZE directive, 2026-08-31 (`etc/sessions/*_sanaa_plumbing_freeze.md`),
verbatim: "Boards become per-team files (one writer each), merged into the lab board by a
nightly tool -- no shared-file splicing by agents, ever."

This module is the single place that knows

  * WHICH source files exist,
  * IN WHAT ORDER they concatenate,
  * WHO is allowed to write each one, and
  * WHAT MAKES ONE MALFORMED.

`split_lab_state.py` (one-time migration) and `merge_lab_state.py` (the nightly merger)
both import it, so the split and the merge cannot disagree about the shape of a source
file -- a disagreement between them is exactly how a "lossless" migration becomes lossy
three days later.

VERIFICATION_CHARTER §2l ("remove the possibility, not the instance") is the reason the
manifest is DATA in one module rather than two parallel literal lists.
"""

import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR_REL = "docs/lab_state"
BOARD_REL = "docs/LAB_STATE.md"

# The lab title line the board has carried since it was created. It lives at the top of
# the chief's source because the chief owns the preamble.
TITLE_LINE = "# LAB_STATE — the resume board"
CHIEF_HEADING = "## CHIEF — standing directives in force"

# The six teams, in the order their sections appear in the board, and the ONE agent
# allowed to write each file. `harness/teams.yaml` is the roster's source of truth; this
# list is asserted against it by `assert_matches_roster()` below, so a seventh team added
# to the roster cannot silently go unboarded.
TEAMS = [
    ("closure", "closure-supervisor"),
    ("dafoam", "dafoam-supervisor"),
    ("heat-transfer", "heat-transfer-supervisor"),
    ("cfd", "cfd-supervisor"),
    ("verification", "verification-supervisor"),
    ("ansys-verification", "ansys-verification-supervisor"),
]

# The chief's file carries the preamble AND the `## CHIEF` section: one writer, the main
# session. It is a source like any other, which is why the merger has SEVEN inputs and
# not six.
CHIEF = ("chief", "the chief (main session)")

H2 = re.compile(r"^## .*$", re.M)


def order():
    """The source files, in concatenation order: (stem, owner, expected_heading)."""
    out = [(CHIEF[0], CHIEF[1], CHIEF_HEADING)]
    for team, owner in TEAMS:
        out.append((team, owner, "## " + team))
    return out


def src_path(stem, repo=REPO):
    return os.path.join(repo, SRC_DIR_REL, stem + ".md")


class Malformed(Exception):
    """A source file the merger REFUSES to merge. Never a warning."""


def validate(stem, expected_heading, raw, path_for_msg):
    """Fail-closed validation of ONE source file's raw bytes.

    Raises Malformed on anything that could produce a board with a team silently
    missing, silently truncated, or silently duplicated. Returns a list of
    non-fatal warnings (strings).

    Every clause here answers a specific way this file could be wrong in a way a
    READER OF THE MERGED BOARD would misread as "that team has nothing to report".
    """
    warn = []

    if raw == b"":
        raise Malformed(f"{path_for_msg}: empty file")

    if b"\x00" in raw:
        raise Malformed(f"{path_for_msg}: contains a NUL byte (not a text board)")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise Malformed(f"{path_for_msg}: not valid UTF-8 ({e})")

    if not raw.endswith(b"\n"):
        raise Malformed(
            f"{path_for_msg}: does not end with a newline; concatenating it would "
            f"weld its last line onto the next team's heading"
        )

    if MARKER in text:
        raise Malformed(
            f"{path_for_msg}: contains the generated-board marker. This file looks "
            f"like a copy of the MERGED board, not a source. Merging it would "
            f"duplicate every team's section."
        )

    lines = text.split("\n")

    if stem == CHIEF[0]:
        if lines[0] != TITLE_LINE:
            raise Malformed(
                f"{path_for_msg}: first line is {lines[0]!r}, expected the board "
                f"title {TITLE_LINE!r}"
            )
    else:
        if lines[0] != expected_heading:
            raise Malformed(
                f"{path_for_msg}: first line is {lines[0]!r}, expected exactly "
                f"{expected_heading!r}"
            )

    heads = H2.findall(text)
    if len(heads) != 1:
        raise Malformed(
            f"{path_for_msg}: contains {len(heads)} '## ' headings, expected exactly "
            f"1 ({expected_heading!r}). A second '## ' heading in a one-writer file "
            f"is a team writing into another team's namespace -- the exact splice "
            f"this design exists to make impossible. Found: {heads[:5]!r}"
        )
    if heads[0] != expected_heading:
        raise Malformed(
            f"{path_for_msg}: its '## ' heading is {heads[0]!r}, expected "
            f"{expected_heading!r}"
        )

    # Truncation guard. A file that is a heading and nothing else reads, in the merged
    # board, as "this team has nothing to report" -- which is the dangerous partial
    # output this whole tool is built to refuse.
    after = text.split(expected_heading, 1)[1]
    if not after.strip():
        raise Malformed(
            f"{path_for_msg}: heading only, no body. A team section with no body is "
            f"indistinguishable in the merged board from a team with nothing to "
            f"report; refusing rather than emitting it."
        )

    # Non-fatal: the freshness stamp `check_harness.py` grades. A missing stamp is a
    # board-hygiene finding, not a reason to refuse to publish the board -- refusing
    # here would let one team's forgotten stamp black out all six teams.
    if "**Section last written:**" not in text:
        warn.append(f"{path_for_msg}: no '**Section last written:**' stamp")

    return warn


def roster_teams(repo=REPO):
    """The team names in `harness/teams.yaml`, which is the roster's source of truth.

    Raises Malformed rather than returning a short list. A reader that answers
    "0 teams" because it could not find or parse the file is the fail-open this
    whole tool exists to refuse: it would report perfect agreement with a manifest
    it never actually read. So the PLANTED CONTROL IS BUILT IN -- the parse must
    return a non-empty list, and the file must exist -- and every other outcome
    refuses.
    """
    y = os.path.join(repo, "harness", "teams.yaml")
    if not os.path.exists(y):
        raise Malformed(
            f"harness/teams.yaml not found at {y}: the roster's source of truth is "
            f"unreadable, so this tool CANNOT KNOW whether a team is missing from "
            f"the board. Refusing rather than publishing a board on an unchecked "
            f"manifest."
        )
    try:
        text = open(y, encoding="utf-8").read()
    except OSError as e:
        raise Malformed(f"harness/teams.yaml unreadable ({e})")
    names = re.findall(r"^\s{4}team:\s*([A-Za-z0-9_-]+)\s*$", text, re.M)
    if not names:
        raise Malformed(
            f"harness/teams.yaml parsed to ZERO teams. A zero from a reader not "
            f"shown able to see a non-zero is not evidence (CLAUDE.md rule 3): "
            f"either the file's shape changed or this regex is dead. Refusing."
        )
    return names


def assert_matches_roster(repo=REPO):
    """The manifest above vs `harness/teams.yaml`. Returns (ok, message).

    A team added to the roster and not to this manifest would be a team whose board
    the nightly merger silently never publishes. THIS IS CALLED BY `build()` ON
    EVERY RUN, not only by the selftest -- see the note there.
    """
    try:
        names = roster_teams(repo)
    except Malformed as e:
        return False, str(e)
    mine = [t for t, _ in TEAMS]
    if sorted(names) != sorted(mine):
        missing = sorted(set(names) - set(mine))
        extra = sorted(set(mine) - set(names))
        return False, (f"roster {sorted(names)} != board manifest {sorted(mine)}"
                       + (f"; IN THE ROSTER AND UNBOARDED: {missing}" if missing else "")
                       + (f"; BOARDED AND NOT IN THE ROSTER: {extra}" if extra else ""))
    return True, f"{len(mine)} teams, manifest == harness/teams.yaml"


# The merged board's first bytes. Deliberately carries NO timestamp: the merger's output
# is a pure function of its sources, so `merge_lab_state.py --check` is a real drift
# test and a nightly run that changes nothing produces no diff.
MARKER = "GENERATED FILE -- DO NOT EDIT -- built by scripts/merge_lab_state.py"

HEADER = (
    "<!-- " + MARKER + "\n"
    "\n"
    "     This board is DERIVED from the per-team source files under docs/lab_state/.\n"
    "     Sources, in this order, one writer each:\n"
    + "".join(f"       docs/lab_state/{s}.md   <- {o}\n" for s, o, _ in order()) +
    "\n"
    "     EDIT YOUR OWN TEAM'S SOURCE FILE. A hand edit made here is destroyed by the\n"
    "     next merge, silently and without a diff anyone will read.\n"
    "\n"
    "     Rebuild:  python3 scripts/merge_lab_state.py\n"
    "     Drift:    python3 scripts/merge_lab_state.py --check\n"
    "\n"
    "     Sanaa's PLUMBING FREEZE directive, 2026-08-31: \"Boards become per-team\n"
    "     files (one writer each), merged into the lab board by a nightly tool -- no\n"
    "     shared-file splicing by agents, ever.\"\n"
    "-->\n"
)


def build(repo=REPO, src_dir=None, check_roster=True):
    """Read every source, validate it, return (board_bytes, warnings).

    Raises Malformed on the FIRST bad source, having written nothing. The caller is
    responsible for never writing an output on that path.

    THE ROSTER GATE RUNS HERE, ON EVERY BUILD. It used to live only in `--selftest`,
    which meant that in PRODUCTION a seventh team added to `harness/teams.yaml` would
    have been silently unboarded for as long as nobody typed `--selftest` -- a gate
    that measured its condition and never acted on it, which is the second direction
    of fail-open catalogued in `docs/FAIL_OPEN_GATE_AUDIT.md` §11. `check_roster` is
    False only where the caller has deliberately relocated the roster (the selftest's
    scratch-tree mutants), and no production path passes it.
    """
    if check_roster:
        ok, msg = assert_matches_roster(repo)
        if not ok:
            raise Malformed(
                f"ROSTER MISMATCH -- {msg}. `harness/teams.yaml` is the roster's "
                f"source of truth and this board manifest disagrees with it, so a "
                f"merge now would publish a board that a reader would take as the "
                f"whole lab while a team is missing from it. Refusing; nothing "
                f"written. Fix `TEAMS` in scripts/lab_state_sources.py and add the "
                f"team's source file under {SRC_DIR_REL}/."
            )
    warns = []
    parts = [HEADER.encode("utf-8")]
    for stem, _owner, heading in order():
        p = (os.path.join(src_dir, stem + ".md") if src_dir
             else src_path(stem, repo))
        rel = os.path.relpath(p, repo) if src_dir is None else p
        if not os.path.isfile(p):
            raise Malformed(f"{rel}: source file missing")
        try:
            raw = open(p, "rb").read()
        except OSError as e:
            raise Malformed(f"{rel}: unreadable ({e})")
        warns += validate(stem, heading, raw, rel)
        parts.append(raw)
    return b"".join(parts), warns
