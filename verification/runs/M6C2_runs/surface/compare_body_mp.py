#!/usr/bin/env python3
"""BODY COMPARISON for the MULTI-PATCH surface family, and against AR-138 itself.

WHY AN ADAPTER AND NOT A SECOND INSTRUMENT. `compare_body.py` takes a SINGLE-BLOCK
surface whose first block is the whole section. The multi-patch file's first block
is one ARC of the section, so handing it over directly would compare upper surfaces
only -- and its planted TE-collapse control would then come back UNDETECTED and the
instrument would (correctly) REFUSE with exit 2 rather than report agreement. That
refusal is the instrument working. The fix is to give it the body it expects.

So this module REASSEMBLES the four wing arcs into the closed section at every
spanwise station and calls `compare_body`'s OWN functions -- the same comparison and
the same planted controls, not a reimplementation of them. A second implementation
of a check is a second chance to be wrong in the same direction.

IT ALSO ADDS THE COMPARISON THE LEVEL-TO-LEVEL TEST CANNOT MAKE: three levels can
agree with each other perfectly and all three be the wrong wing. So every level is
ALSO compared against the AR-138 Table B1-1 section itself, read from
`models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`
(sha256 66b2a7bc...34ab7, provenance in models/onera_m6/PROVENANCE.md), lofted
conically, at the same stations. That is the check A3's surface fails and which no
level-to-level comparison would ever have caught.
"""
import sys, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, "/home/ubuntu/Certonomous/verification/runs/M6C1_runs/geometry")
import compare_body as CB
import m6_section as M
from build_ohgrid import section_loop
import build_capped_multipatch as BC

# patch order written by build_capped_multipatch.build()
I_UP, I_BASE, I_LO, I_NOSE = 0, 1, 2, 3


def reassemble(path):
    """The four wing arcs -> one closed section per spanwise station, (nk+1, ni+1, 3).

    Arc orientations, from build_capped_multipatch.arc_indices:
        UP    nose-end  -> upper TE corner
        BASE  upper TE  -> lower TE corner
        LO    lower TE  -> nose-start
        NOSE  lower nose-start -> LE -> upper nose-end
    So the loop is NOSE[k:] + UP[1:] + BASE[1:] + LO[1:] + NOSE[1:k+1], and the
    junction points are dropped exactly once each. It is asserted closed, not assumed.
    """
    B = CB.read_plot3d(path)              # each (spanwise, arc, 3)
    UP, BASE, LO, NOSE = B[I_UP], B[I_BASE], B[I_LO], B[I_NOSE]
    m = (NOSE.shape[1] - 1) // 2          # index of the LE inside the nose arc
    loop = np.concatenate([NOSE[:, m:, :], UP[:, 1:, :], BASE[:, 1:, :],
                           LO[:, 1:, :], NOSE[:, 1:m+1, :]], axis=1)
    assert np.allclose(loop[:, 0, :], loop[:, -1, :]), "reassembled section is not closed"
    return loop


def reference(nk, ni, n_base, eta_max):
    """The AR-138 body itself, lofted conically at the same stations. Not a mesh."""
    lp = section_loop(ni, n_base)
    etas = eta_max * np.linspace(0.0, 1.0, nk + 1)
    S = np.array([M.loft(lp, e) for e in etas])
    return np.concatenate([S, S[:, :1, :]], axis=1)      # close it in i


def report(name, rows):
    dev, dte, dch, ok = CB.verdict(rows)
    print(f"  {name:34s} max dev {dev:.3e}   dTE(t/c) {dte:.3e}   dchord {dch:.3e}   "
          f"-> {'SAME BODY' if ok else 'BODY DIFFERS -- REFUSE'}")
    return ok


if __name__ == "__main__":
    files = sys.argv[1:]
    loops = {pathlib.Path(f).stem: reassemble(f) for f in files}
    for n, L in loops.items():
        print(f"  {n}: reassembled {L.shape[0]} stations x {L.shape[1]} section points")

    print("\nPLANTED CONTROLS -- run on THIS family's own body, via compare_body's code")
    SA = list(loops.values())[0]
    ctl = []
    d0 = CB.verdict(CB.compare(SA, SA.copy()))
    ctl.append(("C1 identical body -> AGREE", d0[3], f"max dev {d0[0]:.2e}"))
    Bte = SA.copy()
    xm = Bte[:, :, 0].max(axis=1, keepdims=True); m = Bte[:, :, 0] > xm - 1e-9
    for k in range(Bte.shape[0]):
        Bte[k, m[k], 2] = Bte[k, m[k], 2].mean()
    d1 = CB.verdict(CB.compare(SA, Bte))
    ctl.append(("C2 planted TE COLLAPSE -> REFUSE", not d1[3], f"max dev {d1[0]:.2e}, dTE {d1[1]:.2e}"))
    Ble = SA.copy()
    for k in range(Ble.shape[0]):
        x = Ble[k, :, 0]; cut = x.min() + 0.0041 * M.C_ROOT
        Ble[k, x < cut, 0] = cut
    d2 = CB.verdict(CB.compare(SA, Ble))
    ctl.append(("C3 planted LE TRUNCATION 0.41% -> REFUSE", not d2[3], f"max dev {d2[0]:.2e}, dchord {d2[2]:.2e}"))
    # C4: the A3 failure mode itself -- t_TE held ABSOLUTELY constant instead of conical
    Ba3 = SA.copy()
    for k in range(Ba3.shape[0]):
        x = Ba3[k, :, 0]; mm = x > x.max() - 1e-9
        z = Ba3[k, mm, 2]; c = x.max() - x.min()
        Ba3[k, mm, 2] = z * (M.C_ROOT / c)          # freeze t_TE at its ROOT value
    d3 = CB.verdict(CB.compare(SA, Ba3))
    ctl.append(("C4 planted A3 CONSTANT-ABSOLUTE t_TE -> REFUSE", not d3[3],
                f"max dev {d3[0]:.2e}, dTE {d3[1]:.2e}"))
    for nm, ok, det in ctl:
        print(f"  {'PASS' if ok else 'FAIL'}  {nm:46s} {det}")
    if not all(o for _, o, _ in ctl):
        print("REFUSED (2): the reader was not shown able to see every planted change.")
        sys.exit(2)

    print("\nLEVEL-TO-LEVEL  (three levels can agree and all three be the wrong wing)")
    ks = list(loops)
    allok = True
    for i in range(len(ks) - 1):
        allok &= report(f"{ks[i]} vs {ks[i+1]}", CB.compare(loops[ks[i]], loops[ks[i+1]]))

    print("\nAGAINST AR-138 TABLE B1-1 ITSELF  (the check level-to-level cannot make)")
    eta_max = (M.SEMISPAN - BC.H_CAP) / M.SEMISPAN
    for n, L in loops.items():
        nk, npts = L.shape[0] - 1, L.shape[1] - 1
        nb = {201: 16, 301: 24, 451: 36}.get(npts + 1, None)
        nb = nb if nb else int(round(npts * 16 / 200))
        REF = reference(nk, npts, nb, eta_max)
        allok &= report(f"{n} vs AR-138 conical loft", CB.compare(L, REF))
    sys.exit(0 if allok else 5)
