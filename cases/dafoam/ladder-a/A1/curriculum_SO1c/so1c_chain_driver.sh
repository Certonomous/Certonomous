#!/usr/bin/env bash
# SO-1c chain driver -- DERIVED from curriculum_SO1a/so1a_chain_driver.sh with
# the REGISTERED DELTAS listed in PREREGISTRATION.md section 7 and recorded in
# so1c_chain_driver_DELTAS_from_so1a.diff.  THE DELTAS ARE:
#   * item names, run root, launcher/grader/instrument md5s;
#   * the arms are MESH Ns-P Ni-P Ns-S Ni-S -- one mesh at np = 1, then FOUR
#     np = 4 arms: two decompositions (`scotch`, `simple 4x1x1`) on each of the
#     two toolchain rows;
#   * G-SO1B, the precondition, read BEFORE the run root is created and BEFORE
#     the first launcher call, on TWO independent channels;
#   * the optref staging -- SO-1b's own-row `so1b_E.json` and its MESH `points`
#     sha256, copied ONCE into THIS item's run root, so no launcher ever reaches
#     across a run root;
#   * TWO md5-pinned decomposeParDicts staged instead of one;
#   * memory 6g and H5 floor 8.0 GiB at np = 4 -- AV-1's and AV-1R's registered
#     figures for np = 4 on this exact mesh, inherited by citation;
#   * CHAIN_DONE, the fixed-name chain-end marker, written on every exit of a
#     started chain (SO-1b's form).
# The inherited comments below describe machinery that is unchanged.
# refuse on ANY sample below the floor); ALREADY_BOUGHT; AGGREGATE wait-and-retry.
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/so1c_run_arm.sh"
GRADER="$HERE/so1c_grade.py"
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv
SO1B_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt
TUT_SRC=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible
PERMISSION=bc0e687e
H5_FLOOR_GIB=8.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
# The launcher and grader are FROZEN (PREREGISTRATION.md section 7/8);
# asserted before EVERY arm so a mid-chain edit cannot change what runs.
MD5_LAUNCHER=12dd18eced7b67f04348cd29363d31e1   # RE-PINNED by AMENDMENT R7, 2026-08-31 (was 777c33117dd65d882a9be04d27c07526; SO-1bR's run root ADDED to FORBIDDEN_ROOTS)
MD5_GRADER=367f9fc25b3b34535cb2cddfafdc06b1   # RE-PINNED by AMENDMENT R6, 2026-08-28 (was 32af1c494db6884144151c7e7d7e81af)
MD5_RUNSCRIPT=0557da51f6f179f6de865144343c499f
MD5_XN=63d13c88fb915ab7695d6f1a9383a4ed
MD5_DECOMP_SCOTCH=816f5ba44075fde47fa5db4269877bc8
MD5_DECOMP_SIMPLE=194c330803077f0ffa4341f468c09768
# the shipped tutorial's INPUT bytes, frozen here because the checkout is not
MD5_TUT_RUNSCRIPT=0557da51f6f179f6de865144343c499f
MD5_TUT_GEN=681f10659eb90457fca13fc933008b93
MD5_TUT_PREPROC=4a9395452540705686acf94898aa33af
MD5_TUT_PS=51dfed28e1bdb4cd33e0d8d7dabd586a
MD5_TUT_SS=4a6b8ef4501494c7693b71e88a2eabbf
MD5_TUT_FFD=6ddf378b028d03d8a18270488bee1759
test $# -ge 1 || { echo "ABORT usage: so1c_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/so1c_driver.pid"
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
echo "$MD5_GRADER  $GRADER" | md5sum -c - || { echo "ABORT grader md5 drifted before staging"; exit 4; }
# ===========================================================================
# G-SO1B -- THE PRECONDITION, READ BEFORE THE RUN ROOT IS CREATED AND BEFORE THE
# FIRST LAUNCHER CALL.  SO-1c verifies the gradient AT SO-1b's OPTIMUM, so what
# it consumes is narrow and is named here rather than approximated by SO-1b's
# item verdict.
#
# WHAT IS CHECKED IS **NOT** SO-1b's ITEM VERDICT, AND THAT DISTINCTION IS THE
# POINT.  SO-1b's own registered predicted outcome is item `GATE FAIL` -- its
# SHIPPED row is PREDICTED to fail band D at shape[6] at the optimum, and THAT
# FAILURE IS SO-1b's FINDING.  Gating SO-1c on SO-1b's item verdict would kill
# SO-1c in exactly the case SO-1b expects.  The same defect was caught in this
# family one rung earlier, when SO-1b's brief proposed to gate on SO-1a's item
# verdict; the correction is inherited here rather than re-learned.
#
# WHAT SO-1c ACTUALLY CONSUMES, PER ROW:
#   * x*, the design point -- so an OPTIMUM must exist on that row;
#   * the np = 1 analytic gradient AT x* -- so the E arm must have completed;
#   * a REAL FLOW at x* -- so the re-solve must have recovered the lift.
# AND IT DELIBERATELY DOES NOT READ SO-1b's `G5E` FD GATE ON EITHER ROW.  SO-1c
# buys its OWN FD table at np = 4, because `DAFOAM_CHARTER.md` section 5 makes an
# FD reference part of a CONFIGURATION and never carries one across np; SO-1b's
# band-D verdict at np = 1 is therefore not a precondition of anything here.
#
# THE ACCEPTANCE IS ASYMMETRIC BY REGISTRATION, WITH ITS REASON:
#   * PATCHED requires G-OPT `PASS` -- IPOPT's own convergence statement.  It is
#     the CONTROL, and "post-optimum verification" at a point that is not an
#     optimum is a different item.  D1 and D13's five restarts converged on this
#     exact problem six times, so this is a band the problem has cleared six times.
#   * SHIPPED accepts `PASS` OR `GATE REACHED`.  SO-1c's shipped arm asks what a
#     DEFORMED MESH does to a parallel gradient; that question is meaningful at
#     the design point the shipped toolchain reached whether or not IPOPT
#     converged there.  A shipped row stopped at its iteration bound still
#     carries a deformed mesh and a real flow.
#   * BOTH rows require G-CL `PASS`: a design point whose re-solve did not put
#     the lift back is not a point with a real flow, and a gradient measured
#     there would be a gradient of nothing.
#
# TWO INDEPENDENT CHANNELS, AND A DISAGREEMENT REFUSES: (i) SO-1b's own grade
# artefact; (ii) SO-1b's `O-<row>/so1b_O.json`, re-read directly for the
# optimiser's EXIT line.  A grade that says PASS beside an artefact carrying no
# convergence statement is not a pass, it is a defect, and it stops the chain.
# ===========================================================================
# >>> G-SO1B-SELECT   AMENDMENT R6, 2026-08-28.  UNIQUENESS REFUSAL, NOT AN MTIME PICK.
# THE DEFECT THIS REMOVES, as frozen at v1.0:
#     so1b_grade_file() { ls -1t "$SO1B_BASE"/SO1b_grade_*.json ... | head -1; }
# `ls -1t | head -1` reduced a MULTI-MEMBER SET to one member by MTIME -- an
# ordering that is not the physics' ordering.  Which grade is THE grade of SO-1b
# is a FINDING; it is not a question sorting is allowed to answer.  ZERO grade
# files is the SAME BLOCKED branch as before, byte-for-byte; MORE THAN ONE is a
# NEW refusal.  The selection is RECORDED either way: the chosen file AND the
# full candidate list.
SO1B_GRADE_CANDS=$(ls -1 "$SO1B_BASE"/SO1bR_grade_*.json 2>/dev/null)
if [ -z "$SO1B_GRADE_CANDS" ]; then SO1B_GRADE_N=0; else SO1B_GRADE_N=$(printf '%s\n' "$SO1B_GRADE_CANDS" | wc -l); fi
if [ "$SO1B_GRADE_N" -eq 0 ]; then
  echo "ABORT G-SO1B no SO1bR_grade_*.json under $SO1B_BASE."
  echo "  SO-1c verifies the gradient AT SO-1b's OPTIMUM; with no graded optimum"
  echo "  there is no design point to verify at.  BLOCKED at ZERO core-minutes."
  echo "chain=BLOCKED_G_SO1B reason=no_grade stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "${BASE}.STATUS.preflight" 2>/dev/null
  exit 7
fi
if [ "$SO1B_GRADE_N" -ne 1 ]; then
  echo "ABORT G-SO1B $SO1B_GRADE_N files match SO1bR_grade_*.json under $SO1B_BASE."
  echo "  THIS DRIVER REFUSES TO PICK ONE.  Which grade is THE grade is a FINDING,"
  echo "  not an ordering question.  BLOCKED at ZERO core-minutes.  Candidates:"
  printf '    %s\n' $SO1B_GRADE_CANDS
  echo "chain=BLOCKED_G_SO1B reason=grade_selection_ambiguous n=$SO1B_GRADE_N stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "${BASE}.STATUS.preflight" 2>/dev/null
  exit 7
fi
SO1B_GRADE=$SO1B_GRADE_CANDS
echo "G_SO1B_GRADE_SELECTED file=$SO1B_GRADE n_candidates=$SO1B_GRADE_N candidates=$(printf '%s ' $SO1B_GRADE_CANDS)"
# <<< G-SO1B-SELECT
python3 - "$SO1B_GRADE" "$SO1B_BASE" <<'GSO1B'
import json, os, sys
grade_path, so1b_base = sys.argv[1], sys.argv[2]
def refuse(msg):
    sys.stderr.write("G-SO1B REFUSE %s\n" % msg)
    sys.exit(7)
try:
    g = json.load(open(grade_path))
except Exception as exc:
    refuse("SO-1b's grade artefact is unreadable (%s): %r" % (grade_path, exc))
gates = g.get("gates") or {}
ACCEPT = {"PATCHED": ("PASS",), "SHIPPED": ("PASS", "GATE REACHED")}
for row in ("PATCHED", "SHIPPED"):
    gopt = (gates.get("G-OPT_%s" % row) or {}).get("verdict")
    gcl = (gates.get("G-CL_%s" % row) or {}).get("verdict")
    if gopt is None or gcl is None:
        refuse("SO-1b's grade names no G-OPT/G-CL verdict for the %s row "
               "(G-OPT=%r G-CL=%r).  An unreadable dependency is not a licence "
               "to proceed." % (row, gopt, gcl))
    if gopt not in ACCEPT[row]:
        refuse("SO-1b's %s row G-OPT reads %r; SO-1c accepts %s on that row.  "
               "SO-1b's ITEM verdict is deliberately NOT read." % (row, gopt, " or ".join(ACCEPT[row])))
    if gcl != "PASS":
        refuse("SO-1b's %s row G-CL reads %r, not PASS.  A design point whose "
               "re-solve did not recover the lift has no real flow at it." % (row, gcl))
    # ---- CHANNEL (ii): SO-1b's own O artefact, re-read WITHOUT the grade
    o_path = os.path.join(so1b_base, "O-%s" % ("P" if row == "PATCHED" else "S"), "so1b_O.json")
    try:
        o = json.load(open(o_path))
    except Exception as exc:
        refuse("SO-1b's %s optimum artefact is unreadable (%s): %r" % (row, o_path, exc))
    exit_line = (o.get("ipopt") or {}).get("exit_line")
    converged = bool(exit_line) and "Optimal Solution Found" in str(exit_line)
    if gopt == "PASS" and not converged:
        refuse("CHANNEL DISAGREEMENT on the %s row: SO-1b's grade reads G-OPT PASS "
               "while its own artefact carries exit_line=%r.  A grade that says PASS "
               "beside an artefact with no convergence statement is a defect, not a "
               "pass." % (row, exit_line))
    for k in ("shape_opt", "patchV_opt"):
        if not o.get(k):
            refuse("SO-1b's %s optimum artefact carries no %r" % (row, k))
    # ---- and the E artefact SO-1c actually reads
    e_path = os.path.join(so1b_base, "E-%s" % ("P" if row == "PATCHED" else "S"), "so1b_E.json")
    try:
        e = json.load(open(e_path))
    except Exception as exc:
        refuse("SO-1b's %s post-optimum artefact is unreadable (%s): %r" % (row, e_path, exc))
    for k in ("design_point", "adjoint", "identity", "nprocs", "row"):
        if k not in e:
            refuse("SO-1b's %s post-optimum artefact lacks %r" % (row, k))
    if int(e["nprocs"]) != 1:
        refuse("SO-1b's %s post-optimum artefact records nprocs=%r; the serial "
               "reference must be np = 1" % (row, e["nprocs"]))
    if e["row"] != row:
        refuse("SO-1b's %s directory holds an artefact labelled row=%r -- a row is "
               "an image hash, never a directory name" % (row, e["row"]))
print("SO1C_G_SO1B_PASS grade=%s rows=PATCHED,SHIPPED gopt=%s/%s gcl=PASS/PASS "
      "channels=2 item_verdict_deliberately_not_read=yes"
      % (os.path.basename(grade_path),
         (gates.get("G-OPT_PATCHED") or {}).get("verdict"),
         (gates.get("G-OPT_SHIPPED") or {}).get("verdict")))
GSO1B
GRC=$?
if [ "$GRC" -ne 0 ]; then
  echo "ABORT G-SO1B refused (rc=$GRC).  SO-1c is BLOCKED at ZERO core-minutes; nothing was staged and no container started."
  exit 7
fi

# ---- (4) ROOT STAGING on the first fire only ------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$TUT_SRC" || { echo "ABORT tutorial source absent: $TUT_SRC"; exit 4; }
  { echo "$MD5_TUT_RUNSCRIPT  $TUT_SRC/runScript.py"; echo "$MD5_TUT_GEN  $TUT_SRC/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $TUT_SRC/preProcessing.sh";
    echo "$MD5_TUT_PS  $TUT_SRC/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $TUT_SRC/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $TUT_SRC/FFD/wingFFD.xyz"; } | md5sum -c - \
    || { echo "ABORT tutorial input md5 drifted (the checkout moved under this item; nothing staged)"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  mkdir -p "$BASE/base" || exit 4
  cp -a "$TUT_SRC/0.orig" "$TUT_SRC/FFD" "$TUT_SRC/constant" "$TUT_SRC/system" "$TUT_SRC/profiles" "$TUT_SRC/genAirFoilMesh.py" "$TUT_SRC/preProcessing.sh" "$BASE/base/" || { echo "ABORT copy tutorial inputs"; exit 4; }
  rm -rf "$BASE/base/constant/polyMesh" 2>/dev/null
  # base/ carries the SCOTCH dict so the MESH arm is md5-checkable against a
  # registered file; every solver arm OVERLAYS its own dict at staging and the
  # launcher re-asserts the md5 ON THE OVERLAID COPY.
  cp -a "$HERE/so1c_decomposeParDict_scotch" "$BASE/base/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict"; exit 4; }
  cp -a "$HERE/so1c_runScript.py" "$HERE/so1c_xn.py" "$HERE/so1c_decomposeParDict_scotch" "$HERE/so1c_decomposeParDict_simple" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  # ---- THE STAGED INPUTS FROM SO-1b, COPIED ONCE, PER ROW, INTO THIS ITEM'S
  # ---- OWN RUN ROOT.  The launcher never reaches across a run root; it reads
  # ---- only `$BASE/optref/`, which is this item's own directory.  The copies
  # ---- keep SO-1b's mtimes (`cp -a`), which is what makes them provably
  # ---- STAGED INPUTS and not products of this run.
  mkdir -p "$BASE/optref/PATCHED" "$BASE/optref/SHIPPED" || { echo "ABORT cannot create optref"; exit 4; }
  cp -a "$SO1B_BASE/E-P/so1b_E.json" "$BASE/optref/PATCHED/so1b_E.json" || { echo "ABORT copy SO-1b PATCHED optimum"; exit 4; }
  cp -a "$SO1B_BASE/E-S/so1b_E.json" "$BASE/optref/SHIPPED/so1b_E.json" || { echo "ABORT copy SO-1b SHIPPED optimum"; exit 4; }
  # ---- and SO-1b's OWN MESH FINGERPRINT.  `ADJOINT_VERIFICATION_STANDARD.md`
  # ---- section 3 defines np-invariance as "the same gradient at the same design
  # ---- point ON THE SAME MESH and image".  SO-1c regenerates the mesh in its own
  # ---- MESH arm rather than reading one across a run root, so MESH IDENTITY IS
  # ---- NOT FREE AND IS NOT ASSUMED: the `points` sha256 SO-1b's MESH arm printed
  # ---- is copied here and G-MESHID compares it to this item's own.  An inequality
  # ---- is a mesh-regeneration-determinism finding and makes the comparison
  # ---- ungradeable -- it is NOT waved through.
  # >>> G-MESHREF-SELECT   AMENDMENT R6, 2026-08-28.  UNIQUENESS REFUSAL.
  # THE DEFECT THIS REMOVES, as frozen at v1.0:
  #     grep -ah "constant/polyMesh/points" "$SO1B_BASE"/MESH_*.log ... | head -4
  # a MULTI-FILE grep reduced to four lines by OUTPUT ORDER -- and under ugrep
  # (7.8.4 on this box) multi-file output order is a RACE, so it is not even
  # reliably first-wins.  It is the SAME defect as the grader's last-wins loop,
  # on the OTHER side of the same equality test: this is the REFERENCE, SO-1b's
  # root; the grader's is the SUBJECT, SO-1c's own.  BOTH SIDES NOW REFUSE ON A
  # MULTI-MEMBER SET, so the two sides cannot disagree about what "the" mesh is.
  # ONE NAMED FILE IS READ.  The selection is RECORDED beside the reference.
  SO1B_MESH_CANDS=$(ls -1 "$SO1B_BASE"/MESH_*.log 2>/dev/null)
  if [ -z "$SO1B_MESH_CANDS" ]; then SO1B_MESH_N=0; else SO1B_MESH_N=$(printf '%s\n' "$SO1B_MESH_CANDS" | wc -l); fi
  if [ "$SO1B_MESH_N" -ne 1 ]; then
    echo "ABORT G-MESHREF $SO1B_MESH_N files match MESH_*.log under $SO1B_BASE (exactly one is required)."
    echo "  The mesh fingerprint SO-1c compares against must come from ONE NAMED file."
    echo "  A multi-member set reduced by grep's multi-file output order is not a"
    echo "  reference.  Candidates:"
    printf '    %s\n' $SO1B_MESH_CANDS
    exit 4
  fi
  SO1B_MESH_LOG=$SO1B_MESH_CANDS
  grep -a "constant/polyMesh/points" "$SO1B_MESH_LOG" > "$BASE/optref/so1b_mesh_points_sha256.txt"
  SO1B_MESH_REF_N=$(wc -l < "$BASE/optref/so1b_mesh_points_sha256.txt")
  if [ "$SO1B_MESH_REF_N" -ne 1 ]; then
    echo "ABORT G-MESHREF $SO1B_MESH_LOG carries $SO1B_MESH_REF_N points-sha256 lines (exactly one is required)."
    echo "  A reference that names no mesh, or more than one, is not a reference."
    exit 4
  fi
  { echo "G_MESHREF_SELECTED file=$SO1B_MESH_LOG n_candidates=$SO1B_MESH_N sha_lines=$SO1B_MESH_REF_N"
    echo "G_MESHREF_CANDIDATES $(printf '%s ' $SO1B_MESH_CANDS)"; } | tee "$BASE/optref/so1b_mesh_points_sha256.SELECTION.txt"
  # <<< G-MESHREF-SELECT
  echo "SO1C_OPTREF_STAGED patched=$(md5sum "$BASE/optref/PATCHED/so1b_E.json" | cut -d\  -f1) shipped=$(md5sum "$BASE/optref/SHIPPED/so1b_E.json" | cut -d\  -f1) mesh_ref_lines=$(wc -l < "$BASE/optref/so1b_mesh_points_sha256.txt") source=$SO1B_BASE"
  # D5-DRIVER-DEF-1 corrected form, inherited: identity on its own line;
  # staging metadata on a line that does not start with ITEM=.
  echo "ITEM=SO1c" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) tut_src=$TUT_SRC tut_commit=$(git -C "$TUT_SRC" rev-parse HEAD 2>/dev/null || echo NOT_MEASURED) permission=$PERMISSION" >> "$BASE/ledger.txt"
  echo "SO1C_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "SO1C_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT  $BASE/so1c_runScript.py"; echo "$MD5_XN  $BASE/so1c_xn.py";
  echo "$MD5_DECOMP_SCOTCH  $BASE/so1c_decomposeParDict_scotch"; echo "$MD5_DECOMP_SIMPLE  $BASE/so1c_decomposeParDict_simple";
  echo "$MD5_DECOMP_SCOTCH  $BASE/base/system/decomposeParDict";
  echo "$MD5_TUT_GEN  $BASE/base/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $BASE/base/preProcessing.sh";
  echo "$MD5_TUT_PS  $BASE/base/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $BASE/base/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $BASE/base/FFD/wingFFD.xyz"; } | md5sum -c - || { echo "ABORT staged instrument/input md5"; exit 4; }
test -f "$BASE/base/0.orig/U" || { echo "ABORT staged base/ has no 0.orig/U"; exit 4; }
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
# ---- CHAIN_DONE: the FIXED-NAME chain-end marker, written on EVERY exit of a
# ---- STARTED chain (SO-1b's form, so1b_chain_driver.sh:196).  SO-1a had none,
# ---- which is why SO-1b had to wait on a last-arm artefact instead.  A
# ---- successor may still prefer the last-arm artefact -- a marker fires on a
# ---- FAILED chain too, and an artefact does not.
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ arms=[$ARMS]" >> "$BASE/CHAIN_DONE"' EXIT
echo "SO1C_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { case "$1" in MESH) echo 4 ;; *) echo 6 ;; esac; }   # MESH 4g at np=1; every np=4 arm 6g -- AV-1/AV-1R's registered figure for np=4 on THIS mesh, inherited by citation and not re-derived (PREREGISTRATION.md section 4)
img_of() { case "$1" in MESH|*-S) echo "$IMG_SHIPPED" ;; *-P) echo "$IMG_PATCHED" ;; *) echo "" ;; esac; }
CHAIN_RC=0
for ARM in $ARMS; do
  IMG=$(img_of "$ARM"); test -n "$IMG" || { echo "ABORT arm $ARM names no registered row"; echo "chain=ABORT arm=$ARM reason=no_row stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=64; break; }
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=4; break; }
  # ---- (5) STATUS.<arm> is OPENED here (preflight line) and APPENDED from now
  # ---- on; the LAST line carries the rc.  Every AGGREGATE_WAIT is a line in it.
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ image=$IMG permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  # ---- (3) ALREADY BOUGHT: a launcher-written rc=0 row for this arm means a
  # ---- re-fire would re-stage a graded arm.  REFUSED.
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=3; break
  fi
  # ---- H5: a WINDOW of MemAvailable, every sample above the floor
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "SO1C_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=6; break
  fi
  # ---- (2) AGGREGATE: live container caps + this cap + host non-container RSS,
  # ---- WAIT-AND-RETRY (UPDATE F ruling): poll AGG_POLL_S, bounded AGG_BOUND_S;
  # ---- every wait written to STATUS.<arm>; refuse-and-BLOCK at the bound.
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"; AGG_BLOCKED=no
  while true; do
    AGG=$(python3 "$HERE/so1c_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s.  BLOCKED.  Series: $(basename "$AGG_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; AGG_BLOCKED=yes; break
    fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  if [ "$AGG_BLOCKED" = "yes" ]; then CHAIN_RC=6; break; fi
  echo "SO1C_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  echo "SO1C_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "SO1C_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=$rc; break; fi
done
[ "$CHAIN_RC" -eq 0 ] && echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
# ---- (6) the FROZEN grader on the artefacts (zero compute); its rc is INFRASTRUCTURE (L-342)
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/SO1c_grade_${GSTAMP}.json" > "$BASE/SO1c_grade_${GSTAMP}.out" 2>&1; GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=SO1c_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi
echo "SO1C_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC"
exit "$CHAIN_RC"
