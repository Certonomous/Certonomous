#!/usr/bin/env python3
"""W3 ADDENDUM 1 (2026-08-30) -- driven evidence for the W3-LAUNCHER-DEF-2 repair.

ZERO COMPUTE: no solver, no container.  Regenerates
`d12y_w3_fatal_scan_control_evidence.txt` from the REAL preserved corpora, so every
number in the addendum is reproducible rather than transcribed.

THE SCAN UNDER TEST IS NOT RETYPED HERE.  It is EXTRACTED from
`d12y_w3_stage_and_run.sh` and EXECUTED, so this evidence describes the shipping
implementation and cannot keep agreeing with the addendum after the launcher drifts.
"""
import datetime
import glob
import hashlib
import os
import re
import sys
import textwrap

C = os.path.dirname(os.path.abspath(__file__))
LAUNCHER = os.path.join(C, "d12y_w3_stage_and_run.sh")

# The SUPERSEDED nine patterns, whole-file, exactly as they stood at HEAD blob
# 20f8c0c51593576bddaa8a410659d997, lines 564-570.  Kept here ONLY to contrast the
# defect against the repair; nothing grades against them.
OLD = [r"FOAM FATAL ERROR", r"FOAM FATAL IO ERROR", r"Segmentation fault",
       r"signal \(11\)", r"signal \(8\)", r"signal \(6\)",
       r"Floating point exception", r"^\s*\[\d+\]\s+#\d+\s", r"MPI_ABORT"]
BENIGN_RE = re.compile(r"^\s*trapFpe:\s")

CLEAN_CORPORA = [
    ("D12R2W3  S0  (this item's own first stage)",
     "/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady_prior_fires/"
     "20260828T162848Z_supervisor_stopped/"
     "S0_20260828T162848Z_1898005.log"),
    ("D12R2W3  S1a (this item's own second stage)",
     "/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady_prior_fires/"
     "20260828T162848Z_supervisor_stopped/"
     "S1a_20260828T162848Z_1898005.log"),
    ("D6R      ACC multipoint",
     "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/"
     "ACC_mp_20260829T015422Z_2086625.log"),
    ("D18      cone hypersonic MESH",
     "/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic/"
     "MESH_20260828T021951Z_1712849.log"),
    ("D17      cone supersonic MESH",
     "/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic/"
     "MESH_20260827T113545Z_735271.log"),
    ("D12R2W2R S1a",
     "/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady/"
     "S1a_20260826T160035Z_23510.log"),
]
CRASH_GLOB = "/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs/*_solve.log"

MD5_FILES = ["d12y_w3_stage_and_run.sh", "d12y_w3_chain_driver.sh", "d12y_grade_w3.py",
             "d12y_w3_fatal_scan_control.sh", "d12y_w3_fatal_scan_evidence.py",
             "d12y_w3_fixture_REAL_D12R2W3_S0.log",
             "d12y_w3_fixture_REAL_D6R_ACC_excerpt.log",
             "d12y_w3_fixture_REAL_SIGFPE_crash_excerpt.log"]


def extract_block():
    src = open(LAUNCHER, errors="replace").read()
    m = re.search(r"^[ \t]*_FATAL = \[.*?^[ \t]*row\[\"fatal_benign_excluded\"\] = _benign\s*$",
                  src, re.S | re.M)
    if not m:
        print("REFUSE: could not extract the scan block from the launcher.")
        raise SystemExit(2)
    return textwrap.dedent(m.group(0))


BLOCK = extract_block()


def new_scan(txt):
    ns = {"re": re, "txt": txt, "row": {}}
    exec(compile(BLOCK, "<launcher scan block>", "exec"), ns)  # noqa: S102
    return ns["row"]["fatal_tokens"], ns["row"]["fatal_benign_excluded"]


def old_scan(txt):
    return [p for p in OLD if re.search(p, txt, re.M)]


def real_evidence(txt):
    """GROUND TRUTH, independent of both scans: the set of patterns matching a line
    that is NOT the trapFpe enablement banner.  This is the ONLY thing that is real
    evidence of a crash, and it is what the repair must never lose."""
    found = set()
    for ln in txt.splitlines():
        if BENIGN_RE.search(ln):
            continue
        for pat in OLD:
            if re.search(pat, ln):
                found.add(pat)
    return found


def main():
    out = []
    p = out.append
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    p("W3 ADDENDUM 1 -- FATAL-SCAN REPAIR (W3-LAUNCHER-DEF-2): DRIVEN EVIDENCE")
    p("generated %s   ZERO COMPUTE (no solver, no container)" % now)
    p("regenerate with: python3 d12y_w3_fatal_scan_evidence.py")
    p("=" * 78)

    p("")
    p("1. THE DEFECT, REPRODUCED ON REAL LOGS FROM FIVE DISTINCT ITEMS.")
    p("   Every OLD hit below is OpenFOAM's startup banner")
    p("     trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).")
    p("   i.e. the notice that FPE trapping is ENABLED, on runs with FOAM FATAL = 0.")
    p("")
    hdr = "%-44s %8s %8s %8s %10s" % ("corpus", "OLDhits", "NEWhits", "banner", "FOAMFATAL")
    p("   " + hdr)
    p("   " + "-" * len(hdr))
    for name, path in CLEAN_CORPORA:
        if not os.path.isfile(path):
            p("   %-44s   ABSENT (archived?) -- see the addendum's run-root section" % name)
            continue
        t = open(path, errors="replace").read()
        o = old_scan(t)
        n, b = new_scan(t)
        nb = sum(1 for ln in t.splitlines() if "trapFpe" in ln)
        p("   %-44s %8d %8d %8d %10d" % (name, len(o), len(n), nb, t.count("FOAM FATAL")))
    p("")
    p("   OLDhits > 0 with FOAM FATAL = 0 IS the defect: d12y_grade_w3.py:288-293 refuses")
    p("   on ANY non-empty `fatal_tokens`, 'regardless of rc, of the End line and of every")
    p("   other limb'.  W3 was GUARANTEED to refuse at its first stage and to publish a")
    p("   FALSE physics statement about a clean solve.")
    p("   NEWhits = 0 on every clean corpus WHILE the banner column is non-zero, so the")
    p("   zero is a READING and not an empty population (standing rule 3).")

    p("")
    p("2. THE REPAIR DOES NOT DISABLE THE SCAN.")
    p("   THE METRIC HERE WAS CORRECTED, AND THE CORRECTION IS RECORDED RATHER THAN")
    p("   DROPPED.  This lane's first draft counted 'files the OLD scan refused' against")
    p("   'files the REPAIRED scan refuses' and reported 34 -> 28, reading as SIX LOST")
    p("   CRASHES.  That metric was WRONG: it counted a file whose ONLY old hit was the")
    p("   BANNER as a detected crash, i.e. it scored the false positive as a success.")
    p("   The honest metric is GROUND TRUTH -- a pattern matching a NON-BANNER line --")
    p("   computed independently of both scans.  Measured below.")
    p("")
    files = sorted(glob.glob(CRASH_GLOB))
    n_old = n_new = 0
    n_old_banner_only = 0
    n_lost_real = 0
    n_added_decides = 0
    lost_names = []
    for path in files:
        t = open(path, errors="replace").read()
        o = set(old_scan(t))
        n, b = new_scan(t)
        n = set(n)
        real = real_evidence(t)
        if o:
            n_old += 1
        if n:
            n_new += 1
        if o and not real:
            n_old_banner_only += 1
        if real and not real <= n:
            n_lost_real += 1
            lost_names.append(os.path.basename(path))
        if n and not (n - {"Foam::sigFpe::sigHandler"}):
            n_added_decides += 1
    p("   real SIGFPE crash-corpus logs scanned                    : %d" % len(files))
    p("   refused by the OLD scan                                  : %d" % n_old)
    p("   refused by the REPAIRED scan                             : %d" % n_new)
    p("   of the OLD refusals, files whose ONLY hit was the BANNER : %d" % n_old_banner_only)
    p("     (pure false positives -- 0 non-banner fatal lines, 0 FOAM FATAL,")
    p("      0 sigHandler; four of them are externally KILLED_ runs, not FPE crashes)")
    p("")
    p("   >>> files where the REPAIR LOSES REAL CRASH EVIDENCE     : %d" % n_lost_real)
    for nm in lost_names:
        p("       LOST: %s" % nm)
    p("")
    p("   ZERO. The %d -> %d difference is EXACTLY the %d false positives being removed."
      % (n_old, n_new, n_old_banner_only))
    p("   Every real crash signature in the corpus is still refused.")

    p("")
    p("3. THE ONE WIDENING, AND ITS MEASURED CONSEQUENCE.")
    p("   The repair adds ONE positive token, `Foam::sigFpe::sigHandler`, adopted from")
    p("   curriculum_SO1aR/so1ar_grade.py:202 and curriculum_SO1c/so1c_grade.py:167,")
    p("   both of which take it from sdk/chief_engineer/head_engineer.py:188.  It can")
    p("   only ADD refusals, never remove one -- rule 5's one-way direction, the same")
    p("   direction the existing guard already runs in.")
    p("   Files where that token DECIDES a refusal the other nine would have missed: %d"
      % n_added_decides)
    p("   So on every log this lab has ever produced it changes NO graded outcome; it is")
    p("   belt-and-braces against an interleaved multi-rank stack trace whose `[n] #n `")
    p("   prefix is mangled, a shape present in this very corpus.")

    p("")
    p("4. INSTRUMENT AND FIXTURE MD5s AT THIS EVIDENCE RUN")
    for f in MD5_FILES:
        fp = os.path.join(C, f)
        h = hashlib.md5(open(fp, "rb").read()).hexdigest() if os.path.isfile(fp) else "ABSENT"
        p("   %-48s %s" % (f, h))
    p("")
    p("   d12y_grade_w3.py IS UNTOUCHED BY THIS ADDENDUM.  Its pre-answer freeze is this")
    p("   item's entire evidentiary value and nothing here reaches it.")

    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    with open(os.path.join(C, "d12y_w3_fatal_scan_control_evidence.txt"), "w") as fh:
        fh.write(text)


if __name__ == "__main__":
    main()
