#!/usr/bin/env python3
"""check_snappy_layers.py -- post-snappyHexMesh layer/negative-volume GUARD.

WHY THIS EXISTS
---------------
snappyHexMesh prints

    Finished meshing without any errors

on a mesh to which it added ZERO boundary layers.  The banner is emitted after a
final face-quality check run on the POST-layer mesh; when layer addition has
collapsed to nothing, that mesh is just the clean snapped mesh, so the check is
trivially clean and the banner is truthful and useless.  Measured on this box
2026-09-11:

  DrivAer  verification/runs/navier_class/DRIVAER/DIAG_v3_coarse_explicitSnap_tol2_layersFixed
           log.snappyHexMesh:2835  Snapped mesh : cells:128230
           log.snappyHexMesh:4944  Extruding 0 out of 23365 faces (0%).
           log.snappyHexMesh:4945  Added 0 out of 116825 cells (0%).
           log.snappyHexMesh:4946  Layer mesh : cells:128230      <- IDENTICAL to snapped
           log.snappyHexMesh:4964  Finished meshing without any errors
           'Mesh with layers :' and the achieved-layer table: ABSENT.

  SUBOFF   verification/runs/navier_class/SUBOFF_A1/L2
           log.snappyHexMesh:3574  Snapped mesh : cells:6051099
           log.snappyHexMesh:6306  Extruding 443263 out of 444636 faces (99.691%).
           log.snappyHexMesh:6307ff Added 3070138 out of 3112452 cells (98.640%)
           log.snappyHexMesh:6312  Mesh with layers : cells:9121237
           achieved table: hull 7 target / 6.92 mesh ; sail 7 target / 6.88 mesh

THE RULE THIS GUARD ENFORCES
----------------------------
The banner is NEVER evidence.  A mesh passes only on the ACHIEVED numbers that
snappy printed: the final 'Added K out of C cells' fraction, the presence of the
'Mesh with layers :' line and its achieved per-patch table, a strictly positive
net cell gain over the snapped mesh, and a clean negative-volume verdict from
checkMesh.  Any of those missing or short -> REFUSE (exit 2).

checkMesh's exit code is meaningless in both directions on this box; this guard
reads the printed verdict lines, never rc.

THIS IS A TOOL, NOT A GATE.  BINDING LIMIT.
-------------------------------------------
--min-added-frac (default 0.70) and --min-mesh-layers (default 1.0) are the
AUTHOR'S CHOICE.  THEY ARE NOT PRE-REGISTERED THRESHOLDS.

Run this freely as a diagnostic.  But the moment its verdict is used to GRADE a
mesh family -- to award PASS or GATE FAIL to a rung -- the threshold must first
be pre-registered and committed under CLAUDE.md rule 2, BEFORE the mesh is
built.  Adopting the default after seeing a family's numbers is choosing the
gate to fit the answer, which is the one thing a pre-registration exists to
prevent.  (cfd-supervisor, 2026-09-11, adopting this as a binding limit after
nearly citing an inherited-sounding band that exists in no standard.)
"""

import argparse
import os
import re
import sys

EXIT_PASS = 0
EXIT_REFUSE = 2
EXIT_USAGE = 3

BANNER = "Finished meshing without any errors"

RE_SNAPPED = re.compile(r"^Snapped mesh\s*:\s*cells:(\d+)")
RE_LAYERMESH = re.compile(r"^Layer mesh\s*:\s*cells:(\d+)")
RE_MESHWITHLAYERS = re.compile(r"^Mesh with layers\s*:\s*cells:(\d+)")
RE_EXTRUDING = re.compile(
    r"^Extruding (\d+) out of (\d+) faces \(([0-9.eE+-]+)%\)")
RE_ADDED = re.compile(
    r"^Added (\d+) out of (\d+) cells \(([0-9.eE+-]+)%\)")
RE_ILLEGAL = re.compile(r"^Detected (\d+) illegal faces")
# achieved per-patch row: <patch> <faces> <target> <mesh> <thick_m> <thick_pct>
RE_ACHIEVED_ROW = re.compile(
    r"^\s*(\S+)\s+(\d+)\s+(\d+)\s+([0-9.]+)\s+([0-9.eE+-]+)\s+([0-9.]+)\s*$")

# checkMesh negative-volume verdict lines (printed verdicts, never rc)
RE_CM_NEGVOL_FLAG = re.compile(r"\*\*\*Zero or negative cell volume detected")
RE_CM_NEGVOL_COUNT = re.compile(
    r"Zero or negative cell volume detected[^0-9]*?(\d+)\s+cells", re.I)
RE_CM_NEGVOL_COUNT2 = re.compile(r"^\s*(\d+)\s+cells are zero or negative", re.I)


def read_lines(path):
    with open(path, "r", errors="replace") as fh:
        return fh.read().splitlines()


def parse_snappy(lines):
    """Everything the guard is allowed to believe, pulled off the log."""
    r = {
        "snapped_cells": None,
        "layer_mesh_cells": None,
        "mesh_with_layers_cells": None,
        "n_layer_iterations": 0,
        "last_extruded_faces": None,
        "total_extrudable_faces": None,
        "last_added_cells": None,
        "total_layer_cells": None,
        "added_frac": None,        # achieved layer cells / max possible
        "final_illegal_faces": None,
        "achieved_table": [],      # (patch, faces, target_layers, mesh_layers)
        "banner_present": False,
        "end_line_present": False,
    }
    in_achieved = False
    for i, ln in enumerate(lines):
        s = ln.rstrip()
        m = RE_SNAPPED.match(s)
        if m:
            r["snapped_cells"] = int(m.group(1))
            continue
        m = RE_LAYERMESH.match(s)
        if m:
            r["layer_mesh_cells"] = int(m.group(1))
            continue
        m = RE_MESHWITHLAYERS.match(s)
        if m:
            r["mesh_with_layers_cells"] = int(m.group(1))
            continue
        m = RE_EXTRUDING.match(s)
        if m:
            r["last_extruded_faces"] = int(m.group(1))
            r["total_extrudable_faces"] = int(m.group(2))
            r["n_layer_iterations"] += 1
            continue
        m = RE_ADDED.match(s)
        if m:
            r["last_added_cells"] = int(m.group(1))
            r["total_layer_cells"] = int(m.group(2))
            continue
        m = RE_ILLEGAL.match(s)
        if m:
            r["final_illegal_faces"] = int(m.group(1))
            continue
        if s.startswith(BANNER):
            r["banner_present"] = True
            continue
        if s.strip() == "End":
            r["end_line_present"] = True
            continue

        # achieved per-patch table.  Anchor ONLY on the 'target'/'mesh'
        # sub-header -- the *specification* table snappy prints BEFORE
        # extrusion has the columns 'near-wall overall' and must never be
        # mistaken for achievement.
        if ("target" in s and "mesh" in s
                and i > 0 and "overall thickness" in lines[i - 1]):
            in_achieved = True
            r["achieved_table"] = []
            continue
        if in_achieved:
            if s.strip().startswith("-----") or not s.strip():
                if r["achieved_table"] and not s.strip():
                    in_achieved = False
                continue
            m = RE_ACHIEVED_ROW.match(s)
            if m:
                r["achieved_table"].append(
                    (m.group(1), int(m.group(2)), int(m.group(3)),
                     float(m.group(4))))
            else:
                in_achieved = False

    if r["last_added_cells"] is not None and r["total_layer_cells"]:
        r["added_frac"] = r["last_added_cells"] / r["total_layer_cells"]
    return r


def parse_checkmesh(path):
    """Printed verdicts only.  rc is meaningless on this box, both ways."""
    lines = read_lines(path)
    neg = {"flag": False, "count": None, "mesh_ok": None}
    for ln in lines:
        if RE_CM_NEGVOL_FLAG.search(ln):
            neg["flag"] = True
        m = RE_CM_NEGVOL_COUNT.search(ln) or RE_CM_NEGVOL_COUNT2.match(ln)
        if m:
            neg["count"] = int(m.group(1))
        if "Mesh OK." in ln:
            neg["mesh_ok"] = True
        if "Failed" in ln and "mesh checks" in ln:
            neg["mesh_ok"] = False
    return neg


def find_logs(target):
    """target may be a case dir or a snappy log path."""
    if os.path.isfile(target):
        snap = target
        case = os.path.dirname(os.path.abspath(target))
    else:
        case = os.path.abspath(target)
        snap = os.path.join(case, "log.snappyHexMesh")
        if not os.path.isfile(snap):
            return None, []
    cms = []
    if os.path.isdir(case):
        for n in sorted(os.listdir(case)):
            if n.startswith("log.checkMesh"):
                cms.append(os.path.join(case, n))
    return snap, cms


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="REFUSE a snappyHexMesh result that added no layers or "
                    "left negative-volume cells.  Never reads the banner.")
    ap.add_argument("target", nargs="?",
                    help="case directory or path to log.snappyHexMesh")
    ap.add_argument("--min-added-frac", type=float, default=0.70,
                    help="minimum achieved layer cells / max possible "
                         "(default 0.70)")
    ap.add_argument("--min-mesh-layers", type=float, default=1.0,
                    help="minimum achieved mean layers on every patch listed "
                         "in the achieved table (default 1.0)")
    ap.add_argument("--layers-expected", action="store_true", default=True,
                    help="layers were requested (default; this guard exists "
                         "for that case)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the bidirectional mutation control and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.target:
        sys.stderr.write("check_snappy_layers: need a target\n")
        return EXIT_USAGE

    snap, cms = find_logs(args.target)
    if snap is None:
        sys.stderr.write(
            "REFUSE: no log.snappyHexMesh under %s\n" % args.target)
        return EXIT_REFUSE

    r = parse_snappy(read_lines(snap))
    refusals = []

    # --- layer evidence -------------------------------------------------
    if r["last_added_cells"] is None:
        refusals.append(
            "NO LAYER PHASE: log contains no 'Added N out of M cells' line at "
            "all -- snappy never entered layer addition (addLayers off, or it "
            "aborted before the layer phase).")
    else:
        if r["last_added_cells"] == 0:
            refusals.append(
                "ZERO LAYERS: final 'Added %d out of %d cells (0%%)' -- layer "
                "addition collapsed over %d iterations."
                % (r["last_added_cells"], r["total_layer_cells"],
                   r["n_layer_iterations"]))
        elif r["added_frac"] is not None and r["added_frac"] < args.min_added_frac:
            refusals.append(
                "INSUFFICIENT LAYERS: achieved %d/%d layer cells = %.3f%% < "
                "%.3f%% required."
                % (r["last_added_cells"], r["total_layer_cells"],
                   100.0 * r["added_frac"], 100.0 * args.min_added_frac))

    if args.layers_expected and r["mesh_with_layers_cells"] is None:
        refusals.append(
            "NO 'Mesh with layers :' LINE: snappy prints it only when layer "
            "addition produced a mesh; its absence is the zero-layer "
            "signature.")

    if args.layers_expected and not r["achieved_table"]:
        refusals.append(
            "NO ACHIEVED-LAYER TABLE: the per-patch 'target / mesh' table was "
            "never printed, so no patch has a measured layer count.")
    for (patch, faces, target, mesh) in r["achieved_table"]:
        if mesh < args.min_mesh_layers:
            refusals.append(
                "PATCH SHORT: %s achieved %.2f layers (target %d) < %.2f "
                "required." % (patch, mesh, target, args.min_mesh_layers))

    # --- net cell gain ---------------------------------------------------
    if r["snapped_cells"] is not None and r["layer_mesh_cells"] is not None:
        gain = r["layer_mesh_cells"] - r["snapped_cells"]
        if gain <= 0:
            refusals.append(
                "NET ZERO CELLS: layer mesh %d cells == snapped mesh %d cells "
                "(gain %d) -- the layer phase changed nothing."
                % (r["layer_mesh_cells"], r["snapped_cells"], gain))
    else:
        gain = None

    # --- negative volume, from checkMesh printed verdicts ----------------
    if not cms:
        refusals.append(
            "NO checkMesh LOG beside the case -- negative-volume count "
            "unmeasured; this guard refuses rather than assumes zero.")
    for cm in cms:
        neg = parse_checkmesh(cm)
        if neg["flag"] or (neg["count"] or 0) > 0:
            refusals.append(
                "NEGATIVE VOLUME: %s reports '***Zero or negative cell volume "
                "detected'%s."
                % (os.path.basename(cm),
                   "" if neg["count"] is None else " (%d cells)" % neg["count"]))

    # --- report -----------------------------------------------------------
    print("snappy log      : %s" % snap)
    print("checkMesh logs  : %s"
          % (", ".join(os.path.basename(c) for c in cms) or "(none)"))
    print("snapped cells   : %s" % r["snapped_cells"])
    print("layer mesh cells: %s  (net gain %s)" % (r["layer_mesh_cells"], gain))
    print("layer iterations: %d" % r["n_layer_iterations"])
    print("final extruded  : %s / %s faces"
          % (r["last_extruded_faces"], r["total_extrudable_faces"]))
    print("ACHIEVED layers : %s / %s cells = %s"
          % (r["last_added_cells"], r["total_layer_cells"],
             "n/a" if r["added_frac"] is None
             else "%.3f%%" % (100.0 * r["added_frac"])))
    print("achieved table  : %s"
          % (", ".join("%s %.2f/%d" % (p, m, t)
                       for (p, f, t, m) in r["achieved_table"]) or "(ABSENT)"))
    print("final illegal   : %s" % r["final_illegal_faces"])
    print("banner present  : %s   [NOT USED AS EVIDENCE]" % r["banner_present"])

    if refusals:
        print("")
        for x in refusals:
            print("REFUSE: %s" % x)
        print("")
        print("VERDICT: GATE FAIL (%d refusal%s)"
              % (len(refusals), "" if len(refusals) == 1 else "s"))
        return EXIT_REFUSE

    print("")
    print("VERDICT: PASS")
    return EXIT_PASS


# ---------------------------------------------------------------------------
# Anti-no-op control.
#
# Five guards were found in this lab on 2026-09-11 that could not fire: a silent
# no-op decimation control, the same control defeated by an arithmetic
# coincidence, a swap control whose two test patches had identical face counts,
# a hardcoded passing plant, and a plateau limb that could not fail.  A control
# whose fixture makes it a no-op reads identically to a control that passed.
#
# So this selftest is BIDIRECTIONAL and mutates ONLY the fields the guard claims
# to read.  A PASS fixture must flip to REFUSE when its achieved numbers are
# edited down, and a REFUSE fixture must flip to PASS when its achieved numbers
# are edited up.  A guard that does not flip both ways is reading something else.
# ---------------------------------------------------------------------------

PASS_FIXTURE = ("/home/ubuntu/Certonomous/verification/runs/navier_class/"
                "SUBOFF_A1/L2")
FAIL_FIXTURE = ("/home/ubuntu/Certonomous/verification/runs/navier_class/"
                "DRIVAER/DIAG_v3_coarse_explicitSnap_tol2_layersFixed")


def _run_quiet(argv):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def selftest():
    import shutil
    import tempfile
    ok = True

    def report(name, got, want):
        nonlocal ok
        good = (got == want)
        ok = ok and good
        print("  %-58s rc=%d want=%d  %s"
              % (name, got, want, "ok" if good else "*** FAILED"))

    print("check_snappy_layers --selftest")
    print("")
    print("A. live fixtures (unmodified logs on disk)")
    rc, _ = _run_quiet([PASS_FIXTURE])
    report("SUBOFF_A1/L2 (98.640%% layers)", rc, EXIT_PASS)
    rc, _ = _run_quiet([FAIL_FIXTURE])
    report("DRIVAER DIAG_v3 (0%% layers)", rc, EXIT_REFUSE)

    tmp = tempfile.mkdtemp(prefix="snappyguard_")
    try:
        # B. PASS fixture mutated DOWN -> must REFUSE.
        # Only the achieved 'Added' line and the achieved table are touched.
        d = os.path.join(tmp, "pass_mutated_down")
        shutil.copytree(PASS_FIXTURE, d,
                        ignore=lambda s, n: [x for x in n
                                             if not x.startswith("log.")])
        p = os.path.join(d, "log.snappyHexMesh")
        txt = read_lines(p)
        out, n_added, n_tab = [], 0, 0
        for ln in txt:
            m = RE_ADDED.match(ln)
            if m:
                out.append("Added 0 out of %s cells (0%%)" % m.group(2))
                n_added += 1
                continue
            m = RE_ACHIEVED_ROW.match(ln)
            if m and n_tab < 8:
                out.append("%s %s %s 0.00 %s %s"
                           % (m.group(1), m.group(2), m.group(3),
                              m.group(5), m.group(6)))
                n_tab += 1
                continue
            out.append(ln)
        assert n_added > 0, "mutation touched no 'Added' line -- NO-OP FIXTURE"
        assert n_tab > 0, "mutation touched no achieved row -- NO-OP FIXTURE"
        with open(p, "w") as fh:
            fh.write("\n".join(out) + "\n")
        rc, _ = _run_quiet([d])
        report("SUBOFF L2 with Added->0 (%d lines, %d rows)" % (n_added, n_tab),
               rc, EXIT_REFUSE)

        # C. FAIL fixture mutated UP -> must PASS.
        # Give it the layer evidence it lacks; nothing else changes.
        d2 = os.path.join(tmp, "fail_mutated_up")
        shutil.copytree(FAIL_FIXTURE, d2,
                        ignore=lambda s, n: [x for x in n
                                             if not x.startswith("log.")])
        p2 = os.path.join(d2, "log.snappyHexMesh")
        txt = read_lines(p2)
        out, n_added, n_lm = [], 0, 0
        for ln in txt:
            m = RE_ADDED.match(ln)
            if m:
                tot = int(m.group(2))
                out.append("Added %d out of %d cells (98.5%%)"
                           % (int(tot * 0.985), tot))
                n_added += 1
                continue
            m = RE_LAYERMESH.match(ln)
            if m:
                out.append("Mesh with layers : cells:%d" % (int(m.group(1)) * 3))
                out.append("")
                out.append("patch faces        layers        overall thickness")
                out.append("              target   mesh     [m]       [%]")
                out.append("----- -----    -----    ----     ---       ---")
                out.append("BodySide 1698   5        4.90     0.0061    99.0")
                out.append("")
                out.append("Layer mesh : cells:%d" % (int(m.group(1)) * 3))
                n_lm += 1
                continue
            out.append(ln)
        assert n_added > 0, "mutation touched no 'Added' line -- NO-OP FIXTURE"
        assert n_lm > 0, "mutation touched no 'Layer mesh' line -- NO-OP FIXTURE"
        # the DrivAer DIAG case also carries a real negative-volume checkMesh;
        # drop that one file so this limb isolates the LAYER fields only.
        for n in os.listdir(d2):
            if n.startswith("log.checkMesh"):
                os.remove(os.path.join(d2, n))
        with open(os.path.join(d2, "log.checkMesh"), "w") as fh:
            fh.write("Mesh OK.\nEnd\n")
        with open(p2, "w") as fh:
            fh.write("\n".join(out) + "\n")
        rc, _ = _run_quiet([d2])
        report("DrivAer with layer evidence planted (%d, %d)" % (n_added, n_lm),
               rc, EXIT_PASS)

        # D. banner-only control: strip EVERY achieved number, keep the banner.
        # The banner alone must never pass.
        d3 = os.path.join(tmp, "banner_only")
        os.makedirs(d3)
        with open(os.path.join(d3, "log.snappyHexMesh"), "w") as fh:
            fh.write("Snapped mesh : cells:128230\n"
                     "Layer mesh : cells:128230\n"
                     "Finished meshing without any errors\n"
                     "Finished meshing in = 109.5 s.\nEnd\n")
        with open(os.path.join(d3, "log.checkMesh"), "w") as fh:
            fh.write("Mesh OK.\nEnd\n")
        rc, _ = _run_quiet([d3])
        report("banner present, zero achieved numbers", rc, EXIT_REFUSE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("SELFTEST: %s" % ("PASS" if ok else "FAIL"))
    return EXIT_PASS if ok else EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())
