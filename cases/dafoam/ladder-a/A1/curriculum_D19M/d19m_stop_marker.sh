#!/usr/bin/env bash
# ===========================================================================
# Curriculum D19M -- THE STOP MARKER.  This item's duty to ITS successor.
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
#   d19m_stop_marker.sh <run root> <reason> [grade json]
#
# The schema contract is DRIVEN, not asserted: `d19m_chain_driver_selftest.sh`
# runs THIS FILE on a real grade artefact the comparator wrote, then RENAMES the
# key and requires this marker to report it absent.  A schema contract that
# cannot fail is not a contract.
# ===========================================================================
set -uo pipefail

BASE="${1:-}"
REASON="${2:-UNSPECIFIED}"
GRADE="${3:-}"
test -n "$BASE" || { echo "usage: d19m_stop_marker.sh <run root> <reason> [grade json]"; exit 64; }
mkdir -p "$BASE" 2>/dev/null

OUT="$BASE/D19M_STOP_MARKER.json"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)

python3 - "$OUT" "$REASON" "$STAMP" "$GRADE" <<'EOF'
import json, os, sys
out, reason, stamp, grade = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

rec = {
    "item": "D19M",
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
        "D19M spends a COMPRESSIBLE gradient that has NO GRADED VERDICT: D19R's "
        "grader refused rc=2 and D19R2's grading attempt 1 returned NOT A RESULT. "
        "D19R's plateau did NOT close -- all_two_sided=false, "
        "score_pct=21.060684242435336, binding=[shape[7],CD,fine]. AND THE "
        "MULTIPOINT OBJECTIVE J HAS NEVER HAD AN FD TABLE ON COMPRESSIBLE GROUND "
        "AT ALL -- this item's own FE arms are the first. `shape[7]` is a "
        "REGISTERED NON-RESULT here, excluded BY NAME from every aggregate, and "
        "this item's verdict is CEILINGED at GATE REACHED: IT CANNOT PUBLISH PASS."),
    "what_D19O_measured_that_a_successor_may_register_in_advance": (
        "D19O (RESULTS.md section 3.1) MEASURED that at ITS optimum shape[7]'s "
        "|dCD| is 5.887e-03 against 2.099e-04 at the baseline -- a factor of 28 -- "
        "and that its plateau CLOSES there (two-sided, coarse 0.974 % / fine "
        "1.061 %). ITS NEAR-NULLITY IS A PROPERTY OF THE BASELINE, NOT OF THE "
        "COMPONENT. That is evidence a successor may use to register shape[7] as "
        "GRADABLE IN ADVANCE. It did NOT license D19O to grade it, and it does not "
        "license D19M: this item optimises a different objective and reaches a "
        "different design point, and promoting a component after seeing a good "
        "number is the move the registration exists to prevent."),
    "what_D19O_measured_about_the_two_rows": (
        "At D19O's optimum the SHIPPED and PATCHED rows agreed to 0.0232 % on "
        "shape[6], where D15 measured the shipped row 44.8738 % wrong AT THE "
        "BASELINE on this same ground. The IDWarp degenerate-rotation branch fires "
        "when axisMag = 1e-15 < sqrt(eps), certain on an undeformed mesh and false "
        "on a deformed one. THIS IS WHY D19M STILL RUNS BOTH ROWS: the agreement is "
        "CONFIGURATION-DEPENDENT, and a one-row item would bake it in and destroy "
        "the only instrument that can detect it."),
    "the_strongest_follow_on": (
        "A FORWARD-AD or COMPLEX-STEP reference. Both images ship libDASolverADF.so "
        "(docs/dafoam/TOOLCHAIN_INVENTORY.md section 6a), so a non-FD reference IS "
        "reachable on this box. It would settle shape[7] OUTRIGHT, because it has no "
        "step at all and therefore no plateau to close. D19R section 11 named it as "
        "the strongest single follow-on this ground admits and did not reach for it. "
        "NEITHER DID D19O AND NEITHER DOES D19M -- three items now, each saying so "
        "on its own face. D19O sharpened the target: the component differs by 28x "
        "between baseline and optimum, so a non-FD reference AT BOTH POINTS would "
        "separate the defect from the configuration definitively."),
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
print("D19M_STOP_MARKER_WRITTEN %s reason=%s verdict=%s keys_absent=%s"
      % (out, reason, rec["verdict"], rec["keys_absent"]))
EOF
