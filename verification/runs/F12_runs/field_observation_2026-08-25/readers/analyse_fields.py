#!/usr/bin/env python3
"""Per-iteration, per-patch field statistics for the F12 rung-1 observation arm.
Uses field_probe.read_field / patch_owner_cells, both under planted control."""
import json, math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from field_probe import read_field, patch_owner_cells, extremes, mag

CASE = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
TIMES = [str(i) for i in range(0, 16)]
FIELDS = ["p", "U", "T", "k", "omega", "rho", "nut"]

C = read_field(CASE / "0" / "C")["internal"]          # cell centres
PATCH = patch_owner_cells(CASE / "constant" / "polyMesh")
P0, PMINF, PMAXF = 101325.0, 0.1, 2.0                  # 0/p uniform, fvSolution
FLOOR, CEIL = P0 * PMINF, P0 * PMAXF

def loc(i):
    x, y, z = C[i]
    return {"cell": i, "x": round(x, 6), "y": round(y, 6), "z": round(z, 6),
            "r_from_LE": round(math.hypot(x, y), 4),
            "r_from_quarter_chord": round(math.hypot(x - 0.25, y), 4)}

rows = []
for t in TIMES:
    d = CASE / t
    if not d.is_dir(): continue
    row = {"iteration": int(t), "fields": {}}
    for f in FIELDS:
        fp = d / f
        if not fp.exists(): continue
        fld = read_field(fp)
        ex = extremes(fld["internal"])
        if ex is None:
            row["fields"][f] = {"uniform": fld["uniform_internal"]}; continue
        rec = {"min": ex["min"], "min_at": loc(ex["min_index"]),
               "max": ex["max"], "max_at": loc(ex["max_index"]), "n_cells": ex["n"]}
        if f == "p":
            below0 = [i for i, v in enumerate(fld["internal"]) if v < 0]
            belowF = [i for i, v in enumerate(fld["internal"]) if v < FLOOR]
            aboveC = [i for i, v in enumerate(fld["internal"]) if v > CEIL]
            rec["n_cells_p_below_zero"] = len(below0)
            rec["n_cells_below_pMin_floor_10132.5"] = len(belowF)
            rec["n_cells_above_pMax_ceil_202650"] = len(aboveC)
            rec["offending_cells_sample"] = [loc(i) for i in (belowF + aboveC)[:12]]
        if f == "T":
            rec["n_cells_T_below_100K"] = sum(1 for v in fld["internal"] if v < 100)
            rec["n_cells_T_below_0K"] = sum(1 for v in fld["internal"] if v < 0)
        # per-patch, via OWNER CELLS (works for zeroGradient patches too)
        pp = {}
        for nm, meta in PATCH.items():
            if meta["type"] == "empty": continue
            vals = [fld["internal"][c] for c in meta["owner_cells"]]
            e2 = extremes(vals)
            oc = meta["owner_cells"]
            pp[nm] = {"bc_type": meta["type"], "nFaces": meta["nFaces"],
                      "adjacent_cell_min": e2["min"], "adjacent_cell_min_at": loc(oc[e2["min_index"]]),
                      "adjacent_cell_max": e2["max"], "adjacent_cell_max_at": loc(oc[e2["max_index"]])}
        rec["patches"] = pp
        row["fields"][f] = rec
    rows.append(row)
OUT.write_text(json.dumps({"case": str(CASE), "n_cells": len(C),
                           "p_ref": P0, "pMin_floor": FLOOR, "pMax_ceil": CEIL,
                           "iterations": rows}, indent=1))
print(f"wrote {OUT}  ({len(rows)} iterations)")
