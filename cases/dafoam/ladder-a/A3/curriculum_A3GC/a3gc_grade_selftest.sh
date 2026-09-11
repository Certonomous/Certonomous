#!/usr/bin/env bash
# =====================================================================
# a3gc_grade_selftest.sh -- **FROZEN by the dafoam-supervisor, 2026-09-11.**
#
# The executable half of the A3GC grading path.  It does not assert that
# a3gc_grade.py is correct; it MAKES IT PROVE IT, by running it.
#
#   * Every reader that can return a zero or a pass PLANTS a known
#     perturbation, reads it back THROUGH THE REAL PATH, and the test fails
#     if the reader cannot see it (CLAUDE.md rule 3; PREREG Sec.3.4).
#     The plants go into THIS FAMILY'S OWN ON-DISK FORMAT -- owner.gz, an
#     ADF-format CGNS, a DAFoam solver log -- because Sec.3.4 records a
#     reader that returned a false zero on every A3/M6 tree while correctly
#     finding 7 cases elsewhere: these meshes store owner.gz, not owner.
#     A reader shown able to see a non-zero SOMEWHERE is not shown able to
#     see one IN THE CLASS BEING ASKED ABOUT.
#
#   * A SUITE THAT PASSES PROVES NOTHING UNTIL IT IS SEEN TO FAIL.  Every
#     gate is fed a deliberately-wrong input and must REFUSE.  In
#     particular B9 reproduces the cfd team's DrivAer Gate A1 plateau
#     defect -- a two-sample increment wearing a plateau's name -- and
#     asserts G-PLAT catches it.
#
#   * NO GRADED RUN ROOT IS WRITTEN INTO.  Every plant and every fixture
#     lives in a scratch directory; the real artifacts are sha256'd by the
#     comparator's own Untouched() guard and asserted byte-identical, and
#     B13 checks that guard by hand as well.
#
# SUBMISSIONS PARKED.  Nothing here sends anything anywhere.
#
# Usage:  bash a3gc_grade_selftest.sh [scratch-dir]
# Exit:   0 only if every test passed.
# =====================================================================
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../../.." && pwd)"
GRADE="$HERE/a3gc_grade.py"
PY="${PYTHON:-python3}"

SCRATCH="${1:-${TMPDIR:-/tmp}/a3gc_selftest.$$}"
mkdir -p "$SCRATCH"

# ---- real artifacts of THIS family, read-only ------------------------
REAL_CASE="/home/ubuntu/certonomous-runs/A3-onera-m6-transonic"          # 399,360 cells, wing 6240
TRAP_CASE="/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse"     # 99,840 cells, wing 1560  <-- THE TRAP
PROBE="/home/ubuntu/certonomous-runs/A3GC-mesh-family-probe"
S_C0="$PROBE/m6_surfaceMesh_fine.cgns"
S_C1="$PROBE/s_c1.cgns"
S_C2="$PROBE/s_c2.cgns"
S_C3="$PROBE/s_c3.cgns"
REAL_LOG="$REPO/cases/dafoam/ladder-a/logs_A3/run_model_run3.log"

NPASS=0; NFAIL=0; FAILED=()

ok()   { NPASS=$((NPASS+1)); printf '  [PASS] %s\n' "$1"; }
bad()  { NFAIL=$((NFAIL+1)); FAILED+=("$1"); printf '  [FAIL] %s\n' "$1"; }
head1(){ printf '\n== %s ==\n' "$1"; }

# expect_rc <want> <name> <cmd...>
expect_rc() {
  local want="$1" name="$2"; shift 2
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" = "$want" ]; then ok "$name (rc=$rc)"
  else
    bad "$name (wanted rc=$want, got rc=$rc)"
    printf '%s\n' "$out" | tail -12 | sed 's/^/        | /'
  fi
}

# expect_out <regex> <name> <cmd...>
expect_out() {
  local rx="$1" name="$2"; shift 2
  local out
  out="$("$@" 2>&1)"
  if printf '%s' "$out" | grep -qE "$rx"; then ok "$name"
  else
    bad "$name (output did not match /$rx/)"
    printf '%s\n' "$out" | tail -12 | sed 's/^/        | /'
  fi
}

# expect_refusal <refuse-code-regex> <name> <cmd...>
#   rc == 2 IS NOT ENOUGH.  argparse ALSO exits 2 on an unrecognised argument,
#   so a stale flag in this file made FIVE `expect_rc 2` units pass on an
#   ARGPARSE USAGE ERROR while the gate they name was never reached.  Measured
#   by this lane 2026-09-11: B1b / B2a / B3a / B5a / B14 all passed that way
#   after AMENDMENT 2(a) removed the struck limb-5 flag.  A refusal unit now
#   demands rc == 2 AND the comparator's own `REFUSE [CODE]` banner, so a usage
#   error can never wear a gate's name.
expect_refusal() {
  local code="$1" name="$2"; shift 2
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" = 2 ] && printf '%s' "$out" | grep -qE "REFUSE \[$code\]"; then
    ok "$name (rc=2, REFUSE [$code])"
  else
    bad "$name (wanted rc=2 AND REFUSE [$code]; got rc=$rc)"
    printf '%s\n' "$out" | tail -12 | sed 's/^/        | /'
  fi
}

# expect_no_out <regex> <name> <cmd...> -- the output must NOT match.
expect_no_out() {
  local rx="$1" name="$2"; shift 2
  local out
  out="$("$@" 2>&1)"
  if printf '%s' "$out" | grep -qE "$rx"; then
    bad "$name (output matched /$rx/ and must not have)"
    printf '%s\n' "$out" | grep -nE "$rx" | head -4 | sed 's/^/        | /'
  else ok "$name"; fi
}

# ---------------------------------------------------------------------
# fixture builder -- synthetic run roots and synthetic solver logs.
# These are FABRICATED TEST FIXTURES.  They live only in the scratch dir,
# they never enter a run root, and no number in this file is a lab
# measurement.  Every fixture file carries a banner saying so.
# ---------------------------------------------------------------------
mkfix() { "$PY" - "$@" <<'FIXPY'
import gzip, os, shutil, sys

BANNER = ("// SYNTHETIC TEST FIXTURE generated by a3gc_grade_selftest.sh.\n"
          "// NOT A MEASUREMENT.  Not evidence.  Never copy into a run root.\n")

def owner(root, ncells, npoints=0, nfaces=0, gz=True):
    d = os.path.join(root, "constant", "polyMesh"); os.makedirs(d, exist_ok=True)
    txt = (BANNER + "FoamFile\n{\n    version 2.0;\n    format binary;\n"
           "    note        \"nPoints:%d  nCells:%d  nFaces:%d  nInternalFaces:%d\";\n"
           "    class labelList;\n    object owner;\n}\n" % (npoints or ncells+1, ncells,
                                                             nfaces or ncells*3, nfaces or ncells*3))
    if gz:
        with gzip.open(os.path.join(d, "owner.gz"), "wb") as fh: fh.write(txt.encode())
    else:
        open(os.path.join(d, "owner"), "w").write(txt)

def boundary(root, wing, inout=None, sym=8704, wing_type="wall"):
    d = os.path.join(root, "constant", "polyMesh"); os.makedirs(d, exist_ok=True)
    inout = wing if inout is None else inout
    t = BANNER + "FoamFile\n{\n    version 2.0;\n    object boundary;\n}\n\n3\n(\n"
    for nm, ty, nf in (("wing", wing_type, wing), ("inout", "patch", inout),
                       ("sym", "symmetry", sym)):
        t += "    %s\n    {\n        type            %s;\n        nFaces          %d;\n" \
             "        startFace       1;\n    }\n" % (nm, ty, nf)
    t += ")\n"
    open(os.path.join(d, "boundary"), "w").write(t)

def log(path, cd_hist, cl_hist, initres=1.0e-07, tol=1e-08, diff=100,
        printInterval=100, end=True, extra_initres=None):
    L = ["// " + BANNER.replace("// ", "").strip().replace("\n", "\n// "),
         "DAFoam option dictionary: ", "{",
         "    solverName      DARhoSimpleCFoam;",
         "    primalMinResTol %g;" % tol,
         "    printInterval   %d;" % printInterval,
         "    primalMinResTolDiff %g;" % diff, "}", "",
         "Starting time loop", ""]
    n = len(cd_hist)
    for i, (cd, cl) in enumerate(zip(cd_hist, cl_hist)):
        t = 1 if i == 0 else i * printInterval
        L.append("Time = %d" % t); L.append("")
        ir = initres if (i < n - 1 or extra_initres is None) else extra_initres
        for eq in ("U0", "U1", "U2", "he", "p"):
            L.append("%s initRes: %.17g finalRes: %.17g nIters: 2" % (eq, ir, ir * 0.1))
        L.append("Time step continuity errors : sum local = 1e-09")
        L.append("nuTilda initRes: %.17g finalRes: %.17g nIters: 3" % (ir, ir * 0.1))
        L.append("CD: %.17g final: %.17g" % (cd, cd))
        L.append("CL: %.17g final: %.17g" % (cl, cl))
        L.append("yPlus min: 5.6 max: 103.5 mean: 33.7")
        L.append("ExecutionTime = %.2f s  ClockTime = %d s" % (20.0 * (i + 1), 20 * (i + 1)))
        L.append("")
    if end: L.append("End")
    open(path, "w").write("\n".join(L) + "\n")

def complete(root, endtime, fields=("T", "U", "p", "alphat", "nut", "nuTilda"),
             rc=0, rc_name="log.primal.rc", end_newer=True, write_end=True,
             end_fields=None):
    """Make `root` satisfy PREREG Sec.3.7 / CLAUDE.md rule 4.

    Writes system/controlDict (endTime), the solver exit code, a `0` directory,
    and the endTime directory.  MTIMES ARE SET EXPLICITLY, because the age guard
    reads them: every `0` field is backdated 200 s, `0/T` 100 s (it is touched
    LAST at launch and so dates the run allowed to produce the answer), and the
    endTime fields are `now`.  SYNTHETIC TEST FIXTURE.  NOT A MEASUREMENT.
    """
    import time as _t
    os.makedirs(os.path.join(root, "system"), exist_ok=True)
    open(os.path.join(root, "system", "controlDict"), "w").write(
        BANNER + "FoamFile\n{\n    version 2.0;\n    object controlDict;\n}\n"
        "stopAt          endTime;\nendTime         %g;\ndeltaT          1;\n"
        "writeInterval   %g;\n" % (endtime, endtime))
    open(os.path.join(root, rc_name), "w").write("%d\n" % rc)
    now = _t.time()
    z = os.path.join(root, "0"); os.makedirs(z, exist_ok=True)
    for f in fields:
        p = os.path.join(z, f)
        open(p, "w").write(BANNER + "placeholder initial condition for %s\n" % f)
        os.utime(p, (now - 200, now - 200))
    os.utime(os.path.join(z, "T"), (now - 100, now - 100))
    e = os.path.join(root, "%g" % endtime)
    # CLEAR IT FIRST.  These fixtures are built by `cp -a` from a COMPLETE case,
    # so an endTime directory is usually already there; without this,
    # write_end=False and a reduced end_fields both silently leave the ORIGINAL
    # complete directory in place and the clause under test never fires.
    # Measured: that is exactly what made F1c and F4 pass vacuously on the first
    # run of this section.
    shutil.rmtree(e, ignore_errors=True)
    if write_end:
        os.makedirs(e, exist_ok=True)
        for f in (end_fields if end_fields is not None else fields):
            p = os.path.join(e, f)
            open(p, "w").write(BANNER + "written field %s at t=%g\n" % (f, endtime))
            st = now if end_newer else now - 150      # -150 is OLDER than 0/T
            os.utime(p, (st, st))


def flat(v, n=12, jitter=1e-8):
    return [v + jitter * ((-1) ** i) for i in range(n)]

def drift(v, n=12, step=1.0e-4):
    """THE DrivAer Gate A1 DEFECT, reproduced on purpose.  Each adjacent
    sample differs by only `step`, so an adjacent-sample-delta criterion
    sees a tiny number and passes; the 10-sample EXCURSION is 9*step and
    the signal is not plateaued at all."""
    return [v + step * i for i in range(n)]

if __name__ == "__main__":
    exec(sys.argv[1])
FIXPY
}

printf '=========================================================================\n'
printf 'A3GC GRADING-PATH SELFTEST (DRAFT)\n'
printf 'comparator : %s\n' "$GRADE"
printf 'scratch    : %s\n' "$SCRATCH"
printf '=========================================================================\n'

# =====================================================================
head1 "PRECONDITIONS -- the real artifacts this suite reads"
# =====================================================================
for f in "$GRADE" "$REAL_LOG" "$S_C0" "$S_C1" "$S_C2" "$S_C3"; do
  if [ -r "$f" ]; then ok "readable: $f"; else bad "MISSING: $f"; fi
done
for d in "$REAL_CASE" "$TRAP_CASE"; do
  if [ -d "$d" ]; then ok "readable: $d"; else bad "MISSING: $d"; fi
done
# record the sha256 of every real artifact this suite touches, so B13 can
# prove none of them moved.
SHAS="$SCRATCH/real_shas.before"
( sha256sum "$REAL_LOG" "$S_C0" "$S_C1" "$S_C2" "$S_C3" \
    "$REAL_CASE/constant/polyMesh/owner.gz" "$REAL_CASE/constant/polyMesh/boundary" \
    "$REPO/cases/dafoam/ladder-a/logs_A3/extract_cp.py" \
    "$REPO/cases/dafoam/ladder-a/logs_A3/compare_cp.py" \
    "$REPO/cases/dafoam/ladder-a/logs_A3/shock_location.py" \
    "$REPO/cases/dafoam/ladder-a/logs_A3/case_2308.dat" ) > "$SHAS" 2>/dev/null

# =====================================================================
head1 "A -- PLANTED-ZERO CONTROLS (this family's own on-disk format)"
# =====================================================================
expect_rc 0 "A1-A6 every reader sees its planted perturbation" \
  "$PY" "$GRADE" plant --scratch "$SCRATCH/plant" \
    --case "$REAL_CASE" --cgns "$S_C2" --log "$REAL_LOG"

expect_out 'ALL PLANTED CONTROLS SEEN' "A1-A6 the suite says so out loud" \
  "$PY" "$GRADE" plant --scratch "$SCRATCH/plant2" \
    --case "$REAL_CASE" --cgns "$S_C2" --log "$REAL_LOG"

# A7 -- THE FORMAT TRAP OF Sec.3.4, all three ways round.
#   (a) owner.gz only  -- what this family actually ships.  Must be READ.
mkfix 'owner(sys.argv[2], 12345, gz=True); boundary(sys.argv[2], 6240)' "$SCRATCH/fmt_gz"
expect_out '"cells": 12345' "A7a reader sees owner.gz (the format this family ships)" \
  "$PY" "$GRADE" probe --case "$SCRATCH/fmt_gz"
#   (b) plain owner only -- must ALSO be read, so the reader is not gz-only.
mkfix 'owner(sys.argv[2], 54321, gz=False); boundary(sys.argv[2], 6240)' "$SCRATCH/fmt_plain"
expect_out '"cells": 54321' "A7b reader sees plain owner too" \
  "$PY" "$GRADE" probe --case "$SCRATCH/fmt_plain"
#   (c) NEITHER -- must REFUSE (exit 2).  It must never report 0 cells.
mkdir -p "$SCRATCH/fmt_none/constant/polyMesh"
expect_refusal 'READ' "A7c neither owner nor owner.gz -> REFUSES, never reports 0" \
  "$PY" "$GRADE" probe --case "$SCRATCH/fmt_none"
expect_out 'FALSE ZERO' "A7c the refusal names the false-zero it is preventing" \
  "$PY" "$GRADE" probe --case "$SCRATCH/fmt_none"

# A8 -- the ADF coordinate reader reproduces the pre-registration's own
#       Sec.2.3/Sec.2.4 measurements, by a different tool path.
expect_out '"cgns_points": 6765' "A8a c2 reads 6,765 points (PREREG Sec.2.3)" \
  "$PY" "$GRADE" probe --case "$REAL_CASE" --cgns "$S_C2"
expect_out '"cgns_points": 101913' "A8b c0 reads 101,913 points (PREREG Sec.2.3)" \
  "$PY" "$GRADE" probe --case "$REAL_CASE" --cgns "$S_C0"
expect_out '\-0\.0394263' "A8c c0 bbox y = -0.039426 (PREREG Sec.2.4)" \
  "$PY" "$GRADE" probe --case "$REAL_CASE" --cgns "$S_C0"
expect_out '\-0\.0393[12]' "A8d c3 bbox y = -0.039320, the collapsed TE (PREREG Sec.2.4)" \
  "$PY" "$GRADE" probe --case "$REAL_CASE" --cgns "$S_C3"

# =====================================================================
head1 "C1 -- CONTROL: a clean triple must PASS, or nothing below means anything"
# =====================================================================
# Registered family geometry (Sec.2.5), a CONVERGING CD/CL triple with
# p = 2 exactly (eps32/eps21 = 4 at r = 2), and plateaued histories.
build_clean() {
  local base="$1"
  for spec in "L3:99840:6240:$S_C2" "L2:798720:24960:$S_C1" "L1:6389760:99840:$S_C0"; do
    IFS=: read -r lv nc nf surf <<<"$spec"
    local r="$base/$lv"; mkdir -p "$r"
    mkfix "owner(sys.argv[2], $nc); boundary(sys.argv[2], $nf)" "$r"
    cp "$surf" "$r/surfaceMesh.cgns"
  done
  # CD: L1 0.0229956, L2 +2e-4, L3 +8e-4   -> p = 2, GCI ~ 0.36 %
  # CL: L1 0.3131159, L2 +1e-3, L3 +4e-3   -> p = 2, GCI ~ 0.13 %
  mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0239956), flat(0.3181159))' "$base/L3"
  mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0231956), flat(0.3141159))' "$base/L2"
  mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0229956), flat(0.3131159))' "$base/L1"
  # Sec.3.7 / rule 4: each level must also be COMPLETE.  The 12-sample log runs
  # Time = 1, 100, 200 ... 1100, so endTime is 1100.
  for lv in L3 L2 L1; do mkfix 'complete(sys.argv[2], 1100)' "$base/$lv"; done
}
build_clean "$SCRATCH/clean"
CLEAN=( --l3 "$SCRATCH/clean/L3" --l2 "$SCRATCH/clean/L2" --l1 "$SCRATCH/clean/L1"
        --log-name log.primal )

expect_out 'VERDICT  CD triple +: PASS' "C1a a clean CD triple grades PASS" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'VERDICT  CL triple +: PASS' "C1b a clean CL triple grades PASS" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'observed order p = 2\.0000' "C1c observed order p recovers 2.0000 exactly" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'GCI\(fine, Fs=1\.25\)' "C1d GCI is quoted on a monotone triple" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
# ---- C1e/C1f/C1g  REPLACE the pre-AMENDMENT-2 limb-5 units.
# WHAT WAS HERE, and why it is gone: C1e used to pass
# --limb5-unpinned-recipe-diagnostic and assert that the flag FORCED the overall
# to NOT A RESULT.  AMENDMENT 2(a) STRUCK Sec.3.1 limb 5 as a gate -- as
# UNMEASURABLE AS WRITTEN, demonstrated by measurement, NOT because it failed --
# and demoted it to a printed diagnostic, so neither the flag nor the forcing
# exists.  The assertion is not dropped, it is INVERTED and made sharper: on the
# REAL registered family the struck limb reads a 100 % spread at mid and tip
# (AMENDMENT 2(a)'s own measured figures), and the item must grade anyway.  A
# struck limb that still moved a verdict would be the amendment not applied.
expect_out 'limb5 root    DIAGNOSTIC: spread = 0\.0243 %' \
  "C1e the struck limb 5 is REPORTED, at AMENDMENT 2(a)'s own measured root spread" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'limb5 (mid|tip) +DIAGNOSTIC: spread = 100\.0000 %.*would have said FAIL' \
  "C1f the struck limb WOULD have said FAIL on the registered family..." \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'limb5 +\*\*\* REPORTED, NEVER GATING' \
  "C1g ...and it does not gate: it says so, and C1a/C1b PASS beside it" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
# and the REPLACEMENT gate of AMENDMENT 2(a) is green on the real surfaces:
expect_out 'G-NEST +every L3 point present BIT-EXACTLY in L2 : 0 misses of 6765 +OK' \
  "C1h G-NEST (limb 5', the stronger replacement) is green on the real family" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"

# =====================================================================
head1 "B -- MUTATION CONTROLS: every gate must be SEEN to refuse"
# =====================================================================

# ---- B1  THE TRAP.  Measured on disk 2026-09-11:
#      /home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse has EXACTLY
#      99,840 cells -- the registered L3 count -- and `wing` nFaces = 1560
#      (surface c3, N=65).  The registered L3 is 99,840 cells with `wing`
#      nFaces = 6240 (surface c2, N=17).  SAME CELL COUNT, DIFFERENT BODY,
#      DIFFERENT DISCRETISATION.  Cell count alone does not identify a level.
head1 "B1 -- the 99,840-cell impostor offered as L3"
cp -a "$SCRATCH/clean" "$SCRATCH/trap"
rm -rf "$SCRATCH/trap/L3/constant"
mkdir -p "$SCRATCH/trap/L3/constant/polyMesh"
cp "$TRAP_CASE/constant/polyMesh/owner.gz"  "$SCRATCH/trap/L3/constant/polyMesh/"
cp "$TRAP_CASE/constant/polyMesh/boundary"  "$SCRATCH/trap/L3/constant/polyMesh/"
cp "$S_C3" "$SCRATCH/trap/L3/surfaceMesh.cgns"
TRAPARGS=( --l3 "$SCRATCH/trap/L3" --l2 "$SCRATCH/trap/L2" --l1 "$SCRATCH/trap/L1"
           --log-name log.primal )
expect_out 'cells=99840' "B1a the impostor's cell count MATCHES the registered L3" \
  "$PY" "$GRADE" grade "${TRAPARGS[@]}"
expect_refusal 'G-SYS' "B1b G-SYS REFUSES the impostor" \
  "$PY" "$GRADE" grade "${TRAPARGS[@]}"
expect_out 'limb2 faces +L2/L3 = 24960/1560' \
  "B1c the face-count limb is what catches it (ratio 16, not 4)" \
  "$PY" "$GRADE" grade "${TRAPARGS[@]}"
expect_out 'Cell count alone does not identify a level' \
  "B1d the refusal says why in as many words" \
  "$PY" "$GRADE" grade "${TRAPARGS[@]}"
expect_out 'limb4 bbox +L3 vs L1 : max \|d\| = 1\.0[0-9]*e-04' \
  "B1e the bbox limb independently catches c3's collapsed TE (13x the tolerance)" \
  "$PY" "$GRADE" grade "${TRAPARGS[@]}"

# ---- B2  cell-count ratio / registered count
head1 "B2 -- a level with the wrong cell count"
cp -a "$SCRATCH/clean" "$SCRATCH/mut_cells"
mkfix 'owner(sys.argv[2], 800000); boundary(sys.argv[2], 24960)' "$SCRATCH/mut_cells/L2"
expect_refusal 'G-SYS' "B2a a 800,000-cell L2 (ratio 8.013) is REFUSED" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_cells/L3" --l2 "$SCRATCH/mut_cells/L2" \
    --l1 "$SCRATCH/mut_cells/L1" --log-name log.primal
expect_out 'launch-blocking refusal, not a note' "B2b the refusal quotes Sec.2.5" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_cells/L3" --l2 "$SCRATCH/mut_cells/L2" \
    --l1 "$SCRATCH/mut_cells/L1" --log-name log.primal

# ---- B3  coordinate limb: two levels handed the SAME surface
head1 "B3 -- two levels handed the identical surface"
cp -a "$SCRATCH/clean" "$SCRATCH/mut_same"
cp "$S_C2" "$SCRATCH/mut_same/L2/surfaceMesh.cgns"
expect_refusal 'G-SYS' "B3a identical coordinate arrays on L3 and L2 are REFUSED" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_same/L3" --l2 "$SCRATCH/mut_same/L2" \
    --l1 "$SCRATCH/mut_same/L1" --log-name log.primal
expect_out 'limb3 coords .*DIFFER : FAIL' "B3b the coordinate limb is what fails" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_same/L3" --l2 "$SCRATCH/mut_same/L2" \
    --l1 "$SCRATCH/mut_same/L1" --log-name log.primal

# ---- B4  nesting limb: a surface that is NOT a coarsening of the finer one
head1 "B4 -- a surface whose points are not a subset of the finer level's"
cp -a "$SCRATCH/clean" "$SCRATCH/mut_nest"
"$PY" - "$S_C2" "$SCRATCH/mut_nest/L3/surfaceMesh.cgns" <<'PERTURB'
import shutil, struct, sys
src, dst = sys.argv[1], sys.argv[2]
shutil.copy2(src, dst)
b = bytearray(open(dst, "rb").read())
# nudge the first CoordinateY double by 1e-6: still inside the bbox tolerance,
# but no longer a member of the finer level's point set.
i = b.find(b"NoDeCoordinateY")
# locate that node's data pointer: 4+32+32+8+8+12+32+2+96+4 = 230 from 'NoDe'
off_field = i + 230
s = bytes(b[off_field:off_field+12]).decode()
off = int(s[:8], 16) * 4096 + int(s[8:], 16) + 16
v = struct.unpack("<d", bytes(b[off:off+8]))[0]
b[off:off+8] = struct.pack("<d", v + 1.0e-6)
open(dst, "wb").write(bytes(b))
print("perturbed one CoordinateY by 1e-6")
PERTURB
# The regex here was written against a pre-AMENDMENT-2 print that called the
# limb "nested".  AMENDMENT 2(a) registered it as G-NEST (limb 5') and the
# comparator prints that name.  The BEHAVIOUR asserted is unchanged and is
# STRENGTHENED: the nudge must be caught (1 miss, FAIL) AND the run must refuse.
expect_out 'G-NEST +every L3 point present BIT-EXACTLY in L2 : 1 misses of 6765 +FAIL' \
  "B4a a single 1e-6 coordinate nudge breaks G-NEST (limb 5', AMENDMENT 2(a))" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_nest/L3" --l2 "$SCRATCH/mut_nest/L2" \
    --l1 "$SCRATCH/mut_nest/L1" --log-name log.primal
expect_refusal 'G-SYS' "B4b and the comparator REFUSES on it, never degrades" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_nest/L3" --l2 "$SCRATCH/mut_nest/L2" \
    --l1 "$SCRATCH/mut_nest/L1" --log-name log.primal

# ---- B5  G-TOL: the solver dumped a different tolerance product
head1 "B5 -- G-TOL against a wrong tolerance product"
cp -a "$SCRATCH/clean" "$SCRATCH/mut_tol"
mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0239956), flat(0.3181159), diff=10000)' \
  "$SCRATCH/mut_tol/L3"
expect_refusal 'G-TOL' "B5a primalMinResTolDiff 10000 is REFUSED" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_tol/L3" --l2 "$SCRATCH/mut_tol/L2" \
    --l1 "$SCRATCH/mut_tol/L1" --log-name log.primal
expect_out 'accept floor \(PRODUCT, N-D43\) = 0\.0001' \
  "B5b the accept floor is the PRODUCT, not either factor (N-D43)" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_tol/L3" --l2 "$SCRATCH/mut_tol/L2" \
    --l1 "$SCRATCH/mut_tol/L1" --log-name log.primal

# ---- B6  G-RES / N-D44: the reader must read initRes, never finalRes
head1 "B6 -- G-RES reads initRes, NEVER finalRes (N-D44)"
# the plant in A1-A6 already fed it a SMALL initRes beside a LARGE finalRes;
# here the converse: a LARGE initRes beside a SMALL finalRes must FAIL the gate.
cp -a "$SCRATCH/clean" "$SCRATCH/mut_res"
mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0239956), flat(0.3181159), extra_initres=1.0e-03)' \
  "$SCRATCH/mut_res/L3"
expect_out 'initRes = 1\.000000e-03.*FAIL' \
  "B6a a 1e-3 initRes beside a 1e-4 finalRes FAILS the gate (it read the right one)" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_res/L3" --l2 "$SCRATCH/mut_res/L2" \
    --l1 "$SCRATCH/mut_res/L1" --log-name log.primal
expect_out 'VERDICT  CD triple +: NOT A RESULT' \
  "B6b and standing rule 5 clause 1 makes the whole triple NOT A RESULT" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_res/L3" --l2 "$SCRATCH/mut_res/L2" \
    --l1 "$SCRATCH/mut_res/L1" --log-name log.primal
expect_out 'PRECONDITION, NOT DISCRIMINATING' \
  "B6c G-RES is labelled a precondition, per AMENDMENT 1(b)" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"

# ---- B7/B8  G-COLD: the warm-start trap
head1 "B7/B8 -- G-COLD, the warm-start trap measured on this very case"
mkdir -p "$SCRATCH/cold_ok/0" "$SCRATCH/cold_ok/processor0/0"
for f in U p T nut phi; do
  printf 'placeholder initial condition\n' > "$SCRATCH/cold_ok/0/$f"
  printf 'placeholder initial condition\n' > "$SCRATCH/cold_ok/processor0/0/$f"
done
expect_rc 0 "B7a a genuinely cold case passes G-COLD" \
  "$PY" "$GRADE" cold --case "$SCRATCH/cold_ok"
cp -a "$SCRATCH/cold_ok" "$SCRATCH/cold_time"
mkdir -p "$SCRATCH/cold_time/processor0/1000"
expect_refusal 'G-COLD' "B7b a stray time directory is REFUSED" \
  "$PY" "$GRADE" cold --case "$SCRATCH/cold_time"
cp -a "$SCRATCH/cold_ok" "$SCRATCH/cold_warm"
"$PY" -c "open('$SCRATCH/cold_warm/processor0/0/U','w').write('X'*200000)"
expect_refusal 'G-COLD' "B8a an oversized 0-field (a WRITTEN SOLUTION) is REFUSED" \
  "$PY" "$GRADE" cold --case "$SCRATCH/cold_warm"
expect_out 'WRITTEN SOLUTION, not an initial condition' \
  "B8b the refusal names the pyDAFoam warm-start it is catching" \
  "$PY" "$GRADE" cold --case "$SCRATCH/cold_warm"
mkdir -p "$SCRATCH/cold_empty"
expect_refusal 'G-COLD' "B8c a case with NO 0-fields REFUSES rather than passing vacuously" \
  "$PY" "$GRADE" cold --case "$SCRATCH/cold_empty"

# =====================================================================
head1 "B9 -- THE DrivAer GATE A1 DEFECT, reproduced and caught"
# =====================================================================
# A CD history drifting steadily by 1e-4 per printed sample.  The adjacent-
# sample delta is 1.0e-04 at every step; the 10-sample PEAK-TO-PEAK excursion
# is 9.0e-04.  Against a level-to-level difference of 2.0e-04 the ten-times
# rule demands <= 2.0e-05.
#   an adjacent-sample-delta criterion would compare 1.0e-04 ... and still
#   fail here, so the fixture ALSO includes the harder case below, where the
#   adjacent delta PASSES and the excursion does not.
mkfix 'log(sys.argv[2]+"/drift.log", drift(0.0229956, 12, 1.0e-4), flat(0.3131159, 12))' "$SCRATCH"
expect_rc 1 "B9a a drifting CD history is NOT plateaued -> G-PLAT refuses it" \
  "$PY" "$GRADE" plat --log "$SCRATCH/drift.log" --func CD --diff 2.0e-4 --level L3
expect_out 'VERDICT  G-PLAT L3 CD +: NOT A RESULT' \
  "B9b and the verdict is NOT A RESULT, from the fixed vocabulary" \
  "$PY" "$GRADE" plat --log "$SCRATCH/drift.log" --func CD --diff 2.0e-4 --level L3

# The decisive form: adjacent delta 2.0e-06 (PASSES a two-sample criterion at
# 2.0e-05 by 10x), peak-to-peak over the window 1.8e-05 ... which is 90 % of
# the 2.0e-05 allowance and climbing, and over the full history the signal has
# moved 2.2e-05 -- it is DRIFTING, not plateaued.  Tighten the level-to-level
# difference to 1.0e-4 (allowance 1.0e-05) and peak-to-peak refuses while the
# adjacent delta still passes by 5x.  THAT is the 120x defect, in miniature.
mkfix 'log(sys.argv[2]+"/slowdrift.log", drift(0.0229956, 12, 2.0e-6), flat(0.3131159, 12))' "$SCRATCH"
expect_rc 1 "B9c adjacent delta 2.0e-06 PASSES a 1.0e-05 allowance; peak-to-peak 1.8e-05 does NOT" \
  "$PY" "$GRADE" plat --log "$SCRATCH/slowdrift.log" --func CD --diff 1.0e-4 --level L3
expect_out 'peak-to-peak\(last 10\) = 1\.8[0-9]*e-05' \
  "B9d the statistic actually gated is the peak-to-peak excursion" \
  "$PY" "$GRADE" plat --log "$SCRATCH/slowdrift.log" --func CD --diff 1.0e-4 --level L3
expect_out 'reported, NOT gated\] max adjacent-sample delta = 2\.0[0-9]*e-06' \
  "B9e the adjacent-sample delta is printed BESIDE it, and is not the gate" \
  "$PY" "$GRADE" plat --log "$SCRATCH/slowdrift.log" --func CD --diff 1.0e-4 --level L3
# and the control: a genuinely flat history must PASS, or B9 proves nothing.
mkfix 'log(sys.argv[2]+"/flat.log", flat(0.0229956, 12, 1e-9), flat(0.3131159, 12))' "$SCRATCH"
expect_rc 0 "B9f CONTROL: a genuinely plateaued history PASSES G-PLAT" \
  "$PY" "$GRADE" plat --log "$SCRATCH/flat.log" --func CD --diff 2.0e-4 --level L3

# ---- B10  too few samples
head1 "B10 -- fewer than 10 printed samples"
mkfix 'log(sys.argv[2]+"/short.log", flat(0.0229956, 6, 1e-9), flat(0.3131159, 6))' "$SCRATCH"
expect_rc 1 "B10a 6 samples -> NOT A RESULT for want of evidence" \
  "$PY" "$GRADE" plat --log "$SCRATCH/short.log" --func CD --diff 2.0e-4 --level L3
expect_out 'want of evidence' "B10b and it says why" \
  "$PY" "$GRADE" plat --log "$SCRATCH/short.log" --func CD --diff 2.0e-4 --level L3

# ---- B11  non-monotone triple: NOT A RESULT, and NO GCI quoted
head1 "B11 -- a non-monotone triple must not be given a GCI"
cp -a "$SCRATCH/clean" "$SCRATCH/mut_osc"
mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0228956), flat(0.3181159))' "$SCRATCH/mut_osc/L3"
OSC=( --l3 "$SCRATCH/mut_osc/L3" --l2 "$SCRATCH/mut_osc/L2" --l1 "$SCRATCH/mut_osc/L1"
      --log-name log.primal )
expect_out 'class = OSCILLATORY' "B11a the triple is classified OSCILLATORY" \
  "$PY" "$GRADE" grade "${OSC[@]}"
expect_out 'GCI: NOT QUOTED' "B11b no GCI is quoted on a non-monotone triple" \
  "$PY" "$GRADE" grade "${OSC[@]}"
expect_out 'VERDICT  CD triple +: NOT A RESULT' "B11c verdict is NOT A RESULT" \
  "$PY" "$GRADE" grade "${OSC[@]}"
expect_out 'BOTH TRIPLES AND BOTH ORDERS' \
  "B11d both triples and both orders are printed beside it (rule 5 clause 2)" \
  "$PY" "$GRADE" grade "${OSC[@]}"

# ---- B12  observed order outside the registered band
head1 "B12 -- observed order outside [1.0, 3.0]"
cp -a "$SCRATCH/clean" "$SCRATCH/mut_p"
# eps21 = 2e-4, eps32 = 2e-4*2^4 = 3.2e-3  -> p = 4, outside the band
mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0229956+2e-4+3.2e-3), flat(0.3181159))' "$SCRATCH/mut_p/L3"
PBAD=( --l3 "$SCRATCH/mut_p/L3" --l2 "$SCRATCH/mut_p/L2" --l1 "$SCRATCH/mut_p/L1"
       --log-name log.primal )
expect_out 'observed order p = 4\.0000' "B12a p = 4.0000 is recovered" \
  "$PY" "$GRADE" grade "${PBAD[@]}"
expect_out 'outside \[1\.0, 3\.0\]' "B12b the band is the registered Sec.4.3 one" \
  "$PY" "$GRADE" grade "${PBAD[@]}"
expect_out 'VERDICT  CD triple +: NOT A RESULT' "B12c and the verdict is NOT A RESULT" \
  "$PY" "$GRADE" grade "${PBAD[@]}"

# ---- B14  an ambiguous log choice is refused, never guessed
head1 "B14 -- two candidate logs must be refused, not guessed"
cp -a "$SCRATCH/clean" "$SCRATCH/mut_logs"
cp "$SCRATCH/mut_logs/L3/log.primal" "$SCRATCH/mut_logs/L3/log.other"
expect_refusal 'READ' "B14 two candidate logs and no --log-name -> REFUSE (no coin flip)" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/mut_logs/L3" --l2 "$SCRATCH/mut_logs/L2" \
    --l1 "$SCRATCH/mut_logs/L1"

# =====================================================================
head1 "B13 -- EVIDENCE PROTECTION: not one real artifact moved"
# =====================================================================
if sha256sum -c "$SHAS" >/dev/null 2>&1; then
  ok "B13 every real artifact this suite read is byte-identical afterwards"
else
  bad "B13 A REAL ARTIFACT CHANGED -- a graded run root is evidence"
  sha256sum -c "$SHAS" 2>&1 | grep -v ': OK$' | sed 's/^/        | /'
fi

# =====================================================================
head1 "C2 -- G-SYS limb 5 on the REAL family surfaces, AS AMENDMENT 2(a) LEFT IT"
# =====================================================================
# WHAT WAS HERE: C2a asserted rc=2 -- that the REGISTERED Sec.3.1 limb 5 (a 1 %
# cross-level TE-thickness agreement, registered with NO measurement recipe)
# REFUSES the real c2/c1/c0 family.  It did, and AMENDMENT 2(a) is the record of
# what the supervisor did about it: the limb was STRUCK AS A GATE because it is
# UNMEASURABLE AS WRITTEN -- every window-based TE statistic is point-density
# dependent and these levels differ 4x in point count by construction -- and NOT
# because it failed.  It was replaced by the STRICTLY STRONGER G-NEST (limb 5'),
# which C1h and B4a above drive.
#
# So the unit is inverted, not deleted, and it is now the CONTROL ON THE
# AMENDMENT ITSELF: the registered family must NOT be refused by G-SYS, while
# the struck limb's own numbers are still printed in full.
expect_no_out 'REFUSE \[G-SYS\]' \
  "C2a G-SYS does NOT refuse the registered family (limb 5 struck, AMENDMENT 2(a))" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/clean/L3" --l2 "$SCRATCH/clean/L2" \
    --l1 "$SCRATCH/clean/L1" --log-name log.primal
expect_out 'G-SYS: all five limbs green' \
  "C2b and it says so: all five limbs green on the real surfaces" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/clean/L3" --l2 "$SCRATCH/clean/L2" \
    --l1 "$SCRATCH/clean/L1" --log-name log.primal
expect_out 'UNMEASURABLE AS WRITTEN' \
  "C2c the record says WHY the limb was struck, in the comparator's own output" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/clean/L3" --l2 "$SCRATCH/clean/L2" \
    --l1 "$SCRATCH/clean/L1" --log-name log.primal
printf '\n  --- measured TE thickness, real surfaces, comparator definition ---\n'
"$PY" "$GRADE" grade --l3 "$SCRATCH/clean/L3" --l2 "$SCRATCH/clean/L2" \
  --l1 "$SCRATCH/clean/L1" --log-name log.primal 2>&1 | grep -E 'limb5' | sed 's/^/  /'

# =====================================================================
head1 "C3 -- DEFECT A: a REGISTERED STAGE THAT DID NOT RUN MAY NOT LEAVE THE ITEM AT PASS"
# =====================================================================
# Found by the dafoam-supervisor 2026-09-11 and observed directly: the clean
# triple printed `VERDICT  P1-P4 shock : PENDING` and then
# `VERDICT  A3GC OVERALL : PASS`.  NEITHER shock branch wrote into the
# composition dict and the overall was taken over CD and CL only.
# PREREG Sec.6 stage 5 registers the grading path as "Roache order applied
# (Sec.4.2); GCI at Fs=1.25; SHOCK PREDICTIONS P1-P4 EVALUATED", and AMENDMENT 2
# preserves Sec.4.5 verbatim, so P1-P4 evaluation is a REGISTERED STAGE.
# CLAUDE.md rule 1 fixes PENDING as "not yet run" and forbids it softening
# anything.  An item cannot stand at PASS on a stage that produced no evidence.
expect_out 'VERDICT  P1-P4 shock +: PENDING' \
  "C3a the ungraded shock stage carries PENDING, from the fixed vocabulary" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'VERDICT  A3GC OVERALL +: PENDING' \
  "C3b DEFECT A: the item is PENDING, NOT PASS, while a registered stage is ungraded" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_no_out 'VERDICT  A3GC OVERALL +: PASS' \
  "C3c and it is NEVER PASS on this input -- the exact line that was observed" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'composed worst-first over .*P1-P4 shock = PENDING' \
  "C3d the shock gate is NAMED in the composition roster, not silently dropped" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
# ...and PENDING must not soften a worse token: the OSCILLATORY triple still wins.
expect_out 'VERDICT  A3GC OVERALL +: NOT A RESULT' \
  "C3e a NOT A RESULT triple still dominates the PENDING shock (rule 1: PENDING never softens)" \
  "$PY" "$GRADE" grade "${OSC[@]}"

# =====================================================================
head1 "C4 -- DEFECT B: the composition ordering must be TOTAL over all six tokens"
# =====================================================================
# The old ordering listed three of the six: ["NOT A RESULT","GATE FAIL","PASS"].
# `order.index(v)` raises ValueError on PENDING, GATE REACHED or BLOCKED -- a
# traceback, not a refusal.  A comparator refuses cleanly or it is not one.
expect_rc 0 "C4a every token in the fixed vocabulary drives the ordering" \
  "$PY" "$GRADE" compose --census
expect_out 'every one of the 6 tokens composed without raising' \
  "C4b and the census says so, over all six" \
  "$PY" "$GRADE" compose --census
expect_no_out 'Traceback' \
  "C4c NO TRACEBACK on any token -- this is the defect, stated directly" \
  "$PY" "$GRADE" compose --census
expect_out 'VERDICT  COMPOSED +: GATE FAIL' \
  "C4d a GATE FAIL beside a PENDING composes to GATE FAIL (rule 1: PENDING never softens)" \
  "$PY" "$GRADE" compose --gate 'CD=PASS' --gate 'shock=PENDING' --gate 'CL=GATE FAIL'
expect_out 'VERDICT  COMPOSED +: NOT A RESULT' \
  "C4e NOT A RESULT outranks everything (standing rule 5: never the reverse)" \
  "$PY" "$GRADE" compose --gate 'CD=NOT A RESULT' --gate 'shock=PENDING' --gate 'CL=PASS'
expect_out 'VERDICT  COMPOSED +: BLOCKED' \
  "C4f BLOCKED and GATE REACHED are ranked too, not merely accepted" \
  "$PY" "$GRADE" compose --gate 'a=GATE REACHED' --gate 'b=BLOCKED' --gate 'c=PASS'
expect_refusal 'COMPOSE' "C4g a token outside the vocabulary REFUSES, never sorts" \
  "$PY" "$GRADE" compose --gate 'CD=ROUGHLY CONVERGED'
expect_refusal 'COMPOSE' "C4h an EMPTY composition REFUSES, never returns a vacuous PASS" \
  "$PY" "$GRADE" compose

# =====================================================================
head1 "C5 -- L-332: this comparator carries ZERO asserts, and counts its own"
# =====================================================================
# Found by this lane while repairing A and B: the N-D44 structural guard on
# _INITRES_RE WAS an `assert`.  `python3 -O` strips it, so under -O the one
# guard standing between the reader and finalRes-blindness was not there.
expect_rc 0 "C5a ast.Assert census == 0, read off the file on disk" \
  "$PY" -c "import ast,sys;n=sum(1 for x in ast.walk(ast.parse(open(sys.argv[1],encoding='utf-8').read())) if isinstance(x,ast.Assert));print(n);sys.exit(0 if n==0 else 1)" "$GRADE"
expect_out 'VERDICT  CD triple +: PASS' \
  "C5b the clean triple grades identically under python3 -O (no gate vanishes)" \
  "$PY" -O "$GRADE" grade "${CLEAN[@]}"
expect_out 'VERDICT  A3GC OVERALL +: PENDING' \
  "C5c and the DEFECT A repair survives -O too" \
  "$PY" -O "$GRADE" grade "${CLEAN[@]}"

# =====================================================================
head1 "E -- AMENDMENT 3: the shock prediction tokens, P4's strong form, the stage"
# =====================================================================
# *** EVERY JSON BELOW IS A SYNTHETIC TEST FIXTURE.  NOT A MEASUREMENT.  Not
# evidence.  evaluate_shock HAS NEVER RUN AGAINST REAL VTK -- none exists for
# any A3GC level -- so these fixtures are the ONLY way AMENDMENT 3(a)-(d) can be
# driven at all, and NOTHING they print is a lab result. ***
SH="$SCRATCH/shock"; mkdir -p "$SH"
mkshock() { "$PY" - "$@" <<'SHPY'
import json, os, sys
# Sec.4.5's seven stations.  Baselines are the L3 side; the L1 side is built to
# land the run in the band the caller names.  SYNTHETIC.  NOT A MEASUREMENT.
ETAS = ["0.2", "0.44", "0.65", "0.8", "0.9", "0.96", "0.99"]
def write(d, p1, p2, p3):
    # p1: slope multiplier on L1 vs L3 at eta 0.8/0.9
    # p2: (mean-shift multiplier, eta-0.20 shift on L1)
    # p3: pooled upper-surface RMS on L1
    l3 = {e: {"cfd_slope": 5.0, "shift_xoc": 0.10} for e in ETAS}
    l1 = {e: {"cfd_slope": 5.0 * (p1 if e in ("0.8", "0.9") else 1.0),
              "shift_xoc": 0.10 * p2[0]} for e in ETAS}
    l1["0.2"]["shift_xoc"] = p2[1]
    cmp1 = {e: {"upper": {"rms_dev": p3, "n_common": 40}} for e in ETAS}
    for nm, obj in (("shock_L3.json", l3), ("shock_L1.json", l1),
                    ("cmp_L1.json", cmp1)):
        json.dump(obj, open(os.path.join(d, nm), "w"), indent=1)
if __name__ == "__main__":
    exec(sys.argv[2])
SHPY
}
# runs the shock logic on one fixture dir
shockrun() { local d="$1" conv="$2"; shift 2
  "$PY" "$GRADE" shock --shock-l3 "$d/shock_L3.json" --shock-l1 "$d/shock_L1.json" \
    --cmp-l1 "$d/cmp_L1.json" "$conv"; }

# ---- E1  ALL THREE PASS, triple CONVERGING.  The control: if this does not
#          grade PASS, nothing else in section E means anything.
mkdir -p "$SH/allpass"; mkshock "$SH/allpass" 'write(sys.argv[1], 1.60, (0.50, 0.040), 0.050)'
expect_out 'VERDICT  P1 sharpening +: PASS' "E1a P1 PASS at a +60 % slope increase" \
  shockrun "$SH/allpass" --triple-converging
expect_out 'VERDICT  P1-P4 shock stage +: PASS' "E1b the stage is PASS when all three pass" \
  shockrun "$SH/allpass" --triple-converging
expect_no_out 'P4  ALL THREE FALSIFIED' "E1c P4 does NOT fire on three passes" \
  shockrun "$SH/allpass" --triple-converging

# ---- E2  ALL THREE FALSIFIED + CONVERGING triple -> AMENDMENT 3(d) GATE REACHED.
mkdir -p "$SH/allfals"; mkshock "$SH/allfals" 'write(sys.argv[1], 1.05, (1.00, 0.120), 0.090)'
expect_out 'VERDICT  P1 sharpening +: GATE FAIL' "E2a a falsified P1 is GATE FAIL" \
  shockrun "$SH/allfals" --triple-converging
expect_out 'P4  ALL THREE FALSIFIED and the CD/CL triple is CONVERGING' \
  "E2b P4 fires on the STRONG form with a CONVERGING triple" \
  shockrun "$SH/allfals" --triple-converging
expect_out 'turbulence-model limitation, not a grid limitation' \
  "E2c and Sec.4.5 P4's registered reading is printed VERBATIM" \
  shockrun "$SH/allfals" --triple-converging
expect_out 'VERDICT  P1-P4 shock stage +: GATE REACHED' \
  "E2d the stage is GATE REACHED (AMENDMENT 3(d), an INTERPRETIVE CHOICE)" \
  shockrun "$SH/allfals" --triple-converging
expect_out 'INTERPRETIVE CHOICE' \
  "E2e and the output SAYS it is interpretive, so no reader thinks the document said it" \
  shockrun "$SH/allfals" --triple-converging
expect_no_out 'VERDICT  P1-P4 shock stage +: PASS' \
  "E2f it is NEVER PASS -- no shock band was met" \
  shockrun "$SH/allfals" --triple-converging

# ---- E3  ALL THREE FALSIFIED but the triple is NOT CONVERGING -> P4 SHUT.
expect_no_out 'turbulence-model limitation, not a grid limitation' \
  "E3a P4's reading is NOT PRINTED when the triple is not CONVERGING (Sec.4.5 precondition)" \
  shockrun "$SH/allfals" --triple-not-converging
expect_out 'VERDICT  P1-P4 shock stage +: GATE FAIL' \
  "E3b and the stage carries the worst of the three instead" \
  shockrun "$SH/allfals" --triple-not-converging

# ---- E4  THE MIDDLE BAND.  A value between the two registered thresholds is
#          NOT A RESULT and MUST NEVER READ AS PASS.
mkdir -p "$SH/middle"; mkshock "$SH/middle" 'write(sys.argv[1], 1.60, (0.50, 0.040), 0.060)'
expect_out 'VERDICT  P3 pooled Cp +: NOT A RESULT' \
  "E4a P3 at RMS 0.060 -- above the 0.055 PASS, below the 0.070 falsifier -- is NOT A RESULT" \
  shockrun "$SH/middle" --triple-converging
expect_no_out 'VERDICT  P3 pooled Cp +: PASS' \
  "E4b A MIDDLE-BAND VALUE DOES NOT SILENTLY READ AS PASS" \
  shockrun "$SH/middle" --triple-converging
expect_out 'MIDDLE BAND \(AMENDMENT 3\(a\)\)' \
  "E4c and the output names the band and the amendment that registered it" \
  shockrun "$SH/middle" --triple-converging
expect_out 'VERDICT  P1-P4 shock stage +: NOT A RESULT' \
  "E4d the stage takes the worst of the three (AMENDMENT 3(c))" \
  shockrun "$SH/middle" --triple-converging

# ---- E5  THE WEAK READING OF "ALL FAIL".  All three NON-PASS, none FALSIFIED.
#          P4 must stay SHUT -- this is AMENDMENT 3(b)'s whole content.
mkdir -p "$SH/weak"; mkshock "$SH/weak" 'write(sys.argv[1], 1.25, (0.90, 0.070), 0.060)'
expect_out 'VERDICT  P1 sharpening +: NOT A RESULT' \
  "E5a a 25 % slope increase is neither PASS (>=40 %) nor falsified (<15 %)" \
  shockrun "$SH/weak" --triple-converging
expect_no_out 'turbulence-model limitation, not a grid limitation' \
  "E5b P4 DOES NOT FIRE on the WEAK reading -- three middling results are not a counter-hypothesis" \
  shockrun "$SH/weak" --triple-converging
expect_out 'THAT READING IS NOT REGISTERED and P4 stays shut' \
  "E5c and the output says so in as many words" \
  shockrun "$SH/weak" --triple-converging

# ---- E6  PARTIAL FAILURE (AMENDMENT 3(c)): one falsified, two passing.
mkdir -p "$SH/partial"; mkshock "$SH/partial" 'write(sys.argv[1], 1.60, (0.50, 0.040), 0.090)'
expect_no_out 'P4  ALL THREE FALSIFIED' \
  "E6a P4 does not fire on a partial result" shockrun "$SH/partial" --triple-converging
expect_out 'VERDICT  P1-P4 shock stage +: GATE FAIL' \
  "E6b the stage takes the WORST of the three (AMENDMENT 3(c))" \
  shockrun "$SH/partial" --triple-converging

# ---- E7  the P4 precondition may not be assumed either way.
expect_refusal 'ARGS' "E7 neither --triple-converging nor --triple-not-converging -> REFUSE" \
  "$PY" "$GRADE" shock --shock-l3 "$SH/allfals/shock_L3.json" \
    --shock-l1 "$SH/allfals/shock_L1.json" --cmp-l1 "$SH/allfals/cmp_L1.json"

# =====================================================================
head1 "F -- G-COMPLETE: PREREG Sec.3.7 / CLAUDE.md rule 4, clause by clause"
# =====================================================================
# THE FAILURE THIS GATE EXISTS TO PREVENT, and F1 demonstrates it rather than
# asserting it: a level that DIES mid-run leaves a TRUNCATED log whose tail is
# PERFECTLY PLATEAUED -- a dead solve plateaus better than a live one -- so
# G-PLAT passes it and the triple would grade CONVERGING ON A CORPSE.
# A3GC is registered at 1,525 core-min; spending that to grade a dead solve as
# converged is the outcome this repair buys out.
mkcase() { local d="$1"; shift; mkdir -p "$d"
  mkfix "owner(sys.argv[2], 99840); boundary(sys.argv[2], 6240)" "$d"
  cp "$S_C2" "$d/surfaceMesh.cgns"; }

# ---- F1  THE TRUNCATED LOG WITH A PERFECTLY PLATEAUED TAIL.
#      endTime 1100, but the solver died after Time = 700: 8 samples, flat to
#      1e-9, no `End` line.  Every value G-PLAT looks at says "plateaued".
head1 "F1 -- a DEAD solve whose tail is perfectly flat"
# *** THE FIXTURE MUST GIVE G-PLAT NOTHING TO COMPLAIN ABOUT, OR IT PROVES
# NOTHING.  First cut used 8 samples; G-PLAT refused it for want of evidence
# (<10) and the D9 mutation control caught that G-COMPLETE was never the thing
# under test.  So: TWELVE samples, flat to 1e-9 -- G-PLAT passes it happily --
# ending at Time = 1100 against a registered endTime of 6000.  The solver died
# at 1,100 of 6,000 iterations and its tail is immaculate. ***
D="$SCRATCH/dead"; cp -a "$SCRATCH/clean" "$D"
mkfix 'log(sys.argv[2]+"/log.primal", flat(0.0239956, 12, 1e-9), flat(0.3181159, 12, 1e-9), end=False)' "$D/L3"
mkfix 'complete(sys.argv[2], 6000, write_end=False)' "$D/L3"
DEAD=( --l3 "$D/L3" --l2 "$D/L2" --l1 "$D/L1" --log-name log.primal )
expect_out '2 `End` line present +FAIL' \
  "F1a the missing End line is caught (rule 4 clause 2)" "$PY" "$GRADE" grade "${DEAD[@]}"
expect_out '3 last time == endTime +FAIL +last printed Time = 1100, controlDict endTime = 6000' \
  "F1b the truncation is caught: died at 1,100 of 6,000 iterations (clause 3)" \
  "$PY" "$GRADE" grade "${DEAD[@]}"
expect_out '4 fields at endTime +FAIL' \
  "F1c and endTime was never written (clause 4)" "$PY" "$GRADE" grade "${DEAD[@]}"
expect_out 'VERDICT  CD triple +: NOT A RESULT' \
  "F1d THE DEAD SOLVE IS NOT A RESULT" "$PY" "$GRADE" grade "${DEAD[@]}"
expect_out 'clause 1: a level failed G-COMPLETE' \
  "F1e and standing rule 5 clause 1 names G-COMPLETE as the reason" \
  "$PY" "$GRADE" grade "${DEAD[@]}"
expect_no_out 'VERDICT  A3GC OVERALL +: PASS' \
  "F1f the item is NEVER PASS on a corpse" "$PY" "$GRADE" grade "${DEAD[@]}"
expect_no_out 'L3 CD: only [0-9]+ printed samples' \
  "F1g *** AND G-PLAT HAS NO COMPLAINT: the dead tail is not short, it is FLAT. G-COMPLETE is the only thing catching this. ***" \
  "$PY" "$GRADE" grade "${DEAD[@]}"

# ---- F2  rc != 0  (clause 1)
head1 "F2 -- a non-zero solver exit code"
cp -a "$SCRATCH/clean" "$SCRATCH/rcbad"
mkfix 'complete(sys.argv[2], 1100, rc=137)' "$SCRATCH/rcbad/L2"
RCBAD=( --l3 "$SCRATCH/rcbad/L3" --l2 "$SCRATCH/rcbad/L2" --l1 "$SCRATCH/rcbad/L1" --log-name log.primal )
expect_out '1 rc == 0 +FAIL +rc = 137' "F2a rc=137 (an OOM kill) is caught" \
  "$PY" "$GRADE" grade "${RCBAD[@]}"
expect_out 'VERDICT  CD triple +: NOT A RESULT' "F2b and the triple is NOT A RESULT" \
  "$PY" "$GRADE" grade "${RCBAD[@]}"

# ---- F3  NO rc artifact at all.  A MISSING EXIT CODE IS NOT A ZERO EXIT CODE.
head1 "F3 -- no exit code on disk must REFUSE, never pass"
cp -a "$SCRATCH/clean" "$SCRATCH/rcnone"; rm -f "$SCRATCH/rcnone/L3/log.primal.rc"
expect_refusal 'G-COMPLETE' "F3a an absent exit code REFUSES (it is not a zero)" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/rcnone/L3" --l2 "$SCRATCH/rcnone/L2" \
    --l1 "$SCRATCH/rcnone/L1" --log-name log.primal
expect_out 'A MISSING EXIT CODE IS NOT A ZERO EXIT CODE' \
  "F3b and the refusal says so, and names where the runner must write it" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/rcnone/L3" --l2 "$SCRATCH/rcnone/L2" \
    --l1 "$SCRATCH/rcnone/L1" --log-name log.primal

# ---- F4  A MISSING FIELD at endTime (clause 4)
head1 "F4 -- a field missing from the endTime directory"
cp -a "$SCRATCH/clean" "$SCRATCH/nofield"
mkfix 'complete(sys.argv[2], 1100, end_fields=("T","U","p","alphat","nut"))' "$SCRATCH/nofield/L1"
expect_out '4 fields at endTime +FAIL +MISSING at endTime: nuTilda' \
  "F4 a field present in 0 but absent at endTime is named" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/nofield/L3" --l2 "$SCRATCH/nofield/L2" \
    --l1 "$SCRATCH/nofield/L1" --log-name log.primal

# ---- F5  THE AGE GUARD (clause 6): endTime fields OLDER than the case's own 0/T.
#      This is the stale-answer trap -- fields left by an EARLIER run, with a
#      fresh `0` written over them at this launch.
head1 "F5 -- endTime fields older than 0/T: an answer from a PREVIOUS run"
cp -a "$SCRATCH/clean" "$SCRATCH/stale"
mkfix 'complete(sys.argv[2], 1100, end_newer=False)' "$SCRATCH/stale/L2"
expect_out '6 AGE GUARD +FAIL +6 endTime field\(s\) NOT newer than' \
  "F5a fields older than 0/T are caught -- 0/T dates the run allowed to answer" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/stale/L3" --l2 "$SCRATCH/stale/L2" \
    --l1 "$SCRATCH/stale/L1" --log-name log.primal
expect_out 'VERDICT  CD triple +: NOT A RESULT' "F5b and the triple is NOT A RESULT" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/stale/L3" --l2 "$SCRATCH/stale/L2" \
    --l1 "$SCRATCH/stale/L1" --log-name log.primal

# ---- F6  no system/controlDict -> REFUSE (endTime is not in the log)
head1 "F6 -- no controlDict: endTime is unknowable, so REFUSE"
cp -a "$SCRATCH/clean" "$SCRATCH/nocd"; rm -rf "$SCRATCH/nocd/L3/system"
expect_refusal 'G-COMPLETE' "F6 absent controlDict REFUSES rather than assuming an endTime" \
  "$PY" "$GRADE" grade --l3 "$SCRATCH/nocd/L3" --l2 "$SCRATCH/nocd/L2" \
    --l1 "$SCRATCH/nocd/L1" --log-name log.primal

# ---- F7  THE CONTROL: the clean triple is COMPLETE and every clause says so.
head1 "F7 -- CONTROL: all six clauses green on the clean triple"
expect_out 'G-COMPLETE: all six clauses hold for L3' "F7a L3 is complete" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out '6 AGE GUARD +OK +all 6 endTime field\(s\) NEWER than' \
  "F7b the age guard PASSES on a genuinely fresh run (it is not always-fail)" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"
expect_out 'cadence cross-check +predicted 1 \+ floor\(endTime/printInterval\) = 1 \+ floor\(1100/100\) = 12, measured 12' \
  "F7c the cadence arithmetic is printed beside clause 5, REPORTED not gated" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"

# =====================================================================
head1 "D -- MUTATION CONTROLS on the DEFECT A and DEFECT B repairs"
# =====================================================================
# A FIX WITH NO CONTROL PROVING IT IS LIVE IS NOT A FIX.  Each mutation below
# removes exactly one repair's teeth from a COPY of the comparator and asserts a
# NAMED unit above goes BAD.  If a mutation is applied and the named unit still
# passes, that unit is ceremony.
#
# THE MUTATOR IS ITSELF A PLANTED-ZERO RISK AND IS GUARDED (D8G's rule): a
# replacement that matches nothing yields an UNMUTATED copy, the unit then
# passes, and the control reports "failed to fail" when nothing was mutated.
# Every mutation asserts REPLACEMENT COUNT == 1 and asserts the copy DIFFERS
# from the original BEFORE it is run.
MUTDIR="$SCRATCH/mutants"; mkdir -p "$MUTDIR"

mutate() {  # $1 = tag  $2 = old text  $3 = new text
  "$PY" - "$GRADE" "$MUTDIR/$1.py" "$2" "$3" <<'MUTPY'
import sys
src, dst, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src, encoding="utf-8").read()
n = s.count(old)
if n != 1:
    sys.stderr.write("MUTATOR REFUSE: pattern occurs %d times, not once\n" % n)
    sys.exit(3)
open(dst, "w", encoding="utf-8").write(s.replace(old, new))
MUTPY
}

# mut_must_fail <tag> <named-catcher> <regex the UNMUTATED grader satisfies> <cmd...>
#   asserts the mutant was really built, then asserts the catcher's own regex
#   NO LONGER matches against the mutant.
mut_must_fail() {
  local tag="$1" catcher="$2" rx="$3"; shift 3
  if [ ! -s "$MUTDIR/$tag.py" ]; then
    bad "D-$tag MUTATOR did not build a mutant (planted-zero guard)"; return
  fi
  if cmp -s "$GRADE" "$MUTDIR/$tag.py"; then
    bad "D-$tag mutant is IDENTICAL to the original (planted-zero guard)"; return
  fi
  local out; out="$("$@" 2>&1)"
  if printf '%s' "$out" | grep -qE "$rx"; then
    bad "D-$tag THE SUITE FAILED TO FAIL: [$catcher] still matches /$rx/ under the mutation"
    printf '%s\n' "$out" | tail -8 | sed 's/^/        | /'
  else
    ok "D-$tag mutation caught; the catcher is [$catcher]"
  fi
}

# ---- D1  DEFECT A reinstated: the shock verdict stops entering the composition.
#      The overall then reverts to being taken over CD and CL only -- which is
#      exactly the line the supervisor observed: OVERALL PASS beside a PENDING
#      registered stage.
mutate DEFECT-A-SHOCK-NOT-COMPOSED \
  '        verdicts["P1-P4 shock"] = emit_verdict(' \
  '        emit_verdict(' \
  && mut_must_fail DEFECT-A-SHOCK-NOT-COMPOSED 'C3b/C3c/C3d' 'VERDICT  A3GC OVERALL +: PENDING' \
       "$PY" "$MUTDIR/DEFECT-A-SHOCK-NOT-COMPOSED.py" grade "${CLEAN[@]}"
# and the mutant must be seen to produce the ORIGINAL WRONG ANSWER, not merely a
# different one -- otherwise the control does not prove which defect it reinstated.
expect_out 'VERDICT  A3GC OVERALL +: PASS' \
  "D1b the mutant reproduces the OBSERVED defect exactly: OVERALL PASS beside a PENDING stage" \
  "$PY" "$MUTDIR/DEFECT-A-SHOCK-NOT-COMPOSED.py" grade "${CLEAN[@]}"

# ---- D2  DEFECT B reinstated in its own shape: the ordering loses three tokens.
#      compose_verdicts' permutation guard must catch it and REFUSE.
mutate DEFECT-B-PARTIAL-ORDER \
  'VERDICT_SEVERITY = ("NOT A RESULT", "GATE FAIL", "BLOCKED", "PENDING",
                    "GATE REACHED", "PASS")' \
  'VERDICT_SEVERITY = ("NOT A RESULT", "GATE FAIL", "PASS")' \
  && mut_must_fail DEFECT-B-PARTIAL-ORDER 'C4a/C4b' 'every one of the 6 tokens composed without raising' \
       "$PY" "$MUTDIR/DEFECT-B-PARTIAL-ORDER.py" compose --census
expect_refusal 'COMPOSE' \
  "D2b the partial ordering REFUSES (not a permutation of the vocabulary), never raises" \
  "$PY" "$MUTDIR/DEFECT-B-PARTIAL-ORDER.py" compose --census

# ---- D2c  DEFECT B in its ORIGINAL form: the literal `order.index(v)` line the
#      supervisor found, put back.  It must TRACEBACK on PENDING -- which is the
#      behaviour C4c forbids, and the proof C4c is not ceremony.
mutate DEFECT-B-ORDER-INDEX \
  '    return min(items.values(), key=VERDICT_SEVERITY.index)' \
  '    order = ["NOT A RESULT", "GATE FAIL", "PASS"]
    return sorted(items.values(), key=lambda v: order.index(v))[0]' \
  && mut_must_fail DEFECT-B-ORDER-INDEX 'C4c' 'every one of the 6 tokens composed without raising' \
       "$PY" "$MUTDIR/DEFECT-B-ORDER-INDEX.py" compose --census
expect_out 'Traceback|ValueError' \
  "D2d the original expression is SEEN to raise ValueError on a token it does not list" \
  "$PY" "$MUTDIR/DEFECT-B-ORDER-INDEX.py" compose --gate 'shock=PENDING' --gate 'CD=PASS'

# ---- D3  L-332: plant an `assert` and the module's own census must refuse.
mutate L332-ASSERT-PLANTED \
  'def read_log(path):' \
  'def read_log(path):
    assert path, "PLANTED ASSERT -- L-332 control, must be refused"' \
  && mut_must_fail L332-ASSERT-PLANTED 'C5a/guard_no_asserts' 'VERDICT  CD triple +: PASS' \
       "$PY" "$MUTDIR/L332-ASSERT-PLANTED.py" grade "${CLEAN[@]}"
expect_refusal 'L-332' \
  "D3b the module counts its OWN asserts and refuses to run on one" \
  "$PY" "$MUTDIR/L332-ASSERT-PLANTED.py" grade "${CLEAN[@]}"

# ---- D9  *** THE CONTROL THE SUPERVISOR ASKED FOR BY NAME. ***
#      G-COMPLETE removed from the grading path entirely.  The DEAD SOLVE of
#      F1 -- truncated at Time = 700 against endTime 1100, no `End` line,
#      endTime never written -- must then be SEEN TO GRADE, because its tail is
#      perfectly flat and G-PLAT has no complaint about a corpse.
mutate NO-COMPLETION-GATE \
  '        complete_ok[lv] = gate_g_complete(root, logs[lv], lv, report)' \
  '        complete_ok[lv] = True   # MUTATION: the completion gate removed' \
  && mut_must_fail NO-COMPLETION-GATE 'F1d/F1e' 'VERDICT  CD triple +: NOT A RESULT' \
       "$PY" "$MUTDIR/NO-COMPLETION-GATE.py" grade "${DEAD[@]}"
expect_out 'VERDICT  CD triple +: PASS' \
  "D9b THE DEAD SOLVE IS SEEN TO GRADE **PASS** WITHOUT THE GATE -- 1,525 core-min to certify a corpse" \
  "$PY" "$MUTDIR/NO-COMPLETION-GATE.py" grade "${DEAD[@]}"
expect_out 'peak-to-peak\(last 10\)' \
  "D9c and G-PLAT is SEEN to have no complaint about it: the tail plateaus perfectly" \
  "$PY" "$MUTDIR/NO-COMPLETION-GATE.py" grade "${DEAD[@]}"

# ---- D10  the completion result stops reaching standing rule 5 clause 1.
mutate COMPLETION-NOT-IN-CLAUSE1 \
  '    if not complete_ok or not plat_ok or not res_ok:' \
  '    if not plat_ok or not res_ok:' \
  && mut_must_fail COMPLETION-NOT-IN-CLAUSE1 'F2b' 'VERDICT  CD triple +: NOT A RESULT' \
       "$PY" "$MUTDIR/COMPLETION-NOT-IN-CLAUSE1.py" grade "${RCBAD[@]}"

# ---- D11  a MISSING exit code silently reads as zero.
mutate MISSING-RC-IS-ZERO \
  '    refuse("G-COMPLETE", "%s: no solver exit code on disk.  CLAUDE.md rule 4 "' \
  '    return 0, "MUTATION: assumed zero"
    refuse("G-COMPLETE", "%s: no solver exit code on disk.  CLAUDE.md rule 4 "' \
  && mut_must_fail MISSING-RC-IS-ZERO 'F3a/F3b' 'A MISSING EXIT CODE IS NOT A ZERO EXIT CODE' \
       "$PY" "$MUTDIR/MISSING-RC-IS-ZERO.py" grade --l3 "$SCRATCH/rcnone/L3" \
         --l2 "$SCRATCH/rcnone/L2" --l1 "$SCRATCH/rcnone/L1" --log-name log.primal

# ---- D12  the AGE GUARD compares the wrong way round, so stale fields pass.
mutate AGE-GUARD-INVERTED \
  '                    if os.stat(fp).st_mtime <= ref:' \
  '                    if False:' \
  && mut_must_fail AGE-GUARD-INVERTED 'F5a/F5b' '6 AGE GUARD +FAIL' \
       "$PY" "$MUTDIR/AGE-GUARD-INVERTED.py" grade --l3 "$SCRATCH/stale/L3" \
         --l2 "$SCRATCH/stale/L2" --l1 "$SCRATCH/stale/L1" --log-name log.primal

# ---- D5  AMENDMENT 3(b) REVERSED: P4 fires on the WEAK reading of "all fail".
#      Three middling results would then be adopted as the counter-hypothesis.
mutate P4-WEAK-READING \
  'REG_P4_REQUIRES_ALL_FALSIFIED = True' \
  'REG_P4_REQUIRES_ALL_FALSIFIED = False' \
  && mut_must_fail P4-WEAK-READING 'E5b/E5c' 'THAT READING IS NOT REGISTERED and P4 stays shut' \
       "$PY" "$MUTDIR/P4-WEAK-READING.py" shock --shock-l3 "$SH/weak/shock_L3.json" \
         --shock-l1 "$SH/weak/shock_L1.json" --cmp-l1 "$SH/weak/cmp_L1.json" --triple-converging
expect_out 'turbulence-model limitation, not a grid limitation' \
  "D5b the WEAK reading is SEEN to adopt P4 on three middling results -- which is why it is not registered" \
  "$PY" "$MUTDIR/P4-WEAK-READING.py" shock --shock-l3 "$SH/weak/shock_L3.json" \
    --shock-l1 "$SH/weak/shock_L1.json" --cmp-l1 "$SH/weak/cmp_L1.json" --triple-converging

# ---- D6  AMENDMENT 3(a) REVERSED: the MIDDLE BAND collapses into PASS.
mutate MIDDLE-BAND-IS-PASS \
  '    if falsified:
        return "GATE FAIL"
    return "NOT A RESULT"' \
  '    if falsified:
        return "GATE FAIL"
    return "PASS"' \
  && mut_must_fail MIDDLE-BAND-IS-PASS 'E4a/E4b' 'VERDICT  P3 pooled Cp +: NOT A RESULT' \
       "$PY" "$MUTDIR/MIDDLE-BAND-IS-PASS.py" shock --shock-l3 "$SH/middle/shock_L3.json" \
         --shock-l1 "$SH/middle/shock_L1.json" --cmp-l1 "$SH/middle/cmp_L1.json" --triple-converging
expect_out 'VERDICT  P3 pooled Cp +: PASS' \
  "D6b a middle-band RMS of 0.060 is SEEN to read as PASS under the mutation -- the exact silent-pass E4b forbids" \
  "$PY" "$MUTDIR/MIDDLE-BAND-IS-PASS.py" shock --shock-l3 "$SH/middle/shock_L3.json" \
    --shock-l1 "$SH/middle/shock_L1.json" --cmp-l1 "$SH/middle/cmp_L1.json" --triple-converging

# ---- D7  Sec.4.5's P4 PRECONDITION dropped: P4 would fire on a non-CONVERGING triple.
mutate P4-IGNORES-TRIPLE \
  '    if p4 and triple_converging:
        stage = emit_verdict("P1-P4 shock stage", "GATE REACHED",' \
  '    if p4:
        stage = emit_verdict("P1-P4 shock stage", "GATE REACHED",' \
  && mut_must_fail P4-IGNORES-TRIPLE 'E3b' 'VERDICT  P1-P4 shock stage +: GATE FAIL' \
       "$PY" "$MUTDIR/P4-IGNORES-TRIPLE.py" shock --shock-l3 "$SH/allfals/shock_L3.json" \
         --shock-l1 "$SH/allfals/shock_L1.json" --cmp-l1 "$SH/allfals/cmp_L1.json" \
         --triple-not-converging

# ---- D8  AMENDMENT 3(c) REVERSED: the stage stops taking the WORST of the three.
mutate STAGE-NOT-WORST \
  '        stage = emit_verdict("P1-P4 shock stage", compose_verdicts(toks),' \
  '        stage = emit_verdict("P1-P4 shock stage", toks["P1 sharpening"],' \
  && mut_must_fail STAGE-NOT-WORST 'E6b' 'VERDICT  P1-P4 shock stage +: GATE FAIL' \
       "$PY" "$MUTDIR/STAGE-NOT-WORST.py" shock --shock-l3 "$SH/partial/shock_L3.json" \
         --shock-l1 "$SH/partial/shock_L1.json" --cmp-l1 "$SH/partial/cmp_L1.json" --triple-converging

# ---- D4  BRANCH PROBE, not a defect control, and labelled as one.
#      WHAT WAS HERE: D4 asserted REFUSE [COMPOSE-UNREGISTERED] -- the comparator
#      declining to compose an evaluated shock stage because the document
#      registered no composition.  AMENDMENT 3(e) REGISTERS ONE, so that refusal
#      is RESOLVED, not removed: the rule it was waiting for now exists, and
#      section E drives the composition it waited for.  The unit that remains is
#      the one AMENDMENT 3(e) makes load-bearing -- that an UN-EVALUATED stage
#      still cannot leave the item at PASS -- which C3b/C3c already assert on the
#      real grading path and D-DEFECT-A-SHOCK-NOT-COMPOSED already controls.
expect_no_out 'COMPOSE-UNREGISTERED' \
  "D4 the COMPOSE-UNREGISTERED refusal is RESOLVED by AMENDMENT 3(e), not merely deleted" \
  "$PY" "$GRADE" grade "${CLEAN[@]}"

# =====================================================================
printf '\n=========================================================================\n'
printf 'SELFTEST RESULT   passed=%d   failed=%d\n' "$NPASS" "$NFAIL"
if [ "$NFAIL" -ne 0 ]; then
  printf 'FAILED TESTS:\n'
  for t in "${FAILED[@]}"; do printf '  - %s\n' "$t"; done
fi
printf 'scratch kept at %s\n' "$SCRATCH"
printf '=========================================================================\n'
[ "$NFAIL" -eq 0 ]
