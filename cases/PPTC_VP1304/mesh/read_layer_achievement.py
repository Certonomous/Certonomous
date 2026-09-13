#!/usr/bin/env python3
"""
read_layer_achievement.py -- read what snappyHexMesh ACHIEVED in the layer phase,
never what it was ASKED for.

WHY THIS FILE EXISTS (L-590, and the source clause that makes L-590 worse)
--------------------------------------------------------------------------
snappyHexMesh prints TWO per-patch layer tables and they are not the same table.

  REQUEST table   "patch  faces    layers avg thickness[m]  near-wall overall"
                  emitted by snappyLayerDriver::calculateLayerThickness()
                  (openfoam2606 src .../snappyLayerDriver.C:1696-1700),
                  which runs BEFORE the line "Outer iteration : 0".
                  It is what was asked for. It is printed even when nothing
                  whatsoever is extruded.

  ACHIEVEMENT     "Mesh with layers : cells:...  faces:...  points:..."
  table           "patch  faces        layers        overall thickness"
                  "          target   mesh     [m]       [%]"
                  emitted by snappyLayerDriver::printLayerData()
                  (.../snappyLayerDriver.C:3080-3147), called from
                  addLayers() at .../snappyLayerDriver.C:5211.

THE TRAP THAT THIS READER EXISTS TO SURVIVE:
  addLayers() contains, at .../snappyLayerDriver.C:5102-5110,

        const label nTotalAdded = gSum(patchNLayers);
        ...
        if (nTotalAdded == 0)
        {
            break;
        }

  and that break is UPSTREAM of the printLayerData() call at line 5211.
  Therefore a run that added ZERO layers prints NO achievement table at all.
  The only per-patch table left in such a log is the REQUEST table, which
  still cheerfully reads "blades 382233 6 1.79e-06 1.07e-05".

  A parser that "looks for the achieved table" and finds nothing must report
  ACHIEVED = 0, not "unknown", and must never fall back to the request table.
  This reader does exactly that, and says which of the two routes it used.

CORROBORATION (three independent channels, all read from the same log)
  A. achievement table, if present        -> per-patch layers and thickness
  B. net cells:  "Layer mesh : cells:N" minus "Snapped mesh : cells:N"
  C. the LAST "Added A out of B cells (P%)." line after the last
     "Outer iteration", which is snappyLayerDriver.C:4385 and is the count
     that survived checkAndUnmark, not the trial count of an earlier iteration.

PLANTED CONTROL (CLAUDE.md standing rule 3)
  Before it reports anything about a real log, this reader plants a known
  non-zero achievement into a COPY of that same log on disk, re-reads the copy
  through the identical code path, and REFUSES (exit 2) unless every planted
  figure comes back exactly. A zero from a reader not shown able to see a
  non-zero is not evidence.

Usage:
    read_layer_achievement.py <log.snappyHexMesh> [--json] [--keep-plant DIR]

Exit: 0 read ok; 2 REFUSED (planted control failed, or the log is not a
      snappyHexMesh layer log); 3 log unreadable.
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

# ---------------------------------------------------------------- plant values
# Deliberately odd figures that cannot arise by accident from a real run.
PLANT_PATCH        = "plantedPatch"
PLANT_FACES        = 424242
PLANT_TARGET       = 7
PLANT_MESH_LAYERS  = 6.31
PLANT_THICKNESS_M  = 1.234e-03      # the lab's standing plant constant
PLANT_PCT          = 87.65
PLANT_NET_CELLS    = 909091         # planted net cell gain
PLANT_ADDED_CELLS  = 808081         # planted final "Added A out of B cells"
PLANT_EXTRUDED_FCS = 707071         # planted final "Extruding A out of B faces"

# ---------------------------------------------------------------- log patterns
RE_OUTER      = re.compile(r"^\s*Outer iteration\s*:\s*(\d+)\s*$")
RE_SNAPPED    = re.compile(r"^\s*Snapped mesh\s*:\s*cells:(\d+)\s+faces:(\d+)\s+points:(\d+)")
RE_LAYERMESH  = re.compile(r"^\s*Layer mesh\s*:\s*cells:(\d+)\s+faces:(\d+)\s+points:(\d+)")
RE_WITHLAYERS = re.compile(r"^\s*Mesh with layers\s*:\s*cells:(\d+)\s+faces:(\d+)\s+points:(\d+)")
RE_EXTRUDING  = re.compile(
    r"^\s*Extruding\s+(\d+)\s+out of\s+(\d+)\s+faces\s+\(([-\d.eE+]+)%\)\."
    r"\s+Removed extrusion at\s+(\d+)\s+faces\."
)
RE_ADDED      = re.compile(
    r"^\s*Added\s+(\d+)\s+out of\s+(\d+)\s+cells\s+\(([-\d.eE+]+)%\)\."
)
# REQUEST table header: ".. faces    layers avg thickness[m]"
RE_REQ_HDR    = re.compile(r"^\s*\S*\s*faces\s+layers\s+avg thickness\[m\]\s*$")
# ACHIEVEMENT table header: ".. faces        layers        overall thickness"
RE_ACH_HDR    = re.compile(r"^\s*\S*\s*faces\s+layers\s+overall thickness\s*$")
RE_ACH_SUB    = re.compile(r"^\s*target\s+mesh\s+\[m\]\s+\[%\]\s*$")
RE_ACH_ROW    = re.compile(
    r"^\s*(\S+)\s+(\d+)\s+(\d+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*$"
)
RE_REQ_ROW    = re.compile(
    r"^\s*(\S+)\s+(\d+)\s+(\d+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*$"
)
RE_ADDLAYERS  = re.compile(r"^\s*Shrinking and layer addition phase\s*$")


class Refusal(Exception):
    pass


def _read_lines(path):
    with open(path, "r", errors="replace") as fh:
        return fh.read().splitlines()


def parse(path):
    """Return a dict of what the layer phase ACHIEVED. Never reads the request
    table as an achievement; it is parsed only so it can be reported, labelled,
    beside the achievement, and so the L-590 ordering can be asserted."""
    lines = _read_lines(path)

    layer_phase   = None
    outer_idx     = []
    snapped       = None
    layer_mesh    = None
    with_layers   = None
    extruding     = []   # (lineno, nExtruded, nFaces, pct, nRemoved)
    added         = []   # (lineno, nAdded, nIdeal, pct)
    req_hdr_idx   = None
    ach_hdr_idx   = None
    request_rows  = []
    achieved_rows = []

    for i, ln in enumerate(lines):
        if layer_phase is None and RE_ADDLAYERS.match(ln):
            layer_phase = i
        m = RE_OUTER.match(ln)
        if m:
            outer_idx.append(i)
            continue
        m = RE_SNAPPED.match(ln)
        if m:
            snapped = (i, int(m.group(1)), int(m.group(2)), int(m.group(3)))
            continue
        m = RE_LAYERMESH.match(ln)
        if m:
            layer_mesh = (i, int(m.group(1)), int(m.group(2)), int(m.group(3)))
            continue
        m = RE_WITHLAYERS.match(ln)
        if m:
            with_layers = (i, int(m.group(1)), int(m.group(2)), int(m.group(3)))
            continue
        m = RE_EXTRUDING.match(ln)
        if m:
            extruding.append((i, int(m.group(1)), int(m.group(2)),
                              float(m.group(3)), int(m.group(4))))
            continue
        m = RE_ADDED.match(ln)
        if m:
            added.append((i, int(m.group(1)), int(m.group(2)), float(m.group(3))))
            continue
        if RE_REQ_HDR.match(ln) and req_hdr_idx is None:
            req_hdr_idx = i
            continue
        if RE_ACH_HDR.match(ln) and ach_hdr_idx is None:
            # confirm the sub-header two lines on, else it is not the ach table
            if i + 1 < len(lines) and RE_ACH_SUB.match(lines[i + 1]):
                ach_hdr_idx = i
            continue

    if layer_phase is None and not outer_idx:
        raise Refusal(
            "no layer phase in this log: neither 'Shrinking and layer addition "
            "phase' nor any 'Outer iteration :' line. addLayers was not run."
        )

    # ---- request-table rows (REPORTED, NEVER USED AS ACHIEVEMENT) ----------
    if req_hdr_idx is not None:
        for ln in lines[req_hdr_idx + 3:]:
            m = RE_REQ_ROW.match(ln)
            if not m:
                if ln.strip() == "" or ln.strip().startswith("-"):
                    if request_rows:
                        break
                    continue
                break
            request_rows.append({
                "patch": m.group(1), "faces": int(m.group(2)),
                "layers_requested": int(m.group(3)),
                "near_wall_m": float(m.group(4)),
                "overall_m": float(m.group(5)),
            })

    # ---- the L-590 ordering assertion, executable ------------------------
    l590 = None
    if req_hdr_idx is not None and outer_idx:
        l590 = req_hdr_idx < outer_idx[0]
        if not l590:
            raise Refusal(
                "L-590 assertion failed: the per-patch 'avg thickness[m]' table "
                "at line %d is NOT before the first 'Outer iteration :' at line "
                "%d. This reader's whole premise is that that table is the "
                "request; refusing rather than guessing."
                % (req_hdr_idx + 1, outer_idx[0] + 1)
            )

    # ---- achievement-table rows ------------------------------------------
    ach_route = None
    if ach_hdr_idx is not None:
        if outer_idx and ach_hdr_idx < outer_idx[-1]:
            raise Refusal(
                "achievement table at line %d precedes the last 'Outer "
                "iteration :' at line %d; that is not an achievement."
                % (ach_hdr_idx + 1, outer_idx[-1] + 1)
            )
        for ln in lines[ach_hdr_idx + 3:]:
            m = RE_ACH_ROW.match(ln)
            if not m:
                if ln.strip() == "" or ln.strip().startswith("-"):
                    if achieved_rows:
                        break
                    continue
                break
            achieved_rows.append({
                "patch": m.group(1), "faces": int(m.group(2)),
                "layers_target": int(m.group(3)),
                "layers_in_mesh": float(m.group(4)),
                "overall_thickness_m": float(m.group(5)),
                "pct_of_wanted": float(m.group(6)),
            })
        ach_route = "table"
    elif outer_idx:
        # printLayerData() was never reached. Per snappyLayerDriver.C:5102-5110
        # the only way past that point without printing is nTotalAdded == 0.
        ach_route = "absent-table-implies-zero"
        for r in request_rows:
            achieved_rows.append({
                "patch": r["patch"], "faces": r["faces"],
                "layers_target": r["layers_requested"],
                "layers_in_mesh": 0.0,
                "overall_thickness_m": 0.0,
                "pct_of_wanted": 0.0,
            })

    # ---- corroboration channels ------------------------------------------
    net_cells = None
    if snapped and layer_mesh:
        net_cells = layer_mesh[1] - snapped[1]
    elif snapped and with_layers:
        net_cells = with_layers[1] - snapped[1]

    final_added = added[-1] if added else None
    final_extr  = extruding[-1] if extruding else None

    # ---- consistency between the channels --------------------------------
    disagreement = None
    if net_cells is not None and final_added is not None:
        if (net_cells == 0) != (final_added[1] == 0):
            disagreement = (
                "net cell gain (%d) and the final 'Added' line (%d) disagree on "
                "whether any layer survived" % (net_cells, final_added[1])
            )

    zero = None
    if net_cells is not None:
        zero = (net_cells == 0)
    elif final_added is not None:
        zero = (final_added[1] == 0)
    elif achieved_rows:
        zero = all(r["layers_in_mesh"] == 0.0 for r in achieved_rows)

    return {
        "log": os.path.abspath(path),
        "achievement_route": ach_route,
        "achieved_rows": achieved_rows,
        "request_rows_REPORTED_NOT_USED": request_rows,
        "l590_request_table_precedes_outer_iteration": l590,
        "snapped_mesh_cells": snapped[1] if snapped else None,
        "layer_mesh_cells": layer_mesh[1] if layer_mesh else None,
        "mesh_with_layers_cells": with_layers[1] if with_layers else None,
        "net_cells_added": net_cells,
        "final_added_cells": final_added[1] if final_added else None,
        "ideal_cells": final_added[2] if final_added else None,
        "final_added_pct": final_added[3] if final_added else None,
        "final_extruded_faces": final_extr[1] if final_extr else None,
        "final_extrudable_faces": final_extr[2] if final_extr else None,
        "final_extruded_pct": final_extr[3] if final_extr else None,
        "n_outer_iterations": len(outer_idx),
        "n_layer_iterations": len(extruding),
        "channels_disagree": disagreement,
        "achieved_is_zero": zero,
    }


# ----------------------------------------------------------------- the control
def _plant(src, dst):
    """Write a copy of src to dst carrying a KNOWN NON-ZERO achievement.

    Plants into all three achievement channels at once:
      (1) an achievement table after the last 'Outer iteration',
      (2) a 'Layer mesh' cell count raised by PLANT_NET_CELLS,
      (3) a final 'Added A out of B cells' line reading PLANT_ADDED_CELLS.
    A reader blind to any one of the three fails this control."""
    lines = _read_lines(src)

    snapped_cells = None
    last_added_i = None
    last_extr_i = None
    layer_mesh_i = None
    last_outer_i = None
    ach_hdr_i = None
    for i, ln in enumerate(lines):
        if ach_hdr_i is None and RE_ACH_HDR.match(ln) \
                and i + 1 < len(lines) and RE_ACH_SUB.match(lines[i + 1]):
            ach_hdr_i = i
        if RE_EXTRUDING.match(ln):
            last_extr_i = i
        m = RE_SNAPPED.match(ln)
        if m:
            snapped_cells = int(m.group(1))
        if RE_ADDED.match(ln):
            last_added_i = i
        if RE_LAYERMESH.match(ln) or RE_WITHLAYERS.match(ln):
            layer_mesh_i = i
        if RE_OUTER.match(ln):
            last_outer_i = i
    # 'Snapped mesh :' is absent from a layers-only restart; that channel is
    # then genuinely unavailable and the control says so rather than passing
    # silently. Every channel that IS present in the log must be plantable.
    missing = [n for n, v in (("Added ... cells", last_added_i),
                              ("Extruding ... faces", last_extr_i),
                              ("Layer mesh :/Mesh with layers :", layer_mesh_i),
                              ("Outer iteration :", last_outer_i))
               if v is None]
    if missing:
        raise Refusal(
            "cannot build the planted control from %s: it lacks %s. Refusing "
            "to report a zero from an unexercised reader." % (src, ", ".join(missing))
        )

    m = RE_ADDED.match(lines[last_added_i])
    ideal = int(m.group(2))
    lines[last_added_i] = (
        "Added %d out of %d cells (%.6f%%)."
        % (PLANT_ADDED_CELLS, ideal, 100.0 * PLANT_ADDED_CELLS / ideal)
    )
    m = RE_EXTRUDING.match(lines[last_extr_i])
    tot_faces = int(m.group(2))
    lines[last_extr_i] = (
        "Extruding %d out of %d faces (%.6f%%). Removed extrusion at 0 faces."
        % (PLANT_EXTRUDED_FCS, tot_faces, 100.0 * PLANT_EXTRUDED_FCS / tot_faces)
    )
    if snapped_cells is not None:
        m = RE_LAYERMESH.match(lines[layer_mesh_i]) \
            or RE_WITHLAYERS.match(lines[layer_mesh_i])
        if m is None:
            raise Refusal(
                "the line taken as the post-layer mesh-size line (%d) does not "
                "re-parse; refusing to plant blind." % (layer_mesh_i + 1)
            )
        lines[layer_mesh_i] = (
            "%s : cells:%d  faces:%s  points:%s"
            % (lines[layer_mesh_i].split(":")[0].strip(),
               snapped_cells + PLANT_NET_CELLS, m.group(2), m.group(3))
        )
    planted_row = ("%s %8d %8d %8s %8s  %8s"
                   % (PLANT_PATCH, PLANT_FACES, PLANT_TARGET,
                      PLANT_MESH_LAYERS, PLANT_THICKNESS_M, PLANT_PCT))

    if ach_hdr_i is not None:
        # The log ALREADY carries an achievement table and that is the table
        # the reader will use. Plant INTO IT -- overwrite its first data row,
        # located by scanning forward for the first line that parses as a row.
        # Planting a second table elsewhere would be invisible to the reader
        # and the control would pass while proving nothing.
        row_i = None
        for j in range(ach_hdr_i + 2, min(ach_hdr_i + 12, len(lines))):
            if RE_ACH_ROW.match(lines[j]):
                row_i = j
                break
        if row_i is None:
            raise Refusal(
                "found an achievement table header at line %d in %s but no "
                "parseable data row under it; refusing to plant blind."
                % (ach_hdr_i + 1, src)
            )
        lines[row_i] = planted_row
    else:
        base_cells = snapped_cells
        if base_cells is None:
            mm = RE_LAYERMESH.match(lines[layer_mesh_i]) \
                 or RE_WITHLAYERS.match(lines[layer_mesh_i])
            base_cells = int(mm.group(1))
        table = [
            "Mesh with layers : cells:%d  faces:1  points:1"
            % (base_cells + PLANT_NET_CELLS),
            "",
            "patch        faces        layers        overall thickness",
            "                      target   mesh     [m]       [%]",
            "-----        -----    -----    ----     ---       ---",
            planted_row,
            "",
        ]
        lines[layer_mesh_i + 1:layer_mesh_i + 1] = table

    with open(dst, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return dst


def run_control(src, keep_dir=None):
    """Plant, read the plant back FROM DISK through the same parse(), and
    refuse if any planted figure is invisible."""
    tmpdir = keep_dir or tempfile.mkdtemp(prefix="layer_plant_")
    os.makedirs(tmpdir, exist_ok=True)
    dst = os.path.join(tmpdir, "log.PLANTED")
    _plant(src, dst)

    got = parse(dst)          # <-- read back from disk, same code path
    fails = []

    if got["achievement_route"] != "table":
        fails.append("planted achievement TABLE not taken as the route "
                     "(route=%s)" % got["achievement_route"])
    rows = {r["patch"]: r for r in got["achieved_rows"]}
    if PLANT_PATCH not in rows:
        fails.append("planted patch %r invisible in achieved rows %r"
                     % (PLANT_PATCH, list(rows)))
    else:
        r = rows[PLANT_PATCH]
        if r["faces"] != PLANT_FACES:
            fails.append("faces %r != planted %d" % (r["faces"], PLANT_FACES))
        if r["layers_target"] != PLANT_TARGET:
            fails.append("layers_target %r != planted %d"
                         % (r["layers_target"], PLANT_TARGET))
        if abs(r["layers_in_mesh"] - PLANT_MESH_LAYERS) > 1e-9:
            fails.append("layers_in_mesh %r != planted %g"
                         % (r["layers_in_mesh"], PLANT_MESH_LAYERS))
        if abs(r["overall_thickness_m"] - PLANT_THICKNESS_M) > 1e-12:
            fails.append("overall_thickness_m %r != planted %g"
                         % (r["overall_thickness_m"], PLANT_THICKNESS_M))
        if abs(r["pct_of_wanted"] - PLANT_PCT) > 1e-9:
            fails.append("pct_of_wanted %r != planted %g"
                         % (r["pct_of_wanted"], PLANT_PCT))
    net_channel = ("Snapped mesh :" in open(src).read())
    if net_channel:
        if got["net_cells_added"] != PLANT_NET_CELLS:
            fails.append("net_cells_added %r != planted %d"
                         % (got["net_cells_added"], PLANT_NET_CELLS))
    if got["final_added_cells"] != PLANT_ADDED_CELLS:
        fails.append("final_added_cells %r != planted %d"
                     % (got["final_added_cells"], PLANT_ADDED_CELLS))
    if got["final_extruded_faces"] != PLANT_EXTRUDED_FCS:
        fails.append("final_extruded_faces %r != planted %d"
                     % (got["final_extruded_faces"], PLANT_EXTRUDED_FCS))
    if got["achieved_is_zero"] is not False:
        fails.append("achieved_is_zero %r on a planted NON-ZERO log"
                     % got["achieved_is_zero"])

    if not keep_dir:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return fails, dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--keep-plant", default=None,
                    help="directory to keep the planted control log in")
    a = ap.parse_args()

    if not os.path.isfile(a.log):
        sys.stderr.write("log not readable: %s\n" % a.log)
        return 3

    try:
        fails, plantpath = run_control(a.log, a.keep_plant)
    except Refusal as e:
        sys.stderr.write("REFUSED (planted control could not be built): %s\n" % e)
        return 2
    if fails:
        sys.stderr.write("REFUSED: planted control FAILED -- this reader cannot "
                         "be shown able to see a non-zero achievement, so any "
                         "zero it prints is not evidence.\n")
        for f in fails:
            sys.stderr.write("    %s\n" % f)
        return 2

    try:
        out = parse(a.log)
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        return 2

    out["planted_control"] = "PASS"
    out["plant_values"] = {
        "patch": PLANT_PATCH, "faces": PLANT_FACES, "layers_target": PLANT_TARGET,
        "layers_in_mesh": PLANT_MESH_LAYERS,
        "overall_thickness_m": PLANT_THICKNESS_M, "pct_of_wanted": PLANT_PCT,
        "net_cells_added": PLANT_NET_CELLS, "final_added_cells": PLANT_ADDED_CELLS,
        "final_extruded_faces": PLANT_EXTRUDED_FCS,
    }
    if a.keep_plant:
        out["planted_control_log"] = plantpath

    if a.json:
        print(json.dumps(out, indent=2))
        return 0

    print("LAYER ACHIEVEMENT READER -- %s" % out["log"])
    print("  planted control                 : PASS  (reader shown able to see "
          "a non-zero: %g m, %d net cells)" % (PLANT_THICKNESS_M, PLANT_NET_CELLS))
    print("  L-590 ordering assertion        : request table before 'Outer "
          "iteration' = %s" % out["l590_request_table_precedes_outer_iteration"])
    print("  achievement route               : %s" % out["achievement_route"])
    print("  outer iterations / layer iters  : %d / %d"
          % (out["n_outer_iterations"], out["n_layer_iterations"]))
    print("  snapped mesh cells              : %s" % out["snapped_mesh_cells"])
    print("  layer  mesh cells               : %s" % out["layer_mesh_cells"])
    print("  NET CELLS ADDED BY LAYERS       : %s"
          % ("UNAVAILABLE (no 'Snapped mesh :' baseline in this log -- "
             "layers-only restart)" if out["net_cells_added"] is None
             else out["net_cells_added"]))
    print("  final 'Added' cells / ideal     : %s / %s  (%s%%)"
          % (out["final_added_cells"], out["ideal_cells"], out["final_added_pct"]))
    print("  final 'Extruding' faces / total : %s / %s  (%s%%)"
          % (out["final_extruded_faces"], out["final_extrudable_faces"],
             out["final_extruded_pct"]))
    if out["channels_disagree"]:
        print("  CHANNELS DISAGREE               : %s" % out["channels_disagree"])
    print("  ACHIEVED LAYERS ARE ZERO        : %s" % out["achieved_is_zero"])
    print("  --- per patch, ACHIEVED ---")
    for r in out["achieved_rows"]:
        print("      %-16s faces %-9d target %-3d in mesh %-8g  "
              "thickness %-10g m  %g%% of wanted"
              % (r["patch"], r["faces"], r["layers_target"], r["layers_in_mesh"],
                 r["overall_thickness_m"], r["pct_of_wanted"]))
    print("  --- per patch, REQUESTED (reported for contrast, NEVER used as "
          "achievement -- L-590) ---")
    for r in out["request_rows_REPORTED_NOT_USED"]:
        print("      %-16s faces %-9d asked %-3d  near-wall %-10g m  "
              "overall %-10g m" % (r["patch"], r["faces"], r["layers_requested"],
                                   r["near_wall_m"], r["overall_m"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
