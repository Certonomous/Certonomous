#!/usr/bin/env python3
r"""Did a landed commit change a section of the board that is not its own?

WHAT THIS EXISTS FOR
====================
`docs/LAB_STATE.md` is one file with one `## <team>` section per team, written by
five supervisors at once. The shared-board rule routes every board commit through
`git show $H:docs/LAB_STATE.md` -> `hash-object -w` -> `update-index --cacheinfo`,
a path that writes the commit and NEVER the worktree file. So the worktree copy is
stale by design in every section whose last committer conformed, and any committer
whose base is not re-derived from `$H` at commit time silently reverts the
sections it did not mean to touch.

Three such reverts landed on 2026-08-23, each verified here by byte-exact
reconstruction of the offending blob:

  d97ed4c9  reverted `## dafoam` to its 2026-08-22 21:01:45 vintage (`6c6de745`)
            -- the worktree's dafoam section was ~22.5 h old. Repaired `6ae77c79`.
  070da305  == parent `baa32076` with `## heat-transfer` swapped back to
            `b9a78483`; blob `0f65e0f1`. Repaired `40984dac`.
  890bfa7f  == `0bbe62dc` (the committer's OWN previous board commit) plus its new
            `## verification` section; blob `98b2c237`. Reverted TWO teams at once
            -- `## closure` and `## cfd`.

L-245 already names the assertion -- *"On a shared multi-section file, 'only my
paths' is not 'only my content' -- assert your hunks fall inside your own section
before update-index"*. All three incidents changed a foreign section, so all three
were inside that lesson's reach. The lesson was filed and never instrumented.
This module is the instrument.

WHAT IT DOES NOT DO
===================
  * It DETECTS, post-hoc, on a commit that already landed. It is wired into
    nothing, blocks nothing, and prevents nothing. Adopting it as a gate is the
    chief's and Sanaa's call, not this file's.
  * It CANNOT verify that a `Lab-Team:` trailer is truthful. Every commit in this
    repository carries one `Ubuntu` identity, so team attribution is not derivable
    from git and must be DECLARED. A commit that lies in its trailer passes.
    The trailer makes the claim reviewable; it does not make it verified.
  * It cannot see a commit that changed nothing -- absence of a board edit is not
    evidence that the board is correct. Use `check_board_reconciliation.py` for
    the HEAD-vs-worktree question.

EXIT CONTRACT
=============
    0  PASS      only the declared team's own section changed (or the commit does
                 not touch the board at all, or a declared `Board-Repair:` names
                 the incident it is repairing)
    2  REFUSED   a section other than the declared team's own changed, with no
                 `Board-Repair:` trailer naming an incident
    3  UNKNOWN   the revision could not be read, the board parsed to zero
                 sections, or the commit message declares no `Lab-Team:` trailer
    5  a planted control in --selftest did not behave as required

TRAILERS THIS MODULE READS
==========================
    Lab-Team: <team>            REQUIRED. The section this commit is entitled to
                                change. `chief` owns the preamble and the
                                `## CHIEF ...` section.
    Board-Repair: <incident>    OPTIONAL escape for a legitimate cross-section
                                repair -- `6ae77c79` and `40984dac` are both real
                                and both had to write a foreign section. It must
                                NAME the incident (a bare `Board-Repair:` with no
                                text is refused), because a repair that does not
                                say what it repairs is indistinguishable from the
                                accident it is excusing.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_kind  # noqa: E402

EXIT_PASS = 0
EXIT_REFUSED_FOREIGN_SECTION = 2
EXIT_UNKNOWN = 3
EXIT_CONTROL_BROKEN = 5

BOARD_PATH = "docs/LAB_STATE.md"
PREAMBLE = "__PREAMBLE__"

#: Which board section each declared team is entitled to change. The keys are the
#: `team:` values in harness/teams.yaml; `chief` is the main session, which owns
#: the preamble and the standing-directives section.
TEAM_SECTIONS: dict[str, set[str]] = {
    "closure": {"closure"},
    "dafoam": {"dafoam"},
    "heat-transfer": {"heat-transfer"},
    "cfd": {"cfd"},
    "verification": {"verification"},
    "chief": {PREAMBLE, "CHIEF"},
}

#: The `## CHIEF ...` heading carries an em dash and prose after it, so it is
#: matched by prefix rather than by equality.
CHIEF_HEADING_PREFIX = "CHIEF"

TRAILER_TEAM = re.compile(r"^Lab-Team:[ \t]*(.*)$", re.M)
TRAILER_REPAIR = re.compile(r"^Board-Repair:[ \t]*(.*)$", re.M)


def split_sections(text: str) -> dict[str, str]:
    """Split the board into `## <name>` sections, preamble under PREAMBLE.

    The section body INCLUDES its own heading line, so a heading that is edited
    (renamed, re-cased, or given a different em dash) registers as a change to
    that section rather than vanishing silently.
    """
    out: dict[str, str] = {}
    current = PREAMBLE
    buf: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            out[current] = "".join(buf)
            current = line[3:].strip()
            buf = [line]
        else:
            buf.append(line)
    out[current] = "".join(buf)
    return out


def section_owner_key(name: str) -> str:
    """The key TEAM_SECTIONS is written against, for a raw heading."""
    if name.startswith(CHIEF_HEADING_PREFIX):
        return CHIEF_HEADING_PREFIX
    return name


def changed_sections(before: str, after: str) -> list[str]:
    """Every section that differs, INCLUDING ones added or removed.

    Added and removed sections are the two forms a body-only diff would miss, and
    they are exactly how a heading gets swallowed -- `lab_state_section.py`
    refuses a stray `## ` inside a section file for this reason.
    """
    a, b = split_sections(before), split_sections(after)
    names = list(dict.fromkeys(list(a) + list(b)))
    return [n for n in names if a.get(n) != b.get(n)]


def read_rev(repo: Path, rev: str, path: str) -> tuple[str | None, str]:
    done = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True)
    if done.returncode != 0:
        detail = done.stderr.strip().splitlines()
        return None, (detail[-1] if detail else f"git exited {done.returncode}")
    return done.stdout, ""


def read_message(repo: Path, sha: str) -> tuple[str | None, str]:
    done = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%B", sha],
                          capture_output=True, text=True)
    if done.returncode != 0:
        detail = done.stderr.strip().splitlines()
        return None, (detail[-1] if detail else f"git exited {done.returncode}")
    return done.stdout, ""


def parse_trailers(message: str) -> tuple[str | None, str | None, bool]:
    """(team, repair_incident, repair_declared_but_empty)."""
    team_hits = TRAILER_TEAM.findall(message)
    repair_hits = TRAILER_REPAIR.findall(message)
    team = team_hits[-1].strip() if team_hits else None
    repair_declared = bool(repair_hits)
    repair = repair_hits[-1].strip() if repair_hits else None
    return (team or None), (repair or None), (repair_declared and not repair)


def run_controls() -> control_kind.ControlLedger:
    """Plant foreign-section changes and prove `changed_sections` sees them.

    RECOGNITION, not reachability. A PASS from this module is a ZERO -- an empty
    list of foreign sections -- and rule 3 is that a zero from a reader not shown
    able to see a non-zero is not evidence. The four planted forms are four
    genuinely different ways a foreign section changes, and a comparator that only
    diffed the bodies of headings present on BOTH sides would return the same
    empty list for two of them.
    """
    base = ("preamble line\n"
            "## CHIEF - standing directives in force\n"
            "chief text\n"
            "## closure\nclosure text\n"
            "## dafoam\ndafoam text\n"
            "## cfd\ncfd text\n")

    forms = {
        # 1. a foreign body edited in place
        "a foreign section's body edited":
            base.replace("dafoam text", "dafoam text EDITED-BY-A-PEER"),
        # 2. a foreign section deleted outright -- the 070da305 shape
        "a foreign section removed entirely":
            base.replace("## dafoam\ndafoam text\n", ""),
        # 3. a foreign section appended -- present on one side only
        "a foreign section added":
            base + "## verification\nnew text\n",
        # 4. a foreign HEADING altered, body untouched
        "a foreign section's heading altered":
            base.replace("## dafoam", "## dafoam-team"),
    }
    planted = {}
    for name, mutated in forms.items():
        seen = changed_sections(base, mutated)
        planted[name] = any(section_owner_key(s) not in TEAM_SECTIONS["cfd"]
                            for s in seen)

    negatives = {
        # the committer's OWN section changing must NOT read as foreign
        "the declared team's own section edited":
            any(section_owner_key(s) not in TEAM_SECTIONS["cfd"]
                for s in changed_sections(
                    base, base.replace("cfd text", "cfd text, rewritten"))),
        # no change at all must NOT read as foreign
        "an identical board":
            any(section_owner_key(s) not in TEAM_SECTIONS["cfd"]
                for s in changed_sections(base, base)),
    }

    ledger = control_kind.ControlLedger(
        claim_class=f"a foreign-section change in {BOARD_PATH}")
    ledger.plant("board section forms",
                 vocabulary=f"{BOARD_PATH} `## ` sections",
                 planted=planted, negative=negatives)
    return ledger


def grade(before: str, after: str, team: str | None, repair: str | None,
          repair_empty: bool,
          ledger: control_kind.ControlLedger | None = None) -> dict:
    """Pure, so the controls and any test can drive it on fixtures."""
    ledger = run_controls() if ledger is None else ledger

    changed = changed_sections(before, after)
    owned = TEAM_SECTIONS.get(team or "", set())
    foreign = [s for s in changed if section_owner_key(s) not in owned]

    zero_verdict, zero_why = ledger.verdict_for(len(foreign))

    if not split_sections(after) or list(split_sections(after)) == [PREAMBLE]:
        verdict, code, why = "UNKNOWN", EXIT_UNKNOWN, (
            f"{BOARD_PATH} parsed to zero `## ` sections -- the file changed "
            f"shape; do not work around it")
    elif ledger.kind == control_kind.BROKEN:
        verdict, code, why = "UNKNOWN", EXIT_UNKNOWN, (
            f"the planted control did not hold, so this reader is not known to "
            f"be able to see a foreign-section change: {zero_why}")
    elif team is None:
        verdict, code, why = "UNKNOWN", EXIT_UNKNOWN, (
            "the commit message declares no `Lab-Team:` trailer, so the section "
            "it was entitled to change is not stated and cannot be inferred -- "
            "every commit here carries one Ubuntu identity")
    elif team not in TEAM_SECTIONS:
        verdict, code, why = "UNKNOWN", EXIT_UNKNOWN, (
            f"`Lab-Team: {team}` is not a team in harness/teams.yaml "
            f"({', '.join(sorted(TEAM_SECTIONS))})")
    elif repair_empty:
        verdict, code, why = "REFUSED", EXIT_REFUSED_FOREIGN_SECTION, (
            "a `Board-Repair:` trailer was declared but NAMES NO INCIDENT -- a "
            "repair that does not say what it repairs is indistinguishable from "
            "the accident it is excusing")
    elif not foreign:
        verdict, code, why = "PASS", EXIT_PASS, (
            f"only `{team}`'s own section(s) changed"
            if changed else f"the commit does not change {BOARD_PATH}")
    elif repair:
        verdict, code, why = "PASS", EXIT_PASS, (
            f"foreign section(s) {', '.join(foreign)} changed, DECLARED as a "
            f"repair of: {repair}. Declared, not verified -- read the diff")
    else:
        verdict, code, why = "REFUSED", EXIT_REFUSED_FOREIGN_SECTION, (
            f"{len(foreign)} section(s) other than `{team}`'s own changed with "
            f"no `Board-Repair:` trailer: {', '.join(foreign)}")

    return {"path": BOARD_PATH, "team": team, "repair": repair,
            "changed": changed, "foreign": foreign,
            "verdict": verdict, "exit": code, "because": why,
            "zero_verdict": zero_verdict, "zero_because": zero_why,
            "ledger": ledger}


def render(result: dict, sha: str, parent: str) -> None:
    print("=" * 78)
    print(f"BOARD SECTION OWNERSHIP -- {result['path']}")
    print("=" * 78)
    print(f"  commit           : {sha}")
    print(f"  compared against : {parent}")
    print(f"  Lab-Team         : {result['team'] or '(none declared)'}")
    print(f"  attribution from : {result.get('team_source', 'commit trailer')}")
    print(f"  Board-Repair     : {result['repair'] or '(none)'}")
    print(f"  sections changed : {', '.join(result['changed']) or '(none)'}")
    print(f"  foreign sections : {', '.join(result['foreign']) or '(none)'}")
    print(result["ledger"].render(len(result["foreign"])))
    print("-" * 78)
    print(f"VERDICT: {result['verdict']}   (exit {result['exit']})")
    print(f"BECAUSE: {result['because']}")
    print("CANNOT SEE: whether the `Lab-Team:` trailer is TRUTHFUL. All commits "
          "here share one Ubuntu identity, so the declaration is reviewable, "
          "not verified. This check is post-hoc and gates nothing.")


def selftest() -> int:
    board_a = ("preamble\n## CHIEF - directives\nchief\n"
               "## closure\nclosure v1\n## cfd\ncfd v1\n")
    board_b_own = board_a.replace("cfd v1", "cfd v2")
    board_b_foreign = board_a.replace("cfd v1", "cfd v2").replace("closure v1",
                                                                 "closure v0")
    checks: list[tuple[str, bool, str]] = []

    r = grade(board_a, board_b_own, "cfd", None, False)
    checks.append(("own-section-only edit -> PASS",
                   r["exit"] == EXIT_PASS, f"exit {r['exit']}"))

    r = grade(board_a, board_b_foreign, "cfd", None, False)
    checks.append(("PLANTED foreign-section edit -> REFUSED",
                   r["exit"] == EXIT_REFUSED_FOREIGN_SECTION
                   and "closure" in r["foreign"], f"exit {r['exit']}"))

    r = grade(board_a, board_b_foreign, "cfd", "070da305 heat-transfer revert",
              False)
    checks.append(("PLANTED repair trailer naming an incident -> PASS",
                   r["exit"] == EXIT_PASS, f"exit {r['exit']}"))

    r = grade(board_a, board_b_foreign, "cfd", None, True)
    checks.append(("repair trailer naming NOTHING -> REFUSED",
                   r["exit"] == EXIT_REFUSED_FOREIGN_SECTION, f"exit {r['exit']}"))

    r = grade(board_a, board_b_foreign, None, None, False)
    checks.append(("no Lab-Team trailer -> UNKNOWN",
                   r["exit"] == EXIT_UNKNOWN, f"exit {r['exit']}"))

    r = grade(board_a, board_b_foreign, "not-a-team", None, False)
    checks.append(("unregistered team -> UNKNOWN",
                   r["exit"] == EXIT_UNKNOWN, f"exit {r['exit']}"))

    r = grade(board_a, board_a, "cfd", None, False)
    checks.append(("no board change at all -> PASS",
                   r["exit"] == EXIT_PASS, f"exit {r['exit']}"))

    # chief owns the preamble and the CHIEF section
    board_c = board_a.replace("preamble", "preamble, rewritten")
    r = grade(board_a, board_c, "chief", None, False)
    checks.append(("chief edits the preamble -> PASS",
                   r["exit"] == EXIT_PASS, f"exit {r['exit']}"))
    r = grade(board_a, board_c, "cfd", None, False)
    checks.append(("cfd edits the preamble -> REFUSED",
                   r["exit"] == EXIT_REFUSED_FOREIGN_SECTION, f"exit {r['exit']}"))

    ledger = run_controls()
    checks.append(("planted control reaches RECOGNITION",
                   ledger.kind == control_kind.RECOGNITION, ledger.kind))

    print("=" * 78)
    print("check_board_sections.py --selftest")
    print("=" * 78)
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}   [{detail}]")
    print(ledger.render(0))
    ok = all(c[1] for c in checks)
    print("-" * 78)
    print(f"VERDICT: {'PASS' if ok else 'FAIL'}")
    return EXIT_PASS if ok else EXIT_CONTROL_BROKEN


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--at", help="the commit sha to grade")
    ap.add_argument("--path", default=BOARD_PATH)
    ap.add_argument("--team", help="REVIEWER-ASSERTED attribution, for auditing a "
                                   "commit that predates the `Lab-Team:` trailer. "
                                   "It is a reviewer's claim, printed as such, and "
                                   "it is NOT evidence of who authored the commit; "
                                   "a commit-declared trailer always wins")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.at:
        raise SystemExit("REFUSED: --at <sha> is required (or --selftest)")

    repo = Path(a.repo).resolve()
    message, err = read_message(repo, a.at)
    if message is None:
        print(f"UNKNOWN: could not read the message of {a.at} -- {err}")
        return EXIT_UNKNOWN
    parent = f"{a.at}^"
    after, err_a = read_rev(repo, a.at, a.path)
    before, err_b = read_rev(repo, parent, a.path)
    if after is None:
        print(f"UNKNOWN: could not read {a.at}:{a.path} -- {err_a}")
        return EXIT_UNKNOWN
    if before is None:
        # a root commit, or the board was introduced here
        before = ""

    team, repair, repair_empty = parse_trailers(message)
    asserted_by_reviewer = False
    if team is None and a.team:
        team, asserted_by_reviewer = a.team, True
    result = grade(before, after, team, repair, repair_empty)
    result["team_source"] = ("commit trailer" if not asserted_by_reviewer
                             else "REVIEWER-ASSERTED (--team), not declared by "
                                  "the commit and not evidence of authorship")
    if a.json:
        printable = {k: v for k, v in result.items() if k != "ledger"}
        printable["control_kind"] = result["ledger"].kind
        print(json.dumps(printable, indent=2))
    else:
        render(result, a.at, parent)
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
