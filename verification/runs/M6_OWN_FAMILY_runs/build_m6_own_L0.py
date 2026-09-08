#!/usr/bin/env python3
"""M6 OWN FAMILY -- build the FINEST level L0, the fine-side third level of the Roache
triple {L2, L1, L0} (verification RULING b44a0376, PATH B: coarsening is inadmissible off a
390-face M6 surface, so the observed-order triple must land on the clean FINE side).

The two lower levels are already built and CLEAR both hard gates:
    L2 base : 71,760 cells, non-orth 61.4646 deg, skew 2.05915, 0 neg-vol
    L1 fine : 574,080 cells (=8x L2), non-orth 60.8639 deg, skew 1.44118, 0 neg-vol
This driver adds L0 = cgns_utils REFINE of the *L1 surface* (24,960 faces = 4x L1),
marched with pyHyp N=185 (184 layers, =2x L1), s0=5.0e-05 (halved from L1's 1.0e-04),
marchDist=50.0 (UNIFORM across the family -- similarity of the outer boundary). Predicted
~4,592,640 cells = exactly 8x L1, so cell ratios across the family are 8.00 and 8.00.

Non-orthogonality falls MONOTONICALLY with refinement on this family (L2 61.46 -> L1 60.86),
so L0 is PREDICTED admissible -- but predicted is not measured: this driver measures it and
REFUSES to force a pass (T25). If L0 does NOT clear the hard gates it is recorded as a
MEASURED finding and the triple construction returns to the supervisor/chief.

MESH GENERATION + checkMesh ADMISSIBILITY SCREEN ONLY. NO SOLVER RUNS.

RECIPE, DOCKER INVOCATION AND READERS ARE LIFTED VERBATIM-IN-SHAPE from the proven sibling
driver build_m6_own_ends.py (which built L1 and screened L3), itself lifted from the frozen
cases/RUNG1_M6/build_r2_triple.py. NO BARE assert (python3 -O deletes asserts, L-332): every
refusal raises.
"""
import hashlib, json, os, re, shutil, subprocess, sys, time

REPO = "/home/ubuntu/Certonomous"
RR   = f"{REPO}/verification/runs/M6_OWN_FAMILY_runs"
IMG  = "dafoam-idwarp-rot:v1"
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# L0 is the next 2:1 refinement of the FINE level L1. Its surface is cgns_utils refine of the
# PROVEN L1 surface (6,240 faces, sha 915d2537..., itself a refine of the L2 parent), so the
# whole family {L2,L1,L0} shares one geometric ancestor and is exactly nested.
L1_SURF = f"{RR}/L1/surface/surfaceMesh.cgns"
MARCH_DIST = 50.0            # UNIFORM across the triple (similarity of the outer boundary)
SYM_TOL = 1e-9
GATE_NONORTH = 70.0          # docs/standards/MESH_STANDARD.md sec 3.1
GATE_SKEW    = 4.0           # docs/standards/MESH_STANDARD.md sec 3.2

# Planted-nonzero control (rule 3): the SAME preserved broken log the base/ends screens used.
CONTROL_BROKEN_LOG = f"{REPO}/verification/runs/RUNG1_M6_R2_runs/L3/log.checkMesh"

# Mesh-gen cost cap (rule 12). L1 (574k, N=93) pyHyp was 197.3 s; L0 is 8x cells / 2x layers /
# 4x surface faces. Generous single-rank mesh-gen cap; an overrun STOPS (does NOT get a new
# budget). This is the MESH-GEN cap only; the SOLVE cap is a separate registered figure.
CAP_WALL_S = 5400            # 90.0 core-min hard cap for the L0 mesh-gen + screen.

# L0 level definition: refine of L1, N=185 (184 layers), s0 halved to 5.0e-05.
LEVEL = ("L0", "refine", 185, 5.0e-05, 4592640, 24960)

NOMINAL = {"tag": "nominal", "cMax": 0.1, "epsE": 1.0, "epsI": 2.0,
           "volSmoothIter": 100, "volBlend": 0.0005}

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
    "cMax": {cMax},
    "epsE": {epsE},
    "epsI": {epsI},
    "theta": 3.0,
    "volCoef": 0.25,
    "volBlend": {volBlend},
    "volSmoothIter": {volSmoothIter},
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
    """Rule 3: prove the reader can SEE a breach before trusting a clean read."""
    if not os.path.isfile(CONTROL_BROKEN_LOG):
        die(f"planted control log ABSENT: {CONTROL_BROKEN_LOG}; screen void")
    d = read_checkmesh(CONTROL_BROKEN_LOG)
    no = float(d["max_non_orthogonality"]) if d["max_non_orthogonality"] else None
    nv = int(d["negative_volume_cells"]) if d["negative_volume_cells"] else None
    say(f"PLANTED CONTROL (RUNG1 L3 broken log): reader sees nonOrth={no} negVolCells={nv}")
    if no is None or no <= GATE_NONORTH:
        die(f"planted control FAILED: reader did not see the >70 breach (read {no}); screen void")
    if nv is None or nv < 1:
        die(f"planted control FAILED: reader did not see negative-volume cells (read {nv}); screen void")
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


def write_system(case):
    os.makedirs(f"{case}/system", exist_ok=True)
    for fn, body in (
        ("controlDict", "application none;\nstartFrom startTime;\nstartTime 0;\nstopAt endTime;\n"
                        "endTime 1;\ndeltaT 1;\nwriteControl timeStep;\nwriteInterval 1;\n"),
        ("fvSchemes", "ddtSchemes{default steadyState;}\ngradSchemes{default Gauss linear;}\n"
                      "divSchemes{default none;}\nlaplacianSchemes{default Gauss linear limited corrected 0.5;}\n"
                      "snGradSchemes{default limited corrected 0.5;}\n"),
        ("fvSolution", "solvers{}\n")):
        with open(f"{case}/system/{fn}", "w") as f:
            f.write(f"FoamFile{{version 2.0;format ascii;class dictionary;object {fn};}}\n{body}")


def run_pyhyp(workdir, surf_path, N, s0, recipe, log_path, timeout):
    """Copy surface in, write deck, run pyHyp in the container. Returns (rc, wall_s)."""
    os.makedirs(workdir, exist_ok=True)
    shutil.copyfile(surf_path, f"{workdir}/surfaceMesh.cgns")
    with open(f"{workdir}/genWingMesh.py", "w") as f:
        f.write(DECK.format(N=N, s0=s0, md=MARCH_DIST, cMax=recipe["cMax"], epsE=recipe["epsE"],
                            epsI=recipe["epsI"], volBlend=recipe["volBlend"],
                            volSmoothIter=recipe["volSmoothIter"]))
    os.chmod(workdir, 0o777)
    s = time.time()
    r = sh(f"sg docker -c \"docker run --rm -u 1002:1002 -v '{workdir}':/home/dafoamuser/mount "
           f"-w /home/dafoamuser/mount {IMG} bash -c 'set +u; "
           f"source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; python genWingMesh.py'\" "
           f"> {log_path} 2>&1", timeout=timeout)
    return r.returncode, round(time.time() - s, 1)


def make_surface(op, out_path, tag_log):
    """cgns_utils refine|coarsen of the proven L1 surface into out_path. Returns sha."""
    d = os.path.dirname(out_path)
    os.makedirs(d, exist_ok=True); os.chmod(d, 0o777)
    shutil.copyfile(L1_SURF, f"{d}/_L1parent.cgns")
    r = sh(f"sg docker -c \"docker run --rm -u 1002:1002 -v '{d}':/home/dafoamuser/mount "
           f"-w /home/dafoamuser/mount {IMG} bash -c 'set +u; "
           f"source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; "
           f"cgns_utils {op} _L1parent.cgns {os.path.basename(out_path)}'\" > {tag_log} 2>&1",
           timeout=600)
    if r.returncode != 0 or not os.path.isfile(out_path):
        die(f"cgns_utils {op} rc={r.returncode}; out present={os.path.isfile(out_path)}; see {tag_log}")
    return sha(out_path)


def screen_case_for(case, workdir, expect_cells, expect_faces):
    """plot3dToFoam -> createPatch -> checkMesh, then read the named maxima (never a verdict string)."""
    s = time.time()
    r = sh(f"source {FOAM} >/dev/null 2>&1; plot3dToFoam -noBlank {workdir}/volumeMesh.xyz "
           f"> log.plot3dToFoam 2>&1", cwd=case, timeout=3600)
    t_p3d = round(time.time() - s, 1)
    if r.returncode != 0: die(f"plot3dToFoam rc={r.returncode} in {case}")
    ev = classify_and_patch(case)
    s = time.time()
    sh(f"source {FOAM} >/dev/null 2>&1; checkMesh > log.checkMesh 2>&1", cwd=case, timeout=3600)
    t_cm = round(time.time() - s, 1)
    d = read_checkmesh(f"{case}/log.checkMesh")
    no = float(d["max_non_orthogonality"]) if d["max_non_orthogonality"] else None
    sk = float(d["max_skewness"]) if d["max_skewness"] else None
    nv = int(d["negative_volume_cells"]) if d["negative_volume_cells"] else 0
    clears = (no is not None and no < GATE_NONORTH and sk is not None and sk < GATE_SKEW and nv == 0)
    d.update({
        "classification_evidence": ev, "points_sha256": sha(f"{case}/constant/polyMesh/points"),
        "cells_expected": expect_cells,
        "cells_match_expected": (d["cells"] is not None and int(d["cells"]) == expect_cells),
        "surface_faces_expected": expect_faces, "surface_faces_measured": ev["wall_faces"],
        "surface_faces_match": ev["wall_faces"] == expect_faces,
        "checkMesh_log": f"{case}/log.checkMesh", "screen_clears_hard_gates": bool(clears),
        "screen_detail": {"max_non_orthogonality": no, "gate_non_orth": GATE_NONORTH,
                          "non_orth_clears": (no is not None and no < GATE_NONORTH),
                          "max_skewness": sk, "gate_skew": GATE_SKEW,
                          "skew_clears": (sk is not None and sk < GATE_SKEW),
                          "negative_volume_cells": nv},
        "screen_cost": [{"stage": "plot3dToFoam", "wall_s": t_p3d, "core_min": round(t_p3d/60, 4)},
                        {"stage": "checkMesh", "wall_s": t_cm, "core_min": round(t_cm/60, 4)}],
    })
    return d


def build_level(name, op, N, s0, expect_cells, expect_faces, ctrl, t0):
    c = f"{RR}/{name}"
    if os.path.isdir(c):
        die(f"{c} already exists; refusing to clobber (inspect, do not overwrite).")
    os.makedirs(c); os.chmod(c, 0o777)
    surf_path = f"{c}/surface/surfaceMesh.cgns"
    say(f"{name}: cgns_utils {op} of proven L1 surface -> {expect_faces} faces")
    surf_sha = make_surface(op, surf_path, f"{c}/log.cgns_utils")
    L1_parent_sha = sha(L1_SURF)
    out = {"level": name, "family_parent_surface": L1_SURF, "family_parent_sha256": L1_parent_sha,
           "surface_op": op, "surface_cgns": surf_path, "surface_sha256": surf_sha,
           "pyhyp_N": N, "cell_layers": N - 1, "s0_REQUESTED_NOT_MEASURED": s0,
           "marchDist": MARCH_DIST, "gates": {"non_orth": GATE_NONORTH, "skew": GATE_SKEW},
           "planted_control": ctrl, "march_attempts": [], "cost": []}
    chosen = None
    recipe = NOMINAL
    if time.time() - t0 > CAP_WALL_S:
        out["CAP_EXCEEDED"] = f"rule-12 cap {CAP_WALL_S}s reached before {name} pyHyp"
        say(out["CAP_EXCEEDED"])
    else:
        w = f"{c}/work"; case = f"{c}/case"
        os.makedirs(case, exist_ok=True)
        write_system(case)
        say(f"{name}[{recipe['tag']}]: pyHyp N={N} s0={s0} marchDist={MARCH_DIST} "
            f"cMax={recipe['cMax']} volSmoothIter={recipe['volSmoothIter']}")
        rc, wall = run_pyhyp(w, surf_path, N, s0, recipe, f"{c}/log.pyhyp_{recipe['tag']}",
                             timeout=max(60, int(CAP_WALL_S - (time.time() - t0))))
        out["cost"].append({"stage": f"pyhyp_{recipe['tag']}", "wall_s": wall, "ranks": 1,
                            "core_min": round(wall / 60, 4), "rc": rc})
        att = {"recipe": recipe, "pyhyp_rc": rc, "pyhyp_wall_s": wall,
               "volumeMesh_present": os.path.isfile(f"{w}/volumeMesh.xyz"),
               "pyhyp_log": f"{c}/log.pyhyp_{recipe['tag']}"}
        if rc != 0 or not os.path.isfile(f"{w}/volumeMesh.xyz"):
            att["state"] = "PYHYP_FAILED"; out["march_attempts"].append(att)
            say(f"{name}[{recipe['tag']}]: pyHyp rc={rc}, no volumeMesh -- attempt recorded")
        else:
            d = screen_case_for(case, w, expect_cells, expect_faces)
            att.update({"state": "SCREENED", "cells": d["cells"],
                        "max_non_orthogonality": d["screen_detail"]["max_non_orthogonality"],
                        "max_skewness": d["screen_detail"]["max_skewness"],
                        "negative_volume_cells": d["screen_detail"]["negative_volume_cells"],
                        "clears_hard_gates": d["screen_clears_hard_gates"]})
            for cst in d["screen_cost"]:
                out["cost"].append({**cst, "ranks": 1, "stage": f"{cst['stage']}_{recipe['tag']}"})
            out["march_attempts"].append(att)
            say(f"{name}[{recipe['tag']}]: cells={d['cells']} nonOrth={att['max_non_orthogonality']} "
                f"skew={att['max_skewness']} negVol={att['negative_volume_cells']} "
                f"CLEARS={d['screen_clears_hard_gates']}")
            if d["screen_clears_hard_gates"]:
                chosen = {"recipe_tag": recipe["tag"], "case": case, "work": w, "detail": d}
    if chosen:
        out["chosen_recipe_tag"] = chosen["recipe_tag"]
        out["level_result"] = chosen["detail"]
        out["adopted_case"] = chosen["case"]
    else:
        out["chosen_recipe_tag"] = None
        out["level_result"] = None
        out["ADMISSIBILITY"] = f"{name} did NOT clear the hard gates (MEASURED finding; NOT tuned to pass, T25)"
    out["total_core_min_generation"] = round(sum(x["core_min"] for x in out["cost"]), 4)
    out["generated_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(f"{c}/RESULT.json", "w") as f:
        json.dump(out, f, indent=2)
    return out


def main():
    t0 = time.time()
    if not os.path.isfile(L1_SURF): die(f"L1 parent surface ABSENT: {L1_SURF}")
    ctrl = planted_control()
    name, op, N, s0, cells, faces = LEVEL
    res = build_level(name, op, N, s0, cells, faces, ctrl, t0)

    # ---- family identity across the full FINE triple {L2, L1, L0} ----
    L2res = json.load(open(f"{RR}/L2/RESULT.json"))
    L1res = json.load(open(f"{RR}/L1/RESULT.json"))
    fam = {}
    lr = res.get("level_result")
    if lr and lr.get("points_sha256"):
        c0 = int(lr["cells"]); c1 = int(L1res["level_result"]["cells"]); c2 = int(L2res["level_result"]["cells"])
        s0h = lr["points_sha256"]; s1h = L1res["level_result"]["points_sha256"]; s2h = L2res["level_result"]["points_sha256"]
        fam = {"cells": {"L0": c0, "L1": c1, "L2": c2},
               "points_sha256": {"L0": s0h, "L1": s1h, "L2": s2h},
               "points_all_distinct": len({s0h, s1h, s2h}) == 3,
               "ratio_L0_L1": c0 / c1, "ratio_L1_L2": c1 / c2,
               "ratios_exactly_8": (c0 == 8 * c1 and c1 == 8 * c2),
               "r_per_direction": 2.0 if (c0 == 8 * c1 and c1 == 8 * c2) else None}
        fam["IS_A_FAMILY"] = bool(fam["points_all_distinct"] and fam["ratios_exactly_8"])
    else:
        fam["IS_A_FAMILY"] = False
        fam["note"] = "L0 not built / did not clear -- fine triple not yet a family"
    summary = {"level_added": "L0",
               "L0_clears": (res.get("level_result") or {}).get("screen_clears_hard_gates"),
               "L0_cells": (res.get("level_result") or {}).get("cells"),
               "fine_triple_family_proof": fam,
               "total_core_min_L0_generation": res["total_core_min_generation"],
               "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(f"{RR}/L0_SUMMARY.json", "w") as f:
        json.dump(summary, f, indent=2)
    say(f"WROTE {RR}/L0_SUMMARY.json  L0 gen {summary['total_core_min_L0_generation']} core-min")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
