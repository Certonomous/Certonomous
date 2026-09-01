#!/usr/bin/env bash
# ===========================================================================
# Curriculum D19O -- THE STOP MARKER.  This item's duty to ITS successor.
#
# Written on EVERY exit path, including refusal and abort, and read by the
# successor BY ABSOLUTE PATH.  It carries the item verdict, both row verdicts,
# the ceiling that bound them, and the literal key names a successor's reader
# must use.
#
# AN ITEM THAT STOPS WITHOUT TELLING ITS SUCCESSOR WHY HAS MADE ITS SUCCESSOR
# RE-BUY THE FINDING.  D19R stopped with `grader_rc=2` and no verdict, and its
# successor D19R2 had to spend a whole freeze re-deriving what had happened.
#
#   d19o_stop_marker.sh <run root> <reason> [grade json]
#
# The schema contract is DRIVEN, not asserted: `d19o_chain_driver_selftest.sh`
# runs THIS FILE on a real grade artefact the comparator wrote, then RENAMES the
# key and requires this marker to report it absent.  A schema contract that
# cannot fail is not a contract.
# ===========================================================================
set -uo pipefail

BASE="${1:-}"
REASON="${2:-UNSPECIFIED}"
GRADE="${3:-}"
test -n "$BASE" || { echo "usage: d19o_stop_marker.sh <run root> <reason> [grade json]"; exit 64; }
mkdir -p "$BASE" 2>/dev/null

OUT="$BASE/D19O_STOP_MARKER.json"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)

python3 - "$OUT" "$REASON" "$STAMP" "$GRADE" <<'EOF'
import json, os, sys
out, reason, stamp, grade = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

rec = {
    "item": "D19O",
    "stamp": stamp,
    "reason": reason,
    "grade_artefact": grade or None,
    # ---- THE LITERAL KEYS A SUCCESSOR'S READER MUST USE -------------------
    # Named here so a successor does not have to guess where they live.  Both
    # sit at the TOP LEVEL of the grade artefact.
    "keys": {"verdict": "verdict", "rows": "rows",
             "verdict_ceiling": "verdict_ceiling",
             "capped_by_ceiling_anywhere": "capped_by_ceiling_anywhere",
             "the_registered_non_result": 'gates["G-PLAT7"]'},
    "verdict": None, "rows": None,
    "verdict_ceiling": None, "capped_by_ceiling_anywhere": None,
    "keys_absent": [],
    # ---- WHAT TRAVELS WHATEVER HAPPENED ----------------------------------
    "what_a_successor_must_know": (
        "D19O spends a COMPRESSIBLE gradient that has NO GRADED VERDICT: D19R's "
        "grader refused rc=2 and D19R2's grading attempt 1 returned NOT A RESULT. "
        "D19R's plateau did NOT close -- all_two_sided=false, "
        "score_pct=21.060684242435336, binding=[shape[7],CD,fine]. `shape[7]` is a "
        "REGISTERED NON-RESULT here, excluded BY NAME from every aggregate, and "
        "this item's verdict is CEILINGED at GATE REACHED: IT CANNOT PUBLISH PASS."),
    "the_strongest_follow_on": (
        "A FORWARD-AD or COMPLEX-STEP reference. Both images ship libDASolverADF.so "
        "(docs/dafoam/TOOLCHAIN_INVENTORY.md section 6a), so a non-FD reference IS "
        "reachable on this box. It would settle shape[7] OUTRIGHT, because it has no "
        "step at all and therefore no plateau to close. D19R section 11 named it as "
        "the strongest single follow-on this ground admits and did not reach for it; "
        "neither does D19O, and both say so on their own face."),
    "submissions": "PARKED (CLAUDE.md rule 7; DAFOAM_CHARTER.md section 10).",
}

if grade and os.path.isfile(grade):
    try:
        g = json.load(open(grade))
    except Exception as exc:                                      # noqa: BLE001
        rec["grade_unreadable"] = repr(exc)[:200]
        g = None
    if g is not None:
        for k in ("verdict", "rows", "verdict_ceiling", "capped_by_ceiling_anywhere"):
            if k in g:
                rec[k] = g[k]
            else:
                rec["keys_absent"].append(k)
        if "gates" not in g or "G-PLAT7" not in (g.get("gates") or {}):
            rec["keys_absent"].append('gates["G-PLAT7"]')
        else:
            rec["the_registered_non_result"] = {
                r: (g["gates"]["G-PLAT7"].get(r) or {}).get("verdict")
                for r in (g.get("rows") or {})}
elif grade:
    rec["keys_absent"].append("grade_artefact_does_not_exist")

with open(out, "w") as fh:
    json.dump(rec, fh, indent=1, sort_keys=True)
    fh.flush(); os.fsync(fh.fileno())
print("D19O_STOP_MARKER_WRITTEN %s reason=%s verdict=%s keys_absent=%s"
      % (out, reason, rec["verdict"], rec["keys_absent"]))
EOF
