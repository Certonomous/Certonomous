#!/usr/bin/env python3
"""map_inflow_t5.py -- the S5.3 precursor-to-inlet map, and the plane selection LOG.

Reads the CONVERGED X_2d solution (latest time) through `postProcess -func sets`
(vertical lines at registered x stations), computes the floor momentum thickness
theta(x) = int u/U_e (1 - u/U_e) dy over the floor half-channel with U_e = the
centreline velocity, Re_theta = U_e theta / nu, and selects the mapping plane x_p
such that Re_theta(x_p + 8 H) = 660 (S5.3: 8 H of further development inside the
3-D domain, cube absent, reaches Re_theta = 660 at x = 0).  Writes
constant/<fluidRegion>/boundaryData/inlet/{points,0/U,0/k,0/omega} into every
named 3-D case and appends the iteration to T5_INFLOW_LOG.md.  It touches no h.
No `assert`.  REFUSES if X_2d is not DONE (marker), if 660 is outside the
sampled range, or if the chosen plane sits within 2 H of the precursor inlet or
outlet.

AMENDMENT 8 (2026-08-26, T5 lane, for the supervisor's after-the-fact read):
  * PATH.  The reader of `timeVaryingMappedFixedValue` in openfoam-2606 is
    PatchFunction1Types::MappedFile; it opens
    time.constant()/mesh.dbDir()/"boundaryData"/<patch>/points
    (src/meshTools/PatchFunction1/MappedFile/MappedFile.C:496-503), and for a
    multi-region case mesh.dbDir() is the REGION NAME.  The previous version
    wrote to constant/boundaryData/inlet, which the air-region reader never
    opens; rawIOField then held 0 points and the solver FATALed with "Need at
    least 3 non-collinear points for planar interpolation, but only had 0
    points" (T5_CUBE_c, 17:41:39Z) -- the same text it gave at 16:27Z when no
    boundaryData existed at all.  The fluid region is READ from
    constant/regionProperties (exactly one fluid region, else REFUSE) and the
    patch is required to exist in constant/<region>/polyMesh/boundary.
  * EXTRUSION.  The y-profile is written at three z-stations spanning the
    inlet patch width; the width is READ from the region's polyMesh/points
    (streamed, min/max z only -- never loaded whole) with a 0.1 mm outward
    margin so every patch face centre lies inside the triangulated hull.  The
    previous version extruded to a hard-coded W = 0.075 with no margin.
  * REFUSAL.  The points file is read back and REFUSED (exit 2) if the cloud is
    collinear (no triple with a non-zero cross product) or its count differs.
  Station selection, the 2 H guard and the mapping arithmetic are untouched.
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
H, D, NU, RE_TARGET = 0.015, 0.051, 1.510e-05, 660.0
Z_MARGIN = 1.0e-4        # m, outward extrusion margin beyond the patch width (AMENDMENT 8)
N_Z_STATIONS = 3
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
STATIONS_H = list(range(8, 76, 2))          # x/H stations sampled in the precursor


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def latest_time(case):
    ts = [d for d in os.listdir(case) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and d != "0"]
    if not ts:
        refuse("%s has no solved time directory" % case)
    return max(ts, key=float)


def sample(case, t):
    lines = "\n".join("    L%d { type uniform; axis y; start (%.6g 1e-6 0.0005); end (%.6g %.6g 0.0005); nPoints 400; }"
                      % (s, s * H, s * H, D - 1e-6) for s in STATIONS_H)
    d = os.path.join(case, "system", "t5InflowSample")
    open(d, "w").write("type sets;\nlibs (sampling);\ninterpolationScheme cellPoint;\nsetFormat raw;\nfields (U k omega);\nsets\n{\n%s\n}\n" % lines)
    r = subprocess.run(["bash", "-c", "source %s >/dev/null 2>&1; cd %s && postProcess -func t5InflowSample -time %s > log.inflowSample 2>&1"
                        % (FOAM_BASHRC, case, t)])
    if r.returncode != 0:
        refuse("postProcess sampling failed in %s (see log.inflowSample)" % case)
    out = {}
    base = os.path.join(case, "postProcessing", "t5InflowSample", t)
    for s in STATIONS_H:
        # PROPOSED (2026-08-26, lane, for the supervisor's read): openfoam-2606's
        # `sets` writer emits ONE raw file per set carrying every sampled field,
        # named L<s>_k_omega_U.xy with columns (y k omega Ux Uy Uz) -- measured on
        # DONE.X_2d at time 5000 (34 files, 400 rows x 6 columns).  The committed
        # reader expected two files (L<s>_U.xy, L<s>_k_omega.xy) and REFUSED.
        fc = os.path.join(base, "L%d_k_omega_U.xy" % s)
        if not os.path.isfile(fc):
            refuse("sample file missing for station %d: %s" % (s, fc))
        rows = [[float(v) for v in l.split()] for l in open(fc) if l.strip()]
        if not rows or any(len(r) != 6 for r in rows):
            refuse("station %d: expected 6 columns (y k omega Ux Uy Uz) in %s, got %s"
                   % (s, fc, sorted(set(len(r) for r in rows))))
        U = [[r[0], r[3], r[4], r[5]] for r in rows]
        KW = [[r[0], r[1], r[2]] for r in rows]
        out[s] = (U, KW)
    return out


def re_theta(U):
    ys = [r[0] for r in U]; us = [r[1] for r in U]
    ic = min(range(len(ys)), key=lambda i: abs(ys[i] - 0.5 * D))
    ue = max(us[:ic + 1])
    th = 0.0
    for i in range(1, ic + 1):
        f0 = us[i - 1] / ue * (1 - us[i - 1] / ue); f1 = us[i] / ue * (1 - us[i] / ue)
        th += 0.5 * (f0 + f1) * (ys[i] - ys[i - 1])
    return ue * th / NU, ue, th


def fluid_region(case):
    """The single fluid region named in constant/regionProperties (AMENDMENT 8)."""
    rp = os.path.join(case, "constant", "regionProperties")
    if not os.path.isfile(rp):
        refuse("%s: no constant/regionProperties; the region path of boundaryData cannot be established" % case)
    m = re.search(r"fluid\s*\(([^)]*)\)", open(rp).read())
    regs = m.group(1).split() if m else []
    if len(regs) != 1:
        refuse("%s: expected exactly one fluid region in regionProperties, found %s" % (case, regs))
    return regs[0]


def patch_exists(case, region, patch):
    b = os.path.join(case, "constant", region, "polyMesh", "boundary")
    if not os.path.isfile(b):
        refuse("%s: no %s" % (case, b))
    return re.search(r"^\s*%s\s*$" % re.escape(patch), open(b).read(), re.M) is not None


def mesh_z_extent(case, region):
    """min/max z of the region's polyMesh/points, STREAMED line by line -- the
    file is never held in memory (solvers are live on this box)."""
    p = os.path.join(case, "constant", region, "polyMesh", "points")
    if not os.path.isfile(p):
        refuse("%s: no %s" % (case, p))
    zmin, zmax, n = None, None, 0
    pat = re.compile(r"^\(\s*([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)\s*$")
    with open(p) as fh:
        for line in fh:
            m = pat.match(line)
            if not m:
                continue
            z = float(m.group(3)); n += 1
            zmin = z if zmin is None or z < zmin else zmin
            zmax = z if zmax is None or z > zmax else zmax
    if n < 4 or zmax - zmin <= 0.0:
        refuse("%s: mesh points give no z extent (n=%d, zmin=%s, zmax=%s)" % (case, n, zmin, zmax))
    return zmin, zmax


def read_back_points(path):
    """Count and extents of a written points file, streamed; refuses on collinearity."""
    pat = re.compile(r"^\(\s*([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)\s*$")
    n, p0, p1, noncol = 0, None, None, False
    ext = [None] * 6
    with open(path) as fh:
        for line in fh:
            m = pat.match(line)
            if not m:
                continue
            p = tuple(float(g) for g in m.groups()); n += 1
            for i in range(3):
                ext[2 * i] = p[i] if ext[2 * i] is None or p[i] < ext[2 * i] else ext[2 * i]
                ext[2 * i + 1] = p[i] if ext[2 * i + 1] is None or p[i] > ext[2 * i + 1] else ext[2 * i + 1]
            if p0 is None:
                p0 = p
            elif p1 is None and max(abs(p[i] - p0[i]) for i in range(3)) > 1e-12:
                p1 = p
            elif p1 is not None and not noncol:
                a = [p1[i] - p0[i] for i in range(3)]; b = [p[i] - p0[i] for i in range(3)]
                cx = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
                if max(abs(c) for c in cx) > 1e-14:
                    noncol = True
    return n, ext, noncol


def write_boundary_data(case, U, KW, x_in):
    region = fluid_region(case)
    if not patch_exists(case, region, "inlet"):
        refuse("%s: patch `inlet` is not in constant/%s/polyMesh/boundary" % (case, region))
    zmin, zmax = mesh_z_extent(case, region)
    z_lo, z_hi = zmin - Z_MARGIN, zmax + Z_MARGIN
    z_st = [z_lo + (z_hi - z_lo) * i / (N_Z_STATIONS - 1) for i in range(N_Z_STATIONS)]
    bd = os.path.join(case, "constant", region, "boundaryData", "inlet")
    os.makedirs(os.path.join(bd, "0"), exist_ok=True)
    pts = []
    for z in z_st:
        for r in U:
            pts.append((x_in, r[0], z))
    with open(os.path.join(bd, "points"), "w") as fh:
        fh.write("%d\n(\n%s\n)\n" % (len(pts), "\n".join("(%.9g %.9g %.9g)" % p for p in pts)))
    def fld(name, vals, vec):
        with open(os.path.join(bd, "0", name), "w") as fh:
            fh.write("%d\n(\n" % (len(z_st) * len(vals)))
            for _ in z_st:
                for v in vals:
                    fh.write(("(%.9g %.9g %.9g)\n" % tuple(v)) if vec else ("%.9g\n" % v))
            fh.write(")\n")
    fld("U", [(r[1], 0.0, 0.0) for r in U], True)
    fld("k", [r[1] for r in KW], False)
    fld("omega", [r[2] for r in KW], False)
    back, ext, noncol = read_back_points(os.path.join(bd, "points"))
    if back != len(pts):
        refuse("%s: boundaryData points read back %d, wrote %d" % (case, back, len(pts)))
    if not noncol:
        refuse("%s: the written point cloud is COLLINEAR (%d points); planar interpolation needs 3 non-collinear points" % (case, back))
    print("  %s: region %s, mesh z [%.6g, %.6g], %d points at %d z-stations %s, extents x [%.6g, %.6g] y [%.6g, %.6g] z [%.6g, %.6g], non-collinear"
          % (os.path.relpath(bd, case), region, zmin, zmax, back, len(z_st), ["%.6g" % z for z in z_st],
             ext[0], ext[1], ext[2], ext[3], ext[4], ext[5]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--targets", nargs="*", default=["T5_CUBE_c", "H_c", "T5_CUBE_m", "T5_CUBE_f", "P_m", "L_m"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    x2d = os.path.join(a.root, "X_2d")
    if not os.path.isfile(os.path.join(a.root, "DONE.X_2d")):
        refuse("no DONE.X_2d marker: the precursor is not complete under the strict rule; no plane is selected")
    t = latest_time(x2d)
    data = sample(x2d, t)
    table = []
    for s in STATIONS_H:
        rt, ue, th = re_theta(data[s][0])
        table.append((s, rt, ue, th))
    # Re_theta must reach 660 at x_p + 8 H: find station s* with Re_theta(s*) = 660, then x_p = (s* - 8) H
    xs = [r[0] for r in table]; rts = [r[1] for r in table]
    if not (min(rts) <= RE_TARGET <= max(rts)):
        refuse("Re_theta = %.0f not bracketed by the sampled range [%.0f, %.0f]" % (RE_TARGET, min(rts), max(rts)))
    s_star = None
    for (x0, r0), (x1, r1) in zip(zip(xs, rts), zip(xs[1:], rts[1:])):
        if (r0 - RE_TARGET) * (r1 - RE_TARGET) <= 0 and r1 != r0:
            s_star = x0 + (RE_TARGET - r0) * (x1 - x0) / (r1 - r0); break
    if s_star is None:
        refuse("no crossing of Re_theta = 660 found")
    x_p_H = s_star - 8.0
    if x_p_H < 2.0 or x_p_H > STATIONS_H[-1] - 2.0:
        refuse("selected plane x_p/H = %.2f sits within 2 H of the precursor inlet/outlet" % x_p_H)
    # nearest sampled station to x_p for the profile actually mapped
    s_map = min(STATIONS_H, key=lambda s: abs(s - x_p_H))
    rt_map = dict((r[0], r[1]) for r in table)[s_map]
    log = os.path.join(a.root, "T5_INFLOW_LOG.md")
    with open(log, "a") as fh:
        fh.write("\n## iteration %s (X_2d time %s)\n\n| x/H | Re_theta | U_e | theta [m] |\n|---|---|---|---|\n" % (subprocess.run(["date", "-u", "+%FT%TZ"], capture_output=True, text=True).stdout.strip(), t))
        for r in table:
            fh.write("| %d | %.1f | %.4f | %.6g |\n" % r)
        fh.write("\nRe_theta = 660 crossed at x/H = %.3f -> mapping plane x_p/H = %.3f; profile taken from the nearest sampled station x/H = %d (Re_theta %.1f). "
                 "Written to: %s. dry_run=%s\n" % (s_star, x_p_H, s_map, rt_map, ", ".join(a.targets), a.dry_run))
    print("Re_theta crossing x/H=%.3f; plane x_p/H=%.3f; mapped station x/H=%d (Re_theta %.1f)" % (s_star, x_p_H, s_map, rt_map))
    if a.dry_run:
        return 0
    for tg in a.targets:
        c = os.path.join(a.root, tg)
        if not os.path.isdir(c):
            refuse("target case %s absent" % c)
        write_boundary_data(c, data[s_map][0], data[s_map][1], -8 * H)
        print("boundaryData written to " + c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
