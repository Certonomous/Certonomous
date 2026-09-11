#!/usr/bin/env python3
"""MAAOAF grader -- DARhoSimpleFoam MA288 initialisation ladder.

DRAFT, NOT FROZEN.  Grades ONE arm log.  Two limbs, both binding:

  G-BOUND  count of `Bounding (p|U|rho|e)` lines == 0 over the WHOLE log.
  G-RES    max over equations of the LAST iteration's INITIAL residual.

N-D45: the residual is ALWAYS printed beside the clip count, and a nonzero
clip count makes the row NOT A RESULT whatever the residual says.
N-D44: only `initRes` is ever read.  `finalRes` is refused by assert.

The census is only meaningful if the solver printed every iteration:
DAFoam gates the `Bounding` print on printInterval (measured -- MA288's
trim.log:354 reads `printInterval 100` and its 4000-iteration run carries
388 Bounding lines across exactly 41 printed blocks).  A log whose dict
dump does not read `printInterval 1` is REFUSED, not graded.

Direction-aware planted control, run on EVERY graded log, both ways:
  plant_fail()  injects one `Bounding p<500000` line  -> verdict MUST become NOT A RESULT
  plant_pass()  strips p/U/rho/e clips and rewrites the last block's initRes
                to 1e-9                                -> verdict MUST become GATE REACHED
Either direction failing to flip is a BLIND READER: exit 2, no verdict.
"""
import re, sys, os, tempfile

RES_FLOOR = 0.3762          # R0's established residual floor (A1WCT sec.1)
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


def last_block_max_initres(lines):
    starts = [i for i, ln in enumerate(lines) if TIME_RE.match(ln)]
    if not starts:
        return None, None, {}
    i0 = starts[-1]
    i1 = starts[-1] + 1
    while i1 < len(lines) and not TIME_RE.match(lines[i1]):
        i1 += 1
    per = {}
    for ln in lines[i0:i1]:
        m = INIT_RE.match(ln)
        if m:
            assert "finalRes" not in m.group(2), "N-D44: finalRes captured as residual"
            per[m.group(1)] = float(m.group(2))
    if not per:
        return int(TIME_RE.match(lines[i0]).group(1)), None, {}
    return int(TIME_RE.match(lines[i0]).group(1)), max(per.values()), per


def verdict(lines):
    pi = print_interval(lines)
    if pi != 1:
        return "REFUSE", "printInterval is %r, not 1 -- a sampled Bounding census cannot support a zero claim" % pi, None, None
    c = clip_census(lines)
    tot = sum(c.values())
    it, res, per = last_block_max_initres(lines)
    if res is None:
        return "REFUSE", "no initRes line in the last Time block", c, None
    if tot > 0:
        v = "NOT A RESULT"
    elif res < RES_FLOOR:
        v = "GATE REACHED"
    else:
        v = "GATE FAIL"
    why = "clips(p/U/rho/e)=%d %s | max initRes at Time=%d: %.6e (floor %.4f)" % (
        tot, {k: v2 for k, v2 in c.items() if v2}, it, res, RES_FLOOR)
    return v, why, c, res


# ---------------- direction-aware planted control -------------------------
def plant_fail(lines):
    """Make a passing log fail: inject ONE p clip."""
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


def control(lines, tag):
    """Both directions, every log.  Refuse on a reader that cannot see one."""
    ok = True
    vf, wf, _, _ = verdict(plant_fail(lines))
    if vf != "NOT A RESULT":
        print("PLANT-FAIL BLIND: injected clip graded %s (%s)" % (vf, wf)); ok = False
    else:
        print("plant-fail  OK  -> %s | %s" % (vf, wf))
    vp, wp, _, _ = verdict(plant_pass(lines))
    if vp != "GATE REACHED":
        print("PLANT-PASS BLIND: cleaned log graded %s (%s)" % (vp, wp)); ok = False
    else:
        print("plant-pass  OK  -> %s | %s" % (vp, wp))
    if not ok:
        print("REFUSED: the reader is one-directional on %s" % tag)
        sys.exit(2)


def main(path):
    lines = read(path)
    print("== %s" % path)
    v, why, c, res = verdict(lines)
    print("VERDICT: %s" % v)
    print("         %s" % why)
    if v == "REFUSE":
        # the control still runs, on a printInterval-1 copy, to prove the
        # reader is not blind even when this particular log is ungradeable.
        lines = [PI_RE.sub("    printInterval   1;", ln) for ln in lines]
        print("  (control run against a printInterval-1 copy of the same bytes)")
    control(lines, path)
    print("control: BOTH DIRECTIONS LIVE")
    return 0 if v not in ("REFUSE",) else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
