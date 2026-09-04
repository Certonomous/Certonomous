#!/bin/bash
# ---------------------------------------------------------------------------
# VMFL072-R2 -- apply a registered level to a case copied from base/.
#
# CALLED BY THE FROZEN DRIVER:
#     apply_level.sh <DIR> <LEVEL>       LEVEL in L1 L2 L3 B2 C1
# It runs AFTER `cp -r base/. DIR` and AFTER `cp -r DIR/0.orig DIR/0`, and
# BEFORE blockMesh, makeFaMesh and the 0/U age-guard touch. Both DIR/0.orig and
# DIR/0 exist here and BOTH are substituted, so the two copies cannot disagree.
#
# EVERY VALUE BELOW IS READ OUT OF VMFL072-R2/PREREGISTRATION.md. Nothing here
# is a choice this script is entitled to make.
#
#   Mesh (R2 6.6). Refinement is in the FILM plane only, ratio r = 2:
#     L1   64 x 16 x 1 =   1024 cells   dx = 7.812500 mm   1024 fa-faces
#     L2  128 x 32 x 1 =   4096 cells   dx = 3.906250 mm   4096 fa-faces
#     L3  256 x 64 x 1 =  16384 cells   dx = 1.953125 mm  16384 fa-faces
#     B2  L3 geometry (R2 6.5 -- the bracket is at the GRADED level)
#     C1  L2 geometry (R2 6.4)
#
#   NZ = 1 AT EVERY LEVEL, AND IT IS A MEASUREMENT, NOT AN ASSUMPTION (R2 3.6).
#   The primary region's z-resolution enters the film NOWHERE: with the
#   registered `Cf 0`, filmTurbulenceModel.C:252 gives
#   primaryRegionFriction = -fam::Sp(Cf,U) + Cf*Up, identically zero, and the
#   gas Courant number is MEASURED at exactly 0 so pg()'s mapped primary
#   pressure is uniform and contributes no gradient. Verified by running L1 for
#   100 steps at NZ = 1 and at NZ = 8: hf_film is BIT-IDENTICAL on all 1024
#   faces, on a field whose range is 5.633e-04 m, and the same reader DOES see
#   a planted +1.234e-09 m in one face. See R2 3.6 for the control.
#
#   Inlet state. delta_N* = 5.500814601e-04 m is the EXACT DISCRETE STATE
#   (R2 2.7): it solves h^2(h+h0) = 3*nu*q/gs with the solver's own
#   h0 = 1e-7 m, and is -0.006059 % from the h0-free Nusselt delta_N. Gamma is
#   IDENTICAL at every level -- rho*h_in*U_in = 0.381000000 kg/m/s exactly,
#   which is what R2 6.5's bracket requires:
#     L1 L2 L3  h_in = 1.30 dN*  = 7.1510589810e-04   U_in = 0.534177082
#     B2        h_in = 0.70 dN*  = 3.8505702205e-04   U_in = 0.992043153
#     C1        h_in = 1.00 dN*  = 5.5008146008e-04   U_in = 0.694430207
#
#   Time step (R2 8.1). Fixed, never adjustTimeStep: OpenFOAM computes the
#   Courant number on the quiescent PRIMARY region (measured Co = 0), so
#   adjustTimeStep would chase maxDeltaT. Each step is the largest value at or
#   below the film maxCo-0.5 step that divides the 0.05 s write interval an
#   integer number of times, giving EXACTLY 200 written directories and
#   endTime 10.0 hit exactly. B2 carries the smaller step because its inlet
#   velocity is 0.992 m/s, not 0.694 m/s.
#     L1 dt 5.00e-03 WI 10  2000 steps  Co_film 0.4444
#     L2 dt 2.50e-03 WI 20  4000 steps  Co_film 0.4444
#     L3 dt 1.25e-03 WI 40  8000 steps  Co_film 0.4444
#     B2 dt 7.8125e-04 WI 64 12800 steps Co_film 0.3968
#     C1 dt 2.50e-03 WI 20  4000 steps  Co_film 0.4444
#
# FAILS LOUDLY. set -euo pipefail; an unknown level exits 3; a token absent
# before substitution, or still present after it, exits 4; a leftover @...@
# anywhere in the case exits 5. It cannot succeed quietly on a substitution
# that did not apply.
# ---------------------------------------------------------------------------
set -euo pipefail

DIR="${1:?usage: apply_level.sh <DIR> <L1|L2|L3|B2|C1>}"
LEVEL="${2:?usage: apply_level.sh <DIR> <L1|L2|L3|B2|C1>}"

if [ ! -d "${DIR}" ]; then
  echo "apply_level: case directory does not exist: ${DIR}" >&2
  exit 3
fi

# --- the registered level table -------------------------------------------
case "${LEVEL}" in
  L1) NX=64;  NY=16; NZ=1; H_IN=7.1510589810e-04; U_IN=0.534177082; DT=5.0e-03;    WI=10 ;;
  L2) NX=128; NY=32; NZ=1; H_IN=7.1510589810e-04; U_IN=0.534177082; DT=2.5e-03;    WI=20 ;;
  L3) NX=256; NY=64; NZ=1; H_IN=7.1510589810e-04; U_IN=0.534177082; DT=1.25e-03;   WI=40 ;;
  B2) NX=256; NY=64; NZ=1; H_IN=3.8505702205e-04; U_IN=0.992043153; DT=7.8125e-04; WI=64 ;;
  C1) NX=128; NY=32; NZ=1; H_IN=5.5008146008e-04; U_IN=0.694430207; DT=2.5e-03;    WI=20 ;;
  *)
    echo "apply_level: UNKNOWN LEVEL '${LEVEL}'." >&2
    echo "  The registered levels are L1 L2 L3 (6.6), B2 (6.5) and C1 (6.4)." >&2
    echo "  Nothing has been modified." >&2
    exit 3
    ;;
esac

# --- substitution with a before-and-after assertion ------------------------
# A sed that matches nothing exits 0. That is precisely the silent success this
# case must not have, so each substitution is bracketed by two checks.
subst()
{
    local file="$1" token="$2" value="$3"

    if [ ! -f "${file}" ]; then
        echo "apply_level: expected file missing: ${file}" >&2
        exit 4
    fi
    if ! grep -q -- "${token}" "${file}"; then
        echo "apply_level: token ${token} NOT PRESENT in ${file}" >&2
        echo "  base/ and apply_level.sh have drifted apart; refusing to" >&2
        echo "  leave a case that looks configured and is not." >&2
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
done

# --- no leftover token anywhere -------------------------------------------
if grep -rqE '@[A-Z_]+@' "${DIR}" 2>/dev/null; then
    echo "apply_level: LEFTOVER @TOKEN@ in ${DIR}:" >&2
    grep -rnE '@[A-Z_]+@' "${DIR}" >&2 || true
    exit 5
fi

# --- record what was applied, for the run record --------------------------
cat > "${DIR}/LEVEL_APPLIED.txt" <<EOF
LEVEL      ${LEVEL}
NX NY NZ   ${NX} ${NY} ${NZ}
fa-faces   $(( NX * NY ))
H_IN       ${H_IN}
U_IN       ${U_IN}
DELTAT     ${DT}
WRITEINT   ${WI}
applied    $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

echo "apply_level: ${LEVEL} applied to ${DIR} (${NX}x${NY}x${NZ}, dt=${DT}, WI=${WI})"
