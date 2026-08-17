#!/usr/bin/env python3
"""Which surface is allowed to hold a proposal ALONE, and did a record get lost.

WHY THIS EXISTS, AND WHY IT IS NOT THE JOIN (docket D218, D219, D222)
=====================================================================
`scripts/check_docket_surface_agreement.py` joins the two surfaces and compares
`status` on the ids they share. That check is right and it is finished, and its
own docstring names the two classes it can never see:

    ONE SURFACE SILENT   an id on ONE surface only. A join measures agreement
                         between two surfaces; it has nothing to compare when
                         one of them says nothing. 245 ids are in this class.
    BOTH WRONG TOGETHER  an id both surfaces agree on, where the agreed value
                         is false against an artifact on disk. A join measures
                         agreement, not truth.

Both are worse than what the join catches, and the sharpest instance D218 names
turns out to be the first of them rather than a disagreement at all:
`s1-whitened-reinversion-does-the-correction-move-when-sensitivity-is-divided-
out`, 340 core-min, has NO docket record. This module is the check for those two
classes.

THE RULE, DERIVED FROM CODE RATHER THAN INVENTED (D222)
=======================================================
D218 item (2) says no rule exists saying which surface may hold an item alone,
and the join check declined to invent one, correctly: a check that legislates is
not measuring. The rule below is not invented. Every clause is read out of
`chief_engineer.agenda`, and each is stated with the code that makes it true.

    EVERY RECORD OF A DECISION MUST REACH `docket.json`. A surface other than
    the docket may hold an item alone only while that item carries NO decision.
    The moment any non-docket surface records one -- a status past `proposed`,
    or a completed artifact naming the item -- the docket must carry it too,
    and the repair is always to move the record IN, never to promote the other
    surface to a dispatch surface.

Its corollaries, and what makes each one true:

    DOCKET-ONLY IS LEGITIMATE BY CONSTRUCTION.  `agenda.draft_all()` has five
    sources and FOUR of them are code drafters (`draft_tmr_proposals`,
    `draft_gate_proposals`, `draft_ledger_proposals`, `draft_report_proposals`)
    that create a docket record and write no file at all. A docket record with
    no file is the normal output of the system, not a loss. Measured
    2026-08-16: 189 of 189 docket-only records carry a drafter `source_kind`
    (gate 29, report 47, ledger 25, capability 34, measurement 31, challenge
    11, reading 10) or predate the field (2); ZERO carry `source_kind: inbox`.

    DOCKET-ONLY WITH `source_kind: inbox` IS ORPHANED, and is a fault. That
    record entered from a file, and the file is gone: the record can never be
    re-read, repriced or re-evidenced from its source again.

    INBOX-ONLY AND STILL `proposed` IS PENDING, and is not a fault.
    `refresh_docket` merges any inbox id the docket does not hold, so this item
    is one refresh away from the docket and nothing is lost meanwhile.

    INBOX-ONLY WITH A DECIDED STATUS IS LOST, and is the fault this whole check
    exists for. `agenda.set_status` is the only decision-recording function in
    this tree and it writes `docket.json` alone, so a decision that exists only
    in a file exists nowhere any consumer can act on. `docket_view`, what the
    control room serves, has never heard of it. Measured 2026-08-16: SEVEN --
    five `done` and two `approved`.

    INBOX-ONLY AND REFUSED BY `read_inbox` IS BLOCKED, and is a fault of a
    different kind: it is not lost yet, it is UNABLE EVER TO ARRIVE. A file the
    style rails refuse is skipped by every read, so no refresh can ever merge
    it; if it earns a decision tomorrow that decision is lost by construction.

    INBOX-ONLY WHOSE OBJECTIVE COLLIDES WITH A DIFFERENT DOCKET ID IS SHADOWED,
    and is the same kind of fault. `refresh_docket` skips a proposal whose
    normalized objective is already on the docket under another id, so this
    file can never merge either, and the two ids will drift apart forever while
    both look live to a reader.

NOTHING IS DELETED BY ANY OF THIS. Every class is a classification and a named
repair; no clause of the rule says a record should be removed from either
surface. An id on one surface only may be perfectly legitimate -- two whole
classes of it are -- and the check's job is to separate legitimately one-sided
from lost, not to prune.

THE THIRD SURFACE, WHICH IS HOW THIS REACHES `BOTH WRONG TOGETHER`
==================================================================
Some artifacts on disk name the agenda item they were produced for, in a
machine-readable field: `item` or `agenda_entry`. That back-reference is a
THIRD surface, and it is the only one in this tree that is evidence of work
having actually happened rather than a record of what somebody believed. So the
check joins it too: an artifact that names an item the docket still holds OPEN,
where the docket record carries no trace of that work at all -- no `outcome`,
no `progress_note`, no `mission_id` -- is UNABSORBED.

THE REACH OF THAT SECTION IS SMALL AND IS PRINTED RATHER THAN IMPLIED. Measured
2026-08-16 over 506 JSON artifacts under `demo-output/`: FOUR distinct agenda
ids are named by an artifact, 1.5% of the 264 the docket holds. Over those four
it separates cleanly -- the two closed items carry an `outcome` quoting their
artifact's own finding, the two open ones carry nothing -- but four is the
reach, and a section that examined four ids may not be read as a statement
about 264. It says so on every run.

WHAT THIS STILL CANNOT SEE, said plainly rather than left for a reader to find:
an artifact that does NOT carry a back-reference field is invisible here, and
most do not. The 502 artifacts without one could each contradict the docket and
this check would report nothing. Completion is also not read out of the artifact
-- the five back-referencing files share no completion field (`verdict` in three
of five, and the one that records `ALL_DONE` records it nested inside
`stage_two_lhs`) -- so this section reports that the docket has no trace of work
an artifact proves happened. It never asserts the item is finished. That is a
claim about what the work found, and it belongs to whoever reads the artifact.

THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (defect class B1)
====================================================================
    PASS      at least one id was classified, and no id is in a fault class
    FAIL      at least one id is LOST, BLOCKED, SHADOWED, ORPHANED or
              UNABSORBED
    UNKNOWN   a surface could not be read, or zero ids were classified

An empty artifact scan does NOT make the run UNKNOWN -- the one-sided sections
stand on their own -- but it is never reported as agreement either: the reach
line prints the count it examined, and zero back-references prints as "no
statement available" rather than as a clean section. The same discipline
applies sectionally that class B1 applies to the whole run.

EXIT CONTRACT: 0 PASS, 1 FAIL, 3 UNKNOWN -- `scripts/lab_check.py`'s contract.

READ ONLY. This module opens files for reading and writes nothing anywhere. It
imports `chief_engineer.agenda` for one purpose only, `read_inbox`, because the
BLOCKED class is defined as "the style rails refuse this file" and
reimplementing those rails here would let the two drift apart -- the exact
defect the whole check is about. `read_inbox` writes nothing.
"""

from __future__ import annotations

import argparse
import json
import os
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

REPO_ROOT = Path(__file__).resolve().parents[1]
# MOVE_MAP s4: SPLIT-2 by design.  `AGENDA` follows R23 to `research/`;
# `ARTIFACTS` is the whole `demo-output/` archive, which R10-R12 thin but
# do not relocate as a unit, so it is bound as a non-moving name.
AGENDA = lab_paths.AGENDA
ARTIFACTS = lab_paths.DEMO_OUTPUT

#: The status that means "no decision has been taken yet". Everything else in
#: `agenda.STATUSES` -- approved, approved-queued, dismissed, done -- is a
#: decision, and a decision is what may not live on the inbox alone.
UNDECIDED = "proposed"

#: A docket status that means the item is closed and needs nothing further.
CLOSED = ("done", "dismissed")

#: Fields whose presence on a docket record means the docket has absorbed some
#: trace of work actually done on the item.
TRACE_FIELDS = ("outcome", "progress_note", "mission_id", "measured_core_min")

#: Keys under which an artifact names the agenda item it was produced for.
BACKREF_KEYS = ("item", "agenda_entry")

#: The fault classes, each with the repair the rule names for it. A class with
#: no stated repair is a complaint, not a check.
FAULTS = {
    # THE REMEDY PRINTED HERE USED TO NAME `set_status` AND WAS A SILENT
    # NO-OP ON EVERY ID THIS CLASS REPORTS (D261). `set_status` iterates
    # `load_docket()` and returns None for an id it does not find -- and LOST
    # means precisely that the docket has no record of the id. An operator who
    # followed the old instruction literally got no exception, no message and
    # no change, then saw the same ids reported on the next run and concluded
    # the CHECK was broken rather than the remedy. Reproduced 2026-08-16 on a
    # scratch copy of the agenda: `set_status(<a real LOST id>, "done",
    # outcome=...)` returned None with docket.json's sha256 unchanged.
    # `refresh_docket()` is the call that works, and it was verified by
    # execution on all seven at once rather than argued: every one is read by
    # `read_inbox`, all seven are reached by `draft_all()`, none collides by id
    # or by normalized objective, and one call moved 0 of 7 to 7 of 7.
    "LOST": "a decision recorded ONLY in the file; ONE `refresh_docket()` "
            "merges every id in this class into docket.json -- NOT "
            "`set_status`, which returns None for an id the docket does not "
            "yet hold and changes nothing",
    "BLOCKED": "the style rails refuse this file, so no refresh can ever "
               "merge it; repair the file or withdraw it",
    "SHADOWED": "its objective already belongs to another docket id, so "
                "refresh_docket skips it forever; merge the two or reword",
    "ORPHANED": "entered from a file that no longer exists, so the record can "
                "never be re-read from its source; restore or note the file",
    # The OPPOSITE call to LOST's, and the two must not be confused. These ids
    # ARE on the docket, so `set_status` reaches them; and `refresh_docket()`
    # cannot help, because it carries only what the FILE holds and the
    # evidence here lives in an ARTIFACT no carry reaches. Verified 2026-08-16
    # on a scratch copy: a refresh left both without an outcome, both inbox
    # files carry none, and `set_status` returned a record for both.
    "UNABSORBED": "an artifact on disk names this item and the docket record "
                  "carries no trace of that work; READ THE ARTIFACT, then "
                  "`set_status(<id>, <status>, outcome=...)` -- a "
                  "`refresh_docket()` cannot fix this class, it carries only "
                  "what the inbox FILE holds",
}
LEGITIMATE = {
    "PENDING": "inbox-only and undecided; the next refresh_docket merges it",
    "DRAFTED": "docket-only from a code drafter, which writes no file; this "
               "is the normal output of the system",
}


class SurfaceError(Exception):
    """A surface could not be read. UNKNOWN, never FAIL: a statement about the
    instrument's reach, not about the lab."""


def load_docket(path: Path) -> dict[str, dict]:
    """id -> record from docket.json. Raises SurfaceError if unreadable."""
    if not path.is_file():
        raise SurfaceError(f"docket not found at {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise SurfaceError(f"docket at {path} would not parse: {exc}") from exc
    records = data.get("proposals") if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise SurfaceError(f"docket at {path} holds no proposal list")
    return {str(r["id"]): r for r in records
            if isinstance(r, dict) and r.get("id")}


def load_inbox(root: Path) -> dict[str, dict]:
    """id -> record from proposals/*.json, read RAW.

    A file that will not parse is UNKNOWN for the whole run rather than a
    skipped row: a coverage check that quietly drops the file it could not read
    reports coverage over a smaller set than it claims, which is the silent
    zero this lab ranks worst.
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


def refused_ids(agenda_dir: Path) -> set[str]:
    """The ids `agenda.read_inbox` refuses outright, asked of the module itself.

    Imported rather than reimplemented on purpose: BLOCKED is DEFINED as "the
    rails refuse it", so a second copy of the rails here would drift from the
    first and this check would be measuring its own opinion. Raises
    SurfaceError if the module cannot be reached, which is UNKNOWN.
    """
    sdk = REPO_ROOT / "sdk"
    if str(sdk) not in sys.path:
        sys.path.insert(0, str(sdk))
    try:
        from chief_engineer import agenda  # noqa: PLC0415
    except Exception as exc:  # pragma: no cover - import failure is UNKNOWN
        raise SurfaceError(f"chief_engineer.agenda would not import: "
                           f"{exc}") from exc
    saved = os.environ.get("CERTONOMOUS_AGENDA_DIR")
    os.environ["CERTONOMOUS_AGENDA_DIR"] = str(agenda_dir)
    try:
        agenda.read_inbox()
        return {str(row.get("id") or row.get("file"))
                for row in agenda.refused_inbox()}
    finally:
        if saved is None:
            os.environ.pop("CERTONOMOUS_AGENDA_DIR", None)
        else:
            os.environ["CERTONOMOUS_AGENDA_DIR"] = saved


def normalize_objective(text: str) -> str:
    """Byte-for-byte `agenda.normalize_objective`, and it must stay so: the
    SHADOWED class is defined by the key `refresh_docket` collides on."""
    return " ".join(str(text or "").split()).strip().casefold()


def scan_artifacts(root: Path) -> tuple[dict[str, list[str]], int, int]:
    """agenda id -> artifact paths that name it, plus (scanned, unreadable).

    The unreadable count is returned rather than swallowed because every
    unreadable artifact is a reduction in this section's reach, and a reach
    that shrinks silently is how a check starts reporting agreement over a set
    it never examined.
    """
    named: dict[str, list[str]] = {}
    scanned = unreadable = 0
    if not root.is_dir():
        return named, scanned, unreadable
    for path in sorted(root.rglob("*.json")):
        if "agenda" in path.parts:
            continue
        scanned += 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError, UnicodeDecodeError):
            unreadable += 1
            continue
        if not isinstance(data, dict):
            continue
        for key in BACKREF_KEYS:
            value = data.get(key)
            if not isinstance(value, str) or not value:
                continue
            # `agenda_entry` names the proposal FILE; `item` names the id.
            # Both reduce to an id: the file's stem is its id by construction
            # (`load_inbox` falls back to the stem, and every live file's id
            # equals its stem), so taking the stem is not a guess.
            item_id = value.rsplit("/", 1)[-1]
            if item_id.endswith(".json"):
                item_id = item_id[:-len(".json")]
            named.setdefault(item_id, []).append(
                str(path.relative_to(root.parent)
                    if root.parent in path.parents else path))
    return named, scanned, unreadable


def classify(inbox: dict[str, dict], docket: dict[str, dict],
             refused: set[str], named: dict[str, list[str]]) -> dict:
    """The whole finding, as data. Pure: no file system, no clock, no argv.

    Kept separate from every I/O path so the controls can plant a LOST id, a
    PENDING id and a DRAFTED id as plain dictionaries, and never have to write
    into the tree the check is about.
    """
    docket_objectives: dict[str, str] = {}
    for item_id, record in docket.items():
        docket_objectives.setdefault(
            normalize_objective(record.get("objective", "")), item_id)

    rows: list[dict] = []
    for item_id in sorted(set(inbox) - set(docket)):
        record = inbox[item_id]
        status = str(record.get("status") or UNDECIDED)
        collided = docket_objectives.get(
            normalize_objective(record.get("objective", "")))
        if item_id in refused:
            klass, detail = "BLOCKED", "refused by read_inbox's style rails"
        elif collided and collided != item_id:
            klass, detail = "SHADOWED", f"objective already held by {collided}"
        elif status != UNDECIDED:
            klass, detail = "LOST", f"file records {status!r}, docket has "\
                                    f"no record at all"
        else:
            klass, detail = "PENDING", "undecided; next refresh merges it"
        rows.append({"id": item_id, "surface": "inbox", "class": klass,
                     "status": status, "detail": detail,
                     "core_min": _price(record)})

    for item_id in sorted(set(docket) - set(inbox)):
        record = docket[item_id]
        kind = str(record.get("source_kind") or "")
        if kind == "inbox":
            klass, detail = "ORPHANED", "source_kind is inbox but no file exists"
        else:
            klass, detail = "DRAFTED", f"drafted by code (source_kind "\
                                       f"{kind or '<absent>'})"
        rows.append({"id": item_id, "surface": "docket", "class": klass,
                     "status": str(record.get("status") or ""),
                     "detail": detail, "core_min": _price(record)})

    unabsorbed: list[dict] = []
    for item_id, paths in sorted(named.items()):
        record = docket.get(item_id)
        if record is None:
            if item_id not in inbox:
                continue  # an artifact naming something neither surface knows
            unabsorbed.append({
                "id": item_id, "status": "<not on the docket>",
                "artifacts": sorted(paths),
                "detail": "an artifact names this item and the docket has "
                          "never heard of it"})
            continue
        status = str(record.get("status") or "")
        if status in CLOSED:
            continue
        traces = [f for f in TRACE_FIELDS if record.get(f) not in (None, "")]
        if traces:
            continue
        unabsorbed.append({
            "id": item_id, "status": status, "artifacts": sorted(paths),
            "detail": f"docket holds it {status!r} and carries none of "
                      f"{list(TRACE_FIELDS)}, while an artifact names it"})

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["class"]] = counts.get(row["class"], 0) + 1
    if unabsorbed:
        counts["UNABSORBED"] = len(unabsorbed)

    faults = [r for r in rows if r["class"] in FAULTS]
    total_classified = len(rows) + len(unabsorbed)

    if not rows and not unabsorbed:
        verdict = UNKNOWN
        reason = ("zero ids were classified: nothing was examined, and an "
                  "empty selection is never a pass")
    elif faults or unabsorbed:
        verdict = FAIL
        reason = (f"{len(faults)} one-sided ids are in a fault class and "
                  f"{len(unabsorbed)} ids have an artifact the docket has not "
                  f"absorbed")
    else:
        verdict = PASS
        reason = (f"all {len(rows)} one-sided ids are legitimately one-sided "
                  f"and every back-referenced item is absorbed")

    return {
        "verdict": verdict, "reason": reason,
        "inbox_ids": len(inbox), "docket_ids": len(docket),
        "shared": len(set(inbox) & set(docket)),
        "one_sided": len(rows), "classified": total_classified,
        "counts": counts, "rows": rows, "unabsorbed": unabsorbed,
        "faults": [r["id"] for r in faults],
    }


def _price(record: dict) -> float:
    for key in ("measured_core_min", "est_core_min"):
        value = record.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def render(result: dict, scanned: int, unreadable: int, backrefs: int) -> str:
    """The frame, printed on every run whatever the verdict."""
    counts = result["counts"]
    lines = [
        "FRAME (counted before the verdict; both agenda surfaces read RAW)",
        f"  inbox ids (proposals/*.json)   {result['inbox_ids']}",
        f"  docket ids (docket.json)       {result['docket_ids']}",
        f"  shared ids (the JOIN's job,    {result['shared']}",
        "    not this check's)",
        f"  ONE-SIDED ids, this check's    {result['one_sided']}",
        "    population",
        "",
        "CLASSIFICATION (the rule is in this module's docstring; every clause",
        "of it is read out of chief_engineer.agenda, none of it invented)",
    ]
    for klass in ("LOST", "BLOCKED", "SHADOWED", "ORPHANED", "UNABSORBED",
                  "PENDING", "DRAFTED"):
        if klass not in counts:
            continue
        mark = "FAULT " if klass in FAULTS else "ok    "
        note = FAULTS.get(klass) or LEGITIMATE.get(klass, "")
        lines.append(f"  {mark}{klass:<11} {counts[klass]:>4}   {note}")
    lines.append("")
    lines.append("ARTIFACT BACK-REFERENCE, the third surface -- this is the "
                 "only")
    lines.append("section that can see BOTH SURFACES WRONG TOGETHER, and its "
                 "reach")
    lines.append("is small and is printed rather than implied")
    lines.append(f"  artifacts scanned under demo-output   {scanned}")
    lines.append(f"  unreadable (reach lost)               {unreadable}")
    lines.append(f"  distinct agenda ids named by one      {backrefs}")
    if not backrefs:
        lines.append("  NO STATEMENT AVAILABLE from this section: zero "
                     "back-references")
        lines.append("  were found, so it examined nothing. That is not "
                     "agreement.")
    else:
        share = 100.0 * backrefs / max(result["docket_ids"], 1)
        lines.append(f"  which is {share:.1f}% of the docket: this section is "
                     f"a statement")
        lines.append(f"  about {backrefs} ids, never about "
                     f"{result['docket_ids']}")
    for row in result["unabsorbed"]:
        lines.append(f"  UNABSORBED  {row['id']}")
        lines.append(f"              {row['detail']}")
        for path in row["artifacts"]:
            lines.append(f"              artifact: {path}")

    faulty = [r for r in result["rows"] if r["class"] in FAULTS]
    if faulty:
        lines.append("")
        lines.append("EVERY ONE-SIDED FAULT, priced, worst first")
        for row in sorted(faulty, key=lambda r: (-r["core_min"], r["id"])):
            lines.append(f"  {row['core_min']:>9.1f} core-min  "
                         f"{row['class']:<9} {row['status']:<10} {row['id']}")
            lines.append(f"  {'':>9}             {row['detail']}")
    lines.append("")
    lines.append(f"VERDICT: {result['verdict']}  {result['reason']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Classify every proposal id that lives on ONE surface "
                    "only, and join the docket to artifacts that name their "
                    "own agenda item. Reports; never reconciles.")
    parser.add_argument("--agenda", default=str(AGENDA),
                        help="agenda directory holding docket.json and "
                             "proposals/ (default: the repository's)")
    parser.add_argument("--artifacts", default=str(ARTIFACTS),
                        help="root scanned for artifacts that back-reference "
                             "an agenda item (default: demo-output)")
    parser.add_argument("--json", action="store_true",
                        help="emit the finding as JSON after the frame")
    args = parser.parse_args(argv)

    agenda_dir = Path(args.agenda)
    try:
        inbox = load_inbox(agenda_dir / "proposals")
        docket = load_docket(agenda_dir / "docket.json")
        refused = refused_ids(agenda_dir)
    except SurfaceError as exc:
        print("FRAME (counted before the verdict)")
        print(f"  a surface could not be read: {exc}")
        print("")
        print(f"VERDICT: {UNKNOWN}  a surface could not be read, so nothing "
              f"was classified: {exc}")
        return EXIT[UNKNOWN]

    named, scanned, unreadable = scan_artifacts(Path(args.artifacts))
    known = set(inbox) | set(docket)
    named = {k: v for k, v in named.items() if k in known}
    result = classify(inbox, docket, refused, named)
    print(render(result, scanned, unreadable, len(named)))
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    return EXIT[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
