#!/usr/bin/env python3
"""Score this lab's compute forecasts against what the runs actually cost.

WHY THIS EXISTS. `docs/CAPABILITY_STRATEGY.md` §4 proposes a rule:

    Cost model v2: per-family scaling laws with confidence bands;
    forecasts auto-approve when 3-for-3 within 20%.

That rule needs a scorecard, and a scorecard needs pairs — an estimate and the
measured cost of the same work. This script builds those pairs from the proposal
corpus and reports the hit rate. It is deliberately a GENERATOR rather than a
document: a calibration figure quoted into prose is stale the next time a run
finishes, which is L-79.

    python3 scripts/calibration_scorecard.py           # human-readable, stamped
    python3 scripts/calibration_scorecard.py --json    # for a doc build or a test

WHAT IT MEASURED ON ITS FIRST RUN, and the finding is about the record rather
than about anyone's estimating: **the pairs are almost all missing.** 19
proposals are marked `done`; 3 carry `measured_core_min`. So sixteen closed
pieces of work recorded no actual cost, and several of those costs are known and
written down elsewhere — the S1 inversion's 335.98 core-min and the
objective-repair run's 424.80 both sit in campaign records that the proposal file
never learned about. The number exists; the loop was never closed.

The consequence is the point: **§4's auto-approve rule cannot run at all**, not
because forecasting is hard but because the lab does not write the outturn back
to the thing that forecast it. A rule that cannot be evaluated reads exactly like
a rule that is being followed.

This script does not fix that. It measures it, and it says how far from
runnable the rule is, so the gap is a number instead of an impression.

FRAME. `demo-output/website/agenda/proposals/*.json`, every file, no filter. Not
`grep -r`: in this environment `grep` execs `ugrep --ignore-files` and honours
`.gitignore` (L-75). Pairs come only from files carrying BOTH `est_core_min` and
`measured_core_min` — a pair reconstructed by hand from a campaign record would
be a different measurement and is not made here.

THREE DEFECTS FIXED 2026-08-14, and the third is the one worth reading.

(1) INTAKE IS NOW RECONCILED, not spot-patched. `agenda.read_inbox()` refuses
    files that trip its schema and style rails and records each refusal in
    `agenda.refused_inbox()` — a ledger written expressly against "a filter
    nobody can see", and then wired to no caller outside `sdk/tests/`. So the
    refusals were counted into a ledger nobody read, which is the same silence
    one indirection further out. This scorecard is the lab's grading
    instrument and is now that caller. It does NOT re-admit refused files;
    admission is `agenda`'s judgement and stays there. What it adds is an
    ARITHMETIC INVARIANT: files on disk == loaded + refused. A future refusal
    path that forgets to write the ledger cannot hide behind a plausible
    count — it shows up as an UNRECONCILED delta with a nonzero exit. The
    same silence is fixed once, at the shape, rather than a fourth time per
    record: this defect was already fixed for one record on 2026-08-07 and
    recurred with three more (D67).

(2) A FORECAST OF ZERO THAT COST ZERO IS NOT A MISS, and is not a hit either.
    See `EXACT_ZERO` below.

(3) "THREE CONSECUTIVE" IS EVALUATED IN TIME. It used to be evaluated over
    `sorted(glob(...))[-3:]` — filename order — so the rule about the lab's
    three most recent forecasts was scored on three records chosen by
    alphabet. The two sets were fully DISJOINT at `e9a02d31`. See `DATE_FIELD`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROPOSALS = REPO / "demo-output/website/agenda/proposals"

#: §4's bar. A forecast counts as a hit when |measured - est| / measured <= this.
TOLERANCE = 0.20

#: §4 asks for three consecutive hits before forecasts auto-approve.
CONSECUTIVE_HITS_REQUIRED = 3

#: The record's own dated field, used to put "consecutive" in time order.
#:
#: WHY `created_at` AND NOT ANOTHER. It is the only dated field carried by
#: every record: at e9a02d31 all 131 proposals have it, against `decided_at`
#: on 25, `completed_at` on 3 and `executed_at` on 2. It is also the right
#: clock for this rule on the merits — §4 gates FORECASTS, and a forecast is
#: made when the proposal is written, so "three consecutive forecasts" means
#: three consecutive in the order they were forecast. `completed_at` was the
#: considered alternative and is rejected twice over: it orders by when the
#: answer arrived rather than when the guess was made, and it is absent on 8
#: of the 11 scoreable pairs, which would put the rule's own window mostly
#: inside the UNDATED class below and make it unevaluable.
DATE_FIELD = "created_at"


def _head() -> tuple[str, bool]:
    def run(*a: str) -> str:
        return subprocess.run(a, cwd=REPO, capture_output=True, text=True).stdout
    return (run("git", "rev-parse", "--short", "HEAD").strip() or "UNKNOWN",
            bool(run("git", "status", "--porcelain").strip()))


def load() -> tuple[list[dict], list[str]]:
    """Every proposal, plus the ones that would not parse.

    Unparseable files are RETURNED, not skipped. A scorecard that silently drops
    the files it cannot read reports a clean rate over the subset that happened
    to be well-formed -- the fail-open shape this lab keeps finding in its own
    instruments.
    """
    records, broken = [], []
    for path in sorted(PROPOSALS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            broken.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        data["_file"] = path.name
        records.append(data)
    return records, broken


#: The third class, and the whole of defect (2). A forecast of 0 core-min that
#: measured 0 core-min is not a MISS -- the instrument used to print it `inf%
#: off`, scoring the most exactly-right forecast available as an infinite
#: error, because relative error divides by a measured cost of zero. It is
#: also NOT A HIT, and that is the judgement worth defending.
#:
#: WHAT WAS REJECTED: counting them as hits. It is superficially the fair
#: reading -- 0 forecast, 0 spent, perfect. It fails on what the rule is FOR.
#: §4 auto-approves compute budget once "per-family scaling laws" have proved
#: themselves 3-for-3; a zero-compute record exercises no scaling law and
#: clears any tolerance band trivially, since every band contains 0. Counting
#: them as hits would move the headline from 3-of-11 to 5-of-11 on two records
#: that priced no compute, and -- far worse -- would make the auto-approve
#: gate reachable by filing three zero-cost proposals in a row. A gate that
#: can be opened by work that never tested it is not a gate.
#:
#: So: reported by name, counted in neither numerator nor denominator, and
#: never eligible to fill a slot in the consecutive window. The cost of this
#: choice is stated rather than hidden: removing them from the denominator
#: RAISES the headline from 3-of-11 (27%) to 3-of-9 (33%). Both are printed.
EXACT_ZERO = "exact-zero"

#: A record whose forecast was nonzero but which measured zero. Relative error
#: is undefined here too, but this is a genuine forecasting error -- the lab
#: budgeted compute for work that cost none -- so it is a MISS with no
#: percentage, never an `inf%`. Distinct from EXACT_ZERO on purpose.
ZERO_MEASURED = "zero-measured"

#: A record carrying no usable DATE_FIELD. Three-valued by construction: it is
#: neither "earliest" nor "latest", because we do not know. It is named,
#: excluded from the ordered sequence, and -- since an undated record could
#: sort anywhere, including into the last three -- its mere existence makes
#: the consecutive verdict UNKNOWN rather than False. Silently sorting these
#: to one end would be the instrument inventing a fact about the record.
UNDATED = "undated"


def _sort_key(record: dict) -> str | None:
    """The record's own dated field, or None. Never a fabricated default."""
    raw = record.get(DATE_FIELD)
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def score(records: list[dict]) -> dict:
    done = [r for r in records if r.get("status") == "done"]
    pairs, unpaired = [], []
    for r in done:
        est, meas = r.get("est_core_min"), r.get("measured_core_min")
        if est in (None, "") or meas in (None, ""):
            unpaired.append(r["_file"][:-5])
            continue
        est, meas = float(est), float(meas)
        # Error is relative to the MEASURED cost, not the estimate: the question
        # a budget holder asks is "how wrong was the forecast about what this
        # actually took", and dividing by the estimate flatters a low guess.
        if meas == 0 and est == 0:
            klass, err, hit = EXACT_ZERO, None, None
        elif meas == 0:
            klass, err, hit = ZERO_MEASURED, None, False
        else:
            err = abs(meas - est) / meas
            klass, hit = "graded", err <= TOLERANCE
        pairs.append({"id": r["_file"][:-5], "est": est, "measured": meas,
                      "rel_error": err, "hit": hit, "class": klass,
                      "dated": _sort_key(r)})

    # Defect (3). "Consecutive" is a claim about time, so it is evaluated in
    # time. `pairs` arrives in filename order because `load()` walks a sorted
    # glob; taking [-3:] off that scored whichever three ids sort last in the
    # alphabet. At e9a02d31 those were three w4-* records while the three most
    # recent forecasts were s1/kfamily/pydafoam -- a fully disjoint set.
    graded = [p for p in pairs if p["class"] != EXACT_ZERO]
    undated = [p for p in graded if p["dated"] is None]
    dated = sorted((p for p in graded if p["dated"] is not None),
                   key=lambda p: p["dated"])
    window = dated[-CONSECUTIVE_HITS_REQUIRED:]

    if len(dated) < CONSECUTIVE_HITS_REQUIRED:
        satisfied = None          # not enough dated evidence to say
    elif undated:
        satisfied = None          # an undated record could sort into the window
    else:
        satisfied = all(p["hit"] for p in window)

    # THE WINDOW IS THE LAST THREE *RECORDED*, WHICH IS NOT THE LAST THREE.
    # Ordering by date fixes which recorded pairs get scored; it cannot
    # conjure the ones that were never recorded. If a done record newer than
    # the window's start carries no measured cost, then work the lab finished
    # more recently than the scored evidence is missing from it, and the rule
    # is being evaluated over a tail with holes in it. At e9a02d31 exactly one
    # such record exists (a3-transonic-adjoint, 2026-08-10), and it is newer
    # than every pair in the corpus. Reported, because a verdict computed over
    # a tail that is not the tail should say so.
    start = window[0]["dated"] if window else None
    displaced = sorted(
        r["_file"][:-5] for r in done
        if r["_file"][:-5] in unpaired
        and start is not None
        and str(r.get(DATE_FIELD) or "") >= start)

    hits = [p for p in graded if p["hit"]]
    return {
        "proposals": len(records),
        "done": len(done),
        "window_displaced_by": displaced,
        "pairs": pairs,
        "graded": [p["id"] for p in graded],
        "exact_zero": [p["id"] for p in pairs if p["class"] == EXACT_ZERO],
        "undated": [p["id"] for p in undated],
        "unpaired_done": unpaired,
        "date_field": DATE_FIELD,
        "consecutive_window": [p["id"] for p in window],
        "filename_order_window": [p["id"] for p in pairs[-CONSECUTIVE_HITS_REQUIRED:]],
        "hit_rate": (len(hits) / len(graded)) if graded else None,
        "hit_rate_all_pairs": (len(hits) / len(pairs)) if pairs else None,
        "rule_runnable": len(dated) >= CONSECUTIVE_HITS_REQUIRED,
        "rule_satisfied": satisfied,
    }


def intake(records: list[dict]) -> dict:
    """Reconcile what is on disk against what the inbox reader admitted.

    This is defect (1)'s structural fix and the reason it is arithmetic rather
    than a list of known-bad filenames. `agenda.read_inbox()` already refuses
    files and already records why, in `agenda.refused_inbox()`; what was
    missing was any caller. Three real proposals -- two of them solver work --
    were being dropped in a way no report showed, for the second time, having
    been fixed once per-record on 2026-08-07.

    So this does not enumerate the three. It asserts

        files on disk == admitted + refused

    and reports the residual. Patching three records leaves the fourth to be
    discovered by an audit; an invariant that must balance makes the fourth
    announce itself. A refusal path that forgets to write the ledger produces
    an UNRECONCILED delta and a nonzero exit.

    It deliberately does NOT re-admit refused files. Whether a record clears
    the schema and style rails is `agenda`'s judgement and stays there; this
    instrument's job is that the judgement is visible and counted.
    """
    sys.path.insert(0, str(REPO / "sdk"))
    try:
        from chief_engineer import agenda
    except Exception as exc:  # pragma: no cover - reported, never swallowed
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}

    on_disk = sorted(p.name for p in PROPOSALS.glob("*.json"))
    admitted = agenda.read_inbox()
    refused = agenda.refused_inbox()
    refused_names = {e["file"] for e in refused}

    by_file = {r["_file"]: r for r in records}
    for entry in refused:
        rec = by_file.get(entry["file"], {})
        entry = entry  # noqa: PLW2901 - kept for readability below
        est = rec.get("est_core_min")
        try:
            entry["est_core_min"] = float(est) if est not in (None, "") else None
        except (TypeError, ValueError):
            entry["est_core_min"] = None

    # A status the reader does not recognise is silently rewritten to
    # "proposed" by read_inbox's `status if status in STATUSES else
    # "proposed"`. That is the same silence as a refused file, one field
    # down: the record said one thing and the instrument reads back another
    # with nothing anywhere saying so. Named and costed here; the vocabulary
    # decision itself is the docket's (D68), not this reader's to make.
    coerced = []
    for r in records:
        raw = str(r.get("status") or "proposed")
        if raw not in agenda.STATUSES:
            est = r.get("est_core_min")
            try:
                est = float(est) if est not in (None, "") else None
            except (TypeError, ValueError):
                est = None
            coerced.append({"file": r["_file"], "status_on_disk": raw,
                            "read_back_as": "proposed", "est_core_min": est})

    residual = sorted(set(on_disk)
                      - {p["id"] + ".json" for p in admitted}
                      - refused_names)
    # `admitted` is keyed by proposal id, which need not equal the filename, so
    # the id-based residual above can misfire; the count identity is the claim.
    reconciles = len(on_disk) == len(admitted) + len(refused)
    return {
        "available": True,
        "files_on_disk": len(on_disk),
        "admitted": len(admitted),
        "refused": refused,
        "refused_count": len(refused),
        "refused_core_min": sum(e["est_core_min"] or 0.0 for e in refused),
        "reconciles": reconciles,
        "unreconciled_by": len(on_disk) - len(admitted) - len(refused),
        "residual_files": residual if not reconciles else [],
        "status_coerced": coerced,
        "status_coerced_core_min": sum(c["est_core_min"] or 0.0
                                       for c in coerced),
    }


def collect() -> dict:
    records, broken = load()
    out = score(records)
    sha, dirty = _head()
    out["commit"] = sha
    out["working_tree_dirty"] = dirty
    out["unparseable"] = broken
    out["intake"] = intake(records)
    out["frame"] = ("demo-output/website/agenda/proposals/*.json, every file, "
                    "no filter; pairs require BOTH est_core_min and "
                    "measured_core_min on the same record")
    return out


def _emit(d: dict) -> None:
    print(f"CALIBRATION SCORECARD at {d['commit']}"
          f"{' +dirty working tree' if d['working_tree_dirty'] else ''}")
    print(f"FRAME: {d['frame']}")
    print()
    print(f"proposals {d['proposals']}  ·  done {d['done']}  ·  "
          f"scoreable pairs {len(d['pairs'])}")
    if d["unparseable"]:
        print(f"UNPARSEABLE ({len(d['unparseable'])}) -- counted, not skipped:")
        for b in d["unparseable"]:
            print(f"   {b}")
    _emit_intake(d["intake"])
    print()
    if not d["pairs"]:
        print("NO PAIRS. The rule cannot be evaluated at all.")
    else:
        for p in sorted(d["pairs"], key=lambda p: (p["dated"] or "")):
            if p["class"] == EXACT_ZERO:
                mark, err = "ZERO", "  0 → 0, no band tested"
            elif p["class"] == ZERO_MEASURED:
                mark, err = "MISS", "  n/a, measured 0"
            else:
                mark = "HIT " if p["hit"] else "MISS"
                err = f"{p['rel_error']*100:5.1f}% off  "
            date = p["dated"] or "UNDATED"
            print(f"  {mark}  est {p['est']:>8.4g} → measured {p['measured']:>8.4g}"
                  f"   {err}  {date:<21}  {p['id']}")
        n_hit = sum(1 for p in d["pairs"] if p["hit"])
        n_graded = len(d["graded"])
        print(f"\n  hit rate within {int(TOLERANCE*100)}%: "
              f"{n_hit} of {n_graded} graded  "
              f"({d['hit_rate']*100:.0f}%)" if n_graded else "\n  no graded pairs")
        if d["exact_zero"]:
            print(f"  {len(d['exact_zero'])} pair(s) in the {EXACT_ZERO!r} class: "
                  f"forecast 0, cost 0. Correct, and counted NEITHER way --")
            print(f"  every tolerance band contains zero, so they test no "
                  f"scaling law and cannot open §4's gate:")
            for z in d["exact_zero"]:
                print(f"     {z}")
            print(f"  Stated so it cannot flatter: over all "
                  f"{len(d['pairs'])} pairs including these it is "
                  f"{n_hit} of {len(d['pairs'])} "
                  f"({d['hit_rate_all_pairs']*100:.0f}%).")
    print()
    print(f"CAPABILITY_STRATEGY §4's rule ({CONSECUTIVE_HITS_REQUIRED}-for-"
          f"{CONSECUTIVE_HITS_REQUIRED} within {int(TOLERANCE*100)}%):")
    print(f"  ordered by      : {d['date_field']} (the record's own dated field)")
    print(f"  runnable at all : {d['rule_runnable']}")
    verdict = {True: "True", False: "False",
               None: "UNKNOWN"}[d["rule_satisfied"]]
    print(f"  satisfied       : {verdict}")
    print(f"  window scored   : {', '.join(d['consecutive_window']) or '(none)'}")
    if d["undated"]:
        print(f"  UNDATED ({len(d['undated'])}) -- no {d['date_field']}, so their "
              f"place in the sequence is unknown and the verdict above is "
              f"UNKNOWN, not False:")
        for u in d["undated"]:
            print(f"     {u}")
    if d["filename_order_window"] != d["consecutive_window"]:
        print(f"  (filename order -- what this script scored before the fix -- "
              f"would have taken: {', '.join(d['filename_order_window'])})")
    print()
    n = len(d["unpaired_done"])
    done = d["done"] or 1
    print(f"THE BINDING CONSTRAINT IS THE RECORD, NOT THE FORECASTING.")
    print(f"  {n} of {d['done']} proposal(s) marked done carry NO measured "
          f"cost ({n/done*100:.0f}% of completed work).")
    print(f"  Counting the exact-zero pairs, {d['done'] - len(d['graded'])} of "
          f"{d['done']} ({(d['done']-len(d['graded']))/done*100:.0f}%) yield no "
          f"graded evidence at all, so §4's rule is judged on "
          f"{len(d['graded'])} samples where {d['done']} were available.")
    print(f"  Each is a scoreable pair the lab ran, paid for, and did not write down:")
    for u in d["unpaired_done"]:
        print(f"     {u}")
    if d["window_displaced_by"]:
        print()
        print(f"  AND THE SCORED WINDOW IS NOT THE TRUE TAIL. "
              f"{len(d['window_displaced_by'])} done record(s) newer than the "
              f"window's start carry no measured cost, so more recent completed")
        print(f"  work than the evidence above is absent from the verdict:")
        for u in d["window_displaced_by"]:
            print(f"     {u}")


def _emit_intake(k: dict) -> None:
    """Defect (1). The refusal ledger, read out loud by its first real caller."""
    if not k.get("available"):
        print(f"INTAKE UNRECONCILED -- the inbox reader would not import: "
              f"{k.get('error')}")
        return
    print(f"INTAKE: {k['files_on_disk']} file(s) on disk  ·  "
          f"{k['admitted']} admitted by agenda.read_inbox()  ·  "
          f"{k['refused_count']} refused")
    if k["refused"]:
        print(f"  REFUSED AT INTAKE ({k['refused_count']}, "
              f"{k['refused_core_min']:g} core-min) -- counted, never silent:")
        for e in k["refused"]:
            est = ("" if e.get("est_core_min") is None
                   else f"  [{e['est_core_min']:g} core-min]")
            print(f"     {e['file']}{est}")
            for v in e["violations"]:
                print(f"        · {v}")
    if k["status_coerced"]:
        print(f"  STATUS COERCED ({len(k['status_coerced'])}, "
              f"{k['status_coerced_core_min']:g} core-min) -- the file says one "
              f"thing, the reader returns another:")
        for c in k["status_coerced"]:
            est = ("" if c["est_core_min"] is None
                   else f"  [{c['est_core_min']:g} core-min]")
            print(f"     {c['file']}: {c['status_on_disk']!r} not in "
                  f"agenda.STATUSES → read back as "
                  f"{c['read_back_as']!r}{est}")
    if not k["reconciles"]:
        print(f"  *** UNRECONCILED by {k['unreconciled_by']}: files on disk != "
              f"admitted + refused. A record is being dropped by a path that "
              f"writes no refusal. This is the defect, not a rounding. ***")
        for r in k["residual_files"]:
            print(f"     unaccounted: {r}")
    else:
        print(f"  reconciles: {k['files_on_disk']} == {k['admitted']} admitted "
              f"+ {k['refused_count']} refused")


def defects(d: dict) -> list[str]:
    """The findings whose presence must move the exit code, one line each.

    WHY THIS FUNCTION EXISTS (V15 round 7 F6, docket D95; repaired 2026-08-15)
    -------------------------------------------------------------------------
    Until 2026-08-15 `main()` ended:

        return 0 if data["intake"].get("reconciles", False) else 2

    and `reconciles` is `len(on_disk) == len(admitted) + len(refused)`, where
    `admitted` and `refused` come from one pass of `agenda.read_inbox()` whose
    every loop iteration terminates in exactly one of the two lists. The sum IS
    the file count, so the only non-zero path this instrument had was a
    CONSTRUCTION IDENTITY. It printed `satisfied: False`, `hit rate 3 of 9`,
    two coerced statuses and a displaced window, and exited 0 -- the lab's
    forecasting grader could not exit non-zero on a forecasting defect.

    The identity is kept, because an invariant that must balance is still the
    right shape for the silent-drop class it was built for (it is simply not
    the only thing this instrument knows). What is added is every finding here
    that is a DEFECT IN THE RECORD rather than a MEASUREMENT OF IT.

    WHAT IS DELIBERATELY NOT IN THIS LIST, and the line is worth defending:

      * the hit rate, and `rule_satisfied`. Those are the measurement. This
        module's own docstring is that §4's auto-approve rule cannot run
        because the lab does not write outturns back -- that is the finding it
        exists to REPORT, and a grader that goes red because the thing it
        grades scored badly is an alarm, not a gate (L-84). It would be red
        every day until §4 passes, and it would be switched off first.
      * refusals at intake. `agenda` refuses a file on its own schema and style
        rails, records why, and this scorecard's job is that the judgement is
        visible and counted -- not to overrule it. A refusal is a declared,
        counted state with a named reason, which is the opposite of a silence.

    What IS in it, in every case, is a record that says one thing while the
    lab reads back another, or that cannot be read at all.
    """
    out: list[str] = []
    k = d["intake"]
    if not k.get("available"):
        out.append(f"the inbox reader would not import: {k.get('error')} -- "
                   f"nothing about intake was checked on this run")
    elif not k.get("reconciles"):
        out.append(f"intake unreconciled by {k['unreconciled_by']}: files on "
                   f"disk != admitted + refused, so a record is being dropped "
                   f"by a path that writes no refusal")
    if d["unparseable"]:
        out.append(f"{len(d['unparseable'])} proposal file(s) would not parse, "
                   f"so every rate above is over the subset that happened to "
                   f"be well-formed")
    if k.get("status_coerced"):
        out.append(f"{len(k['status_coerced'])} record(s) carry a status the "
                   f"reader does not recognise and silently rewrites to "
                   f"'proposed': the file says one thing and the instrument "
                   f"returns another")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)
    data = collect()
    found = defects(data)
    data["defects"] = found
    if args.json:
        json.dump(data, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        _emit(data)
        if found:
            print()
            print(f"DEFECTS ({len(found)}) -- each of these moves the exit code:")
            for f in found:
                print(f"  · {f}")
        else:
            print()
            print("DEFECTS: none. Every record on disk parsed, was accounted "
                  "for by intake, and reads back as it was written. The rates "
                  "above are measurements and do not move this exit code.")
    # A silently-refused or silently-rewritten record is the defect this
    # instrument was repaired for; it does not get to exit 0.
    return 2 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
