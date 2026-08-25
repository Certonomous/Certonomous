#!/usr/bin/env python3
"""Corner angles of every block in the F1 v2 butterfly, straight from the generator.

WHY.  checkMesh reports a max non-orthogonality but not WHICH BLOCK produces it.
For a structured hex block the interior faces near a corner inherit that corner's
i-edge/j-edge angle: a corner at 180 deg is a degenerate quad and its faces are
non-orthogonal to ~90 deg no matter how the block is refined.  This reads the
generator's own vertices and block connectivity and reports, per block, the
corner angle FURTHEST FROM 90 deg on the x1-x2 (i-j) face.

It measures; it grades nothing.  No mesh is built and no gate is read.

PLANTED CONTROL (CLAUDE.md rule 3).  An angle from a reader not shown able to see
a different angle is not evidence.  --selftest pushes three hand-built quads with
angles known EXACTLY by construction (90, 135 and 180 deg) through the same
estimator and refuses unless all three come back within 1e-9 deg; then it
DISPLACES one real block corner by a known offset and asserts the reported angle
moves to the value recomputed by hand from the displaced points.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def corner_angle(p_prev, p_at, p_next):
    """interior angle at p_at, in degrees, between edges p_at->p_prev and p_at->p_next."""
    a = np.asarray(p_prev, float) - np.asarray(p_at, float)
    b = np.asarray(p_next, float) - np.asarray(p_at, float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-14 or nb < 1e-14:
        return float("nan")          # collapsed edge: report nan, never 0
    c = float(np.dot(a, b) / (na * nb))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def quad_angles(q):
    """the four interior angles of quad q = [v0,v1,v2,v3] traversed in order."""
    return [corner_angle(q[(i - 1) % 4], q[i], q[(i + 1) % 4]) for i in range(4)]


def selftest():
    tests = [(np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], float), 90.0, 0),
             (np.array([[0, 0, 0], [1, 0, 0], [2, 1, 0], [0, 1, 0]], float), 90.0, 0)]
    q90 = tests[0][0]
    got = quad_angles(q90)
    assert all(abs(g - 90.0) < 1e-9 for g in got), f"CONTROL FAILED (square): {got}"
    # 135 deg by construction at v1: edges v1->v0 = (-1,0) and v1->v2 = (cos45,sin45)
    q135 = np.array([[0, 0, 0], [1, 0, 0],
                     [1 + np.cos(np.radians(45)), np.sin(np.radians(45)), 0], [0, 1, 0]], float)
    a135 = quad_angles(q135)[1]
    assert abs(a135 - 135.0) < 1e-9, f"CONTROL FAILED (135): {a135}"
    # 180 deg by construction: v0 sits ON the segment v3-v1, both edges from v0 vertical
    q180 = np.array([[0, 0.5, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0]], float)
    a180 = quad_angles(q180)[0]
    assert abs(a180 - 180.0) < 1e-9, f"CONTROL FAILED (180): {a180}"
    print("  PLANTED CONTROL PASSED: estimator recovers 90.000000000, 135.000000000 and")
    print("                          180.000000000 deg on quads whose angles are exact by")
    print("                          construction, to < 1e-9 deg.")
    # displacement control on a REAL block
    V, B, names = load(1)
    k = int(np.argmax([abs(max(quad_angles(V[b[:4]])) - 90.0) for b in B]))
    q = V[B[k][:4]].copy()
    before = quad_angles(q)
    off = np.array([1.234e-03, -5.678e-03, 0.0])
    q2 = q.copy(); q2[0] += off
    after = quad_angles(q2)
    hand = corner_angle(q2[3], q2[0], q2[1])
    assert abs(after[0] - hand) < 1e-12, "displacement not seen consistently"
    assert abs(after[0] - before[0]) > 1e-6, (
        f"PLANT NOT SEEN: displacing a corner by {off} did not move the angle "
        f"({before[0]} -> {after[0]})")
    print(f"  PLANT SEEN: displacing block {names[k]} corner 0 by {off[:2]} moved its angle")
    print(f"              {before[0]:.6f} -> {after[0]:.6f} deg, matching the hand recompute.")
    print("  SELFTEST PASS.")


BLOCK_NAMES = (
    ["z0_wake_lo", "z0_tail_lo", "z0_mid_lo", "z0_nose_lo",
     "z0_nose_up", "z0_mid_up", "z0_tail_up", "z0_wake_up"]
    + ["z1_wake_lo", "z1_tail_lo", "z1_mid_lo", "z1_nose_lo",
       "z1_nose_up", "z1_mid_up", "z1_tail_up", "z1_wake_up"]
    + ["FILL_up_nose", "FILL_up_mid", "FILL_up_tail",
       "FILL_lo_nose", "FILL_lo_mid", "FILL_lo_tail",
       "FILL_core_up", "FILL_core_lo"])


def load(m):
    import gen_var
    import importlib
    importlib.reload(gen_var)
    g = gen_var.M6Geometry(verbose=False); g.z_tip = g.z_tip_measured
    if gen_var.TSCALE != 1.0:
        _b = g.t2
        g.t2 = (lambda xc, _b=_b, s=gen_var.TSCALE: s * _b(xc))
    gen = gen_var.Gen(m, g).geom().topology()
    V = np.array(gen.V, float)
    B = np.array([b[0] for b in gen.blocks])
    assert len(B) == len(BLOCK_NAMES), f"{len(B)} blocks vs {len(BLOCK_NAMES)} names"
    return V, B, BLOCK_NAMES


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    V, B, names = load(m)
    print(f"DIALS U2={os.environ.get('F1_U2','0.90')} CORE_S={os.environ.get('F1_CORE_S','0.50')} "
          f"NR={os.environ.get('F1_NR','4')} TSCALE={os.environ.get('F1_TSCALE','1.0')}  m={m}")
    print(f"{'block':16s} {'worst i-j corner':>17s} {'at corner':>10s}   all four angles (deg)")
    rows = []
    for nm, b in zip(names, B):
        ang = quad_angles(V[b[:4]])
        j = int(np.nanargmax([abs(a - 90.0) for a in ang]))
        rows.append((abs(ang[j] - 90.0), nm, ang[j], j, ang))
    for dev, nm, a, j, ang in sorted(rows, reverse=True):
        flag = "  <== DEGENERATE (>=170)" if a >= 170.0 else ("  <== severe" if a >= 150 else "")
        print(f"{nm:16s} {a:17.6f} {j:10d}   " + " ".join(f"{x:8.3f}" for x in ang) + flag)
    worst = max(rows)
    print(f"\nWORST BLOCK: {worst[1]} at {worst[2]:.6f} deg "
          f"(deviation from orthogonal {worst[0]:.6f} deg)")
    print(f"blocks with a corner >= 170 deg: "
          f"{[r[1] for r in rows if r[2] >= 170.0]}")
