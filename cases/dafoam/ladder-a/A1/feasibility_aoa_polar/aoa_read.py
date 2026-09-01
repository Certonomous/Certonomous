#!/usr/bin/env python3
r"""AOA POLAR -- the reader.  FEASIBILITY rung: it produces READINGS, not verdicts.

=============================================================================
THE ONE THING THIS READER IS BUILT TO BE INCAPABLE OF
=============================================================================
**IT CANNOT REPORT A STALL ANGLE, AND IT CANNOT BE MADE TO.**

A point that does not converge is evidence that *the steady solver stopped
converging*.  It is NOT evidence of stall.  Those are two different claims and
conflating them throws the finding away.  So:

  * no function here computes a stall angle, a CLmax, or a separation onset;
  * `G-STALL` scans this reader's OWN FINISHED OUTPUT for a stall-word bound to
    a numeric angle and **REFUSES (exit 2)** if it finds one.  It is fail-closed:
    if a successor adds a stall limb, the reader stops publishing rather than
    publishes the inference.  Control C7 plants exactly such a string and proves
    the guard fires.

**AND THE MIRROR OF THAT TRAP, WHICH IS THE HALF USUALLY LEFT OUT:** a point at
high alpha that DOES converge is not thereby trustworthy either.  This is a
4,032-cell wall-function mesh (measured y+ 16.7-92.4 on this family).  It cannot
resolve a separated boundary layer at any alpha.  Convergence and correctness
are independent here, and this reader reports convergence ONLY.

=============================================================================
THE CONVERGENCE CRITERION, REGISTERED IN ADVANCE
=============================================================================
DAFoam's own statement, and nothing else:

    Minimal residual <r> satisfied the prescribed tolerance <tol>

emitted BEFORE the endTime cap.  `classify()` below is carried across from
`feasibility_SO3a_alpha/so3af_read.py`, whose controls were driven on real run
bytes.  **That file's FIRST version got this wrong** -- it grepped for a string
DAFoam never prints ("Primal solution converged"), reported `converged=False` on
three solves that had all reached 1e-8, and the archived table said so.  The
repaired reader re-run on the same bytes returns CONVERGED 3/3.  That is why the
criterion here is a quoted DAFoam string with a mutation control on it (C5) and
not a phrase anybody remembered.

  ABSENCE OF THE LINE IS NOT AUTOMATICALLY NON-CONVERGENCE:
    line present                         -> CONVERGED
    line absent AND last time >= cap     -> NOT CONVERGED  (the cap stopped it)
    line absent AND cap not reached      -> NOT MEASURED   (a named null)
  A null is NOT MEASURED, never False.  A False here would be a silent
  downgrade of "I could not tell" into "it failed".

=============================================================================
GUARDS THAT EXIST BECAUSE THIS FAMILY PAID FOR THEM
=============================================================================
 G1 `SigFpe : Enabling floating point exception trapping` is a STARTUP NOTICE.
    This family read it as a crash twice (L-312).
 G2 The word "error" is in every healthy log -- `Time step continuity errors`.
 G3 `Total Residual Norm2` is a post-`End` DIAGNOSTIC, not the criterion.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

# --- what DAFoam actually emits (carried from so3af_read.py) -----------------
CONV = re.compile(
    r"Minimal residual\s+([0-9.eE+-]+)\s+satisfied the prescribed tolerance\s+([0-9.eE+-]+)")
TIME = re.compile(r"^Time = (\d+)\s*$", re.M)
END = re.compile(r"^End\s*$", re.M)
TOTAL_NORM = re.compile(r"^Total Residual Norm2:\s*([0-9.eE+-]+)", re.M)
STATS_BANNER = "Printing Primal Residual Statistics"
CL_PAT = re.compile(r"^CL:\s*([-+0-9.eE]+)", re.M)
CD_PAT = re.compile(r"^CD:\s*([-+0-9.eE]+)", re.M)

# --- this item's own per-point markers ---------------------------------------
PT_BEGIN = re.compile(
    r"^AOA_POINT_BEGIN idx=(\d+) alpha=([-0-9.]+) mode=(\S+) continued_from=(\S+) "
    r"after_exception=(\S+)\s*$", re.M)
PT_VALUES = re.compile(
    r"^AOA_POINT_VALUES idx=(\d+) alpha=([-0-9.]+) CL=(\S+) CD=(\S+) wall_s=([0-9.]+) "
    r"err=(.*)$", re.M)

CONVERGED = "CONVERGED"
NOT_CONVERGED = "NOT CONVERGED"
NOT_MEASURED = "NOT MEASURED"

# G-STALL: a stall/separation word bound to a numeric angle. Fail-closed.
STALL_CLAIM = re.compile(
    r"(stall|stalls|stalled|separation onset|CL ?max|clmax)"
    r"[^.\n]{0,60}?[-+]?\d+(?:\.\d+)?\s*(?:deg|degree|degrees|°)"
    r"|[-+]?\d+(?:\.\d+)?\s*(?:deg|degree|degrees|°)[^.\n]{0,60}?"
    r"(stall|stalls|stalled|separation onset|CL ?max|clmax)",
    re.I)


def classify(text: str, endtime_cap: int | None) -> dict:
    """The convergence reading. NOT MEASURED for a genuine null."""
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


def last_float(pat: re.Pattern, text: str):
    val = None
    for m in pat.finditer(text):
        try:
            val = float(m.group(1))
        except ValueError:
            continue
    return val


def segment(text: str) -> list[dict]:
    """Split a sweep log into per-point segments on this item's own markers.

    A point whose BEGIN is present but whose END never arrived is kept and
    marked truncated -- it is not dropped.  A dropped point is the omission
    this whole item is built to refuse.
    """
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
    """One point, read through both CL/CD channels and the convergence channel."""
    t = seg["text"]
    r = dict(seg)
    r.pop("text")
    r.update(classify(t, endtime_cap))

    # channel A: the solver's own printed CL:/CD: lines inside this segment
    r["CL_solver_line"] = last_float(CL_PAT, t)
    r["CD_solver_line"] = last_float(CD_PAT, t)

    # channel B: the driver's prob.get_val(), printed on AOA_POINT_VALUES
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

    # THE CROSS-CHECK. Two independent channels on the same quantity; a
    # disagreement is REPORTED, never resolved silently in favour of one.
    r["channel_mismatch"] = []
    for name, a, b in (("CL", r["CL_solver_line"], r["CL_getval"]),
                       ("CD", r["CD_solver_line"], r["CD_getval"])):
        if a is not None and b is not None:
            denom = max(abs(a), abs(b), 1e-30)
            if abs(a - b) / denom > 1e-6:
                r["channel_mismatch"].append(
                    "%s: solver line %.12g vs get_val %.12g (rel %.3e)"
                    % (name, a, b, abs(a - b) / denom))
    return r


# =============================================================================
# PLANTED CONTROLS -- on disk where a real artefact exists, read back THROUGH
# read_point()/classify(), BOTH DIRECTIONS, refusing at exit 2.
# =============================================================================
FIXTURE = """AOA_POINT_BEGIN idx=4 alpha=4.0000000000 mode=CONTINUED continued_from=3.0000000000 after_exception=FALSE
SigFpe : Enabling floating point exception trapping (FOAM_SIGFPE).

Time = 1
smoothSolver:  Solving for Ux, Initial residual = 0.1, Final residual = 1e-06, No Iterations 3
time step continuity errors : sum local = 1e-09, global = 1e-12, cumulative = 1e-12

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


def _one(text: str, cap: int = 1000) -> dict:
    segs = segment(text)
    if len(segs) != 1:
        raise SystemExit("CONTROL HARNESS BROKEN: %d segments, expected 1" % len(segs))
    return read_point(segs[0], cap)


def selftest(real_seg: str | None, source_note: str) -> list[str]:
    global CONV          # C5 rebinds it to drive the mutation control
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

    # C1 [+] the unmodified artefact must read CONVERGED
    r1 = _one(base)
    chk(("C1", "[+]"), r1["verdict"] == CONVERGED,
        "unmodified artefact -> CONVERGED",
        "read off the bytes: verdict %s, min residual %s" % (r1["verdict"], r1["achieved_min_residual"]))

    # C2 [+] a sentinel that exists in NO real log -- proves the read is off the bytes
    SENT = "1.234567e-09"
    b2 = CONV.sub("Minimal residual %s satisfied the prescribed tolerance 1e-08" % SENT, base)
    r2 = _one(b2)
    chk(("C2", "[+]"), r2["achieved_min_residual"] == float(SENT),
        "SENTINEL %s planted -> reader reports it" % SENT,
        "a value in no real log: seeing it proves the read is off the bytes, got %s"
        % r2["achieved_min_residual"])

    # C3 [-] THE ZERO-PASSING CONTROL. The non-convergence channel must be shown
    #        able to FIRE, or a polar of all-CONVERGED proves nothing.
    b3 = CONV.sub("", base).replace("Time = 412", "Time = 1000")
    r3 = _one(b3)
    chk(("C3", "[-]"), r3["verdict"] == NOT_CONVERGED,
        "tolerance line removed, ran to cap -> NOT CONVERGED",
        "last_time %s >= cap 1000; got %s" % (r3["last_time"], r3["verdict"]))

    # C4 [-] a genuine null must be NAMED, not turned into a failure
    b4 = base.split("Time = 412")[0] + "\nAOA_POINT_END idx=4 alpha=4.0000000000\n"
    r4 = _one(b4)
    chk(("C4", "[-]"), r4["verdict"] == NOT_MEASURED,
        "truncated mid-solve -> NOT MEASURED",
        "a null is NOT MEASURED, never False; got %s" % r4["verdict"])

    # C5 [!] MUTATION CONTROL. Disable CONV and C1 must flip. A control that
    #        still passes against a broken reader is not a control.
    _keep = CONV
    CONV = re.compile(r"(?!x)x_this_matches_nothing_([0-9])([0-9])")
    try:
        r5 = _one(base)
    finally:
        CONV = _keep
    chk(("C5", "[!]"), r5["verdict"] != CONVERGED,
        "CONV disabled -> C1 must flip",
        "flipped to %s" % r5["verdict"])

    # C6 [+] the two CL/CD channels must be able to DISAGREE audibly
    b6 = base.replace("CL=0.4123456789012345", "CL=0.9999999999999999")
    r6 = _one(b6)
    chk(("C6", "[+]"), len(r6["channel_mismatch"]) == 1,
        "CL channels forced apart -> mismatch REPORTED",
        "mismatches: %s" % (r6["channel_mismatch"] or "NONE -- the cross-check is dead"))
    r6b = _one(base)
    chk(("C6b", "[-]"), len(r6b["channel_mismatch"]) == 0,
        "unmodified artefact -> NO false mismatch",
        "mismatches: %s" % (r6b["channel_mismatch"] or "none, correct"))

    # C7 [!] G-STALL must fire on a planted stall claim, and must NOT fire on
    #        this reader's own honest prose.
    chk(("C7", "[!]"), bool(STALL_CLAIM.search("the stall angle is 13.0 deg")),
        "G-STALL fires on a planted stall-angle claim",
        "fail-closed: a successor adding a stall limb stops publication")
    chk(("C7b", "[-]"), not STALL_CLAIM.search(
        "A non-converged point is evidence that the steady solver stopped "
        "converging. It is not evidence of separation."),
        "G-STALL does NOT fire on the honest caveat",
        "a guard that fires on everything would be turned off")

    # G1/G2/G3 -- benign text must not move the verdict
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

    if fails:
        out.append("")
        out.append("SELFTEST REFUSED: controls failed: %s" % ", ".join(fails))
    else:
        out.append("")
        out.append("SELFTEST PASS: 11 controls, both directions, mutation control included.")
    return out, fails


# =============================================================================
def main(argv):
    if len(argv) < 2:
        sys.stderr.write("usage: aoa_read.py <RUN_ROOT> [--cap N]\n")
        return 2
    root = Path(argv[1])
    cap = 1000
    if "--cap" in argv:
        cap = int(argv[argv.index("--cap") + 1])

    lines = []
    lines.append("=" * 78)
    lines.append("AOA POLAR READER -- FEASIBILITY READINGS, NOT VERDICTS")
    lines.append("root: %s" % root)
    lines.append("=" * 78)
    lines.append("")

    sweep_log = root / "out" / "sweep.log"
    real_seg = None
    note = "no sweep log on disk yet -- controls born against the WRITER_BUILT fixture"
    if sweep_log.is_file():
        segs = segment(sweep_log.read_text(errors="replace"))
        conv = [s for s in segs if classify(s["text"], cap)["verdict"] == CONVERGED]
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

    # cold control points, each its own single-point process/log
    colds = []
    for p in sorted((root / "out").glob("cold_alpha_*.log")):
        cs = segment(p.read_text(errors="replace"))
        colds.extend(read_point(s, cap) for s in cs)

    dm = re.search(r"^AOA_SWEEP_BEGIN mode=(\S+) n_declared=(\d+)", text, re.M)
    declared = int(dm.group(2)) if dm else None

    lines.append("registered endTime cap (system/controlDict): %d" % cap)
    lines.append("  For a DAFoam steady primal this is an UPPER BOUND on SIMPLE iterations,")
    lines.append("  not a target. Stopping BELOW it is the success signature.")
    lines.append("")
    lines.append("DECLARED points: %s   SEGMENTS FOUND: %d   COLD CONTROLS: %d"
                 % (declared, len(pts), len(colds)))
    if declared is not None and declared != len(pts):
        lines.append("  *** COUNT MISMATCH: %d declared, %d present. The missing points are"
                     % (declared, len(pts)))
        lines.append("  *** NOT absorbed -- a polar short of its declared points is truncated.")
    lines.append("")

    hdr = ("  %5s %9s %14s %12s %12s %8s %9s %10s"
           % ("idx", "alpha", "convergence", "CL", "CD", "iters", "wall_s", "cont_from"))
    lines.append("THE POLAR -- CONTINUED SWEEP")
    lines.append(hdr)
    lines.append("  " + "-" * len(hdr))
    for p in pts:
        lines.append("  %5d %9.4f %14s %12s %12s %8s %9s %10s"
                     % (p["idx"], p["alpha_deg"], p["verdict"],
                        "NA" if p["CL_getval"] is None else "%.6f" % p["CL_getval"],
                        "NA" if p["CD_getval"] is None else "%.6f" % p["CD_getval"],
                        p["last_time"], "NA" if p["wall_s"] is None else "%.2f" % p["wall_s"],
                        p["continued_from"]))
    lines.append("")

    nconv = sum(1 for p in pts if p["verdict"] == CONVERGED)
    nnot = sum(1 for p in pts if p["verdict"] == NOT_CONVERGED)
    nnm = sum(1 for p in pts if p["verdict"] == NOT_MEASURED)
    lines.append("CONVERGED %d   NOT CONVERGED %d   NOT MEASURED %d" % (nconv, nnot, nnm))

    bad = [p for p in pts if p["verdict"] != CONVERGED]
    if bad:
        lines.append("")
        lines.append("POINTS THAT DID NOT CONVERGE -- REPORTED, NOT REMOVED, NOT RETRIED")
        for p in bad:
            lines.append("  alpha %.4f deg: %s" % (p["alpha_deg"], p["verdict"]))
            lines.append("    basis: %s" % p["why"])
            lines.append("    last time %s, End marker %s, Total Residual Norm2 (DIAGNOSTIC) %s"
                         % (p["last_time"], p["end_marker"],
                            p["total_residual_norm2_DIAGNOSTIC"]))
            if p["error"]:
                lines.append("    driver exception: %s" % p["error"])
        lines.append("")
        lines.append("  WHAT THIS DOES AND DOES NOT MEAN")
        lines.append("    IT MEANS: the steady solver did not reach the registered tolerance")
        lines.append("      within the iteration cap at this operating point.")
        lines.append("    IT DOES NOT MEAN the section separated there. This reader reports")
        lines.append("      solver behaviour and does not infer flow physics from it; the two")
        lines.append("      are different claims and only the first is measured here.")

    # continuation provenance: a point continued from a non-converged predecessor
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
        lines.append("  These continued from a state that had not met the tolerance. They are")
        lines.append("  NOT comparable with points continued from a converged predecessor,")
        lines.append("  and that is a property of the chain, not a defect in the point.")

    mism = [(p["alpha_deg"], m) for p in pts for m in p["channel_mismatch"]]
    lines.append("")
    if mism:
        lines.append("CL/CD CHANNEL DISAGREEMENT (solver line vs prob.get_val):")
        for a, m in mism:
            lines.append("  alpha %.4f: %s" % (a, m))
    else:
        lines.append("CL/CD channel cross-check: the solver's own printed lines and")
        lines.append("  prob.get_val() agree to 1e-6 relative on every point that produced both.")

    # --- the cold controls: instrument check AND path-dependence check --------
    if colds:
        lines.append("")
        lines.append("COLD CONTROL POINTS -- re-run from freestream, 0/ reset from 0.orig")
        lines.append("  %9s %14s %12s %12s %8s | %14s %12s %12s %8s"
                     % ("alpha", "cold conv", "cold CL", "cold CD", "cold it",
                        "cont conv", "cont CL", "cont CD", "cont it"))
        for c in colds:
            match = [p for p in pts if abs(p["alpha_deg"] - c["alpha_deg"]) < 1e-9]
            p = match[0] if match else None
            lines.append("  %9.4f %14s %12s %12s %8s | %14s %12s %12s %8s"
                         % (c["alpha_deg"], c["verdict"],
                            "NA" if c["CL_getval"] is None else "%.6f" % c["CL_getval"],
                            "NA" if c["CD_getval"] is None else "%.6f" % c["CD_getval"],
                            c["last_time"],
                            p["verdict"] if p else "NO MATCH",
                            "NA" if not p or p["CL_getval"] is None else "%.6f" % p["CL_getval"],
                            "NA" if not p or p["CD_getval"] is None else "%.6f" % p["CD_getval"],
                            p["last_time"] if p else "NA"))
        lines.append("")
        lines.append("  WHAT THE COLD CONTROLS TEST -- TWO THINGS, REGISTERED IN ADVANCE:")
        lines.append("   (1) IS THE CONTINUATION INSTRUMENT LIVE? If continuation is working,")
        lines.append("       the continued point reaches tolerance in FEWER iterations than the")
        lines.append("       cold one at the same alpha. Equal iteration counts would mean the")
        lines.append("       warm start is not actually being inherited.")
        lines.append("   (2) IS THE ANSWER PATH-DEPENDENT? Agreement in CL/CD means the")
        lines.append("       continued polar is reproducible from freestream at that alpha.")
        lines.append("       DISAGREEMENT IS A FINDING ABOUT PATH DEPENDENCE -- it is not a bug")
        lines.append("       to be tuned away, and neither branch is preferred over the other.")
        for c in colds:
            match = [p for p in pts if abs(p["alpha_deg"] - c["alpha_deg"]) < 1e-9]
            if not match:
                continue
            p = match[0]
            if c["CL_getval"] is not None and p["CL_getval"] is not None:
                dcl = abs(c["CL_getval"] - p["CL_getval"]) / max(abs(c["CL_getval"]), 1e-30)
                dcd = (abs(c["CD_getval"] - p["CD_getval"]) / max(abs(c["CD_getval"]), 1e-30)
                       if c["CD_getval"] is not None and p["CD_getval"] is not None else None)
                lines.append("    alpha %.4f: |dCL|/CL = %.3e   |dCD|/CD = %s"
                             % (c["alpha_deg"], dcl,
                                "NA" if dcd is None else "%.3e" % dcd))
            if c["last_time"] and p["last_time"]:
                lines.append("      iterations cold %s vs continued %s -> continuation %s"
                             % (c["last_time"], p["last_time"],
                                "IS saving iterations" if p["last_time"] < c["last_time"]
                                else "is NOT saving iterations at this point"))
    else:
        lines.append("")
        lines.append("COLD CONTROL POINTS: none on disk. The continuation instrument is")
        lines.append("  therefore UNCHECKED, and no path-independence statement is available.")

    # --- lift slope: an indicator, explicitly not a separation measurement ----
    ok = [p for p in pts if p["verdict"] == CONVERGED and p["CL_getval"] is not None]
    if len(ok) >= 3:
        lines.append("")
        lines.append("LIFT-CURVE SLOPE BETWEEN ADJACENT CONVERGED POINTS (indicator only)")
        lines.append("  thin-airfoil reference 2*pi/rad = 0.109662 per degree")
        for a, b in zip(ok, ok[1:]):
            da = b["alpha_deg"] - a["alpha_deg"]
            if da > 0:
                s = (b["CL_getval"] - a["CL_getval"]) / da
                lines.append("  %6.2f -> %6.2f deg: dCL/dalpha = %9.6f  (%5.1f%% of thin-airfoil)"
                             % (a["alpha_deg"], b["alpha_deg"], s, 100 * s / 0.109662))
        lines.append("")
        lines.append("  READ THIS AS AN INDICATOR AND NOTHING MORE. A falling slope is")
        lines.append("  consistent with the lift going nonlinear. It is NOT a separation")
        lines.append("  measurement: that needs wall shear, which this rung does not buy, on")
        lines.append("  a mesh that could resolve it, which this 4,032-cell wall-function grid")
        lines.append("  is not. No angle is named here and none may be derived from this table.")

    lines.append("")
    lines.append("SCOPE. FEASIBILITY: no grid triple exists for these points, so nothing here")
    lines.append("is a graded result under Sanaa's convergence-prerequisite doctrine. A band")
    lines.append("attaches to this polar only when the wing convergence ladder lands.")

    report = "\n".join(lines) + "\n"

    # ---- G-STALL, on this reader's OWN FINISHED OUTPUT, fail-closed ---------
    hit = STALL_CLAIM.search(report)
    if hit:
        sys.stdout.write(report)
        sys.stderr.write(
            "\nG-STALL REFUSE: this reader's output binds a stall/separation word to a\n"
            "numeric angle -- %r. A stall angle may not be inferred from solver\n"
            "convergence behaviour, and this reader refuses to publish one.\n"
            % hit.group(0))
        return 2
    sys.stdout.write(report)
    sys.stdout.write("G-STALL PASS: no stall/separation claim bound to an angle in this output.\n")

    (root / "AOA_POINTS.json").write_text(json.dumps(
        {"points": pts, "cold_controls": colds, "declared": declared,
         "endtime_cap": cap}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
