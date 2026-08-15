#!/usr/bin/env python3
"""Retrospective double-writer detector: a directory older than the files in it.

WHY THIS EXISTS. On 2026-08-11 two `simpleFoam` processes ran on one case for
about 60 seconds. The duplicate crossed a write time and **completely overwrote**
a snapshot directory the survivor had written 22 seconds earlier, plus nine
profile files. The write ladder still looked monotonic, every field still parsed,
and the case's own report said "no rewrites" -- because the check that was run
could not see one. The thing that could see it costs nothing:

    A REWRITE LEAVES A DIRECTORY OLDER THAN THE FILES INSIDE IT.

Writing a file into a directory updates the directory's mtime, because a
directory entry was created. Overwriting a file that already exists creates no
entry, so **the directory's mtime does not move while every file's does.** The
directory is left carrying the timestamp of the FIRST write and its contents the
timestamp of the SECOND.

This needs no log, no PID, no lock file, and no cooperation from the writer, and
it works retrospectively on any archive -- including archives written by tools
that no longer exist, by processes nobody was watching, and long before anyone
suspected a problem. That is the whole point of shipping it: we know about one
collision because someone disclosed it.

--------------------------------------------------------------------------------
WHAT IT MEASURES

For every directory containing files:

    gap        = min(file mtimes) - dir mtime
    burst_span = max(file mtimes) - min(file mtimes)

A normally written directory has `gap <= 0` or a `gap` of microseconds: entries
are created as the write proceeds, so the directory's mtime lands at the END of
the write burst, not before it. A rewritten directory has a `gap` equal to the
delay between the two writes.

TIERS, because a naive threshold on `gap` alone is wrong and this was measured,
not assumed. Sweeping 4,865 directories of the incident archive, a bare
`gap > 0` rule produced 1,259 hits, and `gap > 1 s` still produced 29 -- almost
all of them **append-mode `.dat` files**, where the directory records the moment
the file was created and the file records its last append 919 seconds later.
That is a normal, correct, single-writer pattern and it is indistinguishable from
an overwrite if the directory holds only that one file.

  CONFIRMED gap > tolerance, AND the directory's SIBLINGS are a usable control:
            at least `--min-peers` of them, with a median gap inside tolerance.
            The siblings show what a normal write of this exact kind of output
            looks like in this exact place, and this directory does not match
            them. The peer control is what separates a rewrite from an append,
            and NOTHING ELSE DOES -- see below.

  SIGNATURE gap > tolerance, but no usable peer control existed. The contents
   ONLY     are newer than the directory, which is consistent with a rewrite and
            EQUALLY consistent with append-mode output. **Cannot be resolved by
            mtime.** Reported so it is countable; never counted as a hit and
            never counted as clean.

WHY THE PEER CONTROL IS LOAD-BEARING, AND WHY AN EARLIER VERSION OF THIS TOOL
WAS WRONG WITHOUT IT. A file that is created once and then APPENDED TO also
leaves its directory older than its contents: appending writes no new directory
entry, exactly as overwriting writes no new directory entry. **Append and
same-name overwrite are the same mtime signature, and no amount of arithmetic on
mtimes can separate them.** A first cut of this detector required only ">= 2
files rewritten in a tight burst", on the reasoning that appends could not be
simultaneous. That reasoning is false: an OpenFOAM `postProcessing/probes1/`
directory holds several `.dat` files that are all created at the start of the
run and all appended to until the end, so they share a final mtime and a burst
span of zero. That rule produced 213 hits over this repository, and the great
majority were probe and function-object directories doing nothing wrong.

The peers settle it because they are the same output written the same way: in a
`singleGraph_x0/` series, 23 sibling time directories have gap ~0 because each
profile is written once and never touched again, so the one member with a 22.9 s
gap is anomalous *against its own kind*. In a `wallShearStress/` series the
siblings have gaps of minutes to hours, because appending is what that directory
does -- there is no control, and this tool correctly declines to call it.

--------------------------------------------------------------------------------
WRITTEN TWICE IS NOT THE SAME QUESTION AS WRITTEN TWICE AT ONCE, and the sweep
reports the two separately. A rewrite whose two writes are ten days apart is
somebody deliberately re-running a case; a collision is two processes alive at
the same time, so its gap is bounded by how long they overlapped -- seconds to
minutes. `--concurrency-window` (default 1 hour) splits CONFIRMED hits into
COLLISION-SHAPED and RE-RUN-SHAPED. The split is an aid to triage and not a
finding: a re-run gap proves nothing about intent, and a short gap is consistent
with a fast deliberate re-run as well as with a collision.

--------------------------------------------------------------------------------
WHAT IT CANNOT SEE -- and these travel in the verdict line, not only here,
because a caveat that does not travel with the verdict reaches nobody.

  * A rewrite that MOVES the directory mtime. If the second writer creates any
    new filename, or deletes one, the directory mtime updates and the signature
    is erased. It sees complete same-name overwrites, which is the OpenFOAM
    snapshot case, and misses partial ones that add a file.
  * A duplicate that never reached a write. It leaves no artifact at all. A
    clean sweep is NOT evidence that no duplicate ran -- only that none of them
    landed on top of an existing directory.
  * A single-file directory, in general (the AMBIGUOUS tier): append and
    overwrite are the same signature when there are no peers to compare against.
  * ANY LATER TOUCH DESTROYS THE EVIDENCE. mtimes are mutable. `cp -r` without
    `-p`, an unpack, a restore, a `git checkout`, or simply writing a note into
    the directory resets it. **Git does not record mtimes at all**, so tracked
    files carry checkout time and this detector says nothing about them.
  * It cannot say WHO wrote it, or WHEN the duplicate ran, or WHICH of the two
    writes survived. It says only: this directory was written at least twice.
    Attribution needs a second record -- a stored solver value, a function-object
    series, an untouched log.
  * Filesystems with coarse mtime granularity, or mounted `noatime`-style with
    reduced timestamp fidelity, can compress a real gap below tolerance.

Provenance: campaign/F6D_COLLISION_INDEPENDENCE_CHECK.md §7.3; LESSONS.md L-69.
"""

from __future__ import annotations

import argparse
import os
import shutil
import statistics
import sys
import tempfile
import time

#: Below this, a positive gap is ordinary directory-entry bookkeeping rather
#: than a second write. Measured, not guessed: across the incident archive every
#: genuine single-write directory sat under 10 ms, and the real overwrite sat at
#: 22.9 s. One second is three orders of magnitude clear of the noise and one
#: order clear of the shortest plausible re-write interval.
DEFAULT_TOLERANCE = 1.0

#: A STRONG hit needs the rewrite burst to be short compared with the delay.
DEFAULT_BURST_RATIO = 10.0

#: Peer control needs enough siblings for a median to mean anything.
DEFAULT_MIN_PEERS = 4


def scan(roots, tolerance=DEFAULT_TOLERANCE, burst_ratio=DEFAULT_BURST_RATIO,
         min_peers=DEFAULT_MIN_PEERS, follow_symlinks=False):
    """Walk *roots* and classify every directory that contains files."""
    stats = {}                       # dirpath -> (gap, nfiles, burst_span)
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root,
                                                    followlinks=follow_symlinks):
            dirnames[:] = [d for d in dirnames if d != '.git']
            names = []
            for f in filenames:
                p = os.path.join(dirpath, f)
                try:
                    if os.path.islink(p):
                        continue     # a symlink's mtime is the link's, not the data's
                    names.append(os.stat(p).st_mtime)
                except OSError:
                    continue
            if not names:
                continue
            try:
                dm = os.stat(dirpath).st_mtime
            except OSError:
                continue
            stats[dirpath] = (min(names) - dm, len(names), max(names) - min(names))

    # Peer control: the median gap of a directory's siblings, when there are
    # enough of them to be a control rather than an anecdote.
    peers = {}
    for d in stats:
        peers.setdefault(os.path.dirname(d), []).append(d)

    confirmed, signature_only = [], []
    for d, (gap, nfiles, span) in stats.items():
        if gap <= tolerance:
            continue
        sibs = [stats[s][0] for s in peers.get(os.path.dirname(d), []) if s != d]
        med = statistics.median(sibs) if sibs else None
        if len(sibs) >= min_peers and med <= tolerance:
            confirmed.append((gap, d, nfiles, span,
                              f'{len(sibs)} peers, median gap {med:.4f}s'))
        else:
            if med is not None and med > tolerance and len(sibs) >= min_peers:
                # The peers carry the signature too. Two readings, and mtimes
                # cannot choose: this is append-mode output (normal), or the
                # rewrite is WIDESPREAD and has destroyed its own control. Do
                # not assert the benign one -- that is how the widest damage
                # would go unreported.
                why = (f'{len(sibs)} peers, median gap {med:.1f}s -- NO CLEAN '
                       f'CONTROL: either this kind of directory is appended to, '
                       f'or the rewrite covers the peers too')
            else:
                why = (f'{len(sibs)} peers -- no control, append and rewrite are '
                       f'indistinguishable here')
            signature_only.append((gap, d, nfiles, span, why))
    confirmed.sort(reverse=True)
    signature_only.sort(reverse=True)
    return dict(scanned=len(stats), confirmed=confirmed,
                signature_only=signature_only)


BLIND_SPOTS = (
    "BLIND SPOTS, which are part of this verdict and not a footnote: (1) it "
    "cannot see a rewrite that added or removed a filename -- the directory "
    "mtime moves and the signature is erased -- so it catches complete "
    "same-name overwrites and misses partial ones; (2) it cannot see a "
    "duplicate that never reached a write, which leaves no artifact at all, so "
    "A CLEAN RESULT IS NOT EVIDENCE THAT NO DUPLICATE RAN; (3) append-mode "
    "output leaves an identical signature and is separated only by the peer "
    "control, so everything in SIGNATURE ONLY is genuinely unresolved rather "
    "than cleared; (4) it names no writer, no time of day and no winner -- it "
    "says only that a directory was written at least twice, and attribution "
    "needs a second record such as a stored solver value or an untouched log; "
    "(5) it cannot tell a collision from a deliberate re-run except by the "
    "crude gap heuristic above; (5a) THE PEER CONTROL FAILS WHEN THE REWRITE IS "
    "WIDESPREAD -- if most of a directory's siblings were rewritten too, the "
    "median gap is large, no control survives, and the hits drop into SIGNATURE "
    "ONLY, so this instrument is at its LEAST sensitive exactly where the damage "
    "is worst, and a large unresolved count deserves more suspicion than a small "
    "one, not less; (6) mtimes are mutable and unversioned -- any "
    "later touch, `cp -r` without `-p`, unpack, restore or `git checkout` "
    "destroys the evidence permanently, and GIT DOES NOT RECORD MTIMES AT ALL, "
    "so this says nothing whatever about git-tracked content; (7) coarse "
    "filesystem timestamp granularity can compress a real gap below tolerance."
)


def report(res, tolerance, window=3600.0, limit=60, out=sys.stdout):
    w = out.write
    conf = res['confirmed']
    n_hits = len(conf)
    collision = [h for h in conf if h[0] <= window]
    rerun = [h for h in conf if h[0] > window]
    w(f"\ndirectories containing files, scanned: {res['scanned']}\n")
    w(f"tolerance: gap > {tolerance}s; concurrency window: {window}s\n\n")

    w(f"CONFIRMED REWRITE, COLLISION-SHAPED (gap <= {window}s, short enough for "
      f"two live writers): {len(collision)}\n")
    for gap, d, nfiles, span, why in collision:
        w(f"  gap={gap:10.3f}s  files={nfiles:<4} burst={span:.4f}s [{why}]  {d}\n")

    w(f"\nCONFIRMED REWRITE, RE-RUN-SHAPED (gap > {window}s, far too long for an "
      f"overlap; someone re-ran this): {len(rerun)}\n")
    for gap, d, nfiles, span, why in rerun[:limit]:
        w(f"  gap={gap:10.3f}s  files={nfiles:<4} [{why}]  {d}\n")
    if len(rerun) > limit:
        w(f"  ... and {len(rerun) - limit} more\n")

    so = res['signature_only']
    w(f"\nSIGNATURE ONLY, UNRESOLVED (no peer control; append and rewrite are "
      f"indistinguishable here): {len(so)}\n")
    for gap, d, nfiles, span, why in so[:limit]:
        w(f"  gap={gap:10.3f}s  files={nfiles:<4} [{why}]  {d}\n")
    if len(so) > limit:
        w(f"  ... and {len(so) - limit} more\n")

    verdict = ("DOUBLE-WRITE SIGNATURE FOUND" if n_hits else
               "no double-write signature")
    w(f"\nVERDICT: {verdict} -- {n_hits} confirmed rewrite(s) "
      f"({len(collision)} collision-shaped, {len(rerun)} re-run-shaped) in "
      f"{res['scanned']} directories, {len(so)} unresolved. {BLIND_SPOTS}\n")
    return n_hits


# --------------------------------------------------------------------------
# Controls. Both directions, and they ship with the tool so they can be re-run
# rather than being a claim about a run nobody can repeat. An instrument that
# has never been shown to fire has not been shown to work.
# --------------------------------------------------------------------------

def _selftest(verbose=True):
    tmp = tempfile.mkdtemp(prefix='overwrite_ctl_')
    ok = True

    def say(*a):
        if verbose:
            print(*a)

    try:
        def build_series(root, times, files, appended=False):
            """A normally written snapshot series: each directory written once."""
            for t in times:
                d = os.path.join(root, t)
                os.makedirs(d)
                for n in files:
                    with open(os.path.join(d, n), 'w') as fh:
                        fh.write('first writer\n')
                time.sleep(0.02)
            return root

        # ---- NEGATIVE CONTROL 1: ordinary single-pass output, nothing wrong.
        neg = build_series(os.path.join(tmp, 'negative'),
                           ('4500', '5000', '5500', '6000', '6500', '7000',
                            '7500', '8000'),
                           ('U', 'p', 'k', 'omega', 'nut'))
        r = scan([neg])
        if not r['confirmed'] and not r['signature_only']:
            say(f"  PASS  negative control (normal write): silent across "
                f"{r['scanned']} directories")
        else:
            print(f"  FAIL  negative control fired: {r['confirmed']} "
                  f"{r['signature_only']}")
            ok = False

        # ---- POSITIVE CONTROL 1: the incident's exact shape. A normal series,
        # then ONE member rewritten in place with no new filenames.
        pos = build_series(os.path.join(tmp, 'positive'),
                           ('4500', '5000', '5500', '6000', '6500', '7000',
                            '7500', '8000'),
                           ('U', 'p', 'k', 'omega', 'nut'))
        target = os.path.join(pos, '7500')
        dir_mtime_before = os.stat(target).st_mtime
        time.sleep(2.2)
        for n in ('U', 'p', 'k', 'omega', 'nut'):
            with open(os.path.join(target, n), 'w') as fh:  # same names
                fh.write('second writer\n')
        dir_mtime_after = os.stat(target).st_mtime

        # The premise itself, asserted rather than assumed: overwriting existing
        # names must NOT have moved the directory mtime. If this filesystem does
        # move it, the detector is inapplicable here and must say so.
        if abs(dir_mtime_after - dir_mtime_before) > 1e-6:
            print("  FAIL  premise: rewriting in place MOVED the directory "
                  "mtime on this filesystem -- the detector cannot work here.")
            ok = False

        r = scan([pos])
        if len(r['confirmed']) == 1 and r['confirmed'][0][1] == target:
            say(f"  PASS  positive control (multi-file overwrite): fired on the "
                f"one rewritten member, gap={r['confirmed'][0][0]:.2f}s")
        else:
            print(f"  FAIL  positive control: expected 1 CONFIRMED at {target}, "
                  f"got {r['confirmed']}")
            ok = False

        # ---- POSITIVE CONTROL 2: one file per directory -- the nine profile
        # files' shape, which only the peer control can recover.
        ser = build_series(os.path.join(tmp, 'series', 'singleGraph_x0'),
                           ('4500', '5000', '5500', '6000', '6500', '7000',
                            '7500', '8000'), ('line.xy',))
        time.sleep(2.2)
        open(os.path.join(ser, '7500', 'line.xy'), 'w').write('second\n')
        r = scan([ser])
        want = os.path.join(ser, '7500')
        if len(r['confirmed']) == 1 and r['confirmed'][0][1] == want:
            say(f"  PASS  positive control (single-file, peer-controlled): "
                f"fired, gap={r['confirmed'][0][0]:.2f}s")
        else:
            print(f"  FAIL  single-file control: expected 1 CONFIRMED at "
                  f"{want}, got {r['confirmed']}")
            ok = False

        # ---- NEGATIVE CONTROL 2: APPEND-MODE OUTPUT. This is the class that
        # made a first cut of this tool report 213 hits over this repository.
        # A probes directory: several files, all created at the start, all
        # appended to until the end -- so they share a final mtime, the burst
        # span is zero, and the directory is much older than all of them. It
        # must NOT be called a rewrite.
        app = os.path.join(tmp, 'append', 'probes1', '0')
        os.makedirs(app)
        for n in ('p', 'U', 'k'):
            open(os.path.join(app, n), 'w').write('# header\n')
        time.sleep(2.2)
        for n in ('p', 'U', 'k'):
            with open(os.path.join(app, n), 'a') as fh:   # append: no new entry
                fh.write('7500 ...\n')
        r = scan([os.path.join(tmp, 'append')])
        if not r['confirmed'] and len(r['signature_only']) == 1:
            say("  PASS  negative control (append-mode, multi-file): NOT called "
                "a rewrite; correctly reported SIGNATURE ONLY / unresolved")
        else:
            print(f"  FAIL  append control misclassified: "
                  f"confirmed={r['confirmed']} unresolved={r['signature_only']}")
            ok = False

        # ---- BLIND-SPOT CONTROL: asserted as a FAILURE TO DETECT rather than
        # merely described. A rewrite that also adds a filename moves the
        # directory mtime and MUST slip past. Stating a blind spot is cheap;
        # demonstrating it is what makes the verdict line honest.
        bs = build_series(os.path.join(tmp, 'blindspot'),
                          ('4500', '5000', '5500', '6000', '6500', '7000',
                           '7500', '8000'), ('U', 'p'))
        time.sleep(2.2)
        t2 = os.path.join(bs, '7500')
        for n in ('U', 'p'):
            open(os.path.join(t2, n), 'w').write('second\n')
        open(os.path.join(t2, 'extra'), 'w').write('new name\n')  # moves dir mtime
        r = scan([bs])
        if not r['confirmed'] and not r['signature_only']:
            say("  PASS  blind-spot control: a rewrite that adds a filename is "
                "correctly NOT detected (a real miss, by construction)")
        else:
            print(f"  FAIL  blind-spot control: detector claimed to see what it "
                  f"cannot: {r['confirmed']} {r['signature_only']}")
            ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("SELF-TEST: " + ("all controls behaved as specified"
                           if ok else "CONTROL FAILURE -- do not trust a sweep"))
    return ok


def _self_test_requested(argv):
    """Is this the controls-only invocation, which sweeps no directory?

    Read before the parser runs, because the parser requires a root -- see the
    note in main(). Option reading stops at `--`, where argparse stops reading
    options too, and prefix matches are honoured because argparse honours them.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    head = args[:args.index('--')] if '--' in args else args
    return any(len(a) > 2 and '--self-test'.startswith(a) for a in head)


def main(argv=None):
    # The controls-only mode, answered ahead of the parser so the parser can
    # require a root. See the `roots` note below.
    if _self_test_requested(argv):
        return 0 if _selftest() else 1

    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    # AT LEAST ONE ROOT IS REQUIRED IN ARGPARSE'S OWN TERMS, rather than
    # accepted as an empty list and rejected afterwards, and the reason is
    # docket D108. `scripts/lab_check.py` decides whether it can invoke a check
    # by reading this call out of the AST, and a positional carrying
    # `nargs='*'` reads to that predicate as a script that runs with no
    # arguments. So the runner admitted this file, launched it with an empty
    # command line, and got exit 2 with argparse's `usage:` on stderr and an
    # empty stdout -- which under the runner's repaired exit contract is a
    # BLOCKING UNKNOWN, since the whole of that diagnosis is written by the
    # graded check itself. Two such checks were enough that the runner could
    # return no non-blocking verdict on the tree whatever else passed. With
    # `nargs='+'` the runner skips this file as `requires-arguments` before
    # launch and it lands in the coverage statement, where a detector that
    # sweeps a named archive belongs.
    ap.add_argument('roots', nargs='+',
                    help='directories to sweep (at least one; use --self-test '
                         'to run the controls instead)')
    ap.add_argument('--tolerance', type=float, default=DEFAULT_TOLERANCE)
    ap.add_argument('--burst-ratio', type=float, default=DEFAULT_BURST_RATIO)
    ap.add_argument('--min-peers', type=int, default=DEFAULT_MIN_PEERS)
    ap.add_argument('--concurrency-window', type=float, default=3600.0,
                    help='gaps at or below this are collision-shaped; above '
                         'it, too long for an overlap (default 3600s)')
    ap.add_argument('--limit', type=int, default=60,
                    help='max rows to print per non-collision section')
    # Declared so `-h` keeps listing it; the invocation itself is answered by
    # _self_test_requested() above, before this parser is built.
    ap.add_argument('--self-test', action='store_true',
                    help='run the positive and negative controls and exit')
    a = ap.parse_args(argv)

    res = scan(a.roots, a.tolerance, a.burst_ratio, a.min_peers)
    return 2 if report(res, a.tolerance, a.concurrency_window, a.limit) else 0


if __name__ == '__main__':
    sys.exit(main())
