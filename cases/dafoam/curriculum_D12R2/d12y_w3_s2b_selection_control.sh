#!/bin/bash
# =============================================================================
# W3-A3 PLANTED-FAILURE CONTROL for the S2b LOG SELECTION -- ZERO COMPUTE.
#
# Sanaa's standing directives section 1 (L-314): every guard ships its
# planted-failure proof.  CLAUDE.md rule 3: a reader not shown able to see a
# NON-zero is not evidence.  This control drives BOTH sides of the W3-A3
# uniqueness refusal and BOTH sides of the manifest cross-check, through the
# REAL `plan()` code path of d12y_grade_w3.py, on a fixture assembled from the
# REAL 33-row D12R2 phase-1 manifest and its REAL S2b log.
#
# IT CREATES NO CONTAINER, TOUCHES NO RUN ROOT AND WRITES ONLY UNDER $TMPD.
# The D12R2 run root is read ONLY (cp -a out of it); nothing is written there.
#
# Legs:
#   L1  exactly one S2b_*.log            -> plan() rc=0, s2b_log_selected names it
#   L2  L1's numbers are BYTE-IDENTICAL to the pre-W3-A3 grader's on the same
#       fixture (delta_eff, h_min, delta_window) -- the repair moves NO number
#   L3  a SECOND S2b_*.log planted        -> REFUSES rc=2 on W3-A3 ambiguity
#   L4  the plant REMOVED again           -> passes again (the refusal is caused
#       by the plant, not by the fixture: this is the planted CONTROL)
#   L5  manifest row "log" == the true name -> passes (cross-check is not a
#       blanket refusal)
#   L6  manifest row "log" == a WRONG name  -> REFUSES rc=2 on the cross-check
#   L7  no S2b_*.log at all               -> REFUSES rc=2 (pre-existing limb,
#       carried unchanged)
#   L8  ast.Assert audit == 0, with the counter SHOWN COUNTING a planted assert
# =============================================================================
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
GRADER="$HERE/d12y_grade_w3.py"
SRC=/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady
TMPD="${1:-/tmp/d12y_w3_s2b_selection_control}"
PY="${PY:-python3}"
PASS=0; FAIL=0
chk () { if [ "$2" = "1" ]; then PASS=$((PASS+1)); echo "  PASS  $1"; else FAIL=$((FAIL+1)); echo "  FAIL  $1"; fi; }

test -f "$GRADER" || { echo "ABORT no grader at $GRADER"; exit 4; }
test -d "$SRC"    || { echo "ABORT the D12R2 seed run root is absent: $SRC"; exit 4; }
# a control that cannot find its seed REFUSES rather than reporting a clean zero
NSEED=$(ls -1 "$SRC"/S2b_*.log 2>/dev/null | wc -l)
[ "$NSEED" = "1" ] || { echo "ABORT the seed root holds $NSEED S2b_*.log, expected exactly 1"; exit 4; }

rm -rf "$TMPD"; mkdir -p "$TMPD"
find "$HERE" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null

"$PY" - "$SRC" "$TMPD" <<'MKFIX'
import json, os, re, shutil, sys
SRC, TMPD = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(os.path.join(SRC, "manifest.jsonl")) if l.strip()]
for r in rows:
    r["W"] = 2000                      # W3-A2 needs W in every row; the fixture is at the registered W
    r.setdefault("fatal_tokens", [])   # Amendment 2's launcher key, absent from the D12R2 seed
led = [L for L in open(os.path.join(SRC, "ledger.txt"), errors="replace").read().splitlines()
       if not L.startswith("W_STEPS=")] + ["W_STEPS=2000"]
s2b = sorted(p for p in os.listdir(SRC) if p.startswith("S2b_") and p.endswith(".log"))[0]
def build(name, extra_log=None, declared=None, drop_s2b=False):
    d = os.path.join(TMPD, name)
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d)
    rr = [dict(r) for r in rows]
    if declared is not None:
        for r in rr:
            if r.get("name") == "S2b":
                r["log"] = declared
    with open(os.path.join(d, "manifest.jsonl"), "w") as f:
        for r in rr: f.write(json.dumps(r, sort_keys=True) + "\n")
    open(os.path.join(d, "ledger.txt"), "w").write("\n".join(led) + "\n")
    if not drop_s2b:
        shutil.copy2(os.path.join(SRC, s2b), os.path.join(d, s2b))
    if extra_log:
        txt = open(os.path.join(SRC, s2b), errors="replace").read()
        pert = re.sub(r"^CD:\s*(\S+)\s+average:\s*(\S+)\s*$",
                      lambda m: "CD: %.10g  average: %.10g" % (float(m.group(1))*1.05,
                                                               float(m.group(2))*1.05),
                      txt, flags=re.M)
        open(os.path.join(d, extra_log), "w").write(pert)
    return d
build("one")
build("two",  extra_log="S2b_29999999T999999Z_9999999.log")   # sorts LAST -> the last-wins target
build("decl", declared=s2b)
build("bad",  declared="S2b_NOT_THE_FILE_ON_DISK.log")
build("none", drop_s2b=True)
print("SEED_S2B=%s" % s2b)
MKFIX
S2B=$(ls -1 "$TMPD/one" | grep '^S2b_' | head -1)

run () {  # $1 fixture -> writes $TMPD/$1.json / .err, echoes rc
  "$PY" "$GRADER" --plan --manifest "$TMPD/$1/manifest.jsonl" --root "$TMPD/$1" \
      > "$TMPD/$1.json" 2> "$TMPD/$1.err"; echo $?
}

echo "== W3-A3 S2b SELECTION CONTROL, interpreter: $PY =="
RC1=$(run one)
SEL=$("$PY" -c "import json;print(json.load(open('$TMPD/one.json'))['s2b_log_selected'])" 2>/dev/null)
chk "L1 exactly one S2b_*.log -> plan() rc=0" "$([ "$RC1" = 0 ] && echo 1 || echo 0)"
chk "L1 s2b_log_selected NAMES the file on disk ($S2B)" "$([ "$(basename "${SEL:-x}")" = "$S2B" ] && echo 1 || echo 0)"

# L2 -- the pre-W3-A3 grader on the SAME fixture, reconstructed by restoring the
# last-wins line, so the number-invariance claim is DRIVEN and not asserted.
"$PY" - "$GRADER" "$TMPD" <<'PREPATCH'
import re, sys
src = open(sys.argv[1]).read()
i = src.index("    # ---- W3-A3 (2026-08-27, PRE-COMPUTE)")
j = src.index("    if len(cd) <= TRANSIENT_DISCARD:", i)
old = ('    logp = os.path.join(root, os.path.basename(s2.get("log", "")))\n'
       '    cands = [p for p in os.listdir(root) if p.startswith("S2b_") and p.endswith(".log")]\n'
       '    if not cands:\n'
       '        raise Refusal("no S2b log on disk in %s" % root)\n'
       '    _, cd, _ = read_series(os.path.join(root, sorted(cands)[-1]))\n')
open(sys.argv[2] + "/grader_PRE_W3A3.py", "w").write(src[:i] + old + src[j:])
PREPATCH
"$PY" "$TMPD/grader_PRE_W3A3.py" --plan --manifest "$TMPD/one/manifest.jsonl" --root "$TMPD/one" \
    > "$TMPD/one_pre.json" 2> "$TMPD/one_pre.err"
SAME=$("$PY" -c "
import json
a=json.load(open('$TMPD/one_pre.json'))['step_plan']; b=json.load(open('$TMPD/one.json'))['step_plan']
print(1 if a==b else 0)
" 2>/dev/null)
chk "L2 step_plan IDENTICAL pre-W3-A3 vs post-W3-A3 on the one-file fixture (no number moves)" "${SAME:-0}"

RC3=$(run two)
AMB=$(grep -c 'W3-A3: S2b log selection is AMBIGUOUS' "$TMPD/two.err")
chk "L3 PLANTED second S2b_*.log -> REFUSES rc=2" "$([ "$RC3" = 2 ] && echo 1 || echo 0)"
chk "L3 the refusal NAMES the ambiguity" "$([ "$AMB" -ge 1 ] && echo 1 || echo 0)"
# and the SAME plant on the PRE-W3-A3 grader is silently ACCEPTED -- the defect, driven
"$PY" "$TMPD/grader_PRE_W3A3.py" --plan --manifest "$TMPD/two/manifest.jsonl" --root "$TMPD/two" \
    > "$TMPD/two_pre.json" 2> "$TMPD/two_pre.err"; RC3P=$?
MOVED=$("$PY" -c "
import json
a=json.load(open('$TMPD/one_pre.json'))['step_plan']['h_min']
b=json.load(open('$TMPD/two_pre.json'))['step_plan']['h_min']
print(1 if a!=b else 0)
" 2>/dev/null)
chk "L3c the PRE-W3-A3 grader accepts the same plant (rc=0) AND its h_min MOVES -- the defect is real" \
    "$([ "$RC3P" = 0 ] && [ "${MOVED:-0}" = 1 ] && echo 1 || echo 0)"

rm -f "$TMPD/two/S2b_29999999T999999Z_9999999.log"
RC4=$(run two)
chk "L4 PLANT REMOVED -> passes again rc=0 (the refusal was the plant, not the fixture)" \
    "$([ "$RC4" = 0 ] && echo 1 || echo 0)"

RC5=$(run decl)
chk "L5 manifest row \"log\" == the file on disk -> passes rc=0" "$([ "$RC5" = 0 ] && echo 1 || echo 0)"

RC6=$(run bad)
XCK=$(grep -c 'W3-A3: the S2b manifest row NAMES log' "$TMPD/bad.err")
chk "L6 manifest row \"log\" == a WRONG name -> REFUSES rc=2 on the cross-check" \
    "$([ "$RC6" = 2 ] && [ "$XCK" -ge 1 ] && echo 1 || echo 0)"

RC7=$(run none)
NOL=$(grep -c 'no S2b log on disk' "$TMPD/none.err")
chk "L7 no S2b_*.log at all -> REFUSES rc=2 (pre-existing limb, unchanged)" \
    "$([ "$RC7" = 2 ] && [ "$NOL" -ge 1 ] && echo 1 || echo 0)"

NA=$("$PY" "$GRADER" --assert-audit | grep -oE '[0-9]+ \(must be 0\)' | grep -oE '^[0-9]+')
cp -a "$GRADER" "$TMPD/grader_PLANTED_ASSERT.py"
printf '\n\ndef _planted_assert_control():\n    assert 1 == 1\n' >> "$TMPD/grader_PLANTED_ASSERT.py"
NP=$("$PY" "$TMPD/grader_PLANTED_ASSERT.py" --assert-audit | grep -oE '[0-9]+ \(must be 0\)' | grep -oE '^[0-9]+')
chk "L8 ast.Assert audit == 0, and the SAME counter reads 1 on a planted assert ($NA -> $NP)" \
    "$([ "${NA:-x}" = "0" ] && [ "${NP:-x}" = "1" ] && echo 1 || echo 0)"

echo "== pass=$PASS fail=$FAIL interpreter=$PY =="
[ "$FAIL" = "0" ]
