#!/usr/bin/env python3
"""THE CASE PROTOCOL -- STAGE 1: SETUP.

EXIT CONDITION
    A committed-ready registration exists whose every choice is traceable, three
    similar levels stand admitted at a refinement ratio in [1.5, 2.0] with a hashed
    birth certificate each, the near-wall discretisation has been shown able to
    carry the chosen closure, the loosest solver tolerance is strictly tighter than
    the tightest gate, and the comparator is pinned by hash.

FAILURE ACTION -- FIXED, NOT DISCRETIONARY
    Any admission check that fails writes the level's refusal into the stage record
    and DROPS THAT LEVEL from the family.  If fewer than three levels survive, the
    stage exits 3 and STAGE 2 MUST NOT RUN: a family is not something to negotiate
    down to two levels, because a two-level pair with an assumed order is not a
    rule-5 CONVERGING triple (verification's own ruling, 2026-09-08).
    A missing knowledge-base entry NEVER blocks: it is registered "class default,
    first use" and the stage continues.

This script leaves no free choice to a human.  Every value it writes is either
read from the registration, derived from measured physics, or taken from the case
class with its provenance recorded in the class-default journal.

It launches NO solver.  `--emit` writes the case files and certificates; without
it the stage is a dry audit that touches nothing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import case_protocol_lib as L  # noqa: E402

STAGE = "STAGE1"
REPO = Path("/home/ubuntu/Certonomous")


# ---------------------------------------------------------------------------
# Geometry gate.  Geometry is ADMITTED, never assumed.
# ---------------------------------------------------------------------------

def geometry_gate(spec: Dict[str, Any], level: Dict[str, Any], mesh: L.MeshRead) -> Dict[str, Any]:
    """Admit the geometry this level was built on, against the registered shape.

    MULTI-LIMB ON PURPOSE.  A single scalar gate on one extent is easy to satisfy
    for the wrong reason and easy to fail for the wrong reason: the first draft of
    this gate measured axis 1 and reported a 93% error, because axis 1 is the wing's
    THICKNESS and not its span.  It refused, correctly, and the refusal was a defect
    in the instrument rather than in the mesh.  The axes are therefore REGISTERED,
    never inferred, and every limb is reported whether or not it passes -- an axis
    mix-up then shows up as one absurd limb beside several clean ones instead of as
    one absurd verdict.

    The gate sits on the MESH's own wall patch rather than on the generator's input
    file alone, because a generator can be handed the right file and still emit the
    wrong thing.
    """
    import numpy as _np
    g = spec["geometry"]
    src = level.get("geometry_source")
    src_sha = L.sha256_file(src) if src and Path(src).is_file() else None

    wing = mesh.boundary.get(g["wall_patch"])
    if wing is None:
        return {"name": g["gate_name"], "value": None, "tol": None, "verdict": "GATE FAIL",
                "detail": f"wall patch {g['wall_patch']!r} absent", "limbs": [],
                "source_file": src, "sha256": src_sha}

    ax_c, ax_t, ax_s = g["chord_axis"], g["thickness_axis"], g["span_axis"]
    start, n = int(wing["startFace"]), int(wing["nFaces"])
    idx = _np.unique(mesh.face_flat[mesh.face_off[start]:mesh.face_off[start + n]])
    w = mesh.points[idx]
    span = float(w[:, ax_s].max() - w[:, ax_s].min())
    b_reg = float(g["semispan_m"])

    # root section: the band nearest the symmetry plane
    root = w[w[:, ax_s] < w[:, ax_s].min() + float(g["root_band_m"])]
    c_root = float(_np.ptp(root[:, ax_c])) if root.size else 0.0
    t_root = float(_np.ptp(root[:, ax_t])) if root.size else 0.0

    # LE / TE sweep from the convex hull's longest edge on each side.  NOT from
    # spanwise banding: the banded estimator returned 30.00 / 29.92 / 26.35 deg on
    # the medium, fine and coarse levels of this very family and so refused the
    # coarse level of a grid family for a reason that was about the estimator.  A
    # gate that systematically fails coarse grids cannot judge a grid family.
    limbs: List[Dict[str, Any]] = []
    diag: Dict[str, Any] = {}
    for side, key, target in (("leading", "LE sweep deg", g["le_sweep_deg"]),
                              ("trailing", "TE sweep deg", g["te_sweep_deg"])):
        sw, d = L.straight_edge_sweep(w[:, ax_s], w[:, ax_c], side,
                                      0.0, float(g.get("sweep_span_window_rel", 0.99)) * b_reg)
        diag[key] = d
        if sw is None:
            limbs.append({"limb": key, "value": None, "target": target, "tol": g["sweep_tol_deg"],
                          "mode": "abs", "error": None, "pass": False,
                          "detail": d.get("reason")})
        else:
            limbs.append(_limb(key, sw, target, g["sweep_tol_deg"], "abs"))
            limbs[-1]["points_on_edge"] = d.get("points_on_edge")

    limbs.append(_limb("root chord m", c_root, g["root_chord_m"], g["chord_tol_rel"], "rel"))
    tc = t_root / c_root if c_root else 0.0
    limbs.append(_limb("root t/c", tc, g["thickness_ratio"], g["thickness_tol_rel"], "rel"))
    limbs.append(_limb("span extent m", span, b_reg, g["span_overhang_tol_rel"], "rel"))

    overhang = span - b_reg
    verdict = "PASS" if all(x["pass"] for x in limbs) else "GATE FAIL"
    return {
        "name": g["gate_name"], "value": span, "tol": g["span_overhang_tol_rel"],
        "verdict": verdict, "limbs": limbs, "sweep_diagnostics": diag,
        "tip_cap_overhang_m": overhang,
        "tip_cap_overhang_rel": overhang / b_reg,
        "detail": (
            f"planform admitted on {len(limbs)} limbs; wall-patch span extent {span:.6f} m against "
            f"registered semispan {b_reg:.6f} m, i.e. a faired TIP CAP overhanging by "
            f"{overhang:.6f} m ({100*overhang/b_reg:.2f} %).  THE REAL ONERA M6 HAS A BLUNT, FLAT "
            f"TIP; this mesh closes the tip to a faired point.  That is a registered geometry "
            f"DEPARTURE, not a mesh error, and it sits outboard of every grading station -- but it "
            f"is the geometry the outboard stations see and it is recorded here so no figure can "
            f"claim otherwise."),
        "source_file": src, "sha256": src_sha,
    }


def _limb(name: str, value: float, target: float, tol: float, mode: str) -> Dict[str, Any]:
    err = abs(value - target) if mode == "abs" else (abs(value - target) / abs(target) if target else float("inf"))
    return {"limb": name, "value": value, "target": target, "tol": tol, "mode": mode,
            "error": err, "pass": bool(err <= tol)}


# ---------------------------------------------------------------------------
# Level admission.
# ---------------------------------------------------------------------------

def admit_level(spec: Dict[str, Any], level: Dict[str, Any], journal: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Measure everything about one candidate level and decide whether it is in."""
    name = level["name"]
    mesh_dir = Path(level["mesh_dir"])
    rec: Dict[str, Any] = {"level": name, "mesh_dir": str(mesh_dir), "refusals": []}

    if not mesh_dir.is_dir():
        rec["refusals"].append(f"mesh directory absent: {mesh_dir}")
        rec["admitted"] = False
        return rec

    # --- cell count.  NEVER len(owner).  (VERIFICATION_CHARTER 2bd.1) -------
    n_cells, n_cells_source = L.n_cells_from_checkmesh(level["checkmesh_log"])
    rec["n_cells"] = n_cells
    rec["n_cells_source"] = n_cells_source
    if n_cells is None:
        rec["refusals"].append(f"no cell-counting source: {n_cells_source}")

    mesh = L.read_polymesh(mesh_dir)
    rec["n_faces"] = mesh.nfaces
    rec["n_points"] = int(mesh.points.shape[0])
    rec["bbox"] = L.bbox_of(mesh.points)
    rec["patches"] = {k: int(v.get("nFaces", 0)) for k, v in mesh.boundary.items()}

    # A cross-check that is reported, never substituted: the topological cell count
    # from owner/neighbour must AGREE with checkMesh.  Disagreement means one of the
    # two files is not describing this mesh.
    topo = mesh.ncells
    rec["n_cells_topology_crosscheck"] = topo
    if n_cells is not None and topo != n_cells:
        rec["refusals"].append(
            f"checkMesh says {n_cells} cells, owner/neighbour topology says {topo}; "
            "the mesh directory and its checkMesh log do not describe the same mesh")

    # --- geometry gate -----------------------------------------------------
    rec["geometry_gate"] = geometry_gate(spec, level, mesh)
    if rec["geometry_gate"]["verdict"] != "PASS":
        rec["refusals"].append("geometry gate: " + str(rec["geometry_gate"]["detail"]))

    # --- checkMesh verdict -------------------------------------------------
    cm = Path(level["checkmesh_log"])
    cm_txt = cm.read_text(errors="replace") if cm.is_file() else ""
    rec["checkmesh_ok"] = "Mesh OK." in cm_txt
    rec["checkmesh_stars"] = [ln.strip() for ln in cm_txt.splitlines() if ln.lstrip().startswith("***")]
    if not rec["checkmesh_ok"]:
        rec["refusals"].append(f"checkMesh did not report 'Mesh OK.' ({cm})")

    # --- resolution from physics ------------------------------------------
    f = spec["flow"]
    ws = L.first_cell_height(mesh, spec["geometry"]["wall_patch"])
    rec["wall_spacing"] = {
        "y1_min": ws.y1_min, "y1_median": ws.y1_median,
        "y1_mean": ws.y1_mean, "y1_max": ws.y1_max, "method": ws.method}
    yp = {k: L.flat_plate_yplus(v, f["rho"], f["U_mag"], f["mu"], f["x_ref"])
          for k, v in (("min", ws.y1_min), ("median", ws.y1_median),
                       ("mean", ws.y1_mean), ("max", ws.y1_max))}
    rec["yplus_estimate"] = yp
    rec["yplus_note"] = ("first-cell-CENTRE y+ from the 1/7-power flat-plate law at x_ref; "
                         "an ESTIMATE good to order tens of percent, used to answer a "
                         "question whose admissible range is a factor of 300 wide")
    treat = L.lookup_class_default(
        REPO, spec["case_class"], "wall_treatment", spec["closure"]["wall_treatment"],
        "set by the wall-function family actually written into the 0/ directory", journal)
    rec["wall_treatment"] = treat
    rec["resolution_verdict"] = resolution_for_treatment(treat, yp)
    if not rec["resolution_verdict"]["admissible"]:
        rec["refusals"].append("resolution: " + rec["resolution_verdict"]["reason"])

    rec["admitted"] = not rec["refusals"]
    return rec


def resolution_for_treatment(treat: str, yp: Dict[str, float]) -> Dict[str, Any]:
    """Judge y+ against the validity range of the wall treatment ACTUALLY in the case.

    The distinction that matters here, and that a naive log-layer test gets wrong:
    `nutUSpaldingWallFunction` inverts SPALDING's law, which is a single continuous
    fit across sublayer, buffer and log regions.  It is therefore ADMISSIBLE at a y+
    where a plain log-law wall function is not.  Reporting a Spalding mesh as
    OUT_OF_MODEL_VALIDITY because y+ is 16 would be a false red.

    What is NOT waved through is the consequence for a grid triple: Spalding is
    continuous but its effective form varies with y+, so a family whose levels sit
    at different y+ carries a MODEL variation that Richardson extrapolation will
    attribute wholly to discretisation.  That is reported as a caveat on the
    observed order, not as an inadmissible level.
    """
    mean = yp["mean"]
    if treat == "spalding_allyplus":
        admissible = 1.0 <= mean <= 300.0
        if mean < 30.0:
            region = "buffer/blend region of Spalding's law"
        elif mean <= 300.0:
            region = "logarithmic region of Spalding's law"
        else:
            region = "beyond the fitted range of Spalding's law"
        return {"admissible": admissible, "region": region, "yplus_mean": mean,
                "reason": (f"y+ {mean:.3g} lies in the {region}; Spalding's law is a single "
                           "continuous fit and is valid there"),
                "triple_caveat": (
                    "Spalding's effective form varies with y+.  If the levels of a grid "
                    "family sit in different regions of that fit, the level-to-level change "
                    "contains a MODEL variation as well as a discretisation error, and "
                    "Richardson extrapolation cannot separate them.  Any observed order from "
                    "such a family carries that contamination and must be labelled with it.")}
    if treat == "loglaw_wallfunction":
        admissible = 30.0 <= mean <= 300.0
        return {"admissible": admissible, "region": "log layer" if admissible else "outside log layer",
                "yplus_mean": mean,
                "reason": f"plain log-law wall function needs 30 <= y+ <= 300; estimate {mean:.3g}"}
    if treat == "resolved":
        admissible = mean <= 5.0
        return {"admissible": admissible, "region": "viscous sublayer" if admissible else "above sublayer",
                "yplus_mean": mean,
                "reason": f"wall-resolved integration wants y+ <= 1 (<= 5 marginal); estimate {mean:.3g}"}
    L.refuse("WALL_TREATMENT_UNKNOWN", f"{treat!r} has no registered validity range")


def refinement_ratios(levels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """r between consecutive levels, from CELL COUNTS, in 3D.

    r = (N_fine / N_coarse)^(1/3).  The count must come from a cell-counting source;
    a face count here is 4x wrong and propagates straight into the observed order
    and every GCI derived from it.
    """
    out = []
    for i in range(len(levels) - 1):
        c, fn = levels[i + 1], levels[i]          # levels ordered fine -> coarse
        if c.get("n_cells") and fn.get("n_cells"):
            r = (fn["n_cells"] / c["n_cells"]) ** (1.0 / 3.0)
        else:
            r = None
        out.append({"fine": fn["level"], "coarse": c["level"],
                    "n_fine": fn.get("n_cells"), "n_coarse": c.get("n_cells"),
                    "r": r,
                    "r_source": "(N_fine/N_coarse)**(1/3), both counts from checkMesh stdout"})
    return out


# ---------------------------------------------------------------------------
# Blockage.
# ---------------------------------------------------------------------------

def blockage(spec: Dict[str, Any], bbox: Dict[str, List[float]]) -> Dict[str, Any]:
    g = spec["geometry"]
    dy = bbox["max"][1] - bbox["min"][1]
    dz = bbox["max"][2] - bbox["min"][2]
    dx = bbox["max"][0] - bbox["min"][0]
    frontal = float(g["frontal_area_m2"])
    cross = dy * dz
    return {
        "domain_extent_m": {"x": dx, "y": dy, "z": dz},
        "domain_extent_semispans": {"x": dx / g["semispan_m"], "y": dy / g["semispan_m"],
                                    "z": dz / g["semispan_m"]},
        "domain_extent_MAC": {"x": dx / g["x_ref_MAC_m"], "y": dy / g["x_ref_MAC_m"],
                              "z": dz / g["x_ref_MAC_m"]},
        "model_frontal_area_m2": frontal,
        "domain_cross_section_m2": cross,
        "blockage_ratio": frontal / cross,
        "note": ("blockage = model frontal area / domain cross-section.  Stated because a "
                 "farfield that is merely 'far' is a claim, not a number.")}


# ---------------------------------------------------------------------------
# Case construction.  ONE script, one template, every departure registered.
# ---------------------------------------------------------------------------

def write_case(spec: Dict[str, Any], level_rec: Dict[str, Any], level_spec: Dict[str, Any],
               out_root: Path) -> Dict[str, Any]:
    """Build ONE runnable case for ONE level from the registered template.

    The template is COPIED and then a REGISTERED LIST OF DELTAS is applied, each
    delta recorded with the reason it exists.  It is not retyped from scratch,
    deliberately: the template's dictionaries carry choices that were argued out and
    written down over several earlier attempts on this case, and retyping them from
    memory is how a validated setting silently changes.  What must never happen is
    an UNRECORDED difference between the template and what runs, so every delta is
    named, and the template itself is hashed into the record.

    The mesh is SYMLINKED to the birth-certified polyMesh rather than copied.  A
    copy is a second artifact that can drift from its certificate; a symlink means
    the certificate and the thing the solver reads are the same bytes.  Nothing in
    stages 1-4 runs `renumberMesh -overwrite`, which is the one utility on this box
    that would rewrite a certified mesh in place.
    """
    tmpl = Path(spec["case_template"])
    case = out_root / level_rec["level"] / "case"
    if case.exists():
        shutil.rmtree(case)
    (case / "constant").mkdir(parents=True, exist_ok=True)

    copied: List[str] = []
    for rel in ("system", "0"):
        if (tmpl / rel).is_dir():
            shutil.copytree(tmpl / rel, case / rel)
            copied.append(rel)
    for rel in ("constant/thermophysicalProperties", "constant/turbulenceProperties"):
        if (tmpl / rel).is_file():
            shutil.copy2(tmpl / rel, case / rel)
            copied.append(rel)

    mesh_src = Path(level_spec["mesh_dir"]).resolve()
    (case / "constant" / "polyMesh").symlink_to(mesh_src)

    deltas: List[Dict[str, Any]] = []

    def edit(rel: str, pattern: str, repl: str, why: str, must_match: bool = True) -> None:
        f = case / rel
        txt = f.read_text()
        new_txt, n = re.subn(pattern, repl, txt, flags=re.M)
        if must_match and n == 0:
            L.refuse("DELTA_DID_NOT_APPLY",
                     f"{rel}: pattern {pattern!r} matched nothing; a delta that silently "
                     "does not apply leaves the case running the template's value while the "
                     "record says otherwise")
        if n:
            f.write_text(new_txt)
        deltas.append({"file": rel, "pattern": pattern, "replacement": repl,
                       "matches": n, "why": why})

    def insert_before(rel: str, anchor_pat: str, block: str, why: str) -> None:
        f = case / rel
        txt = f.read_text()
        m = re.search(anchor_pat, txt, re.M)
        if not m:
            L.refuse("DELTA_ANCHOR_ABSENT", f"{rel}: anchor {anchor_pat!r} not found")
        f.write_text(txt[:m.start()] + block + txt[m.start():])
        deltas.append({"file": rel, "insert_before": anchor_pat, "block": block.strip(), "why": why})

    rc = spec["run_control"]
    edit("system/controlDict", r"^application\s+\S+;", f"application     {rc['solver']};",
         "solver named by the registration, not inherited from whatever the template last ran")
    edit("system/controlDict", r"^endTime\s+\S+;", f"endTime         {rc['end_time']};",
         "full-run length registered before compute")
    edit("system/controlDict", r"^writeInterval\s+\S+;", f"writeInterval   {rc['write_interval']};",
         ("THE PLATEAU LIMB NEEDS A TRAILING WINDOW OF THE RUN'S OWN HISTORY. The template wrote "
          "once, at endTime; one write cannot carry a plateau statistic at all, and a two-write "
          "cadence would only permit the two-point test that VERIFICATION_CHARTER 2bd forbids. "
          f"This cadence gives {int(rc['end_time'])//int(rc['write_interval'])} writes."))
    edit("system/controlDict", r"^deltaT\s+\S+;", f"deltaT          {rc['delta_t']};",
         "pseudo-time step index; with localEuler the physical value is set per cell from maxCo")

    # --- DEAD-LEVER REPAIR, and it is the reason stage 2 has a dead-lever audit ---
    insert_before(
        "system/fvSchemes",
        r"^\s*div\(phi,U\)",
        ("    // DEAD-LEVER REPAIR (stage 2 audit rule TRANSONIC).  Without this entry, setting\n"
         "    // `transonic yes` in fvSolution aborts at the first pressure solve on\n"
         "    //   Entry 'div(phid,p)' not found in dictionary \"system/fvSchemes/divSchemes\"\n"
         "    // because `default none;` makes an unruled term a hard abort.  On this case that\n"
         "    // is exactly what happened: the diagnostic registered to TEST the transonic\n"
         "    // switch died in dictionary lookup at Time = 1 having exercised nothing, and the\n"
         "    // record then carried a rung as tried that was never once pulled.\n"
         "    div(phid,p)                                   Gauss upwind;\n"),
        "makes the transonic lever pullable; it does NOT turn it on")

    tol = spec["numerics"]["solver_tolerances"]
    edit("system/fvSolution", r"tolerance\s+1e-8;\s*relTol\s+0\.01;",
         f"tolerance {tol['p']:g}; relTol 0.01;",
         "p linear tolerance from the registration (T23G2Rn2: strictly tighter than every gate)")
    edit("system/fvSolution", r"tolerance\s+1e-8;\s*relTol\s+0;",
         f"tolerance {tol['U']:g}; relTol 0;",
         "final-corrector tolerances from the registration")

    rec = {
        "level": level_rec["level"], "case": str(case),
        "template": str(tmpl), "template_sha256": L.digest_of_map(L.sha256_tree(
            tmpl, ["system/*", "0/*", "constant/thermophysicalProperties",
                   "constant/turbulenceProperties"])),
        "copied": copied,
        "mesh_symlink_target": str(mesh_src),
        "mesh_is_symlink_not_copy": True,
        "deltas": deltas,
        "written_sha256": L.digest_of_map(L.sha256_tree(case, ["system/*", "0/*", "constant/*"])),
    }
    (case.parent / "CASE_CONSTRUCTION.json").write_text(json.dumps(rec, indent=2) + "\n")
    return rec


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, help="CASE_SPEC.json -- the machine half of the registration")
    ap.add_argument("--out", required=True, help="case run root (verification/runs/<CAMPAIGN>_runs)")
    ap.add_argument("--emit", action="store_true",
                    help="write case files, birth certificates and the freeze manifest; "
                         "without it this is a dry audit that touches nothing")
    a = ap.parse_args(argv)

    spec = json.loads(Path(a.spec).read_text())
    out = Path(a.out)
    journal: List[Dict[str, Any]] = []
    lines: List[str] = []
    t0 = time.time()

    # --- levels ------------------------------------------------------------
    levels = [admit_level(spec, lv, journal) for lv in spec["levels"]]
    admitted = [r for r in levels if r["admitted"]]
    for r in levels:
        lines.append(L.state_line(
            STAGE, f"level {r['level']} admission",
            "ADMITTED" if r["admitted"] else "REFUSED",
            n_cells=r.get("n_cells"),
            yplus_mean=f"{r.get('yplus_estimate',{}).get('mean',float('nan')):.4g}",
            y1_mean=f"{r.get('wall_spacing',{}).get('y1_mean',float('nan')):.4e}"))
        for why in r["refusals"]:
            lines.append(L.state_line(STAGE, f"level {r['level']} refusal", why))

    ratios = refinement_ratios(admitted)
    lo, hi = spec["family"]["r_min"], spec["family"]["r_max"]
    r_ok = bool(ratios) and all(x["r"] is not None and lo <= x["r"] <= hi for x in ratios)
    for x in ratios:
        lines.append(L.state_line(STAGE, f"refinement {x['fine']}/{x['coarse']}",
                                  "IN BAND" if (x["r"] and lo <= x["r"] <= hi) else "OUT OF BAND",
                                  r=f"{x['r']:.7f}" if x["r"] else None,
                                  n_fine=x["n_fine"], n_coarse=x["n_coarse"]))

    family_ok = len(admitted) >= 3 and r_ok
    lines.append(L.state_line(STAGE, "family", "COMPLETE" if family_ok else "INCOMPLETE",
                              admitted=len(admitted), required=3))

    # --- tolerance strictly tighter than the tightest gate -----------------
    gates = spec["gates"]
    tightest = min(gates, key=lambda g: abs(float(g["threshold"])))
    tc = L.check_tolerance_strictly_tighter(
        tightest["name"], abs(float(tightest["threshold"])),
        {k: float(v) for k, v in spec["numerics"]["solver_tolerances"].items()},
        min_decades=float(spec["numerics"].get("min_decades_clear_air", 1.0)))
    lines.append(L.state_line(STAGE, "T23G2Rn2 tolerance-tighter-than-gate",
                              "PASS" if tc.ok else "GATE FAIL",
                              gate=tightest["name"], gate_tol=tc.gate_tolerance,
                              loosest=f"{tc.worst_field}={tc.worst_value:g}",
                              decades=f"{tc.margin_decades:.2f}"))

    # --- comparator pin ----------------------------------------------------
    pins = []
    for p in spec["pins"]:
        fp = REPO / p["path"]
        pins.append({"path": p["path"], "role": p["role"],
                     "blob": L.sha256_file(fp) if fp.is_file() else None})
        lines.append(L.state_line(STAGE, f"pin {p['role']} {p['path']}",
                                  "HASHED" if fp.is_file() else "ABSENT",
                                  sha256=(pins[-1]["blob"] or "")[:16]))

    # --- capacity ----------------------------------------------------------
    mem = L.memory_state()
    cap = capacity_finding(spec, admitted, mem)
    lines.append(L.state_line(STAGE, "memory capacity", cap["verdict"],
                              MemAvailable_GiB=f"{mem.mem_available_gib:.2f}",
                              drained_ceiling_GiB=f"{mem.drained_ceiling_gib:.2f}",
                              fine_level_need_GiB=f"{cap['fine_need_gib']:.2f}"
                              if cap["fine_need_gib"] else None))

    # --- blockage ----------------------------------------------------------
    blk = blockage(spec, admitted[0]["bbox"]) if admitted else None
    if blk:
        lines.append(L.state_line(STAGE, "blockage", "STATED",
                                  ratio=f"{blk['blockage_ratio']:.3e}",
                                  domain_semispans_x=f"{blk['domain_extent_semispans']['x']:.1f}"))

    # --- emit --------------------------------------------------------------
    record = {
        "stage": 1, "case": spec["case"], "case_class": spec["case_class"],
        "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "levels": levels, "refinement_ratios": ratios, "family_complete": family_ok,
        "tolerance_check": tc.__dict__, "pins": pins, "capacity": cap,
        "blockage": blk, "class_default_journal": journal,
        "wall_clock_s": round(time.time() - t0, 2),
    }
    if a.emit:
        out.mkdir(parents=True, exist_ok=True)
        for r in levels:
            if not r["admitted"]:
                continue
            lv = next(x for x in spec["levels"] if x["name"] == r["level"])
            man, man_sha = L.mesh_manifest(lv["mesh_dir"])
            rr = next((x["r"] for x in ratios if x["fine"] == r["level"]), None)
            gen = lv.get("generator", {})
            L.write_birth_certificate(
                out / r["level"] / "BIRTH_CERTIFICATE.json",
                case=spec["case"], level=r["level"],
                n_cells=r.get("n_cells"), n_cells_source=r["n_cells_source"],
                n_faces=r.get("n_faces"), n_points=r.get("n_points"),
                bbox=r.get("bbox"), h_ref=h_ref_of(r), refinement_ratio_vs_next_coarser=rr,
                geometry_source_file=r["geometry_gate"].get("source_file"),
                geometry_sha256=r["geometry_gate"].get("sha256"),
                geometry_gate={k: r["geometry_gate"][k] for k in ("name", "value", "tol", "verdict")},
                generator_script=gen.get("script", "UNRECORDED"),
                generator_blob_sha=(L.sha256_file(REPO / gen["script"])
                                    if gen.get("script") and (REPO / gen["script"]).is_file() else None),
                generator_argv=gen.get("argv", []),
                generator_rc=gen.get("rc"),
                manifest=man, manifest_sha256=man_sha,
                notes=[r["geometry_gate"].get("detail", ""),
                       r["resolution_verdict"].get("reason", ""),
                       r["resolution_verdict"].get("triple_caveat", "")])
            lines.append(L.state_line(STAGE, f"birth certificate {r['level']}", "WRITTEN",
                                      manifest_sha256=man_sha[:16], files=len(man)))
        if spec.get("case_template"):
            record["case_construction"] = []
            for r in levels:
                if not r["admitted"]:
                    continue
                lv = next(x for x in spec["levels"] if x["name"] == r["level"])
                cr = write_case(spec, r, lv, out)
                record["case_construction"].append(cr)
                lines.append(L.state_line(STAGE, f"case built {r['level']}", "WRITTEN",
                                          deltas=len(cr["deltas"]),
                                          sha256=cr["written_sha256"][:16]))
        (out / "STAGE1_RECORD.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
        lines.append(L.state_line(STAGE, "stage record", "WRITTEN", path=str(out / "STAGE1_RECORD.json")))

    for ln in lines:
        print(ln)

    if not family_ok:
        print(L.state_line(STAGE, "EXIT", "REFUSED",
                           reason="fewer than three admitted levels in band; STAGE 2 must not run"))
        return 3
    if not tc.ok:
        print(L.state_line(STAGE, "EXIT", "GATE FAIL", reason="solver tolerance not strictly tighter"))
        return 4
    print(L.state_line(STAGE, "EXIT", "PASS", wall_s=record["wall_clock_s"]))
    return 0


def h_ref_of(rec: Dict[str, Any]) -> Optional[float]:
    """Representative cell size h = (V_domain / N_cells)^(1/3).

    Roache's h.  Reported per level so the observed order has a length scale that is
    not the cell count in disguise.
    """
    if not rec.get("n_cells") or not rec.get("bbox"):
        return None
    b = rec["bbox"]
    v = (b["max"][0] - b["min"][0]) * (b["max"][1] - b["min"][1]) * (b["max"][2] - b["min"][2])
    return (v / rec["n_cells"]) ** (1.0 / 3.0)


def capacity_finding(spec: Dict[str, Any], admitted: List[Dict[str, Any]],
                     mem: L.MemoryState) -> Dict[str, Any]:
    """Will the finest admitted level fit, and say it NOW rather than at 2 GiB from the end.

    Uses the registered per-cell solver footprint if the knowledge base has one,
    otherwise the class default, and says which.  A level that will not fit is a
    CAPACITY FINDING -- a smaller three-level family that fits is worth infinitely
    more than a perfect one that cannot run.
    """
    if not admitted:
        return {"verdict": "NOT EVALUABLE", "fine_need_gib": None,
                "detail": "no admitted level"}
    fine = max(admitted, key=lambda r: r.get("n_cells") or 0)
    bpc = float(spec["numerics"].get("solver_bytes_per_cell", 0) or 0)
    if not bpc or not fine.get("n_cells"):
        return {"verdict": "NOT EVALUABLE", "fine_need_gib": None, "level": fine["level"],
                "mem_available_gib": mem.mem_available_gib,
                "drained_ceiling_gib": mem.drained_ceiling_gib,
                "detail": ("no measured solver bytes/cell registered; STAGE 2 measures it on "
                           "the coarsest level and STAGE 3 re-checks before the full run. "
                           "A meshing bytes/cell is NOT a solver bytes/cell and is not "
                           "substituted here.")}
    need = bpc * fine["n_cells"] / (1024 ** 3)
    fits_now = need <= mem.mem_available_gib
    fits_drained = need <= mem.drained_ceiling_gib
    return {
        "verdict": ("FITS" if fits_now else ("FITS ONLY IF DRAINED" if fits_drained else "CAPACITY FINDING")),
        "level": fine["level"], "n_cells": fine["n_cells"],
        "bytes_per_cell": bpc, "fine_need_gib": need,
        "mem_available_gib": mem.mem_available_gib,
        "drained_ceiling_gib": mem.drained_ceiling_gib,
        "margin_gib_now": mem.mem_available_gib - need,
        "margin_gib_drained": mem.drained_ceiling_gib - need,
        "detail": mem.detail,
    }


if __name__ == "__main__":
    try:
        sys.exit(main())
    except L.Refusal as e:
        print(L.state_line(STAGE, "REFUSAL", e.code, detail=e.detail))
        sys.exit(2)
