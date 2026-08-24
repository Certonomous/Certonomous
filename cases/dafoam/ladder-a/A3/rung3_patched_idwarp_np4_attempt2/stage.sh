#!/usr/bin/env bash
# stage.sh -- A3 rung 3 patched-IDWarp, np=4, ATTEMPT 2. Copied byte-identical from
# ../rung3_patched_idwarp_np4/stage.sh (frozen at 3525f1d2) except for the lines listed in this
# item's PREREGISTRATION.md section 11. It changes no gate, threshold, band, cap or label.
#
# Asserts (PREREGISTRATION.md section 7, bullet 2):
#   sha256(constant/polyMesh/points.gz) == cf35cf14... AND matches birth_certificate.json,
#     whose verdict reads "clean"
#   md5(dRdWColoring_4.bin)             == f91c25c1c6be0d9427d32b2ada482870
#   diff -rq 0 0.orig                    empty
#   no processor* and no non-`0` time directory in the staged copy
#   diff runScript_rung3.py runScript_rung3p.py shows only D1, D2, D3
#
# DISCLOSED PLACEMENT OF D2, recorded here and in RESULTS.md rather than left to the reading:
# section 3 departure 5 registers D2 as `log0(repr(totals))` "immediately after compute_totals",
# and states its purpose is that "if the patched adjoint converges, this is what makes the
# gradient readable at all" -- on THIS arm, which runs -task ct_cd. The only compute_totals this
# arm executes is the one inside the new ct_cd branch, so D2 is placed there. A D2 placed in the
# pre-existing `compute_totals` branch would be dead code that this arm never reaches, which is
# the opposite of what the departure was registered to buy. The consequence is that D2 and D3 are
# textually contiguous and the diff carries TWO insertion hunks rather than three; the registered
# assert -- "the diff shows only D1, D2, D3" -- is checked literally below, insertions only, zero
# deletions, and every inserted line carrying its D-marker.
set -u
ARCH=/home/ubuntu/certonomous-runs/A3-rung3-n52
ROOT=/home/ubuntu/certonomous-runs/P5-a3-rung3-patched-attempt2
HERE="$(cd "$(dirname "$0")" && pwd)"
PTS_SHA=cf35cf1446830d880bded657d59dea0417c2dd3d01b238e1e37514ecd9432caa
CACHE_MD5=f91c25c1c6be0d9427d32b2ada482870
LOGF=""
say() { echo "$(date -u +%FT%TZ) $*"; [ -n "$LOGF" ] && echo "$(date -u +%FT%TZ) $*" >> "$LOGF"; }
die() { say "STAGING REFUSED: $*"; say "=== BLOCKED. Nothing launches. ==="; exit 1; }

mkdir -p "$ROOT"
LOGF="$ROOT/stage.log"
say "=== A3 rung 3 staging begins. Archived case is READ-ONLY to this item. ==="

# --- assert 1: mesh identity, against the file AND the birth certificate -----
GOT=$(sha256sum "$ARCH/constant/polyMesh/points.gz" | awk '{print $1}')
[ "$GOT" = "$PTS_SHA" ] || die "points.gz sha256 $GOT != registered $PTS_SHA"
BC=$(python3 -c "import json;d=json.load(open('$ARCH/constant/birth_certificate.json'));print(d['points_sha256'],d['verdict'],d['cells'])")
set -- $BC
[ "$1" = "$PTS_SHA" ] || die "birth_certificate points_sha256 $1 != registered $PTS_SHA"
[ "$2" = "clean" ]    || die "birth_certificate verdict is '$2', not 'clean'"
[ "$3" = "79560" ]    || die "birth_certificate cells $3 != 79560"
say "assert 1 OK: points.gz sha256 = $GOT; birth certificate verdict=clean cells=79560"

# --- assert 2: colouring cache identity -------------------------------------
GOT=$(md5sum "$ARCH/dRdWColoring_4.bin" | awk '{print $1}')
[ "$GOT" = "$CACHE_MD5" ] || die "dRdWColoring_4.bin md5 $GOT != registered $CACHE_MD5"
say "assert 2 OK: dRdWColoring_4.bin md5 = $GOT"

# --- assert 3: the serial 0/ is byte-identical to 0.orig --------------------
D=$(diff -rq "$ARCH/0" "$ARCH/0.orig" 2>&1)
[ -z "$D" ] || die "diff -rq 0 0.orig is NOT empty: $D"
say "assert 3 OK: diff -rq 0 0.orig empty -- the serial 0/ carries no primal end state"

# --- build runScript_rung3p.py (D1, D2, D3) ---------------------------------
python3 - "$ARCH/runScript_rung3.py" "$ROOT/runScript_rung3p.py" <<'PYEOF'
import sys
src, dst = sys.argv[1], sys.argv[2]
t = open(src).read()

D1 = '''
# --- D1 (PREREGISTRATION.md section 3 departure 5): per-rank IDWarp provenance stamp.
# Log-only; runs before any numeric call. BUILD.md section 2: the md5 of libidwarp.so is the ONLY
# discriminator between the stock and patched stacks (the version string reads 2.6.2 on both).
# BUILD.md section 6: Open MPI may not forward the parent environment to every rank, so the hash
# is printed PER RANK. The .so adjacent to the loaded package is searched in-package first, then
# one level up, and the RESOLVED PATH is printed beside the hash.
import hashlib as _hashlib
import idwarp as _idwarp
import importlib.metadata as _ilmd
_r = MPI.COMM_WORLD.rank
_p = _idwarp.__file__
_so = ""
for _c in (os.path.join(os.path.dirname(_p), "libidwarp.so"),
           os.path.join(os.path.dirname(_p), "..", "libidwarp.so")):
    if os.path.exists(_c):
        _so = os.path.realpath(_c)
        break
_md5 = _hashlib.md5(open(_so, "rb").read()).hexdigest() if _so else "NOT_FOUND"
print("PROV rank %d IDWARP_IMPORTED_FROM: %s" % (_r, _p), flush=True)
print("PROV rank %d IDWARP_SO_PATH: %s" % (_r, _so), flush=True)
print("PROV rank %d IDWARP_SO_MD5 = %s" % (_r, _md5), flush=True)
print("PROV rank %d IDWARP_SO_BYTES = %d" % (_r, os.path.getsize(_so) if _so else -1), flush=True)
print("PROV rank %d idwarp version = %s" % (_r, _ilmd.version("idwarp")), flush=True)
MPI.COMM_WORLD.Barrier()
'''

D3 = '''elif args.task == "ct_cd":
    # --- D3 (PREREGISTRATION.md section 3 departure 5): a new task branch computing totals for
    # CD ONLY. It touches no existing branch. Section 3 departure 6 retires this departure BY
    # MEASUREMENT: at rung 2 the CD-only form (fd3) and the CD+CL form (compute_totals) produced
    # bit-identical CD adjoints on all 11 printed checkpoints, so requesting CL as well does not
    # perturb the CD solve on this case family. ---
    comm = MPI.COMM_WORLD
    def log0(msg):
        if comm.rank == 0:
            print(msg, flush=True)
    OF = "scenario1.aero_post.CD"
    prob.run_model()
    log0("CT_CD baseline CD = %.14e" % float(prob.get_val(OF)[0]))
    totals = prob.compute_totals(of=[OF], wrt=["patchV", "twist", "shape"])
    # --- D2 (PREREGISTRATION.md section 3 departure 5): log-only dump of the full analytic totals
    # dict. It produces nothing in the predicted branch (no convergence => no totals) and exists
    # for the branch predicted NOT to occur: if the patched adjoint converges, this is what makes
    # the gradient readable at all. Placed inside ct_cd because that is the only compute_totals
    # this arm executes; see the disclosure at the head of stage.sh. ---
    log0("CT_CD TOTALS_DUMP_BEGIN")
    log0(repr(totals))
    log0("CT_CD TOTALS_DUMP_END")
    log0("CT_CD done")
'''

def once(text, anchor):
    assert text.count(anchor) == 1, "anchor not unique: %r" % anchor[:60]
    return anchor

a1 = once(t, "from pygeo import geo_utils\n")
t = t.replace(a1, a1 + D1, 1)

a2 = once(t, 'else:\n    print("task arg not found!")\n')
t = t.replace(a2, D3 + a2, 1)

open(dst, "w").write(t)
print("runScript_rung3p.py written: %d bytes" % len(t))
PYEOF
[ -s "$ROOT/runScript_rung3p.py" ] || die "runScript_rung3p.py was not produced"
python3 -c "import ast; ast.parse(open('$ROOT/runScript_rung3p.py').read())" \
  || die "runScript_rung3p.py does not parse"
say "runScript_rung3p.py built and parses"

# --- assert 4: insertions only, and they are D1, D2, D3 ---------------------
diff "$ARCH/runScript_rung3.py" "$ROOT/runScript_rung3p.py" > "$ROOT/runScript_rung3p.diff"
NHUNK=$(grep -cE '^[0-9]+(,[0-9]+)?[acd][0-9]+(,[0-9]+)?$' "$ROOT/runScript_rung3p.diff")
NDEL=$(grep -cE '^<' "$ROOT/runScript_rung3p.diff" || true)
[ "$NHUNK" = "2" ] || die "expected 2 insertion hunks (D1; D3-containing-D2), got $NHUNK"
[ "$NDEL" = "0" ]  || die "the diff DELETES $NDEL line(s) -- insertions only were registered"
for M in 'D1 (PREREGISTRATION.md section 3 departure 5)' \
         'D2 (PREREGISTRATION.md section 3 departure 5)' \
         'D3 (PREREGISTRATION.md section 3 departure 5)'; do
  grep -qF "$M" "$ROOT/runScript_rung3p.diff" || die "marker missing from the diff: $M"
done
say "assert 4 OK: 2 insertion hunks, 0 deletions, all three D-markers present (diff at $ROOT/runScript_rung3p.diff)"

# --- stage the single copy --------------------------------------------------
D="$ROOT/patched"
[ -e "$D" ] && die "$D already exists -- a guard refuses a staged tree that is not fresh"
mkdir -p "$D"
cp -a "$ARCH/0" "$ARCH/0.orig" "$ARCH/FFD" "$ARCH/constant" "$ARCH/system" "$D/"
cp -a "$ARCH/dRdWColoring_4.bin" "$ARCH/dRdWColoring_4.bin.info" "$D/"
cp -a "$ARCH/runScript_rung3.py" "$D/"
cp -a "$ROOT/runScript_rung3p.py" "$D/"
P=$(ls -d "$D"/processor* 2>/dev/null | wc -l)
[ "$P" = "0" ] || die "patched: $P processor* directories exist in the staged copy"
T=$(find "$D" -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' ! -name 0 | wc -l)
[ "$T" = "0" ] || die "patched: $T non-zero time directories exist in the staged copy"
G=$(sha256sum "$D/constant/polyMesh/points.gz" | awk '{print $1}')
[ "$G" = "$PTS_SHA" ] || die "patched: staged points.gz sha256 $G != $PTS_SHA"
G=$(md5sum "$D/dRdWColoring_4.bin" | awk '{print $1}')
[ "$G" = "$CACHE_MD5" ] || die "patched: staged cache md5 $G != $CACHE_MD5"
D2=$(diff -rq "$D/0" "$D/0.orig" 2>&1)
[ -z "$D2" ] || die "patched: staged 0 and 0.orig differ: $D2"
say "staged patched: no processor*, no non-0 time dir, mesh and cache hashes as registered"

say "=== STAGING COMPLETE. One copy under $ROOT. Archived case untouched. ==="
exit 0
