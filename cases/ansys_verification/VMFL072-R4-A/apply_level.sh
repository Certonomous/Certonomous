#!/bin/bash
# ---------------------------------------------------------------------------
# VMFL072-R4-A -- apply a registered rung to a case copied from base/.
#
# DRAFT, NOT FROZEN. Becomes frozen only when committed with the R4-A
# PREREGISTRATION.md and comparator (CLAUDE.md rule 2). Adapted from
# VMFL072-R3/apply_level.sh; the ONE structural change is the single R4-A knob:
# the precursor film thickness H0 (and DELTAWET == H0), tokenized into
# base/0.orig/U as @H0@ / @DELTAWET@. Everything else -- grid, H_IN, U_IN,
# DELTAT, WI -- is PINNED to R3's L3 values at every rung, so exactly one knob
# moves (PREREGISTRATION.md 2, 3).
#
#     apply_level.sh <DIR> <RUNG>        RUNG in A1 A2 A3
#
# EVERY VALUE BELOW IS READ OUT OF VMFL072-R4-A/PREREGISTRATION.md.
#
#   Fixed at L3 (PREREGISTRATION.md 2): 256 x 64 x 1, H_IN 7.1084204656e-04,
#   U_IN 0.537381243, DELTAT 1.25e-03, WI 40 -> 200 written dirs, 8000 steps,
#   endTime 10.0 hit exactly.
#
#   The ONE knob (PREREGISTRATION.md 3), answer-blind, in the sub-octave viable
#   window bounded below by the known-crash 1e-5 and above by the frozen band
#   ceiling 2.09e-5:
#     A1  H0 = 5.0e-06   dN* = 5.484531695601e-04   crash-side control
#     A2  H0 = 1.5e-05   dN* = 5.451599666898e-04   interior of the window
#     A3  H0 = 2.0e-05   dN* = 5.435282688980e-04   just under the ceiling
#   DELTAWET == H0 (not an independent variable).
#
# FAILS LOUDLY. set -euo pipefail; unknown rung exits 3; a token absent before
# or still present after substitution exits 4; any leftover @...@ exits 5.
# ---------------------------------------------------------------------------
set -euo pipefail

DIR="${1:?usage: apply_level.sh <DIR> <A1|A2|A3>}"
RUNG="${2:?usage: apply_level.sh <DIR> <A1|A2|A3>}"

if [ ! -d "${DIR}" ]; then
  echo "apply_level: case directory does not exist: ${DIR}" >&2
  exit 3
fi

# --- pinned at L3 for every rung ------------------------------------------
NX=256; NY=64; NZ=1
H_IN=7.1084204656e-04
U_IN=0.537381243
DT=1.25e-03
WI=40

# --- the single registered knob -------------------------------------------
case "${RUNG}" in
  A1) H0=5.0e-06 ;;
  A2) H0=1.5e-05 ;;
  A3) H0=2.0e-05 ;;
  *)
    echo "apply_level: UNKNOWN RUNG '${RUNG}'." >&2
    echo "  The registered rungs are A1 A2 A3 (PREREGISTRATION.md 3)." >&2
    echo "  Nothing has been modified." >&2
    exit 3
    ;;
esac
DELTAWET="${H0}"   # deltaWet == h0 (PREREGISTRATION.md 2)

subst()
{
    local file="$1" token="$2" value="$3"
    if [ ! -f "${file}" ]; then
        echo "apply_level: expected file missing: ${file}" >&2; exit 4
    fi
    if ! grep -q -- "${token}" "${file}"; then
        echo "apply_level: token ${token} NOT PRESENT in ${file}" >&2
        echo "  base/ and apply_level.sh have drifted apart; refusing." >&2
        exit 4
    fi
    sed -i "s|${token}|${value}|g" "${file}"
    if grep -q -- "${token}" "${file}"; then
        echo "apply_level: token ${token} STILL PRESENT in ${file} after sed" >&2
        exit 4
    fi
}

subst "${DIR}/system/blockMeshDict" "@NX@" "${NX}"
subst "${DIR}/system/blockMeshDict" "@NY@" "${NY}"
subst "${DIR}/system/blockMeshDict" "@NZ@" "${NZ}"

subst "${DIR}/system/controlDict"   "@DELTAT@"        "${DT}"
subst "${DIR}/system/controlDict"   "@WRITEINTERVAL@" "${WI}"

for stage in 0.orig 0; do
    subst "${DIR}/${stage}/finite-area/hf_film" "@H_IN@" "${H_IN}"
    subst "${DIR}/${stage}/finite-area/Uf_film" "@U_IN@" "${U_IN}"
    subst "${DIR}/${stage}/U"                   "@H0@"       "${H0}"
    subst "${DIR}/${stage}/U"                   "@DELTAWET@" "${DELTAWET}"
done

if grep -rqE '@[A-Z_]+@' "${DIR}" 2>/dev/null; then
    echo "apply_level: LEFTOVER @TOKEN@ in ${DIR}:" >&2
    grep -rnE '@[A-Z_]+@' "${DIR}" >&2 || true
    exit 5
fi

cat > "${DIR}/LEVEL_APPLIED.txt" <<EOF
RUNG       ${RUNG}
NX NY NZ   ${NX} ${NY} ${NZ}
fa-faces   $(( NX * NY ))
H_IN       ${H_IN}
U_IN       ${U_IN}
DELTAT     ${DT}
WRITEINT   ${WI}
H0         ${H0}
DELTAWET   ${DELTAWET}
applied    $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

echo "apply_level: ${RUNG} applied to ${DIR} (256x64x1, dt=${DT}, WI=${WI}, H0=${H0})"
