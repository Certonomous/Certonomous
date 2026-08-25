#!/usr/bin/env python3
"""F12 mesh audit -- build all three ladder levels, grade admission gate A on
each from a real checkMesh log, and settle the GEOMETRIC ERROR FLOOR question
FROM THE BUILT DICTIONARIES rather than from the source.

MESH ONLY.  No solver is launched by this script.  It deliberately does NOT
write into the three registered SOLVE directories
(coarse|medium|fine)_workshop_M0.734_a2.79, so their rule-4 ABSENT status is
preserved; the coarse one already exists because rung 1 was fired.

Standing rule 3 (planted-zero control) applies to the "the polygon is
identical" claim as much as to a zero: the comparator PLANTS a deliberately
re-sampled polygon into a dictionary on disk, reads it back with the same
extractor, and REFUSES if the reader cannot see the difference.
"""
import json
import pathlib
import re
import sys
import time

REPO = pathlib.Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "sdk"))

from sdk.workflows import rae2822_case9 as W          # noqa: E402
from sdk.workflows.tmr_verification import _foam      # noqa: E402

HERE = REPO / "verification" / "runs" / "F12_runs" / "mesh_audit_2026-08-25"
PLANT_DROP = 2      # the planted perturbation: keep every 2nd polyLine point


def extract_polylines(dict_text: str):
    """Every polyLine point set in a built blockMeshDict, keyed by its vertex
    pair.  Reads the DICTIONARY ON DISK -- not the generator."""
    out = {}
    for m in re.finditer(r"polyLine\s+(\d+)\s+(\d+)\s*\(([^;]*)\)\s*$",
                         dict_text, re.MULTILINE):
        a, b, body = m.group(1), m.group(2), m.group(3)
        pts = [tuple(float(v) for v in p.split())
               for p in re.findall(r"\(([^()]*)\)", body)]
        out[(int(a), int(b))] = pts
    return out


def polygon_signature(dict_text: str):
    """The (x, y) surface polygon the dictionary actually defines, as an
    ordered, de-duplicated list, plus its point count."""
    pls = extract_polylines(dict_text)
    pts = []
    for key in sorted(pls):
        for (x, y, z) in pls[key]:
            if z != 0.0:          # one z-plane is enough; the mesh is extruded
                continue
            pts.append((round(x, 12), round(y, 12)))
    uniq = sorted(set(pts))
    return {"n_polylines": len(pls),
            "n_points_z0": len(pts),
            "n_unique_xy": len(uniq),
            "points": uniq}


def same_polygon(a, b):
    return a["points"] == b["points"]


def main():
    results = {"levels": {}, "timings": {}}
    for level in W.LEVELS:
        case = HERE / level.name
        if case.exists():
            sys.stderr.write(f"REFUSING: {case} already exists\n")
            return 3
        t0 = time.monotonic()
        params = W.build_case(case, mach=0.734, alpha_deg=2.79,
                              level=level, iterations=6000)
        t_write = time.monotonic() - t0

        t0 = time.monotonic()
        rc_bm = _foam(["blockMesh"], case, "log.blockMesh", timeout=1800)
        t_bm = time.monotonic() - t0

        t0 = time.monotonic()
        _foam(["checkMesh"], case, "log.checkMesh", timeout=1800)
        t_cm = time.monotonic() - t0

        quality = W.parse_check_mesh(
            (case / "log.checkMesh").read_text(errors="replace"))
        gate = W.mesh_gate(quality)
        sig = polygon_signature((case / "system" / "blockMeshDict").read_text())

        results["levels"][level.name] = {
            "blockMesh_rc": rc_bm.returncode,
            "cells_nominal": level.cells,
            "cells_built": quality.get("cells"),
            "n_surf_quarter": level.n_surf_quarter, "ny": level.ny,
            "first_cell": params["first_cell"],
            "far_first_cell": params["far_first_cell"],
            "wall_normal_total_ratio": params["wall_normal_total_ratio"],
            "far_total_ratio": params["far_total_ratio"],
            "quality": {k: v for k, v in quality.items() if k != "per_tap"},
            "gate_A_passed": gate["passed"], "gate_A_breaches": gate["breaches"],
            "polygon": {k: v for k, v in sig.items() if k != "points"},
        }
        results["timings"][level.name] = {
            "dict_write_s": round(t_write, 3),
            "blockMesh_s": round(t_bm, 3),
            "checkMesh_s": round(t_cm, 3)}
        results["levels"][level.name]["_sig"] = sig

    # ---- the geometric error floor, decided on the built dictionaries -----
    sigs = {n: results["levels"][n].pop("_sig") for n in results["levels"]}
    names = [lv.name for lv in W.LEVELS]
    pairs = {}
    for i in range(len(names) - 1):
        a, b = names[i], names[i + 1]
        pairs[f"{a}_vs_{b}"] = same_polygon(sigs[a], sigs[b])
    pairs["coarse_vs_fine"] = same_polygon(sigs[names[0]], sigs[names[2]])

    # ---- STANDING RULE 3: plant a re-sampled polygon and read it back -----
    fine_dict = (HERE / names[2] / "system" / "blockMeshDict").read_text()

    def thin(m):
        a, b, body = m.group(1), m.group(2), m.group(3)
        pts = re.findall(r"\(([^()]*)\)", body)
        kept = pts[::PLANT_DROP]
        return ("polyLine %s %s (" % (a, b)
                + " ".join("(%s)" % p for p in kept) + ")")

    planted_text = re.sub(r"polyLine\s+(\d+)\s+(\d+)\s*\(([^;]*)\)\s*$",
                          thin, fine_dict, flags=re.MULTILINE)
    planted_path = HERE / "PLANTED_CONTROL_blockMeshDict"
    planted_path.write_text(planted_text)          # PLANT ON DISK
    planted_sig = polygon_signature(planted_path.read_text())   # READ BACK

    control_sees_it = not same_polygon(sigs[names[2]], planted_sig)
    results["planted_control"] = {
        "what": f"fine blockMeshDict re-sampled, every {PLANT_DROP}nd polyLine "
                "point kept, written to disk and read back by the SAME extractor",
        "artifact": str(planted_path.relative_to(REPO)),
        "unbuilt_unique_xy": sigs[names[2]]["n_unique_xy"],
        "planted_unique_xy": planted_sig["n_unique_xy"],
        "reader_sees_the_difference": control_sees_it,
    }
    if not control_sees_it:
        sys.stderr.write("REFUSING: the extractor cannot see a planted "
                         "polygon change; its 'identical' verdict is not "
                         "evidence (standing rule 3).\n")
        results["geometric_floor"] = "NOT A RESULT -- planted control failed"
        (HERE / "mesh_audit.json").write_text(json.dumps(results, indent=2) + "\n")
        return 4

    results["geometric_floor"] = {
        "pairs_identical": pairs,
        "unique_xy_per_level": {n: sigs[n]["n_unique_xy"] for n in names},
        "polylines_per_level": {n: sigs[n]["n_polylines"] for n in names},
    }
    (HERE / "mesh_audit.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({k: v for k, v in results.items() if k != "levels"},
                     indent=2))
    for n in names:
        r = results["levels"][n]
        print(n, "cells", r["cells_built"], "gateA", r["gate_A_passed"],
              "nonortho", r["quality"].get("max_non_orthogonality"),
              "skew", r["quality"].get("max_skewness"),
              "AR", r["quality"].get("max_aspect_ratio"),
              "poly_pts", r["polygon"]["n_unique_xy"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
