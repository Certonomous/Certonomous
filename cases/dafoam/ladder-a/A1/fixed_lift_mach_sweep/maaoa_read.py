#!/usr/bin/env python3
r"""MAAOA -- the reader for the fixed-lift (Ma, AoA) sweep. FEASIBILITY rung:
READINGS, not verdicts (no grid triple exists for the A1WR mesh family;
verdict ceiling GATE REACHED; nothing here is grid-converged or carries a band).

Reports, per operating point: the TRIM ANGLE alpha(Ma) at fixed CL = 0.5, the
drag at fixed lift CD(Ma; CL = 0.5), the trim quality |CL - 0.5|, the y+
reading, and the convergence classification of the last primal. It cannot
report a stall angle, a drag-divergence Mach number, or any flow-physics
inference from solver behaviour -- G-STALL and G-MDD refuse (exit 2) on its
own finished output.

Planted controls (every mutation asserted to land):
  M1 [+] real/fixture bytes parse to a full trim row;
  M2 [-] planted CL far from target -> NOT TRIMMED;
  M3 [!] parser disabled -> M1 must flip;
  M4 [-] planted y+max >= 1 -> GATE FAIL on that point;
  M5 [!] G-STALL/G-MDD fire on planted claims, not on the honest caveat.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

TRIM_PAT = re.compile(
    r"^MAAOA_TRIM_VALUES mach=(\S+) U0=([0-9.eE+-]+) alpha_deg=(\S+) CL=(\S+) CD=(\S+) "
    r"wall_s=([0-9.]+) err=(.*)$", re.M)
YP_PAT = re.compile(r"^yPlus min: ([0-9.eE+-]+) max: ([0-9.eE+-]+) mean: ([0-9.eE+-]+)", re.M)
CONV = re.compile(
    r"Minimal residual\s+([0-9.eE+-]+)\s+satisfied the prescribed tolerance\s+([0-9.eE+-]+)")
BC_GOOD = "BCType=nutLowReWallFunction"
BC_BAD = "BCType=nutUSpaldingWallFunction"
TRIM_TOL = 1.0e-3     # frozen: |CL - 0.5| <= 1e-3 is TRIMMED (Newton tol 1e-4 target)
CL_TARGET = 0.5
YP_THRESH = 1.0
SOUND = 347.1904      # m/s at T0 = 300 K from the READ constants (A1WR amendment 1)

STALL_CLAIM = re.compile(
    r"(stall|stalls|stalled|separation onset|CL ?max|clmax)"
    r"[^.\n]{0,60}?[-+]?\d+(?:\.\d+)?\s*(?:deg|degree|degrees|°)"
    r"|[-+]?\d+(?:\.\d+)?\s*(?:deg|degree|degrees|°)[^.\n]{0,60}?"
    r"(stall|stalls|stalled|separation onset|CL ?max|clmax)", re.I)
MDD_CLAIM = re.compile(
    r"(drag[- ]divergence|drag rise onset|M_?dd)[^.\n]{0,40}?(0\.\d+)"
    r"|(0\.\d+)[^.\n]{0,40}?(drag[- ]divergence|drag rise onset|M_?dd)", re.I)


def parse_trim(text: str):
    m = None
    for m0 in TRIM_PAT.finditer(text):
        m = m0
    if m is None:
        return None
    def f(x):
        return None if x == "NA" else float(x)
    return {"mach_label": m.group(1), "U0": float(m.group(2)),
            "alpha_trim_deg": f(m.group(3)), "CL": f(m.group(4)), "CD": f(m.group(5)),
            "wall_s": float(m.group(6)),
            "error": None if m.group(7).strip() == "NONE" else m.group(7).strip()}


def yplus_of(text: str):
    m = None
    for m0 in YP_PAT.finditer(text):
        m = m0
    return None if m is None else tuple(float(m.group(i)) for i in (1, 2, 3))


def trim_verdict(row):
    if row is None:
        return "NOT MEASURED", "no MAAOA_TRIM_VALUES line -- the point never reported"
    if row["CL"] is None:
        return "NOT MEASURED", "trim raised before CL could be read: %s" % row["error"]
    dev = abs(row["CL"] - CL_TARGET)
    if dev <= TRIM_TOL:
        return "TRIMMED", "|CL - %.1f| = %.3e <= %.0e" % (CL_TARGET, dev, TRIM_TOL)
    return "NOT TRIMMED", ("|CL - %.1f| = %.3e > %.0e -- the point did NOT hold the "
                           "fixed lift and its CD is not a fixed-lift drag" % (CL_TARGET, dev, TRIM_TOL))


FIXTURE = """Setting nut wall BC for wing. BCType=nutLowReWallFunction
Time = 100
yPlus min: 0.012 max: 0.31 mean: 0.11
Minimal residual 9.1e-09 satisfied the prescribed tolerance 1e-08
MAAOA_TRIM_VALUES mach=MA400 U0=138.876200 alpha_deg=3.1234567 CL=0.500042 CD=0.0123456789 wall_s=1810.22 err=NONE
MAAOA_TRIM_END mach=MA400
"""


def selftest(base: str, note: str):
    global TRIM_PAT
    out = ["PLANTED CONTROLS -- read back through the real parsers, both directions.",
           "  source: %s" % note,
           "  sha256: %s" % hashlib.sha256(base.encode()).hexdigest()]
    fails = []

    def chk(tag, cond, msg):
        out.append("  %-4s %-56s %s" % (tag, msg, "PASS" if cond else "*** FAIL ***"))
        if not cond:
            fails.append(tag)

    r1 = parse_trim(base)
    chk("M1", r1 is not None and trim_verdict(r1)[0] == "TRIMMED",
        "unmodified bytes -> full row, TRIMMED")

    b2 = TRIM_PAT.sub(lambda m: m.group(0).replace("CL=%s" % m.group(4), "CL=0.612345", 1),
                      base, count=1)
    if b2 == base:
        fails.append("M2"); out.append("  M2   MUTATION DID NOT LAND -- control is inert")
    else:
        chk("M2", trim_verdict(parse_trim(b2))[0] == "NOT TRIMMED",
            "planted CL=0.612 -> NOT TRIMMED")

    keep = TRIM_PAT
    TRIM_PAT = re.compile(r"(?!x)x_nothing (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (.*)")
    try:
        r3 = parse_trim(base)
    finally:
        TRIM_PAT = keep
    chk("M3", r3 is None, "parser disabled -> M1 must flip (channel goes blind)")

    b4 = YP_PAT.sub("yPlus min: 0.02 max: 1.71 mean: 0.4", base, count=1)
    if b4 == base:
        fails.append("M4"); out.append("  M4   MUTATION DID NOT LAND -- control is inert")
    else:
        yp = yplus_of(b4)
        chk("M4", yp is not None and yp[1] >= YP_THRESH,
            "planted y+max 1.71 -> read and >= threshold (GATE FAIL path live)")

    chk("M5", bool(STALL_CLAIM.search("the stall angle is 12 deg"))
        and bool(MDD_CLAIM.search("drag divergence at 0.66"))
        and not STALL_CLAIM.search("a non-converged trim is evidence the steady solver "
                                   "stopped converging, not evidence of separation")
        and not MDD_CLAIM.search("No drag-divergence Mach number is named here and none "
                                 "may be derived from this table."),
        "G-STALL and G-MDD fire on plants, silent on the honest caveats")

    out.append("")
    out.append("SELFTEST %s: 5 controls." % ("REFUSED -- " + ",".join(fails) if fails else "PASS"))
    return out, fails


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("usage: maaoa_read.py <RUN_DIR>\n")
        return 2
    run = Path(argv[1])
    lines = ["=" * 78,
             "MAAOA FIXED-LIFT (Ma, AoA) READER -- FEASIBILITY READINGS, NOT VERDICTS",
             "run dir: %s" % run,
             "REGISTERED READING: each point TRIMMED to CL = %.1f (the D19-family target);"
             % CL_TARGET,
             "the Mach sweep reports alpha(Ma) and CD at fixed lift. 'For both' = both",
             "solver arms; the incompressible arm is the fixed-lift control at its single",
             "regime -- a Mach axis exists only in the compressible arm.",
             "=" * 78, ""]

    # controls born against a real artefact when one exists
    base, note = FIXTURE, "WRITER_BUILT fixture (no completed point on disk yet)"
    for u in sorted(run.glob("MA*")) + sorted(run.glob("INCOMP")):
        lp = u / "out" / "trim.log"
        if lp.is_file() and parse_trim(lp.read_text(errors="replace")):
            base, note = lp.read_text(errors="replace"), str(lp)
            break
    st, fails = selftest(base, note)
    lines.extend(st)
    if fails:
        sys.stdout.write("\n".join(lines) + "\n")
        return 2
    lines.append("")

    rows = []
    wall_bad = []
    units = sorted(run.glob("MA*")) + sorted(run.glob("INCOMP"))
    for u in units:
        lp = u / "out" / "trim.log"
        if not lp.is_file():
            rows.append({"point": u.name, "row": None, "yp": None, "conv": None,
                         "note": "no trim.log on disk -- NOT RUN"})
            continue
        t = lp.read_text(errors="replace")
        if BC_BAD in t:
            wall_bad.append("%s: carries %s" % (u.name, BC_BAD))
        elif BC_GOOD not in t:
            wall_bad.append("%s: no %s line" % (u.name, BC_GOOD))
        rows.append({"point": u.name, "row": parse_trim(t), "yp": yplus_of(t),
                     "conv": bool(CONV.search(t)), "note": None})

    if not units:
        lines.append("NO POINT DIRECTORIES ON DISK -- PENDING: the sweep has not run.")
        sys.stdout.write("\n".join(lines) + "\n")
        return 0

    lines.append("G-WALLTREAT: %s" % ("PASS -- every point log confirms the low-Re BC"
                                      if not wall_bad else "REFUSE -- " + "; ".join(wall_bad)))
    lines.append("")
    hdr = ("  %-7s %9s %8s %12s %12s %12s %11s %8s %9s"
           % ("point", "U0(m/s)", "M(-)", "alpha_trim", "CL", "CD@CL0.5", "trim", "y+max", "last conv"))
    lines.append("THE FIXED-LIFT SWEEP -- A1WR L3, PATCHED BUILD, np=1")
    lines.append(hdr)
    lines.append("  " + "-" * len(hdr))
    gate_fail_yp = []
    for r in rows:
        row = r["row"]
        if row is None:
            lines.append("  %-7s %s" % (r["point"], r["note"] or "no MAAOA_TRIM_VALUES line -- reported, not absorbed"))
            continue
        tv, twhy = trim_verdict(row)
        mach = row["U0"] / SOUND if r["point"] != "INCOMP" else None
        yp = r["yp"]
        if yp is not None and yp[1] >= YP_THRESH:
            gate_fail_yp.append((r["point"], yp[1]))
        lines.append("  %-7s %9.3f %8s %12s %12s %12s %11s %8s %9s"
                     % (r["point"], row["U0"],
                        "n/a" if mach is None else "%.4f" % mach,
                        "NA" if row["alpha_trim_deg"] is None else "%.5f" % row["alpha_trim_deg"],
                        "NA" if row["CL"] is None else "%.6f" % row["CL"],
                        "NA" if row["CD"] is None else "%.7f" % row["CD"],
                        tv, "NA" if yp is None else "%.4f" % yp[1],
                        "yes" if r["conv"] else "no"))
        if tv == "NOT TRIMMED":
            lines.append("          ^ %s" % twhy)
        if row["error"]:
            lines.append("          ^ recorded exception (never retried): %s" % row["error"][:160])
    lines.append("")
    if gate_fail_yp:
        lines.append("G-YPLUS: GATE FAIL -- y+max >= 1.0 at: %s. The wall-resolved claim is"
                     % ", ".join("%s (%.3f)" % x for x in gate_fail_yp))
        lines.append("  WITHDRAWN for those points; the mesh is NOT re-cut.")
    else:
        measured = [r for r in rows if r["yp"] is not None]
        lines.append("G-YPLUS: %s" % ("PASS on every measured point (worst y+max %.4f < 1.0; %d of %d measured)"
                                      % (max(r["yp"][1] for r in measured), len(measured), len(rows))
                                      if measured else "NOT MEASURED on any point -- reported"))
    lines.append("")
    lines.append("SCOPE (G-NOBAND). FEASIBILITY: the A1WR mesh family's grid convergence is")
    lines.append("PENDING; nothing above is grid-converged or carries a band; the item ceiling")
    lines.append("is GATE REACHED. A non-converged trim is evidence the steady solver stopped")
    lines.append("converging, not evidence of separation. No drag-divergence Mach number is")
    lines.append("named here and none may be derived from this table.")

    report = "\n".join(lines) + "\n"
    hit = STALL_CLAIM.search(report) or MDD_CLAIM.search(report)
    if hit:
        sys.stdout.write(report)
        sys.stderr.write("\nG-STALL/G-MDD REFUSE: output binds a flow-physics claim to a "
                         "number: %r\n" % hit.group(0))
        return 2
    sys.stdout.write(report)
    sys.stdout.write("G-STALL/G-MDD PASS: no stall or drag-divergence claim in this output.\n")
    if wall_bad:
        sys.stderr.write("\nG-WALLTREAT REFUSE (exit 2): %s\n" % "; ".join(wall_bad))
        return 2
    (run / "MAAOA_POINTS.json").write_text(json.dumps(
        [{**(r["row"] or {"point_only": r["point"]}), "point": r["point"],
          "yplus_min_max_mean": r["yp"], "last_primal_converged_line": r["conv"],
          "note": r["note"]} for r in rows], indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
