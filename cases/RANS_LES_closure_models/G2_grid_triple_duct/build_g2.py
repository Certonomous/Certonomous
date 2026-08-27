"""G2 stager: builds the three duct case trees of the G2 refinement family.

The G2 substrate ships NO mesh dictionary -- only a frozen `constant/polyMesh`.
This stager therefore CONSTRUCTS a `blockMeshDict` from the shipped geometry and
proves the construction by regenerating the SHIPPED mesh from it and comparing
against the shipped points (the RECONSTRUCTION CONTROL, section 6.1 of the
pre-registration).  Every geometric constant below is re-derived from the
shipped `constant/polyMesh/points` at stage time and the stager REFUSES if the
derivation disagrees with the frozen value.

Refusals are `raise` / `sys.exit(2)`, never `assert`: `python3 -O` deletes every
assert (L-332), and this module counts its own `ast.Assert` nodes to prove it
holds none -- with the counter first shown able to count a planted one.
"""

import ast
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---- FROZEN REGISTRY (PREREGISTRATION.md sections 2, 3) -------------------
SRC_CASE = Path("/home/ubuntu/closure-challenge-benchmark/data/DUCT/AR_1_Ret_360")
DEST_ROOT = Path("/home/ubuntu/closure-data/g2")

# Geometry, DERIVED from the shipped polyMesh (section 3.1) and re-derived here.
LX = 1.0e-3          # streamwise, one cell, between matched cyclic patches
LY = 1.0e-3          # wall-normal, symmetryBottom (y=0) -> wallTop (y=LY)
LZ = 1.0e-3          # wall-normal, symmetrySide  (z=0) -> wallSide (z=LZ)
SHIPPED_N = 55       # shipped cells per cross-plane direction
SHIPPED_Q = 1.0 / 1.1        # shipped per-cell expansion ratio, toward the wall
GRADING_R = 1.1 ** -(SHIPPED_N - 1)   # blockMesh simpleGrading total ratio
GEOM_RTOL = 1e-6     # tolerance on the re-derivation of LX/LY/LZ and the ratio
RECON_ABSTOL_M = 1e-9   # max point deviation allowed in the reconstruction control

# level, N per cross-plane direction, nCells, endTime, timeout_s
LEVELS = (
    ("L1", 32, 1024, 20000, 300),
    ("L2", 64, 4096, 30000, 1500),
    ("L3", 128, 16384, 40000, 5400),
)

# Files copied byte-for-byte from the source case, with their frozen digests.
COPY_VERBATIM = {
    "0/U": "8462a05fa8dce60093aa1a34251596667acdf50bcd2ef704277cd00b1414ec49",
    "0/k": "1e755bd0d840c3a5ede274b64054993ddbb0a7f9e9f31967c59e29ef6f91a131",
    "0/omega": "a84d8a12c28b51e093e4f3ab0de814b15510f5d6c777be90e7048531798a0176",
    "0/p": "da1762534f4ab70f4c07d2bde4bffe55f37ad499798f9fd9bc888cfa15d59232",
    "0/nut": "dcfa06be2390ad4f85da29040a6800a5960d6ce0a2a190b5a2fe766ac160c602",
    "caseDef": "ec407609644975379550ca05c3416ea65702182cd9db79d1406199490ce58c14",
    "fieldDef": "796600b2dc51f825be647e39af7f083e6daf5bc034eb57c293551036092eec55",
    "constant/transportProperties":
        "39a7a82a74c54df0eedd154171ba9765091e9d683ee6d317280b997a3c2879c5",
    "constant/turbulenceProperties":
        "ddfbd17effc13a6e81ddc9da5471860bce32f597ca1eca3dafa291788e09f46c",
    "system/fvSchemes":
        "a82aabc3df41fbf4e3330820b1d8f2263ad671fb417760ebe76b174460272e6d",
    "system/fvOptions":
        "3c60002f3fb71ef5e8188c0d986ab505dde9d53ef44d71f4d1734e64d04a72cb",
}
SRC_FVSOLUTION_SHA = "1baa72f8b6b015701bab3c4561184caf8178a8af1b6721f5d89271841a1ba727"
SRC_POINTS_SHA = "3503916e3526247bd2218fbcee53243166b7130e745b399b74cf6fdc61c32c70"

# The shipped `libs` line, preserved verbatim (standing rule 14: a libs entry is
# never deleted to tidy a case).
LIBS_LINE = 'libs ( "libfrozenIncompressibleTurbulenceModels.so" );'

CONTROLDICT = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

{libs}

application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {end};
purgeWrite      0;
writeFormat     ascii;
writePrecision  12;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

functions
{{
}}
"""

BLOCKMESHDICT = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale   1;

vertices
(
    (0 0 0)
    ({lx} 0 0)
    ({lx} {ly} 0)
    (0 {ly} 0)
    (0 0 {lz})
    ({lx} 0 {lz})
    ({lx} {ly} {lz})
    (0 {ly} {lz})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (1 {n} {n}) simpleGrading (1 {r} {r})
);

edges
(
);

boundary
(
    inflow
    {{
        type            cyclic;
        neighbourPatch  outflow;
        faces           ((0 3 7 4));
    }}
    outflow
    {{
        type            cyclic;
        neighbourPatch  inflow;
        faces           ((1 5 6 2));
    }}
    wallTop
    {{
        type            wall;
        faces           ((3 2 6 7));
    }}
    wallSide
    {{
        type            wall;
        faces           ((4 5 6 7));
    }}
    symmetryBottom
    {{
        type            symmetry;
        faces           ((0 1 5 4));
    }}
    symmetrySide
    {{
        type            symmetry;
        faces           ((0 3 2 1));
    }}
);

mergePatchPairs
(
);
"""

TIME_DIR = re.compile(r"^[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$")


class Refusal(Exception):
    """A condition that must stop this instrument under ANY interpreter flag."""


def refuse(msg):
    raise Refusal(msg)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------
# L-332 control: no refusal in this module may be an `assert`
# --------------------------------------------------------------------------
def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def no_assert_control():
    planted = count_asserts("def f(x):\n    assert x, 'planted'\n    return x\n")
    if planted != 1:
        refuse("AST-CONTROL: the counter returned %d on a snippet holding exactly "
               "one assert; its zero here would be a blind spot, not a reading."
               % planted)
    own = count_asserts(Path(__file__).read_text())
    if own != 0:
        refuse("AST-CONTROL: this module holds %d ast.Assert node(s); python3 -O "
               "deletes every one (L-332)." % own)
    return planted, own


# --------------------------------------------------------------------------
# OpenFOAM ASCII readers used by the geometry derivation
# --------------------------------------------------------------------------
def read_points(path):
    path = Path(path)
    if not path.is_file():
        refuse("POINTS: %s does not exist; there is no geometry to derive" % path)
    text = path.read_text(errors="replace")
    m = re.search(r"\n(\d+)\s*\n\(", text)
    if m is None:
        refuse("POINTS: %s carries no `<count>\\n(` list header" % path)
    n = int(m.group(1))
    start = m.end()
    close = text.find("\n)", start)
    if close < 0:
        refuse("POINTS: %s has an unterminated point list" % path)
    body = text[start:close]
    pts = [tuple(float(x) for x in t.split())
           for t in re.findall(r"\(([^)]*)\)", body)]
    if len(pts) != n:
        refuse("POINTS: %s declares %d points and holds %d" % (path, n, len(pts)))
    for p in pts:
        if len(p) != 3:
            refuse("POINTS: %s holds a non-3-component entry" % path)
    return pts


def unique_axis(pts, axis, tol=1e-14):
    vals = sorted(set(round(p[axis], 14) for p in pts))
    out = []
    for v in vals:
        if not out or abs(v - out[-1]) > tol:
            out.append(v)
    return out


def derive_geometry(src_case):
    """Re-derive every geometric constant from the shipped polyMesh.

    Nothing about the family's geometry is a CHOICE: the bounding box, the cell
    counts per direction and the grading ratio are all read back off the shipped
    mesh, and this function REFUSES if any of them disagrees with the frozen
    value in the registry above.
    """
    ppath = Path(src_case) / "constant/polyMesh/points"
    if not ppath.is_file():
        refuse("SOURCE: %s does not exist; the substrate is absent" % ppath)
    got = sha256_bytes(ppath.read_bytes())
    if got != SRC_POINTS_SHA:
        refuse("SOURCE: %s sha256 %s, registered %s. The substrate moved; the "
               "frozen geometry is no longer the geometry on disk."
               % (ppath, got, SRC_POINTS_SHA))
    pts = read_points(ppath)
    xs, ys, zs = (unique_axis(pts, a) for a in (0, 1, 2))
    if len(xs) != 2:
        refuse("GEOMETRY: the shipped mesh has %d distinct x planes, registered 2 "
               "(one cell between matched cyclic patches)" % len(xs))
    ny, nz = len(ys) - 1, len(zs) - 1
    if ny != SHIPPED_N or nz != SHIPPED_N:
        refuse("GEOMETRY: shipped cross-plane counts %d x %d, registered %d x %d"
               % (ny, nz, SHIPPED_N, SHIPPED_N))
    for name, got_v, want in (("Lx", xs[-1] - xs[0], LX),
                              ("Ly", ys[-1] - ys[0], LY),
                              ("Lz", zs[-1] - zs[0], LZ)):
        if abs(got_v - want) > GEOM_RTOL * want:
            refuse("GEOMETRY: %s derived %.12g, registered %.12g" % (name, got_v, want))
    for name, u in (("y", ys), ("z", zs)):
        d = [u[i + 1] - u[i] for i in range(len(u) - 1)]
        ratios = [d[i + 1] / d[i] for i in range(len(d) - 1)]
        lo, hi = min(ratios), max(ratios)
        if abs(hi - lo) > GEOM_RTOL * abs(SHIPPED_Q):
            refuse("GEOMETRY: the shipped %s spacing is NOT a geometric "
                   "progression: per-cell ratio spans [%.12g, %.12g]. simpleGrading "
                   "cannot reproduce it and the dictionary would be a CHOICE, not a "
                   "derivation." % (name, lo, hi))
        mean = sum(ratios) / len(ratios)
        if abs(mean - SHIPPED_Q) > GEOM_RTOL * SHIPPED_Q:
            refuse("GEOMETRY: shipped %s per-cell ratio %.12g, registered %.12g"
                   % (name, mean, SHIPPED_Q))
        r_meas = d[-1] / d[0]
        if abs(r_meas - GRADING_R) > 1e-4 * GRADING_R:
            refuse("GEOMETRY: shipped %s total ratio %.12g, registered %.12g"
                   % (name, r_meas, GRADING_R))
    return {"nx": 1, "ny": ny, "nz": nz, "Lx": xs[-1] - xs[0],
            "Ly": ys[-1] - ys[0], "Lz": zs[-1] - zs[0],
            "q_per_cell": SHIPPED_Q, "R_total": GRADING_R, "npoints": len(pts)}


# --------------------------------------------------------------------------
# dictionary construction
# --------------------------------------------------------------------------
def make_blockmeshdict(n):
    if n < 2:
        refuse("BLOCKMESHDICT: N = %r is not a usable cross-plane count" % (n,))
    return BLOCKMESHDICT.format(lx="%.12g" % LX, ly="%.12g" % LY, lz="%.12g" % LZ,
                                n=int(n), r="%.15g" % GRADING_R)


def vertices_block(text):
    m = re.search(r"(?m)^vertices\n\(\n.*?^\);\n", text, re.S)
    if m is None:
        refuse("A blockMeshDict holds no vertices block")
    return m.group(0).encode()


def nonhex_bytes(text):
    return "\n".join(ln for ln in text.split("\n")
                     if not ln.lstrip().startswith("hex ")).encode()


def _match_block(text, keyword):
    """Return (open_brace_index, close_brace_index) of the FIRST `keyword {...}`."""
    m = re.search(r"(?m)^\s*%s\s*$" % re.escape(keyword), text)
    if m is None:
        m = re.search(r"(?m)^\s*%s\s*\{" % re.escape(keyword), text)
        if m is None:
            return None
        ob = text.index("{", m.start())
    else:
        ob = text.find("{", m.end())
        if ob < 0:
            return None
    depth = 0
    for i in range(ob, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return ob, i
    return None


def empty_residual_control(text):
    """Empty EVERY residualControl sub-dictionary, walking a cursor.

    The cursor is the point: a scanner that re-searches from position 0 after
    emptying one block finds that same (now empty) block again and returns,
    leaving every later block intact while claiming to have emptied them all.
    That defect was found and repaired in M1's stager; it is not repeated here.
    """
    done, rest = "", text
    while True:
        span = _match_block(rest, "residualControl")
        if span is None:
            return done + rest
        ob, cb = span
        body = rest[ob + 1:cb]
        if body.strip() == "":
            done += rest[:cb + 1]
            rest = rest[cb + 1:]
            continue
        done += rest[:ob] + "{\n    }"
        rest = rest[cb + 1:]


def residual_control_bodies(text):
    """Every residualControl body in the file, as a list of strings."""
    out, rest = [], text
    while True:
        span = _match_block(rest, "residualControl")
        if span is None:
            return out
        ob, cb = span
        out.append(rest[ob + 1:cb])
        rest = rest[cb + 1:]


def assert_all_empty(text):
    """REFUSE unless the text holds at least one residualControl and all are empty."""
    bodies = residual_control_bodies(text)
    if not bodies:
        refuse("FVSOLUTION: the text holds no residualControl block; the "
               "registered edit had nothing to act on and the scanner cannot be "
               "shown to have worked")
    for b in bodies:
        if b.strip() != "":
            refuse("FVSOLUTION: a residualControl block survived the edit: %r. A "
                   "solver-enforced early stop violates standing rule 4 (last time "
                   "== endTime) on EVERY row." % b.strip())
    return bodies


def make_fvsolution(src_text):
    out = empty_residual_control(src_text)
    assert_all_empty(out)
    return out


# --------------------------------------------------------------------------
# reconstruction control -- the control this rung exists to carry
# --------------------------------------------------------------------------
def reconstruction_control(src_case, work_dir):
    """Regenerate the SHIPPED mesh from the CONSTRUCTED dictionary and compare.

    The G1 substrate ships a blockMeshDict, so its family control could compare
    dictionary bytes.  G2's substrate ships none.  The equivalent -- and stronger
    -- evidence is that the constructed dictionary, at the shipped resolution,
    reproduces the shipped polyMesh.  A failure here means the geometry was not
    derived but chosen, and the stager REFUSES.
    """
    work = Path(work_dir)
    (work / "system").mkdir(parents=True, exist_ok=True)
    (work / "system/blockMeshDict").write_text(make_blockmeshdict(SHIPPED_N))
    (work / "system/controlDict").write_text(CONTROLDICT.format(libs=LIBS_LINE, end=1))
    shutil.copyfile(src_case / "system/fvSchemes", work / "system/fvSchemes")
    shutil.copyfile(src_case / "system/fvSolution", work / "system/fvSolution")
    proc = subprocess.run(["blockMesh", "-case", str(work)],
                          capture_output=True, text=True)
    (work / "log.blockMesh").write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0:
        refuse("RECONSTRUCTION: blockMesh rc=%d on the constructed dictionary at "
               "the shipped resolution; see %s"
               % (proc.returncode, work / "log.blockMesh"))
    got = read_points(work / "constant/polyMesh/points")
    want = read_points(src_case / "constant/polyMesh/points")
    if len(got) != len(want):
        refuse("RECONSTRUCTION: regenerated %d points, shipped mesh holds %d"
               % (len(got), len(want)))
    dev = max(max(abs(a - b) for a, b in zip(g, w)) for g, w in zip(got, want))
    if dev > RECON_ABSTOL_M:
        refuse("RECONSTRUCTION: max point deviation %.4e m exceeds the registered "
               "%.1e m. The constructed dictionary does NOT reproduce the shipped "
               "mesh, so the geometry is a CHOICE and this rung has no substrate."
               % (dev, RECON_ABSTOL_M))
    # patch identity, by type and face count, from the regenerated boundary file
    bnd = (work / "constant/polyMesh/boundary").read_text(errors="replace")
    for name, typ in (("inflow", "cyclic"), ("outflow", "cyclic"),
                      ("wallTop", "wall"), ("wallSide", "wall"),
                      ("symmetryBottom", "symmetry"), ("symmetrySide", "symmetry")):
        m = re.search(r"(?m)^\s*%s\s*\n\s*\{(.*?)\n\s*\}" % re.escape(name), bnd, re.S)
        if m is None:
            refuse("RECONSTRUCTION: the regenerated boundary has no patch %r" % name)
        if not re.search(r"type\s+%s\s*;" % typ, m.group(1)):
            refuse("RECONSTRUCTION: patch %r is not of the shipped type %r"
                   % (name, typ))
    return {"max_point_deviation_m": dev, "npoints": len(got),
            "shipped_npoints": len(want)}


# --------------------------------------------------------------------------
# staging
# --------------------------------------------------------------------------
def guard_dest(d):
    """Standing rule 4: never stage into a tree that may already hold an answer."""
    if d.exists():
        refuse("AGE-GUARD: %s already exists. A run is never staged into a tree "
               "that already holds an answer, and a re-stage over a previous one "
               "would make the age guard on 0/U unprovable. Remove it "
               "deliberately." % d)


def stage(src_case, dest_root, level, src_fvsol):
    name, n, ncells, end, _timeout = level
    d = dest_root / name
    guard_dest(d)
    (d / "system").mkdir(parents=True)
    (d / "constant").mkdir(parents=True)
    (d / "0").mkdir(parents=True)

    (d / "system/blockMeshDict").write_text(make_blockmeshdict(n))
    (d / "system/controlDict").write_text(CONTROLDICT.format(libs=LIBS_LINE, end=end))
    (d / "system/fvSolution").write_text(make_fvsolution(src_fvsol))
    for rel, want in COPY_VERBATIM.items():
        srcf = src_case / rel
        got = sha256_bytes(srcf.read_bytes())
        if got != want:
            refuse("SOURCE: %s sha256 %s, registered %s" % (srcf, got, want))
        shutil.copyfile(srcf, d / rel)

    for child in d.iterdir():
        if child.is_dir() and TIME_DIR.match(child.name) and child.name != "0":
            refuse("AGE-GUARD: %s holds a numeric time directory %s immediately "
                   "after staging" % (d, child.name))
    return d


def family_control(dest_root, src_fvsol):
    """Re-run, on the STAGED trees, every clause that makes them a family."""
    dicts, staged = {}, {}
    for name, n, ncells, end, _t in LEVELS:
        d = dest_root / name
        dicts[name] = (d / "system/blockMeshDict").read_text()
        staged[name] = d
    ref = LEVELS[0][0]
    for name, _n, _c, _e, _t in LEVELS[1:]:
        if vertices_block(dicts[name]) != vertices_block(dicts[ref]):
            refuse("FAMILY: the vertices block of %s differs from %s BYTE-WISE. "
                   "This is the alpha_10_9000_{2024,3036,4048} shape: three "
                   "directories that look like a refinement family and are three "
                   "GEOMETRIES (measured: nCells 15600 for all three, three "
                   "different vertices sha256)." % (name, ref))
        if nonhex_bytes(dicts[name]) != nonhex_bytes(dicts[ref]):
            refuse("FAMILY: %s differs from %s outside the single hex block line"
                   % (name, ref))
    counts = [c for _n, _N, c, _e, _t in LEVELS]
    if len(set(counts)) != 3:
        refuse("FAMILY: the three registered cell counts %r are not distinct" % (counts,))
    if counts[1] != 4 * counts[0] or counts[2] != 4 * counts[1]:
        refuse("FAMILY: registered cell counts %r are not in the 1:4:16 ratio"
               % (counts,))
    # every other staged file byte-identical across the three levels
    common = list(COPY_VERBATIM) + ["system/fvSolution"]
    for rel in common:
        digs = {n: sha256_bytes((staged[n] / rel).read_bytes()) for n in staged}
        if len(set(digs.values())) != 1:
            refuse("FAMILY: %s is not byte-identical across the three levels: %r"
                   % (rel, digs))
    # the controlDict differs ONLY in endTime and writeInterval
    def mask(t):
        t = re.sub(r"endTime\s+\d+;", "endTime <E>;", t)
        return re.sub(r"writeInterval\s+\d+;", "writeInterval <E>;", t)
    cds = {n: mask((staged[n] / "system/controlDict").read_text()) for n in staged}
    if len(set(cds.values())) != 1:
        refuse("FAMILY: the three controlDicts differ outside endTime/writeInterval")
    for name, _N, _c, end, _t in LEVELS:
        cd = (staged[name] / "system/controlDict").read_text()
        for key in ("endTime", "writeInterval"):
            m = re.search(r"%s\s+(\d+);" % key, cd)
            if m is None or int(m.group(1)) != end:
                refuse("FAMILY: %s controlDict %s is %s, registered %d"
                       % (name, key, m.group(1) if m else "absent", end))
    if LIBS_LINE not in (staged[ref] / "system/controlDict").read_text():
        refuse("FAMILY: the shipped libs line is absent from the staged "
               "controlDict; a libs entry is never deleted to tidy a case "
               "(standing rule 14)")
    return counts


def write_manifest(dest_root, src_case, geom, recon):
    man = {
        "rung": "G2_grid_triple_duct",
        "prereg_commit": "PENDING_SUPERVISOR_FREEZE",
        "source_case": str(src_case),
        "run_root": str(dest_root),
        "derived_geometry": geom,
        "reconstruction_control": recon,
        "levels": [{"level": n, "N_per_direction": N, "nCells_registered": c,
                    "endTime": e, "timeout_s": t} for n, N, c, e, t in LEVELS],
        "grading_total_ratio": GRADING_R,
        "grading_per_cell_ratio": SHIPPED_Q,
        "staged_file_sha256": {},
    }
    for name, _N, _c, _e, _t in LEVELS:
        d = dest_root / name
        man["staged_file_sha256"][name] = {
            rel: sha256_bytes((d / rel).read_bytes())
            for rel in sorted(list(COPY_VERBATIM) +
                              ["system/fvSolution", "system/controlDict",
                               "system/blockMeshDict"])
        }
    p = dest_root / "STAGING_MANIFEST_G2.json"
    p.write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
    return p


def build(src_case=SRC_CASE, dest_root=DEST_ROOT):
    no_assert_control()
    src_case, dest_root = Path(src_case), Path(dest_root)
    if not src_case.is_dir():
        refuse("SOURCE: %s is not a directory" % src_case)
    geom = derive_geometry(src_case)
    src_fvsol_bytes = (src_case / "system/fvSolution").read_bytes()
    got = sha256_bytes(src_fvsol_bytes)
    if got != SRC_FVSOLUTION_SHA:
        refuse("SOURCE: system/fvSolution sha256 %s, registered %s"
               % (got, SRC_FVSOLUTION_SHA))
    src_fvsol = src_fvsol_bytes.decode()

    dest_root.mkdir(parents=True, exist_ok=True)
    recon_dir = dest_root / "_recon_shipped_N"
    if recon_dir.exists():
        refuse("AGE-GUARD: %s already exists" % recon_dir)
    recon = reconstruction_control(src_case, recon_dir)

    for level in LEVELS:
        stage(src_case, dest_root, level, src_fvsol)
    counts = family_control(dest_root, src_fvsol)
    man = write_manifest(dest_root, src_case, geom, recon)

    print("G2 stager")
    print("  source          : %s" % src_case)
    print("  run root        : %s" % dest_root)
    print("  derived geometry: %g x %g x %g m, %d x %d cross-plane cells shipped"
          % (geom["Lx"], geom["Ly"], geom["Lz"], geom["ny"], geom["nz"]))
    print("  grading         : per-cell %.12g, total %.15g (simpleGrading)"
          % (SHIPPED_Q, GRADING_R))
    print("  RECONSTRUCTION  : %d points regenerated, max deviation from the "
          "shipped mesh %.3e m (ceiling %.0e m)"
          % (recon["npoints"], recon["max_point_deviation_m"], RECON_ABSTOL_M))
    print("  levels staged   : %s, registered cells %r" %
          ([n for n, _N, _c, _e, _t in LEVELS], counts))
    print("  manifest        : %s" % man)
    return 0


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def _must_refuse(label, fn):
    try:
        fn()
    except Refusal as e:
        print("  REFUSED as registered: %s\n      %s" % (label, str(e).split("\n")[0]))
        return True
    print("  CONTROL DID NOT FIRE: %s" % label)
    return False


def selftest():
    ok = True
    print("G2 stager selftest")
    planted, own = no_assert_control()
    print("  L-332: counter saw %d planted assert, this module holds %d"
          % (planted, own))

    print("[residualControl scanner]")
    two = ("SIMPLE\n{\n    residualControl\n    {\n        k 5e-6;\n    }\n}\n"
           "PIMPLE\n{\n    residualControl\n    {\n        omega 1e-10;\n    }\n}\n")
    emptied = empty_residual_control(two)
    bodies = residual_control_bodies(emptied)
    if len(bodies) != 2 or any(b.strip() for b in bodies):
        print("  FAIL: the cursor scanner left %r" % (bodies,))
        ok = False
    else:
        print("  two blocks in one file: BOTH emptied (the cursor defect is absent)")
    ok &= _must_refuse(
        "a residualControl body that survived the edit",
        lambda: assert_all_empty(
            "SIMPLE\n{\n    residualControl\n    {\n        k 5e-6;\n    }\n}\n"))
    ok &= _must_refuse("a source with NO residualControl at all",
                       lambda: make_fvsolution("SIMPLE\n{\n    pRefCell 0;\n}\n"))
    if assert_all_empty(
            "SIMPLE\n{\n    residualControl\n    {\n    }\n}\n") != ["\n    "]:
        print("  NOTE: the emptied-body reading is %r"
              % assert_all_empty("SIMPLE\n{\n    residualControl\n    {\n    }\n}\n"))
    print("  an already-empty residualControl PASSES (the control is not a "
          "constant refusal)")

    print("[geometry derivation]")
    ok &= _must_refuse("a source whose points sha256 has moved",
                       lambda: derive_geometry(Path(tempfile.mkdtemp())))

    print("[blockMeshDict construction]")
    a, b = make_blockmeshdict(32), make_blockmeshdict(64)
    if vertices_block(a) != vertices_block(b):
        print("  FAIL: two levels' vertices blocks differ")
        ok = False
    else:
        print("  vertices block byte-identical between N=32 and N=64")
    if nonhex_bytes(a) != nonhex_bytes(b):
        print("  FAIL: two levels differ outside the hex line")
        ok = False
    else:
        print("  all bytes outside the single hex line byte-identical")
    if a == b:
        print("  FAIL: two different resolutions produced the same dictionary")
        ok = False
    else:
        print("  the hex line, and only the hex line, differs")
    ok &= _must_refuse("N < 2", lambda: make_blockmeshdict(1))

    print("[age guard]")
    tmp = Path(tempfile.mkdtemp())
    (tmp / "L1").mkdir()
    ok &= _must_refuse("staging over an existing level tree",
                       lambda: guard_dest(tmp / "L1"))
    shutil.rmtree(tmp, ignore_errors=True)

    print("[family control, mutated]")
    tmp = Path(tempfile.mkdtemp())
    for name, n, _c, end, _t in LEVELS:
        d = tmp / name
        (d / "system").mkdir(parents=True)
        (d / "constant").mkdir(parents=True)
        (d / "0").mkdir(parents=True)
        (d / "system/blockMeshDict").write_text(make_blockmeshdict(n))
        (d / "system/controlDict").write_text(
            CONTROLDICT.format(libs=LIBS_LINE, end=end))
        (d / "system/fvSolution").write_text("SIMPLE\n{\n    residualControl\n    {\n    }\n}\n")
        for rel in COPY_VERBATIM:
            (d / rel).write_text("identical\n")
    if family_control(tmp, "") != [c for _n, _N, c, _e, _t in LEVELS]:
        print("  FAIL: the family control rejected a clean family")
        ok = False
    else:
        print("  a clean staged family PASSES the family control")
    (tmp / "L2/system/blockMeshDict").write_text(
        make_blockmeshdict(64).replace("(0 0 0)", "(0 0 1e-09)"))
    ok &= _must_refuse("a level whose vertices block was edited",
                       lambda: family_control(tmp, ""))
    (tmp / "L2/system/blockMeshDict").write_text(make_blockmeshdict(64))
    (tmp / "L3/0/k").write_text("different\n")
    ok &= _must_refuse("a level whose 0/k differs from its siblings",
                       lambda: family_control(tmp, ""))
    (tmp / "L3/0/k").write_text("identical\n")
    (tmp / "L1/system/controlDict").write_text(
        CONTROLDICT.format(libs=LIBS_LINE, end=LEVELS[0][3] + 1))
    ok &= _must_refuse("a level staged at an endTime the registry does not carry",
                       lambda: family_control(tmp, ""))
    for name, _N, _c, end, _t in LEVELS:
        (tmp / name / "system/controlDict").write_text(
            CONTROLDICT.format(libs="", end=end))
    ok &= _must_refuse("the shipped libs line deleted from EVERY staged "
                       "controlDict (rule 14)",
                       lambda: family_control(tmp, ""))
    shutil.rmtree(tmp, ignore_errors=True)

    print("SELFTEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    return build()


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        sys.exit(2)
