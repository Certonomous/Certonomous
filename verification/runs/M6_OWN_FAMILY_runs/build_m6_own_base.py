#!/usr/bin/env python3
"""
M6 OWN FAMILY -- base-level own-mesh generator + admissibility screen.

Sanaa's M6 third-direction ruling (etc/sessions/2026-09-04T1500Z): the DPW/committee
grids FAIL both hard mesh gates at every level and cannot carry a credential GCI, and
the structured PLOT3D route (M6I) FAILS at 86-87 deg non-orthogonality on all three
levels. The THIRD direction is the lab's OWN volume mesh: a pyHyp hyperbolic extrusion
off a held M6 surface. On this box that route already produced a gate-CLEARING mesh --
RUNG1_M6_R2 level "L2", 71,760 cells, checkMesh max non-orthogonality 61.46 deg, max
skewness 2.06 (< the 70 / 4 hard gates). RUNG1's L1 (fine surface, N=93) over-resolved
16x and its pyHyp march did not complete; RUNG1's L3 (vcoarse surface, N=24) degenerated
(negative-volume cells, non-orth 109 deg). The proven sweet spot is the MEDIUM level.

This driver REPRODUCES that proven recipe as the standing M6 own-family BASE level, in a
clean own run root, with a fresh generation and a measured checkMesh screen. It is one
level only -- the base that CLEARS the gates is the deliverable; the finer/coarser levels
of a future Roache triple are laid out in the registration, not generated here.

NO SOLVER RUNS. Mesh generation + checkMesh admissibility screen only.
NO BARE assert (python3 -O deletes asserts, L-332): every refusal raises.
Recipe, docker invocation and readers are lifted verbatim-in-shape from the proven
driver cases/RUNG1_M6/build_r2_triple.py.
"""
import hashlib, json, os, re, shutil, subprocess, sys, time

REPO = "/home/ubuntu/Certonomous"
RR   = f"{REPO}/verification/runs/M6_OWN_FAMILY_runs"
IMG  = "dafoam-idwarp-rot:v1"
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# The PROVEN gate-clearing configuration (RUNG1_M6_R2 "L2"): pyHyp N=47, s0=2e-4,
# marchDist=50, off the coarse (1560-face) M6 surface. Named here as the own-family
# medium base level "L2".
LEVEL_NAME = "L2"
SURF = "/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/surfaceMesh.cgns"
N    = 47
S0   = 2.0e-04
MARCH_DIST = 50.0
EXPECT_CELLS = 71760
SYM_TOL = 1e-9

# Hard gates read from docs/standards/MESH_STANDARD.md sec 3.1 / 3.2 (byte-identical
# to the thresholds every M6 mesh screen on this box has used).
GATE_NONORTH = 70.0
GATE_SKEW    = 4.0

# Planted-nonzero control (rule 3): a preserved BROKEN checkMesh log whose breach the
# reader MUST see, else the reader is blind and this screen is void.
CONTROL_BROKEN_LOG = f"{REPO}/verification/runs/RUNG1_M6_R2_runs/L3/log.checkMesh"

DECK = """from pyhyp import pyHyp
options = {{
    "inputFile": "surfaceMesh.cgns",
    "fileType": "CGNS",
    "unattachedEdgesAreSymmetry": True,
    "outerFaceBC": "farfield",
    "autoConnect": True,
    "BC": {{}},
    "families": "wall",
    "N": {N},
    "s0": {s0},
    "marchDist": {md},
    "ps0": -1.0,
    "pGridRatio": -1.0,
    "cMax": 0.1,
    "epsE": 1.0,
    "epsI": 2.0,
    "theta": 3.0,
    "volCoef": 0.25,
    "volBlend": 0.0005,
    "volSmoothIter": 100,
    "kspreltol": 1e-4,
}}
hyp = pyHyp(options=options)
hyp.run()
hyp.writePlot3D("volumeMesh.xyz")
"""


def die(m): raise SystemExit(f"STOP: {m}")
def say(m): print(f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {m}", flush=True)
def sh(cmd, cwd=None, timeout=None):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True, timeout=timeout)
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def block(pm, fn):
    t = open(os.path.join(pm, fn)).read()
    t = t[t.index("// * * *"):]
    m = re.search(r"^\s*(\d+)\s*\n\(", t, re.M)
    if not m: die(f"cannot find the list header in {fn}")
    return t[m.end():t.index("\n)", m.end())]


def read_checkmesh(log):
    t = open(log).read()
    def g(p):
        m = re.search(p, t, re.M); return m.group(1) if m else None
    return {
        "cells": g(r"^\s*cells:\s*(\d+)"),
        "points": g(r"^\s*points:\s*(\d+)"),
        "max_non_orthogonality": g(r"Mesh non-orthogonality Max:\s*([0-9.eE+-]*[0-9])"),
        "avg_non_orthogonality": g(r"Max:\s*[0-9.eE+-]*[0-9]\s*average:\s*([0-9.eE+-]*[0-9])"),
        "severe_non_ortho_faces": g(r"non-orthogonal \(> 70 degrees\) faces:\s*(\d+)"),
        "max_skewness": g(r"Max skewness\s*[=:]\s*([0-9.eE+-]*[0-9])"),
        "max_aspect_ratio": (g(r"Max aspect ratio\s*=\s*([0-9.eE+-]*[0-9])")
                             or g(r"Max aspect ratio:\s*([0-9.eE+-]*[0-9])")),
        # broken meshes NEVER print "Min volume ="; they print the negative form.
        "min_cell_volume": (g(r"Min volume\s*=\s*([0-9.eE+-]*[0-9])")
                            or g(r"Minimum negative volume:\s*([0-9.eE+-]*[0-9])")),
        "negative_volume_cells": g(r"Number of negative volume cells:\s*(\d+)"),
        "face_orientation_errors": g(r"Error in face pyramids:\s*(\d+) faces"),
        "regions": g(r"Number of regions:\s*(\d+)"),
        "bounding_box": g(r"Overall domain bounding box (.*)$"),
        "mesh_ok_line": ("Mesh OK." in t),
        "failed_checks_line": g(r"Failed (\d+) mesh checks"),
    }


def planted_control():
    """Rule 3: prove the reader can SEE a non-zero (a breach) before trusting a clean read."""
    if not os.path.isfile(CONTROL_BROKEN_LOG):
        die(f"planted control log ABSENT: {CONTROL_BROKEN_LOG}; screen void")
    d = read_checkmesh(CONTROL_BROKEN_LOG)
    no = float(d["max_non_orthogonality"]) if d["max_non_orthogonality"] else None
    nv = int(d["negative_volume_cells"]) if d["negative_volume_cells"] else None
    say(f"PLANTED CONTROL (RUNG1 L3 broken log): reader sees nonOrth={no} negVolCells={nv}")
    if no is None or no <= GATE_NONORTH:
        die(f"planted control FAILED: reader did not see the >70 breach in {CONTROL_BROKEN_LOG} "
            f"(read nonOrth={no}). The reader is blind; screen void.")
    if nv is None or nv < 1:
        die(f"planted control FAILED: reader did not see the negative-volume cells in the "
            f"broken log (read {nv}). The reader is blind; screen void.")
    return {"control_log": CONTROL_BROKEN_LOG, "seen_max_non_orthogonality": no,
            "seen_negative_volume_cells": nv, "control_PASSES": True}


def classify_and_patch(case):
    import numpy as np
    pm = os.path.join(case, "constant", "polyMesh")
    pts = np.fromstring(block(pm, "points").replace("(", " ").replace(")", " "), sep=" ").reshape(-1, 3)
    faces = [[int(x) for x in ln.strip().split("(", 1)[1].rstrip(")").split()]
             for ln in block(pm, "faces").strip().split("\n") if ln.strip()]
    m = re.search(r"nInternalFaces:(\d+)", open(os.path.join(pm, "owner")).read())
    if not m: die("owner carries no nInternalFaces note")
    n_int = int(m.group(1))
    cen = np.array([pts[f].mean(axis=0) for f in faces[n_int:]])
    r = np.linalg.norm(cen, axis=1)
    sym = np.abs(cen[:, 2]) < SYM_TOL
    off = ~sym
    lo = np.sort(r[off]); gaps = np.diff(lo); i = int(np.argmax(gaps))
    cut = (lo[i] + lo[i + 1]) / 2.0
    cls = np.where(sym, 0, np.where(r <= cut, 1, 2))
    ev = {"n_boundary_faces": int(len(cen)), "symmetry_faces": int((cls == 0).sum()),
          "wall_faces": int((cls == 1).sum()), "farfield_faces": int((cls == 2).sum()),
          "gap_width": float(gaps[i])}
    if ev["wall_faces"] != ev["farfield_faces"]:
        die(f"wall {ev['wall_faces']} != farfield {ev['farfield_faces']}: split wrong.")
    if ev["gap_width"] < 1.0:
        die(f"radius gap only {ev['gap_width']:.6f}; split ambiguous.")
    sets = os.path.join(pm, "sets"); os.makedirs(sets, exist_ok=True)
    for name, code in (("wingFaces", 1), ("symmetryFaces", 0), ("farfieldFaces", 2)):
        idx = np.where(cls == code)[0]
        with open(os.path.join(sets, name), "w") as f:
            f.write("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                    "    class       faceSet;\n    location    \"constant/polyMesh/sets\";\n"
                    f"    object      {name};\n}}\n\n{len(idx)}\n(\n")
            f.write("\n".join(str(int(x) + n_int) for x in idx)); f.write("\n)\n")
    with open(os.path.join(case, "system", "createPatchDict"), "w") as f:
        f.write("FoamFile{version 2.0;format ascii;class dictionary;object createPatchDict;}\n"
                "pointSync false;\npatches\n(\n")
        for nm, ty in (("wing", "wall"), ("symmetry", "symmetry"), ("farfield", "patch")):
            f.write(f"    {{ name {nm}; patchInfo {{ type {ty}; }} constructFrom set; set {nm}Faces; }}\n")
        f.write(");\n")
    r2 = sh(f"source {FOAM} >/dev/null 2>&1; createPatch -overwrite > log.createPatch 2>&1", cwd=case)
    if r2.returncode != 0: die(f"createPatch rc={r2.returncode} in {case}")
    return ev


def main():
    t0 = time.time()
    ctrl = planted_control()
    c = f"{RR}/{LEVEL_NAME}"; w = f"{c}/work"; case = f"{c}/case"
    os.makedirs(f"{case}/system", exist_ok=True); os.makedirs(w, exist_ok=True)
    if not os.path.isfile(SURF): die(f"surface ABSENT: {SURF}")
    shutil.copyfile(SURF, f"{w}/surfaceMesh.cgns")
    surf_sha = sha(f"{w}/surfaceMesh.cgns")
    with open(f"{w}/genWingMesh.py", "w") as f:
        f.write(DECK.format(N=N, s0=S0, md=MARCH_DIST))
    for fn, body in (
        ("controlDict", "application none;\nstartFrom startTime;\nstartTime 0;\nstopAt endTime;\n"
                        "endTime 1;\ndeltaT 1;\nwriteControl timeStep;\nwriteInterval 1;\n"),
        ("fvSchemes", "ddtSchemes{default steadyState;}\ngradSchemes{default Gauss linear;}\n"
                      "divSchemes{default none;}\nlaplacianSchemes{default Gauss linear limited corrected 0.5;}\n"
                      "snGradSchemes{default limited corrected 0.5;}\n"),
        ("fvSolution", "solvers{}\n")):
        with open(f"{case}/system/{fn}", "w") as f:
            f.write(f"FoamFile{{version 2.0;format ascii;class dictionary;object {fn};}}\n{body}")

    out = {"level": LEVEL_NAME, "surface_cgns": SURF, "surface_sha256": surf_sha,
           "pyhyp_N": N, "cell_layers": N - 1, "s0_REQUESTED_NOT_MEASURED": S0,
           "marchDist": MARCH_DIST, "gates": {"non_orth": GATE_NONORTH, "skew": GATE_SKEW},
           "planted_control": ctrl, "cost": []}

    say(f"{LEVEL_NAME}: pyHyp N={N} s0={S0} marchDist={MARCH_DIST} surface={os.path.basename(SURF)}")
    os.chmod(w, 0o777)
    s = time.time()
    r = sh(f"sg docker -c \"docker run --rm -u 1002:1002 -v '{w}':/home/dafoamuser/mount "
           f"-w /home/dafoamuser/mount {IMG} bash -c 'set +u; "
           f"source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; python genWingMesh.py'\" "
           f"> {c}/log.pyhyp 2>&1", timeout=1200)
    wall = time.time() - s
    out["cost"].append({"stage": "pyhyp", "wall_s": round(wall, 1), "ranks": 1,
                        "core_min": round(wall / 60, 4), "rc": r.returncode})
    if r.returncode != 0 or not os.path.isfile(f"{w}/volumeMesh.xyz"):
        die(f"pyHyp rc={r.returncode}; volumeMesh.xyz present={os.path.isfile(f'{w}/volumeMesh.xyz')}; "
            f"see {c}/log.pyhyp")

    s = time.time()
    r = sh(f"source {FOAM} >/dev/null 2>&1; plot3dToFoam -noBlank {w}/volumeMesh.xyz "
           f"> log.plot3dToFoam 2>&1", cwd=case, timeout=600)
    out["cost"].append({"stage": "plot3dToFoam", "wall_s": round(time.time() - s, 1), "ranks": 1,
                        "core_min": round((time.time() - s) / 60, 4), "rc": r.returncode})
    if r.returncode != 0: die(f"plot3dToFoam rc={r.returncode}")

    ev = classify_and_patch(case)
    s = time.time()
    r = sh(f"source {FOAM} >/dev/null 2>&1; checkMesh > log.checkMesh 2>&1", cwd=case, timeout=600)
    out["cost"].append({"stage": "checkMesh", "wall_s": round(time.time() - s, 1), "ranks": 1,
                        "core_min": round((time.time() - s) / 60, 4), "rc": r.returncode})

    d = read_checkmesh(f"{case}/log.checkMesh")
    d.update({"classification_evidence": ev,
              "points_sha256": sha(f"{case}/constant/polyMesh/points"),
              "cells_expected": EXPECT_CELLS,
              "cells_match_expected": (d["cells"] is not None and int(d["cells"]) == EXPECT_CELLS),
              "checkMesh_log": f"{case}/log.checkMesh"})

    no = float(d["max_non_orthogonality"]) if d["max_non_orthogonality"] else None
    sk = float(d["max_skewness"]) if d["max_skewness"] else None
    nv = int(d["negative_volume_cells"]) if d["negative_volume_cells"] else 0
    clears = (no is not None and no < GATE_NONORTH and sk is not None and sk < GATE_SKEW and nv == 0)
    d["screen_clears_hard_gates"] = bool(clears)
    d["screen_detail"] = {"max_non_orthogonality": no, "gate_non_orth": GATE_NONORTH,
                          "non_orth_clears": (no is not None and no < GATE_NONORTH),
                          "max_skewness": sk, "gate_skew": GATE_SKEW,
                          "skew_clears": (sk is not None and sk < GATE_SKEW),
                          "negative_volume_cells": nv}
    out["level_result"] = d
    total_core_min = round(sum(x["core_min"] for x in out["cost"]), 4)
    out["total_core_min_generation"] = total_core_min
    out["generated_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(f"{RR}/{LEVEL_NAME}/RESULT.json", "w") as f:
        json.dump(out, f, indent=2)
    say(f"{LEVEL_NAME}: cells={d['cells']} (expect {EXPECT_CELLS}, match={d['cells_match_expected']}) "
        f"nonOrth={no} skew={sk} AR={d['max_aspect_ratio']} negVol={nv} "
        f"CLEARS_HARD_GATES={clears} total={total_core_min} core-min")
    print("SCREEN_CLEARS_HARD_GATES:", clears)


if __name__ == "__main__":
    main()
