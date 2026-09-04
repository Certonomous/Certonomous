#!/usr/bin/env python3
"""Family-identity proof for the ONERA M6 `wing_strct` three-direction family.

Grades `Gate F` of `verification/campaign/M6F_PREREGISTRATION.md` from the
artifacts on disk. Reports; grades nothing it cannot measure.

THREE THINGS THIS SCRIPT EXISTS TO STOP:

  R-ENDIAN   The `.lb8.ugrid` files are LITTLE-endian raw-C. A big-endian read
             of the L1 header implies a NEGATIVE file size. The byte-order is
             established by the TOTAL-BYTE-BUDGET IDENTITY, never by a
             plausibility heuristic, and the wrong order is read back and shown
             to be rejected -- a reader not proven able to see the wrong answer
             has not been proven able to see the right one (CLAUDE.md rule 3).

  R-HEXONLY  The volume cell count is HEXES + PRISMS. The prisms are the
             degenerate cells on the collapsed pole axis. Counting hexes alone
             gives ratios 8.103 / 8.211 / 8.444 / 9.000 -- NOT 8 -- and makes a
             sound family look broken.

  R-PATCH    L1's `.mapbc` names patches lowercase (`wing`/`symmetry`/`farfield`)
             while L2-L5 use uppercase (`WING3D`/`SYMMETRY`/`FARFIELD`), AND on
             L2-L5 the `.nmf` face type (`back_pressure`) disagrees with the
             `.mapbc` code (6662 = symmetry). Both are refusals.

Exit 0 = every check this script can make passed. Exit 2 = a REFUSAL (the
script stops rather than degrading). Exit 1 = a measured GATE FAIL.
"""
import os
import struct
import sys

MESH = os.environ.get(
    "M6_MESH_DIR",
    "/home/ubuntu/Certonomous/verification/runs/M6I_runs/mesh")

EXPECT_DIMS = {1: (81, 129, 97), 2: (41, 65, 49), 3: (21, 33, 25),
               4: (11, 17, 13), 5: (6, 9, 7)}
EXPECT_CELLS = {1: 983040, 2: 122880, 3: 15360, 4: 1920, 5: 240}


class Refusal(Exception):
    """A condition this script must stop on under ANY interpreter flag.

    NOT an `assert`: `python3 -O` deletes every assert statement, which would
    remove the entire guard set and turn this comparator into a rubber stamp.
    """


def ugrid_counts(path):
    """(nNode, nTri, nQuad, nTet, nPyr, nPrism, nHex), byte order proven.

    Both orders are tried and each is scored by whether it reproduces the
    ACTUAL file size exactly. Exactly one must survive.
    """
    with open(path, "rb") as f:
        raw = f.read(28)
    actual = os.path.getsize(path)
    survivors = []
    for endian, name in (("<", "little"), (">", "big")):
        h = struct.unpack(endian + "7i", raw)
        nNode, nTri, nQuad, nTet, nPyr, nPrism, nHex = h
        budget = (28 + nNode * 3 * 8 + nTri * 3 * 4 + nQuad * 4 * 4
                  + nTri * 4 + nQuad * 4 + nTet * 4 * 4 + nPyr * 5 * 4
                  + nPrism * 6 * 4 + nHex * 8 * 4)
        survivors.append((name, h, budget, budget == actual))
    ok = [s for s in survivors if s[3]]
    if len(ok) != 1:
        raise Refusal(
            "R-ENDIAN: %d byte orders reproduce the actual size of %s (%d B). "
            "Budgets: %s" % (len(ok), path, actual,
                             [(s[0], s[2]) for s in survivors]))
    return ok[0][1], survivors


def nmf_dims(path):
    """(IDIM, JDIM, KDIM) and the list of BC type tokens, from the .nmf text."""
    dims, types = None, []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) == 4 and all(t.isdigit() for t in p):
            dims = (int(p[1]), int(p[2]), int(p[3]))
        elif p[0].isalpha() or "_" in p[0]:
            types.append(p[0])
    return dims, types


def mapbc_names(path):
    """[(code, name)] from the .mapbc sidecar."""
    out = []
    for line in open(path):
        p = line.split("!")[0].split()
        if len(p) == 3 and p[0].isdigit() and p[1].isdigit():
            out.append((int(p[1]), p[2]))
    return out


def main():
    fails, refusals = [], []
    print("M6 FAMILY IDENTITY -- Gate F")
    print("mesh dir: %s\n" % MESH)

    # ---- F6 FIRST: the planted endianness control. Nothing grades until it passes.
    p1 = os.path.join(MESH, "wing_strct.1.lb8.ugrid")
    if not os.path.exists(p1):
        print("BLOCKED: %s absent -- nothing to grade." % p1)
        return 2
    _, survivors = ugrid_counts(p1)
    bad = [s for s in survivors if s[0] == "big"][0]
    if bad[3]:
        print("F6  NOT A RESULT -- the big-endian read of L1 was ACCEPTED. "
              "The reader cannot tell the orders apart; every figure below is void.")
        return 2
    print("F6  PASS  planted control: big-endian read of L1 implies %d B against "
          "an actual %d B -> REJECTED. The reader can see the wrong answer."
          % (bad[2], os.path.getsize(p1)))

    # ---- F1/F2/F3/F4
    counts, dims_all = {}, {}
    print("\nlvl   IDIMxJDIMxKDIM   hex      prism    TOTAL cells   (I-1)(J-1)(K-1)")
    for L in range(1, 6):
        up = os.path.join(MESH, "wing_strct.%d.lb8.ugrid" % L)
        np_ = os.path.join(MESH, "wing_strct.%d.nmf" % L)
        if not (os.path.exists(up) and os.path.exists(np_)):
            print("BLOCKED: level %d artifacts absent." % L)
            return 2
        h, _ = ugrid_counts(up)
        nHex, nPrism = h[6], h[5]
        total = nHex + nPrism          # R-HEXONLY: hexes ALONE are not the count
        d, _types = nmf_dims(np_)
        struct_cells = (d[0] - 1) * (d[1] - 1) * (d[2] - 1)
        counts[L], dims_all[L] = total, d
        mark = "OK" if struct_cells == total else "MISMATCH"
        print("L%d    %3dx%3dx%-3d  %8d %8d %13d %13d  %s"
              % (L, d[0], d[1], d[2], nHex, nPrism, total, struct_cells, mark))
        if struct_cells != total:
            fails.append("F2 L%d: .nmf dims imply %d cells, .ugrid holds %d"
                         % (L, struct_cells, total))
        if d != EXPECT_DIMS[L]:
            fails.append("F1 L%d: dims %s, registered %s" % (L, d, EXPECT_DIMS[L]))
        if total != EXPECT_CELLS[L]:
            fails.append("F2 L%d: cells %d, registered %d" % (L, total, EXPECT_CELLS[L]))

    print("\nstep      ratio(total)      r          ratio(HEX ONLY -- the trap)")
    for L in range(1, 5):
        rt = counts[L] / counts[L + 1]
        r = rt ** (1.0 / 3.0)
        print("L%d/L%d    %12.6f  %9.6f   (see R-HEXONLY)" % (L, L + 1, rt, r))
        if abs(rt - 8.0) > 1e-9:
            fails.append("F3 L%d/L%d: cell ratio %.9f, registered 8.000000" % (L, L + 1, rt))

    print("\nper-direction (n-1) ratios -- ALL THREE must be exactly 2 (F4)")
    for L in range(1, 5):
        a, b = dims_all[L], dims_all[L + 1]
        rr = [(a[i] - 1) / (b[i] - 1) for i in range(3)]
        ok = all(abs(x - 2.0) < 1e-12 for x in rr)
        print("  L%d->L%d  I %.4f  J(wall-normal) %.4f  K %.4f   %s"
              % (L, L + 1, rr[0], rr[1], rr[2], "OK" if ok else "FAIL"))
        if not ok:
            fails.append("F4 L%d->L%d: (n-1) ratios %s -- not three-directional" % (L, L + 1, rr))

    # ---- R-PATCH: names AND types across levels
    print("\nR-PATCH -- patch names and BC types across levels")
    namesets, typesets = {}, {}
    for L in range(1, 6):
        mp = os.path.join(MESH, "wing_strct.%d.mapbc" % L)
        nf = os.path.join(MESH, "wing_strct.%d.nmf" % L)
        namesets[L] = mapbc_names(mp)
        typesets[L] = nmf_dims(nf)[1]
        print("  L%d  mapbc %s" % (L, namesets[L]))
        print("      nmf   %s" % (typesets[L],))
    base = [n for _, n in namesets[1]]
    for L in range(2, 6):
        if [n for _, n in namesets[L]] != base:
            refusals.append(
                "R-PATCH: L1 patch names %s differ from L%d %s -- a three-level "
                "driver gets different patch names on L1." % (base, L, [n for _, n in namesets[L]]))
            break
    sym_codes = {L: [c for c, _ in namesets[L] if 6660 <= c <= 6669] for L in range(1, 6)}
    for L in range(1, 6):
        if sym_codes[L] and "back_pressure" in typesets[L]:
            refusals.append(
                "R-PATCH: L%d .mapbc carries a symmetry code %s while its .nmf "
                "types are %s -- the two sidecars disagree on whether a face is a "
                "symmetry plane or a pressure outlet. UNRESOLVED: this script does "
                "NOT rule which is authoritative." % (L, sym_codes[L], typesets[L]))

    print("\n" + "=" * 72)
    for r in refusals:
        print("REFUSAL  " + r)
    for f in fails:
        print("GATE FAIL  " + f)
    if refusals:
        print("\nVERDICT: BLOCKED -- a registered refusal fired.")
        return 2
    if fails:
        print("\nVERDICT: GATE FAIL")
        return 1
    print("\nVERDICT: PASS -- F1 dims, F2 cells, F3 ratio 8.000000 / r 2.000000, "
          "F4 all three directions halve, F6 control live.")
    print("NOT GRADED HERE: F5 (points-array sha256) needs the emitted grid, not the header.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        print("REFUSAL: %s" % e)
        sys.exit(2)
