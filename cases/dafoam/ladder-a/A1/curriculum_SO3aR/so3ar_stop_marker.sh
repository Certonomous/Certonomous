#!/usr/bin/env bash
# SO-3aR STOP MARKER WRITER -- PREREGISTRATION.md section 7 row 9.  NEW FILE, NO PARENT.
#
# WHY THIS EXISTS (section 2, limb 2).  SO-3aR's duty to its successor is a FIXED
# ADDRESS the successor's precondition can read.  Two hard lessons, both already
# paid for by this family, are designed into the shape of this file:
#
#   (i)  SO-1b pinned its dependency BY GLOB (`SO1a_grade_*.json`).  The glob
#        could not match the successor artefact `SO1aR_grade_*.json`, so it fired
#        into a guaranteed outcome and closed the item at rc=7.  THEREFORE THIS
#        MARKER HAS ONE FIXED NAME AND NEVER A TIMESTAMP: the successor pins it
#        BY ABSOLUTE PATH AND BY MD5, and a moved md5 REFUSES.  A file whose name
#        carries a timestamp forces the reader to sort, and a sorting instruction
#        is not a fixed address.
#   (ii) SO-1b evaluated its precondition inside an INLINE HEREDOC and that was
#        UNTESTABLE BY CONSTRUCTION.  THIS FILE ALSO CARRIES A HEREDOC, AND THE
#        DIFFERENCE IS STATED PRECISELY RATHER THAN GLOSSED, because a file that
#        condemned heredocs while containing one would be worth less than no
#        comment at all:
#          * SO-1b's heredoc held a DEPENDENCY DECISION -- a glob whose only
#            firing was in production, on an artefact the selftest never built.
#            Nothing could drive that branch before it fired for real.
#          * This heredoc holds NO decision that the file's own invocation does
#            not reach.  EVERY branch in it -- verdict present, verdict absent,
#            verdict out-of-vocabulary, artefact malformed, artefact missing --
#            is reached by calling this script with ordinary arguments, and the
#            selftest drives all five directions plus the read-back refusal.
#        The claim being made is therefore the narrow one: THIS FILE IS DRIVABLE
#        END TO END BY ITS OWN COMMAND LINE.  It is NOT the broad claim that it
#        avoids a heredoc, which would be false.
#        Row 9 registers ONE file, so a helper module is not split out; if a
#        later rung wants the `curriculum_SO1bR/so1br_precondition.py` form, that
#        is a registration change and is not taken by Stage 2 on its own.
#
# IT IS WRITTEN ON EVERY EXIT PATH, INCLUDING THE PATHS WHERE NOTHING RAN.  A
# marker that appears only on success is exactly the address a successor cannot
# rely on, and the successor must be able to distinguish "SO-3aR said NOT A RESULT"
# from "SO-3aR never got far enough to say anything" -- so both are RECORDED
# STATES here, and neither is an absent file.
#
# IT READS AND REPORTS.  IT DOES NOT GRADE, AND IT NEVER COMPOSES A VERDICT.
# The verdict is the frozen comparator's alone; this file copies it or records
# that there is none.  If it cannot read a verdict it writes `PENDING` -- a
# rule-1 token whose plain reading is NOT success -- never a blank and never an
# optimistic default.
#
# Usage:  so3ar_stop_marker.sh <RUN_ROOT> <CHAIN_RC> <DECLARED> <EXECUTED> [GRADE_JSON]
set -uo pipefail

BASE="${1:-}"; CHAIN_RC="${2:-}"; DECLARED="${3:-}"; EXECUTED="${4:-}"; GRADE_JSON="${5:-}"
test -n "$BASE" || { echo "ABORT so3ar_stop_marker.sh: no run root given"; exit 64; }
test -n "$CHAIN_RC" || { echo "ABORT so3ar_stop_marker.sh: no chain rc given"; exit 64; }
test -n "$DECLARED" || { echo "ABORT so3ar_stop_marker.sh: no DECLARED count given"; exit 64; }
test -n "$EXECUTED" || { echo "ABORT so3ar_stop_marker.sh: no EXECUTED count given"; exit 64; }
test -d "$BASE" || { echo "ABORT so3ar_stop_marker.sh: run root absent: $BASE"; exit 4; }

# THE FIXED ADDRESS.  One name, no timestamp, no glob.  Registered in
# PREREGISTRATION.md section 7 row 9 and read by the successor by ABSOLUTE PATH.
MARKER="$BASE/SO3aR_STOP_MARKER.json"

# The write is ATOMIC: a successor polling this address must never read a
# half-written file and conclude anything from it.  Write to a temp name in the
# SAME directory (so the rename cannot cross a filesystem) and mv into place.
TMP="$BASE/.SO3aR_STOP_MARKER.json.tmp.$$"

python3 - "$MARKER" "$TMP" "$CHAIN_RC" "$DECLARED" "$EXECUTED" "$GRADE_JSON" <<'PY'
import json, os, sys, hashlib, datetime

marker, tmp, chain_rc, declared, executed, grade_json = sys.argv[1:7]

def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

rec = {
    "item": "SO3aR",
    "marker_version": 1,
    "written_utc": utc(),
    "chain_rc": int(chain_rc),
    "stages_declared": int(declared),
    "stages_executed": int(executed),
}

# section 5 Requirement 4 / G-STAGES: DECLARED and EXECUTED both carried, and the
# shortfall is an explicit FIELD a successor can read -- not something it must
# re-derive by comparing two numbers and hoping it compared them the right way.
rec["stages_short"] = rec["stages_declared"] - rec["stages_executed"]
rec["truncated"] = rec["stages_short"] > 0

# ---- the verdict.  COPIED from the comparator's artefact, NEVER composed here.
verdict = None
g5j = None
detail = None
if grade_json and os.path.exists(grade_json):
    try:
        with open(grade_json) as f:
            g = json.load(f)
        verdict = g.get("verdict")
        # G5J is the bright-line reading; carried verbatim if the comparator
        # emitted it, and recorded as absent rather than invented if it did not.
        for key in ("G5J", "gates"):
            if isinstance(g.get(key), dict):
                g5j = g[key].get("G5J") if key == "gates" else g[key]
                if g5j is not None:
                    break
        detail = {"rows": g.get("rows"), "source": os.path.basename(grade_json)}
        rec["grade_json_md5"] = hashlib.md5(open(grade_json, "rb").read()).hexdigest()
        rec["grade_json_path"] = os.path.abspath(grade_json)
    except (OSError, ValueError) as exc:
        # A MALFORMED artefact is reported as malformed.  It is NEVER silently
        # treated as an absent one, because those are different findings: absent
        # means the comparator never wrote, malformed means it wrote garbage.
        rec["grade_json_error"] = "%s: %s" % (type(exc).__name__, exc)
        rec["grade_json_path"] = os.path.abspath(grade_json)
elif grade_json:
    rec["grade_json_error"] = "registered grade artefact ABSENT at %s" % os.path.abspath(grade_json)

VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
if verdict in VOCAB:
    rec["verdict"] = verdict
    rec["verdict_source"] = "COPIED FROM THE COMPARATOR ARTEFACT"
else:
    # No readable verdict.  PENDING is a rule-1 token and its plain reading is
    # NOT success.  An unreadable or out-of-vocabulary verdict is recorded as
    # such rather than coerced into one of the six.
    rec["verdict"] = "PENDING"
    rec["verdict_source"] = "NO READABLE COMPARATOR VERDICT AT THIS ADDRESS"
    if verdict is not None:
        rec["verdict_rejected_value"] = str(verdict)[:200]

rec["G5J"] = g5j if g5j is not None else "NOT PRESENT IN THE ARTEFACT"
rec["rows"] = detail["rows"] if detail and detail.get("rows") is not None else "NOT PRESENT IN THE ARTEFACT"

with open(tmp, "w") as f:
    json.dump(rec, f, indent=2, sort_keys=True)
    f.write("\n")
os.replace(tmp, marker)

# READ IT BACK FROM DISK.  A writer not shown able to see what it wrote is not
# evidence that anything landed (CLAUDE.md rule 3, applied to this file's own
# output).  Refuse loudly rather than let a successor poll a file that is not
# there or does not parse.
with open(marker) as f:
    back = json.load(f)
if back.get("verdict") != rec["verdict"] or back.get("chain_rc") != rec["chain_rc"]:
    sys.stderr.write("ABORT stop marker read-back disagrees with what was written\n")
    sys.exit(2)
print("SO3AR_STOP_MARKER written=%s verdict=%s chain_rc=%d declared=%d executed=%d truncated=%s"
      % (marker, back["verdict"], back["chain_rc"], back["stages_declared"],
         back["stages_executed"], back["truncated"]))
PY
RC=$?
rm -f "$TMP" 2>/dev/null
exit "$RC"
