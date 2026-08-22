#!/usr/bin/env python3
"""
T10a-VF analyser.

For one case: stream `constant/F` and `constant/globalFaceFaces`, and for every
boundary (view-factor) face report

  rowSum          sum_j F_ij     -- for a CLOSED enclosure this is exactly 1,
                                    independently of how coarsely the surfaces
                                    are faceted, so (rowSum - 1) needs no
                                    reference band of any kind
  nEdgeVis        how many of the emitting face's edge-sharing mesh neighbours
                  appear in its own visibility list
  Fedge           sum of F_ij over exactly those neighbours

and aggregates per patch.  Writes JSON next to the case.

Read-only with respect to the view-factor data; the only file written is the
analysis JSON at --out.
"""
import sys, os, json, math, re, argparse
from collections import defaultdict


def read_boundary(case):
    txt = open(os.path.join(case, "constant", "polyMesh", "boundary")).read()
    body = txt[txt.index("// * * *"):]
    return [(m.group(1), int(m.group(2)), int(m.group(3)))
            for m in re.finditer(
                r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", body, re.S)]


def read_faces(case, lo, hi):
    path = os.path.join(case, "constant", "polyMesh", "faces")
    out = {}
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        for line in fh:
            if line.strip() == "(":
                break
        i = 0
        while i < hi:
            s = fh.readline().strip()
            if not s or s == "(":
                continue
            if lo <= i < hi:
                k = s.index("(")
                out[i] = tuple(int(x) for x in s[k + 1:s.rindex(")")].split())
            i += 1
    return out


def stream_list_list(path, cast):
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        if n is None:
            raise RuntimeError("no size in " + path)
        for line in fh:
            if line.strip() == "(":
                break
        for _ in range(n):
            # AMENDMENT 2026-08-22 (post-freeze, disclosed in T10aVF_RESULTS):
            # OpenFOAM writes a SHORT inner list inline as `N(v1 v2 ... vN)` on
            # one line (and an empty one as `0()`) instead of the block form the
            # frozen parser assumed.  Cases whose visibility lists are short --
            # the agglomerated pair, and the intTol=1e-4 case whose rays are too
            # short to escape their own faces -- are written that way, and the
            # frozen parser raised on them rather than mis-reading them.  Reading
            # a format it previously refused cannot change a number it already
            # read: every block-form case re-parses bit-identically.
            m = None
            inline = None
            for line in fh:
                s = line.strip()
                if not s or s == "(":
                    continue
                if "(" in s:
                    k = s.index("(")
                    m = int(s[:k])
                    body = s[k + 1:s.rindex(")")].strip()
                    inline = [cast(x) for x in body.split()] if body else []
                else:
                    m = int(s)
                break
            if inline is not None:
                if len(inline) != m:
                    raise RuntimeError("inline row length mismatch")
                yield inline
                continue
            for line in fh:
                if line.strip() == "(":
                    break
            row = [None] * m
            k = 0
            while k < m:
                s = fh.readline().strip()
                if not s:
                    continue
                row[k] = cast(s); k += 1
            for line in fh:
                if line.strip() == ")":
                    break
            yield row


def analyse(case, alpha=None):
    bnds = read_boundary(case)
    off = 0
    comp = []          # (name, compactLo, compactHi, startFace)
    for nm, nf, sf in bnds:
        comp.append((nm, off, off + nf, sf))
        off += nf
    ntot = off
    lo = min(b[2] for b in bnds)
    hi = max(b[2] + b[1] for b in bnds)
    faces = read_faces(case, lo, hi)

    # compact index <-> global face index
    g2c = {}
    c2g = [0] * ntot
    for nm, cl, ch, sf in comp:
        for k in range(ch - cl):
            g2c[sf + k] = cl + k
            c2g[cl + k] = sf + k
    pname = [None] * ntot
    for nm, cl, ch, sf in comp:
        for c in range(cl, ch):
            pname[c] = nm

    # edge -> compact faces, restricted to the view-factor boundary
    e2f = defaultdict(list)
    for c in range(ntot):
        fv = faces[c2g[c]]
        for k in range(len(fv)):
            e2f[frozenset((fv[k], fv[(k + 1) % len(fv)]))].append(c)
    nbr = [set() for _ in range(ntot)]
    for e, fl in e2f.items():
        if len(fl) > 1:
            for x in fl:
                for y in fl:
                    if x != y:
                        nbr[x].add(y)

    P = {nm: dict(n=0, rowsum=0.0, rmin=1e30, rmax=-1e30, rows=[],
                  nEdgeTot=0, nEdgeVis=0, Fedge=0.0, Fself=0.0,
                  cross=defaultdict(float), nvis=0)
         for nm, _, _, _ in comp}

    fgen = stream_list_list(os.path.join(case, "constant", "F"), float)
    ggen = stream_list_list(os.path.join(case, "constant", "globalFaceFaces"), int)
    i = 0
    for frow, grow in zip(fgen, ggen):
        nm = pname[i]
        st = P[nm]
        nb = nbr[i]
        tot = 0.0
        fe = 0.0
        ne = 0
        for v, j in zip(frow, grow):
            tot += v
            st["cross"][pname[j]] += v
            if j in nb:
                fe += v
                ne += 1
        st["n"] += 1
        st["rowsum"] += tot
        st["rmin"] = min(st["rmin"], tot)
        st["rmax"] = max(st["rmax"], tot)
        st["rows"].append(tot)
        st["nEdgeTot"] += len(nb)
        st["nEdgeVis"] += ne
        st["Fedge"] += fe
        st["nvis"] += len(frow)
        i += 1

    out = dict(case=os.path.abspath(case), nFaces=ntot, rowsInF=i, patches={})
    meta_p = os.path.join(case, "CASE.json")
    if os.path.exists(meta_p):
        out["meta"] = json.load(open(meta_p))
        if alpha is None:
            alpha = out["meta"].get("alpha")
    out["alpha"] = alpha
    if alpha:
        out["e_alpha_pred"] = -(2.0 * math.log(alpha) + 3.0) / (4.0 * math.pi)
    for nm, _, _, _ in comp:
        st = P[nm]
        if st["n"] == 0:
            continue
        rows = sorted(st["rows"])
        mean = st["rowsum"] / st["n"]
        nEv = st["nEdgeVis"] / st["n"]
        exc = mean - 1.0
        d = dict(nRows=st["n"], meanRowSum=mean, minRowSum=rows[0],
                 maxRowSum=rows[-1], medRowSum=rows[len(rows) // 2],
                 meanExcess=exc, maxExcess=rows[-1] - 1.0,
                 meanExcessPct=100.0 * exc, maxExcessPct=100.0 * (rows[-1] - 1.0),
                 meanEdgeNbrs=st["nEdgeTot"] / st["n"],
                 meanEdgeNbrsVisible=nEv,
                 meanF_on_edge_nbrs=st["Fedge"] / st["n"],
                 meanVisible=st["nvis"] / st["n"],
                 cross={k: v / st["n"] for k, v in st["cross"].items()})
        if alpha and nEv > 1e-9:
            d["excess_per_edge_pair"] = exc / nEv
            d["excess_over_predicted"] = (exc / nEv) / out["e_alpha_pred"] \
                if abs(out["e_alpha_pred"]) > 1e-12 else None
            d["predicted_excess"] = nEv * out["e_alpha_pred"]
        out["patches"][nm] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="+")
    ap.add_argument("--out", default=None, help="write combined JSON here")
    ap.add_argument("--alpha", type=float, default=None)
    a = ap.parse_args()
    allr = []
    print("%-24s %-9s %7s %11s %11s %11s %8s %11s %11s" %
          ("case", "patch", "nRows", "meanRowSum", "meanExc%", "maxExc%",
           "nEdgeVis", "exc/pair", "pred/pair"))
    for c in a.cases:
        try:
            r = analyse(c, a.alpha)
        except Exception as e:
            print("%-24s  ERROR %s" % (os.path.basename(c), e))
            continue
        allr.append(r)
        base = os.path.basename(os.path.abspath(c))
        for nm, d in r["patches"].items():
            print("%-24s %-9s %7d %11.7f %11.4f %11.4f %8.3f %11.7f %11.7f" %
                  (base, nm, d["nRows"], d["meanRowSum"], d["meanExcessPct"],
                   d["maxExcessPct"], d["meanEdgeNbrsVisible"],
                   d.get("excess_per_edge_pair", float("nan")),
                   r.get("e_alpha_pred", float("nan"))))
        sys.stdout.flush()
    if a.out:
        json.dump(allr, open(a.out, "w"), indent=1)
        print("\nwrote %s" % os.path.abspath(a.out))


if __name__ == "__main__":
    main()
