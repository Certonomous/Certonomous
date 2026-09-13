#!/usr/bin/env python3
"""
isentropic_init.py -- set T, p and rho consistently with a potentialFoam velocity field.

WHY. potentialFoam gives U and phi a field consistent with the GEOMETRY but sets NO
thermodynamic state, so stage 1 began with a developed velocity field sitting on a UNIFORM
310 K. Stagnation regions that should be near 355 K and accelerated regions that should be
cooler were all at freestream, the energy equation had to invent the entire thermal field at
once (enthalpy initial residual 0.999999999957), and by iteration 2 the temperature had been
driven through BOTH limiter bounds. Fixing the kinematic inconsistency moved the failure to the
equation that still had one.

  AN INITIAL CONDITION MUST BE SELF-CONSISTENT ACROSS ALL FIELDS, NOT JUST THE ONE THAT
  FAILED LAST.

WHAT IS AND IS NOT CLAIMED. potentialFoam solves INCOMPRESSIBLE potential flow, so at
M_inf = 0.85 its velocity field is NOT the compressible one, particularly near the shock.
THE PURPOSE OF THIS INITIALISATION IS TO BE SELF-CONSISTENT, NOT CORRECT: a thermodynamic state
consistent with the velocity field it is given, so that no equation has to invent everything at
once. It is not an attempt at the answer.

RELATIONS -- the EXACT isentropic forms, not the linearised one. Total temperature is constant:
    T  = T0 / (1 + (g-1)/2 * M^2),  T0 = T_inf * (1 + (g-1)/2 * M_inf^2)
with M = |U| / sqrt(g R T), which is implicit in T. Solved in CLOSED FORM: writing x = M^2,
    |U|^2 = x g R T0 / (1 + (g-1)/2 x)   =>   x = |U|^2 / (g R T0 - (g-1)/2 |U|^2)
Then p = p_inf (T/T_inf)^(g/(g-1)) and rho = p/(R T), so density is set from a state that was
chosen rather than derived from one that was not.
"""
import argparse, glob, os, re, struct, sys
import numpy as np

G = 1.4
R = 287.058


def read_internal(path):
    """Return (values, raw_bytes, match) for an OpenFOAM scalar/vector internalField."""
    d = open(path, "rb").read()
    m = re.search(rb"internalField\s+nonuniform[^(]*?(\d+)\s*\(", d, re.S)
    if m:
        n = int(m.group(1))
        ncmp = 3 if b"List<vector>" in d[:m.end()] else 1
        vals = np.frombuffer(d, dtype="<f8", count=n * ncmp, offset=m.end())
        return vals.reshape(n, ncmp) if ncmp == 3 else vals, d, ("binary", n)
    m = re.search(rb"internalField\s+uniform\s+\(([^)]*)\)\s*;", d)
    if m:
        v = np.array([float(x) for x in m.group(1).split()])
        return v, d, ("uniform_vec", None)
    m = re.search(rb"internalField\s+uniform\s+([0-9.eE+-]+)\s*;", d)
    if m:
        return float(m.group(1)), d, ("uniform", None)
    raise ValueError(f"cannot parse internalField in {path}")


def write_scalar_nonuniform(path, values):
    """Replace internalField in an existing scalar field file, keeping its boundaryField AND its
    declared format.

    WRITE IN THE FORMAT THE FILE DECLARES. The first version wrote ASCII values and flipped the
    FoamFile header to `ascii` -- which broke the file a second way: potentialFoam had written the
    boundaryField in BINARY form, where an empty patch list is `nonuniform List<scalar> 0;` with no
    parentheses. Under an ascii header the reader demands ASCII syntax and chokes on exactly those
    entries ("Expected a '(' or a '{' while reading List, found punctuation ';'"). Changing a
    file-level declaration reinterprets EVERY part of the file, not the part being edited.
    """
    d = open(path, "rb").read()
    m = re.search(rb"\bformat\s+(\w+)\s*;", d)
    fmt = m.group(1).decode() if m else "ascii"
    if fmt == "binary":
        payload = struct.pack("<%dd" % len(values), *values)
        body = (b"internalField   nonuniform List<scalar>\n%d\n(" % len(values)) + payload + b")\n;\n"
    else:
        body = b"internalField   nonuniform List<scalar>\n%d\n(\n" % len(values)
        body += b"\n".join(b"%.10g" % v for v in values)
        body += b"\n)\n;\n"
    # match the existing internalField entry, binary payload included (it may contain ';' bytes)
    m0 = re.search(rb"internalField\s+nonuniform[^(]*?\(", d, re.S)
    if m0:
        n_old = int(re.search(rb"(\d+)\s*\($", d[:m0.end()], re.S).group(1))
        if fmt == "binary":
            end = m0.end() + n_old * 8
            end = d.index(b";", end) + 1
        else:
            end = d.index(b";", d.index(b")", m0.end())) + 1
        out = d[:m0.start()] + body + d[end:]
    else:
        m1 = re.search(rb"internalField\s+uniform\s+[0-9.eE+-]+\s*;", d)
        if not m1:
            raise ValueError(f"could not locate internalField in {path}")
        out = d[:m1.start()] + body + d[m1.end():]
    open(path, "wb").write(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--Tinf", type=float, required=True)
    ap.add_argument("--pinf", type=float, required=True)
    ap.add_argument("--Minf", type=float, required=True)
    ap.add_argument("--Mmax", type=float, default=1.5,
                    help="DOCUMENTED clamp on the initial local Mach number. Incompressible "
                         "potential flow is SINGULAR at sharp edges: on a cold start it produced "
                         "a local M near 74 (T = 0.325 K, p ~ 0 Pa) on the CRM trailing edge and "
                         "tip. That is an artefact of the incompressible model, not a flow "
                         "feature, and an initial state containing it is unusable. Clamped, "
                         "counted and REPORTED -- never silently.")
    a = ap.parse_args()

    T0 = a.Tinf * (1.0 + 0.5 * (G - 1.0) * a.Minf ** 2)
    Uinf = a.Minf * np.sqrt(G * R * a.Tinf)

    # ---- SELF-CHECK: the freestream speed must reproduce T_inf and p_inf EXACTLY ----
    x = Uinf ** 2 / (G * R * T0 - 0.5 * (G - 1.0) * Uinf ** 2)
    Tchk = T0 / (1.0 + 0.5 * (G - 1.0) * x)
    pchk = a.pinf * (Tchk / a.Tinf) ** (G / (G - 1.0))
    print(f"  T0 = {T0:.6f} K   U_inf = {Uinf:.6f} m/s")
    print(f"  SELF-CHECK at |U| = U_inf:  M = {np.sqrt(x):.9f} (target {a.Minf})")
    print(f"                              T = {Tchk:.9f} K (target {a.Tinf})")
    print(f"                              p = {pchk:.6f} Pa (target {a.pinf})")
    assert abs(np.sqrt(x) - a.Minf) < 1e-9 and abs(Tchk - a.Tinf) < 1e-6, "closed form is wrong"

    procs = sorted(glob.glob(os.path.join(a.case, "processor*")),
                   key=lambda s: int(re.search(r"\d+$", s).group()))
    if not procs:
        procs = [a.case]
    tot = 0
    nclamp = [0]
    Tlo = Thi = plo = phi_ = None
    for d in procs:
        up = os.path.join(d, "0", "U")
        U, _, kind = read_internal(up)
        if kind[0] != "binary":
            print(f"  {os.path.basename(d)}: U is {kind[0]} -- potentialFoam did not write a field here")
            return 2
        mag = np.linalg.norm(U, axis=1)
        x = mag ** 2 / (G * R * T0 - 0.5 * (G - 1.0) * mag ** 2)
        x = np.clip(x, 0.0, None)
        nclamp_local = int((x > a.Mmax ** 2).sum())
        nclamp[0] += nclamp_local
        x = np.minimum(x, a.Mmax ** 2)
        T = T0 / (1.0 + 0.5 * (G - 1.0) * x)
        p = a.pinf * (T / a.Tinf) ** (G / (G - 1.0))
        rho = p / (R * T)
        write_scalar_nonuniform(os.path.join(d, "0", "T"), T)
        write_scalar_nonuniform(os.path.join(d, "0", "p"), p)
        rp = os.path.join(d, "0", "rho")
        if os.path.exists(rp):
            write_scalar_nonuniform(rp, rho)
        tot += len(T)
        Tlo = T.min() if Tlo is None else min(Tlo, T.min())
        Thi = T.max() if Thi is None else max(Thi, T.max())
        plo = p.min() if plo is None else min(plo, p.min())
        phi_ = p.max() if phi_ is None else max(phi_, p.max())
    print(f"  wrote T, p, rho over {tot:,} cells in {len(procs)} tree(s)")
    print(f"  CLAMPED to M <= {a.Mmax}: {nclamp[0]:,} cells "
          f"({100.0*nclamp[0]/max(tot,1):.4f} %) -- potential-flow singularities at sharp edges, "
          f"an artefact of the INCOMPRESSIBLE model, clamped and counted rather than hidden")
    print(f"  T range [{Tlo:.3f}, {Thi:.3f}] K      (T_inf {a.Tinf}, T0 {T0:.3f})")
    print(f"  p range [{plo:.3f}, {phi_:.3f}] Pa    (p_inf {a.pinf})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
