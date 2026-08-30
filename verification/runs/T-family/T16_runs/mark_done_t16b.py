#!/usr/bin/env python3
"""Turn T16 STATUS files into DONE markers under the STRICT COMPLETION RULE,
with L-342's field classes applied from the start (the mark_done_t4b.py form).

FIELD CLASSES, DECLARED EXPLICITLY (L-342; the prose form of
`T3_runs/mark_done_t3_rff.py:8-18`, which `docs/L342_GRADER_AUDIT.md` names as
the model, copied rather than reinvented).  BOTH halves are driven by
`--selftest`; a class declaration no test exercises is a comment.

  PHYSICS-CRITICAL -- each a conjunct; any failure is NOT DONE and no marker is
  written.  L-342 relaxes NOTHING here; it only stops a dead poller voiding a
  good run.
    P1. the solver's rc VALUE is 0
    P2. log.solve carries an `End` line
    P3. the last written time == endTime from the case's own system/controlDict
    P4. every registered field is present at that time: T U p_rgh phi
    P5. THE AGE GUARD -- every field at endTime is NEWER than the case's own
        0/T (0/T is touched LAST at launch; L-143, D438)

  INFRASTRUCTURE -- reported; an absent or malformed value is stated NOT
  MEASURED, disclosed in the marker, and NEVER a refusal and never a conjunct
  (Sanaa's universal rule d4d0c29d, "a bookkeeping failure invalidates the
  bookkeeping, never the physics artifacts"):
    the **ExecutionTime line count**, wall_s, timeout_s, ranks, core_min,
    capped, checkmesh_rc, solver, solver_path, note, started_utc, ended_utc,
    ledger rows, pids, and the presence of log.launch / log.checkMesh.

  **THE `ExecutionTime` COUNT IS INFRASTRUCTURE, NOT PHYSICS.**  This is the
  exact misclassification `docs/L342_GRADER_AUDIT.md` found in
  `T14_runs/mark_done_t14.py:14-16` (refusing at `:107`) and in 27 other
  heat-transfer comparators, and the audit's point is that declaring the
  classes and then putting `ExecutionTime` on the physics side is WORSE than
  not declaring them, because it reassures a reader the split was done.  A
  short or absent count here is printed as NOT MEASURED beside a DONE.  It is
  a line-counting artefact of a print statement -- a solver that reached
  `End` at `endTime` with every field written and newer than `0/T` produced
  the physics whatever its log printing did (VMFLGPU001 AMENDMENT 4:
  petsc4Foam prints endTime + 2 lines and that is not a physics failure).

  `capped` is NOT a conjunct either (the T11/T4 form that returned NOT DONE on
  a missing `capped` witness was audited CONFLATING,
  `L342_FIELD_CLASS_AUDIT_2026-08-26.md`); it is still READ when present,
  because it separates a cap-stop (rule 12: the run stops, NOT A RESULT) from a
  crash (a finding needing triage) -- but it only LABELS a non-zero rc, never
  voids rc = 0.

RULING R-RC (verification, relayed 2026-08-27): **the `rc` VALUE is physics;
the `rc` RECORD is infrastructure.**  An absent STATUS file is therefore NOT an
automatic refusal any more.  It is NOT MEASURED, and only if ALL FOUR remaining
physics conditions P2-P5 hold is the case DONE -- and then `rc = 0` is printed
**as an inference and labelled as one**, never as a reading.  A `FOAM FATAL`
error, a `FOAM FATAL IO` error, a `Segmentation fault` or any signal token
anywhere in log.solve **still REFUSES**, absent record or not: the K0d L1
defect was inferring success from an End line past evidence of a crash, and
that inference is still forbidden.

D541 REPAIR, PROPOSED 2026-08-27 (this file is a PROPOSAL beside the frozen
`mark_done_t16.py`; it replaces nothing until a supervisor reads the diff):

  THE DEFECT.  `CRASH_TOKENS` carried the bare string "Floating point
  exception" and `crash_tokens_in_log()` tested `tok in line`.  EVERY OpenFOAM
  2606 run prints, at startup, before a single equation is assembled:

      trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

  which asserts that trapping is ENABLED -- the OPPOSITE of a crash.  The
  refusal at the head of `check()` runs BEFORE every physics limb, so NO T16
  case could be marked DONE at any level however clean.  Measured: 81 of 81
  clean OpenFOAM 2606 logs under `verification/runs/` (End line present, no
  FOAM FATAL) carry that string, all on the banner line.

  THE ROOT CAUSE, WHICH IS RULE 3 INVERTED.  The frozen `--selftest` passed
  only because its fixture log (`_forge`, the `body`/`fatal` lines) carries NO
  OpenFOAM BANNER at all.  The guard was therefore NEVER SHOWN A REAL CLEAN
  LOG.  It certified a crash detector it had no demonstrated ability to
  distinguish from normal startup.  Standing rule 3 plants a perturbation to
  prove a reader can see a NON-ZERO; THE MIRROR OBLIGATION, UNMET HERE, IS TO
  PROVE A GUARD CAN PASS A KNOWN-GOOD INPUT.  A refusal from a guard never
  shown able to accept is worth exactly as little as a zero from a reader
  never shown able to see.  Both controls are now driven below, from VERBATIM
  excerpts of real artifacts on this box, cited by path and line range.

  THE REPAIR, AND WHY IT DOES NOT WEAKEN DETECTION.  The FPE limb now matches
  the crash FORM -- a SIGNAL-DELIVERY REPORT, which a startup banner cannot
  produce -- and not a substring anywhere in a line.  Deleting the token, or
  merely excluding the banner line, WOULD have weakened detection, and that is
  measured rather than argued: the three real SERIAL FPE crashes on this box
  (`verification/runs/FPE_DIAG_runs/{BP1,BP2,HP1}/log.simpleFoam`) carry ZERO
  of the frozen crash tokens other than the banner itself -- 0 FOAM FATAL, 0
  "Segmentation fault", 0 "Aborted", 0 "signal ", and exactly 1 "Floating
  point exception" WHICH IS THE trapFpe BANNER.  The frozen matcher caught
  that whole crash class only by accident of its own false positive.  So
  `Foam::sigFpe::sigHandler` -- OpenFOAM's own FPE signal handler frame, which
  appears in a stack trace and nowhere else -- is LOAD-BEARING, not widening.
  The three FPE patterns score 0 false positives on the 81 clean logs and at
  least one true positive on all five real FPE crash logs on this box.

  WHAT IS DELIBERATELY NOT REPAIRED, AND WHY.  "Aborted" and "signal " sit in
  the same tuple and were matched the same loose way -- the SAME DEFECT CLASS.
  They are NAMED here and left BYTE-BEHAVIOURALLY UNCHANGED (their patterns
  are unanchored and match exactly what `tok in line` matched).  Measured: 0
  of the same 81 clean logs contain either.  Anchoring them would be a SECOND
  PERMISSIVE CHANGE with NO DEMONSTRATED NEED, and permissive is the dangerous
  direction.  They are a standing finding for the docket, not a repair.
  "FOAM FATAL ERROR", "FOAM FATAL IO ERROR" and "Segmentation fault" are also
  unchanged (0 false positives on the same 81).

T16b SUCCESSOR, REGISTERED 2026-08-30 in
`docs/campaigns/T-family/T16b_PREREGISTRATION.md`.  This file is a BYTE COPY of
the frozen `mark_done_t16.py` (blob efcf7852) with ONE SELFTEST LIMB CHANGED --
the D541 frozen-contrast limb -- and NOTHING ELSE.  The frozen parent is NOT
edited; zero frozen bytes change.  §3 of the registration enumerates the
thirteen carried-over items: every crash pattern, `crash_tokens_in_log`, the
NEEDED tuple, P1-P5, the L-342 field classes, the age-guard predicate, all three
R-RC arms, the exit codes, `main()` and the fourteen `expect` arms.  NO GATE,
THRESHOLD, BAND, CAP OR LABEL MOVES.

  WHY.  The parent's contrast limb loaded `HERE/mark_done_t16.py` -- correct
  when the repair was a PROPOSAL beside the frozen file, and self-referential
  after the A3/A9 promotion renamed the proposal onto that basename.  It
  therefore compared the repair against ITSELF.  Three consequences: (1) the
  clean arm inverts and FAILs; (2) THE TWO CRASH ARMS PASS TAUTOLOGICALLY --
  they re-measure the repaired matcher under a label reading FROZEN, and are
  evidence of nothing; (3) the narration sat OUTSIDE the loop and printed "the
  frozen matcher refuses the CLEAN case" unconditionally, contradicting the
  measurement three lines above it.

  THE REPAIR.  The contrast target is the PRESERVED PRE-REPAIR ORIGINAL
  `mark_done_t16.PRE_D541.py`, named by an EXPLICIT basename that cannot
  collide with this module's own, and guarded: ABSENT -> REFUSE (exit 2), BYTE-
  IDENTICAL TO THE RUNNING MODULE -> REFUSE (exit 2), git blob != the
  registered `2ae1605c` -> FAIL.  Each arm then asserts a REGISTERED
  DISAGREEMENT between the two matchers, limb by limb, instead of asking
  whether each returned something; and every narration line prints only inside
  the branch where its arm's relation actually held.  Arm S-4 DRIVES the guard
  at this module's own path -- D541's own defect, reproduced deliberately --
  and requires it to refuse, so the guard is shown to be a discriminator and
  not a constant.

NO `assert` STATEMENT IN THIS FILE (L-332).  --selftest forges cases in a
scratch root and DRIVES every clause, BOTH class halves, and the R-RC arms,
under python3 and python3 -O alike; --root DIR points the reader at another
tree (selftest use).

Usage:  python3 mark_done_t16b.py [CASE ...] [--root DIR] | --selftest

Exit codes:  0 all requested cases DONE
             1 at least one NOT DONE (a reportable outcome on physics fields)
             2 REFUSAL -- a crash token in the log, or a structural
               precondition (no case directory, no controlDict) failed
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
CASES = ("T16_MC_c", "T16_MC_m", "T16_MC_f")
NEEDED = ("T", "U", "p_rgh", "phi")
INFRA = ("wall_s", "timeout_s", "ranks", "core_min", "capped", "checkmesh_rc",
         "solver", "solver_path", "note", "started_utc", "ended_utc")
EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def control_end_time(case):
    p = os.path.join(ROOT, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- endTime is unknowable" % case)
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", open(p).read(), re.M)
    if not m:
        refuse("controlDict for %s states no endTime" % case)
    return float(m.group(1))


# D541: each entry is (LABEL, compiled pattern).  A pattern matches the crash
# FORM, never a bare substring that normal startup can also print.
CRASH_PATTERNS = (
    # unchanged from the frozen file; each is an error banner, not a state report
    ("FOAM FATAL ERROR",          re.compile(r"FOAM FATAL ERROR")),
    ("FOAM FATAL IO ERROR",       re.compile(r"FOAM FATAL IO ERROR")),
    ("Segmentation fault",        re.compile(r"Segmentation fault")),
    # D541 REPAIR: the frozen bare token "Floating point exception" matched the
    # trapFpe STARTUP BANNER, which says trapping is ENABLED.  Replaced by the
    # three forms in which an FPE is actually DELIVERED and REPORTED on this
    # box.  A banner cannot produce any of them.
    ("FPE: OpenFOAM sigFpe handler frame",
     re.compile(r"Foam::sigFpe::sigHandler")),
    ("FPE: signal report",
     re.compile(r"Signal:\s+Floating point exception")),
    ("FPE: mpirun exit-on-signal",
     re.compile(r"exited on signal\s+\d+\s*\(Floating point exception\)")),
    # NAMED, NOT REPAIRED (see the docstring): the same loose form, but no
    # false positive is demonstrated, so the pattern is left unanchored and
    # matches exactly what `tok in line` matched.
    ("Aborted",                   re.compile(r"Aborted")),
    ("signal ",                   re.compile(r"signal ")),
)
CRASH_TOKENS = tuple(label for label, _ in CRASH_PATTERNS)


def crash_tokens_in_log(case):
    """R-RC's hard limit on inference: a crash token in log.solve REFUSES, absent
    rc record or not.  Streamed, never loaded whole.

    D541: matched by FORM.  `tok in line` is gone; a startup banner is not a
    crash and must not be able to impersonate one."""
    p = os.path.join(ROOT, case, "log.solve")
    if not os.path.isfile(p):
        return []
    hits = []
    with open(p, errors="replace") as fh:
        for line in fh:
            for label, pat in CRASH_PATTERNS:
                if pat.search(line):
                    hits.append(label)
    return sorted(set(hits))


def read_status(case):
    """RULING R-RC: the rc VALUE is physics, the rc RECORD is infrastructure.
    Returns (dict-or-None, not_measured list).  A None dict means the record is
    NOT MEASURED; the caller then requires all four remaining physics conditions
    and prints rc = 0 as a LABELLED INFERENCE, never as a reading."""
    p = os.path.join(ROOT, "STATUS.%s" % case)
    if not os.path.isfile(p):
        return None, ["rc(record)"] + list(INFRA)
    txt = open(p).read()
    d = dict(re.findall(r"^([A-Za-z_]+)=(.*)$", txt, re.M))
    if "rc" not in d or not re.fullmatch(r"-?\d+", d["rc"].strip()):
        return None, ["rc(record, present but not an integer: %r)" % txt.strip()[:60]] + \
            [k for k in INFRA if k not in d]
    not_measured = [k for k in INFRA if k not in d]
    return d, not_measured


def check(case):
    """Return (list of physics failures, list of infrastructure NOT MEASURED)."""
    d = os.path.join(ROOT, case)
    if not os.path.isdir(d):
        refuse("no case directory %s" % d)
    st, nm = read_status(case)
    fails = []
    notes = []
    hits = crash_tokens_in_log(case)
    if hits:
        refuse("log.solve of %s carries crash token(s) %s -- R-RC forbids inferring "
               "success past evidence of a crash (K0d L1), with or without an rc record"
               % (case, ", ".join(repr(h) for h in hits)))
    if st is None:
        # R-RC: the RECORD is missing.  rc is NOT MEASURED.  The case can still be
        # DONE, but only on all four remaining physics conditions, and rc = 0 is
        # then an INFERENCE and is labelled one.
        notes.append("rc RECORD NOT MEASURED (no readable STATUS.%s); log.solve carries no "
                     "crash token; rc = 0 is INFERRED FROM THE REMAINING PHYSICS CONDITIONS "
                     "P2-P5 AND IS LABELLED AN INFERENCE, NOT A READING (ruling R-RC)" % case)
        st = {}
        rc = 0
    else:
        rc = int(st["rc"])
    if rc != 0:
        label = "CRASH (rc=%d)" % rc
        capped = st.get("capped")
        if capped == "yes":
            label = ("CAPPED (rc=%d, wall_s=%s >= timeout_s=%s): rule 12, the run "
                     "stopped at its registered cap and is NOT A RESULT, never "
                     "re-launched at a larger cap" % (rc, st.get("wall_s"), st.get("timeout_s")))
        elif capped == "no":
            label = ("CRASH (rc=%d at wall_s=%s below timeout_s=%s): a finding "
                     "until triage says otherwise" % (rc, st.get("wall_s"), st.get("timeout_s")))
        else:
            label += " -- capped witness NOT MEASURED, cap-stop vs crash undetermined"
        fails.append(label)

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"], nm, notes
    n_end = 0
    n_exec = 0
    with open(log, errors="replace") as fh:          # streamed, never loaded whole
        for line in fh:
            if line.startswith("ExecutionTime"):
                n_exec += 1
            elif line.rstrip() == "End":
                n_end += 1
    if n_end == 0:
        fails.append("log.solve has no End line")
    et = control_end_time(case)
    times = sorted((float(x) for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], nm, notes
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))
    tdir = os.path.join(d, "%g" % last)
    miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], nm, notes
    # THE ExecutionTime COUNT IS INFRASTRUCTURE (L-342 audit, T14 misclassification).
    # It is READ, it is REPORTED, and it never enters `fails`.
    if n_exec != int(et):
        nm = nm + ["ExecutionTime count (%d lines, endTime %d -- a log-printing artefact, "
                   "NOT a physics conjunct)" % (n_exec, int(et))]
    ref = os.path.join(d, "0", "T")
    if not os.path.isfile(ref):
        fails.append("no 0/T, so the run cannot be dated and the age guard cannot be evaluated")
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in NEEDED if os.path.getmtime(os.path.join(tdir, f)) < age]
        if stale:
            fails.append("time %g holds fields OLDER than 0/T (%s) -- not written by this run"
                         % (last, ",".join(stale)))
    return fails, nm, notes


def _forge(root, case, rc="0", end=40, n_exec=None, with_end=True, stale=False,
           status=True, infra=True, missing_field=None, capped="no", fatal=False,
           banner="", crash=""):
    """A synthetic case shaped exactly like a finished run, in a scratch root."""
    import time
    d = os.path.join(root, case)
    for sub in ("0", "system"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write("endTime %d;\n" % end)
    open(os.path.join(d, "0", "T"), "w").write("x\n")
    t0 = time.time() - 100
    os.utime(os.path.join(d, "0", "T"), (t0, t0))
    td = os.path.join(d, str(end))
    os.makedirs(td, exist_ok=True)
    for f in NEEDED:
        if f == missing_field:
            continue
        p = os.path.join(td, f)
        open(p, "w").write("y\n")
        if stale:
            os.utime(p, (t0 - 100, t0 - 100))
    n = end if n_exec is None else n_exec
    body = banner + "ExecutionTime = 1 s\n" * n
    if fatal:
        body += "--> FOAM FATAL ERROR: (openfoam-2606)\n"
    body += crash
    open(os.path.join(d, "log.solve"), "w").write(body + ("End\n" if with_end else ""))
    if status:
        lines = ["case=%s" % case, "rc=%s" % rc]
        if infra:
            lines += ["wall_s=10", "ranks=1", "core_min=0.167", "timeout_s=600", "capped=%s" % capped,
                      "checkmesh_rc=0", "solver=x", "solver_path=/x", "note=clean", "started_utc=x", "ended_utc=y"]
        open(os.path.join(root, "STATUS.%s" % case), "w").write("\n".join(lines) + "\n")


# --------------------------------------------------------------- D541 ----
# VERBATIM excerpts of REAL artifacts on this box, cited by path and line
# range.  `_d541_provenance()` re-reads each source and refuses if the
# embedded text is not a byte-exact substring of it, so these cannot silently
# drift into fabrications.  A source outside the repo may be absent; that is
# reported NOT MEASURED and is never a pass.
CLEAN_BANNER_2606 = r"""/*---------------------------------------------------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2606                                  |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
Build  : _481094f-20260618 OPENFOAM=2606 version=2606
Arch   : "LSB;label=32;scalar=64"
Exec   : /usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/buoyantBoussinesqSimpleFoam -case /home/ubuntu/Certonomous/verification/runs/T-family/T16_runs/T16_MC_c
Date   : Aug 27 2026
Time   : 17:30:06
Host   : ip-172-31-43-247
PID    : 1112110
I/O    : uncollated
Case   : /home/ubuntu/Certonomous/verification/runs/T-family/T16_runs/T16_MC_c
nProcs : 1
trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
memory pool : not available
fileModificationChecking : Monitoring run-time modified files using timeStampMaster (fileModificationSkew 5, maxFileModificationPolls 20)

--> FOAM Warning : allowSystemOperations : Allowing user-supplied system call operations.
                   This can be a security risk if running untrusted cases
                   through e.g. 'coded' on-the-fly-compilation functionality.

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""
CLEAN_BANNER_SRC = ("verification/runs/T-family/T16_runs/T16_MC_c/log.solve", "1-26")

# Form A -- SERIAL crash, OpenFOAM's own sigFpe handler and stack trace.
# This form carries NO other frozen crash token: the frozen matcher caught it
# ONLY via its own trapFpe false positive.
REAL_FPE_CRASH_A = r"""smoothSolver:  Solving for Uy, Initial residual = 0.3754906468, Final residual = 0.00257452692, No Iterations 25
[stack trace]
=============
#1  Foam::sigFpe::sigHandler(int) in <platforms>/linux64GccDPInt32Opt/lib/libOpenFOAM.so
#2  ? in /lib/x86_64-linux-gnu/libc.so.6
#3  Foam::GAMGSolver::scale(Foam::Field<double>&, Foam::Field<double>&, Foam::lduMatrix const&, Foam::FieldField<Foam::Field, double> const&, Foam::UPtrList<Foam::lduInterfaceField const> const&, Foam::Field<double> const&, unsigned char) const in <platforms>/linux64GccDPInt32Opt/lib/libOpenFOAM.so
#4  Foam::GAMGSolver::Vcycle(Foam::PtrList<Foam::lduMatrix::smoother> const&, Foam::Field<double>&, Foam::Field<double> const&, Foam::Field<double>&, Foam::Field<double>&, Foam::Field<double>&, Foam::Field<double>&, Foam::Field<double>&, Foam::PtrList<Foam::Field<double>>&, Foam::PtrList<Foam::Field<double>>&, unsigned char) const in <platforms>/linux64GccDPInt32Opt/lib/libOpenFOAM.so
#5  Foam::GAMGSolver::solve(Foam::Field<double>&, Foam::Field<double> const&, unsigned char) const in <platforms>/linux64GccDPInt32Opt/lib/libOpenFOAM.so
#6  Foam::fvMatrix<double>::solveSegregated(Foam::dictionary const&) in <platforms>/linux64GccDPInt32Opt/lib/libfiniteVolume.so
#7  ? in <platforms>/linux64GccDPInt32Opt/lib/libfiniteVolume.so
"""
REAL_FPE_CRASH_A_SRC = ("verification/runs/FPE_DIAG_runs/BP1/log.simpleFoam", "2035-2044")

# Form B -- MPI crash, the OpenMPI process-signal report plus mpirun summary.
REAL_FPE_CRASH_B = r"""[ip-172-31-43-247:3219838] *** Process received signal ***
[ip-172-31-43-247:3219838] Signal: Floating point exception (8)
[ip-172-31-43-247:3219838] Signal code:  (-6)
[ip-172-31-43-247:3219838] Failing at address: 0x3e80031217e
[ip-172-31-43-247:3219838] [ 0] /lib/x86_64-linux-gnu/libc.so.6(+0x45330)[0x7bd25d645330]
[ip-172-31-43-247:3219838] [ 1] /lib/x86_64-linux-gnu/libc.so.6(pthread_kill+0x11c)[0x7bd25d69ec0c]
[ip-172-31-43-247:3219838] [ 2] /lib/x86_64-linux-gnu/libc.so.6(gsignal+0x1e)[0x7bd25d64527e]
[ip-172-31-43-247:3219838] [ 3] /lib/x86_64-linux-gnu/libc.so.6(+0x45330)[0x7bd25d645330]
[ip-172-31-43-247:3219838] [ 4] /usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/lib/libOpenFOAM.so(_ZN4Foam6divideERNS_5FieldIdEERKdRKNS_5UListIdEE+0x24)[0x7bd25e40ba44]
mpirun noticed that process rank 2 with PID 0 on node ip-172-31-43-247 exited on signal 8 (Floating point exception).
"""
REAL_FPE_CRASH_B_SRC = ("/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs/hybrid_base_incompressible_a2.11_solve.log", "435-443,512")
REPO = "/home/ubuntu/Certonomous"


def _d541_provenance():
    """Each embedded excerpt must be a byte-exact substring of its cited source.
    Returns (list of failures, list of NOT MEASURED)."""
    bad, nm = [], []
    for blob, (path, lines) in ((CLEAN_BANNER_2606, CLEAN_BANNER_SRC),
                                (REAL_FPE_CRASH_A, REAL_FPE_CRASH_A_SRC),
                                (REAL_FPE_CRASH_B, REAL_FPE_CRASH_B_SRC)):
        p = path if os.path.isabs(path) else os.path.join(REPO, path)
        if not os.path.isfile(p):
            nm.append("%s:%s (source absent)" % (path, lines))
            continue
        with open(p, errors="replace") as fh:
            txt = fh.read()
        # form B is two disjoint ranges; check each line is present verbatim
        for ln in blob.splitlines():
            if ln and ln not in txt:
                bad.append("%s:%s -- embedded line not found verbatim: %r" % (path, lines, ln[:70]))
                break
    return bad, nm


# --------------------------------------------------------------- T16b ----
# THE CONTRAST TARGET, registered in `T16b_PREREGISTRATION.md` §4.1.  The parent
# named `mark_done_t16.py` here, which after the D541 promotion IS the running
# basename -- so the limb loaded itself.  T16b names the PRESERVED PRE-REPAIR
# ORIGINAL and REFUSES rather than skipping if it cannot be SHOWN to be a
# different file.
CONTRAST_TARGET = "mark_done_t16.PRE_D541.py"
CONTRAST_BLOB = "2ae1605c7983e379d586467a8ffb4890d0d1b20d"


def _digests(path):
    """(sha256 hex, git blob id, byte length) of a file's bytes, or (None,)*3."""
    import hashlib
    try:
        with open(path, "rb") as fh:
            b = fh.read()
    except OSError:
        return None, None, None
    return (hashlib.sha256(b).hexdigest(),
            hashlib.sha1(b"blob %d\x00" % len(b) + b).hexdigest(),
            len(b))


def _contrast_guard(target, running):
    """T16b §4.1.  Returns (ok, reason, info) WITHOUT exiting, so the selftest can
    DRIVE the refusing limb (arm S-4) rather than argue that it would refuse.

      G-1  target absent or unreadable          -> not ok; the caller REFUSES
      G-2  target bytes == running module bytes -> not ok; the caller REFUSES
      G-3  target git blob != CONTRAST_BLOB     -> reported in `info`; a FAIL for
           the caller and NEVER a refusal

    G-1/G-2 ask whether the contrast is STRUCTURALLY POSSIBLE and are
    preconditions; G-3 asks whether it is the REGISTERED HISTORICAL ARTIFACT and
    is a finding.  Collapsing the two is how a precondition quietly becomes an
    opinion.  G-2 also fires on the stale-index hazard of `DEAD_LEVER_AUDIT.md`
    :823 -- a `git checkout` restoring the 350-line PRE_D541 content over the
    running file would make the two identical and silently recreate D541."""
    t_sha, t_blob, t_len = _digests(target)
    r_sha, _, _ = _digests(running)
    info = dict(target=target, running=running, target_sha256=t_sha,
                running_sha256=r_sha, target_blob=t_blob, target_bytes=t_len)
    if t_sha is None:
        return False, "G-1 contrast target absent or unreadable: %s" % target, info
    if r_sha is None:
        return False, "G-1 running module absent or unreadable: %s" % running, info
    if t_sha == r_sha:
        return False, ("G-2 the contrast target is BYTE-IDENTICAL to the running module "
                       "(sha256 %s) -- that is D541's own defect and the contrast would "
                       "compare the repair against itself" % t_sha), info
    return True, "", info


def selftest():
    """Planted controls: each clause is driven both ways; the STATUS refusal is
    driven; an absent infrastructure field is shown NOT to void the case."""
    import shutil
    import tempfile
    global ROOT
    fails = []
    case = CASES[0]

    def expect(name, want_code, want_marker, **kw):
        global ROOT
        tmp = tempfile.mkdtemp(prefix="md13_selftest_")
        try:
            _forge(tmp, case, **kw)
            ROOT = tmp
            code = None
            try:
                code = main([case])
            except SystemExit as e:
                code = e.code
            marker = os.path.exists(os.path.join(tmp, "DONE.%s" % case))
            ok = (code == want_code) and (marker == want_marker)
            print("  [%s] %s -> exit %s, marker %s" % ("ok " if ok else "FAIL", name, code, marker))
            if not ok:
                fails.append(name)
        finally:
            ROOT = HERE
            shutil.rmtree(tmp, ignore_errors=True)

    print("mark_done_t16b selftest (planted controls; each clause drives the rule):")
    expect("clean forged case -> DONE, marker written", 0, True)
    expect("rc=1, capped=no -> NOT DONE (CRASH label)", 1, False, rc="1")
    expect("rc=124, capped=yes -> NOT DONE (CAPPED label, rule 12)", 1, False, rc="124", capped="yes")
    expect("no End line -> NOT DONE", 1, False, with_end=False)
    expect("a registered field missing at endTime -> NOT DONE (PHYSICS half P4)", 1, False,
           missing_field=NEEDED[3])
    expect("fields OLDER than 0/T (age guard) -> NOT DONE (PHYSICS half P5)", 1, False, stale=True)
    print("  -- the INFRASTRUCTURE half: each of these WOULD have refused before L-342 --")
    expect("ExecutionTime count SHORT (39 of 40) -> still DONE, NOT MEASURED disclosed "
           "(the T14 misclassification, not repeated here)", 0, True, n_exec=39)
    expect("ExecutionTime count LONG (42 of 40, the petsc4Foam shape) -> still DONE", 0, True, n_exec=42)
    expect("every infrastructure field absent (incl. capped) -> still DONE, NOT MEASURED disclosed",
           0, True, infra=False)
    print("  -- ruling R-RC: the rc VALUE is physics, the rc RECORD is infrastructure --")
    expect("absent STATUS record, P2-P5 all hold, clean log -> DONE with rc=0 LABELLED AN INFERENCE",
           0, True, status=False)
    expect("absent STATUS record AND a physics condition fails (no End) -> NOT DONE, no marker",
           1, False, status=False, with_end=False)
    expect("absent STATUS record AND `FOAM FATAL ERROR` in log.solve -> REFUSE exit 2 (R-RC's "
           "hard limit: no inference past evidence of a crash, K0d L1)", 2, False,
           status=False, fatal=True)
    expect("STATUS present with rc=0 but `FOAM FATAL ERROR` in log.solve -> REFUSE exit 2",
           2, False, fatal=True)
    # ------------------------------------------------------------ D541 ----
    print("  -- D541: the guard is shown able to PASS a known-good input, and")
    print("     still able to REFUSE two REAL FPE crashes (rule 3, inverted) --")
    bad, nm = _d541_provenance()
    for b in bad:
        print("  [FAIL] D541 provenance: %s" % b)
        fails.append("d541-provenance")
    for m in nm:
        print("  [ -- ] D541 provenance NOT MEASURED: %s" % m)
    if not bad and not nm:
        print("  [ok ] D541 provenance: all three excerpts verbatim in their cited sources")

    # (b) POSITIVE CONTROL -- a real clean OpenFOAM 2606 banner, trapFpe line
    #     included.  The FROZEN matcher REFUSED this (exit 2, no marker).
    expect("POSITIVE CONTROL: real OpenFOAM 2606 banner (trapFpe line) + clean body "
           "-> DONE, marker written (the frozen matcher REFUSED this)", 0, True,
           banner=CLEAN_BANNER_2606)
    # (a) NEGATIVE CONTROL -- the one that matters.  A real crash, WITH the
    #     banner above it, must still REFUSE.
    expect("NEGATIVE CONTROL A: banner + REAL SERIAL FPE crash "
           "(Foam::sigFpe::sigHandler stack trace) -> REFUSE exit 2, no marker", 2, False,
           banner=CLEAN_BANNER_2606, crash=REAL_FPE_CRASH_A)
    expect("NEGATIVE CONTROL B: banner + REAL MPI FPE crash "
           "(Signal: Floating point exception (8) + mpirun exit-on-signal) -> REFUSE exit 2", 2, False,
           banner=CLEAN_BANNER_2606, crash=REAL_FPE_CRASH_B)

    # which pattern fired, printed, so a reader can see it was not the banner
    import shutil as _sh
    import tempfile as _tf
    for name, kw, want_nonempty in (
            ("clean banner", dict(banner=CLEAN_BANNER_2606), False),
            ("banner + real serial FPE crash", dict(banner=CLEAN_BANNER_2606, crash=REAL_FPE_CRASH_A), True),
            ("banner + real MPI FPE crash", dict(banner=CLEAN_BANNER_2606, crash=REAL_FPE_CRASH_B), True)):
        tmp = _tf.mkdtemp(prefix="md16_d541_")
        try:
            _forge(tmp, case, **kw)
            ROOT = tmp
            globals()["ROOT"] = tmp
            hits = crash_tokens_in_log(case)
        finally:
            globals()["ROOT"] = HERE
            _sh.rmtree(tmp, ignore_errors=True)
        ok = bool(hits) == want_nonempty
        print("  [%s] D541 repaired matcher on %-34s -> %s" %
              ("ok " if ok else "FAIL", name, hits if hits else "no crash token"))
        if not ok:
            fails.append("d541-hits-" + name)

    # the PRE-REPAIR matcher, driven on the same three sacrificial cases, for
    # contrast.  T16b: loaded BY EXPLICIT PATH, GUARDED, and read as a
    # DISAGREEMENT rather than as "did each of them return something".
    frozen = os.path.join(HERE, CONTRAST_TARGET)
    running = os.path.abspath(__file__)
    guard_ok, why, info = _contrast_guard(frozen, running)
    print("  -- S-3: the contrast target must be a GENUINELY DIFFERENT FILE --")
    print("     target  %s (%s bytes)" % (info["target"], info["target_bytes"]))
    print("     target  sha256  %s" % info["target_sha256"])
    print("     running sha256  %s" % info["running_sha256"])
    if not guard_ok:
        refuse(why)                      # REFUSE (exit 2), never a silent skip
    print("  [ok ] S-3 the two digests DIFFER -- this is not a self-comparison")
    ok = (info["target_blob"] == CONTRAST_BLOB)
    print("  [%s] S-3/G-3 target git blob %s vs registered %s" %
          ("ok " if ok else "FAIL", info["target_blob"], CONTRAST_BLOB))
    if not ok:
        fails.append("contrast-blob")

    # S-4: DRIVE the guard at the RUNNING module's own path -- `mark_done_t16.py`
    # :515 reproduced deliberately -- and require it to REFUSE.  Two limbs from
    # one guard with opposite outcomes is what makes it a discriminator rather
    # than a constant; a guard that accepts everything has established nothing.
    self_ok, self_why, _ = _contrast_guard(running, running)
    ok = (not self_ok) and self_why.startswith("G-2")
    print("  [%s] S-4 the guard, pointed at the RUNNING module (D541's own line) -> %s"
          % ("ok " if ok else "FAIL", (self_why.split(" -- ")[0] if self_why else "ACCEPTED")))
    if not ok:
        fails.append("s4-self-target")

    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location("_pre_d541_t16", frozen)
    fz = _ilu.module_from_spec(spec)
    spec.loader.exec_module(fz)

    def _both(kw):
        """Drive BOTH matchers on ONE forged fixture -> (pre-repair, repaired)."""
        tmp = _tf.mkdtemp(prefix="md16_contrast_")
        try:
            _forge(tmp, case, **kw)
            fz.ROOT = tmp
            f_hits = fz.crash_tokens_in_log(case)
            globals()["ROOT"] = tmp
            r_hits = crash_tokens_in_log(case)
        finally:
            fz.ROOT = os.path.dirname(frozen)
            globals()["ROOT"] = HERE
            _sh.rmtree(tmp, ignore_errors=True)
        return f_hits, r_hits

    f_clean, r_clean = _both(dict(banner=CLEAN_BANNER_2606))
    f_a, r_a = _both(dict(banner=CLEAN_BANNER_2606, crash=REAL_FPE_CRASH_A))
    f_b, r_b = _both(dict(banner=CLEAN_BANNER_2606, crash=REAL_FPE_CRASH_B))

    # S-6: the contrast's OWN baseline, re-measured here rather than inherited
    # from the arms above.  A contrast whose baseline is not established is not
    # a contrast.
    ok = (r_clean == [])
    print("  [%s] S-6 repaired matcher on the CLEAN fixture -> %s  (the contrast baseline)"
          % ("ok " if ok else "FAIL", r_clean if r_clean else "no crash token"))
    if not ok:
        fails.append("s6-baseline")

    def _new_fpe(rep, frz):
        return [h for h in rep if h.startswith("FPE: ") and h not in frz]

    print("  -- S-5: each arm is a REGISTERED DISAGREEMENT, driven limb by limb --")
    for arm, fh_, rh_, limbs, narration in (
            ("C-1", f_clean, r_clean, (
                ("pre-repair hit set is NON-EMPTY", bool(f_clean)),
                ("pre-repair carries 'Floating point exception'",
                 "Floating point exception" in f_clean),
                ("repaired hit set is EMPTY", r_clean == []),
                ("the two DISAGREE ON PRESENCE", f_clean != r_clean)),
             "^ the PRE-REPAIR matcher refuses the CLEAN case and the repaired one does "
             "not: that is D541, measured rather than narrated."),
            ("C-2", f_a, r_a, (
                ("pre-repair hit set is NON-EMPTY", bool(f_a)),
                ("repaired hit set is NON-EMPTY", bool(r_a)),
                ("pre-repair on the CRASH == pre-repair on the CLEAN run", f_a == f_clean),
                ("repaired refuses for an FPE FORM the pre-repair cannot produce",
                 bool(_new_fpe(r_a, f_a)))),
             "^ the PRE-REPAIR matcher's refusal here is INDISTINGUISHABLE from its "
             "refusal on a clean run -- it fired on the banner, not on the crash."),
            ("C-3", f_b, r_b, (
                ("pre-repair hit set is NON-EMPTY", bool(f_b)),
                ("repaired hit set is NON-EMPTY", bool(r_b)),
                ("pre-repair still carries the CLEAN-run token(s)",
                 bool(set(f_b) & set(f_clean))),
                ("repaired refuses for an FPE FORM the pre-repair cannot produce",
                 bool(_new_fpe(r_b, f_b)))),
             "^ the same reason-level disagreement; the pre-repair set is a strict "
             "SUPERSET of the clean-run set because form B's own text carries "
             "'signal ' independently of the banner.")):
        print("  -- %s  pre-repair %s | repaired %s" % (arm, fh_ if fh_ else [], rh_ if rh_ else []))
        arm_ok = True
        for limb, held in limbs:
            print("  [%s]   %s %s" % ("ok " if held else "FAIL", arm, limb))
            if not held:
                arm_ok = False
        if arm_ok:
            # S-7: the narration lives INSIDE the branch where the arm's relation
            # actually held, so it can never state a claim the measurement above
            # it contradicts.
            print("     %s" % narration)
        else:
            fails.append("contrast-" + arm)
            print("     [%s did not hold -- NO interpretive claim is printed]" % arm)

    # an unregistered case name is refused
    code = None
    try:
        code = main(["T16_MC_x"])
    except SystemExit as e:
        code = e.code
    ok = (code == 2)
    print("  [%s] unregistered case name -> REFUSE exit 2" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("unregistered")
    import ast
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)" % ("ok " if ok else "FAIL", n_assert, planted))
    if not ok:
        fails.append("ast")
    # VERIFICATION_CHARTER §2d.1 condition (4), registered at
    # `T16b_PREREGISTRATION.md` §6: the PRE-REPAIR STATE is printed beside the
    # repaired one, never replaced by it.
    print("  PRE-REPAIR STATE: `mark_done_t16.py` (blob efcf7852) --selftest reads "
          "24 ok / 1 FAIL (frozen-contrast arm), exit 1 -- and its two crash-arm "
          "greens were TAUTOLOGICAL, not evidence.")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    global ROOT
    if "--selftest" in argv:
        return selftest()
    if "--root" in argv:
        ROOT = os.path.abspath(argv[argv.index("--root") + 1])
        argv = [a for i, a in enumerate(argv) if a != "--root" and (i == 0 or argv[i - 1] != "--root")]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    for c in want:
        if c not in CASES:
            refuse("%r is not one of the registered T16 cases: %s" % (c, " ".join(CASES)))
    rc = EXIT_OK
    for case in want:
        fails, nm, notes = check(case)
        infra = ("  [infrastructure NOT MEASURED: %s -- disclosed, grade proceeds]" % ",".join(nm)) if nm else ""
        infer = ("  [INFERENCE, LABELLED: %s]" % "; ".join(notes)) if notes else ""
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-10s - %s%s%s" % (case, "; ".join(fails), infra, infer))
        else:
            marker = os.path.join(ROOT, "DONE.%s" % case)
            if not os.path.exists(marker):
                open(marker, "w").write(
                    "strict rule met on the PHYSICS-CRITICAL conjuncts P1-P5%s%s\n" % (infra, infer))
            print("DONE      %-10s%s%s" % (case, infra, infer))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
