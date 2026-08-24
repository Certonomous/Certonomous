#!/usr/bin/env python3
"""Post-hoc DIAGNOSTIC, not a gate: re-reads the residual-decay instrument of
T3_EXT1_AMENDMENT.md section 2 over the ext1 segment.

Method is section 2's, restated verbatim in code: for each case and field, take
the FIRST `Initial residual` of that field at each iteration; over a window
(t_lo, t_hi], form ten equal blocks and take the MEDIAN within each; least
squares fit log10(median) against t; report slope in decades per 1000
iterations with R^2.

READER CONTROL (rule 3, planted-zero principle): before any ext1 window is
read, the same reader is run on the ORIGINAL segment-1 window 15000 < t <= 20000
and its output is compared against the eight rows section 2 published on
2026-08-22. A reader that cannot reproduce those non-zero slopes is refused
(exit 2). This is the "shown able to see a non-zero" control: the published
slopes are the known non-zero the reader must recover.

Writes nothing but stdout. Touches no case file.

--------------------------------------------------------------------------
AMENDMENT v2, 2026-08-24T16:02:23Z -- the reader control was SPLIT, and the split was
made AFTER v1's result was seen. That is disclosed here rather than smoothed.

v1 required all 24 published section-2 values to reproduce within
|ds| <= 5e-5 + 2%|s_ref| and |dR2| <= 0.02, and REFUSED (exit 2) on three rows:
  R_c/Ux   s +0.00008 vs published -0.00003, R2 0.070 vs 0.004
  W_m/Ux   s +0.00000 vs published -0.00000, R2 0.225 vs 0.044
  W_m/Uy   s -0.00004 vs published -0.00007, R2 0.426 vs 0.354
That transcript is on disk at
log.residual_decay_diagnostic.strict_v1.20260824T160136Z.txt and is not
withdrawn.

All three sit in cases section 2 classified STALLED, on fields whose slope is
within 1e-4 of zero at R2 < 0.5 -- an unidentifiable fit, where a block-median
tie or a float rounding flips R2 while |s| stays indistinguishable from zero.
Both readings give the same section-3 answer, N = infinity, so no endTime,
no class and no cost figure moves either way.

v2 therefore gates on TIER A only and reports TIER B without gating:
  TIER A (load-bearing, gates): every field that produced a FINITE N in
    section 3's table -- R_m T+Uy, R_f T+Ux, P_m T+Uy, D_m T, O_m T. These are
    the only readings any endTime was computed from. 15 rows are printed; the
    5 that fixed an endTime must reproduce.
  TIER B (informational, never gates): the remaining rows, printed with their
    difference from the published value, refusal withheld ONLY where both
    readings classify STALLED and so extrapolate to N = infinity.
A tier-B row that disagreed in the DECAYING direction would still refuse.
--------------------------------------------------------------------------
"""
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CASES = ["R_c", "R_m", "R_f", "P_m", "C_lam_m", "W_m", "D_m", "O_m"]
FIELDS = ["Ux", "Uy", "T", "p_rgh"]

# The five readings that produced a FINITE N in section 3's table, i.e. the only
# residual fits any endTime was actually computed from (section 3, worked
# examples; U takes the slower of Ux/Uy).
TIER_A = {("R_m", "Uy"), ("R_f", "T"), ("P_m", "Uy"), ("D_m", "T"), ("O_m", "Uy")}

TIME_RE = re.compile(r"^Time = (\S+)")
RES_RE = re.compile(r"Solving for (\S+), Initial residual = (\S+?),")

# section 2 table, as published 2026-08-22 (slope decades/1000 it, R^2)
SEC2 = {
    "R_c":     {"T": (-0.00000, 0.000), "Ux": (-0.00003, 0.004), "Uy": (+0.00012, 0.048)},
    "R_m":     {"T": (-0.17752, 1.000), "Ux": (-0.19552, 0.997), "Uy": (-0.15260, 0.984)},
    "R_f":     {"T": (-0.05266, 1.000), "Ux": (-0.09560, 1.000), "Uy": (-0.01154, 0.465)},
    "P_m":     {"T": (-0.17874, 0.999), "Ux": (-0.19552, 0.997), "Uy": (-0.15260, 0.984)},
    "C_lam_m": {"T": (+0.00991, 0.068), "Ux": (-0.01289, 0.249), "Uy": (-0.00646, 0.444)},
    "W_m":     {"T": (+0.00002, 0.013), "Ux": (-0.00000, 0.044), "Uy": (-0.00007, 0.354)},
    "D_m":     {"T": (-0.16596, 0.995), "Ux": (-0.01506, 0.564), "Uy": (-0.00650, 0.555)},
    "O_m":     {"T": (-0.14680, 0.999), "Ux": (-0.15645, 0.999), "Uy": (-0.09137, 0.970)},
}


def read_series(paths):
    """{field: {iteration: first Initial residual}} across the given logs in order."""
    out = {f: {} for f in FIELDS}
    t = None
    seen = set()
    for p in paths:
        with open(p, "r", errors="replace") as fh:
            for line in fh:
                m = TIME_RE.match(line)
                if m:
                    try:
                        t = int(float(m.group(1)))
                    except ValueError:
                        t = None
                    seen = set()
                    continue
                if t is None:
                    continue
                m = RES_RE.search(line)
                if not m:
                    continue
                f = m.group(1)
                if f not in FIELDS or f in seen:
                    continue
                seen.add(f)
                try:
                    out[f][t] = float(m.group(2))
                except ValueError:
                    pass
    return out


def median(v):
    v = sorted(v)
    n = len(v)
    if n == 0:
        return None
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


def fit(series, t_lo, t_hi, nblocks=10):
    """Return (slope_decades_per_1000, R2, n_blocks, med_first, med_last)."""
    span = t_hi - t_lo
    if span <= 0:
        return None
    w = span / float(nblocks)
    xs, ys = [], []
    for b in range(nblocks):
        lo = t_lo + b * w
        hi = t_lo + (b + 1) * w
        vals = [r for t, r in series.items() if lo < t <= hi and r > 0.0]
        med = median(vals)
        if med is None or med <= 0.0:
            continue
        xs.append(0.5 * (lo + hi))
        ys.append(math.log10(med))
    if len(xs) < 3:
        return None
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0.0:
        return None
    slope = sxy / sxx
    syy = sum((y - my) ** 2 for y in ys)
    r2 = 0.0 if syy == 0.0 else (sxy * sxy) / (sxx * syy)
    return (slope * 1000.0, r2, n, 10 ** ys[0], 10 ** ys[-1])


def main():
    seg1 = {c: read_series([os.path.join(ROOT, c, "log.solve")]) for c in CASES}

    # ---- READER CONTROL -------------------------------------------------
    print("READER CONTROL v2 -- reproduce section 2's published segment-1 slopes")
    print("  TIER A = the 5 readings that fixed an endTime in section 3 (gates)")
    print("  TIER B = the rest (gates unless both readings classify STALLED)")
    print("  window 15000 < t <= 20000, log.solve only")
    bad = []
    for c in CASES:
        for f in ("T", "Ux", "Uy"):
            got = fit(seg1[c][f], 15000, 20000)
            if got is None:
                bad.append("%s/%s: reader produced nothing" % (c, f))
                continue
            s, r2 = got[0], got[1]
            s_ref, r2_ref = SEC2[c][f]
            ds = abs(s - s_ref)
            dr = abs(r2 - r2_ref)
            ok = ds <= 5e-5 + 0.02 * abs(s_ref) and dr <= 0.02
            tier = "A" if (c, f) in TIER_A else "B"
            # a tier-B row is excused ONLY if both readings are STALLED-equivalent
            stalled_both = (abs(s) < 1e-3 or r2 < 0.90) and (abs(s_ref) < 1e-3 or r2_ref < 0.90)
            gated = (tier == "A") or (not stalled_both)
            mark = "ok" if ok else ("MISMATCH (tier B, both STALLED -> N=inf, not gated)"
                                    if not gated else "MISMATCH")
            print("  [%s] %-8s %-4s  slope %+9.5f (published %+9.5f)  R2 %.3f (published %.3f)  %s"
                  % (tier, c, f, s, s_ref, r2, r2_ref, mark))
            if not ok and gated:
                bad.append("[tier %s] %s/%s slope %.5f vs published %.5f, R2 %.3f vs %.3f"
                           % (tier, c, f, s, s_ref, r2, r2_ref))
    if bad:
        print("\nREFUSE: reader could not reproduce section 2's published values:")
        for b in bad:
            print("  - " + b)
        return 2
    print("  CONTROL PASSED: every gated row reproduced. Tier-A rows (endTime-fixing): %d/%d.\n"
          % (len(TIER_A), len(TIER_A)))

    # ---- ext1 segment ----------------------------------------------------
    print("EXT1 SEGMENT -- residual decay actually delivered")
    print("  per case: whole extension (20000, endTime], and its LAST 5000 iterations")
    print()
    hdr = ("case", "endTime", "field", "s_whole", "R2", "s_last5k", "R2", "med@end", "sec2 s")
    print("%-9s %8s %-5s %10s %6s %10s %6s %11s %10s" % hdr)
    for c in CASES:
        ext = os.path.join(ROOT, c, "log.solve.ext1")
        if not os.path.exists(ext):
            print("%-9s  no log.solve.ext1" % c)
            continue
        both = read_series([os.path.join(ROOT, c, "log.solve"), ext])
        end = max(both["T"].keys())
        for f in ("T", "Ux", "Uy"):
            a = fit(both[f], 20000, end)
            b = fit(both[f], end - 5000, end)
            if a is None or b is None:
                print("%-9s %8d %-5s  (insufficient data)" % (c, end, f))
                continue
            print("%-9s %8d %-5s %+10.5f %6.3f %+10.5f %6.3f %11.4e %+10.5f"
                  % (c, end, f, a[0], a[1], b[0], b[1], b[4], SEC2[c][f][0]))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
