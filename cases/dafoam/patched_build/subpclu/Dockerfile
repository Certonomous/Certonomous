# dafoam-subpclu:v2 — reproducible rebuild of the sub-LU adjoint unblock
#
# Reconstructs, as a Dockerfile, the hand-run `docker commit` recipe recorded in
# cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md §4 that produced dafoam-subpclu:v1
# on 2026-08-04. See BUILD.md in this directory for the cost estimate made before
# the build, the actual command output, and the verification gates.
#
# The patch adds an env-var switch at the hard-coded `PCType localPCType = PCILU;`
# (DALinearEqn.C:266): DAFOAM_SUBPC_TYPE=lu -> PCLU on the ASM sub-blocks.
# OFF BY DEFAULT. With the variable unset, not one numeric path changes.
#
# EXPECTED, PRE-REGISTERED DIVERGENCE FROM v1: the patch file on disk is ONE HUNK
# AHEAD of the built v1 image, by its own provenance header ("NEXT-REBUILD DELTA
# (finding B-1)"). v2 therefore CANNOT have v1's DALinearEqn.C md5. See BUILD.md
# gate G2 for the substitute verification.

FROM dafoam/opt-packages:latest

USER root

ARG DAFOAM_REPO=/home/dafoamuser/dafoam/repos/dafoam
ARG SRC=/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DALinearEqn/DALinearEqn.C

COPY DALinearEqn_subpclu.patch /tmp/DALinearEqn_subpclu.patch

# 1. Record the stock state, apply the patch, and prove it applied.
#    `patch -p1` from the repo root, per the patch file's own header.
RUN set -eux; \
    cd "$DAFOAM_REPO"; \
    echo "STOCK md5:"; md5sum "$SRC"; \
    echo "STOCK lines:"; wc -l < "$SRC"; \
    cp "$SRC" /tmp/DALinearEqn.C.stock; \
    patch -p1 --batch --forward < /tmp/DALinearEqn_subpclu.patch; \
    echo "PATCHED md5:"; md5sum "$SRC"; \
    echo "PATCHED lines:"; wc -l < "$SRC"; \
    echo "DAFOAM_SUBPC_TYPE occurrences:"; grep -c DAFOAM_SUBPC_TYPE "$SRC"; \
    grep -q 'localPCType = PCLU' "$SRC"

# 2. Rebuild libDASolver.so — the ORIGINAL (real, non-AD) mode.
#    `source` FIRST, then `set -u`: W4 §4 records that `set -e` before sourcing the
#    OpenFOAM environment kills the shell (a lost first attempt).
RUN bash -c 'source /home/dafoamuser/dafoam/loadDAFoam.sh; \
    set -u; \
    cd /home/dafoamuser/dafoam/repos/dafoam; \
    wmakeLnInclude src/adjoint; \
    cd src/adjoint; \
    wmake -j 4 2>&1 | tail -20; \
    ls -la /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolver.so'

# 3. Rebuild libDASolverADR.so — reverse-mode AD (the library the matrix-free
#    transpose-Jacobian product path uses).
RUN bash -c 'source /home/dafoamuser/dafoam/loadDAFoam.sh; \
    sed -i "s/^export WM_AD_MODE=.*/export WM_AD_MODE=ADR/" /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; \
    source /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; \
    set -u; \
    echo "WM_AD_MODE=$WM_AD_MODE WM_OPTIONS=$WM_OPTIONS"; \
    cd /home/dafoamuser/dafoam/repos/dafoam; \
    wmakeLnInclude src/adjoint; \
    cd src/adjoint; \
    wmake -j 4 2>&1 | tail -20; \
    ls -la /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADR.so'

# 4. Rebuild libDASolverADF.so — forward-mode AD. Restores the bashrc to its
#    shipped ADF default as a side effect, so the image's etc/bashrc matches stock.
RUN bash -c 'source /home/dafoamuser/dafoam/loadDAFoam.sh; \
    sed -i "s/^export WM_AD_MODE=.*/export WM_AD_MODE=ADF/" /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; \
    source /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; \
    set -u; \
    echo "WM_AD_MODE=$WM_AD_MODE WM_OPTIONS=$WM_OPTIONS"; \
    cd /home/dafoamuser/dafoam/repos/dafoam; \
    wmakeLnInclude src/adjoint; \
    cd src/adjoint; \
    wmake -j 4 2>&1 | tail -20; \
    ls -la /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so'

# 5. In-image self-check: all three libraries carry the switch string, and the
#    stock->patched diff is exactly the two blocks the patch adds.
RUN set -eux; \
    for L in libDASolver.so libDASolverADR.so libDASolverADF.so; do \
      echo -n "$L DAFOAM_SUBPC_TYPE: "; \
      strings "/home/dafoamuser/dafoam/OpenFOAM/sharedLibs/$L" | grep -c DAFOAM_SUBPC_TYPE || true; \
    done; \
    diff -u /tmp/DALinearEqn.C.stock "$SRC" | head -60 || true; \
    md5sum "$SRC" /tmp/DALinearEqn.C.stock

USER dafoamuser
WORKDIR /home/dafoamuser
