#!/usr/bin/env python3
"""
F3 SUCCESSOR -- the INSTRUMENTED RUNNER. New file, so the frozen grading path
(`instrument.py`, `grade_f3s.py`, frozen at 5891db27) is not modified after its
freeze. It IMPORTS instrument.py; it does not change it.

The graded values come from the SAME code path as F3's frozen runners, at the
same final time, from the same artifacts. The series is a SECOND, ADDITIVE read
taken from function objects appended to controlDict in a new `functions` block.

VERIFIED BEFORE USE, not assumed: OpenFOAM v2606 MERGES a second `functions`
block with an existing one. `foamDictionary -entry functions -keywords` on the
diamond controlDict with the appended block returns BOTH `forces1` and
`forcesSeries`. Without that check the diamond -- which already carries a
`functions` block -- would have been the case where "additive only" quietly
failed.
"""
import os
import re
import sys
import glob
import json
import math
import time
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
F3_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, F3_ROOT)

import instrument as INS
from make_wedge_case import make_case as make_wedge
from make_diamond_case import make_case as make_diamond

FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
N = INS.SERIES_EVERY_N_STEPS
Z_THICKNESS = 0.01
GAMMA = 1.4


def refuse(m):
    sys.stderr.write("REFUSED: %s\n" % m)
    sys.exit(2)


def sh(cmd, cwd, log):
    full = "source %s >/dev/null 2>&1; %s" % (FOAM, cmd)
    t0 = time.time()
    p = subprocess.run(["bash", "-c", full], cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(log, "wb") as f:
        f.write(p.stdout)
    if p.returncode != 0:
        refuse("command failed (%s) rc=%d; see %s" % (cmd, p.returncode, log))
    return time.time() - t0


# --------------------------------------------------------------------------
# The appended blocks. `writeControl timeStep` ONLY -- never adjustableRunTime,
# which would clip deltaT onto write times and change the trajectory.
# --------------------------------------------------------------------------

def wedge_functions(Lramp, H):
    xs = np.linspace(0.12, 0.88, 6) * Lramp
    sets = "\n".join(
        "            x%d { type uniform; axis y; start (%.6f 0 0); "
        "end (%.6f %.6f 0); nPoints 800; }" % (i, x, x, H)
        for i, x in enumerate(xs))
    return """
%s
functions
{
    surfSeries
    {
        type            surfaces;
        libs            (sampling);
        writeControl    timeStep;
        writeInterval   %d;
        interpolationScheme cellPoint;
        surfaceFormat   raw;
        fields          (p);
        surfaces
        (
            wedgeSurface
            {
                type    patch;
                patches (obstacle);
                interpolate false;
                triangulate false;
            }
        );
    }
    setsSeries
    {
        type            sets;
        libs            (sampling);
        writeControl    timeStep;
        writeInterval   %d;
        interpolationScheme cellPoint;
        setFormat       raw;
        fields          (p rho T);
        sets
        (
%s
        );
    }
}
""" % (INS.FUNCTIONS_MARKER, N, N, sets)


def diamond_functions():
    return """
%s
functions
{
    forcesSeries
    {
        type            forces;
        libs            (forces);
        patches         (obstacle);
        rho             rhoInf;
        rhoInf          1;
        CofR            (0.5 0 0);
        writeControl    timeStep;
        writeInterval   %d;
    }
}
""" % (INS.FUNCTIONS_MARKER, N)


# --------------------------------------------------------------------------
# Graded readers -- IDENTICAL arithmetic to the frozen runners
# --------------------------------------------------------------------------

def p_wall_mean_of(raw_path, Lramp):
    arr = np.loadtxt(raw_path, comments="#")
    x, p = arr[:, 0], arr[:, 3]
    o = np.argsort(x)
    x, p = x[o], p[o]
    mid = (x > 0.3 * Lramp) & (x < 0.85 * Lramp)
    return float(np.mean(p[mid]))


def beta_of(sampdir, n_stations=6):
    """The frozen 5-station fit: shock located by the most negative gradient of
    column 3, stations 1..5 fitted, station 0 dropped (corner smearing)."""
    pts = []
    for i in range(n_stations):
        cands = sorted(glob.glob(os.path.join(sampdir, "x%d_*.xy" % i)))
        if not cands:
            continue
        d = np.loadtxt(cands[0])
        if d.ndim != 2 or len(d) < 10:
            continue
        y, q = d[:, 0], d[:, 3]
        pts.append((float(_station_x(cands[0], sampdir, i)), float(y[np.argmin(np.gradient(q, y))])))
    if len(pts) < 4:
        return None, []
    a = np.array(pts)
    xk, yk = a[1:, 0], a[1:, 1]
    A = np.vstack([xk, np.ones_like(xk)]).T
    m = np.linalg.lstsq(A, yk, rcond=None)[0][0]
    return math.degrees(math.atan(m)), a.tolist()


_STATION_X = {}


def _station_x(path, sampdir, i):
    return _STATION_X[i]


def cd_of(force_path, M, c):
    rows = [l for l in open(force_path) if not l.startswith("#") and l.strip()]
    fx = float(rows[-1].split()[1])
    q1 = 0.5 * GAMMA * 1.0 * M ** 2
    return 2.0 * (fx / Z_THICKNESS) / (q1 * c)


def write_sample_dicts(case_dir, Lramp, H):
    """Written AFTER the solve, exactly as the frozen runner does, so the GRADED
    read path is unchanged."""
    xs = np.linspace(0.12, 0.88, 6) * Lramp
    for i, x in enumerate(xs):
        _STATION_X[i] = x
    sets = "\n".join(
        "    x%d { type uniform; axis y; start (%.6f 0 0); end (%.6f %.6f 0); "
        "nPoints 800; }" % (i, x, x, H) for i, x in enumerate(xs))
    open(os.path.join(case_dir, "system", "sampleDict"), "w").write(
        "FoamFile { version 2.0; format ascii; class dictionary; object sampleDict; }\n"
        "type sets;\nlibs (sampling);\ninterpolationScheme cellPoint;\nsetFormat raw;\n"
        "fields (p rho T);\nsets\n(\n%s\n);\n" % sets)
    open(os.path.join(case_dir, "system", "surfaceSampleDict"), "w").write(
        "FoamFile { version 2.0; format ascii; class dictionary; object surfaceSampleDict; }\n"
        "type surfaces;\nlibs (sampling);\ninterpolationScheme cellPoint;\n"
        "surfaceFormat raw;\nfields (p rho T);\nsurfaces\n(\n    wedgeSurface\n    {\n"
        "        type patch;\n        patches (obstacle);\n        interpolate false;\n"
        "        triangulate false;\n    }\n);\n")
    return list(xs)


def series_times(root):
    out = []
    if not os.path.isdir(root):
        return out
    for d in os.listdir(root):
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d):
            out.append((float(d), os.path.join(root, d)))
    out.sort(key=lambda t: t[0])
    return out


# --------------------------------------------------------------------------
def run_case(case_dir, family, pair, level, instrumented=True):
    INS.guard_fresh_case_dir(case_dir)
    os.makedirs(case_dir, exist_ok=True)
    P = PARAMS[(family, pair)]

    if family == "wedge":
        meta = make_wedge(case_dir, P["M"], P["ang"], level, P["beta"])
    else:
        meta = make_diamond(case_dir, P["M"], P["ang"], level, P["beta"])

    keys, before_txt = INS.read_controldict_keys(case_dir)
    added = None
    if instrumented:
        block = (wedge_functions(meta["Lramp"], meta["H"]) if family == "wedge"
                 else diamond_functions())
        with open(os.path.join(case_dir, "system", "controlDict"), "a") as f:
            f.write(block)
        added = INS.assert_controldict_additive(before_txt, case_dir)
    INS.refuse_clipping_output(case_dir)

    t_mesh = sh("blockMesh", case_dir, case_dir + "/log.blockMesh")
    sh("checkMesh -noTopology", case_dir, case_dir + "/log.checkMesh")
    t_run = sh("rhoCentralFoam", case_dir, case_dir + "/log.rhoCentralFoam")

    end_time = float(keys["endTime"])
    c = meta.get("c", 1.0)
    out = dict(case_dir=case_dir, family=family, pair=pair, res_level=level,
               M=P["M"], c=c, endTime=end_time, instrumented=instrumented,
               t_mesh_s=t_mesh, t_run_s=t_run,
               controlDict_keys=keys, controlDict_additive=added,
               Lramp=meta.get("Lramp"), H=meta.get("H"),
               ncells=meta.get("ncells"))

    if family == "wedge":
        write_sample_dicts(case_dir, meta["Lramp"], meta["H"])
        sh("postProcess -func sampleDict -latestTime", case_dir, case_dir + "/log.sample")
        sh("postProcess -func surfaceSampleDict -latestTime", case_dir, case_dir + "/log.surfsample")
        surfd = _latest(os.path.join(case_dir, "postProcessing", "surfaceSampleDict"))
        rawp = sorted(glob.glob(os.path.join(surfd, "*p*.raw")))[0]
        out["p_wall_mean"] = p_wall_mean_of(rawp, meta["Lramp"])
        sampd = _latest(os.path.join(case_dir, "postProcessing", "sampleDict"))
        b, pts = beta_of(sampd)
        out["beta_computed_deg"], out["shock_pts"] = b, pts
        if instrumented:
            _wedge_series(case_dir, meta["Lramp"], end_time)
    else:
        fd = _latest(os.path.join(case_dir, "postProcessing", "forces1"))
        out["cd_computed"] = cd_of(os.path.join(fd, "force.dat"), P["M"], c)
        if instrumented:
            _diamond_series(case_dir, P["M"], c, end_time)

    json.dump(dict(Lramp=meta.get("Lramp"), H=meta.get("H"), M=P["M"], c=c,
                   endTime=end_time, ncells=meta.get("ncells")),
              open(os.path.join(case_dir, "meta.json"), "w"), indent=2)
    json.dump(out, open(os.path.join(case_dir, "result.json"), "w"), indent=2)
    return out


def _latest(root):
    ts = series_times(root)
    if not ts:
        refuse("no sampled times under %s" % root)
    return ts[-1][1]


def _wedge_series(case_dir, Lramp, end_time):
    t_p, v_p = [], []
    for t, d in series_times(os.path.join(case_dir, "postProcessing", "surfSeries")):
        g = sorted(glob.glob(os.path.join(d, "*p*.raw")))
        if g:
            t_p.append(t); v_p.append(p_wall_mean_of(g[0], Lramp))
    t_b, v_b = [], []
    for t, d in series_times(os.path.join(case_dir, "postProcessing", "setsSeries")):
        b, _ = beta_of(d)
        if b is not None:
            t_b.append(t); v_b.append(b)
    _dump(case_dir, "p_wall_mean", t_p, v_p, end_time)
    _dump(case_dir, "beta_deg", t_b, v_b, end_time)


def _diamond_series(case_dir, M, c, end_time):
    q1 = 0.5 * GAMMA * 1.0 * M ** 2
    t_c, v_c = [], []
    for _t, d in series_times(os.path.join(case_dir, "postProcessing", "forcesSeries")):
        fp = os.path.join(d, "force.dat")
        if not os.path.exists(fp):
            continue
        for ln in open(fp):
            if ln.startswith("#") or not ln.strip():
                continue
            p = ln.split()
            t_c.append(float(p[0]))
            v_c.append(2.0 * (float(p[1]) / Z_THICKNESS) / (q1 * c))
    _dump(case_dir, "cd", t_c, v_c, end_time)


def _dump(case_dir, q, t, v, end_time):
    if len(t) < 2:
        refuse("%s: series for %s has %d points -- the Class C gate cannot be "
               "evaluated and an unevaluated step is not a passed one"
               % (case_dir, q, len(t)))
    json.dump(dict(t=t, v=v, end_time=end_time),
              open(os.path.join(case_dir, "series_%s.json" % q), "w"))


PARAMS = {
    ("wedge", "M2.5_th10"):  dict(M=2.5, ang=10.0, beta=31.85059223127216),
    ("wedge", "M3.0_th15"):  dict(M=3.0, ang=15.0, beta=32.240400182744665),
    ("diamond", "M2.5_eps5"): dict(M=2.5, ang=5.0, beta=27.42266202135665),
}

if __name__ == "__main__":
    cd, fam, pr, lv = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    inst = (len(sys.argv) < 6 or sys.argv[5] != "uninstrumented")
    r = run_case(cd, fam, pr, lv, inst)
    print(json.dumps({k: v for k, v in r.items() if k != "shock_pts"}, indent=2))
