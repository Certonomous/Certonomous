#!/usr/bin/env python3
"""
grade_r5_mesh.py -- report the DrivAer R5 MESH gates from the built mesh.

GOVERNING DOCUMENT
    verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md
    frozen at 38aab8e78662d574d1b14b61da7efc5898be5c7e

This script reports the MESH-side gates only.  It does NOT grade Cd, it does
NOT launch a solve, and it issues no verdict the registration does not define.

  M1  cell count in 15-20 M                      (section 7)
  L1  achieved layers on VEHICLE PATCHES >= 5.0 of 8   (section 5.3)
  L2  >= 90 % of vehicle faces extruded          (section 5.3)
  S1  max skewness                               (section 7; P4 predicts FAIL)
  y+  PREDICTED from the first-cell height       (section 4.1 scaling)

WHY VEHICLE-ONLY IS NOT PEDANTRY (section 5.2).  `floorNoSlip` is the ground
plane.  It carries no vehicle force and contributes nothing to Cd, and on
r2_medium it is the best-covered patch in the mesh.  Including it raises the
global average to 2.503 of 5 from a vehicle-only 1.850 -- a 1.353x flattery on
exactly the number the gate is set against.  The registration therefore sets L1
on vehicle patches only, and so does this script.

EVERY COVERAGE FIGURE COMES FROM THE POST-EXTRUSION TABLE, cross-checked against
the three independent achievement readings, via analyse_layers.py -- which
refuses when they disagree and refuses when the table is absent but the readings
are non-zero (L-590).  AN ABSENT TABLE WITH ZERO READINGS IS ACHIEVED = 0, NEVER
"unknown": snappyLayerDriver breaks out of the loop before printLayerData(), so
the silence is a measurement.

y+ IS A PREDICTION, NOT A MEASUREMENT.  It is the section-4.1 scaling y+ ~ t1 at
fixed u_tau, anchored on r2_medium's measured area-weighted median y+ of 153.1
at a 5.12 mm first layer.  The registration itself flags that u_tau can move
under an 18x cell-count increase, so this number is labelled PREDICTED
everywhere it appears and settles nothing.  The measured y+ needs the solve.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import analyse_layers as A  # noqa: E402

# --- registered constants, quoted from the frozen document -------------------
N_REQ = 8
T1_M = 0.0010
EXP_RATIO = 1.11
STACK_M = T1_M * ((EXP_RATIO ** N_REQ - 1) / (EXP_RATIO - 1))
L1_MIN = 5.0
L2_MIN_FRAC = 0.90
M1_LO, M1_HI = 15e6, 20e6
S1_MAX = 4.0
YPLUS_LO, YPLUS_HI = 30.0, 45.0          # P2 band
ANCHOR_YPLUS, ANCHOR_T1_M = 153.1, 0.005120   # r2_medium, section 4.1
GROUND_PATCH = "floorNoSlip"


def main() -> int:
    case = Path(sys.argv[1])
    out = {"case": str(case), "governing_freeze": "38aab8e78662d574d1b14b61da7efc5898be5c7e"}

    log = case / "log.snappyHexMesh"
    try:
        ach = A.read_achieved_layers(log)
    except A.Refuse as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return 2
    out["achievement_readings"] = ach["readings"]
    out["achieved_table_line"] = ach["achieved_table_line"]
    out["request_table_line"] = ach["request_table_line"]

    patches = ach.get("patches", {})
    veh = {k: v for k, v in patches.items()
           if k != GROUND_PATCH and v["faces"] > 0}
    vfaces = sum(p["faces"] for p in veh.values())

    if ach["no_layer_exists"]:
        # An absent table with all three readings zero is a MEASUREMENT of zero.
        out["L1"] = dict(achieved=0.0, threshold=L1_MIN, verdict="GATE FAIL",
                         note=("no prism layer exists on this mesh; the "
                               "per-patch table in the log is the REQUEST and "
                               "was not achieved (L-590)"))
        vcov = 0.0
    else:
        vcov = sum(p["faces"] * p["layers_mesh"] for p in veh.values()) / vfaces
        out["L1"] = dict(achieved=round(vcov, 4), of=N_REQ, threshold=L1_MIN,
                         vehicle_faces=vfaces,
                         verdict="PASS" if vcov >= L1_MIN else "GATE FAIL")
        if GROUND_PATCH in patches:
            g = patches[GROUND_PATCH]
            gl = ((vcov * vfaces + g["faces"] * g["layers_mesh"])
                  / (vfaces + g["faces"]))
            out["L1"]["global_including_ground"] = round(gl, 4)
            out["L1"]["ground_flattery_factor"] = round(gl / vcov, 4) if vcov else None

    # L2 -- the log's `Extruding N out of M` is GLOBAL; snappy prints no
    # per-patch extruded fraction, so the global figure is reported AS GLOBAL
    # and the vehicle-only figure is NOT invented.
    r = ach["readings"]
    if "extruding_faces" in r:
        frac = r["extruding_faces"] / r["extruding_of"]
        out["L2"] = dict(extruded_global=r["extruding_faces"],
                         extrudable_global=r["extruding_of"],
                         fraction_GLOBAL=round(frac, 5),
                         threshold=L2_MIN_FRAC,
                         verdict="PASS" if frac >= L2_MIN_FRAC else "GATE FAIL",
                         note=("GLOBAL, including the ground plane -- snappy "
                               "prints no per-patch extruded fraction and one "
                               "is not invented here"))
    else:
        out["L2"] = dict(verdict="NOT A RESULT", note="no Extruding line in the log")

    # M1 -- cell count
    cm = None
    for nm in ("log.checkMeshFull", "log.checkMesh", "log.checkMeshPlain"):
        if (case / nm).exists():
            try:
                cm = A.read_checkmesh(case / nm)
                break
            except A.Refuse as e:
                print(f"REFUSE ({nm}): {e}", file=sys.stderr)
                return 2
    cells = (cm or {}).get("cells") or r.get("layer_cells")
    if cells:
        out["M1"] = dict(cells=cells, band=[M1_LO, M1_HI],
                         verdict="PASS" if M1_LO <= cells <= M1_HI else "GATE FAIL")
    else:
        out["M1"] = dict(verdict="NOT A RESULT", note="no cell count readable")

    # S1 -- skewness, read in BOTH checkMesh forms
    if cm:
        sk = cm["metrics"].get("max_skewness")
        out["S1"] = dict(max_skewness=sk, form=cm["form"].get("max_skewness"),
                         threshold=S1_MAX,
                         verdict=("PASS" if (sk is not None and sk < S1_MAX)
                                  else "GATE FAIL"),
                         n_skew_faces=cm["metrics"].get("n_skew_faces"),
                         failed_checks=cm["failed_checks"])
        out["checkmesh"] = {"metrics": cm["metrics"], "form": cm["form"]}
    else:
        out["S1"] = dict(verdict="PENDING", note="no checkMesh log yet")

    # y+ -- PREDICTED, never measured here
    yp = ANCHOR_YPLUS * T1_M / ANCHOR_T1_M
    out["yplus_PREDICTED"] = dict(
        value=round(yp, 2), band=[YPLUS_LO, YPLUS_HI],
        first_layer_m=T1_M, stack_m=round(STACK_M, 6),
        anchor=f"r2_medium measured median y+ {ANCHOR_YPLUS} at t1={ANCHOR_T1_M} m",
        status="PREDICTION, NOT A MEASUREMENT -- the measured y+ needs the solve",
        caveat=("y+ ~ t1 holds at fixed u_tau; the registration itself flags "
                "that u_tau can move under an 18x cell-count increase"))

    out["per_vehicle_patch"] = {
        k: dict(faces=v["faces"], layers_achieved=v["layers_mesh"],
                thickness_m=v["thickness_m"], thickness_pct=v["thickness_pct"])
        for k, v in sorted(veh.items(), key=lambda kv: -kv[1]["faces"])}

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
