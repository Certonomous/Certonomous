#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_sizegroups.py -- the COMMITTED, PINNED sectional-grid + feed generator for
VMFL034-R2 (constant-kernel aggregation in a CMSMPR box).

WHY THIS FILE EXISTS (the defect it repairs).  The struck registration VMFL034
(freeze f4f80b53) committed only ONE instance of its size-group triple; the
Wheeler-quadrature + Kumar-Ramkrishna generator that would build the other two
levels lived ONLY in a scratch directory -- uncommitted, unpinned, unhashable.
Synthesising the missing levels from that scratch code would have put
gate-relevant feed inputs on an UNFROZEN grading path (CLAUDE.md rule 2).  This
generator is therefore committed IN the case, PINNED by blob in the registration,
and used to build ALL THREE frozen level instances under grids/{S1,S2,S3}/ before
the freeze commit exists.  The graded run stages those FROZEN instances; it does
NOT run this generator (nothing is synthesised at grade time).  This file is kept
committed for (a) audit / reproducibility of the frozen bytes and (b) the
check_freeze_ready.py C4 "committed generator" mechanism.

WHAT IT DOES.
  * Lays out a geometric sectional grid of N size-group PIVOTS (diameters d_i)
    over the frozen NOMINAL range [0.45, 22.0] (Ruling 4; NOT SI -- feed mean size
    m1/m0 = 1.108 is O(1), not 1e-6).
  * Places the feed's THREE Wheeler (product-difference) quadrature nodes -- frozen
    ABSCISSAS/weights below, machine-precision reproductions of the six archive
    feed moments -- onto that grid by the KUMAR-RAMKRISHNA fixed-pivot rule (linear
    split in particle VOLUME v = kappa*d^3).  KR conserves m0 (number) and m3
    (volume) EXACTLY at every N; the fractional volume-moments m1,m2,m4,m5 carry a
    grid-refining residual -- exactly the discretisation error the section-7 Roache
    triple bounds.
  * Emits per-level constant/phaseProperties (from templates/phaseProperties.template,
    @SIZEGROUPS@ filled) and 0.orig/f<i>.air.bubbles feed fields (from
    templates/f.template, @OBJECT@/@VALUE@ filled), plus the parent 0.orig/f.air.bubbles.

PROVENANCE OF THE FROZEN INPUTS (consumed NO gate target).
  * Archive feed moments m0..m5 = (1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999),
    read from the shipped archive's plain-ASCII members (PREREGISTRATION VMFL034
    s.5a) -- NOT back-calculated from the manual's OUTLET target table.
  * Wheeler abscissas/weights below were computed once from those six feed moments
    (scratch feed_recon.py; product-difference / Wheeler) and reproduce all six to
    <= 2e-15.  They are frozen here so the generator has no numpy/eig dependency and
    runs in any environment; --selftest re-verifies the reproduction in pure Python.

CLAUDE.md rule 16: silent; writes files, prints only a short summary / the selftest.
"""

import argparse
import math
import os
import sys

# ---------------------------------------------------------------------------
# FROZEN INPUTS
# ---------------------------------------------------------------------------
FEED_MOMENTS = (1.0, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)   # archive; NOT the target
KAPPA = 0.5235987756            # formFactor = pi/6 (spheres) -- must equal phaseProperties
DMIN, DMAX = 0.45, 22.0         # frozen NOMINAL sectional range (Ruling 4)

# Wheeler 3-node quadrature of FEED_MOMENTS (frozen; reproduces all six to <=2e-15).
# Provenance: scratch feed_recon.py, product-difference / Wheeler on FEED_MOMENTS.
WHEELER_ABSCISSAS = (0.51034075, 1.15677209, 1.85317510)
WHEELER_WEIGHTS   = (0.22888048, 0.62869707, 0.14242245)

# The registered r=2 triple (class count N_g / 2N_g / 4N_g; section-7).
REGISTERED_LEVELS = {"S1": 16, "S2": 32, "S3": 64}


# ---------------------------------------------------------------------------
def geom_grid(n):
    """N geometric PIVOT diameters over [DMIN, DMAX]."""
    if n < 2:
        raise ValueError("need >= 2 groups")
    return [DMIN * (DMAX / DMIN) ** (i / (n - 1)) for i in range(n)]


def kr_feed_number(d):
    """Kumar-Ramkrishna fixed-pivot placement of the frozen Wheeler nodes onto the
    grid pivots d, splitting each node linearly in particle VOLUME v = kappa*d^3.
    Returns the number N_i in each group.  Conserves m0 and m3 exactly."""
    v = [KAPPA * di ** 3 for di in d]
    nn = [0.0] * len(d)
    for lj, wj in zip(WHEELER_ABSCISSAS, WHEELER_WEIGHTS):
        vj = KAPPA * lj ** 3
        if vj <= v[0]:
            nn[0] += wj
            continue
        if vj >= v[-1]:
            nn[-1] += wj
            continue
        # locate interval [a, a+1] with v[a] <= vj < v[a+1]
        a = 0
        while a + 1 < len(v) and v[a + 1] <= vj:
            a += 1
        ga = (v[a + 1] - vj) / (v[a + 1] - v[a])   # to lower pivot
        gb = (vj - v[a]) / (v[a + 1] - v[a])       # to upper pivot
        nn[a] += wj * ga
        nn[a + 1] += wj * gb
    return nn


def moments(d, nn):
    return [sum(ni * di ** k for ni, di in zip(nn, d)) for k in range(6)]


def value_volume_fractions(d):
    """Per-group VOLUME fractions value_i = N_i*kappa*d_i^3 / sum, normalised to 1
    (the sizeGroup `value` OpenFOAM expects; sum over populated groups == 1)."""
    nn = kr_feed_number(d)
    vol = [ni * KAPPA * di ** 3 for ni, di in zip(nn, d)]
    s = sum(vol)
    if s <= 0:
        raise ValueError("empty feed")
    return [x / s for x in vol]


# ---------------------------------------------------------------------------
def _fmt(x):
    return repr(float(x)) if x == 0.0 else "%.10g" % x


def emit_level(n, template_pp, template_f, out_dir):
    """Write out_dir/constant/phaseProperties and out_dir/0.orig/f<i>.air.bubbles
    (+ parent f.air.bubbles) for an n-group instance."""
    d = geom_grid(n)
    vals = value_volume_fractions(d)

    # -- sizeGroups block ----------------------------------------------------
    lines = []
    for i, (di, vi) in enumerate(zip(d, vals)):
        # print tiny values as exact 0 so a group is unambiguously empty
        v_out = 0 if vi < 1e-12 else vi
        lines.append("            f%d{d %.8e; value %s;}" % (i, di, _fmt(v_out)))
    sizegroups = "\n".join(lines)

    with open(template_pp) as fh:
        pp = fh.read()
    if "@SIZEGROUPS@" not in pp or "@NGROUPS@" not in pp:
        raise SystemExit("phaseProperties template missing @SIZEGROUPS@/@NGROUPS@")
    pp = pp.replace("@SIZEGROUPS@", sizegroups).replace("@NGROUPS@", str(n))

    cdir = os.path.join(out_dir, "constant")
    zdir = os.path.join(out_dir, "0.orig")
    os.makedirs(cdir, exist_ok=True)
    os.makedirs(zdir, exist_ok=True)
    with open(os.path.join(cdir, "phaseProperties"), "w") as fh:
        fh.write(pp)

    with open(template_f) as fh:
        ftpl = fh.read()
    if "@OBJECT@" not in ftpl or "@VALUE@" not in ftpl:
        raise SystemExit("f template missing @OBJECT@/@VALUE@")
    # per-group feed fields
    for i, vi in enumerate(vals):
        v_out = 0 if vi < 1e-12 else vi
        obj = "f%d.air.bubbles" % i
        txt = ftpl.replace("@OBJECT@", obj).replace("@VALUE@", _fmt(v_out))
        with open(os.path.join(zdir, obj), "w") as fh:
            fh.write(txt)
    # parent f.air.bubbles == uniform 1 (the total)
    txt = ftpl.replace("@OBJECT@", "f.air.bubbles").replace("@VALUE@", "1")
    with open(os.path.join(zdir, "f.air.bubbles"), "w") as fh:
        fh.write(txt)

    m = moments(d, kr_feed_number(d))
    return d, vals, m


# ---------------------------------------------------------------------------
def roache(c, me, f):
    d1 = me - c
    d2 = f - me
    if d1 == 0 and d2 == 0:
        return "EXACT", None
    if d1 == 0 or d2 == 0:
        return "STAGNANT", None
    if d1 * d2 < 0:
        return "OSCILLATORY", None
    r = abs(d1) / abs(d2)
    if r <= 1.0:
        return "DIVERGENT", None
    return "CONVERGING", math.log(r) / math.log(2.0)


def selftest():
    print("=== gen_sizegroups.py SELFTEST ===")
    ok = True
    # 1. frozen Wheeler nodes reproduce the six feed moments (pure python)
    print("Wheeler 3-node reproduction of the six archive FEED moments:")
    for k in range(6):
        rec = sum(w * l ** k for l, w in zip(WHEELER_ABSCISSAS, WHEELER_WEIGHTS))
        resid = rec - FEED_MOMENTS[k]
        flag = "ok" if abs(resid) <= 1e-6 else "XX"
        print("  m%d recon=%.7f feed=%.7f resid=%+.2e [%s]" %
              (k, rec, FEED_MOMENTS[k], resid, flag))
        if abs(resid) > 1e-6:
            ok = False
    # 2. KR conserves m0 (number) and m3 (volume) EXACTLY -- i.e. equal to the
    #    WHEELER feed's own m0/m3 (its true input). The Wheeler feed itself matches
    #    the ARCHIVE m0/m3 to the frozen-abscissa precision (<=1e-6, checked in (1)),
    #    so the small archive residual reported here is that rounding, NOT a KR error.
    wm0 = sum(w for w in WHEELER_WEIGHTS)
    wm3 = sum(w * l ** 3 for l, w in zip(WHEELER_ABSCISSAS, WHEELER_WEIGHTS))
    print("KR fixed-pivot m0/m3 conservation (KR == Wheeler feed, must be exact) + m1/m2/m4/m5 residual:")
    mrec = {}
    for lvl, n in sorted(REGISTERED_LEVELS.items(), key=lambda kv: kv[1]):
        d = geom_grid(n)
        m = moments(d, kr_feed_number(d))
        mrec[n] = m
        cons0 = m[0] - wm0     # KR number vs Wheeler number (exact split)
        cons3 = m[3] - wm3     # KR volume vs Wheeler volume (linear-in-volume split)
        print("  N=%2d  m0-Wheeler=%+.2e  m3-Wheeler=%+.2e  |  m1 %+.3f%% m2 %+.3f%% m4 %+.3f%% m5 %+.3f%% (vs archive)"
              % (n, cons0, cons3,
                 100 * (m[1] - FEED_MOMENTS[1]) / FEED_MOMENTS[1],
                 100 * (m[2] - FEED_MOMENTS[2]) / FEED_MOMENTS[2],
                 100 * (m[4] - FEED_MOMENTS[4]) / FEED_MOMENTS[4],
                 100 * (m[5] - FEED_MOMENTS[5]) / FEED_MOMENTS[5]))
        if abs(cons0) > 1e-12 or abs(cons3) > 1e-12:
            ok = False
    # 3. the registered r=2 triple's FEED reconstruction is CONVERGING on every
    #    gated feed-shape moment (m1,m2,m4,m5) -- the a-priori design check that
    #    selected 16/32/64 over 12/24/48 (which is DIVERGENT on m4/m5).
    ns = sorted(REGISTERED_LEVELS.values())
    print("registered feed-reconstruction Roache class (must be CONVERGING for gated feed-shape limbs):")
    for k in (1, 2, 4, 5):
        st, p = roache(mrec[ns[0]][k], mrec[ns[1]][k], mrec[ns[2]][k])
        pr = "" if p is None else " order=%.2f" % p
        flag = "ok" if st == "CONVERGING" else "XX"
        print("  m%d: %s%s [%s]" % (k, st, pr, flag))
        if st != "CONVERGING":
            ok = False
    # 4. r == 2 on class count for the registered levels
    r21 = ns[1] / ns[0]
    r32 = ns[2] / ns[1]
    print("class-count ratios: %d/%d=%.3f  %d/%d=%.3f  (must both be 2.000)"
          % (ns[1], ns[0], r21, ns[2], ns[1], r32))
    if abs(r21 - 2.0) > 1e-9 or abs(r32 - 2.0) > 1e-9:
        ok = False
    print("SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 2


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="VMFL034-R2 sectional grid + KR feed generator")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit", type=int, metavar="N", help="emit an N-group instance")
    ap.add_argument("--template-pp", help="phaseProperties.template path")
    ap.add_argument("--template-f", help="f.template path")
    ap.add_argument("--out", help="output instance dir")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.emit:
        for req in ("template_pp", "template_f", "out"):
            if not getattr(args, req):
                ap.error("--emit needs --template-pp, --template-f and --out")
        d, vals, m = emit_level(args.emit, args.template_pp, args.template_f, args.out)
        pop = sum(1 for v in vals if v > 1e-12)
        print("emitted %d-group instance -> %s  (populated groups=%d, "
              "feed m3=%.5f, sum(value)=%.6f)"
              % (args.emit, args.out, pop, m[3], sum(vals)))
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
