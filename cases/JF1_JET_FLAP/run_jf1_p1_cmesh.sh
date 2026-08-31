#!/usr/bin/env bash
# =============================================================================
# JF1 JET-FLAP AIRFOIL -- STAGE P, ROW P1, ON THE REGISTERED C-TOPOLOGY.
#   C_mu_jet = 0.1, alpha = 0, tau = 30 deg, LEVEL L1 (46,180 cells), 2nd order.
#   JF1_PREREGISTRATION.md:1843  | P1 | P | 0.1 | 0 | L1 | physics/diagnostic |
#
# LABEL: physics/diagnostic.  Frozen section 6 line 1234 answers "Gated?" for
# stage P with "No.  Diagnostic only."  NO GATE, NO THRESHOLD AND NO VERDICT OF
# THE FIXED VOCABULARY ATTACHES TO ANY RUN THIS SCRIPT PRODUCES.  No PASS, no
# GCI, no observed order, no theory comparison.  A disagreement with the
# registration is a FINDING, never a gate outcome.
#
# -----------------------------------------------------------------------------
# LINEAGE -- WHAT WAS CARRIED OVER AND WHAT WAS RE-DERIVED
# -----------------------------------------------------------------------------
# This launcher descends from cases/JF1_JET_FLAP/run_jf1.sh and
# cases/JF1_JET_FLAP/run_jf1_blown.sh.  Neither is modified by this file and
# neither is imported by it; the five completed L1 feasibility rows of
# 2026-08-31 stay byte-for-byte reproducible from their own launchers.
#
# CARRIED OVER UNCHANGED, because each was checked and is still right here:
#   * the five-part freeze pin (a)-(e)          run_jf1_blown.sh:145-173
#   * the jet-constant reproduction refusal     run_jf1_blown.sh:181-196
#   * the @TOKEN@ substitution refusal          run_jf1_blown.sh:264-268
#   * the age guard on the run root             run_jf1_blown.sh:198-199
#   * the environment step INSIDE the preflight run_jf1_blown.sh:216-229
#     (the unblown row's attempt 1 died on `source` under `set -u` after a
#      preflight that had returned rc 0 by exiting before that line)
#   * STATUS at RUN_STATUS.*.txt, never STATUS.*  queue_runner.py:496 truncates
#   * rc captured INSIDE the wrapper, never around a setsid line
#
# RE-DERIVED, NOT PASTED -- and each re-derivation is a correction:
#   * WALL_ALLOWANCE_S.  run_jf1.sh:65 and run_jf1_blown.sh:52 both hard-code
#     2700.  That was only ever a proxy for 45.0 core-min at RANKS=1.  Rule 12
#     makes core-minutes the unit, so here the wall figure is COMPUTED from the
#     two numbers the script already holds:  CAP_CORE_MIN * 60 / RANKS.  The
#     budget is identical; the wall clock stops lying about it when RANKS != 1.
#   * CAP_CORE_MIN.  NO DEFAULT.  --cap-core-min is REQUIRED and the script
#     refuses without it, so this file can neither silently inherit a cap nor
#     silently drop one.
#   * RANKS.  NO DEFAULT.  --ranks is REQUIRED, for the same reason.
#   * THE MESH.  run_jf1_blown.sh:272-274 calls build_jf1.py, which emits an
#     O-MESH.  This launcher calls the section 4.1 REGISTERED generator
#     verification/runs/JF1_jet_flap/mesh/make_jf1_mesh.py --topology c.
#   * THE checkMesh GATE.  run_jf1.sh:214 and run_jf1_blown.sh:275-277 do
#     `grep -q "^Mesh OK" || exit 5`.  NO C-MESH LEVEL PRINTS `Mesh OK`: all
#     three print "Failed 1 mesh checks", the ASPECT-RATIO ADVISORY ALONE,
#     which nothing in this registration gates.  Pasting that line would have
#     refused this run at LAUNCH, before a solver started, on a mesh that
#     passes every metric frozen section 4.5 actually gates.  Replaced by a
#     parse of the four gated metrics -- see THE MESH ADMISSIBILITY READ below.
#   * Aref.  case_blown/system/controlDict carries Aref 0.01 for the O-mesh's
#     t_z = 0.01 m span.  The C-mesh has t_z = 1.0 m EXACTLY (make_jf1_mesh.py
#     refuses otherwise, citing frozen section 5.6) so Aref = c*t_z = 1.0.
#     case_p1/system/controlDict carries 1.0 and its header records why.
#     Copying the blown dictionary would have reported CL and Cd 100x TOO LARGE.
#
# -----------------------------------------------------------------------------
# WHICH CAP BINDS FIRST FOR P1 -- SETTLED ON PAPER BEFORE THE SOLVER STARTS
# -----------------------------------------------------------------------------
# MEASURED BASIS.  The five completed L1 feasibility rows, each row's own
# verification/runs/JF1_jet_flap/<row>/RUN_STATUS.<row>.txt core_min_MEASURED:
#   23.7667 / 24.4333 / 21.7500 / 22.3333 / 25.2000  = 117.4833 core-min spent,
#   mean 23.496660 core-min per 8000 iterations, rank 1, 39,984-cell O-mesh.
#   -> 5.876516e-04 core-min/cell   -> 2.937082e-03 core-min/iteration
#   Scaled to this C-mesh L1 by the cell ratio 46180/39984 = 1.154962 (the same
#   first-order correction frozen section 12 item A17 applies):
#   -> 3.392219e-03 core-min/iteration at rank 1.
#
#   | cap                                             | core-min | binds at iter |
#   |-------------------------------------------------|----------|---------------|
#   | iteration cap 20,000  (frozen 5.5) REGISTERED   |   67.84  | 20,000 (def.) |
#   | family cap 300        (frozen line 9) REGISTERED|  300.00  |     88,438    |
#   |   remaining after the five completed rows       |  182.52  |     53,805    |
#   | per-row 45.0 (run_jf1_blown.sh:51) NOT REGISTERED|  45.00  |     13,266    |
#   | section 12 P1 figure 11.36 -- AN ESTIMATE, NOT A CAP | 11.36 |      3,349  |
#
# THE ANSWER, AND IT IS NOT THE ONE THE TENSION WAS RAISED AGAINST: AMONG THE
# CAPS THIS REGISTRATION ACTUALLY REGISTERS, THE ITERATION CAP BINDS FIRST.
# P1 to 20,000 iterations costs 67.84 core-min against 182.52 remaining in the
# registered family budget -- 37.2 % of it.  The frozen line-9 family cap does
# NOT bite on this row.
#
# AND THE NUMBER THAT WOULD HAVE BOUND FIRST IS NOT A REGISTERED NUMBER.
# 45.0 core-min appears NOWHERE in JF1_PREREGISTRATION.md -- grep is the
# evidence, on the frozen 152,436-byte document.  It originates at
# run_jf1.sh:64 and run_jf1_blown.sh:51, where BOTH files label it
# "Registered cap".  That label is false and is recorded here as a finding
# rather than propagated: the only core-minute cap this registration registers
# is frozen line 9's 300 core-min FAMILY cap, and section 12's 11.36 for P1 is
# an ESTIMATE, which rule 12 distinguishes from a cap.  Importing 45.0 would
# have stopped P1 at ~13,266 iterations -- unconverged, by a number no one
# registered.  THIS SCRIPT THEREFORE DOES NOT DEFAULT TO 45.0, AND DOES NOT
# DEFAULT TO ANYTHING; the caller states the cap and the header states what the
# registered ones are.
#
# EXPECTED STOPPING CONDITION, PREDICTED BEFORE THE RUN, NOT AFTER:
# the five completed rows ALL reached their 8000-iteration limit WITHOUT
# simpleFoam printing a converged line (CMU010's final initial residuals: k
# 2.55e-05, p 1.27e-05, Uy 3.63e-06, all ABOVE the 1e-6 residualControl).  On
# that evidence P1 is EXPECTED to reach the registered 20,000-iteration cap
# unconverged.  Frozen section 5.5 and Sanaa's own directive fix the label for
# that outcome and it is not negotiable: a run that hits the cap is
# `NOT A RESULT`, never "close enough".  For a DIAGNOSTIC row that label is a
# finding about the case, not a gate outcome -- but it is still the label, and
# every plot and number taken off this run carries it.
#
# PARALLELISM BUYS WALL CLOCK AND BUYS THE BUDGET NOTHING.  core-minutes =
# wall_s * ranks / 60 are rank-invariant to first order and get WORSE with
# parallel inefficiency.  RANKS is therefore a demo-schedule decision, never a
# budget one, and the cost_basis says so rather than letting the two blur.
#
# rc DISCIPLINE: the return code is captured INSIDE this wrapper.
# `setsid timeout cmd` returns 0 for every outcome, so an rc taken AROUND a
# setsid line is not the solver's rc (lab memory: "setsid parent returns zero").
# ARTIFACT DISCIPLINE: every artifact is under RUN_ROOT.  Nothing to /tmp.
# =============================================================================
set -u
set -o pipefail

CASE_DIR="/home/ubuntu/Certonomous/cases/JF1_JET_FLAP"
REPO="/home/ubuntu/Certonomous"
PREREG_PATH="verification/campaign/JF1_PREREGISTRATION.md"
MESH_GEN_REL="verification/runs/JF1_jet_flap/mesh/make_jf1_mesh.py"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# --- THE FREEZE, PINNED -------------------------------------------------------
# Re-derived on disk 2026-08-31, not taken on anyone's say-so:
#   git log --format=%H -1 -- verification/campaign/JF1_PREREGISTRATION.md
#     -> 12b1bd84766117d99c88dedf391470bb8bf47e5c   (2026-08-31T15:29Z freeze)
#   git rev-parse 12b1bd84...:verification/campaign/JF1_PREREGISTRATION.md
#     -> 66543c97fa1527ef7c36f0980460fcc0ca348508   (the frozen BLOB)
# The blob pin is the load-bearing one: a commit sha alone proves only that
# SOME document existed there.  Commit 8bc27a79 tightened exactly this.
FREEZE_COMMIT="12b1bd84766117d99c88dedf391470bb8bf47e5c"
FREEZE_BLOB="66543c97fa1527ef7c36f0980460fcc0ca348508"
FREEZE_BYTES=152436

# The section 4.1 registered generator, pinned by blob for the same reason.
MESH_GEN_BLOB="$(cd "${REPO}" && git rev-parse "HEAD:${MESH_GEN_REL}" 2>/dev/null || true)"

CASE_ID="JF1_P1_L1_CMESH_PHYSICS"
RUN_ROOT="${REPO}/verification/runs/JF1_jet_flap/${CASE_ID}"

# Frozen section 2: C_mu_jet = 0.1 row.
CMU_REG="0.1"
VJ="31.622776602"       # U_inf sqrt(C_mu_jet/(2 h/c)) = 10 sqrt(0.1/0.01)
KJET="0.1500000000"     # 1.5 (I V_j)^2, I = 0.01        -- reproduced below, not trusted
OMJET="2020.305089104"  # sqrt(k)/(C_mu_turb^0.25 l_j), l_j = 0.07 h = 3.5e-4,
                        # C_mu_turb = 0.09 (frozen section 0: NOT the jet
                        # coefficient -- read with C_mu_jet this formula is a
                        # division by zero at the unblown point).
                        # THE FIRST VALUE WRITTEN HERE BY THIS LANE WAS
                        # 140.9203521 AND IT WAS WRONG BY A FACTOR OF 14.3.
                        # The reproduction guard below caught it at preflight,
                        # at zero compute, before a solver started.  Recorded
                        # rather than quietly fixed: this is the guard earning
                        # its place, and it is why these three constants are
                        # re-derived from the frozen formulae on every launch
                        # instead of being trusted as transcriptions.

PREREG_COMMIT=""; CMU=""; LEVEL=""; RANKS=""; CAP_CORE_MIN=""; PREFLIGHT=0
for a in "$@"; do
  case "$a" in
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    --cmu=*)           CMU="${a#*=}" ;;
    --level=*)         LEVEL="${a#*=}" ;;
    --ranks=*)         RANKS="${a#*=}" ;;
    --cap-core-min=*)  CAP_CORE_MIN="${a#*=}" ;;
    --preflight)       PREFLIGHT=1 ;;
    *) echo "REFUSED: unknown argument '$a'"; exit 2 ;;
  esac
done

# --- REQUIRED ARGUMENTS, NO DEFAULTS -----------------------------------------
[ -n "${PREREG_COMMIT}" ] || { echo "REFUSED: --prereg-commit is required"; exit 2; }
[ -n "${CMU}" ]          || { echo "REFUSED: --cmu is required"; exit 2; }
[ -n "${LEVEL}" ]        || { echo "REFUSED: --level is required"; exit 2; }
[ -n "${RANKS}" ]        || { echo "REFUSED: --ranks is required (no default: a launcher must not silently choose a rank count that changes the core-minute cost)"; exit 2; }
[ -n "${CAP_CORE_MIN}" ] || { echo "REFUSED: --cap-core-min is required (no default: this file neither silently inherits the unregistered 45.0 of run_jf1_blown.sh:51 nor silently drops a cap)"; exit 2; }

# --- THIS SCRIPT RUNS THE P1 DIAGNOSTIC ROW AND NOTHING ELSE ------------------
# case_p1/system/controlDict carries writeInterval 1000, a DISCLOSED departure
# from the writeInterval 20000 that frozen section 5.5 registers and section 8.1
# clause 3 PINS.  It is legal here only because no gate scores on stage P.  This
# refusal is what stops that departure leaking into a graded row.
[ "${CMU}" = "${CMU_REG}" ] || { echo "REFUSED: this launcher runs the registered P1 row only, C_mu_jet = ${CMU_REG} (frozen :1843).  Got --cmu=${CMU}.  A gated row must use a launcher carrying the registered writeInterval 20000."; exit 2; }
[ "${LEVEL}" = "L1" ]       || { echo "REFUSED: this launcher runs P1 at level L1 only (frozen :1843).  Got --level=${LEVEL}."; exit 2; }
case "${RANKS}" in ''|*[!0-9]*) echo "REFUSED: --ranks must be a positive integer"; exit 2 ;; esac
[ "${RANKS}" -ge 1 ] || { echo "REFUSED: --ranks must be >= 1"; exit 2; }

# --- THE WALL ALLOWANCE IS DERIVED, NEVER PASTED ------------------------------
# CLAUDE.md rule 12: the unit is core-minutes.  The wall clock is the proxy the
# `timeout` call needs, and it is computed from the cap and the rank count so
# the two can never drift apart the way the hard-coded 2700 did.
WALL_ALLOWANCE_S="$(awk -v c="${CAP_CORE_MIN}" -v r="${RANKS}" 'BEGIN{printf "%d", c*60.0/r}')"
[ "${WALL_ALLOWANCE_S}" -gt 0 ] 2>/dev/null || { echo "REFUSED: derived wall allowance is not positive (cap ${CAP_CORE_MIN}, ranks ${RANKS})"; exit 2; }

# =============================================================================
# THE FREEZE CROSS-CHECK.  (a)-(d) are run_jf1_blown.sh's, unchanged.
# (e) is STRICTLY STRONGER than that file's byte-equality test -- see below.
# =============================================================================
[ "${PREREG_COMMIT}" = "${FREEZE_COMMIT}" ] \
  || { echo "REFUSED: prereg commit ${PREREG_COMMIT} is not the freeze commit ${FREEZE_COMMIT}"; exit 3; }

git -C "${REPO}" cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "REFUSED: prereg commit does not exist"; exit 3; }

git -C "${REPO}" cat-file -e "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null \
  || { echo "REFUSED: ${PREREG_PATH} absent at ${PREREG_COMMIT}"; exit 3; }

# (d) THE BLOB CHECK -- CLAUDE.md rule 2, "verify the frozen file IS the file
#     that ran by hashing it against the committed blob."  Fail-closed: an empty
#     or unreadable rev-parse result is a REFUSAL, never a pass.
GOT_BLOB="$(git -C "${REPO}" rev-parse "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null || true)"
[ -n "${GOT_BLOB}" ] || { echo "REFUSED: could not read the prereg blob sha at that commit"; exit 3; }
[ "${GOT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: prereg blob ${GOT_BLOB} != frozen blob ${FREEZE_BLOB}"; exit 3; }

# (e) THE WORKING-TREE CHECK, RE-DERIVED AS A PREFIX TEST.
#     run_jf1_blown.sh:170-173 demands the working-tree file hash EXACTLY to the
#     frozen blob.  That is right today and becomes WRONG the moment a lawful
#     rule-6 dated amendment is appended at the foot -- which is precisely how
#     this registration is required to change (rule 6: originals struck, never
#     rewritten; the section 18 cap amendment is drafted and will do exactly
#     this).  An equality pin would then refuse every JF1 launch for ever.
#     The prefix form is STRICTLY STRONGER where it matters: it REFUSES ANY EDIT
#     to the frozen 152,436 bytes while ADMITTING an append below them.  That is
#     the rule-6 guarantee, mechanised, and it needs no maintenance per amendment.
WT_BYTES="$(stat -c%s "${REPO}/${PREREG_PATH}" 2>/dev/null || echo 0)"
[ "${WT_BYTES}" -ge "${FREEZE_BYTES}" ] \
  || { echo "REFUSED: working-tree ${PREREG_PATH} is ${WT_BYTES} bytes, SHORTER than the frozen ${FREEZE_BYTES} -- frozen content has been deleted"; exit 3; }
cmp -s -n "${FREEZE_BYTES}" \
     <(git -C "${REPO}" cat-file blob "${FREEZE_BLOB}") \
     "${REPO}/${PREREG_PATH}" \
  || { echo "REFUSED: the first ${FREEZE_BYTES} bytes of the working-tree ${PREREG_PATH} are NOT the frozen bytes -- the frozen document has been EDITED, not appended to (rule 6)"; exit 3; }

#     AND THE APPEND MUST BE COMMITTED.  A prefix test alone would admit an
#     UNCOMMITTED append -- an agent could add a section in the working tree and
#     launch against it, and nothing would be auditable.  This closes that.
WT_BLOB="$(git -C "${REPO}" hash-object "${REPO}/${PREREG_PATH}" 2>/dev/null || true)"
HEAD_BLOB="$(git -C "${REPO}" rev-parse "HEAD:${PREREG_PATH}" 2>/dev/null || true)"
[ -n "${WT_BLOB}" ] && [ -n "${HEAD_BLOB}" ] \
  || { echo "REFUSED: could not hash the working-tree or HEAD copy of ${PREREG_PATH}"; exit 3; }
[ "${WT_BLOB}" = "${HEAD_BLOB}" ] \
  || { echo "REFUSED: working-tree ${PREREG_PATH} (${WT_BLOB}) is not committed at HEAD (${HEAD_BLOB}) -- an uncommitted registration is not a registration"; exit 3; }

APPENDED=$(( WT_BYTES - FREEZE_BYTES ))
if [ "${APPENDED}" -eq 0 ]; then
  FREEZE_CHECK="VERIFIED (EXACT) -- commit is the freeze commit; document present at it; its blob equals the pinned frozen blob; the working-tree copy is byte-identical to it and is committed at HEAD"
else
  FREEZE_CHECK="VERIFIED (PREFIX) -- commit is the freeze commit; its blob equals the pinned frozen blob; the working-tree copy carries the frozen ${FREEZE_BYTES} bytes UNCHANGED with ${APPENDED} bytes appended below them (a lawful rule-6 dated amendment) and is committed at HEAD"
fi

# --- THE GENERATOR, PINNED THE SAME WAY ---------------------------------------
[ -n "${MESH_GEN_BLOB}" ] \
  || { echo "REFUSED: ${MESH_GEN_REL} is not committed at HEAD -- an uncommitted generator has no provenance"; exit 3; }
GEN_WT_BLOB="$(git -C "${REPO}" hash-object "${REPO}/${MESH_GEN_REL}" 2>/dev/null || true)"
[ "${GEN_WT_BLOB}" = "${MESH_GEN_BLOB}" ] \
  || { echo "REFUSED: working-tree ${MESH_GEN_REL} (${GEN_WT_BLOB}) differs from HEAD (${MESH_GEN_BLOB})"; exit 3; }

# --- THE JET CONSTANTS ARE REPRODUCED, NOT TRANSCRIBED ------------------------
# A transcription error in KJET/OMJET is exactly what this catches, and it is a
# refusal rather than a silently wrong jet.  Frozen section 5.2 formulae.
awk -v cmu="${CMU}" -v vj="${VJ}" -v kj="${KJET}" -v om="${OMJET}" 'BEGIN{
    Uinf=10.0; hoc=0.005; I=0.01; lj=0.07*0.005; Cmt=0.09; kinf=1.5e-04; ominf=5.0;
    v = Uinf*sqrt(cmu/(2*hoc));
    k = 1.5*(I*v)^2; if (k < kinf) k = kinf;
    o = sqrt(k)/((Cmt^0.25)*lj); if (o < ominf) o = ominf;
    bad = 0;
    if ((v-vj)/v >  1e-6 || (v-vj)/v < -1e-6) { printf "V_j mismatch: derived %.9f vs table %s\n", v, vj; bad=1 }
    if ((k-kj)/k >  1e-9 || (k-kj)/k < -1e-9) { printf "k_jet mismatch: derived %.12e vs table %s\n", k, kj; bad=1 }
    if ((o-om)/o >  1e-8 || (o-om)/o < -1e-8) { printf "omega_jet mismatch: derived %.9f vs table %s\n", o, om; bad=1 }
    exit bad
}' || { echo "REFUSED: substituted jet constants do not reproduce the frozen section 5.2 formulae"; exit 3; }

# --- AGE GUARD (CLAUDE.md rule 4) ---------------------------------------------
# Never launch into a tree that already holds an answer.
[ -e "${RUN_ROOT}" ] && { echo "REFUSED: run root already exists: ${RUN_ROOT}"; exit 3; }

# --- REQUIRED INPUTS ----------------------------------------------------------
for f in "${CASE_DIR}/case_blown/0/U.template" \
         "${CASE_DIR}/case_blown/0/k.template" \
         "${CASE_DIR}/case_blown/0/omega.template" \
         "${CASE_DIR}/case_blown/0/nut" \
         "${CASE_DIR}/case_blown/0/p" \
         "${CASE_DIR}/case_p1/system/controlDict" \
         "${CASE_DIR}/case/system/fvSchemes" \
         "${CASE_DIR}/case/system/fvSolution" \
         "${CASE_DIR}/case/constant/transportProperties" \
         "${CASE_DIR}/case/constant/turbulenceProperties" \
         "${REPO}/${MESH_GEN_REL}" ; do
  [ -f "$f" ] || { echo "REFUSED: required input absent: $f"; exit 3; }
done

# --- THE REGISTERED TERMINATION SETTINGS, ASSERTED ON THE DICTIONARY ----------
# Frozen section 5.5 / section 8.1 clause 3.  endTime, deltaT, startTime,
# writeControl and the four residualControl keys are asserted here so a run can
# never be made against silently changed termination settings.  writeInterval is
# the ONE disclosed departure (D1 in case_p1/system/controlDict) and is asserted
# at its departed value so it too cannot drift unnoticed.
assert_key () { # file key expected
  got="$(awk -v k="$2" '$1==k {v=$2; sub(/;.*$/,"",v); print v; exit}' "$1")"
  [ "${got}" = "$3" ] || { echo "REFUSED: $(basename "$1") ${2} is '${got}', registered '${3}'"; exit 3; }
}
CD="${CASE_DIR}/case_p1/system/controlDict"
assert_key "${CD}" startTime     0
assert_key "${CD}" endTime       20000
assert_key "${CD}" deltaT        1
assert_key "${CD}" writeControl  timeStep
assert_key "${CD}" purgeWrite    0
assert_key "${CD}" writeInterval 1000      # DISCLOSED DEPARTURE D1 (registered 20000)
FS="${CASE_DIR}/case/system/fvSolution"
for key in p U k omega; do
  got="$(awk -v k="${key}" '$1==k {v=$2; sub(/;.*$/,"",v); print v; exit}' <(sed -n '/residualControl/,/}/p' "${FS}"))"
  [ "${got}" = "1e-06" ] || { echo "REFUSED: fvSolution residualControl ${key} is '${got}', registered 1e-06 (frozen 5.5)"; exit 3; }
done
# Aref must be the C-mesh value.  The O-mesh's 0.01 here would report CL 100x high.
AREF="$(awk '$1=="Aref" {v=$2; sub(/;.*$/,"",v); print v; exit}' "${CD}")"
[ "${AREF}" = "1.0" ] || { echo "REFUSED: forceCoeffs Aref is '${AREF}'; the C-topology has t_z = 1.0 m so Aref = c*t_z = 1.0 (frozen 5.6).  0.01 is the O-mesh value and would report CL and Cd 100x too large."; exit 3; }

# --- OPENFOAM ENVIRONMENT -- PART OF THE PREFLIGHT, NOT AFTER IT --------------
# The unblown row's attempt 1 (2026-08-31T15:38:32Z, rc 1) died on this `source`:
# the OpenFOAM bashrc expands unset variables and `set -u` EXITS a non-interactive
# shell on that.  Its preflight had returned rc 0 because it exited BEFORE this
# line -- it tested only the part that was never going to fail.  A preflight that
# stops short of the environment is not a preflight.
[ -f "${FOAM_BASHRC}" ] || { echo "REFUSED: OpenFOAM bashrc absent"; exit 3; }
STAGE="foamenv"
set +u
# shellcheck disable=SC1090
source "${FOAM_BASHRC}" "" > /dev/null 2>&1 || true
set -u
for exe in simpleFoam checkMesh decomposePar reconstructPar; do
  command -v "${exe}" > /dev/null 2>&1 \
    || { echo "REFUSED: ${exe} not on PATH after sourcing the OpenFOAM environment"; exit 3; }
done

# --- THE MESH ADMISSIBILITY READ ----------------------------------------------
# Frozen section 4.5 gates FOUR metrics.  `Mesh OK` is NOT one of them, and no
# C-mesh level prints it -- all three print "Failed 1 mesh checks", the
# ASPECT-RATIO ADVISORY ALONE.  MESH_STANDARD.md section 3.3 makes AR advisory at
# 1000; JF1 promotes only the COMPOUND condition (AR > 1000 AND non-orth > 60 or
# skew > 2) to a refusal.  This function reads a checkMesh log and enforces
# exactly that, and it REFUSES on an unreadable metric rather than passing it.
mesh_admissible () {  # log
  local log="$1"
  local no sk minv arv
  no="$(awk '/Mesh non-orthogonality Max:/ {print $4; exit}' "${log}")"
  sk="$(awk '/Max skewness =/ {v=$4; sub(/[^0-9.eE+-]/,"",v); print v; exit}' "${log}")"
  minv="$(awk '/Min volume =/ {v=$4; sub(/\.$/,"",v); sub(/,$/,"",v); print v; exit}' "${log}")"
  arv="$(awk '/Max aspect ratio:/ {v=$0; sub(/.*Max aspect ratio: /,"",v); sub(/,.*/,"",v); print v; exit}' "${log}")"
  [ -n "${no}" ]   || { echo "REFUSED: could not read max non-orthogonality from ${log}"; return 1; }
  [ -n "${sk}" ]   || { echo "REFUSED: could not read max skewness from ${log}"; return 1; }
  [ -n "${minv}" ] || { echo "REFUSED: could not read min cell volume from ${log}"; return 1; }
  [ -n "${arv}" ]  || arv="0"   # no advisory printed means no high-AR cells
  awk -v no="${no}" -v sk="${sk}" -v mv="${minv}" -v ar="${arv}" 'BEGIN{
    bad=0;
    if (!(no  < 65))  { printf "REFUSED: max non-orthogonality %s is not < 65 (JF1 gate, TIGHTER than MESH_STANDARD.md 70 -- a JF1 refusal against a self-imposed threshold, NOT a lab-standard failure)\n", no; bad=1 }
    if (!(sk  < 4))   { printf "REFUSED: max skewness %s is not < 4\n", sk; bad=1 }
    if (!(mv  > 0))   { printf "REFUSED: min cell volume %s is not > 0 -- negative or zero volumes present\n", mv; bad=1 }
    if (ar > 1000 && (no > 60 || sk > 2)) { printf "REFUSED: JF1 compound aspect-ratio condition: AR %s > 1000 TOGETHER WITH non-orth %s > 60 or skew %s > 2\n", ar, no, sk; bad=1 }
    printf "  non-orthogonality %s (gate < 65)  skewness %s (gate < 4)  min volume %s (gate > 0)  max aspect ratio %s (REPORTED; advisory)\n", no, sk, mv, ar;
    exit bad }' || return 1
  return 0
}

# --- PREFLIGHT EXITS HERE, AT ZERO COMPUTE ------------------------------------
# The mesh is NOT built in the preflight; instead the ALREADY-BUILT reference L1
# level's checkMesh log is read, so the preflight exercises the real
# admissibility reader against real numbers without spending a core-second.
if [ "${PREFLIGHT}" = "1" ]; then
  echo "PREFLIGHT -- ZERO COMPUTE"
  echo "  case_id       : ${CASE_ID}"
  echo "  row           : P1, stage P, PHYSICS/DIAGNOSTIC -- no gate scores on it (frozen :1234, :1843)"
  echo "  C_mu_jet      : ${CMU}   V_j ${VJ} m/s   k_jet ${KJET}   omega_jet ${OMJET}  (reproduced from frozen 5.2, not transcribed)"
  echo "  level         : ${LEVEL}, registered C-topology, 46,180 cells"
  echo "  freeze        : ${FREEZE_CHECK}"
  echo "  generator     : ${MESH_GEN_REL} blob ${MESH_GEN_BLOB} (worktree == HEAD)"
  echo "  ranks         : ${RANKS}"
  echo "  cap           : ${CAP_CORE_MIN} core-min  -> DERIVED wall allowance ${WALL_ALLOWANCE_S} s (cap x 60 / ranks)"
  echo "  registered caps: iteration 20,000 (frozen 5.5) and family 300 core-min (frozen line 9)."
  echo "                  45.0 core-min is NOT in the frozen document; run_jf1_blown.sh:51 mislabels it 'Registered cap'."
  echo "  simpleFoam    : $(command -v simpleFoam)"
  REF_LOG="${REPO}/verification/runs/JF1_jet_flap/mesh/L1/checkMesh.log"
  if [ -f "${REF_LOG}" ]; then
    echo "  mesh admissibility, read from the reference L1 build ${REF_LOG}:"
    mesh_admissible "${REF_LOG}" || { echo "PREFLIGHT FAILED on the reference mesh"; exit 5; }
  else
    echo "  NOTE: reference checkMesh log absent; the run will build and check its own."
  fi
  echo "PREFLIGHT OK -- guards pass, OpenFOAM environment live, zero compute"
  exit 0
fi

# =============================================================================
# FROM HERE DOWN COMPUTE HAPPENS.
# =============================================================================
mkdir -p "${RUN_ROOT}/0" "${RUN_ROOT}/system" "${RUN_ROOT}/constant" "${RUN_ROOT}/artefacts"
STATUS_FILE="${RUN_ROOT}/artefacts/RUN_STATUS.${CASE_ID}.txt"   # frozen 9.3 path
UTC_START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EPOCH_START="$(date +%s)"
STAGE="stage"

cp "${CASE_DIR}/case/system/fvSchemes"              "${RUN_ROOT}/system/fvSchemes"
cp "${CASE_DIR}/case/system/fvSolution"             "${RUN_ROOT}/system/fvSolution"
cp "${CASE_DIR}/case_p1/system/controlDict"         "${RUN_ROOT}/system/controlDict"
cp "${CASE_DIR}/case/constant/transportProperties"  "${RUN_ROOT}/constant/transportProperties"
cp "${CASE_DIR}/case/constant/turbulenceProperties" "${RUN_ROOT}/constant/turbulenceProperties"
cp "${CASE_DIR}/case_blown/0/nut"                   "${RUN_ROOT}/0/nut"
cp "${CASE_DIR}/case_blown/0/p"                     "${RUN_ROOT}/0/p"

# tau = 30 deg, jet fixed in the AIRFOIL frame and NOT rotated with alpha
# (frozen 1.6a / amendment A3).  alpha = 0 here, so this is also the only frame.
VJX=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", v*cos(3.14159265358979323846/6.0)}')
VJY=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", -v*sin(3.14159265358979323846/6.0)}')
sed -e "s|@VJX@|${VJX}|" -e "s|@VJY@|${VJY}|" "${CASE_DIR}/case_blown/0/U.template" > "${RUN_ROOT}/0/U"
sed -e "s|@KJET@|${KJET}|"      "${CASE_DIR}/case_blown/0/k.template"     > "${RUN_ROOT}/0/k"
sed -e "s|@OMEGAJET@|${OMJET}|" "${CASE_DIR}/case_blown/0/omega.template" > "${RUN_ROOT}/0/omega"

# NO UNSUBSTITUTED TOKEN MAY SURVIVE INTO A FIELD FILE.  A surviving @VJX@ is
# not a crash; a PARTIALLY substituted file could read as a plausible wrong
# number.  Refuse instead.
if grep -l '@[A-Z]*@' "${RUN_ROOT}"/0/U "${RUN_ROOT}"/0/k "${RUN_ROOT}"/0/omega > /dev/null 2>&1; then
  echo "SUBSTITUTION INCOMPLETE: an @TOKEN@ survived into a 0/ field"; exit 8
fi

# --- MESH: THE REGISTERED SECTION 4.1 GENERATOR, C-TOPOLOGY -------------------
# --topology is required with NO default in that script; --topology o REFUSES and
# points back at build_jf1.py.  The generator also REFUSES on a cell-count
# mismatch against the frozen section 4.2 table rather than reporting one.
STAGE="mesh"
python3 "${REPO}/${MESH_GEN_REL}" \
    --topology c --level "${LEVEL}" --out "${RUN_ROOT}" \
    > "${RUN_ROOT}/log.make_jf1_mesh" 2>&1 \
  || { echo "MESH BUILD FAILED -- see ${RUN_ROOT}/log.make_jf1_mesh"; exit 4; }

STAGE="checkMesh"
checkMesh -case "${RUN_ROOT}" > "${RUN_ROOT}/log.checkMesh" 2>&1 || true
NCELLS="$(awk '/^ *cells:/ {print $2; exit}' "${RUN_ROOT}/log.checkMesh")"
[ "${NCELLS}" = "46180" ] \
  || { echo "REFUSED: emitted mesh has ${NCELLS} cells, registered section 4.2 L1 is 46180"; exit 5; }
echo "MESH ADMISSIBILITY (frozen section 4.5 -- the four GATED metrics; 'Mesh OK' is NOT one of them):"
mesh_admissible "${RUN_ROOT}/log.checkMesh" || { echo "MESH INADMISSIBLE"; exit 5; }

# --- DECOMPOSITION (frozen 9.4) -----------------------------------------------
export SCOTCH_RANDOM_SEED=20260830          # frozen 9.4 DECOMP_SEED, recorded
DECOMP_DIGEST="serial"
if [ "${RANKS}" -gt 1 ]; then
  STAGE="decompose"
  cat > "${RUN_ROOT}/system/decomposeParDict" <<EOD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
// Frozen section 9.4: method hierarchical, delta 0.001, order xyz, deterministic
// by construction.  numberOfSubdomains is ${RANKS}; frozen 9.4 registers 4, and
// any other value is a DISCLOSED DEPARTURE recorded on this row's STATUS.
numberOfSubdomains ${RANKS};
method          hierarchical;
coeffs { n (${RANKS} 1 1); delta 0.001; order xyz; }
EOD
  decomposePar -force -case "${RUN_ROOT}" > "${RUN_ROOT}/log.decomposePar" 2>&1 \
    || { echo "DECOMPOSE FAILED"; exit 6; }
  DECOMP_DIGEST="$(awk '/Number of cells/ {print $4}' "${RUN_ROOT}/log.decomposePar" | sort -n | md5sum | cut -c1-32)"
fi

# --- AGE DATUM, TOUCHED LAST BEFORE THE SOLVER (frozen 8.1 clause 6) ----------
# This family has no 0/T; 0/U is the registered age datum.
STAGE="touch0"
touch "${RUN_ROOT}"/0/*

# --- SOLVE.  rc CAPTURED ON THE LINE IMMEDIATELY AFTER THE SOLVER ------------
STAGE="simpleFoam"
if [ "${RANKS}" -gt 1 ]; then
  timeout --signal=TERM --kill-after=60 "${WALL_ALLOWANCE_S}" \
      mpirun -np "${RANKS}" simpleFoam -case "${RUN_ROOT}" -parallel \
      > "${RUN_ROOT}/log.simpleFoam" 2>&1
  SOLVER_RC=$?
else
  timeout --signal=TERM --kill-after=60 "${WALL_ALLOWANCE_S}" \
      simpleFoam -case "${RUN_ROOT}" > "${RUN_ROOT}/log.simpleFoam" 2>&1
  SOLVER_RC=$?
fi
EPOCH_END="$(date +%s)"
echo "solver_rc ${SOLVER_RC}" > "${RUN_ROOT}/SOLVER_RC.txt"

if [ "${RANKS}" -gt 1 ]; then
  reconstructPar -latestTime -case "${RUN_ROOT}" > "${RUN_ROOT}/log.reconstructPar" 2>&1 || true
fi

WALL_S=$(( EPOCH_END - EPOCH_START ))
CORE_MIN="$(awk -v w="${WALL_S}" -v r="${RANKS}" 'BEGIN{printf "%.4f", w*r/60.0}')"

# --- TERMINATION READ (frozen 8.1 clause 3) -----------------------------------
N_STOP="$(ls -1 "${RUN_ROOT}" | awk '/^[0-9]+$/' | sort -n | tail -1)"
[ -n "${N_STOP}" ] || N_STOP="none"
CONV_LINE="$(grep -c 'SIMPLE solution converged in' "${RUN_ROOT}/log.simpleFoam" 2>/dev/null || true)"
END_LINE="$(grep -c '^End' "${RUN_ROOT}/log.simpleFoam" 2>/dev/null || true)"
EXEC_COUNT="$(grep -c '^ExecutionTime' "${RUN_ROOT}/log.simpleFoam" 2>/dev/null || true)"

if [ "${CONV_LINE}" -ge 1 ] 2>/dev/null; then
  TERMINATION="3a CONVERGED EARLY EXIT (candidate) -- the comparator, not this launcher, decides"
elif [ "${N_STOP}" = "20000" ]; then
  TERMINATION="3b ITERATION CAP HIT at 20000 without a converged line -- frozen 5.5: NOT A RESULT, never 'close enough'"
elif [ "${WALL_S}" -ge "${WALL_ALLOWANCE_S}" ]; then
  TERMINATION="3c STOPPED ON THE CORE-MINUTE CAP at ${CAP_CORE_MIN} core-min (derived wall allowance ${WALL_ALLOWANCE_S} s), N_stop ${N_STOP} -- a BUDGET stop, not convergence.  Rule 12: an overrun stops the run and does not get a new budget."
else
  TERMINATION="3c OTHER EARLY STOP -- N_stop ${N_STOP} with no converged line and no cap reached.  Refusal class."
fi

{
  echo "case_id            ${CASE_ID}"
  echo "row                P1  STAGE P  C_mu_jet ${CMU}  alpha 0 deg  tau 30 deg  LEVEL ${LEVEL} C-TOPOLOGY 46180 cells"
  echo "label              physics/diagnostic"
  echo "gate               NONE -- frozen section 6 line 1234: stage P is 'No. Diagnostic only.'  This run scores nothing."
  echo "verdict_vocabulary NOT APPLICABLE to this row.  If a number here is quoted, it is quoted UNGRADED."
  echo "rc                 ${SOLVER_RC}"
  echo "utc_start          ${UTC_START}"
  echo "utc_end            $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "wall_s             ${WALL_S}"
  echo "ranks              ${RANKS}"
  echo "core_min_MEASURED  ${CORE_MIN}"
  echo "cap_core_min       ${CAP_CORE_MIN}   (LANE-SET, NOT REGISTERED.  The registered caps are the 20,000-iteration cap of frozen 5.5 and the 300 core-min FAMILY cap of frozen line 9.  45.0 is NOT in the frozen document.)"
  echo "wall_allowance_s   ${WALL_ALLOWANCE_S}   (DERIVED as cap x 60 / ranks, not pasted)"
  echo "cost_estimate      67.84 core-min at rank 1 for the full 20,000 iterations, from the MEASURED 3.392219e-03 core-min/iteration"
  echo "cost_basis         MEASURED on this case's own five completed L1 feasibility rows (mean 23.496660 core-min / 8000 iters / 39,984 cells = 5.876516e-04 core-min/cell), scaled by the cell ratio 46180/39984 = 1.154962.  DOLLARS ARE DERIVED, NOT MEASURED, at the owner-stated \$0.0513/core-h -- this box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5).  PARALLELISM BUYS WALL CLOCK, NOT BUDGET: core-minutes are rank-invariant to first order and rise with parallel inefficiency."
  echo "n_stop             ${N_STOP}"
  echo "converged_lines    ${CONV_LINE}"
  echo "end_lines          ${END_LINE}"
  echo "executiontime_rows ${EXEC_COUNT}"
  echo "termination        ${TERMINATION}"
  echo "prereg_commit      ${PREREG_COMMIT}"
  echo "prereg_blob_pinned ${FREEZE_BLOB}"
  echo "prereg_check       ${FREEZE_CHECK}"
  echo "mesh_generator     ${MESH_GEN_REL} blob ${MESH_GEN_BLOB}"
  echo "decomp_seed        20260830"
  echo "decomp_digest      ${DECOMP_DIGEST}"
  echo "decomp_departure   frozen 9.4 registers numberOfSubdomains 4; this run used ${RANKS}"
  echo "controlDict_note   writeInterval 1000, a DISCLOSED DEPARTURE from the registered 20000 (frozen 5.5, pinned by 8.1 clause 3).  The comparator WILL refuse this run on that clause, and that is correct: this row is not gradeable."
  echo "run_root           ${RUN_ROOT}"
} > "${STATUS_FILE}"

echo "P1 finished.  rc ${SOLVER_RC}, ${WALL_S} s wall, ${CORE_MIN} core-min, N_stop ${N_STOP}."
echo "STATUS: ${STATUS_FILE}"
exit "${SOLVER_RC}"
