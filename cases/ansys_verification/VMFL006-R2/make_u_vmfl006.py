#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VMFL006 -- emit 0/U as the CELL-AVERAGED analytic Poiseuille profile.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27-28.
The manual prescribes "Fully developed laminar velocity profile at inlet with an
average velocity of 1 m/s" (p.27).  The Graetz reference the manual cites assumes
that parabola EVERYWHERE, so this case IMPOSES it instead of computing it:

  * the hydrodynamic entrance length at Re_D = 500 is ~0.05*Re*D = 0.125 m,
    LONGER than the whole 0.1 m pipe, so a uniform inlet would leave the flow
    developing over the entire domain and every mixing-cup average -- which is
    weighted BY the velocity -- would be weighted by the wrong profile;
  * and a computed parabola carries its own discretisation error, which the
    analytical reference does not have.  Imposing it removes that channel.

WHAT IS WRITTEN, AND WHY IT IS THE CELL AVERAGE AND NOT THE CENTROID VALUE.
For the cell occupying the radial band [r_a, r_b], the exact area-average of
u(r) = 2*Uavg*(1 - r^2/R^2) over that band is

    u_cell = 2*Uavg*(1 - (r_a^2 + r_b^2)/(2 R^2))

and the discrete volumetric flow rate SUM(u_cell * A_cell) then equals the
analytic flow rate Uavg * A EXACTLY, on every level of the grid family, because
A_cell of a flat-sided wedge is exactly proportional to (r_b^2 - r_a^2).  A
centroid-sampled parabola does not have that property and would put an O(dr^2)
error into the mean velocity -- i.e. straight into the Graetz coordinate tau.

DISCRETE CONSERVATION.  u depends on r only, so with `zeroGradient` on U at the
inlet and outlet the face flux of every axial face in a radial band equals
u_cell*A, the radial faces carry no flux (U is axial, their normal is radial) and
the wedge faces carry none either.  div(phi) is therefore ZERO TO MACHINE
PRECISION on every cell, and the flux control in grade_vmfl006.py measures that
rather than assuming it.

NO `assert` CARRIES ANY GUARD HERE (PREREG_TEMPLATE Amendment 6): `python3 -O`
strips asserts, so every refusal below is an explicit sys.exit(2).

  usage: make_u_vmfl006.py <case_dir> <NR> <RGRAD> [--selftest]
"""
import os, re, sys, math

R_PIPE = 0.0025      # m,   manual p.27
U_AVG  = 1.0         # m/s, manual p.27


def refuse(tag, msg):
    sys.stderr.write("REFUSED (exit 2) [%s]: %s\n" % (tag, msg))
    sys.exit(2)


def read_internal_scalar(path):
    s = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;",
                  s, re.S)
    if not m:
        m2 = re.search(r"internalField\s+uniform\s+([0-9eE.+-]+)\s*;", s)
        if m2:
            refuse("U1", "%s holds a UNIFORM internalField; cell centres must be nonuniform" % path)
        refuse("U1", "no nonuniform scalar internalField in %s" % path)
    vals = [float(v) for v in m.group(2).split()]
    if len(vals) != int(m.group(1)):
        refuse("U2", "%s: declared %s values, parsed %d" % (path, m.group(1), len(vals)))
    return vals


def radial_faces(nr, rgrad, R=R_PIPE):
    """blockMesh simpleGrading face radii. `rgrad` is blockMesh's expansion ratio
    (last cell width / first cell width); rgrad < 1 refines towards the WALL."""
    if nr < 1:
        refuse("U3", "NR must be >= 1, got %d" % nr)
    if rgrad <= 0.0:
        refuse("U3", "RGRAD must be > 0, got %g" % rgrad)
    if nr == 1:
        return [0.0, R]
    if abs(rgrad - 1.0) < 1e-14:
        return [R * k / nr for k in range(nr + 1)]
    r = rgrad ** (1.0 / (nr - 1))          # cell-to-cell ratio
    d0 = R * (r - 1.0) / (r ** nr - 1.0)   # first cell width
    out, acc = [0.0], 0.0
    for k in range(nr):
        acc += d0 * (r ** k)
        out.append(acc)
    out[-1] = R                            # pin the wall exactly
    return out


def cell_velocity(r_a, r_b, R=R_PIPE, uavg=U_AVG):
    """Exact area-average of 2*uavg*(1-(r/R)^2) over the band [r_a, r_b]."""
    return 2.0 * uavg * (1.0 - (r_a * r_a + r_b * r_b) / (2.0 * R * R))


def build(case_dir, nr, rgrad):
    zero = os.path.join(case_dir, "0")
    cy = os.path.join(zero, "Cy")
    cz = os.path.join(zero, "Cz")
    for p in (cy, cz):
        if not os.path.exists(p):
            refuse("U4", "%s missing -- run `postProcess -func writeCellCentres -time 0` first" % p)
    ys, zs = read_internal_scalar(cy), read_internal_scalar(cz)
    if len(ys) != len(zs):
        refuse("U5", "Cy has %d cells, Cz has %d" % (len(ys), len(zs)))
    ncell = len(ys)
    if ncell % nr != 0:
        refuse("U6", "cell count %d is not a multiple of NR = %d" % (ncell, nr))
    nx = ncell // nr

    faces = radial_faces(nr, rgrad)
    # Bin every cell by its own centroid radius. The centroid of a cell lies
    # STRICTLY inside its own radial extent, so this binning is exact -- and it
    # is a MEASUREMENT of the mesh, not an assumption about blockMesh's cell
    # ordering. If the ordering is ever not (i fastest, then j), this still works
    # and the per-band count check below still refuses a mesh it cannot explain.
    band = [-1] * ncell
    for i in range(ncell):
        rc = math.hypot(ys[i], zs[i])
        lo, hi = 0, nr - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if rc < faces[mid]:
                hi = mid - 1
            elif rc > faces[mid + 1]:
                lo = mid + 1
            else:
                band[i] = mid
                break
        if band[i] < 0:
            refuse("U7", "cell %d has centroid radius %.12g outside every radial band "
                         "[0, %.12g] -- the mesh is not the one this writer assumes"
                   % (i, rc, faces[-1]))
    counts = [0] * nr
    for b in band:
        counts[b] += 1
    bad = [(j, counts[j]) for j in range(nr) if counts[j] != nx]
    if bad:
        refuse("U8", "radial band population is not uniform: expected %d cells per band, "
                     "got %s -- the mesh is not the NX x NR structured wedge this writer assumes"
               % (nx, bad[:5]))

    u_band = [cell_velocity(faces[j], faces[j + 1]) for j in range(nr)]
    # BUILD-TIME IDENTITY CHECK, labelled as such (VERIFICATION_CHARTER sec.2a):
    # the flow-weighted mean of the CONSTRUCTED profile is derivable from its own
    # inputs, so it is REPORTED and used as a BUILD refusal -- it is never a gate
    # on the physics. What it protects against is an arithmetic slip in
    # cell_velocity() or in radial_faces().
    num = sum(u_band[j] * (faces[j + 1] ** 2 - faces[j] ** 2) for j in range(nr))
    den = sum((faces[j + 1] ** 2 - faces[j] ** 2) for j in range(nr))
    mean_u = num / den
    if abs(mean_u - U_AVG) > 1e-12:
        refuse("U9", "constructed profile's flow-weighted mean is %.15g m/s, not %.15g "
                     "(build identity check)" % (mean_u, U_AVG))

    body = "\n".join("(%.15g 0 0)" % u_band[band[i]] for i in range(ncell))
    txt = ('''/*--------------------------------*- C++ -*----------------------------------*\\
  VMFL006 -- 0/U, GENERATED by make_u_vmfl006.py. Do not hand-edit.
  Cell-averaged analytic Poiseuille profile u(r) = 2*Uavg*(1-(r/R)^2),
  Uavg = %.15g m/s, R = %.15g m, NR = %d, NX = %d, RGRAD = %.15g.
  Flow-weighted mean of the constructed profile = %.15g m/s (build identity check).
  Inlet and outlet are zeroGradient so the face flux equals the cell flux exactly
  and div(phi) is zero to machine precision; the walls are noSlip (their face
  normal is radial, so they carry no flux either way).
  THIS FILE IS ALSO THE AGE-GUARD MARKER: run_vmfl006.sh touches every 0/ field
  immediately before launching the solver.
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];

internalField   nonuniform List<vector>
%d
(
%s
)
;

boundaryField
{
    inlet   { type zeroGradient; }
    outlet  { type zeroGradient; }
    walls   { type noSlip; }
    wedge1  { type wedge; }
    wedge2  { type wedge; }
}
''' % (U_AVG, R_PIPE, nr, nx, rgrad, mean_u, ncell, body))
    out = os.path.join(zero, "U")
    open(out, "w").write(txt)
    print("  0/U written: %d cells (NX=%d, NR=%d, RGRAD=%g), u_max=%.9f m/s, "
          "flow-weighted mean=%.15g m/s" % (ncell, nx, nr, rgrad, max(u_band), mean_u))
    return {"ncell": ncell, "nx": nx, "nr": nr, "mean_u": mean_u, "u_max": max(u_band)}


def selftest():
    ok = True

    def chk(name, cond, got=""):
        nonlocal ok
        print("  [%s] %s  %s" % ("PASS" if cond else "FAIL", name, got))
        ok = ok and bool(cond)

    print("--- make_u_vmfl006.py --selftest")
    f = radial_faces(4, 1.0)
    chk("uniform grading gives uniform faces", all(
        abs(f[k] - R_PIPE * k / 4) < 1e-15 for k in range(5)), f)
    g = radial_faces(8, 0.25)
    chk("graded faces start at 0 and end exactly at R",
        g[0] == 0.0 and abs(g[-1] - R_PIPE) < 1e-18)
    w = [g[k + 1] - g[k] for k in range(8)]
    chk("rgrad=0.25 -> last cell is a quarter of the first",
        abs(w[-1] / w[0] - 0.25) < 1e-12, "%.12f" % (w[-1] / w[0]))
    chk("graded widths are monotonically decreasing towards the wall",
        all(w[k + 1] < w[k] for k in range(7)))

    # the identity the writer is built on, driven on several levels
    for nr, rg in ((5, 1.0), (20, 0.25), (40, 0.25), (80, 0.25), (13, 3.0)):
        fc = radial_faces(nr, rg)
        num = sum(cell_velocity(fc[j], fc[j + 1]) * (fc[j + 1] ** 2 - fc[j] ** 2) for j in range(nr))
        den = sum((fc[j + 1] ** 2 - fc[j] ** 2) for j in range(nr))
        chk("cell-averaged profile has flow-weighted mean exactly 1 m/s (NR=%d, rgrad=%g)"
            % (nr, rg), abs(num / den - U_AVG) < 1e-13, "%.16g" % (num / den))

    # a CENTROID-sampled profile must NOT have that property -- this is the control
    # that shows the check above can fail, so it is not a green light wired to nothing.
    fc = radial_faces(20, 0.25)
    rc = [0.5 * (fc[j] + fc[j + 1]) for j in range(20)]
    uc = [2.0 * U_AVG * (1.0 - (r / R_PIPE) ** 2) for r in rc]
    num = sum(uc[j] * (fc[j + 1] ** 2 - fc[j] ** 2) for j in range(20))
    den = sum((fc[j + 1] ** 2 - fc[j] ** 2) for j in range(20))
    chk("CONTROL: a centroid-sampled profile FAILS the same identity (so it can fail)",
        abs(num / den - U_AVG) > 1e-9, "%.12f" % (num / den))

    chk("cell_velocity is exactly 2*Uavg on the axis cell of an infinitely fine mesh",
        abs(cell_velocity(0.0, 0.0) - 2.0 * U_AVG) < 1e-15)
    chk("cell_velocity is negative-free at the wall band",
        cell_velocity(R_PIPE * 0.99, R_PIPE) > 0.0)

    print("SELFTEST: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if len(sys.argv) < 4:
        refuse("U0", "usage: make_u_vmfl006.py <case_dir> <NR> <RGRAD>")
    build(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
    sys.exit(0)
