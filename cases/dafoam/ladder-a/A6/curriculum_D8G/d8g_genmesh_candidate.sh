#!/usr/bin/env bash
# =============================================================================
# PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.
# **THIS SCRIPT HAS NEVER BEEN EXECUTED.**  The lane that wrote it ran ZERO
# solver compute and ZERO mesh generation by instruction.  Every number it
# asserts below was measured by the DRAFTING lane's pre-compute probe
# (PREREGISTRATION.md section 9.4) or read from the archive; NONE of it was
# produced by this file.  Its assertions are therefore PREDICTIONS (section 8,
# P1/P2), and a failure to reproduce them under this script is a DEFECT TO
# REPORT, not a number to adjust.
#
# Curriculum D8G MESH GENERATOR -- the three registered levels of
# PREREGISTRATION.md section 2.2, built from the PRISTINE c0 surface.
#
#   level   surface   pyHyp N   layers   s0        cells      quads   points
#   L1      c3            9        8     4.0e-4     5,568       696      996
#   L2      c2           17       16     2.0e-4    44,544     2,784    3,358
#   L3      c1           33       32     1.0e-4   356,352    11,136   12,258
#
# r = 2.000 EXACTLY in all three directions; both cell ratios are the exact
# integer 8 (= r^3).  c4 is EXCLUDED from the family and the reason is
# registered: its surface ratio is 3.702, not 4, because several blocks of this
# 26-block surface reach a 2-node dimension that cannot be coarsened again -- a
# level at c4 would not be a factor-2 coarsening of c3 and must never be used as
# one.  It also degrades the trailing edge (section 4.4).
#
# ===========================================================================
# THE SOURCE IS THE TARBALL, AND THE FILE BESIDE IT IS A TRAP.
#
#   USE     /home/ubuntu/certonomous-runs/A6-crm-wing/CRM_surfMesh.cgns.tar.gz
#           1,015,901 bytes, md5 0635beaae7d9117eb0d27bceaeb69066 -- the
#           PRISTINE c0 surface as shipped, 44,544 quad faces.
#
#   NEVER   /home/ubuntu/certonomous-runs/A6-crm-wing/surfMesh.cgns
#           552,960 bytes.  `cgns_utils coarsen` WRITES IN PLACE, and the
#           archived preProcessing.sh ran it once, so that file IS ALREADY c1.
#           Building "c1/c2/c3" from it would silently produce c2/c3/c4 -- a
#           family whose finest level is the registered medium one and whose
#           coarsest is the level this registration EXCLUDES.
#
# THE GUARD IS NOT A COMMENT.  After extraction the c0 quad-face count is
# ASSERTED == 44,544.  The trap file would read 11,136 and the script would
# refuse before any mesh was built.  That assertion is the discriminator; the
# md5 check above it only proves the bytes are the ones that were measured.
# ===========================================================================
#
# THE IMAGE IS PINNED BY DIGEST, NEVER BY TAG (DAFOAM_CHARTER.md section 11).
# `cgns_utils`, `pyhyp` and the OpenFOAM-v2506 `checkMesh` were all verified
# present in BOTH registered images on 2026-09-10, so the family is generatable
# inside the graded toolchain and not only on the host.  THE MESH IS GENERATED
# ONCE PER LEVEL, IN THE PATCHED IMAGE, AND STAGED TO BOTH ROWS: a grid family
# whose two rows ran different meshes is not a grid family, and the primal at a
# fixed baseline design cannot depend on the reverse-mode warp patch anyway
# (section 8, P5).
#
# OUTPUT, per level, into the item's own run root:
#   $ROOT/base_<LEVEL>/            0/ constant/polyMesh/ system/ FFD/  (staged cold)
#   $ROOT/mesh_record_<LEVEL>.json THE CONSTRUCTION EVIDENCE d8g_grade.py reads
#                                  for G-MESH / G-MESH-STRICT / G-SYS / G-BODY /
#                                  G-TE, and the points_md5 d8g_run_arm.sh
#                                  asserts the staged mesh against.
#   $ROOT/mesh_logs_<LEVEL>/       BOTH checkMesh logs, retained.  `Mesh OK.`
#                                  from plain checkMesh is NOT sufficient
#                                  evidence of mesh health anywhere in this
#                                  team's tree (section 4.1 clause 4).
# =============================================================================
set -uo pipefail

ROOT="${ROOT:-/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple}"
ARCHIVE=/home/ubuntu/certonomous-runs/A6-crm-wing
SRC_TGZ="$ARCHIVE/CRM_surfMesh.cgns.tar.gz"
SRC_MD5=0635beaae7d9117eb0d27bceaeb69066
SRC_BYTES=1015901
TRAP_C1="$ARCHIVE/surfMesh.cgns"                 # named ONLY so the refusal can name it
C0_QUADS=44544                                    # the discriminating assertion

# THE IMAGE, BY DIGEST.  A tag is not an identity.
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_REF="dafoam-idwarp-rot@$IMG_PATCHED_DIGEST"
IMG_TAG=dafoam-idwarp-rot:v1

# The dicts and fields the recipe needs, with the md5s this lane read from the
# archive on 2026-09-11.  MEASURED THE SAME DAY, AND WORTH STATING: the archive's
# system/ is BYTE-IDENTICAL to the D8R producer's base/system/ on all five dicts
# (controlDict, fvSchemes, fvSolution, createPatchDict, decomposeParDict), and
# FFD/wingFFD.xyz is byte-identical too.  There is therefore NO CHOICE to make
# between "the archive's dicts" and "the graded producer's dicts": they are the
# same bytes.  decomposeParDict already carries numberOfSubdomains 4, scotch.
DICT_MD5="527a589ea4e074a711316d6e1ef2239a  @A@/system/controlDict
bfe390aeb22f4e9d48eb23e2827ab3ab  @A@/system/fvSchemes
36a8ad5cf2edd672b8aa752829647dfd  @A@/system/fvSolution
5ef8b5ece78a1305cc9c5e2f85288924  @A@/system/createPatchDict
1dbd9ead3f40a29f483444dc5fa1288b  @A@/system/decomposeParDict
905ade2c1120aee7e6517432cd8abbaf  @A@/FFD/wingFFD.xyz
8f10013191a33d5dd757affb8caa3cb8  @A@/0.orig/T
d298286a05f0b031f2a571211a79ef83  @A@/0.orig/U
d381ad50711abb780643b5544cc1ef0c  @A@/0.orig/alphat
55ef53cbfe7ee5cec731e4d090a74292  @A@/0.orig/nuTilda
16be134ba7458c5e43a1fd9207856fa0  @A@/0.orig/nut
96fabd08064482aa037599de4cfd8b64  @A@/0.orig/p"
N_DICTS=12

# ---- THE REGISTERED LEVEL TABLE (section 2.2).  Nothing here is a parameter. --
coarsen_of() { case "$1" in L1) echo 3 ;; L2) echo 2 ;; L3) echo 1 ;; *) echo "" ;; esac; }
pyhyp_N_of()  { case "$1" in L1) echo 9 ;; L2) echo 17 ;; L3) echo 33 ;; *) echo "" ;; esac; }
s0_of()       { case "$1" in L1) echo 4.0e-4 ;; L2) echo 2.0e-4 ;; L3) echo 1.0e-4 ;; *) echo "" ;; esac; }
cells_of()    { case "$1" in L1) echo 5568 ;; L2) echo 44544 ;; L3) echo 356352 ;; *) echo "" ;; esac; }
quads_of()    { case "$1" in L1) echo 696 ;; L2) echo 2784 ;; L3) echo 11136 ;; *) echo "" ;; esac; }
points_of()   { case "$1" in L1) echo 996 ;; L2) echo 3358 ;; L3) echo 12258 ;; *) echo "" ;; esac; }
finer_of()    { case "$1" in L1) echo L2 ;; L2) echo L3 ;; L3) echo "" ;; *) echo "" ;; esac; }

LEVEL="${1:-}"
test -n "$LEVEL" || { echo "ABORT usage: d8g_genmesh.sh <L1|L2|L3>   (one level per invocation)"; exit 64; }
NC=$(coarsen_of "$LEVEL");  test -n "$NC" || { echo "ABORT $LEVEL is not a registered level"; exit 64; }
NP=$(pyhyp_N_of "$LEVEL"); S0=$(s0_of "$LEVEL"); WANT_CELLS=$(cells_of "$LEVEL")
WANT_QUADS=$(quads_of "$LEVEL"); WANT_POINTS=$(points_of "$LEVEL"); FINER=$(finer_of "$LEVEL")

# ---- G-GEN.1  the run root is THIS item's and is not the archive ------------
ROOT_REAL=$(realpath -m "$ROOT")
test "$ROOT_REAL" = "/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple" || {
  echo "ABORT G-GEN.1 ROOT is not D8G's registered run root: $ROOT_REAL"; exit 3; }
for forb in "$ARCHIVE" /home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv \
            /home/ubuntu/certonomous-runs /home/ubuntu/Certonomous; do
  test "$ROOT_REAL" = "$(realpath -m "$forb")" && {
    echo "ABORT G-GEN.1 ROOT resolves to $forb -- A GRADED RUN ROOT IS EVIDENCE AND IS NEVER WRITTEN INTO."; exit 3; }
done
mkdir -p "$ROOT" || { echo "ABORT cannot create $ROOT"; exit 4; }
chmod 777 "$ROOT" 2>/dev/null
BUILD="$ROOT/mesh_build_$LEVEL"
LOGS="$ROOT/mesh_logs_$LEVEL"
BASEOUT="$ROOT/base_$LEVEL"
test -e "$BASEOUT" && { echo "ABORT G-GEN.1 $BASEOUT already exists.  A regenerated mesh must not silently"; \
                        echo "  overwrite one an arm may already have run against.  REFUSED."; exit 5; }
rm -rf "$BUILD" "$LOGS"; mkdir -p "$BUILD" "$LOGS" || { echo "ABORT cannot create build dirs"; exit 4; }

# ---- G-GEN.2  THE SOURCE.  Bytes first, then the DISCRIMINATING face count --
test -f "$SRC_TGZ" || { echo "ABORT G-GEN.2 source tarball absent: $SRC_TGZ"; exit 4; }
GOT_BYTES=$(stat -c '%s' "$SRC_TGZ")
test "$GOT_BYTES" = "$SRC_BYTES" || { echo "ABORT G-GEN.2 tarball is $GOT_BYTES bytes, registered $SRC_BYTES"; exit 4; }
echo "$SRC_MD5  $SRC_TGZ" | md5sum -c - || { echo "ABORT G-GEN.2 tarball md5"; exit 4; }
cp -a "$SRC_TGZ" "$BUILD/" || { echo "ABORT copy tarball"; exit 4; }
echo "D8G_GENMESH_SOURCE level=$LEVEL tarball=$(basename "$SRC_TGZ") bytes=$GOT_BYTES md5=$SRC_MD5 forbidden_c1_not_used=$TRAP_C1"

# ---- THE CONTAINER STEP.  One cmd file, executed under the PINNED DIGEST. ----
# The whole recipe runs inside the image so that `cgns_utils`, `pyhyp`,
# `plot3dToFoam`, `autoPatch`, `createPatch`, `renumberMesh` and `checkMesh` are
# the GRADED toolchain's own binaries, not the host's.
cat > "$BUILD/genWingMesh_$LEVEL.py" <<PYEOF
# D8G $LEVEL -- the archived A6 genWingMesh.py (md5 af9b63c2a22886b40c2309b298288cb8)
# with EXACTLY TWO registered substitutions: N and s0 (PREREGISTRATION.md 2.2).
# marchDist and every other pyHyp option are unchanged from the archive.
from pyhyp import pyHyp

fileName = "surfMesh.cgns"
options = {
    "inputFile": fileName,
    "fileType": "CGNS",
    "unattachedEdgesAreSymmetry": True,
    "outerFaceBC": "farfield",
    "autoConnect": True,
    "BC": {},
    "families": "wall",
    "N": $NP,
    "s0": $S0,
    "marchDist": 25 * 3.758151,
    "ps0": -1.0,
    "pGridRatio": 1.1,
    "cMax": 5.0,
    "epsE": 1.0,
    "epsI": 2.0,
    "theta": 3.0,
    "volCoef": 0.16,
    "volBlend": 0.0005,
    "volSmoothIter": 30,
    "kspRelTol": 1e-4,
    "kspMaxIts": 50,
    "kspSubspaceSize": 50,
}

hyp = pyHyp(options=options)
hyp.run()
hyp.writePlot3D("volumeMesh.xyz")
PYEOF

# The surface probe: quad faces, points, bounding box and the TE bands.  IT IS
# RUN AFTER EVERY COARSENING, so the c0 assertion and the per-level assertion
# come from the SAME reader.
cat > "$BUILD/d8g_surf_probe.py" <<'PYEOF'
"""Read a CGNS surface and print quad faces, points, bbox and TE statistics as
JSON.  COORDINATES, NOT BYTES: re-running `cgns_utils coarsen` on the same input
produced a file byte-different from the archived one at identical size, so CGNS
file md5 is NOT an instrument for comparing surfaces (PREREGISTRATION.md 4.3)."""
import json, sys
import numpy as np
from cgnsutilities.cgnsutilities import readGrid

g = readGrid(sys.argv[1])
quads, pts = 0, []
for b in g.blocks:
    d = b.dims
    quads += (d[0] - 1) * (d[1] - 1) * (d[2] - 1 if d[2] > 1 else 1)
    pts.append(b.coords.reshape(-1, 3))
P = np.vstack(pts)
bbox = {"x": [float(P[:, 0].min()), float(P[:, 0].max())],
        "y": [float(P[:, 1].min()), float(P[:, 1].max())],
        "z": [float(P[:, 2].min()), float(P[:, 2].max())]}
# TRAILING EDGE, PER SPANWISE BAND.  Coarsening is exactly the operation that
# would collapse it, so it is measured rather than assumed (4.4, G-TE).
y0, y1 = bbox["y"]
nb, mn_pts, lo, hi = 10, None, None, None
for i in range(nb):
    m = (P[:, 1] >= y0 + (y1 - y0) * i / nb) & (P[:, 1] <= y0 + (y1 - y0) * (i + 1) / nb)
    B = P[m]
    if B.shape[0] < 2:
        continue
    chord = float(B[:, 0].max() - B[:, 0].min())
    if chord <= 0.0:
        continue
    te = B[B[:, 0] >= B[:, 0].max() - 0.005 * chord]
    n = int(te.shape[0])
    spread = float(te[:, 2].max() - te[:, 2].min()) / chord if n else 0.0
    mn_pts = n if mn_pts is None else min(mn_pts, n)
    lo = spread if lo is None else min(lo, spread)
    hi = spread if hi is None else max(hi, spread)
print(json.dumps({"quad_faces": int(quads), "points": int(P.shape[0]), "bbox": bbox,
                  "te_bands": {"min_points": mn_pts, "zspread_over_chord_min": lo,
                               "zspread_over_chord_max": hi},
                  "coords_sha_free": True}, sort_keys=True))
PYEOF

# --------------------------------------------------------------------------
# THE PROLOGUE ORDER IS LOAD-BEARING AND WAS MEASURED, NOT REASONED.
#
# This file previously opened cmd.sh with
#     set -e
#     source /home/dafoamuser/dafoam/loadDAFoam.sh
# and THAT ORDER ABORTS.  Measured on D8G's OWN pinned image
# (sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35),
# at D8G's OWN --user 0:0, under D8G's OWN nesting
# (bash -lc "timeout -k 60 3600 bash cmd.sh"):
#     OpenFOAM-v2506/etc/config.sh/setup: line 207:
#     pop_var_context: head of shell_variables not a function context
#   -> the shell exits rc=1 AT LINE 2 and `cd` -- and every line after it --
#      NEVER RUNS.  Control, `set -e` removed: line 3 runs, rc 0.
# The abort is inside OpenFOAM's own etc/bashrc, is independent of uid, and
# happens under both `bash -c` and `bash -lc`.
#
# *** D8G FAILS LOUDLY, AND THAT IS THE ONE MERCY HERE.  Line :299 below tests
#     `test "$GRC" -eq 0` and aborts G-GEN.5 with the rc.  The sister defect in
#     A3GC's generator wrapped the same source in `>/dev/null 2>&1 || true`, so
#     A3GC went on to run SEVEN dead steps and reported a missing binary
#     instead of a dead environment.  Same class, opposite failure mode: THIS
#     rung stops; THAT rung continued. ***
#
# `set -e` is therefore armed AFTER the source, and the source is checked by a
# POSITIVE CAPABILITY ASSERTION rather than by its rc -- because its rc is not
# a test: WITHOUT `set -e` this source returns rc 0 EVEN WHEN THE ENVIRONMENT
# DID NOT LOAD (measured: rc 0, WM_PROJECT_DIR empty, cgns_utils absent).  A
# silent success and a silent failure carry the same rc.  The assertion demands
# the environment SHOW a variable and a binary that exist only after a
# successful load (CLAUDE.md rule 3 -- plant the zero -- applied to an
# environment rather than a field).
#
# NOTE THE ESCAPING.  This heredoc is UNQUOTED (<<CMDEOF), so every `$`
# below that must survive to the CONTAINER is backslash-escaped, exactly as the
# existing `\$(id -u)` and `\$(seq 1 $NC)` are.  An unescaped ${WM_PROJECT_DIR}
# here would be expanded by the HOST shell -- to the empty string -- and the
# assertion would then test nothing at all.
# --------------------------------------------------------------------------
cat > "$BUILD/cmd.sh" <<CMDEOF
source /home/dafoamuser/dafoam/loadDAFoam.sh
if [ -z "\${WM_PROJECT_DIR:-}" ] || ! command -v cgns_utils >/dev/null 2>&1; then
  printf 'ABORT G-GEN.0 loadDAFoam.sh did not populate the environment.\n' >&2
  printf '  WM_PROJECT_DIR = [%s]\n' "\${WM_PROJECT_DIR:-}" >&2
  printf '  cgns_utils     = %s\n' "\$(command -v cgns_utils || echo MISSING)" >&2
  printf '  id             = %s\n' "\$(id)" >&2
  exit 97
fi
set -e
cd /mnt/mesh_build_$LEVEL
echo D8G_GENMESH_UID: \$(id -u)
tar -xvf CRM_surfMesh.cgns.tar.gz
# --- THE DISCRIMINATING ASSERTION: the extracted surface MUST be c0 -----------
python d8g_surf_probe.py surfMesh.cgns > probe_c0.json
python - <<'PY'
import json, sys
j = json.load(open("probe_c0.json"))
if j["quad_faces"] != $C0_QUADS:
    sys.stderr.write("ABORT G-GEN.2 the extracted surface has %d quad faces, not the pristine c0 %d.\n"
                     "  THE FILE BESIDE THE TARBALL IS ALREADY c1 (cgns_utils coarsen writes IN PLACE).\n"
                     % (j["quad_faces"], $C0_QUADS)); sys.exit(9)
print("D8G_C0_CONFIRMED quad_faces=%d points=%d" % (j["quad_faces"], j["points"]))
PY
# --- coarsen exactly $NC times, MEASURING the ratio after each ---------------
prev=$C0_QUADS
for i in \$(seq 1 $NC); do
  cgns_utils coarsen surfMesh.cgns
  python d8g_surf_probe.py surfMesh.cgns > probe_c\$i.json
  python - <<PY
import json, sys
j = json.load(open("probe_c\$i.json"))
r = \$prev / float(j["quad_faces"])
if abs(r - 4.0) > 1e-9:
    sys.stderr.write("ABORT G-GEN.3 coarsening \$i gave ratio %.4f, not the exact 4.  A level whose surface\n"
                     "  ratio is not 4 is NOT a factor-2 coarsening and must never be used as one (c4 reads\n"
                     "  3.702 and is EXCLUDED from this family).\n" % r); sys.exit(9)
print("D8G_COARSEN_OK step=\$i quad_faces=%d ratio=%.4f" % (j["quad_faces"], r))
PY
  prev=\$(python -c "import json;print(json.load(open('probe_c\$i.json'))['quad_faces'])")
done
cp probe_c$NC.json probe_final.json
python - <<PY
import json, sys
j = json.load(open("probe_final.json"))
if j["quad_faces"] != $WANT_QUADS or j["points"] != $WANT_POINTS:
    sys.stderr.write("ABORT G-GEN.3 $LEVEL surface is %d quads / %d points, registered %d / %d\n"
                     % (j["quad_faces"], j["points"], $WANT_QUADS, $WANT_POINTS)); sys.exit(9)
PY
# --- pyHyp, then the archived OpenFOAM chain, verbatim -----------------------
python genWingMesh_$LEVEL.py 2>&1 | tee logMeshGeneration.txt
plot3dToFoam -noBlank volumeMesh.xyz >> logMeshGeneration.txt 2>&1
autoPatch 45 -overwrite       >> logMeshGeneration.txt 2>&1
createPatch -overwrite        >> logMeshGeneration.txt 2>&1
renumberMesh -overwrite       >> logMeshGeneration.txt 2>&1
# --- BOTH checkMesh runs, both logs retained (4.1 clause 4) ------------------
checkMesh                                 > checkMesh_plain.log  2>&1 || true
checkMesh -allGeometry -allTopology       > checkMesh_strict.log 2>&1 || true
echo D8G_GENMESH_DONE level=$LEVEL
CMDEOF

GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG_TAG" 2>/dev/null | sed 's/.*@//')
test "$GOT_DIGEST" = "$IMG_PATCHED_DIGEST" || {
  echo "ABORT G-GEN.4 image digest mismatch: got=$GOT_DIGEST want=$IMG_PATCHED_DIGEST"; exit 4; }
echo "D8G_GENMESH_IMAGE ref=$IMG_REF digest=$GOT_DIGEST pinned_by=digest"

# The generator is CONTAINED, not budgeted: mesh generation is deterministic case
# construction, not a measurement.  The deadline exists so a wedged pyHyp cannot
# hold the box; the L3 generation was measured at 125.47 wall s on 2 cores by the
# drafting lane's probe (section 9.4), so 3,600 s is ~29x that.
sudo -n docker run --rm --user 0:0 --cpus=2 --memory=12g --memory-swap=12g \
  -v "$ROOT":/mnt -w "/mnt/mesh_build_$LEVEL" "$IMG_REF" \
  bash -lc "timeout -k 60 3600 bash /mnt/mesh_build_$LEVEL/cmd.sh" > "$LOGS/genmesh.log" 2>&1
GRC=$?
sudo -n chown -R ubuntu:ubuntu "$BUILD" "$LOGS" 2>/dev/null
test "$GRC" -eq 0 || { echo "ABORT G-GEN.5 generation rc=$GRC -- see $LOGS/genmesh.log"; tail -20 "$LOGS/genmesh.log"; exit "$GRC"; }
cp -a "$BUILD/checkMesh_plain.log" "$BUILD/checkMesh_strict.log" "$BUILD/logMeshGeneration.txt" "$LOGS/" 2>/dev/null

# ---- ASSEMBLE base_<LEVEL>/ --------------------------------------------------
printf '%s\n' "$DICT_MD5" | sed "s#@A@#$ARCHIVE#g" | md5sum -c - > "$LOGS/dict_md5.txt" 2>&1 \
  || { echo "ABORT G-GEN.6 archive dict/field md5 mismatch; see $LOGS/dict_md5.txt"; exit 4; }
NOK=$(grep -c ': OK$' "$LOGS/dict_md5.txt")
test "$NOK" -eq "$N_DICTS" || { echo "ABORT G-GEN.6 dict manifest returned $NOK OK lines, not $N_DICTS"; exit 4; }
mkdir -p "$BASEOUT/constant" "$BASEOUT/system" || { echo "ABORT cannot create $BASEOUT"; exit 4; }
cp -a "$BUILD/constant/polyMesh" "$BASEOUT/constant/" || { echo "ABORT no polyMesh produced"; exit 4; }
cp -a "$ARCHIVE/system/." "$BASEOUT/system/"           || { echo "ABORT copy system"; exit 4; }
cp -a "$ARCHIVE/FFD" "$BASEOUT/"                       || { echo "ABORT copy FFD"; exit 4; }
cp -a "$ARCHIVE/0.orig" "$BASEOUT/0"                   || { echo "ABORT copy 0.orig -> 0"; exit 4; }
test -f "$BASEOUT/constant/polyMesh/points.gz" || { echo "ABORT no points.gz in the staged mesh"; exit 4; }

# ---- WRITE THE CONSTRUCTION RECORD d8g_grade.py READS ------------------------
# EVERY FIELD IS MEASURED FROM THE LOGS AND THE MESH THIS RUN JUST PRODUCED.
# Nothing is copied forward from the drafting lane's probe.
python3 - "$LEVEL" "$BUILD" "$BASEOUT" "$ROOT" "$WANT_CELLS" "$FINER" <<'PYEOF'
import hashlib, json, os, re, sys
level, build, baseout, root, want_cells, finer = sys.argv[1:7]
want_cells = int(want_cells)

def refuse(msg):
    sys.stderr.write("ABORT G-GEN.7 %s\n" % msg); sys.exit(7)

plain = open(os.path.join(build, "checkMesh_plain.log"), errors="replace").read()
strict = open(os.path.join(build, "checkMesh_strict.log"), errors="replace").read()

cells = re.findall(r"cells:\s+(\d+)", plain)
if not cells:
    refuse("no cell count in checkMesh_plain.log")
cells = int(cells[0])

# THE AUTHORITATIVE DIMENSIONALITY LINE IS THE GEOMETRIC ONE.  `Mesh has 3
# solution (non-empty) directions` sits four lines away AND A WEDGE READS 3 ON
# IT, so both are recorded and only the geometric one is graded (4.1 clause 3).
geo = [int(x) for x in re.findall(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions", strict + plain)]
sol = [int(x) for x in re.findall(r"Mesh has (\d+) solution \(non-empty\) directions", strict + plain)]
if not geo:
    refuse("no `Mesh has N geometric (non-empty/wedge) directions` line in either checkMesh log")

# patches, by NAME, from the mesh's own boundary file
bnd = open(os.path.join(baseout, "constant", "polyMesh", "boundary"), errors="replace").read()
patches = []
for m in re.finditer(r"^\s{4}(\w+)\s*$\s*\{(.*?)^\s{4}\}", bnd, re.M | re.S):
    body = m.group(2)
    t = re.search(r"type\s+(\w+)\s*;", body)
    nf = re.search(r"nFaces\s+(\d+)\s*;", body)
    if t and nf:
        patches.append({"name": m.group(1), "type": t.group(1), "nFaces": int(nf.group(1))})
if not patches:
    refuse("could not parse constant/polyMesh/boundary")

# the strict failures, BY NAME.  The two this family expects are registered in
# 4.2; anything else must surface as a THIRD failing check, not be swallowed.
failed = []
if re.search(r"\*\*\*Error in face tets", strict):
    failed.append("face tets")
if re.search(r"Cells with small determinant", strict):
    failed.append("small determinant")
for m in re.finditer(r"^\s*\*\*\*(.+)$", strict, re.M):
    txt = m.group(1)
    if "face tets" in txt or "small determinant" in txt:
        continue
    failed.append(txt.strip()[:60])
bad_tets = re.search(r"face tets:\s+(\d+)\s+faces", strict)
small_det = re.search(r"small determinant \(< 0\.001\) found, number of cells:\s+(\d+)", strict)
frac = (int(small_det.group(1)) / float(cells)) if small_det else None

probe = json.load(open(os.path.join(build, "probe_final.json")))
delta = None
if finer:
    fp = os.path.join(root, "mesh_build_%s" % finer, "probe_final.json")
    if os.path.isfile(fp):
        f = json.load(open(fp))
        delta = max(abs(probe["bbox"][ax][i] - f["bbox"][ax][i]) for ax in "xyz" for i in (0, 1))

pts = os.path.join(baseout, "constant", "polyMesh", "points.gz")
rec = {"level": level, "cells": cells, "cells_registered": want_cells,
       "surface_points": probe["points"], "surface_quad_faces": probe["quad_faces"],
       "patches": patches, "geometric_directions": geo, "solution_directions": sol,
       "checkmesh_plain": ("Mesh OK." if "Mesh OK." in plain else plain.strip().splitlines()[-1][:120]),
       "checkmesh_plain_log": "mesh_logs_%s/checkMesh_plain.log" % level,
       "checkmesh_strict_log": "mesh_logs_%s/checkMesh_strict.log" % level,
       "strict_failed_checks": failed,
       "bad_face_tets": (int(bad_tets.group(1)) if bad_tets else None),
       "small_det_cells": (int(small_det.group(1)) if small_det else None),
       "small_det_fraction": frac, "bbox": probe["bbox"], "te_bands": probe["te_bands"],
       "surface_max_coord_delta_to_finer": delta,
       "points_md5": hashlib.md5(open(pts, "rb").read()).hexdigest(),
       "image_digest": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35",
       "generated_by": "d8g_genmesh.sh",
       "NOTE": "this record is MEASURED EVIDENCE, not a claim: d8g_grade.py's G-MESH gates every "
               "field in it against the values PREREGISTRATION.md section 2.2/4.1-4.4 registered, "
               "so it cannot self-certify."}
if cells != want_cells:
    sys.stderr.write("D8G_GENMESH_CELL_MISMATCH level=%s got=%d registered=%d -- the record is written "
                     "ANYWAY so the grader can render the GATE FAIL from evidence rather than from a "
                     "missing file\n" % (level, cells, want_cells))
out = os.path.join(root, "mesh_record_%s.json" % level)
json.dump(rec, open(out, "w"), indent=1, sort_keys=True)
print("D8G_MESH_RECORD level=%s cells=%d patches=%d geometric=%s strict_failed=%s small_det_fraction=%s "
      "points_md5=%s file=%s" % (level, cells, len(patches), geo, failed, frac, rec["points_md5"], out))
PYEOF
RRC=$?
test "$RRC" -eq 0 || { echo "ABORT G-GEN.7 record not written (rc=$RRC)"; exit "$RRC"; }
chmod -R a+rX "$BASEOUT" 2>/dev/null
echo "D8G_GENMESH_COMPLETE level=$LEVEL base=$BASEOUT record=$ROOT/mesh_record_$LEVEL.json logs=$LOGS"
echo "  NEXT: this script has NEVER BEEN EXECUTED.  Its cell-count, patch, dimensionality,"
echo "  strict-check and TE assertions are section 8 P1/P2 PREDICTIONS.  A failure to reproduce"
echo "  them is a DEFECT TO REPORT, not a number to adjust."
exit 0
