#!/usr/bin/env bash
# stage.sh -- A3 rung 1 patched-IDWarp, np=4. Phase-2 lane, written AFTER the pre-registration
# commit 5d8e2f52 and committed BEFORE it runs. It changes no gate, threshold, band, cap or label.
#
# It builds the three staged copies named in PREREGISTRATION.md section 7 and runs every staging
# assert registered there. ANY failure => BLOCKED, nothing launches.
#
# Asserts (PREREGISTRATION.md section 7, bullet 2):
#   sha256(constant/polyMesh/points.gz) == 695b729d...
#   md5(dRdWColoring_4.bin)             == a6919b8494a78f09c9c876e0d21686e2
#   diff -rq 0 0.orig                    empty
#   no processor* and no non-`0` time directory in any staged copy
#   diff runScript_fd3.py runScript_fd3p.py shows only D1, D2, D2b, D3
set -u
ARCH=/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840
ROOT=/home/ubuntu/certonomous-runs/P4-a3-rung1-patched
HERE="$(cd "$(dirname "$0")" && pwd)"
PTS_SHA=695b729da801ed2f95723877e34702ee65ce37a87fddbddacb3f3b4ce38f0a7f
CACHE_MD5=a6919b8494a78f09c9c876e0d21686e2
LOGF=""
say() { echo "$(date -u +%FT%TZ) $*"; [ -n "$LOGF" ] && echo "$(date -u +%FT%TZ) $*" >> "$LOGF"; }
die() { say "STAGING REFUSED: $*"; say "=== BLOCKED. Nothing launches. ==="; exit 1; }

mkdir -p "$ROOT"
LOGF="$ROOT/stage.log"
say "=== A3 rung 1 staging begins. Archived case is READ-ONLY to this item. ==="

# --- assert 1: mesh identity ------------------------------------------------
GOT=$(sha256sum "$ARCH/constant/polyMesh/points.gz" | awk '{print $1}')
[ "$GOT" = "$PTS_SHA" ] || die "points.gz sha256 $GOT != registered $PTS_SHA"
say "assert 1 OK: points.gz sha256 = $GOT"

# --- assert 2: colouring cache identity -------------------------------------
GOT=$(md5sum "$ARCH/dRdWColoring_4.bin" | awk '{print $1}')
[ "$GOT" = "$CACHE_MD5" ] || die "dRdWColoring_4.bin md5 $GOT != registered $CACHE_MD5"
say "assert 2 OK: dRdWColoring_4.bin md5 = $GOT"

# --- assert 3: the serial 0/ is byte-identical to 0.orig --------------------
D=$(diff -rq "$ARCH/0" "$ARCH/0.orig" 2>&1)
[ -z "$D" ] || die "diff -rq 0 0.orig is NOT empty: $D"
say "assert 3 OK: diff -rq 0 0.orig empty -- the serial 0/ carries no primal end state"

# --- build runScript_fd3p.py (D1, D2, D2b, D3), all log-only or new-branch --
python3 - "$ARCH/runScript_fd3.py" "$ROOT/runScript_fd3p.py" <<'PYEOF'
import sys
src, dst = sys.argv[1], sys.argv[2]
t = open(src).read()

D1 = '''
# --- D1 (PREREGISTRATION.md section 3 departure 6): per-rank IDWarp provenance stamp.
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

D2 = '''    # --- D2 (PREREGISTRATION.md section 3 departure 6): log-only dump of the full analytic
    # totals dict at default numpy print options. It is what makes R1-P10 measurable. ---
    log0("FD3 TOTALS_DUMP_BEGIN")
    log0(repr(totals))
    log0("FD3 TOTALS_DUMP_END")
'''

D2B = '''    # --- D2b (PREREGISTRATION.md section 3 departure 5/6): log-only runtime argmax|g| per DV
    # group. It changes NOTHING about which components are perturbed or graded. ---
    for _g in ("patchV", "twist", "shape"): _row = find_total(_g)[0]; log0("FD3 ARGMAX %s: index %d value %.14e (row len %d)" % (_g, int(np.argmax(np.abs(_row))), float(_row[int(np.argmax(np.abs(_row)))]), len(_row)))
'''

D3 = '''elif args.task == "fd1wrong":
    # --- D3 (PREREGISTRATION.md section 3 departure 6, section 6 arm R1-C): the Charter section 4
    # registered TRIVIAL BASELINE. Deliberately wrong FD step 1e-8 (the registered step is 1e-2),
    # ONE component, no adjoint. patchV = [U0, aoa0] with U0 registered at lower == upper == U0, so
    # index 1 (AoA) is the only free component BY CONSTRUCTION -- not transcribed from any output.
    comm = MPI.COMM_WORLD
    def log0(msg):
        if comm.rank == 0:
            print(msg, flush=True)
    VAR = "patchV"
    IDX = 1
    H = 1.0e-8
    OF = "scenario1.aero_post.CD"
    FLOOR = 1.626e-06          # rung 1's measured repeat-baseline drift, fd3_run.log:4905
    THRESH = 10.0 * FLOOR      # this rung's pre-registered evaluability gate

    prob.run_model()
    cd_base1 = float(prob.get_val(OF)[0])
    log0("FD1W baseline1 CD = %.14e" % cd_base1)

    base = prob.get_val(VAR).copy()
    log0("FD1W component %s[%d] of %d, base value %0.14g" % (VAR, IDX, len(base), base[IDX]))
    cd_pm = {}
    for sgn in (+1, -1):
        v = base.copy()
        v[IDX] += sgn * H
        prob.set_val(VAR, v)
        log0("FD1W perturb %s[%d] %s h=%g: DV %0.14g -> %0.14g" % (
            VAR, IDX, "+" if sgn > 0 else "-", H, base[IDX], v[IDX]))
        prob.run_model()
        cd_pm[sgn] = float(prob.get_val(OF)[0])
        log0("FD1W CD(%s h=%g) = %.14e" % ("+" if sgn > 0 else "-", H, cd_pm[sgn]))
    prob.set_val(VAR, base)
    delta = cd_pm[1] - cd_pm[-1]
    fd = delta / (2.0 * H)
    log0("FD1W raw delta |CD(+h)-CD(-h)| = %.6e" % abs(delta))
    log0("FD1W evaluability threshold (10x drift %.6e) = %.6e" % (FLOOR, THRESH))
    log0("FD1W EVALUABLE = %s  (delta/threshold = %.6e)" % (
        "YES" if abs(delta) > THRESH else "NO", abs(delta) / THRESH))
    log0("FD1W central FD %s[%d] h=%g: %.14e" % (VAR, IDX, H, fd))

    prob.run_model()
    cd_base2 = float(prob.get_val(OF)[0])
    log0("FD1W baseline2 CD = %.14e" % cd_base2)
    log0("FD1W |baseline drift| = %.6e" % abs(cd_base2 - cd_base1))
    log0("FD1W done")
'''

def once(text, anchor):
    assert text.count(anchor) == 1, "anchor not unique: %r" % anchor[:60]
    return anchor

a1 = once(t, "from pygeo import geo_utils\n")
t = t.replace(a1, a1 + D1, 1)

a2 = once(t, '    totals = prob.compute_totals(of=[OF], wrt=["patchV", "twist", "shape"])\n')
t = t.replace(a2, a2 + D2, 1)

a3 = once(t, '    base_vals = {var: prob.get_val(var).copy() for var, _ in comps}\n')
t = t.replace(a3, D2B + a3, 1)

a4 = once(t, 'else:\n    print("task arg not found!")\n')
t = t.replace(a4, D3 + a4, 1)

open(dst, "w").write(t)
print("runScript_fd3p.py written: %d bytes" % len(t))
PYEOF
[ -s "$ROOT/runScript_fd3p.py" ] || die "runScript_fd3p.py was not produced"
python3 -c "import ast,sys; ast.parse(open('$ROOT/runScript_fd3p.py').read())" \
  || die "runScript_fd3p.py does not parse"
say "runScript_fd3p.py built and parses"

# --- assert 4: the diff contains ONLY D1, D2, D2b, D3 -----------------------
diff "$ARCH/runScript_fd3.py" "$ROOT/runScript_fd3p.py" > "$ROOT/runScript_fd3p.diff"
NHUNK=$(grep -cE '^[0-9]+(,[0-9]+)?[acd][0-9]+(,[0-9]+)?$' "$ROOT/runScript_fd3p.diff")
NDEL=$(grep -cE '^<' "$ROOT/runScript_fd3p.diff" || true)
[ "$NHUNK" = "4" ] || die "expected exactly 4 diff hunks (D1, D2, D2b, D3), got $NHUNK"
[ "$NDEL" = "0" ]  || die "the diff DELETES $NDEL line(s) -- insertions only were registered"
say "assert 4 OK: 4 insertion hunks, 0 deletions, 0 modifications (diff at $ROOT/runScript_fd3p.diff)"

# --- stage the three copies -------------------------------------------------
for ARM in patched shipped wrongstep; do
  D="$ROOT/$ARM"
  [ -e "$D" ] && die "$D already exists -- a guard refuses a staged tree that is not fresh"
  mkdir -p "$D"
  cp -a "$ARCH/0" "$ARCH/0.orig" "$ARCH/FFD" "$ARCH/constant" "$ARCH/system" "$D/"
  cp -a "$ARCH/dRdWColoring_4.bin" "$ARCH/dRdWColoring_4.bin.info" "$D/"
  cp -a "$ARCH/runScript_fd3.py" "$D/"
  cp -a "$ROOT/runScript_fd3p.py" "$D/"
  # assert: no processor*, no non-`0` time directory, cache and mesh intact in the COPY
  P=$(ls -d "$D"/processor* 2>/dev/null | wc -l)
  [ "$P" = "0" ] || die "$ARM: $P processor* directories exist in the staged copy"
  T=$(find "$D" -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' \
        ! -name 0 | wc -l)
  [ "$T" = "0" ] || die "$ARM: $T non-zero time directories exist in the staged copy"
  G=$(sha256sum "$D/constant/polyMesh/points.gz" | awk '{print $1}')
  [ "$G" = "$PTS_SHA" ] || die "$ARM: staged points.gz sha256 $G != $PTS_SHA"
  G=$(md5sum "$D/dRdWColoring_4.bin" | awk '{print $1}')
  [ "$G" = "$CACHE_MD5" ] || die "$ARM: staged cache md5 $G != $CACHE_MD5"
  D2=$(diff -rq "$D/0" "$D/0.orig" 2>&1)
  [ -z "$D2" ] || die "$ARM: staged 0 and 0.orig differ: $D2"
  say "staged $ARM: no processor*, no non-0 time dir, mesh and cache hashes as registered"
done

say "=== STAGING COMPLETE. Three copies under $ROOT. Archived case untouched. ==="
exit 0
