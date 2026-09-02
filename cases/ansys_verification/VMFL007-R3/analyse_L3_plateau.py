#!/usr/bin/env python3
"""
VMFL007-R3 -- L3 (100x100) PLATEAU DIAGNOSTIC.

Stitches the original 0..30000 leg and the 30000..90000 extension into one series
and answers one question: is the near-axis viscosity swing DECAYING, and if so at
what rate and toward what settling iteration?

THIS SCRIPT IS ON THE RECORD PATH AND OWES GRADING-PATH HYGIENE.  It grades nothing and
issues no verdict -- but its outputs are QUOTED AS LAB FACTS in NUMERICS_KNOWLEDGE N-AV15
and in ANSYS_VERIFICATION_CHARTER sec.16, so "it only diagnoses" buys it no latitude
(verification's sweep, sec.2p.5).  It produces measured numbers, and
computes NO deviation from any reference value -- the only Delta p quantity it
touches is the peak-to-peak of the Delta p series against itself, which is a
flatness measure and contains no reference.

Planted-failure control (rule 3): --plant injects a known spike of a named size at
a named iteration into a COPY of the stitched series and re-runs the SAME window
statistics.  A window statistic that cannot see an injected spike cannot certify a
plateau, so a "it has settled" answer from an unplanted reader is not evidence.

Usage: analyse_L3_plateau.py <legAdir> <legBdir> [--plant ITER:VALUE]
"""

import sys
import os
import glob
import math

# RHO cannot be read from `constant/transportProperties`: an incompressible OpenFOAM case
# stores only the KINEMATIC transport properties, so the density that converts the solver's
# kinematic p (m2/s2) to Pa simply is not in any case file.  It is therefore NAMED here with
# its derivation rather than left as a bare literal in an expression -- the manual gives
# k = 10 Pa.s^n and the case runs k = 0.01 kinematic, so RHO = 10/0.01 = 1000 kg/m3.
# A magic number in a record-path instrument is a number nobody can check.
RHO = 1000.0
_K_MANUAL, _K_KINEMATIC = 10.0, 0.01
assert abs(RHO - _K_MANUAL / _K_KINEMATIC) < 1e-9, "RHO is inconsistent with its own derivation"


def one_or_refuse(paths, what):
    """Return the single matching path, or REFUSE.

    THE DISCRIMINATOR IS GUARDED vs UNGUARDED, NOT WHICH INDEX (verification's sweep,
    VERIFICATION_CHARTER sec.2p.5).  The earlier form took `sorted(paths)[0]` -- a
    LEXICOGRAPHIC sort on numeric time-directory names, where sorted(['0','10000',
    '30000','5000']) is ['0','10000','30000','5000'], so `[0]` is not the earliest and
    `[-1]` is not the latest.  But swapping the index was never the fix: under
    refuse-unless-exactly-one, `[0]`, `[-1]` and an integer-keyed max are ALL IDENTICAL
    and all safe.  Ambiguity is refused, never resolved by a convention the caller
    cannot see.  Exemplar: grade_vmflgpu003.py:364-400.
    """
    if len(paths) != 1:
        # The message says exit 2, so the process MUST exit 2.  `raise SystemExit("...")`
        # prints the string and exits 1 -- a refusal that announces one code and returns
        # another is the "evidence annotated as non-binding" defect, and this line carried
        # it for the length of one planted-failure test.
        sys.stderr.write("REFUSE (exit 2): %s matched %d paths %s -- a restart or a stale "
                         "directory makes this ambiguous; REFUSING rather than guessing "
                         "which is current\n" % (what, len(paths), sorted(paths)))
        raise SystemExit(2)
    return paths[0]


def read_series(path):
    """Read an OpenFOAM functionObject .dat as [(iteration, lastColumnValue)]."""
    out = []
    for ln in open(path):
        if ln.startswith('#'):
            continue
        q = ln.split()
        if len(q) >= 2:
            out.append((int(float(q[0])), float(q[-1])))
    return out


def read_probes(path):
    """Read a probes 'nu' file as (headerLines, [(iteration, [v0,v1,...])])."""
    hdr, rows = [], []
    for ln in open(path):
        if ln.startswith('#'):
            hdr.append(ln.rstrip())
            continue
        q = ln.split()
        if len(q) >= 2:
            rows.append((int(float(q[0])), [float(x) for x in q[1:]]))
    return hdr, rows


def stitch(a, b):
    """Concatenate two legs, dropping any overlap so each iteration appears once."""
    d = {}
    for k, v in a:
        d[k] = v
    for k, v in b:
        d[k] = v          # leg B wins on the shared restart iteration
    return [(k, d[k]) for k in sorted(d)]


def windows(series, w):
    """Peak-to-peak and mean in consecutive windows of w iterations."""
    out = []
    for i in range(0, len(series) - w + 1, w):
        s = [v for _, v in series[i:i + w]]
        it = series[i + w - 1][0]
        m = sum(s) / len(s)
        out.append((it, max(s) - min(s), m))
    return out


def decay_fit(win, first_iter):
    """Least-squares fit of ln(ptp) against iteration over windows past first_iter.

    Returns (slope_per_iter, r2, halflife_iters) or None when the fit is useless.
    """
    pts = [(it, p) for it, p, _ in win if it >= first_iter and p > 0]
    if len(pts) < 4:
        return None
    xs = [float(it) for it, _ in pts]
    ys = [math.log(p) for _, p in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None
    b = sxy / sxx
    a = my - b * mx
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    hl = (math.log(0.5) / b) if b < 0 else float('inf')
    return b, r2, hl, a


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    A, B = sys.argv[1], sys.argv[2]
    plant = None
    for i, x in enumerate(sys.argv):
        if x == '--plant':
            it_s, v_s = sys.argv[i + 1].split(':')
            plant = (int(it_s), float(v_s))

    def leg(d, name):
        return read_series(one_or_refuse(
            glob.glob(os.path.join(d, 'postProcessing', name, '*', '*.dat')),
            "%s/postProcessing/%s" % (d, name))) if glob.glob(
            os.path.join(d, 'postProcessing', name, '*', '*.dat')) else []

    numax = stitch(leg(A, 'nuMaxAll'), leg(B, 'nuMaxAll'))
    pin = stitch(leg(A, 'pInlet'), leg(B, 'pInlet'))
    pout = stitch(leg(A, 'pOutlet'), leg(B, 'pOutlet'))
    din, dout = dict(pin), dict(pout)
    dp = [(k, RHO * (din[k] - dout[k])) for k in sorted(set(din) & set(dout))]

    if plant:
        it, val = plant
        numax = [(k, (val if k == it else v)) for k, v in numax]
        print("PLANT: max(nu) at iteration %d overwritten with %.6g" % (it, val))

    W = 5000
    print("=== stitched series: %d iterations, %d .. %d ==="
          % (len(numax), numax[0][0], numax[-1][0]))
    print()
    print("window (last iter) |   max(nu) ptp |  max(nu) mean |      dp ptp (Pa)")
    wn = windows(numax, W)
    wd = windows(dp, W)
    for (it, p, m), (_, pd, _) in zip(wn, wd):
        print("%18d | %13.6g | %13.6g | %16.6g" % (it, p, m, pd))
    print()

    f = decay_fit(wn, 30000)
    if f:
        b, r2, hl, a = f
        print("ln(ptp) vs iteration, fitted over windows past 30000:")
        print("  slope       = %.4g per iteration   (r2 = %.4f)" % (b, r2))
        if b < 0:
            print("  half-life   = %.0f iterations" % hl)
            for thr in (1e-2, 1e-3):
                target = (math.log(thr) - a) / b
                print("  ptp < %.0e reached at iteration ~ %.0f  [EXTRAPOLATED, not measured]"
                      % (thr, target))
        else:
            print("  slope is NOT negative -> no decay detected over this span.")
    else:
        print("decay fit: not enough windows past 30000.")

    # probes: the pointwise channel
    print()
    for tag, d in (("legB", B),):
        g = glob.glob(os.path.join(d, 'postProcessing', 'nuAxisProbes', '*', 'nu'))
        if not g:
            continue
        hdr, rows = read_probes(one_or_refuse(
            g, "%s/postProcessing/nuAxisProbes" % d))
        for h in hdr:
            if h.startswith('# Probe'):
                print(h)
        npr = len(rows[0][1])
        print("probe | value at 90000 |  ptp last 5000 | ptp last 20000")
        for j in range(npr):
            s5 = [v[j] for _, v in rows[-5000:]]
            s20 = [v[j] for _, v in rows[-20000:]]
            print("%5d | %14.8g | %14.6g | %14.6g"
                  % (j, rows[-1][1][j], max(s5) - min(s5), max(s20) - min(s20)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
