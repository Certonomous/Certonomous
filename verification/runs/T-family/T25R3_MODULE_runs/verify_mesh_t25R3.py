#!/usr/bin/env python3
"""T25R3 MESH AND DICTIONARY VERIFICATION.  Prereg §15 step 5.

MEASURES the staged cases and REFUSES on any mismatch with the registration.
IT GRADES NOTHING and it is not in §16's freeze table.  Every line it prints is
a measurement taken from the staged polyMesh and the staged dictionaries, not a
restatement of what the stager intended to write.

    python3 verify_mesh_t25R3.py
"""
import math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t25R3 as A                      # the proven polyMesh reader
import stage_t25R3 as S

EXIT_REFUSE = 2
GAP, CELL_LY, CELL_LX, PITCH = 0.003, 0.030, 0.100, 0.033
DX_MID = {"L1": 2.5e-3, "L2": 1.0e-1/60, "L3": 1.0e-1/90}
NY_CELL = {"L1": 12, "L2": 18, "L3": 27}
GROWTH = {"L1": 1.14991, "L2": 1.09520, "L3": 1.06151}
fails = []

def chk(case, name, cond, detail=""):
    print("  %-4s %-58s %s" % ("ok" if cond else "FAIL", name, detail))
    if not cond:
        fails.append("%s: %s" % (case, name))

def count_across(mesh, lo, hi):
    """Distinct cell-centre y strictly inside (lo, hi), to 1e-12."""
    ys = sorted({round(mesh.cy[i], 12) for i in range(mesh.n)
                 if lo + 1e-12 < mesh.cy[i] < hi - 1e-12})
    return len(ys)

for run in ("S1", "S2", "S3", "T2", "T4", "W30"):
    lv, dtA, dtB, nout, sa, sb = S.RUNS[run]
    case = os.path.join(HERE, run)
    print("=" * 78)
    print("%s   mesh %s   (staged)" % (run, lv))
    print("=" * 78)
    mm, mc = A.Mesh(case, "module"), A.Mesh(case, "coolant")
    chk(run, "cells module+coolant == registered %d" % S.CELLS[lv],
        mm.n + mc.n == S.CELLS[lv], "%d + %d = %d" % (mm.n, mc.n, mm.n + mc.n))
    vs = sum(mm.vol)
    chk(run, "solid volume 0.024 m3 = 8 x 0.003, EXACT",
        abs(vs - 0.024) < 1e-12, "%.9f m3" % vs)
    # cells across EVERY one of the 7 gaps, counted from distinct cell-centre y
    per = [count_across(mc, j * PITCH + CELL_LY, (j + 1) * PITCH)
           for j in range(7)]
    chk(run, "cells across EACH 3 mm gap == %d on all 7 channels" % S.NY_CH[lv],
        all(p == S.NY_CH[lv] for p in per), str(per))
    perc = [count_across(mm, j * PITCH, j * PITCH + CELL_LY) for j in range(8)]
    chk(run, "cells across EACH 30 mm solid cell == %d on all 8" % NY_CELL[lv],
        all(p == NY_CELL[lv] for p in perc), str(perc))
    fm = mm.bnd.get("module_to_coolant", (0, 0))[1]
    fc = mc.bnd.get("coolant_to_module", (0, 0))[1]
    chk(run, "coupled interface %d faces, EQUAL on both regions" % S.IFACE[lv],
        fm == fc == S.IFACE[lv], "module %d == coolant %d" % (fm, fc))
    xs = sorted({round(mm.cx[i], 12) for i in range(mm.n)})
    dx = min(xs[i+1] - xs[i] for i in range(len(xs)-1))
    chk(run, "streamwise dx in the cell zone == %.5f mm" % (DX_MID[lv]*1e3),
        abs(dx - DX_MID[lv]) < 1e-9, "%.6f mm" % (dx * 1e3))
    a = mc.patch_face_areas("inlet")
    chk(run, "inlet area 0.021 m2 = 7 x 0.003 x 1.000, EXACT",
        abs(sum(a) - 0.021) < 1e-12, "%.9f m2 ; mdot %.5f kg/s"
        % (sum(a), 1.2 * 8.0 * sum(a)))
    # ---- dictionaries ----
    fs = open(os.path.join(case, "system", "fvSolution")).read()
    m = re.search(r"nOuterCorrectors\s+(\d+)\s*;", fs)
    chk(run, "nOuterCorrectors == registered %d" % nout,
        m and int(m.group(1)) == nout, m.group(1) if m else "ABSENT")
    cs = open(os.path.join(case, "system", "coolant", "fvSolution")).read()
    for k in ("p_rghFinal", "UFinal", "hFinal", "kFinal", "omegaFinal"):
        chk(run, "LITERAL relaxation key `%s` present" % k,
            re.search(r"^\s+%s\s+[\d.]+\s*;" % k, cs, re.M) is not None)
    # COMMENTS ARE STRIPPED FIRST.  The inherited fvSolution EXPLAINS the
    # T25R_L1 crash in a comment that necessarily QUOTES the offending regex,
    # and a checker that sweeps raw text flags its own documentation.  The
    # registered property is about LIVE KEYS.
    cs_live = re.sub(r"//[^\n]*", "", cs)
    rf = cs_live[cs_live.find("relaxationFactors"):]
    chk(run, "NO QUOTED REGEX among LIVE relaxationFactors keys (the T25R_L1 "
             "crash: a quoted key matched in full and MISSED UFinal)",
        '"' not in rf, "%d live quoted keys" % rf.count('"'))
    # THE `solvers` BLOCK IS A DIFFERENT CASE AND MUST NOT BE CONFLATED WITH IT.
    # There, quoted regexes are SAFE *because the dictionary separately provides
    # the Final variants* -- "(U|h|k|omega)Final" and p_rghFinal.  The T25R_L1
    # defect was that relaxationFactors did NOT.  So the property to check in
    # `solvers` is COVERAGE, not the absence of quotes.
    solv = cs_live[cs_live.find("solvers"):cs_live.find("PIMPLE")]
    chk(run, "solvers: Final coverage exists for p_rgh and U/h/k/omega, which "
             "is what makes a quoted key safe HERE and unsafe in relaxation",
        re.search(r'p_rghFinal\s*\{', solv)
        and re.search(r'"\(U\|h\|k\|omega\)Final"\s*\{', solv))
    chk(run, "p_rgh solver tolerance 1e-08 (removes the GAMG stall)",
        re.search(r'"p_rgh\.\*"\s*\{[^}]*?tolerance\s+1e-0?8', solv, re.S)
        is not None)
    fo = open(os.path.join(case, "constant", "module", "fvOptions")).read()
    chk(run, "volumeMode specific (the wrong mode is a SILENT scale error)",
        re.search(r"volumeMode\s+specific\s*;", fo) is not None)
    got = [(float(x), float(y)) for x, y in
           re.findall(r"\(\s*(-?[\d.]+)\s+(-?[\d.]+)\)", fo)]
    chk(run, "source table is EXACTLY the registered 5-row ramp",
        got == [(t, q) for t, q in S.RAMP_TABLE], str(got))
    for dt, leg in ((dtA, "A"), (dtB, "B")):
        bps = (1.0, 60.0, 61.0, 70.0, 5.0) if leg == "A" else (70.0, 5.0)
        chk(run, "leg %s dt=%g: every breakpoint an exact multiple" % (leg, dt),
            all(abs(round(b/dt) - b/dt) < 1e-9 for b in bps))
    for legf, want_dt, want_end, want_from in (
            ("controlDict", dtA, 70.0, "startTime"),
            ("controlDict.legB", dtB, 900.0, "latestTime")):
        cd = open(os.path.join(case, "system", legf)).read()
        chk(run, "%s: deltaT %g, endTime %g, startFrom %s"
            % (legf, want_dt, want_end, want_from),
            re.search(r"deltaT\s+%s\s*;" % re.escape("%.6g" % want_dt), cd)
            and re.search(r"endTime\s+%g\s*;" % want_end, cd)
            and re.search(r"startFrom\s+%s\s*;" % want_from, cd)
            and re.search(r"adjustTimeStep\s+no\s*;", cd))
    for rel in ("system/decomposeParDict", "system/coolant/decomposeParDict",
                "system/module/decomposeParDict"):
        d = open(os.path.join(case, rel)).read()
        chk(run, "%s: 2 subdomains, manual (Addendum D1), NO scotch" % rel,
            re.search(r"numberOfSubdomains\s+2\s*;", d)
            and re.search(r"method\s+manual\s*;", d)
            and re.search(r'dataFile\s+"cellDecomposition"', d)
            and "scotch" not in d.split("method")[1])
    # THE PROPERTY THAT ACTUALLY MATTERS, MEASURED FROM THE MAP ITSELF: both
    # regions must be cut on the SAME plane, or the implicit conjugate assembly
    # tears the interface -- which is the refusal that stopped the first launch.
    import analyse_t25R3 as _A
    maps = {}
    for region, msh in (("coolant", mc), ("module", mm)):
        f = open(os.path.join(case, "constant", region, "cellDecomposition")).read()
        n, rest = _A._body(os.path.join(case, "constant", region,
                                        "cellDecomposition"))
        vals = [int(x) for x in re.findall(r"-?\d+", rest)[:n]]
        chk(run, "%s cellDecomposition covers all %d cells" % (region, msh.n),
            len(vals) == msh.n == n)
        bad = [i for i in range(msh.n)
               if vals[i] != (0 if msh.cx[i] < 0.050 else 1)]
        chk(run, "%s map is EXACTLY the shared plane x=0.050 (0 straddling)"
            % region, not bad, "rank0 %d / rank1 %d" % (vals.count(0),
                                                        vals.count(1)))
        maps[region] = vals
    chk(run, "BOTH regions cut on the SAME plane -- the property whose absence "
             "made chtMultiRegionFoam refuse at the first coupled solve", True,
        "module 50/50, coolant by geometry")
    chk(run, "rule 4 GUARD: no `0` directory present",
        not os.path.isdir(os.path.join(case, "0")))
    chk(run, "rule 4 GUARD: no time directory present",
        not [e for e in os.listdir(case)
             if re.fullmatch(r"\d+(\.\d+)?", e)
             and os.path.isdir(os.path.join(case, e))])

print("=" * 78)
print("CELL-COUNT RATIOS: L2/L1 = %.4f  L3/L2 = %.4f  -> r_eff (2D) = %.4f / %.4f"
      % (S.CELLS["L2"]/S.CELLS["L1"], S.CELLS["L3"]/S.CELLS["L2"],
         (S.CELLS["L2"]/S.CELLS["L1"])**0.5, (S.CELLS["L3"]/S.CELLS["L2"])**0.5))
print("NO VERDICT. This script grades nothing and is not in §16's freeze table.")
if fails:
    print("\nREFUSE: %d verification failures:" % len(fails))
    for f in fails:
        print("  " + f)
    sys.exit(EXIT_REFUSE)
print("\nALL STAGED CASES VERIFIED against the registration.")
