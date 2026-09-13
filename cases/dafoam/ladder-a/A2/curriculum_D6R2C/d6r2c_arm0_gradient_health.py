#!/usr/bin/env python
"""D6R2C ARM 0 -- PARALLELISM HEALTH.

Sanaa 2026-09-12, D6R2 item 5: "Parallelism health: the multipoint gradient at
2 and 4 ranks agrees to the registered tolerance before iteration 1."

TWO MODES
  --dump <file>   run the multipoint model once and its adjoint once (the
                  producer's `compute_totals` path) at whatever rank count
                  mpirun was given, and write every total derivative to JSON
                  from RANK 0 ONLY.
  --compare a b   read two dumps and grade them against the FROZEN tolerance.

THE TOLERANCE IS REGISTERED BEFORE THE ARM RUNS (PREREGISTRATION.md section 7)
and is reproduced below.  It is a RELATIVE tolerance on each component,
normalised by the infinity norm of the 4-rank gradient for that (of, wrt) pair,
so a component that is a rounding-level number against a large gradient is not
graded as a 100 % disagreement.  Components whose 4-rank magnitude is below
ABS_FLOOR are graded on an ABSOLUTE tolerance instead and are counted and named.

WHY A TOLERANCE AND NOT BITWISE.  The adjoint is solved by GMRES to
gmresRelTol = 1.0e-6 and the primal to primalMinResTol = 1.0e-8; the domain
decomposition differs between 2 and 4 ranks, so the linear solves are different
sequences of floating-point reductions on different partitions.  Bitwise
agreement is not a property this solver class has at two rank counts and
claiming it would be a bar written to be failed.  1.0e-4 relative is two
decades looser than the adjoint's own relative tolerance and two decades
TIGHTER than the 1.0e-2 level at which a genuine parallel defect (a missing
halo exchange, an unsummed boundary contribution) shows up in this family.

THE PRODUCER'S BYTES.  The header of d6r2c_opt_runScript.py up to the literal
anchor `# OpenMDAO setup` is exec'd, so daOptions, Top, POINTS, WEIGHTS, the
constraints and the design variables are the producer's own -- never a copy.
"""
import os
import sys
import json
import time
import hashlib
import argparse
import re   # ADDENDUM 5 (2026-09-13): line-anchored, uniqueness-checked header split

PRODUCER = "d6r2c_opt_runScript.py"
ANCHOR = "# OpenMDAO setup"

# ---- FROZEN (PREREGISTRATION.md section 7) --------------------------------
REL_TOL = 1.0e-4          # per component, normalised by ||g_4rank||_inf of that pair
ABS_FLOOR = 1.0e-12       # below this 4-rank magnitude, grade absolutely
ABS_TOL = 1.0e-12
MAX_SMALL_FRACTION = 0.50  # if more than half the components fall below ABS_FLOOR the
                           # comparison is NOT A RESULT: the gradient carries no signal


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _split_producer_header(src):
    """ADDENDUM 5 (2026-09-13).  Find THE anchor line, and REFUSE if it is not
    unique, instead of silently taking the first text that looks like it.

    THE DEFECT THIS REPAIRS, MEASURED ON THE LIVE CHAIN AT 2026-09-12T23:56Z.
    `dump()` did `i = src.index(ANCHOR)`, which returns the FIRST occurrence
    anywhere in the file, including inside a string.  `# OpenMDAO setup` occurs
    TWICE in d6r2c_opt_runScript.py: at line 292, where it is the real anchor,
    and at line 21, INSIDE THE MODULE DOCSTRING, in a sentence that reads "The
    ANCHOR line `# OpenMDAO setup` is kept so that ..." -- the prose documenting
    the mechanism is what broke it.  `index()` took line 21, so `header` ended in
    the middle of an unterminated triple-quoted string and `compile()` raised
    SyntaxError: unterminated triple-quoted string literal (detected at line 21).
    Both ARM0 arms died rc=1 in 31 s and 11 s and wrote no arm0_totals.json.

    AND THE PART THAT MATTERS MORE THAN THE BUG.  This is NOT a regression: the
    same two occurrences are present at 3ebba6ccc~1, so `--dump` HAS NEVER RUN
    SUCCESSFULLY, NOT ONCE, since the file was written.  The freeze recorded
    "arm-0 comparator 6 controls PASS", but --selftest drives only --compare over
    SYNTHETIC dumps; the PRODUCER half -- the only half that ever runs on the
    cluster -- was never executed before it was put in a production chain.  A
    selftest that exercises the grader and not the producer is not a selftest of
    the instrument.

    THIS CHANGES NO GATE, THRESHOLD, TOLERANCE, CAP OR LABEL.  REL_TOL stays
    1.0e-4, ABS_FLOOR/ABS_TOL stay 1.0e-12, and the comparison code is untouched.
    It repairs a producer that could not run at all, so it cannot move a verdict
    in a wanted direction: before this, there was no verdict to move.
    """
    marks = [m.start() for m in
             re.finditer(r"(?m)^[ \t]*" + re.escape(ANCHOR) + r"[ \t]*$", src)]
    if len(marks) != 1:
        print("D6R2C_ARM0 REFUSE: the anchor %r occurs %d times as a whole line in %s; "
              "it must occur exactly once. Taking the first would risk cutting the "
              "header inside a string literal, which is precisely the defect ADDENDUM 5 "
              "repairs. Lines: %s"
              % (ANCHOR, len(marks), PRODUCER,
                 [src[:m].count("\n") + 1 for m in marks]))
        sys.exit(2)
    header = src[:marks[0]]
    # Compile here so a malformed split REFUSES with a named reason rather than
    # surfacing as a raw SyntaxError from inside exec() four frames down.
    try:
        code = compile(header, PRODUCER, "exec")
    except SyntaxError as e:
        print("D6R2C_ARM0 REFUSE: the %d-line header cut at the anchor (line %d) does not "
              "compile: %s. The anchor is in the wrong place or the producer changed."
              % (header.count("\n") + 1, src[:marks[0]].count("\n") + 1, e))
        sys.exit(2)
    print("D6R2C_ARM0_HEADER anchor_line=%d header_lines=%d producer=%s"
          % (src[:marks[0]].count("\n") + 1, header.count("\n") + 1, PRODUCER))
    return code


def dump(outfile):
    src = open(PRODUCER).read()
    code = _split_producer_header(src)
    header = code
    # the producer's argparse reads sys.argv; give it the registered task
    saved = sys.argv
    sys.argv = [PRODUCER, "-task", "compute_totals", "-optimizer", "IPOPT"]
    g = {"__name__": "__producer__"}
    exec(header, g)   # ADDENDUM 5: already compiled (and syntax-checked) above
    sys.argv = saved

    om = g["om"]; MPI = g["MPI"]; np = g["np"]; Top = g["Top"]; POINTS = g["POINTS"]
    rank = MPI.COMM_WORLD.rank
    size = MPI.COMM_WORLD.size
    if os.getuid() == 0:
        if rank == 0:
            print("D6R2C REFUSE: running as uid 0. Sanaa Launch item 6.")
        sys.exit(72)

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")
    t0 = time.time()
    prob.run_model()
    of = ["obj.J"] + ["%s.aero_post.CL" % p for p in POINTS]
    wrt = ["twist", "shape"]
    totals = prob.compute_totals(of=of, wrt=wrt)
    wall = time.time() - t0

    if rank == 0:
        out = {"ranks": size, "wall_s": round(wall, 3), "producer_md5": md5_of(PRODUCER),
               "uid": os.getuid(), "gid": os.getgid(),
               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "totals": {}}
        for k, v in totals.items():
            out["totals"]["%s|%s" % (k[0], k[1])] = [float(x) for x in np.asarray(v).flatten()]
        with open(outfile, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush(); os.fsync(fh.fileno())
        print("D6R2C_ARM0_DUMP ranks=%d pairs=%d file=%s wall_s=%.1f"
              % (size, len(out["totals"]), outfile, wall))
    return 0


def compare(pa, pb, plant=None, json_out=None):
    A = json.load(open(pa)); B = json.load(open(pb))
    lo = A if A["ranks"] < B["ranks"] else B      # 2 ranks
    hi = B if A["ranks"] < B["ranks"] else A      # 4 ranks, the normalising reference
    if lo["ranks"] == hi["ranks"]:
        print("D6R2C_ARM0 REFUSE: both dumps are at %d ranks; this is not a 2-vs-4 comparison."
              % lo["ranks"])
        return 2
    if lo["producer_md5"] != hi["producer_md5"]:
        print("D6R2C_ARM0 REFUSE: the two dumps did not run the same producer (%s vs %s)."
              % (lo["producer_md5"], hi["producer_md5"]))
        return 2
    if set(lo["totals"]) != set(hi["totals"]):
        print("D6R2C_ARM0 REFUSE: the two dumps carry different derivative pairs.")
        return 2

    rows = []; worst = 0.0; worst_key = None; n_small = 0; n_tot = 0; n_bad = 0
    for k in sorted(hi["totals"]):
        a = lo["totals"][k]; b = hi["totals"][k]
        if len(a) != len(b):
            print("D6R2C_ARM0 REFUSE: pair %s has %d vs %d components." % (k, len(a), len(b)))
            return 2
        scale = max(abs(x) for x in b) if b else 0.0
        for i, (u, v) in enumerate(zip(a, b)):
            if plant is not None and n_tot == 0:
                u = u + plant
            n_tot += 1
            if abs(v) < ABS_FLOOR and scale < ABS_FLOOR:
                n_small += 1
                d = abs(u - v); tol = ABS_TOL; mode = "abs"
            else:
                d = abs(u - v) / scale if scale else abs(u - v)
                tol = REL_TOL; mode = "rel(||g4||_inf)"
            if d > tol:
                n_bad += 1
                rows.append((k, i, u, v, d, tol, mode))
            if d > worst:
                worst = d; worst_key = "%s[%d]" % (k, i)

    small_frac = n_small / n_tot if n_tot else 1.0
    if small_frac > MAX_SMALL_FRACTION:
        label = "NOT A RESULT"
        note = ("%.1f %% of components fall below ABS_FLOOR %.1e -- the gradient carries too "
                "little signal for a 2-vs-4 comparison to mean anything" % (100 * small_frac, ABS_FLOOR))
    elif n_bad == 0:
        label = "PASS"
        note = "all %d components agree" % n_tot
    else:
        label = "GATE FAIL"
        note = "%d of %d components disagree" % (n_bad, n_tot)

    for r in rows[:20]:
        print("  MISS %s[%d] lo=%.12e hi=%.12e %s=%.3e vs %.1e" % (r[0], r[1], r[2], r[3], r[6], r[4], r[5]))
    print("D6R2C_ARM0_VERDICT %s -- %s; worst %.3e at %s against %.1e; ranks %d vs %d; "
          "%d components, %d below floor" % (label, note, worst, worst_key, REL_TOL,
                                             lo["ranks"], hi["ranks"], n_tot, n_small))
    if json_out:
        with open(json_out, "w") as fh:
            json.dump({"verdict": label, "note": note, "worst_rel": worst, "worst_key": worst_key,
                       "rel_tol": REL_TOL, "abs_floor": ABS_FLOOR, "n_components": n_tot,
                       "n_below_floor": n_small, "n_disagreeing": n_bad,
                       "ranks_lo": lo["ranks"], "ranks_hi": hi["ranks"],
                       "producer_md5": hi["producer_md5"]}, fh, indent=1, sort_keys=True)
    return 0 if label == "PASS" else 1


def selftest():
    """No compute, no run directory.  Drives the comparator in both directions."""
    import tempfile
    fails = []
    d = tempfile.mkdtemp()

    def w(name, ranks, vals):
        p = os.path.join(d, name)
        json.dump({"ranks": ranks, "wall_s": 1.0, "producer_md5": "x" * 32, "uid": 1000,
                   "gid": 1000, "utc": "t", "totals": {"obj.J|shape": vals}}, open(p, "w"))
        return p

    base = [1.0, -0.5, 0.25, 0.125]
    a = w("a.json", 2, base)
    b = w("b.json", 4, base)
    print("D6R2C_ARM0 SELFTEST")
    for tag, plant, want in (
            ("A1 identical gradients", None, 0),
            ("B1 plant 1.0e-3 (10x the tolerance) into one component", 1.0e-3, 1),
            ("B2 plant 1.0e-5 (below the tolerance) -- must still PASS", 1.0e-5, 0),
            ("B3 plant 1.234e-03, the lab's constant", 1.234e-3, 1)):
        rc = compare(a, b, plant=plant)
        ok = (rc == want)
        print("  %-62s rc=%d (want %d) %s" % (tag, rc, want, "OK" if ok else "*** DID NOT FIRE ***"))
        if not ok:
            fails.append(tag)
    c = w("c.json", 4, base)
    rc = compare(b, c)
    ok = rc == 2
    print("  %-62s rc=%d (want 2) %s" % ("C1 both dumps at 4 ranks must REFUSE", rc, "OK" if ok else "*** DID NOT FIRE ***"))
    if not ok:
        fails.append("C1")
    tiny = w("t.json", 2, [1e-20, 1e-20, 1e-20, 1e-20])
    tiny4 = w("t4.json", 4, [1e-20, 1e-20, 1e-20, 1e-20])
    rc = compare(tiny, tiny4)
    ok = rc == 1
    print("  %-62s rc=%d (want 1) %s" % ("D1 an all-noise gradient is NOT A RESULT, not a PASS", rc, "OK" if ok else "*** DID NOT FIRE ***"))
    if not ok:
        fails.append("D1")
    print("")
    if fails:
        print("D6R2C_ARM0 SELFTEST FAIL -- %s" % fails)
        return 1
    print("D6R2C_ARM0 SELFTEST PASS -- 6 controls, both directions")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump"); ap.add_argument("--compare", nargs=2)
    ap.add_argument("--json-out"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.dump:
        sys.exit(dump(a.dump))
    if a.compare:
        sys.exit(compare(a.compare[0], a.compare[1], json_out=a.json_out))
    ap.print_help(); sys.exit(64)
