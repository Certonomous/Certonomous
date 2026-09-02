#!/usr/bin/env python3
"""
VMFL007-R3 — DIAGNOSTIC READER.  Does the powerLaw nuMax clip BIND in a converged
solution?  Reads a discrete OpenFOAM volScalarField `nu` from disk together with the
cell-centre fields Cx/Cy/Cz, and reports min/max plus the count and radii of cells
sitting on either clip.

This script PRODUCES MEASURED NUMBERS.  It is a diagnostic reader only: it grades
nothing, writes nothing into any run directory, and issues no verdict.

Rule-3 planted-failure control is built in and is NOT optional: --plant writes a
known value into a named cell index of a COPY of the field and the same parser then
re-reads it.  A caller that cannot show the reader seeing a planted non-zero has no
right to report a zero.

Usage:
  read_nu_clip.py <caseTimeDir> [--plant IDX:VALUE --plant-out FILE]

Fields expected in <caseTimeDir>: nu, Cx, Cy, Cz.
"""

import sys
import os
import re
import math


def parse_scalar_internal(path):
    """Parse the internalField of an OpenFOAM ascii volScalarField.

    Handles both `nonuniform List<scalar> N ( ... )` and `uniform V`.
    Returns (values, header_lines, body_span) where body_span = (first_value_line,
    last_value_line) as 0-based indices into the raw line list, or None for uniform.
    """
    with open(path) as f:
        lines = f.read().split("\n")

    idx = None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("internalField"):
            idx = i
            break
    if idx is None:
        raise ValueError("no internalField in %s" % path)

    head = lines[idx]
    if "uniform" in head and "nonuniform" not in head:
        m = re.search(r"uniform\s+([-\deE.+]+)", head)
        if not m:
            raise ValueError("cannot parse uniform internalField: %r" % head)
        return [float(m.group(1))], lines, None

    # nonuniform: count may be on the same line or the next non-blank line
    j = idx
    count = None
    m = re.search(r"List<scalar>\s*(\d+)", head)
    if m:
        count = int(m.group(1))
    else:
        j = idx + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        count = int(lines[j].strip())
    # find the opening paren
    k = j + 1
    while k < len(lines) and lines[k].strip() != "(":
        if lines[k].strip().startswith("("):
            break
        k += 1
    first = k + 1
    vals = []
    p = first
    while len(vals) < count:
        s = lines[p].strip()
        if s and s != "(":
            vals.append(float(s))
        p += 1
    last = p - 1
    if len(vals) != count:
        raise ValueError("read %d values, header said %d" % (len(vals), count))
    return vals, lines, (first, last)


def plant(src, dst, cell_idx, value):
    """Write a copy of `src` to `dst` with cell `cell_idx` set to `value`.

    Planting is done BY LINE INDEX into the value block, derived from the same
    parser the measurement uses, so a parser that mislocates the block plants in
    the wrong place and the control fails loudly rather than silently passing.
    """
    vals, lines, span = parse_scalar_internal(src)
    if span is None:
        raise ValueError("cannot plant into a uniform field")
    first, last = span
    # map cell_idx -> line, skipping blank lines exactly as the parser does
    seen = 0
    target_line = None
    for p in range(first, last + 1):
        if lines[p].strip() and lines[p].strip() != "(":
            if seen == cell_idx:
                target_line = p
                break
            seen += 1
    if target_line is None:
        raise ValueError("cell index %d not found in value block" % cell_idx)
    old = lines[target_line].strip()
    lines[target_line] = repr(float(value))
    with open(dst, "w") as f:
        f.write("\n".join(lines))
    return target_line, old


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    tdir = sys.argv[1]
    plant_spec = None
    plant_out = None
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--plant":
            plant_spec = args[i + 1]
            i += 2
        elif args[i] == "--plant-out":
            plant_out = args[i + 1]
            i += 2
        else:
            i += 1

    nupath = os.path.join(tdir, "nu")

    if plant_spec:
        idx_s, val_s = plant_spec.split(":")
        cell_idx, value = int(idx_s), float(val_s)
        if not plant_out:
            print("REFUSE: --plant needs --plant-out")
            return 2
        line_no, old = plant(nupath, plant_out, cell_idx, value)
        vals, _, _ = parse_scalar_internal(plant_out)
        got = vals[cell_idx]
        print("PLANT  cell=%d  file_line=%d  was=%s  planted=%.17g" %
              (cell_idx, line_no + 1, old, value))
        print("REREAD cell=%d  reader_reports=%.17g" % (cell_idx, got))
        print("REREAD max_over_domain=%.17g" % max(vals))
        ok = abs(got - value) <= 1e-12 * max(1.0, abs(value))
        print("CONTROL: %s" % ("READER SEES THE PLANT"
                               if ok else "READER BLIND -> MEASUREMENT REFUSES"))
        return 0 if ok else 2

    nu, _, _ = parse_scalar_internal(nupath)
    cx, _, _ = parse_scalar_internal(os.path.join(tdir, "Cx"))
    cy, _, _ = parse_scalar_internal(os.path.join(tdir, "Cy"))
    cz, _, _ = parse_scalar_internal(os.path.join(tdir, "Cz"))
    n = len(nu)
    if not (len(cx) == len(cy) == len(cz) == n):
        print("REFUSE: field lengths differ: nu=%d Cx=%d Cy=%d Cz=%d"
              % (n, len(cx), len(cy), len(cz)))
        return 2

    # radius in the wedge plane: the axis is x, so r = sqrt(y^2 + z^2)
    r = [math.hypot(cy[i], cz[i]) for i in range(n)]

    NUMIN, NUMAX = 1e-8, 1.0
    hi = [i for i in range(n) if nu[i] >= 0.999 * NUMAX]
    lo = [i for i in range(n) if nu[i] <= 1.001 * NUMIN]

    imin = min(range(n), key=lambda i: nu[i])
    imax = max(range(n), key=lambda i: nu[i])

    print("cells                 = %d" % n)
    print("nu min                = %.12g   at cell %d, r = %.6e m, x = %.6e m"
          % (nu[imin], imin, r[imin], cx[imin]))
    print("nu max                = %.12g   at cell %d, r = %.6e m, x = %.6e m"
          % (nu[imax], imax, r[imax], cx[imax]))
    print("nuMax clip (>= %.6g)  : %d cells" % (0.999 * NUMAX, len(hi)))
    print("nuMin clip (<= %.6g)  : %d cells" % (1.001 * NUMIN, len(lo)))
    print("headroom to nuMax     = %.6g x  (nuMax / nu_max_observed)"
          % (NUMAX / nu[imax]))
    print("headroom to nuMin     = %.6g x  (nu_min_observed / nuMin)"
          % (nu[imin] / NUMIN))
    for tag, lst in (("nuMax-clipped", hi), ("nuMin-clipped", lo)):
        for i in lst[:20]:
            print("  %s cell %d  nu=%.12g  r=%.6e  x=%.6e"
                  % (tag, i, nu[i], r[i], cx[i]))
    rmax = max(r)
    print("mesh radius max       = %.6e m   (min = %.6e m)" % (rmax, min(r)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
