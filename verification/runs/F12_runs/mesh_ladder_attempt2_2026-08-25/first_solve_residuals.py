#!/usr/bin/env python3
"""F12 — FIRST-SOLVE residual reader, and its planted control.

WHY THIS FILE EXISTS
--------------------
`F12_GATE_B_RULING_2026-08-25.md` §3 (the binding instrument condition):

    Every residual reading on F12, by any monitor, sampler, grader or human, is
    the FIRST solve of the iteration. A tail-read of `p` is reading a number the
    solver's own criterion never sees, and is an instrument defect wherever it
    appears.

F12 runs `nNonOrthogonalCorrectors 1`, so `p` is solved TWICE per SIMPLE
iteration. `simpleControl` tests the FIRST solve's initial residual. A reader
that greps the last `Solving for p` in an iteration returns the last
corrector's value, which the solver's own convergence criterion never sees.

WHAT IT DOES NOT DO
-------------------
It reads. It holds no threshold, no band, no gate arithmetic and no verdict. It
is NOT a grading path and it does not authorise its own use. `launch_f12_rung.py`
is untouched by this file and its bytes are unchanged.

THE CONTROL (standing rule 3, planted zero)
-------------------------------------------
`--selftest` plants two DISTINGUISHABLE values into a copy of a real log — one at
the FIRST `p` position of an iteration, a different one at the LAST — and
requires that this reader returns the FIRST. It also runs a deliberately-wrong
TAIL reader over the same planted copy and requires that it returns the LAST.
Both arms must fire: the first proves the reader is correct, the second proves
the plant actually landed and the two positions are discriminable. If either arm
does not fire, the reader is NOT shown able to tell first from last and every
number it produces is refused.
"""
from __future__ import annotations

import json
import pathlib
import re
import statistics
import sys

# "GAMG:  Solving for p, Initial residual = 1.23e-04, Final residual = ..."
SOLVE = re.compile(
    r"Solving for (?P<f>\w+),\s*Initial residual = (?P<r>[-+0-9.eE]+)")
TIME = re.compile(r"^Time = (\d+)\s*$")

PLANT_FIRST = 1.234e-03   # planted at the FIRST p solve  -> reader MUST return
PLANT_LAST = 5.678e-09    # planted at the LAST  p solve  -> reader MUST NOT


def iterations(text: str):
    """Yield (time, [(field, residual), ...]) per SIMPLE iteration, in order."""
    t, block = None, []
    for line in text.splitlines():
        m = TIME.match(line)
        if m:
            if t is not None:
                yield t, block
            t, block = int(m.group(1)), []
            continue
        if t is None:
            continue
        s = SOLVE.search(line)
        if s:
            try:
                block.append((s.group("f"), float(s.group("r"))))
            except ValueError:
                pass
    if t is not None:
        yield t, block


def _pick(block, first: bool):
    """Reduce one iteration's solves to one value per field.

    first=True  -> the FIRST solve of each field (what simpleControl reads).
    first=False -> the LAST solve (the tail-read DEFECT; control arm only).
    """
    out = {}
    for f, r in block:
        if first and f in out:
            continue
        out[f] = r
    return out


def series(text: str, first: bool = True):
    """Per-iteration first-solve residuals. U = max over solved components,
    which is how residualControl's `U` entry gates (every component must pass)."""
    rows = []
    for t, block in iterations(text):
        if not block:
            continue
        d = _pick(block, first)
        comps = [d[c] for c in ("Ux", "Uy", "Uz") if c in d]
        rows.append({"iteration": t,
                     "p": d.get("p"),
                     "U": max(comps) if comps else None,
                     "k": d.get("k"),
                     "omega": d.get("omega"),
                     "e": d.get("e")})
    return rows


def windows(rows, key, n=6):
    """Median of `key` over n equal windows, ignoring missing values."""
    vals = [(r["iteration"], r[key]) for r in rows if r.get(key) is not None]
    if not vals:
        return []
    w, out = max(1, len(vals) // n), []
    for i in range(0, len(vals), w):
        chunk = vals[i:i + w]
        if chunk:
            out.append({"i_lo": chunk[0][0], "i_hi": chunk[-1][0],
                        "median": statistics.median(v for _, v in chunk),
                        "n": len(chunk)})
    return out


def floor_and_rise(rows, key):
    """Floor value + the iteration it floored at, and the rise ratio the F2
    probe used: median(last quarter) / median(third quarter)."""
    vals = [(r["iteration"], r[key]) for r in rows if r.get(key) is not None]
    if not vals:
        return None
    lo_i, lo_v = min(vals, key=lambda kv: kv[1])
    q = len(vals) // 4
    out = {"floor": lo_v, "floor_iteration": lo_i,
           "first": vals[0][1], "last": vals[-1][1], "n": len(vals)}
    if q >= 2:
        q3 = statistics.median(v for _, v in vals[2 * q:3 * q])
        q4 = statistics.median(v for _, v in vals[3 * q:])
        out.update({"median_q3": q3, "median_q4": q4,
                    "rise_ratio_q4_over_q3": (q4 / q3) if q3 else None,
                    "rose_again": bool(q3 and q4 > q3)})
    return out


# ---------------------------------------------------------------------------
# the control
# ---------------------------------------------------------------------------

def _plant(text: str):
    """Plant PLANT_FIRST at the FIRST p solve and PLANT_LAST at the LAST p solve
    of the first iteration that has >= 2 p solves. Returns (text, time)."""
    lines = text.splitlines()
    bounds, t, start = [], None, None
    for i, line in enumerate(lines):
        m = TIME.match(line)
        if m:
            if t is not None:
                bounds.append((t, start, i))
            t, start = int(m.group(1)), i
    if t is not None:
        bounds.append((t, start, len(lines)))
    for tt, a, b in bounds:
        ps = [i for i in range(a, b)
              if (s := SOLVE.search(lines[i])) and s.group("f") == "p"]
        if len(ps) >= 2:
            for idx, val in ((ps[0], PLANT_FIRST), (ps[-1], PLANT_LAST)):
                lines[idx] = SOLVE.sub(
                    lambda m, v=val: f"Solving for p, Initial residual = {v:.6e}",
                    lines[idx])
            return "\n".join(lines) + "\n", tt
    raise SystemExit("CONTROL REFUSED: no iteration in this log has >= 2 p "
                     "solves, so first and last cannot be discriminated")


def selftest(log_path: pathlib.Path) -> int:
    ok = []

    def chk(name, cond, detail=""):
        ok.append((name, bool(cond)))
        print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))

    raw = log_path.read_text(errors="replace")
    planted, t = _plant(raw)

    got_first = {r["iteration"]: r["p"] for r in series(planted, first=True)}.get(t)
    got_last = {r["iteration"]: r["p"] for r in series(planted, first=False)}.get(t)

    chk(f"POSITIVE arm: reader returns the PLANTED FIRST p at Time = {t}",
        got_first is not None and abs(got_first - PLANT_FIRST) < 1e-12,
        f"got {got_first!r}, planted {PLANT_FIRST}")
    chk("NEGATIVE arm: reader does NOT return the planted LAST-corrector value",
        got_first is None or abs(got_first - PLANT_LAST) > 1e-12,
        f"got {got_first!r}, last-plant {PLANT_LAST}")
    chk("DISCRIMINATION arm: the deliberately-WRONG tail reader returns the "
        "planted LAST value, proving the plant landed and the two positions differ",
        got_last is not None and abs(got_last - PLANT_LAST) < 1e-12,
        f"tail-read got {got_last!r}")
    chk("the two plants are distinguishable at all",
        abs(PLANT_FIRST - PLANT_LAST) > 1e-12)

    # unplanted sanity: F12 has 2 p solves per iteration, so first != last often
    rf = {r["iteration"]: r["p"] for r in series(raw, first=True)}
    rl = {r["iteration"]: r["p"] for r in series(raw, first=False)}
    diff = [i for i in rf if rf[i] is not None and rl.get(i) is not None
            and rf[i] != rl[i]]
    chk("on the UNPLANTED log the first-solve and tail-read series actually "
        "differ, so the distinction is not cosmetic",
        len(diff) > 0, f"{len(diff)}/{len(rf)} iterations differ")

    bad = [n for n, v in ok if not v]
    print(f"\n{len(ok) - len(bad)}/{len(ok)} control checks passed"
          + (f"; FAILED: {bad}" if bad else "; reader IS shown able to discriminate"))
    return 1 if bad else 0


def main(argv):
    if len(argv) >= 3 and argv[1] == "--selftest":
        return selftest(pathlib.Path(argv[2]))
    if len(argv) >= 3 and argv[1] == "--read":
        log = pathlib.Path(argv[2])
        rows = series(log.read_text(errors="replace"), first=True)
        out = {"source_log": str(log), "n_iterations": len(rows),
               "reading": "FIRST solve of each iteration (ruling section 3)",
               "series": rows,
               "windows": {k: windows(rows, k) for k in ("p", "U", "k", "omega", "e")},
               "floor": {k: floor_and_rise(rows, k) for k in ("p", "U", "k", "omega", "e")}}
        print(json.dumps(out, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
