#!/usr/bin/env python3
"""MAAOAF2 grader -- DARhoSimpleFoam MA288, potentialFoam-baselined settings ladder.

DRAFT, NOT FROZEN.  Grades ONE arm log.  Derived from the frozen
cases/dafoam/ladder-a/A1/curriculum_MAAOAF/grade_maaoaf.py (md5
0b81bdef8ab595e7901612f7908f44a2), which caught three real failures.
G-BOUND, G-SAMPLE, G-RES and the direction-aware planted control are carried
UNCHANGED in behaviour and threshold -- a gate that moves between rungs of one
ladder is gate-shopping, so RES_FLOOR stays at R0's established 0.3762.

WHAT IS NEW HERE, AND IT IS THE RULE THAT DECIDED MAAOAF:

  G-MATCH.  Arms are compared on CLIP ONSET and on CLIP RATE AT MATCHED
  ITERATIONS (t1, t10, t50, t100) -- NEVER on a total, and NEVER on how long
  an arm survived.  MAAOAF's N1 had the LOWEST total of four arms (8) and was
  the WORST arm: its count fell to zero at t10 because the field had gone
  non-finite, not because it was healthy.  A FALLING CLIP COUNT IS NOT HEALTH.
  (cfd measured two identical configurations of a diverging compressible case
  dying at iterations 20 and 324 under MPI reduction-order non-determinism, so
  survival length is not a measurement at all.)

  Therefore this grader ALWAYS prints `first_clip_iteration` and the matched-
  iteration census, and when the log's last Time is short of END_TIME_EXPECT
  it stamps the row TRUNCATED and says in words that its total is NOT
  comparable with a full arm's.  The stamp is informational to the verdict and
  binding on the reader.

N-D45: the residual is ALWAYS printed beside the clip count, and a nonzero
clip count makes the row NOT A RESULT whatever the residual says.
N-D44: only `initRes` is ever read.  `finalRes` is refused by assert.
"""
import re, sys

RES_FLOOR       = 0.3762     # inherited UNCHANGED from MAAOAF/A1WCT: R0's floor
END_TIME_EXPECT = 500        # registered arm length; short of it => TRUNCATED
MATCH_ITERS     = (1, 10, 50, 100)   # the matched-iteration comparison points
CLIPPED   = ("p", "U", "rho", "e")
BOUND_RE  = re.compile(r"^Bounding (p|U|rho|e)[<>]")
INIT_RE   = re.compile(r"^(\w+) initRes: ([0-9.eE+-]+) finalRes:")
TIME_RE   = re.compile(r"^Time = (\d+)\s*$")
PI_RE     = re.compile(r"^\s*printInterval\s+(\d+);")


def read(path):
    with open(path, errors="replace") as fh:
        return fh.read().splitlines()


def print_interval(lines):
    for ln in lines:
        m = PI_RE.match(ln)
        if m:
            return int(m.group(1))
    return None


def clip_census(lines):
    c = {f: 0 for f in CLIPPED}
    for ln in lines:
        m = BOUND_RE.match(ln)
        if m:
            c[m.group(1)] += 1
    return c


def walk_iters(lines):
    """-> (first_clip_iteration|None, {iter: clips}, last_time|None).

    A clip printed before the first `Time =` block is attributed to iteration
    0, not silently dropped: `no Time yet` and `no clip` are different facts.
    """
    cur, first, per, last = None, None, {}, None
    for ln in lines:
        m = TIME_RE.match(ln)
        if m:
            cur = int(m.group(1)); last = cur; per.setdefault(cur, 0)
            continue
        if BOUND_RE.match(ln):
            it = 0 if cur is None else cur
            per[it] = per.get(it, 0) + 1
            if first is None:
                first = it
    return first, per, last


def last_block_max_initres(lines):
    starts = [i for i, ln in enumerate(lines) if TIME_RE.match(ln)]
    if not starts:
        return None, None, {}
    i0 = starts[-1]
    i1 = i0 + 1
    while i1 < len(lines) and not TIME_RE.match(lines[i1]):
        i1 += 1
    per = {}
    for ln in lines[i0:i1]:
        m = INIT_RE.match(ln)
        if m:
            assert "finalRes" not in m.group(2), "N-D44: finalRes captured as residual"
            per[m.group(1)] = float(m.group(2))
    it = int(TIME_RE.match(lines[i0]).group(1))
    if not per:
        return it, None, {}
    return it, max(per.values()), per


def verdict(lines):
    """-> (verdict, why, census, res, extras).  extras carries G-MATCH."""
    pi = print_interval(lines)
    if pi != 1:
        return ("REFUSE",
                "printInterval is %r, not 1 -- a sampled Bounding census cannot support a zero claim" % pi,
                None, None, {})
    c   = clip_census(lines)
    tot = sum(c.values())
    first, per_iter, last_time = walk_iters(lines)
    it, res, _ = last_block_max_initres(lines)
    extras = {
        "first_clip_iteration": first,
        "matched": {k: per_iter.get(k) for k in MATCH_ITERS},
        "last_time": last_time,
        "truncated": (last_time is None or last_time < END_TIME_EXPECT),
    }
    if res is None:
        return "REFUSE", "no initRes line in the last Time block", c, None, extras
    if tot > 0:
        v = "NOT A RESULT"
    elif res < RES_FLOOR:
        v = "GATE REACHED"
    else:
        v = "GATE FAIL"
    why = "clips(p/U/rho/e)=%d %s | max initRes at Time=%d: %.6e (floor %.4f)" % (
        tot, {k: n for k, n in c.items() if n}, it, res, RES_FLOOR)
    return v, why, c, res, extras


def report_match(extras):
    """G-MATCH: the comparison the ladder is judged on, printed every time."""
    print("G-MATCH  first_clip_iteration: %s" % extras.get("first_clip_iteration"))
    m = extras.get("matched", {})
    print("G-MATCH  clips at matched iterations %s: %s"
          % (list(MATCH_ITERS), {k: ("-" if m.get(k) is None else m[k]) for k in MATCH_ITERS}))
    print("G-MATCH  arms are ranked on ONSET and MATCHED-ITERATION RATE, never on a total")
    print("G-MATCH  and never on survival length.  A FALLING CLIP COUNT IS NOT HEALTH.")
    if extras.get("truncated"):
        print("G-MATCH  TRUNCATED: last Time = %s, short of the registered %d."
              % (extras.get("last_time"), END_TIME_EXPECT))
        print("G-MATCH  THIS ROW'S TOTAL CLIP COUNT IS NOT COMPARABLE WITH A FULL ARM'S")
        print("G-MATCH  (MAAOAF N1: total 8, the LOWEST of four arms, and the worst arm).")


# ---------------- direction-aware planted control -------------------------
def plant_fail(lines):
    """Make a passing log fail: inject ONE p clip into the FIRST Time block."""
    out = list(lines)
    for i, ln in enumerate(out):
        if TIME_RE.match(ln):
            out.insert(i + 1, "Bounding p<500000")
            return out
    return out + ["Bounding p<500000"]


def plant_pass(lines):
    """Make a failing log pass: strip p/U/rho/e clips, drive last initRes to 1e-9."""
    out = [ln for ln in lines if not BOUND_RE.match(ln)]
    starts = [i for i, ln in enumerate(out) if TIME_RE.match(ln)]
    if starts:
        for i in range(starts[-1], len(out)):
            m = INIT_RE.match(out[i])
            if m:
                out[i] = re.sub(r"initRes: [0-9.eE+-]+", "initRes: 1.0e-09", out[i])
    return out


def first_time(lines):
    for ln in lines:
        m = TIME_RE.match(ln)
        if m:
            return int(m.group(1))
    return None


def control(lines, tag):
    """Both directions, every log, AND the new G-MATCH field in both.

    A reader that grades correctly but reports first_clip_iteration blind
    would let the whole judging rule read as a planted zero, so the control
    asserts THAT FIELD MOVES TOO, in both directions.
    """
    ok = True
    ft = first_time(lines)

    vf, wf, _, _, ef = verdict(plant_fail(lines))
    if vf != "NOT A RESULT":
        print("PLANT-FAIL BLIND: injected clip graded %s (%s)" % (vf, wf)); ok = False
    elif ef.get("first_clip_iteration") != ft:
        print("PLANT-FAIL BLIND ON G-MATCH: clip injected into Time=%s but"
              " first_clip_iteration read %s" % (ft, ef.get("first_clip_iteration"))); ok = False
    else:
        print("plant-fail  OK  -> %s | first_clip_iteration=%s | %s" % (vf, ef.get("first_clip_iteration"), wf))

    vp, wp, _, _, ep = verdict(plant_pass(lines))
    if vp != "GATE REACHED":
        print("PLANT-PASS BLIND: cleaned log graded %s (%s)" % (vp, wp)); ok = False
    elif ep.get("first_clip_iteration") is not None:
        print("PLANT-PASS BLIND ON G-MATCH: all clips stripped but"
              " first_clip_iteration read %s" % ep.get("first_clip_iteration")); ok = False
    else:
        print("plant-pass  OK  -> %s | first_clip_iteration=None | %s" % (vp, wp))

    if not ok:
        print("REFUSED: the reader is one-directional on %s" % tag)
        sys.exit(2)


def main(path):
    lines = read(path)
    print("== %s" % path)
    v, why, c, res, extras = verdict(lines)
    print("VERDICT: %s" % v)
    print("         %s" % why)
    if v != "REFUSE":
        report_match(extras)
    if v == "REFUSE":
        lines = [PI_RE.sub("    printInterval   1;", ln) for ln in lines]
        print("  (control run against a printInterval-1 copy of the same bytes)")
    control(lines, path)
    print("control: BOTH DIRECTIONS LIVE, VERDICT AND G-MATCH")
    return 0 if v != "REFUSE" else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
