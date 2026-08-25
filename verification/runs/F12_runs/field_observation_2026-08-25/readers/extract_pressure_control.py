#!/usr/bin/env python3
"""Extract rhoSimpleFoam's own `pressureControl: p max/min` series per SIMPLE
iteration from a solver log, plus the time-step continuity errors.

These lines are printed by pressureControl::limit() BEFORE the pMinFactor /
pMaxFactor clip is applied, so they report the UNCLIPPED extremes of the
pressure field the pressure equation actually produced.  They are therefore a
FIELD observation already present in the registered log, not a residual.

CONTROL (standing rule 3): --selftest plants a known p-min value at a known
iteration in a copy of a real log and requires the reader return exactly it at
exactly that iteration, and requires a reader given a log with the lines removed
to return NOTHING -- proving the reader is not manufacturing rows.
"""
import json, pathlib, re, sys

TIME = re.compile(r"^Time = (\d+)\s*$")
PMAX = re.compile(r"^pressureControl: p max ([-+0-9.eE]+)")
PMIN = re.compile(r"^pressureControl: p min ([-+0-9.eE]+)")
CONT = re.compile(r"^time step continuity errors : sum local = ([-+0-9.eE]+), "
                  r"global = ([-+0-9.eE]+), cumulative = ([-+0-9.eE]+)")
PLANT_PMIN = -9.87654321e+05

def read(text):
    rows, t, cur = [], None, None
    def flush():
        if cur is not None and (cur["p_max"] is not None or cur["p_min"] is not None
                                or cur["cont_local"] is not None):
            rows.append(cur)
    for line in text.splitlines():
        m = TIME.match(line)
        if m:
            flush()
            t = int(m.group(1))
            cur = {"iteration": t, "p_max": None, "p_min": None,
                   "cont_local": None, "cont_global": None, "cont_cum": None}
            continue
        if cur is None:
            continue
        a = PMAX.match(line)
        if a and cur["p_max"] is None: cur["p_max"] = float(a.group(1)); continue
        b = PMIN.match(line)
        if b and cur["p_min"] is None: cur["p_min"] = float(b.group(1)); continue
        c = CONT.match(line)
        if c and cur["cont_local"] is None:
            cur["cont_local"] = float(c.group(1)); cur["cont_global"] = float(c.group(2))
            cur["cont_cum"] = float(c.group(3)); continue
    flush()
    return rows

def selftest(path):
    ok = []
    def chk(n, c, d=""):
        ok.append((n, bool(c))); print(("PASS  " if c else "FAIL  ")+n+(f"  [{d}]" if d else ""))
    raw = path.read_text(errors="replace")
    base = read(raw)
    chk("baseline: the reader finds pressureControl rows in the real log at all",
        len(base) > 0, f"{len(base)} rows")
    # POSITIVE arm -- plant a distinctive p min at the 7th such iteration
    target = base[6]["iteration"]
    lines, t, done = raw.splitlines(), None, False
    for i, l in enumerate(lines):
        m = TIME.match(l)
        if m: t = int(m.group(1)); continue
        if t == target and PMIN.match(l) and not done:
            lines[i] = f"pressureControl: p min {PLANT_PMIN}"; done = True
    chk("the plant landed in the text", done)
    got = {r["iteration"]: r["p_min"] for r in read("\n".join(lines)+"\n")}.get(target)
    chk(f"POSITIVE arm: reader returns the PLANTED p min at iteration {target}",
        got is not None and abs(got - PLANT_PMIN) < 1e-6, f"got {got!r}")
    chk("and returns it at the RIGHT iteration, not a neighbour",
        {r["iteration"]: r["p_min"] for r in read("\n".join(lines)+"\n")}.get(target-1) != PLANT_PMIN)
    # NEGATIVE arm -- strip every pressureControl line; reader must see NO p values
    stripped = "\n".join(l for l in raw.splitlines() if not l.startswith("pressureControl:"))
    sr = read(stripped)
    chk("NEGATIVE arm: with the lines removed the reader reports NO p extremes, "
        "so a zero/absent reading is not manufactured",
        all(r["p_min"] is None and r["p_max"] is None for r in sr),
        f"{sum(1 for r in sr if r['p_min'] is not None)} spurious")
    bad = [n for n, v in ok if not v]
    print(f"\n{len(ok)-len(bad)}/{len(ok)} control checks passed" + (f"; FAILED {bad}" if bad else
          "; reader IS shown able to see a planted p extreme and not to invent one"))
    return 1 if bad else 0

if __name__ == "__main__":
    p = pathlib.Path(sys.argv[2])
    if sys.argv[1] == "--selftest": raise SystemExit(selftest(p))
    rows = read(p.read_text(errors="replace"))
    print(json.dumps({"source_log": str(p), "n_rows": len(rows), "series": rows}, indent=1))
