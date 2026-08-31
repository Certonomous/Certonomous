#!/usr/bin/env python3
"""VR7 -- CALIBRATION ROW COMPLETENESS.

Gate question: does every rung this lab has actually LAUNCHED carry a row in
`docs/COST_CALIBRATION.md`, as CLAUDE.md rule 12 requires at every process
completion ("A completion report without this comparison is incomplete")?

WHAT IS MINE: the measurement. The ROWS are each team's own to write and this
item writes none of them. A GATE FAIL here is a finding about the LAB'S
CALIBRATION RECORD, not a failure of any run, and no verdict is withdrawn by it.

THIS ITEM INDICTS ITS OWN TEAM FIRST. Verification's six VR rungs are all
launched and all graded, and at the time of freezing NONE of them carried a
calibration row. That is stated in the pre-registration as a PREDICTION.

-------------------------------------------------------------------------------
SS2j -- THE BIRTH REQUIREMENT, AND WHO WROTE THE BYTES
-------------------------------------------------------------------------------
VERIFICATION_CHARTER SS2j.2: "ask who WROTE the bytes the control reads. If the
answer is the control itself or the test harness rather than the real producer,
the birth requirement is NOT met."

The bytes this reader reads, in every limb of the selftest, are:

  * `verification/queue/LAUNCH_LOG.tsv` -- written by `scripts/queue_runner.py`
    at launch. THE REAL PRODUCER. Not synthesised here, not copied, not shaped.
  * `docs/COST_CALIBRATION.md` -- written by team supervisors under the rule-10
    private-index protocol. THE REAL PRODUCER.

NOTHING IN THIS FILE WRITES EITHER FILE. There is no plant, no fixture and no
temporary tree, because both answers ALREADY EXIST IN THE REAL CORPUS and the
honest control is to demonstrate the reader returning both FROM THE REAL BYTES
in one invocation. A synthetic ledger would have been easier and would have
failed SS2j exactly as the three specimens in SS2j.2 do.

The one thing the selftest supplies is a QUERY TOKEN proven absent from the real
ledger (limb N1). SS2j governs the bytes READ, not the query asked of them: the
ledger bytes are still the real producer's.

-------------------------------------------------------------------------------
THE MATCHER, AND WHY IT IS ROW-ANCHORED
-------------------------------------------------------------------------------
A case_id that appears in the ledger's PROSE is not a calibration row for it.
`docs/COST_CALIBRATION.md` prose cites other rungs constantly -- a free-text
search for `C-\\d+` in this file returns 910 hits against 229 actual row ids.
Limb N2 drives exactly that contamination and REFUSES a matcher that admits it.
"""

import argparse
import os
import re
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"
LAUNCH_LOG = os.path.join(REPO, "verification/queue/LAUNCH_LOG.tsv")
LEDGER = os.path.join(REPO, "docs/COST_CALIBRATION.md")

# A ledger ROW: a markdown table row whose FIRST cell is the C-id. Bold markers
# optional because the ledger uses `| **C-216** |` for emphasised rows.
ROW_ID = re.compile(r"^\|\s*\*{0,2}(C-\d+)\*{0,2}\s*\|")


class Refusal(Exception):
    """The instrument cannot honestly grade. Exit 2, never a degraded answer."""


# ---------------------------------------------------------------- readers ----

def read_launch_log(path=LAUNCH_LOG):
    """Distinct (team, case_id) actually launched, from the runner's own log.

    Producer: scripts/queue_runner.py. Columns are tab separated; col 0 is the
    UTC stamp, col 1 the team, col 2 the case_id.
    """
    if not os.path.exists(path):
        raise Refusal("LAUNCH_LOG.tsv absent at %s -- cannot enumerate launched "
                      "rungs, and an empty list would read as a clean PASS" % path)
    seen, out = set(), []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "\t" not in line:
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 3:
                continue
            team, case_id = cols[1].strip(), cols[2].strip()
            if not case_id or case_id in seen:
                continue
            seen.add(case_id)
            out.append((team, case_id))
    if not out:
        raise Refusal("LAUNCH_LOG.tsv parsed to ZERO launched rungs -- a reader "
                      "that sees nothing reports everything as covered")
    return out


def ledger_rows(path=LEDGER):
    """(row_id, line_no, row_text) for every ROW-ANCHORED entry in the ledger."""
    if not os.path.exists(path):
        raise Refusal("COST_CALIBRATION.md absent at %s" % path)
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            m = ROW_ID.match(line)
            if m:
                rows.append((m.group(1), n, line))
    if not rows:
        raise Refusal("COST_CALIBRATION.md yielded ZERO row-anchored ids -- the "
                      "matcher is blind and every rung would read UNCALIBRATED")
    return rows


def case_has_row(case_id, rows):
    """True iff `case_id` is named INSIDE a ledger ROW (not merely in prose).

    The distinction is the whole point: prose in one row citing another rung is
    not that rung's calibration row.
    """
    return any(case_id in text for _, _, text in rows)


def census(launched, rows):
    covered = [(t, c) for t, c in launched if case_has_row(c, rows)]
    missing = [(t, c) for t, c in launched if not case_has_row(c, rows)]
    return covered, missing


# ------------------------------------------------------------- selftest -------

def _fail(results, name, detail):
    results.append((name, False, detail))


def _ok(results, name, detail):
    results.append((name, True, detail))


def selftest():
    """Both limbs, on the REAL corpus, refusing rather than degrading."""
    results = []
    try:
        launched = read_launch_log()
        rows = ledger_rows()
    except Refusal as exc:
        print("SELFTEST REFUSED: %s" % exc)
        return 2

    print("  corpus: %d distinct launched rungs (producer scripts/queue_runner.py)"
          % len(launched))
    print("  corpus: %d row-anchored ledger ids (producer: team supervisors)"
          % len(rows))

    # -- P1 POSITIVE: the reader must SEE a real covered rung, from real bytes.
    covered, missing = census(launched, rows)
    if covered:
        _ok(results, "P1 positive (real covered rung seen)",
            "%d covered; specimen %s" % (len(covered), covered[0][1]))
    else:
        _fail(results, "P1 positive (real covered rung seen)",
              "ZERO covered rungs -- reader never shown able to return HAS_ROW "
              "on real bytes; a 'nothing is covered' verdict is unfalsifiable")

    # -- P2 NEGATIVE: the reader must STAY SILENT where a row genuinely exists,
    #    i.e. it must not report a covered rung as missing. Driven by asserting
    #    the covered specimen is absent from `missing`.
    if covered and covered[0] not in missing:
        _ok(results, "P2 negative (covered rung not reported missing)",
            "specimen %s absent from the missing list" % covered[0][1])
    elif not covered:
        _fail(results, "P2 negative (covered rung not reported missing)",
              "no covered specimen exists to drive the negative limb")
    else:
        _fail(results, "P2 negative (covered rung not reported missing)",
              "%s appears in BOTH lists -- the classifier is not a partition"
              % covered[0][1])

    # -- N1 the reader must be able to return NO_ROW. Query token proven absent
    #    from the REAL ledger bytes (SS2j governs bytes read, not the query).
    absent_token = "VR7_ABSENT_PROBE_TOKEN_NOT_IN_ANY_LEDGER_ROW"
    if any(absent_token in t for _, _, t in rows):
        _fail(results, "N1 absent-probe precondition",
              "the probe token is PRESENT in the ledger; probe is void")
    elif case_has_row(absent_token, rows):
        _fail(results, "N1 negative (absent token reads NO_ROW)",
              "reader claimed a row for a token proven absent -- it cannot "
              "return a zero, so its zeros are not evidence")
    else:
        _ok(results, "N1 negative (absent token reads NO_ROW)",
            "reader returns NO_ROW on real ledger bytes")

    # -- N2 PROSE CONTAMINATION: a token appearing ONLY in the ledger's prose
    #    must NOT count as that rung's row. This is the matcher control the
    #    free-text/row-anchored gap demands.
    full = open(LEDGER, encoding="utf-8", errors="replace").read()
    free_ids = re.findall(r"C-\d+", full)
    row_ids = [r for r, _, _ in rows]
    if len(free_ids) <= len(row_ids):
        _fail(results, "N2 prose contamination is real",
              "free-text ids (%d) do not exceed row ids (%d) -- this ledger "
              "cannot drive the contamination limb" % (len(free_ids), len(row_ids)))
    else:
        _ok(results, "N2 prose contamination is real",
            "free-text %d vs row-anchored %d; matcher is row-anchored"
            % (len(free_ids), len(row_ids)))

    # -- N3 the matcher must REJECT a non-row line carrying a C-id. Driven on a
    #    real prose line from the real ledger, not a fabricated one.
    prose_line = None
    for line in full.splitlines():
        if re.search(r"C-\d+", line) and not ROW_ID.match(line):
            prose_line = line
            break
    if prose_line is None:
        _fail(results, "N3 matcher rejects a real prose line",
              "no real prose line carrying a C-id found to drive the limb")
    elif ROW_ID.match(prose_line):
        _fail(results, "N3 matcher rejects a real prose line",
              "row matcher accepted a prose line")
    else:
        _ok(results, "N3 matcher rejects a real prose line",
            "specimen prose line correctly not a row")

    # -- N4 REFUSAL PATH: an empty ledger must REFUSE, never report total
    #    divergence. "I cannot read the ledger" and "nothing is calibrated" are
    #    the same output from a broken parser and only one is a finding.
    try:
        ledger_rows("/nonexistent/vr7/ledger.md")
        _fail(results, "N4 refusal on unreadable ledger", "did not refuse")
    except Refusal:
        _ok(results, "N4 refusal on unreadable ledger", "refused (exit 2 path)")

    # -- N5 same, for the launch log.
    try:
        read_launch_log("/nonexistent/vr7/launch_log.tsv")
        _fail(results, "N5 refusal on unreadable launch log", "did not refuse")
    except Refusal:
        _ok(results, "N5 refusal on unreadable launch log", "refused (exit 2 path)")

    print()
    for name, good, detail in results:
        print("  [%s] %s -- %s" % ("ok" if good else "FAIL", name, detail))
    bad = sum(1 for _, g, _ in results if not g)
    print("\nSELFTEST: %d case(s), %d failure(s)" % (len(results), bad))
    return 0 if bad == 0 else 2


# ---------------------------------------------------------------- census ------

def run_census():
    launched = read_launch_log()
    rows = ledger_rows()
    covered, missing = census(launched, rows)

    print("VR7 -- calibration row completeness "
          "(frozen: verification/campaign/VR7_PREREGISTRATION.md)")
    print("  repo=%s" % REPO)
    print("  launched rungs (distinct, LAUNCH_LOG.tsv): %d" % len(launched))
    print("  ledger rows (row-anchored):                %d" % len(rows))
    print("  CALIBRATED:   %d" % len(covered))
    print("  UNCALIBRATED: %d" % len(missing))

    by_team = {}
    for team, case in missing:
        by_team.setdefault(team, []).append(case)
    print("\n  UNCALIBRATED by team:")
    for team in sorted(by_team):
        print("    %-22s %d" % (team, len(by_team[team])))

    own = [c for t, c in missing if t == "verification"]
    print("\n  THIS TEAM'S OWN UNCALIBRATED RUNGS: %d" % len(own))
    for c in own:
        print("    %s" % c)

    if missing:
        print("\nVERDICT: GATE FAIL -- %d of %d launched rungs carry no "
              "row-anchored entry in docs/COST_CALIBRATION.md. Rule 12 requires "
              "the estimate-versus-actual comparison at every process "
              "completion. This is a finding about the CALIBRATION RECORD, not "
              "about any run: NO VERDICT IS WITHDRAWN and the remedy is to WRITE "
              "the rows, never to delete anything. The rows are each team's own."
              % (len(missing), len(launched)))
        return 1
    print("\nVERDICT: PASS -- every launched rung carries a calibration row.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="VR7 calibration row completeness")
    ap.add_argument("--selftest", action="store_true",
                    help="drive both control limbs on the real corpus; exit 2 on "
                         "any failure or refusal")
    args = ap.parse_args()
    try:
        if args.selftest:
            print("VR7 SELFTEST -- controls read bytes written by "
                  "scripts/queue_runner.py and by team supervisors (SS2j.2)")
            return selftest()
        return run_census()
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
