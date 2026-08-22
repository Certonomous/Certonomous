#!/usr/bin/env python3
"""Print per-patch view-factor row sums for an OpenFOAM case.  stdlib only.

For any CLOSED enclosure of opaque surfaces, sum_j F_ij = 1 exactly for every
face i, whatever the mesh.  This script reads constant/F (written by
viewFactorsGen) and constant/polyMesh/boundary and reports how far each patch's
rows are from 1.
"""
import sys, os, re


def rows(path):
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        for line in fh:
            if line.strip() == "(":
                break
        for _ in range(n):
            m = inline = None
            for line in fh:
                s = line.strip()
                if not s or s == "(":
                    continue
                if "(" in s:
                    k = s.index("(")
                    m = int(s[:k]); b = s[k+1:s.rindex(")")].strip()
                    inline = [float(x) for x in b.split()] if b else []
                else:
                    m = int(s)
                break
            if inline is not None:
                yield inline; continue
            for line in fh:
                if line.strip() == "(":
                    break
            r = []
            while len(r) < m:
                s = fh.readline().strip()
                if s:
                    r.append(float(s))
            for line in fh:
                if line.strip() == ")":
                    break
            yield r


def main():
    case = sys.argv[1] if len(sys.argv) > 1 else "."
    txt = open(os.path.join(case, "constant/polyMesh/boundary")).read()
    body = txt[txt.index("// * * *"):]
    pat = [(m.group(1), int(m.group(2))) for m in re.finditer(
        r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", body, re.S)]
    alpha = "?"
    try:
        d = open(os.path.join(case, "constant/viewFactorsDict")).read()
        alpha = re.search(r"^\s*alpha\s+([0-9.eE+-]+)\s*;", d, re.M).group(1)
    except Exception:
        pass
    lo = 0
    lim = []
    for nm, nf in pat:
        lim.append((nm, lo, lo + nf)); lo += nf
    acc = {nm: [] for nm, _ in pat}
    i = 0
    for r in rows(os.path.join(case, "constant/F")):
        for nm, a, b in lim:
            if a <= i < b:
                acc[nm].append(sum(r)); break
        i += 1
    print("case %s   alpha = %s" % (os.path.abspath(case), alpha))
    print("%-10s %7s %13s %13s %13s %12s" %
          ("patch", "nFaces", "mean rowSum", "min rowSum", "max rowSum", "mean err %"))
    for nm, _, _ in lim:
        v = acc[nm]
        if not v:
            continue
        mean = sum(v) / len(v)
        print("%-10s %7d %13.6f %13.6f %13.6f %12.4f" %
              (nm, len(v), mean, min(v), max(v), 100 * (mean - 1.0)))
    print()


if __name__ == "__main__":
    main()
