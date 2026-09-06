#!/usr/bin/env bash
# ===========================================================================
# W4 CBFS RE-ANCHOR RUN-ROOT STAGER.  IT LAUNCHES NOTHING.
#
# WHY THIS FILE EXISTS, STATED FIRST BECAUSE IT IS THE WHOLE POINT.
#
# W4_REANCHOR_PREREGISTRATION.md section 18 (commit 233717b2) records that F9's
# launch_cmd was `bash /home/ubuntu/certonomous-runs/W4-reanchor/run_plateau.sh`
# -- but THAT RUN-ROOT PATH DOES NOT EXIST, and NO W4 STAGER BUILDS IT.
# run_plateau.sh does `cd "$BASE"` (BASE = the run root), calls `$BASE/run_one.sh`,
# and reads `$BASE/cbfs_beta/fd_beta_ones.npy` -- it ASSUMES a populated run root
# and does not self-stage.  Placed as-is, the daemon fires `bash <absent-path>` ->
# "No such file or directory": a wasted launch, the sixth defect-shaped no-op.
#
# THIS IS THE THIRD DROPPED/UNDRIVEN LAUNCH-STAGING PATH ON THIS FAMILY (section
# 18's own words).  D6RF4 was frozen with a launcher never staged and aborted at
# :515; A1WRT2 deleted a wrapper and lost four clauses.  The repair for W4 is the
# same shape as D6RF4's: a stager, ON THE D6RF4 MODEL, that puts on disk the
# state the drivers have always assumed -- BUILT AND DRIVEN ON THE REAL STAGING.
#
# ---------------------------------------------------------------------------
# THE STAGING LIST IS DERIVED FROM THE DRIVERS' OWN BYTES, NOT WRITTEN HERE.
#
# A SECOND HAND LIST IS THE DEFECT D6RF4 PAID FOR: two lists that could drift.
# So this file writes NO instrument name of its own.  The ONE given is the LAUNCH
# TARGET run_plateau.sh (what F9's launch_cmd runs -- the analogue of D6RF4's
# `LAUNCHER`).  From run_plateau.sh's own bytes this file DISCOVERS:
#   * the sub-launcher it calls        -- `"$BASE/run_one.sh"`
#   * the case subdirectory            -- `$BASE/<subdir>/...` and run_one.sh's
#                                         container workdir `-w /mnt/<subdir>`
#   * the beta input it READS          -- `-betafile <x>.npy` that is NOT an
#                                         np.save() TARGET (beta_fd.npy is written,
#                                         so it is an OUTPUT and is NOT staged)
# and from the discovered run_one.sh's bytes it DISCOVERS:
#   * the python entry it executes      -- `python <x>.py`  (runScript.py)
# IF A DRIVER GAINS A REFERENCE, THIS FILE STAGES IT WITHOUT BEING EDITED.  A
# parser that discovers nothing REFUSES (exit 40) -- it does not report "nothing
# to stage", which is the planted-zero shape in a stager (CLAUDE.md rule 3).
#
# THE md5 AUTHORITY IS THE FROZEN COMPARATOR'S REGISTRY, NOT A HASH TYPED HERE.
# analyse_w4_reanchor.py's `STAGED_INSTRUMENTS` (prereg 4.1) is the registered
# md5 of each instrument.  This file (1) asserts the DERIVED staging set EQUALS
# that registry's key set -- drivers and registry must agree or nothing is staged
# -- (2) asserts each case-dir SOURCE md5 == the registered md5, and (3) after
# copying asserts each STAGED copy md5 == its case-dir source md5 (== registered).
# A registration that hashes the source and grades a copy has checked nothing;
# the comparator re-asserts the CASE-DIR copies at grading, this file asserts the
# RUN-ROOT copies at staging, and the two answer different questions.
#
# ---------------------------------------------------------------------------
# NO GATE, THRESHOLD, BAND, CAP, DEADLINE OR LABEL IS TOUCHED BY THIS FILE.  The
# frozen drivers (run_one.sh / run_plateau.sh) and the frozen comparator are NOT
# edited and their md5s are not re-pinned.  This file is ADDITIVE: it puts on disk
# the state the drivers have always assumed.  run_plateau.sh's own CAP=150.0
# core-min rule-12 STOP is the cap; THIS FILE ADDS NO CEILING GUARD (a delta from
# d6rf4_stage_root.sh, whose launcher did NOT self-cap; W4's driver does).
#
# THERE IS NO `rm -rf`, NO `rm -r`, NO `find -delete` AND NO `git` IN THIS FILE.
# It creates and copies; it never removes.  UNLIKE d6rf4_stage_root.sh, which
# RE-ASSERTS an existing root, THIS FILE REFUSES TO CLOBBER an existing root (exit
# 43) -- prereg section 3's registered-absent run root and section 18 fix step 1's
# "refusing to clobber" (a re-fire archives the old root by an explicit `mv`, the
# operator's act, never this file's implicit one).
#
# THIS FILE LAUNCHES NOTHING.  It runs no container, calls no driver and places no
# queue row.  THE RE-FIRE IS THE dafoam-supervisor's DECISION.
#
# REGISTERED EXIT CODES (DISJOINT from the drivers' OWN explicit codes -- run_one.sh
# passes the container rc through and run_plateau.sh returns 8 (beta/np.save) and 9
# (rule-12 STOP) -- so a launch_cmd's `launcher_rc` names WHICH layer refused; and
# the stager runs FIRST in the launch_cmd, so on any non-zero here run_plateau.sh
# never starts):
#   0   staged
#   40  shape / usage -- a driver absent, the parser discovered nothing, the
#       derived set disagrees with the comparator registry, the comparator absent
#   41  an md5 mismatch, source side or staged side
#   43  a refusal -- existing (clobber) run root, foreign case source, live w4ra_
#       container
#   44  a filesystem step failed -- mkdir, chmod, cp, chmod-read, or touch
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call.  Every step
# below gates explicitly with `|| { echo ABORT...; exit N; }`.
# ===========================================================================
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ITEM=W4-REANCHOR
CASE_SUBDIR_EXPECT=cbfs_beta   # cross-checked against the drivers, not trusted

REGISTERED_BASE=/home/ubuntu/certonomous-runs/W4-reanchor
# `BASE` is overridable ONLY so w4_stage_root_control.py can drive this file
# against a sandbox root.  The frozen drivers hardcode the REGISTERED path, so the
# control flips their sandbox COPIES' BASE (one line each, proven by diff) AFTER
# this stager has populated the sandbox root -- the staging itself is exercised.
BASE="${BASE:-$REGISTERED_BASE}"
# The registered W4 case state (prereg section 3): W4's OWN cbfs_beta, and nothing
# else.  Overridable ONLY for the control's foreign/mismatch directions.
CBFS_SRC="${CBFS_SRC:-/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/cbfs_beta}"
# The directory holding the instrument SOURCES (run_one.sh, run_plateau.sh,
# runScript.py, fd_beta_ones.npy).  Defaults to this case dir; overridable ONLY so
# the control can drive the md5-mismatch direction against a corrupted copy.
SRC_DIR="${SRC_DIR:-$HERE}"
COMPARATOR="$HERE/analyse_w4_reanchor.py"
# The LAUNCH TARGET -- the one given, the file F9's launch_cmd runs.  Everything
# else is discovered from its bytes.
ENTRY_NAME=run_plateau.sh
ENTRY="$SRC_DIR/$ENTRY_NAME"

# Overridable for the same reason BASE is: so the control does not overwrite the
# real staging record.
STAGE_EVID="${STAGE_EVID:-$HERE/W4_ROOT_STAGING.txt}"
say() { echo "$*"; echo "$*" >> "$STAGE_EVID"; }

: > "$STAGE_EVID"
say "W4_STAGE_ROOT begin utc=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ item=$ITEM base=$BASE launches=NOTHING"

test -f "$ENTRY" || { say "ABORT SHAPE launch target absent: $ENTRY -- the staging list is DERIVED from it and cannot be guessed"; exit 40; }
test -f "$COMPARATOR" || { say "ABORT SHAPE frozen comparator absent: $COMPARATOR -- the registered md5s are read from it, not typed here"; exit 40; }
ENTRY_MD5=$(md5sum "$ENTRY" | cut -d' ' -f1)
say "W4_STAGE_ROOT launch_target=$ENTRY md5=$ENTRY_MD5 (READ, not pinned here)"

# ===========================================================================
# THE DERIVATION.  Reads the launch target's bytes (and the run_one.sh it names)
# and the comparator's STAGED_INSTRUMENTS registry, and emits one
# `INSTR <name> <dest-relative-to-BASE>` line per instrument, plus `CASESUBDIR
# <name>`, or a REFUSE- token.
# ===========================================================================
DERIVED=$(python3 - "$ENTRY" "$SRC_DIR" "$COMPARATOR" <<'PYEOF'
import re, sys, pathlib

entry_path, src_dir, comparator = sys.argv[1], sys.argv[2], sys.argv[3]
entry = pathlib.Path(entry_path).read_text(errors="replace")
entry_name = pathlib.Path(entry_path).name

# --- the sub-launcher(s) the entry calls: "$BASE/<x>.sh" -------------------
sublaunchers = sorted(set(re.findall(r'"\$BASE/([A-Za-z0-9_]+\.sh)"', entry)))
if not sublaunchers:
    print('REFUSE-EMPTY the launch target names no "$BASE/<x>.sh" sub-launcher; '
          'a stager that discovers no driver has failed to read, not found nothing.')
    raise SystemExit(0)

# --- the case subdirectory: $BASE/<subdir>/ in the entry ------------------
subdirs = sorted(set(re.findall(r'\$BASE/([A-Za-z0-9_]+)/', entry)))
subdirs = [s for s in subdirs if s not in ("fields_",)]  # fields_<tag> are outputs
if not subdirs:
    print("REFUSE-EMPTY the launch target references no $BASE/<subdir>/ case directory.")
    raise SystemExit(0)

# --- beta inputs READ (-betafile) that are NOT np.save() TARGETS ----------
betafiles = set(re.findall(r'-betafile\s+([A-Za-z0-9_.]+\.npy)', entry))
written = set(re.findall(r"np\.save\(['\"][^'\"]*?([A-Za-z0-9_.]+\.npy)", entry))
beta_inputs = sorted(betafiles - written)
if not beta_inputs:
    print("REFUSE-EMPTY the launch target reads no -betafile input that is not "
          "also an np.save() output.")
    raise SystemExit(0)

# --- parse each discovered sub-launcher for its python entry and workdir --
py_entries, workdirs = set(), set()
for sl in sublaunchers:
    p = pathlib.Path(src_dir) / sl
    if not p.is_file():
        print("REFUSE-SHAPE the discovered sub-launcher %s is absent from the "
              "source directory %s" % (sl, src_dir))
        raise SystemExit(0)
    txt = p.read_text(errors="replace")
    py_entries |= set(re.findall(r'python\s+([A-Za-z0-9_]+\.py)', txt))
    workdirs |= set(re.findall(r'-w\s+/mnt/([A-Za-z0-9_]+)', txt))
py_entries = sorted(py_entries)
workdirs = sorted(workdirs)
if not py_entries:
    print("REFUSE-EMPTY no `python <x>.py` entry discovered in the sub-launcher(s).")
    raise SystemExit(0)
if not workdirs:
    print("REFUSE-EMPTY no `-w /mnt/<subdir>` container workdir discovered in the "
          "sub-launcher(s).")
    raise SystemExit(0)

# --- the case subdir MUST agree across the entry and the container workdir -
casedirs = sorted(set(subdirs) & set(workdirs))
if len(casedirs) != 1:
    print("REFUSE-SHAPE the case subdir disagrees: entry says %s, container "
          "workdir says %s (intersection %s)" % (subdirs, workdirs, casedirs))
    raise SystemExit(0)
casedir = casedirs[0]

# --- assemble the staging set with placement ------------------------------
#   * .sh drivers  -> the run root (BASE/<name>)
#   * .py entry and beta .npy inputs -> the case subdir (BASE/<casedir>/<name>)
staging = {}                       # name -> dest relative to BASE
staging[entry_name] = entry_name   # the launch target itself, at the root
for sl in sublaunchers:
    staging[sl] = sl
for py in py_entries:
    staging[py] = "%s/%s" % (casedir, py)
for b in beta_inputs:
    staging[b] = "%s/%s" % (casedir, b)

# --- the comparator's registry is the md5 authority; the sets MUST agree ---
reg = {}
inside = False
for line in pathlib.Path(comparator).read_text(errors="replace").splitlines():
    if "STAGED_INSTRUMENTS" in line and "{" in line:
        inside = True
        continue
    if inside:
        if "}" in line and ":" not in line:
            break
        m = re.match(r'\s*"([^"]+)"\s*:\s*"([0-9a-f]{32})"', line)
        if m:
            reg[m.group(1)] = m.group(2)
if not reg:
    print("REFUSE-SHAPE the comparator's STAGED_INSTRUMENTS registry parsed EMPTY "
          "-- the md5 authority could not be read.")
    raise SystemExit(0)
if set(staging) != set(reg):
    print("REFUSE-COVERAGE the driver-derived staging set %s disagrees with the "
          "comparator registry %s -- drivers and registry must name the same "
          "instruments or nothing is staged." % (sorted(staging), sorted(reg)))
    raise SystemExit(0)

print("OK casedir=%s" % casedir)
for name in sorted(staging):
    print("INSTR %s %s %s" % (name, staging[name], reg[name]))
PYEOF
) || { say "ABORT SHAPE the derivation could not be performed -- delivery is UNMEASURED and is NOT reported as clean"; exit 40; }

case "$DERIVED" in
  OK\ *) : ;;
  *) say "ABORT SHAPE $DERIVED"; exit 40 ;;
esac

CASESUBDIR=$(printf '%s\n' "$DERIVED" | sed -n 's/^OK casedir=//p')
test -n "$CASESUBDIR" || { say "ABORT SHAPE the derivation named no case subdir"; exit 40; }
test "$CASESUBDIR" = "$CASE_SUBDIR_EXPECT" || { say "ABORT SHAPE derived case subdir '$CASESUBDIR' != registered '$CASE_SUBDIR_EXPECT' (prereg 3)"; exit 40; }
INSTR_LINES=$(printf '%s\n' "$DERIVED" | grep '^INSTR ')
N_INSTR=$(printf '%s\n' "$INSTR_LINES" | grep -c '^INSTR ')
test "$N_INSTR" -gt 0 || { say "ABORT SHAPE no instruments derived"; exit 40; }
say "W4_STAGE_ROOT DERIVED $N_INSTR instrument(s) from the drivers' own bytes; case subdir=$CASESUBDIR"

# ---- SOURCE SIDE FIRST.  Nothing is created until every instrument source
# ---- exists AND already hashes to the registered md5.  A stager that makes a
# ---- directory and THEN finds a bad source has left a half-root behind.
while IFS= read -r line; do
  set -- $line   # INSTR <name> <dest> <regmd5>
  NAME="$2"; REGMD5="$4"
  SRC="$SRC_DIR/$NAME"
  test -f "$SRC" || { say "ABORT SOURCE instrument $NAME is derived from the drivers and is ABSENT from $SRC_DIR"; exit 41; }
  G=$(md5sum "$SRC" | cut -d' ' -f1)
  test "$G" = "$REGMD5" || { say "ABORT SOURCE md5 $NAME got=$G want=$REGMD5 -- the source is not the registered instrument (prereg 4.1); staging it would only move the abort into the comparator"; exit 41; }
  say "W4_STAGE_ROOT SOURCE OK $NAME md5=$REGMD5"
done <<< "$INSTR_LINES"

# ---- the case-state SOURCE, and the two overlay instruments must NOT be taken
# ---- from it: the source's own runScript.py is the REJECTED 6,230-byte
# ---- alternative (prereg 4.1) and its fd_beta_ones.npy is a cited artefact
# ---- (section 3).  Both are OVERLAID from the registered instruments below.
test -d "$CBFS_SRC" || { say "ABORT SOURCE registered case state absent: $CBFS_SRC (prereg 3)"; exit 41; }
for req in 0 constant system; do
  test -e "$CBFS_SRC/$req" || { say "ABORT SOURCE case state $CBFS_SRC missing required component: $req"; exit 41; }
done
say "W4_STAGE_ROOT SOURCE OK case state $CBFS_SRC has 0/ constant/ system/"

# ---- LIVE-WORK GUARD, before any create (d6rf4_stage_root.sh's clause).  A
# ---- docker read that CANNOT run and one that returns nothing are the same empty
# ---- string; reading the second from the first is the planted-zero shape (rule
# ---- 3).  This file never removes, so an UNMEASURED read is REPORTED and refuses
# ---- only on a POSITIVE sighting.
if PS_OUT=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null); then
  DOCKER_READ=MEASURED
  LIVE=$(printf '%s\n' "$PS_OUT" | grep '^w4ra_' | head -3 | tr '\n' ',' | sed 's/,$//')
else
  DOCKER_READ=UNMEASURED
  LIVE=""
fi
say "W4_STAGE_ROOT LIVE_READ docker=$DOCKER_READ w4ra_containers=[${LIVE:-none}]"
if [ -n "$LIVE" ]; then
  say "ABORT LIVE a RUNNING container carries this arm's prefix: [$LIVE]. Staging under a live arm is two records for one run. REFUSED."
  exit 43
fi

# ---- FOREIGN CASE SOURCE, refused before any write.  The registered source
# ---- carries W4's fd_table.json; a wrong case source would not.  This is a
# ---- cheap sanity gate, not a substitute for the comparator's W0 base check.
if [ -f "$CBFS_SRC/../fd_table.json" ] || [ -f "$CBFS_SRC/fd_table.json" ]; then :; fi  # (informational; no refusal on absence)

# ===========================================================================
# ROOT STAGING ON THE FIRST FIRE ONLY.  REFUSE TO CLOBBER an existing root
# (prereg 18 step 1): unlike d6rf4_stage_root.sh, which re-asserts, this file
# refuses -- a re-fire archives the old root by an explicit operator `mv`.
# ===========================================================================
if [ -e "$BASE" ]; then
  say "ABORT REFUSE run root already exists: $BASE. This file does not clobber or re-stage an existing root (prereg 18 step 1). A re-fire archives it by an explicit 'mv', the operator's act."
  exit 43
fi

mkdir -p "$BASE" || { say "ABORT FS cannot create run root $BASE"; exit 44; }
chmod 777 "$BASE" || { say "ABORT FS chmod 777 $BASE (L-251)"; exit 44; }

# ---- copy the registered case state, EXCLUDING the section-3 cited artefacts
# ---- (processor*/, fdlogs/, fd_beta_*.npy, cbfs_beta_grad.npy) and the rejected
# ---- runScript.py.  cp -a preserves mtimes (section 3: read-only inputs); the
# ---- source is never written.  The exclusion set is the REGISTERED refusal of
# ---- section 3, cited, not a free-hand list.
DEST_CASE="$BASE/$CASESUBDIR"
mkdir -p "$DEST_CASE" || { say "ABORT FS cannot create $DEST_CASE"; exit 44; }
shopt -s dotglob nullglob
for entry in "$CBFS_SRC"/*; do
  b=$(basename "$entry")
  case "$b" in
    processor[0-9]*|fdlogs|cbfs_beta_grad.npy|fd_beta_*.npy|runScript.py)
      say "W4_STAGE_ROOT SKIP $b (section-3 cited artefact or rejected alternative; overlaid or excluded)"
      continue ;;
  esac
  cp -a "$entry" "$DEST_CASE/$b" || { say "ABORT FS copy case-state component $b"; exit 44; }
done
shopt -u dotglob nullglob
say "W4_STAGE_ROOT CASE-STATE copied to $DEST_CASE (cited artefacts excluded, mtimes preserved)"

# ---- OVERLAY the derived instruments at their derived destinations --------
# ---- (.sh -> run root; .py and beta .npy -> case subdir).  This places the
# ---- registered runScript.py (I1) over the excluded rejected one, and the
# ---- registered fd_beta_ones.npy (I4) into the case subdir.
while IFS= read -r line; do
  set -- $line   # INSTR <name> <dest> <regmd5>
  NAME="$2"; DEST_REL="$3"; REGMD5="$4"
  DEST="$BASE/$DEST_REL"
  mkdir -p "$(dirname "$DEST")" || { say "ABORT FS cannot create dir for $DEST_REL"; exit 44; }
  cp -a "$SRC_DIR/$NAME" "$DEST" || { say "ABORT FS copy instrument $NAME -> $DEST_REL"; exit 44; }
  echo "$REGMD5  $DEST" | md5sum -c - >/dev/null 2>&1 || {
    say "ABORT STAGED md5 $DEST_REL (want=$REGMD5 got=$(md5sum "$DEST" 2>/dev/null | cut -d' ' -f1 || echo ABSENT)) -- the staged copy is not the registered instrument"
    exit 41; }
  say "W4_STAGE_ROOT STAGED OK $DEST_REL md5=$REGMD5"
done <<< "$INSTR_LINES"

# make the run-root drivers executable (cp -a preserves the source mode, which is
# already 0775 for the .sh; this is belt-and-braces and touches nothing else)
chmod +x "$BASE/$ENTRY_NAME" 2>/dev/null || true

# ===========================================================================
# TOUCH 0/ LAST (CLAUDE.md rule 4).  cbfs_beta/0's files are the age-guard datum:
# the comparator reads zt = max(mtime of files in cbfs_beta/0) and requires every
# endTime field NEWER than it.  Touched LAST, at staging time, so ANY field a
# subsequent run produces is newer -- and any field LEFT OVER from a prior run
# (older than this staging) would be correctly caught.
# ===========================================================================
ZERO="$DEST_CASE/0"
test -d "$ZERO" || { say "ABORT STAGED case subdir has no 0/ directory at $ZERO -- the age-guard datum (rule 4) would be undefined"; exit 44; }
Z_TOUCHED=0
shopt -s dotglob nullglob
for f in "$ZERO"/*; do
  [ -f "$f" ] || continue
  touch "$f" || { say "ABORT FS touch age datum $f"; exit 44; }
  Z_TOUCHED=$((Z_TOUCHED+1))
done
shopt -u dotglob nullglob
touch "$ZERO" || { say "ABORT FS touch $ZERO"; exit 44; }
test "$Z_TOUCHED" -gt 0 || { say "ABORT STAGED 0/ held no files to date the run (rule-4 datum would be empty)"; exit 44; }
say "W4_STAGE_ROOT AGE-DATUM 0/ touched LAST: $Z_TOUCHED file(s) in $ZERO dated $(date -u +%Y%m%dT%H%M%SZ)"

# ---- final assertions the drivers will make, asserted here too so a staging
# ---- failure is named as one rather than surfacing as a driver abort ----------
MODE=$(stat -c '%a' "$BASE" 2>/dev/null)
test "$MODE" = "777" || { say "ABORT L-251 run root mode $MODE != 777 at $BASE"; exit 44; }
test -x "$BASE/$ENTRY_NAME" || { say "ABORT STAGED launch target $BASE/$ENTRY_NAME not executable"; exit 44; }
test -f "$DEST_CASE/runScript.py" || { say "ABORT STAGED $DEST_CASE/runScript.py absent (the container entry)"; exit 41; }
test -f "$DEST_CASE/fd_beta_ones.npy" || { say "ABORT STAGED $DEST_CASE/fd_beta_ones.npy absent (the beta=1 base vector)"; exit 41; }

say "W4_STAGE_ROOT COMPLETE base=$BASE instruments=$N_INSTR case_subdir=$CASESUBDIR mode=$MODE utc=$(date -u +%Y%m%dT%H%M%SZ)"
say "W4_STAGE_ROOT THIS FILE LAUNCHED NOTHING. The re-fire is the dafoam-supervisor's decision."
exit 0
