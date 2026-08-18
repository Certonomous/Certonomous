#!/usr/bin/env python3
"""build_k2bU3.py -- K2b-U3: does the 2D limit cycle survive in 3D?

    python3 build_k2bU3.py        # writes K2bU3_M (2D control) and K2bU3_D (3D)

Pre-registered in `K2b_3D_UNSTEADINESS_PREREGISTRATION.md`, sha256
91a26fc9327f3bc425a5c21bd9efe5d4e49c7127729aafc51dadd2652cc81695, written and
hashed BEFORE either case was built or run.

TWO CASES, AND THE FIRST IS A GATE ON THE SECOND
------------------------------------------------
The 3D mesh affordable inside ~11 core-minutes is h = 0.1 m -- EIGHT TIMES
COARSER than the 12.5 mm slice the 6.000 s limit cycle was found on. So a 3D run
showing no oscillation would be ambiguous between "three-dimensionality damped
it" and "the coarse mesh damped it", which are opposite conclusions.

  K2bU3_M   THE GATE. The same 2D slice, same 70 % provisioning, same transient
            solver, at the 3D test's own 100 mm resolution. Does the limit cycle
            survive coarsening ALONE? If not, Test D cannot separate mesh from
            dimensionality and the question is unanswerable at this price.
  K2bU3_D   THE TEST. Full 3D module, N = 4 racks, OPEN row ends -- the spanwise
            freedom a slice structurally cannot have -- same 100 mm cell.

Both start from a UNIFORM field at T_sup and run 80 s, of which the first 40 s
are discarded as development (the 3D room turnover at 70 % provisioning is
~35 s). Graded on 60-80 s against 40-60 s.

THE ALIASING GUARD
------------------
A period sampled too coarsely aliases into something that looks like decay. At
maxCo 2 and h = 0.1 with max|U| ~ 1.2 m/s the step is ~0.167 s, giving ~36 steps
and ~30 monitor samples per 6.000 s period, against a pre-registered floor of 20
and 10. `analyse_k2bU3.py` recomputes both from the log and REFUSES rather than
grading if either falls short.
"""
import os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_k2b as B

H_CELL, END_TIME, MON_INT, MAX_CO, QV_TILE = 0.1, 80.0, 0.2, 2.0, 0.245
WRITE_INT = 20.0

# ---- 3D interval structure, parameterised by cell size ----------------------
XS = [0.0, 0.6, 1.2, 1.8, 2.4, 3.0, 3.6]
YS = [0.0, 0.6, B.W_CA, B.W_CA + B.D_R, 2.6, 3.2, B.W_CA + B.D_R + B.W_HA]
ZS = [0.0, B.H_R, B.H_ROOM]
RACK_XI, RACK_YI, RACK_ZI, TILE_YI, RETURN_YI = (1, 2, 3, 4), 2, 0, 1, 4
N_RACKS = len(RACK_XI)
WALLS3 = ["floor", "ceiling", "wall_cold", "wall_hot", "wall_x0", "wall_x1",
          "rack_top", "rack_end"]
RIN = [f"rack{r}_in" for r in range(N_RACKS)]
ROUT = [f"rack{r}_out" for r in range(N_RACKS)]
OPEN3 = ["tile", "return"] + RIN + ROUT


def steady_to_euler(path):
    """steadyState -> Euler in fvSchemes, READ BEFORE WRITE.

    MEASURED TWICE IN THIS FILE: `open(p,"w").write(open(p).read()...)` truncates
    the file before the inner read runs and leaves it EMPTY. The first time it
    produced a zero-byte `0.orig/U`; the second a zero-byte `system/fvSchemes`,
    which OpenFOAM reported as "problem while reading header for object
    fvSchemes". Same one-liner, same fault, twice. It is a function now, with the
    assertion that would have caught either.
    """
    txt = open(path).read()
    assert "steadyState" in txt, f"no steadyState entry in {path}"
    out = txt.replace("    default         steadyState;",
                      "    default         Euler;", 1)
    with open(path, "w") as fh:
        fh.write(out)
    back = open(path).read()
    assert "Euler" in back and len(back) > 100, f"{path} came back empty or unchanged"


def divs(edges, h):
    n = [int(round((edges[i + 1] - edges[i]) / h)) for i in range(len(edges) - 1)]
    for i, v in enumerate(n):
        got = (edges[i + 1] - edges[i]) / v
        assert abs(got - h) < 0.02 * h, \
            f"cell size {h} does not divide interval {edges[i]}-{edges[i+1]} evenly"
    return n


def mesh3d(h):
    NXD, NYD, NZD = divs(XS, h), divs(YS, h), divs(ZS, h)
    NX, NY, NZ = len(XS), len(YS), len(ZS)
    vid = lambda i, j, k: k * (NY * NX) + j * NX + i
    verts = [f"    ({x:.6f} {y:.6f} {z:.6f})"
             for k, z in enumerate(ZS) for j, y in enumerate(YS) for i, x in enumerate(XS)]
    void = lambda i, j, k: (i in RACK_XI) and j == RACK_YI and k == RACK_ZI
    active = [(i, j, k) for k in range(NZ - 1) for j in range(NY - 1)
              for i in range(NX - 1) if not void(i, j, k)]
    C = lambda i, j, k: dict(
        v0=vid(i,j,k), v1=vid(i+1,j,k), v2=vid(i+1,j+1,k), v3=vid(i,j+1,k),
        v4=vid(i,j,k+1), v5=vid(i+1,j,k+1), v6=vid(i+1,j+1,k+1), v7=vid(i,j+1,k+1))
    blocks = ["    hex ({v0} {v1} {v2} {v3} {v4} {v5} {v6} {v7}) ({a} {b} {c}) simpleGrading (1 1 1)"
              .format(a=NXD[i], b=NYD[j], c=NZD[k], **C(i, j, k)) for i, j, k in active]
    f_bot = lambda i,j,k: "({v0} {v3} {v2} {v1})".format(**C(i,j,k))
    f_top = lambda i,j,k: "({v4} {v5} {v6} {v7})".format(**C(i,j,k))
    f_ylo = lambda i,j,k: "({v0} {v1} {v5} {v4})".format(**C(i,j,k))
    f_yhi = lambda i,j,k: "({v3} {v7} {v6} {v2})".format(**C(i,j,k))
    f_xlo = lambda i,j,k: "({v0} {v4} {v7} {v3})".format(**C(i,j,k))
    f_xhi = lambda i,j,k: "({v1} {v2} {v6} {v5})".format(**C(i,j,k))
    pf = {p: [] for p in WALLS3 + OPEN3}
    for i, j, k in active:
        if k == 0:
            pf["tile" if (j == TILE_YI and i in RACK_XI) else "floor"].append(f_bot(i,j,k))
        if k == NZ - 2:
            pf["return" if (j == RETURN_YI and i in RACK_XI) else "ceiling"].append(f_top(i,j,k))
        if j == 0:        pf["wall_cold"].append(f_ylo(i,j,k))
        if j == NY - 2:   pf["wall_hot"].append(f_yhi(i,j,k))
        if i == 0:        pf["wall_x0"].append(f_xlo(i,j,k))
        if i == NX - 2:   pf["wall_x1"].append(f_xhi(i,j,k))
    for n, i in enumerate(RACK_XI):
        pf[RIN[n]].append(f_yhi(i, RACK_YI - 1, RACK_ZI))
        pf[ROUT[n]].append(f_ylo(i, RACK_YI + 1, RACK_ZI))
        pf["rack_top"].append(f_bot(i, RACK_YI, RACK_ZI + 1))
    pf["rack_end"].append(f_xhi(RACK_XI[0] - 1, RACK_YI, RACK_ZI))
    pf["rack_end"].append(f_xlo(RACK_XI[-1] + 1, RACK_YI, RACK_ZI))
    def blk(nm, ty):
        fl = "\n            ".join(pf[nm])
        return f"    {nm}\n    {{\n        type {ty};\n        faces\n        (\n            {fl}\n        );\n    }}"
    bnd = [blk(p, "wall") for p in WALLS3] + [blk(p, "patch") for p in OPEN3]
    n = sum(NXD[i]*NYD[j]*NZD[k] for i, j, k in active)
    return "\n".join(["scale   1;", "", "vertices", "(", "\n".join(verts), ");", "",
                      "blocks", "(", "\n".join(blocks), ");", "", "edges();", "",
                      "boundary", "(", "\n".join(bnd), ");", ""]), n


TRANS_FVSOL = """solvers
{
    "p_rgh.*"
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-09;
        relTol          0.01;
    }

    "(U|T|k|omega).*"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-11;
        relTol          0.01;
    }
}

PIMPLE
{
    momentumPredictor   yes;
    nOuterCorrectors    2;
    nCorrectors         2;
    nNonOrthogonalCorrectors 0;
}

relaxationFactors
{
    fields
    {
        p_rgh           1;
    }
    equations
    {
        U               1;
        T               1;
        "(k|omega)"     1;
    }
}
"""


def control_dict(fos):
    return f"""application     buoyantBoussinesqPimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          0.005;
writeControl    adjustableRunTime;
writeInterval   {WRITE_INT};
purgeWrite      0;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
adjustTimeStep  yes;
maxCo           {MAX_CO};
maxDeltaT       0.25;

functions
{{
{fos}
}}
"""


def fo(name, patch, op, fld, weight=None):
    s = B._sfv(name, patch, op, fld, weight)
    return (s.replace("executeControl  timeStep", "executeControl  runTime")
             .replace(f"executeInterval {B.MONITOR_INTERVAL}", f"executeInterval {MON_INT}")
             .replace("writeControl    timeStep", "writeControl    runTime")
             .replace(f"writeInterval   {B.MONITOR_INTERVAL}", f"writeInterval   {MON_INT}"))


def build_2d(h=H_CELL, name="K2bU3_M"):
    """Control M and the resolution ladder: the 2D slice as a transient, at a
    given cell size.

    THE LADDER EXISTS BECAUSE THE GATE FAILED. Control M at 100 mm shows the
    6.000 s limit cycle DAMPING (ratio 0.482 against a 0.5 threshold), so a 3D
    run at 100 mm cannot separate three-dimensionality from mesh resolution and
    the pre-registered outcome is P3. P3 owes "the cost of the un-confounded
    experiment", and the honest way to state that is to MEASURE the coarsest 2D
    mesh on which the limit cycle survives, rather than to guess it. Each rung
    of the ladder is a 2D transient and costs ~h^-3.
    """
    case, n = B.build(name, h, int(END_TIME), int(WRITE_INT),
                      B.DT_RACK, True, False, None, QV_TILE)
    # steady -> transient
    steady_to_euler(os.path.join(case, "system", "fvSchemes"))
    B.w(case, "system/fvSolution", "dictionary", "fvSolution", TRANS_FVSOL)
    fos = "\n".join([fo("T_rack_in_mdot", "rack_in", "weightedAverage", "T", "phi"),
                     fo("T_rack_out_area", "rack_out", "areaAverage", "T"),
                     fo("phi_return", "return", "sum", "phi")])
    B.w(case, "system/controlDict", "dictionary", "controlDict", control_dict(fos))
    return name, n


LADDER = [(0.05, "K2bU3_L050"), (0.025, "K2bU3_L025")]


def build_3d():
    """Test D: the full module with OPEN row ends, the 3D-only freedom."""
    name = "K2bU3_D"
    case = os.path.join(HERE, name)
    src = os.path.join(HERE, "K2b3D_probe")
    for sub in ("system", "constant", "0.orig"):
        d = os.path.join(case, sub)
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(os.path.join(src, sub), d, ignore=shutil.ignore_patterns("polyMesh"))
    bmd, n = mesh3d(H_CELL)
    B.w(case, "system/blockMeshDict", "dictionary", "blockMeshDict", bmd)
    steady_to_euler(os.path.join(case, "system", "fvSchemes"))
    B.w(case, "system/fvSolution", "dictionary", "fvSolution", TRANS_FVSOL)
    # 70 % provisioning: the probe was built BALANCED, so the tile flow changes
    # and the tile inlet turbulence changes with it.
    u = os.path.join(case, "0.orig", "U")
    tot = N_RACKS * QV_TILE
    # MEASURED: `open(u,"w").write(... open(u).read() ...)` TRUNCATES THE FILE
    # BEFORE THE INNER READ RUNS, and leaves a zero-byte U behind. It did
    # exactly that here. Read first, into a name, then write, then assert.
    src_txt = open(u).read()
    old_tile = N_RACKS * B.QV_TILE          # the probe is built BALANCED
    assert f"volumetricFlowRate constant {old_tile};" in src_txt, \
        f"expected the balanced tile flow {old_tile} in {u}"
    out_txt = src_txt.replace(f"volumetricFlowRate constant {old_tile};",
                              f"volumetricFlowRate constant {tot};", 1)
    with open(u, "w") as fh:
        fh.write(out_txt)
    back = open(u).read()
    assert f"volumetricFlowRate constant {tot};" in back, "tile flow rewrite failed"
    assert back.count(f"volumetricFlowRate constant {B.QV_RACK};") == 2 * N_RACKS, \
        "the rack face pairs must be untouched"
    assert len(back) > 0, "U is empty"
    # the tile inlet turbulence follows the tile velocity, not the balanced one
    for fld, val in (("k", 1.5 * (B.I_SUP * tot / (N_RACKS * B.S_T * B.S_T)) ** 2),):
        fp = os.path.join(case, "0.orig", fld)
        t = open(fp).read()
        oldk = 1.5 * (B.I_SUP * (N_RACKS * B.QV_TILE) / (N_RACKS * B.S_T ** 2)) ** 2
        t = t.replace(f"{oldk:.6e}", f"{val:.6e}")
        with open(fp, "w") as fh:
            fh.write(t)
    fos = "\n".join([fo(f"T_rack{r}_in_mdot", RIN[r], "weightedAverage", "T", "phi")
                     for r in range(N_RACKS)]
                    + [fo("phi_return", "return", "sum", "phi")]
                    + [f"""    Tspan
    {{
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        fields          (T U);
        location        true;
        writeToFile     true;
        log             true;
        executeControl  runTime;
        executeInterval {MON_INT};
        writeControl    runTime;
        writeInterval   {MON_INT};
    }}"""])
    B.w(case, "system/controlDict", "dictionary", "controlDict", control_dict(fos))
    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write(f"""case               {name}
kind               K2b-U3 TEST D -- does the 2D limit cycle survive in 3D?
pre-registration   K2b_3D_UNSTEADINESS_PREREGISTRATION.md sha256 91a26fc9...
gate               K2bU3_M must show the limit cycle surviving at this same
                   100 mm cell in 2D, or mesh and dimensionality are confounded
solver             buoyantBoussinesqPimpleFoam, Euler, PIMPLE 2/2
cells              {n}   (cell {H_CELL} m; the spec's 3D coarse is 60 mm)
racks              {N_RACKS}, row ends OPEN -- the spanwise path a slice cannot have
provisioning       {100.0*N_RACKS*QV_TILE/(N_RACKS*B.QV_RACK):.0f} % (tile {QV_TILE} m3/s each)
endTime            {END_TIME} s, maxCo {MAX_CO}, monitor every {MON_INT} s
discard            first 40 s (3D room turnover ~35 s)
graded             60-80 s against 40-60 s, on the mass-flow-weighted mean T_in
                   over ALL FOUR rack front faces
thresholds         p2p >= 0.30 K and ratio >= 0.8 = SURVIVES;
                   p2p <= 0.10 K or ratio <= 0.5 = DAMPS; else UNDECIDABLE
aliasing floor     >= 20 steps and >= 10 samples per 6.000 s period, measured
""")
    return name, n


def main():
    if "--ladder" in sys.argv:
        for h, nm_ in LADDER:
            _, c = build_2d(h, nm_)
            dt = 2 * h / 1.2
            print(f"built {nm_}  2D slice at h={h} m: {c} cells, "
                  f"dt~{dt:.3f} s, {6.0/dt:.0f} steps/period, "
                  f"~{80/dt*c/51556/60:.2f} core-min")
        return 0
    m, nm = build_2d()
    d, nd = build_3d()
    print(f"built {m}  (GATE, 2D slice at h={H_CELL} m): {nm} cells")
    print(f"built {d}  (TEST, 3D module at h={H_CELL} m): {nd} cells, {N_RACKS} racks, open ends")
    rate = 46400 * 1978 / 1780.0 / 1.21
    dt = 2 * H_CELL / 1.2
    print(f"  expected dt ~{dt:.3f} s at maxCo {MAX_CO} -> {6.0/dt:.0f} steps and "
          f"{6.0/MON_INT:.0f} samples per 6.000 s period (floors 20 and 10)")
    print(f"  estimated cost: {m} {END_TIME/dt*nm/(rate*1.21)/60:.2f} core-min, "
          f"{d} {END_TIME/dt*nd/rate/60:.2f} core-min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
