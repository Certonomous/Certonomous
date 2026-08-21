# dafoam-team:v1 — Ladder B's pinned image: stock + the sub-PC patch + the kspopts patch.
#
# WHY ONE IMAGE. Ladder B's numbers currently come from three tags whose lineage is only
# recoverable by reading TOOLCHAIN_INVENTORY.md §6e:
#   dafoam-subpclu:v1  = opt-packages + subpclu, built by a hand-run `docker commit`
#                        in a session whose scratch tree no longer exists
#   dafoam-subpclu:v2  = opt-packages + subpclu, reproducible (patched_build/subpclu/)
#   dafoam-kspopts:v1  = dafoam-subpclu:v1 + kspopts, also hand-built
# This Dockerfile builds the union FROM the stock image in one layer stack, so the team
# image's provenance is this file plus the two committed .patch files and nothing else.
#
# BOTH LEVERS ARE OFF BY DEFAULT. With DAFOAM_SUBPC_TYPE unset and no PETSC_OPTIONS set,
# this image must reproduce the stock `-9` at iteration 0 with residual 7.091590452305e-04
# to all 13 digits. That is gate G4 in BUILD.md and it is the whole safety argument.
#
# ORDER MATTERS. subpclu is applied first, then kspopts, which is the lineage every
# recorded kspopts number was measured on (kspopts:v1 = subpclu:v1 + kspopts).
#
# TRAP, recorded rather than silently worked around: the kspopts patch's headers carry
# ABSOLUTE paths (--- /tmp/DALinearEqn.C.orig, +++ /home/dafoamuser/...), so `git apply`
# and `patch -p1` both fail on it. It is applied with an explicit target file.
#
# TRAP 2: `set -e` before sourcing the OpenFOAM environment kills the shell — source first.
# (W4_ADJOINT_PC_UNBLOCK.md §4, a lost first attempt.)

FROM dafoam/opt-packages:latest

USER root

ARG SRC=/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DALinearEqn/DALinearEqn.C

COPY DALinearEqn_subpclu.patch /tmp/subpclu.patch
COPY DALinearEqn_kspopts.patch /tmp/kspopts.patch

RUN set -eux; \
    echo "STOCK md5:"; md5sum "$SRC"; \
    echo "STOCK lines:"; wc -l < "$SRC"; \
    cp "$SRC" /tmp/DALinearEqn.C.stock; \
    patch --batch --forward "$SRC" < /tmp/subpclu.patch; \
    echo "AFTER subpclu lines:"; wc -l < "$SRC"; \
    patch --batch --forward "$SRC" < /tmp/kspopts.patch; \
    echo "AFTER kspopts md5:"; md5sum "$SRC"; \
    echo "AFTER kspopts lines:"; wc -l < "$SRC"; \
    echo "DAFOAM_SUBPC_TYPE occurrences:"; grep -c 'DAFOAM_SUBPC_TYPE' "$SRC"; \
    echo "KSPSetFromOptions sites:"; grep -n 'KSPSetFromOptions' "$SRC"

RUN bash -c 'source /home/dafoamuser/dafoam/loadDAFoam.sh; \
    set -u; cd /home/dafoamuser/dafoam/repos/dafoam; \
    wmakeLnInclude src/adjoint; cd src/adjoint; wmake -j 4 2>&1 | tail -10; \
    ls -la /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolver.so'

RUN bash -c 'source /home/dafoamuser/dafoam/loadDAFoam.sh; \
    sed -i "s/^export WM_AD_MODE=.*/export WM_AD_MODE=ADR/" /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; \
    source /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; set -u; \
    echo "WM_OPTIONS=$WM_OPTIONS"; cd /home/dafoamuser/dafoam/repos/dafoam; \
    wmakeLnInclude src/adjoint; cd src/adjoint; wmake -j 4 2>&1 | tail -10; \
    ls -la /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADR.so'

RUN bash -c 'source /home/dafoamuser/dafoam/loadDAFoam.sh; \
    sed -i "s/^export WM_AD_MODE=.*/export WM_AD_MODE=ADF/" /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; \
    source /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-AD/etc/bashrc; set -u; \
    echo "WM_OPTIONS=$WM_OPTIONS"; cd /home/dafoamuser/dafoam/repos/dafoam; \
    wmakeLnInclude src/adjoint; cd src/adjoint; wmake -j 4 2>&1 | tail -10; \
    ls -la /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so'

RUN set -eux; diff -u /tmp/DALinearEqn.C.stock "$SRC" | head -80 || true; md5sum "$SRC"; \
    strings /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolver.so | grep -c 'DAFOAM_SUBPC_TYPE'

USER dafoamuser
WORKDIR /home/dafoamuser
