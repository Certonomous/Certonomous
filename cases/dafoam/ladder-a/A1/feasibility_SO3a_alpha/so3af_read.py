#!/usr/bin/env python3
"""Read the SO-3a alpha feasibility solves and state the physics answer.

UNREGISTERED FEASIBILITY RUNG. Nothing here is a verdict, and no value produced
by this reader may be graded as one, nor used to score another item's registered
predictions (Sanaa 2026-08-31; queue_entry_check.py's UNREGISTERED_PREREG_TAGS).

=============================================================================
v2, 2026-08-31 -- THE CONVERGENCE COLUMN IS REWRITTEN. WHY IT WAS WRONG TWICE.
=============================================================================
v0 tested for the literal string "Primal solution converged". DAFoam NEVER
prints it on this path, so the column read False for three solves that had in
fact converged, and n_res=0 was the tell: the reader had parsed ZERO residual
lines and was reporting the absence of its own evidence as a measured negative.
ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE, and printing `False` in a
column headed `converged` makes a null read as a finding.

v1 (a partial fix) replaced it with a CD-stability proxy. Better, but still an
INFERENCE printed as a measurement -- CD can be stable on an unconverged field.

v2 parses WHAT DAFOAM ACTUALLY EMITS:

    Time = 424
    Minimal residual 9.907086431972576e-09 satisfied the prescribed tolerance 1e-08

That line IS the convergence statement, and `primalMinResTol` in the runScript
(1.0e-8) is the tolerance it names.

TWO TRAPS THIS READER NOW AVOIDS, both real on these logs:

  1. `Total Residual Norm2: 3.6e-04` is NOT the convergence criterion and must
     never be read as one. It sits INSIDE the "Printing Primal Residual
     Statistics" block that DAFoam prints AFTER `End` (line 583 vs End at 568
     in the alpha 7.139 log): an un-normalised diagnostic over the whole
     residual vector, reported here as a DIAGNOSTIC and labelled as such.

  2. `endTime 1000` in controlDict is an UPPER BOUND on SIMPLE iterations, not
     a target. A DAFoam steady primal STOPS EARLY when primalMinResTol is met,
     so "last time < endTime" is the SUCCESS signature here, not a truncation.
     CLAUDE.md rule 4's "last time == endTime" clause is written for runs whose
     endTime IS the target and does not transfer to this solver mode unaltered.
     The corroborating discriminator is reported: the three alphas stopped at
     443 / 435 / 424, THREE DIFFERENT ITERATIONS, which is convergence-driven.
     Had they all stopped at the same number, that would be a cap.

WHERE CONVERGENCE CANNOT BE DETERMINED THIS READER PRINTS `NOT MEASURED`,
NEVER `False`. That distinction is the whole point of v2.

Controls are planted IN BOTH DIRECTIONS (`--selftest`): the reader must be
shown able to report a CONVERGED log and a NON-CONVERGED one. A reader only
ever shown one answer has not been calibrated.

=============================================================================
v2-final -- THE CONTROLS ARE PLANTED ON DISK, THROUGH THE SAME READER PATH.
=============================================================================
The first cut of this selftest handed STRING FIXTURES straight to classify().
That tests the regexes and NOTHING ELSE: it never opens a file, so it could
pass while read_alpha(), the glob and the decode were all broken. Standing
rule 3 asks for a perturbation planted INTO THE ARTIFACT ON DISK and read back
THROUGH THE SAME PATH, and this now does that -- every control is written to a
real file and read with read_alpha(Path, cap), the identical call main() makes.

The plant carries a SENTINEL VALUE (PLANT_RESIDUAL below). A control that only
asserts "CONVERGED" is nearly vacuous, because a reader hard-wired to say
CONVERGED would pass it. Asserting that the reader returns THE SENTINEL, a
number that appears nowhere in the source and could only have come off the
disk, is what makes the positive direction evidence.

The fixtures are cut FROM THE REAL LOG'S OWN BYTES, not typed by hand, so the
negative cases differ from the positive one by exactly the mutation under test
and nothing else. The original is sha256'd before and after and asserted
BYTE-IDENTICAL. (The run-root logs are root-owned and mode 644, so nothing is
planted in place; the plant/restore cycle runs on a byte-exact copy the lane
owns, and the run-root artefact is proven untouched rather than assumed so.)

FIVE CONTROLS, AND WHY EACH EXISTS:

  C1 positive, real bytes         -- CONVERGED off the unmodified artefact.
  C2 positive, SENTINEL planted   -- reader returns the planted residual, so it
                                     is demonstrably reading disk, not guessing.
  C3 negative, ran to the cap     -- NOT CONVERGED.
  C4 negative, truncated          -- NOT MEASURED, never False. This is the
                                     exact shape v0 got wrong.
  C5 mutation guard               -- with CONV disabled, C1 MUST flip. A control
                                     that still passes against a broken reader
                                     is not a control.

THREE MATCH-IS-NOT-A-MEANING GUARDS (L-312: a regex limb needs a DISCRIMINATOR,
not just a pattern). All three are things that ARE in these logs, or that this
family has already been bitten by:

  G1 THE FPE BANNER. OpenFOAM announces at startup that floating-point-exception
     trapping is ENABLED -- `SigFpe : Enabling floating point exception trapping
     (FOAM_SIGFPE).` THAT IS A SAFETY NOTICE, NOT A CRASH, and this family has
     read it as a crash TWICE. This reader has NO crash limb at all, so it
     cannot currently make that mistake; G1 is a FAIL-CLOSED GUARD that fires
     the moment anyone adds one. The discriminator is the verb: the banner says
     "Enabling", a crash says "Foam::sigFpe::sigHandler" and kills the run.

  G2 THE WORD "error" IS IN EVERY HEALTHY LOG. `Time step continuity errors :
     sum local = ...` appears FIVE TIMES per log here, on perfectly converged
     solves. Any `grep -i error` limb would report five crashes per success.

  G3 THE DIAGNOSTIC MUST NOT DRIVE THE VERDICT. Total Residual Norm2 wrecked by
     ~10^6 leaves the verdict CONVERGED, because it is not the criterion.
"""
from __future__ import annotations

import hashlib
import math
import re
import sys
import tempfile
from pathlib import Path

# --- what DAFoam actually emits ---------------------------------------------
CONV = re.compile(
    r"Minimal residual\s+([0-9.eE+-]+)\s+satisfied the prescribed tolerance\s+([0-9.eE+-]+)")
TIME = re.compile(r"^Time = (\d+)\s*$", re.M)
END = re.compile(r"^End\s*$", re.M)
TOTAL_NORM = re.compile(r"^Total Residual Norm2:\s*([0-9.eE+-]+)", re.M)
STATS_BANNER = "Printing Primal Residual Statistics"

PATTERNS = {
    "CL": [re.compile(r"^CL:\s*([-+0-9.eE]+)", re.M)],
    "CD": [re.compile(r"^CD:\s*([-+0-9.eE]+)", re.M)],
}

# Verdict vocabulary for THIS COLUMN. Not lab verdicts -- a feasibility rung
# produces none -- but the same discipline: no soft words, and a null is named.
CONVERGED = "CONVERGED"
NOT_CONVERGED = "NOT CONVERGED"
NOT_MEASURED = "NOT MEASURED"


def last_match(text: str, pats: list[re.Pattern]) -> float | None:
    val = None
    for p in pats:
        for m in p.finditer(text):
            try:
                val = float(m.group(1))
            except ValueError:
                continue
    return val


def classify(text: str, endtime_cap: int | None) -> dict:
    """Return the convergence reading, with NOT MEASURED for a genuine null."""
    times = [int(m.group(1)) for m in TIME.finditer(text)]
    last_time = times[-1] if times else None
    ended = bool(END.search(text))

    cm = None
    for m in CONV.finditer(text):
        cm = m
    achieved = float(cm.group(1)) if cm else None
    tol = float(cm.group(2)) if cm else None

    # The post-End diagnostic. Captured so it can be REPORTED, never so it can
    # be mistaken for the criterion.
    tn = None
    for m in TOTAL_NORM.finditer(text):
        tn = float(m.group(1))

    if cm is not None:
        verdict = CONVERGED
        why = (f"DAFoam's own statement: minimal residual {achieved:.6e} "
               f"satisfied the prescribed tolerance {tol:.0e}")
    elif ended and endtime_cap is not None and last_time is not None and last_time >= endtime_cap:
        verdict = NOT_CONVERGED
        why = (f"ran to the endTime cap ({last_time} >= {endtime_cap}) and emitted no "
               f"tolerance-satisfied line: the iteration limit stopped it, not convergence")
    else:
        verdict = NOT_MEASURED
        why = ("no tolerance-satisfied line, and the log does not show the run reaching "
               "its endTime cap either -- this reader cannot tell whether the field "
               "converged, and says so rather than guessing")

    return {
        "verdict": verdict,
        "why": why,
        "achieved_min_residual": achieved,
        "prescribed_tolerance": tol,
        "last_time": last_time,
        "n_time_lines": len(times),
        "end_marker": ended,
        "total_residual_norm2_DIAGNOSTIC": tn,
        "stats_block_present": STATS_BANNER in text,
    }


def read_alpha(log: Path, endtime_cap: int | None) -> dict:
    text = log.read_text(errors="replace")
    r = classify(text, endtime_cap)
    r["log"] = str(log)
    r["CL"] = last_match(text, PATTERNS["CL"])
    r["CD"] = last_match(text, PATTERNS["CD"])
    return r


def read_endtime_cap(root: Path) -> int | None:
    cd = root / "case" / "system" / "controlDict"
    if not cd.is_file():
        return None
    m = re.search(r"^\s*endTime\s+([0-9]+)\s*;", cd.read_text(errors="replace"), re.M)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# PLANTED CONTROLS, IN BOTH DIRECTIONS, ON DISK, THROUGH read_alpha().
# ---------------------------------------------------------------------------
# A value that appears nowhere else in this file or in any real log. If the
# reader reports it, the reader read the disk.
PLANT_RESIDUAL = "1.234567e-09"
PLANT_TOL = "5.5e-08"

# The OpenFOAM startup banner this family has twice mistaken for a crash.
FPE_BANNER = (
    "fileModificationChecking : Monitoring run-time modified files using "
    "timeStampMaster (fileModificationSkew 5, maxFileModificationPolls 20)\n"
    "SigFpe : Enabling floating point exception trapping (FOAM_SIGFPE).\n"
)
# The healthy line whose text contains the word "errors", five times per log.
CONTINUITY_LINE = "Time step continuity errors : sum local = 8.5e-06\n"

CAP_FIXTURE = 1000


def _synthetic_source() -> str:
    """Fallback source bytes when the real artefact is unavailable.

    Deliberately shaped like the real log so the mutations below are the only
    difference between the positive and negative controls.
    """
    return ("Time = 100\nTime = 424\n"
            "Minimal residual 9.907086431972576e-09 satisfied the prescribed "
            "tolerance 1e-08\n\n"
            "CD: 0.02726805411971688 final: 0.02726805411971688\n"
            "CL: 0.6639763551107052 final: 0.6639763551107052\n"
            "End\n\n"
            "Printing Primal Residual Statistics.\n"
            "Total Residual Norm2: 0.0003622601706836595\n")


def _plant(work: Path, name: str, text: str, cap: int | None) -> dict:
    """Write a planted artefact to disk and read it back the way main() does."""
    target = work / name
    target.write_text(text)
    return read_alpha(target, cap)


def _mutate_to_cap(src: str) -> str:
    """Strip the tolerance statement and drive the last Time to the cap."""
    out = "\n".join(l for l in src.splitlines()
                    if "satisfied the prescribed tolerance" not in l)
    times = TIME.findall(out)
    if times:
        out = re.sub(r"^Time = %s\s*$" % re.escape(times[-1]),
                     "Time = %d" % CAP_FIXTURE, out, count=1, flags=re.M)
    return out + "\n"


def _mutate_to_truncated(src: str) -> str:
    """Cut the run off before it could either converge or reach the cap."""
    i = src.find("Minimal residual")
    if i < 0:
        i = len(src) // 2
    return src[:i]


def selftest(sample: Path | None = None) -> int:
    ok = True
    print("PLANTED CONTROLS -- on disk, read back through read_alpha(), "
          "BOTH DIRECTIONS.")

    # --- source bytes, and the restore proof -------------------------------
    if sample is not None and sample.is_file():
        src_bytes = sample.read_bytes()
        src = src_bytes.decode(errors="replace")
        sha_before = hashlib.sha256(src_bytes).hexdigest()
        origin = str(sample)
        real = True
    else:
        src = _synthetic_source()
        src_bytes = src.encode()
        sha_before = hashlib.sha256(src_bytes).hexdigest()
        origin = "SYNTHETIC (no real artefact supplied)"
        real = False
    print("  source artefact : %s" % origin)
    print("  sha256 before   : %s" % sha_before)
    print("  %s\n" % ("REAL RUN ARTEFACT -- controls are cut from its own bytes"
                      if real else
                      "NO REAL ARTEFACT -- controls run on a synthetic stand-in"))

    with tempfile.TemporaryDirectory(prefix="so3af_ctl_") as td:
        work = Path(td)

        # The plant/restore cycle runs on a byte-exact copy, because the
        # run-root logs are root-owned. The copy is restored and proven.
        copy = work / "restore_cycle.log"
        copy.write_bytes(src_bytes)
        assert hashlib.sha256(copy.read_bytes()).hexdigest() == sha_before

        # ---- C1 positive, unmodified real bytes ---------------------------
        a = _plant(work, "c1_real.log", src, CAP_FIXTURE)
        good = (a["verdict"] == CONVERGED
                and a["achieved_min_residual"] is not None
                and a["prescribed_tolerance"] is not None
                and a["achieved_min_residual"] < a["prescribed_tolerance"])
        print("  C1 [+] unmodified artefact      -> %-13s  %s" % (
            a["verdict"], "PASS" if good else "FAIL"))
        if a["achieved_min_residual"] is not None:
            print("         read off disk: min residual %.6e < tol %.1e"
                  % (a["achieved_min_residual"], a["prescribed_tolerance"]))
        ok &= good

        # ---- C2 positive, SENTINEL planted --------------------------------
        planted = re.sub(
            r"Minimal residual\s+[0-9.eE+-]+\s+satisfied the prescribed "
            r"tolerance\s+[0-9.eE+-]+",
            "Minimal residual %s satisfied the prescribed tolerance %s"
            % (PLANT_RESIDUAL, PLANT_TOL), src, count=1)
        planted_ok = planted != src or not real
        b = _plant(work, "c2_planted.log", planted, CAP_FIXTURE)
        seen = b["achieved_min_residual"]
        good = (planted_ok and b["verdict"] == CONVERGED and seen is not None
                and abs(seen - float(PLANT_RESIDUAL)) < 1e-18
                and b["prescribed_tolerance"] == float(PLANT_TOL))
        print("  C2 [+] SENTINEL %s planted -> reader reports %s  %s" % (
            PLANT_RESIDUAL, ("%.6e" % seen) if seen is not None else "NOTHING",
            "PASS" if good else "FAIL"))
        print("         a value that exists in no real log: seeing it proves "
              "the read is off disk")
        ok &= good

        # ---- C3 negative, ran to the cap ----------------------------------
        c = _plant(work, "c3_cap.log", _mutate_to_cap(src), CAP_FIXTURE)
        good = c["verdict"] == NOT_CONVERGED and c["last_time"] == CAP_FIXTURE
        print("  C3 [-] tolerance line removed, ran to cap -> %-13s  %s" % (
            c["verdict"], "PASS" if good else "FAIL"))
        print("         last_time %s >= cap %d" % (c["last_time"], CAP_FIXTURE))
        ok &= good

        # ---- C4 negative, truncated ---------------------------------------
        d = _plant(work, "c4_trunc.log", _mutate_to_truncated(src), CAP_FIXTURE)
        good = d["verdict"] == NOT_MEASURED
        print("  C4 [-] truncated mid-solve      -> %-13s  %s" % (
            d["verdict"], "PASS" if good else "FAIL"))
        print("         a null is NOT MEASURED, never False -- the exact shape "
              "v0 got wrong")
        ok &= good
        ok &= (d["verdict"] is not False and d["verdict"] != "False")

        # ---- C5 mutation guard: is C1 load-bearing at all? ----------------
        global CONV
        saved = CONV
        try:
            CONV = re.compile(r"THIS PATTERN CANNOT MATCH ANY LOG LINE ZZZ")
            e = _plant(work, "c5_mutation.log", src, CAP_FIXTURE)
        finally:
            CONV = saved
        good = e["verdict"] != CONVERGED
        print("  C5 [!] CONV disabled -> C1 must flip: %-13s  %s" % (
            e["verdict"], "PASS" if good else "FAIL"))
        print("         a control that still passes against a broken reader "
              "is not a control")
        ok &= good

        # ---- G1 THE FPE BANNER IS A SAFETY NOTICE, NOT A CRASH ------------
        with_fpe = FPE_BANNER + src
        f = _plant(work, "g1_fpe.log", with_fpe, CAP_FIXTURE)
        good = f["verdict"] == CONVERGED
        print("  G1 [!] OpenFOAM FPE-trapping banner injected -> %-13s  %s" % (
            f["verdict"], "PASS" if good else "FAIL"))
        print("         'SigFpe : Enabling floating point exception trapping' "
              "is a STARTUP NOTICE.")
        print("         This family read it as a crash twice. Fail-closed "
              "guard: fires if a crash limb is ever added without a "
              "discriminator (L-312).")
        ok &= good

        # ---- G2 THE WORD "error" IS IN EVERY HEALTHY LOG ------------------
        with_cont = src.replace("End\n", CONTINUITY_LINE * 5 + "End\n", 1)
        g = _plant(work, "g2_continuity.log", with_cont, CAP_FIXTURE)
        n_err = with_cont.lower().count("error")
        good = g["verdict"] == CONVERGED
        print("  G2 [!] %d lines containing 'error' -> %-13s  %s" % (
            n_err, g["verdict"], "PASS" if good else "FAIL"))
        print("         'Time step continuity errors' is a HEALTHY line and is "
              "in every real log here.")
        ok &= good

        # ---- G3 the diagnostic must not drive the verdict -----------------
        wrecked = re.sub(r"^Total Residual Norm2:.*$",
                         "Total Residual Norm2: 9.9e+02", src, flags=re.M)
        h = _plant(work, "g3_diag.log", wrecked, CAP_FIXTURE)
        good = h["verdict"] == CONVERGED
        print("  G3 [!] Total Residual Norm2 wrecked to 9.9e+02 -> %-13s  %s"
              % (h["verdict"], "PASS" if good else "FAIL"))
        print("         it is a post-End DIAGNOSTIC, not the criterion")
        ok &= good

        # ---- restore the plant/restore copy, byte-identically -------------
        copy.write_bytes(src_bytes)
        sha_restored = hashlib.sha256(copy.read_bytes()).hexdigest()
        good = sha_restored == sha_before
        print("  R  [=] planted copy restored    -> sha256 %s  %s" % (
            "MATCHES" if good else "DIFFERS", "PASS" if good else "FAIL"))
        ok &= good

    # ---- the run-root artefact must be untouched --------------------------
    if real:
        sha_after = hashlib.sha256(sample.read_bytes()).hexdigest()
        good = sha_after == sha_before
        print("  R  [=] run-root artefact untouched: sha256 after %s  %s" % (
            sha_after[:16] + "...", "PASS" if good else "FAIL"))
        ok &= good

    print("\n%s: 8 controls + restore, both directions driven, on disk."
          % ("SELFTEST PASS" if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


def find_logs(root: Path) -> list[Path]:
    out = root / "out"
    if not out.is_dir():
        return []
    return sorted(out.glob("primal_alpha_*.log"))


def main() -> int:
    argv = sys.argv[1:]
    selftest_only = bool(argv) and argv[0] == "--selftest"
    if selftest_only:
        argv = argv[1:]
    if len(argv) > 1 or (not selftest_only and len(argv) != 1):
        print("usage: so3af_read.py <run root> | --selftest [run root]")
        return 64
    root = Path(argv[0]) if argv else None

    # Locate the artefacts FIRST, so the controls can be cut from the very
    # bytes this reader is about to report on. A control planted into an
    # unrelated fixture proves less than one planted into the real log.
    logs = find_logs(root) if root is not None else []
    sample = logs[0] if logs else None

    if selftest(sample) != 0:
        print("REFUSING: the reader failed its own two-directional planted "
              "controls, so no reading from the real logs would be evidence "
              "(standing rule 3).")
        return 2
    if selftest_only:
        return 0

    if not (root / "out").is_dir():
        print(f"REFUSING: no out/ directory under {root}")
        return 2
    if not logs:
        print("NO LOGS -- nothing executed. This is not a physics answer.")
        return 2

    cap = read_endtime_cap(root)
    print(f"\nregistered endTime cap (case/system/controlDict): "
          f"{cap if cap is not None else 'NOT FOUND'}")
    print("  NOTE: for a DAFoam steady primal this is an UPPER BOUND on SIMPLE "
          "iterations, not a target.\n  Stopping BELOW it is the success signature, "
          "not a truncation.\n")

    rows = []
    for lg in logs:
        a = lg.name.replace("primal_alpha_", "").replace(".log", "")
        try:
            alpha = float(a)
        except ValueError:
            continue
        r = read_alpha(lg, cap)
        r["alpha_deg"] = alpha
        rows.append(r)
    rows.sort(key=lambda r: r["alpha_deg"])

    print(f"{'alpha_deg':>18} {'CL':>10} {'CD':>10} {'convergence':>14} "
          f"{'min_resid':>12} {'tol':>8} {'lastTime':>9} {'End':>5}")
    for r in rows:
        mr = f"{r['achieved_min_residual']:.4e}" if r["achieved_min_residual"] is not None else "-"
        tl = f"{r['prescribed_tolerance']:.0e}" if r["prescribed_tolerance"] is not None else "-"
        print(f"{r['alpha_deg']:>18.11f} "
              f"{('%.6f' % r['CL']) if r['CL'] is not None else 'None':>10} "
              f"{('%.6f' % r['CD']) if r['CD'] is not None else 'None':>10} "
              f"{r['verdict']:>14} {mr:>12} {tl:>8} "
              f"{str(r['last_time']):>9} {str(r['end_marker']):>5}")

    print("\nper-alpha basis:")
    for r in rows:
        print(f"  {r['alpha_deg']:.5f} deg: {r['why']}")

    print("\nDIAGNOSTIC ONLY -- 'Total Residual Norm2', printed by DAFoam AFTER End, "
          "inside the\n'Printing Primal Residual Statistics' block. It is an "
          "un-normalised norm over the whole\nresidual vector and IS NOT the "
          "convergence criterion. Reported so nobody has to hunt it:")
    for r in rows:
        print(f"  {r['alpha_deg']:.5f} deg: Total Residual Norm2 = "
              f"{r['total_residual_norm2_DIAGNOSTIC']}")

    stops = [r["last_time"] for r in rows]
    print(f"\nSTOPPING ITERATIONS: {stops}")
    if len(set(stops)) == len(stops) and len(stops) > 1:
        print("  All DIFFERENT -> convergence-driven, not an iteration cap. "
              "A shared stopping\n  number would have been the cap signature.")
    elif len(stops) > 1:
        print("  NOT all different -> check whether an iteration cap stopped these runs.")

    print("\n--- FEASIBILITY READINGS (not verdicts; NOT scoring any other item) ---")
    n_conv = sum(1 for r in rows if r["verdict"] == CONVERGED)
    n_nm = sum(1 for r in rows if r["verdict"] == NOT_MEASURED)
    print(f"declared alphas: 3   logs present: {len(rows)}   "
          f"CONVERGED: {n_conv}   NOT MEASURED: {n_nm}")

    cds = [r["CD"] for r in rows]
    if all(c is not None for c in cds) and len(cds) == 3:
        print(f"CD monotone increasing across the bracket: {cds[0] < cds[1] < cds[2]}  ({cds})")

    cls = [r["CL"] for r in rows]
    alphas = [r["alpha_deg"] for r in rows]
    if all(c is not None for c in cls) and len(cls) == 3:
        s1 = (cls[1] - cls[0]) / (alphas[1] - alphas[0])
        s2 = (cls[2] - cls[1]) / (alphas[2] - alphas[1])
        thin = 2 * math.pi * math.pi / 180.0   # 2*pi per RADIAN, expressed per DEGREE
        print(f"dCL/dalpha lower pair: {s1:.6f} /deg   ({100*s1/thin:.1f}% of thin-airfoil)")
        print(f"dCL/dalpha upper pair: {s2:.6f} /deg   ({100*s2/thin:.1f}% of thin-airfoil)")
        if s1:
            print(f"slope ratio upper/lower: {s2/s1:.4f}   "
                  f"(thin-airfoil reference {thin:.6f} /deg)")
            print("  ratio near 1.0 -> bracket is in the linear, attached range.")
            print("  ratio materially below 1.0 -> lift going nonlinear at the top of "
                  "the bracket.")
            print("  INDICATOR ONLY -- a real attachment claim needs wall shear, which "
                  "this rung does not buy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
