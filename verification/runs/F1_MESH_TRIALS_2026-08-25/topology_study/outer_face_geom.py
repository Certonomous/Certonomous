#!/usr/bin/env python3
"""WHERE and WHY: the worst non-orthogonal face, in geometric terms.

worst_nonortho.py answers WHERE (centroid, owner, neighbour).  It does not print
the FACE NORMAL, and without the normal the angle is a number with no mechanism
attached.  This adds exactly that: the face's four corner points, its unit area
normal, the owner->neighbour vector resolved into face-normal and face-tangential
components, and the structured (block, i, j, k) address of the offending pair.

IT DOES NOT REIMPLEMENT ANYTHING.  Cell centres, face centres and area vectors
come from worst_nonortho.cell_centres -- OpenFOAM's pyramid-weighted form -- by
import, so any correction to that file corrects this one too.

PLANTED CONTROL (CLAUDE.md rule 3), the SAME two legs worst_nonortho.py carries:
  (a) AGREEMENT   -- recomputed max must match log.checkMesh to < 0.05 deg.
  (b) DISPLACEMENT-- moving one point of the winning face must move its angle by
                     > 1e-6 deg.
Both must pass or this exits 2 WITHOUT printing a result.
"""
import os
import re
import sys

import numpy as np

# rule 14 / L-221: the import path is CHECKED, never assumed.  The te-study lane's
# 14 dead variants were a bare sys.path.insert that pointed at nothing.
#
# THESE TWO REFUSALS WERE `assert`s UNTIL 2026-08-25, AND `python3 -O` / PYTHONOPTIMIZE
# DELETE EVERY `assert`.  Under -O this file would have imported WHATEVER `worst_nonortho`
# happened to resolve -- a stale sys.modules entry from another path included -- and then
# reported angles from it as though they came from the reader carrying the planted
# controls.  Rule 14's shape with the assert itself as the removable part.  They now
# refuse explicitly; `--o-control` drives both under -O and requires the refusal.
WN_DIR = "/home/ubuntu/Certonomous/verification/runs/F1_MESH_TRIALS_2026-08-25/te_study"


def _refuse(msg):
    """A provenance check that fails STOPS THE SCRIPT. Never an assert: -O deletes those."""
    print("  REFUSED: " + msg)
    print("  No result printed. (CLAUDE.md rule 14 / L-221)")
    sys.exit(2)


if not os.path.isfile(os.path.join(WN_DIR, "worst_nonortho.py")):
    _refuse("worst_nonortho.py not at " + WN_DIR
            + " -- refusing rather than importing something else")
sys.path.insert(0, WN_DIR)
import worst_nonortho as wn  # noqa: E402
if os.path.dirname(os.path.abspath(wn.__file__)) != WN_DIR:
    _refuse("imported worst_nonortho from " + wn.__file__ + ", not from " + WN_DIR)


def block_index(case):
    """(cells_per_block, (ni,nj,nk) per block) read from the blockMeshDict that
    generated this case.  blockMesh numbers cells block by block, i fastest then
    j then k, so a global cell id maps back to (block, i, j, k) exactly."""
    p = os.path.join(case, "system", "blockMeshDict")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    ns = [tuple(int(v) for v in m) for m in
          re.findall(r"hex \([\d\s]+\)\s*\((\d+) (\d+) (\d+)\)", txt)]
    return ns


def addr(cid, ns):
    if ns is None:
        return "?"
    off = 0
    for b, (ni, nj, nk) in enumerate(ns):
        n = ni * nj * nk
        if cid < off + n:
            r = cid - off
            return f"blk{b:02d}[{ni}x{nj}x{nk}] i={r % ni} j={(r // ni) % nj} k={r // (ni * nj)}"
        off += n
    return "?out-of-range"


def cell_block(ncell, ns):
    """global cell id -> block index, as a vector."""
    b = np.zeros(ncell, dtype=np.int64)
    off = 0
    for i, (ni, nj, nk) in enumerate(ns):
        n = ni * nj * nk
        b[off:off + n] = i
        off += n
    if off != ncell:
        raise RuntimeError(f"blockMeshDict block cells {off} != mesh cells {ncell}")
    return b


def angles(P, F, own, nei, ncell):
    Cc, Cf, Sf, V = wn.cell_centres(P, F, own, nei, ncell)
    ni = len(nei)
    d = Cc[nei] - Cc[own[:ni]]
    S = Sf[:ni]
    dn = np.linalg.norm(d, axis=1)
    Sn = np.linalg.norm(S, axis=1)
    ok = (dn > 1e-300) & (Sn > 1e-300)
    cosa = np.ones(ni)
    cosa[ok] = np.einsum('ij,ij->i', d[ok], S[ok]) / (dn[ok] * Sn[ok])
    return np.degrees(np.arccos(np.clip(cosa, -1.0, 1.0))), Cc, Cf, Sf, V, d


def main(case, ntop):
    P, F, own, nei, ncell = wn.load(case)
    ang, Cc, Cf, Sf, V, d = angles(P, F, own, nei, ncell)
    mine = float(np.nanmax(ang))
    ref = float(re.search(r"Mesh non-orthogonality Max:\s*(\S+)",
                          open(os.path.join(case, "log.checkMesh")).read()).group(1))
    print(f"{case}")
    print(f"  cells {ncell}  faces {len(F)}  internal {len(nei)}")
    print(f"  CONTROL (a) AGREEMENT: recomputed {mine:.4f} vs checkMesh {ref:.4f}"
          f"  |diff| {abs(mine - ref):.5f} deg")
    if abs(mine - ref) >= 0.05:
        print("  REFUSED: reader does not reproduce checkMesh.  No result printed.")
        sys.exit(2)
    k = int(np.nanargmax(ang))
    P2 = P.copy()
    P2[F[k][0]] += np.array([0.0, 1.234e-04, 0.0])
    ang2 = angles(P2, F, own, nei, ncell)[0]
    if not abs(ang2[k] - ang[k]) > 1e-6:
        print("  REFUSED: displacing a point of the winning face did not move its angle.")
        sys.exit(2)
    print(f"  CONTROL (b) DISPLACEMENT: {ang[k]:.6f} -> {ang2[k]:.6f} deg.  PLANT SEEN.")

    ns = block_index(case)
    order = np.argsort(ang)[::-1][:ntop]
    for r, fi in enumerate(order):
        fi = int(fi)
        n = Sf[fi] / np.linalg.norm(Sf[fi])
        dv = d[fi]
        dm = np.linalg.norm(dv)
        dnorm = float(dv @ n)
        dtangv = dv - dnorm * n
        dtang = float(np.linalg.norm(dtangv))
        print(f"\n  [{r}] face {fi}  angle {ang[fi]:.4f} deg   area {np.linalg.norm(Sf[fi]):.6e}")
        print(f"      owner  {own[fi]:8d}  {addr(int(own[fi]), ns)}")
        print(f"      neigh  {nei[fi]:8d}  {addr(int(nei[fi]), ns)}")
        print(f"      face pts:")
        for q in F[fi]:
            print(f"        ({P[q][0]:12.6f} {P[q][1]:12.6f} {P[q][2]:12.6f})")
        print(f"      face centroid  ({Cf[fi][0]:.6f} {Cf[fi][1]:.6f} {Cf[fi][2]:.6f})")
        print(f"      unit normal    ({n[0]:.6f} {n[1]:.6f} {n[2]:.6f})")
        print(f"      owner  centre  ({Cc[own[fi]][0]:.6f} {Cc[own[fi]][1]:.6f} {Cc[own[fi]][2]:.6f})"
              f"   vol {V[own[fi]]:.6e}")
        print(f"      neigh  centre  ({Cc[nei[fi]][0]:.6f} {Cc[nei[fi]][1]:.6f} {Cc[nei[fi]][2]:.6f})"
              f"   vol {V[nei[fi]]:.6e}")
        print(f"      d = neigh-owner ({dv[0]:.6e} {dv[1]:.6e} {dv[2]:.6e})  |d| {dm:.6e}")
        print(f"      d.n (through-face) {dnorm:.6e}   |d_tangential| {dtang:.6e}"
              f"   ratio t/n {dtang / abs(dnorm) if dnorm else float('nan'):.4f}"
              f"   atan(t/n) {np.degrees(np.arctan2(dtang, abs(dnorm))):.4f} deg")
        print(f"      d_tangential   ({dtangv[0]:.6e} {dtangv[1]:.6e} {dtangv[2]:.6e})")

    # --- PER-BLOCK CENSUS.  Which blocks would have to change for the maximum to
    # move?  A face is attributed to the pair of blocks it separates.  The
    # "excluding" line is the free equivalent of deleting those blocks and
    # re-meshing: it is the maximum this topology could reach if every face
    # touching them were repaired perfectly.
    if ns is not None:
        cb = cell_block(ncell, ns)
        ni_ = len(nei)
        bo, bn = cb[own[:ni_]], cb[nei]
        print("\n  PER-BLOCK-PAIR MAXIMUM (deg), pairs above 70:")
        seen = {}
        for a, b, v in zip(bo, bn, ang):
            k2 = (int(min(a, b)), int(max(a, b)))
            if v > seen.get(k2, -1):
                seen[k2] = float(v)
        for k2, v in sorted(seen.items(), key=lambda kv: -kv[1])[:12]:
            print(f"      blk{k2[0]:02d}|blk{k2[1]:02d}  {v:8.4f}")
        # the tip fill is ALWAYS the last 8 blocks emitted, in every topology variant --
        # derived from the dict, never hard-coded to one variant's numbering.
        FILLB = set(range(len(ns) - 8, len(ns)))
        m_nofill = np.array([not (int(a) in FILLB or int(b) in FILLB)
                             for a, b in zip(bo, bn)])
        print(f"      MAX EXCLUDING every face touching blk16-23 (the tip fill):"
              f" {float(ang[m_nofill].max()):.4f} deg")
        WRAPOUT = set()

    for t in (70.0, 80.0, 85.0, 89.0):
        print(f"\n  faces above {t:5.1f} deg: {int((ang > t).sum())}")
    sel = ang > 70.0
    if sel.any():
        blocks = {}
        for fi in np.nonzero(sel)[0]:
            key = addr(int(own[fi]), ns).split("[")[0]
            blocks[key] = blocks.get(key, 0) + 1
        print("  >70 deg by OWNER block: " + ", ".join(
            f"{a}:{b}" for a, b in sorted(blocks.items(), key=lambda kv: -kv[1])))


def _o_flag_control():
    """Drive BOTH import-provenance refusals under `python3 -O` and require refusal.

    An `assert`-based guard passes every normal-mode test and is DELETED by -O,
    leaving no trace: the import simply proceeds with the wrong module.  Only
    running the interpreter WITH the flag can see it.  Every probe drives a
    SACRIFICIAL COPY of this module in a temp tree, so a fully stripped guard
    cannot make the real study directory produce a number.
    """
    import shutil
    import subprocess
    import tempfile

    tmp = tempfile.mkdtemp(prefix="ofg_oflag_")
    try:
        src = io_open_read(os.path.abspath(__file__))
        pristine = os.path.join(tmp, "pristine_ofg.py")
        with open(pristine, "w", encoding="utf-8") as fh:
            fh.write(src)

        # variant A: WN_DIR repointed at a directory that has no worst_nonortho.py
        nowhere = os.path.join(tmp, "nowhere")
        os.makedirs(nowhere, exist_ok=True)
        anchor = 'WN_DIR = "%s"' % WN_DIR
        if src.count(anchor) != 1:
            print("  REFUSED: -O control anchor not unique; cannot build the mutant.")
            sys.exit(2)
        bad = os.path.join(tmp, "badpath_ofg.py")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write(src.replace(anchor, 'WN_DIR = "%s"' % nowhere, 1))

        # variant B: a DECOY worst_nonortho pre-seeded in sys.modules from another
        # directory -- the exact stale-cache case the identity check exists for.
        decoy = os.path.join(tmp, "decoy")
        os.makedirs(decoy, exist_ok=True)
        with open(os.path.join(decoy, "worst_nonortho.py"), "w", encoding="utf-8") as fh:
            fh.write("# decoy: NOT the reader carrying the planted controls\n")
        driver = os.path.join(tmp, "drive_decoy.py")
        with open(driver, "w", encoding="utf-8") as fh:
            fh.write(
                "import sys\n"
                "sys.path.insert(0, %r)\n" % decoy
                + "import worst_nonortho  # noqa: F401  -- poisons sys.modules\n"
                "sys.path.insert(0, %r)\n" % tmp
                + "import pristine_ofg  # noqa: F401\n")

        probes = [
            ("A: WN_DIR missing the reader, under -O", [sys.executable, "-O", bad], 2),
            ("A: same, normal mode", [sys.executable, bad], 2),
            ("B: decoy module in sys.modules, under -O", [sys.executable, "-O", driver], 2),
            ("positive: pristine imports under -O",
             [sys.executable, "-O", "-c",
              "import sys; sys.path.insert(0, %r); import pristine_ofg" % tmp], 0),
        ]
        ok = True
        for label, cmd, want in probes:
            env = dict(os.environ)
            env.pop("PYTHONOPTIMIZE", None)
            r = subprocess.run(cmd, capture_output=True, cwd=tmp, env=env)
            good = r.returncode == want
            ok = ok and good
            print("  %s %-40s want rc=%d  got rc=%d"
                  % ("ok  " if good else "FAIL", label, want, r.returncode))
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def io_open_read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


if __name__ == "__main__":
    if "--o-control" in sys.argv:
        print("INTERPRETER-FLAG CONTROL -- the import-provenance refusals must")
        print("survive `python3 -O`. (`assert` is REMOVED by -O; a guard that")
        print("vanishes under a flag is not a guard.)")
        sys.exit(0 if _o_flag_control() else 3)
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
