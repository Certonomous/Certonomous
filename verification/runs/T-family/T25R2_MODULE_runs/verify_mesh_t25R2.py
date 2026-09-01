#!/usr/bin/env python3
"""T25R2 PRE-SOLVE MESH VERIFICATION.

*** THIS SCRIPT GRADES NOTHING AND IS NOT IN SECTION 11's FREEZE TABLE. ***
It emits no word from the fixed vocabulary and no verdict.  It MEASURES the
staged meshes against the numbers section 2.2 of the frozen document registers,
so that "the mesh is correct" is a measurement rather than an inherited
sentence, and it REFUSES (exit 2) on any mismatch.

Ordered by `heat-transfer-supervisor` at section 10 step 3: *"Stage and verify
the mesh before solving -- 16,608 (L1) / 37,368 (L2), ratio 2.2500, 24 cells
across each 3 mm channel."*

WHY THE CELL COUNTS ARE NOT ENOUGH ON THEIR OWN.  7 x 76 x 24 = 12,768 and
8 x 40 x 12 = 3,840 are arithmetic identities that a WRONG mesh with
compensating factors could also satisfy.  The gap resolution is therefore
counted GEOMETRICALLY -- distinct cell-centre `y` values inside one 3 mm gap at
one streamwise station -- and the streamwise spacing is measured from the cell
boxes, not inferred from `NX`.

It starts no external program: no subprocess, no os.system, no os.exec*.

Usage: python3 verify_mesh_t25R2.py [--out FILE]
Exit:  0 every measurement matches the registration, 2 REFUSAL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t25R2 as A                                       # noqa: E402

# Section 2.2 of the frozen document, transcribed.
REG = {
    "L1": dict(module=3840, coolant=12768, total=16608, gap_ny=24, cell_ny=12,
               nx_cellzone=40, dx=0.0025),
    "L2": dict(module=8640, coolant=28728, total=37368, gap_ny=36, cell_ny=18,
               nx_cellzone=60, dx=0.0025 / 1.5),
}
# Section 4.4: the registered inlet area and mass flow.
INLET_AREA = 7 * 0.003 * 1.000            # 0.021 m2
MDOT = 1.2 * 8.0 * INLET_AREA             # 0.20160 kg/s
TOL = 1e-12


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def _uniq(vals, tol=1e-10):
    out = []
    for v in sorted(vals):
        if not out or abs(v - out[-1]) > tol:
            out.append(v)
    return out


def verify(case, lines):
    d = os.path.join(HERE, case)
    lvl = A.LEVEL[case]
    reg = REG[lvl]
    say = lines.append
    say("=" * 72)
    say("%s   (mesh %s)   source-reused, section 2.5" % (case, lvl))
    say("=" * 72)

    mm = A.Mesh(d, "module")
    mc = A.Mesh(d, "coolant")

    # ---- 1. CELL COUNTS, read from the mesh, not from a log.
    if mm.n != reg["module"] or mc.n != reg["coolant"]:
        refuse("%s: module %d / coolant %d cells, not the registered %d / %d"
               % (case, mm.n, mc.n, reg["module"], reg["coolant"]))
    tot = mm.n + mc.n
    if tot != reg["total"]:
        refuse("%s: %d total cells, not the registered %d"
               % (case, tot, reg["total"]))
    say("  cells        module %6d + coolant %6d = %6d   (registered %d)"
        % (mm.n, mc.n, tot, reg["total"]))

    # ---- 2. TOTAL SOLID VOLUME -- an independent check on the geometry.
    vs = sum(mm.vol)
    want_vs = A.N_CELLS * A.V_CELL
    if abs(vs - want_vs) > 1e-12:
        refuse("%s: solid volume %.12g m3, not the registered 8 x %.6g = %.12g"
               % (case, vs, A.V_CELL, want_vs))
    say("  solid volume %.12g m3 = 8 x %.6g m3   (section 2.1 geometry, EXACT)"
        % (vs, A.V_CELL))

    # ---- 3. *** 24 CELLS ACROSS EACH 3 mm CHANNEL, COUNTED GEOMETRICALLY. ***
    #      One streamwise station inside the cell zone, one gap, distinct cell
    #      centre y values.  Not inferred from NX.
    x0 = min(b[0][0] for b in mc.box)
    xs = _uniq([c for c in mc.cx])
    # a station comfortably inside the cell zone x in [0, 0.100]
    station = min((x for x in xs if 0.02 < x < 0.08), key=lambda v: abs(v - 0.05))
    per_gap = []
    for g in range(7):
        ylo = A.CELL_LY + g * A.PITCH
        yhi = ylo + A.GAP
        ys = [mc.cy[i] for i in range(mc.n)
              if abs(mc.cx[i] - station) < 1e-12 and ylo - 1e-12 < mc.cy[i] < yhi + 1e-12]
        per_gap.append(len(_uniq(ys)))
    if len(set(per_gap)) != 1 or per_gap[0] != reg["gap_ny"]:
        refuse("%s: cells across the 3 mm gaps measured %r at x = %.6g m, not "
               "the registered %d on every one of the 7 channels"
               % (case, per_gap, station, reg["gap_ny"]))
    say("  ACROSS EACH 3 mm GAP: %d cells, on all 7 channels, COUNTED from "
        "distinct cell-centre y at x = %.6g m   (registered %d)"
        % (per_gap[0], station, reg["gap_ny"]))

    # ---- 4. cells across each 30 mm solid cell, likewise.
    ms = _uniq([c for c in mm.cx])
    mstation = min((x for x in ms if 0.02 < x < 0.08), key=lambda v: abs(v - 0.05))
    per_cell = []
    for j in range(A.N_CELLS):
        ylo = j * A.PITCH
        yhi = ylo + A.CELL_LY
        ys = [mm.cy[i] for i in range(mm.n)
              if abs(mm.cx[i] - mstation) < 1e-12
              and ylo - 1e-12 < mm.cy[i] < yhi + 1e-12]
        per_cell.append(len(_uniq(ys)))
    if len(set(per_cell)) != 1 or per_cell[0] != reg["cell_ny"]:
        refuse("%s: cells across the 30 mm solid cells measured %r, not the "
               "registered %d" % (case, per_cell, reg["cell_ny"]))
    say("  ACROSS EACH 30 mm CELL: %d cells, on all 8 cells   (registered %d)"
        % (per_cell[0], reg["cell_ny"]))

    # ---- 5. STREAMWISE SPACING in the cell zone, MEASURED from cell boxes.
    dxs = _uniq([b[1][0] - b[0][0] for i, b in enumerate(mm.box)])
    if len(dxs) != 1 or abs(dxs[0] - reg["dx"]) > 1e-12:
        refuse("%s: module streamwise spacings %r, not the single registered "
               "%.12g m" % (case, dxs, reg["dx"]))
    say("  STREAMWISE dx in the cell zone: %.6g mm, uniform   (registered "
        "%.6g mm)" % (1000 * dxs[0], 1000 * reg["dx"]))

    # ---- 6. INLET AREA and the mass flow section 4.4 predicts from it.
    a_in = sum(mc.patch_face_areas("inlet"))
    if abs(a_in - INLET_AREA) > 1e-12:
        refuse("%s: coolant inlet area %.12g m2, not the registered %.12g"
               % (case, a_in, INLET_AREA))
    say("  INLET AREA %.12g m2 = 7 x 0.003 x 1.000, EXACT; mdot at rho 1.2, "
        "U 8 = %.5f kg/s   (section 4.4 registers %.5f)"
        % (a_in, 1.2 * 8.0 * a_in, MDOT))

    # ---- 7. the interface patch exists on BOTH regions.
    for region, m in (("module", mm), ("coolant", mc)):
        want = A.IFACE[region]
        if want not in m.bnd:
            refuse("%s: %s carries no %s patch; it has %s"
                   % (case, region, want, ",".join(sorted(m.bnd))))
    nf_m = mm.bnd[A.IFACE["module"]][1]
    nf_c = mc.bnd[A.IFACE["coolant"]][1]
    if nf_m != nf_c:
        refuse("%s: the coupled interface has %d faces on module and %d on "
               "coolant -- they must match face for face" % (case, nf_m, nf_c))
    # 14 cell/channel contacts (7 channels x 2 faces) x NX over the cell zone
    want_iface = 14 * reg["nx_cellzone"]
    if nf_m != want_iface:
        refuse("%s: the coupled interface carries %d faces, not the %d implied "
               "by 7 channels x 2 faces x NX %d over the cell zone"
               % (case, nf_m, want_iface, reg["nx_cellzone"]))
    say("  COUPLED INTERFACE: %d faces on module == %d on coolant = 7 channels "
        "x 2 faces x NX %d   (section 2.5's registered assertion)"
        % (nf_m, nf_c, reg["nx_cellzone"]))

    # ---- 8. the numerics and the pulse, re-read from the staged dictionaries.
    nc = A.numerics_check(d, case)
    pt = A.pulse_table_check(d, case)
    mq = A.mesh_quality(d)
    say("  numerics     nOuterCorrectors %d (registered %d); five LITERAL "
        "final-sweep keys present; p_rgh tolerance %g"
        % (nc["nOuterCorrectors"], A.NOUTER[case], nc["p_rgh_tol"]))
    say("  pulse        %r W/m3, no step time inside the ramp at deltaT %g"
        % (pt["table"], pt["deltaT"]))
    for r in A.REGIONS:
        say("  checkMesh %-8s Mesh OK=%s maxNonOrth=%.4g (<70) maxSkew=%.4g "
            "(<4)" % (r, mq[r]["mesh_ok"], mq[r]["nonorth"], mq[r]["skew"]))
    say("  0 / time dirs present: %r  (rule 4's guard requires NONE)"
        % sorted(x for x in os.listdir(d)
                 if x == "0" or x.replace(".", "").isdigit()))
    return tot


def main(argv):
    lines = []
    tots = {}
    for case in A.CASES:
        tots[case] = verify(case, lines)
    lines.append("=" * 72)
    r = float(tots["T25R2_L2"]) / tots["T25R2_L1"]
    if abs(r - 2.25) > 1e-12:
        refuse("cell-count ratio L2/L1 = %.12g, not the registered 2.2500 "
               "(= r^2 at r = 1.5 in two resolved directions)" % r)
    lines.append("CELL-COUNT RATIO L2/L1 = %.4f EXACTLY = r^2 at r = 1.5 in "
                 "two resolved directions   (section 2.2)" % r)
    lines.append("The two L1 arms share one mesh: T25R2_L1 %d == T25R2_L1_OC20 "
                 "%d." % (tots["T25R2_L1"], tots["T25R2_L1_OC20"]))
    lines.append("The two L2 arms share one mesh: T25R2_L2 %d == "
                 "T25R2_L2_DT025 %d." % (tots["T25R2_L2"],
                                         tots["T25R2_L2_DT025"]))
    lines.append("")
    lines.append("NO VERDICT. This script grades nothing and is not in section "
                 "11's freeze table. Every line above is a MEASUREMENT taken "
                 "from the staged polyMesh and the staged dictionaries.")
    txt = "\n".join(lines)
    print(txt)
    if "--out" in argv:
        p = argv[argv.index("--out") + 1]
        open(p, "w").write(txt + "\n")
    return 0


def _guarded(argv, _fn=None):
    fn = main if _fn is None else _fn
    try:
        return fn(argv)
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        print("REFUSE: verify_mesh_t25R2.py raised an uncaught exception. A "
              "CRASHED VERIFIER HAS VERIFIED NOTHING and exits 2.")
        return 2


if __name__ == "__main__":
    sys.exit(_guarded(sys.argv[1:]))
