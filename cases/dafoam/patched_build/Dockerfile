# ---------------------------------------------------------------------------
# dafoam-idwarp-rot:v1
#
# The IDWarp getRotationMatrix3d degenerate-branch fix, delivered as a container
# layer instead of a bind-mount + PYTHONPATH incantation.
#
# WHY THIS IMAGE EXISTS. Every "patched toolchain" number this lab has published
# was produced by mounting a host-side scratch clone into the stock image and
# prepending it to PYTHONPATH. That works, but it makes the patched stack a
# property of the *command line* rather than of an artifact: a run that forgot
# the -v or the export silently produced stock numbers under a patched label,
# and the only tell was the IDWARP_IMPORTED_FROM line each script had to
# remember to print. This image makes the patched stack an artifact with a
# digest.
#
# WHAT IS PATCHED. Two Tapenade-generated files inside IDWarp 2.6.2:
#   src/adjoint/outputReverse/vectorUtils_b.f90
#   src/adjoint/outputForward/vectorUtils_d.f90
# supplying the analytic limit the sqrt(eps) guard at src/utils/vectorUtils.f90:58
# discards:  v2b += (axial(mib - mib^T) x v1) / (|v1| |v2|)
# The PRIMAL is untouched; warpMesh output is md5-identical patched vs unpatched.
# Derivation and acceptance tests: cases/dafoam/PATCH_getRotationMatrix3d.md
# Root cause:                      cases/dafoam/ROOTCAUSE_getRotationMatrix3d.md
#
# IDENTITY. `idwarp.__version__` reads 2.6.2 in BOTH the stock and the patched
# stack, and every .py file in the package is byte-identical between them (same
# sizes: 2558 / 36443 / 1035 / 42475 / 1024 / 265). libidwarp.so is even the
# SAME SIZE in both, 491344 bytes. **The md5 of libidwarp.so is the only thing
# that distinguishes a patched run from a stock one.** Any verification that
# checks the version string is checking nothing.
#     stock   libidwarp.so  md5 f0fcb488e0e98156575cd19548e91663
#     patched libidwarp.so  md5 85f59e87253e0a71a813f64ca6e4c425
#
# PROVENANCE OF THE COPIED PACKAGE
#   source clone : /home/ubuntu/certonomous-runs/W5-patch/idwarp
#   upstream repo: https://github.com/mdolab/idwarp  tag v2.6.2
#   git HEAD     : 647fd8fc2c06fc61b31cc07a7b63ffd4fbaf65ce  ("version update (#102)")
#   working tree : exactly 2 modified files, both listed above
#   patch file   : cases/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch
#   patch md5    : 5d5afd856760c19f03e8c363f0c3ac3d
#   .so built    : 2026-08-01 00:04 UTC, after the .f90 edits of 2026-07-31 23:59
#
# BUILD CONTEXT is the clone itself, so no binary enters the git repo:
#   sudo -n docker build -f cases/dafoam/patched_build/Dockerfile \
#        -t dafoam-idwarp-rot:v1 /home/ubuntu/certonomous-runs/W5-patch/idwarp
#
# NOT FILED ANYWHERE. This is a local proof-of-concept hand-edit of generated
# code; upstream should fix the primal's parameterisation and regenerate.
# ---------------------------------------------------------------------------
FROM dafoam/opt-packages:latest

# The patched Python package, copied whole. __pycache__ is excluded on purpose:
# it carries absolute paths from the host build and would shadow the real files.
COPY --chown=root:root idwarp/__init__.py                 /opt/idwarp_patched/idwarp/
COPY --chown=root:root idwarp/MExt.py                     /opt/idwarp_patched/idwarp/
COPY --chown=root:root idwarp/MultiUnstructuredMesh.py    /opt/idwarp_patched/idwarp/
COPY --chown=root:root idwarp/MultiUnstructuredMesh_C.py  /opt/idwarp_patched/idwarp/
COPY --chown=root:root idwarp/UnstructuredMesh.py         /opt/idwarp_patched/idwarp/
COPY --chown=root:root idwarp/UnstructuredMesh_C.py       /opt/idwarp_patched/idwarp/
COPY --chown=root:root idwarp/libidwarp.so                /opt/idwarp_patched/idwarp/

# Two independent hooks, deliberately: ENV covers a bare `docker run ... python`,
# and the loadDAFoam.sh append covers anything that sources the environment the
# lab's run scripts all source. loadDAFoam.sh never touches PYTHONPATH itself
# (verified in-image), so appending cannot clobber anything.
ENV PYTHONPATH=/opt/idwarp_patched
RUN printf '\n# dafoam-idwarp-rot:v1 -- patched IDWarp ahead of site-packages\nexport PYTHONPATH=/opt/idwarp_patched:$PYTHONPATH\n' \
      >> /home/dafoamuser/dafoam/loadDAFoam.sh

LABEL org.certonomous.image="dafoam-idwarp-rot:v1"
LABEL org.certonomous.base="dafoam/opt-packages:latest"
LABEL org.certonomous.base.digest="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
LABEL org.certonomous.patch="idwarp_v2.6.2_degenerate_branch_fix.patch"
LABEL org.certonomous.patch.md5="5d5afd856760c19f03e8c363f0c3ac3d"
LABEL org.certonomous.idwarp.git_head="647fd8fc2c06fc61b31cc07a7b63ffd4fbaf65ce"
LABEL org.certonomous.idwarp.so.md5.patched="85f59e87253e0a71a813f64ca6e4c425"
LABEL org.certonomous.idwarp.so.md5.stock="f0fcb488e0e98156575cd19548e91663"
LABEL org.certonomous.filed_upstream="no"
