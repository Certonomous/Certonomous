#!/usr/bin/env python3
"""Extract the FIRST-SOLVE residual series from an OpenFOAM solver log.

WHY FIRST-SOLVE ONLY.  `simpleControl::criteriaSatisfied` tests the FIRST solve
of each field in an iteration.  Fields under non-orthogonal correction -- `p`,
typically -- are solved more than once per iteration, and a tail read of the log
returns the LAST corrector, which can be orders of magnitude smaller than the
value the criterion actually reads.  Measured on this box: F2's final-iteration
`p` reads 4.2657e-04 on the first solve and 3.2756e-06 on the last, and the
difference decided whether a run looked converged.  Every other channel is solved
once, so first and last coincide -- which is why the artifact is easy to miss.

Emits CSV: iteration, then one column per field, first solve only.  This is the
first-class artifact records and gates cite; the raw log is gzipped beside it.
"""
import argparse, csv, gzip, re, sys

RE_TIME = re.compile(r'^Time = (\S+)')
RE_SOLVE = re.compile(r'Solving for (\w+), Initial residual = ([0-9.eE+-]+)')


def series(path):
    op = gzip.open if str(path).endswith('.gz') else open
    out, cur, it = [], {}, None
    for line in op(path, 'rt', errors='replace'):
        m = RE_TIME.match(line)
        if m:
            if it is not None:
                out.append((it, cur))
            it, cur = m.group(1), {}
            continue
        m = RE_SOLVE.search(line)
        if m:
            cur.setdefault(m.group(1), float(m.group(2)))   # FIRST solve wins
    if it is not None:
        out.append((it, cur))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('log')
    ap.add_argument('-o', '--out', default='-')
    a = ap.parse_args(argv)
    rows = series(a.log)
    if not rows:
        sys.stderr.write('no iterations found in %s\n' % a.log)
        return 1
    fields = []
    for _, c in rows:
        for k in c:
            if k not in fields:
                fields.append(k)
    fh = sys.stdout if a.out == '-' else open(a.out, 'w', newline='')
    w = csv.writer(fh)
    w.writerow(['iteration'] + fields)
    for it, c in rows:
        w.writerow([it] + ['' if f not in c else repr(c[f]) for f in fields])
    if fh is not sys.stdout:
        fh.close()
    sys.stderr.write('%d iterations, fields: %s\n' % (len(rows), ', '.join(fields)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
