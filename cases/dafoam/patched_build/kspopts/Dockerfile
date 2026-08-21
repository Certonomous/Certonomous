# dafoam-kspopts:v2 — reproducible rebuild of the KSPSetFromOptions relocation
#
# Reconstructs the hand-run build recorded in
# cases/dafoam/A3_KSPOPTS_PATCH_PREREGISTRATION.md §2 and §6, which produced
# dafoam-kspopts:v1 on 2026-08-10.
#
# LINEAGE, measured this session and NOT obvious from the file names:
#   dafoam-kspopts:v1 = dafoam-subpclu:v1 + the kspopts patch.
# `diff` of the two images' DALinearEqn.C returns exactly the two kspopts hunks and
# nothing else, and kspopts:v1 carries 3 DAFOAM_SUBPC_TYPE occurrences (the v1 sub-LU
# block). The prereg says so in its own words: "Base: dafoam-subpclu:v1 -- the image the
# A3 evidence chain actually ran on -- so the regression comparison is against the exact
# baseline, not a different lineage."
# This Dockerfile therefore builds FROM dafoam-subpclu:v2, preserving that lineage.
#
# The patch relocates KSPSetFromOptions(ksp) from the top of createMLRKSP to the end, so
# daOptions act as DEFAULTS and PETSc runtime options act as OVERRIDES. Measured
# behaviour-neutral with no options set (ONERA M6 21,840 cells: CD 368 / CL 383
# iterations, PetscConvergedReason 2, bit-identical to the unpatched image).
#
# NOTE on applying it: this patch's headers carry ABSOLUTE paths
# (--- /tmp/DALinearEqn.C.orig, +++ /home/dafoamuser/...), so `git apply` and `patch -p1`
# both fail on it. It is applied with an explicit target file, which makes patch ignore
# the header names. Recorded here rather than silently worked around.

FROM dafoam-subpclu:v2

USER root

ARG SRC=/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DALinearEqn/DALinearEqn.C

COPY DALinearEqn_kspopts.patch /tmp/DALinearEqn_kspopts.patch

RUN set -eux; \
    echo "BASE (subpclu:v2) md5:"; md5sum "$SRC"; \
    echo "BASE lines:"; wc -l < "$SRC"; \
    cp "$SRC" /tmp/DALinearEqn.C.base; \
    patch --batch --forward "$SRC" < /tmp/DALinearEqn_kspopts.patch; \
    echo "PATCHED md5:"; md5sum "$SRC"; \
    echo "PATCHED lines:"; wc -l < "$SRC"; \
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

RUN set -eux; diff -u /tmp/DALinearEqn.C.base "$SRC" || true; md5sum "$SRC"

USER dafoamuser
WORKDIR /home/dafoamuser
