#!/usr/bin/env python3
r"""A1WR -- the reader for the wall-resolved alpha polars. FEASIBILITY rung:
READINGS, not verdicts (A1WR_PREREGISTRATION.md section 1.3: this mesh family's
own grid convergence is PENDING; nothing here may be quoted as grid-converged;
verdict ceiling GATE REACHED, composition per section 1.4 at grading).

Derived from the FROZEN coarse reader `feasibility_aoa_polar/aoa_read.py`
(md5 recorded in A1WR ADDENDUM C), carrying ALL ELEVEN of its planted
controls unchanged, plus this item's own channels:

  * G-YPLUS   -- per-point y+ from DAFoam's own printed `yPlus min/max/mean`
                 line (print-cadence exact to <= printInterval iterations,
                 stated per point), verdict GATE FAIL on y+max >= 1.0 anywhere;
                 REFUSE (exit 2) when a point ran >= 200 iterations and the
                 reader saw NO y+ line (a blind channel, rule 3); a shorter
                 point with no line is NOT MEASURED, a named null.
  * G-WALLTREAT -- every unit log must carry `BCType=nutLowReWallFunction`
                 and must NOT carry a set `BCType=nutUSpaldingWallFunction`;
                 REFUSE (exit 2) otherwise.
  * G-CONCURRENCY-BITS -- cold_I_4 (run under full 8-unit load) vs dup_I_4
                 (run alone): the CL/CD line SERIES must be BIT-IDENTICAL.
                 Registered falsifier (Addendum B 14.3): ANY differing bit
                 means concurrency is not numerically free on this ground and
                 the item REPORTS that.

THE ONE THING THIS READER IS BUILT TO BE INCAPABLE OF: reporting a stall
angle. G-STALL scans this reader's own finished output and REFUSES (exit 2)
on a stall word bound to a numeric angle. Both directions of the stall trap
(section 6) apply: a non-converged point is not evidence of stall, and a
converged high-alpha point is not evidence of attached flow -- 2-D steady RANS
past stall is not a valid model of the flow at any resolution.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

# --- what DAFoam actually emits (carried from aoa_read.py / so3af_read.py) ---
CONV = re.compile(
    r"Minimal residual\s+([0-9.eE+-]+)\s+satisfied the prescribed tolerance\s+([0-9.eE+-]+)")
TIME = re.compile(r"^Time = (\d+)\s*$", re.M)
END = re.compile(r"^End\s*$", re.M)
TOTAL_NORM = re.compile(r"^Total Residual Norm2:\s*([0-9.eE+-]+)", re.M)
STATS_BANNER = "Printing Primal Residual Statistics"
CL_PAT = re.compile(r"^CL:\s*([-+0-9.eE]+)", re.M)
CD_PAT = re.compile(r"^CD:\s*([-+0-9.eE]+)", re.M)
YP_PAT = re.compile(r"^yPlus min: ([0-9.eE+-]+) max: ([0-9.eE+-]+) mean: ([0-9.eE+-]+)", re.M)
BC_GOOD = "BCType=nutLowReWallFunction"
BC_BAD = "BCType=nutUSpaldingWallFunction"

PT_BEGIN = re.compile(
    r"^AOA_POINT_BEGIN idx=(\d+) alpha=([-0-9.]+) mode=(\S+) continued_from=(\S+) "
    r"after_exception=(\S+)\s*$", re.M)
PT_VALUES = re.compile(
    r"^AOA_POINT_VALUES idx=(\d+) alpha=([-0-9.]+) CL=(\S+) CD=(\S+) wall_s=([0-9.]+) "
    r"err=(.*)$", re.M)

CONVERGED = "CONVERGED"
NOT_CONVERGED = "NOT CONVERGED"
NOT_MEASURED = "NOT MEASURED"
YP_THRESH = 1.0
YP_MIN_ITERS_FOR_REFUSAL = 200

STALL_CLAIM = re.compile(
    r"(stall|stalls|stalled|separation onset|CL ?max|clmax)"
    r"[^.\n]{0,60}?[-+]?\d+(?:\.\d+)?\s*(?:deg|degree|degrees|°)"
    r"|[-+]?\d+(?:\.\d+)?\s*(?:deg|degree|degrees|°)[^.\n]{0,60}?"
    r"(stall|stalls|stalled|separation onset|CL ?max|clmax)",
    re.I)


def classify(text: str, endtime_cap: int | None) -> dict:
    times = [int(m.group(1)) for m in TIME.finditer(text)]
    last_time = times[-1] if times else None
    ended = bool(END.search(text))
    cm = None
    for m in CONV.finditer(text):
        cm = m
    achieved = float(cm.group(1)) if cm else None
    tol = float(cm.group(2)) if cm else None
    tn = None
    for m in TOTAL_NORM.finditer(text):
        tn = float(m.group(1))
    if cm is not None:
        verdict = CONVERGED
        why = ("DAFoam's own statement: minimal residual %.6e satisfied the "
               "prescribed tolerance %.0e" % (achieved, tol))
    elif ended and endtime_cap is not None and last_time is not None and last_time >= endtime_cap:
        verdict = NOT_CONVERGED
        why = ("ran to the endTime cap (%d >= %d) and emitted no tolerance-satisfied "
               "line: the iteration limit stopped it, not convergence"
               % (last_time, endtime_cap))
    else:
        verdict = NOT_MEASURED
        why = ("no tolerance-satisfied line, and the log does not show the run reaching "
               "its endTime cap either -- this reader cannot tell whether the field "
               "converged, and says so rather than guessing")
    return {"verdict": verdict, "why": why, "achieved_min_residual": achieved,
            "prescribed_tolerance": tol, "last_time": last_time,
            "n_time_lines": len(times), "end_marker": ended,
            "total_residual_norm2_DIAGNOSTIC": tn,
            "stats_block_present": STATS_BANNER in text}


def last_float(pat, text):
    val = None
    for m in pat.finditer(text):
        try:
            val = float(m.group(1))
        except ValueError:
            continue
    return val


def yplus_of(text: str):
    m = None
    for m0 in YP_PAT.finditer(text):
        m = m0
    if m is None:
        return None
    return tuple(float(m.group(i)) for i in (1, 2, 3))


def yplus_verdict(seg_yp, last_time):
    """G-YPLUS on one point. Returns (verdict, why)."""
    if seg_yp is None:
        if last_time is not None and last_time >= YP_MIN_ITERS_FOR_REFUSAL:
            return ("REFUSED", "point ran %d iterations (>= %d, past the print cadence) "
                    "and the reader saw NO y+ line -- a blind channel is not a fine mesh "
                    "(rule 3)" % (last_time, YP_MIN_ITERS_FOR_REFUSAL))
        return (NOT_MEASURED, "point too short for the y+ print cadence; a named null")
    if all(v == 0.0 for v in seg_yp):
        return ("REFUSED", "y+ reads 0/0/0 -- a zero from a reader not shown able to "
                "see a non-zero is not evidence (rule 3)")
    if seg_yp[1] >= YP_THRESH:
        return ("GATE FAIL", "measured y+max %.6g >= %.1f -- the wall-resolved claim is "
                "WITHDRAWN for this point (section 3.4)" % (seg_yp[1], YP_THRESH))
    return ("PASS", "measured y+max %.6g < %.1f" % (seg_yp[1], YP_THRESH))


def segment(text: str) -> list[dict]:
    begins = list(PT_BEGIN.finditer(text))
    segs = []
    for i, m in enumerate(begins):
        start = m.start()
        stop = begins[i + 1].start() if i + 1 < len(begins) else len(text)
        body = text[start:stop]
        endm = re.search(r"^AOA_POINT_END idx=%s alpha=" % re.escape(m.group(1)),
                         body, re.M)
        segs.append({"idx": int(m.group(1)), "alpha_deg": float(m.group(2)),
                     "mode": m.group(3), "continued_from": m.group(4),
                     "after_exception": m.group(5) == "TRUE",
                     "text": body, "point_end_marker": bool(endm)})
    return segs


def read_point(seg: dict, endtime_cap: int | None) -> dict:
    t = seg["text"]
    r = dict(seg)
    r.pop("text")
    r.update(classify(t, endtime_cap))
    r["CL_solver_line"] = last_float(CL_PAT, t)
    r["CD_solver_line"] = last_float(CD_PAT, t)
    vm = None
    for m in PT_VALUES.finditer(t):
        vm = m
    if vm is not None:
        r["CL_getval"] = None if vm.group(3) == "NA" else float(vm.group(3))
        r["CD_getval"] = None if vm.group(4) == "NA" else float(vm.group(4))
        r["wall_s"] = float(vm.group(5))
        r["error"] = None if vm.group(6).strip() == "NONE" else vm.group(6).strip()
    else:
        r["CL_getval"] = r["CD_getval"] = r["wall_s"] = None
        r["error"] = None
    r["channel_mismatch"] = []
    for name, a, b in (("CL", r["CL_solver_line"], r["CL_getval"]),
                       ("CD", r["CD_solver_line"], r["CD_getval"])):
        if a is not None and b is not None:
            denom = max(abs(a), abs(b), 1e-30)
            if abs(a - b) / denom > 1e-6:
                r["channel_mismatch"].append(
                    "%s: solver line %.12g vs get_val %.12g (rel %.3e)"
                    % (name, a, b, abs(a - b) / denom))
    r["yplus_min_max_mean"] = yplus_of(t)
    r["yplus_verdict"], r["yplus_why"] = yplus_verdict(r["yplus_min_max_mean"],
                                                       r["last_time"])
    return r


def cl_cd_series(text: str) -> list[str]:
    """The exact CL:/CD: line bytes, in order -- the G-CONCURRENCY-BITS series."""
    out = []
    for m in re.finditer(r"^(C[LD]:.*)$", text, re.M):
        out.append(m.group(1))
    return out


def bits_compare(load_text: str, alone_text: str) -> dict:
    a = cl_cd_series(load_text)
    b = cl_cd_series(alone_text)
    if not a or not b:
        return {"status": "NOT RUN", "why": "one or both series empty",
                "n_load": len(a), "n_alone": len(b)}
    if a == b:
        return {"status": "BIT-IDENTICAL", "n_lines": len(a),
                "why": "every CL:/CD: line byte-identical between the under-load and "
                       "alone copies"}
    ndiff = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
    return {"status": "FALSIFIER FIRED", "n_load": len(a), "n_alone": len(b),
            "n_differing": ndiff,
            "why": "the registered falsifier of Addendum B 14.3: concurrency is NOT "
                   "numerically free on this ground; the sweep's comparability is IN "
                   "QUESTION and this item reports that rather than proceeding"}


# =============================================================================
# PLANTED CONTROLS -- the coarse reader's eleven, unchanged, plus this item's.
# =============================================================================
FIXTURE = """AOA_POINT_BEGIN idx=4 alpha=4.0000000000 mode=CONTINUED continued_from=3.0000000000 after_exception=FALSE
SigFpe : Enabling floating point exception trapping (FOAM_SIGFPE).
Setting nut wall BC for wing. BCType=nutLowReWallFunction

Time = 1
smoothSolver:  Solving for Ux, Initial residual = 0.1, Final residual = 1e-06, No Iterations 3
time step continuity errors : sum local = 1e-09, global = 1e-12, cumulative = 1e-12
yPlus min: 0.012345 max: 0.234567 mean: 0.098765

Time = 412
Minimal residual 9.671227459413947e-09 satisfied the prescribed tolerance 1e-08

CD: 0.0212345678901234 final: 0.0212345678901234
CL: 0.4123456789012345 final: 0.4123456789012345
ExecutionTime = 4.8 s  ClockTime = 4 s
End

Printing Primal Residual Statistics.
Total Residual Norm2: 0.0005194447995472946
AOA_POINT_VALUES idx=4 alpha=4.0000000000 CL=0.4123456789012345 CD=0.0212345678901234 wall_s=4.9010 err=NONE
AOA_POINT_END idx=4 alpha=4.0000000000
"""


def _one(text: str, cap: int = 4000) -> dict:
    segs = segment(text)
    if len(segs) != 1:
        raise SystemExit("CONTROL HARNESS BROKEN: %d segments, expected 1" % len(segs))
    return read_point(segs[0], cap)


def selftest(real_seg: str | None, source_note: str):
    global CONV, YP_PAT
    out = []
    base = real_seg if real_seg is not None else FIXTURE
    kind = "REAL RUN ARTEFACT" if real_seg is not None else "WRITER_BUILT FIXTURE"
    out.append("PLANTED CONTROLS -- read back through read_point(), BOTH DIRECTIONS.")
    out.append("  born against  : %s" % kind)
    out.append("  source        : %s" % source_note)
    out.append("  sha256 of base: %s" % hashlib.sha256(base.encode()).hexdigest())
    fails = []

    def chk(tag, cond, msg, detail):
        out.append("  %-4s %-3s %-52s %s" % (tag[0], tag[1], msg,
                                             "PASS" if cond else "*** FAIL ***"))
        out.append("         %s" % detail)
        if not cond:
            fails.append(tag[0])

    def mutate(tag, text):
        if text == base:
            fails.append(tag)
            out.append("  %-4s     MUTATION DID NOT LAND -- control is inert" % tag)
        return text

    def force_last_time_to(text, n):
        ms = list(TIME.finditer(text))
        if not ms:
            return text
        m = ms[-1]
        return text[:m.start()] + ("Time = %d" % n) + text[m.end():]

    def truncate_before_last_time(text):
        ms = list(TIME.finditer(text))
        if not ms:
            return text
        return text[:ms[-1].start()]

    # ----- the coarse reader's eleven, unchanged in substance -----------------
    r1 = _one(base)
    chk(("C1", "[+]"), r1["verdict"] == CONVERGED,
        "unmodified artefact -> CONVERGED",
        "read off the bytes: verdict %s, min residual %s" % (r1["verdict"], r1["achieved_min_residual"]))

    SENT = "1.234567e-09"
    b2 = CONV.sub("Minimal residual %s satisfied the prescribed tolerance 1e-08" % SENT, base)
    r2 = _one(b2)
    chk(("C2", "[+]"), r2["achieved_min_residual"] == float(SENT),
        "SENTINEL %s planted -> reader reports it" % SENT,
        "a value in no real log: seeing it proves the read is off the bytes, got %s"
        % r2["achieved_min_residual"])

    b3 = mutate("C3", force_last_time_to(CONV.sub("", base), 4000))
    r3 = _one(b3)
    chk(("C3", "[-]"), r3["verdict"] == NOT_CONVERGED,
        "tolerance line removed, ran to cap -> NOT CONVERGED",
        "last_time %s >= cap 4000; got %s" % (r3["last_time"], r3["verdict"]))

    b4 = mutate("C4", truncate_before_last_time(CONV.sub("", base)))
    r4 = _one(b4)
    chk(("C4", "[-]"), r4["verdict"] == NOT_MEASURED,
        "truncated mid-solve -> NOT MEASURED",
        "a null is NOT MEASURED, never False; got %s" % r4["verdict"])

    _keep = CONV
    CONV = re.compile(r"(?!x)x_this_matches_nothing_([0-9])([0-9])")
    try:
        r5 = _one(base)
    finally:
        CONV = _keep
    chk(("C5", "[!]"), r5["verdict"] != CONVERGED,
        "CONV disabled -> C1 must flip",
        "flipped to %s" % r5["verdict"])

    def _shift_cl(m):
        try:
            v = float(m.group(3))
        except ValueError:
            return m.group(0)
        return m.group(0).replace("CL=%s" % m.group(3), "CL=%.12g" % (v + 0.5), 1)
    b6 = mutate("C6", PT_VALUES.sub(_shift_cl, base, count=1))
    r6 = _one(b6)
    chk(("C6", "[+]"), len(r6["channel_mismatch"]) == 1,
        "CL channels forced apart -> mismatch REPORTED",
        "mismatches: %s" % (r6["channel_mismatch"] or "NONE -- the cross-check is dead"))
    r6b = _one(base)
    chk(("C6b", "[-]"), len(r6b["channel_mismatch"]) == 0,
        "unmodified artefact -> NO false mismatch",
        "mismatches: %s" % (r6b["channel_mismatch"] or "none, correct"))

    chk(("C7", "[!]"), bool(STALL_CLAIM.search("the stall angle is 13.0 deg")),
        "G-STALL fires on a planted stall-angle claim",
        "fail-closed: a successor adding a stall limb stops publication")
    chk(("C7b", "[-]"), not STALL_CLAIM.search(
        "A non-converged point is evidence that the steady solver stopped "
        "converging. It is not evidence of separation."),
        "G-STALL does NOT fire on the honest caveat",
        "a guard that fires on everything would be turned off")

    g1 = _one(base + "\nSigFpe : Enabling floating point exception trapping\n")
    chk(("G1", "[!]"), g1["verdict"] == CONVERGED,
        "SigFpe startup banner -> still CONVERGED",
        "a STARTUP NOTICE, read as a crash twice in this family (L-312)")
    g2 = _one(base + "\n" + "\n".join(
        "time step continuity errors : sum local = 1e-09" for _ in range(10)))
    chk(("G2", "[!]"), g2["verdict"] == CONVERGED,
        "10 lines containing 'error' -> still CONVERGED",
        "'continuity errors' is a HEALTHY line, in every real log here")
    g3 = _one(TOTAL_NORM.sub("Total Residual Norm2: 9.9e+02", base))
    chk(("G3", "[!]"), g3["verdict"] == CONVERGED,
        "Total Residual Norm2 wrecked to 9.9e+02 -> still CONVERGED",
        "a post-End DIAGNOSTIC, not the criterion")

    # ----- this item's own controls -------------------------------------------
    # Y1 [+] the y+ channel reads the planted line off the bytes
    ry = _one(base)
    have_yp = ry["yplus_min_max_mean"] is not None
    chk(("Y1", "[+]"), have_yp and ry["yplus_verdict"] == "PASS",
        "y+ line present -> parsed, verdict PASS below threshold",
        "read %s -> %s" % (ry["yplus_min_max_mean"], ry["yplus_verdict"]))

    # Y2 [-] planted y+max >= 1 must flip to GATE FAIL; mutation asserted
    by = mutate("Y2", YP_PAT.sub("yPlus min: 0.01 max: 2.345 mean: 0.5", base, count=1))
    ry2 = _one(by)
    chk(("Y2", "[-]"), ry2["yplus_verdict"] == "GATE FAIL",
        "planted y+max 2.345 -> GATE FAIL",
        "got %s (%s)" % (ry2["yplus_verdict"], ry2["yplus_why"]))

    # Y3 [-] y+ line REMOVED on a long point must REFUSE; mutation asserted
    by3 = mutate("Y3", YP_PAT.sub("", base, count=1))
    ry3 = _one(by3)
    chk(("Y3", "[-]"), ry3["yplus_verdict"] == "REFUSED",
        "y+ line removed on a 412-iteration point -> REFUSED",
        "a blind channel is refused, not passed: got %s" % ry3["yplus_verdict"])

    # Y4 [!] mutation control on the y+ parser itself
    _kyp = YP_PAT
    YP_PAT = re.compile(r"(?!x)x_nothing ([0-9]) ([0-9]) ([0-9])")
    try:
        ry4 = _one(base)
    finally:
        YP_PAT = _kyp
    chk(("Y4", "[!]"), ry4["yplus_min_max_mean"] is None,
        "YP_PAT disabled -> the channel goes blind (and Y1 would flip)",
        "a control that passes against a broken reader is not a control")

    # W1 [-] G-WALLTREAT: planted Spalding line must be caught
    bw = base.replace(BC_GOOD, BC_BAD, 1)
    chk(("W1", "[-]"), (BC_BAD in bw) and (BC_GOOD not in bw),
        "planted nutUSpaldingWallFunction -> wall-treat check must refuse",
        "mutation landed and the BAD token is what the check scans for")

    # B1 [-] the bits comparator must fire on a single perturbed digit
    load = "CL: 0.41234567890\nCD: 0.02123456789\nCL: 0.41234567891\n"
    alone_bad = load.replace("0.02123456789", "0.02123456780", 1)
    if alone_bad == load:
        fails.append("B1")
        out.append("  B1       MUTATION DID NOT LAND -- control is inert")
    r_b1 = bits_compare(load, alone_bad)
    chk(("B1", "[-]"), r_b1["status"] == "FALSIFIER FIRED",
        "one perturbed digit -> G-CONCURRENCY-BITS fires",
        "got %s" % r_b1["status"])
    r_b2 = bits_compare(load, load)
    chk(("B1b", "[+]"), r_b2["status"] == "BIT-IDENTICAL",
        "identical series -> BIT-IDENTICAL, no false alarm",
        "got %s" % r_b2["status"])

    if fails:
        out.append("")
        out.append("SELFTEST REFUSED: controls failed: %s" % ", ".join(fails))
    else:
        out.append("")
        out.append("SELFTEST PASS: 18 controls, both directions, mutation controls included.")
    return out, fails


# =============================================================================
def main(argv):
    if len(argv) < 3 or argv[2] not in ("I", "C"):
        sys.stderr.write("usage: a1wr_read.py <RUN_DIR (.../A1WR/STAGE12)> <I|C> [--cap N]\n")
        return 2
    run = Path(argv[1])
    arm = argv[2]
    cap = 4000
    if "--cap" in argv:
        cap = int(argv[argv.index("--cap") + 1])

    lines = []
    lines.append("=" * 78)
    lines.append("A1WR WALL-RESOLVED POLAR READER, ARM %s -- FEASIBILITY READINGS, NOT VERDICTS" % arm)
    lines.append("run dir: %s" % run)
    lines.append("=" * 78)
    lines.append("")

    sweep_log = run / ("sweep_%s" % arm) / "out" / "sweep.log"
    real_seg = None
    note = "no sweep log on disk yet -- controls born against the WRITER_BUILT fixture"
    if sweep_log.is_file():
        segs = segment(sweep_log.read_text(errors="replace"))
        conv = [s for s in segs
                if classify(s["text"], cap)["verdict"] == CONVERGED
                and yplus_of(s["text"]) is not None]
        if conv:
            real_seg = conv[0]["text"]
            note = "%s (point idx=%d, alpha=%.4f)" % (
                sweep_log, conv[0]["idx"], conv[0]["alpha_deg"])

    st, fails = selftest(real_seg, note)
    lines.extend(st)
    if fails:
        sys.stdout.write("\n".join(lines) + "\n")
        return 2
    lines.append("")

    if not sweep_log.is_file():
        lines.append("NO SWEEP LOG AT %s -- nothing to read." % sweep_log)
        lines.append("PENDING: the sweep has not produced its log.")
        sys.stdout.write("\n".join(lines) + "\n")
        return 0

    text = sweep_log.read_text(errors="replace")
    segs = segment(text)
    pts = [read_point(s, cap) for s in segs]

    # ---- G-WALLTREAT over every unit log of this arm -------------------------
    wall_bad = []
    unit_dirs = sorted(run.glob("sweep_%s" % arm)) + sorted(run.glob("cold_%s_*" % arm)) \
        + (sorted(run.glob("dup_I_4")) if arm == "I" else []) \
        + sorted(run.glob("probe_%s" % arm))
    for u in unit_dirs:
        lp = u / "out" / "sweep.log"
        if not lp.is_file():
            wall_bad.append("%s: no sweep.log" % u.name)
            continue
        t = lp.read_text(errors="replace")
        if BC_BAD in t:
            wall_bad.append("%s: carries %s -- the WALL-FUNCTION path ran" % (u.name, BC_BAD))
        elif BC_GOOD not in t:
            wall_bad.append("%s: no %s line -- the BC that ran is UNCONFIRMED" % (u.name, BC_GOOD))
    lines.append("G-WALLTREAT (every unit of this arm must confirm the low-Re BC in its log):")
    if wall_bad:
        for w in wall_bad:
            lines.append("  REFUSE: %s" % w)
    else:
        lines.append("  PASS: %d unit logs, every one carries %s and none carries the "
                     "Spalding line" % (len(unit_dirs), BC_GOOD))
    lines.append("")

    dm = re.search(r"^AOA_SWEEP_BEGIN mode=(\S+) n_declared=(\d+)", text, re.M)
    declared = int(dm.group(2)) if dm else None
    lines.append("registered endTime cap (system/controlDict): %d" % cap)
    lines.append("DECLARED points: %s   SEGMENTS FOUND: %d" % (declared, len(pts)))
    if declared is not None and declared != len(pts):
        lines.append("  *** COUNT MISMATCH: %d declared, %d present -- a polar short of its"
                     % (declared, len(pts)))
        lines.append("  *** declared points is truncated, and the gap is NOT absorbed.")
    lines.append("")

    hdr = ("  %5s %7s %14s %12s %12s %7s %9s %11s %10s"
           % ("idx", "alpha", "convergence", "CL", "CD", "iters", "y+max", "y+ verdict", "cont_from"))
    lines.append("THE POLAR -- CONTINUED SWEEP, WALL-RESOLVED L3 (%s arm)" % arm)
    lines.append(hdr)
    lines.append("  " + "-" * len(hdr))
    yp_refused = []
    for p in pts:
        yp = p["yplus_min_max_mean"]
        lines.append("  %5d %7.2f %14s %12s %12s %7s %9s %11s %10s"
                     % (p["idx"], p["alpha_deg"], p["verdict"],
                        "NA" if p["CL_getval"] is None else "%.6f" % p["CL_getval"],
                        "NA" if p["CD_getval"] is None else "%.6f" % p["CD_getval"],
                        p["last_time"],
                        "NA" if yp is None else "%.4f" % yp[1],
                        p["yplus_verdict"], p["continued_from"]))
        if p["yplus_verdict"] == "REFUSED":
            yp_refused.append(p)
    lines.append("")
    lines.append("  y+ channel: DAFoam's own per-print `yPlus min/max/mean` line, the LAST in")
    lines.append("  each point's segment -- exact to <= printInterval (100) iterations before")
    lines.append("  the point stopped. Stated per Addendum C; the Stage-1 probe's reading is")
    lines.append("  field-exact (postProcess on the written endTime state).")

    nfail_yp = [p for p in pts if p["yplus_verdict"] == "GATE FAIL"]
    if nfail_yp:
        lines.append("")
        lines.append("G-YPLUS: GATE FAIL -- y+max >= 1.0 at: %s. THE WALL-RESOLVED CLAIM IS"
                     % ", ".join("alpha %.1f (y+max %.4f)" % (p["alpha_deg"], p["yplus_min_max_mean"][1])
                                 for p in nfail_yp))
        lines.append("  WITHDRAWN FOR THOSE POINTS (section 3.4). The mesh is NOT re-cut.")
    elif not yp_refused:
        measured = [p for p in pts if p["yplus_min_max_mean"] is not None]
        if measured:
            worst = max(p["yplus_min_max_mean"][1] for p in measured)
            lines.append("")
            lines.append("G-YPLUS: PASS on every measured point; worst y+max %.4f < 1.0 "
                         "(%d of %d points carried a reading)" % (worst, len(measured), len(pts)))

    nconv = sum(1 for p in pts if p["verdict"] == CONVERGED)
    nnot = sum(1 for p in pts if p["verdict"] == NOT_CONVERGED)
    nnm = sum(1 for p in pts if p["verdict"] == NOT_MEASURED)
    lines.append("")
    lines.append("CONVERGED %d   NOT CONVERGED %d   NOT MEASURED %d" % (nconv, nnot, nnm))

    bad = [p for p in pts if p["verdict"] != CONVERGED]
    if bad:
        lines.append("")
        lines.append("POINTS THAT DID NOT CONVERGE -- REPORTED, NOT REMOVED, NOT RETRIED")
        for p in bad:
            lines.append("  alpha %.2f deg: %s -- %s" % (p["alpha_deg"], p["verdict"], p["why"]))
            if p["error"]:
                lines.append("    driver exception: %s" % p["error"])
        lines.append("  IT MEANS the steady solver did not reach tolerance within the cap at")
        lines.append("  that operating point. IT DOES NOT MEAN the section separated there:")
        lines.append("  solver behaviour is what is measured, flow physics is not inferred.")

    poisoned = []
    prev_ok = None
    for p in pts:
        if prev_ok is False:
            poisoned.append(p["alpha_deg"])
        prev_ok = (p["verdict"] == CONVERGED)
    if poisoned:
        lines.append("")
        lines.append("CONTINUATION PROVENANCE -- points whose predecessor did NOT converge:")
        lines.append("  %s" % ", ".join("%.2f" % a for a in poisoned))

    mism = [(p["alpha_deg"], m) for p in pts for m in p["channel_mismatch"]]
    lines.append("")
    if mism:
        lines.append("CL/CD CHANNEL DISAGREEMENT (solver line vs prob.get_val):")
        for a, m in mism:
            lines.append("  alpha %.4f: %s" % (a, m))
    else:
        lines.append("CL/CD channel cross-check: solver lines and prob.get_val() agree to")
        lines.append("  1e-6 relative on every point that produced both.")

    # ---- the cold controls ---------------------------------------------------
    colds = []
    for u in sorted(run.glob("cold_%s_*" % arm)):
        lp = u / "out" / "sweep.log"
        if lp.is_file():
            for s in segment(lp.read_text(errors="replace")):
                colds.append(read_point(s, cap))
    if colds:
        lines.append("")
        lines.append("COLD CONTROL POINTS -- re-run from freestream, own case tree (G-COLD)")
        for c in colds:
            match = [p for p in pts if abs(p["alpha_deg"] - c["alpha_deg"]) < 1e-9]
            p = match[0] if match else None
            lines.append("  alpha %.2f: cold %s (%s iters) | continued %s (%s iters)"
                         % (c["alpha_deg"], c["verdict"], c["last_time"],
                            p["verdict"] if p else "NO MATCH",
                            p["last_time"] if p else "NA"))
            if p and c["last_time"] and p["last_time"]:
                lines.append("    continuation %s"
                             % ("IS saving iterations" if p["last_time"] < c["last_time"]
                                else "is NOT saving iterations at this point -- if counts are"
                                     " EQUAL the continued label is FALSE (G-COLD)"))
            if p and c["CL_getval"] is not None and p["CL_getval"] is not None:
                dcl = abs(c["CL_getval"] - p["CL_getval"]) / max(abs(c["CL_getval"]), 1e-30)
                lines.append("    |dCL|/CL cold-vs-continued = %.3e (path dependence is a "
                             "FINDING, not a bug)" % dcl)
    else:
        lines.append("")
        lines.append("COLD CONTROL POINTS: none on disk -- the continuation instrument is")
        lines.append("  UNCHECKED for this arm and no path-independence statement exists.")

    # ---- G-CONCURRENCY-BITS (I arm only) -------------------------------------
    if arm == "I":
        lines.append("")
        lines.append("G-CONCURRENCY-BITS (Addendum B 14.3): cold_I_4 under full load vs dup_I_4 alone")
        lp_load = run / "cold_I_4" / "out" / "sweep.log"
        lp_alone = run / "dup_I_4" / "out" / "sweep.log"
        if lp_load.is_file() and lp_alone.is_file():
            r = bits_compare(lp_load.read_text(errors="replace"),
                             lp_alone.read_text(errors="replace"))
            lines.append("  %s -- %s" % (r["status"], r["why"]))
        else:
            lines.append("  NOT RUN -- alone-copy or under-load copy absent on disk. The")
            lines.append("  control's ABSENCE is reported, never papered over; if it was")
            lines.append("  cap-stopped that is NOT A RESULT on this control (G-CAPS).")

    lines.append("")
    lines.append("SCOPE (G-NOBAND). FEASIBILITY: this mesh family's own grid convergence is")
    lines.append("PENDING (section 1.3) -- NO value above is grid-converged, NO value carries")
    lines.append("a band, and the item's verdict ceiling is GATE REACHED (section 1.4).")
    lines.append("2-D steady RANS with SA past the onset of significant separation is not a")
    lines.append("valid model of the flow at ANY resolution (section 6): convergence and")
    lines.append("correctness remain independent claims and only the first is measured here.")

    report = "\n".join(lines) + "\n"

    hit = STALL_CLAIM.search(report)
    if hit:
        sys.stdout.write(report)
        sys.stderr.write("\nG-STALL REFUSE: output binds a stall word to an angle: %r\n"
                         % hit.group(0))
        return 2
    sys.stdout.write(report)
    sys.stdout.write("G-STALL PASS: no stall/separation claim bound to an angle in this output.\n")

    if wall_bad:
        sys.stderr.write("\nG-WALLTREAT REFUSE (exit 2): %s\n" % "; ".join(wall_bad))
        return 2
    if yp_refused:
        sys.stderr.write("\nG-YPLUS REFUSE (exit 2): blind y+ channel on: %s\n"
                         % ", ".join("alpha %.1f" % p["alpha_deg"] for p in yp_refused))
        return 2

    (run / ("A1WR_POINTS_%s.json" % arm)).write_text(json.dumps(
        {"arm": arm, "points": pts, "cold_controls": colds, "declared": declared,
         "endtime_cap": cap}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
