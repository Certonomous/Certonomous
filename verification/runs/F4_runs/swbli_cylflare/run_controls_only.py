#!/usr/bin/env python3
"""Run ONLY the positive controls of F4_SIGFPE_STEP01_PREREGISTRATION.md section 6
against the two step logs, and write each step's <STEP>/POSITIVE_CONTROL.txt.

WHY THIS FILE EXISTS. The frozen reader analyse_f4_sigfpe_step01.py has its
grading bodies (check_completion, grade_step0, grade_step1) as NotImplementedError
BY DESIGN -- writing a grading body before there is a run to grade invites tuning
it to the log. Its main() therefore refuses (exit 2) on anything but --selftest.
The controls, however, ARE coded and ARE the gate that must reproduce before any
number is believed. This driver calls those already-committed control functions
directly. It IMPLEMENTS NO GRADING and DEFINES NO THRESHOLD: every function it
calls is imported from the frozen reader, so the control code that runs here is
the same code the supervisor reads as a diff.

    C1  reader sees a known non-zero, from the committed fixture   (no run needed)
    C3  the same counter returns zero on the stock-solver crash log (no run needed)
    C4  the plant, into EACH STEP'S OWN log, by line index          (needs the run)
    C2  can the reader tell step 1's log from step 0's?             (needs both)

C0 (instrument inertness) is a twin-run comparison and is NOT this reader's; its
output is c0_twin_diag/C0_RESULT.txt and is copied into each POSITIVE_CONTROL.txt
below, as prereg section 6 requires ("the full control output is written to
<STEP>/POSITIVE_CONTROL.txt and quoted in the results record").

NOTHING HERE IS A GRADE. No prereg section 8 label is computed, printed or implied.
"""
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import analyse_f4_sigfpe_step01 as R  # noqa: E402

STEPS = [
    (HERE / "step0_instrumented", "log.rhoCentralFoamBoundedDiag"),
    (HERE / "step1_inletupwind", "log.rhoCentralFoamInletUpwindDiag"),
]
C0_RESULT = HERE / "c0_twin_diag" / "C0_RESULT.txt"


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%a %b %d %H:%M:%S UTC %Y")


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(HERE), *args],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception as exc:                      # noqa: BLE001
        return f"<unavailable: {exc}>"


def main() -> int:
    logs = [d / n for d, n in STEPS]
    for lg in logs:
        if not lg.exists():
            print(f"REFUSING: {lg} does not exist", file=sys.stderr)
            return 2

    # C4's scratch copies live UNDER THE STEP DIRECTORY, not in the session
    # scratchpad: L-186 -- the scratchpad is temp only and a repository document
    # (this POSITIVE_CONTROL.txt is one) never cites a scratch path. The
    # directory name carries this invocation's pid so it is unique per prereg
    # section 6 ("a scratch path unique to the invocation").
    tag = f"c4_plant_{os.getpid()}"

    header = [
        "POSITIVE_CONTROL.txt -- F4_SIGFPE_STEP01_PREREGISTRATION.md section 6",
        f"Produced {stamp()} (box clock, date -u equivalent, read in the same "
        "invocation as this write)",
        f"HEAD at write time: {git('rev-parse', 'HEAD')}",
        "Prereg blob at HEAD: "
        + git("rev-parse",
              "HEAD:verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md"),
        "Reader blob at HEAD: "
        + git("rev-parse",
              "HEAD:verification/runs/F4_runs/swbli_cylflare/"
              "analyse_f4_sigfpe_step01.py"),
        "",
        "Every control function called below is imported from the frozen reader.",
        "This driver implements no grading and defines no threshold.",
        "",
    ]

    try:
        c13 = R.control_c1() + R.control_c3()
        sig = R.selftest_sigfpe_regex()
    except R.ControlFailure as exc:
        print(f"CONTROL FAILURE (C1/C3): {exc}", file=sys.stderr)
        return 2

    # --- C2, across the two logs
    try:
        differ, c2 = R.control_c2(logs[0], logs[1])
    except R.ControlFailure as exc:
        print(f"CONTROL FAILURE (C2): {exc}", file=sys.stderr)
        return 2

    c0_text = (C0_RESULT.read_text(errors="replace")
               if C0_RESULT.exists() else "<C0_RESULT.txt MISSING>")

    overall = 0
    for (step_dir, log_name) in STEPS:
        log = step_dir / log_name
        out = list(header)
        out.append(f"STEP: {step_dir.name}")
        out.append(f"LOG : {log}  ({log.stat().st_size} bytes)")
        out.append(f"LOG md5: {R.md5_of(log)}")
        out.append("")
        out.append("=== C1 -- reader sees a known non-zero (committed fixture) ===")
        out += c13[:len(R.EXPECTED_C1) + 2]
        out.append("")
        out.append("=== C3 -- the same counter returns zero on a log with no clamp lines ===")
        out += c13[len(R.EXPECTED_C1) + 2:]
        out.append("")
        out.append("=== prereg 13.3 -- the SIGFPE regex cannot fire on the startup banner ===")
        out += sig
        out.append("")
        out.append("=== C4 -- the plant, into THIS STEP'S OWN log, by line index ===")
        try:
            out += R.control_c4(log, step_dir / tag)
            out.append("C4 PASSED: the reader is demonstrably reading THIS step's file.")
        except R.ControlFailure as exc:
            out.append(f"C4 CONTROL FAILURE: {exc}")
            out.append("This step is NOT graded (prereg section 6).")
            overall = 2
        out.append("")
        out.append("=== C2 -- can the reader tell step 1's log from step 0's? ===")
        out += c2
        out.append(f"C2 logs differ: {differ}")
        if not differ:
            out.append("C2 => LEVER-INERT. Per prereg 5.2/6 and the 9.1 row, the "
                       "discrimination question is NOT A RESULT and is not graded.")
        out.append("")
        out.append("=== C0 -- instrument inertness (twin runs; not this reader's) ===")
        out.append("Verbatim copy of c0_twin_diag/C0_RESULT.txt:")
        out.append("-" * 72)
        out.append(c0_text.rstrip())
        out.append("-" * 72)
        out.append("")
        out.append("NOTE: no prereg section 8 label is computed here. The grading "
                   "bodies of analyse_f4_sigfpe_step01.py remain NotImplementedError "
                   "and are a separate commit the supervisor reads as a diff.")
        (step_dir / "POSITIVE_CONTROL.txt").write_text("\n".join(out) + "\n")
        print(f"wrote {step_dir / 'POSITIVE_CONTROL.txt'}")

    print(f"C2 differ = {differ}")
    return overall


if __name__ == "__main__":
    sys.exit(main())
