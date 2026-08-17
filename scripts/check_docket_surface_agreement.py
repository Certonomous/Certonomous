#!/usr/bin/env python3
"""The two surfaces that both call themselves the docket, joined on id.

WHY THIS EXISTS (docket D218, measured 2026-08-15; the collision is D38 item 5,
and the same measurement was already sitting in MEMORY_ARCHITECTURE as D-1 since
2026-08-10)
=============================================================================
This lab keeps proposal status in two tracked places:

    INBOX    demo-output/website/agenda/proposals/*.json   one file per item
    DOCKET   demo-output/website/agenda/docket.json        one record per item

Joined on `id`, 34 of 75 shared ids disagreed on `status` -- 45.3% -- on the one
field that decides whether an agent starts a run. In one direction that
advertises finished work for dispatch; in the other it hides work the owner has
already authorised. Nothing joined the two surfaces: the two scripts that read
the inbox (`calibration_scorecard`, `add_proposals_supervisor_review_2026_08_07`)
never load the docket, and the docket's own module never re-reads a file once an
id has been merged.

WHAT IT CHECKS, AND WHAT IT DELIBERATELY DOES NOT
=================================================
It checks ONE thing: for every id present in BOTH surfaces, the two `status`
values are equal, and both are inside the closed status vocabulary that
`chief_engineer.agenda.STATUSES` declares.

It does NOT adjudicate. A checker cannot repair a disagreement it cannot
adjudicate, so a disagreement is reported with both values and both prices and
left standing. It also does not judge the THIRD CLASS -- ids that exist on only
one surface. Those are counted and printed on every run because the frame is
meaningless without them, but they are not faults here: nothing in this lab has
ever ruled which surface is allowed to hold an item alone, and a check that
invented that rule would be legislating rather than measuring.

Nor can it see the class where BOTH surfaces are wrong together. Two surfaces
agreeing that an item is `proposed` reads PASS here even when a completed report
for it sits on disk. That is a real hole and it is named rather than hidden:
this instrument measures agreement, not truth.

THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (defect class B1)
===================================================================
Zero shared ids is UNKNOWN with a reason, never PASS. A join that matched
nothing has examined nothing, and "no disagreement was found" over an empty
selection is the silent-zero sweep this lab ranks as its worst defect class --
found three separate times in this tree on 2026-08-15 alone. The same applies to
an unreadable surface: a docket that will not parse, an inbox directory that is
not there, or a proposal file that is not JSON, all report UNKNOWN. Only a join
that actually compared at least one pair may say PASS.

    PASS      at least one shared id, every shared id agrees, every status in
              both surfaces is inside the vocabulary
    FAIL      at least one shared id disagrees, or a status is outside the
              vocabulary
    UNKNOWN   nothing was compared, or a surface could not be read

EXIT CONTRACT: 0 PASS, 1 FAIL, 3 UNKNOWN -- `scripts/lab_check.py`'s published
contract, so this check is readable by the runner without an adapter.

READ ONLY. This module opens files for reading and writes nothing anywhere. It
is safe to run against the live tree with ten agents working in it, which is
`lab_check.py` predicate P4.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[1]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}

#: The closed status vocabulary, copied from `chief_engineer.agenda.STATUSES`
#: rather than imported, so that this check does not go green by importing a
#: module somebody widened. `agenda.read_inbox` silently coerces anything
#: outside this set to "proposed", which means an out-of-vocabulary value in a
#: file is invisible to every consumer that goes through the module and visible
#: only to a reader that opens the raw file -- exactly what an agent does.
STATUSES = ("proposed", "approved", "approved-queued", "dismissed", "done")

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENDA = lab_paths.AGENDA


class SurfaceError(Exception):
    """A surface could not be read. This is UNKNOWN, never FAIL: it is a
    statement about the instrument's reach, not about the lab."""


def load_docket(path: Path) -> dict[str, dict]:
    """id -> record, from docket.json. Raises SurfaceError if unreadable."""
    if not path.is_file():
        raise SurfaceError(f"docket not found at {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise SurfaceError(f"docket at {path} would not parse: {exc}") from exc
    records = data.get("proposals") if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise SurfaceError(f"docket at {path} holds no proposal list")
    out: dict[str, dict] = {}
    for record in records:
        if isinstance(record, dict) and record.get("id"):
            out[str(record["id"])] = record
    return out


def load_inbox(root: Path) -> dict[str, dict]:
    """id -> record, from proposals/*.json. Raises SurfaceError if unreadable.

    A file that will not parse is UNKNOWN for the whole run rather than a
    skipped row: a join that quietly dropped the file it could not read would
    report agreement over a smaller set than it claims.
    """
    if not root.is_dir():
        raise SurfaceError(f"inbox directory not found at {root}")
    out: dict[str, dict] = {}
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise SurfaceError(f"{path.name} would not parse: {exc}") from exc
        if not isinstance(data, dict):
            raise SurfaceError(f"{path.name} is not a JSON object")
        out[str(data.get("id") or path.stem)] = data
    return out


def _price(inbox_record: dict, docket_record: dict) -> float:
    """Core-minutes for one item. The inbox is asked first because it is where
    a reprice is filed; the docket answers when the file carries no number."""
    for record in (inbox_record, docket_record):
        value = record.get("est_core_min")
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def compare(inbox: dict[str, dict], docket: dict[str, dict]) -> dict:
    """The whole finding, as data. Pure: no file system, no clock, no argv.

    Kept separate from every I/O path on purpose. The controls in
    `sdk/tests/test_docket_surface_agreement.py` plant a disagreement and a
    one-sided id by calling this with dictionaries, so the positive control
    never has to write into the tree it is checking.
    """
    shared = sorted(set(inbox) & set(docket))
    disagreements = []
    for item_id in shared:
        inbox_status = str(inbox[item_id].get("status") or "")
        docket_status = str(docket[item_id].get("status") or "")
        if inbox_status != docket_status:
            disagreements.append({
                "id": item_id,
                "inbox": inbox_status,
                "docket": docket_status,
                "core_min": _price(inbox[item_id], docket[item_id]),
            })
    bad_vocab = []
    for surface, records in (("inbox", inbox), ("docket", docket)):
        for item_id, record in sorted(records.items()):
            status = str(record.get("status") or "")
            if status not in STATUSES:
                bad_vocab.append({"id": item_id, "surface": surface,
                                  "status": status})

    if not shared:
        verdict = UNKNOWN
        reason = ("zero shared ids: the join compared nothing, so no "
                  "statement about agreement is available. An empty "
                  "selection is never a pass")
    elif disagreements or bad_vocab:
        verdict = FAIL
        reason = (f"{len(disagreements)} of {len(shared)} shared ids disagree "
                  f"on status; {len(bad_vocab)} status values are outside the "
                  f"vocabulary")
    else:
        verdict = PASS
        reason = (f"all {len(shared)} shared ids agree on status, and every "
                  f"status on both surfaces is inside the vocabulary")

    return {
        "verdict": verdict,
        "reason": reason,
        "inbox_ids": len(inbox),
        "docket_ids": len(docket),
        "shared": len(shared),
        "agreeing": len(shared) - len(disagreements),
        "disagreeing": len(disagreements),
        "inbox_only": sorted(set(inbox) - set(docket)),
        "docket_only": sorted(set(docket) - set(inbox)),
        "disagreements": disagreements,
        "bad_vocab": bad_vocab,
    }


def _direction_totals(disagreements: list[dict]) -> list[tuple[str, int, float]]:
    """(inbox_status -> docket_status, count, core-min), busiest first.

    The two directions cost different things and are never summed: finished
    work advertised as available wastes a whole dispatch, and authorised work
    shown as speculative wastes the authorisation. One number over both hides
    which of those is happening.
    """
    buckets: dict[str, list] = {}
    for row in disagreements:
        key = f"{row['inbox']} -> {row['docket']}"
        entry = buckets.setdefault(key, [0, 0.0])
        entry[0] += 1
        entry[1] += row["core_min"]
    return sorted(((k, v[0], v[1]) for k, v in buckets.items()),
                  key=lambda t: (-t[1], t[0]))


def render(result: dict) -> str:
    """The frame, printed on every run whatever the verdict."""
    lines = [
        "FRAME (counted before the verdict, both surfaces read raw)",
        f"  inbox ids (proposals/*.json)   {result['inbox_ids']}",
        f"  docket ids (docket.json)       {result['docket_ids']}",
        f"  shared ids                     {result['shared']}",
        f"    agreeing on status           {result['agreeing']}",
        f"    DISAGREEING on status        {result['disagreeing']}",
        f"  present in one surface only    "
        f"{len(result['inbox_only']) + len(result['docket_only'])}"
        f"  (inbox-only {len(result['inbox_only'])}, "
        f"docket-only {len(result['docket_only'])})",
        "  the one-sided ids are COUNTED, NOT JUDGED: no rule exists saying",
        "  which surface may hold an item alone, and this check does not "
        "invent one",
    ]
    if result["shared"]:
        share = 100.0 * result["disagreeing"] / result["shared"]
        lines.append(f"  disagreement rate              {share:.1f}%")
    if result["disagreements"]:
        lines.append("")
        lines.append("BY DIRECTION (inbox status -> docket status), never summed")
        for key, count, core_min in _direction_totals(result["disagreements"]):
            lines.append(f"  {key:<34} n={count:<4} {core_min:>9.1f} core-min")
        lines.append("")
        lines.append("EVERY DISAGREEMENT, priced")
        for row in sorted(result["disagreements"],
                          key=lambda r: (-r["core_min"], r["id"])):
            lines.append(f"  {row['core_min']:>9.1f} core-min  "
                         f"inbox={row['inbox']:<16} docket={row['docket']:<16} "
                         f"{row['id']}")
    if result["bad_vocab"]:
        lines.append("")
        lines.append("STATUS VALUES OUTSIDE THE CLOSED VOCABULARY "
                     f"{list(STATUSES)}")
        for row in result["bad_vocab"]:
            lines.append(f"  {row['surface']:<7} {row['status']!r:<16} "
                         f"{row['id']}")
    lines.append("")
    lines.append(f"VERDICT: {result['verdict']}  {result['reason']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Join the proposal inbox to docket.json on id and compare "
                    "status. Reports; never reconciles.")
    parser.add_argument("--agenda", default=str(AGENDA),
                        help="agenda directory holding docket.json and "
                             "proposals/ (default: the repository's)")
    parser.add_argument("--json", action="store_true",
                        help="emit the finding as JSON after the frame")
    args = parser.parse_args(argv)

    agenda = Path(args.agenda)
    try:
        inbox = load_inbox(agenda / "proposals")
        docket = load_docket(agenda / "docket.json")
    except SurfaceError as exc:
        print("FRAME (counted before the verdict, both surfaces read raw)")
        print(f"  a surface could not be read: {exc}")
        print("")
        print(f"VERDICT: {UNKNOWN}  a surface could not be read, so nothing "
              f"was compared: {exc}")
        return EXIT[UNKNOWN]

    result = compare(inbox, docket)
    print(render(result))
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    return EXIT[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
